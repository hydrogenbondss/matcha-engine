from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


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
    # Ren'Py scaffolding options (the deploy "last mile").
    display_name: Optional[str] = None  # Character() display name; defaults to name.title()
    color: Optional[str] = None  # dialogue name color, e.g. "#ffcc00"
    layered: bool = False  # emit a layeredimage grouping poses as attributes
    side_image: bool = False  # emit side-image defs + wire Character(image=...)
    # Fraction of sprite height kept for side portraits (top-center crop).
    # ~0.45 ≈ head/shoulders on typical waist-up VN sprites.
    side_image_height_ratio: float = Field(default=0.45, gt=0.0, le=1.0)
    checkpoint: str = "anythingV5PrtRE.safetensors"
    # Prefer small_hours_style_v1 when it works; on Mac MPS it currently
    # NaNs — example configs use last.safetensors as the interim.
    lora: Optional[str] = "last.safetensors"
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
    output_dir: Path = Path("./output")


class MatchaConfig(BaseModel):
    """Project-level settings (reserved for multi-character projects)."""

    comfyui: str = "127.0.0.1:8188"
    project: Optional[Path] = None
