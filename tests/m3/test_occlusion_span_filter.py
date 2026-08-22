"""RED-first tests for src/python/occlusion_span_filter.py (m3-07a Wave 0, T1).

The SCIENCE these tests encode is SETTLED and byte-verified — do NOT re-derive it
here. Mechanism = overlapping-deletion occlusion
(``m3_region1_nan_geometry_verdict.md``, body anchor ``4543dcf4…``); policy =
exclude-in-lockstep + provenance, never zeroing
(``m3_panel_occlusion_policy_decision.md``, body anchor ``42d70167…``,
pre-registered on OSF ``osf.io/az52u`` 2026-07-10T13:32:22Z, recorded ``ac4c990``).

THE DETERMINISTIC OCCLUSION RULE (conservative; RESEARCH §2/§7)::

    V is OCCLUDED iff ∃ window variant D with len(REF_D) > 1 and
    POS_D < POS_V <= POS_D + len(REF_D) − 1        (computed over the ORIGINAL window)

Insertions and SNVs never occlude (the footprint is defined by ``len(REF)`` ONLY).
The occluded downstream variant V is EXCLUDED; the occluding deletion D is kept.

``.bim`` allele convention (``plink_ld_to_npz.load_bim``, FROZEN): columns are
``[chr, snp_id, cm, bp, A1, A2]`` with **A1 = ALT** (col 5) and **A2 = REF**
(col 6); canonical vid = ``{chr}:{bp}:{A2}:{A1}`` = ``chr:pos:REF:ALT``. A deletion
therefore carries a MULTI-CHAR A2/REF whose length IS its reference footprint.

RED-for-the-right-reason: ``occlusion_span_filter`` does not exist yet (07b builds
it). It is imported INSIDE each test body, NOT at module top, so pytest COLLECTS
this file cleanly and every test fails as a test/assert failure
(``ModuleNotFoundError`` raised at call-time) rather than as a collection error.

NOTE: Seth's full detector prototype exists as a READ-ONLY reference for the
executor — it is deliberately NOT committed. 07b must build the detector test-first
against the real ``.bim`` loader rather than importing that prototype.

Runs in smoke_dev py3.11 (stdlib only for the pure rule). No Hail.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import occlusion_span_filter`` — see the docstring.


# --------------------------------------------------------------------------- #
# .bim row helpers (mirror tests/m3/test_run_native_ld_panel.py:48-61)        #
# --------------------------------------------------------------------------- #

def _ref_seq(n: int, anchor: str = "G") -> str:
    """A deterministic n-char REF string, left-anchored on ``anchor``.

    A left-anchored VCF deletion has REF = <anchor><deleted bases…> and ALT =
    <anchor>, so REF[0] == ALT and len(REF) == the reference footprint length.
    """
    filler = "ACGT" * ((n // 4) + 1)
    return (anchor + filler)[:n]


def _del_row(bp: int, ref_len: int, chrom: int = 1) -> tuple:
    """A DELETION .bim row whose REF (A2) spans exactly ``ref_len`` bases.

    Reference footprint = [bp, bp + ref_len − 1].
    """
    assert ref_len > 1, "a deletion must have len(REF) > 1"
    ref = _ref_seq(ref_len)
    alt = ref[0]  # left-anchored: ALT is the single anchor base
    return (chrom, f"{chrom}:{bp}:{ref}:{alt}", 0, bp, alt, ref)


def _snp_row(bp: int, ref: str = "A", alt: str = "A", chrom: int = 1) -> tuple:
    """A len(REF)==1 .bim row (never an occluder).

    The region-1 fixture table pins A1=A / A2=A for its SNP rows. The occlusion
    rule keys ONLY on ``len(REF)``, so the allele identity is immaterial to the
    geometry — these values are reproduced verbatim from the settled fixture spec
    rather than "corrected" to a biologically distinct REF/ALT pair.
    """
    return (chrom, f"{chrom}:{bp}:{ref}:{alt}", 0, bp, alt, ref)


def _ins_row(bp: int, ins_len: int, chrom: int = 1) -> tuple:
    """An INSERTION row: len(ALT) > len(REF), REF = a single anchor base.

    Its reference footprint is the single anchor base, so it NEVER occludes.
    """
    ref = "G"
    alt = _ref_seq(ins_len + 1)
    return (chrom, f"{chrom}:{bp}:{ref}:{alt}", 0, bp, alt, ref)


def _vid(bp: int, rows: list[tuple] | None = None) -> str:
    """The col-2 variant id of the fixture row at ``bp``."""
    rows = _REGION1_BIM_ROWS if rows is None else rows
    hits = [r[1] for r in rows if int(r[3]) == bp]
    assert len(hits) == 1, f"expected exactly one row at bp={bp}, got {len(hits)}"
    return hits[0]


def _pos_of(vid: str, rows: list[tuple] | None = None) -> int:
    rows = _REGION1_BIM_ROWS if rows is None else rows
    hits = [int(r[3]) for r in rows if r[1] == vid]
    assert len(hits) == 1, f"expected exactly one row with id={vid}"
    return hits[0]


# --------------------------------------------------------------------------- #
# The region-1 `.bim` fixture (RESEARCH §5; geometry verdict `4543dcf4…`)      #
# --------------------------------------------------------------------------- #
#
# | bp      | role | A1 (ALT) | len(A2/REF) | outcome                          |
# |---------|------|----------|-------------|----------------------------------|
# | 1980423 | del1 | G        | 60          | occluder                         |
# | 1980475 | snpA | A        | 1           | OCCLUDED (by del1)               |
# | 5733474 | del2 | G        | 29          | occluder                         |
# | 5733487 | snpB | A        | 1           | OCCLUDED (by del2)               |
# | 5922716 | del3 | G        | 7           | occluder  ── pair-4 tangle       |
# | 5922718 | snpC | A        | 1           | OCCLUDED (by UPSTREAM del3)      |
# | 5922724 | del4 | G        | 31          | occluder, occludes nothing here  |
# | 7492679 | del5 | G        | 31          | occluder                         |
# | 7492693 | del6 | G        | 17          | OCCLUDED (by del5) — a DELETION  |
# | 8375794 | del7 | G        | 29          | occluder                         |
# | 8375822 | snpD | A        | 1           | OCCLUDED (by del7) — BOUNDARY    |
#
# del7's footprint ENDS at 8375794 + 29 − 1 == 8375822 == snpD, so snpD is the
# last-covered-base boundary case living inside the real fixture.

_REGION1_BIM_ROWS: list[tuple] = [
    _del_row(1_980_423, 60),   # del1
    _snp_row(1_980_475),       # snpA — occluded
    _del_row(5_733_474, 29),   # del2
    _snp_row(5_733_487),       # snpB — occluded
    _del_row(5_922_716, 7),    # del3
    _snp_row(5_922_718),       # snpC — occluded by the UPSTREAM del3
    _del_row(5_922_724, 31),   # del4 — downstream of snpC; occludes nothing
    _del_row(7_492_679, 31),   # del5
    _del_row(7_492_693, 17),   # del6 — occluded (a deletion CAN be occluded)
    _del_row(8_375_794, 29),   # del7
    _snp_row(8_375_822),       # snpD — occluded, boundary (== last covered base)
]

#: The SETTLED expected occluded set for the SYNTHETIC region-1 fixture (5 ids;
#: the 5922716/5922718/5922724 tangle collapses to the single 5922718 drop).
_REGION1_EXPECTED_OCCLUDED_POS: set[int] = {
    1_980_475, 5_733_487, 5_922_718, 7_492_693, 8_375_822,
}

#: The 7-deletion REF-span inventory (bp), in ascending-position order.
_REGION1_DELETION_REF_SPANS: list[int] = [60, 29, 7, 31, 31, 17, 29]

# --------------------------------------------------------------------------- #
# REGION-1 REAL-WINDOW ORACLE — TWO LAYERS, DELIBERATELY KEPT APART            #
# --------------------------------------------------------------------------- #
#
# The synthetic fixture above pins the RULE. Everything below concerns the REAL
# region-1 window `.bim` inside the AoU perimeter, and it comes in two kinds that
# were conflated once already, at cost (re-derived 2026-08-19/21, see
# .planning/debug/fire-morning-occlusion-oracle-vs-geometry.md):
#
# ── LAYER 1 — DERIVED. Assert CONTAINMENT, never equality. ──────────────────
#
#   * the SETTLED-5 occluded variants, at 0-based .bim ROW INDICES
#         {10328, 44784, 46714, 59097, 66730}
#     NOT bp positions and NOT window offsets. RECONCILED 2026-07-15
#     (blast-radius HIGH): the prior comment mislabelled them "window-relative
#     offsets" and the gated assertion compared them against absolute bp
#     (`int(r[3])`). Region-1's variants span ~1.98M–8.38M bp, so that comparison
#     can NEVER hold for a correct detector. The scientific review fixes the space
#     unambiguously as row indices: `m3_nan_conditioning_scientific_review.md` —
#     "pairs are index-adjacent (10327/10328, 46713/46714/46715, …); one variant
#     (46714) chains two pairs (a run of co-located records)". Consecutive integers
#     + "index-adjacent" + "co-located records" describe .bim row ordering, not bp.
#   * the 7 deletion REF spans implicated in those 6 June-2026 NaN pairs:
#         60/29/7/31/31/17/29 bp
#
#   WHY CONTAINMENT REPLACED EQUALITY (2026-08-21). Probe 2 (2026-08-19,
#   in-perimeter) ran the FROZEN detector over the real window and measured 231
#   occluded variants with the settled 5 a strict SUBSET
#   (`oracle_subset_of_observed: True`, `oracle_missing_from_observed: []`) —
#   nothing missing, no index shift — over 7,951 multi-base-REF rows with a max
#   span of 170 bp. The two `==` assertions were therefore FALSE ABOUT THE WINDOW
#   while being TRUE ABOUT THE FORENSICS: the 5 and the 7 were the NaN-pair
#   forensics' scope, and the scope was lost in transcription. Containment asserts
#   exactly what was established — the detector must still reproduce every settled
#   finding — and asserts nothing the evidence does not support.
#
#   NOT IN SCOPE, AND DELIBERATELY NOT ASSERTED: the index->bp mapping of the five
#   indices, and the five attribution EDGES (which deletion occludes which
#   variant). Neither has been directly observed. Asserting either would
#   manufacture an oracle out of an inference.
#
# ── LAYER 2 — MEASURED. Substrate totals, in their own gated test. ──────────
#
#   The window's totals (rows, deletion rows, occluded rows/sites, max span, site
#   count) are MEASUREMENTS OF A DATA SUBSTRATE, not derived science. They live in
#   `test_region1_real_window_substrate_totals_MEASURED_NOT_DERIVED` below, kept
#   physically apart so that a CDR refresh moving them cannot take the derived
#   science down with it — and so that nobody mistakes a measurement for a
#   conclusion twice.

#: LAYER 1 (DERIVED). 0-based .bim ROW INDICES of the SETTLED-5 occluded variants.
#: The real window contains MANY more; assert CONTAINMENT, never equality.
_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES: set[int] = {10328, 44784, 46714, 59097, 66730}

#: LAYER 1 (DERIVED). The 7 deletion REF spans implicated in the 6 NaN pairs. This
#: is NOT a window inventory — the real window carries 7,951 multi-base-REF rows
#: with a max span of 170 bp — it is a MULTISET that must be PRESENT in the window.
_REGION1_SETTLED_DELETION_REF_SPANS: list[int] = [60, 29, 7, 31, 31, 17, 29]

#: LAYER 1 (DERIVED), RE-SCOPED 2026-08-21. The June-2026 forensics found ZERO
#: same-position variants AMONG THE 6 NaN PAIRS. That scope was lost at HOP 2 and
#: the number went on to read as a window-wide claim, which is FALSE (the real
#: window's occluded set includes consecutive-index runs of co-located records).
#: The name now carries the scope, and it is never asserted window-wide.
_REGION1_NAN_PAIRS_SAME_POSITION_COUNT: int = 0

#: LAYER 2 (MEASURED, NOT DERIVED). See the gated test of the same name below for
#: the provenance and the re-measure rule; the dict lives here only so the Layer-1
#: skip message can stay short.
_REGION1_MEASURED_SUBSTRATE: dict[str, int] = {
    "n_rows": 102421,
    "n_deletion_rows": 7951,
    "n_occluded_rows": 231,
    "max_span": 170,
    "n_sites": 96708,
    "occ_sites": 196,
}


# --------------------------------------------------------------------------- #
# 0. fixture self-checks (no impl needed — these guard the fixture geometry)   #
# --------------------------------------------------------------------------- #

def test_region1_fixture_encodes_the_settled_deletion_inventory():
    """The fixture's 7 deletions carry REF spans 60/29/7/31/31/17/29 bp — the
    SETTLED inventory. Guards the fixture itself against silent coordinate drift
    (T-m3-07a-02: a mis-encoded fixture would let a WRONG 07b impl pass)."""
    spans = [len(r[5]) for r in _REGION1_BIM_ROWS if len(r[5]) > 1]
    assert spans == _REGION1_DELETION_REF_SPANS
    # The synthetic mirrors the RULE and the 7 SETTLED spans — NOT the real
    # window's inventory (that is 7,951 multi-base-REF rows, max span 170 bp).
    assert spans == _REGION1_SETTLED_DELETION_REF_SPANS
    assert len(spans) == 7


def test_region1_fixture_row_shape_matches_bim_convention():
    """Every fixture row is a 6-tuple (chr, snp_id, cm, bp, A1=ALT, A2=REF) whose
    col-2 id is the production canonical vid chr:pos:REF:ALT (== chr:bp:A2:A1)."""
    for r in _REGION1_BIM_ROWS:
        chrom, vid, cm, bp, a1, a2 = r
        assert len(r) == 6
        assert cm == 0
        assert vid == f"{chrom}:{bp}:{a2}:{a1}"   # chr:pos:REF:ALT
    assert len({r[1] for r in _REGION1_BIM_ROWS}) == len(_REGION1_BIM_ROWS)  # unique ids
    assert [int(r[3]) for r in _REGION1_BIM_ROWS] == sorted(
        int(r[3]) for r in _REGION1_BIM_ROWS
    )


# --------------------------------------------------------------------------- #
# 1. the region-1 fixture -> EXACTLY the 5 settled occluded ids                #
# --------------------------------------------------------------------------- #

def test_region1_fixture_returns_exactly_five_occluded():
    """The headline known-answer: detect_occluded_variants over the region-1
    window returns EXACTLY {snpA, snpB, snpC, del6, snpD}."""
    import occlusion_span_filter as osf

    occluded, _edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)

    assert set(occluded) == {_vid(bp) for bp in _REGION1_EXPECTED_OCCLUDED_POS}
    assert {_pos_of(v) for v in occluded} == _REGION1_EXPECTED_OCCLUDED_POS
    assert len(set(occluded)) == 5
    # the occluding deletions themselves are KEPT (exclude the downstream V only)
    for keeper_bp in (1_980_423, 5_733_474, 5_922_716, 5_922_724, 7_492_679, 8_375_794):
        assert _vid(keeper_bp) not in set(occluded)


def test_region1_tangle_collapses_to_a_single_drop():
    """The 3-record 5922716/5922718/5922724 tangle collapses with the SINGLE
    5922718 drop: neither deletion is excluded."""
    import occlusion_span_filter as osf

    occluded, _edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)
    tangle = {_vid(5_922_716), _vid(5_922_718), _vid(5_922_724)}
    assert tangle & set(occluded) == {_vid(5_922_718)}


# --------------------------------------------------------------------------- #
# 2. pair-4 second-order attribution (SETTLED — Seth 5/5 vs `4543dcf4…`)       #
# --------------------------------------------------------------------------- #

def test_pair4_snp_attributed_to_upstream_deletion_not_downstream():
    """SETTLED: SNP 5922718 is occluded by the UPSTREAM DEL 5922716 (whose 7 bp
    REF span covers it), NOT by the downstream DEL 5922724. The detector must
    ATTRIBUTE the occlusion to 5922716 — the manifest's ref_span / occluder
    columns are derived from that attribution, so getting it backwards would
    publish a wrong provenance record."""
    import occlusion_span_filter as osf

    occluded, edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)
    snp_c, del_up, del_down = _vid(5_922_718), _vid(5_922_716), _vid(5_922_724)

    assert snp_c in set(occluded)
    edge_set = set(edges)
    assert (del_up, snp_c) in edge_set        # attributed UPSTREAM
    assert (del_down, snp_c) not in edge_set  # NOT the downstream deletion

    # exactly one occluder is attributed to snpC in this window
    occluders_of_c = {o for (o, v) in edge_set if v == snp_c}
    assert occluders_of_c == {del_up}


def test_pair4_downstream_deletion_is_disjoint_second_order():
    """The 5922718 <-> 5922724 pair is DISJOINT (second-order): del4 starts at
    5922724, strictly DOWNSTREAM of snpC at 5922718, so it occludes neither snpC
    nor anything else in the window — it contributes NO new edge."""
    import occlusion_span_filter as osf

    occluded, edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)
    del_down = _vid(5_922_724)

    assert del_down not in set(occluded)                       # not itself occluded
    assert not [v for (o, v) in set(edges) if o == del_down]   # occludes nothing
    # del3's footprint stops at 5922716 + 7 − 1 == 5922722, short of 5922724
    assert 5_922_716 + 7 - 1 == 5_922_722 < 5_922_724


# --------------------------------------------------------------------------- #
# 3. edges record occluder -> occluded                                         #
# --------------------------------------------------------------------------- #

def test_edges_record_occluder_to_occluded():
    """``edges`` is a sequence of (occluder_id, occluded_id) pairs covering every
    occluded variant, with each occluder a real deletion (len(REF) > 1)."""
    import occlusion_span_filter as osf

    occluded, edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)
    edge_set = set(edges)

    assert {v for (_o, v) in edge_set} == set(occluded)  # every drop is explained
    expected = {
        (_vid(1_980_423), _vid(1_980_475)),
        (_vid(5_733_474), _vid(5_733_487)),
        (_vid(5_922_716), _vid(5_922_718)),
        (_vid(7_492_679), _vid(7_492_693)),
        (_vid(8_375_794), _vid(8_375_822)),
    }
    assert edge_set == expected

    # every occluder is a real deletion (len(REF) > 1) lying strictly upstream
    ref_len_by_id = {r[1]: len(r[5]) for r in _REGION1_BIM_ROWS}
    for occluder, occluded_id in edge_set:
        assert ref_len_by_id[occluder] > 1
        assert _pos_of(occluder) < _pos_of(occluded_id)


# --------------------------------------------------------------------------- #
# 4. unit cases                                                                #
# --------------------------------------------------------------------------- #

def test_no_deletion_window_returns_empty():
    """A window with NO deletion (all len(REF)==1) occludes nothing."""
    import occlusion_span_filter as osf

    rows = [_snp_row(1_000), _snp_row(1_001), _snp_row(2_000)]
    occluded, edges = osf.detect_occluded_variants(rows)
    assert list(occluded) == []
    assert list(edges) == []


def test_single_deletion_occludes_downstream_snp():
    """One 10 bp deletion at 1000 (footprint [1000, 1009]) occludes the SNP at
    1005 and only that SNP."""
    import occlusion_span_filter as osf

    d = _del_row(1_000, 10)
    v = _snp_row(1_005)
    far = _snp_row(9_999)
    rows = [d, v, far]
    occluded, edges = osf.detect_occluded_variants(rows)
    assert set(occluded) == {v[1]}
    assert set(edges) == {(d[1], v[1])}


def test_snp_upstream_of_deletion_not_occluded():
    """A SNP strictly UPSTREAM of a deletion is disjoint — the footprint extends
    downstream only (POS_D < POS_V is strict)."""
    import occlusion_span_filter as osf

    up = _snp_row(999)
    d = _del_row(1_000, 10)
    rows = [up, d]
    occluded, edges = osf.detect_occluded_variants(rows)
    assert list(occluded) == []
    assert list(edges) == []


def test_off_by_one_boundary_last_covered_base_occluded():
    """Boundary: with D at POS=1000, len(REF)=10 -> footprint [1000, 1009].
    POS_V == 1009 (== POS_D + len(REF) − 1) IS occluded;
    POS_V == 1010 (== POS_D + len(REF))      is NOT;
    POS_V == 1000 (== POS_D, the deletion itself) is NOT (strict POS_D < POS_V).
    """
    import occlusion_span_filter as osf

    d = _del_row(1_000, 10)
    last_covered = _snp_row(1_009)
    first_uncovered = _snp_row(1_010)
    rows = [d, last_covered, first_uncovered]

    occluded, _edges = osf.detect_occluded_variants(rows)
    assert last_covered[1] in set(occluded)
    assert first_uncovered[1] not in set(occluded)
    assert d[1] not in set(occluded)  # a deletion never occludes itself


def test_snv_never_occludes():
    """An SNV (len(REF) == 1) is never an occluder, even for the immediately
    adjacent base."""
    import occlusion_span_filter as osf

    snv = _snp_row(1_000, ref="A", alt="T")
    nxt = _snp_row(1_001)
    occluded, edges = osf.detect_occluded_variants([snv, nxt])
    assert list(occluded) == []
    assert list(edges) == []


def test_insertion_never_occludes_downstream_base():
    """An INSERTION (len(ALT) > len(REF), REF = single anchor base) has a
    single-base footprint and never occludes a downstream variant — the footprint
    is defined by len(REF) ONLY (RESEARCH §7 decision 2)."""
    import occlusion_span_filter as osf

    ins = _ins_row(1_000, ins_len=20)   # REF="G" (len 1), ALT 21 bp
    assert len(ins[5]) == 1 and len(ins[4]) > len(ins[5])
    downstream = _snp_row(1_001)
    far = _snp_row(1_015)

    occluded, edges = osf.detect_occluded_variants([ins, downstream, far])
    assert list(occluded) == []
    assert list(edges) == []


def test_deletion_can_itself_be_occluded():
    """A DELETION whose POS falls inside a LARGER upstream deletion's footprint is
    itself occluded (region-1's del6 at 7492693 inside del5's [7492679, 7492709])
    — the rule keys on POS_V, regardless of V's own len(REF)."""
    import occlusion_span_filter as osf

    occluded, edges = osf.detect_occluded_variants(_REGION1_BIM_ROWS)
    del5, del6 = _vid(7_492_679), _vid(7_492_693)
    assert del6 in set(occluded)
    assert (del5, del6) in set(edges)
    assert 7_492_679 + 31 - 1 == 7_492_709 >= 7_492_693


