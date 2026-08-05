"""RED-first tests for src/python/occlusion_coord_key.py (quick-260804-rtc, T1).

D-04b-01 — THE DEFECT THIS SUITE EXISTS TO CLOSE
------------------------------------------------
The ``(CHR, POS)`` canonical key was implemented THREE times, verbatim, and every
copy ended in a bare ``int(pos)``. A position written as the float-formatted string
``'5982778.0'`` therefore raises ``ValueError: invalid literal for int() with base
10: '5982778.0'`` — which BOTH call sites swallow fail-open, so the row is silently
kept.

The blast radius (``m3-04b-BLAST-RADIUS.md`` §D-04b-01) measured the exposure over
all ten ``*.AFR*.tsv.bgz`` in a full streaming pass: exactly ONE file is affected,
and it is affected TOTALLY —

    bmi.AFR.PAGE.2019.GRCh37   100% FLOAT POS   17,195,956 body rows   17,195,956 failing

so the harm is not a scattering of odd rows, it is one whole trait. Today that costs
the published present-rate ``k/n`` (6 of 9 instead of the correct 7 of 9 for
rs182965575). It becomes a SILENT UNDER-DROP on a real ``run_finemap`` input the
moment BMI-AFR is re-harmonized to the canonical ``bmi.AFR.tsv.bgz`` name that
``Snakefile:68-71`` already requests.

WHY A SHARED MODULE AND NOT THREE PATCHES
-----------------------------------------
``[[feedback_extract_reusable_utilities]]``: a recurrent bug class gets ONE reusable
utility plus a failing-test-first regression, never a third in-place patch. The
three-way byte-compat matrix below is the proof that consolidating the rule did not
MOVE the join — a moved key would silently stop matching the manifest, which reads
exactly like "nothing was occluded".

NEVER TRUNCATE. ``'5982778.5'`` must RAISE, not become ``5982778``. A truncated
coordinate is a plausible-but-wrong position, and the panel<->sumstats join is
(CHR,POS)-only and DROP-ONLY: a wrong position deletes the WRONG variant's row from
real scientific data. That is strictly worse than failing.

RED-for-the-right-reason: ``occlusion_coord_key`` does not exist yet. It is imported
INSIDE each test body (mirroring ``test_occlusion_lockstep_drop.py:30-40``) so pytest
COLLECTS cleanly and each test fails as a test failure, NOT a collection error.

Runs in smoke_dev py3.11. No Hail, no perimeter, $0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import occlusion_coord_key`` — see the docstring.

#: The settled hinge anchor: rs182965575, GRCh38 5922718 -> GRCh37 5982778.
_SNP_C_B37 = 5_982_778


# --------------------------------------------------------------------------- #
# 1. coerce_integral_position — the D-04b-01 headline                          #
# --------------------------------------------------------------------------- #

def test_float_formatted_integral_string_coerces_to_int():
    """``'5982778.0'`` -> ``5982778``. THE D-04b-01 headline.

    This is the exact shape 100% of ``bmi.AFR.PAGE.2019.GRCh37``'s 17,195,956 rows
    carry. Today a bare ``int()`` raises on it and both consumers swallow the raise
    fail-open, so the variant is silently kept.
    """
    from occlusion_coord_key import coerce_integral_position

    assert coerce_integral_position("5982778.0") == _SNP_C_B37


def test_plain_integer_string_is_unchanged():
    """The overwhelmingly common shape must not move."""
    from occlusion_coord_key import coerce_integral_position

    assert coerce_integral_position("5982778") == _SNP_C_B37


def test_python_float_coerces_to_int():
    """A ``float`` (pandas hands back ``numpy.float64`` whenever ONE row in the
    column failed to lift) is accepted when it is integral."""
    from occlusion_coord_key import coerce_integral_position

    assert coerce_integral_position(5_982_778.0) == _SNP_C_B37


def test_trailing_zero_variants_coerce():
    """``'5982778.00'`` and ``'5982778.'`` are the same integral position."""
    from occlusion_coord_key import coerce_integral_position

    assert coerce_integral_position("5982778.00") == _SNP_C_B37
    assert coerce_integral_position("5982778.") == _SNP_C_B37


def test_non_integral_position_raises_and_is_never_truncated():
    """``'5982778.5'`` RAISES. It must NEVER become ``5982778``.

    A truncated coordinate joins and drops the WRONG sumstats row — the exact harm
    the lockstep exists to prevent, wearing a clean count. The message names the
    offending value so the T2 unparseable counter's exemplar line is
    self-explanatory (``m3-04b-W4-SUMMARY.md:312-314`` prescribes this fix shape).
    """
    from occlusion_coord_key import coerce_integral_position

    with pytest.raises(ValueError) as exc:
        coerce_integral_position("5982778.5")

    assert "5982778.5" in str(exc.value), "the raise must QUOTE the offending value"


@pytest.mark.parametrize("bad", ["1_000", "1e6", "1E6", "1.5e6"])
def test_latent_int_quirks_and_scientific_notation_raise(bad):
    """``int('1_000')`` -> 1000 today, a latent quirk the blast radius flagged with
    no live exposure. And scientific notation occurs ZERO times in the whole 10-file
    AFR corpus, so accepting it would be a silent WIDENING of the contract.

    Rejecting both makes a file that uses them BLARE through the T2 unparseable
    counter instead of scoring silently absent.
    """
    from occlusion_coord_key import coerce_integral_position

    with pytest.raises(ValueError):
        coerce_integral_position(bad)


@pytest.mark.parametrize("bad", ["", "NA", ".", "  ", "chr1", "-", "５９８２７７８"])
def test_missing_and_non_numeric_positions_raise(bad):
    """Empty / NA / '.' / blank / non-ASCII-digit positions are NOT coordinates.

    ``'５９８２７７８'`` (full-width digits) is the second latent ``int()`` quirk:
    today ``int()`` accepts it. An explicit ``re.fullmatch`` on ``[0-9]`` closes it.
    """
    from occlusion_coord_key import coerce_integral_position

    with pytest.raises(ValueError):
        coerce_integral_position(bad)


def test_none_raises():
    from occlusion_coord_key import coerce_integral_position

    with pytest.raises(ValueError):
        coerce_integral_position(None)


# --------------------------------------------------------------------------- #
# 2. canonical_coord_key — contig normalization is byte-identical to today     #
# --------------------------------------------------------------------------- #

def test_canonical_key_normalizes_the_contig_and_the_position():
    """``('chr1', '5982778.0')``, ``('1', 5982778)`` and ``(1, 5982778)`` are ONE key.

    The manifest producer emits ``chr`` as the STRING ``'1'`` while the scan RED keys
    on the int ``1`` — normalizing both to ``1`` is what makes those the same variant
    instead of two silent near-misses.
    """
    from occlusion_coord_key import canonical_coord_key

    assert canonical_coord_key("chr1", "5982778.0") == (1, _SNP_C_B37)
    assert canonical_coord_key("1", 5_982_778) == (1, _SNP_C_B37)
    assert canonical_coord_key(1, 5_982_778) == (1, _SNP_C_B37)
    assert canonical_coord_key("CHR1", 5_982_778) == (1, _SNP_C_B37)


def test_non_numeric_contig_stays_a_string():
    """``'X'`` stays the STRING ``'X'``. LOW-5 (chrX ``'X'`` vs ``23``) is explicitly
    OUT of scope for this fix; today's behavior is pinned here so it cannot drift
    silently while nobody is looking."""
    from occlusion_coord_key import canonical_coord_key

    assert canonical_coord_key("X", 100) == ("X", 100)
    assert canonical_coord_key("chrX", 100) == ("X", 100)


# --------------------------------------------------------------------------- #
# 3. THE THREE-WAY BYTE-COMPAT PROOF — the join must not move                  #
# --------------------------------------------------------------------------- #

def _numpy_int(value):
    import numpy as np

    return np.int64(value)


@pytest.mark.parametrize("chrom,pos", [
    ("1", "5982778"),
    (1, 5_982_778),
    ("chr1", 5_982_778),
    ("1", "5982778.0"),          # <-- the D-04b-01 shape; RED until the fix lands
    ("1", 5_982_778.0),
    ("X", 100),
])
def test_all_three_key_implementations_agree(chrom, pos):
    """``occlusion_present_rate_scan._canonical_key``,
    ``drop_occluded_from_sumstats._canonical_key`` and
    ``occlusion_manifest._present_rate_key`` return the IDENTICAL tuple.

    This is the "prove the join still holds" requirement. The three implementations
    were verbatim copies; consolidating them into one shared module must not MOVE the
    key, because a moved key stops matching the manifest and reads downstream exactly
    like "nothing was occluded".
    """
    import drop_occluded_from_sumstats as dof
    import occlusion_manifest as om
    import occlusion_present_rate_scan as prs
    from occlusion_coord_key import canonical_coord_key

    expected = canonical_coord_key(chrom, pos)
    assert prs._canonical_key(chrom, pos) == expected
    assert dof._canonical_key(chrom, pos) == expected
    assert om._present_rate_key(chrom, pos) == expected


def test_numpy_int64_position_agrees_across_all_three():
    """pandas hands the manifest's ``pos_grch37`` back as ``numpy.int64``; all three
    implementations must key it identically to a plain ``int``."""
    import drop_occluded_from_sumstats as dof
    import occlusion_manifest as om
    import occlusion_present_rate_scan as prs
    from occlusion_coord_key import canonical_coord_key

    pos = _numpy_int(_SNP_C_B37)
    expected = canonical_coord_key("1", pos)
    assert expected == (1, _SNP_C_B37)
    assert prs._canonical_key("1", pos) == expected
    assert dof._canonical_key("1", pos) == expected
    assert om._present_rate_key("1", pos) == expected


def test_present_rate_key_keeps_its_unlifted_none_branch():
    """``occlusion_manifest._present_rate_key`` returns ``None`` for an UNLIFTED row.

    That branch needs pandas (``pd.isna``) and stays in ``occlusion_manifest``; it is
    a documented, deliberate signal (a variant in a liftover/assembly gap), and the
    refactor must not swallow it into a raise.
    """
    import pandas as pd
    import occlusion_manifest as om

    assert om._present_rate_key(1, None) is None
    assert om._present_rate_key(1, pd.NA) is None
    assert om._present_rate_key(1, float("nan")) is None


# --------------------------------------------------------------------------- #
# 4. the shared module is DEPENDENCY-FREE (stdlib only)                        #
# --------------------------------------------------------------------------- #

def test_shared_key_module_imports_nothing_outside_the_stdlib():
    """``occlusion_coord_key`` must import NO pandas, NO numpy, NO pyliftover.

    ``occlusion_present_rate_scan``'s docstring guarantees it stays importable
    without the span filter or pyliftover ("stdlib only — streamed line-wise"). If
    the shared key module dragged pandas in, that guarantee would quietly die and the
    scan would stop being runnable in a bare env.
    """
    import inspect

    import occlusion_coord_key

    src = inspect.getsource(occlusion_coord_key)
    import_lines = [
        ln.strip() for ln in src.splitlines()
        if ln.strip().startswith(("import ", "from ")) and "import" in ln
    ]
    joined = " ".join(import_lines)
    for forbidden in ("pandas", "numpy", "pyliftover", "occlusion_span_filter"):
        assert forbidden not in joined, (
            f"occlusion_coord_key must stay dependency-free; found {forbidden!r} in "
            f"{import_lines!r}"
        )
