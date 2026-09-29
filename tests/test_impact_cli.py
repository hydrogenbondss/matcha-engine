import json
import re
from pathlib import Path

from typer.testing import CliRunner

import matcha.impact.engine as engine
from impact_helpers import REAL_FIXTURE, REPO, fake_discovery
from matcha.cli import app
from matcha.impact.engine import run_impact

REQ = "The character's canonical hairstyle changes to shoulder-length dark hair."
REF = REAL_FIXTURE / "reference" / "kite_male_neutral.png"


class _Always:
    name, model = "fake", "fake-1"

    def __init__(self, raw):
        self.raw = raw

    def available(self):
        return True, "ok"

    def classify(self, request, reference_image, candidate_image, context):
        return self.raw


def test_cli_unavailable_provider_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "discover", lambda: fake_discovery())
    out, md = tmp_path / "r.json", tmp_path / "r.md"
    res = CliRunner().invoke(
        app,
        ["impact", "--fixture", str(REAL_FIXTURE), "--request", REQ, "--reference", str(REF),
         "--output", str(out), "--summary", str(md), "--provider", "auto"],
    )
    assert res.exit_code == 0, res.output
    assert "provider unavailable" in res.output
    r = json.loads(out.read_text())
    assert r["counts"]["assets"] == 15 and r["counts"]["code_units"] == 8 and r["counts"]["relationships"] == 30
    assert r["counts"]["asset_status"] == {"REVIEW_REQUIRED": 15}
    assert all(a["reason"] == "provider unavailable" for a in r["assets"])
    assert r["provider"]["state"] == "UNAVAILABLE"
    assert r["counts"]["asset_provider_state"] == {"UNAVAILABLE": 15}
    assert r["counts"]["asset_review_cause"] == {"PROVIDER_UNAVAILABLE": 15}
    assert '"valid_provider_output": true' not in out.read_text()
    assert r["limitations"]
    assert r["provider"]["available"] is False and r["provider"]["missing"]
    assert r["unresolved_items"][0]["item"].startswith("Vision provider unavailable")
    assert r["unresolved_items"][0]["kind"] == "provider_unavailable"
    assert r["reference_asset"]["path"] == "reference/kite_male_neutral.png"
    for k in ("start", "end", "elapsed"):
        assert r["timing"][k]
    assert re.match(r"\d{2}:\d{2}:\d{2}\.\d{3}$", r["timing"]["elapsed"])
    assert "Provider unavailable" in md.read_text()
    for a in r["assets"]:
        assert a["item_type"] == "ASSET" and "test_case" not in a
        assert re.fullmatch(r"candidate-\d{2}", a["candidate_id"])
        assert a["evidence"][0]["anchor_type"] == "asset"
    for c in r["code"]:
        assert c["item_type"] == "CODE" and c["relationships"] and "test_case" not in c
    assert "test_case" not in r


def test_all_asset_action_propagates_to_downstream(tmp_path):
    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
        discovery_fn=fake_discovery,
        provider_obj=_Always({"status": "ASSET_ACTION", "confidence": 0.95, "reason": "hair visible"}),
    )
    assert r["counts"]["asset_status"] == {"ASSET_ACTION": 15}
    assert r["counts"]["relationship_status"] == {"DOWNSTREAM_USAGE": 30}
    assert r["counts"]["file_status"] == {"DOWNSTREAM_USAGE": 8}
    assert r["identifier_policy"]["policy"] == "preserved"


def test_identifier_change_gives_code_action(tmp_path):
    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
        discovery_fn=fake_discovery, identifier_policy="changed",
        provider_obj=_Always({"status": "ASSET_ACTION", "confidence": 0.95, "reason": "hair visible"}),
    )
    assert r["counts"]["relationship_status"] == {"CODE_ACTION": 30}
    assert r["counts"]["file_status"] == {"CODE_ACTION": 8}


