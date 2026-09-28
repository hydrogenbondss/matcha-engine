# Experiment 1: human baseline worksheet

```text
Protocol commit: e93f0da4dfccd4498b485d23e51147bf9c256a3b
Fixture commit: c1364f48ff92b248b3cd2aa7729c6014648008aa
Tests: A, B, C
ASSET denominator: 15
CODE denominator: 8
```

This worksheet is the blank recording form for the human baseline defined in `docs/experiments/EVIDENCE-PROTOCOL-01.md` (§14) at the protocol commit above. It contains no classifications, no timing and no Matcha output. Paths are relative to the fixture root `fixtures/kite-production/`, as in the protocol.

## Human-only fields

The following fields are completed only by the human. Cursor must leave them blank.

- ASSET status
- ASSET reason
- ASSET evidence
- CODE file_status
- CODE reason
- CODE evidence
- CODE relationship_status
- CODE relationship reason
- CODE relationship evidence
- start/end timing
- unresolved items

Allowed status values, field meanings and file-status derivation are defined in the protocol (Decision 5, §5, §6) and are not repeated here.

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

## How to use this worksheet

- Each test section contains 15 blank ASSET records (protocol §4.1) and 8 blank CODE records (protocol §4.3).
- The `relationships` field of each CODE record is left blank. The human uses the Structural relationship inventory (below the three test sections) to know which `related_asset` pairs to record for each CODE unit, one relationship per CODE unit × ASSET pair (protocol Decision 4).
- The inventory is fixture-derived, identical for all three tests, and records structure only. It contains no status of any kind.

## Test A: major hair change

Exact request:

> Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair.

Question:

> Which existing static production assets require regeneration or review because of this change?

Start timing when the human receives the exact frozen test request and the frozen fixture. Stop when all required classifications and relationships for that test are complete.

```yaml
start_time: 2026-09-29T00:45:42+08:00
end_time:
elapsed_time:
```

### Test A: ASSET records

```yaml
- id: A-ASSET-01
  test_case: A
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status: ASSET_ACTION
  reason: >-
    The frozen neutral sprite visibly depicts Kite with the current short hairstyle. Changing Kite's canonical hairstyle to shoulder-length dark hair would change what this asset depicts, so this existing sprite would need regeneration or replacement.
  evidence:
    - source_path: reference/kite_male_neutral.png
      anchor_type: asset
      anchor: sha256:b3469eeed8510f5ae0807cafc8564b21b9be617a3a27027f7eca6d230c0da07d
      fact: The frozen production neutral sprite depicts Kite with the current short hairstyle; the Test A change replaces that hairstyle with shoulder-length dark hair.
  game_usage:
    -
- id: A-ASSET-02
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status: ASSET_ACTION
  reason: >-
    This is a production Kite character sprite depicting his full stage presentation, including his head and hairstyle. Changing Kite's canonical hairstyle to shoulder-length dark hair changes what this asset depicts, so the existing sprite requires regeneration or replacement.
  evidence:
    - source_path: assets/kite_male_crossed_arms.png
      anchor_type: asset
      anchor: sha256:3e02cec081434374e582fed11b18ed1ab8c0b76625429803de8e6ff5bed502fd
      fact: The frozen fixture contains this 928×1232 production Kite character sprite; the proposed canonical hairstyle change alters the character depiction in this sprite.
  game_usage:
    -
- id: A-ASSET-03
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle to shoulder-length dark hair changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_dark.png
      anchor_type: asset
      anchor: sha256:d67a8f71a0e055603d59aa5f6af3437d46206981c9929ce6da481440d7593f6d
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-04
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_dark_relaxed.png
      anchor_type: asset
      anchor: sha256:26f1969b35afe1556eb87e4929f662ea0373093763a1c04cb317efd3150e5a43
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-05
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_dark_withdrawn.png
      anchor_type: asset
      anchor: sha256:42187a9344adca4c2a26a51e6b5155d869aa67ae42a233c7251817cea1f009da
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-06
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_gentle.png
      anchor_type: asset
      anchor: sha256:33b6351638692e99ed21eeb17c609a375fc1d33c3c754e4d2e42dc155a3e874c
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-07
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_relaxed.png
      anchor_type: asset
      anchor: sha256:a070c5e8300aa4bd97768908bb1d5a4c0eca43504401b29f1a826bb1dd0ad924
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-08
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_smoking.png
      anchor_type: asset
      anchor: sha256:0a3cc3d19d12e8effd81d332865d34e54d91c6f9415ac4234f36c7a69f96646f
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-09
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_soft.png
      anchor_type: asset
      anchor: sha256:32df57007cc98a8d023940427bbac30f3fbbfe190c6deeeb441b42180698b798
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-10
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_stressed.png
      anchor_type: asset
      anchor: sha256:06646bfe838667a133513a7bef50d984210ad36b1e158b357ca8a0efd226840a
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-11
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_tired.png
      anchor_type: asset
      anchor: sha256:ca79e5aa3db24ef244510093f1176f772d5021ca575e2f4b2dd7be1adac42dc2
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-12
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_warm.png
      anchor_type: asset
      anchor: sha256:ef315af8367228a4c734be226ff89884842598769a1f6b76b0fede71ed054d1c
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-13
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status: ASSET_ACTION
  reason: >-
    This frozen production Kite sprite depicts the character's head and current hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/kite_male_withdrawn.png
      anchor_type: asset
      anchor: sha256:041a58e8c5649a9f80e67be0f3076051d8dcc6286115a374eb2d0e25827d1fec
      fact: The frozen production sprite depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
- id: A-ASSET-14
  test_case: A
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status: UNAFFECTED
  reason: >-
    This frozen asset is an evidence close-up of Kite's tattoo/bare torso and does not depict the hairstyle or head. Changing the canonical hairstyle does not change what this asset depicts.
  evidence:
    - source_path: assets/kite_tattoo.png
      anchor_type: asset
      anchor: sha256:2eb838636fc6dc1aff000d4f36957662c18ad3f7719c28a8d2f21492bdccff76
      fact: The frozen fixture identifies this as a tattoo-detail close-up rather than a head/hairstyle depiction.
  game_usage:
    -
- id: A-ASSET-15
  test_case: A
  item_type: ASSET
  asset_path: assets/side_kite_male.png
  status: ASSET_ACTION
  reason: >-
    This frozen side portrait depicts Kite's head and hairstyle. Changing the canonical hairstyle changes what this asset depicts.
  evidence:
    - source_path: assets/side_kite_male.png
      anchor_type: asset
      anchor: sha256:baa592a3fae8be9cef1bedbedf739a549228670cb138db2f39b43638c7b19339
      fact: The frozen side portrait depicts Kite with the current hairstyle, which is changed by Test A.
  game_usage:
    -
```

### Test A: CODE records

