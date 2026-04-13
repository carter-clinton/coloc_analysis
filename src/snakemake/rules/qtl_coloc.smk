"""Manifest-driven QTL colocalization dispatch (Phase 2).

Extends the Phase 1 coloc.smk pattern to GWAS-vs-QTL pairwise coloc.
The QTL coloc manifest cross-joins (locus x tissue x gene) per QTL source.
Each row maps to a single run_qtl_coloc.R invocation.

T-02-05 mitigation: wildcard_constraints qtl_coloc_id regex prevents path
traversal (same pattern as T-1-03).

Must be included AFTER qtl_download.smk and finemap.smk in the top-level
Snakefile so QTL_RAW_DIR, QTL_HARMONIZED_DIR, FINEMAP_DIR, and
finemap_output() are in scope.
"""

import os
import sys

import pandas as pd

PYTHON_BIN = sys.executable
QTL_COLOC_DIR = os.path.join(config["paths"]["results_root"], "qtl_coloc")

# T-02-05: Region-safe manifest ID constraint (same pattern as coloc.smk T-1-03).
# Only alphanumeric + underscore + dot + hyphen allowed.
wildcard_constraints:
    qtl_coloc_id=r"[A-Za-z0-9_.\-]+",


def _qtl_coloc_manifest_path():
    """Return the path to the QTL coloc manifest TSV."""
    return os.path.join(QTL_COLOC_DIR, "qtl_coloc_manifest.tsv")


def _qtl_coloc_manifest_row(qtl_coloc_id):
    """Resolve a single row from qtl_coloc_manifest.tsv by ID.

    Returns a dict, or None if the manifest does not exist or the ID is not
    found (Snakemake will retry once the manifest exists).
    """
    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return None
    df = pd.read_csv(manifest_path, sep="\t", dtype=str)
    if "qtl_coloc_id" not in df.columns:
        return None
    row = df[df["qtl_coloc_id"] == qtl_coloc_id]
    if len(row) != 1:
        return None
    return row.iloc[0].to_dict()


def _qtl_manifest_field(wildcards, field):
    """Resolve a single field from the QTL coloc manifest for a given wildcard.

    Used by qtl_download.smk (harmonize_eqtl_region) and by rules in this file.
    """
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return "MISSING_MANIFEST"
    return row.get(field, "MISSING_FIELD")


def _qtl_coloc_gwas_fit_input(wildcards):
    """Input function: resolve GWAS .fit.rds path from the manifest row."""
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.gwas.fit.rds",
        )
    return row.get(
        "gwas_fit_path",
        finemap_output("susie", row["gwas_trait"], row["ancestry"], row["region"]).replace(
            ".json", ".fit.rds"
        ),
    )


def _qtl_coloc_ld_input(wildcards):
    """Input function: resolve LD matrix path from the manifest row."""
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.ld.rds",
        )
    return row.get(
        "ld_matrix_path",
        os.path.join(
            config["paths"]["ld_reference"],
            row["ancestry"],
            f"{row['region']}.rds",
        ),
    )


def _qtl_coloc_harmonized_input(wildcards):
    """Input function: resolve harmonized QTL TSV path from the manifest row."""
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.harmonized.tsv.gz",
        )
    return row.get(
        "harmonized_qtl_path",
        os.path.join(
            QTL_HARMONIZED_DIR,
            row["qtl_source"].replace("gtex_", "").replace("ukbppp_", "").replace("onek1k_", ""),
            row.get("dataset_id", "unknown"),
            row["gene_id"],
            f"{row['region']}.harmonized.tsv.gz",
        ),
    )


