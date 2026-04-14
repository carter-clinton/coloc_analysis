"""HLA negative control — scientific Layer 3 sanity check (T-09-21 mitigation).

After Plan 09-05 produces master_table.tsv, HLA-region signals (chr6:28-33Mb)
must fail the joint criterion in >= 3/4 cohorts. This is a scientific layer
check, not a unit test — it xfails pre-execution, skips if no HLA signals
entered Tier A/B/credible-set, and fails loud if HLA unexpectedly replicates.
"""
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_negative_controls_yaml_exists():
    """Phase 2 negative control YAML is reused by Phase 9 HLA check."""
    assert (PROJECT_ROOT / "config" / "negative_controls.yaml").exists()


def test_hla_fails_replication_joint():
    """Scientific Layer 3: HLA region fails joint criterion in ≥ 3/4 cohorts."""
    path = PROJECT_ROOT / "results" / "replication" / "master_table.tsv"
    if not path.exists():
        pytest.xfail("master_table.tsv not yet generated (pre-execution)")

    df = pd.read_csv(path, sep="\t")
    if "region" not in df.columns:
        pytest.xfail("master_table has no region column (pre-execution)")

    hla = df[df["region"].astype(str).str.contains(
        r"6:(28|29|30|31|32|33)", na=False, regex=True
    )]
    if len(hla) == 0:
        pytest.skip("No HLA signals in Tier A/B/credible-set — nothing to validate")

    # All {cohort}_replicated_joint_0.8 columns across finngen+gbmi_eur+gbmi_afr+mvp_eur+mvp_afr.
    joint_cols = [c for c in df.columns if c.endswith("_replicated_joint_0.8")]
    if not joint_cols:
        pytest.xfail("no *_replicated_joint_0.8 columns — pre-execution schema")

    # WR-11 fix: the previous `fillna(False).astype(bool) == False` counted
    # NaN AS False — so an all-NaN joint matrix (partial run, columns not
    # populated) trivially satisfied the assertion and masked genuine
    # regressions. Require that at least one cohort produced a non-NaN
    # joint flag per HLA row; otherwise xfail to signal "cannot validate".
    has_any_real = hla[joint_cols].notna().any(axis=1)
    if not has_any_real.all():
        pytest.xfail(
            f"{(~has_any_real).sum()} HLA rows have no populated "
            "*_replicated_joint_0.8 column — cannot validate scientific "
            "Layer 3 negative control (partial run?)"
        )
    # NaN treated as "neither True nor False" so it doesn't count as a fail.
    n_fail = (hla[joint_cols] == False).sum(axis=1)
    # ≥ 70% of HLA rows must fail in ≥3 cohorts (T-09-21)
    assert (n_fail >= 3).mean() > 0.7, (
        "HLA negative control unexpectedly replicates (scientific Layer 3 fail)"
    )
