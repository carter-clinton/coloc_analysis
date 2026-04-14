#!/usr/bin/env python3
"""Lift over GWAS summary statistics from GRCh38 to GRCh37.

Uses UCSC liftOver binary and hg38ToHg19.over.chain.gz.
Standalone script -- will be wired into a Snakemake rule in a later phase.

Usage:
    python liftover.py --input sumstats.tsv --output sumstats_hg19.tsv \
        --chain data/external/liftover/hg38ToHg19.over.chain.gz \
        [--liftover-bin liftOver] [--min-match 0.95]
"""

import argparse
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


@lru_cache(maxsize=4)
def _load_pyliftover(chain_file: str):
    """Load and cache a pyliftover LiftOver object per chain file."""
    from pyliftover import LiftOver

    return LiftOver(chain_file)


def liftover_coordinates(
    chain_file: str, chrom: str, pos: int
) -> Optional[Tuple[str, int]]:
    """Lift a single (chrom, pos) coordinate through a UCSC chain file.

    Pure-Python pyliftover implementation — avoids subprocess overhead when
    calling per-variant (callers that can batch should prefer
    :func:`liftover_sumstats` which uses the UCSC liftOver binary).

    Parameters
    ----------
    chain_file : str
        Path to UCSC chain file (e.g., hg38ToHg19.over.chain.gz).
    chrom : str
        Source chromosome (with or without 'chr' prefix).
    pos : int
        Source position, 1-based (GWAS convention).

    Returns
    -------
    (new_chrom, new_pos) tuple on success, or ``None`` if the coordinate
    cannot be lifted over. The returned chromosome has no ``chr`` prefix.
    """
    lo = _load_pyliftover(chain_file)
    chrom_str = str(chrom)
    chrom_pref = chrom_str if chrom_str.startswith("chr") else f"chr{chrom_str}"
    # pyliftover uses 0-based half-open coords; GWAS pos is 1-based.
    result = lo.convert_coordinate(chrom_pref, int(pos) - 1)
    if not result:
        return None
    new_chrom, new_pos0, _strand, _score = result[0]
    new_chrom = new_chrom.replace("chr", "")
    return (new_chrom, int(new_pos0) + 1)


def liftover_sumstats(
    input_path: str,
    output_path: str,
    chain_file: str,
    liftover_bin: str = "liftOver",
    min_match: float = 0.95,
) -> dict:
    """Convert GRCh38 coordinates in a sumstats TSV to GRCh37.

    Parameters
    ----------
    input_path : str
        Path to input sumstats TSV with at least CHR and POS columns.
    output_path : str
        Path for the output TSV with lifted coordinates.
    chain_file : str
        Path to UCSC chain file (e.g., hg38ToHg19.over.chain.gz).
    liftover_bin : str
        Path to the UCSC liftOver binary.
    min_match : float
        Minimum ratio of bases that must remap (default 0.95).

    Returns
    -------
    dict
        Summary statistics: total_variants, lifted, unmapped, lift_rate.
    """
    # 1. Read sumstats
    df = pd.read_csv(input_path, sep="\t", dtype={"CHR": str})

    if "CHR" not in df.columns or "POS" not in df.columns:
        raise ValueError(
            f"Input file must have CHR and POS columns. Found: {list(df.columns)}"
        )

    total = len(df)
    df["_original_index"] = range(total)

    # Normalise chromosome names: strip "chr" prefix if present, then add it
    df["_chr_bed"] = df["CHR"].astype(str).str.replace(r"^chr", "", regex=True)
    df["_chr_bed"] = "chr" + df["_chr_bed"]

    # 2. Create BED from CHR/POS (BED is 0-based, half-open)
    with tempfile.TemporaryDirectory() as tmpdir:
        bed_in = os.path.join(tmpdir, "input.bed")
        bed_out = os.path.join(tmpdir, "output.bed")
        bed_unmap = os.path.join(tmpdir, "unmapped.bed")

        with open(bed_in, "w") as fh:
            for idx, row in df.iterrows():
                pos = int(row["POS"])
                # BED: chrom, start (0-based), end (1-based), name (original index)
                fh.write(f"{row['_chr_bed']}\t{pos - 1}\t{pos}\t{row['_original_index']}\n")

        # 3. Run liftOver
        cmd = [
            liftover_bin,
            bed_in,
            chain_file,
            bed_out,
            bed_unmap,
            f"-minMatch={min_match}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"liftOver failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

        # 4. Map back lifted coordinates to sumstats
        lifted = pd.read_csv(
            bed_out,
            sep="\t",
            header=None,
            names=["chrom_lifted", "start_lifted", "end_lifted", "original_index"],
            dtype={"chrom_lifted": str},
        )
        lifted["original_index"] = lifted["original_index"].astype(int)
        # Convert back to 1-based POS
        lifted["POS_lifted"] = lifted["end_lifted"]
        lifted["CHR_lifted"] = lifted["chrom_lifted"].str.replace(r"^chr", "", regex=True)

        # Merge back
        lifted_idx = set(lifted["original_index"].tolist())
        df_lifted = df[df["_original_index"].isin(lifted_idx)].copy()

        # Map lifted coordinates
        lift_map = lifted.set_index("original_index")[["CHR_lifted", "POS_lifted"]]
        df_lifted = df_lifted.join(lift_map, on="_original_index")

        # Replace original CHR/POS with lifted values
        df_lifted["CHR"] = df_lifted["CHR_lifted"]
        df_lifted["POS"] = df_lifted["POS_lifted"]

        # Clean up temporary columns
        drop_cols = [
            "_original_index",
            "_chr_bed",
            "CHR_lifted",
            "POS_lifted",
        ]
        df_lifted = df_lifted.drop(columns=drop_cols, errors="ignore")

    # 5. Write output
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df_lifted.to_csv(output_path, sep="\t", index=False)

    n_lifted = len(df_lifted)
    n_unmapped = total - n_lifted
    lift_rate = n_lifted / total if total > 0 else 0.0

    summary = {
        "total_variants": total,
        "lifted": n_lifted,
        "unmapped": n_unmapped,
        "lift_rate": round(lift_rate, 4),
    }

    print(
        f"[liftover] {input_path}: {n_lifted}/{total} variants lifted "
        f"({lift_rate:.1%}), {n_unmapped} unmapped"
    )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Lift over GWAS summary statistics from GRCh38 to GRCh37"
    )
    parser.add_argument(
        "--input", required=True, help="Input sumstats TSV (GRCh38 coordinates)"
    )
    parser.add_argument(
        "--output", required=True, help="Output sumstats TSV (GRCh37 coordinates)"
    )
    parser.add_argument(
        "--chain",
        required=True,
        help="UCSC chain file (e.g., hg38ToHg19.over.chain.gz)",
    )
    parser.add_argument(
        "--liftover-bin",
        default="liftOver",
        help="Path to UCSC liftOver binary (default: liftOver)",
    )
    parser.add_argument(
        "--min-match",
        type=float,
        default=0.95,
        help="Minimum ratio of bases that must remap (default: 0.95)",
    )
    args = parser.parse_args()

    liftover_sumstats(
        input_path=args.input,
        output_path=args.output,
        chain_file=args.chain,
        liftover_bin=args.liftover_bin,
        min_match=args.min_match,
    )


if __name__ == "__main__":
    main()
