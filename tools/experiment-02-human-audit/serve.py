#!/usr/bin/env python3
"""Experiment 2, condition H: local human-only recording tool.

A repository inspector with an evidence ledger beside it. It records what the
human enters and nothing else: it never classifies, suggests, infers, sorts by
relevance or pre-fills anything.

Standard library only. Binds to 127.0.0.1 only. Read-only access to the 15
scored ASSET files and 8 scored CODE files listed in the Experiment 2 H
worksheet, and (separate evidence view) to the frozen files inside
fixtures/kite-production/ through an exact whitelist built at start-up. Cases
unlock in order A -> B -> C; a case unlocks only after the previous one has been
exported and finalized. The Investigation and Documentation timers never
overlap. All recorded data is written to an output directory that must be
outside this Git repository.

Usage:
    python3 tools/experiment-02-human-audit/serve.py --output-dir <local-experiment-02-human-output>
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path
from typing import Any, Optional

TOOL_NAME = "experiment-02-human-audit"
TOOL_VERSION = "0.2.0"

TOOL_DIR = Path(__file__).resolve().parent
STATIC_DIR = TOOL_DIR / "static"
REPO_ROOT = TOOL_DIR.parents[1]
WORKSHEET = REPO_ROOT / "docs" / "experiments" / "EXPERIMENT-02-HUMAN-BASELINE.md"
FIXTURE_ROOT = REPO_ROOT / "fixtures" / "kite-production"

CASES = ("A", "B", "C")
# Allowed values, exactly as defined in docs/experiments/EVIDENCE-PROTOCOL-01.md
# (Decision 5 for ASSET status; §5 for CODE file_status and relationship_status;
# §5.1 for anchor_type). Checked at start-up against the worksheet's own lines.
ASSET_STATUS = ("ASSET_ACTION", "UNAFFECTED", "REVIEW_REQUIRED")
CODE_STATUS = ("CODE_ACTION", "DOWNSTREAM_USAGE", "REVIEW_REQUIRED", "UNAFFECTED")
ANCHOR_TYPES = ("declaration", "statement", "function", "label", "assignment", "config",
                "excerpt_header", "asset", "metadata")
_ALLOWED_LINES = (
    "- ASSET `status`: one of `ASSET_ACTION`, `UNAFFECTED`, `REVIEW_REQUIRED`.",
    "- CODE `file_status` and `relationship_status`: one of `CODE_ACTION`, `DOWNSTREAM_USAGE`, "
    "`REVIEW_REQUIRED`, `UNAFFECTED`.",
    "- Allowed `anchor_type` values: `declaration`, `statement`, `function`, `label`, `assignment`, "
    "`config`, `excerpt_header`, `asset`, `metadata`.",
)
# Evidence browser: file types shown. Video and audio are never listed (protocol §19;
# docs/experiments/KITE-FIXTURE-01.md §4). Anything else is not listed either.
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
               ".gif": "image/gif"}
TEXT_TYPES = {".rpy", ".txt", ".md", ".json", ".yaml", ".yml"}
EVIDENCE_FIELDS = ("source_path", "anchor_type", "anchor", "context", "locator", "fingerprint", "fact")
MAX_BODY = 8 * 1024 * 1024
MAX_TEXT = 200_000


# --------------------------------------------------------------------------- worksheet
def load_worksheet(path: Path = WORKSHEET) -> dict[str, Any]:
    """Read the frozen Experiment 2 H worksheet: the exact request/question lines
    and the scored ASSET / CODE paths, in the order the worksheet lists them."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    for want in _ALLOWED_LINES:
        if want not in lines:
            raise SystemExit(f"worksheet allowed-values line not found: {want!r}")
    sections: dict[str, list[str]] = {}
    current = None
    for line in lines:
        m = re.match(r"^## Test ([ABC]): (.+)$", line)
        if m:
            current = m.group(1)
            sections[current] = [line]
            continue
        if line.startswith("## ") and current:
            current = None
        if current:
            sections[current].append(line)
    if tuple(sorted(sections)) != CASES:
        raise SystemExit("worksheet does not contain exactly Test A, B and C sections")
    cases: dict[str, Any] = {}
    asset_lists, code_lists = [], []
    for c in CASES:
        sec = sections[c]
        title = re.match(r"^## Test [ABC]: (.+)$", sec[0]).group(1)

        def quoted_after(label: str) -> str:
            i = sec.index(label)
            j = i + 1
            while sec[j] == "":
                j += 1
            if not sec[j].startswith("> "):
                raise SystemExit(f"Test {c}: no quoted line after {label!r}")
            return sec[j]

        req, que = quoted_after("Exact request:"), quoted_after("Question:")
        ids_assets, ids_code, cur_id = [], [], None
        for l in sec:
            m = re.match(r"^- id: (H-[ABC]-(ASSET|CODE)-\d\d)$", l)
            if m:
                cur_id = (m.group(1), m.group(2))
                continue
            m = re.match(r"^  (asset_path|source_path): (\S+)$", l)
            if m and cur_id:
                if cur_id[1] == "ASSET" and m.group(1) == "asset_path":
                    ids_assets.append((cur_id[0], m.group(2)))
                elif cur_id[1] == "CODE" and m.group(1) == "source_path":
                    ids_code.append((cur_id[0], m.group(2)))
                cur_id = None
        cases[c] = {
            "title": title,
            "request_line": req,
            "question_line": que,
            "request": req[2:],
            "question": que[2:],
            "asset_ids": [i for i, _ in ids_assets],
            "code_ids": [i for i, _ in ids_code],
        }
        asset_lists.append([p for _, p in ids_assets])
        code_lists.append([p for _, p in ids_code])
    if any(a != asset_lists[0] for a in asset_lists) or any(k != code_lists[0] for k in code_lists):
        raise SystemExit("worksheet ASSET/CODE lists differ between tests")
    assets, code = asset_lists[0], code_lists[0]
    if len(assets) != 15 or len(set(assets)) != 15 or len(code) != 8 or len(set(code)) != 8:
        raise SystemExit(f"expected 15 ASSET and 8 CODE paths, found {len(assets)} and {len(code)}")
    for c in CASES:
        if cases[c]["asset_ids"] != [f"H-{c}-ASSET-{i:02d}" for i in range(1, 16)] or \
                cases[c]["code_ids"] != [f"H-{c}-CODE-{i:02d}" for i in range(1, 9)]:
            raise SystemExit(f"unexpected record ids in Test {c}")
    return {"cases": cases, "assets": assets, "code": code}


