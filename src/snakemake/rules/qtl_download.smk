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
import json
import sys

PYTHON_BIN = sys.executable
QTL_RAW_DIR = os.path.join(config["paths"]["data_root"], "raw", "gtex_v8")
QTL_RAW_SQTL_DIR = os.path.join(config["paths"]["data_root"], "raw", "gtex_v8_sqtl")
QTL_RAW_PQTL_DIR = os.path.join(config["paths"]["data_root"], "raw", "ukbppp")
ONEK1K_RAW_DIR = os.path.join(config["paths"]["data_root"], "raw", "onek1k")
QTL_HARMONIZED_DIR = os.path.join(
    config["paths"]["data_root"], "processed", "qtl_harmonized"
)


rule download_eqtl_catalogue:
    """Download a single eQTL Catalogue allpairs file + tabix index.

    T-02-04: validates downloaded file is non-empty.
    T-02-06: full local download avoids remote tabix rate limiting.
    """
    output:
        tsv=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_DIR, "{dataset_id}.all.tsv.gz.tbi"),
    params:
        ftp_base=config.get("qtl_sources", {}).get(
            "gtex_eqtl", {}
        ).get(
            "ftp_base",
            "ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/",
        ),
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p $(dirname {output.tsv})
        wget -q -O {output.tsv} \
            "{params.ftp_base}{wildcards.dataset_id}/{wildcards.dataset_id}.all.tsv.gz"
        wget -q -O {output.tbi} \
            "{params.ftp_base}{wildcards.dataset_id}/{wildcards.dataset_id}.all.tsv.gz.tbi"

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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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

    Same FTP source as eQTL, different dataset IDs (sQTL-specific QTD IDs).
    T-02-04: validates downloaded file is non-empty.
    """
    output:
        tsv=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz"),
        tbi=os.path.join(QTL_RAW_SQTL_DIR, "{dataset_id}.all.tsv.gz.tbi"),
    params:
        ftp_base=config.get("qtl_sources", {}).get(
            "gtex_sqtl", {}
        ).get(
            "ftp_base",
            "ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/",
        ),
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p $(dirname {output.tsv})
        wget -q -O {output.tsv} \
            "{params.ftp_base}{wildcards.dataset_id}/{wildcards.dataset_id}.all.tsv.gz"
        wget -q -O {output.tbi} \
            "{params.ftp_base}{wildcards.dataset_id}/{wildcards.dataset_id}.all.tsv.gz.tbi"

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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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


rule harmonize_pqtl_region:
    """Harmonize UKB-PPP pQTL data for a single (protein, region) pair.

    Reads REGENIE output, converts LOG10P to pvalue, constructs variant_id,
    estimates sdY from summary statistics (Open Question 1: NPX may not be
    unit-variance).
    """
    input:
        gz=os.path.join(QTL_RAW_PQTL_DIR, "{protein}", "discovery_chr{chrom}_{protein}.gz"),
        qtl_config="config/qtl_sources.yaml",
    output:
        harmonized=os.path.join(
            QTL_HARMONIZED_DIR,
            "pqtl",
            "{protein}",
            "{region}.harmonized.tsv.gz",
        ),
    params:
        script=os.path.join("src", "python", "harmonize_pqtl.py"),
        region_chr=lambda wc: wc.chrom,
        region_start=lambda wc: _qtl_manifest_field(wc, "start_grch38"),
        region_end=lambda wc: _qtl_manifest_field(wc, "end_grch38"),
        sample_size=54219,
        sdy="estimate",  # UKB-PPP Olink NPX may not be unit-variance
    conda:
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
    shell:
        r"""
        mkdir -p $(dirname {output.harmonized})
        python {params.script} \
            --input {input.gz} \
            --region-chr {params.region_chr} \
            --region-start {params.region_start} \
            --region-end {params.region_end} \
            --protein-name {wildcards.protein} \
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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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


rule harmonize_onek1k_region:
    """Harmonize OneK1K sc-eQTL data for a single (cell_type, gene, region) triple.

    Reuses harmonize_eqtl core logic via harmonize_onek1k.py since eQTL
    Catalogue OneK1K files have the same column schema as GTEx eQTL.
    Cell type goes into the "tissue" column of the common intermediate TSV.
    """
    input:
        tsv=os.path.join(ONEK1K_RAW_DIR, "{cell_type}", "{dataset_id}.all.tsv.gz"),
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
        str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml"))
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