```yaml
- test_case: A
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The source declares the kite_male neutral image identifier as _kite_sprite("kite_male_neutral.png").'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male angry = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:26'
      fact: 'The source declares the kite_male angry image identifier as _kite_sprite("kite_male_neutral.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:72'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:113'
      fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:131'
      fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:177'
      fingerprint: 'previous non-blank line: narrator "He leaves it on the rail. Turns to the sink."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:568'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:698'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:798'
      fingerprint: "previous non-blank line: kite \"Fine is a word people use when they don't want to explain.\""
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:861'
      fingerprint: "previous non-blank line: kite \"Belonging somewhere doesn't mean it belongs back.\""
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1585'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1607'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2591'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_female; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2625'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_6_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3131'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_6_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3200'
      fingerprint: 'previous non-blank line: kite "Please."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3428'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3510'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3554'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male neutral image identifier as the "image" value of a pb_elements entry.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male crossed_arms = _kite_sprite("kite_male_crossed_arms.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:27'
      fact: 'The source declares the kite_male crossed_arms image identifier as _kite_sprite("kite_male_crossed_arms.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2148'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male crossed_arms image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2179'
      fingerprint: "previous non-blank line: call screen email_message(sender=\"Verrerie Accounts\", subject=\"\", body=\"You think this is over? I'm always watching.\")"
      fact: 'The source displays the kite_male crossed_arms image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2242'
      fingerprint: "previous non-blank line: kite \"The email said 'watching.' So did whatever just said that in my own voice.\""
      fact: 'The source displays the kite_male crossed_arms image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male gentle = _kite_sprite("kite_male_gentle.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:18'
      fact: 'The source declares the kite_male gentle image identifier as _kite_sprite("kite_male_gentle.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2207'
      fingerprint: 'previous non-blank line: pause 0.4'
      fact: 'The source displays the kite_male gentle image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_right'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2262'
      fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
      fact: 'The source displays the kite_male gentle image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_center'
      context: 'label kite_interaction_5_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2265'
      fingerprint: 'previous non-blank line: narrator "You sweep the glass into the bin. He watches once, then pretends not to."'
      fact: 'The source displays the kite_male gentle image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:19'
      fact: 'The source declares the kite_male relaxed image identifier as _kite_sprite("kite_male_relaxed.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1675'
      fingerprint: 'previous non-blank line: scene bg street_night with fade'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 2 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1684'
      fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 3 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1710'
      fingerprint: 'previous non-blank line: $ remy_phone_soft_open()'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 4 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1722'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 5 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1726'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 6 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1730'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 7 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1740'
      fingerprint: 'previous non-blank line: kite "I know I kept them."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 8 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1749'
      fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 9 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1781'
      fingerprint: 'previous non-blank line: narrator "Salt. Tequila. Lime. The first shot burns. By the third, his shoulders drop."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 10 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1810'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 11 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1913'
      fingerprint: 'previous non-blank line: narrator "He tenses. Then relaxes. His head finds your shoulder."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_4_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1952'
      fingerprint: "previous non-blank line: \"He comes over. Yesterday's pants. Same henley.\""
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_4_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2008'
      fingerprint: 'previous non-blank line: scene bg street_day with fade'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male smoking = _kite_sprite("kite_male_smoking.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:20'
      fact: 'The source declares the kite_male smoking image identifier as _kite_sprite("kite_male_smoking.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male smoking at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1550'
      fingerprint: 'previous non-blank line: scene bg bar_exterior'
      fact: 'The source displays the kite_male smoking image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male soft = _kite_sprite("kite_male_soft.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:21'
      fact: 'The source declares the kite_male soft image identifier as _kite_sprite("kite_male_soft.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:137'
      fingerprint: 'previous non-blank line: if result_key in ("balanced", "interesting"):'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:170'
      fingerprint: 'previous non-blank line: narrator "He slides it to your hand. Warm. Exact."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:185'
      fingerprint: 'previous non-blank line: narrator "He does. Small. Professional. Then pushes it to you."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:192'
      fingerprint: 'previous non-blank line: narrator "He sets a water glass on the rail. No pour. No performance."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:622'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_expression_beat'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:643'
      fingerprint: 'previous non-blank line: narrator "You tap the bar where a glass would sit."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_expression_beat'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:720'
      fingerprint: "previous non-blank line: narrator \"You don't sit yet. He sets a glass down anyway.\""
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:760'
      fingerprint: 'previous non-blank line: narrator "You look at the bar top. Not at him."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1160'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1405'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_look_away'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1417'
      fingerprint: 'previous non-blank line: kite "Promise?"'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male stressed = _kite_sprite("kite_male_stressed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:22'
      fact: 'The source declares the kite_male stressed image identifier as _kite_sprite("kite_male_stressed.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, li_flinch, corrupt_tier2'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:725'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 2:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:734'
      fingerprint: 'previous non-blank line: kite "{stutter}W-why did I s-say that?{/stutter}"'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:738'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:764'
      fingerprint: 'previous non-blank line: elif birthday_choice == "skip":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:781'
      fingerprint: 'previous non-blank line: elif birthday_choice is not None:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:790'
      fingerprint: 'previous non-blank line: "I was with someone.":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1622'
      fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2231'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2290'
      fingerprint: 'previous non-blank line: $ stop_story_music(fadeout=1.2)'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_route_lockin; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2435'
      fingerprint: 'previous non-blank line: scene bg bar_night'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2563'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3180'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_ending_bad_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3568'
      fingerprint: "previous non-blank line: p \"I can't. This is too much.\""
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_ending_bad_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3586'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male stressed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_bad_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3624'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male stressed image identifier as the "image" value of a pb_elements entry.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male tired = _kite_sprite("kite_male_tired.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:23'
      fact: 'The source declares the kite_male tired image identifier as _kite_sprite("kite_male_tired.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:855'
      fingerprint: 'previous non-blank line: narrator "[kite_name] wipes down the counter again."'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:858'
      fingerprint: "previous non-blank line: kite \"Lease is up in eight months. Landlord's been sniffing around.\""
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center, li_look_away'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1155'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1643'
      fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2013'
      fingerprint: 'previous non-blank line: scene bg bar_backroom with dissolve'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2026'
      fingerprint: 'previous non-blank line: scene bg bar_interior with dissolve'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2056'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3150'
      fingerprint: 'previous non-blank line: else:'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3498'
      fingerprint: "previous non-blank line: kite \"I know. You're saying not yet.\""
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3521'
      fingerprint: "previous non-blank line: kite \"Same stool as night one. I didn't retire it.\""
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:24'
      fact: 'The source declares the kite_male warm image identifier as _kite_sprite("kite_male_warm.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:141'
      fingerprint: 'previous non-blank line: elif result_key in ("messy_twice", "bitter_meaning"):'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at kite_first_night, li_lean_in'
      context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:162'
      fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:423'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:748'
      fingerprint: 'previous non-blank line: if birthday_choice == "kite":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1088'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1201'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1281'
      fingerprint: 'previous non-blank line: narrator "He smiles, and this time it reaches his eyes."'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1314'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center, li_expression_beat'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1415'
      fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center, li_lean_in'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1429'
      fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male warm", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3478'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male warm image identifier as the "image" value of a pb_elements entry.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male withdrawn = _kite_sprite("kite_male_withdrawn.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:25'
      fact: 'The source declares the kite_male withdrawn image identifier as _kite_sprite("kite_male_withdrawn.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male withdrawn at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1625'
      fingerprint: 'previous non-blank line: else:'
      fact: 'The source displays the kite_male withdrawn image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male withdrawn at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2633'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male withdrawn image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image evidence kite_tattoo = "images/evidence/kite_tattoo.png"'
      context: 'init-time image declaration'
      locator: 'game/route_kite.rpy:10'
      fact: 'The source declares the evidence kite_tattoo image identifier from the path images/evidence/kite_tattoo.png.'
  relationships:
    - related_asset: reference/kite_male_neutral.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:17'
          fact: 'The source declares the kite_male neutral image identifier as _kite_sprite("kite_male_neutral.png").'
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male angry = _kite_sprite("kite_male_neutral.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:26'
          fact: 'The source declares the kite_male angry image identifier as _kite_sprite("kite_male_neutral.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at kite_first_night'
          context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:72'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at kite_first_night'
          context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:113'
          fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at kite_first_night'
          context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:131'
          fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at kite_first_night'
          context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:177'
          fingerprint: 'previous non-blank line: narrator "He leaves it on the rail. Turns to the sink."'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:568'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:698'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:798'
          fingerprint: "previous non-blank line: kite \"Fine is a word people use when they don't want to explain.\""
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:861'
          fingerprint: "previous non-blank line: kite \"Belonging somewhere doesn't mean it belongs back.\""
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:1585'
          fingerprint: 'previous non-blank line: scene bg bar_interior'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_3_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:1607'
          fingerprint: 'previous non-blank line: scene bg bar_interior'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_3_female; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:2591'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_3_female; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:2625'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_6_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3131'
          fingerprint: 'previous non-blank line: with fade'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_interaction_6_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3200'
          fingerprint: 'previous non-blank line: kite "Please."'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3428'
          fingerprint: 'previous non-blank line: with fade'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male neutral at li_center'
          context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3510'
          fingerprint: 'previous non-blank line: with fade'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: assignment
          anchor: '$ pb_elements = [{"image": "kite_male neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
          context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3554'
          fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
          fact: 'The source lists the kite_male neutral image identifier as the "image" value of a pb_elements entry.'
    - related_asset: assets/kite_male_crossed_arms.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male crossed_arms = _kite_sprite("kite_male_crossed_arms.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:27'
          fact: 'The source declares the kite_male crossed_arms image identifier as _kite_sprite("kite_male_crossed_arms.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male crossed_arms at li_center'
          context: 'label kite_interaction_5_male; occurrence 1 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2148'
          fingerprint: 'previous non-blank line: with fade'
          fact: 'The source displays the kite_male crossed_arms image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male crossed_arms at li_center'
          context: 'label kite_interaction_5_male; occurrence 2 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2179'
          fingerprint: "previous non-blank line: call screen email_message(sender=\"Verrerie Accounts\", subject=\"\", body=\"You think this is over? I'm always watching.\")"
          fact: 'The source displays the kite_male crossed_arms image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male crossed_arms at li_center'
          context: 'label kite_interaction_5_male; occurrence 3 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2242'
          fingerprint: "previous non-blank line: kite \"The email said 'watching.' So did whatever just said that in my own voice.\""
          fact: 'The source displays the kite_male crossed_arms image identifier.'
    - related_asset: assets/kite_male_gentle.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male gentle = _kite_sprite("kite_male_gentle.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:18'
          fact: 'The source declares the kite_male gentle image identifier as _kite_sprite("kite_male_gentle.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male gentle at li_center'
          context: 'label kite_interaction_5_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:2207'
          fingerprint: 'previous non-blank line: pause 0.4'
          fact: 'The source displays the kite_male gentle image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male gentle at li_right'
          context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2262'
          fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
          fact: 'The source displays the kite_male gentle image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male gentle at li_center'
          context: 'label kite_interaction_5_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:2265'
          fingerprint: 'previous non-blank line: narrator "You sweep the glass into the bin. He watches once, then pretends not to."'
          fact: 'The source displays the kite_male gentle image identifier.'
    - related_asset: assets/kite_male_relaxed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:19'
          fact: 'The source declares the kite_male relaxed image identifier as _kite_sprite("kite_male_relaxed.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1675'
          fingerprint: 'previous non-blank line: scene bg street_night with fade'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 2 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1684'
          fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 3 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1710'
          fingerprint: 'previous non-blank line: $ remy_phone_soft_open()'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 4 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1722'
          fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 5 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1726'
          fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 6 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1730'
          fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 7 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1740'
          fingerprint: 'previous non-blank line: kite "I know I kept them."'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 8 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1749'
          fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 9 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1781'
          fingerprint: 'previous non-blank line: narrator "Salt. Tequila. Lime. The first shot burns. By the third, his shoulders drop."'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 10 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1810'
          fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_3_male; occurrence 11 of 11 of this anchor in this label'
          locator: 'game/route_kite.rpy:1913'
          fingerprint: 'previous non-blank line: narrator "He tenses. Then relaxes. His head finds your shoulder."'
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_4_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:1952'
          fingerprint: "previous non-blank line: \"He comes over. Yesterday's pants. Same henley.\""
          fact: 'The source displays the kite_male relaxed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male relaxed at li_center'
          context: 'label kite_interaction_4_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:2008'
          fingerprint: 'previous non-blank line: scene bg street_day with fade'
          fact: 'The source displays the kite_male relaxed image identifier.'
    - related_asset: assets/kite_male_smoking.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male smoking = _kite_sprite("kite_male_smoking.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:20'
          fact: 'The source declares the kite_male smoking image identifier as _kite_sprite("kite_male_smoking.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male smoking at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1550'
          fingerprint: 'previous non-blank line: scene bg bar_exterior'
          fact: 'The source displays the kite_male smoking image identifier.'
    - related_asset: assets/kite_male_soft.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male soft = _kite_sprite("kite_male_soft.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:21'
          fact: 'The source declares the kite_male soft image identifier as _kite_sprite("kite_male_soft.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at kite_first_night'
          context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:137'
          fingerprint: 'previous non-blank line: if result_key in ("balanced", "interesting"):'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at kite_first_night'
          context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:170'
          fingerprint: 'previous non-blank line: narrator "He slides it to your hand. Warm. Exact."'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at kite_first_night'
          context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:185'
          fingerprint: 'previous non-blank line: narrator "He does. Small. Professional. Then pushes it to you."'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at kite_first_night'
          context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
          locator: 'game/route_kite.rpy:192'
          fingerprint: 'previous non-blank line: narrator "He sets a water glass on the rail. No pour. No performance."'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center'
          context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:622'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center, li_expression_beat'
          context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:643'
          fingerprint: 'previous non-blank line: narrator "You tap the bar where a glass would sit."'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center, li_expression_beat'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:720'
          fingerprint: "previous non-blank line: narrator \"You don't sit yet. He sets a glass down anyway.\""
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center, li_look_away'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:760'
          fingerprint: 'previous non-blank line: narrator "You look at the bar top. Not at him."'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center'
          context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1160'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center'
          context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1405'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male soft image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male soft at li_center, li_look_away'
          context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1417'
          fingerprint: 'previous non-blank line: kite "Promise?"'
          fact: 'The source displays the kite_male soft image identifier.'
    - related_asset: assets/kite_male_stressed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male stressed = _kite_sprite("kite_male_stressed.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:22'
          fact: 'The source declares the kite_male stressed image identifier as _kite_sprite("kite_male_stressed.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center, li_flinch, corrupt_tier2'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:725'
          fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 2:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:734'
          fingerprint: 'previous non-blank line: kite "{stutter}W-why did I s-say that?{/stutter}"'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:738'
          fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:764'
          fingerprint: 'previous non-blank line: elif birthday_choice == "skip":'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:781'
          fingerprint: 'previous non-blank line: elif birthday_choice is not None:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center, li_look_away'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:790'
          fingerprint: 'previous non-blank line: "I was with someone.":'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1622'
          fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
          context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2231'
          fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2290'
          fingerprint: 'previous non-blank line: $ stop_story_music(fadeout=1.2)'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_route_lockin; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2435'
          fingerprint: 'previous non-blank line: scene bg bar_night'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2563'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
          context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3180'
          fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_ending_bad_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3568'
          fingerprint: "previous non-blank line: p \"I can't. This is too much.\""
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male stressed at li_center'
          context: 'label kite_ending_bad_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3586'
          fingerprint: 'previous non-blank line: with fade'
          fact: 'The source displays the kite_male stressed image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: assignment
          anchor: '$ pb_elements = [{"image": "kite_male stressed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
          context: 'label kite_ending_bad_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3624'
          fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
          fact: 'The source lists the kite_male stressed image identifier as the "image" value of a pb_elements entry.'
    - related_asset: assets/kite_male_tired.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male tired = _kite_sprite("kite_male_tired.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:23'
          fact: 'The source declares the kite_male tired image identifier as _kite_sprite("kite_male_tired.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center, li_look_away'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:855'
          fingerprint: 'previous non-blank line: narrator "[kite_name] wipes down the counter again."'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:858'
          fingerprint: "previous non-blank line: kite \"Lease is up in eight months. Landlord's been sniffing around.\""
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center, li_look_away'
          context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1155'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1643'
          fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_4_male; occurrence 1 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2013'
          fingerprint: 'previous non-blank line: scene bg bar_backroom with dissolve'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_4_male; occurrence 2 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2026'
          fingerprint: 'previous non-blank line: scene bg bar_interior with dissolve'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_4_male; occurrence 3 of 3 of this anchor in this label'
          locator: 'game/route_kite.rpy:2056'
          fingerprint: 'previous non-blank line: scene bg bar_interior'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3150'
          fingerprint: 'previous non-blank line: else:'
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_ending_bittersweet_male; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3498'
          fingerprint: "previous non-blank line: kite \"I know. You're saying not yet.\""
          fact: 'The source displays the kite_male tired image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male tired at li_center'
          context: 'label kite_ending_bittersweet_male; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:3521'
          fingerprint: "previous non-blank line: kite \"Same stool as night one. I didn't retire it.\""
          fact: 'The source displays the kite_male tired image identifier.'
    - related_asset: assets/kite_male_warm.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:24'
          fact: 'The source declares the kite_male warm image identifier as _kite_sprite("kite_male_warm.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at kite_first_night'
          context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:141'
          fingerprint: 'previous non-blank line: elif result_key in ("messy_twice", "bitter_meaning"):'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at kite_first_night, li_lean_in'
          context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:162'
          fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:423'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:748'
          fingerprint: 'previous non-blank line: if birthday_choice == "kite":'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1088'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_warm_scene; occurrence 1 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:1201'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_warm_scene; occurrence 2 of 2 of this anchor in this label'
          locator: 'game/route_kite.rpy:1281'
          fingerprint: 'previous non-blank line: narrator "He smiles, and this time it reaches his eyes."'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center'
          context: 'label kite_warm_scene_dense; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1314'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center, li_expression_beat'
          context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1415'
          fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male warm at li_center, li_lean_in'
          context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1429'
          fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
          fact: 'The source displays the kite_male warm image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: assignment
          anchor: '$ pb_elements = [{"image": "kite_male warm", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
          context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:3478'
          fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
          fact: 'The source lists the kite_male warm image identifier as the "image" value of a pb_elements entry.'
    - related_asset: assets/kite_male_withdrawn.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male withdrawn = _kite_sprite("kite_male_withdrawn.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:25'
          fact: 'The source declares the kite_male withdrawn image identifier as _kite_sprite("kite_male_withdrawn.png").'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male withdrawn at li_center'
          context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:1625'
          fingerprint: 'previous non-blank line: else:'
          fact: 'The source displays the kite_male withdrawn image identifier.'
        - source_path: game/route_kite.rpy
          anchor_type: statement
          anchor: 'show kite_male withdrawn at li_center'
          context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
          locator: 'game/route_kite.rpy:2633'
          fingerprint: 'previous non-blank line: if kite_variant == "male":'
          fact: 'The source displays the kite_male withdrawn image identifier.'
    - related_asset: assets/kite_tattoo.png
      relationship_status: UNAFFECTED
      reason: >-
        This relationship points to a tattoo-detail asset that is unrelated to the hairstyle change, so no source edit is required for this relationship.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image evidence kite_tattoo = "images/evidence/kite_tattoo.png"'
          context: 'init-time image declaration'
          locator: 'game/route_kite.rpy:10'
          fact: 'The source declares the evidence kite_tattoo image identifier from the path images/evidence/kite_tattoo.png.'
- test_case: A
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "angry"): "kite_male_neutral.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:189'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "angry") to the filename kite_male_neutral.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "crossed_arms"): "kite_male_crossed_arms.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:190'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "crossed_arms") to the filename kite_male_crossed_arms.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_gentle.png": (1.011, -8),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:101'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_gentle.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_relaxed.png": (1.002, -2),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:102'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_relaxed.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "smoking"): "kite_male_smoking.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:187'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "smoking") to the filename kite_male_smoking.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "soft"): "kite_male_soft.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:188'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "soft") to the filename kite_male_soft.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_stressed.png": (0.996, 3),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:104'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_stressed.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_tired.png": (0.971, 22),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:106'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_tired.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_warm.png": (0.998, 2),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:103'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_warm.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_withdrawn.png": (0.975, 19),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:105'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_withdrawn.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"side_kite_male.png": (0.92, 1.0),'
      context: 'LI_CIRCLE_LOCK table'
      locator: 'game/li_sprite_normalization.rpy:149'
      fact: 'The LI_CIRCLE_LOCK table contains an entry keyed by the filename side_kite_male.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: statement
      anchor: 'return "images/side_treated/side_kite_male.png"'
      context: 'function _li_circle_path'
      locator: 'game/li_sprite_normalization.rpy:166'
      fact: 'The _li_circle_path function returns the path images/side_treated/side_kite_male.png for names starting with kite_male or "kite ".'
  relationships:
    - related_asset: reference/kite_male_neutral.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '("kite_male", "angry"): "kite_male_neutral.png",'
          context: 'LI_EXPR_ALIAS table'
          locator: 'game/li_sprite_normalization.rpy:189'
          fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "angry") to the filename kite_male_neutral.png.'
    - related_asset: assets/kite_male_crossed_arms.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '("kite_male", "crossed_arms"): "kite_male_crossed_arms.png",'
          context: 'LI_EXPR_ALIAS table'
          locator: 'game/li_sprite_normalization.rpy:190'
          fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "crossed_arms") to the filename kite_male_crossed_arms.png.'
    - related_asset: assets/kite_male_gentle.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_gentle.png": (1.011, -8),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:101'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_gentle.png.'
    - related_asset: assets/kite_male_relaxed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_relaxed.png": (1.002, -2),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:102'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_relaxed.png.'
    - related_asset: assets/kite_male_smoking.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '("kite_male", "smoking"): "kite_male_smoking.png",'
          context: 'LI_EXPR_ALIAS table'
          locator: 'game/li_sprite_normalization.rpy:187'
          fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "smoking") to the filename kite_male_smoking.png.'
    - related_asset: assets/kite_male_soft.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '("kite_male", "soft"): "kite_male_soft.png",'
          context: 'LI_EXPR_ALIAS table'
          locator: 'game/li_sprite_normalization.rpy:188'
          fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "soft") to the filename kite_male_soft.png.'
    - related_asset: assets/kite_male_stressed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_stressed.png": (0.996, 3),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:104'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_stressed.png.'
    - related_asset: assets/kite_male_tired.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_tired.png": (0.971, 22),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:106'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_tired.png.'
    - related_asset: assets/kite_male_warm.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_warm.png": (0.998, 2),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:103'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_warm.png.'
    - related_asset: assets/kite_male_withdrawn.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"kite_male_withdrawn.png": (0.975, 19),'
          context: 'LI_ALIGN table'
          locator: 'game/li_sprite_normalization.rpy:105'
          fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_withdrawn.png.'
    - related_asset: assets/side_kite_male.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: config
          anchor: '"side_kite_male.png": (0.92, 1.0),'
          context: 'LI_CIRCLE_LOCK table'
          locator: 'game/li_sprite_normalization.rpy:149'
          fact: 'The LI_CIRCLE_LOCK table contains an entry keyed by the filename side_kite_male.png.'
        - source_path: game/li_sprite_normalization.rpy
          anchor_type: statement
          anchor: 'return "images/side_treated/side_kite_male.png"'
          context: 'function _li_circle_path'
          locator: 'game/li_sprite_normalization.rpy:166'
          fact: 'The _li_circle_path function returns the path images/side_treated/side_kite_male.png for names starting with kite_male or "kite ".'
- test_case: A
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/side_portraits.rpy
      anchor_type: declaration
      anchor: 'image side kite_male      = _li_circle_lock("images/side_treated/side_kite_male.png")'
      context: 'side portrait image declarations'
      locator: 'game/side_portraits.rpy:24'
      fact: 'The source declares the side kite_male image identifier from the path images/side_treated/side_kite_male.png.'
  relationships:
    - related_asset: assets/side_kite_male.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/side_portraits.rpy
          anchor_type: declaration
          anchor: 'image side kite_male      = _li_circle_lock("images/side_treated/side_kite_male.png")'
          context: 'side portrait image declarations'
          locator: 'game/side_portraits.rpy:24'
          fact: 'The source declares the side kite_male image identifier from the path images/side_treated/side_kite_male.png.'
- test_case: A
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_neutral.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:118'
      fingerprint: 'previous non-blank line in block: "images/kite_male_relaxed.png",'
      fact: 'The source lists the path images/kite_male_neutral.png in the male-branch _credits_first_ok candidate list.'
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_relaxed.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:117'
      fingerprint: 'previous non-blank line in block: "images/kite_male_warm.png",'
      fact: 'The source lists the path images/kite_male_relaxed.png in the male-branch _credits_first_ok candidate list.'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:24'
      fact: 'The frozen fixture maps the kite_male warm identifier to kite_male_warm.png.'
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_warm.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:116'
      fingerprint: 'previous non-blank line in block: return _credits_first_ok(['
      fact: 'The source lists the path images/kite_male_warm.png in the male-branch _credits_first_ok candidate list.'
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: assignment
      anchor: 'li = "kite_female warm" if female else "kite_male warm"'
      context: 'excerpt block marker: # --- credits.rpy lines 164-176 ---'
      locator: 'source game/credits.rpy:168'
      fingerprint: 'previous non-blank line in block: female = getattr(store, "kite_variant", "male") == "female"'
      fact: 'The source assigns the kite_male warm image identifier to li when female is false.'
  relationships:
    - related_asset: reference/kite_male_neutral.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/credits.rpy.excerpt.txt
          anchor_type: statement
          anchor: '"images/kite_male_neutral.png",'
          context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
          locator: 'source game/credits.rpy:118'
          fingerprint: 'previous non-blank line in block: "images/kite_male_relaxed.png",'
          fact: 'The source lists the path images/kite_male_neutral.png in the male-branch _credits_first_ok candidate list.'
    - related_asset: assets/kite_male_relaxed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/credits.rpy.excerpt.txt
          anchor_type: statement
          anchor: '"images/kite_male_relaxed.png",'
          context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
          locator: 'source game/credits.rpy:117'
          fingerprint: 'previous non-blank line in block: "images/kite_male_warm.png",'
          fact: 'The source lists the path images/kite_male_relaxed.png in the male-branch _credits_first_ok candidate list.'
    - related_asset: assets/kite_male_warm.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:24'
          fact: 'The frozen fixture maps the kite_male warm identifier to kite_male_warm.png.'
        - source_path: game/credits.rpy.excerpt.txt
          anchor_type: statement
          anchor: '"images/kite_male_warm.png",'
          context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
          locator: 'source game/credits.rpy:116'
          fingerprint: 'previous non-blank line in block: return _credits_first_ok(['
          fact: 'The source lists the path images/kite_male_warm.png in the male-branch _credits_first_ok candidate list.'
        - source_path: game/credits.rpy.excerpt.txt
          anchor_type: assignment
          anchor: 'li = "kite_female warm" if female else "kite_male warm"'
          context: 'excerpt block marker: # --- credits.rpy lines 164-176 ---'
          locator: 'source game/credits.rpy:168'
          fingerprint: 'previous non-blank line in block: female = getattr(store, "kite_variant", "male") == "female"'
          fact: 'The source assigns the kite_male warm image identifier to li when female is false.'
- test_case: A
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/route_select.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'portrait = "images/side_treated/side_kite_male.png"'
      context: 'excerpt block marker: # --- route_select.rpy lines 54-64 ---'
      locator: 'source game/route_select.rpy:58'
      fingerprint: 'previous non-blank line in block: else:'
      fact: 'The source assigns the path images/side_treated/side_kite_male.png to portrait in the non-female branch.'
  relationships:
    - related_asset: assets/side_kite_male.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_select.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'portrait = "images/side_treated/side_kite_male.png"'
          context: 'excerpt block marker: # --- route_select.rpy lines 54-64 ---'
          locator: 'source game/route_select.rpy:58'
          fingerprint: 'previous non-blank line in block: else:'
          fact: 'The source assigns the path images/side_treated/side_kite_male.png to portrait in the non-female branch.'
- test_case: A
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 59-63 ---'
      locator: 'source game/route_friendships.rpy:62'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 157-160 ---'
      locator: 'source game/route_friendships.rpy:159'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 246-249 ---'
      locator: 'source game/route_friendships.rpy:248'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 343-346 ---'
      locator: 'source game/route_friendships.rpy:345'
      fingerprint: 'previous non-blank line in block: narrator "[kite_name] keeps glancing at [neo_obj] between other customers."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 650-653 ---'
      locator: 'source game/route_friendships.rpy:652'
      fingerprint: 'previous non-blank line in block: narrator "[neo_name] is behind the counter — not working, just belonging. Leaning on the service side like [neo_subj] is allowed to be there."'
      fact: 'The source displays the kite_male neutral image identifier.'
  relationships:
    - related_asset: reference/kite_male_neutral.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:17'
          fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
        - source_path: game/route_friendships.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_friendships.rpy lines 59-63 ---'
          locator: 'source game/route_friendships.rpy:62'
          fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_friendships.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_friendships.rpy lines 157-160 ---'
          locator: 'source game/route_friendships.rpy:159'
          fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_friendships.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_friendships.rpy lines 246-249 ---'
          locator: 'source game/route_friendships.rpy:248'
          fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_friendships.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_friendships.rpy lines 343-346 ---'
          locator: 'source game/route_friendships.rpy:345'
          fingerprint: 'previous non-blank line in block: narrator "[kite_name] keeps glancing at [neo_obj] between other customers."'
          fact: 'The source displays the kite_male neutral image identifier.'
        - source_path: game/route_friendships.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_friendships.rpy lines 650-653 ---'
          locator: 'source game/route_friendships.rpy:652'
          fingerprint: 'previous non-blank line in block: narrator "[neo_name] is behind the counter — not working, just belonging. Leaning on the service side like [neo_subj] is allowed to be there."'
          fact: 'The source displays the kite_male neutral image identifier.'
- test_case: A
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
    - source_path: game/route_neo.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_neo.rpy lines 2610-2615 ---'
      locator: 'source game/route_neo.rpy:2614'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
  relationships:
    - related_asset: reference/kite_male_neutral.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:17'
          fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
        - source_path: game/route_neo.rpy.excerpt.txt
          anchor_type: statement
          anchor: 'show kite_male neutral at left'
          context: 'excerpt block marker: # --- route_neo.rpy lines 2610-2615 ---'
          locator: 'source game/route_neo.rpy:2614'
          fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
          fact: 'The source displays the kite_male neutral image identifier.'
- test_case: A
  item_type: CODE
  source_path: game/minigames.rpy.excerpt.txt
  file_status: DOWNSTREAM_USAGE
  reason: >-
    The source references or maps Kite production assets affected by the hairstyle change, but the existing filenames/image identifiers remain valid when the underlying asset pixels are replaced, so the source itself does not require editing.
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:19'
      fact: 'The frozen fixture maps the kite_male relaxed identifier to kite_male_relaxed.png.'
    - source_path: game/minigames.rpy.excerpt.txt
      anchor_type: assignment
      anchor: '"li": "kite_male relaxed",'
      context: 'excerpt block marker: # --- minigames.rpy lines 5202-5212 ---'
      locator: 'source game/minigames.rpy:5206'
      fingerprint: 'previous non-blank line in block: "accent": LOVE32_AMBER,'
      fact: 'The source sets the "li" value of the Cocktail Time gallery entry to the kite_male relaxed image identifier.'
  relationships:
    - related_asset: assets/kite_male_relaxed.png
      relationship_status: DOWNSTREAM_USAGE
      reason: >-
        The source references an affected production asset, but the Test A change alters the asset content rather than its existing identifier or source relationship, so the source remains valid without editing.
      evidence:
        - source_path: game/route_kite.rpy
          anchor_type: declaration
          anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
          context: 'init-time kite_male image declaration'
          locator: 'game/route_kite.rpy:19'
          fact: 'The frozen fixture maps the kite_male relaxed identifier to kite_male_relaxed.png.'
        - source_path: game/minigames.rpy.excerpt.txt
          anchor_type: assignment
          anchor: '"li": "kite_male relaxed",'
          context: 'excerpt block marker: # --- minigames.rpy lines 5202-5212 ---'
          locator: 'source game/minigames.rpy:5206'
          fingerprint: 'previous non-blank line in block: "accent": LOVE32_AMBER,'
          fact: 'The source sets the "li" value of the Cocktail Time gallery entry to the kite_male relaxed image identifier.'
```

