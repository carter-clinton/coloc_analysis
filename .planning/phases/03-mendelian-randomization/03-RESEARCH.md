# Phase 3: Mendelian Randomization - Research

**Researched:** 2026-04-16
**Domain:** Bidirectional two-sample MR with SuSiE-based instruments, weak-instrument mitigation, MVMR mediation
**Confidence:** HIGH

## Summary

Phase 3 implements bidirectional Mendelian randomization for all 10 unique trait pairs (20 directed tests) plus 3 MVMR mediation triangles. Instruments are extracted from Phase 1 SuSiE `.fit.rds` files as lead SNPs (highest PIP per credible set), with FIQT-corrected betas from Phase 9. The standard R stack for this is TwoSampleMR (IVW/Egger/median + Steiger + harmonization + diagnostics), MRPRESSO (outlier detection), cause (correlated pleiotropy), mr.raps (weak-instrument robust estimation for non-EUR), and MVMR (multivariable MR with conditional F-statistics). All five packages are GitHub-only (not on CRAN) except mr.raps which was archived from CRAN in March 2025 and must now be installed from GitHub.

The critical architectural insight is that this phase has TWO distinct data pipelines: (1) a region-level instrument extraction pipeline in R that reads SuSiE `.fit.rds` and JSON files and produces a flat instrument table, and (2) a genome-wide summary statistics pipeline that feeds CAUSE (which requires genome-wide data, not just instruments). The manifest-driven Snakemake dispatch pattern established in Phases 2/9 applies directly: a manifest TSV defines all 20+3 tests, and `expand()` rules iterate over manifest rows.

