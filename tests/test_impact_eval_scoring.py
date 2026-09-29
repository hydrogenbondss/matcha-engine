"""ASSET scoring per protocol §17.1 / §18: REVIEW_REQUIRED is neither positive
nor negative; precision/recall only over determinate GT AND determinate output."""

import sys

from impact_helpers import REPO

sys.path.insert(0, str(REPO / "scripts"))
import impact_eval  # noqa: E402

AA, UN, RR = "ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED"


def _score(pairs):
    gt = {f"a{i}": g for i, (g, _) in enumerate(pairs)}
    auto = {f"a{i}": a for i, (_, a) in enumerate(pairs)}
    return impact_eval.score_assets(gt, auto)


def test_all_review_required_output_gives_undefined_not_zero():
    s = _score([(AA, RR)] * 3 + [(UN, RR)] * 2 + [(RR, RR)])
    assert (s["TP"], s["FP"], s["FN"], s["TN"]) == (0, 0, 0, 0)  # AA+RR is not FN, UN+RR is not FP
    assert s["precision"] is None and s["recall"] is None
    assert s["matcha_review_rate"] == 1.0 and s["coverage"] == 0.0
    assert s["ground_truth_review_rate"] == round(1 / 6, 4)
    assert s["scored_binary_items"] == 0
    assert s["matcha_review_required_on_gt_determinate"] == 5


def test_rr_never_counts_as_positive_or_negative():
    s = _score([(AA, AA), (AA, RR), (AA, UN), (UN, AA), (UN, RR), (UN, UN), (UN, UN), (RR, AA), (RR, UN)])
    assert (s["TP"], s["FP"], s["FN"], s["TN"]) == (1, 1, 1, 2)
    assert s["scored_binary_items"] == 5  # GT RR rows and automated RR columns excluded
    assert s["precision"] == 0.5 and s["recall"] == 0.5
    assert s["matcha_review_required"] == 2 and s["ground_truth_review_required"] == 2
    assert s["ground_truth_determinate"] == 7
    assert s["coverage"] == round(7 / 9, 4) and s["matcha_review_rate"] == round(2 / 9, 4)


def test_confusion_matrix_is_full_3x3_including_review_required():
    s = _score([(AA, AA), (AA, RR), (UN, RR), (RR, UN), (RR, RR)])
    m = s["confusion_matrix"]
    assert list(m) == [AA, UN, RR] and all(list(row) == [AA, UN, RR] for row in m.values())
    assert m[AA] == {AA: 1, UN: 0, RR: 1}
    assert m[UN] == {AA: 0, UN: 0, RR: 1}
    assert m[RR] == {AA: 0, UN: 1, RR: 1}
    assert sum(sum(r.values()) for r in m.values()) == 5


def test_precision_defined_recall_undefined():
    s = _score([(UN, AA), (UN, UN)])
    assert s["precision"] == 0.0 and s["recall"] is None


def test_asset_sets_must_match():
    import pytest

    with pytest.raises(ValueError):
        impact_eval.score_assets({"a": AA}, {"b": AA})


def test_compare_report_uses_protocol_scoring_and_reports_causes():
    base = {
        "timing": {"elapsed": "00:01:00.000"},
        "assets": [{"asset_path": "x.png", "status": AA}, {"asset_path": "y.png", "status": UN}],
        "code": [{"source_path": "s.rpy", "file_status": "DOWNSTREAM_USAGE",
                  "relationships": [{"related_asset": "x.png", "relationship_status": "DOWNSTREAM_USAGE"}]}],
    }
    rep = {
        "timing": {"elapsed": "00:00:01.000"},
        "provider": {"name": "unavailable", "model": None, "state": "UNAVAILABLE", "available": False},
        "assets": [{"asset_path": p, "status": RR, "review_cause": "PROVIDER_UNAVAILABLE"} for p in ("x.png", "y.png")],
        "code": [{"source_path": "s.rpy", "file_status": RR,
                  "relationships": [{"related_asset": "x.png", "relationship_status": RR}]}],
    }
    r = impact_eval.compare_report(rep, base, test="Z")
    a = r["assets"]
    assert r["test"] == "Z" and r["provider"]["state"] == "UNAVAILABLE"
    assert a["FN"] == 0 and a["FP"] == 0 and a["precision"] is None and a["recall"] is None
    assert a["matcha_review_causes"] == {"PROVIDER_UNAVAILABLE": 2}
    c = r["relationships"]
    assert c["confusion_matrix"]["DOWNSTREAM_USAGE"][RR] == 1
    assert c["code_action_precision"] is None
    assert c["missed_downstream"] == 0 and c["downstream_gt_automated_review_required"] == 1
    assert list(r["code"]["confusion_matrix"]) == list(impact_eval.CODE_STATUSES)
