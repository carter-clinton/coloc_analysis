---
phase: 09-replication-in-independent-cohorts
plan: 03
subsystem: replication-signal-dispatch
tags: [python, pandas, r, susieR, coloc, winnerscurse, fiqt, snakemake, pytest, testthat, manifest]

# Dependency graph
requires:
  - phase: 09-replication-in-independent-cohorts
    provides: "Plan 09-01 skeleton (replication.smk §C+§E-FIQT TODO rules + test scaffolding) + Plan 09-02 harmonized_grch37/{cohort}/{trait}.tsv.gz canonical outputs"
  - phase: 01-finemapping
    provides: ".fit.rds schema (annotate_susie-augmented susie_rss objects) + config/susie_policy.yaml (L=10, coverage=0.95, retry ladder)"
  - phase: 02-3-way-qtl-colocalization
    provides: "tier_assignments.tsv schema (signal_id, gwas_trait, gwas_ancestry, region, gene_id, tissue, qtl_source, tier)"
provides:
  - "Plan 09-03 — replication manifest (data/processed/replication/manifest.tsv) crossjoining Phase-1 credible-set SNPs + Phase-2 Tier A+B triples against cohort panels"
  - "run_replication_susie.R — SuSiE-RSS re-fit on replication cohort per region; coloc::runsusie(suffix=2) so fit consumes straight into coloc.susie(discovery_fit, replication_fit)"
  - "run_fiqt.R — winnerscurse::FDR_IQT wrapper emitting beta_FIQT + se_FIQT for D-04a winner's-curse-corrected discovery effects"
  - "4 real Snakemake rules in §C + §E-FIQT (build_replication_manifest, fit_replication_susie, run_fiqt_on_discovery; run_replication_coloc_susie remains §D-scoped for Plan 09-04)"
  - "12 new tests (7 pytest + 5 testthat) enforcing D-02b, D-05, D-05c, D-08"
affects: [09-04-coloc-fiqt-meta, 09-05-cojo-aggregate]

# Tech tracking
tech-stack:
  added:
    - "winnerscurse (amandaforde/winnerscurse @ 2ed00bb) — R GitHub package; FDR_IQT function implementing Bigdeli 2016 FIQT correction"
  patterns:
    - "Manifest builder crossjoins a config-driven panel registry (config/replication_cohorts.yaml → panels.primary_eur / primary_afr / generalization_eas) against two discovery inputs (credible_set_summary.tsv + tier_assignments.tsv) to emit one row per (signal × cohort) target. MVP-style nested-strata availability is surfaced via a 3-arg _cohort_trait_available(cfg, trait, ancestry_key) that returns False for trait-level NOT_RELEASED_AS_OF_2026-04 statuses AND for ancestry strata missing from per-ancestry-nested trait dicts."
    - "Manifest-driven Snakemake dispatch: fit_replication_susie / run_fiqt_on_discovery rules look up runtime parameters (sumstats path, region, ld_panel) from manifest.tsv via _manifest_lookup(signal_id, cohort, field) resolver — same pattern as Phase-2 _qtl_coloc_manifest_row. Rules resolve to `MISSING` sentinels when the manifest doesn't yet exist so Snakemake can still dry-run the DAG before data arrives."
    - "Lazy GitHub install of R package: run_fiqt.R checks requireNamespace(winnerscurse) at source-time and invokes remotes::install_github('amandaforde/winnerscurse', upgrade='never') on first use — no manual post-conda step. r-remotes already in envs/r_coloc.yml from Phase 0."
    - "testthat script-path resolver: because testthat::test_file() chdir's into the test file's directory, guard helpers walk up a candidate list of relative paths (`../../../src/...`, `../../src/...`, `src/...`) to locate project-root artifacts. Pattern documented in test_fiqt.R for future R tests."

