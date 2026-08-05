import random
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import typer
import yaml

from matcha.config import CharacterConfig
from matcha.disclosure import build_disclosure_document
from matcha.errors import GenerationError, PreflightError
from matcha.formatters.renpy import RenPyFormatter
from matcha.deployers.filesystem import FilesystemDeployer
from matcha.generators.comfyui import ComfyUIGenerator
from matcha.images import assert_usable_image
from matcha.licenses import format_license_report
from matcha.prompts import build_negative_prompt, build_pose_prompt
from matcha import preflight

app = typer.Typer(help="Matcha Engine — AI game asset pipeline")

_EXAMPLE_YAML = """\
name: sakura
display_name: Sakura
color: "#ff69b4"
# Lock identity here: outfit, hair, eyes. Pose prompts only vary expression.
description: >-
  sh_style, 1girl, long straight pink hair down past shoulders with bangs,
  not in a ponytail, purple eyes, white collared shirt, pink bow tie,
  black school sweater with pink trim at the neckline, no chest emblem,
  visual novel style
poses:
  - idle
  - happy
  - sad
  - surprised

# Model selection — checkpoint and LoRA must share a base model family.
# small_hours_style_v1 is SD1.5 but currently NaNs/blacks on Mac MPS;
# last.safetensors is the working interim on that stack.
checkpoint: anythingV5PrtRE.safetensors
lora: last.safetensors
lora_strength: 0.7

# 512×512 is safer on Mac MPS; use 512×768 when VRAM allows.
width: 512
height: 512
steps: 20
seed: 42
# Later poses img2img from the first sprite (identity lock). 1.0 = off.
# On Mac MPS, values < 1.0 currently produce glitched frames — keep off.
consistency_denoise: 1.0
# IP-Adapter identity lock (later poses condition on first sprite).
# 0.0 = off. Works on CUDA; currently corrupts on Mac MPS — leave off here.
# ip_adapter_weight: 0.65
# ip_adapter_file: ip-adapter_sd15.safetensors
# clip_vision: CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors

# Optional: shrink sprites to fit within these bounds after generation
# (aspect preserved, never upscales). Useful for 720p Ren'Py projects.
# resize_max_width: 1280
# resize_max_height: 720

# Side-image portraits (opt in with --side-image or side_image: true).
# Crops the top fraction of each sprite for Ren'Py dialogue portraits.
# side_image: true
# side_image_height_ratio: 0.45

output_dir: ./output
"""


