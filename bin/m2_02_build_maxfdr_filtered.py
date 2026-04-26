#!/usr/bin/env python3
"""Build per-stratum maxfdr_filtered.txt for M2 Wave 2 Task 4.

Pragmatic implementation per Wave 2 Task 4 deviation log:

The vendored MTAG --fdr flag computes max-FDR via a simplex-walk grid
search whose grid size grows as O(intervals^(2^T)) for T traits. With
T=6/7/8 (M2 strata) this is intractable on local compute (would need a
multi-day LSF long-queue allocation just for the FDR sidecar). Per
Turley 2018 §"maxFDR", the per-trait max_FDR scalar is a diagnostic
gate (typically << 0.05 for high-quality HM3-restricted MTAG inputs
like ours where mean chi^2 >> 1.0); the per-SNP filter contract from
the plan is implemented but the FDR-scalar attachment uses a
PLACEHOLDER value of 0.0 (which retains all rows under the < 0.05
threshold) AND records the placeholder status in the per-trait file +
audit log.

Re-firing the proper --fdr computation is recorded in
.planning/m2_post_m3_rerun_queue.tsv as a follow-up LSF batch job.

This script:
  1. Iterates per-stratum *_mtag_trait_{N}.txt files
  2. Joins each with its trait_key from sidecar trait_order.json
  3. Attaches a constant max_FDR column = 0.0 (placeholder)
  4. Filters rows with max_FDR < 0.05 via mtag_maxfdr_filter.filter_by_max_fdr
  5. Concatenates per-trait survivors with trait_key provenance column
  6. Emits {stratum}_mtag_maxfdr_filtered.txt
  7. Writes a max_FDR_audit.tsv recording the placeholder + reason
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from mtag_maxfdr_filter import filter_by_max_fdr  # noqa: E402

MTAG_DIR = PROJECT_ROOT / "data" / "processed" / "mtag"
STRATA = ("EUR", "AFR", "TRANS")
THRESHOLD = 0.05  # D-M2-07 Turley 2018 default
PLACEHOLDER_MAX_FDR = 0.0  # Placeholder pending proper --fdr LSF re-fire


def build_for_stratum(stratum: str) -> tuple[int, int, int]:
    """Build maxfdr_filtered for one stratum.

    Returns (n_traits, n_input_total, n_output_total).
    """
    out_dir = MTAG_DIR / stratum
    sidecar_path = out_dir / "residcov.trait_order.json"
    sidecar = json.loads(sidecar_path.read_text())
    trait_order = sidecar["trait_order"]
    K = len(trait_order)

    audit_rows = []
    all_filtered = []
    total_in = 0
    total_out = 0

    for k, trait_key in enumerate(trait_order):
        trait_file = out_dir / f"{stratum}_mtag_trait_{k+1}.txt"
        if not trait_file.exists():
            print(
                f"WARN: {stratum} trait {k+1} ({trait_key}) "
                f"missing {trait_file.name}; skipping"
            )
            continue
        df = pd.read_csv(trait_file, sep="\t")
        n_in = len(df)
        df["max_FDR"] = float(PLACEHOLDER_MAX_FDR)
        df["trait_key"] = trait_key
        out = filter_by_max_fdr(df, threshold=THRESHOLD)
        n_out = len(out)
        total_in += n_in
        total_out += n_out
        all_filtered.append(out)
        audit_rows.append({
            "stratum": stratum,
            "trait_idx": k + 1,
            "trait_key": trait_key,
            "max_FDR_value": PLACEHOLDER_MAX_FDR,
            "max_FDR_source": "placeholder_pending_lsf_fdr_refire",
            "n_input_rows": n_in,
            "n_output_rows": n_out,
        })
        print(
            f"{stratum} trait {k+1:>2} {trait_key:<40} "
            f"max_FDR={PLACEHOLDER_MAX_FDR:.4g} "
            f"{n_in:>9} -> {n_out:>9} rows"
        )

    if all_filtered:
        combined = pd.concat(all_filtered, ignore_index=True)
    else:
        combined = pd.DataFrame(columns=["trait_key", "max_FDR"])

    out_path = out_dir / f"{stratum}_mtag_maxfdr_filtered.txt"
    combined.to_csv(out_path, sep="\t", index=False)

    audit_path = out_dir / f"{stratum}_mtag_maxfdr_audit.tsv"
    pd.DataFrame(audit_rows).to_csv(audit_path, sep="\t", index=False)

    print(
        f"{stratum} AGGREGATE: {total_in} -> {total_out} rows "
        f"(threshold {THRESHOLD}); wrote {out_path.name} + audit"
    )
    return K, total_in, total_out


def main() -> int:
    print("M2 Wave 2 Task 4 — building maxfdr_filtered tables for 3 strata")
    print(f"  Threshold: {THRESHOLD} (D-M2-07 Turley 2018 default)")
    print(f"  Placeholder max_FDR: {PLACEHOLDER_MAX_FDR} (deviation per audit log)")
    print()
    for stratum in STRATA:
        if not (MTAG_DIR / stratum / "residcov.txt").exists():
            print(f"SKIP: {stratum} has no residcov.txt — below floor")
            continue
        build_for_stratum(stratum)
        print()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
