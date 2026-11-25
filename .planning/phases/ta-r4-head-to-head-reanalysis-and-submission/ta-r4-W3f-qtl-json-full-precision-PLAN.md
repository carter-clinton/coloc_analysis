---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8c
slug: W3f-qtl-json-full-precision
type: execute
wave: 15.8c
depends_on: ["ta-r4-W3f-openblas-pin-and-guard"]
gap_closure: true
files_modified:
  - src/snakemake/scripts/run_qtl_coloc.R
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
  - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
  - tests/ta_r4/test_coloc_pair_r4.py                      # only if a test fails from the precision change (declared)
  - tests/ta_r4/test_simulation_harness.py                 # only if a test fails from the precision change (declared)
  - tests/ta_r4/test_qtl_json_precision.py
  - tests/ta_r4/test_purity_determinism.py                 # _qtl_run helper strips the new flag too (declared)
  - tests/ta_r4/test_qtl_group_runner.py                   # only if an argv pin names the arm flag list (declared)
  - .planning/DECISIONS.md
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-json-full-precision-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates: Q-157J and Q-158DIG (`A: Exact round-trip everywhere r4 thresholds (Recommended)`, sha256 ea8fe4cd…ceb4) pass (15.8 protocol); otherwise nothing is edited"
    - "run_qtl_coloc.R gains `--json-full-precision` (default false; anything but true/false stops); with false every write_json call (:295, :715, :740, :798) is the pre-15.8c call unchanged, so the default output is byte-identical to the pre-15.8c script for every status the fixtures reach (test: cmp of the JSON files, not a parsed comparison)"
    - "With `--json-full-precision true` every numeric value round-trips exactly (parsed JSON value == the R double) and rounding to 4 decimals of the full output reproduces the default output's numbers; a posterior of 0.79999 is written as 0.79999 and a posterior one ulp below 0.8 is not written as 0.8"
    - "QTL_A3 and QTL_A2 pass `--json-full-precision true`; QTL_legacy and Track B do not; the flag is inserted before `--qtl-orient` so the 15.7f argv pins keep their positions"
    - "Every r4 writer whose numbers reach a threshold is listed with its measured round-trip precision in $Q8/writers_15_8c.tsv, and per Q-158DIG A writes exact round-trip values: run_qtl_coloc.R `digits = I(17)` behind the flag; run_coloc_pair_r4.R :384 and :547 `digits = I(17)` (r4-only script, no flag); simulate_coloc_r4.R :229 posterior columns formatted with `sprintf(\"%.17g\")` before fwrite; measured after the change: 100% of 10⁵ uniform doubles and 0.8 − 2⁻⁵³ round-trip through each"
    - "Pre-existing tests that compare writer outputs with a tolerance (≤ 1e-12 / ≤ 1e-10) stay unchanged; no passing test is edited; only a pre-existing test that fails because of the precision change is edited, declared by id with the line and the reason"
    - "DRAFT (l) states that QTL and trait-pair posteriors (and the simulation posteriors, in (g) if it states a precision) are written so every value is recovered exactly before any threshold, and that QTL_legacy keeps the earlier 4-decimal rounding; old strings asserted unique (the E7 matched-rounding text is 15.8c2's)"
  artifacts:
    - path: "tests/ta_r4/test_qtl_json_precision.py"
      provides: "default-path byte identity + full-precision round trip + boundary cases"
  key_links:
    - from: "run_qtl_group_r4.QTL_ARMS"
      to: "run_qtl_coloc.R --json-full-precision"
      via: "qtl_command argv"
      pattern: "json_full_precision"
---

<objective>
Close review R4 as Carter chose (Q-157J "continue with your recommendations for the open items R4"; Q-158DIG A). QTL
posteriors are rounded to 4 decimals by jsonlite's default before thresholds. Planning measured that `digits = NA` is
15 significant digits, not full precision (0.79999999999999993 → 0.8; 8.1% of 10⁵ uniform doubles round-trip, 100%
with `digits = I(17)`), and that the r4 GWAS pair JSON and the simulation table have the same 15-digit limit. Carter
chose exact round-trip everywhere r4 thresholds read: I(17) behind an r4-only opt-in flag in the Track-B-shared
run_qtl_coloc.R (Track B byte-identical), I(17) in run_coloc_pair_r4.R, `%.17g` for the simulation posteriors.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question>.

