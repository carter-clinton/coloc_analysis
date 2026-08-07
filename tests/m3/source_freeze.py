"""The reusable CODE-identity utility: "has the CODE of this file moved since <ref>?"

WHAT THIS PINS
--------------
The **CODE** of a source file -- R or Python -- against a fixed revision.

WHAT IT DELIBERATELY IGNORES
----------------------------
Comments, Python docstrings, blank lines and trailing whitespace. Correcting a
wrong comment in a frozen file therefore costs **nothing**: no unfreeze, no
re-pin, no decision. That is the entire point of the rescope. Before
``quick-260806-sr4`` the gate on ``run_susie_rss.R`` was
``git diff --exit-code <SHA> -- <file>`` -- a **byte** pin -- which made shipping
a known-false census figure (finding **K-3**: ``1,944``, correct ``1,909``) the
*cheaper* option than correcting the comment that carried it. A rule that makes
shipping a falsehood cheaper than fixing it is mis-scoped.

WHY A GUARD EXISTS AT ALL
-------------------------
``BLOCKER-1`` proved this pipeline can move Track A numbers **silently**: fixing
the LD read path moved EUR ``r[1,2]`` 0.1 -> 0.9, credible sets 3 -> 10, nonzero
PIPs 200 -> 78, while ``ld_status`` and ``ld_overlap_fraction`` -- the two fields
anyone would check to argue nothing moved -- stayed byte-identical. The AFR-side
regression oracle costs the AoU perimeter and an ~11-day billed fire. Silent
numeric drift with no cheap oracle is the threat. The guard is not weakened
here; it is aimed at the right target.

THE RE-PIN PROTOCOL, IN ONE SENTENCE
------------------------------------
When an authorized unfreeze changes **code**, update **exactly one constant per
FROZEN SUBJECT** -- ``R_CODE_REF`` for ``run_susie_rss.R``, ``PY_CODE_REF`` for
the three m3 Python modules -- to the SHA of the commit that landed the change,
**and nothing else**. ``FROZEN_R_CODE_REV`` and ``FREEZE_CODE_REF`` are *import
aliases* of ``R_CODE_REF``, so they follow automatically. Comment and docstring
changes update **nothing**. Constants annotated ``DIFFERENTIAL SUBSTRATE`` or
``HISTORICAL NARRATIVE`` (``K3_PRE_FIX_REF``, every ``PRE_CHANGE_REF``, ...) are
**never** re-pinned -- bumping one silently destroys the control it feeds
(``[[feedback_fixing_a_split_unpins_what_it_pinned]]``).

See ``DEC-2026-08-06-sr4-freeze-scope`` in ``.planning/DECISIONS.md``.

THE ACTUAL SIDE IS THE WORKING TREE. NEVER A COMMITTED READ.
------------------------------------------------------------
``assert_code_frozen`` resolves its ACTUAL side with
``(PROJECT_ROOT / rel_path).read_text()``. It must **never** become
``git_show("HEAD", rel_path)``. This is not stylistic.
``_assert_r_freeze_clean()`` is called MID-TEST from
``test_finemap_receipt_early_exit.py`` (at ``:341`` and ``:357``, guarding the
comment "the frozen file is READ here, never written"), and
``test_qtl_coloc_allele_join.py``'s NC-2g controls alter the loader source in
memory and then re-assert the freeze. If the actual side became a
``git show HEAD:`` read, every one of those gates would go structurally **blind
to an uncommitted working-tree write** -- a coverage reduction with nothing
turning red. ``NC-SR10`` in ``test_source_freeze.py`` pins this permanently, at
module scope, by stripping THIS module to code and requiring that no executable
string literal names the symbolic revision.

THE CORRECTNESS HAZARD IS THE STRIPPER ITSELF
---------------------------------------------
A stripper that mangles string literals makes a **real code change invisible**,
which is strictly worse than the byte pin it replaces. ``#`` inside a string is
**not** a comment (``gsub("#.*", "", s)``, ``re.compile("#[0-9]+")``). So:

* **R** -- a *length-preserving* mask (comment bodies -> space, string CONTENTS
  -> ``_`` with the delimiters kept), then the brace-walk runs over the **mask**,
  never over raw text, and the code prefix is sliced out of the **original**.
* **Python** -- ``ast``. Comments never enter the AST, and a ``#`` inside a
  string is a ``Constant``, so comment-insensitivity is true *by construction*.
  Python is never brace-walked: braces inside f-strings are live (23 in
  ``plink_ld_to_npz.py``), so a brace-walk over Python text is already wrong.

Two mask invariants are load-bearing and **no live file exercises either one**,
so ``test_source_freeze.py`` pins both synthetically:

* **(4a)** a ``\\n`` is written through UNCHANGED even inside a string. Filling
  it deletes a line from the mask and misaligns every subsequent ``zip()`` pair,
  so the comparison drifts wholesale and silently. ``len(masked) == len(text)``
  is **BLIND** to this -- it holds under both variants.
* **(4b)** the filler is non-whitespace (``_``). With a space filler the content
  of a multi-line string is lost to ``rstrip()``.

``ast.unparse`` output can differ across Python minor versions. That is harmless
**because both sides of every comparison are unparsed by the same interpreter in
the same process**. Do not "fix" it by freezing an unparse string.

NINE AD-HOC COMMENT-STRIPPERS ALREADY EXISTED
---------------------------------------------
This module supersedes them **going forward**; it does not refactor them. Each
backs a different pre-existing assertion with deliberate, differing semantics
(``strip_py_comments`` KEEPS triple-quoted strings because a Snakemake ``shell:``
body IS one; ``code_only`` DELETES them). ``r_code_only``
(``test_qtl_coloc_allele_join.py``) is deliberately kept and is consumed as an
INDEPENDENT R cross-check by ``test_source_freeze.py``. What existed **nowhere**
was the FREEZE convention itself.
"""
from __future__ import annotations

