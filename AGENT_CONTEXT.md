# Matcha Engine — Agent Context

## What This Is
AI-powered game asset pipeline. Describe a character → generate sprites → format for Ren'Py → deploy.

## Status
- [x] Repo created
- [x] AGENT_CONTEXT.md written
- [x] CLI skeleton (init, character commands)
- [x] Config schema (Pydantic models)
- [x] Example config
- [ ] ComfyUI generator module
- [ ] Ren'Py formatter
- [ ] First working pipeline

## Tech Stack
- Python, Typer, Pydantic, Pillow, GitPython
- ComfyUI API for generation
- Ren'Py for deployment target

## Unknowns (Need User Input)
- ComfyUI checkpoint/model used
- Typical prompts and LoRA setup
- Number of poses per character
- Output folder structure (RunPod vs local)
- Ren'Py project path and image folder structure

## Next Action
Write ComfyUI generator module. User to provide workflow details.

## Decisions
- Focus on Ren'Py first, Godot later
- One character pipeline before scene/background
- Manual copy-paste agent workflow until token setup
