"""``source_freeze``'s OWN proof -- the stripper cannot be fooled, and it was PROVEN.

The rescope in ``quick-260806-sr4`` replaced a whole-file BYTE pin on
``run_susie_rss.R`` with a comment-insensitive CODE pin. That trade has exactly
one way to go badly wrong, and it is **silent**: a stripper that mangles string
literals makes a REAL code change **invisible**, turning the guard into the
structurally-incapable-assertion class this project has been bitten by eight
times (``[[feedback_green_assertion_needs_a_negative_control]]``). Every control
here exists to make that failure mode observable.

THE CONTROLS ARE IN-MEMORY, PERMANENTLY
---------------------------------------
Nothing in this module writes the working tree and nothing re-imports. A
byte-length-identical edit reverted inside the same second runs STALE bytecode,
because ``importlib`` validates its cache on ``(mtime_seconds, size)``
(``[[feedback_negative_control_defeated_by_bytecode_cache]]``). Every fixture is
an in-memory string or a ``git show`` read, so ``NC-SR1`` .. ``NC-SR4``,
``NC-SR9`` and ``NC-SR10`` are permanent and in-suite rather than one-off
reverts that decay into a claim.

NO FIXTURE ANCHORS ON THE K-3 DIGITS
------------------------------------
``1,944``/``1,935`` are the most obviously unique numerals in
``run_susie_rss.R`` and they are a trap twice over: they live inside a COMMENT
(so a code-anchored control using them is dead on arrival) and ``T2`` deletes
them (so a comment-anchored control using them goes red in a task that never
touched this file). No fixture below anchors on them or on anything in
``run_susie_rss.R:1013-1025``.

NO SKIPS, BY CONSTRUCTION
-------------------------
Pure source text + ``git`` + stdlib. No R subprocess, no Snakemake, no
toolchain fixture -- so this module is structurally incapable of skipping and
cannot dilute the suite's fixed skip count.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from source_freeze import (  # noqa: E402
    LANG_PY,
    LANG_R,
    PROJECT_ROOT,
    assert_code_frozen,
    assert_unchanged_on_disk,
    code_lines,
    git_show,
    py_identifier_multiset,
    strip_to_code,
    symbol_code,
    symbol_spans,
)
from source_freeze import (  # noqa: E402
    _code_lines_from_mask,
    _mask_r,
    _strip_to_code_py,
)
# ⭐ An INDEPENDENT R comment-stripper that predates this utility, with string
# literal and backslash handling of its own. Deliberately NOT refactored (it
# backs a pre-existing absence assertion); consumed here as the R twin of the
# Python mask-vs-ast cross-check. Two independent implementations, one answer.
from test_qtl_coloc_allele_join import r_code_only  # noqa: E402

SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
SUSIE_R = PROJECT_ROOT / SUSIE_R_REL

PY_MODULE_RELS = (
    "src/python/plink_ld_to_npz.py",
    "src/python/condition_ld_matrix.py",
    "src/python/occlusion_span_filter.py",
)

#: ``run_susie_rss.R``'s CODE pin. A CODE PIN. Imported, never re-declared: the
#: R code pin is spelled exactly once in the repository, in
#: ``test_source_freeze_pins.py``. See DEC-2026-08-06-sr4-freeze-scope.
from test_source_freeze_pins import (  # noqa: E402
    PY_CODE_REF,
    R_CODE_REF,
    R_NUMERIC_SYMBOLS,
)

#: The five R symbols and a SECOND expected marker each. A symbol pin over an
#: empty or wrong slice is green forever, so extraction is proven non-vacuous
#: against something other than the name that selected it.
R_SYMBOL_MARKERS = {
    "regularize_ld": "eps",
    "run_susie_with_ladder": "max_iter_primary",
    "safe_region_id": "gsub",
    "load_ld_matrix": "match_indices_allele_aware",
    "assert_declared_ld_authoritative": "LD_DECLARED_REJECTED",
}

#: A comment anchor in ``run_susie_rss.R``, verified unique, far from the K-3
#: digits.
R_COMMENT_ANCHOR = "# THE TRAP (m3-04c Task 1b)"

#: The single ``toJSON`` emit that is unique in the raw text (the other two, at
#: ``:938`` and ``:970``, are byte-identical to each other). It lives at
#: ``:1357`` -- inside the ~700-line top-level main body that is inside NO
#: function, which is what NC-SR4 is about.
R_TOPLEVEL_EMIT = (
    'write(toJSON(result, auto_unbox = TRUE, pretty = TRUE, na = "null"), '
    "file = opt$output)"
)

#: The first line of ``option_list <- list(``'s block: the start of the
#: top-level main body.
R_MAIN_BODY_ANCHOR = "option_list <- list("


# ==========================================================================
# THE CONTRAST STRIPPER -- lives HERE, never in the utility
# ==========================================================================
def _naive_strip_for_contrast(text: str) -> str:
    """The obvious wrong implementation: ``#`` to end of line, unconditionally.

    Shipped in the TEST module only. Its job is to be **blind** to NC-SR3's
    fixture, which is what proves the concealment hazard is real rather than
    argued. Without this contrast, NC-SR3 would prove only that *some* edit is
    detectable.
    """
    return "\n".join(re.sub(r"#.*$", "", line) for line in text.split("\n"))


# ==========================================================================
# FIXTURE BUILDERS -- every one asserts its anchor is unique before perturbing
# ==========================================================================
def _read(rel: str) -> str:
    return (PROJECT_ROOT / rel).read_text()


def _unique(text: str, anchor: str, what: str) -> None:
    assert text.count(anchor) == 1, (
        f"the {what} anchor {anchor!r} occurs {text.count(anchor)} times, not "
        "once -- the control would be altering nothing (or altering too much) "
        "and would pass for free"
    )


def _first_unique_comment_line(text: str) -> str:
    """The first whole-line ``#`` comment that occurs exactly once."""
    for line in text.split("\n"):
        if line.lstrip().startswith("#") and text.count(line) == 1 and line.strip():
            return line
    raise AssertionError("no unique whole-line comment found -- fixture impossible")


