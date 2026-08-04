# Matcha Engine

AI game asset pipeline: define a character once in YAML, generate a
consistent sprite set on your own GPU (ComfyUI + Stable Diffusion/LoRA),
and deploy it straight into a Ren'Py project — images in the right folder,
`.rpy` definitions written for you.

See [STRATEGY.md](STRATEGY.md) for positioning, roadmap, and business model.

## Install

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e .
```

Requires a running [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
server with your checkpoint in `models/checkpoints/` and (optionally) a
LoRA in `models/loras/`. The checkpoint and LoRA must share a base model
family — an SD1.5 LoRA on an SDXL checkpoint fails or silently degrades.

### Mac MPS (Apple Silicon)

Start ComfyUI with these flags (avoid `--force-fp16` — it produces solid
black PNGs):

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
cd ~/ComfyUI && ./venv/bin/python main.py \
  --listen 127.0.0.1 --port 8188 \
  --fp32-vae --cpu-vae --lowvram --use-split-cross-attention
```

Prefer `512×512` and keep `consistency_denoise: 1.0` and
`ip_adapter_weight: 0` — partial img2img and IP-Adapter currently corrupt
on MPS. Matcha already forces LoRA `strength_clip=0` for the same reason.

## Usage

```bash
# Scaffold a project with an example character config
.venv/bin/matcha init myproject

# Validate config + models without generating (checks the ComfyUI server
# actually has the checkpoint/LoRA you named)
.venv/bin/matcha character configs/example_character.yaml --dry-run

# Generate and deploy into a Ren'Py project
.venv/bin/matcha character configs/example_character.yaml \
  --deploy --project ~/path/to/renpy-project --layered
```

Model selection lives in the YAML (`checkpoint:`, `lora:`,
`lora_strength:`) and can be overridden per-run with `--checkpoint` /
`--lora` (`--lora none` disables the LoRA).

Generated Ren'Py definitions go to `game/matcha_characters.rpy` — a
dedicated file that re-runs update idempotently, never touching your
hand-written script files. Only poses that actually generated get
definitions; the CLI exits non-zero if any pose fails.

### Sandbox play-test (dogfood)

Use a throwaway Ren'Py project — do **not** deploy into a live game while
you're polishing it (Ren'Py auto-loads every `game/*.rpy`).

```bash
# After generating into sandbox-renpy/ (create once with a minimal project
# + options.rpy/gui.rpy/screens.rpy from the Ren'Py SDK "the_question" sample):
.venv/bin/matcha character configs/example_character.yaml \
  --deploy --project ./sandbox-renpy --layered

# Launch with the Ren'Py SDK:
~/Desktop/renpy-8.5.2-sdk/renpy.sh ./sandbox-renpy
```

Click through each pose. With `--side-image`, dialogue portraits use cropped
head/shoulders PNGs (not the full sprite), so they won't double up on screen.

### Ren'Py scaffolding options

By default each pose becomes a flat `image <char> <pose>` definition. For a
richer, more idiomatic Ren'Py setup you can opt into:

- `--layered` / `layered: true` — emit a `layeredimage` that groups the poses
  as attributes, so `show sakura happy` composes from one declared sprite set
  (the first pose becomes the `default`).
- `--side-image` / `side_image: true` — crop a head/shoulders portrait from
  each sprite (top `side_image_height_ratio`, default `0.45`), deploy as
  `images/characters/<name>_<pose>_side.png`, emit `image side <char> <pose>`
  pointing at those files, and wire `Character(image="<char>")` so the portrait
  auto-shows beside dialogue. Full sprites remain for `show` / layeredimage.
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
image side sakura idle = "images/characters/sakura_idle_side.png"
```

## Development

```bash
pip install -e . pytest
python -m pytest tests/
```
