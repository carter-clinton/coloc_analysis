#!/usr/bin/env python3
"""Assemble gene x tissue x cell-type matrix from QTL coloc results.

Reads aggregated QTL coloc results (from all 4 sources: GTEx eQTL, GTEx sQTL,
UKB-PPP pQTL, OneK1K sc-eQTL) and produces:
1. Wide-format matrix (heatmap-ready): genes x tissues, values = max PP.H4
2. Long-format table (analysis-ready): gene, tissue, qtl_source, PP.H4

The matrix includes all QTL sources that produced results above the PP.H4
threshold. Column labels combine tissue/cell_type with QTL source for
unambiguous identification (e.g., "Adipose_Subcutaneous.gtex_eqtl",
"CD4_NC.onek1k_sceqtl").
"""
import argparse
import logging
import os
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def build_matrix(input_df, pph4_threshold=0.8):
    """Build gene x tissue matrix from QTL coloc results.

    Parameters
    ----------
    input_df : pd.DataFrame
        Aggregated QTL coloc results with columns: gene_id, region, tissue,
        qtl_source, PP.H4.abf.
    pph4_threshold : float
        PP.H4 threshold for matrix inclusion.

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame)
        (wide_matrix, long_table):
        - wide_matrix: genes x tissue_source columns, values = max PP.H4
        - long_table: filtered long-format with gene, tissue, qtl_source, PP.H4
    """
    # Filter to PP.H4 >= threshold
    filtered = input_df[input_df["PP.H4.abf"] >= pph4_threshold].copy()

    if filtered.empty:
        logger.warning("No results above PP.H4 threshold %.2f", pph4_threshold)
        # Return empty DataFrames with correct structure
        wide = pd.DataFrame(columns=["gene_id", "region"])
        long = pd.DataFrame(columns=["gene_id", "region", "tissue", "qtl_source", "PP.H4.abf"])
        return wide, long

    # Create tissue_source column for unambiguous column labels
    filtered["tissue_source"] = (
        filtered["tissue"].astype(str) + "." + filtered["qtl_source"].astype(str)
    )

    # Long-format table
    long_table = filtered[["gene_id", "region", "tissue", "qtl_source", "PP.H4.abf"]].copy()
    long_table = long_table.sort_values(
        ["gene_id", "region", "PP.H4.abf"], ascending=[True, True, False]
    )

    # Wide-format matrix: pivot on (gene_id, region) x tissue_source
    # Use max PP.H4 in case of multiple credible set pairs
    wide_matrix = filtered.pivot_table(
        index=["gene_id", "region"],
        columns="tissue_source",
        values="PP.H4.abf",
        aggfunc="max",
    ).reset_index()

    # Sort by gene_id
    wide_matrix = wide_matrix.sort_values("gene_id")

    logger.info(
        "Gene-tissue matrix: %d genes x %d tissue-source combinations",
        len(wide_matrix),
        len(wide_matrix.columns) - 2,  # subtract gene_id and region
    )

    return wide_matrix, long_table


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build gene x tissue x cell-type matrix from QTL coloc results."
    )
    parser.add_argument("--input", required=True, help="QTL coloc aggregated results TSV")
    parser.add_argument(
        "--pph4-threshold", type=float, default=0.8,
        help="PP.H4 threshold for matrix inclusion (default: 0.8)",
    )
    parser.add_argument("--output-matrix", required=True, help="Output wide-format matrix TSV")
    parser.add_argument("--output-long", required=True, help="Output long-format table TSV")
    return parser.parse_args()


def main():
    args = parse_args()

    input_df = pd.read_csv(args.input, sep="\t")
    logger.info("Loaded %d QTL coloc results", len(input_df))

    wide_matrix, long_table = build_matrix(input_df, args.pph4_threshold)

    # Write outputs
    os.makedirs(os.path.dirname(args.output_matrix), exist_ok=True)
    wide_matrix.to_csv(args.output_matrix, sep="\t", index=False)
    logger.info("Wide matrix: %s", args.output_matrix)

    os.makedirs(os.path.dirname(args.output_long), exist_ok=True)
    long_table.to_csv(args.output_long, sep="\t", index=False)
    logger.info("Long table: %s", args.output_long)


if __name__ == "__main__":
    main()
