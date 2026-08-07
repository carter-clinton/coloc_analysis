"""THE LIVE PINS -- the forward gate for every source freeze in m3.

Run this to answer "has any frozen file's CODE moved?"::

    pytest tests/m3/test_source_freeze_pins.py

Before ``quick-260806-sr4`` the answer came from
``git diff --exit-code <SHA> -- <file>`` in two test modules -- a **byte** pin --
and from a per-task hand check for everything else. The hand check had been
reporting a claim that is **FALSE for 5 of 8 files** (see
``test_the_handoff_frozen_claim_is_recorded_as_partly_false``), and the byte pin
made shipping a known-wrong census figure cheaper than correcting the comment
that carried it (finding **K-3**).

Every pin here is a CODE pin: comments, docstrings, blank lines and trailing
whitespace are ignored. The mechanism, the two mask invariants it rests on and
the re-pin protocol are documented in ``source_freeze.py``; the decision is
``DEC-2026-08-06-sr4-freeze-scope``.

NO SKIPS, BY CONSTRUCTION -- pure source text + ``git`` + stdlib.
"""
from __future__ import annotations

import ast
import re
import subprocess
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
    git_show,
)

# ==========================================================================
# THE PINS
# ==========================================================================
#: CODE PIN. The three m3 modules that have genuinely not moved since the
#: 2026-07-16 freeze declaration (``bf16289``). A CODE pin: comment and
#: docstring edits do not move it. On an AUTHORIZED code change, update THIS ONE
#: CONSTANT to the landing commit's SHA and nothing else.
#: See DEC-2026-08-06-sr4-freeze-scope.
PY_CODE_REF = "bf16289"

#: CODE PIN. ``run_susie_rss.R``'s CODE freeze, and the ONLY place the R pin is
#: spelled: ``test_finemap_receipt_early_exit.py`` and
#: ``test_qtl_coloc_allele_join.py`` IMPORT it rather than re-declaring it, so a
#: re-pinner who obeys "update exactly one constant" cannot leave a gate red.
#: ⚠ DELIBERATELY NOT MOVED by quick-260806-sr4: the K-3 edit was COMMENT-ONLY,
#: so this pin remains valid ACROSS it -- which is the acceptance demonstration
#: for the whole rescope. It still means "no CODE has moved since the K-1
#: closure". On an AUTHORIZED code change, update THIS ONE CONSTANT.
#: See DEC-2026-08-06-sr4-freeze-scope.
R_CODE_REF = "bf04199"

#: The numeric-bearing R symbols. Symbol pins are DIAGNOSTICS -- they name WHICH
#: block moved. The whole-file floor is the SAFETY NET: it covers the ~700-line
#: top-level main body (``:659-1357``) that lives inside no function at all,
#: including all three ``toJSON`` emits. NC-SR4 proves the floor catches a
#: perturbation all five symbol pins miss.
R_NUMERIC_SYMBOLS = (
    "regularize_ld",
    "run_susie_with_ladder",
    "safe_region_id",
    "load_ld_matrix",
    "assert_declared_ld_authoritative",
)

SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"

#: The three files AUTH-SR4-EXTEND covers -- MEASURED 0-diff against
#: ``PY_CODE_REF`` before they were gated. Adding a file here requires a
#: RECORDED DECISION that it is frozen, not an inference.
PY_FROZEN_RELS = (
    "src/python/plink_ld_to_npz.py",
    "src/python/condition_ld_matrix.py",
    "src/python/occlusion_span_filter.py",
)

