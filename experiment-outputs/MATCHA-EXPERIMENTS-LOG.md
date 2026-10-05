# Matcha 2.0 experiments log

Factual, chronological record of the Matcha 2.0 work done to date in this repository and on Jeffrey's Mac. Written 2026-10-05 (HKT) on branch `matcha-2-experiment-02`, parent commit `ebb2384`.

All times are HKT (UTC+8) unless marked otherwise. Commit times come from `git log --date=iso-strict`.

Evidence labels:

- **PROVEN**: backed by git objects in this repository (`git log --all`, `git show`, `git rev-parse`) or by files copied verbatim into `experiment-outputs/`, or by machine state read when this log was written.
- **INFERRED**: follows from the evidence but isn't stated directly by it.
- **UNPROVEN**: reported in the working session, but not backed by git or files and not re-verified for this log.

This log makes no judgment about whether Matcha succeeds or fails.

---

## 1. Frozen fixture and evidence protocol (2026-09-28)

| Item | Commit | Time | Evidence |
|---|---|---|---|
| Frozen fixture `fixtures/kite-production/` (31 files) and `docs/experiments/KITE-FIXTURE-01.md` | `c1364f48ff92b248b3cd2aa7729c6014648008aa` on `matcha-2-kite-fixture` | 2026-09-28 12:20:32 | PROVEN |
| Fixture tree object `fixtures/kite-production` | `9f8fbe99affbfa0b55acb182fb89029d2eb30a11` | n/a | PROVEN (identical at `c1364f4`, `d6092e9` and `ebb2384`) |
| `docs/experiments/EVIDENCE-PROTOCOL-01.md` defined | `495087c` | 2026-09-28 12:37:23 | PROVEN |
| Protocol frozen | `d4dab96` | 2026-09-28 12:54:31 | PROVEN |
| Protocol corrected (stable anchors) | `2eea32c` | 2026-09-28 15:31:04 | PROVEN |
| Protocol: evidence occurrence identity clarified (head of `matcha-2-evidence-protocol-1`) | `e93f0da` | 2026-09-28 16:08:01 | PROVEN |

The fixture's parent commit is `65bb0f5`. Local `matcha-2-kite-fixture` tracks `origin/main`, while `origin/matcha-2-kite-fixture` is also at `c1364f4`. PROVEN.

## 2. Experiment 1: human baseline (2026-09-28 to 2026-09-29)

Branch `matcha-2-experiment-01-baseline`, head `36426d8`. Worksheet `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md`. Its header pins protocol commit `e93f0da…` and fixture commit `c1364f4…`, with denominators ASSET 15 and CODE 8. PROVEN.

Jeffrey made the classifications. The agent recorded them, one commit per answer or group of answers. (Roles: UNPROVEN in git, because every commit is authored as Jeffrey Tse. Reported in the session.)

