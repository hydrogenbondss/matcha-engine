# Matcha Engine — Phase 2 announce plan

Executable checklist for the first public posts. Goal: show a stranger that
YAML → ComfyUI → Ren'Py sprites is real, without hyping past known Mac MPS
limits. **Never hide AI.** Point to `matcha licenses` / `matcha disclose`.

Do **not** post on artist-heavy general VN forums. Target: Lemma Soft (tools),
Ren'Py Discord, r/comfyui, Civitai.

---

## 0. Before you shoot

```bash
# ComfyUI up at 127.0.0.1:8188 (see AGENTS.md / README for Mac MPS flags)
cd /path/to/matcha-engine
.venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \
  --deploy --project examples/sample-vn --layered

# Optional portraits for one announce still:
#   … --layered --side-image

~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn
```

Use config as-is (`last.safetensors` + `anythingV5PrtRE`). Prefer a clean
terminal font and a dark editor theme so YAML/CLI screenshots read well.

Generated PNGs under `game/images/characters/` stay gitignored — capture
locally; do not commit them for the announce.

---

## 1. Shot list

Capture stills at **1280×720** (or crop cleanly to 16:9). Name files as below
so the GIF script stays boring.

| # | File | What to capture | Framing notes |
|---|------|-----------------|---------------|
| 1 | `01-config.png` | `examples/sample-vn/configs/example_character.yaml` open in editor | Show `name`, `description`, `poses:` (idle/happy/sad/surprised), checkpoint/LoRA lines. Crop UI chrome if noisy. |
| 2 | `02-terminal.png` | Terminal mid/after generate | Full command with `--deploy --project examples/sample-vn --layered`, plus a few lines of progress / “Deployed N images”. No secrets. |
| 3 | `03-renpy-idle.png` | Ren'Py: Sakura **idle** | Full window titled “Matcha Engine Sample”; character centered; dialogue visible. |
| 4 | `04-renpy-happy.png` | Same shot, **happy** | Same framing as #3 — identity lock is the point. |
| 5 | `05-renpy-sad.png` | Same shot, **sad** | Same framing. |
| 6 | `06-renpy-surprised.png` | Same shot, **surprised** | Same framing. |
| 7 | *(optional)* `07-side-image.png` | Dialogue with side portrait | Only if you regenerated with `--side-image`. |

### Short GIF (~8–12 s)

Loop: **config → terminal → idle → happy → sad → surprised** (frames 1→2→3→4→5→6).

Suggested hold times: config 1.5s, terminal 2s, each pose ~1.2s. Export
`matcha-engine-demo.gif` at ≤ ~3 MB (or a short mp4 + GIF fallback).

Tooling example (ImageMagick), after stills exist in `~/Desktop/matcha-announce/`:

```bash
cd ~/Desktop/matcha-announce
magick -delay 150 01-config.png -delay 200 02-terminal.png \
  -delay 120 03-renpy-idle.png 04-renpy-happy.png 05-renpy-sad.png 06-renpy-surprised.png \
  -loop 0 matcha-engine-demo.gif
```

---

## 2. Copy drafts

Tone: honest, concrete, short. Product name: **Matcha Engine** (`matcha` CLI).
Mention Mac MPS limits lightly where the audience cares about local Apple Silicon.
Always say sprites are AI-generated via the user’s own ComfyUI.

### Lemma Soft forums (tools / utilities thread)

**Title:** Matcha Engine — YAML → ComfyUI sprites → Ren'Py deploy (CLI)

**Body:**

```
Matcha Engine is a small open CLI for Ren'Py character pipelines.

You define a character once in YAML (identity prompt + poses). It talks to a
local ComfyUI server, generates the pose set, and writes images +
matcha_characters.rpy into your project (folders, image/layeredimage/
Character defs). Opt-in --layered and --side-image for portraits.

It is orchestration + last mile — not a hosted model and not a GUI.

Honest limits (esp. Mac MPS): shared seed + locked prompts work; img2img /
IP-Adapter paths are off by default because they currently corrupt on Apple
Silicon. CUDA may do better later.

Also ships matcha licenses (checkpoint/LoRA commercial-use status lookup —
not legal advice) and matcha disclose (Steam AI survey + itch.io AI-tag draft).
Do not hide AI assets.

Repo + sample VN: <GITHUB_URL>
Example: examples/sample-vn/ — clone, generate, click the pose lineup.
```

