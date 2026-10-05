# Matcha impact report

- Request: Kite's canonical small ear accessory changes.
- Reference asset: `reference/kite_male_neutral.png` (sha256 b3469eeed8510f5ae0807cafc8564b21b9be617a3a27027f7eca6d230c0da07d)
- Fixture: `/Users/jeffreytse/Projects/matcha-engine-e2-M-d6092e9/fixtures/kite-production` (manifest sha256 6453f313d5767c498ffc29fd3e7a7e85b816d743a5485a5f71cad3370c93e1b1)
- Provider: **unavailable** (state: UNAVAILABLE; no available vision provider found by discovery)
- Identifier policy: preserved (request describes a visual design change and names no new file names, paths or image identifiers, so existing identifiers are treated as remaining valid)
- Timing: 2026-10-03T16:33:27+08:00 -> 2026-10-03T16:33:28+08:00 (00:00:00.860)

> **Provider unavailable.** No visual judgement was made; every asset is REVIEW_REQUIRED.

Missing for a real provider:

- no cloud vision API key present in the environment
- ollama server not reachable at http://127.0.0.1:11434
- llama.cpp binaries present but no llama.cpp adapter/multimodal model is configured

## Analysis completeness

- Analysis completeness: **INCOMPLETE**
- Statically established relationships: 30
- Unresolved dependencies: 19 (dynamic_reference 19)
- 30 CODE-to-ASSET relationship(s) were statically established. This is NOT a claim that all production dependencies were established: 19 unresolved dependency item(s) (dynamic_reference 19) could hide further relationships.
- Provider execution (separate, operational): state UNAVAILABLE; 0/15 assets have valid provider output.

## Counts

- ASSET: 15 — REVIEW_REQUIRED 15
- CODE: 8 — REVIEW_REQUIRED 8
- Relationships: 30 — REVIEW_REQUIRED 30
- Relationship evidence items: 127
- Unresolved items: 23 (dynamic_reference 19, no_static_relationship 3, provider_unavailable 1)
- Asset provider states: UNAVAILABLE 15
- Asset review causes: PROVIDER_UNAVAILABLE 15

## Assets

| Asset | Candidate id | Status | Provider state | Review cause | Confidence | Reason | Game usage | Dynamic candidates |
|---|---|---|---|---|---|---|---|---|
| `reference/kite_male_neutral.png` | candidate-01 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 27 | 5 |
| `assets/kite_male_gentle.png` | candidate-02 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 5 | 5 |
| `assets/kite_male_stressed.png` | candidate-03 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 17 | 5 |
| `assets/kite_male_warm.png` | candidate-04 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 15 | 5 |
| `assets/kite_male_withdrawn.png` | candidate-05 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 4 | 5 |
| `assets/kite_male_crossed_arms.png` | candidate-06 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 5 | 5 |
| `assets/kite_male_relaxed.png` | candidate-07 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 17 | 5 |
| `assets/kite_male_smoking.png` | candidate-08 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 3 | 5 |
| `assets/kite_male_soft.png` | candidate-09 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 13 | 5 |
| `assets/kite_male_tired.png` | candidate-10 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 12 | 5 |
| `assets/kite_male_dark.png` | candidate-11 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 0 | 5 |
| `assets/kite_male_dark_relaxed.png` | candidate-12 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 0 | 5 |
| `assets/kite_male_dark_withdrawn.png` | candidate-13 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 0 | 5 |
| `assets/side_kite_male.png` | candidate-14 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 4 | 4 |
| `assets/kite_tattoo.png` | candidate-15 | REVIEW_REQUIRED | UNAVAILABLE | PROVIDER_UNAVAILABLE | - | provider unavailable | 1 | 4 |

## CODE units

| Source | File status | Relationships |
|---|---|---|
| `game/credits.rpy.excerpt.txt` | REVIEW_REQUIRED | 3 (REVIEW_REQUIRED 3) |
| `game/li_sprite_normalization.rpy` | REVIEW_REQUIRED | 11 (REVIEW_REQUIRED 11) |
| `game/minigames.rpy.excerpt.txt` | REVIEW_REQUIRED | 1 (REVIEW_REQUIRED 1) |
| `game/route_friendships.rpy.excerpt.txt` | REVIEW_REQUIRED | 1 (REVIEW_REQUIRED 1) |
| `game/route_kite.rpy` | REVIEW_REQUIRED | 11 (REVIEW_REQUIRED 11) |
| `game/route_neo.rpy.excerpt.txt` | REVIEW_REQUIRED | 1 (REVIEW_REQUIRED 1) |
| `game/route_select.rpy.excerpt.txt` | REVIEW_REQUIRED | 1 (REVIEW_REQUIRED 1) |
| `game/side_portraits.rpy` | REVIEW_REQUIRED | 1 (REVIEW_REQUIRED 1) |