@app.command()
def character(
    config: Path = typer.Argument(..., help="Path to character YAML config"),
    project: Optional[Path] = typer.Option(
        None, "--project", "-p", help="Path to Ren'Py project"
    ),
    deploy: bool = typer.Option(False, "--deploy", help="Deploy to Ren'Py project"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate config and models without generating"),
    comfyui: str = typer.Option("127.0.0.1:8188", "--comfyui", help="ComfyUI server address"),
    checkpoint: Optional[str] = typer.Option(
        None, "--checkpoint", "-c", help="Override the checkpoint from the YAML config"
    ),
    lora: Optional[str] = typer.Option(
        None, "--lora", help="Override the LoRA from the YAML config ('none' to disable)"
    ),
    layered: Optional[bool] = typer.Option(
        None, "--layered/--no-layered",
        help="Emit a Ren'Py layeredimage grouping poses as attributes",
    ),
    side_image: Optional[bool] = typer.Option(
        None, "--side-image/--no-side-image",
        help=(
            "Crop head/shoulders portraits, emit image side defs, "
            "and wire Character(image=...)"
        ),
    ),
):
    """Generate character assets and optionally deploy to Ren'Py."""
    if not config.exists():
        typer.echo(f"Config not found: {config}", err=True)
        raise typer.Exit(1)

    with open(config) as f:
        data = yaml.safe_load(f)

    char_config = CharacterConfig(**data)
    if checkpoint:
        char_config.checkpoint = checkpoint
    if lora:
        char_config.lora = None if lora.lower() == "none" else lora
    if layered is not None:
        char_config.layered = layered
    if side_image is not None:
        char_config.side_image = side_image

    # One seed for the whole set — identity consistency across poses.
    run_seed = (
        char_config.seed
        if char_config.seed is not None
        else random.randint(0, 2**32 - 1)
    )

    typer.echo(f"Character: {char_config.name}")
    typer.echo(f"Poses: {', '.join(char_config.poses)}")
    typer.echo(f"Description: {char_config.description}")
    typer.echo(f"Checkpoint: {char_config.checkpoint}")
    typer.echo(f"LoRA: {char_config.lora or '(none)'}")
    typer.echo(f"Seed: {run_seed} (shared across poses)")
    typer.echo(format_license_report(char_config.checkpoint, char_config.lora))
    if char_config.consistency_denoise < 1.0:
        typer.echo(
            f"Consistency: later poses img2img from first "
            f"(denoise={char_config.consistency_denoise})"
        )
    if char_config.ip_adapter_weight > 0:
        typer.echo(
            f"IP-Adapter: later poses lock to first "
            f"(weight={char_config.ip_adapter_weight})"
        )

    # Preflight: verify the server knows these models before queueing
    # anything, so a wrong name is one clear error, not N opaque 400s.
    try:
        ipa = (
            char_config.ip_adapter_file
            if char_config.ip_adapter_weight > 0
            else None
        )
        cv = (
            char_config.clip_vision
            if char_config.ip_adapter_weight > 0
            else None
        )
        preflight.validate_models(
            comfyui,
            char_config.checkpoint,
            char_config.lora,
            ip_adapter_file=ipa,
            clip_vision=cv,
        )
    except PreflightError as e:
        typer.echo(f"Preflight failed: {e}", err=True)
        raise typer.Exit(1)
    typer.echo("Preflight OK: models found on server")

    if dry_run:
        typer.echo("Dry run — config and models validated, no generation")
        return

    generator = ComfyUIGenerator(server_address=comfyui)
    negative = build_negative_prompt(char_config.negative_prompt)

    generated: list[tuple[str, bytes]] = []  # (pose, image bytes)
    failures: list[tuple[str, str]] = []
    reference_bytes: Optional[bytes] = None
    for i, pose in enumerate(char_config.poses):
        prompt = build_pose_prompt(char_config.description, pose)
        use_img2img = (
            reference_bytes is not None
            and char_config.consistency_denoise < 1.0
        )
        use_ipa = (
            reference_bytes is not None
            and char_config.ip_adapter_weight > 0
        )
        # Slight seed offset per pose so expression can change under img2img.
        pose_seed = run_seed + i
        modes = []
        if use_img2img:
            modes.append(f"img2img denoise={char_config.consistency_denoise}")
        if use_ipa:
            modes.append(f"ip-adapter w={char_config.ip_adapter_weight}")
        mode = "+".join(modes) if modes else "txt2img"
        typer.echo(f"Generating: {pose} ({mode})...")
        try:
            images = generator.generate(
                prompt=prompt,
                negative_prompt=negative,
                checkpoint=char_config.checkpoint,
                lora=char_config.lora,
                lora_strength=char_config.lora_strength,
                width=char_config.width,
                height=char_config.height,
                steps=char_config.steps,
                cfg=char_config.cfg,
                seed=pose_seed,
                init_image_bytes=reference_bytes if use_img2img else None,
                denoise=(
                    char_config.consistency_denoise if use_img2img else 1.0
                ),
                ip_adapter_image_bytes=reference_bytes if use_ipa else None,
                ip_adapter_weight=(
                    char_config.ip_adapter_weight if use_ipa else 0.0
                ),
                ip_adapter_file=char_config.ip_adapter_file,
                clip_vision=char_config.clip_vision,
            )
            assert_usable_image(images[0], label=pose)
            generated.append((pose, images[0]))
            if reference_bytes is None:
                reference_bytes = images[0]
        except GenerationError as e:
            typer.echo(f"  FAILED ({pose}): {e}", err=True)
            failures.append((pose, str(e)))

    typer.echo(f"Generated {len(generated)}/{len(char_config.poses)} poses")

    if not generated:
        typer.echo(
            "No images were generated — skipping deploy and script update.",
            err=True,
        )
        raise typer.Exit(1)

    out_dir = Path(char_config.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    # Also keep a temp copy so deploy formatting never mutates unexpected paths
    # if the user points output_dir at something shared — we copy into out_dir
    # as the canonical local artifacts.
    image_paths: list[Path] = []
    poses_done: list[str] = []
    for pose, img_data in generated:
        img_path = out_dir / f"{char_config.name}_{pose}.png"
        img_path.write_bytes(img_data)
        image_paths.append(img_path)
        poses_done.append(pose)
        typer.echo(f"Saved: {img_path}")

    if deploy and project:
        project = project.expanduser()
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)

        # format_batch may resize in place — work on copies so output_dir
        # keeps the originals.
        work_dir = Path(tempfile.mkdtemp(prefix="matcha_deploy_"))
        work_paths = []
        for src in image_paths:
            dest = work_dir / src.name
            shutil.copy2(src, dest)
            work_paths.append(dest)

        typer.echo(f"Deploying to {project}...")
        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)

        formatted = formatter.format_batch(
            work_paths,
            char_config.name,
            poses_done,
            max_width=char_config.resize_max_width,
            max_height=char_config.resize_max_height,
        )
        deployed = deployer.deploy_images(formatted, subfolder="characters")

        if char_config.side_image:
            # Crop from resized work copies so portraits match deployed sprites.
            side_formatted = formatter.format_side_images(
                work_paths,
                char_config.name,
                poses_done,
                height_ratio=char_config.side_image_height_ratio,
                dest_dir=work_dir,
            )
            side_deployed = deployer.deploy_images(
                side_formatted, subfolder="characters"
            )
            deployed.extend(side_deployed)
            # Also keep local copies next to the full sprites.
            for src, filename in side_formatted:
                local = out_dir / filename
                shutil.copy2(src, local)
                typer.echo(f"Saved side portrait: {local}")

        script_path = deployer.update_script(
            char_config.name,
            formatter.script_block(
                char_config.name,
                poses_done,
                display_name=char_config.display_name,
                color=char_config.color,
                layered=char_config.layered,
                side_image=char_config.side_image,
            ),
        )
        typer.echo(f"Deployed {len(deployed)} images")
        typer.echo(f"Definitions written to {script_path}")
    else:
        if char_config.side_image:
            formatter = RenPyFormatter(out_dir)
            side_formatted = formatter.format_side_images(
                image_paths,
                char_config.name,
                poses_done,
                height_ratio=char_config.side_image_height_ratio,
                dest_dir=out_dir,
            )
            for _, filename in side_formatted:
                typer.echo(f"Saved side portrait: {out_dir / filename}")
        typer.echo(f"Images saved to: {out_dir}")
        typer.echo("Use --deploy --project /path/to/renpy to deploy")

    if failures:
        typer.echo(
            f"{len(failures)} pose(s) failed: "
            + ", ".join(pose for pose, _ in failures),
            err=True,
        )
        raise typer.Exit(2)


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
):
    """Initialize a new Matcha project."""
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)

    configs_dir = project_dir / "configs"
    configs_dir.mkdir(exist_ok=True)

    example = configs_dir / "example_character.yaml"
    example.write_text(_EXAMPLE_YAML)

    typer.echo(f"Created project: {name}")
    typer.echo(f"Edit {example} and run (from your Matcha venv):")
    typer.echo(
        f"  .venv/bin/matcha character {example} "
        f"--deploy --project /path/to/renpy"
    )


