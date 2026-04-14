"""Plan 09-04 Task 2 — per-cohort Bonferroni effect-size test.

Implements D-03a (joint effect-size + coloc criterion) + RESEARCH pitfalls
#4 (Bonferroni denominator = N_signals_tested_in_THIS_cohort) and #5 (report
post-hoc power for small-N cohorts).

Public functions:
  compute_bonferroni(n_signals_in_cohort, alpha=0.05) -> float
  check_same_direction(beta_disc, beta_rep) -> bool
  posthoc_power(beta_fiqt, se_rep, alpha) -> float  (NaN on invalid input)
  compute_joint_criterion(row, primary_threshold=0.8) -> bool
  process_cohort(effect_df, fiqt_df, coloc_df, cohort, primary_threshold)
      -> pd.DataFrame with derived columns

CLI (driven by rule compute_per_cohort_effect_size_test):
  python -m compute_per_cohort_effect_size_test \
    --effect effect_size_raw/{cohort}.tsv \
    --fiqt discovery_beta_fiqt.tsv \
    --coloc sweep_aggregated_{cohort}.tsv \
    --cohort {cohort} \
    --out effect_size/{cohort}.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import norm


def compute_bonferroni(n_signals_in_cohort: int, alpha: float = 0.05) -> float:
    """Return Bonferroni-adjusted α for this cohort.

    RESEARCH pitfall #4: the denominator is the NUMBER OF SIGNALS TESTED IN
    THIS COHORT — NOT the global count across all cohorts. This implements
    T-09-15 mitigation (test_bonferroni.py::test_bonferroni_denominator
    guards the contract).
    """
    if n_signals_in_cohort < 1:
        raise ValueError(
            f"n_signals_in_cohort must be >= 1, got {n_signals_in_cohort}"
        )
    return float(alpha) / float(n_signals_in_cohort)


def check_same_direction(beta_disc: float, beta_rep: float) -> bool:
    """Return True iff signs of beta_disc and beta_rep match.

    D-03a explicit requirement for the effect-size criterion. NaN inputs
    return False (we cannot affirm same-direction without a measurement).
    Zero-β inputs: treat sign(0)=0 as matching only another 0; to be
    conservative we treat 0 as "not a reliable direction" and return False
    unless both are 0.
    """
    if pd.isna(beta_disc) or pd.isna(beta_rep):
        return False
    sign_d = np.sign(beta_disc)
    sign_r = np.sign(beta_rep)
    return bool(sign_d == sign_r) and (sign_d != 0 or sign_r == 0)


def posthoc_power(beta_fiqt: float, se_rep: float, alpha: float) -> float:
    """Two-sided post-hoc power at α for detecting β_fiqt given se_rep.

    Power = Φ(|β_fiqt|/se_rep − z_{α/2}) where z_{α/2} = Φ^{-1}(1 − α/2).

    Invalid input (NaN β, non-positive SE) returns NaN so callers can
    distinguish "could not compute" from "genuinely low power".
    """
    if pd.isna(beta_fiqt) or pd.isna(se_rep) or se_rep <= 0:
        return float("nan")
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = abs(beta_fiqt) / se_rep - z_alpha
    return float(norm.cdf(z_beta))


def pph4_sweep_colname(threshold: float) -> str:
    """Canonical column name for a PP.H4 sweep threshold.

    WR-04 fix: Python's ``f"{0.80}"`` yields ``"0.8"`` but a caller passing
    a non-exact float like ``0.75 + 0.05`` repr'd as ``"0.8000000001"`` would
    silently break the Python↔R join (R emits via ``sprintf("%.1f", ...)``).
    Pin both sides to one-decimal formatting so the column name is invariant
    to input precision, matching the R synthesis in
    ``src/snakemake/scripts/run_replication_coloc_susie.R`` (updated to
    ``sprintf("replicated_pph4_%.1f", pph4_thresholds)``).
    """
    return f"replicated_pph4_{threshold:.1f}"


def compute_joint_criterion(row: pd.Series, primary_threshold: float = 0.8) -> bool:
    """Return True iff the Bonferroni AND coloc criteria both hold.

    D-03a: a signal counts as "replicated" in a cohort iff BOTH:
      - replicated_bonferroni is True (per-cohort Bonferroni + same-direction β)
      - replicated_pph4_<primary_threshold> is True

    Defensive: missing columns default to False (joint is a conjunction;
    absence of evidence → not replicated).
    """
    key_pph4 = pph4_sweep_colname(primary_threshold)
    bonf = bool(row.get("replicated_bonferroni", False))
    pph4 = bool(row.get(key_pph4, False))
    return bonf and pph4


def process_cohort(
    effect_df: pd.DataFrame,
    fiqt_df: pd.DataFrame,
    coloc_df: pd.DataFrame,
    cohort: str,
    primary_threshold: float = 0.8,
) -> pd.DataFrame:
    """Merge FIQT discovery + per-cohort replication effect + coloc sweep
    and compute derived columns.

    Required columns:
      effect_df: signal_id, cohort, beta_replication, se_replication, p_replication
      fiqt_df:   signal_id, beta_discovery_FIQT
      coloc_df:  signal_id, cohort, replicated_pph4_{0.5,0.7,0.8,0.9}

    Derived columns added to the output:
      bonf_threshold, same_direction, replicated_bonferroni,
      power_posthoc, replicated_joint_{primary_threshold}
    """
    df = (
        effect_df.merge(fiqt_df, on="signal_id", how="left")
        .merge(coloc_df, on=["signal_id", "cohort"], how="left")
    )

    # WR-10 fix: defensive guard against (signal_id, cohort) duplicates from
    # upstream aggregators. If coloc_df emits >1 row per pair (e.g., multiple
    # credible-set pairs from coloc.susie) the merge cross-joins, and the
    # per-row Bonferroni test would give a single signal multiple shots at
    # the threshold — inflating replication rate in a way that defeats
    # RESEARCH pitfall #4. The upstream sweep aggregator is expected to
    # collapse to one row per (signal, cohort) with pph4_best already
    # applied; this guard catches any regression in that invariant.
    dup = df.groupby(["signal_id", "cohort"]).size()
    if (dup > 1).any():
        raise ValueError(
            "process_cohort: duplicated (signal_id, cohort) rows after "
            f"merge: {dup[dup > 1].to_dict()}. Upstream sweep aggregator "
            "must collapse to one row per (signal_id, cohort)."
        )

    n_in_cohort = df["signal_id"].nunique()
    alpha_bonf = compute_bonferroni(n_in_cohort)

    df = df.copy()
    df["bonf_threshold"] = alpha_bonf
    df["same_direction"] = df.apply(
        lambda r: check_same_direction(
            r.get("beta_discovery_FIQT"), r.get("beta_replication")
        ),
        axis=1,
    )
    df["replicated_bonferroni"] = (
        (df["p_replication"] < alpha_bonf) & df["same_direction"]
    )
    df["power_posthoc"] = df.apply(
        lambda r: posthoc_power(
            r.get("beta_discovery_FIQT"),
            r.get("se_replication"),
            alpha_bonf,
        ),
        axis=1,
    )
    df[f"replicated_joint_{primary_threshold}"] = df.apply(
        lambda r: compute_joint_criterion(r, primary_threshold), axis=1
    )
    return df


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--effect", required=True,
                   help="results/replication/effect_size_raw/{cohort}.tsv (Plan 09-04 Step 1b producer)")
    p.add_argument("--fiqt", required=True,
                   help="results/replication/fiqt/discovery_beta_fiqt.tsv (Plan 09-03 producer)")
    p.add_argument("--coloc", required=True,
                   help="results/replication/coloc/sweep_aggregated_{cohort}.tsv (Plan 09-05 aggregator)")
    p.add_argument("--cohort", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--primary-threshold", type=float, default=0.8)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    effect = pd.read_csv(a.effect, sep="\t")
    fiqt = pd.read_csv(a.fiqt, sep="\t")
    coloc = pd.read_csv(a.coloc, sep="\t")
    out = process_cohort(effect, fiqt, coloc, a.cohort, a.primary_threshold)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.out, sep="\t", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
