# Audit #1 — Kite Production-State Audit

Forensic inventory of what this repository contains about Kite. Labels used below:

- **EXPLICIT** — the text or code states it directly.
- **INFERENCE** — concluded by combining clues. Not a field or file that states the conclusion.
- **UNKNOWN** — not established by anything inspected.
- Evidence quality: **HIGH** (structured data or code), **MEDIUM** (several pieces of prose or code that agree, but the fact is not a modeled field), **LOW** (naming or a single weak clue), **UNKNOWN** (no usable evidence).

No image in this repository was opened, because no Kite image is present.

---

## 1. Scope

Inspected the Matcha repository on branch `matcha-2-kite-audit`, created from `main` at commit `65bb0f5` (`VNCCS wrap: Character Cloner from a sandbox reference is the same-face lock`). The working tree at the start of the audit matched that commit. `matcha-2-reset` was not used as a source.

Inspected: `configs/kite_male.yaml`; Kite-related passages in `README.md`, `TIMELINE.md`, `AGENT_CONTEXT.md`, `AGENTS.md`, `STRATEGY.md`, and `docs/ANNOUNCE.md`; `.gitignore`; `refs/.gitkeep`; the character, prompt, config, VNCCS, image, formatter, and deployer code paths cited in §7–§9; Kite-related tests in `tests/test_quality_looksheet.py` and `tests/test_vnccs.py`; every `*.rpy` under `examples/sample-vn/game/`; `git ls-files` and history for `*kite*` and `*.png`.

Present on disk and checked: `refs/` contains only an empty `refs/.gitkeep`. These paths are not on disk: `sandbox-kite/`, `sandbox-renpy/`, `output/`, `refs/kite_male_neutral.png`.

Not accessed: the live LOVE32 / Echo project. Docs name `/Users/jeffreytse/Desktop/LOVE32/LOVE32/` (`README.md` lines 148–149, `configs/kite_male.yaml` lines 82–83, `AGENT_CONTEXT.md` lines 45–47). That tree is not in this repository. It was not opened, copied, or searched. `examples/sample-vn/` was searched only to see whether it names Kite. It does not. It is a Sakura sample, not a Kite project.

Not done: no ComfyUI connection, no generation, no writes into any game tree, no web lookups, no changes to character, asset, script, or config files.

---

## 2. Sources Inspected

| Source | What it is |
|---|---|
| `configs/kite_male.yaml` | The only Kite character file. 98 lines. |
| `README.md` lines 107–108, 143–179, 261–264, 307–381 | Prose restating the YAML, the hand-copy reference procedure, filenames, pixel sizes, and copy-only behavior. |
| `TIMELINE.md` lines 10–12, 35–37, 169–176 | Mentions an "Echo disk spec" and forbids live LOVE32 deploy. Does not list Kite's poses. |
| `AGENT_CONTEXT.md` lines 44–47 | Describes a LOVE32 tree (`game/images/characters/`, `game/matcha_characters.rpy`). Does not name Kite. |
| `AGENTS.md` (LOVE32 dogfood warning), `STRATEGY.md` (sandbox, not live LOVE32), `docs/ANNOUNCE.md` line 174 | Say not to deploy into live LOVE32. No Kite appearance data. |
| `.gitignore` lines 8–11 | Ignores `sandbox-renpy/`, `sandbox-kite/`, and `refs/*.png`. |
| `refs/.gitkeep` | Empty tracked file. No image. |
| `matcha/config.py` | `CharacterConfig`, `PoseOverride`, `outfit_for`. |
| `matcha/prompts.py` | `POSE_EXPRESSIONS`, `build_pose_prompt`, `build_negative_prompt`. |
| `matcha/cli.py` | Load, alias resolution, filenames, LOVE32 refusal, copy-only, reject dumps. |
| `matcha/vnccs.py` | `character_info_from_config`, clothes widget, pose plates, pose data. |
| `matcha/images.py` | `persist_rejection` sidecar shape. |
| `matcha/formatters/renpy.py`, `matcha/deployers/filesystem.py` | Generic Ren'Py text and file copy. No Kite-specific branch. |
| `tests/test_quality_looksheet.py` `test_kite_yaml_matches_live_echo_disk_spec` (lines 204–278) | Loads `configs/kite_male.yaml` and checks in-repo fields. Does not open LOVE32. |
| `tests/test_vnccs.py` `_kite_cfg` (lines 67–89) and `test_kite_identity_maps_to_creator_fields` (lines 230–238) | A shortened in-test config, not the YAML file. |
| `examples/sample-vn/game/*.rpy` | No occurrence of `kite`, `Kite`, `LOVE32`, or `Echo`. |
| Git history | `configs/kite_male.yaml` is tracked. No `*.png` path containing `kite`, `character`, or `sprite` has ever been committed. Sample-vn GUI PNGs exist and are not Kite art. |

---

## 3. Kite Canonical Information

There is no separate canon, bible, or approval record. Appearance text lives in one YAML file. Other files repeat parts of it or map it into generator fields.

### 3.1 Identity keys

