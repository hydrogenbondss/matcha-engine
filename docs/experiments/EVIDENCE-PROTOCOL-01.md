# Evidence Protocol #1: Kite static-asset impact

Status: **frozen methodology.** This protocol contains no open decisions. The previous protocol contained exactly six provisional decisions; all six are now permanently resolved (§3).

Path convention: unless stated otherwise, paths are relative to the fixture root `fixtures/kite-production/` (for example `assets/kite_male_warm.png`, `game/route_kite.rpy`). Repository paths such as `docs/experiments/KITE-FIXTURE-01.md` are relative to the matcha-engine repository root.

## 1. Base and immutability

- This protocol's branch is based on `matcha-2-kite-fixture` at commit `c1364f48ff92b248b3cd2aa7729c6014648008aa`.
- The fixture `fixtures/kite-production/` is byte-identical to that commit.
- This protocol does not alter `fixtures/kite-production/`, and nothing done under it may alter the fixture.

## 2. Purpose

Evidence Protocol #1 defines the exact methodology for the later controlled experiment:

> Given a specific canonical visual change to Kite, can Matcha correctly identify which existing static production assets require action, while avoiding unnecessary work?

This document is methodology only. It does NOT:

- run the experiment;
- assign ground-truth classifications;
- measure human or Matcha time;
- modify the fixture;
- modify Matcha production code;
- generate assets;
- connect to ComfyUI;
- access LOVE32;
- make a product or strategy judgment.

## 3. The six original decisions: all resolved

### Decision 1: KEEP asset

- `reference/KEEP_kite_male.png` is **evidence-only**.
- It is not a scored production asset, because it is a review-folder copy documenting the approved 2026-09-09 install, not the frozen production-baseline file at LOVE32 HEAD.
- The scored ASSET set is exactly: the 14 files under `fixtures/kite-production/assets/` plus `reference/kite_male_neutral.png` = **15 scored ASSET units** (listed in §4.1).
- `reference/KEEP_kite_male.png` may be cited as canonical-reference evidence.

### Decision 2: Excerpts

- The five excerpts `game/credits.rpy.excerpt.txt`, `game/route_select.rpy.excerpt.txt`, `game/route_friendships.rpy.excerpt.txt`, `game/route_neo.rpy.excerpt.txt` and `game/minigames.rpy.excerpt.txt` are **eligible scored CODE units**, because they contain direct relationships to scored static assets.
- Their scope is strictly limited to the source line ranges stated in each excerpt header.
- An excerpt:
  - represents only those stated lines;
  - does not establish anything about the rest of the original source file;
  - retains the original source path;
  - retains the original full-file SHA-256;
  - retains the stated source line ranges;
  - retains its stated limitation.

Excerpt headers as frozen in the fixture:

| Excerpt | Original source path (LOVE32-relative) | Original full-file SHA-256 | Original total lines | Stated line ranges | Stated limitation (summary) |
|---|---|---|---|---|---|
| `game/credits.rpy.excerpt.txt` | `game/credits.rpy` | `e77b031c7c5f109552170736822afdd7d8f44200b0bfcf7b986ff0ae31270f88` | 1165 | 106-120, 164-176, 668-678 | Kite credits-polaroid sprite resolver, its caller, and the credits hide statement only |
| `game/route_select.rpy.excerpt.txt` | `game/route_select.rpy` | `5507133b10af54513e5ec82996db02c392a7618397a2aee2ab26c1d2c51bc0a5` | 609 | 54-64 | Kite route-card portrait selection only |
| `game/route_friendships.rpy.excerpt.txt` | `game/route_friendships.rpy` | `1305bd6ee6e64bb37de2e833b257920587f8e2c675d07185be16d80077978434` | 976 | 59-63, 157-160, 220-223, 246-249, 307-310, 343-346, 507-510, 650-653, 931-934 | show/hide `kite_male` lines with 1-3 lines of context only |
| `game/route_neo.rpy.excerpt.txt` | `game/route_neo.rpy` | `a4f4553031b1fd1ace7979bdfd0329a829b4c93a74956ebf7714f12af8e30877` | 3621 | 2610-2615, 2670-2673 | The single Kite cameo show/hide in Neo's route only |
| `game/minigames.rpy.excerpt.txt` | `game/minigames.rpy` | `32633c9dc7b31e9c3c65d588bd7d3dfbeee0a41cad7eee3ee14f51bb5d2eb089` | 6542 | 5202-5212 | Cocktail Time gallery entry referencing `kite_male relaxed` only |

