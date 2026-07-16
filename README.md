# Matcha Engine

AI game asset pipeline: define a character once in YAML, generate a
consistent sprite set on your own GPU (ComfyUI + Stable Diffusion/LoRA),
and deploy it straight into a Ren'Py project — images in the right folder,
`.rpy` definitions written for you.

See [STRATEGY.md](STRATEGY.md) for positioning, roadmap, and business model.

## Install

```bash
pip install -e .
```

Requires a running [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
server with your checkpoint in `models/checkpoints/` and (optionally) a
LoRA in `models/loras/`. The checkpoint and LoRA must share a base model
family — an SD1.5 LoRA on an SDXL checkpoint fails or silently degrades.

## Usage

```bash
# Scaffold a project with an example character config
matcha init myproject

# Validate config + models without generating (checks the ComfyUI server
# actually has the checkpoint/LoRA you named)
matcha character configs/example_character.yaml --dry-run

# Generate and deploy into a Ren'Py project
matcha character configs/example_character.yaml \
  --deploy --project ~/path/to/renpy-project
```

Model selection lives in the YAML (`checkpoint:`, `lora:`,
`lora_strength:`) and can be overridden per-run with `--checkpoint` /
`--lora` (`--lora none` disables the LoRA).

Generated Ren'Py definitions go to `game/matcha_characters.rpy` — a
dedicated file that re-runs update idempotently, never touching your
hand-written script files. Only poses that actually generated get
definitions; the CLI exits non-zero if any pose fails.

## Development

```bash
pip install -e . pytest
python -m pytest tests/
```
