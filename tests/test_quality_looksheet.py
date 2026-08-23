"""Quality guard, look-sheet prompts, incremental CLI, copy-only deploy."""

from __future__ import annotations

import io
import json
import math
import random
from pathlib import Path
from unittest import mock

import pytest
from PIL import Image, ImageDraw, ImageFilter

from matcha.cli import (
    ECHO_FILENAME_TEMPLATE,
    app,
    copy_only_template,
    is_love32_project,
    parse_poses_flag,
    render_filename,
)
from matcha.config import CharacterConfig
from matcha.errors import GenerationError
from matcha.images import (
    ImageQualityError,
    assert_usable_image,
    knockout_near_black,
    pad_to_canvas,
    persist_rejection,
)
from matcha.prompts import POSE_EXPRESSIONS, build_pose_prompt, pose_expression


def _png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def make_cel_sprite(size: int = 512) -> bytes:
    """Sharp outlines + flat fills — a stand-in for a clean cel sprite."""
    im = Image.new("RGB", (size, size), (236, 230, 220))
    d = ImageDraw.Draw(im)
    d.ellipse([170, 28, 342, 210], fill=(236, 198, 168), outline=(36, 24, 18), width=5)
    d.ellipse([160, 20, 350, 120], fill=(52, 36, 28), outline=(20, 12, 8), width=4)
    d.rectangle([168, 220, 344, 490], fill=(248, 248, 246), outline=(28, 28, 28), width=5)
    d.polygon([(188, 280), (324, 280), (340, 490), (172, 490)], fill=(32, 32, 40))
    d.ellipse([208, 98, 236, 132], fill=(70, 42, 18), outline=(16, 8, 4), width=3)
    d.ellipse([276, 98, 304, 132], fill=(70, 42, 18), outline=(16, 8, 4), width=3)
    d.line([(230, 168), (282, 168)], fill=(80, 40, 36), width=3)
    return _png_bytes(im)


def make_smear_static(size: int = 512, *, seed: int = 0) -> bytes:
    """Left smear + a right-edge high-frequency static band."""
    im = Image.new("RGB", (size, size))
    px = im.load()
    split = int(size * 0.78)
    for y in range(size):
        for x in range(split):
            t = (x / size) + (y / size)
            px[x, y] = (
                int(88 + 36 * math.sin(t * 2.1)),
                int(74 + 28 * math.sin(t * 1.4 + 0.3)),
                int(96 + 22 * math.cos(t * 1.7)),
            )
    left = im.crop((0, 0, split, size)).filter(ImageFilter.GaussianBlur(14))
    im.paste(left, (0, 0))
    rng = random.Random(seed)
    for y in range(size):
        for x in range(split, size):
            choice = rng.randrange(4)
            if choice == 0:
                px[x, y] = (255, 255, 255)
            elif choice == 1:
                px[x, y] = (0, 30, 70)
            elif choice == 2:
                px[x, y] = (0, 220, 255)
            else:
                px[x, y] = (10, 10, 12)
    return _png_bytes(im)


class TestQualityGuard:
    def test_smear_static_band_rejected(self):
        data = make_smear_static()
        with pytest.raises(ImageQualityError, match="static-band|smear") as exc:
            assert_usable_image(data, label="idle")
        metrics = exc.value.metrics
        assert metrics["verdict"] == "reject"
        assert metrics["static_band_ratio"] >= 1.5
        assert metrics["right_adj"] > metrics["interior_adj"]

    def test_cel_sprite_accepted(self):
        metrics = assert_usable_image(make_cel_sprite(), label="idle")
        assert metrics.verdict == "ok"
        assert metrics.interior_edge > 16

    def test_solid_color_still_accepted(self):
        buf = io.BytesIO()
        Image.new("RGB", (512, 512), (180, 120, 160)).save(buf, format="PNG")
        assert_usable_image(buf.getvalue(), label="idle")

    def test_persist_rejection_writes_png_and_metrics(self, tmp_path):
        data = make_smear_static()
        with pytest.raises(ImageQualityError) as exc:
            assert_usable_image(data, label="warm")
        dest = tmp_path / "rejected" / "kite_male_warm_seed42.png"
        sidecar = persist_rejection(
            exc.value.data,
            exc.value.metrics,
            dest,
            extra={"pose": "warm", "seed": 42},
        )
        assert dest.exists() and dest.stat().st_size > 0
        payload = json.loads(sidecar.read_text())
        assert payload["pose"] == "warm"
        assert payload["seed"] == 42
        assert payload["metrics"]["verdict"] == "reject"
        assert "right_adj" in payload["metrics"]

    def test_knockout_black_makes_bg_transparent(self):
        im = Image.new("RGB", (32, 32), (0, 0, 0))
        im.putpixel((16, 16), (200, 40, 40))
        out = Image.open(io.BytesIO(knockout_near_black(_png_bytes(im)))).convert(
            "RGBA"
        )
        assert out.getpixel((0, 0))[3] == 0
        assert out.getpixel((16, 16))[3] == 255

    def test_pad_to_canvas_centers_and_does_not_shrink(self):
        src = Image.new("RGBA", (64, 64), (10, 20, 30, 255))
        out = Image.open(io.BytesIO(pad_to_canvas(_png_bytes(src), 128, 96)))
        assert out.size == (128, 96)
        assert out.getpixel((64, 48))[:3] == (10, 20, 30)
        with pytest.raises(GenerationError, match="smaller"):
            pad_to_canvas(_png_bytes(src), 32, 32)


