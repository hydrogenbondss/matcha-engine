import json

import pytest

from impact_helpers import REAL_FIXTURE, make_fixture
from matcha.impact.fixture import FixtureError, load_fixture, parse_excerpt_header, verify_asset_hashes


def test_real_fixture_scored_assets_derived_from_manifest():
    fx = load_fixture(REAL_FIXTURE)
    assert len(fx.assets) == 15
    assert len(fx.evidence_only_images) == 2
    manifest = json.loads((REAL_FIXTURE / "metadata/fixture-manifest.json").read_text())
    expected = {
        i["fixture_path"]
        for i in manifest["items"]
        if str(i.get("type", "")).startswith("image/") and i.get("direct_production_file") is True
    }
    assert {a.fixture_path for a in fx.assets} == expected
    assert all(a.game_path and a.game_path.startswith("images/") for a in fx.assets)
    assert verify_asset_hashes(fx) == []


def test_real_fixture_code_candidates_and_excerpts():
    fx = load_fixture(REAL_FIXTURE)
    paths = {c.fixture_path for c in fx.code_candidates}
    assert len(paths) == 11
    excerpts = [c for c in fx.code_candidates if c.is_excerpt]
    assert len(excerpts) == 7
    for c in excerpts:
        assert c.origin_path and c.origin_path.startswith("game/")
        assert c.excerpt_header.get("line_ranges")
        assert c.excerpt_header.get("limitation")


def test_scored_rule_is_generic(tmp_path):
    root = make_fixture(
        tmp_path / "fx",
        {"game/a.rpy": "label start:\n    return\n"},
        {
            "assets/x.png": {"game": "images/x.png"},
            "assets/y.png": {"game": "images/sub/y.png", "production_path": False},
            "reference/review_copy.png": {"direct": False},
        },
    )
    fx = load_fixture(root)
    assert {a.fixture_path: a.game_path for a in fx.assets} == {
        "assets/x.png": "images/x.png",
        "assets/y.png": "images/sub/y.png",
    }
    assert fx.evidence_only_images == ["reference/review_copy.png"]


def test_missing_manifest_and_missing_image(tmp_path):
    with pytest.raises(FixtureError):
        load_fixture(tmp_path)
    root = make_fixture(tmp_path / "fx", {}, {"assets/x.png": {"game": "images/x.png"}})
    (root / "assets/x.png").unlink()
    with pytest.raises(FixtureError):
        load_fixture(root)


def test_hash_mismatch_detected(tmp_path):
    root = make_fixture(tmp_path / "fx", {}, {"assets/x.png": {"game": "images/x.png"}})
    (root / "assets/x.png").write_bytes(b"changed")
    assert verify_asset_hashes(load_fixture(root)) == ["assets/x.png"]


def test_parse_excerpt_header():
    text = "# EVIDENCE EXCERPT (x)\n# source_path: /p/game/a.rpy\n# line_ranges: 1-2\n# --- a.rpy lines 1-2 ---\nshow a b\n"
    assert parse_excerpt_header(text) == {"source_path": "/p/game/a.rpy", "line_ranges": "1-2"}
    assert parse_excerpt_header("show a b\n") == {}
