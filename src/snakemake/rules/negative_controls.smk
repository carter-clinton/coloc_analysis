"""Negative control colocalization and PP.H4 threshold sweep (REQ-3, REQ-7).

Three sub-pipelines:
1. Curated negative controls: run QTL coloc on 3 gene sets (HLA, cosmetic, blood group).
2. Matched null loci: run QTL coloc on distance-matched random loci for empirical calibration.
3. PP.H4 threshold sweep: compute tier counts at {0.5, 0.7, 0.8, 0.9} for real + neg control loci.

T-02-18 mitigation: deterministic seeds for null loci sampling.
"""
import os
import yaml

NEG_CTRL_DIR = os.path.join(config["paths"]["results_root"], "negative_controls")
QTL_COLOC_DIR = os.path.join(config["paths"]["results_root"], "qtl_coloc")

QTL_PROC_ENV = str(
    os.path.join(workflow.basedir, "..", "..", "..", "envs", "qtl_processing.yml")
)


rule generate_null_loci:
    """Generate distance-matched null loci via bedtools shuffle (REQ-7, D-04c).

    Produces n_draws sets of null loci BED files, each matched on region size
    and gene density to real loci in regions_curated_grch38.csv. Seeds are
    deterministic: seed_base + draw_id (T-02-18 mitigation).
    """
    input:
        regions="config/regions_curated_grch38.csv",
        neg_config="config/negative_controls.yaml",
    output:
        summary=os.path.join(NEG_CTRL_DIR, "null_loci_summary.tsv"),
    params:
        script=os.path.join("src", "python", "sample_null_loci.py"),
        output_dir=os.path.join(NEG_CTRL_DIR, "null_loci"),
    conda:
        QTL_PROC_ENV
    shell:
        r"""
        mkdir -p {params.output_dir}
        python {params.script} \
          --regions {input.regions} \
          --neg-ctrl-config {input.neg_config} \
          --output-dir {params.output_dir}
        """


rule build_neg_ctrl_manifest:
    """Build negative control coloc manifest from curated gene sets.

    Reads config/negative_controls.yaml and generates manifest rows in the
    same format as qtl_coloc_manifest.tsv, one row per (neg_ctrl_set x gene x
    region x qtl_source). This manifest is then consumed by the existing
    run_qtl_coloc rule from qtl_coloc.smk -- no separate dispatch script needed.
    """
    input:
        neg_config="config/negative_controls.yaml",
        qtl_config="config/qtl_sources.yaml",
        regions="config/regions_curated_grch38.csv",
    output:
        manifest=os.path.join(NEG_CTRL_DIR, "neg_ctrl_coloc_manifest.tsv"),
    params:
        script=os.path.join("src", "python", "sample_null_loci.py"),
    conda:
        QTL_PROC_ENV
    shell:
        r"""
        mkdir -p $(dirname {output.manifest})
        python {params.script} \
          --build-neg-ctrl-manifest \
          --neg-ctrl-config {input.neg_config} \
          --qtl-config {input.qtl_config} \
          --regions {input.regions} \
          --output {output.manifest}
        """


rule run_curated_negative_controls:
    """Run QTL coloc on curated negative control gene sets.

    Uses the existing run_qtl_coloc.R via the neg_ctrl_coloc_manifest.tsv.
    Each manifest row dispatches to a separate run_qtl_coloc invocation,
    reusing the same pipeline as real loci. Results are aggregated into a
    single TSV for downstream comparison against the primary_threshold.
    """
    input:
        manifest=os.path.join(NEG_CTRL_DIR, "neg_ctrl_coloc_manifest.tsv"),
        qtl_config="config/qtl_sources.yaml",
        neg_config="config/negative_controls.yaml",
    output:
        results=os.path.join(NEG_CTRL_DIR, "curated_neg_ctrl_results.tsv"),
    params:
        script=os.path.join("src", "python", "sample_null_loci.py"),
    conda:
        QTL_PROC_ENV
    shell:
        r"""
        python {params.script} \
          --run-neg-ctrl-coloc \
          --neg-ctrl-config {input.neg_config} \
          --manifest {input.manifest} \
          --output {output.results}
        """


rule pph4_threshold_sweep:
    """Compute tier counts at each PP.H4 threshold (REQ-3).

    Runs assign_tiers.py in sweep mode to produce a table of tier counts
    (Tier A, B, C) at each of {0.5, 0.7, 0.8, 0.9}, per ancestry.
    """
    input:
        qtl_results=os.path.join(QTL_COLOC_DIR, "qtl_coloc_aggregated.tsv"),
        pph4_config="config/pph4_thresholds.yaml",
    output:
        sweep_table=os.path.join(QTL_COLOC_DIR, "pph4_threshold_sweep.tsv"),
    params:
        script=os.path.join("src", "python", "assign_tiers.py"),
    conda:
        QTL_PROC_ENV
    shell:
        r"""
        python {params.script} \
          --input {input.qtl_results} \
          --pph4-config {input.pph4_config} \
          --sweep \
          --output {output.sweep_table}
        """
