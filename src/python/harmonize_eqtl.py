#!/usr/bin/env python3
"""Harmonize eQTL Catalogue GTEx v8 eQTL data for coloc.susie (Phase 2).

Reads an eQTL Catalogue all-pairs TSV (gzipped, optionally tabix-indexed) and
outputs a standardized harmonized TSV for a single (gene x tissue x region)
triple. The output format is the common intermediate consumed by run_qtl_coloc.R.

Columns follow the mapping from config/qtl_sources.yaml::sources::gtex_eqtl.

T-02-07 mitigation: variants outside the region window are dropped.
"""

import argparse
import gzip
import logging
import sys
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

# Common intermediate output columns (shared across all QTL sources)
OUTPUT_COLUMNS = [
    "variant_id",
    "beta",
    "se",
    "maf",
    "position",
    "N",
    "sdY",
    "gene_id",
    "tissue",
    "pvalue",
    "rsid",
    "chromosome",
]


def harmonize_eqtl(
    input_path: str,
    region: dict,
    gene_id: str,
    tissue_name: str,
    tissue_n: int,
    config: dict,
) -> pd.DataFrame:
    """Harmonize eQTL Catalogue data for a single (gene, tissue, region) triple.

    Parameters
    ----------
    input_path : str
        Path to eQTL Catalogue all-pairs TSV file (gzipped).
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
    # Extract column mapping from config
    source_cfg = config.get("sources", {}).get("gtex_eqtl", {})
    col_map = source_cfg.get("columns", {})

    # Read input (try pysam tabix first, fallback to pandas)
    df = _read_eqtl_file(input_path, region)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Column name normalization: rename from eQTL Catalogue names to internal
    beta_col = col_map.get("beta", "beta")
    se_col = col_map.get("se", "se")
    pval_col = col_map.get("pvalue", "pvalue")
    maf_col = col_map.get("maf", "maf")
    gene_col = col_map.get("gene_id", "gene_id")
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

    # Gene filter (match on Ensembl ID prefix, ignoring version suffix)
    gene_prefix = gene_id.split(".")[0]
    df["_gene_prefix"] = df[gene_col].astype(str).str.split(".").str[0]
    df = df[df["_gene_prefix"] == gene_prefix].copy()
    df.drop(columns=["_gene_prefix"], inplace=True)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Compute N = an / 2
    if sample_size_field in df.columns:
        df["N"] = (pd.to_numeric(df[sample_size_field], errors="coerce") / 2).astype(
            "Int64"
        )
    else:
        df["N"] = tissue_n

    # Set sdY = 1.0 (GTEx inverse-normal transformed)
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
    out["gene_id"] = df[gene_col].astype(str).str.split(".").str[0].values
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


def _read_eqtl_file(
    input_path: str, region: dict
) -> pd.DataFrame:
    """Read an eQTL Catalogue TSV file, optionally using tabix for region query.

    Falls back to pandas chunked reading if pysam is not available or if no
    tabix index (.tbi) file exists alongside the input.
    """
    tbi_path = input_path + ".tbi"

    # Try pysam tabix first
    if Path(tbi_path).exists():
        try:
            import pysam

            return _read_with_tabix(input_path, region)
        except ImportError:
            logger.info("pysam not available, falling back to pandas")
        except Exception as e:
            logger.warning("tabix query failed (%s), falling back to pandas", e)

    # Pandas fallback
    return _read_with_pandas(input_path)


def _read_with_tabix(input_path: str, region: dict) -> pd.DataFrame:
    """Read region slice via pysam TabixFile."""
    import pysam

    region_chr = str(region["chr"])
    region_start = int(region["start"])
    region_end = int(region["end"])

    tbx = pysam.TabixFile(input_path)
    header = tbx.header
    if header:
        col_names = header[-1].lstrip("#").split("\t")
    else:
        # Read first line manually to get column names
        with gzip.open(input_path, "rt") as f:
            col_names = f.readline().strip().split("\t")

    # Try with and without 'chr' prefix
    rows = []
    for chr_fmt in [region_chr, f"chr{region_chr}", region_chr.replace("chr", "")]:
        try:
            for row in tbx.fetch(chr_fmt, region_start, region_end):
                rows.append(row.split("\t"))
            if rows:
                break
        except ValueError:
            continue

    tbx.close()

    if not rows:
        return pd.DataFrame(columns=col_names)

    return pd.DataFrame(rows, columns=col_names)


def _read_with_pandas(input_path: str) -> pd.DataFrame:
    """Read entire gzipped TSV via pandas."""
    return pd.read_csv(input_path, sep="\t", dtype=str)


def write_harmonized(df: pd.DataFrame, output_path: str) -> None:
    """Write harmonized DataFrame to gzipped TSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False, compression="gzip")


def main():
    parser = argparse.ArgumentParser(
        description="Harmonize eQTL Catalogue data for coloc.susie"
    )
    parser.add_argument("--input", required=True, help="Input eQTL Catalogue TSV.gz")
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

    df = harmonize_eqtl(
        input_path=args.input,
        region=region,
        gene_id=args.gene_id,
        tissue_name=args.tissue_name,
        tissue_n=args.tissue_n,
        config=config,
    )

    if df.empty:
        logger.warning("No variants after harmonization for %s / %s", args.gene_id, args.tissue_name)

    write_harmonized(df, args.output)
    print(
        f"[harmonize_eqtl] wrote {len(df)} variants to {args.output} "
        f"(gene={args.gene_id}, tissue={args.tissue_name})"
    )


if __name__ == "__main__":
    main()
