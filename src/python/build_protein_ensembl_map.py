#!/usr/bin/env python3
"""Build protein name -> Ensembl gene ID lookup for UKB-PPP.

Parses UKB-PPP Olink metadata (olink_protein_map_3k_v1.tsv from Synapse
syn51365301) to build a mapping from protein names to Ensembl gene IDs.
Falls back to HGNC REST API if metadata not available.

Output: TSV with columns protein_name, hgnc_symbol, ensembl_gene_id.
"""

import argparse
import json
import logging
import re
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def build_from_metadata(metadata_path: str) -> pd.DataFrame:
    """Build protein-to-Ensembl map from UKB-PPP Olink metadata.

    Parameters
    ----------
    metadata_path : str
        Path to olink_protein_map_3k_v1.tsv from Synapse syn51365301.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: protein_name, hgnc_symbol, ensembl_gene_id.
    """
    df = pd.read_csv(metadata_path, sep="\t")

    # Expected columns in the Olink metadata (names may vary slightly)
    # Look for gene symbol and Ensembl ID columns
    gene_col = None
    ensembl_col = None

    for col in df.columns:
        col_lower = col.lower()
        if "gene" in col_lower and "symbol" in col_lower:
            gene_col = col
        elif "hgnc" in col_lower and "symbol" in col_lower:
            gene_col = col
        elif "ensembl" in col_lower:
            ensembl_col = col

    if gene_col is None:
        raise ValueError(
            f"Could not find gene symbol column in metadata. "
            f"Available columns: {list(df.columns)}"
        )

    # Build the mapping
    records = []
    for _, row in df.iterrows():
        protein_name = str(row.get("Assay", row.get("protein", row.iloc[0])))
        hgnc_symbol = str(row[gene_col]) if gene_col else protein_name
        ensembl_id = str(row[ensembl_col]) if ensembl_col else ""

        records.append({
            "protein_name": protein_name,
            "hgnc_symbol": hgnc_symbol,
            "ensembl_gene_id": ensembl_id,
        })

    result = pd.DataFrame(records)

    # Validate Ensembl IDs
    valid_mask = result["ensembl_gene_id"].str.match(r"^ENSG\d+", na=False)
    n_valid = valid_mask.sum()
    n_total = len(result)
    logger.info(
        "Mapped %d / %d proteins to Ensembl gene IDs from metadata", n_valid, n_total
    )

    if n_valid < n_total:
        unmapped = result[~valid_mask]["protein_name"].tolist()
        logger.warning("Unmapped proteins: %s", unmapped[:10])

    return result


def build_from_hgnc_api(gene_symbols: list) -> pd.DataFrame:
    """Build protein-to-Ensembl map via HGNC REST API.

    Parameters
    ----------
    gene_symbols : list
        List of HGNC gene symbols to resolve.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: protein_name, hgnc_symbol, ensembl_gene_id.
    """
    records = []

    for symbol in gene_symbols:
        try:
            url = f"https://rest.genenames.org/fetch/symbol/{symbol}"
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            docs = data.get("response", {}).get("docs", [])
            if docs:
                doc = docs[0]
                ensembl_id = doc.get("ensembl_gene_id", "")
                records.append({
                    "protein_name": symbol,
                    "hgnc_symbol": doc.get("symbol", symbol),
                    "ensembl_gene_id": ensembl_id,
                })
            else:
                logger.warning("HGNC API: no results for symbol '%s'", symbol)
                records.append({
                    "protein_name": symbol,
                    "hgnc_symbol": symbol,
                    "ensembl_gene_id": "",
                })

            # Rate limiting: max 10 requests per second
            time.sleep(0.1)

        except Exception as e:
            logger.warning("HGNC API error for '%s': %s", symbol, e)
            records.append({
                "protein_name": symbol,
                "hgnc_symbol": symbol,
                "ensembl_gene_id": "",
            })

    result = pd.DataFrame(records)

    valid_mask = result["ensembl_gene_id"].str.match(r"^ENSG\d+", na=False)
    logger.info(
        "Mapped %d / %d symbols to Ensembl IDs via HGNC API",
        valid_mask.sum(),
        len(result),
    )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Build protein -> Ensembl gene ID lookup for UKB-PPP"
    )
    parser.add_argument(
        "--ukbppp-metadata",
        default=None,
        help="Path to UKB-PPP olink_protein_map_3k_v1.tsv (from Synapse syn51365301)",
    )
    parser.add_argument(
        "--gene-symbols",
        nargs="*",
        default=None,
        help="Protein/gene symbols to resolve via HGNC API (if no metadata file)",
    )
    parser.add_argument(
        "--output",
        default="data/external/ukbppp_protein_to_ensembl.tsv",
        help="Output TSV path",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.ukbppp_metadata and Path(args.ukbppp_metadata).exists():
        logger.info("Building map from UKB-PPP metadata: %s", args.ukbppp_metadata)
        result = build_from_metadata(args.ukbppp_metadata)
    elif args.gene_symbols:
        logger.info("Building map from HGNC API for %d symbols", len(args.gene_symbols))
        result = build_from_hgnc_api(args.gene_symbols)
    else:
        logger.error(
            "Either --ukbppp-metadata or --gene-symbols must be provided"
        )
        sys.exit(1)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, sep="\t", index=False)

    # Validation
    valid = result["ensembl_gene_id"].str.match(r"^ENSG\d+", na=False).sum()
    total = len(result)
    print(
        f"[build_protein_ensembl_map] Wrote {total} entries to {output_path} "
        f"({valid} with valid Ensembl IDs)"
    )


if __name__ == "__main__":
    main()
