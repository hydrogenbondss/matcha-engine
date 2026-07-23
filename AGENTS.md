# Matcha Engine — Agent Guide

Matcha Engine is a single Python CLI (`matcha`) that turns a YAML character
config into a consistent sprite set (via ComfyUI + Stable Diffusion) and
deploys the results into a Ren'Py project. See `README.md` for usage and
`STRATEGY.md` for positioning. Progress lives in `TIMELINE.md`.

## Repo layout caveat

- The `main` branch may still be a stub (only `README.md`). The application
  code lives on feature branches — currently
  `cursor/setup-dev-environment-c8f9` (PR #2) is the branch to work on.
- If `main` looks empty, check out the PR branch before developing.

## Local / Cloud environment

- Python 3.12 recommended (project requires `>=3.10`). Create a venv at
  `.venv` (gitignored):

  ```bash
  python3.12 -m venv .venv
  .venv/bin/pip install -e . pytest
  ```

- Activate (`. .venv/bin/activate`) or call binaries directly
  (`.venv/bin/python`, `.venv/bin/matcha`, `.venv/bin/pytest`).

### Test / run

- Tests: `.venv/bin/python -m pytest tests/` — fully mocked, no ComfyUI or
  GPU needed. This is the primary correctness signal (25 tests as of
  2026-07-22).
- Run the CLI: `matcha init <name>` scaffolds a project; `matcha character
  <config.yaml> [--dry-run] [--deploy --project <renpy-dir>]` runs the
  pipeline. Opt-in Ren'Py scaffolding: `--layered`, `--side-image`.
- No linter/formatter is configured (no ruff/flake8/black config).

### ComfyUI dependency (non-obvious)

- `matcha character` (without `--dry-run`) requires a running ComfyUI server
  at `127.0.0.1:8188` speaking HTTP **and** WebSocket, with the
  checkpoint/LoRA named in the YAML installed server-side.
- Cloud VMs typically have neither ComfyUI nor a GPU — real generation cannot
  run there. Local Macs may have ComfyUI installed but idle; start the server
  before a real run.
- To exercise the pipeline end-to-end without a GPU, stand up a mock ComfyUI
  server implementing `GET /object_info/{node}`, `POST /prompt`,
  `GET /history/{pid}`, `GET /view`, and a `GET /ws` WebSocket that emits an
  `executing` frame with `node: null` to signal completion. `--dry-run` only
  hits `/object_info` (preflight), so a plain HTTP mock is enough for that
  path.

### Confirmed local models (Mac, 2026-07-22)

Inspected without generating:

| Asset | Path | Notes |
|---|---|---|
| LoRA `small_hours_style_v1` | `~/ComfyUI/models/loras/` | **SD1.5** — trained on `sd-v1-5-pruned`; **black/NaN on Mac MPS** with anythingV5 |
| LoRA `last` (interim) | `~/ComfyUI/models/loras/` (from `~/SmallHours_LoRA_test`) | Works @ ~0.7 with anythingV5 on Mac MPS |
| Checkpoint `anythingV5PrtRE` | `~/ComfyUI/models/checkpoints/` | SD1.5 anime checkpoint |
| Checkpoint `sd_xl_base` | `~/ComfyUI/models/checkpoints/` | SDXL — do **not** pair with these LoRAs |

Trigger word observed in training tags: `sh_style`.
Ren'Py dogfood target: `~/Desktop/LOVE32/LOVE32/`.
Ren'Py SDK (for lint/compile of generated `.rpy`):
`~/Desktop/renpy-8.5.2-sdk/renpy.sh`.

Start ComfyUI (local Mac MPS — required flags):

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
cd ~/ComfyUI && ./venv/bin/python main.py \
  --listen 127.0.0.1 --port 8188 \
  --fp32-vae --cpu-vae --lowvram --use-split-cross-attention
```

Do **not** pass `--force-fp16` on this machine — it produces NaN → solid black
PNGs. Prefer `512×512` over `512×768` to avoid MPS OOM; raise
`PYTORCH_MPS_HIGH_WATERMARK_RATIO` as above.

**LoRA caveat (2026-07-23):** `small_hours_style_v1.safetensors` currently
yields black images on Mac MPS with `anythingV5PrtRE` (even at strength 0.5).
Working interim: `last.safetensors` (from `~/SmallHours_LoRA_test`) at ~0.7.
Base checkpoint alone also works.

Not useful for matcha: `~/bentopdf` (unrelated client-side PDF toolkit).
`~/kohya_ss` is only needed if retraining LoRAs.
