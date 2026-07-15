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
# SETTLED REAL-WINDOW ORACLE — for the GATED real-`.bim` validation ONLY       #
# --------------------------------------------------------------------------- #
#
# The synthetic fixture above pins the RULE. The constants below pin the ANSWER
# the detector must reproduce when it is finally run against the REAL region-1
# window `.bim` inside the AoU perimeter (out of scope for this synthetic unit;
# no perimeter access this phase — see the gated stub at the bottom of the file).
#
# SETTLED (Seth 5/5 vs the geometry verdict `4543dcf4…`):
#   * occluded set                 = {10328, 44784, 46714, 59097, 66730}
#       These are 0-based .bim ROW INDICES, NOT bp positions and NOT window offsets.
#       RECONCILED 2026-07-15 (blast-radius HIGH): the prior comment mislabelled them
#       "window-relative offsets" and the gated assertion compared them against `_pos_of`
#       = absolute bp (`int(r[3])`). Region-1's variants span ~1.98M–8.38M bp, so that
#       comparison can NEVER hold for a correct detector — it would fail a good impl at
#       the gated run, inviting someone to weaken the one oracle that validates the
#       genome-wide panel. The scientific review fixes the space unambiguously as row
#       indices: `m3_nan_conditioning_scientific_review.md` — "pairs are index-adjacent
#       (10327/10328, 46713/46714/46715, …); one variant (46714) chains two pairs (a run
#       of co-located records)". Consecutive integers + "index-adjacent" + "co-located
#       records" describe .bim row ordering, not bp.
#   * 7-deletion REF-span inventory = 60/29/7/31/31/17/29 bp
#   * same-position variants        = 0  (`bcftools norm -m` fixes none)
# This gives the gated 276-region Nyquist check a CONCRETE expected answer.
#
# ⚠ ONE reconciliation item for the gated run (harmless while skipped): confirm the
# index ORIGIN (0- vs 1-based) against the real region-1 `.bim` header before trusting
# the equality — the source doc does not state the base explicitly. 0-based is assumed
# here (the natural `enumerate(rows)` index). If the real `.bim` shows 1-based, add 1.

#: 0-based .bim row indices of the occluded variants in the REAL region-1 window.
_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES: set[int] = {10328, 44784, 46714, 59097, 66730}
_REGION1_REAL_DELETION_REF_SPANS: list[int] = [60, 29, 7, 31, 31, 17, 29]
_REGION1_REAL_SAME_POSITION_COUNT: int = 0


# --------------------------------------------------------------------------- #
# 0. fixture self-checks (no impl needed — these guard the fixture geometry)   #
# --------------------------------------------------------------------------- #

def test_region1_fixture_encodes_the_settled_deletion_inventory():
    """The fixture's 7 deletions carry REF spans 60/29/7/31/31/17/29 bp — the
    SETTLED inventory. Guards the fixture itself against silent coordinate drift
    (T-m3-07a-02: a mis-encoded fixture would let a WRONG 07b impl pass)."""
    spans = [len(r[5]) for r in _REGION1_BIM_ROWS if len(r[5]) > 1]
    assert spans == _REGION1_DELETION_REF_SPANS
    assert spans == _REGION1_REAL_DELETION_REF_SPANS  # synthetic mirrors the real window
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
    """GATED: the SETTLED real-window oracle the detector must reproduce when run
    against the REAL region-1 window `.bim` inside the AoU perimeter.

    Occluded set {10328, 44784, 46714, 59097, 66730} as 0-based .bim ROW INDICES
    (NOT bp — see the constant's note); 7-deletion REF-span inventory
    60/29/7/31/31/17/29 bp; 0 same-position variants. NC-State has no perimeter
    access this phase, so the real `.bim` is absent and this SKIPS — it stands as
    the concrete expected answer for the gated 276-region check.
    """
    real_bim = PROJECT_ROOT / "data" / "aou" / "region1_window.bim"
    if not real_bim.exists():
        pytest.skip(
            "GATED real-`.bim` validation: no AoU perimeter access this phase "
            f"({real_bim} absent). SETTLED oracle held for the gated run — "
            f"occluded_row_indices={sorted(_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES)} "
            "(0-based; confirm origin vs the real .bim header), "
            f"ref_span_inventory={_REGION1_REAL_DELETION_REF_SPANS} bp, "
            f"same_position={_REGION1_REAL_SAME_POSITION_COUNT}."
        )

    import occlusion_span_filter as osf

    rows = osf.load_bim_rows(real_bim)
    occluded, _edges = osf.detect_occluded_variants(rows)
    # Compare in the CORRECT space: 0-based .bim row index of each occluded variant
    # (the oracle is index-adjacent row indices, not bp — see the constant's note).
    occluded_set = set(occluded)
    got_row_indices = {i for i, r in enumerate(rows) if r[1] in occluded_set}
    assert got_row_indices == _REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES
    spans = sorted(len(r[5]) for r in rows if len(r[5]) > 1)
    assert spans == sorted(_REGION1_REAL_DELETION_REF_SPANS)
