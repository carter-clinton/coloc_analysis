"""QTL data download and harmonization rules for Phase 2 coloc pipeline.

Covers four QTL sources:
  - eQTL: GTEx v8 eQTL via eQTL Catalogue (Plan 02-02)
  - sQTL: GTEx v8 sQTL via eQTL Catalogue (Plan 02-03)
  - pQTL: UKB-PPP pQTL via Synapse / S3 (Plan 02-03)
  - sc-eQTL: OneK1K single-cell eQTL via eQTL Catalogue / onek1k.org (Plan 02-04)

Downloads per-tissue allpairs summary statistics from the eQTL Catalogue
FTP server. Each file is ~1-5 GB compressed. Files are downloaded locally
to avoid rate-limiting on remote tabix queries (Pitfall 5 from RESEARCH.md).

T-02-04 mitigation: validate file size > 0 bytes after download.
T-02-06 mitigation: download full files locally first; never use remote tabix.
T-02-08 mitigation: Synapse auth from env var only (UKB-PPP download).
T-02-12 mitigation: prefer eQTL Catalogue for OneK1K (known provenance).
T-02-13 mitigation: validate OneK1K file size + tabix index after download.
"""

import os
from pathlib import Path
import json
import sys

import yaml

PYTHON_BIN = sys.executable
QTL_RAW_DIR = os.path.join(config["paths"]["data_root"], "raw", "gtex_v8")
QTL_RAW_SQTL_DIR = os.path.join(config["paths"]["data_root"], "raw", "gtex_v8_sqtl")
QTL_RAW_PQTL_DIR = os.path.join(config["paths"]["data_root"], "raw", "ukbppp")
ONEK1K_RAW_DIR = os.path.join(config["paths"]["data_root"], "raw", "onek1k")
QTL_HARMONIZED_DIR = os.path.join(
    config["paths"]["data_root"], "processed", "qtl_harmonized"
)


# eQTL Catalogue URL resolution. `config/qtl_sources.yaml` is not merged into
# Snakemake's `config` dict (rules read it via input paths); load it directly here
# so module-scope helpers have access at param-evaluation time.
def _load_yaml(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path) as f:
        return yaml.safe_load(f) or (default if default is not None else {})


_EQTLCAT_QTD_MAP = _load_yaml("config/eqtl_catalogue_qtd_map.yaml")
_QTL_SOURCES_CFG = _load_yaml("config/qtl_sources.yaml").get("sources", {})


def _resolve_eqtlcat_url(tissue, source_key, suffix):
    """Resolve the eQTL Catalogue URL for a (tissue, source, suffix) triple.

    source_key is the key in config/qtl_sources.yaml::sources (e.g. 'gtex_eqtl',
    'gtex_sqtl'). Reads study_id + qtd_kind from qtl_sources.yaml (loaded at
    module scope into _QTL_SOURCES_CFG) and the tissue -> QTD mapping from
    config/eqtl_catalogue_qtd_map.yaml.

    Raises ValueError with a descriptive message for unknown tissue/source.
    """
    src = _QTL_SOURCES_CFG.get(source_key)
    if not src:
        raise ValueError(
            f"Unknown QTL source '{source_key}'. Available: "
            f"{sorted(_QTL_SOURCES_CFG.keys())}"
        )
    base = src.get("ftp_base", "https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/")
    study_id = src.get("study_id")
    qtd_kind = src.get("qtd_kind")
    if not study_id or not qtd_kind:
        raise ValueError(
            f"Source '{source_key}' missing study_id or qtd_kind in qtl_sources.yaml "
            f"(study_id={study_id!r}, qtd_kind={qtd_kind!r})"
        )
    tissues = _EQTLCAT_QTD_MAP.get("tissues", {})
    if tissue not in tissues:
        raise ValueError(
            f"Tissue '{tissue}' not found in {source_key} QTD map. "
            f"Available ({len(tissues)}): {sorted(tissues.keys())[:5]}..."
        )
    qtd_id = tissues[tissue].get(qtd_kind)
    if qtd_id is None:
        raise ValueError(
            f"QTD kind '{qtd_kind}' missing for tissue '{tissue}' in {source_key}"
        )
    return f"{base}{study_id}/{qtd_id}/{qtd_id}{suffix}"


