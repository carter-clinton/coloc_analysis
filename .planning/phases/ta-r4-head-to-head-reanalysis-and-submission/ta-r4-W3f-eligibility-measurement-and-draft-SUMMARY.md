---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5
slug: W3f-eligibility-measurement-and-draft
subsystem: ta-r4 fit eligibility / OSF amendment DRAFT
tags: [ta-r4, W3f, N1, N7, eligibility, cap, DRAFT, confirmatory_sha256]
requires: [ta-r4-W3f-reporting-widening-qtl-sim, ta-r4-W3f-catalog-dupkey-producer-and-guard]
provides: [measure_fit_eligibility module, w3f_fit_eligibility.tsv, w3f_region_contribution_proxy.tsv, DRAFT matching W3f + 15.5a code, confirmatory_sha256 recomputed]
affects: [ta-r4-W3f-ukb-panels-biallelic (15.5b), ta-r4-W3f-review-suite-and-close (15.6), W4a-T3 lock]
tech-stack:
  added: []
  patterns: [no-fit measurement (cap 0, tmp-only output, RDS lbf_variable probe), in-job input sha256 records, identity reconciliation against an independent join reproduction]
key-files:
  created:
    - src/python/ta_r4/measure_fit_eligibility.py
    - tests/ta_r4/test_measure_fit_eligibility.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_region_contribution_proxy.tsv
  modified:
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/STATE.md
decisions:
  - "No confirmatory fit can reach the 16,000 cap after 15.5a: A3_1kg and A2_identity primary rows hit 0 of 100 (measured / bound)"
  - "The M2 CHR:POS Pre-Paste row stays OPEN and points to 15.5b (Carter a1); it gates W4a-T3"
metrics:
  completed: 2026-11-18
  tasks: 3
---

# Phase ta-r4 Plan 15.5: W3f eligibility measurement and DRAFT Summary

The fixes' effect on fit eligibility was measured without fitting, on the 15.5a rebuilt catalogs. No 1000 Genomes EUR,
identity or intersection fit can reach the 16,000-variant cap. 10 of 815 production fits exceed it: 4 A3_ukb, plus 2 in
each AFR arm. The DRAFT now states this and describes the 15.5a catalog and guard change. Nothing is pushed.

## Commits

| Part | Commit | What |
|---|---|---|
| Task 1 code (2026-11-16) | f33a582c | `measure_fit_eligibility.py` + tests (60 quick + 4 heavy; 6 negative controls) |
| Task 1 proxy, Task 2 partial, Task 3 sha (2026-11-16) | c3e42237 | proxy manifest, DRAFT (c)(h)(k)(m), LOG, STATE |
| Checkpoint -> 15.5a | e9c0d400, 13b0821c, 3f4d0cb9, 30b13692 | catalog unique key, guard, R_CODE_REF, re-pin (15.5a SUMMARY) |
| Remainder | 518960d4 | w3f_fit_eligibility.tsv + DRAFT (k), (c), (m), Pre-Paste rows |
| Remainder docs | (this commit) | LOG, PLAN-INDEX, this SUMMARY (the STATE block was committed by the c62ddacd session close) |

## Task 1: measurement (remainder)

- Fresh dir `data/r4/tmp/w3f/elig_20261118/meas`. The run list was re-planned from current code: 83 tasks, the same keys as
  Slurm 1946095. The only argv change is `--require-unique-allele-key true`.
- Slurm 1968979 (cascadelake, `-t 01:00:00 --mem=32G`): 83/83 COMPLETED 0:0, max RSS 6.7 GB. summarise() accepted all 83:
  exact run list, early exits, no RDS with lbf_variable. Input sha256 matched the current pins 83/83.
  `find -L data/r4/results -newer .../meas/run.sh -type f | wc -l` = 0.
- eligibility_table() passes the bound check (n_variants <= panel n_var, 83/83). `w3f_fit_eligibility.tsv`: 815 rows
  (5 EUR arms x 145 + 3 AFR arms x 30) = 83 measured + 732 bound; 10 not eligible.

### Reconciliation (each 83 of 83; `reconcile.py`, inline and Slurm 1970719, identical output)

| Identity | Result |
|---|---|
| new n_variants == 15.5a m123_fits.tsv[new].restricted_rows | 83/83 |
| new n_variants_pre_ld == m123[new].joined_rows | 83/83 |
| m123[new].restricted_4key_extra == 0 | 83/83 |
| new n_variants == 11-16 n_variants_distinct (dedup) | 83/83 |
| new n_variants_pre_ld == 11-16 n_pre_ld_distinct | 83/83 |
| old n_variants == m123[old].restricted_rows | 83/83 |
| old - new n_variants == m123[old].restricted_4key_extra | 83/83 |
| new n_variants <= panel n_var; <= old n_variants | 83/83; 83/83 |

### Post-restriction counts above 16,000

| Arm | measured | old catalogs (1946095) | rebuilt (1968979) | m123[new] | pair rows hit |
|---|---|---|---|---|---|
| A3_1kg | 50 | 4 | 0 | 0 | 0 of 100 primary |
| A2_identity | 0 (bound, max panel 15,236) | - | 0 | 0 | 0 of 100 primary |
| A3_ukb | 15 | 6 | 4 (asthma, t2d x BMI_5q13_3, PYHIN1_1q23) | 4 | 14 of 100 primary = 2 x (10 - C(3,2)) |
| AFR661_A3 / AFR661_A2 / AFR504_A3 | 6 each | 4 each | 2 each (asthma x same 2 regions) | 2 each | 4 of 30 each = 2 x 2 |
| total | 83 | 22 | 10 = 4 + 3 x 2 | 10 | negative-control rows 0 |