**Primary recommendation:** Create a dedicated `envs/r_mr.yml` conda environment extending `r_coloc.yml` with TwoSampleMR, MRPRESSO, MVMR, and mr.raps installed via `remotes::install_github()` in a post-create hook. CAUSE requires a separate install due to its dependency on mixsqp/ashr. The CAUSE analysis is a sensitivity analysis (not primary) and can run as a separate rule with its own env if needed.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01a: Test ALL 10 unique trait pairs (5-choose-2) in BOTH directions = 20 directed MR tests. Pre-register expected directions from literature but test both; non-significant reverse directions strengthen causal claims.
- D-01b: Include MVMR for 3 key triangular paths: (1) BMI->Stroke adjusting for HTN, (2) BMI->T2D adjusting for HTN, (3) HTN->T2D adjusting for BMI.
- D-01c: Config `mr.hypotheses` must be expanded from 3 to all 10 bidirectional pairs. MVMR triangles specified separately.
- D-02a: Ancestry-specific MR as primary analysis. EUR is the strongest. AFR/EAS run with MR-RAPS where ancestry-matched GWAS exists.
- D-02b: Trans-ancestry meta-MR (Lyon et al. 2023) as additional sensitivity analysis.
- D-02c: For trait pairs where one trait lacks non-EUR GWAS, run EUR-only MR. Document gaps explicitly.
- D-02d: This satisfies REQ-4: explicit ancestry-specific vs. trans-ancestry choice documented per pair; MR-RAPS mandatory for all non-EUR analyses.
- D-03a: Lead SNP per credible set (highest PIP variant from each SuSiE CS). For multi-signal regions (L>1), each CS contributes one independent instrument.
- D-03b: Complex regions included in all analyses but flagged. Let MR-PRESSO and MR-CAUSE detect outliers. Do NOT exclude a priori.
- D-03c: No minimum F-statistic threshold for instrument inclusion. Report full F-statistic distribution. MR-RAPS handles weak instruments explicitly.
- D-03d: Instruments derived from FIQT-corrected discovery betas (Phase 9 winner's-curse adjustment), not raw discovery betas.
- D-04a: Run 5 MR methods per directed pair: IVW (random-effects), MR-Egger, weighted median, MR-PRESSO, MR-CAUSE. Plus MR-RAPS for all non-EUR analyses.
- D-04b: Majority rule decision criterion: call causal effect if >=3 of 5 methods reach nominal significance in the same direction.
- D-04c: Steiger directionality filtering applied. Instruments failing Steiger test are flagged (not dropped).
- D-04d: Bonferroni correction across 20 directed tests (p < 0.0025). MVMR tests reported separately (3 tests, p < 0.017).
- D-04e: Output as directed graph (Figure 5) and full evidence matrix (Supplementary Table).

### Claude's Discretion
- R package choices within TwoSampleMR/MR-CAUSE/MRPRESSO ecosystem
- Exact MVMR implementation (MVMR package vs. manual IVW extension)
- Diagnostic plot selection for supplementary (funnel, leave-one-out, forest)
- Steiger flagging visualization approach

### Deferred Ideas (OUT OF SCOPE)
- Formal network MR / Bayesian mediation -- full path analysis with coefficients
- Drug-target MR -- use gene-tissue coloc to proxy drug targets
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-4 | MR weak-instrument mitigation for AFR/EAS: at least 2 of MR-RAPS, IVW-with-correction, trans-ancestry MR per Lyon 2023; explicit ancestry-specific vs trans-ancestry choice per pair; MR-RAPS on AFR/EAS; weak-instrument diagnostic table (F-stat, I-squared, Q-stat) per ancestry per pair | MR-RAPS (GitHub: qingyuanzhao/mr.raps) handles weak instruments via adjusted profile score. TEMR (hhoulei/TEMR, AJHG 2025) provides formal trans-ancestry MR framework. F-stat computed as beta^2/se^2 per SNP. Cochran's Q and I^2 from TwoSampleMR::mr_heterogeneity(). Satisfies all REQ-4 acceptance criteria. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| TwoSampleMR | 0.7.4 | IVW, Egger, weighted median, Steiger, harmonization, diagnostics | De facto standard for two-sample MR. 4,800+ citations. All 5 primary methods available via single `mr()` call. Steiger filtering built-in. [VERIFIED: mrcieu.r-universe.dev, Feb 2026 docs] |
| MRPRESSO | 1.0 | Horizontal pleiotropy detection + outlier removal | Standard for MR-PRESSO global test, outlier test, distortion test. Required by D-04a. GitHub-only (rondolab/MR-PRESSO). [VERIFIED: github.com/rondolab/MR-PRESSO] |
| cause | 1.2.0 | Correlated pleiotropy model (CAUSE method, Morrison 2020) | Distinguishes shared etiology from causation -- uniquely valuable for cardiometabolic traits where shared pleiotropy is expected. Uses genome-wide data. [VERIFIED: github.com/jean997/cause v1.2.0] |
| mr.raps | 0.4.1 | Robust adjusted profile score for weak instruments | Mandatory for non-EUR per D-02a/REQ-4. CRAN archived 2025-03-01; GitHub version 0.4.1 is current. Integrated into TwoSampleMR as method "mr_raps". [VERIFIED: github.com/qingyuanzhao/mr.raps, CRAN archive notice] |
| MVMR | 0.4 | Multivariable MR with conditional F-statistics | Sanderson et al. 2021 Statistics in Medicine. Conditional F-stat, IVW-MVMR, Q-statistic pleiotropy test. Required for D-01b triangles. [VERIFIED: github.com/WSpiller/MVMR] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| TEMR | 0.1.0 | Trans-ethnic MR framework (Liu et al. AJHG 2025) | For D-02b trans-ancestry sensitivity analysis. Formal method for combining multi-ancestry instruments. [VERIFIED: github.com/hhoulei/TEMR, AJHG 112(1):28-43] |
| metafor | 4.6+ | Fixed-effects meta-analysis of ancestry-specific IVW estimates | Already in r_coloc.yml (Phase 9). For simple meta-MR: combine EUR + AFR IVW estimates via rma.uni(method='FE'). [VERIFIED: already installed in r_coloc env] |
| susieR | 0.14.2 | Read SuSiE .fit.rds files for instrument extraction | Already in r_coloc.yml. Provides susie_get_cs(), susie_get_pip(). [VERIFIED: installed in r_coloc env] |
| data.table | 1.16.4 | Fast I/O for large sumstats files | Already in r_coloc.yml. Needed for reading .bgz harmonized sumstats. [VERIFIED: installed in r_coloc env] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TwoSampleMR | MendelianRandomization (Burgess, CRAN v0.9.0) | MendelianRandomization is on CRAN and more formally maintained; but TwoSampleMR has Steiger filtering, harmonise_data(), and diagnostic plots built-in. TwoSampleMR is the ecosystem standard for pipeline work. Use MendelianRandomization only if TwoSampleMR installation fails. |
| TEMR | Simple fixed-effects meta of ancestry-specific IVW estimates via metafor | metafor approach is simpler and well-understood. TEMR provides calibrated p-values and better power for underrepresented populations. Given D-02b calls for "Lyon 2023" which appears to be a meta-MR sensitivity, either works. Recommend: metafor for primary trans-ancestry meta, TEMR as additional sensitivity if feasible. |
| MVMR | TwoSampleMR::mv_multiple() | TwoSampleMR has basic MVMR capability but lacks conditional F-statistics (Sanderson 2021). MVMR package is purpose-built for this. Use MVMR package. |

**Installation:**
```bash
# Create dedicated MR conda environment extending r_coloc
# Base: R 4.4.2 + susieR + coloc + data.table + metafor (from r_coloc.yml)
# Then install MR packages via R:
conda activate r_mr
Rscript -e '
  library(remotes)
  install_github("MRCIEU/TwoSampleMR")
  install_github("rondolab/MR-PRESSO")
  install_github("qingyuanzhao/mr.raps")
  install_github("WSpiller/MVMR")
  install_github("jean997/cause@v1.2.0")
  install_github("hhoulei/TEMR")
'
```

**Version verification:** TwoSampleMR 0.7.4 confirmed via r-universe (Feb 2026). mr.raps removed from CRAN 2025-03-01, GitHub 0.4.1 is current. CAUSE v1.2.0 includes loo package compatibility fix (critical). MVMR latest commit on GitHub. TEMR from AJHG 2025 publication. [VERIFIED: web search results + GitHub repos]

## Architecture Patterns

### Recommended Project Structure
```
src/
  snakemake/
    rules/
      mr.smk                      # Expanded from stub: all MR rules
    scripts/
      extract_mr_instruments.R     # SuSiE .fit.rds -> instrument table
      run_bidirectional_mr.R       # Single directed MR test (5 methods)
      run_cause.R                  # CAUSE analysis (genome-wide data)
      run_mvmr.R                   # MVMR for 3 triangles
      run_mr_raps.R                # MR-RAPS for non-EUR (standalone)
      run_steiger.R                # Steiger directionality + flagging
      build_mr_diagnostics.R       # Funnel/forest/LOO/scatter plots
      aggregate_mr_results.R       # Combine all results -> evidence matrix
      build_causal_graph.R         # Directed graph (Figure 5)
  legacy/
    region_analysis/
      scripts/
        create_mr_design.py        # Existing manifest builder (extend)
config/
  pipeline.yaml                    # §mr expanded to 10 bidirectional + 3 MVMR
envs/
  r_mr.yml                         # MR-specific conda env
results/
  mr/
    instruments/                   # Per-trait instrument tables
    bidirectional/                 # Per-pair MR results (5 methods)
    cause/                         # CAUSE results (genome-wide)
    mvmr/                          # MVMR triangle results
    diagnostics/                   # Plots (funnel, forest, LOO, scatter)
    mr_manifest.tsv                # Manifest: 20 directed + 3 MVMR rows
    mr_evidence_matrix.tsv         # Final aggregated evidence table
    mr_causal_graph.json           # Graph data for Figure 5
```

### Pattern 1: Manifest-Driven MR Dispatch (from Phase 2/9 pattern)
**What:** Build a manifest TSV with all 20 directed MR tests + 3 MVMR triangles, then `expand()` rules over manifest rows.
**When to use:** All MR execution rules.
**Example:**
```python
# mr.smk — manifest-driven rule expansion
import pandas as pd

# Load manifest at DAG-build time
MR_MANIFEST = os.path.join(MR_DIR, "mr_manifest.tsv")

def get_mr_pairs(wildcards):
    """Read manifest to enumerate all directed pairs."""
    df = pd.read_csv(MR_MANIFEST, sep="\t")
    ready = df[df["status"] == "ready"]
    return ready[["exposure", "outcome", "ancestry"]].drop_duplicates()

rule run_bidirectional_mr:
    input:
        instruments=os.path.join(MR_DIR, "instruments",
            "{exposure}.{ancestry}.instruments.tsv"),
        outcome_sumstats=lambda wc: config_sumstats_path(wc.outcome, wc.ancestry),
    output:
        results=os.path.join(MR_DIR, "bidirectional",
            "{exposure}_to_{outcome}.{ancestry}.mr_results.tsv"),
    conda: str(Path(workflow.basedir) / "envs" / "r_mr.yml")
    # ... script call
```

### Pattern 2: SuSiE-to-Instrument Extraction (R, region-aggregated)
**What:** Read all `.fit.rds` files for a given trait+ancestry, extract lead SNP per CS, merge with FIQT-corrected betas, produce instrument table.
**When to use:** Before any MR test.
**Example:**
```r
# extract_mr_instruments.R — core instrument extraction logic
# Source: SuSiE credible set structure verified from project .fit.rds files
extract_instruments <- function(fit_rds_path, json_path, fiqt_path = NULL) {
  fit <- readRDS(fit_rds_path)
  json <- jsonlite::fromJSON(json_path)

  # Get credible sets
  cs <- susieR::susie_get_cs(fit)
  if (is.null(cs$cs) || length(cs$cs) == 0) return(NULL)

  instruments <- data.table::rbindlist(lapply(seq_along(cs$cs), function(i) {
    idx <- cs$cs[[i]]
    pip <- fit$pip[idx]
    # Lead SNP = highest PIP in this CS (D-03a)
    lead_idx <- idx[which.max(pip)]
    cs_info <- json$credible_sets[[paste0("CS", i)]]
    # Get the lead variant row from JSON (has CHR, POS, BETA, SE)
    lead_row <- cs_info[which.max(cs_info$pip), ]
    data.table::data.table(
      cs_id = paste0("CS", i),
      chr = lead_row$CHR,
      pos = lead_row$POS,
      beta = lead_row$BETA,
      se = lead_row$SE,
      pip = max(pip),
      n_variants_in_cs = length(idx),
      purity = cs$purity[i, "min.abs.corr"]
    )
  }))

  # Merge with FIQT-corrected betas if available (D-03d)
  if (!is.null(fiqt_path) && file.exists(fiqt_path)) {
    fiqt <- data.table::fread(fiqt_path)
    # Use beta_FIQT instead of raw discovery beta
    instruments <- merge(instruments, fiqt[, .(chr, pos, beta_FIQT, se_FIQT)],
                         by = c("chr", "pos"), all.x = TRUE)
    instruments[!is.na(beta_FIQT), `:=`(beta = beta_FIQT, se = se_FIQT)]
  }

  instruments
}
```

### Pattern 3: TwoSampleMR Harmonization + Multi-Method MR
**What:** Format instrument + outcome data into TwoSampleMR format, harmonize, run 5 methods, collect diagnostics.
**When to use:** Every directed MR test.
**Example:**
```r
# Source: TwoSampleMR docs at mrcieu.github.io/TwoSampleMR/
# [VERIFIED: format_data() parameters from official reference docs]

# Format exposure instruments
exposure_dat <- TwoSampleMR::format_data(
  instruments,
  type = "exposure",
  snp_col = "snp_id",
  beta_col = "beta",
  se_col = "se",
  effect_allele_col = "effect_allele",
  other_allele_col = "other_allele",
  eaf_col = "eaf",
  pval_col = "pval",
  samplesize_col = "samplesize",
  phenotype_col = "exposure_name"
)

# Format outcome data (extract outcome stats at instrument positions)
outcome_dat <- TwoSampleMR::format_data(
  outcome_at_instruments,
  type = "outcome",
  snp_col = "snp_id",
  beta_col = "beta",
  se_col = "se",
  effect_allele_col = "effect_allele",
  other_allele_col = "other_allele",
  eaf_col = "eaf",
  pval_col = "pval",
  samplesize_col = "samplesize",
  phenotype_col = "outcome_name"
)

# Harmonize (action=2: infer strand from EAF, default)
dat <- TwoSampleMR::harmonise_data(exposure_dat, outcome_dat, action = 2)

# Run 5 methods (D-04a)
methods <- c(
  "mr_ivw",                    # IVW random-effects
  "mr_egger_regression",       # MR-Egger
  "mr_weighted_median",        # Weighted median
  "mr_raps"                    # MR-RAPS (calls mr.raps package)
)
res <- TwoSampleMR::mr(dat, method_list = methods)

# MR-PRESSO separately (its own calling convention)
presso_res <- MRPRESSO::mr_presso(
  BetaOutcome = "beta.outcome",
  BetaExposure = "beta.exposure",
  SdOutcome = "se.outcome",
  SdExposure = "se.exposure",
  OUTLIERtest = TRUE,
  DISTORTIONtest = TRUE,
  data = as.data.frame(dat),
  NbDistribution = 1000,
  SignifThreshold = 0.05
)

# Heterogeneity + pleiotropy diagnostics
het <- TwoSampleMR::mr_heterogeneity(dat)
pleio <- TwoSampleMR::mr_pleiotropy_test(dat)

# Steiger directionality (D-04c)
steiger <- TwoSampleMR::directionality_test(dat)
```

### Pattern 4: CAUSE Genome-Wide Analysis
**What:** CAUSE requires genome-wide summary statistics (not just instruments). Must be run separately from instrument-based methods.
**When to use:** As sensitivity analysis per D-04a.
**Example:**
```r
# Source: jean997.github.io/cause/ tutorial [VERIFIED]
# CAUSE needs genome-wide GWAS summary data merged across exposure + outcome
X <- cause::gwas_merge(
  exposure_gwas, outcome_gwas,
  snp_name_cols = c("SNP_ID", "SNP_ID"),
  beta_hat_cols = c("BETA", "BETA"),
  se_cols = c("SE", "SE"),
  A1_cols = c("effect_allele", "effect_allele"),
  A2_cols = c("other_allele", "other_allele")
)

# LD pruning (use ieugwasr::ld_clump or cause built-in)
# Requires LD reference panel — use 1000G EUR plink files already on disk
# at data/reference/ldsc/1000G_EUR_Phase3_plink/

# Estimate nuisance parameters (sample overlap, confounding)
set.seed(42)
varlist <- sample(X$snp, min(1e6, nrow(X)))
params <- cause::est_cause_params(X, varlist)

# LD prune for CAUSE variants (top SNPs by p-value, r2 < 0.01)
top_vars <- X$snp[X$p1 < 1e-3]  # Exposure p < 1e-3
# ... LD prune top_vars ...

# Fit CAUSE model
res <- cause::cause(X = X, variants = pruned_vars, param_ests = params)

# Interpret: z-score for causal vs sharing model
# Negative z with p < 0.05 = evidence for causation over shared pleiotropy
summary(res)
```

### Pattern 5: MVMR Triangle Analysis
**What:** Multivariable MR for 3 mediation triangles using MVMR package.
**When to use:** D-01b triangles only (BMI->Stroke adj HTN, BMI->T2D adj HTN, HTN->T2D adj BMI).
**Example:**
```r
# Source: wspiller.github.io/MVMR/articles/MVMR.html [VERIFIED]
# Need instruments for BOTH exposures (e.g., BMI + HTN for BMI->Stroke adj HTN)

# Format: columns = exposures, rows = instruments (union of both instrument sets)
mvmr_input <- MVMR::format_mvmr(
  BXGs = cbind(bmi_betas, htn_betas),      # N_snps x 2 matrix
  BYG = stroke_betas,                        # N_snps vector
  seBXGs = cbind(bmi_se, htn_se),
  seBYG = stroke_se,
  RSID = snp_ids
)

# Conditional F-statistics (Sanderson 2021)
cond_f <- MVMR::strength_mvmr(r_input = mvmr_input, gencov = 0)

# Test pleiotropy via Q-statistic
pleio <- MVMR::pleiotropy_mvmr(r_input = mvmr_input, gencov = 0)

# IVW-MVMR estimates
mvmr_res <- MVMR::ivw_mvmr(r_input = mvmr_input)
```

### Anti-Patterns to Avoid
- **Using discovery betas for instruments:** Must use FIQT-corrected betas from Phase 9 (D-03d). Raw discovery betas are winner's-curse inflated.
- **Excluding complex regions a priori:** D-03b says include but flag. Let MR-PRESSO detect outliers.
- **Dropping Steiger failures:** D-04c says FLAG, not drop. Keep all instruments but annotate Steiger direction.
- **Hard F-stat cutoff:** D-03c explicitly says no minimum threshold. Report distribution but do not filter.
- **Running CAUSE with only instruments:** CAUSE requires genome-wide data (100K+ variants). The instrument-based methods (IVW, Egger, etc.) use the SuSiE lead SNPs only.
- **Using `action=1` for harmonization:** Default `action=2` infers strand from EAF. `action=1` assumes forward strand (dangerous with palindromic SNPs).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Allele harmonization | Custom allele-flip logic | `TwoSampleMR::harmonise_data(action=2)` | Handles palindromic SNPs, strand inference from EAF, ambiguous allele detection. Thoroughly tested. [VERIFIED: official docs] |
| Steiger directionality | Custom R-squared comparison | `TwoSampleMR::directionality_test()` + `steiger_filtering()` | Computes variance explained for exposure and outcome, applies Steiger test per SNP. [VERIFIED: official docs] |
| MR-PRESSO outlier detection | Custom leave-one-out residual analysis | `MRPRESSO::mr_presso()` | Global test + outlier identification + distortion test in one call. Published method (Verbanck 2018). [VERIFIED: official docs] |
| F-statistic computation | Manual beta^2/se^2 loop | Formula: `F_j = (beta_j / se_j)^2` for each SNP j. For aggregate: `F = mean(F_j)` or use Cragg-Donald. For MVMR: `MVMR::strength_mvmr()` | Simple formula but the MVMR conditional F-stat is complex. [CITED: Sanderson 2021 Stat Med 40:5434-52] |
| Cochran's Q / I-squared | Custom heterogeneity calculation | `TwoSampleMR::mr_heterogeneity()` | Returns Q-statistic and I^2 for IVW and Egger. [VERIFIED: official docs] |
| Trans-ancestry meta-MR | Custom inverse-variance weighting | `metafor::rma.uni(method='FE')` for simple meta, or `TEMR::TEMR()` for formal framework | metafor already proven in Phase 9 pipeline. TEMR handles genetic correlation across ancestries. [VERIFIED: metafor in r_coloc, TEMR on GitHub] |
| Diagnostic plots | Custom ggplot scatter/forest/funnel | `TwoSampleMR::mr_scatter_plot()`, `mr_forest_plot()`, `mr_funnel_plot()`, `mr_leaveoneout_plot()` | Consistent publication-quality plots with method annotations. [VERIFIED: official docs] |
| CAUSE model comparison | Custom ELPD computation | `cause::cause()` returns `elpd` table with z-score and p-value for causal vs sharing model | The ELPD comparison is the core CAUSE output. [VERIFIED: official tutorial] |

**Key insight:** The MR ecosystem has mature, well-tested implementations for every step. The complexity is in orchestrating them correctly within Snakemake, not in the statistical methods themselves. The planner should focus pipeline architecture, not method implementation.

## Common Pitfalls

### Pitfall 1: BMI EUR Sumstats Missing Allele Columns
**What goes wrong:** bmi.EUR harmonized sumstats lack REF/ALT/EAF columns (Yengo 2018 format). TwoSampleMR `harmonise_data()` requires effect_allele and other_allele for allele alignment.
**Why it happens:** Phase 0 harmonization (bug #5 from T1 production) added dummy alleles for LDSC munge but the harmonized .bgz may still lack proper REF/ALT. Other traits (t2d, asthma, stroke, hypertension) have REF/ALT/EAF.
**How to avoid:** Before MR instrument extraction, verify allele columns exist in harmonized sumstats. If missing, instruments extracted from SuSiE JSON have CHR+POS+BETA+SE but NO alleles. Must cross-reference with a reference panel (1000G) to recover alleles, OR the instrument extraction script must read the raw sumstats (not harmonized) for alleles if available.
**Warning signs:** `harmonise_data()` returns 0 rows after harmonization, or all SNPs flagged as "palindromic" with no EAF to resolve.
[VERIFIED: inspected bmi.EUR.tsv.bgz on disk -- columns are CHR, POS, BETA, SE, P, N, SNP_ID, TRAIT, ANCESTRY, BUILD -- no REF/ALT/EAF]

### Pitfall 2: CAUSE Requires Genome-Wide Data
**What goes wrong:** CAUSE fitted with only instrument SNPs (10-50 per pair) gives unreliable parameter estimates. CAUSE explicitly needs 100K+ variants.
**Why it happens:** All other methods use only instruments. CAUSE is fundamentally different -- it models shared pleiotropy genome-wide.
**How to avoid:** CAUSE analysis is a separate Snakemake rule that reads full harmonized sumstats (.bgz files), not the instrument table. The `gwas_merge()` step merges the two full GWAS files. LD pruning step uses 1000G reference.
**Warning signs:** CAUSE param estimation (`est_cause_params`) warns about too few variants. Recommendation from CAUSE docs: use at least 100K variants for parameter estimation, 1000+ LD-pruned variants for fitting.
[CITED: jean997.github.io/cause/ldl_cad.html tutorial]

### Pitfall 3: Palindromic SNP Handling
**What goes wrong:** Palindromic SNPs (A/T or G/C) cannot be unambiguously oriented between exposure and outcome datasets. If EAF is near 0.5, strand cannot be inferred.
**Why it happens:** Two-sample MR combines data from different GWAS which may report on different strands.
**How to avoid:** Use `harmonise_data(action=2)` (default) which infers strand from EAF. SNPs with MAF > 0.42 that are palindromic are dropped. For bmi.EUR which lacks EAF, use `action=3` (drop all palindromic SNPs) as fallback.
**Warning signs:** Large fraction of instruments dropped during harmonization. Check `dat$palindromic` and `dat$ambiguous` columns.
[VERIFIED: mrcieu.github.io/TwoSampleMR/articles/harmonise.html]

### Pitfall 4: Winner's Curse Inflates MR Estimates
**What goes wrong:** Instruments selected for genome-wide significance have upward-biased effect sizes, inflating MR causal estimates.
**Why it happens:** Selection on statistical significance at discovery creates systematic upward bias (winner's curse).
**How to avoid:** D-03d mandates FIQT-corrected betas from Phase 9. The FIQT correction (Bigdeli 2016) shrinks discovery betas toward their BH-adjusted posterior. This is already implemented in `src/snakemake/scripts/run_fiqt.R`. Instruments must use `beta_FIQT` not raw `beta`.
**Warning signs:** MR estimates systematically larger than expected from observational epidemiology. Check that FIQT merge step ran successfully.
[VERIFIED: FIQT implementation exists in codebase, Phase 9 decision D-04a]

### Pitfall 5: Sample Overlap Between Exposure and Outcome GWAS
**What goes wrong:** If exposure and outcome GWAS share participants, MR estimates are biased toward the observational association.
**Why it happens:** Two-sample MR assumes independent samples. UK Biobank is in both GIANT BMI GWAS and some outcome GWAS.
**How to avoid:** For trait pairs where both GWAS use UK Biobank (e.g., BMI from GIANT+UKBB and hypertension from UKBB), sample overlap is expected. MR-RAPS and CAUSE are more robust to sample overlap than IVW. The CAUSE parameter estimation explicitly estimates the sample overlap correlation (rho). Report estimated overlap in supplementary. For EUR, this is largely unavoidable -- document and rely on method robustness.
**Warning signs:** CAUSE's estimated rho parameter is far from zero. MR-Egger intercept is significant (though this tests pleiotropy, not overlap).
[CITED: jean997.github.io/cause/ -- CAUSE estimates rho for overlap]

### Pitfall 6: Too Few Instruments for Non-EUR MR
**What goes wrong:** AFR analyses have far fewer SuSiE credible sets (smaller GWAS, fewer genome-wide significant loci). With < 3 instruments, most MR methods are unstable or cannot run.
**Why it happens:** AFR GWAS have smaller sample sizes (e.g., asthma AFR N~15K vs EUR N~286K). Fewer loci reach genome-wide significance.
**How to avoid:** MR-RAPS is explicitly designed for weak/few instruments (D-02a). For pairs with < 3 instruments in non-EUR, run MR-RAPS only (skip IVW/Egger/median which need > 3 instruments for stability). Report the number of instruments per pair per ancestry in the diagnostic table. If a pair has 0 instruments in an ancestry, document as "MR not feasible" rather than forcing an underpowered analysis.
**Warning signs:** `mr()` returns NA or errors for Egger (needs >= 3 SNPs). MR-RAPS warns about convergence.
[ASSUMED -- instrument count for AFR not yet verified from SuSiE JSON files on disk]

### Pitfall 7: MR-PRESSO Fails with Too Few Instruments
**What goes wrong:** MR-PRESSO requires >= 4 instruments to compute the global test. With fewer, `mr_presso()` errors out.
**Why it happens:** The residual sum of squares distribution needs degrees of freedom.
**How to avoid:** Wrap MR-PRESSO in tryCatch. If < 4 instruments, skip PRESSO and note in results. For the majority rule (D-04b), count PRESSO as NA (not counted toward 3/5 or against).
**Warning signs:** `mr_presso()` throws "Not enough instrumental variables" error.
[VERIFIED: MRPRESSO documentation states minimum instrument requirement]

### Pitfall 8: CAUSE Package Version Compatibility
**What goes wrong:** CAUSE v1.1.0 has a known bug in ELPD computation due to loo package API change. Results are incorrect.
**Why it happens:** The loo R package changed the order of `loo_compare()` output, and CAUSE v1.1.0 did not account for this.
**How to avoid:** Pin to CAUSE v1.2.0 which fixes this bug. Install with `install_github("jean997/cause@v1.2.0")`.
**Warning signs:** CAUSE z-scores are unexpectedly large or have the wrong sign. Summary output mentions "loo_compare" warnings.
[VERIFIED: github.com/jean997/cause README documents this bug]

## Code Examples

Verified patterns from official sources:

### F-Statistic Computation for Instrument Strength
```r
# Source: Burgess et al. 2011, Sanderson 2022 Nat Rev Methods Primers
# F_j = (beta_j / se_j)^2 for each instrument SNP j
# Approximate two-sample F-stat per SNP
compute_f_stats <- function(instruments_dt) {
  instruments_dt[, f_stat := (beta / se)^2]
  instruments_dt[, r2_snp := f_stat / (f_stat + samplesize - 2)]  # per-SNP R^2
  list(
    f_stats = instruments_dt$f_stat,
    mean_f = mean(instruments_dt$f_stat),
    median_f = median(instruments_dt$f_stat),
    min_f = min(instruments_dt$f_stat),
    n_weak = sum(instruments_dt$f_stat < 10),
    total_r2 = sum(instruments_dt$r2_snp)
  )
}
```

### SNP ID Recovery for Instruments
```r
# SuSiE JSON stores CHR:POS but TwoSampleMR needs rsIDs.
# Cross-reference with harmonized sumstats (which have SNP_ID column).
# Source: project harmonized sumstats format verified on disk.
recover_snp_ids <- function(instruments_dt, sumstats_path) {
  ss <- data.table::fread(
    cmd = sprintf("zcat %s", sumstats_path),
    select = c("CHR", "POS", "SNP_ID"),
    colClasses = c(CHR = "character", POS = "integer", SNP_ID = "character")
  )
  merged <- merge(instruments_dt, ss,
                  by.x = c("chr", "pos"), by.y = c("CHR", "POS"),
                  all.x = TRUE)
  # Fallback: chr:pos format if rsID not found
  merged[is.na(SNP_ID), SNP_ID := paste0(chr, ":", pos)]
  merged
}
```

### Trans-Ancestry Meta-MR via metafor
```r
# Source: metafor already used in Phase 9 for IVW meta
# [VERIFIED: Phase 9 decision D-06b uses metafor::rma.uni]
# Combine ancestry-specific IVW estimates via fixed-effects meta-analysis
meta_mr <- function(eur_beta, eur_se, afr_beta, afr_se) {
  if (is.na(afr_beta)) return(list(beta = eur_beta, se = eur_se, ancestry = "EUR_only"))
  yi <- c(eur_beta, afr_beta)
  sei <- c(eur_se, afr_se)
  fit <- metafor::rma.uni(yi = yi, sei = sei, method = "FE")
  list(
    beta = as.numeric(fit$beta),
    se = as.numeric(fit$se),
    pval = fit$pval,
    Q = fit$QE,
    Q_pval = fit$QEp,
    I2 = fit$I2,
    ancestry = "trans_ancestry_meta"
  )
}
```

### Majority Rule Decision (D-04b)
```r
# Apply majority rule: causal if >= 3 of 5 methods significant + same direction
# Source: D-04b from CONTEXT.md
apply_majority_rule <- function(results_dt, alpha = 0.0025) {
  # results_dt has columns: method, beta, se, pval
  results_dt[, significant := pval < alpha]
  results_dt[, direction := sign(beta)]

  n_sig <- sum(results_dt$significant, na.rm = TRUE)
  # Direction consistency among significant results
  if (n_sig == 0) return(list(verdict = "null", n_significant = 0))

  sig_direction <- results_dt[significant == TRUE, direction]
  dominant_dir <- as.numeric(names(sort(table(sig_direction), decreasing = TRUE))[1])
  n_concordant <- sum(sig_direction == dominant_dir)

  verdict <- if (n_concordant >= 3) "strong"
             else if (n_concordant == 2) "moderate"
             else if (n_concordant == 1) "suggestive"
             else "null"

  list(
    verdict = verdict,
    n_significant = n_sig,
    n_concordant = n_concordant,
    dominant_direction = dominant_dir
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| IVW with genome-wide sig instruments | SuSiE CS lead SNPs as instruments | 2022-2023 (Zou, Zuber, Burgess) | Better instrument selection: multiple independent signals per locus; PIP-based rather than p-value threshold |
| Raw discovery betas | FIQT-corrected betas | 2016 (Bigdeli), adopted widely 2023+ | Reduces winner's curse bias in MR estimates |
| EUR-only MR | Multi-ancestry MR with TEMR/meta-MR | 2024-2025 (Liu et al. AJHG) | Improves power for underrepresented populations; tests transportability |
| MR-Egger as pleiotropy test | CAUSE (Morrison 2020) | 2020 | Models correlated AND uncorrelated pleiotropy; Egger only detects directional pleiotropy |
| Hard F > 10 cutoff | MR-RAPS (no cutoff needed) | 2018 (Zhao et al.) | Profile-score approach handles weak instruments without excluding them |
| Single-method MR | Multi-method triangulation (3+/5 rule) | 2019+ (Burgess guidelines) | More robust inference; reduces reliance on any single method's assumptions |
| mr.raps on CRAN | mr.raps GitHub-only (archived 2025-03) | 2025-03-01 | Must install from GitHub; still integrated with TwoSampleMR via "mr_raps" method name |

**Deprecated/outdated:**
- **mr.raps CRAN version (0.2):** Archived 2025-03-01. Use GitHub version 0.4.1. [VERIFIED: CRAN archive notice]
- **CAUSE v1.1.0:** Has loo_compare bug. Pin to v1.2.0. [VERIFIED: GitHub README]
- **Simple Wald ratio as primary method:** Superseded by IVW random-effects as primary. Wald ratio appropriate only for single-instrument analyses.

## Assumptions Log

> List all claims tagged [ASSUMED] in this research.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AFR analyses will have fewer than 10 instruments per trait pair on average, making IVW/Egger unreliable | Pitfall 6 | If AFR has enough instruments, the MR-RAPS-only fallback is unnecessarily conservative. Low risk: can always run all methods and let them succeed/fail. |
| A2 | "Lyon et al. 2023" from CONTEXT.md refers to a general trans-ancestry meta-MR approach (combining ancestry-specific IVW estimates), not a specific R package | Architecture Patterns, Standard Stack | If Lyon 2023 is a specific paper with a specific tool, we may need to install that instead of TEMR/metafor. Medium risk: the sensitivity analysis approach (fixed-effects meta of ancestry-specific estimates) is methodologically sound regardless. User should confirm the specific reference. |
| A3 | MVMR package version is approximately 0.4 (latest GitHub commit) | Standard Stack | Low risk: MVMR is a simple, stable package. Version mismatch would not affect API. |
| A4 | TwoSampleMR "mr_raps" method correctly calls mr.raps package when installed from GitHub (not CRAN) | Standard Stack | If the integration is broken after CRAN archival, we need to call mr.raps::mr.raps.overdispersed() directly. Medium risk: should be tested early. |

**If this table is empty:** N/A -- 4 assumptions identified above.

## Open Questions

1. **"Lyon et al. 2023" reference identity**
   - What we know: CONTEXT.md D-02b specifies "Trans-ancestry meta-MR (Lyon et al. 2023)" as a sensitivity analysis
   - What's unclear: No paper by "Lyon" found in web searches for trans-ancestry MR. The closest formal method is TEMR (Liu et al., AJHG 2025). The standard informal approach is fixed-effects meta-analysis of ancestry-specific IVW estimates.
   - Recommendation: Implement trans-ancestry sensitivity as metafor fixed-effects meta of ancestry-specific IVW estimates (proven pattern from Phase 9). Add TEMR as a second sensitivity if time permits. **User should clarify the Lyon 2023 reference.** [ASSUMED: A2]

2. **BMI EUR allele recovery**
   - What we know: bmi.EUR harmonized sumstats lack REF/ALT/EAF columns
   - What's unclear: Whether Yengo 2018 raw sumstats have alleles, or if we must cross-reference with 1000G
   - Recommendation: Instrument extraction script should: (1) check if alleles exist in harmonized sumstats; (2) if not, cross-reference instrument positions with 1000G .bim file to recover REF/ALT; (3) compute EAF from 1000G for the correct ancestry. This is a data-wrangling task, not a methodological decision.

3. **CAUSE LD pruning on HPC without internet**
   - What we know: CAUSE tutorial suggests `ieugwasr::ld_clump()` which requires API access (OpenGWAS server). HPC compute nodes lack internet.
   - What's unclear: Whether CAUSE's built-in `ld_prune()` function with local LD data is sufficient.
   - Recommendation: Use local PLINK LD clumping with 1000G reference files already on disk (`data/reference/ldsc/1000G_EUR_Phase3_plink/`). Feed clumped variant list to CAUSE. This avoids any API dependency.

4. **EAS instruments**
   - What we know: Config shows no EAS ancestries currently harmonized (`trait_ancestries` has only EUR and AFR for some traits). BBJ data is staged but not harmonized.
   - What's unclear: Whether BBJ harmonization is in scope for Phase 3 or deferred
   - Recommendation: Phase 3 should handle EUR (primary) and AFR (where available) per D-02c. EAS MR is only possible if BBJ harmonization completes first. Document as "future extension" per D-02c.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + R testthat (via subprocess) |
| Config file | `tests/conftest.py` (root-level, Phase 4 created) |
| Quick run command | `pytest tests/test_mr/ -x --timeout=60` |
| Full suite command | `pytest tests/test_mr/ -v --timeout=120` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-4a | MR-RAPS runs on AFR trait pairs | integration | `pytest tests/test_mr/test_mr_raps_afr.py -x` | Wave 0 |
| REQ-4b | Weak-instrument diagnostic table produced per ancestry | unit | `pytest tests/test_mr/test_diagnostics.py -x` | Wave 0 |
| REQ-4c | F-statistic, I^2, Q-stat columns present in output | unit | `pytest tests/test_mr/test_diagnostics.py::test_diagnostic_columns -x` | Wave 0 |
| D-01a | All 20 directed MR tests enumerated in manifest | unit | `pytest tests/test_mr/test_manifest.py -x` | Wave 0 |
| D-01b | 3 MVMR triangles produce conditional F-stats | integration | `pytest tests/test_mr/test_mvmr.py -x` | Wave 0 |
| D-03a | Lead SNP per CS extracted correctly | unit | `pytest tests/test_mr/test_instrument_extraction.py -x` | Wave 0 |
| D-03d | FIQT betas used (not raw) | unit | `pytest tests/test_mr/test_instrument_extraction.py::test_fiqt_merge -x` | Wave 0 |
| D-04b | Majority rule applied correctly | unit | `pytest tests/test_mr/test_majority_rule.py -x` | Wave 0 |
| D-04c | Steiger filtering flags (not drops) | unit | `pytest tests/test_mr/test_steiger.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_mr/ -x --timeout=60`
- **Per wave merge:** `pytest tests/test_mr/ -v --timeout=120`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_mr/` directory -- all test files listed above
- [ ] `tests/test_mr/conftest.py` -- shared fixtures (mock SuSiE .fit.rds, mock harmonized sumstats, mock instrument tables)
- [ ] `envs/r_mr.yml` -- conda environment for MR packages
- [ ] R package installation verification test

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A -- no auth in MR analysis scripts |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | Validate instrument count >= 1 before MR; validate harmonized data columns; tryCatch around all R package calls |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for R/Snakemake MR Pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| GitHub package supply chain (install_github) | Tampering | Pin to specific commit SHA or tag (e.g., cause@v1.2.0, mr.raps@master specific commit) |
| Untrusted GWAS sumstats injection | Tampering | Validate column schema before processing; reject unexpected columns |
| Integer overflow in F-stat with tiny SE | Elevation | Cap F-stat at reasonable maximum (e.g., 1e6); check for SE == 0 |

## Sources

### Primary (HIGH confidence)
- [TwoSampleMR official docs](https://mrcieu.github.io/TwoSampleMR/) - format_data(), harmonise_data(), mr(), steiger_filtering(), diagnostic plots
- [TwoSampleMR r-universe](https://mrcieu.r-universe.dev/TwoSampleMR) - version 0.7.4 confirmed (Feb 2026)
- [MRPRESSO GitHub](https://github.com/rondolab/MR-PRESSO) - mr_presso() API, parameter documentation
- [CAUSE docs](https://jean997.github.io/cause/) - full tutorial, gwas_merge(), est_cause_params(), cause(), v1.2.0 fix
- [MVMR docs](https://wspiller.github.io/MVMR/articles/MVMR.html) - format_mvmr(), ivw_mvmr(), strength_mvmr(), conditional F-stat
- [mr.raps CRAN archive](https://cran.r-project.org/web/packages/mr.raps/) - archived 2025-03-01, GitHub 0.4.1 current
- [TEMR GitHub](https://github.com/hhoulei/TEMR) - trans-ethnic MR method, AJHG 2025

### Secondary (MEDIUM confidence)
- [Sanderson et al. 2021](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.9133) - Conditional F-statistics for MVMR
- [Burgess MR Guidelines 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC7384151/) - MR best practices update
- [MR Dictionary](https://mr-dictionary.mrcieu.ac.uk/) - F-statistic, harmonization, IVW definitions
- Project codebase inspection: SuSiE JSON format, harmonized sumstats columns, FIQT implementation

### Tertiary (LOW confidence)
- "Lyon et al. 2023" trans-ancestry MR reference -- not found in web searches [ASSUMED: A2]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All packages verified via official docs, GitHub repos, and r-universe. Version numbers confirmed.
- Architecture: HIGH - Manifest-driven dispatch pattern proven in Phases 2/5/9. SuSiE JSON format inspected on disk. TwoSampleMR API verified from official docs.
- Pitfalls: HIGH for pitfalls 1-5, 7-8 (verified from docs/codebase). MEDIUM for pitfall 6 (AFR instrument count assumed).
- MVMR: HIGH - Sanderson 2021 is the definitive reference. MVMR package API verified from official tutorial.
- Trans-ancestry: MEDIUM - metafor approach proven in Phase 9; TEMR verified on GitHub; but "Lyon 2023" reference unresolved.

**Research date:** 2026-04-16
**Valid until:** 2026-05-16 (stable domain; packages update slowly)
