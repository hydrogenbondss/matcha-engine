import typer
from pathlib import Path
from typing import Optional
import yaml

from matcha.config import CharacterConfig, MatchaConfig

app = typer.Typer(help="Matcha Engine — AI game asset pipeline")

@app.command()
def character(
    config: Path = typer.Argument(..., help="Path to character YAML config"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without generating"),
):
    """Generate character assets from config."""
    if not config.exists():
        typer.echo(f"Config not found: {config}", err=True)
        raise typer.Exit(1)
    
    with open(config) as f:
        data = yaml.safe_load(f)
    
    char_config = CharacterConfig(**data)
    
    typer.echo(f"Character: {char_config.name}")
    typer.echo(f"Poses: {', '.join(char_config.poses)}")
    typer.echo(f"Output: {char_config.output_dir}")
    
    if dry_run:
        typer.echo("Dry run — no generation")
        return
    
    typer.echo("Generating... (not implemented yet)")
    # TODO: Call generator pipeline


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
    typer.echo(f"Edit {example} and run: matcha character {example}")


if __name__ == "__main__":
    app()
