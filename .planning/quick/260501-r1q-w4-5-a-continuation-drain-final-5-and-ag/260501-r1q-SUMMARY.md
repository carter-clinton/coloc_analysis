---
phase: 260501-r1q
plan: 1
slug: w4-5-a-drain-final-5-and-aggregator-3rd-pass
status: completed
outcome: FAILED  # W4 PASS gate (too_few_snps <= 200) FAILED on substance; drain + aggregator-refresh succeeded mechanically
w5_gate: BLOCKED
duration_minutes: ~30
completed_iso: 2026-05-02T00:13:00Z
commits:
  - f165e57: feat(ta-sh2b3, W4.5) drain final 4 run_qtl_coloc — W4.5-A continuation
  - bf2a18a: feat(ta-sh2b3, W4.5) aggregator 3rd-pass + tracker v7 (FAILED, too_few_snps=1005)
predecessor_tracker: .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v6.json
successor_tracker: .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v7.json
w4_plan_pass_gate_definition: .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md
---

# Quick Task 260501-r1q: W4.5-A Continuation (Drain Final 4 + Aggregator 3rd-Pass) Summary

W4.5-A continuation closed. Drain + aggregator-refresh succeeded mechanically; W4 PASS gate FAILED on substance (too_few_snps = 1005 / 1274 = 78.9%, >= 800 cutoff). W4.5 SuSiE-RSS-layer fallback territory; remediation OUT OF SCOPE for this quick task.

## The 4 Missing qtl_coloc_ids (verbatim from /tmp/missing_5_qtl_coloc_ids.txt)

```
CXADR_F2RL1_6p21_ENSG00000154639_gtex_sqtl_Heart_Atrial_Appendage
FTO_16q12_ENSG00000140718_gtex_eqtl_Brain_Nucleus_accumbens_basal_ganglia
MC4R_18q21_ENSG00000166603_gtex_eqtl_Brain_Spinal_cord_cervical_c-1
SH2B3_12q24_ENSG00000111252_gtex_eqtl_Skin_Sun_Exposed_Lower_leg
```

**Note on count discrepancy (4 vs 5):** Tracker v6 reported "1270 of 1275 DAG steps" suggesting 5 missing run_qtl_coloc. Set difference (planned 1274 - on-disk 1270) yields **4** missing run_qtl_coloc targets; the 5th DAG step is the localrule `all_qtl_coloc` aggregation target itself (snakemake reported `run_qtl_coloc=4 + all_qtl_coloc=1 = 5 total steps`). Plan anticipated this with a WARN note and instructed to proceed.

## JSON Count Progression

| Stage                               | JSON count | Note                                                      |
| ----------------------------------- | ---------- | --------------------------------------------------------- |
| Pre-drain (W4.5-a re-fire stop)     | 1270       | Per tracker v6; supervisor PID 2670648 exited at 99.6%    |
| Post-drain (Task 1 complete)        | **1274**   | 4 LSF jobs (82066-82069) finished cleanly in ~4 min       |
| Post-3rd-pass (Task 2 complete)     | 1274       | Aggregator pass does not change per-id JSON count         |

## Aggregator Output Mtime Diff (V4 vs 3rd-pass)

W4.5-a re-fire dispatch baseline: `1777589595` (2026-04-30T16:53:15-04:00).

| File                          | V4 mtime (pre)                | 3rd-pass mtime (post)         | Status |
| ----------------------------- | ------------------------------ | ------------------------------ | ------ |
| qtl_coloc_summary.tsv         | 1777564412 (Apr 30 11:53)      | **1777680429 (May 1 20:07)**   | FRESH  |
| tier_assignments.tsv          | 1777567540 (Apr 30 12:45)      | **1777680509 (May 1 20:08)**   | FRESH  |
| gene_tissue_matrix.tsv        | 1777564468 (Apr 30 11:54)      | **1777680479 (May 1 20:07)**   | FRESH  |
| gene_tissue_long.tsv          | 1777564468 (Apr 30 11:54)      | **1777680479 (May 1 20:07)**   | FRESH  |
| pph4_threshold_sweep.tsv      | 1777567540 (Apr 30 12:45)      | **1777680509 (May 1 20:08)**   | FRESH  |
| qtl_coloc_manifest.tsv        | 1777564356 (Apr 30 11:52)      | 1777564356 (Apr 30 11:52)      | STALE (correct: built upstream from regions config, not downstream from JSONs) |

