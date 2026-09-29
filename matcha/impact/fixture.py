"""Load a frozen impact fixture.

Scored-set derivation (generic, data-driven; no file names are hard-coded):

* **ASSET candidates** are manifest items whose ``type`` starts with
  ``image/`` and whose ``direct_production_file`` is true, i.e. image files
  that are the production-baseline bytes rather than review copies or
  approval references.  Other images (``direct_production_file: false``)
  are evidence-only.
* **CODE candidates** are every text file under the fixture's ``game/``
  directory (``*.rpy`` and ``*.rpy.excerpt.txt``).  A candidate becomes a
  scored CODE unit only if relationship discovery finds at least one
  relationship to a scored ASSET (protocol eligibility rule, applied in
  graph.py).  Candidates without such a relationship are reported as out of
  scoring scope, never as UNAFFECTED.

The loader never reads anything outside the fixture root.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from matcha.impact.model import AssetUnit, CodeUnit

MANIFEST_REL = "metadata/fixture-manifest.json"
CODE_SUFFIXES = (".rpy", ".rpy.excerpt.txt")
EXCERPT_MAGIC = "# EVIDENCE EXCERPT"
_HEADER_RE = re.compile(r"^#\s*([a-z_0-9]+):\s*(.*)$")


class FixtureError(Exception):
    pass


@dataclass
class Fixture:
    root: Path
    manifest: dict[str, Any]
    manifest_sha256: str
    assets: list[AssetUnit]
    code_candidates: list[CodeUnit]
    evidence_only_images: list[str] = field(default_factory=list)

    def asset(self, fixture_path: str) -> Optional[AssetUnit]:
        for a in self.assets:
            if a.fixture_path == fixture_path:
                return a
        return None

    def read_text(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def rel(self, path: Path) -> str:
        return Path(path).resolve().relative_to(self.root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _game_relative(item: dict[str, Any], source_root: Optional[str]) -> Optional[str]:
    """Production path of a manifest item relative to the Ren'Py game dir."""
    candidates = []
    if item.get("production_path"):
        candidates.append(str(item["production_path"]))
    if item.get("direct_production_file") and item.get("source_path"):
        candidates.append(str(item["source_path"]))
    for raw in candidates:
        p = raw.replace("\\", "/")
        if source_root:
            root = source_root.rstrip("/") + "/"
            if p.startswith(root):
                p = p[len(root):]
        if p.startswith("game/"):
            return p[len("game/"):]
        if "/game/" in p and not source_root:
            return p.split("/game/", 1)[1]
    return None


def parse_excerpt_header(text: str) -> dict[str, str]:
    header: dict[str, str] = {}
    lines = text.splitlines()
    if not lines or not lines[0].startswith(EXCERPT_MAGIC):
        return header
    for line in lines[1:]:
        if line.startswith("# ---"):
            break
        m = _HEADER_RE.match(line)
        if m:
            header[m.group(1)] = m.group(2).strip()
    return header


def load_fixture(root: Path) -> Fixture:
    root = Path(root).expanduser()
    if not root.is_dir():
        raise FixtureError(f"fixture root not found: {root}")
    manifest_path = root / MANIFEST_REL
    if not manifest_path.is_file():
        raise FixtureError(f"fixture manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = manifest.get("items")
    if not isinstance(items, list):
        raise FixtureError("fixture manifest has no 'items' list")
    source_root = manifest.get("source_root")

    assets: list[AssetUnit] = []
    evidence_only: list[str] = []
    for item in items:
        fpath = item.get("fixture_path")
        itype = str(item.get("type") or "")
        if not fpath or not itype.startswith("image/"):
            continue
        if not (root / fpath).is_file():
            raise FixtureError(f"manifest image missing from fixture: {fpath}")
        if item.get("direct_production_file") is True:
            assets.append(
                AssetUnit(
                    fixture_path=fpath,
                    game_path=_game_relative(item, source_root),
                    sha256=item.get("sha256"),
                    type=itype,
                    width=item.get("width"),
                    height=item.get("height"),
                )
            )
        else:
            evidence_only.append(fpath)

    code: list[CodeUnit] = []
    game_dir = root / "game"
    if game_dir.is_dir():
        for p in sorted(game_dir.rglob("*")):
            if not p.is_file() or not p.name.endswith(CODE_SUFFIXES):
                continue
            rel = p.relative_to(root).as_posix()
            text = p.read_text(encoding="utf-8")
            header = parse_excerpt_header(text)
            origin = None
            if header.get("source_path"):
                origin = header["source_path"].replace("\\", "/")
                if source_root and origin.startswith(source_root.rstrip("/") + "/"):
                    origin = origin[len(source_root.rstrip("/")) + 1:]
            code.append(
                CodeUnit(
                    fixture_path=rel,
                    is_excerpt=bool(header),
                    origin_path=origin,
                    excerpt_header=header,
                )
            )

    return Fixture(
        root=root,
        manifest=manifest,
        manifest_sha256=sha256_file(manifest_path),
        assets=assets,
        code_candidates=code,
        evidence_only_images=evidence_only,
    )


def verify_asset_hashes(fx: Fixture) -> list[str]:
    """Return fixture paths whose bytes do not match the manifest sha256."""
    bad = []
    for a in fx.assets:
        if a.sha256 and sha256_file(fx.root / a.fixture_path) != a.sha256:
            bad.append(a.fixture_path)
    return bad