def _py_first_symbol_def_line(text: str) -> tuple[str, str]:
    """``(symbol_name, its def/class line)`` for the first top-level symbol."""
    spans = symbol_spans(text, LANG_PY)
    name, (start, end) = min(spans.items(), key=lambda kv: kv[1][0])
    for line in text[start:end].split("\n"):
        stripped = line.strip()
        if stripped.startswith(("def ", "async def ", "class ")):
            return name, line
    raise AssertionError(f"no def/class line found for {name!r}")


# ==========================================================================
# (a) / (b) -- comment and docstring edits are INVISIBLE
# ==========================================================================
@pytest.mark.parametrize("rel", (SUSIE_R_REL,) + PY_MODULE_RELS)
def test_a_comment_only_edit_is_invisible(rel):
    text = _read(rel)
    lang = LANG_R if rel.endswith(".R") else LANG_PY
    if lang == LANG_R:
        anchor = R_COMMENT_ANCHOR
    else:
        anchor = _first_unique_comment_line(text)
    _unique(text, anchor, "comment")
    perturbed = text.replace(anchor, anchor + " [sr4 comment fixture]", 1)
    # NON-VACUITY: a no-op replacement would make this pass for free.
    assert perturbed != text
    assert code_lines(perturbed, lang) == code_lines(text, lang), (
        f"{rel}: a COMMENT-only edit moved the code view -- the whole rescope "
        "is void if this is not true"
    )


