---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a4
subsystem: ta-r4 W3f N1 eligibility on the oriented sumstats + DRAFT (Carter Q-158R2 D, Q-158OR A, Q-158PAL A, Q-158EL A)
tags: [R2, N1, eligibility, cap, orientation, DRAFT, Q-158EL]
requires: [ta-r4-W3f-sumstats-orientation-consumers]
provides: [manifests/w3f_fit_eligibility.tsv on the oriented inputs, DRAFT (c)/(i)/measured-counts orientation and audit text, tests/ta_r4/test_sumstats_orient_draft.py]
affects: [15.8b (base full_15_8a4.xml), 15.8f (R2 row; cumulative reconcile)]
tech-stack:
  added: []
  patterns: [re-measure behind must-be-identity checks, change set equal to the set shown to the decider, DRAFT numbers read from manifests and re-derived by tests]
key-files:
  created:
    - tests/ta_r4/test_sumstats_orient_draft.py
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/w3f_fit_eligibility.tsv
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/STATE.md
decisions:
  - "The 16,000-variant cap applies as pre-registered on the oriented inputs (Carter Q-158EL A); the measured change set equals the estimate set, so the table was re-pinned"
metrics:
  completed: 2026-11-25
---

# Phase ta-r4 Plan 15.8a4: eligibility on the oriented inputs and DRAFT Summary

I re-measured N1 eligibility on the oriented sumstats at cap 0, with no fit. All five identities hold. The fits whose
eligibility changes are exactly the 3 Carter was shown in Q-158EL: type 2 diabetes AFR × BMI_5q13_3 in AFR661_A3,
AFR661_A2 and AFR504_A3 now go over 16,000. Each measured count equals the planner's estimate. The table is re-pinned.
The DRAFT now states the orientation step, its counts, the collector audit and the new eligibility. R2 is resolved.

## Commits (this executor pushed nothing)

| Task | Commit | Content |
|------|--------|---------|
| 1 | 5fb24630 | Q-158EL DEC bullet; the reply was already committed as received in 1298b511 |
| 1 | cda233a8 | w3f_fit_eligibility.tsv re-pinned; tests 1-2 |
| 2 | 8d8b7bb6 | DRAFT edits (a0)-(e); tests 3-6 |
| 3 | (records commit) | LOG; PLAN-INDEX 15.8a4 COMPLETE; STATE ★ block; this SUMMARY |

## Gates

I added Q-158EL's question, sha256 and label to gate_158a2.sh. The question is plan line 60 without its leading
`Q-158EL `. I asserted it equal to line 1 of the reply after the prefix.

All five gates returned rc 0 (a4/gates.txt): gate_158a2.sh for Q-158OR, Q-158PAL and Q-158EL, plus gate_157j.sh and
gate_158r2.sh. Each of 4 NCs exits 2 (a4/gate_nc_15_8a4.txt):
- one byte changed in the copy;
- another label;
- one sha256 character changed;
- the question typed with its QID.

## Eligibility (Slurm 2099709, 83/83 COMPLETED, cap 0, no fit)

The run list is the same 83 keys as the pinned table's measured set, and every run reads an `.r4_oriented.` file. The
table still has 815 rows with the same keys.

Identities (data/r4/tmp/w3f/q158/a4/identities.txt), all PASS:
- (a) 0 of 732 bound rows differ outside sumstats_sha256.
- (b) bmi EUR and t2d EUR are unchanged in 26 of 26 measured rows.
- (c) n_variants_pre_ld == after_exact + after_both in 83 of 83.
- (d) No n_variants fell.
- (e) Δn ≤ Δpre-LD in 83 of 83.
- Catalog sha256, panel sha256 and panel_n_var are unchanged in 83 of 83.

| fit | pre-LD | after restriction | eligible |
|---|---|---|---|
| AFR661_A3 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,398 → 16,966 | true → **false** |
| AFR661_A2 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,398 → 16,966 | true → **false** |
| AFR504_A3 t2d AFR × BMI_5q13_3 | 23,718 → 28,840 | 14,343 → 16,841 | true → **false** |
| AFR661_A3 / A2 t2d AFR × PYHIN1_1q23 | 22,260 → 27,281 | 13,341 → 15,832 | true |
| AFR504_A3 t2d AFR × PYHIN1_1q23 | 22,260 → 27,281 | 13,265 → 15,718 | true |
| A3_ukb asthma EUR × SLC2A9_urate | 26,934 → 27,241 | 14,263 → 14,402 | true |
| A3_ukb hypertension EUR × PYHIN1_1q23 | 7,495 → 10,786 | 6,414 → 9,154 | true |

- The change set equals the Q-158EL set, so Q-158EL2 was not asked.
- Not eligible: 10 → 13. By arm, A3_ukb has 4 of 145 and AFR661_A3, AFR661_A2 and AFR504_A3 have 3 of 30 each. The
  other arms have 0.
- The table's sha256 went from 4a07d89c…3208 to 1058dd64…554f.

## DRAFT (old → new in data/r4/tmp/w3f/q158/a4/draft_oldnew.txt)

Each old string is unique. The script (a4/draft_15_8a4.py) reads every number from the manifests.
- (a0) The (c) inputs parenthetical now says the source sha256 are recorded and every production job verifies the
  oriented copies.
- (a) The 8 oriented sha256 follow the inputs list.
- (b) The collection clause now states the audit: 722,928 rows over 31 regions. Of these, 162,724 carry an allele key
  not in the catalog: 159,969 are restored by orientation and 2,755 are not fitted.
