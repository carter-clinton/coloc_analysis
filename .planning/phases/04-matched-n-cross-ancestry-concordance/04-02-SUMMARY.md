---
phase: 04-matched-n-cross-ancestry-concordance
plan: 02
subsystem: matched-n-bootstrap-engine
tags: [se-inflation, bootstrap, susie-refit, coloc-susie, matched-n, D-01a, D-01b, D-01c]

requires:
  - phase: 01-coloc-susie-fine-mapping-spine
    provides: run_susie_rss.R (reused verbatim), .fit.rds schema, susie_policy.yaml
  - phase: 04-01
    provides: config/matched_n.yaml, matched_n.smk skeleton, manifest rule
provides:
  - src/python/se_inflation.py (inflate_se, draw_z_bootstrap, compute_seed)
  - src/snakemake/scripts/bootstrap_driver.py (per-bootstrap Z resampling + SuSiE refit)
  - src/snakemake/scripts/run_matched_coloc.R (per-bootstrap coloc.susie wrapper)
  - run_matched_bootstrap + run_matched_coloc rules in matched_n.smk
affects: [04-03, 04-04, 04-05, phase-11-manuscript]

tech-stack:
  added: []
  patterns: [SE-inflation analytic rescaling, independent-Z bootstrap, Phase 1 script verbatim reuse]

key-files:
  created:
    - src/python/se_inflation.py
    - src/snakemake/scripts/bootstrap_driver.py
    - src/snakemake/scripts/run_matched_coloc.R
    - tests/test_matched_n_bootstrap_driver.py
  modified:
    - src/snakemake/rules/matched_n.smk
    - tests/test_matched_n_se_inflation.py

key-decisions:
  - "SE-inflation formula: SE_matched = SE_EUR * sqrt(N_EUR / N_AFR) per D-01a"
  - "Bootstrap Z: Z_b ~ N(beta_hat/SE_matched, 1) per variant independently per D-01b"
  - "Phase 1 run_susie_rss.R reused verbatim via subprocess (no modifications)"
  - "AFR discovery .fit.rds held immutably fixed on input side per D-01c"
  - "Failure path: minimal .rds sentinel matching Phase 1/9 convention"
  - "Temp pseudo-sumstats culled after SuSiE fit (retention policy per CONTEXT)"

patterns-established:
  - "Pattern: SE-inflation for matched-N power correction (Mahajan 2022 convention)"
  - "Pattern: bootstrap_driver.py as Python orchestrator calling R via subprocess"
  - "Pattern: run_matched_coloc.R thin wrapper with D-02c lead_sign_agree hook"

requirements-completed: []

duration: 8min
completed: 2026-04-16
---

# Phase 4 Plan 02: Bootstrap Engine (SE-inflation + SuSiE refit + coloc.susie per bootstrap) Summary

**SE-inflation math (sqrt(N_EUR/N_AFR)), independent-Z bootstrap resampling with deterministic seeds, SuSiE refit via Phase 1 script reuse, per-bootstrap coloc.susie with fixed AFR discovery fits**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-16T02:28:28Z
- **Completed:** 2026-04-16T02:36:28Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- D-01a SE-inflation formula implemented and unit-tested: `SE_matched = SE_EUR * sqrt(N_EUR / N_AFR)` with input validation (positive N, N_AFR <= N_EUR)
- D-01b bootstrap Z resampling: `Z_b ~ N(beta_hat/SE_matched, 1)` per variant independently, deterministic seeds via `seed = seed_base * trait_id + bootstrap_idx`
- Bootstrap driver (`bootstrap_driver.py`) loads EUR sumstats, inflates SE, draws Z, writes pseudo-sumstats, invokes Phase 1 `run_susie_rss.R` verbatim via subprocess
- D-01c coloc.susie re-estimation (`run_matched_coloc.R`) pairs bootstrap EUR-matched `.fit.rds` with immutable AFR discovery `.fit.rds`; outputs per-signal TSV with PP.H4, CS sizes, lead variants, and D-02c direction-of-effect sign agreement
- Snakemake rules `run_matched_bootstrap` and `run_matched_coloc` wired in `matched_n.smk` (listed by `snakemake --list`)
- 17 unit tests passing (11 SE-inflation + 6 bootstrap driver)

