---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 14
slug: W3d-estimators-and-branch-classifier
subsystem: ta-r4 estimands, decision rule, coverage, aggregation (pre-lock analysis code)
tags: [estimands, branch-classifier, cluster-bootstrap, mcnemar, coverage, aggregation, pre-lock]
requires: [ta-r4-W3c-simulation-harness]
provides:
  - src/python/ta_r4/estimands.py (E1-E8, contrast_stats, categorize, output_status)
  - src/python/ta_r4/branch_classifier.py (classify, enumerate_truth_table)
  - src/python/ta_r4/coloc_coverage.py (expected_ids, check, CLI)
  - src/python/ta_r4/run_aggregation.py (17 tables, TABLES)
  - src/snakemake/scripts/ta_r4/cs_cross_purity.R
  - config/ta_r4/decision_rules.yaml (draft; locked false)
affects: [W3e (QTL tier/JSON paths read by run_aggregation), W4a (amendment cites the W3d commits; Carter locks kappa_cut, n_both_min, partial_rule x4, confirmatory block), W4b (locks decision_rules.yaml), W5b/W5c (coverage CLI), W7 (runs run_aggregation, no edits)]
tech-stack:
  added: []
  patterns: [selection and cut-offs read from yaml at call time, data-driven step precedence, NaN-padded vectorized cluster bootstrap, header-comment TSV status]
key-files:
  created:
    - config/ta_r4/decision_rules.yaml
    - src/python/ta_r4/estimands.py
    - src/python/ta_r4/branch_classifier.py
    - src/python/ta_r4/coloc_coverage.py
    - src/python/ta_r4/run_aggregation.py
    - src/snakemake/scripts/ta_r4/cs_cross_purity.R
    - tests/ta_r4/test_estimands.py
    - tests/ta_r4/test_contrast_stats.py
    - tests/ta_r4/test_branch_classifier.py
    - tests/ta_r4/test_cs_cross_purity.py
    - tests/ta_r4/test_coloc_coverage.py
    - tests/ta_r4/test_run_aggregation.py
    - tests/ta_r4/fixtures/estimand_fixtures.py
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "Precedence is data: classify() runs the steps in decision_rules.yaml `precedence` order (validated: all four names, partial_rule last), so the locked yaml is the decision rule"
  - "A1 outputs carry label A1_matched / A1_allvars (from the JSON `mode`); the confirmatory X for A1 is A1_matched with the yaml a1_varset filter applied"
  - "FINAL also requires the W4a-T3 fields to equal the locked config values (p12_primary, kappa_cut, n_both_min, partial_rule x4, confirmatory sha256), mirroring test_signoffs.check_locks"
  - "e1_paired_delta.tsv carries per-row values (level=row) and the dual-reporting summaries (level=summary, subsets both_have_cs and all_rows), because W7 figures read only tables"
metrics:
  duration: "~3 h 20 min (21:11 EST start; final wave close Slurm 1674938 ended 23:30 EST)"
  completed: "2026-11-03"
  tasks: 4
  files: 16
  commits: [db2bf8c9, 83b3240d, bd551895, aef3be84]
---

# Phase ta-r4 Plan W3d: Estimators and Branch Classifier Summary

E1–E8, the confirmatory `contrast_stats`, a total ordered branch classifier, the coloc coverage tool and the 17-table
`run_aggregation.py` are written and tested on synthetic data with hand-computed answers. All selection rules and cut-offs come from a
draft `decision_rules.yaml` (locked: false). No estimator was run on production data; none exists.

## Commits (cite in W4a as analysis-code commits, with W0d/W3c/W3e)

| Task | Commit | Subject |
|---|---|---|
| 1 | db2bf8c9 | E1-E8 estimators, confirmatory contrast_stats, total branch classifier, cross purity |
| 2 | 83b3240d | coloc coverage tool, pre-lock (B2) |
| 3 | bd551895 | run_aggregation.py, the single R4 table entry point |
| 4 | aef3be84 | fix: run_aggregation calls Rscript from PATH, not an /rs1 literal (caught by FULL run 1) |
| 4 | (docs commit after this SUMMARY) | wave close: LOG, STATE, ROADMAP, SUMMARY |

