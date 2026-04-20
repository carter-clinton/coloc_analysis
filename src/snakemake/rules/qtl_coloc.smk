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
from pathlib import Path

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


def _qtl_coloc_per_id_jsons():
    """Enumerate per-id JSON output targets from the on-disk manifest.

    Called at Snakefile parse time (inside this .smk file) to expose
    QTL_COLOC_PER_ID_JSONS as a module-level global. Returns an empty list
    when the manifest does not yet exist — Snakemake will then only expand
    per-id targets after `build_qtl_coloc_manifest` has run once and the
    user re-invokes snakemake (manifest is a checkpoint-style prerequisite).

    This mirrors the FINEMAP_OUTPUTS parse-time enumeration pattern in
    Snakefile (lines 80-88), but sources its row list from a materialized
    TSV rather than a config-driven cross product.
    """
    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return []
    try:
        df = pd.read_csv(manifest_path, sep="\t", dtype=str, usecols=["qtl_coloc_id"])
    except (ValueError, KeyError):
        return []
    return [
        os.path.join(QTL_COLOC_DIR, f"{qtl_coloc_id}.json")
        for qtl_coloc_id in df["qtl_coloc_id"].dropna().unique()
    ]


# Module-level parse-time enumeration. Exposed as a global so that both
# aggregate_qtl_coloc (below) and the Snakefile-level all_qtl_coloc target
# can reference the same list without divergence.
QTL_COLOC_PER_ID_JSONS = _qtl_coloc_per_id_jsons()

# L2G concordance is gated on OpenTargets L2G prediction data existing on disk
# (rule l2g_concordance input requires the directory). No auto-download rule
# currently exists; if the dir is absent, omit l2g_concordance.tsv from the
# default Phase 2 target list. Users can still request it explicitly once the
# data is landed.
_L2G_DIR = os.path.join(
    config["paths"]["data_root"], "raw", "opentargets", "l2g_prediction"
)
_L2G_OUTPUTS = (
    [os.path.join(QTL_COLOC_DIR, "l2g_concordance.tsv")]
    if os.path.isdir(_L2G_DIR)
    else []
)

QTL_COLOC_OUTPUTS = (
    [_qtl_coloc_manifest_path()]
    + QTL_COLOC_PER_ID_JSONS
    + [
        os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
        os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        os.path.join(QTL_COLOC_DIR, "pph4_threshold_sweep.tsv"),
        os.path.join(QTL_COLOC_DIR, "gene_tissue_matrix.tsv"),
        os.path.join(QTL_COLOC_DIR, "gene_tissue_long.tsv"),
    ]
    + _L2G_OUTPUTS
)


def _qtl_manifest_row_by_wildcards(wildcards):
    """Resolve a manifest row via multiple lookup strategies.

    Tries in order:
      1. wildcards.qtl_coloc_id (used by run_qtl_coloc in this file).
      2. Compound key (tissue, gene_id, region) — used by
         harmonize_eqtl_region / harmonize_sqtl_region / harmonize_pqtl_region
         / harmonize_onek1k_region, whose wildcards don't carry qtl_coloc_id.
         When (tissue, gene_id, region) matches multiple sources (e.g.
         gtex_eqtl vs gtex_sqtl vs ukbppp_pqtl all with tissue=plasma),
         additional disambiguation is delegated to qtl_source if the
         wildcard carries it. In practice, path structure
         (eqtl/sqtl/pqtl/sceqtl root segment) is not available here — we
         take the first matching row.

    Returns a dict (manifest row) or None if no match.
    """
    # Path 1: direct qtl_coloc_id lookup.
    qtl_coloc_id = getattr(wildcards, "qtl_coloc_id", None)
    if qtl_coloc_id is not None:
        return _qtl_coloc_manifest_row(qtl_coloc_id)

    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return None
    df = pd.read_csv(manifest_path, sep="\t", dtype=str)

    # Path 2: compound key via available wildcards. Apply each present
    # wildcard as an equality filter against its corresponding column.
    filter_map = {
        "tissue": "tissue",
        "gene_id": "gene_id",
        "region": "region",
        "dataset_id": "dataset_id",
        "cell_type": "tissue",   # harmonize_onek1k_region uses cell_type
        "protein": "gene_id",    # legacy wildcard name → manifest gene_id
    }
    sub = df
    for wc_name, col_name in filter_map.items():
        wc_val = getattr(wildcards, wc_name, None)
        if wc_val is None or col_name not in sub.columns:
            continue
        sub = sub[sub[col_name] == wc_val]
        if len(sub) == 0:
            return None
    if len(sub) == 0:
        return None
    return sub.iloc[0].to_dict()


