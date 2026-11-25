---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8c2
slug: W3f-qtl-legacy-rule-and-e7-rounding
type: execute
wave: 15.8c2
depends_on: ["ta-r4-W3f-qtl-json-full-precision"]
gap_closure: true
files_modified:
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/rules/ta_r4_qtl.smk
  - src/python/ta_r4/estimands.py
  - src/python/ta_r4/run_aggregation.py
  - tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py
  - tests/ta_r4/test_qtl_sweep_gwas_pph4.py   # test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order (declared)
  - tests/ta_r4/test_estimands.py             # only if an E7 column-list assertion names the columns (declared)
  - tests/ta_r4/test_run_aggregation.py       # fixture builder / column-list assertion, if needed (declared by id)
  - .planning/DECISIONS.md
  - .planning/HANDOFF.json                    # do_not: the 15.7g W6 tripwire string superseded (old string kept)
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J, Q-F3NL (`Keep legacy rule for QTL_legacy (Recommended)`, sha256 9b4c0bb0…a1) and Q-158E7R (`Add a matched-rounding column (Recommended)`, sha256 43a4d899…bd09) pass (15.8 protocol); otherwise nothing is edited"
    - "tiers_argv takes the QTL arm and passes `--nan-gwas-below-threshold` for QTL_A3 and QTL_A2 only, never for QTL_legacy (per-arm key in QTL_ARMS; the r4_qtl_tiers rule passes the wildcard arm); the argument order is otherwise unchanged; the rendered r4_qtl_tiers command per arm shows it (test)"
    - "E7 qtl_tier rows gain fixed_value_qtl_4dp (the QTL_A3 tier re-derived by assign_tiers.py with QTL_A3's own argv, on a temporary copy of QTL_A3's tierable summary whose PP.H0.abf … PP.H4.abf columns (aggregate_qtl_coloc.py:27-31) are rounded exactly as jsonlite's default digits = 4 writes them) and changed_qtl_4dp (frozen_value != fixed_value_qtl_4dp); `changed` is unchanged; other sections leave both columns empty"
    - "The rounding function reproduces jsonlite's default output, with R's default `toJSON` (no `digits`) as the oracle, on 10⁵ uniform doubles, 10⁵ log-uniform magnitudes from 1e-300 to 1, 10⁴ values in the 1e-5 to 1e-4 band and decimal ties (x.xxxx5), in the r_coloc job env (test)"
    - "Nothing frozen changes: QTL_legacy's argv and inputs, the committed QTL tables and known-answer manifests are byte-equal before and after (sha256), and the matched-rounding run writes only under a temporary directory"
    - "DRAFT (l) says the NaN-GWAS below-threshold rule applies to the A3 and A2 QTL arms and that the earlier-pipeline comparator keeps the earlier rule; DRAFT (e) E7 says QTL tiers are also reported with the A3 QTL posteriors rounded to 4 decimals as the earlier pipeline did; the Pre-Paste/(m) text `passed by r4_qtl_tiers only` is made arm-specific if present; old strings asserted unique"
    - "HANDOFF do_not: the 15.7g W6 tripwire string is kept unchanged and a new string, prefixed `SUPERSEDES the 15.7g W6 tripwire (15.8c2, Carter Q-F3NL):`, states the matching rule; key count +1; every pre-existing string present"
  artifacts:
    - path: "tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py"
      provides: "per-arm NaN rule, matched-rounding column, jsonlite rounding identity"
  key_links:
    - from: "ta_r4_qtl.smk r4_qtl_tiers"
      to: "run_qtl_group_r4.tiers_argv(qtl_arm, …)"
      via: "wildcards.qtl_arm"
      pattern: "tiers_argv"
---

