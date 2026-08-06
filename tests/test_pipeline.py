import json
from pathlib import Path
from unittest import mock

import pytest

from matcha import preflight
from matcha.config import CharacterConfig
from matcha.errors import GenerationError, PreflightError
from matcha.formatters.renpy import RenPyFormatter
from matcha.deployers.filesystem import FilesystemDeployer
from matcha.generators.comfyui import ComfyUIGenerator


OBJECT_INFO = {
    "CheckpointLoaderSimple": {
        "input": {"required": {"ckpt_name": [["good_model.safetensors"], {}]}}
    },
    "LoraLoader": {
        "input": {"required": {"lora_name": [["style.safetensors"], {}]}}
    },
}


def fake_object_info(server, node):
    return {node: OBJECT_INFO[node]}


class TestPreflight:
    def test_known_models_pass(self):
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            preflight.validate_models("x", "good_model.safetensors", "style.safetensors")

    def test_unknown_checkpoint_fails_with_available_list(self):
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            with pytest.raises(PreflightError, match="anythingV5PrtRE"):
                try:
                    preflight.validate_models("x", "anythingV5PrtRE.safetensors")
                except PreflightError as e:
                    assert "good_model.safetensors" in str(e)
                    raise

    def test_unknown_lora_fails(self):
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            with pytest.raises(PreflightError, match="LoRA 'wrong.safetensors'"):
                preflight.validate_models("x", "good_model.safetensors", "wrong.safetensors")

    def test_no_lora_skips_lora_check(self):
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            preflight.validate_models("x", "good_model.safetensors", None)

    def test_tiny_model_file_rejected(self):
        # The 26-byte sd_xl_base.safetensors case
        with pytest.raises(PreflightError, match="26 bytes"):
            preflight.validate_model_file(26, "sd_xl_base.safetensors")

    def test_real_sized_model_file_accepted(self):
        preflight.validate_model_file(6_600_000_000, "sd_xl_base.safetensors")


class TestConfig:
    def test_yaml_model_fields(self):
        cfg = CharacterConfig(
            name="sakura",
            description="1girl",
            poses=["idle"],
            checkpoint="a.safetensors",
            lora=None,
        )
        assert cfg.checkpoint == "a.safetensors"
        assert cfg.lora is None
        assert cfg.height == 512

    def test_defaults(self):
        cfg = CharacterConfig(name="s", description="d", poses=["idle"])
        assert cfg.checkpoint.endswith(".safetensors")
        assert cfg.lora_strength == 0.7
        assert cfg.lora is None
        assert cfg.height == 512
        assert cfg.width == 512
        assert cfg.ip_adapter_weight == 0.0
        assert cfg.consistency_denoise == 1.0

