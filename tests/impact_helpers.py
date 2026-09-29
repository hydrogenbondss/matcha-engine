"""Shared helpers for impact tests (synthetic fixtures; no real game data)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
REAL_FIXTURE = REPO / "fixtures" / "kite-production"


def png(path: Path, color=(10, 20, 30)) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), color).save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(root: Path, files: dict[str, str], images: dict[str, dict]) -> Path:
    """Create a minimal fixture.

    images: fixture_path -> {"game": "images/x.png" or None, "direct": bool}
    files:  fixture-relative text files (game sources / excerpts)
    """
    root.mkdir(parents=True, exist_ok=True)
    items = []
    for i, (fp, spec) in enumerate(images.items()):
        sha = png(root / fp, (i * 20 % 255, 40, 60))
        item = {
            "fixture_path": fp,
            "type": "image/png test plate",
            "direct_production_file": spec.get("direct", True),
            "sha256": sha,
            "source_path": "/proj/" + ("game/" + spec["game"] if spec.get("game") else "review/" + fp),
        }
        if spec.get("game") and spec.get("production_path", True):
            item["production_path"] = "/proj/game/" + spec["game"]
        items.append(item)
    for fp, text in files.items():
        p = root / fp
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        items.append({"fixture_path": fp, "type": "renpy script", "direct_production_file": True})
    (root / "metadata").mkdir(exist_ok=True)
    (root / "metadata" / "fixture-manifest.json").write_text(
        json.dumps({"source_root": "/proj", "items": items})
    )
    return root


def fake_discovery(**over):
    d = {
        "api_key_env_present": {},
        "python_packages": {},
        "binaries": {},
        "ollama": {"host": "http://127.0.0.1:11434", "reachable": False, "models": [], "vision_models": []},
        "comfyui": {"address": "127.0.0.1:8188", "reachable": False},
        "missing": ["test: no provider"],
    }
    d.update(over)
    return d
