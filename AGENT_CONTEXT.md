# Matcha Engine — Agent Context

## What This Is
AI-powered game asset pipeline. Describe a character → generate sprites →
format for Ren'Py → deploy. See STRATEGY.md for positioning and roadmap.

## Status
- [x] Repo created
- [x] CLI skeleton (init, character commands)
- [x] Config schema (Pydantic models)
- [x] ComfyUI generator module
- [x] Ren'Py formatter (incl. opt-in layeredimage / side-image scaffolding)
- [x] Filesystem deployer
- [x] First working pipeline (verified end-to-end against a mock ComfyUI)
- [x] v0.2: models in YAML config, preflight validation, loud failures,
      idempotent deploy to game/matcha_characters.rpy
- [x] LoRA base confirmed: small_hours_style_v1 is **SD1.5**; pair with
      anythingV5PrtRE (both present under ~/ComfyUI/models/)
- [x] First real-GPU run (2026-07-23, Mac MPS) — 4/4 sakura poses
- [x] Dogfood on LOVE32 + Ren'Py SDK lint clean for matcha script
- [!] small_hours_style_v1 NaNs/blacks on Mac MPS — interim: last.safetensors
- [ ] Consistency evaluation vs VNCCS (ComfyUI_VNCCS)

## Tech Stack
- Python, Typer, Pydantic, Pillow, websocket-client
- ComfyUI API for generation
- Ren'Py for deployment target

## Known Config
- ComfyUI: local at 127.0.0.1:8188 (start the server before real runs)
- Checkpoint: anythingV5PrtRE.safetensors (SD1.5; installed locally)
- LoRA (interim working / default): last.safetensors @ strength 0.7
- LoRA (preferred but broken on MPS): small_hours_style_v1.safetensors
  (SD1.5, trigger `sh_style`; produces solid black / NaN on this Mac)
- Practical local resolution: 512×512 (512×768 OOMs MPS easily)
- Shared seed across poses; prompt builder locks framing / outfit wording
- Black/NaN PNGs rejected post-decode; `output_dir` is wired
- Steps 12–20, Euler, CFG 8
- Negative: base quality negatives + collage/reference-sheet guards

## Ren'Py Project
- Path: ~/Desktop/LOVE32/LOVE32/
- Images: game/images/characters/
- Script: game/matcha_characters.rpy (generated, idempotent per character)
- SDK: ~/Desktop/renpy-8.5.2-sdk/renpy.sh (lint/compile after deploy)

## Local ComfyUI (Mac MPS)
- Install: ~/ComfyUI (venv at ~/ComfyUI/venv)
- Start (MPS-safe):

  ```bash
  export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
  cd ~/ComfyUI && ./venv/bin/python main.py \
    --listen 127.0.0.1 --port 8188 \
    --fp32-vae --cpu-vae --lowvram --use-split-cross-attention
  ```

- Do **not** use `--force-fp16` here — NaN → black PNGs
- Useful local paths: ~/small_hours_lora, ~/SmallHours_LoRA_test,
  ~/small_hours_dataset (train_config confirms SD1.5)
- Not relevant to matcha: ~/bentopdf (PDF toolkit); ~/kohya_ss only for retrain

## Decisions
- Focus on Ren'Py first, Godot later
- One character pipeline before scene/background
- Models are YAML config, never hardcoded
- Fail loudly: no deploy/script-update on zero generated images
