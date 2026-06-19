---
phase: m3-02b-W2-rescope
reviewed: 2026-06-19T00:00:00Z
depth: deep
files_reviewed: 10
files_reviewed_list:
  - src/scripts/stitch_subregions_to_rds.R
  - src/scripts/ld_npz_to_rds.R
  - src/python/build_ld_region_manifest.py
  - src/python/select_ld_regions_dev.py
  - src/python/aou_ld_panel.py
  - tests/m3/test_stitch_subregions_to_rds.py
  - tests/m3/test_build_ld_region_manifest.py
  - tests/m3/test_finemap_loader_contract.py
  - tests/m3/test_sparse_parent_benchmark.py
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
findings:
  critical: 1
  warning: 3
  info: 4
  total: 8
status: issues_found
---

# Phase m3-02b: Code Review Report (ADVERSARIAL DEEP)

**Reviewed:** 2026-06-19
**Depth:** deep
**Files Reviewed:** 10
**Status:** issues_found

## Summary

This was an adversarial deep review of the m3-02b overlapping-window banded stitch
(commits a17a47a / 0e3ec43 / 908de71), the LD-panel build code that feeds SuSiE-RSS
fine-mapping. The brief was to BREAK the code, not bless it, with special focus on
silent numerical corruption that passes every unit test.

**The banded overlapping-window stitch geometry is CORRECT** — I verified this with
fuzzing, not by reading comments (evidence below). The central fix that distinguishes
this from the previously-rejected block-diagonal design genuinely works:

* **No cross-core band fall-through.** I fuzzed 200k random cross-core variant pairs
  within `buffer_bp` under both `buffer == core_span` and `buffer < core_span`
  configurations. Every such pair is contained in at least one compute window
  (`stitch_subregions_to_rds.R:223` `abs(pa$pos - pb$pos) <= buffer_bp` stages it; the
  window `[core_start - buffer, core_end + buffer]` provably contains both endpoints of
  any within-buffer cross-core pair). **0 fall-throughs.**
* **Band condition is coordinate-consistent.** The stitch bands on GRCh38 positions
  (`pa$pos`/`pb$pos` parsed from the b38 `variant_ids`), and the compute-side A.3 band
  (`_write_a3_banded_correlation_bm` → `locus_windows(mt_r.locus, radius_bp)`) is also
  GRCh38. Liftover to GRCh37 happens AFTER ownership/banding. Consistent.
* **Overlap-pair reconciliation is correct.** `stitch_subregions_to_rds.R:300-319` is
  first-writer-wins + a `> 1e-4` disagreement `stop()`. No averaging, no summing, no
  double-count. Because both windows compute the SAME pair from the SAME genotypes, the
  two float32 r values are bit-identical, so agreement is exact.
* **Symmetrization does not corrupt the band.** Staged pairs are upper-triangle
  (`lo_i <= hi_j`), so `R + t(R)` moves them to the lower triangle with no overlap
  (no doubling); the diagonal is hard-set to 1 (`:332`, `:338`). Verified algebraically.
* **Core ownership is half-open and bijective** (`:252` `pos38 >= core_start && pos38 <
  core_end`), de-duped on the GRCh38 `(chr,pos,ref,alt)` key (`:274`). Multiallelic sites
  are NOT collapsed. Cores tile `[start,end)` exactly (verified: exact-multiple,
  remainder, core>region, n=1 edge cases all tile with `covered == span`).

**However, I found one CRITICAL silent-corruption bug that is invisible to the entire
test suite**, plus a WARNING that the default config reintroduces the very capacity wall
this re-scope was built to fix. Details below.

---

## Critical Issues

### CR-01: Symmetry-recovery DOUBLES every off-diagonal r on FULL (Path A.1) matrices

**File:** `src/scripts/ld_npz_to_rds.R:117` (and identically `src/scripts/stitch_subregions_to_rds.R:171`)

