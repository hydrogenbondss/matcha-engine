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

### Ren'Py scaffolding options

By default each pose becomes a flat `image <char> <pose>` definition. For a
richer, more idiomatic Ren'Py setup you can opt into:

- `--layered` / `layered: true` — emit a `layeredimage` that groups the poses
  as attributes, so `show sakura happy` composes from one declared sprite set
  (the first pose becomes the `default`).
- `--side-image` / `side_image: true` — emit `image side <char> <pose>`
  definitions and wire `Character(image="<char>")` so a portrait auto-shows
  beside that character's dialogue. (These reuse the full sprite; regenerate as
  cropped portraits for best results.)
- `display_name:` and `color:` in the YAML — set the `Character` display name
  and dialogue name color.

```bash
matcha character configs/example_character.yaml \
  --deploy --project ~/my-vn --layered --side-image
```

Produces, for example:

```renpy
define sakura = Character("Sakura Kinomoto", color="#ff77aa", image="sakura")
layeredimage sakura:
    group pose:
        attribute idle default "images/characters/sakura_idle.png"
        attribute happy "images/characters/sakura_happy.png"
image side sakura idle = "images/characters/sakura_idle.png"
```

## Development

```bash
pip install -e . pytest
python -m pytest tests/
```
