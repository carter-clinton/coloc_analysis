#!/usr/bin/env python3
"""Harmonize UKB-PPP pQTL REGENIE output for coloc.susie (Phase 2).

Reads UKB-PPP REGENIE output and produces the common intermediate TSV format
consumed by run_qtl_coloc.R. Column mapping follows
config/qtl_sources.yaml::sources::ukbppp_pqtl.

T-02-09 mitigation: validates expected REGENIE columns before processing.

Key differences from eQTL/sQTL harmonization:
- REGENIE uses LOG10P (not pvalue): pvalue = 10^(-LOG10P)
- variant_id must be constructed: chr{CHROM}_{GENPOS}_{ALLELE0}_{ALLELE1}
- sdY is not 1.0; must be estimated or passed explicitly
- gene_id maps protein_name to Ensembl via a lookup table
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
import yaml

from estimate_sdy import estimate_sdy

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

# Required REGENIE columns (T-02-09 mitigation)
REQUIRED_REGENIE_COLUMNS = {
    "CHROM",
    "GENPOS",
    "ID",
    "ALLELE0",
    "ALLELE1",
    "A1FREQ",
    "BETA",
    "SE",
    "LOG10P",
}


def _load_protein_ensembl_map(
    map_path: str = "data/external/ukbppp_protein_to_ensembl.tsv",
) -> dict:
    """Load protein name -> Ensembl gene ID lookup from TSV.

    Parameters
    ----------
    map_path : str
        Path to the protein-to-Ensembl TSV (columns: protein_name, hgnc_symbol,
        ensembl_gene_id).

    Returns
    -------
    dict
        Mapping of protein_name -> ensembl_gene_id.
    """
    path = Path(map_path)
    if not path.exists():
        logger.warning(
            "Protein-to-Ensembl map not found at %s; gene_id will be set to "
            "protein_name. Run build_protein_ensembl_map.py to create it.",
            map_path,
        )
        return {}

    df = pd.read_csv(path, sep="\t")
    return dict(zip(df["protein_name"], df["ensembl_gene_id"]))


def harmonize_pqtl(
    input_path: str,
    region: dict,
    protein_name: str,
    sample_size: int,
    sdy: Union[float, str],
    config: dict,
    protein_ensembl_map: Optional[dict] = None,
) -> pd.DataFrame:
    """Harmonize UKB-PPP pQTL REGENIE output for a single (protein, region) pair.

    Parameters
    ----------
    input_path : str
        Path to UKB-PPP per-protein REGENIE file (gzipped).
    region : dict
        Region window with keys 'chr', 'start', 'end' (GRCh38 coordinates).
    protein_name : str
        Protein identifier (used as "tissue" in common format).
    sample_size : int
        Sample size fallback (default 54219 from Sun 2023).
    sdy : float or str
        sdY value. Pass a float to use directly, or "estimate" to compute from data.
    config : dict
        Loaded qtl_sources.yaml content.
    protein_ensembl_map : dict, optional
        Mapping of protein_name -> Ensembl gene ID. If None, attempts to load
        from data/external/ukbppp_protein_to_ensembl.tsv.

    Returns
    -------
    pd.DataFrame
        Harmonized DataFrame with OUTPUT_COLUMNS.
    """
    # Extract column mapping from config
    source_cfg = config.get("sources", {}).get("ukbppp_pqtl", {})
    col_map = source_cfg.get("columns", {})

    # Read REGENIE output (space or tab-delimited, gzipped)
    df = pd.read_csv(input_path, sep=r"\s+", dtype=str)

    # T-02-09: Validate expected columns
    missing_cols = REQUIRED_REGENIE_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"REGENIE file missing required columns: {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )

    # Convert numeric columns
    chrom_col = col_map.get("chromosome", "CHROM")
    pos_col = col_map.get("position", "GENPOS")
    beta_col = col_map.get("beta", "BETA")
    se_col = col_map.get("se", "SE")
    log10p_col = col_map.get("pvalue_log10", "LOG10P")
    maf_col = col_map.get("maf", "A1FREQ")
    allele_ref_col = col_map.get("allele_ref", "ALLELE0")
    allele_alt_col = col_map.get("allele_alt", "ALLELE1")
    n_col = col_map.get("sample_size", "N")
    info_col = col_map.get("info", "INFO")
    snp_id_col = col_map.get("snp_id", "ID")

    df[pos_col] = pd.to_numeric(df[pos_col], errors="coerce")
    df[beta_col] = pd.to_numeric(df[beta_col], errors="coerce")
    df[se_col] = pd.to_numeric(df[se_col], errors="coerce")
    df[log10p_col] = pd.to_numeric(df[log10p_col], errors="coerce")
    df[maf_col] = pd.to_numeric(df[maf_col], errors="coerce")
    df[chrom_col] = df[chrom_col].astype(str).str.replace("chr", "", regex=False)

    if info_col in df.columns:
        df[info_col] = pd.to_numeric(df[info_col], errors="coerce")
    if n_col in df.columns:
        df[n_col] = pd.to_numeric(df[n_col], errors="coerce")

    # Region filter
    region_chr = str(region["chr"]).replace("chr", "")
    region_start = int(region["start"])
    region_end = int(region["end"])

    df = df[df[chrom_col] == region_chr].copy()
    df = df[(df[pos_col] >= region_start) & (df[pos_col] <= region_end)].copy()

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Construct variant_id: chr{CHROM}_{GENPOS}_{ALLELE0}_{ALLELE1}
    df["variant_id"] = (
        "chr"
        + df[chrom_col].astype(str)
        + "_"
        + df[pos_col].astype(int).astype(str)
        + "_"
        + df[allele_ref_col].astype(str)
        + "_"
        + df[allele_alt_col].astype(str)
    )

    # MAF: ensure 0 < maf < 1; flip if A1FREQ > 0.5
    df["maf"] = df[maf_col].copy()
    df.loc[df["maf"] > 0.5, "maf"] = 1.0 - df.loc[df["maf"] > 0.5, "maf"]

    # pvalue = 10^(-LOG10P)
    # Clip LOG10P: lower bound 0 (pvalue <= 1.0) and upper bound 300 (avoid underflow)
    df["pvalue"] = 10.0 ** (-df[log10p_col].clip(lower=0, upper=300))

    # N: use per-row N if available, else fallback to sample_size arg
    if n_col in df.columns:
        df["N"] = df[n_col].fillna(sample_size).astype(int)
    else:
        df["N"] = sample_size

    # gene_id: map protein_name to Ensembl ID
    if protein_ensembl_map is None:
        protein_ensembl_map = _load_protein_ensembl_map()

    ensembl_id = protein_ensembl_map.get(protein_name, protein_name)
    if not str(ensembl_id).startswith("ENSG"):
        logger.warning(
            "Protein '%s' not mapped to Ensembl gene ID (using '%s'). "
            "Run build_protein_ensembl_map.py for proper mapping.",
            protein_name,
            ensembl_id,
        )

    # INFO filter: drop rows with INFO < 0.3
    if info_col in df.columns:
        df = df[df[info_col] >= 0.3].copy()

    # Drop rows with missing beta or se
    df = df.dropna(subset=[beta_col, se_col]).copy()

    # MAF filter: drop rows where maf < 0.005 or maf > 0.995
    df = df[(df["maf"] >= 0.005) & (df["maf"] <= 0.995)].copy()

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # sdY handling
    if isinstance(sdy, str) and sdy.lower() == "estimate":
        sdy_value = estimate_sdy(
            beta=df[beta_col].values,
            se=df[se_col].values,
            maf=df["maf"].values,
            n=sample_size,
        )
        logger.info("Estimated sdY = %.6f for protein %s", sdy_value, protein_name)
    else:
        sdy_value = float(sdy)

    # Build output DataFrame
    out = pd.DataFrame()
    out["variant_id"] = df["variant_id"].values
    out["beta"] = df[beta_col].values
    out["se"] = df[se_col].values
    out["maf"] = df["maf"].values
    out["position"] = df[pos_col].values.astype(int)
    out["N"] = df["N"].values
    out["sdY"] = sdy_value
    out["gene_id"] = ensembl_id
    out["tissue"] = protein_name
    out["pvalue"] = df["pvalue"].values
    out["rsid"] = df[snp_id_col].values if snp_id_col in df.columns else "NA"
    out["chromosome"] = df[chrom_col].values

    out = out.reset_index(drop=True)
    return out[OUTPUT_COLUMNS]


def write_harmonized(df: pd.DataFrame, output_path: str) -> None:
    """Write harmonized DataFrame to gzipped TSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False, compression="gzip")


