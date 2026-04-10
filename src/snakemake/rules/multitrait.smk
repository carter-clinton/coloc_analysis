"""Multi-trait colocalization rules (coloc.abf, hyprcoloc).

Refactored from src/legacy/region_analysis/workflow/rules/multitrait.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
No hardcoded rscript_bin -- conda env resolves Rscript.
"""

import os
import sys

import pandas as pd

PYTHON_BIN = sys.executable
RESULTS_ROOT = config["paths"]["results_root"]
MULTITRAIT_DIR = os.path.join(RESULTS_ROOT, "multitrait")


def hyprcoloc_group_ids():
    path = os.path.join(MULTITRAIT_DIR, "hyprcoloc_manifest.tsv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path, sep="\t")
    if df.empty or "group_id" not in df.columns:
        return []
    return df["group_id"].dropna().astype(str).unique().tolist()


def stroke_afr_coloc_targets(wildcards=None):
    path = os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path, sep="\t")
    if df.empty:
        return []
    sub = df[
        (df["ancestry"] == "AFR")
        & ((df["trait_a"] == "stroke") | (df["trait_b"] == "stroke"))
    ]
    if sub.empty:
        return []
    return [
        os.path.join(MULTITRAIT_DIR, "coloc", f"{pid}.json")
        for pid in sub["pair_id"].dropna().astype(str).tolist()
    ]


