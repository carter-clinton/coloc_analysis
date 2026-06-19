---
phase: 260619-qjy
plan: 01
subsystem: m3-aou-ld
tags: [m3, aou-ld, path-a3, allele-freq, af-sidecar, tdd, wr-03]
requires:
  - aou_ld_panel.py {rid}.allele_freq.tsv sidecar (A.3 producer, committed m3-02b)
  - ld_npz_to_rds.R allele_freq reader -> obj$variants$AF (committed m3-02b)
provides:
  - bm_to_npz.py --allele-freq CLI arg + allele_freq_tsv param
  - .npz allele_freq key (always emitted; row-aligned; NaN-filled when omitted)
  - AF flows end-to-end A.3 sidecar -> .npz -> obj$variants$AF
affects:
  - m3-04 production A.3 fire (precondition: A.3 ships LD+AF, not NA AF)
tech-stack:
  added: []
  patterns:
    - NaN-aware line-wise float sidecar loader (blank -> np.nan, WR-03)
    - loud-on-omission (all-NaN key + stdout WARNING) instead of silent NA
    - row-alignment length-guard ValueError (mirror variant_ids/rsids guards)
    - stub-hail sys.modules injection so converter-level tests run without Hail
key-files:
  created: []
  modified:
    - src/python/bm_to_npz.py
    - tests/m3/test_ld_npz_to_rds.py
decisions:
  - "AF key ALWAYS emitted (NaN-filled + loud WARNING when --allele-freq omitted) so a forgotten sidecar is auditable, never silently shipping NA AF (T-qjy-03)"
  - "Blank sidecar line -> np.nan, never fake 0.0 (WR-03 missing-vs-zero distinction preserved into obj$variants$AF)"
  - "Converter-level AF tests inject a stub hail module so they RUN (not skip) on Hail-less envs; A.3 end-to-end test stays R-env-gated"
metrics:
  duration: ~30m (excl. 2x 6.5min full-suite runs)
  tasks: 3
  files: 2
  completed: 2026-06-19
---

# Phase 260619-qjy: Close A.3 AF Sidecar Gap (allele_freq for large/xlarge LD regions) Summary

`bm_to_npz.py` now carries the A.3 `{rid}.allele_freq.tsv` sidecar into the
`.npz` `allele_freq` key (row-aligned, NaN-aware), closing the middle-converter
gap that left every Path A.3 (large/xlarge) region shipping NA AF — an m3-04
production precondition.

## What Was Built

`bm_to_npz.py` was the only break in the AF chain: the AoU-side
`aou_ld_panel.py` already emits a row-aligned `{rid}.allele_freq.tsv` sidecar
(WR-03 NaN for missing), and the R reader `ld_npz_to_rds.R` already reads
`z$f[["allele_freq"]]` into `obj$variants$AF` (both committed m3-02b). The
converter wrote `ld/variant_ids/rsids/lower_triangular` but NOT `allele_freq`,
so AF died in the middle.

Added to `bm_to_npz.py`:

- `_load_af_sidecar(path)` — NaN-aware line-wise float loader. A blank /
  whitespace-only line → `np.nan` (WR-03: genuinely-missing AF, never a fake
  0.0, which for a MAF≥0.005-prefiltered cohort would mask a collection fault);
  `np.asarray(dtype=float)`, 1-D even for a single-variant region. (`np.loadtxt`
  with `dtype=float` chokes on blanks → line-wise parse.)
- `--allele-freq` CLI arg (`dest=allele_freq_tsv`, optional, `type=Path`,
  default `None`) + `allele_freq_tsv: Path | None = None` param on
  `bm_to_npz()`, threaded from `main()`.
- Row-alignment length-guard: `allele_freq` length ≠ `n_rows` raises a loud
  `ValueError` naming both lengths + the sidecar + `out_npz` (mirrors the
  existing variant_ids/rsids guards; T-qjy-01 row-alignment invariant).
- Omission path: `np.full(n_rows, np.nan)` + a loud stdout `WARNING` naming the
  out path and the missing `--allele-freq` (T-qjy-03 — absence is auditable, not
  silent).
- `allele_freq=allele_freq` added to the existing `np.savez_compressed` call —
  the key is ALWAYS present. `ld/variant_ids/rsids/lower_triangular` keys
  unchanged (BR-01 fix intact).
- Module Usage block + `bm_to_npz()` Args docstring document the
  `--allele-freq` line and the sidecar contract.

## TDD Flow

| Task | Phase | Commit | What |
| ---- | ----- | ------ | ---- |
| 1 | RED | `c14c3e8` | 4 AF-contract tests (3 converter-level + 1 A.3 end-to-end); converter-level tests FAILED with `TypeError: unexpected keyword argument 'allele_freq_tsv'` |
| 2 | GREEN | `5ef39d6` | `_load_af_sidecar` + `--allele-freq` + always-emit `allele_freq` key; all 4 AF tests pass |
| 3 | REGRESSION | (no code) | full `tests/m3` suite — 198 passed / 0 failed / 30 skipped |

New tests in `tests/m3/test_ld_npz_to_rds.py`:

- `test_bm_to_npz_writes_allele_freq_when_provided` — `--allele-freq` with a
  blank middle line → `allele_freq = [0.12, nan, 0.34]`, row-aligned, length
  n_rows; existing keys intact.
