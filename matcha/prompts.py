"""Prompt builders for consistent visual-novel sprites.

Keeps appearance locked in the character description and only varies
expression/pose wording, while adding framing positives/negatives that
discourage dual-sprite sheets and outfit drift.
"""

from __future__ import annotations

# Appended to every positive prompt so the model targets a single VN sprite.
SPRITE_FRAMING = (
    "single character, one person only, waist-up portrait, facing viewer, "
    "simple solid light background, clean visual novel sprite, "
    "same outfit, same hairstyle, same eye color"
)

# Appended to the configured negative prompt.
SPRITE_NEGATIVES = (
    "multiple views, collage, reference sheet, character sheet, split screen, "
    "dual pose, two girls, twin, comic panel, panel layout, text, watermark, "
    "border, frame, different outfit, wardrobe change, clothes change, "
    "eye color change, hair color change, full body crowd"
)

# Pose label → expression guidance. Outfit stays in the character description.
POSE_EXPRESSIONS: dict[str, str] = {
    "idle": "neutral calm expression, relaxed mouth, standing still",
    "happy": "happy expression, gentle smile, cheerful eyes",
    "sad": "sad expression, downturned eyes, slight frown",
    "surprised": "surprised expression, eyes wide, mouth slightly open",
    "angry": "angry expression, furrowed brows",
    "embarrassed": "embarrassed expression, blushing, looking aside",
}


def pose_expression(pose: str) -> str:
    key = pose.strip().lower()
    return POSE_EXPRESSIONS.get(key, f"{pose} expression, {pose} pose")


def build_pose_prompt(description: str, pose: str) -> str:
    """Build a positive prompt that locks identity and only varies expression."""
    desc = description.strip().rstrip(",")
    return f"{desc}, {pose_expression(pose)}, {SPRITE_FRAMING}"


def build_negative_prompt(base_negative: str) -> str:
    base = base_negative.strip().rstrip(",")
    if not base:
        return SPRITE_NEGATIVES
    return f"{base}, {SPRITE_NEGATIVES}"
