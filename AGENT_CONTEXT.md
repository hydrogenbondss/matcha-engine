# Matcha Engine — Agent Context

## What This Is
AI-powered game asset pipeline. Describe a character → generate sprites → format for Ren'Py → deploy.

## Status
- [x] Repo created
- [x] AGENT_CONTEXT.md written
- [x] CLI skeleton (init, character commands)
- [x] Config schema (Pydantic models)
- [x] Example config
- [x] ComfyUI generator module
- [x] Ren'Py formatter
- [x] Filesystem deployer
- [ ] First working pipeline (connect all modules)
- [ ] Test with actual ECHO project

## Tech Stack
- Python, Typer, Pydantic, Pillow, GitPython
- ComfyUI API for generation
- Ren'Py for deployment target

## Known Config
- ComfyUI: local at 127.0.0.1:8188
- Checkpoint: anythingV5PrtRE.safetensors
- LoRA: small_hours_style_v1.safetensors (strength 1.0)
- Resolution: 512x512
- Steps: 20, Euler, CFG 8
- Negative: low quality, blurry, worst quality, deformed, bad anatomy, extra limbs, bad hands

## Ren'Py Project
- Path: ~/Desktop/LOVE32/LOVE32/
- Images: game/images/
- Script: game/script.rpy

## Next Action
Connect CLI to generator + formatter + deployer for end-to-end pipeline.

## Decisions
- Focus on Ren'Py first, Godot later
- One character pipeline before scene/background
- Manual copy-paste agent workflow until token setup
