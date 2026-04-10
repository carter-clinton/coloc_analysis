#!/usr/bin/env bash
#==============================================================================
# CREATE REPRODUCIBILITY PACKAGE FOR ADMIXMAP ANALYSIS
#
# Packages all scripts, configuration, workflow definitions, and conda
# environment specifications from the three analysis modules:
#   - region_analysis/  (Snakemake pipeline: harmonization -> coloc)
#   - genome_wide/      (genome-wide colocalization via LSF job arrays)
#   - ml/               (ML-enhanced interpretation)
#
# Output: admixmap_reproducibility_package_YYYYMMDD.zip
#==============================================================================
set -euo pipefail

PROJECT_ROOT="/gpfs_common/share01/clintonlab/ckclinto/admixmap"
DATESTAMP=$(date +%Y%m%d)
PACKAGE_NAME="admixmap_reproducibility_package_${DATESTAMP}"
STAGING_DIR="${PROJECT_ROOT}/${PACKAGE_NAME}"
ZIP_FILE="${PROJECT_ROOT}/${PACKAGE_NAME}.zip"

# Clean up staging directory on error or exit
cleanup() { rm -rf "$STAGING_DIR"; }
trap cleanup ERR

# Verify project root exists
if [[ ! -d "$PROJECT_ROOT" ]]; then
    echo "ERROR: Project root not found: $PROJECT_ROOT" >&2
    exit 1
fi

echo "============================================================"
echo "Creating reproducibility package: ${PACKAGE_NAME}"
echo "============================================================"

#----------------------------------------------------------------------
# 1. Create staging directory structure
#----------------------------------------------------------------------
echo "Setting up staging directory..."
mkdir -p "${STAGING_DIR}/region_analysis/config"
mkdir -p "${STAGING_DIR}/region_analysis/envs"
mkdir -p "${STAGING_DIR}/region_analysis/workflow/rules"
mkdir -p "${STAGING_DIR}/region_analysis/scripts"
mkdir -p "${STAGING_DIR}/region_analysis/genome_wide_analysis/scripts"
mkdir -p "${STAGING_DIR}/genome_wide/scripts"
mkdir -p "${STAGING_DIR}/genome_wide/envs"
mkdir -p "${STAGING_DIR}/ml/scripts"

#----------------------------------------------------------------------
# 2. region_analysis/ -- config, envs, workflow, top-level files
#----------------------------------------------------------------------
echo "Copying region_analysis configs, envs, workflow..."

# Config files
cp "${PROJECT_ROOT}/region_analysis/config/config.yaml"          "${STAGING_DIR}/region_analysis/config/"
cp "${PROJECT_ROOT}/region_analysis/config/datasets.yaml"        "${STAGING_DIR}/region_analysis/config/"
cp "${PROJECT_ROOT}/region_analysis/config/cluster_lsf.yaml"     "${STAGING_DIR}/region_analysis/config/"
cp "${PROJECT_ROOT}/region_analysis/config/regions_curated.csv"  "${STAGING_DIR}/region_analysis/config/"
cp "${PROJECT_ROOT}/region_analysis/config/regions_tiled.csv"    "${STAGING_DIR}/region_analysis/config/"

# Conda environment definitions
cp "${PROJECT_ROOT}/region_analysis/envs/snakemake_env.yml"  "${STAGING_DIR}/region_analysis/envs/"
cp "${PROJECT_ROOT}/region_analysis/envs/r_stats_env.yml"    "${STAGING_DIR}/region_analysis/envs/"
cp "${PROJECT_ROOT}/region_analysis/envs/plink_env.yml"      "${STAGING_DIR}/region_analysis/envs/"

# Snakemake workflow
cp "${PROJECT_ROOT}/region_analysis/workflow/Snakefile"  "${STAGING_DIR}/region_analysis/workflow/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/sumstats.smk"     "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/regions.smk"      "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/qc.smk"           "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/ld_reference.smk"  "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/finemap.smk"      "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/multitrait.smk"   "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/pgs.smk"          "${STAGING_DIR}/region_analysis/workflow/rules/"
cp "${PROJECT_ROOT}/region_analysis/workflow/rules/mr.smk"           "${STAGING_DIR}/region_analysis/workflow/rules/"

