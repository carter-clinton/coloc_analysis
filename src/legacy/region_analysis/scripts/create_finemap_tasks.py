#!/usr/bin/env python
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any

from scripts.manifest_utils import parse_trait_ancestry


def parse_args():
    parser = argparse.ArgumentParser(description="Enumerate region-level fine-mapping jobs.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized sumstats files.")
    parser.add_argument("--regions", required=True, help="Curated regions CSV.")
    parser.add_argument("--methods", required=True, help="Comma-separated list of fine-mapping methods.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_regions(path: str) -> List[Dict[str, Any]]:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    required = {"region_id", "chr", "start", "end"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}")
    return rows


def main():
    args = parse_args()
    regions = load_regions(args.regions)
    methods: List[str] = [m.strip() for m in args.methods.split(",") if m.strip()]
    records = []
    for sumstats_path in args.harmonized:
        trait, ancestry = parse_trait_ancestry(Path(sumstats_path).name)
        for row in regions:
            for method in methods:
                records.append(
                    {
                        "trait": trait,
                        "ancestry": ancestry,
                        "method": method,
                        "region_id": row["region_id"],
                        "chr": row["chr"],
                        "start": row["start"],
                        "end": row["end"],
                        "sumstats_path": sumstats_path,
                    }
                )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["trait", "ancestry", "method", "region_id", "chr", "start", "end", "sumstats_path"]
    with open(out_path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for record in records:
            writer.writerow(record)


if __name__ == "__main__":
    main()
