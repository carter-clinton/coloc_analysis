"""Phase 9 — Replication in Independent Cohorts (skeleton rules).

This file is a SKELETON. Every rule in it is a placeholder whose recipe
is `echo 'TODO plan 09-0X' && touch {output}` so the DAG resolves cleanly
while downstream plans 09-02 through 09-05 fill in real implementations.

Structure mirrors RESEARCH §17 (A through G):

    §A Cohort ingest               (Plan 09-02)
    §B Harmonization               (Plan 09-02)
    §C Manifest + SuSiE fit        (Plan 09-03)
    §D Coloc re-estimation         (Plan 09-04)
    §E FIQT + per-cohort + meta    (Plan 09-04)
    §F COJO sensitivity            (Plan 09-05)
    §G Aggregation (master table)  (Plan 09-05)

The config file `config/replication_cohorts.yaml` is loaded additively so
this skeleton can be exercised via `snakemake --list` without disturbing
the main config/pipeline.yaml already loaded by the top-level Snakefile.

Path conventions:
  - envs/ lookups use `Path(workflow.basedir) / "envs" / ...` because
    `workflow.basedir` is the directory of the including Snakefile
    (i.e., project root). This matches ld_reference.smk.
  - config lookup uses the same `Path(workflow.basedir)` base.
"""
from pathlib import Path

# Load the Phase 9 cohort registry additively onto the main config.
# `configfile:` directives only accept string literals, so use a relative
# path anchored at project root (same convention as the top-level
# Snakefile's `configfile: "config/pipeline.yaml"`).
configfile: "config/replication_cohorts.yaml"

# Top-level results directory (fall back if main config absent).
REPLICATION_ROOT = Path(config.get("paths", {}).get("results_root", "results")) / "replication"

# Env files — project-root relative via workflow.basedir.
GCTA_ENV = str(Path(workflow.basedir) / "envs" / "gcta.yml")
R_COLOC_ENV = str(Path(workflow.basedir) / "envs" / "r_coloc.yml")

# ============================================================
# §A. COHORT INGEST — implemented by Plan 09-02
# ============================================================
rule download_finngen_r12:
    """Fetch FinnGen R12 per-endpoint sumstats + tabix index from the
    public GCS HTTP mirror. URL shape:
        {http_mirror}/finngen_R12_{endpoint}.gz[.tbi]
    """
    output:
        gz = "data/raw/replication/finngen_r12/finngen_R12_{endpoint}.gz",
        tbi = "data/raw/replication/finngen_r12/finngen_R12_{endpoint}.gz.tbi",
    params:
        url = lambda wc: f"{config['cohorts']['finngen_r12']['http_mirror']}/finngen_R12_{wc.endpoint}.gz"
    shell:
        "curl -fsSL {params.url} -o {output.gz} && "
        "curl -fsSL {params.url}.tbi -o {output.tbi}"

rule download_gbmi:
    output:
        touch("data/raw/replication/gbmi/{trait}_{ancestry}.downloaded")
    shell:
        "echo 'TODO plan 09-02 Task 2 — download GBMI {wildcards.trait}/{wildcards.ancestry}' && touch {output}"

rule download_mvp_phs001672:
    output:
        touch("data/raw/replication/mvp/{pha_id}.downloaded")
    shell:
        "echo 'TODO plan 09-02 Task 3 — download MVP {wildcards.pha_id}' && touch {output}"

rule download_bbj_hum0197_v3:
    output:
        touch("data/raw/replication/bbj/{trait_code}.zip.downloaded")
    shell:
        "echo 'TODO plan 09-02 Task 4 — download BBJ {wildcards.trait_code}' && touch {output}"

rule extract_bbj_zip:
    input:
        "data/raw/replication/bbj/{trait_code}.zip.downloaded"
    output:
        touch("data/raw/replication/bbj/{trait_code}.extracted")
    shell:
        "echo 'TODO plan 09-02 Task 4 — extract BBJ zip for {wildcards.trait_code}' && touch {output}"