import ast
import keyword
import re
import subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LANG_R = "r"
LANG_PY = "py"

#: A pin must be an immutable revision. A symbolic name would make every gate
#: permanently green with nothing ever turning red -- the cheapest possible
#: weakening, and one a 7-hex sweep would never notice.
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")

#: hard rule 4b -- NON-whitespace, or a multi-line string's content is lost to
#: ``rstrip()``.
_FILLER = "_"

#: R function definitions. Matched against the MASKED text, so a definition-like
#: sequence inside a string or a comment cannot spoof one. R permits a leading
#: dot in a name.
_R_DEF_RE = re.compile(r"^([.A-Za-z][.A-Za-z0-9_]*)\s*<-\s*function", re.M)

#: The placeholder ``_mask_strip_py`` substitutes for a whole string literal.
#: Excluded from the cross-check multiset, so its spelling is immaterial.
_PY_STR_TOKEN = "STRLIT"

_PY_STR_PREFIX_CHARS = set("rbfuRBFU")


# ==========================================================================
# R -- the length-preserving mask
# ==========================================================================
def _mask_r(text: str, *, filler: str = _FILLER, keep_newlines: bool = True) -> str:
    """A LENGTH-PRESERVING mask of ``text``: comments -> space, string contents
    -> ``filler``, string delimiters kept, newlines written through.

    ``filler`` and ``keep_newlines`` exist so ``test_source_freeze.py`` can pin
    hard rule 4a and 4b permanently. **Production callers must never pass
    either** -- the defaults ARE the contract. See the module docstring.
    """
    out: list[str] = []
    i, n = 0, len(text)
    in_str = False
    in_comment = False
    quote = ""
    while i < n:
        ch = text[i]
        if ch == "\n":
            in_comment = False
            # hard rule 4a: written through UNCHANGED, even inside a string.
            out.append(filler if (in_str and not keep_newlines) else "\n")
            i += 1
            continue
        if in_comment:
            out.append(" ")
            i += 1
            continue
        if in_str:
            if ch == "\\" and i + 1 < n:
                # An escape. Mask the backslash and let the loop re-dispatch on
                # the escaped character, so a backslash-newline still yields a
                # written-through newline.
                out.append(filler)
                i += 1
                if text[i] != "\n":
                    out.append(filler)
                    i += 1
                continue
            if ch == quote:
                out.append(ch)          # the delimiter is CODE
                in_str = False
                i += 1
                continue
            out.append(filler)
            i += 1
            continue
        if ch in "\"'":
            in_str, quote = True, ch
            out.append(ch)
            i += 1
            continue
        if ch == "#":
            in_comment = True
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
    masked = "".join(out)
    assert len(masked) == len(text), (
        "the R mask is not length-preserving -- offset slicing is unsafe: "
        f"{len(masked)} vs {len(text)}"
    )
    return masked


