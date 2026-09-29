"""Dynamic image/file references become structured unresolved items (synthetic)."""

import json

from impact_helpers import fake_discovery, make_fixture
from matcha.impact.engine import run_impact
from matcha.impact.fixture import load_fixture
from matcha.impact.graph import build_graph

SRC = '''init python:
    def _pick_sprite(name):
        path = "images/hero_" + name + ".png"
        if renpy.loadable(path):
            return path
        return None

image hero happy = "images/hero_happy.png"

label start:
    $ mood = "calm"
    $ a = f"images/hero_{mood}.png"
    $ b = "images/villain_%s.png" % mood
    $ c = "images/villain_{}.png".format(mood)
    show expression a
    $ d = _pick_sprite(mood)
    show hero happy
    return
'''

FILES = {"game/main.rpy": SRC}
IMAGES = {
    "assets/hero_happy.png": {"game": "images/hero_happy.png"},
    "assets/hero_calm.png": {"game": "images/hero_calm.png"},
    "assets/villain_calm.png": {"game": "images/villain_calm.png"},
    "assets/prop_box.png": {"game": "props/prop_box.png"},
}


def _graph(tmp_path):
    return build_graph(load_fixture(make_fixture(tmp_path / "fx", FILES, IMAGES)))


def _by_line(items):
    return {int(i["locator"].rsplit(":", 1)[1]): i for i in items}


def test_each_dynamic_construct_is_a_structured_unresolved_item(tmp_path):
    g = _graph(tmp_path)
    items = [u for u in g.unresolved if u.get("kind") == "dynamic_reference"]
    assert items == g.dynamic_refs
    by = _by_line(items)
    for i in items:
        for k in ("source_path", "locator", "snippet", "reasons", "candidate_assets", "evidence"):
            assert k in i
        assert i["source_path"] == "game/main.rpy" and i["reasons"]
    assert any("concatenation" in r for r in by[3]["reasons"])
    assert any("loadable()" in r for r in by[4]["reasons"])
    assert any("f-string" in r for r in by[12]["reasons"])
    assert any("%-formatting" in r for r in by[13]["reasons"])
    assert any(".format()" in r for r in by[14]["reasons"])
    assert any("expression" in r for r in by[15]["reasons"])
    assert any("_pick_sprite()" in r for r in by[16]["reasons"])
    # prefix candidates
    assert set(by[3]["candidate_assets"]) == {"assets/hero_happy.png", "assets/hero_calm.png"}
    assert by[13]["candidate_assets"] == ["assets/villain_calm.png"]
    assert "assets/prop_box.png" not in {a for i in items for a in i["candidate_assets"]}
    assert by[3]["snippet"] == 'path = "images/hero_" + name + ".png"'


def test_static_literal_is_not_flagged(tmp_path):
    g = _graph(tmp_path)
    lines = set(_by_line(g.dynamic_refs))
    assert 8 not in lines and 17 not in lines  # image declaration / plain show
    assert ("game/main.rpy", "assets/hero_happy.png") in g.pairs()


def test_dynamic_candidate_without_static_relationship_is_not_reported_unreferenced(tmp_path):
    fx = make_fixture(tmp_path / "fx", FILES, IMAGES)
    r = run_impact(fixture=fx, request="Hair changes.", reference=None, output=tmp_path / "r.json",
                   provider="unavailable", discovery_fn=fake_discovery)
    assets = {a["asset_path"]: a for a in r["assets"]}
    calm = assets["assets/villain_calm.png"]
    assert calm["dynamic_reference_candidates"]
    assert calm["status"] == "REVIEW_REQUIRED"
    nsr = {u["asset_path"]: u for u in r["unresolved_items"] if u.get("kind") == "no_static_relationship"}
    assert "must not be treated as unreferenced" in nsr["assets/villain_calm.png"]["item"]
    assert nsr["assets/villain_calm.png"]["dynamic_reference_locators"]
    assert r["counts"]["unresolved_by_kind"]["dynamic_reference"] == 7
    json.dumps(r)  # serialisable