# ============================================================
# §B. HARMONIZATION — implemented by Plan 09-02
# ============================================================
rule harmonize_finngen:
    """Rename FinnGen R12 raw schema to canonical, liftover GRCh38->37,
    and drop palindromic ambiguous SNPs (RESEARCH pitfalls #1 + #2)."""
    input:
        gz = "data/raw/replication/finngen_r12/finngen_R12_{endpoint}.gz",
        chain = "data/raw/liftover/hg38ToHg19.over.chain.gz",
    output:
        tsv = "data/processed/replication/harmonized/finngen_r12/{trait}_{endpoint}.tsv.gz",
        qc  = "data/processed/replication/harmonized/finngen_r12/{trait}_{endpoint}.qc.json",
    params:
        case_n = lambda wc: config['cohorts']['finngen_r12']['traits'][wc.trait]['case_n'],
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/harmonize_finngen.py "
        "--input {input.gz} --output {output.tsv} "
        "--chain-file {input.chain} --trait {wildcards.trait} "
        "--case-n {params.case_n} --qc-out {output.qc}"

rule harmonize_gbmi:
    input:
        "data/raw/replication/gbmi/{trait}_{ancestry}.downloaded"
    output:
        touch("data/processed/replication/harmonized/gbmi/{trait}_{ancestry}.tsv.gz")
    shell:
        "echo 'TODO plan 09-02 — harmonize GBMI {wildcards.trait}/{wildcards.ancestry}' && touch {output}"

rule harmonize_mvp:
    input:
        "data/raw/replication/mvp/{pha_id}.downloaded"
    output:
        touch("data/processed/replication/harmonized/mvp/{pha_id}.tsv.gz")
    shell:
        "echo 'TODO plan 09-02 — harmonize MVP {wildcards.pha_id}' && touch {output}"

rule harmonize_bbj:
    input:
        "data/raw/replication/bbj/{trait_code}.extracted"
    output:
        touch("data/processed/replication/harmonized/bbj/{trait_code}.tsv.gz")
    shell:
        "echo 'TODO plan 09-02 — harmonize BBJ {wildcards.trait_code}' && touch {output}"

rule liftover_replication_sumstats_grch38_to_37:
    input:
        "data/processed/replication/harmonized/{cohort}/{trait_file}.tsv.gz"
    output:
        touch("data/processed/replication/harmonized_grch37/{cohort}/{trait_file}.tsv.gz")
    shell:
        "echo 'TODO plan 09-02 — liftover {wildcards.cohort}/{wildcards.trait_file} GRCh38→GRCh37' && touch {output}"

rule validate_harmonized_sumstats:
    input:
        "data/processed/replication/harmonized_grch37/{cohort}/{trait_file}.tsv.gz"
    output:
        touch("data/processed/replication/harmonized_grch37/{cohort}/{trait_file}.validated")
    shell:
        "echo 'TODO plan 09-02 — validate harmonized sumstats {wildcards.cohort}/{wildcards.trait_file}' && touch {output}"

# ============================================================
# §C. MANIFEST & SUSIE FIT — implemented by Plan 09-03
# ============================================================
rule build_replication_manifest:
    output:
        touch("data/processed/replication/manifest.tsv")
    shell:
        "echo 'TODO plan 09-03 Task 1 — build replication manifest' && touch {output}"

rule fit_replication_susie:
    input:
        manifest="data/processed/replication/manifest.tsv"
    output:
        touch("results/replication/fits/{signal_id}_{cohort}.fit.rds")
    shell:
        "echo 'TODO plan 09-03 Task 2 — fit SuSiE for {wildcards.signal_id}/{wildcards.cohort}' && touch {output}"