# --------------------------------------------------------------------------- git / provenance
def _git(*args: str, cwd: Path = REPO_ROOT) -> Optional[str]:
    try:
        out = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                             timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def tool_provenance() -> dict[str, Any]:
    head = _git("rev-parse", "HEAD")
    head = head if head and re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", head) else None
    porcelain = _git("status", "--porcelain", "--untracked-files=normal")
    tree = _git("rev-parse", "HEAD:fixtures/kite-production")
    tree = tree if tree and re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", tree) else None
    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "tool_source_commit": head,
        "tool_source_dirty": None if porcelain is None else bool(porcelain.strip()),
        "export_timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "fixture_tree_at_head": tree,
    }


# --------------------------------------------------------------------------- output directory
def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_output_dir(raw: str) -> Path:
    """The output directory must be outside this Git repository (and outside any
    other worktree of it). Refuses the repo, the fixture and docs/."""
    out = Path(os.path.expanduser(raw)).resolve()
    repo = REPO_ROOT.resolve()
    for forbidden in (repo, FIXTURE_ROOT.resolve(), (REPO_ROOT / "docs").resolve()):
        if out == forbidden or _is_within(out, forbidden):
            raise ValueError(f"output directory must be outside the repository: {out} is inside {forbidden}")
    anc = out
    while not anc.exists():
        anc = anc.parent
    here = _git("rev-parse", "--path-format=absolute", "--git-common-dir")
    there = _git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=anc if anc.is_dir() else anc.parent)
    if here and there and Path(here).resolve() == Path(there).resolve():
        raise ValueError(f"output directory must be outside the repository: {out} is inside a worktree of it")
    out.mkdir(parents=True, exist_ok=True)
    return out