@pytest.mark.parametrize("rel", PY_MODULE_RELS)
def test_a_docstring_only_edit_is_invisible(rel):
    text = _read(rel)
    tree = ast.parse(text)
    head = tree.body[0]
    assert isinstance(head, ast.Expr) and isinstance(head.value, ast.Constant), (
        f"{rel} has no module docstring -- the fixture assumption has moved"
    )
    first_line = head.value.value.split("\n")[0]
    assert first_line.strip(), f"{rel}'s module docstring starts with a blank line"
    _unique(text, first_line, "docstring")
    perturbed = text.replace(first_line, first_line + " [sr4 docstring fixture]", 1)
    assert perturbed != text                      # non-vacuity
    assert code_lines(perturbed, LANG_PY) == code_lines(text, LANG_PY)


# ==========================================================================
# NC-SR1 -- a CODE edit IS detected
# ==========================================================================
@pytest.mark.parametrize("rel", (SUSIE_R_REL,) + PY_MODULE_RELS)
def test_nc_sr1_a_code_edit_is_detected(rel):
    text = _read(rel)
    if rel.endswith(".R"):
        lang = LANG_R
        anchor = "regularize_ld <- function(R, eps = 1e-4) {"
        _unique(text, anchor, "R code")
        perturbed = text.replace(anchor, anchor.replace("1e-4", "1e-3"), 1)
    else:
        lang = LANG_PY
        name, anchor = _py_first_symbol_def_line(text)
        _unique(text, anchor, "python code")
        perturbed = text.replace(anchor, anchor.replace(name, name + "_sr4nc1", 1), 1)
    assert perturbed != text                      # non-vacuity
    assert code_lines(perturbed, lang) != code_lines(text, lang), (
        f"{rel}: a CODE edit was INVISIBLE to the stripper -- the guard is not "
        "guarding"
    )


# ==========================================================================
# NC-SR2 -- a code edit inside a named symbol NAMES that symbol
# ==========================================================================
def _perturb_inside_r_symbol(text: str, symbol: str) -> str:
    """Insert a statement after the first uniquely-locatable code line of
    ``symbol``. Mechanical -- nothing is hand-transcribed."""
    for line in symbol_code(text, LANG_R, symbol)[1:]:
        needle = "\n" + line + "\n"
        if text.count(needle) == 1:
            return text.replace(needle, needle + "ZZZ_SR4_NC2_PERTURBATION <- 1\n", 1)
    raise AssertionError(
        f"no uniquely-locatable code line inside {symbol!r} -- fixture impossible"
    )


@pytest.mark.parametrize("symbol", R_NUMERIC_SYMBOLS)
def test_nc_sr2_a_code_edit_inside_a_named_symbol_names_that_symbol(symbol):
    real = SUSIE_R.read_text()
    perturbed = _perturb_inside_r_symbol(real, symbol)
    assert perturbed != real
    with pytest.raises(AssertionError, match=symbol):
        assert_code_frozen(
            SUSIE_R_REL, R_CODE_REF, LANG_R, symbol=symbol, actual_text=perturbed
        )
    # the working tree was never written
    assert SUSIE_R.read_text() == real


def test_nc_sr2_the_message_carries_the_repin_instruction_and_both_hypotheses():
    real = SUSIE_R.read_text()
    perturbed = _perturb_inside_r_symbol(real, "regularize_ld")
    with pytest.raises(AssertionError) as excinfo:
        assert_code_frozen(
            SUSIE_R_REL, R_CODE_REF, LANG_R, symbol="regularize_ld",
            actual_text=perturbed,
        )
    msg = str(excinfo.value)
    assert "R_CODE_REF" in msg
    assert "EXACTLY ONE" in msg
    assert "either the code moved, or the extractor is reading the wrong region" in msg
    assert SUSIE_R.read_text() == real


