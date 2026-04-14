"""Plan 09-05 Task 2 — leave-one-cohort-out IVW meta (RESEARCH §16 recommendation).

For each signal with ≥ 2 ancestry-matched replication cohorts, we iterate
over each cohort as a "held-out" observation and compute the IVW
fixed-effect meta of the *remaining* cohorts. This isolates the contribution
of any single cohort to the meta-analytic signal — a classic jack-knife
sensitivity for detecting cohort-driven outlier support.

Output columns (one row per (signal_id, held_out_cohort)):
    signal_id, held_out_cohort, held_out_beta, held_out_se,
    loco_meta_beta, loco_meta_se, loco_n_cohorts

Ancestry matching: rows are grouped by `cohort_ancestry` so EUR and AFR
cohorts never pool into the same leave-out. BBJ (is_generalization=TRUE)
is expected to be excluded upstream (aggregate_replication_meta.R) before
this module sees the per-cohort-combined table.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def loco_meta(per_cohort_long: pd.DataFrame) -> pd.DataFrame:
    """Compute leave-one-cohort-out IVW meta.

    Expected input columns:
        signal_id, cohort, cohort_ancestry, beta_replication, se_replication

    Each (signal_id, cohort_ancestry) group is jack-knifed: every cohort in
    the group is held out once, and the remaining cohorts form an IVW FE meta.
    Groups with < 2 valid cohorts contribute no rows. A hold-out leaving
    < 2 cohorts in the meta also contributes no row (need ≥ 2 to meta).
    """
    rows: list[dict] = []

    if per_cohort_long.empty:
        return pd.DataFrame(columns=[
            "signal_id", "held_out_cohort", "held_out_beta", "held_out_se",
            "loco_meta_beta", "loco_meta_se", "loco_n_cohorts",
        ])

    group_cols = ["signal_id"]
    if "cohort_ancestry" in per_cohort_long.columns:
        group_cols.append("cohort_ancestry")

    for group_key, grp in per_cohort_long.groupby(group_cols):
        # Filter to valid beta/se rows.
        valid = grp[
            grp["beta_replication"].notna()
            & grp["se_replication"].notna()
            & (grp["se_replication"] > 0)
        ]
        if len(valid) < 2:
            continue

        sig = group_key[0] if isinstance(group_key, tuple) else group_key

        for idx, hold_out in valid.iterrows():
            rest = valid.drop(idx)
            if len(rest) < 2:
                continue
            w = 1.0 / (rest["se_replication"].astype(float) ** 2)
            beta_loco = float(
                (w * rest["beta_replication"].astype(float)).sum() / w.sum()
            )
            se_loco = float(np.sqrt(1.0 / w.sum()))
            rows.append({
                "signal_id": sig,
                "held_out_cohort": hold_out.get("cohort"),
                "held_out_beta": float(hold_out["beta_replication"]),
                "held_out_se": float(hold_out["se_replication"]),
                "loco_meta_beta": beta_loco,
                "loco_meta_se": se_loco,
                "loco_n_cohorts": len(rest),
            })

    return pd.DataFrame(rows, columns=[
        "signal_id", "held_out_cohort", "held_out_beta", "held_out_se",
        "loco_meta_beta", "loco_meta_se", "loco_n_cohorts",
    ])


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--per-cohort", required=True,
        help="long-form TSV with signal_id, cohort, cohort_ancestry, "
             "beta_replication, se_replication (Plan 09-05 aggregator output)",
    )
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    df = pd.read_csv(a.per_cohort, sep="\t")
    out = loco_meta(df)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.out, sep="\t", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
