"""Vision provider interface, strict response validation, and adapters.

A provider judges one candidate image against one change request (optionally
with a reference image of the current canonical design).  Providers return a
*raw* response; :func:`validate_response` turns it into a
:class:`Classification` and is the only way a provider verdict enters the
report.  Anything malformed, out of enum, or below the confidence threshold
becomes ``REVIEW_REQUIRED`` with the reason recorded.

Nothing here inspects pixels heuristically.  When no real provider is
available, :class:`UnavailableProvider` returns an explicit
"provider unavailable" verdict for every asset.
"""

from __future__ import annotations

import base64
import json
import math
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

from matcha.impact.model import ASSET_STATUSES

DEFAULT_CONFIDENCE_THRESHOLD = 0.7
PROVIDER_UNAVAILABLE = "provider unavailable"


@dataclass
class Classification:
    status: str
    confidence: float
    reason: str
    locator: Optional[str] = None
    valid: bool = True  # False when validation replaced the provider verdict
    provider_status: Optional[str] = None  # what the provider claimed, if parseable
    raw: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "confidence": self.confidence,
            "reason": self.reason,
            "locator": self.locator,
            "valid_provider_output": self.valid,
            "provider_status": self.provider_status,
        }


class VisionProvider(Protocol):
    name: str
    model: Optional[str]

    def available(self) -> tuple[bool, str]: ...

    def classify(
        self,
        request: str,
        reference_image: Optional[Path],
        candidate_image: Path,
        context: dict[str, Any],
    ) -> Any: ...


def _review(reason: str, raw: Any = None, provider_status: Optional[str] = None) -> Classification:
    return Classification(
        status="REVIEW_REQUIRED",
        confidence=0.0,
        reason=reason,
        valid=False,
        provider_status=provider_status,
        raw=raw,
    )


def validate_response(raw: Any, *, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> Classification:
    """Strictly validate a provider response.

    Accepted shape (JSON object or JSON text)::

        {"status": "ASSET_ACTION"|"UNAFFECTED"|"REVIEW_REQUIRED",
         "confidence": <number in [0, 1]>,
         "reason": <non-empty string>,
         "locator": <optional string>}

    Unknown extra keys are rejected so a drifting model format is noticed.
    """
    data = raw
    if isinstance(raw, (bytes, bytearray)):
        try:
            data = raw.decode("utf-8")
        except UnicodeDecodeError:
            return _review("malformed provider output: not UTF-8", raw)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, ValueError) as e:
            return _review(f"malformed provider output: not JSON ({e.msg})", raw)
    if not isinstance(data, dict):
        return _review("malformed provider output: expected a JSON object", raw)

    allowed = {"status", "confidence", "reason", "locator"}
    extra = sorted(set(data) - allowed)
    if extra:
        return _review(f"malformed provider output: unexpected keys {extra}", raw)
    missing = sorted({"status", "confidence", "reason"} - set(data))
    if missing:
        return _review(f"malformed provider output: missing keys {missing}", raw)

    status = data["status"]
    if not isinstance(status, str) or status not in ASSET_STATUSES:
        return _review(f"provider status out of enum: {status!r}", raw)

    conf = data["confidence"]
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        return _review(f"malformed provider output: confidence is not a number ({conf!r})", raw, status)
    conf = float(conf)
    if math.isnan(conf) or conf < 0.0 or conf > 1.0:
        return _review(f"malformed provider output: confidence {conf} outside [0, 1]", raw, status)

    reason = data["reason"]
    if not isinstance(reason, str) or not reason.strip():
        return _review("malformed provider output: reason must be a non-empty string", raw, status)

    locator = data.get("locator")
    if locator is not None and not isinstance(locator, str):
        return _review("malformed provider output: locator must be a string", raw, status)

    if status != "REVIEW_REQUIRED" and conf < threshold:
        return Classification(
            status="REVIEW_REQUIRED",
            confidence=conf,
            reason=(
                f"provider verdict {status} not accepted: confidence {conf:.2f} is below the "
                f"threshold {threshold:.2f}, so the automated evidence is treated as insufficient. "
                f"Provider reason: {reason.strip()}"
            ),
            locator=locator,
            valid=False,
            provider_status=status,
            raw=raw,
        )
    return Classification(
        status=status,
        confidence=conf,
        reason=reason.strip(),
        locator=locator,
        valid=True,
        provider_status=status,
        raw=raw,
    )


