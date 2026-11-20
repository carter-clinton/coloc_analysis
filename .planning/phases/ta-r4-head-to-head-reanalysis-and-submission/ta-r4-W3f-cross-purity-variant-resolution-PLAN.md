---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7c
slug: W3f-cross-purity-variant-resolution
type: execute
wave: 15.7c
depends_on: ["ta-r4-W3f-completeness-by-identity"]
gap_closure: true
files_modified:
  - src/snakemake/scripts/ta_r4/variant_match.R
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R      # only if sourcing variant_match.R from run_coloc_pair_r4.R needs a path change here
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - src/python/ta_r4/run_aggregation.py
  - tests/ta_r4/test_cs_cross_purity_resolution.py
  - tests/ta_r4/test_cs_cross_purity.py
  - tests/ta_r4/test_reporting_widened.py
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-cross-purity-variant-resolution-SUMMARY.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Fit variable names follow run_susie_rss.R: the subset keeps the sumstats SNP_ID (the catalog join at :855-856 keeps x's SNP_ID; the catalog's arrives as i.SNP_ID), a CHR:POS-style id is replaced by the panel's rsid (:1124-1140), a blank id becomes CHR:POS (:1308-1312), and make.unique adds `.N` to repeats (:1313)"
    - "cs_cross_purity.R takes --fit-sumstats (paths.sumstats_path(trait, anc, fit_arm)), --fit-catalog (paths.catalog_path(ARMS[fit_arm]['route'], region), which must equal the fit JSON's variant_catalog_path: run_aggregation._cross_purity checks that per fit and a mismatch is a STOP), --region-id / --regions-csv (read through the same window rule as run_susie_rss.R's read_region) and --fit-panel, and resolves each credible-set member: base = name without a trailing `.N`; route 1: sumstats rows in the window with SNP_ID == base whose allele key is both in the fit's catalog (the run_susie_rss.R:855-856 join; the probe's !is.na(ord)) and in the fit panel; route 2: fit-panel rows with SNP_ID == base (the rsid override); route 3: base as CHR:POS with exactly one fit-panel row; the first route with a candidate is used"
    - "The `.N` rule. Duplicate row (the base resolves to one key and the name carries `.N`; the pre-15.5a catalog defect): refused with the error DUPLICATE_ROW unless --allow-duplicate-rows is given, which is for measuring pre-15.5a fits only and is never passed for production. Multi-key base (the base resolves to k > 1 keys): with --allow-duplicate-rows, `.N` selects the (N+1)-th key in catalog order (N ≥ k is an error); without it (production), the member is refused, never chosen by order: it is not matched, counted in the column n_refused_multi_key and the set gets the note refused_multi_key. No route → UNRESOLVED. DUPLICATE_ROW and UNRESOLVED are errors even under --allow-absent"
    - "The key is located in the other panel by position + alleles through the shared matcher (exact / swapped / strand complement of a non-palindromic SNV): one match = present; none = absent (counted under --allow-absent, else UNMATCHED); more than one = AMBIGUOUS"
    - "Measured at planning on the 20 real pilot fits (data/r4/measure_asthma_fix/fits/A3_1kg_newcat, pre-15.5a catalogs; probe planner_probes/f10_real_fit_routes.R, Slurm 2005234): 33,438 names, 14,063 suffixed; bases resolve 6,282 by the own sumstats (asthma, BMI), 22,092 by the panel-rsid override (every hypertension, stroke and type 2 diabetes name, part of asthma), 0 by CHR:POS, 0 unresolved; every one of the 14,063 suffixed names is a duplicated row of its base's single key (0 multi-key bases). Re-measured by the executor before RED"
    - "With identical fit and other panels and credible sets of ≤ 100 members, every set's min_abs_corr equals the fit's own purity exactly (must-be-identity)"
    - "map_fit_names in run_coloc_pair_r4.R, now calling variant_match.R, returns idx and counts identical to the source at the literal PRE_157C_REF on the fit-name fixtures and the SH2B3 hypertension × stroke case (589 names); a mutated classification in an in-memory copy of variant_match.R makes that comparison fail"
    - "On the committed panels (read-only, r4_heavy), the new rule matches every member the current rule matches with agreeing alleles; no count is asserted"
    - "The 18 ids in <new_tests> pass; FULL vs full_15_7b.xml: 0 removed, added == <new_tests>, 0 outcome changes; 2,636 = 2,583 P / 53 S / 0 F"
  artifacts:
    - path: "src/snakemake/scripts/ta_r4/variant_match.R"
      provides: "norm_allele, missing_allele, complement, classify_alleles, match_at_position, resolve_fit_names(names, sumstats_window, catalog_order, fit_panel, allow_duplicate_rows)"
    - path: "src/snakemake/scripts/ta_r4/cs_cross_purity.R"
      provides: "--fit-sumstats / --fit-catalog / --region-id / --regions-csv / --fit-panel resolution; route and match-kind count columns"
  key_links:
    - from: "cs_cross_purity.R and run_coloc_pair_r4.R::map_fit_names"
      to: "variant_match.R"
      via: "source() relative to the calling script's directory"
      pattern: "variant_match.R"
    - from: "run_aggregation._rscript_purity"
      to: "cs_cross_purity.R --fit-sumstats --fit-catalog --region-id --fit-panel"
      via: "paths.sumstats_path(trait, ancestry, fit_arm), paths.catalog_path(route, region) and paths.panel_path(fit_arm, region)"
      pattern: "--fit-sumstats"
