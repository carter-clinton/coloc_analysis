import os
import sys

import pandas as pd

PYTHON_BIN = sys.executable
COLOC_RSCRIPT = config.get("finemap", {}).get("rscript_bin", "Rscript")
HYPRCOLOC_RSCRIPT = config.get("finemap", {}).get("rscript_bin", "Rscript")

def hyprcoloc_group_ids():
    path = "results/multitrait/hyprcoloc_manifest.tsv"
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path, sep="\t")
    if df.empty or "group_id" not in df.columns:
        return []
    return df["group_id"].dropna().astype(str).unique().tolist()


def stroke_afr_coloc_targets(wildcards=None):
    path = "results/multitrait/coloc_manifest.tsv"
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
        os.path.join("results", "multitrait", "coloc", f"{pid}.json")
        for pid in sub["pair_id"].dropna().astype(str).tolist()
    ]


rule build_multitrait_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"]
    output:
        manifest="results/multitrait/harmonized_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/create_multitrait_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --output {output.manifest}
        """

rule build_coloc_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
        tier3="results/fine_mapping/finemap_tier3_coloc.tsv"
    output:
        manifest="results/multitrait/coloc_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/create_coloc_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --tier3 {input.tier3} \
            --output {output.manifest}
        """


rule run_multitrait_placeholder:
    input:
        multitrait_manifest="results/multitrait/harmonized_manifest.tsv",
        coloc_manifest="results/multitrait/coloc_manifest.tsv"
    output:
        done="results/multitrait/placeholder.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
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
        manifest="results/multitrait/coloc_manifest.tsv"
    output:
        "results/multitrait/coloc/{pair_id}.json"
    params:
        ref_fasta=lambda wc: config.get("paths", {}).get("ref_fasta", "")
    conda:
        "../../envs/r_stats_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        REF_ARG=""
        if [ -n "{params.ref_fasta}" ] && [ -f "{params.ref_fasta}" ]; then
          REF_ARG="--ref-fasta {params.ref_fasta}"
        fi
        {COLOC_RSCRIPT} scripts/run_coloc.R \
            --manifest {input.manifest} \
            --pair-id {wildcards.pair_id} \
            --output {output} \
            $REF_ARG
        """

rule stroke_afr_coloc_sweep:
    input:
        stroke_afr_coloc_targets
    output:
        "results/multitrait/stroke_AFR_coloc.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        echo "stroke.AFR coloc sweep complete" > {output}
        """

rule summarize_coloc_results:
    input:
        manifest="results/multitrait/coloc_manifest.tsv"
    output:
        summary="results/multitrait/coloc_summary.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/summarize_coloc_results.py \
            --manifest {input.manifest} \
            --coloc-dir results/multitrait/coloc \
            --output {output.summary}
        """

rule build_hyprcoloc_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
        tier3="results/fine_mapping/finemap_tier3_coloc.tsv"
    output:
        manifest="results/multitrait/hyprcoloc_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/create_hyprcoloc_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --tier3 {input.tier3} \
            --output {output.manifest}
        """

rule run_hyprcoloc_group:
    input:
        manifest="results/multitrait/hyprcoloc_manifest.tsv"
    output:
        "results/multitrait/hyprcoloc/{group_id}.json"
    conda:
        "../../envs/r_stats_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {HYPRCOLOC_RSCRIPT} scripts/run_hyprcoloc.R \
            --manifest {input.manifest} \
            --group-id {wildcards.group_id} \
            --output {output}
        """

rule summarize_hyprcoloc:
    input:
        manifest="results/multitrait/hyprcoloc_manifest.tsv",
        outputs=lambda wildcards: expand(
            "results/multitrait/hyprcoloc/{group_id}.json",
            group_id=hyprcoloc_group_ids(),
        )
    output:
        summary="results/multitrait/hyprcoloc_summary.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/summarize_hyprcoloc_results.py \
            --manifest {input.manifest} \
            --out-dir results/multitrait/hyprcoloc \
            --output {output.summary}
        """

rule augment_coloc_summary:
    input:
        summary="results/multitrait/coloc_summary.tsv",
        qc_report="results/qc/region_trait_qc.tsv",
        effect_actions="results/qc/effect_scale_actions_fixed.tsv"
    output:
        summary="results/multitrait/coloc_summary_augmented.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/augment_coloc_summary.py \
            --coloc-summary {input.summary} \
            --region-trait-qc {input.qc_report} \
            --effect-scale-actions {input.effect_actions} \
            --output {output.summary}
        """

rule build_coloc_clean_sets:
    input:
        summary="results/multitrait/coloc_summary_augmented.tsv"
    output:
        clean="results/multitrait/coloc_clean.tsv",
        clean_h4="results/multitrait/coloc_clean_h4.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/build_coloc_clean_sets.py
        """

rule build_coloc_h4_reports:
    input:
        summary="results/multitrait/coloc_summary_augmented.tsv"
    output:
        main="results/analysis/coloc_main_h4.tsv",
        candidate="results/analysis/coloc_candidate_h4.tsv",
        counts="results/analysis/coloc_h4_traitpair_counts.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/build_coloc_h4_reports.py
        """

rule build_coloc_top_hits_table:
    input:
        candidate="results/analysis/coloc_candidate_h4.tsv",
        clean="results/analysis/coloc_main_h4.tsv",
        effect_scale="results/qc/effect_scale_report_fixed.tsv",
        stroke_afr_susie="results/fine_mapping/stroke_AFR_sweep.done",
        stroke_afr_coloc="results/multitrait/stroke_AFR_coloc.done"
    output:
        table="results/analysis/coloc_top_hits_table.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/build_coloc_top_hits_table.py \
            --candidate {input.candidate} \
            --clean {input.clean} \
            --effect-scale {input.effect_scale} \
            --output {output.table}
        """