The full limitation text is the `# limitation:` line in each excerpt header; that text governs.

### Decision 3: `options.rpy`

- `game/options.rpy.excerpt.txt` is **evidence-only**, not scored CODE.
- Reason: its excerpt establishes build/package exclusion rules, not a direct relationship to a scored Kite static asset under Tests A–C.
- It may be cited to establish why backup/archive/dev material is excluded from the fixture.
- It does not enter the CODE denominator.

### Decision 4: Relationship granularity

**One relationship per scored CODE unit × scored ASSET pair.**

- Do NOT create one relationship per source line.
- Example: if `game/route_kite.rpy` references `reference/kite_male_neutral.png` at 17 source locations, that is one relationship whose evidence array contains all 17 occurrences.
- Repeated occurrences of the same CODE unit × ASSET pair go into that one relationship's evidence array. Evidence items use the anchor structure in §5.1; line numbers are locators only.

Illustrative format example only. This is NOT a ground-truth classification of any item, and it shows only three occurrences:

```yaml
relationships:
  - related_asset: reference/kite_male_neutral.png
    relationship_status: DOWNSTREAM_USAGE
    reason: "The source references the asset but remains valid when the image changes without changing the image identifier."
    evidence:
      - source_path: game/route_kite.rpy
        anchor_type: declaration
        anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
        locator: "game/route_kite.rpy:17"
        fact: "The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png."
      - source_path: game/route_kite.rpy
        anchor_type: statement
        anchor: "show kite_male neutral at kite_first_night"
        context: "label kite_interaction_1; male-kite branch, first-impression show"
        locator: "game/route_kite.rpy:72"
        fact: "The source displays the kite_male neutral image identifier."
      - source_path: game/route_kite.rpy
        anchor_type: statement
        anchor: "show kite_male neutral at kite_first_night"
        context: "label kite_interaction_1; inside the while result_key == \"kite_interlude\" loop"
        locator: "game/route_kite.rpy:113"
        fact: "The source displays the kite_male neutral image identifier."
      - source_path: game/route_kite.rpy
        anchor_type: statement
        anchor: "show kite_male neutral at kite_first_night"
        context: "label kite_interaction_1; scene reset after the kite_interlude loop"
        locator: "game/route_kite.rpy:131"
        fact: "The source displays the kite_male neutral image identifier."
```

The three statement entries share the same evidence identity, but their `context` values distinguish the three evidence occurrences.

### Decision 5: ASSET schema

An ASSET record has exactly one status field. `file_status` is NOT used for ASSETs. Exact schema:

```yaml
test_case: <A|B|C>
item_type: ASSET
asset_path: <fixture-relative-path>
status: <ASSET_ACTION|UNAFFECTED|REVIEW_REQUIRED>
reason: <why this status applies to this test>
evidence:
  - source_path: <fixture-relative-path>
    anchor_type: <allowed-type>
    anchor: <stable-content-anchor>
    context: <optional>
    locator: <optional>
    fingerprint: <optional>
    fact: <factual observation>
game_usage:
  - <fixture-relative game source location>
```

Fields:

