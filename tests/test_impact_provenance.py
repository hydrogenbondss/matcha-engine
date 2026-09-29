"""Run provenance in impact reports (mocks only: no provider, no Ollama, no network)."""

import hashlib
import json
import re
import subprocess
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


def test_engine_git_worktree_dirty_from_porcelain():
    seen = []

    def status(out):
        def run_git(args, cwd):
            seen.append((args, cwd))
            return out
        return run_git

    assert provenance.engine_git_worktree_dirty(status("")) is False  # clean
    assert provenance.engine_git_worktree_dirty(status(" M matcha/impact/report.py")) is True  # tracked change
    assert provenance.engine_git_worktree_dirty(status("?? untracked_only.txt")) is True  # untracked only
    assert provenance.engine_git_worktree_dirty(status(None)) is None  # git failed / no repository
    assert seen[0] == (["status", "--porcelain", "--untracked-files=normal"], provenance.PACKAGE_DIR)


def _fake_subprocess(monkeypatch, status_stdout, *, status_rc=0):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(cmd, 0, FAKE_SHA + "\n", "")
        if cmd[:3] == ["git", "status", "--porcelain"]:
            return subprocess.CompletedProcess(cmd, status_rc, status_stdout, "fatal: x" if status_rc else "")
        raise AssertionError(f"unexpected subprocess call {cmd}")

    monkeypatch.setattr(provenance.subprocess, "run", fake_run)
    return calls


@pytest.mark.parametrize(
    "stdout, rc, expected",
    [
        ("", 0, False),
        (" M matcha/impact/LEAKY_TRACKED_NAME.py\n", 0, True),
        ("?? LEAKY_UNTRACKED_NAME.txt\n", 0, True),
        ("", 128, None),
    ],
    ids=["clean", "tracked-change", "untracked-only", "git-failure"],
)
def test_worktree_dirty_in_report_without_filenames(tmp_path, monkeypatch, stdout, rc, expected):
    calls = _fake_subprocess(monkeypatch, stdout, status_rc=rc)
    out, md = tmp_path / "r.json", tmp_path / "r.md"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out, summary=md,
                   provider="unavailable", discovery_fn=fake_discovery)
    assert ["git", "status", "--porcelain", "--untracked-files=normal"] in calls
    assert r["provenance"]["engine"]["git_worktree_dirty"] is expected
    assert r["provenance"]["engine"]["git_commit"] == FAKE_SHA
    for text in (out.read_text(), md.read_text(), json.dumps(r["provenance"])):
        assert "LEAKY" not in text and "??" not in text
    word = {True: "yes", False: "no", None: "unknown"}[expected]
    assert f"Engine worktree dirty (tracked or untracked changes): {word}" in md.read_text()


@pytest.mark.parametrize("exc", [FileNotFoundError("git"), subprocess.TimeoutExpired("git", 10)],
                         ids=["git-missing", "git-timeout"])
def test_worktree_dirty_null_when_git_missing(monkeypatch, exc):
    def fake_run(cmd, **kwargs):
        raise exc

    monkeypatch.setattr(provenance.subprocess, "run", fake_run)
    assert provenance.engine_git_worktree_dirty() is None
    assert provenance.engine_git_commit() is None


def test_engine_git_worktree_dirty_real_call_is_bool_or_null():
    assert provenance.engine_git_worktree_dirty() in (True, False, None)


def test_unavailable_run_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: FAKE_SHA)
    monkeypatch.setattr(provenance, "engine_git_worktree_dirty", lambda: False)
    out, md = tmp_path / "r.json", tmp_path / "r.md"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out, summary=md,
                   provider="unavailable", discovery_fn=fake_discovery)
    pv = r["provenance"]
    assert json.loads(out.read_text())["provenance"] == pv
    assert set(pv) == {"engine", "fixture", "reference", "provider", "vision_prompt"}
    assert pv["engine"]["git_commit"] == FAKE_SHA
    assert pv["engine"]["git_worktree_dirty"] is False
    assert "porcelain" in pv["engine"]["git_worktree_dirty_source"]
    assert pv["fixture"]["manifest_sha256"] == r["fixture"]["manifest_sha256"]
    assert pv["reference"] == {"path": r["reference_asset"]["path"], "sha256": r["reference_asset"]["sha256"]}
    assert pv["provider"] == {"name": "unavailable", "model": None, "state": "UNAVAILABLE", "model_identity": None}
    vp = pv["vision_prompt"]
    assert vp["template_sha256"] == _sha(vision.PROMPT_TEMPLATE)
    assert vp["vision_module_sha256"] == hashlib.sha256(Path(vision.__file__).read_bytes()).hexdigest()
    assert vp["rendered_prompt_sha256"] is None
    assert "sent_to_provider" not in vp
    assert set(vp) == {"template_sha256", "vision_module_sha256", "rendered_prompt_sha256",
                       "rendered_prompt_sha256_note"}
    assert "not proof of network delivery" in vp["rendered_prompt_sha256_note"]
    text = md.read_text()
    assert "## Provenance" in text and FAKE_SHA in text and "none (no prompt rendered)" in text
    assert "not proof of network delivery" in text and "reported separately" in text
    assert "Engine worktree dirty (tracked or untracked changes): no" in text


def test_git_unavailable_gives_null(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "engine_git_commit", lambda: None)
    monkeypatch.setattr(provenance, "engine_git_worktree_dirty", lambda: None)
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
                   provider="unavailable", discovery_fn=fake_discovery)
    assert r["provenance"]["engine"]["git_commit"] is None
    assert r["provenance"]["engine"]["git_worktree_dirty"] is None
    text = render_markdown(r)
    assert "Engine git commit: unavailable" in text
    assert "Engine worktree dirty (tracked or untracked changes): unknown" in text


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
    monkeypatch.setattr(provenance, "engine_git_worktree_dirty", lambda: True)
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
    assert "sent_to_provider" not in vp
    assert vp["rendered_prompt_sha256"] == _sha(build_prompt(REQ, True))
    assert pv["engine"]["git_worktree_dirty"] is True
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
    monkeypatch.setattr(provenance, "engine_git_worktree_dirty", lambda: None)
    disc = discover(http=lambda *a, **k: (_ for _ in ()).throw(OSError("closed")),
                    which=lambda b: None, environ={"ANTHROPIC_API_KEY": SECRET})
    out = tmp_path / "r.json"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out,
                   provider="unavailable", discovery_fn=lambda: disc)
    assert SECRET not in out.read_text() and SECRET not in json.dumps(r["provenance"])