| Item | Where | What it establishes | Label | Evidence |
|---|---|---|---|---|
| Machine name `kite_male` | `configs/kite_male.yaml` line 13, key `name` | The character id used in filenames and, if a script block were written, as the Ren'Py identifier. | EXPLICIT | HIGH |
| Display name `Kite` | same file, line 14, key `display_name` | A display string. `RenPyFormatter.script_block` uses `display_name` as the `Character()` name when a deploy writes a block (`matcha/formatters/renpy.py`). This YAML does not set `color`. | EXPLICIT | HIGH |
| "Echo" and "LOVE32" | YAML comments lines 1–5 and 81–85; `README.md` lines 143–153 and 316–317; CLI strings in `matcha/cli.py` (for example lines 462–465) | The repo's names for a live project that is not in this tree. The comments say that project already owns `Character`, `layeredimage`, and `_kite_sprite`. | EXPLICIT as documentation. The game files are not here. | MEDIUM for "the docs assert this." UNKNOWN for the unread game files. |
| "Jeffrey already has the real Kite on disk. That path is on his Mac only" | `README.md` lines 145–146 | A statement that a PNG exists on a machine that is not this checkout. | EXPLICIT as a sentence. The file was not in the inspection set. | MEDIUM for the sentence. UNKNOWN for the bytes. |

`test_kite_yaml_matches_live_echo_disk_spec` loads this YAML and checks fields inside it (`tests/test_quality_looksheet.py` lines 204–278). The test name says "live echo disk spec." The test body does not read a LOVE32 path.

### 3.2 Shared visual description

`configs/kite_male.yaml` lines 18–22, key `description` (folded scalar). The stored text is one comma-separated string:

`1boy, young man, tan skin, very short dark olive-grey buzz cut, no spikes, no fade, reddish-orange eyes, small silver hoop earrings, chest-up visual novel sprite, solid black background, inked cel-shaded, strong dark linework, dramatic lighting`

| Topic | Clause in that string | Label |
|---|---|---|
| Sex / subject tag | `1boy` | EXPLICIT |
| Age wording | `young man` (no number) | EXPLICIT |
| Skin | `tan skin` | EXPLICIT |
| Hair | `very short dark olive-grey buzz cut`, plus `no spikes`, plus `no fade` | EXPLICIT as clauses of one string. Not separate fields. |
| Eyes | `reddish-orange eyes` | EXPLICIT |
| Accessory | `small silver hoop earrings` | EXPLICIT as a clause. No accessory key. |
| Framing | `chest-up visual novel sprite` | EXPLICIT |
| Backdrop in the prompt | `solid black background` | EXPLICIT in this string |
| Rendering words | `inked cel-shaded`, `strong dark linework`, `dramatic lighting` | EXPLICIT |

`build_pose_prompt` (`matcha/prompts.py` lines 66–98) puts `description` first in the positive prompt for every pose it builds, then outfit text, then either `pose_overrides.prompt` or `pose_expression(pose)`. That is how this string is attached to a pose at generation time. No generated prompt file is stored.

`README.md` lines 309–311 say to keep hair, eyes, and face in `description`. The YAML has no separate face key. A face description is not present beyond what is inside the string above (eyes, and the earring clause). **UNKNOWN** whether any other face facts exist outside this repo.

### 3.3 Values computed only when VNCCS mapping runs

`character_info_from_config` (`matcha/vnccs.py` lines 213–270) splits `description` on commas and fills generator fields. It is not stored on the YAML. `test_kite_identity_maps_to_creator_fields` (tests lines 230–238) runs it on `_kite_cfg()`, whose description is shorter than the YAML (no earrings, no "no spikes" / "no fade", no background or linework clauses). The full YAML is not what that test loads.

Rules in the function, which are EXPLICIT code, applied to the YAML string by reading the function (this audit did not execute it):

| Output key | Rule | Result of reading the rule against the YAML string |
|---|---|---|
| `sex` | `1boy` / `male` / `man` / `guy` → `"male"` (`infer_sex`, lines 193–199) | `"male"` |
| `age` | `young man`, `1boy`, or `man` → integer `22` (`infer_age`, lines 202–206). Comment on line 203 names kite. The YAML has no age number. | `22` is a function result, not a stored Kite field. |
| `hair` | tag containing `hair`, `bang`, `buzz`, or `ponytail` (lines 221–224) | The tag `very short dark olive-grey buzz cut`. `no spikes` and `no fade` do not match that predicate. |
| `eyes` | tag containing `eye` | `reddish-orange eyes` |
| `skin_color` | tag containing `skin`, or the whole tag equal to `tan` / `olive` / `pale` / `fair` / `dark` | `tan skin` |
| `race` | tag equal to `human` / `elf` / `oni` / `demon`, else `"human"` | `"human"` (default). The YAML does not say race. |
| `face` | always `""` (line 260) | empty |
| `body` | always `""` (line 261) | empty |
| `additional_details` | remaining tags, then outfit, then pose prompt or expression | includes `young man`, `no spikes`, `no fade`, `small silver hoop earrings`, the framing and style tags, plus whatever outfit and pose text the caller passes |
| `background_color` | hardcoded `"Green"` (line 267) | `"Green"`, which is not the YAML's `solid black background` |
| `aesthetics` | hardcoded `"masterpiece, visual novel style, cel shaded"` (line 264) | that string, not the YAML's linework sentence |
| `name` | `cfg.name` | `kite_male` |

`pose_data_for` (`matcha/vnccs.py` lines 400–446) adds mesh numbers that are not in the YAML: for `sex == "male"`, `weight` 0.66, `muscle` 0.55, `height` 0.85; `gender` 1; camera `yaw_deg` 0, `pitch_deg` 0, `zoom` 1.4; `skin_type` `"naked"`. These are the same for any male config passed through this function. They are not measurements taken from a Kite image. `pose_plate_png` (lines 361–397) draws a stick figure on a white canvas. For pose key `crossed_arms` or `smoking` the stick figure differs; every other key shares one standing figure.

Label for this subsection: code behavior, not stored canon. Evidence quality **HIGH** for what the function writes, **UNKNOWN** for whether those numbers describe the unseen artwork.

### 3.4 Reference image named, not present

