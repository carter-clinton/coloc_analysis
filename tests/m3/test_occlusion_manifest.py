"""RED-first tests for src/python/occlusion_manifest.py (m3-07a Wave 0, T2).

The provenance manifest is the OTHER half of the pre-registered policy: a variant
excluded because an overlapping deletion's REF span makes its LD structurally
undefined is dropped in LOCKSTEP from the LD panel AND the harmonized sumstats,
and EVERY drop is auditable. That auditability is what the OSF amendment-update
(osf.io/az52u, POSTED 2026-07-10T13:32:22Z, recorded ``ac4c990``) pre-registers —
so a missing/incorrect manifest column is a pre-registration failure, not a nit.

Stage A (in-perimeter, egress-safe): pure variant-metadata / coordinate geometry —
no genotypes, no per-person counts (REQ-AOU-LD-EGRESS).
Stage B (NC-State): liftover to GRCh37 + traits-present enrichment.

RED-for-the-right-reason: ``occlusion_manifest`` does not exist yet (07b/07c build
it). It is imported INSIDE each test body so pytest COLLECTS cleanly and each test
fails as a test/assert failure, NOT a collection error.

LIFTOVER: GRCh38 -> GRCh37 via the hg38ToHg19 chain, reusing the exact
``ld_npz_to_rds.R:167-183`` recipe (pyliftover; ``convert_coordinate("chr"+chr,
pos-1)`` 0-based in, ``+1`` out). NOTE: this deliberately does NOT use conftest's
``chain_fixture`` — that fixture points at ``hg19ToHg38.over.chain.gz``, which is
the WRONG DIRECTION for this test (and is not present, so it would always skip).

Runs in smoke_dev py3.11 (numpy/pandas + pyliftover). No Hail.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import occlusion_manifest`` — see the docstring.

#: The ONLY chain present in-repo, and the correct DIRECTION (GRCh38 -> GRCh37).
_HG38_TO_HG19_CHAIN = (
    PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"
)

#: Settled hinge-check anchors [m3_region1_occlusion_hinge_check.md:40-48,124-133]
_LIFTOVER_ANCHORS: dict[int, int] = {
    5_922_716: 5_982_776,   # del3 (the occluder)
    5_922_718: 5_982_778,   # snpC (the occluded variant)
    5_922_724: 5_982_784,   # del4 (the disjoint downstream deletion)
}

#: Stage-A columns every occluded-variant record MUST carry.
_STAGE_A_COLUMNS = [
    "region_id",
    "chr",
    "variant_id",
    "pos_grch38",
    "ref",
    "alt",
    "ref_span_start_grch38",
    "ref_span_end_grch38",
    "occluding_deletion_id",
    "occluding_deletion_ref_len",
    "reason",
]


def _require_chain() -> Path:
    """Skip-if-absent guard for the hg38ToHg19 chain (mirrors the conftest
    chain-skip pattern, but for the CORRECT direction)."""
    if not _HG38_TO_HG19_CHAIN.exists():
        pytest.skip(f"chain file not present: {_HG38_TO_HG19_CHAIN}")
    return _HG38_TO_HG19_CHAIN


def _region1_rows() -> list[tuple]:
    """The canonical region-1 `.bim` fixture rows, sourced from the single source
    of truth in test_occlusion_span_filter.py (loaded by file path so it resolves
    regardless of the pytest package/rootdir import mode). Duplicating the
    coordinate table here would invite exactly the drift T-m3-07a-02 warns about.
    """
    import importlib.util

    path = Path(__file__).with_name("test_occlusion_span_filter.py")
    spec = importlib.util.spec_from_file_location("_m3_occlusion_span_fixture", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # safe: its impl imports are function-local
    return list(mod._REGION1_BIM_ROWS)


def _vid_at(rows: list[tuple], bp: int) -> str:
    hits = [r[1] for r in rows if int(r[3]) == bp]
    assert len(hits) == 1
    return hits[0]


# --------------------------------------------------------------------------- #
# 1. Stage-A record schema                                                     #
# --------------------------------------------------------------------------- #

def test_stage_a_record_has_all_coordinate_columns():
    """Every Stage-A record carries the full coordinate/provenance column set."""
    import occlusion_manifest as om

    rows = _region1_rows()
    records = om.build_region_records("m2_region_00001", rows)

    assert len(records) == 5  # one per occluded variant
    for rec in records:
        for col in _STAGE_A_COLUMNS:
            assert col in rec, f"Stage-A record missing column {col!r}"
        assert rec["region_id"] == "m2_region_00001"
        assert int(rec["pos_grch38"]) > 0
        assert int(rec["occluding_deletion_ref_len"]) > 1


def test_stage_a_record_carries_no_individual_level_fields():
    """Egress boundary (REQ-AOU-LD-EGRESS): Stage-A is coordinate geometry ONLY —
    no genotypes, no per-person / per-sample counts may ride out of the perimeter."""
    import occlusion_manifest as om

    records = om.build_region_records("m2_region_00001", _region1_rows())
    # SUBSTRING match, not whole-key equality (blast-radius MEDIUM 2026-07-15): the
    # prior whole-key check let `n_samples` / `sample_count` / `genotype_ac` / `AC_alt`
    # ride out — exactly the individual-level leak REQ-AOU-LD-EGRESS forbids — because
    # `_STAGE_A_COLUMNS` contains no such literal key. `genotype`/`sample`/`person`/
    # `individual` are matched as substrings; the short allele-tally tokens `gt`/`ac`/
    # `an` are matched as delimited TOKENS (not substrings) to avoid false positives on
    # innocent keys (the 'an' in 'span'/'variant', the 'gt' in 'length'). AF/MAF are NOT
    # forbidden — allele frequency is aggregate and legitimately egresses (the AF
    # sidecar); this guard targets per-person / per-sample / per-genotype fields only.
    import re
    substring_forbidden = ("genotype", "sample", "person", "individual")
    token_forbidden = ("gt", "ac", "an")
    for rec in records:
        for key in rec:
            k = key.lower()
            for bad in substring_forbidden:
                assert bad not in k, f"individual-level column {key!r} (contains {bad!r})"
            tokens = set(re.split(r"[^a-z0-9]+", k))
            for bad in token_forbidden:
                assert bad not in tokens, f"individual-level column {key!r} (token {bad!r})"


def test_ref_span_derives_from_the_occluding_deletion():
    """ref_span_start/end == POS_D / POS_D + len(REF_D) − 1 of the OCCLUDING
    deletion, and the occluder columns name that deletion. Asserted on the pair-4
    tangle, where the attribution is UPSTREAM (5922716), NOT downstream (5922724)."""
    import occlusion_manifest as om

    rows = _region1_rows()
    records = om.build_region_records("m2_region_00001", rows)
    by_vid = {r["variant_id"]: r for r in records}

    snp_c = _vid_at(rows, 5_922_718)
    rec = by_vid[snp_c]
    assert rec["occluding_deletion_id"] == _vid_at(rows, 5_922_716)   # UPSTREAM
    assert rec["occluding_deletion_id"] != _vid_at(rows, 5_922_724)   # not downstream
    assert int(rec["occluding_deletion_ref_len"]) == 7
    assert int(rec["ref_span_start_grch38"]) == 5_922_716
    assert int(rec["ref_span_end_grch38"]) == 5_922_716 + 7 - 1 == 5_922_722
    assert int(rec["pos_grch38"]) == 5_922_718
    # the occluded variant lies strictly inside the occluding deletion's footprint
    assert rec["ref_span_start_grch38"] < rec["pos_grch38"] <= rec["ref_span_end_grch38"]


def test_ref_span_on_the_boundary_case():
    """snpD at 8375822 sits on del7's LAST covered base (8375794 + 29 − 1)."""
    import occlusion_manifest as om

    rows = _region1_rows()
    records = om.build_region_records("m2_region_00001", rows)
    by_vid = {r["variant_id"]: r for r in records}
    rec = by_vid[_vid_at(rows, 8_375_822)]

    assert int(rec["ref_span_start_grch38"]) == 8_375_794
    assert int(rec["ref_span_end_grch38"]) == 8_375_822
    assert int(rec["pos_grch38"]) == int(rec["ref_span_end_grch38"])