class TestLookSheet:
    def test_unknown_pose_does_not_invent_expression_pose_template(self):
        text = pose_expression("custom_wave")
        assert "custom_wave expression, custom_wave pose" not in text
        assert text == "custom wave"
        prompt = build_pose_prompt("1boy, buzz cut", "custom_wave")
        assert "custom_wave expression, custom_wave pose" not in prompt

    def test_echo_pose_names_are_in_the_map(self):
        for name in (
            "neutral",
            "warm",
            "withdrawn",
            "smoking",
            "relaxed",
            "soft",
            "tired",
            "stressed",
            "gentle",
            "crossed_arms",
        ):
            assert name in POSE_EXPRESSIONS
            assert "expression, " + name + " pose" not in pose_expression(name)

    def test_outfit_override_does_not_lock_same_outfit(self):
        from matcha.config import PoseOverride

        smoking = build_pose_prompt(
            "1boy, buzz-cut brown hair, amber eyes",
            "smoking",
            PoseOverride(
                outfit="dark henley shirt, no apron, no bartender outfit",
                prompt="holding a small flame",
            ),
        )
        idle = build_pose_prompt(
            "1boy, buzz-cut brown hair, amber eyes",
            "idle",
            PoseOverride(outfit="white bartender shirt, black apron"),
        )
        assert "dark henley" in smoking
        assert "bartender apron" not in smoking or "no bartender" in smoking
        assert "same outfit" not in smoking
        assert "black apron" in idle
        assert "holding a small flame" in smoking

    def test_inline_pose_mapping_normalized(self):
        cfg = CharacterConfig(
            name="kite_male",
            description="1boy, buzz cut",
            poses=[
                "idle",
                {
                    "name": "smoking",
                    "outfit": "dark henley",
                    "prompt": "holding a flame",
                },
            ],
        )
        assert cfg.poses == ["idle", "smoking"]
        assert cfg.pose_overrides["smoking"].outfit == "dark henley"
        assert cfg.pose_overrides["smoking"].prompt == "holding a flame"

    def test_kite_yaml_matches_live_echo_disk_spec(self):
        import yaml

        path = Path(__file__).resolve().parents[1] / "configs" / "kite_male.yaml"
        data = yaml.safe_load(path.read_text())
        cfg = CharacterConfig(**data)
        assert cfg.name == "kite_male"
        assert cfg.filename_template == "{name} {pose}.png"
        assert cfg.poses == [
            "neutral",
            "gentle",
            "relaxed",
            "smoking",
            "soft",
            "stressed",
            "tired",
            "warm",
            "withdrawn",
            "crossed_arms",
        ]
        assert "idle" not in cfg.poses
        assert "angry" not in cfg.poses
        assert cfg.pose_aliases.get("angry") == "stressed"
        assert set(cfg.outfit_families) == {
            "apron_bar",
            "home_henley",
            "withdrawn_dark",
        }
        bar = {
            "neutral",
            "warm",
            "soft",
            "stressed",
            "tired",
            "gentle",
        }
        henley = {"relaxed", "smoking"}
        withdrawn = {"withdrawn", "crossed_arms"}
        assert bar | henley | withdrawn == set(cfg.poses)
        for pose in bar:
            assert cfg.pose_overrides[pose].family == "apron_bar"
            assert "apron" in (cfg.outfit_for(pose) or "")
            assert "charcoal" in (cfg.outfit_for(pose) or "")
        for pose in henley:
            assert cfg.pose_overrides[pose].family == "home_henley"
            outfit = cfg.outfit_for(pose) or ""
            assert "henley" in outfit or "polo" in outfit
            assert "no apron" in outfit
        for pose in withdrawn:
            assert cfg.pose_overrides[pose].family == "withdrawn_dark"
            outfit = cfg.outfit_for(pose) or ""
            assert "oversized" in outfit and "no apron" in outfit
        smoking = build_pose_prompt(
            cfg.description, "smoking", cfg.pose_overrides["smoking"],
            outfit=cfg.outfit_for("smoking"),
        )
        assert "cigarette" in smoking
        assert "ledge" in smoking
        assert "apron" not in smoking or "no apron" in smoking
        assert "same outfit" not in smoking
        assert render_filename(cfg.filename_template, cfg.name, "neutral") == (
            "kite_male neutral.png"
        )
        assert render_filename(cfg.filename_template, cfg.name, "crossed_arms") == (
            "kite_male crossed_arms.png"
        )
        assert cfg.width == 512 and cfg.height == 512
        assert cfg.lora is None
        assert cfg.ip_adapter_weight == 0
        assert cfg.consistency_denoise == 1.0


