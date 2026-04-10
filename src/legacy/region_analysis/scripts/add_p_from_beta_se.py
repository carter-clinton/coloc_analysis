#!/usr/bin/env python3
"""
Add a P column derived from BETA/SE for harmonized sumstats.

Writes an uncompressed TSV; caller should bgzip + tabix.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import List

import gzip


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input .tsv.bgz file.")
    parser.add_argument("--output", required=True, help="Output TSV (uncompressed).")
    return parser.parse_args()


def insert_p_column(header: List[str]) -> List[str]:
    if "P" in header:
        return header
    if "SE" in header:
        idx = header.index("SE") + 1
        return header[:idx] + ["P"] + header[idx:]
    # fallback: append
    return header + ["P"]


def compute_p(beta_str: str, se_str: str) -> str:
    try:
        beta = float(beta_str)
        se = float(se_str)
        if se == 0:
            return "1"
        z = beta / se
        if math.isinf(z) or math.isnan(z):
            return "1"
        p = math.erfc(abs(z) / math.sqrt(2.0))
        return f"{p:.6g}"
    except Exception:
        return "1"


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input: {input_path}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with gzip.open(input_path, "rt") as src, open(output_path, "w") as out:
        header_line = src.readline()
        if not header_line:
            raise SystemExit(f"Empty file: {input_path}")
        header = header_line.rstrip("\n").split("\t")
        out_header = insert_p_column(header)
        out.write("\t".join(out_header) + "\n")

        has_p = "P" in header
        try:
            idx_beta = header.index("BETA")
            idx_se = header.index("SE")
        except ValueError:
            idx_beta = None
            idx_se = None

        for line in src:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if has_p:
                out.write(line + "\n")
                continue
            if idx_beta is None or idx_se is None:
                # No BETA/SE; append empty P
                out.write(line + "\t\n")
                continue
            beta = parts[idx_beta] if idx_beta < len(parts) else ""
            se = parts[idx_se] if idx_se < len(parts) else ""
            p_val = compute_p(beta, se)
            # Insert P after SE when possible; otherwise append
            if "SE" in header:
                insert_at = header.index("SE") + 1
                out_parts = parts[:insert_at] + [p_val] + parts[insert_at:]
                out.write("\t".join(out_parts) + "\n")
            else:
                out.write(line + "\t" + p_val + "\n")


if __name__ == "__main__":
    main()
