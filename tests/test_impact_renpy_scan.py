from collections import Counter

from impact_helpers import REAL_FIXTURE, make_fixture
from matcha.impact.fixture import load_fixture
from matcha.impact.graph import build_graph, match_assets
from matcha.impact.model import AssetUnit, CodeUnit
from matcha.impact.renpy_scan import parse_show_name, scan_unit, tokenize

EXCERPT = """# EVIDENCE EXCERPT (not a full copy)
# source_path: /proj/game/other.rpy
# line_ranges: 10-12,40-41
# limitation: test only
# --- other.rpy lines 10-12 ---
    if flag:
        show hero happy at left
    x = 1
# --- other.rpy lines 40-41 ---
    $ items = [{"image": "hero happy"}]
    show hero happy at left
"""

MAIN = """# header comment mentions hero_happy.png but comments are ignored
image hero happy = helper("hero_happy.png")
image hero sad = "images/hero_sad.png"
image villain calm = helper("villain.png")

init python:
    TABLE = {
        "hero_sad.png": (1.0, 0),
        ("hero", "alias"): "hero_happy.png",
    }
    def pick(a):
        return "images/hero_" + a + ".png"
    def side():
        return "images/side/side_hero.png"

label start:
    show hero happy at center
    show hero happy at center with dissolve
    show hero
    show hero unknownattr
    hide hero
    show screen hero_screen("hero happy.png")
    $ label_text = "not an image"
    return
"""


def _fx(tmp_path):
    return load_fixture(
        make_fixture(
            tmp_path / "fx",
            {"game/main.rpy": MAIN, "game/other.rpy.excerpt.txt": EXCERPT, "game/none.rpy": "define x = 1\n"},
            {
                "assets/hero_happy.png": {"game": "images/hero_happy.png"},
                "assets/hero_sad.png": {"game": "images/hero_sad.png"},
                "assets/side_hero.png": {"game": "images/side/side_hero.png"},
                "assets/unused.png": {"game": "images/unused.png"},
            },
        )
    )


def test_tokenize_strips_comments_not_strings():
    code, strings, bare, triple = tokenize('    x = "a # b"  # real comment')
    assert code == 'x = "a # b"'
    assert strings == ["a # b"]
    assert triple is None
    code, strings, _, _ = tokenize("kite \"don't\" 'it\\'s'")
    assert strings == ["don't", "it's"]


def test_parse_show_name():
    assert parse_show_name("hero happy at left, glitch") == "hero happy"
    assert parse_show_name("hero happy with dissolve") == "hero happy"
    assert parse_show_name("evidence photo:") == "evidence photo"
    assert parse_show_name("screen foo()") is None
    assert parse_show_name("expression Solid('#000')") is None


def test_excerpt_lines_map_to_original_source():
    unit = CodeUnit("game/other.rpy.excerpt.txt", True, "game/other.rpy", {"line_ranges": "10-12,40-41"})
    sr = scan_unit(unit, EXCERPT)
    shows = [u for u in sr.usages]
    assert [u.line.locator for u in shows] == ["source game/other.rpy:11", "source game/other.rpy:41"]
    assert all(u.line.block.startswith("# --- other.rpy lines") for u in shows)
    # header lines are never scanned as source
    assert all(ln.fixture_line > 4 for ln in sr.lines)


def test_match_assets_path_and_bare_filename():
    a = AssetUnit("assets/x.png", "images/sub/x.png", None)
    assert match_assets("images/sub/x.png", [a]) == [a]
    assert match_assets("game/images/sub/x.png", [a]) == [a]
    assert match_assets("x.png", [a]) == [a]
    assert match_assets("images/other/x.png", [a]) == []
    assert match_assets("images/x", [a]) == []


def test_graph_on_synthetic_fixture(tmp_path):
    g = build_graph(_fx(tmp_path))
    pairs = g.pairs()
    assert pairs == {
        ("game/main.rpy", "assets/hero_happy.png"),
        ("game/main.rpy", "assets/hero_sad.png"),
        ("game/main.rpy", "assets/side_hero.png"),
        ("game/other.rpy.excerpt.txt", "assets/hero_happy.png"),
    }
    assert [u.fixture_path for u in g.eligible_code] == ["game/main.rpy", "game/other.rpy.excerpt.txt"]
    assert [u.fixture_path for u in g.out_of_scope_code] == ["game/none.rpy"]

    happy = g.relationships[("game/main.rpy", "assets/hero_happy.png")]
    types = Counter(e.anchor_type for e in happy.evidence)
    # declaration + TABLE alias entry + 2 show statements; the comment is ignored,
    # the dynamic "images/hero_" + a + ".png" is ignored, "hero happy.png" (space) is not a match
    assert types == Counter({"declaration": 1, "config": 1, "statement": 2})
    shows = [e for e in happy.evidence if e.anchor_type == "statement"]
    assert shows[0].anchor == shows[1].anchor.replace(" with dissolve", "")
    assert "label start" in shows[0].context

    sad = g.relationships[("game/main.rpy", "assets/hero_sad.png")]
    assert Counter(e.anchor_type for e in sad.evidence) == Counter({"declaration": 1, "config": 1})

    side = g.relationships[("game/main.rpy", "assets/side_hero.png")]
    assert side.evidence[0].context == "function side"

    ex = g.relationships[("game/other.rpy.excerpt.txt", "assets/hero_happy.png")]
    assert ex.basis == {"fixture_proven"}
    kinds = [(e.source_path, e.anchor_type) for e in ex.evidence]
    assert kinds[0] == ("game/main.rpy", "declaration")  # the mapping declaration is cited
    assert Counter(k[1] for k in kinds) == Counter({"declaration": 1, "statement": 2, "assignment": 1})
    # two identical show anchors in different blocks are distinct occurrences
    st = [e for e in ex.evidence if e.anchor_type == "statement"]
    assert st[0].identity == st[1].identity and st[0].occurrence_identity != st[1].occurrence_identity

    items = [u["item"] for u in g.unresolved]
    assert any("hero unknownattr" in i for i in items)


def _all_evidence(g):
    for r in g.relationships.values():
        yield r, r.evidence


def test_real_fixture_relationships_structure():
    fx = load_fixture(REAL_FIXTURE)
    g = build_graph(fx)
    assert len(g.relationships) == 30
    assert len(g.eligible_code) == 8
    assert {u.fixture_path for u in g.out_of_scope_code} == {
        "game/characters.rpy",
        "game/options.rpy.excerpt.txt",
        "game/screens.rpy.excerpt.txt",
    }
    scored = {a.fixture_path for a in fx.assets}
    for r, evs in _all_evidence(g):
        assert r.related_asset in scored
        occ = [e.occurrence_identity for e in evs]
        assert len(occ) == len(set(occ)), f"duplicate occurrence identity in {r.source_path} -> {r.related_asset}"
        for e in evs:
            src = (REAL_FIXTURE / e.source_path).read_text()
            assert e.anchor in src, f"anchor not verbatim in {e.source_path}: {e.anchor}"
        if "fixture_proven" in r.basis:
            assert any(e.anchor_type == "declaration" and e.source_path != r.source_path for e in evs)