rule download_eqtl_catalogue:
    """Download a single eQTL Catalogue allpairs file + tabix index.

    T-02-04: validates downloaded file is non-empty.
    T-02-06: full local download avoids remote tabix rate limiting.

    URL scheme updated 2026-04-20: eQTL Catalogue r8 (2023-04) moved from
    `{ftp_base}{tissue}/{tissue}.all.tsv.gz` to
    `{ftp_base}{study_id}/{qtd_id}/{qtd_id}.cc.tsv.gz`. File is saved locally
    under the legacy `{tissue}.all.tsv.gz` name to avoid re-downloading the
    3.6 GB-per-tissue eQTL files that were pre-staged from eQTL Catalogue r7
    (2020) using the old URL scheme. Schema is r7<->r8 compatible.
    """
    output:
        tsv=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz.tbi"),
    params:
        tsv_url=lambda wc: _resolve_eqtlcat_url(wc.dataset_id, "gtex_eqtl", ".cc.tsv.gz"),
        tbi_url=lambda wc: _resolve_eqtlcat_url(wc.dataset_id, "gtex_eqtl", ".cc.tsv.gz.tbi"),
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p $(dirname {output.tsv})
        curl -sS -L --retry 3 --retry-delay 5 --max-time 7200 \
            -o {output.tsv} "{params.tsv_url}"
        curl -sS -L --retry 3 --retry-delay 5 --max-time 300 \
            -o {output.tbi} "{params.tbi_url}"

        # T-02-04: validate non-empty download
        if [ ! -s {output.tsv} ]; then
            echo "ERROR: downloaded file is empty: {output.tsv}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        if [ ! -s {output.tbi} ]; then
            echo "ERROR: downloaded tabix index is empty: {output.tbi}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        """


rule build_tissue_n_lookup:
    """Build tissue -> N sample size lookup JSON."""
    output:
        json=os.path.join(QTL_HARMONIZED_DIR, "gtex_tissue_n_lookup.json"),
    params:
        script=os.path.join("src", "python", "build_tissue_n_lookup.py"),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.json})
        python {params.script} --output {output.json}
        """


rule harmonize_eqtl_region:
    """Harmonize eQTL Catalogue data for a single (tissue, gene, region) triple."""
    input:
        tsv=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz.tbi"),
        qtl_config="config/qtl_sources.yaml",
    output:
        harmonized=os.path.join(
            QTL_HARMONIZED_DIR,
            "eqtl",
            "{dataset_id}",
            "{gene_id}",
            "{region}.harmonized.tsv.gz",
        ),
    params:
        script=os.path.join("src", "python", "harmonize_eqtl.py"),
        region_chr=lambda wc: _qtl_manifest_field(wc, "chr"),
        region_start=lambda wc: _qtl_manifest_field(wc, "start_grch38"),
        region_end=lambda wc: _qtl_manifest_field(wc, "end_grch38"),
        tissue_name=lambda wc: _qtl_manifest_field(wc, "tissue"),
        tissue_n=lambda wc: _qtl_manifest_field(wc, "tissue_n"),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.harmonized})
        python {params.script} \
            --input {input.tsv} \
            --region-chr {params.region_chr} \
            --region-start {params.region_start} \
            --region-end {params.region_end} \
            --gene-id {wildcards.gene_id} \
            --tissue-name {params.tissue_name} \
            --tissue-n {params.tissue_n} \
            --qtl-source-config {input.qtl_config} \
            --output {output.harmonized}
        """


# ===================================================================
# sQTL: GTEx v8 sQTL via eQTL Catalogue (Plan 02-03)
# ===================================================================

rule download_sqtl_catalogue:
    """Download a single eQTL Catalogue sQTL allpairs file + tabix index.

    Same upstream as eQTL (eQTL Catalogue r8 QTS000015), different QTD ids
    (sqtl_qtd = leafcutter quant method).  URL resolved via
    config/eqtl_catalogue_qtd_map.yaml + _resolve_eqtlcat_url helper.

    The upstream file is named `{qtd_id}.cc.tsv.gz` (r8 convention);
    saved locally under `{tissue}.all.tsv.gz` to keep filesystem names
    tissue-addressable and consistent with the manifest's dataset_id column.

    T-02-04: validates downloaded file is non-empty.
    """
    output:
        tsv=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz.tbi"),
    params:
        tsv_url=lambda wc: _resolve_eqtlcat_url(wc.dataset_id, "gtex_sqtl", ".cc.tsv.gz"),
        tbi_url=lambda wc: _resolve_eqtlcat_url(wc.dataset_id, "gtex_sqtl", ".cc.tsv.gz.tbi"),
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p $(dirname {output.tsv})
        curl -sS -L --retry 3 --retry-delay 5 --max-time 7200 \
            -o {output.tsv} "{params.tsv_url}"
        curl -sS -L --retry 3 --retry-delay 5 --max-time 300 \
            -o {output.tbi} "{params.tbi_url}"

        # T-02-04: validate non-empty download
        if [ ! -s {output.tsv} ]; then
            echo "ERROR: downloaded sQTL file is empty: {output.tsv}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        if [ ! -s {output.tbi} ]; then
            echo "ERROR: downloaded sQTL tabix index is empty: {output.tbi}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        # Gzip integrity check: upstream truncation or aborted transfer must fail loud.
        if ! gzip -t {output.tsv} 2>/dev/null; then
            echo "ERROR: gzip integrity check failed for {output.tsv}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        """