---

<objective>
Close F10 (CONFIRMED, `cs_cross_purity.R:27-36`): `panel_index` matches a fit name to the other panel's SNP_ID, else
tries the name as CHR:POS, never resolving it through what the fit was built from and never checking alleles. Effect:
descriptive E4 cross-panel purity (A3_ukb ↔ A3_1kg); no confirmatory number. Against the UKB panel the current rule
misses 251 of 86,035 1000G variants present by position and alleles and accepts 8 name matches with differing alleles
(`planner_probes/f10_panels.out`).

Fit names come from the fit's own sumstats (with the panel-rsid override and make.unique), as the coordinator
verified at `run_susie_rss.R:855-856, 1124-1140, 1306-1311`; the earlier catalog-first probe was wrong and is
superseded. This plan resolves members through the fit's sumstats and panel and extracts the N2 position + allele
classification into a shared R file used by both scripts.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/snakemake/scripts/ta_r4/cs_cross_purity.R
@src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
@src/python/ta_r4/run_aggregation.py

**Standing rules:** PLAN-INDEX §A, §B and the 15.7 shared protocol. Tests never read an untracked `$Q` file: any
reference commit is a literal constant in the test.

**Forbidden:** changing map_fit_names' results or messages; edits outside files_modified; changing any panel, catalog
or sumstats; asserting a real-data count in a test.

**Measured at planning:**
- `run_coloc_pair_r4.R:128-200`: `norm_allele`, `missing_allele`, `complement`, `map_fit_names` (classification
  :163-176); `read_region` is the window rule to reuse; `:345-346` sources siblings via a `scripts` directory;
  `simulate_coloc_r4.R:39` `sys.source`s run_coloc_pair_r4.R.
- The sumstats .bgz files carry an unprefixed header line that `tabix -h` does not return; read the header from the
  file's first line (the planning probe failed on this first).
- Existing tests: test_cs_cross_purity.py (no new arguments; expected n_present / notes at :68, :93, :100);
  test_reporting_widened.py:156-158 (PURITY_COLS row).
- Superseded: the catalog-first routes from `f10_fitname_routes.R` (emulated names) are not used.
</context>

<new_tests>
tests/ta_r4/test_cs_cross_purity_resolution.py; N_new = 18.
1. `test_same_position_and_alleles_with_a_different_id_is_present`
2. `test_same_id_with_different_alleles_is_absent`
3. `test_swapped_alleles_match_and_keep_abs_r`
4. `test_strand_complement_of_a_non_palindromic_snv_matches`
5. `test_palindromic_snv_is_not_matched_by_complement`
6. `test_two_candidates_at_one_position_is_ambiguous`
7. `test_unresolved_name_is_an_error_even_with_allow_absent`
8. `test_absent_without_allow_absent_is_an_error`
9. `test_identical_panels_reproduce_the_fit_purity` (sets of ≤ 100 members only)
10. `test_map_fit_names_unchanged_after_extraction` (PRE_157C_REF literal; `git show` of run_coloc_pair_r4.R)
11. `test_mutated_classification_breaks_the_extraction_identity` (negative control for 10)
12. `test_run_aggregation_passes_the_fit_sumstats_and_panel`
13. `test_ukb_indel_id_resolves_through_the_sumstats` (fit name = sumstats id, fit-panel id `CHR:POS_REF_ALT`, other
    panel id an rsid at the same key → present, route sumstats)
