---
phase: quick-260429-w2a
plan: 01
subsystem: m2/mtag
tags: [m2, mtag, fdr, harvest, lsf, m2-post-m3-07, wave-2-d6, production-fire]
requires:
  - bin/fire_m2_post_m3_07_mtag_fdr.sh (driver, hard-locked, quick-260429-utt)
  - data/processed/mtag/{EUR,AFR,TRANS}/residcov.txt (Wave 2 fire output)
  - data/processed/mtag/{EUR,AFR,TRANS}/residcov.trait_order.json (sidecar)
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_omega_hat.txt
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_sigma_hat.txt
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_maxfdr_filtered.txt (placeholder 0.0)
  - /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10 + numpy 1.26.4 + joblib 1.4.2)
provides:
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_maxfdr_filtered.txt (col 11 rewritten with K finite floats)
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_fdr_audit.tsv (per-trait max_FDR + n_rows)
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_fdr_run.log (LSF run logs)
  - data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_fdr.bjob.done (sentinels)
  - data/processed/mtag/m2_post_m3_07_bjobs.tsv (LSF manifest)
  - src/python/harvest_mtag_fdr_scalars.py (harvest module)
  - tests/m2/test_harvest_mtag_fdr_scalars.py (5-case pytest contract)
affects:
  - .planning/m2_post_m3_rerun_queue.tsv (M2-POST-M3-07 row: not_started → completed)
tech-stack:
  added: []
  patterns:
    - "atomic-rewrite-via-tmp-os.replace (mid-stream-exception-safe)"
    - "TDD RED-then-GREEN with stdlib-only harvest (no pandas dep)"
    - "explicit-path git staging on shared GPFS tree"
    - "--allow-empty marker commits for gitignored data artifacts (per tq9 §3 pattern)"
key-files:
  created:
    - src/python/harvest_mtag_fdr_scalars.py
    - tests/m2/test_harvest_mtag_fdr_scalars.py
  modified:
    - .planning/m2_post_m3_rerun_queue.tsv
decisions:
  - "Production-fire defaults locked at CORES=4 / MEM_GB=8 / INTERVALS=2 (smoke-witness-derived; no over-allocation)"
  - "Stdlib-only harvest (json + os + re + pathlib) for env-footprint minimalism + Python 3.11 smoke_dev consistency with pytest runner"
  - "Atomic-rewrite via *.tmp + os.replace() with try/except cleanup of *.tmp shard on mid-stream exception — original maxfdr_filtered.txt preserved on any KeyError/IOError"
  - "Fail-loud on unmapped trait_key (KeyError) and on K mismatch between log and sidecar (ValueError) — no silent skip-rows or pad-zeros"
metrics:
  duration_minutes: ~10 (LSF dispatch + 3-stratum production walls in parallel + harvest + queue flip)
  completed_date: 2026-04-29
  total_commits: 5
  total_tasks: 5
  total_lsf_jobs: 3
  total_rows_rewritten: 22894472
---

# Quick Plan 260429-w2a: Fire M2-POST-M3-07 MTAG --fdr Production + Harvest Summary

**Production-fire closure of Wave 2-D6 hand-off** (`m2-02-task4-mtag-production-fire.md` §6) — 3 LSF parallel jobs replaced the placeholder `max_FDR=0.0` column in EUR/AFR/TRANS `_mtag_maxfdr_filtered.txt` with the actual per-trait Turley scalars from `--skip_mtag --fdr --intervals 2 --fit_ss`. All 22,894,472 rows across the three strata now carry their correct trait-specific maxFDR.

## Per-stratum LSF job + wall + RSS

| Stratum | Job ID | Submit (UTC-4)         | Wall    | Peak RSS (GB) | Grid pts (--fit_ss) | LSF status |
| ------- | ------ | ---------------------- | ------- | ------------- | -------------------- | ---------- |
| EUR T=8 | 69641  | 2026-04-29T23:15:09    | 3:12.35 | 1.56          | 2                    | DONE       |
| AFR T=6 | 69642  | 2026-04-29T23:15:10    | 1:19.53 | 1.33          | 2                    | DONE       |
| TRANS T=7 | 69643 | 2026-04-29T23:15:10   | 1:29.23 | 1.57          | 1                    | DONE       |

All three completed within ~3 min wall (well under the 30-min Task 3 cap). 0 LSF EXITs.

**Spike-Slab grid pruning verdict:** 1–2 grid points after `--fit_ss` for all three strata — **order-of-magnitude consistent with the AFR T=6 smoke witness** (2 grid points). T=8 EUR did NOT expand materially (still 2 points), and T=7 TRANS pruned to 1 point — empirically validating the smoke-projected sub-2-min-per-stratum envelope and refuting the Wave 2-D6 "~24 hr per stratum" worst-case anchor for the unconstrained simplex. AFR walls reproduced the 52 s smoke witness to within ~50 % (1:19 vs 0:52, scaled by post-ABI-lock production environment overhead).

