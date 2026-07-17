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
    checkpoint: str = "anythingV5PrtRE.safetensors"
    lora: Optional[str] = "small_hours_style_v1.safetensors"
    lora_strength: float = 1.0
    negative_prompt: str = (
        "low quality, blurry, worst quality, deformed, bad anatomy, "
        "extra limbs, bad hands"
    )
    width: int = 512
    height: int = 768
    # Optional post-generation resize (fit within, aspect preserved).
    # Ren'Py 720p projects typically want sprites no taller than the screen.
    resize_max_width: Optional[int] = None
    resize_max_height: Optional[int] = None
    steps: int = 20
    cfg: float = 8.0
    seed: Optional[int] = None
    output_dir: Path = Path("./output")


class MatchaConfig(BaseModel):
    """Project-level settings (reserved for multi-character projects)."""

    comfyui: str = "127.0.0.1:8188"
    project: Optional[Path] = None