@app.command("licenses")
def licenses_cmd(
    checkpoint: Optional[str] = typer.Option(
        None, "--checkpoint", "-c", help="Checkpoint filename to look up"
    ),
    lora: Optional[str] = typer.Option(
        None, "--lora", help="LoRA filename to look up ('none' to skip)"
    ),
    config: Optional[Path] = typer.Argument(
        None,
        help="Optional character YAML — uses its checkpoint/LoRA if flags omitted",
    ),
):
    """Look up commercial-use status for a checkpoint / LoRA (not legal advice)."""
    ckpt = checkpoint
    lr: Optional[str] = None if (lora and lora.lower() == "none") else lora

    if config is not None:
        if not config.exists():
            typer.echo(f"Config not found: {config}", err=True)
            raise typer.Exit(1)
        with open(config) as f:
            data = yaml.safe_load(f) or {}
        if ckpt is None:
            ckpt = data.get("checkpoint")
        if lr is None and lora is None:
            lr = data.get("lora")

    if not ckpt:
        typer.echo(
            "Provide a checkpoint via --checkpoint or a character YAML path.",
            err=True,
        )
        raise typer.Exit(1)

    typer.echo(format_license_report(ckpt, lr))


@app.command()
def disclose(
    config: Optional[Path] = typer.Argument(
        None,
        help="Optional character YAML — fills name/checkpoint/LoRA",
    ),
    checkpoint: Optional[str] = typer.Option(
        None, "--checkpoint", "-c", help="Checkpoint filename used for generation"
    ),
    lora: Optional[str] = typer.Option(
        None, "--lora", help="LoRA filename ('none' to omit)"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Character name for the disclosure draft"
    ),
    write: Optional[Path] = typer.Option(
        None,
        "--write",
        "-w",
        help="Write markdown to this path instead of printing",
    ),
    project: Optional[Path] = typer.Option(
        None,
        "--project",
        "-p",
        help="Ren'Py project dir — writes matcha_disclosure.md there "
        "(unless --write is set)",
    ),
    live_generated: bool = typer.Option(
        False,
        "--live-generated",
        help="Draft Steam survey as Live-Generated instead of Pre-Generated",
    ),
):
    """Draft Steam AI Content Survey + itch.io AI-tag disclosure text.

    Not legal advice. Use a character YAML and/or --checkpoint/--lora/--name.
    Prints markdown to stdout, or write with --write / --project.
    """
    char_name = name
    ckpt = checkpoint
    lr: Optional[str] = None if (lora and lora.lower() == "none") else lora

    if config is not None:
        if not config.exists():
            typer.echo(f"Config not found: {config}", err=True)
            raise typer.Exit(1)
        with open(config) as f:
            data = yaml.safe_load(f) or {}
        if char_name is None:
            char_name = data.get("display_name") or data.get("name")
        if ckpt is None:
            ckpt = data.get("checkpoint")
        if lr is None and lora is None:
            lr = data.get("lora")

    doc = build_disclosure_document(
        character_name=char_name,
        checkpoint=ckpt,
        lora=lr,
        live_generated=live_generated,
    )

    out_path = write
    if out_path is None and project is not None:
        project = project.expanduser()
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)
        out_path = project / "matcha_disclosure.md"

    if out_path is not None:
        out_path = out_path.expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(doc)
        typer.echo(f"Wrote disclosure draft: {out_path}")
    else:
        typer.echo(doc)


if __name__ == "__main__":
    app()
