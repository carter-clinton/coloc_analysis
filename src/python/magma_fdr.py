#!/usr/bin/env python3
"""Apply Benjamini-Hochberg FDR to a MAGMA gene-set analysis output.

Reads a MAGMA `.gsa.out` file (whitespace-delimited, comment-prefixed header
lines allowed) and writes a TSV with an appended FDR_Q column. FDR is applied
jointly across ALL gene sets in the file -- standard + custom + negative
controls -- per D-01a/D-01b.

Extracted from the previous `magma_fdr` Snakemake `run:` block (WR-07 fix).
Running in an isolated script lets the rule attach a `conda:` directive to
envs/magma.yml (which now pins pandas/scipy/statsmodels) instead of relying
on whichever packages happen to be in the host interpreter.

Usage:
    python magma_fdr.py --gsa INPUT.gsa.out --out OUTPUT.tsv
"""
import argparse
import sys
from io import StringIO


def apply_fdr(gsa_path: str, out_path: str) -> None:
    """Apply BH-FDR to a MAGMA .gsa.out file and write a TSV with FDR_Q."""
    import pandas as pd  # Imported lazily for testability.

    lines = []
    header = None
    with open(gsa_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if header is None:
                header = line
                continue
            lines.append(line)

    if not lines:
        with open(out_path, "w") as fout:
            fout.write("VARIABLE\tTYPE\tNGENES\tBETA\tBETA_STD\tSE\tP\tFDR_Q\n")
        return

    df = pd.read_csv(
        StringIO(header + "\n" + "\n".join(lines)),
        sep=r"\s+",
    )

    if "P" in df.columns and len(df) > 0:
        from statsmodels.stats.multitest import multipletests

        _, fdr_q, _, _ = multipletests(df["P"].values, method="fdr_bh")
        df["FDR_Q"] = fdr_q
    else:
        df["FDR_Q"] = float("nan")

    df.to_csv(out_path, sep="\t", index=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply BH-FDR across all gene sets in a MAGMA .gsa.out"
    )
    parser.add_argument("--gsa", required=True, help="Input .gsa.out path")
    parser.add_argument("--out", required=True, help="Output TSV path")
    args = parser.parse_args(argv)

    apply_fdr(args.gsa, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
