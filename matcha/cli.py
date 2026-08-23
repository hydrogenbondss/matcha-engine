import random
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import typer
import yaml

from matcha.config import CharacterConfig, PoseOverride
from matcha.disclosure import build_disclosure_document
from matcha.errors import GenerationError, PreflightError
from matcha.formatters.renpy import RenPyFormatter
from matcha.deployers.filesystem import FilesystemDeployer
from matcha.generators.comfyui import ComfyUIGenerator
from matcha.images import (
    ImageQualityError,
    assert_usable_image,
    knockout_near_black,
    pad_to_canvas,
    parse_canvas,
    persist_rejection,
)
from matcha.licenses import format_license_report
from matcha.prompts import build_negative_prompt, build_pose_prompt
from matcha import preflight

app = typer.Typer(help="Matcha Engine — AI game asset pipeline")

DEFAULT_FILENAME_TEMPLATE = "{name}_{pose}.png"
# Echo live convention: space, not underscore. Copy-only only — never
# used as the generate output name (underscores stay inspectable locally).
ECHO_FILENAME_TEMPLATE = "{name} {pose}.png"
SEED_RETRY_STRIDE = 10007

_EXAMPLE_YAML = """\
name: sakura
display_name: Sakura
color: "#ff69b4"
# Shared identity only: face, hair, eyes, style. Outfit families belong
# under pose_overrides so one description cannot paint an apron onto every pose.
description: >-
  sh_style, 1girl, long straight pink hair down past shoulders with bangs,
  not in a ponytail, purple eyes, visual novel style, cel shaded
poses:
  - idle
  - happy
  - sad
  - surprised
# Optional look-sheet extras (also accepted inline: `- name: idle` + keys).
# pose_overrides:
#   idle:
#     outfit: white collared shirt, pink bow tie, black school sweater
#   happy:
#     outfit: white collared shirt, pink bow tie, black school sweater

# Model selection — checkpoint and LoRA must share a base model family.
# Trusted first success: base checkpoint only (lora: null). Override with
# --lora none even if a LoRA is set. Optional LoRAs are machine-specific
# (e.g. last.safetensors @ 0.7 on some Macs); small_hours_style_v1 NaNs on MPS.
checkpoint: anythingV5PrtRE.safetensors
lora: null
# lora: last.safetensors   # optional, after a clean base-checkpoint run
lora_strength: 0.7

# 512×512 is safer on Mac MPS; use 512×768 when VRAM allows.
width: 512
height: 512
steps: 20
seed: 42
# Later poses img2img from the first sprite (identity lock). 1.0 = off.
# DO NOT enable on Mac MPS — values < 1.0 currently produce glitched frames.
consistency_denoise: 1.0
# IP-Adapter identity lock (later poses condition on first sprite).
# DO NOT enable on Mac MPS — corrupts output. Leave weight at 0 / commented.
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


def parse_poses_flag(raw: Optional[str], available: list[str]) -> list[str]:
    """Resolve ``--poses idle,smoking`` against the YAML list.

    Order follows the flag (so a single named pose can run first). Unknown
    names are an error rather than a silent no-op.
    """
    if raw is None or not str(raw).strip():
        return list(available)
    wanted = [p.strip() for p in str(raw).split(",") if p.strip()]
    if not wanted:
        return list(available)
    unknown = [p for p in wanted if p not in available]
    if unknown:
        raise ValueError(
            "unknown pose(s) "
            + ", ".join(unknown)
            + " — YAML has: "
            + ", ".join(available)
        )
    return wanted


def render_filename(template: str, name: str, pose: str) -> str:
    try:
        out = template.format(name=name, pose=pose)
    except KeyError as e:
        raise ValueError(
            f"filename template {template!r} has unknown placeholder {e}; "
            "use {name} and/or {pose}"
        ) from e
    if not out.lower().endswith(".png"):
        out += ".png"
    return out


def is_love32_project(project: Path) -> bool:
    """True if *project* looks like the live LOVE32 tree.

    Matcha must never write into that game — Ren'Py auto-loads every
    ``game/*.rpy`` and Echo already owns the Character / layeredimage defs.
    """
    try:
        parts = [p.lower() for p in Path(project).expanduser().resolve().parts]
    except OSError:
        parts = [p.lower() for p in Path(project).parts]
    needle = str(project).lower()
    return any("love32" in p for p in parts) or "love32" in needle


def accepted_png_path(out_dir: Path, name: str, pose: str) -> Path:
    return Path(out_dir) / f"{name}_{pose}.png"


def reject_png_path(out_dir: Path, name: str, pose: str, seed: int) -> Path:
    return Path(out_dir) / "rejected" / f"{name}_{pose}_seed{seed}.png"


@app.command()
def character(
    config: Path = typer.Argument(..., help="Path to character YAML config"),
    project: Optional[Path] = typer.Option(
        None, "--project", "-p", help="Path to Ren'Py project"
    ),
    deploy: bool = typer.Option(
        False,
        "--deploy",
        help=(
            "Deploy images AND write game/matcha_characters.rpy "
            "(dangerous in a live game — prefer sample-vn / sandbox, "
            "or --copy-only for Echo-style filename copies)"
        ),
    ),
    copy_only: bool = typer.Option(
        False,
        "--copy-only",
        help=(
            "Copy accepted PNGs into the project's images folder using "
            "--filename-template. Does NOT write Character() or layeredimage."
        ),
    ),
    filename_template: Optional[str] = typer.Option(
        None,
        "--filename-template",
        help=(
            "Copy-only dest name. Placeholders: {name} {pose}. "
            f"Default {DEFAULT_FILENAME_TEMPLATE!r}; Echo live uses "
            f"{ECHO_FILENAME_TEMPLATE!r} (space)."
        ),
    ),
    images_subdir: Optional[str] = typer.Option(
        None,
        "--images-subdir",
        help=(
            "Under game/images/. Default 'characters' for --deploy, "
            "empty (game/images/) for --copy-only."
        ),
    ),
    poses: Optional[str] = typer.Option(
        None,
        "--poses",
        help="Generate only these YAML poses (comma-separated), e.g. smoking or idle,warm",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Regenerate even when an accepted PNG already exists in output_dir",
    ),
    retries: Optional[int] = typer.Option(
        None,
        "--retries",
        help="Extra seed attempts after a quality/generate failure (default: YAML quality_retries, 2)",
    ),
    knockout_black: bool = typer.Option(
        False,
        "--knockout-black",
        help="Best-effort: near-black pixels → transparent. Grey/white cards stay opaque.",
    ),
    canvas: Optional[str] = typer.Option(
        None,
        "--canvas",
        help="Pad accepted sprites onto a larger canvas (e.g. 768x1024). Does not change generation res.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate config and models without generating"),
    comfyui: str = typer.Option("127.0.0.1:8188", "--comfyui", help="ComfyUI server address"),
    checkpoint: Optional[str] = typer.Option(
        None, "--checkpoint", "-c", help="Override the checkpoint from the YAML config"
    ),
    lora: Optional[str] = typer.Option(
        None,
        "--lora",
        help=(
            "Override YAML LoRA ('none' = base checkpoint only — "
            "trusted first-success path)"
        ),
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

    try:
        run_poses = parse_poses_flag(poses, char_config.poses)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    retry_budget = char_config.quality_retries if retries is None else retries
    if retry_budget < 0:
        typer.echo("--retries must be >= 0", err=True)
        raise typer.Exit(1)

    canvas_size = None
    if canvas:
        try:
            canvas_size = parse_canvas(canvas)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)

    if (deploy or copy_only) and project is not None:
        if is_love32_project(project):
            typer.echo(
                "Refusing to write into a LOVE32 project. Echo already owns "
                "those Character / layeredimage defs. Generate into a sandbox "
                "(output_dir / sandbox-kite) and hand-copy PNGs, or use "
                "--copy-only against examples/sample-vn or sandbox-renpy.",
                err=True,
            )
            raise typer.Exit(1)

    # One seed for the whole set — identity consistency across poses.
    run_seed = (
        char_config.seed
        if char_config.seed is not None
        else random.randint(0, 2**32 - 1)
    )

    typer.echo(f"Character: {char_config.name}")
    typer.echo(f"Poses: {', '.join(run_poses)}")
    if run_poses != char_config.poses:
        typer.echo(f"  (YAML list: {', '.join(char_config.poses)})")
    typer.echo(f"Description: {char_config.description}")
    typer.echo(f"Checkpoint: {char_config.checkpoint}")
    typer.echo(f"LoRA: {char_config.lora or '(none)'}")
    typer.echo(f"Seed: {run_seed} (shared across poses; retries offset)")
    typer.echo(format_license_report(char_config.checkpoint, char_config.lora))
    if char_config.lora:
        typer.echo(
            "Tip: for a trusted first success, re-run with --lora none "
            "(base checkpoint only), then add a LoRA once that works."
        )
    if char_config.consistency_denoise < 1.0:
        typer.echo(
            "WARNING: consistency_denoise < 1.0 (img2img) corrupts on Mac MPS "
            f"(denoise={char_config.consistency_denoise}). Keep 1.0 for "
            "reliable runs.",
            err=True,
        )
    if char_config.ip_adapter_weight > 0:
        typer.echo(
            "WARNING: IP-Adapter corrupts on Mac MPS "
            f"(weight={char_config.ip_adapter_weight}). Leave "
            "ip_adapter_weight: 0 for reliable runs.",
            err=True,
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
        if char_config.lora:
            typer.echo(
                "Next: generate with --lora none for the safest first run, "
                "or omit the flag to use the YAML LoRA."
            )
        else:
            typer.echo(
                "Next: generate (no LoRA) — trusted first-success path is ready."
            )
        return

    out_dir = Path(char_config.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    generator = ComfyUIGenerator(server_address=comfyui)
    base_negative = char_config.negative_prompt

    generated: list[tuple[str, bytes, Path]] = []
    failures: list[tuple[str, str]] = []
    skipped: list[str] = []
    reference_bytes: Optional[bytes] = None

    # Original YAML index keeps pose_seed stable when --poses subsets.
    pose_index = {name: i for i, name in enumerate(char_config.poses)}

    for pose in run_poses:
        dest = accepted_png_path(out_dir, char_config.name, pose)
        if not force and dest.exists():
            try:
                existing = dest.read_bytes()
                assert_usable_image(existing, label=pose)
                typer.echo(f"Skipping {pose} (already accepted: {dest})")
                generated.append((pose, existing, dest))
                skipped.append(pose)
                if reference_bytes is None:
                    reference_bytes = existing
                continue
            except GenerationError as e:
                typer.echo(
                    f"Existing {dest} failed quality ({e}); regenerating...",
                    err=True,
                )

        override: Optional[PoseOverride] = char_config.pose_overrides.get(pose)
        prompt = build_pose_prompt(char_config.description, pose, override)
        negative = build_negative_prompt(base_negative, override)
        use_img2img = (
            reference_bytes is not None
            and char_config.consistency_denoise < 1.0
        )
        use_ipa = (
            reference_bytes is not None
            and char_config.ip_adapter_weight > 0
        )
        modes = []
        if use_img2img:
            modes.append(f"img2img denoise={char_config.consistency_denoise}")
        if use_ipa:
            modes.append(f"ip-adapter w={char_config.ip_adapter_weight}")
        mode = "+".join(modes) if modes else "txt2img"
        typer.echo(f"Generating: {pose} ({mode})...")

        last_err: Optional[Exception] = None
        accepted = False
        i = pose_index.get(pose, 0)
        for attempt in range(1 + retry_budget):
            pose_seed = run_seed + i + attempt * SEED_RETRY_STRIDE
            if attempt:
                typer.echo(f"  retry {attempt}/{retry_budget} (seed {pose_seed})...")
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
                raw = images[0]
                try:
                    assert_usable_image(raw, label=pose)
                except ImageQualityError as qe:
                    dump = reject_png_path(
                        out_dir, char_config.name, pose, pose_seed
                    )
                    persist_rejection(
                        qe.data or raw,
                        qe.metrics,
                        dump,
                        extra={
                            "character": char_config.name,
                            "pose": pose,
                            "seed": pose_seed,
                            "attempt": attempt + 1,
                            "reason": str(qe),
                        },
                    )
                    typer.echo(f"  rejected → {dump} (+ .json)", err=True)
                    raise
                img_data = raw
                if knockout_black:
                    img_data = knockout_near_black(img_data)
                if canvas_size is not None:
                    img_data = pad_to_canvas(img_data, *canvas_size)
                dest.write_bytes(img_data)
                typer.echo(f"Saved: {dest}")
                generated.append((pose, img_data, dest))
                if reference_bytes is None:
                    reference_bytes = raw
                accepted = True
                break
            except GenerationError as e:
                last_err = e
                typer.echo(f"  FAILED ({pose}, attempt {attempt + 1}): {e}", err=True)

        if not accepted:
            failures.append((pose, str(last_err) if last_err else "unknown"))

    typer.echo(
        f"Generated {len(generated) - len(skipped)}/{len(run_poses)} poses"
        + (f" ({len(skipped)} skipped)" if skipped else "")
        + f" → {out_dir}"
    )

    if not generated:
        typer.echo(
            "No images were generated — skipping deploy and script update.\n"
            "Rejected frames (if any) are under "
            f"{out_dir / 'rejected'}. "
            "If ComfyUI was unreachable or returned black/corrupt PNGs, fix "
            "the server (health-check curl), then retry with --lora none.\n"
            "Keep ComfyUI in one durable session — a second generate that "
            "issues a global interrupt can kill an in-flight pose.",
            err=True,
        )
        raise typer.Exit(1)

    image_paths = [path for _, _, path in generated]
    poses_done = [pose for pose, _, _ in generated]

    if copy_only:
        if project is None:
            typer.echo("--copy-only requires --project <renpy-dir>", err=True)
            raise typer.Exit(1)
        project = project.expanduser()
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)
        template = filename_template or DEFAULT_FILENAME_TEMPLATE
        sub = "" if images_subdir is None else images_subdir
        deployer = FilesystemDeployer(project)
        formatted: list[tuple[Path, str]] = []
        for pose, _, path in generated:
            try:
                fname = render_filename(template, char_config.name, pose)
            except ValueError as e:
                typer.echo(str(e), err=True)
                raise typer.Exit(1)
            formatted.append((path, fname))
        copied = deployer.deploy_images(formatted, subfolder=sub)
        dest_dir = (
            deployer.images_dir / sub if sub else deployer.images_dir
        )
        typer.echo(
            f"Copy-only: {len(copied)} PNG(s) → {dest_dir} "
            f"(template {template!r}). No Character() / layeredimage written."
        )
    elif deploy and project:
        project = project.expanduser()
        if not project.exists():
            typer.echo(f"Project not found: {project}", err=True)
            raise typer.Exit(1)
        looks_sandbox = any(
            token in str(project).lower()
            for token in ("sample-vn", "sandbox")
        )
        if not looks_sandbox:
            typer.echo(
                "WARNING: --deploy writes game/matcha_characters.rpy. "
                "That is dangerous in a live game (Ren'Py auto-loads every "
                "game/*.rpy). Prefer examples/sample-vn, sandbox-renpy, or "
                "--copy-only with a filename template.",
                err=True,
            )

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
        sub = "characters" if images_subdir is None else images_subdir

        formatted = formatter.format_batch(
            work_paths,
            char_config.name,
            poses_done,
            max_width=char_config.resize_max_width,
            max_height=char_config.resize_max_height,
        )
        deployed = deployer.deploy_images(formatted, subfolder=sub)

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
                side_formatted, subfolder=sub
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
        typer.echo(
            "Sandbox deploy: --deploy --project examples/sample-vn. "
            "Echo-style copy (no script): --copy-only --project <sandbox> "
            f"--filename-template '{ECHO_FILENAME_TEMPLATE}'."
        )

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
    typer.echo(f"Edit {example}, then trusted first success (from your Matcha venv):")
    typer.echo(
        f"  .venv/bin/matcha character {example} --lora none "
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