def _code_lines_from_mask(masked: str, original: str) -> list[str]:
    """Recover each line's CODE prefix by offset, from the mask's rstripped length.

    Deliberately does NOT assert alignment: ``test_source_freeze.py`` drives it
    with a hard-rule-4a-violating mask precisely to observe the misalignment.
    """
    out: list[str] = []
    for m_line, o_line in zip(masked.split("\n"), original.split("\n")):
        prefix = o_line[: len(m_line.rstrip())].rstrip()
        if prefix:
            out.append(prefix)
    return out


def _code_lines_r(text: str) -> list[str]:
    masked = _mask_r(text)
    assert masked.count("\n") == text.count("\n"), (
        "the R mask dropped or added a line break -- every subsequent line pair "
        "would be misaligned and the comparison would drift silently "
        "(hard rule 4a)"
    )
    return _code_lines_from_mask(masked, text)


def _r_symbol_spans(text: str) -> dict[str, tuple[int, int]]:
    masked = _mask_r(text)
    spans: dict[str, tuple[int, int]] = {}
    for m in _R_DEF_RE.finditer(masked):
        name = m.group(1)
        open_at = masked.find("{", m.end())
        if open_at == -1:
            continue
        depth, j = 0, open_at
        while j < len(masked):
            if masked[j] == "{":
                depth += 1
            elif masked[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            continue
        spans[name] = (m.start(), j + 1)
    return spans


# ==========================================================================
# Python -- ast, never a brace-walk
# ==========================================================================
_DOCSTRING_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _strip_to_code_py(text: str) -> str:
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, _DOCSTRING_OWNERS):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body.pop(0)
            if not body and not isinstance(node, ast.Module):
                body.append(ast.Pass())
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _line_start_offsets(text: str) -> list[int]:
    starts, pos = [0], 0
    for line in text.split("\n"):
        pos += len(line) + 1
        starts.append(pos)
    return starts


def _py_symbol_spans(text: str) -> dict[str, tuple[int, int]]:
    tree = ast.parse(text)
    starts = _line_start_offsets(text)
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        first = min([node.lineno] + [d.lineno for d in node.decorator_list])
        last = node.end_lineno or node.lineno
        spans[node.name] = (starts[first - 1], min(starts[last], len(text)))
    return spans


def _mask_strip_py(text: str) -> str:
    """The SECOND, independent Python implementation: a hand-written scanner.

    Comments are deleted; every string literal -- prefix, delimiters and
    contents, triple-quoted or not -- collapses to ``_PY_STR_TOKEN``. Used ONLY
    by ``test_source_freeze.py``'s cross-check against the ``ast`` path. It is
    NOT the primary implementation and no pin runs through it.
    """
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "#":
            nxt = text.find("\n", i)
            i = n if nxt == -1 else nxt
            continue
        if ch in "\"'":
            # Drop a string PREFIX (r / b / f / u, up to two chars) so the two
            # sides agree: ``ast.unparse`` does not preserve an ``r`` prefix.
            while (
                out
                and out[-1] in _PY_STR_PREFIX_CHARS
                and not (len(out) > 1 and (out[-2].isalnum() or out[-2] == "_"))
            ):
                out.pop()
            quote = text[i : i + 3] if text[i : i + 3] in ('"""', "'''") else ch
            qlen = len(quote)
            j = i + qlen
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j : j + qlen] == quote:
                    j += qlen
                    break
                j += 1
            else:
                j = n
            out.append(_PY_STR_TOKEN)
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def py_identifier_multiset(text: str) -> Counter:
    """Non-keyword identifiers of ``text``, string literals collapsed away.

    The cross-check currency in ``test_source_freeze.py``: robust to the
    formatting ``ast.unparse`` imposes (parentheses, trailing commas, line
    joins) while remaining sensitive to exactly the thing under test -- whether
    a comment, a docstring or a string literal was misclassified as code. A
    stripper that leaked a comment's or a docstring's words into the code stream
    shows up here immediately.

    ⚠ The lookbehind is load-bearing, not cosmetic. Without it the ``e`` of a
    scientific-notation literal (``1e-4`` at ``plink_ld_to_npz.py:234``) is
    tokenised as an identifier on the scanner side while ``ast.unparse``
    normalises the literal to ``0.0001`` and it vanishes -- a pure
    number-formatting artifact that would masquerade as a stripper disagreement.
    MEASURED: exactly 2 such tokens in ``plink_ld_to_npz.py``.
    """
    collapsed = _mask_strip_py(text)
    return Counter(
        tok
        for tok in re.findall(r"(?<![A-Za-z_0-9])[A-Za-z_][A-Za-z_0-9]*", collapsed)
        if tok != _PY_STR_TOKEN and not keyword.iskeyword(tok)
    )