# --------------------------------------------------------------------------- state validation
def _s(v: Any, name: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"{name}: expected a string")
    if len(v) > MAX_TEXT:
        raise ValueError(f"{name}: too long")
    return v


def _choice(v: Any, allowed: tuple[str, ...], name: str) -> str:
    v = _s(v, name)
    if v != "" and v not in allowed:
        raise ValueError(f"{name}: {v!r} is not an allowed value")
    return v


def _obj(v: Any, keys: tuple[str, ...], name: str) -> dict:
    if not isinstance(v, dict):
        raise ValueError(f"{name}: expected an object")
    extra = set(v) - set(keys)
    if extra:
        raise ValueError(f"{name}: unknown field(s) {sorted(extra)}")
    return v


def _list(v: Any, name: str) -> list:
    if not isinstance(v, list):
        raise ValueError(f"{name}: expected a list")
    return v


def _ts(v: Any, name: str, allow_null: bool) -> Optional[str]:
    if v is None and allow_null:
        return None
    v = _s(v, name)
    try:
        t = dt.datetime.fromisoformat(v)
    except ValueError:
        raise ValueError(f"{name}: not an ISO 8601 timestamp")
    if t.tzinfo is None:
        raise ValueError(f"{name}: timestamp must carry a UTC offset")
    return v


def _evidence(v: Any, name: str) -> list[dict]:
    out = []
    for i, e in enumerate(_list(v, name)):
        e = _obj(e, EVIDENCE_FIELDS, f"{name}[{i}]")
        item = {k: _s(e.get(k, ""), f"{name}[{i}].{k}") for k in EVIDENCE_FIELDS}
        _choice(item["anchor_type"], ANCHOR_TYPES, f"{name}[{i}].anchor_type")
        out.append(item)
    return out


def _segments(v: Any, name: str) -> list[dict]:
    out = []
    segs = _list(v, name)
    for i, s in enumerate(segs):
        s = _obj(s, ("start", "end"), f"{name}[{i}]")
        start = _ts(s.get("start"), f"{name}[{i}].start", False)
        end = _ts(s.get("end"), f"{name}[{i}].end", True)
        if end is None and i != len(segs) - 1:
            raise ValueError(f"{name}[{i}]: only the last segment may be open")
        if end is not None and dt.datetime.fromisoformat(end) < dt.datetime.fromisoformat(start):
            raise ValueError(f"{name}[{i}]: end before start")
        out.append({"start": start, "end": end})
    return out


def _check_no_overlap(inv: list[dict], doc: list[dict]) -> None:
    """Investigation and Documentation segments must never overlap: at most one
    open segment in total, and no two intervals (open = still running) overlap.
    Touching intervals (one ends when the next starts) are allowed."""
    far = dt.datetime.max.replace(tzinfo=dt.timezone.utc)
    iv = []
    for name, segs in (("investigation", inv), ("documentation", doc)):
        for s in segs:
            a = dt.datetime.fromisoformat(s["start"])
            b = far if s["end"] is None else dt.datetime.fromisoformat(s["end"])
            iv.append((a, b, name))
    if sum(1 for s in inv + doc if s["end"] is None) > 1:
        raise ValueError("timers overlap: more than one timer is running")
    iv.sort(key=lambda x: (x[0], x[1]))
    for (a1, b1, n1), (a2, b2, n2) in zip(iv, iv[1:]):
        if a2 < b1:
            raise ValueError(f"timers overlap: {n2} segment starts before {n1} segment ends")


def empty_state(case: str, ws: dict) -> dict:
    return {
        "case": case,
        "updated_at": None,
        "investigation_segments": [],
        "documentation_segments": [],
        "assets": {p: {"status": "", "reason": "", "evidence": [], "game_usage": []} for p in ws["assets"]},
        "code": {p: {"file_status": "", "reason": "", "evidence": [], "relationships": []} for p in ws["code"]},
        "unresolved_items": [],
        "work_notes": "",
    }


