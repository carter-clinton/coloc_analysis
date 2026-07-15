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
    forbidden = ("genotype", "sample", "person", "individual", "gt", "ac", "an")
    for rec in records:
        for key in rec:
            assert key.lower() not in forbidden, f"individual-level column {key!r}"


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


def test_occlusion_order_marks_direct_vs_second_order():
    """The optional ``occlusion_order`` column distinguishes the plain
    ref_span_overlap drops from the pair-4 tangle member (Angle-1/3 catalog
    flags deletion chains explicitly — RESEARCH §7 decision 1)."""
    import occlusion_manifest as om

    rows = _region1_rows()
    records = om.build_region_records("m2_region_00001", rows)
    by_vid = {r["variant_id"]: r for r in records}

    assert {r["occlusion_order"] for r in records} <= {"direct", "second_order"}
    # the plain ref_span_overlap drops are 'direct'
    for bp in (1_980_475, 5_733_487, 7_492_693, 8_375_822):
        assert by_vid[_vid_at(rows, bp)]["occlusion_order"] == "direct"
    # snpC is the pair-4 tangle member (the 3-record 5922716/5922718/5922724 knot)
    assert by_vid[_vid_at(rows, 5_922_718)]["occlusion_order"] == "second_order"


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
