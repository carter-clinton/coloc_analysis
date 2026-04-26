#!/usr/bin/env python3
"""Post-hoc max_FDR filter on MTAG per-trait outputs.

Decision references:
  D-M2-07 (max_FDR threshold = 0.05 per Turley 2018 default)
  D-M2-Q1 (post-hoc filter via mtag_maxFDR machinery; the vendored MTAG
           release exposes max-FDR computation through the main mtag.py
           --fdr flag rather than as a separate mtag_maxFDR.py script —
           this module wraps the post-hoc filter and per-trait
           augmentation logic the Snakemake rule needs)

VENDORED MTAG ANOMALY (recorded in m2-02-SUMMARY deviations):
  The plan's `mtag_maxFDR.py` reference assumed a separate post-hoc
  script. The pinned upstream JonJala/mtag commit
  9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc ships max-FDR computation
  inside mtag.py via the `--fdr` flag. The flag computes a SINGLE
  per-trait max-FDR scalar (saved to {out}_fdr_mat.txt) — there is no
  per-SNP `max_FDR` column in the standard `_trait_{N}.txt` output.

  The Wave 2 contract is: the Snakemake rule fires `mtag.py` with `--fdr`
  enabled; we then read the per-trait scalar from {out}_fdr_mat.txt and
  attach it as a constant `max_FDR` column to each `_trait_{N}.txt`. The
  per-trait file is then filtered by this module.

  This is the canonical implementation of "max_FDR filter per Turley 2018
  default 0.05" given the vendored MTAG release shape; the per-SNP
  max_FDR shorthand in the plan body is reconciled here.

Public API:

  filter_by_max_fdr(df, threshold=0.05) -> pd.DataFrame
    Filter test-facing primary entry point. Drops rows where max_FDR
    column is >= threshold. Preserves row order of survivors.

  filter_file(input_path, output_path, threshold=0.05) -> tuple[int, int]
    File-driven convenience wrapper for the Snakemake shell. Returns
    (n_input_rows, n_output_rows).

  attach_per_trait_max_fdr(input_path, output_path, max_fdr_value)
    Snakemake-rule helper. Reads MTAG `_trait_{N}.txt`, attaches a
    constant `max_FDR` column equal to `max_fdr_value`, writes to
    output_path. The per-trait scalar is read from the
    `{out}_fdr_mat.txt` file written by `mtag.py --fdr`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Pandas is the contract for the test (test_drops_rows_at_or_above_threshold
# constructs a pd.DataFrame and passes it in).
import pandas as pd

_DEFAULT_THRESHOLD = 0.05  # D-M2-07 Turley 2018 default.


def filter_by_max_fdr(
    df: pd.DataFrame, threshold: float = _DEFAULT_THRESHOLD
) -> pd.DataFrame:
    """Drop rows where max_FDR is at or above `threshold`.

    Per Turley 2018 Methods §"maxFDR" + D-M2-07: rows with `max_FDR < 0.05`
    are retained for downstream Class 1 novelty calling; rows with
    `max_FDR >= 0.05` are dropped.

    Parameters
    ----------
    df : pd.DataFrame
        Input MTAG per-trait DataFrame; MUST have a `max_FDR` column.
    threshold : float, default 0.05
        Drop threshold. Strict less-than semantics: rows kept iff
        max_FDR < threshold.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame; same column order as input.
    """
    if "max_FDR" not in df.columns:
        raise KeyError(
            "filter_by_max_fdr: input DataFrame missing 'max_FDR' column"
        )
    return df.loc[df["max_FDR"] < threshold].copy()


def attach_per_trait_max_fdr(
    input_path: Path,
    output_path: Path,
    max_fdr_value: float,
) -> int:
    """Attach a constant `max_FDR` column to a per-trait MTAG output.

    The vendored MTAG `--fdr` machinery emits a per-TRAIT scalar (one
    value per input trait), saved to `{out}_fdr_mat.txt`. This helper
    reads `{out}_trait_{N}.txt` and attaches that scalar as a column
    named `max_FDR` so the downstream `filter_by_max_fdr` semantics
    apply.

    Parameters
    ----------
    input_path : Path
        Path to MTAG `_trait_{N}.txt` (whitespace-delimited per save_mtag_results
        in tools/mtag/mtag.py — actually tab-separated from to_csv).
    output_path : Path
        Path to write the augmented file. Same format as input.
    max_fdr_value : float
        Per-trait scalar from the corresponding row of
        `{out}_fdr_mat.txt`.

    Returns
    -------
    int
        Number of rows written (== rows in input — this attach step does
        not filter).
    """
    df = pd.read_csv(input_path, sep="\t")
    df["max_FDR"] = float(max_fdr_value)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)
    return len(df)


def filter_file(
    input_path: Path,
    output_path: Path,
    threshold: float = _DEFAULT_THRESHOLD,
) -> tuple[int, int]:
    """File-driven convenience wrapper.

    Reads input_path (TSV with `max_FDR` column), filters via
    filter_by_max_fdr(), writes survivors to output_path.

    Returns (n_input, n_output).
    """
    df = pd.read_csv(input_path, sep="\t")
    n_in = len(df)
    out = filter_by_max_fdr(df, threshold=threshold)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, sep="\t", index=False)
    return n_in, len(out)


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser(
        "filter", help="Filter rows with max_FDR >= threshold"
    )
    f.add_argument("--input", type=Path, required=True)
    f.add_argument("--output", type=Path, required=True)
    f.add_argument(
        "--threshold", type=float, default=_DEFAULT_THRESHOLD
    )

    a = sub.add_parser(
        "attach",
        help="Attach a per-trait max_FDR scalar as a column to a trait file",
    )
    a.add_argument("--input", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a.add_argument("--value", type=float, required=True)

    args = ap.parse_args(argv)

    if args.cmd == "filter":
        n_in, n_out = filter_file(args.input, args.output, args.threshold)
        print(
            f"mtag_maxfdr_filter: {n_in} -> {n_out} rows "
            f"(dropped {n_in - n_out} at threshold {args.threshold})"
        )
        return 0
    if args.cmd == "attach":
        n = attach_per_trait_max_fdr(args.input, args.output, args.value)
        print(
            f"mtag_maxfdr_filter: attached max_FDR={args.value} to "
            f"{n} rows; wrote {args.output}"
        )
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_main())
