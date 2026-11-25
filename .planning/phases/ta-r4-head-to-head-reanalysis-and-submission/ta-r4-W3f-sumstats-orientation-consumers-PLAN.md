---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a3
slug: W3f-sumstats-orientation-consumers
type: execute
wave: 15.8a3
depends_on: ["ta-r4-W3f-sumstats-orientation-harmonize"]
gap_closure: true
files_modified:
  - src/python/ta_r4/paths.py                         # catalog_source_sumstats_path(); sumstats_path() route r4 -> oriented copy
  - src/python/ta_r4/sumstats_orient.py               # oriented_path() delegates to paths.oriented_sumstats_path; CATALOG_SOURCES unchanged
  - src/snakemake/rules/ta_r4_panels.smk               # CATALOG_SUMSTATS["r4"] -> catalog sources (bytes of the rule's command unchanged)
  - src/python/ta_r4/collector_drop_audit.py           # r4_sumstats() -> catalog sources
  - src/python/ta_r4/measure_fit_eligibility.py        # ASTHMA_PILOT_SUMSTATS pinned to the corrected lift (the pilot fits' input)
  - config/ta_r4/data_sources.yaml                     # `r4_oriented` record per sumstats entry
  - tests/ta_r4/test_sumstats_orient_consumers.py      # new
  - tests/ta_r4/fixtures/qtl_group_fixture.py          # fixture builder: copy the toy sumstats to the r4-route path
  - tests/ta_r4/test_measure_fit_eligibility.py        # 2 declared spec updates
  - tests/ta_r4/test_proxy_exact_purity.py             # 1 declared spec update
  - tests/ta_r4/test_fit_name_alignment.py             # 1 declared spec update
  - tests/ta_r4/test_verify_inputs.py                  # 1 declared spec update (test_real_asthma_eur_sumstats_verifies stays on the corrected lift)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_fixed_point.tsv   # new
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-consumers-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J, Q-158R2, Q-158OR and Q-158PAL pass (15.8a2's gate scripts, unchanged); otherwise nothing is edited"
    - "paths.sumstats_path(t, a, arm) returns data/r4/sumstats/<t>.<a>.r4_oriented.tsv.bgz for every route-r4 arm and is unchanged for every legacy-route arm (data/processed/sumstats_harmonized/<t>.<a>.tsv.bgz); paths.catalog_source_sumstats_path(t, a) returns exactly what sumstats_path(t, a, 'A3_1kg') returned at 15.8a2's HEAD for the 8 pairs"
    - "No production arm reads a data/processed file: fit, coloc, QTL, purity and verify commands of every production arm name only oriented sumstats; the repro arms (and so E7's earlier-pipeline comparator and QTL_legacy) read exactly the files they read before"
    - "The r4 catalog rule, the 15.8a collector audit, the asthma pilot-fit commands and the region-contribution proxy read the catalog sources, not the oriented copies (a dry run of r4_catalog_raw prints the 8 source paths in collector order)"
    - "Catalog fixed point, all 31 regions (Slurm): collect_region_variants.collect_variants on the 8 oriented files, written as the rule writes it, is byte-equal to the pinned raw catalog, and catalog_unique_key on it is byte-equal to the pinned final catalog and its dropped file; recorded in manifests/catalogs_r4_fixed_point.tsv; any region that differs is STOP for Carter (the catalog orientation is not self-consistent) and nothing is re-pinned"
    - "Because every catalog is byte-identical, no panel input changes (AFR panels read catalog positions, UKB native the unordered {REF, ALT} at catalog positions; the 1000G EUR and isect panels do not read the catalog): catalogs_sha256.tsv, catalogs_r4_unique_key.tsv and every panels_*.tsv are unchanged (sha256 before == after)"
    - "Every pre-existing test keeps its id and passes; the only edited assertions are the 5 declared ones; any other failure is STOP (re-plan), never an edit"
  artifacts:
    - path: "src/python/ta_r4/paths.py"
      provides: "catalog_source_sumstats_path, oriented sumstats_path"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_fixed_point.tsv"
      provides: "per-region proof that the catalogs are unchanged by the orientation"
  key_links:
    - from: "commands.fit_command / coloc_command / run_qtl_group_r4 / run_aggregation"
      to: "paths.sumstats_path (route r4)"
      via: "oriented copy"
      pattern: "r4_oriented"
    - from: "ta_r4_panels.smk CATALOG_SUMSTATS['r4']"
      to: "paths.catalog_source_sumstats_path"
      via: "collector input (no cycle: oriented copies are derived from the catalogs)"
      pattern: "catalog_source_sumstats_path"
---

<objective>
Point every r4 production consumer at the oriented sumstats of 15.8a2, keep everything that defines or reproduces the
catalogs and the pre-lock pilots on the original inputs, and prove that the catalogs (and so the panels) are a fixed
point of the orientation: rebuilt from the oriented files they are byte-identical, so no catalog or panel is re-pinned.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J, Q-158R2, Q-158OR, Q-158PAL: as in ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md <question> (sha256 and
labels pinned there). Task 2 STOP question (only if a region's rebuilt catalog differs), QID Q-158FP, file
`W3f-carter-15-8-Q-158FP-reply-<date>.txt`: "Rebuilding the r4 catalogs from the oriented sumstats changes N of 31
catalogs (table: region, rows added / removed / re-oriented). The plan assumed they would be unchanged. How should
15.8a3 proceed?" Labels: `A: Stop and re-plan the orientation (Recommended)` / `B: Re-pin the rebuilt catalogs and
re-run the 15.8a audit and the panel checks (new plan)` / `C: Other (free text)`.
</question>

<protocol>
The 15.8 shared protocol (ta-r4-W3f-collector-drop-audit-PLAN.md) with the 15.8a2 sub-chain changes
(ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md `<protocol>`). Base `$Q8/full_15_8a2.xml` (expected 2,714; use its
actual totals). Scratch `$Q8/a3/`.
</protocol>

<context>
@src/python/ta_r4/paths.py
@src/python/ta_r4/commands.py
@src/snakemake/rules/ta_r4_panels.smk
@src/snakemake/rules/ta_r4_panels_afr_ukb.smk
@src/python/ta_r4/collector_drop_audit.py
@src/python/ta_r4/measure_fit_eligibility.py
@tests/ta_r4/fixtures/qtl_group_fixture.py

**Consumers of paths.sumstats_path, verified at 8da7bfbe (planning).**

| consumer | arm(s) | orientation handling today | after this plan |
|---|---|---|---|
| commands.fit_command → run_susie_rss.R (frozen) | production | catalog join exact (:856-870) → swapped rows lost; panel join exact/swapped, palindromes dropped (:220-323), z negated on swap (:1185-1194) | oriented copy: every non-absent row joins; panel join unchanged |
| commands.verify_command / coloc_verify_command | production | sha256 vs sumstats_r4_sha256.tsv | the oriented rows pinned in 15.8a2 |
| commands.coloc_command → run_coloc_pair_r4.R | production + repro | fit names → sumstats rows by name, else through the panel by position + exact/swapped/strand alleles (map_fit_names, variant_match.R); A1_allvars by CHR:POS + unordered {REF,ALT}; coloc.abf is sign-invariant | oriented copy (production); repro unchanged; no code change |
| run_qtl_group_r4 (QTL_A3 / QTL_A2 via fit arm; QTL_legacy via repro_routeL) | both | GWAS side = fit names; QTL betas oriented to the panel (qtl_orient); ABF sign-invariant | QTL_A3/A2 read oriented; QTL_legacy unchanged |
| run_aggregation → cs_cross_purity.R (resolve_fit_names: sumstats rows in the catalog by exact key, kept by the panel) | production | mirrors the fit's exact join | oriented copy, consistent with fits run on it |
| measure_fit_eligibility.pinned_inputs / measurement_argv | production | = fit_command | oriented (15.8a4 re-measures) |
| measure_fit_eligibility.ASTHMA_PILOT_SUMSTATS (:447) | repro pilot | `paths.sumstats_path("asthma","EUR","A3_1kg")` = the corrected lift | must stay the corrected lift: pinned to catalog_source_sumstats_path |
| collector_drop_audit.r4_sumstats (:292-301) | catalog audit | = CATALOG_SUMSTATS["r4"] | catalog sources |
| ta_r4_panels.smk CATALOG_SUMSTATS["r4"] (:14-17) | catalog build | — | catalog sources (else a DAG cycle: oriented copies are made from the catalogs) |
| select_null_windows (15.7h, inputs typed in test_null_windows_production_pool.py) | NC windows | P and per-tile counts only | unchanged inputs; invariant by 15.8a2 test 13 |
| simulate_coloc_r4.R / ta_r4_sim.smk | simulation | panels and simulated z only; no sumstats | unaffected |

Panels (ta_r4_panels.smk, ta_r4_panels_afr_ukb.smk): A3_1kg = 1000G EUR .bim window, `--keep-allele-order`, no
catalog; A2_identity from A3_1kg; AFR661/AFR504 = 1000G VCF, `--extract range` on catalog CHR:POS only; UKB native =
UKB rows at catalog positions whose unordered {allele1, allele2} equals a catalog {REF, ALT}
(ukb337k_tiles.build_native :341-347); isect panels oriented to EUR_1kg_r4 by ALT (±1). None depends on the catalog's
orientation, and with byte-identical catalogs none of their inputs changes.

Tests that name the old path (planning grep): test_measure_fit_eligibility.py:48-50, :134-137; test_proxy_exact_purity.py:251-252;
test_fit_name_alignment.py:154 (rewrites the toy tA file at the data/processed path, then runs QTL_A3);
qtl_group_fixture.py:61 (writes the toy sumstats at the data/processed path only) and :127 (manifests list
paths.sumstats_path for A3_1kg and repro_routeL). build_toy_workflow.py writes at paths.sumstats_path(trait, ANC, arm)
and follows the change. test_coloc_pair_r4.py:317 reads the toy data/processed file directly (same bytes once the
fixture copies it). test_null_windows_production_pool.py types the 8 source paths (unchanged, still pinned).

<interfaces>
```python
# paths.py after this plan
def catalog_source_sumstats_path(trait, anc):   # bmi.EUR -> data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz (D-18);
                                                # asthma -> data/r4/sumstats/asthma.<anc>.grch37_lifted_strand.tsv.bgz;
                                                # else data/processed/sumstats_harmonized/<trait>.<anc>.tsv.bgz
def oriented_sumstats_path(trait, anc):         # f"{R4}/sumstats/{trait}.{anc}.r4_oriented.tsv.bgz"
def sumstats_path(trait, anc, arm):             # route r4 -> oriented_sumstats_path; legacy -> data/processed (as before)
```
</interfaces>
</context>

<new_tests>
tests/ta_r4/test_sumstats_orient_consumers.py; N_new = 8 (no parametrize).
1. `test_production_arms_read_only_oriented_sumstats` (every production arm × the 8 pairs: fit, verify, coloc (3 modes),
   QTL group files and the aggregation purity input name `.r4_oriented.`; none under data/processed)
2. `test_legacy_route_paths_are_unchanged` (every repro arm × the 8 pairs == the 15.8a2-HEAD values, typed from
   `$Q8/a3/paths_before.tsv`). Characterization test: it passes on the old code by design (nothing about the legacy
   route should change); NC (d) below is its evidence that it can fail
3. `test_catalog_source_paths_equal_the_previous_r4_inputs` (two assertions: (i) the set of
   `paths.catalog_source_sumstats_path(t, a)` over the 8 pairs == set(test_null_windows_production_pool.PRODUCTION_INPUTS);
   (ii) the list in collector order (config/pipeline.yaml traits × trait_ancestries) == the A3_1kg column of
   `$Q8/a3/paths_before.tsv` in that order, typed, == `[p for _, _, p in sumstats_orient.CATALOG_SOURCES]`. Order matters:
   the collector keeps the first file's row, so a reordered list would change the catalogs. RED: catalog_source_sumstats_path absent)
4. `test_catalog_rule_dry_run_reads_the_catalog_sources` (r4_heavy: `snakemake -s Snakefile.ta_r4 -n -F --printshellcmds
   <raw catalog of NC_ABO>` as test_dry_run_shell_commands_isolated runs it; the `--harmonized` arguments == the 8
   sources, as a list in collector order; no `.r4_oriented.` path). Characterization test (the rule reads the sources
   before and after the edit); NC (b) is its evidence
5. `test_collector_audit_and_asthma_pilot_read_the_catalog_sources` (collector_drop_audit.r4_sumstats() and
   measure_fit_eligibility.ASTHMA_PILOT_SUMSTATS, typed paths). Characterization test (both read the sources before and
   after the edit); NC (c) and NC (e) are its evidence
6. `test_data_sources_record_the_oriented_copies` (each sumstats entry's `r4_oriented.path` == paths.sumstats_path(…,
   "A3_1kg"), its sha256 == the pinned row, its `from` == the entry's url)
7. `test_catalog_is_a_fixed_point_of_the_oriented_inputs` (r4_heavy: NC_ABO (fewest input rows): rebuilt raw, final and
   dropped bytes == pinned)
8. `test_fixed_point_manifest_matches_disk` (31 rows, all equal; sha256 columns == catalogs_sha256.tsv and the files on disk)
Declared spec updates (assertion edits only, ids and passed outcomes unchanged):
- `tests.ta_r4.test_measure_fit_eligibility::test_argv_reads_the_corrected_asthma_lift` → `--sumstats` ==
  `data/r4/sumstats/asthma.EUR.r4_oriented.tsv.bgz`, and the 15.8a2 report for asthma.EUR names the corrected lift
  (sha256 49edfc54…) as its input (the corrected lift is still what the fit reads, oriented)
- `tests.ta_r4.test_measure_fit_eligibility::test_pinned_inputs_come_from_the_committed_manifests` → oriented path;
  sha256 prefix = the oriented asthma.EUR pin (typed from manifests/sumstats_r4_sha256.tsv)
- `tests.ta_r4.test_proxy_exact_purity::test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir` →
  `argv[s] == CORRECTED == paths.catalog_source_sumstats_path("asthma", "EUR")` (the pilot argv itself is unchanged)
- `tests.ta_r4.test_fit_name_alignment::test_qtl_abf_maps_bridged_names_through_panel` → rewrites
  `paths.sumstats_path("tA", "EUR", "A3_1kg")`, the file QTL_A3 reads. Not RED-able (it passes on the old code, where
  that path is the data/processed file). Need is shown instead: after the switch, run the **unedited** test (it must
  fail: QTL_A3 reads the un-rewritten r4-route copy, so `n_direct != 0`); record the failure in `$Q8/red_15_8a3.txt`;
  then edit and re-run (pass)
- `tests.ta_r4.test_verify_inputs::test_real_asthma_eur_sumstats_verifies` → `rel =
  paths.catalog_source_sumstats_path("asthma", "EUR")` (stays on the corrected lift, the file it was written to check;
  the oriented asthma file is verified by 15.8a2 test 12). Without the edit it would silently switch to the oriented
  file and still pass; declared so the change of subject cannot happen unseen. Not RED-able for the same reason;
  shown by asserting, after the switch, that the unedited `rel` ends `.r4_oriented.tsv.bgz` (recorded), then editing
Expected FULL: base full_15_8a2.xml (expected 2,714) + 8 = 2,722; outcome changes only on the 5 declared ids, each passed.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates; path split and consumer switch (RED first); fixture and declared updates</name>
  <files>src/python/ta_r4/paths.py, src/python/ta_r4/sumstats_orient.py, src/snakemake/rules/ta_r4_panels.smk, src/python/ta_r4/collector_drop_audit.py, src/python/ta_r4/measure_fit_eligibility.py, config/ta_r4/data_sources.yaml, tests/ta_r4/test_sumstats_orient_consumers.py, tests/ta_r4/fixtures/qtl_group_fixture.py, tests/ta_r4/test_measure_fit_eligibility.py, tests/ta_r4/test_proxy_exact_purity.py, tests/ta_r4/test_fit_name_alignment.py</files>
  <behavior>
    - Tests 1, 3 and 6 per <new_tests> are RED (fail on the old code); tests 2, 4, 5 are characterization tests with
      named NCs; declared edits 1-3 are RED; declared edits 4-5 are shown needed after the switch (<new_tests>)
  </behavior>
  <action>
    0. `mkdir -p $Q8/a3`; HEAD → `$Q8/a3/start.txt`. Gates: gate_157j.sh, gate_158r2.sh, gate_158a2.sh Q-158OR Q-158PAL.
       Confirm 15.8a2 closed (SUMMARY committed, full_15_8a2.xml present). `sha256sum` of catalogs_sha256.tsv,
       catalogs_r4_unique_key.tsv, every panels_*.tsv, the 31 raw/final/dropped catalogs → `$Q8/a3/sha_before.txt`.
       Record `paths.sumstats_path(t, a, arm)` for every arm × 8 pairs at this HEAD → `$Q8/a3/paths_before.tsv` (test 2
       and 3 type their expectations from it).
    1. RED: tests 1, 3, 6 and declared edits 1-3 → `$Q8/red_15_8a3.txt`; tests 2, 4, 5 run and pass on the old code
       (recorded as characterization).
    2. paths.py per <interfaces>; sumstats_orient.oriented_path → paths.oriented_sumstats_path. sumstats_orient keeps its
       typed CATALOG_SOURCES (15.8a2), so 15.8a2's tests 9, 11 and 14 still read the sources and test 10 the oriented
       files; no 15.8a2 test needs rewiring (test 3 here pins CATALOG_SOURCES == catalog_source_sumstats_path).
       ta_r4_panels.smk: `CATALOG_SUMSTATS["r4"] = [r4paths.catalog_source_sumstats_path(t, a) for t, a in TRACK_A_SUMSTATS]`
       (no other line). collector_drop_audit.r4_sumstats → catalog_source_sumstats_path (docstring: "the 8 r4 catalog
       inputs"). measure_fit_eligibility.ASTHMA_PILOT_SUMSTATS → `paths.catalog_source_sumstats_path("asthma", "EUR")`.
       data_sources.yaml: each of the 8 sumstats entries gains `r4_oriented: {path, sha256, from: <url>}` (sha256 from
       the 15.8a2 pin); no other key changes. qtl_group_fixture.py: after writing the toy files, copy each
       `data/processed/sumstats_harmonized/<tr>.EUR.tsv.bgz` to `paths.sumstats_path(tr, "EUR", "A3_1kg")` when the two
       differ (the catalog-copy pattern at :112-114).
    3. Run `pytest tests/ta_r4 -m "not r4_heavy" -q` and the r4_heavy files that import paths
       (test_coloc_pair_r4, test_fit_name_alignment, test_purity_determinism, test_cs_cross_purity_resolution,
       test_simulation_harness, test_frozen_script_armed_e2e, test_unique_allele_key_guard, test_in_job_gate,
       test_verify_inputs, test_track_b_isolation, test_collector_drop_audit, test_proxy_exact_purity,
       test_measure_fit_eligibility, test_sumstats_orient) under sbatch (`-t 02:00:00 --mem=32G --constraint=cascadelake`).
       Before editing declared tests 4-5, run them unedited and record the expected failure / path (<new_tests>).
       A failure outside the 5 declared ids is STOP: record it, do not edit the test, return to planning.
    4. Negative controls (`$Q8/nc_15_8a3.txt`): (a) sumstats_path returns the source for A3_ukb → test 1 fails;
       (b) CATALOG_SUMSTATS["r4"] built from sumstats_path → test 4 fails; (c) ASTHMA_PILOT_SUMSTATS from sumstats_path →
       test 5 and the declared proxy test fail; (d) sumstats_path returns the oriented path for repro_routeC → test 2
       fails; (e) collector_drop_audit.r4_sumstats built from sumstats_path → test 5 fails. md5-restore after each.
    5. Commit 1 (explicit paths): `feat(ta-r4-W3f): r4 production reads the oriented sumstats; catalogs and pilots keep
       their inputs (15.8a3)`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient_consumers.py tests/ta_r4/test_sumstats_orient.py -q -p no:cacheprovider -m "not r4_heavy"</automated>
  </verify>
  <done>Production arms read the oriented copies; the catalog build, audit and pilots read the sources; only the 5 declared assertions changed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Catalog fixed point on all 31 regions (STOP for Carter on any difference)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_fixed_point.tsv, tests/ta_r4/test_sumstats_orient_consumers.py</files>
  <behavior>
    - Tests 7-8 per <new_tests> (RED: manifest absent)
  </behavior>
  <action>
    1. RED tests 7-8 → `$Q8/red_15_8a3.txt`.
    2. `$Q8/a3/fixed_point.py <region>`: `collector_drop_audit.load_collector().collect_variants(...)` on the 8 oriented
       files (paths.sumstats_path(t, a, "A3_1kg"), collector order; first assert all 8 exist and pass ta_r4.verify_inputs,
       because the collector skips a missing path silently, collect_region_variants.py:38-40) for the region window
       (collector_drop_audit.region_window),
       serialized exactly as collect_region_variants.py's main writes it (`to_csv(sep="\t", index=False)`, the 15.8a
       byte-identity), then `catalog_unique_key.unique_allele_key` on those lines, rendered as its main() writes them
       (kept lines joined; DROPPED_HEADER + one line per dropped row); compare raw, final and dropped bytes with
       `paths.catalog_raw_path`, `paths.catalog_path("r4", …)` and `paths.catalog_dropped_path`; write `$Q8/a3/fp/<region>.json` (sha256 of each, equal flags, row counts). Slurm array
       over the 31 regions (`-t 02:00:00 --mem=12G`, 15.8a's audit_array.sh sizing).
    3. Any region not equal → write `fp_outcome=<n>` to `$Q8/a3/fp_outcome.txt`, print the per-region diff table, ask
       Q-158FP (<question>) as a `checkpoint:human-action` (stops even under --auto; only Carter's typed reply creates
       the reply file) and do nothing else. All 31 equal → manifests/catalogs_r4_fixed_point.tsv (region_safe,
       raw/final/dropped sha256 pinned vs rebuilt, rows, equal); tests 7-8 green.
    4. Re-hash: `$Q8/a3/sha_after.txt` == sha_before.txt (`cmp`): catalogs, catalogs_sha256.tsv,
       catalogs_r4_unique_key.tsv and every panels_*.tsv unchanged.
    5. NC (`$Q8/nc_15_8a3.txt`): flipping a row the harmonizer flipped back cannot change the catalog (those rows are
       dropped by the collector either way), so the NC flips a row that **defines** a catalog entry. In NC_ABO, take
       the first catalog row whose SNP_ID comes from bmi.EUR (the first file in collector order) and whose alleles are
       not A/T or C/G; in a temp copy of the oriented bmi.EUR file restricted to the NC_ABO window (bgzipped + tabix'd
       under `$Q8/a3/nc_fp/`), apply sumstats_orient.flip_fields to that row only; run fixed_point.py for NC_ABO with
       that copy in bmi.EUR's place (the other 7 unchanged). Required: raw and final catalogs "not equal" (that
       variant's REF/ALT reversed). A result of "equal" means the comparison cannot fail: STOP.
    6. Commit 2: manifest + tests 7-8 (`test(ta-r4-W3f): r4 catalogs are a fixed point of the oriented sumstats, 31/31 (15.8a3)`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient_consumers.py -q -p no:cacheprovider && cmp data/r4/tmp/w3f/q158/a3/sha_before.txt data/r4/tmp/w3f/q158/a3/sha_after.txt</automated>
  </verify>
  <done>31 of 31 catalogs rebuild byte-identically from the oriented inputs (or Carter has the table); no catalog or panel pin moved.</done>
</task>

<task type="auto">
  <name>Task 3: FULL vs full_15_8a2.xml; records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-consumers-SUMMARY.md</files>
  <action>
    1. `$Q8/close.sh 15_8a3` under sbatch. `$Q8/check_15_8a3.py`: base full_15_8a2.xml, NEW = the 8 ids, declared = the
       5 ids above (each passed in both files), expect = base totals + 8.
    2. Records: LOG (consumer table as executed, path diffs, fixed-point table, NCs, check output); PLAN-INDEX 15.8a3
       COMPLETE; STATE ★ (NEXT = 15.8a4; NOT PUSHED); SUMMARY with `## Declared spec updates` (the 5 ids) and
       `## New test ids` (8). fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8a3.py && test -z "$(git status --porcelain -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_r4_unique_key.tsv)" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml;d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False and d['confirmatory']['n_regions_min']==7"</automated>
  </verify>
  <done>FULL reconciled; records committed; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| oriented copies → production jobs | jobs must read the pinned oriented bytes |
| catalog sources → catalogs, pilots, E7 comparator | must not silently move to the oriented copies |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158a3-01 | Tampering | a consumer left on the source file (silent row loss persists) | mitigate | test 1 over every production arm and command kind; NC (a) |
| T-r4-158a3-02 | Tampering | catalog built from oriented copies (cycle, silent catalog change) | mitigate | dry-run test 4; fixed point 31/31; NC (b) |
| T-r4-158a3-03 | Repudiation | pilot fits no longer reproducible from their recorded input | mitigate | ASTHMA_PILOT_SUMSTATS pinned (test 5, NC (c)) |
| T-r4-158a3-04 | Tampering | test edited to pass | mitigate | 5 declared assertions only; any other failure STOP |
</threat_model>

<verification>
- Gates pass; 8 new tests green, NCs seen failing; fixed point 31/31; catalog and panel pins unchanged; check_15_8a3.py passes.
</verification>

<success_criteria>
- Production reads one orientation; the catalogs, panels and pilot records are provably unchanged.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-consumers-SUMMARY.md`
</output>
