# Matcha 2.0 Reset

Planning note only. Written 2026-09-28 from the tree at `main` (`65bb0f5`, tag `v0.1.0` plus five commits) and from public sources fetched the same day. This document does not choose a product, declare a moat, or authorize implementation.

Evidence tags used below:

- **PROVEN** — observed in this repository, or stated on a primary page we fetched (vendor claims are tagged as vendor claims).
- **INFERRED** — a conclusion drawn from those observations. It can be wrong.
- **UNPROVEN** — plausible, searched, or locally claimed, but not demonstrated by an artifact we can point at.

---

## 1. Current Matcha 1.0

Matcha 1.0, as implemented on `main`, is a single-user Python CLI (`matcha`, package version `0.1.0`) of about 3,600 lines under `matcha/`. It turns one character YAML file into a batch of PNGs by talking to a ComfyUI server the user already runs, then optionally copies those PNGs into a Ren'Py tree and writes a generated `game/matcha_characters.rpy` block. Tests are mocked: 105 test functions across `tests/test_pipeline.py` (43), `tests/test_quality_looksheet.py` (24), `tests/test_vnccs.py` (24), and `tests/test_licenses.py` (14). Nothing in CI generates an image.

There is no UI, no database, no account, no network service of Matcha's own, and no second generation provider. `MatchaConfig` in `matcha/config.py` reserves `comfyui` and `project` fields and is never referenced. Public outreach is explicitly deferred in `TIMELINE.md`. This repo contains no user counts, no sales, and no generated sprites (PNGs under `examples/sample-vn/game/images/characters/` are gitignored; `refs/*.png` is gitignored).

### What the code actually does

| Command | Behavior in code |
|---|---|
| `matcha init <name>` | Creates `<name>/configs/example_character.yaml`. Does not create a Ren'Py game. |
| `matcha character <yaml>` | Loads one `CharacterConfig`, preflights ComfyUI, generates the selected poses, writes accepted PNGs under `output_dir` as each one passes. |
| `matcha character --dry-run` | Config parse plus ComfyUI `/object_info` (and VNCCS node checks if that backend is selected). No GPU work. |
| `matcha character --deploy --project <dir>` | Copies images under `game/images/characters/` by default and replaces that character's block in `game/matcha_characters.rpy`. Refuses any path whose components look like `LOVE32`. Warns if the path does not contain `sample-vn` or `sandbox`. |
| `matcha character --copy-only` | Copies PNGs only. Does not write `Character`, `layeredimage`, or `_kite_sprite`. |
| `matcha licenses` | Prints a built-in commercial-use note. The catalog matches two families: Anything V5 (treated as commercially usable) and NoobAI (treated as restricted). Everything else is "unknown." The module says it is not legal advice. |
| `matcha disclose` | Drafts Steam AI Content Survey text and an itch.io AI-tag reminder, to stdout or `matcha_disclosure.md`. Also not legal advice. |

Generation has two backends, selected with `--backend`:

1. **`txt2img` (the default).** Builds a ComfyUI graph: `CheckpointLoaderSimple`, optional `LoraLoader` with `strength_clip` forced to `0.0`, `KSampler`, `VAEDecode`, `SaveImage`. Optional branches, both off by default and warned against on Mac MPS: img2img when `consistency_denoise < 1.0`, and IP-Adapter when `ip_adapter_weight > 0`. The CLI prints that prompt plus a shared seed is not a same-face lock.
2. **`vnccs` (opt-in).** Queues node types copied from upstream VNCCS 3.0 (`CharacterCloner` plus `VNCCS_CharacterCloneGenerator` when a sandbox `reference:` PNG exists; otherwise `CharacterCreatorV2` plus `VNCCS_CharacterGenerator`). Can add the clothes graph if those nodes are installed and the pose has an outfit. Preflight fails on Apple Silicon MPS unless `--vnccs-allow-mps`. There is no silent fallback to txt2img. Headless pose plates are drawn with Pillow and stuffed into Pose Studio `pose_data` so the real node can emit images without a browser tab.

Surrounding machinery that is real:

- **Look sheet.** `description` is shared identity. `outfit_families` plus `pose_overrides` supply per-pose clothing. `pose_aliases` maps names that must not become files (`angry` → `stressed` in `configs/kite_male.yaml`). `matcha/prompts.py` has a fixed expression table for a handful of pose names; unknown names become the token with underscores turned into spaces.
- **Quality gate.** `matcha/images.py` rejects near-black frames and a measured smear / edge-static pattern, dumps PNG plus metrics JSON under `output_dir/rejected/`, and retries with a strided seed (`quality_retries`, default 2). This is luma and edge statistics. It does not compare a face to a reference.
- **Resume.** An accepted PNG already on disk is skipped unless `--force` or the file itself fails the quality gate.
- **Post-process.** Optional near-black knockout, canvas pad, max-dimension shrink, and a top-fraction crop for side portraits (`side_image_height_ratio`, default 0.45). The crop is geometric. It does not find a face.
- **Ren'Py text.** Flat `image char pose = "..."` by default. `--layered` emits a Ren'Py `layeredimage` whose attributes are whole sprites, not separate body / clothes / face layers. `--side-image` adds `image side ...` lines and `Character(image=...)`.
- **Preflight.** Checkpoint and LoRA names must appear in ComfyUI's `/object_info` lists. `validate_model_file()` (reject suspiciously small checkpoint byte sizes) exists and is unit-tested. It is not called from `matcha character`.

Checked-in subjects:

- **Sakura** (`configs/example_character.yaml`, `examples/sample-vn/`). Four poses, one school outfit repeated four times, Placeholder images in `game/matcha_characters.rpy`, a four-line pose lineup in `game/script.rpy`.
- **Kite** (`configs/kite_male.yaml`). Ten poses, three outfit families, one alias, a filename template with a space (`kite_male <pose>.png`), and a `reference:` path into gitignored `refs/`. Comments describe a live LOVE32 sprite (1200×992, apron/bar) and a display-only 1.39 scale on `crossed_arms` because that live file is a different pixel size. The CLI is written to refuse reading or writing that live tree.

### What the docs claim that the repo does not establish

