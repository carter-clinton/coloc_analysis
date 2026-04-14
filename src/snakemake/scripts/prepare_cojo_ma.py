"""Plan 09-05 Task 1 — convert canonical harmonized sumstats to GCTA .ma format.

GCTA's --cojo-file expects a whitespace-delimited file with columns:
    SNP A1 A2 freq b se p N

where A1 is the effect allele (matches EA in canonical) and A2 is the other
allele. This wrapper filters to a single GRCh37 locus (chr:start-end) and
emits the .ma file expected by run_cojo.sh / rule run_cojo_slct.

Scope: one locus per call; the driver (rule prepare_cojo_ma in
replication.smk) unrolls over (cohort, trait, locus) wildcards.

CLI:
    python prepare_cojo_ma.py \
        --sumstats <canonical.tsv[.gz]> \
        --region chr10:100000-300000 \
        --out <out.ma>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

import pandas as pd

CANONICAL_REQUIRED = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _parse_region(region: str) -> tuple[str, int, int]:
    """Parse a 'chr10:100-300' region spec. Leading 'chr' optional."""
    chrom_raw, range_ = region.split(":", 1)
    start_str, end_str = range_.split("-", 1)
    chrom = chrom_raw[3:] if chrom_raw.lower().startswith("chr") else chrom_raw
    return chrom, int(start_str), int(end_str)


def canonical_to_ma(
    canonical_tsv: Union[str, Path],
    locus_region: str,
    output_ma: Union[str, Path],
) -> int:
    """Filter canonical sumstats to `locus_region` and emit GCTA .ma format.

    Returns the number of SNPs written.
    """
    canonical_tsv = Path(canonical_tsv)
    output_ma = Path(output_ma)
    output_ma.parent.mkdir(parents=True, exist_ok=True)

    compression = "gzip" if str(canonical_tsv).endswith(".gz") else None
    df = pd.read_csv(canonical_tsv, sep="\t", compression=compression)

    missing = [c for c in CANONICAL_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(
            f"canonical sumstats {canonical_tsv} missing columns: {missing}"
        )

    chrom, start, end = _parse_region(locus_region)
    in_region = df[
        (df["CHR"].astype(str) == str(chrom))
        & (df["BP"].astype(int) >= start)
        & (df["BP"].astype(int) <= end)
    ]

    ma = pd.DataFrame({
        "SNP": in_region["SNP"],
        "A1": in_region["EA"],
        "A2": in_region["OA"],
        "freq": in_region["EAF"],
        "b": in_region["BETA"],
        "se": in_region["SE"],
        "p": in_region["P"],
        "N": in_region["N"],
    })
    ma.to_csv(output_ma, sep=" ", index=False)
    return len(ma)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sumstats", required=True,
                   help="canonical harmonized sumstats TSV (optionally .gz)")
    p.add_argument("--region", required=True,
                   help="locus in chr:start-end format (GRCh37)")
    p.add_argument("--out", required=True,
                   help="output .ma path (GCTA 8-column format)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    n = canonical_to_ma(a.sumstats, a.region, a.out)
    print(f"wrote {n} SNPs to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