**Issue:**
```r
if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))
tri <- (tri + t(tri)) / 2
```
This recovery formula `tri + t(tri) - diag(diag(tri))` is **only valid when `tri` is
one-sided (lower-triangular, upper == 0)** — the A.2 case. For a **FULL symmetric**
matrix it doubles every off-diagonal entry (`r` → `2r`), and the subsequent
`(tri + t(tri))/2` does NOT undo it (a doubled symmetric matrix stays doubled after
re-symmetrization). I verified numerically: a full `[[1,0.6],[0.6,1]]` with one entry
0.6000001 and its mirror 0.5999999 becomes `[[1,1.2],[1.2,1]]`.

Path **A.1 (small regions ≤ 5 Mb) writes a FULL matrix** via `ld_bm.to_numpy()`
(`aou_ld_panel.py:2290`, no triangle sparsify; `_save_npz` records
`lower_triangular=False`). The R scripts **never consult the `lower_triangular` flag**
in the .npz — they apply the lower-triangular recovery unconditionally. Small whole
regions are NOT split, so they flow through `ld_npz_to_rds.R` (the whole-region
converter), hitting this branch.

The guard is `if (!isSymmetric(tri))`. R's `isSymmetric` default tolerance is
`100 * .Machine$double.eps ≈ 2.2e-14`. A float32-origin LD matrix widened to float64
carries ~1e-7 triangle asymmetry — **~7 orders of magnitude above tolerance** — so
`isSymmetric` returns FALSE and the doubling branch FIRES. The code's own WR-003 comment
(`ld_npz_to_rds.R:108-116`) confirms `isSymmetric(tri)` is routinely FALSE for real
regions (HLA, 8p23). For such a region the off-diagonal r values are silently doubled,
corrupting the LD panel fed to SuSiE-RSS. Where `2r > 1` the matrix goes non-PSD (may
fail loudly); where `2r ≤ 1` (e.g. 0.4→0.8) it corrupts credible sets SILENTLY — exactly
the failure mode m3-REVIEWS HIGH#1 was about.

**Why the test suite misses it:** `_write_window_npz`
(`test_stitch_subregions_to_rds.py:184`) writes a FULL but EXACTLY symmetric `ld`
(hand-built, e.g. `[[1,0.6],[0.6,1]]`), so `isSymmetric` returns TRUE and the doubling
branch is never taken. The only lower-triangular fixture
(`test_whole_region_payload_reconciled:534` `np.tril(ld)`) IS valid for the recovery.
**No test ever feeds a full matrix with float32 asymmetry — the exact production A.1
shape.** The bug is structurally invisible to the suite.

**Fix:** Consult the `lower_triangular` flag the .npz already carries, and only run the
one-sided recovery when the input is actually one-sided; for a full matrix just
symmetrize:
```r
lower_only <- tryCatch(as.logical(z$f[["lower_triangular"]])[1], error = function(e) FALSE)
if (isTRUE(lower_only)) {
  # one-sided input: mirror the populated triangle
  tri <- tri + t(tri) - diag(diag(tri))
} else {
  # full input: already two-sided — only project out float asymmetry, never double
  tri <- (tri + t(tri)) / 2
}
diag(tri) <- 1   # diag(R)==1 by construction; reset to suppress float drift
```
Then add a regression test that feeds a FULL float32 matrix whose two triangles differ
by ~1e-7 and asserts the recovered off-diagonal equals the true r (NOT 2r). Apply the
same fix to `stitch_subregions_to_rds.R:171` (the per-window `tri` there is the A.3
banded npz, normally lower-ish, but the same unconditional-double hazard exists if a
full window npz is ever passed).

---

## Warnings

### WR-01: Default `buffer_bp = 50 Mb` reintroduces the capacity wall the split exists to fix

**File:** `src/python/build_ld_region_manifest.py:497` (`buffer_bp = ... else radius_bp`); test `test_build_ld_region_manifest.py:334-338`

