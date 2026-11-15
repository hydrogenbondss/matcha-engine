"""VNCCS backend — wrap AHEKOT/ComfyUI_VNCCS, do not reimplement it.

STRATEGY.md: do not compete with VNCCS on generation. Same-face lock is
their pipeline (MIT). Matcha queues their shipped 3.0 graph via the same
ComfyUI ``/prompt`` API the txt2img path already uses, filling
``widget_data`` / ``pose_data`` / ``node_state`` from YAML.

Verified node types (upstream repo + wiki Technical-Workflow-Node-Map,
2026-06-28):

* ``VNCCS_ControlCenter`` — shared ``VNCCS_PIPE``
* ``CharacterCloner`` — **same-face lock**: collage from an approved sprite
* ``CharacterCreatorV2`` — text/tag identity (**fallback**, not the lock)
* ``VNCCS_PoseStudio`` — VNCCS Utils; pose plates + lighting prompt
* ``VNCCS_CharacterGenerator`` / ``VNCCS_CharacterCloneGenerator``
* ``ClothesDesigner`` / ``VNCCS_ClothesGenerator`` — outfit families

3.0 is UI-heavy: Pose Studio's Python side no longer renders 3D. Headless
CLI injects ``captured_images`` (simple pose plates) into ``pose_data`` so
the *real* ``VNCCS_PoseStudio`` node still emits IMAGE poses. That is not
a renamed KSampler graph.

Sources:
https://github.com/AHEKOT/ComfyUI_VNCCS
https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Workflows-Overview
https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Technical-Workflow-Node-Map
https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Installation-and-Updates
https://github.com/AHEKOT/ComfyUI_VNCCS_Utils
"""

from __future__ import annotations

import base64
import io
import json
import re
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image, ImageDraw

from matcha.config import CharacterConfig
from matcha.errors import GenerationError
from matcha.prompts import pose_expression

# --- Verified class_type strings. Do not invent or rename. ---

NODE_CONTROL_CENTER = "VNCCS_ControlCenter"
NODE_CHARACTER_CREATOR = "CharacterCreatorV2"
NODE_CHARACTER_CLONER = "CharacterCloner"
NODE_POSE_STUDIO = "VNCCS_PoseStudio"
NODE_CHARACTER_GENERATOR = "VNCCS_CharacterGenerator"
NODE_CHARACTER_CLONE_GENERATOR = "VNCCS_CharacterCloneGenerator"
NODE_CLOTHES_DESIGNER = "ClothesDesigner"
NODE_CLOTHES_GENERATOR = "VNCCS_ClothesGenerator"

# Wiki Step 1 Character Creator ids (workflows/VNCCS_3.0_Step1_CharacterCreator.json)
ID_CONTROL_CENTER = "812"
ID_CHARACTER_CREATOR = "797"
ID_POSE_STUDIO = "703"
ID_CHARACTER_GENERATOR = "798"
ID_SAVE = "14"

# Wiki Step 1 Character Cloner ids
ID_CLONER_CONTROL = "771"
ID_CLONER = "774"
ID_CLONER_POSE = "761"
ID_CLONE_GENERATOR = "776"

# Wiki Step 2 clothes ids
ID_CLOTHES_CONTROL = "758"
ID_CLOTHES_DESIGNER = "753"
ID_CLOTHES_POSE = "728"
ID_CLOTHES_GENERATOR = "751"

# Always required for any VNCCS queue.
CORE_VNCCS_NODES = (NODE_CONTROL_CENTER,)
REQUIRED_VNCCS_UTILS_NODES = (NODE_POSE_STUDIO,)
# Same-face lock (primary).
CLONER_NODES = (NODE_CHARACTER_CLONER, NODE_CHARACTER_CLONE_GENERATOR)
# Text-only fallback — not a lock.
CREATOR_NODES = (NODE_CHARACTER_CREATOR, NODE_CHARACTER_GENERATOR)
# Backward-compatible alias used by older tests / preflight imports.
REQUIRED_VNCCS_NODES = CORE_VNCCS_NODES + CREATOR_NODES
CLOTHES_NODES = (NODE_CLOTHES_DESIGNER, NODE_CLOTHES_GENERATOR)

