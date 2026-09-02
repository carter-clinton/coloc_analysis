"""POST-HOC panel-wide ``--exclude`` reclassification of an emitted pcs_pairs.tsv.

(1) WHY IT EXISTS — ``already_occluded`` IS ANCHOR-RELATIVE, THE EXCLUDELIST IS
PANEL-WIDE
------------------------------------------------------------------------------
``pairwise_completeness_scan``'s ``already_occluded`` is computed inside
``pairwise_completeness_scan.enumerate_candidates`` as::

    already_occluded = bool(deletion.pos < partner.pos <= deletion.span_end)

— against THE ANCHOR DELETION OF THAT ROW ONLY. (The symbol is cited, not a line
number: a line number is a proxy that decays silently on any edit above it, which
is the same scoping mistake this module's history is about.)

The PRODUCTION excludelist is a DIFFERENT quantity and it is PANEL-WIDE:
``occlusion_span_filter.detect_occluded_variants`` evaluated over EVERY deletion
in the window (``run_native_ld_panel.py:878``, on the row set built at
``:851-872``).

ANCHOR-RELATIVE vs PANEL-WIDE is the whole distinction. Therefore
``already_occluded == False`` means "not inside THIS anchor's span". It does NOT
mean "survives ``--exclude``", and ``n_undefined_not_already_occluded`` does NOT
count pairs that survive filtering: a pair can carry ``already_occluded=False``
while one of its members is dropped by a DIFFERENT deletion in the same window.
That disagreement is DEMONSTRATED at runtime, not asserted, by
``tests/m3/test_pairwise_completeness_scan.py::test_already_occluded_is_anchor_relative_and_is_not_the_exclude_side``.
This module computes the PANEL-WIDE quantity that the scanner never asked for,
from the scanner's OWN output.

The scanner's own module docstring now carries this correction too (it briefly
did not; the correction landed in ``quick-260901-l55`` together with the rescope
of the runbook gate that had made the fix expensive). Its absence there is
machine-enforced by
``tests/m3/test_pairwise_completeness_scan.py::test_the_scanner_docstring_no_longer_claims_already_occluded_is_the_exclude_side``.

(2) WHY VID-KEYED — BECAUSE PRODUCTION IS
------------------------------------------
``detect_occluded_variants`` returns col-2 IDS because that is exactly what
plink ``--exclude`` consumes (``aou_ld_panel.py:2910-2913``), and ``--exclude``
on a DUPLICATED id drops EVERY row carrying it. A vid key therefore MATCHES
PRODUCTION SEMANTICS, and any id ambiguity is PRODUCTION'S ambiguity: it is
counted in ``n_pairs_with_ambiguous_member_id`` and NAMED in
``ambiguous_member_ids``, never "fixed" by switching to row indices.

⚠ Do NOT conflate this with ``_pair_key`` (``pairwise_completeness_scan.py:446``),
which is deliberately INDEX-keyed for the OPPOSITE reason: two rows sharing a
``.`` id are DISTINCT pairs and a vid key would UNDERCOUNT them. Both
conventions are correct; they answer different questions. Pair-level rollups
here use ``pair_key``; occlusion verdicts use the vid.

(3) MONOTONICITY AND SCOPE
---------------------------
Occlusion is MONOTONE in the row set: for a variant present in both, ``R`` a
subset of ``R'`` implies ``occluded(v, R)`` implies ``occluded(v, R')``, because
adding rows can only ADD covering deletions and the self-guard is index-based
and recomputed per call. CONSEQUENCE: an OCCLUDED verdict computed on a SUBSET
is SOUND, while a NOT-OCCLUDED verdict on a SUBSET is NOT. Every not-occluded
verdict emitted here is therefore RELATIVE TO the row set named in
``provenance`` — which records the bim path, its sha256, its line count, the
region ids NAMED, the per-region in-window row counts, and a literal
``verdict_scope`` sentence saying exactly this.
``tests/m3/test_pcs_panelwide_reclassify.py::test_occlusion_is_monotone_in_the_row_set``
proves the property the soundness argument rests on rather than assuming it.

(4) POST-HOC ONLY — IT CANNOT REQUIRE A RE-RUN
-----------------------------------------------
This tool reads an ALREADY-EMITTED ``pcs_pairs.tsv``, the cohort ``.bim`` and
the region manifest, AND NOTHING ELSE. It opens no ``.bed``, decodes no
genotype, and therefore CANNOT require the ~4h20m sweep to be re-run: the
sweep's OUTPUT is this tool's INPUT.

That property is MACHINE-CHECKED, not narrated. An AST gate (in this module's
verify block and in
``test_the_tool_never_opens_a_bed_or_decodes_a_genotype``) fails on any
``BedReader``/``Genotypes``/``MISSING_DOSAGE`` import, any ``BedReader``
reference, any ``read_variant`` call, or any ``.bed`` string literal OUTSIDE a
docstring. The gate is AST-based rather than ``grep``-based precisely so that
this paragraph — which MENTIONS ``.bed`` — cannot false-fire it.

(5) WHAT IT DOES NOT ESTABLISH
-------------------------------
No prevalence. No boundary width. No policy, criterion or threshold moves. The
pre-registered ``n_undefined_rows`` 15 / ``n_undefined_distinct_pairs`` 13 /
``already_occluded`` 10 / ``not_already_occluded`` 3 and the offset histogram
are UNCHANGED and are not revised by anything here; this module ADDS a DERIVED
quantity BESIDE them.

(6) THE DEFINED-ROW TAIL AND THE INFORMATIVE-CARRIER DISTRIBUTION
------------------------------------------------------------------
THE QUESTION: of the DEFINED rows whose ``max(del_carriers_lost_frac,
partner_carriers_lost_frac) >= 0.9`` — finite-``r`` pairs computed on
carrier-depleted intersections that no NaN check anywhere in the pipeline can
see — how many involve a variant the posted rule ALREADY EXCLUDES (PRE-filter,
a characterisation of what the rule correctly discards) and how many SURVIVE
into the banked panel (POST-filter, a silent corruption of the LD matrix)? The
two are reported as SEPARATE KEYS at BOTH row and pair level
(``n_tail_rows_member_occluded_panelwide`` vs
``n_tail_rows_neither_member_occluded_panelwide``, and the pair twins),
reconciled arithmetically or the tool STOPS. Nothing in the output permits
collapsing them into one number.

THE PREDICATE IS NOT A SILENT FORK. ``TAIL_MIN_CARRIERS_LOST_FRAC`` REPRODUCES
the boundary already inside ``pairwise_completeness_scan.summarize`` (whose
summary key ``n_defined_lost_frac_ge_0p9`` is the banked 3,094-row / 0.876%
tail). It could not be shared from there: the scanner's CODE is pinned against
``cb199b6`` by the live runbook's STEP 0 gate, which
``tests/m3/test_pairwise_completeness_scan.py`` executes in a subprocess and
requires to exit 0, and the runbook may not be edited to repair it. The two are
therefore held together by a DIFFERENTIAL test —
``tests/m3/test_pcs_panelwide_reclassify.py::test_the_tail_predicate_agrees_with_the_scanners_own_defined_lost_frac_ge_0p9``
— and, at runtime, by the optional ``--pcs-summary`` reconciliation against the
scanner's OWN emitted summary.

`THE RARER VARIANT` is decided by ``*_maf_marginal`` (each member's minor-allele
frequency over its OWN called set), NEVER by ``*_carriers_marginal``, which is
not comparable across members because ``n_called_del != n_called_partner`` IS
the phenomenon under study. On an EXACT MAF tie the member with the SMALLER
``*_carriers_retained`` is chosen — the WORSE precision, the same conservative
shape as the scanner's own MINOR-ALLELE TIE RULE — then smaller
``*_carriers_marginal``, then ``del``; ``rarer_by_maf_tie`` makes the tie
visible. ``informative_carriers_min`` is emitted BESIDE it because
``SE(r) ~ 1/sqrt(m)`` binds on the MINIMUM, and
``n_defined_rows_rarer_and_min_definitions_disagree`` COUNTS the rows where the
two differ rather than assuming they agree.

MONOTONICITY TRAVELS WITH THE TAIL CLAIM. Occlusion is monotone in the row set
(section 3), so a PRE-filter verdict on a tail row is SOUND and a POST-filter
verdict is CONDITIONAL on the row set named in ``provenance``.
``TAIL_VERDICT_SCOPE`` says exactly that, is written into the summary, and is
PRINTED beside the split — never a screenful away from it.

NO FLOOR IS PROPOSED ANYWHERE IN THIS MODULE. It emits the informative-carrier
DISTRIBUTION — integer nearest-rank percentiles, exact counts for every ``m`` in
``0..100``, and cumulative low-tail counts — computed twice, over all in-scope
defined rows and over the defined rows REACHING THE MATRIX. Choosing a floor
from "what passes" is the error this project has already made twice; a floor, if
ever adopted, must be derived from a location statistic on this distribution
with a stated purpose and margin, and live in a ledger slot. The absence is
machine-enforced by
``tests/m3/test_pcs_panelwide_reclassify.py::test_no_carrier_floor_is_declared_anywhere``,
which fails if a floor is DECLARED (a module-level numeric constant), APPLIED
(any comparison of an informative-carrier quantity against a numeric literal) or
NAMED (a key asserting a pass/fail/reliable verdict).

EMISSION STAYS BOUNDED. Per-row output is UNDEFINED rows plus TAIL rows only;
defined rows below the tail are COUNTED, never EMITTED, and ``reclassify``
refuses to return if that identity does not hold.

Pure stdlib. No numpy, no Hail, no plink, no network.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from occlusion_span_filter import detect_occluded_variants

# PRIVATE BY NAME, SHARED BY DESIGN: a local copy would diverge from the
# scanner's own window selection the day either moves. The identity of all
# three imports is asserted by
# test_the_frozen_detector_is_called_not_reimplemented.
from pairwise_completeness_scan import (  # noqa: F401
    DEFAULT_ANCESTRY,
    TSV_COLUMNS,
    _read_regions_tsv,
    iter_bim_windows,
)

__all__ = [
    "BANKED_POOLED_KEYS",
    "NO_FLOOR_NOTICE",
    "OUT_COLUMNS",
    "PER_REGION_KEYS",
    "POOLED_KEYS",
    "PROVENANCE_KEYS",
    "TAIL_MIN_CARRIERS_LOST_FRAC",
    "TAIL_SCOPE_POOLED_KEYS",
    "TAIL_VERDICT_SCOPE",
    "VERDICT_SCOPE",
    "is_tail_row",
    "main",
    "pair_max_lost_frac",
    "rarer_member",
    "reclassify",
]

#: The emitted per-row TSV columns, in order.
OUT_COLUMNS: tuple = (
    "region_id",
    "del_index",
    "del_vid",
    "del_pos",
    "partner_index",
    "partner_vid",
    "partner_pos",
    "offset",
    "side",
    "already_occluded",
    "pair_key",
    "del_occluded_panelwide",
    "partner_occluded_panelwide",
    "del_occluding_deletion_id",
    "partner_occluding_deletion_id",
    "occluding_deletion_id",
    "pair_reaches_matrix",
    "del_globally_invariant",
    "partner_globally_invariant",
    "member_id_ambiguous",
    # --- quick-260901-rvu: APPENDED, never reordered. The twenty above keep
    # --- their positions so an already-parsed verdict TSV stays readable.
    "row_class",
    "carriers_lost_frac_pair_max",
    "n_both_called",
    "del_carriers_retained",
    "partner_carriers_retained",
    "del_maf_marginal",
    "partner_maf_marginal",
    "rarer_member",
    "rarer_by_maf_tie",
    "informative_carriers_rarer",
    "informative_carriers_min",
    "informative_carriers_defs_disagree",
)

PROVENANCE_KEYS: tuple = (
    "pairs_tsv_path",
    "pairs_tsv_sha256",
    "pairs_tsv_n_lines",
    "bim_path",
    "bim_sha256",
    "bim_n_lines",
    "regions_tsv_path",
    "regions_tsv_sha256",
    "ancestry",
    "region_ids",
    "region_ids_selected",
    "region_ids_out_of_scope",
    "n_rows_in_window_per_region",
    "verdict_scope",
)

#: THE THIRTEEN THE BANKED RUN EMITTED. Names AND semantics are FROZEN: these
#: carry the pre-registered ``n_undefined_rows_in`` 15 /
#: ``n_undefined_distinct_pairs_in`` 13 / 14-1 rows / 12-1 pairs and
#: ``n_defined_rows_in`` 353,074. They are rolled up from the UNDEFINED-CLASS
#: subset ALONE — see :func:`reclassify`'s split-before-rollup comment.
BANKED_POOLED_KEYS: tuple = (
    "n_rows_in_tsv",
    "n_defined_rows_in",
    "n_undefined_rows_in",
    "n_undefined_distinct_pairs_in",
    "n_undefined_rows_out_of_scope",
    "n_rows_member_occluded_panelwide",
    "n_rows_neither_member_occluded_panelwide",
    "n_pairs_member_occluded_panelwide",
    "n_pairs_neither_member_occluded_panelwide",
    "n_pairs_neither_occluded_and_no_globally_invariant_member",
    "n_pairs_with_ambiguous_member_id",
    "ambiguous_member_ids",
    "occluded_member_vids",
)

#: ADDED BESIDE the thirteen (quick-260901-rvu). Nothing here feeds any key
#: above; the two scopes never share a rollup.
TAIL_SCOPE_POOLED_KEYS: tuple = (
    "tail_min_carriers_lost_frac",
    "n_tail_rows_in",
    "n_tail_rows_out_of_scope",
    "n_tail_distinct_pairs_in",
    "n_tail_rows_member_occluded_panelwide",
    "n_tail_rows_neither_member_occluded_panelwide",
    "n_tail_pairs_member_occluded_panelwide",
    "n_tail_pairs_neither_member_occluded_panelwide",
    "n_tail_regions_with_rows",
    # The DEFINED-row basis. ``n_defined_rows_out_of_scope`` exists so the
    # reconciliation below is checkable from the artifact alone: the two
    # classification counts are IN-SCOPE quantities while ``n_defined_rows_in``
    # is the INPUT count, and a reader who cannot see the difference cannot
    # verify the identity. A count is a claim — scope it and reconcile it.
    "n_defined_rows_out_of_scope",
    "n_defined_rows_member_occluded_panelwide",
    "n_defined_rows_reaching_matrix",
    "n_defined_rows_rarer_and_min_definitions_disagree",
    "informative_carriers_percentiles_defined_rows",
    "informative_carriers_percentiles_defined_rows_reaching_matrix",
    "informative_carriers_low_tail_defined_rows",
    "informative_carriers_low_tail_defined_rows_reaching_matrix",
    "no_floor_notice",
    "tail_verdict_scope",
)

POOLED_KEYS: tuple = BANKED_POOLED_KEYS + TAIL_SCOPE_POOLED_KEYS

PER_REGION_KEYS: tuple = (
    "region_id",
    "chrom",
    "start_bp",
    "end_bp",
    "n_rows_in_window",
    "n_occluded_ids_in_window",
    "n_undefined_rows_in",
    "n_undefined_distinct_pairs_in",
    "n_rows_member_occluded_panelwide",
    "n_rows_neither_member_occluded_panelwide",
    "n_pairs_member_occluded_panelwide",
    "n_pairs_neither_member_occluded_panelwide",
    "n_pairs_neither_occluded_and_no_globally_invariant_member",
    "n_pairs_with_ambiguous_member_id",
    "ambiguous_member_ids",
    # --- quick-260901-rvu ------------------------------------------------- #
    "n_defined_rows_in",
    "n_defined_rows_reaching_matrix",
    "n_tail_rows_in",
    "n_tail_distinct_pairs_in",
    "n_tail_rows_member_occluded_panelwide",
    "n_tail_rows_neither_member_occluded_panelwide",
    "n_tail_pairs_member_occluded_panelwide",
    "n_tail_pairs_neither_member_occluded_panelwide",
)

#: The literal scope sentence written into every summary. Occlusion is MONOTONE
#: in the row set, so the two verdict directions do NOT carry the same warrant.
VERDICT_SCOPE: str = (
    "Occlusion is MONOTONE in the row set: for a variant present in both, "
    "R subset-of R' implies occluded(v, R) implies occluded(v, R'). An OCCLUDED "
    "verdict computed on a SUBSET of the region window is therefore SOUND, while "
    "a NOT-OCCLUDED verdict on a SUBSET is NOT — it can flip once the missing "
    "rows are supplied. Every not-occluded verdict in this summary is RELATIVE "
    "TO the row set named by bim_path / bim_sha256 / bim_n_lines and the "
    "per-region n_rows_in_window counts recorded beside it."
)

#: THE TAIL BOUNDARY — A RE-DERIVATION, NOT A NEW THRESHOLD.
#:
#: This REPRODUCES the ``frac >= 0.9`` comparison already inside
#: ``pairwise_completeness_scan.summarize``, whose summary key
#: ``n_defined_lost_frac_ge_0p9`` is the banked 3,094-row (0.876%) partial-
#: confounding tail. It is not a policy choice made here and it moves nothing.
#:
#: It is DECLARED here rather than imported because the scanner's CODE is pinned
#: against ``cb199b6`` by the live runbook's STEP 0 gate — which
#: ``tests/m3/test_pairwise_completeness_scan.py`` EXECUTES in a subprocess and
#: requires to exit 0 — so the predicate cannot be extracted into a shared helper
#: there, and the runbook may not be edited to repair it. THE ENFORCER THAT FAILS
#: IF THE TWO EVER DISAGREE:
#: ``tests/m3/test_pcs_panelwide_reclassify.py::test_the_tail_predicate_agrees_with_the_scanners_own_defined_lost_frac_ge_0p9``
#: (differential, over a grid that includes ``frac == 0.9`` EXACTLY and both
#: float neighbours), plus the optional runtime ``--pcs-summary`` reconciliation.
#:
#: ⚠ The bins and the tail DELIBERATELY disagree at the boundary:
#: ``_lost_frac_bin(0.9) == "(0.5,0.9]"`` (inclusive right edge) while the tail
#: INCLUDES 0.9 (``>=``). The bins are NOT a substitute for the tail.
TAIL_MIN_CARRIERS_LOST_FRAC: float = 0.9

#: The DISCLAIMER, written into every summary and PRINTED by :func:`main`.
NO_FLOOR_NOTICE: str = (
    "NO CARRIER FLOOR IS PROPOSED BY THIS TOOL. It emits the informative-carrier "
    "DISTRIBUTION only. A floor, if ever adopted, must be derived from a location "
    "statistic on this distribution with a stated purpose and margin and live in a "
    "ledger slot, not as a literal here."
)

#: The scope condition that must travel WITH the pre/post split, never beside it.
TAIL_VERDICT_SCOPE: str = (
    "PRE-filter vs POST-filter carries the SAME monotonicity asymmetry as the "
    "undefined-row verdicts: a tail row classified PRE-filter (a member IS on the "
    "panel-wide excludelist) is SOUND, while a tail row classified POST-filter "
    "(NEITHER member is) is CONDITIONAL on the row set named in provenance and can "
    "flip to PRE-filter once more rows are supplied. It cannot flip the other way."
)

#: Reported quantiles for the informative-carrier distribution.
_PERCENTILE_QUANTILES: tuple = (0, 1, 5, 10, 25, 50, 75, 90, 99, 100)

#: The low tail is reported EXACTLY for every m in ``0..cap``, zeros included.
_LOW_TAIL_CAP: int = 100
_LOW_TAIL_CUMULATIVE_AT: tuple = (0, 1, 2, 5, 10, 25, 50, 100)

#: ``.bim`` column indices (mirrored from occlusion_span_filter's convention:
#: A1 = ALT is column 5, A2 = REF is column 6, and len(REF) IS the footprint).
_BIM_COL_ID = 1


# =========================================================================== #
# Small, separately testable helpers                                          #
# =========================================================================== #

def _sha256(path: "str | Path") -> str:
    """Streamed sha256 of a file.

    A full pass over a ~20.7M-line cohort manifest takes seconds-to-minutes.
    That is PROVENANCE, not overhead: a verdict that cannot name the bytes it
    was computed against is not reproducible.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count_lines(path: "str | Path") -> int:
    """Non-blank line count, streamed."""
    total = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                total += 1
    return total


