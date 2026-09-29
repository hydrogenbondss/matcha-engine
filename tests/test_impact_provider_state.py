"""Provider execution state is recorded separately from the asset status."""

import json

import pytest

import matcha.impact.vision as vision
from impact_helpers import REAL_FIXTURE, fake_discovery
from matcha.impact.engine import run_impact
from matcha.impact.model import ASSET_STATUSES
from matcha.impact.vision import Classification, UnavailableProvider, classify_asset, load_image_input

REQ = "The character's canonical hairstyle changes to shoulder-length dark hair."
REF = REAL_FIXTURE / "reference" / "kite_male_neutral.png"


def _forbid_validate(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("validate_response must not run when no provider classified anything")

    monkeypatch.setattr(vision, "validate_response", boom)


def test_unavailable_never_goes_through_validate_response(tmp_path, monkeypatch):
    _forbid_validate(monkeypatch)
    img = tmp_path / "c.png"
    img.write_bytes(REF.read_bytes())
    c = classify_asset(UnavailableProvider(), "r", None, load_image_input(img, "candidate-01"), {})
    assert (c.status, c.provider_state, c.review_cause) == ("REVIEW_REQUIRED", "UNAVAILABLE", "PROVIDER_UNAVAILABLE")
    assert c.valid_provider_output is False and c.confidence is None and c.provider_status is None


def test_unavailable_report_never_claims_valid_output(tmp_path, monkeypatch):
    _forbid_validate(monkeypatch)
    out = tmp_path / "r.json"
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=out,
                   provider="unavailable", discovery_fn=fake_discovery)
    text = out.read_text()
    assert '"valid_provider_output": true' not in text
    assert r["provider"]["state"] == "UNAVAILABLE"
    for a in r["assets"]:
        assert a["status"] == "REVIEW_REQUIRED"
        assert a["provider_state"] == "UNAVAILABLE" and a["review_cause"] == "PROVIDER_UNAVAILABLE"
        assert a["classification"]["valid_provider_output"] is False
        assert a["classification"]["confidence"] is None


class _PerCandidate:
    """Behaviour chosen by opaque candidate number: 1 error, 2 malformed, 3 semantic RR,
    4 low confidence, others ASSET_ACTION."""

    name, model = "fake", "fake-1"

    def available(self):
        return True, "ok"

    def classify(self, request, reference_image, candidate_image, context):
        n = int(candidate_image.id.split("-")[1])
        if n == 1:
            raise RuntimeError("boom")
        if n == 2:
            return "not json"
        if n == 3:
            return {"status": "REVIEW_REQUIRED", "confidence": 0.9, "reason": "cannot tell"}
        if n == 4:
            return {"status": "UNAFFECTED", "confidence": 0.1, "reason": "unsure"}
        return {"status": "ASSET_ACTION", "confidence": 0.95, "reason": "visible"}


def test_each_cause_is_distinguishable_in_the_report(tmp_path):
    r = run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
                   discovery_fn=fake_discovery, provider_obj=_PerCandidate())
    by = {int(a["candidate_id"].split("-")[1]): a for a in r["assets"]}
    assert (by[1]["provider_state"], by[1]["review_cause"]) == ("ERROR", "PROVIDER_ERROR")
    assert (by[2]["provider_state"], by[2]["review_cause"]) == ("INVALID_OUTPUT", "INVALID_PROVIDER_OUTPUT")
    assert (by[3]["provider_state"], by[3]["review_cause"]) == ("AVAILABLE", "SEMANTIC_REVIEW_REQUIRED")
    assert (by[4]["provider_state"], by[4]["review_cause"]) == ("AVAILABLE", "LOW_CONFIDENCE")
    assert (by[5]["status"], by[5]["provider_state"], by[5]["review_cause"]) == ("ASSET_ACTION", "AVAILABLE", None)
    for n in (1, 2):
        assert by[n]["classification"]["valid_provider_output"] is False
    for n in (3, 4, 5):
        assert by[n]["classification"]["valid_provider_output"] is True
    assert all(a["status"] in ASSET_STATUSES for a in r["assets"])
    assert set(ASSET_STATUSES) == {"ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED"}
    assert r["counts"]["asset_provider_state"]["ERROR"] == 1
    assert r["counts"]["asset_review_cause"]["INVALID_PROVIDER_OUTPUT"] == 1
    json.dumps(r)


@pytest.mark.parametrize(
    "kw",
    [
        {"status": "ASSET_ACTION", "provider_state": "UNAVAILABLE", "reason": "x"},
        {"status": "UNAFFECTED", "provider_state": "ERROR", "reason": "x"},
        {"status": "REVIEW_REQUIRED", "provider_state": "AVAILABLE", "reason": "x"},  # no cause
        {"status": "ASSET_ACTION", "provider_state": "AVAILABLE", "reason": "x", "review_cause": "LOW_CONFIDENCE"},
        {"status": "PROVIDER_UNAVAILABLE", "provider_state": "UNAVAILABLE", "reason": "x"},
        {"status": "REVIEW_REQUIRED", "provider_state": "BROKEN", "reason": "x", "review_cause": "PROVIDER_ERROR"},
    ],
)
def test_classification_invariants(kw):
    with pytest.raises(ValueError):
        Classification(**kw)
