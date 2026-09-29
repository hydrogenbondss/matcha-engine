"""Validation A: discovered relationships vs the worksheet's frozen inventory.

Evaluation-only test: it reads the worksheet (the engine never does).
"""

import sys

from impact_helpers import REAL_FIXTURE, REPO

sys.path.insert(0, str(REPO / "scripts"))
import impact_eval  # noqa: E402


def test_pairs_exactly_match_frozen_inventory():
    inv = impact_eval.load_inventory()
    assert len(inv) == 30
    r = impact_eval.compare_inventory(impact_eval.discovered_from_fixture(REAL_FIXTURE), inv)
    assert r["exact_pairs"] == 30
    assert r["extra_pairs"] == [] and r["missing_pairs"] == []
    assert r["pairs_ok"]


def test_evidence_agreement_is_reported():
    r = impact_eval.compare_inventory(
        impact_eval.discovered_from_fixture(REAL_FIXTURE), impact_eval.load_inventory()
    )
    e = r["evidence"]
    assert e["inventory_items"] > 0 and e["discovered_items"] > 0
    # informational floor so a regression is noticed; exact numbers are in the report
    assert e["identity_matched"] >= e["inventory_items"] - 5
