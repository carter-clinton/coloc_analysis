---
phase: quick-260429-utt
plan: 01
subsystem: m2-mtag-fdr-prep
tags: [m2-post-m3-07, mtag, fdr, conda-env, smoke-gate, lsf-prep, wave-2-d6, pitfall-6]
requires:
  - envs/m2-mtag.yml (committed; UNTOUCHED)
  - tools/mtag/mtag.py (vendored; UNTOUCHED)
  - bin/fire_m2_02_mtag_3strata.sh (canonical Wave 2 fire; UNTOUCHED)
  - data/processed/mtag/AFR/AFR_mtag_*.txt (Wave 2 outputs; UNTOUCHED)
  - data/processed/mtag/AFR/residcov.txt + residcov.trait_order.json
provides:
  - /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (filesystem env; OFF-REPO)
  - bin/fire_m2_post_m3_07_mtag_fdr.sh (LSF burst-fire driver)
  - .planning/quick/260429-utt-.../SMOKE-AFR-FDR.log + TIMING.md
  - .planning/quick/260429-utt-.../M2-POST-M3-07-RUNBOOK.md
  - .planning/m2_post_m3_rerun_queue.tsv (M2-POST-M3-07 dependency_blockers annotated)
affects:
  - M2-POST-M3-07 obligation: env-build dependency_blocker CLOSED;
    LSF long-queue allocation dependency_blocker REMAINS OPEN
tech-stack:
  added:
    - conda env at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10.20)
    - joblib 1.4.2 (pip-installed Rule 3 auto-fix; NOT in envs/m2-mtag.yml lock)
  patterns:
    - Wave 2/3 bypass pattern (bin/fire_m2_02_mtag_3strata.sh canonical preserved)
    - Per-stratum LSF jobscript rendering with .bjob.done sentinel
    - --skip_mtag --fdr --fit_ss --intervals 2 simplex-pruning idiom
key-files:
  created:
    - bin/fire_m2_post_m3_07_mtag_fdr.sh
    - .planning/quick/260429-utt-.../SMOKE-AFR-FDR.log
    - .planning/quick/260429-utt-.../SMOKE-AFR-FDR.time.txt
    - .planning/quick/260429-utt-.../TIMING.md
    - .planning/quick/260429-utt-.../M2-POST-M3-07-RUNBOOK.md
  modified:
    - .planning/m2_post_m3_rerun_queue.tsv (M2-POST-M3-07 row dependency_blockers cell only)
decisions:
  - Used `mamba env create -p` (prefix path) NOT `-n` (name) for env materialization
    in Carter's standard /rs1/.../conda_envs/ directory
  - Pip-installed joblib 1.4.2 into m2-mtag env as Rule 3 auto-fix (matches Wave 2
    magma_helpers bypass pattern); did NOT modify envs/m2-mtag.yml hard-lock
  - Reproducibility check used full md5 (strictest) instead of 1e-9 tolerance
    fallback; md5-identical despite pandas 2.2.2 vs 2.2.1 patch-bump
  - Smoke target was AFR T=6 (smallest stratum) per plan rationale; production
    fire envelope extrapolated from this floor witness
metrics:
  duration_min: 6
  task_count: 5
  commit_count: 3
  smoke_wall_sec: 52.04
  smoke_peak_rss_gb: 1.36
  reproducibility_md5_match: true
completed: 2026-04-29
---

# quick-260429-utt: Prep M2-POST-M3-07 MTAG --fdr env + smoke

One-liner: Built m2-mtag conda env (Python 3.10 + numpy 1.26.4 ABI lock per
Pitfall 6) at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag, smoke-validated
MTAG --skip_mtag --fdr --intervals 2 --fit_ss --cores 4 on AFR T=6 in 52.04 s
(vs 1800 s cap), and pre-wrote the LSF burst-fire driver
bin/fire_m2_post_m3_07_mtag_fdr.sh closing the env-build half of the
M2-POST-M3-07 dependency_blocker pair.

## Objective achieved

Prepared the MTAG `--fdr` LSF re-fire (obligation M2-POST-M3-07) by closing
one of its two locked `dependency_blockers` — the **m2-mtag conda env build**
— and rigor-validated the post-MTAG `--fdr` workflow on the smallest-T
stratum BEFORE the production fire is committed to the LSF long-queue in a
follow-up quick task.

