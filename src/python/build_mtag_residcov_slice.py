#!/usr/bin/env python3
"""Slice the M2 LDSC bivariate-intercept matrix to a per-stratum residcov for MTAG.

Decision references:
  D-M2-10 (CRITICAL — flag is --residcov_path, NOT --overlap; verified in
           tools/mtag/.git_clone_log)
  D-M2-04 (LDSC bivariate-intercept matrix is the cohort-correlation R)
  D-M2-Q6 (_MIN_PER_STRATUM = 3 floor)
  D-M2-06 (skip-with-doc when stratum trait absent)

Pitfall references:
  Pitfall 1 — "--overlap" is colloquial shorthand; the actual MTAG flag is
              "--residcov_path".
  Pitfall 2 — MTAG calls np.loadtxt() on the matrix file; output MUST be
              bare numeric (no header row, no row index, whitespace
              delimited). Header / index would parse as data and fail.
  Pitfall 7 — silent mis-alignment if --sumstats trait order does not match
              residcov.txt row/col order. The sidecar
              residcov.trait_order.json is the alignment contract that the
              Snakemake rule reads to construct --sumstats deterministically.

Public API:

  slice_for_stratum(matrix, full_keys, stratum_keys, out_dir)
    Test-facing primary entry point. Accepts (a) an in-memory K_full x
    K_full numpy array AND (b) the column-order list `full_keys`, plus the
    target stratum subset `stratum_keys`. Slices to the K_strat x K_strat
    sub-matrix preserving the order of `stratum_keys` and writes:
      - {out_dir}/residcov.txt          (bare numeric, np.savetxt)
      - {out_dir}/residcov.trait_order.json  (sidecar with trait order)
    Returns (sliced_matrix, trait_order_list).

  slice_from_files(matrix_path, stratum, inventory_path, out_dir)
    Snakemake-rule entry point. Reads the indexed wide TSV at matrix_path
    (m1-03 reducer output), enumerates stratum trait keys via
    m2_stratum_keys.keys_for_stratum(), enforces the
    _MIN_PER_STRATUM = 3 floor (raises ValueError below floor), filters
    to keys present in the matrix index, sorts deterministically
    (lexicographic), defensively symmetrizes ((R + R.T) / 2), zero-fills
    any residual NaN cells (defensive — per-stratum slices are NaN-free
    given the M2 matrix), and delegates to slice_for_stratum() for the
    actual write. Returns (sliced_matrix, trait_order_list).

CLI:
  python -m build_mtag_residcov_slice \
      --matrix data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv \
      --stratum EUR \
      --inventory config/trait_inventory.yaml \
      --out-dir data/processed/mtag/EUR
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

# Make src/python importable for the m2_stratum_keys helper when invoked
# either as a module (python -m build_mtag_residcov_slice) or as a script
# (python src/python/build_mtag_residcov_slice.py).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from m2_stratum_keys import keys_for_stratum, _MIN_PER_STRATUM  # noqa: E402


# ---------------------------------------------------------------------------
# Primary test-facing API.
# ---------------------------------------------------------------------------

def slice_for_stratum(
    matrix: np.ndarray,
    full_keys: Sequence[str],
    stratum_keys: Sequence[str],
    out_dir: Path,
) -> tuple[np.ndarray, list[str]]:
    """Slice an in-memory K_full x K_full matrix to its K_strat x K_strat block.

    Order is preserved as given in `stratum_keys` (NOT re-sorted) — this is
    intentional so that the caller can control the row/col order to match
    its --sumstats list construction.

    Parameters
    ----------
    matrix : np.ndarray
        K_full x K_full square numeric matrix (LDSC bivariate-intercept
        output). NaN cells are tolerated and converted to 0.0 in the slice
        (per Wave 1 SUMMARY note: MTAG cannot ingest NaN; off-diagonal
        zero-fill is the documented downstream policy).
    full_keys : sequence[str]
        Trait keys aligned with `matrix` rows/cols (length K_full).
    stratum_keys : sequence[str]
        Subset of `full_keys` to slice; preserves the given order.
        Length K_strat.
    out_dir : Path
        Output directory. Created if missing. Receives:
          - residcov.txt (bare numeric K_strat x K_strat matrix)
          - residcov.trait_order.json (sidecar listing trait order)

    Returns
    -------
    (sliced, trait_order)
        sliced : np.ndarray of shape (K_strat, K_strat)
        trait_order : list[str] equal to list(stratum_keys)

    Raises
    ------
    ValueError
        If any element of stratum_keys is not in full_keys, or if matrix
        is not square / does not match len(full_keys).
    """
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            f"slice_for_stratum: matrix must be square 2-D; got shape {matrix.shape}"
        )
    if matrix.shape[0] != len(full_keys):
        raise ValueError(
            "slice_for_stratum: matrix shape does not match len(full_keys); "
            f"matrix is {matrix.shape}, len(full_keys)={len(full_keys)}"
        )
    full_keys = list(full_keys)
    stratum_keys = list(stratum_keys)
    missing = [k for k in stratum_keys if k not in full_keys]
    if missing:
        raise ValueError(
            "slice_for_stratum: stratum_keys not present in full_keys: "
            f"{missing}"
        )

    # Build index list in stratum_keys order (preserved).
    idx = [full_keys.index(k) for k in stratum_keys]
    sliced = matrix[np.ix_(idx, idx)]

    # Defensive NaN -> 0.0 (off-diagonal substitution per Wave 1 SUMMARY
    # policy; MTAG cannot ingest NaN). Diagonal is enforced 1.0 below.
    sliced = np.where(np.isnan(sliced), 0.0, sliced)

    # Defensive symmetrize.
    sliced = (sliced + sliced.T) / 2.0

    # Diagonal MUST be 1.0 (LDSC self-pair convention; Wave 1 already
    # enforces this but defend in case the upstream matrix changes).
    np.fill_diagonal(sliced, 1.0)

    # Write outputs.
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_matrix = out_dir / "residcov.txt"
    # Pitfall 2: NO header, NO index, whitespace-delimited.
    np.savetxt(out_matrix, sliced, fmt="%.10g", delimiter=" ")

    out_sidecar = out_dir / "residcov.trait_order.json"
    out_sidecar.write_text(
        json.dumps(
            {
                "trait_order": stratum_keys,
                "K": len(stratum_keys),
            },
            indent=2,
        )
        + "\n"
    )

    return sliced, list(stratum_keys)


# ---------------------------------------------------------------------------
# File-driven Snakemake-rule entry point.
# ---------------------------------------------------------------------------

def slice_from_files(
    matrix_path: Path,
    stratum: str,
    inventory_path: Path,
    out_dir: Path,
) -> tuple[np.ndarray, list[str]]:
    """Read the wide TSV, enumerate stratum keys, and slice.

    Snakemake-rule entry point. Wraps slice_for_stratum() with the I/O +
    floor-enforcement + sidecar-augmentation logic the production rule
    needs.

    Parameters
    ----------
    matrix_path : Path
        Path to the indexed wide TSV from m1_ldsc_rg_reduce
        (Wave-1 output: data/processed/ldsc_overlap/
        bivariate_intercept_matrix_2026-04-M2.tsv).
    stratum : str
        One of {"EUR", "AFR", "TRANS"}.
    inventory_path : Path
        Path to config/trait_inventory.yaml.
    out_dir : Path
        Output directory: data/processed/mtag/{stratum}.

    Returns
    -------
    (sliced, trait_order)

    Raises
    ------
    ValueError
        If the post-filter K is below _MIN_PER_STRATUM (D-M2-Q6 floor).
        Caller (Snakemake rule) catches this and emits a row to
        skipped_strata.tsv per D-M2-06.
    """
    import pandas as pd  # local import to keep numpy-only path light

    # 1. Read indexed wide TSV.
    M = pd.read_csv(matrix_path, sep="\t", index_col=0)
    full_keys = list(M.columns)
    matrix = M.values.astype(float)

    # 2. Enumerate stratum keys + intersect with matrix index.
    raw_stratum_keys = keys_for_stratum(Path(inventory_path), stratum)
    keys_in_matrix = sorted(
        k for k in raw_stratum_keys if k in M.index and k in M.columns
    )
    dropped = sorted(set(raw_stratum_keys) - set(keys_in_matrix))

    # 3. Floor enforcement (D-M2-Q6).
    K = len(keys_in_matrix)
    if K < _MIN_PER_STRATUM:
        raise ValueError(
            f"slice_from_files: stratum {stratum} has K={K} keys after "
            f"intersect with matrix; below floor _MIN_PER_STRATUM="
            f"{_MIN_PER_STRATUM} per D-M2-Q6. dropped_keys={dropped}"
        )

    # 4. Delegate to primary entry point (writes residcov.txt + sidecar).
    sliced, trait_order = slice_for_stratum(
        matrix, full_keys, keys_in_matrix, Path(out_dir)
    )

    # 5. Augment sidecar with provenance fields the Snakemake rule needs.
    sidecar_path = Path(out_dir) / "residcov.trait_order.json"
    payload = json.loads(sidecar_path.read_text())
    payload.update(
        {
            "stratum": stratum,
            "matrix_path": str(matrix_path),
            "inventory_path": str(inventory_path),
            "dropped_for_missing_matrix_row": dropped,
            "_MIN_PER_STRATUM": _MIN_PER_STRATUM,
        }
    )
    sidecar_path.write_text(json.dumps(payload, indent=2) + "\n")

    return sliced, trait_order


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def _main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Slice M2 LDSC bivariate-intercept matrix to per-stratum "
                    "residcov.txt + sidecar for MTAG --residcov_path."
    )
    ap.add_argument(
        "--matrix",
        type=Path,
        required=True,
        help="Indexed wide TSV from m1_ldsc_rg_reduce "
             "(M2 expanded ~26-trait matrix).",
    )
    ap.add_argument(
        "--stratum", required=True, choices=("EUR", "AFR", "TRANS")
    )
    ap.add_argument(
        "--inventory",
        type=Path,
        default=Path("config/trait_inventory.yaml"),
    )
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args(list(argv) if argv is not None else None)

    sliced, trait_order = slice_from_files(
        args.matrix, args.stratum, args.inventory, args.out_dir
    )
    print(
        f"build_mtag_residcov_slice: {args.stratum} "
        f"K={sliced.shape[0]}x{sliced.shape[1]}; "
        f"trait_order_head={trait_order[:3]}..."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
