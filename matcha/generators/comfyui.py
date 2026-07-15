import json
import uuid
import websocket
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


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
    
    def build_character_workflow(
        self,
        prompt: str,
        checkpoint: str = "anythingV5PrtRE.safetensors",
        lora: str = "small_hours_style_v1.safetensors",
        lora_strength: float = 1.0,
        width: int = 512,
        height: int = 512,
        seed: Optional[int] = None,
        negative_prompt: str = "low quality, blurry, worst quality, deformed, bad anatomy, extra limbs, bad hands",
    ) -> dict:
        if seed is None:
            seed = int(uuid.uuid4().int % (2**32))
        
        return {
            "10": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "12": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1}
            },
            "2": {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["10", 0],
                    "clip": ["10", 1],
                    "lora_name": lora,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["2", 1],
                    "text": prompt
                }
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["2", 1],
                    "text": negative_prompt
                }
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["2", 0],
                    "positive": ["6", 0],
                    "negative": ["5", 0],
                    "latent_image": ["12", 0],
                    "seed": seed,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["10", 2]
                }
            },
            "14": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["8", 0],
                    "filename_prefix": "matcha_character"
                }
            }
        }
    
    def generate(self, prompt: str, **kwargs) -> list[bytes]:
        workflow = self.build_character_workflow(prompt, **kwargs)
        response = self.queue_prompt(workflow)
        prompt_id = response['prompt_id']
        
        # Wait for completion via websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break
        
        ws.close()
        
        # Get images from history
        history = self.get_history(prompt_id)
        outputs = history[prompt_id]['outputs']
        
        images = []
        for node_id in outputs:
            node_output = outputs[node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    img_data = self.get_image(
                        image['filename'],
                        image.get('subfolder', ''),
                        image.get('type', '')
                    )
                    images.append(img_data)
        
        return images
