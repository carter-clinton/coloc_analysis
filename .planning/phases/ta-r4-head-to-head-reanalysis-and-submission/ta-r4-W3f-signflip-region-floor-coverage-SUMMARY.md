---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.3
slug: W3f-signflip-region-floor-coverage
subsystem: ta-r4 confirmatory statistics and aggregation (W3f fix-up; review N7a, N7b, N6)
tags: [w3f, confirmatory, sign-flip, region-floor, completeness, coverage]
requires: [ta-r4-W3f-lock-paths-input-sha-in-job-gate]
provides: [estimands.region_signflip, estimands.ConfirmatoryIncomplete, contrast_stats(rows, X, ref, rules, manifest), run_aggregation exit 3, confirmatory.region_signflip, confirmatory.n_regions_min 7]
key-files:
  created: [tests/ta_r4/test_region_signflip.py, tests/ta_r4/test_confirmatory_completeness.py]
  modified: [config/ta_r4/decision_rules.yaml, src/python/ta_r4/estimands.py, src/python/ta_r4/run_aggregation.py, src/python/ta_r4/extract_paste_block.py, .planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_contrast_stats.py, tests/ta_r4/test_branch_classifier.py, tests/ta_r4/test_run_aggregation.py, tests/ta_r4/test_amendment_text.py]
decisions:
  - "The confirmatory mcnemar category is decided by the exact region-level sign-flip test (signflip_p < alpha and sign of T); row-level McNemar b, c, p stay as descriptive columns (DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor)"
  - "n_both_ok = n_both >= n_both_min and n_regions >= confirmatory.n_regions_min (7)"
  - "contrast_stats takes the pair manifest; its expected confirmatory ids come from the manifest, and any missing or duplicated output on either side raises ConfirmatoryIncomplete"
  - "run_aggregation runs coloc_coverage for EUR and AFR before build_tables; FINAL with any missing or extra output exits 3 and writes nothing; every table carries a '# coverage=' header line"
  - "Interim confirmatory_sha256 9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5 (was f6e6e90f...e9e3); final value recomputed in 15.5"
commits: [92caa306, 0ac1a15e, a36d4ad1]
metrics: {completed: 2026-11-09, tasks: 3}
---

# 15.3 SUMMARY: N7 region sign-flip test and region floor; N6 completeness and coverage-gated FINAL

The confirmatory direction test is now an exact region-level sign-flip test on d_r = b_r - c_r. A contrast needs at
least 7 contributing regions to be informative. The estimator refuses a row set that does not match the manifest's
confirmatory rows. FINAL aggregation refuses to write tables unless coloc coverage is complete. Codex's
counterexample (10 rows of one region) no longer classifies as INFLATION_SUPPORTED.

## Task 1: N7 (92caa306)
- `region_signflip(d_by_region, *, exact_max_k, B, seed)`: exact enumeration of all 2^k sign vectors (chunks of 65,536
  rows, int64) when k <= exact_max_k; otherwise seeded Monte Carlo with p = (1 + count) / (B + 1).
- `describe_contrast` adds n_regions and signflip_T/k/p/method/direction. `categorize` reads
  `confirmatory.n_regions_min` and the sign-flip result. `contrast_stats` refuses a `region_signflip` block whose
  subset/call differ from `mcnemar_kappa`.
- Hand-computed exact p values asserted with `==`: [1]x7 0.015625, [1]x6 0.03125, [1,1,1] 0.25, [3,1,1] 0.25,
  [2,-1] 1.0, all-zero 1.0. Also k=20 gives 2/2^20; 4 vectors are cross-checked against an independent
  itertools enumeration; MC (exact_max_k 5, k 12) lands within 4 SE of the exact p and is deterministic.
- 7 regions with d_r = [1,1,1,1,1,1,0]: n_both 14, n_regions 7, k 6, p 0.03125, n_both_ok True, mcnemar ns.
- Rows significant, regions not (10 X-only rows over 3 regions): row McNemar (10, 0, 0.001953125) is descriptive;
  signflip k 3, T 10, p 0.25: mcnemar ns, n_both_ok False.
