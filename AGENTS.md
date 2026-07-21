# Matcha Engine — Agent Guide

Matcha Engine is a single Python CLI (`matcha`) that turns a YAML character
config into a consistent sprite set (via ComfyUI + Stable Diffusion) and
deploys the results into a Ren'Py project. See `README.md` for usage and
`STRATEGY.md` for positioning.

## Cursor Cloud specific instructions

### Repo layout caveat
- The `main` branch is a stub (only `README.md`). The actual application code
  lives on feature branches. If `main` looks empty, the code you want is on a
  feature branch (e.g. the branch this guide was added on).

### Environment
- Python dev env lives in a virtualenv at `.venv` (Python 3.12; project requires
  >= 3.10). It is created/refreshed by the startup update script.
- Activate it (`. .venv/bin/activate`) or call binaries directly
  (`.venv/bin/python`, `.venv/bin/matcha`, `.venv/bin/pytest`) before running
  anything.

### Test / run
- Tests: `.venv/bin/python -m pytest tests/` — fully mocked, no ComfyUI or GPU
  needed. This is the primary correctness signal.
- Run the CLI: `matcha init <name>` scaffolds a project; `matcha character
  <config.yaml> [--dry-run] [--deploy --project <renpy-dir>]` runs the pipeline.
- No linter/formatter is configured in the repo (no ruff/flake8/black config).

### ComfyUI dependency (non-obvious)
- `matcha character` (without `--dry-run` it also generates) requires a running
  ComfyUI server at `127.0.0.1:8188` speaking HTTP **and** WebSocket, with the
  checkpoint/LoRA named in the YAML actually installed server-side. There is no
  ComfyUI server or GPU in the Cloud VM, so real image generation cannot run
  here.
- To exercise the pipeline end-to-end without a GPU, stand up a mock ComfyUI
  server implementing `GET /object_info/{node}`, `POST /prompt`,
  `GET /history/{pid}`, `GET /view`, and a `GET /ws` WebSocket that emits an
  `executing` frame with `node: null` to signal completion. `--dry-run` only
  hits `/object_info` (preflight), so a plain HTTP mock is enough for that path.
