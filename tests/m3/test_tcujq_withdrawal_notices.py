"""THE NAMED ENFORCER for the tcujq WITHDRAWN-by-trsx5 docstring notices.

Decision: ``DEC-2026-09-16-condition-ld-matrix-freeze-code-only`` (Carter,
2026-09-16), landed by ``quick-260916-oyq``.

WHAT IT PINS
------------
``src/python/condition_ld_matrix.py`` and ``src/python/write_conditioned_ld_npz.py``
still carry their original 2026-07 wording, which calls the off-diagonal
``NaN -> 0`` zeroing "pre-registered". That was TRUE when written (OSF file tcujq,
posted 2026-07-04) and was later WITHDRAWN by the amendment-update OSF file trsx5
(posted 2026-07-10). The honest correction is ADDITIVE: a WITHDRAWN POLICY NOTICE
at the top of each module docstring (plus a short one in the
``condition_ld_matrix()`` function docstring) that quotes the POSTED trsx5
withdrawal sentence verbatim. The history is kept, and no code moves.

This file checks that:

- each module DOCSTRING holds exactly one notice block, beginning within the
  first lines of the docstring, whose BODY names tcujq, trsx5, both posting
  dates, the replacement policy, the pipeline status and the decision id, and
  contains the whitespace-normalised POSTED withdrawal sentence (read from the
  byte-exact reconstruction of the posted body, size checked FIRST, then md5);
- the ``condition_ld_matrix()`` FUNCTION docstring carries its short notice in
  its first lines;
- neither module has a caller in the pipeline.

BEHAVIOUR, NOT TEXT
-------------------
The docstrings are read the way Python reads them: ``ast.parse`` +
``ast.get_docstring``, never a grep. A notice moved into a ``#`` comment or
into a module-level string constant keeps every token in the file TEXT, so a
text grep would stay green, and it must still go RED here. The file carries its
own negative controls on a synthetic module (each must raise its SPECIFIC
message), including the two "moved" controls, which also assert that a grep
WOULD have been green.

"THE PIPELINE", OPERATIONALLY
-----------------------------
"Not called by the pipeline" means: no TRACKED file under ``Snakefile``,
``src/``, ``scripts/``, ``bin/`` or ``tools/`` imports either module, names it
as a script path in a non-docstring string constant (``.py`` files, via
``ast``), or mentions it at all (``.smk``, ``.sh``, ``.R``, ``.yaml``,
``.yml``, ``.ipynb`` and ``Snakefile`` files, as text). LIMIT, stated rather
than sold as coverage: untracked files and anything outside those paths are
NOT scanned. The scan has a must-be-identity non-vacuity check (the ONLY
importer of ``condition_ld_matrix`` is ``write_conditioned_ld_npz.py``) and
positive controls for both other detectors.

The positive-control anchor files (``m3_occlusion_lockstep.smk``,
``run_ld_build_plan.py``) are LIVE DATA. If one is renamed or stops naming its
stem, that is a re-measure decision, not a fixup: find another observed
positive before touching the constant.

NO SKIPS, NO NETWORK, NOTHING WRITTEN -- stdlib + pytest + ``git ls-files``.
"""
from __future__ import annotations

import ast
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NOTICE_MODULES = ("src/python/condition_ld_matrix.py", "src/python/write_conditioned_ld_npz.py")
NOTICE_MODULE_IDS = ("condition_ld_matrix", "write_conditioned_ld_npz")
NOTICE_FUNCTIONS = (("src/python/condition_ld_matrix.py", "condition_ld_matrix"),)

#: The byte-exact reconstruction of the POSTED trsx5 body. Size adjudicates
#: first (it is checked before the md5), then the md5.
POSTED_TRSX5_REL = ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt"
POSTED_TRSX5_SIZE = 9695
POSTED_TRSX5_MD5 = "c19be8b2ad7cd6a45fee1d668d8a9cf9"
POSTED_WITHDRAWAL_LINE = 19          # 1-based, via str.splitlines(); the file has NO trailing newline (wc -l says 58)
POSTED_SENTENCE_PREFIX = "The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries"
POSTED_SENTENCE_END = "is withdrawn."

