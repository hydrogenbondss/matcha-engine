# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Detailed
positioning lives in [STRATEGY.md](STRATEGY.md); engineering notes in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
of STRATEGY.md §6.

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-07-27 (LoRA clip=0 MPS fix; clean 4-pose sandbox re-run)_

---

## Phase map (4 phases)

| # | Phase | Goal | Exit criteria |
|---|--------|------|----------------|
| **1** | Pipeline demo | Config → sprites → Ren'Py deploy works on real GPU | 4 usable poses in **sandbox**; play-tested; consistency good enough *or* wrap/IP-Adapter decided |
| **2** | Free release | A stranger can install and use it | README + example project; cropped side images; license/disclosure helpers; public announce |
| **3** | First dollar | Money changes hands | Pro pack on itch/Gumroad; acquisition LoRA(s) on Civitai |
| **4** | Hosted (optional) | Cloud generate | Only if ≥~100 Pro sales — Replicate/fal + auth/billing |

**You are here:** end of **Phase 1** — plumbing is done; the remaining gate is
**sprite consistency + sandbox play-test**. Do **not** deploy into live LOVE32
while that game is being polished (use `sandbox-renpy/` only).

---

## Where we are right now

- **Current phase:** Phase 1 — close-out (consistency + sandbox play-test).
- **Shipped:** v0.2 pipeline on live ComfyUI (Mac MPS); preflight; black-PNG
  guard; shared seed + locked prompts; layered/side-image scaffolding;
  dogfood target = `sandbox-renpy/` (LOVE32 cleared of matcha artifacts).
- **In flight:** IP-Adapter consistency prototype (hair/outfit still drifts).
- **Biggest open risk:** poses still drift (outfit/hair/ponytail). img2img
  chaining glitched on MPS — disabled. LoRA on MPS needs `strength_clip=0`
  (shipped). Next consistency lever: **IP-Adapter** or **VNCCS** wrap-vs-own.

### Phase 1 — next actions (this week)

1. ~~Play-test sandbox sprites~~ — done 2026-07-27 (no side-image double-up).
2. Prototype IP-Adapter from first pose (preferred over broken img2img on MPS).
3. ~~Commit pending matcha code~~ (img2img default off; LoRA clip=0 on MPS).
4. Only then consider Phase 2 polish — **not** more LOVE32 deploys.

---

## Phase 1 — Pipeline demo works (Month 1)

Exit criteria: a real character set generates on GPU and deploys cleanly into
a **sandbox** Ren'Py project; consistency accepted or a wrap path chosen.

- [x] Repo + CLI skeleton (`init`, `character`)
- [x] Pydantic config; checkpoint/LoRA are YAML fields
- [x] ComfyUI generator + Ren'Py formatter + filesystem deployer
- [x] Mock ComfyUI e2e + 31 unit tests
- [x] Preflight, loud failures, no-deploy-on-zero, idempotent `.rpy`
- [x] Dev env (venv, `pip install -e .`); LoRA base confirmed SD1.5
- [x] First real-GPU run (Mac MPS); Ren'Py SDK lint of generated `.rpy`
- [x] Consistency prompts + shared seed + black-image guard + `output_dir`
- [x] img2img chaining code — **default off** (MPS glitch); use `1.0`
- [x] Stop using live LOVE32 as dogfood; sandbox project only
  - [x] txt2img-only 4-pose sandbox re-run (LoRA clip=0; no half-static)
  - [x] Eyeball / play-test in `sandbox-renpy/` (Ren'Py launcher)
- [!] `small_hours_style_v1` NaNs on MPS — interim `last.safetensors` @ 0.7
- [ ] Consistency path: IP-Adapter and/or VNCCS wrap-vs-own (STRATEGY §4.2)

## Phase 2 — Free release (Months 2–3)

Exit criteria: a stranger can install the CLI, generate, and deploy without us.

**Do in this phase**

- [~] Deploy polish (STRATEGY §4.3 — over-invest here)
  - [x] `--layered` / `--side-image` / display name + color
  - [ ] Cropped portrait side images (not full-sprite reuse)
  - [ ] Documented play-test recipe against `sandbox-renpy/`
- [ ] Per-model license surfacing (§4.6)
- [ ] Disclosure helper: Steam AI survey + itch.io tag reminder (§4.7)
- [ ] Install/README + example project for outsiders
- [ ] Announce: Lemma Soft, Ren'Py Discord, r/comfyui, Civitai

## Phase 3 — First dollar (Months 3–4)

Exit criteria: money changes hands at least once.

**Do in this phase**

- [ ] Pro package (installer, presets, one-command deploy)
- [ ] List on itch.io + Gumroad (~$19–29)
- [ ] Free VN-style LoRA(s) on Civitai (acquisition loop)

## Phase 4 — Hosted, conditional (Month 6+)

Only if ≥ ~100 Pro sales.

**Do in this phase**

- [ ] Serverless inference (Replicate / fal)
- [ ] Auth + billing + abuse handling

---

## Open verification items (STRATEGY.md §8)

- [x] `small_hours_style_v1` base — **SD1.5** (use `anythingV5PrtRE`, not SDXL)
- [ ] VNCCS traction (conflicting star counts)
- [ ] Re-verify Lemma Soft commission price ranges before public quoting
- [ ] "No one else does Ren'Py deploy" — searched, not exhaustively proven
