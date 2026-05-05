---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 1
slug: W1-sh2b3-psd-regularized-refit
type: execute
wave: 1
depends_on: []
files_modified:
  - src/R/regularization/refit_sh2b3_psd_regularized.R
  - results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.001.fit.rds
  - results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.01.fit.rds
  - results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.1.fit.rds
  - results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.001.fit.rds
  - results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.01.fit.rds
  - results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.1.fit.rds
  - results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.001.fit.rds
  - results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.01.fit.rds
  - results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.1.fit.rds
  - results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.001.fit.rds
  - results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.01.fit.rds
  - results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.1.fit.rds
  - results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.001.fit.rds
  - results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.01.fit.rds
  - results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.1.fit.rds
  - results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv
  - results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  - logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "ta-r3-CONTEXT.md exists with `D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>` recorded BEFORE any LSF dispatch fires (pre-execute hard gate per OSF amendment)"
    - "src/R/regularization/ directory exists (created in Task 1; did not exist pre-W1)"
    - "src/R/regularization/refit_sh2b3_psd_regularized.R implements Wen 2017 ridge regularization R_reg = R + lambda*I with row-and-column normalization, swept across lambda in {0.001, 0.01, 0.1}, plus Hutchinson 2020 eigenvalue-clip alternative at floor 1e-6"
    - "LD pathology numbers (negative-eigenvalue %, effective-rank %, variant-coverage %) recorded against W1.5-audit numbers (23.46% / 50.4% / 6.7%) BEFORE any per-trait fitting fires"
    - "15 PSD-regularized SuSiE-RSS fits land on disk: 5 EUR traits (asthma, bmi, hypertension, stroke, t2d) x 3 lambda values"
    - "Each per-fit RDS records lambda_used, niter, n_CS, converged flag (TRUE/FALSE)"
    - "coloc.susie runs on 3 canonical pairs (BMI-HTN, HTN-stroke, HTN-T2D) at the smallest lambda where all three of (BMI, HTN, stroke) per-trait fits converge"
    - "Pair x lambda x PP summary TSV exists with PP.H0-PP.H4 per pair per lambda + both_traits_converged flag"
    - "W1 outcome classified into exactly one of {BRANCH_PSD_FIRM, BRANCH_PSD_PARTIAL, BRANCH_PSD_COLLAPSE, BRANCH_PSD_NON_CONVERGE} per OSF amendment decision matrix and written to ta-r3-CONTEXT.md as D-TA-R3-W1-BRANCH_PSD_*"
    - "LSF dispatch uses serial queue with -W=5760 min via bsub_wrapper.sh (per memory feedback_lsf_queues.md)"
    - "docs/manuscript/id-vs-ref-LD.md md5 unchanged (63fd81385590ffc8d23d45a0f0598959; honest-framing-lock invariant — manuscript edits OUT of phase scope)"
  artifacts:
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md"
      provides: "Phase context scaffold; records D-TA-R3-OSF-COVERAGE pre-execute gate + D-TA-R3-W1 outcome branch + downstream wave decision tokens"
      contains: "D-TA-R3-OSF-COVERAGE: COVERED"
    - path: "src/R/regularization/refit_sh2b3_psd_regularized.R"
      provides: "Wen 2017 ridge + Hutchinson 2020 eigenvalue-clip PSD regularization fitter (NEW; dir did not exist)"
      contains: "susieR::susie_rss"
    - path: "results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv"
      provides: "Pair x lambda x PP table; primary substrate for W1 outcome-branch classification"
      contains: "pair	lambda	PP.H0	PP.H1	PP.H2	PP.H3	PP.H4	n_snps	both_traits_converged"
    - path: "results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv"
      provides: "Eigen-decomposition pathology table on data/processed/ld_reference/EUR/SH2B3_12q24.rds (verifies W1.5-audit numbers before fitting)"
      contains: "negative_eig_pct"
    - path: "results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.01.fit.rds"
      provides: "Reference BMI fit at lambda=0.01 (mid-sweep canonical reference)"
  key_links:
    - from: "data/processed/sumstats_harmonized/{trait}.EUR.tsv.bgz"
      to: "results/fine_mapping_psd_regularized/{trait}.EUR.SH2B3_12q24.lambda{0.001,0.01,0.1}.fit.rds"
      via: "z = BETA / SE derived inline at fit time (per src/legacy/region_analysis/scripts/run_susie_rss.R:466 pattern)"
      pattern: "subset\\[, z := BETA / SE\\]"
    - from: "data/processed/ld_reference/EUR/SH2B3_12q24.rds"
      to: "R_reg = R + lambda*I (Wen 2017) + row-col normalize"
      via: "psd_regularize() in src/R/regularization/refit_sh2b3_psd_regularized.R"
      pattern: "R_reg.*lambda"
    - from: "results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv"
      to: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W1-BRANCH_PSD_*)"
      via: "outcome-branch classification function reads summary.tsv + applies amendment decision matrix"
      pattern: "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)"
    - from: ".planning/amendments/osf-amendment-r3-2026-05-04.md (posted to osf.io/az52u)"
      to: "ta-r3-CONTEXT.md `D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>`"
      via: "pre-execute hard gate; W1 Task 2 LSF dispatch checks this token"
      pattern: "D-TA-R3-OSF-COVERAGE: COVERED"
---

<objective>
Wave 1 — SH2B3 12q24 EUR PSD-regularized SuSiE-RSS audit-driven re-fit. Test whether the original Track A SH2B3 12q24 EUR Tier-A pass at PP.H4 = 1.0 across canonical pairs (BMI–HTN, HTN–stroke, HTN–T2D) survives a SuSiE-RSS configuration where the LD matrix is regularized to PSD (Wen 2017 ridge `R_reg = R + lambda*I` swept across lambda in {0.001, 0.01, 0.1}; Hutchinson 2020 eigenvalue-clip alternative at floor 1e-6) and the per-trait fits actually converge under `estimate_residual_variance = FALSE`.

Purpose: This wave addresses audit-V2 finding HQ#2(i) on the SH2B3 12q24 EUR LD matrix flagged 23.46% negative eigenvalues / 50.4% effective rank / 6.7% variant coverage with all 3 backing per-trait SuSiE fits flagged `convergence_status = non_converged`. Per Zou 2022, Wallace 2021, Wen 2017, Benner 2017, "PP near 1.0 from non-PSD LD plus non-converged fine-mapping" is a recognized false-positive mode. The W1 outcome (one of FIRM, PARTIAL, COLLAPSE, NON_CONVERGE — pre-registered in OSF amendment) determines W3 gate state and Cowork-side manuscript narrative branch. This is audit-driven re-analysis, NOT a fix or revision.

Output: 15 PSD-regularized SuSiE-RSS fits at `results/fine_mapping_psd_regularized/{trait}.EUR.SH2B3_12q24.lambda{lambda}.fit.rds`; LD pathology TSV; pair x lambda x PP summary TSV; ta-r3-CONTEXT.md scaffold (created BY this phase, used by all downstream waves) carrying D-TA-R3-OSF-COVERAGE token + D-TA-R3-W1-BRANCH_PSD_* outcome.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/amendments/osf-amendment-r3-2026-05-04.md
@.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-SUMMARY.md
@CLAUDE.md