NOTICE_BEGIN = "==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5)"
NOTICE_END = "==== END WITHDRAWN POLICY NOTICE ===="
NOTICE_MAX_START_LINE = 4            # 0-based index into ast.get_docstring(clean=True).split("\n")
FUNCTION_NOTICE_WINDOW = 7           # the function notice must sit in the first 7 docstring lines
MODULE_BODY_TOKENS = (
    "withdrawn",
    "tcujq",
    "trsx5",
    "2026-07-04",
    "2026-07-10",
    "exclude-in-lockstep",
    "not called by the pipeline",
    "dec-2026-09-16-condition-ld-matrix-freeze-code-only",
)
FUNCTION_TOKENS = ("withdrawn", "tcujq", "trsx5", "2026-07-10", "withdrawn policy notice")

PIPELINE_PATHSPECS = ("Snakefile", "src/", "scripts/", "bin/", "tools/")
NON_PY_SUFFIXES = (".smk", ".sh", ".R", ".r", ".yaml", ".yml", ".ipynb")
NOTICE_STEMS = ("condition_ld_matrix", "write_conditioned_ld_npz")
#: Observed positives for the two non-importer detectors (live data; see the module docstring).
POSITIVE_TEXT_HIT = ("occlusion_span_filter", "src/snakemake/rules/m3_occlusion_lockstep.smk")
POSITIVE_SCRIPT_PATH_HIT = ("build_ld_rds", "src/legacy/region_analysis/scripts/run_ld_build_plan.py")

_DOC_OWNERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


# ==========================================================================
# Helpers -- the assertion messages are load-bearing: the controls match them
# ==========================================================================
def _norm(s: str) -> str:
    return " ".join(s.split()).casefold()


def posted_withdrawal_sentence() -> str:
    """The POSTED trsx5 withdrawal sentence, up to and including ``is withdrawn.``."""
    raw = (PROJECT_ROOT / POSTED_TRSX5_REL).read_bytes()
    assert len(raw) == POSTED_TRSX5_SIZE, (
        f"the posted trsx5 reconstruction is {len(raw)} B, not {POSTED_TRSX5_SIZE} B -- "
        "it is no longer the byte-exact posted body"
    )
    digest = hashlib.md5(raw).hexdigest()
    assert digest == POSTED_TRSX5_MD5, (
        f"the posted trsx5 reconstruction has md5 {digest}, not {POSTED_TRSX5_MD5}"
    )
    lines = raw.decode("utf-8").splitlines()
    line = lines[POSTED_WITHDRAWAL_LINE - 1]
    assert line.startswith(POSTED_SENTENCE_PREFIX), (
        f"posted trsx5 line {POSTED_WITHDRAWAL_LINE} does not start with the withdrawal sentence: {line[:80]!r}"
    )
    assert POSTED_SENTENCE_END in line, (
        f"posted trsx5 line {POSTED_WITHDRAWAL_LINE} does not contain {POSTED_SENTENCE_END!r}"
    )
    return line[: line.index(POSTED_SENTENCE_END) + len(POSTED_SENTENCE_END)]


def notice_body(source: str, where: str) -> str:
    """The lines STRICTLY between the notice markers of the MODULE docstring."""
    doc = ast.get_docstring(ast.parse(source), clean=True)
    assert doc, f"{where}: NO module docstring"
    lines = doc.split("\n")
    begins = [i for i, ln in enumerate(lines) if ln.strip().startswith(NOTICE_BEGIN)]
    assert len(begins) == 1, (
        f"{where}: the module DOCSTRING holds {len(begins)} WITHDRAWN POLICY NOTICE blocks, not exactly 1"
    )
    ends = [i for i, ln in enumerate(lines) if ln.strip() == NOTICE_END]
    assert len(ends) == 1 and ends[0] > begins[0], (
        f"{where}: the notice END marker is missing, duplicated or precedes BEGIN"
    )
    assert begins[0] <= NOTICE_MAX_START_LINE, (
        f"{where}: the notice begins at docstring line {begins[0]} (> {NOTICE_MAX_START_LINE}) -- not prominent"
    )
    return "\n".join(lines[begins[0] + 1: ends[0]])