- `test_case`: exactly one of `A`, `B`, `C`.
- `item_type`: always `ASSET`.
- `asset_path`: exactly one of the 15 scored ASSET paths (§4.1).
- `status`: exactly one of `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.
- `reason`: why that asset receives that status for that specific test case.
- `evidence`: factual evidence, recorded as anchor-structured evidence items (§5.1). Actual fixture image pixels are valid evidence (anchor type `asset`).
- `game_usage`: known production usage locations. It is contextual, not a status. It may be an empty list.

Status definitions:

- **`ASSET_ACTION`:** The available evidence establishes that the specified design change changes the visual content that this asset depicts.
- **`UNAFFECTED`:** The available evidence establishes that the specified design change does not change the visual content that this asset depicts.
- **`REVIEW_REQUIRED`:** The available evidence is insufficient to determine whether the specified design change affects this asset.

`ASSET_ACTION` must never mean "might need review". `REVIEW_REQUIRED` must never mean "low confidence".

### Decision 6: CODE units without relevant relationships

- CODE units without relevant relationships are NOT scored.
- A CODE unit is eligible only if it contains at least one relationship to one of the 15 scored ASSET units.
- Otherwise it is **out of scoring scope**. It is not assigned `UNAFFECTED` to enlarge the denominator.

## 4. Scored units

### 4.1 ASSET units (15)

1. `reference/kite_male_neutral.png`
2. `assets/kite_male_crossed_arms.png`
3. `assets/kite_male_dark.png`
4. `assets/kite_male_dark_relaxed.png`
5. `assets/kite_male_dark_withdrawn.png`
6. `assets/kite_male_gentle.png`
7. `assets/kite_male_relaxed.png`
8. `assets/kite_male_smoking.png`
9. `assets/kite_male_soft.png`
10. `assets/kite_male_stressed.png`
11. `assets/kite_male_tired.png`
12. `assets/kite_male_warm.png`
13. `assets/kite_male_withdrawn.png`
14. `assets/kite_tattoo.png`
15. `assets/side_kite_male.png`

Final ASSET scored-unit count: **15.**

### 4.2 Fixed CODE denominator

- The CODE denominator is determined once, before ground truth and before either human or Matcha evaluation.
- Eligibility depends only on frozen fixture structural evidence, not on the results of Tests A, B or C.
- **The CODE denominator is a property of the frozen fixture, not of an individual test case.**
- The same eligible CODE set is used for A, B and C.
- A CODE unit cannot enter or leave the denominator because of a test result.

### 4.3 Final CODE count = 8

Full files (3):

1. `game/route_kite.rpy`
2. `game/li_sprite_normalization.rpy`
3. `game/side_portraits.rpy`

Eligible excerpts (5):

4. `game/credits.rpy.excerpt.txt`
5. `game/route_select.rpy.excerpt.txt`
6. `game/route_friendships.rpy.excerpt.txt`
7. `game/route_neo.rpy.excerpt.txt`
8. `game/minigames.rpy.excerpt.txt`

Eligibility rule (frozen): A CODE unit is eligible only if it contains at least one relationship to one of the 15 scored ASSET units.

Explicit exclusions:

- `game/characters.rpy`: evidence-only, and excluded because it contains only `define kite = Character(...)` with no image attribute and no relationship to any of the 15 scored assets (Decision 6).
- `game/options.rpy.excerpt.txt`: evidence-only (Decision 3).
- `game/screens.rpy.excerpt.txt`: evidence-only, and excluded because the excerpt only detects a generic `kite_male*` stage tag and does not establish a relationship to any specific one of the 15 scored assets. A generic character-level relationship is insufficient under the fixed CODE unit × scored ASSET pair rule.

Final CODE scored-unit count: **8**, frozen before ground truth and before experiment timing.

## 5. CODE output contract

A CODE record has two levels, and both are recorded: file level and relationship level. Exact schema:

```yaml
test_case: <A|B|C>
item_type: CODE
source_path: <fixture-relative-path>
file_status: <CODE_ACTION|DOWNSTREAM_USAGE|REVIEW_REQUIRED|UNAFFECTED>
reason: <why the file receives this status for this test>
evidence:
  - source_path: <fixture-relative-path>
    anchor_type: <allowed-type>
    anchor: <stable-content-anchor>
    context: <optional>
    locator: <optional>
    fingerprint: <optional>
    fact: <factual observation>
