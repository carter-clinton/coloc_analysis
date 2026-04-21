#!/usr/bin/env python3
"""Assign Tier A/B/C confidence levels to colocalization results.

Implements tier assignment logic per D-02c (QTL-source-agnostic):
- Tier A: Trait-trait coloc PP.H4 >= threshold AND QTL coloc PP.H4 >= threshold
- Tier B: Trait-trait coloc PP.H4 >= threshold AND QTL PP.H4 in [tier_b_min, threshold)
- Tier C: Trait-trait coloc PP.H4 >= threshold AND no QTL PP.H4 >= tier_b_min

Also provides PP.H4 threshold sweep (REQ-3): tier counts at {0.5, 0.7, 0.8, 0.9}
per ancestry.

T-02-16 mitigation: all thresholds from config/pph4_thresholds.yaml, not hardcoded.
"""
import argparse
import csv
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def assign_tier(gwas_pph4, qtl_pph4, threshold, tier_b_min=0.5):
    """Assign a single tier based on GWAS and QTL PP.H4 values.

    Parameters
    ----------
    gwas_pph4 : float
        Best GWAS-GWAS coloc PP.H4 at this locus.
    qtl_pph4 : float or None
        Best QTL coloc PP.H4 at this locus (across all sources/tissues/genes).
    threshold : float
        Primary PP.H4 threshold (typically 0.8).
    tier_b_min : float
        Minimum QTL PP.H4 for Tier B (typically 0.5).

    Returns
    -------
    str
        One of "Tier A", "Tier B", "Tier C", or "below_threshold".
    """
    if gwas_pph4 < threshold:
        return "below_threshold"

    if qtl_pph4 is None:
        return "Tier C"

    if qtl_pph4 >= threshold:
        return "Tier A"
    elif qtl_pph4 >= tier_b_min:
        return "Tier B"
    else:
        return "Tier C"


def sweep_tiers(results_df, sweep_values, gwas_pph4_col="PP.H4.abf", tier_b_min=0.5):
    """Compute tier counts at each threshold for a sweep analysis (REQ-3).

    Parameters
    ----------
    results_df : pd.DataFrame
        QTL coloc results with at least columns: region, ancestry, PP.H4.abf.
    sweep_values : list of float
        Threshold values to sweep over, e.g. [0.5, 0.7, 0.8, 0.9].
    gwas_pph4_col : str
        Column name for PP.H4 values.
    tier_b_min : float
        Minimum PP.H4 for Tier B assignment.

    Returns
    -------
    pd.DataFrame
        Sweep table with columns: threshold, ancestry, n_tier_a, n_tier_b, n_tier_c.
    """
    rows = []
    for threshold in sweep_values:
        for ancestry in results_df["ancestry"].unique():
            anc_df = results_df[results_df["ancestry"] == ancestry]

            # For sweep purposes, treat each row as having both GWAS and QTL PP.H4
            # equal to the reported PP.H4.abf (simplified for sweep mode).
            # In full mode, GWAS PP.H4 comes from a separate table.
            n_tier_a = 0
            n_tier_b = 0
            n_tier_c = 0

            # Group by region to get best PP.H4 per locus
            for region, group in anc_df.groupby("region"):
                best_pph4 = group[gwas_pph4_col].max()
                # In sweep mode: use best_pph4 as both GWAS and QTL metric
                tier = assign_tier(best_pph4, best_pph4, threshold, tier_b_min)
                if tier == "Tier A":
                    n_tier_a += 1
                elif tier == "Tier B":
                    n_tier_b += 1
                elif tier == "Tier C":
                    n_tier_c += 1
                # below_threshold: not counted

            rows.append({
                "threshold": threshold,
                "ancestry": ancestry,
                "n_tier_a": n_tier_a,
                "n_tier_b": n_tier_b,
                "n_tier_c": n_tier_c,
            })

    return pd.DataFrame(rows)