<interfaces>
<!-- Pre-execute hard gate (THIS WAVE OPENS THE PHASE; ta-r3-CONTEXT.md does not yet exist) -->
- D-TA-R3-OSF-COVERAGE: COVERED at <timestamp> — MUST appear in ta-r3-CONTEXT.md BEFORE Task 2 (the LSF dispatch) fires.
- Task 1 is permitted to fire BEFORE OSF posting (mkdir + CONTEXT.md scaffold + LD pathology inspection are read-only/local; no LSF jobs).
- Task 2 hard-gates on the OSF coverage token; if missing or stale, abort with non-zero exit.

<!-- Existing files Wave 1 reads -->
- data/processed/ld_reference/EUR/SH2B3_12q24.rds — 1000G Phase 3 EUR LD reference (3.0 MB; 2026-04-21); canonical LD substrate per ta-sh2b3-W7 closeout
- data/processed/sumstats_harmonized/{asthma,bmi,hypertension,stroke,t2d}.EUR.tsv.bgz — 5 EUR harmonized sumstats (BETA, SE, MarkerName columns)
- src/legacy/region_analysis/scripts/run_susie_rss.R — z-score derivation pattern at line 466 (`subset[, z := BETA / SE]`); fitter pattern reused by W1's new PSD-regularized script
- config/bsub_wrapper.sh — sets -W per queue; serial=5760 min (96 hr); wrapper enforces, per-driver scripts do NOT need explicit -W stanzas
- /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript — R 4.4.2 + susieR 0.14.2 + coloc 5.2.3 env
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv — schema reference (4 columns: path, md5, rationale, commit_introducing); W5 will append successor rows (NOT in this wave)
- docs/manuscript/id-vs-ref-LD.md — md5=63fd81385590ffc8d23d45a0f0598959 — honest-framing-lock invariant; this wave MUST NOT modify

<!-- W1 PSD regularization specification (locked by OSF amendment) -->
- Wen 2017 ridge: R_reg = R + lambda * I; then row-and-column normalize so diag(R_reg) = 1
- Lambda sweep: {0.001, 0.01, 0.1}
- Hutchinson 2020 eigenvalue-clip alternative: clip negative eigenvalues to floor lambda_floor = 1e-6, reconstruct R_clip = V * diag(max(d, lambda_floor)) * V^T
- SuSiE-RSS call: susieR::susie_rss(z, R_reg, n, L = 10, coverage = 0.95, max_iter = 1000, estimate_residual_variance = FALSE, check_R = FALSE)

<!-- W1 outcome-branch decision matrix (pre-registered in OSF amendment; locked) -->
- BRANCH_PSD_FIRM: lambda exists where all 3 of (BMI, HTN, stroke) per-trait fits converge AND PP.H4 >= 0.8 across all 3 canonical pairs (BMI-HTN, HTN-stroke, HTN-T2D)
- BRANCH_PSD_PARTIAL: lambda exists with convergence but PP.H4 in [0.5, 0.8) for at least one canonical pair
- BRANCH_PSD_COLLAPSE: PP.H4 < 0.5 at all converged lambda values
- BRANCH_PSD_NON_CONVERGE: even with regularization across all lambda values, per-trait fits remain non-converged

<!-- Compute envelope -->
- ~30 min/fit on serial queue with la_multitrait_r env; 15 fits aggregate ~7.5 hr; parallelizable across 15 LSF slots -> wall ~30 min; mem 32 GB; LSF_UNIT_FOR_LIMITS=GB

