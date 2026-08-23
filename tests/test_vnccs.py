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
    NODE_CHARACTER_CLONE_GENERATOR,
    NODE_CHARACTER_CLONER,
    NODE_CHARACTER_CREATOR,
    NODE_CHARACTER_GENERATOR,
    NODE_CLOTHES_DESIGNER,
    NODE_CLOTHES_GENERATOR,
    NODE_CONTROL_CENTER,
    NODE_POSE_STUDIO,
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
        with mock.patch.object(preflight, "_object_info", txt2img_only_object_info):
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
        with mock.patch.object(preflight, "_object_info", vnccs_object_info):
            status = preflight.validate_vnccs("x")
        assert status.required_ok
        assert status.clothes_ok
        assert status.cloner_ok

    def test_cloner_flag_requires_cloner_nodes(self):
        def no_cloner(server, node):
            if node in (NODE_CHARACTER_CLONER, NODE_CHARACTER_CLONE_GENERATOR):
                return {}
            return vnccs_object_info(server, node)

        with mock.patch.object(preflight, "_object_info", no_cloner):
            with pytest.raises(PreflightError, match="Character Cloner"):
                preflight.validate_vnccs("x", require_cloner=True)

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
        with mock.patch.object(preflight, "_object_info", vnccs_object_info):
            result = CliRunner().invoke(
                app, ["character", str(cfg), "--dry-run", "--backend", "vnccs"]
            )
        assert result.exit_code == 0, result.output
        assert "Backend: vnccs" in result.stdout
        assert "same-face lock" in result.stdout
        assert "Preflight OK: VNCCS nodes" in result.stdout

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
        with mock.patch.object(preflight, "_object_info", vnccs_object_info):
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

        with mock.patch.object(preflight, "_object_info", vnccs_object_info), mock.patch(
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
        assert queued
        types = workflow_class_types(queued[0])
        assert NODE_CHARACTER_CREATOR in types
        assert NODE_CHARACTER_GENERATOR in types
        assert NODE_POSE_STUDIO in types
        assert (tmp_path / "out" / "kite_male_idle.png").exists()