## Per-stratum max_FDR scalar summary (from audit TSVs)

### EUR (K=8, 8,012,176 rows; 1,001,522 per trait)

| trait_key                       | max_FDR        |
| ------------------------------- | -------------- |
| bmi.EUR.GIANT-UKBB.2018         | 1.091e-06      |
| egfr.EUR.CKDGen.2019            | 4.460e-05      |
| hdl.EUR.GLGC.2021               | 1.217e-06      |
| ldl.EUR.GLGC.2021               | 2.541e-06      |
| sbp.EUR.Evangelou-ICBP-UKBB.2018 | 2.525e-06     |
| stroke.EUR.GIGASTROKE.2022      | 1.338e-04      |
| tc.EUR.GLGC.2021                | 1.046e-06      |
| tg.EUR.GLGC.2021                | 1.701e-06      |

**Range:** min=1.046e-06 (tc) / max=1.338e-04 (stroke). **n_below_0.05=8/8 / n_below_0.01=8/8.**

### AFR (K=6, 6,801,006 rows; 1,133,501 per trait)

| trait_key                  | max_FDR        |
| -------------------------- | -------------- |
| bmi.AFR.PAGE.2019          | 9.706e-03      |
| hdl.AFR.GLGC.2021          | 3.316e-03      |
| ldl.AFR.GLGC.2021          | 4.083e-06      |
| stroke.AFR.GIGASTROKE.2022 | 1.154e-01      |
| tc.AFR.GLGC.2021           | 8.643e-09      |
| tg.AFR.GLGC.2021           | 1.765e-03      |

**Range:** min=8.643e-09 (tc) / max=1.154e-01 (stroke). **n_below_0.05=5/6 / n_below_0.01=4/6.** Production scalars match the AFR smoke witness exactly (verifies env reproducibility from quick-260429-utt → quick-260429-w2a).

**Stroke.AFR observation (rigor flag):** max_FDR = 0.1154 — the only above-0.05 scalar across the 21-trait union. Carter-locked downstream consumers (HyPrColoc inputs / MTAG-novel SNP inheritance) should treat AFR stroke MTAG hits with the appropriate max-FDR-aware confidence threshold; an 11.5 % maxFDR is well above the conventional 5 % discovery threshold and reflects the lower power of the GIGASTROKE AFR slice within the simplex grid.

### TRANS (K=7, 8,081,290 rows; 1,154,470 per trait)

| trait_key                  | max_FDR        |
| -------------------------- | -------------- |
| cad.TRANS.Aragam.2022      | 1.319e-05      |
| egfr.TRANS.CKDGen.2019     | 3.067e-05      |
| hdl.TRANS.GLGC.2021        | 1.034e-06      |
| ldl.TRANS.GLGC.2021        | 2.157e-06      |
| stroke.TRANS.GIGASTROKE.2022 | 1.431e-04    |
| tc.TRANS.GLGC.2021         | 7.459e-07      |
| tg.TRANS.GLGC.2021         | 1.480e-06      |

**Range:** min=7.459e-07 (tc) / max=1.431e-04 (stroke). **n_below_0.05=7/7 / n_below_0.01=7/7.**

## Wave 2-D6 hand-off CLOSED witness

The deferred annotation in `m2-02-task4-mtag-production-fire.md` §6 — *"the result will replace the placeholder 0.0 with the actual per-trait Turley scalars in a subsequent commit"* — is now closed by the two-quick-task chain:

- **quick-260429-utt** (env build + AFR T=6 smoke gate, 52 s wall, 2-grid-point pruning witness)
- **quick-260429-w2a** (this task: 3-stratum LSF burst + harvest + queue close)

Per-stratum row-by-row verification (RUNBOOK §5 step 4):

```
EUR: rows=8012176 distinct max_FDR=8 (expected K=8) placeholder_0.0_rows=0
AFR: rows=6801006 distinct max_FDR=6 (expected K=6) placeholder_0.0_rows=0
TRANS: rows=8081290 distinct max_FDR=7 (expected K=7) placeholder_0.0_rows=0
```

Cardinality match (`N_DISTINCT == K`) proves the rewrite engaged across all three strata; placeholder filter (0 rows match `^0\.?0*$`) proves the placeholder was actually replaced (not coincidentally re-emitted as one of the K scalars).

## Queue-row diff (M2-POST-M3-07)

```
status:      not_started → completed
submit_ts:   - → 2026-04-29T23:15:09-04:00
lsf_job_ids: - → 69641,69642,69643
current_artifact: appended HARVEST witness with per-stratum K, min/max
                  max_FDR scalars, n_below_0.05 + n_below_0.01 thresholds,
                  ~6.8M-8.0M row in-place rewrite scope, audit-TSV pointers,
                  and Spike-Slab grid pruning depths
```

Verified: only the M2-POST-M3-07 row changed (`git diff --stat`: 1 insertion / 1 deletion); 7 other obligation rows preserved byte-identical to pre-task tree.

## Tasks executed (5/5)