def test_reason_is_the_reference_occlusion_constant():
    """Every record's ``reason`` is the module's single reference-occlusion
    constant. Asserted against the exported constant rather than a hardcoded
    literal: the source doc-set renders this string with and without spaces around
    the arrow, so pinning one rendering here would bake a coin-flip into the
    contract. The SEMANTICS (reference-occlusion -> undefined LD) are pinned."""
    import occlusion_manifest as om

    reason = om.REASON_REFERENCE_OCCLUSION
    assert "reference-occlusion" in reason
    assert "undefined-LD" in reason.replace(" ", "")

    records = om.build_region_records("m2_region_00001", _region1_rows())
    assert {r["reason"] for r in records} == {reason}


def test_occlusion_order_is_direct_for_every_coordinate_derived_drop():
    """``occlusion_order`` records HOW a variant's occlusion was derived, and for a
    Stage-A (coordinate-geometry-only) manifest every occluded variant is ``direct``
    — each sits inside exactly one occluding deletion's REF span.

    RECONCILED 2026-07-15 (blast-radius BLOCKER). The prior assertion demanded snpC
    (5922718) be ``second_order``, which INVERTED the byte-verified geometry verdict
    (`m3_region1_nan_geometry_verdict.md:19` — pair 3 `DEL 5922716 → SNP 5922718` is
    `ref_span_overlap` = DIRECT; the "2nd-order" label attaches to the *disjoint*
    pair-4 EDGE `5922718 → DEL 5922724`, which occludes NOTHING). It was also
    underivable: the sibling detector pins `edges` to EXACTLY the 5 direct-overlap
    edges and explicitly EXCLUDES the disjoint pair-4 edge
    (`test_occlusion_span_filter.py:267,292`), so nothing a coordinate Stage-A can see
    separates snpC from the other four — the only way to make ``second_order`` pass was
    to hardcode position 5922718, publishing a false provenance label across all 276
    regions (T-m3-07a-02 realized). snpC's OCCLUSION is direct (via the upstream
    DEL 5922716); the pair-4 disjoint NaN is a genotype-layer, second-order CONSEQUENCE
    of that single drop ("one drop, two edges" — RESEARCH §7), not a second-order
    occlusion, and it is not visible to a genotype-free Stage A. If a later
    genotype-aware stage annotates the tangle, it does so in its own field, not by
    mislabelling this variant's coordinate-derived occlusion.

    The value is derivable from the SAME edge set the detector suite pins (one direct
    edge per occluded variant), so a correct impl produces ``direct`` for all five
    without hardcoding anything.
    """
    import occlusion_manifest as om

    rows = _region1_rows()
    records = om.build_region_records("m2_region_00001", rows)

    # ``occlusion_order`` is OPTIONAL (RESEARCH §7:296 — "A (optional, from edges)"),
    # so do NOT force 07b to emit it. But IF present, every coordinate-derived value
    # MUST be "direct" — INCLUDING snpC (5922718), whose occluder is the UPSTREAM
    # DEL 5922716 (a genuine ref_span_overlap), NOT the downstream disjoint DEL 5922724.
    present = [r["occlusion_order"] for r in records if "occlusion_order" in r]
    if present:
        assert set(present) == {"direct"}
        assert len(present) == len(records)  # all-or-none, not a partial column


