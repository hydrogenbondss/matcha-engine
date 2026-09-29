"""Pair-set validation and evidence validation are separate (synthetic data)."""

import subprocess
import sys

from impact_helpers import REPO

sys.path.insert(0, str(REPO / "scripts"))
import impact_eval  # noqa: E402


def _e(anchor, anchor_type="statement", locator="source game/x.rpy:1", src="game/x.rpy", **kw):
    return {"source_path": src, "anchor_type": anchor_type, "anchor": anchor, "locator": locator,
            "context": kw.get("context", "ctx"), "fingerprint": kw.get("fingerprint"), "fact": kw.get("fact", "f")}


BASE = {
    ("game/x.rpy", "assets/a.png"): [_e('show a happy', "statement", "source game/x.rpy:1")],
    ("game/x.rpy", "assets/b.png"): [_e('p = "images/b.png"', "assignment", "source game/x.rpy:2")],
}


def _copy(d):
    return {k: [dict(e) for e in v] for k, v in d.items()}


def test_all_pass():
    r = impact_eval.compare_inventory(_copy(BASE), _copy(BASE))
    assert r["overall"] == "PASS" and r["exit_code"] == 0
    assert all(r[k]["result"] == "PASS" for k in ("pairs", "evidence_identity", "evidence_occurrence", "field_agreement"))


def test_pairs_match_but_evidence_identity_differs_is_not_pass():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/a.png")][0]["anchor"] = "show a sad"
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["pairs"]["result"] == "PASS"
    assert r["evidence_identity"]["result"] == "FAIL"
    assert r["overall"] == "FAIL"
    assert r["exit_code"] & 2 and not r["exit_code"] & 1
    # aligned by locator, the anchor difference is a field disagreement too
    assert r["evidence_occurrence"]["result"] == "PASS"
    assert r["field_agreement"]["anchor_equal"] == 1


def test_pair_mismatch_is_a_distinct_failure():
    disc = _copy(BASE)
    disc[("game/y.rpy", "assets/a.png")] = [_e("show a happy", src="game/y.rpy", locator="source game/y.rpy:5")]
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["pairs"]["result"] == "FAIL" and r["pairs"]["extra"] == [("game/y.rpy", "assets/a.png")]
    assert r["exit_code"] & 1
    # the extra pair's evidence is also reported on the evidence side, in its own fields
    assert len(r["evidence_identity"]["discovered_only"]) == 1
    assert r["overall"] == "FAIL"


def test_occurrence_mismatch_duplicate_and_field_disagreement():
    disc = _copy(BASE)
    extra = _e('show a happy', "statement", "source game/x.rpy:9")
    disc[("game/x.rpy", "assets/a.png")].append(extra)
    inv = _copy(BASE)
    inv[("game/x.rpy", "assets/a.png")].append(_e('show a happy', "statement", "source game/x.rpy:7"))
    r = impact_eval.compare_inventory(disc, inv)
    # same identity multiset (2 x show a happy on each side) ...
    assert r["evidence_identity"]["result"] == "PASS"
    # ... but the occurrences are at different positions and share context+fingerprint
    o = r["evidence_occurrence"]
    assert o["result"] == "FAIL"
    assert len(o["unaligned_inventory"]) == 1 and len(o["unaligned_discovered"]) == 1
    assert o["duplicate_occurrence_identity"]
    assert r["exit_code"] & 4 and not r["exit_code"] & 3


def test_field_agreement_counts_each_field():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/b.png")][0].update(context="other", fingerprint="fp", fact="other fact")
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    f = r["field_agreement"]
    assert (f["aligned"], f["anchor_equal"], f["anchor_type_equal"], f["context_equal"], f["fingerprint_equal"], f["fact_equal"]) == (2, 2, 2, 1, 1, 1)
    assert f["result"] == "FAIL" and r["exit_code"] == 8
    assert r["pairs"]["result"] == r["evidence_identity"]["result"] == r["evidence_occurrence"]["result"] == "PASS"


def test_cli_exit_code_is_bitmask(tmp_path):
    # the real fixture: pairs PASS, so bit 1 is never set; the process exit mirrors exit_code
    res = subprocess.run([sys.executable, str(REPO / "scripts/impact_eval.py"), "validate-inventory"],
                         capture_output=True, text=True)
    assert "[PASS] pairs:" in res.stdout and "OVERALL:" in res.stdout
    assert res.returncode & 1 == 0
    assert ("OVERALL: PASS" in res.stdout) == (res.returncode == 0)