def validate_state(case: str, raw: Any, ws: dict) -> dict:
    st = _obj(raw, ("case", "updated_at", "investigation_segments", "documentation_segments", "assets", "code",
                    "unresolved_items", "work_notes"), "state")
    if st.get("case") != case:
        raise ValueError("state.case does not match the URL")
    out = empty_state(case, ws)
    out["updated_at"] = _ts(st.get("updated_at"), "updated_at", True)
    out["investigation_segments"] = _segments(st.get("investigation_segments", []), "investigation_segments")
    out["documentation_segments"] = _segments(st.get("documentation_segments", []), "documentation_segments")
    _check_no_overlap(out["investigation_segments"], out["documentation_segments"])
    assets = _obj(st.get("assets", {}), tuple(ws["assets"]), "assets")
    for p, rec in assets.items():
        rec = _obj(rec, ("status", "reason", "evidence", "game_usage"), f"assets[{p}]")
        out["assets"][p] = {
            "status": _choice(rec.get("status", ""), ASSET_STATUS, f"assets[{p}].status"),
            "reason": _s(rec.get("reason", ""), f"assets[{p}].reason"),
            "evidence": _evidence(rec.get("evidence", []), f"assets[{p}].evidence"),
            "game_usage": [_s(g, f"assets[{p}].game_usage") for g in _list(rec.get("game_usage", []), "game_usage")],
        }
    code = _obj(st.get("code", {}), tuple(ws["code"]), "code")
    for p, rec in code.items():
        rec = _obj(rec, ("file_status", "reason", "evidence", "relationships"), f"code[{p}]")
        rels = []
        for i, r in enumerate(_list(rec.get("relationships", []), f"code[{p}].relationships")):
            r = _obj(r, ("related_asset", "relationship_status", "reason", "evidence"), f"code[{p}].relationships[{i}]")
            rels.append({
                "related_asset": _choice(r.get("related_asset", ""), tuple(ws["assets"]),
                                         f"code[{p}].relationships[{i}].related_asset"),
                "relationship_status": _choice(r.get("relationship_status", ""), CODE_STATUS,
                                               f"code[{p}].relationships[{i}].relationship_status"),
                "reason": _s(r.get("reason", ""), f"code[{p}].relationships[{i}].reason"),
                "evidence": _evidence(r.get("evidence", []), f"code[{p}].relationships[{i}].evidence"),
            })
        out["code"][p] = {
            "file_status": _choice(rec.get("file_status", ""), CODE_STATUS, f"code[{p}].file_status"),
            "reason": _s(rec.get("reason", ""), f"code[{p}].reason"),
            "evidence": _evidence(rec.get("evidence", []), f"code[{p}].evidence"),
            "relationships": rels,
        }
    out["unresolved_items"] = [_s(u, "unresolved_items") for u in _list(st.get("unresolved_items", []), "unresolved_items")]
    out["work_notes"] = _s(st.get("work_notes", ""), "work_notes")
    return out