class TestCliHelpers:
    def test_parse_poses_flag_subset_and_unknown(self):
        available = ["idle", "warm", "smoking"]
        assert parse_poses_flag(None, available) == available
        assert parse_poses_flag("smoking", available) == ["smoking"]
        assert parse_poses_flag("idle,smoking", available) == ["idle", "smoking"]
        with pytest.raises(ValueError, match="unknown pose"):
            parse_poses_flag("dance", available)

    def test_parse_poses_flag_aliases_angry_to_stressed(self):
        available = [
            "neutral",
            "stressed",
            "smoking",
        ]
        aliases = {"angry": "stressed"}
        assert parse_poses_flag("angry", available, aliases) == ["stressed"]
        assert parse_poses_flag("angry,stressed", available, aliases) == ["stressed"]
        assert parse_poses_flag("smoking", available, aliases) == ["smoking"]

    def test_render_filename_echo_space_template(self):
        assert (
            render_filename(ECHO_FILENAME_TEMPLATE, "kite_male", "neutral")
            == "kite_male neutral.png"
        )
        assert (
            render_filename("{name}_{pose}.png", "kite_male", "warm")
            == "kite_male_warm.png"
        )
        assert copy_only_template(None, None) == ECHO_FILENAME_TEMPLATE
        assert (
            copy_only_template(None, "{name} {pose}.png") == "{name} {pose}.png"
        )

    def test_love32_paths_detected(self, tmp_path):
        assert is_love32_project(Path("/Users/me/Desktop/LOVE32/LOVE32"))
        assert is_love32_project(tmp_path / "love32-backup")
        # tmp_path itself may contain the test name; use a sibling sandbox.
        assert not is_love32_project(tmp_path / "sandbox-kite")
        assert not is_love32_project(Path("examples/sample-vn"))
        assert not is_love32_project(Path("/tmp/sandbox-kite"))


def _write_char_yaml(path: Path, poses=None, extra=""):
    poses = poses or ["idle", "happy"]
    pose_block = "\n".join(f"  - {p}" for p in poses)
    path.write_text(
        "name: kite_male\n"
        "description: 1boy, buzz cut\n"
        "poses:\n"
        f"{pose_block}\n"
        "checkpoint: good_model.safetensors\n"
        "lora: null\n"
        f"output_dir: {path.parent / 'out'}\n"
        f"{extra}"
    )
    return path


def _patch_preflight():
    return mock.patch("matcha.cli.preflight.validate_models")