## Task Commits

1. **Task 1: se_inflation.py + unit tests** - `9d143cd` (feat)
2. **Task 2: bootstrap_driver.py + tests** - `19854c4` (feat)
3. **Task 3: matched_n.smk rules + run_matched_coloc.R** - `072eefb` (feat)

## Files Created/Modified

- `src/python/se_inflation.py` - D-01a/D-01b math: inflate_se, draw_z_bootstrap, reconstruct_pseudo_sumstats, compute_seed
- `src/snakemake/scripts/bootstrap_driver.py` - Per-bootstrap orchestrator: EUR sumstats -> SE inflation -> Z draw -> pseudo-sumstats -> SuSiE refit
- `src/snakemake/scripts/run_matched_coloc.R` - Per-bootstrap coloc.susie wrapper with AFR fit fixed, D-02c hook, per-signal TSV
- `tests/test_matched_n_se_inflation.py` - 11 tests replacing xfail stub (identity, scaling, validation, determinism, reconstruction, seeds)
- `tests/test_matched_n_bootstrap_driver.py` - 6 tests (CLI parsing, column normalization, Rscript mock integration, seed determinism)
- `src/snakemake/rules/matched_n.smk` - Added run_matched_bootstrap + run_matched_coloc rules + read_trait_afr_n helper

## Decisions Made

- SE-inflation formula exactly as specified in D-01a: `SE_matched = SE_EUR * sqrt(N_EUR / N_AFR)`
- Phase 1 `run_susie_rss.R` invoked verbatim via subprocess (at `src/legacy/region_analysis/scripts/run_susie_rss.R`)
- AFR discovery `.fit.rds` is a read-only input to `run_matched_coloc` -- never written or modified (D-01c)
- SuSiE failure path writes minimal `.rds` sentinel with `susie_failure` class for downstream detection
- `read_trait_afr_n` helper in matched_n.smk reads from `config/trait_sample_sizes.yaml` with hardcoded fallback from Phase 0/4 data access audit
- run_matched_coloc.R uses `coloc::coloc.susie(fit_afr, fit_eur)` with AFR as dataset 1 (discovery) and EUR-matched as dataset 2 (replication)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Snakemake dry-run for `results/matched_n/coloc/t2d/chr10_114p/bootstrap_1/coloc_summary.tsv` hits pre-existing `InputFunctionException` in `ld_reference.smk` (`build_ld_rds` does not recognize `chr10_114p` region ID). This is DEF-RO7-01 from STATE.md, not caused by this plan. The matched_n rules themselves resolve correctly (`snakemake --list` confirms both rules load).
- `run_susie_rss.R` is at `src/legacy/region_analysis/scripts/run_susie_rss.R` (not `src/snakemake/scripts/`); bootstrap_driver.py defaults to the correct legacy path.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Bootstrap engine complete: Plans 04-03 through 04-05 can implement concordance metrics, LDSC r_g, Table 2 assembly
- run_matched_bootstrap produces per-bootstrap `.fit.rds` at `FITS_ROOT/{trait}/{region}/bootstrap_{b}/eur_matched.fit.rds`
- run_matched_coloc produces per-bootstrap `coloc_summary.tsv` at `results/matched_n/coloc/{trait}/{region}/bootstrap_{b}/`
- TSV schema locked: signal_id, pph4, pph3, pph2, pph1, pph0, cs_afr_size, cs_eur_size, lead_variant_afr, lead_variant_eur, lead_sign_agree

## Self-Check: PASSED

All 6 created/modified files verified present on disk. All 3 task commits (9d143cd, 19854c4, 072eefb) verified in git log.
