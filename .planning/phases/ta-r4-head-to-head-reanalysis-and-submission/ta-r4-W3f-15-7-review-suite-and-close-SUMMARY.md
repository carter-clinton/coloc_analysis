---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7j
slug: W3f-15-7-review-suite-and-close
subsystem: ta-r4 W3f OSF amendment DRAFT / brief-blind review / suite reconciliation / resume records
tags: [ta-r4, W3f, 15.7, review, codex, reconciliation, HANDOFF]
requires: [ta-r4-W3f-pilot-fit-disclosure]
provides: [15.7 commits in DRAFT (m) and Pre-Paste, 12 RESOLVED Pre-Paste rows, banked 15.7j brief-blind review with dispositions, cumulative FULL reconciliation vs full_W3f.xml, HANDOFF w4a_checkpoint refresh]
affects: [15.8 (W3f157_* items), W4a-T3 lock presentation]
tech-stack:
  added: []
  patterns: [SUMMARY-parsed cumulative id reconciliation, byte-equal review banking, target-dict line edits for a mixed-escaping JSON]
key-files:
  created:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F3N-reply-2026-11-24.txt (committed; authored by Carter)
  modified:
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/DECISIONS.md
    - .planning/HANDOFF.json
    - .planning/STATE.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-null-window-reselection-SUMMARY.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-proxy-asthma-refit-SUMMARY.md
decisions:
  - "Review OPEN items R2–R7 and the Q-F3N premise were decided by Carter 2026-11-24/25 and carried to 15.8 (HANDOFF W3f157_*)"
  - "W4a depends_on left unchanged; 15.8f sets it (orchestrator 2026-11-25)"
metrics:
  completed: 2026-11-25
  tasks: 3
---

# Phase ta-r4 Plan 15.7j: W3f 15.7 review suite and close Summary

15.7 is closed. All 12 W3f_F* production blockers are RESOLVED. A fresh brief-blind Codex review of the changed DRAFT is
banked byte for byte: 14 findings, 7 fixed in DRAFT text only. Carter decided the code items, and they go to 15.8. FULL is
2,694 = 2,641 P / 53 S / 0 F, reconciled per id against full_W3f.xml (2,555 + 140 − 1) and identical to full_15_7i.xml.
Nothing is pushed.

## Commits (none pushed)

| Task | Commit | What |
|---|---|---|
| 1 | 99ab219d | DRAFT (m) + Pre-Paste (13 commits; 12 RESOLVED rows); LOG text-vs-code table; review banked; 6 DRAFT text fixes |
| 3 | (this commit) | 15.7h/15.7h2 SUMMARY records completion; Q-F3N reply + DEC addendum; HANDOFF; STATE; PLAN-INDEX; LOG; SUMMARY |

## Task 1: DRAFT, text vs code, review

- (m) has 47 distinct shas = 34 + 13 new; 47/47 are ancestors of HEAD (NC: a bogus sha gives rc 128).
- Text-vs-code table for F1–F15 at 72e4d1f4 (LOG): every DRAFT clause matches the code. One finding is outside the review:
  the Q-F3N question said QTL_legacy does not get `--nan-gwas-below-threshold`, but the code gives it the flag.
- Review: codex-cli 0.166.0, `-m gpt-6.1-sol`, read-only, rc 0.
  - Prompt sha256 a16f75f7…2bc5: 15.6's wrapper bytes around the extract (4,909 words).
  - Output: 37,290 B, sha256 `6d2060d718e0e200746d47faf8f5263c9aff28c530d0313151ff7c3ede4b1fe0`.
  - The banked block cmp-equals the raw stdout. NC: a tampered copy gives rc 1.
