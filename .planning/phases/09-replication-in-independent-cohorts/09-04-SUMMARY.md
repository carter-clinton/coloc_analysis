---
phase: 09-replication-in-independent-cohorts
plan: 04
subsystem: replication-coloc-effect-size-meta
tags: [r, coloc, susieR, metafor, python, scipy, pandas, snakemake, pytest, testthat, bonferroni, ivw, fiqt, posthoc-power]

# Dependency graph
requires:
  - phase: 09-replication-in-independent-cohorts
    provides: "Plan 09-03 manifest + fit_replication_susie results/replication/fits/*.fit.rds + run_fiqt_on_discovery results/replication/fiqt/discovery_beta_fiqt.tsv"
  - phase: 01-finemapping
    provides: "Phase 1 discovery .fit.rds at results/fine_mapping/*.fit.rds (consumed by run_replication_coloc_susie.R via manifest.discovery_fit_path)"
  - external:
      package: "metafor"
      provides: "rma.uni(method='FE') IVW fixed-effect meta; installed CRAN into .r_lib_phase1/"
      usage: "aggregate_replication_meta.R line 42"
provides:
  - "Plan 09-04 — coloc.susie re-estimation wrapper producing results/replication/coloc/{signal_id}_{cohort}.coloc.json with PP.H4 sweep booleans at 0.5 / 0.7 / 0.8 / 0.9"
  - "per-cohort effect-size test producing results/replication/effect_size/{cohort}.tsv (Bonferroni + same-direction + post-hoc power + joint criterion)"
  - "collect_replication_effect_sizes.py producing results/replication/effect_size_raw/{cohort}.tsv (I-5 producer — makes the effect-size-raw input explicit, not implicit)"
  - "IVW meta script producing results/replication/meta/ivw_meta.tsv via metafor::rma.uni(method='FE') grouped by (signal_id × cohort_ancestry)"
  - "Replication §D + §E fully implemented (grep 'TODO plan 09-04' → 0 hits)"
affects: [09-05-cojo-aggregate]

# Tech tracking
tech-stack:
  added:
    - "metafor (CRAN) — installed into .r_lib_phase1/ for IVW fixed-effect meta via rma.uni(method='FE'); was absent from Phase 1 env despite being listed in envs/r_coloc.yml (the env file doesn't drive the .r_lib_phase1 cache — new R deps need install.packages into R_LIBS_USER)"
    - "scipy (pip) — installed into smoke_dev for scipy.stats.norm in posthoc_power; smoke_dev had pandas but no scipy"
  patterns:
    - "Output-schema mirroring across failure paths: run_replication_coloc_susie.R emits the SAME 4 sweep column keys (replicated_pph4_{0.5,0.7,0.8,0.9}) whether coloc.susie succeeded or failed — failure path sets them to NA. This lets Plan 09-05's master-table join be uniform; consumer rules never have to branch on coloc_succeeded to decide which columns to expect."
    - "Single tryCatch wrapping BOTH readRDS + coloc.susie (not two nested ones): a missing .fit.rds file is treated identically to a coloc.susie convergence error — both yield coloc_succeeded=FALSE with the error message preserved. Simpler code, uniform failure surface (T-09-16 mitigation)."
    - "Per-cohort (not per-signal) output key on compute_per_cohort_effect_size_test: the Bonferroni denominator IS the number of signals in that cohort, so materializing a single TSV per cohort keeps the denominator computation single-source. Plan 09-05 Task 2 concatenates the per-cohort tables."
    - "Textbook IVW smoke verification embedded in the Snakemake script: aggregate_replication_meta.R was smoke-tested inline against the closed-form textbook expectation (β1=0.2/se1=0.05, β2=0.18/se2=0.04 → meta β=0.1878, se=0.0312) BEFORE committing — metafor's FE weights match the hand-calculated IVW to 4 decimal places."
    - "Fixture-based testthat for coloc wrappers: deterministic .rds fixtures (mock_disc + mock_rep built via runsusie on identity-LD z-scores with shared causal) committed to tests/phase9/fixtures/ — testthat suite no longer needs to regenerate them from scratch and thus doesn't depend on Phase-1 data being present."

