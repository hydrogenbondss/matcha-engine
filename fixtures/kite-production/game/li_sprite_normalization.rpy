# =========================================================
# LIVE LI SPRITE NORMALIZATION
# =========================================================
#
# Purpose:
# - Blake / Kite / Remy historically came in from mixed generations with mixed
#   canvas sizes.
# - Neo / Nia already route through a contain-fit transform, which makes them
#   feel more consistent in-game.
# - This file gives the other live LI families the same basic treatment so
#   display consistency depends less on the raw source PNG canvas.
#
# Notes:
# - This does NOT magically fix a bad source asset with an opaque background or
#   broken crop. It standardizes the display box so once better replacements
#   land, they sit more consistently without extra route work.

init -100 python:
    LI_PORTRAIT_CANVAS = (720, 960)
    LI_STAGE_ZOOM = 0.78

    # ── Unified cast color-grade (session 25 — option C) ─────────────────
    # Mixed-generation LI sprites differ in saturation/contrast/temperature,
    # which is a big part of the "looks like different projects" feeling.
    # This applies ONE gentle grade to every sprite routed through the
    # normalization helpers so the cast shares a tone.
    #
    # DEFAULT OFF. Color is a by-eye decision and this was authored without a
    # live view — turning an unseen global tint ON could regress the demo, and
    # it currently only reaches Blake/Kite/Remy (Neo/Nia route through their
    # own transform). To use it:
    #   1) set LI_GRADE_ENABLED = True
    #   2) boot, look at Blake/Kite/Remy in a scene, tune LI_GRADE
    #      (start subtle: SaturationMatrix(0.95) * ContrastMatrix(1.03))
    #   3) if it helps, wrap Neo/Nia's displayables in apply_li_grade(...) too
    #      so the WHOLE cast is graded (grading only some worsens the mismatch).
    LI_GRADE_ENABLED = False
    LI_GRADE = SaturationMatrix(0.95) * ContrastMatrix(1.03)

    def apply_li_grade(d):
        # Wrap any displayable in the cast grade (no-op when disabled).
        if LI_GRADE_ENABLED:
            return Transform(d, matrixcolor=LI_GRADE)
        return d

    # ── Per-character on-stage scale (calibrated from the dev SPRITE TEST) ────
    # The live build showed every figure at ~half the height it should be: heads
    # landing at mid-screen instead of the upper third, swimming in empty space,
    # the textbox swallowing the body. Root cause: a compounding 0.78 x 0.74
    # double-zoom shrank the cast to ~0.58 of stage size.
    #
    # Sources are framed differently (Blake = 3/4 body, Remy = full body), so a
    # single zoom can't size them equally — each gets its own multiplier on top
    # of LI_STAGE_ZOOM. Tune against the SPRITE TEST lineup: bigger = head rises
    # toward the green eye-band and the body fills down behind the textbox.
    ## 2026-07-11 restaging (author playtest verdict: "all the sprites seem
    ## wrong"). Measured the old values against real bottom-anchored scene
    ## composites (bg + sprite + textbox mock, proof grids in
    ## review/sprite_scale_grids/): Blake at 1.80 rendered ~1340px tall on a
    ## 1080px stage — 24% taller than the screen, hair clipping the top edge,
    ## venue blotted out; every ordinary line read as an extreme close-up.
    ## Remy at 1.85 (full-body source) had her HEAD CUT OFF entirely at
    ## bottom-anchored staging. New values picked by eye from 4-scale grids:
    ## the figure stands IN the room, air above the head, background reads,
    ## face still carries at dialogue distance.
    LI_CHAR_SCALE = {
        "blake": 1.45,   # was 1.80 — see grid: head upper-fifth, balcony/venue visible
        # 2026-09-15 layout followup: live plates changed since Aug-31 alpha
        # split (kite_male neutral now fills 928×1232; kite_female ~1116px
        # alpha). Pipeline: contain(720×960) × LI_STAGE_ZOOM 0.78 × scale ×
        # li_center 0.74. Target ~70% of 1080 (~756px) stand height.
        # kite_male 1.65 → ~84% (too tall); kite_female 0.97 → ~45% (too small).
        # New: 1.37 / 1.51 → ~70% each on measured alpha. blake 1.45 (~74%
        # female full-bleed) and remy 1.50 (~65–77% by plate) already in band.
        "kite_male": 1.37,    # was 1.65 — full-bleed plate; 1.37 ≈ 70% @1080
        "kite_female": 1.51,  # was 0.97 — shorter alpha plate; 1.51 ≈ 70% @1080
        "remy":  1.50,   # was 1.85 (head off-frame) — full figure fits, head just under top
    }

    # 2026-09-01 CODE-ALIGN vs KEEP lock (LI_SPRITE_AUDIT.md / li_align_metrics.tsv).
    # Extra zoom + yoffset on that filename so the same LI does not jump size
    # when the expression changes. Inner Transform yoffset stacks under idle ATL
    # — keep Kite male +19. Neo 1.04 / Nia yalign 1.0 lift 0 stay.
    # Female Kite stressed / tired / date: scale only (NEEDS-MJ pixels; do not
    # fake crown or jewelry with yoffset). Leftover plates (Female Blake /
    # Remy / Neo hopeful-relaxed-withdrawn / Nia) are CODE-ALIGN crutches —
    # jewelry/face/style still NEEDS-MJ. Do not overwrite V3 KEEP PNGs.
    # Revert a row: delete its key. Revert the pass: delete LI_ALIGN + the
    # _li_align lookups in _blake_sprite / _kite_sprite / _remy_sprite /
    # _neo_sprite / _nia_sprite + circle fallbacks (_li_circle_lock /
    # _normalized_li_sprite missing-file path) + say-chip / route-card
    # discs (_li_circle_disc).
    LI_ALIGN = {
        # Male Blake vs lock stage_h 845.9
        "blake_male_tank.png": (1.007, -61),
        "blake_male_relaxed.png": (0.903, 46),
        "blake_male_soft.png": (0.903, 46),
        "blake_male_polished.png": (0.880, 57),
        "blake_male_stressed.png": (1.169, -61),
        # Male Kite wired vs lock 716.6
        "kite_male_gentle.png": (1.011, -8),
        "kite_male_relaxed.png": (1.002, -2),
        "kite_male_warm.png": (0.998, 2),
        "kite_male_stressed.png": (0.996, 3),
        "kite_male_withdrawn.png": (0.975, 19),
        "kite_male_tired.png": (0.971, 22),
        # Female Kite KEEP vs lock 710.0
        "kite_female_relaxed.png": (0.996, 3),
        "kite_female_withdrawn.png": (0.997, 3),
        "kite_female_angry.png": (0.997, 3),
        "kite_female_warm.png": (0.990, 7),
        # Female Kite scale-only (CROWN_CUT / glossy = NEEDS-MJ)
        "kite_female_stressed.png": (0.982, 0),
        "kite_female_tired.png": (0.982, 0),
        "kite_female_date.png": (1.034, 0),
        # Female Blake vs lock 970.9 (GIANT lock; jewelry/face still NEEDS-MJ)
        "blake_female_neutral.png": (0.994, 0),  ## was blake_female.png (duplicate plate removed)
        "blake_female_relaxed.png": (1.057, 0),
        "blake_female_soft.png": (1.082, 0),
        "blake_female_oversized_shirt.png": (0.994, 0),
        "blake_female_stressed.png": (1.208, -177),
        "blake_female_panicked.png": (1.059, -64),
        "blake_female_polished.png": (0.909, 68),
        # Remy vs lock 1118.7 (GIANT lock; scale even except meltdown)
        "remy_meltdown.png": (0.997, 0),
        # Neo vs lock 719.7 (1.04 / lift -120 stay). Distressed KEEP.
        "neo_hopeful.png": (0.965, 14),
        "neo_relaxed.png": (0.822, 78),
        "neo_withdrawn.png": (0.841, 68),
        # Nia vs lock 874.9 (yalign 1.0 / lift 0 stay). Scale-only.
        "nia_hopeful.png": (1.002, 0),
        "nia_distressed.png": (1.003, 0),
        "nia_tired_alt.png": (1.002, 0),
        "nia_withdrawn.png": (1.110, 0),
        "nia_tired.png": (1.130, 0),
    }

    def _li_align(filename):
        return LI_ALIGN.get(filename, (1.0, 0))

    # Cropped side discs (not a new image). KEEP lock = air above the crown
    # (F-01 ~8%). Neo / Nia V3 KEEP already hold air — identity. Tight crops
    # zoom out on the same PNG. Jewelry/face still NEEDS-MJ.
    LI_CIRCLE_LOCK = {
        "side_neo.png": (1.0, 0.5),
        "side_nia.png": (1.0, 0.5),
        "side_blake.png": (1.0, 0.5),
        "side_blake_female.png": (0.92, 1.0),
        "side_kite_male.png": (0.92, 1.0),
        "side_kite_female.png": (0.92, 1.0),
        "side_remy.png": (0.92, 1.0),
    }

    def _li_circle_basename(rel_path):
        return rel_path.replace("\\", "/").rsplit("/", 1)[-1]

    def _li_circle_path(filename):
        name = _li_circle_basename(filename)
        if name.startswith("blake_female"):
            return "images/side_treated/side_blake_female.png"
        if name.startswith("blake"):
            return "images/side_treated/side_blake.png"
        if name.startswith("kite_female"):
            return "images/side_treated/side_kite_female.png"
        if name.startswith("kite_male") or name.startswith("kite "):
            return "images/side_treated/side_kite_male.png"
        if name.startswith("neo_"):
            return "images/side_treated/side_neo.png"
        if name.startswith("nia_"):
            return "images/side_treated/side_nia.png"
        if name.startswith("remy"):
            return "images/side_treated/side_remy.png"
        return None

    def _li_circle_lock(rel_path):
        # KEEP air-above on a cropped circle file. Do not overwrite V3 PNGs.
        if not rel_path or not renpy.loadable(rel_path):
            return Null()
        z, ya = LI_CIRCLE_LOCK.get(_li_circle_basename(rel_path), (1.0, 0.5))
        if z == 1.0 and ya == 0.5:
            return rel_path
        return Transform(Transform(rel_path, zoom=z), xysize=(400, 400), fit="contain", yalign=ya)

    # Image-statement aliases → the filename LI_ALIGN / stage helpers use.
    LI_EXPR_ALIAS = {
        ("blake_male", "panicked"): "blake_male_stressed.png",
        ("kite_male", "smoking"): "kite_male_smoking.png",
        ("kite_male", "soft"): "kite_male_soft.png",
        ("kite_male", "angry"): "kite_male_neutral.png",
        ("kite_male", "crossed_arms"): "kite_male_crossed_arms.png",
        ("kite_female", "soft"): "kite_female_warm.png",
        ("nia", "relaxed"): "nia_neutral.png",
        ("remy", "calm"): "remy.png",
        ("remy", "watching"): "remy.png",
        ("remy", "crying"): "remy_vulnerable.png",
        ("remy", "transition"): "remy_meltdown.png",
        ("remy", "berserk"): "remy_meltdown.png",
    }

    def _li_expr_filename(tag, attr):
        a = (attr or "").strip() or None
        aliased = LI_EXPR_ALIAS.get((tag, a))
        if aliased:
            return aliased
        if tag == "blake_male":
            return "blake_male_" + (a or "neutral") + ".png"
        if tag == "blake_female":
            if not a or a == "neutral":
                return "blake_female_neutral.png"
            return "blake_female_" + a + ".png"
        if tag == "kite_male":
            return "kite_male_" + (a or "neutral") + ".png"
        if tag == "kite_female":
            return "kite_female_" + (a or "neutral") + ".png"
        if tag == "neo":
            return "neo_" + (a or "neutral") + ".png"
        if tag == "nia":
            return "nia_" + (a or "neutral") + ".png"
        if tag == "remy":
            return "remy.png" if not a else "remy_" + a + ".png"
        return None

    def _li_showing_expression(who_key):
        # On-stage attribute → that plate's filename. None if nobody is planted.
        key = str(who_key or "").strip().lower()
        if key == "blake":
            tags = ("blake_female", "blake_male") if blake_variant == "female" else ("blake_male", "blake_female")
        elif key == "kite":
            tags = ("kite_female", "kite_male") if kite_variant == "female" else ("kite_male", "kite_female")
        elif key in ("neo", "nia"):
            tags = ("nia", "neo") if (key == "nia" or neo_variant == "female") else ("neo", "nia")
        elif key == "remy":
            tags = ("remy",)
        else:
            return None
        for tag in tags:
            if not renpy.showing(tag):
                continue
            try:
                attrs = renpy.get_attributes(tag)
            except Exception:
                attrs = None
            attr = None
            if attrs:
                for item in attrs:
                    if item:
                        attr = str(item)
            return _li_expr_filename(tag, attr)
        return None

    def _li_route_who_key(route):
        if route == "neo" and neo_variant == "female":
            return "nia"
        return route

    def _li_circle_disc(rel_path, expression=None):
        # KEEP air-above on the cropped PNG. Same expression LI_ALIGN as the
        # stage plate when that filename is known. Do not overwrite V3 files.
        locked = _li_circle_lock(rel_path)
        if not expression:
            return locked
        sm, yd = _li_align(_li_circle_basename(expression))
        if sm == 1.0 and yd == 0:
            return locked
        y = int(round(yd * (400.0 / float(LI_PORTRAIT_CANVAS[1]))))
        return Transform(locked, zoom=sm, yoffset=y)

    def _normalized_li_sprite(rel_path, canvas=LI_PORTRAIT_CANVAS, scale=1.0, yoffset=0):
        # Missing PNG (box female / Remy / Blake) must not predict-crash or blank.
        # Circle stand-in uses that expression's LI_ALIGN (caller scale/yoffset)
        # plus KEEP circle lock. Do not invent art.
        if renpy.loadable(rel_path):
            inner = Transform(rel_path, xysize=canvas, fit="contain")
        else:
            circle = _li_circle_path(rel_path)
            if not circle or not renpy.loadable(circle):
                return Null()
            inner = Transform(_li_circle_lock(circle), xysize=canvas, fit="contain")
        z = LI_STAGE_ZOOM * scale
        if LI_GRADE_ENABLED:
            out = Transform(inner, zoom=z, yoffset=yoffset, matrixcolor=LI_GRADE)
        else:
            out = Transform(inner, zoom=z, yoffset=yoffset)
        # 2026-07-11 motion pass (author: "the visuals were not interesting"):
        # every arrival gets a gentle rise-and-settle; expression swaps stay
        # still (on replace). li_sprite_enter is defined below at init 0 and
        # resolved when the image statements CALL this helper (init 500+),
        # so the late binding is safe. Finite one-shot animation — no
        # perpetual redraw cost on the author's lag-prone machine.
        return At(out, li_sprite_enter, li_sprite_idle)

    def _blake_sprite(filename):
        sm, yd = _li_align(filename)
        return _normalized_li_sprite(
            "images/" + filename,
            scale=LI_CHAR_SCALE["blake"] * sm,
            yoffset=yd,
        )

    def _kite_sprite(filename):
        scale_key = "kite_female" if filename.startswith("kite_female") else "kite_male"
        # Aug-31 subtraction-first recanvas: wired male plates were shifted
        # upward 24 source pixels to create a transparent bottom safety margin.
        # At the current width-fit and stage scale that is ~18.5 screen pixels;
        # +19 keeps the pre-recanvas baseline while preserving visible size.
        baseline_compensation = 0 if scale_key == "kite_female" else 19
        sm, yd = _li_align(filename)
        return _normalized_li_sprite(
            "images/" + filename,
            scale=LI_CHAR_SCALE[scale_key] * sm,
            yoffset=baseline_compensation + yd,
        )

    def _remy_sprite(filename):
        sm, yd = _li_align(filename)
        return _normalized_li_sprite(
            "images/" + filename,
            scale=LI_CHAR_SCALE["remy"] * sm,
            yoffset=yd,
        )


