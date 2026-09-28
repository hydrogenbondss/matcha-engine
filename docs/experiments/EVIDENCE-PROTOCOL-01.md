# Evidence Protocol #1: Kite static-asset impact

This protocol defines how Experiment #1 is scored against the frozen Kite fixture. It does not run the experiment, and it assigns no ground-truth status to any item.

## 1. Purpose and non-goals

**Purpose.** Fix, before any experiment runs, how ground truth and Matcha output are recorded for this question: "If Kite's canonical visual design changes, which existing production assets and game references are actually affected?" The question is asked separately for each test case in §3, against the frozen fixture in §2.

**Non-goals.** This document does not:
- run the experiment or produce any result;
- assign a ground-truth status to any fixture item;
- measure time or effort;
- judge strategy, usefulness or market position;
- change the fixture.

## 2. Frozen baseline

- **The baseline is the frozen fixture** `fixtures/kite-production/` at matcha-engine commit `c1364f48ff92b248b3cd2aa7729c6014648008aa`. It represents LOVE32 Git HEAD `f4816ca90c9a15bc927a63df5148050199ad2842`.
- **The dirty LOVE32 working tree is not the baseline.** Nothing in the working tree after that HEAD is in scope. That includes deleted files, untracked backups and later edits.
- **Five sprites are the frozen committed versions.** `kite_male_neutral`, `kite_male_relaxed`, `kite_male_smoking`, `kite_male_soft` and `kite_male_tired` are deleted in the LOVE32 working tree but present at HEAD. For this protocol they are the frozen committed versions held in the fixture:
  - `reference/kite_male_neutral.png`
  - `assets/kite_male_relaxed.png`
  - `assets/kite_male_smoking.png`
  - `assets/kite_male_soft.png`
  - `assets/kite_male_tired.png`
- **A working-tree difference is not uncertainty.** An item is never marked `REVIEW_REQUIRED` because the LOVE32 working tree differs from HEAD. That difference is a documented source-state limitation (§12), not experimental uncertainty.
- **Two neutral images, kept separate on purpose:**
  - `reference/kite_male_neutral.png` is the frozen production-baseline asset.
  - `reference/kite_male_bust_neutral_credits_v19g.png` is approved-reference evidence.
  - They differ. That difference is recorded as a historical inconsistency (§12). It does not by itself make any test case `REVIEW_REQUIRED`.
- **What ground truth answers:** each test case is answered against the frozen production baseline. v19g is used as canonical-reference evidence where it is relevant.

## 3. Test cases

There are exactly three test cases:

- **A.** Major hairstyle change.
- **B.** Materially different outfit.
- **C.** Small ear-accessory change.

No further detail of the changes is defined here.

*Fixture context only. This does not define the changes:*
- `metadata/KITE_ASSET_MASTERLIST.md` video prompts describe male Kite with a "shaved head".
- Comments in `game/route_kite.rpy` link some plates to an apron, a henley or a dark shirt (for example lines 16, 747, 1575, 1621, 1624, 1739, 2006).
- In the fixture, earrings are mentioned only for female Kite (`KITE_ASSET_MASTERLIST.md` prompts for the female scenes). No fixture file mentions an ear accessory for male Kite.

## 4. Scoring scope

Experiment #1 scores only two item types: `ASSET` and `CODE`. Everything else in the fixture is evidence-only.

### 4.1 Scored units

**Frozen Kite asset items (item type `ASSET`), 15 items:**
- `reference/kite_male_neutral.png`
- `assets/kite_male_gentle.png`
- `assets/kite_male_stressed.png`
- `assets/kite_male_warm.png`
- `assets/kite_male_withdrawn.png`
- `assets/kite_male_crossed_arms.png`
- `assets/kite_male_relaxed.png`
- `assets/kite_male_smoking.png`
- `assets/kite_male_soft.png`
- `assets/kite_male_tired.png`
- `assets/kite_male_dark.png`
- `assets/kite_male_dark_relaxed.png`
- `assets/kite_male_dark_withdrawn.png`
- `assets/side_kite_male.png`
- `assets/kite_tattoo.png`

**Frozen relevant game-source items (item type `CODE`), 11 items:**
- Full copies:
  - `game/route_kite.rpy`
  - `game/li_sprite_normalization.rpy`
  - `game/side_portraits.rpy`
  - `game/characters.rpy`