def assert_module_notice(source: str, where: str) -> None:
    body = _norm(notice_body(source, where))
    for tok in MODULE_BODY_TOKENS:
        assert tok in body, f"{where}: required token {tok!r} is missing from the notice BODY"
    assert _norm(posted_withdrawal_sentence()) in body, (
        f"{where}: the verbatim POSTED trsx5 withdrawal sentence is missing from the notice BODY"
    )


def assert_function_notice(source: str, func: str, where: str) -> None:
    nodes = [
        n for n in ast.parse(source).body
        if isinstance(n, ast.FunctionDef) and n.name == func
    ]
    assert len(nodes) == 1, (
        f"{where}: {len(nodes)} top-level functions named {func!r}, not exactly 1"
    )
    doc = ast.get_docstring(nodes[0], clean=True) or ""
    head = _norm("\n".join(doc.split("\n")[:FUNCTION_NOTICE_WINDOW]))
    for tok in FUNCTION_TOKENS:
        assert tok in head, (
            f"{where}::{func}: required token {tok!r} is missing from the first "
            f"{FUNCTION_NOTICE_WINDOW} lines of the FUNCTION docstring"
        )


def _docstring_constant_ids(tree: ast.AST) -> set[int]:
    """Same owner rule as source_freeze: the first-statement ``Expr(Constant str)``
    of a Module / FunctionDef / AsyncFunctionDef / ClassDef."""
    ids = set()
    for node in ast.walk(tree):
        if not isinstance(node, _DOC_OWNERS) or not node.body:
            continue
        head = node.body[0]
        if (isinstance(head, ast.Expr) and isinstance(head.value, ast.Constant)
                and isinstance(head.value.value, str)):
            ids.add(id(head.value))
    return ids


def py_hits(source: str, stem: str, rel_stem: str) -> tuple[bool, bool]:
    """PURE classifier of one ``.py`` source for one module ``stem``.

    Returns ``(importer, script_path)``:
    - importer: an ``import`` alias, or a ``from`` module / alias, whose LAST
      dotted component is ``stem``;
    - script_path: a NON-docstring ``str`` constant containing ``<stem>.py``,
      counted only when ``rel_stem != stem`` (a module is never its own caller).
    """
    tree = ast.parse(source)
    docs = _docstring_constant_ids(tree)
    importer = script_path = False
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""] + [a.name for a in node.names]
        if any(name.split(".")[-1] == stem for name in names):
            importer = True
        if (rel_stem != stem and isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docs and f"{stem}.py" in node.value):
            script_path = True
    return importer, script_path


def pipeline_scan(stems) -> dict:
    """ONE pass over the TRACKED pipeline files (see the module docstring for the limit)."""
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--", *PIPELINE_PATHSPECS],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    rels = [r for r in listing.split("\0") if r]
    out = {
        "n_py": 0,
        "n_other": 0,
        "importers": {s: set() for s in stems},
        "script_path": {s: set() for s in stems},
        "text": {s: set() for s in stems},
    }
    for rel in rels:
        path = PROJECT_ROOT / rel
        if rel.endswith(".py"):
            out["n_py"] += 1
            source = path.read_text(encoding="utf-8")        # unreadable = an ERROR, never a skip
            for stem in stems:
                importer, script_path = py_hits(source, stem, Path(rel).stem)
                if importer:
                    out["importers"][stem].add(rel)
                if script_path:
                    out["script_path"][stem].add(rel)
        elif rel.endswith(NON_PY_SUFFIXES) or Path(rel).name == "Snakefile":
            out["n_other"] += 1
            text = path.read_text(encoding="utf-8", errors="replace")   # unreadable = an ERROR
            for stem in stems:
                if stem in text:
                    out["text"][stem].add(rel)
    return out


# ==========================================================================
# Mutation helpers -- PURE str -> str, reused on the REAL texts by the task's
# one-shot controls. Every mutation must CHANGE the source and still PARSE, so a
# RED can never be a SyntaxError masquerade.
# ==========================================================================
_FUTURE_LINE = "from __future__ import annotations"


def _checked(source: str, mutated: str) -> str:
    assert mutated != source, "the mutation did not change the source -- the control would be vacuous"
    ast.parse(mutated)
    return mutated