# ==========================================================================
# NC-SR3 -- ⚠ THE LOAD-BEARING CONTROL
# a code change CONCEALED behind a '#' INSIDE A STRING LITERAL
# ==========================================================================
# No live file has a '#' inside an EXECUTABLE string literal (measured: 0 in all
# four), so the carrier MUST be synthesised. That is the point: the hazard is
# latent, not absent, and a latent hazard with no control is how a guard rots.
def _r_concealment_fixtures() -> tuple[str, str]:
    real = SUSIE_R.read_text()
    sig = "regularize_ld <- function(R, eps = 1e-4) {"
    _unique(real, sig, "NC-SR3 R carrier")
    carrier_line = '  .tag <- gsub("#.*", "", "regularize#v1")'
    carrier = real.replace(sig, sig + "\n" + carrier_line, 1)
    concealed = carrier.replace(carrier_line, carrier_line + "; eps <- 1e-3", 1)
    return carrier, concealed


def _py_concealment_fixtures() -> tuple[str, str]:
    real = _read("src/python/condition_ld_matrix.py")
    at = real.index("\ndef ") + 1
    body = '    return re.sub("#.*", "", "cond#v1")'
    helper = "def _sr4_carrier():\n" + body + "\n\n\n"
    carrier = real[:at] + helper + real[at:]
    concealed = carrier.replace(body, body + " or (1e-3)", 1)
    return carrier, concealed


@pytest.mark.parametrize(
    "lang,builder",
    [(LANG_R, _r_concealment_fixtures), (LANG_PY, _py_concealment_fixtures)],
)
def test_nc_sr3_a_code_edit_concealed_behind_a_hash_in_a_string_is_detected(lang, builder):
    carrier, concealed = builder()
    assert concealed != carrier

    # HALF 1 -- the hazard is REAL: the obvious implementation is BLIND to it.
    assert _naive_strip_for_contrast(carrier) == _naive_strip_for_contrast(concealed), (
        "the naive '#-to-end-of-line' stripper was NOT blind to this fixture, so "
        "the fixture does not exercise the concealment hazard and NC-SR3 proves "
        "nothing -- rebuild the fixture rather than relaxing this assertion"
    )

    # HALF 2 -- the utility SEES it.
    assert code_lines(carrier, lang) != code_lines(concealed, lang), (
        "a code change concealed after a '#' INSIDE A STRING LITERAL was "
        "invisible to source_freeze -- the guard is strictly worse than the "
        "byte pin it replaced"
    )


# ==========================================================================
# NC-SR4 -- the whole-file floor covers what NO symbol pin does
# ==========================================================================
def _line_of_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def test_nc_sr4_the_top_level_main_body_is_inside_no_named_symbol():
    """Prove the GAP first. ~700 lines of run_susie_rss.R -- the fitting flow and
    all three ``toJSON`` emits -- live inside no function at all."""
    text = SUSIE_R.read_text()
    _unique(text, R_MAIN_BODY_ANCHOR, "main body")
    body_start = _line_of_offset(text, text.index(R_MAIN_BODY_ANCHOR))
    body_end = text.count("\n") + 1
    assert body_end - body_start > 600, (
        f"the top-level main body is only {body_end - body_start} lines -- the "
        "premise of the floor has moved"
    )
    spans = symbol_spans(text, LANG_R)
    for name in R_NUMERIC_SYMBOLS:
        start, end = spans[name]
        assert _line_of_offset(text, end - 1) < body_start, (
            f"{name} extends past :{body_start}; the main body is NOT outside "
            "every symbol and NC-SR4's premise has moved"
        )
    for emit_line in (938, 970, 1357):
        assert emit_line >= body_start


def test_nc_sr4_the_whole_file_floor_catches_what_all_five_symbol_pins_miss():
    real = SUSIE_R.read_text()
    _unique(real, R_TOPLEVEL_EMIT, "NC-SR4 emit")
    perturbed = real.replace(
        R_TOPLEVEL_EMIT, R_TOPLEVEL_EMIT.replace("pretty = TRUE", "pretty = FALSE"), 1
    )
    assert perturbed != real

    with pytest.raises(AssertionError, match="whole file"):
        assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R, actual_text=perturbed)

    for symbol in R_NUMERIC_SYMBOLS:
        assert_code_frozen(
            SUSIE_R_REL, R_CODE_REF, LANG_R, symbol=symbol, actual_text=perturbed
        )
    assert SUSIE_R.read_text() == real