<!-- LSF dispatch envelope (per memory feedback_lsf_queues.md) -->
- Queue: serial; -W: 5760 min (96 hr cap; well above ~30 min envelope); -n 1; -R "rusage[mem=32000]"
- Logs: logs/sh2b3_psd_refit/%J.{out,err}
- bsub_wrapper.sh transparent enforcement (per ta-sh2b3-W1 pattern)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Create ta-r3-CONTEXT.md scaffold + mkdir src/R/regularization + write Wen 2017 + Hutchinson 2020 PSD-regularized fitter + record LD pathology numbers</name>
  <files>
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
    src/R/regularization/refit_sh2b3_psd_regularized.R
    results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv
  </files>
  <read_first>
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md (PRIMARY SPEC; the W1 skeleton at lines 54-91 is authoritative)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md (OSF amendment; locks lambda sweep + outcome branches; W1 decision matrix at lines 52-65)
    - .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md (v2 audit; HQ#2(i) flag on SH2B3 12q24 EUR LD pathology numbers — 23.46% negative eigenvalues / 50.4% effective rank / 6.7% variant coverage)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-PLAN.md (predecessor PLAN.md format template; mirror frontmatter + interfaces + tasks XML)
    - src/legacy/region_analysis/scripts/run_susie_rss.R (z-score derivation pattern at line 466; fitter pattern to mirror)
    - data/processed/ld_reference/EUR/SH2B3_12q24.rds (read-only inspection target — eigen-decompose to verify pathology numbers BEFORE fitting)
  </read_first>
  <action>
    1. **Create ta-r3-CONTEXT.md scaffold** at `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` with the OSF coverage decision section, outcome-branch placeholders, and downstream wave decision tokens. CRITICAL: The OSF coverage token starts as `PENDING` here; it transitions to `COVERED at <timestamp>` ONLY after Carter posts the OSF amendment to osf.io/az52u (web-UI; manual). Task 2 will hard-gate on that transition.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       cat > .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<'EOF'
       # ta-r3 phase CONTEXT: audit-V2-driven PSD-regularized SH2B3 re-fit + R1 trait-pair coloc.susie cache-invalidated re-fire

       **Phase scope:** HPC-side compute work that produces substrate the Cowork-side v5 *Genome Medicine* manuscript revision (audit items A1, A2, A3, A6-stats, A7, A8, A9 — explicitly OUT of phase scope) draws on. After W5 closeout, a `/gsd-quick 260504-XXX-ta-r3-cowork-handoff` ships artifacts back to Cowork for v5 bundle ship.

       **Honest-framing lock (per `.planning/feedback_original_research_framing.md`):** Frame as "audit-driven re-analysis," NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The W6 manuscript md5 (`63fd81385590ffc8d23d45a0f0598959`) MUST stay stable through this phase; manuscript edits OUT of scope.

       **OSF amendment:** [.planning/amendments/osf-amendment-r3-2026-05-04.md](../../amendments/osf-amendment-r3-2026-05-04.md) — locks lambda sweep + W1 outcome branches + W2 outcome branches + W3 conditional gate.

       ---

       ## Decisions

       ### D-TA-R3-OSF-COVERAGE: PENDING

       **Status:** PENDING — Carter posts amendment to osf.io/az52u (web-UI workflow; ~15 min); after posting, this token transitions to `COVERED at <ISO-8601-timestamp>`.

       **Pre-execute hard gate:** W1 Task 2 (the LSF dispatch) MUST NOT fire until this token reads `COVERED at <timestamp>`. Task 2's pre-fire check greps for the `COVERED` substring; absence aborts with non-zero exit.

       **Permitted before COVERAGE:** W1 Task 1 (mkdir + CONTEXT.md scaffold + LD pathology inspection) — read-only / local-only; no LSF.

       **Verification at posting time:**
       - `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` returns 3 (commits remain ancestors)
       - OSF assigned a timestamp predating any commit that creates `results/fine_mapping_psd_regularized/`
       - URL of the amendment record copied back into `.planning/osf_deviations.md` under a new dated entry

       ---

       ### D-TA-R3-W1-BRANCH_PSD_*: PENDING (Wave 1 outcome)

       **Status:** PENDING — Wave 1 Task 3 classifies into exactly one of:
       - `BRANCH_PSD_FIRM` — lambda exists where all 3 SuSiE-RSS fits converge AND PP.H4 >= 0.8 across all 3 canonical pairs
       - `BRANCH_PSD_PARTIAL` — lambda exists with convergence but PP.H4 in [0.5, 0.8) for at least one canonical pair
       - `BRANCH_PSD_COLLAPSE` — PP.H4 < 0.5 at all converged lambda values
       - `BRANCH_PSD_NON_CONVERGE` — even with regularization across all lambda values, per-trait fits remain non-converged

       Wave 3 gate consumes this: FIRM/PARTIAL -> W3 fires; COLLAPSE -> W3 skipped (anchor itself fails; parity moot); NON_CONVERGE -> W3 deferred to Track B.

       ---

       ### D-TA-R3-W2-BRANCH_R1_*: PENDING (Wave 2 outcome)

       **Status:** PENDING — Wave 2 Task 3 classifies into exactly one of:
       - `BRANCH_R1_BUG` — post-refire produces non-empty PP rows in previously-empty 28
       - `BRANCH_R1_STRUCTURAL` — post-refire holds at 28/28 empty (or near-empty)

       ---

       ### D-TA-R3-W3-GATE: PENDING (computed from W1 outcome at W3 entry)

       **Status:** PENDING — gate fires only if W1 returns FIRM or PARTIAL; SKIPPED if COLLAPSE; DEFERRED_TO_TRACK_B if NON_CONVERGE.

       ---

       ### D-TA-R3-W4-GATE: PENDING (default DEFERRED_TO_FOOTNOTE; only fires if Cowork-side decides cheap A9 footnote insufficient)

       **Status:** PENDING — default disposition is `DEFERRED_TO_FOOTNOTE`.

       ---

       ## Reused Existing Substrate

       - [src/legacy/region_analysis/scripts/run_susie_rss.R](../../../src/legacy/region_analysis/scripts/run_susie_rss.R) — z-score derivation at line 466 (`subset[, z := BETA / SE]`); fitter pattern reused by W1's new PSD-regularized script
       - [config/bsub_wrapper.sh](../../../config/bsub_wrapper.sh) — sets -W per queue (serial=5760 min); W1+W2+W3 use it via the same pattern as ta-sh2b3-W1-PLAN.md
       - [.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv](../ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv) — W5 appends successor rows (NOT overwrite)
       - Commits in HEAD: `069b34f` (variant-ID matcher in run_qtl_coloc.R), `7d54183` (LD-panel-rsid override in run_susie_rss.R), `02c4404` (max_iterations -> max_iter)
       EOF
       ```

    2. **Create src/R/regularization/ directory** (does not exist; verified empty pre-W1):

       ```bash
       mkdir -p src/R/regularization
       mkdir -p results/fine_mapping_psd_regularized
       mkdir -p logs/sh2b3_psd_refit
       ```

    3. **Write src/R/regularization/refit_sh2b3_psd_regularized.R** implementing both Wen 2017 ridge regularization and Hutchinson 2020 eigenvalue-clip alternative. The script accepts `--trait`, `--lambda`, `--method` (ridge|eigclip), and `--out` arguments. It loads the LD matrix, regularizes per `--method`, derives z = BETA / SE inline at fit time from the harmonized sumstats, and runs `susieR::susie_rss(z, R_reg, n, L = 10, coverage = 0.95, max_iter = 1000, estimate_residual_variance = FALSE, check_R = FALSE)`. The output RDS is a list with fields: lambda, lambda_method, niter, n_CS, converged, susie_fit (full susie object), L_used, n, n_snps, dropped_snps_count, residual_variance.

       The script body (write to `src/R/regularization/refit_sh2b3_psd_regularized.R`):
       ```R
       #!/usr/bin/env Rscript
       # src/R/regularization/refit_sh2b3_psd_regularized.R
       # ta-r3 W1: PSD-regularized SuSiE-RSS re-fit per OSF amendment osf-amendment-r3-2026-05-04.md
       # Implements: Wen 2017 ridge (R_reg = R + lambda*I + row-col normalize) AND
       #             Hutchinson 2020 eigenvalue-clip alternative (clip negatives to lambda_floor=1e-6).
       # Reused from src/legacy/region_analysis/scripts/run_susie_rss.R: z = BETA / SE inline derivation pattern.
       # SuSiE-RSS call: susieR::susie_rss(z, R_reg, n, L=10, coverage=0.95, max_iter=1000,
       #                                    estimate_residual_variance=FALSE, check_R=FALSE).

       suppressPackageStartupMessages({
         library(optparse)
         library(susieR)
         library(data.table)
         library(R.utils)
       })

       opt <- OptionParser(option_list = list(
         make_option("--trait", type = "character", help = "asthma|bmi|hypertension|stroke|t2d"),
         make_option("--lambda", type = "numeric", help = "ridge lambda or eigclip floor"),
         make_option("--method", type = "character", default = "ridge",
                     help = "ridge (Wen 2017) or eigclip (Hutchinson 2020)"),
         make_option("--region", type = "character", default = "SH2B3_12q24"),
         make_option("--ancestry", type = "character", default = "EUR"),
         make_option("--ld_path", type = "character",
                     default = "data/processed/ld_reference/EUR/SH2B3_12q24.rds"),
         make_option("--sumstats_dir", type = "character",
                     default = "data/processed/sumstats_harmonized"),
         make_option("--out", type = "character", help = "output .fit.rds path")
       )) |> parse_args()

       psd_regularize_ridge <- function(R, lambda) {
         R_reg <- R + lambda * diag(nrow(R))
         d <- sqrt(diag(R_reg))
         R_reg <- sweep(sweep(R_reg, 1, d, "/"), 2, d, "/")
         R_reg
       }

       psd_regularize_eigclip <- function(R, lambda_floor = 1e-6) {
         e <- eigen(R, symmetric = TRUE)
         d_clip <- pmax(e$values, lambda_floor)
         R_clip <- e$vectors %*% diag(d_clip) %*% t(e$vectors)
         d <- sqrt(diag(R_clip))
         R_clip <- sweep(sweep(R_clip, 1, d, "/"), 2, d, "/")
         R_clip
       }

       # Load LD
       R <- readRDS(opt$ld_path)
       stopifnot(is.matrix(R), isSymmetric(R, tol = 1e-6))

       # Load harmonized sumstats; subset to LD overlap
       sumstats_path <- file.path(opt$sumstats_dir,
                                  sprintf("%s.%s.tsv.bgz", opt$trait, opt$ancestry))
       stopifnot(file.exists(sumstats_path))
       ss <- fread(cmd = sprintf("zcat %s", sumstats_path))
       # Subset to variants in LD; mirror src/legacy/region_analysis/scripts/run_susie_rss.R:466 pattern.
       # The SH2B3 12q24 region anchor: chr12 cytoband 12q24.12 (~110-115 Mb GRCh37 boundary).
       chr_anchor <- 12L
       pos_lo <- 111e6L; pos_hi <- 113e6L
       chrcol <- intersect(c("CHR", "chr", "Chr", "chromosome"), names(ss))[1]
       poscol <- intersect(c("POS", "pos", "Pos", "BP", "position"), names(ss))[1]
       betacol <- intersect(c("BETA", "beta", "Effect"), names(ss))[1]
       secol  <- intersect(c("SE", "se", "StdErr"), names(ss))[1]
       ncol_  <- intersect(c("N", "n_total", "Nsamples"), names(ss))[1]
       if (is.null(ncol_) || is.na(ncol_)) {
         # Per harmonized-sumstats convention; if absent, infer from neff or set fallback per trait.
         n_eff <- 350000L
       } else {
         n_eff <- as.integer(median(ss[[ncol_]], na.rm = TRUE))
       }
       sub <- ss[get(chrcol) == chr_anchor & get(poscol) >= pos_lo & get(poscol) <= pos_hi]
       sub[, z := get(betacol) / get(secol)]
       # Match LD rownames -> sumstats rsid; assume rownames(R) are rsids and sub has SNP/MarkerName col.
       snpcol <- intersect(c("SNP", "MarkerName", "rsid", "ID"), names(sub))[1]
       overlap <- intersect(rownames(R), sub[[snpcol]])
       n_dropped <- nrow(sub) - length(overlap)
       sub <- sub[get(snpcol) %in% overlap]
       setkeyv(sub, snpcol)
       sub <- sub[overlap]  # reorder to match R rownames
       R_sub <- R[overlap, overlap]
       z <- sub$z

       # Regularize
       R_reg <- if (opt$method == "ridge") psd_regularize_ridge(R_sub, opt$lambda) \
                else if (opt$method == "eigclip") psd_regularize_eigclip(R_sub, opt$lambda) \
                else stop(sprintf("Unknown method: %s", opt$method))

       # Fit
       t0 <- Sys.time()
       fit <- susieR::susie_rss(
         z = z, R = R_reg, n = n_eff,
         L = 10, coverage = 0.95, max_iter = 1000,
         estimate_residual_variance = FALSE, check_R = FALSE
       )
       wall_sec <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

       converged <- isTRUE(fit$converged)
       n_CS <- if (!is.null(fit$sets$cs)) length(fit$sets$cs) else 0L

       out_list <- list(
         trait = opt$trait, region = opt$region, ancestry = opt$ancestry,
         lambda = opt$lambda, lambda_method = opt$method,
         L_used = 10L, niter = fit$niter %||% NA_integer_,
         n_CS = n_CS, converged = converged,
         n = n_eff, n_snps = length(z), dropped_snps_count = n_dropped,
         residual_variance = fit$sigma2 %||% NA_real_,
         wall_sec = wall_sec, susie_fit = fit
       )
       dir.create(dirname(opt$out), recursive = TRUE, showWarnings = FALSE)
       saveRDS(out_list, opt$out)
       cat(sprintf("WROTE %s; converged=%s; n_CS=%d; niter=%s; lambda=%s; method=%s; wall=%.1fs\n",
                   opt$out, converged, n_CS, out_list$niter, opt$lambda, opt$method, wall_sec))
       ```

       Make executable:
       ```bash
       chmod +x src/R/regularization/refit_sh2b3_psd_regularized.R
       ```

    4. **Verify W1.5-audit LD pathology numbers** by eigen-decomposing the LD matrix BEFORE any fitting fires. If the recomputed numbers diverge from the v2-audit values (23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage) by more than 1 percentage point in any dimension, HALT and investigate provenance — the LD matrix may not be the same one that produced the audit numbers (per plan-of-plans risk register row 2).

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS' > results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv
       R <- readRDS("data/processed/ld_reference/EUR/SH2B3_12q24.rds")
       stopifnot(is.matrix(R), isSymmetric(R, tol = 1e-6))
       e <- eigen(R, symmetric = TRUE, only.values = TRUE)$values
       n <- length(e)
       neg_pct <- 100 * sum(e < 0) / n
       eff_rank_pct <- 100 * sum(e > 1e-6) / n
       cat(sprintf("metric\tvalue\taudit_v2_target\tdelta_abs\n"))
       cat(sprintf("n_variants\t%d\tNA\tNA\n", n))
       cat(sprintf("negative_eig_pct\t%.4f\t23.46\t%.4f\n", neg_pct, abs(neg_pct - 23.46)))
       cat(sprintf("effective_rank_pct\t%.4f\t50.4\t%.4f\n", eff_rank_pct, abs(eff_rank_pct - 50.4)))
       cat(sprintf("min_eigenvalue\t%.6e\tNA\tNA\n", min(e)))
       cat(sprintf("max_eigenvalue\t%.6e\tNA\tNA\n", max(e)))
       cat(sprintf("condition_number\t%.6e\tNA\tNA\n", max(abs(e)) / max(min(abs(e)), 1e-30)))
       RS
       cat results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv

       # Halt-on-divergence check (delta > 1.0 percentage point):
       AWK_OUT=$(awk -F'\t' 'NR>1 && $1 ~ /(negative_eig_pct|effective_rank_pct)/ && $4 != "NA" && $4+0 > 1.0 { print $1": delta="$4 }' results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv)
       if [ -n "$AWK_OUT" ]; then
         echo "HALT: LD pathology numbers diverge from v2-audit by >1.0 percentage point:"
         echo "$AWK_OUT"
         echo "Investigate provenance of data/processed/ld_reference/EUR/SH2B3_12q24.rds before fitting."
         exit 1
       fi
       echo "PASS: LD pathology numbers match v2-audit baseline within 1.0 percentage point"
       ```

    5. **Atomic commit** (CONTEXT.md scaffold + fitter script + LD pathology TSV; explicit paths only per `.planning/feedback_multi_terminal_staging.md`):

       ```bash
       git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md \
               src/R/regularization/refit_sh2b3_psd_regularized.R \
               results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv
       git commit -m "feat(ta-r3, W1): scaffold ta-r3-CONTEXT.md + Wen 2017 ridge / Hutchinson 2020 eigclip fitter + verify LD pathology baseline (audit-driven re-analysis)"
       ```
  </action>
  <acceptance_criteria>
    - File `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` exists.
    - `grep "D-TA-R3-OSF-COVERAGE: PENDING" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1 hit (token initialized as PENDING; transitions to COVERED at OSF post time).
    - `grep -E "D-TA-R3-W(1|2|3|4)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | wc -l` returns ≥ 4 (one decision token per downstream wave).
    - Directory `src/R/regularization/` exists: `[ -d src/R/regularization ]`.
    - File `src/R/regularization/refit_sh2b3_psd_regularized.R` exists and is executable: `[ -x src/R/regularization/refit_sh2b3_psd_regularized.R ]`.
    - Fitter script contains both methods + correct SuSiE-RSS call: `grep -c "psd_regularize_ridge\|psd_regularize_eigclip\|susie_rss" src/R/regularization/refit_sh2b3_psd_regularized.R` returns ≥ 3.
    - SuSiE-RSS call uses required parameters: `grep -E "L = 10.*coverage = 0.95|max_iter = 1000.*estimate_residual_variance = FALSE.*check_R = FALSE" src/R/regularization/refit_sh2b3_psd_regularized.R` matches.
    - LD pathology TSV exists with at least 5 rows: `[ "$(wc -l < results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv)" -ge 6 ]` (header + 5 data rows).
    - LD pathology numbers match v2-audit within 1.0 pp: `awk -F'\t' 'NR>1 && $1 ~ /(negative_eig_pct|effective_rank_pct)/ && $4+0 > 1.0' results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv` returns empty (no divergence).
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W1.*scaffold.*audit-driven re-analysis"` matches.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md ] && grep -q "D-TA-R3-OSF-COVERAGE: PENDING" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && [ "$(grep -cE 'D-TA-R3-W[1-4]' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 4 ] && [ -d src/R/regularization ] && [ -x src/R/regularization/refit_sh2b3_psd_regularized.R ] && grep -q "susie_rss" src/R/regularization/refit_sh2b3_psd_regularized.R && [ -f results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv ] && [ "$(wc -l < results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv)" -ge 6 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Phase scaffold landed: ta-r3-CONTEXT.md created with D-TA-R3-OSF-COVERAGE token at PENDING + outcome-branch placeholders for all downstream waves. src/R/regularization/ created with Wen 2017 ridge + Hutchinson 2020 eigclip fitter. LD pathology numbers verified against v2-audit baseline within 1.0 pp. Manuscript md5 unchanged (honest-framing-lock invariant). Task 1 is read-only/local-only — no LSF dispatch fired (intentional; OSF posting gate not yet cleared).
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Pre-execute hard gate on D-TA-R3-OSF-COVERAGE COVERED + dispatch 15 PSD-regularized SuSiE-RSS fits via LSF (serial queue, -W=5760 via bsub_wrapper.sh)</name>
  <files>
    results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.001.fit.rds
    results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.01.fit.rds
    results/fine_mapping_psd_regularized/asthma.EUR.SH2B3_12q24.lambda0.1.fit.rds
    results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.001.fit.rds
    results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.01.fit.rds
    results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.1.fit.rds
    results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.001.fit.rds
    results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.01.fit.rds
    results/fine_mapping_psd_regularized/hypertension.EUR.SH2B3_12q24.lambda0.1.fit.rds
    results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.001.fit.rds
    results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.01.fit.rds
    results/fine_mapping_psd_regularized/stroke.EUR.SH2B3_12q24.lambda0.1.fit.rds
    results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.001.fit.rds
    results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.01.fit.rds
    results/fine_mapping_psd_regularized/t2d.EUR.SH2B3_12q24.lambda0.1.fit.rds
    logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-OSF-COVERAGE MUST read COVERED before this task fires)
    - src/R/regularization/refit_sh2b3_psd_regularized.R (Task 1 output; verify executable + fitter signature)
    - config/bsub_wrapper.sh (verify -W=5760 for serial queue per memory feedback_lsf_queues.md)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-PLAN.md §"Task 1" (LSF dispatch pattern to mirror)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 1 Tasks (skeleton)" lines 76-91 (acceptance criteria source)
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks:** Verify D-TA-R3-OSF-COVERAGE has transitioned from PENDING to COVERED (Carter posted OSF amendment). Verify the three commit hashes remain HEAD ancestors. Verify bsub_wrapper.sh enforces -W=5760 for serial queue.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # OSF coverage gate (per OSF amendment posting requirement)
       grep -q "D-TA-R3-OSF-COVERAGE: COVERED at" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md || \
         { echo "ABORT: D-TA-R3-OSF-COVERAGE still PENDING. OSF amendment must be posted to osf.io/az52u and the COVERED token written to ta-r3-CONTEXT.md before W1 LSF dispatch fires (per OSF amendment hard gate)."; exit 1; }
       echo "PASS: D-TA-R3-OSF-COVERAGE = COVERED"

       # Commit-ancestor invariants (per OSF amendment posting verification)
       N_ANCESTORS=$(git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l)
       [ "$N_ANCESTORS" -eq 3 ] || \
         { echo "ABORT: required commit ancestors missing (069b34f + 7d54183 + 02c4404 must be in git log; got $N_ANCESTORS)"; exit 1; }
       echo "PASS: 3/3 commit ancestors verified"

       # LSF wall-time configuration
       grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh || \
         { echo "ABORT: bsub_wrapper.sh does not enforce -W=5760 for serial queue"; exit 1; }
       echo "PASS: bsub_wrapper.sh enforces -W=5760 (96 hr) for serial queue"

       # Fitter script executable
       [ -x src/R/regularization/refit_sh2b3_psd_regularized.R ] || \
         { echo "ABORT: fitter not executable"; exit 1; }
       echo "PASS: fitter script ready"
       ```

    2. **Dispatch 15 PSD-regularized SuSiE-RSS fits** via LSF — 5 traits (asthma, bmi, hypertension, stroke, t2d) x 3 lambda values (0.001, 0.01, 0.1) = 15 fits. Each fit runs on serial queue with -W=5760 min (transparently set by bsub_wrapper.sh), 1 slot, 32 GB mem, R env la_multitrait_r. Method = ridge (Wen 2017); the eigenvalue-clip alternative (Hutchinson 2020) is run as a robustness companion at lambda=1e-6 in the same dispatch loop if the primary ridge sweep fails to converge at any lambda (per OSF amendment paragraph (a)). For Task 2 we fire only the ridge sweep; eigclip companion fires if Task 3 detects all-non-converged outcome.

       ```bash
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       export LSF_UNIT_FOR_LIMITS=GB
       mkdir -p logs/sh2b3_psd_refit

       LOG=logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log
       : > "$LOG"

       for trait in asthma bmi hypertension stroke t2d; do
         for lam in 0.001 0.01 0.1; do
           jobname="ta_r3_W1_${trait}_l${lam}"
           outpath="results/fine_mapping_psd_regularized/${trait}.EUR.SH2B3_12q24.lambda${lam}.fit.rds"
           # bsub_wrapper.sh transparently appends -W=5760 for QUEUE=serial
           QUEUE=serial config/bsub_wrapper.sh \
             bsub -J "$jobname" \
                  -q serial \
                  -n 1 \
                  -R "rusage[mem=32000]" \
                  -o "logs/sh2b3_psd_refit/%J.out" \
                  -e "logs/sh2b3_psd_refit/%J.err" \
                  /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
                    src/R/regularization/refit_sh2b3_psd_regularized.R \
                    --trait "$trait" --lambda "$lam" --method ridge \
                    --out "$outpath" \
             | tee -a "$LOG"
         done
       done

       echo "[$(date +%H:%M:%S)] All 15 LSF jobs submitted." | tee -a "$LOG"
       ```

    3. **Monitor LSF jobs to completion:** poll until no PEND/RUN jobs match the W1 jobname prefix `ta_r3_W1_`. Wait at most ~2 hr wall (compute envelope is ~30 min/fit at full parallelism; allow 4x margin).

       ```bash
       while bjobs -J 'ta_r3_W1_*' 2>&1 | grep -qE "PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running: $(bjobs -J 'ta_r3_W1_*' 2>&1 | grep -cE 'PEND|RUN')"
         sleep 300
       done
       echo "[$(date +%H:%M:%S)] All W1 LSF jobs done." | tee -a "$LOG"
       ```

    4. **Verify all 15 outputs landed:**

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       missing=0
       for trait in asthma bmi hypertension stroke t2d; do
         for lam in 0.001 0.01 0.1; do
           f="results/fine_mapping_psd_regularized/${trait}.EUR.SH2B3_12q24.lambda${lam}.fit.rds"
           if [ ! -f "$f" ]; then
             echo "MISSING: $f"
             missing=$((missing+1))
           else
             # Quick sanity: file is a valid RDS
             /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e "x <- readRDS('$f'); stopifnot(!is.null(x\$susie_fit), !is.null(x\$converged))" || \
               { echo "CORRUPT: $f"; missing=$((missing+1)); }
           fi
         done
       done
       echo "$missing missing of 15"
       [ "$missing" -eq 0 ] || exit 1
       ```

    5. **Atomic commit** (dispatch log + fits — fits are tracked because the regularized output namespace is small and stable; verify .gitignore policy first):

       ```bash
       grep -n "results/fine_mapping_psd_regularized" .gitignore && \
         echo "(gitignored — committing only the dispatch log)" || \
         git add results/fine_mapping_psd_regularized/*.fit.rds
       git add logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log
       git commit -m "feat(ta-r3, W1): dispatch + land 15 PSD-regularized SuSiE-RSS fits (audit-driven re-analysis; ridge sweep lambda in {0.001,0.01,0.1} x 5 EUR traits)"
       ```
  </action>
  <acceptance_criteria>
    - Pre-fire gate: `grep "D-TA-R3-OSF-COVERAGE: COVERED at" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1 hit.
    - Pre-fire gate: `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` returns 3.
    - Pre-fire gate: `grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh` returns 0.
    - 15 fit RDS files exist on disk: `ls results/fine_mapping_psd_regularized/*.fit.rds | wc -l` returns ≥ 15.
    - All 5 EUR traits represented at all 3 lambdas: for each trait in {asthma, bmi, hypertension, stroke, t2d} and lambda in {0.001, 0.01, 0.1}, the path `results/fine_mapping_psd_regularized/{trait}.EUR.SH2B3_12q24.lambda{lambda}.fit.rds` exists.
    - Each RDS is structurally valid: `Rscript -e 'x <- readRDS("results/fine_mapping_psd_regularized/bmi.EUR.SH2B3_12q24.lambda0.01.fit.rds"); stopifnot(!is.null(x$susie_fit), !is.null(x$converged), !is.null(x$lambda))'` exits 0.
    - Dispatch log file exists: `[ -s logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log ]`.
    - All LSF jobs completed exit 0: `bhist -a -J 'ta_r3_W1_*' 2>&1 | grep -c "Done successfully"` ≥ 15.
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W1.*PSD-regularized.*audit-driven re-analysis"` matches.
    - Honest-framing-lock invariant preserved: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-R3-OSF-COVERAGE: COVERED at" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && [ "$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')" -eq 3 ] && grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh && [ "$(ls results/fine_mapping_psd_regularized/*.fit.rds 2>/dev/null | wc -l)" -ge 15 ] && for t in asthma bmi hypertension stroke t2d; do for l in 0.001 0.01 0.1; do [ -f "results/fine_mapping_psd_regularized/${t}.EUR.SH2B3_12q24.lambda${l}.fit.rds" ] || { echo "MISSING ${t} ${l}"; exit 1; }; done; done && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    OSF coverage gate cleared (Carter posted amendment). 15 PSD-regularized SuSiE-RSS fits land on disk under lambda in {0.001, 0.01, 0.1} x 5 EUR traits. Each RDS structurally valid with susie_fit, converged, lambda fields populated. LSF dispatch log committed. Honest-framing-lock manuscript md5 unchanged. Substrate ready for Task 3 (canonical-pair coloc.susie + outcome-branch classification).
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Run coloc.susie on 3 canonical pairs at smallest converged lambda + classify W1 outcome branch (FIRM | PARTIAL | COLLAPSE | NON_CONVERGE) + write D-TA-R3-W1-BRANCH_PSD_* to ta-r3-CONTEXT.md</name>
  <files>
    results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  </files>
  <read_first>
    - results/fine_mapping_psd_regularized/{bmi,hypertension,stroke,t2d}.EUR.SH2B3_12q24.lambda{0.001,0.01,0.1}.fit.rds (Task 2 outputs; 12 fits driving the canonical-pair coloc)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — SH2B3 12q24 EUR PSD-regularized re-fit" lines 52-65 (W1 outcome-branch decision matrix; AUTHORITATIVE)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 1 Tasks (skeleton) #5 + #6" lines 81-83 (coloc.susie + branch classification spec)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md §"Task 2: Generate Wave 3 outcome-presentation report" (predecessor pattern for outcome-branch TSV format)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (write target — append D-TA-R3-W1-BRANCH_PSD_* to existing scaffold under Decisions section)
  </read_first>
  <action>
    1. **Build the pair x lambda x PP table** by running `coloc::coloc.susie` on the 3 canonical trait-pairs (BMI–HTN, HTN–stroke, HTN–T2D) at each lambda value where BOTH traits in the pair converged. The pair-by-pair structure is per the OSF amendment paragraph (b): the smallest lambda where all three of (BMI, HTN, stroke) converge is the "primary lambda"; PP.H4 at that lambda is the headline number.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS' > results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv
       suppressPackageStartupMessages({ library(coloc); library(susieR) })
       cat("pair\tlambda\tPP.H0\tPP.H1\tPP.H2\tPP.H3\tPP.H4\tn_snps\tboth_traits_converged\n")
       canonical_pairs <- list(
         c("bmi", "hypertension"),
         c("hypertension", "stroke"),
         c("hypertension", "t2d")
       )
       for (lam in c("0.001", "0.01", "0.1")) {
         for (pp in canonical_pairs) {
           t1 <- pp[1]; t2 <- pp[2]
           f1 <- sprintf("results/fine_mapping_psd_regularized/%s.EUR.SH2B3_12q24.lambda%s.fit.rds", t1, lam)
           f2 <- sprintf("results/fine_mapping_psd_regularized/%s.EUR.SH2B3_12q24.lambda%s.fit.rds", t2, lam)
           if (!file.exists(f1) || !file.exists(f2)) {
             cat(sprintf("%s_vs_%s\t%s\tNA\tNA\tNA\tNA\tNA\tNA\tFALSE\n", t1, t2, lam))
             next
           }
           fit1 <- readRDS(f1); fit2 <- readRDS(f2)
           both_conv <- isTRUE(fit1$converged) && isTRUE(fit2$converged)
           if (!both_conv) {
             cat(sprintf("%s_vs_%s\t%s\tNA\tNA\tNA\tNA\tNA\t%d\tFALSE\n",
                         t1, t2, lam, fit1$n_snps %||% NA))
             next
           }
           res <- tryCatch(
             coloc::coloc.susie(fit1$susie_fit, fit2$susie_fit),
             error = function(e) NULL
           )
           if (is.null(res) || is.null(res$summary) || nrow(res$summary) == 0) {
             cat(sprintf("%s_vs_%s\t%s\tNA\tNA\tNA\tNA\tNA\t%d\tTRUE\n",
                         t1, t2, lam, fit1$n_snps %||% NA))
             next
           }
           # coloc.susie returns one row per CS-pair; take the maximum PP.H4 across CS-pairs.
           idx <- which.max(res$summary$PP.H4.abf)
           s <- res$summary[idx, ]
           cat(sprintf("%s_vs_%s\t%s\t%g\t%g\t%g\t%g\t%g\t%d\tTRUE\n",
                       t1, t2, lam,
                       s[["PP.H0.abf"]], s[["PP.H1.abf"]], s[["PP.H2.abf"]],
                       s[["PP.H3.abf"]], s[["PP.H4.abf"]],
                       fit1$n_snps %||% NA))
         }
       }
       RS
       cat results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv
       ```

       Verify schema: header is `pair\tlambda\tPP.H0\tPP.H1\tPP.H2\tPP.H3\tPP.H4\tn_snps\tboth_traits_converged`; expect 3 pairs x 3 lambdas = 9 data rows.

    2. **Classify W1 outcome branch** per OSF amendment decision matrix. The classifier reads `sh2b3_psd_pph4_summary.tsv` and applies these rules in order:
       - Find smallest lambda where all 3 of (bmi, hypertension, stroke) per-trait converged. That requires looking at the per-trait fit RDS files (not the pair table), because the OSF amendment paragraph (b) specifies "smallest lambda where all three of (BMI, hypertension, stroke) per-trait fits converge."
       - At that "primary lambda," check the 3 canonical pair PP.H4 values:
         - All 3 PP.H4 ≥ 0.8 → BRANCH_PSD_FIRM
         - At least one PP.H4 in [0.5, 0.8) and none below 0.5 → BRANCH_PSD_PARTIAL
         - At least one PP.H4 < 0.5 → BRANCH_PSD_COLLAPSE
       - If no lambda has all 3 of (bmi, hypertension, stroke) converged → BRANCH_PSD_NON_CONVERGE.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       BRANCH=$(/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS'
       summary <- read.delim("results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv",
                              stringsAsFactors = FALSE)
       primary_lambda <- NA_real_
       for (lam in c(0.001, 0.01, 0.1)) {
         all_three_conv <- TRUE
         for (t in c("bmi", "hypertension", "stroke")) {
           f <- sprintf("results/fine_mapping_psd_regularized/%s.EUR.SH2B3_12q24.lambda%s.fit.rds",
                        t, format(lam, scientific = FALSE))
           if (!file.exists(f)) { all_three_conv <- FALSE; break }
           x <- readRDS(f)
           if (!isTRUE(x$converged)) { all_three_conv <- FALSE; break }
         }
         if (all_three_conv) { primary_lambda <- lam; break }
       }
       if (is.na(primary_lambda)) {
         cat("BRANCH_PSD_NON_CONVERGE\n")
       } else {
         lam_str <- format(primary_lambda, scientific = FALSE)
         sub <- summary[summary$lambda == lam_str & summary$both_traits_converged == "TRUE", ]
         if (nrow(sub) < 3) {
           cat("BRANCH_PSD_NON_CONVERGE\n")
         } else {
           pph4 <- as.numeric(sub$PP.H4)
           pph4 <- pph4[!is.na(pph4)]
           if (length(pph4) < 3) {
             cat("BRANCH_PSD_NON_CONVERGE\n")
           } else if (all(pph4 >= 0.8)) {
             cat("BRANCH_PSD_FIRM\n")
           } else if (any(pph4 < 0.5)) {
             cat("BRANCH_PSD_COLLAPSE\n")
           } else {
             cat("BRANCH_PSD_PARTIAL\n")
           }
         }
       }
       RS
       )
       echo "Computed branch: $BRANCH"
       PRIMARY_LAMBDA=$(awk -F'\t' 'NR>1 && $9 == "TRUE" {print $2; exit}' results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv)
       echo "Primary lambda: $PRIMARY_LAMBDA"
       ```

    3. **Append D-TA-R3-W1-BRANCH_PSD_* to ta-r3-CONTEXT.md** using `Edit` semantics — replace the line `### D-TA-R3-W1-BRANCH_PSD_*: PENDING (Wave 1 outcome)` and the subsequent "Status: PENDING" with the resolved branch + primary lambda + per-pair PP.H4 table:

       Use the Edit tool to replace the W1 PENDING block with the resolved block. The replacement block:

       ```markdown
       ### D-TA-R3-W1-BRANCH_PSD_<BRANCH>: <BRANCH> (Wave 1 outcome)

       **Recorded:** <ISO-8601 timestamp>

       **Primary lambda:** <PRIMARY_LAMBDA> (smallest lambda where all 3 of bmi, hypertension, stroke per-trait fits converged; NONE if branch=NON_CONVERGE).

       **Per-trait convergence at primary lambda:**

       | trait | converged | n_CS | niter |
       |---|---|---|---|
       | bmi | <TRUE/FALSE> | <n_CS> | <niter> |
       | hypertension | <TRUE/FALSE> | <n_CS> | <niter> |
       | stroke | <TRUE/FALSE> | <n_CS> | <niter> |
       | asthma | <TRUE/FALSE> | <n_CS> | <niter> |
       | t2d | <TRUE/FALSE> | <n_CS> | <niter> |

       **Canonical-pair coloc.susie PP.H4 at primary lambda:**

       | pair | PP.H4 | Threshold class |
       |---|---|---|
       | bmi_vs_hypertension | <value> | <SURVIVE_GE_0.8 \| PARTIAL_0.5_TO_0.8 \| COLLAPSE_BELOW_0.5> |
       | hypertension_vs_stroke | <value> | <class> |
       | hypertension_vs_t2d | <value> | <class> |

       **Detailed numerics:** [results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv](../../../results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv)

       **W3 gate implication:** `D-TA-R3-W3-GATE = <FIRES | SKIPPED | DEFERRED_TO_TRACK_B>`
       - FIRM or PARTIAL → W3 fires (R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR)
       - COLLAPSE → W3 SKIPPED (anchor itself fails; parity moot; record `D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME`)
       - NON_CONVERGE → W3 DEFERRED_TO_TRACK_B (deeper LD-panel-vs-GWAS-cohort mismatch)

       **Cowork-side branch (informational; manuscript edits OUT of phase scope):** Per OSF amendment paragraph (c), the manuscript v5 narrative branches:
       - FIRM → SH2B3 anchor empirically supported under regularized LD; report lambda + PSD diagnostic + converged-status disclosure
       - PARTIAL → reframe SH2B3 from Tier-A to Tier-B; revise abstract + discussion
       - COLLAPSE → SH2B3 no longer Tier-A; report prior-literature PP=1.0 anchor as not surviving matched-LD with PSD regularization
       - NON_CONVERGE → disclose deeper LD-panel-vs-GWAS-cohort mismatch; defer to Track B (in-sample LD via UKB/AoU EUR)
       ```

       Use the `Edit` tool to perform the replacement (the executor agent has Edit semantics; substitute concrete values for all `<...>` placeholders from the resolved BRANCH + PRIMARY_LAMBDA + summary.tsv numerics).

    4. **Update D-TA-R3-W3-GATE token in ta-r3-CONTEXT.md** to reflect the W1-driven gate state. Use Edit to replace `### D-TA-R3-W3-GATE: PENDING` block with `### D-TA-R3-W3-GATE: <FIRES | SKIPPED | DEFERRED_TO_TRACK_B> (driven by W1 = <BRANCH>)`.

    5. **Atomic commit** with explicit paths only:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
       git commit -m "docs(ta-r3, W1): record D-TA-R3-W1-BRANCH_PSD_${BRANCH} (audit-driven re-analysis; primary lambda=${PRIMARY_LAMBDA}; canonical-pair PP.H4 table)"
       ```
  </action>
  <acceptance_criteria>
    - File `results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv` exists with header `pair\tlambda\tPP.H0\tPP.H1\tPP.H2\tPP.H3\tPP.H4\tn_snps\tboth_traits_converged`.
    - Pair x lambda summary has 9 data rows (3 canonical pairs x 3 lambdas): `[ "$(awk 'NR>1' results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv | wc -l)" -ge 9 ]`.
    - W1 outcome-branch token recorded in ta-r3-CONTEXT.md with exactly one of FIRM, PARTIAL, COLLAPSE, NON_CONVERGE: `grep -E "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | wc -l` returns ≥ 1.
    - The PENDING token has been replaced (no `D-TA-R3-W1-BRANCH_PSD_\\*: PENDING` remaining): `grep -c "D-TA-R3-W1-BRANCH_PSD_\\*: PENDING" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns 0.
    - W3 gate token resolved to FIRES, SKIPPED, or DEFERRED_TO_TRACK_B: `grep -E "D-TA-R3-W3-GATE: (FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - Per-pair canonical-pair table present in the W1 decision block: `grep -E "bmi_vs_hypertension|hypertension_vs_stroke|hypertension_vs_t2d" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | wc -l` returns ≥ 3.
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W1.*D-TA-R3-W1-BRANCH_PSD.*audit-driven re-analysis"` matches.
    - Honest-framing-lock invariant preserved: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv ] && head -1 results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv | grep -q "pair	lambda	PP.H0	PP.H1	PP.H2	PP.H3	PP.H4	n_snps	both_traits_converged" && [ "$(awk 'NR>1' results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv | wc -l)" -ge 9 ] && [ "$(grep -cE 'D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(grep -cE 'D-TA-R3-W3-GATE: (FIRES|SKIPPED|DEFERRED_TO_TRACK_B)' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Pair x lambda x PP table built (9 data rows). W1 outcome branch classified (one of FIRM, PARTIAL, COLLAPSE, NON_CONVERGE) and recorded in ta-r3-CONTEXT.md per OSF amendment decision matrix. W3 gate token resolved (FIRES, SKIPPED, or DEFERRED_TO_TRACK_B). Honest-framing-lock manuscript md5 unchanged. Atomic commit landed. W2 substrate ready (W2 reads W1 outcome from CONTEXT.md to decide whether SH2B3-row reframing flows downstream).
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| OSF amendment posting (manual web-UI) ↔ Task 2 LSF dispatch | D-TA-R3-OSF-COVERAGE PENDING→COVERED transition is the pre-execute hard gate; Task 2 hard-aborts if PENDING |
| 1000G EUR LD reference (data/processed/ld_reference/EUR/SH2B3_12q24.rds) ↔ W1.5-audit numbers | W1 Task 1 step 4 recomputes eigen-decomposition + halts on >1.0 pp divergence (per plan-of-plans risk register row 2 — "LD panel may be the WRONG matrix") |
| Manuscript md5 (63fd81385590ffc8d23d45a0f0598959) ↔ honest-framing-lock invariant | Every task's acceptance criteria verifies md5 unchanged (per `.planning/feedback_original_research_framing.md`) |
| Multi-terminal git staging on GPFS ↔ explicit-path commits | Per `.planning/feedback_multi_terminal_staging.md`: never `git add .` / `-A`; only explicit paths |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-TA-R3-W1-01 | T (Tampering) | LD reference matrix provenance | mitigate | Task 1 step 4 eigen-decomposes + halts on >1.0 pp divergence from v2-audit baseline (23.46% / 50.4%); records to sh2b3_psd_ld_pathology.tsv for post-hoc audit |
| T-TA-R3-W1-02 | T (Tampering) | OSF amendment posting bypass | mitigate | Task 2 step 1 hard-grep on `D-TA-R3-OSF-COVERAGE: COVERED at`; absence aborts non-zero exit (no LSF dispatch fires without OSF coverage) |
| T-TA-R3-W1-03 | I (Information disclosure) | Implicit `git add .` could stage results_identity_ld/ (DEC-2026-04-25-01) or unintended files | mitigate | Every commit task uses explicit file paths only (per `.planning/feedback_multi_terminal_staging.md`) |
| T-TA-R3-W1-04 | I (Information disclosure) | Honest-framing-lock manuscript edit | accept | OUT of phase scope per OSF amendment "What is not changing" paragraph; verified md5 unchanged in every task acceptance |
| T-TA-R3-W1-05 | D (Denial of service) | LSF jobs killed by 30-min queue default RUNLIMIT | mitigate | bsub_wrapper.sh transparently sets -W=5760 for serial queue (per memory feedback_lsf_queues.md); Task 2 step 1 verifies wrapper config |
| T-TA-R3-W1-06 | E (Elevation of privilege) | Outcome-branch classifier silently picks favorable branch | mitigate | Branch decision rules pre-registered in OSF amendment paragraph (c); classifier in Task 3 step 2 reads summary.tsv + applies rules verbatim; no rule selection by Claude |
</threat_model>

<verification>
- ta-r3-CONTEXT.md scaffold landed with D-TA-R3-OSF-COVERAGE PENDING + outcome-branch placeholders (Task 1)
- src/R/regularization/refit_sh2b3_psd_regularized.R landed with Wen 2017 ridge + Hutchinson 2020 eigclip implementations (Task 1)
- LD pathology numbers verified within 1.0 pp of v2-audit baseline (Task 1 step 4)
- 15 PSD-regularized SuSiE-RSS fits land on disk (5 traits x 3 lambdas) post-OSF-coverage gate clear (Task 2)
- coloc.susie pair x lambda x PP table built (9 rows; Task 3)
- W1 outcome branch classified per OSF amendment decision matrix (Task 3)
- W3 gate token resolved (Task 3)
- 3 atomic commits landed (Task 1, Task 2, Task 3)
- Honest-framing-lock manuscript md5 unchanged through all 3 tasks
</verification>

<success_criteria>
- ta-r3-CONTEXT.md scaffold created with D-TA-R3-OSF-COVERAGE token + outcome-branch placeholders for W1/W2/W3/W4
- src/R/regularization/ directory + refit_sh2b3_psd_regularized.R fitter (Wen 2017 ridge + Hutchinson 2020 eigclip) landed
- LD pathology TSV verifies v2-audit numbers within 1.0 pp (or halts on divergence)
- Pre-execute hard gate on D-TA-R3-OSF-COVERAGE COVERED enforced before LSF dispatch
- 15 PSD-regularized SuSiE-RSS fits land on disk
- Pair x lambda x PP summary TSV with 9 data rows
- W1 outcome branch (FIRM/PARTIAL/COLLAPSE/NON_CONVERGE) recorded in ta-r3-CONTEXT.md
- W3 gate token resolved (FIRES/SKIPPED/DEFERRED_TO_TRACK_B)
- bsub_wrapper.sh enforces -W=5760 for serial queue
- Honest-framing-lock manuscript md5 unchanged (63fd81385590ffc8d23d45a0f0598959)
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md` with:
- D1 ta-r3-CONTEXT.md scaffold landed (PASS/WARN/FAIL)
- D2 fitter script + src/R/regularization/ directory landed (PASS/WARN/FAIL)
- D3 LD pathology numbers within 1.0 pp of v2-audit baseline (PASS/WARN/FAIL)
- D4 OSF coverage gate cleared before LSF dispatch (PASS/WARN/FAIL)
- D5 15 fits land on disk (PASS/WARN/FAIL)
- D6 pair x lambda x PP table built (PASS/WARN/FAIL)
- D7 W1 outcome branch classified per OSF amendment decision matrix (PASS/WARN/FAIL); record exact branch
- LSF wall-time observed vs projected (~30 min wall expected)
- Manuscript md5 invariant preservation (PASS/WARN/FAIL)
- W2 GO/NO-GO status (W2 always fires regardless of W1 branch — W2 reads CONTEXT for downstream framing implication only)
- W3 gate disposition (FIRES/SKIPPED/DEFERRED_TO_TRACK_B per W1 outcome)
- Honest-framing-lock invariant preservation
</output>
