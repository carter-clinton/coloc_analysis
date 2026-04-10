"""Quality control rules for harmonized sumstats and region analysis.

Refactored from src/legacy/region_analysis/workflow/rules/qc.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
"""

import sys

PYTHON_BIN = sys.executable
RESULTS_ROOT = config["paths"]["results_root"]


rule summarize_harmonized_sumstats:
    input:
        harmonized=HARMONIZED_ALL,
    output:
        report=os.path.join(RESULTS_ROOT, "qc", "harmonized_summary.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/qc_harmonized_sumstats.py \
            --harmonized {input.harmonized} \
            --output {output.report}
        """


rule effect_scale_qc:
    input:
        harmonized=HARMONIZED_ALL,
    output:
        report=os.path.join(RESULTS_ROOT, "qc", "effect_scale_report_fixed.tsv"),
        actions=os.path.join(RESULTS_ROOT, "qc", "effect_scale_actions_fixed.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/qc_effect_scale.py \
            --inputs {input.harmonized} \
            --out_report {output.report} \
            --out_actions {output.actions} \
            --sample 200000
        """


rule check_region_overlap:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
    output:
        report=os.path.join(RESULTS_ROOT, "qc", "region_overlap.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/check_region_overlap.py \
            --regions {input.regions} \
            --harmonized {input.harmonized} \
            --output {output.report}
        """


rule build_region_trait_qc:
    input:
        summary=os.path.join(FINEMAP_DIR, "finemap_summary_augmented.tsv"),
        regions=config["paths"]["regions_curated"],
    output:
        report=os.path.join(RESULTS_ROOT, "qc", "region_trait_qc.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        harmonized_dir=HARMONIZED_DIR,
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_region_trait_qc.py \
            --finemap-summary {input.summary} \
            --regions {input.regions} \
            --harmonized-dir {params.harmonized_dir} \
            --output {output.report}
        """