# Top-level files
cp "${PROJECT_ROOT}/region_analysis/run_snakemake.sh"   "${STAGING_DIR}/region_analysis/"
cp "${PROJECT_ROOT}/region_analysis/setup_project.sh"   "${STAGING_DIR}/region_analysis/"
cp "${PROJECT_ROOT}/region_analysis/README.md"          "${STAGING_DIR}/region_analysis/"

#----------------------------------------------------------------------
# 3. region_analysis/scripts/ -- Python (excluding diagnostics/)
#----------------------------------------------------------------------
echo "Copying region_analysis Python scripts..."

RA_SCRIPTS="${PROJECT_ROOT}/region_analysis/scripts"
RA_DEST="${STAGING_DIR}/region_analysis/scripts"

PYTHON_SCRIPTS=(
    __init__.py
    manifest_utils.py
    utils_logging.py
    dataset_config.py
    harmonize_sumstats.py
    harmonize_hypertension.py
    qc_harmonized_sumstats.py
    qc_effect_scale.py
    create_finemap_tasks.py
    create_coloc_manifest.py
    create_hyprcoloc_manifest.py
    create_multitrait_manifest.py
    create_pgs_manifest.py
    create_mr_design.py
    build_ld_rds.py
    build_1kg_sample_lists.py
    build_tiled_regions.py
    build_coloc_h4_reports.py
    build_coloc_main_hits.py
    build_coloc_top_hits_table.py
    build_coloc_clean_sets.py
    build_coloc_shared_counts.py
    build_a_list_pip_summary.py
    build_region_trait_qc.py
    build_run_manifest.py
    build_tables_index.py
    collect_region_variants.py
    collect_region_variants_tabix.py
    make_regions_from_loci.py
    check_region_overlap.py
    filter_finemap_summary.py
    fine_mapping_gap_reports.py
    thin_variant_list.py
    summarize_finemap_results.py
    summarize_coloc_results.py
    summarize_hyprcoloc_results.py
    summarize_effect_scale.py
    cross_ancestry_compare.py
    replication_compare.py
    annotate_replication_ld_r2.py
    augment_coloc_summary.py
    add_p_from_beta_se.py
    plan_ld_builds.py
    run_ld_build_plan.py
    retile_regions.py
    run_rad50_window_shift.py
    run_finemap_placeholder.py
    stage_mock_sumstats.py
    update_figures_index_alist.py
    extract_hyprcoloc_focus.py
    comprehensive_coloc_analysis.py
)

for f in "${PYTHON_SCRIPTS[@]}"; do
    cp "${RA_SCRIPTS}/${f}" "${RA_DEST}/"
done

#----------------------------------------------------------------------
# 4. region_analysis/scripts/ -- R scripts (excluding diagnostics/)
#----------------------------------------------------------------------
echo "Copying region_analysis R scripts..."

R_SCRIPTS=(
    run_coloc.R
    run_susie_rss.R
    run_hyprcoloc.R
    compute_ld_r2.R
    create_figures.R
    plot_summary_figures.R
    plot_additional_figures.R
    plot_additional_panels.R
    plot_coloc_h4_summary.R
    create_pathway_figures_additional.R
    create_pathway_network_figure.R
    create_locuszoom_plots.R
)

for f in "${R_SCRIPTS[@]}"; do
    cp "${RA_SCRIPTS}/${f}" "${RA_DEST}/"
done

#----------------------------------------------------------------------
# 5. region_analysis/scripts/ -- Shell scripts (excluding diagnostics/)
#----------------------------------------------------------------------
echo "Copying region_analysis shell scripts..."

