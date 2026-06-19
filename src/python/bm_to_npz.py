"""bm_to_npz.py -- Path A.3 helper: read a Hail BlockMatrix sharded directory
and emit a single lower-triangular .npz that ld_npz_to_rds.R can ingest.

Used by Wave 3 + Wave 4 for regions where compute_region_ld() chose Path A.3
(region_class in {large, xlarge}; > 10 Mb spans, n_var > ~100k -- driver
RAM cannot densify via to_numpy() on the AoU Dataproc driver). Per
RESEARCH Q5: large regions use BlockMatrix.write() to bucket inside the
Workbench; Carter then `gsutil cp -r` the sharded directory to NCSU GPFS at
``data/interim/aou_ld_exports/{ANCESTRY}_aou/bm/{region_id}.bm/`` and this
script converts the sharded directory to .npz for the standard ingest path.

Why not call this from inside the R converter?
  - Hail / pyspark are heavy (JVM 11 + spark 3.5 + ~3 GB on-disk env);
    the R converter env (envs/m3-r-ld.yml) intentionally does NOT carry
    Hail. This script is invoked only for the Path A.3 regions (n=36
    out of 161, per D-M3-09 region_class column) using envs/m3-aou-dev.yml.
  - Decoupling means the Path A.1 / A.2 small + medium regions go straight
    to the R converter without paying the Hail import cost.

Usage:
    python src/python/bm_to_npz.py \
        --bm-dir       data/interim/aou_ld_exports/AFR_aou/bm/m2_region_00120.bm \
        --variant-ids  data/interim/aou_ld_exports/AFR_aou/bm/m2_region_00120.variant_ids.tsv \
        --rsids        data/interim/aou_ld_exports/AFR_aou/bm/m2_region_00120.rsids.tsv \
        --out-npz      data/interim/aou_ld_exports/AFR_aou/m2_region_00120.npz

Sidecar TSVs (variant_ids, rsids) are emitted by AOU-2 alongside the
BlockMatrix at the AoU side; they encode variant ordering matching the
BlockMatrix rows/cols.

T-M3-EGR-W3 (info disclosure) disposition: ACCEPT. This script operates on
already-egressed BlockMatrix sharded directories (post-AoU classification
ruling); no AoU access required, no individual-level data exposed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def _load_sidecar(path: Path) -> np.ndarray:
    """Load a one-column TSV/text file as a 1-D string array (no header).

    WR-002 fix (2026-05-01): ``ndmin=1`` forces a 1-D array even when the
    TSV has exactly one row. Without it, np.loadtxt returns a 0-D scalar
    array for single-row files, which raises ``IndexError`` on the
    downstream ``shape[0]`` access. MIN_VARIANTS_PER_REGION=10 means Path
    A.3 should never produce a 1-variant region in production, but this
    helper is also reusable for non-region debugging paths.
    """
    if not path.is_file():
        raise FileNotFoundError(f"sidecar TSV missing: {path}")
    return np.loadtxt(str(path), dtype=str, delimiter="\t", ndmin=1)


def bm_to_npz(
    bm_dir: Path,
    variant_ids_tsv: Path,
    rsids_tsv: Path,
    out_npz: Path,
    block_size_hint: int | None = None,
) -> None:
    """Read a Hail BlockMatrix sharded directory + emit lower-triangular .npz.

    Args:
        bm_dir: Path to the sharded BlockMatrix directory (contains
            ``metadata.json``, ``parts/``).
        variant_ids_tsv: 1-column TSV of chr:pos:ref:alt variant IDs in
            BlockMatrix row order.
        rsids_tsv: 1-column TSV of rsids (or empty string for variants
            without an rsid) in BlockMatrix row order.
        out_npz: Destination .npz path (compressed).
        block_size_hint: Optional override for diagnostic prints.
    """
    # Hail import is intentionally inside the function so test discovery does
    # not require Hail; pytest.importorskip("hail") at the test layer keeps
    # the test suite green on environments without Hail (e.g., Track A NCSU
    # devboxes).
    import hail as hl  # noqa: WPS433 -- lazy import is correct here

    if not bm_dir.is_dir():
        raise FileNotFoundError(f"BlockMatrix directory missing: {bm_dir}")

    # init() is idempotent within a session; default GRCh38 matches AoU.
    if not hl.is_initialized():  # type: ignore[attr-defined]
        hl.init(default_reference="GRCh38", quiet=True)

    bm = hl.linalg.BlockMatrix.read(str(bm_dir))
    n_rows = bm.shape[0]
    n_cols = bm.shape[1]
    if n_rows != n_cols:
        raise ValueError(
            f"BlockMatrix is not square ({n_rows} x {n_cols}); LD must be square"
        )

    # to_numpy() loads the full dense matrix into driver RAM. Path A.3 hits
    # this only after the BlockMatrix has been *exported* to GPFS, so we are
    # bounded by NCSU GPFS RAM (typically 256+ GB on the LSF login head),
    # not by the AoU Dataproc driver. Still, we cast to float32 explicitly to
    # halve memory vs Hail's default float64.
    ld_dense = bm.to_numpy().astype("float32", copy=False)

    variant_ids = _load_sidecar(variant_ids_tsv)
    rsids = _load_sidecar(rsids_tsv)
    if variant_ids.shape[0] != n_rows:
        raise ValueError(
            f"variant_ids length {variant_ids.shape[0]} != BlockMatrix rows {n_rows}"
        )
    if rsids.shape[0] != n_rows:
        raise ValueError(
            f"rsids length {rsids.shape[0]} != BlockMatrix rows {n_rows}"
        )

    # Lower-triangular storage (matches AOU-LD-PIPELINE.md §7.2 export schema).
    # ld_npz_to_rds.R reconstructs symmetry via tri + t(tri) - diag(diag(tri)).
    lower = np.tril(ld_dense)

    # BR-01 fix (2026-06-19): write the `lower_triangular` flag so the reader
    # RECONSTRUCTS the upper triangle instead of HALVING the off-diagonals.
    # The CR-01 fix (ld_npz_to_rds.R / stitch_subregions_to_rds.R, commit
    # 3b2de9a) made this flag AUTHORITATIVE: the one-sided recovery
    # (tri + t(tri) - diag(diag(tri))) runs ONLY when lower_triangular == TRUE;
    # absent => defaulted FALSE => the matrix is treated as already-full and is
    # ONLY symmetrized (L + t(L))/2, which averages each populated r against a
    # structural 0 and HALVES every off-diagonal (0.6 -> 0.30). Path A.3 stores
    # np.tril(...) (lower only), so the flag MUST be present. This matches the
    # Path A.2 `_save_npz` convention in aou_ld_panel.py (lower_triangular=
    # np.array([lower_triangular])).
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(out_npz),
        ld=lower,
        variant_ids=variant_ids,
        rsids=rsids,
        lower_triangular=np.array([True]),
    )
    print(
        f"WROTE {out_npz} ({n_rows} x {n_rows}; "
        f"block_size={block_size_hint or 'default'})"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Hail BlockMatrix sharded directory -> lower-triangular .npz"
    )
    p.add_argument(
        "--bm-dir",
        required=True,
        type=Path,
        help="Path to Hail BlockMatrix sharded directory",
    )
    p.add_argument(
        "--variant-ids",
        dest="variant_ids_tsv",
        required=True,
        type=Path,
        help="1-column TSV of variant IDs (BlockMatrix row order)",
    )
    p.add_argument(
        "--rsids",
        dest="rsids_tsv",
        required=True,
        type=Path,
        help="1-column TSV of rsids (BlockMatrix row order; '' for missing)",
    )
    p.add_argument(
        "--out-npz",
        required=True,
        type=Path,
        help="Output .npz path",
    )
    p.add_argument(
        "--block-size-hint",
        type=int,
        default=None,
        help="Optional diagnostic block_size annotation (no functional effect)",
    )
    args = p.parse_args(argv)

    bm_to_npz(
        bm_dir=args.bm_dir,
        variant_ids_tsv=args.variant_ids_tsv,
        rsids_tsv=args.rsids_tsv,
        out_npz=args.out_npz,
        block_size_hint=args.block_size_hint,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
