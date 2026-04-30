"""tests/m3/test_validation_check_2_aou_eur_vs_1kg.py — Wave 2 Task 2 scaffold.

Validates the Check 2 per-region Pearson r TSV schema + pass-threshold logic.

Per AOU-LD-PIPELINE.md §9.2 + RESEARCH Validation Architecture: Check 2
compares AoU EUR LD vs 1000G EUR LD entry-wise per MAF bin {<0.01,
0.01-0.05, >=0.05}. Pass: mean r >= 0.97 for `maf_bin == "ge_0.05"` in
each of the 3 EUR overlap regions.

Synthetic fixture: 3 regions x 3 MAF bins = 9 rows.
"""
from __future__ import annotations

import io

import pandas as pd
import pytest


CHECK_2_FIXTURE_TSV = """region_id\tregion_safe\tmaf_bin\tn_var\tmean_r
m2_region_00067\tFTO_16q12\tlt_0.01\t1200\t0.85
m2_region_00067\tFTO_16q12\t01_05\t800\t0.93
m2_region_00067\tFTO_16q12\tge_0.05\t450\t0.985
m2_region_00040\tSH2B3_12q24\tlt_0.01\t950\t0.82
m2_region_00040\tSH2B3_12q24\t01_05\t610\t0.91
m2_region_00040\tSH2B3_12q24\tge_0.05\t320\t0.978
m2_region_00083\tAPOE_19q13\tlt_0.01\t880\t0.84
m2_region_00083\tAPOE_19q13\t01_05\t540\t0.92
m2_region_00083\tAPOE_19q13\tge_0.05\t290\t0.973
"""

PASS_R_GE_05 = 0.97
PASS_R_01_05 = 0.90
EXPECTED_REGIONS = {"m2_region_00067", "m2_region_00040", "m2_region_00083"}
EXPECTED_BINS = {"lt_0.01", "01_05", "ge_0.05"}


@pytest.fixture()
def check_2_pearson_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(CHECK_2_FIXTURE_TSV), sep="\t")


def test_check_2_schema(check_2_pearson_df: pd.DataFrame) -> None:
    required = {"region_id", "region_safe", "maf_bin", "n_var", "mean_r"}
    missing = required - set(check_2_pearson_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_check_2_three_regions_three_bins(check_2_pearson_df: pd.DataFrame) -> None:
    """All 3 EUR overlap regions have all 3 MAF bins populated."""
    by_region = check_2_pearson_df.groupby("region_id")["maf_bin"].apply(set)
    for region_id, bins in by_region.items():
        assert region_id in EXPECTED_REGIONS, f"unexpected region {region_id}"
        assert bins == EXPECTED_BINS, (
            f"region {region_id} missing bins: {EXPECTED_BINS - bins}"
        )


def test_check_2_pearson_correlation(check_2_pearson_df: pd.DataFrame) -> None:
    """For each region, mean r >= 0.97 in the ge_0.05 MAF bin."""
    ge_05 = check_2_pearson_df[check_2_pearson_df.maf_bin == "ge_0.05"]
    for _, row in ge_05.iterrows():
        assert row.mean_r >= PASS_R_GE_05, (
            f"region {row.region_id} mean_r={row.mean_r} < {PASS_R_GE_05} "
            f"at MAF >= 0.05; Check 2 R4 risk per RESEARCH Validation Arch."
        )


def test_check_2_secondary_threshold_01_05(check_2_pearson_df: pd.DataFrame) -> None:
    """Secondary threshold r >= 0.90 for MAF 0.01-0.05 (Validation Architecture §)."""
    bin_01_05 = check_2_pearson_df[check_2_pearson_df.maf_bin == "01_05"]
    for _, row in bin_01_05.iterrows():
        assert row.mean_r >= PASS_R_01_05, (
            f"region {row.region_id} secondary mean_r={row.mean_r} < "
            f"{PASS_R_01_05} at MAF 0.01-0.05"
        )
