# Experiment 2, condition H: human recording tool

A temporary, local, human-only recording tool for condition **H (human alone)** of
`docs/experiments/EXPERIMENT-02-DESIGN.md`. It is a repository inspector with an
evidence ledger beside it. It records what the human enters and nothing else.

It does **not** classify, suggest statuses, suggest or infer relationships, sort or
highlight by relevance, pre-fill reasons/evidence/game_usage, or call any model or
external service. It does not import `matcha/` code. It does not read the
Experiment 1 worksheet, its structural relationship inventory, or any Experiment 1
result.

## Start

```sh
python3 tools/experiment-02-human-audit/serve.py --output-dir <local-experiment-02-human-output>
```

- Python 3 standard library only; plain HTML/JS/CSS; no network resources.
- Binds to `127.0.0.1` only (default port 8765; `--port 0` picks a free port). Open
  the printed `http://127.0.0.1:<port>/` URL. Stop with Ctrl+C.
- `--output-dir` is required and must be **outside** this Git repository (the
  tool refuses the repository, `fixtures/`, `docs/`, and any other worktree of the
  same repository). It is created if missing. One output directory = one run.

## What it reads

- `docs/experiments/EXPERIMENT-02-HUMAN-BASELINE.md` (read-only): the exact Test
  A/B/C request and question lines (verbatim from protocol §9), the 15 scored ASSET
  paths, the 8 scored CODE paths, the record ids (`H-<case>-ASSET-NN`,
  `H-<case>-CODE-NN`), and its "Allowed values" lines (checked at start-up).
- `fixtures/kite-production/` only, read-only and byte-for-byte:
  - Record view: the 15 scored ASSET images and 8 scored CODE files
    (`/fixture/<fixture-relative-path>`, exact-match whitelist).
  - **Fixture evidence** view: the permitted static-production evidence
    (`/evidence/<fixture-relative-path>`), see below. Not every fixture file
    is listed.
- `git rev-parse HEAD`, `git status --porcelain`, `git rev-parse
  HEAD:fixtures/kite-production`: export provenance only. `git ls-tree -r
  HEAD:fixtures/kite-production`: the evidence whitelist.

Anything not in a whitelist returns 404. Lookups are by exact whitelist key; no
request path is ever joined onto a directory.

## Fixture evidence view

The **Fixture evidence** view exposes the permitted static-production evidence.
It lists, in plain path order with only the path and type (image / text), files
of `HEAD:fixtures/kite-production` (from `git ls-tree`) that are regular files,
are not symlinks, resolve inside the fixture root, whose on-disk bytes equal
the committed blob, and that are not named in the exclusion list below:

