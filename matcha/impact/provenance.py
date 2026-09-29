"""Run provenance for ``matcha impact`` reports.

Records only facts that can be read at run time; nothing is guessed:

* ``engine.git_commit``: ``git rev-parse HEAD`` of the repository that
  contains this package, or null when git or a repository is unavailable.
* ``engine.git_worktree_dirty``: from ``git status --porcelain`` in that
  repository (tracked and untracked changes): false when clean, true when any
  change is present, null when the status cannot be determined.  Only the
  boolean is recorded; no filenames, diffs or contents.
* ``fixture.manifest_sha256`` and ``reference.sha256``: copied from the
  report (computed by the engine from the files it read).
* ``provider.name`` / ``provider.model`` / ``provider.state``: copied from
  the report.
* ``provider.model_identity``: only what the selected provider already
  exposes.  For Ollama this is the ``digest`` (from ``/api/tags``) and the
  ``details`` (from ``/api/show``, else ``/api/tags``) that discovery
  already received for the selected model; null when absent or when the
  provider is unavailable.
* ``vision_prompt``: sha256 of the prompt template, of the vision module
  source (which also holds the provider request options), and
  ``rendered_prompt_sha256``: the SHA-256 of the exact prompt Matcha renders
  (``vision.build_prompt``) from the request and the reference-presence
  state.  It is a reproducibility fingerprint, NOT proof that the prompt was
  delivered over the network; provider availability and execution state are
  reported separately (``provider.state``, the report's
  ``provider_execution``).  Null when the run renders no prompt (no
  available provider).

No environment values, API keys or other secrets are read or recorded.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Optional

import matcha.impact.vision as vision

_SHA_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
PACKAGE_DIR = Path(__file__).resolve().parent


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_git(args: list[str], cwd: Path) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def engine_git_commit(run_git: Callable[[list[str], Path], Optional[str]] = _run_git) -> Optional[str]:
    """HEAD commit of the repository containing this package, or None (never guessed)."""
    sha = run_git(["rev-parse", "HEAD"], PACKAGE_DIR)
    return sha if sha and _SHA_RE.match(sha) else None


def engine_git_worktree_dirty(run_git: Callable[[list[str], Path], Optional[str]] = _run_git) -> Optional[bool]:
    """Whether the repository containing this package has tracked or untracked
    changes (``git status --porcelain``): False when clean, True when any change
    is present, None when the status cannot be determined.  Only the boolean is
    returned; the porcelain output (filenames) is discarded."""
    out = run_git(["status", "--porcelain", "--untracked-files=normal"], PACKAGE_DIR)
    if out is None:
        return None
    return bool(out.strip())


def _model_identity(report: dict[str, Any]) -> Optional[dict[str, Any]]:
    prov = report.get("provider") or {}
    if not prov.get("available") or prov.get("name") != "ollama" or not prov.get("model"):
        return None
    ident = (((prov.get("discovery") or {}).get("ollama") or {}).get("model_identity") or {}).get(prov["model"])
    if not ident or (ident.get("digest") is None and ident.get("details") is None):
        return None
    return {"digest": ident.get("digest"), "details": ident.get("details"), "source": ident.get("source")}


def build_provenance(
    report: dict[str, Any],
    *,
    git_commit: Optional[Callable[[], Optional[str]]] = None,
    git_worktree_dirty: Optional[Callable[[], Optional[bool]]] = None,
) -> dict[str, Any]:
    prov = report.get("provider") or {}
    ref = report.get("reference_asset") or {}
    fx = report.get("fixture") or {}
    # Matcha renders the vision prompt only for an available provider.
    rendered = (
        _sha256_text(vision.build_prompt(report.get("request", ""), ref.get("path") is not None))
        if prov.get("available")
        else None
    )
    return {
        "engine": {
            "git_commit": (git_commit or engine_git_commit)(),
            "git_commit_source": "git rev-parse HEAD in the repository containing matcha/impact; null if unavailable",
            "git_worktree_dirty": (git_worktree_dirty or engine_git_worktree_dirty)(),
            "git_worktree_dirty_source": (
                "git status --porcelain (tracked and untracked changes) in the repository containing "
                "matcha/impact; true if any change, false if clean, null if undeterminable; "
                "no filenames recorded"
            ),
            "matcha_version": (report.get("tool") or {}).get("matcha_version"),
            "report_schema": report.get("schema_version"),
        },
        "fixture": {"manifest_sha256": fx.get("manifest_sha256")},
        "reference": {"path": ref.get("path"), "sha256": ref.get("sha256")},
        "provider": {
            "name": prov.get("name"),
            "model": prov.get("model"),
            "state": prov.get("state"),
            "model_identity": _model_identity(report),
        },
        "vision_prompt": {
            "template_sha256": _sha256_text(vision.PROMPT_TEMPLATE),
            "vision_module_sha256": hashlib.sha256(Path(vision.__file__).read_bytes()).hexdigest(),
            "rendered_prompt_sha256": rendered,
            "rendered_prompt_sha256_note": (
                "SHA-256 of the exact prompt Matcha renders from the request and reference-presence state; "
                "a reproducibility fingerprint, not proof of network delivery; provider availability and "
                "execution state are reported separately; null when no prompt is rendered"
            ),
        },
    }