# --------------------------------------------------------------------------- export (YAML, stdlib emitter)
def _hms(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def _closed_total(segs: list[dict]) -> Optional[float]:
    closed = [s for s in segs if s["end"] is not None]
    if not closed:
        return None
    return sum((dt.datetime.fromisoformat(s["end"]) - dt.datetime.fromisoformat(s["start"])).total_seconds()
               for s in closed)


def _blank(v: str) -> Optional[str]:
    return None if v == "" else v


def build_export(case: str, st: dict, ws: dict, provenance: dict) -> dict:
    inv, doc = st["investigation_segments"], st["documentation_segments"]
    inv_total, doc_total = _closed_total(inv), _closed_total(doc)
    c = ws["cases"][case]

    def ev(items):
        return [{k: _blank(e[k]) for k in EVIDENCE_FIELDS} for e in items]

    return {
        "provenance": provenance,
        "test_case": case,
        "start_time": inv[0]["start"] if inv else None,
        "end_time": inv[-1]["end"] if inv else None,
        "elapsed_time": None if inv_total is None else _hms(inv_total),
        "investigation_segments": [dict(s) for s in inv],
        "documentation_segments": [dict(s) for s in doc],
        "documentation_elapsed_time": None if doc_total is None else _hms(doc_total),
        "asset_records": [
            {"id": rid, "test_case": case, "item_type": "ASSET", "asset_path": p,
             "status": _blank(st["assets"][p]["status"]), "reason": _blank(st["assets"][p]["reason"]),
             "evidence": ev(st["assets"][p]["evidence"]), "game_usage": list(st["assets"][p]["game_usage"])}
            for rid, p in zip(c["asset_ids"], ws["assets"])
        ],
        "code_records": [
            {"id": rid, "test_case": case, "item_type": "CODE", "source_path": p,
             "file_status": _blank(st["code"][p]["file_status"]), "reason": _blank(st["code"][p]["reason"]),
             "evidence": ev(st["code"][p]["evidence"]),
             "relationships": [
                 {"related_asset": _blank(r["related_asset"]), "relationship_status": _blank(r["relationship_status"]),
                  "reason": _blank(r["reason"]), "evidence": ev(r["evidence"])}
                 for r in st["code"][p]["relationships"]
             ]}
            for rid, p in zip(c["code_ids"], ws["code"])
        ],
        "unresolved_items": [{"item": u} for u in st["unresolved_items"]],
        "work_notes": [st["work_notes"]] if st["work_notes"] != "" else [],
    }


_PLAIN = re.compile(r"^[A-Za-z0-9_./-]+$")
_RESERVED = {"", "~", "null", "Null", "NULL", "true", "True", "TRUE", "false", "False", "FALSE",
             "yes", "Yes", "no", "No", "on", "On", "off", "Off", "y", "Y", "n", "N"}


def _scalar(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    s = str(v)
    if _PLAIN.match(s) and s not in _RESERVED and not re.match(r"^[-+.]?\d", s):
        return s
    return json.dumps(s, ensure_ascii=False)  # JSON string escapes are valid YAML double-quoted scalars


def to_yaml(v: Any, indent: int = 0) -> str:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(v, dict):
        for k, x in v.items():
            key = _scalar(k)
            if isinstance(x, (dict, list)) and x:
                lines.append(f"{pad}{key}:")
                lines.append(to_yaml(x, indent + 2) if isinstance(x, dict) else to_yaml(x, indent))
            elif isinstance(x, dict):
                lines.append(f"{pad}{key}: {{}}")
            elif isinstance(x, list):
                lines.append(f"{pad}{key}: []")
            else:
                sc = _scalar(x)
                lines.append(f"{pad}{key}:" + (f" {sc}" if sc else ""))
    elif isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and x:
                sub = to_yaml(x, indent + 2).split("\n")
                sub[0] = f"{pad}- " + sub[0][indent + 2:]
                lines.extend(sub)
            elif isinstance(x, list) and x:
                lines.append(f"{pad}-")
                lines.append(to_yaml(x, indent + 2))
            elif isinstance(x, dict):
                lines.append(f"{pad}- {{}}")
            elif isinstance(x, list):
                lines.append(f"{pad}- []")
            else:
                sc = _scalar(x)
                lines.append(f"{pad}-" + (f" {sc}" if sc else ""))
    else:
        lines.append(pad + _scalar(v))
    return "\n".join(lines)


def export_text(data: dict) -> str:
    head = (f"# Experiment 2, condition H, Test {data['test_case']}: human-recorded export.\n"
            f"# Written by tools/{TOOL_NAME}; contains only what the human entered.\n")
    return head + to_yaml(data) + "\n"


# --------------------------------------------------------------------------- evidence whitelist
def _git_blob_id(data: bytes, oid_len: int) -> str:
    h = hashlib.sha256 if oid_len == 64 else hashlib.sha1
    return h(b"blob %d\0" % len(data) + data).hexdigest()


def _evidence_type(rel: str) -> Optional[str]:
    ext = os.path.splitext(rel)[1].lower()
    if ext in IMAGE_TYPES:
        return "image"
    if ext in TEXT_TYPES:
        return "text"
    return None


def build_evidence_whitelist() -> tuple[dict[str, dict], list[dict], str]:
    """Exact whitelist of frozen fixture files (fixture-relative path -> entry).
    Source: `git ls-tree -r HEAD:fixtures/kite-production` (regular files only),
    each checked on disk: not a symlink, resolves inside the fixture root, and
    its bytes equal the committed blob. Fallback when git is unavailable: a
    filesystem walk with the same symlink / realpath checks."""
    root = FIXTURE_ROOT.resolve()
    listing = _git("ls-tree", "-r", "-z", "HEAD:fixtures/kite-production")
    entries: list[tuple[str, Optional[str]]] = []
    skipped: list[dict] = []
    if listing is not None:
        source = "git ls-tree -r HEAD:fixtures/kite-production"
        for rec in filter(None, listing.split("\0")):
            meta, rel = rec.split("\t", 1)
            mode, otype, oid = meta.split()
            if otype != "blob" or mode not in ("100644", "100755"):
                skipped.append({"path": rel, "reason": f"not a regular file in HEAD (mode {mode})"})
                continue
            entries.append((rel, oid))
    else:
        source = "filesystem walk (git unavailable)"
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            for fn in filenames:
                full = Path(dirpath) / fn
                entries.append((full.relative_to(root).as_posix(), None))
    whitelist: dict[str, dict] = {}
    for rel, oid in sorted(entries):
        kind = _evidence_type(rel)
        if kind is None:
            skipped.append({"path": rel, "reason": "not an image or text file (video/audio and other types are not listed)"})
            continue
        p = root / rel
        if p.is_symlink() or not p.is_file():
            skipped.append({"path": rel, "reason": "symlink or not a regular file on disk"})
            continue
        real = p.resolve()
        if not _is_within(real, root):
            skipped.append({"path": rel, "reason": "resolves outside the fixture"})
            continue
        data = real.read_bytes()
        if oid is not None and _git_blob_id(data, len(oid)) != oid:
            skipped.append({"path": rel, "reason": "on-disk bytes differ from the committed fixture"})
            continue
        whitelist[rel] = {"path": rel, "type": kind, "bytes": len(data), "file": real, "disk": p,
                          "sha256": hashlib.sha256(data).hexdigest(),
                          "ctype": IMAGE_TYPES.get(os.path.splitext(rel)[1].lower(), "text/plain; charset=utf-8")}
    return whitelist, skipped, source


# --------------------------------------------------------------------------- server
class Locked(Exception):
    pass


class App:
    def __init__(self, output_dir: Path):
        self.ws = load_worksheet()
        self.output_dir = output_dir
        self.lock = threading.Lock()
        self.files: dict[str, Path] = {}
        for rel in list(self.ws["assets"]) + list(self.ws["code"]):
            p = (FIXTURE_ROOT / rel).resolve()
            if not _is_within(p, FIXTURE_ROOT.resolve()) or not p.is_file() or (FIXTURE_ROOT / rel).is_symlink():
                raise SystemExit(f"scored fixture file missing: {rel}")
            self.files[rel] = p
        self.evidence, self.evidence_skipped, self.evidence_source = build_evidence_whitelist()
        missing = [rel for rel in self.files if rel not in self.evidence]
        if missing:
            raise SystemExit(f"scored files not in the fixture evidence whitelist: {missing}")
        run = self.output_dir / "H-run.json"
        if not run.exists():
            run.write_text(json.dumps({"run_id": os.urandom(8).hex(),
                                       "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds")},
                                      indent=2) + "\n", encoding="utf-8")
        self.run_id = json.loads(run.read_text(encoding="utf-8"))["run_id"]

    # ---- finalize / lock (mechanical: no semantic checks)
    def _final_paths(self, case: str) -> tuple[Path, Path]:
        return self.output_dir / f"H-{case}.yaml", self.output_dir / f"H-{case}.finalized.json"

    def finalized(self, case: str) -> Optional[dict]:
        y, f = self._final_paths(case)
        if not (y.is_file() and f.is_file()):
            return None
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None
        if rec.get("case") != case or rec.get("export_sha256") != hashlib.sha256(y.read_bytes()).hexdigest():
            return None
        return rec

    def unlocked(self, case: str) -> bool:
        i = CASES.index(case)
        return all(self.finalized(c) for c in CASES[:i])

    def status(self) -> dict:
        cases = {}
        for c in CASES:
            rec = self.finalized(c)
            cases[c] = {"unlocked": self.unlocked(c), "finalized": rec is not None,
                        "finalized_at": rec.get("finalized_at") if rec else None}
        resume = next((c for c in CASES if cases[c]["unlocked"] and not cases[c]["finalized"]), CASES[0])
        return {"run_id": self.run_id, "cases": cases, "resume": resume}

    def require(self, case: str, *, editable: bool) -> None:
        if not self.unlocked(case):
            prev = CASES[CASES.index(case) - 1]
            raise Locked(f"Test {case} is locked until Test {prev} is exported and finalized")
        if editable and self.finalized(case):
            raise Locked(f"Test {case} is finalized and read-only")

    # ---- state
    def state_path(self, case: str) -> Path:
        return self.output_dir / f"H-{case}.state.json"

    def load_state(self, case: str) -> dict:
        p = self.state_path(case)
        if p.exists():
            return validate_state(case, json.loads(p.read_text(encoding="utf-8")), self.ws)
        return empty_state(case, self.ws)

    def save_state(self, case: str, raw: Any) -> dict:
        st = validate_state(case, raw, self.ws)
        with self.lock:
            self.require(case, editable=True)
            p = self.state_path(case)
            tmp = p.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, p)
        return st

    def finalize(self, case: str) -> tuple[Path, str, dict]:
        """Export H-<case>.yaml and write H-<case>.finalized.json. Refused while a
        timer is running. After this the case is read-only and the next case unlocks."""
        with self.lock:
            self.require(case, editable=True)
            st = self.load_state(case)
            if any(s["end"] is None for s in st["investigation_segments"] + st["documentation_segments"]):
                raise ValueError("stop the running timer before exporting and finalizing")
            text = export_text(build_export(case, st, self.ws, tool_provenance()))
            y, f = self._final_paths(case)
            tmp = y.with_suffix(".yaml.tmp")
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, y)
            rec = {"case": case, "finalized_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                   "export_file": y.name, "export_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                   "tool_version": TOOL_VERSION}
            tmp = f.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            os.replace(tmp, f)
        return y, text, rec


