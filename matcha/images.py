"""Post-generation image sanity checks.

Catches Mac MPS failure modes that still return a valid PNG:

* solid black (NaN / fp16 VAE)
* smear + a high-frequency static band along an edge (the 2026-08
  Anything V5 / MPS pattern that slipped a global-threshold guard)

Rejected frames are meant to be persisted by the CLI (PNG + metrics JSON)
so a long run stays inspectable after the process exits.
"""

from __future__ import annotations

import io
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from PIL import Image, ImageStat

from matcha.errors import GenerationError

_BLACK_LUMA = 12  # mean / max channel threshold for "solid black"

# Sample size for neighbor/edge stats. 128 is enough to see a 20% static
# stripe without spending seconds on a 512×512 decode path.
_SAMPLE = 128

# Right/left strip width as a fraction of the (sampled) frame.
_STRIP_FRAC = 0.22

# A pixel pair counts as "high frequency" when its luma jump is this large.
_HIGH_FREQ_DELTA = 40

# Static-band: an edge strip that is both noisy and much noisier than the
# interior. Tuned so smear+static fixtures fail and a cel-like drawing
# (sharp outlines, flat fills, clean margins) passes.
_STATIC_STRIP_ADJ = 18.0
_STATIC_RATIO = 1.55
_STATIC_HIGH_FREQ = 0.10
_STATIC_STRIP_EDGE = 55.0

# Smear: interior has color variation but almost no structure. Solid-color
# cards (stddev ≈ 0) are not smears — they fail the black check or pass.
_SMEAR_INTERIOR_EDGE = 16.0
_SMEAR_INTERIOR_ADJ = 14.0
_SMEAR_LUMA_STD = 12.0


class ImageQualityError(GenerationError):
    """Raised when a decoded PNG fails a quality guard.

    Carries the raw bytes and the metrics dict so the CLI can dump both
    under ``output_dir/rejected/`` before retrying or moving on.
    """

    def __init__(
        self,
        message: str,
        *,
        metrics: Optional[dict[str, Any]] = None,
        data: bytes = b"",
    ):
        self.metrics = metrics or {}
        self.data = data
        super().__init__(message)


@dataclass
class ImageMetrics:
    width: int
    height: int
    mean_luma: float
    max_channel: float
    luma_std: float
    adj_luma_delta: float
    edge: float
    interior_adj: float
    interior_edge: float
    left_adj: float
    right_adj: float
    left_edge: float
    right_edge: float
    left_high_freq: float
    right_high_freq: float
    static_band_ratio: float
    verdict: str = "ok"
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _luma_bytes(im: Image.Image) -> tuple[list[int], int, int]:
    gray = im.convert("L")
    w, h = gray.size
    return list(gray.getdata()), w, h


def _region_stats(
    pixels: list[int],
    w: int,
    h: int,
    x0: int,
    x1: int,
) -> tuple[float, float, float]:
    """Return (mean adjacent-luma Δ, mean Sobel-ish edge, high-freq fraction).

    Adjacent Δ averages absolute horizontal + vertical neighbor differences.
    Edge is a 3-tap horizontal+vertical gradient (cheap Sobel stand-in).
    High-freq is the fraction of horizontal pairs with |Δ| >= _HIGH_FREQ_DELTA.
    """
    x0 = max(0, min(x0, w))
    x1 = max(x0 + 1, min(x1, w))
    adj_sum = 0.0
    adj_n = 0
    edge_sum = 0.0
    edge_n = 0
    hf = 0
    hf_n = 0

    for y in range(h):
        row = y * w
        for x in range(x0, x1 - 1):
            d = abs(pixels[row + x] - pixels[row + x + 1])
            adj_sum += d
            adj_n += 1
            hf_n += 1
            if d >= _HIGH_FREQ_DELTA:
                hf += 1
        if y + 1 < h:
            below = (y + 1) * w
            for x in range(x0, x1):
                adj_sum += abs(pixels[row + x] - pixels[below + x])
                adj_n += 1

    # Interior of the strip so the 3-tap kernel stays in-bounds.
    for y in range(1, h - 1):
        row = y * w
        for x in range(max(x0, 1), min(x1, w - 1)):
            gx = pixels[row + x + 1] - pixels[row + x - 1]
            gy = pixels[(y + 1) * w + x] - pixels[(y - 1) * w + x]
            edge_sum += abs(gx) + abs(gy)
            edge_n += 1

    adj = adj_sum / adj_n if adj_n else 0.0
    edge = edge_sum / edge_n if edge_n else 0.0
    high_freq = (hf / hf_n) if hf_n else 0.0
    return adj, edge, high_freq