#: ⚠ ``.planning/HANDOFF.json:14`` claims "All 7 pinned files 0-line diff vs
#: bf16289". FOUR of these five are named there and every one of them has MOVED;
#: ``git diff --numstat bf16289 HEAD`` measured 2026-08-06:
#:
#:   occlusion_manifest.py            +46  / -8    (bf963df, 2026-08-04)
#:   occlusion_present_rate_scan.py   +154 / -21   (fac9a93, 2026-08-04)
#:   drop_occluded_from_sumstats.py   +97  / -24   (bf963df, 2026-08-04)
#:   ld_npz_to_rds.R                  +313 / -62   (57b381f, 2026-08-05)
#:   pipeline.schema.yaml             +119 / -0    (2563451, 2026-08-06)
#:
#: Declaring a moving file frozen is a DECISION, not an inference, and gating a
#: file that changed three times in three days would manufacture exactly the
#: nuisance-repin timebomb this rescope exists to remove. They are registered as
#: an OPEN QUESTION for Carter in deferred-items.md and deliberately NOT gated.
MOVED_SINCE_PY_CODE_REF = (
    "src/python/occlusion_manifest.py",
    "src/python/occlusion_present_rate_scan.py",
    "src/python/drop_occluded_from_sumstats.py",
    "src/scripts/ld_npz_to_rds.R",
    "src/snakemake/schemas/pipeline.schema.yaml",
)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True
    )


def _top_level_symbols_at(ref: str, rel: str) -> tuple[str, ...]:
    """DERIVED from the source at ``ref`` -- never hand-transcribed.

    A hand-typed symbol list is a test that agrees with itself: it can only ever
    check the names someone remembered to type, and a deleted symbol silently
    stops being checked.
    """
    tree = ast.parse(git_show(ref, rel))
    return tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )


PY_SYMBOL_CASES = [
    (rel, name)
    for rel in PY_FROZEN_RELS
    for name in _top_level_symbols_at(PY_CODE_REF, rel)
]


# ==========================================================================
# THE PYTHON PINS -- AUTH-SR4-EXTEND
# ==========================================================================
@pytest.mark.parametrize("rel", PY_FROZEN_RELS)
def test_python_module_code_is_frozen(rel):
    assert_code_frozen(rel, PY_CODE_REF, LANG_PY)


@pytest.mark.parametrize("rel,symbol", PY_SYMBOL_CASES)
def test_python_symbol_code_is_frozen(rel, symbol):
    assert_code_frozen(rel, PY_CODE_REF, LANG_PY, symbol=symbol)


def test_the_python_symbol_set_is_derived_and_non_empty():
    """22 symbols across three modules, all DERIVED from ``PY_CODE_REF``."""
    assert len(PY_SYMBOL_CASES) == 22, (
        f"{len(PY_SYMBOL_CASES)} top-level symbols were derived, not 22 -- the "
        "frozen surface has changed shape and that is a decision, not a fixup"
    )
    per_module = {rel: 0 for rel in PY_FROZEN_RELS}
    for rel, _ in PY_SYMBOL_CASES:
        per_module[rel] += 1
    assert per_module == {
        "src/python/plink_ld_to_npz.py": 13,
        "src/python/condition_ld_matrix.py": 3,
        "src/python/occlusion_span_filter.py": 6,
    }


def test_the_pinned_set_is_exactly_the_files_that_have_not_moved():
    assert _git("cat-file", "-t", PY_CODE_REF).stdout.strip() == "commit"
    assert _git("cat-file", "-t", R_CODE_REF).stdout.strip() == "commit"
    for rel in PY_FROZEN_RELS + (SUSIE_R_REL,):
        assert (PROJECT_ROOT / rel).exists(), f"{rel} is gone from the working tree"
        ref = R_CODE_REF if rel == SUSIE_R_REL else PY_CODE_REF
        assert git_show(ref, rel), f"{rel} does not exist at {ref}"


