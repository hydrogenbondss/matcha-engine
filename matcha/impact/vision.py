"""Vision provider interface, strict response validation, and adapters.

A provider judges one candidate image against one change request, optionally
with a reference image of the current canonical design.  Providers return a
*raw* response.  :func:`validate_response` turns that response into a
:class:`Classification` and is the only way a provider verdict enters the
report.

Two things are recorded separately for every asset:

* the **asset status** (protocol enum, exactly ``ASSET_ACTION`` /
  ``UNAFFECTED`` / ``REVIEW_REQUIRED``), and
* the **provider execution state** (``AVAILABLE`` / ``UNAVAILABLE`` /
  ``ERROR`` / ``INVALID_OUTPUT``), plus a machine-readable ``review_cause``
  whenever the status is ``REVIEW_REQUIRED``.

Confidence is recorded as metadata only.  It never changes a verdict: a
valid determinate verdict stays determinate at any confidence, and a valid
``REVIEW_REQUIRED`` stays ``REVIEW_REQUIRED`` (protocol: REVIEW_REQUIRED
never means "low confidence").  There is no confidence threshold.

When no provider can run, no verdict is fabricated.  The asset gets
``REVIEW_REQUIRED`` with provider state ``UNAVAILABLE`` and cause
``PROVIDER_UNAVAILABLE``.  It never goes through :func:`validate_response`,
and ``valid_provider_output`` is false.

Blinding of the visual step: the provider receives only the change request,
the reference image bytes (if supplied), the candidate image bytes, and an
opaque candidate id (``candidate-NN``).  It never receives a file name, a
path, or any other asset metadata.  The engine maps the id back to the asset
outside the provider.

Nothing here inspects pixels heuristically.
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

PROVIDER_UNAVAILABLE = "provider unavailable"

# Provider execution state, per asset. Independent of the asset status.
PROVIDER_STATES = ("AVAILABLE", "UNAVAILABLE", "ERROR", "INVALID_OUTPUT")

# Why an asset is REVIEW_REQUIRED (None when the status is determinate).
REVIEW_CAUSES = (
    "SEMANTIC_REVIEW_REQUIRED",  # a valid provider verdict of REVIEW_REQUIRED
    "PROVIDER_UNAVAILABLE",  # no provider could run; nothing was classified
    "PROVIDER_ERROR",  # the provider raised or the transport failed
    "INVALID_PROVIDER_OUTPUT",  # malformed or out-of-enum provider output
)


@dataclass(frozen=True)
class ImageInput:
    """Image handed to a provider: opaque id plus bytes, no path or name."""

    id: str
    data: bytes
    media_type: str = "image/png"

    def __repr__(self) -> str:  # never expose bytes in logs
        return f"ImageInput(id={self.id!r}, bytes={len(self.data)}, media_type={self.media_type!r})"


@dataclass
class Classification:
    status: str  # ASSET_ACTION | UNAFFECTED | REVIEW_REQUIRED
    provider_state: str  # AVAILABLE | UNAVAILABLE | ERROR | INVALID_OUTPUT
    reason: str
    review_cause: Optional[str] = None
    confidence: Optional[float] = None  # None when no valid provider verdict exists
    locator: Optional[str] = None
    provider_status: Optional[str] = None  # what a valid provider output claimed
    raw: Any = None

    def __post_init__(self) -> None:
        if self.status not in ASSET_STATUSES:
            raise ValueError(f"asset status {self.status!r} not allowed")
        if self.provider_state not in PROVIDER_STATES:
            raise ValueError(f"provider state {self.provider_state!r} not allowed")
        if self.status == "REVIEW_REQUIRED":
            if self.review_cause not in REVIEW_CAUSES:
                raise ValueError("REVIEW_REQUIRED needs a review_cause")
        elif self.review_cause is not None:
            raise ValueError("a determinate status has no review_cause")
        if self.provider_state != "AVAILABLE" and self.status != "REVIEW_REQUIRED":
            raise ValueError("only an AVAILABLE provider can yield a determinate status")

    @property
    def valid_provider_output(self) -> bool:
        """True only when a provider ran and its output passed validation."""
        return self.provider_state == "AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "provider_state": self.provider_state,
            "review_cause": self.review_cause,
            "valid_provider_output": self.valid_provider_output,
            "provider_status": self.provider_status,
            "confidence": self.confidence,
            "reason": self.reason,
            "locator": self.locator,
        }


def unavailable_classification(detail: str = PROVIDER_UNAVAILABLE) -> Classification:
    return Classification(
        status="REVIEW_REQUIRED",
        provider_state="UNAVAILABLE",
        review_cause="PROVIDER_UNAVAILABLE",
        reason=PROVIDER_UNAVAILABLE if detail == PROVIDER_UNAVAILABLE else f"{PROVIDER_UNAVAILABLE}: {detail}",
    )


def _error(reason: str, raw: Any = None) -> Classification:
    return Classification(
        status="REVIEW_REQUIRED",
        provider_state="ERROR",
        review_cause="PROVIDER_ERROR",
        reason=reason,
        raw=raw,
    )


def _invalid(reason: str, raw: Any = None) -> Classification:
    return Classification(
        status="REVIEW_REQUIRED",
        provider_state="INVALID_OUTPUT",
        review_cause="INVALID_PROVIDER_OUTPUT",
        reason=reason,
        raw=raw,
    )


class VisionProvider(Protocol):
    name: str
    model: Optional[str]

    def available(self) -> tuple[bool, str]: ...

    def classify(
        self,
        request: str,
        reference_image: Optional[ImageInput],
        candidate_image: ImageInput,
        context: dict[str, Any],
    ) -> Any: ...


class ProviderUnavailableError(RuntimeError):
    """Raised by a provider that cannot classify anything."""


def validate_response(raw: Any) -> Classification:
    """Strictly validate the output of a provider that actually ran.

    Accepted shape (JSON object or JSON text)::

        {"status": "ASSET_ACTION"|"UNAFFECTED"|"REVIEW_REQUIRED",
         "confidence": <number in [0, 1]>,
         "reason": <non-empty string>,
         "locator": <optional string>}

    Unknown extra keys are rejected, so a drifting model format gets noticed.
    Invalid output gives provider state ``INVALID_OUTPUT``.  Valid output
    gives ``AVAILABLE`` and the provider's verdict unchanged; ``confidence``
    is kept as metadata and never alters the verdict.
    """
    data = raw
    if isinstance(raw, (bytes, bytearray)):
        try:
            data = raw.decode("utf-8")
        except UnicodeDecodeError:
            return _invalid("malformed provider output: not UTF-8", raw)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, ValueError) as e:
            return _invalid(f"malformed provider output: not JSON ({getattr(e, 'msg', e)})", raw)
    if not isinstance(data, dict):
        return _invalid("malformed provider output: expected a JSON object", raw)

    allowed = {"status", "confidence", "reason", "locator"}
    extra = sorted(set(data) - allowed)
    if extra:
        return _invalid(f"malformed provider output: unexpected keys {extra}", raw)
    missing = sorted({"status", "confidence", "reason"} - set(data))
    if missing:
        return _invalid(f"malformed provider output: missing keys {missing}", raw)

    status = data["status"]
    if not isinstance(status, str) or status not in ASSET_STATUSES:
        return _invalid(f"provider status out of enum: {status!r}", raw)

    conf = data["confidence"]
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        return _invalid(f"malformed provider output: confidence is not a number ({conf!r})", raw)
    conf = float(conf)
    if math.isnan(conf) or conf < 0.0 or conf > 1.0:
        return _invalid(f"malformed provider output: confidence {conf} outside [0, 1]", raw)

    reason = data["reason"]
    if not isinstance(reason, str) or not reason.strip():
        return _invalid("malformed provider output: reason must be a non-empty string", raw)

    locator = data.get("locator")
    if locator is not None and not isinstance(locator, str):
        return _invalid("malformed provider output: locator must be a string", raw)

    if status == "REVIEW_REQUIRED":
        return Classification(
            status="REVIEW_REQUIRED",
            provider_state="AVAILABLE",
            review_cause="SEMANTIC_REVIEW_REQUIRED",
            confidence=conf,
            reason=reason.strip(),
            locator=locator,
            provider_status=status,
            raw=raw,
        )
    return Classification(
        status=status,
        provider_state="AVAILABLE",
        confidence=conf,
        reason=reason.strip(),
        locator=locator,
        provider_status=status,
        raw=raw,
    )


# --------------------------------------------------------------------------
# Prompt: the change request plus neutral definitions of the three verdicts.
# No candidate path, file name, id or other metadata is ever included.
# --------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are auditing existing static production art for a game.

A canonical design change has been requested:
"{request}"

{reference_note}The LAST image is the candidate production asset.

Decide whether the requested change alters what the CANDIDATE image visibly depicts.
- ASSET_ACTION: the candidate visibly depicts the feature being changed, so its depicted content changes.
- UNAFFECTED: the candidate visibly does not depict the feature being changed, so its depicted content does not change.
- REVIEW_REQUIRED: the image does not let you determine whether the feature being changed is depicted.
Judge only from the pixels.

Reply with ONLY a JSON object:
{{"status": "ASSET_ACTION" | "UNAFFECTED" | "REVIEW_REQUIRED",
  "confidence": <number 0..1>,
  "reason": "<one or two sentences naming what is or is not visible>",
  "locator": "<optional: where in the image the relevant region is>"}}
"""


