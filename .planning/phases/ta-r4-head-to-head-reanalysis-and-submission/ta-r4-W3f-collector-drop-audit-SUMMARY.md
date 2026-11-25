---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a
subsystem: ta-r4 W3f r4 variant catalogs (collector step audit, review R2)
tags: [R2, collector-drops, audit, allele-key, orientation, Q-158R2]
requires: [ta-r4-W3f-15-7-review-suite-and-close]
provides: [collector replay + drop classification, manifests/catalog_collector_drops.tsv, per-region audit files, 15.8 reply gates]
affects: [15.8a2 (sumstats orientation harmonization, Carter Q-158R2 D), 15.8b-15.8f (shared protocol, gate scripts)]
tech-stack:
  added: []
  patterns: [replay of an unmodified legacy step with a per-region identity assertion, staging-copy reply gate]
key-files:
  created:
    - src/python/ta_r4/collector_drop_audit.py
    - tests/ta_r4/test_collector_drop_audit.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalog_collector_drops.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158R2-reply-2026-11-25.txt
  modified:
    - .planning/DECISIONS.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - DEC-2026-11-24-ta-r4-w3f-15-8-open-items
metrics:
  completed: 2026-11-25
---

# Phase ta-r4 Plan 15.8a: W3f collector drop audit Summary

The r4 collector step (collect_region_variants.py) is now replayed and audited. In 31 of 31 r4 regions the replay keeps
exactly what the unmodified collector keeps, and its TSV is byte-equal to the on-disk raw catalog. Every in-window row it
does not keep is in a per-region audit file with one class: 1,598,153 input rows = 875,225 kept + 722,928 dropped, 0 of
class `other`. 162,724 dropped rows (67,626 distinct allele keys) carry a key that is not in the final catalog, and 65,753
of those keys are the swapped orientation of a catalog key. That stopped the plan at Task 2. The orchestrator then measured
that the fit's exact catalog join drops every sumstats row written in the other orientation (hypertension EUR 33.5%,
stroke EUR 33.6%, stroke AFR 29.4%, t2d AFR 21.9% of rows). Carter chose D, "Harmonize r4 sumstats to one orientation",
as the new plan 15.8a2. 15.8a therefore closes on its B path: no test 7, and no DRAFT (c) edit.

**R2: audit done; the lost-key consequence is the orientation drop; fix = Carter D, plan 15.8a2.** The review row R2
stays OPEN until 15.8a2.

## Commits (none pushed)

| Step | Commit | Content |
|------|--------|---------|
| T1.0 | 159c06ad | 15.8 planning set (7 PLANs), PLAN-INDEX 15.8 rows + protocol, six reply files as received, DEC-2026-11-24-ta-r4-w3f-15-8-open-items |
| T1.6 | 06b68482 | collector_drop_audit.py, tests 1-6, manifests/catalog_collector_drops.tsv |
| T3.1 | 8da7bfbe | Q-158R2 reply (D), DEC addendum with the orientation measurement, reply sha256 pinned in the plan |
| T3.3 | (records commit) | LOG, PLAN-INDEX 15.8a COMPLETE, STATE ★ block, this SUMMARY |

## Gates

- gate_157j.sh (Q-157J free text with "pin  libopenblas", two spaces) and gate_158.sh (Q-158DIG, Q-158R6S, Q-158E7R,
  Q-F3NL, Q-158R7) rc 0. NCs (data/r4/tmp/w3f/q158/gate_nc_15_8a.txt), each rc 2: one byte changed in a staging copy
  (cmp); the same mutated copy given to gate_reply.py with cmp bypassed (sha256); one space instead of two; one byte
  changed in a gate_158 copy; an unknown QID.
- gate_158r2.sh (Q-158R2, sha256 4183859f…bacb, label D) rc 0. NCs (gate_158r2_15_8a.txt), each rc 2: a one-byte-changed
  copy, a wrong question text, label A.
- full_15_7j.xml identical by id and outcome to full_15_7i.xml (2,694 = 2,641 P / 53 S / 0 F, read from the file).
- The 8 r4 sumstats pass ta_r4.verify_inputs; the 31 raw catalogs equal their pinned raw_sha256.