key-files:
  created:
    - "src/python/build_replication_manifest.py (313 lines) — build_manifest entry point + _resolve_rep_path + _ld_panel_for + _cohort_trait_available"
    - "src/snakemake/scripts/run_fiqt.R (111 lines) — apply_fiqt wrapper + CLI entrypoint"
    - "src/snakemake/scripts/run_replication_susie.R (234 lines) — fit_replication_susie + load_policy + ld_panel_path + parse_region + CLI entrypoint"
    - "tests/phase9/test_replication_manifest.py (217 lines, 7 tests)"
  modified:
    - "tests/phase9/r/test_fiqt.R — promoted from Wave-1 RED scaffold with skip_if_not guards into 5 real tests with 100-row null background for BH-shrinkage verification"
    - "src/snakemake/rules/replication.smk — replaced 3 TODO stubs (build_replication_manifest, fit_replication_susie, run_fiqt_on_discovery) with real rules; added _replication_manifest_row + _manifest_lookup helpers"
    - "envs/r_coloc.yml — documented winnerscurse lazy-install convention (D-04a)"

key-decisions:
  - "Panel-driven manifest routing rather than hardcoding cohort lists: build_replication_manifest reads config['panels']['primary_eur']['cohorts'] and config['panels']['generalization_eas']['cohorts'] + signal_scope='tier_ab_only' directly. New cohorts added to the YAML appear in the manifest without code changes."
  - "BBJ generalization layer gated by signal_scope='tier_ab_only' at the config level (not hardcoded in manifest builder). Layer 2 (Tier A+B triples) appends BBJ iff discovery_ancestry matches panels.generalization_eas.discovery_ancestry AND signal_scope == 'tier_ab_only'. D-05c compliance surfaces through YAML, not Python literals."
  - "Tolerant missing-input handling: build_manifest accepts empty / missing credible_set_summary.tsv and tier_assignments.tsv and returns an empty DataFrame. Lets the replication Snakemake rule execute before upstream Phase 1/2 outputs exist (enabling dry-run / DAG smoke testing)."
  - "run_replication_susie.R reuses config/susie_policy.yaml verbatim (D-08) rather than maintaining a Phase-9 policy fork. load_policy() reads the single YAML, applies %||% fallbacks for missing keys, and passes (L, coverage, min_abs_corr) to coloc::runsusie. Retry ladder is simplified to primary + min_abs_corr=0.1 fallback (vs Phase-1's three-stage ladder) because replication re-fits are typically less edge-case-prone — the discovery fit has already passed the three-stage ladder."
  - "se_FIQT column is passthrough equal to raw SE. winnerscurse::FDR_IQT does not emit a shrunken SE (only beta_FIQT). Downstream consumers want a stable 2-column (beta_FIQT, se_FIQT) addition; emitting raw SE as se_FIQT documents the correct statistical treatment (SE of the winner's-curse-corrected estimator is the same as raw SE to first order; formal SE shrinkage would require a parametric bootstrap per row)."
  - "apply_fiqt normalizes column case to lowercase at entry (winnerscurse requires exact `rsid`, `beta`, `se` column names). Handles both canonical UPPERCASE (harmonized sumstats schema) and lowercase (winnerscurse convention) without caller intervention."
  - "%||% operator placement matters: defined BEFORE the CLI block that uses it (M-2 revision from checker iteration 2). Also required a length/list guard because yaml::read_yaml returns multi-element lists — `is.na(list_value)` is vectorized and breaks `||`. Guard `length(a) == 1L && !is.list(a)` routes scalars through the NA/''/empty path and leaves lists alone."

patterns-established:
  - "Manifest schema for Phase 9: 14 columns — signal_id, signal_class, discovery_trait, discovery_ancestry, region, lead_snp, gene_id, tissue, qtl_source, cohort, cohort_ancestry, is_generalization, discovery_fit_path, replication_sumstats_path, ld_panel. Two signal_class values (credible_set_SNP for Layer 1; tier_A_triple / tier_B_triple for Layer 2). Layer 1 leaves gene/tissue/qtl_source blank; Layer 2 leaves lead_snp blank."
  - "Canonical replication outputs layout: results/replication/fits/{signal_id}_{cohort}.fit.rds (SuSiE fits), results/replication/fiqt/discovery_beta_fiqt.tsv (FIQT output). Plan 09-04 inherits these paths."
  - "R package lazy-install with GitHub SHA pinning: track the resolved SHA in the SUMMARY's key-decisions + docs/methods_fragment (after first successful install) rather than in the script — keeps the script future-proof when upstream advances."