def build_prompt(request: str, has_reference: bool) -> str:
    ref = (
        "The FIRST image is the reference showing the current canonical design.\n"
        if has_reference
        else ""
    )
    return PROMPT_TEMPLATE.format(request=request, reference_note=ref)


def load_image_input(path: Path, image_id: str) -> ImageInput:
    """Read image bytes for a provider; only the opaque *image_id* travels with them."""
    p = Path(path)
    suffix = p.suffix.lower()
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
        suffix, "application/octet-stream"
    )
    return ImageInput(id=image_id, data=p.read_bytes(), media_type=media)


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------


@dataclass
class UnavailableProvider:
    """Explicit no-provider result. It never fakes a visual judgement.

    ``classify`` raises :class:`ProviderUnavailableError`.  The engine never
    calls it, and :func:`classify_asset` maps it to provider state
    ``UNAVAILABLE`` without calling :func:`validate_response`.
    """

    missing: list[str] = field(default_factory=list)
    name: str = "unavailable"
    model: Optional[str] = None

    def available(self) -> tuple[bool, str]:
        return False, PROVIDER_UNAVAILABLE

    def classify(self, request, reference_image, candidate_image, context) -> Any:
        raise ProviderUnavailableError(PROVIDER_UNAVAILABLE)


@dataclass
class OllamaProvider:
    """Local Ollama server with a vision-capable model (``/api/chat``).

    Used only when discovery confirms the server is reachable and the model
    reports the ``vision`` capability.  Images go to the local server only,
    as bytes with no file name.  NOTE: never exercised against a live server
    in v1; tests mock the HTTP layer.
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
            images.append(base64.b64encode(reference_image.data).decode("ascii"))
        images.append(base64.b64encode(candidate_image.data).decode("ascii"))
        prompt = build_prompt(request, reference_image is not None)
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
    reference_image: Optional[ImageInput],
    candidate_image: ImageInput,
    context: dict[str, Any],
) -> Classification:
    if isinstance(provider, UnavailableProvider):
        return unavailable_classification()
    try:
        raw = provider.classify(request, reference_image, candidate_image, context)
    except ProviderUnavailableError as e:
        return unavailable_classification(str(e))
    except Exception as e:  # provider bugs must not crash the run
        return _error(f"provider error: {type(e).__name__}: {e}")
    if isinstance(raw, dict) and "__transport_error__" in raw:
        return _error(f"provider transport error: {raw['__transport_error__']}", raw)
    return validate_response(raw)