# --------------------------------------------------------------------------- #
# 2. resume-safe emission + aggregate rollup                                   #
# --------------------------------------------------------------------------- #

def test_append_region_manifest_is_resume_safe_dedup(tmp_path):
    """Appending the SAME region twice (Spot-VM preemption re-run) yields exactly
    one row per (region_id, variant_id) — mirrors _append_panel_row_local."""
    import pandas as pd
    import occlusion_manifest as om

    manifest = tmp_path / "occlusion_manifest.tsv"
    records = om.build_region_records("m2_region_00001", _region1_rows())

    om.append_region_manifest(manifest, records)
    om.append_region_manifest(manifest, records)  # re-run after preemption

    df = pd.read_csv(manifest, sep="\t")
    assert len(df) == 5
    assert not df.duplicated(subset=["region_id", "variant_id"]).any()
    # header written exactly once
    raw = manifest.read_text().splitlines()
    assert sum(1 for ln in raw if ln.startswith("region_id\t")) == 1


def test_append_region_manifest_keeps_distinct_regions(tmp_path):
    """Dedup is keyed on (region_id, variant_id) — the SAME variant_id under a
    DIFFERENT region_id is a distinct record and must not be swallowed."""
    import pandas as pd
    import occlusion_manifest as om

    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(manifest, om.build_region_records("regA", _region1_rows()))
    om.append_region_manifest(manifest, om.build_region_records("regB", _region1_rows()))

    df = pd.read_csv(manifest, sep="\t")
    assert len(df) == 10
    assert set(df["region_id"]) == {"regA", "regB"}