# ==========================================================================
# Public API
# ==========================================================================
def strip_to_code(text: str, lang: str) -> str:
    """``text`` reduced to CODE: comments, docstrings, blank lines and trailing
    whitespace removed."""
    if lang == LANG_R:
        return "\n".join(_code_lines_r(text))
    if lang == LANG_PY:
        return "\n".join(code_lines(text, LANG_PY))
    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")


def code_lines(text: str, lang: str) -> list[str]:
    """The ordered CODE lines of ``text``. Order matters: a reordering is a
    change."""
    if lang == LANG_R:
        return _code_lines_r(text)
    if lang == LANG_PY:
        return [ln for ln in _strip_to_code_py(text).split("\n") if ln.strip()]
    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")


def symbol_spans(text: str, lang: str) -> dict[str, tuple[int, int]]:
    """``{name: (start_offset, end_offset)}`` for every top-level definition.

    R spans are found by brace-walking the MASK (so a brace inside a string or a
    comment cannot break the walk and a multi-line signature is handled);
    Python spans come from ``ast`` line numbers, decorators included.
    """
    if lang == LANG_R:
        return _r_symbol_spans(text)
    if lang == LANG_PY:
        return _py_symbol_spans(text)
    raise AssertionError(f"unsupported lang {lang!r}; expected {LANG_R!r} or {LANG_PY!r}")


def symbol_code(text: str, lang: str, name: str) -> list[str]:
    """The ordered CODE lines of one named top-level symbol."""
    spans = symbol_spans(text, lang)
    if name not in spans:
        raise AssertionError(
            f"symbol {name!r} was not found. Two hypotheses, both to be checked: "
            "either the symbol was renamed or deleted, or the extractor is "
            f"reading the wrong region. Found: {sorted(spans)}"
        )
    start, end = spans[name]
    return code_lines(text[start:end], lang)


@lru_cache(maxsize=None)
def git_show(ref: str, rel_path: str) -> str:
    """``<ref>:<rel_path>`` as text.

    Deliberately UNRESTRICTED as to ``ref`` -- the JOB B capture guards in
    ``test_qtl_coloc_allele_join.py`` need a symbolic revision, which is exactly
    what makes them timebomb-free. ``assert_code_frozen`` applies the SHA
    restriction itself, because a pin is a different thing from a read.
    """
    res = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    assert res.returncode == 0, (
        f"could not read {rel_path!r} at {ref!r}: {res.stderr.strip()}"
    )
    return res.stdout


def _repin_sentence(lang: str, pin_constant: str | None) -> str:
    if pin_constant is None:
        pin_constant = "R_CODE_REF" if lang == LANG_R else "PY_CODE_REF"
    return (
        "RE-PIN PROTOCOL: on an AUTHORIZED code change update EXACTLY ONE "
        f"constant -- {pin_constant} in tests/m3/test_source_freeze_pins.py -- "
        "to the landing commit's SHA, and nothing else. A comment or docstring "
        "change updates NOTHING. See DEC-2026-08-06-sr4-freeze-scope."
    )


