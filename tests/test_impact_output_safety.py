"""`matcha impact` refuses --output/--summary inside the fixture root or a
protected repository directory (after resolving symlinks and '..')."""

import pytest
from typer.testing import CliRunner

import matcha.impact.engine as engine
from impact_helpers import REAL_FIXTURE, REPO, fake_discovery, make_fixture
from matcha.cli import PROTECTED_REPO_DIRS, app, protected_output_reason


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "discover", lambda: fake_discovery())
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    fx = make_fixture(root / "fixtures" / "fx", {"game/main.rpy": 'image hero = "images/hero.png"\n'},
                      {"assets/hero.png": {"game": "images/hero.png"}})
    docs = root / "docs" / "experiments"
    docs.mkdir(parents=True)
    for name in ("PROTOCOL.md", "WORKSHEET.md", "FIXTURE-DOC.md"):
        (docs / name).write_text(f"frozen {name}\n")
    (root / "out").mkdir()
    return root, fx, docs


def _snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and "out" not in p.parts}


def _invoke(fx, output, summary=None):
    args = ["impact", "--fixture", str(fx), "--request", "x", "--output", str(output), "--provider", "unavailable"]
    if summary is not None:
        args += ["--summary", str(summary)]
    return CliRunner().invoke(app, args)


def _targets(root, fx, docs):
    out = root / "out"
    (out / "to_meta").symlink_to(fx / "metadata", target_is_directory=True)
    (out / "to_docs").symlink_to(docs, target_is_directory=True)
    (out / "evil.json").symlink_to(docs / "WORKSHEET.md")
    (out / "dangling.json").symlink_to(fx / "game" / "new.json")
    return {
        "fixture root": fx / "r.json",
        "fixture metadata": fx / "metadata" / "fixture-manifest.json",
        "fixture game": fx / "game" / "main.rpy",
        "fixture new file": fx / "game" / "new.json",
        "protocol": docs / "PROTOCOL.md",
        "worksheet": docs / "WORKSHEET.md",
        "fixture doc": docs / "FIXTURE-DOC.md",
        "new doc file": docs / "NEW.md",
        "dotdot into fixture": out / ".." / "fixtures" / "fx" / "metadata" / "x.json",
        "dotdot into docs": out / ".." / "docs" / "experiments" / "PROTOCOL.md",
        "symlinked dir into fixture": out / "to_meta" / "fixture-manifest.json",
        "symlinked dir into docs": out / "to_docs" / "WORKSHEET.md",
        "symlinked file into docs": out / "evil.json",
        "dangling symlink into fixture": out / "dangling.json",
    }


def test_every_protected_destination_is_rejected_for_output_and_summary(repo):
    root, fx, docs = repo
    before = _snapshot(root)
    for label, target in _targets(root, fx, docs).items():
        res = _invoke(fx, target)
        assert res.exit_code == 1 and "refusing to write --output" in res.output, label
        res = _invoke(fx, root / "out" / "ok.json", summary=target)
        assert res.exit_code == 1 and "refusing to write --summary" in res.output, label
    assert _snapshot(root) == before  # nothing protected was written or changed
    assert not (fx / "game" / "new.json").exists() and not (docs / "NEW.md").exists()
    assert not (root / "out" / "ok.json").exists()  # refused before any write


def test_worktree_style_git_file_is_a_repo_root(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "discover", lambda: fake_discovery())
    root = tmp_path / "wt"
    root.mkdir()
    (root / ".git").write_text("gitdir: /elsewhere/.git/worktrees/wt\n")
    fx = make_fixture(root / "fixtures" / "fx", {"game/a.rpy": 'image h = "images/h.png"\n'},
                      {"assets/h.png": {"game": "images/h.png"}})
    (root / "docs" / "experiments").mkdir(parents=True)
    assert protected_output_reason(root / "docs" / "experiments" / "X.md", fx)


def test_safe_output_under_out_is_accepted(repo):
    root, fx, _ = repo
    res = _invoke(fx, root / "out" / "r.json", summary=root / "out" / "r.md")
    assert res.exit_code == 0, res.output
    assert (root / "out" / "r.json").exists() and (root / "out" / "r.md").exists()


def test_real_repository_paths(tmp_path):
    docs = REPO / "docs" / "experiments"
    for p in (
        docs / "EXPERIMENT-01-HUMAN-BASELINE.md",
        docs / "EVIDENCE-PROTOCOL-01.md",
        docs / "KITE-FIXTURE-01.md",
        REAL_FIXTURE / "metadata" / "fixture-manifest.json",
        REAL_FIXTURE / "game" / "route_kite.rpy",
        REPO / "out" / ".." / "fixtures" / "kite-production" / "x.json",
    ):
        assert protected_output_reason(p, REAL_FIXTURE), p
    assert protected_output_reason(REPO / "out" / "testA-impact.json", REAL_FIXTURE) is None
    # the repository that contains the matcha package is protected even for an outside fixture
    fx = make_fixture(tmp_path / "fx", {"game/a.rpy": 'image h = "images/h.png"\n'}, {"assets/h.png": {"game": "images/h.png"}})
    assert protected_output_reason(docs / "EVIDENCE-PROTOCOL-01.md", fx)
    assert protected_output_reason(tmp_path / "elsewhere.json", fx) is None
    assert PROTECTED_REPO_DIRS == ("docs/experiments",)