# One-shot entrance for every LI sprite routed through the helpers above
# (and neo_sprites.rpy). Show = rise+fade in; expression change = no re-pop.
transform li_sprite_enter:
    on show:
        alpha 0.0 yoffset 10
        easeout_quint 0.5 alpha 1.0 yoffset 0
    on replace:
        alpha 1.0 yoffset 0

## 2026-07-11 (author, comparing to Dream Daddy: "they have slight gestures
## or movements... while talking"). Composed via At() alongside li_sprite_enter
## on every LI sprite, so every static portrait breathes instead of sitting
## dead-still through pages of dialogue. Same amplitude class as the existing
## remy_breathe loop (phone_shell.rpy) and the already-live onboarding Remy
## portrait -- both run continuously on this exact machine without the
## documented lag/freeze issues (those traced to GL boot calibration and
## audio-thread crashes, not simple ATL position loops). Deliberately tiny
## (2px, 0.6% zoom) so it reads as breathing, not bobbing.
## 2026-07-16 perf fix (author: "extremely laggy"): the breathe used to animate
## zoom (1.0 -> 1.006), which forces a full per-frame texture rescale of every
## staged ~1000px sprite — a perpetual GPU cost multiplied by sprite count, on
## top of the now-actually-playing background loops. yoffset-only keeps the
## same 2px visible breathing as a cheap translate instead of a rescale.
transform li_sprite_idle:
    subpixel True
    yoffset 0
    # reduce_motion: rm() holds amplitude at 0 → static (same helper as LI emphasis).
    ease 3.4 yoffset rm(-2, 0)
    ease 3.4 yoffset 0
    repeat
