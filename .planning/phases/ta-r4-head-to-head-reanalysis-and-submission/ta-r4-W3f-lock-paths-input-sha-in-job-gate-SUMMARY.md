---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.2
slug: W3f-lock-paths-input-sha-in-job-gate
subsystem: ta-r4 lock gate, in-job input integrity, fire script (W3f fix-up; review N3, N4, N5, T1)
tags: [w3f, lock-gate, sha256, in-job-gate, r4-fire]
requires: [ta-r4-W3f-producer-cap-fit-names-early-exit]
provides: [LOCKED_PATHS 29 entries, ta_r4.verify_inputs, commands.gate_command/verify_command/coloc_verify_command]
key-files:
  created: [src/python/ta_r4/verify_inputs.py, tests/ta_r4/test_verify_inputs.py, tests/ta_r4/test_in_job_gate.py, tests/ta_r4/test_data_sources_labels.py]
  modified: [src/python/ta_r4/r4_lock_gate.py, src/python/ta_r4/commands.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, src/snakemake/rules/ta_r4_qtl.smk, src/snakemake/rules/ta_r4_sim.smk, bin/r4_fire.sh, config/ta_r4/data_sources.yaml, .planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_lock_gate.py, tests/ta_r4/test_qtl_group_runner.py, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/fixtures/build_toy_workflow.py, tests/ta_r4/fixtures/qtl_group_fixture.py]
decisions:
  - "LOCKED_PATHS also locks the three input sha256 manifests (read by the in-job check) and the two known-answer tables (run_aggregation.py:27-28)"
  - "Fit/coloc input verification is production-only: 19 legacy NC catalogs are unlisted; QTL group verification applies to all QTL arms (all listed)"
commits: [82490835, 6312db61, d61fb081]
metrics: {completed: 2026-11-09, tasks: 3}
---

# 15.2 SUMMARY: N3 locked paths, N4 in-job input sha256, N5 in-job gate, T1 label

LOCKED_PATHS now covers every non-data file a production R4 run reads (18 → 29 entries). Every production fit, coloc and
QTL-group job checks the sha256 of its GWAS, catalog and harmonized QTL inputs before reading them. Every production
job re-runs the offline lock gate as its first shell command. The AFR T2D label now reads T2DGGI AFA, Suzuki 2024.

## Task 1: N3 (82490835)
- Added the six Codex paths, plus five found by measuring which files production runs read:
  `manifests/{sumstats_r4,catalogs,qtl_harmonized}_sha256.tsv` and `manifests/known_answer_{W3a,sh2b3}.tsv`.
  The measurement method and the excluded builder inputs are listed in the LOG.
- RED `t1_red.txt` 13F. GREEN `t1_green.txt` 77P / 2S (test_lock_gate + test_amendment_text, heavy included).
  NC (config/susie_policy.yaml removed from the list) `t1_nc.txt`: 3F (locked-paths check, completeness, drift case).
- `python -m ta_r4.r4_lock_gate paths` (cwd src/python): rc 0, prints all 29 entries, including the six.
- DRAFT (m) frozen-path list names the 11 new paths (paths only; rest of (m) is 15.5). Without it,
  `test_draft_extract_names_every_frozen_path` failed, as expected.
- Enforcer: `test_lock_gate.py::test_every_measured_dependency_is_covered_by_locked_paths` (41-entry R4_DEPENDENCIES)
  and `test_g_drift_in_each_new_locked_path` (11 cases: a committed one-byte change fails gate (g); restoring passes).

## Task 2: N4 (6312db61)
- Measured: production sumstats 8/8, catalogs 29/29, harmonized QTL files 23,310/23,310 listed. Repro catalogs 10/29
  (19 `variants_legacy/NC_*.tsv` unlisted), so fit/coloc verification is production-only and repro renders `true`.
- `verify_inputs.verify(files, manifests, repo)` + CLI (exit 1 names every mismatched, unreadable or unlisted file).
  Rendered after the gate in r4_run_finemap (sumstats + catalog) and in r4_coloc_pair / r4_coloc_A1 (both sumstats).
  run_qtl_group_r4 verifies every harmonized file, sumstats file and (allele-join arms) catalog before any row runs.
  On failure the CLI exits 1 and writes no .done.