def test_aggregate_rollup_concatenates_per_region_records(tmp_path):
    """The genome-wide occlusion_catalog.tsv (the Angle-1/3 catalog seed) is the
    concatenation of the per-region manifests."""
    import pandas as pd
    import occlusion_manifest as om

    rows = _region1_rows()
    m1 = tmp_path / "regA" / "occlusion_manifest.tsv"
    m2 = tmp_path / "regB" / "occlusion_manifest.tsv"
    m1.parent.mkdir(parents=True)
    m2.parent.mkdir(parents=True)
    om.append_region_manifest(m1, om.build_region_records("regA", rows))
    om.append_region_manifest(m2, om.build_region_records("regB", rows))

    catalog = tmp_path / "occlusion_catalog.tsv"
    om.aggregate_manifests([m1, m2], catalog)

    df = pd.read_csv(catalog, sep="\t")
    assert len(df) == 10
    assert set(df["region_id"]) == {"regA", "regB"}
    for col in _STAGE_A_COLUMNS:
        assert col in df.columns


# --------------------------------------------------------------------------- #
# 3. Stage-B liftover GRCh38 -> GRCh37 (hinge-check anchors)                   #
# --------------------------------------------------------------------------- #

def test_liftover_pos_grch37_matches_hinge_check_anchors():
    """Stage B: pos_grch37 for the pair-4 tangle members reproduces the SETTLED
    hinge-check anchors 5922716/5922718/5922724 -> 5982776/5982778/5982784.

    The panel<->sumstats join is (CHR,POS)-only on GRCh37 (snp_id_bridge.R:107-121,
    drop-only, no re-key), so a wrong pos_grch37 silently drops the WRONG sumstats
    row — this is the assertion that keeps the lockstep honest.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import occlusion_manifest as om

    rows = _region1_rows()
    records = [
        {"chr": "1", "variant_id": _vid_at(rows, bp), "pos_grch38": bp}
        for bp in sorted(_LIFTOVER_ANCHORS)
    ]

    lifted = om.add_grch37_positions(records, chain_path=chain)

    got = {int(r["pos_grch38"]): int(r["pos_grch37"]) for r in lifted}
    assert got == _LIFTOVER_ANCHORS


def test_liftover_failure_records_na_not_a_wrong_position():
    """A variant that does NOT lift must record an EXPLICITLY missing pos_grch37
    (None/NA/NaN) — never a silently wrong coordinate, and never a pass-through of
    the GRCh38 position. ld_npz_to_rds.R:184-190 records failed liftovers as NA and
    drops them rather than guessing; the manifest must be equally explicit."""
    import math

    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import occlusion_manifest as om

    # an unmappable coordinate far past the end of chr1
    records = [{"chr": "1", "variant_id": "1:999999999:A:T", "pos_grch38": 999_999_999}]
    lifted = om.add_grch37_positions(records, chain_path=chain)

    assert len(lifted) == 1
    val = lifted[0]["pos_grch37"]
    is_missing = val is None or val == "NA" or (isinstance(val, float) and math.isnan(val))
    assert is_missing, f"unmappable variant must record NA, got {val!r}"


# --------------------------------------------------------------------------- #
# 4. the scan->enrich SEAM: present_rate is keyed (chr, pos_grch37) on GRCh37  #
# --------------------------------------------------------------------------- #
#
# SEAM (blast-radius 2026-07-15, quick-260715-u22). The sibling seam — the manifest
# PRODUCER vs the sumstats CONSUMER — got a guard at
# test_occlusion_lockstep_drop.py:272 (test_producer_manifest_feeds_the_consumer),
# whose docstring warns that "07b and 07c can each ship green while producing a
# manifest the other cannot consume". THIS seam is its sibling and had none: the 07c
# present-rate scan (`scan_present_rate`, unbuilt) is pinned by its own RED to return
# a dict keyed by a (chr, pos) TUPLE on **GRCh37**
# (test_occlusion_present_rate_scan.py:72 — `target = (1, 5_982_778)`; the string
# `variant_id` appears NOWHERE in that suite), while the SHIPPED consumer looked the
# hand-off up by the GRCh38-derived `variant_id` STRING. A dict `.get()` miss is
# SILENT: build 07c exactly to its RED and every lookup misses -> traits_present /
# n_traits_present / n_traits_scanned go pd.NA across ALL 276 regions, reading
# "scanned but absent everywhere" and INDISTINGUISHABLE from a real k=0 — which would
# silently blank the rs182965575 "present in 7 of 9 AFR sumstats" evidence that
# retired NaN->0 and is published as the osf.io/az52u provenance. Both suites stay
# green throughout.
#
# It is not a cast: the scan reads PUBLIC GRCh37 harmonized sumstats and locates rows
# by (CHR,POS), so it can never compute a GRCh38 variant_id. `STAGE_A_COLUMNS` carries
# no `pos_grch37` at all — `add_grch37_positions` adds it — so `enrich` (post-lift) is
# the ONLY place carrying BOTH `variant_id` and `chr` + `pos_grch37`. The join must
# therefore happen there, on (chr, pos_grch37).
#
# The present_rate dicts below are HAND-CONSTRUCTED on purpose: importing
# `occlusion_present_rate_scan` would tie these tests to unbuilt 07c and keep them RED
# forever instead of pinning the contract 07c must be built against TODAY.


def test_present_rate_joins_on_the_chr_pos_grch37_tuple_key(tmp_path):
    """present_rate keyed {(chr, pos_grch37): {...}} populates the matching row.

    `(1, 5_982_778)` is byte-identical to the key the 07c producer RED emits
    (test_occlusion_present_rate_scan.py:72) — that identity IS the seam. snpC is
    GRCh38 5922718 -> GRCh37 5982778 (the settled hinge-check anchor), so a consumer
    keying on the GRCh38 `variant_id` ('1:5922718:A:A') can never match it.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import occlusion_manifest as om

    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(
        manifest, om.build_region_records("m2_region_00001", _region1_rows())
    )

    out = tmp_path / "enriched.tsv"
    om.enrich_occlusion_manifest(
        manifest, chain, out_path=out,
        present_rate={
            (1, 5_982_778): {
                "traits_present": "bmi,ldl",
                "n_traits_present": 2,
                "n_traits_scanned": 3,
            }
        },
    )

    df = pd.read_csv(out, sep="\t")
    target = df[df["pos_grch38"] == 5_922_718]
    assert len(target) == 1, "the region-1 fixture emits exactly one snpC row"
    row = target.iloc[0]
    assert int(row["pos_grch37"]) == 5_982_778          # the seam's join key
    assert row["traits_present"] == "bmi,ldl"
    assert int(row["n_traits_present"]) == 2
    assert int(row["n_traits_scanned"]) == 3

    # the four NON-target occluded rows were not scanned -> explicitly missing
    others = df[df["pos_grch38"] != 5_922_718]
    assert len(others) == 4
    for col in om.STAGE_B_TRAIT_COLUMNS:
        assert others[col].isna().all(), f"unscanned row got a value in {col!r}"


