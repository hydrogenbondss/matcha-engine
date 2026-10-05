# Matcha Media Replica 01 — Higgsfield Workflow Recon

**Branch:** `matcha-2-media-replica-01`  
**Date:** 2026-10-05  
**Mode:** Reconnaissance + architecture mapping only — **no implementation**  
**Replica skill:** `replica-recon` (clean-room; public/account-observable behavior only)  
**Does not touch:** `matcha-2-experiment-02`, impact-engine experiment artifacts, H/M methodology

**Evidence confidence legend:** VERIFIED (observed) · LIKELY · UNPROVEN · SPECULATIVE

---

## 1. Scope

| In scope | Out of scope |
|----------|--------------|
| One Higgsfield core loop: **reference image → image gen/edit → image-to-video → review/export** | Cloning entire Higgsfield product |
| Mapping that loop onto Matcha | Building UI / billing / auth / video backends |
| Honest cost-structure identification | Fabricated pricing apples-to-apples totals |
| Clean-room product patterns | Copying Higgsfield source, private APIs, branding, credentials |

**Not declaring:** Matcha is now a general AI creative platform. This is an **experimental extension probe**.

### How evidence was gathered

| Source | Used? | Notes |
|--------|-------|-------|
| User Higgsfield MCP account (generation history, model catalog, cost preflight, plans widget) | Yes | VERIFIED account-observable |
| Public marketing / apps pages (`higgsfield.ai`, `/apps`) | Yes | Feature surface, not full studio click path |
| Higgsfield MCP tool schemas (`generate_image`, `generate_video`, `media_upload_widget`, `job_status`, `models_explore`) | Yes | Workflow contract as exposed to agents |
| Full interactive web Studio click-through in browser this session | **No** | Gap — see Open questions |
| Private JS bundles / hidden endpoints | **No** (forbidden) |

---

## 2. Target workflow

```text
REFERENCE IMAGE
   → IMAGE INTENT (prompt + model + aspect/quality)
   → IMAGE GENERATION / EDIT
   → IMAGE REVIEW (accept / retry / variant)
   → VIDEO INTENT (motion prompt + duration + aspect + model)
   → IMAGE-TO-VIDEO (prior image job OR uploaded still as start/reference)
   → VIDEO REVIEW
   → EXPORT / DOWNLOAD
```

This matches both (a) the requested slice and (b) **patterns in the user’s own recent Higgsfield history** (image jobs such as `nano_banana_2` / removers followed by `seedance_*` / `kling*` videos; durable `job` UUIDs + CDN URLs). **VERIFIED** via `show_generations`.

---

## 3. Observed user flow

Happy path (product-system reconstruction from MCP + history; web Studio may add UI chrome):

1. Enter generator (Studio / MCP / Apps surface).
2. Supply reference image → upload → receive `media_id` (**VERIFIED** contract: `media_upload` / `media_upload_widget`).
3. Describe intended still (prompt).
4. Select image model + aspect ratio + quality/resolution/variant (**VERIFIED** on `gpt_image_2_5`: quality, resolution, variant, aspect_ratios; medias role `image_references`).
5. Generate image → async job → poll until `completed` / failure (**VERIFIED**: `job_status`, typical image ~10–20s).
6. Review still (URL / widget). Accept, retry, or generate variants (`count` 1–4 same settings — **VERIFIED** schema).
7. Chain into video: pass prior `job_id` or `media_id` as video media role (e.g. `start_image` / `image_references` — **VERIFIED** on `seedance_2_5`, `grok_video_v15`, etc.).
8. Specify motion/camera intent via prompt; set duration, resolution, aspect, optional audio (**VERIFIED** model parameters).
9. Generate video → async job (~60–180s typical — **VERIFIED** `job_status` docs).
10. Review video URL.
11. Retry / regenerate / vary (new job; history retains prior IDs — **VERIFIED** history list).
12. Export: download CDN asset URL (mp4/png) — **VERIFIED** in history payloads.

**Edge observed in schemas (not exercised this run):** credit exhaustion → plan/top-up widget; `use_unlim` choice; transport timeout with unknown submission outcome (must not blindly resubmit).

