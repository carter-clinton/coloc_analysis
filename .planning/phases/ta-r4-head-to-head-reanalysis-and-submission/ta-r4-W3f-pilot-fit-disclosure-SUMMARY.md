---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7i
subsystem: ta-r4 W3f OSF amendment DRAFT (F15 disclosure)
tags: [F15, pre-lock-pilot-fits, disclosure, manifest, sha256]
requires: [ta-r4-W3f-proxy-asthma-refit]
provides: [prelock pilot-fit manifest, F15 v3 paragraph in DRAFT (h), production-arm purpose line]
affects: [15.7j review suite and close]
tech-stack:
  added: []
  patterns: [inserted-from-file approved wording with an equality test, disk-enumerating sha256 manifest test]
key-files:
  created:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/prelock_pilot_fits.tsv
    - tests/ta_r4/test_prelock_pilot_fits.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15V3-reply-2026-11-24.txt
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-7-Q-F15-wording-as-approved-v3-2026-11-24.txt
  modified:
    - .planning/DECISIONS.md
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-pilot-fit-disclosure-PLAN.md
decisions:
  - DEC-2026-11-20-ta-r4-prelock-pilot-fit-disclosure
metrics:
  completed: 2026-11-24
---

# Phase ta-r4 Plan 15.7i: W3f pre-lock pilot-fit disclosure Summary

DRAFT (h) now discloses all 166 pre-lock pilot fits (20 production-panel, 18 earlier-catalog, 128 reproduction-route, of
which 39 stopped before fitting) and the 17 kernel runs. The text is Carter's approved v3, inserted from its file. Every
listed file is enforced by a sha256 manifest test, and no colocalization output from any pilot fit exists.

## Commits (none pushed)

| Step | Commit | Content |
|------|--------|---------|
| 1.0 DEC | b343872f | DEC-2026-11-20-ta-r4-prelock-pilot-fit-disclosure quoting Q-F15, Q-F15W, wording v2 |
| 1.2 | 42f3eb9c | manifests/prelock_pilot_fits.tsv (183 fits, 366 files) + tests 1-2 |
| 3.1 | ac61c486 | Q-F15V3 reply + wording v3, DEC addendum, sha256 pinned in the plan's <question> |
| 3.2 | 46e0b1fe | DRAFT purpose line + v3 in (h); test 3 |
| 3.3 records | (this commit) | LOG, STATE, PLAN-INDEX, SUMMARY |

## Results

- Gates: Q-F15, Q-F15W, v2 sha256 (gate_15_7i.txt); Q-F15V3 + v3 sha256 (gate_15_7i_v3.txt). Every NC was RED.
- Recount (data/r4/tmp/w3f/q157/pilot_recount.txt), v2 → disk:

  | item | v2 | disk |
  |---|---|---|
  | pilot fits | 146 | 166 |
  | reproduction-route fits | 108 | 128 |
  | production-panel / earlier-catalog / kernel runs | 20 / 18 / 17 | 20 / 18 / 17 |
  | production-panel fits with ≥ 1 set | 7 of 20 | 7 of 20, same list |
  | purity components | 109 | 109 |

  New in v3:
  - 39 of the 128 stopped before fitting: 31 among the original 108 plus 8 of the asthma fits (too_many_variants 32, no_variants 7).
  - 69 existing repro fits had exact purity recomputed in the recorded proxy.
  - 0 asthma fits are in that proxy.
- Coloc search (Slurm 2041110): 0 colocalization outputs reference measure_asthma_fix. Both planted NCs were found.
- FULL Slurm 2083696 (cascadelake): 2,694 = 2,641 P / 53 S / 0 F. Against full_15_7h2.xml: 0 removed, +3, 0 outcome changes.
  check_15_7i.py PASS; it FAILs on its NCs (the base fed in as new, and the Haswell run).

## Declared spec updates

None. No pre-existing test changed outcome or was edited. The 3 added ids are:
- tests.ta_r4.test_prelock_pilot_fits::test_manifest_lists_every_pilot_fit_on_disk
- tests.ta_r4.test_prelock_pilot_fits::test_manifest_sha256_match
- tests.ta_r4.test_prelock_pilot_fits::test_draft_paragraph_equals_the_approved_file_unwrapped

Plan-target amendment (orchestrator sign-off, 2026-11-24; arithmetic only): the FULL target is 2,694 = 2,641 P / 53 S / 0 F.
The plan's 2,692 = 2,639 P assumed a 2,689 base, but full_15_7h2.xml has 2,691. For 15.7j, the per-plan increments since
full_W3f.xml (2,555) are 32, 31, 18, 6 (7 new, 1 rename), 12, 13, 11, 4, 9, 3, so its target is 2,555 + 140 − 1 = 2,694. Its plan
still lists 15.7h2 as +7 and expects 2,692 = 2,639 P, and needs the same correction.

## Deviations from Plan

1. [Rule 4, Task 2] The plan's v3 template was false under Q-DROPASTHMA: it put the asthma fits in the proxy. It also counted
   the 20 asthma outputs twice ("A further 20" on top of 166). I redrafted it and stopped. Carter chose
   "v3 + all early exits (Recommended)", which is the draft plus the 39-of-128 sentence. That label differs from the plan's
   "Approve v3 (Recommended)", so it was gated as presented.
2. M = 69, not 70 as measured at planning.
3. The manifest's used_for for the 20 asthma outputs says they were withdrawn from the proxy. The plan expected
   w3f_region_contribution_proxy.tsv there. The orchestrator accepted this.
4. FULL target 2,692 → 2,694 (see above).
5. [Rule 3] FULL Slurm 2080101 was submitted without --constraint=cascadelake and ran on Haswell c200n03. 5 pre-existing tests
   failed the job guard's CPU check. The run is kept as full_15_7i_haswell_2080101.xml and was rerun as 2083696 with the
   constraint every earlier close used.
6. Slurm 2041108 was cancelled: its path pattern matched the repo name. It was resubmitted as 2041110 matching on basename.
7. The (h) paragraph is appended to the (h) line, joined by one space, so it stays inside (h).

## Known Stubs

None.

## Self-Check: PASSED

Commits b343872f, 42f3eb9c, ac61c486 and 46e0b1fe are ancestors of HEAD. The manifest, the test file and both v3 files exist.
src/, tests/ and config/ta_r4 are clean after FULL, and decision_rules.yaml is unchanged (locked: false, n_regions_min 7).
Nothing was pushed. W3f-carter-15-7-Q-F3N-reply-2026-11-24.txt is left untracked for 15.7j.