- Excerpts (provisional handling, see §4.3):
  - `game/credits.rpy.excerpt.txt`
  - `game/screens.rpy.excerpt.txt`
  - `game/route_select.rpy.excerpt.txt`
  - `game/route_friendships.rpy.excerpt.txt`
  - `game/route_neo.rpy.excerpt.txt`
  - `game/minigames.rpy.excerpt.txt`
  - `game/options.rpy.excerpt.txt`

### 4.2 Evidence-only items

These items are never classified and never receive an experiment status:
- `metadata/fixture-manifest.json` (manifest and provenance)
- `metadata/INSTALL_REPORT_MALEKITE_V19G.json` (install report)
- `metadata/KITE_ASSET_MASTERLIST.md` (masterlist)
- `reference/kite_male_bust_neutral_credits_v19g.png` (approved-reference evidence, §2)
- `reference/KEEP_kite_male.png` (provisional, see §4.3)
- `docs/experiments/KITE-FIXTURE-01.md` (provenance record)

Evidence-only items can be read and cited during ground-truth review and during evaluation of Matcha's output. They can change how a scored item is classified. They are never themselves scored as an affected or unaffected production unit.

### 4.3 Provisional scope choices

These choices are provisional and are listed again under "Open points for Jeffrey".

- **`reference/KEEP_kite_male.png` is evidence-only.** It is a review-folder copy of the approved plate as installed on 2026-09-09. It is not a production file at the baseline HEAD, so it is treated as canonical-reference evidence alongside v19g.
- **Excerpt files are scored as `CODE` for their excerpted lines only.**
  - Each excerpt stands for its original source file, but only for the line ranges stated in its header.
  - Its `file_status` describes those lines only.
  - References outside the excerpted ranges are out of scope and are not inferred.
  - The excerpt's limitation is cited in `evidence`.
- **`game/options.rpy.excerpt.txt` is scored as `CODE`,** like the other game-source items, even though its lines are build-packaging rules rather than asset references.
- **Relationships are recorded only against scored `ASSET` items.** A code relationship is recorded only when the related asset is one of the 15 scored asset items. References to assets outside the fixture are not recorded as relationships; §12 lists them. Examples: female Kite images, `namebox_kite.png`, `bg/kite_apartment.png`, videos.

## 5. Item types

- **Assign the item type first.** Every scored item gets its item type before any status: `ASSET` or `CODE`.
- **METADATA is evidence-only.** `METADATA` is not a scored item type in Experiment #1. Metadata files may be used as evidence during ground-truth review and Matcha evaluation. They are never themselves classified as `ASSET_ACTION`, `CODE_ACTION`, `DOWNSTREAM_USAGE`, `UNAFFECTED` or `REVIEW_REQUIRED`.
- **Asset and code statuses never mix.** Asset items never receive `CODE_ACTION` or `DOWNSTREAM_USAGE`. Code items never receive `ASSET_ACTION`.

## 6. Asset status

Each scored `ASSET` item receives exactly one status per test case:

- **`ASSET_ACTION`:** The available evidence establishes that the specified design change changes the visual content that this asset depicts.
- **`UNAFFECTED`:** The available evidence establishes that the specified design change does not change the visual content that this asset depicts.
- **`REVIEW_REQUIRED`:** The available evidence is insufficient to determine whether the specified design change affects this asset.

In short:
- established affected → `ASSET_ACTION`
- established unaffected → `UNAFFECTED`
- cannot determine → `REVIEW_REQUIRED`

`ASSET_ACTION` does not mean "might need review". It is used only when the effect is established.

## 7. Code status

Code status has two layers: the relationship level and the file level.

### 7.1 Relationship level

For each relevant asset/code relationship in a scored `CODE` item (see §4.3 for which relationships count), record exactly one of:

- **`CODE_ACTION`:** Because of the specified design change, this reference requires the source code itself to be edited.
- **`DOWNSTREAM_USAGE`:** This source references an affected asset, but the source remains valid and needs no edit just because the asset changed.
- **`UNAFFECTED`:** The specified design change has no effect on this reference. The related asset is unaffected, and no edit is needed.
- **`REVIEW_REQUIRED`:** The available evidence is insufficient to determine whether this reference requires an edit or points to an affected asset.