Library versions (smoke_dev): numpy 2.4.4, pandas 3.0.2. Exact binomials use `math.comb`; there is no scipy.

## Task 1: estimators, contrast_stats, classifier, cross purity

**RED** (`data/r4/tmp/w3d/red_t1.txt`): `49 failed, 1 passed, 33 errors`. The failures and errors are
`ModuleNotFoundError: ta_r4.estimands` / `ta_r4.branch_classifier` and the missing `cs_cross_purity.R`. The 1 pass is the yaml-shape
test, because the config was written first.

**GREEN:** plan verify `83 passed`. Hand-checked values:

| Check | Value |
|---|---|
| Sign test, 8+/0−/2 ties | 0.0078125 (ties excluded) |
| McNemar, b=10, c=0 | 0.001953125, direction X>A3 |
| McNemar, b=c | p = 1 |
| κ for [[20,5],[10,15]] | 0.4 |
| Wilson upper bound, 0/200 | 0.018846 |
| Bootstrap on constant 0.1 | [0.1, 0.1] |
| Cross purity, R=I CS with real \|r\| = 0.1 | 0.1 (fit purity 1) |

On between-cluster variance, the cluster bootstrap CI is more than 1.5× wider than a row bootstrap.

**Real manifest:** 100 confirmatory row_ids over 10 region_safe clusters (no NC_ regions). With the yaml edited to `ancestry: AFR`, the
selection is 30 AFR rows.

**Negative controls** (each restored sha256-identical; `data/r4/tmp/w3d/nc_t1_out.txt`):
```
NC1 delete partial_rule key ci_neg_mcnemar_ns   6 failed (coverage/counts/partial rows/KeyError)
NC2 swap precedence steps 1 and 2               3 failed (test_per_branch_counts, precedence pin, NON_INFORMATIVE example)
NC3 bootstrap resamples rows                    1 failed test_bootstrap_resamples_clusters_not_rows (re-observed after vectorizing)
NC4 row filter widened to negative_control      2 failed (NC-perturbation test, real-manifest 100-row test)
```

**Truth table** (`data/r4/tmp/w3d/truth_table.tsv`). By `via`: rule1_n_both 18, rule2_ci_includes_0 6, rule3_agree 4, partial_rule 8.
By branch excluding partial_rule: NON_INFORMATIVE 18, NO_SYSTEMATIC_DIFFERENCE 3, HETEROGENEOUS 3, INFLATION_SUPPORTED 2, DEFLATION 2.
Total 18 + 3 + 3 + 2 + 2 + 8 = 36.

```
n_both_ok ci    mcnemar     kappa_ok branch                   via
True      pos   sig_X_gt_A3 True     INFLATION_SUPPORTED      rule3_agree
True      pos   sig_X_gt_A3 False    INFLATION_SUPPORTED      rule3_agree
True      pos   sig_A3_gt_X True     HETEROGENEOUS            partial_rule:ci_pos_mcnemar_opposite
True      pos   sig_A3_gt_X False    HETEROGENEOUS            partial_rule:ci_pos_mcnemar_opposite
True      pos   ns          True     HETEROGENEOUS            partial_rule:ci_pos_mcnemar_ns
True      pos   ns          False    HETEROGENEOUS            partial_rule:ci_pos_mcnemar_ns
True      neg   sig_X_gt_A3 True     HETEROGENEOUS            partial_rule:ci_neg_mcnemar_opposite
True      neg   sig_X_gt_A3 False    HETEROGENEOUS            partial_rule:ci_neg_mcnemar_opposite
True      neg   sig_A3_gt_X True     DEFLATION                rule3_agree
True      neg   sig_A3_gt_X False    DEFLATION                rule3_agree
True      neg   ns          True     HETEROGENEOUS            partial_rule:ci_neg_mcnemar_ns
True      neg   ns          False    HETEROGENEOUS            partial_rule:ci_neg_mcnemar_ns
True      incl0 sig_X_gt_A3 True     NO_SYSTEMATIC_DIFFERENCE rule2_ci_includes_0
True      incl0 sig_X_gt_A3 False    HETEROGENEOUS            rule2_ci_includes_0
True      incl0 sig_A3_gt_X True     NO_SYSTEMATIC_DIFFERENCE rule2_ci_includes_0
True      incl0 sig_A3_gt_X False    HETEROGENEOUS            rule2_ci_includes_0
True      incl0 ns          True     NO_SYSTEMATIC_DIFFERENCE rule2_ci_includes_0
True      incl0 ns          False    HETEROGENEOUS            rule2_ci_includes_0
False     (all 18 ci x mcnemar x kappa_ok combinations)     NON_INFORMATIVE rule1_n_both
```

