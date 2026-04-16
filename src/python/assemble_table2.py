#!/usr/bin/env python3
"""
D-06a: Table 2 with one row per trait and 10 columns:
  1. Trait
  2. N_AFR_eff
  3. N_EUR_eff (full)
  4. N_EUR_matched (= N_AFR_eff)
  5. Unmatched concordance % (Phase 2)
  6. Matched-N concordance mean % (D-02a)
  7. Matched-N concordance 95% CI
  8. Expected concordance % under Hou null (D-05b, original-research construction)
  9. LDSC same-trait cross-ancestry r_g (D-04b is_global_benchmark subset) +/- SE
  10. H7 verdict per trait (D-02d 20pp absolute reduction threshold)

D-06b: Secondary Table 2b with trait x (mean_jaccard, ci95).

References:
    - 04-CONTEXT.md D-06a, D-06b, D-02d
    - config/matched_n.yaml: h7_reduction_threshold_pp
    - config/trait_sample_sizes.yaml: per-trait N_eff
"""
import argparse
import sys

import pandas as pd
import yaml


# ---------------------------------------------------------------------------
# D-02d H7 verdict logic
# ---------------------------------------------------------------------------
def compute_h7_verdict(matched_mean_pct: float, unmatched_pct: float,
                       threshold_pp: float = 20.0) -> str:
    """Compute H7 pre-registered verdict per D-02d.

    Args:
        matched_mean_pct: Mean matched-N concordance percentage (D-02a).
        unmatched_pct: Unmatched concordance percentage (full EUR N).
        threshold_pp: Absolute reduction threshold in percentage points.

    Returns:
        'power_artifact' if reduction >= threshold_pp, else 'concordance_holds'.
    """
    reduction = unmatched_pct - matched_mean_pct
    if reduction >= threshold_pp:
        return "power_artifact"
    else:
        return "concordance_holds"


# ---------------------------------------------------------------------------
# Table 2 assembly
# ---------------------------------------------------------------------------
FINAL_COLS = [
    "trait",
    "N_AFR_eff",
    "N_EUR_eff",
    "N_EUR_matched",
    "unmatched_concordance_pct",
    "matched_concordance_pct",
    "matched_ci95",
    "expected_concordance_hou_pct",
    "rg_eur_afr_formatted",
    "h7_verdict",
]


def assemble(tier_a_tsv, jaccard_tsv, detection_tsv, rg_matrix_tsv,
             trait_sample_sizes_yaml, config_yaml, out_table2, out_table2_jaccard):
    """Assemble D-06a Table 2 and D-06b Table 2b from upstream outputs.

    Args:
        tier_a_tsv: Path to tier_a_retention.tsv (D-02a).
        jaccard_tsv: Path to jaccard.tsv (D-02b).
        detection_tsv: Path to detection_probability.tsv (D-05b).
        rg_matrix_tsv: Path to rg_matrix.tsv (D-04d, with is_global_benchmark flag).
        trait_sample_sizes_yaml: Path to config/trait_sample_sizes.yaml.
        config_yaml: Path to config/matched_n.yaml.
        out_table2: Output path for table2.tsv (D-06a).
        out_table2_jaccard: Output path for table2_jaccard.tsv (D-06b).
    """
    cfg = yaml.safe_load(open(config_yaml))
    threshold_pp = cfg["h7_reduction_threshold_pp"]  # 20
    ns = yaml.safe_load(open(trait_sample_sizes_yaml))

    tier = pd.read_csv(tier_a_tsv, sep="\t")
    jac = pd.read_csv(jaccard_tsv, sep="\t")
    det = pd.read_csv(detection_tsv, sep="\t")
    rg = pd.read_csv(rg_matrix_tsv, sep="\t")

    # D-04b: filter to same-trait cross-ancestry EUR_AFR (is_global_benchmark)
    rg_gb = rg[(rg["trait1"] == rg["trait2"]) & (rg["is_global_benchmark"])]
    rg_gb = rg_gb.rename(
        columns={"trait1": "trait", "rg": "rg_eur_afr", "se": "rg_eur_afr_se"}
    )[["trait", "rg_eur_afr", "rg_eur_afr_se"]]

    out = tier.merge(
        det[["trait", "expected_concordance_hou_null"]], on="trait", how="left"
    ).merge(rg_gb, on="trait", how="left")

    out["N_AFR_eff"] = out["trait"].map(lambda t: ns[t]["AFR"])
    out["N_EUR_eff"] = out["trait"].map(lambda t: ns[t]["EUR"])
    out["N_EUR_matched"] = out["N_AFR_eff"]
    out["matched_concordance_pct"] = out["mean_retention"] * 100
    out["matched_ci95"] = out.apply(
        lambda r: f"[{r['ci95_lo'] * 100:.1f}, {r['ci95_hi'] * 100:.1f}]", axis=1
    )
    out["unmatched_concordance_pct"] = out["unmatched_concordance"] * 100
    out["expected_concordance_hou_pct"] = out["expected_concordance_hou_null"] * 100
    out["rg_eur_afr_formatted"] = out.apply(
        lambda r: (
            f"{r['rg_eur_afr']:.3f} +/- {r['rg_eur_afr_se']:.3f}"
            if pd.notna(r["rg_eur_afr"])
            else "NA"
        ),
        axis=1,
    )
    out["h7_verdict"] = out.apply(
        lambda r: compute_h7_verdict(
            r["matched_concordance_pct"],
            r["unmatched_concordance_pct"],
            threshold_pp,
        ),
        axis=1,
    )

    out[FINAL_COLS].to_csv(out_table2, sep="\t", index=False)
    print(f"[assemble_table2] Wrote {len(out)} rows x {len(FINAL_COLS)} cols to {out_table2}")

    # D-06b Table 2b jaccard
    jaccard_cols = [c for c in ["trait", "mean_jaccard", "ci95_lo", "ci95_hi", "n_locus_pairs"] if c in jac.columns]
    jac[jaccard_cols].to_csv(out_table2_jaccard, sep="\t", index=False)
    print(f"[assemble_table2] Wrote {len(jac)} rows to {out_table2_jaccard}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Assemble D-06a Table 2 + D-06b Table 2b")
    parser.add_argument("--tier", required=True, help="tier_a_retention.tsv")
    parser.add_argument("--jaccard", required=True, help="jaccard.tsv")
    parser.add_argument("--detection", required=True, help="detection_probability.tsv")
    parser.add_argument("--rg", required=True, help="rg_matrix.tsv")
    parser.add_argument("--config", required=True, help="config/matched_n.yaml")
    parser.add_argument("--sample-sizes", required=True, help="config/trait_sample_sizes.yaml")
    parser.add_argument("--out-table2", required=True, help="Output table2.tsv")
    parser.add_argument("--out-jaccard", required=True, help="Output table2_jaccard.tsv")
    args = parser.parse_args()

    assemble(
        tier_a_tsv=args.tier,
        jaccard_tsv=args.jaccard,
        detection_tsv=args.detection,
        rg_matrix_tsv=args.rg,
        trait_sample_sizes_yaml=args.sample_sizes,
        config_yaml=args.config,
        out_table2=args.out_table2,
        out_table2_jaccard=args.out_jaccard,
    )


if __name__ == "__main__":
    main()
