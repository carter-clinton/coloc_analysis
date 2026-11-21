---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7f
subsystem: ta-r4 fine-mapping + QTL coloc (W3f review F2)
tags: [susie, credible-set-purity, determinism, d-28-unfreeze, q-f2, q-f2q]
requires: [ta-r4-W3f-none-rows-denominators]
provides: [run_susie_rss.R --exact-purity, run_qtl_coloc.R --exact-purity, production and QTL_A3/QTL_A2 argv pass it, simulation ladder n_purity, pre-fix flip measurement manifest, r4_qtl_group 30 GB]
affects: [ta-r4-W3f-qtl-sweep-gwas-pph4, W5a-W6 production fits, DRAFT (k)]
tech-stack:
  added: []
  patterns: [RNG seeded per run through R_PROFILE_USER to prove seed invariance and its negative control]
key-files:
  created:
    - tests/ta_r4/test_purity_determinism.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/purity_flip_measurement.tsv
  modified:
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - src/snakemake/scripts/run_qtl_coloc.R
    - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
    - src/python/ta_r4/commands.py
    - src/python/ta_r4/run_qtl_group_r4.py
    - config/ta_r4/cluster_slurm/config.yaml
    - tests/m3/test_source_freeze_pins.py
    - tests/ta_r4/test_unique_allele_key_guard.py
    - tests/ta_r4/test_json_cs_equals_fit_sets.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
decisions:
  - "DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze: Carter Q-F2 = A: Exact purity, third unfreeze (Recommended); third W3f lift of D-28, scope = --exact-purity only"
  - "DEC-2026-11-20-ta-r4-qtl-exact-purity-flag: Carter Q-F2Q = i: Same treatment on the QTL side (Recommended); opt-in flag, QTL_A3/QTL_A2 only"
  - "--exact-purity accepts exactly 'true' or 'false' in both scripts (the plan's 'anything but true/false stops'); the older run_susie_rss.R flags keep their t/1/yes synonyms"
  - "r4_qtl_group:mem_mb=30000 from the conservative (all live copies) exact-purity peak 19.3 GB at the PYHIN1_1q23 cap"
commits: [29de2a4d, c3c76ba2, 57ddb59d, 38e4080d, b11b10b6]  # + the 15.7f records commit
completed: 2026-11-21
---

# Phase ta-r4 Plan 15.7f: W3f purity determinism Summary

Credible-set purity no longer depends on an unseeded random draw. susieR 0.14.2 scores a set of more than 100 members
on `sample(pos, 100)`; with `--exact-purity true`, run_susie_rss.R and run_qtl_coloc.R pass `n_purity` = the number of
variants, so purity is the minimum |r| over all pairs. Production fit arms, QTL_A3 and QTL_A2 and the simulation ladder
use it; the repro arms, QTL_legacy and Track B do not, and their default paths are proven identical to the start commit.
On the 20 pilot fits the measured exposure is real (109 subsampled components) but no outcome flips: every one of those
sets has exact min |r| <= 0.024 and failed 0.5 in all 1,000 seeded draws.

## Gates

- `gate_reply.py Q-F2 --question <plan text> --sha256 57886063…c52e5a "A: Exact purity, third unfreeze (Recommended)"`
  printed the label and sha256, rc 0.
- `gate_reply.py Q-F2Q --question <plan text> --sha256 63a54f5f…ab790e "i: Same treatment on the QTL side (Recommended)"`
  printed the label and sha256, rc 0.
- Both ran before any edit (`$Q/gate_15_7f.txt`).

## Task 1: DECs and pre-fix measurement

- Start sha 78f62719 (`$Q/start_15_7f.txt`), in the test as the literal `PRE_157F_REF`.
- 29de2a4d: both DECs. Each quoted block is `cmp`-identical to its reply file.
- c3c76ba2: `manifests/purity_flip_measurement.tsv`, committed before any code change
  (`$Q/purity_flip_measure.R`, Slurm 2014394, cascadelake c020n04):
  - Every pilot panel's sha256 equals its manifest row. Every fit variable was resolved with
    variant_match.R::resolve_fit_names (allow_duplicate_rows); 0 fits stopped.
  - Identity (i): 19/19 stored sets equal the 95% set from alpha. Identity (ii): 19/19 stored purities (all sets
    <= 100 members) equal the exact all-pairs minimum within 1e-12. For the two non_converged fits the matrix is the
    regularized R / (1 + eps), as susie_rss saw it.
  - 109 components (V > 1e-9, 95% set > 100) in 12 fits, as at planning. Exact min |r| 0..0.0243. The share of
    seeds 1..1000 whose 100-member subsample has min |r| >= 0.5 is 0.000 for all 109. Kept 0/109. Demonstrated flips
    (exact >= 0.5, or a share strictly between 0 and 1): **0**.
  - Largest set 3,350 (asthma FTO_16q12 L3). 39 of the 109 duplicate an earlier component's set (susie_get_cs
    dedups them before purity).
  - Peak RSS: sacct MaxRSS 14.2 GB (/usr/bin/time 12.4 GB).
