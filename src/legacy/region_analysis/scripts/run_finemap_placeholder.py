#!/usr/bin/env python
import argparse
import csv
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Placeholder fine-mapping runner.")
    parser.add_argument("--sumstats", required=True)
    parser.add_argument("--trait", required=True)
    parser.add_argument("--ancestry", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--regions-csv", required=True)
    parser.add_argument("--ld-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def region_info(region_id: str, regions_csv: str) -> dict:
    with open(regions_csv, newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["region_id"] == region_id:
                return row
    raise ValueError(f"Region {region_id} not found in {regions_csv}")


def main():
    args = parse_args()
    info = region_info(args.region, args.regions_csv)
    result = {
        "trait": args.trait,
        "ancestry": args.ancestry,
        "method": args.method,
        "region_id": args.region,
        "chrom": info.get("chr"),
        "start": int(info.get("start", 0)),
        "end": int(info.get("end", 0)),
        "sumstats": args.sumstats,
        "ld_dir": args.ld_dir,
        "status": "placeholder",
        "notes": "Replace with real fine-mapping command.",
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