def test_rule_computed_over_the_original_window_not_iteratively():
    """CONSERVATIVE rule (RESEARCH §7 decision 1): occlusion is computed over the
    ORIGINAL window, so a chain D1 ⊃ D2 ⊃ V3 drops BOTH D2 and V3 — V3 is NOT
    rescued by D2 having been dropped. Over-exclusion here is deliberate and is
    audited variant-by-variant in the provenance manifest."""
    import occlusion_span_filter as osf

    d1 = _del_row(1_000, 100)   # footprint [1000, 1099]
    d2 = _del_row(1_010, 20)    # footprint [1010, 1029]; itself inside d1
    v3 = _snp_row(1_015)        # inside BOTH
    occluded, _edges = osf.detect_occluded_variants([d1, d2, v3])

    assert set(occluded) == {d2[1], v3[1]}
    assert d1[1] not in set(occluded)


def test_doubly_occluded_variant_appears_exactly_once():
    """A variant covered by TWO deletions must appear EXACTLY ONCE in ``occluded``
    (blast-radius MEDIUM 2026-07-15). The region-1 fixture has at most one occluder
    per occluded variant, so its ``set(occluded) == {...}`` assertions cannot catch a
    naive per-edge-append impl that emits a doubly-covered variant TWICE — the
    surrounding `set()` silently swallows the duplicate. A genome-wide window WILL
    have nested deletions, and a duplicated drop double-counts the Angle-1/3 catalog
    and can double-drop in lockstep. Pin the LIST (not the set) to length-unique."""
    import occlusion_span_filter as osf

    d1 = _del_row(1_000, 100)   # footprint [1000, 1099]
    d2 = _del_row(1_010, 20)    # footprint [1010, 1029]; itself inside d1
    v3 = _snp_row(1_015)        # inside BOTH d1 and d2
    occluded, edges = osf.detect_occluded_variants([d1, d2, v3])

    occ_list = list(occluded)
    assert len(occ_list) == len(set(occ_list)), f"duplicate drop(s): {occ_list}"
    assert occ_list.count(v3[1]) == 1
    # the manifest attributes ONE occluder per variant, so the detector must expose a
    # deterministic single attribution for v3 (which specific deletion is the
    # manifest tie-break decision, pinned in test_occlusion_manifest.py); here we only
    # require that v3's attribution is SOME real covering deletion, chosen deterministically.
    v3_occluders = {o for (o, v) in set(edges) if v == v3[1]}
    assert v3_occluders <= {d1[1], d2[1]} and len(v3_occluders) >= 1
    again, _ = osf.detect_occluded_variants([d1, d2, v3])
    assert list(again) == occ_list  # deterministic across calls