class TestCliGenerateLoop:
    def test_help_lists_new_flags(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(app, ["character", "--help"])
        assert result.exit_code == 0
        for flag in (
            "--poses",
            "--copy-only",
            "--filename-template",
            "--force",
            "--retries",
            "--knockout-black",
            "--canvas",
        ):
            assert flag in result.stdout

    def test_dry_run_poses_subset(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle", "warm", "smoking"])
        with _patch_preflight():
            result = CliRunner().invoke(
                app,
                ["character", str(cfg), "--dry-run", "--poses", "smoking"],
            )
        assert result.exit_code == 0
        assert "Poses: smoking" in result.stdout
        assert "YAML list: idle, warm, smoking" in result.stdout

    def test_incremental_write_survives_later_failure(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle", "happy"])
        clean = make_cel_sprite()

        def fake_generate(**kwargs):
            prompt = kwargs.get("prompt") or ""
            if "happy" in prompt or "smile" in prompt:
                raise GenerationError("ComfyUI died mid-pose")
            return [clean]

        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", side_effect=fake_generate
        ):
            result = CliRunner().invoke(app, ["character", str(cfg), "--lora", "none"])
        assert result.exit_code == 2
        saved = tmp_path / "out" / "kite_male_idle.png"
        assert saved.exists()
        assert saved.read_bytes() == clean
        assert not (tmp_path / "out" / "kite_male_happy.png").exists()

    def test_quality_reject_is_dumped_and_retried(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        smear = make_smear_static()
        clean = make_cel_sprite()
        calls = {"n": 0}

        def fake_generate(**kwargs):
            calls["n"] += 1
            return [smear if calls["n"] == 1 else clean]

        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", side_effect=fake_generate
        ):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--lora", "none", "--retries", "2"]
            )
        assert result.exit_code == 0, result.output
        assert calls["n"] == 2
        assert (tmp_path / "out" / "kite_male_idle.png").exists()
        rejected = list((tmp_path / "out" / "rejected").glob("*.png"))
        assert rejected
        sidecar = rejected[0].with_suffix(".json")
        assert sidecar.exists()
        payload = json.loads(sidecar.read_text())
        assert payload["pose"] == "idle"
        assert payload["metrics"]["verdict"] == "reject"

    def test_skip_existing_accepted(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        out = tmp_path / "out"
        out.mkdir()
        existing = make_cel_sprite()
        (out / "kite_male_idle.png").write_bytes(existing)
        generate = mock.Mock(side_effect=AssertionError("should not generate"))
        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", generate
        ):
            result = CliRunner().invoke(app, ["character", str(cfg), "--lora", "none"])
        assert result.exit_code == 0, result.output
        assert generate.call_count == 0
        assert "Skipping idle" in result.stdout

    def test_copy_only_uses_template_and_skips_script(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        project = tmp_path / "sandbox-vn"
        (project / "game").mkdir(parents=True)
        clean = make_cel_sprite()
        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", return_value=[clean]
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--lora",
                    "none",
                    "--copy-only",
                    "--project",
                    str(project),
                    "--filename-template",
                    ECHO_FILENAME_TEMPLATE,
                ],
            )
        assert result.exit_code == 0, result.output
        copied = project / "game" / "images" / "kite_male idle.png"
        assert copied.exists()
        assert copied.read_bytes() == clean
        assert not (project / "game" / "matcha_characters.rpy").exists()
        assert "No Character()" in result.stdout
        assert "_kite_sprite" in result.stdout
        assert "kite_male_idle.png" not in result.stdout

    def test_copy_only_default_is_echo_space_name(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["smoking"])
        project = tmp_path / "sandbox-vn"
        (project / "game").mkdir(parents=True)
        clean = make_cel_sprite()
        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", return_value=[clean]
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--lora",
                    "none",
                    "--copy-only",
                    "--project",
                    str(project),
                ],
            )
        assert result.exit_code == 0, result.output
        assert (project / "game" / "images" / "kite_male smoking.png").exists()
        assert not (project / "game" / "images" / "kite_male_smoking.png").exists()
        assert not (project / "game" / "images" / "kite_smoking.png").exists()
        assert not (project / "game" / "matcha_characters.rpy").exists()
        text = result.stdout + result.output
        assert "Character(" not in text or "No Character()" in text
        assert "_kite_sprite" in result.stdout

    def test_copy_only_kite_yaml_template_and_angry_alias(self, tmp_path):
        from typer.testing import CliRunner

        cfg = tmp_path / "kite_male.yaml"
        cfg.write_text(
            "name: kite_male\n"
            "description: 1boy, buzz cut\n"
            "filename_template: \"{name} {pose}.png\"\n"
            "poses: [neutral, stressed, smoking, crossed_arms]\n"
            "pose_aliases:\n  angry: stressed\n"
            "outfit_families:\n"
            "  apron_bar: charcoal shirt, dark buckle apron\n"
            "  home_henley: olive henley, no apron\n"
            "pose_overrides:\n"
            "  stressed:\n    family: apron_bar\n"
            "  smoking:\n    family: home_henley\n"
            "checkpoint: good_model.safetensors\n"
            "lora: null\n"
            f"output_dir: {tmp_path / 'out'}\n"
        )
        project = tmp_path / "sandbox-vn"
        (project / "game").mkdir(parents=True)
        clean = make_cel_sprite()
        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate", return_value=[clean]
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--lora",
                    "none",
                    "--poses",
                    "angry",
                    "--copy-only",
                    "--project",
                    str(project),
                ],
            )
        assert result.exit_code == 0, result.output
        assert "Poses: stressed" in result.stdout
        dest = project / "game" / "images" / "kite_male stressed.png"
        assert dest.exists()
        assert not (project / "game" / "images" / "kite_male angry.png").exists()
        assert not (project / "game" / "matcha_characters.rpy").exists()
        local = tmp_path / "out" / "kite_male stressed.png"
        assert local.exists()

    def test_copy_only_refuses_love32(self, tmp_path):
        from typer.testing import CliRunner

        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        project = tmp_path / "LOVE32" / "LOVE32"
        (project / "game").mkdir(parents=True)
        with _patch_preflight(), mock.patch(
            "matcha.cli.ComfyUIGenerator.generate",
            return_value=[make_cel_sprite()],
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--copy-only",
                    "--project",
                    str(project),
                ],
            )
        assert result.exit_code == 1
        assert "LOVE32" in result.output
        assert not list((project / "game").rglob("*.png"))
        assert not (project / "game" / "matcha_characters.rpy").exists()
