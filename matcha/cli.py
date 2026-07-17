import tempfile
from pathlib import Path
from typing import Optional

import typer
import yaml

from matcha.config import CharacterConfig
from matcha.errors import GenerationError, PreflightError
from matcha.formatters.renpy import RenPyFormatter
from matcha.deployers.filesystem import FilesystemDeployer
from matcha.generators.comfyui import ComfyUIGenerator
from matcha import preflight

app = typer.Typer(help="Matcha Engine — AI game asset pipeline")


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

    typer.echo(f"Character: {char_config.name}")
    typer.echo(f"Poses: {', '.join(char_config.poses)}")
    typer.echo(f"Description: {char_config.description}")
    typer.echo(f"Checkpoint: {char_config.checkpoint}")
    typer.echo(f"LoRA: {char_config.lora or '(none)'}")

    # Preflight: verify the server knows these models before queueing
    # anything, so a wrong name is one clear error, not N opaque 400s.
    try:
        preflight.validate_models(comfyui, char_config.checkpoint, char_config.lora)
    except PreflightError as e:
        typer.echo(f"Preflight failed: {e}", err=True)
        raise typer.Exit(1)
    typer.echo("Preflight OK: models found on server")

    if dry_run:
        typer.echo("Dry run — config and models validated, no generation")
        return

    generator = ComfyUIGenerator(server_address=comfyui)

    generated: list[tuple[str, bytes]] = []  # (pose, image bytes)
    failures: list[tuple[str, str]] = []
    for pose in char_config.poses:
        prompt = f"{char_config.description}, {pose} pose, visual novel style"
        typer.echo(f"Generating: {pose}...")
        try:
            images = generator.generate(
                prompt=prompt,
                negative_prompt=char_config.negative_prompt,
                checkpoint=char_config.checkpoint,
                lora=char_config.lora,
                lora_strength=char_config.lora_strength,
                width=char_config.width,
                height=char_config.height,
                steps=char_config.steps,
                cfg=char_config.cfg,
                seed=char_config.seed,
            )
            generated.append((pose, images[0]))
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

    temp_dir = Path(tempfile.mkdtemp(prefix="matcha_"))
    image_paths: list[Path] = []
    poses_done: list[str] = []
    for pose, img_data in generated:
        img_path = temp_dir / f"{char_config.name}_{pose}.png"
        img_path.write_bytes(img_data)
        image_paths.append(img_path)
        poses_done.append(pose)
        typer.echo(f"Saved: {img_path}")

    if deploy and project:
        project = project.expanduser()
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)

        typer.echo(f"Deploying to {project}...")
        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)

        formatted = formatter.format_batch(
            image_paths,
            char_config.name,
            poses_done,
            max_width=char_config.resize_max_width,
            max_height=char_config.resize_max_height,
        )
        deployed = deployer.deploy_images(formatted, subfolder="characters")
        # Only the poses that actually generated get definitions.
        script_path = deployer.update_script(
            char_config.name,
            formatter.script_block(char_config.name, poses_done),
        )
        typer.echo(f"Deployed {len(deployed)} images")
        typer.echo(f"Definitions written to {script_path}")
    else:
        typer.echo(f"Images saved to: {temp_dir}")
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
    example.write_text(
        """name: sakura
description: "1girl, pink hair, school uniform, visual novel style"
poses:
  - idle
  - happy
  - sad
  - surprised

# Model selection — the checkpoint and LoRA must share a base model family
# (an SD1.5 LoRA on an SDXL checkpoint fails or degrades silently).
checkpoint: anythingV5PrtRE.safetensors
lora: small_hours_style_v1.safetensors
lora_strength: 1.0

width: 512
height: 768
output_dir: ./output
"""
    )

    typer.echo(f"Created project: {name}")
    typer.echo(f"Edit {example} and run:")
    typer.echo(f"  matcha character {example} --deploy --project /path/to/renpy")


if __name__ == "__main__":
    app()