relationships:
  - related_asset: <one scored ASSET path>
    relationship_status: <CODE_ACTION|DOWNSTREAM_USAGE|REVIEW_REQUIRED|UNAFFECTED>
    reason: <why this relationship has this status>
    evidence:
      - source_path: <fixture-relative-path>
        anchor_type: <allowed-type>
        anchor: <stable-content-anchor>
        context: <optional>
        locator: <optional>
        fingerprint: <optional>
        fact: <factual observation>
```

Allowed `file_status` and `relationship_status` values are exactly: `CODE_ACTION`, `DOWNSTREAM_USAGE`, `REVIEW_REQUIRED`, `UNAFFECTED`. No others.

- `source_path` of the record is exactly one of the 8 eligible CODE paths (§4.3).
- `related_asset` is exactly one of the 15 scored ASSET paths (§4.1).
- Each scored CODE unit × scored ASSET pair appears at most once in `relationships` (Decision 4).
- A relationship's evidence array contains all relevant occurrences, as anchor-structured evidence items (§5.1).
- For an excerpt, evidence items cite only content inside the excerpt's stated line ranges (Decision 2).

Relationship status meanings:

- **`CODE_ACTION`:** because of the specified design change, the source itself must be edited for this asset relationship.
- **`DOWNSTREAM_USAGE`:** the source references an affected asset, but the source remains valid and needs no edit just because the asset changed.
- **`REVIEW_REQUIRED`:** the available evidence is insufficient to determine whether this relationship requires a source edit or points to an affected asset.
- **`UNAFFECTED`:** the specified design change has no effect on this relationship; the related asset is unaffected and no edit is needed.

### 5.1 Evidence items and evidence identity

Every `evidence` entry in the ASSET schema (Decision 5) and in the CODE schema (file-level `evidence` and relationship `evidence`) uses this structure:

```yaml
evidence:
  - source_path: <fixture-relative-path>
    anchor_type: <allowed-type>
    anchor: <stable-content-anchor>
    context: <optional>
    locator: <optional>
    fingerprint: <optional>
    fact: <factual observation>
```

**Evidence identity** is `source_path + anchor_type + anchor` and identifies the underlying semantic/source evidence.

**Evidence occurrence identity** is required when the same evidence anchor occurs multiple times within the same `source_path`. In that case, `context` and/or `fingerprint` MUST distinguish the specific occurrence.

`locator` is a convenience locator only and never defines evidence identity or occurrence identity.

An anchor must identify the actual semantic/source content being cited.

Two evidence items may share the same evidence identity when they represent repeated occurrences of the same semantic anchor. They are distinct evidence occurrences when `context` and/or `fingerprint` distinguishes them.

Line numbers are convenience locators only and must never be the sole evidence identifier.

Allowed `anchor_type` values are exactly: `declaration`, `statement`, `function`, `label`, `assignment`, `config`, `excerpt_header`, `asset`, `metadata`.

For repeated identical statements, the anchor may be the same semantic statement, but `context` and/or `fingerprint` MUST distinguish the occurrence when necessary.

### 5.2 Stable-anchor examples

Format examples only. These are NOT ground-truth classifications of any item. Both anchor strings are verbatim in the frozen fixture.

```yaml
source_path: game/route_friendships.rpy.excerpt.txt
anchor_type: statement
anchor: "show kite_male neutral at left"
context: "male-kite branch"
locator: "source game/route_friendships.rpy:59-63"
fact: "The source displays the kite_male neutral image identifier."
```

```yaml
source_path: game/route_kite.rpy
anchor_type: declaration
anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
locator: "game/route_kite.rpy:17"
fact: "The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png."
```

### 5.3 Direct and fixture-proven relationships

A CODE → ASSET relationship may be direct or fixture-proven through an explicit image-identifier declaration contained in the frozen fixture. Filename similarity or semantic guessing is not sufficient.

Valid fixture-proven relationship:

```text
show kite_male neutral
        ↓
image kite_male neutral = _kite_sprite("kite_male_neutral.png")
        ↓
