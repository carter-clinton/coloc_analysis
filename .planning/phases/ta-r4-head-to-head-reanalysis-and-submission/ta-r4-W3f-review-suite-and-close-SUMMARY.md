---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.6
subsystem: ta-r4 public text review, suite reconciliation, resume records (W3f close)
tags: [review, codex, brief-blind, FULL, reconciliation, handoff]
requires: [ta-r4-W3f-eligibility-measurement-and-draft, ta-r4-W3f-ukb-panels-biallelic, ta-r4-W3f-trackb-pins-indent]
provides: [banked W3f re-review + dispositions, FULL 2555/2502/53/0 reconciled by id, HANDOFF w4a_checkpoint refreshed, W4a depends_on]
affects: [ta-r4-W4a-amendment-draft-review-locks]
key-files:
  created:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md
  modified:
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/HANDOFF.json
    - .planning/STATE.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md
decisions:
  - "Code defects found by the re-review are OPEN for Carter, not narrowed in text (DEC-2026-11-04-ta-r4-w3f-fix-all chose code fixes; narrowing text to buggy code is the post-hoc choice the review guards against)"
commits: [5a6d4a01]
completed: 2026-11-19
---

# 15.6 SUMMARY: W3f brief-blind re-review, FULL reconciliation, records

## Task 1: re-review (5a6d4a01)

- Prompt = W4a wrapper + extract at 03b60744 only (sha256 6bce3707…7339). codex-cli 0.166.0, gpt-6.1-sol, rc 0.
  Output 35,587 B, sha256 e66f3c96d0e39fb5b8da6e5a267cc6c2fa4fa13b89500f28f7b29aaa4ac87994; banked block byte-equal (True).
- 23 findings (F1–F16, Q1–Q7) = 23 rows. DRAFT fixed 6 (F5 seed rule, F13 E7 A3 scope, F14 priors + runsusie rule,
  F16 Wallace 2026 correction, Q4 E6 n_snps, Q6 QTL prior refusal). OPEN for Carter: 11 code (F1–F4, F6–F12) + F15
  disclosure; Q2 optional; Q1 rejected; Q3, Q5, Q7 noted.
- test_amendment_text 21 P / 2 S; NC observed failing (test_draft_extract_framing on an inserted "pivot").

## Task 2: FULL (Slurm 1992683)

- QUICK 748 P / 2 S (150.7 s); HEAVY 306 P / 5 S; PINS 39 P; FULL 2,555 = 2,502 P / 53 S / 0 F.
- vs full_W4a.xml: 2069 − 6 + 492 = 2555; removed = the 6 renames, successors passed; tests/m3 +20 15.5c ids only, 0
  outcome changes; 1 new skip (asthma.AFR grch38_backup has no tabix index). vs full_15_5c.xml identical by id.
  check_W3f.py PASS and check_W4a.py (path pointed at full_W3f.xml) PASS; checker NCs FAIL on full_15_5b.xml and a
  synthetic XML. sparse_parent_benchmark.tsv clean.

## Task 3: records

- HANDOFF (keys 330 → 359, every pre-existing string kept), STATE block, LOG entry, PLAN-INDEX §B.6/§B.8 notes, W4a
  depends_on (one line). Push withheld by the orchestrator.

## Deviations

1. Plan premises predating 15.5a–15.5c, corrected as facts: STATE's latest block was 15.5c, not W4a (new block inserted
   above it); resume_on_reconnect had been rewritten for 15.5 (each step annotated DONE); the do_not / §B.6 note names
   both run_susie_rss.R lifts (N1 and the 15.5a guard), not "N1 only".
2. close_W3f.sh adds `export RSCRIPT=…` (as the 15.5b/15.5c close scripts) and ran with --mem 48G, not 32G (15.5c used
   48G and reached 48.00 GB).
3. Push (Task 3 step 6) not run: orchestrator instruction.

## Open items for Carter

F1, F2, F3, F4, F6, F7, F8, F9, F10, F11, F12 (code), F15 (disclosure); optional Q2 and the coloc_priors.yaml
citation_check note; Q6: a p12_primary other than 5×10⁻⁶ stops the QTL layer. All are HANDOFF production_blockers
`W3f_*` (optional ones under other_code_items.W3f_optional).

## Self-Check: PASSED

Review file and SUMMARY exist; 5a6d4a01 is in the log; decision_rules.yaml locked False; signoffs/ = W2c-T4.yaml, W3b-T3.yaml.
