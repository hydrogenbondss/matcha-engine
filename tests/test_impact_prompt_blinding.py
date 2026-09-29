"""The vision step never sees a candidate path, file name or stem."""

import json
from pathlib import Path

from impact_helpers import REAL_FIXTURE, fake_discovery, make_fixture
from matcha.impact.engine import run_impact
from matcha.impact.fixture import load_fixture
from matcha.impact.vision import ImageInput, OllamaProvider, build_prompt

REQ = "The character's canonical hairstyle changes to shoulder-length dark hair."
GOOD = {"status": "UNAFFECTED", "confidence": 0.9, "reason": "no hair visible"}


class _Recorder:
    name, model = "rec", None

    def __init__(self):
        self.calls = []

    def available(self):
        return True, "ok"

    def classify(self, request, reference_image, candidate_image, context):
        self.calls.append((request, reference_image, candidate_image, context))
        return GOOD


def _leaks(paths):
    out = set()
    for p in paths:
        pp = Path(p)
        out |= {p, pp.name, pp.stem}
    return out


def _assert_blind(calls, leaks):
    for request, ref, cand, ctx in calls:
        assert isinstance(cand, ImageInput) and (ref is None or isinstance(ref, ImageInput))
        assert set(ctx) == {"candidate_id"} and ctx["candidate_id"] == cand.id
        texts = [request, cand.id, repr(cand), json.dumps(ctx), build_prompt(request, ref is not None)]
        if ref is not None:
            texts += [ref.id, repr(ref)]
        for t in texts:
            for leak in leaks:
                assert leak not in t, f"{leak!r} leaked into provider input"
        assert not hasattr(cand, "path")


def test_synthetic_filenames_never_reach_the_provider(tmp_path):
    names = {
        "assets/hero_longhair_closeup.png": {"game": "images/hero_longhair_closeup.png"},
        "assets/background_empty_sky.png": {"game": "images/background_empty_sky.png"},
    }
    fx = make_fixture(tmp_path / "fx", {"game/a.rpy": 'image hero = "images/hero_longhair_closeup.png"\n'}, names)
    rec = _Recorder()
    r = run_impact(fixture=fx, request="The hero's hair becomes short.", reference=fx / "assets/hero_longhair_closeup.png",
                   output=tmp_path / "r.json", discovery_fn=fake_discovery, provider_obj=rec)
    assert len(rec.calls) == 2
    leaks = _leaks(list(names) + [n["game"] for n in names.values()]) | {"longhair", "closeup", "empty_sky", str(tmp_path)}
    _assert_blind(rec.calls, leaks)
    # the report maps the opaque id back to the asset outside the provider
    assert {a["candidate_id"] for a in r["assets"]} == {c[2].id for c in rec.calls}
    assert all(a["asset_path"] in names for a in r["assets"])


def test_real_fixture_asset_names_are_absent_from_prompt_and_payload(tmp_path, monkeypatch):
    fx = load_fixture(REAL_FIXTURE)
    names = [a.fixture_path for a in fx.assets] + [a.game_path for a in fx.assets if a.game_path]
    leaks = _leaks(names) | {str(REAL_FIXTURE), "reference/kite_male_neutral.png", "kite_male_neutral"}
    rec = _Recorder()
    run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REAL_FIXTURE / "reference/kite_male_neutral.png",
               output=tmp_path / "r.json", discovery_fn=fake_discovery, provider_obj=rec)
    assert len(rec.calls) == len(fx.assets) == 15
    _assert_blind(rec.calls, leaks)

    payloads = []

    def fake_post(self, path, payload):
        payloads.append(payload)
        return {"capabilities": ["vision"]} if path == "/api/show" else {"message": {"content": json.dumps(GOOD)}}

    monkeypatch.setattr(OllamaProvider, "_post", fake_post)
    run_impact(fixture=REAL_FIXTURE, request=REQ, reference=REAL_FIXTURE / "reference/kite_male_neutral.png",
               output=tmp_path / "o.json", discovery_fn=fake_discovery, provider_obj=OllamaProvider(model="m"))
    chats = [p for p in payloads if "messages" in p]
    assert len(chats) == 15
    for p in chats:
        content = p["messages"][0]["content"]
        assert "not in frame" not in content
        assert REQ in content
        assert set(p["messages"][0]) == {"role", "content", "images"}
        for leak in leaks:
            assert leak not in content


def test_prompt_contains_only_request_and_neutral_definitions():
    p = build_prompt("Some change.", True)
    assert "Some change." in p
    for verdict in ("ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED"):
        assert verdict in p
    assert "not in frame" not in p and "e.g." not in p
    assert ".png" not in p and "/" not in p.replace("0..1", "")