| Claim | Where | Status |
|---|---|---|
| "The moat is orchestration + the last mile, not generation." | `STRATEGY.md` §1 | Positioning, not a measured result. **UNPROVEN** as a moat. The orchestration that exists is one character in, one ComfyUI server, one Ren'Py folder. |
| Config → consistent sprite matrix → deploy → generated engine code, and nobody else does that. | `STRATEGY.md` §3, still an open item in `TIMELINE.md` | The pipeline shape is **PROVEN** as code. "Nobody else" was labeled Likely in July 2026 and is still **UNPROVEN**. See §4. |
| Same-face lock is VNCCS Character Cloner from a sandbox reference. | README, `TIMELINE.md`, `matcha/vnccs.py` | The graph builder and the preflight rules are **PROVEN**. A successful clone that holds a face, on any GPU, is not an artifact in this repo. `TIMELINE.md` says the author's Mac fails VNCCS preflight and that VNCCS is not installed there. **UNPROVEN** as a production result. |
| prompt + shared seed is a consistency story. | Older announce copy in `docs/ANNOUNCE.md` (r/comfyui draft); README now contradicts this | README and the CLI are explicit that it is not a lock. The announce draft is stale. |
| "The current CLI reports success on total failure." | `STRATEGY.md` §4.5 | Stale. Zero images exits 1. Partial failure exits 2. No `.rpy` update when nothing was generated. **PROVEN** in `matcha/cli.py`. |
| Model file-size sanity check before queueing. | `STRATEGY.md` §4.4 | Function exists. The character command does not call it. |
| 4 usable poses play-tested; 3× `--lora none` smoke, ~15–16 min/run. | `TIMELINE.md` | Local notes from August 2026. Not reproduced by the test suite and not stored as images. Treat as author testimony, not as a checked-in result. |
| Phase 2 "a stranger can install, generate, and deploy without us." | `TIMELINE.md` | Install docs and a sample project with Placeholders are in the repo. Generation still requires that stranger's ComfyUI, GPU, and checkpoint. Outreach is deferred indefinitely, so the stranger path has not been observed. |
| Dogfood on LOVE32. | `AGENT_CONTEXT.md` | Contradicts the later refuse-LOVE32 policy in the CLI, README, and `TIMELINE.md`. The context file is stale. |
| North star: the creator describes intent and Matcha generates systems, scenes, assets, dialogue, and logic; a mystery game from a sentence. | `STRATEGY.md` §1 | Explicitly out of v0.1 scope. None of it is implemented. |
| Pro pack (~$19–29), Civitai LoRAs, hosted credits after ~100 sales. | `STRATEGY.md` §5, `TIMELINE.md` Phases 3–4 | Not built. |
| IP-Adapter and img2img as identity locks. | Config comments, generator code | Implemented and default-off, with warnings that they corrupt on the author's Mac MPS. Not the supported consistency path. |

`docs/ANNOUNCE.md` is an unsent launch checklist. Several drafts still describe Matcha as "thin CLI" / "orchestration + last mile" and one of them still calls prompt + seed the consistency story. Shots were captured locally on 2026-08-05 and are not in git.

Parallel branches (`cursor/setup-dev-environment-c8f9`, `cursor/vnccs-consistency-backend-8796`, `cursor/echo-quality-looksheet-5b89`) contain earlier commits of work that landed on `main` under different hashes (licenses, VNCCS wrap, quality guard, Kite look sheet). They are not a second product. `origin/local-mac` has no merge base with `main` and is an older snapshot. The description in this file is `main`.

---

## 2. Current Product Thesis

Read from `STRATEGY.md`, the README, and what the CLI is shaped to do, Matcha currently appears to be selling this:

> A zero-to-low-budget visual-novel developer who will not commission art can declare a character once, generate a pose × expression × outfit set on their own GPU, and have it dropped into Ren'Py with the right filenames and image statements.

The priced pain in the strategy doc is commission cost (Lemma Soft thread snippets, tagged there as Likely and still unverified) and the difficulty of keeping a face stable across many images. The proposed alternative to "a better generator" is: wrap VNCCS for consistency, and win on declarative config, reproducible batch runs, Ren'Py scaffolding, preflight, loud failure, and AI-disclosure drafts.

The commercial shape attached to that thesis is a free CLI, then a one-time Pro pack, then a hosted credit product only after about a hundred sales. That sequence is a plan in `TIMELINE.md`. It is not a business that has started.

A second, larger thesis sits above it and is easy to confuse with the product: an AI-native creation engine where making a game no longer starts from code. The same document says that is not the wedge and that building "an AI game engine" is the mistake to avoid. The code followed the wedge. The wedge is a character-sprite batch tool.

---

## 3. Why We Are Reconsidering It

The July 2026 thesis can be wrong even if the code does what it says. The reasons to reopen it are specific, and they should not be inflated.

**Image generation is more available than it was when the strategy was drafted.** Google's 26 February 2026 post on Nano Banana 2 (Gemini 3.1 Flash Image) describes subject consistency for up to five characters and fourteen objects inside one workflow, at multiple aspect ratios, through the Gemini app and, in preview, the Gemini API ([blog.google](https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/)). That is a vendor claim about a general image model, not a measured result on transparent visual-novel sprites. It is enough to show that "keep the same character across several pictures" is now a headline feature of a frontier model, not a niche ComfyUI trick. It is not enough to say frontier models have replaced a sprite pipeline.