def _first_difference(actual: list[str], reference: list[str]) -> str:
    for idx, (a, b) in enumerate(zip(actual, reference)):
        if a != b:
            return f"first difference at code-line index {idx}:\n  - {b}\n  + {a}"
    idx = min(len(actual), len(reference))
    if len(actual) > len(reference):
        return f"code line {idx} was ADDED:\n  + {actual[idx]}"
    return f"code line {idx} was REMOVED:\n  - {reference[idx]}"


def assert_code_frozen(
    rel_path: str,
    ref: str,
    lang: str,
    symbol: str | None = None,
    *,
    actual_text: str | None = None,
    pin_constant: str | None = None,
) -> None:
    """Assert the CODE of ``rel_path`` (or of one ``symbol`` in it) is identical
    to its code at ``ref``.

    ``actual_text`` is a **TEST-CONTROL SEAM, not a production parameter.** It is
    keyword-only, defaults to ``None``, and no production call site may pass it
    -- ``test_source_freeze.py`` enforces that permanently with an AST walk of
    every module in ``tests/m3/`` (a grep is evaded by ``actual_text = forged``
    and ``**{"actual_text": ...}``). Without the seam, three of this mechanism's
    own negative controls are unrunnable except by writing the working tree,
    which the bytecode-cache rule forbids
    (``[[feedback_negative_control_defeated_by_bytecode_cache]]``).

    The ACTUAL side is the WORKING TREE. See the module docstring: making it a
    committed read would blind every mid-test leak gate with nothing turning red.
    """
    assert _SHA_RE.match(ref), (
        f"the freeze ref {ref!r} is not an immutable revision. A symbolic name "
        "would make this gate permanently green with nothing ever able to turn "
        "it red -- the cheapest possible weakening. " + _repin_sentence(lang, pin_constant)
    )
    actual = actual_text if actual_text is not None else (PROJECT_ROOT / rel_path).read_text()
    reference = git_show(ref, rel_path)

    if symbol is None:
        got, want = code_lines(actual, lang), code_lines(reference, lang)
        subject = f"{rel_path} (whole file)"
    else:
        got, want = symbol_code(actual, lang, symbol), symbol_code(reference, lang, symbol)
        subject = f"{rel_path} :: symbol `{symbol}`"

    if got == want:
        return

    lead = f"`{symbol}`: " if symbol else ""
    raise AssertionError(
        f"{lead}the CODE of {subject} has MOVED off its pin {ref}.\n"
        "Comments, docstrings, blank lines and trailing whitespace are ignored "
        "by this comparison, so this is a REAL code change.\n"
        f"{_first_difference(got, want)}\n"
        f"(reference: {len(want)} code lines / actual: {len(got)} code lines)\n"
        "Two hypotheses, both to be checked: either the code moved, or the "
        "extractor is reading the wrong region.\n"
        + _repin_sentence(lang, pin_constant)
    )


def assert_unchanged_on_disk(
    path,
    expected_text: str,
    *,
    actual_text: str | None = None,
) -> None:
    """JOB B -- leak detection. A **SHA-FREE, BYTE-EXACT** comparison against the
    string the caller itself read.

    This is NOT the freeze gate and it is deliberately NOT comment-insensitive: a
    control that alters a source in memory must be caught leaking **any** byte
    onto the working tree, comments included. Being SHA-free it can never become
    a timebomb, and it is strictly stronger than the fixed-SHA byte diff it
    replaced -- but only when paired with a capture guard proving ``expected_text``
    was itself read from an unleaked tree.

    Same controls-only rule for ``actual_text`` as ``assert_code_frozen``.
    """
    on_disk = actual_text if actual_text is not None else Path(path).read_text()
    if on_disk == expected_text:
        return
    raise AssertionError(
        f"an in-memory alteration LEAKED onto the working tree at {path}.\n"
        f"(captured: {len(expected_text)} chars / on disk now: {len(on_disk)} chars)\n"
        "This is a byte comparison against the text this control itself read, "
        "so a leaked COMMENT is caught too -- a code-only check would have "
        "missed it. Restore the file with `git checkout --` before continuing."
    )
