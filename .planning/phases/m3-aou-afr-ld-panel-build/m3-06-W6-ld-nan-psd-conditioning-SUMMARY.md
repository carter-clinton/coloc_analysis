---
phase: m3-aou-afr-ld-panel-build
plan: 06
subsystem: ld
tags: [ld, psd, conditioning, nan, aou, afr, osf-prereg, track-a, eigclip, ridge]

# Dependency graph
requires:
  - phase: m3-02e-W2-native-ld-export-and-public-eur
    provides: "raw native-plink {region}.npz contract + plink_ld_to_npz.read_square_bin raise-on-NaN + content_verify_npz + ld_npz_to_rds.R ingest key set"
  - phase: ta-r3 (osf-amendment-r3-2026-05-04.md)
    provides: "psd_regularize_ridge (Wen 2017) + psd_regularize_eigclip (Hutchinson 2020) inline in refit_sh2b3_psd_regularized.R"
provides:
  - "Canonical src/R/regularization/psd_utils.R (single home of the two r3 PSD methods), consumed by the EUR r3 refit AND (deferred §5) the AFR native panel"
  - "condition_ld_matrix — memory-bounded, pre-registered off-diagonal NaN->0 conditioning (topology branch + 0.0005*n_var ceiling + egress-safe provenance)"
  - "write_conditioned_npz — banks the conditioned matrix as a separate {region}.conditioned.npz with base + provenance keys (fit-time PSD placeholders)"
  - "Three TDD test suites (byte-identity R gate + two Python suites), all NCSU-local, zero perimeter access"
affects: [m3-fit-time-wiring-§5, m3-in-perimeter-region1-verify-§6, track-a-r3-submission, afr-native-ld-fine-mapping]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Byte-identity refactor gate: capture golden from PRE-refactor inline source, then identical() vs golden + verbatim in-test cross-check"
    - "Block-wise (block x n_var) NaN topology scan + in-place coordinate zeroing (m3-02e-T4 dense-verify OOM discipline reused)"
    - "Separate {region}.conditioned.npz artifact + out-path guard so the FROZEN raw contract is un-clobberable"

key-files:
  created:
    - src/R/regularization/psd_utils.R
    - tests/testthat-phase1/test_psd_utils_byte_identical.R
    - tests/testthat-phase1/fixtures/psd_golden_r3.rds
    - src/python/condition_ld_matrix.py
    - tests/m3/test_condition_ld_matrix.py
    - src/python/write_conditioned_ld_npz.py
    - tests/m3/test_write_conditioned_ld_npz.py
  modified:
    - src/R/regularization/refit_sh2b3_psd_regularized.R

key-decisions:
  - "psd_utils.R is the single canonical PSD definition; refit_sh2b3 sources it (path-robust, snp_id_bridge.R dual-path pattern) — no duplicated body, byte-identity gated"
  - "n_zeroed_pairs > ceiling_frac*n_var compared as a FLOAT ceiling_n (matches amendment 51.21 @ n_var=102421 and the plan's n=4000 -> ceiling_n=2.0 boundary)"
  - "Off-diagonal NaN pairs collected as unordered (min,max) from EITHER triangle + de-duplicated (robust to a lone lower-triangle NaN), zeroed at both (i,j) and (j,i)"
  - "psd_method/psd_lambda are PENDING_FIT_TIME/NaN placeholders in the conditioned .npz — PSD runs on the fine-mapping submatrix at fit time (§5), not the full n_var~1e5 panel"

patterns-established:
  - "Golden-capture-first for Track-A-sensitive refactors (fixtures dir created before saveRDS)"
  - "Frozen-contract SHA snapshot + git-diff assertion (plink_ld_to_npz.py, run_native_ld_panel.py, ld_npz_to_rds.R) around additive downstream stages"

requirements-completed: [REQ-AOU-LD-VALIDATION, REQ-AOU-LD-EGRESS, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI]

# Metrics
duration: ~15min (code); +8min full-suite regression
completed: 2026-07-07
---

# Phase m3 Plan 06 (W6): LD NaN->0 + PSD Conditioning Machinery Summary

**NC-State conditioning machinery for the AoU AFR native-plink LD panel: a byte-identity-gated shared `psd_utils.R`, a memory-bounded `condition_ld_matrix` (pre-registered off-diagonal NaN->0 with topology branch + 0.0005*n_var ceiling + egress-safe provenance), and a `write_conditioned_npz` that banks a separate provenance-stamped `{region}.conditioned.npz` — all NCSU-local, zero perimeter access, r3 numerics unchanged.**

## Performance

- **Duration:** ~15 min (code) + ~8 min full `tests/m3` regression
- **Started:** 2026-07-07T15:03Z (golden capture)
- **Completed:** 2026-07-07T19:27Z
- **Tasks:** 3 (all TDD RED->GREEN)
- **Files modified:** 8 (7 created, 1 modified)

