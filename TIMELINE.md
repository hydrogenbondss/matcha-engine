# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Update
the status boxes as work lands. Detailed positioning and rationale live in
[STRATEGY.md](STRATEGY.md); rolling engineering notes live in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
that ties those together to the phased plan (STRATEGY.md §6).

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-07-21_

---

## Where we are right now

- **Current phase:** Month 1 — *Pipeline demo works*.
- **Shipped:** v0.2.0 pipeline (config → preflight → generate → deploy →
  Ren'Py `.rpy`), verified end-to-end against a **mock** ComfyUI and by 19
  passing unit tests.
- **Biggest open risk:** no real-GPU run yet — sprite *quality/consistency* is
  unproven, and the `small_hours_style_v1` LoRA's base model (SD1.5 vs SDXL) is
  still unconfirmed, which decides the correct checkpoint.

---

## Phase 1 — Pipeline demo works (Month 1)

Exit criteria: a real character set generates on a GPU and deploys cleanly into
a real Ren'Py project, with the four product bugs closed.

- [x] Repo + CLI skeleton (`init`, `character`)
- [x] Pydantic config schema; checkpoint/LoRA are YAML fields, not hardcoded
- [x] ComfyUI generator (workflow build, queue, WS completion, image fetch)
- [x] Ren'Py formatter (naming, resize, script block)
- [x] Filesystem deployer (images + idempotent `game/matcha_characters.rpy`)
- [x] First working pipeline verified end-to-end (against mock ComfyUI)
- [x] v0.2 hardening: preflight `/object_info` validation, loud per-pose
      failures, no-deploy-on-zero-images, idempotent deploy
- [x] Dev environment reproducible (venv + `pip install -e .`, tests green)
- [!] **First real-GPU run** — blocked on: pick the checkpoint matching the
      LoRA's base model (SD1.5 vs SDXL); needs a ComfyUI server + GPU
- [ ] Confirm `small_hours_style_v1` base model (unblocks the run above)
- [ ] Dogfood on the actual **LOVE32** Ren'Py project
- [ ] Evaluate consistency vs **VNCCS**; decide wrap-vs-own (STRATEGY.md §4.2)

## Phase 2 — Free release (Months 2–3)

Exit criteria: a stranger can install the CLI, generate, and deploy without us.

- [ ] Deploy polish: `layeredimage` / side-image / `Character` scaffolding
      (STRATEGY.md §4.3 — the differentiator, over-invest here)
- [ ] Per-model license surfacing (STRATEGY.md §4.6)
- [ ] Disclosure helper: Steam AI survey text + itch.io tag reminder (§4.7)
- [ ] Install/README polish for non-us users; example project
- [ ] Announce: Lemma Soft, Ren'Py Discord, r/comfyui, Civitai

## Phase 3 — First dollar (Months 3–4)

Exit criteria: money changes hands at least once.

- [ ] Pro package (packaged installer, preset library, one-command deploy)
- [ ] List on itch.io + Gumroad (~$19–29 one-time)
- [ ] Free VN-style LoRA(s) on Civitai as the acquisition loop

## Phase 4 — Hosted, conditional (Month 6+)

Only pursue if ≥ ~100 Pro sales.

- [ ] Serverless inference (Replicate / fal)
- [ ] Auth + billing + abuse handling

---

## Open verification items (carry-over from STRATEGY.md §8)

- [ ] `small_hours_style_v1` base model (SD1.5 vs SDXL)
- [ ] VNCCS traction (conflicting star counts)
- [ ] Re-verify Lemma Soft commission price ranges before public quoting
- [ ] "No one else does Ren'Py deploy" — searched, not exhaustively proven
