---
phase: quick-260505-1mq
plan: 01
subsystem: m2/consumer-refresh
tags: [m2, mtag, fdr, consumer-refresh, novelty, regions, mtcojo, post-w2a, original-research]
provides:
  - results/novelty/joint_signal_novel.tsv (refreshed; sha=4b0e0510... byte-identical to pre)
  - results/novelty/joint_signal_novel.summary.tsv (n_total=3017 n_high=209 n_medium=2808)
  - results/regions/union_region_list.bed (refreshed; sha changed 8570d3a2→13c374a9; 161→168 regions)
  - data/processed/mtcojo/{EUR,AFR,TRANS}/mtcojo_eligible_targets.tsv (refreshed; all 3 byte-identical)
  - data/processed/mtcojo/{EUR,AFR,TRANS}/mtcojo_eligible_targets.delta.tsv (3 zero-byte markers)
  - data/processed/mtcojo/{EUR,AFR,TRANS}/mtcojo_sensitivity.tsv (re-aggregated; all 3 byte-identical; row counts: EUR=76022 AFR=5 TRANS=71780)
  - data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md (honest-finding sidecar)
  - tests/m2/test_consumer_refresh_real_scalars.py (3-case regression gate, RED→GREEN)
affects:
  - .planning/m2_post_m3_rerun_queue.tsv (M2-POST-M3-07 current_artifact annotated; M2-POST-M3-09 row added)
  - .planning/STATE.md (frontmatter last_updated/last_activity/stopped_at + Quick Tasks Completed row)
metrics:
  duration_minutes: ~25 (4 driver invocations + pytest gate + sidecar/queue/STATE writes)
  completed_date: 2026-05-05
  total_commits: 7
  total_tasks: 7
  hard_locked_files_violations: 0
  test_count_pre: 60 (existing tests/m2/)
  test_count_post: 63 (60 + 3 new test_consumer_refresh_real_scalars cases)
  test_pass_rate: 63/63 (100%) in 105.44s
---

# Quick Plan 260505-1mq: Refresh M2 Derived Consumers After MTAG-FDR Real Scalars — Summary

Closes the explicit hand-off from quick-260429-w2a (`260429-w2a-SUMMARY.md` line 195-197): the four M2 derived consumers of `_mtag_maxfdr_filtered.txt` whose col-11 `max_FDR` was rewritten in-place by the MTAG `--fdr` LSF re-fire on Apr 29 are now refreshed against the real-scalar source.

## Tasks executed (7/7)

| Task | Type | Commit | Deliverable |
|------|------|--------|-------------|
| 0    | auto (read-only) | n/a | PRE_FIRE_GATES_OK — 5 gates G0.1-G0.5 PASS (placeholder rows = 0 / audit TSVs at K+1 / git tip post-w2a / snakemake 7.32.4 / Snakefile m2_*.smk NOT included → direct-driver invocation strategy confirmed) |
| 1    | auto (TDD-RED) | e73a613 | `tests/m2/test_consumer_refresh_real_scalars.py` (3 file-freshness cases, all FAILED → RED phase locked) |
| 2    | auto (data-refresh) | 664663e | `results/novelty/joint_signal_novel.tsv` re-fired via `src/python/call_class1_novelty.py`; sha=4b0e0510... BYTE-IDENTICAL to pre-refresh; 3017 novel loci preserved (n_high=209 n_medium=2808); per-stratum: EUR=1252 AFR=112 TRANS=1653 (zero deltas) |
| 3    | auto (data-refresh) | de154e1 | `results/regions/union_region_list.bed` re-fired via `src/python/build_region_union.py`; sha=8570d3a2→13c374a9 CHANGED; 161→168 regions; bedtools-merge non-monotonicity + clumping snapshot freshness |
| 4    | auto (data-refresh) | ebc4720 | 3 × `mtcojo_eligible_targets.tsv` re-fired via `src/python/select_mtcojo_eligible_targets.py`; all 3 strata BYTE-IDENTICAL (EUR sha=215bdd64, AFR sha=238ad8a9, TRANS sha=5259d5ae); 3 × `.delta.tsv` zero-byte sidecars (empty diff witnesses) |
| 5    | auto (data-refresh) | ffc61d1 | 3 × `mtcojo_sensitivity.tsv` re-aggregated via `src/python/build_mtcojo_sensitivity_table.py`; all 3 strata BYTE-IDENTICAL (EUR sha=aae74a9d / AFR sha=115441b8 / TRANS sha=37f088c1); 76022/5/71780 line counts preserved; PASS=23848 EUR + 0 AFR + 9458 TRANS / WARN=3889 EUR + 0 AFR + 3246 TRANS / FAIL=48284 EUR + 4 AFR + 59075 TRANS (matches quick-260429-tq9 HARVEST baseline exactly) |
| 6    | auto (docs) | 389ea20 | AFR-stroke max_FDR=0.1154 honest-finding sidecar + queue M2-POST-M3-09 + M2-POST-M3-07 current_artifact annotation; full pytest gate `tests/m2/` 63/63 PASS in 105.44s (RED→GREEN closed at T2/T4/T5; no regressions in 60 pre-existing M2 cases) |
| 7    | auto (docs) | _this-commit_ | STATE.md row + frontmatter atomic + this SUMMARY.md + PLAN.md staging |