rule harmonize_sqtl_region:
    """Harmonize eQTL Catalogue sQTL data for a single (tissue, gene, region) triple.

    Uses harmonize_sqtl.py which wraps harmonize_eqtl core logic. Molecular
    trait IDs (splice junctions) are preserved; gene_id column uses Ensembl IDs.
    """
    input:
        tsv=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz.tbi"),
        qtl_config="config/qtl_sources.yaml",
    output:
        harmonized=os.path.join(
            QTL_HARMONIZED_DIR,
            "sqtl",
            "{dataset_id}",
            "{gene_id}",
            "{region}.harmonized.tsv.gz",
        ),
    params:
        script=os.path.join("src", "python", "harmonize_sqtl.py"),
        region_chr=lambda wc: _qtl_manifest_field(wc, "chr"),
        region_start=lambda wc: _qtl_manifest_field(wc, "start_grch38"),
        region_end=lambda wc: _qtl_manifest_field(wc, "end_grch38"),
        tissue_name=lambda wc: _qtl_manifest_field(wc, "tissue"),
        tissue_n=lambda wc: _qtl_manifest_field(wc, "tissue_n"),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.harmonized})
        python {params.script} \
            --input {input.tsv} \
            --region-chr {params.region_chr} \
            --region-start {params.region_start} \
            --region-end {params.region_end} \
            --gene-id {wildcards.gene_id} \
            --tissue-name {params.tissue_name} \
            --tissue-n {params.tissue_n} \
            --qtl-source-config {input.qtl_config} \
            --output {output.harmonized}
        """


# ===================================================================
# pQTL: UKB-PPP pQTL via Synapse / S3 (Plan 02-03)
# ===================================================================

rule download_ukbppp_protein:
    """Download UKB-PPP per-protein summary stats from Synapse.

    Auth via SYNAPSE_AUTH_TOKEN env var (T-02-08: never committed).
    T-02-10: per-protein per-chromosome download (not bulk tar).
    """
    output:
        gz=os.path.join(QTL_RAW_PQTL_DIR, "{protein}", "discovery_chr{chrom}_{protein}.gz"),
    params:
        script=os.path.join("src", "python", "download_ukbppp.py"),
        synapse_project="syn51364943",
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    resources:
        mem_mb=4000,
    shell:
        r"""
        mkdir -p $(dirname {output.gz})
        python {params.script} \
            --protein {wildcards.protein} \
            --chromosome {wildcards.chrom} \
            --output-dir $(dirname {output.gz})
        test -s {output.gz}  # verify non-empty
        """


def _pqtl_download_input(wildcards):
    """Resolve UKB-PPP download path for a given (tissue, gene_id, region).

    The download output path embeds {chrom} which cannot be inferred from
    the harmonize rule's output wildcards. Resolve chrom from the manifest
    row via qtl_coloc.smk._qtl_manifest_field — same pattern used by
    harmonize_onek1k_region for region_chr (line 345 of this file).
    """
    chrom = _qtl_manifest_field(wildcards, "chr")
    return os.path.join(
        QTL_RAW_PQTL_DIR,
        wildcards.gene_id,
        f"discovery_chr{chrom}_{wildcards.gene_id}.gz",
    )


rule harmonize_pqtl_region:
    """Harmonize UKB-PPP pQTL data for a single (tissue, gene_id, region) triple.

    Reads REGENIE output, converts LOG10P to pvalue, constructs variant_id,
    estimates sdY from summary statistics (Open Question 1: NPX may not be
    unit-variance).

    Output-path structure matches the 4-segment manifest path
    `pqtl/{tissue}/{gene_id}/{region}.harmonized.tsv.gz` (e.g.
    `pqtl/plasma/FTO/FTO_16q12.harmonized.tsv.gz`), consistent with
    sQTL/sceQTL 3-segment conventions. Prior 2-segment form
    (`pqtl/{protein}/{region}`) did not match the path emitted by
    build_qtl_coloc_manifest.py.

    Input resolves chrom from the manifest via an input function, mirroring
    the `_qtl_manifest_field(wc, "chr")` pattern in harmonize_onek1k_region.
    """
    input:
        gz=_pqtl_download_input,
        qtl_config="config/qtl_sources.yaml",
    output:
        harmonized=os.path.join(
            QTL_HARMONIZED_DIR,
            "pqtl",
            "{tissue}",
            "{gene_id}",
            "{region}.harmonized.tsv.gz",
        ),
    params:
        script=os.path.join("src", "python", "harmonize_pqtl.py"),
        region_chr=lambda wc: _qtl_manifest_field(wc, "chr"),
        region_start=lambda wc: _qtl_manifest_field(wc, "start_grch38"),
        region_end=lambda wc: _qtl_manifest_field(wc, "end_grch38"),
        sample_size=lambda wc: _qtl_manifest_field(wc, "tissue_n"),
        sdy="estimate",  # UKB-PPP Olink NPX may not be unit-variance
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.harmonized})
        python {params.script} \
            --input {input.gz} \
            --region-chr {params.region_chr} \
            --region-start {params.region_start} \
            --region-end {params.region_end} \
            --protein-name {wildcards.gene_id} \
            --sample-size {params.sample_size} \
            --sdy {params.sdy} \
            --qtl-source-config {input.qtl_config} \
            --output {output.harmonized}
        """


