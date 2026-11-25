---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a3
subsystem: ta-r4 W3f r4 sumstats consumers (oriented inputs, Carter Q-158R2 D, Q-158OR A)
tags: [R2, orientation, sumstats, consumers, catalog-fixed-point, Q-158FP]
requires: [ta-r4-W3f-sumstats-orientation-harmonize]
provides: [paths.catalog_source_sumstats_path, paths.oriented_sumstats_path, oriented paths.sumstats_path, manifests/catalogs_r4_fixed_point.tsv]
affects: [15.8a4 (eligibility re-measure on the oriented inputs), 15.8e, 15.8f (cumulative reconcile)]
tech-stack:
  added: []
  patterns: [split a path function by role (catalog source vs production read), byte-level fixed-point rebuild, characterization tests with named negative controls]
key-files:
  created:
    - tests/ta_r4/test_sumstats_orient_consumers.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_fixed_point.tsv
  modified:
    - src/python/ta_r4/paths.py
    - src/python/ta_r4/sumstats_orient.py
    - src/snakemake/rules/ta_r4_panels.smk
    - src/python/ta_r4/collector_drop_audit.py
    - src/python/ta_r4/measure_fit_eligibility.py
    - config/ta_r4/data_sources.yaml
    - tests/ta_r4/fixtures/qtl_group_fixture.py
    - tests/ta_r4/test_measure_fit_eligibility.py
    - tests/ta_r4/test_proxy_exact_purity.py
    - tests/ta_r4/test_fit_name_alignment.py
    - tests/ta_r4/test_verify_inputs.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/STATE.md
decisions:
  - "Production arms (route r4) read the oriented copies; everything that defines or reproduces the catalogs (r4_catalog_raw, the 15.8a collector audit) and the pre-lock asthma pilots read the catalog sources"
  - "data_sources.yaml r4_oriented.from records the file each copy was made from; for bmi EUR that is the D-18 r4_alleles file, not the entry's url"
metrics:
  completed: 2026-11-25
---

# Phase ta-r4 Plan 15.8a3: r4 production reads the oriented sumstats Summary

Every route-r4 (production) arm now reads data/r4/sumstats/<trait>.<anc>.r4_oriented.tsv.bgz, the copies 15.8a2 wrote
and pinned. That covers fit, verify, coloc (susie, A1_matched, A1_allvars), the QTL_A3 / QTL_A2 group files and the
aggregation's cross-purity input. The repro arms and QTL_legacy read exactly what they read before. The r4 catalog rule,
the 15.8a collector audit and the asthma pilot-fit input keep reading the catalog sources, so there is no DAG cycle.

Rebuilt from the oriented files, the r4 catalogs are byte-identical to the pinned ones in 31 of 31 regions (raw, final
and dropped files). So no catalog or panel input changed and nothing was re-pinned. Q-158FP was not needed.

## Commits (this executor pushed nothing)

| Task | Commit | Content |
|------|--------|---------|
| 1 | 9b5876c9 | path split + consumer switch; data_sources r4_oriented records; fixture copy; tests 1-6; 5 declared spec updates |
| 2 | 50a7bad9 | manifests/catalogs_r4_fixed_point.tsv; tests 7-8 |
| 3 | (records commit) | LOG; PLAN-INDEX 15.8a3 COMPLETE; STATE ★ block; this SUMMARY |

## Gates

gate_157j.sh, gate_158r2.sh and gate_158a2.sh Q-158OR Q-158PAL all returned rc 0 (data/r4/tmp/w3f/q158/a3/gates.txt).
15.8a2 was closed (SUMMARY 83e17b38, full_15_8a2.xml present). Start HEAD 83e17b38.

## Consumer switch (path diff a3/paths_before.tsv → a3/paths_after.tsv)

- The 8 production arms × 8 pairs moved to `.r4_oriented.` (64 changes).
- The 5 repro arms × 8 pairs are unchanged (40).
- `paths.catalog_source_sumstats_path` over the 8 pairs, in collector order, equals all three of these:
  - the A3_1kg column at 83e17b38;
  - `sumstats_orient.CATALOG_SOURCES`;
  - set(test_null_windows_production_pool.PRODUCTION_INPUTS).
- The dry run of r4_catalog_raw for NC_ABO prints the 8 source paths in collector order, and no `.r4_oriented.` path.

## Catalog fixed point (manifests/catalogs_r4_fixed_point.tsv; Slurm array 2096913_[0-30])