**5 of 6 aggregator outputs FRESH.** `qtl_coloc_manifest.tsv` correctly remains at V4 mtime — it is built from upstream config (`regions_curated.csv`) by `build_qtl_coloc_manifest`, NOT downstream from per-id JSONs. Plan's "acceptable downgrade" footnote applies; manifest invariance is correct architectural behavior.

## too_few_snps Count + W4 PASS Gate Disposition

Computed from 1274 fresh per-id JSONs via Python `json.load` parser (the plan's `grep '"status":"too_few_snps"'` fails because the JSONs are pretty-printed with `"status": "..."` — note space after colon).

| Status              | Count | Fraction |
| ------------------- | ----- | -------- |
| **too_few_snps**    | 1005  | 78.9%    |
| no_qtl_cs           | 235   | 18.4%    |
| success             | 32    | 2.5%     |
| qtl_susie_failed    | 2     | 0.2%     |
| **TOTAL**           | 1274  | 100.0%   |

**W4 PASS gate evaluation** (per `ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md`):

| Criterion                            | Threshold        | Observed | Result      |
| ------------------------------------ | ---------------- | -------- | ----------- |
| PASS                                 | <= 200           | 1005     | NOT MET     |
| PARTIAL_PASSED (CARTER_DECIDES)      | (200, 800)       | 1005     | NOT MET     |
| **FAIL**                             | **>= 800**       | **1005** | **MET**     |

**Outcome: FAILED. W5 gate: BLOCKED.**

This is W4.5 SuSiE-RSS-layer fallback territory per the W4 plan PASS/FAIL/WARN gate taxonomy. Per the plan's quick-task scope: *"FAIL: 1274 JSONs + aggregator refresh but too_few_snps >= 800 (W4.5 SuSiE-RSS fallback territory; outside this quick task's scope — record in tracker v7 and stop)."* Remediation deferred to Carter's W5 disposition decision.

## Tracker v7 Status

`wave4_dispatch_tracker_v7.json`: **status = "FAILED"** (`v7_W4_5_A_CONTINUATION_FAILED`). Validated via `python -c "import json; d = json.load(...); assert d['status'] in ('PASSED','PARTIAL_PASSED','FAILED')"` — PASS. All 4 invariant md5s in `preserved_invariants` block match v6 pinned values exactly.

## 4 Invariant md5s Post-Wave (3 SH2B3 anchors + TRACK-A-FROZEN)

