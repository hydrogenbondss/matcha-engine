# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Detailed
positioning lives in [STRATEGY.md](STRATEGY.md); engineering notes in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
of STRATEGY.md §6.

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-08-06 (north star in STRATEGY §1; v0.1.0 quiet tag; announce still held)_

---

## Phase map (4 phases)

Keep **four** phases — do not invent a fifth for consistency. CUDA IP-Adapter /
VNCCS stay optional levers inside Phase 2/3, not a gate that stalls forever on
Mac MPS.

| # | Phase | Goal | Exit criteria |
|---|--------|------|----------------|
| **1** | Pipeline demo | Config → sprites → Ren'Py deploy works on a real GPU *for you* | 4 usable poses in **sandbox**; play-tested; consistency path decided |
| **2** | Free release | A stranger can install, generate, and deploy without us | Example project; cropped side images; license/disclosure helpers; README limits honest; public announce |
| **3** | First dollar | Money changes hands | Pro pack on itch/Gumroad; ≥1 paid sale; acquisition LoRA(s) on Civitai |
| **4** | Hosted (conditional) | Cloud generate | Only if ≥~100 Pro sales — Replicate/fal + auth/billing |

```
Phase1 → Phase2 → Phase3 ──(if ~100 Pro sales)──► Phase4
```

**You are here:** **Phase 2 — Free release.** Phase 1 is closed (2026-07-27).
Do **not** deploy into live LOVE32 while that game is being polished — use
`examples/sample-vn/` (checked in) or gitignored `sandbox-renpy/`.

---

## Where we are right now

- **North star:** documented in [STRATEGY.md](STRATEGY.md) §1 (wedge-first
  AI-native creation; not a full engine) — 2026-08-06.
- **Current phase:** Phase 2 — Free release.
- **Shipped (Phase 1):** v0.2 pipeline on live ComfyUI (Mac MPS); preflight;
  black-PNG guard; shared seed + locked prompts; LoRA `strength_clip=0`;
  layered/side-image scaffolding; sandbox dogfood; IP-Adapter path (default off).
- **Shipped (Phase 2 preview):** quiet **v0.1.0** tag (2026-08-06) — free CLI
  preview; README ComfyUI + models onboarding (install, paths, name match /
  `--checkpoint` / `--lora none`, `curl` health-check cliff, Mac MPS limits,
  Placeholders without generation). No forum announce.