Example:

```renpy
show kite_male neutral
```

- If `kite_male_neutral.png` changes but the image identifier stays valid: `DOWNSTREAM_USAGE`.
- If the source must change the identifier, path, declaration, transform or other code because of the design change: `CODE_ACTION`.

### 7.2 File level

Each scored `CODE` item receives exactly one primary `file_status` per test case, derived from its relationships:

- **Precedence:** `CODE_ACTION` > `DOWNSTREAM_USAGE` > `UNAFFECTED`.
- **When `REVIEW_REQUIRED` applies:** only when no higher-priority definite status exists and the evidence prevents classification.
- **An unresolved relationship never downgrades a definite edit.** If any relationship is `CODE_ACTION`, the file is `CODE_ACTION`, even if other relationships are `REVIEW_REQUIRED`.
- **Unresolved relationships stay visible.** They are still recorded individually as `REVIEW_REQUIRED` at the relationship level.

Example: a `.rpy` file has (1) a reference that definitely requires editing, which is `CODE_ACTION`, and (2) another reference whose impact cannot be determined, which is `REVIEW_REQUIRED`. The file's primary status is `CODE_ACTION`. The second relationship is still listed separately as `REVIEW_REQUIRED`.

A code file with no relevant relationship to any scored asset is `UNAFFECTED` at file level.

## 8. Asset/code separation

- **Status is not a dependency record.** Do not encode the whole dependency relationship in a status.
  - An asset's `status` answers only whether the asset's depicted content changes.
  - A code file's `file_status` answers only whether that file needs an edit or references an affected asset.
  - Relationships are recorded separately, under `relationships` in the code output (§11).
- **Code references do not change asset statuses.** That a code file references an affected asset does not change the asset's own status.
- **Asset statuses do not force code edits.** An asset's `ASSET_ACTION` does not by itself make any code file `CODE_ACTION`.

## 9. Meaning of REVIEW_REQUIRED

- **Asset items:** `REVIEW_REQUIRED` means only that the available evidence is insufficient to determine whether the specified design change affects this asset.
- **Code items and relationships:** it means only that the available evidence is insufficient to determine whether the source requires editing, or whether it references an affected asset.

It does NOT mean:
- low confidence;
- an inconvenient result;
- that Matcha is unsure despite sufficient evidence;
- "probably affected";
- that the LOVE32 working tree differs from HEAD (§2, §12);
- that the approved v19g image differs from the frozen production neutral (§2, §12).

Use it only when the evidence genuinely cannot establish the answer.

## 10. Ground-truth rule

**Classify by required action.** Ground truth classifies what action is actually required under the specific test case. It does not classify by ownership or dependency.

- **Assets:** "Does the specified visual change alter what this asset depicts?"
- **Code:** "Does the specified visual change require editing this source code?" If yes: `CODE_ACTION`.
- **Code, separately:** "Does this source reference an affected asset even though the source itself remains valid?" If yes: `DOWNSTREAM_USAGE`.

**Non-reasons.** Do not classify an item as affected merely because:
- it belongs to Kite;
- it mentions Kite;
- it references Kite;
- it is downstream of Kite;
- it could conceivably contain the changed feature.

**Per test case.** Every status is tied to one specific test case (A, B or C). Each item is classified separately for each test case.

**Baseline and evidence.**
- Ground truth is set against the frozen production baseline (§2).
- Evidence-only items (§4.2), including v19g as canonical-reference evidence, may inform a classification.
- Ground truth is not set by this document.

## 11. Output contract

Ground truth and Matcha output both use the same contract, once per test case. Only the status values below are allowed.

**Allowed status vocabulary** (no others):
- ASSET: `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.
- CODE: `CODE_ACTION`, `DOWNSTREAM_USAGE`, `UNAFFECTED`, `REVIEW_REQUIRED`.

**For each scored asset:**

```text
item_type: ASSET
asset/path
file_status
status
reason
evidence
game_usage
```

**For each scored code file:**

```text
item_type: CODE
source/path
file_status
reason
evidence
relationships:
  - related_asset
  - relationship_status
  - reason
  - evidence
