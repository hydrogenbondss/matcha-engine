# Experiment 2: human-alone (H) baseline worksheet

```text
Design: docs/experiments/EXPERIMENT-02-DESIGN.md
Base commit: e47283b9e68f9d25a43cbb74eb81efe3662965d0
Protocol commit: e93f0da4dfccd4498b485d23e51147bf9c256a3b
Fixture commit: c1364f48ff92b248b3cd2aa7729c6014648008aa
Tests: A, B, C
ASSET denominator: 15
CODE denominator: 8
```

This worksheet is the blank recording form for condition **H (human alone)** defined in `docs/experiments/EXPERIMENT-02-DESIGN.md`. It contains no classifications, no reasons, no timing and no Matcha output. Paths are relative to the fixture root `fixtures/kite-production/`, as in the protocol. The Test A/B/C request and question wording is copied verbatim from `docs/experiments/EVIDENCE-PROTOCOL-01.md` §9 (identical to the wording in `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`).

## Blinding reminder (condition H)

While performing this baseline, the human receives only the frozen test request, the frozen Kite fixture and the fixed experiment scope (the 15 scored ASSET units and 8 eligible CODE units listed below, with the protocol's record schemas and status definitions), and independently performs the impact investigation, including independently discovering the CODE/ASSET relationships. The human must NOT receive or use:

- ChatGPT classification help;
- Grok Bot classification help;
- Matcha output (any Matcha report, summary or classification);
- Experiment 1 answers (the classifications, reasons, evidence and unresolved items recorded in `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`);
- the Experiment 1 structural relationship inventory (in the same Experiment 1 worksheet).

Execution order (design §7): H is performed for Test A → Test B → Test C before any Matcha exposure, and the completed H baseline is frozen before any Matcha run. The same participant later performs H+M (design §5).

## Human-only fields

The following fields are completed only by the human. The worksheet preparer leaves them blank.

- start/end/elapsed timing
- ASSET status
- ASSET reason
- ASSET evidence
- ASSET game_usage
- CODE file_status
- CODE reason
- CODE evidence
- CODE relationships (related_asset, relationship_status, reason, evidence)
- unresolved items
- notes on work performed

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

- Each test section contains 15 blank ASSET records (protocol §4.1) and 8 blank CODE records (protocol §4.3), in the same record structure as the Experiment 1 worksheet.
- The `relationships` field of each CODE record is left blank. The human records one relationship per CODE unit × scored ASSET pair that the human establishes from the frozen fixture (protocol Decision 4, §5.3), using the relationship item structure above.
- This worksheet does not add or reproduce the structural relationship inventory from the Experiment 1 worksheet. Giving H that engineered inventory would precompute part of the dependency-discovery work that Matcha is intended to reduce (design §6.1.1); H discovers the relationships from the frozen fixture.
- Timing: start when the human receives the exact frozen test request and the frozen fixture. Stop when all required classifications and relationships for that test are complete. Record `elapsed_time` as `HH:MM:SS`.
- `work_notes` is optional: a description of the work the human had to perform (what was inspected, what had to be resolved).

## Test A: major hair change

Exact request:

> Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair.

Question:

> Which existing static production assets require regeneration or review because of this change?

```yaml
start_time:
end_time:
elapsed_time:
```

### Test A: ASSET records

```yaml
- id: H-A-ASSET-01
  test_case: A
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-02
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-03
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-04
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-05
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-06
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-07
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-08
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-09
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-10
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-11
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-12
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-13
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-14
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-A-ASSET-15
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

### Test A: CODE records

```yaml
- id: H-A-CODE-01
  test_case: A
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-02
  test_case: A
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-03
  test_case: A
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-04
  test_case: A
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-05
  test_case: A
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-06
  test_case: A
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-07
  test_case: A
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-A-CODE-08
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

### Test A: notes on work performed (optional)

```yaml
work_notes:
  -
```

## Test B: outfit change

Exact request:

> Kite's canonical outfit changes to a materially different outfit.

Question:

> Which existing static production assets visually depict the changed outfit and therefore require action?

```yaml
start_time:
end_time:
elapsed_time:
```

### Test B: ASSET records

```yaml
- id: H-B-ASSET-01
  test_case: B
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-02
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-03
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-04
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-05
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-06
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-07
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-08
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-09
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-10
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-11
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-12
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-13
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-14
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-B-ASSET-15
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

### Test B: CODE records

```yaml
- id: H-B-CODE-01
  test_case: B
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-02
  test_case: B
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-03
  test_case: B
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-04
  test_case: B
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-05
  test_case: B
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-06
  test_case: B
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-07
  test_case: B
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-B-CODE-08
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

### Test B: notes on work performed (optional)

```yaml
work_notes:
  -
```

## Test C: small accessory change

Exact request:

> Kite's canonical small ear accessory changes.

Question:

> Which existing static production assets actually show the affected accessory and therefore require action?

```yaml
start_time:
end_time:
elapsed_time:
```

### Test C: ASSET records

```yaml
- id: H-C-ASSET-01
  test_case: C
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-02
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-03
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-04
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-05
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-06
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-07
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-08
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-09
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-10
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-11
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-12
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-13
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-14
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: H-C-ASSET-15
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

### Test C: CODE records

```yaml
- id: H-C-CODE-01
  test_case: C
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-02
  test_case: C
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-03
  test_case: C
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-04
  test_case: C
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-05
  test_case: C
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-06
  test_case: C
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-07
  test_case: C
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- id: H-C-CODE-08
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

### Test C: notes on work performed (optional)

```yaml
work_notes:
  -
```