def test_malformed_and_uncertain_provider_output_end_to_end(tmp_path):
    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "a.json",
        discovery_fn=fake_discovery, provider_obj=_Always("I think it's affected!"),
    )
    assert r["counts"]["asset_status"] == {"REVIEW_REQUIRED": 15}
    assert all("malformed provider output" in a["reason"] for a in r["assets"])
    assert r["counts"]["asset_provider_state"] == {"INVALID_OUTPUT": 15}
    assert r["counts"]["asset_review_cause"] == {"INVALID_PROVIDER_OUTPUT": 15}
    assert r["counts"]["relationship_status"] == {"REVIEW_REQUIRED": 30}

    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "b.json",
        discovery_fn=fake_discovery,
        provider_obj=_Always({"status": "UNAFFECTED", "confidence": 0.3, "reason": "maybe"}),
    )
    # low confidence never changes a determinate verdict; confidence is metadata
    assert r["counts"]["asset_status"] == {"UNAFFECTED": 15}
    assert all(a["classification"]["confidence"] == 0.3 for a in r["assets"])
    assert r["counts"]["asset_review_cause"] == {}
    assert r["counts"]["relationship_status"] == {"UNAFFECTED": 30}


def test_mixed_statuses_file_precedence(tmp_path):
    # The provider only sees opaque candidate ids; odd ids -> UNAFFECTED, even -> REVIEW_REQUIRED.
    class _Mixed(_Always):
        def classify(self, request, reference_image, candidate_image, context):
            if int(candidate_image.id.split("-")[1]) % 2:
                return {"status": "UNAFFECTED", "confidence": 0.9, "reason": "n/a"}
            return {"status": "REVIEW_REQUIRED", "confidence": 0.9, "reason": "unclear"}

    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
        discovery_fn=fake_discovery, provider_obj=_Mixed(None),
    )
    asset = {a["asset_path"]: a["status"] for a in r["assets"]}
    for c in r["code"]:
        rel = {x["relationship_status"] for x in c["relationships"]}
        for x in c["relationships"]:
            assert x["relationship_status"] == (
                "UNAFFECTED" if asset[x["related_asset"]] == "UNAFFECTED" else "REVIEW_REQUIRED"
            )
        # precedence: any REVIEW_REQUIRED relationship -> file REVIEW_REQUIRED; all UNAFFECTED -> UNAFFECTED
        assert c["file_status"] == ("REVIEW_REQUIRED" if "REVIEW_REQUIRED" in rel else "UNAFFECTED")
    assert {a["review_cause"] for a in r["assets"] if a["status"] == "REVIEW_REQUIRED"} == {"SEMANTIC_REVIEW_REQUIRED"}


def test_cli_has_no_confidence_threshold_option(tmp_path):
    res = CliRunner().invoke(
        app,
        ["impact", "--fixture", str(REAL_FIXTURE), "--request", "x", "--output", str(tmp_path / "o.json"),
         "--provider", "unavailable", "--confidence-threshold", "0.7"],
    )
    assert res.exit_code == 2 and "No such option" in res.output


def test_bad_inputs(tmp_path):
    (tmp_path / "emptyfx").mkdir()
    res = CliRunner().invoke(app, ["impact", "--fixture", str(tmp_path / "emptyfx"), "--request", "x", "--output", str(tmp_path / "o.json")])
    assert res.exit_code == 1 and "fixture manifest not found" in res.output
    res = CliRunner().invoke(
        app,
        ["impact", "--fixture", str(REAL_FIXTURE), "--request", "x", "--reference", "nope.png",
         "--output", str(tmp_path / "o.json"), "--provider", "unavailable"],
    )
    assert res.exit_code == 1 and "reference image not found" in res.output


def test_engine_package_is_blind_and_generic():
    """matcha/impact must not read ground truth or hard-code fixture specifics."""
    banned = [
        "EXPERIMENT-01", "HUMAN-BASELINE", "Structural relationship inventory", "docs/experiments",
        "EVIDENCE-PROTOCOL", "kite", "LI_ALIGN", "LI_EXPR_ALIAS", "LI_CIRCLE_LOCK", "LOVE32", "route_",
    ]
    for p in (REPO / "matcha" / "impact").glob("*.py"):
        text = p.read_text()
        for b in banned:
            assert b.lower() not in text.lower(), f"{p.name} contains {b!r}"
