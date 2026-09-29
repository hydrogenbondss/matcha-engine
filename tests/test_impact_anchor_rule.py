"""Generic anchor_type rule (production) and the evaluator's documented
anchor_type normalization, both on SYNTHETIC source lines."""

import sys

import pytest

from impact_helpers import REPO
from matcha.impact.model import CodeUnit
from matcha.impact.renpy_scan import literal_anchor_type, scan_unit

sys.path.insert(0, str(REPO / "scripts"))
import impact_eval  # noqa: E402

SRC = '''init python:
    TABLE_X = {
        "hero_a.png": (1.0, 0),
    }
    def pick(flag):
        pic = "images/hero_b.png"
        tag = "hero c" if flag else "hero d"
        obj.face = "images/hero_e.png"
        pic += "images/hero_f.png"
        d = {"img": "images/hero_g.png"}
        return "images/hero_h.png"
    def other():
        setup("images/hero_i.png")
        return pic == "images/hero_j.png"
'''


def _types():
    sr = scan_unit(CodeUnit(fixture_path="game/syn.rpy", is_excerpt=False, origin_path="game/syn.rpy"), SRC)
    out = {}
    for ln in sr.lines:
        for s in ln.strings:
            out[s] = literal_anchor_type(ln)
    return out


@pytest.mark.parametrize(
    "literal,expected",
    [
        ("hero_a.png", "config"),  # entry of an UPPER_CASE table literal
        ("images/hero_b.png", "assignment"),  # name = "file"
        ("hero c", "assignment"),  # name = "ident" if ... else ...
        ("images/hero_e.png", "assignment"),  # attribute target
        ("images/hero_f.png", "assignment"),  # augmented assignment
        ("images/hero_h.png", "statement"),  # return
        ("images/hero_i.png", "statement"),  # call argument
        ("images/hero_j.png", "statement"),  # comparison, not a binding
    ],
)
def test_generic_rule_depends_on_syntax_only(literal, expected):
    assert _types()[literal] == expected


def test_file_literal_and_identifier_literal_bindings_get_the_same_type():
    t = _types()
    assert t["images/hero_b.png"] == t["hero c"] == "assignment"


@pytest.mark.parametrize(
    "anchor_type,anchor,expected",
    [
        ("statement", 'pic = "images/hero_b.png"', "binding"),
        ("assignment", 'pic = "images/hero_b.png"', "binding"),
        ("assignment", 'tag = "hero c" if flag else "hero d"', "binding"),
        ("statement", '$ pic = "x.png"', "binding"),
        ("statement", 'define pic = "x.png"', "binding"),
        ("statement", '"img": "images/hero_g.png"', "binding"),
        ("statement", 'return "images/hero_h.png"', "statement"),
        ("statement", 'return pic == "images/hero_j.png"', "statement"),
        ("config", '"hero_a.png": (1.0, 0),', "config"),
        ("declaration", 'image hero = "hero.png"', "declaration"),
    ],
)
def test_evaluator_normalization_rule(anchor_type, anchor, expected):
    assert impact_eval.normalize_anchor_type(anchor_type, anchor) == expected


def test_normalization_is_symmetric_and_stays_visible():
    anchor = 'pic = "images/hero_b.png"'
    inv = {("game/syn.rpy", "assets/b.png"): [{"source_path": "game/syn.rpy", "anchor_type": "statement", "anchor": anchor,
                                               "locator": "source game/syn.rpy:6", "context": "c", "fingerprint": None, "fact": "f"}]}
    disc = {k: [dict(v[0], anchor_type="assignment")] for k, v in inv.items()}
    r = impact_eval.compare_inventory(disc, inv)
    assert r["evidence_identity"]["result"] == "FAIL"  # strict mismatch stays visible
    assert r["evidence_identity_normalized"]["result"] == "PASS"
    assert r["overall"] == "FAIL" and r["exit_code"] == 2  # strict identity is authoritative
    assert r["evidence_identity"]["explained_by_normalization"] is True
    r2 = impact_eval.compare_inventory(inv, disc)  # swapped sides
    assert r2["evidence_identity_normalized"]["result"] == "PASS"
