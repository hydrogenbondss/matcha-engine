# Experiment 2: design (H / M / H+M production-work pilot)

Status: design and blank worksheets only. This document does not run Matcha, a provider or any benchmark, does not record any classification or timing, and does not declare success or failure.

```text
Base commit (branch matcha-2-impact-engine-v1-hardening): e47283b9e68f9d25a43cbb74eb81efe3662965d0
Protocol commit (docs/experiments/EVIDENCE-PROTOCOL-01.md): e93f0da4dfccd4498b485d23e51147bf9c256a3b
Fixture commit (fixtures/kite-production/): c1364f48ff92b248b3cd2aa7729c6014648008aa
Worksheets: docs/experiments/EXPERIMENT-02-HUMAN-BASELINE.md (H)
            docs/experiments/EXPERIMENT-02-ASSISTED-REVIEW.md (H+M)
```

Paths are relative to the fixture root `fixtures/kite-production/` unless they start with `docs/`, `matcha/` or `scripts/` (repository paths), as in the protocol.

## 1. Product thesis and experimental question

Product thesis:

> "Matcha should reduce the production work required to understand the impact of canonical design changes."

Thesis context (the motivating question):

> "Does Matcha reduce the human production work required to determine which existing assets and production dependencies are affected by a canonical visual design change?"

Key H+M comparison question for this pilot:

> "How much human investigative work remains after Matcha produces its first-pass impact analysis, and what errors, omissions, false positives, or unresolved cases does human verification uncover?"

This experiment is evidence toward the product thesis, not a statistically powered proof of it. A three-case, single-participant pilot cannot establish causal time savings (§14, limitations 2 and 3).

## 2. Frozen inputs

- **Fixture:** `fixtures/kite-production/`, frozen at `c1364f4`. It is not modified by Experiment 2.
- **Protocol:** `docs/experiments/EVIDENCE-PROTOCOL-01.md`, frozen at `e93f0da`. Experiment 2 uses its scored units (15 ASSET units, §4.1; 8 eligible CODE units, §4.3), its record schemas (Decision 5, §5), its evidence rules (§5.1, §5.3), its status definitions and its file-status derivation (§6). It is not modified by Experiment 2.
- **Reference:** `reference/kite_male_neutral.png` (the frozen production neutral, protocol §11).
- **Frozen cases:** the Experiment 1 Test A/B/C requests, reused verbatim (§3).
- Not modified by Experiment 2: `fixtures/kite-production/`, `docs/experiments/KITE-FIXTURE-01.md`, `docs/experiments/EVIDENCE-PROTOCOL-01.md`, and the Experiment 1 worksheet and records (`docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`, `docs/experiments/EXPERIMENT-01-PROVENANCE.md`).

## 3. Frozen cases

The request and question wording below is copied verbatim from `docs/experiments/EVIDENCE-PROTOCOL-01.md` §9 (identical to the wording in `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`). Only the wording is reused; no Experiment 1 answer, classification, reason or evidence is carried into Experiment 2. The per-test notes in protocol §9 continue to apply. No case is added and no request is modified.

### Test A: major hair change

Exact request:

> Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair.

Question:

> Which existing static production assets require regeneration or review because of this change?

### Test B: outfit change

Exact request:

> Kite's canonical outfit changes to a materially different outfit.

Question:

> Which existing static production assets visually depict the changed outfit and therefore require action?

### Test C: small accessory change

Exact request:

> Kite's canonical small ear accessory changes.

Question:

> Which existing static production assets actually show the affected accessory and therefore require action?

## 4. Fixture interpretation

The frozen fixture remains authoritative. Its documentation notes that the production canonical-reference history is not completely settled (§14, limitation 1); the fixture is not fixed or changed for Experiment 2, and that ambiguity is carried as an explicit Experiment 2 limitation.

## 5. Participant

- H and H+M use the **same human participant**. For this pilot this is one within-person comparison.
- No second participant is used or recruited.
- Consequence: see §14, limitation 3.

## 6. Conditions

### 6.1 H: human alone

- **Receives:** the frozen request, the frozen Kite fixture and the fixed experiment scope (the 15 scored ASSET units, the 8 eligible CODE units, the record schemas and the status definitions of the frozen protocol). The human independently performs the impact investigation, including independently discovering the CODE/ASSET relationships.
- **Must NOT receive:**
  - ChatGPT classification help;
  - Grok Bot classification help;
  - Matcha output;
  - Experiment 1 answers while performing the baseline;
  - the Experiment 1 structural relationship inventory (§6.1.1).