kite_male_neutral.png
```

- For transitive relationships, evidence must include both the usage anchor and the mapping declaration anchor.
- One relationship per scored CODE unit × scored ASSET pair still applies. A fixture-proven relationship is not a second relationship for the same pair.
- Repeated occurrences go into the same relationship's evidence array.

## 6. CODE file-status derivation

Precedence, exactly:

`CODE_ACTION > DOWNSTREAM_USAGE > REVIEW_REQUIRED > UNAFFECTED`

The file status is the highest-precedence status among the unit's relationships. Examples:

```text
(1) UNAFFECTED, DOWNSTREAM_USAGE, UNAFFECTED  -> file_status DOWNSTREAM_USAGE
(2) DOWNSTREAM_USAGE + REVIEW_REQUIRED        -> file_status DOWNSTREAM_USAGE
    (the unresolved relationship remains visible at relationship level)
(3) CODE_ACTION + REVIEW_REQUIRED             -> file_status CODE_ACTION
    (the definite edit requirement wins)
(4) REVIEW_REQUIRED + UNAFFECTED              -> file_status REVIEW_REQUIRED
(5) UNAFFECTED + UNAFFECTED                   -> file_status UNAFFECTED
(6) No relevant scored-asset relationships    -> out of scoring scope; no experiment file_status
```

An unresolved relationship never downgrades a definite `CODE_ACTION` or `DOWNSTREAM_USAGE`.

## 7. Relationship status vs file status

- Do not confuse relationship_status `DOWNSTREAM_USAGE` with file_status `DOWNSTREAM_USAGE`.
- Relationship status describes one CODE-to-ASSET relationship. File status summarizes the entire eligible CODE unit.
- A `CODE_ACTION` relationship means the source must change for that specific asset relationship. It does not automatically make every other relationship in the same file `CODE_ACTION`.
- Asset and code statuses never mix: ASSET records never receive `CODE_ACTION` or `DOWNSTREAM_USAGE`; CODE records never receive `ASSET_ACTION`.
- A CODE reference to an affected asset does not change that asset's own `status`, and an asset's `ASSET_ACTION` does not by itself make any CODE unit or relationship `CODE_ACTION`.

## 8. Metadata and evidence-only material

There is no scored `METADATA` item type. The following are evidence-only:

- `metadata/fixture-manifest.json`
- `metadata/INSTALL_REPORT_MALEKITE_V19G.json`
- `metadata/KITE_ASSET_MASTERLIST.md`
- `docs/experiments/KITE-FIXTURE-01.md` (repository path)
- `reference/kite_male_bust_neutral_credits_v19g.png`
- `reference/KEEP_kite_male.png`
- `game/options.rpy.excerpt.txt`
- `game/screens.rpy.excerpt.txt`
- `game/characters.rpy` (contains only `define kite = Character(...)` with no image attribute and no relationship to any of the 15 scored assets)

Evidence-only material:

- may be cited as evidence;
- never receives an experiment status;
- never enters a scoring denominator.

## 9. Exact test requests (frozen)

The wording below is quoted exactly and must not be paraphrased.

### Test A: major hair change

Exact request:

> Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair.

Question:

> Which existing static production assets require regeneration or review because of this change?

- Do not specify new filenames.
- Do not assume a generation pipeline.

### Test B: outfit change

Exact request:

> Kite's canonical outfit changes to a materially different outfit.

Question:

> Which existing static production assets visually depict the changed outfit and therefore require action?

- Ground truth must rely on frozen production evidence, not on Matcha YAML outfit-family declarations as production truth.

### Test C: small accessory change

Exact request:

> Kite's canonical small ear accessory changes.

Question:

> Which existing static production assets actually show the affected accessory and therefore require action?

- The absence of a male-earring statement in text metadata does NOT automatically justify `REVIEW_REQUIRED`.
- Actual fixture image pixels are valid evidence.
- Use `REVIEW_REQUIRED` only when the total available evidence genuinely cannot establish whether the accessory is depicted.

These exact requests are frozen once the experiment begins.

## 10. Frozen baseline

- Fixture commit: `c1364f48ff92b248b3cd2aa7729c6014648008aa`.
- Underlying LOVE32 HEAD: `f4816ca90c9a15bc927a63df5148050199ad2842`.
- The dirty LOVE32 working tree is not the baseline.
- The five sprites deleted in the LOVE32 working tree are evaluated using their frozen HEAD versions contained in the fixture:
  - `reference/kite_male_neutral.png`
  - `assets/kite_male_relaxed.png`
  - `assets/kite_male_smoking.png`
  - `assets/kite_male_soft.png`
  - `assets/kite_male_tired.png`
- A working-tree/HEAD difference is not itself `REVIEW_REQUIRED`.

## 11. Canonical reference treatment

- `reference/kite_male_neutral.png`: frozen production-baseline asset (scored).
- `reference/kite_male_bust_neutral_credits_v19g.png`: approved-reference evidence (evidence-only).
- `reference/KEEP_kite_male.png`: evidence-only approved-install copy.
- Historical inconsistency: the approved-reference material (v19g, approved and installed on 2026-09-09 per `metadata/INSTALL_REPORT_MALEKITE_V19G.json`, with `KEEP_kite_male.png` saved at install) and the frozen production neutral differ.
- That inconsistency does not automatically make any test item `REVIEW_REQUIRED`.
- Ground truth is established against the frozen production baseline, using approved-reference material as evidence where relevant.

## 12. Ground-truth rule

Ground truth classifies the action actually required for the specific test case.

- **ASSET:** "Does the specified visual change alter what this asset depicts?"
- **CODE:** "Does the specified visual change require editing this source code?" If yes: `CODE_ACTION`.
- **CODE, separately:** "Does this source reference an affected asset even though the source itself remains valid?" If yes: `DOWNSTREAM_USAGE`.

Do not classify an item as affected merely because it:

- belongs to Kite;
- mentions Kite;
- references Kite;
- is downstream of Kite;
- could conceivably contain the changed feature.

Statuses are assigned independently for Tests A, B and C.

`REVIEW_REQUIRED` means only that the available evidence is insufficient to determine the answer. It does not mean low confidence, an inconvenient result, "probably affected", or that Matcha is unsure despite sufficient evidence.

## 13. CODE eligibility frozen before ground truth

Exact sequence:

1. Freeze the fixture at `c1364f48`.
2. Enumerate the 15 ASSET units.
3. Enumerate the CODE files and excerpts.
4. Apply the fixed CODE eligibility rule.
5. Freeze the final CODE denominator at 8.
6. Freeze this protocol.
7. Establish human ground truth.
8. Run the Matcha evaluation.
9. Compare and score.

The CODE count cannot change after step 5. A later discovery requiring a different denominator becomes a future protocol revision, not a change to Experiment #1.

## 14. Human baseline

The human baseline runs only after the protocol and fixture are frozen. Per test case:

- **Start:** when the human receives the exact frozen test request and the frozen fixture.
- **Stop:** when the human has completed classifications for all 15 ASSET units and all 8 eligible CODE units, including required relationships, for that test.

The human may inspect:

- frozen fixture images;
- evidence-only metadata;
- frozen fixture game source.

The human may not:

- inspect Matcha's output;
- modify the fixture;
- use evidence outside the fixture;
- change the test wording.

Record: elapsed time, final output, unresolved items. Timing is not estimated beforehand.

## 15. Matcha evaluation

The Matcha evaluation runs only after human ground truth is frozen.

Matcha receives:

- the same frozen fixture;
- the same exact test request;
- the same evidence scope.

Matcha may not receive:

- human ground truth;
- human classifications;
- human timing;
- corrections based on its partial output.

Record: elapsed time, final output, unresolved items. No manual correction is made during the evaluation.

## 16. Blinding

- Human ground truth is completed and frozen before Matcha output is compared against it.
- The evaluator must not modify ground truth after seeing Matcha's result.
- Comparison occurs only after both sides are complete.

## 17. Scoring

### 17.1 ASSET scoring

- Binary action classes: `ASSET_ACTION`, `UNAFFECTED`. Third state: `REVIEW_REQUIRED`.
- Precision and recall are calculated only over ground-truth cases where ground truth is binary-determinable.
- `REVIEW_REQUIRED` is NOT treated as positive or negative.
- Record separately:
  - ground-truth determinate cases;
  - ground-truth `REVIEW_REQUIRED` cases;
  - Matcha `REVIEW_REQUIRED` cases;
  - false positives;
  - false negatives.
- Per test: at most 15 ASSET units. Across the three tests: 45 ASSET classification records.

### 17.2 CODE scoring

- Both file-level and relationship-level classification are evaluated.
- The denominator is always the frozen 8 eligible CODE units per test. It is never changed based on a result.
- Measure:
  - correct `CODE_ACTION`;
  - correct `DOWNSTREAM_USAGE`;
  - correct `REVIEW_REQUIRED`;
  - incorrect code actions;
  - missed code actions;
  - incorrect downstream relationships;
  - missed downstream relationships.

## 18. Metrics

- **Asset precision:** `TP / (TP + FP)`.
- **Asset recall:** `TP / (TP + FN)`.
- Only determinate binary ASSET ground truth enters asset precision and recall.
- **Ground-truth review rate:** ASSET cases whose ground truth is `REVIEW_REQUIRED`, divided by all ASSET cases.
- **Matcha review rate:** Matcha ASSET outputs classified `REVIEW_REQUIRED`, divided by all eligible ASSET cases.
- **Coverage:** percentage of eligible scored items for which Matcha produces a non-`REVIEW_REQUIRED` classification.
- **Downstream traceability:** how many actual eligible CODE-to-ASSET relationships are correctly identified.
- **Code-action precision:** how often a predicted `CODE_ACTION` relationship or file corresponds to a ground-truth code edit requirement.

No arbitrary success thresholds are defined.

## 19. Limitations

Known limitations. None of them automatically produces `REVIEW_REQUIRED`.

- Videos are excluded.
- Audio is excluded.
- Backgrounds are excluded.
- UI/namebox assets are excluded.
- Female Kite is excluded.
- Dev-only, archive and backup material is excluded.
- The LOVE32 working tree differs from HEAD.
- The approved v19g reference differs from the frozen production neutral.
- Outfit per plate is not explicitly encoded (the fixture manifest records outfit as UNKNOWN for every asset; comments in `game/route_kite.rpy` are the only in-fixture statements linking plates to clothing).
- Some production sprites are unreferenced (`assets/kite_male_dark.png`, `assets/kite_male_dark_relaxed.png` and `assets/kite_male_dark_withdrawn.png` have no `.rpy` reference in the fixture manifest; `assets/kite_tattoo.png` is declared by `image evidence kite_tattoo = "images/evidence/kite_tattoo.png"` in `game/route_kite.rpy` but no `show` statement was found).
- Some CODE evidence is excerpted (Decision 2).
- The fixture game source was not executed.

## 20. Stop conditions

Once the experiment begins, do NOT:

- add test cases;
- change test wording;
- change the fixture;
- change the ASSET denominator;
- change the CODE denominator;
- change status definitions;
- change relationship granularity;
- remove inconvenient false positives;
- treat `REVIEW_REQUIRED` as success;
- add newly discovered files to the denominator.

Any methodological change becomes a new protocol revision and is not applied retroactively.

## 21. Success-evidence criteria

This protocol does not declare success or failure. The experiment may identify evidence relevant to a later strategy judgment:

- high asset precision;
- high asset recall;
- low false-positive rate;
- useful downstream tracing;
- correct separation of asset action vs code action;
- measurable human-work reduction;
- measurable time reduction.

No arbitrary pass/fail thresholds are defined.

## 22. Protocol freeze rule

> Once the controlled experiment begins, this protocol must not be changed for Tests A, B, or C. Any methodological change becomes a new protocol revision and cannot be applied retroactively to Experiment #1.

The fixture freeze rule in `docs/experiments/KITE-FIXTURE-01.md` §10 continues to apply.