| Item | Where | Label |
|---|---|---|
| `reference: ./refs/kite_male_neutral.png` | `configs/kite_male.yaml` line 88 | EXPLICIT path. |
| File bytes | `refs/` has only `.gitkeep`. `refs/*.png` is gitignored (`.gitignore` lines 10–11). No PNG with this name is in git history. | The path is declared. The image is absent. |
| Comment describing the copy source | YAML lines 80–85; `README.md` lines 143–165; `matcha/vnccs.py` lines 97–111 | EXPLICIT sentences: a file named `kite_male neutral.png` (space) at `/Users/jeffreytse/Desktop/LOVE32/LOVE32/game/images/kite_male neutral.png`, described as 1200×992, transparent, apron/bar; a person copies it by hand into `refs/`. |

`is_love32_project` / `refuse_love32_reference` (`matcha/cli.py` lines 173–198) refuse to read a path with a `love32` component. The YAML reference path does not contain `love32` (`tests/test_quality_looksheet.py` lines 276–278). The Mac path in the comment does. This audit did not read either file.

The word "approved" appears in comments and README (`configs/kite_male.yaml` lines 80–81, `README.md` lines 143–151, `matcha/cli.py` lines 92 and 364–366). There is no approval field, reviewer, timestamp, or file hash.

### 3.5 Generation settings stored on the same YAML

These are keys on the character file. They do not describe hair, face, or clothing.

| Key | Value in `configs/kite_male.yaml` | Lines |
|---|---|---|
| `checkpoint` | `anythingV5PrtRE.safetensors` | 77 |
| `lora` | `null` | 78 |
| `lora_strength` | `0.7` | 79 |
| `width`, `height` | `512`, `512` | 91–92 |
| `steps` | `20` | 93 |
| `seed` | `42` | 94 |
| `consistency_denoise` | `1.0` | 95 |
| `ip_adapter_weight` | `0` | 96 |
| `quality_retries` | `2` | 97 |
| `output_dir` | `./sandbox-kite` | 98 |
| `filename_template` | `{name} {pose}.png` | 15 |

Not set in the file, so `CharacterConfig` defaults apply if the file is loaded: `cfg` 8.0 (line 71), `negative_prompt` lines 60–63, `layered` false, `side_image` false, `color` unset, `resize_max_width` / `resize_max_height` unset. Those defaults are the model, not Kite-specific text.

`output_dir` `./sandbox-kite` is gitignored (`.gitignore` line 9) and the directory is not on disk.

---

## 4. Kite Asset Inventory

No Kite image, CG, side image, reject dump, metrics JSON, or generation log is in the tree or in git history. The table lists named file identities the repo states. It does not invent pixel metadata.

Columns left blank in the source are **UNKNOWN** here. "Outfit" and "pose" for the ten names are the YAML links in §5–§6, not labels read off a file. Expression is not a separate stored attribute (**UNKNOWN** as its own asset type). Side/profile: no Kite side-image flag and no profile filename. `yaw_deg: 0` in `pose_data_for` is a hardcoded camera default, not a file.

| Path as written | Filename | Bytes in repo | Type as stated | Outfit key | Pose token | Expression field | Reference role | Provenance stored | Approval record | Version record |
|---|---|---|---|---|---|---|---|---|---|---|
| `./refs/kite_male_neutral.png` (`reference`, YAML line 88) | `kite_male_neutral.png` | absent | docs call the hand-copy source a transparent sprite; this path itself has no type field | **UNKNOWN** for this path. Comment says the live source is apron/bar (YAML lines 82–83). The filename contains `neutral`, and `neutral` is in `poses`. | filename token `neutral` is **INFERENCE** from the filename plus the pose list, not a key on the reference | none | declared clone source | none (no hash, seed record, or output log) | word "approved" in prose only | none |
| Live path in comments only: `.../LOVE32/LOVE32/game/images/kite_male neutral.png` | `kite_male neutral.png` | not in repo; path not opened | comment: 1200×992, transparent, apron/bar | `apron_bar` is what the comment asserts for this one file | comment does not set a pose key; filename token is `neutral` | none | described as the copy source for `reference` | none in repo | prose "approved" | none |
| `game/images/kite_male neutral.png` (template + pose; README line 325 "ten files on disk") | `kite_male neutral.png` | absent | described as a sprite filename, not a file here | `apron_bar` via `pose_overrides.neutral.family` | `neutral` | none | not the `reference` key (different filename: space vs underscore) | none | none | none |
| same pattern | `kite_male gentle.png` | absent | same | `apron_bar` | `gentle` | none | no | none | none | none |
| same pattern | `kite_male relaxed.png` | absent | same | `home_henley` | `relaxed` | none | no | none | none | none |
| same pattern | `kite_male smoking.png` | absent | same | `home_henley` | `smoking` | none | no | none | none | none |
| same pattern | `kite_male soft.png` | absent | same | `apron_bar` | `soft` | none | no | none | none | none |
| same pattern | `kite_male stressed.png` | absent | same | `apron_bar` | `stressed` | none | no | none | none | none |
| same pattern | `kite_male tired.png` | absent | same | `apron_bar` | `tired` | none | no | none | none | none |
| same pattern | `kite_male warm.png` | absent | same | `apron_bar` | `warm` | none | no | none | none | none |
| same pattern | `kite_male withdrawn.png` | absent | same | `withdrawn_dark` | `withdrawn` | none | no | none | none | none |
| same pattern | `kite_male crossed_arms.png` | absent | comment and README also state a live pixel size 880×1184 for "that file" | `apron_bar` | `crossed_arms` | none | no | none | none | none |

