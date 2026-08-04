"""Per-model license surfacing for checkpoints and LoRAs.

Not legal advice. Catalog entries are best-effort summaries of commonly
cited terms; always verify the license on Civitai / Hugging Face / the
model card before shipping commercially.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CommercialStatus(str, Enum):
    """Whether model outputs are generally treated as commercially usable."""

    OK = "ok"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ModelLicense:
    name: str
    license_name: str
    commercial_outputs: CommercialStatus
    notes: str
    source_url: Optional[str] = None
    # Substrings matched case-insensitively against the filename.
    match_substrings: tuple[str, ...] = ()


# Built-in catalog. First match wins (more specific entries first).
_CATALOG: tuple[ModelLicense, ...] = (
    ModelLicense(
        name="Anything V5",
        license_name="Fair AI Public License 1.0-SD (lineage)",
        commercial_outputs=CommercialStatus.OK,
        notes=(
            "Anything-series checkpoints typically inherit Fair AI PL terms: "
            "the license covers the model weights, not outputs "
            '("output… not covered by this license"). Commercial use of '
            "generated sprites is commonly treated as OK — verify the "
            "specific file's license on Civitai/Hugging Face before shipping."
        ),
        source_url="https://civitai.com/articles/18619/what-the-license",
        match_substrings=("anythingv5", "anything-v5", "anything v5"),
    ),
    ModelLicense(
        name="NoobAI-XL",
        license_name="NoobAI license (claims no commercialization)",
        commercial_outputs=CommercialStatus.RESTRICTED,
        notes=(
            "WARNING: NoobAI-XL's published terms claim to prohibit "
            "commercialization of model-generated products. Do not treat "
            "outputs as commercially safe without reading the current "
            "license and getting independent confirmation."
        ),
        source_url="https://civitai.com/",
        match_substrings=("noobai", "noob_ai", "noob-ai"),
    ),
)


_UNKNOWN_CHECKPOINT = ModelLicense(
    name="Unknown checkpoint",
    license_name="Unknown — check model page",
    commercial_outputs=CommercialStatus.UNKNOWN,
    notes=(
        "No built-in license entry for this checkpoint. Look up the model "
        "on Civitai or Hugging Face and confirm output / commercial-use "
        "terms before shipping."
    ),
)

_UNKNOWN_LORA = ModelLicense(
    name="Unknown LoRA",
    license_name="Unknown — check model page",
    commercial_outputs=CommercialStatus.UNKNOWN,
    notes=(
        "No built-in license entry for this LoRA. Check the LoRA's Civitai "
        "/ Hugging Face page for commercial-use and derivative terms."
    ),
)


def lookup_model(filename: str, *, kind: str = "checkpoint") -> ModelLicense:
    """Return license info for a checkpoint or LoRA filename.

    Matching is case-insensitive substring against the catalog. Unknown
    files get a generic UNKNOWN status.
    """
    needle = (filename or "").lower()
    for entry in _CATALOG:
        for sub in entry.match_substrings:
            if sub in needle:
                return entry
    if kind == "lora":
        return _UNKNOWN_LORA
    return _UNKNOWN_CHECKPOINT


def _status_label(status: CommercialStatus) -> str:
    if status is CommercialStatus.OK:
        return "commercial outputs: likely OK (verify)"
    if status is CommercialStatus.RESTRICTED:
        return "commercial outputs: RESTRICTED — do not assume commercial OK"
    return "commercial outputs: UNKNOWN — check model page"


def format_license_report(
    checkpoint: str,
    lora: Optional[str] = None,
) -> str:
    """Human-readable license summary for CLI echo."""
    lines: list[str] = [
        "Model license status (not legal advice — verify yourself):",
    ]
    ckpt = lookup_model(checkpoint, kind="checkpoint")
    lines.append(f"  Checkpoint: {checkpoint}")
    lines.append(f"    → {ckpt.name} · {ckpt.license_name}")
    lines.append(f"    → {_status_label(ckpt.commercial_outputs)}")
    if ckpt.notes:
        # Indent multi-line notes cleanly.
        for note_line in ckpt.notes.splitlines():
            lines.append(f"    → {note_line}")
    if ckpt.source_url:
        lines.append(f"    → see {ckpt.source_url}")

    if lora:
        lr = lookup_model(lora, kind="lora")
        lines.append(f"  LoRA: {lora}")
        lines.append(f"    → {lr.name} · {lr.license_name}")
        lines.append(f"    → {_status_label(lr.commercial_outputs)}")
        for note_line in lr.notes.splitlines():
            lines.append(f"    → {note_line}")
        if lr.source_url:
            lines.append(f"    → see {lr.source_url}")
    else:
        lines.append("  LoRA: (none)")

    return "\n".join(lines)
