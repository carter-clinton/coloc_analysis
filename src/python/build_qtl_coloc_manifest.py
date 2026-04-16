#!/usr/bin/env python3
"""Build QTL colocalization manifest by cross-joining regions x QTL sources.

Produces a TSV with one row per (region x qtl_source x tissue x gene x ancestry)
combination, used by run_qtl_coloc to dispatch individual coloc jobs.

For each row, derives paths to:
  - GWAS SuSiE fit (.fit.rds)
  - LD matrix (.rds)
  - Harmonized QTL sumstats (.harmonized.tsv.gz)

Rows are emitted even if the underlying files do not yet exist on disk
(Snakemake will create them via upstream rules).

Usage:
    python build_qtl_coloc_manifest.py \
        --regions config/regions_curated_grch38.csv \
        --qtl-sources config/qtl_sources.yaml \
        --tissue-n-lookup data/processed/qtl_harmonized/gtex_tissue_n_lookup.json \
        --results-root results \
        --ld-reference data/processed/ld_reference \
        --harmonized-dir data/processed/qtl_harmonized \
        --output results/qtl_coloc/qtl_coloc_manifest.tsv
"""
import argparse
import csv
import json
import logging
import os
import sys

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build QTL colocalization manifest"
    )
    parser.add_argument("--regions", required=True,
                        help="Curated regions CSV (GRCh38 coordinates)")
    parser.add_argument("--qtl-sources", required=True,
                        help="QTL sources YAML config")
    parser.add_argument("--tissue-n-lookup", required=True,
                        help="JSON mapping tissue name -> sample size")
    parser.add_argument("--results-root", required=True,
                        help="Pipeline results root directory")
    parser.add_argument("--ld-reference", required=True,
                        help="LD reference directory")
    parser.add_argument("--harmonized-dir", required=True,
                        help="Harmonized QTL data directory")
    parser.add_argument("--output", required=True,
                        help="Output manifest TSV path")
    return parser.parse_args()


def load_regions(path):
    """Load curated regions CSV."""
    regions = []
    with open(path) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            regions.append(row)
    return regions


def load_qtl_sources(path):
    """Load QTL sources YAML config."""
    with open(path) as fh:
        cfg = yaml.safe_load(fh)
    return cfg.get("sources", {})


def load_tissue_n(path):
    """Load tissue name -> sample size lookup."""
    with open(path) as fh:
        return json.load(fh)


def _tissues_for_source(source_name, source_cfg):
    """Determine tissue list for a QTL source.

    GTEx eQTL/sQTL: all tissues from tissue_n_lookup (populated at runtime).
    OneK1K: cell_types list from config.
    UKB-PPP pQTL: single pseudo-tissue 'plasma'.
    """
    if "cell_types" in source_cfg:
        return source_cfg["cell_types"]
    # pQTL sources have a single tissue
    if source_cfg.get("data_type") == "pQTL":
        return ["plasma"]
    # For GTEx sources, tissues are determined from the lookup at runtime
    return None  # sentinel: use tissue_n_lookup keys


def _genes_for_region(region):
    """Extract gene list from a region row.

    The 'gene' field may contain multiple genes separated by '/' or ';'.
    Returns a list of gene symbols, filtering out NA/empty.
    """
    gene_field = region.get("gene", "")
    if not gene_field or gene_field.upper() == "NA":
        return []
    # Split on / or ;
    genes = []
    for part in gene_field.replace(";", "/").split("/"):
        g = part.strip()
        if g and g.upper() != "NA":
            genes.append(g)
    return genes if genes else [region.get("region_id", "unknown")]


def _ancestry_for_region(region):
    """Determine ancestry from the region's trait list.

    For now, emit EUR for all regions (GTEx is EUR-only).
    AFR-ancestry QTL data is limited; we include EUR as primary.
    """
    return "EUR"