# ==========================================================================
# (g) / (j) -- two independent implementations, one answer
# ==========================================================================
@pytest.mark.parametrize("rel", PY_MODULE_RELS)
def test_the_python_mask_stripper_agrees_with_the_ast_canonicaliser(rel):
    """The hand-written scanner and ``ast`` must classify comments, docstrings
    and string literals identically.

    Compared on a whitespace- and formatting-insensitive currency (the
    non-keyword identifier multiset with string literals collapsed), because
    ``ast.unparse`` reformats: it drops redundant parentheses and trailing
    commas, joins continuation lines and normalises numeric literals. A
    misclassified comment or docstring leaks its WORDS into one side's stream
    and shows up immediately.
    """
    text = _read(rel)
    scanner_side = py_identifier_multiset(text)
    ast_side = py_identifier_multiset(_strip_to_code_py(text))
    assert scanner_side == ast_side, (
        f"{rel}: the two independent Python implementations disagree.\n"
        f"only the scanner saw: {dict((scanner_side - ast_side).most_common(12))}\n"
        f"only ast saw:         {dict((ast_side - scanner_side).most_common(12))}"
    )
    assert scanner_side, "the multiset is EMPTY -- the cross-check is vacuous"


def _r_code_only_lines(text: str) -> list[str]:
    return [ln.rstrip() for ln in r_code_only(text).split("\n") if ln.strip()]


def test_the_r_mask_agrees_with_the_pre_existing_r_code_only():
    """The R twin of the cross-check, against an implementation this plan did
    NOT write.

    ``r_code_only`` (``test_qtl_coloc_allele_join.py``) is an independent R
    stripper with its own string-literal and backslash handling, and it is the
    substrate of a pre-existing absence assertion. If these two disagree, that
    is a finding ABOUT ``r_code_only`` and a STOP -- never a licence to weaken
    either side.
    """
    real = SUSIE_R.read_text()
    carrier, concealed = _r_concealment_fixtures()
    comment_edit = real.replace(
        R_COMMENT_ANCHOR, R_COMMENT_ANCHOR + " [sr4 comment fixture]", 1
    )
    for label, text in (
        ("run_susie_rss.R", real),
        ("comment-perturbed", comment_edit),
        ("NC-SR3 carrier", carrier),
        ("NC-SR3 concealed", concealed),
    ):
        assert code_lines(text, LANG_R) == _r_code_only_lines(text), f"disagreement on {label}"


# ==========================================================================
# (h) / (i) / (k) -- extraction and the two mask invariants
# ==========================================================================
@pytest.mark.parametrize("symbol", R_NUMERIC_SYMBOLS)
def test_symbol_extraction_is_non_vacuous(symbol):
    text = SUSIE_R.read_text()
    matches = re.findall(
        rf"^{re.escape(symbol)}\s*<-\s*function", text, flags=re.M
    )
    assert len(matches) == 1, f"{symbol} is defined {len(matches)} times, not once"
    lines = symbol_code(text, LANG_R, symbol)
    assert lines, f"{symbol} extracted an EMPTY slice -- a pin over it is green forever"
    marker = R_SYMBOL_MARKERS[symbol]
    assert any(marker in ln for ln in lines), (
        f"{symbol}'s extracted code does not contain its second marker "
        f"{marker!r} -- the extractor is reading the wrong region"
    )


@pytest.mark.parametrize("rel", (SUSIE_R_REL,) + PY_MODULE_RELS)
def test_the_mask_is_length_preserving(rel):
    text = _read(rel)
    assert len(_mask_r(text)) == len(text)


