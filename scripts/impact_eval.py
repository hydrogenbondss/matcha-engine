#!/usr/bin/env python3
"""Evaluation helpers for ``matcha impact`` (validation / comparison only).

This module is the ONLY place that reads the human baseline worksheet.
The executable engine (``matcha/impact``) never imports it.

Subcommands:

    validate-inventory  compare discovered CODE x ASSET pairs (and evidence)
                        with the worksheet's frozen structural inventory
    compare             compare an impact JSON report with one frozen test
                        section (A, B or C) of the worksheet

Both are read-only: they print results (and optionally write a JSON file
outside the fixture); they never edit the worksheet.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_WORKSHEET = REPO / "docs/experiments/EXPERIMENT-01-HUMAN-BASELINE.md"
DEFAULT_FIXTURE = REPO / "fixtures/kite-production"


# ---------------------------------------------------------------- worksheet ---

def _section(text: str, heading: str, level: int = 2) -> str:
    pat = re.compile(rf"^{'#' * level} {re.escape(heading)}.*$", re.M)
    m = pat.search(text)
    if not m:
        raise ValueError(f"heading not found: {heading}")
    nxt = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, m.end())
    return text[m.end() : nxt.start() if nxt else len(text)]


def _yaml_blocks(text: str) -> list[Any]:
    return [yaml.safe_load(b) for b in re.findall(r"```yaml\n(.*?)```", text, re.S)]


def load_inventory(worksheet: Path = DEFAULT_WORKSHEET) -> dict[tuple[str, str], list[dict]]:
    text = Path(worksheet).read_text(encoding="utf-8")
    inv = _section(text, "Structural relationship inventory")
    parts = re.split(r"^### (\S+)\s*$", inv, flags=re.M)
    out: dict[tuple[str, str], list[dict]] = {}
    for i in range(1, len(parts), 2):
        src = parts[i]
        for block in _yaml_blocks(parts[i + 1]):
            for entry in block or []:
                key = (src, entry["related_asset"])
                if key in out:
                    raise ValueError(f"duplicate inventory pair {key}")
                out[key] = entry["evidence"]
    return out


def load_test(worksheet: Path, test: str) -> dict[str, Any]:
    text = Path(worksheet).read_text(encoding="utf-8")
    m = re.search(rf"^## Test {test}:.*$", text, re.M)
    if not m:
        raise ValueError(f"Test {test} not found")
    nxt = re.compile(r"^## ", re.M).search(text, m.end())
    sec = text[m.end() : nxt.start() if nxt else len(text)]
    timing = next(b for b in _yaml_blocks(sec.split(f"### Test {test}: ASSET records")[0]) if isinstance(b, dict))
    assets = _yaml_blocks(_section(sec, f"Test {test}: ASSET records", 3))[0]
    code = _yaml_blocks(_section(sec, f"Test {test}: CODE records", 3))[0]
    unresolved = _yaml_blocks(_section(sec, f"Test {test}: unresolved items", 3))[0]
    return {"timing": timing, "assets": assets, "code": code, "unresolved": unresolved}


# ------------------------------------------------------------- validation ----

def _identity(e: dict) -> tuple:
    return (e["source_path"], e["anchor_type"], e["anchor"])


def compare_inventory(discovered: dict[tuple[str, str], list[dict]], inventory: dict[tuple[str, str], list[dict]]) -> dict:
    d_pairs, i_pairs = set(discovered), set(inventory)
    result: dict[str, Any] = {
        "inventory_pairs": len(i_pairs),
        "discovered_pairs": len(d_pairs),
        "exact_pairs": len(d_pairs & i_pairs),
        "extra_pairs": sorted(d_pairs - i_pairs),
        "missing_pairs": sorted(i_pairs - d_pairs),
    }
    ev = Counter()
    mismatches = []
    for pair in sorted(d_pairs & i_pairs):
        inv_items, dis_items = inventory[pair], discovered[pair]
        ev["inventory_items"] += len(inv_items)
        ev["discovered_items"] += len(dis_items)
        inv_id = Counter(_identity(e) for e in inv_items)
        dis_id = Counter(_identity(e) for e in dis_items)
        ev["identity_matched"] += sum((inv_id & dis_id).values())
        # occurrence level: identity + source location (validation-only matching aid)
        inv_occ = {(_identity(e), e.get("locator")): e for e in inv_items}
        dis_occ = {(_identity(e), e.get("locator")): e for e in dis_items}
        both = set(inv_occ) & set(dis_occ)
        ev["occurrence_matched"] += len(both)
        ev["context_equal"] += sum(inv_occ[k].get("context") == dis_occ[k].get("context") for k in both)
        ev["fingerprint_equal"] += sum(inv_occ[k].get("fingerprint") == dis_occ[k].get("fingerprint") for k in both)
        ev["fact_equal"] += sum(inv_occ[k].get("fact") == dis_occ[k].get("fact") for k in both)
        by_loc_inv = {(e["source_path"], e.get("locator")): e for e in inv_items}
        for e in dis_items:
            k = (_identity(e), e.get("locator"))
            if k in inv_occ:
                continue
            other = by_loc_inv.get((e["source_path"], e.get("locator")))
            mismatches.append(
                {
                    "pair": list(pair),
                    "locator": e.get("locator"),
                    "discovered": {"anchor_type": e["anchor_type"], "anchor": e["anchor"]},
                    "inventory": (
                        {"anchor_type": other["anchor_type"], "anchor": other["anchor"]} if other else None
                    ),
                }
            )
        for e in inv_items:
            k = (_identity(e), e.get("locator"))
            if k not in dis_occ and (e["source_path"], e.get("locator")) not in {
                (x["source_path"], x.get("locator")) for x in dis_items
            }:
                mismatches.append({"pair": list(pair), "locator": e.get("locator"), "discovered": None,
                                   "inventory": {"anchor_type": e["anchor_type"], "anchor": e["anchor"]}})
    result["evidence"] = dict(ev)
    result["evidence_mismatches"] = mismatches
    result["pairs_ok"] = not result["extra_pairs"] and not result["missing_pairs"] and result["exact_pairs"] == len(i_pairs)
    return result


def discovered_from_fixture(fixture: Path) -> dict[tuple[str, str], list[dict]]:
    sys.path.insert(0, str(REPO))
    from matcha.impact.fixture import load_fixture
    from matcha.impact.graph import build_graph

    g = build_graph(load_fixture(fixture))
    return {k: [e.to_dict() for e in r.evidence] for k, r in g.relationships.items()}


def discovered_from_report(report: dict) -> dict[tuple[str, str], list[dict]]:
    return {
        (c["source_path"], r["related_asset"]): r["evidence"] for c in report["code"] for r in c["relationships"]
    }


# ------------------------------------------------------------- comparison ----

def _ratio(n: int, d: int) -> Optional[float]:
    return round(n / d, 4) if d else None


def compare_report(report: dict, baseline: dict) -> dict:
    base_assets = {a["asset_path"]: a["status"] for a in baseline["assets"]}
    auto_assets = {a["asset_path"]: a["status"] for a in report["assets"]}
    if set(base_assets) != set(auto_assets):
        raise ValueError(f"ASSET sets differ: {sorted(set(base_assets) ^ set(auto_assets))}")
    tp = fp = fn = tn = 0
    matrix = Counter()
    rows = []
    for p in sorted(base_assets):
        b, a = base_assets[p], auto_assets[p]
        matrix[(b, a)] += 1
        bp, ap = b == "ASSET_ACTION", a == "ASSET_ACTION"
        tp += bp and ap
        fp += (not bp) and ap
        fn += bp and not ap
        tn += (not bp) and not ap
        rows.append({"asset_path": p, "baseline": b, "automated": a, "agree": a == b})
    determinate = [p for p, s in base_assets.items() if s != "REVIEW_REQUIRED"]
    d_tp = sum(base_assets[p] == "ASSET_ACTION" and auto_assets[p] == "ASSET_ACTION" for p in determinate)
    d_fp = sum(base_assets[p] == "UNAFFECTED" and auto_assets[p] == "ASSET_ACTION" for p in determinate)
    d_fn = sum(base_assets[p] == "ASSET_ACTION" and auto_assets[p] != "ASSET_ACTION" for p in determinate)
    assets = {
        "n": len(base_assets),
        "exact_status_agreement": sum(r["agree"] for r in rows),
        "binary_asset_action_vs_not": {
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "precision": _ratio(tp, tp + fp), "recall": _ratio(tp, tp + fn),
        },
        "protocol_17_1": {
            "ground_truth_determinate": len(determinate),
            "ground_truth_review_required": len(base_assets) - len(determinate),
            "automated_review_required": sum(s == "REVIEW_REQUIRED" for s in auto_assets.values()),
            "TP": d_tp, "FP": d_fp, "FN": d_fn,
            "precision": _ratio(d_tp, d_tp + d_fp), "recall": _ratio(d_tp, d_tp + d_fn),
            "automated_review_rate": _ratio(sum(s == "REVIEW_REQUIRED" for s in auto_assets.values()), len(auto_assets)),
            "coverage": _ratio(sum(s != "REVIEW_REQUIRED" for s in auto_assets.values()), len(auto_assets)),
        },
        "confusion_baseline_to_automated": {f"{b} -> {a}": n for (b, a), n in sorted(matrix.items())},
        "rows": rows,
    }

    base_files = {c["source_path"]: c for c in baseline["code"]}
    auto_files = {c["source_path"]: c for c in report["code"]}
    fm = Counter((base_files[p]["file_status"], auto_files[p]["file_status"]) for p in base_files if p in auto_files)
    code = {
        "baseline_units": len(base_files),
        "automated_units": len(auto_files),
        "same_unit_set": set(base_files) == set(auto_files),
        "exact_file_status_agreement": sum(n for (b, a), n in fm.items() if a == b),
        "confusion_baseline_to_automated": {f"{b} -> {a}": n for (b, a), n in sorted(fm.items())},
    }

    def rels(files):
        return {(p, r["related_asset"]): r["relationship_status"] for p, c in files.items() for r in (c.get("relationships") or [])}

    br, ar = rels(base_files), rels(auto_files)
    rm = Counter((br[k], ar[k]) for k in br if k in ar)
    relationships = {
        "baseline": len(br),
        "automated": len(ar),
        "same_pair_set": set(br) == set(ar),
        "missing_in_automated": sorted(set(br) - set(ar)),
        "extra_in_automated": sorted(set(ar) - set(br)),
        "exact_status_agreement": sum(n for (b, a), n in rm.items() if a == b),
        "downstream_traceability_pairs_found": len(set(br) & set(ar)),
        "confusion_baseline_to_automated": {f"{b} -> {a}": n for (b, a), n in sorted(rm.items())},
        "code_action": {
            "baseline": sum(v == "CODE_ACTION" for v in br.values()),
            "automated": sum(v == "CODE_ACTION" for v in ar.values()),
        },
    }
    return {
        "provider": {k: report["provider"].get(k) for k in ("name", "model", "available")},
        "baseline_timing": baseline["timing"],
        "automated_timing": report["timing"],
        "assets": assets,
        "code": code,
        "relationships": relationships,
    }


def oracle_propagation(baseline: dict, fixture: Path = DEFAULT_FIXTURE, identifier_policy: str = "preserved") -> dict:
    """Feed the BASELINE asset statuses through the engine's propagation rules
    and compare the resulting CODE statuses with the baseline CODE statuses.

    Isolates the status rules from the vision step ("if every asset verdict
    were right, would CODE and relationships agree?"). Evaluation only.
    """
    sys.path.insert(0, str(REPO))
    from matcha.impact.fixture import load_fixture
    from matcha.impact.graph import build_graph
    from matcha.impact.propagate import file_status, relationship_status

    g = build_graph(load_fixture(fixture))
    asset = {a["asset_path"]: a["status"] for a in baseline["assets"]}
    derived_rel = {k: relationship_status(asset[k[1]], identifier_policy) for k in g.relationships}
    derived_file = {
        u.fixture_path: file_status([v for (s, _), v in derived_rel.items() if s == u.fixture_path])
        for u in g.eligible_code
    }
    base_rel = {(c["source_path"], r["related_asset"]): r["relationship_status"]
                for c in baseline["code"] for r in c["relationships"]}
    base_file = {c["source_path"]: c["file_status"] for c in baseline["code"]}
    rel_diff = sorted([list(k), base_rel.get(k), derived_rel.get(k)]
                      for k in set(base_rel) | set(derived_rel) if base_rel.get(k) != derived_rel.get(k))
    file_diff = sorted([k, base_file.get(k), derived_file.get(k)]
                       for k in set(base_file) | set(derived_file) if base_file.get(k) != derived_file.get(k))
    return {
        "identifier_policy": identifier_policy,
        "relationships_agree": len(base_rel) - len([d for d in rel_diff if d[1] is not None]),
        "relationships_total": len(base_rel),
        "relationship_diffs": rel_diff,
        "files_agree": len(base_file) - len([d for d in file_diff if d[1] is not None]),
        "files_total": len(base_file),
        "file_diffs": file_diff,
    }


# -------------------------------------------------------------------- CLI ----

def _pairs_text(r: dict) -> str:
    lines = [
        f"pairs: inventory {r['inventory_pairs']}, discovered {r['discovered_pairs']}, "
        f"exact {r['exact_pairs']}/{r['inventory_pairs']}, extra {len(r['extra_pairs'])}, missing {len(r['missing_pairs'])}"
    ]
    lines += [f"  EXTRA   {p}" for p in r["extra_pairs"]] + [f"  MISSING {p}" for p in r["missing_pairs"]]
    e = r["evidence"]
    lines.append(
        "evidence: inventory {inventory_items}, discovered {discovered_items}, identity-matched {identity_matched}, "
        "occurrence-matched (identity+locator) {occurrence_matched}; of matched occurrences: context equal "
        "{context_equal}, fingerprint equal {fingerprint_equal}, fact equal {fact_equal}".format(
            **{k: e.get(k, 0) for k in ("inventory_items", "discovered_items", "identity_matched",
                                        "occurrence_matched", "context_equal", "fingerprint_equal", "fact_equal")}
        )
    )
    for m in r["evidence_mismatches"]:
        lines.append(f"  EVIDENCE DIFF {m['pair']} @ {m['locator']}: discovered={m['discovered']} inventory={m['inventory']}")
    lines.append("RESULT: " + ("PASS (pairs exact)" if r["pairs_ok"] else "FAIL (pair mismatch)"))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate-inventory")
    v.add_argument("--worksheet", type=Path, default=DEFAULT_WORKSHEET)
    v.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    v.add_argument("--report", type=Path, help="validate relationships from an impact JSON report instead of re-scanning")
    v.add_argument("--json-out", type=Path)
    c = sub.add_parser("compare")
    c.add_argument("--worksheet", type=Path, default=DEFAULT_WORKSHEET)
    c.add_argument("--report", type=Path, required=True)
    c.add_argument("--test", required=True, choices=["A", "B", "C"])
    c.add_argument("--json-out", type=Path)
    o = sub.add_parser("oracle-propagation")
    o.add_argument("--worksheet", type=Path, default=DEFAULT_WORKSHEET)
    o.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    o.add_argument("--test", required=True, choices=["A", "B", "C"])
    a = ap.parse_args(argv)

    if a.cmd == "oracle-propagation":
        print(json.dumps(oracle_propagation(load_test(a.worksheet, a.test), a.fixture), indent=2))
        return 0

    if a.cmd == "validate-inventory":
        inv = load_inventory(a.worksheet)
        disc = discovered_from_report(json.loads(a.report.read_text())) if a.report else discovered_from_fixture(a.fixture)
        r = compare_inventory(disc, inv)
        print(_pairs_text(r))
        if a.json_out:
            a.json_out.write_text(json.dumps(r, indent=2, default=list) + "\n")
        return 0 if r["pairs_ok"] else 1

    report = json.loads(a.report.read_text())
    res = compare_report(report, load_test(a.worksheet, a.test))
    print(json.dumps({k: v for k, v in res.items() if k != "assets"} | {"assets": {k: v for k, v in res["assets"].items() if k != "rows"}}, indent=2, default=str))
    print("\nper-asset:")
    for row in res["assets"]["rows"]:
        print(f"  {'=' if row['agree'] else 'x'} {row['asset_path']}: baseline {row['baseline']} / automated {row['automated']}")
    if a.json_out:
        a.json_out.write_text(json.dumps(res, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
