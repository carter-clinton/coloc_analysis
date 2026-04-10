#!/usr/bin/env python3
"""
Collect variants for a region using tabix (fast path for bgz + index).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def load_regions(path: Path) -> Dict[str, Dict[str, str]]:
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"No regions found in {path}")
    regions: Dict[str, Dict[str, str]] = {}
    for row in rows:
        region_id = row["region_id"]
        regions[region_id] = {
            "chr": str(row["chr"]).replace("chr", "").replace("CHR", ""),
            "start": int(float(row["start"])),
            "end": int(float(row["end"])),
        }
    return regions


def read_header(path: Path) -> List[str]:
    with gzip.open(path, "rt") as handle:
        header = handle.readline().strip().split("\t")
    return header


def extract_variants(
    harmonized_paths: Iterable[str],
    chrom: str,
    start: int,
    end: int,
    tabix_bin: str,
) -> List[Dict[str, str]]:
    chrom_clean = str(chrom)
    records = OrderedDict()
    region_spec = f"{chrom_clean}:{start}-{end}"

    for path in harmonized_paths:
        path_obj = Path(path)
        if not path_obj.exists():
            continue
        header = read_header(path_obj)
        idx = {name: i for i, name in enumerate(header)}
        if "CHR" not in idx or "POS" not in idx:
            continue
        idx_chr = idx["CHR"]
        idx_pos = idx["POS"]
        idx_ref = idx.get("REF")
        idx_alt = idx.get("ALT")
        idx_snp = idx.get("SNP_ID")

        cmd = [tabix_bin, str(path_obj), region_spec]
        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        except OSError:
            continue
        if proc.returncode != 0 or not proc.stdout:
            continue
        for line in proc.stdout.splitlines():
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) <= idx_pos:
                continue
            chr_val = parts[idx_chr]
            pos_val = parts[idx_pos]
            if chr_val is None or pos_val is None:
                continue
            try:
                pos_int = int(float(pos_val))
            except ValueError:
                continue
            ref_val = parts[idx_ref] if idx_ref is not None and idx_ref < len(parts) else "N"
            alt_val = parts[idx_alt] if idx_alt is not None and idx_alt < len(parts) else "N"
            snp_val = parts[idx_snp] if idx_snp is not None and idx_snp < len(parts) else ""
            snp_val = snp_val.strip()
            if snp_val.lower() == "na":
                snp_val = ""
            key = f"SNP::{snp_val}" if snp_val else f"POS::{chr_val}:{pos_int}:{ref_val}:{alt_val}"
            if key in records:
                continue
            records[key] = {
                "CHR": chr_val.replace("chr", "").replace("CHR", ""),
                "POS": pos_int,
                "REF": ref_val or "N",
                "ALT": alt_val or "N",
                "SNP_ID": snp_val,
            }
    return list(records.values())


def write_variant_list(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["CHR", "POS", "REF", "ALT", "SNP_ID"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: int(r.get("POS", 0))):
            writer.writerow(
                {
                    "CHR": row.get("CHR", ""),
                    "POS": row.get("POS", ""),
                    "REF": row.get("REF", "N"),
                    "ALT": row.get("ALT", "N"),
                    "SNP_ID": row.get("SNP_ID", ""),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-id", required=True, help="Region identifier to subset.")
    parser.add_argument("--regions-csv", required=True, help="CSV with region definitions.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized GWAS files.")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument("--tabix", default="tabix", help="Tabix binary path.")
    args = parser.parse_args()

    regions = load_regions(Path(args.regions_csv))
    if args.region_id not in regions:
        available = ", ".join(sorted(regions.keys()))
        raise KeyError(f"Region {args.region_id} not found. Available: {available}")
    region = regions[args.region_id]

    rows = extract_variants(
        harmonized_paths=args.harmonized,
        chrom=region["chr"],
        start=region["start"],
        end=region["end"],
        tabix_bin=args.tabix,
    )
    write_variant_list(Path(args.output), rows)


if __name__ == "__main__":
    main()