**Issue:** When `--subregion-buffer-mb` is not given, `buffer_bp` defaults to the parent
`radius_bp = min(span + 500kb, 50Mb)` — i.e. **50 Mb for every xlarge region**. With the
10 Mb core, each compute window then becomes `core + 2×buffer = 10 + 100 = up to 90 Mb`
(clamped to the parent). I confirmed: for a 90 Mb region with default buffer, windows are
60–90 Mb wide and the FIRST SIX windows each span essentially the whole parent. Each
window's dense scratch (`_write_a3_banded_correlation_bm` checkpoints the FULL DENSE
`n_var × n_var` correlation, per CR-01 note at `aou_ld_panel.py:2557`) is then ~parent-
sized — exactly the ~65 GiB master-crash / "intractable" wall documented in
project_state (dev-10 KILLED). The split tiles correctly but the default buffer defeats
the bounded-scratch purpose. The numerics stay correct; the COST regresses to the
pre-split catastrophe.

The code is self-aware (CLI help: "DO NOT silently keep 50 Mb"; m3-02c YELLOW
disposition), and `test_buffer_bp_defaults_to_region_radius_when_unset` ACTIVELY ASSERTS
the 50 Mb default — locking in the dangerous behavior as "expected." This is the
[[feedback_size_cost_experiments_on_real_data_dimensions]] failure mode: a window-cost
number must be sized on real density before the default ships.

**Fix:** Make the default buffer a bounded multiple of the core span (e.g.
`buffer_bp = min(radius_bp, core_span_bp)`, i.e. 10 Mb), not the 50 Mb parent radius, OR
make `--subregion-buffer-mb` REQUIRED when any region splits (fail closed). At minimum,
emit a loud manifest-build WARNING when `buffer_bp > core_span_bp` (window ≥ 3× core),
and change the test to assert the bounded default rather than enshrining 50 Mb.

### WR-02: Completeness guard silently bypassed when .npz filenames lack `__subNN`

**File:** `src/scripts/stitch_subregions_to_rds.R:158-166, 233-237`

**Issue:** `infer_sub_index()` returns `NA` when a path has no `__subNN` token, and the
`seen_idx` accumulator is only appended `if (!is.na(idx))` (`:159`). The missing-child
guard is then `if (... && length(seen_idx) > 0L && length(unique(seen_idx)) <
n_subregions)` (`:233`). If ALL passed `--npz` paths lack the `__subNN` token,
`seen_idx` stays empty, `length(seen_idx) > 0L` is FALSE, and **the completeness check is
skipped entirely** — a stitch missing whole windows (and therefore missing whole core
intervals of the panel) proceeds silently and writes an incomplete LD matrix that passes
every downstream assertion (`nrow(variants) == nrow(R)` etc. are all internally
consistent on the partial set).

**Fix:** Treat an un-inferable index as an error, not a silent pass:
```r
if (is.na(idx)) stop("STITCH_INPUT: cannot infer subregion_index from ", npz_path,
                     " (expected __subNN); refusing to stitch (completeness unverifiable)")
```
or require `length(unique(seen_idx)) == n_subregions` unconditionally (every child MUST
map to a known sub-index).

### WR-03: AF `0.0` sentinel for null is indistinguishable from a real AF of 0

**File:** `src/python/aou_ld_panel.py:2274`

**Issue:**
```python
allele_freq = [float(a.af) if a.af is not None else 0.0 for a in aligned]
```
A null AF is coerced to `0.0`, which is a legitimate allele frequency value. Downstream
(`obj$variants$AF`) cannot distinguish "AF was missing" from "AF is genuinely 0". `0.0`
also silently passes the `_save_npz` `(af >= 0) & (af <= 1)` validity check
(`test_build_ld_region_manifest.py:500`). For variants surviving `MAF >= 0.005`
pre-filter a true 0.0 should be impossible, so a `0.0` here actually signals a collection
fault — which is being masked. The variant_qc path (`vqc.AF[1]`) should always be
populated; only the synthetic-fixture fallback risks nulls, but the sentinel hides the
fault either way.

**Fix:** Use `float("nan")` for nulls (then `obj$variants$AF` carries `NA`, which R/the
manuscript can audit), and tighten the validity assertion to flag any AF outside
`(0, 1)` for a `MAF >= 0.005`-filtered cohort, OR assert `a.af is not None` for the
variant_qc path and only allow NaN on the synthetic fallback.

