# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Update
the status boxes as work lands. Detailed positioning and rationale live in
[STRATEGY.md](STRATEGY.md); rolling engineering notes live in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
that ties those together to the phased plan (STRATEGY.md §6).

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-07-23 (consistency prompts, black-image guard, output_dir)_

---

## Where we are right now

- **Current phase:** Month 1 — *Pipeline demo works* (nearly closed).
- **Shipped:** v0.2.0 pipeline verified on **live ComfyUI (Mac MPS)** —
  4 sakura poses generated, deployed into LOVE32 with `--layered
  --side-image`, and `renpy.sh … lint` reports no matcha script errors.
- **Biggest open risk:** sprite *consistency* across poses (outfit/eye drift,
  dual-sprite sheets) — prompt locking + shared seed landed 2026-07-23;
  still need play-test / VNCCS eval. `small_hours_style_v1` still NaNs on
  Mac MPS (interim LoRA: `last.safetensors`).

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
- [x] Confirm `small_hours_style_v1` base model — **SD1.5** (safetensors
      metadata: `stable-diffusion-v1/lora`, trained on `sd-v1-5-pruned`;
      pairs with `anythingV5PrtRE.safetensors`, already on local Mac)
- [x] **First real-GPU run** (2026-07-23, Mac MPS) — 4/4 poses via live
      ComfyUI; use `--fp32-vae --cpu-vae --lowvram` (no `--force-fp16`)
- [x] Dogfood on the actual **LOVE32** Ren'Py project
      (`~/Desktop/LOVE32/LOVE32/`) — images under
      `game/images/characters/sakura_*.png` + `game/matcha_characters.rpy`
- [x] Verify generated `.rpy` with Ren'Py SDK lint
      (`~/Desktop/renpy-8.5.2-sdk/renpy.sh … lint`) — clean for matcha
- [x] Consistency hardening (shared seed, locked outfit prompt, sprite
      framing positives/negatives, reject black/NaN PNGs, wire `output_dir`)
- [!] Fix / replace `small_hours_style_v1` on MPS (black/NaN); interim
      `last.safetensors` @ 0.7 works
- [ ] Evaluate consistency vs **VNCCS**; decide wrap-vs-own (STRATEGY.md §4.2)
- [ ] Re-run 4-pose set with new prompts and eyeball / play-test in LOVE32
## Phase 2 — Free release (Months 2–3)

Exit criteria: a stranger can install the CLI, generate, and deploy without us.

- [~] Deploy polish: `layeredimage` / side-image / `Character` scaffolding
      (STRATEGY.md §4.3 — the differentiator, over-invest here)
      - [x] Opt-in `layeredimage` grouping poses as attributes (`--layered`)
      - [x] Side-image defs + `Character(image=...)` wiring (`--side-image`)
      - [x] Richer `Character` (display name + color) via config
      - [ ] Generate *cropped portrait* side images (currently reuse full sprite)
      - [x] Verify generated `.rpy` via Ren'Py SDK lint (2026-07-23 on LOVE32)
      - [ ] Interactive play-test of `show sakura …` in the LOVE32 launcher
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

- [x] `small_hours_style_v1` base model — **SD1.5** (confirmed 2026-07-22
      via LoRA safetensors metadata; use `anythingV5PrtRE`, not `sd_xl_base`)
- [ ] VNCCS traction (conflicting star counts)
- [ ] Re-verify Lemma Soft commission price ranges before public quoting
- [ ] "No one else does Ren'Py deploy" — searched, not exhaustively proven
