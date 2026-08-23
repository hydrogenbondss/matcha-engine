"""Preflight validation: fail loudly before queueing anything.

Checks the ComfyUI server is reachable and that the configured checkpoint
and LoRA actually exist server-side (via /object_info). A wrong model name
otherwise surfaces as an opaque HTTP 400 on every pose; a corrupt/partial
model file surfaces even later, as an execution_error mid-run.
"""

import json
import urllib.error
import urllib.request

from matcha.errors import PreflightError
from matcha.vnccs import (
    CLONER_NODES,
    CLOTHES_NODES,
    INSTALL_HINT,
    REQUIRED_VNCCS_NODES,
    REQUIRED_VNCCS_UTILS_NODES,
    VNCCSStatus,
)

# A real SD checkpoint is gigabytes; anything under this is a failed
# download (LFS pointer, HTML error page) that will fail to deserialize.
MIN_CHECKPOINT_BYTES = 100 * 1024 * 1024


def _object_info(server_address: str, node: str) -> dict:
    url = f"http://{server_address}/object_info/{node}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise PreflightError(
            f"Cannot reach ComfyUI at {server_address}: {e}. "
            "Is the server running? Health-check first:\n"
            f"  curl -s -o /dev/null -w '%{{http_code}}\\n' "
            f"http://{server_address}/\n"
            "(expect 200 — connection refused means ComfyUI is not up)"
        ) from e
    except (urllib.error.URLError, OSError) as e:
        raise PreflightError(
            f"Cannot reach ComfyUI at {server_address}: {e}. "
            "Is the server running? Health-check first:\n"
            f"  curl -s -o /dev/null -w '%{{http_code}}\\n' "
            f"http://{server_address}/\n"
            "(expect 200 — connection refused means ComfyUI is not up)"
        ) from e


def node_registered(server_address: str, node: str) -> bool:
    """True if ``/object_info/{node}`` lists that class_type."""
    info = _object_info(server_address, node)
    return bool(info.get(node))


def _available(info: dict, node: str, field: str) -> list[str]:
    try:
        values = info[node]["input"]["required"][field][0]
    except (KeyError, IndexError, TypeError):
        return []
    return values if isinstance(values, list) else []


def validate_models(
    server_address: str,
    checkpoint: str,
    lora: str | None = None,
    *,
    ip_adapter_file: str | None = None,
    clip_vision: str | None = None,
) -> None:
    """Raise PreflightError unless the server knows both model names."""
    ckpt_info = _object_info(server_address, "CheckpointLoaderSimple")
    checkpoints = _available(ckpt_info, "CheckpointLoaderSimple", "ckpt_name")
    if checkpoint not in checkpoints:
        raise PreflightError(
            f"Checkpoint '{checkpoint}' not found on the ComfyUI server.\n"
            f"Available checkpoints: {', '.join(checkpoints) or '(none)'}\n"
            "Set 'checkpoint:' in your character YAML to one of these, or "
            "install the model into ComfyUI/models/checkpoints/."
        )

    if lora:
        lora_info = _object_info(server_address, "LoraLoader")
        loras = _available(lora_info, "LoraLoader", "lora_name")
        if lora not in loras:
            raise PreflightError(
                f"LoRA '{lora}' not found on the ComfyUI server.\n"
                f"Available LoRAs: {', '.join(loras) or '(none)'}\n"
                "Set 'lora:' in your character YAML to one of these, set it "
                "to null to skip the LoRA, or install the file into "
                "ComfyUI/models/loras/."
            )

    if ip_adapter_file:
        try:
            ipa_info = _object_info(server_address, "IPAdapterModelLoader")
        except PreflightError as e:
            raise PreflightError(
                f"IP-Adapter requested but ComfyUI has no IPAdapterModelLoader "
                f"node (is ComfyUI_IPAdapter_plus installed?): {e}"
            ) from e
        files = _available(ipa_info, "IPAdapterModelLoader", "ipadapter_file")
        if ip_adapter_file not in files:
            raise PreflightError(
                f"IP-Adapter '{ip_adapter_file}' not found on the ComfyUI "
                f"server.\nAvailable: {', '.join(files) or '(none)'}\n"
                "Install into ComfyUI/models/ipadapter/."
            )

    if clip_vision:
        try:
            cv_info = _object_info(server_address, "CLIPVisionLoader")
        except PreflightError as e:
            raise PreflightError(
                f"CLIP vision requested but CLIPVisionLoader is unavailable: {e}"
            ) from e
        files = _available(cv_info, "CLIPVisionLoader", "clip_name")
        if clip_vision not in files:
            raise PreflightError(
                f"CLIP vision '{clip_vision}' not found on the ComfyUI server.\n"
                f"Available: {', '.join(files) or '(none)'}\n"
                "Download CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors into "
                "ComfyUI/models/clip_vision/ (see ComfyUI_IPAdapter_plus README)."
            )


def validate_vnccs(
    server_address: str,
    *,
    require_cloner: bool = False,
) -> VNCCSStatus:
    """Raise PreflightError unless VNCCS + Utils nodes are on the server.

    Does not fall back to prompt+seed. Missing nodes get the install hint.
    Clothes / cloner are optional extras reported on the status object.
    """
    missing_required: list[str] = []
    for node in REQUIRED_VNCCS_NODES + REQUIRED_VNCCS_UTILS_NODES:
        if not node_registered(server_address, node):
            missing_required.append(node)

    missing_optional: list[str] = []
    clothes_ok = True
    for node in CLOTHES_NODES:
        if not node_registered(server_address, node):
            clothes_ok = False
            missing_optional.append(node)
    cloner_ok = True
    for node in CLONER_NODES:
        if not node_registered(server_address, node):
            cloner_ok = False
            missing_optional.append(node)

    if missing_required:
        listed = ", ".join(missing_required)
        raise PreflightError(
            f"VNCCS backend requested but these nodes are missing: {listed}.\n"
            + INSTALL_HINT
        )
    if require_cloner and not cloner_ok:
        listed = ", ".join(n for n in CLONER_NODES if n in missing_optional)
        raise PreflightError(
            f"--vnccs-ref needs Character Cloner nodes: {listed}.\n"
            + INSTALL_HINT
        )
    return VNCCSStatus(
        required_ok=True,
        missing_required=[],
        clothes_ok=clothes_ok,
        cloner_ok=cloner_ok,
        missing_optional=missing_optional,
    )


def validate_model_file(path_bytes: int, name: str) -> None:
    """Raise PreflightError for a model file too small to be real.

    Callers pass the on-disk size when they have filesystem access to the
    ComfyUI models directory (local setups). Catches the classic failure:
    a 26-byte Git-LFS pointer or HTML error page saved as a .safetensors.
    """
    if path_bytes < MIN_CHECKPOINT_BYTES:
        raise PreflightError(
            f"Model file '{name}' is only {path_bytes} bytes — that is a "
            "failed/partial download (e.g. a Git-LFS pointer or an error "
            "page), not a model. Re-download it before generating."
        )