**For Carter (W4a amendment, explicit decision):** the 8 partial_rule rows are
(pos, ns), (pos, sig_A3_gt_X), (neg, ns) and (neg, sig_X_gt_A3), each × kappa_ok T/F. They are governed by four keys, all drafted as
HETEROGENEOUS. Carter also locks kappa_cut 0.6, n_both_min 10 and the confirmatory block (W4a-T3).

## Task 2: coloc coverage

**RED:** `6 failed` (ModuleNotFoundError). **GREEN:** `6 passed`.

**Expected totals** from the committed manifest and ARMS:
- **EUR:** 290 × 2 × 7 = **4060** (5 production arms + A1 matched/allvars).
- **AFR:** 30 × 2 × 5 = **300**.

The real repo CLI gives `missing=4060 extra=0 expected=4060` and `missing=300 extra=0 expected=300`, rc 1 (no outputs yet).

**Negative controls:**
- A complete AFR fixture tree gives `missing=0 extra=0 expected=300`, rc 0. With one file removed it gives `missing=1`, rc 1, and the
  missing path is named on stderr.
- Mutation `check()` drops missing: 3 failed. Restored sha256-identical.

## Task 3: run_aggregation

**RED:** `6 failed, 4 errors` (module and file absent). **GREEN:** `10 passed`.

**Negative controls** (`data/r4/tmp/w3d/nc_t3_out.txt`, `nc_t3_NC2_rerun.txt`):
```
NC1 gate removed                                  2 failed (unlocked writes nothing / CLI exit 2)
NC2 coloc globbed from every results dir          1 failed: AssertionError ['data/r4/results/repro_sh2b3_r2/coloc/...'] (path assertion)
NC3 'import math' in run_aggregation              1 failed (ast test)
NC4 confirmatory filter drops row_class (NC leak) 2 failed (NC perturbation moves branch_outcomes; n_rows 15)
```
The plan-specified controls are themselves tests:
- An unlocked yaml gives exit 2 and nothing written.
- `row_class: [primary, negative_control]` in a tmp yaml changes `branch_outcomes.tsv`.

The FINAL path works with a fixture lock commit, a W4b-T3 and a matching W4a-T3: all 17 tables are `# status=FINAL`, and `--draft` labels
them DRAFT.

## Task 4: wave close (§C, Slurm)

| Suite | Run 1 (1674027, HEAD bd551895) | Run 2 (1674938, HEAD aef3be84, 59m36s) |
|---|---|---|
| QUICK | 1 failed, 422 passed (-x stop) | 470 passed, 67 deselected (118 s) |
| HEAVY | 63 passed, 4 skipped | 63 passed, 4 skipped (same 4 W5a/W5b skips) |
| Pins | 39 passed | 39 passed |
| FULL | 1960 passed, 50 skipped, 1 failed | **2011 ids = 1961 passed + 50 skipped + 0 failed** (`data/r4/tmp/w3d/full_W3d.xml`) |

Run 1's failure was `test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src`. The cause was my
`RSCRIPT = "/rs1/.../r_coloc/bin/Rscript"` literal in run_aggregation.py. The guard was right: the code was fixed in aef3be84 and the test
was not edited.