| File                                                          | md5                                | v6 pin                             | Match  |
| ------------------------------------------------------------- | ---------------------------------- | ---------------------------------- | ------ |
| `results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds`      | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | YES    |
| `results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds` | `8255c1acf50add5f68dfb551af977b53` | `8255c1acf50add5f68dfb551af977b53` | YES    |
| `results/fine_mapping/susie/stroke.EUR.SH2B3_12q24.fit.rds`   | `a041eecc27f3086190069783eeb45ffe` | `a041eecc27f3086190069783eeb45ffe` | YES    |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`              | `9d0405a4db95655b1be7401883d22165` | `9d0405a4db95655b1be7401883d22165` | YES    |

All 4 invariants intact post-wave. Susie .fit.rds count = 96 (unchanged; V4 niter=1000 layer fully preserved per the plan's `--forcerun` exclusion).

## Cross-References

- **Predecessor tracker (v6):** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v6.json` — v7 explicitly fulfills v6's `next_actions_when_run_qtl_coloc_completes` checklist (write tracker v7 with PASS/FAIL/PARTIAL determination + 3rd-pass aggregator refresh).
- **W4 PLAN PASS gate definition:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md` — too_few_snps PASS=≤200 / FAIL=≥800 / PARTIAL=(200,800).
- **W4.5-a launcher (predecessor):** `bin/fire_w4_5_qtl_coloc_only.sh` (commit b368e0e) — supervisor PID 2670648 dispatched 2026-04-30T16:53:15 EDT, exited at 99.6% (1270/1275 steps).
- **Drain launcher (this task):** `bin/fire_w4_5_drain_final5.sh` — minimally differs: NO `--forcerun run_qtl_coloc` (vs predecessor's `--forcerun`); mtime cascade dispatches only the missing 4.

## Other-Terminal PID 830751 Preservation

PID 830751 (results_identity_ld pipeline, other-terminal) **preserved throughout**:
- `bkill 0` was **NEVER** used (forbidden per CLAUDE.md memory `feedback_lsf_queues.md` + plan threat T-260501-r1q-03).
- Lock-file edits surgical: every pre-clear inspected for `results_identity_ld` lines (count = 0 each time, so full removal was safe per tracker v6's confirmed pattern). Timestamped backups preserved at `.snakemake/locks/0.{input,output}.lock.bak.20260501_194011` and `.bak.20260501_200550`.
- LSF bkill in v2-scope-creep recovery: explicit jobid list (82073, 82074, ..., 82081 — 9 jobs all confirmed ours by JOBID range; PID 830751 LSF jobs untouched).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's anchor md5 globs and TRACK-A-FROZEN path were stale**
- **Found during:** Task 1 step 1 (pre-flight invariant check)
- **Issue:** Plan globs `*sh2b3*bmi*` / `*sh2b3*hypertension*` / `*sh2b3*stroke*` did not match actual file naming (`bmi.EUR.SH2B3_12q24.fit.rds` etc.). Lowercase `sh2b3` glob caused alphabetical-first match issues — the stroke pattern would have matched `stroke.AFR.SH2B3_12q24.fit.rds` first (md5 `5fbbcb325a10ae5a5a61012d2a59a6c4` — does NOT match v6 pin), but tracker v6's `a041eecc...` is actually the **EUR** stroke. Plan path `data/processed/region_analysis/SH2B3_12q24/TRACK-A-FROZEN-NUMBERS.md` does not exist; actual file is at `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`.
- **Fix:** Used correct paths throughout: `bmi.EUR.SH2B3_12q24.fit.rds`, `hypertension.EUR.SH2B3_12q24.fit.rds`, `stroke.EUR.SH2B3_12q24.fit.rds`, `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`. All 4 invariant md5s verified pre-drain and post-drain match v6 pinned values exactly.
- **Files modified:** None (corrected path usage in shell logic only).
- **Recorded in:** tracker v7 `preserved_invariants.anchor_path_corrections_from_plan_globs`.

**2. [Rule 3 - Blocking issue] Plan's 'no --forcerun anywhere; mtime cascade naturally rebuilds aggregators' assumption was architecturally incorrect**
- **Found during:** Task 2 step 2 (initial 3rd-pass v1)
- **Issue:** Per `src/snakemake/rules/qtl_coloc.smk` lines 336-348 (intentional design comment in `aggregate_qtl_coloc` rule docstring), per-id JSONs are **NOT** declared as inputs of `aggregate_qtl_coloc`. Only the manifest is declared as input. This is a deliberate Phase-5 compatibility decision (so `all_pathway` can fire without backward-chaining through 1243 qtl_coloc jobs). Therefore the JSON mtime cascade does NOT propagate to aggregator outputs — `qtl_coloc_summary.tsv` mtime > `qtl_coloc_manifest.tsv` mtime, so snakemake's planner saw it as up-to-date. Initial v1 invocation `snakemake all_qtl_coloc` returned "Nothing to be done."
- **Fix:** Targeted aggregator-pass v3: explicit aggregator output paths as snakemake targets (`snakemake results/qtl_coloc/qtl_coloc_summary.tsv tier_assignments.tsv pph4_threshold_sweep.tsv gene_tissue_matrix.tsv gene_tissue_long.tsv`). `qtl_coloc_summary.tsv` was missing (bkilled mid-write from failed v2 attempt — see deviation 3), so snakemake correctly rebuilt it, then natural mtime cascade triggered `assign_tiers` + `build_gene_tissue_matrix`. 3/3 steps clean in ~3 min.
- **Files modified:** None (invocation choice only).
- **Recorded in:** tracker v7 `outcome_summary.aggregator_3rd_pass.deviation_from_plan`.

**3. [Rule 1 - Bug] v2 attempt scope creep due to snakemake CLI `--forcerun` semantics**
- **Found during:** Task 2 step 2 (3rd-pass v2 mid-flight)
- **Issue:** v2 invocation `snakemake --forcerun aggregate_qtl_coloc all_qtl_coloc` was misparsed: `--forcerun` consumed BOTH `aggregate_qtl_coloc` and `all_qtl_coloc` as rule names (greedy list semantics), with no positional target left → snakemake defaulted to `rule all` and planned 19 jobs including unrelated targets (`summarize_harmonized_sumstats`, `build_pgs_manifest`, `build_mr_manifest`, `effect_scale_qc`, etc.). 9 LSF jobs (82073-82081) submitted before recovery.
- **Fix:** SIGINT then SIGKILL on supervisor PID 416173 (local snakemake driver). Explicit bkill of 9 LSF jobs by jobid (82073-82081, all confirmed ours from this v2 dispatch by JOBID range — **NEVER `bkill 0`**; PID 830751 LSF jobs untouched). Locks re-cleared (0 identity_ld entries; safe full removal). v3 (targeted) launched and completed cleanly. Note: bkilled `aggregate_qtl_coloc` job (82076) had started writing `qtl_coloc_summary.tsv` and was interrupted mid-write; snakemake removed the partial file as incomplete — which actually helped v3 (snakemake saw it as missing and rebuilt cleanly without `--forcerun`).
- **Files modified:** None (recovery via process/job control only).
- **Recorded in:** tracker v7 `deviations_applied[2]`.

### Auth Gates

None. No external authentication required for this purely local snakemake + LSF orchestration task.

## Self-Check: PASSED

**Created files exist:**
- FOUND: `bin/fire_w4_5_drain_final5.sh` (45 lines, executable)
- FOUND: `logs/wave4_5_drain_final5_20260501_194043.log` (gitignored)
- FOUND: `logs/wave4_5_aggregator_3rd_pass_20260501_200603.log` (gitignored)
- FOUND: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v7.json` (validated JSON, status=FAILED)
- FOUND: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_v4_monitor.tsv` (4 rows: header + 2 prior + W4.5-A-continuation row)

**Commits exist:**
- FOUND: `f165e57` (drain final 4 run_qtl_coloc)
- FOUND: `bf2a18a` (aggregator 3rd-pass + tracker v7)

**Outputs from `<output>` block of plan:**
- 4 missing qtl_coloc_ids: documented verbatim above
- JSON count progression: 1270 → 1274 → 1274 (Pre-drain → Post-drain → Post-3rd-pass)
- Aggregator mtime diff: V4 (~Apr 30 11:52-12:45) vs 3rd-pass (May 1 20:07-20:08); 5 of 6 FRESH
- too_few_snps + W4 PASS gate: 1005 → FAILED → W5 BLOCKED
- Tracker v7 status: FAILED
- 4 invariant md5s: all match v6 pins
- W5 gate: BLOCKED
- Predecessor cross-ref: tracker v6 `next_actions_when_run_qtl_coloc_completes` fulfilled
- PID 830751 preservation: confirmed (no bkill 0; surgical lock edits; explicit-jobid recovery)