def test_the_mask_invariants_are_load_bearing():
    """hard rule 4 -- pinned SYNTHETICALLY, because no live file exercises either.

    ⚠ ``len(masked) == len(text)`` is BLIND to (4a): it holds under BOTH
    variants, which is exactly why the length test above is not sufficient
    evidence and this one has to exist.
    """
    fixture = 'q <- "line1\nline2 trailing   \nend"'

    correct = _code_lines_from_mask(_mask_r(fixture), fixture)
    filled_newlines = _code_lines_from_mask(
        _mask_r(fixture, keep_newlines=False), fixture
    )
    space_filler = _code_lines_from_mask(_mask_r(fixture, filler=" "), fixture)

    # (4a) filling a newline inside a string DELETES lines and misaligns every
    # subsequent zip() pair.
    assert correct == ['q <- "line1', "line2 trailing", 'end"']
    assert filled_newlines == ['q <- "line1']
    assert correct != filled_newlines
    assert any("line2 trailing" in ln for ln in correct)
    assert not any("line2 trailing" in ln for ln in filled_newlines)

    # the length invariant is BLIND to 4a -- demonstrated, not asserted
    assert len(_mask_r(fixture, keep_newlines=False)) == len(fixture)

    # (4b) a WHITESPACE filler loses a multi-line string's content to rstrip()
    assert space_filler == ['q <- "', 'end"']
    assert correct != space_filler
    assert not any("line2 trailing" in ln for ln in space_filler)

    # the production defaults ARE the contract
    import inspect

    params = inspect.signature(_mask_r).parameters
    assert params["filler"].default == "_"
    assert params["keep_newlines"].default is True

    # and on the real file the bug is INVISIBLE -- 818 either way. That is why a
    # synthetic pin is the only thing that can hold this invariant.
    real = SUSIE_R.read_text()
    assert len(code_lines(real, LANG_R)) == 818
    assert len(_code_lines_from_mask(_mask_r(real, keep_newlines=False), real)) == 818


# ==========================================================================
# NC-SR10 / (m) / (n) -- the three cheap weakenings, each closed
# ==========================================================================
#: ⚠ MODULE SCOPE, deliberately -- it survives an ``_read_actual()`` extraction
#: that a function-scoped check inside one test would not. Evaluated with the
#: plan's OWN stripper because ``source_freeze``'s docstring literally quotes the
#: forbidden call, so a raw substring check over the file would be RED AT BIRTH.
_SOURCE_FREEZE_CODE = strip_to_code(
    (_THIS_DIR / "source_freeze.py").read_text(), LANG_PY
)
assert '"HEAD"' not in _SOURCE_FREEZE_CODE and "'HEAD'" not in _SOURCE_FREEZE_CODE, (
    "source_freeze's EXECUTABLE code names the symbolic revision. If the ACTUAL "
    "side of assert_code_frozen became a committed read, every mid-test leak "
    "gate (test_finemap_receipt_early_exit.py:341/:357, NC-2g) would go blind to "
    "an uncommitted working-tree write with NOTHING turning red."
)


def test_nc_sr10_the_actual_side_is_the_working_tree_not_the_index():
    real = SUSIE_R.read_text()
    perturbed = _perturb_inside_r_symbol(real, "regularize_ld")
    with pytest.raises(AssertionError):
        assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R, actual_text=perturbed)
    assert '"HEAD"' not in _SOURCE_FREEZE_CODE
    assert "'HEAD'" not in _SOURCE_FREEZE_CODE