The ten `kite_male <pose>.png` strings are what `filename_template` plus `poses` produce. `render_filename` is asserted for `neutral` and `crossed_arms` only (`tests/test_quality_looksheet.py` lines 266–271). The other eight use the same template and the pose list at YAML lines 23–33. That is EXPLICIT from the template, not from files on disk.

`README.md` lines 325–329 say those ten names are "on disk" in live Echo, that `angry` is not a file, and that live Echo scales `crossed_arms` by 1.39 because that file is 880×1184 while other `kite_male` files are 1200×992. Same sentences are in YAML comments lines 7–12. No image was available to measure.

`README.md` lines 333–335 say accepted poses are written as `<name>_<pose>.png`. `matcha/cli.py` lines 31–34 comment that the space template is for copy-only and is not the generate output name. The write loop at lines 643–649 uses the CLI `--filename-template` if set, otherwise `CharacterConfig.filename_template`, otherwise `{name}_{pose}.png`. This YAML sets `filename_template`, so a run that loaded it would pass the space template into that loop. No output file exists to show which name was actually written. Reject dumps are a different pattern: `output_dir/rejected/<name>_<pose>_seed<seed>.png` plus `.json` (`matcha/cli.py` lines 254–256, `persist_rejection` at `matcha/images.py` lines 298–318). None are present.

`angry` is not a filename. YAML lines 34–35: `pose_aliases.angry` = `stressed`. README line 326 says the same.

Side images, CGs, and expression-only files: none declared for Kite. `side_image` is unset (default false).

`refs/.gitkeep` is a tracked empty file, not an image.

Test files under `tmp_path` such as `kite_male_idle.png` (`tests/test_quality_looksheet.py`) are fixture names inside tests. `idle` is not in this YAML's `poses` (the test asserts that, line 224). They are not assets in the tree.

---

## 5. Kite Outfits

Three outfit families are EXPLICIT keys under `outfit_families` (`configs/kite_male.yaml` lines 36–46). Membership is EXPLICIT under `pose_overrides.*.family` (lines 47–75). `CharacterConfig.outfit_for` ( `matcha/config.py` lines 145–155) returns `pose_overrides[pose].outfit` if that string is set, otherwise the family string. This YAML sets `family` and does not set per-pose `outfit`, so `outfit_for` returns the family text. The test at lines 244–256 checks that.

No directory is an outfit. There is no outfit folder.

| Key | Prose name in comments / README | Clothing text (EXPLICIT) | Poses whose `family` is this key (EXPLICIT) | Assets on disk |
|---|---|---|---|---|
| `apron_bar` | YAML line 48: "Apron / bar — Male New Game bar family". README line 321: "Apron / bar". | lines 37–40: charcoal long-sleeve button shirt buttoned to the collar, dark matching bartender apron with metal buckles and a chest pocket, empty hands, standing square facing camera, no henley, no polo | `neutral`, `warm`, `soft`, `stressed`, `tired`, `gentle`, `crossed_arms` | none in repo |
| `home_henley` | YAML line 64: "Home henley". README line 322: "Home henley". | lines 41–43: olive or charcoal henley or polo shirt, no apron, no bartender outfit, no buckle apron | `relaxed`, `smoking` | none in repo |
| `withdrawn_dark` | YAML line 71: "Withdrawn dark shirt, no apron — withdrawn only". README line 323: "Withdrawn dark shirt". | lines 44–46: oversized dark long-sleeve button shirt, no apron, no bartender outfit, no henley, no polo | `withdrawn` | none in repo |

"Male New Game" appears only in that one comment. Nothing else defines it. **UNKNOWN** beyond the comment.

`home_henley`'s text says "henley or polo". The repo has one family, not two outfit keys and not two files. Whether both garments exist as separate artworks is **UNKNOWN**.

Extra negatives, EXPLICIT, not outfits:

- `smoking.extra_negative` (line 70): `bartender apron, buckle apron, bar counter, standing behind a bar`
- `withdrawn.extra_negative` (line 75): `bartender apron, buckle apron, henley, polo`

`crossed_arms` is `apron_bar`, and the test asserts it is not `withdrawn_dark` (line 257). The family string still contains "empty hands, standing square facing camera". The pose override prompt (lines 63) says "arms crossed over chest, reserved, standing at the bar". Both strings are stored. The file does not say which wording wins inside an image, because there is no image.

On the VNCCS clothes path, `clothes_widget_data` (`matcha/vnccs.py` lines 321–341) sets `costume` from the family key sanitized to letters, digits, `_` and `-`, puts the outfit string in `costume_info.top`, and sets `bottom`, `shoes`, `head`, and `face` to `""`. That is code, used only if that graph is built. It is not an extra outfit declaration in the YAML.

The comment that the live neutral PNG is apron/bar (YAML lines 82–83, README line 149) is the only place a specific existing file is tied to an outfit. That file is not in the repo. Evidence quality **MEDIUM** (repeated prose), not **HIGH** (no structured link from `reference` to `apron_bar`; the `reference` value is only a path).

---

## 6. Kite Poses & Expressions

### How they are represented

EXPLICIT structure: one list, `poses`, of ten strings (YAML lines 23–33). There is no `expressions` key, no pose×expression matrix, and no directory per expression. A name in this list is used as:

- the pose token in `{name} {pose}.png`
- the key in `pose_overrides`
- the argument to `build_pose_prompt` / `pose_expression`
- the VNCCS pose-plate key when the VNCCS backend runs