def main():
    parser = argparse.ArgumentParser(
        description="Harmonize UKB-PPP pQTL REGENIE data for coloc.susie"
    )
    parser.add_argument(
        "--input", required=True, help="Input UKB-PPP per-protein file (gzipped)"
    )
    parser.add_argument("--region-chr", required=True, help="Region chromosome")
    parser.add_argument(
        "--region-start", required=True, type=int, help="Region start (GRCh38)"
    )
    parser.add_argument(
        "--region-end", required=True, type=int, help="Region end (GRCh38)"
    )
    parser.add_argument(
        "--protein-name", required=True, help="Protein identifier"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=54219,
        help="Sample size (default: 54219 from Sun 2023)",
    )
    parser.add_argument(
        "--sdy",
        required=True,
        help='sdY value (float) or "estimate" to compute from data',
    )
    parser.add_argument(
        "--qtl-source-config", required=True, help="Path to qtl_sources.yaml"
    )
    parser.add_argument(
        "--output", required=True, help="Output harmonized TSV.gz path"
    )
    parser.add_argument(
        "--protein-ensembl-map",
        default="data/external/ukbppp_protein_to_ensembl.tsv",
        help="Path to protein-to-Ensembl lookup TSV",
    )

    args = parser.parse_args()

    with open(args.qtl_source_config) as f:
        config = yaml.safe_load(f)

    region = {
        "chr": args.region_chr,
        "start": args.region_start,
        "end": args.region_end,
    }

    # Load protein-Ensembl map
    protein_ensembl_map = _load_protein_ensembl_map(args.protein_ensembl_map)

    # Parse sdy: either float or "estimate"
    try:
        sdy = float(args.sdy)
    except ValueError:
        sdy = args.sdy  # "estimate"

    df = harmonize_pqtl(
        input_path=args.input,
        region=region,
        protein_name=args.protein_name,
        sample_size=args.sample_size,
        sdy=sdy,
        config=config,
        protein_ensembl_map=protein_ensembl_map,
    )

    if df.empty:
        logger.warning(
            "No variants after harmonization for %s", args.protein_name
        )

    write_harmonized(df, args.output)
    print(
        f"[harmonize_pqtl] wrote {len(df)} variants to {args.output} "
        f"(protein={args.protein_name})"
    )


if __name__ == "__main__":
    main()
