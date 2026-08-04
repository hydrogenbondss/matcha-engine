"""Platform AI disclosure helpers (Steam survey + itch.io tagging).

Not legal advice. These drafts help you fill in platform forms; you must
verify current Steam / itch.io policy and your own model licenses.
"""

from __future__ import annotations

from typing import Optional

from matcha.licenses import format_license_report

STEAM_SURVEY_URL = (
    "https://partner.steamgames.com/doc/gettingstarted/contentsurvey"
)
ITCH_DISCLOSURE_URL = (
    "https://itch.io/t/4309690/generative-ai-disclosure-tagging"
)

_DISCLAIMER = (
    "> **Not legal advice.** Matcha Engine drafts this text to help you "
    "disclose AI-generated assets. Platform rules and model licenses change "
    "— verify Steam / itch.io policy and each model's license yourself "
    "before shipping."
)


def build_steam_survey_text(
    *,
    character_name: Optional[str] = None,
    checkpoint: Optional[str] = None,
    lora: Optional[str] = None,
    live_generated: bool = False,
) -> str:
    """Draft answers for Steam Content Survey §3 Generative AI.

    Matcha sprites are Pre-Generated artwork by default (generated offline
    via ComfyUI / Stable Diffusion, then shipped as static PNGs).
    """
    subject = (
        f'character sprites / side images for "{character_name}"'
        if character_name
        else "character sprites / side images"
    )
    models: list[str] = []
    if checkpoint:
        models.append(f"checkpoint `{checkpoint}`")
    if lora:
        models.append(f"LoRA `{lora}`")
    model_clause = (
        " Models used: " + "; ".join(models) + "."
        if models
        else ""
    )

    if live_generated:
        gen_type = (
            "**Live-Generated** — content is generated on the player's "
            "machine or via a live service during play. Confirm this matches "
            "your actual product before submitting."
        )
    else:
        gen_type = (
            "**Pre-Generated** — artwork was created before release with "
            "generative AI (Stable Diffusion via Matcha Engine / ComfyUI) "
            f"and ships as static image files ({subject}). "
            "It is not generated live during gameplay."
            f"{model_clause}"
        )

    return "\n".join(
        [
            "## Steam — Generative AI Content Survey",
            "",
            f"Reference: {STEAM_SURVEY_URL}",
            "",
            "### Suggested disclosure (Section 3 — Generative AI)",
            "",
            "- **Disclose AI assets:** Yes — Pre-Generated generative AI "
            "artwork is used.",
            f"- **Type:** {gen_type}",
            "- **What was AI-generated:** Character sprites and (if enabled) "
            "dialogue side-image portraits produced by Matcha Engine.",
            "- **What was not:** Hand-authored script, UI chrome, and any "
            "non-Matcha assets you created or licensed separately "
            "(adjust this list to match your game).",
            "",
            "Copy/adapt the above into the Steamworks Content Survey. "
            "Re-read Valve's current wording before submit — forms change.",
        ]
    )


def build_itch_reminder(
    *,
    character_name: Optional[str] = None,
    checkpoint: Optional[str] = None,
    lora: Optional[str] = None,
) -> str:
    """Reminder to use itch.io generative AI disclosure tagging."""
    extra = ""
    if character_name or checkpoint or lora:
        bits = []
        if character_name:
            bits.append(f'character "{character_name}"')
        if checkpoint:
            bits.append(f"checkpoint `{checkpoint}`")
        if lora:
            bits.append(f"LoRA `{lora}`")
        extra = " Relevant to this project: " + "; ".join(bits) + "."

    return "\n".join(
        [
            "## itch.io — Generative AI disclosure / tagging",
            "",
            f"Reference: {ITCH_DISCLOSURE_URL}",
            "",
            "- itch.io requires **generative AI disclosure / tagging** for "
            "pages that include AI-generated assets.",
            "- **Undisclosed AI assets can be de-indexed** (removed from "
            "browse/search). Tag and describe honestly.",
            "- Suggested tag / tool note: sprites generated with Stable "
            "Diffusion via Matcha Engine / ComfyUI (Pre-Generated artwork)."
            f"{extra}",
            "",
            "Check your itch.io project page settings for the current "
            "disclosure UI before publishing.",
        ]
    )


def build_disclosure_document(
    character_name: Optional[str] = None,
    checkpoint: Optional[str] = None,
    lora: Optional[str] = None,
    *,
    live_generated: bool = False,
) -> str:
    """Markdown document combining Steam + itch helpers and a license note."""
    sections = [
        "# Matcha Engine — AI disclosure draft",
        "",
        _DISCLAIMER,
        "",
        build_steam_survey_text(
            character_name=character_name,
            checkpoint=checkpoint,
            lora=lora,
            live_generated=live_generated,
        ),
        "",
        build_itch_reminder(
            character_name=character_name,
            checkpoint=checkpoint,
            lora=lora,
        ),
    ]
    if checkpoint:
        sections.extend(
            [
                "",
                "## Model license snapshot",
                "",
                "```",
                format_license_report(checkpoint, lora),
                "```",
                "",
                "Confirm each model's current license on Civitai / Hugging "
                "Face before relying on this snapshot.",
            ]
        )
    return "\n".join(sections) + "\n"