- **Records** (in `docs/experiments/EXPERIMENT-02-HUMAN-BASELINE.md`):
  - start time, end time, elapsed time;
  - ASSET classifications;
  - ASSET reasons/evidence;
  - CODE/dependency conclusions;
  - unresolved items;
  - optional notes on the work required.

#### 6.1.1 Why H does not receive the Experiment 1 relationship inventory

The structural relationship inventory in `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md` is an engineered, precomputed enumeration of the CODE × ASSET relationships. Giving it to H would precompute part of the dependency-discovery work that Matcha is intended to reduce. H therefore discovers the relationships from the frozen fixture, and the inventory is not added to or reproduced in the H worksheet.

### 6.2 M: Matcha alone

- **Receives:** the same frozen request, fixture, reference and protocol.
- **Must NOT receive:** the human baseline.
- **Records:**
  - the complete Matcha report;
  - machine runtime;
  - provider/model identity;
  - provenance (the report's `provenance` block);
  - Matcha ASSET/CODE classifications;
  - unresolved items;
  - completeness;
  - output artefacts.
- **Output storage:** §10.

### 6.3 H+M: human with Matcha

- **Receives:** after all three Matcha reports are frozen (§7), the same participant receives the frozen Matcha report for each test and verifies/corrects it to produce the final production-impact answer.
- **Records** (in `docs/experiments/EXPERIMENT-02-ASSISTED-REVIEW.md`):
  - human verification start time, end time, elapsed time;
  - corrections made to Matcha;
  - missed impacts discovered by the human;
  - unnecessary impacts removed by the human;
  - remaining `REVIEW_REQUIRED` items;
  - final verified classification;
  - final verified dependency conclusion;
  - notes on what the human had to inspect or resolve.

## 7. Execution order

The execution order is fixed:

1. **H:** Test A → Test B → Test C.
2. **Freeze** the completed H baseline.
3. **M:** Test A → Test B → Test C.
4. **Freeze** all three Matcha reports.
5. **H+M:** Test A → Test B → Test C.

H occurs before any Matcha exposure, to protect the clean human baseline from Matcha contamination. Conditions are not interleaved by case.

## 8. Blinding

- H: no ChatGPT classification help, no Grok Bot classification help, no Matcha output, no Experiment 1 answers and no Experiment 1 relationship inventory while performing the baseline. H is completed and frozen before any Matcha output exists for the participant to see (§7).
- M: the human baseline is not provided to Matcha.
- H+M: the participant receives the Matcha reports only after all three are frozen (§7).

## 9. Timing rules

- Machine time and human time are kept separate.
- Matcha runtime (M) is never combined with human verification time (H+M).
- H records human start, end and elapsed time per case.
- M records Matcha machine runtime per case.
- H+M records human verification start, end and elapsed time per case.

## 10. Matcha report storage and run provenance

- Live Matcha benchmark outputs are initially written **outside the Git repository**, in an external benchmark-output directory: `<external-experiment-02-output-dir>/`. No absolute path is fixed by this design.
- Reason: the benchmark's engine provenance should record `engine.git_worktree_dirty = false`.
- The reports are generated from a clean worktree. External output storage does not modify the source repository.
- After the benchmark, the reports may be archived into the experiment branch as a separate archival action.
- Any later archival commit must not be confused with the engine commit recorded in the run provenance (`engine.git_commit`).

## 11. Correction and verification recording (H+M)

For each case, the H+M worksheet records, against the frozen Matcha report for that case:

- the Matcha report reference (report path under `<external-experiment-02-output-dir>/` and the provenance fields: engine `git_commit`, `git_worktree_dirty`, fixture manifest sha256, reference sha256, provider/model identity, prompt hashes);
- human verification start, end and elapsed time;
- every correction to Matcha (item, Matcha value, corrected value, reason, evidence);
- missed impacts discovered by the human;
- false/unnecessary Matcha impacts removed by the human;
- `REVIEW_REQUIRED` items remaining after verification;
- the final verified ASSET state (15 records) and final verified CODE/dependency state (8 records with relationships);
- notes on what the human had to inspect or resolve.

## 12. Comparison and measurements (descriptive only)

Experiment 2 compares:

1. human-alone work (H);
2. Matcha output quality (M);
3. human-with-Matcha verification work (H+M).

The key H+M comparison is the question in §1: "How much human investigative work remains after Matcha produces its first-pass impact analysis, and what errors, omissions, false positives, or unresolved cases does human verification uncover?"

Measurements, reported per case (A, B, C) and as descriptive totals where appropriate:

- H elapsed time;
- M machine runtime (reported separately; never added to human time);
- H+M verification elapsed time;
- corrections to Matcha;
- missed impacts discovered by the human;
- unnecessary impacts removed by the human;
- `REVIEW_REQUIRED` items remaining after verification;
- final verified state (ASSET and CODE/dependency);
- notes on what the human had to inspect or resolve.

The most important H+M evidence is the actual work remaining after Matcha (the corrections, missed impacts, unnecessary impacts removed, remaining `REVIEW_REQUIRED` items, and what the human had to inspect or resolve), not merely elapsed time. H vs H+M elapsed time is descriptive evidence only (§14, limitation 3).

No arbitrary accuracy thresholds are defined. There is no overall pass/fail score for the three cases. A/B/C is a small controlled pilot with diagnostic value.

## 13. Relationship to Experiment 1

- The recorded Experiment 1 Test A and Test B human-baseline work was AI-assisted (`docs/experiments/EXPERIMENT-01-PROVENANCE.md`, "Human-baseline records").
- Experiment 1 Test C is not provenance-certified as unaided.
- Experiment 1 must not be silently reused as clean ground truth for Experiment 2.
- Experiment 2 reuses only the frozen request wording, the frozen fixture and the frozen protocol. It does not change any Experiment 1 classification, timing, fixture, protocol or worksheet.

## 14. Limitations

1. **Canonical-reference ambiguity.** `docs/experiments/KITE-FIXTURE-01.md` §5, subsection "Canonical reference" (the final bullet) records that the frozen HEAD neutral does not match the approved KEEP plate and states: "Which one is "canonical" is not settled by the evidence; all three images are included." §9 ("Known Blind Spots", "Post-approval edit is undocumented") records that the change between the approved neutral (KEEP) and the HEAD neutral is not described in any file read. Protocol §11 treats `reference/kite_male_neutral.png` as the frozen production-baseline asset and the approved-reference material as evidence. The fixture is not fixed for Experiment 2; the ambiguity remains.
2. **Small pilot.** n = 3 cases (A, B, C), one participant. It is not statistically powered.
3. **Within-person comparison and prior exposure.** H and H+M use the same participant (§5). After completing H, the participant has prior exposure to each case and cannot be treated as cognitively fresh for H+M. Therefore H vs H+M elapsed time is descriptive evidence only, not clean causal proof of time savings. H+M primarily measures the remaining human verification/investigation work after Matcha's first-pass analysis.
4. **Same fixture.** All three cases use the same frozen Kite fixture (one character, one production).
5. **Known strict-identity inventory mismatch.** Per `docs/experiments/EXPERIMENT-01-PROVENANCE.md`, `scripts/impact_eval.py validate-inventory` reports strict evidence identity 126/127 against the Experiment 1 structural inventory (normalized and occurrence layers 127/127); the single difference is the `anchor_type` of `portrait = "images/side_treated/side_kite_male.png"` in `game/route_select.rpy.excerpt.txt` (`statement` in the inventory, `assignment` from the scanner). The evaluator returns overall FAIL, exit code 2.
6. **Protocol limitations.** The limitations in protocol §19 continue to apply (videos, audio, backgrounds and UI/namebox assets excluded; female Kite excluded; dev/archive/backup material excluded; LOVE32 working tree differs from HEAD; approved v19g reference differs from the frozen production neutral; outfit per plate not explicitly encoded; some sprites unreferenced; some CODE evidence excerpted; fixture game source not executed).
7. **Matcha v1 limitations (facts, as listed in `matcha/impact/propagate.py` `V1_LIMITATIONS` at the base commit and emitted in each report's `limitations` field):**
   - `CODE_ACTION` is derived only from the identifier policy; v1 does not independently understand semantic source edits a visual change may require.
   - The identifier policy is a keyword heuristic over the request text; `auto` yields only `preserved` or `unknown`, never `changed`.
   - Provider confidence is metadata only; it never changes a verdict, and there is no confidence threshold.
   - Dynamic image/file references are surfaced as unresolved items and never resolved or counted as relationships.
   - Ren'Py automatic image names and ATL image blocks are not modelled.
   - Excerpt block markers are trusted; their ranges are not cross-checked against the excerpt header.
   - The vision provider receives only the request, the reference image and the candidate image; it does not receive written design documentation.

   Also at the base commit (not part of `V1_LIMITATIONS`):
   - With no available vision provider, no visual judgement is made and every ASSET is `REVIEW_REQUIRED` (`matcha/impact/report.py`).
   - `engine.git_commit` identifies the engine commit; uncommitted state is reported only as the boolean `engine.git_worktree_dirty` (`matcha/impact/provenance.py`).