def test_the_handoff_frozen_claim_is_recorded_as_partly_false():
    """``HANDOFF.json:14``'s "All 7 pinned files 0-line diff vs bf16289" is FALSE
    for 5 of 8. Recorded here so a future sweep cannot "helpfully" add them back
    without a decision, and so the record itself stays honest."""
    for rel in MOVED_SINCE_PY_CODE_REF:
        assert rel not in PY_FROZEN_RELS, (
            f"{rel} has MOVED since {PY_CODE_REF} and must not be gated against "
            "it -- declaring a moving file frozen is a DECISION for Carter, not "
            "an inference (see deferred-items.md)"
        )
        numstat = _git("diff", "--numstat", PY_CODE_REF, "HEAD", "--", rel).stdout.strip()
        assert numstat, (
            f"{rel} is now 0-diff vs {PY_CODE_REF}. The recorded finding "
            "(HANDOFF's claim is false for 5 of 8 files) has changed -- re-open "
            "the question rather than editing this list"
        )
    for rel in PY_FROZEN_RELS:
        numstat = _git("diff", "--numstat", PY_CODE_REF, "HEAD", "--", rel).stdout.strip()
        assert not numstat, (
            f"{rel} is NO LONGER 0-diff vs {PY_CODE_REF} ({numstat!r}); it left "
            "the measured basis for AUTH-SR4-EXTEND"
        )


# ==========================================================================
# THE R PINS -- AUTH-SR4-RESCOPE
# ==========================================================================
def test_run_susie_rss_whole_file_code_is_frozen():
    """THE FLOOR. Not optional: ``:659-1357`` -- the fitting flow and all three
    ``toJSON`` emits -- is inside no named symbol, so the five symbol pins alone
    would have a ~700-line silent hole. NC-SR4 proves that mechanically."""
    assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R)


@pytest.mark.parametrize("symbol", R_NUMERIC_SYMBOLS)
def test_run_susie_rss_symbol_code_is_frozen(symbol):
    """DIAGNOSTICS: these name WHICH numeric-bearing block moved."""
    assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R, symbol=symbol)


# ==========================================================================
# THE ACCEPTANCE TEST -- the K-3 comment fix cost NO re-pin
# ==========================================================================
#: DIFFERENTIAL SUBSTRATE. The revision the K-3 digits were corrected FROM. NOT
#: a freeze pin: it MUST stay bf04199 forever, even after R_CODE_REF is
#: re-pinned. Same treatment as PRE_K1_REF. Bumping it in a re-pin sweep would
#: silently kill the acceptance proof below, because clauses (ii)/(iii) would
#: then compare the live file against itself and could never fail.
#: See DEC-2026-08-06-sr4-freeze-scope.
K3_PRE_FIX_REF = "bf04199"

#: The corrected K-3 census figures and the wrong ones they replaced.
K3_CORRECTED = ("1,909", "1,900")
K3_WRONG = ("1,944", "1,935")


def _k3_historical_clauses(reference_text: str) -> None:
    """Clauses (ii) and (iii): frozen HISTORICAL facts about the K-3 edit.

    ``reference_text`` is the file as it stood at ``K3_PRE_FIX_REF``. It is a
    parameter, not a lookup, so the control below can hand this helper exactly
    what ``git show <new-ref>`` would return AFTER an authorized re-pin -- the
    live text -- and observe it go RED. Without that, the ref split would be
    fixed in prose and not in fact: both constants hold the same value today.
    """
    live = (PROJECT_ROOT / SUSIE_R_REL).read_text()

    # (ii) the raw texts DIFFER -- the comment edit really did land
    assert live != reference_text, (
        "the live file is byte-identical to the K-3 pre-fix substrate. Either "
        "the correction was reverted, or K3_PRE_FIX_REF was bumped in a re-pin "
        "sweep -- it is a DIFFERENTIAL SUBSTRATE and must never move"
    )
    # (iii) the corrected figures are live and the wrong ones are gone
    for figure in K3_CORRECTED:
        assert figure in live, f"the corrected K-3 figure {figure} is not in the file"
        assert figure not in reference_text
    for figure in K3_WRONG:
        assert figure not in live, f"the wrong K-3 figure {figure} is STILL shipped"
        assert figure in reference_text