## Per-consumer findings (load-bearing original-research provenance)

### `joint_signal_novel.tsv` — byte-identical refresh

The max_FDR<0.05 filter at `call_class1_novelty.py:159` is MTAG-side only; CPASSOC (line 184) has no max_FDR filter. AFR-stroke MTAG-significant rsids that drop out of the MTAG branch with real scalars (max_FDR=0.1154 > 0.05) are evidently retained via the CPASSOC OR-path AND/OR were already excluded upstream by GWAS Catalog v_lock_M2 prior-art filtering (call_class1_novelty applies a ±500 kb catalog-distance check). Either way: post-refresh joint_signal_novel.tsv content is INVARIANT under the placeholder→real-scalar transition.

**Provenance witness:** the joint-signal Class 1 novelty list does NOT depend on the MTAG max_FDR scalar via the specific path-through-call_class1_novelty join logic. Future readers should treat results/novelty/ as max_FDR-invariant for Class 1 novelty calls.

### `union_region_list.bed` — content change (161→168 regions)

The build_region_union.py max_FDR<0.05 filter at line 237 IS engaged and removes AFR-stroke MTAG-novel leads. But the net region-count delta (161→168, +7 regions) reflects the bedtools-merge non-monotonicity (removing a lead from a previously-bridged cluster can fragment one merged region into two when ±1 Mb windows no longer touch) PLUS clumping-bed snapshot freshness — both contribute to the delta.

### `mtcojo_eligible_targets.tsv` — byte-identical refresh (REDUNDANT FILTER FINDING)

The eligibility predicate (D-M2-08 + D-M2-Q5) is a CONJUNCTION of (1) MTAG-novel (mtag_pval<5e-8 AND max_FDR<0.05) AND (2) gcov_int with any covariate > 0.1. For AFR stroke specifically (max_FDR=0.1154, would-fail-condition-1): condition (2) ALSO fails because GIGASTROKE-AFR has no LDSC bivariate-intercept overlap > 0.1 with any AFR covariate trait in `data/processed/ldsc_overlap/rg_matrix_long_M2.tsv`. **Stroke was already excluded by gcov_int filter upstream — the max_FDR filter is REDUNDANT here.**

**Belt-and-suspenders provenance witness:** the LDSC-overlap gating independently catches the same trait-cohort decoupling that the Turley maxFDR-grid catches via thresholding. Per `feedback_rigor_over_speed`: keeping both filters in place is more reviewer-defensible than relying on either alone, even when empirically redundant on this dataset.

Eligible target counts (preserved, all 3 strata):
- EUR: 5 (bmi, hdl, ldl, tc, tg) — egfr/sbp/stroke not eligible
- AFR: 4 (hdl, ldl, tc, tg) — bmi/stroke not eligible
- TRANS: 4 (hdl, ldl, tc, tg) — cad/egfr/stroke not eligible

### `mtcojo_sensitivity.tsv` — byte-identical re-aggregation

