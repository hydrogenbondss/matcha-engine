"""Production (matcha/impact and the `matcha impact` CLI) knows nothing about
test cases, worksheets or human classifications; the evaluator owns labels."""

import inspect
import json
import re

from typer.testing import CliRunner

import matcha.cli as cli
from impact_helpers import REAL_FIXTURE, REPO, fake_discovery
from matcha.cli import app
from matcha.impact.engine import run_impact

BANNED = ["test_case", "test-case", "testcase", "worksheet", "baseline", "EXPERIMENT-01", "HUMAN-BASELINE"]


def _hits(text):
    return [b for b in BANNED if b.lower() in text.lower()]


def test_engine_package_has_no_test_case_or_worksheet_tokens():
    files = sorted((REPO / "matcha" / "impact").glob("*.py"))
    assert files
    for p in files:
        assert _hits(p.read_text()) == [], p.name


def test_impact_cli_function_has_no_test_case_or_worksheet_tokens():
    assert _hits(inspect.getsource(cli.impact)) == []
    assert "test_case" not in inspect.signature(run_impact).parameters


def test_cli_rejects_test_case_option(tmp_path):
    res = CliRunner().invoke(
        app,
        ["impact", "--fixture", str(REAL_FIXTURE), "--request", "x", "--output", str(tmp_path / "o.json"),
         "--provider", "unavailable", "--test-case", "A"],
    )
    assert res.exit_code == 2 and "No such option" in res.output
    assert not (tmp_path / "o.json").exists()


def test_report_carries_no_test_label(tmp_path):
    out = tmp_path / "r.json"
    run_impact(fixture=REAL_FIXTURE, request="x", reference=None, output=out,
               provider="unavailable", discovery_fn=fake_discovery)
    text = out.read_text()
    assert _hits(text) == []
    assert not re.search(r'"test"\s*:', text)
    json.loads(text)
