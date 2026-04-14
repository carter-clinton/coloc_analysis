"""Phase 9 — Replication in Independent Cohorts (production rules).

This file was seeded as a Wave-1 skeleton and progressively filled in by
Plans 09-02 through 09-05. All §F (COJO) and §G (aggregation) rules are
now production-grade; no placeholder recipes remain.

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


def _build_mvp_pha_index():
    """Invert config['cohorts']['mvp_phs001672']['traits'] to a
    pha_id_norm -> (trait, ancestry_key) lookup. Used by harmonize_mvp
    to resolve wildcards at rule evaluation.

    Key normalization: real dbGaP files are named phs001672.phaNNNNNN.txt,
    whereas the config carries versioned IDs like "pha004945.1". The
    lookup strips the '.N' version suffix.
    """
    idx = {}
    mvp = config.get('cohorts', {}).get('mvp_phs001672', {}).get('traits', {})
    for trait, strata in mvp.items():
        if not isinstance(strata, dict):
            continue
        # Skip traits with a top-level status: NOT_RELEASED_*
        if strata.get('status', '').startswith('NOT_RELEASED'):
            continue
        for anc_key, meta in strata.items():
            if not isinstance(meta, dict):
                continue
            pha = meta.get('pha')
            if pha is None:
                continue
            pha_base = str(pha).split('.')[0]
            idx[pha_base] = (trait, anc_key)
    return idx


_MVP_PHA_INDEX = _build_mvp_pha_index()


def _mvp_trait_from_pha(pha_id: str) -> str:
    base = str(pha_id).split('.')[0]
    if base not in _MVP_PHA_INDEX:
        raise ValueError(f"MVP pha_id '{pha_id}' not in config['cohorts']['mvp_phs001672']['traits']")
    return _MVP_PHA_INDEX[base][0]


def _mvp_ancestry_from_pha(pha_id: str) -> str:
    """Return the ancestry stratum key (eur / afr / eas / his / trans /
    eur_sbp / ...). Downstream harmonize_mvp uses this as-is; the panel
    logic in Plan 09-04 will translate stratum keys into canonical
    ancestry codes for the panel assignment."""
    base = str(pha_id).split('.')[0]
    if base not in _MVP_PHA_INDEX:
        raise ValueError(f"MVP pha_id '{pha_id}' not in config['cohorts']['mvp_phs001672']['traits']")
    return _MVP_PHA_INDEX[base][1]

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
    """Download the per-trait GBMI all-ancestry meta file. Per-ancestry
    strata are extracted downstream by harmonize_gbmi via the prefix map
    (see src/python/harmonize_gbmi.py). One download serves all ancestries
    for a trait, so {ancestry} is captured into the filename only as a
    record of intent; the same source URL is used.

    NOTE: The GBMI portal ('https://www.globalbiobankmeta.org/resources')
    serves some files behind a Google Forms gate — if curl 404s the
    operator should manually download and place the file at `{output}`.
    """
    output: "data/raw/replication/gbmi/{trait}_{ancestry}.tsv.gz"
    params:
        portal = lambda wc: config['cohorts']['gbmi']['portal_url'],
    shell:
        # Best-effort automated fetch; portal may require manual download
        # (document caveat in data_access.md).
        "curl -fsSL '{params.portal}/{wildcards.trait}/all_ancestries.tsv.gz' -o {output} || "
        "(echo 'ERROR: GBMI portal download failed — see .planning/data_access.md for manual steps' && exit 1)"

rule download_mvp_phs001672:
    """Fetch a single MVP phs001672 analysis file from the dbGaP FTP.
    The {pha_id} wildcard carries the dbGaP ID (e.g., 'pha004945.1' or
    'pha004945') — downloaded as phs001672.{pha_id}.txt.gz.
    """
    output:
        "data/raw/replication/mvp/{pha_id}.txt.gz"
    params:
        ftp = lambda wc: config['cohorts']['mvp_phs001672']['ftp_root'],
    shell:
        "curl -fsSL '{params.ftp}/phs001672.{wildcards.pha_id}.txt.gz' -o {output}"

rule download_bbj_hum0197_v3:
    """Fetch the NBDC hum0197.v3 zip for a single trait code. BBJ trait
    codes come from config['cohorts']['bbj_hum0197_v3']['traits'] (T2D,
    BMI, As, IS, SBP).
    """
    output:
        "data/raw/replication/bbj/hum0197.v3.BBJ.{trait_code}.v1.zip"
    params:
        base = lambda wc: config['cohorts']['bbj_hum0197_v3']['http_base'],
    shell:
        "curl -fsSL '{params.base}/hum0197.v3.BBJ.{wildcards.trait_code}.v1.zip' -o {output}"

rule extract_bbj_zip:
    """Extract the sumstats TSV payload from a BBJ zip. Skips README.*
    entries. Output filename is normalized to 'sumstats.tsv' so the
    harmonize step has a stable path independent of the zip's internal
    layout.
    """
    input:
        "data/raw/replication/bbj/hum0197.v3.BBJ.{trait_code}.v1.zip"
    output:
        "data/raw/replication/bbj/extracted/{trait_code}/sumstats.tsv"
    run:
        import sys as _sys
        from pathlib import Path as _Path
        _src_py = _Path(workflow.basedir) / "src" / "python"
        if str(_src_py) not in _sys.path:
            _sys.path.insert(0, str(_src_py))
        from harmonize_bbj import extract_bbj_zip as _extract
        _out = _Path(output[0])
        _out.parent.mkdir(parents=True, exist_ok=True)
        _found = _extract(_Path(input[0]), _out.parent)
        if str(_found) != str(_out):
            _found.rename(_out)

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
        tsv = "data/processed/replication/harmonized_grch37/finngen_r12/{trait}_{endpoint}.tsv.gz",
        qc  = "data/processed/replication/harmonized_grch37/finngen_r12/{trait}_{endpoint}.qc.json",
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
    """Extract a per-ancestry stratum from the GBMI all-ancestry meta file
    and rename to the canonical schema. B-2 guard: fails loudly if the
    requested ancestry's prefix columns are absent (no silent empty output).

    Output pattern intentionally mirrors the download step — one harmonized
    file per (trait, ancestry) pair so the panel definitions in
    config['panels'] can refer to them directly.
    """
    input: "data/raw/replication/gbmi/{trait}_{ancestry}.tsv.gz"
    output: "data/processed/replication/harmonized_grch37/gbmi/{trait}_{ancestry}.tsv.gz"
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/harmonize_gbmi.py "
        "--input {input} "
        "--output-prefix data/processed/replication/harmonized_grch37/gbmi/{wildcards.trait} "
        "--trait {wildcards.trait} --ancestry {wildcards.ancestry}"

rule harmonize_mvp:
    """Harmonize an MVP phs001672 analysis file -- dispatches on detected
    schema (dbGaP GWAS-central or REGENIE-style). Phase 9 real data is
    GRCh38 (Wave-1 correction) so --genome-build GRCh38 + chain file.
    """
    input:
        gz = "data/raw/replication/mvp/{pha_id}.txt.gz",
        chain = "data/raw/liftover/hg38ToHg19.over.chain.gz",
    output:
        tsv = "data/processed/replication/harmonized_grch37/mvp/{pha_id}.tsv.gz",
        qc  = "data/processed/replication/harmonized_grch37/mvp/{pha_id}.qc.json",
    params:
        trait = lambda wc: _mvp_trait_from_pha(wc.pha_id),
        ancestry = lambda wc: _mvp_ancestry_from_pha(wc.pha_id),
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/harmonize_mvp.py "
        "--input {input.gz} --output {output.tsv} "
        "--pha-id {wildcards.pha_id} --trait {params.trait} --ancestry {params.ancestry} "
        "--genome-build GRCh38 --chain-file {input.chain} "
        "--qc-out {output.qc}"

rule harmonize_bbj:
    """Harmonize a BBJ hum0197-v3 extracted TSV to canonical schema.
    BBJ is always GRCh38 -> liftover required (chain file dependency).
    """
    input:
        tsv = "data/raw/replication/bbj/extracted/{trait_code}/sumstats.tsv",
        chain = "data/raw/liftover/hg38ToHg19.over.chain.gz",
    output:
        tsv = "data/processed/replication/harmonized_grch37/bbj/{trait}_{trait_code}.tsv.gz",
        qc  = "data/processed/replication/harmonized_grch37/bbj/{trait}_{trait_code}.qc.json",
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/harmonize_bbj.py "
        "--input {input.tsv} --output {output.tsv} --chain-file {input.chain} "
        "--trait {wildcards.trait} --trait-code {wildcards.trait_code} "
        "--qc-out {output.qc}"

# NOTE: The Wave-1 skeleton originally included a standalone
# liftover_replication_sumstats_grch38_to_37 rule. Wave-2 harmonizers apply
# liftover INLINE (each harmonize_* invokes sumstats_utils.liftover_to_grch37
# directly) so the output of harmonize_{finngen,mvp,bbj} is already GRCh37.
# GBMI flagship releases are GRCh37 natively, so no liftover is needed.
# The standalone rule has therefore been removed.

rule validate_harmonized_sumstats:
    """Canonical-schema + liftover-QC gate. Looks up the matching .qc.json
    when present (harmonizers always emit one); FinnGen, MVP, and BBJ all
    produce QC JSON, GBMI produces none (no liftover step)."""
    input:
        tsv = "data/processed/replication/harmonized_grch37/{cohort}/{trait_file}.tsv.gz",
    output:
        touch("data/processed/replication/harmonized_grch37/{cohort}/{trait_file}.validated")
    params:
        qc_path = lambda wc, input: str(input.tsv).replace(".tsv.gz", ".qc.json"),
    conda:
        R_COLOC_ENV
    shell:
        "QC_FLAG=''; "
        "if [ -f '{params.qc_path}' ]; then QC_FLAG='--qc {params.qc_path}'; fi; "
        "python {workflow.basedir}/src/python/validate_replication_sumstats.py "
        "--tsv {input.tsv} $QC_FLAG --max-drop 0.05 && touch {output}"

# ============================================================
# §C. MANIFEST & SUSIE FIT — implemented by Plan 09-03
# ============================================================

def _replication_manifest_path():
    """Canonical replication manifest location."""
    return "data/processed/replication/manifest.tsv"


def _replication_manifest_row(signal_id: str, cohort: str):
    """Resolve a single row from the replication manifest.

    Returns a dict or None if the manifest does not yet exist / id missing.
    Mirrors the Phase-2 `_qtl_coloc_manifest_row` convention.
    """
    import pandas as _pd
    path = _replication_manifest_path()
    if not Path(path).exists():
        return None
    df = _pd.read_csv(path, sep="\t", dtype=str)
    if "signal_id" not in df.columns or "cohort" not in df.columns:
        return None
    sub = df[(df["signal_id"] == signal_id) & (df["cohort"] == cohort)]
    if len(sub) != 1:
        return None
    return sub.iloc[0].to_dict()


def _manifest_lookup(signal_id: str, cohort: str, field: str, default: str = "MISSING"):
    row = _replication_manifest_row(signal_id, cohort)
    if row is None:
        return default
    return row.get(field, default)


rule build_replication_manifest:
    """Build the Phase 9 replication manifest — signal × cohort × ancestry
    crossmap. Consumes Phase 1 credible-set summary + Phase 2 tier
    assignments; emits one row per (signal, cohort) target pair.

    Honors D-02b (Tier C excluded), D-05 (ancestry-matched routing),
    D-05c (BBJ tier_ab_only generalization), D-08 (LD panel routing).
    """
    input:
        credset = "results/fine_mapping/credible_set_summary.tsv",
        tiers   = "results/qtl_coloc/tier_assignments.tsv",
        config  = "config/replication_cohorts.yaml",
        script_dep = "src/python/build_replication_manifest.py",
    output:
        _replication_manifest_path()
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/build_replication_manifest.py "
        "--credset {input.credset} --tiers {input.tiers} "
        "--config {input.config} --out {output}"


rule fit_replication_susie:
    """Re-fit SuSiE-RSS on the replication cohort at a single (signal_id, cohort)
    pair. Reuses Phase-1 config/susie_policy.yaml (D-08 reuse, not fork) and
    per-cohort LD panel routed by manifest.
    """
    input:
        manifest = _replication_manifest_path(),
        policy   = "config/susie_policy.yaml",
        script_dep = "src/snakemake/scripts/run_replication_susie.R",
    output:
        "results/replication/fits/{signal_id}_{cohort}.fit.rds"
    params:
        sumstats = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "replication_sumstats_path"),
        region   = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "region"),
        ld_panel = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "ld_panel"),
    conda:
        R_COLOC_ENV
    shell:
        "Rscript {workflow.basedir}/src/snakemake/scripts/run_replication_susie.R "
        "sumstats={params.sumstats} "
        "region={params.region} "
        "ld_panel={params.ld_panel} "
        "policy={input.policy} "
        "out={output}"

# ============================================================
# §D. COLOC RE-ESTIMATION — implemented by Plan 09-04
# ============================================================
rule run_replication_coloc_susie:
    """Plan 09-04 Task 1 — coloc.susie(disc_fit, rep_fit) re-estimation for a
    single (signal_id × cohort) pair. Emits PP.H4 sweep JSON per D-03b.

    Discovery fit path is resolved from the manifest (not templated from the
    {signal_id} wildcard) because Plan 09-03's manifest-builder encodes the
    full Phase-1 fit layout `{trait}_{ancestry}_{region}.fit.rds` and we
    honor that as the single source of truth (T-09-05 mitigation).
    """
    input:
        disc = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "discovery_fit_path"),
        rep  = "results/replication/fits/{signal_id}_{cohort}.fit.rds",
        script_dep = "src/snakemake/scripts/run_replication_coloc_susie.R",
    output:
        "results/replication/coloc/{signal_id}_{cohort}.coloc.json"
    params:
        thresholds = lambda wc: ",".join(str(t) for t in config.get("pph4_thresholds", [0.5, 0.7, 0.8, 0.9])),
    conda:
        R_COLOC_ENV
    shell:
        "Rscript {workflow.basedir}/src/snakemake/scripts/run_replication_coloc_susie.R "
        "disc={input.disc} rep={input.rep} "
        "signal_id={wildcards.signal_id} cohort={wildcards.cohort} "
        "thresholds={params.thresholds} out={output}"

# ============================================================
# §E. FIQT + META — implemented by Plan 09-04
# ============================================================
rule run_fiqt_on_discovery:
    """Apply FIQT (Bigdeli 2016) winner's-curse correction to discovery β̂.

    Input is a TSV assembled from the Phase-1 credible-set lead SNPs + Phase-2
    Tier A+B triples with columns (rsid, beta, se, n). Output adds beta_FIQT
    and se_FIQT columns; row order follows winnerscurse's descending-|z|
    contract.

    Plan 09-04 Task 2 produces the discovery_signals.tsv input; this rule
    consumes it verbatim. Plan 09-03 makes the wrapper real so 09-04 only
    needs to assemble the signal list.
    """
    input:
        signals = "results/replication/fiqt/discovery_signals.tsv",
        script_dep = "src/snakemake/scripts/run_fiqt.R",
    output:
        "results/replication/fiqt/discovery_beta_fiqt.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "Rscript {workflow.basedir}/src/snakemake/scripts/run_fiqt.R "
        "{input.signals} {output}"

rule collect_replication_effect_sizes:
    """Plan 09-04 Task 2 Step 1b (I-5 revision producer): read the manifest +
    Wave-2 harmonized sumstats for this cohort and emit one (beta, se, p, eaf,
    N) row per signal_id routed to this cohort. Consumed by
    compute_per_cohort_effect_size_test.
    """
    input:
        manifest = _replication_manifest_path(),
        script_dep = "src/python/collect_replication_effect_sizes.py",
    output:
        "results/replication/effect_size_raw/{cohort}.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/collect_replication_effect_sizes.py "
        "--manifest {input.manifest} --cohort {wildcards.cohort} --out {output}"


rule compute_per_cohort_effect_size_test:
    """Plan 09-04 Task 2 — per-cohort Bonferroni + same-direction + post-hoc
    power + joint criterion (D-03a + pitfalls #4, #5). Output is per-cohort
    (one TSV per cohort, not per-signal) to keep the Bonferroni denominator
    computation single-source.
    """
    input:
        effect = "results/replication/effect_size_raw/{cohort}.tsv",
        fiqt   = "results/replication/fiqt/discovery_beta_fiqt.tsv",
        coloc  = "results/replication/coloc/sweep_aggregated_{cohort}.tsv",
        script_dep = "src/python/compute_per_cohort_effect_size_test.py",
    output:
        "results/replication/effect_size/{cohort}.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/compute_per_cohort_effect_size_test.py "
        "--effect {input.effect} --fiqt {input.fiqt} --coloc {input.coloc} "
        "--cohort {wildcards.cohort} --out {output}"


rule ivw_meta_aggregate:
    """Plan 09-04 Task 2 — IVW fixed-effect meta-analysis across ancestry-matched
    replication cohorts per signal (D-06b, T-09-17). Uses metafor::rma.uni(FE).
    Consumes per_cohort_combined.tsv which is a Plan 09-05 Task 2 aggregator
    over the per-cohort tables; that aggregator concatenates the per-cohort
    effect_size/{cohort}.tsv outputs into a single long TSV.
    """
    input:
        per_cohort = "results/replication/effect_size/per_cohort_combined.tsv",
        script_dep = "src/snakemake/scripts/aggregate_replication_meta.R",
    output:
        "results/replication/meta/ivw_meta.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "Rscript {workflow.basedir}/src/snakemake/scripts/aggregate_replication_meta.R "
        "{input.per_cohort} {output}"

# ============================================================
# §F. COJO SENSITIVITY — implemented by Plan 09-05 Task 1
# ============================================================
# Gotcha #1 layer-2 enforcement: the 1000G Phase 3 LD reference (503 EUR /
# 661 AFR samples) is below GCTA's recommended N>=4000 threshold. run_cojo.sh
# emits a WARN stderr at runtime; methods doc embeds the caveat in docs/methods/
# phase9_replication.md (Task 2). Downstream consumers treat COJO as TIER-2
# SENSITIVITY supplementary, NOT primary replication (D-04c + RESEARCH §6 Opt D).

# {ancestry} wildcard = EUR|AFR (matches Broad LDSC 1000G.{EUR|AFR}.QC.{chrom}
# naming). {locus} is the region stub chrN_start_end.
wildcard_constraints:
    ancestry = "EUR|AFR",
    chrom = r"\d+",

rule prepare_cojo_ma:
    """Extract a single locus from the canonical harmonized sumstats and emit
    GCTA .ma (8-column: SNP A1 A2 freq b se p N). Consumed by run_cojo_slct.

    {locus} is derived from the region string chr:start-end as chrN_start_end
    (see build_cojo_sensitivity_table._region_to_filename_stub).
    """
    input:
        sumstats = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "replication_sumstats_path"),
        manifest = _replication_manifest_path(),
        script_dep = "src/snakemake/scripts/prepare_cojo_ma.py",
    output:
        ma = "results/replication/cojo/input/{cohort}_{trait}_{locus}_{signal_id}.ma"
    params:
        region = lambda wc: _manifest_lookup(wc.signal_id, wc.cohort, "region"),
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/snakemake/scripts/prepare_cojo_ma.py "
        "--sumstats {input.sumstats} --region {params.region} --out {output.ma}"

rule run_cojo_slct:
    """GCTA 1.94.1 --cojo-slct wrapper at a single (cohort, trait, locus) with
    1000G Phase 3 {EUR|AFR} LD reference. Consumes the LDSC download flag
    (download_ldsc_baseline in pathway.smk) to guarantee PLINK files exist.

    Flag file path `data/reference/ldsc/.baseline_download_done` is the
    touched output of pathway.smk rule `download_ldsc_baseline` (RO7 DAG
    wiring convention).
    """
    input:
        ma = "results/replication/cojo/input/{cohort}_{trait}_{locus}_{signal_id}.ma",
        plink_bed = "data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{ancestry}.QC.{chrom}.bed",
        plink_done = "data/reference/ldsc/.baseline_download_done",
        snp_list = "results/replication/cojo/input/{cohort}_{trait}_{locus}_{signal_id}.snps",
        script_dep = "src/snakemake/scripts/run_cojo.sh",
    output:
        jma = "results/replication/cojo/{cohort}_{trait}_{locus}_{signal_id}_{ancestry}_{chrom}.jma.cojo"
    params:
        plink_prefix = lambda wc, input: input.plink_bed[:-4],  # strip '.bed'
        out_prefix = lambda wc, output: output.jma[:-len(".jma.cojo")],
    conda:
        GCTA_ENV
    shell:
        "bash {workflow.basedir}/src/snakemake/scripts/run_cojo.sh "
        "{input.ma} {params.plink_prefix} {input.snp_list} {params.out_prefix}"

# ============================================================
# §G. AGGREGATION — implemented by Plan 09-05 Task 2
# ============================================================
# Produces the four D-07 output artifacts consumed by Phase 11 manuscript
# figures + supplementary tables. Pipeline terminus: `all_replication`.

rule aggregate_per_cohort_combined:
    """Concatenate per-cohort effect_size/{cohort}.tsv into a single long
    TSV consumed by IVW meta (aggregate_replication_meta.R) and by the
    leave-one-cohort-out hold-out (build_replication_holdout.py).

    The cohort list is pulled from config['panels'] (EUR + AFR + BBJ EAS
    for completeness; downstream IVW excludes is_generalization=TRUE
    rows per T-09-17).
    """
    input:
        lambda wc: [
            f"results/replication/effect_size/{cohort}.tsv"
            for cohort in config.get("panels", {}).get("all_replication_cohorts", [
                "finngen_r12", "gbmi_eur", "gbmi_afr",
                "mvp_eur", "mvp_afr", "bbj",
            ])
        ]
    output:
        "results/replication/effect_size/per_cohort_combined.tsv"
    run:
        import pandas as _pd
        frames = []
        for p in input:
            try:
                frames.append(_pd.read_csv(p, sep="\t"))
            except (_pd.errors.EmptyDataError, FileNotFoundError):
                continue
        if frames:
            combined = _pd.concat(frames, ignore_index=True, sort=False)
        else:
            combined = _pd.DataFrame(columns=[
                "signal_id", "cohort", "cohort_ancestry",
                "beta_replication", "se_replication",
            ])
        combined.to_csv(output[0], sep="\t", index=False)

rule assemble_master_replication_table:
    """Assemble the canonical replication matrix per RESEARCH §16.

    Merges: manifest + FIQT discovery corrections + per-cohort effect/coloc
    + IVW meta (I-2: merge on (signal_id, discovery_ancestry)). Emits
    per-cohort sample_overlap_flag columns (I-3) + low_maf_founder_flag.
    """
    input:
        manifest = _replication_manifest_path(),
        fiqt = "results/replication/fiqt/discovery_beta_fiqt.tsv",
        meta = "results/replication/meta/ivw_meta.tsv",
        coloc_dir_flag = "results/replication/coloc",  # directory marker
        per_cohort_finngen = "results/replication/effect_size/finngen_r12.tsv",
        per_cohort_gbmi_eur = "results/replication/effect_size/gbmi_eur.tsv",
        per_cohort_gbmi_afr = "results/replication/effect_size/gbmi_afr.tsv",
        per_cohort_mvp_eur = "results/replication/effect_size/mvp_eur.tsv",
        per_cohort_mvp_afr = "results/replication/effect_size/mvp_afr.tsv",
        script_dep = "src/python/build_master_replication_table.py",
    output:
        "results/replication/master_table.tsv"
    params:
        per_cohort_dir = "results/replication/effect_size",
        coloc_dir = "results/replication/coloc",
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/build_master_replication_table.py "
        "--manifest {input.manifest} --fiqt {input.fiqt} "
        "--per-cohort-dir {params.per_cohort_dir} --coloc-dir {params.coloc_dir} "
        "--meta {input.meta} --out {output}"

rule assemble_cross_ancestry_generalization_bbj:
    """Assemble the Tier A+B × BBJ-EAS cross-ancestry generalization panel
    per D-05c. No credible_set_SNP rows. is_generalization=True always.
    """
    input:
        manifest = _replication_manifest_path(),
        bbj = "results/replication/effect_size/bbj.tsv",
        script_dep = "src/python/build_cross_ancestry_panel.py",
    output:
        "results/replication/cross_ancestry_generalization_tier_ab.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/build_cross_ancestry_panel.py "
        "--manifest {input.manifest} --bbj-cohort {input.bbj} --out {output}"

rule assemble_cojo_sensitivity_supplementary:
    """Aggregate all .jma.cojo outputs across (signal × cohort) into the
    cojo_sensitivity.tsv supplementary table (D-04c). Missing / skipped loci
    are silently omitted — COJO is TIER-2 SENSITIVITY, not a hard gate.
    """
    input:
        manifest = _replication_manifest_path(),
        script_dep = "src/python/build_cojo_sensitivity_table.py",
    output:
        "results/replication/cojo_sensitivity.tsv"
    params:
        cojo_dir = "results/replication/cojo",
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/build_cojo_sensitivity_table.py "
        "--cojo-dir {params.cojo_dir} --manifest {input.manifest} --out {output}"

rule assemble_replication_holdout_supplementary:
    """Leave-one-cohort-out IVW meta per signal (RESEARCH §16 recommendation).
    Complements the primary IVW meta with a jack-knife sensitivity that
    surfaces cohort-driven outlier effects.
    """
    input:
        per_cohort = "results/replication/effect_size/per_cohort_combined.tsv",
        script_dep = "src/python/build_replication_holdout.py",
    output:
        "results/replication/replication_holdout_supplementary.tsv"
    conda:
        R_COLOC_ENV
    shell:
        "python {workflow.basedir}/src/python/build_replication_holdout.py "
        "--per-cohort {input.per_cohort} --out {output}"

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