rule build_qtl_coloc_manifest:
    """Build the QTL coloc manifest by cross-joining regions x QTL sources x tissues x genes.

    IMPORTANT: The manifest builder iterates ALL sources defined in
    qtl_sources.yaml (gtex_eqtl, gtex_sqtl, ukbppp_pqtl, onek1k_sceqtl),
    not just eQTL. Plans 02-03 and 02-04 add harmonization scripts for
    new source types, but the manifest already includes rows for all sources
    because it reads from config. sQTL/pQTL/OneK1K rows will appear once
    their harmonized files exist on disk.

    Columns: qtl_coloc_id, qtl_source, tissue, gene_id, region, ancestry,
    gwas_trait, dataset_id, chr, start_grch38, end_grch38, tissue_n, sdy,
    gwas_fit_path, ld_matrix_path, harmonized_qtl_path.
    """
    input:
        regions="config/regions_curated_grch38.csv",
        qtl_config="config/qtl_sources.yaml",
        tissue_n_lookup=os.path.join(QTL_HARMONIZED_DIR, "gtex_tissue_n_lookup.json"),
    output:
        manifest=_qtl_coloc_manifest_path(),
    params:
        script=os.path.join("src", "python", "build_qtl_coloc_manifest.py"),
        results_root=config["paths"]["results_root"],
        ld_reference=config["paths"]["ld_reference"],
        harmonized_dir=QTL_HARMONIZED_DIR,
    conda:
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
    shell:
        r"""
        mkdir -p $(dirname {output.manifest})
        python {params.script} \
            --regions {input.regions} \
            --qtl-sources {input.qtl_config} \
            --tissue-n-lookup {input.tissue_n_lookup} \
            --results-root {params.results_root} \
            --ld-reference {params.ld_reference} \
            --harmonized-dir {params.harmonized_dir} \
            --output {output.manifest}
        """


rule run_qtl_coloc:
    """Run GWAS-vs-QTL coloc.susie for a single manifest row.

    This is the main dispatch rule. Each qtl_coloc_id corresponds to a
    unique (region x tissue x gene x qtl_source x ancestry) combination.
    """
    input:
        manifest=_qtl_coloc_manifest_path(),
        gwas_fit=_qtl_coloc_gwas_fit_input,
        qtl_sumstats=_qtl_coloc_harmonized_input,
        ld_matrix=_qtl_coloc_ld_input,
        policy="config/susie_policy.yaml",
        script="src/snakemake/scripts/run_qtl_coloc.R",
    output:
        json=os.path.join(QTL_COLOC_DIR, "{qtl_coloc_id}.json"),
    params:
        qtl_source=lambda wc: _qtl_manifest_field(wc, "qtl_source"),
        tissue=lambda wc: _qtl_manifest_field(wc, "tissue"),
        gene_id=lambda wc: _qtl_manifest_field(wc, "gene_id"),
        region=lambda wc: _qtl_manifest_field(wc, "region"),
        ancestry=lambda wc: _qtl_manifest_field(wc, "ancestry"),
        sdy=lambda wc: _qtl_manifest_field(wc, "sdy"),
        sample_size=lambda wc: _qtl_manifest_field(wc, "tissue_n"),
    conda:
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "r_coloc.yml"))
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p $(dirname {output.json})
        Rscript {input.script} \
            --gwas-fit {input.gwas_fit} \
            --qtl-sumstats {input.qtl_sumstats} \
            --ld-matrix {input.ld_matrix} \
            --qtl-source {params.qtl_source} \
            --tissue {params.tissue} \
            --gene-id {params.gene_id} \
            --region {params.region} \
            --ancestry {params.ancestry} \
            --sdy {params.sdy} \
            --sample-size {params.sample_size} \
            --policy {input.policy} \
            --output {output.json}
        """


rule aggregate_qtl_coloc:
    """Aggregate all per-pair QTL coloc JSON outputs into a summary TSV.

    Reads all JSON files in QTL_COLOC_DIR matching *.json, extracts the
    summary row (best PP.H4.abf pairwise comparison), and writes a flat TSV
    for downstream filtering and tiering.
    """
    input:
        manifest=_qtl_coloc_manifest_path(),
    output:
        summary=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
    params:
        script=os.path.join("src", "python", "aggregate_qtl_coloc.py"),
        json_dir=QTL_COLOC_DIR,
    conda:
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
    shell:
        r"""
        python {params.script} \
            --json-dir {params.json_dir} \
            --manifest {input.manifest} \
            --output {output.summary}
        """