**Character consistency products aimed at games already exist, including ones aimed at visual novels.** VNCCS (MIT, 1,615 GitHub stars on 2026-09-28) is a character production system: create or clone, pose, clothes, emotions, and a per-character folder with config JSON and version directories ([repo](https://github.com/AHEKOT/ComfyUI_VNCCS), [output folders](https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Output-Folders)). TavernSprite sells a 28-expression set from one portrait and tells Ren'Py users to drop the files in an images folder ([tavernsprite.com/for/visual-novels](https://tavernsprite.com/for/visual-novels/)). Scenario trains style and character models and ships an API, workflows, and a Unity plugin ([Scenario FAQ](https://help.scenario.com/articles/1129045411-frequently-asked-questions-faq)). Ludo markets engine-ready sprites and sprite sheets, including a Unity plugin and an MCP server ([ludo.ai](https://ludo.ai/)). Matcha wrapping one of these, or calling ComfyUI beside them, does not by itself create a product.

**ComfyUI orchestration plus a Ren'Py writer is a thin place to stand.** The README already calls Matcha "a thin CLI around your local ComfyUI." `sprite-forge-mcp` is a different codebase with the same shape: a Python process that does not run the model, calls ComfyUI, keeps a character record, and copies a result into a game folder only when asked ([README](https://github.com/kitepon-rgb/sprite-forge-mcp)). It has two stars. Traction is not the point. The point is that the architecture Matcha treats as the wedge is an obvious one, and a popular agent-skill variant of "plan, generate, clean, export sprites" already has thousands of stars (`agent-sprite-forge`, 4,215; `sprite-gen`, 2,077; both fetched 2026-09-28). Orchestration is not scarce.

**A wrapper around an image generator is a bad destination.** If the only thing a user notices is the PNG, they will use whichever generator is good enough and skip the wrapper. Matcha's own dogfood points the same way: for the one real character in the repo (Kite), `--deploy` is refused, and the recommended last mile is `--copy-only` or a hand copy. The generated `layeredimage` is not what the live game uses. The differentiator named in the strategy doc is the part the real project will not accept.

None of this proves the Ren'Py batch tool is useless to its author. It proves that "YAML → ComfyUI → `.rpy`" is a weak bet to keep funding as the product, and that consistency-by-orchestration is no longer a credible reason on its own.

---

## 4. Competitive Reality

Rows are not a ranking. "What Matcha currently solves" is the same narrow pipeline in every row: one YAML character, ComfyUI txt2img or a VNCCS graph, heuristic PNG checks, optional Ren'Py file copy and `matcha_characters.rpy`. Stars and prices move. Figures below are from the cited page on 2026-09-28 unless noted.

| Product | What it already solves | What Matcha currently solves that this product does not, as far as we can show | What appears different | Uncertain | Tag |
|---|---|---|---|---|---|
| **Nano Banana 2 / Gemini 3.1 Flash Image** ([Google, 26 Feb 2026](https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/)) | General image generation and editing. Vendor: subject consistency for up to 5 characters and 14 objects in one workflow; 512px–4K; Gemini app, and API preview in AI Studio / Vertex. | A Ren'Py project layout and a character YAML with outfit families. Gemini does not write `matcha_characters.rpy`. | Matcha is a local batch and file writer. Gemini is the model. Using Gemini does not require Matcha. | Whether the consistency claim holds for a transparent, cel-shaded VN sprite set across outfits. No independent eval in this repo. Third-party guides describe drift on long storyboards and recommend re-anchoring ([example](https://flowith.io/blog/nano-banana-consistent-characters-storyboard/)); those guides are not measurements. | Vendor claim **PROVEN** as published. Fitness for VN sprites **UNPROVEN**. |
| **Seedance 2.5** ([ByteDance Seed, 31 Jul 2026](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)) | Audio-video clips up to 30 seconds, multi-round extension, up to 30 reference images plus 10 video and 10 audio clips. Vendor: multi-character appearance can stay stable in complex shots. Rolling out on Jimeng and Doubao; API "coming soon" via BytePlus ModelArk as of that post. | Still images, Ren'Py files. Seedance does not make a sprite matrix. | Different medium. Seedance is relevant because reference-conditioned character identity is being productized for video, which raises the bar for "we lock the face." It is not a substitute for a VN sprite exporter. | Unofficial API wrappers describe a 4K character-sheet endpoint ([example](https://github.com/Anil-matcha/Seedance-2.0-API/blob/main/CHARACTER_CONSISTENCY.md)). That is wrapper documentation, not the Seed blog. Do not treat it as Seedance's product. | Official video scope **PROVEN**. Sprite-pipeline overlap **UNPROVEN** and likely small. |
| **Ludo.ai** ([site](https://ludo.ai/), [asset docs](https://ludo.ai/docs/game-asset-generation), [MCP post](https://ludo.ai/blog/introducing-ludo-ai-api-mcp-integration)) | Vendor: sprites, animated sheets, tiles, UI, audio, 3D, short video; style reference; edit-by-instruction that keeps identity; Unity plugin; REST API; MCP server for Cursor and similar. A comparison page written by Ludo claims broad animation coverage ([their comparison](https://ludo.ai/compare/best-ai-game-asset-generators)). | Declarative outfit families and a Ren'Py `Character` / `layeredimage` writer. Ludo's published engine targets in the pages we saw are Unity, Godot, and GameMaker exports, not Ren'Py script generation. | Ludo is a hosted asset factory with an agent hook. Matcha is a local one-character batch. If "engine-ready sprites from a prompt" is the job, Ludo already sells that job. | Pricing was not on the pages fetched. Ren'Py support was not found and was not exhaustively searched. Quality of identity lock was not tested. | Product surface **PROVEN** as marketed. "Better than Matcha at sprites" **UNPROVEN** — we did not run it. |
| **VNCCS** ([GitHub](https://github.com/AHEKOT/ComfyUI_VNCCS), [workflows](https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Workflows-Overview), [outputs](https://github.com/AHEKOT/ComfyUI_VNCCS/wiki/Output-Folders)) | MIT ComfyUI suite for VN sprites. Create or clone a character, pose, generate transparent PNGs, add costume sets, add emotions. Writes `Characters/<name>/<name>_config.json` and `Sprites/<costume>/<emotion>/...`. Replacing sprites can move older files into `V1/`, `V2/`, … . 1,615 stars, 96 forks, MIT, repo updated 2026-09-28. Easy Install is a separate Windows package (79 stars). | Matcha adds a YAML file, a non-interactive queue of a subset of those nodes, MPS refusal, LOVE32 path refusal, and Ren'Py text. VNCCS's wiki tells the user to copy PNGs out of `ComfyUI/output/VNCCS/Characters/`. It does not mention writing `.rpy`. | Matcha is a client of VNCCS, not a peer. The character / costume / emotion / version layout already exists upstream. Matcha's clothes step is skipped when those nodes are absent, and Emotion Studio is not wrapped. | Whether Matcha's headless pose plates match Pose Studio's WebGL captures. Whether the cloner holds identity on a CUDA box. Star count in `STRATEGY.md` was already flagged as conflicting; the API count above supersedes that note for this date only. | VNCCS scope **PROVEN** from upstream wiki and this repo's wrapper. "Matcha is the missing Ren'Py layer VNCCS needs" **UNPROVEN**. |
| **Scenario** ([FAQ](https://help.scenario.com/articles/1129045411-frequently-asked-questions-faq), [scenario.com](https://www.scenario.com/)) | Hosted generation across image, video, 3D, and audio. Custom style and character training. Projects, collections, tags, search. Visual workflows. API. Open-source Unity plugin. MCP server. FAQ lists foundation models including Flux, GPT, Seedance, and names Gemini 3.1 Flash (Nano Banana 2) as an edit model. FAQ pricing: Free (50 daily credits), Starter from $15/mo, Pro from $45/mo, Max from $75/mo, enterprise custom. FAQ: Scenario does not build the game; you still use an engine. | Local-only runs, a Ren'Py writer, and a YAML look sheet. Scenario's project features are a workspace for generated assets, not a parse of a Ren'Py tree. | Scenario already sits closer to "assets for a production" than Matcha does: projects, collections, workflows, several providers. It does not appear to know that `angry` is an alias of `stressed` inside a particular game. | Whether any Scenario workflow writes Ren'Py. Not found in the FAQ. Third-party reviews quote a $750 Pro tier that contradicts the official FAQ; those numbers are not used here. | Official feature list and prices **PROVEN** as FAQ text. Ren'Py gap **INFERRED** from absence on the pages read, not from an exhaustive search. |
| **Agent Sprite Forge** ([0x0funky/agent-sprite-forge](https://github.com/0x0funky/agent-sprite-forge)) | MIT Codex/Grok skill, 4,215 stars, 409 forks. Natural language in; the agent plans a 2D asset; built-in image generation renders; local scripts clean, split, validate, and export frames, GIFs, and metadata for Godot, Unity, or raw 2D. Also maps. | VN-specific outfit families, expression prompts, and Ren'Py definitions. | This is already "an agent plus deterministic checks plus export," aimed at sprite sheets rather than a narrative-game project model. It is the nearest popular version of an execution loop. It does not read an existing game and report stale assets. | How often the validation catches identity drift versus frame-extraction errors. Not evaluated. | README scope **PROVEN**. Overlap with a future Matcha audit **INFERRED** to be small. |
| **sprite-gen** ([aldegad/sprite-gen](https://github.com/aldegad/sprite-gen)) | Apache-2.0 skill, 2,077 stars, 209 forks. One base image plus a list of actions; row-by-row generation; identity lock claimed; chroma to alpha; frames; runtime atlas; `manifest.json`. Providers named as Codex and Grok. | Multi-outfit look sheet and Ren'Py deploy. | Same "one reference, many states, then a manifest" idea, for animation atlases. The manifest is an export contract, not a live project graph. | Quality of the identity lock. Not run. | README **PROVEN**. |
| **sprite-forge-mcp** ([kitepon-rgb/sprite-forge-mcp](https://github.com/kitepon-rgb/sprite-forge-mcp)) | MIT, 2 stars, updated 2026-09-23. Local Python orchestrator over remote ComfyUI. Character folder, samples, character LoRA, "bible" sheet (turnaround, expressions, actions, costumes), style LoRA, WebUI and MCP on the same service functions, explicit adopt into a game sprites directory. README status line says the matte, bible, and LoRA paths run on an RTX 5090 plus a Mac. | Ren'Py script generation, VN pose aliases, the Kite filename convention. | Architecturally the closest thing to Matcha, plus a character bible and an agent face. The README both describes production gates and, under design principles, says measurements are reported and "nothing is rejected for you." Which behavior is current was not verified by reading the code. | Everything about quality, because the project is tiny and we did not run it. Treat it as prior art for the shape, not as a competitor with users. | Existence and README **PROVEN**. Runtime claims **UNPROVEN** by us. |
| **Unreal Sprite Forge** ([Epic forum thread](https://forums.unrealengine.com/t/sprite-forge-2d-asset-editor-native-to-unreal/2715013)) | A 2D painting / normal-map / animation plugin aimed at Unreal, described by its author in a forum post. Not an AI pipeline and not open source in the material we saw. | Different product. Listed so the name "Sprite Forge" is not collapsed into one tool. | Name collision only. | Current shipping status. The thread is a developer update, not a store page we audited. | Existence of the effort **PROVEN** as a forum post. |
| **TavernSprite** ([visual novels page](https://tavernsprite.com/for/visual-novels/)) | Vendor: upload one front-facing portrait, receive 28 expressions as transparent WEBP in a ZIP, retry single expressions. Page says Ren'Py can reference the files like any other sprite. Page: credit packs start at $6 for 300 credits; 25 free credits on signup. | Multiple outfits, full-body or waist-up poses, generated `.rpy`, local models. TavernSprite's own blog also says the hard part of an expression sheet is consistency, and that their product generates the set for you. | If the user's job is "28 faces, one pose, one outfit," this is a direct hosted answer. Matcha's sample character is four expressions of one outfit, which is inside that job. Kite's three outfits and seated smoking pose are outside it. | Whether output is actually consistent. Not purchased or run. "Ren'Py-ready" on this page means importable files, which is the same bar `STRATEGY.md` already criticized. | Offer and price line **PROVEN** as page text. Quality **UNPROVEN**. |
| **Confetti** ([unLomTrois/Confetti](https://github.com/unLomTrois/Confetti)) | MIT, 9 stars, last update March 2026. A Ren'Py-side Python script: `generate(workflow)` sends a ComfyUI workflow, saves into `game/images`, shows it. README todo still includes batch support. | Offline batch from a character spec, quality reject, deploy of definitions. Confetti generates at play time from hand-written workflows. | Evidence that "Ren'Py calls ComfyUI" has existed as a small open-source script since 2024. It does not own the character matrix. Low traction, so it is prior art rather than a threat. | Maintained or abandoned. The commit silence is real; intent is not. | README **PROVEN**. |
| **Layer** ([layer.ai/alternatives](https://www.layer.ai/alternatives), [layer.ai vs Runway](https://layer.ai/vs/runway.md)) | Vendor, aimed at mobile studios: many frontier models, batch workflows, user-acquisition creatives, LiveOps art, Photoshop / Premiere / Figma plugins, API, MCP, agent features. Their alternatives page says one-time credits start at $10 with no seat fee. | A personal VN sprite batch. Layer is not trying to be that. | Included because it shows "model-agnostic generation plus a workflow runner plus MCP" shipping as studio infrastructure. That is adjacent to the candidate in §5, at a scale and a job (ads and live-ops volume) Matcha does not have. | How much of the agent/memory story is marketing. Not tested. Third-party prices conflict with Layer's own page and are ignored. | Vendor page **PROVEN**. Fit for a solo VN **INFERRED** to be poor. |
| **Flow Production Tracking (ShotGrid) Scene Breakdown** ([developer doc](https://developers.shotgridsoftware.com/3c0c0ab6/)) and **ftrack** ([features](https://www.ftrack.com/en/features), [publishing](https://help.ftrack-studio.backlight.co/hc/en-us/articles/13129940761495-Publishing)) | Studio production tracking. ShotGrid's breakdown app scans a DCC scene for published-file references and lists which are older than the latest version on disk. ftrack models assets, versions, components, review, and approvals. | Nothing in this row. Matcha does not track versions, reviews, or publishes. | These tools already answer "which referenced publish is stale?" and "what is approved?" for teams that publish into them. They do not read a Ren'Py script, and a solo VN developer is not their user. They matter so Matcha does not describe production state as a new idea. | Whether any of them have a Ren'Py integration. Not found in the pages read. | The class of feature **PROVEN**. Usefulness to Matcha's current user **UNPROVEN**. |

Also in the old strategy doc, and not re-audited deeply because they sit beside the job rather than on it: PixelLab and Retro Diffusion (pixel-art tools; `STRATEGY.md` already said not to quote PixelLab's price), Leonardo, and Rosebud (prompt-to-browser-game in secondary roundups). Rosebud prices in those roundups are **UNPROVEN** here and are not repeated. None of them is a reason to keep the current CLI thesis, and none of them is evidence that a project-audit tool for Ren'Py already exists.

**What this table does not support.** It does not support "nobody writes Ren'Py definitions." It does not support "nobody can keep a character consistent." It does not support "there is a proven gap." The narrowest thing Matcha still does that the fetched pages do not show another tool doing is: read one YAML look sheet (outfits, aliases, filename template) and emit idempotent Ren'Py image statements for the poses that survived a local quality check. That is a feature. It is not, on this evidence, a company.

---

## 5. Candidate Matcha 2.0 Problem

Hypothesis, not a decision:

> Matcha could become a production intelligence layer for AI-assisted game assets: understand the state of a game project, its characters, assets, dependencies, requirements, approvals, and changes, then help execute the work.

The word "could" is load-bearing. The pain this names is real in ordinary production (which files are missing, which are out of date, which are approved, which scenes cite them). It is not yet shown to be a pain for the person Matcha is built for, on a project the size of a solo visual novel, beyond what a YAML file and a directory listing already answer.

Why it is worth one experiment:

- The current tool generates files and then stops. It cannot look at `examples/sample-vn/game/script.rpy` and say which images that script requires. It cannot look at Kite's alias and say `angry` is not a missing file.
- The author already maintains that knowledge by hand in `configs/kite_male.yaml` and in comments about live pixel sizes. The knowledge exists. It is not queryable, and it is not tied to the files in a game.
- Generators are getting easier to swap. A layer that knows the project could call whichever generator is good this month. A layer that *is* a generator call will be rewritten every time the model changes.

Why it may be the wrong problem:

- For a four-pose sample character, the "graph" is the YAML. A person can see it.
- Studio trackers already model version, review, and approval. Rebuilding a worse tracker is a known failure mode.
- The author of this repo has one live game and has deliberately forbidden the tool from writing to it. A product that only pays off inside a large, messy project may have no user if that project cannot be touched and no second project exists.
- If users keep asking for better pictures, an intelligence layer will feel like delay.

This hypothesis is adopted only as the thing to falsify in §16. It is not a roadmap commitment.

---

## 6. Candidate Core Objects

These are candidates for a model, if the experiment shows they earn their keep. They are not a schema to build.

| Object | Why it might exist | Relationship that would actually matter |
|---|---|---|
| **Game** | The root a human already has: a Ren'Py directory, later maybe another engine. | Which characters and files belong to it. Without this, every run is a loose YAML. |
| **Character** | Already the only real object (`CharacterConfig.name`). | Identity that survives outfit and pose changes. |
| **Canonical Design** | The approved description of face, body, and style. Today this is a prompt string plus, for Kite, an uncommitted reference PNG. | A content hash. Generations record which hash they used. Change the hash and previous generations become candidates for stale, not automatically wrong. |
| **Reference** | A specific image the design is anchored to. Kite's `reference:` is this, and it is easy to confuse with the design itself. | Reference is evidence for a design, not the design. Replacing the PNG is a design change only if a human says so. |
| **Outfit** | Already `outfit_families` plus per-pose overrides. | Which poses wear it. An apron change affects the apron poses and not `withdrawn`. That edge is the one already encoded and not queried. |
| **Expression** and **Pose** | Today one field, `poses`, means both ("happy", "smoking", "crossed_arms"). | Split them only if a real asset is expression-on-a-shared-body, which `--layered` does not currently produce. Forcing the split now would invent a structure the sample game does not use. Kite's smoking pose is a pose with an expression baked in. Keep them as one **Sprite state** until a layered body exists. |
| **Asset** | A file: path, pixel size, hash, which state it claims to be. | The join between a state and a file. Missing means the state has no file. Ambiguous means two files claim one state (Kite's underscore names versus space names are already this bug, handled with a template). |
| **Scene** | A Ren'Py label or a block that shows images. | Which assets it references. Low value if the game is a straight script with a handful of `show` lines. High value if outfits change by attribute and the script is long. |
| **Script** | The `.rpy` files. | The text that names images. This is the source of "required," not a parallel spec. |
| **Dependency** | Not an object. An edge: script → image name → asset; alias → real state; outfit → states; design hash → generation. | A generic dependency table before those edges are real will be empty architecture. |
| **Requirement** | "The game needs this state." Derived from the script and the character spec, not typed in a second time. | Requirement without a matching approved asset is the missing-asset question. |
| **Generation** | One attempt: provider, model, seed, prompt, inputs, output hash, timestamp. | Ties an asset to the design hash and the provider. This is what makes "stale" computable. |
| **Evaluation** | A recorded check. Today the quality gate is an anonymous pass/fail on luma. | Separate "file is not garbage" from "file still looks like the character." The second is unsolved here. Do not pretend one object solves it. |
| **Approval** | A human decision on a specific file hash. | Approval of hash H is not approval of a later file. This is the only state that must be stored, because it cannot be derived. |
| **Version** | The sequence of generations and approvals for one state. | VNCCS already versions by moving old PNGs into `V1/`. A Matcha version object is only useful if it records why the new file exists (design change versus reroll). |
| **Export** | A copy into the game tree, distinct from the working file. | Echo's workflow already separates them (`output_dir` versus `--copy-only`). The live game has its own scale rule for one file. Export is not "the asset." |

If only three relationships survived a cut, they would be: **design hash → generation → file**, **outfit → states**, and **script image name → state, including aliases**. Scene, expression-versus-pose, and a generic Dependency object can wait.

---

## 7. Asset / Project Graph Hypothesis

Hypothesis, not a moat:

> A useful graph for this product is Character → Outfit → Sprite state → Asset → Scene → Script → Game. When the canonical design changes, the graph names the assets whose generations used the old design.

What is already true without a graph: `configs/kite_male.yaml` lists ten states, three outfit families, and one alias. A person who can read YAML can answer "which poses wear the apron?" That means the first demo of a graph that only reprints `outfit_families` has failed.

Where a graph might still earn a result:

- **Alias.** `show kite_male angry` is not a missing `angry` file. The CLI knows the alias when generating. It does not know it when reading a script, because it never reads a script.
- **Filename versus tag.** Disk name `kite_male smoking.png` (space) versus local output `kite_male_smoking.png`. The template is a comment and a string. A graph would make "these two paths are the same state" a fact.
- **Design change versus outfit change versus reroll.** Changing eye color invalidates every Kite file. Changing the apron invalidates seven states, not `withdrawn`. Rerolling `smoking` invalidates one file. The YAML can express this. Nothing computes it, and nothing checks the game tree afterward.
- **Display exception.** The live `crossed_arms` file is a different size and the game scales it by 1.39. That fact lives in a YAML comment. If a regeneration writes one canvas for every pose, the scale rule in the game becomes wrong. The affected thing is not only the PNG. It is a line of game code. A file-only tool will miss that. This is the strongest example in the repo, and it lives in a project the tool is not allowed to edit.

What the graph does not automatically give:

- Visual consistency. Knowing that seven files are affected does not make the new seven files match.
- A moat. VNCCS already stores character, costume, and emotion as folders. ShotGrid already stores "this publish is older than the latest." The hypothesis is that joining **game script references** to **design hashes** is the useful join for a solo narrative project. That join was not found as a shipped feature in §4. Absence after a search is **INFERRED**, not proof of a gap.

---

## 8. Production State

Possible states, if anything like them is stored or computed:

`PLANNED`, `GENERATING`, `GENERATED`, `VALIDATING`, `REVIEW`, `APPROVED`, `EXPORTED`, `REJECTED`, `STALE`, `SUPERSEDED`, `BROKEN`.

Most of these are either a transient CLI phase or a fact already sitting on disk.

| State | Can it be computed from files? | Would a stored status help? |
|---|---|---|
| PLANNED | Yes: a state in the spec with no generation record. | No. |
| GENERATING | Only while a process is running. | A lock file at most. A database row for this is ceremony. |
| GENERATED | Yes: a PNG exists for the state. | No. |
| VALIDATING | Transient. | No. |
| REVIEW | Yes if "PNG exists and no approval record." | Maybe, as a query, not as a column someone must remember to set. |
| APPROVED | No. A human has to say so, and it must name a file hash. | Yes. This is the one worth storing. |
| EXPORTED | Yes: hash in the game tree matches an approved or generated hash. | The comparison is the feature. A flag will drift. |
| REJECTED | Partly: `output_dir/rejected/` already stores dumps. | Keep the dumps. A status word adds nothing. |
| STALE | Yes if generations store the design hash and the outfit hash they used. | Compute it. A hand-set STALE bit will be wrong. |
| SUPERSEDED | Yes: an older generation for the same state, kept on purpose. | Only if we keep history. VNCCS already keeps old PNGs in version folders. |
| BROKEN | Partly: quality gate, missing file the script names, unreadable PNG, alias pointing at a missing target. | Compute it. "Broken" as a workflow status will get used as a junk drawer. |

A full lifecycle enum is architectural complexity unless the slice in §16 shows a person losing track of something the filesystem does not already show. The useful design is: **store approvals and generation records; derive everything else.** Shipping eleven statuses before that evidence exists repeats the failure mode of a tracker nobody updates.

---

## 9. Project Audit Hypothesis

Hypothesis: Matcha could answer, for one game:

1. What assets are missing?
2. What is stale?
3. What is broken?
4. What is inconsistent?
5. What is still blocking release?
6. Which assets are affected by this character change?

How each question sits today:

| Question | Answerable from this repo's code? | Who already answers a version of it? |
|---|---|---|
| Missing | No. The CLI knows the YAML pose list and the output folder. It does not read `script.rpy` or compare them. | A person with the YAML and `ls`. VNCCS shows which sprites it has generated for its own character folder, not for the game. |
| Stale | No. There is no design hash on output files. Resume skips any PNG that passes the luma gate, including one generated from an old prompt. | ShotGrid breakdown, for published DCC references. Not for prompts. |
| Broken | Only the quality gate (black, smear, static band) and "ComfyUI error." | The author, by looking. sprite-forge-mcp claims measured adopt checks; two stars, not verified. |
| Inconsistent | No semantic check. Prompt text says "same hairstyle, same eye color." That is a wish. | Frontier models and VNCCS claim consistency. None of them audit an existing Ren'Py project for it. **UNPROVEN** that anyone does that audit. |
| Blocking release | No notion of release. `matcha disclose` drafts a platform form. It does not know whether every speaking character has an approved sprite. | The developer, and store checklists. |
| Affected by a character change | No. Editing `description` or an outfit family does not mark files. | The author, by reading `pose_overrides`. |

So the audit is not a crowded feature under a name we found. Parts of it are crowded under other names (version freshness, expression packs, character libraries). The specific combination — a Ren'Py script, an alias, an outfit family, and a design hash — was not found as a product. That is an observation from the sources in §4, **INFERRED** to be incomplete, and it is exactly what the slice has to test. If the combination takes an afternoon of Python to demonstrate and the author shrugs, it is not a product.

---

## 10. Execution Hypothesis

Hypothesis: once a plan exists ("these seven apron poses are stale"), executing it should go through replaceable adapters, not through a new generator.

Plausible adapters, and whether the slice needs them:

| Adapter | Role | Needed to test the hypothesis? |
|---|---|---|
| Filesystem | Read the game, write approved files, record hashes. | Yes. This is the whole read side and the export side. |
| Git | See whether an asset or a script line changed. Optional diff of the game. | Useful, not required for a first read-only inventory. |
| Game-project tools | Ren'Py lint (`renpy.sh <project> lint`) is the one already named in the README. | Worth using as a check that generated script still parses. Not a new integration. |
| Generation APIs | ComfyUI's existing HTTP and WebSocket API; Gemini's API preview; Scenario's API; Ludo's API. One of these, whichever is actually available, regenerates the affected files. | Yes, one existing provider, behind a narrow call. Building a provider is out of scope. |
| MCP | Ludo, Scenario, Layer, and sprite-forge-mcp already expose MCP so an external agent can call them. | No. An MCP server would make Matcha callable from Cursor. It does not help Matcha understand the game. Adding one now is a distribution choice disguised as architecture. |
| Browser automation | Drive a website or a ComfyUI tab that has no API. | See below. |

**Browser execution is not necessary for the experiment.** ComfyUI is already an API, which is how Matcha queues both txt2img and VNCCS. Gemini, Scenario, and Ludo publish APIs. VNCCS's Pose Studio is the one UI-shaped dependency in the current stack, and the current code already injects pose plates so it does not have to drive that UI. A human can still approve images by looking at PNGs on disk.

A service like TinyFish, or an open-source browser agent, would fit only as a later adapter for a provider that is genuinely web-only and worth using. That situation was not found for the slice. Building a browser agent, or a clone of a hosted browser-automation service, does not answer whether the project graph is useful. It adds a fragile execution path in front of an unvalidated question. Do not build it. Do not design for it until a concrete provider blocks the slice and an official API does not exist.

Provider-agnostic execution, in the smallest form: a function that accepts "make this state again from this design hash" and returns a PNG plus the record of how it was made. ComfyUI can be the first implementation because it is what the repo already calls. It must be swappable in the experiment's notes even if the code stays on ComfyUI.

---

## 11. Open Ramp Relationship

Open Ramp is not in this repository. No document, comment, config, or commit message here names it. From the request that prompted this note, the only facts used are: it is a separate product of the same people, the name is a working name, and it is described as a control-panel / open-ecosystem product. Its objects, license, stack, users, and whether any code exists are **unknown**. Choosing a shared architecture from that description would be fiction.

| Option | For | Against |
|---|---|---|
| **A. Remain independent** | Matcha can be validated or killed without waiting on another product. The sprite problem is concrete. Independence avoids coupling to an unspecified control panel. | Two products may invent two approval models and two notions of "project" and then pay to merge them. If Open Ramp is the thing users actually open, an independent Matcha CLI repeats the "thin wrapper nobody launches" failure. |
| **B. Share architectural concepts, not code** | Cheap, if it means a written glossary (Game, Asset, Approval, Version) that both sides can ignore where it does not fit. A glossary is not a dependency. | A shared glossary with no shared users becomes a naming exercise. It also creates pressure to model Matcha objects so they look like Open Ramp objects that have not been seen. |
| **C. Share a core** | Only makes sense if both products turn out to be the same loop: inspect a project, decide what is stale, execute through adapters, record approval. A core extracted after both loops exist would be evidence-based. | There is nothing to share today. Matcha's core is a ComfyUI client. Extracting it into a library for an unknown product freezes the wrong boundary. |
| **D. Become a specialized vertical on Open Ramp** | If Open Ramp is a real control panel with projects, permissions, and job running, a game-asset vertical could be a pack of objects and adapters rather than a second app. | Unknown whether Open Ramp wants verticals, whether its control panel is local or hosted, or whether its user is a game developer. Betting the reset on that is a dependency on a product this repo cannot describe. |
| **E. Fork Open Ramp** | A fork is justified when a codebase is close and its maintainers will not take the changes. | There is no codebase in view. Forking an unknown project is how a reset acquires someone else's unvalidated scope. |

No option is selected. A is the only one that can proceed before Open Ramp is written down. B is acceptable as a one-page glossary after Open Ramp has its own object list, and not before. C, D, and E should not be chosen from this document.

---

## 12. What Matcha 1.0 Should KEEP

Keep means "do not throw away if a slice starts." It does not mean "build 2.0 on top without changing boundaries."

- **The character spec as data.** Name, shared description, pose list, outfit families, per-pose overrides, aliases, filename template, reference path. `configs/kite_male.yaml` is the best requirements document in the repo. Sakura's YAML is a demo and is too flat to learn from.
- **The ComfyUI client as one provider.** Queue, upload, websocket wait, history, `/view`, loud `execution_error`. It is the only working execution path.
- **Preflight against `/object_info` and the VNCCS node list.** Fail before a long run. The unwired file-size check can stay as a function if a provider still loads local checkpoints.
- **Incremental PNG writes, skip-if-accepted, reject dumps with metrics.** These are operationally real on a fifteen-minute Mac run. They are not a product.
- **The quality gate as a "this file is garbage" filter.** Black frames and the smear pattern are observed failure modes. Keep them labeled as garbage detection.
- **Idempotent replacement of one character's block in a generated `.rpy` file.** The marker comments are a decent export tactic for a sandbox project.
- **Side-image crop and resize.** Small, deterministic, tested. Easy to rehome.
- **Refusing to write the live LOVE32 tree.** Safety policy for that game, not a feature to generalize into a denylist architecture.
- **License and disclosure drafts.** Narrow, honest about not being legal advice, and directly tied to shipping AI images on Steam and itch. Two catalog entries is a start, not a system.
- **The mocked test suite as the way changes stay honest.** 105 tests, no GPU. Any slice should add tests for inventory and affected-set logic the same way, without requiring ComfyUI.
- **The written habit of tagging limits.** README statements like "prompt plus seed is not a lock" and "VNCCS fails preflight on MPS" are worth more than a new subsystem.

---

## 13. What Should Be REFACTORED

Not done in this change. Listed because the current boundaries will mislead a 2.0 experiment if they are treated as given.

- **`matcha character` is the product.** A project-intelligence experiment needs a read command that does not generate. Stuffing an audit into more flags on `character` will keep generation as the center.
- **Pose means three things.** A filename token, an expression prompt, and a body pose. Kite's look sheet works around this with overrides. A refactor splits them only if the slice needs the split (§6).
- **`--layered` sounds like layered sprites.** It emits whole-image attributes. Rename the concept in any new spec so nobody plans a face-layer pipeline on top of it.
- **The Ren'Py deployer assumes Matcha owns the character definitions.** The one real game cannot accept that, which is why `--copy-only` exists. Export should be a strategy (write definitions, or copy into an existing naming scheme) rather than a default that the important project forbids.
- **VNCCS graph construction inside this repo.** Node ids and `widget_data` are copied from upstream workflows. They will rot as VNCCS 3.0 moves. If VNCCS remains a provider, prefer running their workflow JSON with substitutions over a second implementation of their graph. That judgment is **INFERRED** from the size of `matcha/vnccs.py` (about 640 lines) and from the upstream wiki's separate Emotion Studio step, which Matcha does not wrap.
- **Prompt tables as the canonical design.** `POSE_EXPRESSIONS` is a hidden second spec. The YAML should be the only authoring surface, or the hidden table will disagree with the game.
- **`validate_model_file` disconnected from the CLI.** Either the character path calls it or the strategy doc stops claiming it.
- **Stale docs.** `AGENT_CONTEXT.md` still points at LOVE32 as the dogfood project. `STRATEGY.md` §4.5 still says the CLI reports success on total failure. `docs/ANNOUNCE.md` still has a draft that calls prompt plus seed the consistency story. Fixing those is documentation hygiene for later, not part of this branch.
- **Provider details on `CharacterConfig`.** Checkpoint, LoRA, IP-Adapter, denoise, and VNCCS reference are all fields of the character. A character is not a ComfyUI job. Generation parameters belong on the generation record.

---

## 14. What Should Be DELETED

Concepts to retire. Nothing in the repository is deleted by this note.

- **"The moat is orchestration plus the last mile."** It was a hypothesis. §4 does not support promoting it to a fact.
- **prompt + shared seed as a user-facing consistency feature.** The code already disclaims it. The remaining work is to stop older docs from selling it.
- **IP-Adapter and img2img chaining as the identity strategy.** They remain in the tree as default-off experiments that corrupt on the only GPU the timeline records. They are not a roadmap item unless a CUDA run produces a saved comparison. Until then they are dead product surface.
- **The north star "mystery game from a sentence" as an implied promise.** It pulls the project toward an engine. The strategy doc already says that is the mistake. Say it once and stop planning toward it.
- **The four-phase commercial roadmap** (pipeline demo → free release → first dollar → hosted after ~100 sales). Phase 1's technical exit happened. Phase 2's outreach was then deferred indefinitely. Phases 3 and 4 are a business stacked on an unvalidated wedge. Do not carry that sequence forward. See §20.
- **Matcha as a VNCCS competitor.** The code already says it wraps VNCCS. Any future doc that lists VNCCS under "what they don't do" as if that were the gap should be treated as expired.
- **Hardcoded personal production details as architecture.** Jeffrey's machine paths, the Echo scale factor, and the LOVE32 component check are safety and dogfood notes. A 2.0 model must not grow a special case per friend project. The Kite YAML can stay as the fixture for the slice.
- **A license catalog presented as coverage.** Two families and an unknown bucket is a helper. It is not "per-model license surfacing" in any general sense.
- **Announce-driven scope.** `docs/ANNOUNCE.md` assumes the thing to ship is the current wedge. Public posts are not the next step while the wedge is the thing under reconsideration.

---

## 15. What Should Be NEW

Only what the candidate problem needs in order to be tested. Each item is unjustified if the slice fails.

1. **A read-only inventory of one Ren'Py project** against one character spec: files present, image names declared, image names used in script, aliases, outfit membership, pixel sizes.
2. **A generation record** (even a JSON sidecar): design hash, outfit hash, provider, seed, output hash. Without it, stale is a feeling.
3. **An affected-set query:** given a described change (identity field, one outfit, one state), list files and script sites. This is the graph hypothesis in one command.
4. **An approval record** bound to a file hash, written only by an explicit human action.
5. **A regenerate call** for the affected set through one existing provider, writing to a sandbox directory, not to a live game, and not exporting until approval.
6. **A short written result from the person who ran the slice**, compared with doing the same questions by hand.

Not new, until those six exist and survive §18: a service, a database, a UI, an MCP server, a browser agent, a second image backend built in-house, multi-engine support, accounts, billing, a Pro pack.

---

## 16. Proposed Vertical Slice

Smallest experiment. One character. Goal: learn whether the candidate problem is real. Completeness is a failure mode.

**Character:** Kite, because Sakura cannot teach this. Sakura has four poses and one outfit copied four times. Kite has three outfit families, an alias, a filename rule, a reference image, and a known display-size exception. **Project:** a sandbox copy, never the live LOVE32 tree. The existing refuse rule stands. If the live files are required as ground truth, a human copies them into the sandbox first, which is already the documented Kite workflow.

The slice walks ten steps and records what a human had to supply at each one:

1. **Understand the project.** Point at the sandbox Ren'Py tree. List scripts, image declarations, and image files. No generation.
2. **Understand the character.** Load `configs/kite_male.yaml` as the spec: states, families, alias, template, reference path.
3. **Inventory assets.** Join spec states to files in the sandbox, including the space-versus-underscore naming trap.
4. **Identify missing and stale.** Missing: a state with no file, and a script reference that does not resolve through the alias. Stale: only if a generation record exists; on the first run, say "no record, cannot know" rather than inventing freshness.
5. **Change canonical character info.** Two scripted edits, done separately: (a) apron family wording, (b) a shared identity field such as eye color. Record the hashes before and after.
6. **Determine affected assets.** (a) should list the apron states and not `withdrawn`. (b) should list every Kite state. `angry` should follow `stressed`. The `crossed_arms` display scale should be reported as a game-side consequence if that line exists in the sandbox script; if the sandbox does not contain it, record that the graph cannot see consequences that were not copied.
7. **Generate or regenerate the affected assets.** One existing provider. Prefer the provider the operator can actually run. On a Mac without VNCCS, that may be txt2img with the disclaimer that identity will not hold, which is a useful negative result. Do not add a provider to make the slice look better.
8. **Validate.** Run the existing garbage filter. Separately, have a human say whether the face and the outfit match the spec. Write down both results. Do not average them into one score.
9. **Approve.** Explicit accept or reject per file hash. Rejection leaves the sandbox game unchanged.
10. **Update the game project.** Copy approved files into the sandbox using the filename template. Do not write `Character` / `layeredimage` into a tree that already defines Kite, unless the sandbox is the sample project and the definitions are the thing under test. Run Ren'Py lint if the SDK is present. If it is not, record that export parsing was not checked.

Stop. Do not add a second character inside the same experiment. A second character is the first generalization test, and it belongs after the notes from this one exist.

---

## 17. Success Criteria

Measurable on this one slice. No score for the company.

| # | Criterion | How to measure | Passing looks like |
|---|---|---|---|
| 1 | Inventory matches a hand-built gold list for the sandbox. | Beforehand, a person lists expected states, files, aliases, and script references. Compare. | Every gold-list required file is found. Zero alias resolved as a missing file. False-missing and false-present counts written down. |
| 2 | Affected-set for the apron edit. | Gold list is the apron-family poses in the YAML, plus any sandbox script lines that show those states. | Recall 1.0 against that gold list and precision 1.0, including not selecting `withdrawn`. If this fails, the graph is worse than the YAML and the slice stops. |
| 3 | Affected-set for the identity edit. | Gold list is every Kite state that has or should have a file. | Same standard as #2. |
| 4 | Time against the baseline. | The same person answers "what is missing, what is affected by an apron change" with the YAML, `ls`, and search, then with the slice. Record minutes, including time to set the tool up. | The slice is clearly shorter on this project, not by a minute. If setup exceeds the savings, that is a fail even if the answers are right. |
| 5 | Approval gates export. | Attempt to update the sandbox before approval. | No file in the game tree changes. After approval, only approved hashes are copied. |
| 6 | The operator can say what was learned. | One paragraph: what they would do next time without this tool, and whether the tool changed that. | The paragraph names a decision (keep going, narrow the problem, or stop). A demo without a decision is not success. |
| 7 | No new infrastructure. | Diff of the experiment. | Filesystem, the existing CLI or a throwaway script, and at most one already-available generator. No service, database, UI, MCP server, or browser agent. |

Criteria 2 and 4 are the ones that can kill the hypothesis even if the software works.

---

## 18. Kill Criteria

Stop or reposition if any of these is true after the slice. Do not respond by adding scope.

1. **An existing tool already does this workflow** for the sandbox, once the operator tries VNCCS's character folder plus a plain file diff, or a frontier model's reference edits plus a manual copy. "We also write `.rpy`" is not a rescue.
2. **The developer cannot perceive a meaningful time saving** on Kite, the character we already understand best. If it does not save time here, it will not save time on Sakura.
3. **The dependency graph adds little beyond the YAML.** If the affected set is a lookup of `outfit_families` and `pose_aliases`, the graph is a reprint. Retire the graph hypothesis.
4. **Automated visual QA is unreliable** and the human review is the whole validation step. Garbage detection can stay. Identity scoring that the human overrides every time is not a subsystem to deepen.
5. **Change propagation is brittle.** It works only with Kite's exact keys, or it misses the display-scale consequence and also misses a second kind of consequence. A graph that is right only for the fixture it was read from is not a product.
6. **Generation remains the only thing the operator cares about.** If the notes say the valuable moment was the PNG and the inventory was ignored, Matcha is still a generator wrapper. Reposition or stop. Do not add a tracker in front of a generator the user does not want a tracker for.
7. **The slice only works by writing into the live game,** or only by special-casing LOVE32. The safety constraint is not optional. A hypothesis that requires violating it is the wrong hypothesis.
8. **A second, smaller check fails immediately:** explain the slice's result to someone who did not write the YAML. If they cannot tell what question it answered, it is an internal script.

Passing none of the kill criteria is not a launch decision. It is permission to consider §20 phase 2.

---

## 19. Architecture

**PROVISIONAL. Not a design to implement.** A sketch of the slice if it survives, so later work does not grow the CLI flags again.

```
Matcha core (specs, records, queries)
  → Project intelligence (read a game tree and a character spec)
    → Asset graph (the few edges in §6, not a general graph database)
      → Production state (derived, plus stored approvals and generation records)
        → Planner (affected set and a proposed regenerate list)
          → Validation (garbage filter, then a human)
            → Execution (filesystem export; one swappable generator)
```

Generation providers sit behind execution and are replaceable by definition: ComfyUI txt2img, a VNCCS workflow JSON, or an HTTP image API. The core does not import a provider's node graph. Records store provider name and inputs so a later provider can regenerate from the same spec without claiming the pixels will match.

This sketch is wrong if the slice shows that a directory listing and the YAML are enough. In that case the architecture is a script with no layers, and this section should be ignored.

Explicit non-contents: no service, no database requirement (JSON sidecars are enough at this size), no UI, no MCP, no browser runner, no TinyFish-shaped component, no new model.

---

## 20. Matcha 2.0 Roadmap

Gates are validation results, not dates. The previous sequence — Phase 1 pipeline demo, Phase 2 free release, Phase 3 first dollar, Phase 4 hosted after about a hundred sales — is **retired** as the plan for this product. It assumed the wedge was the thing to ship. This reset does not assume that. Commercial packaging, a public launch, and a hosted generator are not phases here. They can be invented later only if a workflow has already survived the kill criteria.

**Phase 0 — This note.** Done when `docs/MATCHA-2-RESET.md` exists and the diff against `main` is only that file. No behavior change.

**Phase 1 — Run the slice in §16.** Gate: the criteria in §17 are filled in with actual counts and times, and §18 has been applied honestly. The output is a short results note. It is allowed to say "stop." No product surface is added in order to make the gate easier to pass.

**Phase 2 — Read-only project intelligence, only if phase 1 did not trip a kill criterion.** One character spec, one Ren'Py sandbox, inventory and affected-set as a command. Still no regenerate requirement beyond what phase 1 already used. Gate: a second, planned change (not the apron edit and not the eye-color edit) produces an affected set a human accepts without editing the tool's rules by hand.

**Phase 3 — Approved regenerate and export, only if phase 2's gate holds.** The same provider interface as the slice, records stored, export still sandbox-only. Gate: one full loop from design edit to approved file in the sandbox, and the operator chooses to run it a second time without being asked.

**Phase 4 — A second character or a second project, only if phase 3's gate holds.** If Kite-specific names, templates, or path checks are required for correctness, stop and call the result a Kite tool. Generalizing engines, adding providers, or talking about Open Ramp sharing belongs after this gate, not before.

If phase 1 says the valuable product is still "generate sprites," the roadmap ends. The remaining choice is to maintain the CLI as a personal tool or to stop. That choice is not given a phase, because it is not a 2.0.

---

## 21. Final Assessment

**What Matcha is today.** A local, honest, narrow CLI: one character YAML, ComfyUI, optional VNCCS nodes, a garbage filter tuned for a Mac failure mode, and a Ren'Py copy step that the author's real game will not accept. Version 0.1.0. Tested with mocks. Not launched. The best artifact in the repo is the Kite look sheet, not the generator.

**What it could become.** A small production-intelligence layer that reads a narrative game, joins a character spec to real files and script references, and helps regenerate only what a design change invalidates. That is a hypothesis. It is interesting because the repo already contains the spec and already refuses to confuse generation with deployment. It is unproven because nobody has asked the tool those questions and timed the answers.

**What is genuinely promising.** The outfit-family and alias data is real structure, not a prompt. The separation between "generate into a sandbox" and "write the live game" is the right instinct and is already enforced. Disclosure drafts match a real platform constraint. The team has a record of writing down when a technique does not work (IP-Adapter on MPS, prompt plus seed is not a lock). That habit is an asset. The slice is small enough to run.

**What is weak.** The stated moat is orchestration of a generator category that is crowded and getting more capable. The default backend does not lock identity, and the backend that might has no saved successful run in this repo. The Ren'Py "last mile" is the piece the real project opts out of. There is no evidence of a user who is not the author. `MatchaConfig` is a placeholder. A month of quiet after August 2026 is consistent with a wedge that did not pull the next step by itself (outreach deferred is a decision recorded in `TIMELINE.md`, not a guess about motivation).

**What is still unknown.** Whether anyone will care about missing, stale, and affected-set answers once a generator is good enough. Whether that join already exists in a tool the search did not surface. Whether Open Ramp has any objects worth sharing. Whether VNCCS Character Cloner actually holds Kite's face on a CUDA machine. Whether Nano Banana-class models make the sprite matrix a one-prompt task for this art style. Whether the `crossed_arms` scale issue is a hint of a class of problems or a one-off.

**What to test next.** The Kite sandbox slice in §16, starting with the read-only questions, with a clock running against a YAML-and-`ls` baseline. Do not implement a platform first. Do not add a provider. Do not announce the current CLI while this question is open.

---

## Repository Safety

This reset is a planning document. It does not change the CLI, the Python package, tests, configs, examples, or any existing document.

The only path added on `matcha-2-reset` relative to `main` is `docs/MATCHA-2-RESET.md`.

Diff stat (`git diff --stat main...matcha-2-reset`), recorded after the final commit on this branch:

```
 docs/MATCHA-2-RESET.md | 484 +++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 484 insertions(+)
```
