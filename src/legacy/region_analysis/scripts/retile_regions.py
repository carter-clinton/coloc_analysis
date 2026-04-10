#!/usr/bin/env python3
"""
Retile selected base regions using existing variant lists.

This updates the regions CSV and rewrites variant lists for the new tiles.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


def to_safe(name: str) -> str:
    return name.replace("/", "_").replace(".", "_")


def load_regions(path: Path) -> List[Dict[str, str]]:
    with path.open() as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def write_regions(path: Path, rows: Sequence[Dict[str, str]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_variants(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for row in reader:
            chrom = str(row.get("CHR", "")).replace("chr", "").replace("CHR", "")
            pos = row.get("POS")
            if not chrom or pos is None or pos == "":
                continue
            try:
                pos_int = int(float(pos))
            except ValueError:
                continue
            ref = row.get("REF") or "N"
            alt = row.get("ALT") or "N"
            snp_id = row.get("SNP_ID") or ""
            rows.append(
                {
                    "CHR": chrom,
                    "POS": pos_int,
                    "REF": ref,
                    "ALT": alt,
                    "SNP_ID": snp_id,
                }
            )
        return rows


def dedupe_variants(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    unique = []
    for row in rows:
        key = (
            row.get("CHR", ""),
            int(row.get("POS", 0)),
            str(row.get("REF", "")),
            str(row.get("ALT", "")),
            str(row.get("SNP_ID", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    unique.sort(key=lambda r: int(r["POS"]))
    return unique


def write_variant_list(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["CHR", "POS", "REF", "ALT", "SNP_ID"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "CHR": row.get("CHR", ""),
                    "POS": row.get("POS", ""),
                    "REF": row.get("REF", "N"),
                    "ALT": row.get("ALT", "N"),
                    "SNP_ID": row.get("SNP_ID", ""),
                }
            )


def parse_base_regions(args: argparse.Namespace) -> List[str]:
    regions: List[str] = []
    if args.base_regions:
        for item in args.base_regions.split(","):
            item = item.strip()
            if item:
                regions.append(item)
    if args.base_regions_file:
        for line in Path(args.base_regions_file).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            regions.append(line)
    return sorted(set(regions))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regions-csv", required=True, help="Input regions CSV.")
    parser.add_argument(
        "--variant-dir",
        required=True,
        help="Directory containing per-tile variant lists.",
    )
    parser.add_argument("--base-regions", help="Comma-separated base region IDs.")
    parser.add_argument("--base-regions-file", help="File with one base region per line.")
    parser.add_argument("--max-variants", type=int, default=3000, help="Target max variants per tile.")
    parser.add_argument("--pad-bp", type=int, default=0, help="Padding around tile boundaries.")
    parser.add_argument(
        "--output-regions",
        help="Output regions CSV (defaults to overwrite input).",
    )
    parser.add_argument(
        "--output-variant-dir",
        help="Output variant list directory (defaults to input variant dir).",
    )
    parser.add_argument(
        "--keep-old-variants",
        action="store_true",
        help="Do not remove old variant lists for retiled regions.",
    )
    args = parser.parse_args()

    base_regions = parse_base_regions(args)
    if not base_regions:
        raise SystemExit("No base regions provided.")

    regions_path = Path(args.regions_csv)
    rows = load_regions(regions_path)
    if not rows:
        raise SystemExit(f"No rows found in {regions_path}")
    fieldnames = list(rows[0].keys())
    if "parent_region" not in fieldnames:
        raise SystemExit("regions CSV must include parent_region column")

    variant_dir = Path(args.variant_dir)
    output_variant_dir = Path(args.output_variant_dir) if args.output_variant_dir else variant_dir

    # Index rows by parent_region
    by_parent: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        parent = row.get("parent_region") or row.get("region_id")
        by_parent.setdefault(parent, []).append(row)

    new_rows: List[Dict[str, str]] = []
    removed_safe: List[str] = []
    new_safe: set[str] = set()
    for row in rows:
        parent = row.get("parent_region") or row.get("region_id")
        if parent not in base_regions:
            new_rows.append(row)
        else:
            removed_safe.append(to_safe(row.get("region_id", "")))

    for base_region in base_regions:
        region_rows = by_parent.get(base_region, [])
        if not region_rows:
            print(f"[retile] Warning: base region {base_region} not found in regions CSV.", file=sys.stderr)
            continue
        starts = [int(float(r["start"])) for r in region_rows]
        ends = [int(float(r["end"])) for r in region_rows]
        chrom = str(region_rows[0]["chr"]).replace("chr", "").replace("CHR", "")
        base_start = min(starts)
        base_end = max(ends)

        variants = []
        for row in region_rows:
            safe = to_safe(row["region_id"])
            path = variant_dir / f"{safe}.tsv"
            variants.extend(load_variants(path))
        if not variants:
            # Fallback to a base-region variant list if tile lists are missing.
            base_safe = to_safe(base_region)
            base_path = variant_dir / f"{base_safe}.tsv"
            variants.extend(load_variants(base_path))
        variants = dedupe_variants(variants)
        total = len(variants)
        if total == 0:
            tile_defs = [(base_region, base_start, base_end, [])]
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
                padded_start = max(base_start, chunk_start - args.pad_bp)
                padded_end = min(base_end, chunk_end + args.pad_bp)
                tile_id = base_region if tile_count == 1 else f"{base_region}__tile{idx + 1}"
                tile_defs.append((tile_id, padded_start, padded_end, chunk))

        for tile_id, tile_start, tile_end, chunk in tile_defs:
            new_rows.append(
                {
                    "region_id": tile_id,
                    "chr": chrom,
                    "start": tile_start,
                    "end": tile_end,
                    "parent_region": base_region,
                }
            )
            safe_tile = to_safe(tile_id)
            new_safe.add(safe_tile)
            output_variant_path = output_variant_dir / f"{safe_tile}.tsv"
            write_variant_list(output_variant_path, chunk)

    if not args.keep_old_variants:
        for safe in removed_safe:
            if safe in new_safe:
                continue
            old_path = output_variant_dir / f"{safe}.tsv"
            if old_path.exists():
                old_path.unlink()

    output_regions = Path(args.output_regions) if args.output_regions else regions_path
    write_regions(output_regions, new_rows, fieldnames)
    print(f"[retile] Wrote {len(new_rows)} region rows to {output_regions}")


if __name__ == "__main__":
    main()
