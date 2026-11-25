---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a2
subsystem: ta-r4 W3f r4 sumstats inputs (orientation harmonization, Carter Q-158R2 D)
tags: [R2, orientation, allele-key, sumstats, Q-158R2, Q-158OR, Q-158PAL]
requires: [ta-r4-W3f-collector-drop-audit]
provides: [src/python/ta_r4/sumstats_orient.py, 8 oriented r4 sumstats copies pinned, manifests/sumstats_r4_orientation.tsv, manifests/sumstats_r4_orientation_eaf.tsv, data/r4/tmp/w3f/q158/gate_158a2.sh]
affects: [15.8a3 (switches consumers), 15.8a4 (eligibility + DRAFT), 15.8e (oriented-input multi-key bound), 15.8f (cumulative reconcile)]
tech-stack:
  added: []
  patterns: [string-exact sign toggle and Decimal 1-EAF, independent per-line verify of a rewritten file, must-be-identity re-measurement, cross-module count identity]
key-files:
  created:
    - src/python/ta_r4/sumstats_orient.py
    - tests/ta_r4/test_sumstats_orient.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158OR-reply-2026-11-25.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158PAL-reply-2026-11-25.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158EL-reply-2026-11-25.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-consumers-PLAN.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-eligibility-and-draft-PLAN.md
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv
    - .planning/DECISIONS.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - the six amended 15.8b-f PLAN files (commit 1)
decisions:
  - DEC-2026-11-25-ta-r4-sumstats-orientation
metrics:
  completed: 2026-11-25
---

# Phase ta-r4 Plan 15.8a2: r4 sumstats in the catalog's orientation Summary

Each of the 8 r4 catalog inputs now has one copy written in the r4 catalog's orientation:
data/r4/sumstats/<trait>.<anc>.r4_oriented.tsv.bgz + .tbi, sha256-pinned. A row in an r4 window is flipped only when its
allele key is absent from the region's catalog and its swapped key is present. A flip exchanges REF and ALT, toggles the
BETA sign on the string and sets EAF to 1 − EAF in exact decimal arithmetic. A/T and C/G SNPs follow the same rule
(Carter Q-158OR A, Q-158PAL A). Every other byte is unchanged.

Of 1,598,153 window rows, 159,969 were flipped. 28,637 of the flipped rows are A/T or C/G, and 2,387 of those have EAF
0.4-0.6. On the oriented files swapped_only is 0 in all 248 trait × region rows, and per source file the flips equal
the 15.8a audit's swapped-present rows. No consumer reads the copies yet (15.8a3), and no catalog, panel or
data/processed byte changed.

## Commits (this executor pushed nothing)

| Step | Commit | Content |
|------|--------|---------|
| T1.0 | 1298b511 | 15.8a2-a4 PLANs; the six 15.8b-f amendments; Q-158OR, Q-158PAL and Q-158EL replies as received; DEC-2026-11-25-ta-r4-sumstats-orientation; PLAN-INDEX 15.8a2-a4 rows, order line and base chain through full_15_8e (2,761) |
| T2.6 | 859458f9 | sumstats_orient.py; tests 1-14; sumstats_r4_orientation.tsv; sumstats_r4_orientation_eaf.tsv; sumstats_r4_sha256.tsv +16 rows |
| T3.2 | (records commit) | LOG; PLAN-INDEX 15.8a2 COMPLETE; STATE ★ block; this SUMMARY |