def test_present_rate_leaves_na_for_a_variant_that_did_not_lift(tmp_path):
    """A row whose liftover FAILED (pos_grch37 is None) can never join the
    (CHR,POS)-only GRCh37 scan, so its trait columns are pd.NA — deliberately.

    `None` is an EXPLICIT, already-documented signal (add_grch37_positions:270-279,
    :291), not an error. This test also forces the float normalization the join must
    survive: one unlifted row demotes `out["pos_grch37"]` from int64 to float64
    (None -> NaN), so a key built by a naive `int(...)` over the column would raise
    and a key built without NaN-handling would fabricate a bogus position.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import occlusion_manifest as om

    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(
        manifest, om.build_region_records("m2_region_00001", _region1_rows())
    )
    # one synthetic Stage-A row at an unmappable coordinate far past the end of chr1
    # (mirrors test_liftover_failure_records_na_not_a_wrong_position:341)
    unmappable_vid = "1:999999999:A:T"
    om.append_region_manifest(manifest, [{
        "region_id": "m2_region_00001",
        "chr": "1",
        "variant_id": unmappable_vid,
        "pos_grch38": 999_999_999,
        "ref": "A",
        "alt": "T",
        "ref_span_start_grch38": 999_999_990,
        "ref_span_end_grch38": 999_999_999,
        "occluding_deletion_id": "1:999999990:AAAAAAAAAA:A",
        "occluding_deletion_ref_len": 10,
        "reason": om.REASON_REFERENCE_OCCLUSION,
        "occlusion_order": "direct",
    }])

    out = tmp_path / "enriched.tsv"
    # a LEGITIMATE key that DOES match a liftable row, so the total-miss guard
    # (pinned separately) is not what is under test here
    om.enrich_occlusion_manifest(
        manifest, chain, out_path=out,
        present_rate={
            (1, 5_982_778): {
                "traits_present": "bmi", "n_traits_present": 1, "n_traits_scanned": 9,
            }
        },
    )

    df = pd.read_csv(out, sep="\t")
    unlifted = df[df["variant_id"] == unmappable_vid]
    assert len(unlifted) == 1
    assert unlifted.iloc[0]["pos_grch37"] is None or pd.isna(unlifted.iloc[0]["pos_grch37"])
    for col in om.STAGE_B_TRAIT_COLUMNS:
        assert unlifted[col].isna().all(), (
            f"an unlifted variant must carry NA in {col!r}, never a guessed join"
        )
    # the liftable target still joined (the unlifted row must not poison the join)
    target = df[df["pos_grch38"] == 5_922_718]
    assert target.iloc[0]["traits_present"] == "bmi"


def test_present_rate_matching_no_liftable_row_raises_not_silent_na(tmp_path):
    """A non-empty present_rate that matches NOT ONE liftable row RAISES.

    This whole bug class is silent-pd.NA. When liftable rows EXIST, a total miss is
    indistinguishable from a real "scanned, absent in every trait" result — the
    manifest would publish k=0 provenance that is actually a key-contract bug. There
    is no honest way to tell those apart after the fact, so we refuse to write the
    file rather than publish silently-wrong pre-registered provenance (osf.io/az52u).
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import occlusion_manifest as om

    manifest = tmp_path / "occlusion_manifest.tsv"
    # all 5 region-1 records LIFT, so liftable keys exist -> the guard is armed
    om.append_region_manifest(
        manifest, om.build_region_records("m2_region_00001", _region1_rows())
    )

    with pytest.raises(ValueError) as exc:
        om.enrich_occlusion_manifest(
            manifest, chain, out_path=tmp_path / "enriched.tsv",
            present_rate={(99, 1): {"traits_present": "bmi",
                                    "n_traits_present": 1,
                                    "n_traits_scanned": 9}},
        )

    msg = str(exc.value)
    # the message must NAME the contract, not just say "no match"
    assert "pos_grch37" in msg
    assert "chr" in msg


