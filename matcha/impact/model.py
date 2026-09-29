"""Shared data types for impact analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

ASSET_STATUSES = ("ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED")
CODE_STATUSES = ("CODE_ACTION", "DOWNSTREAM_USAGE", "REVIEW_REQUIRED", "UNAFFECTED")
ANCHOR_TYPES = (
    "declaration",
    "statement",
    "function",
    "label",
    "assignment",
    "config",
    "excerpt_header",
    "asset",
    "metadata",
)


@dataclass
class Evidence:
    """Protocol evidence item.

    Evidence identity is ``(source_path, anchor_type, anchor)``. Occurrence
    identity additionally uses ``context`` and ``fingerprint``. ``locator`` is
    a convenience pointer only and never part of either identity.
    """

    source_path: str
    anchor_type: str
    anchor: str
    fact: str
    context: Optional[str] = None
    locator: Optional[str] = None
    fingerprint: Optional[str] = None

    def __post_init__(self) -> None:
        if self.anchor_type not in ANCHOR_TYPES:
            raise ValueError(f"anchor_type {self.anchor_type!r} not allowed")
        if not self.anchor:
            raise ValueError("anchor must be non-empty")

    @property
    def identity(self) -> tuple[str, str, str]:
        return (self.source_path, self.anchor_type, self.anchor)

    @property
    def occurrence_identity(self) -> tuple:
        return self.identity + (self.context, self.fingerprint)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "source_path": self.source_path,
            "anchor_type": self.anchor_type,
            "anchor": self.anchor,
        }
        if self.context is not None:
            out["context"] = self.context
        if self.locator is not None:
            out["locator"] = self.locator
        if self.fingerprint is not None:
            out["fingerprint"] = self.fingerprint
        out["fact"] = self.fact
        return out


@dataclass
class AssetUnit:
    """A scored static asset in the fixture."""

    fixture_path: str  # fixture-relative, e.g. assets/foo.png
    game_path: Optional[str]  # production path relative to the game dir
    sha256: Optional[str]
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    @property
    def basename(self) -> str:
        src = self.game_path or self.fixture_path
        return src.replace("\\", "/").rsplit("/", 1)[-1]


@dataclass
class CodeUnit:
    """A game source file or evidence excerpt in the fixture."""

    fixture_path: str
    is_excerpt: bool
    origin_path: Optional[str] = None  # source path relative to project root
    excerpt_header: dict[str, str] = field(default_factory=dict)


@dataclass
class Relationship:
    source_path: str  # CODE unit fixture path
    related_asset: str  # ASSET fixture path
    evidence: list[Evidence] = field(default_factory=list)
    basis: set[str] = field(default_factory=set)  # {"direct", "fixture_proven"}

    def add(self, ev: Evidence) -> None:
        if all(e.occurrence_identity != ev.occurrence_identity for e in self.evidence):
            self.evidence.append(ev)