def test_no_production_call_site_supplies_the_control_seam():
    """The ``actual_text=`` seam is for CONTROLS ONLY.

    An AST walk, not a grep: ``actual_text = forged`` (spaces) and
    ``**{"actual_text": ...}`` both evade a substring scan -- verified. A
    ``**`` unpack into either assertion is rejected too, since it can smuggle
    the seam past a keyword-name check.
    """
    guarded = {"assert_code_frozen", "assert_unchanged_on_disk"}
    offenders, seen = [], 0
    for path in sorted(_THIS_DIR.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name not in guarded:
                continue
            seen += 1
            for kw in node.keywords:
                if kw.arg == "actual_text" or kw.arg is None:
                    offenders.append(f"{path.name}:{node.lineno} -> {name}({kw.arg})")
    # NON-VACUITY: "no offenders" is evidence only if the walk actually resolves
    # calls. A broken glob or a renamed helper would otherwise make this test
    # green forever -- the exact failure class it exists to prevent.
    assert seen >= 1, (
        "the walk found ZERO calls to assert_code_frozen / "
        "assert_unchanged_on_disk anywhere in tests/m3/, so 'no offenders' "
        "proves nothing -- the guarded names or the glob have moved"
    )
    assert not offenders, (
        "a PRODUCTION call site supplies the test-control seam, so its assertion "
        "no longer reads the working tree: " + "; ".join(offenders)
    )


# ==========================================================================
# NC-SR9 -- the rewired JOB B leak check can still FAIL
# ==========================================================================
# Lands HERE, not in test_qtl_coloc_allele_join.py, so no assertion count moves
# in a pre-existing module.
def test_nc_sr9_the_job_b_leak_check_detects_a_leak():
    """JOB B replaced ``git diff --exit-code <SHA>`` with a SHA-free byte
    comparison. That is only a strengthening if it can still go RED."""
    real = SUSIE_R.read_text()

    # a leaked CODE line
    with pytest.raises(AssertionError, match="LEAKED"):
        assert_unchanged_on_disk(
            SUSIE_R, real, actual_text=real + "\nZZZ_SR4_LEAK <- 1\n"
        )
    # ...and a leaked COMMENT, which the code-only JOB A gate would deliberately
    # let through. This is exactly why JOB B was NOT made comment-insensitive.
    with pytest.raises(AssertionError, match="LEAKED"):
        assert_unchanged_on_disk(SUSIE_R, real, actual_text=real + "\n# leaked\n")

    # non-vacuity: the unleaked case passes
    assert_unchanged_on_disk(SUSIE_R, real)
    assert SUSIE_R.read_text() == real


def test_nc_sr9_the_capture_guards_are_present_at_both_job_b_sites():
    """Without a capture guard, JOB B is a coverage REDUCTION.

    For a leak that occurred BEFORE ``real = SUSIE_R.read_text()``, ``real``
    holds the already-leaked bytes and the byte comparison passes where the old
    fixed-SHA diff went red. Both guards are asserted present, mechanically.
    """
    source = (_THIS_DIR / "test_qtl_coloc_allele_join.py").read_text()
    guards = source.count('git_show("HEAD", SUSIE_R_REL)')
    leak_checks = source.count("assert_unchanged_on_disk(SUSIE_R, real)")
    assert guards == 2, f"expected 2 capture guards, found {guards}"
    assert leak_checks == 2, f"expected 2 JOB B leak checks, found {leak_checks}"


def test_a_non_sha_ref_is_rejected():
    """A symbolic ref would make every gate permanently green, and a 7-hex sweep
    would never notice it."""
    for bad in ("HEAD", "main", "HEAD~1", "bf04199^", ""):
        with pytest.raises(AssertionError, match="immutable revision"):
            assert_code_frozen(SUSIE_R_REL, bad, LANG_R)
    # ...while the real pins are accepted (non-vacuity for the rejection).
    assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R)
    assert_code_frozen(PY_MODULE_RELS[1], PY_CODE_REF, LANG_PY)


def test_git_show_stays_unrestricted_so_the_capture_guards_can_use_a_symbolic_ref():
    """JOB B's capture guard needs a symbolic revision -- that is precisely what
    makes it timebomb-free. The SHA restriction belongs to the PIN, not the read."""
    import subprocess

    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    symbolic = git_show("HEAD", SUSIE_R_REL)
    assert symbolic, "a symbolic read returned nothing"
    assert symbolic == git_show(head_sha, SUSIE_R_REL)
    # ...and the same symbolic name is REFUSED as a pin. One mechanism, two
    # deliberately different contracts.
    with pytest.raises(AssertionError, match="immutable revision"):
        assert_code_frozen(SUSIE_R_REL, "HEAD", LANG_R)