def test_distinct_variant_at_the_deletion_position_is_not_occluded():
    """Strict-left boundary against a DISTINCT co-located variant (blast-radius
    MEDIUM 2026-07-15). The rule is ``POS_D < POS_V`` (STRICT on the left), so a
    variant sharing the deletion's POS is NOT occluded — it is a co-located
    representation (handled upstream by `bcftools norm -m`), not an occlusion drop
    (RESEARCH §7 decision 2; verdict "0 same-position"). Region-1 has 0 same-position
    rows and `_vid` forbids them, so the existing self-occlusion check (`D not in
    occluded`) is passed by any `if V is D: continue` impl REGARDLESS of `<` vs `<=`
    on the left. Hail `split_multi` DOES emit same-position rows genome-wide, so an
    impl using `POS_D <= POS_V` would over-drop the multiallelic partner. This is the
    only test that distinguishes `<` from `<=` on the left."""
    import occlusion_span_filter as osf

    d = _del_row(1_000, 10)                       # footprint [1000, 1009]
    # a DISTINCT variant at the SAME position (different ref/alt -> different vid)
    same_pos = _snp_row(1_000, ref="C", alt="T")
    assert same_pos[1] != d[1] and int(same_pos[3]) == int(d[3])
    downstream = _snp_row(1_005)                  # genuinely inside -> the positive control

    occluded, _edges = osf.detect_occluded_variants([d, same_pos, downstream])
    occ = set(occluded)
    assert same_pos[1] not in occ                 # strict POS_D < POS_V: co-located, NOT occluded
    assert d[1] not in occ                         # the deletion itself
    assert downstream[1] in occ                    # positive control: a real downstream drop