- `test_bm_to_npz_omitted_allele_freq_is_all_nan_and_warns` — no `--allele-freq`
  → all-NaN key (length n_rows) + stdout substring `WARNING` / `no --allele-freq`.
- `test_bm_to_npz_misaligned_allele_freq_raises` — length 2 vs 3 rows → loud
  `ValueError` naming lengths + `out.npz`.
- `test_a3_style_npz_carries_af_into_variants` (R-env-gated) — a hand-built
  A.3-shaped `.npz` (`np.tril` ld + 2 FTO-liftable vids + rsids +
  `lower_triangular=[True]` + `allele_freq=[0.12, 0.34]`) → `ld_npz_to_rds.R` →
  `obj$variants$AF == [0.12, 0.34]`. A new `_read_rds_with_af` helper dumps
  `obj$variants$AF` (`na="null"`).

The three converter-level tests inject a minimal stub `hail` module into
`sys.modules` (a `BlockMatrix.read` returning a known dense matrix) so the REAL
`bm_to_npz()` AF code path (loader + length-guard + savez) runs without a Hail
JVM — they do NOT skip on Hail-less envs (smoke_dev has no Hail). The A.3
end-to-end test stays R-env-gated via `rscript_or_skip` (m3-r-ld present here →
it RAN and passed).

## Test Results

- Baseline (entry): **194 passed / 0 failed / 30 skipped**.
- After (exit): **198 passed / 0 failed / 30 skipped** (+4 AF tests, all GREEN;
  zero regressions). BR-01 tests
  (`test_bm_to_npz_static_writes_lower_triangular_flag`,
  `test_bm_style_lower_tri_npz_recovers_true_r`, `test_bm_to_npz_helper`) still
  pass/skip exactly as before — the `allele_freq` addition did not disturb
  `ld`/`lower_triangular`. Skip count unchanged at 30 (m3-r-ld present → the A.3
  end-to-end test ran rather than adding to skips; the 30 skips are the existing
  Hail-gated `test_bm_to_npz_helper` + other env-gated cases).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] stub-hail bm_dir is_dir() guard + all-blank rsids loadtxt quirk in test fixtures**
- **Found during:** Task 2 (GREEN), first test run.
- **Issue (a):** `bm_to_npz()` correctly guards `bm_dir.is_dir()` before the
  (stubbed) Hail read; the converter-level tests passed a non-existent
  `fake.bm`, so the guard fired before the AF path. **Issue (b):** the tests
  wrote all-blank `rsids.tsv` (`"\n".join([""]*n)`), and `_load_sidecar`
  (`np.loadtxt`) collapses an all-blank file to a length-0 array → the
  pre-existing rsids length-guard tripped (`rsids length 0 != BlockMatrix rows
  3`) before the AF assertions.
- **Fix:** `mkdir` the `fake.bm` directory in each converter-level test (the
  stub read ignores its contents); write non-empty placeholder rsids
  (`rs0..rsN`). Both are test-fixture corrections so the tests exercise the real
  AF code path — NO production change to the `is_dir()` guard or `_load_sidecar`
  (the all-blank `_load_sidecar` quirk is pre-existing and out of scope; real
  A.3 sidecars are not all-blank).
- **Files modified:** `tests/m3/test_ld_npz_to_rds.py` (committed with Task 2).
- **Commit:** `5ef39d6`

## Threat Surface

All three plan threats addressed as specified — no new surface introduced:

- **T-qjy-01** (Tampering, row-misaligned AF) — `mitigate` — loud `ValueError`
  on `allele_freq` length ≠ `n_rows`, naming lengths + out path.
- **T-qjy-02** (Info disclosure, manual converter on egressed BM) — `accept` —
  inherits the existing `T-M3-EGR-W3` ACCEPT; AF is a population summary stat.
- **T-qjy-03** (Repudiation, forgotten sidecar silently shipping NA AF) —
  `mitigate` — omission writes all-NaN key + loud stdout WARNING; WR-03 keeps
  missing(NaN) distinct from a real 0.0.

## Known Stubs

None. The `allele_freq` key is always populated (real floats or explicit NaN
with a loud warning) — no silent placeholder. The only "stub" is the test-side
`sys.modules` Hail injection, which is intentional test infrastructure to run
the converter AF path without a JVM, not a product stub.

## Carry-forward

The m3-04 A.3 precondition tracked in STATE/HANDOFF ("bm_to_npz writes no
allele_freq → A.3 regions get NA AF", DEFERRED from m3-02b BR-01 sweep) is now
CLOSED. A.3 can ship LD+AF provided the operator passes `--allele-freq
{rid}.allele_freq.tsv` (and is loudly warned if they forget).

## Self-Check: PASSED

- `src/python/bm_to_npz.py` — FOUND (allele_freq loader, guard, savez key, docstring).
- `tests/m3/test_ld_npz_to_rds.py` — FOUND (4 new AF tests + helpers).
- Commit `c14c3e8` (Task 1 RED) — FOUND.
- Commit `5ef39d6` (Task 2 GREEN) — FOUND.
- `git diff --stat` lists ONLY `bm_to_npz.py` + the test file; `aou_ld_panel.py`
  and `ld_npz_to_rds.R` untouched — VERIFIED.