`POSE_EXPRESSIONS` (`matcha/prompts.py` lines 33–50) is a global table, not stored on the Kite file. `build_pose_prompt` uses `pose_overrides.prompt` when that is non-empty, and otherwise `pose_expression` (lines 91–94). Three Kite poses set `prompt`. For those, the table entry is not what `build_pose_prompt` appends.

`README.md` lines 313–314 say unknown pose names stay plain wording and give ``crossed_arms`` → `crossed arms`. In `POSE_EXPRESSIONS`, `crossed_arms` is a key (line 49), so `pose_expression("crossed_arms")` returns `arms crossed over chest, reserved expression`, not `crossed arms`. The YAML then overrides that with line 63 when the override is passed in. Three different wordings exist in the repo for that name. Which pixels would show is **UNKNOWN**.

### Pose list, override, and table text

| Token | In `poses` | `family` | `pose_overrides.prompt` if any | `POSE_EXPRESSIONS` text (used by `build_pose_prompt` only when override prompt is empty) |
|---|---|---|---|---|
| `neutral` | yes | `apron_bar` | none | `neutral calm expression, relaxed face, standing at ease` |
| `gentle` | yes | `apron_bar` | none | `gentle expression, kind eyes, calm smile` |
| `relaxed` | yes | `home_henley` | none | `relaxed expression, loose shoulders, easy stance` |
| `smoking` | yes | `home_henley` | `seated on a ledge, holding a cigarette, chest-up, relaxed jaw` (line 69) | table has `seated on a ledge, holding a cigarette, relaxed jaw` (prompts.py line 43); the YAML prompt is what `build_pose_prompt` uses |
| `soft` | yes | `apron_bar` | none | `soft gentle expression, quiet eyes, slight smile` |
| `stressed` | yes | `apron_bar` | none | `stressed expression, tense brow, tight mouth` |
| `tired` | yes | `apron_bar` | none | `tired expression, heavy eyelids, weary mouth` |
| `warm` | yes | `apron_bar` | none | `warm soft smile, kind eyes, open posture` |
| `withdrawn` | yes | `withdrawn_dark` | `withdrawn, looking aside, closed-off, distant` (line 74) | table text is not used when this override is passed |
| `crossed_arms` | yes | `apron_bar` | `arms crossed over chest, reserved, standing at the bar` (line 63) | table text is not used when this override is passed |

`test_echo_pose_names_are_in_the_map` (tests lines 149–163) asserts those ten names are keys in `POSE_EXPRESSIONS`. It does not assert the YAML overrides.

Combinations: the file does not list expression separately from pose. There are ten entries, not a product of outfits and faces. **INFERENCE** that some tokens are mostly facial (`gentle`, `soft`, `stressed`, `tired`, `warm`) and some include body (`smoking`, `crossed_arms`) comes only from the English in the prompt strings. The data model does not mark that split. Evidence quality **LOW** for any pose-versus-expression classification.

### Alias

`pose_aliases` (YAML lines 34–35): `angry` → `stressed`. EXPLICIT. `angry` is not in `poses` (test line 225). `parse_poses_flag` (`matcha/cli.py` lines 100–141) resolves an alias to the pose list before generation. `POSE_EXPRESSIONS["angry"]` is `angry expression, furrowed brows` (prompts.py line 39). The character command does not pass the unresolved name `angry` into `build_pose_prompt` when the alias map is applied. Nothing in the repo shows a game script using the word `angry`.

### Stick-figure plates

Only if `--backend vnccs` builds pose data. `pose_plate_png` special-cases the strings `crossed_arms` and `smoking`. Other Kite tokens share one drawing. These plates are generated in memory for the ComfyUI payload. They are not checked-in assets.

---

## 7. Kite Game / Script References

Every `*.rpy` in the repository was searched for `kite`, `Kite`, `LOVE32`, and `Echo`. No matches. `examples/sample-vn/game/script.rpy` and `matcha_characters.rpy` define Sakura placeholders, not Kite.

So there is no in-repo character declaration, dialogue line, label, screen, transform, image statement, or `show` call for Kite. Classified against game files in this repo: **UNKNOWN** (the game files are absent).

What the repo does state about a game that was not opened:

| Statement | Where | Class |
|---|---|---|
| Live project already owns `Character`, `layeredimage`, and `_kite_sprite`. Do not `--deploy` / `--project` into LOVE32. | YAML lines 3–5; `matcha/cli.py` lines 462–465 and the `--copy-only` help text (lines 274–281) | EXPLICIT sentence in Matcha. Game source not in repo, so the dependency inside the game is **UNKNOWN**. |
| Disk name `kite_male <pose>.png` (space). Ren'Py tag `kite_male <pose>`. | YAML lines 7–8; README lines 325–327 | EXPLICIT sentence. No `.rpy` here contains that tag. |
| Live game scales `crossed_arms` by 1.39 because that file is 880×1184 and other kite_male files are 1200×992. Called display, not generate. | YAML lines 8–11; README lines 327–330 and 378–380 | EXPLICIT sentence, repeated. The scale statement is not in a `.rpy` in this repo. **UNKNOWN** as a located script line. Evidence quality of the prose claim: **MEDIUM** (YAML comment and README agree). |
| Copy-only destination example `game/images/kite_male smoking.png` under a project flag pointed at `sandbox-renpy`. | README lines 357–366 | EXPLICIT description of a command. `sandbox-renpy/` is not on disk. Not a located use in a game. |
| `AGENT_CONTEXT.md` lines 45–47: LOVE32 images in `game/images/characters/`, script `game/matcha_characters.rpy` | Does not name Kite | Not a Kite reference. It does not match, and does not contradict by name, the `game/images/kite_male <pose>.png` sentences. Joining them into one Kite path would be an **INFERENCE** this audit does not make. |
| `--images-subdir characters` would place copies under `game/images/characters/` | README lines 369–370; copy-only default subfolder is empty (`matcha/cli.py` around 812–813) | EXPLICIT option. Not set on the Kite YAML. |

