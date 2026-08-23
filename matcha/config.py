from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class PoseOverride(BaseModel):
    """Per-pose look-sheet extras. Outfit families live here, not in the
    shared description, so an apron on the bar set does not paint onto
    ``smoking``.
    """

    prompt: Optional[str] = None
    outfit: Optional[str] = None
    # Key into CharacterConfig.outfit_families. Used when outfit is unset.
    family: Optional[str] = None
    extra_negative: Optional[str] = None


class CharacterConfig(BaseModel):
    """A character definition loaded from a YAML config.

    Model selection lives here, not in code: the checkpoint and LoRA are
    per-character (or per-project) choices, and the pair must be trained on
    the same base model family (an SD1.5 LoRA on an SDXL checkpoint fails or
    silently degrades output).
    """

    name: str
    description: str
    poses: list[str]
    # Look-sheet extras keyed by pose name. Also accepted inline on each
    # poses: entry as a mapping with a name: key (normalized below).
    pose_overrides: dict[str, PoseOverride] = Field(default_factory=dict)
    # Named outfit families (apron_bar / home_henley / withdrawn_dark).
    # Poses reference these via pose_overrides.family so one description
    # cannot paint a single outfit onto every pose.
    outfit_families: dict[str, str] = Field(default_factory=dict)
    # Display-only aliases that must not become their own files.
    # Echo: angry → stressed (kite_male stressed.png).
    pose_aliases: dict[str, str] = Field(default_factory=dict)
    # Dest / sandbox filename. Echo live: "{name} {pose}.png" (space).
    # Underscore "{name}_{pose}.png" will not drop into Echo.
    # None: local output uses underscore; --copy-only uses the space template.
    filename_template: Optional[str] = None
    # Ren'Py scaffolding options (the deploy "last mile").
    display_name: Optional[str] = None  # Character() display name; defaults to name.title()
    color: Optional[str] = None  # dialogue name color, e.g. "#ffcc00"
    layered: bool = False  # emit a layeredimage grouping poses as attributes
    side_image: bool = False  # emit side-image defs + wire Character(image=...)
    # Fraction of sprite height kept for side portraits (top-center crop).
    # ~0.45 ≈ head/shoulders on typical waist-up VN sprites.
    side_image_height_ratio: float = Field(default=0.45, gt=0.0, le=1.0)
    checkpoint: str = "anythingV5PrtRE.safetensors"
    # Default None = base checkpoint only (trusted first success).
    # Optional LoRAs are machine-specific; on Mac MPS prefer --lora none
    # first, then try a known-good LoRA (e.g. last.safetensors @ 0.7).
    lora: Optional[str] = None
    lora_strength: float = 0.7
    negative_prompt: str = (
        "low quality, blurry, worst quality, deformed, bad anatomy, "
        "extra limbs, bad hands"
    )
    width: int = 512
    height: int = 512
    # Optional post-generation resize (fit within, aspect preserved).
    # Ren'Py 720p projects typically want sprites no taller than the screen.
    resize_max_width: Optional[int] = None
    resize_max_height: Optional[int] = None
    steps: int = 20
    cfg: float = 8.0
    seed: Optional[int] = None
    # After the first pose, later poses img2img from it at this denoise
    # (0.45–0.65 typical). Set to 1.0 to disable chaining (pure txt2img).
    # Default off: Mac MPS currently glitches partial-denoise img2img.
    consistency_denoise: float = Field(default=1.0, ge=0.0, le=1.0)
    # IP-Adapter identity lock: later poses condition on the first sprite.
    # 0.0 = off. ~0.55–0.75 typical on CUDA. Currently corrupts on Mac MPS.
    ip_adapter_weight: float = Field(default=0.0, ge=0.0, le=2.0)
    ip_adapter_file: str = "ip-adapter_sd15.safetensors"
    clip_vision: str = "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
    # Extra quality-guard attempts after the first failure (new seed each time).
    quality_retries: int = Field(default=2, ge=0, le=8)
    # Same-face lock for --backend vnccs: Character Cloner source PNG.
    # Sandbox copy only (e.g. ./refs/kite_male_neutral.png). Never a LOVE32
    # path — Echo hand-copies the approved live sprite into refs/.
    # None: text-only CharacterCreatorV2 fallback (not the lock).
    reference: Optional[Path] = None
    output_dir: Path = Path("./output")

    @model_validator(mode="before")
    @classmethod
    def _normalize_poses(cls, data: Any) -> Any:
        """Allow poses as a list of strings *or* mappings with look-sheet keys.

        Example::

            poses:
              - idle
              - name: smoking
                outfit: dark henley, no apron
                prompt: holding a small flame
        """
        if not isinstance(data, dict):
            return data
        poses = data.get("poses") or []
        overrides: dict[str, Any] = dict(data.get("pose_overrides") or {})
        names: list[str] = []
        for item in poses:
            if isinstance(item, str):
                names.append(item)
                continue
            if isinstance(item, dict):
                name = item.get("name") or item.get("pose")
                if not name:
                    raise ValueError(
                        "pose mapping must include a 'name' (or 'pose') key"
                    )
                names.append(str(name))
                extra = {
                    k: item[k]
                    for k in ("prompt", "outfit", "family", "extra_negative")
                    if k in item and item[k] is not None
                }
                if extra:
                    existing = overrides.get(str(name)) or {}
                    if isinstance(existing, PoseOverride):
                        existing = existing.model_dump()
                    overrides[str(name)] = {**existing, **extra}
                continue
            raise ValueError(f"pose entry must be a string or mapping, got {item!r}")
        data["poses"] = names
        data["pose_overrides"] = overrides
        return data

    @field_validator("pose_overrides", mode="before")
    @classmethod
    def _coerce_overrides(
        cls, value: Any
    ) -> dict[str, Union[PoseOverride, dict[str, Any]]]:
        if value is None:
            return {}
        return value

    def outfit_for(self, pose: str) -> Optional[str]:
        """Resolved clothing string for a pose (explicit outfit, else family)."""
        ov = self.pose_overrides.get(pose)
        if ov is None:
            return None
        if ov.outfit and ov.outfit.strip():
            return ov.outfit.strip()
        if ov.family:
            family = self.outfit_families.get(ov.family)
            if family:
                return family.strip()
        return None


class MatchaConfig(BaseModel):
    """Project-level settings (reserved for multi-character projects)."""

    comfyui: str = "127.0.0.1:8188"
    project: Optional[Path] = None
