"""tests/m3/test_validation_check_1_known_locus.py — Wave 2 Task 2 scaffold.

Validates the Check 1 invariants TSV schema + pass-threshold logic against a
synthetic 3-row fixture (FTO + SORT1 + a deliberate failure case).

Per AOU-LD-PIPELINE.md §9.1 + RESEARCH Validation Architecture: Check 1
emits per-region {region_id, block_start_kb, block_end_kb,
distance_to_published_kb}; pass = |distance_to_published_kb| <= 5 for the
known-locus rows (FTO rs1558902, SORT1 rs12740374).

The test runs entirely on a synthetic in-memory TSV — no AoU access.
"""
from __future__ import annotations

import io

import pandas as pd
import pytest


CHECK_1_FIXTURE_TSV = """region_id\tlead_rsid\tgene\tcyto\tblock_start_kb\tblock_end_kb\tdistance_to_published_kb\tpublished_paper
m2_region_00067\trs1558902\tFTO\t16q12\t53800.5\t54200.0\t1.2\tLocke 2015
m2_region_00006\trs12740374\tSORT1\t1p13\t109800.0\t110100.5\t-0.8\tTeslovich 2010
m2_region_99999\trs99999999\tFAKE\t99q99\t100.0\t110.0\t12.5\tFakePaper 2099
"""

PASS_THRESHOLD_KB = 5.0
KNOWN_LOCI = {"rs1558902", "rs12740374"}


@pytest.fixture()
def check_1_invariants_df() -> pd.DataFrame:
    """Synthetic Check 1 invariants TSV with 2 known-locus pass rows + 1 fail row."""
    return pd.read_csv(io.StringIO(CHECK_1_FIXTURE_TSV), sep="\t")


def test_check_1_invariants_schema(check_1_invariants_df: pd.DataFrame) -> None:
    """Required columns are present per AOU-LD-PIPELINE.md §9.1."""
    required = {"region_id", "lead_rsid", "gene", "cyto",
                "block_start_kb", "block_end_kb",
                "distance_to_published_kb", "published_paper"}
    missing = required - set(check_1_invariants_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_check_1_block_boundary_invariants(check_1_invariants_df: pd.DataFrame) -> None:
    """For each known-locus row (FTO + SORT1), |distance_to_published_kb| <= 5."""
    known_rows = check_1_invariants_df[
        check_1_invariants_df.lead_rsid.isin(KNOWN_LOCI)
    ]
    assert len(known_rows) == 2, (
        f"expected 2 known-locus rows (FTO + SORT1); got {len(known_rows)}"
    )
    for _, row in known_rows.iterrows():
        d = abs(float(row["distance_to_published_kb"]))
        assert d <= PASS_THRESHOLD_KB, (
            f"region {row.region_id} ({row.lead_rsid}/{row.gene}) "
            f"distance_to_published_kb={d} > {PASS_THRESHOLD_KB} threshold"
        )


def test_check_1_known_loci_present(check_1_invariants_df: pd.DataFrame) -> None:
    """Both rs1558902 (FTO) and rs12740374 (SORT1) are present."""
    rsids = set(check_1_invariants_df.lead_rsid)
    assert "rs1558902" in rsids, "FTO 16q12 lead rs1558902 missing"
    assert "rs12740374" in rsids, "SORT1 1p13 lead rs12740374 missing"


def test_check_1_block_boundaries_ordered(check_1_invariants_df: pd.DataFrame) -> None:
    """block_start_kb <= block_end_kb in every row."""
    for _, row in check_1_invariants_df.iterrows():
        assert row.block_start_kb <= row.block_end_kb, (
            f"region {row.region_id}: block_start_kb={row.block_start_kb} "
            f"> block_end_kb={row.block_end_kb}"
        )