- 8 regions with one discordant row each: p 2/256, sig_X_gt_A3 / sig_A3_gt_X by direction.
- RED `t1_red.txt` 31F / 80P. GREEN `t1_green.txt` 111P. The truth-table test prints
  `{'DEFLATION': 2, 'HETEROGENEOUS': 11, 'INFLATION_SUPPORTED': 2, 'NON_INFORMATIVE': 18, 'NO_SYSTEMATIC_DIFFERENCE': 3}`
  (18 + 3 + 11 + 2 + 2 = 36; 11 = 3 by rule 2 + 8 by partial rule). It passed in RED too: it pins unchanged behaviour.
- NC1 (category from row-level McNemar) `t1_nc1.txt` 9F / 102P, including test_rows_significant_regions_not.
  NC2 (n_regions term dropped) `t1_nc2.txt` 5F / 106P, including the floor cases. NC3 (`>` for `>=` in the exact count)
  `t1_nc3.txt` 17F / 94P, including all 6 hand-computed p cases.

## Task 2: N6 (0ac1a15e)
- Counterexample A on the pre-15.3 code (0ad0b742; `t2_cx_old.txt`): `('INFLATION_SUPPORTED', 'rule3_agree')`, n_both 10,
  CI [0.2, 0.2], McNemar p 0.001953125, matching the review. On the Task 1 code (`t2_cx_t1.txt`), the one-region
  version becomes NON_INFORMATIVE (the floor). A cherry-picked version, one X-favouring row from each of 10 regions, is
  still `('INFLATION_SUPPORTED', 'rule3_agree')` (n_regions 10, signflip p 0.001953125). Only completeness stops it.
- After: both raise `ConfirmatoryIncomplete` ("A2_identity: 90 of 100 missing ..."). Counterexample B (10-row manifest)
  gives `('NON_INFORMATIVE', 'rule1_n_both')`, with n_both 10, n_regions 1 and CI 0.2 / 0.2.
- Other cases tested: missing ref side named (first 5 ids), wrong p12_key does not count, A1 needs the matched varset,
  method none counts as present (n_rows 99 / n_both 99 of 100).
- run_aggregation FINAL (fixture lock): one missing A3_ukb output, or one extra JSON in A3_1kg/coloc, gives exit 3, no
  .tsv, and stderr with the counts and paths. Complete coverage writes FINAL. In DRAFT, the line 2 of all 17 tables is
  `# coverage=EUR missing=1 extra=0; AFR missing=0 extra=0`, and the same counts go to stderr.
- RED `t2_red.txt` 27F / 34P. GREEN `t2_green.txt` 91P. NC1 (ids rebuilt from `rows`, the old line) `t2_nc1.txt` 2F
  (counterexample A and cherry-picked: DID NOT RAISE). NC2 (coverage call replaced by a constant) `t2_nc2.txt` 3F
  (both FINAL exit-3 cases + the DRAFT header).

## Task 3: DRAFT block, interim sha (a36d4ad1)
- `render_confirmatory` adds a sign-flip line built from the yaml strings (subset, call, d_r, statistic, p,
  exact_max_k, Monte Carlo rule, B, seed) and an n_regions / n_regions_min line. The kappa/McNemar line now reads
  "row-level McNemar test (descriptive; not used for categories)". The rendered block replaced DRAFT (e) lines 79-88
  unchanged (10 lines -> 12). The rest of the DRAFT prose, including (f)'s "NON_INFORMATIVE if n_both < n_both_min",
  is left for 15.5.
- RED `t3_red.txt` 5F / 16P / 2S. GREEN `t3_green.txt` 62P / 2S (the W4b FINAL/PUBLIC skips).
- NC: a renderer hard-coding "n_regions_min = 7" (so the DRAFT still matches) `t3_nc.txt` 1F / 20P / 2S. Only
  `test_confirmatory_check_fails_on_a_changed_signflip_rule[path0-6]` failed. Direct check (`t3_nc_direct.txt`): the
  committed yaml is in the DRAFT verbatim (True); with n_regions_min 6 it is not (False).