def test_present_rate_against_a_wholly_unliftable_manifest_does_not_raise(tmp_path):
    """ZERO liftable rows + a non-empty present_rate -> NO raise, all pd.NA.

    The symmetric case to the total-miss guard, and the reason that guard is scoped to
    LIFTABLE rows only. A None key means "this variant did not lift" — an EXPLICIT,
    already-documented signal (add_grch37_positions:270-279, :291), correctly carried
    as pd.NA. There is nothing to join against, so silence is CORRECT here.

    A guard that also halted this legitimate case would trade a silent-wrong-data bug
    for a false-abort bug — hard-aborting a region whose occluded variants all sit in
    a liftover/assembly gap (rare but plausible; nothing upstream excludes assembly
    gaps), with a message indistinguishable from a real regression. That guard would
    get ripped out by a future maintainer, silently restoring the original defect.
    **Test C and this test together pin the exact raise boundary; neither is complete
    without the other.**
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import occlusion_manifest as om

    # Mutate the REAL producer's output so nothing lifts — this keeps the full Stage-A
    # schema (an honest manifest) rather than hand-rolling one. 999_999_999+ is far
    # past the end of chr1 and is already pinned as unmappable at :341.
    records = om.build_region_records("m2_region_00001", _region1_rows())
    assert len(records) == 5
    for i, rec in enumerate(records):
        rec["pos_grch38"] = 999_999_999 + i
        # keep the 5 records distinct under the (region_id, variant_id) dedup
        rec["variant_id"] = f"{rec['chr']}:{rec['pos_grch38']}:{rec['ref']}:{rec['alt']}"

    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(manifest, records)

    out = tmp_path / "enriched.tsv"
    # a LEGITIMATE non-empty present_rate — the same real key Test A joins on
    out_path = om.enrich_occlusion_manifest(   # must NOT raise
        manifest, chain, out_path=out,
        present_rate={
            (1, 5_982_778): {
                "traits_present": "bmi,ldl", "n_traits_present": 2, "n_traits_scanned": 3,
            }
        },
    )

    import pandas as pd
    df = pd.read_csv(out_path, sep="\t")
    assert len(df) == 5
    assert df["pos_grch37"].isna().all(), "the fixture is meant to be wholly unliftable"
    for col in om.STAGE_B_TRAIT_COLUMNS:
        assert df[col].isna().all()


# --------------------------------------------------------------------------- #
# 5. HIGH-0: the total-miss guard could not fire — SUBSTANCE, not membership   #
# --------------------------------------------------------------------------- #
#
# The shipped guard tests `any(k in present_rate for k in keys_present)`. But the scan
# keys are built FROM the manifest's own lifted rows (assemble_occlusion_catalog.py:399-410)
# and `scan_present_rate` returns a record for EVERY requested key — so that membership
# test is ALWAYS True. It can detect key-SHAPE drift and nothing else.
#
# Verified in the blast radius (HIGH-0): a manifest lifted to (1, 5982778) scanned
# against a file the scan could not parse publishes `n_traits_present=0,
# traits_present='[]'` and does NOT raise. If every AFR file were unparseable, the
# catalog would publish "present in 0 of 9 traits" for every row — a wholly wrong
# PRE-REGISTERED claim (osf.io/az52u) — with zero error signal.
#
# Substance (did the scan actually parse anything?) is the missing half, and it is NOT
# derivable from `present_rate` alone. That is why `scan_stats` is threaded in.
#
# The present_rate/scan_stats dicts below are HAND-CONSTRUCTED for the same reason the
# section-4 ones are: pinning the CONTRACT rather than coupling to the 07c producer.


def _lifted_present_rate(records, chain, om):
    """A present_rate carrying a record for EVERY liftable manifest key, all k=0.

    This is EXACTLY the shape `scan_present_rate` returns after a scan that parsed
    nothing: never a missing key, always an honest-looking zero. Building it from the
    REAL lifted records is what makes the membership guard genuinely pass.
    """
    lifted = om.add_grch37_positions(records, chain_path=chain)
    keys = [om._present_rate_key(r["chr"], r["pos_grch37"]) for r in lifted]
    return {
        k: {"traits_present": [], "n_traits_present": 0, "n_traits_scanned": 1}
        for k in keys if k is not None
    }


def test_scan_stats_that_parsed_nothing_raises_even_though_every_key_is_present(tmp_path):
    """HIGH-0. Key PRESENCE is necessary but NOT sufficient — substance is the guard.

    The first half of this test DEMONSTRATES the defect: with every requested key
    present in `present_rate`, the shipped membership guard passes and enrich writes a
    silent, wholly-wrong `n_traits_present = 0` across every row. The second half
    requires that threading the scan's parse health in makes the SAME call raise.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import occlusion_manifest as om

    records = om.build_region_records("m2_region_00001", _region1_rows())
    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(manifest, records)
    present_rate = _lifted_present_rate(records, chain, om)
    assert len(present_rate) == 5, "every region-1 row lifts -> the old guard is armed"

    # (a) TODAY: no raise, and the catalog silently publishes k=0 everywhere.
    quiet = om.enrich_occlusion_manifest(
        manifest, chain, out_path=tmp_path / "quiet.tsv", present_rate=present_rate,
    )
    df = pd.read_csv(quiet, sep="\t")
    assert (df["n_traits_present"] == 0).all(), (
        "this is the silently-wrong pre-registered provenance HIGH-0 describes"
    )

    # (b) REQUIRED: the same call, told the scan parsed NOTHING, must refuse.
    with pytest.raises(ValueError) as exc:
        om.enrich_occlusion_manifest(
            manifest, chain, out_path=tmp_path / "loud.tsv",
            present_rate=present_rate,
            scan_stats={"n_rows_seen": 17_195_956, "n_rows_parsed": 0,
                        "n_unparseable": 17_195_956, "n_truncated": 0,
                        "n_files_scanned": 1},
        )

    msg = str(exc.value)
    assert "n_rows_parsed" in msg or "parsed" in msg.lower()
    assert "17195956" in msg.replace(",", "") or "17,195,956" in msg


