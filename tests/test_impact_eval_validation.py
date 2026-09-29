"""Pair-set validation and evidence validation are separate (synthetic data).

Overall fails only for: a pair mismatch, a strict identity mismatch that the
accepted normalization does not explain, or an occurrence mismatch/duplicate.
Field (prose) differences are diagnostic only."""

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
    assert r["overall"] == "PASS" and r["exit_code"] == 0 and r["failures"] == []
    assert r["normalization_applied"] is False
    assert all(r[k]["result"] == "PASS" for k in ("pairs", "evidence_identity", "evidence_identity_normalized", "evidence_occurrence"))
    assert r["field_agreement"]["result"] == "DIAGNOSTIC" and r["field_agreement"]["all_fields_equal"] is True


def test_pairs_match_but_evidence_identity_differs_is_not_pass():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/a.png")][0]["anchor"] = "show a sad"
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["pairs"]["result"] == "PASS"
    assert r["evidence_identity"]["result"] == "FAIL"
    assert r["evidence_identity_normalized"]["result"] == "FAIL"  # no accepted normalization explains it
    assert r["overall"] == "FAIL" and r["failures"] == ["evidence_identity"]
    assert r["exit_code"] == 2
    # aligned by locator, the anchor difference is a field disagreement too
    assert r["evidence_occurrence"]["result"] == "PASS"
    assert r["field_agreement"]["anchor_equal"] == 1


def test_pair_mismatch_is_a_distinct_failure():
    disc = _copy(BASE)
    disc[("game/y.rpy", "assets/a.png")] = [_e("show a happy", src="game/y.rpy", locator="source game/y.rpy:5")]
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["pairs"]["result"] == "FAIL" and r["pairs"]["extra"] == [("game/y.rpy", "assets/a.png")]
    assert r["exit_code"] & 1 and "pairs" in r["failures"]
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
    assert r["exit_code"] == 4 and r["failures"] == ["evidence_occurrence"] and r["overall"] == "FAIL"


def test_duplicate_occurrence_identity_alone_fails():
    # both sides agree position by position, but the discovered side cannot tell two occurrences apart
    two = [_e("show a happy", locator="source game/x.rpy:1", context="c1"),
           _e("show a happy", locator="source game/x.rpy:2", context="c2")]
    inv = {("game/x.rpy", "assets/a.png"): [dict(e) for e in two]}
    disc = {("game/x.rpy", "assets/a.png"): [dict(e, context="same") for e in two]}
    r = impact_eval.compare_inventory(disc, inv)
    o = r["evidence_occurrence"]
    assert o["aligned"] == 2 and not o["unaligned_inventory"] and not o["unaligned_discovered"]
    assert [d["side"] for d in o["duplicate_occurrence_identity"]] == ["discovered"]
    assert o["result"] == "FAIL" and r["overall"] == "FAIL" and r["exit_code"] == 4


def test_distinct_prose_is_enough_to_distinguish_occurrences():
    # contexts differ from the inventory's wording but still distinguish the two occurrences
    two = [_e("show a happy", locator="source game/x.rpy:1", context="c1"),
           _e("show a happy", locator="source game/x.rpy:2", context="c2")]
    inv = {("game/x.rpy", "assets/a.png"): [dict(e) for e in two]}
    disc = {("game/x.rpy", "assets/a.png"): [dict(two[0], context="first"), dict(two[1], context="second")]}
    r = impact_eval.compare_inventory(disc, inv)
    assert r["evidence_occurrence"]["result"] == "PASS"
    assert r["field_agreement"]["context_equal"] == 0
    assert r["overall"] == "PASS" and r["exit_code"] == 0


def test_field_agreement_counts_each_field():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/b.png")][0].update(context="other", fingerprint="fp", fact="other fact")
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    f = r["field_agreement"]
    assert (f["aligned"], f["anchor_equal"], f["anchor_type_equal"], f["context_equal"], f["fingerprint_equal"], f["fact_equal"]) == (2, 2, 2, 1, 1, 1)
    assert f["result"] == "DIAGNOSTIC" and f["all_fields_equal"] is False and f["affects_overall"] is False
    assert r["pairs"]["result"] == r["evidence_identity"]["result"] == r["evidence_occurrence"]["result"] == "PASS"
    # prose differences never fail the overall result
    assert r["overall"] == "PASS" and r["exit_code"] == 0 and r["failures"] == []


def test_strict_mismatch_explained_by_normalization_passes_with_normalization():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/b.png")][0]["anchor_type"] = "statement"  # binding anchor, other label
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["evidence_identity"]["result"] == "FAIL"  # stays visible
    assert r["evidence_identity_normalized"]["result"] == "PASS"
    assert r["evidence_identity_normalized"]["explains_strict_mismatch"] is True
    assert r["overall"] == "PASS_WITH_NORMALIZATION" and r["normalization_applied"] is True
    assert r["accepted_normalizations"] == ["anchor_type_binding"]
    assert r["exit_code"] == 0 and r["failures"] == []


def test_normalization_does_not_rescue_other_failures():
    disc = _copy(BASE)
    disc[("game/x.rpy", "assets/b.png")][0]["anchor_type"] = "statement"
    disc[("game/y.rpy", "assets/a.png")] = [_e("show a happy", src="game/y.rpy", locator="source game/y.rpy:5")]
    r = impact_eval.compare_inventory(disc, _copy(BASE))
    assert r["overall"] == "FAIL" and r["normalization_applied"] is False and "pairs" in r["failures"]


def test_cli_exit_code_is_bitmask(tmp_path):
    # the real fixture: pairs PASS, so bit 1 is never set; the process exit mirrors exit_code
    res = subprocess.run([sys.executable, str(REPO / "scripts/impact_eval.py"), "validate-inventory"],
                         capture_output=True, text=True)
    assert "[A PASS] pairs:" in res.stdout and "OVERALL:" in res.stdout
    assert res.returncode & 1 == 0
    passed = "OVERALL: PASS " in res.stdout or "OVERALL: PASS_WITH_NORMALIZATION " in res.stdout
    assert passed == (res.returncode == 0)