---

## 4. Inputs

| Input | Required? | Effect (observed) | Useful vs fluff |
|-------|-----------|-------------------|-----------------|
| Reference / start image (`media_id` or prior `job_id`) | Required for true ref→edit / I2V | Conditions identity / start frame | **Essential** |
| Prompt (image) | Strongly expected | Edit/generation intent | **Essential** |
| Prompt (video / motion) | Strongly expected for non-preset I2V | Camera/motion language | **Essential** |
| Image model id | Required | Quality/capability stack | **Essential** |
| Video model id | Required | Motion quality / duration limits | **Essential** |
| Aspect ratio | Optional (defaults exist) | Framing | **Essential** |
| Duration (video) | Optional (clamped to model range) | Clip length | **Essential** |
| Resolution / quality | Optional | Cost + fidelity | **Useful** |
| `count` / batch variants | Optional | Parallel variants same recipe | **Useful** |
| `generate_audio` | Optional (model-dependent) | Audio track | **Useful** for some; fluff for silent VN tests |
| Presets / Apps one-clicks | Optional | Packaged effects | **Nice-to-have** for replacement wedge; fluff for Matcha MVP |
| Folders / projects | Optional | Organization | **Useful** for history; not MVP |
| Negative prompt | **Not observed** as first-class on default GPT Image / Seedance MCP params | — | Do not invent |
| Explicit “image strength” slider | **Not observed** in MCP params for these models | May exist in web UI | **UNPROVEN** |
| Seed | **Not observed** in these MCP schemas | — | **UNPROVEN** |

---

## 5. Outputs

| Artifact | Format (observed) | Persistence |
|----------|-------------------|-------------|
| Image job | PNG URL on CDN | Job UUID + `createdAt` + model id + status |
| Video job | MP4 URL on CDN | Same |
| Intermediate utility jobs | e.g. background remover image/video | Same history stream |

**Chaining:** Prior generation `job_id` is a valid media value for later steps (**VERIFIED** tool docs).  
**Dimensions:** Driven by aspect_ratio + resolution class; exact pixels not fully enumerated here.

---

## 6. States

| State | Evidence |
|-------|----------|
| idle | Before submit |
| uploading | `media_upload_widget` / upload confirm |
| queued / processing / generating | Non-terminal `job_status`; poll interval |
| completed / success | History `status=completed` + URL |
| failure | Schema implies terminal fail; exact UI copy **UNPROVEN** this session |
| retry | New generation call; old job retained |
| credit / plan gate | `show_plans_and_credits`, `get_cost` preflight |
| timeout ambiguity | Explicit: do not auto-resubmit |

---

## 7. Failure behavior

Observed / documented contracts:

- **Preflight cost** (`get_cost: true`) returns credits **without** submitting — **VERIFIED** (image 0.5 cr for probed `gpt_image_2_5` settings; video 35 cr for probed `seedance_2_5` 5s/720p).
- **Out of credits / plan** → billing widget path (subscription + credit packs).
- **Async failure** → job terminal non-completed (exact error strings not captured this session).
- **Transport timeout** → submission outcome may be unknown; reuse job IDs; do not double-charge blindly.

---

## 8. Product patterns (classification)

| Pattern | Class |
|---------|-------|
| Reference media → conditioned generation | **essential** |
| Still → video chaining via job/media IDs | **essential** |
| Async jobs + poll + durable history | **essential** |
| Cost preflight before spend | **essential** (for replacement economics) |
| Model catalog with roles/params | **essential** |
| Aspect + duration + resolution knobs | **useful** |
| Multi-variant `count` | **useful** |
| Folder/project organization | **useful** |
| One-click viral Apps / presets | **nice-to-have** (not needed to cancel for *this* workflow) |
| Social/community/festival surfaces | **probably fluff** for Matcha wedge |
| Genjutsu / Recast / full VFX suite | **out of scope** for this experiment |

---

## 9. Model capability vs product orchestration

### MODEL CAPABILITY (hard / expensive)

