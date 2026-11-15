# Matcha Engine

Define a character once in YAML, generate a consistent sprite set on your own
GPU ([ComfyUI](https://github.com/comfyanonymous/ComfyUI) + Stable Diffusion /
optional LoRA), and deploy it into a Ren'Py project — images in the right
folder, `.rpy` definitions written for you.

Positioning and roadmap: [STRATEGY.md](STRATEGY.md) · progress:
[TIMELINE.md](TIMELINE.md).

## Install

Python 3.12 recommended (`>=3.10`):

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e .
```

Use `.venv/bin/matcha` (or `source .venv/bin/activate` first).

### Prebuilt binaries

CI builds a single-file `matcha` binary on every push (see the Actions
artifacts). The macOS binary is **Apple Silicon (arm64) only**. Intel Mac
(x86_64) users install from source with `pip install -e .` instead — full
capability, no feature difference. The Windows x64 binary is **beta**
(CI smoke-tested, not verified on real hardware).

**Gatekeeper note:** browser-downloaded binaries carry a quarantine
attribute. If macOS refuses to run the binary, either run
`xattr -cr matcha` on it or right-click → **Open** once.

## ComfyUI + models (required for generation)

Matcha is a thin CLI around **your** local ComfyUI. It does **not** install
ComfyUI, download checkpoints, or ship GPU runtimes.

**Without ComfyUI:** you can still open
[`examples/sample-vn/`](examples/sample-vn/) in the Ren'Py SDK — starter
`Placeholder` art keeps it playable. **Generation** needs a live server +
a matching checkpoint.

### 1. Install ComfyUI

Clone and set up from the official repo:
[github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI).
Follow their install docs for your OS / GPU. Typical local path: `~/ComfyUI`.

### 2. Drop in models

| Asset | Put it here (under your ComfyUI root) |
|---|---|
| Checkpoint (required) | `models/checkpoints/` |
| LoRA (optional) | `models/loras/` |

Checkpoint and LoRA must share a base family — an SD1.5 LoRA on an SDXL
checkpoint fails or silently degrades. **First success needs only a
checkpoint** — leave LoRA off until base generate works.

### 3. Match names (or override)

The sample YAML expects a checkpoint filename on disk:

- `anythingV5PrtRE.safetensors` (checkpoint)
- LoRA defaults to off (`lora: null`); add one only after a clean base run

If your checkpoint name differs, override on the CLI:

```bash
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --checkpoint your_checkpoint.safetensors --lora none
```

### 4. Start the server, then health-check

ComfyUI must speak HTTP **and** WebSocket on `127.0.0.1:8188`. **Do this
before** any `--dry-run` or generate — connection refused means the server
is not up.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/
# expect 200 — if connection refused, start ComfyUI first
```

`--dry-run` only checks that the named models exist on that server (no GPU
work). Real generation needs the same server still running.

### Mac MPS (Apple Silicon) — read this

On Apple Silicon, several “nice” consistency features currently **corrupt**
output. Matcha defaults keep you safe; **do not turn them on** locally:

| Setting | Safe on MPS | Notes |
|---|---|---|
| Resolution | `512×512` | Prefer over `512×768` (OOM risk) |
| LoRA | off (`--lora none` / `lora: null`) | First-success path; some LoRAs black/NaN on MPS |
| `consistency_denoise` | `1.0` (off) | Below `1.0` → glitched frames — leave off |
| `ip_adapter_weight` | `0` (off) | IPA → noise/corruption on MPS — leave off. **Not** the same-face path. |
| LoRA clip strength | forced `0` by Matcha | Non-zero clip → half-static PNGs |
| `--backend vnccs` | opt-in | Same-face lock = **Character Cloner** from a sandbox `--reference`. Requires VNCCS + Utils + CUDA-ish companions. **Fails preflight on MPS** unless `--vnccs-allow-mps`. Not txt2img. |

Start ComfyUI with these flags (adjust the path if your install is not
`~/ComfyUI`). **Do not** pass `--force-fp16` — it produces solid black PNGs:

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
cd ~/ComfyUI && ./venv/bin/python main.py \
  --listen 127.0.0.1 --port 8188 \
  --fp32-vae --cpu-vae --lowvram --use-split-cross-attention
```

**prompt + shared seed is not a same-face lock.** It is the trusted
512×512 `--lora none` first-success path. Identity lock is **VNCCS
Character Cloner** from a sandbox copy of an approved sprite
(`--backend vnccs` + `--reference` / YAML `reference:`). Text-only
Character Creator is fallback, not the lock. Do **not** turn on
IP-Adapter or `consistency_denoise < 1.0` on Mac MPS — they corrupt,
and they are not the VNCCS path. Never drop a live-game PNG
in as an IP-Adapter reference, and never point `reference:` at your live
game.
Expect
**several minutes per pose** on Mac MPS (four poses can take ~15–25+ minutes)
— the CLI prints each pose name as it starts; it is not hung. After a heavy
IP-Adapter experiment, fully quit ComfyUI (or reboot) before the next clean
run — a soft restart is not enough.

Keep ComfyUI in **one durable session**. Matcha does not manage that process.
A second generate (or a UI "interrupt") that issues a global interrupt can
kill an in-flight pose. If a run dies mid-batch, already-accepted PNGs stay
on disk (see **Partial runs** below).

## Same-face lock = VNCCS Character Cloner (not prompt+seed)

[VNCCS](https://github.com/AHEKOT/ComfyUI_VNCCS) (MIT) is the character
consistency engine. Matcha does **not** compete with it on generation —
`--backend vnccs` queues their shipped 3.0 graph via the same ComfyUI
`/prompt` API.

**The lock is Character Cloner from an existing approved sprite**, not
Character Creator from text. prompt+seed is not a lock. IP-Adapter stays
off on MPS.

1. **Character Cloner** (primary) — collage from a sandbox `reference:` /
   `--reference` PNG. Requires `CharacterCloner` +
   `VNCCS_CharacterCloneGenerator`.
2. **Character Creator** (fallback) — text/tags via `CharacterCreatorV2`.
   Use this only when there is no approved sprite to clone. It is **not**
   a lock.
3. **txt2img** — trusted first success (`--lora none`). Not VNCCS. Do not
   pretend it is.

If those nodes are missing, Matcha **errors** with install steps. It will
not silently fall back to txt2img and call that consistent.

### Approved sprite — hand-copy into `refs/` (never your live game)

If you already have an approved sprite inside a live game, that path stays
out of Matcha — Matcha **cannot and must not** read or write the live game
tree. Hand-copy the approved PNG out of your live game
(`<your-live-game>/game/images/...`) into the Matcha sandbox `refs/` folder
**by hand**. Never `--project` your live game. Never point `reference:` or
`--reference` at it — Matcha refuses known live-game paths before any read.

```bash
mkdir -p refs
# After you have a hand-copied PNG (not the live game path):
cp "/path/to/hand-copied/kite_male neutral.png" refs/kite_male_neutral.png
```

YAML (`configs/kite_male.yaml`):

```yaml
reference: ./refs/kite_male_neutral.png
```

Then:

```bash
.venv/bin/matcha character configs/kite_male.yaml --backend vnccs --dry-run
.venv/bin/matcha character configs/kite_male.yaml --backend vnccs --poses neutral
# or: --reference ./refs/kite_male_neutral.png  (implies --backend vnccs)
```

`--vnccs-ref` is an alias for `--reference`. That is **not** IP-Adapter
and does not turn IPA on. `refs/*.png` is gitignored so the live sprite
is never committed. YAML `reference:` alone does **not** switch the
default backend — trusted first success stays txt2img until you pass
`--backend vnccs`.

### Apple Silicon / MPS — VNCCS is not txt2img

VNCCS 3.0's Control Center default is **Qwen-Image-Edit GGUF** plus
Impact / FaceDetailer / SAM companions. Those are CUDA-oriented. On a
ComfyUI device whose `/system_stats` type or name contains `mps` /
`metal`, `--backend vnccs` **fails preflight** with that explanation.

That failure is still the VNCCS path. Matcha will **not** silently run
KSampler txt2img and call it VNCCS. `--vnccs-allow-mps` queues the real
Cloner / Creator nodes anyway (still not txt2img; GGUF / Impact / SAM
may still fail at runtime).

On a typical Mac MPS dev box ComfyUI lives at `~/ComfyUI` — and if it has
`ComfyUI_IPAdapter_plus` only, **VNCCS is not installed there yet.**
IP-Adapter stays off. A CUDA ComfyUI is the honest same-face machine.

### Install VNCCS

ComfyUI Manager (easiest):

1. Search and install **VNCCS - Visual Novel Character Creation Suite**
2. Search and install **VNCCS Utils** (Pose Studio lives here)
3. Restart ComfyUI
4. Open a VNCCS 3.0 workflow. In **Control Center**, download the
   recommended Qwen-Image-Edit GGUF + helper LoRAs (Pose Studio QIE,
   Clothes Core, …). Wiki: [Installation-and-Updates](https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Installation-and-Updates)

Manual:

```bash
cd ~/ComfyUI/custom_nodes
git clone https://github.com/AHEKOT/ComfyUI_VNCCS
git clone https://github.com/AHEKOT/ComfyUI_VNCCS_Utils
# restart ComfyUI, then use Control Center to pull models
```

Honest limits: VNCCS 3.0 is UI-heavy (`widget_data` / Pose Studio WebGL).
Matcha fills their widgets from YAML (identity + pose + outfit families)
and injects headless pose plates so Pose Studio can emit IMAGE without a
browser tab. Keep the ComfyUI tab open if you want their 3D captures.
Control Center models are **Qwen-Image-Edit**, not the YAML Anything V5
checkpoint — that checkpoint is only used for the Character Creator
preview (`generation_mode: illustrious`). Default `--backend txt2img`
/`--lora none` stays the trusted 512 first-success path.

## Trusted first success

Checked-in sample Ren'Py project: [`examples/sample-vn/`](examples/sample-vn/).
Sprites are not committed — Placeholders until you generate. Open it in Ren'Py
anytime; generate only after ComfyUI + a checkpoint (section above) are ready.

Goal: one clean base-checkpoint generate into the sample project — not a
perfect style LoRA on day one.

```bash
# 0. Server up? Expect 200 — skip this cliff and dry-run fails immediately
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/

# 1. Validate config + models (ComfyUI must be running; no GPU work)
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --dry-run

# 2. Generate with LoRA off (safest first path) + deploy into sample-vn
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --lora none --deploy --project examples/sample-vn --layered

# 3. Open with the Ren'Py SDK (adjust path)
~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn
```

Click through the pose lineup in `script.rpy`. Lint without launching the UI:
`~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn lint`.

After that works, optionally set a LoRA in the YAML (machine-specific; e.g.
`last.safetensors` @ 0.7 on some Macs) or pass `--lora your_lora.safetensors`.

Or scaffold your own tree: `.venv/bin/matcha init myproject`, then point
`--project` at any Ren'Py game directory.

**Do not** deploy into a live game you are polishing — Ren'Py auto-loads every
`game/*.rpy`. Use `examples/sample-vn/` or a throwaway `sandbox-renpy/` /
`sandbox-kite/` (gitignored). Matcha **refuses** `--project` paths that look
like a known live game. The author's own VN project already owns those
`define` / `layeredimage` lines; hand-copy PNGs (or use `--copy-only`)
instead of letting Matcha write the live script.

## CLI overview

| Command | What it does |
|---|---|
| `matcha character <config.yaml>` | Generate sprites; `--backend vnccs --reference` for Character Cloner same-face; `--poses`, `--copy-only`, `--deploy`, `--dry-run`, `--lora none` |
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
`--deploy` writes `game/matcha_characters.rpy` — idempotent on re-run, never
touches your hand-written scripts, but still dangerous in a live game.
Only poses that actually generated get definitions; the CLI exits non-zero
if any pose fails. For last-mile copies into the author's own VN project,
use `--copy-only` (below).

### Ren'Py scaffolding flags

Default: flat `image <char> <pose>` per pose. Opt in for a richer setup:

- `--layered` / `layered: true` — `layeredimage` with poses as attributes
  (`show sakura happy`; first pose is `default`)
- `--side-image` / `side_image: true` — crop head/shoulders portraits, emit
  `image side <char> <pose>`, wire `Character(image="<char>")` for dialogue
- YAML `display_name:` / `color:` — Character display name and name color

```bash
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --lora none --deploy --project examples/sample-vn --layered --side-image
```

### Look sheet (shared face, per-pose outfit)

Keep hair / eyes / face in `description`. Put **outfit families** in
`outfit_families` + `pose_overrides.family` (or inline `- name: smoking`
mappings) so a bartender apron cannot paint onto `smoking`.

Unknown pose names stay as plain wording (`crossed_arms` → `crossed arms`).
They do **not** become `{pose} expression, {pose} pose`.

The author's own VN project disk spec (live-game filenames — do **not**
`--project` your live game) is
[`configs/kite_male.yaml`](configs/kite_male.yaml):

| Family | Outfit | Poses |
|---|---|---|
| Apron / bar | charcoal long-sleeve button shirt + dark buckle apron | warm, soft, neutral, stressed, tired, gentle, **crossed_arms** |
| Home henley | olive/charcoal henley or polo, no apron | relaxed, smoking (seated on a ledge with a cigarette) |
| Withdrawn dark shirt | oversized dark long-sleeve button shirt, no apron | withdrawn only |

Ten files on disk: `kite_male <pose>.png` (space) for those names.
`angry` is **not** a file — it aliases `stressed`. `crossed_arms` is still
emitted as `kite_male crossed_arms.png` (apron family). The live game scales
it 1.39 because that file is 880×1184 vs other kite_male 1200×992 — display,
not generate. Later `--canvas` copy-out should be one uniform size so the
live game can drop that special case. Never `--project` your live game.

### Partial runs, `--poses`, rejects

Each accepted pose is written to `output_dir` **as soon as it passes** the
quality guard (`<name>_<pose>.png`). A 15-minute crash no longer orphans
finished poses in ComfyUI with zero files on disk.

```bash
# One pose (or a subset) without rerunning the full YAML list
.venv/bin/matcha character configs/kite_male.yaml --lora none --poses smoking

# Already-accepted PNGs are skipped; --force regenerates
.venv/bin/matcha character configs/kite_male.yaml --lora none --poses warm,soft
```

Smear + right-edge static-band frames (the Mac MPS Anything V5 failure) are
**rejected**. The PNG and the metrics used (adjacent-luma Δ, edge, strip
ratio, high-freq fraction) land in `output_dir/rejected/<name>_<pose>_seedN.png`
(+ `.json`) so a long run stays inspectable. The CLI then retries with a new
seed (`quality_retries` in YAML, or `--retries`). A global-threshold guard
that required both adj ≥ 15 **and** edge ≥ 48 is what let those frames
through locally; this repo measures the **edge strip vs the interior**
instead.

### Copy-only deploy (no script writes)

`--deploy` into a real game stays dangerous. For the author's own VN
project, `--copy-only` writes
`kite_male <pose>.png` (space) into `game/images/` and does **not** write
`Character()`, `layeredimage`, or `_kite_sprite`. Underscore names
(`kite_male_smoking.png`, `kite_<pose>.png`) will not drop into the live
game.

```bash
.venv/bin/matcha character configs/kite_male.yaml --lora none --poses smoking \
  --copy-only --project sandbox-renpy
# dest: game/images/kite_male smoking.png
```

`configs/kite_male.yaml` sets `filename_template: "{name} {pose}.png"`.
`--filename-template` overrides if needed. `--images-subdir characters` puts
files under `game/images/characters/` instead. Later, one `--canvas` size
for every kite_male pose lets the live game drop the 1.39 `crossed_arms`
scale. Never `--project` your live game.

Optional extras (Pillow only, no rembg / GPU): `--knockout-black` turns
near-black pixels transparent (grey/white studio cards stay opaque — a
subject matte would need rembg, which we skipped). `--canvas 768x1024` pads
an accepted 512×512 onto a larger canvas; it does **not** change generation
resolution. Later live-game copy-out should use **one** canvas for every
`kite_male` pose so the live game can drop the 1.39 `crossed_arms` scale
(that file is 880×1184 vs 1200×992). **512×512 `--lora none` remains the
trusted first-success default.** Never `--project` your live game.

## Development

```bash
.venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/
```

Tests are fully mocked — no ComfyUI or GPU required.