# ===================================================================
# sc-eQTL: OneK1K single-cell eQTL (Plan 02-04)
# ===================================================================

rule download_onek1k_cell_type:
    """Download OneK1K sc-eQTL data for a single cell type.

    Primary: eQTL Catalogue (QTS000038, GRCh38).
    Fallback: onek1k.org S3 (GRCh37, needs liftover).
    T-02-12: prefers eQTL Catalogue for known provenance.
    T-02-13: validates non-empty download.
    """
    output:
        tsv=os.path.join(ONEK1K_RAW_DIR, "{cell_type}", "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(ONEK1K_RAW_DIR, "{cell_type}", "{dataset_id}.all.tsv.gz.tbi"),
    params:
        script=os.path.join("src", "python", "download_onek1k.py"),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p $(dirname {output.tsv})
        python {params.script} \
          --cell-type {wildcards.cell_type} \
          --output-dir $(dirname {output.tsv})

        # T-02-13: validate non-empty download
        if [ ! -s {output.tsv} ]; then
            echo "ERROR: downloaded OneK1K file is empty: {output.tsv}" >&2
            rm -f {output.tsv} {output.tbi}
            exit 1
        fi
        """


def _onek1k_download_input(wildcards):
    """Resolve OneK1K download TSV path from manifest.

    The download output has {cell_type}/{dataset_id}.all.tsv.gz — dataset_id
    is not a wildcard of the harmonize rule's output, so resolve it from the
    manifest (same pattern as _pqtl_download_input). For OneK1K, tissue==
    cell_type and dataset_id==cell_type in practice.
    """
    dataset_id = _qtl_manifest_field(wildcards, "dataset_id")
    return os.path.join(
        ONEK1K_RAW_DIR,
        wildcards.cell_type,
        f"{dataset_id}.all.tsv.gz",
    )


rule harmonize_onek1k_region:
    """Harmonize OneK1K sc-eQTL data for a single (cell_type, gene, region) triple.

    Reuses harmonize_eqtl core logic via harmonize_onek1k.py since eQTL
    Catalogue OneK1K files have the same column schema as GTEx eQTL.
    Cell type goes into the "tissue" column of the common intermediate TSV.
    """
    input:
        tsv=_onek1k_download_input,
        qtl_config="config/qtl_sources.yaml",
    output:
        harmonized=os.path.join(
            QTL_HARMONIZED_DIR,
            "sceqtl",
            "{cell_type}",
            "{gene_id}",
            "{region}.harmonized.tsv.gz",
        ),
    params:
        script=os.path.join("src", "python", "harmonize_onek1k.py"),
        region_chr=lambda wc: _qtl_manifest_field(wc, "chr"),
        region_start=lambda wc: _qtl_manifest_field(wc, "start_grch38"),
        region_end=lambda wc: _qtl_manifest_field(wc, "end_grch38"),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.harmonized})
        python {params.script} \
            --input {input.tsv} \
            --cell-type {wildcards.cell_type} \
            --region-chr {params.region_chr} \
            --region-start {params.region_start} \
            --region-end {params.region_end} \
            --gene-id {wildcards.gene_id} \
            --qtl-source-config {input.qtl_config} \
            --output {output.harmonized}
        """
