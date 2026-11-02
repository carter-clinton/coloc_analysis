---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 12
slug: W3b-sh2b3-known-answer-and-findings
subsystem: ta-r4 known-answer reproduction
tags: [susie-rss, coloc-susie, sh2b3, known-answer, provenance, findings]
requires: [ta-r4-W3a-known-answer-routes]
provides:
  - data/r4/results/repro_sh2b3_r2/{fine_mapping/susie,coloc} (L15 fits + 9 R2-exact coloc JSONs)
  - data/r4/results/repro_sh2b3_L10/coloc (9 L10/iter-100 coloc JSONs)
  - manifests/known_answer_sh2b3.tsv (18 rows)
  - ta-r4-W3-KNOWN-ANSWER-FINDINGS.md (input to W4a amendment §(h))
affects: [W3c (starts only after `signoff verify W3b-T3`), W4a]
tech-stack:
  added: []
  patterns: [extracted-commit legacy code (bin/r4_extract_legacy_code.sh, path-aware), LSF exit-255 stall watchdog]
key-files:
  created:
    - src/python/ta_r4/sh2b3_known_answer.py
    - tests/ta_r4/test_sh2b3_known_answer.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_sh2b3.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sh2b3_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fit_cs_json_vs_rds.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/r1_structural_crosscheck.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3-KNOWN-ANSWER-FINDINGS.md
  modified:
    - bin/r4_extract_legacy_code.sh
    - src/python/ta_r4/arms.py
    - src/snakemake/rules/ta_r4_repro.smk
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "R2 provenance: L15 fits = run_susie_rss.R at 02c4404 + susie_policy_L15.yaml (500/1000, 9c87157); coloc = run_coloc_susie.R at c0f02b6 under la_multitrait_r"
  - "commands.fit_command and ta_r4_finemap.smk unchanged: the W0c/W3a legacy branch suffices"
  - "L10/iter-100 is reported as a separate measurement, never as the known answer (D-17)"
metrics:
  duration: "Tasks 1-2 2026-10-29 02:20-02:43 EDT; doc completion + wave close 2026-11-02 (~2.5 h, mostly the 64-min LSF close)"
  completed: "Tasks 1-2 2026-11-02; Task 3 pending"
  tasks: "2 of 3"
  files: 13
---

# Phase ta-r4 Plan W3b: SH2B3 Known Answer and Findings Summary (Tasks 1–2; Task 3 pending)

The SH2B3 R2 known answer reproduces byte-for-byte in its true configuration: L=15 fits from 02c4404 code with the
500/1000 policy, plus Stage-2 L=10 asthma/t2d, run through the c0f02b6 coloc script under la_multitrait_r. All 9
coloc JSONs are `cmp`-identical to `results/multitrait/coloc_susie_R2/`. The bmi–hypertension fingerprint matches on
5/5 fields. Under standard L=10 / iter-100, hypertension–t2d falls from 1.0 to 3.1e-08. All W2a/W2b/W3a/W3b
known-answer results are consolidated in `ta-r4-W3-KNOWN-ANSWER-FINDINGS.md`, which Carter has not yet reviewed.

## Commits

| Task | Commit | Subject |
|---|---|---|
| 1 | 0ef8b029 | feat(ta-r4-W3b): R2-exact SH2B3 code extraction + repro_sh2b3_r2 / L10 coloc rules |
| 2 | 57ed36a8 | test(ta-r4-W3b): SH2B3 known-answer table, R1 cross-check, findings report |
| close | (docs commit after this SUMMARY) | docs(ta-r4-W3b): LOG, STATE, SUMMARY |

Interleaved: 3b2d9bed (orchestrator handoff) is not this plan's commit.

## Task 1: provenance, rules, fire

- Provenance (each with a quoted evidence line and file:line in `ta-r4-LOG.md`, 2026-10-29 W3b entry): (a) 02c4404, (b) 9c87157
  policy max_iter_primary 500 / max_iter_retry 1000, (c) c0f02b6 + `bin/fire_canonical_susie_pairs_W2_strategy3.sh:11` Rscript.
- legacy_code_sha256.tsv: 2 + 5 = 7 rows.
- Fire: DAG 22 jobs (3 + 9 + 9 + 1 local). One LSF start failure (440334, exit-255 pattern), watchdog re-fire 440672. Dry-run
  "Nothing to be done" (re-checked 2026-11-02).