- High-quality reference-conditioned **image edit**
- High-quality **image-to-video** with controllable motion
- Optional audio, multi-ref, motion transfer (Genjutsu) — beyond MVP

These are **not** Matcha’s current ComfyUI SD1.5 strengths (prior Matcha experiments: controlled identity already unproven on Intel Mac).

### PRODUCT ORCHESTRATION (Matcha-shaped)

- Recipe objects (inputs + model + params)
- Job state machine
- Provenance (what media + model + prompt + seed/params produced what)
- Retry / variant loops
- Asset chaining (image artifact → video request)
- Local CLI/UI review
- Export paths
- Human evaluation gates (Matcha already has this for sprites)

**Critical split:** Higgsfield subscription buys **model access + orchestration UX**. Matcha can own orchestration; it still needs **someone’s GPU/API** for model capability.

---

## 10. Matcha architecture mapping

### Repo reality (this branch base)

`matcha-2-media-replica-01` was created from `matcha-2-impact-engine-v1-hardening` (`e47283b`).

| Area | On this branch | Elsewhere (do not mix casually) |
|------|----------------|----------------------------------|
| CLI `matcha character` + ComfyUI SD1.5/VNCCS | Yes | — |
| `matcha impact` + strict provenance | Yes | — |
| Experiment 1/2 H/M evidence machinery | Sibling worktrees | **Do not modify** |
| `GenerationBackend` / CharacterSpec / Candidate / ApprovedAsset / ECHO export | Present on dirty **main** workspace (Phases 1–5) — **not** on this impact-engine tip | Reuse as *concept*; merge decision later |

### Mapping table

| Higgsfield concept | Matcha equivalent | Reuse existing? | New abstraction? |
|--------------------|-------------------|-----------------|------------------|
| Reference image | Canonical / input media path; (Phase 1–5) `CanonicalReference` | Partial | MediaAsset id |
| Image recipe | YAML / GenerationRequest-like | Partial (prompt+checkpoint today) | MediaRecipe (model, params, refs) |
| Image generation | `ComfyUIGenerator` / backends | Partial (still/sprites) | Pluggable **ImageBackend** (API or Comfy) |
| Video recipe | None | No | VideoRecipe |
| Image → video | None | No | VideoBackend + chain from ImageArtifact |
| Output artifact | PNG under output/; Candidate | Partial | MediaArtifact (image\|video) |
| Generation provenance | Impact provenance; Phase 1–5 Provenance | Yes (pattern) | Extend for video + remote job ids |
| Retry | Seed stride / quality retries | Partial | Job retry policy |
| History | Filesystem / `.matcha` store | Partial | JobHistory index |
| Human eval | Candidate evaluate (main Phases) | Yes for stills | Optional for video later |
| ECHO / Ren'Py deploy | FilesystemDeployer | Keep for game path | **Do not force** media wedge through Ren'Py |

### Assumptions that hard-code Ren'Py/game assets

- Character YAML poses → sprite filenames  
- Deploy into `game/images` + optional `.rpy`  
- Impact engine scans Ren'Py graphs  

**Media replica must not require Ren'Py.** Keep game path intact; add a **parallel media experiment surface**.

---

## 11. What can be reproduced (ourselves)

- Workflow stages and recipe schemas  
- Job state + polling adapter to *any* provider  
- Provenance (media hashes, model id, params, job ids, costs)  
- Retry / variant orchestration  
- Image→video chaining  
- Local review + export folders  
- Cost logging for apples-to-apples later  
- Optional thin CLI: `matcha media image` / `matcha media video` (**proposal only**)

---

## 12. What cannot (or should not) be reproduced now

| Item | Why |
|------|-----|
| Higgsfield’s proprietary model quality | Requires their (or peers’) paid inference |
| Viral Apps marketplace / community | Network + content; not the wedge |
| Guaranteed local I2V at Seedance-class quality | Compute + model gap; **SPECULATIVE** if claimed free |
| “Cancel Higgsfield tomorrow” | Orchestration alone ≠ model quality |
| Cloning UI branding / private APIs | Forbidden / useless |

