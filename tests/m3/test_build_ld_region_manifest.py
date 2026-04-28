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
