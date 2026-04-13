"""eQTL Catalogue download and indexing rules for Phase 2 QTL coloc.

Downloads per-tissue allpairs summary statistics from the eQTL Catalogue
FTP server. Each file is ~1-5 GB compressed. Files are downloaded locally
to avoid rate-limiting on remote tabix queries (Pitfall 5 from RESEARCH.md).

T-02-04 mitigation: validate file size > 0 bytes after download.
T-02-06 mitigation: download full files locally first; never use remote tabix.
"""

import os
import json
import sys

PYTHON_BIN = sys.executable
QTL_RAW_DIR = os.path.join(config["paths"]["data_root"], "raw", "gtex_v8")
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
