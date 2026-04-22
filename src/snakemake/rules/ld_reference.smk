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

# Plan 01-03 (Wave 2b): HGDP+1kG AFR panel scratch cache + output dir.
# /rs1/scratch does NOT exist on this cluster -- default under the
# ckclinto /rs1 allocation (29 TB avail; verified in
# wave2b_preflight.log step 11).
HGDP_1KG_SCRATCH = config.get("paths", {}).get(
    "hgdp_1kg_scratch",
    "/rs1/researchers/c/ckclinto/hgdp_1kg_scratch",
)
HGDP_1KG_OUT_DIR = os.path.join(LD_REF_DIR, "AFR_hgdp_1kg")

# Plan 01-03: HGDP+1kG v2 autosome BCFs are one file per chr1..chr22;
# chrX uses a separate PAR / non-PAR triplet. For Scope B, restrict to
# autosomal regions (mirrors UKBB_LD_REGION_INFOS), dropping BMI_Xq24.
# Reuse of UKBB_LD_REGION_INFOS is avoided per handoff note (5): construct
# the HGDP filter independently so changes to UKBB scope do not silently
# alter AFR coverage.
HGDP_REGION_INFOS = [
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
# susie_credible_set_yield RECOVERY_PLAN Stage 2 (2026-04-21): real 1000G EUR
# LD panel from the LDSC-landed 1000G Phase 3 plink files (GRCh37, HM3-filtered,
# 503 EUR samples). Replaces the identity-placeholder EUR .rds files written
# by build_ld_rds when n_variants > LD_MAX_VARIANTS=6000 (universal for all
# 12 curated regions; see .planning/debug/susie_credible_set_yield.md).
#
# Scope: 11 EUR autosomal regions. Emits to the SAME path the finemap rule
# reads from (data/processed/ld_reference/EUR/{region}.rds) and takes priority
# over build_ld_rds via ruleorder below. BMI_Xq24 is excluded (chrX not in
# LDSC's 1000G_EUR_Phase3_plink .bim files). HLA_6p21 at 69k HM3 variants
# exceeds the 16k SUSIE_MAX_VARIANTS cap -- it stays on the UKBB-LD tiled
# block-diagonal panel (already scaffolded in download_ukbb_ld_tiles).
#
# Why this over build_ld_rds (VCF-based): plink reads bed/bim/fam in a fraction
# of the time of VCF streaming, and the LDSC 1000G EUR QC panel is already
# HM3-filtered (matching what Phase 1 sumstats have post-harmonize), so LD
# matches sumstats density. Narrow validation: SH2B3_12q24 EUR hypertension
# CS collapsed from 10 L-saturated size-1 CS (identity LD artifact) to 4
# purity=1.0 CS at positions 12:111884608, 12:111904371, 12:111910219,
# 12:111932800 -- the exact leads from Stage 1d trait-pair coloc (PP.H4=1.0).
ONEKG_EUR_PLINK_PREFIX = config.get("paths", {}).get(
    "onekg_eur_plink_prefix",
    "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC",
)

# Regions eligible for the 1kG EUR plink build. Autosomal only; HLA on UKBB-LD.
_AUTO_NO_HLA = {
    safe
    for _, safe in REGION_INFOS
    if str(REGION_METADATA[safe].get("chr", "")).lstrip("chr") in _AUTOSOMES
    and safe != "HLA_6p21"
}

# Regions eligible for the 1kG EUR plink-based LD build. Python regex
# alternation (a|b|c) works reliably as a snakemake wildcard_constraints
# pattern, whereas PCRE negative lookahead does not. HLA_6p21 stays on
# the UKBB-LD tiled block-diagonal panel (download_ukbb_ld_tiles);
# BMI_Xq24 stays on build_ld_rds (chrX not in LDSC 1000G QC plink).
_ONEKG_EUR_ELIGIBLE_REGIONS = sorted(_AUTO_NO_HLA)
_ONEKG_EUR_REGION_PATTERN = "|".join(
    [r for r in _ONEKG_EUR_ELIGIBLE_REGIONS if r != "BMI_Xq24"]
)

ruleorder: build_ld_rds_1kg_eur > build_ld_rds


rule build_ld_rds_1kg_eur:
    """Build a real LD matrix RDS for one EUR autosomal region from 1000G
    Phase 3 plink files and write it at the canonical LD-reference path that
    finemap.smk::run_finemap consumes. HLA is excluded (stays on the UKBB-LD
    tiled panel); chrX/BMI_Xq24 is excluded (not in LDSC 1000G QC plink).
    """
    wildcard_constraints:
        ancestry=r"EUR",
        region=_ONEKG_EUR_REGION_PATTERN,
    input:
        bed=lambda wildcards: f"{ONEKG_EUR_PLINK_PREFIX}.{REGION_METADATA[wildcards.region]['chr']}.bed",
        bim=lambda wildcards: f"{ONEKG_EUR_PLINK_PREFIX}.{REGION_METADATA[wildcards.region]['chr']}.bim",
        fam=lambda wildcards: f"{ONEKG_EUR_PLINK_PREFIX}.{REGION_METADATA[wildcards.region]['chr']}.fam",
        rscript="src/snakemake/scripts/plink_ld_to_rds.R",
    output:
        rds=os.path.join(LD_REF_DIR, "{ancestry}", "{region}.rds"),
    params:
        bfile=lambda wildcards: f"{ONEKG_EUR_PLINK_PREFIX}.{REGION_METADATA[wildcards.region]['chr']}",
        chrom=lambda wildcards: str(REGION_METADATA[wildcards.region]["chr"]),
        start=lambda wildcards: int(REGION_METADATA[wildcards.region]["start"]),
        end=lambda wildcards: int(REGION_METADATA[wildcards.region]["end"]),
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
        work_prefix=lambda wildcards: os.path.join(
            LD_REF_DIR, "EUR_1kg_work", wildcards.region
        ),
    conda:
        # plink.yml has plink1 (required for --r square), plink2, bcftools,
        # and (added 2026-04-21 for this rule) r-base + r-data.table + r-optparse
        # so plink_ld_to_rds.R can run in the same env immediately after plink1
        # without a second conda activation.
        "envs/plink.yml"
    threads: 2
    resources:
        mem_mb=8000,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {params.work_prefix})
        # plink1 (not plink2) emits --r square output in the
        # ntab-separated float layout that plink_ld_to_rds.R parses.
        plink \
            --bfile {params.bfile} \
            --chr {params.chrom} \
            --from-bp {params.start} \
            --to-bp {params.end} \
            --r square \
            --write-snplist \
            --make-just-bim \
            --out {params.work_prefix} \
            --threads {threads}
        Rscript {input.rscript} \
            --ld {params.work_prefix}.ld \
            --variants {params.work_prefix}.bim \
            --region-id {params.region_id} \
            --ancestry {wildcards.ancestry} \
            --ld-source onekg_phase3_eur_hm3 \
            --output {output.rds}
        # Keep the intermediate .ld/.bim/.snplist for provenance; remove only
        # the large .ld file if space becomes a concern.
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


