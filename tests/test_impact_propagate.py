import pytest

from matcha.impact.propagate import (
    file_reason,
    file_status,
    infer_identifier_policy,
    relationship_status,
)


@pytest.mark.parametrize(
    "asset,policy,expected",
    [
        ("ASSET_ACTION", "preserved", "DOWNSTREAM_USAGE"),
        ("ASSET_ACTION", "changed", "CODE_ACTION"),
        ("ASSET_ACTION", "unknown", "REVIEW_REQUIRED"),
        ("UNAFFECTED", "preserved", "UNAFFECTED"),
        ("UNAFFECTED", "changed", "UNAFFECTED"),
        ("UNAFFECTED", "unknown", "UNAFFECTED"),
        ("REVIEW_REQUIRED", "preserved", "REVIEW_REQUIRED"),
        ("REVIEW_REQUIRED", "changed", "REVIEW_REQUIRED"),
        ("REVIEW_REQUIRED", "unknown", "REVIEW_REQUIRED"),
    ],
)
def test_relationship_status_table(asset, policy, expected):
    assert relationship_status(asset, policy) == expected


def test_relationship_status_rejects_unknown_values():
    with pytest.raises(ValueError):
        relationship_status("DOWNSTREAM_USAGE", "preserved")  # CODE status is not an asset status
    with pytest.raises(ValueError):
        relationship_status("ASSET_ACTION", "sometimes")


@pytest.mark.parametrize(
    "statuses,expected",
    [  # protocol §6 examples (1)-(5)
        (["UNAFFECTED", "DOWNSTREAM_USAGE", "UNAFFECTED"], "DOWNSTREAM_USAGE"),
        (["DOWNSTREAM_USAGE", "REVIEW_REQUIRED"], "DOWNSTREAM_USAGE"),
        (["CODE_ACTION", "REVIEW_REQUIRED"], "CODE_ACTION"),
        (["REVIEW_REQUIRED", "UNAFFECTED"], "REVIEW_REQUIRED"),
        (["UNAFFECTED", "UNAFFECTED"], "UNAFFECTED"),
        (["DOWNSTREAM_USAGE", "CODE_ACTION", "UNAFFECTED"], "CODE_ACTION"),
    ],
)
def test_file_status_precedence(statuses, expected):
    assert file_status(statuses) == expected
    assert expected in file_reason(statuses)


def test_file_status_needs_relationships_and_valid_values():
    with pytest.raises(ValueError):
        file_status([])  # example (6): out of scoring scope, no file status
    with pytest.raises(ValueError):
        file_status(["ASSET_ACTION"])  # asset and code statuses never mix


def test_asset_action_alone_never_creates_code_action():
    assert relationship_status("ASSET_ACTION", "preserved") != "CODE_ACTION"


@pytest.mark.parametrize(
    "request_text,policy",
    [
        ("The character's canonical hairstyle changes to long hair.", "preserved"),
        ("The canonical outfit changes to a materially different outfit.", "preserved"),
        ("Rename every sprite to the new naming scheme.", "unknown"),
        ("Move the files into images/v2/ with new file names.", "unknown"),
        ("Replace hero.png with a new plate.", "unknown"),
    ],
)
def test_identifier_policy_inference(request_text, policy):
    assert infer_identifier_policy(request_text)[0] == policy


def test_v1_code_action_limitation_is_documented():
    import matcha.impact.propagate as propagate
    from matcha.impact.propagate import V1_LIMITATIONS

    text = " ".join(V1_LIMITATIONS)
    assert "CODE_ACTION" in text and "DOWNSTREAM_USAGE" in text
    assert "semantic" in text.lower()
    assert "semantic" in (propagate.__doc__ or "").lower() and "limitation" in (propagate.__doc__ or "").lower()
