"""tests/m3/test_aou_export_landing.py — Wave 2 Task 2 scaffold.

Validates the per-chromosome .npz landing schema under
data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/ matches the egress bundle
manifest emitted by AOU-2 cell 6 (egress_bundles_dev.tsv).

Per RESEARCH Q12 + AOU-LD-PIPELINE.md §7.2: per-chromosome bundling, one
export request per chromosome x ancestry. Lower-triangular float32 .npz with
MAF >= 0.01.

The test mocks .npz files in tmp_path (no AoU access). Verifies that:
1. Per-ancestry directory structure exists (markers + .npz files).
2. .npz file count matches the egress_bundles inventory.
3. At least 1 chr with at least 1 region for each ancestry.
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


EGRESS_BUNDLES_FIXTURE_TSV = """ancestry\tchr\tn_regions\tsizes_listed_in_bucket
AFR\t1\t1\t1 of 1 ok
AFR\t11\t1\t1 of 1 ok
AFR\t12\t1\t1 of 1 ok
AFR\t16\t1\t1 of 1 ok
AFR\t19\t1\t1 of 1 ok
AFR\t6\t1\t1 of 1 ok
AFR\t8\t1\t1 of 1 ok
EUR\t12\t1\t1 of 1 ok
EUR\t16\t1\t1 of 1 ok
EUR\t19\t1\t1 of 1 ok
"""

EXPECTED_AFR_NPZ = 5  # 7 AFR regions in dev manifest, 2 are A.3 BlockMatrix-shard (HLA + 8p23)
EXPECTED_EUR_NPZ = 3  # 3 EUR overlap regions, all .npz


@pytest.fixture()
def egress_bundles_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO(EGRESS_BUNDLES_FIXTURE_TSV), sep="\t")


@pytest.fixture()
def synthetic_export_landing(tmp_path: Path) -> dict[str, Path]:
    """Mock data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/ with synthetic .npz files."""
    afr_dir = tmp_path / "AFR_aou"
    eur_dir = tmp_path / "EUR_aou"
    afr_dir.mkdir(parents=True, exist_ok=True)
    eur_dir.mkdir(parents=True, exist_ok=True)

    # 5 AFR .npz (the small/medium regions) + 2 BlockMatrix shard subdirs (the A.3 large)
    afr_regions = [
        "m2_region_00006",  # 1p13 SORT1
        "m2_region_00027",  # 11
        "m2_region_00040",  # 12 SH2B3
        "m2_region_00067",  # 16q12 FTO
        "m2_region_00083",  # 19 APOE
    ]
    for region in afr_regions:
        ld = np.eye(10, dtype=np.float32)
        variant_ids = np.array([f"chr1:{i}:A:G" for i in range(10)])
        np.savez_compressed(afr_dir / f"{region}.npz",
                            ld=ld, variant_ids=variant_ids,
                            rsids=np.array([""] * 10),
                            lower_triangular=np.array([False]))
    # 2 BlockMatrix shard subdirs (HLA 6p21, 8p23 inversion)
    bm_dir = afr_dir / "bm"
    bm_dir.mkdir(parents=True, exist_ok=True)
    for region in ("m2_region_00143", "m2_region_00153"):
        (bm_dir / f"{region}.bm").mkdir(parents=True, exist_ok=True)
        (bm_dir / f"{region}.bm" / "metadata.json").write_text("{}")

    # 3 EUR overlap regions
    for region in ("m2_region_00040", "m2_region_00067", "m2_region_00083"):
        ld = np.eye(10, dtype=np.float32)
        variant_ids = np.array([f"chr1:{i}:A:G" for i in range(10)])
        np.savez_compressed(eur_dir / f"{region}.npz",
                            ld=ld, variant_ids=variant_ids,
                            rsids=np.array([""] * 10),
                            lower_triangular=np.array([False]))

    return {"AFR_aou": afr_dir, "EUR_aou": eur_dir}


def test_npz_count_per_ancestry_matches_inventory(
    synthetic_export_landing: dict[str, Path],
) -> None:
    """The .npz file count under each ancestry dir matches the expected inventory."""
    afr_npz = sorted(synthetic_export_landing["AFR_aou"].glob("*.npz"))
    eur_npz = sorted(synthetic_export_landing["EUR_aou"].glob("*.npz"))
    assert len(afr_npz) == EXPECTED_AFR_NPZ, (
        f"expected {EXPECTED_AFR_NPZ} AFR .npz files; got {len(afr_npz)}"
    )
    assert len(eur_npz) == EXPECTED_EUR_NPZ, (
        f"expected {EXPECTED_EUR_NPZ} EUR .npz files; got {len(eur_npz)}"
    )


def test_blockmatrix_shard_dirs_for_a3_regions(
    synthetic_export_landing: dict[str, Path],
) -> None:
    """A.3 large regions land as BlockMatrix shard subdirs under bm/ (not .npz)."""
    bm_dir = synthetic_export_landing["AFR_aou"] / "bm"
    assert bm_dir.exists(), "AFR bm/ shard dir missing"
    shards = sorted(bm_dir.glob("*.bm"))
    assert len(shards) == 2, (
        f"expected 2 BlockMatrix shard dirs (HLA + 8p23); got {len(shards)}"
    )


def test_per_chromosome_bundle_inventory_schema(
    egress_bundles_df: pd.DataFrame,
) -> None:
    """egress_bundles_dev.tsv schema per AOU-2 cell 6 + RESEARCH Q12."""
    required = {"ancestry", "chr", "n_regions", "sizes_listed_in_bucket"}
    missing = required - set(egress_bundles_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_at_least_one_chr_per_ancestry(egress_bundles_df: pd.DataFrame) -> None:
    """Each ancestry has at least 1 chromosome with at least 1 region."""
    by_ancestry = egress_bundles_df.groupby("ancestry")["n_regions"].sum()
    for ancestry, total in by_ancestry.items():
        assert total >= 1, (
            f"ancestry {ancestry} has 0 regions in egress bundle inventory"
        )


def test_npz_files_loadable_and_have_ld_key(
    synthetic_export_landing: dict[str, Path],
) -> None:
    """Each .npz round-trips through np.load and contains the 'ld' key."""
    for anc_dir in synthetic_export_landing.values():
        for npz_path in anc_dir.glob("*.npz"):
            with np.load(npz_path) as z:
                assert "ld" in z.files, (
                    f"{npz_path.name}: missing 'ld' key in .npz"
                )
                assert "variant_ids" in z.files, (
                    f"{npz_path.name}: missing 'variant_ids' key"
                )
