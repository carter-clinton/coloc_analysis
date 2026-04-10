#!/usr/bin/env python3
"""
Generate tiled region definitions and variant lists to keep per-window variant counts under a threshold.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
from pathlib import Path
from typing import List


def to_safe(name: str) -> str:
    return name.replace("/", "_").replace(".", "_")


def load_regions(path: Path) -> List[dict]:
    with path.open() as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader if row.get("region_id")]


def load_variant_table(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for row in reader:
            chrom = str(row.get("CHR", "")).replace("chr", "").replace("CHR", "")
            pos = row.get("POS")
            if pos is None or pos == "":
                continue
            try:
                pos_int = int(float(pos))
            except ValueError:
                continue
            ref = row.get("REF") or "N"
            alt = row.get("ALT") or "N"
            rows.append({"CHR": chrom, "POS": pos_int, "REF": ref, "ALT": alt})
        return rows


def write_variant_table(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["CHR", "POS", "REF", "ALT"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions", required=True, help="Input curated regions CSV.")
    parser.add_argument("--variant-dir", required=True, help="Directory with full variant lists (per region_safe).")
    parser.add_argument("--output-regions", required=True, help="Output CSV with tiled regions.")
    parser.add_argument("--output-variants", required=True, help="Directory for tiled variant lists.")
    parser.add_argument("--max-variants", type=int, default=6000, help="Maximum variants per tile.")
    parser.add_argument("--pad-bp", type=int, default=0, help="Optional padding (bp) added to each tile boundary.")
    args = parser.parse_args()

    regions = load_regions(Path(args.regions))
    variant_dir = Path(args.variant_dir)
    output_regions_path = Path(args.output_regions)
    output_variant_dir = Path(args.output_variants)

    if output_variant_dir.exists():
        shutil.rmtree(output_variant_dir)
    output_variant_dir.mkdir(parents=True, exist_ok=True)

    tiled_rows: List[dict] = []
    for region in regions:
        region_id = region["region_id"]
        chrom = str(region["chr"]).replace("chr", "").replace("CHR", "")
        start = int(float(region["start"]))
        end = int(float(region["end"]))
        safe = to_safe(region_id)
        variant_path = variant_dir / f"{safe}.tsv"
        variants = load_variant_table(variant_path)
        total = len(variants)
        if total == 0:
            tile_defs = [(region_id, start, end, [])]
        else:
            tile_count = max(1, math.ceil(total / args.max_variants))
            chunk_size = math.ceil(total / tile_count)
            tile_defs = []
            for idx in range(tile_count):
                chunk = variants[idx * chunk_size : (idx + 1) * chunk_size]
                if not chunk:
                    continue
                chunk_start = chunk[0]["POS"]
                chunk_end = chunk[-1]["POS"]
                padded_start = max(start, chunk_start - args.pad_bp)
                padded_end = min(end, chunk_end + args.pad_bp)
                tile_id = region_id if tile_count == 1 else f"{region_id}__tile{idx + 1}"
                tile_defs.append((tile_id, padded_start, padded_end, chunk))

        for tile_id, tile_start, tile_end, chunk in tile_defs:
            if chunk:
                write_variant_table(output_variant_dir / f"{to_safe(tile_id)}.tsv", chunk)
            else:
                # still write empty file for consistency
                write_variant_table(output_variant_dir / f"{to_safe(tile_id)}.tsv", [])
            tiled_rows.append(
                {
                    "region_id": tile_id,
                    "chr": chrom,
                    "start": tile_start,
                    "end": tile_end,
                    "parent_region": region_id,
                }
            )

    with output_regions_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["region_id", "chr", "start", "end", "parent_region"])
        writer.writeheader()
        writer.writerows(tiled_rows)


if __name__ == "__main__":
    main()