- Dispositions: 14 findings = 14 rows.
  - DRAFT fixed 7: R2, R3, R5, R7, Q1, Q4, Q5.
  - OPEN code 2: R4 (QTL JSON 4-decimal rounding) and R6 (BLAS not pinned or checked; job env libopenblas 0.3.34 vs the named-env lock's 0.3.32).
  - Rejected 1: R1. Noted 4.
- Text tests: 24 P / 2 S. NC: "pivot" makes test_draft_extract_framing FAIL; restored sha256-equal.

## Task 2: FULL

- Slurm 2086699, cascadelake c020n02, HEAD 99ab219d. QUICK 861 P / 2 S; HEAVY 332 P / 5 S; PINS 39 P; FULL 2,694 = 2,641 P / 53 S / 0 F.
- The first strict check STOPPED (rc 3): 15.7h and 15.7h2 SUMMARYs had no id lists, and 15.7h2 had no spec section (127 of 140 ids).
  - After records completion (orchestrator sign-off), `check_15_7j.py` strict PASS, rc 0.
  - Added ids per plan: 32 + 31 + 18 + 7 + 12 + 13 + 11 + 4 + 9 + 3 = 140.
  - Removed: exactly `test_draft_writes_exactly_19_draft_tables`; its `_20_` successor passed.
  - 0 outcome changes; the 27 declared spec-update ids all passed.
  - 2,555 + 140 − 1 = 2,694; skips 53. Identical to full_15_7i.xml.
- NCs: base as new FAIL rc 1; Haswell 2080101 FAIL rc 1; a SUMMARY copy missing the 15.7h2 spec section STOP rc 3.

## Task 3: records

- HANDOFF w4a_checkpoint:
  - 12 W3f_F* → RESOLVED, with plan, commit and Carter label; old text kept under _PRE_2026_11_20.
  - W3f157_R2–R7 and W3f157_QF3N_premise recorded as decided by Carter → 15.8.
  - read_first gains the 15.7j review.
  - region_contribution_proxy: A1 8/1/1, A2 3/2/5, k unknown, exact purity changed no set count, asthma excluded, n_regions_min 7 (Q-NREG "keep 7"); FLAG lines kept.
  - suite_baselines_ta_r4_latest = FULL 2694/2641/53/0; resume_on_reconnect is now for 15.8.
  - Keys 401 → 429. All 488 pre-existing strings are present (NC: 1 missing after deleting a PRE key).
- confirmatory_sha256 is unchanged: 9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5.
- W4a PLAN is untouched (`git diff` empty). Its depends_on stays `["ta-r4-W3f-review-suite-and-close"]` (the 15.6 plan) until 15.8f sets it.

## Declared spec updates

none

## New test ids

None. 15.7j adds no tests.

## Deviations from Plan

1. **Target totals (orchestrator amendment 1):** 2,692 = 2,639 P became 2,694 = 2,641 P. The 140 was re-derived from the SUMMARY id lists after the records completion; 15.7h2 is +9, not +7.
2. **Per-id base (amendment 2):** full_15_7i.xml.
3. **FULL constraint (amendment 3):** FULL ran with `--constraint=cascadelake`.
4. **Records (amendment 4 + 2026-11-25 sign-off):**
   - Committed W3f-carter-15-7-Q-F3N-reply-2026-11-24.txt.
   - Added a DEC addendum quoting it, with a cmp check; it records that the question's premise was wrong and that Carter's corrected answer (Q-F3NL) goes to 15.8.
   - The 15-8 replies and the 15-7j open-items reply are not committed here; 15.8a commits them.
5. **Proxy (amendment 5):** not re-run (done in 15.7h2); the HANDOFF proxy line is updated.
6. **[Rule 4] STOP at Task 2:** the 15.7h and 15.7h2 SUMMARY records were incomplete.
   - Resolved by the orchestrator's sign-off: their sections were added by copying from the new_tests files.
   - The parser header match was widened to "New test".
7. **[Rule 1]** My step-1 Pre-Paste F15 row quoted `**Pre-lock pilot fits.**`, which broke test_prelock_pilot_fits' count assertion. Fixed before commit 1.
8. **W4a depends_on not edited (orchestrator):** this replaces the plan's Task 3 step 2.
9. **HANDOFF written as line edits:** the file mixes escaped and literal non-ASCII, so a re-dump would have rewritten 150+ unrelated lines. The result is asserted equal to the script's target dict.
10. **NEXT = 15.8, not W4a-T3:** Carter's 2026-11-24/25 decisions on R2–R7 and Q-F3NL need code.

## Known Stubs

None.

## Self-Check: PASSED

Commit 99ab219d is an ancestor of HEAD. The review file exists, and its banked block cmp-equals `$Q/codex_out.md`.
`$Q/full_15_7j.xml` exists (27b0596e…), and check_15_7j.py strict returns rc 0. decision_rules.yaml is `locked: false` with
n_regions_min 7, and there is no signoff file. Nothing was pushed.