class TestGeneratorErrorSurfacing:
    def test_execution_error_raises_with_server_message(self):
        gen = ComfyUIGenerator("127.0.0.1:9999")
        frames = [
            json.dumps({"type": "status", "data": {}}),
            json.dumps({"type": "executing", "data": {"node": "10"}}),
            json.dumps({
                "type": "execution_error",
                "data": {
                    "prompt_id": "p1",
                    "node_type": "CheckpointLoaderSimple",
                    "exception_message": "Error while deserializing header",
                },
            }),
        ]
        fake_ws = mock.MagicMock()
        fake_ws.recv.side_effect = frames
        with mock.patch("websocket.WebSocket", return_value=fake_ws):
            with pytest.raises(GenerationError, match="deserializing"):
                gen._wait_for_completion("p1")
        fake_ws.close.assert_called_once()

    def test_clean_completion_returns(self):
        gen = ComfyUIGenerator("127.0.0.1:9999")
        frames = [
            json.dumps({"type": "executing", "data": {"node": "10"}}),
            json.dumps({"type": "executing", "data": {"node": None, "prompt_id": "p1"}}),
        ]
        fake_ws = mock.MagicMock()
        fake_ws.recv.side_effect = frames
        with mock.patch("websocket.WebSocket", return_value=fake_ws):
            gen._wait_for_completion("p1")

    def test_empty_outputs_raise_instead_of_returning_zero_images(self):
        gen = ComfyUIGenerator("127.0.0.1:9999")
        with mock.patch.object(gen, "queue_prompt", return_value={"prompt_id": "p1"}), \
             mock.patch.object(gen, "_wait_for_completion"), \
             mock.patch.object(gen, "get_history", return_value={"p1": {"outputs": {}}}):
            with pytest.raises(GenerationError, match="no images"):
                gen.generate(prompt="x", checkpoint="c.safetensors")

    def test_uses_saveimage_node_14_images(self):
        gen = ComfyUIGenerator("127.0.0.1:9999")
        with mock.patch.object(gen, "queue_prompt", return_value={"prompt_id": "p1"}), \
             mock.patch.object(gen, "_wait_for_completion"), \
             mock.patch.object(gen, "get_history", return_value={
                 "p1": {
                     "outputs": {
                         # Wrong node image should be ignored.
                         "8": {"images": [{"filename": "bad.png", "subfolder": "", "type": "output"}]},
                         # SaveImage node id in our workflow.
                         "14": {"images": [{"filename": "good.png", "subfolder": "", "type": "output"}]},
                     }
                 }
             }), \
             mock.patch.object(gen, "get_image", side_effect=lambda filename, subfolder, folder_type: filename.encode()):
            images = gen.generate(prompt="x", checkpoint="c.safetensors")
            assert images == [b"good.png"]

    def test_workflow_without_lora_skips_loraloader(self):
        gen = ComfyUIGenerator()
        wf = gen.build_workflow("p", "n", "c.safetensors", None, 1.0, 512, 768, 20, 8.0, 1)
        assert "2" not in wf
        assert wf["7"]["inputs"]["model"] == ["10", 0]
        assert wf["6"]["inputs"]["clip"] == ["10", 1]

    def test_workflow_with_lora_routes_through_it(self):
        gen = ComfyUIGenerator()
        wf = gen.build_workflow("p", "n", "c.safetensors", "l.safetensors", 0.8, 512, 768, 20, 8.0, 1)
        assert wf["2"]["inputs"]["lora_name"] == "l.safetensors"
        assert wf["7"]["inputs"]["model"] == ["2", 0]

    def test_workflow_img2img_uses_vae_encode_and_partial_denoise(self):
        gen = ComfyUIGenerator()
        wf = gen.build_workflow(
            "p", "n", "c.safetensors", None, 1.0, 512, 512, 20, 8.0, 1,
            init_image="ref.png", denoise=0.55,
        )
        assert "12" not in wf  # no EmptyLatentImage
        assert wf["20"]["class_type"] == "LoadImage"
        assert wf["21"]["class_type"] == "VAEEncode"
        assert wf["7"]["inputs"]["latent_image"] == ["21", 0]
        assert wf["7"]["inputs"]["denoise"] == 0.55

    def test_workflow_ip_adapter_routes_model_through_advanced_node(self):
        gen = ComfyUIGenerator()
        wf = gen.build_workflow(
            "p", "n", "c.safetensors", "l.safetensors", 0.7, 512, 512, 12, 8.0, 1,
            ip_adapter_image="ref.png",
            ip_adapter_weight=0.65,
            ip_adapter_file="ip-adapter_sd15.safetensors",
            clip_vision="CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors",
        )
        assert wf["30"]["class_type"] == "IPAdapterModelLoader"
        assert wf["31"]["class_type"] == "CLIPVisionLoader"
        assert wf["34"]["class_type"] == "IPAdapterAdvanced"
        assert wf["34"]["inputs"]["model"] == ["2", 0]  # after LoRA
        assert wf["34"]["inputs"]["weight"] == 0.65
        assert wf["7"]["inputs"]["model"] == ["34", 0]
        assert "12" in wf  # still txt2img latent


