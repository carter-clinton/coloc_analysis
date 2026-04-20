"""Top-level Snakefile for coloc_analysis pipeline.

Imports all modular rules from src/snakemake/rules/.
All paths are parameterized via config/pipeline.yaml (D-08, D-09).
No hardcoded absolute paths (REQ-12).
"""

import os
import csv
import yaml

# ---------------------------------------------------------------------------
# Config loading and validation (D-06, D-08)
# ---------------------------------------------------------------------------
configfile: "config/pipeline.yaml"

from snakemake.utils import validate
validate(config, "src/snakemake/schemas/pipeline.schema.yaml")

# Also load datasets config (with schema validation)
with open("config/datasets.yaml") as _dsfh:
    DATASETS_CONFIG = yaml.safe_load(_dsfh)
validate(DATASETS_CONFIG, "src/snakemake/schemas/datasets.schema.yaml")

# ---------------------------------------------------------------------------
# Global variables derived from config
# ---------------------------------------------------------------------------
TRAITS = config["traits"]
ANCESTRIES = config["ancestries"]
TRAIT_ANCESTRIES = config.get("trait_ancestries", {})

HARMONIZED_DIR = config["paths"]["harmonized_sumstats"]

# Build trait-ancestry pairs from trait_ancestries mapping
TRAIT_ANCESTRY_PAIRS = []
for _trait in TRAITS:
    _ancestries = TRAIT_ANCESTRIES.get(_trait, ANCESTRIES)
    for _anc in _ancestries:
        TRAIT_ANCESTRY_PAIRS.append((_trait, _anc))

# ---------------------------------------------------------------------------
# Load curated regions from config path (not hardcoded)
# ---------------------------------------------------------------------------
REGION_INFOS = []
REGION_SAFE_TO_ID = {}
REGION_METADATA = {}
with open(config["paths"]["regions_curated"], newline="") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        orig = row["region_id"]
        safe = orig.replace(".", "_").replace("/", "_")
        suffix = 1
        while safe in REGION_SAFE_TO_ID:
            suffix += 1
            safe = f"{safe}_{suffix}"
        start = int(float(row["start"]))
        end = int(float(row["end"]))
        chrom = row["chr"].replace("chr", "").replace("CHR", "")
        REGION_INFOS.append((orig, safe))
        REGION_SAFE_TO_ID[safe] = orig
        REGION_METADATA[safe] = {"chr": chrom, "start": start, "end": end}

REGION_SAFE_IDS = [safe for _, safe in REGION_INFOS]

# ---------------------------------------------------------------------------
# Build target lists using config paths (no hardcoded paths)
# ---------------------------------------------------------------------------
HARMONIZED_ALL = [
    os.path.join(HARMONIZED_DIR, f"{trait}.{ancestry}.tsv.bgz")
    for trait, ancestry in TRAIT_ANCESTRY_PAIRS
]

FINEMAP_CONFIG = config.get("finemap", {})
FINEMAP_METHODS = FINEMAP_CONFIG.get("methods", [])
FINEMAP_DIR = FINEMAP_CONFIG.get(
    "output_dir",
    os.path.join(config["paths"]["results_root"], "fine_mapping"),
)

if FINEMAP_METHODS:
    FINEMAP_MANIFEST = os.path.join(FINEMAP_DIR, "finemap_manifest.tsv")
    UNIQUE_TRAIT_ANC = sorted(set(TRAIT_ANCESTRY_PAIRS))
    FINEMAP_OUTPUTS = [
        os.path.join(FINEMAP_DIR, method, f"{trait}.{ancestry}.{region_safe}.json")
        for method in FINEMAP_METHODS
        for trait, ancestry in UNIQUE_TRAIT_ANC
        for _, region_safe in REGION_INFOS
    ]
    FINEMAP_SUMMARY = os.path.join(FINEMAP_DIR, "finemap_summary.tsv")
    FINEMAP_FILTERED_TARGETS = [
        os.path.join(FINEMAP_DIR, "finemap_summary_augmented.tsv"),
        os.path.join(FINEMAP_DIR, "finemap_tier1_high_conf.tsv"),
        os.path.join(FINEMAP_DIR, "finemap_tier2_relaxed.tsv"),
        os.path.join(FINEMAP_DIR, "finemap_tier3_coloc.tsv"),
    ]
else:
    FINEMAP_MANIFEST = None
    FINEMAP_OUTPUTS = []
    FINEMAP_SUMMARY = None
    FINEMAP_FILTERED_TARGETS = []

# ---------------------------------------------------------------------------
# Include refactored rules from src/snakemake/rules/ (D-05)
# ---------------------------------------------------------------------------
include: "src/snakemake/rules/sumstats.smk"
include: "src/snakemake/rules/regions.smk"
include: "src/snakemake/rules/qc.smk"
include: "src/snakemake/rules/multitrait.smk"
include: "src/snakemake/rules/pgs.smk"
include: "src/snakemake/rules/mr.smk"