def test_the_k3_comment_fix_did_not_move_the_code_pin():
    """⭐ THE ACCEPTANCE TEST for the whole rescope.

    ``quick-260806-sr4`` spent AUTH-SR4-K3 on a COMMENT-ONLY correction to
    ``run_susie_rss.R`` (``1,944`` -> ``1,909``, ``1,935`` -> ``1,900`` at
    ``:1018-1019``) and did **NOT** re-pin. Under the old byte gate that edit was
    impossible without an unfreeze and a re-pin cascade, which is exactly why a
    known-false census figure shipped instead. Under the code pin it is FREE, and
    ``bf04199`` keeps its stronger meaning: "no CODE has moved since the K-1
    closure" rather than "nothing has moved since yesterday's typo fix".

    ⚠ TWO REFS, DELIBERATELY. Clause (i) reads the LIVE ``R_CODE_REF`` so it
    survives a future authorized re-pin correctly. Clauses (ii)/(iii) read
    ``K3_PRE_FIX_REF``, a never-re-pinned substrate. Evaluating all three against
    ``R_CODE_REF`` would re-plant the very timebomb this plan removes: the first
    authorized code change would make ``git show <new-ref>`` equal the live file,
    (ii)/(iii) would go red, and the DECISIONS re-pin protocol -- "update exactly
    one constant and nothing else" -- would be FALSE ON ITS FIRST EXERCISE.
    """
    # (i) the LIVE pin: the code has not moved across the comment edit
    assert_code_frozen(SUSIE_R_REL, R_CODE_REF, LANG_R)
    # (ii)/(iii) the historical facts
    _k3_historical_clauses(git_show(K3_PRE_FIX_REF, SUSIE_R_REL))


def test_the_two_ref_split_is_real_and_not_merely_annotated():
    """The control that makes the split observable TODAY.

    Both constants hold ``bf04199`` right now, so (ii)/(iii) would pass under
    either one and the fix would exist only in prose. Hand the helper the live
    text -- precisely what ``git show <new-ref>`` returns once ``R_CODE_REF`` is
    re-pinned to a landing commit -- and it must go RED.
    """
    live = (PROJECT_ROOT / SUSIE_R_REL).read_text()
    with pytest.raises(AssertionError, match="DIFFERENTIAL SUBSTRATE"):
        _k3_historical_clauses(live)          # simulates a re-pinned R_CODE_REF
    _k3_historical_clauses(git_show(K3_PRE_FIX_REF, SUSIE_R_REL))   # GREEN


def test_the_k3_edit_touched_only_two_comment_lines():
    """AUTH-SR4-K3's containment, permanent and in-suite.

    The authorization was two digits in a comment. Anything else in that diff is
    an unauthorized widening of a spent unfreeze, and it must not be possible to
    discover that only by reading a summary.
    """
    diff = _git("diff", "-U0", K3_PRE_FIX_REF, "--", SUSIE_R_REL).stdout
    # ⚠ `ln[:1] in "-+"` alone is WRONG: "" is a substring of every string, so
    # the trailing blank from split("\n") counts as a changed line.
    changed = [
        ln[1:] for ln in diff.split("\n")
        if ln[:1] and ln[0] in "-+" and not ln.startswith(("---", "+++"))
    ]
    assert len(changed) == 4, f"expected 2 -/+ pairs, got {len(changed)} changed lines"
    for line in changed:
        assert line.lstrip().startswith("#"), (
            f"a NON-COMMENT line moved under AUTH-SR4-K3: {line!r}. The "
            "authorization was two digits in a comment and nothing else"
        )
    hunks = [ln for ln in diff.split("\n") if ln.startswith("@@")]
    assert len(hunks) == 1, f"expected ONE hunk, got {len(hunks)}: {hunks}"
    # the two pairs differ ONLY in the census digits
    before = [ln for ln in changed[:2]]
    after = [ln for ln in changed[2:]]
    for old, new in zip(before, after):
        for wrong, right in zip(K3_WRONG, K3_CORRECTED):
            old = old.replace(wrong, right)
        assert old == new, (
            "the K-3 hunk changed something other than the census digits:\n"
            f"  - {changed[:2]}\n  + {changed[2:]}"
        )


