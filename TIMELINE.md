# Matcha Engine — Timeline & Progress Tracker

A living checklist so we can see, at a glance, whether we're on track. Detailed
positioning lives in [STRATEGY.md](STRATEGY.md); engineering notes in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md). This file is the "are we on track" view
of STRATEGY.md §6.

Status legend: `[x]` done · `[~]` in progress · `[ ]` not started · `[!]` blocked

_Last updated: 2026-08-23 (VNCCS same-face = Character Cloner from a
sandbox `reference:`; Creator is fallback; MPS fail-preflight; Echo disk
spec unchanged; public outreach still deferred)_

2026-11-14: Three-stage audit committed (docs/AUDIT-2026-11-14.md) —
self-recon, competitor recon + review mining, north-star gap map.
Phase 3 scope unchanged; audit feeds listing copy + Pro packaging only.

2026-11-14: Phase 3 sequenced — Pro package specced (installer / PyPI /
setup / presets / run wrapper), price locked at listing day, open-core
convenience gating confirmed in STRATEGY §5, 4-point launch-readiness
gate defined.

2026-11-14: STRATEGY §4 Later — GUI wrapper + Matcha MCP server explicitly
parked post-first-dollar (Phase 3 scope unchanged).

2026-11-14: Pro packaging CI green — test + macOS-arm64 +
Windows-x64-beta all pass; PyInstaller binaries build in CI;
ANSI-fragile --help assertion fixed (strip styling before asserting).
First Phase 3 engineering task done.

2026-11-15: `matcha setup` guided first-run checklist (reachability /
model inventory / placement table / trusted-first-success sequence),
3 starter presets (presets/), verified model checklist
(docs/verified-models.md). Phase 3 Pro contents landing.

2026-11-15: `matcha run <yaml>` one-command path — health-check gate →
delegates to the character flow (no reimplemented logic); --project =
deploy, omitted = generate only; --lora / --layered / --side-image
passthroughs. Pro `run` wrapper done.

---

## Phase map (4 phases)

Keep **four** phases — do not invent a fifth for consistency. CUDA IP-Adapter /
VNCCS stay optional levers inside Phase 2/3, not a gate that stalls forever on
Mac MPS.

| # | Phase | Goal | Exit criteria |
|---|--------|------|----------------|
| **1** | Pipeline demo | Config → sprites → Ren'Py deploy works on a real GPU *for you* | 4 usable poses in **sandbox**; play-tested; consistency path decided |
| **2** | Free release | A stranger can install, generate, and deploy without us | Example project; cropped side images; license/disclosure helpers; README limits honest; trustworthy cold-run path |
| **3** | First dollar | Money changes hands | Pro pack on itch/Gumroad; ≥1 paid sale; acquisition LoRA(s) |
| **4** | Hosted (conditional) | Cloud generate | Only if ≥~100 Pro sales — Replicate/fal + auth/billing |

```
Phase1 → Phase2 → Phase3 ──(if ~100 Pro sales)──► Phase4
```

**You are here:** **Phase 2 — Free release** (wedge deepen: reliability +
time-to-wow). Phase 1 is closed (2026-07-27). Public outreach stays deferred
indefinitely — not the current goal. Do **not** deploy into live LOVE32 while
that game is being polished — use `examples/sample-vn/` (checked in) or
gitignored `sandbox-renpy/`.

---

## Where we are right now

- **North star:** documented in [STRATEGY.md](STRATEGY.md) §1 (wedge-first
  AI-native creation; not a full engine) — 2026-08-06.
- **Current focus:** deepen the wedge — reliable first generate (especially
  Mac MPS) via `--lora none` / `lora: null`, clearer failure modes, trusted
  first-success recipe in README. Public outreach is deferred indefinitely.
- **Current phase:** Phase 2 — Free release.
- **Shipped (Phase 1):** v0.2 pipeline on live ComfyUI (Mac MPS); preflight;
  black-PNG guard; shared seed + locked prompts; LoRA `strength_clip=0`;
  layered/side-image scaffolding; sandbox dogfood; IP-Adapter path (default off).
- **Shipped (Phase 2 preview):** quiet **v0.1.0** tag (2026-08-06) — free CLI
  preview; README ComfyUI + models onboarding (install, paths, name match /
  `--checkpoint` / `--lora none`, `curl` health-check cliff, Mac MPS limits,
  Placeholders without generation).
