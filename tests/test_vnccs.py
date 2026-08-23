"""VNCCS backend: real upstream node types, no silent prompt+seed fallback."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from matcha import preflight
from matcha.cli import app
from matcha.config import CharacterConfig
from matcha.errors import PreflightError
from matcha.vnccs import (
    INSTALL_HINT,
    MPS_VNCCS_HINT,
    NODE_CHARACTER_CLONE_GENERATOR,
    NODE_CHARACTER_CLONER,
    NODE_CHARACTER_CREATOR,
    NODE_CHARACTER_GENERATOR,
    NODE_CLOTHES_DESIGNER,
    NODE_CLOTHES_GENERATOR,
    NODE_CONTROL_CENTER,
    NODE_POSE_STUDIO,
    REFERENCE_COPY_HINT,
    build_step1_cloner_prompt,
    build_step1_creator_prompt,
    build_step2_clothes_prompt,
    character_info_from_config,
    workflow_class_types,
)

from tests.test_pipeline import OBJECT_INFO, fake_object_info
from tests.test_quality_looksheet import (
    _write_char_yaml,
    make_cel_sprite,
)


VNCCS_OBJECT_INFO = {
    **OBJECT_INFO,
    NODE_CONTROL_CENTER: {"input": {"required": {}}},
    NODE_CHARACTER_CREATOR: {"input": {"required": {}}},
    NODE_CHARACTER_GENERATOR: {"input": {"required": {}}},
    NODE_POSE_STUDIO: {"input": {"required": {}}},
    NODE_CLOTHES_DESIGNER: {"input": {"required": {}}},
    NODE_CLOTHES_GENERATOR: {"input": {"required": {}}},
    NODE_CHARACTER_CLONER: {"input": {"required": {}}},
    NODE_CHARACTER_CLONE_GENERATOR: {"input": {"required": {}}},
}


def vnccs_object_info(server, node):
    if node not in VNCCS_OBJECT_INFO:
        return {}
    return {node: VNCCS_OBJECT_INFO[node]}


def txt2img_only_object_info(server, node):
    """Models present, VNCCS nodes absent — do not KeyError on unknown names."""
    if node not in OBJECT_INFO:
        return {}
    return {node: OBJECT_INFO[node]}


def _kite_cfg(**kwargs) -> CharacterConfig:
    data = dict(
        name="kite_male",
        description=(
            "1boy, young man, tan skin, very short dark olive-grey buzz cut, "
            "reddish-orange eyes"
        ),
        poses=["neutral", "smoking"],
        checkpoint="anythingV5PrtRE.safetensors",
        outfit_families={
            "apron_bar": "charcoal shirt, dark buckle apron",
            "home_henley": "olive henley, no apron",
        },
        pose_overrides={
            "neutral": {"family": "apron_bar"},
            "smoking": {
                "family": "home_henley",
                "prompt": "seated on a ledge, holding a cigarette",
            },
        },
    )
    data.update(kwargs)
    return CharacterConfig(**data)


class TestVNCCSPreflight:
    def test_missing_nodes_are_an_error_with_install_hint(self):
        with mock.patch.object(preflight, "_object_info", txt2img_only_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={}
        ):
            with pytest.raises(PreflightError, match="VNCCS") as exc:
                preflight.validate_vnccs("127.0.0.1:8188")
        text = str(exc.value)
        assert NODE_CONTROL_CENTER in text
        assert NODE_POSE_STUDIO in text
        assert "ComfyUI Manager" in text
        assert "will not silently fall back" in text
        assert "prompt+seed" in text
        assert INSTALL_HINT.splitlines()[0] in text

    def test_present_nodes_pass(self):
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={"devices": [{"type": "cpu"}]}
        ):
            status = preflight.validate_vnccs("x")
        assert status.required_ok
        assert status.clothes_ok
        assert status.cloner_ok
        assert status.creator_ok
        assert status.device == "cpu"
        assert status.used_cloner is False

    def test_mps_fails_preflight_unless_allow_mps(self):
        mps_stats = {"devices": [{"type": "mps", "name": "mps"}]}
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value=mps_stats
        ):
            with pytest.raises(PreflightError, match="Apple Silicon MPS") as exc:
                preflight.validate_vnccs("x")
            assert "will not silently fall back" in str(exc.value)
            assert "txt2img" in str(exc.value)
            assert MPS_VNCCS_HINT.splitlines()[0] in str(exc.value)
            status = preflight.validate_vnccs("x", allow_mps=True)
        assert status.required_ok
        assert status.device == "mps"

    def test_cloner_flag_requires_cloner_nodes(self):
        def no_cloner(server, node):
            if node in (NODE_CHARACTER_CLONER, NODE_CHARACTER_CLONE_GENERATOR):
                return {}
            return vnccs_object_info(server, node)

        with mock.patch.object(preflight, "_object_info", no_cloner), mock.patch.object(
            preflight, "fetch_system_stats", return_value={}
        ):
            with pytest.raises(PreflightError, match="Character Cloner"):
                preflight.validate_vnccs("x", require_cloner=True)

    def test_yaml_reference_field_is_optional_path(self):
        cfg = _kite_cfg(reference=Path("./refs/kite_male_neutral.png"))
        assert cfg.reference == Path("./refs/kite_male_neutral.png")

    def test_device_kind_mps_from_name_or_type(self):
        assert preflight.device_kind({"devices": [{"type": "mps"}]}) == "mps"
        assert preflight.device_kind({"devices": [{"name": "Metal"}]}) == "mps"
        assert preflight.device_kind({"devices": [{"type": "cuda"}]}) == "cuda"
        assert preflight.device_kind({}) == "unknown"

    def test_404_counts_as_missing_not_unreachable(self):
        import urllib.error

        # node_registered uses _object_info, which now maps 404 → {}
        with mock.patch.object(
            preflight.urllib.request,
            "urlopen",
            side_effect=urllib.error.HTTPError(
                "http://x/object_info/VNCCS_ControlCenter",
                404,
                "Not Found",
                hdrs=None,
                fp=None,
            ),
        ):
            assert preflight.node_registered("x", NODE_CONTROL_CENTER) is False


class TestVNCCSWorkflow:
    def test_step1_uses_verified_vnccs_nodes_not_ksampler_only(self):
        cfg = _kite_cfg()
        wf = build_step1_creator_prompt(cfg, "smoking", seed=42)
        types = workflow_class_types(wf)
        assert NODE_CONTROL_CENTER in types
        assert NODE_CHARACTER_CREATOR in types
        assert NODE_POSE_STUDIO in types
        assert NODE_CHARACTER_GENERATOR in types
        assert "SaveImage" in types
        # The old txt2img graph is CheckpointLoaderSimple + KSampler.
        assert "CheckpointLoaderSimple" not in types
        assert "KSampler" not in types
        assert "IPAdapterAdvanced" not in types
        gen = wf["798"]
        assert gen["class_type"] == NODE_CHARACTER_GENERATOR
        assert gen["inputs"]["pipe"] == ["812", 0]
        assert gen["inputs"]["poses"] == ["703", 0]
        assert gen["inputs"]["character"] == ["797", 0]
        creator = wf["797"]
        payload = creator["inputs"]["widget_data"]
        assert "kite_male" in payload
        assert "buzz cut" in payload
        assert "olive henley" in payload
        pose_data = wf["703"]["inputs"]["pose_data"]
        assert "captured_images" in pose_data
        assert "Draw character from image2" in pose_data

    def test_cloner_graph_uses_character_cloner_not_ipa(self):
        cfg = _kite_cfg()
        wf = build_step1_cloner_prompt(
            cfg, "neutral", "ref.png", seed=1
        )
        types = workflow_class_types(wf)
        assert NODE_CHARACTER_CLONER in types
        assert NODE_CHARACTER_CLONE_GENERATOR in types
        assert NODE_CONTROL_CENTER in types
        assert NODE_POSE_STUDIO in types
        assert "IPAdapterAdvanced" not in types
        assert "IPAdapterModelLoader" not in types
        assert wf["774"]["inputs"]["widget_data"]
        assert "ref.png" in wf["774"]["inputs"]["widget_data"]

    def test_clothes_graph_uses_clothes_designer(self):
        cfg = _kite_cfg()
        wf = build_step2_clothes_prompt(
            cfg, "neutral", "charcoal shirt, dark buckle apron"
        )
        types = workflow_class_types(wf)
        assert NODE_CLOTHES_DESIGNER in types
        assert NODE_CLOTHES_GENERATOR in types
        assert NODE_CONTROL_CENTER in types
        assert NODE_POSE_STUDIO in types
        assert "KSampler" not in types

    def test_kite_identity_maps_to_creator_fields(self):
        info = character_info_from_config(_kite_cfg(), pose="smoking")
        assert info["sex"] == "male"
        assert info["age"] == 22
        assert "buzz" in info["hair"]
        assert "orange" in info["eyes"] or "eye" in info["eyes"]
        assert "tan" in info["skin_color"]
        assert info["nsfw"] is False
        assert "cigarette" in info["additional_details"]


class TestVNCCSBackendFlag:
    def test_txt2img_dry_run_does_not_require_vnccs(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "txt2img"]
            )
        assert result.exit_code == 0, result.output
        assert "prompt+seed is not a same-face lock" in result.stdout
        assert "Preflight OK: VNCCS" not in result.stdout

    def test_vnccs_dry_run_errors_when_nodes_missing(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        with mock.patch.object(preflight, "_object_info", txt2img_only_object_info):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "vnccs"]
            )
        assert result.exit_code == 1
        assert "Preflight failed" in result.output
        assert "VNCCS" in result.output
        assert "ComfyUI Manager" in result.output
        assert "will not silently fall back" in result.output

    def test_vnccs_dry_run_ok_when_nodes_present(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={"devices": [{"type": "cpu"}]}
        ):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "vnccs"]
            )
        assert result.exit_code == 0, result.output
        assert "Backend: vnccs" in result.stdout
        assert "fallback" in result.stdout
        assert "not a same-face lock" in result.stdout
        assert "Using Character Creator" in result.stdout
        assert "Preflight OK: VNCCS nodes" in result.stdout

    def test_txt2img_mentions_unused_yaml_reference(self, tmp_path):
        cfg = _write_char_yaml(
            tmp_path / "char.yaml",
            ["idle"],
            extra="reference: ./refs/kite_male_neutral.png\n",
        )
        with mock.patch.object(preflight, "_object_info", fake_object_info):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "txt2img"]
            )
        assert result.exit_code == 0, result.output
        assert "unused on --backend txt2img" in result.stdout
        assert "Character Cloner" in result.stdout
        assert "Preflight OK: VNCCS" not in result.stdout

    def test_yaml_reference_plus_backend_vnccs_uses_cloner(self, tmp_path):
        ref = tmp_path / "refs" / "kite_male_neutral.png"
        ref.parent.mkdir()
        ref.write_bytes(make_cel_sprite())
        cfg = _write_char_yaml(
            tmp_path / "char.yaml",
            ["idle"],
            extra="reference: ./refs/kite_male_neutral.png\n",
        )
        queued = []

        def fake_workflow(self, workflow, prefer_node="14"):
            queued.append(workflow)
            return [make_cel_sprite()]

        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={"devices": [{"type": "cpu"}]}
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate_workflow",
            fake_workflow,
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.upload_image",
            return_value="uploaded_ref.png",
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate",
            side_effect=AssertionError("txt2img generate must not run"),
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--backend",
                    "vnccs",
                    "--poses",
                    "idle",
                ],
            )
        assert result.exit_code == 0, result.output
        assert "Character Cloner" in result.stdout
        types = workflow_class_types(queued[0])
        assert NODE_CHARACTER_CLONER in types
        assert NODE_CHARACTER_CREATOR not in types

    def test_cli_reference_uses_cloner_graph(self, tmp_path):
        ref = tmp_path / "refs" / "kite_male_neutral.png"
        ref.parent.mkdir()
        ref.write_bytes(make_cel_sprite())
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        queued = []

        def fake_workflow(self, workflow, prefer_node="14"):
            queued.append(workflow)
            return [make_cel_sprite()]

        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={"devices": [{"type": "cpu"}]}
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate_workflow",
            fake_workflow,
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.upload_image",
            return_value="uploaded_ref.png",
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate",
            side_effect=AssertionError("txt2img generate must not run"),
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--reference",
                    str(ref),
                    "--poses",
                    "idle",
                ],
            )
        assert result.exit_code == 0, result.output
        assert "Character Cloner" in result.stdout
        assert queued
        types = workflow_class_types(queued[0])
        assert NODE_CHARACTER_CLONER in types
        assert NODE_CHARACTER_CLONE_GENERATOR in types
        assert NODE_CHARACTER_CREATOR not in types
        assert "IPAdapterAdvanced" not in types

    def test_love32_reference_path_refused_without_read(self, tmp_path):
        live = (
            tmp_path
            / "LOVE32"
            / "LOVE32"
            / "game"
            / "images"
            / "kite_male neutral.png"
        )
        live.parent.mkdir(parents=True)
        live.write_bytes(b"should-not-be-read")
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch(
            "pathlib.Path.read_bytes",
            side_effect=AssertionError("must not read LOVE32"),
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--dry-run",
                    "--reference",
                    str(live),
                ],
            )
        assert result.exit_code == 1
        assert "Refusing to read a LOVE32 path" in result.output
        assert "sandbox refs" in result.output

    def test_mac_love32_path_string_refused_even_if_missing(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        live = Path(
            "/Users/jeffreytse/Desktop/LOVE32/LOVE32/game/images/"
            "kite_male neutral.png"
        )
        result = CliRunner().invoke(
            app,
            ["character", str(cfg), "--dry-run", "--reference", str(live)],
        )
        assert result.exit_code == 1
        assert "LOVE32" in result.output
        assert "not found" not in result.output.lower() or "Refusing" in result.output

    def test_missing_sandbox_ref_prints_copy_hint(self, tmp_path):
        cfg = _write_char_yaml(
            tmp_path / "char.yaml",
            ["idle"],
            extra="reference: ./refs/kite_male_neutral.png\n",
        )
        with mock.patch.object(preflight, "_object_info", vnccs_object_info):
            result = CliRunner().invoke(
                app,
                ["character", str(cfg), "--dry-run", "--backend", "vnccs"],
            )
        assert result.exit_code == 1
        assert "Character Cloner reference not found" in result.output
        assert "hand-copy" in result.output
        assert REFERENCE_COPY_HINT.splitlines()[0] in result.output

    def test_mps_cli_fails_unless_allow_flag(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        mps_stats = {"devices": [{"type": "mps", "name": "Apple M-series"}]}
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value=mps_stats
        ):
            blocked = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "vnccs"]
            )
            allowed = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--dry-run",
                    "--backend",
                    "vnccs",
                    "--vnccs-allow-mps",
                ],
            )
        assert blocked.exit_code == 1
        assert "Apple Silicon MPS" in blocked.output
        assert "will not silently fall back" in blocked.output
        assert allowed.exit_code == 0, allowed.output
        assert "fallback" in allowed.stdout
        assert "WARNING: Apple Silicon MPS" in allowed.output

    def test_unknown_backend_rejected(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        result = CliRunner().invoke(
            app, ["character", str(cfg), "--dry-run", "--backend", "magic"]
        )
        assert result.exit_code == 1
        assert "txt2img or vnccs" in result.output

    def test_love32_refuse_still_works_with_vnccs_backend(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        project = tmp_path / "LOVE32" / "LOVE32"
        (project / "game").mkdir(parents=True)
        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={}
        ):
            result = CliRunner().invoke(
                app,
                [
                    "character",
                    str(cfg),
                    "--backend",
                    "vnccs",
                    "--copy-only",
                    "--project",
                    str(project),
                ],
            )
        assert result.exit_code == 1
        assert "LOVE32" in result.output
        assert not list((project / "game").rglob("*.png"))
        assert not (project / "game" / "matcha_characters.rpy").exists()

    def test_vnccs_generate_queues_vnccs_graph(self, tmp_path):
        cfg = _write_char_yaml(tmp_path / "char.yaml", ["idle"])
        queued = []

        def fake_workflow(self, workflow, prefer_node="14"):
            queued.append(workflow)
            return [make_cel_sprite()]

        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch.object(
            preflight, "fetch_system_stats", return_value={}
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate_workflow",
            fake_workflow,
        ), mock.patch(
            "matcha.generators.comfyui.ComfyUIGenerator.generate",
            side_effect=AssertionError("txt2img generate must not run"),
        ):
            result = CliRunner().invoke(
                app,
                ["character", str(cfg), "--backend", "vnccs", "--poses", "idle"],
            )
        assert result.exit_code == 0, result.output
        assert "fallback" in result.stdout
        assert queued
        types = workflow_class_types(queued[0])
        assert NODE_CHARACTER_CREATOR in types
        assert NODE_CHARACTER_GENERATOR in types
        assert NODE_POSE_STUDIO in types
        assert NODE_CHARACTER_CLONER not in types
        assert (tmp_path / "out" / "kite_male_idle.png").exists()