key-files:
  created:
    - "src/snakemake/scripts/run_replication_coloc_susie.R (151 lines) — run_replication_coloc(disc_fit_path, rep_fit_path, signal_id, cohort, pph4_thresholds, output_json) wrapper with PP.H4 sweep JSON output; single tryCatch covering readRDS + coloc.susie"
    - "src/snakemake/scripts/aggregate_replication_meta.R (133 lines) — ivw_meta_per_signal + aggregate_ivw using metafor::rma.uni(FE); groups by (signal_id × cohort_ancestry); excludes is_generalization=TRUE rows (D-05c); emits empty-header table if no signals qualify"
    - "src/python/compute_per_cohort_effect_size_test.py (159 lines) — compute_bonferroni + check_same_direction + posthoc_power + compute_joint_criterion + process_cohort end-to-end; CLI for Snakemake rule"
    - "src/python/collect_replication_effect_sizes.py (142 lines, I-5 producer) — per-cohort raw effect-size collector: lead-SNP match in Wave-2 harmonized sumstats, region-min-P fallback; graceful degradation to empty rows for missing sumstats files"
    - "tests/phase9/test_bonferroni.py (162 lines, 12 tests) — covers all 4 pure functions + process_cohort smoke"
    - "tests/phase9/r/gen_coloc_fixtures.R (47 lines) — one-shot deterministic fixture generator (seed=42, identity LD, shared causal at SNP 10); committed output fixtures are <3 KB each"
    - "tests/phase9/fixtures/mock_disc.fit.rds (2994 bytes, new) — runsusie-fit discovery SuSiE object"
    - "tests/phase9/fixtures/mock_rep.fit.rds (2983 bytes, new) — runsusie-fit replication SuSiE object"
  modified:
    - "tests/phase9/r/test_coloc_replication.R — promoted Wave-1 RED scaffold into 3 testthat tests: sweep-booleans (GREEN), error-path coloc_succeeded=FALSE (GREEN), preserved TCF7L2 smoke (skip-guarded)"
    - "tests/phase9/test_meta_ivw.py — added test_aggregate_ivw_script_present + test_aggregate_ivw_uses_metafor (T-09-17 mitigation enforcing metafor::rma.uni + FE method via static grep)"
    - "src/snakemake/rules/replication.smk — replaced 3 TODO placeholders (run_replication_coloc_susie, compute_per_cohort_effect_size_test, ivw_meta_aggregate) with real rules; added collect_replication_effect_sizes (new rule upstream of the effect-size test)"
    - ".gitignore — added exception `!tests/**/fixtures/*.rds` under the global `*.rds` rule so deterministic test fixtures can be committed"

