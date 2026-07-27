import json
import random
import uuid
import urllib.parse
import urllib.request
from typing import Optional

import websocket

from matcha.errors import GenerationError


class ComfyUIGenerator:
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt: dict) -> dict:
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        return json.loads(urllib.request.urlopen(req).read())

    def upload_image(self, data: bytes, filename: str = "matcha_ref.png") -> str:
        """Upload PNG bytes to ComfyUI's input folder; return the server filename."""
        boundary = f"----MatchaBoundary{uuid.uuid4().hex}"
        parts = []
        parts.append(f"--{boundary}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="image"; filename="{filename}"'.encode()
        )
        parts.append(b"Content-Type: image/png")
        parts.append(b"")
        parts.append(data)
        parts.append(f"--{boundary}".encode())
        parts.append(b'Content-Disposition: form-data; name="type"')
        parts.append(b"")
        parts.append(b"input")
        parts.append(f"--{boundary}".encode())
        parts.append(b'Content-Disposition: form-data; name="overwrite"')
        parts.append(b"")
        parts.append(b"true")
        parts.append(f"--{boundary}--".encode())
        parts.append(b"")
        body = b"\r\n".join(parts)
        req = urllib.request.Request(
            f"http://{self.server_address}/upload/image",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            resp = json.loads(urllib.request.urlopen(req).read())
        except Exception as e:
            raise GenerationError(f"Failed to upload reference image: {e}") from e
        name = resp.get("name")
        if not name:
            raise GenerationError(f"Upload succeeded but returned no name: {resp}")
        return name

    def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            f"http://{self.server_address}/view?{url_values}"
        ) as response:
            return response.read()

    def get_history(self, prompt_id: str) -> dict:
        with urllib.request.urlopen(
            f"http://{self.server_address}/history/{prompt_id}"
        ) as response:
            return json.loads(response.read())

    def build_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        checkpoint: str,
        lora: Optional[str],
        lora_strength: float,
        width: int,
        height: int,
        steps: int,
        cfg: float,
        seed: Optional[int],
        init_image: Optional[str] = None,
        denoise: float = 1.0,
    ) -> dict:
        workflow = {
            "10": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
        }
        # With no LoRA, text encoders and the sampler read the checkpoint
        # outputs directly.
        model_ref, clip_ref = ["10", 0], ["10", 1]
        if lora:
            workflow["2"] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["10", 0],
                    "clip": ["10", 1],
                    "lora_name": lora,
                    "strength_model": lora_strength,
                    # Workaround: on Mac MPS, LoRA application can produce
                    # "half-static" / corrupted decode when both model+clip
                    # strengths are set. Empirically, setting clip strength to
                    # 0 keeps the prompt encoding stable while the model
                    # still gets the style.
                    "strength_clip": 0.0,
                },
            }
            model_ref, clip_ref = ["2", 0], ["2", 1]

        if init_image:
            # img2img: encode a reference sprite and partially denoise.
            workflow["20"] = {
                "class_type": "LoadImage",
                "inputs": {"image": init_image},
            }
            workflow["21"] = {
                "class_type": "VAEEncode",
                "inputs": {"pixels": ["20", 0], "vae": ["10", 2]},
            }
            latent_ref = ["21", 0]
            denoise_value = denoise
        else:
            workflow["12"] = {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            }
            latent_ref = ["12", 0]
            denoise_value = 1.0

        workflow.update(
            {
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"clip": clip_ref, "text": prompt},
                },
                "5": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"clip": clip_ref, "text": negative_prompt},
                },
                "7": {
                    "class_type": "KSampler",
                    "inputs": {
                        "model": model_ref,
                        "positive": ["6", 0],
                        "negative": ["5", 0],
                        "latent_image": latent_ref,
                        "seed": seed if seed is not None else random.randint(0, 2**32),
                        "steps": steps,
                        "cfg": cfg,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": denoise_value,
                    },
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {"samples": ["7", 0], "vae": ["10", 2]},
                },
                "14": {
                    "class_type": "SaveImage",
                    "inputs": {"images": ["8", 0], "filename_prefix": "matcha"},
                },
            }
        )
        return workflow

    def _wait_for_completion(self, prompt_id: str) -> None:
        """Block on the websocket until the prompt finishes.

        Raises GenerationError with the server's actual failure message on
        an execution_error frame — this is where 'Generated 0 images' used
        to silently swallow corrupt-checkpoint and bad-node failures.
        """
        ws = websocket.WebSocket()
        ws.connect(
            f"ws://{self.server_address}/ws?clientId={self.client_id}"
        )
        try:
            while True:
                msg = ws.recv()
                if not isinstance(msg, str):
                    continue  # binary preview frames
                data = json.loads(msg)
                if data.get("type") == "execution_error":
                    err = data.get("data", {})
                    if err.get("prompt_id") not in (None, prompt_id):
                        continue
                    raise GenerationError(
                        f"ComfyUI failed at node {err.get('node_type', '?')}: "
                        f"{err.get('exception_message', 'unknown error')}",
                        node_type=err.get("node_type", ""),
                        prompt_id=prompt_id,
                    )
                if data.get("type") == "executing":
                    d = data.get("data", {})
                    if d.get("node") is None and d.get("prompt_id") == prompt_id:
                        return
        finally:
            ws.close()

    def generate(
        self,
        prompt: str,
        checkpoint: str,
        negative_prompt: str = "low quality",
        lora: Optional[str] = None,
        lora_strength: float = 1.0,
        width: int = 512,
        height: int = 768,
        steps: int = 20,
        cfg: float = 8.0,
        seed: Optional[int] = None,
        init_image_bytes: Optional[bytes] = None,
        denoise: float = 1.0,
    ) -> list[bytes]:
        init_name = None
        if init_image_bytes is not None and denoise < 1.0:
            init_name = self.upload_image(
                init_image_bytes, filename=f"matcha_ref_{self.client_id[:8]}.png"
            )
        workflow = self.build_workflow(
            prompt, negative_prompt, checkpoint, lora, lora_strength,
            width, height, steps, cfg, seed,
            init_image=init_name,
            denoise=denoise,
        )
        queued = self.queue_prompt(workflow)
        prompt_id = queued["prompt_id"]

        self._wait_for_completion(prompt_id)

        history = self.get_history(prompt_id)
        if prompt_id not in history:
            raise GenerationError(
                f"Prompt {prompt_id} completed but is missing from history",
                prompt_id=prompt_id,
            )
        outputs = history[prompt_id]["outputs"]

        # The workflow's SaveImage node is stable: "14".
        # History includes other nodes with "images", and relying on dict
        # iteration order can occasionally pick the wrong one.
        save_node = outputs.get("14") or {}
        save_images = save_node.get("images", [])

        images: list[bytes] = []
        for image in save_images:
            images.append(
                self.get_image(
                    image["filename"],
                    image.get("subfolder", ""),
                    image.get("type", "output"),
                )
            )

        # Fallback: older / alternate workflows might not use node id "14".
        if not images:
            for node_output in outputs.values():
                for image in node_output.get("images", []):
                    images.append(
                        self.get_image(
                            image["filename"],
                            image.get("subfolder", ""),
                            image.get("type", "output"),
                        )
                    )
        if not images:
            raise GenerationError(
                "Prompt executed but produced no images — check the SaveImage "
                "node and the ComfyUI server log",
                prompt_id=prompt_id,
            )
        return images