- image (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`; shown as images) or
  text (`.rpy`, `.txt`, `.md`, `.json`, `.yaml`, `.yml`; shown as raw text).

At the frozen fixture (`c1364f4`) the evidence browser exposes 29 files: the 15
scored ASSET images, `reference/KEEP_kite_male.png` and
`reference/kite_male_bust_neutral_credits_v19g.png` (evidence-only, protocol
Decision 1 and §8), `metadata/INSTALL_REPORT_MALEKITE_V19G.json`, and the 11
`game/` files: the 8 scored CODE units plus the evidence-only
`game/characters.rpy`, `game/options.rpy.excerpt.txt` and
`game/screens.rpy.excerpt.txt` (§4.3, §8).

Intentionally not exposed. These exclusions are experiment-interface protections
and do not modify the frozen fixture:

- `metadata/fixture-manifest.json` is intentionally not exposed because it
  contains precomputed relationship/game-usage information.
- `metadata/KITE_ASSET_MASTERLIST.md` is intentionally not exposed because it
  describes excluded video material.

Not listed: video and audio (excluded by protocol §19 and
`docs/experiments/KITE-FIXTURE-01.md` §4; none are in the fixture) and any other
file type; and anything outside `fixtures/kite-production/`, including
`docs/experiments/KITE-FIXTURE-01.md` (a repository document, not fixture material).
If git is unavailable, the whitelist is built by a filesystem walk with the same
symlink and realpath checks and the same two named exclusions.

## Ordering

ASSET and CODE units are shown in the fixed order in which the frozen protocol
(§4.1, §4.3) and the Experiment 2 H worksheet list them. The evidence view uses
plain path (alphabetical) order. No other ordering is used.

## Allowed options

The selects start blank and offer exactly the values defined in
`docs/experiments/EVIDENCE-PROTOCOL-01.md`:

- ASSET `status` (Decision 5): `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.
- CODE `file_status` and `relationship_status` (§5): `CODE_ACTION`,
  `DOWNSTREAM_USAGE`, `REVIEW_REQUIRED`, `UNAFFECTED`.
- Evidence `anchor_type` (§5.1): `declaration`, `statement`, `function`, `label`,
  `assignment`, `config`, `excerpt_header`, `asset`, `metadata`.
- Relationship `related_asset`: the 15 scored ASSET paths, same fixed order.

## Case order and finalize (A → B → C)

- Test A is always unlocked. Test B unlocks only when Test A is finalized; Test C
  only when Test B is finalized. The server enforces this: case data, state reads,
  saves and exports for a locked case are rejected (HTTP 423).
- **Export and finalize Test X** writes `<output-dir>/H-X.yaml` and
  `<output-dir>/H-X.finalized.json` (`case`, `finalized_at`, `export_file`,
  `export_sha256`, `tool_version`). A case is finalized when both files exist and
  the recorded `export_sha256` matches `H-X.yaml`. There are no semantic or
  correctness checks; any allowed values (including blanks) can be finalized.
- Finalize is refused while a timer is running (stop it first).
- A finalized case stays viewable but is **read-only**: the server rejects further
  saves and exports for it.
- On every start or reload the tool opens the earliest unlocked case that is not
  finalized (Test A if all three are finalized). There is no "last case" memory.
- The navigation shows each case as `open`, `finalized` or `locked`.

## Timers

- One **Investigation** timer and one separate **Documentation** timer. Each
  Start/Stop pair is one segment (ISO 8601 timestamps with UTC offset, from the
  browser's clock).
- They never overlap: while one is running, the other's Start button is disabled
  and marked "Start blocked"; neither timer is ever stopped automatically. The
  server rejects any save in which two segments overlap or more than one segment
  is open.
- `elapsed_time` = sum of closed Investigation segments;
  `documentation_elapsed_time` = sum of closed Documentation segments. They are
  never added together.

## Saving

Every change is saved to the browser (`localStorage`, keyed by the run id in
`<output-dir>/H-run.json`) at once and to `<output-dir>/H-<case>.state.json` shortly
after. On reload the newer copy wins; for a finalized case the server copy is used.

## Export format

Field names follow the H worksheet records. Blank fields are empty; empty lists are `[]`.

- `provenance`: `tool_name`, `tool_version`, `tool_source_commit` (`git rev-parse
  HEAD`, empty if unavailable), `tool_source_dirty` (`git status --porcelain`
  including untracked; empty if unavailable), `export_timestamp`,
  `fixture_tree_at_head` (`git rev-parse HEAD:fixtures/kite-production`).
- `test_case`, `start_time` (first investigation segment start), `end_time` (last
  investigation segment end), `elapsed_time`, `investigation_segments`,
  `documentation_segments`, `documentation_elapsed_time`.
- `asset_records`: 15 records (`id`, `test_case`, `item_type`, `asset_path`,
  `status`, `reason`, `evidence`, `game_usage`).
- `code_records`: 8 records (`id`, `test_case`, `item_type`, `source_path`,
  `file_status`, `reason`, `evidence`, `relationships` of `related_asset`,
  `relationship_status`, `reason`, `evidence`).
- Evidence items: `source_path`, `anchor_type`, `anchor`, `context`, `locator`,
  `fingerprint`, `fact`.
- `unresolved_items` (list of `item`), `work_notes` (list with the notes text, or `[]`).

The tool never modifies the frozen worksheet and never commits anything.