key-decisions:
  - "readRDS + coloc.susie in ONE tryCatch (T-09-16 mitigation): a missing discovery fit file is handled identically to a coloc convergence error — both produce coloc_succeeded=FALSE with error preserved. Uniform failure surface simplifies Plan 09-05 master-table joins."
  - "Failure-path JSON emits the SAME sweep column keys as success-path (set to NA): downstream join operations never have to branch on coloc_succeeded to decide column schema. Chose this over an 'omit sweep columns on failure' contract because the latter forces every consumer to check and fill."
  - "Per-cohort (not per-signal) output for compute_per_cohort_effect_size_test: the Bonferroni denominator = number of signals tested IN THIS COHORT. Producing one TSV per cohort keeps the denominator computation single-source (single n_in_cohort) and avoids recomputing the count per signal."
  - "metafor::rma.uni(method='FE') over hand-rolled IVW: metafor's FE-weights match textbook IVW to 4 decimals (smoke-verified); also gives QE / I² / CI for free if reviewers ask for heterogeneity diagnostics later. Hand-rolled code would ship less and require more tests."
  - "IVW meta groups by (signal_id, cohort_ancestry), not just signal_id: T-09-17 mitigation — EUR FinnGen/GBMI-EUR/MVP-EUR meta never mixes with AFR MVP-AFR/GBMI-AFR meta. BBJ (EAS, is_generalization=TRUE) is explicitly excluded so generalization rows cannot contaminate primary-replication meta."
  - "collect_replication_effect_sizes.py materialized as a standalone script + rule (I-5 revision from plan iteration 2): the plan draft had compute_per_cohort_effect_size_test consuming `effect_size_raw/{cohort}.tsv` without a producer. Split into (collect) → (test) so the DAG is complete before any real data arrives; both rules dry-run cleanly with empty manifest."
  - "Fixture .rds files committed to git via .gitignore exception (`!tests/**/fixtures/*.rds`): deterministic coloc replication tests need paired discovery/replication SuSiE fits, and regenerating them on every test run would require runsusie to converge every time (known flaky for near-null z-scores). Committing <3KB files is far cheaper in operation and keeps CI deterministic."
  - "posthoc_power returns NaN (not 0 or 1) on invalid input (NaN β, se<=0): distinguishes 'could not compute' from 'genuinely zero power'. Callers can then pd.isna() filter without losing low-power real signals."

patterns-established:
  - "Output layout for Plan 09-04 §D/§E: results/replication/coloc/{signal_id}_{cohort}.coloc.json (per-pair JSON), results/replication/effect_size_raw/{cohort}.tsv (per-cohort raw), results/replication/effect_size/{cohort}.tsv (per-cohort tested), results/replication/meta/ivw_meta.tsv (single meta table for all signals × ancestries). Plan 09-05's master table will left-join on (signal_id, cohort)."
  - "Single tryCatch per analytical wrapper (not nested): readRDS and the analysis call go inside the SAME block. Simpler than catching readRDS separately, and the user-visible error message still distinguishes the two failure modes via conditionMessage()."
  - "Testing pure functions in Python with pytest + thin CLI wrappers: the analytical core (compute_bonferroni, check_same_direction, posthoc_power, compute_joint_criterion, process_cohort) is 5 pure functions; pytest hits each directly + one integration test (process_cohort end-to-end). CLI wrapper uses the same functions; no parallel implementations."

requirements-completed: []

# Metrics
duration: 18min
completed: 2026-04-14
---

# Phase 09 Plan 04: coloc.susie + Bonferroni + IVW Meta Summary

**Two R wrappers (coloc.susie re-estimation; metafor FE meta) + one Python pure-function module (Bonferroni / same-direction / post-hoc power / joint criterion) + one I-5 producer script + four real Snakemake rules close §D and §E of the Phase 9 replication pipeline — the analytical core of D-03a (joint criterion), D-03b (PP.H4 sweep), D-06b (IVW meta), and RESEARCH pitfalls #4 (per-cohort Bonferroni) + #5 (post-hoc power).**

## Performance

- **Duration:** ~18 min wall clock
- **Tasks:** 2 / 2 (all real, no checkpoints)
- **Files created:** 8 (+2 binary .rds fixtures)
- **Files modified:** 3
- **Commits:** 4 (2 RED + 2 GREEN — full TDD)
- **Test outcomes:** 16 new tests all passing (12 pytest Bonferroni + 4 pytest IVW + 2 testthat coloc); 58 phase9 pytest passed + 5 xfailed (no regressions)

## Accomplishments