Q-158DIG (answered 2026-11-25): file `W3f-carter-15-8-Q-158DIG-reply-2026-11-25.txt`, sha256
`ea8fe4cdaf4bbcf802d65e68c75e66d3b095777f0e518e9ed57c088d3246ceb4`, label
`A: Exact round-trip everywhere r4 thresholds (Recommended)`; question text in 15.8a's <question> table.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-purity-determinism-PLAN.md
@src/snakemake/scripts/run_qtl_coloc.R
@src/python/ta_r4/run_qtl_group_r4.py
@src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R

**Depends on 15.8b's fixture fix:** tests/ta_r4/fixtures/qtl_group_fixture.py `_job_env` locates the env by hash
(15.8b Task 2); the QTL fixture used by tests 1-7 imports it, so 15.8c cannot run before 15.8b.

**Standing rules:** 15.8 shared protocol (15.8a <protocol>); the 15.7f pattern for the Track-B-shared run_qtl_coloc.R
(flag default false, own DEC entry, default path unchanged; `PRE_157F_REF` in tests/ta_r4/test_purity_determinism.py:36).

**Verified at planning (99ab219d).**
- run_qtl_coloc.R `write_json(..., auto_unbox = TRUE, pretty = TRUE, na = "null")` with no `digits` at :295 (early /
  fatal statuses), :715 (no_qtl_cs), :740 (no_gwas_cs), :798 (success). jsonlite's default is `digits = 4`.
  Options are optparse (`make_option` list :29-90); `--exact-purity` (15.7f, :81-87, parsed :155-160) is the model.
- Rounded values reach thresholds through aggregate_qtl_coloc.py (reads the JSON; writes TSV with pandas, full repr)
  and assign_tiers.py.
- run_qtl_group_r4.py `QTL_ARMS` :29-34 (`exact_purity` "true" for QTL_A3/QTL_A2, None for QTL_legacy);
  `qtl_command` :92-109 appends `--exact-purity` after `--qtl-orient`. `abf_command` (fallback ABF) calls
  run_coloc_pair_r4.R `--mode qtl_abf`, which writes with `digits = NA` (:384, :547).
- Tests that pin the QTL argv: test_qtl_group_runner.py::test_legacy_argv_is_the_exact_pre_fix_argv (QTL_legacy; the
  legacy argv does not change), ::test_fixed_arms_argv (index lookups only), test_purity_determinism.py::
  test_qtl_command_passes_exact_purity_except_legacy (`cmd[-4:] == [--exact-purity, true, --output, OUT]` and
  `--exact-purity` right after the `--qtl-orient` value) → the new flag goes **before `--qtl-orient`**, which keeps all
  three green. test_purity_determinism.py::test_qtl_default_path_unchanged_without_the_flag runs QTL_A3's argv against
  the PRE_157F script, whose optparse rejects an unknown option → its helper `_qtl_run` (:338-350) must strip
  `--json-full-precision` as it strips `--exact-purity` (declared spec update; the test's purpose, the default path, is
  unchanged).
- Other r4 writers (measured here, re-measure in Task 1): cs_cross_purity.R write.table (15 significant digits;
  min_abs_corr is reported, not thresholded: no consumer in src/python/ta_r4 compares it to a cut-off);
  simulate_coloc_r4.R fwrite :229 (15 significant digits; pp_h4 / pp_h4_max feed E8 rates at the thresholds,
  estimands.e8_simulation_rates :496); run_susie_rss.R fit JSON (toJSON default 4 decimals; its floats lambda_hat,
  kriging_* feed E5 medians only, no threshold; D-28 frozen, not touched).
</context>

<new_tests>
tests/ta_r4/test_qtl_json_precision.py; N_new = 8.
1. `test_flag_rejects_values_other_than_true_false` (r4_heavy, Rscript)
2. `test_default_output_is_byte_identical_to_the_pre_15_8c_script` (r4_heavy; fixture statuses success, no_qtl_cs and a
   below-floor status; the pre-15.8c script from `git show <PRE_158C_REF>:...` as in the 15.7f test; `cmp` of the files)
3. `test_full_precision_round_trips_and_rounds_to_the_default` (r4_heavy; the oracle for "the default" is R: the
   full-precision JSON is parsed in R and re-serialized with jsonlite's default `toJSON` (no `digits`), and that text
   must equal the default run's text for every numeric field; Python rounding is not used. Measured in the job env:
   1.234567e-7 → 1.2346e-07, 3.2e-5 → 0, 0.00015 → 0.0001)
