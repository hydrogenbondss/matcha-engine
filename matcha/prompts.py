"""Prompt builders for consistent visual-novel sprites.

Keeps appearance locked in the shared character description and only varies
expression / pose / outfit via the look sheet. Unknown pose names stay as
plain wording — they must not become ``"{pose} expression, {pose} pose"``.
"""

from __future__ import annotations

from typing import Optional

from matcha.config import PoseOverride

# Appended to every positive prompt so the model targets a single VN sprite.
# Outfit is *not* locked here — per-pose outfit families (apron vs henley)
# are the look sheet's job.
SPRITE_FRAMING = (
    "single character, one person only, waist-up portrait, clean visual novel sprite, "
    "same hairstyle, same eye color"
)

SPRITE_FRAMING_SAME_OUTFIT = "same outfit"

# Appended to the configured negative prompt.
SPRITE_NEGATIVES = (
    "multiple views, collage, reference sheet, character sheet, split screen, "
    "comic panel, panel layout, text, watermark, border, frame, "
    "eye color change, hair color change"
)

# Pose label → expression / body-language guidance. Outfit stays out of this
# map so a bartender apron is not implied for every name.
POSE_EXPRESSIONS: dict[str, str] = {
    "idle": "neutral calm expression, relaxed mouth, standing still",
    "neutral": "neutral calm expression, relaxed face, standing at ease",
    "happy": "happy expression, gentle smile, cheerful eyes",
    "sad": "sad expression, downturned eyes, slight frown",
    "surprised": "surprised expression, eyes wide, mouth slightly open",
    "angry": "angry expression, furrowed brows",
    "embarrassed": "embarrassed expression, blushing, looking aside",
    "warm": "warm soft smile, kind eyes, open posture",
    "withdrawn": "withdrawn expression, looking aside, closed-off posture, distant eyes",
    "smoking": "seated on a ledge, holding a cigarette, relaxed jaw",
    "relaxed": "relaxed expression, loose shoulders, easy stance",
    "soft": "soft gentle expression, quiet eyes, slight smile",
    "tired": "tired expression, heavy eyelids, weary mouth",
    "stressed": "stressed expression, tense brow, tight mouth",
    "gentle": "gentle expression, kind eyes, calm smile",
    "crossed_arms": "arms crossed over chest, reserved expression",
}


def pose_expression(pose: str) -> str:
    """Map a pose name to prompt wording.

    Known names use the look-sheet table. Unknown names become the pose
    token with underscores as spaces — never ``"{pose} expression, {pose} pose"``.
    """
    key = pose.strip().lower()
    if key in POSE_EXPRESSIONS:
        return POSE_EXPRESSIONS[key]
    cleaned = pose.strip().replace("_", " ")
    return cleaned or "neutral expression"


def build_pose_prompt(
    description: str,
    pose: str,
    override: Optional[PoseOverride] = None,
    *,
    outfit: Optional[str] = None,
    extra: Optional[str] = None,
) -> str:
    """Build a positive prompt that locks identity and varies pose/outfit.

    ``override.prompt`` / ``extra`` replace the expression-map wording when
    set. ``override.outfit`` / ``outfit`` append a per-pose clothing family
    and drop the global "same outfit" lock so one description cannot paint
    an apron onto every pose.
    """
    desc = description.strip().rstrip(",")
    ov = override
    outfit_text = (outfit if outfit is not None else (ov.outfit if ov else None)) or ""
    extra_text = (extra if extra is not None else (ov.prompt if ov else None)) or ""
    outfit_text = outfit_text.strip().rstrip(",")
    extra_text = extra_text.strip().rstrip(",")

    parts = [desc]
    if outfit_text:
        parts.append(outfit_text)
    if extra_text:
        parts.append(extra_text)
    else:
        parts.append(pose_expression(pose))
    parts.append(SPRITE_FRAMING)
    if not outfit_text:
        parts.append(SPRITE_FRAMING_SAME_OUTFIT)
    return ", ".join(p for p in parts if p)


def build_negative_prompt(
    base_negative: str,
    override: Optional[PoseOverride] = None,
) -> str:
    base = base_negative.strip().rstrip(",")
    extra = (override.extra_negative or "").strip().rstrip(",") if override else ""
    chunks = [c for c in (base, SPRITE_NEGATIVES, extra) if c]
    return ", ".join(chunks)
