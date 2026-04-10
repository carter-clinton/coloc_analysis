#!/usr/bin/env python
#!/usr/bin/env python
"""
Summarize how many harmonized variants fall inside each curated region for every
trait/ancestry combination. Streams through each bgzip-compressed TSV in chunks
to avoid loading the entire file into memory or relying on external tabix
binaries—everything runs through pandas/numpy only.
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import parse_trait_ancestry


def load_regions(path: Path) -> List[Dict[str, object]]:
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    required = {"region_id", "chr", "start", "end"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Regions file missing columns: {missing}")
    cleaned = []
    for row in rows:
        cleaned.append(
            {
                "region_id": row["region_id"],
                "chr": str(row["chr"]).replace("chr", "").replace("CHR", ""),
                "start": int(float(row["start"])),
                "end": int(float(row["end"])),
            }
        )
    return cleaned


def summarize_file(
    harmonized_path: Path,
    regions: Iterable[Dict[str, object]],
    chunksize: int = 500_000,
) -> List[Dict[str, object]]:
    trait, ancestry = parse_trait_ancestry(harmonized_path.name)
    regions = list(regions)
    regions_by_chr: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for region in regions:
        regions_by_chr[region["chr"]].append(region)

    counts = {region["region_id"]: 0 for region in regions}

    usecols = ["CHR", "POS"]
    for chunk in pd.read_csv(
        harmonized_path,
        sep="\t",
        compression="gzip",
        usecols=usecols,
        chunksize=chunksize,
    ):
        if chunk.empty:
            continue
        chunk = chunk.dropna(subset=["CHR", "POS"])
        if chunk.empty:
            continue
        chunk["CHR"] = chunk["CHR"].astype(str).str.replace("^chr", "", regex=True)
        chunk["POS"] = pd.to_numeric(chunk["POS"], errors="coerce")
        chunk = chunk.dropna(subset=["POS"])
        if chunk.empty:
            continue

        for chrom, chrom_df in chunk.groupby("CHR"):
            chrom_regions = regions_by_chr.get(chrom)
            if not chrom_regions:
                continue
            positions: np.ndarray = chrom_df["POS"].to_numpy()
            for region in chrom_regions:
                start = region["start"]
                end = region["end"]
                mask = (positions >= start) & (positions <= end)
                counts[region["region_id"]] += int(mask.sum())

    records: List[Dict[str, object]] = []
    for region in regions:
        count = counts.get(region["region_id"], 0)
        records.append(
            {
                "trait": trait,
                "ancestry": ancestry,
                "region_id": region["region_id"],
                "chrom": region["chr"],
                "start": region["start"],
                "end": region["end"],
                "variant_count": count,
                "has_variants": bool(count),
                "harmonized_path": str(harmonized_path),
            }
        )
    return records


def main():
    parser = argparse.ArgumentParser(description="Check region coverage for harmonized GWAS files.")
    parser.add_argument("--regions", required=True, help="Curated region CSV.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized TSV.BGZ files.")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument("--chunksize", type=int, default=500_000, help="Rows per streaming chunk.")
    args = parser.parse_args()

    regions = load_regions(Path(args.regions))
    rows: List[Dict[str, object]] = []
    for path in args.harmonized:
        rows.extend(summarize_file(Path(path), regions, chunksize=args.chunksize))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "trait",
                "ancestry",
                "region_id",
                "chrom",
                "start",
                "end",
                "variant_count",
                "has_variants",
                "harmonized_path",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
