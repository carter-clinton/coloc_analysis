---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5c
slug: W3f-trackb-pins-indent
subsystem: tests/m3 K-1 legacy-semantics pins (Track B, run_susie_rss.R)
tags: [gap-closure, tests, negative-controls, ta-r4, W3f]
requires: [ta-r4-W3f-ukb-panels-biallelic]
provides: [indentation-insensitive too_many_variants_payload pin, same-hunk re-indent cancellation in the symbol-scoped diff, 15.6 FULL scope for the W4a renames]
affects: [ta-r4-W3f-review-suite-and-close (15.6)]
tech-stack:
  added: []
  patterns: [in-memory negative controls (NC-K2 pattern), difflib/git parity, per-id junit reconciliation]
key-files:
  created:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-pins-and-push-reply-2026-11-19.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-n1-emit-line-reply-2026-11-19.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-SUMMARY.md
  modified:
    - tests/m3/test_variant_catalog_fallback_legacy_semantics.py
    - .planning/DECISIONS.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation: too_many_variants_payload compared after lstrip(' \\t') per line; same-hunk whitespace-only diff pairs cancel; added side = exactly the one N1 emit line (Carter Q1, Q3 A); the in-N1-payload and 2 -> 3 checks are the planner's"
metrics:
  completed: 2026-11-19
  tasks: 2
  commits: 3
  full_job: 1990243
  full_wall_s: 4663
---

# Phase ta-r4 Plan 15.5c: Track B K-1 pins ignore indentation Summary

The two tests/m3 K-1 pins now tolerate the N1 re-indent. The default too_many_variants payload is compared line by line
with leading spaces and tabs stripped. In the symbol-scoped diff, a whitespace-only pair inside one hunk cancels, and
the one N1 emit line is allowed. `PRE_K1_REF` stays dc4bbd2 and no src/ file changed. 20 new in-memory tests were
added, and every negative control was observed failing. FULL is 2,555 = 2,502 P / 53 S / 0 F.

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | fb08a75f | docs(ta-r4-W3f): DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation + Carter replies + 15.5c PLAN (15.5c) |
| 2 | dc15a630 | test(ta-r4-W3f): K-1 pins ignore leading whitespace; N1 emit line allowed; 20 in-memory tests (15.5c) |
| 3 | (this docs commit) | docs(ta-r4-W3f): 15.5c LOG, STATE, SUMMARY, deferred-items, 15.6 depends_on + FULL scope (no push) |

## Evidence

- Gate: both reply sha256 values match; the Q3 = A line grep returns 1; start HEAD 61201774, 0 ahead of origin. The
  re-measured (hunk header, raw line) set equals the plan's 4 pairs.
- RED under the stubs: 7 F / 24 P, i.e. the 2 original tests plus #2, #8, #9, #14 and #16. GREEN: 31/31. The collected
  id list equals the 11 old ids plus the 20 in <new_tests>.
- NCs: the observed failure messages are in the LOG (data/r4/tmp/w3f/indent/nc_messages.txt). The on-disk file was
  unchanged after every control.
- AST: 31 of 34 pre-existing top-level nodes are identical. The 3 excluded nodes are the module docstring and the two
  rewired tests.
- FULL 1990243, checked against full_15_5b.xml (check_15_5b.py PASS) and full_W4a.xml (check_W4a.py PASS). Both
  checkers fail in memory when given the wrong substrate.

## Deviations from Plan

- [Rule 3] The re-measure script inlines `_brace_block`/`_paren_block`, because a bare import of test_ld_read_path
  fails on `conftest.R_SUBPROCESS_TIMEOUT_S` (the plan warns about this). The script is throwaway; the module itself is
  unaffected.
- Small private helpers were added beyond the named interface: `_git_diff_vs_pre_k1`, `_splice_region`,
  `_reindent_after_first`, `_replace_once`, the perturbation tables and `_DIFF_MSG`. The test list and test ids are
  exactly the contract.
- For the diff NCs, the message check is the predicate's "symbol-scoped diff" phrase, not the literal "K-1". The
  removed-side message is kept verbatim as the plan requires, and it does not contain "K-1". The added-side, N1-payload
  and 2 -> 3 messages do cite K-1.
- The gsd-tools state/roadmap/requirements commands were not run. The plan restricts commit 3 to six named paths, and
  ROADMAP and REQUIREMENTS are not among them, which matches 15.5b.

## Self-Check: PASSED
