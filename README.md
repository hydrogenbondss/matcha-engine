# Matcha Engine

Define a character once in YAML, generate a consistent sprite set on your own
GPU ([ComfyUI](https://github.com/comfyanonymous/ComfyUI) + Stable Diffusion /
LoRA), and deploy it into a Ren'Py project — images in the right folder,
`.rpy` definitions written for you.

Positioning and roadmap: [STRATEGY.md](STRATEGY.md) · progress:
[TIMELINE.md](TIMELINE.md).

## Install

Python 3.12 recommended (`>=3.10`):

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e .
```

Use `.venv/bin/matcha` (or `source .venv/bin/activate` first).

## ComfyUI requirement

Matcha does **not** bundle ComfyUI. Install it separately
([ComfyUI](https://github.com/comfyanonymous/ComfyUI)), put your checkpoint under
`models/checkpoints/` and any LoRA under `models/loras/`, then start the
server on `127.0.0.1:8188` (HTTP + WebSocket).

`matcha character` (without `--dry-run`) talks to that server. Checkpoint and
LoRA must share a base model family — an SD1.5 LoRA on an SDXL checkpoint
fails or silently degrades.

`--dry-run` only checks that those models exist on the server (no generation).

Verify the server is up before the sample recipe:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/
# expect 200 — if connection refused, start ComfyUI first
```

### Mac MPS (Apple Silicon) — read this

On Apple Silicon, several “nice” consistency features currently **corrupt**
output. Matcha defaults keep you safe; do not turn them on locally:

| Setting | Safe on MPS | Notes |
|---|---|---|
| Resolution | `512×512` | Prefer over `512×768` (OOM risk) |
| `consistency_denoise` | `1.0` (off) | Below `1.0` → glitched frames |
| `ip_adapter_weight` | `0` (off) | IPA → noise/corruption on MPS |
| LoRA clip strength | forced `0` by Matcha | Non-zero clip → half-static PNGs |

Start ComfyUI with these flags (adjust the path if your install is not
`~/ComfyUI`). **Do not** pass `--force-fp16` — it produces solid black PNGs:

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
cd ~/ComfyUI && ./venv/bin/python main.py \
  --listen 127.0.0.1 --port 8188 \
  --fp32-vae --cpu-vae --lowvram --use-split-cross-attention
```

Consistency on MPS is **prompt + shared seed** for now. Expect **several
minutes per pose** on Mac MPS (four poses can take ~15–25+ minutes) — the CLI
prints each pose name as it starts; it is not hung. After a heavy IP-Adapter
experiment, fully quit ComfyUI (or reboot) before the next clean run — a soft
restart is not enough.

## Quick start (stranger path)

Checked-in sample Ren'Py project: [`examples/sample-vn/`](examples/sample-vn/).
Sprites are not committed — starter `Placeholder` art keeps it playable until
you generate. You can open it in the Ren'Py SDK before ComfyUI is ready.

The sample YAML names `anythingV5PrtRE.safetensors` and `last.safetensors`.
Those files must exist in your ComfyUI `models/` folders, **or** override on
the CLI (`--checkpoint your.safetensors --lora none`).

```bash
# 0. ComfyUI running? (see section above; Mac MPS start flags if needed)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/

# 1. Validate config + models (ComfyUI must be running; no GPU work)
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --dry-run

# 2. Generate + deploy into the sample project (slow on Mac MPS — wait)
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --deploy --project examples/sample-vn --layered

# 3. Open with the Ren'Py SDK (adjust path)
~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn
```

Click through the pose lineup in `script.rpy`. Lint without launching the UI:
`~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn lint`.

Or scaffold your own tree: `.venv/bin/matcha init myproject`, then point
`--project` at any Ren'Py game directory.

**Do not** deploy into a live game you are polishing — Ren'Py auto-loads every
`game/*.rpy`. Use `examples/sample-vn/` or a throwaway `sandbox-renpy/`
(gitignored).

## CLI overview

| Command | What it does |
|---|---|
| `matcha character <config.yaml>` | Generate sprites; optional `--deploy` / `--dry-run` |
| `matcha licenses …` | Commercial-use status for checkpoint/LoRA (**not legal advice**) |
| `matcha disclose …` | Draft Steam AI survey + itch.io AI-tag text |
| `matcha init <name>` | Scaffold a project + example character YAML |

```bash
# License lookup (YAML and/or flags)
.venv/bin/matcha licenses examples/sample-vn/configs/example_character.yaml
.venv/bin/matcha licenses --checkpoint anythingV5PrtRE.safetensors

# Disclosure draft (stdout, or write into a Ren'Py project)
.venv/bin/matcha disclose examples/sample-vn/configs/example_character.yaml
.venv/bin/matcha disclose --name sakura -c anythingV5PrtRE.safetensors \
  --project examples/sample-vn   # writes matcha_disclosure.md
```

`matcha character` also prints a short license status before generating.
Generated definitions go to `game/matcha_characters.rpy` — idempotent on
re-run, never touches your hand-written scripts. Only poses that actually
generated get definitions; the CLI exits non-zero if any pose fails.

### Ren'Py scaffolding flags

Default: flat `image <char> <pose>` per pose. Opt in for a richer setup:

- `--layered` / `layered: true` — `layeredimage` with poses as attributes
  (`show sakura happy`; first pose is `default`)
- `--side-image` / `side_image: true` — crop head/shoulders portraits, emit
  `image side <char> <pose>`, wire `Character(image="<char>")` for dialogue
- YAML `display_name:` / `color:` — Character display name and name color

```bash
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --deploy --project examples/sample-vn --layered --side-image
```

## Development

```bash
.venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/
```

Tests are fully mocked — no ComfyUI or GPU required.