def _module_block_span(source: str) -> tuple[list[str], int, int]:
    lines = source.split("\n")
    begins = [i for i, ln in enumerate(lines) if ln.strip().startswith(NOTICE_BEGIN)]
    assert begins, "no WITHDRAWN POLICY NOTICE block in the RAW text to mutate"
    b = begins[0]
    ends = [i for i in range(b + 1, len(lines)) if lines[i].strip() == NOTICE_END]
    assert ends, "the RAW notice block has no END marker to mutate"
    return lines, b, ends[0]


def _insert_after_future(lines: list[str], insert: list[str]) -> list[str]:
    assert lines.count(_FUTURE_LINE) == 1, f"expected exactly one {_FUTURE_LINE!r} line"
    at = lines.index(_FUTURE_LINE) + 1
    return lines[:at] + insert + lines[at:]


def mutate_removed(source: str) -> str:
    lines, b, e = _module_block_span(source)
    return _checked(source, "\n".join(lines[:b] + lines[e + 1:]))


def mutate_moved_into_comment(source: str) -> str:
    lines, b, e = _module_block_span(source)
    block, rest = lines[b:e + 1], lines[:b] + lines[e + 1:]
    return _checked(source, "\n".join(_insert_after_future(rest, ["# " + ln for ln in block])))


def mutate_moved_into_string_constant(source: str) -> str:
    lines, b, e = _module_block_span(source)
    block, rest = lines[b:e + 1], lines[:b] + lines[e + 1:]
    const = ['_WITHDRAWAL_NOTICE = """'] + block + ['"""']
    return _checked(source, "\n".join(_insert_after_future(rest, const)))


def mutate_body_token_misspelled(source: str) -> str:
    lines, b, e = _module_block_span(source)
    body = [ln.replace("trsx5", "trxs5") for ln in lines[b + 1:e]]
    assert body != lines[b + 1:e], "the notice BODY holds no 'trsx5' to misspell"
    return _checked(source, "\n".join(lines[:b + 1] + body + lines[e:]))


def mutate_sentence_altered(source: str) -> str:
    lines, b, e = _module_block_span(source)
    block = "\n".join(lines[b:e + 1])
    assert block.count(POSTED_SENTENCE_END) == 1, (
        f"the notice block holds {block.count(POSTED_SENTENCE_END)} copies of {POSTED_SENTENCE_END!r}, not 1"
    )
    altered = block.replace(POSTED_SENTENCE_END, "is retained.", 1)
    return _checked(source, "\n".join(lines[:b] + altered.split("\n") + lines[e + 1:]))


def mutate_moved_to_docstring_end(source: str) -> str:
    lines, b, e = _module_block_span(source)
    block, rest = lines[b:e + 1], lines[:b] + lines[e + 1:]
    head = ast.parse("\n".join(rest)).body[0]
    close = head.end_lineno - 1
    assert rest[close].strip() == '"""', (
        f"the module docstring does not close on its own line: {rest[close]!r}"
    )
    return _checked(source, "\n".join(rest[:close] + block + rest[close:]))


def mutate_duplicated(source: str) -> str:
    lines, b, e = _module_block_span(source)
    return _checked(source, "\n".join(lines[:e + 1] + lines[b:e + 1] + lines[e + 1:]))


def _function_notice_span(source: str) -> tuple[list[str], int, int]:
    lines = source.split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.strip().startswith("WITHDRAWN POLICY:")]
    assert len(starts) == 1, f"{len(starts)} 'WITHDRAWN POLICY:' lines in the RAW text, not exactly 1"
    b = e = starts[0]
    while e + 1 < len(lines) and lines[e + 1].strip():
        e += 1
    return lines, b, e


def mutate_function_notice_removed(source: str) -> str:
    lines, b, e = _function_notice_span(source)
    return _checked(source, "\n".join(lines[:b] + lines[e + 1:]))


def mutate_function_notice_moved_into_comment(source: str) -> str:
    lines, b, e = _function_notice_span(source)
    block, rest = lines[b:e + 1], lines[:b] + lines[e + 1:]
    return _checked(source, "\n".join(_insert_after_future(rest, ["# " + ln.strip() for ln in block])))