14. `test_panel_rsid_override_name_resolves_through_the_panel` (sumstats id CHR:POS, name = panel rsid)
15. `test_chrpos_name_resolves_to_the_unique_fit_panel_row`
16. `test_duplicate_row_suffix_is_refused_unless_allowed`
17. `test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed` (and N ≥ k is
    an error under the flag)
18. `test_real_panels_new_rule_is_a_superset_of_allele_agreeing_matches` (r4_heavy; read-only; superset only)
Declared spec updates (invocation / fixture only; ids kept, outcomes stay passed; listed in the SUMMARY's `## Declared
spec updates`):
- `tests.ta_r4.test_cs_cross_purity::test_cross_purity_against_real_panel`, `::test_identity_panel_gives_zero_for_multi_member_sets`,
  `::test_refuses_unmatched_or_ambiguous_members[dup.rds-AMBIGUOUS]`, `[missing.rds-UNMATCHED]`,
  `::test_allow_absent_scores_present_members_and_counts_them`, `::test_allow_absent_still_refuses_ambiguous`: each
  invocation gains the new arguments and the fixture gains a fit sumstats window, catalog and fit panel;
- `tests.ta_r4.test_reporting_widened::test_cross_purity_is_status_agnostic`: its stub runner takes the new
  `_rscript_purity` signature; and the PURITY_COLS row at :156-158 gains the new columns.
If an expected n_present, note or purity value must change, STOP.
Expected FULL: base full_15_7b.xml (2,618) + 18 = 2,636 = 2,583 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Confirm the naming on real pilot fits; extract variant_match.R; resolve members through sumstats and panel (RED first)</name>
  <files>src/snakemake/scripts/ta_r4/variant_match.R, src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, src/snakemake/scripts/ta_r4/simulate_coloc_r4.R (conditional), src/snakemake/scripts/ta_r4/cs_cross_purity.R, src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_cs_cross_purity_resolution.py, tests/ta_r4/test_cs_cross_purity.py, tests/ta_r4/test_reporting_widened.py</files>
  <read_first>
    - run_susie_rss.R :780-900 (reader, catalog join), :1060-1070, :1113-1145, :1300-1315 (read only)
    - run_coloc_pair_r4.R :1-30, :100-200, :340-350, :430-462; cs_cross_purity.R; run_aggregation.py :43-92
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q/start_15_7c.txt`; that sha is the literal `PRE_157C_REF` in the test.
    1. **Confirm on real fits before RED.** Re-run `planner_probes/f10_real_fit_routes.R` under sbatch (`-t 00:45:00
       --mem=24G`, read-only) and reproduce the must_haves counts. Then confirm the rule exactly on the same 20 fits:
       rebuild each fit's subset (window rows of its sumstats ⋈ its recorded catalog on the allele key in catalog order,
       restricted to its panel as run_susie_rss.R does, override, blank → CHR:POS, make.unique) and assert the rebuilt
       names equal `colnames(fit$lbf_variable)` exactly for 20 of 20 fits. Any mismatch → STOP and report (the rule in
       must_haves would be wrong).
    2. **RED.** Tests 1-18 against the current script (new arguments accepted and ignored; variant_match.R absent).
       Expected RED: 1, 2, 4, 6, 7, 10-14, 16-18; expected green: 3, 5, 8, 9, 15 (record why).
    3. **GREEN.** `variant_match.R` (moved classification, `match_at_position`, `resolve_fit_names` per must_haves);
       run_coloc_pair_r4.R sources it by its own directory for both Rscript and `sys.source` callers;
       `cs_cross_purity.R` new required arguments and `--allow-duplicate-rows`; output adds route, match-kind and n_refused_multi_key count
       columns; `run_aggregation._rscript_purity` / `_cross_purity` pass the fit's sumstats, catalog
       (paths.catalog_path(ARMS[fit_arm]["route"], region)), region id (derived from region_safe with
       run_qtl_group_r4.region_ids(), the Snakefile safe-id rule over regions_r4.csv), regions csv and fit panel. The
       comparison of paths.catalog_path with the fit JSON's variant_catalog_path is made in run_aggregation._cross_purity,
       per fit, before cs_cross_purity.R runs, comparing resolved real paths (the JSON records absolute /rs1 paths): a
       mismatch is a STOP (FINAL refuses with exit 3 and names the fit; DRAFT
       prints it), never a silent choice of one catalog (no `--allow-duplicate-rows`: production fits). PURITY_COLS gains the new columns. Update the
       pre-existing tests (invocation / fixture only). 18/18 green; test_cs_cross_purity.py, test_fit_name_alignment.py,
       test_coloc_pair_r4.py, test_simulation_harness.py, test_reporting_widened.py green.
    4. **DRAFT** (e) E4: replace "purity is computed over the set members present in the other panel" with "purity is
       computed over the set members present in the other panel, a member being identified through the fit's own
       summary statistics and panel and located by position and alleles (exact, swapped, or the strand complement of a
       non-palindromic SNV)". Old string asserted unique; test_amendment_text.py green.
    5. Commit 1 (`fix(ta-r4-W3f): cross-panel purity resolves members through the fit's sumstats and panel by position
       and alleles; shared variant_match.R (15.7c, F10)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && set -o pipefail && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_cs_cross_purity_resolution.py tests/ta_r4/test_cs_cross_purity.py tests/ta_r4/test_fit_name_alignment.py tests/ta_r4/test_coloc_pair_r4.py tests/ta_r4/test_simulation_harness.py tests/ta_r4/test_reporting_widened.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider</automated>
  </verify>
  <done>The naming rule reproduced exactly on 20/20 real pilot fits; RED observed; resolver and extraction green; DRAFT matches.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation vs full_15_7b.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-cross-purity-variant-resolution-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7c: `$Q/check_15_7c.py` (removed 0; added == the 18; 0 outcome changes,
    the 7 declared ids included (passed → passed); 2,636 = 2,583 / 53 / 0). Records (LOG with
    the route counts and the 20/20 name reconstruction; STATE NEXT = 15.7d; NOT PUSHED; PLAN-INDEX COMPLETE; SUMMARY
    with ids and its `## Declared spec updates` section: the 7 ids above). fsck; commit 2.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7c.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled per id; records committed; no push.</done>
</task>

</tasks>

<enforcers>
| must_have | enforcer | negative control |
|---|---|---|
| naming rule | 20/20 exact name reconstruction on real pilot fits (Task 1 step 1) | — (must-be-identity) |
| id-independent presence | 1, 13 | current script (RED) |
| allele check on a name match | 2 | current script (RED) |
| routes | 13, 14, 15; 7 for no route | current script (RED) |
| `.N` handling | 16, 17 | current script (RED) |
| purity identity | 9 | — (sets ≤ 100) |
| N2 behaviour unchanged | 10 | 11 |
| real-panel superset | 18 | current rule misses the 251 (RED) |
</enforcers>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| variant identifiers across sumstats, fit and panels | the same variant carries different ids |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157c-01 | Tampering | cross-purity membership | mitigate | sumstats → panel override → CHR:POS, then position + alleles (1-8, 13-18) |
| T-r4-157c-02 | Tampering | a wrong naming premise | mitigate | exact name reconstruction on 20 real fits before any test |
| T-r4-157c-03 | Tampering | refactor changes N2 pair results | mitigate | identity vs PRE_157C_REF (10) with its negative control (11) |
</threat_model>

<verification>
- 18 new tests pass; check_15_7c.py passes; `git diff $(cat data/r4/tmp/w3f/q157/start_15_7c.txt)..HEAD --name-only` ⊆ files_modified.
</verification>

<success_criteria>
- Cross-panel purity counts a variant present exactly when it is physically present with compatible alleles, whatever its identifier.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-cross-purity-variant-resolution-SUMMARY.md`
</output>