---

## 13. Cost / replacement implications

**Question:** Could I cancel Higgsfield and use Matcha instead?

### Structure to compare later (do not fabricate totals)

| Cost bucket | Higgsfield today | Matcha path |
|-------------|------------------|-------------|
| Subscription | Plus ~$49/mo or annual deals; Ultra higher; credit packs | $0 for Matcha software |
| Per-generation credits | **VERIFIED probes:** ~0.5 cr image (`gpt_image_2_5` medium/1k); ~35 cr I2V (`seedance_2_5` 5s/720p) | Same if calling HF/API; or GPU rental $ if self-host |
| Local compute | N/A (they host) | Electricity + optional GPU cloud |
| Engineering time | $0 | Matcha build + maintain adapters |
| Quality risk | Known good for user’s history | Local/open stacks may fail Matcha-grade identity (prior evidence) |

**Honest interim answer:** Matcha can replace the **orchestration** of this workflow. Replacing the **subscription** requires either (1) continued paid APIs (possibly multi-provider) wired through Matcha, or (2) local/open models that pass a later quality experiment. Without (1) or (2), answer is **NO**.

---

## 14. Proposed smallest Matcha prototype (DO NOT BUILD YET)

**Name:** Media Chain Spike (docs-only proposal)

```text
MediaRecipe(image)
  → ImageBackend.generate() → ImageArtifact + Provenance
  → human glance / accept
MediaRecipe(video)  [input = ImageArtifact]
  → VideoBackend.generate() → VideoArtifact + Provenance
  → export folder
```

Constraints:

- One CLI or script under `experiments/media-replica-01/` (isolated)  
- One remote provider adapter **or** stub with recorded fixtures  
- No accounts, billing, teams, dashboards  
- No Ren'Py deploy  
- No claim of Higgsfield parity  

Success metric for a *future* build phase: reproduce **user’s own** ref→still→5s clip loop with provenance + cost log — quality scored honestly.

---

## 15. Open questions

1. Exact web Studio controls for “reference strength” / seed — not in MCP schemas; need one supervised UI session.  
2. Which models the user considers **non-negotiable** for canceling (Seedance vs Kling vs Nano Banana, etc.).  
3. Whether video is required for Love32/ECHO or only for general creative work (scope of “replace subscription”).  
4. Whether Phase 1–5 `GenerationBackend` on dirty main should be merged before any media spike.  
5. Acceptable monthly API budget vs current Higgsfield plan.  
6. Failure UX details (partial renders, content policy blocks) — need live fail probes later.

---

## Phase 1 — Matcha repo audit summary

### Reuse

- ComfyUI HTTP/WS client patterns  
- Impact provenance discipline (no guessed facts)  
- Experiment isolation culture (sibling worktrees)  
- Phase 1–5 backend protocol *concept* (on main)

### Leave untouched

- Experiment 02 H/M outputs and methodology  
- Impact engine contracts unless a later task says otherwise  
- ECHO/Love32 deploy safety rules  

### Needs new abstraction

- `MediaArtifact` / video recipes / provider job IDs  
- Non-Ren'Py export root  

### Hard-coded Ren'Py assumptions

- Pose lists, filename templates, `game/images`, impact Ren'Py scan  

---

## CAN MATCHA REPLACE THIS WORKFLOW?

### **PARTIALLY**

| | |
|--|--|
| Orchestration (flow, recipes, jobs, provenance, chaining, export) | **YES — Matcha-shaped** |
| Model quality for user’s observed Higgsfield still→video path | **NO without paid APIs or a proven local I2V stack** |
| Cancel subscription today via Matcha alone | **NO** |

---

## Next experiment recommendation (awaiting your review)

**Do not implement yet.** If you approve:

1. Supervised Studio UI pass to close control gaps (strength/seed).  
2. Freeze a **personal golden path** (one ref, one still model, one I2V model, one duration).  
3. Then a **harness-only** spike that calls **one** paid API through Matcha recipes and logs cost + provenance — still no product UI.
