"""Matcha impact analysis (experimental v1).

Read-only analysis of a frozen fixture: given a canonical visual change
request, classify which static production assets change and how the game
source that references them is affected.

Pipeline:
    fixture.py      load scored ASSET candidates and CODE candidates from the
                    fixture manifest and the fixture's game/ directory
    renpy_scan.py   generic line-level Ren'Py / Python scanner (declarations,
                    show/scene statements, literal paths, identifier strings,
                    UPPER_CASE table entries, excerpt headers)
    graph.py        resolve references to scored assets (direct and
                    declaration-proven), one relationship per CODE x ASSET pair
    vision.py       VisionProvider interface, strict response validation,
                    "unavailable" and Ollama adapters
    discovery.py    provider discovery (env-var presence only, local tools)
    propagate.py    protocol status rules (relationship + file precedence)
    report.py       JSON report + markdown summary
    engine.py       orchestration used by ``matcha impact``

Nothing in this package reads experiment worksheets or ground truth.
"""

__all__ = ["run_impact"]


def run_impact(*args, **kwargs):  # lazy import keeps ``matcha --help`` fast
    from matcha.impact.engine import run_impact as _run

    return _run(*args, **kwargs)