# ============================================================
# §D. COLOC RE-ESTIMATION — implemented by Plan 09-04
# ============================================================
rule run_replication_coloc_susie:
    input:
        disc="results/fine_mapping/{signal_id}.fit.rds",
        rep="results/replication/fits/{signal_id}_{cohort}.fit.rds"
    output:
        touch("results/replication/coloc/{signal_id}_{cohort}.coloc.json")
    shell:
        "echo 'TODO plan 09-04 Task 1 — coloc.susie {wildcards.signal_id}/{wildcards.cohort}' && touch {output}"

# ============================================================
# §E. FIQT + META — implemented by Plan 09-04
# ============================================================
rule run_fiqt_on_discovery:
    output:
        touch("results/replication/fiqt/discovery_beta_fiqt.tsv")
    shell:
        "echo 'TODO plan 09-04 Task 2 — FIQT on discovery betas' && touch {output}"

rule compute_per_cohort_effect_size_test:
    input:
        fiqt="results/replication/fiqt/discovery_beta_fiqt.tsv"
    output:
        touch("results/replication/effect_size/{signal_id}_{cohort}.tsv")
    shell:
        "echo 'TODO plan 09-04 — per-cohort effect-size test {wildcards.signal_id}/{wildcards.cohort}' && touch {output}"

rule ivw_meta_aggregate:
    output:
        touch("results/replication/meta/{signal_id}_{ancestry}.meta.tsv")
    shell:
        "echo 'TODO plan 09-04 Task 3 — IVW meta {wildcards.signal_id}/{wildcards.ancestry}' && touch {output}"

# ============================================================
# §F. COJO SENSITIVITY — implemented by Plan 09-05
# ============================================================
rule prepare_cojo_ma:
    output:
        touch("results/replication/cojo/input/{cohort}_{trait}_{locus}.ma")
    shell:
        "echo 'TODO plan 09-05 Task 1 — prepare COJO .ma for {wildcards.cohort}/{wildcards.trait}/{wildcards.locus}' && touch {output}"

rule run_cojo_slct:
    input:
        ma="results/replication/cojo/input/{cohort}_{trait}_{locus}.ma"
    output:
        touch("results/replication/cojo/{cohort}_{trait}_{locus}.cojo.tsv")
    conda:
        GCTA_ENV
    shell:
        "echo 'TODO plan 09-05 Task 1 — run gcta --cojo-slct {wildcards.cohort}/{wildcards.trait}/{wildcards.locus}' && touch {output}"

# ============================================================
# §G. AGGREGATION — implemented by Plan 09-05
# ============================================================
rule assemble_master_replication_table:
    output:
        touch("results/replication/master_table.tsv")
    shell:
        "echo 'TODO plan 09-05 Task 2 — assemble master replication table' && touch {output}"

rule assemble_cross_ancestry_generalization_bbj:
    output:
        touch("results/replication/cross_ancestry_generalization_tier_ab.tsv")
    shell:
        "echo 'TODO plan 09-05 Task 2 — assemble BBJ cross-ancestry generalization (tier A/B only)' && touch {output}"

rule assemble_cojo_sensitivity_supplementary:
    output:
        touch("results/replication/cojo_sensitivity.tsv")
    shell:
        "echo 'TODO plan 09-05 Task 2 — assemble COJO sensitivity supplementary' && touch {output}"

rule assemble_replication_holdout_supplementary:
    output:
        touch("results/replication/replication_holdout_supplementary.tsv")
    shell:
        "echo 'TODO plan 09-05 Task 2 — assemble replication hold-out supplementary' && touch {output}"

# ============================================================
# Top-level aggregate target (Plan 09-05 final)
# ============================================================
rule all_replication:
    input:
        "results/replication/master_table.tsv",
        "results/replication/cross_ancestry_generalization_tier_ab.tsv",
        "results/replication/cojo_sensitivity.tsv",
        "results/replication/replication_holdout_supplementary.tsv"
    output:
        touch("results/replication/.all_replication.done")
