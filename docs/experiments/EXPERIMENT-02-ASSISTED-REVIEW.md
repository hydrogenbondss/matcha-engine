# Experiment 2: human-with-Matcha (H+M) assisted-review worksheet

```text
Design: docs/experiments/EXPERIMENT-02-DESIGN.md
Base commit: e47283b9e68f9d25a43cbb74eb81efe3662965d0
Protocol commit: e93f0da4dfccd4498b485d23e51147bf9c256a3b
Fixture commit: c1364f48ff92b248b3cd2aa7729c6014648008aa
Tests: A, B, C
ASSET denominator: 15
CODE denominator: 8
```

This worksheet is the blank recording form for condition **H+M (human with Matcha)** defined in `docs/experiments/EXPERIMENT-02-DESIGN.md`. It contains no classifications, no corrections, no timing and no Matcha output. Paths are relative to the fixture root `fixtures/kite-production/`, as in the protocol. The Test A/B/C request and question wording is copied verbatim from `docs/experiments/EVIDENCE-PROTOCOL-01.md` §9.

## Condition reminder (H+M)

- The Matcha output for a test is frozen (condition M) before the human receives it.
- The human then receives the frozen Matcha report for that test and verifies/corrects it to produce the final production-impact answer.
- Human verification time is recorded here. Matcha machine runtime is recorded under condition M and is never added to, or combined with, the human verification time.

## Human-only fields

Everything below the Matcha report reference is completed only by the human. The Matcha report reference is copied from the frozen Matcha report (its `provenance` block) for the test. The worksheet preparer leaves all fields blank.

## Allowed values (options only)

Defined in the protocol (Decision 5, §5, §6) and listed here only as the options to choose from:

- ASSET `status`: one of `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.
- CODE `file_status` and `relationship_status`: one of `CODE_ACTION`, `DOWNSTREAM_USAGE`, `REVIEW_REQUIRED`, `UNAFFECTED`.
- File-status derivation precedence (protocol §6): `CODE_ACTION > DOWNSTREAM_USAGE > REVIEW_REQUIRED > UNAFFECTED`.

## Evidence-anchor rules (restated from protocol §5.1)

- **Evidence identity** is `source_path + anchor_type + anchor` and identifies the underlying semantic/source evidence.
- **Evidence occurrence identity:** when the same evidence anchor occurs multiple times within the same `source_path`, `context` and/or `fingerprint` MUST distinguish the specific occurrence.
- `locator` is optional and a convenience locator only. It never defines evidence identity or occurrence identity.
- A line number is never the sole evidence identity.
- An anchor must identify the actual semantic/source content being cited.
- Allowed `anchor_type` values: `declaration`, `statement`, `function`, `label`, `assignment`, `config`, `excerpt_header`, `asset`, `metadata`.

Evidence item structure:

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

Relationship item structure (protocol §5; one relationship per CODE unit × scored ASSET pair, protocol Decision 4):

```yaml
relationships:
  - related_asset: <one scored ASSET path>
    relationship_status: <allowed CODE status>
    reason: <why this relationship has this status>
    evidence:
      - <evidence item, structure above>
```

## How to use this worksheet

- **Matcha report reference:** copy from the frozen Matcha report for that test. The fields correspond to the report's `provenance` block (`engine`, `fixture`, `reference`, `provider`, `vision_prompt`).
- **Timing:** `verification_start_time` when the human receives the frozen Matcha report for the test; `verification_end_time` when the final verified ASSET and CODE records for that test are complete. Record `verification_elapsed_time` as `HH:MM:SS`.
- **Corrections to Matcha:** every item whose final verified value differs from Matcha's output (ASSET status, CODE file_status, or a relationship's relationship_status), one entry per corrected item.
- **Missed impacts discovered by the human:** impacts (affected assets, or dependencies/relationships) that the Matcha output did not identify and the human added.
- **Unnecessary impacts removed by the human:** impacts in the Matcha output that the human removed as false or unnecessary.
- **REVIEW_REQUIRED remaining:** items still `REVIEW_REQUIRED` after human verification.
- **Final verified records:** 15 ASSET records (protocol §4.1) and 8 CODE records (protocol §4.3), in the same record structure as the H worksheet.
- **Notes:** what the human had to inspect or resolve during verification.

## Test A: major hair change

Exact request:

> Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair.

Question:

> Which existing static production assets require regeneration or review because of this change?

### Test A: Matcha report reference

```yaml
matcha_report:
  report_path:
  summary_path:
  engine:
    git_commit:
    git_worktree_dirty:
  fixture:
    manifest_sha256:
  reference:
    path:
    sha256:
  provider:
    name:
    model:
    state:
    model_identity:
  vision_prompt:
    template_sha256:
    vision_module_sha256:
    rendered_prompt_sha256:
```

### Test A: human verification timing

```yaml
verification_start_time:
verification_end_time:
verification_elapsed_time:
```

### Test A: corrections to Matcha

```yaml
corrections:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    field:
    matcha_value:
    corrected_value:
    reason:
    evidence:
      -
```

### Test A: missed impacts discovered by the human

```yaml
missed_impacts:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    final_value:
    reason:
    evidence:
      -
```

### Test A: unnecessary Matcha impacts removed by the human

```yaml
unnecessary_impacts_removed:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    matcha_value:
    final_value:
    reason:
    evidence:
      -
```

### Test A: REVIEW_REQUIRED remaining after verification

```yaml
review_required_remaining:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    reason:
    evidence:
      -