# ==========================================================================
# T-sr4-10 -- every pin constant declares its BUCKET, repo-wide and permanent
# ==========================================================================
#: The three buckets. Only CODE PINs ever move. A re-pin sweep that bumps a
#: DIFFERENTIAL SUBSTRATE silently destroys the control it feeds
#: (``[[feedback_fixing_a_split_unpins_what_it_pinned]]``), and a hand-written
#: never-re-pin LIST is the wrong shape: any omission LICENSES a sweeper to bump
#: the ones left out. So the rule is derived, not enumerated.
_BUCKETS = ("CODE PIN", "DIFFERENTIAL SUBSTRATE", "HISTORICAL NARRATIVE")
_PIN_NAME_RE = re.compile(r"_REF$|_REV$|^BASE_COMMIT$|^BASELINE_REV$")


def _preceding_comment_block(lines: list[str], lineno: int) -> str:
    """The contiguous comment block immediately above a 1-based ``lineno``,
    whitespace-normalised so a bucket phrase may wrap across ``#:`` lines."""
    idx, block = lineno - 2, []
    while idx >= 0 and lines[idx].lstrip().startswith("#"):
        block.append(lines[idx].lstrip().lstrip("#").lstrip(":"))
        idx -= 1
    return " ".join(" ".join(reversed(block)).split())


def _pin_constants() -> list[tuple[str, str, int, str]]:
    found = []
    for path in sorted(Path(__file__).resolve().parent.glob("*.py")):
        lines = path.read_text().split("\n")
        for node in ast.parse(path.read_text()).body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or not _PIN_NAME_RE.search(target.id):
                continue
            if not (isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                continue
            found.append(
                (path.name, target.id, node.lineno, _preceding_comment_block(lines, node.lineno))
            )
    return found


def test_every_pin_constant_declares_its_bucket():
    unbucketed, ambiguous = [], []
    for filename, name, lineno, block in _pin_constants():
        buckets = [b for b in _BUCKETS if b in block]
        if not buckets:
            unbucketed.append(f"{filename}:{lineno} {name}")
        elif len(buckets) > 1:
            ambiguous.append(f"{filename}:{lineno} {name} -> {buckets}")
    assert not unbucketed, (
        "a revision constant carries no bucket annotation, so a re-pin sweep "
        "cannot tell whether moving it is correct or destroys a control. Add a "
        f"'#:' block naming exactly one of {_BUCKETS}: " + "; ".join(unbucketed)
    )
    assert not ambiguous, (
        "a revision constant names more than one bucket: " + "; ".join(ambiguous)
    )


def test_the_bucket_scan_is_non_vacuous():
    """"Everything is annotated" is evidence only if the scan finds anything."""
    constants = _pin_constants()
    assert len(constants) >= 15, (
        f"the bucket scan found only {len(constants)} revision constants; 17 "
        "were measured on 2026-08-06. The walk has stopped resolving them and "
        "the gate above is passing for free"
    )
    names = {name for _, name, _, _ in constants}
    for expected in ("PRE_CHANGE_REF", "BASE_COMMIT", "BASELINE_REV",
                     "PRE_K1_REF", "R_CODE_REF", "PY_CODE_REF", "K3_PRE_FIX_REF"):
        assert expected in names, f"the scan no longer sees {expected}"
    # and an UNannotated constant is genuinely rejected -- the classifier is
    # exercised on a synthetic negative, never only on the happy path.
    assert _preceding_comment_block(["# just a note", 'X_REF = "abc1234"'], 2) == "just a note"
    assert not [b for b in _BUCKETS if b in "just a note"]
