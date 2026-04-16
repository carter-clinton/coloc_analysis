#!/usr/bin/env python3
"""
Per-locus detection probability under empirical beta_hat/SE null (D-05a).

# ORIGINAL-RESEARCH CONSTRUCTION (per RESEARCH B-2 resolution 2026-04-15).
# The originally-cited Hou 2023 Nat Genet paper (PMC10403901 -> PMC11120833) is
# the radmix paper, which does NOT describe an NCP-based detection-probability
# framework. D-05 is an original analytic construction by this study; the OSF
# pre-registration section 12.1 line 320 does NOT cite Hou by name for the NCP
# framework, so this is an internal clarification, not an OSF deviation
# (logged in .planning/osf_deviations.md as clarification).

D-05a: For each AFR Tier A locus with observed beta_hat_AFR and SE_AFR at the AFR
       lead variant, compute the chi-square non-centrality parameter at
       N_EUR_matched:
           NCP = (beta_hat_AFR / SE_AFR_at_matched_N)^2
       where SE_AFR_at_matched_N = SE_AFR (AFR discovery N already = matched N).
       Detection probability = P(chi^2_1,NCP >= T) where T = qchisq(1 - 5e-8, df=1)
       for genome-wide significance. Use scipy.stats.ncx2.sf(T, df=1, nc=NCP).
D-05b: Aggregate per-locus detection probabilities to trait-level expected
       concordance via arithmetic mean across AFR Tier A loci per trait (D-05d).
D-05c: Parametric prior from Hou et al. 2023 Table S1 is NOT used for primary
       analysis. Empirical beta_hat/SE from this study's T1 first-production
       Tier A loci is more tailored to the loci under study.
D-05d: arithmetic mean aggregation across loci per trait to match D-02a metric.
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy import stats

# Genome-wide significance threshold on the chi-square scale (5e-8)
GW_SIG_CHI2_THRESHOLD = stats.chi2.ppf(1 - 5e-8, df=1)  # ~29.72


def per_locus_detection_prob(
    beta_hat: np.ndarray,
    se: np.ndarray,
    chi2_threshold: float = GW_SIG_CHI2_THRESHOLD,
) -> np.ndarray:
    """Compute per-locus detection probability under empirical NCP null.

    D-05a: NCP = (beta_hat / SE)^2, then P(chi^2_1(NCP) >= threshold).

    Parameters
    ----------
    beta_hat : np.ndarray
        Observed effect sizes (beta_hat_AFR at lead variant).
    se : np.ndarray
        Standard errors at matched N.
    chi2_threshold : float
        Chi-square threshold for genome-wide significance (~29.72).

    Returns
    -------
    np.ndarray
        Detection probabilities, one per locus.
    """
    beta_hat = np.asarray(beta_hat, dtype=float)
    se = np.asarray(se, dtype=float)

    ncp = (beta_hat / se) ** 2
    # P(chi^2_1(NCP) >= T) = survival function of noncentral chi-squared
    return stats.ncx2.sf(chi2_threshold, df=1, nc=ncp)


def trait_expected_concordance(tier_a_tsv: str, out_tsv: str) -> pd.DataFrame:
    """Aggregate per-locus detection probabilities to trait-level (D-05b/d).

    Uses arithmetic mean across AFR Tier A loci per trait (D-05d) to produce
    trait-level expected concordance under the matched-N null.

    Parameters
    ----------
    tier_a_tsv : str
        Input TSV with columns: trait, locus_id, beta_afr, se_afr.
    out_tsv : str
        Output TSV path.

    Returns
    -------
    pd.DataFrame
        Trait-level expected concordance with columns:
        trait, n_tier_a_loci, expected_concordance_hou_null.
    """
    df = pd.read_csv(tier_a_tsv, sep="\t")

    # Compute per-locus detection probability (D-05a)
    df["detection_prob"] = per_locus_detection_prob(
        df["beta_afr"].values, df["se_afr"].values
    )

    # Trait-level aggregation: arithmetic mean (D-05d)
    agg = df.groupby("trait", as_index=False).agg(
        n_tier_a_loci=("locus_id", "count"),
        expected_concordance_hou_null=("detection_prob", "mean"),  # D-05d arithmetic mean
    )

    agg.to_csv(out_tsv, sep="\t", index=False)
    return agg


def main():
    parser = argparse.ArgumentParser(
        description="D-05: Compute per-locus detection probability + trait-level expected concordance."
    )
    parser.add_argument("--in", dest="input_tsv", required=True,
                        help="Input tier_a TSV (trait, locus_id, beta_afr, se_afr)")
    parser.add_argument("--out", required=True, help="Output detection_probability.tsv")
    args = parser.parse_args()

    agg = trait_expected_concordance(args.input_tsv, args.out)
    print(f"Detection probability computed for {len(agg)} traits:")
    for _, row in agg.iterrows():
        print(f"  {row['trait']}: {row['n_tier_a_loci']} loci, "
              f"expected concordance = {row['expected_concordance_hou_null']:.4f}")


if __name__ == "__main__":
    main()