**By id vs `data/r4/tmp/w3c/full_W3c.xml`** (`data/r4/tmp/w3c/reconcile.py`):
- 0 removed, 99 added (all passed), 0 changed; 1912 − 0 + 99 = 2011.
- The 99 added ids by module: contrast_stats 33, branch_classifier 24, estimands 22, run_aggregation 10, coloc_coverage 6,
  cs_cross_purity 4.
- No passed→skipped.
- tests/m3: 1299 ids (1265 passed / 34 skipped), unchanged.
- The run-1 XML is kept as `full_W3d_run1_1674027.xml`. Its reconciliation shows exactly that 1 id as changed.
- `sparse_parent_benchmark.tsv` is clean.
- `git fsck --connectivity-only` reports dangling objects only, before and after every commit.

## Deviations from Plan

1. **[Rule 3] Vectorized cluster bootstrap.**
   - Problem: QUICK was 97 s at W3c, and the per-draw loop added about 55 s.
   - Change: the bootstrap now does a NaN-padded gather plus nanmedian/nanmean in chunks of 1000. It is bit-identical to the loop on the
     same picks (median and mean checked).
   - Also: the six selection-perturbation tests use `bootstrap_B=1000` on a rules copy. Their property is selection-only; the real-rules
     positive control keeps B=10000.
   - Result: QUICK 118 s. That is under 120 s with little headroom, so the next wave may need to move tests to r4_heavy.
2. **[Rule 1] Rscript literal** (above). As a result, run_aggregation's cross-purity step needs `Rscript` from envs/r_coloc.yml on PATH
   when W7 runs it.
3. **Interface details the plan left open:**
   - `both_have_cs` rule strings are parsed as `<both|arm prefix> method(s) <method>`.
   - `contrast_stats` refuses any contrast not in `confirmatory.contrasts` or with a non-reference ref.
   - `output_status(repo)` and `with_status(obj, status)` carry the label (a dict key, or `DataFrame.attrs`).
   - E4 per-fit structure and E5 are per-fit tables; W7 joins them to |ΔPP.H4|.
   - E7 sections: fit_yield (W3a Route L real-LD vs R4 A3), sh2b3_pair (R2_exact vs A3_1kg p12_primary), flipped_share_region,
     flipped_share_qtl and qtl_tier.
   - E8 also counts sim files and `no_qualifying_pair` files per (scenario, gen_panel). Those files are counted, never filled in.
   - A shared fixture helper was added: `tests/ta_r4/fixtures/estimand_fixtures.py`.
4. **Test-code fixes before first green** (my new tests):
   - The repro "never opened" check matched the pytest tmp dir name `test_repro_...`. It now uses repo-relative paths.
   - The fixture repro output became a well-formed coloc doc, so NC2 fails on the path assertion, not on a crash.
   - The sim filename scenario `H3_r2_0.6` contains a dot. Parse it as `{region}.{scenario}.{gen}` using the first and last dots.

## Interfaces W3e/W6 must honour (run_aggregation reads them by fixed path)

- `data/r4/results/{QTL_A3,QTL_A2,QTL_legacy}/qtl_tiers.tsv`, the assign_tiers.py `--output` (columns region, ancestry, tier, ...). A
  sweep table must use a different name.
- QTL JSONs under `data/r4/results/QTL_A3/qtl/` (rglob `*.json`) carrying `qtl_orient_exact` / `qtl_orient_flipped`.

## Known Stubs

None. The QTL tables are empty until W6 writes the files above (by design; no fill-in).

## Threat Flags

None. No new network, auth or trust-boundary surface; the cross-purity subprocess runs a repo script on local files.

## Self-Check
Files exist: all 13 created paths in key-files, full_W3d.xml, truth_table.tsv, nc_t1_out.txt, nc_t3_out.txt. Commits db2bf8c9, 83b3240d,
bd551895, aef3be84 are in `git log`.

## Self-Check: PASSED