### Test A: unresolved items

```yaml
unresolved_items:
  -
```

## Test B: outfit change

Exact request:

> Kite's canonical outfit changes to a materially different outfit.

Question:

> Which existing static production assets visually depict the changed outfit and therefore require action?

Start timing when the human receives the exact frozen test request and the frozen fixture. Stop when all required classifications and relationships for that test are complete.

```yaml
start_time:
end_time:
elapsed_time:
```

### Test B: ASSET records

```yaml
- id: B-ASSET-01
  test_case: B
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-02
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-03
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-04
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-05
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-06
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-07
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-08
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-09
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-10
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-11
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-12
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-13
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-14
  test_case: B
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: B-ASSET-15
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
- test_case: B
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: B
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

## Test C: small accessory change

Exact request:

> Kite's canonical small ear accessory changes.

Question:

> Which existing static production assets actually show the affected accessory and therefore require action?

Start timing when the human receives the exact frozen test request and the frozen fixture. Stop when all required classifications and relationships for that test are complete.

```yaml
start_time:
end_time:
elapsed_time:
```

### Test C: ASSET records

```yaml
- id: C-ASSET-01
  test_case: C
  item_type: ASSET
  asset_path: reference/kite_male_neutral.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-02
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_crossed_arms.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-03
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-04
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-05
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_dark_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-06
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_gentle.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-07
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_relaxed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-08
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_smoking.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-09
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_soft.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-10
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_stressed.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-11
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_tired.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-12
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_warm.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-13
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_male_withdrawn.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-14
  test_case: C
  item_type: ASSET
  asset_path: assets/kite_tattoo.png
  status:
  reason:
  evidence:
    -
  game_usage:
    -
