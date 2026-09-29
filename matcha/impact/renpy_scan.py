"""Generic line-level scanner for Ren'Py sources and evidence excerpts.

This is deliberately *not* a full Ren'Py parser.  It recognises the handful of
constructs that create a static-asset reference:

* ``image <name> = <expr>`` declarations (string literals in the expression)
* ``show`` / ``scene`` statements naming an image (``show tag attr ... at ...``)
* string literals that are image file names or paths (``*.png`` etc.)
* string literals that spell a space-separated image name (``"tag attr"``),
  e.g. Python data passed to screens or dict entries
* entries of module-level UPPER_CASE table literals (``NAME = { ... }``)

It also *flags* (but never resolves) constructs that appear to build an
image/file reference dynamically: string concatenation, f-strings, ``%``
formatting or ``.format`` with image-like pieces, ``show expression <expr>``,
and image-loading calls (``Image``, ``im.*``, ``renpy.loadable`` and similar)
whose argument is not a string literal.  These become ``DynamicRef`` records
so that relationship discovery can surface them as unresolved dependencies.

Comments are ignored.  Excerpt files (``# EVIDENCE EXCERPT`` header plus
``# --- <file> lines A-B ---`` block markers) are scanned only inside their
marked blocks, and every line is mapped back to its original source line.

The scanner has no knowledge of any particular game, character, or file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from matcha.impact.model import CodeUnit

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".bmp", ".tga")

_MARKER_RE = re.compile(r"^# --- (?P<file>\S+) lines (?P<a>\d+)-(?P<b>\d+) ---\s*$")
_LABEL_RE = re.compile(r"^label\s+([A-Za-z_][\w\.]*)")
_TOPLEVEL_RESET_RE = re.compile(
    r"^(init|image|define|default|screen|transform|style|python|layeredimage|translate)\b"
)
_DEF_RE = re.compile(r"^(\s*)def\s+([A-Za-z_]\w*)\s*\(")
_TABLE_RE = re.compile(r"^\s*(?:\$\s*|define\s+|default\s+)?([A-Z][A-Z0-9_]*)\s*=\s*[\{\[\(]")
_IMAGE_DECL_RE = re.compile(r"^image\s+([A-Za-z0-9_][\w\- ]*?)\s*=\s*(.+)$")
_IMAGE_ATL_RE = re.compile(r"^image\s+([A-Za-z0-9_][\w\- ]*?)\s*:\s*$")
_SHOW_RE = re.compile(r"^(show|scene)\s+(.+?)\s*:?\s*$")
_SHOW_STOP = {"at", "with", "as", "behind", "zorder", "onlayer"}
_SHOW_SKIP_FIRST = {"screen", "expression", "layer"}
_NAME_TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]+$")
_IDENT_STRING_RE = re.compile(r"^[A-Za-z_][\w\-]*(?: [A-Za-z0-9_][\w\-]*)+$")
_ASSIGN_RE = re.compile(
    r"^(?:\$\s*)?(?:define\s+|default\s+)?[A-Za-z_][\w\.]*(?:\[[^\]]*\])?\s*[-+*/]?=(?!=)"
)
_DICT_ENTRY_RE = re.compile(r"^(?:\"[^\"]*\"|'[^']*')\s*:")


@dataclass
class Line:
    source_path: str  # fixture-relative CODE unit path
    fixture_line: int  # 1-based line in the fixture file
    raw: str
    code: str  # comment stripped, whitespace stripped
    strings: list[str]
    locator: str
    block: Optional[str] = None  # excerpt block marker (verbatim)
    origin_line: Optional[int] = None
    label: Optional[str] = None
    function: Optional[str] = None
    table: Optional[str] = None
    prev_nonblank: Optional[str] = None
    indent: int = 0
    bare: str = ""  # code with string literals blanked to ""

    @property
    def is_excerpt(self) -> bool:
        return self.block is not None

    def scope(self) -> tuple[str, str]:
        """(scope kind, scope text) used for occurrence contexts."""
        parts = []
        if self.block is not None:
            parts.append(f"excerpt block marker: {self.block}")
            if self.function:
                parts.append(f"inside function {self.function}()")
            return ("block", "; ".join(parts))
        if self.label:
            return ("label", f"label {self.label}")
        if self.function:
            return ("function", f"function {self.function}")
        return ("file", "top level")


@dataclass
class Declaration:
    name: str  # normalised "tag attr ..."
    rhs: str
    literals: list[str]
    line: Line


@dataclass
class ImageUsage:
    name: str
    keyword: str  # show | scene
    line: Line


@dataclass
class StringRef:
    value: str
    kind: str  # "file" | "ident"
    line: Line


@dataclass
class DynamicRef:
    """A construct that seems to build an image/file reference at run time."""

    line: Line
    reasons: list[str]
    prefixes: list[str] = field(default_factory=list)  # literal leading fragments
    suffixes: list[str] = field(default_factory=list)  # literal trailing fragments (e.g. ".png")


@dataclass
class ScanResult:
    unit: CodeUnit
    lines: list[Line] = field(default_factory=list)
    declarations: list[Declaration] = field(default_factory=list)
    usages: list[ImageUsage] = field(default_factory=list)
    strings: list[StringRef] = field(default_factory=list)
    dynamic: list[DynamicRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _unescape(s: str) -> str:
    return s.replace("\\\\", "\x00").replace('\\"', '"').replace("\\'", "'").replace("\x00", "\\")


def tokenize(line: str, triple: Optional[str] = None):
    """Split *line* into (code_without_comment, string_values, code_without_strings, triple_state).

    ``triple`` carries an open triple-quoted string across lines; its content
    is not reported as string literals (treated like a docstring).
    """
    code: list[str] = []
    bare: list[str] = []
    strings: list[str] = []
    i, n = 0, len(line)
    if triple:
        j = line.find(triple)
        if j < 0:
            return "", [], "", triple
        code.append(line[: j + 3])
        i = j + 3
        triple = None
    while i < n:
        c = line[i]
        if c == "#":
            break
        if c in "\"'":
            if line.startswith(c * 3, i):
                q = c * 3
                j = line.find(q, i + 3)
                if j < 0:
                    code.append(line[i:])
                    return "".join(code).strip(), strings, "".join(bare), q
                code.append(line[i : j + 3])
                bare.append('""')
                i = j + 3
                continue
            j = i + 1
            buf: list[str] = []
            while j < n:
                if line[j] == "\\" and j + 1 < n:
                    buf.append(line[j : j + 2])
                    j += 2
                    continue
                if line[j] == c:
                    break
                buf.append(line[j])
                j += 1
            strings.append(_unescape("".join(buf)))
            code.append(line[i : j + 1])
            bare.append('""')
            i = j + 1
            continue
        code.append(c)
        bare.append(c)
        i += 1
    return "".join(code).strip(), strings, "".join(bare), triple


def _bracket_delta(bare: str) -> int:
    return sum(bare.count(c) for c in "([{") - sum(bare.count(c) for c in ")]}")


def is_image_path(value: str) -> bool:
    return value.lower().endswith(IMAGE_EXTS)


def parse_show_name(rest: str) -> Optional[str]:
    tokens = rest.split()
    if not tokens or tokens[0] in _SHOW_SKIP_FIRST:
        return None
    name: list[str] = []
    for tok in tokens:
        if tok in _SHOW_STOP:
            break
        tok = tok.rstrip(":")
        if not _NAME_TOKEN_RE.match(tok):
            break
        name.append(tok)
    return " ".join(name) if name else None


def literal_anchor_type(line: Line) -> str:
    """Anchor type for a line that carries a string-literal reference.

    Generic rule, from Ren'Py/Python syntax only:

    * inside an UPPER_CASE table literal -> ``config``
    * a binding: ``name = expr`` / ``$ name = expr`` / ``define|default name =
      expr`` / ``obj.attr = expr`` / ``x[k] = expr`` (augmented forms too, but
      not ``==``), or a ``"key": value`` dict entry -> ``assignment``
    * anything else (return, call argument, list item, ...) -> ``statement``
    """
    if line.table:
        return "config"
    if _ASSIGN_RE.match(line.code) or _DICT_ENTRY_RE.match(line.code):
        return "assignment"
    return "statement"


# ---------------------------------------------------------------------------
# Dynamic reference detection (flag only; no static evaluation)
# ---------------------------------------------------------------------------

_LOAD_CALL_RE = re.compile(
    r"(?<![\w.])(Image|im\.\w+|renpy\.(?:loadable|image|show|displayable|file|open_file|exists|load_image))"
    r"\s*\(\s*(?!(?:True|False|None)\b)([A-Za-z_][\w\.]*(?:\s*\[[^\]]*\])?)\s*[,)]"
)
_FSTRING_PREFIX_RE = re.compile(r"(?i)^(?:rf|fr|f)$")


def string_spans(code: str) -> list[tuple[int, int, str, str]]:
    """(start, end, value, prefix) for each string literal in *code*.

    *code* is a comment-stripped line.  ``prefix`` holds the string-prefix
    letters (``f``, ``rb`` ...) directly before the opening quote.  ``start``
    includes the prefix.
    """
    spans = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        if c not in "\"'":
            i += 1
            continue
        k = i
        while k > 0 and i - k < 2 and code[k - 1] in "rRbBfFuU":
            k -= 1
        if k > 0 and (code[k - 1].isalnum() or code[k - 1] == "_"):
            k = i  # letters belong to an identifier, not a string prefix
        pre = code[k:i]
        q = c * 3 if code.startswith(c * 3, i) else c
        j = i + len(q)
        buf = []
        while j < n:
            if code[j] == "\\" and j + 1 < n:
                buf.append(code[j : j + 2])
                j += 2
                continue
            if code.startswith(q, j):
                break
            buf.append(code[j])
            j += 1
        end = min(j + len(q), n)
        spans.append((k, end, "".join(buf), pre))
        i = end
    return spans


def _image_like(v: str) -> bool:
    low = v.lower()
    return is_image_path(v) or low.startswith("images/") or v.endswith("/")


def _ext_suffix(v: str) -> Optional[str]:
    for ext in IMAGE_EXTS:
        if v.lower().endswith(ext):
            return v
    return None


def detect_dynamic(code: str, bare: str) -> tuple[list[str], list[str], list[str]]:
    """Return (reasons, literal prefixes, literal suffixes) for *code*."""
    reasons: list[str] = []
    prefixes: list[str] = []
    suffixes: list[str] = []
    spans = string_spans(code)
    concat_parts = []
    for idx, (start, end, value, pre) in enumerate(spans):
        after = code[end:].lstrip()
        before = code[:start].rstrip()
        cat_after = after.startswith("+") and not after.startswith("+=")
        cat_before = before.endswith("+") or before.endswith("+=")
        if cat_after or cat_before:
            concat_parts.append((value, cat_before, cat_after))
        if _FSTRING_PREFIX_RE.match(pre or "") and "{" in value and _image_like(value.split("{")[0] + value.rsplit("}", 1)[-1]):
            reasons.append("f-string builds an image/file path")
            head = value.split("{", 1)[0]
            if head and not head.startswith("."):
                prefixes.append(head)
            tail = value.rsplit("}", 1)[-1]
            if _ext_suffix(tail):
                suffixes.append(tail)
        if after.startswith("%") and not after.startswith("%=") and "%" in value and _image_like(value.replace("%s", "").replace("%d", "")):
            reasons.append("%-formatting builds an image/file path")
            head = value.split("%", 1)[0]
            if head and not head.startswith("."):
                prefixes.append(head)
        if after.startswith(".format(") and "{" in value and _image_like(value.split("{")[0] + value.rsplit("}", 1)[-1]):
            reasons.append(".format() builds an image/file path")
            head = value.split("{", 1)[0]
            if head and not head.startswith("."):
                prefixes.append(head)
    if concat_parts and any(_image_like(v) for v, _, _ in concat_parts):
        reasons.append("string concatenation builds an image/file path")
        for v, cb, ca in concat_parts:
            if ca and not cb and v and not v.startswith("."):
                prefixes.append(v)
            if cb and _ext_suffix(v):
                suffixes.append(v)
    for m in _LOAD_CALL_RE.finditer(bare):
        reasons.append(f"{m.group(1)}() is called with a non-literal argument '{m.group(2)}'")
    # de-duplicate, keep order
    uniq = lambda xs: list(dict.fromkeys(xs))
    return uniq(reasons), uniq(prefixes), uniq(suffixes)


def _iter_units(unit: CodeUnit, text: str):
    """Yield (fixture_line_no, raw, block_marker, origin_line, block_start)."""
    lines = text.splitlines()
    if not unit.is_excerpt:
        for i, raw in enumerate(lines, 1):
            yield i, raw, None, None, False
        return
    block = None
    origin = None
    for i, raw in enumerate(lines, 1):
        m = _MARKER_RE.match(raw)
        if m:
            block = raw.strip()
            origin = int(m.group("a"))
            yield i, raw, block, None, True
            continue
        if block is None:
            continue  # excerpt header: evidence metadata, not source
        yield i, raw, block, origin, False
        origin += 1


def scan_unit(unit: CodeUnit, text: str) -> ScanResult:
    res = ScanResult(unit=unit)
    label = None
    funcs: list[tuple[int, str]] = []
    table: Optional[str] = None
    depth = 0
    triple = None
    prev: Optional[str] = None
    origin_rel = unit.origin_path or unit.fixture_path

    for lineno, raw, block, origin_line, block_start in _iter_units(unit, text):
        if block_start:
            label, funcs, table, depth, triple, prev = None, [], None, 0, None, None
            continue
        code, strings, bare, triple = tokenize(raw, triple)
        stripped_raw = raw.strip()
        indent = len(raw) - len(raw.lstrip(" \t"))
        if code:
            while funcs and indent <= funcs[-1][0] and not code.startswith("@"):
                funcs.pop()
            if indent == 0:
                m = _LABEL_RE.match(code)
                if m:
                    label = m.group(1)
                elif _TOPLEVEL_RESET_RE.match(code):
                    label = None
            m = _DEF_RE.match(raw)
            if m:
                funcs.append((len(m.group(1)), m.group(2)))

        line_table = table
        if code and table is None:
            m = _TABLE_RE.match(code)
            if m:
                line_table = m.group(1)
                depth = _bracket_delta(bare)
                table = line_table if depth > 0 else None
        elif code and table is not None:
            depth += _bracket_delta(bare)
            if depth <= 0:
                table, depth = None, 0

        locator = (
            f"source {origin_rel}:{origin_line}" if block is not None else f"{unit.fixture_path}:{lineno}"
        )
        ln = Line(
            source_path=unit.fixture_path,
            fixture_line=lineno,
            raw=raw,
            code=code,
            strings=strings,
            locator=locator,
            block=block,
            origin_line=origin_line,
            label=label,
            function=funcs[-1][1] if funcs else None,
            table=line_table,
            prev_nonblank=prev,
            indent=indent,
            bare=bare,
        )
        res.lines.append(ln)
        if stripped_raw:
            prev = stripped_raw
        if not code:
            continue

        reasons, prefixes, suffixes = detect_dynamic(code, bare)
        m = _SHOW_RE.match(code)
        if m and m.group(2).split()[0] == "expression":
            expr = m.group(2).split(None, 1)[1] if len(m.group(2).split(None, 1)) > 1 else ""
            if not (expr[:1] in "\"'" and len(strings) == 1):
                reasons = [f"{m.group(1)} expression with a non-literal displayable"] + reasons
        if reasons:
            res.dynamic.append(DynamicRef(line=ln, reasons=reasons, prefixes=prefixes, suffixes=suffixes))

        m = _IMAGE_DECL_RE.match(code)
        if m:
            name = " ".join(m.group(1).split())
            lits = [s for s in strings if is_image_path(s)]
            res.declarations.append(Declaration(name=name, rhs=m.group(2).strip(), literals=lits, line=ln))
            continue
        if _IMAGE_ATL_RE.match(code):
            res.warnings.append(
                f"{locator}: ATL image block not resolved by the v1 scanner: {code}"
            )
            continue
        m = _SHOW_RE.match(code)
        if m:
            name = parse_show_name(m.group(2))
            if name:
                res.usages.append(ImageUsage(name=name, keyword=m.group(1), line=ln))
                continue
            # show screen / show expression / show layer: fall through so any
            # string literal on the line is still scanned.
        for s in strings:
            if is_image_path(s):
                res.strings.append(StringRef(value=s, kind="file", line=ln))
            elif _IDENT_STRING_RE.match(s):
                res.strings.append(StringRef(value=" ".join(s.split()), kind="ident", line=ln))
    return res