- (c) The orientation step: 159,969 rows, given per trait.
  - The 28,637 A/T and C/G SNPs are dropped from the fits by the allele-aware panel join. The all-variant A1 keeps
    them.
  - 31 of 31 catalogs are byte-identical.
- (d) (i) names the step.
- (e) The measured-counts row gains the per-arm counts on the oriented inputs: total 13, pre-LD 83/83.

test_amendment_text and test_prelock_pilot_fits are green: 30 passed and 2 skipped. The skips are the absent FINAL and
PUBLIC files, as before.

## Negative controls (data/r4/tmp/w3f/q158/nc_15_8a4.txt; all md5-restored)

| mutation | result |
|---|---|
| one measured n_variants_pre_ld +1 | test 1 RED |
| one sumstats_sha256 set to the source pin | test 2 RED |
| `revision` inserted in (c) (framing NC) | test_draft_extract_framing RED |
| one per-trait count changed | test 3 RED |
| 2,755 changed | test 4 RED |
| one sha256 character changed | test 5 RED |
| total 13 changed | test 6 RED |

RED evidence:
- Tests 1-2 fail against the pinned table (red_15_8a4_t12.txt). For test 1, identity (c) gives 22,684 vs 22,927.
- Tests 3-6 fail against the pre-edit DRAFT (red_15_8a4.txt).

## For Carter: asthma EUR EAF diagnostic (15.8a2; not a DRAFT edit, the plan does not cover it)

The diagnostic is in manifests/sumstats_r4_orientation_eaf.tsv.
- In asthma EUR, flipped rows have a median |ΔEAF| of 0.027, vs 0.005 for unflipped rows.
- 19 of the 225 flipped rows are above 0.2, and 14 of those 19 are indels. On SNVs only, the figures are 204 rows,
  median 0.0225 and 5 above 0.2.
- In every other file, flipped and unflipped rows agree about equally.
- No row is filtered by EAF. Do you want a rule for the asthma EUR indels?

## Slurm jobs

| Job | Purpose | Result |
|-----|---------|--------|
| 2099709_[1-83] | eligibility measurement (cascadelake, cap 0) | 83/83 COMPLETED 0:0 |
| 2100181 | FULL close (cascadelake c020n02) | 2,728 = 2,675 P / 53 S / 0 F |

## FULL

- Slurm 2100181 ran at HEAD 8d8b7bb6 and took 2h34m.
- QUICK 887 P / 2 S; HEAVY 340 P / 5 S; PINS 39 P.
- FULL 2,728 = 2,675 P / 53 S / 0 F (data/r4/tmp/w3f/q158/full_15_8a4.xml, sha256 a6f2132b…5567).
- check_15_8a4.py against full_15_8a3.xml (2,722 = 2,669 P / 53 S, read from the file):
  - 0 removed and +6, all passed;
  - 0 outcome changes;
  - totals 2,728 / 2,675 / 53 / 0;
  - CHECK PASS.
- The check's NC (base given as new) gives CHECK FAIL, rc 1.
- tests/m3/sparse_parent_benchmark.tsv is clean.

## Deviations from Plan

1. **[Records] Commit 1.** The plan asks for the Q-158EL reply plus its DEC bullet. The reply was already committed as
   received in 1298b511, with sha256 unchanged. So commit 1 is the DEC bullet only. The quote is `cmp`-equal to the
   file.
2. **[Process] Tests 1-2 committed first.** Commit 2 carries only tests 1-2, the file's first 77 lines. Tests 3-6 were
   written and RED before the DRAFT edit, and they land in commit 3, so every commit's test file is green.
3. **[Format] Measured-counts row.** The per-arm counts are written as `<arm> <k> of <n fits>` for all 8 arms in table
   order.
4. **[Records] STATE.md** got the project's ★ block, not the gsd-tools state commands. This is the same as 15.8a2-a3.
   REQ-OSF-PREREG and REQ-SNAKEMAKE-CI are not marked complete because they span the phase.
5. **[Premise note]** The plan's premise lists 10 ineligible measured rows, all asthma. The pinned table's 10 are A3_ukb
   asthma and t2d EUR × BMI_5q13_3 / PYHIN1_1q23 (4) plus asthma in the 3 AFR arms (6). The count matches; only the
   trait wording differs. It does not affect the change set.

## Declared spec updates

none

## New test ids

tests.ta_r4.test_sumstats_orient_draft::test_eligibility_on_oriented_inputs_reconciles
tests.ta_r4.test_sumstats_orient_draft::test_eligibility_manifest_records_the_oriented_sumstats
tests.ta_r4.test_sumstats_orient_draft::test_draft_orientation_sentence_matches_the_manifests
tests.ta_r4.test_sumstats_orient_draft::test_draft_collection_clause_matches_the_collector_audit
tests.ta_r4.test_sumstats_orient_draft::test_draft_inputs_list_the_oriented_sha256
tests.ta_r4.test_sumstats_orient_draft::test_draft_eligibility_counts_match_the_manifest

## Not done here (by design)

- No production fit, no OSF, no W4a-T3 lock. decision_rules.yaml stays locked: false, and n_regions_min stays 7.
- Nothing was pushed.

## Self-Check: PASSED

The test file, the re-pinned manifest, this SUMMARY and full_15_8a4.xml exist. Commits 5fb24630, cda233a8 and 8d8b7bb6
are in `git log`. check_15_8a4.py passes.
