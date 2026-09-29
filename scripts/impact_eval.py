#!/usr/bin/env python3
"""Evaluation helpers for ``matcha impact`` (validation / comparison only).

This module is the ONLY place that reads the human baseline worksheet.
The executable engine (``matcha/impact``) never imports it.

Subcommands:

    validate-inventory  compare discovered CODE x ASSET pairs and evidence with
                        the worksheet's frozen structural inventory; separate
                        layers for pairs, strict and normalized evidence
                        identity, evidence occurrence, and diagnostic field
                        agreement; overall PASS / PASS_WITH_NORMALIZATION /
                        FAIL (bit-mask exit code, see "validation" below)
    compare             score an impact JSON report against one frozen test
                        section (A, B or C) of the worksheet, per protocol
                        §17-18 (REVIEW_REQUIRED neither positive nor negative)
    oracle-propagation  feed baseline asset statuses through the engine rules

The evaluator owns the test labels (A/B/C); the engine report carries none.

All are read-only: they print results (and optionally write a JSON file
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
#
# validate-inventory reports five separate layers, each with its own result:
#
#   A pairs                         the exact CODE x ASSET pair set.  PASS/FAIL.
#   B evidence_identity             per pair, the multiset of strict evidence
#                                   identities (source_path, anchor_type, anchor),
#                                   protocol §5.1.  PASS/FAIL.
#   C evidence_identity_normalized  B after the documented ANCHOR_TYPE
#                                   NORMALIZATION below, applied to both sides.
#                                   PASS/FAIL (informational on its own).
#   D evidence_occurrence           per pair, every occurrence on one side aligns
#                                   with exactly one occurrence on the other, and
#                                   within each side no two occurrences share
#                                   identity + context + fingerprint (protocol:
#                                   repeated identities must be distinguished by
#                                   context and/or fingerprint).  Alignment uses
#                                   (source_path, locator) as a matching aid only,
#                                   preferring equal anchors; context/fingerprint
#                                   prose is used only to tell occurrences apart,
#                                   never required to equal the inventory's prose.
#                                   PASS/FAIL.
#   E field_agreement               anchor / anchor_type / context / fingerprint /
#                                   fact equality over aligned occurrences.
#                                   DIAGNOSTIC ONLY: result is "DIAGNOSTIC", with
#                                   all_fields_equal true/false; never fails.
#
# overall (machine-readable) is one of:
#   "PASS"                     A, B and D pass.
#   "PASS_WITH_NORMALIZATION"  A and D pass; B fails strictly, but every strict
#                              identity difference is explained by the accepted
#                              normalization (C passes).  The strict FAIL stays
#                              visible in B, and normalization_applied is true.
#   "FAIL"                     A fails, or B fails and C fails (a strict identity
#                              difference no accepted normalization explains),
#                              or D fails.  "failures" lists the failing layers.
# Exit code: bit mask of failures, so pair and evidence failures stay distinct:
#   1 = pairs, 2 = evidence identity not explained by an accepted normalization,
#   4 = evidence occurrence.  PASS and PASS_WITH_NORMALIZATION both exit 0.
#   Field-agreement differences never set a bit.

EXIT_BITS = {"pairs": 1, "evidence_identity": 2, "evidence_occurrence": 4}
ACCEPTED_NORMALIZATIONS = ("anchor_type_binding",)

# Python/Ren'Py binding syntax: `name = expr`, `$ name = expr`, `define|default name = expr`,
# `obj.attr = expr`, `x[k] = expr`, augmented `op=`, but not `==`; or a `"key": value` dict entry.
_BINDING_RE = re.compile(
    r"^(?:\$\s*)?(?:define\s+|default\s+)?[A-Za-z_][\w\.]*(?:\[[^\]]*\])?\s*[-+*/]?=(?!=)"
    r"|^(?:\"[^\"]*\"|'[^']*')\s*:"
)

ANCHOR_TYPE_NORMALIZATION = (
    "anchor_type 'statement' and 'assignment' are normalized to one class 'binding' when the anchor "
    "text is itself a Python/Ren'Py binding (name = expr, $ name = expr, define/default name = expr, "
    "attribute or subscript target, augmented assignment, or a \"key\": value dict entry). Every other "
    "anchor_type is compared unchanged. Reason: the frozen protocol (§5.1) allows both types but defines "
    "neither, and the frozen inventory labels syntactically identical bindings inconsistently, so the "
    "distinction cannot be derived from source syntax."
)


def normalize_anchor_type(anchor_type: str, anchor: str) -> str:
    if anchor_type in ("statement", "assignment") and _BINDING_RE.match(anchor.strip()):
        return "binding"
    return anchor_type


def _identity(e: dict) -> tuple:
    return (e["source_path"], e["anchor_type"], e["anchor"])


def _norm_identity(e: dict) -> tuple:
    return (e["source_path"], normalize_anchor_type(e["anchor_type"], e["anchor"]), e["anchor"])


def _occ_identity(e: dict) -> tuple:
    return _identity(e) + (e.get("context"), e.get("fingerprint"))


def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _brief(e: dict) -> dict:
    return {k: e.get(k) for k in ("source_path", "anchor_type", "anchor", "locator")}


def _align(inv_items: list[dict], dis_items: list[dict]):
    """Pair occurrences by (source_path, locator); prefer equal anchors within a group."""
    groups: dict[tuple, tuple[list, list]] = {}
    for e in inv_items:
        groups.setdefault((e["source_path"], e.get("locator")), ([], []))[0].append(e)
    for e in dis_items:
        groups.setdefault((e["source_path"], e.get("locator")), ([], []))[1].append(e)
    aligned, inv_only, dis_only = [], [], []
    for _, (iv, dv) in groups.items():
        iv, dv = list(iv), list(dv)
        for e in list(iv):
            match = next((d for d in dv if d["anchor"] == e["anchor"]), None)
            if match is not None:
                aligned.append((e, match))
                iv.remove(e)
                dv.remove(match)
        while iv and dv:
            aligned.append((iv.pop(0), dv.pop(0)))
        inv_only += iv
        dis_only += dv
    return aligned, inv_only, dis_only


def compare_inventory(discovered: dict[tuple[str, str], list[dict]], inventory: dict[tuple[str, str], list[dict]]) -> dict:
    d_pairs, i_pairs = set(discovered), set(inventory)
    pairs = {
        "inventory": len(i_pairs),
        "discovered": len(d_pairs),
        "exact": len(d_pairs & i_pairs),
        "extra": sorted(d_pairs - i_pairs),
        "missing": sorted(i_pairs - d_pairs),
    }
    pairs["result"] = _pf(not pairs["extra"] and not pairs["missing"])

    ident = {"inventory_items": 0, "discovered_items": 0, "matched": 0, "inventory_only": [], "discovered_only": []}
    norm = {"matched": 0, "inventory_only": [], "discovered_only": [], "rule": ANCHOR_TYPE_NORMALIZATION}
    occ = {"inventory_occurrences": 0, "discovered_occurrences": 0, "aligned": 0,
           "unaligned_inventory": [], "unaligned_discovered": [], "duplicate_occurrence_identity": []}
    fields = ("anchor", "anchor_type", "context", "fingerprint", "fact")
    agree = {"aligned": 0, **{f"{f}_equal": 0 for f in fields}, "differences": []}

    for pair in sorted(d_pairs | i_pairs):
        inv_items, dis_items = inventory.get(pair, []), discovered.get(pair, [])
        ident["inventory_items"] += len(inv_items)
        ident["discovered_items"] += len(dis_items)
        for key, bucket in ((_identity, ident), (_norm_identity, norm)):
            ic, dc = Counter(key(e) for e in inv_items), Counter(key(e) for e in dis_items)
            bucket["matched"] += sum((ic & dc).values())
            for k, n in (ic - dc).items():
                bucket["inventory_only"] += [{"pair": list(pair), "identity": list(k)}] * n
            for k, n in (dc - ic).items():
                bucket["discovered_only"] += [{"pair": list(pair), "identity": list(k)}] * n

        occ["inventory_occurrences"] += len(inv_items)
        occ["discovered_occurrences"] += len(dis_items)
        for side, items in (("inventory", inv_items), ("discovered", dis_items)):
            for k, n in Counter(_occ_identity(e) for e in items).items():
                if n > 1:
                    occ["duplicate_occurrence_identity"].append({"side": side, "pair": list(pair), "occurrence_identity": list(k), "count": n})
        aligned, inv_only, dis_only = _align(inv_items, dis_items)
        occ["aligned"] += len(aligned)
        occ["unaligned_inventory"] += [{"pair": list(pair), **_brief(e)} for e in inv_only]
        occ["unaligned_discovered"] += [{"pair": list(pair), **_brief(e)} for e in dis_only]

        for ie, de in aligned:
            agree["aligned"] += 1
            for f in fields:
                if ie.get(f) == de.get(f):
                    agree[f"{f}_equal"] += 1
                else:
                    agree["differences"].append({"pair": list(pair), "locator": ie.get("locator"), "field": f,
                                                 "inventory": ie.get(f), "discovered": de.get(f)})

    ident["result"] = _pf(not ident["inventory_only"] and not ident["discovered_only"])
    norm["result"] = _pf(not norm["inventory_only"] and not norm["discovered_only"])
    occ["result"] = _pf(not occ["unaligned_inventory"] and not occ["unaligned_discovered"]
                        and not occ["duplicate_occurrence_identity"])
    agree["result"] = "DIAGNOSTIC"
    agree["all_fields_equal"] = not agree["differences"]
    agree["affects_overall"] = False
    norm["name"] = ACCEPTED_NORMALIZATIONS[0]
    norm["explains_strict_mismatch"] = ident["result"] == "FAIL" and norm["result"] == "PASS"

    failures = []
    if pairs["result"] == "FAIL":
        failures.append("pairs")
    if ident["result"] == "FAIL" and norm["result"] == "FAIL":
        failures.append("evidence_identity")
    if occ["result"] == "FAIL":
        failures.append("evidence_occurrence")
    code = sum(EXIT_BITS[f] for f in failures)
    normalization_applied = not failures and norm["explains_strict_mismatch"]
    overall = "FAIL" if failures else ("PASS_WITH_NORMALIZATION" if normalization_applied else "PASS")
    return {
        "pairs": pairs,
        "evidence_identity": ident,
        "evidence_identity_normalized": norm,
        "evidence_occurrence": occ,
        "field_agreement": agree,
        "overall": overall,
        "failures": failures,
        "normalization_applied": normalization_applied,
        "accepted_normalizations": list(ACCEPTED_NORMALIZATIONS) if normalization_applied else [],
        "exit_code": code,
    }


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
    """n/d, or None (reported as JSON null / 'undefined') when d == 0."""
    return round(n / d, 4) if d else None


ASSET_STATUSES = ("ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED")
CODE_STATUSES = ("CODE_ACTION", "DOWNSTREAM_USAGE", "REVIEW_REQUIRED", "UNAFFECTED")


def _matrix(pairs: list[tuple[str, str]], statuses: tuple[str, ...]) -> dict[str, dict[str, int]]:
    """Ground truth rows x automated columns, every status present (zeros included)."""
    m = {g: {a: 0 for a in statuses} for g in statuses}
    for g, a in pairs:
        m.setdefault(g, {x: 0 for x in statuses}).setdefault(a, 0)
        m[g][a] += 1
    return m


def score_assets(base_assets: dict[str, str], auto_assets: dict[str, str]) -> dict:
    """ASSET scoring per protocol §17.1 / §18.

    REVIEW_REQUIRED is neither positive nor negative.  Binary TP/FP/FN/TN,
    precision and recall use only items where BOTH the ground truth and the
    automated output are determinate (ASSET_ACTION or UNAFFECTED).  GT
    ASSET_ACTION + automated REVIEW_REQUIRED is not an FN; GT UNAFFECTED +
    automated REVIEW_REQUIRED is not an FP.  Undefined ratios are None.
    """
    if set(base_assets) != set(auto_assets):
        raise ValueError(f"ASSET sets differ: {sorted(set(base_assets) ^ set(auto_assets))}")
    det = ("ASSET_ACTION", "UNAFFECTED")
    keys = sorted(base_assets)
    pairs = [(base_assets[k], auto_assets[k]) for k in keys]
    both_det = [(g, a) for g, a in pairs if g in det and a in det]
    tp = sum(g == "ASSET_ACTION" and a == "ASSET_ACTION" for g, a in both_det)
    fp = sum(g == "UNAFFECTED" and a == "ASSET_ACTION" for g, a in both_det)
    fn = sum(g == "ASSET_ACTION" and a == "UNAFFECTED" for g, a in both_det)
    tn = sum(g == "UNAFFECTED" and a == "UNAFFECTED" for g, a in both_det)
    n = len(keys)
    gt_rr = sum(g == "REVIEW_REQUIRED" for g, _ in pairs)
    auto_rr = sum(a == "REVIEW_REQUIRED" for _, a in pairs)
    return {
        "n": n,
        "exact_status_agreement": sum(g == a for g, a in pairs),
        "confusion_matrix": _matrix(pairs, ASSET_STATUSES),
        "ground_truth_determinate": n - gt_rr,
        "ground_truth_review_required": gt_rr,
        "matcha_review_required": auto_rr,
        "matcha_review_required_on_gt_determinate": sum(g in det and a == "REVIEW_REQUIRED" for g, a in pairs),
        "scored_binary_items": len(both_det),
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "precision": _ratio(tp, tp + fp),
        "recall": _ratio(tp, tp + fn),
        "ground_truth_review_rate": _ratio(gt_rr, n),
        "matcha_review_rate": _ratio(auto_rr, n),
        "coverage": _ratio(n - auto_rr, n),
        "coverage_percent": None if not n else round(100 * (n - auto_rr) / n, 2),
        "rows": [{"asset_path": k, "baseline": g, "automated": a, "agree": g == a} for k, (g, a) in zip(keys, pairs)],
    }


def score_code(base: dict, auto: dict) -> dict:
    """File- or relationship-level CODE scoring (§17.2), keys -> status dicts."""
    common = sorted(set(base) & set(auto))
    pairs = [(base[k], auto[k]) for k in common]
    auto_ca = sum(a == "CODE_ACTION" for _, a in pairs)
    correct_ca = sum(g == a == "CODE_ACTION" for g, a in pairs)
    return {
        "baseline": len(base),
        "automated": len(auto),
        "same_set": set(base) == set(auto),
        "missing_in_automated": sorted(set(base) - set(auto)),
        "extra_in_automated": sorted(set(auto) - set(base)),
        "exact_status_agreement": sum(g == a for g, a in pairs),
        "confusion_matrix": _matrix(pairs, CODE_STATUSES),
        "correct_code_action": correct_ca,
        "correct_downstream_usage": sum(g == a == "DOWNSTREAM_USAGE" for g, a in pairs),
        "correct_review_required": sum(g == a == "REVIEW_REQUIRED" for g, a in pairs),
        "incorrect_code_actions": sum(a == "CODE_ACTION" and g != "CODE_ACTION" for g, a in pairs),
        "missed_code_actions": sum(g == "CODE_ACTION" and a in ("DOWNSTREAM_USAGE", "UNAFFECTED") for g, a in pairs),
        "code_action_gt_automated_review_required": sum(g == "CODE_ACTION" and a == "REVIEW_REQUIRED" for g, a in pairs),
        "incorrect_downstream": sum(a == "DOWNSTREAM_USAGE" and g in ("CODE_ACTION", "UNAFFECTED") for g, a in pairs),
        "missed_downstream": sum(g == "DOWNSTREAM_USAGE" and a in ("CODE_ACTION", "UNAFFECTED") for g, a in pairs),
        "downstream_gt_automated_review_required": sum(g == "DOWNSTREAM_USAGE" and a == "REVIEW_REQUIRED" for g, a in pairs),
        "code_action_precision": _ratio(correct_ca, auto_ca),
        "matcha_review_rate": _ratio(sum(a == "REVIEW_REQUIRED" for _, a in pairs), len(pairs)),
        "coverage": _ratio(sum(a != "REVIEW_REQUIRED" for _, a in pairs), len(pairs)),
    }


def compare_report(report: dict, baseline: dict, test: Optional[str] = None) -> dict:
    base_assets = {a["asset_path"]: a["status"] for a in baseline["assets"]}
    auto_assets = {a["asset_path"]: a["status"] for a in report["assets"]}
    assets = score_assets(base_assets, auto_assets)
    assets["matcha_review_causes"] = dict(
        Counter(a.get("review_cause") for a in report["assets"] if a["status"] == "REVIEW_REQUIRED")
    )
    base_files = {c["source_path"]: c["file_status"] for c in baseline["code"]}
    auto_files = {c["source_path"]: c["file_status"] for c in report["code"]}

    def rels(code):
        return {(c["source_path"], r["related_asset"]): r["relationship_status"]
                for c in code for r in (c.get("relationships") or [])}

    br, ar = rels(baseline["code"]), rels(report["code"])
    relationships = score_code(br, ar)
    relationships["downstream_traceability_pairs_found"] = len(set(br) & set(ar))
    relationships["missing_in_automated"] = [list(k) for k in relationships["missing_in_automated"]]
    relationships["extra_in_automated"] = [list(k) for k in relationships["extra_in_automated"]]
    prov = report["provider"]
    return {
        "test": test,
        "provider": {k: prov.get(k) for k in ("name", "model", "state", "available")},
        "baseline_timing": baseline["timing"],
        "automated_timing": report["timing"],
        "assets": assets,
        "code": score_code(base_files, auto_files),
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

def _fmt(v) -> str:
    return "undefined" if v is None else str(v)


def _validation_text(r: dict) -> str:
    p, i, n, o, f = r["pairs"], r["evidence_identity"], r["evidence_identity_normalized"], r["evidence_occurrence"], r["field_agreement"]
    lines = [
        f"[A {p['result']}] pairs: inventory {p['inventory']}, discovered {p['discovered']}, exact {p['exact']}/{p['inventory']}, "
        f"extra {len(p['extra'])}, missing {len(p['missing'])}"
    ]
    lines += [f"    EXTRA   {x}" for x in p["extra"]] + [f"    MISSING {x}" for x in p["missing"]]
    lines.append(
        f"[B {i['result']}] evidence identity (strict source_path+anchor_type+anchor): inventory {i['inventory_items']}, "
        f"discovered {i['discovered_items']}, matched {i['matched']}, inventory-only {len(i['inventory_only'])}, "
        f"discovered-only {len(i['discovered_only'])}"
    )
    lines += [f"    INVENTORY-ONLY  {x['pair']} {x['identity']}" for x in i["inventory_only"]]
    lines += [f"    DISCOVERED-ONLY {x['pair']} {x['identity']}" for x in i["discovered_only"]]
    lines.append(
        f"[C {n['result']}] evidence identity after accepted normalization '{n['name']}' (statement/assignment on a "
        f"binding anchor -> binding): matched {n['matched']}, inventory-only {len(n['inventory_only'])}, "
        f"discovered-only {len(n['discovered_only'])}; explains strict mismatch: {str(n['explains_strict_mismatch']).lower()}"
    )
    lines.append(
        f"[D {o['result']}] evidence occurrence: inventory {o['inventory_occurrences']}, discovered "
        f"{o['discovered_occurrences']}, aligned {o['aligned']}, unaligned inventory {len(o['unaligned_inventory'])}, "
        f"unaligned discovered {len(o['unaligned_discovered'])}, duplicate occurrence identities "
        f"{len(o['duplicate_occurrence_identity'])}"
    )
    lines.append(
        f"[E DIAGNOSTIC] field agreement over {f['aligned']} aligned occurrences (never affects overall): "
        f"anchor {f['anchor_equal']}, anchor_type {f['anchor_type_equal']}, context {f['context_equal']}, "
        f"fingerprint {f['fingerprint_equal']}, fact {f['fact_equal']} ({len(f['differences'])} field differences)"
    )
    for d in f["differences"]:
        if d["field"] in ("anchor", "anchor_type"):
            lines.append(f"    {d['field'].upper()} DIFF {d['pair']} @ {d['locator']}: inventory={d['inventory']!r} discovered={d['discovered']!r}")
    lines.append(
        f"OVERALL: {r['overall']} (failures: {', '.join(r['failures']) or 'none'}; exit code {r['exit_code']}: "
        f"1=pairs 2=unexplained identity 4=occurrence)"
    )
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
        print(_validation_text(r))
        if a.json_out:
            a.json_out.write_text(json.dumps(r, indent=2, default=list) + "\n")
        return r["exit_code"]

    report = json.loads(a.report.read_text())
    res = compare_report(report, load_test(a.worksheet, a.test), test=a.test)
    print(json.dumps({k: v for k, v in res.items() if k != "assets"} | {"assets": {k: v for k, v in res["assets"].items() if k != "rows"}}, indent=2, default=str))
    s_ = res["assets"]
    print(f"\nasset precision: {_fmt(s_['precision'])}; recall: {_fmt(s_['recall'])}; "
          f"Matcha review rate: {_fmt(s_['matcha_review_rate'])}; coverage: {_fmt(s_['coverage'])}")
    print("per-asset:")
    for row in res["assets"]["rows"]:
        print(f"  {'=' if row['agree'] else 'x'} {row['asset_path']}: baseline {row['baseline']} / automated {row['automated']}")
    if a.json_out:
        a.json_out.write_text(json.dumps(res, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
