"""Quality control rules for harmonized sumstats and region analysis.

Refactored from src/legacy/region_analysis/workflow/rules/qc.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).

Plan 01-05 additions: susie_qc_aggregate, build_susie_qc_dashboard,
build_sweep_complex_regions_table rules (REQ-2 acceptance #5, T-1-04).
"""

import sys
from pathlib import Path

PYTHON_BIN = sys.executable
RESULTS_ROOT = config["paths"]["results_root"]

# Dashboard conda env (absolute path -- sidesteps DEF-01-01 --use-conda bug)
QC_DASHBOARD_ENV = str(Path(workflow.basedir) / "envs" / "qc_dashboard.yml")


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


# ===================================================================
# Plan 01-05: SuSiE fine-mapping QC dashboard (REQ-2 #5, T-1-04)
# ===================================================================


rule susie_qc_aggregate:
    """Aggregate all run_finemap JSON outputs into a single flat TSV.

    Scans {FINEMAP_DIR}/susie/ recursively for *.json and flattens D1/D2/D3
    diagnostic fields + ld_source + L_saturated + min_abs_corr_sweep D4 counts
    into one row per (trait x ancestry x region_id).
    """
    input:
        finemap_outputs=FINEMAP_OUTPUTS,
        script="src/snakemake/scripts/susie_qc_aggregate.py",
    output:
        tsv=os.path.join(FINEMAP_DIR, "qc_aggregated.tsv"),
    params:
        input_dir=os.path.join(FINEMAP_DIR, "susie"),
    conda:
        QC_DASHBOARD_ENV
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} {input.script} \
            --input-dir {params.input_dir} \
            --output {output.tsv}
        """


rule build_sweep_complex_regions_table:
    """Produce standalone REQ-2 supplementary sensitivity table.

    Two row-groups: 'known_complex' (4 pre-specified regions from
    config/susie_policy.yaml) and 'data_flagged' (L_saturated or
    n_CS_macor_0.5 >= 3). Cite directly in Phase 11 methods / OSF.
    """
    input:
        aggregated=os.path.join(FINEMAP_DIR, "qc_aggregated.tsv"),
        policy="config/susie_policy.yaml",
        script="src/snakemake/scripts/susie_qc_aggregate.py",
    output:
        sweep=os.path.join(FINEMAP_DIR, "sweep_complex_regions.tsv"),
    conda:
        QC_DASHBOARD_ENV
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} {input.script} \
            --aggregated-only \
            --input {input.aggregated} \
            --policy {input.policy} \
            --sweep-out {output.sweep}
        """


rule build_susie_qc_dashboard:
    """Render the Phase 1 SuSiE QC dashboard (Quarto HTML with DT tables).

    Falls back to rmarkdown::render if quarto CLI is unavailable in the
    active environment.
    """
    input:
        tsv=os.path.join(FINEMAP_DIR, "qc_aggregated.tsv"),
        sweep=os.path.join(FINEMAP_DIR, "sweep_complex_regions.tsv"),
        qmd="src/snakemake/scripts/susie_qc_report.qmd",
    output:
        html=os.path.join(FINEMAP_DIR, "qc_dashboard.html"),
    conda:
        QC_DASHBOARD_ENV
    threads: 1
    resources:
        mem_mb=4000,
    shell:
        r"""
        # Try quarto first; fall back to rmarkdown::render if quarto missing
        if command -v quarto >/dev/null 2>&1; then
            quarto render {input.qmd} \
                --to html \
                -P input_tsv:{input.tsv} \
                -P sweep_tsv:{input.sweep} \
                --output $(basename {output.html}) \
                --output-dir $(dirname {output.html})
        else
            Rscript -e '
                rmarkdown::render(
                  "{input.qmd}",
                  params = list(
                    input_tsv = "{input.tsv}",
                    sweep_tsv = "{input.sweep}"
                  ),
                  output_file = basename("{output.html}"),
                  output_dir = dirname("{output.html}")
                )
            '
        fi
        """
