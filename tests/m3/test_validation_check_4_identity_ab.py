"""tests/m3/test_validation_check_4_identity_ab.py — Wave 2 Task 2 scaffold.

Validates the Check 4 yield contrast table + MAF drop sanity table.

Per AOU-LD-PIPELINE.md §9.4 + RESEARCH Validation Architecture: Check 4
tabulates SuSiE-RSS yield (n_cs, median_cs_size, lead_pip, converged)
for 7 AFR regions x 2 LD sources (AoU AFR vs identity-placeholder) = 14
rows. Soft-expected: AoU LD lead PIP > identity LD lead PIP for >= 5 of
7 regions.

Per RESEARCH Q10: maf_drop.tsv tabulates per-region n_var counts at MAF
0.005 vs MAF 0.01. Halt threshold: max(per-region drop_ratio) <= 0.50.

Synthetic fixture: 14-row yield table + 7-row maf_drop table.
"""
from __future__ import annotations

import io

import pandas as pd
import pytest


YIELD_FIXTURE_TSV = """ancestry\tregion_id\tld_source\tconverged\tn_cs\tmedian_cs_size\tlead_pip
AFR\tm2_region_00006\taou_afr\tTrue\t2\t14\t0.42
AFR\tm2_region_00006\tidentity\tTrue\t1\t38\t0.18
AFR\tm2_region_00027\taou_afr\tTrue\t1\t10\t0.55
AFR\tm2_region_00027\tidentity\tTrue\t1\t29\t0.22
AFR\tm2_region_00040\taou_afr\tTrue\t3\t12\t0.61
AFR\tm2_region_00040\tidentity\tTrue\t1\t44\t0.31
AFR\tm2_region_00067\taou_afr\tTrue\t2\t9\t0.48
AFR\tm2_region_00067\tidentity\tTrue\t1\t31\t0.20
AFR\tm2_region_00083\taou_afr\tTrue\t2\t15\t0.39
AFR\tm2_region_00083\tidentity\tTrue\t1\t36\t0.17
AFR\tm2_region_00143\taou_afr\tTrue\t1\t22\t0.28
AFR\tm2_region_00143\tidentity\tTrue\t1\t27\t0.30
AFR\tm2_region_00153\taou_afr\tTrue\t2\t11\t0.45
AFR\tm2_region_00153\tidentity\tTrue\t1\t34\t0.21
"""

MAF_DROP_FIXTURE_TSV = """region_id\tn_var_maf_005\tn_var_maf_010\tdrop_ratio
m2_region_00006\t12000\t9500\t0.208
m2_region_00027\t9800\t8100\t0.173
m2_region_00040\t14500\t11200\t0.228
m2_region_00067\t11200\t9000\t0.196
m2_region_00083\t10100\t8200\t0.188
m2_region_00143\t18900\t15800\t0.164
m2_region_00153\t13400\t10800\t0.194
"""

EXPECTED_AFR_REGIONS = 7
SOFT_PASS_MIN = 5  # of 7 regions: AoU lead PIP > identity lead PIP
HALT_DROP_RATIO = 0.50


@pytest.fixture()
def yield_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(YIELD_FIXTURE_TSV), sep="\t")


@pytest.fixture()
def maf_drop_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(MAF_DROP_FIXTURE_TSV), sep="\t")


def test_yield_table_schema(yield_df: pd.DataFrame) -> None:
    required = {"ancestry", "region_id", "ld_source", "converged",
                "n_cs", "median_cs_size", "lead_pip"}
    missing = required - set(yield_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_yield_table_seven_regions_two_sources(yield_df: pd.DataFrame) -> None:
    """7 AFR regions x 2 LD sources = 14 rows; per-region both sources present."""
    assert len(yield_df) == EXPECTED_AFR_REGIONS * 2, (
        f"expected {EXPECTED_AFR_REGIONS * 2} rows; got {len(yield_df)}"
    )
    by_region = yield_df.groupby("region_id")["ld_source"].apply(set)
    for region_id, sources in by_region.items():
        assert sources == {"aou_afr", "identity"}, (
            f"region {region_id} sources={sources}; expected both"
        )


def test_check_4_yield_contrast(yield_df: pd.DataFrame) -> None:
    """For >= 5 of 7 AFR regions, AoU AFR lead PIP > identity LD lead PIP."""
    pivoted = yield_df.pivot(index="region_id", columns="ld_source",
                             values="lead_pip")
    aou_better = (pivoted["aou_afr"] > pivoted["identity"]).sum()
    assert aou_better >= SOFT_PASS_MIN, (
        f"only {aou_better} of {EXPECTED_AFR_REGIONS} regions show "
        f"AoU lead_pip > identity lead_pip; soft-expected >= {SOFT_PASS_MIN}"
    )


def test_check_4_yield_n_cs_and_median_populated(yield_df: pd.DataFrame) -> None:
    """n_cs and median_cs_size populated (non-null) per region per LD source."""
    assert yield_df.n_cs.notna().all(), "some n_cs values are null"
    assert yield_df.median_cs_size.notna().all(), (
        "some median_cs_size values are null"
    )


def test_check_4_maf_drop_schema(maf_drop_df: pd.DataFrame) -> None:
    required = {"region_id", "n_var_maf_005", "n_var_maf_010", "drop_ratio"}
    missing = required - set(maf_drop_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_check_4_maf_drop_under_halt_threshold(maf_drop_df: pd.DataFrame) -> None:
    """RESEARCH Q10 sanity: max(per-region drop ratio) <= 0.50."""
    max_drop = maf_drop_df.drop_ratio.max()
    assert max_drop <= HALT_DROP_RATIO, (
        f"max drop_ratio={max_drop} > {HALT_DROP_RATIO} halt threshold; "
        f"validation memo halts dev-fire signoff per RESEARCH Q10"
    )
