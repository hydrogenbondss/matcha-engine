"""Guided first-run checklist (`matcha setup`).

Checks and guidance only — no downloads, no installs, no bundled weights.
Walks a new user through the three things that actually break a first run:
ComfyUI reachability, server-side model presence, and the exact
trusted-first-success sequence to run next.
"""

from __future__ import annotations

import urllib.error
import urllib.request

import typer

from matcha import preflight
from matcha.config import CharacterConfig

START_COMMAND_HINT = """\
ComfyUI is not reachable. Start it first (Mac MPS flags — see README):

  export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
  cd ~/ComfyUI && ./venv/bin/python main.py \\
    --listen 127.0.0.1 --port 8188 \\
    --fp32-vae --cpu-vae --lowvram --use-split-cross-attention

On CUDA/Linux the flags differ — follow ComfyUI's own docs, then re-run
`matcha setup`."""

MODEL_PLACEMENT_TABLE = """\
Model placement (files go in ComfyUI's models tree, then restart ComfyUI):

  Kind        Folder                          Rule
  ----------  ------------------------------  ---------------------------------
  Checkpoint  ComfyUI/models/checkpoints/     Filename must match the YAML
                                              `checkpoint:` value exactly.
  LoRA        ComfyUI/models/loras/           Base family must match the
                                              checkpoint (an SD1.5 LoRA on an
                                              SDXL checkpoint fails or
                                              silently degrades output).

See docs/verified-models.md for the verified checklist (filenames, base
families, commercial-use status, known issues). Not legal advice."""

NEXT_STEPS_TEMPLATE = """\
Next — trusted first success (health-check → dry-run → --lora none → sample-vn):

  # 0. Server up? Expect 200
  curl -s -o /dev/null -w "%{{http_code}}\\n" http://{addr}/

  # 1. Validate config + models (no GPU work)
  .venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \\
    --dry-run

  # 2. Generate with LoRA off + deploy into the sample project
  .venv/bin/matcha character examples/sample-vn/configs/example_character.yaml \\
    --lora none --deploy --project examples/sample-vn --layered

  # 3. Open in the Ren'Py SDK: <your-renpy-sdk>/renpy.sh examples/sample-vn"""


def is_server_reachable(server_address: str, timeout: float = 5.0) -> bool:
    """True if ComfyUI answers HTTP at all (any status code counts)."""
    url = f"http://{server_address}/"
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, OSError):
        return False


def list_server_models(server_address: str) -> tuple[list[str], list[str]]:
    """(checkpoints, loras) the server actually has, via /object_info."""
    ckpt_info = preflight._object_info(server_address, "CheckpointLoaderSimple")
    checkpoints = preflight._available(ckpt_info, "CheckpointLoaderSimple", "ckpt_name")
    lora_info = preflight._object_info(server_address, "LoraLoader")
    loras = preflight._available(lora_info, "LoraLoader", "lora_name")
    return checkpoints, loras


def run_setup(server_address: str, checkpoint: str | None = None) -> int:
    """Print the checklist. Exit 0 = ready to generate; 1 = action needed."""
    wanted = checkpoint or CharacterConfig.model_fields["checkpoint"].default
    typer.echo(f"Matcha setup checklist (ComfyUI at {server_address})\n")

    if not is_server_reachable(server_address):
        typer.echo("[1/3] ComfyUI reachability ... DOWN\n")
        typer.echo(START_COMMAND_HINT)
        typer.echo("")
        typer.echo(NEXT_STEPS_TEMPLATE.format(addr=server_address))
        return 1
    typer.echo("[1/3] ComfyUI reachability ... OK")

    checkpoints, loras = list_server_models(server_address)
    typer.echo("\n[2/3] Models on the server:")
    typer.echo(f"  Checkpoints ({len(checkpoints)}):")
    for name in checkpoints:
        typer.echo(f"    - {name}")
    typer.echo(f"  LoRAs ({len(loras)}):")
    for name in loras:
        typer.echo(f"    - {name}")

    missing = False
    if wanted in checkpoints:
        typer.echo(f"\n  Sample YAML checkpoint '{wanted}' ... PRESENT")
    else:
        missing = True
        typer.echo(f"\n  Sample YAML checkpoint '{wanted}' ... MISSING")
        typer.echo("")
        typer.echo(MODEL_PLACEMENT_TABLE)

    typer.echo("\n[3/3] What to run next:\n")
    typer.echo(NEXT_STEPS_TEMPLATE.format(addr=server_address))
    return 1 if missing else 0
