"""analysis_completeness: static dependency discovery completeness, kept
separate from provider execution state."""

from impact_helpers import fake_discovery, make_fixture
from matcha.impact.engine import NON_DEPENDENCY_KINDS, analysis_completeness, run_impact
from matcha.impact.report import render_markdown
from test_impact_dynamic_refs import FILES as DYN_FILES, IMAGES as DYN_IMAGES

CLEAN = '''image hero happy = "images/hero_happy.png"

label start:
    show hero happy
    return
'''


def _run(tmp_path, files, images, **kw):
    fx = make_fixture(tmp_path / "fx", files, images)
    return run_impact(fixture=fx, request="Hair changes.", reference=None, output=tmp_path / "r.json",
                      discovery_fn=fake_discovery, **({"provider": "unavailable"} | kw))


def test_dynamic_references_make_analysis_incomplete(tmp_path):
    r = _run(tmp_path, DYN_FILES, DYN_IMAGES)
    assert r["analysis_completeness"] == "INCOMPLETE"
    assert r["unresolved_dependency_kinds"] == {"dynamic_reference": 7}
    assert r["unresolved_dependency_count"] == 7
    assert r["static_relationships"] == len([1 for c in r["code"] for _ in c["relationships"]])
    assert "NOT a claim that all production dependencies were established" in r["completeness_statement"]
    md = render_markdown(r)
    assert "Analysis completeness: **INCOMPLETE**" in md and "dynamic_reference 7" in md


def test_clean_fixture_is_complete_even_with_provider_unavailable(tmp_path):
    r = _run(tmp_path, {"game/main.rpy": CLEAN}, {"assets/hero_happy.png": {"game": "images/hero_happy.png"}})
    kinds = {u["kind"] for u in r["unresolved_items"]}
    assert kinds == {"provider_unavailable"}  # operational, not a dependency
    assert r["analysis_completeness"] == "COMPLETE"
    assert r["unresolved_dependency_count"] == 0 and r["unresolved_dependency_kinds"] == {}
    assert r["static_relationships"] == 1
    assert "not proof that all production dependencies were established" in r["completeness_statement"]
    # provider execution is reported separately
    assert r["provider_execution"]["provider_state"] == "UNAVAILABLE"
    assert r["provider_execution"]["assets_with_valid_provider_output"] == 0
    assert "Analysis completeness: **COMPLETE**" in render_markdown(r)


def test_atl_image_block_is_an_unsupported_construct(tmp_path):
    src = CLEAN + '''
image hero blink:
    "images/hero_happy.png"
    pause 1.0
'''
    r = _run(tmp_path, {"game/main.rpy": src}, {"assets/hero_happy.png": {"game": "images/hero_happy.png"}})
    assert r["analysis_completeness"] == "INCOMPLETE"
    assert r["unresolved_dependency_kinds"].get("scanner_limitation", 0) >= 1


def test_completeness_rule_on_synthetic_items():
    assert analysis_completeness([], 3)["analysis_completeness"] == "COMPLETE"
    only_non_deps = [{"kind": k} for k in NON_DEPENDENCY_KINDS]
    assert analysis_completeness(only_non_deps, 0)["analysis_completeness"] == "COMPLETE"
    for kind in ("dynamic_reference", "unresolved_image_name", "conflicting_declaration",
                 "ambiguous_literal", "scanner_limitation", "some_future_kind"):
        c = analysis_completeness([{"kind": kind}, {"kind": "provider_unavailable"}], 5)
        assert c["analysis_completeness"] == "INCOMPLETE" and c["unresolved_dependency_kinds"] == {kind: 1}
        assert c["static_relationships"] == 5 and c["unresolved_dependency_count"] == 1
