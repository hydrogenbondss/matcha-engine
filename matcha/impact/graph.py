"""Resolve scanned references into CODE x ASSET relationships.

Relationship rules (protocol §5.3, applied generically):

* **Direct** – a CODE unit contains a literal file name or path of a scored
  asset (in any statement, assignment or table entry), or an
  ``image <name> = ...`` declaration whose expression contains such a literal.
* **Fixture-proven** – a CODE unit uses an image name (``show``/``scene``
  statement, or a string literal spelling the name), and a declaration
  anywhere in the fixture maps that exact name to a scored asset.  Evidence
  then contains both the usage anchor and the declaration anchor.

A literal matches an asset when it equals the asset's production path
relative to the game directory (``images/x.png``), or, for a bare file name
without a directory, when it equals the asset's file name.  Dynamically
composed names (``"prefix_" + attr + ".png"``) and name similarity are never
used.  One relationship per CODE unit x ASSET pair; repeated occurrences go
into that relationship's evidence list.

Dynamic references (concatenated / formatted paths, ``show expression``,
image-loading calls with non-literal arguments, and calls with non-literal
arguments to helper functions whose bodies build image paths dynamically)
never create relationships.  Each becomes a structured unresolved item
(``kind: dynamic_reference``) with its source path, locator, snippet,
reasons, and the scored assets it *might* match by literal prefix/suffix.
Assets named as such candidates are recorded so they are never presented
as simply unreferenced.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

from matcha.impact.fixture import Fixture
from matcha.impact.model import AssetUnit, CodeUnit, Evidence, Relationship
import re

from matcha.impact.renpy_scan import (
    Declaration,
    DynamicRef,
    Line,
    ScanResult,
    literal_anchor_type,
    scan_unit,
)


@dataclass
class ImpactGraph:
    fixture: Fixture
    scans: dict[str, ScanResult]
    relationships: dict[tuple[str, str], Relationship]
    eligible_code: list[CodeUnit]
    out_of_scope_code: list[CodeUnit]
    unresolved: list[dict] = field(default_factory=list)
    dynamic_refs: list[dict] = field(default_factory=list)
    dynamic_candidates: dict[str, list[str]] = field(default_factory=dict)  # asset -> locators

    def relationships_for(self, source_path: str) -> list[Relationship]:
        rels = [r for (s, _), r in self.relationships.items() if s == source_path]
        order = {a.fixture_path: i for i, a in enumerate(self.fixture.assets)}
        return sorted(rels, key=lambda r: order.get(r.related_asset, 1 << 30))

    def relationships_to(self, asset_path: str) -> list[Relationship]:
        return [r for (_, a), r in self.relationships.items() if a == asset_path]

    def pairs(self) -> set[tuple[str, str]]:
        return set(self.relationships)


def normalise_literal(value: str) -> str:
    v = value.replace("\\", "/").strip()
    while v.startswith("./"):
        v = v[2:]
    if v.startswith("game/"):
        v = v[len("game/"):]
    return v


def match_assets(value: str, assets: list[AssetUnit]) -> list[AssetUnit]:
    v = normalise_literal(value)
    hits = []
    for a in assets:
        if "/" in v:
            if a.game_path and v == a.game_path:
                hits.append(a)
        elif v == a.basename:
            hits.append(a)
    return hits


class _OccurrenceIndex:
    """Counts identical anchors per scope so occurrences can be told apart."""

    def __init__(self, scans: dict[str, ScanResult]):
        self.index: dict[tuple, list[int]] = defaultdict(list)
        for path, sr in scans.items():
            for ln in sr.lines:
                if ln.code:
                    self.index[(path, ln.code, ln.scope())].append(ln.fixture_line)

    def position(self, ln: Line) -> tuple[int, int]:
        seq = self.index[(ln.source_path, ln.code, ln.scope())]
        return seq.index(ln.fixture_line) + 1, len(seq)


def _context(ln: Line, occ: _OccurrenceIndex, anchor_type: str) -> str:
    kind, text = ln.scope()
    if anchor_type == "declaration":
        base = "init-time image declaration"
        return f"{text}; {base}" if kind == "block" else base
    if anchor_type == "config" and ln.table:
        base = f"{ln.table} table"
        return f"{text}; {base}" if kind == "block" else base
    i, n = occ.position(ln)
    if kind == "label" or n > 1:
        where = {"label": "label", "block": "block", "function": "function", "file": "file"}[kind]
        return f"{text}; occurrence {i} of {n} of this anchor in this {where}"
    return text


def _fingerprint(ln: Line, anchor_type: str) -> Optional[str]:
    if anchor_type in ("declaration", "config") or ln.prev_nonblank is None:
        return None
    if ln.is_excerpt:
        return f"previous non-blank line in block: {ln.prev_nonblank}"
    return f"previous non-blank line: {ln.prev_nonblank}"


def _ev(ln: Line, anchor_type: str, fact: str, occ: _OccurrenceIndex) -> Evidence:
    return Evidence(
        source_path=ln.source_path,
        anchor_type=anchor_type,
        anchor=ln.code,
        context=_context(ln, occ, anchor_type),
        locator=ln.locator,
        fingerprint=_fingerprint(ln, anchor_type),
        fact=fact,
    )


def build_graph(fx: Fixture) -> ImpactGraph:
    scans: dict[str, ScanResult] = {}
    for unit in fx.code_candidates:
        scans[unit.fixture_path] = scan_unit(unit, fx.read_text(unit.fixture_path))
    occ = _OccurrenceIndex(scans)
    unresolved: list[dict] = []

    # Declaration index across the whole fixture (cross-file resolution).
    decls: dict[str, list[tuple[Declaration, list[AssetUnit]]]] = defaultdict(list)
    for sr in scans.values():
        for d in sr.declarations:
            hits = []
            for lit in d.literals:
                hits.extend(match_assets(lit, fx.assets))
            decls[d.name].append((d, hits))
    scored_tags = {
        name.split()[0] for name, entries in decls.items() if any(h for _, h in entries)
    }

    rels: dict[tuple[str, str], Relationship] = {}

    def rel(src: str, asset: AssetUnit) -> Relationship:
        key = (src, asset.fixture_path)
        if key not in rels:
            rels[key] = Relationship(source_path=src, related_asset=asset.fixture_path)
        return rels[key]

    def decl_ev(d: Declaration, user_path: str) -> Evidence:
        lit = ", ".join(d.literals)
        if d.line.source_path == user_path:
            fact = f"The source declares the {d.name} image identifier as {d.rhs}."
        else:
            fact = f"The frozen fixture maps the {d.name} identifier to {lit}."
        return _ev(d.line, "declaration", fact, occ)

    def resolve_name(name: str, usage_ev: Evidence, src: str, ln: Line) -> None:
        entries = decls.get(name)
        if not entries:
            if name.split()[0] in scored_tags:
                unresolved.append(
                    {
                        "kind": "unresolved_image_name",
                        "item": (
                            f"Image name '{name}' is used but no exact image declaration was found "
                            "in the fixture; the usage is not attributed to a scored asset."
                        ),
                        "evidence": [usage_ev.to_dict()],
                    }
                )
            return
        targets = {a.fixture_path for _, hits in entries for a in hits}
        if len({tuple(sorted(a.fixture_path for a in h)) for _, h in entries}) > 1:
            unresolved.append(
                {
                    "kind": "conflicting_declaration",
                    "item": (
                        f"Image name '{name}' has conflicting declarations mapping to "
                        f"{sorted(targets)}; not attributed."
                    ),
                    "evidence": [usage_ev.to_dict()] + [decl_ev(d, src).to_dict() for d, _ in entries],
                }
            )
            return
        for d, hits in entries:
            for a in hits:
                r = rel(src, a)
                if d.line.source_path != src:
                    r.add(decl_ev(d, src))
                    r.basis.add("fixture_proven")
                else:
                    r.basis.add("direct")
                r.add(usage_ev)

    for src, sr in scans.items():
        for d in sr.declarations:
            for lit in d.literals:
                for a in match_assets(lit, fx.assets):
                    r = rel(src, a)
                    r.add(decl_ev(d, src))
                    r.basis.add("direct")
        for u in sr.usages:
            ev = _ev(u.line, "statement", f"The source displays the {u.name} image identifier.", occ)
            resolve_name(u.name, ev, src, u.line)
        for s in sr.strings:
            at = literal_anchor_type(s.line)
            if s.kind == "file":
                hits = match_assets(s.value, fx.assets)
                if len(hits) > 1:
                    unresolved.append(
                        {
                            "kind": "ambiguous_literal",
                            "item": f"Literal '{s.value}' matches several scored assets by file name; not attributed.",
                            "evidence": [_ev(s.line, at, f"The source contains the literal {s.value}.", occ).to_dict()],
                        }
                    )
                    continue
                for a in hits:
                    where = f"The {s.line.table} table contains" if at == "config" else "The source contains"
                    fact = f"{where} the literal {s.value}, which names the asset file {a.basename}."
                    r = rel(src, a)
                    r.add(_ev(s.line, at, fact, occ))
                    r.basis.add("direct")
            else:
                ev = _ev(
                    s.line,
                    at,
                    f"The source references the {s.value} image identifier in a string literal.",
                    occ,
                )
                if s.value in decls:
                    resolve_name(s.value, ev, src, s.line)

    # Order evidence: declarations from other files first, then own-file line order.
    def sort_key(e: Evidence, src: str):
        own = e.source_path == src
        loc = e.locator or ""
        num = int(loc.rsplit(":", 1)[-1]) if loc.rsplit(":", 1)[-1].isdigit() else 0
        return (own, e.source_path, num)

    for (src, _), r in rels.items():
        r.evidence.sort(key=lambda e, s=src: sort_key(e, s))

    eligible = [u for u in fx.code_candidates if any(s == u.fixture_path for s, _ in rels)]
    out_scope = [u for u in fx.code_candidates if u not in eligible]
    for sr in scans.values():
        for w in sr.warnings:
            unresolved.append({"kind": "scanner_limitation", "item": w, "evidence": []})

    dyn_items, dyn_candidates = _dynamic_items(scans, fx.assets, occ)
    unresolved.extend(dyn_items)
    return ImpactGraph(
        fixture=fx,
        scans=scans,
        relationships=rels,
        eligible_code=eligible,
        out_of_scope_code=out_scope,
        unresolved=unresolved,
        dynamic_refs=dyn_items,
        dynamic_candidates=dyn_candidates,
    )


def _candidates(prefixes: list[str], suffixes: list[str], assets: list[AssetUnit]) -> list[AssetUnit]:
    hits: list[AssetUnit] = []
    for p in prefixes:
        v = normalise_literal(p)
        for a in assets:
            gp = a.game_path or ""
            ok = gp.startswith(v) if "/" in v else (a.basename.startswith(v) or gp.startswith(v))
            if ok and all(gp.lower().endswith(normalise_literal(sfx).lower()) or a.basename.lower().endswith(sfx.lower()) for sfx in suffixes):
                if a not in hits:
                    hits.append(a)
    return hits


def _dynamic_items(scans: dict[str, ScanResult], assets: list[AssetUnit], occ: "_OccurrenceIndex"):
    """Structured unresolved items for dynamic references (flag only)."""
    found: list[DynamicRef] = []
    for sr in scans.values():
        found.extend(sr.dynamic)
    # helpers whose body builds image paths dynamically (defined anywhere in the fixture)
    helpers = sorted({d.line.function for d in found if d.line.function})
    if helpers:
        call_re = re.compile(
            r"(?<![\w.])(" + "|".join(re.escape(h) for h in helpers) + r")\s*\(\s*(?!(?:True|False|None)\b)([A-Za-z_][\w\.]*)\s*[,)]"
        )
        seen = {(d.line.source_path, d.line.fixture_line) for d in found}
        for sr in scans.values():
            for ln in sr.lines:
                if not ln.code or ln.code.startswith("def "):
                    continue
                m = call_re.search(ln.bare)
                if not m:
                    continue
                reason = (
                    f"call to {m.group(1)}(), whose body builds image paths dynamically, "
                    f"with the non-literal argument '{m.group(2)}'"
                )
                key = (ln.source_path, ln.fixture_line)
                if key in seen:
                    for d in found:
                        if (d.line.source_path, d.line.fixture_line) == key and reason not in d.reasons:
                            d.reasons.append(reason)
                    continue
                seen.add(key)
                found.append(DynamicRef(line=ln, reasons=[reason]))

    items: list[dict] = []
    by_asset: dict[str, list[str]] = {}
    for d in sorted(found, key=lambda d: (d.line.source_path, d.line.fixture_line)):
        cands = _candidates(d.prefixes, d.suffixes, assets)
        for a in cands:
            by_asset.setdefault(a.fixture_path, []).append(d.line.locator)
        ev = _ev(
            d.line,
            literal_anchor_type(d.line),
            "The source builds an image/file reference dynamically; it is not resolved statically.",
            occ,
        )
        items.append(
            {
                "kind": "dynamic_reference",
                "item": (
                    f"{d.line.locator}: dynamic image/file reference not resolved to a scored asset "
                    f"({'; '.join(d.reasons)})."
                ),
                "source_path": d.line.source_path,
                "locator": d.line.locator,
                "snippet": d.line.code,
                "reasons": list(d.reasons),
                "literal_prefixes": list(d.prefixes),
                "literal_suffixes": list(d.suffixes),
                "candidate_assets": [a.fixture_path for a in cands],
                "candidate_basis": (
                    "scored assets whose path or file name starts with a literal prefix of the expression"
                    if d.prefixes
                    else "no literal prefix; candidates cannot be narrowed"
                ),
                "evidence": [ev.to_dict()],
            }
        )
    return items, by_asset