def _parse_bool(value: str) -> bool:
    """Parse the scanner's rendered boolean, LOUDLY.

    ``_render_field`` writes exactly ``True`` / ``False``; anything else means
    the artifact was not produced by that writer and a truthiness coercion
    (``bool("False") is True``) would invert the verdict silently.
    """
    text = str(value).strip()
    if text == "True":
        return True
    if text == "False":
        return False
    raise ValueError(
        f"unparseable boolean field {value!r}: the scanner renders exactly "
        f"'True' or 'False'; anything else means this TSV was not written by "
        f"pairwise_completeness_scan.write_tsv"
    )


def _count_distinct_pairs(rows) -> int:
    """DISTINCT ``(region_id, pair_key)`` count over ``rows``.

    A MODULE-GLOBAL function, not an inline expression, so the reconciliation
    below has something a test can monkeypatch into disagreement — a
    self-check that has never been observed failing is not a check
    (``feedback_green_assertion_needs_a_negative_control``).
    """
    return len({(r["region_id"], r["pair_key"]) for r in rows})


def _reconcile_or_raise(scope: str, unit: str, member: int, neither: int,
                        total: int) -> None:
    """The two populations are EXHAUSTIVE over ``total`` or the tool STOPS.

    A count is a claim: it reconciles arithmetically or nothing is written.
    """
    if member + neither != total:
        raise ValueError(
            f"{scope}: the two panel-wide populations do not reconcile at the "
            f"{unit} level — member_occluded {member} + neither {neither} = "
            f"{member + neither}, but the input carries {total} {unit}(s). "
            f"These MUST be exhaustive and disjoint; a difference means the "
            f"classification lost or double-counted a {unit}."
        )