### Ren'Py Discord

```
**Matcha Engine** — CLI: YAML character → local ComfyUI → sprites + Ren'Py defs

One config → consistent expression set → `game/images/characters/` +
`matcha_characters.rpy`. `--deploy --layered` / `--side-image` optional.

Sample project in the repo (`examples/sample-vn/`). Mac MPS: keep consistency
features off (documented). Helpers: `matcha licenses`, `matcha disclose`.

Repo: <GITHUB_URL>
```

### r/comfyui

**Title:** Matcha Engine — ComfyUI-backed Ren'Py character sprite CLI (YAML → deploy)

**Body:**

```
Built a thin CLI around ComfyUI for visual novel sprites.

Flow: character YAML (checkpoint/LoRA, poses, seed) → queue on
127.0.0.1:8188 → download PNGs → copy into a Ren'Py tree and emit image /
layeredimage / Character blocks.

Not a custom node pack — a project-level orchestrator. Preflight checks that
models exist; black-PNG guard on bad MPS runs.

On Apple Silicon we force LoRA strength_clip=0 and leave IP-Adapter / img2img
off by default (corruption). Prompt + shared seed is the local consistency
story for now.

Repo + sample Ren'Py project: <GITHUB_URL>
Happy to hear CUDA workflow tips (IPA / better identity lock).
```

### Civitai (post / model-card style description)

**Title:** Matcha Engine — Ren'Py sprite pipeline (ComfyUI)

**Description:**

```
Matcha Engine (`matcha`) turns a YAML character into a Ren'Py-ready sprite
set using your own ComfyUI install.

• Poses from one identity prompt + shared seed
• Deploy into game/images/characters/ + matcha_characters.rpy
• Optional layeredimage + cropped side images
• License lookup + Steam/itch disclosure drafts (be honest about AI)

Sample: examples/sample-vn in the repo.
Mac MPS users: read the README — some “consistency” features corrupt locally.

Repo: <GITHUB_URL>
Tags: renpy, visualnovel, comfyui, sprites, tool
```

Replace `<GITHUB_URL>` with the public repo URL before posting.

---

## 3. Post checklist

1. [x] ComfyUI running; clean quit if a previous IPA run wedged MPS
2. [x] Generate + deploy into `examples/sample-vn` (layered; optional side-image for one still) — **done locally 2026-08-05** (`last` LoRA + `anythingV5PrtRE`, `--layered`; side-image **not** run). Sprites at `examples/sample-vn/game/images/characters/sakura_{idle,happy,sad,surprised}.png` (gitignored). Ren'Py lint clean.
3. [ ] Click through `script.rpy` — confirm four poses look like one character
4. [ ] Capture shot list #1–#6 (+ optional #7); build GIF — **human capture still required** (open Ren'Py GUI; no programmatic stills this pass)
5. [ ] Paste copy drafts; fill `<GITHUB_URL>`; skim for leftover “Match Engine”
6. [ ] Post order (same day or close): **Civitai** (asset/home base) → **r/comfyui** → **Ren'Py Discord** → **Lemma Soft**
7. [ ] Tick Phase 2 announce boxes in [TIMELINE.md](../TIMELINE.md) when posts are live
8. [ ] Do **not** deploy announce characters into live LOVE32

### Capture now (after local generate)

```bash
# From repo root — project already has layered defs + PNGs from 2026-08-05 deploy
~/Desktop/renpy-8.5.2-sdk/renpy.sh examples/sample-vn
```

Then shoot §1 rows **#1–#6** into `~/Desktop/matcha-announce/` and run the ImageMagick GIF command above. Optional #7 only after a `--side-image` redeploy.

Screenshots / GIF stay on your machine (or a private folder) until you attach
them to posts — they are not required in git.
