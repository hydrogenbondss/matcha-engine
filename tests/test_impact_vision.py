import json
import math

import pytest

from impact_helpers import fake_discovery, png
from matcha.impact.discovery import discover, select_provider
from matcha.impact.vision import (
    OllamaProvider,
    UnavailableProvider,
    build_prompt,
    classify_asset,
    validate_response,
)

GOOD = {"status": "ASSET_ACTION", "confidence": 0.93, "reason": "The head and hair are visible."}


def test_valid_dict_and_json_text():
    c = validate_response(GOOD)
    assert (c.status, c.valid, c.confidence) == ("ASSET_ACTION", True, 0.93)
    c = validate_response(json.dumps({**GOOD, "locator": "upper third"}))
    assert c.status == "ASSET_ACTION" and c.locator == "upper third"
    assert validate_response(json.dumps(GOOD).encode()).status == "ASSET_ACTION"


@pytest.mark.parametrize(
    "raw,fragment",
    [
        ("not json at all", "not JSON"),
        ("[1, 2]", "expected a JSON object"),
        (None, "expected a JSON object"),
        (b"\xff\xfe", "not UTF-8"),
        ({**GOOD, "extra": 1}, "unexpected keys"),
        ({"status": "ASSET_ACTION", "reason": "x"}, "missing keys"),
        ({**GOOD, "status": "AFFECTED"}, "out of enum"),
        ({**GOOD, "status": "DOWNSTREAM_USAGE"}, "out of enum"),
        ({**GOOD, "status": 1}, "out of enum"),
        ({**GOOD, "confidence": "high"}, "not a number"),
        ({**GOOD, "confidence": True}, "not a number"),
        ({**GOOD, "confidence": 1.5}, "outside [0, 1]"),
        ({**GOOD, "confidence": -0.1}, "outside [0, 1]"),
        ({**GOOD, "confidence": math.nan}, "outside [0, 1]"),
        ({**GOOD, "reason": "  "}, "reason must be"),
        ({**GOOD, "reason": 3}, "reason must be"),
        ({**GOOD, "locator": 5}, "locator must be"),
    ],
)
def test_malformed_output_becomes_review_required(raw, fragment):
    c = validate_response(raw)
    assert c.status == "REVIEW_REQUIRED"
    assert c.valid is False
    assert fragment in c.reason


def test_low_confidence_becomes_review_required_with_reason():
    c = validate_response({**GOOD, "confidence": 0.4}, threshold=0.7)
    assert c.status == "REVIEW_REQUIRED"
    assert c.provider_status == "ASSET_ACTION"
    assert "below the threshold" in c.reason and "head and hair" in c.reason
    c = validate_response({"status": "UNAFFECTED", "confidence": 0.69, "reason": "not in frame"}, threshold=0.7)
    assert c.status == "REVIEW_REQUIRED"
    assert validate_response({**GOOD, "confidence": 0.7}, threshold=0.7).status == "ASSET_ACTION"


def test_provider_review_required_is_kept_even_at_low_confidence():
    c = validate_response({"status": "REVIEW_REQUIRED", "confidence": 0.2, "reason": "cropped out"})
    assert c.status == "REVIEW_REQUIRED" and c.valid is True and c.reason == "cropped out"


class _Boom:
    name, model = "boom", None

    def available(self):
        return True, "ok"

    def classify(self, *a):
        raise RuntimeError("kaput")


def test_provider_exception_and_transport_error(tmp_path):
    img = tmp_path / "a.png"
    png(img)
    c = classify_asset(_Boom(), "req", None, img, {})
    assert c.status == "REVIEW_REQUIRED" and "provider error" in c.reason

    class _T(_Boom):
        def classify(self, *a):
            return {"__transport_error__": "timed out"}

    c = classify_asset(_T(), "req", None, img, {})
    assert c.status == "REVIEW_REQUIRED" and "transport error" in c.reason


def test_unavailable_provider(tmp_path):
    img = tmp_path / "a.png"
    png(img)
    p = UnavailableProvider(missing=["x"])
    assert p.available() == (False, "provider unavailable")
    c = classify_asset(p, "req", None, img, {})
    assert (c.status, c.reason, c.confidence) == ("REVIEW_REQUIRED", "provider unavailable", 0.0)


def test_ollama_adapter_payload_and_validation(tmp_path, monkeypatch):
    ref, cand = tmp_path / "r.png", tmp_path / "c.png"
    png(ref), png(cand, (200, 0, 0))
    calls = []

    def fake_post(self, path, payload):
        calls.append((path, payload))
        if path == "/api/show":
            return {"capabilities": ["completion", "vision"]}
        return {"message": {"content": json.dumps(GOOD)}}

    monkeypatch.setattr(OllamaProvider, "_post", fake_post)
    p = OllamaProvider(model="some-vl")
    assert p.available() == (True, "ok")
    c = classify_asset(p, "Hair changes.", ref, cand, {"asset_path": "assets/c.png"})
    assert c.status == "ASSET_ACTION"
    path, payload = calls[-1]
    assert path == "/api/chat" and payload["format"] == "json"
    assert len(payload["messages"][0]["images"]) == 2
    assert "Hair changes." in payload["messages"][0]["content"]
    assert "assets/c.png" in payload["messages"][0]["content"]


def test_ollama_without_vision_is_unavailable(monkeypatch):
    monkeypatch.setattr(OllamaProvider, "_post", lambda self, p, d: {"capabilities": ["completion"]})
    ok, why = OllamaProvider(model="text-only").available()
    assert not ok and "vision" in why


def test_prompt_is_generic():
    p = build_prompt("X changes.", "assets/a.png", True)
    assert "FIRST image is the reference" in p and "JSON" in p
    assert "Do not guess from the file name" in p


def test_discovery_reports_presence_only_and_no_values():
    secret = "sk-test-SHOULD-NOT-APPEAR"

    def http(url, payload=None, timeout=2.0):
        if url.endswith("/api/tags"):
            return {"models": [{"name": "text:1b"}, {"name": "vl:3b"}]}
        if url.endswith("/api/show"):
            return {"capabilities": ["vision"] if payload["model"] == "vl:3b" else ["completion"]}
        raise OSError("closed")

    d = discover(http=http, which=lambda b: "/x/" + b if b == "ollama" else None, environ={"OPENAI_API_KEY": secret})
    assert d["api_key_env_present"]["OPENAI_API_KEY"] is True
    assert d["api_key_env_present"]["ANTHROPIC_API_KEY"] is False
    assert d["ollama"]["vision_models"] == ["vl:3b"]
    assert secret not in json.dumps(d)
    assert any("OPENAI_API_KEY is set but no adapter" in m for m in d["missing"])
    prov, note = select_provider("auto", d)
    assert isinstance(prov, OllamaProvider) and prov.model == "vl:3b"


def test_discovery_nothing_available():
    def http(url, payload=None, timeout=2.0):
        raise OSError("connection refused")

    d = discover(http=http, which=lambda b: None, environ={})
    assert not d["ollama"]["reachable"]
    assert "no cloud vision API key present in the environment" in d["missing"]
    prov, note = select_provider("auto", d)
    assert isinstance(prov, UnavailableProvider)
    prov, _ = select_provider("ollama:vl:3b", fake_discovery())
    assert isinstance(prov, UnavailableProvider)
    prov, _ = select_provider("bogus", fake_discovery())
    assert isinstance(prov, UnavailableProvider) and any("unknown provider" in m for m in prov.missing)