MODULE_MUTATIONS = {
    "removed": (mutate_removed, re.escape("not exactly 1")),
    "moved_into_comment": (mutate_moved_into_comment, re.escape("not exactly 1")),
    "moved_into_string_constant": (mutate_moved_into_string_constant, re.escape("not exactly 1")),
    "body_token_misspelled": (mutate_body_token_misspelled, re.escape("required token 'trsx5'")),
    "sentence_altered": (mutate_sentence_altered, re.escape("verbatim POSTED")),
    "moved_to_docstring_end": (mutate_moved_to_docstring_end, re.escape("not prominent")),
    "duplicated": (mutate_duplicated, re.escape("not exactly 1")),
}
FUNCTION_MUTATIONS = {
    "function_notice_removed": (mutate_function_notice_removed, re.escape("required token 'withdrawn'")),
    "function_notice_moved_into_comment": (
        mutate_function_notice_moved_into_comment, re.escape("required token 'withdrawn'"),
    ),
}


def synthetic_module() -> str:
    """The GOOD synthetic fixture. Its historical tail is deliberately 7 lines long,
    so ``moved_to_docstring_end`` really lands the notice past
    ``NOTICE_MAX_START_LINE``; the blank line after the See-line keeps the
    function-notice removal from swallowing the docstring close."""
    return "\n".join([
        '"""Synthetic title line for the enforcer controls.',
        "",
        NOTICE_BEGIN + " -- READ BEFORE ANYTHING BELOW ====",
        "",
        "Pre-registered in tcujq (OSF 2026-07-04); WITHDRAWN by trsx5 (OSF 2026-07-10).",
        posted_withdrawal_sentence(),
        "Replaced by exclude-in-lockstep. This module is NOT called by the pipeline.",
        "Recorded: DEC-2026-09-16-condition-ld-matrix-freeze-code-only.",
        "",
        NOTICE_END,
        "",
        "Historical text, kept as written.",
        "",
        "A second historical paragraph.",
        "",
        "A third historical paragraph.",
        "",
        "A fourth historical paragraph.",
        '"""',
        _FUTURE_LINE,
        "",
        "",
        "def condition_ld_matrix(m):",
        '    """Apply the synthetic conditioning.',
        "",
        "    WITHDRAWN POLICY: tcujq (OSF 2026-07-04) was WITHDRAWN by trsx5 (OSF 2026-07-10).",
        "    See the WITHDRAWN POLICY NOTICE in the module docstring.",
        "",
        '    """',
        "    return m",
        "",
    ])


# ==========================================================================
# The posted anchor
# ==========================================================================
def test_the_posted_trsx5_body_is_the_byte_exact_reconstruction():
    sentence = posted_withdrawal_sentence()
    assert sentence.startswith(POSTED_SENTENCE_PREFIX)
    assert sentence.endswith(POSTED_SENTENCE_END)
    assert sentence.count(POSTED_SENTENCE_END) == 1


# ==========================================================================
# THE POSITIVE NOTICE CHECKS -- real files
# ==========================================================================
@pytest.mark.parametrize("rel", NOTICE_MODULES, ids=NOTICE_MODULE_IDS)
def test_module_docstring_carries_the_withdrawal_notice(rel):
    assert_module_notice((PROJECT_ROOT / rel).read_text(encoding="utf-8"), rel)


@pytest.mark.parametrize("rel,func", NOTICE_FUNCTIONS, ids=[func for _, func in NOTICE_FUNCTIONS])
def test_function_docstring_carries_the_withdrawal_notice(rel, func):
    assert_function_notice((PROJECT_ROOT / rel).read_text(encoding="utf-8"), func, rel)