```

### Test A: final verified ASSET records

```yaml
- id: HM-A-ASSET-01
  test_case: A
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-02
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-03
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-04
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-05
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-06
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-07
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-08
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-09
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-10
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-11
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-12
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-13
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-14
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-A-ASSET-15
  test_case: A
  item_type: ASSET
  asset_path: assets/side_kite_male.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
```

### Test A: final verified CODE / dependency records

```yaml
- id: HM-A-CODE-01
  test_case: A
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-02
  test_case: A
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-03
  test_case: A
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-04
  test_case: A
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-05
  test_case: A
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-06
  test_case: A
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-07
  test_case: A
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-A-CODE-08
  test_case: A
  item_type: CODE
  source_path: game/minigames.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
```

### Test A: unresolved items

```yaml
unresolved_items:
  -
```

### Test A: notes on what the human had to inspect or resolve

```yaml
verification_notes:
  -
```

## Test B: outfit change

Exact request:

> Kite's canonical outfit changes to a materially different outfit.

Question:

> Which existing static production assets visually depict the changed outfit and therefore require action?

### Test B: Matcha report reference

```yaml
matcha_report:
  report_path:
  summary_path:
  engine:
    git_commit:
    git_worktree_dirty:
  fixture:
    manifest_sha256:
  reference:
    path:
    sha256:
  provider:
    name:
    model:
    state:
    model_identity:
  vision_prompt:
    template_sha256:
    vision_module_sha256:
    rendered_prompt_sha256:
```

### Test B: human verification timing

```yaml
verification_start_time:
verification_end_time:
verification_elapsed_time:
```

### Test B: corrections to Matcha

```yaml
corrections:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    field:
    matcha_value:
    corrected_value:
    reason:
    evidence:
      -
```

### Test B: missed impacts discovered by the human

```yaml
missed_impacts:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    final_value:
    reason:
    evidence:
      -
```

### Test B: unnecessary Matcha impacts removed by the human

```yaml
unnecessary_impacts_removed:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    matcha_value:
    final_value:
    reason:
    evidence:
      -
```

### Test B: REVIEW_REQUIRED remaining after verification

```yaml
review_required_remaining:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    reason:
    evidence:
      -
```

### Test B: final verified ASSET records

```yaml
- id: HM-B-ASSET-01
  test_case: B
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-02
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-03
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-04
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-05
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-06
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-07
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-08
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-09
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-10
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-11
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-12
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-13
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-14
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-B-ASSET-15
  test_case: B
  item_type: ASSET
  asset_path: assets/side_kite_male.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
```

### Test B: final verified CODE / dependency records

```yaml
- id: HM-B-CODE-01
  test_case: B
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-02
  test_case: B
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-03
  test_case: B
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-04
  test_case: B
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-05
  test_case: B
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-06
  test_case: B
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-07
  test_case: B
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-B-CODE-08
  test_case: B
  item_type: CODE
  source_path: game/minigames.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
```

### Test B: unresolved items

```yaml
unresolved_items:
  -
```

### Test B: notes on what the human had to inspect or resolve

```yaml
verification_notes:
  -
```

## Test C: small accessory change

Exact request:

> Kite's canonical small ear accessory changes.

Question:

> Which existing static production assets actually show the affected accessory and therefore require action?

### Test C: Matcha report reference

```yaml
matcha_report:
  report_path:
  summary_path:
  engine:
    git_commit:
    git_worktree_dirty:
  fixture:
    manifest_sha256:
  reference:
    path:
    sha256:
  provider:
    name:
    model:
    state:
    model_identity:
  vision_prompt:
    template_sha256:
    vision_module_sha256:
    rendered_prompt_sha256:
```

### Test C: human verification timing

```yaml
verification_start_time:
verification_end_time:
verification_elapsed_time:
```

### Test C: corrections to Matcha

```yaml
corrections:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    field:
    matcha_value:
    corrected_value:
    reason:
    evidence:
      -
```

### Test C: missed impacts discovered by the human

```yaml
missed_impacts:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    final_value:
    reason:
    evidence:
      -
```

### Test C: unnecessary Matcha impacts removed by the human

```yaml
unnecessary_impacts_removed:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    matcha_value:
    final_value:
    reason:
    evidence:
      -
```

### Test C: REVIEW_REQUIRED remaining after verification

```yaml
review_required_remaining:
  - item_type:
    asset_path:
    source_path:
    related_asset:
    reason:
    evidence:
      -
```

### Test C: final verified ASSET records

```yaml
- id: HM-C-ASSET-01
  test_case: C
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-02
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-03
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-04
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-05
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-06
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-07
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-08
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-09
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-10
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-11
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-12
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-13
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-14
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: HM-C-ASSET-15
  test_case: C
  item_type: ASSET
  asset_path: assets/side_kite_male.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
```

### Test C: final verified CODE / dependency records

```yaml
- id: HM-C-CODE-01
  test_case: C
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-02
  test_case: C
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-03
  test_case: C
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-04
  test_case: C
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-05
  test_case: C
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-06
  test_case: C
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-07
  test_case: C
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: HM-C-CODE-08
  test_case: C
  item_type: CODE
  source_path: game/minigames.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
```

### Test C: unresolved items

```yaml
unresolved_items:
  -
```

### Test C: notes on what the human had to inspect or resolve

```yaml
verification_notes:
  -
```
