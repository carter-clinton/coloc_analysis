#!/usr/bin/env python3
"""Harmonize eQTL Catalogue GTEx v8 sQTL data for coloc.susie (Phase 2).

Thin wrapper around harmonize_eqtl.py since sQTL from eQTL Catalogue has the
same column schema. The key difference: molecular_trait_id is a splice junction
ID (e.g., chr16:53700000:53750000:clu_12345), not an Ensembl gene ID.

The sQTL files from eQTL Catalogue include both molecular_trait_id (splice
junction) and gene_id (Ensembl gene ID) columns, so we filter on gene_id
and preserve the junction information.

Columns follow the mapping from config/qtl_sources.yaml::sources::gtex_sqtl.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

# Import core eQTL harmonization logic
from harmonize_eqtl import OUTPUT_COLUMNS, _read_eqtl_file, write_harmonized

logger = logging.getLogger(__name__)


def harmonize_sqtl(
    input_path: str,
    region: dict,
    gene_id: str,
    tissue_name: str,
    tissue_n: int,
    config: dict,
) -> pd.DataFrame:
    """Harmonize sQTL Catalogue data for a single (gene, tissue, region) triple.

    Reuses harmonize_eqtl core logic. The sQTL files from eQTL Catalogue have
    the same column schema as eQTL, but molecular_trait_id contains splice
    junction IDs instead of gene IDs. The file also has a gene_id column which
    maps junctions to their parent gene.

    Parameters
    ----------
    input_path : str
        Path to eQTL Catalogue sQTL allpairs TSV file (gzipped).
    region : dict
        Region window with keys 'chr', 'start', 'end' (GRCh38 coordinates).
    gene_id : str
        Ensembl gene ID to filter on (e.g., ENSG00000140718).
        Matching ignores version suffix (e.g., .12).
    tissue_name : str
        Tissue label (e.g., Adipose_Subcutaneous).
    tissue_n : int
        Sample size for this tissue.
    config : dict
        Loaded qtl_sources.yaml content.

    Returns
    -------
    pd.DataFrame
        Harmonized DataFrame with OUTPUT_COLUMNS.
    """
    # Extract column mapping from config (sQTL-specific)
    source_cfg = config.get("sources", {}).get("gtex_sqtl", {})
    col_map = source_cfg.get("columns", {})

    # Read input using the shared eQTL file reader
    df = _read_eqtl_file(input_path, region)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Column name normalization from sQTL config
    beta_col = col_map.get("beta", "beta")
    se_col = col_map.get("se", "se")
    pval_col = col_map.get("pvalue", "pvalue")
    maf_col = col_map.get("maf", "maf")
    # For sQTL, the gene_id config points to molecular_trait_id,
    # but we need to filter by the actual gene_id column
    variant_col = col_map.get("variant_id", "variant")
    pos_col = col_map.get("position", "position")
    chrom_col = col_map.get("chromosome", "chromosome")
    sample_size_field = col_map.get("sample_size_field", "an")

    # Ensure position and chromosome are correct types
    df[pos_col] = pd.to_numeric(df[pos_col], errors="coerce")
    df[chrom_col] = df[chrom_col].astype(str).str.replace("chr", "", regex=False)

    # Region filter (T-02-07 mitigation)
    region_chr = str(region["chr"]).replace("chr", "")
    region_start = int(region["start"])
    region_end = int(region["end"])

    df = df[df[chrom_col] == region_chr].copy()
    df = df[(df[pos_col] >= region_start) & (df[pos_col] <= region_end)].copy()

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Gene filter: sQTL files have a 'gene_id' column alongside molecular_trait_id.
    # Filter by gene_id (Ensembl ID), not molecular_trait_id (junction).
    gene_prefix = gene_id.split(".")[0]
    gene_col_name = "gene_id"  # Always use actual gene_id column for filtering

    if gene_col_name in df.columns:
        df["_gene_prefix"] = df[gene_col_name].astype(str).str.split(".").str[0]
        df = df[df["_gene_prefix"] == gene_prefix].copy()
        df.drop(columns=["_gene_prefix"], inplace=True)
    else:
        logger.warning(
            "gene_id column not found in sQTL data; skipping gene filter"
        )

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Compute N = an / 2 (same as eQTL)
    if sample_size_field in df.columns:
        df["N"] = (pd.to_numeric(df[sample_size_field], errors="coerce") / 2).astype(
            "Int64"
        )
    else:
        df["N"] = tissue_n

    # Set sdY = 1.0 (GTEx inverse-normal transformed, same as eQTL)
    df["sdY"] = 1.0

    # Set tissue column
    df["tissue"] = tissue_name

    # Build output DataFrame
    out = pd.DataFrame()
    out["variant_id"] = df[variant_col].values
    out["beta"] = pd.to_numeric(df[beta_col], errors="coerce").values
    out["se"] = pd.to_numeric(df[se_col], errors="coerce").values
    out["maf"] = pd.to_numeric(df[maf_col], errors="coerce").values
    out["position"] = df[pos_col].values.astype(int)
    out["N"] = df["N"].values
    out["sdY"] = df["sdY"].values
    # gene_id: use the Ensembl gene ID (not the molecular_trait_id/junction)
    out["gene_id"] = df[gene_col_name].astype(str).str.split(".").str[0].values
    out["tissue"] = df["tissue"].values
    out["pvalue"] = pd.to_numeric(df[pval_col], errors="coerce").values
    out["rsid"] = df.get("rsid", pd.Series(["NA"] * len(df))).values
    out["chromosome"] = df[chrom_col].values

    # Drop rows with missing beta or se
    out = out.dropna(subset=["beta", "se"]).copy()

    # MAF filter: drop rows where maf < 0.005 or maf > 0.995
    out = out[(out["maf"] >= 0.005) & (out["maf"] <= 0.995)].copy()

    out = out.reset_index(drop=True)
    return out[OUTPUT_COLUMNS]


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Harmonize eQTL Catalogue sQTL data for coloc.susie"
    )
    parser.add_argument("--input", required=True, help="Input sQTL Catalogue TSV.gz")
    parser.add_argument("--region-chr", required=True, help="Region chromosome")
    parser.add_argument(
        "--region-start", required=True, type=int, help="Region start (GRCh38)"
    )
    parser.add_argument(
        "--region-end", required=True, type=int, help="Region end (GRCh38)"
    )
    parser.add_argument("--gene-id", required=True, help="Ensembl gene ID")
    parser.add_argument("--tissue-name", required=True, help="Tissue label")
    parser.add_argument("--tissue-n", required=True, type=int, help="Tissue N")
    parser.add_argument(
        "--qtl-source-config", required=True, help="Path to qtl_sources.yaml"
    )
    parser.add_argument("--output", required=True, help="Output harmonized TSV.gz path")

    args = parser.parse_args()

    with open(args.qtl_source_config) as f:
        config = yaml.safe_load(f)

    region = {
        "chr": args.region_chr,
        "start": args.region_start,
        "end": args.region_end,
    }

    df = harmonize_sqtl(
        input_path=args.input,
        region=region,
        gene_id=args.gene_id,
        tissue_name=args.tissue_name,
        tissue_n=args.tissue_n,
        config=config,
    )

    if df.empty:
        logger.warning(
            "No variants after harmonization for %s / %s",
            args.gene_id,
            args.tissue_name,
        )

    write_harmonized(df, args.output)
    print(
        f"[harmonize_sqtl] wrote {len(df)} variants to {args.output} "
        f"(gene={args.gene_id}, tissue={args.tissue_name})"
    )


if __name__ == "__main__":
    main()