# --------------------------------------------------------------------------- #
# 5. GATED real-`.bim` known-answer stub (out of scope for the synthetic unit) #
# --------------------------------------------------------------------------- #

def test_region1_real_window_known_answer_gated():
    """GATED — LAYER 1 (DERIVED): the SETTLED findings the frozen detector must
    still reproduce against the REAL region-1 window `.bim` in the AoU perimeter.

    CONTAINMENT on both halves, never equality (see the LAYER 1 block above): the
    settled-5 row indices must all be PRESENT among the detected occluded rows, and
    the 7 settled REF spans must all be PRESENT in the window's span multiset. The
    window legitimately carries far more of both — 231 occluded rows over 7,951
    multi-base-REF rows, measured 2026-08-19 — and an equality here was false about
    the window while true only about the June-2026 NaN-pair forensics.

    NC-State has no perimeter access this phase, so the real `.bim` is absent and
    this SKIPS. `test_containment_assertions_discriminate_a_wrong_answer` below is
    its unconditional negative control.
    """
    real_bim = PROJECT_ROOT / "data" / "aou" / "region1_window.bim"
    if not real_bim.exists():
        pytest.skip(
            "GATED real-`.bim` validation: no AoU perimeter access this phase "
            f"({real_bim} absent). LAYER 1 (DERIVED) held for the gated run, as "
            "CONTAINMENT — settled occluded_row_indices="
            f"{sorted(_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES)} (0-based) must be "
            "PRESENT among the detected rows, and settled ref_spans="
            f"{_REGION1_SETTLED_DELETION_REF_SPANS} bp must be PRESENT in the "
            "window multiset. Same-position count "
            f"{_REGION1_NAN_PAIRS_SAME_POSITION_COUNT} is scoped to the 6 NaN pairs "
            "ONLY and is deliberately NOT asserted window-wide."
        )

    from collections import Counter

    import occlusion_span_filter as osf

    rows = osf.load_bim_rows(real_bim)
    occluded, _edges = osf.detect_occluded_variants(rows)
    # Compare in the CORRECT space: 0-based .bim row index of each occluded variant
    # (the oracle is index-adjacent row indices, not bp — see the constant's note).
    occluded_set = set(occluded)
    got_row_indices = {i for i, r in enumerate(rows) if r[1] in occluded_set}
    assert got_row_indices, "the frozen detector returned an EMPTY occluded set"
    missing = _REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES - got_row_indices
    assert not missing, (
        f"the SETTLED-5 occluded row indices are no longer all present: missing "
        f"{sorted(missing)}. The frozen detector and the June-2026 forensics "
        f"disagree — REPORT AND DIAGNOSE; never widen this assertion to make it "
        f"pass.")

    window_spans = [len(r[5]) for r in rows if len(r[5]) > 1]
    have = Counter(window_spans)
    want = Counter(_REGION1_SETTLED_DELETION_REF_SPANS)
    # Multiset containment, written as the explicit per-key form rather than
    # `want <= have`. PORTABILITY: Counter.__le__ means multiset containment only on
    # Python 3.10+, and raises TypeError on 3.9. This test RUNS (does not skip)
    # inside the AoU perimeter, where a TypeError would read as a detector failure.
    short = {span: (n, have[span]) for span, n in want.items() if have[span] < n}
    assert not short, (
        f"the 7 settled REF spans are not all present in the window: {short} "
        f"(span -> (settled_count, observed_count))")


