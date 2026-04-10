#!/usr/bin/env python3
"""
Down-sample a region-level variant list to a maximum number of variants.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import List


def thin_indices(total: int, max_variants: int) -> List[int]:
    if max_variants <= 0:
        raise ValueError("max_variants must be > 0")
    if total <= max_variants:
        return list(range(total))
    step = math.ceil(total / max_variants)
    idx = list(range(0, total, step))
    return idx[:max_variants]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input variant TSV (CHR,POS,REF,ALT).")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument(
        "--max-variants",
        type=int,
        default=6000,
        help="Maximum number of variants to retain.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise FileNotFoundError(f"Input variant list not found: {input_path}")

    with input_path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"Input file {input_path} missing header")
        fieldnames = [name.strip() for name in fieldnames]
        required_cols = {"CHR", "POS", "REF", "ALT"}
        missing = required_cols.difference(fieldnames)
        base_fieldnames = list(fieldnames)
        for col in required_cols:
            if col not in base_fieldnames:
                base_fieldnames.append(col)
        rows = list(reader)

    if not rows:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=base_fieldnames, delimiter="\t")
            writer.writeheader()
        return

    indices = thin_indices(len(rows), args.max_variants)
    selected = []
    for i in indices:
        row = rows[i].copy()
        if "REF" not in row:
            row["REF"] = "N"
        if "ALT" not in row:
            row["ALT"] = "N"
        selected.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=base_fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(selected)


if __name__ == "__main__":
    main()
