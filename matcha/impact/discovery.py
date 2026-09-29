"""Discover which vision providers could actually run here.

Checks only *presence*: environment variable names (values are never read
into the report or printed), importable packages, binaries on PATH, and
local servers on their default ports.  It does not download models, start
servers, or call any remote API.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from matcha.impact.vision import OllamaProvider, UnavailableProvider

API_KEY_VARS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "XAI_API_KEY",
    "OPENROUTER_API_KEY",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "HF_TOKEN",
    "HUGGINGFACE_API_KEY",
    "REPLICATE_API_TOKEN",
    "AZURE_OPENAI_API_KEY",
)
PACKAGES = ("openai", "anthropic", "google.generativeai", "google.genai", "transformers", "torch", "ollama")
BINARIES = ("ollama", "llama-server", "llama-cli", "llama-mtmd-cli", "llava-cli", "lms")
DEFAULT_OLLAMA = "http://127.0.0.1:11434"
DEFAULT_COMFYUI = "127.0.0.1:8188"  # matcha.config.MatchaConfig / CLI default

# API-key providers that have an adapter in this version (none yet).
IMPLEMENTED_KEY_ADAPTERS: dict[str, str] = {}


def _http_json(url: str, payload: Optional[dict] = None, timeout: float = 2.0) -> Any:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST" if data else "GET"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _find_spec(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def discover(
    *,
    ollama_host: Optional[str] = None,
    comfyui: str = DEFAULT_COMFYUI,
    http: Callable[..., Any] = _http_json,
    which: Callable[[str], Optional[str]] = shutil.which,
    environ: Optional[dict] = None,
) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    host = ollama_host or env.get("OLLAMA_HOST") or DEFAULT_OLLAMA
    if not host.startswith("http"):
        host = "http://" + host
    out: dict[str, Any] = {
        "api_key_env_present": {k: bool(env.get(k)) for k in API_KEY_VARS},
        "python_packages": {p: _find_spec(p) for p in PACKAGES},
        "binaries": {b: bool(which(b)) for b in BINARIES},
        "ollama": {"host": host, "reachable": False, "models": [], "vision_models": []},
        "comfyui": {"address": comfyui, "reachable": False,
                    "note": "ComfyUI is Matcha's image-generation backend; there is no classification adapter for it."},
        "missing": [],
    }

    try:
        tags = http(host.rstrip("/") + "/api/tags")
        out["ollama"]["reachable"] = True
        names = [m.get("name") or m.get("model") for m in (tags.get("models") or [])]
        out["ollama"]["models"] = [n for n in names if n]
        for n in out["ollama"]["models"]:
            try:
                info = http(host.rstrip("/") + "/api/show", {"model": n})
            except (urllib.error.URLError, OSError, ValueError):
                continue
            if "vision" in (info.get("capabilities") or []):
                out["ollama"]["vision_models"].append(n)
    except (urllib.error.URLError, OSError, ValueError) as e:
        out["ollama"]["error"] = str(e)

    try:
        http("http://" + comfyui + "/system_stats")
        out["comfyui"]["reachable"] = True
    except (urllib.error.URLError, OSError, ValueError):
        pass

    missing = out["missing"]
    keys = [k for k, v in out["api_key_env_present"].items() if v]
    if not keys:
        missing.append("no cloud vision API key present in the environment")
    for k in keys:
        if k not in IMPLEMENTED_KEY_ADAPTERS:
            missing.append(f"{k} is set but no adapter for it is implemented in impact v1")
    if not out["binaries"]["ollama"]:
        missing.append("ollama binary not on PATH")
    elif not out["ollama"]["reachable"]:
        missing.append(f"ollama server not reachable at {host}")
    elif not out["ollama"]["vision_models"]:
        missing.append("ollama is running but has no model with the 'vision' capability")
    if any(out["binaries"][b] for b in ("llama-server", "llama-cli", "llama-mtmd-cli")):
        missing.append("llama.cpp binaries present but no llama.cpp adapter/multimodal model is configured")
    return out


def select_provider(spec: str, discovery: dict[str, Any]):
    """Return (provider, selection_note) for ``--provider`` *spec*.

    ``auto``: an Ollama vision model if one is available, else unavailable.
    ``ollama`` / ``ollama:<model>``: that adapter if the model has vision.
    ``unavailable``: the explicit no-provider result.
    """
    spec = (spec or "auto").strip()
    missing = list(discovery.get("missing") or [])
    oll = discovery.get("ollama") or {}
    if spec == "unavailable":
        return UnavailableProvider(missing=missing), "explicitly requested"
    if spec == "auto" or spec == "ollama" or spec.startswith("ollama:"):
        model = spec.split(":", 1)[1] if spec.startswith("ollama:") else None
        vision = oll.get("vision_models") or []
        if model is None and vision:
            model = vision[0]
        if model and model in vision:
            return OllamaProvider(model=model, host=oll.get("host", DEFAULT_OLLAMA)), f"ollama vision model {model}"
        why = (
            f"requested ollama model {model!r} is not an available vision model"
            if model
            else "no available vision provider found by discovery"
        )
        return UnavailableProvider(missing=missing + ([why] if model else [])), why
    return UnavailableProvider(missing=missing + [f"unknown provider spec {spec!r}"]), f"unknown provider {spec!r}"
