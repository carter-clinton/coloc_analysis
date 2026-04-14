"""HLA negative control — RED until full pipeline run (scientific Layer 3).

Requires Phase 2's config/negative_controls.yaml (reused for Phase 9 HLA
locus negative test) and Plan 09-05 Task 2's master_table.tsv.
"""
from pathlib import Path

import pytest


def test_negative_controls_yaml_exists():
    assert Path("config/negative_controls.yaml").exists(), (
        "Phase 2 negative control YAML must be reusable"
    )


def test_hla_fails_placeholder():
    path = Path("results/replication/master_table.tsv")
    if not path.exists():
        pytest.xfail("master_table.tsv not yet generated (post Plan 09-05)")
    import pandas as pd

    df = pd.read_csv(path, sep="\t")
    hla_rows = df[df["region"].str.contains("6:28|6:29|6:30|6:31|6:32|6:33", na=False)]
    if len(hla_rows) == 0:
        pytest.skip(
            "No HLA signals in master_table — may be OK if none entered Tier A/B"
        )
    # Most HLA rows should fail the joint criterion in ≥3/4 cohorts
    fail_counts = (hla_rows.filter(regex="replicated_joint_0.8$") == False).sum(axis=1)
    assert (fail_counts >= 3).mean() > 0.7, "HLA negative control unexpectedly replicates"