def build_manifest(regions, qtl_sources, tissue_n_lookup,
                   results_root, ld_reference, harmonized_dir):
    """Build manifest rows by cross-joining regions x sources x tissues x genes."""
    rows = []

    for source_name, source_cfg in qtl_sources.items():
        sdy = source_cfg.get("sdY", source_cfg.get("sdy", 1.0))
        if sdy is None:
            sdy = 1.0

        # Determine tissues for this source
        source_tissues = _tissues_for_source(source_name, source_cfg)
        if source_tissues is None:
            # Use tissue_n_lookup keys (GTEx eQTL/sQTL)
            source_tissues = sorted(tissue_n_lookup.keys())

        data_type_dir = (source_name.replace("gtex_", "")
                         .replace("ukbppp_", "")
                         .replace("onek1k_", ""))

        for region in regions:
            region_id = region.get("region_id", "")
            chrom = region.get("chr", "")
            start = region.get("start_grch38", "")
            end = region.get("end_grch38", "")
            trait_list = region.get("trait_list", "")
            genes = _genes_for_region(region)
            ancestry = _ancestry_for_region(region)

            # Derive GWAS trait from region (use first trait)
            traits = [t.strip() for t in trait_list.split(";") if t.strip()]
            gwas_trait = traits[0] if traits else "unknown"

            for tissue in source_tissues:
                tissue_n = tissue_n_lookup.get(tissue, source_cfg.get("sample_size", 0))
                if tissue_n is None:
                    tissue_n = 0

                for gene in genes:
                    # Build unique coloc ID
                    qtl_coloc_id = f"{region_id}_{gene}_{source_name}_{tissue}"
                    # Sanitize ID: replace problematic chars
                    qtl_coloc_id = (qtl_coloc_id
                                    .replace(" ", "_")
                                    .replace("?", "")
                                    .replace("(", "")
                                    .replace(")", ""))

                    # Derive file paths
                    gwas_fit_path = os.path.join(
                        results_root, "fine_mapping", "susie",
                        f"{gwas_trait}.{ancestry}.{region_id}.fit.rds"
                    )
                    ld_matrix_path = os.path.join(
                        ld_reference, ancestry,
                        f"{region_id}.rds"
                    )
                    dataset_id = tissue  # dataset_id varies by source
                    harmonized_qtl_path = os.path.join(
                        harmonized_dir, data_type_dir,
                        dataset_id, gene,
                        f"{region_id}.harmonized.tsv.gz"
                    )

                    rows.append({
                        "qtl_coloc_id": qtl_coloc_id,
                        "qtl_source": source_name,
                        "tissue": tissue,
                        "gene_id": gene,
                        "region": region_id,
                        "ancestry": ancestry,
                        "gwas_trait": gwas_trait,
                        "dataset_id": dataset_id,
                        "chr": chrom,
                        "start_grch38": start,
                        "end_grch38": end,
                        "tissue_n": str(tissue_n),
                        "sdy": str(sdy),
                        "gwas_fit_path": gwas_fit_path,
                        "ld_matrix_path": ld_matrix_path,
                        "harmonized_qtl_path": harmonized_qtl_path,
                    })

    return rows


def main():
    args = parse_args()

    regions = load_regions(args.regions)
    logger.info("Loaded %d regions from %s", len(regions), args.regions)

    qtl_sources = load_qtl_sources(args.qtl_sources)
    logger.info("Loaded %d QTL sources from %s", len(qtl_sources), args.qtl_sources)

    tissue_n_lookup = load_tissue_n(args.tissue_n_lookup)
    logger.info("Loaded %d tissue N entries from %s", len(tissue_n_lookup), args.tissue_n_lookup)

    rows = build_manifest(
        regions, qtl_sources, tissue_n_lookup,
        args.results_root, args.ld_reference, args.harmonized_dir,
    )

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    fieldnames = [
        "qtl_coloc_id", "qtl_source", "tissue", "gene_id", "region",
        "ancestry", "gwas_trait", "dataset_id", "chr", "start_grch38",
        "end_grch38", "tissue_n", "sdy", "gwas_fit_path", "ld_matrix_path",
        "harmonized_qtl_path",
    ]
    with open(args.output, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Wrote %d manifest rows to %s", len(rows), args.output)


if __name__ == "__main__":
    main()