def test_containment_assertions_discriminate_a_wrong_answer():
    """CONTROL for the two gated LAYER-1 assertions above.

    Containment is WEAKER than the equality it replaced, so it has to be shown able
    to fail before it can be trusted — and the gated test that uses it SKIPS
    outside the perimeter, so it can never demonstrate that itself. This runs the
    SAME two assertion shapes over deliberately wrong inputs and asserts they
    detect the defect."""
    from collections import Counter

    # (a) a detector that lost three of the settled five
    got = {10328, 44784}
    missing = _REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES - got
    assert missing == {46714, 59097, 66730}, missing   # -> the gated assert FAILS

    # (b) a window one 31-bp span short of the settled multiset
    have = Counter([60, 29, 7, 31, 17, 29, 170, 4, 4])
    want = Counter(_REGION1_SETTLED_DELETION_REF_SPANS)
    short = {span: (n, have[span]) for span, n in want.items() if have[span] < n}
    assert short == {31: (2, 1)}, short                # -> the gated assert FAILS

    # and the same shapes are SILENT on a superset (the real-window case)
    superset = _REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES | {1, 2, 3}
    assert not (_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES - superset)
    rich = Counter(_REGION1_SETTLED_DELETION_REF_SPANS + [170] * 7944)
    assert not {s: n for s, n in want.items() if rich[s] < n}