def test_healthy_scan_stats_do_not_raise(tmp_path):
    """A scan that DID parse rows is not a failure just because k is 0 everywhere.

    "Scanned and found nowhere" is a real, reportable scientific result — it is the
    cheap end of the exclusion cost. The new guard must key on parse SUBSTANCE, never
    on k, or it would forbid an honest answer.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import occlusion_manifest as om

    records = om.build_region_records("m2_region_00001", _region1_rows())
    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(manifest, records)

    om.enrich_occlusion_manifest(          # must NOT raise
        manifest, chain, out_path=tmp_path / "ok.tsv",
        present_rate=_lifted_present_rate(records, chain, om),
        scan_stats={"n_rows_seen": 19_695_660, "n_rows_parsed": 19_695_660,
                    "n_unparseable": 0, "n_truncated": 0, "n_files_scanned": 1},
    )


def test_assembly_gap_manifest_still_does_not_raise_with_scan_stats(tmp_path):
    """The DELIBERATE decision at ``occlusion_manifest.py:375-383`` survives.

    ZERO liftable rows (every occluded variant in a liftover/assembly gap) + a healthy
    scan -> still NO raise, all pd.NA. Scoping the total-miss guard to LIFTABLE rows is
    correct and documented; adding the substance guard must not turn that legitimate
    case into a hard abort. A guard that false-aborts gets ripped out by a future
    maintainer, silently restoring the original defect.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import occlusion_manifest as om

    records = om.build_region_records("m2_region_00001", _region1_rows())
    for i, rec in enumerate(records):
        rec["pos_grch38"] = 999_999_999 + i
        rec["variant_id"] = f"{rec['chr']}:{rec['pos_grch38']}:{rec['ref']}:{rec['alt']}"
    manifest = tmp_path / "occlusion_manifest.tsv"
    om.append_region_manifest(manifest, records)

    out = om.enrich_occlusion_manifest(   # must NOT raise
        manifest, chain, out_path=tmp_path / "gap.tsv",
        present_rate={(1, 5_982_778): {"traits_present": "bmi",
                                       "n_traits_present": 1, "n_traits_scanned": 9}},
        scan_stats={"n_rows_seen": 19_695_660, "n_rows_parsed": 19_695_660,
                    "n_unparseable": 0, "n_truncated": 0, "n_files_scanned": 1},
    )

    df = pd.read_csv(out, sep="\t")
    assert df["pos_grch37"].isna().all()
    for col in om.STAGE_B_TRAIT_COLUMNS:
        assert df[col].isna().all()