- RED `t2_red.txt` (collection error), `t2_red2.txt` 11F / 10P → 21P. NC1 (skip unlisted) `t2_nc1.txt` 2F; NC2 (no
  verify call in run_group) `t2_nc2.txt` 4F. Plan verify Slurm 1782976: 64 passed (includes the real asthma.EUR heavy case).

## Task 3: N5 + r4_fire.sh + T1 (d61fb081)
- `commands.gate_command(stage)` is the first command of r4_run_finemap, r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group,
  r4_qtl_aggregate and r4_qtl_tiers. This is checked by parsing the `$SMK -n -p` listing from a fixture lock repo.
  Snakefile.ta_r4 is unchanged. Rendered gate in a fixture job: rc 0 before, rc 1 with "(g) locked paths drifted" after a
  committed change to config/susie_policy.yaml.
- bin/r4_fire.sh: the DIRTY check now uses the gate's own `paths` list. The comment now says what jobs check.
  RED with the old list: a dirty susie_policy returned rc 0 and reached SMK. With globbing on, a deleted tracked
  ta_r4_b.smk was missed (RED), so the line runs under `set -f`. Fire fixture tests: 5P (exit 2, REFUSED, SMK not called;
  this covers an untracked glob-matched new file plus a modified match, and the deletion).
- T1: `T2D AFR (T2DGGI AFA, Suzuki 2024)`. The label test checks every sumstats entry's label against trait_manifest source_study.
- RED `t3_red.txt` 16F / 3P; GREEN `t3_green.txt` 19P; NC1 (gate only in finemap) `t3_nc1.txt` 6F / 1P; NC2 (DIAMANTE
  restored) `t3_nc2.txt` 2F.

## Close
- Slurm 1783263 (c203n05): plan verify T3 104P (toy e2e both arms rc 0); HEAVY 115P / 4S (W5a/W5b skips) in 29m15s;
  PINS 39P; QUICK 566P / 1F / 2S. The failure is handled under deviation 4. QUICK rerun Slurm 1783856: 567P / 2S in 137.7 s
  (over the 120 s budget, carried to 15.6). FULL not run.
- fsck before/after each commit: 0 missing/broken. Push: 4c1956dd..d61fb081.

## Deviations from Plan
1. [Rule 2] Five extra LOCKED_PATHS entries (above). Without the three sha manifests, someone could change a data file and
   its record after the lock and still pass the in-job check.
2. [Rule 3] The fixtures now write sha256 records for their inputs (toy workflow, QTL group fixture).
   `test_qtl_group_runner::test_cli_exit_1_names_the_missing_row` used to delete a harmonized file, which now fails
   verification first. It now forces the row failure with an Rscript wrapper; its assertions are unchanged. A new test,
   `test_cli_absent_harmonized_file_fails_input_verification`, covers the deletion.
3. [Rule 2] The QTL group also verifies the catalog for allele-join arms, which the plan did not list.
4. [Rule 3] `test_run_aggregation::test_final_label_with_fixture_lock_and_signoff`: its fixture left the now-locked
   known-answer tables untracked, so the gate refused at check (h). The fixture now commits them; assertions unchanged.
5. bin/r4_fire.sh changes beyond the DIRTY line: PY/SMK can be set from R4_FIRE_PY/R4_FIRE_SMK (the minimal change the
   plan allows). The path list is computed in its own assignment, so a `paths` failure stops the script under set -e.
   The line runs under `set -f`.
6. Three per-task code commits instead of the single combined commit in Task 3 step 6 (orchestrator instruction).

## Known residuals (not changed)
- `config/ta_r4/trait_manifest.tsv` t2d AFR `evidence` still says "data_sources.yaml labels this file DIAMANTE 2022".
  That is now stale. The plan said to change data_sources.yaml only. For 15.5 / Carter.
- Sumstats `.tbi` indexes are not hash-checked (only bmi's r4 .tbi is listed). Coloc jobs do not byte-check the panel;
  fits check it by md5 through the receipt.

## Self-Check: PASSED
Commits 82490835, 6312db61, d61fb081 are on origin; the four created files exist.