# Control Center companions (wiki Technical-Reference). CUDA-oriented;
# commonly fail or are unusable on Apple Silicon MPS.
CUDA_ORIENTED_COMPANIONS = (
    "UnetLoaderGGUF",
    "UnetLoaderGGUFAdvanced",
    "FaceDetailer",
    "UltralyticsDetectorProvider",
    "SAMLoader",
)

REFERENCE_COPY_HINT = """\
Same-face lock is Character Cloner from a sandbox copy of an approved
sprite — not Character Creator from text, and not prompt+seed.

To fix: hand-copy the approved PNG out of your live game into the Matcha
refs folder. Never point reference: or --reference at the live game tree
(Matcha refuses to read it).

  mkdir -p refs
  # e.g. hand-copied from <your-live-game>/game/images/kite_male neutral.png
  # Copy it; do not --project your live game.
  cp "/path/to/hand-copied/kite_male neutral.png" refs/kite_male_neutral.png

Then: reference: ./refs/kite_male_neutral.png
  matcha character configs/kite_male.yaml --backend vnccs --poses neutral
"""

MPS_VNCCS_HINT = """\
This ComfyUI device is Apple Silicon MPS. VNCCS 3.0's Control Center
stack is CUDA-oriented (Qwen-Image-Edit GGUF, Impact Pack / FaceDetailer,
SAM). Those companions commonly fail on MPS.

Matcha will not silently fall back to --backend txt2img / prompt+seed
and call that VNCCS. prompt+seed is not a lock. IP-Adapter stays off.

Use a CUDA ComfyUI for --backend vnccs, or pass --vnccs-allow-mps to
queue the real VNCCS nodes anyway (still Character Cloner / Creator —
still not txt2img; still may fail at runtime).
"""

CONTROL_CENTER_REPO = "MIUProject/VNCCS_v3.0"

# Shipped Control Center widget (GGUF Qwen-Image-Edit). Not Anything V5.
# Anything V5 stays on --backend txt2img. Do not pretend they are the same.
DEFAULT_CONTROL_CENTER_STATE = {
    "output_slot_names": [],
    "selected_models": {"gguf": "Qwen-Image-Edit-2511-GGUF-Q5"},
    "selected_model": "Qwen-Image-Edit-2511-GGUF-Q5",
    "selected_type": "gguf",
    "collapsed": {"controlnet": True, "clip_vae": False},
    "loras": [
        {
            "name": "Qwen Image Edit 2511 Lightning",
            "auto_apply": True,
            "strength": 1,
        }
    ],
    "model_params": {"steps": 4, "cfg": 1},
}

INSTALL_HINT = """\
VNCCS nodes are not installed on this ComfyUI server.

Same-face lock requires VNCCS (MIT). Matcha will not silently fall back
to prompt+seed and call that consistent.

Install via ComfyUI Manager:
  1. Search and install: VNCCS - Visual Novel Character Creation Suite
  2. Search and install: VNCCS Utils
  3. Restart ComfyUI
  4. Open a VNCCS 3.0 workflow, use Control Center to download the
     recommended Qwen-Image-Edit GGUF + helper LoRAs

Manual (into ~/ComfyUI/custom_nodes/):
  https://github.com/AHEKOT/ComfyUI_VNCCS
  https://github.com/AHEKOT/ComfyUI_VNCCS_Utils

Wiki: Installation-and-Updates · Workflows-Overview · Technical-Workflow-Node-Map

Then: matcha character <yaml> --backend vnccs --dry-run

Trusted first success without VNCCS stays --lora none (txt2img).
That path is prompt+seed. It is not a same-face lock.
IP-Adapter and consistency_denoise < 1.0 stay off on Mac MPS.
"""


