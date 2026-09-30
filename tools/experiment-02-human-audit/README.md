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
  same repository). It is created if missing.

## What it reads

- `docs/experiments/EXPERIMENT-02-HUMAN-BASELINE.md` (read-only): the exact Test
  A/B/C request and question lines (verbatim from protocol §9), the 15 scored ASSET
  paths, the 8 scored CODE paths, the record ids (`H-<case>-ASSET-NN`,
  `H-<case>-CODE-NN`), and its "Allowed values" lines (checked at start-up).
- `fixtures/kite-production/`: only the 15 scored ASSET images and the 8 scored
  CODE source files, served read-only and byte-for-byte through an exact-match
  whitelist (`/fixture/<fixture-relative-path>`). Anything else returns 404.
- `git rev-parse HEAD`, `git status --porcelain`, `git rev-parse
  HEAD:fixtures/kite-production`: export provenance only.

## Ordering

ASSET and CODE units are shown in the fixed order in which the frozen protocol
(§4.1, §4.3) and the Experiment 2 H worksheet list them. No other ordering is used.

## Allowed options

The selects start blank and offer exactly the values defined in
`docs/experiments/EVIDENCE-PROTOCOL-01.md`:

- ASSET `status` (Decision 5): `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.
- CODE `file_status` and `relationship_status` (§5): `CODE_ACTION`,
  `DOWNSTREAM_USAGE`, `REVIEW_REQUIRED`, `UNAFFECTED`.
- Evidence `anchor_type` (§5.1): `declaration`, `statement`, `function`, `label`,
  `assignment`, `config`, `excerpt_header`, `asset`, `metadata`.
- Relationship `related_asset`: the 15 scored ASSET paths, same fixed order.

## Use

- One test at a time, A → B → C. Only the case you navigate to is shown.
- **Investigation** timer and a separate **Documentation** timer. Each Start/Stop
  pair is one segment (ISO 8601 timestamps with UTC offset, from the browser's
  clock). Documentation time is never added to investigation time. The two timers
  are independent.
- Every change is saved to the browser (`localStorage`) at once and to
  `<output-dir>/H-<case>.state.json` shortly after. On reload, the newer copy wins.
- **Export H-<case>.yaml** writes `<output-dir>/H-<case>.yaml`. Stop the timers
  first; an open segment is exported without an end time and is not counted.

## Export format

Field names follow the H worksheet records. Blank fields are empty; empty lists are `[]`.

- `provenance`: `tool_name`, `tool_version`, `tool_source_commit` (`git rev-parse
  HEAD`, empty if unavailable), `tool_source_dirty` (`git status --porcelain`
  including untracked; empty if unavailable), `export_timestamp`,
  `fixture_tree_at_head` (`git rev-parse HEAD:fixtures/kite-production`).
- `test_case`, `start_time` (first investigation segment start), `end_time` (last
  investigation segment end), `elapsed_time` (sum of closed investigation segments,
  `HH:MM:SS`), `investigation_segments`, `documentation_segments`,
  `documentation_elapsed_time`.
- `asset_records`: 15 records (`id`, `test_case`, `item_type`, `asset_path`,
  `status`, `reason`, `evidence`, `game_usage`).
- `code_records`: 8 records (`id`, `test_case`, `item_type`, `source_path`,
  `file_status`, `reason`, `evidence`, `relationships` of `related_asset`,
  `relationship_status`, `reason`, `evidence`).
- Evidence items: `source_path`, `anchor_type`, `anchor`, `context`, `locator`,
  `fingerprint`, `fact`.
- `unresolved_items` (list of `item`), `work_notes` (list with the notes text, or `[]`).

The tool never modifies the frozen worksheet and never commits anything.
