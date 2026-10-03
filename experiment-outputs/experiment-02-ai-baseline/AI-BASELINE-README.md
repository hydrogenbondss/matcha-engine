# Experiment 2: AI-assisted exploratory baseline (NOT the H condition)

The files in this folder were produced on 2026-10-01 (HKT) by an AI agent, Matcha. It ran the tool `tools/experiment-02-human-audit` at commit `d6092e993672408a8235e9e9ac9a94f25e004ccb` (fixture tree `9f8fbe99`) in a browser, and the agent itself did all the semantic investigation.

- The tool writes files named `H-*` and the header "condition H, human-recorded" because those labels are built into the tool. The files are NOT human-only H data, and they do not measure unaided human work.
- The investigation was not blind. Before the run, the agent had seen the Experiment 1 summary counts. The Experiment 1 inventory and classifications were not opened during the run.
- The tool ran on a byte-identical clone of `d6092e9` on the agent's computer, because the agent's browser cannot reach the Mac's localhost.
- `attempt1-A-rejected/` holds the first Test A attempt. It was discarded because most of its relationship reason fields were blank and its image evidence was boilerplate. Test A was then redone from a fresh run (new `run_id`).
