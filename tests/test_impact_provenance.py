"""Run provenance in impact reports (mocks only: no provider, no Ollama, no network)."""

import hashlib
import json
import re
import urllib.request
from pathlib import Path

import pytest

import matcha.impact.provenance as provenance
import matcha.impact.vision as vision
from impact_helpers import REAL_FIXTURE, fake_discovery
from matcha.impact.discovery import discover
from matcha.impact.engine import run_impact
from matcha.impact.report import render_markdown
from matcha.impact.vision import OllamaProvider, build_prompt

REQ = "The character's canonical hairstyle changes to shoulder-length dark hair."
REF = REAL_FIXTURE / "reference" / "kite_male_neutral.png"
FAKE_SHA = "0123456789abcdef0123456789abcdef01234567"
SECRET = "sk-test-PROVENANCE-SHOULD-NOT-APPEAR"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*a, **k):
        raise AssertionError("network access attempted in a provenance test")

    monkeypatch.setattr(urllib.request, "urlopen", refuse)


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_engine_git_commit_is_never_guessed():
    assert provenance.engine_git_commit(lambda args, cwd: FAKE_SHA) == FAKE_SHA
    assert provenance.engine_git_commit(lambda args, cwd: None) is None
    assert provenance.engine_git_commit(lambda args, cwd: "not a sha") is None
    assert provenance.engine_git_commit(lambda args, cwd: FAKE_SHA[:12]) is None
    seen = []
    provenance.engine_git_commit(lambda args, cwd: seen.append((args, cwd)))
    assert seen == [(["rev-parse", "HEAD"], provenance.PACKAGE_DIR)]


def test_engine_git_commit_real_call_is_sha_or_null():
    sha = provenance.engine_git_commit()
    assert sha is None or re.fullmatch(r"[0-9a-f]{40}([0-9a-f]{24})?", sha)


def test_unavailable_run_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: FAKE_SHA)
    out, md = tmp_path / "r.json", tmp_path / "r.md"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out, summary=md,
                   provider="unavailable", discovery_fn=fake_discovery)
    pv = r["provenance"]
    assert json.loads(out.read_text())["provenance"] == pv
    assert set(pv) == {"engine", "fixture", "reference", "provider", "vision_prompt"}
    assert pv["engine"]["git_commit"] == FAKE_SHA
    assert pv["fixture"]["manifest_sha256"] == r["fixture"]["manifest_sha256"]
    assert pv["reference"] == {"path": r["reference_asset"]["path"], "sha256": r["reference_asset"]["sha256"]}
    assert pv["provider"] == {"name": "unavailable", "model": None, "state": "UNAVAILABLE", "model_identity": None}
    vp = pv["vision_prompt"]
    assert vp["template_sha256"] == _sha(vision.PROMPT_TEMPLATE)
    assert vp["vision_module_sha256"] == hashlib.sha256(Path(vision.__file__).read_bytes()).hexdigest()
    assert vp["rendered_prompt_sha256"] is None and vp["sent_to_provider"] is False
    text = md.read_text()
    assert "## Provenance" in text and FAKE_SHA in text and "none (no prompt sent)" in text


def test_git_unavailable_gives_null(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: None)
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
                   provider="unavailable", discovery_fn=fake_discovery)
    assert r["provenance"]["engine"]["git_commit"] is None
    assert "Engine git commit: unavailable" in render_markdown(r)


def _mocked_ollama(monkeypatch, tags_model, show_extra):
    def http(url, payload=None, timeout=2.0):
        if url.endswith("/api/tags"):
            return {"models": [tags_model]}
        if url.endswith("/api/show"):
            return {"capabilities": ["completion", "vision"], **show_extra}
        raise OSError("closed")

    disc = discover(http=http, which=lambda b: "/x/" + b if b == "ollama" else None,
                    environ={"OPENAI_API_KEY": SECRET})
    posts = []

    def fake_post(self, path, payload):
        posts.append(path)
        if path == "/api/show":
            return {"capabilities": ["vision"]}
        return {"message": {"content": json.dumps({"status": "UNAFFECTED", "confidence": 0.9, "reason": "n/a"})}}

    monkeypatch.setattr(OllamaProvider, "_post", fake_post)
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: FAKE_SHA)
    return disc, posts


def test_ollama_model_identity_preserved_from_discovery(tmp_path, monkeypatch):
    digest = "sha256:" + "ab" * 32
    tag_details = {"family": "fam", "parameter_size": "3B", "quantization_level": "Q4_K_M"}
    show_details = {"family": "fam", "format": "gguf", "parameter_size": "3B", "quantization_level": "Q4_K_M"}
    disc, posts = _mocked_ollama(monkeypatch, {"name": "vl:3b", "digest": digest, "details": tag_details},
                                 {"details": show_details, "modelfile": "FROM x"})
    assert disc["ollama"]["model_identity"]["vl:3b"] == {
        "digest": digest, "details": show_details, "source": "digest: /api/tags; details: /api/show"}
    out = tmp_path / "r.json"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out,
                   provider="auto", discovery_fn=lambda: disc)
    pv = r["provenance"]
    assert pv["provider"]["name"] == "ollama" and pv["provider"]["model"] == "vl:3b"
    assert pv["provider"]["state"] == "AVAILABLE"
    assert pv["provider"]["model_identity"] == {
        "digest": digest, "details": show_details, "source": "digest: /api/tags; details: /api/show"}
    vp = pv["vision_prompt"]
    assert vp["sent_to_provider"] is True
    assert vp["rendered_prompt_sha256"] == _sha(build_prompt(REQ, True))
    assert "/api/chat" in posts  # the mocked adapter was used
    text = out.read_text()
    assert SECRET not in text and "modelfile" not in json.dumps(pv)


def test_ollama_without_identity_fields_gives_null(tmp_path, monkeypatch):
    disc, _ = _mocked_ollama(monkeypatch, {"name": "vl:3b"}, {})
    assert disc["ollama"]["model_identity"]["vl:3b"] == {"digest": None, "details": None, "source": "/api/tags"}
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=None, output=tmp_path / "r.json",
                   provider="auto", discovery_fn=lambda: disc)
    assert r["provenance"]["provider"]["model_identity"] is None
    assert r["provenance"]["vision_prompt"]["rendered_prompt_sha256"] == _sha(build_prompt(REQ, False))


def test_provenance_carries_no_secrets(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: None)
    disc = discover(http=lambda *a, **k: (_ for _ in ()).throw(OSError("closed")),
                    which=lambda b: None, environ={"ANTHROPIC_API_KEY": SECRET})
    out = tmp_path / "r.json"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out,
                   provider="unavailable", discovery_fn=lambda: disc)
    assert SECRET not in out.read_text() and SECRET not in json.dumps(r["provenance"])
