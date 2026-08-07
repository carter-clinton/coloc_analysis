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