# --------------------------------------------------------------------------
# Prompt (generic; describes the protocol status meanings, never an answer)
# --------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are auditing existing static production art for a game.

A canonical design change has been requested:
"{request}"

{reference_note}The LAST image is the candidate production asset `{asset_path}`.

Decide whether the requested change alters what the CANDIDATE image visibly depicts.
- ASSET_ACTION: the candidate visibly depicts the feature being changed, so its content changes.
- UNAFFECTED: the candidate visibly does not depict the feature (e.g. it is not in frame), so its content does not change.
- REVIEW_REQUIRED: the image genuinely does not let you determine whether the feature is depicted.
Judge only from the pixels. Do not guess from the file name.

Reply with ONLY a JSON object:
{{"status": "ASSET_ACTION" | "UNAFFECTED" | "REVIEW_REQUIRED",
  "confidence": <number 0..1>,
  "reason": "<one or two sentences naming what is or is not visible>",
  "locator": "<optional: where in the image, e.g. 'upper third, head'>"}}
"""


def build_prompt(request: str, asset_path: str, has_reference: bool) -> str:
    ref = (
        "The FIRST image is the reference showing the current canonical design.\n"
        if has_reference
        else ""
    )
    return PROMPT_TEMPLATE.format(request=request, asset_path=asset_path, reference_note=ref)


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------


@dataclass
class UnavailableProvider:
    """Explicit no-provider result. Never fakes a visual judgement."""

    missing: list[str] = field(default_factory=list)
    name: str = "unavailable"
    model: Optional[str] = None

    def available(self) -> tuple[bool, str]:
        return False, PROVIDER_UNAVAILABLE

    def classify(self, request, reference_image, candidate_image, context) -> Any:
        return {
            "status": "REVIEW_REQUIRED",
            "confidence": 0.0,
            "reason": PROVIDER_UNAVAILABLE,
        }


@dataclass
class OllamaProvider:
    """Local Ollama server with a vision-capable model (``/api/chat``).

    Only used when discovery confirms the server is reachable and the model
    reports the ``vision`` capability.  Images are sent to the local server
    only.
    """

    model: str
    host: str = "http://127.0.0.1:11434"
    timeout: float = 600.0
    name: str = "ollama"

    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            self.host.rstrip("/") + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def available(self) -> tuple[bool, str]:
        try:
            info = self._post("/api/show", {"model": self.model})
        except (urllib.error.URLError, OSError, ValueError) as e:
            return False, f"ollama not reachable or model missing: {e}"
        caps = info.get("capabilities") or []
        if "vision" not in caps:
            return False, f"ollama model {self.model!r} does not report the vision capability ({caps})"
        return True, "ok"

    def classify(self, request, reference_image, candidate_image, context) -> Any:
        images = []
        if reference_image is not None:
            images.append(base64.b64encode(Path(reference_image).read_bytes()).decode("ascii"))
        images.append(base64.b64encode(Path(candidate_image).read_bytes()).decode("ascii"))
        prompt = build_prompt(request, context.get("asset_path", ""), reference_image is not None)
        try:
            out = self._post(
                "/api/chat",
                {
                    "model": self.model,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                    "messages": [{"role": "user", "content": prompt, "images": images}],
                },
            )
        except (urllib.error.URLError, OSError, ValueError) as e:
            return {"__transport_error__": str(e)}
        return (out.get("message") or {}).get("content", "")


def classify_asset(
    provider: VisionProvider,
    request: str,
    reference_image: Optional[Path],
    candidate_image: Path,
    context: dict[str, Any],
    *,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> Classification:
    try:
        raw = provider.classify(request, reference_image, candidate_image, context)
    except Exception as e:  # provider bugs must not crash the run
        return _review(f"provider error: {type(e).__name__}: {e}")
    if isinstance(raw, dict) and "__transport_error__" in raw:
        return _review(f"provider transport error: {raw['__transport_error__']}", raw)
    return validate_response(raw, threshold=threshold)