CSP = ("default-src 'self'; img-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; "
       "object-src 'none'; media-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


def make_handler(app: App, port_ref: list[int]):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = TOOL_NAME
        sys_version = ""

        def log_message(self, fmt, *args):  # quiet
            pass

        def _host_ok(self) -> bool:
            host = (self.headers.get("Host") or "").lower()
            return host in {f"127.0.0.1:{port_ref[0]}", f"localhost:{port_ref[0]}"}

        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: Any):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if not self._host_ok():
                return self._json(403, {"error": "forbidden host"})
            path = urllib.parse.urlsplit(self.path).path
            if path in ("/", "/index.html"):
                return self._static("index.html")
            if path.startswith("/static/"):
                return self._static(path[len("/static/"):])
            if path == "/api/units":
                return self._json(200, {
                    "cases": list(CASES),
                    "assets": app.ws["assets"],
                    "code": app.ws["code"],
                    "asset_status": list(ASSET_STATUS),
                    "code_status": list(CODE_STATUS),
                    "anchor_types": list(ANCHOR_TYPES),
                    "evidence_fields": list(EVIDENCE_FIELDS),
                })
            if path == "/api/status":
                return self._json(200, app.status())
            if path == "/api/evidence":
                return self._json(200, {"source": app.evidence_source,
                                        "files": [{"path": e["path"], "type": e["type"], "bytes": e["bytes"]}
                                                  for e in app.evidence.values()]})
            m = re.fullmatch(r"/api/case/([ABC])", path)
            if m:
                try:
                    app.require(m.group(1), editable=False)
                except Locked as e:
                    return self._json(423, {"error": str(e)})
                c = app.ws["cases"][m.group(1)]
                return self._json(200, {"case": m.group(1), "title": c["title"], "request": c["request"],
                                        "question": c["question"], "asset_ids": c["asset_ids"],
                                        "code_ids": c["code_ids"], "finalized": app.finalized(m.group(1))})
            m = re.fullmatch(r"/api/state/([ABC])", path)
            if m:
                try:
                    app.require(m.group(1), editable=False)
                    return self._json(200, app.load_state(m.group(1)))
                except Locked as e:
                    return self._json(423, {"error": str(e)})
                except (ValueError, json.JSONDecodeError) as e:
                    return self._json(500, {"error": f"saved state unreadable: {e}"})
            if path.startswith("/fixture/"):
                rel = urllib.parse.unquote(path[len("/fixture/"):])
                f = app.files.get(rel)  # exact whitelist match only; no path joining
                if f is None:
                    return self._json(404, {"error": "not in the scored-file whitelist"})
                ctype = "image/png" if rel.endswith(".png") else "text/plain; charset=utf-8"
                return self._send(200, f.read_bytes(), ctype)
            if path.startswith("/evidence/"):
                rel = urllib.parse.unquote(path[len("/evidence/"):])
                e = app.evidence.get(rel)  # exact whitelist key lookup only; no path joining
                if e is None:
                    return self._json(404, {"error": "not in the fixture evidence whitelist"})
                # re-check at serve time: still no symlink, same real path, same frozen bytes
                if e["disk"].is_symlink() or e["disk"].resolve() != e["file"]:
                    return self._json(404, {"error": "not in the fixture evidence whitelist"})
                data = e["file"].read_bytes()
                if hashlib.sha256(data).hexdigest() != e["sha256"]:
                    return self._json(404, {"error": "fixture file changed since start-up"})
                return self._send(200, data, e["ctype"])
            return self._json(404, {"error": "not found"})

        def _static(self, name: str):
            allowed = {"index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8",
                       "app.css": "text/css; charset=utf-8"}
            if name not in allowed:
                return self._json(404, {"error": "not found"})
            return self._send(200, (STATIC_DIR / name).read_bytes(), allowed[name])

        def do_POST(self):
            if not self._host_ok():
                return self._json(403, {"error": "forbidden host"})
            origin = self.headers.get("Origin")
            if origin is not None and origin not in {f"http://127.0.0.1:{port_ref[0]}",
                                                     f"http://localhost:{port_ref[0]}"}:
                return self._json(403, {"error": "forbidden origin"})
            if not (self.headers.get("Content-Type") or "").startswith("application/json"):
                return self._json(415, {"error": "expected application/json"})
            try:
                n = int(self.headers.get("Content-Length") or "0")
            except ValueError:
                return self._json(400, {"error": "bad length"})
            if n > MAX_BODY:
                return self._json(413, {"error": "too large"})
            body = self.rfile.read(n)
            path = urllib.parse.urlsplit(self.path).path
            m = re.fullmatch(r"/api/state/([ABC])", path)
            if m:
                try:
                    st = app.save_state(m.group(1), json.loads(body.decode("utf-8")))
                except Locked as e:
                    return self._json(423, {"error": str(e)})
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
                    return self._json(400, {"error": str(e)})
                return self._json(200, {"saved": True, "updated_at": st["updated_at"]})
            m = re.fullmatch(r"/api/(?:export|finalize)/([ABC])", path)
            if m:
                try:
                    p, text, rec = app.finalize(m.group(1))
                except Locked as e:
                    return self._json(423, {"error": str(e)})
                except (ValueError, json.JSONDecodeError) as e:
                    return self._json(400, {"error": str(e)})
                return self._json(200, {"written": str(p), "yaml": text, "finalized": rec})
            return self._json(404, {"error": "not found"})

    return Handler


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Experiment 2 condition H: local human-only recording tool.")
    ap.add_argument("--output-dir", required=True,
                    help="directory for saved state and exports; must be outside this Git repository")
    ap.add_argument("--port", type=int, default=8765, help="localhost port (0 = any free port)")
    a = ap.parse_args(argv)
    try:
        out = validate_output_dir(a.output_dir)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    app = App(out)
    port_ref = [a.port]
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(app, port_ref))
    port_ref[0] = httpd.server_address[1]
    print(f"Serving on http://127.0.0.1:{port_ref[0]}/  (output: {out})  Ctrl+C to stop.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