rule build_multitrait_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
    output:
        manifest=os.path.join(MULTITRAIT_DIR, "harmonized_manifest.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_multitrait_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --output {output.manifest}
        """


rule build_coloc_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
        tier3=os.path.join(FINEMAP_DIR, "finemap_tier3_coloc.tsv"),
    output:
        manifest=os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_coloc_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --tier3 {input.tier3} \
            --output {output.manifest}
        """


rule run_multitrait_placeholder:
    input:
        multitrait_manifest=os.path.join(MULTITRAIT_DIR, "harmonized_manifest.tsv"),
        coloc_manifest=os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv"),
    output:
        done=os.path.join(MULTITRAIT_DIR, "placeholder.done"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} - <<'PY'
import pandas as pd
from pathlib import Path
mt_df = pd.read_csv("{input.multitrait_manifest}", sep="\t")
coloc_df = pd.read_csv("{input.coloc_manifest}", sep="\t")
regions = mt_df['region_count'].iloc[0] if not mt_df.empty else 0
print(f"[multitrait] Harmonized entries: {{len(mt_df)}} across {{regions}} regions")
print(f"[coloc] Planned comparisons: {{len(coloc_df)}}")
Path("{output.done}").write_text("multitrait placeholder complete\n")
PY
        """


rule run_coloc_pair:
    input:
        manifest=os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv"),
    output:
        os.path.join(MULTITRAIT_DIR, "coloc", "{pair_id}.json"),
    params:
        ref_fasta=lambda wc: config.get("paths", {}).get("ref_fasta", ""),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        REF_ARG=""
        if [ -n "{params.ref_fasta}" ] && [ -f "{params.ref_fasta}" ]; then
          REF_ARG="--ref-fasta {params.ref_fasta}"
        fi
        Rscript src/legacy/region_analysis/scripts/run_coloc.R \
            --manifest {input.manifest} \
            --pair-id {wildcards.pair_id} \
            --output {output} \
            $REF_ARG
        """


rule stroke_afr_coloc_sweep:
    input:
        stroke_afr_coloc_targets,
    output:
        os.path.join(MULTITRAIT_DIR, "stroke_AFR_coloc.done"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        echo "stroke.AFR coloc sweep complete" > {output}
        """


rule summarize_coloc_results:
    input:
        manifest=os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv"),
    output:
        summary=os.path.join(MULTITRAIT_DIR, "coloc_summary.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/summarize_coloc_results.py \
            --manifest {input.manifest} \
            --coloc-dir {MULTITRAIT_DIR}/coloc \
            --output {output.summary}
        """


rule build_hyprcoloc_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
        tier3=os.path.join(FINEMAP_DIR, "finemap_tier3_coloc.tsv"),
    output:
        manifest=os.path.join(MULTITRAIT_DIR, "hyprcoloc_manifest.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_hyprcoloc_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --tier3 {input.tier3} \
            --output {output.manifest}
        """


rule run_hyprcoloc_group:
    input:
        manifest=os.path.join(MULTITRAIT_DIR, "hyprcoloc_manifest.tsv"),
    output:
        os.path.join(MULTITRAIT_DIR, "hyprcoloc", "{group_id}.json"),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        Rscript src/legacy/region_analysis/scripts/run_hyprcoloc.R \
            --manifest {input.manifest} \
            --group-id {wildcards.group_id} \
            --output {output}
        """


rule summarize_hyprcoloc:
    input:
        manifest=os.path.join(MULTITRAIT_DIR, "hyprcoloc_manifest.tsv"),
        outputs=lambda wildcards: expand(
            os.path.join(MULTITRAIT_DIR, "hyprcoloc", "{group_id}.json"),
            group_id=hyprcoloc_group_ids(),
        ),
    output:
        summary=os.path.join(MULTITRAIT_DIR, "hyprcoloc_summary.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/summarize_hyprcoloc_results.py \
            --manifest {input.manifest} \
            --out-dir {MULTITRAIT_DIR}/hyprcoloc \
            --output {output.summary}
        """


rule augment_coloc_summary:
    input:
        summary=os.path.join(MULTITRAIT_DIR, "coloc_summary.tsv"),
        qc_report=os.path.join(RESULTS_ROOT, "qc", "region_trait_qc.tsv"),
        effect_actions=os.path.join(RESULTS_ROOT, "qc", "effect_scale_actions_fixed.tsv"),
    output:
        summary=os.path.join(MULTITRAIT_DIR, "coloc_summary_augmented.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/augment_coloc_summary.py \
            --coloc-summary {input.summary} \
            --region-trait-qc {input.qc_report} \
            --effect-scale-actions {input.effect_actions} \
            --output {output.summary}
        """


rule build_coloc_clean_sets:
    input:
        summary=os.path.join(MULTITRAIT_DIR, "coloc_summary_augmented.tsv"),
    output:
        clean=os.path.join(MULTITRAIT_DIR, "coloc_clean.tsv"),
        clean_h4=os.path.join(MULTITRAIT_DIR, "coloc_clean_h4.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_coloc_clean_sets.py
        """


rule build_coloc_h4_reports:
    input:
        summary=os.path.join(MULTITRAIT_DIR, "coloc_summary_augmented.tsv"),
    output:
        main=os.path.join(RESULTS_ROOT, "analysis", "coloc_main_h4.tsv"),
        candidate=os.path.join(RESULTS_ROOT, "analysis", "coloc_candidate_h4.tsv"),
        counts=os.path.join(RESULTS_ROOT, "analysis", "coloc_h4_traitpair_counts.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_coloc_h4_reports.py
        """


rule build_coloc_top_hits_table:
    input:
        candidate=os.path.join(RESULTS_ROOT, "analysis", "coloc_candidate_h4.tsv"),
        clean=os.path.join(RESULTS_ROOT, "analysis", "coloc_main_h4.tsv"),
        effect_scale=os.path.join(RESULTS_ROOT, "qc", "effect_scale_report_fixed.tsv"),
        stroke_afr_susie=os.path.join(FINEMAP_DIR, "stroke_AFR_sweep.done"),
        stroke_afr_coloc=os.path.join(MULTITRAIT_DIR, "stroke_AFR_coloc.done"),
    output:
        table=os.path.join(RESULTS_ROOT, "analysis", "coloc_top_hits_table.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_coloc_top_hits_table.py \
            --candidate {input.candidate} \
            --clean {input.clean} \
            --effect-scale {input.effect_scale} \
            --output {output.table}
        """