While this plan ran, the orchestrating session committed bda956a0 ("docs(handoff)", HANDOFF.json + STATE.md, "push
approved by Carter 2026-11-26"), and afterwards the branch was level with origin, so 1298b511 is on origin. 859458f9
and the records commit are local.

## Gates

- These gates returned rc 0:
  - gate_157j.sh.
  - gate_158r2.sh: Q-158R2, sha256 4183859f…bacb, label D.
  - The new gate_158a2.sh: Q-158OR (b4a87020…646a, label `A: Catalog orientation, catalogs unchanged (Recommended)`)
    and Q-158PAL (b5cde5c3…ec13, label `A: Flip by allele key like other SNPs (Recommended)`).
- gate_158a2.sh types `--question` as the plan's text minus the leading `<QID> `. A script extracts that text from the
  plan's <question> block, and only the Recommended label is allowed.
- Negative controls (data/r4/tmp/w3f/q158/a2/gate_nc_15_8a2.txt). Each of these returned rc 2:
  - one byte changed in the staging copy, for Q-158OR and for Q-158PAL;
  - one character of the Q-158OR question changed;
  - the question typed with its leading QID;
  - only a non-Recommended label allowed;
  - one sha256 character changed;
  - an unknown QID.
- DEC quotes: each is cmp-equal to its reply file. The negative control, a copy with one character changed, gives DIFFER.

## Per-file result (harmonize reports, data/r4/tmp/w3f/q158/a2/report_<t>.<a>.json; bgzip/tabix htslib 1.9)

| file | lines | window rows | exact | swapped_only = flipped | both | absent | flipped A/T-C/G | of them EAF 0.4-0.6 |
|---|---|---|---|---|---|---|---|---|
| bmi.EUR | 2,327,244 | 24,881 | 12,906 | 0 | 11,975 | 0 | 0 | 0 |
| t2d.EUR | 25,677,382 | 376,940 | 364,527 | 0 | 12,413 | 0 | 0 | 0 |
| t2d.AFR | 19,257,160 | 253,745 | 153,327 | 55,567 | 44,633 | 218 | 9,748 | 612 |
| hypertension.EUR | 7,160,657 | 104,047 | 56,921 | 34,871 | 12,131 | 124 | 5,951 | 611 |
| asthma.EUR | 27,843,603 | 377,364 | 345,303 | 2,412 | 28,378 | 1,271 | 784 | 17 |
| asthma.AFR | 20,231,905 | 261,183 | 213,118 | 3,798 | 43,446 | 821 | 1,347 | 13 |
| stroke.EUR | 7,511,476 | 107,772 | 59,222 | 36,195 | 12,257 | 98 | 6,227 | 624 |
| stroke.AFR | 5,259,724 | 92,221 | 52,293 | 27,126 | 12,579 | 223 | 4,580 | 510 |
| total | | 1,598,153 | 1,257,617 | 159,969 | 177,812 | 2,755 | 28,637 | 2,387 |

## Identities (all hold; data/r4/tmp/w3f/q158/a2/identities.txt, Slurm 2094864 and 2094863)

- (a) `measure` on the 8 catalog-source files equals orient_by_fit.tsv (b154b0fa…c4f1) row for row, 248 rows.
- (a2) The streaming harmonize counts equal the tabix measure per region × trait (classes, flipped == swapped_only,
  palindromic counts).
- (a3) verify_unflip passed on 8/8 files.
- (a4) There are 12 duplicate allele keys before and 12 after, all asthma EUR/AFR × HLA_6p21. SNP_IDs with more than one
  catalog-joined key: 0 before and 0 after.
- (b) On the oriented files swapped_only == 0 in 248/248 rows, after_exact == exact + swapped_only, after_both == both,
  and absent and n_rows are unchanged.
- (c) harmonize() on each oriented file flips 0 rows, and its output is cmp-equal to the decompressed oriented bytes in
  8/8 files.
- (d) Per source file, flipped == the audit rows with key false and swapped true, and absent == the audit rows with both
  flags false:
  - t2d AFR 55,567 / 218
  - hypertension 34,871 / 124
  - asthma EUR 2,412 / 1,271
  - asthma AFR 3,798 / 821
  - stroke EUR 36,195 / 98
  - stroke AFR 27,126 / 223
  - bmi and t2d EUR 0 / 0
  - totals 159,969 / 2,755
- (e) 44 files had the same sha256 before and after: the 8 inputs, every data/processed file in sumstats_r4_sha256.tsv,
  the 31 catalogs and the manifest (measured before pinning). After pinning:
  - only the manifest differs (a2/sha_after.txt);
  - its diff against a2/sumstats_manifest_before.tsv is exactly the 16 appended lines;
  - each appended sha256 equals the harmonize report;
  - verify_inputs on the 16 outputs + 8 inputs is OK.

## Slurm jobs

| Job | Purpose | Result |
|-----|---------|--------|
| 2094616 | before-state sha256 + verify_inputs | 44 files; OK |
| 2094641 | RED test 9 | ImportError (module absent) |
| 2094669 | GREEN test 9 | passed, 18.8 s |
| 2094696, 2094779 | NC (f) | RED (the first run's report line crashed on an empty message, so it was re-run) |
| 2094697_[0-7] | harmonize + verify_unflip | 8/8 rc 0 (harmonize 1:01-3:22, max RSS 633 MB; verify 0:14-2:13) |
| 2094798_[0-7] | idempotence, first run | cmp rc 1 on 8/8, from a script bug (see Deviations) |
| 2094863_[0-7] | idempotence, fixed | 8/8: 0 flips, cmp equal; NC cmp rc 1 |
| 2094864 | identities + manifests | ALL HOLD |
| 2094929 | verify_inputs 24 files; 14 tests; NC (g)-(j) | OK; 14 passed; 5/5 RED |
| 2094979 | FULL close (cascadelake c020n02) | 2,714 = 2,661 P / 53 S / 0 F |

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8a2.txt)

Each mutation was md5-restored, and the fast tests pass after restore. Every one of these made its test fail:

- (a) Flip on swapped_only or both: test 3 RED.
- (b) BETA via str(-float): test 2 RED (`-0.01` vs `-0.0100`).
- (c) EAF via str(1 - float): test 2 RED (`0.16349999999999998` vs `0.1635`).
- (d) Duplicate-key check removed: test 5 RED.
- (e) verify_unflip skipping outside-window lines: test 8 RED.
- (f) Test 9 `_compare` on a copy with one count changed (762 → 763): RED.
- (g) Test 10 `_check_oriented` on the source files: RED (FTO_16q12 t2d AFR).
- (h) Test 11 with one audit count +1: RED.
- (i) Test 12 with one sha256 character changed, once in an appended row and once in a pre-existing data/processed row:
  RED both times.
- (j) Test 14 on a re-bgzipped oriented stroke.AFR with one SE changed on an unflipped in-window line (data line 48,655,
  NC_RH): RED.

Two non-test checks also failed as they should: identity (c)'s cmp on a stream with one byte changed gave rc 1, and the
DEC quote cmp on a one-character-changed copy gave DIFFER.

## EAF diagnostic (manifests/sumstats_r4_orientation_eaf.tsv; not a filter)

Median |ΔEAF|, flipped / unflipped:

| file | flipped | unflipped | flipped rows above 0.2 |
|---|---|---|---|
| hypertension | 0.0167 | 0.0164 | |
| stroke EUR | 0.0157 | 0.0155 | |
| stroke AFR | 0.0057 | 0.0058 | |
| t2d AFR | 0.0026 | 0.0021 | |
| asthma AFR | 0.0019 | 0.0022 | 0 of 2,355 |
| asthma EUR | 0.0270 | 0.0047 | 19 of 225 |

For all but asthma EUR, flipped and unflipped rows agree with the reference about equally. Those flips are allele swaps,
not mislabels.

asthma EUR differs. The planner's figure (0.0225, 5 of 204) counted single-base SNVs only, and this run's SNV subset
gives exactly 204, 0.0225 and 5. The other 21 flipped asthma EUR rows are indels, and they carry 14 of the 19 rows above
0.2. This is recorded for 15.8a4 / Carter and not acted on here: the plan flips by allele key, and no row is filtered by
EAF.

## FULL

- Slurm 2094979, cascadelake c020n02, HEAD 859458f9, 2h27m.
- QUICK 875 P / 2 S; HEAVY 338 P / 5 S; PINS 39 P.
- FULL 2,714 = 2,661 P / 53 S / 0 F (data/r4/tmp/w3f/q158/full_15_8a2.xml, sha256 63e6db93…15ef).
- check_15_8a2.py against full_15_8a.xml (2,700 = 2,647 P / 53 S, read from the file): 0 removed, +14 (all passed),
  0 outcome changes, totals 2,714 / 2,661 / 53 / 0. CHECK PASS.
- The check's NC (base given as new) gives CHECK FAIL, rc 1.
- close.sh restored tests/m3/sparse_parent_benchmark.tsv (clean).
- Test times inside a dedicated run (2094929): tests 9 / 10 / 12 / 14 took 19 s / 19 s / 22 s / 27 s, all far under 15
  min, so none was restricted.

## Deviations from Plan

1. **[Rule 3 - Blocking, scratch script] First idempotence run.** The first idempotence array (2094798) reported cmp
   rc 1 on all 8 files. bgzip 1.9 refuses `-dc` on a `.bgz` file name ("unknown suffix -- ignored"), so cmp compared
   against an empty stream. The script now pipes the file through stdin (`bgzip -dc < file`). The re-run (2094863) is
   cmp-equal on 8/8, and a one-byte NC fails. No identity was relaxed, and the first run's outputs are kept in
   a2/idem_run1_bgzip_suffix_bug/.
2. **[Rule 1 - Bug, NC script] NC (f) report line.** NC (f)'s first run raised AssertionError as required, but its
   report line crashed on the empty message. I fixed the print and re-ran it (RED). The first output is kept as
   a2/nc_f_run1_printbug.txt.
3. **[Orchestrator directive] PLAN-INDEX edits moved into commit 1.** The plan puts them in Task 3; they went into
   commit 1 as instructed: the three 15.8a2-a4 rows, the order line and the base chain through full_15_8e (2,761). The
   exact orchestrator row text was not in the plan, so the executor wrote the three rows from each plan's objective, in
   the style of the existing rows. **Please check that wording.** Task 3 then marked 15.8a2 COMPLETE.
4. **[Additions within the interface]** No behaviour was relaxed:
   - The CLI has a `verify-unflip` subcommand (used by the Slurm array) and a `--repo` option (used by test 7).
   - `source_path(T, A)` and `row_class(fields, catalog)` are public helpers.
   - `check_out_path` also refuses an input path or a `.tbi` as the output.
   - `measure` also reports `swapped_only_palindromic` and `swapped_only_palindromic_eaf_0.4_0.6`.

## Declared spec updates

none

## New test ids

tests.ta_r4.test_sumstats_orient::test_classify_reproduces_the_measurement_rule
tests.ta_r4.test_sumstats_orient::test_flip_fields_is_exact_on_strings
tests.ta_r4.test_sumstats_orient::test_harmonize_flips_only_swapped_only_rows_in_a_window
tests.ta_r4.test_sumstats_orient::test_harmonize_is_idempotent
tests.ta_r4.test_sumstats_orient::test_harmonize_refuses_a_new_duplicate_allele_key
tests.ta_r4.test_sumstats_orient::test_harmonize_refuses_an_unexpected_header
tests.ta_r4.test_sumstats_orient::test_harmonize_refuses_an_output_outside_r4_sumstats
tests.ta_r4.test_sumstats_orient::test_verify_unflip_detects_any_other_change
tests.ta_r4.test_sumstats_orient::test_measure_reproduces_the_orchestrator_measurement
tests.ta_r4.test_sumstats_orient::test_oriented_files_have_no_swapped_only_rows
tests.ta_r4.test_sumstats_orient::test_flips_equal_the_collector_audit_counts
tests.ta_r4.test_sumstats_orient::test_oriented_pins_match_disk_and_track_b_is_unchanged
tests.ta_r4.test_sumstats_orient::test_null_window_scan_is_invariant_to_flips
tests.ta_r4.test_sumstats_orient::test_real_oriented_file_differs_only_in_flipped_rows

## Not done here (by design)

- No consumer was switched. paths.sumstats_path is unchanged; 15.8a3 switches the consumers and proves the catalog
  fixed point.
- There is no DRAFT edit (15.8a4), and R2 stays OPEN until 15.8a4.
- No production fit, no OSF, no W4a-T3 lock; decision_rules.yaml stays locked: false; n_regions_min stays 7; nothing was
  pushed by this executor.
- The oriented files are on /rs1 through the data/r4 symlink and are not git-tracked, as with the other
  data/r4/sumstats files. Their sha256 values are in sumstats_r4_sha256.tsv.

## Self-Check: PASSED

All files listed under key-files exist. Commits 1298b511 and 859458f9 are in `git log`. The 16 oriented files and
indexes exist and verify against the manifest. full_15_8a2.xml exists, and check_15_8a2.py passes.