@dataclass
class VNCCSStatus:
    """What the live /object_info actually registered."""

    required_ok: bool
    missing_required: list[str] = field(default_factory=list)
    clothes_ok: bool = False
    cloner_ok: bool = False
    creator_ok: bool = False
    device: str = "unknown"
    cuda_companions: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    used_cloner: bool = False


def split_tags(description: str) -> list[str]:
    return [t.strip() for t in description.split(",") if t.strip()]


def infer_sex(tags: list[str], description: str) -> str:
    blob = " ".join(tags).lower() + " " + description.lower()
    if re.search(r"\b(1boy|male|man|guy)\b", blob):
        return "male"
    if re.search(r"\b(1girl|female|woman|girl)\b", blob):
        return "female"
    return "female"


def infer_age(description: str) -> int:
    # CharacterCreatorV2 defaults to 18; kite is "young man" — adult.
    if re.search(r"\byoung man\b|\b1boy\b|\bman\b", description.lower()):
        return 22
    return 18


def _join_matching(tags: list[str], predicate) -> str:
    return ", ".join(t for t in tags if predicate(t.lower()))


def character_info_from_config(
    cfg: CharacterConfig,
    *,
    pose: Optional[str] = None,
    outfit: Optional[str] = None,
) -> dict:
    """Map YAML identity (+ optional look-sheet outfit) to CharacterCreatorV2 fields."""
    tags = split_tags(cfg.description)
    hair = _join_matching(
        tags,
        lambda t: "hair" in t or "bang" in t or "buzz" in t or "ponytail" in t,
    )
    eyes = _join_matching(tags, lambda t: "eye" in t)
    skin = _join_matching(
        tags,
        lambda t: "skin" in t or t in {"tan", "olive", "pale", "fair", "dark"},
    )
    race = _join_matching(tags, lambda t: t in {"human", "elf", "oni", "demon"})
    extras = []
    skip = {"1boy", "1girl", "solo"}
    for t in tags:
        low = t.lower()
        if low in skip:
            continue
        if t in (hair, eyes, skin, race):
            continue
        if "hair" in low or "bang" in low or "buzz" in low:
            continue
        if "eye" in low or "skin" in low:
            continue
        extras.append(t)
    if outfit:
        extras.append(outfit.strip())
    if pose:
        ov = cfg.pose_overrides.get(pose)
        extra_prompt = (ov.prompt if ov else None) or ""
        if extra_prompt.strip():
            extras.append(extra_prompt.strip())
        else:
            extras.append(pose_expression(pose))
    return {
        "sex": infer_sex(tags, cfg.description),
        "age": infer_age(cfg.description),
        "race": race or "human",
        "skin_color": skin,
        "hair": hair,
        "eyes": eyes,
        "face": "",
        "body": "",
        "additional_details": ", ".join(extras),
        "nsfw": False,
        "aesthetics": "masterpiece, visual novel style, cel shaded",
        "negative_prompt": cfg.negative_prompt,
        "lora_prompt": "",
        "background_color": "Green",
        "name": cfg.name,
        "seed": int(cfg.seed or 0),
    }


def creator_widget_data(
    cfg: CharacterConfig,
    *,
    pose: Optional[str] = None,
    outfit: Optional[str] = None,
    seed: Optional[int] = None,
) -> dict:
    info = character_info_from_config(cfg, pose=pose, outfit=outfit)
    run_seed = int(seed if seed is not None else (cfg.seed or 0))
    info["seed"] = run_seed
    return {
        "preview_valid": False,
        "preview_source": "gen",
        "character": cfg.name,
        "character_info": info,
        "gen_settings": {
            "generation_mode": "illustrious",
            "ckpt_name": cfg.checkpoint,
            "sampler": "euler",
            "scheduler": "normal",
            "steps": int(cfg.steps),
            "cfg": float(cfg.cfg),
            "seed": run_seed,
            "seed_mode": "fixed",
            "dmd_lora_name": "",
            "dmd_lora_strength": 0,
            "age_lora_name": "",
            "lora_stack": [],
            "turbo_enabled": False,
        },
    }


