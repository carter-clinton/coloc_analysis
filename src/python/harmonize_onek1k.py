#!/usr/bin/env python3
"""Harmonize OneK1K single-cell eQTL data for coloc.susie (Phase 2).

OneK1K (Yazar 2022) provides single-cell eQTL across 14 immune cell types
with 982 donors. When sourced via eQTL Catalogue (QTS000038), the files
have the same column schema as GTEx eQTL, so harmonization reuses the core
eQTL logic from harmonize_eqtl.py.

For onek1k.org direct downloads (GRCh37), a custom parser handles the
different format and applies liftover to GRCh38.

The "tissue" column is set to the cell type name (e.g., "Mono_C").

T-02-12 mitigation: log which source format was used in output metadata.
T-02-13 mitigation: validate input file integrity before processing.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

# Import core eQTL harmonization logic (same schema for eQTL Catalogue format)
from harmonize_eqtl import (
    OUTPUT_COLUMNS,
    _read_eqtl_file,
    write_harmonized,
    harmonize_eqtl,
)

logger = logging.getLogger(__name__)

# OneK1K sample size (982 donors)
ONEK1K_DEFAULT_N = 982


def harmonize_onek1k(
    input_path: str,
    cell_type: str,
    region: dict,
    gene_id: str,
    source_format: str = "eqtl_catalogue",
    config: Optional[dict] = None,
) -> pd.DataFrame:
    """Harmonize OneK1K sc-eQTL data for a single (cell_type, gene, region) triple.

    Parameters
    ----------
    input_path : str
        Path to OneK1K sc-eQTL file (gzipped TSV).
    cell_type : str
        Cell type name (e.g., "Mono_C", "CD4_NC").
    region : dict
        Region window with keys 'chr', 'start', 'end' (GRCh38 coordinates).
    gene_id : str
        Ensembl gene ID to filter on (e.g., ENSG00000140718).
    source_format : str
        Either "eqtl_catalogue" (default, same schema as GTEx) or "onek1k_org"
        (direct download from onek1k.org, GRCh37 format).
    config : dict, optional
        Loaded qtl_sources.yaml content.

    Returns
    -------
    pd.DataFrame
        Harmonized DataFrame with OUTPUT_COLUMNS. The "tissue" column
        contains the cell_type name.
    """
    if config is None:
        config = {}

    # T-02-13: validate input file exists and is non-empty
    if not os.path.exists(input_path):
        logger.error("Input file does not exist: %s", input_path)
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    if os.path.getsize(input_path) == 0:
        logger.error("Input file is empty: %s", input_path)
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Extract OneK1K config
    source_cfg = config.get("sources", {}).get("onek1k_sceqtl", {})
    default_n = source_cfg.get("sample_size", ONEK1K_DEFAULT_N)

    if source_format == "eqtl_catalogue":
        # T-02-12: log source provenance
        logger.info(
            "Harmonizing OneK1K via eQTL Catalogue format (cell_type=%s, gene=%s)",
            cell_type,
            gene_id,
        )
        df = _harmonize_eqtl_catalogue_format(
            input_path, cell_type, region, gene_id, default_n, config
        )
    elif source_format == "onek1k_org":
        # T-02-12: log source provenance
        logger.info(
            "Harmonizing OneK1K via onek1k.org format (cell_type=%s, gene=%s)",
            cell_type,
            gene_id,
        )
        df = _harmonize_onek1k_org_format(
            input_path, cell_type, region, gene_id, default_n, config
        )
    else:
        raise ValueError(
            f"Unknown source_format '{source_format}'. "
            "Expected 'eqtl_catalogue' or 'onek1k_org'."
        )

    return df


def _harmonize_eqtl_catalogue_format(
    input_path: str,
    cell_type: str,
    region: dict,
    gene_id: str,
    default_n: int,
    config: dict,
) -> pd.DataFrame:
    """Harmonize OneK1K data in eQTL Catalogue format.

    Reuses harmonize_eqtl() core logic since the column schema is identical.
    The tissue_name is set to the cell_type (e.g., "Mono_C").
    sdY = 1.0 (eQTL Catalogue re-processes with inverse-normal).
    N = an/2 (with default_n fallback).
    """
    # Delegate to harmonize_eqtl -- the column schema is identical
    # The OneK1K eQTL Catalogue config has the same column mappings as GTEx eQTL
    df = harmonize_eqtl(
        input_path=input_path,
        region=region,
        gene_id=gene_id,
        tissue_name=cell_type,  # cell type goes into tissue column
        tissue_n=default_n,
        config=config,
    )

    return df


def _harmonize_onek1k_org_format(
    input_path: str,
    cell_type: str,
    region: dict,
    gene_id: str,
    default_n: int,
    config: dict,
) -> pd.DataFrame:
    """Harmonize OneK1K data from onek1k.org (GRCh37 format).

    This is the fallback path when eQTL Catalogue is unavailable.
    Data from onek1k.org is in GRCh37 and needs liftover to GRCh38.

    Note: This path requires pyliftover for coordinate conversion.
    """
    # Read the raw file
    df = pd.read_csv(input_path, sep="\t", dtype=str)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # onek1k.org format has different column names
    # Map to internal representation
    # Expected columns: SNP, CHR, BP, A1, A2, BETA, SE, P, MAF, GENE
    col_map = {
        "SNP": "variant_id",
        "CHR": "chromosome",
        "BP": "position",
        "BETA": "beta",
        "SE": "se",
        "P": "pvalue",
        "MAF": "maf",
        "GENE": "gene_id",
    }

    # Rename columns that exist
    rename_map = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Ensure numeric types
    for col in ["position", "beta", "se", "pvalue", "maf"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "chromosome" in df.columns:
        df["chromosome"] = df["chromosome"].astype(str).str.replace("chr", "", regex=False)

    # Liftover from GRCh37 to GRCh38 (required: onek1k_org data is GRCh37,
    # but region filters expect GRCh38; skipping liftover silently drops variants)
    try:
        from pyliftover import LiftOver
    except ImportError:
        raise ImportError(
            "pyliftover is required for onek1k_org format (GRCh37->GRCh38 liftover). "
            "Install with: pip install pyliftover"
        )

    lo = LiftOver("hg19", "hg38")

    def _liftover_pos(chrom, pos):
        result = lo.convert_coordinate(f"chr{chrom}", int(pos))
        if result and len(result) > 0:
            return int(result[0][1])
        return None

    df["position"] = df.apply(
        lambda row: _liftover_pos(row["chromosome"], row["position"]),
        axis=1,
    )
    df = df.dropna(subset=["position"])
    df["position"] = df["position"].astype(int)

    # Region filter
    region_chr = str(region["chr"]).replace("chr", "")
    region_start = int(region["start"])
    region_end = int(region["end"])

    df = df[df["chromosome"] == region_chr].copy()
    df = df[(df["position"] >= region_start) & (df["position"] <= region_end)].copy()

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Gene filter
    gene_prefix = gene_id.split(".")[0]
    if "gene_id" in df.columns:
        df["_gene_prefix"] = df["gene_id"].astype(str).str.split(".").str[0]
        df = df[df["_gene_prefix"] == gene_prefix].copy()
        df.drop(columns=["_gene_prefix"], inplace=True)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Build output
    out = pd.DataFrame()
    out["variant_id"] = df.get("variant_id", pd.Series(["NA"] * len(df))).values
    out["beta"] = df["beta"].values
    out["se"] = df["se"].values
    out["maf"] = df["maf"].values
    out["position"] = df["position"].values
    out["N"] = default_n
    out["sdY"] = 1.0
    out["gene_id"] = df["gene_id"].astype(str).str.split(".").str[0].values
    out["tissue"] = cell_type
    out["pvalue"] = df["pvalue"].values
    out["rsid"] = df.get("rsid", pd.Series(["NA"] * len(df))).values
    out["chromosome"] = df["chromosome"].values

    # Drop rows with missing beta or se
    out = out.dropna(subset=["beta", "se"]).copy()

    # MAF filter
    out = out[(out["maf"] >= 0.005) & (out["maf"] <= 0.995)].copy()

    out = out.reset_index(drop=True)
    return out[OUTPUT_COLUMNS]


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Harmonize OneK1K sc-eQTL data for coloc.susie"
    )
    parser.add_argument("--input", required=True, help="Input OneK1K TSV.gz")
    parser.add_argument(
        "--cell-type",
        required=True,
        help="Cell type name (e.g., Mono_C, CD4_NC)",
    )
    parser.add_argument("--region-chr", required=True, help="Region chromosome")
    parser.add_argument(
        "--region-start", required=True, type=int, help="Region start (GRCh38)"
    )
    parser.add_argument(
        "--region-end", required=True, type=int, help="Region end (GRCh38)"
    )
    parser.add_argument("--gene-id", required=True, help="Ensembl gene ID")
    parser.add_argument(
        "--source-format",
        default="eqtl_catalogue",
        choices=["eqtl_catalogue", "onek1k_org"],
        help="Input data format (default: eqtl_catalogue)",
    )
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

    df = harmonize_onek1k(
        input_path=args.input,
        cell_type=args.cell_type,
        region=region,
        gene_id=args.gene_id,
        source_format=args.source_format,
        config=config,
    )

    if df.empty:
        logger.warning(
            "No variants after harmonization for %s / %s",
            args.gene_id,
            args.cell_type,
        )

    write_harmonized(df, args.output)
    print(
        f"[harmonize_onek1k] wrote {len(df)} variants to {args.output} "
        f"(gene={args.gene_id}, cell_type={args.cell_type}, "
        f"source={args.source_format})"
    )


if __name__ == "__main__":
    main()