`_kite_sprite` occurs as a string the CLI promises not to write (`matcha/cli.py` lines 280, 830, 921; tests assert the stdout contains that phrase). The definition of `_kite_sprite` is not in the repository.

No variable, alias usage, or asset path was found inside a game script.

---

## 8. Asset → Game Relationships

No Kite asset file is in the repository, and no game script that displays Kite is in the repository. For every row in §4, where the picture is used inside a game is **USAGE UNKNOWN**.

The only represented file relationship in code, which is not evidence that a copy happened:

- If `matcha character` is run with this YAML, accepted bytes are written under `output_dir` (`./sandbox-kite`) using `filename_template` unless `--filename-template` is passed (`matcha/cli.py` lines 643–649). That directory is absent.
- If `--copy-only --project <dir>` is also passed, and `<dir>` is not classified as LOVE32, files are copied to `<dir>/game/images/` plus an optional subfolder, using the same template (`copy_only` block, lines 802–831). The command does not write `Character`, `layeredimage`, or `_kite_sprite`.
- If `--deploy` is passed for a path `is_love32_project` accepts as LOVE32, the command exits before write (lines 459–468).
- `--deploy` on a non-LOVE32 project writes images and replaces a marked block in `game/matcha_characters.rpy` (`FilesystemDeployer`, `RenPyFormatter.script_block`). Nothing in the tree is the result of that for Kite.

`reference: ./refs/kite_male_neutral.png` is a path on the config. It is not linked by a key to a scene, a script line, or a hash. The comments say it should be a hand copy of one live neutral file. That link is prose. Evidence quality **MEDIUM** for the prose, **UNKNOWN** for use in a game.

---

## 9. Matcha's Current Model

Current behavior of the code on `main`. Not a description of unused designs.

| Topic | What the code does now | Where |
|---|---|---|
| Character | Loads one YAML into `CharacterConfig`: `name`, `description`, `poses`, `display_name`, `color`, `layered`, `side_image`, filename template, reference path, and generator knobs. `MatchaConfig` exists (`matcha/config.py` lines 159–163) and is not referenced by the CLI. | `CharacterConfig`; `matcha character` in `matcha/cli.py` |
| Outfit | `outfit_families` dict of strings; `pose_overrides[pose].family` or `.outfit`. `outfit_for` resolves one string. No outfit id on an output file. | `matcha/config.py` |
| Pose | List of strings. `--poses` selects a subset. Aliases map to list entries via `parse_poses_flag`. | YAML `poses`, `pose_aliases`; `matcha/cli.py` `parse_poses_flag` |
| Expression | No field. Wording comes from `pose_overrides.prompt` or the global `POSE_EXPRESSIONS` table. | `matcha/prompts.py` |
| Reference | Optional path. CLI flag `--reference` / `--vnccs-ref` overrides YAML. LOVE32 paths are refused before read. On `--backend vnccs`, an existing file is uploaded and passed as the cloner source image. On `--backend txt2img` (the default), a YAML `reference` is printed as unused (`matcha/cli.py` lines 452–457). Setting `reference` does not switch the backend. | `resolve_clone_reference`; `ComfyUIGenerator.upload_image`; `vnccs.cloner_widget_data` |
| Generated assets | Each accepted PNG is written under `output_dir` when generation runs. Skip if that path exists and passes `assert_usable_image`, unless `--force`. | `matcha/cli.py` lines 642–770 |
| Provenance | Not written on success. A reject sidecar can contain `rejected_at`, metrics, and the `extra` dict the CLI passes: `character`, `pose`, `seed`, `attempt`, `reason` (`matcha/cli.py` inside the quality-error handler; `persist_rejection`). No success-side JSON, no prompt archive, no file hash. | `matcha/images.py` lines 298–318 |
| Approvals | No status field and no stored decision. "Approved" is a word in comments about a hand-copied PNG. | comments only |
| Deployment | `--deploy` copies images and writes/replaces one character's block in `game/matcha_characters.rpy`. `--copy-only` copies images and does not write that block. LOVE32 paths are refused for both. | `FilesystemDeployer`; `is_love32_project` |
| Ren'Py relationships | The formatter can emit `define`, flat `image` lines or a `layeredimage` whose attributes are whole sprites, and optional `image side` lines. It does not read existing scripts. It does not parse `show` statements. Kite's YAML leaves `layered` and `side_image` at defaults (false). | `matcha/formatters/renpy.py` `script_block` |
| Game scripts | Not read. Not searched for image names. | no such code path |
| Dependencies | Alias map and outfit-family keys exist on the config. Nothing records "this script line depends on this file." | `pose_aliases`, `pose_overrides` |
| Versions | Package `__version__` is `0.1.0` (`matcha/__init__.py`). No per-asset version. | that constant only |
| Stale assets | Resume treats an existing PNG as skippable if the quality gate accepts it. The gate does not compare the file to `description`, outfit text, or `reference`. There is no stale state. | `assert_usable_image` in the skip branch |
| Regeneration | `--force`, or a missing/failed file, queues ComfyUI again (`txt2img` graph or VNCCS graph). There is no record of a previous generation to compare. | `matcha/cli.py` character loop; `matcha/generators/comfyui.py`; `vnccs.generate_pose` |
| Validation | `assert_usable_image` rejects empty, undecodable, near-black, and smear/static-band PNGs using luma and edge statistics. It does not check identity, outfit, or expression. | `matcha/images.py` |