Closed blocker: "m2-mtag conda env build (currently bypassed via magma_helpers)".
Remaining open blocker: "LSF long-queue allocation".

## Tasks executed

| # | Task                                                                | Outcome                                                | Commit  |
|---|--------------------------------------------------------------------|--------------------------------------------------------|---------|
| 1 | Build m2-mtag conda env at /rs1/.../m2-mtag                        | Built; ABI lock holds (numpy 1.26.4); joblib auto-fix  | (no commit — /rs1 filesystem-only) |
| 2 | Pre-flight reproducibility check vs magma_helpers bypass            | **md5-IDENTICAL** AFR_mtag_trait_1.txt (1,133,502 rows) | (no commit — /tmp staging only) |
| 3 | Production smoke gate — MTAG --fdr on AFR (T=6)                    | **PASS** wall 52.04 s, peak RSS 1.36 GB, all 6 max_FDR finite | `d4c94aa` |
| 4 | Write bin/fire_m2_post_m3_07_mtag_fdr.sh (do NOT execute)           | Driver written (154 lines, 26 contract tokens, exec)   | `36033dc` |
| 5 | Write M2-POST-M3-07-RUNBOOK.md + annotate queue blockers            | 6 numbered sections; queue row annotated (status not_started preserved) | `37e932b` |

3 commits landed. Tasks 1 + 2 produced no commits per plan (env build is
/rs1 filesystem-only; reproducibility check is /tmp staging only).

## Smoke witness (load-bearing for production fire)

**Branch: PASS** — every gate metric clean.

| Metric                            | Observed                | Target / Cap          |
|-----------------------------------|-------------------------|-----------------------|
| Wall                              | **52.04 s**             | < 1800 s (30-min cap) |
| Peak RSS                          | **1,389,996 KB ≈ 1.36 GB** | < 8 GB (LSF mem pin) |
| CPU                               | 260% (4 cores effective) | --cores 4 saturating |
| Exit status                       | 0                       | 0                     |
| Per-trait max_FDR scalars (T=6)   | 6 finite floats         | none = 0.0; none NaN  |
| Spike-Slab simplex prune          | 2 grid points (post-fit) | tractable (vs 2^63 unconstrained) |

**Per-trait max_FDR scalars** (in residcov.trait_order: bmi/hdl/ldl/stroke/tc/tg):

```
Trait 1 (bmi.AFR.PAGE.2019):           0.00970590589390107
Trait 2 (hdl.AFR.GLGC.2021):           0.003316170693667885
Trait 3 (ldl.AFR.GLGC.2021):           4.08283132227812e-06
Trait 4 (stroke.AFR.GIGASTROKE.2022):  0.11541401327515466    ← grid pt idx=1; saturated Spike-Slab
Trait 5 (tc.AFR.GLGC.2021):            8.642644223250632e-09
Trait 6 (tg.AFR.GLGC.2021):            0.0017651764636435043
```

These six scalars are the witness that the production-fire output structure
is real. The harvest task (separate quick task) will extract analogous
scalars for EUR (T=8) and TRANS (T=7) from the LSF jobs and join onto the
existing `_mtag_maxfdr_filtered.txt` placeholder column (currently all 0.0).

## Reproducibility check witness

| Comparison                                | Result                                          |
|-------------------------------------------|-------------------------------------------------|
| Row count match (legacy vs new)           | 1,133,502 = 1,133,502 ✓                         |
| Header diff                               | byte-identical ✓                                |
| **md5 of AFR_mtag_trait_1.txt**           | `612f856221e6be29a3a3a0c3397b970b` (match) ✓    |
| pandas patch-version drift impact         | **zero** (2.2.1 → 2.2.2 produced identical output) |

Reproducibility achieved at the strictest possible level (md5-identical),
not just 1e-9 tolerance.

## Production-fire envelope (extrapolated from smoke)