requirements-completed: []

# Metrics
duration: 13min
completed: 2026-04-14
---

# Phase 09 Plan 03: Replication Manifest + SuSiE Re-fit + FIQT

**One Python manifest builder, two R analytical wrappers, one env update, and three real Snakemake rules bind Phase-1 `.fit.rds` + Phase-2 `tier_assignments.tsv` to the Phase-9 harmonized cohort sumstats — the first wave that produces signal-scoped (not file-scoped) outputs.**

## Performance

- **Duration:** ~13 min wall clock (03:47:50Z → 04:00:30Z)
- **Tasks:** 2 / 2 (all real, no checkpoints)
- **Files created:** 4
- **Files modified:** 3
- **Commits:** 3 (1 RED test + 2 task GREEN)
- **Test outcomes:** 7 new pytest + 5 new testthat; 44 pytest phase9 passed + 5 xfailed

## Accomplishments

- **`build_replication_manifest.py`** — 313-line Python manifest builder. Reads Phase-1 credible-set summary + Phase-2 tier_assignments.tsv + replication_cohorts.yaml; crossjoins against `panels.primary_eur` / `primary_afr` / `generalization_eas`; enforces D-02b (Tier C excluded), D-05 (ancestry-matched routing), D-05c (BBJ tier_ab_only), D-08 (LD panel routed per cohort ancestry). Emits 14-column manifest TSV. Tolerates missing / empty discovery inputs (returns empty DF) so Snakemake can dry-run the DAG before upstream phases complete.
- **`run_replication_susie.R`** — 234-line SuSiE-RSS re-fit wrapper using `coloc::runsusie(suffix=2)` so the .fit.rds is immediately consumable by `coloc.susie(discovery_fit, replication_fit)` in Wave 4. Reuses Phase-1 `config/susie_policy.yaml` verbatim (D-08). CLI: `key=value` arg parsing; routes LD panel via `ld_panel_path(ld_panel, region)` lookup; two-stage retry ladder (primary call + `min_abs_corr=0.1` fallback).
- **`run_fiqt.R`** — 111-line winner's-curse correction wrapper. Wraps `winnerscurse::FDR_IQT` (amandaforde/winnerscurse @ 2ed00bb); lazy-installs via `remotes::install_github` on first use. Emits `beta_FIQT` + `se_FIQT` columns; passes a self-test on z=10 (shrinkage < 10%) and z=1.5 in a 100-row null background (shrinkage > 50%).
- **Snakemake §C + §E-FIQT** — 3 TODO placeholders promoted to real rules: `build_replication_manifest`, `fit_replication_susie`, `run_fiqt_on_discovery`. `grep -c 'TODO plan 09-03' src/snakemake/rules/replication.smk` → 0. Added `_replication_manifest_row` + `_manifest_lookup` helpers mirroring Phase-2's `_qtl_coloc_manifest_row` pattern.
- **Threat mitigations in place:**
  - T-09-05 (Validation: manifest file paths): Manifest resolves `replication_sumstats_path` via `_resolve_rep_path` to the Wave-2 canonical layout; Snakemake rule inputs declare the resolved path so missing files fail the rule (not silently drop signals).
  - T-09-12 (Tampering: winnerscurse pinned SHA): Resolved commit SHA `2ed00bb119a5445e6a2985c0b6bf37a3068b9560` documented in this summary + key-decisions; `upgrade="never"` in the lazy-install prevents further pulls.
  - T-09-13 (Validation: D-05 asymmetric panels): Tests `test_afr_never_finngen`, `test_eur_never_mvp_afr`, `test_bbj_only_for_tier_ab` + `test_tier_ab_triple_dispatches_to_bbj` guard the routing.
  - T-09-14 (Integrity: SuSiE convergence silent failure): `tryCatch` retry ladder with `min_abs_corr=0.1` fallback; no silent empty fit.

