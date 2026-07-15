import typer
from pathlib import Path
from typing import Optional
import yaml
import tempfile

from matcha.config import CharacterConfig, MatchaConfig
from matcha.generators.comfyui import ComfyUIGenerator
from matcha.formatters.renpy import RenPyFormatter
from matcha.deployers.filesystem import FilesystemDeployer

app = typer.Typer(help="Matcha Engine — AI game asset pipeline")

@app.command()
def character(
    config: Path = typer.Argument(..., help="Path to character YAML config"),
    project: Optional[Path] = typer.Option(
        None, "--project", "-p", help="Path to Ren'Py project (e.g., ~/Desktop/LOVE32/LOVE32)"
    ),
    deploy: bool = typer.Option(False, "--deploy", help="Deploy to Ren'Py project"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without generating"),
    comfyui: str = typer.Option("127.0.0.1:8188", "--comfyui", help="ComfyUI server address"),
):
    """Generate character assets and optionally deploy to Ren'Py."""
    if not config.exists():
        typer.echo(f"Config not found: {config}", err=True)
        raise typer.Exit(1)
    
    with open(config) as f:
        data = yaml.safe_load(f)
    
    char_config = CharacterConfig(**data)
    
    typer.echo(f"Character: {char_config.name}")
    typer.echo(f"Poses: {', '.join(char_config.poses)}")
    typer.echo(f"Description: {char_config.description}")
    
    if dry_run:
        typer.echo("Dry run — no generation")
        return
    
    # Generate images
    typer.echo("Connecting to ComfyUI...")
    generator = ComfyUIGenerator(server_address=comfyui)
    
    generated_images = []
    for pose in char_config.poses:
        prompt = f"{char_config.description}, {pose} pose, visual novel style"
        typer.echo(f"Generating: {pose}...")
        
        try:
            images = generator.generate(
                prompt=prompt,
                checkpoint="anythingV5PrtRE.safetensors",
                lora="small_hours_style_v1.safetensors",
                lora_strength=1.0,
                width=char_config.width,
                height=char_config.height,
            )
            generated_images.extend(images)
        except Exception as e:
            typer.echo(f"Error generating {pose}: {e}", err=True)
            continue
    
    typer.echo(f"Generated {len(generated_images)} images")
    
    # Save to temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="matcha_"))
    image_paths = []
    for i, img_data in enumerate(generated_images):
        pose = char_config.poses[i] if i < len(char_config.poses) else f"pose_{i}"
        img_path = temp_dir / f"{char_config.name}_{pose}.png"
        with open(img_path, "wb") as f:
            f.write(img_data)
        image_paths.append(img_path)
        typer.echo(f"Saved: {img_path}")
    
    # Deploy if requested
    if deploy and project:
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"Deploying to {project}...")
        
        # Format and deploy
        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)
        
        formatted = formatter.format_batch(
            image_paths,
            char_config.name,
            char_config.poses,
        )
        
        deployed = deployer.deploy_images(formatted, subfolder="characters")
        
        # Update script
        script_block = deployer.update_script(
            char_config.name,
            char_config.poses,
        )
        
        typer.echo(f"Deployed {len(deployed)} images")
        typer.echo("Script updated with character definitions")
    else:
        typer.echo(f"Images saved to: {temp_dir}")
        typer.echo("Use --deploy --project /path/to/renpy to deploy")


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
    example.write_text("""name: sakura
description: "1girl, pink hair, school uniform, visual novel style"
poses:
  - idle
  - happy
  - sad
  - surprised
output_dir: ./output
""")
    
    typer.echo(f"Created project: {name}")
    typer.echo(f"Edit {example} and run:")
    typer.echo(f"  matcha character {example} --deploy --project ~/Desktop/LOVE32/LOVE32")


if __name__ == "__main__":
    app()