- `ls data/r4/results/repro_sh2b3_r2/coloc/*.json | wc -l` = 9; same for repro_sh2b3_L10 = 9.
- fits_repro_sh2b3_sha256.tsv: 3 + 3 + 18 = 24 rows; `sha256sum -c` OK.

## Task 2: table and findings

- `awk 'NR>1' known_answer_sh2b3.tsv | wc -l` = 18 (9 R2_exact + 9 L10_iter100). R2_exact match 9 + differ 0 = 9.
- L15 n_CS 13/5/3 and ld_overlap 170/589/622 equal the recorded values.
- `pytest tests/ta_r4/test_sh2b3_known_answer.py -q -rs`: 16 passed, 0 skipped (the live tests ran).
- Negative controls (2026-11-02; module restored, sha256 51784f77… re-verified):
  ```
  NC1 TOL = 1e-30:      FAILED tests/ta_r4/test_sh2b3_known_answer.py::test_tolerance_1e6[5e-07-true]   1 failed, 15 passed
  NC2 no fingerprint:   FAILED tests/ta_r4/test_sh2b3_known_answer.py::test_bmi_htn_fingerprint_is_absolute_not_relative   1 failed, 15 passed
  ```
  The original RED run (§B.2) from 2026-10-29 is not on record; these controls stand in for it.
- FINDINGS report: 8 sections. §8 quotes `ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md:25` and `:66` (line numbers re-read
  2026-11-02). All cited line numbers were re-checked (W2a :52/:66, W2b :71/:96/:151, W3a :124-156, FROZEN-NUMBERS :26/:72/:180-188/:222/:357/:361,
  sh2b3 W2 :29/:63/:102/:155/:159, CONTEXT :38-41, wave2 tracker :33-35).

## Wave close (§C, LSF 481675, c017n04, serial, 2026-11-02)

| Suite | Result |
|---|---|
| QUICK | 360 passed, 54 deselected (87.7 s) |
| HEAVY | 50 passed, 4 skipped (21m44s; the same 4 W5a/W5b skips) |
| Pins (D-28) | 39 passed |
| FULL | 1888 ids = 1838 passed + 50 skipped + 0 failed (40m02s, `data/r4/logs/full_W3b.xml`) |

Reconciled by test id against `full_W3a.xml`: common 1872, removed 0, added 16 (all `test_sh2b3_known_answer`), changed 0;
1872 − 0 + 16 = 1888. tests/m3 1299 (1265 / 34) unchanged. `sparse_parent_benchmark.tsv` restored. `git fsck --connectivity-only`
reported no missing or broken links before and after the commit (dangling blobs only).

## Deviations from Plan

1. **[Rule 2 - sourcing] FINDINGS §6/§7 lacked source paths.** Added `$W1:218` + Route C `niter` for "effective max_iter 100" in §6 and a
   section + path pointer on each §7 line. No number changed.
   - Before §6: "Route C Stage-2 fits (L=10, effective max_iter 100) for all 5 traits, …"
   - After §6: "… effective max_iter 100: the pre-02c4404 `max_iterations` argument fell through to the susieR default, `…W1-…-SUMMARY.md:218`;
     JSON `niter` bmi/hypertension/stroke 100, asthma 3, t2d 33 …"
   - §7: e.g. line 1 gained "(§5; `$MAN/known_answer_sh2b3.tsv`, `$MAN/fits_repro_sh2b3_sha256.tsv`)".
2. **LOG entry for W3b written late** (2026-11-02), dated 2026-10-29 (the work date), reconstructed from commit 0ef8b029, fire logs and manifests.
3. **Wave close re-run.** A close job (440842, 2026-10-29) had already run with identical ids/outcomes; its FULL summary line was cut off by `tail -3`.
   Re-run as 481675 with `tail -6`; the old XML is kept as `data/r4/logs/full_W3b.440842.xml`.
4. **ROADMAP not ticked.** W3b is not complete until Task 3 (Carter sign-off) passes.

## Known Stubs

None.

## Task 3 (checkpoint:human-action) — NOT STARTED

Carter reviews `ta-r4-W3-KNOWN-ANSWER-FINDINGS.md`. Resume token: first line `carter-approved YYYY-MM-DD`, then `instructions: …`.
No sign-off file, raw reply file or LOG sign-off entry has been written.

## Self-Check: PASSED

Files exist (7 Task-2 files + SUMMARY); commits 0ef8b029 and 57ed36a8 present in `git log`.
