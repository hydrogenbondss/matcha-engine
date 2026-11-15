"""`matcha run` one-command wrapper: health-check gate + delegation."""

from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from matcha.cli import app


def _invoke(args, reachable=True):
    with mock.patch("matcha.setup.is_server_reachable", return_value=reachable), \
         mock.patch("matcha.cli.character") as char_mock:
        result = CliRunner().invoke(app, args)
    return result, char_mock


class TestRunCommand:
    def test_server_down_exits_1_with_setup_pointer(self):
        result, char_mock = _invoke(["run", "char.yaml"], reachable=False)
        assert result.exit_code == 1
        assert "matcha setup" in result.output
        assert "not reachable" in result.output
        char_mock.assert_not_called()

    def test_happy_path_without_project_generates_only(self):
        result, char_mock = _invoke(["run", "char.yaml"])
        assert result.exit_code == 0
        char_mock.assert_called_once()
        kwargs = char_mock.call_args.kwargs
        assert kwargs["config"] == Path("char.yaml")
        assert kwargs["project"] is None
        assert kwargs["deploy"] is False
        # Tail summary points at the compliance helpers
        assert "matcha licenses" in result.stdout
        assert "matcha disclose" in result.stdout

    def test_happy_path_with_project_deploys(self):
        result, char_mock = _invoke(["run", "char.yaml", "--project", "examples/sample-vn"])
        assert result.exit_code == 0
        kwargs = char_mock.call_args.kwargs
        assert kwargs["project"] == Path("examples/sample-vn")
        assert kwargs["deploy"] is True

    def test_flag_passthrough(self):
        result, char_mock = _invoke(
            ["run", "char.yaml", "--lora", "none", "--no-layered", "--side-image"]
        )
        assert result.exit_code == 0
        kwargs = char_mock.call_args.kwargs
        assert kwargs["lora"] == "none"
        assert kwargs["layered"] is False
        assert kwargs["side_image"] is True

    def test_layered_flag_defaults_to_none(self):
        result, char_mock = _invoke(["run", "char.yaml", "--layered"])
        assert result.exit_code == 0
        assert char_mock.call_args.kwargs["layered"] is True

    def test_delegation_uses_safe_defaults_for_hidden_flags(self):
        result, char_mock = _invoke(["run", "char.yaml"])
        assert result.exit_code == 0
        kwargs = char_mock.call_args.kwargs
        # run never reimplements the flow — hidden character flags stay default
        assert kwargs["dry_run"] is False
        assert kwargs["backend"] == "txt2img"
        assert kwargs["copy_only"] is False
        assert kwargs["force"] is False