class TestDeploy:
    def test_deploy_and_script(self, tmp_path):
        project = tmp_path / "vn"
        (project / "game").mkdir(parents=True)
        img = tmp_path / "sakura_idle.png"
        img.write_bytes(b"png")

        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)

        formatted = formatter.format_batch([img], "sakura", ["idle"])
        deployed = deployer.deploy_images(formatted)
        assert deployed[0].name == "sakura_idle.png"
        assert deployed[0].read_bytes() == b"png"

        script = deployer.update_script(
            "sakura", formatter.script_block("sakura", ["idle"])
        )
        text = script.read_text()
        assert 'image sakura idle = "images/characters/sakura_idle.png"' in text
        assert "define sakura = Character" in text

    def test_update_script_is_idempotent_per_character(self, tmp_path):
        project = tmp_path / "vn"
        (project / "game").mkdir(parents=True)
        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)

        deployer.update_script("sakura", formatter.script_block("sakura", ["idle"]))
        deployer.update_script("sakura", formatter.script_block("sakura", ["idle", "happy"]))
        text = deployer.script_path.read_text()
        assert text.count("define sakura = Character") == 1
        assert "image sakura happy" in text

    def test_resize_shrinks_to_fit(self, tmp_path):
        from PIL import Image

        img_path = tmp_path / "sakura_idle.png"
        Image.new("RGBA", (512, 1024)).save(img_path)

        project = tmp_path / "vn"
        (project / "game").mkdir(parents=True)
        formatter = RenPyFormatter(project)
        formatter.format_batch(
            [img_path], "sakura", ["idle"], max_width=1280, max_height=720
        )
        w, h = Image.open(img_path).size
        assert h == 720 and w == 360  # aspect preserved, fits bounds

    def test_resize_never_upscales(self, tmp_path):
        from PIL import Image

        img_path = tmp_path / "sakura_idle.png"
        Image.new("RGBA", (300, 400)).save(img_path)
        RenPyFormatter(tmp_path).resize_for_renpy(img_path, 1280, 720)
        assert Image.open(img_path).size == (300, 400)

    def test_show_statement(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        assert f.generate_show_statement("sakura", "happy") == "show sakura happy at center"

    def test_two_characters_coexist(self, tmp_path):
        project = tmp_path / "vn"
        (project / "game").mkdir(parents=True)
        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)

        deployer.update_script("sakura", formatter.script_block("sakura", ["idle"]))
        deployer.update_script("kenji", formatter.script_block("kenji", ["idle"]))
        text = deployer.script_path.read_text()
        assert "define sakura" in text and "define kenji" in text


