#!/usr/bin/env python3
"""Canonical-schema validator + liftover QC gate (Plan 09-02 Task 5).

Used by Snakemake rule `validate_harmonized_sumstats` to verify that a
harmonized TSV.gz:

  1. Contains all 10 canonical columns (CHR BP SNP EA OA BETA SE P EAF N).
  2. Passes the liftover QC check (drop_rate <= max_drop).

Exits 0 on success, 1 on any failure. When invoked as a library use
:func:`validate_schema` and :func:`check_liftover_qc` directly.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

CANONICAL = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def validate_schema(tsv_gz: Path) -> dict:
    """Read 100 header rows and confirm the canonical columns are present.

    Returns dict with keys: ``valid`` (bool), ``missing`` (list),
    ``columns`` (list of observed columns).
    """
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip", nrows=100)
    missing = [c for c in CANONICAL if c not in df.columns]
    return {
        "valid": not missing,
        "missing": missing,
        "columns": list(df.columns),
    }


def check_liftover_qc(qc_json: Path, max_drop: float = 0.05) -> bool:
    """Return True if ``drop_rate`` in the QC JSON is <= ``max_drop``.

    Missing ``drop_rate`` field is treated as 0 (cohorts with no liftover
    step, e.g. GBMI, still emit QC JSON with no drop_rate key).
    """
    qc = json.loads(Path(qc_json).read_text())
    return float(qc.get("drop_rate", 0)) <= max_drop


def _main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tsv", required=True, help="Harmonized tsv.gz path")
    ap.add_argument("--qc", default=None, help="Optional QC JSON")
    ap.add_argument("--max-drop", type=float, default=0.05)
    args = ap.parse_args()

    res = validate_schema(Path(args.tsv))
    if not res["valid"]:
        print(
            f"FAIL schema: missing {res['missing']}; "
            f"observed {res['columns']}"
        )
        return 1
    if args.qc and not check_liftover_qc(Path(args.qc), args.max_drop):
        print(f"FAIL liftover QC (drop_rate > {args.max_drop:.2%})")
        return 1
    print(f"OK {args.tsv}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
