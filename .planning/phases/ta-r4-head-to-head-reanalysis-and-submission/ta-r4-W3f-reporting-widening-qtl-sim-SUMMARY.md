---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.4
slug: W3f-reporting-widening-qtl-sim
subsystem: ta-r4 aggregation, QTL export, simulation harness (W3f fix-up; review N8 drops, N9, N10, N12, N14)
tags: [w3f, row-drops, cross-purity, e6, qtl-fallback, simulation, e8]
requires: [ta-r4-W3f-signflip-region-floor-coverage]
provides: [estimands.row_drop_table, estimands.e4_no_cs_rate(rows, fits), estimands.e6_panel_contrast(rows, fits, ...) long format, estimands.SimulationIncomplete, run_aggregation.expected_sim_cells, aggregate_qtl_coloc --with-method-columns, run_qtl_group_r4 --tierable-summary, TABLES 19]
key-files:
  created: [tests/ta_r4/test_reporting_widened.py, tests/ta_r4/test_qtl_fallback_export.py, tests/ta_r4/test_sim_by_method_and_cells.py]
  modified: [src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, src/snakemake/scripts/ta_r4/cs_cross_purity.R, src/python/aggregate_qtl_coloc.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, src/snakemake/scripts/ta_r4/simulate_coloc_r4.R, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_cs_cross_purity.py, tests/ta_r4/test_estimands.py, tests/ta_r4/test_simulation_harness.py]
decisions:
  - "row_drops counts reconcile inside row_drop_table (n_output = coloc_susie + A1 + fallback + none; none = sum of none_reason classes; n_both <= n_paired_finite <= n_paired <= min outputs); a violation raises"
  - "Cross-purity allows absent CS members only for panels with different variant sets (A3_ukb<->A3_1kg, AFR504_A3<->AFR661_A3); identity and intersection pairs stay strict (UNMATCHED is an error)"
  - "QTL tiers read qtl_coloc_summary_tierable.tsv (method == coloc_susie) for every QTL arm, QTL_legacy included"
  - "Simulation cell check is strict in DRAFT too: rows per arm must equal the yaml reps; only reps_override=none is FINAL-only"
commits: [ade4e9c5, bed315d4, 4d11c047]
metrics: {completed: 2026-11-09, tasks: 3}
---

# 15.4 SUMMARY: N8 row drops, N9/N10 widened E4/E6, N12 QTL fallback export, N14 simulation

The review offered "narrow the text or widen the code" for each of these. In every case the code was widened. The
aggregation now reports where rows drop out of each contrast. Cross-purity is scored for every fit with credible sets,
whatever its status. E6 and afr_secondary report E1 to E5 plus drops. QTL fallback rows keep their label and posterior in an
exported table, and tiers use an explicit coloc_susie filter. The simulation no longer refits with R = I, reports rates
per method, and aggregation refuses an incomplete design.

## Task 1: N8, N9, N10 (ade4e9c5)
- `row_drop_table(rows, manifest, contrasts, p12_keys, a1_varset=None)`: one row per (contrast, p12 key, side x/ref). The
  columns are n_expected (manifest), n_output, n_coloc_susie, n_a1, n_fallback, n_method_none, n_none_<class> (the prefix of
  none_reason before ":"; coloc_susie_empty, coloc_susie_no_finite_h4 and fit_early_exit are always present, and any other
  class gets its own column), n_paired (outputs on both sides), n_paired_finite, n_both_have_cs and
  n_dropped_not_both_have_cs. `none_reason` was added to DOC_COLS so it reaches the rows. The function raises on an
  unknown method or on counts that do not reconcile.
- Hand-computed fixture (4 rows, A3_ukb vs A3_1kg). x: expected 4, output 4, coloc_susie 1, fallback 1, none 2
  (fit_early_exit 1, coloc_susie_empty 1). ref: output 3, coloc_susie 3. Shared: paired 3, paired_finite 2, both 1,
  dropped 1. Every cell is asserted.