- id: C-ASSET-15
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
- test_case: C
  item_type: CODE
  source_path: game/route_kite.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/li_sprite_normalization.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/side_portraits.rpy
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/credits.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/route_select.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/route_friendships.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
  item_type: CODE
  source_path: game/route_neo.rpy.excerpt.txt
  file_status:
  reason:
  evidence:
    -
  relationships:
    -
- test_case: C
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

## Structural relationship inventory

Fixture-derived from the frozen fixture only, identical for Tests A, B and C, and listed once. For each of the 8 eligible CODE units it enumerates every structurally established relationship to one of the 15 scored ASSET units:

- **Direct:** the CODE unit contains a literal path or filename of the asset, or an explicit image-identifier declaration naming it.
- **Fixture-proven (protocol §5.3):** the CODE unit uses an image identifier, and an explicit image-identifier declaration in the frozen fixture maps that identifier to the asset. Both the usage anchor and the mapping declaration anchor are cited.

Filename similarity and dynamically composed filenames are not used. There is one entry per CODE unit × ASSET pair; repeated occurrences are in that entry's `evidence` array, distinguished by `context` and/or `fingerprint`. Entries contain only `related_asset` and `evidence`. They carry no status.

### game/route_kite.rpy

```yaml
- related_asset: reference/kite_male_neutral.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The source declares the kite_male neutral image identifier as _kite_sprite("kite_male_neutral.png").'
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male angry = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:26'
      fact: 'The source declares the kite_male angry image identifier as _kite_sprite("kite_male_neutral.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:72'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:113'
      fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:131'
      fingerprint: 'previous non-blank line: show buddy neutral at buddy_first_night'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at kite_first_night'
      context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:177'
      fingerprint: 'previous non-blank line: narrator "He leaves it on the rail. Turns to the sink."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:568'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:698'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:798'
      fingerprint: "previous non-blank line: kite \"Fine is a word people use when they don't want to explain.\""
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:861'
      fingerprint: "previous non-blank line: kite \"Belonging somewhere doesn't mean it belongs back.\""
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1585'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1607'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2591'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_3_female; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2625'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_6_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3131'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_interaction_6_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3200'
      fingerprint: 'previous non-blank line: kite "Please."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3428'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male neutral at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3510'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3554'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male neutral image identifier as the "image" value of a pb_elements entry.'
- related_asset: assets/kite_male_crossed_arms.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male crossed_arms = _kite_sprite("kite_male_crossed_arms.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:27'
      fact: 'The source declares the kite_male crossed_arms image identifier as _kite_sprite("kite_male_crossed_arms.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2148'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male crossed_arms image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2179'
      fingerprint: "previous non-blank line: call screen email_message(sender=\"Verrerie Accounts\", subject=\"\", body=\"You think this is over? I'm always watching.\")"
      fact: 'The source displays the kite_male crossed_arms image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male crossed_arms at li_center'
      context: 'label kite_interaction_5_male; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2242'
      fingerprint: "previous non-blank line: kite \"The email said 'watching.' So did whatever just said that in my own voice.\""
      fact: 'The source displays the kite_male crossed_arms image identifier.'
- related_asset: assets/kite_male_gentle.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male gentle = _kite_sprite("kite_male_gentle.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:18'
      fact: 'The source declares the kite_male gentle image identifier as _kite_sprite("kite_male_gentle.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2207'
      fingerprint: 'previous non-blank line: pause 0.4'
      fact: 'The source displays the kite_male gentle image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_right'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2262'
      fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
      fact: 'The source displays the kite_male gentle image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male gentle at li_center'
      context: 'label kite_interaction_5_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2265'
      fingerprint: 'previous non-blank line: narrator "You sweep the glass into the bin. He watches once, then pretends not to."'
      fact: 'The source displays the kite_male gentle image identifier.'
- related_asset: assets/kite_male_relaxed.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:19'
      fact: 'The source declares the kite_male relaxed image identifier as _kite_sprite("kite_male_relaxed.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1675'
      fingerprint: 'previous non-blank line: scene bg street_night with fade'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 2 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1684'
      fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 3 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1710'
      fingerprint: 'previous non-blank line: $ remy_phone_soft_open()'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 4 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1722'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 5 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1726'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 6 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1730'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 7 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1740'
      fingerprint: 'previous non-blank line: kite "I know I kept them."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 8 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1749'
      fingerprint: 'previous non-blank line: scene bg player_apartment_night at bg_fill with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 9 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1781'
      fingerprint: 'previous non-blank line: narrator "Salt. Tequila. Lime. The first shot burns. By the third, his shoulders drop."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 10 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1810'
      fingerprint: 'previous non-blank line: scene bg bedroom_night with dissolve'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_3_male; occurrence 11 of 11 of this anchor in this label'
      locator: 'game/route_kite.rpy:1913'
      fingerprint: 'previous non-blank line: narrator "He tenses. Then relaxes. His head finds your shoulder."'
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_4_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1952'
      fingerprint: "previous non-blank line: \"He comes over. Yesterday's pants. Same henley.\""
      fact: 'The source displays the kite_male relaxed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male relaxed at li_center'
      context: 'label kite_interaction_4_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:2008'
      fingerprint: 'previous non-blank line: scene bg street_day with fade'
      fact: 'The source displays the kite_male relaxed image identifier.'
- related_asset: assets/kite_male_smoking.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male smoking = _kite_sprite("kite_male_smoking.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:20'
      fact: 'The source declares the kite_male smoking image identifier as _kite_sprite("kite_male_smoking.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male smoking at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1550'
      fingerprint: 'previous non-blank line: scene bg bar_exterior'
      fact: 'The source displays the kite_male smoking image identifier.'
- related_asset: assets/kite_male_soft.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male soft = _kite_sprite("kite_male_soft.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:21'
      fact: 'The source declares the kite_male soft image identifier as _kite_sprite("kite_male_soft.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:137'
      fingerprint: 'previous non-blank line: if result_key in ("balanced", "interesting"):'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 2 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:170'
      fingerprint: 'previous non-blank line: narrator "He slides it to your hand. Warm. Exact."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 3 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:185'
      fingerprint: 'previous non-blank line: narrator "He does. Small. Professional. Then pushes it to you."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at kite_first_night'
      context: 'label kite_interaction_1; occurrence 4 of 4 of this anchor in this label'
      locator: 'game/route_kite.rpy:192'
      fingerprint: 'previous non-blank line: narrator "He sets a water glass on the rail. No pour. No performance."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:622'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_expression_beat'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:643'
      fingerprint: 'previous non-blank line: narrator "You tap the bar where a glass would sit."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_expression_beat'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:720'
      fingerprint: "previous non-blank line: narrator \"You don't sit yet. He sets a glass down anyway.\""
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:760'
      fingerprint: 'previous non-blank line: narrator "You look at the bar top. Not at him."'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1160'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1405'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male soft image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male soft at li_center, li_look_away'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1417'
      fingerprint: 'previous non-blank line: kite "Promise?"'
      fact: 'The source displays the kite_male soft image identifier.'
- related_asset: assets/kite_male_stressed.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male stressed = _kite_sprite("kite_male_stressed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:22'
      fact: 'The source declares the kite_male stressed image identifier as _kite_sprite("kite_male_stressed.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, li_flinch, corrupt_tier2'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:725'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 2:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:734'
      fingerprint: 'previous non-blank line: kite "{stutter}W-why did I s-say that?{/stutter}"'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:738'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:764'
      fingerprint: 'previous non-blank line: elif birthday_choice == "skip":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_2; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:781'
      fingerprint: 'previous non-blank line: elif birthday_choice is not None:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:790'
      fingerprint: 'previous non-blank line: "I was with someone.":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1622'
      fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2231'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_5_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2290'
      fingerprint: 'previous non-blank line: $ stop_story_music(fadeout=1.2)'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_route_lockin; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2435'
      fingerprint: 'previous non-blank line: scene bg bar_night'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2563'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center, glitch_flicker, corrupt_tier3'
      context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3180'
      fingerprint: 'previous non-blank line: if persistent.corruption_tier >= 3:'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_ending_bad_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3568'
      fingerprint: "previous non-blank line: p \"I can't. This is too much.\""
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male stressed at li_center'
      context: 'label kite_ending_bad_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3586'
      fingerprint: 'previous non-blank line: with fade'
      fact: 'The source displays the kite_male stressed image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male stressed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_bad_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3624'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male stressed image identifier as the "image" value of a pb_elements entry.'
- related_asset: assets/kite_male_tired.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male tired = _kite_sprite("kite_male_tired.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:23'
      fact: 'The source declares the kite_male tired image identifier as _kite_sprite("kite_male_tired.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center, li_look_away'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:855'
      fingerprint: 'previous non-blank line: narrator "[kite_name] wipes down the counter again."'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:858'
      fingerprint: "previous non-blank line: kite \"Lease is up in eight months. Landlord's been sniffing around.\""
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center, li_look_away'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1155'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1643'
      fingerprint: 'previous non-blank line: if kite_came_inside_after_smoke:'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 1 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2013'
      fingerprint: 'previous non-blank line: scene bg bar_backroom with dissolve'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 2 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2026'
      fingerprint: 'previous non-blank line: scene bg bar_interior with dissolve'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_4_male; occurrence 3 of 3 of this anchor in this label'
      locator: 'game/route_kite.rpy:2056'
      fingerprint: 'previous non-blank line: scene bg bar_interior'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_interaction_6_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3150'
      fingerprint: 'previous non-blank line: else:'
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3498'
      fingerprint: "previous non-blank line: kite \"I know. You're saying not yet.\""
      fact: 'The source displays the kite_male tired image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male tired at li_center'
      context: 'label kite_ending_bittersweet_male; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:3521'
      fingerprint: "previous non-blank line: kite \"Same stool as night one. I didn't retire it.\""
      fact: 'The source displays the kite_male tired image identifier.'
- related_asset: assets/kite_male_warm.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:24'
      fact: 'The source declares the kite_male warm image identifier as _kite_sprite("kite_male_warm.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at kite_first_night'
      context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:141'
      fingerprint: 'previous non-blank line: elif result_key in ("messy_twice", "bitter_meaning"):'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at kite_first_night, li_lean_in'
      context: 'label kite_interaction_1; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:162'
      fingerprint: 'previous non-blank line: $ play_story_sfx("glass_set")'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_birthday_scene; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:423'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_interaction_2; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:748'
      fingerprint: 'previous non-blank line: if birthday_choice == "kite":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_interaction_2_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1088'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene; occurrence 1 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1201'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene; occurrence 2 of 2 of this anchor in this label'
      locator: 'game/route_kite.rpy:1281'
      fingerprint: 'previous non-blank line: narrator "He smiles, and this time it reaches his eyes."'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center'
      context: 'label kite_warm_scene_dense; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1314'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center, li_expression_beat'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1415'
      fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male warm at li_center, li_lean_in'
      context: 'label kite_warm_after_cocktail; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1429'
      fingerprint: 'previous non-blank line: $ meter_bump("kite", 2)'
      fact: 'The source displays the kite_male warm image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: assignment
      anchor: '$ pb_elements = [{"image": "kite_male warm", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]'
      context: 'label kite_ending_good_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:3478'
      fingerprint: 'previous non-blank line: $ stop_story_ambience(fadeout=0.8)'
      fact: 'The source lists the kite_male warm image identifier as the "image" value of a pb_elements entry.'
- related_asset: assets/kite_male_withdrawn.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male withdrawn = _kite_sprite("kite_male_withdrawn.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:25'
      fact: 'The source declares the kite_male withdrawn image identifier as _kite_sprite("kite_male_withdrawn.png").'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male withdrawn at li_center'
      context: 'label kite_interaction_3_male; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:1625'
      fingerprint: 'previous non-blank line: else:'
      fact: 'The source displays the kite_male withdrawn image identifier.'
    - source_path: game/route_kite.rpy
      anchor_type: statement
      anchor: 'show kite_male withdrawn at li_center'
      context: 'label kite_interaction_3_female; occurrence 1 of 1 of this anchor in this label'
      locator: 'game/route_kite.rpy:2633'
      fingerprint: 'previous non-blank line: if kite_variant == "male":'
      fact: 'The source displays the kite_male withdrawn image identifier.'
- related_asset: assets/kite_tattoo.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image evidence kite_tattoo = "images/evidence/kite_tattoo.png"'
      context: 'init-time image declaration'
      locator: 'game/route_kite.rpy:10'
      fact: 'The source declares the evidence kite_tattoo image identifier from the path images/evidence/kite_tattoo.png.'
```