def _render(value) -> str:
    """Render one scalar for the TSV, deterministically."""
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


# =========================================================================== #
# The DEFINED-row tail and the informative-carrier distribution                #
# (quick-260901-rvu). MODULE-GLOBAL by design, so a test can monkeypatch them  #
# into disagreement — a self-check never observed failing is not a check.      #
# =========================================================================== #

def pair_max_lost_frac(row) -> float:
    """``max(del_carriers_lost_frac, partner_carriers_lost_frac)`` for one row.

    The scanner wrote these floats through ``_render_field``, i.e. ``repr``
    (shortest round-trip), so ``float()`` recovers the EXACT value it computed.
    An unparseable field RAISES rather than defaulting: a silent 0.0 would move
    a row out of the tail and understate the very count this tool exists for.
    """
    try:
        del_frac = float(row["del_carriers_lost_frac"])
        partner_frac = float(row["partner_carriers_lost_frac"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"unparseable carriers-lost fraction on pair "
            f"{row.get('region_id')!r}/{row.get('pair_key')!r}: "
            f"del={row.get('del_carriers_lost_frac')!r} "
            f"partner={row.get('partner_carriers_lost_frac')!r}. The scanner "
            f"renders these with repr(); anything else means this TSV was not "
            f"written by pairwise_completeness_scan.write_tsv."
        ) from exc
    return max(del_frac, partner_frac)


def is_tail_row(row, *, threshold: "float | None" = None) -> bool:
    """Is this a DEFINED row in the partial-confounding tail?

    ⚠ ``threshold`` is resolved from :data:`TAIL_MIN_CARRIERS_LOST_FRAC` AT CALL
    TIME, never bound as a default argument at ``def`` time. A default would be
    frozen at import and would make every monkeypatch of the module global
    SILENTLY INERT — i.e. it would make the differential test's negative control
    vacuous, which is worse than having no control at all.

    UNDEFINED rows are excluded on BOTH sides of the differential: the tail is a
    DEFINED-row quantity by construction (``lost_frac == 1.0`` implies the member
    is invariant, which implies the pair is undefined).
    """
    if threshold is None:
        threshold = TAIL_MIN_CARRIERS_LOST_FRAC
    if _parse_bool(row["undefined"]):
        return False
    return pair_max_lost_frac(row) >= threshold


def rarer_member(row) -> tuple:
    """Return ``("del"|"partner", maf_tie)`` — which member is `the rarer variant`.

    RARITY IS A FREQUENCY, NOT A COUNT. The decision is made on
    ``*_maf_marginal`` — each member's minor-allele frequency over its OWN called
    set — and NEVER on ``*_carriers_marginal``, because ``n_called_del !=
    n_called_partner`` IS the phenomenon under study: a member called on a much
    larger sample can carry more minor alleles while being the rarer variant.

    ON AN EXACT TIE the choice breaks toward the WORSE PRECISION: the smaller
    ``*_carriers_retained`` first, then the smaller ``*_carriers_marginal``, then
    ``del`` so the result is total and deterministic. That is the same
    conservative shape as the scanner's own MINOR-ALLELE TIE RULE, which reports
    the LARGER ``lost_frac`` when ``af_a1 == 0.5``. The tie is FLAGGED in the
    returned boolean and emitted as ``rarer_by_maf_tie`` so a reader can see the
    choice was forced rather than measured.
    """
    del_maf = float(row["del_maf_marginal"])
    partner_maf = float(row["partner_maf_marginal"])
    if del_maf < partner_maf:
        return "del", False
    if partner_maf < del_maf:
        return "partner", False

    del_retained = int(row["del_carriers_retained"])
    partner_retained = int(row["partner_carriers_retained"])
    if del_retained < partner_retained:
        return "del", True
    if partner_retained < del_retained:
        return "partner", True

    del_marginal = int(row["del_carriers_marginal"])
    partner_marginal = int(row["partner_carriers_marginal"])
    if del_marginal < partner_marginal:
        return "del", True
    if partner_marginal < del_marginal:
        return "partner", True
    return "del", True


def _percentiles(sorted_values, quantiles=_PERCENTILE_QUANTILES) -> dict:
    """INTEGER NEAREST-RANK percentiles over an ALREADY-SORTED sequence.

    ``rank = ceil(q * n / 100)`` clamped to ``>= 1``, value ``sorted[rank - 1]``.
    Integer arithmetic only (``-(-a // b)`` is exact ceiling division), so no
    float rounding can move a reported carrier count. CONVENTION, stated so no
    reader has to guess: ``p0`` is the MINIMUM and ``p100`` the MAXIMUM. Returns
    ``{}`` on an empty input — an empty distribution has no percentiles, and
    inventing zeros would read as "every pair has zero informative carriers".
    """
    n = len(sorted_values)
    if n == 0:
        return {}
    out: dict = {}
    for quantile in quantiles:
        rank = -(-int(quantile) * n // 100)
        if rank < 1:
            rank = 1
        out[f"p{int(quantile)}"] = sorted_values[rank - 1]
    return out


def _low_tail_counts(values, *, cap: int = _LOW_TAIL_CAP,
                     cumulative_at=_LOW_TAIL_CUMULATIVE_AT) -> dict:
    """EXACT counts for EVERY m in ``0..cap`` (zeros included) plus prefix sums.

    Emitting a key per m — not only the occupied ones — is what lets a reader see
    the SHAPE of the low tail instead of a summary of it. The ``n_le_K`` entries
    are the running prefix sums of those same counts, so the two cannot drift.
    """
    counts = {m: 0 for m in range(0, cap + 1)}
    n_above = 0
    for value in values:
        count = int(value)
        if count < 0:
            raise ValueError(
                f"negative informative-carrier count {count!r}: a retained "
                f"minor-allele carrier count cannot be below zero, so this "
                f"artifact is not the scanner's own output"
            )
        if count > cap:
            n_above += 1
        else:
            counts[count] += 1

    out = {f"m_{m}": counts[m] for m in range(0, cap + 1)}
    marks = {int(k) for k in cumulative_at}
    running = 0
    for m in range(0, cap + 1):
        running += counts[m]
        if m in marks:
            out[f"n_le_{m}"] = running
    out[f"n_gt_{cap}"] = n_above
    return out


# =========================================================================== #
# The reclassification                                                        #
# =========================================================================== #

def _read_pairs_tsv(pairs_tsv: Path) -> list:
    """Parse the pairs TSV BY HEADER, never positionally.

    RAISES if the header is not EXACTLY ``TSV_COLUMNS``: a drifted header means
    the artifact was not produced by this scanner and its pair semantics are
    unverified.
    """
    with open(pairs_tsv, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        observed = tuple(reader.fieldnames or ())
        if observed != tuple(TSV_COLUMNS):
            missing = [c for c in TSV_COLUMNS if c not in observed]
            unexpected = [c for c in observed if c not in TSV_COLUMNS]
            raise ValueError(
                f"pairs TSV header does not equal pairwise_completeness_scan."
                f"TSV_COLUMNS for {pairs_tsv}: missing {missing}, unexpected "
                f"{unexpected}, observed {len(observed)} columns vs expected "
                f"{len(TSV_COLUMNS)}. A drifted header means this artifact was "
                f"not written by this scanner, so its pair semantics are "
                f"unverified and no verdict is computed."
            )
        return [dict(row) for row in reader]


def _assert_members_present(region_id: str, chrom: str, start_bp: int,
                            end_bp: int, row, id_counts, n_window_rows: int) -> None:
    """Both pair members must appear in the region's window row set, or STOP.

    Applies to UNDEFINED, TAIL and BELOW-TAIL rows alike: a not-occluded verdict
    on a member you cannot see is a silent fabrication, and a mismatched ``.bim``
    must be loud rather than quietly partial.
    """
    for role in ("del_vid", "partner_vid"):
        vid = row[role]
        if vid not in id_counts:
            raise ValueError(
                f"region {region_id}: {role} {vid!r} from the pairs TSV does "
                f"not appear in that region's window row set "
                f"[{chrom}:{start_bp}-{end_bp}] ({n_window_rows} rows). "
                f"The .bim you supplied is not the .bim these pairs came "
                f"from; a not-occluded verdict here would be a silent "
                f"fabrication, so nothing is classified."
            )


def _verdict_row(region_id: str, row, row_class: str, occluded: set,
                 attributed: dict, id_counts) -> dict:
    """One per-row verdict dict, identical in shape for every ``row_class``."""
    del_vid = row["del_vid"]
    partner_vid = row["partner_vid"]
    del_occ = del_vid in occluded
    partner_occ = partner_vid in occluded
    del_occluder = attributed.get(del_vid, "") if del_occ else ""
    partner_occluder = attributed.get(partner_vid, "") if partner_occ else ""

    member, maf_tie = rarer_member(row)
    del_retained = int(row["del_carriers_retained"])
    partner_retained = int(row["partner_carriers_retained"])
    informative_carriers_rarer = (
        del_retained if member == "del" else partner_retained
    )
    # SE(r) ~ 1/sqrt(m) binds on the MINIMUM, while `the rarer variant` is the
    # wording of the question. They are different quantities; both are emitted
    # and their disagreement is counted, never assumed away.
    informative_carriers_min = min(del_retained, partner_retained)

    return {
        "region_id": region_id,
        "del_index": row["del_index"],
        "del_vid": del_vid,
        "del_pos": row["del_pos"],
        "partner_index": row["partner_index"],
        "partner_vid": partner_vid,
        "partner_pos": row["partner_pos"],
        "offset": row["offset"],
        "side": row["side"],
        "already_occluded": _parse_bool(row["already_occluded"]),
        "pair_key": row["pair_key"],
        "del_occluded_panelwide": del_occ,
        "partner_occluded_panelwide": partner_occ,
        "del_occluding_deletion_id": del_occluder,
        "partner_occluding_deletion_id": partner_occluder,
        # PRECEDENCE, stated: the deletion member's attribution when it is
        # occluded, otherwise the partner's. The two per-member columns
        # above stay authoritative when BOTH members are occluded.
        "occluding_deletion_id": del_occluder or partner_occluder,
        "pair_reaches_matrix": not (del_occ or partner_occ),
        "del_globally_invariant": _parse_bool(row["del_globally_invariant"]),
        "partner_globally_invariant": _parse_bool(
            row["partner_globally_invariant"]
        ),
        "member_id_ambiguous": bool(
            id_counts[del_vid] > 1 or id_counts[partner_vid] > 1
        ),
        "row_class": row_class,
        "carriers_lost_frac_pair_max": pair_max_lost_frac(row),
        "n_both_called": int(row["n_both_called"]),
        "del_carriers_retained": del_retained,
        "partner_carriers_retained": partner_retained,
        "del_maf_marginal": float(row["del_maf_marginal"]),
        "partner_maf_marginal": float(row["partner_maf_marginal"]),
        "rarer_member": member,
        "rarer_by_maf_tie": maf_tie,
        "informative_carriers_rarer": informative_carriers_rarer,
        "informative_carriers_min": informative_carriers_min,
        "informative_carriers_defs_disagree": (
            informative_carriers_rarer != informative_carriers_min
        ),
    }


def _classify_region(region_id: str, chrom: str, start_bp: int, end_bp: int,
                     indexed_rows, undefined_rows: list,
                     defined_rows: "list | None" = None,
                     *, tail_threshold: "float | None" = None) -> tuple:
    """Reclassify ONE region's rows against its FULL window row set.

    ONE excludelist per region — the single ``detect_occluded_variants`` call
    below — is shared by the undefined rows and the defined tail. A second call
    with a different row set would answer a different question and would break
    the monotonicity argument that section (3) rests on.
    """
    window_rows = [row for _index, row in indexed_rows]
    occluded_ids, edges = detect_occluded_variants(window_rows)
    occluded = set(occluded_ids)
    attributed = {edge.occluded_id: edge.occluder_id for edge in edges}
    id_counts = Counter(str(row[_BIM_COL_ID]) for row in window_rows)
    n_window_rows = len(window_rows)

    out_rows = []
    ambiguous_vids: set = set()
    for row in undefined_rows:
        _assert_members_present(
            region_id, chrom, start_bp, end_bp, row, id_counts, n_window_rows
        )
        out_rows.append(
            _verdict_row(region_id, row, "undefined", occluded, attributed,
                         id_counts)
        )
        # NAME the ids that are ACTUALLY duplicated. Collecting both members of
        # a flagged ROW would name the innocent partner too, turning a precise
        # production-semantics warning into a list a reader cannot act on.
        # ⚠ UNDEFINED-SCOPE ONLY: this set feeds the BANKED `ambiguous_member_ids`
        # key, so tail rows must never contribute to it.
        for vid in (row["del_vid"], row["partner_vid"]):
            if id_counts[vid] > 1:
                ambiguous_vids.add(vid)

    carriers_all: list = []
    carriers_reaching: list = []
    n_defs_disagree = 0
    n_defined_member_occluded = 0
    n_defined_reaching = 0
    for row in defined_rows or ():
        _assert_members_present(
            region_id, chrom, start_bp, end_bp, row, id_counts, n_window_rows
        )
        row_class = (
            "tail" if is_tail_row(row, threshold=tail_threshold) else "below_tail"
        )
        verdict = _verdict_row(
            region_id, row, row_class, occluded, attributed, id_counts
        )
        carriers_all.append(verdict["informative_carriers_rarer"])
        if verdict["pair_reaches_matrix"]:
            carriers_reaching.append(verdict["informative_carriers_rarer"])
            n_defined_reaching += 1
        else:
            n_defined_member_occluded += 1
        if verdict["informative_carriers_defs_disagree"]:
            n_defs_disagree += 1
        # EMISSION STAYS BOUNDED: undefined + tail only. Below-tail defined rows
        # feed the aggregates and are never appended.
        if row_class == "tail":
            out_rows.append(verdict)

    defined_aggregates = {
        "n_defined_rows_in": len(defined_rows or ()),
        "n_defined_rows_member_occluded_panelwide": n_defined_member_occluded,
        "n_defined_rows_reaching_matrix": n_defined_reaching,
        "n_defined_rows_rarer_and_min_definitions_disagree": n_defs_disagree,
        "carriers_all": carriers_all,
        "carriers_reaching": carriers_reaching,
    }
    return (out_rows, sorted(occluded), n_window_rows, sorted(ambiguous_vids),
            defined_aggregates)


def _occlusion_split(scope: str, out_rows: list) -> tuple:
    """The row-level and pair-level occlusion split for ONE scope, reconciled.

    SHARED by the UNDEFINED rollup and the TAIL rollup so the two can never
    diverge in how they count — but called on DISJOINT row subsets, never on the
    combined list (``feedback_extract_reusable_utilities``).
    """
    n_rows_member = sum(
        1 for r in out_rows
        if r["del_occluded_panelwide"] or r["partner_occluded_panelwide"]
    )
    n_rows_neither = len(out_rows) - n_rows_member
    _reconcile_or_raise(scope, "row", n_rows_member, n_rows_neither, len(out_rows))

    pair_member: dict = {}
    pair_gi: dict = {}
    for r in out_rows:
        key = (r["region_id"], r["pair_key"])
        occluded = r["del_occluded_panelwide"] or r["partner_occluded_panelwide"]
        pair_member[key] = pair_member.get(key, False) or occluded
        gi = r["del_globally_invariant"] or r["partner_globally_invariant"]
        pair_gi[key] = pair_gi.get(key, False) or gi

    n_pairs_member = sum(1 for v in pair_member.values() if v)
    n_pairs_neither = sum(1 for v in pair_member.values() if not v)
    n_distinct = _count_distinct_pairs(out_rows)
    _reconcile_or_raise(scope, "pair", n_pairs_member, n_pairs_neither, n_distinct)
    return (n_rows_member, n_rows_neither, n_pairs_member, n_pairs_neither,
            n_distinct, pair_member, pair_gi)


def _roll_up_tail(scope: str, out_rows: list) -> dict:
    """The TAIL scope's counts. SEPARATE KEYS — never merged with the undefined
    scope, and never computed from the combined row list."""
    (n_rows_member, n_rows_neither, n_pairs_member, n_pairs_neither, n_distinct,
     _pair_member, _pair_gi) = _occlusion_split(scope, out_rows)
    return {
        "n_tail_rows_in": len(out_rows),
        "n_tail_distinct_pairs_in": n_distinct,
        "n_tail_rows_member_occluded_panelwide": n_rows_member,
        "n_tail_rows_neither_member_occluded_panelwide": n_rows_neither,
        "n_tail_pairs_member_occluded_panelwide": n_pairs_member,
        "n_tail_pairs_neither_member_occluded_panelwide": n_pairs_neither,
    }


def _roll_up(scope: str, out_rows: list, ambiguous_vids) -> dict:
    """Row-level AND pair-level counts for one scope, RECONCILED before return.

    ⚠ CALL THIS ON THE UNDEFINED-CLASS SUBSET ONLY. Its keys are the BANKED
    thirteen; feeding it the combined list would fold tail rows into
    ``n_undefined_rows_in`` and the occlusion twins and silently move the
    pre-registered 15 / 13 / 14-1 / 12-1.
    """
    (n_rows_member, n_rows_neither, n_pairs_member, n_pairs_neither, n_distinct,
     pair_member, pair_gi) = _occlusion_split(scope, out_rows)

    third_tier = sum(
        1 for key, occluded in pair_member.items()
        if not occluded and not pair_gi[key]
    )
    ambiguous_ids = sorted(set(ambiguous_vids))
    n_pairs_ambiguous = len({
        (r["region_id"], r["pair_key"]) for r in out_rows if r["member_id_ambiguous"]
    })
    occluded_member_vids = sorted({
        vid
        for r in out_rows
        for vid, flag in (
            (r["del_vid"], r["del_occluded_panelwide"]),
            (r["partner_vid"], r["partner_occluded_panelwide"]),
        )
        if flag
    })
    return {
        "n_undefined_rows_in": len(out_rows),
        "n_undefined_distinct_pairs_in": n_distinct,
        "n_rows_member_occluded_panelwide": n_rows_member,
        "n_rows_neither_member_occluded_panelwide": n_rows_neither,
        "n_pairs_member_occluded_panelwide": n_pairs_member,
        "n_pairs_neither_member_occluded_panelwide": n_pairs_neither,
        "n_pairs_neither_occluded_and_no_globally_invariant_member": third_tier,
        "n_pairs_with_ambiguous_member_id": n_pairs_ambiguous,
        "ambiguous_member_ids": ambiguous_ids,
        "occluded_member_vids": occluded_member_vids,
    }


def _reconcile_against_scanner_summary(pcs_summary: "str | Path", scan_ids,
                                       n_tail_rows_in: int,
                                       threshold: float) -> None:
    """Close the local tail predicate against the SCANNER'S OWN measurement.

    Sums ``n_defined_lost_frac_ge_0p9`` over the SCANNED regions of the scanner's
    emitted summary (a dict keyed by ``region_id``) and RAISES if it differs from
    ``n_tail_rows_in``, naming both numbers and both bases. This is the runtime
    twin of the differential test: the test proves the predicates agree on a
    synthetic grid, this proves they agree on the artifact actually in hand.
    """
    if threshold != TAIL_MIN_CARRIERS_LOST_FRAC:
        raise ValueError(
            f"--pcs-summary reconciliation requested with a tail threshold of "
            f"{threshold!r}, but the scanner's n_defined_lost_frac_ge_0p9 was "
            f"computed at {TAIL_MIN_CARRIERS_LOST_FRAC!r}. The two would be "
            f"counting different populations; drop --pcs-summary or restore the "
            f"default threshold."
        )
    payload = json.loads(Path(pcs_summary).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(
            f"{pcs_summary} is not a region-keyed summary dict (got "
            f"{type(payload).__name__}); it was not written by "
            f"pairwise_completeness_scan.main"
        )
    missing = sorted(rid for rid in scan_ids if rid not in payload)
    if missing:
        raise ValueError(
            f"{pcs_summary} carries no summary for scanned region(s) {missing}. "
            f"A partial reconciliation would compare a subset against a total; "
            f"supply the summary for the SAME regions or drop --pcs-summary."
        )
    scanner_total = 0
    for region_id in sorted(scan_ids):
        block = payload[region_id]
        if "n_defined_lost_frac_ge_0p9" not in block:
            raise ValueError(
                f"{pcs_summary}: region {region_id!r} has no "
                f"n_defined_lost_frac_ge_0p9 key; this is not a "
                f"pairwise_completeness_scan summary."
            )
        scanner_total += int(block["n_defined_lost_frac_ge_0p9"])
    if scanner_total != n_tail_rows_in:
        raise ValueError(
            f"THE TAIL PREDICATE DISAGREES WITH THE SCANNER'S OWN MEASUREMENT: "
            f"this run classified n_tail_rows_in={n_tail_rows_in} defined rows "
            f"at max(carriers_lost_frac) >= {TAIL_MIN_CARRIERS_LOST_FRAC!r} "
            f"(basis: the in-scope rows of the pairs TSV), while "
            f"{pcs_summary} reports n_defined_lost_frac_ge_0p9 summing to "
            f"{scanner_total} over the same {len(scan_ids)} scanned region(s) "
            f"(basis: the scanner's per-region summaries). A count is a claim: "
            f"nothing is written until these reconcile."
        )


def reclassify(pairs_tsv: "str | Path", bim_path: "str | Path",
               regions_tsv: "str | Path", *, ancestry: str = DEFAULT_ANCESTRY,
               region_ids: "list[str] | None" = None,
               tail_min_lost_frac: "float | None" = None,
               pcs_summary: "str | Path | None" = None) -> tuple:
    """Return ``(out_rows, summary)`` for one emitted ``pcs_pairs.tsv``.

    Reads the pairs TSV, the region manifest and the cohort ``.bim``. Nothing
    else is opened; no genotype is decoded; the sweep is never re-run.
    """
    pairs_tsv = Path(pairs_tsv)
    bim_path = Path(bim_path)
    regions_tsv = Path(regions_tsv)
    for path in (pairs_tsv, regions_tsv):
        if not path.exists():
            raise FileNotFoundError(f"missing input: {path}")
    if not bim_path.exists():
        raise FileNotFoundError(
            f"missing cohort .bim: {bim_path}. This tool reads the prefix's own "
            f".bim and nothing else."
        )

    threshold = (
        TAIL_MIN_CARRIERS_LOST_FRAC if tail_min_lost_frac is None
        else float(tail_min_lost_frac)
    )

    rows = _read_pairs_tsv(pairs_tsv)
    undefined_rows = [r for r in rows if _parse_bool(r["undefined"])]
    # THE TWO LINES THIS EXTENSION EXISTS TO CHANGE. Every defined row was
    # already READ; none was ever CLASSIFIED. The question was UNMEASURED, not
    # mis-scoped.
    defined_rows = [r for r in rows if not _parse_bool(r["undefined"])]

    windows_selected = _read_regions_tsv(regions_tsv, region_ids, ancestry=ancestry)
    selected_ids = [w[0] for w in windows_selected]
    selected_set = set(selected_ids)

    tsv_region_ids = sorted({r["region_id"] for r in rows})
    unknown = [rid for rid in tsv_region_ids if rid not in selected_set]
    if unknown and region_ids is None:
        raise ValueError(
            f"pairs TSV carries rows for region id(s) {unknown} that "
            f"{regions_tsv} does not contain for ancestry {ancestry!r}. That is "
            f"a manifest/ancestry mismatch, not a residual: refusing to drop "
            f"them silently."
        )
    in_scope = [r for r in undefined_rows if r["region_id"] in selected_set]
    defined_in_scope = [r for r in defined_rows if r["region_id"] in selected_set]
    defined_out_of_scope = [
        r for r in defined_rows if r["region_id"] not in selected_set
    ]
    n_tail_rows_out_of_scope = sum(
        1 for r in defined_out_of_scope if is_tail_row(r, threshold=threshold)
    )
    out_of_scope_ids = unknown

    # The scan set is the UNION: with defined rows in scope this grows from the
    # 6 regions carrying undefined rows to all 21 carrying any row at all.
    scan_ids = {r["region_id"] for r in in_scope}
    scan_ids |= {r["region_id"] for r in defined_in_scope}
    windows = [w for w in windows_selected if w[0] in scan_ids]
    indexed = iter_bim_windows(
        # pad_bp=0 is LOAD-BEARING. Production builds its excludelist row set
        # from EXACTLY the in-window rows for [from_bp, to_bp] on chrom, with NO
        # padding (run_native_ld_panel.py:851-878). A padded row set is a
        # DIFFERENT population and would answer a different question.
        bim_path, windows, pad_bp=0,
    )

    all_out: list = []
    all_undefined_out: list = []
    all_tail_out: list = []
    per_region: dict = {}
    rows_in_window: dict = {}
    pooled_ambiguous: set = set()
    carriers_all: list = []
    carriers_reaching: list = []
    n_defined_member_occluded = 0
    n_defined_reaching = 0
    n_defs_disagree = 0
    n_tail_regions_with_rows = 0
    for region_id, chrom, start_bp, end_bp in windows:
        region_rows = [r for r in in_scope if r["region_id"] == region_id]
        region_defined = [
            r for r in defined_in_scope if r["region_id"] == region_id
        ]
        (out_rows, occluded_ids, n_window_rows, region_ambiguous,
         defined_aggregates) = _classify_region(
            region_id, chrom, start_bp, end_bp, indexed[region_id], region_rows,
            region_defined, tail_threshold=threshold,
        )
        # ⚠ SPLIT BY row_class BEFORE ROLLING UP. `_roll_up` produces the BANKED
        # thirteen and must see the UNDEFINED subset ALONE; the tail rollup is a
        # SECOND, separately-scoped call. Letting the combined list reach
        # `_roll_up` silently moves 15 / 13 / 14-1 / 12-1.
        region_undefined_out = [r for r in out_rows if r["row_class"] == "undefined"]
        region_tail_out = [r for r in out_rows if r["row_class"] == "tail"]

        pooled_ambiguous.update(region_ambiguous)
        rollup = _roll_up(
            f"region {region_id}", region_undefined_out, region_ambiguous
        )
        rollup.pop("occluded_member_vids")
        tail_rollup = _roll_up_tail(f"region {region_id} TAIL", region_tail_out)
        if tail_rollup["n_tail_rows_in"]:
            n_tail_regions_with_rows += 1
        per_region[region_id] = {
            "region_id": region_id,
            "chrom": chrom,
            "start_bp": int(start_bp),
            "end_bp": int(end_bp),
            "n_rows_in_window": n_window_rows,
            "n_occluded_ids_in_window": len(occluded_ids),
            **rollup,
            **tail_rollup,
            "n_defined_rows_in": defined_aggregates["n_defined_rows_in"],
            "n_defined_rows_reaching_matrix":
                defined_aggregates["n_defined_rows_reaching_matrix"],
        }
        rows_in_window[region_id] = n_window_rows
        all_out.extend(out_rows)
        all_undefined_out.extend(region_undefined_out)
        all_tail_out.extend(region_tail_out)
        carriers_all.extend(defined_aggregates["carriers_all"])
        carriers_reaching.extend(defined_aggregates["carriers_reaching"])
        n_defined_member_occluded += defined_aggregates[
            "n_defined_rows_member_occluded_panelwide"
        ]
        n_defined_reaching += defined_aggregates["n_defined_rows_reaching_matrix"]
        n_defs_disagree += defined_aggregates[
            "n_defined_rows_rarer_and_min_definitions_disagree"
        ]

    # EMISSION IS BOUNDED, and the bound is CHECKED rather than narrated.
    if len(all_out) != len(all_undefined_out) + len(all_tail_out):
        raise ValueError(
            f"emission bound violated: {len(all_out)} emitted rows against "
            f"{len(all_undefined_out)} undefined + {len(all_tail_out)} tail. "
            f"Only undefined and tail rows may be emitted; a third class means "
            f"a below-tail defined row escaped into the output."
        )

    pooled = _roll_up("pooled", all_undefined_out, pooled_ambiguous)
    pooled.update({
        "n_rows_in_tsv": len(rows),
        "n_defined_rows_in": len(rows) - len(undefined_rows),
        "n_undefined_rows_out_of_scope": len(undefined_rows) - len(in_scope),
    })

    tail_pooled = _roll_up_tail("pooled TAIL", all_tail_out)
    _reconcile_or_raise(
        "pooled DEFINED (in-scope basis)", "row", n_defined_member_occluded,
        n_defined_reaching, len(defined_in_scope),
    )
    if pcs_summary is not None:
        _reconcile_against_scanner_summary(
            pcs_summary, scan_ids, tail_pooled["n_tail_rows_in"], threshold
        )
    carriers_all.sort()
    carriers_reaching.sort()
    pooled.update(tail_pooled)
    pooled.update({
        "tail_min_carriers_lost_frac": threshold,
        "n_tail_rows_out_of_scope": n_tail_rows_out_of_scope,
        "n_tail_regions_with_rows": n_tail_regions_with_rows,
        "n_defined_rows_out_of_scope": len(defined_out_of_scope),
        "n_defined_rows_member_occluded_panelwide": n_defined_member_occluded,
        "n_defined_rows_reaching_matrix": n_defined_reaching,
        "n_defined_rows_rarer_and_min_definitions_disagree": n_defs_disagree,
        "informative_carriers_percentiles_defined_rows":
            _percentiles(carriers_all),
        "informative_carriers_percentiles_defined_rows_reaching_matrix":
            _percentiles(carriers_reaching),
        "informative_carriers_low_tail_defined_rows":
            _low_tail_counts(carriers_all),
        "informative_carriers_low_tail_defined_rows_reaching_matrix":
            _low_tail_counts(carriers_reaching),
        "no_floor_notice": NO_FLOOR_NOTICE,
        "tail_verdict_scope": TAIL_VERDICT_SCOPE,
    })

    summary = {
        "provenance": {
            "pairs_tsv_path": str(pairs_tsv),
            "pairs_tsv_sha256": _sha256(pairs_tsv),
            "pairs_tsv_n_lines": _count_lines(pairs_tsv),
            "bim_path": str(bim_path),
            "bim_sha256": _sha256(bim_path),
            "bim_n_lines": _count_lines(bim_path),
            "regions_tsv_path": str(regions_tsv),
            "regions_tsv_sha256": _sha256(regions_tsv),
            "ancestry": ancestry,
            "region_ids": sorted(scan_ids),
            "region_ids_selected": sorted(selected_set),
            "region_ids_out_of_scope": sorted(out_of_scope_ids),
            "n_rows_in_window_per_region": rows_in_window,
            "verdict_scope": VERDICT_SCOPE,
        },
        "pooled": {key: pooled[key] for key in POOLED_KEYS},
        "per_region": {
            rid: {key: block[key] for key in PER_REGION_KEYS}
            for rid, block in per_region.items()
        },
    }
    return all_out, summary


def write_out_tsv(out_rows, path: "str | Path") -> None:
    """Write the per-row verdict TSV. Header EQUALS :data:`OUT_COLUMNS`."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(OUT_COLUMNS) + "\n")
        for row in out_rows:
            fh.write("\t".join(_render(row[col]) for col in OUT_COLUMNS) + "\n")


# =========================================================================== #
# CLI                                                                         #
# =========================================================================== #

def _build_parser() -> argparse.ArgumentParser:
    """The argv contract, mirroring ``pairwise_completeness_scan.py:1343``.

    ⚠ THE NAME IS A DECLARED CROSS-TASK CONTRACT: the staged-invocation gate in
    ``.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md``
    feeds its STAGED argv to this exact function, so a staged typo fails at
    verify time on this node instead of inside the perimeter.
    """
    parser = argparse.ArgumentParser(
        prog="pcs_panelwide_reclassify",
        description=(
            "POST-HOC: for each UNDEFINED pair in an already-emitted "
            "pcs_pairs.tsv, does either member land on the PRODUCTION "
            "excludelist that detect_occluded_variants builds over EVERY "
            "deletion in the region window? Reads the pairs TSV, the region "
            "manifest and the cohort .bim ONLY. Decodes no genotype, computes "
            "no LD, changes no criterion, and cannot require the sweep to be "
            "re-run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pairs-tsv", dest="pairs_tsv", type=Path, required=True,
        help=(
            "an emitted pcs_pairs.tsv. Its header must EQUAL "
            "pairwise_completeness_scan.TSV_COLUMNS or the run stops."
        ),
    )
    parser.add_argument(
        "--bfile-prefix", dest="bfile_prefix", type=Path, required=True,
        help=(
            "plink1 bfile prefix. ONLY the prefix's own .bim is opened — this "
            "tool is coordinate-only and reads no genotypes at all."
        ),
    )
    parser.add_argument(
        "--regions-tsv", dest="regions_tsv", type=Path, required=True,
        help=(
            "a config/ld_regions.tsv-shaped manifest (1-based cols 1 region_id, "
            "2 chr, 7 ancestry, 15 window_start, 16 window_end). Keyed on "
            "(region_id x ancestry), so --ancestry selects as well as --region-ids."
        ),
    )
    parser.add_argument(
        "--ancestry", dest="ancestry", default=DEFAULT_ANCESTRY,
        help=(
            "which ancestry's windows to read (1-based column 7). Reading the "
            f"manifest BLIND returns every window twice. Default {DEFAULT_ANCESTRY}."
        ),
    )
    parser.add_argument(
        "--region-ids", dest="region_ids",
        help=(
            "comma-separated subset of --regions-tsv region ids. OMIT the flag "
            "to use every region; a value that names no id after stripping "
            "(e.g. ' , ') is an ERROR and exits 2, NOT a silent all-region run."
        ),
    )
    parser.add_argument(
        "--out", dest="out", type=Path, required=True,
        help="per-undefined-row verdict TSV output path",
    )
    parser.add_argument(
        "--summary", dest="summary", type=Path, required=True,
        help="summary JSON output path (provenance / pooled / per_region)",
    )
    parser.add_argument(
        "--tail-min-lost-frac", dest="tail_min_lost_frac", type=float,
        default=TAIL_MIN_CARRIERS_LOST_FRAC,
        help=(
            "the DEFINED-row tail boundary on max(del, partner) "
            "carriers_lost_frac. This REPRODUCES the pre-registered boundary "
            "already inside pairwise_completeness_scan.summarize (summary key "
            "n_defined_lost_frac_ge_0p9); it is NOT a policy threshold and no "
            "carrier floor is proposed anywhere by this tool. Changing it "
            "INVALIDATES the --pcs-summary reconciliation, which refuses to run "
            f"against a different boundary. Default {TAIL_MIN_CARRIERS_LOST_FRAC}."
        ),
    )
    parser.add_argument(
        "--pcs-summary", dest="pcs_summary", type=Path, default=None,
        help=(
            "OPTIONAL: the scanner's own emitted pcs_summary.json. When given, "
            "n_defined_lost_frac_ge_0p9 is summed over the SCANNED regions and "
            "must EQUAL this run's n_tail_rows_in, or the tool STOPS before "
            "writing. That closes the local tail predicate against the "
            "scanner's own measurement at runtime."
        ),
    )
    return parser


def main(argv: "list[str] | None" = None) -> int:
    """Run the reclassification. 0 on success, 2 on a bad or missing input.

    Every input is validated BEFORE either output file is opened, so a failure
    never leaves a partial artifact behind.
    """
    args = _build_parser().parse_args(argv)

    if args.region_ids is None:
        region_ids = None
    else:
        region_ids = [r.strip() for r in args.region_ids.split(",") if r.strip()]
        if not region_ids:
            print(
                f"ERROR: --region-ids was given but names no region id after "
                f"stripping: {args.region_ids!r}. OMIT the flag entirely to use "
                f"every region in --regions-tsv; an empty value is not the same "
                f"request.",
                file=sys.stderr,
            )
            return 2

    bim_path = Path(args.bfile_prefix).with_suffix(".bim")
    try:
        out_rows, summary = reclassify(
            args.pairs_tsv, bim_path, args.regions_tsv,
            ancestry=args.ancestry, region_ids=region_ids,
            tail_min_lost_frac=args.tail_min_lost_frac,
            pcs_summary=args.pcs_summary,
        )
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    write_out_tsv(out_rows, args.out)
    Path(args.summary).write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    pooled = summary["pooled"]
    print("=== PANEL-WIDE RECLASSIFICATION (POST-HOC; nothing was re-run) ===")
    for key in BANKED_POOLED_KEYS:
        print(f"{key}\t{pooled[key]}")
    print()
    print("VERDICT SCOPE: " + summary["provenance"]["verdict_scope"])
    print(
        "NOTE: these are COUNTS over the scanned regions. They are NOT a "
        "prevalence, and they REVISE no pre-registered number."
    )

    # THE SPLIT AND ITS CONDITION, TOGETHER. The scope sentence is printed
    # INSIDE this block, immediately under the header, so the pre/post numbers
    # cannot be read — or quoted — without it.
    print()
    print("=== THE TAIL: PRE-FILTER vs POST-FILTER ===")
    print("TAIL VERDICT SCOPE: " + TAIL_VERDICT_SCOPE)
    for key in (
        "tail_min_carriers_lost_frac",
        "n_tail_rows_in",
        "n_tail_rows_out_of_scope",
        "n_tail_distinct_pairs_in",
        "n_tail_rows_member_occluded_panelwide",
        "n_tail_rows_neither_member_occluded_panelwide",
        "n_tail_pairs_member_occluded_panelwide",
        "n_tail_pairs_neither_member_occluded_panelwide",
        "n_tail_regions_with_rows",
        "n_defined_rows_in",
        "n_defined_rows_out_of_scope",
        "n_defined_rows_member_occluded_panelwide",
        "n_defined_rows_reaching_matrix",
        "n_defined_rows_rarer_and_min_definitions_disagree",
    ):
        print(f"{key}\t{pooled[key]}")

    print()
    print("=== INFORMATIVE-CARRIER DISTRIBUTION (Seth's quantity) ===")
    for key in (
        "informative_carriers_percentiles_defined_rows",
        "informative_carriers_percentiles_defined_rows_reaching_matrix",
        "informative_carriers_low_tail_defined_rows",
        "informative_carriers_low_tail_defined_rows_reaching_matrix",
    ):
        print(f"{key}\t{json.dumps(pooled[key], sort_keys=True)}")
    print()
    print("NO FLOOR: " + NO_FLOOR_NOTICE)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