## Accomplishments
- **Task 1 (999.1 §2):** Factored the two r3 PSD functions (`psd_regularize_ridge` Wen 2017; `psd_regularize_eigclip` Hutchinson 2020, `lambda_floor=1e-6`) into canonical `src/R/regularization/psd_utils.R`; `refit_sh2b3_psd_regularized.R` now path-robustly sources it (0 inline PSD defs, 1 `source(psd_utils)` line). Byte-identity gate: **all 16 `identical()` checks TRUE** (ridge {0.001,0.01,0.1} x {well-conditioned, negative-eigenvalue} + eigclip x both) vs a frozen golden AND a verbatim in-test reference — r3 / Track-A numerics provably unchanged.
- **Task 2 (999.1 §3):** `condition_ld_matrix` implements amendment (a) topology branch / (b) ceiling / (d) provenance. Fully-NaN row RAISES (directs upstream MAF/missingness drop, priority over ceiling); isolated off-diagonal NaN pairs -> 0.0 at both triangles with the 1.0 diagonal untouched; over-ceiling RAISES `BRANCH_AFR_COND_DEFERRED` with NO mutation; clean no-op passthrough. Block-wise topology helpers + in-place zeroing (no full n_var**2 temporary); block-size-invariant. **Region-1 topology fixture confirms `n_zeroed_pairs == 6`** (6 symmetric pairs / 11 index-adjacent rows / 0 fully-NaN rows). 14/14 pass.
- **Task 3 (999.1 §4):** `write_conditioned_npz` banks a SEPARATE `{region}.conditioned.npz` carrying base keys (`ld, variant_ids, rsids, allele_freq, lower_triangular`) + provenance (`n_zeroed, zeroed_pairs, nan_policy, psd_method, psd_lambda, ceiling_frac`); out-path guard refuses any non-`.conditioned.npz` (and the raw `{region}.npz`) so the frozen raw contract is un-clobberable. 10/10 pass.
- **Full regression:** `pytest tests/m3` = **360 passed / 30 skipped** (baseline 336/30 + 24 new; no regressions, skip count unchanged).

## Task Commits

Each task committed atomically (TDD RED then GREEN), explicit GPFS paths only, tag convention `m3-06-W6-TN`:

1. **Task 1 (§2) RED** — `0150459` (test: failing byte-identity gate + frozen golden)
2. **Task 1 (§2) GREEN** — `47707ad` (refactor: extract psd_utils.R; refit_sh2b3 sources it)
3. **Task 2 (§3) RED** — `d73ac70` (test: failing-first condition_ld_matrix cases)
4. **Task 2 (§3) GREEN** — `ccca5b8` (feat: memory-bounded NaN->0 conditioning)
5. **Task 3 (§4) RED** — `aa753ba` (test: failing-first write_conditioned_npz cases)
6. **Task 3 (§4) GREEN** — `f147041` (feat: bank conditioned matrix as separate .npz)

**Plan metadata:** handled by the orchestrator docs commit (SUMMARY/STATE/ROADMAP not committed by this executor per wave instructions).

## Files Created/Modified
- `src/R/regularization/psd_utils.R` (created) — canonical ridge + eigclip, bodies copied VERBATIM from refit_sh2b3 lines 71-87
- `src/R/regularization/refit_sh2b3_psd_regularized.R` (modified) — deleted inline PSD defs; added path-robust `source(psd_utils.R)` + `stopifnot(exists(...))`
- `tests/testthat-phase1/test_psd_utils_byte_identical.R` (created) — base-R stopifnot byte-identity gate
- `tests/testthat-phase1/fixtures/psd_golden_r3.rds` (created) — golden captured from the PRE-refactor inline source; **sha256 `335f944aac0d588970bc75e74f08b6e28888bd310d70c345f98c0cf4c7d24371`**
- `src/python/condition_ld_matrix.py` (created) — `condition_ld_matrix` + `_fully_nan_rows_blocked` + `_nan_offdiag_pairs_blocked`
- `tests/m3/test_condition_ld_matrix.py` (created) — 14 cases
- `src/python/write_conditioned_ld_npz.py` (created) — `write_conditioned_npz`
- `tests/m3/test_write_conditioned_ld_npz.py` (created) — 10 cases

