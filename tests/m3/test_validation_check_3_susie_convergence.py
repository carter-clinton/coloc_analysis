"""tests/m3/test_validation_check_3_susie_convergence.py — Wave 2 Task 2 scaffold.

Validates the Check 3 SuSiE-RSS convergence summary TSV.

Per AOU-LD-PIPELINE.md §9.3 + RESEARCH Validation Architecture: Check 3
runs susieR::susie_rss on FTO 16q12 (m2_region_00067) BMI AFR with L=10,
min_abs_corr=0.5 per config/susie_policy.yaml. Pass thresholds:
  converged == True, n_cs >= 1, median_cs_size <= 30, lead_pip >= 0.1
where lead_pip is the PIP at rs1558902.

Synthetic fixture: 1 row (the FTO 16q12 result).
"""
from __future__ import annotations

import io

import pandas as pd
import pytest


CHECK_3_FIXTURE_TSV = """region_id\tlead_rsid\tconverged\tn_cs\tmedian_cs_size\tlead_pip
m2_region_00067\trs1558902\tTrue\t2\t12\t0.34
"""

PASS_N_CS_MIN = 1
PASS_MEDIAN_CS_MAX = 30
PASS_LEAD_PIP_MIN = 0.1


@pytest.fixture()
def check_3_summary_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(CHECK_3_FIXTURE_TSV), sep="\t")


def test_check_3_schema(check_3_summary_df: pd.DataFrame) -> None:
    required = {"region_id", "lead_rsid", "converged",
                "n_cs", "median_cs_size", "lead_pip"}
    missing = required - set(check_3_summary_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_check_3_susie_convergence(check_3_summary_df: pd.DataFrame) -> None:
    """4 pass thresholds met for FTO 16q12 BMI AFR row."""
    row = check_3_summary_df.iloc[0]
    assert row.region_id == "m2_region_00067", (
        f"expected FTO 16q12 = m2_region_00067; got {row.region_id}"
    )
    assert row.lead_rsid == "rs1558902", (
        f"expected lead rs1558902; got {row.lead_rsid}"
    )
    assert bool(row.converged) is True, "SuSiE-RSS did not converge"
    assert row.n_cs >= PASS_N_CS_MIN, (
        f"n_cs={row.n_cs} < {PASS_N_CS_MIN} (no credible sets)"
    )
    assert row.median_cs_size <= PASS_MEDIAN_CS_MAX, (
        f"median_cs_size={row.median_cs_size} > {PASS_MEDIAN_CS_MAX}"
    )
    assert row.lead_pip >= PASS_LEAD_PIP_MIN, (
        f"lead PIP at rs1558902 = {row.lead_pip} < {PASS_LEAD_PIP_MIN}"
    )


def test_check_3_lead_variant_is_known(check_3_summary_df: pd.DataFrame) -> None:
    """The lead variant for FTO 16q12 BMI is rs1558902 (Locke 2015 / PAGE 2017)."""
    leads = set(check_3_summary_df.lead_rsid)
    assert "rs1558902" in leads, (
        "Check 3 must report PIP at the published FTO 16q12 lead rs1558902"
    )