<objective>
Carry out Carter's Q-F3NL and Q-158E7R answers. Q-F3NL: QTL_legacy, E7's earlier-pipeline comparator, keeps the earlier
NaN-GWAS rule; `--nan-gwas-below-threshold` is passed for QTL_A3 and QTL_A2 only (today tiers_argv passes it for every
arm, run_qtl_group_r4.py:277-280). Q-158E7R: after 15.8c, QTL_A3 posteriors are exact while QTL_legacy's are rounded to 4
decimals, so E7 also reports QTL_A3 tiers re-derived from 4-decimal posteriors, and `changed` can be read with and
without the rounding difference.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question>.
Q-F3NL (answered 2026-11-25): file `W3f-carter-15-8-Q-F3NL-reply-2026-11-25.txt`, sha256
`9b4c0bb009e5262c38262da953e2a009b8c1859447bbb0975a24c68c9162b6a1`, label `Keep legacy rule for QTL_legacy (Recommended)`.
Q-158E7R (answered 2026-11-25): file `W3f-carter-15-8-Q-158E7R-reply-2026-11-25.txt`, sha256
`43a4d89900c7225576a9edef1980716db999ca8c3193694305fca2c42376bd09`, label `Add a matched-rounding column (Recommended)`.
Question texts in 15.8a's <question> table.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-sweep-gwas-pph4-SUMMARY.md
@src/python/ta_r4/run_qtl_group_r4.py
@src/python/assign_tiers.py
@src/python/ta_r4/estimands.py

**Verified at planning (99ab219d).**
- run_qtl_group_r4.py:277-280 `tiers_argv(summary, gwas, pph4, tiers, sweep, py)` ends with
  `--nan-gwas-below-threshold` for every arm; ta_r4_qtl.smk:169-170 calls it from the r4_qtl_tiers rule, which runs for
  every QTL arm (QTL_legacy included, via repro_routeL). `QTL_ARMS` :29-34.
- tests.ta_r4.test_qtl_sweep_gwas_pph4::test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order (:266-279)
  pins the argv without an arm and the rendered QTL_A3 command → declared spec update: both of its calls, :267 (the
  expected list) and :275 (the rendered-command comparison), take `"QTL_A3"` as the new first argument; the expected
  list and the rendered assertion are otherwise unchanged. Any 15.7g test that measures
  QTL_legacy tiers under the flag (e.g. the `qtl_legacy_tiers_15_7g` measurement) is checked and, if it asserts the
  flag on QTL_legacy, declared with its id.
- assign_tiers.py: `assign_tier(…, nan_below=False)` :29; the script (`main` :317) is what the rule runs. The matched
  rounding re-runs the script as a subprocess with QTL_A3's argv on rounded copies in a tmp dir, so the production
  tiering code path is reused, not copied.
- estimands.e7_frozen_vs_fixed :472-478 builds qtl_tier rows from QTL_legacy (frozen) vs QTL_A3 (fixed) tiers;
  run_aggregation._qtl :283-294 loads the tier tables.
- The HANDOFF do_not string (15.7g) reads: "W6 tripwire (15.7g, NaN rule): before E7, read
  data/r4/logs/QTL_legacy/qtl_tiers.log; if any line `NaN-GWAS groups: N ...` has N > 0 (… QTL_legacy's qtl_tiers.tsv
  moved under --nan-gwas-below-threshold), STOP for Carter before E7. …". With Q-F3NL QTL_legacy no longer moves.
  The log cannot show whether the flag was passed, and assign_tiers.py is not touched. New string: "SUPERSEDES the
  15.7g W6 tripwire (15.8c2, Carter Q-F3NL): QTL_legacy runs without --nan-gwas-below-threshold. Before E7, render
  the QTL_legacy r4_qtl_tiers command (`snakemake -n -p` on the repro_routeL invocation) and check that it lacks
  --nan-gwas-below-threshold (if it has it, STOP for Carter); then read N from the `NaN-GWAS groups: N` line of
  data/r4/logs/QTL_legacy/qtl_tiers.log and record it in E7's notes as the number of regions where the QTL_legacy vs
  QTL_A3 comparison includes the NaN-rule difference."
</context>