## Task Commits

1. **RED — failing manifest tests** — `bf3c460` (test)
2. **Task 1 GREEN — build_replication_manifest.py + §C rules** — `925deb9` (feat)
3. **Task 2 — run_replication_susie.R + run_fiqt.R + §E-FIQT rule + testthat** — `1a051d0` (feat)

## Files Created / Modified

See frontmatter `key-files.created` and `key-files.modified`.

## Decisions Made

See `key-decisions` in frontmatter — 7 decisions captured:
1. Panel-driven manifest routing (not hardcoded cohort lists)
2. BBJ generalization gated by YAML `signal_scope`, not Python literal
3. Tolerant missing-input handling in `build_manifest`
4. `run_replication_susie.R` reuses Phase-1 susie_policy.yaml verbatim; simplified 2-stage retry ladder
5. `se_FIQT` passthrough column (winnerscurse emits no shrunken SE)
6. `apply_fiqt` normalizes column case to lowercase at entry
7. `%||%` operator placement + length/list guard for multi-element YAML values

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's single-row FIQT tests cannot shrink**
- **Found during:** Task 2 validation against real winnerscurse::FDR_IQT API.
- **Issue:** The plan's testthat cases created single-row DataFrames at z=1.5 and expected `beta_FIQT / beta_raw < 0.8`. But `winnerscurse::FDR_IQT` applies Benjamini-Hochberg FDR correction across rows — with n=1, BH is a no-op and the row passes through at its raw beta. Single-row tests can therefore never exhibit shrinkage.
- **Fix:** Constructed realistic multi-entry test frames (focal signal + 100-row null-distributed background at z ~ 0 / se=0.05). In that context BH multiplicity shrinks a z=1.5 focal row to ~0.5% of raw while keeping a z=10 focal row at ~95% of raw. Thresholds adjusted: high-z expect `> 0.90`; low-z expect `< 0.5`.
- **Files modified:** `tests/phase9/r/test_fiqt.R`
- **Verification:** 5 testthat tests pass (1 benign data.table R-version warning).
- **Committed in:** `1a051d0`

**2. [Rule 1 - Bug] `%||%` operator throws on multi-element YAML values**
- **Found during:** Task 2 source-smoke of `run_replication_susie.R`.
- **Issue:** The plan's `%||%` definition was `if (is.null(a) || is.na(a) || identical(a, "")) b else a`. When `a` is a list (like `yaml::read_yaml()$susie`), `is.na(a)` returns a length-N vector and `||` raises "'length = N' in coercion to 'logical(1)'".
- **Fix:** Gated the NA/'' check behind `length(a) == 1L && !is.list(a)` so only scalar inputs take that path. Lists and vectors bypass to `return(a)` after the length/NULL gate.
- **Files modified:** `src/snakemake/scripts/run_replication_susie.R`
- **Verification:** `load_policy(config/susie_policy.yaml)` returns a list of scalars; CLI block source-loads cleanly.
- **Committed in:** `1a051d0`

**3. [Rule 1 - Bug] testthat::test_file() chdir breaks `skip_if_not(file.exists(...))` guard**
- **Found during:** First testthat run — all 5 tests skipped even though `src/snakemake/scripts/run_fiqt.R` existed.
- **Issue:** `testthat::test_file("tests/phase9/r/test_fiqt.R")` changes cwd to `tests/phase9/r/` for the duration of the test. The Wave-1 scaffold's `file.exists("src/snakemake/scripts/run_fiqt.R")` always evaluates False after that chdir.
- **Fix:** Replaced single-path check with a candidate-list resolver (`.run_fiqt_path()`) that walks up relative paths `../../../src/...`, `../../src/...`, `src/...` and returns the first hit. Source() also routed through that helper so the actual sourcing location stays valid.
- **Files modified:** `tests/phase9/r/test_fiqt.R`
- **Verification:** `.run_fiqt_path()` returns `../../../src/snakemake/scripts/run_fiqt.R` when testthat runs; 5 tests execute.
- **Committed in:** `1a051d0`

