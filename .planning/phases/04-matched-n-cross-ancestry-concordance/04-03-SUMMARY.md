---
phase: 04-matched-n-cross-ancestry-concordance
plan: 03
subsystem: matched-n-concordance-metrics
tags: [tier-a-retention, jaccard, sign-agreement, D-02a, D-02b, D-02c, D-02d, D-02e, bootstrap]

requires:
  - phase: 04-02
    provides: bootstrap coloc_summary.tsv schema (signal_id, pph4, lead_sign_agree), coloc.rds per bootstrap
  - phase: 02-3-way-qtl-colocalization
    provides: tier_assignments.tsv (AFR Tier A locus list)
provides:
  - src/snakemake/scripts/compute_tier_a_retention.R (D-02a/c/d primary + sign + unmatched)
  - src/snakemake/scripts/compute_jaccard.R (D-02b secondary + D-02c tertiary)
  - compute_tier_a_retention + compute_jaccard_and_sign rules in matched_n.smk
  - results/matched_n/tier_a_retention.tsv (D-02a output)
  - results/matched_n/jaccard.tsv (D-02b output)
  - results/matched_n/sign_agreement.tsv (D-02c output)
affects: [04-05, phase-11-manuscript]

tech-stack:
  added: []
  patterns: [per-trait bootstrap aggregation with quantile CI, coloc.rds CS extraction for Jaccard]

key-files:
  created:
    - src/snakemake/scripts/compute_tier_a_retention.R
    - src/snakemake/scripts/compute_jaccard.R
    - tests/fixtures/matched_n/synthetic_bootstraps/create_fixtures.py
    - tests/fixtures/matched_n/synthetic_bootstraps/tier_assignments.tsv
  modified:
    - src/snakemake/rules/matched_n.smk
    - tests/test_matched_n_tier_a.py

key-decisions:
  - "Tier A criterion: max(pph4) >= 0.8 AND any(pph4 >= 0.8) across signal rows (treats each coloc.susie signal row as QTL-level evidence)"
  - "Jaccard computed over union of all CS variants per dataset (not per-signal pairing)"
  - "Sign agreement collected from coloc_summary.tsv lead_sign_agree column (not recomputed)"
  - "Snakemake rules depend on manifest as proxy for bootstrap completion (not direct expand over coloc TSVs)"

patterns-established:
  - "Pattern: R scripts with --out + --out-sign dual output for primary metric + sanity check"
  - "Pattern: synthetic fixture generator script alongside fixture files for reproducibility"

requirements-completed: []

duration: 8min
completed: 2026-04-16
---

# Phase 4 Plan 03: Concordance Metrics (D-02a Tier A retention + D-02b Jaccard + D-02c sign agreement) Summary

**Per-trait Tier A retention with bootstrap 95% CI, credible-set Jaccard at relaxed PP.H4>=0.5, sign agreement sanity check, D-02e Phase 9 joint criterion guard, unmatched concordance baseline for H7**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-16T03:00:33Z
- **Completed:** 2026-04-16T03:09:08Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- D-02a primary metric implemented: per-trait Tier A retention fraction across 100 bootstraps with 95% CI from quantiles
- D-02b secondary metric implemented: credible-set Jaccard similarity at PP.H4 >= 0.5 relaxed threshold per bootstrap
- D-02c tertiary sanity check: lead-variant sign agreement co-produced by both scripts; WARN to stderr if < 98%
- D-02d unmatched concordance baseline co-computed in retention script for H7 verdict
- D-02e guard: explicit header comments in both R scripts rejecting Phase 9 joint criterion
- 7 unit tests passing (replacing xfail stub): mean retention, CI, unmatched concordance, column schema, sign agreement, D-02e regression guard, D-02a label guard
- Synthetic fixtures: 5 loci x 5 bootstraps with known retention=0.6, verified deterministic

## Task Commits

1. **Task 1: compute_tier_a_retention.R + tests + fixtures** - `128c480` (feat)
2. **Task 2: compute_jaccard.R + Snakemake rules** - `9bca59b` (feat)

## Files Created/Modified

- `src/snakemake/scripts/compute_tier_a_retention.R` - D-02a/c/d: Tier A retention, sign agreement, unmatched baseline
- `src/snakemake/scripts/compute_jaccard.R` - D-02b/c: Jaccard at relaxed threshold, sign agreement
- `src/snakemake/rules/matched_n.smk` - Added compute_tier_a_retention + compute_jaccard_and_sign rules
- `tests/test_matched_n_tier_a.py` - 7 tests replacing xfail stub (retention, CI, unmatched, columns, sign, D-02e/D-02a guards)
- `tests/fixtures/matched_n/synthetic_bootstraps/` - Fixture generator + 25 coloc_summary TSVs + 5 unmatched + tier_assignments

## Decisions Made

- Tier A criterion checks `max(pph4) >= 0.8 AND any(pph4 >= threshold)` across all signal rows in a coloc_summary.tsv; each row from coloc.susie represents a CS pair, so any row achieving threshold counts as QTL-level evidence
- Jaccard is computed over the union of all CS variant names per dataset (not per-signal-pair matching), consistent with the "overall credible set overlap" interpretation of D-02b
- Sign agreement values are read directly from the `lead_sign_agree` column produced by run_matched_coloc.R (04-02 T3), not recomputed
- Snakemake rules use manifest.tsv as input proxy (not a full expand over all bootstrap x region x trait coloc TSVs) to avoid DAG explosion; the R scripts glob over the coloc directory at runtime

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Rscript not on default PATH in smoke_dev conda env; test harness resolves r_coloc env at `/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript` via candidate list + shutil.which fallback
- Snakemake dry-run for `results/matched_n/tier_a_retention.tsv` hits pre-existing MissingInputException on `results/phase2/tier_assignments.tsv` (not yet produced by upstream Phase 2 execution). Same pattern as 04-02 finding. Rules load correctly per `snakemake --list`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Concordance metrics complete: Plan 04-05 can assemble Table 2 from tier_a_retention.tsv + jaccard.tsv + sign_agreement.tsv + detection_probability.tsv (04-04) + rg_matrix.tsv (04-04)
- Output TSV schemas locked:
  - tier_a_retention.tsv: trait, n_afr_tier_a, mean_retention, ci95_lo, ci95_hi, n_bootstraps, unmatched_concordance
  - jaccard.tsv: trait, mean_jaccard, ci95_lo, ci95_hi, n_locus_pairs
  - sign_agreement.tsv: trait, n_loci_checked, n_sign_agree, frac_sign_agree

## Self-Check: PASSED

All 6 created/modified files verified present on disk. Both task commits (128c480, 9bca59b) verified in git log.