- confirmatory_sha256: old f6e6e90f83fd14975d3afa04789c3dcf1a9211b8e3ddd38bf23c72f8cbe0e9e3 -> interim
  9fa410aa411fc2c682a4886dd25ca98d5dfd37f6968ecffc1a0a8860003888d5. Command (cwd src/python):
  `$PY -c "import yaml; from ta_r4.signoff import canonical_sha256; print(canonical_sha256(yaml.safe_load(open('../../config/ta_r4/decision_rules.yaml'))['confirmatory']))"`.
  The old value is recomputed from `git show 0ad0b742:config/ta_r4/decision_rules.yaml`.

## Close
- Slurm 1784345 (c207n08, tree = 0ac1a15e + the Task 3 working-tree edits that became a36d4ad1): plan verify
  T1 111P, T2 61P, T3 62P / 2S. QUICK 612P / 2S in 189.2 s wall (183.9 s in pytest). That is 567 (15.2) + 45 new ids:
  30 test_region_signflip, 11 test_confirmatory_completeness, 2 amendment, 1 category edge (15 → 16), 1 T13.
  It is over the 120 s budget; the slowest are pre-existing (track_b_isolation 13.9 s, coloc_none_states setup 12.7 s),
  and the new FINAL fixture tests take about 7 s each. HEAVY 115P / 4S (the W5a/W5b skips) in 32m00s. PINS 39P. FULL was not run
  (same §C list as 15.2).
- fsck before and after each commit: only dangling blobs, no missing or broken links. Push 0ad0b742..a36d4ad1.

## Fixture rule overrides (plan context rule)
None of the fixture repos carries its own decision_rules.yaml for this plan. The committed yaml was not changed to make
a fixture pass. The non-NON_INFORMATIVE branches are reached with fixtures of 8 regions. In-memory rule changes used by
tests: `n_regions_min` 3 (test_n_regions_min_read_from_rules); key deletions (missing-key tests); `n_regions_min` 6 and
`exact_max_k` 19 (amendment NC). The existing aggregation fixture (build_tree) has 3 regions, so both of its
contrasts are now NON_INFORMATIVE; no test asserts a specific branch for it.

## Deviations from Plan
1. [Rule 1] `test_contrast_stats::test_selection_is_read_from_the_yaml` used to assert n_rows == 0 for an AFR-selecting
   yaml. That case has no A2/A3_1kg outputs for the 5 AFR rows, so it now raises ConfirmatoryIncomplete (matched on
   `AREG__AFR`). The test still shows that selection comes from the yaml, and the behaviour change is the one N6 requires.
2. [Rule 2] `contrast_stats` raises ValueError if `region_signflip.subset` is not both_have_cs or its call differs from
   `mcnemar_kappa.call`, because the estimator uses one threshold for both.
3. [Rule 2] Extra completeness cases beyond the plan: cherry-picked rows over 10 regions (the case the floor
   cannot catch), wrong p12_key, A1 varset, and a named missing ref side.
4. The `# coverage=` header line is written in FINAL tables too (missing=0 extra=0), not only in DRAFT. Line 1 is
   still `# status=...`, so FINAL tables still start with `# status=FINAL\n`.
5. [Rule 3] test fixture `build_tree` now writes A3_ukb / A3_ukb_isect / A3_1kg_isect outputs, so its coverage is
   complete. `final_repo(tmp_path)` was factored out of the FINAL label test (assertions unchanged).
6. Three per-task commits instead of the single combined commit in Task 3 step 5 (orchestrator instruction). Commit
   92caa306 has two red DRAFT-text tests (test_amendment_text: cluster-rule check, rendered-block check) until the Task 3
   commit re-renders the block. 0ac1a15e has the same two red.

## Known residuals (not changed)
- `tests/ta_r4/test_lock_gate.py` R4_DEPENDENCIES cites `run_aggregation.py:27`, `:28`, `:36`. These are descriptive
  strings, not enforced, and the docstring edit moved the lines to 28, 29 and 37. For 15.6 (cite by quote).
- DRAFT (f) prose ("NON_INFORMATIVE if n_both < n_both_min", McNemar wording) and the (e) E2 sentence still describe
  the row-level test. Plan 15.5 owns the rest of the DRAFT text.
- QUICK wall time is over the 120 s budget (carried to 15.6, as in 15.2).

## Self-Check: PASSED
Commits 92caa306, 0ac1a15e, a36d4ad1 are on origin/m3-W2-aou-deltas. The two created test files exist. Raw outputs are
under data/r4/tmp/w3f3/.