---

## 10. Matcha → Kite Coverage

"Matcha" means data or code in this repository. "Project" means Kite's game tree. That tree was not accessible. `examples/sample-vn` is not that project. "Relationship represented" means a structured link inside this repository, not a sentence about an unread game.

| Category | Present in Matcha? | Present in project? | Relationship represented? | Evidence quality |
|---|---|---|---|---|
| Character id `kite_male` and display name `Kite` | Yes, YAML keys | Not in this repo | Id is the filename prefix via `filename_template`. No link to a game object | HIGH for the keys. UNKNOWN for the game object |
| Shared description (hair, eyes, skin, earrings, framing) | Yes, one string | Not in this repo | Prepended to prompts by `build_pose_prompt`. Not stored on an asset | HIGH for the string. UNKNOWN for pixels |
| Outfit families and pose membership | Yes, three keys and ten `family` entries | Not in this repo | `family` → family string, via `outfit_for`. No link from family to a file hash or a script line | HIGH for the YAML graph. UNKNOWN for artwork |
| Pose tokens | Yes, ten strings | Not in this repo | Token is the `{pose}` in the filename template. Files absent | HIGH for the list |
| Expression as its own attribute | No field | Not in this repo | Only prompt wording | HIGH that the field is absent |
| Alias `angry` → `stressed` | Yes | No script in repo uses it | `parse_poses_flag` resolves it before generate. No game edge | HIGH for the map. UNKNOWN for game use |
| Reference path | Key present; PNG absent | Commented live path not opened | Prose says the ref is a hand copy of one live neutral file. No id linking `reference` to `apron_bar` | MEDIUM for the prose. UNKNOWN for bytes |
| Asset files | Names can be computed; zero image files | Not opened | No file to attach to a `show` or a declaration | UNKNOWN for usage |
| Scene | No scene object | No Kite scene file here | none | UNKNOWN |
| Script | No Kite `.rpy` | Not in repo | none | UNKNOWN |
| Dependency script → asset | Not stored | Not readable here | none | UNKNOWN |
| Generation record | Settings on the YAML; no output log | n/a | seed/checkpoint are config, not a record of a run | HIGH that no run record exists |
| Validation record | Quality gate exists; no Kite reject file | n/a | Gate does not store outfit or identity checks | HIGH for what the gate measures |
| Approval | Prose only | Not readable here | No record tied to a hash | LOW for the word "approved" |
| Version | No per-asset version | Not readable here | none | HIGH that Matcha has no asset version for Kite |
| Ren'Py `Character` / `layeredimage` / `_kite_sprite` | CLI names them as things it must not write | Claimed to exist in the live game; source not here | Refusal path only | MEDIUM for the refusal text. UNKNOWN for the game definitions |
| Pixel sizes 1200×992 and 880×1184, scale 1.39 | Comment and README only | Not measured here | Not a field on `CharacterConfig` | MEDIUM for the repeated sentence. UNKNOWN for the files |
| Side image / CG | Not set / not declared | Not in repo | none | HIGH that the YAML does not declare them |

---

## 11. Existing Information Relevant to Design Changes

This section lists information that is already in the repository for three lenses. It does not select files to regenerate.

### Hairstyle

Information that mentions hair:

- The `description` clauses `very short dark olive-grey buzz cut`, `no spikes`, and `no fade` (`configs/kite_male.yaml` lines 18–22). EXPLICIT.
- `README.md` lines 309–311, which say hair belongs in `description`. EXPLICIT instruction, not a second hair value.
- `character_info_from_config` hair predicate (`matcha/vnccs.py` lines 221–224): a tag containing `buzz` is copied into the `hair` field. `no spikes` and `no fade` do not match that predicate and would remain in `additional_details` if the function were applied. The full YAML is not the fixture in `test_kite_identity_maps_to_creator_fields`.
- `build_pose_prompt` places the whole `description`, including those clauses, at the start of each pose prompt it builds (`matcha/prompts.py` lines 88–98).
- No per-pose hair override. No hair key. No asset metadata, filename, hash, or approval record contains a hairstyle. The reference PNG that comments call the identity source is not in the tree, so its pixels cannot be inspected. No generation record ties an output file to this string.

Not present: a list of images indexed by hair, a fingerprint of the current hair, or a script citation.

### Outfit

Information that mentions clothing:

- The three `outfit_families` strings and the `family` on each of the ten poses (§5). EXPLICIT.
- `outfit_for` returns that family string for each of those poses. EXPLICIT code.
- `smoking` and `withdrawn` `extra_negative` strings name apron, henley, and polo items to negate. EXPLICIT.
- `crossed_arms` carries both the apron family string (including "empty hands, standing square facing camera") and the override prompt "arms crossed over chest... standing at the bar". EXPLICIT. Both are inputs available to a prompt builder.
- `home_henley` is a single string that says "henley or polo". EXPLICIT wording. Separate assets for henley versus polo are not in the repo.
- README table lines 319–323 restates the three families and their pose names.
- `clothes_widget_data` would put the resolved outfit string into `costume_info.top` and the family key into `costume` if that function were called.
- `build_pose_prompt` appends the outfit string and, when an outfit string is present, does not append the phrase `same outfit` (`matcha/prompts.py` lines 89–97).
- Comments say the unseen live neutral file is apron/bar, and that `crossed_arms` is apron/bar rather than withdrawn. EXPLICIT comments. The files are not here.
- No filename in the ten-name pattern encodes the outfit key. Outfit is not recoverable from those filenames alone. Linking a name to an outfit requires the YAML `family` map. That map is present. Image contents are not. Script usage is not. Hashes and approval records are not.

