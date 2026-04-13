#!/usr/bin/env python3
"""Parse Open Targets Locus2Gene predictions and compute concordance with QTL coloc.

Reads L2G predictions from versioned Parquet (v26.03), computes concordance
rate for Tier A loci: fraction where QTL coloc resolving gene matches L2G
top gene.

D-05a: L2G is independent corroborating evidence, NOT a gate.
D-05b: Disagreements are findings (potential distal enhancer-driven assignments).

T-02-15 mitigation: version-pinned L2G release; schema validated after read.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Attempt pyarrow import; graceful fallback if not available
try:
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False
    logger.warning("pyarrow not available; L2G Parquet reading will use pandas fallback")


def read_l2g_parquet(l2g_dir, columns=None):
    """Read Open Targets L2G predictions from Parquet directory.

    Parameters
    ----------
    l2g_dir : str or Path
        Path to L2G Parquet directory (may contain partitioned files).
    columns : list of str, optional
        Columns to select. Defaults to ["studyLocusId", "geneId", "score"].

    Returns
    -------
    pd.DataFrame
        L2G predictions with columns: studyLocusId, geneId, score.

    Raises
    ------
    FileNotFoundError
        If l2g_dir does not exist.
    ValueError
        If required columns are missing (T-02-15 schema validation).
    """
    l2g_path = Path(l2g_dir)
    if not l2g_path.exists():
        raise FileNotFoundError(f"L2G directory not found: {l2g_dir}")

    if columns is None:
        columns = ["studyLocusId", "geneId", "score"]

    if HAS_PYARROW:
        table = pq.read_table(str(l2g_path), columns=columns)
        df = table.to_pandas()
    else:
        # Fallback: try reading as single parquet file with pandas
        if l2g_path.is_file():
            df = pd.read_parquet(str(l2g_path), columns=columns)
        else:
            # Directory of parquet files
            parquet_files = list(l2g_path.glob("**/*.parquet"))
            if not parquet_files:
                raise FileNotFoundError(f"No parquet files found in {l2g_dir}")
            dfs = [pd.read_parquet(str(f), columns=columns) for f in parquet_files]
            df = pd.concat(dfs, ignore_index=True)

    # T-02-15: validate schema
    required_cols = {"studyLocusId", "geneId", "score"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"L2G schema validation failed. Missing columns: {missing}")

    return df


def compute_concordance(tier_table, l2g_df, l2g_threshold=0.5):
    """Compute concordance between Tier A QTL coloc genes and L2G top genes.

    Parameters
    ----------
    tier_table : pd.DataFrame
        Tier assignment table with columns: region, tier, resolving_gene.
    l2g_df : pd.DataFrame
        L2G predictions with columns: studyLocusId, geneId, score.
    l2g_threshold : float
        Score threshold for high-confidence L2G assignments.

    Returns
    -------
    pd.DataFrame
        Concordance table with columns: region, qtl_gene, l2g_gene, l2g_score,
        concordant, annotation.
    """
    # Filter to high-confidence L2G assignments
    l2g_hc = l2g_df[l2g_df["score"] >= l2g_threshold].copy()

    # Get top L2G gene per studyLocusId
    l2g_top = (
        l2g_hc.sort_values("score", ascending=False)
        .drop_duplicates(subset=["studyLocusId"], keep="first")
    )

    # Filter tier table to Tier A only
    tier_a = tier_table[tier_table["tier"] == "Tier A"].copy()

    results = []
    for _, row in tier_a.iterrows():
        region = row["region"]
        qtl_gene = row.get("resolving_gene", "")

        # Find matching L2G entry (fuzzy match on region/studyLocusId)
        # L2G studyLocusId may not directly map; try substring match
        l2g_match = l2g_top[
            l2g_top["studyLocusId"].str.contains(region, case=False, na=False)
        ]

        if len(l2g_match) > 0:
            l2g_gene = l2g_match.iloc[0]["geneId"]
            l2g_score = l2g_match.iloc[0]["score"]
            concordant = _genes_match(qtl_gene, l2g_gene)
        else:
            l2g_gene = ""
            l2g_score = None
            concordant = None

        # D-05b: disagreements are findings, annotate appropriately
        if concordant is False:
            annotation = "distal_enhancer_candidate"
        elif concordant is True:
            annotation = "concordant"
        else:
            annotation = "no_l2g_match"

        results.append({
            "region": region,
            "ancestry": row.get("ancestry", ""),
            "qtl_gene": qtl_gene,
            "l2g_gene": l2g_gene,
            "l2g_score": l2g_score,
            "concordant": concordant,
            "annotation": annotation,
        })

    concordance_df = pd.DataFrame(results)

    # Compute concordance rate
    matched = concordance_df[concordance_df["concordant"].notna()]
    if len(matched) > 0:
        concordance_rate = matched["concordant"].mean()
        logger.info(
            "L2G concordance rate for Tier A: %.1f%% (%d/%d matched)",
            concordance_rate * 100,
            matched["concordant"].sum(),
            len(matched),
        )
    else:
        logger.info("No L2G matches found for Tier A loci")

    return concordance_df


def _genes_match(qtl_gene, l2g_gene):
    """Check if QTL coloc gene matches L2G gene.

    Handles Ensembl ID format (ENSGXXX) and gene symbol matching.
    """
    if not qtl_gene or not l2g_gene:
        return None

    # Direct match
    if qtl_gene == l2g_gene:
        return True

    # Strip version suffix from Ensembl IDs (ENSG00000140718.12 -> ENSG00000140718)
    qtl_clean = qtl_gene.split(".")[0]
    l2g_clean = l2g_gene.split(".")[0]

    return qtl_clean == l2g_clean


def parse_args():
    parser = argparse.ArgumentParser(
        description="Parse Open Targets L2G and compute concordance with QTL coloc."
    )
    parser.add_argument("--l2g-dir", required=True, help="Path to L2G Parquet directory")
    parser.add_argument("--tier-table", required=True, help="Path to tier assignment TSV")
    parser.add_argument("--output", required=True, help="Output concordance TSV")
    parser.add_argument(
        "--l2g-threshold", type=float, default=0.5,
        help="L2G score threshold for high confidence (default: 0.5, per D-05a)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Read L2G predictions
    l2g_df = read_l2g_parquet(args.l2g_dir)
    logger.info("Loaded %d L2G predictions", len(l2g_df))

    # Read tier table
    tier_table = pd.read_csv(args.tier_table, sep="\t")
    logger.info("Loaded %d tier assignments", len(tier_table))

    # Compute concordance
    concordance_df = compute_concordance(tier_table, l2g_df, args.l2g_threshold)

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    concordance_df.to_csv(args.output, sep="\t", index=False)
    logger.info("Concordance table: %d rows -> %s", len(concordance_df), args.output)


if __name__ == "__main__":
    main()
