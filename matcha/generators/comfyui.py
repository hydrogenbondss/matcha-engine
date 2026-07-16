import json
import random
import urllib.parse
import urllib.request
import uuid
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
    ) -> dict:
        workflow = {
            "10": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "12": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
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
                    "strength_clip": lora_strength,
                },
            }
            model_ref, clip_ref = ["2", 0], ["2", 1]

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
                        "latent_image": ["12", 0],
                        "seed": seed if seed is not None else random.randint(0, 2**32),
                        "steps": steps,
                        "cfg": cfg,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1,
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
    ) -> list[bytes]:
        workflow = self.build_workflow(
            prompt, negative_prompt, checkpoint, lora, lora_strength,
            width, height, steps, cfg, seed,
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

        images = []
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