def measure_image(data: bytes) -> tuple[Image.Image, ImageMetrics]:
    """Decode PNG bytes and compute quality metrics. Does not reject."""
    if not data:
        raise ImageQualityError("empty image bytes", metrics={}, data=data)

    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        rgb = im.convert("RGB")
    except Exception as e:
        raise ImageQualityError(
            f"cannot decode PNG ({e}) — got {len(data)} bytes",
            metrics={},
            data=data,
        ) from e

    w0, h0 = rgb.size
    sample = rgb.resize((_SAMPLE, _SAMPLE), Image.Resampling.BILINEAR) if max(
        rgb.size
    ) > _SAMPLE else rgb
    pixels, w, h = _luma_bytes(sample)

    strip = max(4, int(round(w * _STRIP_FRAC)))
    left_x1 = strip
    right_x0 = w - strip

    left_adj, left_edge, left_hf = _region_stats(pixels, w, h, 0, left_x1)
    right_adj, right_edge, right_hf = _region_stats(pixels, w, h, right_x0, w)
    interior_adj, interior_edge, _ = _region_stats(pixels, w, h, left_x1, right_x0)
    glob_adj, glob_edge, _ = _region_stats(pixels, w, h, 0, w)

    stat = ImageStat.Stat(sample)
    mean_luma = sum(stat.mean) / max(len(stat.mean), 1)
    max_channel = max(hi for _, hi in stat.extrema)
    # RMS of the luma plane as a cheap stddev.
    luma_im = sample.convert("L")
    luma_stat = ImageStat.Stat(luma_im)
    luma_std = float(luma_stat.stddev[0]) if luma_stat.stddev else 0.0

    edge_strip_adj = max(left_adj, right_adj)
    static_ratio = edge_strip_adj / max(interior_adj, 1.0)

    metrics = ImageMetrics(
        width=w0,
        height=h0,
        mean_luma=round(mean_luma, 3),
        max_channel=float(max_channel),
        luma_std=round(luma_std, 3),
        adj_luma_delta=round(glob_adj, 3),
        edge=round(glob_edge, 3),
        interior_adj=round(interior_adj, 3),
        interior_edge=round(interior_edge, 3),
        left_adj=round(left_adj, 3),
        right_adj=round(right_adj, 3),
        left_edge=round(left_edge, 3),
        right_edge=round(right_edge, 3),
        left_high_freq=round(left_hf, 4),
        right_high_freq=round(right_hf, 4),
        static_band_ratio=round(static_ratio, 3),
    )
    return rgb, metrics