<new_tests>
tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py; N_new = 6.
1. `test_tiers_argv_passes_the_nan_flag_for_a3_and_a2_only` (per arm)
2. `test_rendered_r4_qtl_tiers_command_per_arm` (r4_heavy; the rendered rule for QTL_legacy has no flag, QTL_A3 has it)
3. `test_round_like_jsonlite_default_matches_jsonlite` (r4_heavy; the sample of must_haves; oracle = R default
   `toJSON` in the job env)
4. `test_e7_qtl_tier_has_the_matched_rounding_columns`
5. `test_matched_rounding_isolates_a_boundary_flip` (QTL_A3 PP.H4 0.79996: exact tier below threshold, rounded 0.8
   tier at threshold; changed vs changed_qtl_4dp differ as expected)
6. `test_matched_rounding_changes_nothing_frozen` (sha256 of the inputs and committed tables before == after; outputs only
   under tmp)
Expected FULL: base full_15_8c.xml (expected 2,747) + 6 = 2,753. Declared:
tests.ta_r4.test_qtl_sweep_gwas_pph4::test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order, plus any id
named under <context> or in Task 2 step 3.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates; DEC; tiers_argv per arm (RED first)</name>
  <files>.planning/DECISIONS.md, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_qtl.smk, tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py, tests/ta_r4/test_qtl_sweep_gwas_pph4.py</files>
  <behavior>
    - Tests 1-2 per <new_tests>
  </behavior>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8c2.txt`; `bash $Q8/gate_157j.sh`; `bash $Q8/gate_158.sh Q-F3NL Q-158E7R`.
       DEC `DEC-2026-11-25-ta-r4-qtl-legacy-nan-rule-and-e7-matched-rounding` quoting both replies (`cat` + `cmp`).
    1. RED: tests 1-6 (`$Q8/red_15_8c2.txt`).
    2. QTL_ARMS gains `"nan_gwas_below_threshold": True` for QTL_A3/QTL_A2 and False for QTL_legacy;
       `tiers_argv(qtl_arm, summary, gwas, pph4, tiers, sweep, py=…)` appends the flag only when True; the rule passes
       `wildcards.qtl_arm` (`lambda w, input, output: … tiers_argv(w.qtl_arm, …)`). Declared edit of
       test_r4_tiers_argv_passes_the_flag_and_keeps_the_input_order (adds the arm argument; same expected list).
    3. Green: tests 1-2, test_qtl_sweep_gwas_pph4.py, test_qtl_group_runner.py. NCs (`$Q8/nc_15_8c2.txt`;
       md5-restore each): flag passed for every arm again → test 1 fails; the rule passes a literal `"QTL_A3"` instead
       of `w.qtl_arm` → test 2 fails for QTL_legacy. Commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_158.sh Q-F3NL Q-158E7R && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py tests/ta_r4/test_qtl_sweep_gwas_pph4.py tests/ta_r4/test_qtl_group_runner.py -q -p no:cacheprovider -k "argv or rendered or nan_flag"</automated>
  </verify>
  <done>QTL_legacy keeps the earlier NaN rule; A3 and A2 get the flag; per-arm test seen to fail under its mutation.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: E7 matched-rounding columns (RED first)</name>
  <files>src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py, tests/ta_r4/test_estimands.py, tests/ta_r4/test_run_aggregation.py</files>
  <behavior>
    - Tests 3-6 per <new_tests>
  </behavior>
  <action>
    1. `round_like_jsonlite_default(x)` in estimands (documented as reproducing jsonlite's default toJSON); test 3
       compares it with R's default `toJSON` in the r_coloc job env on the must_haves sample (it must give, e.g.,
       1.234567e-7 → 1.2346e-07, 3.2e-5 → 0, 0.00015 → 0.0001). A mismatch is fixed in the
       function, never in the test.
    2. run_aggregation: `_qtl_tiers_qtl4dp(repo)` writes rounded copies of QTL_A3's `qtl_coloc_summary_tierable.tsv`
       (columns PP.H0.abf, PP.H1.abf, PP.H2.abf, PP.H3.abf, PP.H4.abf) to a tmp dir, runs `tiers_argv("QTL_A3", …)` on the copy with QTL_A3's GWAS table and pph4
       config (outputs in the tmp dir), and returns the tier table, or None when QTL_A3's summary is absent (then the two
       columns stay empty); e7_frozen_vs_fixed gains `qtl_tiers_fixed_4dp=None`
       and fills `fixed_value_qtl_4dp` / `changed_qtl_4dp` on qtl_tier rows (columns appended at the end; empty
       elsewhere). 15.8d will append its own column after these.
    3. Green: tests 3-6, test_estimands.py, test_run_aggregation.py (a column-list assertion is a declared spec update
       with its id). NCs (md5-restore each): rounding by Python round() instead of the jsonlite rule → test 3 fails;
       rounded copy not used (exact tiers) → test 5 fails; the two new columns not written → test 4 fails; the matched
       run writing into data/r4/results instead of tmp → test 6 fails. Commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_qtl_legacy_rule_and_e7_rounding.py tests/ta_r4/test_estimands.py tests/ta_r4/test_run_aggregation.py -q -p no:cacheprovider</automated>
  </verify>
  <done>E7 reports QTL tiers with and without the rounding difference; nothing frozen changed.</done>
</task>

<task type="auto">
  <name>Task 3: DRAFT (l) + E7 + tripwire; FULL vs full_15_8c.xml; records (no push)</name>
  <files>.planning/HANDOFF.json, .planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-SUMMARY.md</files>
  <action>
    1. DRAFT script (old strings asserted unique): (l) `and a region whose trait-pair rows have no PP.H4 (all method
       `none`) is below threshold.` → `and, for the A3 and A2 QTL arms, a region whose trait-pair rows have no PP.H4 (all
       method `none`) is below threshold; the earlier-pipeline comparator keeps the earlier pipeline's rule for such
       regions.` (e) E7: after `the SH2B3 pairs and QTL tiers` add `(also reported with the A3 QTL posteriors rounded to 4
       decimals, as the earlier pipeline rounded them)`. If the Pre-Paste or (m) still reads `passed by r4_qtl_tiers
       only`, make it `passed by r4_qtl_tiers for the A3 and A2 QTL arms only`. test_amendment_text.py,
       test_prelock_pilot_fits.py green.
    2. HANDOFF (one script): append the new do_not string from <context>; assert the old string is unchanged, the list
       grew by exactly 1 and every pre-existing string value is present.
    3. `$Q8/close.sh 15_8c2`; `$Q8/check_15_8c2.py` (base full_15_8c.xml; NEW = 6; declared per <new_tests>). Records:
       LOG, PLAN-INDEX 15.8c2 row, STATE (NEXT = 15.8d; NOT PUSHED), SUMMARY with `## Declared spec updates` and `## New
       test ids`. fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8c2.py && grep -q "SUPERSEDES the 15.7g W6 tripwire" .planning/HANDOFF.json</automated>
  </verify>
  <done>Q-F3NL and Q-158E7R carried out in code, text and the W6 tripwire; FULL reconciled; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| E7 comparator → "changed" claims | a change must not mix in rule or rounding differences silently |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158c2-01 | Tampering | comparator rule drift | mitigate | per-arm argv test + rendered rule test; tripwire renders the QTL_legacy command |
| T-r4-158c2-02 | Tampering | mis-modelled rounding | mitigate | rounding function checked against R jsonlite incl. ties |
| T-r4-158c2-03 | Tampering | frozen outputs touched | mitigate | sha256 before == after; tmp-only outputs (test 6) |
</threat_model>

<verification>
- check_15_8c2.py passes; HANDOFF string asserts pass.
</verification>

<success_criteria>
- QTL_legacy reproduces the earlier rule; E7's QTL tier change is readable with and without the rounding difference.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-SUMMARY.md`
</output>
