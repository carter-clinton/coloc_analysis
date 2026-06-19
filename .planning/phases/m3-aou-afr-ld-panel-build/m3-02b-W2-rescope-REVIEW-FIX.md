---
phase: m3-02b-W2-rescope
fixed_at: 2026-06-19T00:00:00Z
review_path: .planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase m3-02b: Code Review Fix Report

**Fixed at:** 2026-06-19
**Source review:** .planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (CR-01 + WR-01 + WR-02 + WR-03)
- Fixed: 4 (all RED-first regression tests now GREEN)
- Skipped: 0
- Out of scope (Info, NOT fixed): IR-01, IR-02, IR-03, IR-04 — see "Out-of-Scope" below.

**Final test tally:** `pytest tests/m3 -q` -> **186 passed, 0 failed, 36 skipped**
(the 36 skips are pre-existing fixture-absent skips: missing hg19ToHg38 chain,
missing M2 union BED, `hail not installed` in the smoke_dev env — none introduced
by these fixes; baseline was identical). The R-dependent stitch/loader families
RAN (no skip) in the M3 env (`m3-r-ld`): `test_stitch_subregions_to_rds.py` 15
passed, `test_finemap_loader_contract.py` 2 passed.

---

## Fixed Issues

### CR-01: Symmetry-recovery DOUBLES every off-diagonal r on FULL (Path A.1) matrices

**Files modified:** `src/scripts/ld_npz_to_rds.R`, `src/scripts/stitch_subregions_to_rds.R`, `tests/m3/test_stitch_subregions_to_rds.py`
**Commit:** 3b2de9a
**Severity:** Critical (silent LD corruption fed to SuSiE-RSS)

**Applied fix:** Both R scripts now HONOR the `lower_triangular` flag the `.npz`
already carries (`aou_ld_panel.py:2642`). The one-sided recovery
`tri + t(tri) - diag(diag(tri))` runs ONLY when the flag is `TRUE` (Path A.2
lower-tri). For a FULL matrix (flag `FALSE` or absent — Path A.1) the code applies
ONLY the idempotent `tri <- (tri + t(tri)) / 2` projection (avg(r,r)=r — kills the
~1e-7 float32 Hail block-sum asymmetry WITHOUT doubling). The `!isSymmetric` gate
that was the trap (its ~2.2e-14 tol tripped on 1e-7 noise → fired the doubling
branch) is REMOVED; the symmetrizer is now ALWAYS applied. The WR-003 float32
rationale comment is kept and corrected to reference the flag.

**TDD evidence (RED → GREEN):**
- RED: added `test_whole_region_full_matrix_float32_asymmetric_not_doubled`
  (whole-region `ld_npz_to_rds.R` path) and
  `test_stitch_full_window_float32_asymmetric_not_doubled` (stitch per-window
  path), each feeding a FULL float32 matrix with ~1e-7 triangle asymmetry and
  `lower_triangular=False`. Confirmed FAILING against the unfixed code:
  `full-window off-diagonal DOUBLED: 1.2 (CR-01)` (true r 0.6 → 1.2).
- GREEN: after the fix both assert the recovered off-diagonal ≈ true r (0.6, 0.3),
  diag==1, symmetric. Existing full-symmetric stitch families
  (`test_stitch_cross_core_band_retained`, `test_stitch_banded_psd`,
  `test_whole_region_payload_reconciled`) remain GREEN (no regression).

### WR-01: Default buffer reintroduces the capacity wall (parent-spanning window)

**Files modified:** `src/python/build_ld_region_manifest.py`, `tests/m3/test_build_ld_region_manifest.py`
**Commit:** 56e2974
**Severity:** Warning (cost regression to the ~65 GiB master-crash wall)

**Applied fix (LOUD guard, override preserved):** Added
`SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC = 0.90` + a guard in
`build_manifest`'s split branch. When NO explicit `--subregion-buffer-mb` is
given (radius default) AND the widest resulting compute window span reaches
≥ 90% of the parent span — the exact parent-spanning / 65 GiB-master-crash
condition — the build RAISES `SUBREGION_BUFFER_GUARD` with an actionable message
telling the user to pass an explicit `--subregion-buffer-mb` (citing the Pan-UKBB
AFR/EUR 10 Mb anchor). An explicit override is always honored and bypasses the
guard, so m3-02c can widen + measure freely.

**Plan-deviation rationale (REQUIRED disclosure):** The plan's locked `must_have`
states the buffer "default = the region radius i.e. min(core_span+500kb, 50Mb)".
This fix does NOT change that default value (so it does not pre-empt m3-02c's
band-width science, which the plan assigns to the m3-02c cost probe) — it GUARDS
the default so its silent-failure mode (a parent-spanning window) becomes an
explicit, actionable error rather than a $-burning intractable fire. This honors
BOTH the plan's "default = region radius" lock AND its own CLI directive "DO NOT
silently keep 50 Mb". m3-02c still owns and measures the correct band width; the
override remains the lever. The radius-default path is now fail-closed, not
fail-silent.

