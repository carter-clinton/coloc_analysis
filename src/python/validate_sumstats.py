#!/usr/bin/env python3
"""Validate that harmonized sumstats contain required columns.

Stub validation script -- confirms the harmonized output has the expected
column schema before downstream rules consume it.
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path


REQUIRED_COLUMNS = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Harmonized sumstats (.tsv.bgz)")
    parser.add_argument("--output", required=True, help="Validation report TSV")
    parser.add_argument("--trait", required=True, help="Trait name")
    parser.add_argument("--ancestry", required=True, help="Ancestry label")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with gzip.open(args.input, "rt") as f:
        header = f.readline().strip().split("\t")

    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    status = "PASS" if not missing else "FAIL"

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as out:
        out.write("trait\tancestry\tstatus\tmissing_columns\n")
        out.write(f"{args.trait}\t{args.ancestry}\t{status}\t{','.join(missing)}\n")

    if missing:
        print(f"WARNING: Missing columns: {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