### game/li_sprite_normalization.rpy

```yaml
- related_asset: reference/kite_male_neutral.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "angry"): "kite_male_neutral.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:189'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "angry") to the filename kite_male_neutral.png.'
- related_asset: assets/kite_male_crossed_arms.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "crossed_arms"): "kite_male_crossed_arms.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:190'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "crossed_arms") to the filename kite_male_crossed_arms.png.'
- related_asset: assets/kite_male_gentle.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_gentle.png": (1.011, -8),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:101'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_gentle.png.'
- related_asset: assets/kite_male_relaxed.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_relaxed.png": (1.002, -2),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:102'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_relaxed.png.'
- related_asset: assets/kite_male_smoking.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "smoking"): "kite_male_smoking.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:187'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "smoking") to the filename kite_male_smoking.png.'
- related_asset: assets/kite_male_soft.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '("kite_male", "soft"): "kite_male_soft.png",'
      context: 'LI_EXPR_ALIAS table'
      locator: 'game/li_sprite_normalization.rpy:188'
      fact: 'The LI_EXPR_ALIAS table maps ("kite_male", "soft") to the filename kite_male_soft.png.'
- related_asset: assets/kite_male_stressed.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_stressed.png": (0.996, 3),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:104'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_stressed.png.'
- related_asset: assets/kite_male_tired.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_tired.png": (0.971, 22),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:106'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_tired.png.'
- related_asset: assets/kite_male_warm.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_warm.png": (0.998, 2),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:103'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_warm.png.'
- related_asset: assets/kite_male_withdrawn.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"kite_male_withdrawn.png": (0.975, 19),'
      context: 'LI_ALIGN table'
      locator: 'game/li_sprite_normalization.rpy:105'
      fact: 'The LI_ALIGN table contains an entry keyed by the filename kite_male_withdrawn.png.'
- related_asset: assets/side_kite_male.png
  evidence:
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: config
      anchor: '"side_kite_male.png": (0.92, 1.0),'
      context: 'LI_CIRCLE_LOCK table'
      locator: 'game/li_sprite_normalization.rpy:149'
      fact: 'The LI_CIRCLE_LOCK table contains an entry keyed by the filename side_kite_male.png.'
    - source_path: game/li_sprite_normalization.rpy
      anchor_type: statement
      anchor: 'return "images/side_treated/side_kite_male.png"'
      context: 'function _li_circle_path'
      locator: 'game/li_sprite_normalization.rpy:166'
      fact: 'The _li_circle_path function returns the path images/side_treated/side_kite_male.png for names starting with kite_male or "kite ".'
```