```

**Notes on use:**
- Paths are fixture paths as listed in §4.1.
- `related_asset` is one of the 15 scored asset paths.
- Asset `game_usage` may cite the manifest's `game_usage` references.
- The code contract carries both the file-level classification and the relationship-level evidence, so uncertainty is not hidden.
- The asset contract lists both `file_status` and `status`. It is kept exactly as given.
  - Provisional handling until Jeffrey clarifies: both fields use the ASSET vocabulary and carry the same value.
- Evidence-only items (§4.2) never appear as scored entries. They may be cited inside `evidence`.

## 12. Documented source-state limitations and historical inconsistencies

These are recorded facts about the source. None of them is by itself a reason for `REVIEW_REQUIRED`.

- **Working tree vs HEAD.** At fixture capture the LOVE32 working tree had five `kite_male` plates deleted (unstaged), plus other unrelated changes. The fixture holds the committed HEAD versions, and they are the baseline.
  - In the working tree, the code shows `side_kite_male.png` in place of a missing plate (`li_sprite_normalization.rpy:268-290`).
  - That fallback does not occur at the baseline, because the plates exist there.
- **Approved reference vs production neutral.**
  - The v19g plate was approved on 2026-09-09 (`INSTALL_REPORT_MALEKITE_V19G.json`) and installed. `KEEP_kite_male.png` is the copy saved at install.
  - The HEAD neutral (`reference/kite_male_neutral.png`) differs from both. No approval for the later change appears in the fixture.
- **YAML vs production.**
  - `configs/kite_male.yaml` says `angry` aliases `stressed`. Production maps `angry` to the neutral file (`route_kite.rpy:26`).
  - The YAML's comments on space-separated filenames and mixed canvases do not match the fixture: underscore filenames, all 928×1232 plates.
  - The YAML is not evidence for ground truth unless a fixture item supports it.
- **Unreferenced plates.** `assets/kite_male_dark*.png` ship in `game/images` but no reference was found in the searched `.rpy` source.
- **Declared but not shown.** `assets/kite_tattoo.png` is declared (`route_kite.rpy:10`) but no `show` statement was found.
- **Excerpt coverage.** The seven excerpt files contain only their stated line ranges (§4.3).
- **Out of fixture.** None of the following is in the fixture, so none can be scored:
  - Kite videos. Content was not verified. `kite_good_male_ending.mp4` is referenced but missing.
  - Female Kite assets.
  - `namebox_kite.png`, `bg/kite_apartment.png`, audio.
  - Backup and review folders.
  - Their references are listed in `docs/experiments/KITE-FIXTURE-01.md` §4.
- **Outfit per plate.** The fixture manifest records outfit as UNKNOWN for every asset. Comments in `route_kite.rpy` are the only in-fixture statements linking plates to clothing.

## 13. Freeze rule

- After this commit, neither this protocol nor the fixture (`fixtures/kite-production/`) may be changed during Evidence Protocol #1 or the controlled experiment.
- The fixture freeze rule in `docs/experiments/KITE-FIXTURE-01.md` §10 still applies.
- Any later change to this protocol requires a new, separately committed version before any scoring takes place.

## Open points for Jeffrey

Each point below has provisional handling in this document. None is settled by the rules given.

1. **`reference/KEEP_kite_male.png`:** provisionally evidence-only, not a scored asset (§4.2, §4.3).
2. **Excerpt files** (`game/*.excerpt.txt`, 7 files): provisionally scored as `CODE` for their excerpted line ranges only. References outside those ranges are out of scope and not inferred (§4.3).
3. **`game/options.rpy.excerpt.txt`:** provisionally scored as `CODE`, even though it holds build-packaging rules rather than asset references (§4.3).
4. **Relationship granularity:** provisionally, relationships are recorded only against the 15 scored asset items. How many relationships to record per file (per reference line, or per related asset with all lines cited in `evidence`) is not fixed by the rules. Provisionally: one relationship per related asset, with all line references in `evidence` (§4.3, §7.1).
5. **Asset contract `file_status` vs `status`:** kept exactly as given. Provisionally both carry the same ASSET-vocabulary value (§11).
6. **Code file with no relevant relationship:** provisionally `UNAFFECTED` at file level (§7.2).
