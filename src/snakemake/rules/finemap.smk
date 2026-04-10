"""Fine-mapping rules (SuSiE and related methods).

Refactored from src/legacy/region_analysis/workflow/rules/finemap.smk.
All paths parameterized via config (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
Removed hardcoded rscript_bin -- conda env resolves Rscript.
"""

import os
import sys

FINEMAP_DIR = config["finemap"]["output_dir"]
FINEMAP_METHODS = config["finemap"]["methods"]
PYTHON_BIN = sys.executable


def finemap_output(path_method, trait, ancestry, region):
    return os.path.join(FINEMAP_DIR, path_method, f"{trait}.{ancestry}.{region}.json")


def stroke_afr_outputs(wildcards=None):
    return [
        os.path.join(FINEMAP_DIR, method, f"stroke.AFR.{region_safe}.json")
        for method in FINEMAP_METHODS
        for _, region_safe in REGION_INFOS
    ]


rule build_finemap_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
    output:
        manifest=FINEMAP_MANIFEST,
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        methods=",".join(FINEMAP_METHODS),
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_finemap_tasks.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --methods {params.methods} \
            --output {output.manifest}
        """


rule run_finemap:
    input:
        sumstats=lambda wildcards: os.path.join(
            HARMONIZED_DIR,
            f"{wildcards.trait}.{wildcards.ancestry}.tsv.bgz",
        ),
        variants=lambda wildcards: os.path.join(
            config["paths"]["ld_reference"],
            "variants",
            f"{wildcards.region}.tsv",
        ),
        ld_matrix=lambda wildcards: os.path.join(
            config["paths"]["ld_reference"],
            wildcards.ancestry,
            f"{wildcards.region}.rds",
        ),
        manifest=FINEMAP_MANIFEST,
        script_dep="src/legacy/region_analysis/scripts/run_susie_rss.R",
    output:
        finemap_output("{method}", "{trait}", "{ancestry}", "{region}"),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        regions_csv=config["paths"]["regions_curated"],
        ld_dir=config["finemap"]["ld_reference_dir"],
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
        credible_set=config["finemap"].get("credible_set", 0.95),
    shell:
        r"""
        Rscript src/legacy/region_analysis/scripts/run_susie_rss.R \
          --sumstats {input.sumstats} \
          --trait {wildcards.trait} \
          --ancestry {wildcards.ancestry} \
          --method {wildcards.method} \
          --region {params.region_id} \
          --regions-csv {params.regions_csv} \
          --ld-dir {params.ld_dir} \
          --variant-list {input.variants} \
          --credible-set {params.credible_set} \
          --output {output}
        """


rule stroke_afr_susie_sweep:
    input:
        stroke_afr_outputs,
    output:
        os.path.join(FINEMAP_DIR, "stroke_AFR_sweep.done"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        echo "stroke.AFR sweep complete" > {output}
        """


rule summarize_finemap_results:
    input:
        FINEMAP_OUTPUTS,
    output:
        summary=FINEMAP_SUMMARY,
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    script:
        "../../legacy/region_analysis/scripts/summarize_finemap_results.py"


rule filter_finemap_summary:
    input:
        summary=FINEMAP_SUMMARY,
    output:
        augmented=os.path.join(FINEMAP_DIR, "finemap_summary_augmented.tsv"),
        tier1=os.path.join(FINEMAP_DIR, "finemap_tier1_high_conf.tsv"),
        tier2=os.path.join(FINEMAP_DIR, "finemap_tier2_relaxed.tsv"),
        tier3=os.path.join(FINEMAP_DIR, "finemap_tier3_coloc.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/filter_finemap_summary.py \
            --summary {input.summary} \
            --augment-out {output.augmented} \
            --tier1-out {output.tier1} \
            --tier2-out {output.tier2} \
            --tier3-out {output.tier3}
        """
