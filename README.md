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

### Example project

Checked-in Ren'Py sample at [`examples/sample-vn/`](examples/sample-vn/).
Character PNGs are not committed — starter `Placeholder` art makes it
playable before generation; `matcha character --deploy` replaces them.

```bash
# Validate against ComfyUI (no GPU generation):
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --dry-run

# Generate + deploy into the sample project:
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --deploy --project examples/sample-vn --layered

# Open with the Ren'Py SDK (adjust the SDK path if needed):
~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn
```

Click through the pose lineup in `script.rpy`. With `--side-image`, dialogue
portraits use cropped head/shoulders PNGs (not the full sprite).

### Sandbox play-test (local dogfood)

For private experiments, use a throwaway `sandbox-renpy/` (gitignored) —
do **not** deploy into a live game while you're polishing it (Ren'Py
auto-loads every `game/*.rpy`).

```bash
.venv/bin/matcha character configs/example_character.yaml \
  --deploy --project ./sandbox-renpy --layered

~/Desktop/renpy-8.5.2-sdk/renpy.sh ./sandbox-renpy
```

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