| Task | Type           | Commit  | Deliverable                                                              |
| ---- | -------------- | ------- | ------------------------------------------------------------------------ |
| 1    | auto (read-only) | n/a    | PRE_FIRE_OK — 4 RUNBOOK §1 checks PASS (env, Wave 2 outputs, LSF, driver) |
| 2    | auto           | e9077af | LSF burst submitted (3 jobs marker; manifest gitignored per project policy) |
| 3    | auto           | n/a     | 3/3 sentinels at ~3 min wall; 3/3 DONE; 0 EXIT; HARVEST_GATE_OPEN          |
| 4    | auto (TDD)     | 928f426 + 8a6e230 + 436a645 | RED test (5 cases) + GREEN script + harvest data marker (22,894,472 rows rewritten) |
| 5    | auto           | 7746450 | Queue row M2-POST-M3-07 flip (not_started → completed)                    |

## Pytest contract

```
tests/m2/test_harvest_mtag_fdr_scalars.py::test_parse_fdr_log_smoke_witness_exact_float_match PASSED
tests/m2/test_harvest_mtag_fdr_scalars.py::test_parse_fdr_log_no_fdr_lines_raises PASSED
tests/m2/test_harvest_mtag_fdr_scalars.py::test_parse_fdr_log_handles_scientific_notation PASSED
tests/m2/test_harvest_mtag_fdr_scalars.py::test_rewrite_maxfdr_column_join_contract PASSED
tests/m2/test_harvest_mtag_fdr_scalars.py::test_rewrite_maxfdr_column_unmapped_trait_key_raises PASSED
============================== 5 passed in 0.11s ===============================
```

5 cases pass under `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python` (Python 3.11 + pytest 9.0.3). The plan's spec called for 2 cases; I added one additional scientific-notation regression test (rigor over speed; ensures `8.642644223250632e-09` is parsed correctly, not silently rejected by a permissive-but-wrong regex).

## Deviations from Plan

**None — plan executed exactly as written.** All 5 tasks completed in order; 5 commits posted with the exact spec-message templates; no architectural-change escalations; no auto-fix engagements. The one in-spec rigor enhancement was an extra pytest case for scientific notation (counted as 5 tests, plan called for "at least 2" — the plan's wording explicitly permitted additional cases).

## Authentication gates

**None** — LSF login was alive at Task 1 (verified via `bjobs -u $USER`); production fire ran under existing Carter user account; no DUA / 2FA / OAuth interactions required.

## Hard-locked-file integrity

`git log --since="2026-04-29" --` against the protected-file list confirms zero modifications to:
- `bin/fire_m2_post_m3_07_mtag_fdr.sh` (driver)
- `bin/fire_m2_02_mtag_3strata.sh` (Wave 2 canonical fire)
- `tools/mtag/` (vendored MTAG repo)
- `envs/m2-mtag.yml` (env spec)
- `src/snakemake/rules/m2_mtag.smk` (Snakemake rule)
- per-stratum `_mtag_trait_*.txt` and omega/sigma matrices

Cumulative diff (`git diff --name-status e9077af^..7746450`):

```
M  .planning/m2_post_m3_rerun_queue.tsv
A  src/python/harvest_mtag_fdr_scalars.py
A  tests/m2/test_harvest_mtag_fdr_scalars.py
```

Three files in the source tree; data artifacts are gitignored markers (commits `e9077af` and `436a645`).

## Downstream consumer pointer (out of scope, newly unblocked)

Consumers of `_mtag_maxfdr_filtered.txt` — joint-signal HyPrColoc inputs, Phase 2 MTAG-novel SNP inheritance, CPASSOC overlap table — were previously blocked on the `max_FDR=0.0` placeholder. With the K-cardinal scalars now committed, downstream refresh is unblocked. List of downstream consumers is the responsibility of the next quick task or phase plan that elects to re-fire them (RUNBOOK §6 follow-up bullet); enumeration is **out of scope for w2a** but explicitly newly-unblocked.

## Self-Check: PASSED

- [x] `tests/m2/test_harvest_mtag_fdr_scalars.py` exists (FOUND)
- [x] `src/python/harvest_mtag_fdr_scalars.py` exists (FOUND)
- [x] `.planning/m2_post_m3_rerun_queue.tsv` modified, M2-POST-M3-07 row reads `completed` (FOUND)
- [x] Commit `e9077af` exists (FOUND)
- [x] Commit `928f426` exists (FOUND)
- [x] Commit `8a6e230` exists (FOUND)
- [x] Commit `436a645` exists (FOUND)
- [x] Commit `7746450` exists (FOUND)
- [x] All 3 `_mtag_maxfdr_filtered.txt` files have col 11 cardinality K (8/6/7) and 0 placeholder rows (VERIFIED)
- [x] All 3 `_mtag_fdr_audit.tsv` files have K data rows each (VERIFIED)
- [x] All 3 `_mtag_fdr.bjob.done` sentinels present (VERIFIED)
- [x] Hard-locked files diff = 0 (VERIFIED)