- Pre-fix recount (pre-LD rows > 16,000) on the rebuilt catalogs: 11 A3_1kg fits -> 39 primary rows = 5 regions x 7 +
  CXADR_F2RL1_6p21 (1 trait) x 4. On the old catalogs it was 12 -> 42; the review counted 10 -> 35 on earlier inputs.
- Regression asthma x PYHIN1_1q23 A3_1kg: n_variants_pre_ld 40,649 (> 16,000); n_variants 12,605 <= panel 15,236
  (old catalogs 22,038). t2d: 36,582 / 12,584.
- Region-contribution proxy unchanged (c3e42237; repro fits do not read the r4 catalogs). A1_matched_vs_A3_1kg: 8 likely /
  1 unknown / 1 unlikely. A2_identity_vs_A3_1kg: 3 / 2 / 5. Both FLAG lines stand for A2 (n_regions_min 7; k <= 5).
  n_regions_min was not changed.

## Task 2: DRAFT

| Item | Code it describes | State |
|---|---|---|
| 1 status gate (N5) | `r4_lock_gate` construct + in-job | 11-09, re-checked 11-16 |
| 2 (c) in-job input sha256 (N4) | `verify_inputs`, job gate | 11-09; asthma lift pins 11-16 |
| 2b (c) one catalog row per allele key; fit refuses a repeated key | `ta_r4.catalog_unique_key`; `run_susie_rss.R --require-unique-allele-key` | **added in the remainder** |
| 3 (d) early-exit + fit-name rules (N1/N2/N8) | `run_susie_rss.R` cap stage; `map_fit_names` | 11-09; placeholders 0/0 |
| 4 (e) E2 descriptive, E4/E6 widened, completeness/coverage (N6/N9/N10) | estimands, coverage | 11-09 |
| 5 (f) n_regions_min 7 + sign-flip, 2/2^k (N7) | `contrast_stats` region_signflip | 11-09; truth table 36 re-derived |
| 6 (g) simulation by method, 100 cells (N14) | simulation harness | 11-09 |
| 7 (k) cap after restriction + measured count | `run_susie_rss.R`; this manifest | **(k) count clause added in the remainder** |
| 8 (l) QTL fallback export (N12) | `aggregate_qtl_coloc.py` | 11-09 |
| 9 (m) frozen paths + commits | `LOCKED_PATHS` (29) | + e9c0d400, 13b0821c, 30b13692 in the remainder |

- Pre-Paste: the measured-count row was rewritten from 1968979. The duplicate-key OPEN row is now **RESOLVED**, citing the
  15.5a commits. The analysis-code row gained the 15.5a commits. The M2 CHR:POS row **stays OPEN**, with a pointer to 15.5b (Carter a1).
- test_amendment_text: 21 passed, 2 skipped (FINAL/PUBLIC not written yet). Extract 4,127 words (3,998 at 37b0e9e2; 2,945
  before 15.5; target ~3,100). `CARTER-LOCK: early-exit` 0, `CARTER-LOCK: fit-name` 0, other placeholders 9.

## Task 3: sha and wave close

- confirmatory_sha256 recomputed: `9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5`, which equals the 15.3 interim value
  (old f6e6e90f…e9e3). It is recorded in the DRAFT Pre-Paste and the LOG.
- QUICK (Slurm 1970722): 738P/2S, 173.0 s pytest / 192.0 s wall. That is over the 120 s budget, already carried to 15.6.
- PINS: 39P. HEAVY: 244P/5S, 1,551 s.
- FULL (Slurm 1970723): 2,408P / 53S / 2F of 2,463 ids, 2,673 s. Per-id identical to the 15.5a FULL (0 removed, 0 added, 0 outcome changes).
  The 2 failures are the deferred `tests/m3/test_variant_catalog_fallback_legacy_semantics` pair (failing since 6c6e9546; 15.6).
- No push (the brief forbids it, overriding plan Task 3's push step).

## Deviations from Plan

1. **[Rule 3] Out dirs.** I used `elig_20261116/` and `elig_20261118/` instead of `elig/`, because a fresh dir is needed for each measurement.
   The backstop `find` used the matching run.sh.
2. **[Rule 4, resolved by Carter] Checkpoint 2026-11-16** (duplicate catalog keys) -> 15.5a -> this remainder.
3. **[Rule 2] DRAFT (c)** gained a sentence for the 15.5a catalog and guard change, which the plan's item list predates.
4. **No push**, per the remainder brief.
5. **Duplicate reconcile run.** The reconcile ran inline and as Slurm 1970719, with identical output. The official
   manifest was written by the same `summarise` command in both.

## Known Stubs

None.

## Threat Flags

None. Measurement outputs live only under data/r4/tmp/w3f (T-r4-W3f5-01). The PASTE block passes the internal and framing scans (T-r4-W3f5-02).

## Open for Carter

- DRAFT M2 CHR:POS row OPEN -> 15.5b (gates W4a-T3). 15.5b re-measures A3_ukb after the panel rebuild.
- FLAG: A2_identity_vs_A3_1kg proxy likely 3/10 contributing regions, k <= 5 < 7. n_regions_min 7 may give NON_INFORMATIVE.
- DRAFT 4,127 words vs a ~3,100 target. QUICK 192 s vs 120 s.
- 2 deferred tests/m3 failures and 6 removed ids from W4a (deferred-items.md, 15.6).

## Self-Check: PASSED

Files: measure_fit_eligibility.py, its test, w3f_fit_eligibility.tsv, w3f_region_contribution_proxy.tsv, this SUMMARY: found. Commits f33a582c, c3e42237, e9c0d400, 13b0821c, 30b13692, 518960d4: found; 30b13692 is an ancestor of HEAD.