- **`run_replication_coloc_susie.R`** — 151-line coloc.susie wrapper. Single-tryCatch failure handling so missing fit files and coloc errors both yield `coloc_succeeded=FALSE` with the error message preserved. JSON output mirrors Phase 1 `run_coloc_susie.R` schema plus the 4 PP.H4 sweep booleans at {0.5, 0.7, 0.8, 0.9} per D-03b. Best-pair row promoted via `which.max(PP.H4.abf)` (Pattern 6 Option A inherited from Phase 1 01-04).
- **`aggregate_replication_meta.R`** — 133-line IVW FE meta wrapper via `metafor::rma.uni(method='FE')`. Groups by (signal_id × cohort_ancestry) enforcing D-06b ancestry-matched meta (T-09-17). Excludes `is_generalization=TRUE` rows (BBJ, D-05c). Smoke-verified inline: β1=0.2/se1=0.05 + β2=0.18/se2=0.04 → meta β=0.1878, se=0.0312 — matches textbook to 4 decimals.
- **`compute_per_cohort_effect_size_test.py`** — 159-line pure-function module. Four public functions (`compute_bonferroni`, `check_same_direction`, `posthoc_power`, `compute_joint_criterion`) + one merger (`process_cohort`). Bonferroni uses per-cohort denominator (pitfall #4); post-hoc power uses `scipy.stats.norm` with NaN guards (pitfall #5); joint criterion = Bonferroni AND `replicated_pph4_<threshold>` (D-03a).
- **`collect_replication_effect_sizes.py`** — 142-line I-5 producer making the effect-size-raw input explicit. Reads manifest + Wave-2 harmonized sumstats; matches on lead SNP first, then region-min-P fallback; graceful empty-row output for missing files so the DAG dry-runs before real data.
- **Snakemake §D + §E fully implemented** — 4 rules real, 0 TODOs remaining:
  - `run_replication_coloc_susie` (§D) — 1 JSON per (signal × cohort)
  - `collect_replication_effect_sizes` (§E raw) — 1 TSV per cohort
  - `compute_per_cohort_effect_size_test` (§E test) — 1 TSV per cohort
  - `ivw_meta_aggregate` (§E meta) — 1 TSV total
- **Threat mitigations in place:**
  - T-09-15 (Validation: Bonferroni denominator): `compute_bonferroni(n_in_cohort)` uses per-cohort denominator exclusively; `test_bonferroni_denominator` + `test_bonferroni_rejects_zero` guard.
  - T-09-16 (Integrity: silent coloc failure): single `tryCatch` wraps readRDS + coloc.susie; failure emits `coloc_succeeded=FALSE` with preserved error + NA sweep columns; `test_coloc_replication.R::coloc_succeeded=FALSE` test guards.
  - T-09-17 (Validation: cross-ancestry meta): `aggregate_replication_meta.R` groups by `cohort_ancestry` AND excludes `is_generalization=TRUE`; `test_aggregate_ivw_uses_metafor` enforces via static check.
  - T-09-18 (Validation: FIQT on replication β): `run_fiqt.R` from Plan 09-03 is only wired into `run_fiqt_on_discovery` rule; this wave does NOT apply FIQT to replication β anywhere — verified by `grep -r 'apply_fiqt' src/` only matching the discovery-side rule.

## Task Commits

1. **RED — failing coloc replication tests + fixture generator** — `c2c3582` (test)
2. **Task 1 GREEN — coloc.susie wrapper + PP.H4 sweep JSON + §D rule** — `942d34b` (feat)
3. **RED — failing Bonferroni + IVW meta tests** — `95fe392` (test)
4. **Task 2 GREEN — effect-size module + metafor IVW + §E rules** — `f68d8fe` (feat)

## Files Created / Modified

See frontmatter `key-files.created` / `key-files.modified`.

## Decisions Made

See `key-decisions` in frontmatter — 8 decisions captured:
1. Single tryCatch wrapping both readRDS + coloc.susie (uniform failure surface)
2. Failure-path JSON emits same sweep column keys as success-path
3. Per-cohort (not per-signal) output for effect-size test (single-source Bonferroni denom)
4. metafor::rma.uni(method='FE') over hand-rolled IVW
5. IVW meta groups by (signal_id × cohort_ancestry); BBJ excluded
6. collect_replication_effect_sizes.py materialized as standalone I-5 producer
7. .rds fixtures committed via .gitignore exception for deterministic testing
8. posthoc_power returns NaN on invalid input (distinguishable from zero power)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] metafor R package absent from .r_lib_phase1/**
- **Found during:** Task 2 pre-execution env check.
- **Issue:** The Phase 1 CRAN cache at `.r_lib_phase1/` did not have `metafor` installed despite the package being listed in `envs/r_coloc.yml`. The env file drives Snakemake conda envs, but the interactive CRAN cache for direct `Rscript -e '...'` tests is a separate library path.
- **Fix:** `install.packages("metafor", repos="https://cloud.r-project.org", lib=Sys.getenv("R_LIBS_USER"))` into `.r_lib_phase1/`. Installed successfully (Matrix 4.4.3 warning benign).
- **Files modified:** none (side-effect install into user R library)
- **Verification:** `Rscript -e 'requireNamespace("metafor")'` → TRUE.

**2. [Rule 3 - Blocking] scipy absent from smoke_dev Python env**
- **Found during:** Task 2 pre-execution env check.
- **Issue:** `posthoc_power` uses `scipy.stats.norm`; `smoke_dev` had pandas + numpy but no scipy.
- **Fix:** `pip install scipy` into the smoke_dev env.
- **Files modified:** none (side-effect install)
- **Verification:** `python -c 'from scipy.stats import norm; norm.ppf(0.975)'` → 1.96.

**3. [Rule 3 - Blocking] Global `*.rds` gitignore blocks fixture commits**
- **Found during:** Task 1 RED commit — `git add` reported ignored files.
- **Issue:** The project `.gitignore` has a blanket `*.rds` rule to avoid committing Phase 1 pipeline outputs (which can be hundreds of MB). That same rule blocks the 2-3 KB deterministic test fixtures we need committed for CI reproducibility.
- **Fix:** Added `!tests/**/fixtures/*.rds` exception below the `*.rds` line. Narrow scope — only RDS files under any `tests/.../fixtures/` directory are allowed through.
- **Files modified:** `.gitignore`
- **Committed in:** `c2c3582`

**4. [Rule 1 - Bug] Plan's fixture generator used raw susieR::susie_rss, not coloc::runsusie**
- **Found during:** Task 1 RED — test design review.
- **Issue:** The plan's Step 4 `gen_coloc_fixtures.R` used `susieR::susie_rss(z, R, L, n)` directly. But `coloc.susie` needs S3 dispatch on `class("susie")` AND the `coloc:::annotate_susie` metadata (Phase 1 01-04 A6 resolution). A raw `susie_rss` fit would work in most cases but occasionally fails the `coloc::runsusie` contract — inconsistent with how Wave 3's `fit_replication_susie` generates its fits.
- **Fix:** Fixture generator uses `coloc::runsusie(D, suffix=N, L=L, coverage=0.95)` with a full coloc-format `D` list (beta, varbeta, snp, position, type, LD, N, sdY). This matches Wave-3 production fit semantics exactly — the test really is testing what Plan 09-04 runs in production.
- **Files modified:** `tests/phase9/r/gen_coloc_fixtures.R`
- **Committed in:** `c2c3582`

### Out-of-scope discoveries (NOT fixed)

None — all deviations were Rule 3 (blocking) environment setups or Rule 1 (bug) plan-spec corrections directly in scope.

---

**Total deviations:** 4 (3 Rule 3 blocking, 1 Rule 1 bug fix); 0 deferred.

## Issues Encountered

- `metafor` + `scipy` env gaps (see Deviations #1–#2) are one-time installs; the conda-env files (`envs/r_coloc.yml` + pip install in smoke_dev) are the source of truth for Snakemake rule runtime, so the interactive-test installs don't need to be replayed in prod workflow.
- Wave-3's TCF7L2 smoke test in `test_coloc_replication.R` remains skip-guarded: it needs Phase 1 discovery `.fit.rds` on disk and a cohort-specific replication fit. Both remain pre-execution. The new fixture-based tests validate the wrapper without that dependency.
- `aggregate_replication_meta.R` produces one meta TSV per rule invocation (one global output file, not per-signal). This matches D-06b semantics ("IVW meta across ancestry-matched cohorts" is a single operation) and lets Plan 09-05's master table join on `signal_id`. An alternative pattern — one file per `(signal_id, ancestry)` — was considered and rejected because the downstream master-table rule would need to scatter-gather hundreds of small files.

## User Setup Required

None. `metafor` and `scipy` installed into user R library / pip env as part of execution; both Snakemake conda envs (`envs/r_coloc.yml`) already carry these declarations so real Snakemake runs will resolve them from conda.

## Next Phase Readiness

Plan 09-05 (COJO sensitivity + master-table aggregation) can begin immediately. It consumes:
- `results/replication/coloc/{signal_id}_{cohort}.coloc.json` (per-pair PP.H4 sweep JSONs)
- `results/replication/effect_size/{cohort}.tsv` (per-cohort tested tables with joint criterion)
- `results/replication/effect_size_raw/{cohort}.tsv` (upstream of the test)
- `results/replication/meta/ivw_meta.tsv` (one meta TSV across signals × ancestries)
- `results/replication/fiqt/discovery_beta_fiqt.tsv` (Plan 09-03 output)

Plan 09-05 will:
- Implement COJO slct + joint prep / run (GCTA dependency)
- Assemble `results/replication/master_table.tsv` (signal × cohort long format per D-07)
- Assemble `results/replication/cross_ancestry_generalization_tier_ab.tsv` (BBJ-only per D-05c)
- Assemble the two supplementary tables (cojo_sensitivity, replication_holdout)

## Known Stubs

None — all new rules dispatch real work against canonical paths. The `ivw_meta_aggregate` rule requires `results/replication/effect_size/per_cohort_combined.tsv` (a Plan 09-05 aggregator that concatenates per-cohort effect_size files into a single long table); the filename is declared as a rule input so Snakemake will enforce it when real data arrives, and Plan 09-05 Task 2 owns its producer.

## Self-Check: PASSED

Verified present:
- FOUND: `src/snakemake/scripts/run_replication_coloc_susie.R`
- FOUND: `src/snakemake/scripts/aggregate_replication_meta.R`
- FOUND: `src/python/compute_per_cohort_effect_size_test.py`
- FOUND: `src/python/collect_replication_effect_sizes.py`
- FOUND: `tests/phase9/test_bonferroni.py`
- FOUND: `tests/phase9/r/gen_coloc_fixtures.R`
- FOUND: `tests/phase9/r/test_coloc_replication.R` (modified from Wave-1 scaffold)
- FOUND: `tests/phase9/fixtures/mock_disc.fit.rds`
- FOUND: `tests/phase9/fixtures/mock_rep.fit.rds`
- FOUND: `src/snakemake/rules/replication.smk` (all 3 Plan 09-04 TODOs replaced; 1 new rule added)

Verified commits:
- FOUND: `c2c3582` (RED coloc + fixtures + gitignore)
- FOUND: `942d34b` (Task 1 GREEN — coloc.susie wrapper)
- FOUND: `95fe392` (RED Bonferroni + IVW)
- FOUND: `f68d8fe` (Task 2 GREEN — effect-size + IVW + rules)

Verified behavior:
- `pytest tests/phase9/test_bonferroni.py tests/phase9/test_meta_ivw.py -q` → 16 passed
- `Rscript -e 'testthat::test_file("tests/phase9/r/test_coloc_replication.R", reporter="summary")'` → 2 passed + 1 skipped (TCF7L2 pre-execution)
- `grep -c 'TODO plan 09-04' src/snakemake/rules/replication.smk` → 0
- Aggregate IVW textbook smoke (inline): beta=0.1878, se=0.0312 (expected: 0.1878, 0.0312 to 4dp)
- `pytest tests/phase9 --tb=line -q --ignore=tests/phase9/r` → 58 passed, 5 xfailed (no regressions)

---
*Phase: 09-replication-in-independent-cohorts*
*Completed: 2026-04-14*
