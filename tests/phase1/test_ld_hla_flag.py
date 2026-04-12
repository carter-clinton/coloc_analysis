"""Verify HLA_6p21 UKBB-LD panel carries the block-diagonal flag.

T-1-04 mitigation test (Plan 01-02 Task 1-02-03, scaffold RED-until-GREEN).

HLA_6p21 spans ~10 Mb, which crosses multiple 3 Mb UKBB-LD tiles. Cross-tile
LD is NOT available in the Weissbrod 2020 release, so Phase 1 approximates
the region via scipy.linalg.block_diag. This test guards that the
`.meta.json` sidecar written by download_ukbb_ld_tiles.py flags the
approximation via ld_source='ukbb_ld_tiled_block_diagonal'. The QC
dashboard (Plan 01-05) and methods fragment (Plan 01-06) consume this flag
to surface the statistical caveat to downstream readers.
"""
import json
import os
from pathlib import Path

import pytest

try:
    import pyreadr  # noqa: F401
    HAVE_PYREADR = True
except ImportError:
    HAVE_PYREADR = False

LD_REF_DIR = Path(os.environ.get("LD_REF_DIR", "data/processed/ld_reference"))
HLA_RDS = LD_REF_DIR / "EUR_ukbb_ld" / "HLA_6p21.rds"

pytestmark = pytest.mark.skipif(
    not HAVE_PYREADR,
    reason="pyreadr not installed (only materialized in ld_build env)",
)


def test_hla_block_diagonal():
    """HLA_6p21 sidecar must carry ld_source='ukbb_ld_tiled_block_diagonal'."""
    if not HLA_RDS.exists():
        pytest.skip(f"{HLA_RDS} not yet produced (Task 1-02-02 pending)")
    meta_path = HLA_RDS.with_suffix(".meta.json")
    assert meta_path.exists(), (
        f"sidecar {meta_path} missing -- Task 1-02-02 must write it"
    )
    meta = json.loads(meta_path.read_text())
    assert meta.get("ld_source") == "ukbb_ld_tiled_block_diagonal", (
        f"Expected block-diagonal flag, got: {meta.get('ld_source')!r}"
    )
    # Sanity: n_variants must be > 0 (HLA always has thousands of variants)
    assert meta.get("n_variants", 0) > 0, (
        f"HLA_6p21 meta reports n_variants={meta.get('n_variants')}"
    )
    # Multi-tile: tile_keys should list >= 2 keys
    tile_keys = meta.get("tile_keys", [])
    assert len(tile_keys) >= 2, (
        f"HLA_6p21 expected to span >=2 tiles, got tile_keys={tile_keys}"
    )