def evaluate_image(data: bytes, *, label: str = "image") -> ImageMetrics:
    """Measure and stamp a verdict. Raises ImageQualityError on failure."""
    rgb, metrics = measure_image(data)
    reasons: list[str] = []

    if metrics.mean_luma <= _BLACK_LUMA and metrics.max_channel <= _BLACK_LUMA:
        reasons.append(
            f"nearly solid black (mean luma {metrics.mean_luma:.1f}) — "
            "likely a NaN/VAE failure. On Mac MPS avoid --force-fp16; "
            "start ComfyUI with --fp32-vae --cpu-vae; retry with "
            "--lora none (base checkpoint)"
        )

    edge_strip_adj = max(metrics.left_adj, metrics.right_adj)
    edge_strip_edge = max(metrics.left_edge, metrics.right_edge)
    edge_hf = max(metrics.left_high_freq, metrics.right_high_freq)
    static_like = (
        edge_strip_adj >= _STATIC_STRIP_ADJ
        and metrics.static_band_ratio >= _STATIC_RATIO
        and (
            edge_hf >= _STATIC_HIGH_FREQ
            or edge_strip_edge >= _STATIC_STRIP_EDGE
        )
    )
    if static_like:
        side = "right" if metrics.right_adj >= metrics.left_adj else "left"
        reasons.append(
            f"static-band along the {side} edge "
            f"(strip adj {edge_strip_adj:.1f} vs interior "
            f"{metrics.interior_adj:.1f}, ratio {metrics.static_band_ratio:.2f}, "
            f"high-freq {edge_hf:.2f})"
        )

    smear_like = (
        metrics.interior_edge < _SMEAR_INTERIOR_EDGE
        and metrics.interior_adj < _SMEAR_INTERIOR_ADJ
        and metrics.luma_std >= _SMEAR_LUMA_STD
        and not static_like  # static-band reason is enough; avoid double-talk
    )
    if smear_like:
        reasons.append(
            f"smear / no structure in the interior "
            f"(interior edge {metrics.interior_edge:.1f}, "
            f"adj {metrics.interior_adj:.1f}, luma std {metrics.luma_std:.1f})"
        )

    if reasons:
        metrics.verdict = "reject"
        metrics.reasons = reasons
        detail = "; ".join(reasons)
        raise ImageQualityError(
            f"{label}: {detail}",
            metrics=metrics.to_dict(),
            data=data,
        )

    metrics.verdict = "ok"
    metrics.reasons = []
    # Keep a reference so callers can ignore the unused rgb if they want.
    _ = rgb
    return metrics


def assert_usable_image(data: bytes, *, label: str = "image") -> ImageMetrics:
    """Raise ImageQualityError if *data* is empty, undecodable, or unusable."""
    return evaluate_image(data, label=label)


def persist_rejection(
    data: bytes,
    metrics: dict[str, Any],
    dest_png: Path,
    *,
    extra: Optional[dict[str, Any]] = None,
) -> Path:
    """Write a rejected PNG and a sidecar JSON of the metrics used."""
    dest_png = Path(dest_png)
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    if data:
        dest_png.write_bytes(data)
    payload = {
        "rejected_at": datetime.now(timezone.utc).isoformat(),
        "png": dest_png.name,
        "metrics": metrics,
    }
    if extra:
        payload.update(extra)
    dest_json = dest_png.with_suffix(".json")
    dest_json.write_text(json.dumps(payload, indent=2) + "\n")
    return dest_json


def knockout_near_black(
    data: bytes,
    *,
    threshold: int = 18,
) -> bytes:
    """Best-effort: turn near-black RGB pixels into transparent alpha.

    This is a luma-threshold knockout, not a subject matte. Grey/white
    studio cards are left opaque on purpose — a rembg-class model is
    out of scope (new GPU/MPS stack, would break the mocked test suite).
    """
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    pixels = list(im.getdata())
    out = []
    for r, g, b, a in pixels:
        if r <= threshold and g <= threshold and b <= threshold:
            out.append((r, g, b, 0))
        else:
            out.append((r, g, b, a))
    im.putdata(out)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def pad_to_canvas(data: bytes, width: int, height: int) -> bytes:
    """Center the sprite on a larger transparent canvas. Never shrinks."""
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    w, h = im.size
    if width < w or height < h:
        raise GenerationError(
            f"canvas {width}×{height} is smaller than the sprite {w}×{h}; "
            "canvas only pads, it does not downscale generation"
        )
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.paste(im, ((width - w) // 2, (height - h) // 2), im)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


def parse_canvas(spec: str) -> tuple[int, int]:
    """Parse a ``WIDTHxHEIGHT`` canvas spec."""
    raw = spec.lower().replace(" ", "")
    if "x" not in raw:
        raise ValueError(f"canvas must look like 768x1024, got {spec!r}")
    w_s, h_s = raw.split("x", 1)
    w, h = int(w_s), int(h_s)
    if w < 1 or h < 1:
        raise ValueError(f"canvas dimensions must be positive, got {spec!r}")
    return w, h