# ==========================================================================
# "NOT called by the pipeline" -- with non-vacuity and positive controls
# ==========================================================================
def test_neither_notice_module_has_a_pipeline_caller():
    scan = pipeline_scan(NOTICE_STEMS)
    # Non-vacuity FLOORS, not equalities (187 .py / 161 other were measured 2026-09-16).
    assert scan["n_py"] >= 150, f"the scan read only {scan['n_py']} tracked .py files -- it has gone blind"
    assert scan["n_other"] >= 100, f"the scan read only {scan['n_other']} tracked non-.py files -- it has gone blind"
    # MUST-BE-IDENTITY: the importer detector demonstrably resolves imports.
    assert scan["importers"]["condition_ld_matrix"] == {"src/python/write_conditioned_ld_npz.py"}, (
        "the importers of condition_ld_matrix are no longer exactly write_conditioned_ld_npz.py: "
        f"{sorted(scan['importers']['condition_ld_matrix'])}"
    )
    assert scan["importers"]["write_conditioned_ld_npz"] == set(), (
        "write_conditioned_ld_npz now HAS an importer, so its notice's 'NOT called by the pipeline' "
        f"is false: {sorted(scan['importers']['write_conditioned_ld_npz'])}"
    )
    for stem in NOTICE_STEMS:
        assert scan["script_path"][stem] == set(), (
            f"{stem}.py is named as a script path in pipeline code: {sorted(scan['script_path'][stem])}"
        )
        assert scan["text"][stem] == set(), (
            f"{stem} is mentioned by non-.py pipeline files: {sorted(scan['text'][stem])}"
        )


def test_the_pipeline_scan_detects_known_positives():
    text_stem, text_rel = POSITIVE_TEXT_HIT
    script_stem, script_rel = POSITIVE_SCRIPT_PATH_HIT
    scan = pipeline_scan((text_stem, script_stem))
    assert text_rel in scan["text"][text_stem], (
        f"the TEXT detector no longer sees {text_stem} in {text_rel} -- blind, or the live anchor moved "
        "(re-measure; do not fix up)"
    )
    assert script_rel in scan["script_path"][script_stem], (
        f"the SCRIPT-PATH detector no longer sees {script_stem}.py in {script_rel} -- blind, or the live "
        "anchor moved (re-measure; do not fix up)"
    )


def test_a_docstring_only_mention_is_not_a_script_path_hit():
    doc_only = '"""Mentions condition_ld_matrix.py in a docstring only."""\nX = 1\n'
    code_string = 'X = "src/python/condition_ld_matrix.py"\n'
    assert py_hits(doc_only, "condition_ld_matrix", "other") == (False, False)
    assert py_hits(code_string, "condition_ld_matrix", "other") == (False, True)


# ==========================================================================
# THE COMMITTED NEGATIVE CONTROLS -- synthetic fixture
# ==========================================================================
def test_the_synthetic_fixture_is_green():
    """Non-vacuity for every control below: the UNMUTATED fixture passes."""
    source = synthetic_module()
    assert_module_notice(source, "synthetic")
    assert_function_notice(source, "condition_ld_matrix", "synthetic")


@pytest.mark.parametrize("mid", list(MODULE_MUTATIONS))
def test_module_notice_negative_control(mid):
    mutate, match = MODULE_MUTATIONS[mid]
    source = synthetic_module()
    mutated = mutate(source)
    if mid == "moved_to_docstring_end":
        # Premise FIRST: a too-short fixture lets this control pass for free.
        doc = ast.get_docstring(ast.parse(mutated), clean=True).split("\n")
        begins = [i for i, ln in enumerate(doc) if ln.strip().startswith(NOTICE_BEGIN)]
        assert len(begins) == 1 and begins[0] > NOTICE_MAX_START_LINE, (
            f"fixture too short for this control: BEGIN lands at docstring line(s) {begins}"
        )
    if mid in ("moved_into_comment", "moved_into_string_constant"):
        # A text grep would have been GREEN: every body token is still in the file text.
        flat = _norm(mutated)
        missing = [tok for tok in MODULE_BODY_TOKENS if tok not in flat]
        assert not missing, f"the mutation dropped tokens from the TEXT, so it does not model a grep pass: {missing}"
    with pytest.raises(AssertionError, match=match):
        assert_module_notice(mutated, "synthetic")


@pytest.mark.parametrize("mid", list(FUNCTION_MUTATIONS))
def test_function_notice_negative_control(mid):
    mutate, match = FUNCTION_MUTATIONS[mid]
    mutated = mutate(synthetic_module())
    with pytest.raises(AssertionError, match=match):
        assert_function_notice(mutated, "condition_ld_matrix", "synthetic")