## Frozen Contracts (byte-unchanged, verified)
SHA-256 snapshotted before Task 1 and re-verified after Task 3 (git diff + status empty for all):
- `src/python/plink_ld_to_npz.py` — `45b46096...5653027` (read_square_bin raise-on-NaN + content_verify_npz reuse-only, unmodified)
- `src/python/run_native_ld_panel.py` — `1cd97039...4e4d636` (content_verify_npz untouched — actively asserted per fold-in #2)
- `src/scripts/ld_npz_to_rds.R` — `0b52c589...b32b03d` (ingest key set unchanged; conditioned .rds materialization is §5)

## Decisions Made
- **Float ceiling.** `ceiling_n = ceiling_frac * n_var` kept as a float; `n_zeroed_pairs > ceiling_n` matches both the amendment's "<= 51 pairs @ n_var=102421" (51.21) and the plan's n=4000 -> ceiling_n=2.0 boundary (1 pair passes, 5 raise).
- **Unordered-pair collection from either triangle.** `_nan_offdiag_pairs_blocked` records `(min,max)` and de-duplicates, so a symmetric plink NaN counts once and a lone lower-triangle NaN is still paired; both coordinates zeroed.
- **Fit-time PSD boundary.** `psd_method="PENDING_FIT_TIME"`, `psd_lambda=NaN` placeholders in the conditioned `.npz`; PSD (eigclip primary / ridge companion) runs on the fine-mapping submatrix at fit time (§5), not on the full n_var~1e5 panel.
- **Provenance-name unification (fold-in #3).** The `.npz` key `n_zeroed` IS the record's `n_zeroed_pairs` — documented in both module docstrings and asserted in the round-trip test.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added an unsupported-nan_policy guard + a non-square-input guard to `condition_ld_matrix`**
- **Found during:** Task 2 (condition_ld_matrix implementation)
- **Issue:** The amendment pre-registers exactly one policy (`off_diagonal_zero`); without a guard a caller passing a different label would silently receive off_diagonal_zero behavior mislabeled in the provenance record (a reproducibility/repudiation hazard, T-m3-06-02 class). A non-square matrix would also silently mis-scan.
- **Fix:** `condition_ld_matrix` raises `ValueError` on any `nan_policy != "off_diagonal_zero"` and on a non-square input, before any scan/mutation. Added two covering tests (`test_unsupported_nan_policy_raises`, `test_non_square_input_raises`).
- **Files modified:** src/python/condition_ld_matrix.py, tests/m3/test_condition_ld_matrix.py
- **Verification:** both new tests pass; part of the 14/14 GREEN suite.
- **Committed in:** ccca5b8 (Task 2 GREEN) + d73ac70 (tests)

---

**Total deviations:** 1 auto-fixed (1 missing-critical validation guard).
**Impact on plan:** Correctness/reproducibility safeguard consistent with the pre-registered single-policy commitment. No scope creep — the raw contract, r3 numerics, and the frozen modules are untouched; §5/§6 not entered.

### Plan-check fold-ins applied
1. `dir.create("tests/testthat-phase1/fixtures", recursive=TRUE)` before `saveRDS` in the golden-capture (dir did not pre-exist).
2. `src/python/run_native_ld_panel.py` added to the git-diff/SHA freeze assertion so "content_verify_npz untouched" is ACTIVELY verified.
3. Provenance name unified: `.npz` key `n_zeroed` == record `n_zeroed_pairs` (documented + asserted).
4. `ceiling_frac` provenance key retained (records the pre-registered 0.0005 ceiling; benign, not a fine-mapping-tunable).

## Issues Encountered
- Full `tests/m3` suite is slow (~8 min) and exceeds a 2-minute foreground timeout — ran it as a background task to completion (360 passed / 30 skipped). No GPFS git object-store loss occurred during any commit (all commits landed first-try; no `hash-object -w` recovery needed). Not pushed to origin (optional; NCSU local HEAD advanced 6 commits ahead of 205b03e).

## Residual Track-A byte-identity risk note (per plan output)
- **`source()` path resolution under LSF cwd.** `refit_sh2b3` now sources `psd_utils.R` via the same dual-path block as `snp_id_bridge.R` (script-relative via `commandArgs('--file=')`, fallback to `src/R/regularization/psd_utils.R`). LSF jobs run with cwd=project root and the fallback resolves there; the byte-identity test exercises the script-relative branch. A `stopifnot(exists(...))` guard hard-fails fast if resolution ever misses.
- **BLAS/LAPACK determinism unchanged.** `eigen(symmetric=TRUE)` in `psd_regularize_eigclip` calls the SAME LAPACK as the pre-refactor inline version (identical function body, same m3-r-ld R install); `identical()` bit-equality held across the separate capture and test processes. The refactor moves code, not the numeric path — no new BLAS surface introduced.

## Next Phase Readiness
- Machinery ready for §5 (fit-time wiring against the real AFR panel: apply `psd_utils.R` PSD to the region submatrix, fill `psd_method`/`psd_lambda`, materialize the conditioned `.rds`) and §6 (in-perimeter region-1 verification) — both remain **PARKED / LOOP-GATED** in ROADMAP 999.1.
- **Do NOT** fire/re-fire anything in-perimeter: the 276-region AoU LD loop is still running; the panel does not exist yet. This wave was entirely NCSU-local on synthetic + region-1's characterized topology.

## Self-Check: PASSED
- All 7 created source/test/fixture files + the SUMMARY exist on disk (FOUND).
- All 6 task commits exist in the log (`0150459`, `47707ad`, `d73ac70`, `ccca5b8`, `aa753ba`, `f147041`).
- `refit_sh2b3_psd_regularized.R`: 0 inline PSD defs, 1 `source(psd_utils)` line.
- Frozen contracts (plink_ld_to_npz.py, run_native_ld_panel.py, ld_npz_to_rds.R) SHA-unchanged, git diff/status empty.
- Byte-identity: all 16 `identical()` TRUE. Region-1 topology: `n_zeroed_pairs == 6`. Full suite: 360 passed / 30 skipped.

---
*Phase: m3-aou-afr-ld-panel-build*
*Completed: 2026-07-07*