class TestRenPyScaffolding:
    def test_layeredimage_groups_poses_with_default(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        block = f.script_block("sakura", ["idle", "happy"], layered=True)
        assert "layeredimage sakura:" in block
        assert "group pose:" in block
        assert 'attribute idle default "images/characters/sakura_idle.png"' in block
        assert 'attribute happy "images/characters/sakura_happy.png"' in block
        # Layered mode replaces the flat `image <char> <pose>` definitions.
        assert "image sakura idle =" not in block

    def test_side_image_defs_and_character_wiring(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        block = f.script_block("sakura", ["idle", "happy"], side_image=True)
        assert 'define sakura = Character("Sakura", image="sakura")' in block
        assert 'image side sakura idle = "images/characters/sakura_idle_side.png"' in block
        assert 'image side sakura happy = "images/characters/sakura_happy_side.png"' in block
        # Full sprites stay for main show; side defs must not reuse them.
        assert 'image side sakura idle = "images/characters/sakura_idle.png"' not in block

    def test_display_name_and_color(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        block = f.script_block(
            "sakura", ["idle"], display_name="Sakura Kinomoto", color="#ffcc00"
        )
        assert 'define sakura = Character("Sakura Kinomoto", color="#ffcc00")' in block

    def test_layered_and_side_image_combine(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        block = f.script_block("sakura", ["idle", "happy"], layered=True, side_image=True)
        assert "layeredimage sakura:" in block
        assert 'attribute idle default "images/characters/sakura_idle.png"' in block
        assert 'image side sakura happy = "images/characters/sakura_happy_side.png"' in block
        assert 'define sakura = Character("Sakura", image="sakura")' in block

    def test_default_output_is_unchanged(self, tmp_path):
        f = RenPyFormatter(tmp_path)
        block = f.script_block("sakura", ["idle", "happy"])
        assert 'define sakura = Character("Sakura")' in block
        assert 'image sakura idle = "images/characters/sakura_idle.png"' in block
        assert "layeredimage" not in block
        assert "image side" not in block

    def test_config_defaults_for_scaffolding(self):
        cfg = CharacterConfig(name="s", description="d", poses=["idle"])
        assert cfg.layered is False
        assert cfg.side_image is False
        assert cfg.side_image_height_ratio == 0.45
        assert cfg.display_name is None
        assert cfg.color is None

    def test_crop_side_portrait_top_fraction(self, tmp_path):
        from PIL import Image

        src = tmp_path / "sakura_idle.png"
        # Distinct top/bottom bands so we can verify which region was kept.
        img = Image.new("RGB", (200, 400), (0, 0, 255))  # blue bottom
        for y in range(180):
            for x in range(200):
                img.putpixel((x, y), (255, 0, 0))  # red top
        img.save(src)

        dest = tmp_path / "sakura_idle_side.png"
        RenPyFormatter(tmp_path).crop_side_portrait(src, dest, height_ratio=0.45)
        out = Image.open(dest)
        assert out.size == (200, 180)  # 400 * 0.45
        assert out.getpixel((100, 0)) == (255, 0, 0)
        assert out.getpixel((100, 179)) == (255, 0, 0)

    def test_format_side_images_names_and_deploys(self, tmp_path):
        from PIL import Image

        project = tmp_path / "vn"
        (project / "game").mkdir(parents=True)
        idle = tmp_path / "sakura_idle.png"
        happy = tmp_path / "sakura_happy.png"
        Image.new("RGBA", (100, 200), (200, 100, 150, 255)).save(idle)
        Image.new("RGBA", (100, 200), (200, 100, 150, 255)).save(happy)

        formatter = RenPyFormatter(project)
        deployer = FilesystemDeployer(project)
        side = formatter.format_side_images(
            [idle, happy], "sakura", ["idle", "happy"], height_ratio=0.5
        )
        assert [fn for _, fn in side] == [
            "sakura_idle_side.png",
            "sakura_happy_side.png",
        ]
        deployed = deployer.deploy_images(side, subfolder="characters")
        assert deployed[0].name == "sakura_idle_side.png"
        assert Image.open(deployed[0]).size == (100, 100)

        block = formatter.script_block("sakura", ["idle", "happy"], side_image=True)
        deployer.update_script("sakura", block)
        text = deployer.script_path.read_text()
        assert "sakura_idle_side.png" in text
        assert 'image sakura idle = "images/characters/sakura_idle.png"' in text


class TestPrompts:
    def test_pose_prompt_locks_framing_and_varies_expression(self):
        from matcha.prompts import build_pose_prompt

        idle = build_pose_prompt("1girl, pink hair, black jumper", "idle")
        happy = build_pose_prompt("1girl, pink hair, black jumper", "happy")
        assert "pink hair" in idle and "pink hair" in happy
        assert "single character" in idle
        assert "neutral" in idle or "calm" in idle
        assert "smile" in happy or "happy" in happy
        assert idle != happy

    def test_negative_prompt_appends_consistency_terms(self):
        from matcha.prompts import build_negative_prompt

        neg = build_negative_prompt("low quality")
        assert neg.startswith("low quality")
        assert "reference sheet" in neg
        assert "multiple views" in neg


class TestImageSanity:
    def test_black_image_rejected(self):
        from io import BytesIO

        from PIL import Image

        from matcha.images import assert_usable_image

        buf = BytesIO()
        Image.new("RGB", (512, 512), (0, 0, 0)).save(buf, format="PNG")
        with pytest.raises(GenerationError, match="--lora none"):
            assert_usable_image(buf.getvalue(), label="idle")

    def test_tiny_image_rejected(self):
        from matcha.images import assert_usable_image

        with pytest.raises(GenerationError, match="cannot decode"):
            assert_usable_image(b"not-a-real-png", label="idle")

    def test_normal_image_accepted(self):
        from io import BytesIO

        from PIL import Image

        from matcha.images import assert_usable_image

        buf = BytesIO()
        # Non-trivial colors so it isn't flagged as black.
        Image.new("RGB", (512, 512), (180, 120, 160)).save(buf, format="PNG")
        assert_usable_image(buf.getvalue(), label="idle")

    def test_empty_bytes_rejected(self):
        from matcha.images import assert_usable_image

        with pytest.raises(GenerationError, match="empty image"):
            assert_usable_image(b"", label="idle")


class TestCliFirstRun:
    def test_init_writes_lora_null_and_tips_lora_none(self, tmp_path, monkeypatch):
        from typer.testing import CliRunner

        from matcha.cli import app

        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["init", "demo"])
        assert result.exit_code == 0
        yaml_text = (tmp_path / "demo" / "configs" / "example_character.yaml").read_text()
        assert "lora: null" in yaml_text
        assert "--lora none" in result.stdout

    def test_lora_override_none_and_tip_when_yaml_has_lora(self, tmp_path):
        from typer.testing import CliRunner

        from matcha import preflight
        from matcha.cli import app

        cfg = tmp_path / "char.yaml"
        cfg.write_text(
            "name: s\ndescription: d\nposes: [idle]\n"
            "checkpoint: good_model.safetensors\nlora: style.safetensors\n"
        )
        runner = CliRunner()
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            result = runner.invoke(
                app,
                ["character", str(cfg), "--dry-run", "--lora", "none"],
            )
        assert result.exit_code == 0
        assert "LoRA: (none)" in result.stdout
        assert "trusted first-success" in result.stdout.lower() or "Trusted" in result.stdout or "no LoRA" in result.stdout

    def test_tip_when_lora_set_on_dry_run(self, tmp_path):
        from typer.testing import CliRunner

        from matcha import preflight
        from matcha.cli import app

        cfg = tmp_path / "char.yaml"
        cfg.write_text(
            "name: s\ndescription: d\nposes: [idle]\n"
            "checkpoint: good_model.safetensors\nlora: style.safetensors\n"
        )
        runner = CliRunner()
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            result = runner.invoke(app, ["character", str(cfg), "--dry-run"])
        assert result.exit_code == 0
        assert "--lora none" in result.stdout
        assert "Next: generate with --lora none" in result.stdout

    def test_warns_when_ipa_enabled(self, tmp_path):
        from typer.testing import CliRunner

        from matcha import preflight
        from matcha.cli import app

        cfg = tmp_path / "char.yaml"
        cfg.write_text(
            "name: s\ndescription: d\nposes: [idle]\n"
            "checkpoint: good_model.safetensors\nlora: null\n"
            "ip_adapter_weight: 0.5\n"
        )
        runner = CliRunner()
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            # IPA preflight needs IPAdapterModelLoader — patch validate to skip IPA
            with mock.patch.object(preflight, "validate_models"):
                result = runner.invoke(app, ["character", str(cfg), "--dry-run"])
        assert result.exit_code == 0
        assert "WARNING" in result.output
        assert "IP-Adapter" in result.output

    def test_preflight_unreachable_mentions_health_check(self):
        with mock.patch.object(
            preflight.urllib.request,
            "urlopen",
            side_effect=OSError("Connection refused"),
        ):
            with pytest.raises(PreflightError, match="Health-check"):
                preflight.validate_models("127.0.0.1:8188", "good_model.safetensors")

    def test_queue_prompt_unreachable_is_generation_error(self):
        gen = ComfyUIGenerator("127.0.0.1:1")
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=OSError("Connection refused"),
        ):
            with pytest.raises(GenerationError, match="Cannot reach ComfyUI"):
                gen.queue_prompt({"1": {}})