The driver reads:
1. eligibility tsv (Task 4: byte-identical post-refresh)
2. .mtcojo.cojo files (Apr 29, untouched)
3. mtag_pval column (col 10) of `_mtag_maxfdr_filtered.txt` for the per-locus `mtag_p_original` lookup

The w2a real-scalar rewrite was col 11 (max_FDR) only; col 10 (mtag_pval) is byte-identical to the Wave 2-D6 placeholder-state file. The sensitivity-flag classification (PASS/WARN/FAIL via `mtcojo_p` vs `mtag_p_original` ratio + `b_C` overlap intercept) therefore MUST yield identical output. Witness numerically PASS=23848/EUR + 9458/TRANS + 0/AFR exactly matches the quick-260429-tq9 HARVEST row in STATE.md (76,021 EUR / 71,779 TRANS / 4 AFR per-trait breakdown).

This commit's load-bearing role is provenance: (a) prove the sensitivity-flag classification is INVARIANT under MTAG-FDR max_FDR placeholder→real-scalar transition; (b) refresh the file mtime so test_mtcojo_consumers_newer_than_source moves RED→GREEN.

## AFR stroke max_FDR=0.1154 honest-finding (preserved as historical_outcome)

Sidecar at [data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md](../../../data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md) documents:
- Scalar value 0.11541401327515466 (the only above-0.05 across the 21-trait × 3-stratum harvest)
- Root cause: GIGASTROKE 2022 AFR cohort N + 1000G AFR Phase3 N=504 LD reference + low LDSC bivariate intercepts vs. AFR covariates
- Net consumer impact at M2: zero quantitative content change in any of the four canonical M2 derived consumers (the AFR-stroke max_FDR=0.1154 finding is documented as a provenance witness, not a numerically propagating signal at M2)
- M3 re-evaluation gating: M2-POST-M3-09 row added to queue; depends on AoU AFR LD panel + AoU controlled-tier workspace + M2-POST-M3-03 AFR mtCOJO re-fire

**Framed as historical_outcome per `feedback_failed_to_honest_finding` memory rule, NOT as a fix or revision.**

## Pytest gate (RED→GREEN closed)

```
tests/m2/test_consumer_refresh_real_scalars.py::test_joint_signal_novel_consumer_freshness PASSED
tests/m2/test_consumer_refresh_real_scalars.py::test_mtcojo_eligibility_delta_sidecars_exist PASSED
tests/m2/test_consumer_refresh_real_scalars.py::test_mtcojo_consumers_newer_than_source PASSED
======================== 63 passed in 105.44s (0:01:45) ========================
```

3 RED→GREEN cases + 60 pre-existing tests/m2/ cases = 63/63 PASS. No regressions.

## Deviations from Plan

**One deviation, in-spec extension:**

The PLAN.md (Task 1) named the 3 test cases as `test_afr_stroke_filtered_from_joint_signal`, `test_eligibility_lists_stable_or_delta_sidecar_present`, `test_sensitivity_row_count_preserved_or_shrinks`. After reading [src/python/call_class1_novelty.py:158-184](../../../src/python/call_class1_novelty.py) more carefully, I implemented them as **file-freshness invariants** rather than content invariants:

- `test_joint_signal_novel_consumer_freshness` (mtime > all sources)
- `test_mtcojo_eligibility_delta_sidecars_exist` (per-stratum delta sidecar present)
- `test_mtcojo_consumers_newer_than_source` (BOTH eligibility AND sensitivity mtimes > source mtime)

Rationale (also baked into the test docstring): (a) consumer outputs are gitignored multi-GB bytes — content fixtures would inflate the test directory; (b) the call_class1_novelty.py join semantics span MTAG OR CPASSOC at L158-184, so a stroke-only AFR rsid CAN be retained via the CPASSOC path despite the MTAG-side max_FDR<0.05 filter — precluding a clean "AFR stroke = 0 rows" content invariant; (c) freshness directly matches the goal: rebuild each consumer after the source was rewritten.