**TDD evidence (RED → GREEN):** Replaced the enshrining
`test_buffer_bp_defaults_to_region_radius_when_unset` (which actively ASSERTED
the dangerous 50 Mb default as "expected") with
`test_default_buffer_parent_spanning_window_guard_raises`: asserts the radius
default on a 90 Mb xlarge now `pytest.raises(ValueError, match="SUBREGION_BUFFER_GUARD")`,
AND that an explicit `--subregion-buffer-mb 10` still builds a bounded (≤31 Mb)
window. Confirmed the new assertion is satisfied only after the guard was added.
Updated `test_subregion_region_ids_match_sub_suffix` to pass an explicit buffer
(it tests id suffixes, not the buffer default).

### WR-02: Completeness guard silently bypassed when .npz filenames lack `__subNN`

**Files modified:** `src/scripts/stitch_subregions_to_rds.R`, `tests/m3/test_stitch_subregions_to_rds.py`
**Commit:** 0f496e7
**Severity:** Warning (silent incomplete LD panel)

**Applied fix:** Subregion identity is now AUTHORITATIVE from the manifest. In the
per-`.npz` loop, an un-inferable index (`infer_sub_index` returns `NA` because the
filename lacks `__subNN`) is now a hard `STITCH_INPUT` `stop()`, never a silent
pass. The downstream completeness check is made UNCONDITIONAL
(`length(unique(seen_idx)) != n_subregions` → error), removing the
`length(seen_idx) > 0L` bypass that let an all-un-named npz set slip past.

**TDD evidence (RED → GREEN):** Added
`test_stitch_completeness_guard_not_bypassed_by_filename`: a 2-subregion parent
fed ONE npz named `window_zero.npz` (no `__sub` token). Confirmed FAILING against
the unfixed code — the stitch returned 0 and wrote an incomplete panel
("`M=2; ... 2 sub-regions`" while only 1 window was given). After the fix the
stitch exits non-zero with a `STITCH_INPUT` error. GREEN.

### WR-03: AF `0.0` sentinel for null is indistinguishable from a real AF of 0

**Files modified:** `src/python/aou_ld_panel.py`, `tests/m3/test_build_ld_region_manifest.py`, `tests/m3/test_stitch_subregions_to_rds.py`
**Commit:** a3f32f2
**Severity:** Warning (masks a collection fault)

**Applied fix:** The load-bearing change is the Python collection path
(`aou_ld_panel.py`). Added a unit-testable `_af_or_nan()` helper that maps a null
AF to `float("nan")` (instead of the old `0.0`) and replaced the comprehension at
the former line 2274 with `[_af_or_nan(a.af) for a in aligned]`. A NaN flows
through `_save_npz` (which only asserts presence + length, not value range) into
the R `obj$variants$AF` as `NA` (R `is.na(NaN)` is TRUE), so "missing" is now
auditable and distinguishable from a genuine (post-MAF-filter-impossible) AF of 0.
The R payload paths (`ld_npz_to_rds.R::parse_variants_frame` /
`stitch_subregions_to_rds.R`) already carried AF via `as.numeric`, which preserves
NaN→NA — so no R change was needed for the survival contract.

**TDD evidence (RED → GREEN):**
- RED (Python): `test_af_null_becomes_nan_not_zero` asserts `_af_or_nan(None)` is
  NaN and a real `0.0` stays distinguishable. Against the unfixed code the helper
  did not exist (AttributeError) — RED.
- RED→GREEN (R end-to-end): `test_whole_region_null_af_survives_as_na_not_zero`
  feeds an `.npz` with `[NaN, 0.0, 0.3]` AF through `ld_npz_to_rds.R` and asserts
  `is.na(v$AF[1])` (missing → NA), `v$AF[2] == 0.0` (genuine zero preserved),
  `v$AF[3] ≈ 0.3`. GREEN.
- Note: this finding is a value-semantics fix, not a pure logic bug; both the
  Python helper test and the R round-trip test directly assert the corrected
  semantics, so it is reported as `fixed` (not "requires human verification").

---

## Out-of-Scope (Info findings — NOT fixed this iteration)

Per the fix scope (`critical_warning`) these 4 Info items were intentionally
NOT addressed and are deferred (not silently dropped):

- **IR-01** — `diag(R) <- 1` masks a real computed diagonal != 1 (lost QC signal).
  Deferred: correctness-neutral for valid data; a diagnostic enhancement.
- **IR-02** — liftover can map two distinct GRCh38 variants to the same b37 SNP_ID;
  not asserted. Deferred: low likelihood; suggested `stopifnot(anyDuplicated...)`.
- **IR-03** — `__sub` index regex breaks at ≥ 100 sub-regions (`[0-9]{2}`).
  Deferred: not reachable today (10 Mb cores cap at ~25 subs).
- **IR-04** — hardcoded user-specific conda path in TEST discovery
  (`tests/m3/test_stitch_subregions_to_rds.py:48-49`). Deferred AND out of scope
  per the project convention: it is in a TEST (overridable via `M3_R_LD_RSCRIPT`
  env var + `shutil.which` fallback), committed `src/` is clean of hardcoded paths
  (REQ-PATH-PARAMETERIZATION satisfied).

---

_Fixed: 2026-06-19_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