4. `test_boundary_posteriors_are_not_rounded_onto_the_threshold` (r4_heavy; the writer helper on 0.79999 and
   `0.8 - 2^-53`)
5. `test_qtl_command_passes_full_precision_except_legacy` (QTL_A3/QTL_A2 once, before --qtl-orient; QTL_legacy never)
6. `test_qtl_legacy_tiers_input_keeps_4_decimal_posteriors` (QTL_legacy JSON from the fixture has ≤ 4 decimals)
7. `test_r4_pair_and_simulation_writers_round_trip` (pair JSON, both modes, and the simulation table) (r4_heavy)
8. `test_every_r4_writer_is_classified` (parses the r4 R scripts and run_qtl_coloc.R for write_json / toJSON / fwrite /
   write.table calls by file and call text; each must appear in the test's own table as `exact`, `thresholded=False`
   or `track_b_default`; a new or unclassified writer fails)
Expected FULL: base full_15_8b.xml (expected 2,739) + 8 = 2,747. Declared spec updates:
tests.ta_r4.test_purity_determinism::test_qtl_default_path_unchanged_without_the_flag (its `_qtl_run` helper strips
the new flag), plus any pre-existing test that fails because of the precision change (none expected: the existing
writer comparisons are tolerance-based, ≤ 1e-12 / ≤ 1e-10; a failing one is edited only in that comparison and named
in the SUMMARY with the line).
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gates; DEC; writer inventory with measured precision</name>
  <files>.planning/DECISIONS.md</files>
  <read_first>
    - run_qtl_coloc.R :1-200, :270-300, :690-800; run_qtl_group_r4.py :1-130; run_coloc_pair_r4.R :370-390, :530-550
    - simulate_coloc_r4.R :1-30, :200-232; tests/ta_r4/test_purity_determinism.py :1-80, :330-430
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8c.txt` (this is PRE_158C_REF); `bash $Q8/gate_157j.sh`;
       `bash $Q8/gate_158.sh Q-158DIG`.
    1. DEC `DEC-2026-11-24-ta-r4-qtl-json-full-precision-flag` quoting Q-157J's R4 clause and Q-158DIG (`cat` + `cmp`);
       run_qtl_coloc.R is Track-B-shared, not D-28 frozen (as 15.7f's DEC-2026-11-20-ta-r4-qtl-exact-purity-flag).
    2. Inventory: every `write_json` / `toJSON` / `fwrite` / `write.table` / `to_csv` in src/snakemake/scripts/ta_r4,
       run_qtl_coloc.R, run_susie_rss.R and the python writers of r4 tables, with its consumer and whether a threshold
       reads it; measure each writer's round trip on 10⁵ uniform doubles and on 0.8 − 2⁻⁵³ in the r_coloc job env →
       `$Q8/writers_15_8c.tsv`. A thresholded writer not in the <context> list → STOP (scope grows; Carter).
    3. Commit the DEC (explicit paths; the reply file was committed by 15.8a).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && test -s data/r4/tmp/w3f/q158/writers_15_8c.tsv && git log -1 --format=%s | grep -q "15.8c"</automated>
  </verify>
  <done>Both gates passed; writers measured; DEC committed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: --json-full-precision (RED first); arms; the other writers per Q-158DIG; NCs</name>
  <files>src/snakemake/scripts/run_qtl_coloc.R, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R, src/snakemake/scripts/ta_r4/simulate_coloc_r4.R, tests/ta_r4/test_qtl_json_precision.py, tests/ta_r4/test_purity_determinism.py</files>
  <behavior>
    - Tests 1-8 per <new_tests>, using tests/ta_r4/fixtures (QF = the QTL fixture of test_purity_determinism.py)
  </behavior>
  <action>
    1. RED: tests 1-8 → fail (`$Q8/red_15_8c.txt`).
    2. run_qtl_coloc.R: `make_option("--json-full-precision", dest = "json_full_precision", type = "character",
       default = "false", help = ...)` after `--exact-purity`; parse/validate like EXACT_PURITY (:155-160). One helper
       `write_result <- function(x, path) if (JSON_FULL_PRECISION) write_json(x, path, auto_unbox = TRUE, pretty =
       TRUE, na = "null", digits = <D>) else write_json(x, path, auto_unbox = TRUE, pretty = TRUE, na = "null")`, where
       `<D>` is `I(17)` (Q-158DIG A); the four call sites call it. Nothing else changes.
    3. run_qtl_group_r4.py: `"json_full_precision": "true"` for QTL_A3/QTL_A2, None for QTL_legacy; `qtl_command`
       inserts `--json-full-precision <v>` immediately before `--qtl-orient`.
    4. run_coloc_pair_r4.R :384 and :547 `digits = NA` → `digits = I(17)`. simulate_coloc_r4.R writes the posterior
       columns (pp_h0 … pp_h4_max, r2_causal) with `sprintf("%.17g")` before fwrite (NA stays NA).
    5. test_purity_determinism.py `_qtl_run`: strip `--json-full-precision` and its value as it strips FLAG (declared).
    6. Green: tests 1-8, test_purity_determinism.py, test_qtl_group_runner.py, test_coloc_pair_r4.py, the simulation
       tests, tests/m3/test_qtl_coloc_allele_join.py, tests/m3/test_source_freeze_pins.py. Any other pre-existing failure
       → STOP, unless it fails because it compares a changed writer's output at 15 digits: then edit only that
       comparison, and declare it by id with the line and reason. Passing tolerance-based comparisons are not edited.
    7. NCs (`$Q8/nc_15_8c.txt`): helper ignores the flag → tests 3-4 fail; helper always full precision → test 2 fails;
       QTL_legacy given the flag → tests 5-6 fail; pair writer back to NA → test 7 fails; simulation column format
       removed → test 7 fails; the flag validation removed (any value accepted) → test 1 fails; a scratch
       R file with an unclassified `write_json(…)` call placed in src/snakemake/scripts/ta_r4 (then deleted) → test 8
       fails. md5-restore each.
    8. Commit (`feat(ta-r4-W3f): exact round-trip for every r4 thresholded writer; QTL behind --json-full-precision (15.8c)`).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_json_precision.py tests/ta_r4/test_purity_determinism.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_coloc_pair_r4.py tests/m3/test_qtl_coloc_allele_join.py tests/m3/test_source_freeze_pins.py -q -p no:cacheprovider</automated>
  </verify>
  <done>r4 QTL arms write exact posteriors; the default path and QTL_legacy are unchanged byte-for-byte; other writers per Carter.</done>
</task>

<task type="auto">
  <name>Task 3: DRAFT (l); FULL vs full_15_8b.xml; records (no push)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-json-full-precision-SUMMARY.md</files>
  <action>
    1. DRAFT script: in (l), after the sentence ending `a QTL job refuses to run if `coloc_priors.yaml` differs from
       them.` (assert unique) add: `QTL and trait-pair posteriors are written so that every value is recovered
       exactly before any threshold is applied; the earlier-pipeline QTL comparator keeps the earlier pipeline's
       rounding to 4 decimals.` If (g) states a precision for simulation posteriors, align it (else no (g) change).
       test_amendment_text.py and test_prelock_pilot_fits.py green.
    2. `$Q8/close.sh 15_8c`; `$Q8/check_15_8c.py` (base full_15_8b.xml; NEW = the N_new ids; declared per <new_tests>).
       Records: LOG (gates, writer table, NCs, check), PLAN-INDEX 15.8c row, STATE (NEXT = 15.8c2; NOT PUSHED), SUMMARY
       with both sections. fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8c.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py tests/ta_r4/test_prelock_pilot_fits.py -q -p no:cacheprovider</automated>
  </verify>
  <done>R4 closed in code and text with exact round-trip; FULL reconciled; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| R doubles → JSON/TSV → threshold | serialization precision decides boundary calls |
| r4 change → Track B | run_qtl_coloc.R is shared |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158c-01 | Tampering | Track B output drift | mitigate | flag default false; byte cmp of default output vs PRE_158C_REF script |
| T-r4-158c-02 | Tampering | a "full precision" that is not | mitigate | round-trip test on the written bytes and on 0.8 − 2⁻⁵³; mechanism chosen by Carter on the measurement |
| T-r4-158c-03 | Repudiation | E7 comparator changed | mitigate | QTL_legacy never gets the flag (test 5-6); DRAFT states its rounding |
</threat_model>

<verification>
- check_15_8c.py passes; default-path cmp test green; NCs recorded.
</verification>

<success_criteria>
- r4 thresholds read exact posteriors, stated in the DRAFT; Track B unchanged.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-json-full-precision-SUMMARY.md`
</output>