## Premise (collector drop points, verified by the replay)

| Step | Lines | Class(es) | Rows |
|------|-------|-----------|------|
| rsid keying, same rsid seen again | :104-123 | exact_duplicate / rsid_same_key_other_bytes / rsid_other_allele_key | 358,583 / 57,009 / 216,218 |
| rsid keying, allele-less stored record replaced | :111-123 | rsid_replaced_allele_less | 0 |
| unnamed exact repeat (alleles lower-cased) | :106-109 | unnamed_duplicate | 33,842 |
| five-column drop_duplicates | :142 | other | 0 (no-op, as planned) |
| unnamed at a CHR:POS carrying a named row | :143-150 | unnamed_at_named_position | 57,119 |
| second unnamed at the same CHR:POS | :151-155 | unnamed_same_position_other_alleles | 157 |
| allele-less row (any step, unless a byte-exact duplicate) | | allele_less | 0 |

Lost keys (real alleles, normalized key absent from the final catalog): 162,724 rows, of which 159,969 have the swapped key
present. By class: rsid_other_allele_key 154,562; unnamed_at_named_position 5,592; unnamed_duplicate 2,413;
unnamed_same_position_other_alleles 157. Distinct: 67,626 keys (65,753 swapped present; 1,873 not). 39,103 distinct lost
keys are in at least one production panel, exact or swapped (A3_1kg 24,507; A3_ukb 37,169; AFR661_A3 17,210;
AFR504_A3 16,915). Of the 1,873 keys with no swapped key in the catalog, 207 are in a panel
(data/r4/tmp/w3f/q158/lost_keys_panel_table_15_8a.tsv). The per-region table is in the manifest.

Orientation measurement (orchestrator, Slurm 2092423; copied to data/r4/tmp/w3f/q158/orient_by_fit.tsv, sha256
b154b0fa…c4f1, and measure_orient.py, 6d417291…347e): rows dropped by the exact join, over the 31 regions:
hypertension EUR 34,871/104,047 (33.5%); stroke EUR 36,195/107,772 (33.6%); stroke AFR 27,126/92,221 (29.4%); t2d AFR
55,567/253,745 (21.9%); asthma AFR 1.5%; asthma EUR 0.6%; bmi EUR and t2d EUR 0%. These were recomputed here from the
TSV and match the orchestrator's figures.

## Slurm jobs

- 2092056 (array 0-30): per-region audit, about 10 min and ≤ 0.42 GB each; all rc 0.
- 2092136-2092139: lost keys against the production panels (r_coloc Rscript), rc 0.
- 2092140: tests 1-6 with `--durations=0`, all passed; test 6 took 603 s (NC_ABO, the fewest input rows; under 15 min).
  Identity NCs (e) and (f).
- 2092261, 2092269: identity NCs (e2), (e3).
- 2093289 (FULL, `--constraint=cascadelake -t 04:00:00 --mem=48G`, c020n02, HEAD 8da7bfbe, 2h29m), rc 0.

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8a.txt)

- Module mutations, each md5-restored with the pyc cleared: (a) replay skips :151-155 → tests 1 and 5 RED; (b)
  rsid_other_allele_key reported as exact_duplicate → test 2 RED (and test 1); (c) the flag uses the un-normalized key →
  test 4 RED; (d) the swapped key counted as exact → test 4 RED.
