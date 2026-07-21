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
        assert cfg.height == 768

    def test_defaults(self):
        cfg = CharacterConfig(name="s", description="d", poses=["idle"])
        assert cfg.checkpoint.endswith(".safetensors")
        assert cfg.lora_strength == 1.0


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
        assert 'image side sakura idle = "images/characters/sakura_idle.png"' in block
        assert 'image side sakura happy = "images/characters/sakura_happy.png"' in block

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
        assert 'image side sakura happy = "images/characters/sakura_happy.png"' in block
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
        assert cfg.display_name is None
        assert cfg.color is None
