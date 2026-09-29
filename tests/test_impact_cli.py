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
         "--output", str(out), "--summary", str(md), "--provider", "auto", "--test-case", "A"],
    )
    assert res.exit_code == 0, res.output
    assert "provider unavailable" in res.output
    r = json.loads(out.read_text())
    assert r["counts"]["assets"] == 15 and r["counts"]["code_units"] == 8 and r["counts"]["relationships"] == 30
    assert r["counts"]["asset_status"] == {"REVIEW_REQUIRED": 15}
    assert all(a["reason"] == "provider unavailable" for a in r["assets"])
    assert r["provider"]["available"] is False and r["provider"]["missing"]
    assert r["unresolved_items"][0]["item"].startswith("Vision provider unavailable")
    assert r["reference_asset"]["path"] == "reference/kite_male_neutral.png"
    for k in ("start", "end", "elapsed"):
        assert r["timing"][k]
    assert re.match(r"\d{2}:\d{2}:\d{2}\.\d{3}$", r["timing"]["elapsed"])
    assert "Provider unavailable" in md.read_text()
    for a in r["assets"]:
        assert a["item_type"] == "ASSET" and a["test_case"] == "A"
        assert a["evidence"][0]["anchor_type"] == "asset"
    for c in r["code"]:
        assert c["item_type"] == "CODE" and c["relationships"]


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
    assert r["counts"]["relationship_status"] == {"REVIEW_REQUIRED": 30}

    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "b.json",
        discovery_fn=fake_discovery,
        provider_obj=_Always({"status": "UNAFFECTED", "confidence": 0.3, "reason": "maybe"}),
    )
    assert r["counts"]["asset_status"] == {"REVIEW_REQUIRED": 15}
    assert all(a["classification"]["provider_status"] == "UNAFFECTED" for a in r["assets"])


def test_mixed_statuses_file_precedence(tmp_path):
    class _Mixed(_Always):
        def classify(self, request, reference_image, candidate_image, context):
            if "side" in context["asset_path"]:
                return {"status": "UNAFFECTED", "confidence": 0.9, "reason": "n/a"}
            return {"status": "REVIEW_REQUIRED", "confidence": 0.9, "reason": "unclear"}

    r = run_impact(
        fixture=REAL_FIXTURE, request=REQ, reference=REF, output=tmp_path / "r.json",
        discovery_fn=fake_discovery, provider_obj=_Mixed(None),
    )
    files = {c["source_path"]: c["file_status"] for c in r["code"]}
    # a unit whose only relationships are UNAFFECTED stays UNAFFECTED; mixed -> REVIEW_REQUIRED
    assert "UNAFFECTED" in files.values() and "REVIEW_REQUIRED" in files.values()


def test_bad_inputs(tmp_path):
    res = CliRunner().invoke(app, ["impact", "--fixture", str(tmp_path), "--request", "x", "--output", str(tmp_path / "o.json")])
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