- For each region, data/r4/tmp/w3f/q158/a3/fixed_point.py does this:
  - checks that all 8 oriented files exist and pass verify_inputs;
  - runs `collect_variants` on them in collector order and serializes the result as the rule does;
  - runs `catalog_unique_key.unique_allele_key` and renders the output as its main() does.
- Raw, final and dropped bytes equal the pinned files in **31/31** regions.
- Totals: raw 875,225 (= 15.8a n_kept), final 627,685, dropped 247,540.
- Each region took 6-7 min, with max RSS 3.2 GB.
- sha256 of 106 files is unchanged, before == after Task 2 and again after the FULL (`cmp`). The 106 files are the 31 × 3
  catalogs, catalogs_sha256.tsv, catalogs_r4_unique_key.tsv and the 11 panels_*.tsv.

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8a3.txt)

Each mutation was md5-restored, with PYTHONDONTWRITEBYTECODE=1. Every one of these made its named test(s) fail:

- (a) sumstats_path returns the source for A3_ukb: test 1 RED.
- (b) CATALOG_SUMSTATS["r4"] built from sumstats_path: test 4 RED.
- (c) ASTHMA_PILOT_SUMSTATS from sumstats_path: test 5 and the declared proxy test RED.
- (d) sumstats_path returns the oriented path for repro_routeC: test 2 RED.
- (e) collector_drop_audit.r4_sumstats built from sumstats_path: test 5 RED.
- Fixed-point NC. NC_ABO's first final-catalog row from bmi.EUR that is not A/T or C/G is 9:136127268 C/T rs9411475. I
  applied `flip_fields` to that row only, in a window copy of the oriented bmi.EUR file:
  - fixed_point.py reports raw, final and dropped all **not equal**. In the raw catalog 1 row is re-oriented (0 added,
    0 removed). Final goes 773 → 772 and dropped 295 → 296, because the flipped key collides with the other entry at
    that position.
  - Test 7 run on the same copy fails (a pytest plugin swaps the input).
- Test 8 with one manifest sha256 character changed: RED.

## RED and need evidence (data/r4/tmp/w3f/q158/red_15_8a3.txt)

- Slurm 2096701, on the old code with declared edits 1-3 applied:
  - tests 1, 3, 6 and declared updates 1-3 FAILED;
  - tests 2, 4, 5 PASSED, as characterization tests by design.
- Slurm 2096713, after the switch, with declared tests 4-5 still unedited:
  - test_qtl_abf_maps_bridged_names_through_panel FAILED with `n_direct` 196 != 0;
  - test_real_asthma_eur_sumstats_verifies' `rel` had become data/r4/sumstats/asthma.EUR.r4_oriented.tsv.bgz. The test
    would have silently changed subject and still passed.
  - Both were then edited, and both pass.
- Slurm 2096914 (Task 2): test 8 RED because the manifest was absent. Test 7 passes on arrival, because the fixed point
  is a property of the pinned data, not of new code. Its evidence that it can fail is the fixed-point NC above.

## Slurm jobs

| Job | Purpose | Result |
|-----|---------|--------|
| 2096701 | RED, old code | 6 failed (1, 3, 6, declared 1-3), 3 passed (2, 4, 5) |
| 2096713 | declared 4-5 unedited, after the switch | test_qtl_abf… FAILED (n_direct 196); rest passed |
| 2096746 | QUICK + 15 r4_heavy files (cascadelake) | 880 P / 2 S; 86 P; 0 outcome changes vs full_15_8a2 |
| 2096854 | NCs (a)-(e) | 5/5 RED; 5 passed after restore |
| 2096913_[0-30] | catalog fixed point | 31/31 rc 0, 31/31 equal |
| 2096914 | RED tests 7-8 | test 8 FAILED (manifest absent), test 7 passed (240 s) |
| 2096917 | fixed-point NC, first run | stopped in the NC script before any comparison (header bug, see Deviations) |
| 2097246 | fixed-point NC + test 7 NC | not equal; test 7 FAILED |
| 2097324 | test 8 NC, green, sha_after | test 8 RED; 22 passed; sha_after == sha_before |
| 2097342 | FULL close (cascadelake c022n03) | 2,722 = 2,669 P / 53 S / 0 F |

## FULL

- Slurm 2097342, cascadelake c022n03, HEAD 50a7bad9, 2h27m.
- QUICK 881 P / 2 S; HEAVY 340 P / 5 S; PINS 39 P.
- FULL 2,722 = 2,669 P / 53 S / 0 F (data/r4/tmp/w3f/q158/full_15_8a3.xml, sha256 0d538bd6…d988).
- check_15_8a3.py against full_15_8a2.xml (2,714 = 2,661 P / 53 S, read from the file):
  - 0 removed and +8 (the 8 new ids, all passed);
  - 0 outcome changes;
  - the 5 declared ids passed → passed;
  - totals 2,722 / 2,669 / 53 / 0;
  - CHECK PASS.