def cloner_widget_data(
    cfg: CharacterConfig,
    source_filename: str,
    *,
    pose: Optional[str] = None,
    outfit: Optional[str] = None,
) -> dict:
    info = character_info_from_config(cfg, pose=pose, outfit=outfit)
    return {
        "character": cfg.name,
        "character_info": info,
        "source_images": [{"name": source_filename, "subfolder": "", "type": "input"}],
    }


def clothes_widget_data(
    cfg: CharacterConfig,
    pose: str,
    outfit: str,
) -> dict:
    ov = cfg.pose_overrides.get(pose)
    family = (ov.family if ov else None) or pose
    costume = re.sub(r"[^A-Za-z0-9_-]+", "_", family).strip("_") or pose
    return {
        "character": cfg.name,
        "costume": costume,
        "activeTab": "generate",
        "costume_info": {
            "top": outfit.strip(),
            "bottom": "",
            "shoes": "",
            "head": "",
            "face": "",
        },
        "gen_settings": {"background_color": "Green"},
    }


def generator_widget_data(cfg: CharacterConfig) -> dict:
    return {
        "character_name": cfg.name,
        "nsfw_enabled": False,
    }


def lighting_prompt_for_pose(cfg: CharacterConfig, pose: str) -> str:
    ov = cfg.pose_overrides.get(pose)
    extra = (ov.prompt if ov else None) or pose_expression(pose)
    outfit = cfg.outfit_for(pose) or ""
    bits = ["Draw character from image2", extra.strip()]
    if outfit:
        bits.append(outfit.strip())
    return "\n".join(b for b in bits if b)


