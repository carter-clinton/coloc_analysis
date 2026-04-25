# M1 Wave 4 — Quarto QC reports + trait_inventory.yaml builder.
#
# Rules
# -----
#  - m1_qc_per_trait     : render src/R/qc/m1_qc_report.qmd to per-trait HTML
#  - m1_qc_index         : render src/R/qc/m1_qc_index.qmd to qc_log/index.html
#  - m1_build_trait_inventory : run src/python/build_trait_inventory.py
#
# Plan ref: m1-04-qc-reports-inventory-manifest-PLAN.md Task 1 step (D).

import os

HARM_DIR     = config["paths"]["harmonized_sumstats"]
PARQ_DIR     = config["paths"]["harmonized_parquet"]
QC_DIR       = config["paths"]["qc_log"]
RG_LOG_DIR   = config["paths"]["ldsc_rg_logs"]
LDSC_OVERLAP = config["paths"]["ldsc_overlap"]
RAW_DIR_V2   = config["paths"]["raw_sumstats_v2"]


rule m1_qc_per_trait:
    """Render the 9-section per-trait QC HTML for one D-16 cell.

    The .qmd reads the parquet via arrow::read_parquet and greps focal_*.log
    files in rg_log_dir for h2_obs / h2_int extraction (W1 fix — depend on
    the entire rg_logs/ directory rather than a per-trait focal log lookup).
    """
    input:
        parquet = os.path.join(PARQ_DIR,
            "{trait}.{ancestry}.{consortium}.{year}.GRCh37.parquet"),
        qmd     = "src/R/qc/m1_qc_report.qmd",
        loci    = "src/R/qc/control_loci.csv",
    output:
        html = os.path.join(QC_DIR,
            "{trait}.{ancestry}.{consortium}.{year}.qc.html"),
    params:
        rg_log_dir = RG_LOG_DIR,
        qc_json    = lambda wc: os.path.join(QC_DIR,
            f"{wc.trait}.{wc.ancestry}.{wc.consortium}.{wc.year}.qc.json"),
        harmonized_tsv = lambda wc: os.path.join(HARM_DIR,
            f"{wc.trait}.{wc.ancestry}.{wc.consortium}.{wc.year}.GRCh37.tsv.bgz"),
    conda: "../../../envs/m1-qc.yml"
    resources: mem_mb=6000, runtime=2880
    shell:
        r"""
        # CR-01 fix: render into a per-trait temp dir to avoid races on
        # the shared {QC_DIR}/m1_qc_report.html name when --cores>1.
        mkdir -p {QC_DIR}
        TMPDIR=$(mktemp -d -p {QC_DIR} qc_render.XXXXXX)
        quarto render {input.qmd} \
          --to html \
          --output-dir "$TMPDIR" \
          -P trait:{wildcards.trait} \
          -P ancestry:{wildcards.ancestry} \
          -P consortium:{wildcards.consortium} \
          -P year:{wildcards.year} \
          -P parquet:{input.parquet} \
          -P harmonized_tsv:{params.harmonized_tsv} \
          -P rg_log_dir:{params.rg_log_dir} \
          -P qc_json:{params.qc_json} \
          -P control_loci_csv:{input.loci}
        mv "$TMPDIR/m1_qc_report.html" {output.html}
        rm -rf "$TMPDIR"
        """


rule m1_qc_index:
    """Aggregate per-trait QC sidecars + render the NxN intercept heatmap."""
    input:
        inventory = "config/trait_inventory.yaml",
        matrix    = os.path.join(LDSC_OVERLAP,
            "bivariate_intercept_matrix_2026-04.tsv"),
        warnings  = os.path.join(LDSC_OVERLAP, "rg_validation_warnings.json"),
        qmd       = "src/R/qc/m1_qc_index.qmd",
    output:
        html = os.path.join(QC_DIR, "index.html"),
    params:
        qc_log_dir = QC_DIR,
    conda: "../../../envs/m1-qc.yml"
    resources: mem_mb=4000, runtime=1440
    shell:
        r"""
        # CR-01 symmetry fix: render into a temp dir then move.
        # m1_qc_index is single-output and won't race with itself, but
        # the same pattern is applied for consistency with m1_qc_per_trait
        # and to avoid clobbering an in-progress per-trait render that
        # incidentally landed in {QC_DIR}.
        mkdir -p {QC_DIR}
        TMPDIR=$(mktemp -d -p {QC_DIR} qc_index.XXXXXX)
        quarto render {input.qmd} \
          --to html \
          --output-dir "$TMPDIR" \
          -P inventory:{input.inventory} \
          -P matrix:{input.matrix} \
          -P warnings:{input.warnings} \
          -P qc_log_dir:{params.qc_log_dir}
        mv "$TMPDIR/m1_qc_index.html" {output.html}
        rm -rf "$TMPDIR"
        """


rule m1_build_trait_inventory:
    """Build config/trait_inventory.yaml from SUMSTATS-UPGRADE.tsv +
    SHA-256 manifests + per-trait qc.json sidecars + LDSC rg logs."""
    input:
        tsv      = ".planning/amendments/SUMSTATS-UPGRADE.tsv",
        raw_sha  = os.path.join(RAW_DIR_V2, "sha256_manifest.tsv"),
        harm_sha = os.path.join(HARM_DIR, "sha256_manifest.tsv"),
    output:
        yaml = "config/trait_inventory.yaml",
    params:
        qc_log_dir = QC_DIR,
        rg_log_dir = RG_LOG_DIR,
    conda: "../../../envs/m1-harmonize.yml"
    resources: mem_mb=2000, runtime=60
    shell:
        r"""
        python src/python/build_trait_inventory.py \
          --tsv {input.tsv} \
          --raw-manifest {input.raw_sha} \
          --harm-manifest {input.harm_sha} \
          --qc-log-dir {params.qc_log_dir} \
          --rg-log-dir {params.rg_log_dir} \
          --output {output.yaml}
        """
