"""JSON report + markdown summary for ``matcha impact``."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "matcha-impact/1"


def summarise_counts(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "assets": len(report["assets"]),
        "asset_status": dict(Counter(a["status"] for a in report["assets"])),
        "code_units": len(report["code"]),
        "file_status": dict(Counter(c["file_status"] for c in report["code"])),
        "relationships": sum(len(c["relationships"]) for c in report["code"]),
        "relationship_status": dict(
            Counter(r["relationship_status"] for c in report["code"] for r in c["relationships"])
        ),
        "relationship_evidence_items": sum(
            len(r["evidence"]) for c in report["code"] for r in c["relationships"]
        ),
        "unresolved_items": len(report["unresolved_items"]),
    }


def write_json(report: dict[str, Any], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _md_escape(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    c = report["counts"]
    prov = report["provider"]
    t = report["timing"]
    lines = [
        "# Matcha impact report",
        "",
        f"- Request: {report['request']}",
        f"- Test case label: {report.get('test_case') or '(none)'}",
        f"- Reference asset: `{report['reference_asset']['path']}` (sha256 {report['reference_asset']['sha256']})",
        f"- Fixture: `{report['fixture']['root']}` (manifest sha256 {report['fixture']['manifest_sha256']})",
        f"- Provider: **{prov['name']}**" + (f" / model `{prov['model']}`" if prov.get("model") else "")
        + f" (available: {prov['available']}; {prov['selection_note']})",
        f"- Identifier policy: {report['identifier_policy']['policy']} ({report['identifier_policy']['reason']})",
        f"- Timing: {t['start']} -> {t['end']} ({t['elapsed']})",
        "",
    ]
    if not prov["available"]:
        lines += ["> **Provider unavailable.** No visual judgement was made; every asset is REVIEW_REQUIRED.", ""]
        if prov.get("missing"):
            lines += ["Missing for a real provider:", ""] + [f"- {m}" for m in prov["missing"]] + [""]
    lines += [
        "## Counts",
        "",
        f"- ASSET: {c['assets']} — " + ", ".join(f"{k} {v}" for k, v in sorted(c["asset_status"].items())),
        f"- CODE: {c['code_units']} — " + ", ".join(f"{k} {v}" for k, v in sorted(c["file_status"].items())),
        f"- Relationships: {c['relationships']} — "
        + ", ".join(f"{k} {v}" for k, v in sorted(c["relationship_status"].items())),
        f"- Relationship evidence items: {c['relationship_evidence_items']}",
        f"- Unresolved items: {c['unresolved_items']}",
        "",
        "## Assets",
        "",
        "| Asset | Status | Confidence | Reason | Game usage |",
        "|---|---|---|---|---|",
    ]
    for a in report["assets"]:
        lines.append(
            f"| `{a['asset_path']}` | {a['status']} | {a['classification']['confidence']:.2f} | "
            f"{_md_escape(a['reason'])} | {len(a['game_usage'])} |"
        )
    lines += ["", "## CODE units", "", "| Source | File status | Relationships |", "|---|---|---|"]
    for u in report["code"]:
        rs = Counter(r["relationship_status"] for r in u["relationships"])
        lines.append(
            f"| `{u['source_path']}` | {u['file_status']} | {len(u['relationships'])} ("
            + ", ".join(f"{k} {v}" for k, v in sorted(rs.items()))
            + ") |"
        )
    lines += ["", "## Relationships", "", "| Source | Asset | Status | Basis | Evidence |", "|---|---|---|---|---|"]
    for u in report["code"]:
        for r in u["relationships"]:
            lines.append(
                f"| `{u['source_path']}` | `{r['related_asset']}` | {r['relationship_status']} | "
                f"{', '.join(r['basis'])} | {len(r['evidence'])} |"
            )
    if report.get("out_of_scope_code"):
        lines += ["", "## CODE candidates out of scoring scope", ""]
        lines += [f"- `{o['source_path']}`: {o['reason']}" for o in report["out_of_scope_code"]]
    lines += ["", "## Unresolved items", ""]
    lines += [f"- {_md_escape(u['item'])}" for u in report["unresolved_items"]] or ["- (none)"]
    lines.append("")
    return "\n".join(lines)


def write_markdown(report: dict[str, Any], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")
    return path
