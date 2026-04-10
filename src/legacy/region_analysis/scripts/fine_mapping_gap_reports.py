#!/usr/bin/env python3
"""
Produce helper manifests describing fine-mapping LD gaps and variant-overflow issues.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional


def _to_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--summary",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
        help="Augmented finemap summary TSV (output of filter_finemap_summary.py).",
    )
    p.add_argument(
        "--ld-out",
        default="results/fine_mapping/ld_gaps.tsv",
        help="Output TSV listing trait×ancestry×region combos lacking usable LD.",
    )
    p.add_argument(
        "--overflow-out",
        default="results/fine_mapping/variant_overflow.tsv",
        help="Output TSV listing regions that exceeded variant limits or had zero variants.",
    )
    p.add_argument(
        "--susie-max-variants",
        type=int,
        default=6000,
        help="Threshold for highlighting regions that still have too many variants.",
    )
    return p.parse_args()


def load_summary(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Summary file not found: {path}")

    with path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit("Summary file missing header.")
        return list(reader)


def main() -> None:
    args = parse_args()
    summary = load_summary(Path(args.summary))

    ld_gap_rows: List[Dict[str, str]] = []
    overflow_rows: List[Dict[str, str]] = []

    for row in summary:
        trait = row.get("trait", "")
        ancestry = row.get("ancestry", "")
        region = row.get("region_id", "")
        status = row.get("status", "")
        ld_flag = row.get("ld_flag", "")
        n_snps = _to_int(row.get("n_snps"))
        region_total = _to_int(row.get("region_variant_total"))

        # LD gaps (anything that is not an actual LD matrix)
        if ld_flag not in {"used_ld"}:
            ld_gap_rows.append(
                {
                    "trait": trait,
                    "ancestry": ancestry,
                    "region_id": region,
                    "ld_flag": ld_flag,
                    "ld_status_raw": row.get("ld_status_raw", ""),
                    "ld_matrix_path": row.get("ld_matrix_path", ""),
                    "status": status,
                    "n_snps": n_snps if n_snps is not None else "",
                    "region_variant_total": region_total
                    if region_total is not None
                    else "",
                    "qc_notes": row.get("qc_notes", ""),
                }
            )

        too_many_variants = status == "too_many_variants"
        zero_variants = status == "no_variants"
        still_large = (
            False
            if region_total is None
            else region_total > args.susie_max_variants
        )

        if too_many_variants or zero_variants or still_large:
            overflow_rows.append(
                {
                    "trait": trait,
                    "ancestry": ancestry,
                    "region_id": region,
                    "status": status,
                    "region_variant_total": region_total
                    if region_total is not None
                    else "",
                    "susie_max_variants": args.susie_max_variants,
                    "n_snps": n_snps if n_snps is not None else "",
                    "qc_notes": row.get("qc_notes", ""),
                }
            )

    Path(args.ld_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.overflow_out).parent.mkdir(parents=True, exist_ok=True)

    def write_tsv(path: Path, rows: List[Dict[str, str]]) -> None:
        headers: List[str] = []
        for row in rows:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)
        if not headers:
            headers = ["trait", "ancestry", "region_id"]

        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(Path(args.ld_out), ld_gap_rows)
    write_tsv(Path(args.overflow_out), overflow_rows)


if __name__ == "__main__":
    main()