def _qtl_manifest_field(wildcards, field):
    """Resolve a single field from the QTL coloc manifest for a given wildcard.

    Used by qtl_download.smk (harmonize_*_region) and by rules in this file.
    Supports both qtl_coloc_id-keyed lookup (run_qtl_coloc) and compound-key
    lookup (harmonize_* rules whose wildcards are path components).
    """
    row = _qtl_manifest_row_by_wildcards(wildcards)
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
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
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
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
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

    Note: per-id JSONs are NOT declared as inputs of this rule. Doing so
    would transitively propagate into rule all_pathway (via
    extract_tier_ab_genes → assign_tiers → aggregate_qtl_coloc), which
    would force all_pathway to require all 1243 QTL coloc jobs before it
    can run — breaking the Launch10-15 pathway drain pattern.

    Instead, rule all_qtl_coloc (in the top-level Snakefile) explicitly
    lists QTL_COLOC_PER_ID_JSONS so that invoking all_qtl_coloc correctly
    expands to all 1243 per-id coloc jobs. Invoking qtl_coloc_summary.tsv
    directly will NOT backward-chain to per-id jobs — this is intentional
    for Phase 5 compatibility. Phase 2 first-production fires via
    all_qtl_coloc.
    """
    input:
        manifest=_qtl_coloc_manifest_path(),
    output:
        summary=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
    params:
        script=os.path.join("src", "python", "aggregate_qtl_coloc.py"),
        json_dir=QTL_COLOC_DIR,
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        python {params.script} \
            --json-dir {params.json_dir} \
            --manifest {input.manifest} \
            --output {output.summary}
        """


# ---------------------------------------------------------------------------
# Phase 2 Plan 05: Tier assignment, L2G concordance, gene-tissue matrix
# ---------------------------------------------------------------------------

# NEG_CTRL_DIR defined in negative_controls.smk (included before this file).
# Redefined here for self-contained reference; Snakemake tolerates re-assignment.
NEG_CTRL_DIR = os.path.join(config["paths"]["results_root"], "negative_controls")

QTL_PROC_ENV_COLOC = str(
    str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
)


rule assign_tiers:
    """Assign Tier A/B/C confidence levels (D-02c, QTL-source-agnostic).

    Combines GWAS-GWAS coloc results (trait-trait PP.H4) with QTL coloc
    results to produce mechanistic tier assignments. Also produces the
    PP.H4 threshold sweep table (REQ-3).
    """
    input:
        qtl_results=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
        gwas_coloc=os.path.join(
            config["paths"]["results_root"], "multitrait",
            "coloc_summary.tsv",
        ),
        neg_ctrl_results=os.path.join(NEG_CTRL_DIR, "curated_neg_ctrl_results.tsv"),
        pph4_config="config/pph4_thresholds.yaml",
    output:
        tiers=os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        sweep=os.path.join(QTL_COLOC_DIR, "pph4_threshold_sweep.tsv"),
    params:
        script=os.path.join("src", "python", "assign_tiers.py"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        python {params.script} \
          --input {input.qtl_results} \
          --gwas-coloc {input.gwas_coloc} \
          --pph4-config {input.pph4_config} \
          --neg-ctrl-results {input.neg_ctrl_results} \
          --output {output.tiers} \
          --sweep --sweep-output {output.sweep}
        """


rule l2g_concordance:
    """Compute Open Targets L2G concordance for Tier A loci (D-05a/D-05b).

    L2G is independent corroboration, NOT a filter gate. Disagreements are
    flagged as findings (potential distal enhancer-driven assignments).
    """
    input:
        tiers=os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        l2g_dir=os.path.join(
            config["paths"]["data_root"], "raw", "opentargets", "l2g_prediction",
        ),
    output:
        concordance=os.path.join(QTL_COLOC_DIR, "l2g_concordance.tsv"),
    params:
        script=os.path.join("src", "python", "parse_l2g.py"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        python {params.script} \
          --l2g-dir {input.l2g_dir} \
          --tier-table {input.tiers} \
          --output {output.concordance}
        """


rule build_gene_tissue_matrix:
    """Build gene x tissue x cell-type matrix from all QTL coloc results.

    Produces both wide-format (heatmap-ready) and long-format (analysis-ready)
    tables. Columns combine tissue/cell_type with QTL source for unambiguous
    identification.
    """
    input:
        qtl_results=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
    output:
        matrix=os.path.join(QTL_COLOC_DIR, "gene_tissue_matrix.tsv"),
        long_table=os.path.join(QTL_COLOC_DIR, "gene_tissue_long.tsv"),
    params:
        script=os.path.join("src", "python", "build_gene_tissue_matrix.py"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        python {params.script} \
          --input {input.qtl_results} \
          --output-matrix {output.matrix} \
          --output-long {output.long_table}
        """
