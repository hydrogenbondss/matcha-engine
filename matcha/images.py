"""Post-generation image sanity checks."""

from __future__ import annotations

import io

from PIL import Image

from matcha.errors import GenerationError

_BLACK_LUMA = 12  # mean / max channel threshold for "solid black"


def assert_usable_image(data: bytes, *, label: str = "image") -> None:
    """Raise GenerationError if *data* is empty, undecodable, or nearly black.

    Catches the Mac MPS / fp16-VAE failure mode where ComfyUI still returns a
    valid PNG that is entirely black (NaN cast to 0).
    """
    if not data:
        raise GenerationError(f"{label}: empty image bytes")

    try:
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.load()
    except Exception as e:
        raise GenerationError(
            f"{label}: cannot decode PNG ({e}) — got {len(data)} bytes"
        ) from e

    # Downsample for speed; ImageStat avoids deprecated getdata().
    from PIL import ImageStat

    sample = im.resize((64, 64)) if max(im.size) > 64 else im
    stat = ImageStat.Stat(sample)
    # Nearly solid black: very low mean and no bright pixels.
    mean_luma = sum(stat.mean) / max(len(stat.mean), 1)
    max_channel = max(hi for _, hi in stat.extrema)
    if mean_luma <= _BLACK_LUMA and max_channel <= _BLACK_LUMA:
        raise GenerationError(
            f"{label}: image is nearly solid black "
            f"(mean luma {mean_luma:.1f}) — likely a NaN/VAE failure. "
            f"On Mac MPS avoid --force-fp16; start ComfyUI with "
            f"--fp32-vae --cpu-vae; retry with --lora none (base checkpoint), "
            f"then try a different LoRA if needed."
        )
