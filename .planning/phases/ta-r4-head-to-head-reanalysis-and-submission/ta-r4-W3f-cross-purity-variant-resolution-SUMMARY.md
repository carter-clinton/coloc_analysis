---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7c
subsystem: ta-r4 cross-panel purity (W3f review F10)
tags: [cross-purity, variant-identity, position-and-alleles, make-unique, shared-matcher]
requires: [ta-r4-W3f-completeness-by-identity]
provides: [src/snakemake/scripts/ta_r4/variant_match.R, cs_cross_purity.R member resolution through the fit's sumstats / catalog / panel, run_aggregation catalog and panel check per fit]
affects: [ta-r4-W3f-a1-allvars-secondary, W7 aggregation E4 cross-purity]
tech-stack:
  added: []
  patterns: [rebuild an identifier from its producer and compare exactly before writing tests against it, extract a classification into a shared file and pin the caller to its pre-extraction source by a literal ref]
key-files:
  created:
    - src/snakemake/scripts/ta_r4/variant_match.R
    - tests/ta_r4/test_cs_cross_purity_resolution.py
  modified:
    - src/snakemake/scripts/ta_r4/cs_cross_purity.R
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - src/python/ta_r4/run_aggregation.py
    - tests/ta_r4/test_cs_cross_purity.py
    - tests/ta_r4/test_reporting_widened.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "Route 1 keeps only sumstats rows that run_susie_rss.R's allele-aware panel match would keep (exact or swapped on a non-duplicated panel key, usable alleles, no palindromic SNV), so a palindromic or dropped row never makes a base look multi-key"
  - "The fit panel is checked with the catalog: run_aggregation._cross_purity compares the fit JSON's ld_file_declared (else ld_matrix) with paths.panel_path(fit_arm, region) as well as variant_catalog_path with paths.catalog_path(route, region); a missing fit JSON is a mismatch"
  - "The region id is derived inside _rscript_purity (run_qtl_group_r4.region_ids over regions_csv); the runner receives region_safe and regions_csv"
commits: [e1422df1]  # + the 15.7c records commit
completed: 2026-11-20
---

# Phase ta-r4 Plan 15.7c: W3f cross-panel purity variant resolution Summary

Cross-panel purity now finds each credible-set member through what the fit was built from, and looks it up in the other panel by position and alleles. Before, `cs_cross_purity.R` matched a fit name against the other panel's SNP_ID, or failing that read the name as CHR:POS, and never checked alleles (F10).

- **variant_match.R** (new, sourced by both scripts): `norm_allele`, `missing_allele` and `complement`, plus the N2 classification moved out of `run_coloc_pair_r4.R` as `classify_alleles` and `match_at_position`. It also adds `panel_alleles`, `panel_keeps` and `resolve_fit_names`. `resolve_fit_names` recovers each name's allele key in route order. Route sumstats: rows in the window whose SNP_ID equals the base, whose key is in the catalog and which the fit panel keeps. Route panel: fit-panel rows with that SNP_ID (the rsid override). Route chrpos: the base read as CHR:POS, with exactly one fit-panel row.
- **The `.N` rule.** A suffixed name whose base resolves to one key is a duplicate row. It is refused with `DUPLICATE_ROW` unless `--allow-duplicate-rows` is given; that flag is for measuring pre-15.5a fits and is never passed for production. A base that resolves to k > 1 keys is refused in production: the member is not matched, it is counted in `n_refused_multi_key`, and the set gets the note `refused_multi_key`. Under the flag, the (N+1)-th key in catalog order is taken; N ≥ k gives `BAD_OCCURRENCE`.
- **cs_cross_purity.R** now requires `--fit-sumstats`, `--fit-catalog`, `--region-id`, `--regions-csv` and `--fit-panel`. It reads the window with run_susie_rss.R's rule. Each key is located in `--panel` by position and alleles: exact, swapped, or the strand complement of a non-palindromic SNV. One match means present, more than one is `AMBIGUOUS`, none means absent. `DUPLICATE_ROW`, `BAD_OCCURRENCE`, `UNRESOLVED` and `AMBIGUOUS` are errors even under `--allow-absent`. New output columns: `n_route_sumstats`, `n_route_panel`, `n_route_chrpos`, `n_match_exact`, `n_match_swapped`, `n_match_strand` and `n_refused_multi_key`.
- **run_coloc_pair_r4.R** sources variant_match.R from its own directory, for Rscript and `sys.source` callers alike. `map_fit_names` calls `match_at_position`; its idx, counts and messages are identical to PRE_157C_REF 0351c628.
- **run_aggregation**: `_rscript_purity` passes the fit's sumstats (`paths.sumstats_path(trait, anc, fit_arm)`), catalog (`paths.catalog_path(ARMS[fit_arm]["route"], region)`), region id, regions csv and fit panel (`paths.panel_path(fit_arm, region)`). Before any fit is scored, `_cross_purity` compares the real paths of that catalog and panel with the ones the fit JSON records. On a mismatch, FINAL raises `CrossPurityInputMismatch`, which `run_aggregation` turns into exit 3 naming the fit. DRAFT prints the mismatch and records the note `fit_inputs_mismatch` without scoring the fit. `PURITY_COLS` gains the seven new columns.

## Task 1 step 1: naming confirmed on the 20 real pilot fits (before RED)

- `planner_probes/f10_real_fit_routes.R` re-run (Slurm 2009767, read-only). Its output is byte-identical to the planning output: 33,438 names, 14,063 suffixed. Bases resolve 6,282 by the sumstats route, 22,092 by the panel route, 0 by chrpos, 0 unresolved and 0 by sumstats occurrence (0 multi-key bases). Every suffixed name duplicates its base's single key: 5,064 on the sumstats route (the probe's `bad_occurrence`) and 8,999 on the panel route (`dup_keys`).
- Exact rebuild `data/r4/tmp/w3f/q157/c157/rebuild_names.R` (same job). For each fit, an independent emulation rebuilds the names: full gunzip read of the recorded sumstats; the window; the catalog allele-key join in catalog order, with x keeping SNP_ID; the allele-aware panel match; the rsid override; blank → CHR:POS; make.unique. The result is compared with `colnames(fit$lbf_variable)` by `identical()`. **REBUILD 20/20 exact** (`c157/rebuild_names.tsv`). Override and make.unique both carry weight: they touch 22,092 and 14,063 names. 0 names are blank.