| Stratum  | Trait count (K)  | Predicted wall    | LSF resource pins (defaults) |
|----------|------------------|-------------------|-------------------------------|
| AFR      | 6 (smoke target) | 52.04 s observed  | -q long, -n 4, mem=8GB        |
| TRANS    | 7                | ~60-90 s         | same defaults                 |
| EUR      | 8                | ~75-120 s        | same defaults                 |

All three sit FOUR orders of magnitude under the long-queue 14400-min cap.
The Wave 2-D6 hand-off "~24 hr per stratum at proper grid resolution" was
a worst-case anchor for the unconstrained simplex; pruned-prior reality
with `--fit_ss` is sub-2-min per stratum.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] joblib missing from m2-mtag env**
- **Found during:** Task 1 verify step 4 (`import mtag` failed with
  `ModuleNotFoundError: No module named 'joblib'`)
- **Issue:** The vendored MTAG (`tools/mtag/mtag.py` line 14) imports joblib
  for `--cores` parallelism. The Wave 2 magma_helpers bypass had joblib
  pip-installed (Wave 2 Task 4 deviation §1 ref). The new envs/m2-mtag.yml
  spec did NOT include joblib (the plan called this out as a possible Task
  2/3 finding).
- **Fix:** Pip-installed `joblib==1.4.2 --no-deps` into the m2-mtag env.
  Did NOT modify `envs/m2-mtag.yml` (hard-locked per plan; modification
  is owned by a follow-up quick task per Task 5 §6 out-of-scope). Matches
  the Wave 2 magma_helpers bypass pattern (legacy joblib 1.5.3 there;
  same modern stable ABI as 1.4.2).
- **Files modified:** None tracked in git (env is at /rs1/.../m2-mtag —
  off-repo filesystem); `envs/m2-mtag.yml` deliberately NOT changed.
- **Commit:** N/A (Task 1 produces no commit per plan).
- **Verification:** Post-fix `import mtag` succeeded; `mtag.py --help`
  surfaced 8 hits across the 5 fdr-family flags (target ≥ 5);
  reproducibility smoke and AFR --fdr smoke both ran cleanly.

### Substituted Verification Approach

**2. [Per-prompt allowance] Reproducibility check used full md5 instead of
   1e-9 tolerance fallback**
- **Authority:** Prompt explicitly allowed "substitute a quick
  numpy.testing.assert_allclose on a single MTAG output column rather than a
  full md5 check." I went the other direction — chose md5 (strictest) to
  honor Carter's "rigor over time-saving" rule. The md5 matched on the
  first try, so no fallback was needed.
- **Outcome:** md5 of new AFR_mtag_trait_1.txt = legacy AFR_mtag_trait_1.txt
  exactly. Pandas patch-version drift (2.2.1 → 2.2.2) produced
  byte-identical output, eliminating the reproducibility risk the plan
  flagged.

## Auth gates

None encountered.

## Self-Check: PASSED

**Files exist:**
- `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/bin/fire_m2_post_m3_07_mtag_fdr.sh` — FOUND
- `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log` — FOUND
- `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.time.txt` — FOUND
- `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md` — FOUND
- `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md` — FOUND
- `/rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python` — FOUND (Python 3.10.20)

**Commits exist:**
- `d4c94aa` (Task 3 docs/smoke) — FOUND in git log
- `36033dc` (Task 4 feat/driver) — FOUND in git log
- `37e932b` (Task 5 docs/runbook) — FOUND in git log

**Canonical artifacts UNTOUCHED:**
- `bin/fire_m2_02_mtag_3strata.sh` — `git diff HEAD~3` returns 0 lines
- `tools/mtag/` — `git diff HEAD~3` returns 0 lines
- `envs/m2-mtag.yml` — `git diff HEAD~3` returns 0 lines

**Wave 2 MTAG outputs UNTOUCHED:**
- `data/processed/mtag/AFR/AFR_mtag_trait_1.txt` mtime preserved at
  `2026-04-26 18:58:24` (Wave 2 fire timestamp; smoke wrote to /tmp only).

**Queue integrity:**
- 8 obligation rows + 1 header = 9 lines in `m2_post_m3_rerun_queue.tsv` ✓
- M2-POST-M3-07 status STAYS `not_started` ✓
- Annotation contains "BUILT 2026-04-29" sentinel ✓