- QTL memory (`$Q/qtl_purity_mem.R`, Slurm 2014452, c021n03): PYHIN1_1q23 (15,236 variants, the largest EUR 1000G
  panel among the QTL regions), with the whole panel as the one set:
  - panel + susie_get_cs: 11.09 GB with n_purity 100, 11.09 GB with n_purity all;
  - with the copies run_qtl_coloc.R, runsusie and susie_rss hold live at the purity call: 19.26 GB with n_purity 100,
    19.26 GB with n_purity all.
  - Exact purity adds nothing measurable; the p x p copies and susie_get_cs's symmetry check dominate. Both peaks
    exceed 6 GB, so c3c76ba2 adds one resource line, `r4_qtl_group:mem_mb=30000` (ceil(19.7 GB x 1.5)).
    test_slurm_profile: 15 passed.

## Task 2 RED → GREEN

- RED (`$Q/red_15_7f.txt`, `$Q/red_15_7f.xml`, Slurm 2014603): 9 failed / 4 passed.
  - Tests 2, 3, 5, 6, 7, 9, 12, 13 failed on the defect (no flag; the simulation's purity was 0.9604 against an
    exact 0.6).
  - Tests 4, 8, 11 passed, as planned.
  - Test 10 passed. It checks the manifest committed in Task 1, not the code, so it cannot be RED once Task 1 is in.
  - Test 1 failed, but on its own non-vacuity assert: seeds 1-3 all drew the low-loading variant. It was widened to
    the 8 seeds before GREEN; the differential itself matched in RED.
- GREEN, 57ddb59d:
  - run_susie_rss.R: `--exact-purity` (default false; only true/false). With true, `ladder_policy$n_purity` is
    `nrow(subset)`, `susie_call` passes it to susie_rss, and the sweep and L-saturation calls pass
    `n_purity = nrow(R_cs)`. Without it, the calls pass susieR's own default 100.
  - run_qtl_coloc.R: `--exact-purity` (default false). With true, both runsusie calls pass
    `n_purity = length(qtl_data$snp)`. The default branch keeps the original calls literally.
  - fit_command appends `--exact-purity true` after `--require-unique-allele-key true`; qtl_command appends it after
    `--qtl-orient` for QTL_A3 and QTL_A2; simulate_coloc_r4.R adds `n_purity = length(z)` to its ladder policy.
  - Task 2 verify set, pre-repin (Slurm 2014634): 308 P / 2 S / 9 F. The 9 were the 3 freeze pins, the imported R pin
    in test_qtl_coloc_allele_join, and 5 working-tree-vs-HEAD guards; the commits cleared all of them.
    test_variant_catalog_fallback_legacy_semantics: 31 passed, no edits.
- Re-pin, 38e4080d (own commit): R_CODE_REF 13b0821 → 57ddb59. Pins 3 failed / 36 passed at the old pin, 39 passed
  after.
- Mutation NCs on the GREEN source (`$Q/mutation_nc_15_7f.py`; Slurm 2014781, M9 re-run 2015125). Each failed exactly
  its predicted tests; every file md5-restored; a 13/13 baseline ran first.
  - M1 ladder ignores the flag → 2, 3.
  - M2 sweep and L-saturation ignore the flag → 3, 5.
  - M3 susie_call drops policy n_purity → 2, 3, 9.
  - M4 simulation ladder without n_purity → 9.
  - M5 QTL first runsusie ignores the flag → 12.
  - M6 fit_command without the flag → 7.
  - M7 QTL_legacy passes the flag → 13 and test_qtl_group_runner::test_legacy_argv_is_the_exact_pre_fix_argv.
  - M8 GWAS default path made exact → 1, 4.
  - M9 QTL default call perturbed → 11. Run 1 used `prior_variance = 0.05`, which susie re-estimates away; the JSON
    did not change and nothing failed (`$Q/mutation_nc_15_7f_run1_M9_weak.txt`). With `prior_variance = 1e-4,
    estimate_prior_variance = FALSE` test 11 fails. Only the mutation changed, no code or test.
  - M10 manifest share edited → 10.
  - M11 bad value accepted as false → 6.
- DRAFT (k), b11b10b6 (`$Q/draft_15_7f.py`, old string asserted unique). test_amendment_text: 21 passed / 2 skipped.

## Default-path identity

- run_susie_rss.R: test_default_path_unchanged_without_the_flag runs the toy under 8 seeds with HEAD and with the
  script at PRE_157F_REF (`git show` into the copied root). The fit JSON is equal and the RDS md5 is equal for every
  seed. The seeds cover both outcomes of the subsample draw (purity 0.6 and 0.9604). M8 shows the test fails when the
  default path is made exact.
- run_qtl_coloc.R: test_qtl_default_path_unchanged_without_the_flag runs QTL_A3 (flag stripped) and QTL_legacy on both
  fixture features (success and no_qtl_cs) with HEAD and with the PRE_157F_REF script (sibling helpers symlinked). The
  output JSON is equal in all 4 cases. M9 shows the test fails on a changed default call.