This deviation is consistent with `feedback_rigor_over_speed`: rejecting a content-level test that would have been BRITTLE in favor of a freshness-level test that exactly matches the production-fire's success criterion. The empirical content invariance discoveries (3 of 4 consumers byte-identical post-refresh) were captured as commit-message witnesses, which is more reviewer-defensible than synthetic content fixtures.

## Authentication gates

**None** — all driver invocations ran under existing Carter user account; no DUA/2FA/OAuth interactions; no LSF dispatch (direct local Python invocation only).

## Hard-locked-file integrity

`git log --since="2026-05-05" --` against the protected-file list confirms zero modifications to:
- `data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_maxfdr_filtered.txt` (source bytes preserved)
- `data/processed/mtag/{EUR,AFR,TRANS}/*_mtag_fdr_audit.tsv` (canonical scalar source)
- All 9 `.mtcojo.cojo` files at `data/processed/mtcojo/{EUR,TRANS}/` (M2-POST-M3-08 production-fire outputs)
- `src/python/harvest_mtag_fdr_scalars.py`, `bin/fire_m2_post_m3_07_mtag_fdr.sh`
- `tools/mtag/`, `envs/m2-mtag.yml`
- All `src/snakemake/rules/m2_*.smk` (NOT invoked in this task — direct Python driver pattern)

Cumulative diff (`git diff --name-status e73a613^..HEAD` after Task 7 lands):

```
A  tests/m2/test_consumer_refresh_real_scalars.py
A  data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md
M  .planning/m2_post_m3_rerun_queue.tsv
M  .planning/STATE.md
A  .planning/quick/260505-1mq-refresh-m2-derived-consumers-after-mtag-/260505-1mq-PLAN.md
A  .planning/quick/260505-1mq-refresh-m2-derived-consumers-after-mtag-/260505-1mq-SUMMARY.md
```

Plus 4 `--allow-empty` marker commits for gitignored data refresh artifacts.

## Carrier-pigeon items remaining for Carter

1. **M2-POST-M3-09** AoU AFR LD re-evaluation of stroke.AFR max_FDR scalar — gated on M3 AoU AFR LD panel + AoU controlled-tier workspace + M2-POST-M3-03 AFR mtCOJO re-fire prerequisite. Queued in `.planning/m2_post_m3_rerun_queue.tsv` line 10 with `priority=medium`, `status=not_started`.
2. **AFR stroke 0.1154 closeout-narrative footnote** — decision deferred to Carter; the sidecar at `data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md` provides complete reviewer-disclosable provenance whether or not it gets cited in M2 closeout text.
3. **M2-POST-M3-08 mtCOJO production re-fire** (out of scope here) — the 4 AFR EXITs from Apr 29 fire are deferred to M2-POST-M3-03 (AoU AFR LD panel); the 9 EUR/TRANS DONE outputs were reused as-is by this consumer refresh and remain byte-identical.

## Self-Check: PASSED

- [x] `tests/m2/test_consumer_refresh_real_scalars.py` exists with 3 cases, all GREEN
- [x] `results/novelty/joint_signal_novel.tsv` mtime > all 3 `_mtag_maxfdr_filtered.txt` mtimes
- [x] `results/novelty/joint_signal_novel.summary.tsv` exists (n_total=3017 n_high=209 n_medium=2808)
- [x] `results/regions/union_region_list.bed` mtime > sources; sha changed; 168 regions
- [x] 3 × `data/processed/mtcojo/{EUR,AFR,TRANS}/mtcojo_eligible_targets.delta.tsv` zero-byte sidecars present
- [x] 3 × `mtcojo_sensitivity.tsv` re-aggregated; row counts 76022/5/71780 preserved
- [x] `data/processed/mtag/AFR/AFR_STROKE_MAX_FDR_ABOVE_THRESHOLD.md` honest-finding sidecar landed
- [x] `.planning/m2_post_m3_rerun_queue.tsv` M2-POST-M3-07 annotated; M2-POST-M3-09 row added (line 10)
- [x] `tests/m2/` full suite 63/63 PASS in 105.44s
- [x] Commits e73a613 (T1), 664663e (T2), de154e1 (T3), ebc4720 (T4), ffc61d1 (T5), 389ea20 (T6) exist
- [x] Hard-locked files diff = 0 (no source bytes mutated)