### Out-of-scope discoveries (NOT fixed)

None — all deviations were directly caused by this plan's changes.

---

**Total deviations:** 3 auto-fixed (all Rule 1 bugs); 0 deferred.

## Issues Encountered

- `winnerscurse` is CRAN-absent (amandaforde/winnerscurse on GitHub only); the r_coloc env already ships `r-remotes` from Phase 0 so the lazy install works. Phase 1's `.r_lib_phase1/` CRAN cache is writable and served as the install target for the smoke check.
- Phase-1 and Phase-2 outputs don't exist on disk yet (`results/fine_mapping/` and `results/qtl_coloc/` are empty directories). `build_manifest` degrades gracefully to an empty manifest — this is the expected state until the upstream phases produce data. When they do, the existing rule dependencies (`credset = "results/fine_mapping/credible_set_summary.tsv"` + `tiers = "results/qtl_coloc/tier_assignments.tsv"`) automatically trigger a manifest rebuild.
- Testthat's cwd-munging (see Deviation #3) is a known footgun; the candidate-list resolver pattern is the cleanest fix that works from both `Rscript -e 'testthat::test_file(...)'` (direct) and future `testthat::test_dir()` invocations.

## User Setup Required

None. winnerscurse installs automatically on first Snakemake invocation of `run_fiqt_on_discovery` via the lazy-install block in `run_fiqt.R`. The conda env (`envs/r_coloc.yml`) already ships `r-remotes`.

## Next Phase Readiness

Plan 09-04 (coloc.susie re-estimation + effect-size test + IVW meta) can begin immediately. It consumes:
- `data/processed/replication/manifest.tsv` (driver for per-signal × per-cohort rules)
- `results/replication/fits/{signal_id}_{cohort}.fit.rds` (output of `fit_replication_susie`)
- `results/replication/fiqt/discovery_beta_fiqt.tsv` (output of `run_fiqt_on_discovery`)
- `results/fine_mapping/{signal_id}.fit.rds` (Phase-1 discovery fits)

Plan 09-04 will:
- Assemble `results/replication/fiqt/discovery_signals.tsv` (credible-set SNPs ∪ Tier A+B triples)
- Implement `run_replication_coloc_susie` (remaining §D TODO) — pairs discovery + replication fits through `coloc.susie`
- Implement `compute_per_cohort_effect_size_test` + `ivw_meta_aggregate` (§E TODO)

## Known Stubs

None — all rules produced in this wave dispatch real work against canonical paths. The `run_replication_coloc_susie` rule (scope-adjacent but §D) remains a `TODO plan 09-04` placeholder per plan boundary.

## Self-Check: PASSED

Verified present:
- FOUND: `src/python/build_replication_manifest.py`
- FOUND: `src/snakemake/scripts/run_fiqt.R`
- FOUND: `src/snakemake/scripts/run_replication_susie.R`
- FOUND: `tests/phase9/test_replication_manifest.py`
- FOUND: `tests/phase9/r/test_fiqt.R` (modified from Wave-1 scaffold)
- FOUND: `src/snakemake/rules/replication.smk` (3 TODO 09-03 stubs replaced)
- FOUND: `envs/r_coloc.yml` (winnerscurse lazy-install documented)

Verified commits:
- FOUND: `bf3c460` (RED manifest tests)
- FOUND: `925deb9` (Task 1 GREEN)
- FOUND: `1a051d0` (Task 2 GREEN)

Verified behavior:
- `pytest tests/phase9 --tb=short -q` → 44 passed, 5 xfailed
- `Rscript -e 'testthat::test_file("tests/phase9/r/test_fiqt.R", reporter="summary")'` → 5 passed, 1 benign warning
- `snakemake --list | grep -E "build_replication|fit_replication|run_fiqt"` → 3 rules visible
- `grep -c 'TODO plan 09-03' src/snakemake/rules/replication.smk` → 0
- winnerscurse pinned commit SHA: `2ed00bb119a5445e6a2985c0b6bf37a3068b9560`

---
*Phase: 09-replication-in-independent-cohorts*
*Completed: 2026-04-14*
