#!/usr/bin/env python3
"""Lift over curated GWAS regions from GRCh37 (hg19) to GRCh38 (hg38).

Reads config/regions_curated.csv (GRCh37 coordinates) and produces
config/regions_curated_grch38.csv with both GRCh37 and GRCh38 coordinates.

Uses the pyliftover library with the UCSC hg19ToHg38.over.chain.gz chain file.
Expected chain file size > 100 KB (T-02-01 tamper check).
Known-good md5 for hg19ToHg38.over.chain.gz: check UCSC golden path for current value.

Usage:
    python src/python/liftover_regions.py \
        --input config/regions_curated.csv \
        --output config/regions_curated_grch38.csv \
        --chain data/external/liftover/hg19ToHg38.over.chain.gz

If --chain is not provided or the chain file does not exist, the script
will attempt to download it from UCSC.

Requires: pyliftover (pip install pyliftover or conda install -c bioconda pyliftover)
"""

import argparse
import csv
import os
import sys
import urllib.request
from pathlib import Path


CHAIN_URL = "https://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz"
MIN_CHAIN_SIZE = 100_000  # T-02-01: chain file must be > 100 KB


def download_chain(dest: str) -> None:
    """Download hg19ToHg38 chain file from UCSC if not present."""
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[liftover_regions] Downloading chain file to {dest} ...")
    urllib.request.urlretrieve(CHAIN_URL, dest)
    size = dest_path.stat().st_size
    if size < MIN_CHAIN_SIZE:
        raise RuntimeError(
            f"Chain file too small ({size} bytes < {MIN_CHAIN_SIZE}). "
            "Possible download corruption or tampered file (T-02-01)."
        )
    print(f"[liftover_regions] Chain file downloaded: {size:,} bytes")


def lift_regions(input_path: str, output_path: str, chain_path: str) -> dict:
    """Lift all regions from GRCh37 to GRCh38.

    Parameters
    ----------
    input_path : str
        Path to regions_curated.csv (GRCh37).
    output_path : str
        Path for output CSV with both GRCh37 and GRCh38 coordinates.
    chain_path : str
        Path to hg19ToHg38.over.chain.gz.

    Returns
    -------
    dict
        Summary: total, lifted_ok, warned, failed.
    """
    from pyliftover import LiftOver

    lo = LiftOver(chain_path)

    with open(input_path, newline="") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    results = []
    stats = {"total": len(rows), "OK": 0, "WARN": 0, "FAIL": 0}

    for row in rows:
        chrom = row["chr"]
        start_37 = int(row["start"])
        end_37 = int(row["end"])
        size_37 = end_37 - start_37

        # pyliftover expects 'chrN' format
        chrom_str = f"chr{chrom}"

        # Lift start coordinate
        start_result = lo.convert_coordinate(chrom_str, start_37)
        # Lift end coordinate
        end_result = lo.convert_coordinate(chrom_str, end_37)

        if start_result and end_result:
            # Take first (highest confidence) result
            start_38 = start_result[0][1]
            end_38 = end_result[0][1]

            # Validate orientation
            if start_38 > end_38:
                start_38, end_38 = end_38, start_38

            size_38 = end_38 - start_38
            size_diff = abs(size_38 - size_37)

            if size_diff >= 100000:
                lift_status = "WARN"
                stats["WARN"] += 1
                print(
                    f"[liftover_regions] WARNING: {row['region_id']} size diff "
                    f"{size_diff:,} bp exceeds 100 kb sanity threshold"
                )
            else:
                lift_status = "OK"
                stats["OK"] += 1
        elif start_result or end_result:
            # Only one endpoint lifted
            start_38 = start_result[0][1] if start_result else ""
            end_38 = end_result[0][1] if end_result else ""
            lift_status = "WARN"
            stats["WARN"] += 1
            print(f"[liftover_regions] WARNING: {row['region_id']} partial lift")
        else:
            start_38 = ""
            end_38 = ""
            lift_status = "FAIL"
            stats["FAIL"] += 1
            print(f"[liftover_regions] FAIL: {row['region_id']} could not lift")

        results.append({
            "region_id": row["region_id"],
            "chr": chrom,
            "start_grch37": start_37,
            "end_grch37": end_37,
            "start_grch38": start_38,
            "end_grch38": end_38,
            "lead_snp": row["lead_snp"],
            "gene": row["gene"],
            "trait_list": row["trait_list"],
            "source": row["source"],
            "lift_status": lift_status,
        })

    # Write output
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "region_id", "chr", "start_grch37", "end_grch37",
        "start_grch38", "end_grch38", "lead_snp", "gene",
        "trait_list", "source", "lift_status",
    ]
    with open(output_path, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[liftover_regions] Wrote {len(results)} regions to {output_path}")
    print(
        f"[liftover_regions] OK={stats['OK']}, WARN={stats['WARN']}, "
        f"FAIL={stats['FAIL']}"
    )

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Lift curated GWAS regions from GRCh37 to GRCh38"
    )
    parser.add_argument(
        "--input",
        default="config/regions_curated.csv",
        help="Input regions CSV (GRCh37 coordinates)",
    )
    parser.add_argument(
        "--output",
        default="config/regions_curated_grch38.csv",
        help="Output regions CSV (with GRCh38 coordinates)",
    )
    parser.add_argument(
        "--chain",
        default="data/external/liftover/hg19ToHg38.over.chain.gz",
        help="UCSC chain file for hg19->hg38 liftover",
    )
    args = parser.parse_args()

    # Download chain file if not present
    if not Path(args.chain).exists():
        print(f"[liftover_regions] Chain file not found at {args.chain}")
        download_chain(args.chain)

    stats = lift_regions(args.input, args.output, args.chain)

    if stats["FAIL"] > 0:
        print(f"[liftover_regions] ERROR: {stats['FAIL']} regions failed to lift")
        sys.exit(1)


if __name__ == "__main__":
    main()
