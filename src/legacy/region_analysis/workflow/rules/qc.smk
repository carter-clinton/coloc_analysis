import sys

PYTHON_BIN = sys.executable


rule summarize_harmonized_sumstats:
    input:
        harmonized=HARMONIZED_ALL
    output:
        report="results/qc/harmonized_summary.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/qc_harmonized_sumstats.py \
            --harmonized {input.harmonized} \
            --output {output.report}
        """

rule effect_scale_qc:
    input:
        harmonized=HARMONIZED_ALL
    output:
        report="results/qc/effect_scale_report_fixed.tsv",
        actions="results/qc/effect_scale_actions_fixed.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/qc_effect_scale.py \
            --inputs {input.harmonized} \
            --out_report {output.report} \
            --out_actions {output.actions} \
            --sample 200000
        """

rule check_region_overlap:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"]
    output:
        report="results/qc/region_overlap.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/check_region_overlap.py \
            --regions {input.regions} \
            --harmonized {input.harmonized} \
            --output {output.report}
        """

rule build_region_trait_qc:
    input:
        summary="results/fine_mapping/finemap_summary_augmented.tsv",
        regions=config["paths"]["regions_curated"]
    output:
        report="results/qc/region_trait_qc.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    params:
        harmonized_dir=HARMONIZED_DIR
    shell:
        r"""
        {PYTHON_BIN} scripts/build_region_trait_qc.py \
            --finemap-summary {input.summary} \
            --regions {input.regions} \
            --harmonized-dir {params.harmonized_dir} \
            --output {output.report}
        """