| Commit | Time | Subject |
|---|---|---|
| `9e9eb68` | 09-28 16:14:55 | Prepare Experiment 1 human baseline (blank worksheet) |
| `9eb7949` | 09-29 00:51:48 | Record Test A start time and A-ASSET-01 |
| `863a7e2` | 09-29 00:56:54 | Record A-ASSET-02 |
| `8729a46` | 09-29 01:06:53 | Record A-ASSET-03 through A-ASSET-15 |
| `50751ff` | 09-29 01:14:24 | Record Test A CODE baseline (**prefilled by the agent, not Jeffrey's classifications**) |
| `4a996ce` | 09-29 01:25:45 | Revert "Record Test A CODE baseline" (reverts `50751ff`) |
| `9b7d269` | 09-29 01:41:00 | Record Test A CODE baseline (human evaluator) |
| `6cff975` | 09-29 01:48:11 | Stop Test A timer |
| `331378a` | 09-29 02:30:59 | Record Test B baseline |
| `36426d8` | 09-29 16:02:53 | Record Test C baseline |

The commits and the revert are PROVEN. That `50751ff` held agent-prefilled rather than human classifications is UNPROVEN in git. The revert and the "(human evaluator)" re-record are consistent with it (INFERRED).

Summary counts, parsed mechanically from the worksheet at `36426d8` (PROVEN). Classifications aren't reproduced here.

| Test | Request (short) | Timer (worksheet) | ASSET statuses (15) | CODE file_status (8) | Relationships | Unresolved items |
|---|---|---|---|---|---|---|
| A | hairstyle → shoulder-length dark hair | 00:45:42 → 01:47:00, 01:01:18 | 14 ASSET_ACTION, 1 UNAFFECTED | 8 DOWNSTREAM_USAGE | 30 (29 DOWNSTREAM_USAGE, 1 UNAFFECTED) | 0 |
| B | materially different outfit | 02:05:00 → 02:30:00, 00:25:00 | 11 ASSET_ACTION, 3 UNAFFECTED, 1 REVIEW_REQUIRED | 8 DOWNSTREAM_USAGE | 30 (29 DOWNSTREAM_USAGE, 1 UNAFFECTED) | 1 |
| C | small ear accessory | 15:32:00 → 15:59:00, 00:27:00 | 14 ASSET_ACTION, 1 UNAFFECTED | 8 DOWNSTREAM_USAGE | 30 (29 DOWNSTREAM_USAGE, 1 UNAFFECTED) | 1 |

## 3. Impact engine (2026-09-29 to 2026-09-30)

All SHAs below exist, and each one's parent is the previous row. PROVEN.

| Branch | Commit | Parent | Time | Subject |
|---|---|---|---|---|
| `matcha-2-impact-engine-v1` | `5f56351` | `36426d8` | 09-29 18:07:04 | feat: add impact analysis prototype for review (`matcha/impact/*`, `scripts/impact_eval.py`, tests) |
| `matcha-2-impact-engine-v1-hardening` | `edd7ec9` | `5f56351` | 09-29 21:53:21 | refactor: harden impact analysis evaluation contracts |
| ″ | `51b14c2` | `edd7ec9` | 09-29 22:36:23 | refactor: finalize impact analysis evaluation contracts |
| ″ | `ea172cf` | `51b14c2` | 09-29 23:29:29 | fix: make strict evidence identity authoritative in validate-inventory |
| ″ | `f47ea61` | `ea172cf` | 09-30 00:00:32 | feat: add run provenance to impact reports (adds `EXPERIMENT-01-PROVENANCE.md`, `matcha/impact/provenance.py`) |
| ″ | `e47283b` | `f47ea61` | 09-30 02:49:48 | fix: record worktree cleanliness and clarify prompt provenance (`git_worktree_dirty`) |

- At `ea172cf`, `validate-inventory` exits FAIL (exit 2) at 126/127 strict. **UNPROVEN** here: the commit message doesn't say it and it wasn't re-run for this log.
- 269 tests passed at `e47283b`. **UNPROVEN** here: not re-run. A static count of `def test_` at `e47283b` gives 199 across 20 `tests/test_*.py` files, and that count doesn't expand parametrized tests.
- The relationship-evidence total 127 matches `counts.relationship_evidence_items = 127` in each condition M report (PROVEN, section 6).

## 4. Experiment 2 setup (2026-09-30 to 2026-10-01)

Branch `matcha-2-experiment-02`, branched from `e47283b`. PROVEN.

| Commit | Time | Author | Subject / content |
|---|---|---|---|
| `7557d06` | 09-30 16:00:02 | Jeffrey Tse | docs: `EXPERIMENT-02-DESIGN.md`, `EXPERIMENT-02-HUMAN-BASELINE.md`, `EXPERIMENT-02-ASSISTED-REVIEW.md` |
| `4c65837` | 09-30 16:09:29 | Jeffrey Tse | docs: methodology corrections to the three docs |
| `400a9dc` | 09-30 17:58:44 | Jeffrey Tse | tools: `tools/experiment-02-human-audit/` (human-only audit recorder) |
| `a85bed1` | 10-01 00:04:52 | Jeffrey Tse | tools: fixture evidence browser, locked A→B→C case order, exclusive Investigation/Documentation timers |
| `4f81f05` | 10-01 15:10:02 (07:10:02 UTC) | **Cursor Agent** (co-author hydrogenbondss) | tools: withhold `metadata/fixture-manifest.json` and `metadata/KITE_ASSET_MASTERLIST.md` from the H evidence browser. Both stay in the frozen fixture. |
| `d6092e9` | 10-01 15:23:01 | Jeffrey Tse | tools: neutral evidence-browser exclusion wording |

### H audit server (2026-10-01)

- Output folder `~/Desktop/matcha-engine-experiment-02-human-output/` holds `H-run.json` (`created_at` 2026-10-01 15:46:37) and `H-A.state.json` (updated 15:48:07). PROVEN.
- `H-A.state.json` has one 34-second investigation segment (15:47:33 to 15:48:07), and all 15 ASSET statuses and reasons are empty. **No H classifications were recorded.** PROVEN by a mechanical field check. The folder isn't committed.
- The server has since stopped. In the session this was put down to a Mac restart on Oct 3. **UNPROVEN**: `last reboot` on the Mac shows shutdowns/reboots on 10-01 17:12/17:24 and 10-04 17:39/17:40, and none on 10-03. So the server most likely stopped at or before the 10-01 17:12 shutdown, unless it was restarted later (INFERRED).
- **There is no clean human-only (H) baseline for Experiment 2.**

## 5. AI-assisted exploratory baseline (2026-10-01): NOT condition H

- Committed as `ebb2384` (10-03 16:17:41) under `experiment-outputs/experiment-02-ai-baseline/`, 15 files. PROVEN. File names: `AI-BASELINE-README.md`, `H-A|H-B|H-C.{state.json,yaml,finalized.json}`, `H-run.json`, and `attempt1-A-rejected/{H-A.state.json,H-A.yaml,H-A.finalized.json,H-run.json}`. The `H-*` names are the tool's built-in labels. The commit message records archive sha256 `6a2ef9bd507da20878587fb2dcc4110520b77f9080885ac8d3332171057f4f13`. PROVEN.
- The agent did the semantic work in the audit tool's browser UI, on a byte-identical copy of the tool at `d6092e9`. The commit message says these are "Verbatim finalized exports from tools/experiment-02-human-audit @ d6092e9, produced by an AI agent". PROVEN for that statement. The byte-identical-copy detail is UNPROVEN here.
- The agent was **not blind**: it had seen the Experiment 1 summary counts beforehand. UNPROVEN (from the session).
- The first Test A attempt was rejected for blank reasons and redone. It's kept in `attempt1-A-rejected/` (PROVEN, file names). The reason for rejection is UNPROVEN (from the session).
- Counts and known gaps below come from the session. **UNPROVEN** here, because the AI-baseline files were deliberately not opened for this log.
  - A: 14 ASSET_ACTION / 1 UNAFFECTED, 30 relationships.
  - B: 11 ASSET_ACTION / 4 UNAFFECTED, 24 relationships, 1 unresolved.
  - C: 14 ASSET_ACTION / 1 UNAFFECTED, 30 relationships, 1 unresolved.
  - Known B gaps: it missed 6 `li_sprite_normalization` relationships (lines 101–106). The tattoo relationship is DOWNSTREAM_USAGE while the tattoo asset is UNAFFECTED. The henley comment conflict at `route_kite.rpy:1471` wasn't logged as unresolved.
- These outputs are archival only. They weren't used as answers or as input to Matcha.

## 6. Condition M, Matcha alone, provider unavailable (2026-10-03)

Outputs: `experiment-outputs/experiment-02-M-provider-unavailable/`, copied verbatim from `~/Desktop/matcha-engine-experiment-02-M-output/`, sha256 verified.

- **Checkout** (PROVEN, `preflight.txt`): clean detached worktree `/Users/jeffreytse/Projects/matcha-engine-e2-M-d6092e9`, `HEAD=d6092e993672408a8235e9e9ac9a94f25e004ccb`, `porcelain=[]`, fixture tree `9f8fbe99…`, Python 3.12.4. The `matcha` module resolves from the worktree. Ollama binary is present, the only local manifest is `qwen2.5/1.5b`, and the Ollama server wasn't reachable. Preflight time 2026-10-03 16:32:32.
- **Entrypoint** (PROVEN, `command.txt`): `PYTHONDONTWRITEBYTECODE=1 python3 -m matcha.cli impact --fixture <worktree>/fixtures/kite-production --request "<frozen request>" --reference reference/kite_male_neutral.png --provider auto --output <dir>/report.json --summary <dir>/summary.md`, run from the worktree.
- Why not the installed `matcha` command: it points at the dirty main checkout. Why not `scripts/impact_eval.py`: it loads the Experiment 1 inventory. UNPROVEN here (from the session).
- **Provider** (PROVEN, `report.json` for each case): `provider.name = "unavailable"`, `model = null`, `state = "UNAVAILABLE"`, `requested = "auto"`. `missing`, verbatim:
  - "no cloud vision API key present in the environment"
  - "ollama server not reachable at http://127.0.0.1:11434"
  - "llama.cpp binaries present but no llama.cpp adapter/multimodal model is configured"

Per-case values from `report.json` and `runtime.txt` (PROVEN):

| Case | Request | Wall clock (`runtime.txt`) | Engine `timing.elapsed` | Exit | Assets | Code units | Relationships | Unresolved |
|---|---|---|---|---|---|---|---|---|
| A | Kite's canonical hairstyle changes from the current documented hairstyle to shoulder-length dark hair. | 16:32:45 → 16:32:52, 6.035 s | 1.286 s | 0 | 15 REVIEW_REQUIRED | 8 REVIEW_REQUIRED | 30 REVIEW_REQUIRED | 23 |
| B | Kite's canonical outfit changes to a materially different outfit. | 16:33:04 → 16:33:11, 6.116 s | 1.091 s | 0 | 15 REVIEW_REQUIRED | 8 REVIEW_REQUIRED | 30 REVIEW_REQUIRED | 23 |
| C | Kite's canonical small ear accessory changes. | 16:33:24 → 16:33:29, 4.342 s | 0.860 s | 0 | 15 REVIEW_REQUIRED | 8 REVIEW_REQUIRED | 30 REVIEW_REQUIRED | 23 |

Values common to A, B and C (PROVEN):

- `asset_review_cause`: 15 × PROVIDER_UNAVAILABLE.
- `provider_execution.assets_with_valid_provider_output`: 0.
- `analysis_completeness`: INCOMPLETE. 30 static relationships, 19 unresolved dependencies (`dynamic_reference`).
- `unresolved_by_kind`: provider_unavailable 1, dynamic_reference 19, no_static_relationship 3. The three are `assets/kite_male_dark.png`, `kite_male_dark_relaxed.png` and `kite_male_dark_withdrawn.png`.
- `relationship_evidence_items`: 127.
- `provenance.engine.git_commit`: `d6092e993672408a8235e9e9ac9a94f25e004ccb`, and `git_worktree_dirty: false`.
- `provenance.fixture.manifest_sha256`: `6453f313d5767c498ffc29fd3e7a7e85b816d743a5485a5f71cad3370c93e1b1`, and `asset_hashes_verified: true`.
- `provenance.reference`: `reference/kite_male_neutral.png`, sha256 `b3469eeed8510f5ae0807cafc8564b21b9be617a3a27027f7eca6d230c0da07d`.
- `provenance.vision_prompt`: template_sha256 `8440896196edeca3af996aefa7056da98262f5d2d8e5115c909b5390b9016c4a`, vision_module_sha256 `3a43cbfeb46dd318eace6382b6401269909d4493b197754ed357913795572723`, rendered_prompt_sha256 `null` (no prompt rendered).

**Mechanical validation**: all of the following passed.

- Reports and provenance exist for all three cases.
- The engine commit and dirty flag are as listed above.
- Fixture and reference hashes are present.
- The provider is recorded.
- A grep of the output folder finds no reference to the AI-baseline files or the Experiment 1 worksheet. This grep was re-run for this log and still matches nothing.

PROVEN.

## 7. Ollama vision-model setup attempts (2026-10-03 to 2026-10-04)

Outputs: `experiment-outputs/experiment-02-M-smoke-incomplete/`, copied verbatim from `~/Desktop/matcha-engine-experiment-02-M-smoke/`, sha256 verified.

- **Machine** (PROVEN, read 2026-10-05): `uname -m` = x86_64 (Intel), `hw.memsize` = 17179869184 bytes (16 GiB), `ollama --version` client 0.20.4. `ollama-serve.log` says "Listening on 127.0.0.1:11434 (version 0.20.4)".
- **Model chosen**: `qwen3-vl:8b`, an official Ollama Qwen3-VL model. Ollama 0.20.4 meets the ≥ 0.12.7 requirement. The pull log shows manifest `registry.ollama.ai/v2/library/qwen3-vl/manifests/8b` and a main layer `ed12a4674d72…` of 6.1 GB. PROVEN.
- **Pull attempts** (PROVEN, from the logs):

| Log | Window | Outcome | Furthest CLI progress |
|---|---|---|---|
| `pull.log` | 10-03 17:52 | `Error: could not connect to ollama server` (the server wasn't up yet), `pull_exit=1` | n/a |
| `pull.attempt1.raw.log` | 10-03 ~17:55 → 18:12 | `Error: max retries exceeded: Get "https://…r2.cloudflarestorage.com/…": net/http: TLS handshake timeout`, `pull_exit=1` | 865 MB / 6.1 GB (14%) |
| `pull.attempt2.raw.log` | tries 2–6: 10-03 18:24, 22:27, 22:59, 23:15, 23:16 (exit file 10-04 00:16) | 4 × `pull model manifest: … dial tcp: lookup registry.ollama.ai: i/o timeout`, 1 × blob host `no such host`. Every try rc=1, `pull_exit=1` | 618 MB (10%) |
| `pull.attempt3.raw.log` | 10-04 15:32 → 17:40 | try 1 (15:32–17:16) rc=1 blob `TLS handshake timeout`. Tries 2–3 rc=1 manifest `TLS handshake timeout`. Try 4 started 17:19:49 with **no end record** | 855 MB (14%) |

- `ollama-serve.log` ends with `POST /api/pull` at 10-04 17:40:01 (20m11s) and contains **no `/api/chat` requests**. PROVEN.
- **Mac disconnects**: `last reboot` shows a shutdown at 10-04 17:39 and a reboot at 17:40, which matches the end of attempt 3 try 4 (PROVEN). The earlier disconnect on the evening of 10-03 is UNPROVEN, since no matching reboot is recorded.
- The logs contain Ollama-registry presigned blob URLs (`X-Amz-*`, `X-Amz-Expires=86400`, issued 10-03/10-04). These are registry-issued, time-limited download URLs that have now expired. They aren't user credentials.
- **Current state (read 2026-10-05 ~11:54 HKT)**, all PROVEN:
  - No Ollama server is running, so `ollama list` returns "could not connect to ollama server".
  - On-disk manifests under `~/.ollama/models/manifests/registry.ollama.ai/library/` contain only `qwen2.5/1.5b`. **`qwen3-vl:8b` is not installed.**
  - A partial blob `sha256-ed12a4674d72…-partial` exists: 6.1 GB allocated, 1.6 GB actually on disk.
  - No pull is running.
- The source smoke folder contains an empty `A/` directory. Git can't track empty directories, so it isn't in the commit.
- **The Test A smoke test has not run.** No Matcha run was made with `ollama:<model>`.

## 8. Pending

1. Get a local Ollama vision model installed (`qwen3-vl:8b`, or fall back to `qwen3-vl:4b`) and confirm Matcha discovery lists it in `vision_models`.
2. Run the Test A smoke test only, from the clean `d6092e9` worktree with `--provider ollama:<model>`, and check it mechanically.
3. Run the full condition M sequence A → B → C into a fresh folder outside the repository.
4. Run H+M afterwards. **There is no clean H baseline** (section 4). The AI-assisted exploratory baseline (section 5) is not H.

## 9. Paths

| What | Location |
|---|---|
| Repo worktree for this branch | `/Users/jeffreytse/Projects/matcha-engine-experiment-02` (`matcha-2-experiment-02`) |
| Clean M worktree (detached `d6092e9`) | `/Users/jeffreytse/Projects/matcha-engine-e2-M-d6092e9` |
| Frozen fixture | `fixtures/kite-production/` (tree `9f8fbe99…`) |
| Experiment 1 worksheet | `docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md` on `matcha-2-experiment-01-baseline` (`36426d8`) |
| Experiment 2 docs | `docs/experiments/EXPERIMENT-02-*.md` |
| H audit tool | `tools/experiment-02-human-audit/` |
| H output (no data; not committed) | `~/Desktop/matcha-engine-experiment-02-human-output/` |
| AI-assisted exploratory baseline (archival, not H) | `experiment-outputs/experiment-02-ai-baseline/` (`ebb2384`) |
| Condition M, provider unavailable | `experiment-outputs/experiment-02-M-provider-unavailable/` (source `~/Desktop/matcha-engine-experiment-02-M-output/`) |
| Ollama setup / incomplete smoke | `experiment-outputs/experiment-02-M-smoke-incomplete/` (source `~/Desktop/matcha-engine-experiment-02-M-smoke/`) |
| Ollama models | `~/.ollama/models/` |
