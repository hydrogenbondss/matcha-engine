"""Tests for model license lookup and platform disclosure helpers."""

from pathlib import Path

from typer.testing import CliRunner

from matcha.cli import app
from matcha.disclosure import (
    STEAM_SURVEY_URL,
    build_disclosure_document,
    build_itch_reminder,
    build_steam_survey_text,
)
from matcha.licenses import CommercialStatus, format_license_report, lookup_model


class TestLicenses:
    def test_anythingv5_commercial_ok(self):
        info = lookup_model("anythingV5PrtRE.safetensors")
        assert info.commercial_outputs is CommercialStatus.OK
        assert "Anything" in info.name
        assert "Fair AI" in info.license_name

    def test_noobai_restricted(self):
        info = lookup_model("NoobAI-XL-v1.0.safetensors")
        assert info.commercial_outputs is CommercialStatus.RESTRICTED
        assert "NoobAI" in info.name
        assert "prohibit" in info.notes.lower() or "WARNING" in info.notes

    def test_unknown_checkpoint(self):
        info = lookup_model("mystery_sdxl_v9.safetensors")
        assert info.commercial_outputs is CommercialStatus.UNKNOWN
        assert "Unknown" in info.name

    def test_unknown_lora(self):
        info = lookup_model("last.safetensors", kind="lora")
        assert info.commercial_outputs is CommercialStatus.UNKNOWN
        assert "LoRA" in info.name

    def test_format_report_includes_both(self):
        text = format_license_report(
            "anythingV5PrtRE.safetensors", "last.safetensors"
        )
        assert "not legal advice" in text.lower()
        assert "anythingV5PrtRE.safetensors" in text
        assert "last.safetensors" in text
        assert "likely OK" in text
        assert "UNKNOWN" in text

    def test_format_report_noobai_warns(self):
        text = format_license_report("noobaiXLNAIXL_vPred10.safetensors")
        assert "RESTRICTED" in text
        assert "WARNING" in text


class TestDisclosure:
    def test_steam_pre_generated_default(self):
        text = build_steam_survey_text(
            character_name="sakura",
            checkpoint="anythingV5PrtRE.safetensors",
            lora="last.safetensors",
        )
        assert "Pre-Generated" in text
        assert STEAM_SURVEY_URL in text
        assert "anythingV5PrtRE.safetensors" in text
        assert "last.safetensors" in text
        assert "Live-Generated" not in text.split("Pre-Generated")[0]

    def test_itch_reminder(self):
        text = build_itch_reminder(character_name="sakura")
        assert "itch.io" in text.lower()
        assert "de-indexed" in text.lower()
        assert "disclosure" in text.lower()

    def test_document_has_disclaimer_steam_itch(self):
        doc = build_disclosure_document(
            character_name="sakura",
            checkpoint="anythingV5PrtRE.safetensors",
            lora="last.safetensors",
        )
        assert "Not legal advice" in doc
        assert "Steam" in doc
        assert "itch.io" in doc
        assert "Model license snapshot" in doc


class TestLicenseDiscloseCLI:
    def test_licenses_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["licenses", "--checkpoint", "anythingV5PrtRE.safetensors"],
        )
        assert result.exit_code == 0, result.output
        assert "likely OK" in result.output
        assert "not legal advice" in result.output.lower()

    def test_licenses_cli_noobai(self):
        runner = CliRunner()
        result = runner.invoke(
            app, ["licenses", "-c", "NoobAI-XL.safetensors"]
        )
        assert result.exit_code == 0, result.output
        assert "RESTRICTED" in result.output

    def test_disclose_cli_stdout(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "disclose",
                "--name",
                "sakura",
                "--checkpoint",
                "anythingV5PrtRE.safetensors",
                "--lora",
                "none",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Not legal advice" in result.output
        assert "Steam" in result.output
        assert "itch.io" in result.output

    def test_disclose_cli_write(self, tmp_path: Path):
        runner = CliRunner()
        out = tmp_path / "out" / "disclosure.md"
        result = runner.invoke(
            app,
            [
                "disclose",
                "--name",
                "sakura",
                "-c",
                "noobai.safetensors",
                "--write",
                str(out),
            ],
        )
        assert result.exit_code == 0, result.output
        assert out.exists()
        body = out.read_text()
        assert "Not legal advice" in body
        assert "RESTRICTED" in body

    def test_disclose_cli_project(self, tmp_path: Path):
        runner = CliRunner()
        project = tmp_path / "game_proj"
        project.mkdir()
        result = runner.invoke(
            app,
            [
                "disclose",
                "--name",
                "sakura",
                "-c",
                "anythingV5PrtRE.safetensors",
                "--project",
                str(project),
            ],
        )
        assert result.exit_code == 0, result.output
        path = project / "matcha_disclosure.md"
        assert path.exists()
        assert "Pre-Generated" in path.read_text()