### game/side_portraits.rpy

```yaml
- related_asset: assets/side_kite_male.png
  evidence:
    - source_path: game/side_portraits.rpy
      anchor_type: declaration
      anchor: 'image side kite_male      = _li_circle_lock("images/side_treated/side_kite_male.png")'
      context: 'side portrait image declarations'
      locator: 'game/side_portraits.rpy:24'
      fact: 'The source declares the side kite_male image identifier from the path images/side_treated/side_kite_male.png.'
```

### game/credits.rpy.excerpt.txt

```yaml
- related_asset: reference/kite_male_neutral.png
  evidence:
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_neutral.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:118'
      fingerprint: 'previous non-blank line in block: "images/kite_male_relaxed.png",'
      fact: 'The source lists the path images/kite_male_neutral.png in the male-branch _credits_first_ok candidate list.'
- related_asset: assets/kite_male_relaxed.png
  evidence:
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_relaxed.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:117'
      fingerprint: 'previous non-blank line in block: "images/kite_male_warm.png",'
      fact: 'The source lists the path images/kite_male_relaxed.png in the male-branch _credits_first_ok candidate list.'
- related_asset: assets/kite_male_warm.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male warm = _kite_sprite("kite_male_warm.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:24'
      fact: 'The frozen fixture maps the kite_male warm identifier to kite_male_warm.png.'
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: statement
      anchor: '"images/kite_male_warm.png",'
      context: 'excerpt block marker: # --- credits.rpy lines 106-120 ---; inside function _credits_kite_sprite_path()'
      locator: 'source game/credits.rpy:116'
      fingerprint: 'previous non-blank line in block: return _credits_first_ok(['
      fact: 'The source lists the path images/kite_male_warm.png in the male-branch _credits_first_ok candidate list.'
    - source_path: game/credits.rpy.excerpt.txt
      anchor_type: assignment
      anchor: 'li = "kite_female warm" if female else "kite_male warm"'
      context: 'excerpt block marker: # --- credits.rpy lines 164-176 ---'
      locator: 'source game/credits.rpy:168'
      fingerprint: 'previous non-blank line in block: female = getattr(store, "kite_variant", "male") == "female"'
      fact: 'The source assigns the kite_male warm image identifier to li when female is false.'
```

