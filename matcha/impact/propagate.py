"""Status propagation per Evidence Protocol #1 (§5, §6, §7, §12).

Relationship status is derived from (a) the related asset's status and
(b) whether the source's identifier for that asset stays valid under the
requested change:

=================  ====================  ==================  ==================
asset status       identifiers kept      identifiers change  unknown
=================  ====================  ==================  ==================
ASSET_ACTION       DOWNSTREAM_USAGE      CODE_ACTION         REVIEW_REQUIRED
UNAFFECTED         UNAFFECTED            UNAFFECTED          UNAFFECTED
REVIEW_REQUIRED    REVIEW_REQUIRED       REVIEW_REQUIRED     REVIEW_REQUIRED
=================  ====================  ==================  ==================

File status is the highest-precedence relationship status:
``CODE_ACTION > DOWNSTREAM_USAGE > REVIEW_REQUIRED > UNAFFECTED`` (§6).
An asset's ASSET_ACTION never by itself makes a relationship CODE_ACTION
(§7); only an identifier change does.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from matcha.impact.model import CODE_STATUSES

PRECEDENCE = ("CODE_ACTION", "DOWNSTREAM_USAGE", "REVIEW_REQUIRED", "UNAFFECTED")
IDENTIFIER_POLICIES = ("preserved", "changed", "unknown")

# Wording that would put file names / paths / image identifiers in play.
_IDENTIFIER_CHANGE_RE = re.compile(
    r"\b(renam\w*|new (file ?names?|paths?|identifiers?|tags?|image names?)|"
    r"file ?names?|move[sd]? (the )?(files?|assets?)|relocat\w*|path changes?|"
    r"\.(png|jpe?g|webp)\b|identifier)",
    re.IGNORECASE,
)


def infer_identifier_policy(request: str) -> tuple[str, str]:
    """Decide whether the request keeps existing file names / image identifiers.

    A canonical *visual* change replaces pixels in place.  If the request text
    does not mention file names, paths, renames or identifiers, existing
    identifiers are taken to stay valid ("preserved").  If it does, the tool
    cannot decide the required source edits automatically ("unknown").
    """
    m = _IDENTIFIER_CHANGE_RE.search(request or "")
    if m:
        return "unknown", f"request mentions '{m.group(0)}', so identifier validity is not decided automatically"
    return (
        "preserved",
        "request describes a visual design change and names no new file names, paths or image "
        "identifiers, so existing identifiers are treated as remaining valid",
    )


def relationship_status(asset_status: str, identifier_policy: str) -> str:
    if identifier_policy not in IDENTIFIER_POLICIES:
        raise ValueError(f"unknown identifier policy {identifier_policy!r}")
    if asset_status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"
    if asset_status == "UNAFFECTED":
        return "UNAFFECTED"
    if asset_status == "ASSET_ACTION":
        return {
            "preserved": "DOWNSTREAM_USAGE",
            "changed": "CODE_ACTION",
            "unknown": "REVIEW_REQUIRED",
        }[identifier_policy]
    raise ValueError(f"unknown asset status {asset_status!r}")


def relationship_reason(asset_path: str, asset_status: str, rel_status: str, identifier_policy: str) -> str:
    if rel_status == "DOWNSTREAM_USAGE":
        return (
            f"The source references {asset_path}, whose asset status is ASSET_ACTION; the request keeps "
            "existing file names and image identifiers, so the reference stays valid and the source "
            "needs no edit because of this change."
        )
    if rel_status == "CODE_ACTION":
        return (
            f"The source references {asset_path}, whose asset status is ASSET_ACTION, and the request "
            "changes the identifier or file name the source uses, so the source must be edited."
        )
    if rel_status == "UNAFFECTED":
        return (
            f"The related asset {asset_path} is UNAFFECTED by this change and no identifier changes, "
            "so this relationship needs no edit."
        )
    if asset_status == "REVIEW_REQUIRED":
        return (
            f"The related asset {asset_path} has status REVIEW_REQUIRED, so it cannot be determined "
            "whether this relationship points to an affected asset."
        )
    return (
        f"The related asset {asset_path} is ASSET_ACTION, but whether the source's identifier stays "
        f"valid is undetermined (identifier policy: {identifier_policy})."
    )


def file_status(statuses: Iterable[str]) -> str:
    sts = list(statuses)
    if not sts:
        raise ValueError("a scored CODE unit must have at least one relationship")
    for s in sts:
        if s not in CODE_STATUSES:
            raise ValueError(f"unknown relationship status {s!r}")
    for p in PRECEDENCE:
        if p in sts:
            return p
    raise AssertionError("unreachable")


def file_reason(statuses: Iterable[str]) -> str:
    sts = list(statuses)
    fs = file_status(sts)
    counts = Counter(sts)
    parts = ", ".join(f"{counts[p]} {p}" for p in PRECEDENCE if counts[p])
    return (
        f"File status {fs} is the highest-precedence status (CODE_ACTION > DOWNSTREAM_USAGE > "
        f"REVIEW_REQUIRED > UNAFFECTED) among this unit's {len(sts)} scored relationships ({parts})."
    )
