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


# ---------------------------------------------------------------------------
# Identifier convention normalization (Stage B.5 audit fix, 2026-04-20)
# ---------------------------------------------------------------------------
#
# build_qtl_coloc_manifest.py is the single source of truth for the
# results/qtl_coloc/qtl_coloc_manifest.tsv TSV. Downstream consumers
# (harmonize_eqtl.py, harmonize_sqtl.py, harmonize_onek1k.py, Phase 1
# SuSiE fit filenames, pipeline.yaml trait keys) expect specific
# identifier conventions that do NOT match the short codes used in
# config/regions_curated_grch38.csv (the upstream source).
#
# Rather than couple every harmonize_*.py script to a shared alias
# dependency, we normalize at the manifest-builder boundary. See
# .planning/debug/t1_phase2_first_production.md (Stage B.5 Audit) for
# the column-by-column downstream-consumer audit that motivated these
# maps.

# Trait short code -> long name used by pipeline.yaml trait_ancestries
# keys and Phase 1 SuSiE fit filenames (hypertension.EUR.*.fit.rds).
# "stroke" has no short-code variant (used verbatim). Extend as new
# traits enter regions_curated_grch38.csv.
TRAIT_ALIASES = {
    "htn": "hypertension",
    # "cad", "ckd", "obesity" appear as SECOND/THIRD traits in some
    # regions_curated_grch38.csv rows but build_qtl_coloc_manifest.py
    # selects traits[0] only, so those aliases are not currently needed.
}

# Gene symbol -> canonical Ensembl gene ID (GRCh38). Used by eQTL/sQTL/
# sc-eQTL rows only; harmonize_eqtl.py (shared across all three) filters
# GTEx gene_id column by Ensembl prefix match and would drop every row
# when filtered against a gene SYMBOL. Hand-curated against Ensembl 111
# (release matching GENCODE v45 used by GTEx v8 eQTL Catalogue pipeline).
#
# For pQTL (ukbppp_pqtl) we intentionally keep the gene SYMBOL in the
# manifest's gene_id column because the UKB-PPP Synapse files are named
# by protein symbol (discovery_chr{chrom}_{protein}.gz) and the harmonize
# rule passes gene_id as --protein-name. Cross-source aggregation in
# aggregate_qtl_coloc.py therefore sees mixed IDs — this is documented as
# BUG-AUDIT-03 in the debug file and accepted for Stage B.5 scope.
#
# HLA is a multi-gene locus with ~40 genes. We use HLA-A (ENSG00000206503)
# as a proxy pointer — real Tier A assignment for HLA regions requires
# post-hoc audit. Flagged in debug file BUG-AUDIT-02.
GENE_SYMBOL_TO_ENSEMBL = {
    "FTO": "ENSG00000140718",
    "MC4R": "ENSG00000166603",
    "SH2B3": "ENSG00000111252",
    "APOL1": "ENSG00000100342",
    "PYHIN1": "ENSG00000163564",
    "CXADR": "ENSG00000154639",
    "F2RL1": "ENSG00000164251",
    "CDKN2A": "ENSG00000147889",
    "APOE": "ENSG00000130203",
    "HLA": "ENSG00000206503",     # HLA-A proxy; audit required post-smoke
    "SLC2A9": "ENSG00000109107",
    # Distal regulatory targets added 2026-04-21 per RECOVERY_PLAN Stage 3
    # Option-C scope. Verified against Ensembl REST /lookup/id (GRCh38).
    # Pre-registration: see DECISIONS.md 2026-04-21 entry.
    "IRX3":  "ENSG00000177508",   # FTO_16q12 distal target (Smemo 2014, Claussnitzer 2015)
    "ATXN2": "ENSG00000204842",   # SH2B3_12q24 distal target (Machiela 2011, Kato 2011)
}

# Sources that require Ensembl gene_id in the manifest. pQTL is excluded
# per note above.
SOURCES_REQUIRING_ENSEMBL = {"gtex_eqtl", "gtex_sqtl", "onek1k_sceqtl"}


def _normalize_trait(short_code: str) -> str:
    """Resolve trait short code to canonical long name per TRAIT_ALIASES.

    Pass through unchanged when no alias is registered — lets future
    traits (e.g., 'cad', 'ckd') emit loudly as "missing Phase 1 fit" at
    harmonize_sumstats resolution time rather than silently mistranslate.
    """
    return TRAIT_ALIASES.get(short_code, short_code)