## Relationships

| Source | Asset | Status | Basis | Evidence |
|---|---|---|---|---|
| `game/credits.rpy.excerpt.txt` | `reference/kite_male_neutral.png` | REVIEW_REQUIRED | direct | 1 |
| `game/credits.rpy.excerpt.txt` | `assets/kite_male_warm.png` | REVIEW_REQUIRED | direct, fixture_proven | 3 |
| `game/credits.rpy.excerpt.txt` | `assets/kite_male_relaxed.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `reference/kite_male_neutral.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_gentle.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_stressed.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_warm.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_withdrawn.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_crossed_arms.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_relaxed.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_smoking.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_soft.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/kite_male_tired.png` | REVIEW_REQUIRED | direct | 1 |
| `game/li_sprite_normalization.rpy` | `assets/side_kite_male.png` | REVIEW_REQUIRED | direct | 2 |
| `game/minigames.rpy.excerpt.txt` | `assets/kite_male_relaxed.png` | REVIEW_REQUIRED | fixture_proven | 2 |
| `game/route_friendships.rpy.excerpt.txt` | `reference/kite_male_neutral.png` | REVIEW_REQUIRED | fixture_proven | 6 |
| `game/route_kite.rpy` | `reference/kite_male_neutral.png` | REVIEW_REQUIRED | direct | 19 |
| `game/route_kite.rpy` | `assets/kite_male_gentle.png` | REVIEW_REQUIRED | direct | 4 |
| `game/route_kite.rpy` | `assets/kite_male_stressed.png` | REVIEW_REQUIRED | direct | 16 |
| `game/route_kite.rpy` | `assets/kite_male_warm.png` | REVIEW_REQUIRED | direct | 12 |
| `game/route_kite.rpy` | `assets/kite_male_withdrawn.png` | REVIEW_REQUIRED | direct | 3 |
| `game/route_kite.rpy` | `assets/kite_male_crossed_arms.png` | REVIEW_REQUIRED | direct | 4 |
| `game/route_kite.rpy` | `assets/kite_male_relaxed.png` | REVIEW_REQUIRED | direct | 14 |
| `game/route_kite.rpy` | `assets/kite_male_smoking.png` | REVIEW_REQUIRED | direct | 2 |
| `game/route_kite.rpy` | `assets/kite_male_soft.png` | REVIEW_REQUIRED | direct | 12 |
| `game/route_kite.rpy` | `assets/kite_male_tired.png` | REVIEW_REQUIRED | direct | 11 |
| `game/route_kite.rpy` | `assets/kite_tattoo.png` | REVIEW_REQUIRED | direct | 1 |
| `game/route_neo.rpy.excerpt.txt` | `reference/kite_male_neutral.png` | REVIEW_REQUIRED | fixture_proven | 2 |
| `game/route_select.rpy.excerpt.txt` | `assets/side_kite_male.png` | REVIEW_REQUIRED | direct | 1 |
| `game/side_portraits.rpy` | `assets/side_kite_male.png` | REVIEW_REQUIRED | direct | 1 |

## CODE candidates out of scoring scope

- `game/characters.rpy`: no relationship to a scored asset was found (not scored)
- `game/options.rpy.excerpt.txt`: no relationship to a scored asset was found (not scored)
- `game/screens.rpy.excerpt.txt`: no relationship to a scored asset was found (not scored)

## Unresolved items

- [provider_unavailable] Vision provider unavailable: no asset was visually classified, so every ASSET is REVIEW_REQUIRED and every relationship follows. Missing: no cloud vision API key present in the environment; ollama server not reachable at http://127.0.0.1:11434; llama.cpp binaries present but no llama.cpp adapter/multimodal model is configured
- [dynamic_reference] game/li_sprite_normalization.rpy:177: dynamic image/file reference not resolved to a scored asset (renpy.loadable() is called with a non-literal argument 'rel_path').
- [dynamic_reference] game/li_sprite_normalization.rpy:206: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:210: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:212: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:214: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:216: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:218: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:220: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:248: dynamic image/file reference not resolved to a scored asset (call to _li_expr_filename(), whose body builds image paths dynamically, with the non-literal argument 'tag').
- [dynamic_reference] game/li_sprite_normalization.rpy:259: dynamic image/file reference not resolved to a scored asset (call to _li_circle_lock(), whose body builds image paths dynamically, with the non-literal argument 'rel_path').
- [dynamic_reference] game/li_sprite_normalization.rpy:272: dynamic image/file reference not resolved to a scored asset (renpy.loadable() is called with a non-literal argument 'rel_path').
- [dynamic_reference] game/li_sprite_normalization.rpy:276: dynamic image/file reference not resolved to a scored asset (renpy.loadable() is called with a non-literal argument 'circle').
- [dynamic_reference] game/li_sprite_normalization.rpy:278: dynamic image/file reference not resolved to a scored asset (call to _li_circle_lock(), whose body builds image paths dynamically, with the non-literal argument 'circle').
- [dynamic_reference] game/li_sprite_normalization.rpy:295: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:309: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/li_sprite_normalization.rpy:317: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/route_kite.rpy:40: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/route_kite.rpy:41: dynamic image/file reference not resolved to a scored asset (string concatenation builds an image/file path).
- [dynamic_reference] game/route_kite.rpy:42: dynamic image/file reference not resolved to a scored asset (renpy.loadable() is called with a non-literal argument 'path').
- [no_static_relationship] assets/kite_male_dark.png: no static relationship from any scanned CODE unit was found; 5 dynamic reference(s) might resolve to it (game/li_sprite_normalization.rpy:212, game/li_sprite_normalization.rpy:295, game/li_sprite_normalization.rpy:309, game/li_sprite_normalization.rpy:317, game/route_kite.rpy:41), so it must not be treated as unreferenced; 14 dynamic reference(s) without a literal prefix could resolve to any asset, so absence of a static relationship does not prove it unreferenced.
- [no_static_relationship] assets/kite_male_dark_relaxed.png: no static relationship from any scanned CODE unit was found; 5 dynamic reference(s) might resolve to it (game/li_sprite_normalization.rpy:212, game/li_sprite_normalization.rpy:295, game/li_sprite_normalization.rpy:309, game/li_sprite_normalization.rpy:317, game/route_kite.rpy:41), so it must not be treated as unreferenced; 14 dynamic reference(s) without a literal prefix could resolve to any asset, so absence of a static relationship does not prove it unreferenced.
- [no_static_relationship] assets/kite_male_dark_withdrawn.png: no static relationship from any scanned CODE unit was found; 5 dynamic reference(s) might resolve to it (game/li_sprite_normalization.rpy:212, game/li_sprite_normalization.rpy:295, game/li_sprite_normalization.rpy:309, game/li_sprite_normalization.rpy:317, game/route_kite.rpy:41), so it must not be treated as unreferenced; 14 dynamic reference(s) without a literal prefix could resolve to any asset, so absence of a static relationship does not prove it unreferenced.

## Provenance

- Engine git commit: d6092e993672408a8235e9e9ac9a94f25e004ccb
- Engine worktree dirty (tracked or untracked changes): no
- Fixture manifest sha256: 6453f313d5767c498ffc29fd3e7a7e85b816d743a5485a5f71cad3370c93e1b1
- Reference: `reference/kite_male_neutral.png` sha256 b3469eeed8510f5ae0807cafc8564b21b9be617a3a27027f7eca6d230c0da07d
- Provider: unavailable / model - (state UNAVAILABLE)
- Provider model identity: none
- Vision prompt template sha256: 8440896196edeca3af996aefa7056da98262f5d2d8e5115c909b5390b9016c4a
- Vision module sha256: 3a43cbfeb46dd318eace6382b6401269909d4493b197754ed357913795572723
- Rendered prompt sha256: none (no prompt rendered) (SHA-256 of the exact prompt Matcha renders from the request and reference-presence state; a reproducibility fingerprint, not proof of network delivery; provider availability and execution state are reported separately)

## Limitations (v1)

- CODE_ACTION is derived only from the identifier policy: an affected asset with preserved identifiers propagates to DOWNSTREAM_USAGE and with changed identifiers to CODE_ACTION. v1 does not independently understand semantic source edits a visual change may require (e.g. dialogue or narration describing the old look, alignment/crop/offset tables tuned to the old art, comments documenting the old design).
- The identifier policy is a keyword heuristic over the request text; 'auto' yields only 'preserved' or 'unknown', never 'changed'. 'changed' is a manual assertion via --identifier-policy.
- Provider confidence is recorded as metadata only; it never changes a verdict, and there is no confidence threshold. A determinate provider verdict is reported as given, even at low confidence.
- Dynamic image/file references (concatenation, formatting, show expression, image-loading calls with non-literal arguments, calls to helpers that build paths dynamically) are surfaced as unresolved items and never resolved or counted as relationships.
- Ren'Py automatic image names (declared implicitly from files under images/) and ATL image blocks are not modelled.
- Excerpt block markers are trusted; their ranges are not cross-checked against the excerpt header.
- The vision provider receives only the request, the reference image and the candidate image; it does not receive written design documentation.
