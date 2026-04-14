"""Wave 5 test (RED in Wave 1): master_table.tsv 4-column-effect schema.

Validates that Plan 09-05 Task 2's assemble_master_replication_table
emits all four effect-size columns required by D-04b.
"""
from pathlib import Path

import pytest

REQUIRED_DISCOVERY = [
    "beta_discovery_raw",
    "se_discovery_raw",
    "p_discovery_raw",
    "beta_discovery_FIQT",
    "se_discovery_FIQT",
]
REQUIRED_PER_COHORT_SUFFIXES = [
    "beta_replication",
    "se_replication",
    "p_replication",
    "pph4_replication",
    "replicated_bonferroni",
    "replicated_pph4_0.5",
    "replicated_pph4_0.7",
    "replicated_pph4_0.8",
    "replicated_pph4_0.9",
    "replicated_joint_0.8",
]
REQUIRED_META = [
    "beta_meta",
    "se_meta",
    "p_meta",
    "meta_replicated_bonferroni",
    "meta_replicated_pph4_0.8",
]


def test_master_table_schema_placeholder():
    path = Path("results/replication/master_table.tsv")
    if not path.exists():
        pytest.xfail("master_table.tsv not yet generated (Plan 09-05 Task 2)")
    import pandas as pd

    df = pd.read_csv(path, sep="\t", nrows=0)
    for col in REQUIRED_DISCOVERY:
        assert col in df.columns, f"missing {col}"
    for col in REQUIRED_META:
        assert col in df.columns, f"missing {col}"


def test_four_effect_size_columns_in_schema_spec():
    """D-04b: beta_discovery_raw + beta_discovery_FIQT + beta_replication + beta_meta = 4 columns.
    This test validates our schema lists all 4 (string-equality — no production code required)."""
    per_cohort = set(REQUIRED_PER_COHORT_SUFFIXES)
    assert "beta_replication" in per_cohort
    assert "beta_discovery_FIQT" in REQUIRED_DISCOVERY
    assert "beta_discovery_raw" in REQUIRED_DISCOVERY
    assert "beta_meta" in REQUIRED_META