SH_SCRIPTS=(
    compute_ld_plink.sh
    run_afr_coloc_batch.sh
    run_hypertension_coloc_batch.sh
    liftover_asthma_afr.sh
    regenerate_coloc_summaries.sh
    analyze_afr_results.sh
    simple_coloc_summary.sh
    pathway_enrichment_analysis.sh
    comprehensive_coloc_analysis.sh
    publication_additions.sh
    rerun_hypertension_t2d.sh
    monitor_afr_coloc.sh
    monitor_hypertension_coloc.sh
    monitor_hypertension_rerun.sh
)

for f in "${SH_SCRIPTS[@]}"; do
    cp "${RA_SCRIPTS}/${f}" "${RA_DEST}/"
done

#----------------------------------------------------------------------
# 6. region_analysis/genome_wide_analysis/scripts/
#----------------------------------------------------------------------
echo "Copying region_analysis genome_wide_analysis scripts..."

cp "${PROJECT_ROOT}/region_analysis/genome_wide_analysis/scripts/create_annotated_signals.py"        "${STAGING_DIR}/region_analysis/genome_wide_analysis/scripts/"
cp "${PROJECT_ROOT}/region_analysis/genome_wide_analysis/scripts/pathway_enrichment_genomewide.py"   "${STAGING_DIR}/region_analysis/genome_wide_analysis/scripts/"

#----------------------------------------------------------------------
# 7. genome_wide/ -- scripts (excluding generated chunk files)
#----------------------------------------------------------------------
echo "Copying genome_wide scripts..."

GW_SCRIPTS="${PROJECT_ROOT}/genome_wide/scripts"
GW_DEST="${STAGING_DIR}/genome_wide/scripts"

GW_FILES=(
    harmonize_sumstats.py
    identify_genomewide_regions.py
    create_coloc_manifest.py
    aggregate_genomewide_results.py
    compare_to_region_analysis.py
    annotate_genes.py
    run_coloc.R
    run_coloc_genomewide.R
    create_genomewide_figures.R
    submit_genomewide_coloc.sh
    submit_coloc_chunk.sh
    rerun_failed_jobs.sh
    submit_rerun.sh
    monitor_jobs.sh
)

for f in "${GW_FILES[@]}"; do
    cp "${GW_SCRIPTS}/${f}" "${GW_DEST}/"
done

# Conda env
cp "${PROJECT_ROOT}/genome_wide/envs/r_stats_env.yml"  "${STAGING_DIR}/genome_wide/envs/"

#----------------------------------------------------------------------
# 8. ml/ -- scripts
#----------------------------------------------------------------------
echo "Copying ml scripts..."

ML_SCRIPTS="${PROJECT_ROOT}/ml/scripts"
ML_DEST="${STAGING_DIR}/ml/scripts"

ML_FILES=(
    recover_coloc_errors.py
    characterize_coloc_errors.py
    cross_ancestry_prediction.py
    gene_prioritization.py
    variant_effect_prediction.py
)

for f in "${ML_FILES[@]}"; do
    cp "${ML_SCRIPTS}/${f}" "${ML_DEST}/"
done

#----------------------------------------------------------------------
# 9. Generate README
#----------------------------------------------------------------------
echo "Generating README..."

cat > "${STAGING_DIR}/README.md" << 'READMEEOF'
# Admixmap Analysis -- Reproducibility Package

## Overview

This package contains all scripts, configuration files, Snakemake workflow
definitions, and conda environment specifications needed to reproduce the
admixmap multi-trait colocalization analysis. The analysis studies shared
genetic architecture across five cardiometabolic/respiratory traits
(BMI, T2D, hypertension, asthma, stroke) in European and African ancestry
populations using GWAS summary statistics.

## Directory Structure