- `row_drops` table: family confirmatory (2 contrasts, a1_varset from the yaml), e6 (2) and afr_secondary (3), x both p12
  keys x both sides.
- `e4_no_cs_rate(rows, fits)`: columns `level` in {pair_row, region, fit} and `denominator` ("pair rows of the arm", "pair
  rows of the arm in the region", "fits of the arm"). At fit level, n_no_cs counts fits with zero sets or an early exit,
  and n_early_exit is a separate column. The pair_row level keeps its old definition.
- Cross-purity: `CROSS_PURITY` holds the 8 (fit, panel, allow_absent) triples from the plan. `_cross_purity` iterates
  every fit of the fit arm. Notes: early_exit (status no_variants / too_many_variants, so no RDS is read),
  fit_rds_missing, panel_missing, no_cs (the RDS has no sets). It adds fit_status, n_cs_variants and n_present columns.
- cs_cross_purity.R `--allow-absent`: unmatched members are counted rather than raising an error. Purity is computed over
  the present members, with note partial_present. When fewer than min(2, size) members are present, purity is NA with
  note fewer_than_2_present. AMBIGUOUS is still an error. Without the flag, UNMATCHED is still an error (the existing
  test is unchanged).
- `e6_panel_contrast(rows, fits, rules, row_ids, contrasts, p12_keys)` returns a long table (variant_set, contrast, p12_key,
  estimand, subset, metric, value). Estimands: E1 (e1_summary plus median n_snps x / ref / diff) and E2 (e2_agreement over
  the sweep: n, a, b, c, d, kappa, observed_agreement, mcnemar_p at each threshold) and E3 (e3_reclassification), each
  on both_have_cs and all_rows; E4 (pair-row and fit no-CS counts per side); E5 (n_fits, median lambda_hat, median kriging
  outliers per side; A1 has no fits); drops (row_drop_table). afr_secondary is built by the same function.
- RED `t1_red.txt` 14F / 32P. GREEN `t1_green.txt` 46P. NC1 (`status == "ok"` restored) `t1_nc1.txt` 1F
  (test_cross_purity_is_status_agnostic). NC2 (old e6 body) `t1_nc2.txt` 2F (E1-E5 case and aggregation long-table case).
  NC3 (fallback counted as none) `t1_nc3.txt` 2F, both raising "counts do not reconcile".

## Task 2: N12 (bed315d4)
- `aggregate_qtl_coloc.py --with-method-columns` adds method, fallback_reason, none_status (the status of a method-none
  row) and pp_h0..pp_h4 (the doc's top-level values; for fallback_abf these are the fallback posteriors). PP.H*.abf
  keep summary semantics (blank for fallback). A doc without a method, or a malformed doc, is an error under the flag,
  and no output is written.
- Default output is byte-identical to 319ae8f1 (the last commit of the script before this change), checked by a
  differential test on a fixture with coloc_susie, fallback_abf and none docs. NC0 (columns added unconditionally)
  `t2_nc0.txt` 1F, that test only.
- `run_qtl_group_r4 --tierable-summary IN --out OUT` copies the header and the method == coloc_susie rows byte-for-byte.
  An empty method is an error, and nothing is written.
- ta_r4_qtl.smk: r4_qtl_aggregate writes the method-column summary and `qtl_coloc_summary_tierable.tsv`; r4_qtl_tiers
  reads the tierable file. This is pinned on the rendered `$SMK -n -p` listing (test_in_job_gate `rendered` fixture,
  r4_heavy), not on rule text.
- Tier equality on the fixture: tier, best_gwas_pph4, best_qtl_pph4 and resolving_gene/tissue/source are equal for
  every (region, ancestry). Two measured side effects are pinned in the test:
  - all_supporting_sources narrows to sources with coloc_susie rows (R1: "gtex_eqtl;gtex_sqtl" -> "gtex_eqtl").
  - In sweep mode (qtl_tiers_sweep.tsv), a region with no coloc_susie row (best PP.H4.abf NaN) used to count as Tier C,
    because NaN fails every comparison in assign_tier. It is no longer counted: n_tier_c 1 -> 0 at all 4 thresholds.
    The primary tier column is unchanged.
- run_aggregation: the `qtl_rows` table holds every row of each QTL arm's summary, with qtl_arm. In FINAL, a missing QTL
  arm summary or tier table exits 3 and nothing is written. DRAFT tolerates absence and names the missing paths on stderr.
- RED `t2_red.txt` 11F / 49P. One case passed RED for the wrong reason (argparse's "unrecognized arguments:
  --with-method-columns" contains "method"). It now requires the doc id and "no method": `t2_red2.txt` 5F / 1P.
  GREEN `t2_green.txt` 60P. Track B (tests/phase2 test_tier_assignment, test_run_qtl_coloc, test_pph4_sweep +
  test_track_b_isolation): 67P with the HEAD script (`t2_trackb_before.txt`) and 67P after (`t2_trackb_after.txt`).
  NC1 (posteriors from summary only) `t2_nc1.txt` 1F. NC2 (fallback_abf tiered) `t2_nc2.txt` 2F.

## Task 3: N14 (4d11c047)
- simulate_coloc_r4.R `fit_frozen`: when the ladder returns a NULL fit, the function returns `list(fit = NULL, status)`.
  The R = I refit block is removed. `run_rep` writes an arm with a NULL fit on either trait as method "none", with
  none_reason `fit_failed:<status_a>|<status_b>` and NA posteriors. COLUMNS gain none_reason, fit_status_a and
  fit_status_b (NA for A1).
- R unit case (stubbed run_susie_with_ladder in H$FZ that returns NULL for any non-identity R): the ladder is called once
  (no identity call), status non_converged. In run_rep, A3 is none with `fit_failed:non_converged|non_converged`, and the
  ladder calls are identity x2 + panel x2.
- `e8_simulation_rates` groups by (arm, method, scenario, gen_panel). Method-none rows are counted in n with k 0 and rate
  and CI NA. Fixture: coloc_susie (6, 3, 0.5), fallback_abf (3, 3, 1.0), none n 1.
- run_aggregation: `expected_sim_cells(repo)` reads the repo's config/ta_r4/simulation.yaml. With the committed yaml it
  returns 100 cells and reps 200 (asserted). `_sim(repo, final=)` raises SimulationIncomplete on any of: a missing or extra
  cell file; an ok cell whose rows per arm are not {A1, A2, A3: reps}; a no_qualifying_pair cell with rows; any other
  status; and, in FINAL only, reps_override != none. run_aggregation catches it: exit 3, nothing written, FINAL and DRAFT.
- RED `t3_red.txt` 13F / 35P. GREEN `t3_green.txt` 81P (this file, test_simulation_harness including its heavy cases,
  test_run_aggregation, test_estimands, test_confirmatory_completeness). NC1 (identity refit restored) `t3_nc1.txt` 2F.
  NC2 (methods pooled) `t3_nc2.txt` 2F. NC3 (cell check disabled) `t3_nc3.txt` 8F (7 incomplete-cell cases + exit 3).

## Fixture and test updates (spec changes, not weakened assertions)
- test_run_aggregation: TABLES +row_drops +qtl_rows (17 -> 19). The test is renamed
  `test_draft_writes_exactly_19_draft_tables`; the added tables are row_drops and qtl_rows. `build_tree` now writes each
  QTL arm's summary (one coloc_susie and one fallback_abf row) and tier table. It also writes its own simulation.yaml with
  exactly its two cells: CUR0 x {H3_r2_0.6, H3_r2_0.9} x gen_1kg, reps 1. The ok cell gained an A1 row. Headers now read
  `reps_override=none`. The no_qualifying_pair cell moved from CUR1 to CUR0 so the cell set is a full cartesian product.
  `final_repo` commits that yaml through write_fixture_lock as before.
- test_estimands::test_e4_no_cs_rate: the call is now `e4_no_cs_rate(rows, fit_frame([]))` and selects level ==
  pair_row. The assertions are unchanged.
- test_simulation_harness: COLUMNS gain none_reason, fit_status_a, fit_status_b.
- test_cs_cross_purity: the default run also asserts n_cs_variants / n_present / note. Two new tests cover --allow-absent.

## Close
- Slurm 1785577 (c207n05, HEAD 4d11c047, rc 0, 43m32s): plan verify T1 49P, T2 60P, T3 48P; Track B 67P.
  QUICK 644P / 2S in 181.0 s pytest (189.7 s wall). That is 612 (15.3) + 32 new: 7 test_reporting_widened,
  2 test_cs_cross_purity, 4 test_run_aggregation, 6 test_qtl_fallback_export, 13 test_sim_by_method_and_cells. It is over
  the 120 s budget (carried to 15.6). HEAVY 116P / 4S (W5a/W5b skips) in 32m51s: 115 + 1 (the rendered rule test).
  PINS 39P. FULL was not run (same §C list as 15.2/15.3).
- fsck before and after each commit: only dangling objects, no missing or broken links. Raw outputs are under
  data/r4/tmp/w3f4/.

## Deviations from Plan
1. [Rule 2] Cross-purity absent-member tolerance is behind `--allow-absent` and used only for the native and AFR504/AFR661
   pairs. The identity and intersection pairs keep UNMATCHED as an error, because there an absent member means a naming
   bug (as in N2), not a panel difference. The plan asked for NA purity below 2 present in general.
2. [Rule 2] The size-1 rule is NA when n_present < min(2, size). A fully present size-1 CS keeps purity 1, as before. A CS
   with 2 or more present but some absent gets note partial_present.
3. [Rule 2] Under --with-method-columns, a malformed JSON is an error, not a skip.
4. [Rule 2] `_sim` also rejects extra cell files, rows-per-arm mismatches, no_qualifying_pair cells with rows and unknown
   statuses, beyond the plan's missing-cell, row-count and reps_override checks.
5. The plan's tier-equality behaviour holds for the tier column. Two side effects of the explicit filter were measured
   and pinned rather than hidden: all_supporting_sources narrows, and the sweep stops counting regions without a
   coloc_susie row as Tier C. Both apply to every QTL arm, QTL_legacy included. The E7 qtl_tier section compares only
   the tier.
6. The rule wiring is tested on the rendered dry-run commands (r4_heavy) instead of on the rule's source text.
7. Three per-task code commits instead of the single combined commit in Task 3 step 4 (orchestrator instruction).
8. test_qtl_group_runner.py is in files_modified but needed no change; the tierable CLI is tested in test_qtl_fallback_export.

## Open items (not changed here)
- The DRAFT amendment text still describes the narrower code: (e) E4 ("for fits with status ok"; isect pairs only) and E6
  ("both-have-CS paired summary"); (g) ("refitted with R = I", "pooling coloc_susie and fallback_abf"); (l) ("labelled in
  per-row outputs, not tiered"); the OPEN row naming N12 and N14. Plan 15.5 owns the DRAFT text.
- The sweep side effect and all_supporting_sources narrowing (deviation 5) should be named in the DRAFT QTL paragraph.
- The 15.3 residual stands: test_lock_gate R4_DEPENDENCIES cites run_aggregation.py line numbers (descriptive strings, not
  enforced); this plan moved them again. For 15.6 (cite by quote).

## Self-Check: PASSED
: commits ade4e9c5, bed315d4, 4d11c047 exist, and the three created test files exist. The push result is recorded in the LOG.
