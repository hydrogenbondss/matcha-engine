from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path


class CharacterConfig(BaseModel):
    name: str = Field(..., description="Character name for file naming")
    description: str = Field(..., description="Visual description for generation")
    poses: List[str] = Field(default=["idle", "happy", "sad", "angry"], description="Poses to generate")
    lora: Optional[str] = Field(None, description="LoRA model path or name")
    negative_prompt: str = Field(
        "lowres, bad anatomy, bad hands, text, error, missing fingers",
        description="Negative prompt for generation"
    )
    width: int = Field(512, description="Output width")
    height: int = Field(768, description="Output height")
    output_dir: Path = Field(Path("./output"), description="Where to save generated assets")
    renpy_project: Optional[Path] = Field(None, description="Path to Ren'Py project for auto-deployment")
    
    class Config:
        extra = "allow"


class MatchaConfig(BaseModel):
    comfyui_url: str = Field("http://localhost:8188", description="ComfyUI API URL")
    comfyui_workflow: Optional[Path] = Field(None, description="Path to ComfyUI workflow JSON")
    default_character: Optional[CharacterConfig] = None