## Task 1 RED → GREEN (e1422df1)

- RED (`red_15_7c.txt` / `.xml`): the start script, accepting and ignoring the new options, with variant_match.R absent. 13 F / 5 P, exactly the planned split. RED: 1, 2, 4, 6, 7, 10–14, 16–18. Green: 3, 5, 8, 9, 15. Why the five were green:
  - 3: the swapped member has the same SNP_ID, and |r| ignores sign.
  - 5: the fixture's ids agree with the physical answer. The `!pal` guard cannot change presence, because a palindromic pair's complement is its own swap.
  - 8: the member is absent by id and by position.
  - 9: identity panels, with names matching by id.
  - 15: the CHR:POS name is unique in the other panel.
  - Each RED failed for the expected reason: wrong n_present, rc 0 where an error was due, the old `AMBIGUOUS ... by CHR:POS` (13), `UNMATCHED rsM.1` (17), empty runner inputs (12), and a missing variant_match.R (10, 11, 18).
- Test 2's fixture first used C/T against A/G. That is the strand complement, so the new rule correctly called the member present. The fixture was changed to A/C, and RED was re-confirmed against the start script with that fixture (`c157/red_test2_refixture.txt`: ('3','') ≠ ('2','partial_present')).
- GREEN: the 16 non-heavy tests pass locally. Heavy tests 10 and 18 passed under Slurm 2009922 (cascadelake). Test 18 measured 29 regions, both directions: 167,956 allele-agreeing pre-15.7c matches, all 167,956 kept on the same row; no count is asserted. Task 1 `<verify>` ran under `sbatch --wait` (Slurm 2009987, cascadelake c020n03), 7 files: **114 P / 2 S** (the 2 S are test_amendment_text's existing skips).
- Mutation NCs (`mutation_nc_15_7c.txt`): 9 mutations, each failing exactly its predicted tests, with the source md5-restored after each. The mutations: no strand; ambiguity takes the first candidate; duplicate row accepted; multi-key chosen by order in production; no panel route; no chrpos route; catalog check skipped; `--fit-panel` not passed; no allele check. Run 1 (`mutation_nc_15_7c_run1_mispredicted.txt`) had one wrong prediction and one bad old string, neither a code defect. For M5 (no panel route), test 5 also fails: its palindromic members are not kept by the fit panel, so they resolve through the panel route. M9's old string had the wrong indentation, and the count assertion caught it. The M5 fix changed only the prediction; no fixture changed. Test 5's members rs1 and rs3 are A/T SNVs. run_susie_rss.R's allele-aware match drops palindromic SNVs, so `panel_keeps` never lets the sumstats route claim them, and they resolve through the fit-panel rsid. With that route removed they become UNRESOLVED, and test 5 fails. Real allele-aware fits contain no palindromic names. The panel route is what resolves such names in non-allele-aware fits.
- Test 11 is test 10's negative control: mutated classification in an in-memory copy of variant_match.R. It passes in GREEN: `same` is TRUE before the mutation and FALSE after.
- No-weaken AST (`noweaken_15_7c.txt`) PASS. All 5 test functions in test_cs_cross_purity.py are unchanged. In test_reporting_widened.py, only `test_cross_purity_is_status_agnostic` changed, and its 7 assertions are identical and in the same order. The NC (`noweaken_15_7c_nc.txt`, `== 6` → `>= 6`) FAILs.
- DRAFT (e) E4: one replacement (`draft_15_7c.py`), old string unique. test_amendment_text 21 P / 2 S.

## Task 2: FULL

- FULL (Slurm 2010023, cascadelake c020n03, HEAD e1422df1, clean tree; `close_15_7c_2010023.out`):
  - QUICK 820 P / 2 S (+16); HEAVY 315 P / 5 S (+2); PINS 39 P.
  - FULL **2,636 = 2,583 P / 53 S / 0 F** (`data/r4/tmp/w3f/q157/full_15_7c.xml`).
- Per id vs full_15_7b.xml (`check_15_7c.txt`, `cmp_15_7c.txt`): removed 0; added 18, all passed, exactly the `<new_tests>` ids; outcome changes 0; tests/m3 0. All 7 declared spec updates went passed → passed. check_15_7c.py **PASS**.
- check NCs (`check_15_7c_nc.txt`): using the base as the new XML FAILs (18 missing, totals). A synthetic failure on the declared id test_cross_purity_is_status_agnostic FAILs (outcome change, failed 1, declared passed → failed).
- Files of e1422df1 and the records commit ⊆ files_modified; simulate_coloc_r4.R needed no change. The orchestrator's docs commits 927ff53e and ecf6dab7 (HANDOFF.json, STATE.md, .continue-here.md) landed during FULL. They are outside this plan, and the 15.7c STATE block supersedes their 'FULL running' block.
- No push, no production fit, decision_rules.yaml locked: false, no OSF posting, n_regions_min 7.

## Declared spec updates

tests.ta_r4.test_cs_cross_purity::test_cross_purity_against_real_panel
tests.ta_r4.test_cs_cross_purity::test_identity_panel_gives_zero_for_multi_member_sets
tests.ta_r4.test_cs_cross_purity::test_refuses_unmatched_or_ambiguous_members[dup.rds-AMBIGUOUS]
tests.ta_r4.test_cs_cross_purity::test_refuses_unmatched_or_ambiguous_members[missing.rds-UNMATCHED]
tests.ta_r4.test_cs_cross_purity::test_allow_absent_scores_present_members_and_counts_them
tests.ta_r4.test_cs_cross_purity::test_allow_absent_still_refuses_ambiguous
tests.ta_r4.test_reporting_widened::test_cross_purity_is_status_agnostic

What changed (invocation and fixture only; no assertion changed, and no expected n_present, note or purity value changed):
- test_cs_cross_purity.py, 6 ids: `_run` passes the five new arguments. BUILD writes the fit's sumstats window, catalog, fit panel (REF = A2, ALT = A1) and regions csv. `missing.rds` also moves rs1 from 1:100 to 1:101. Under the new rule a variant at the same position with the same alleles is present whatever its id, so the old id-only change (rs1 → rsZ) no longer made it absent.
- test_reporting_widened.py::test_cross_purity_is_status_agnostic: the stub runner takes the new `_rscript_purity` keyword signature. Its empty-table column list gains the seven new columns. Its fixture loop writes each scored fit's JSON (variant_catalog_path, ld_file_declared), which the per-fit catalog and panel check reads.

## New tests (18)

tests/ta_r4/test_cs_cross_purity_resolution.py: test_same_position_and_alleles_with_a_different_id_is_present, test_same_id_with_different_alleles_is_absent, test_swapped_alleles_match_and_keep_abs_r, test_strand_complement_of_a_non_palindromic_snv_matches, test_palindromic_snv_is_not_matched_by_complement, test_two_candidates_at_one_position_is_ambiguous, test_unresolved_name_is_an_error_even_with_allow_absent, test_absent_without_allow_absent_is_an_error, test_identical_panels_reproduce_the_fit_purity, test_map_fit_names_unchanged_after_extraction (r4_heavy), test_mutated_classification_breaks_the_extraction_identity, test_run_aggregation_passes_the_fit_sumstats_and_panel, test_ukb_indel_id_resolves_through_the_sumstats, test_panel_rsid_override_name_resolves_through_the_panel, test_chrpos_name_resolves_to_the_unique_fit_panel_row, test_duplicate_row_suffix_is_refused_unless_allowed, test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed, test_real_panels_new_rule_is_a_superset_of_allele_agreeing_matches (r4_heavy).

## Deviations from Plan

1. **[Rule 2] Fit-panel check added beside the catalog check.** `_cross_purity` also compares the fit JSON's ld_file_declared (else ld_matrix) with `paths.panel_path(fit_arm, region)`, and treats a missing fit JSON as a mismatch. It uses the same STOP semantics as the catalog check (FINAL exit 3; DRAFT prints, note `fit_inputs_mismatch`). Resolving members through a panel other than the one the fit read would be the same defect class as a wrong catalog.
2. **Resolver details the plan left open.** Route 1 drops rows that run_susie_rss.R's allele-aware panel match drops, as recorded under decisions. A candidate without alleles next to a compatible one is `AMBIGUOUS`, as in `match_at_position`. A key without alleles is `UNRESOLVED`. The sumstats are read with `colClasses = "character"` and POS made numeric for the window, so allele columns stay character whatever their content. The window rule is the same CHR equality and POS bounds. The region id is derived in `_rscript_purity`, not `_cross_purity`.
3. **Test 10 is marked r4_heavy.** It reads the real SH2B3 sumstats, panel and fits; the plan labelled only test 18 as heavy. The id and its outcome are unchanged, and test 11 (its NC) stays quick, on fixtures only.
4. **Fixture edits beyond "gains a sumstats window, catalog and fit panel"** (the missing.rds position and the status-agnostic fit JSONs) are listed under Declared spec updates. The no-weaken AST check PASS covers them.
5. **Overlap.** The pre-commit heavy run 2009922 was still running test 18 while mutation-NC run 1 began editing variant_match.R in place. Its PASS is not relied on: the FULL at e1422df1 re-runs both heavy tests on committed sources.

## Known Stubs

None.

## Self-Check: PASSED

These all exist: variant_match.R, test_cs_cross_purity_resolution.py, check_15_7c.py, full_15_7c.xml, rebuild_names.tsv (REBUILD 20/20 exact), red_15_7c.txt, mutation_nc_15_7c.txt (PASS), noweaken_15_7c.txt (PASS), check_15_7c_nc.txt (both FAIL) and draft_15_7c.py. Commit e1422df1 is in the log. check_15_7c.txt reads CHECK PASS.