- The check's NC (base given as new) gives CHECK FAIL, rc 1.
- close.sh restored tests/m3/sparse_parent_benchmark.tsv (clean).
- The 5 qtl_group_fixture importers collect, and every id in them passes. They are test_qtl_group_runner,
  test_coloc_pair_r4, test_verify_inputs, test_fit_name_alignment and test_purity_determinism.

## Deviations from Plan

1. **[Rule 1 - provenance] `r4_oriented.from` for bmi EUR.** The plan says each entry's `from` is the entry's url. For 7
   of the 8 entries the url is the file the oriented copy was made from. bmi EUR is the exception:
   - its url is data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz;
   - but its oriented copy was made from data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz (D-18; the 15.8a2 harmonize report's
     `src`).

   Writing the url would have recorded a false provenance in config. So `from` = `paths.catalog_source_sumstats_path(t,
   a)`. Test 6 asserts that, and also asserts `from == url` exactly for the 7 entries other than bmi EUR. **Please
   confirm this reading.**
2. **[Rule 3 - scratch script] Fixed-point NC, first run.** `tabix -h` prints no header for an index built with `-S 1`,
   so nc_fp.py's header assertion stopped the job (2096917) before any comparison. The fix reads the header from line 1
   of the file. The re-run is 2097246, and the first output is kept as a3/nc_fp_2096917_run1_header_bug.out.
3. **[Additions] Extra checks; nothing relaxed:**
   - Test 1 also checks the aggregation input by calling `run_aggregation._cross_purity` on a tmp repo with a recording
     runner (for every CROSS_PURITY fit arm).
   - Test 7 and test 8 each have their own NC: a pytest plugin runs test 7 on the flipped copy, and one manifest sha256
     character is changed for test 8.
   - The step 3 heavy run also included the new test file.
4. **[Records] STATE.md** was updated with the project's ★ block (as in 15.8a2), not with the gsd-tools state / roadmap /
   requirements commands. Those commands would rewrite the custom STATE frontmatter. REQ-OSF-PREREG and REQ-SNAKEMAKE-CI
   are not marked complete: they span the phase.

## Declared spec updates

tests.ta_r4.test_measure_fit_eligibility::test_argv_reads_the_corrected_asthma_lift
tests.ta_r4.test_measure_fit_eligibility::test_pinned_inputs_come_from_the_committed_manifests
tests.ta_r4.test_proxy_exact_purity::test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir
tests.ta_r4.test_fit_name_alignment::test_qtl_abf_maps_bridged_names_through_panel
tests.ta_r4.test_verify_inputs::test_real_asthma_eur_sumstats_verifies

## New test ids

tests.ta_r4.test_sumstats_orient_consumers::test_production_arms_read_only_oriented_sumstats
tests.ta_r4.test_sumstats_orient_consumers::test_legacy_route_paths_are_unchanged
tests.ta_r4.test_sumstats_orient_consumers::test_catalog_source_paths_equal_the_previous_r4_inputs
tests.ta_r4.test_sumstats_orient_consumers::test_catalog_rule_dry_run_reads_the_catalog_sources
tests.ta_r4.test_sumstats_orient_consumers::test_collector_audit_and_asthma_pilot_read_the_catalog_sources
tests.ta_r4.test_sumstats_orient_consumers::test_data_sources_record_the_oriented_copies
tests.ta_r4.test_sumstats_orient_consumers::test_catalog_is_a_fixed_point_of_the_oriented_inputs
tests.ta_r4.test_sumstats_orient_consumers::test_fixed_point_manifest_matches_disk

## Not done here (by design)

- No production fit, no OSF, no W4a-T3 lock. decision_rules.yaml stays locked: false, and n_regions_min stays 7.
- No catalog, panel, sumstats or data/processed byte changed. Track B is unchanged.
- Nothing was pushed.
- The eligibility re-measure on the oriented inputs and the DRAFT edit belong to 15.8a4. R2 stays OPEN until 15.8a4.

## Self-Check: PASSED

The test file, the fixed-point manifest, this SUMMARY and full_15_8a3.xml exist. Commits 9b5876c9 and 50a7bad9 are in
`git log`. check_15_8a3.py passes. The 5 fixture importers have the same ids and outcomes as in full_15_8a2.xml (100/100 passed).