- **Shipped (wedge deepen 2026-08-06):** sample/init YAML default `lora: null`;
  CLI tip + dry-run next-step when a LoRA is set; louder MPS warnings for
  img2img/IPA; clearer ComfyUI-down / black-PNG / WebSocket errors; README
  **Trusted first success** recipe (health-check → dry-run → `--lora none` →
  sample-vn).
- **Reliability smoke (2026-08-08, Mac MPS):** **3 consecutive**
  `--lora none` character runs (4/4 poses each), PNGs not near-black;
  ~15–16 min/run. ComfyUI can still die mid-job if the process is torn down —
  keep the server in a durable Terminal session for long batches.
- **Earlier walkthrough (2026-08-05):** fresh `/tmp` clone → venv install →
  start ComfyUI (Mac MPS flags) → dry-run → generate+deploy 4/4 poses → Ren'Py
  lint OK; `licenses` / `disclose` OK.
- **Mac / MPS limits (document in README, do not hide):** img2img and
  IP-Adapter corrupt — leave off locally (`consistency_denoise: 1.0`,
  `ip_adapter_weight: 0`). prompt+seed is **not** a same-face lock;
  `--backend vnccs` + Character Cloner from a sandbox `reference:` is
  (after installing VNCCS + Utils on CUDA). Text-only Character Creator
  is fallback. Apple Silicon MPS fails VNCCS preflight (GGUF / Impact /
  SAM). CUDA IPA is
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
   quiet v0.1.0 tag 2026-08-06; remaining gaps are obtaining ComfyUI/GPU +
   checkpoint, not Matcha install)
5. ~~Trusted first-success path (`--lora none` / `lora: null`, failure-mode
   clarity, README recipe).~~ **done** 2026-08-06
6. ~~Local 3× consecutive `--lora none` reliability smoke (Mac MPS).~~ **done**
   2026-08-08 (~15–16 min/run; 4 usable poses × 3)
7. Public outreach — **deferred indefinitely** (not the goal; prep may exist
   in-repo but do not treat as active work)

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

**Exit:** stranger walkthrough succeeds once (trusted first success:
health-check → dry-run → `--lora none` → sample-vn); known Mac/MPS limits are
written in README (not hidden). Public outreach is deferred indefinitely —
not an exit criterion.

**Out of scope:** Pro installer, Gumroad listing, hosted API.

**Must (in this order)**

1. [x] Cropped portrait side images (not full-sprite reuse) — STRATEGY §4.3
2. [x] Example / sample Ren'Py project strangers can clone — `examples/sample-vn/`
3. [x] Per-model license surfacing (§4.6) — `matcha/licenses.py`, `matcha licenses`, echoed on `character`
4. [x] Disclosure helper: Steam AI survey + itch.io tag reminder (§4.7) — `matcha/disclosure.py`, `matcha disclose`
5. [x] Install/README cold-start for outsiders (venv + ComfyUI + Mac MPS limits + sample-vn recipe + licenses/disclose) — cold clone re-walk 2026-08-05; ComfyUI+models onboarding section expanded 2026-08-06; quiet **v0.1.0** tag
6. [x] Trusted first-success path — `lora: null` / `--lora none` defaults + tips; clearer ComfyUI-down / black-PNG / WS errors; README recipe (2026-08-06)
7. [ ] Public outreach — **deferred indefinitely** (not the goal)

**Branding / marketing / design (same phase — not a 5th phase)**

- [x] Product name consistency everywhere (**Matcha Engine** / `matcha` — STRATEGY leftovers fixed)
- [x] README voice: clear, honest (Mac MPS limits), outsider-friendly tone; trusted first-success recipe
- [ ] Wordmark / simple logo if needed later (skip if text-only is enough)
- [ ] Optional screenshots / GIF for docs (not a gate)

**Already shipped toward Phase 2**