- Repro arms, QTL_legacy, Track B: test_repro_arms_do_not_pass_exact_purity, test 13, and no diff under
  src/snakemake/rules, Snakefile, config/pipeline.yaml or sample_null_loci.py (`git diff 78f62719 HEAD`).

## Task 3: FULL

Slurm 2015198 (cascadelake c020n01, HEAD b11b10b6; `$Q/close_15_7f_2015198.out`): QUICK 839 P / 2 S; HEAVY
327 P / 5 S; PINS 39 P; FULL **2,667 = 2,614 P / 53 S / 0 F** (`$Q/full_15_7f.xml`).

Against full_15_7e.xml (`$Q/check_15_7f.txt`, `$Q/cmp_15_7f.txt`):
- 0 ids removed.
- 13 ids added, all passed: exactly the 13 new tests (`$Q/new_tests_15_7f.txt`).
- 0 outcome changes, including 0 in tests/m3.
- The 3 declared spec updates went passed → passed.

check_15_7f.py: PASS, rc 0. Its NCs FAIL with rc 1 (base as new; a synthetic failure on a declared id)
(`$Q/check_15_7f_nc.txt`). src/ and tests/ are clean.

No push, no production fit, decision_rules.yaml `locked: false`, no OSF posting, n_regions_min 7.

## Declared spec updates

tests.ta_r4.test_unique_allele_key_guard::test_default_is_pre_guard_behaviour[None]
tests.ta_r4.test_unique_allele_key_guard::test_default_is_pre_guard_behaviour[false]
tests.ta_r4.test_json_cs_equals_fit_sets::test_fit_rds_unchanged_by_the_fix

What changed: fixture helpers only. `test_unique_allele_key_guard._argv` also strips `--exact-purity` and its value,
and `test_json_cs_equals_fit_sets.pre_fix_argv` also strips `--exact-purity`, because their pre-fix substrates
(1f77128, 656529a) reject the new option. No assertion changed. All three ids went passed → passed. No test in
test_qtl_group_runner.py needed a change (test_fixed_arms_argv checks `got[-2:] == ["--output", "OUT"]`, which still
holds); test_legacy_argv_is_the_exact_pre_fix_argv is unchanged.

## New tests (13)

tests/ta_r4/test_purity_determinism.py:
1. test_default_path_unchanged_without_the_flag (r4_heavy)
2. test_exact_purity_equals_the_full_pairwise_minimum (r4_heavy)
3. test_exact_purity_is_invariant_to_the_rng_seed (r4_heavy)
4. test_subsample_purity_depends_on_the_seed_without_the_flag (r4_heavy; negative control)
5. test_sweep_and_l_saturation_use_exact_purity (r4_heavy)
6. test_bad_exact_purity_value_stops (r4_heavy)
7. test_fit_command_passes_exact_purity_for_production_arms
8. test_repro_arms_do_not_pass_exact_purity
9. test_simulation_ladder_uses_exact_purity (r4_heavy)
10. test_flip_measurement_manifest_matches_its_recount (r4_heavy)
11. test_qtl_default_path_unchanged_without_the_flag (r4_heavy)
12. test_qtl_exact_purity_equals_the_full_pairwise_minimum (r4_heavy)
13. test_qtl_command_passes_exact_purity_except_legacy

## Deviations from Plan

1. **More tests are r4_heavy than the plan marked.** The plan marked 1, 10, 11, 12. Tests 2-6 and 9 also run Rscript
   (the frozen script on the toy, or the simulation harness), so they carry r4_heavy like the repo's other script runs.
   Ids and the count are unchanged.
2. **Seeds through R_PROFILE_USER.** The scripts set no seed. The tests seed R per run with an Rprofile, which shows the
   flag's seed invariance (3) and the default path's seed dependence (4).
3. **Test 2 reads the purity value, test 12 reads retention.** The GWAS toy keeps its set at 0.5 either way, so the
   purity value itself shows exact vs subsample. The QTL output records no purity, so test 12 uses a toy whose exact
   min |r| is 0.441: with the flag n_cs_qtl is 0 under all 8 seeds; without it some seeds keep the set.
4. **Test 10 recounts independently.** It reads the sumstats window with tabix (the measurement read the whole file),
   then recomputes the largest and smallest rows. It also checks every listed file exists and every panel sha256.
5. **Test 10 was not RED** at Task 2 step 1, and test 1 failed RED on its non-vacuity check (see RED above).
6. **QTL memory: two measurements.** The plan's (panel + susie_get_cs, 11.09 GB) plus one with every live copy
   (19.26 GB). The resource line uses the larger, 30000 MB. Both show exact purity adds no measurable memory at the
   cap. They also show the 8 GB default would not hold a full-panel bridged set at PYHIN1_1q23 on the default path;
   the new line covers that too.
7. **Mutation NCs added** (15.7c-e precedent); M9 run 1 was too weak (recorded above).
8. **The FULL close job was submitted with plain sbatch and polled to completion**, not `sbatch --wait`.

## Known Stubs

None.

## Self-Check: PASSED
