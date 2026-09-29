"""Validation A: discovered relationships vs the worksheet's frozen inventory.

Evaluation-only test: it reads the worksheet (the engine never does).
Pair-set correctness and evidence correctness are separate checks with
separate PASS/FAIL results; a pair PASS does not make the overall PASS.
"""

import sys

from impact_helpers import REAL_FIXTURE, REPO

sys.path.insert(0, str(REPO / "scripts"))
import impact_eval  # noqa: E402


def _real():
    return impact_eval.compare_inventory(impact_eval.discovered_from_fixture(REAL_FIXTURE), impact_eval.load_inventory())


def test_pairs_exactly_match_frozen_inventory():
    inv = impact_eval.load_inventory()
    assert len(inv) == 30
    p = _real()["pairs"]
    assert p["exact"] == 30 and p["extra"] == [] and p["missing"] == []
    assert p["result"] == "PASS"


def test_evidence_checks_are_reported_separately_and_mismatch_stays_visible():
    r = _real()
    for k in ("pairs", "evidence_identity", "evidence_occurrence", "field_agreement", "evidence_identity_normalized"):
        assert r[k]["result"] in ("PASS", "FAIL")
    i = r["evidence_identity"]
    assert i["inventory_items"] == i["discovered_items"] == 127
    # every occurrence aligns one-to-one
    assert r["evidence_occurrence"]["result"] == "PASS" and r["evidence_occurrence"]["aligned"] == 127
    # the overall verdict is the AND of the four strict checks, never the pair result alone
    strict = [r[k]["result"] for k in ("pairs", "evidence_identity", "evidence_occurrence", "field_agreement")]
    assert r["overall"] == ("PASS" if all(x == "PASS" for x in strict) else "FAIL")
    assert (r["exit_code"] & 1) == 0
    if i["result"] == "FAIL":
        assert r["overall"] == "FAIL" and r["exit_code"] & 2
        # any strict identity mismatch is an anchor_type-only difference that the documented
        # normalization accounts for; it is still reported as a strict FAIL
        assert r["evidence_identity_normalized"]["result"] == "PASS"
        for x in i["inventory_only"] + i["discovered_only"]:
            assert x["identity"][1] in ("statement", "assignment")
