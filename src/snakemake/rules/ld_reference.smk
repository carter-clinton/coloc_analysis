"""LD reference panel rules (1000 Genomes download + LD matrix construction).

Refactored from src/legacy/region_analysis/workflow/rules/ld_reference.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
No hardcoded rscript_bin -- conda env resolves Rscript (D-25).

Plan 01-02 (Wave 2a): adds download_ukbb_ld_tiles rule backing the UKBB-LD
tiled EUR panel (Weissbrod 2020). That rule uses an absolute-path conda
directive (str(Path(workflow.basedir) / "envs" / "ld_build.yml")) to
sidestep DEF-01-01 (snakemake 7.32.4 resolves relative conda: paths from
the included rule file rather than workflow.basedir).
"""

import os
import sys
from pathlib import Path

CHROMOSOMES = config["onekg"].get(
    "chromosomes",
    [str(chrom) for chrom in range(1, 23)],
)
CHROM_STRING = " ".join(CHROMOSOMES)
LD_ROOT = config["paths"]["ld_1kg_root"]
LD_REF_DIR = config["paths"]["ld_reference"]
PYTHON_BIN = sys.executable

# Plan 01-02: absolute path to envs/ld_build.yml so --use-conda resolves it
# correctly regardless of which Snakefile included this module. See
# deferred-items.md DEF-01-01.
LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")

# Plan 01-02: UKBB-LD tile scratch cache (large, excluded from git)
UKBB_LD_SCRATCH = config.get("paths", {}).get(
    "ukbb_ld_scratch",
    "/rs1/researchers/c/ckclinto/ukbb_ld_scratch",
)
UKBB_LD_OUT_DIR = os.path.join(LD_REF_DIR, "EUR_ukbb_ld")

# Plan 01-02: UKBB-LD is EUR-only and autosomal. Drop X/Y/MT regions and
# anything whose chromosome is not 1..22.
_AUTOSOMES = {str(c) for c in range(1, 23)}
UKBB_LD_REGION_INFOS = [
    (orig, safe)
    for orig, safe in REGION_INFOS
    if str(REGION_METADATA[safe].get("chr", "")).lstrip("chr") in _AUTOSOMES
]


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


# ---------------------------------------------------------------------------
# Plan 01-02 (Wave 2a): UKBB-LD tiled EUR panel (Weissbrod 2020)
# ---------------------------------------------------------------------------
# Downloads NPZ + variant TSV tiles anonymously from the AWS Open Data
# Registry and extracts per-curated-region LD .rds + sidecar .meta.json
# files into {LD_REF_DIR}/EUR_ukbb_ld/. HLA_6p21 spans multiple tiles and
# gets block-diagonal treatment with ld_source='ukbb_ld_tiled_block_diagonal'
# (T-1-04 mitigation). Non-autosomal regions are skipped (UKBB-LD is autosomes
# only) via UKBB_LD_REGION_INFOS above.
#
# DEF-01-01 workaround: conda directive uses the absolute LD_BUILD_ENV path
# (str(Path(workflow.basedir) / "envs" / "ld_build.yml")) so --use-conda
# resolves it correctly regardless of the including Snakefile.
rule download_ukbb_ld_tiles:
    input:
        regions=config["paths"]["regions_curated"],
        script="src/snakemake/scripts/download_ukbb_ld_tiles.py",
    output:
        rds=[
            os.path.join(UKBB_LD_OUT_DIR, f"{safe}.rds")
            for _, safe in UKBB_LD_REGION_INFOS
        ],
        meta=[
            os.path.join(UKBB_LD_OUT_DIR, f"{safe}.meta.json")
            for _, safe in UKBB_LD_REGION_INFOS
        ],
    params:
        out_dir=UKBB_LD_OUT_DIR,
        scratch_dir=UKBB_LD_SCRATCH,
    conda:
        LD_BUILD_ENV
    threads: 4
    resources:
        mem_mb=16000,
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.out_dir} {params.scratch_dir}
        {PYTHON_BIN} {input.script} \
            --regions-csv {input.regions} \
            --out-dir {params.out_dir} \
            --scratch-dir {params.scratch_dir} \
            --ancestry EUR
        """
