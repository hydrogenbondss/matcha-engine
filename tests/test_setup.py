"""`matcha setup` checklist + preset YAML integrity."""

from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from matcha import preflight
from matcha.cli import app
from matcha.config import CharacterConfig

OBJECT_INFO = {
    "CheckpointLoaderSimple": {
        "input": {"required": {"ckpt_name": [["anythingV5PrtRE.safetensors"], {}]}}
    },
    "LoraLoader": {
        "input": {"required": {"lora_name": [["style.safetensors"], {}]}}
    },
}

EMPTY_OBJECT_INFO = {
    "CheckpointLoaderSimple": {
        "input": {"required": {"ckpt_name": [["other_model.safetensors"], {}]}}
    },
    "LoraLoader": {"input": {"required": {"lora_name": [[], {}]}}},
}


def _fake_object_info(table):
    def fake(server, node):
        return {node: table[node]}

    return fake


class TestSetupCommand:
    def test_server_down_prints_start_command_and_exits_1(self):
        with mock.patch("matcha.setup.is_server_reachable", return_value=False):
            result = CliRunner().invoke(app, ["setup"])
        assert result.exit_code == 1
        assert "DOWN" in result.stdout
        # Exact Mac MPS start command from the README
        assert "--fp32-vae --cpu-vae --lowvram" in result.stdout
        assert "PYTORCH_MPS_HIGH_WATERMARK_RATIO" in result.stdout
        # Still ends with the trusted-first-success sequence
        assert "--dry-run" in result.stdout
        assert "--lora none" in result.stdout

    def test_server_up_with_checkpoint_present_exits_0(self):
        with mock.patch("matcha.setup.is_server_reachable", return_value=True), \
             mock.patch.object(preflight, "_object_info", _fake_object_info(OBJECT_INFO)):
            result = CliRunner().invoke(app, ["setup"])
        assert result.exit_code == 0
        assert "reachability ... OK" in result.stdout
        assert "anythingV5PrtRE.safetensors" in result.stdout
        assert "PRESENT" in result.stdout
        # Server's LoRA inventory is listed
        assert "style.safetensors" in result.stdout
        # Ends with the trusted-first-success sequence
        assert "curl -s -o /dev/null" in result.stdout
        assert "--lora none --deploy --project examples/sample-vn" in result.stdout

    def test_missing_checkpoint_prints_placement_table_and_exits_1(self):
        with mock.patch("matcha.setup.is_server_reachable", return_value=True), \
             mock.patch.object(preflight, "_object_info", _fake_object_info(EMPTY_OBJECT_INFO)):
            result = CliRunner().invoke(app, ["setup"])
        assert result.exit_code == 1
        assert "MISSING" in result.stdout
        assert "ComfyUI/models/checkpoints/" in result.stdout
        assert "Base family must match" in result.stdout
        assert "docs/verified-models.md" in result.stdout

    def test_checkpoint_flag_overrides_default(self):
        table = {
            "CheckpointLoaderSimple": {
                "input": {"required": {"ckpt_name": [["custom.safetensors"], {}]}}
            },
            "LoraLoader": {"input": {"required": {"lora_name": [[], {}]}}},
        }
        with mock.patch("matcha.setup.is_server_reachable", return_value=True), \
             mock.patch.object(preflight, "_object_info", _fake_object_info(table)):
            result = CliRunner().invoke(app, ["setup", "--checkpoint", "custom.safetensors"])
        assert result.exit_code == 0
        assert "'custom.safetensors' ... PRESENT" in result.stdout

    def test_reachability_helper_tolerates_http_errors(self):
        import urllib.error

        from matcha.setup import is_server_reachable

        def raise_http(*args, **kwargs):
            raise urllib.error.HTTPError("u", 500, "err", {}, None)

        def raise_url(*args, **kwargs):
            raise urllib.error.URLError("refused")

        with mock.patch("urllib.request.urlopen", side_effect=raise_http):
            assert is_server_reachable("127.0.0.1:8188") is True
        with mock.patch("urllib.request.urlopen", side_effect=raise_url):
            assert is_server_reachable("127.0.0.1:8188") is False


PRESETS_DIR = Path(__file__).resolve().parents[1] / "presets"


class TestPresets:
    @pytest.fixture(params=sorted(PRESETS_DIR.glob("*.yaml")), ids=lambda p: p.name)
    def preset(self, request):
        return request.param

    def test_three_presets_exist(self):
        assert len(list(PRESETS_DIR.glob("*.yaml"))) == 3

    def test_preset_loads_and_is_trusted_path(self, preset):
        cfg = CharacterConfig(**yaml.safe_load(preset.read_text()))
        assert cfg.lora is None  # trusted first-success path
        assert (cfg.width, cfg.height) == (512, 512)
        assert 4 <= len(cfg.poses) <= 6
        assert cfg.consistency_denoise == 1.0  # MPS-safe default
        assert cfg.ip_adapter_weight == 0.0

    def test_outfit_families_resolve_for_every_pose(self, preset):
        cfg = CharacterConfig(**yaml.safe_load(preset.read_text()))
        assert cfg.outfit_families, "preset must define outfit families"
        for pose in cfg.poses:
            ov = cfg.pose_overrides.get(pose)
            assert ov is not None, f"{preset.name}: pose '{pose}' has no override"
            assert ov.family or ov.outfit, f"{preset.name}: pose '{pose}' has no outfit"
            if ov.family:
                assert ov.family in cfg.outfit_families, (
                    f"{preset.name}: pose '{pose}' references unknown family "
                    f"'{ov.family}'"
                )
                assert cfg.outfit_for(pose), f"{preset.name}: '{pose}' resolves empty"

    def test_archetypes_are_distinct(self):
        names = {
            CharacterConfig(**yaml.safe_load(p.read_text())).name
            for p in PRESETS_DIR.glob("*.yaml")
        }
        assert len(names) == 3
