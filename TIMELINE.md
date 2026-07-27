# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Detailed
positioning lives in [STRATEGY.md](STRATEGY.md); engineering notes in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
of STRATEGY.md §6.

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-07-27 (Phase 1 closed; prompt+seed consistency accepted)_

---

## Phase map (4 phases)

| # | Phase | Goal | Exit criteria |
|---|--------|------|----------------|
| **1** | Pipeline demo | Config → sprites → Ren'Py deploy works on real GPU | 4 usable poses in **sandbox**; play-tested; consistency good enough *or* wrap/IP-Adapter decided |
| **2** | Free release | A stranger can install and use it | README + example project; cropped side images; license/disclosure helpers; public announce |
| **3** | First dollar | Money changes hands | Pro pack on itch/Gumroad; acquisition LoRA(s) on Civitai |
| **4** | Hosted (optional) | Cloud generate | Only if ≥~100 Pro sales — Replicate/fal + auth/billing |

**You are here:** start of **Phase 2**. Phase 1 is closed: pipeline demo works on
Mac MPS; sandbox play-tested; consistency accepted as prompt+seed (IP-Adapter /
img2img both corrupt on this MPS stack — code kept, default off). Do **not**
deploy into live LOVE32 while that game is being polished (use `sandbox-renpy/`).

---

## Where we are right now

- **Current phase:** Phase 2 — Free release.
- **Shipped (Phase 1):** v0.2 pipeline on live ComfyUI (Mac MPS); preflight;
  black-PNG guard; shared seed + locked prompts; LoRA `strength_clip=0`;
  layered/side-image scaffolding; sandbox dogfood; IP-Adapter path (default off).
- **In flight:** Phase 2 polish for outsider install + deploy.
- **Known MPS limits:** img2img and IP-Adapter corrupt — leave off locally.
  Re-try IP-Adapter on CUDA when available. Pose drift remains acceptable for
  Phase 1 exit; improve later if CUDA IPA works.

### Phase 2 — next actions

1. Documented play-test recipe + README install for strangers.
2. Cropped portrait side images (not full-sprite reuse).
3. Example project strangers can clone.
4. License/disclosure helpers (Steam AI survey, itch tag).

---

## Phase 1 — Pipeline demo works (Month 1) — CLOSED 2026-07-27

Exit criteria: a real character set generates on GPU and deploys cleanly into
a **sandbox** Ren'Py project; consistency accepted or a wrap path chosen.

- [x] Repo + CLI skeleton (`init`, `character`)
- [x] Pydantic config; checkpoint/LoRA are YAML fields
- [x] ComfyUI generator + Ren'Py formatter + filesystem deployer
- [x] Mock ComfyUI e2e + unit tests
- [x] Preflight, loud failures, no-deploy-on-zero, idempotent `.rpy`
- [x] Dev env (venv, `pip install -e .`); LoRA base confirmed SD1.5
- [x] First real-GPU run (Mac MPS); Ren'Py SDK lint of generated `.rpy`
- [x] Consistency prompts + shared seed + black-image guard + `output_dir`
- [x] img2img chaining code — **default off** (MPS glitch); use `1.0`
- [x] Stop using live LOVE32 as dogfood; sandbox project only
- [x] txt2img-only 4-pose sandbox re-run (LoRA clip=0; no half-static)
- [x] Eyeball / play-test in `sandbox-renpy/` (Ren'Py launcher)
- [x] IP-Adapter workflow + preflight (default off; MPS corrupts)
- [x] Consistency path decision: **accept prompt+seed on MPS**; CUDA IPA / VNCCS optional later
- [!] `small_hours_style_v1` NaNs on MPS — interim `last.safetensors` @ 0.7

## Phase 2 — Free release (Months 2–3)

Exit criteria: a stranger can install the CLI, generate, and deploy without us.

**Do in this phase**

- [~] Deploy polish (STRATEGY §4.3 — over-invest here)
  - [x] `--layered` / `--side-image` / display name + color
  - [ ] Cropped portrait side images (not full-sprite reuse)
  - [x] Documented play-test recipe against `sandbox-renpy/` (README)
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
