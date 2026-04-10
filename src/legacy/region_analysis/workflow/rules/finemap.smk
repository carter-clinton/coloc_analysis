import os
import sys

FINEMAP_DIR = config["finemap"]["output_dir"]
FINEMAP_METHODS = config["finemap"]["methods"]
RSCRIPT_BIN = config["finemap"].get("rscript_bin", "Rscript")
PYTHON_BIN = sys.executable

def finemap_output(path_method, trait, ancestry, region):
    return os.path.join(
        FINEMAP_DIR,
        path_method,
        f"{trait}.{ancestry}.{region}.json",
    )

def stroke_afr_outputs(wildcards=None):
    return [
        os.path.join(
            FINEMAP_DIR,
            method,
            f"stroke.AFR.{region_safe}.json",
        )
        for method in FINEMAP_METHODS
        for _, region_safe in REGION_INFOS
    ]

rule build_finemap_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"]
    output:
        manifest=FINEMAP_MANIFEST
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    params:
        methods=",".join(FINEMAP_METHODS)
    shell:
        r"""
        {PYTHON_BIN} scripts/create_finemap_tasks.py \
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
        script_dep="scripts/run_susie_rss.R"
    output:
        finemap_output("{method}", "{trait}", "{ancestry}", "{region}")
    conda:
        "../../envs/r_stats_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    params:
        regions_csv=config["paths"]["regions_curated"],
        ld_dir=config["finemap"]["ld_reference_dir"],
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
        credible_set=config["finemap"].get("credible_set", 0.95),
        rscript=RSCRIPT_BIN
    shell:
        r"""
        {params.rscript} scripts/run_susie_rss.R \
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
        stroke_afr_outputs
    output:
        "results/fine_mapping/stroke_AFR_sweep.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        echo "stroke.AFR sweep complete" > {output}
        """

rule summarize_finemap_results:
    input:
        FINEMAP_OUTPUTS
    output:
        summary=FINEMAP_SUMMARY
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    script:
        "../../scripts/summarize_finemap_results.py"

rule filter_finemap_summary:
    input:
        summary=FINEMAP_SUMMARY
    output:
        augmented="results/fine_mapping/finemap_summary_augmented.tsv",
        tier1="results/fine_mapping/finemap_tier1_high_conf.tsv",
        tier2="results/fine_mapping/finemap_tier2_relaxed.tsv",
        tier3="results/fine_mapping/finemap_tier3_coloc.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/filter_finemap_summary.py \
            --summary {input.summary} \
            --augment-out {output.augmented} \
            --tier1-out {output.tier1} \
            --tier2-out {output.tier2} \
            --tier3-out {output.tier3}
        """