- **In flight:** Phase 2 announce (#6) — copy drafts + shot list in
  [`docs/ANNOUNCE.md`](docs/ANNOUNCE.md). **Cold stranger walkthrough
  2026-08-05:** fresh `/tmp` clone → venv install → start ComfyUI (Mac MPS
  flags) → dry-run → generate+deploy 4/4 poses → Ren'Py lint OK;
  `licenses` / `disclose` OK; 49 tests pass. Screenshots/GIF still need human
  capture. **Do not announce yet** — ComfyUI/GPU + obtaining models remain the
  real stranger blockers.
- **Mac / MPS limits (document in README, do not hide):** img2img and
  IP-Adapter corrupt — leave off locally (`consistency_denoise: 1.0`,
  `ip_adapter_weight: 0`). Consistency = prompt + shared seed. CUDA IPA is
  Phase 2 stretch / Phase 3 Pro value-add, **not** a Phase 2 exit gate.
  After heavy IPA runs, fully quit ComfyUI (or reboot) before the next clean
  generation.

### Phase 2 — next actions (ordered)

1. ~~Cropped portrait side images (not full-sprite reuse).~~ **done**
2. ~~Example / sample Ren'Py project strangers can clone.~~ **done** (`examples/sample-vn/`)
3. ~~Per-model license surfacing + Steam/itch disclosure helpers.~~ **done**
   (`matcha licenses`, `matcha disclose`, printed on `character` runs)
4. ~~Finish outsider install/README cold-start polish.~~ **done** (re-verified
   2026-08-05 cold clone walkthrough; ComfyUI+models onboarding expanded +
   quiet v0.1.0 tag 2026-08-06; remaining stranger gaps are obtaining
   ComfyUI/GPU + checkpoint/LoRA, not Matcha install)
5. Announce: Lemma Soft, Ren'Py Discord, r/comfyui, Civitai —
   copy/shot plan in `docs/ANNOUNCE.md`; local sprites ready (2026-08-05);
   posts + screenshots still pending — **hold announce** (v0.1.0 is tag-only;
   no forum posts required for this ship)

---

## Phase 1 — Pipeline demo (Month 1) — CLOSED 2026-07-27

**Goal:** Config → sprites → Ren'Py deploy works on a real GPU for *you*.

**Exit (met):** 4 usable poses in `sandbox-renpy/`; play-tested; consistency
path decided (prompt+seed on MPS; IP-Adapter/img2img default off).

**Out of scope for this phase:** public announce, payments, LOVE32 live deploy.

- [x] Repo + CLI skeleton (`init`, `character`)
- [x] Pydantic config; checkpoint/LoRA are YAML fields
- [x] ComfyUI generator + Ren'Py formatter + filesystem deployer
- [x] Mock ComfyUI e2e + unit tests
- [x] Preflight, loud failures, no-deploy-on-zero, idempotent `.rpy`
- [x] Dev env (venv, `pip install -e .`); LoRA base confirmed SD1.5
- [x] First real-GPU run (Mac MPS); Ren'Py SDK lint of generated `.rpy`
- [x] Consistency prompts + shared seed + black-image guard + `output_dir`
- [x] img2img chaining code — **default off** (MPS glitch)
- [x] Stop using live LOVE32 as dogfood; sandbox project only
- [x] txt2img-only 4-pose sandbox re-run (LoRA clip=0; no half-static)
- [x] Eyeball / play-test in `sandbox-renpy/` (Ren'Py launcher)
- [x] IP-Adapter workflow + preflight (default off; MPS corrupts)
- [x] Consistency path decision: **accept prompt+seed on MPS**; CUDA IPA / VNCCS optional later
- [!] `small_hours_style_v1` NaNs on MPS — interim `last.safetensors` @ 0.7

**Branding / identity (deferred — Phase 1 closed with minimal brand)**

- [x] No dedicated brand system this phase — CLI name `matcha` + README title only
- [x] Visual identity / wordmark / marketing polish deferred to Phase 2 announce prep

---

## Phase 2 — Free release (Months 2–3)

**Goal:** A stranger can install, generate, and deploy without us sitting next
to them.

**Exit:** stranger walkthrough succeeds once; announce posts go out; known
Mac/MPS limits are written in README (not hidden).

**Out of scope:** Pro installer, Gumroad listing, hosted API.

**Must (in this order)**

1. [x] Cropped portrait side images (not full-sprite reuse) — STRATEGY §4.3
2. [x] Example / sample Ren'Py project strangers can clone — `examples/sample-vn/`
3. [x] Per-model license surfacing (§4.6) — `matcha/licenses.py`, `matcha licenses`, echoed on `character`
4. [x] Disclosure helper: Steam AI survey + itch.io tag reminder (§4.7) — `matcha/disclosure.py`, `matcha disclose`
5. [x] Install/README cold-start for outsiders (venv + ComfyUI + Mac MPS limits + sample-vn recipe + licenses/disclose) — cold clone re-walk 2026-08-05; ComfyUI+models onboarding section expanded 2026-08-06; quiet **v0.1.0** tag (no forum announce)
6. [~] Announce: Lemma Soft, Ren'Py Discord, r/comfyui, Civitai — **not** artist-heavy general VN forums
   (prep: [`docs/ANNOUNCE.md`](docs/ANNOUNCE.md); posts not live yet — hold; v0.1.0 is tag-only)

**Branding / marketing / design (same phase — not a 5th phase)**

- [x] Product name consistency everywhere (**Matcha Engine** / `matcha` — STRATEGY leftovers fixed)
- [x] README voice: clear, honest (Mac MPS limits), outsider-friendly tone
- [ ] Wordmark / simple logo if announce posts need one (skip if text-only is enough)
- [ ] Announce screenshots + short GIF (config → sprites → Ren'Py) — shot list in `docs/ANNOUNCE.md`; sprites generated locally 2026-08-05, human capture still pending
- [x] Announce copy drafts for Lemma Soft, Ren'Py Discord, r/comfyui, Civitai — `docs/ANNOUNCE.md`

**Already shipped toward Phase 2**

- [x] `--layered` / `--side-image` / display name + color
- [x] Documented sandbox play-test recipe (README)
- [x] Cropped portrait side images (`<name>_<pose>_side.png`, `side_image_height_ratio`)
- [x] Checked-in example Ren'Py project (`examples/sample-vn/`) + README recipe
- [x] Per-model license surfacing + Steam/itch disclosure helpers (`licenses` / `disclose`)
- [x] Outsider README cold-start (install → ComfyUI/Mac MPS → sample-vn → licenses/disclose) — cold `/tmp` clone walkthrough 2026-08-05; ComfyUI+models onboarding + quiet v0.1.0 tag 2026-08-06; forum announce still held

**Stretch (not an exit gate)**

- [ ] CUDA IP-Adapter retest when a GPU is available
- [ ] Document “Mac = prompt+seed only” next to any CUDA-improved path

---

## Phase 3 — First dollar (Months 3–4)

**Goal:** Money changes hands once.

**Exit:** ≥1 paid sale (prefer actual sale over listing-only).

**Out of scope:** auth/billing for cloud credits; marketing site/landing.

- [ ] Pro package (installer, presets, one-command deploy) ~$19–29
- [ ] List on itch.io + Gumroad
- [ ] Free VN-style LoRA(s) on Civitai (acquisition loop)

**Branding / marketing / design**

- [ ] itch.io + Gumroad listing visuals (cover, gallery, short trailer/GIF)
- [ ] Package naming clarity (Free CLI vs Pro pack)
- [ ] Civitai LoRA card branding (“made for Matcha Engine”)
- [ ] Pricing clarity on listings (~$19–29 one-time; what’s in Free vs Pro)

---

## Phase 4 — Hosted, conditional (Month 6+)

**Goal:** Cloud generate only if the Pro business earned it.

**Gate:** ≥ ~100 Pro sales. If the gate never hits: stay offline CLI + Pro.

- [ ] Serverless inference (Replicate / fal)
- [ ] Auth + billing + abuse handling

**Branding / marketing / design**

- [ ] Marketing site / landing **only if** the ≥~100 Pro sales gate hits (do not build earlier)

---

## Open verification items (STRATEGY.md §8)

- [x] `small_hours_style_v1` base — **SD1.5** (use `anythingV5PrtRE`, not SDXL)
- [ ] VNCCS traction (conflicting star counts)
- [ ] Re-verify Lemma Soft commission price ranges before public quoting
- [ ] "No one else does Ren'Py deploy" — searched, not exhaustively proven