def _resolve_gene_identifier(gene_symbol: str, qtl_source: str) -> str:
    """Resolve a gene symbol to the identifier convention this source expects.

    eQTL/sQTL/sc-eQTL sources expect Ensembl gene IDs (ENSG...) since
    harmonize_eqtl.py filters GTEx files' gene_id column by Ensembl ID.
    pQTL sources keep the gene symbol since UKB-PPP files are named by
    protein symbol. Unmapped symbols get a WARNING and pass through
    unchanged so the symptom surfaces loudly downstream.
    """
    if qtl_source not in SOURCES_REQUIRING_ENSEMBL:
        return gene_symbol
    ensembl = GENE_SYMBOL_TO_ENSEMBL.get(gene_symbol)
    if ensembl is None:
        logger.warning(
            "Gene symbol '%s' has no Ensembl mapping in GENE_SYMBOL_TO_ENSEMBL "
            "(qtl_source=%s). Downstream harmonize_%s.py will filter to zero "
            "variants for this row. Extend GENE_SYMBOL_TO_ENSEMBL in "
            "build_qtl_coloc_manifest.py to fix.",
            gene_symbol,
            qtl_source,
            qtl_source.replace("gtex_", "").replace("onek1k_", ""),
        )
        return gene_symbol
    return ensembl


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

            # Derive GWAS trait from region (use first trait). Normalize
            # short codes to canonical long names so the trait matches
            # pipeline.yaml trait_ancestries keys and Phase 1 SuSiE fit
            # filenames (Stage B.5 BUG-AUDIT-01).
            traits = [t.strip() for t in trait_list.split(";") if t.strip()]
            raw_trait = traits[0] if traits else "unknown"
            gwas_trait = _normalize_trait(raw_trait)

            for tissue in source_tissues:
                tissue_n = tissue_n_lookup.get(tissue, source_cfg.get("sample_size", 0))
                if tissue_n is None:
                    tissue_n = 0

                for gene_symbol in genes:
                    # Resolve gene symbol to the identifier convention
                    # this qtl_source expects. eQTL/sQTL/sc-eQTL require
                    # Ensembl IDs to match GTEx file gene_id column
                    # (Stage B.5 BUG-AUDIT-02). pQTL keeps the symbol
                    # because UKB-PPP files are symbol-named
                    # (BUG-AUDIT-03).
                    gene_id = _resolve_gene_identifier(gene_symbol, source_name)

                    # Build unique coloc ID. Use the resolved gene_id
                    # (Ensembl for non-pQTL, symbol for pQTL) so IDs
                    # cross-reference cleanly with the harmonized path.
                    qtl_coloc_id = f"{region_id}_{gene_id}_{source_name}_{tissue}"
                    # Sanitize ID: replace problematic chars
                    qtl_coloc_id = (qtl_coloc_id
                                    .replace(" ", "_")
                                    .replace("?", "")
                                    .replace("(", "")
                                    .replace(")", ""))

                    # Derive file paths. gwas_trait is already alias-normalized;
                    # gene_id is resolved per source.
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
                        dataset_id, gene_id,
                        f"{region_id}.harmonized.tsv.gz"
                    )

                    rows.append({
                        "qtl_coloc_id": qtl_coloc_id,
                        "qtl_source": source_name,
                        "tissue": tissue,
                        "gene_id": gene_id,
                        "gene_symbol": gene_symbol,
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
    # gene_symbol is additive (Stage B.5): preserves the original symbol
    # from regions_curated_grch38.csv for traceability / downstream joins.
    # Existing consumers that read by column name (not position) are
    # unaffected because csv.DictReader looks up by header key.
    fieldnames = [
        "qtl_coloc_id", "qtl_source", "tissue", "gene_id", "gene_symbol",
        "region", "ancestry", "gwas_trait", "dataset_id", "chr",
        "start_grch38", "end_grch38", "tissue_n", "sdy", "gwas_fit_path",
        "ld_matrix_path", "harmonized_qtl_path",
    ]
    with open(args.output, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Wrote %d manifest rows to %s", len(rows), args.output)


if __name__ == "__main__":
    main()
