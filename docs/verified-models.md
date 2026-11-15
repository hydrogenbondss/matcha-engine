# Verified model checklist

**Not legal advice.** Commercial-use status below is a best-effort summary of
commonly cited terms — always verify the license on the model's own page
(Civitai / Hugging Face / model card) before shipping anything. Matcha does
not download, install, or redistribute model weights; put files in the
folders below yourself and restart ComfyUI.

Base-family rule: checkpoint and LoRA must be trained on the same base
family. An SD1.5 LoRA on an SDXL checkpoint (or vice versa) fails or
silently degrades output.

## Checkpoints → `ComfyUI/models/checkpoints/`

| Filename | Base family | Where to get it | Commercial-use status | Known issues |
|---|---|---|---|---|
| `anythingV5PrtRE.safetensors` | SD1.5 | Civitai ("Anything V5 / PrtRE") | **Likely OK (verify).** Anything-series inherits Fair AI Public License 1.0-SD: the license covers the weights, not outputs ([Civitai licensing article](https://civitai.com/articles/18619/what-the-license)) | The Matcha trusted-first-success default. Pair only with SD1.5 LoRAs |
| `sd_xl_base_1.0.safetensors` | SDXL | Stability AI / Hugging Face | **Unknown — check the model page** (OpenRAIL-family terms) | Do **not** pair with SD1.5 LoRAs; higher VRAM; 512×512 recipes do not transfer |

## LoRAs → `ComfyUI/models/loras/`

| Filename | Base family | Where to get it | Commercial-use status | Known issues |
|---|---|---|---|---|
| `small_hours_style_v1.safetensors` | SD1.5 (trained on `sd-v1-5-pruned`) | Author-trained; not publicly distributed | **Unknown — check with the LoRA's author** | **Black/NaN output on Mac MPS** with Anything V5 (even at strength 0.5). Avoid on MPS |
| `last.safetensors` (interim SmallHours) | SD1.5 | Author-trained; not publicly distributed | **Unknown — check with the LoRA's author** | Works at ~0.7 strength with Anything V5 on Mac MPS; keep `strength_clip = 0` (Matcha does this automatically) |

## Optional: IP-Adapter (same-face experiments, CUDA only) → `ComfyUI/models/ipadapter/` + `ComfyUI/models/clip_vision/`

| Filename | Base family | Where to get it | Commercial-use status | Known issues |
|---|---|---|---|---|
| `ip-adapter_sd15.safetensors` | SD1.5 | h94 / IP-Adapter on Hugging Face (needs `ComfyUI_IPAdapter_plus` custom nodes) | **Unknown — check the model page** | **Corrupt output on Mac MPS** — leave `ip_adapter_weight: 0` locally; retry on CUDA |
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | — (vision encoder) | Hugging Face (laion) | **Unknown — check the model page** | Required companion for IP-Adapter; same MPS corruption caveat |

After placing files, restart ComfyUI and run `matcha setup` — it lists the
checkpoint/LoRA names the server actually sees, which is the name your YAML
must match exactly.
