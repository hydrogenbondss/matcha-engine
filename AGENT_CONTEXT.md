# Matcha Engine — Agent Context

## What This Is
AI-powered game asset pipeline. Describe a character → generate sprites →
format for Ren'Py → deploy. See STRATEGY.md for positioning and roadmap.

## Status
- [x] Repo created
- [x] CLI skeleton (init, character commands)
- [x] Config schema (Pydantic models)
- [x] ComfyUI generator module
- [x] Ren'Py formatter
- [x] Filesystem deployer
- [x] First working pipeline (verified end-to-end against a mock ComfyUI)
- [x] v0.2: models in YAML config, preflight validation, loud failures,
      idempotent deploy to game/matcha_characters.rpy
- [ ] First real-GPU run (blocked on: correct checkpoint for the LoRA)
- [ ] Test with actual LOVE32 project
- [ ] Consistency evaluation vs VNCCS (ComfyUI_VNCCS)

## Tech Stack
- Python, Typer, Pydantic, Pillow, websocket-client
- ComfyUI API for generation
- Ren'Py for deployment target

## Known Config
- ComfyUI: local at 127.0.0.1:8188
- Checkpoint: anythingV5PrtRE.safetensors (NOT installed locally yet —
  only sd_xl_base is; verify the LoRA's base model before choosing)
- LoRA: small_hours_style_v1.safetensors (strength 1.0; base model unconfirmed)
- Default resolution: 512x768; steps 20, Euler, CFG 8
- Negative: low quality, blurry, worst quality, deformed, bad anatomy,
  extra limbs, bad hands

## Ren'Py Project
- Path: ~/Desktop/LOVE32/LOVE32/
- Images: game/images/characters/
- Script: game/matcha_characters.rpy (generated, idempotent per character)

## Decisions
- Focus on Ren'Py first, Godot later
- One character pipeline before scene/background
- Models are YAML config, never hardcoded
- Fail loudly: no deploy/script-update on zero generated images
