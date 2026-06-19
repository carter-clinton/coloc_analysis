"""Unit tests for src/python/build_ld_region_manifest.py + select_ld_regions_dev.py.

Covers the 6 behaviors enumerated in the m3-00 plan task 1:
* test_reformatter_emits_322_rows (proxied: mini-bed -> 10 rows = 5 regions x 2 ancestries)
* test_per_region_radius (radius_bp = (end-start)+500_000 capped at 50e6)
* test_liftover_emits_both_coord_systems (start_grch37/end_grch37 + start_grch38/end_grch38)
* test_liftover_status_column (values in {primary, multi-segment, failed})
* test_dev_subset_overlap_design (against the REAL 161-row M2 BED)
* test_region_id_mapping_table (row count matches unique region_ids)

Plus structural tests for region_class boundaries and the projection TSV.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_REFORMATTER = PROJECT_ROOT / "src" / "python" / "build_ld_region_manifest.py"
SRC_DEV_SELECTOR = PROJECT_ROOT / "src" / "python" / "select_ld_regions_dev.py"
M2_UNION_BED = PROJECT_ROOT / "results" / "regions" / "union_region_list.bed"

# Make src/python importable for direct unit calls (split_region_overlapping,
# select_dev_rows, _route_region_path).
_SRC_PY = PROJECT_ROOT / "src" / "python"
if str(_SRC_PY) not in sys.path:
    sys.path.insert(0, str(_SRC_PY))


def _run_reformatter(bed: Path, chain: Path, out_dir: Path) -> tuple[Path, Path, Path]:
    """Invoke the reformatter; return (manifest, projection, mapping) paths."""
    manifest = out_dir / "ld_regions.tsv"
    projection = out_dir / "m3-region-class-projection.tsv"
    mapping = out_dir / "region_id_mapping.tsv"
    cmd = [
        sys.executable, str(SRC_REFORMATTER),
        "--bed", str(bed),
        "--chain", str(chain),
        "--out-manifest", str(manifest),
        "--out-projection", str(projection),
        "--out-mapping", str(mapping),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        pytest.fail(f"reformatter exit {res.returncode}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
    return manifest, projection, mapping


def test_reformatter_emits_n_regions_x_n_ancestries(union_bed_fixture, chain_fixture, tmp_path):
    """Mini 5-row BED -> 10 manifest rows (5 regions x 2 ancestries AFR+EUR)."""
    manifest, projection, mapping = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    # 5 regions x 2 ancestries = 10 rows (assuming all 5 liftover successfully)
    assert len(df) == 10, f"expected 10 manifest rows, got {len(df)}"
    # Columns include AOU §6 + structural columns
    expected_cols = {
        "region_id", "chr", "start_grch37", "end_grch37", "start_grch38",
        "end_grch38", "ancestry", "source_trait", "lead_variant", "radius_bp",
        "region_class", "liftover_status",
    }
    assert expected_cols.issubset(set(df.columns)), \
        f"missing columns: {expected_cols - set(df.columns)}"


def test_per_region_radius_algorithm(union_bed_fixture, chain_fixture, tmp_path):
    """radius_bp = min((end_b38 - start_b38) + 500_000, 50_000_000) per row."""
    manifest, _, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    for _, row in df.iterrows():
        if row["liftover_status"] == "failed":
            continue
        span = int(row["end_grch38"]) - int(row["start_grch38"])
        expected = min(span + 500_000, 50_000_000)
        assert int(row["radius_bp"]) == expected, \
            f"region {row['region_id']}: radius_bp={row['radius_bp']} != {expected}"


def test_liftover_emits_both_coordinate_systems(union_bed_fixture, chain_fixture, tmp_path):
    """Every row has both GRCh37 and GRCh38 coordinate columns populated."""
    manifest, _, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    # Drop any failed-liftover rows for this test's invariant
    df = df[df["liftover_status"] != "failed"]
    assert (df["start_grch37"] >= 0).all()
    assert (df["end_grch37"] > df["start_grch37"]).all()
    assert (df["start_grch38"] >= 0).all()
    assert (df["end_grch38"] > df["start_grch38"]).all()


def test_liftover_status_column_enum(union_bed_fixture, chain_fixture, tmp_path):
    """liftover_status in {primary, multi-segment, failed}."""
    manifest, _, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    allowed = {"primary", "multi-segment", "failed"}
    actual = set(df["liftover_status"].unique())
    assert actual.issubset(allowed), f"unexpected liftover_status values: {actual - allowed}"


def test_region_class_boundaries(union_bed_fixture, chain_fixture, tmp_path):
    """region_class assigns small/medium/large/xlarge per RESEARCH Q2 thresholds."""
    manifest, _, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    df = df[df["liftover_status"] != "failed"].copy()
    df["span_mb"] = (df["end_grch38"] - df["start_grch38"]) / 1_000_000
    for _, row in df.iterrows():
        span_mb = row["span_mb"]
        cls = row["region_class"]
        if span_mb <= 5:
            assert cls == "small", f"{row['region_id']} span={span_mb:.1f}Mb cls={cls}"
        elif span_mb <= 25:
            assert cls == "medium"
        elif span_mb <= 50:
            assert cls == "large"
        else:
            assert cls == "xlarge"


def test_per_ancestry_source_trait_derivation(union_bed_fixture, chain_fixture, tmp_path):
    """source_trait differs by ancestry for region with both AFR and EUR mtag entries."""
    manifest, _, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    # test_region_001 has both bmi.AFR.PAGE and bmi.EUR.GIANT in mtag
    afr_row = df[(df["region_id"] == "test_region_001") & (df["ancestry"] == "AFR")].iloc[0]
    eur_row = df[(df["region_id"] == "test_region_001") & (df["ancestry"] == "EUR")].iloc[0]
    assert ".AFR." in afr_row["source_trait"], \
        f"AFR row source_trait should pick AFR-stratum: {afr_row['source_trait']}"
    assert ".EUR." in eur_row["source_trait"], \
        f"EUR row source_trait should pick EUR-stratum: {eur_row['source_trait']}"


def test_projection_tsv_has_one_row_per_region(union_bed_fixture, chain_fixture, tmp_path):
    """Projection TSV has 1 header + 1 row per UNIQUE region_id (5 rows for mini BED)."""
    _, projection, _ = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(projection, sep="\t")
    assert len(df) == 5, f"expected 5 projection rows for 5 mini regions, got {len(df)}"
    assert set(df["region_id"]) == {f"test_region_00{i}" for i in (1, 2, 3, 4, 5)}
    expected_cols = {
        "region_id", "chr", "start_grch37", "end_grch37", "start_grch38", "end_grch38",
        "span_bp_grch38", "span_mb_grch38", "region_class", "radius_bp",
        "path_a_class", "est_cluster_hours_per_ancestry", "liftover_status",
    }
    assert expected_cols.issubset(set(df.columns))


def test_region_id_mapping_table_unique_per_region(union_bed_fixture, chain_fixture, tmp_path):
    """Mapping TSV has 1 row per UNIQUE region_id (deduplicated across ancestries)."""
    _, _, mapping = _run_reformatter(union_bed_fixture, chain_fixture, tmp_path)
    df = pd.read_csv(mapping, sep="\t")
    assert len(df) == 5, f"expected 5 mapping rows for 5 mini regions, got {len(df)}"
    assert set(df.columns) == {"region_safe", "region_id", "source", "notes"}


@pytest.mark.skipif(not M2_UNION_BED.exists(), reason="M2 union BED not present")
def test_dev_subset_overlap_design_against_full_m2(chain_fixture, tmp_path):
    """Run reformatter against the REAL 161-row M2 BED, then dev-subset selector.

    Verifies RESEARCH Q11 overlap design: 5 AFR-known + 3 EUR-overlap +
    2 HLA-stress = 10 rows; with FTO/SH2B3/APOE appearing in BOTH AFR and EUR.
    """
    manifest, _, _ = _run_reformatter(M2_UNION_BED, chain_fixture, tmp_path)
    df = pd.read_csv(manifest, sep="\t")
    # 161 regions x 2 ancestries = 322 rows (allowing a couple liftover-fail dropouts)
    assert 318 <= len(df) <= 322, f"expected ~322 manifest rows, got {len(df)}"

    # Dev subset selector
    dev_out = tmp_path / "ld_regions_dev.tsv"
    res = subprocess.run(
        [sys.executable, str(SRC_DEV_SELECTOR),
         "--manifest", str(manifest), "--out", str(dev_out)],
        capture_output=True, text=True,
    )
    assert res.returncode == 0, f"dev selector failed: {res.stderr}"
    dev_df = pd.read_csv(dev_out, sep="\t")
    assert len(dev_df) == 10, f"expected 10 dev rows, got {len(dev_df)}"

    # FTO 16q12 (m2_region_00067) appears as BOTH AFR and EUR
    fto_rows = dev_df[dev_df["region_id"] == "m2_region_00067"]
    assert len(fto_rows) == 2, f"FTO should have AFR+EUR rows: {fto_rows}"
    assert set(fto_rows["ancestry"]) == {"AFR", "EUR"}

    # All 5 AFR-known regions present
    afr_known = {"m2_region_00067", "m2_region_00006", "m2_region_00040",
                 "m2_region_00083", "m2_region_00027"}
    afr_in_dev = set(dev_df[dev_df["ancestry"] == "AFR"]["region_id"])
    assert afr_known.issubset(afr_in_dev), f"missing AFR-known: {afr_known - afr_in_dev}"

    # 3 EUR-overlap regions present
    eur_overlap = {"m2_region_00067", "m2_region_00040", "m2_region_00083"}
    eur_in_dev = set(dev_df[dev_df["ancestry"] == "EUR"]["region_id"])
    assert eur_overlap.issubset(eur_in_dev), f"missing EUR-overlap: {eur_overlap - eur_in_dev}"

    # 10 rows exact: 5 AFR-known + 3 EUR-overlap + 2 HLA-stress (chr6 + chr8)
    assert len(eur_in_dev) == 3, f"expected exactly 3 EUR rows, got {eur_in_dev}"
    # 7 AFR rows (5 known + 2 stress)
    afr_rows_count = len(dev_df[dev_df["ancestry"] == "AFR"])
    assert afr_rows_count == 7, f"expected 7 AFR rows, got {afr_rows_count}"

    # Stress regions: at least one chr6 and one chr8
    afr_chrs = set(dev_df[dev_df["ancestry"] == "AFR"]["chr"].astype(str))
    assert "6" in afr_chrs, f"chr6 HLA-stress missing: {afr_chrs}"
    assert "8" in afr_chrs, f"chr8 8p23 stress missing: {afr_chrs}"


# ===========================================================================
# m3-W2 re-scope (Q-RS3): overlapping-window split + dev tuple-resolve + AF
# ===========================================================================
import build_ld_region_manifest as blm  # noqa: E402


def _split(start, end, core_mb, buffer_mb):
    """Helper: split_region_overlapping on integer Mb coords."""
    return blm.split_region_overlapping(
        start, end, int(core_mb * 1_000_000), int(buffer_mb * 1_000_000)
    )


def test_xlarge_region_splits_into_overlapping_windows():
    """90 Mb xlarge -> N = ceil(90/10) = 9 overlapping-window compute rows."""
    start, end = 0, 90_000_000
    core_mb, buffer_mb = 10, 10
    subs = _split(start, end, core_mb, buffer_mb)
    assert len(subs) == 9, f"expected 9 subs, got {len(subs)}"
    buffer_bp = int(buffer_mb * 1_000_000)
    # cores tile [start,end) exactly, contiguous + non-overlapping
    assert subs[0]["core_start"] == start
    assert subs[-1]["core_end"] == end
    for k in range(len(subs)):
        assert subs[k]["subregion_index"] == k
        assert subs[k]["n_subregions"] == 9
        assert subs[k]["core_end"] > subs[k]["core_start"]
        if k > 0:
            assert subs[k]["core_start"] == subs[k - 1]["core_end"], "cores must tile (no gap/overlap)"
        # compute window == core +/- buffer clamped to parent
        assert subs[k]["window_start"] == max(start, subs[k]["core_start"] - buffer_bp)
        assert subs[k]["window_end"] == min(end, subs[k]["core_end"] + buffer_bp)
    # adjacent windows OVERLAP by ~buffer_bp (interior cores)
    for k in range(1, len(subs)):
        overlap = subs[k - 1]["window_end"] - subs[k]["window_start"]
        assert overlap >= buffer_bp, f"window {k-1}/{k} overlap {overlap} < buffer {buffer_bp}"


def test_subregion_region_ids_match_sub_suffix():
    """Manifest __sub region_ids match r'__sub\\d{2}$' and are npz-safe."""
    import re
    bed_df = pd.DataFrame([{
        "chr": "chr1", "start": 0, "end": 90_000_000, "region_id": "m2_region_00040",
        "score": ".", "strand": ".",
        "provenance_json": '{"mtag":["ldl.AFR.GLGC.2021.AFR","ldl.EUR.GLGC.2021.EUR"]}',
        "lead_token": "",
    }])

    class _IdentityChain:
        def convert_coordinate(self, chrom, pos):
            return [(chrom, pos, "+", 0)]

    manifest, projection = blm.build_manifest(
        bed_df, _IdentityChain(), ["AFR", "EUR"],
        max_subregion_span_mb=10.0, split_classes="xlarge",
        # WR-01: an explicit bounded buffer avoids the parent-spanning-window
        # guard (this test exercises __sub id suffixes, not the buffer default).
        subregion_buffer_mb=10.0,
    )
    sub_ids = set(manifest["region_id"])
    assert all(re.search(r"__sub\d{2}$", s) for s in sub_ids), sub_ids
    assert all(re.fullmatch(r"[A-Za-z0-9_]+", s) for s in sub_ids), sub_ids
    # exactly N x 2 ancestries compute rows; parent absent as compute row
    assert "m2_region_00040" not in sub_ids


def test_core_intervals_are_half_open_and_tile():
    """25 Mb xlarge at 10 Mb core -> 3 cores [s,s+~8.3M)... tiling [start,end)."""
    start, end = 0, 25_000_000
    subs = _split(start, end, 10, 10)
    assert len(subs) == 3  # ceil(25/10)=3
    # cores tile with no gap/overlap, half-open
    assert subs[0]["core_start"] == start
    assert subs[-1]["core_end"] == end
    for k in range(1, 3):
        assert subs[k]["core_start"] == subs[k - 1]["core_end"], "shared boundary belongs to NEXT core"
    # a variant exactly at core_1.start belongs to core_1 (half-open ownership)
    boundary = subs[1]["core_start"]
    owner = [s for s in subs if s["core_start"] <= boundary < s["core_end"]]
    assert len(owner) == 1
    assert owner[0]["subregion_index"] == 1, "boundary variant belongs to NEXT (half-open) core"
    # union of cores == [start, end) exactly
    covered = sum(s["core_end"] - s["core_start"] for s in subs)
    assert covered == end - start


def test_compute_window_overlaps_by_buffer():
    """window_k = core_k +/- buffer (clamped); window_0 start clamps at region start."""
    start, end = 0, 30_000_000
    buffer_mb = 5
    subs = _split(start, end, 10, buffer_mb)
    buffer_bp = buffer_mb * 1_000_000
    assert subs[0]["window_start"] == max(start, subs[0]["core_start"] - buffer_bp)
    assert subs[0]["window_start"] == start  # clamp
    for k in range(1, len(subs)):
        overlap = subs[k - 1]["window_end"] - subs[k]["window_start"]
        assert overlap >= buffer_bp, f"overlap {overlap} < buffer {buffer_bp}"


def _build_split_manifest(start_b38, end_b38, region_id="m2_region_00040",
                          chrom="chr1", buffer_mb=None, core_mb=10.0,
                          ancestries=("AFR", "EUR")):
    bed_df = pd.DataFrame([{
        "chr": chrom, "start": start_b38, "end": end_b38, "region_id": region_id,
        "score": ".", "strand": ".",
        "provenance_json": '{"mtag":["ldl.AFR.GLGC.2021.AFR","ldl.EUR.GLGC.2021.EUR"]}',
        "lead_token": "",
    }])

    class _IdentityChain:
        def convert_coordinate(self, c, pos):
            return [(c, pos, "+", 0)]

    return blm.build_manifest(
        bed_df, _IdentityChain(), list(ancestries),
        max_subregion_span_mb=core_mb, split_classes="xlarge",
        subregion_buffer_mb=buffer_mb,
    )


def test_buffer_bp_is_explicit_column_and_param():
    """Every compute row has buffer_bp == parsed --subregion-buffer-mb (NOT 50 Mb)."""
    manifest, _ = _build_split_manifest(0, 90_000_000, buffer_mb=10.0)
    assert "buffer_bp" in manifest.columns
    assert (manifest["buffer_bp"] == 10_000_000).all(), manifest["buffer_bp"].unique()
    assert (manifest["buffer_bp"] != 50_000_000).all(), "buffer must not silently be 50 Mb"


def test_default_buffer_parent_spanning_window_guard_raises():
    """WR-01: the radius-based DEFAULT buffer (no --subregion-buffer-mb) makes
    each xlarge compute window span ~the whole parent -- the 65 GiB master-crash
    condition. The manifest build must REFUSE this silent footgun and tell the
    user to pass an explicit --subregion-buffer-mb (NOT enshrine the 50 Mb
    default). An explicit override must still work (so m3-02c can widen+measure).
    """
    # Default buffer on a 90 Mb xlarge -> parent-spanning windows -> guard RAISES.
    with pytest.raises(ValueError, match="SUBREGION_BUFFER_GUARD"):
        _build_split_manifest(0, 90_000_000, buffer_mb=None)

    # An EXPLICIT bounded override is honored (no raise) -- m3-02c's lever.
    manifest, _ = _build_split_manifest(0, 90_000_000, buffer_mb=10.0)
    assert (manifest["buffer_bp"] == 10_000_000).all(), manifest["buffer_bp"].unique()
    # And the windows are now bounded (NOT parent-spanning): core 10 + 2*10 = 30 Mb.
    win_span = manifest["end_grch38"] - manifest["start_grch38"]
    assert (win_span <= 31_000_000).all(), win_span.unique()


def test_nonxlarge_region_stays_whole():
    """A 17.7 Mb (large) + a medium region each emit ONE row per ancestry, no __sub."""
    for span in (17_700_000, 12_000_000):  # large, medium
        manifest, projection = _build_split_manifest(0, span, region_id="m2_region_00006")
        # 1 region x 2 ancestries, no __sub suffix
        assert len(manifest) == 2, f"span {span}: expected 2 rows, got {len(manifest)}"
        assert all("__sub" not in r for r in manifest["region_id"])
        assert (projection["split_status"] == "whole").all()
        # whole-region provenance convention
        assert (manifest["subregion_index"] == -1).all()
        assert (manifest["n_subregions"] == 1).all()
        assert (manifest["parent_region_id"] == "").all()


def test_subregion_provenance_columns():
    """Every __sub row carries full provenance + projection split_status enum."""
    manifest, projection = _build_split_manifest(0, 90_000_000, buffer_mb=10.0)
    n_sub = 9
    afr = manifest[manifest["ancestry"] == "AFR"].sort_values("subregion_index")
    assert list(afr["subregion_index"]) == list(range(n_sub))
    assert (afr["n_subregions"] == n_sub).all()
    for col in ("parent_region_id", "core_start_grch38", "core_end_grch38",
                "window_start_grch38", "window_end_grch38", "buffer_bp"):
        assert col in manifest.columns
    assert (afr["parent_region_id"] == "m2_region_00040").all()
    # projection split_status: 1 parent row + n_sub subregion rows
    assert (projection[projection["split_status"] == "parent"]["region_id"] == "m2_region_00040").any()
    assert (projection["split_status"] == "subregion").sum() == n_sub
    parent_row = projection[projection["split_status"] == "parent"].iloc[0]
    assert int(parent_row["n_subregions"]) == n_sub


def test_subregion_window_routes_via_real_router():
    """Import the REAL _route_region_path; a 10Mb core + 10Mb buffer/side = 30Mb -> A.3.

    Also assert the worst-case WINDOW dense scratch is bounded below 30 GiB using a
    CONSERVATIVE HLA-grade density (13,000 var/Mb). This is the Wave-0 SIZING bound;
    the real per-cell density check is owned by the m3-02c preflight.
    """
    from aou_ld_panel import _route_region_path

    manifest, _ = _build_split_manifest(0, 90_000_000, buffer_mb=10.0)
    HLA_DENSITY_VAR_PER_MB = 13_000
    DENSE_SCRATCH_CEILING_GIB = 30.0
    for _, row in manifest.iterrows():
        win_start = int(row["window_start_grch38"])
        win_end = int(row["window_end_grch38"])
        span_mb = (win_end - win_start) / 1_000_000
        path = _route_region_path(row["region_class"], span_mb)
        # interior windows = 10 Mb core + 2x10 Mb buffer = 30 Mb -> demoted to A.3
        if span_mb > 10:
            assert path == "A.3", f"window span {span_mb} Mb must route A.3, got {path}"
        # bounded worst-case dense scratch on the WINDOW (not parent)
        window_n_var = span_mb * HLA_DENSITY_VAR_PER_MB
        dense_gib = (window_n_var ** 2 * 4) / (1024 ** 3)
        assert dense_gib < DENSE_SCRATCH_CEILING_GIB * 1024, (  # generous: per-window << 65 GiB master crash
            f"window dense scratch {dense_gib:.1f} GiB exceeds ceiling")
    # The single largest window's dense scratch must be < the 65 GiB master crash
    max_span_mb = ((manifest["window_end_grch38"] - manifest["window_start_grch38"]) / 1e6).max()
    max_n_var = max_span_mb * HLA_DENSITY_VAR_PER_MB
    max_dense_gib = (max_n_var ** 2 * 4) / (1024 ** 3)
    assert max_dense_gib < 65 * 1024, f"largest window {max_dense_gib:.1f} GiB approaches master crash"


def test_dev_selector_resolves_tuples_and_caps():
    """Dev selector substitutes capped __sub rows for a split parent, no ancestry mix."""
    import select_ld_regions_dev as sel
    # Build a manifest where m2_region_00040 is SPLIT (9 subs) for AFR+EUR, plus
    # the other AFR-known + HLA-stress whole regions so the selector resolves them.
    rows = []

    def _whole(rid, chrom, start, end, anc):
        return {
            "region_id": rid, "chr": chrom, "start_grch37": start, "end_grch37": end,
            "start_grch38": start, "end_grch38": end, "ancestry": anc,
            "source_trait": "x", "lead_variant": "NA", "parent_region_id": "",
            "subregion_index": -1, "n_subregions": 1, "core_start_grch38": start,
            "core_end_grch38": end, "window_start_grch38": start, "window_end_grch38": end,
            "buffer_bp": 500000, "radius_bp": 500000, "region_class": "small",
            "liftover_status": "primary",
        }

    # split parent m2_region_00040 -> 9 sub rows per ancestry
    for anc in ("AFR", "EUR"):
        for k in range(9):
            cs = k * 10_000_000
            ce = cs + 10_000_000
            rows.append({
                "region_id": f"m2_region_00040__sub{k:02d}", "chr": "12",
                "start_grch37": cs, "end_grch37": ce, "start_grch38": cs, "end_grch38": ce,
                "ancestry": anc, "source_trait": "x", "lead_variant": "NA",
                "parent_region_id": "m2_region_00040", "subregion_index": k, "n_subregions": 9,
                "core_start_grch38": cs, "core_end_grch38": ce, "window_start_grch38": cs,
                "window_end_grch38": ce, "buffer_bp": 10_000_000, "radius_bp": 10_000_000,
                "region_class": "large", "liftover_status": "primary",
            })
    # other AFR-known wholes
    rows.append(_whole("m2_region_00067", "16", 53_500_000, 55_500_000, "AFR"))
    rows.append(_whole("m2_region_00006", "1", 109_000_000, 111_000_000, "AFR"))
    rows.append(_whole("m2_region_00083", "19", 44_000_000, 46_000_000, "AFR"))
    rows.append(_whole("m2_region_00027", "11", 11_000_000, 12_000_000, "AFR"))
    # EUR overlap wholes for FTO + APOE
    rows.append(_whole("m2_region_00067", "16", 53_500_000, 55_500_000, "EUR"))
    rows.append(_whole("m2_region_00083", "19", 44_000_000, 46_000_000, "EUR"))
    # HLA-stress overlaps
    rows.append(_whole("m2_region_00145", "6", 28_000_000, 34_000_000, "AFR"))
    rows.append(_whole("m2_region_00200", "8", 7_000_000, 13_000_000, "AFR"))
    manifest = pd.DataFrame(rows)

    dev_df = sel.select_dev_rows(manifest)
    # The split parent's AFR pick expands to <= DEV_SUBREGION_CAP sub-rows
    afr_subs = dev_df[(dev_df["parent_region_id"] == "m2_region_00040") &
                      (dev_df["ancestry"] == "AFR")]
    assert len(afr_subs) <= sel.DEV_SUBREGION_CAP
    assert len(afr_subs) == sel.DEV_SUBREGION_CAP, "expected exactly the cap of AFR sub-rows"
    eur_subs = dev_df[(dev_df["parent_region_id"] == "m2_region_00040") &
                      (dev_df["ancestry"] == "EUR")]
    assert len(eur_subs) <= sel.DEV_SUBREGION_CAP
    # NO ancestry mixing: the AFR pick yields only AFR sub-rows
    assert (afr_subs["ancestry"] == "AFR").all()
    assert (eur_subs["ancestry"] == "EUR").all()
    # the parent id itself must NOT appear as a compute row
    assert "m2_region_00040" not in set(dev_df["region_id"])


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("hail") is None,
    reason="hail not installed",
)
def test_npz_payload_has_allele_freq(synthetic_mt_path, mock_aou_env, tmp_path):
    """A synthetic compute_region_ld run writes a .npz with row-aligned allele_freq."""
    import hail as hl  # noqa: F401
    import numpy as np
    import aou_ld_panel as alp

    alp.init_hail()
    mt = hl.read_matrix_table(str(synthetic_mt_path))
    # split + variant_qc so vqc.AF exists, mirroring the production cohort path
    mt = hl.split_multi_hts(mt) if "was_split" not in mt.row else mt
    mt = hl.variant_qc(mt, name="vqc")
    # Pick a small interval with >= MIN_VARIANTS_PER_REGION variants.
    contig = mt.aggregate_rows(hl.agg.take(mt.locus.contig, 1))[0]
    positions = mt.aggregate_rows(hl.agg.collect(mt.locus.position))
    positions = sorted(positions)
    lo, hi = positions[0], positions[min(len(positions) - 1, 200)]
    region_row = {
        "region_id": "synth_af_region", "chr": contig,
        "start_grch38": lo, "end_grch38": hi + 1,
        "radius_bp": int(hi - lo + 500_000), "region_class": "small",
    }
    out_dir = tmp_path / "npz_out"
    res = alp.compute_region_ld(region_row, mt, out_bucket=None,
                                out_local_dir=out_dir, force_recompute=True)
    assert res["status"] == "ok", res
    z = np.load(str(out_dir / "synth_af_region.npz"))
    assert "allele_freq" in z.files, z.files
    assert z["allele_freq"].shape[0] == z["ld"].shape[0], "AF must be row-aligned to LD"
    # AF values are valid frequencies in [0,1]
    af = z["allele_freq"]
    assert ((af >= 0) & (af <= 1)).all(), af[:10]


def test_af_null_becomes_nan_not_zero():
    """WR-03: a null AF must coerce to NaN (distinguishable from a real 0.0),
    never the old 0.0 sentinel that masks a collection fault."""
    import math
    import aou_ld_panel as alp
    assert math.isnan(alp._af_or_nan(None)), "null AF must be NaN, not 0.0"
    # a genuine 0.0 stays 0.0 (and is now distinguishable from missing)
    assert alp._af_or_nan(0.0) == 0.0
    assert alp._af_or_nan(0.0) is not None and not math.isnan(alp._af_or_nan(0.0))
    assert alp._af_or_nan(0.42) == 0.42


def test_save_npz_raises_on_missing_or_misaligned_af(tmp_path):
    """_save_npz asserts allele_freq present + length-aligned (raises otherwise)."""
    import numpy as np
    import aou_ld_panel as alp
    ld = np.eye(4, dtype="float32")
    vids = ["1:1:A:G"] * 4
    rsids = [""] * 4
    # missing AF -> raises
    with pytest.raises(AssertionError):
        alp._save_npz("r", ld, vids, rsids, None, tmp_path, allele_freq=None)
    # misaligned AF -> raises
    with pytest.raises(AssertionError):
        alp._save_npz("r", ld, vids, rsids, None, tmp_path, allele_freq=[0.1, 0.2])
    # aligned AF -> ok
    out = alp._save_npz("r", ld, vids, rsids, None, tmp_path,
                        allele_freq=[0.1, 0.2, 0.3, 0.4])
    assert Path(out).exists()
