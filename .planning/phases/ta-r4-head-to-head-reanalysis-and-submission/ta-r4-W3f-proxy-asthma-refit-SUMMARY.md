---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7h2
subsystem: ta-r4 W3f confirmatory-floor proxy
tags: [n_regions_min, exact-purity, susieR, pilot-fits, build-check]
requires: [ta-r4-W3f-null-window-reselection]
provides: [exact-purity region-contribution proxy, asthma pilot-fit manifest, production catalog build check]
affects: [15.7i pilot-fit disclosure recount]
tech-stack:
  added: []
  patterns: [scored-matrix purity recomputation, recorded-vs-panel identity cross-check]
key-files:
  created:
    - tests/ta_r4/test_proxy_exact_purity.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/proxy_asthma_pilot_fits_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_157h2_build_check.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-mem-and-k2d-mapping-reply-2026-11-21.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7h2-drop-asthma-reply-2026-11-22.txt
  modified:
    - src/python/ta_r4/measure_fit_eligibility.py
    - .planning/DECISIONS.md
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/HANDOFF.json
decisions:
  - DEC-2026-11-20-ta-r4-proxy-asthma-refit-keep-n-regions-min-7
  - DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix
  - DEC-2026-11-21-ta-r4-proxy-k2d-identity-and-56g
  - DEC-2026-11-22-ta-r4-proxy-drop-asthma-build-mix
metrics:
  completed: 2026-11-22
---

# Phase ta-r4 Plan 15.7h2: W3f exact-purity region-contribution proxy Summary

Exact purity recomputed on each fit's scored matrix (panel R, cov2cor(R + eps·I) for regularised fits, identity for k2d)
leaves every repro set count unchanged: the proxy over the 4 non-asthma EUR traits stays A1_matched 8 / 1 / 1 and
A2_identity 3 / 2 / 5. The 20 asthma pilot commands ran (12 fits) but are kept out of the proxy because the legacy catalog is
GRCh38-framed; the production catalog is GRCh37.

## Commits (none pushed)

| Step | Commit | Content |
|------|--------|---------|
| 1 DEC | d1498dff | DEC keep n_regions_min 7, option D; Q-PROXY, Q-PROXYA, Q-PROXYB, Q-NREG quoted |
| 1b DEC | f1f17bef | DEC exact purity on the scored matrix (Q-PURITY A) |
| 2 | 265434df | asthma_pilot_commands, split commands, exact-purity proxy, CLI; 9 tests |
| 1c DEC | 563f4753 | DEC k2d 56G + identity-panel rule; Q-MEMK2D reply file |
| 2b | bcd0310a | identity iff the fit JSON records it, cross-checked against the panel; test 2 cases |
| 1d DEC | 688a6220 | DEC drop asthma (build mix); Q-DROPASTHMA reply file |
| 2c | 4f3d692a | test 5 exact-path exclusion case |
| 3 | dd5eb803 | pilot-fit manifest, build check, DRAFT row, HANDOFF value |
| records | (this commit) | LOG, STATE, PLAN-INDEX, SUMMARY |

## Results

- Split (Slurm 2025948): 8 too_many_variants, 12 fit. Pilot fits: Slurm 2026078 (2), 2036650 (k2d 9, 56G), 2036651 (routeC 9);
  all COMPLETED, policy_hash 60c195cb…, max MaxRSS 42,565,388 KiB at 48G (sample) and 33,720,796 KiB at 56G.
- Recorded proxy (Slurm 2039595): 69 fits rows equal to job 2037096's non-asthma rows; scored_matrix identity 34, regularized
  21, panel 14, unmapped 0; stored = exact everywhere; proxy table byte-identical to the committed manifest.
- Build check (Slurm 2039532): variants_r4 at GRCh37 asthma positions in the 30 of 31 regions with joined rsids (BMI_Xq24 has
  none); variants_legacy GRCh38-framed.
- 15.7i: 12 pilot fits (24 files) to count and disclose.
- FULL (Slurm 2039942): 2,691 = 2,638 P / 53 S / 0 F; vs full_15_7h.xml 0 removed, +9, 0 outcome changes; check PASS.

## Deviations from Plan

1. [Rule 4, three times] Stops handed back and answered by Carter: Q-PURITY (regularised purity), Q-MEMK2D (k2d memory, k2d
   mapping), Q-DROPASTHMA (build mix). Each became a plan amendment and a DEC.
2. Commit 2 and 2b preceded their negative-control runs so that `git diff --quiet -- src` was meaningful after each restore.
3. The R snippet runs from a script file: `Rscript -e` joins lines, so a `#` comment swallows the rest.
4. FULL ran at --mem=64G -t 06:00:00 (15.7h's close used 48G / 3 h).
5. A parent-session handoff commit (6f62b6d4) landed during FULL; checked (HANDOFF proxy value intact) and built on.

## Known Stubs

None.

## Self-Check: PASSED

Commits d1498dff, f1f17bef, 265434df, 563f4753, bcd0310a, 688a6220, 4f3d692a, dd5eb803 are ancestors of HEAD; the test file,
both manifests and both reply files exist; src/tests clean after FULL; decision_rules.yaml unchanged; nothing pushed.

## New test ids

Records completion, 15.7j, orchestrator sign-off 2026-11-25; copied from `$Q/new_tests_15_7h2.txt` (9 ids):

- `tests.ta_r4.test_proxy_exact_purity::test_exact_purity_set_counts_on_a_fixture`
- `tests.ta_r4.test_proxy_exact_purity::test_identity_ld_counts_unchanged_by_exact_purity`
- `tests.ta_r4.test_proxy_exact_purity::test_proxy_default_path_unchanged`
- `tests.ta_r4.test_proxy_exact_purity::test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir`
- `tests.ta_r4.test_proxy_exact_purity::test_split_argv_equals_the_pilot_argv_except_cap_rscript_and_output`
- `tests.ta_r4.test_proxy_exact_purity::test_proxy_reads_asthma_from_the_pilot_root_and_stops_excluding_it`
- `tests.ta_r4.test_proxy_exact_purity::test_n_regions_min_is_7`
- `tests.ta_r4.test_proxy_exact_purity::test_regularised_fit_is_scored_on_the_regularised_matrix`
- `tests.ta_r4.test_proxy_exact_purity::test_scored_matrix_label_names_the_matrix_that_matched`

## Declared spec updates

none

(Records completion, 15.7j, orchestrator sign-off 2026-11-25; check_15_7h2.py declared 0.)