```
region_analysis/               # Region-based Snakemake analysis pipeline
  config/                      # Configuration files
    config.yaml                #   Traits, ancestries, paths, workflow params
    datasets.yaml              #   GWAS data sources, column mappings, URLs
    cluster_lsf.yaml           #   LSF resource allocation per rule
    regions_curated.csv        #   8 seed genomic loci
    regions_tiled.csv          #   ~200 tiled sub-regions (expanded from seed)
  envs/                        # Conda environment definitions
    snakemake_env.yml          #   Python 3.11, Snakemake 8, pandas, scipy, ...
    r_stats_env.yml            #   R, coloc, susieR, data.table, tidyverse, ...
    plink_env.yml              #   PLINK, bcftools
  workflow/                    # Snakemake workflow
    Snakefile                  #   Main orchestrator
    rules/                     #   Modular rule files
      sumstats.smk             #     Download & harmonize GWAS summary stats
      regions.smk              #     Convert curated loci to BED regions
      qc.smk                   #     QC of harmonized summary stats
      ld_reference.smk         #     Build LD reference from 1000 Genomes
      finemap.smk              #     Fine-mapping via SuSiE
      multitrait.smk           #     Multi-trait colocalization manifests
      pgs.smk                  #     PRS-CSx / LDpred2 scaffolding
      mr.smk                   #     Mendelian randomization design
  scripts/                     # Python, R, and shell analysis scripts
  genome_wide_analysis/        # Additional genome-wide analysis scripts
  README.md                    # Original project documentation
  run_snakemake.sh             # Workflow launcher
  setup_project.sh             # Full project bootstrapper

genome_wide/                   # Genome-wide colocalization analysis
  scripts/                     # Analysis, submission, monitoring scripts
  envs/                        # Conda environment definitions

ml/                            # ML-enhanced analysis
  scripts/                     # Machine learning interpretation scripts
```

## Analysis Pipeline

### Stage 1: Region-Based Analysis (region_analysis/)

A Snakemake-orchestrated pipeline for multi-trait genetic analysis across
curated genomic regions.

**Setup:**
```bash
# 1. Install conda environments
mamba env create -f region_analysis/envs/snakemake_env.yml
mamba env create -f region_analysis/envs/r_stats_env.yml
mamba env create -f region_analysis/envs/plink_env.yml

# 2. Activate the main environment
conda activate la_multitrait

# 3. Configure data paths in region_analysis/config/config.yaml
#    and dataset sources in region_analysis/config/datasets.yaml

# 4. Run the pipeline
cd region_analysis && snakemake --cores 4 --use-conda
```

**Workflow modules:**
- `sumstats.smk` -- Download and harmonize GWAS summary statistics
- `regions.smk` -- Convert curated loci to BED-format regions
- `qc.smk` -- Quality control of harmonized summary statistics
- `ld_reference.smk` -- Build LD reference panels from 1000 Genomes
- `finemap.smk` -- Fine-mapping via SuSiE
- `multitrait.smk` -- Multi-trait colocalization task manifests
- `pgs.smk` -- Polygenic score planning (PRS-CSx / LDpred2)
- `mr.smk` -- Mendelian randomization design

**Key scripts:**
- `harmonize_sumstats.py` / `dataset_config.py` -- Standardize GWAS columns
- `create_coloc_manifest.py` -- Generate colocalization task lists
- `run_coloc.R` / `run_susie_rss.R` / `run_hyprcoloc.R` -- Statistical engines
- `summarize_coloc_results.py` / `build_coloc_h4_reports.py` -- Result aggregation
- `create_figures.R` / `plot_summary_figures.R` -- Visualization
- `pathway_enrichment_analysis.sh` -- GO/KEGG pathway analysis

**Batch launchers (LSF):**
- `run_afr_coloc_batch.sh` -- African ancestry colocalization
- `run_hypertension_coloc_batch.sh` -- Hypertension-focused analysis
- `liftover_asthma_afr.sh` -- Coordinate liftover for AFR asthma GWAS

### Stage 2: Genome-Wide Analysis (genome_wide/)

Expands colocalization to all genome-wide significant regions across all
trait pairs (~7,150 pairwise tests via LSF job arrays).