### game/route_select.rpy.excerpt.txt

```yaml
- related_asset: assets/side_kite_male.png
  evidence:
    - source_path: game/route_select.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'portrait = "images/side_treated/side_kite_male.png"'
      context: 'excerpt block marker: # --- route_select.rpy lines 54-64 ---'
      locator: 'source game/route_select.rpy:58'
      fingerprint: 'previous non-blank line in block: else:'
      fact: 'The source assigns the path images/side_treated/side_kite_male.png to portrait in the non-female branch.'
```

### game/route_friendships.rpy.excerpt.txt

```yaml
- related_asset: reference/kite_male_neutral.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 59-63 ---'
      locator: 'source game/route_friendships.rpy:62'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 157-160 ---'
      locator: 'source game/route_friendships.rpy:159'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 246-249 ---'
      locator: 'source game/route_friendships.rpy:248'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 343-346 ---'
      locator: 'source game/route_friendships.rpy:345'
      fingerprint: 'previous non-blank line in block: narrator "[kite_name] keeps glancing at [neo_obj] between other customers."'
      fact: 'The source displays the kite_male neutral image identifier.'
    - source_path: game/route_friendships.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_friendships.rpy lines 650-653 ---'
      locator: 'source game/route_friendships.rpy:652'
      fingerprint: 'previous non-blank line in block: narrator "[neo_name] is behind the counter — not working, just belonging. Leaning on the service side like [neo_subj] is allowed to be there."'
      fact: 'The source displays the kite_male neutral image identifier.'
```