def assign_tiers_full(qtl_results_df, gwas_coloc_df, pph4_config,
                      neg_ctrl_df=None):
    """Full tier assignment combining GWAS-GWAS coloc and QTL coloc results.

    Parameters
    ----------
    qtl_results_df : pd.DataFrame
        QTL coloc aggregated results (region, ancestry, qtl_source, tissue,
        gene_id, PP.H4.abf).
    gwas_coloc_df : pd.DataFrame
        GWAS-GWAS coloc results (region, ancestry, trait_a, trait_b, PP.H4.abf).
    pph4_config : dict
        Loaded pph4_thresholds.yaml config.
    neg_ctrl_df : pd.DataFrame or None
        Negative control results to append with tier="negative_control".

    Returns
    -------
    pd.DataFrame
        Tier assignment table.
    """
    primary_threshold = pph4_config["primary_threshold"]
    tier_defs = pph4_config["tier_definitions"]
    tier_b_min = tier_defs["tier_b"]["min_pph4_qtl"]

    results = []

    # Get best GWAS PP.H4 per (region, ancestry)
    if not gwas_coloc_df.empty:
        gwas_best = (
            gwas_coloc_df.groupby(["region", "ancestry"])["PP.H4.abf"]
            .max()
            .reset_index()
            .rename(columns={"PP.H4.abf": "best_gwas_pph4"})
        )
    else:
        gwas_best = pd.DataFrame(columns=["region", "ancestry", "best_gwas_pph4"])

    # Get best QTL PP.H4 per (region, ancestry) with resolving details.
    # Groups can be all-NaN (every row in the group has status in
    # {no_qtl_cs, too_few_snps, error, no_gwas_cs}, so PP.H4.abf is NaN);
    # pandas idxmax raises on all-NaN since v1.3. Fall back to a synthetic
    # "no QTL resolution" row for those groups so downstream merge still
    # produces a complete GWAS-vs-QTL matrix.
    if not qtl_results_df.empty:
        qtl_grouped = qtl_results_df.groupby(["region", "ancestry"])
        qtl_best_list = []
        for (region, ancestry), group in qtl_grouped:
            pph4_col = group["PP.H4.abf"]
            all_sources = group["qtl_source"].unique().tolist()
            if pph4_col.notna().any():
                best_idx = pph4_col.idxmax()
                best_row = group.loc[best_idx]
                qtl_best_list.append({
                    "region": region,
                    "ancestry": ancestry,
                    "best_qtl_pph4": best_row["PP.H4.abf"],
                    "resolving_gene": best_row.get("gene_id", ""),
                    "resolving_tissue": best_row.get("tissue", ""),
                    "resolving_qtl_source": best_row.get("qtl_source", ""),
                    "all_supporting_sources": ";".join(all_sources),
                })
            else:
                # All rows in this (region, ancestry) have status != ok.
                # Record the null-QTL row so merge produces the GWAS row.
                qtl_best_list.append({
                    "region": region,
                    "ancestry": ancestry,
                    "best_qtl_pph4": None,
                    "resolving_gene": "",
                    "resolving_tissue": "",
                    "resolving_qtl_source": "",
                    "all_supporting_sources": ";".join(all_sources),
                })
        qtl_best = pd.DataFrame(qtl_best_list)
    else:
        qtl_best = pd.DataFrame(
            columns=["region", "ancestry", "best_qtl_pph4", "resolving_gene",
                      "resolving_tissue", "resolving_qtl_source",
                      "all_supporting_sources"]
        )

    # Merge and assign tiers
    merged = gwas_best.merge(qtl_best, on=["region", "ancestry"], how="left")
    for _, row in merged.iterrows():
        gwas_pph4 = row["best_gwas_pph4"]
        qtl_pph4 = row.get("best_qtl_pph4")
        if pd.isna(qtl_pph4):
            qtl_pph4 = None

        tier = assign_tier(gwas_pph4, qtl_pph4, primary_threshold, tier_b_min)

        results.append({
            "region": row["region"],
            "ancestry": row["ancestry"],
            "tier": tier,
            "best_gwas_pph4": gwas_pph4,
            "best_qtl_pph4": qtl_pph4 if qtl_pph4 is not None else 0.0,
            "resolving_gene": row.get("resolving_gene", ""),
            "resolving_tissue": row.get("resolving_tissue", ""),
            "resolving_qtl_source": row.get("resolving_qtl_source", ""),
            "all_supporting_sources": row.get("all_supporting_sources", ""),
            "neg_ctrl_set": "",
        })

    # Append negative control rows if provided
    if neg_ctrl_df is not None and not neg_ctrl_df.empty:
        for _, row in neg_ctrl_df.iterrows():
            results.append({
                "region": row.get("region", ""),
                "ancestry": row.get("ancestry", "EUR"),
                "tier": "negative_control",
                "best_gwas_pph4": 0.0,
                "best_qtl_pph4": row.get("PP.H4.abf", 0.0) if pd.notna(row.get("PP.H4.abf")) else 0.0,
                "resolving_gene": row.get("gene_id", ""),
                "resolving_tissue": "",
                "resolving_qtl_source": row.get("qtl_source", ""),
                "all_supporting_sources": row.get("qtl_source", ""),
                "neg_ctrl_set": row.get("neg_ctrl_set", ""),
            })

    return pd.DataFrame(results)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Assign Tier A/B/C confidence levels to coloc results."
    )
    parser.add_argument("--input", required=True, help="QTL coloc aggregated results TSV")
    parser.add_argument("--gwas-coloc", help="GWAS-GWAS coloc results TSV")
    parser.add_argument("--pph4-config", required=True, help="Path to pph4_thresholds.yaml")
    parser.add_argument(
        "--neg-ctrl-results",
        help="Path to curated_neg_ctrl_results.tsv (optional, appends negative_control rows)",
    )
    parser.add_argument("--output", required=True, help="Output tier assignment TSV")
    parser.add_argument("--sweep", action="store_true", help="Produce sweep table")
    parser.add_argument("--sweep-output", help="Output sweep table TSV (with --sweep)")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.pph4_config) as f:
        pph4_config = yaml.safe_load(f)

    qtl_results = pd.read_csv(args.input, sep="\t")

    # Load GWAS coloc if provided. Tolerate both missing file and empty file
    # (zero-byte / header-only TSV produced by summarize_coloc_results when the
    # upstream trait-pair manifest had no populated rows — e.g., Phase 1
    # trait-pair coloc has not yet fired for this tier, or is scope-gated out).
    gwas_coloc = pd.DataFrame(columns=["region", "ancestry", "PP.H4.abf"])
    if args.gwas_coloc and os.path.exists(args.gwas_coloc):
        try:
            if os.path.getsize(args.gwas_coloc) > 0:
                gwas_coloc = pd.read_csv(args.gwas_coloc, sep="\t")
            else:
                logger.warning(
                    "GWAS coloc file is empty (0 bytes) — proceeding with no "
                    "trait-pair evidence; tier assignments reflect QTL-only signals."
                )
        except pd.errors.EmptyDataError:
            logger.warning(
                "GWAS coloc file has no parseable columns — proceeding with no "
                "trait-pair evidence."
            )

    # Load negative control results if provided (same empty-tolerance logic)
    neg_ctrl_df = None
    if args.neg_ctrl_results and os.path.exists(args.neg_ctrl_results):
        try:
            if os.path.getsize(args.neg_ctrl_results) > 0:
                neg_ctrl_df = pd.read_csv(args.neg_ctrl_results, sep="\t")
        except pd.errors.EmptyDataError:
            logger.warning(
                "Negative-control results file has no parseable columns — "
                "proceeding without negative_control tier rows."
            )

    # Full tier assignment
    tier_df = assign_tiers_full(qtl_results, gwas_coloc, pph4_config, neg_ctrl_df)
    tier_df.to_csv(args.output, sep="\t", index=False)
    logger.info("Tier assignments: %d rows -> %s", len(tier_df), args.output)

    # Sweep mode
    if args.sweep:
        sweep_df = sweep_tiers(qtl_results, pph4_config["sweep_values"])
        sweep_output = args.sweep_output or args.output.replace(".tsv", "_sweep.tsv")
        sweep_df.to_csv(sweep_output, sep="\t", index=False)
        logger.info("PP.H4 sweep: %d rows -> %s", len(sweep_df), sweep_output)


if __name__ == "__main__":
    main()
