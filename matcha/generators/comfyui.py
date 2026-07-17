import json
import uuid
import websocket
import urllib.request
import urllib.parse
import time
from typing import Optional, List


class ComfyUIGenerator:
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt: dict) -> dict:
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
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

    def generate(
        self,
        prompt: str,
        checkpoint: str = "sd_xl_base.safetensors",
        lora: Optional[str] = None,
        lora_strength: float = 1.0,
        width: int = 512,
        height: int = 512,
        negative_prompt: str = "low quality, blurry, worst quality",
        steps: int = 20,
        cfg: float = 8.0,
        seed: int = -1,
    ) -> List[bytes]:
        if seed == -1:
            seed = uuid.uuid4().int % (2**32)

        # Build workflow (same structure as your working test)
        workflow = {
            "10": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "12": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["10", 1], "text": prompt}
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["10", 1], "text": negative_prompt}
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["10", 0],
                    "positive": ["6", 0],
                    "negative": ["5", 0],
                    "latent_image": ["12", 0],
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["7", 0], "vae": ["10", 2]}
            },
            "14": {
                "class_type": "SaveImage",
                "inputs": {"images": ["8", 0], "filename_prefix": "matcha"}
            }
        }

        # Inject LoRA if specified
        if lora:
            workflow["2"] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["10", 0],
                    "clip": ["10", 1],
                    "lora_name": lora,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                }
            }
            workflow["6"]["inputs"]["clip"] = ["2", 1]
            workflow["5"]["inputs"]["clip"] = ["2", 1]
            workflow["7"]["inputs"]["model"] = ["2", 0]

        # Queue prompt
        response = self.queue_prompt(workflow)
        prompt_id = response['prompt_id']
        print(f"[Matcha] Prompt queued: {prompt_id}")

        # Wait for execution via websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        try:
            while True:
                msg = ws.recv()
                if isinstance(msg, str):
                    data = json.loads(msg)
                    # FIXED: Check data['data'], not data directly
                    if data.get('type') == 'executing':
                        node = data.get('data', {}).get('node')
                        msg_prompt_id = data.get('data', {}).get('prompt_id')
                        if node is None and msg_prompt_id == prompt_id:
                            print(f"[Matcha] Execution complete for {prompt_id}")
                            break
                # Ignore binary preview frames
        finally:
            ws.close()

        # Small delay to ensure history is written
        time.sleep(0.5)

        # Get images from history
        history = self.get_history(prompt_id)
        if prompt_id not in history:
            raise RuntimeError(f"Prompt {prompt_id} not found in history")

        outputs = history[prompt_id]['outputs']
        images = []
        for node_id in outputs:
            node_output = outputs[node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    img_data = self.get_image(
                        image['filename'],
                        image.get('subfolder', ''),
                        image.get('type', 'output')
                    )
                    images.append(img_data)

        return images
