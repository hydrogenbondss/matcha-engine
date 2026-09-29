# Experiment 01: provenance note

This note is additive. It records facts about the state of Experiment 01's frozen inputs and the evaluator result. It does not change any Experiment 01 classification, timing, fixture, protocol, inventory, or worksheet, and it does not interpret whether Matcha succeeded or failed.

## Frozen inputs

- The structural evidence protocol, `docs/experiments/EVIDENCE-PROTOCOL-01.md`, remained frozen at commit `e93f0da`. Its blob in this commit is identical to its blob at `e93f0da`.
- The fixture, `fixtures/kite-production/`, remained frozen at commit `c1364f4`. Its tree in this commit is identical to its tree at `c1364f4`.
- The worksheet with the structural inventory and the Tests A/B/C records, `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`, is unchanged by this note.

## Known strict evidence mismatch in the structural inventory

`scripts/impact_eval.py validate-inventory` compares the evidence the scanner discovers with the frozen structural inventory:

| Layer | Result |
|---|---|
| CODE x ASSET pairs | PASS, 30/30 |
| Strict evidence identity (`source_path` + `anchor_type` + `anchor`, protocol §5.1) | FAIL, 126/127 |
| Evidence identity after the documented `statement`/`assignment` binding normalization (diagnostic) | PASS, 127/127 |
| Evidence occurrence alignment | PASS, 127/127 |

The single strict difference is in `game/route_select.rpy.excerpt.txt` for `assets/side_kite_male.png`, at `source game/route_select.rpy:58`: the anchor `portrait = "images/side_treated/side_kite_male.png"` has `anchor_type: statement` in the inventory and `anchor_type: assignment` from the scanner.

Strict evidence identity is authoritative in the evaluator, so `validate-inventory` returns overall `FAIL` with exit code `2`. The normalization is reported only as an explanation of the strict difference.

## Human-baseline records

The recorded Test A and Test B human-baseline work was AI-assisted. It must not be treated as an independent, unaided human benchmark.

## Scope of this note

This note does not change any Experiment 01 classification, timing, fixture, or protocol.