# ---------------------------------------------------------------------------
# Plan 01-03 (Wave 2b): HGDP+1kG AFR LD panel (gnomAD v3.1.2 phased BCFs)
# ---------------------------------------------------------------------------
# Builds per-region AFR LD by streaming gnomAD v3.1.2 phased BCFs from
# the anonymous GCS public bucket via bcftools + plink2, converting the
# plink square-LD output to .rds via plink_ld_to_rds.R. Outputs land at
# {LD_REF_DIR}/AFR_hgdp_1kg/{region}.rds plus a sidecar .meta.json with
# ld_source='hgdp_1kg_v3_1_2' and sha256 provenance (T-1-02, T-1-04).
#
# Scope B pilot (01-03-scope-decision.md): autosomal regions only (11 of
# 12 curated regions; BMI_Xq24 excluded because chrX uses separate BCF
# files in HGDP+1kG v2). Real execution is gated on GRCh38 liftover of
# regions_curated.csv (DEF-01-04) -- this rule is plumbing-ready for
# dry-run DAG resolution but should NOT be invoked end-to-end until
# that deferred item is resolved.
#
# DEF-01-01 workaround: conda directive uses LD_BUILD_ENV (absolute
# path) so --use-conda resolves correctly regardless of including
# Snakefile -- reuses the Plan 01-02 pattern.
rule build_hgdp_1kg_ld:
    input:
        regions=config["paths"]["regions_curated"],
        script="src/snakemake/scripts/build_hgdp_1kg_ld.py",
        rscript="src/snakemake/scripts/plink_ld_to_rds.R",
    output:
        rds=[
            os.path.join(HGDP_1KG_OUT_DIR, f"{safe}.rds")
            for _, safe in HGDP_REGION_INFOS
        ],
        meta=[
            os.path.join(HGDP_1KG_OUT_DIR, f"{safe}.meta.json")
            for _, safe in HGDP_REGION_INFOS
        ],
    params:
        out_dir=HGDP_1KG_OUT_DIR,
        scratch_dir=HGDP_1KG_SCRATCH,
        # Wrap params in a lambda so Snakemake does not try to interpret
        # '{chrom}' in the BCF filename template as a wildcard.
        bcf_template=lambda wildcards: config.get("hgdp_1kg", {}).get(
            "bcf_fname_template",
            "hgdp1kgp_chr{chrom}.filtered.SNV_INDEL.phased.shapeit5.bcf",
        ),
        region_col=lambda wildcards: config.get("hgdp_1kg", {}).get(
            "region_column", "hgdp_tgp_meta.Genetic.region"
        ),
        sample_col=lambda wildcards: config.get("hgdp_1kg", {}).get(
            "sample_column", "s"
        ),
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
            --bcf-fname-template "{params.bcf_template}" \
            --region-column "{params.region_col}" \
            --sample-column "{params.sample_col}" \
            --rscript Rscript \
            --r-helper-script {input.rscript}
        """
