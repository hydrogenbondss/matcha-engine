"""Orchestrates one ``matcha impact`` run.

The engine knows nothing about experiments, evaluation labels or human
classifications.  It reads only the fixture and the change request, and it
writes one report.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any, Callable, Optional

import matcha
from matcha.impact.discovery import discover, select_provider
from matcha.impact.fixture import Fixture, load_fixture, sha256_file, verify_asset_hashes
from matcha.impact.graph import ImpactGraph, build_graph
from matcha.impact.model import Evidence
from matcha.impact.propagate import (
    IDENTIFIER_POLICIES,
    V1_LIMITATIONS,
    file_reason,
    file_status,
    infer_identifier_policy,
    relationship_reason,
    relationship_status,
)
from matcha.impact.report import SCHEMA_VERSION, summarise_counts, write_json, write_markdown
from matcha.impact.vision import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    PROVIDER_UNAVAILABLE,
    UnavailableProvider,
    classify_asset,
    load_image_input,
    unavailable_classification,
)


class ImpactError(Exception):
    pass


def _now() -> _dt.datetime:
    return _dt.datetime.now().astimezone()


def _fmt_elapsed(seconds: float) -> str:
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    if ms == 1000:
        whole, ms = whole + 1, 0
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def _locator_key(loc: str):
    path, _, num = loc.rpartition(":")
    return (path, int(num) if num.isdigit() else 0)


def _resolve_reference(fx: Fixture, reference: Optional[Path]) -> Optional[Path]:
    if reference is None:
        return None
    p = Path(reference).expanduser()
    for cand in (p, fx.root / p):
        if cand.is_file():
            return cand.resolve()
    raise ImpactError(f"reference image not found: {reference}")


def _fixture_rel(fx: Fixture, p: Path) -> str:
    try:
        return p.resolve().relative_to(fx.root.resolve()).as_posix()
    except ValueError:
        return str(p)


def _excerpt_header_evidence(fx: Fixture, path: str) -> list[Evidence]:
    out = []
    for i, line in enumerate(fx.read_text(path).splitlines(), 1):
        if line.startswith("# line_ranges:") or line.startswith("# limitation:"):
            key = line[2:].split(":", 1)[0]
            out.append(
                Evidence(
                    source_path=path,
                    anchor_type="excerpt_header",
                    anchor=line.strip(),
                    locator=f"{path}:{i}",
                    fact=f"The excerpt header states the excerpt's {key.replace('_', ' ')}; evidence is limited to that scope.",
                )
            )
        if line.startswith("# ---"):
            break
    return out


def run_impact(
    *,
    fixture: Path,
    request: str,
    reference: Optional[Path],
    output: Path,
    provider: str = "auto",
    summary: Optional[Path] = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    identifier_policy: str = "auto",
    discovery_fn: Optional[Callable[[], dict[str, Any]]] = None,
    provider_obj: Any = None,
) -> dict[str, Any]:
    if not request or not request.strip():
        raise ImpactError("--request must be non-empty")
    start = _now()

    fx = load_fixture(Path(fixture))
    bad = verify_asset_hashes(fx)
    if bad:
        raise ImpactError(f"fixture assets do not match manifest sha256: {bad}")
    ref_path = _resolve_reference(fx, reference)
    graph: ImpactGraph = build_graph(fx)

    disc = (discovery_fn or discover)()
    if provider_obj is not None:
        prov, note = provider_obj, "injected provider"
    else:
        prov, note = select_provider(provider, disc)
    ok, why = prov.available()
    if not ok and not isinstance(prov, UnavailableProvider):
        prov, note = UnavailableProvider(missing=list(disc.get("missing") or []) + [why]), why
        ok = False

    if identifier_policy == "auto":
        policy, policy_reason = infer_identifier_policy(request)
    elif identifier_policy in IDENTIFIER_POLICIES:
        policy, policy_reason = identifier_policy, "set explicitly with --identifier-policy"
    else:
        raise ImpactError(f"unknown identifier policy {identifier_policy!r}")

    # ---- ASSET classification ------------------------------------------------
    # The provider sees only the request, the reference bytes and the
    # candidate bytes under an opaque id; the id is mapped back here.
    ref_input = load_image_input(ref_path, "reference") if (ref_path and ok) else None
    asset_records: list[dict[str, Any]] = []
    asset_status: dict[str, str] = {}
    width = max(2, len(str(len(fx.assets))))
    for idx, a in enumerate(fx.assets, 1):
        cand = fx.root / a.fixture_path
        candidate_id = f"candidate-{idx:0{width}d}"
        if ok:
            cls = classify_asset(
                prov,
                request,
                ref_input,
                load_image_input(cand, candidate_id),
                {"candidate_id": candidate_id},
                threshold=confidence_threshold,
            )
        else:
            cls = unavailable_classification()
        asset_status[a.fixture_path] = cls.status
        usage = sorted(
            {
                e.locator
                for r in graph.relationships_to(a.fixture_path)
                for e in r.evidence
                if e.locator and e.source_path == r.source_path
            },
            key=_locator_key,
        )
        if cls.provider_state == "UNAVAILABLE":
            fact = f"No visual classification was made ({PROVIDER_UNAVAILABLE}); the image pixels were not judged."
        elif cls.provider_state == "AVAILABLE":
            fact = (
                f"Provider {prov.name}"
                + (f" ({prov.model})" if getattr(prov, "model", None) else "")
                + f" returned {cls.provider_status} with confidence {cls.confidence:.2f}: {cls.reason}"
            )
        else:
            fact = f"No valid visual classification was obtained (provider state {cls.provider_state}): {cls.reason}"
        asset_records.append(
            {
                "item_type": "ASSET",
                "asset_path": a.fixture_path,
                "candidate_id": candidate_id,
                "status": cls.status,
                "reason": cls.reason,
                "provider_state": cls.provider_state,
                "review_cause": cls.review_cause,
                "evidence": [
                    Evidence(
                        source_path=a.fixture_path,
                        anchor_type="asset",
                        anchor=f"sha256:{sha256_file(cand)}",
                        locator=cls.locator,
                        fact=fact,
                    ).to_dict()
                ],
                "game_usage": usage,
                "dynamic_reference_candidates": list(graph.dynamic_candidates.get(a.fixture_path, [])),
                "classification": cls.to_dict(),
            }
        )

    # ---- CODE records --------------------------------------------------------
    code_records: list[dict[str, Any]] = []
    for u in graph.eligible_code:
        rels = []
        for r in graph.relationships_for(u.fixture_path):
            ast = asset_status[r.related_asset]
            rs = relationship_status(ast, policy)
            rels.append(
                {
                    "related_asset": r.related_asset,
                    "relationship_status": rs,
                    "reason": relationship_reason(r.related_asset, ast, rs, policy),
                    "basis": sorted(r.basis),
                    "evidence": [e.to_dict() for e in r.evidence],
                }
            )
        statuses = [r["relationship_status"] for r in rels]
        fs = file_status(statuses)
        file_ev: list[dict] = []
        if u.is_excerpt:
            file_ev += [e.to_dict() for e in _excerpt_header_evidence(fx, u.fixture_path)]
        seen = set()
        for r in rels:
            if r["relationship_status"] != fs:
                continue
            for e in r["evidence"]:
                key = (e["source_path"], e["anchor_type"], e["anchor"], e.get("context"), e.get("fingerprint"))
                if key not in seen:
                    seen.add(key)
                    file_ev.append(e)
        code_records.append(
            {
                "item_type": "CODE",
                "source_path": u.fixture_path,
                "file_status": fs,
                "reason": file_reason(statuses),
                "evidence": file_ev,
                "relationships": rels,
            }
        )

    # ---- unresolved ------------------------------------------------------------
    unresolved = list(graph.unresolved)
    if not ok:
        unresolved.insert(
            0,
            {
                "kind": "provider_unavailable",
                "item": (
                    "Vision provider unavailable: no asset was visually classified, so every ASSET is "
                    "REVIEW_REQUIRED and every relationship follows. Missing: "
                    + "; ".join(getattr(prov, "missing", []) or ["(not reported)"])
                ),
                "evidence": [],
            },
        )
    unnarrowed = [d["locator"] for d in graph.dynamic_refs if not d["candidate_assets"]]
    for a in fx.assets:
        if not graph.relationships_to(a.fixture_path):
            dyn = graph.dynamic_candidates.get(a.fixture_path, [])
            unresolved.append(
                {
                    "kind": "no_static_relationship",
                    "asset_path": a.fixture_path,
                    "item": (
                        f"{a.fixture_path}: no static relationship from any scanned CODE unit was found"
                        + (
                            f"; {len(dyn)} dynamic reference(s) might resolve to it ({', '.join(dyn)}), "
                            "so it must not be treated as unreferenced"
                            if dyn
                            else "; its production usage is not established by the fixture sources"
                        )
                        + (
                            f"; {len(unnarrowed)} dynamic reference(s) without a literal prefix could resolve "
                            "to any asset, so absence of a static relationship does not prove it unreferenced"
                            if unnarrowed
                            else ""
                        )
                        + "."
                    ),
                    "dynamic_reference_locators": list(dyn),
                    "unnarrowed_dynamic_reference_locators": list(unnarrowed),
                    "evidence": [],
                }
            )

    end = _now()
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "matcha impact", "matcha_version": getattr(matcha, "__version__", None), "engine": "impact v1"},
        "request": request,
        "reference_asset": {
            "path": _fixture_rel(fx, ref_path) if ref_path else None,
            "sha256": sha256_file(ref_path) if ref_path else None,
            "is_scored_asset": bool(ref_path and fx.asset(_fixture_rel(fx, ref_path))),
        },
        "fixture": {
            "root": str(fixture),
            "manifest_sha256": fx.manifest_sha256,
            "asset_hashes_verified": True,
            "scored_asset_rule": "manifest items with type image/* and direct_production_file == true",
            "scored_code_rule": "files under game/ with >= 1 discovered relationship to a scored asset",
            "evidence_only_images": fx.evidence_only_images,
        },
        "provider": {
            "name": prov.name,
            "model": getattr(prov, "model", None),
            "state": "AVAILABLE" if ok else "UNAVAILABLE",
            "available": ok,
            "selection_note": note,
            "requested": provider if provider_obj is None else "injected",
            "confidence_threshold": confidence_threshold,
            "missing": list(getattr(prov, "missing", []) or []) if not ok else [],
            "discovery": disc,
        },
        "identifier_policy": {"policy": policy, "reason": policy_reason},
        "timing": {
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds"),
            "elapsed": _fmt_elapsed((end - start).total_seconds()),
            "elapsed_seconds": round((end - start).total_seconds(), 3),
        },
        "assets": asset_records,
        "code": code_records,
        "out_of_scope_code": [
            {"source_path": u.fixture_path, "reason": "no relationship to a scored asset was found (not scored)"}
            for u in graph.out_of_scope_code
        ],
        "unresolved_items": unresolved,
        "limitations": list(V1_LIMITATIONS),
    }
    report["counts"] = summarise_counts(report)
    write_json(report, Path(output))
    if summary is not None:
        write_markdown(report, Path(summary))
    return report