**Key scripts:**
- `harmonize_sumstats.py` -- Harmonize genome-wide GWAS files
- `identify_genomewide_regions.py` -- Extract significant regions from GWAS
- `create_coloc_manifest.py` -- Build ~7K pair-wise coloc manifest
- `run_coloc_genomewide.R` -- Run coloc for each pair
- `submit_genomewide_coloc.sh` -- Master LSF submission template
- `submit_coloc_chunk.sh` -- Chunk-based submission generator
- `aggregate_genomewide_results.py` -- Collect JSON results
- `annotate_genes.py` -- Add gene annotations to signals
- `compare_to_region_analysis.py` -- Cross-validate with region analysis
- `create_genomewide_figures.R` -- Result visualization
- `rerun_failed_jobs.sh` / `monitor_jobs.sh` -- Job management

**Running on an LSF cluster:**
```bash
# 1. Generate manifest
python scripts/create_coloc_manifest.py ...

# 2. Submit jobs
bash scripts/submit_genomewide_coloc.sh

# 3. Monitor progress
bash scripts/monitor_jobs.sh

# 4. Rerun any failures
bash scripts/rerun_failed_jobs.sh

# 5. Aggregate results
python scripts/aggregate_genomewide_results.py ...
```

### Stage 3: ML-Enhanced Analysis (ml/)

Four machine-learning approaches applied to colocalization results.

**Scripts:**
- `recover_coloc_errors.py` -- Impute results for failed colocalization tests
- `characterize_coloc_errors.py` -- Assess bias from failed tests
- `cross_ancestry_prediction.py` -- Validate EUR->AFR signal replication
- `gene_prioritization.py` -- Rank candidate genes using constraint,
  expression, PPI, and druggability features
- `variant_effect_prediction.py` -- Classify regulatory vs coding mechanisms

**Dependencies:** pandas, numpy, scipy, scikit-learn. These scripts consume
outputs from Stages 1 and 2.

```bash
cd ml/
python3 scripts/characterize_coloc_errors.py
python3 scripts/cross_ancestry_prediction.py
python3 scripts/gene_prioritization.py
python3 scripts/variant_effect_prediction.py
```

## Data Requirements (not included)

This package does NOT include raw or processed data. To reproduce the
analysis, you will need:

1. **GWAS summary statistics** from public repositories:
   - GBMI asthma (EUR + AFR)
   - Yengo 2018 BMI (EUR)
   - DIAMANTE 2022 T2D (EUR + TRANS + AFR)
   - Evangelou 2018 blood pressure (EUR)
   - MEGASTROKE/GIGASTROKE stroke (EUR + AFR)

2. **1000 Genomes Phase 3 VCF files** (for LD reference panels)

Download URLs and column mappings are fully specified in
`region_analysis/config/datasets.yaml`. The Snakemake pipeline automates
downloads when run with `--use-conda`.

## Notes

- Both `region_analysis/` and `genome_wide/` contain their own copies of
  `harmonize_sumstats.py` and `run_coloc.R`. These are independent
  implementations tailored to each module's scope.

- Diagnostic/debug scripts, generated chunk submission scripts, compiled
  binaries, and snapshot publication packages were excluded from this
  package as they are not required for reproducibility.
READMEEOF

#----------------------------------------------------------------------
# 10. Create the zip
#----------------------------------------------------------------------
echo "Creating zip archive..."

cd "$PROJECT_ROOT"
zip -r "$ZIP_FILE" "$PACKAGE_NAME"/ -x "*.pyc" "*__pycache__*" "*.DS_Store"

#----------------------------------------------------------------------
# 11. Cleanup staging directory
#----------------------------------------------------------------------
echo "Cleaning up staging directory..."
rm -rf "$STAGING_DIR"

#----------------------------------------------------------------------
# 12. Report
#----------------------------------------------------------------------
echo ""
echo "============================================================"
echo "PACKAGE CREATED SUCCESSFULLY"
echo "============================================================"
echo "File: ${ZIP_FILE}"
echo "Size: $(du -h "$ZIP_FILE" | cut -f1)"
echo "Contents: $(zipinfo -1 "$ZIP_FILE" | wc -l) files"
echo ""
echo "Verify with:  unzip -l ${ZIP_FILE}"