- [x] `--layered` / `--side-image` / display name + color
- [x] Documented sandbox play-test recipe (README)
- [x] Cropped portrait side images (`<name>_<pose>_side.png`, `side_image_height_ratio`)
- [x] Checked-in example Ren'Py project (`examples/sample-vn/`) + README recipe
- [x] Per-model license surfacing + Steam/itch disclosure helpers (`licenses` / `disclose`)
- [x] Outsider README cold-start (install → ComfyUI/Mac MPS → sample-vn → licenses/disclose) — cold `/tmp` clone walkthrough 2026-08-05; ComfyUI+models onboarding + quiet v0.1.0 tag 2026-08-06
- [x] Wedge deepen: `--lora none` first-success path + failure-mode clarity (2026-08-06)
- [x] Wedge deepen (2026-08-23): smear/static-band quality guard + reject dump;
  seed retry; look-sheet `pose_overrides`; `--poses` + incremental writes +
  resume; `--copy-only` filename template (no Character/layeredimage); LOVE32
  path refused. rembg knockout skipped (grey-card mattes). IPA/img2img still off.

**Stretch (not an exit gate)**

- [x] VNCCS wrap (`--backend vnccs`) — same-face lock is Character Cloner
      from YAML/CLI `reference:` (sandbox copy of an approved sprite; LOVE32
      paths refused). Character Creator from text is fallback. Preflight
      real nodes; no silent prompt+seed fallback. MPS fails clearly
      (GGUF / Impact / SAM). IPA / `consistency_denoise < 1.0` stay off
      on MPS. 2026-08-23
- [ ] CUDA IP-Adapter retest when a GPU is available
- [ ] Document “Mac = prompt+seed only” next to any CUDA-improved path

---

## Phase 3 — First dollar (Months 3–4)

**Goal:** Money changes hands once.

**Exit:** ≥1 paid sale (prefer actual sale over listing-only).

**Out of scope:** auth/billing for cloud credits; marketing site/landing.

**Pro package spec + pricing sequencing (decided 2026-11-14):**

- **Pricing sequencing:** build Pro first; final price locked on listing
  day. The ~$19–29 band is locked NOW as a scoping input only, not a price
  commitment. Phase 3 exit criterion unchanged: ≥1 paid sale.
- **Pro package contents:**
  - PyInstaller standalone binary — Mac arm64 first (verifiable); Windows
    x64 via GitHub Actions CI, honestly labelled beta (CI smoke-tested, not
    verified on real hardware)
  - PyPI release (`pip install matcha-engine`) + pyproject license /
    classifiers cleanup
  - `matcha setup` guided first-run checklist (ComfyUI reachability, model
    placement, health-check → dry-run). NO bundled model weights — Fair AI
    PL covers outputs, not weight redistribution. Ship a verified model
    checklist instead.
  - Preset library: 3 character YAMLs (distinct archetypes, look-sheet
    outfit families done properly) + verified model checklist + one worked
    sample-vn example
  - `matcha run <yaml>`: health-check → preflight → generate → deploy as
    one command (thin wrapper over existing commands; no new generation
    logic)
- **Free tier keeps every feature it has today; Pro sells convenience,
  never capability.**

**Launch-readiness gate (decided 2026-11-14):** ALL FOUR must pass before
any listing goes live. This is the definition of "excellent" for this
phase — anything beyond it is the polish trap and parks post-first-dollar:

- [ ] Pro binary cold-installs on a fresh machine (no dev environment) and
  reaches trusted first success unaided
- [ ] All 3 presets run end-to-end against examples/sample-vn without
  needing to re-read the README
- [ ] Every known failure mode (ComfyUI down, wrong model name, Mac MPS
  corruption) produces a clear error — never a silent one
- [ ] Honest-limits docs ship in the box: platform support (Mac verified,
  Windows beta) stated plainly in listing + README

- [ ] Pro package (installer, presets, one-command deploy) ~$19–29
- [ ] List on itch.io + Gumroad
- [ ] Free VN-style LoRA(s) (acquisition loop)

**Branding / marketing / design**

- [ ] itch.io + Gumroad listing visuals (cover, gallery, short trailer/GIF)
- [ ] Package naming clarity (Free CLI vs Pro pack)
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
- [x] VNCCS traction — resolved high 2026-11-14 (1,765★, 115 forks,
  last push 2026-11-12)
- [ ] Re-verify Lemma Soft commission price ranges before public quoting
- [ ] "No one else does Ren'Py deploy" — searched, not exhaustively proven