def test_region1_real_window_substrate_totals_MEASURED_NOT_DERIVED():
    """GATED — LAYER 2: MEASURED_NOT_DERIVED substrate totals of the real region-1
    window.

    THESE ARE MEASUREMENTS, NOT DERIVED SCIENCE. Nothing here was reasoned to; every
    number was read off the substrate:

      n_rows=102421, n_deletion_rows=7951, n_occluded_rows=231, max_span=170,
      n_sites=96708, occ_sites=196

    PROVENANCE. Probe 2, 2026-08-19, in-perimeter, read-only, mirroring this test's
    own loading (`osf.load_bim_rows` + `detect_occluded_variants`) over
    `data/aou/region1_window.bim` — the `awk '($1=="1"||$1=="chr1") && $4>=10000 &&
    $4<=13506933'` window of `/home/jupyter/afr_cohort.bim`. The site-basis pair
    (n_sites, occ_sites) came from PENDING PASTE #3, 2026-08-20, the ruled
    site-basis sweep on VM 20260626b. Both banked verbatim at
    `.planning/debug/260820-site-basis-sweep-results-as-received.md` and
    `.planning/debug/fire-morning-occlusion-oracle-vs-geometry.md`.

    THE RULE WHEN THIS BREAKS: RE-MEASURE AND RECORD, never edit-to-green. A CDR
    refresh WILL move these numbers, and that is precisely the event this test
    exists to surface — the substrate changed, so the recorded measurement must be
    retaken and re-banked with its own provenance, and every consumer of it (the
    runbooks' region-1 EXPECT, the amendment's Class-M slots) re-checked. Editing a
    number here to restore green would silently re-create the exact defect this
    batch repaired.

    It is kept SEPARATE from the LAYER-1 derived test on purpose: substrate drift
    must not be able to take the derived science down with it.

    SKIPS on the same `data/aou/region1_window.bim` gate as LAYER 1 (no NC-State
    perimeter access), which is why it adds exactly one skip to the tests/m3 count.
    """
    real_bim = PROJECT_ROOT / "data" / "aou" / "region1_window.bim"
    if not real_bim.exists():
        pytest.skip(
            "GATED MEASURED_NOT_DERIVED substrate totals: no AoU perimeter access "
            f"this phase ({real_bim} absent). Held for the gated run — "
            f"{_REGION1_MEASURED_SUBSTRATE} (probe 2, 2026-08-19; site basis from "
            "PENDING PASTE #3, 2026-08-20). On a break: RE-MEASURE AND RECORD, "
            "never edit-to-green."
        )

    import occlusion_span_filter as osf

    rows = osf.load_bim_rows(real_bim)
    occluded, _edges = osf.detect_occluded_variants(rows)
    occluded_set = set(occluded)
    deletion_spans = [len(r[5]) for r in rows if len(r[5]) > 1]
    got = {
        "n_rows": len(rows),
        "n_deletion_rows": len(deletion_spans),
        "n_occluded_rows": len(occluded_set),
        "max_span": max(deletion_spans) if deletion_spans else 0,
        "n_sites": len({(r[0], r[3]) for r in rows}),
        "occ_sites": len({(r[0], r[3]) for r in rows if r[1] in occluded_set}),
    }
    assert got == _REGION1_MEASURED_SUBSTRATE, (
        f"the measured substrate moved: {got} vs recorded "
        f"{_REGION1_MEASURED_SUBSTRATE}. RE-MEASURE AND RECORD (with fresh "
        f"provenance), and re-check every consumer of these numbers — the runbooks' "
        f"region-1 EXPECT and the posted amendment's Class-M slots. NEVER edit a "
        f"number here to restore green.")