### game/route_neo.rpy.excerpt.txt

```yaml
- related_asset: reference/kite_male_neutral.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male neutral = _kite_sprite("kite_male_neutral.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:17'
      fact: 'The frozen fixture maps the kite_male neutral identifier to kite_male_neutral.png.'
    - source_path: game/route_neo.rpy.excerpt.txt
      anchor_type: statement
      anchor: 'show kite_male neutral at left'
      context: 'excerpt block marker: # --- route_neo.rpy lines 2610-2615 ---'
      locator: 'source game/route_neo.rpy:2614'
      fingerprint: 'previous non-blank line in block: if kite_variant == "male":'
      fact: 'The source displays the kite_male neutral image identifier.'
```

### game/minigames.rpy.excerpt.txt

```yaml
- related_asset: assets/kite_male_relaxed.png
  evidence:
    - source_path: game/route_kite.rpy
      anchor_type: declaration
      anchor: 'image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")'
      context: 'init-time kite_male image declaration'
      locator: 'game/route_kite.rpy:19'
      fact: 'The frozen fixture maps the kite_male relaxed identifier to kite_male_relaxed.png.'
    - source_path: game/minigames.rpy.excerpt.txt
      anchor_type: assignment
      anchor: '"li": "kite_male relaxed",'
      context: 'excerpt block marker: # --- minigames.rpy lines 5202-5212 ---'
      locator: 'source game/minigames.rpy:5206'
      fingerprint: 'previous non-blank line in block: "accent": LOVE32_AMBER,'
      fact: 'The source sets the "li" value of the Cocktail Time gallery entry to the kite_male relaxed image identifier.'
```