if FINEMAP_METHODS:
    include: "src/snakemake/rules/finemap.smk"
    # coloc.smk must follow finemap.smk because run_coloc_susie consumes
    # .fit.rds outputs from run_finemap (Phase 1 Wave 4, REQ-2 #4).
    include: "src/snakemake/rules/coloc.smk"

# Phase 2 QTL coloc rules. qtl_download.smk defines QTL_RAW_DIR and
# QTL_HARMONIZED_DIR; qtl_coloc.smk uses those plus finemap_output() from
# finemap.smk. Order: download -> coloc (coloc uses _qtl_manifest_field
# and QTL_HARMONIZED_DIR from download).
include: "src/snakemake/rules/qtl_download.smk"
include: "src/snakemake/rules/qtl_coloc.smk"
include: "src/snakemake/rules/negative_controls.smk"

# Phase 5 pathway + partitioned heritability rules. Depends on config.pathway
# section; download rules populate reference data, analysis rules consume
# outputs from Phase 2 QTL coloc and Phase 1 fine-mapping.
include: "src/snakemake/rules/pathway.smk"

# Phase 9 — replication cohorts (FinnGen R12, MVP phs001672, BBJ hum0197-v3,
# GBMI). Skeleton rules with TODO placeholders; implementations added by
# Plans 09-02 through 09-05.
include: "src/snakemake/rules/replication.smk"

# Phase 4 — matched-N cross-ancestry concordance (EUR-AFR bootstrap +
# LDSC r_g matrix + Table 2). Skeleton rules with manifest generation;
# implementations added by Plans 04-02 through 04-05.
include: "src/snakemake/rules/matched_n.smk"

ENABLE_LD = config.get("enable_ld_pipeline", False)
# Only generate LD targets for ancestries that (a) appear in at least one
# active trait_ancestry pair AND (b) have a 1000G population mapping.
# This prevents the DAG from requesting EAS/HIS LD matrices before those
# ancestries have harmonized sumstats on disk.
_USED_ANCESTRIES = sorted(set(anc for _, anc in TRAIT_ANCESTRY_PAIRS))
LD_ANCESTRIES = [a for a in _USED_ANCESTRIES if a in config.get("onekg", {}).get("populations", {})]
# Only generate LD targets for regions whose chromosome has a 1000G VCF
ONEKG_CHROMS = set(config.get("onekg", {}).get("chromosomes", []))
LD_REGION_INFOS = [(orig, safe) for orig, safe in REGION_INFOS if REGION_METADATA[safe]["chr"] in ONEKG_CHROMS]
if ENABLE_LD:
    include: "src/snakemake/rules/ld_reference.smk"
    LD_TARGETS = [
        os.path.join(
            config["paths"]["ld_reference"],
            ancestry,
            f"{region_safe}.rds",
        )
        for ancestry in LD_ANCESTRIES
        for _, region_safe in LD_REGION_INFOS
    ]
else:
    LD_TARGETS = []

# ---------------------------------------------------------------------------
# Build master target list
# ---------------------------------------------------------------------------
RESULTS_ROOT = config["paths"]["results_root"]

ALL_TARGETS = (
    HARMONIZED_ALL
    + [config["paths"]["regions_bed"]]
    + LD_TARGETS
    + FINEMAP_OUTPUTS
    + ([FINEMAP_MANIFEST] if FINEMAP_MANIFEST else [])
    + ([FINEMAP_SUMMARY] if FINEMAP_SUMMARY else [])
    + FINEMAP_FILTERED_TARGETS
    + [
        os.path.join(RESULTS_ROOT, "multitrait", "harmonized_manifest.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "coloc_manifest.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "coloc_summary.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "coloc_summary_augmented.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "hyprcoloc_manifest.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "hyprcoloc_summary.tsv"),
        os.path.join(RESULTS_ROOT, "pgs", "pgs_manifest.tsv"),
        os.path.join(RESULTS_ROOT, "mr", "mr_manifest.tsv"),
        os.path.join(RESULTS_ROOT, "qc", "harmonized_summary.tsv"),
        os.path.join(RESULTS_ROOT, "qc", "region_overlap.tsv"),
        os.path.join(RESULTS_ROOT, "qc", "region_trait_qc.tsv"),
        os.path.join(RESULTS_ROOT, "multitrait", "placeholder.done"),
        os.path.join(RESULTS_ROOT, "pgs", "placeholder.done"),
        os.path.join(RESULTS_ROOT, "mr", "placeholder.done"),
    ]
)

rule all:
    input:
        ALL_TARGETS


# Phase 2 QTL coloc explicit opt-in target. QTL_COLOC_OUTPUTS is defined at
# parse time inside src/snakemake/rules/qtl_coloc.smk (included above at
# line 123), so it is a module-level global by the time this rule resolves.
#
# Phase 2 is intentionally NOT wired into ALL_TARGETS: CP#1-final memo
# (.planning/checkpoints/T1_review_final_draft.md line 72) specifies that
# Phase 2 fires as a separate named target from Launch10-15 pathway runs.
# Invoke via: snakemake -s Snakefile all_qtl_coloc
rule all_qtl_coloc:
    input:
        QTL_COLOC_OUTPUTS
