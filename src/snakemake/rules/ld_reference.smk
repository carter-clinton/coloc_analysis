"""LD reference panel rules (1000 Genomes download + LD matrix construction).

Refactored from src/legacy/region_analysis/workflow/rules/ld_reference.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
No hardcoded rscript_bin -- conda env resolves Rscript (D-25).
"""

import os
import sys

CHROMOSOMES = config["onekg"].get(
    "chromosomes",
    [str(chrom) for chrom in range(1, 23)],
)
CHROM_STRING = " ".join(CHROMOSOMES)
LD_ROOT = config["paths"]["ld_1kg_root"]
LD_REF_DIR = config["paths"]["ld_reference"]
PYTHON_BIN = sys.executable


def vcf_path(chrom):
    return os.path.join(LD_ROOT, "vcf", f"chr{chrom}.vcf.gz")


def vcf_tbi_path(chrom):
    return vcf_path(chrom) + ".tbi"


def sample_list_path(ancestry):
    return os.path.join(LD_ROOT, f"{ancestry}.samples")


def ld_index_path(ancestry):
    return os.path.join(LD_REF_DIR, f"{ancestry}.ldindex")


VCF_PATHS = [vcf_path(chrom) for chrom in CHROMOSOMES]
VCF_TBI_PATHS = [vcf_tbi_path(chrom) for chrom in CHROMOSOMES]
SAMPLE_LISTS = [sample_list_path(ancestry) for ancestry in config["ancestries"]]
VARIANT_LIST_DIR = os.path.join(LD_REF_DIR, "variants")
LD_VARIANT_PATHS = [
    os.path.join(VARIANT_LIST_DIR, f"{region_safe}.tsv")
    for _, region_safe in REGION_INFOS
]
LD_RDS_PATHS = [
    os.path.join(LD_REF_DIR, ancestry, f"{region_safe}.rds")
    for ancestry in config["ancestries"]
    for _, region_safe in REGION_INFOS
]


rule download_1kg_panel:
    output:
        panel=os.path.join(LD_ROOT, "integrated_call_samples.panel"),
    params:
        url=config["onekg"].get("panel_url"),
        ld_root=LD_ROOT,
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.ld_root}
        curl -L "{params.url}" -o {output.panel}
        """


rule download_1kg_vcf:
    output:
        vcf=os.path.join(LD_ROOT, "vcf", "chr{chrom}.vcf.gz"),
        tbi=os.path.join(LD_ROOT, "vcf", "chr{chrom}.vcf.gz.tbi"),
    params:
        url=lambda wildcards: "{base}/{fname}".format(
            base=config["onekg"].get("ftp_base", "").rstrip("/"),
            fname=config["onekg"]
            .get(
                "vcf_template",
                "ALL.chr{chrom}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
            )
            .format(chrom=wildcards.chrom),
        ),
        ld_root=LD_ROOT,
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.vcf})
        curl -L "{params.url}" -o {output.vcf}
        curl -L "{params.url}.tbi" -o {output.tbi}
        """


rule build_1kg_sample_lists:
    input:
        panel=os.path.join(LD_ROOT, "integrated_call_samples.panel"),
    output:
        SAMPLE_LISTS,
    params:
        ld_root=LD_ROOT,
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_1kg_sample_lists.py \
            --panel {input.panel} \
            --config config/pipeline.yaml \
            --output-dir {params.ld_root}
        """


rule build_ld_rds:
    input:
        vcf=lambda wildcards: vcf_path(REGION_METADATA[wildcards.region]["chr"]),
        tbi=lambda wildcards: vcf_tbi_path(REGION_METADATA[wildcards.region]["chr"]),
        samples=lambda wildcards: sample_list_path(wildcards.ancestry),
        variants=os.path.join(VARIANT_LIST_DIR, "{region}.tsv"),
    output:
        os.path.join(LD_REF_DIR, "{ancestry}", "{region}.rds"),
    params:
        chrom=lambda wildcards: REGION_METADATA[wildcards.region]["chr"],
        start=lambda wildcards: REGION_METADATA[wildcards.region]["start"],
        end=lambda wildcards: REGION_METADATA[wildcards.region]["end"],
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        set -euo pipefail
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_ld_rds.py \
            --vcf {input.vcf} \
            --samples {input.samples} \
            --chrom {params.chrom} \
            --start {params.start} \
            --end {params.end} \
            --region-id {params.region_id} \
            --ancestry {wildcards.ancestry} \
            --output {output} \
            --rscript Rscript \
            --variant-list {input.variants}
        """


rule collect_region_variants:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
    output:
        os.path.join(VARIANT_LIST_DIR, "{region}.tsv"),
    params:
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p {VARIANT_LIST_DIR}
        {PYTHON_BIN} src/legacy/region_analysis/scripts/collect_region_variants.py \
            --region-id {params.region_id} \
            --regions-csv {input.regions} \
            --harmonized {input.harmonized} \
            --output {output}
        """