### Small hair accessory

Information that mentions an accessory:

- The clause `small silver hoop earrings` inside `description` (YAML lines 19–20). EXPLICIT. It is not its own key.
- No pose override, outfit string, filename, or alias contains "earring", "hoop", or "accessory".
- `character_info_from_config` does not have an accessory field. A tag that is not hair, eyes, skin, or race is appended to `additional_details` ( `matcha/vnccs.py` lines 231–262). The earring clause does not contain `hair`, `buzz`, `eye`, or `skin`. `clothes_widget_data` sets `costume_info.head` and `costume_info.face` to empty strings (lines 333–339).
- `build_pose_prompt` would include the clause because it includes the whole `description`.
- No reference crop, no asset, no hash, no approval, and no script line names this accessory. The reference image that might show it is not in the repository.

---

## 12. Information Gaps

### Explicitly missing

Absent from the tree, not merely unread inside a file that exists:

- All Kite PNG bytes, including `refs/kite_male_neutral.png` and anything under `sandbox-kite/` or `output/`.
- The LOVE32 / Echo project: scripts, image declarations, `_kite_sprite`, layeredimage, and the files the comments describe.
- A success-side generation record (prompt used, seed actually used, model, time, output hash).
- An approval record bound to a file.
- A per-asset version.
- A stored link from `reference` to an outfit key or a file hash.
- Separate fields for expression, face, body, accessory, age (as a number), or race.
- Kite side images, CGs, and profile images.
- Any `.rpy` occurrence of Kite.

### Potentially recoverable

Not in git. Named by the docs as locations outside this checkout. This audit did not open them, so their contents stay unknown. They are recoverable only from those locations, not from this repository:

- The Mac path written in `README.md` lines 148–149 and `configs/kite_male.yaml` lines 82–83, if that file still exists there.
- A hand copy at `refs/kite_male_neutral.png` on a machine where someone made one. `.gitignore` would keep it untracked. It is not here.
- `sandbox-kite/` on a machine where generation was run. Gitignored. Not here.
- Pixel sizes and the 1.39 scale, if the live image files and the live script are opened. They are not in this git history (`git log --all` shows no Kite PNG path).

### Unknown

- Whether the live files match the YAML comments (names, counts, pixel sizes, apron/bar contents, transparency).
- Whether a game script uses `angry`, `kite_male <pose>`, or `_kite_sprite`, and in which labels.
- Whether `game/images/` or `game/images/characters/` is where those files actually sit. Both locations are mentioned in different documents; only the Kite-specific sentences name `game/images/kite_male <pose>.png`. `AGENT_CONTEXT.md` does not name Kite.
- What the absent reference image depicts.
- Whether "henley or polo" corresponds to one garment or two.
- Whether any output was ever accepted for Kite. Local notes in other docs talk about Sakura and about sandbox pose counts. They do not include Kite output files.
- Any fact about Kite that is not written in the sources in §2.

---

## 13. Evidence Limitations

- One YAML file is the structured source. README text mostly repeats it. Agreement between those two is not independent measurement.
- Comments claim a live disk layout. The test named `test_kite_yaml_matches_live_echo_disk_spec` checks the YAML only.
- No visual inspection was possible. Filename tokens were not treated as outfits or expressions except where a YAML key uses the same token.
- `POSE_EXPRESSIONS` is global. Several entries (`idle`, `happy`, `sad`, `surprised`, `embarrassed`, `angry`) are not Kite pose-list entries. `angry`'s table row is not the alias target's prompt.
- `_kite_cfg()` in the VNCCS tests is a reduced config. Assertions there are not assertions about every clause of `configs/kite_male.yaml`.
- `character_info_from_config` field splits for the full description were read off the function. They were not executed in this audit.
- `AGENT_CONTEXT.md` still describes LOVE32 as the image and script paths for generated Matcha output. The Kite YAML and the CLI refuse writing that project and describe a different filename pattern. Both texts are in the repo. Neither was checked against the game.
- Git ignorance of `refs/*.png` and `sandbox-kite/` means a local copy could exist on another machine and still be invisible to this clone. This clone does not contain them.
- Sample-vn GUI PNGs are Ren'Py chrome. They were not treated as Kite assets.

---

## 14. Audit Conclusions

The repository's structured Kite record is `configs/kite_male.yaml`: id `kite_male`, display name `Kite`, one description string, ten pose tokens, one alias (`angry` → `stressed`), three outfit-family strings, a `family` on each pose, three pose prompt overrides, two extra-negative strings, a filename template `{name} {pose}.png`, a reference path, and generator settings. `outfit_for` and `parse_poses_flag` are code that read those keys. `build_pose_prompt` attaches the description and the resolved outfit string to pose wording. That is the explicit relationship set.

No Kite image is in the repository, including the declared reference. No Kite game script, image declaration, scene, show call, approval record, file hash, generation log, or asset version is in the repository. The live project named in comments was not accessible. Usage of any Kite picture inside a game cannot be established from this checkout.

Pixel sizes, the 1.39 scale, transparency, and "approved" are prose, repeated in the YAML header and the README, not fields and not measured files. Age `22`, VNCCS `hair` / `eyes` / `skin_color` splits, empty `face` and `body`, green `background_color`, and male mesh constants exist only as function outputs or literals in `matcha/vnccs.py`, not as Kite YAML keys. Pose versus expression is not modeled; splitting the ten tokens that way is an inference from prompt English. Outfit membership of the ten pose tokens is explicit in `pose_overrides`. Outfit membership of real image bytes is not establishable here, because the bytes are absent. The earring clause exists only inside `description`.