---

## Info

### IR-01: `diag(R) <- 1` masks a real computed diagonal != 1 (lost QC signal)

**File:** `src/scripts/stitch_subregions_to_rds.R:332, 338`; `ld_npz_to_rds.R:118`

The diagonal is unconditionally forced to 1 after assembly. A self-correlation that the
compute produced as != 1 (a genotype-standardization fault, a constant/monomorphic
variant, an all-missing row) is a useful QC signal that is silently overwritten. Consider
asserting `all(abs(diag - 1) < tol)` BEFORE resetting (warn/record on violation) rather
than blindly clamping. Correctness-neutral for valid data; loses a diagnostic.

### IR-02: Liftover can map two distinct GRCh38 variants to the same b37 SNP_ID; not asserted

**File:** `src/scripts/stitch_subregions_to_rds.R:274 (b38-key uniqueness only)`,
`ld_npz_to_rds.R:183 (dimnames set, no uniqueness check)`

The stitch de-dupes on the GRCh38 `(chr,pos,ref,alt)` key, but liftover (`:287`) can
collapse two distinct b38 variants onto the same b37 position → duplicate `SNP_ID`
dimnames. The loader (`run_susie_rss.R:91`) matches via `match()`, which returns the
FIRST hit, silently dropping the duplicate from the credible-set window. Low likelihood
(distinct alleles rarely liftover-collapse), but add
`stopifnot(anyDuplicated(snp_ids_b37[!is.na(snp_ids_b37)]) == 0L)` after liftover so the
rare case fails loudly instead of silently mis-matching.

### IR-03: `__sub` index regex breaks at ≥ 100 sub-regions

**File:** `src/scripts/stitch_subregions_to_rds.R:134` (`regexpr("__sub([0-9]{2})")`)

`infer_sub_index` matches exactly 2 digits, while the manifest writes `f"__sub{k:02d}"`
which becomes `__sub100` for k≥100. The regex would read `10`, mis-identifying the
sub-index and either colliding with sub10 or mismatching the manifest set. Not reachable
today (10 Mb cores cap at ~25 subs on the largest chromosome), but brittle. Use
`__sub([0-9]+)` and pad the manifest writer to match width.

### IR-04: Hardcoded user-specific conda path in test discovery

**File:** `tests/m3/test_stitch_subregions_to_rds.py:48-49`

`M3_R_LD_RSCRIPT = Path("/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript")`
hardcodes one user's environment. It IS overridable via the `M3_R_LD_RSCRIPT` env var and
falls back to `shutil.which`, so this is a discovery hint, not production src (committed
`src/` is clean of hardcoded paths — REQ-PATH-PARAMETERIZATION satisfied). Still, prefer
deriving from `$CONDA_PREFIX` or an env var with no baked default for portability.

---

## Test-audit notes (adversarial)

* `test_stitch_overlap_pair_agreement` and `test_stitch_cross_core_band_retained` DO
  assert the retained band value equals the computed r (`abs(r_ab - 0.6) < 1e-3`), not
  merely non-zero — good. But both windows give the straddle pair the SAME r (0.6), so
  these tests cannot distinguish "keep one" from a hypothetical "average two equal
  values." The disagreement test (0.6 vs 0.9) covers the `stop()` path. Consider a
  fixture where the two windows carry r differing by < 1e-4 to prove first-writer-wins
  (not average).
* The sparse benchmark ceiling (8 GiB load vs ~18.6 GiB dense for M=50k) IS
  discriminating, not vacuous — a whole-parent densify would breach it. Acceptable.
* The no-skip R families correctly ERROR (not skip) when the M3 marker env is present but
  the toolchain is broken (`_require_m3_r_toolchain`). No hidden xfail path found.
* The Python manifest tests assert exact integers (9 subs, n_subregions, cap counts,
  tiling `covered == span`) — robust.
* **Coverage gap (ties to CR-01):** no test exercises a FULL float32-asymmetric .npz
  through either R script. Add one.

---

_Reviewed: 2026-06-19_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