def pose_plate_png(pose: str, width: int = 512, height: int = 512) -> bytes:
    """Simple standing-figure plate so Pose Studio can emit IMAGE without WebGL.

    VNCCS_PoseStudio (Utils) raises if ``captured_images`` is empty and the
    browser widget did not sync. These plates are that documented CSR path —
    not a substitute KSampler graph.
    """
    im = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(im)
    cx = width // 2
    head_r = max(18, width // 14)
    head_y = int(height * 0.18)
    d.ellipse(
        [cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
        outline=(20, 20, 20),
        width=4,
    )
    body_top = head_y + head_r + 4
    body_bot = int(height * 0.78)
    d.line([(cx, body_top), (cx, body_bot)], fill=(20, 20, 20), width=5)
    key = pose.strip().lower()
    if key == "crossed_arms":
        mid = (body_top + body_bot) // 2
        d.line([(cx - 70, mid + 20), (cx + 50, mid - 10)], fill=(20, 20, 20), width=5)
        d.line([(cx + 70, mid + 20), (cx - 50, mid + 8)], fill=(20, 20, 20), width=5)
    elif key == "smoking":
        d.line([(cx, body_top + 30), (cx + 90, body_top + 10)], fill=(20, 20, 20), width=5)
        d.line([(cx, body_top + 40), (cx - 70, body_bot - 20)], fill=(20, 20, 20), width=5)
        d.line([(cx + 90, body_top + 10), (cx + 120, body_top)], fill=(80, 80, 80), width=2)
    else:
        d.line([(cx, body_top + 40), (cx - 70, body_bot - 40)], fill=(20, 20, 20), width=5)
        d.line([(cx, body_top + 40), (cx + 70, body_bot - 40)], fill=(20, 20, 20), width=5)
    d.line([(cx, body_bot), (cx - 40, height - 12)], fill=(20, 20, 20), width=5)
    d.line([(cx, body_bot), (cx + 40, height - 12)], fill=(20, 20, 20), width=5)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def pose_data_for(
    cfg: CharacterConfig,
    pose: str,
    *,
    width: int,
    height: int,
) -> dict:
    lighting = lighting_prompt_for_pose(cfg, pose)
    plate = pose_plate_png(pose, width=width, height=height)
    b64 = base64.b64encode(plate).decode("ascii")
    sex = infer_sex(split_tags(cfg.description), cfg.description)
    return {
        "mesh": {
            "age": infer_age(cfg.description),
            "gender": 1 if sex == "male" else 0,
            "weight": 0.66,
            "muscle": 0.55 if sex == "male" else 0.5,
            "height": 0.85,
        },
        "export": {
            "view_width": width,
            "view_height": height,
            "output_mode": "LIST",
            "grid_columns": 1,
            "bg_color": [255, 255, 255],
            "user_prompt": lighting,
            "prompt_template": "Draw character from image2\n<lighting>\n<user_prompt>",
            "skin_type": "naked",
            "interface_mode": "manager",
        },
        "poses": [
            {
                "bones": {},
                "prompt": lighting,
                "cameraParams": {
                    "offset_x": 0,
                    "offset_y": 0,
                    "yaw_deg": 0,
                    "pitch_deg": 0,
                    "zoom": 1.4,
                },
            }
        ],
        "captured_images": [f"data:image/png;base64,{b64}"],
        "lighting_prompts": [lighting],
        "activeTab": 0,
    }


def _control_center_node(cfg: CharacterConfig) -> dict:
    state = dict(DEFAULT_CONTROL_CENTER_STATE)
    params = dict(state.get("model_params") or {})
    params["steps"] = int(cfg.steps)
    params["cfg"] = float(cfg.cfg)
    state["model_params"] = params
    return {
        "class_type": NODE_CONTROL_CENTER,
        "inputs": {
            "repo_id": CONTROL_CENTER_REPO,
            "node_state": json.dumps(state, separators=(",", ":")),
        },
    }


def _save_image_node(from_id: str, output_index: int, prefix: str) -> dict:
    return {
        "class_type": "SaveImage",
        "inputs": {
            "images": [from_id, output_index],
            "filename_prefix": prefix,
        },
    }


def build_step1_creator_prompt(
    cfg: CharacterConfig,
    pose: str,
    *,
    seed: int,
    outfit: Optional[str] = None,
) -> dict:
    """API prompt matching shipped Step 1 Character Creator connections."""
    if outfit is None:
        outfit = cfg.outfit_for(pose)
    creator = creator_widget_data(cfg, pose=pose, outfit=outfit, seed=seed)
    pose_payload = pose_data_for(cfg, pose, width=cfg.width, height=cfg.height)
    return {
        ID_CONTROL_CENTER: _control_center_node(cfg),
        ID_CHARACTER_CREATOR: {
            "class_type": NODE_CHARACTER_CREATOR,
            "inputs": {
                "widget_data": json.dumps(creator, ensure_ascii=False),
            },
        },
        ID_POSE_STUDIO: {
            "class_type": NODE_POSE_STUDIO,
            "inputs": {
                "pose_data": json.dumps(pose_payload, ensure_ascii=False),
            },
        },
        ID_CHARACTER_GENERATOR: {
            "class_type": NODE_CHARACTER_GENERATOR,
            "inputs": {
                "poses": [ID_POSE_STUDIO, 0],
                "character": [ID_CHARACTER_CREATOR, 0],
                "pipe": [ID_CONTROL_CENTER, 0],
                "prompt": [ID_POSE_STUDIO, 1],
                "background": [ID_CHARACTER_CREATOR, 2],
                "sheets_path": [ID_CHARACTER_CREATOR, 1],
                "widget_data": json.dumps(generator_widget_data(cfg)),
            },
        },
        ID_SAVE: _save_image_node(ID_CHARACTER_GENERATOR, 2, "matcha_vnccs"),
    }


def build_step1_cloner_prompt(
    cfg: CharacterConfig,
    pose: str,
    source_filename: str,
    *,
    seed: int,
    outfit: Optional[str] = None,
) -> dict:
    """API prompt matching shipped Step 1 Character Cloner connections."""
    if outfit is None:
        outfit = cfg.outfit_for(pose)
    _ = seed  # seed lives on Control Center / generator widget, not cloner
    pose_payload = pose_data_for(cfg, pose, width=cfg.width, height=cfg.height)
    return {
        ID_CLONER_CONTROL: _control_center_node(cfg),
        ID_CLONER: {
            "class_type": NODE_CHARACTER_CLONER,
            "inputs": {
                "widget_data": json.dumps(
                    cloner_widget_data(
                        cfg, source_filename, pose=pose, outfit=outfit
                    ),
                    ensure_ascii=False,
                ),
            },
        },
        ID_CLONER_POSE: {
            "class_type": NODE_POSE_STUDIO,
            "inputs": {
                "pose_data": json.dumps(pose_payload, ensure_ascii=False),
            },
        },
        ID_CLONE_GENERATOR: {
            "class_type": NODE_CHARACTER_CLONE_GENERATOR,
            "inputs": {
                "poses": [ID_CLONER_POSE, 0],
                "character": [ID_CLONER, 0],
                "pipe": [ID_CLONER_CONTROL, 0],
                "prompt": [ID_CLONER_POSE, 1],
                "background": [ID_CLONER, 2],
                "sheets_path": [ID_CLONER, 1],
                "widget_data": json.dumps(generator_widget_data(cfg)),
            },
        },
        ID_SAVE: _save_image_node(ID_CLONE_GENERATOR, 0, "matcha_vnccs_clone"),
    }


def build_step2_clothes_prompt(
    cfg: CharacterConfig,
    pose: str,
    outfit: str,
) -> dict:
    """API prompt matching shipped Step 2 Character Clothes connections."""
    pose_payload = pose_data_for(cfg, pose, width=cfg.width, height=cfg.height)
    return {
        ID_CLOTHES_CONTROL: _control_center_node(cfg),
        ID_CLOTHES_DESIGNER: {
            "class_type": NODE_CLOTHES_DESIGNER,
            "inputs": {
                "pipe": [ID_CLOTHES_CONTROL, 0],
                "widget_data": json.dumps(
                    clothes_widget_data(cfg, pose, outfit), ensure_ascii=False
                ),
            },
        },
        ID_CLOTHES_POSE: {
            "class_type": NODE_POSE_STUDIO,
            "inputs": {
                "pose_data": json.dumps(pose_payload, ensure_ascii=False),
            },
        },
        ID_CLOTHES_GENERATOR: {
            "class_type": NODE_CLOTHES_GENERATOR,
            "inputs": {
                "poses": [ID_CLOTHES_POSE, 0],
                "character": [ID_CLOTHES_DESIGNER, 0],
                "pipe": [ID_CLOTHES_CONTROL, 0],
                "prompt": [ID_CLOTHES_POSE, 1],
                "background": [ID_CLOTHES_DESIGNER, 2],
                "sheets_path": [ID_CLOTHES_DESIGNER, 1],
                "widget_data": json.dumps(generator_widget_data(cfg)),
            },
        },
        ID_SAVE: _save_image_node(ID_CLOTHES_GENERATOR, 0, "matcha_vnccs_clothes"),
    }


def workflow_class_types(workflow: dict) -> set[str]:
    return {
        str(node.get("class_type"))
        for node in workflow.values()
        if isinstance(node, dict)
    }


def generate_pose(
    generator,
    cfg: CharacterConfig,
    pose: str,
    *,
    seed: int,
    clone_filename: Optional[str] = None,
    include_clothes: bool = False,
) -> list[bytes]:
    """Queue the VNCCS graph for one pose. Does not enable IPA or img2img."""
    outfit = cfg.outfit_for(pose)
    if clone_filename:
        step1 = build_step1_cloner_prompt(
            cfg, pose, clone_filename, seed=seed, outfit=outfit
        )
    else:
        step1 = build_step1_creator_prompt(
            cfg, pose, seed=seed, outfit=outfit
        )
    images = generator.generate_workflow(step1)
    if include_clothes and outfit:
        try:
            clothed = generator.generate_workflow(
                build_step2_clothes_prompt(cfg, pose, outfit)
            )
            if clothed:
                return clothed
        except GenerationError:
            # Step 2 needs Naked sprites on disk from Step 1. Keep Step 1
            # frames rather than pretending clothes ran.
            return images
    return images