- Identity guards (a mutated copy exec'd in-process; the source is not edited), on NC_ABO: (f) the TSV written with its
  index → ReplayMismatch "replay TSV != on-disk" OK; (e3) every later same-rsid row replaces the stored one →
  ReplayMismatch "kept rows != collect_variants" OK. (e) was refused by the row-accounting guard, not by the kept-equality
  guard it targeted. (e2), skipping the :143 step entirely, was not refused: all 82 unnamed_at_named_position rows of
  NC_ABO sit at a CHR:POS whose kept row's SNP_ID is that CHR:POS string (checked 82/82), so :151 removes them anyway. That
  is not a guard failure, but (e2) does not discriminate on this region; (e3) does.
- Test 6: n_dropped_exact_duplicate, n_kept and n_lost_keys each +1 in the manifest → test 6 RED, md5 restored.
- Catalog sha256 cmp: a one-byte change → rc 1. Panel measurement: a panel variant as-is → exact TRUE, its swap →
  swapped TRUE, a fabricated key → FALSE/FALSE.
- check_15_8a.py with full_15_7j.xml as the new file → CHECK FAIL rc 1.

## FULL

Slurm 2093289 (cascadelake c020n02, HEAD 8da7bfbe): QUICK 866 P / 2 S (5m33s); HEAVY 333 P / 5 S (60m53s); PINS 39 P;
FULL 2,700 = 2,647 P / 53 S / 0 F in 1h21m51s (`data/r4/tmp/w3f/q158/full_15_8a.xml`, sha256 41fdc36e…4d8c). Test 6 ran in
493 s inside FULL. tests/m3/sparse_parent_benchmark.tsv was restored, and src/, tests/ and config/ta_r4 were clean before the run.
`data/r4/tmp/w3f/q158/check_15_8a.py` against full_15_7j.xml (2,694 = 2,641 P / 53 S, read from the file): 0 removed,
6 added (the six ids below, all passed), 0 outcome changes, 0 failed, 2,694 + 6 = 2,700, totals (2700, 2647, 53, 0):
CHECK PASS rc 0 (`check_15_8a.txt`). NC: full_15_7j.xml given as the new file gives CHECK FAIL rc 1 (`check_15_8a_nc.txt`).

## Catalogs unchanged

catalog_sha_before_15_8a.txt == catalog_sha_after_15_8a.txt (cmp): 93 r4 files (final, raw and dropped catalogs ×31),
catalogs_sha256.tsv and catalogs_r4_unique_key.tsv. No catalog, panel or pin changed.

## Deviations from Plan

1. **[Rule 2] Two extra audit-file columns.** `source_row` (0-based data row in the source file) and `real_alleles` let
   each row be identified and the lost keys be recounted from the file alone. Commit 06b68482.
2. **[Rule 2] Class precedence documented.** An allele-less row dropped at rsid keying is `allele_less` unless it is a
   byte-exact duplicate. Allele-less rows removed by :143 or :151 are also `allele_less`. Both counts are 0 on the real
   data. See the module docstring.
3. **Task 2 / Task 3 path.** Q-158R2 was answered with a fourth option, D, after the orchestrator's measurement. On the
   orchestrator's instruction 15.8a closes on its B path: test 7 is not written, N_new = 6, and DRAFT (c) is not edited
   (15.8a2 rewrites it). The Q-158R2 question text is the orchestrator's revised text, pinned by its sha256 in the plan.
4. **close.sh diff.** One line differs from q157/close.sh: the junit path, `--durations=25`, and `tail -40` so the
   durations appear in the log.
5. **Panel R script.** An optional 4th argument (input path) was added after the four panel jobs ran, for its controls.
   The default input is unchanged.

## Declared spec updates

none

## New test ids

- `tests.ta_r4.test_collector_drop_audit::test_replay_keeps_exactly_what_the_collector_keeps`
- `tests.ta_r4.test_collector_drop_audit::test_same_rsid_other_allele_key_is_audited`
- `tests.ta_r4.test_collector_drop_audit::test_allele_less_record_replaced_by_real_alleles_is_audited`
- `tests.ta_r4.test_collector_drop_audit::test_unnamed_at_named_position_is_audited_with_key_flags`
- `tests.ta_r4.test_collector_drop_audit::test_unnamed_same_position_other_alleles_is_audited`
- `tests.ta_r4.test_collector_drop_audit::test_manifest_matches_disk`

## Not done here (by design)

No push, no production fit, no OSF, no W4a-T3 lock. decision_rules.yaml stays locked: false and n_regions_min 7. No
re-pin. DRAFT (c) is unchanged.

## Self-Check: PASSED

These all exist on disk: the module, the test file, the manifest, the Q-158R2 reply, full_15_8a.xml and the 31 audit files. Commits 159c06ad, 06b68482 and 8da7bfbe
resolve. check_15_8a.py PASS; decision_rules.yaml locked False; catalogs_sha256.tsv unmodified.
