---
phase: m3-aou-afr-ld-panel-build
fixed_at: 2026-05-01T00:00:00Z
review_path: .planning/phases/m3-aou-afr-ld-panel-build/m3-aou-afr-ld-panel-REVIEW.md
iteration: 1
findings_in_scope: 13
fixed: 10
skipped: 3
status: partial
---

# Phase m3-aou-afr-ld-panel-build: Code Review Fix Report

**Fixed at:** 2026-05-01
**Source review:** .planning/phases/m3-aou-afr-ld-panel-build/m3-aou-afr-ld-panel-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 13 (4 Critical + 9 Warning; Info findings explicitly out-of-scope this pass)
- Fixed: 10
- Skipped: 3

**Verification protocol per fix:**
- Tier 1 (always): re-read modified file, confirm fix text + surrounding code intact.
- Tier 2 (preferred): `python -m ast` for .py files; pytest unit-test sweeps where coverage exists.
- Tier 3 (fallback): for .smk and .R files, syntax check is unsupported; relied on Tier 1 + pytest harness coverage.

**Existing pytest harness re-run after every fix:**
- `tests/m3/test_ld_panel_resolver.py` (8 tests) — all passing post-CR-001
- `tests/m3/test_aou_ld_panel_local.py` (6 non-Hail; 4 Hail-skipped) — all non-skipped passing
- `tests/m3/test_aou_export_landing.py` (5 tests) — all passing post-CR-004 + WR-004
- `tests/m3/test_ld_npz_to_rds.py` (3 non-Rscript; 7 skipped without Rscript) — all non-skipped passing

## Fixed Issues

### CR-001: resolver receives region_safe slug but AoU chain expects region_id

**Files modified:** `src/python/ld_panel.py`, `src/snakemake/rules/finemap.smk`
**Commit:** 6d2e753
**Applied fix:** Added `region_safe` keyword argument to `resolve_ld_path()` so the resolver substitutes `{region_id}` and `{region_safe}` placeholders independently. Updated `run_finemap.input.ld_matrix` lambda in `finemap.smk` to translate `wildcards.region` (the safe slug) to `region_id` via `REGION_SAFE_TO_ID` and pass both to the resolver. Default `region_safe=None` falls back to `region_id` for back-compat with non-finemap callers. Also addresses **WR-008** by adding a "Precedence: pin > strict_aou_only > fallback walk" note to the docstring.
**Verification:** All 8 tests in `tests/m3/test_ld_panel_resolver.py` still pass (the new keyword arg is optional, so the existing positional-call tests are unaffected).

### CR-002: rsids/variant_ids row-order may diverge from BlockMatrix row order

**Files modified:** `src/python/aou_ld_panel.py`
**Commit:** 1c713f9
**Status:** **fixed: requires human verification**
**Applied fix:** Replaced the two separate `aggregate_rows(hl.agg.collect(...))` calls with a single `aggregate_rows(hl.agg.collect(hl.struct(vid=..., rsid=...)))` so `variant_ids` and `rsids` are guaranteed to come from the same row traversal. Added defensive assertions `len(variant_ids) == n_var` and `len(rsids) == n_var` (also addresses **IR-003** and **WR-001**).
**Why human verification:** The fix preserves Hail's implicit "aggregate_rows row order = MT key (locus, alleles)" semantics, which is what `hl.ld_matrix` uses for its row indexing. This is the documented and expected alignment, but the contract is implicit. Carter should run the dev-fire 4-check validation pytest (`tests/m3/test_validation_check_*.py`) against the synthetic MT to confirm that `ld[i,i] == 1.0` (self-correlation diagonal) holds across all 10 dev-subset regions before declaring this fix verified.

### CR-003: Path A.3 BlockMatrix write does not emit variant_ids/rsids sidecar TSVs

**Files modified:** `src/python/aou_ld_panel.py`
**Commit:** c127a8d
**Applied fix:** Added sidecar TSV emission (`{rid}.variant_ids.tsv`, `{rid}.rsids.tsv`) alongside the BlockMatrix write in Path A.3, in both the local-test branch (`out_bucket is None`) and the bucket branch. Refactored the GCS upload code from `_save_npz` into a `_upload_to_gcs(local_path, out_bucket, blob_subpath)` helper so it can be reused for the Path A.3 sidecar uploads. The bucket-branch sidecars land at `{out_bucket}/bm/{rid}.{variant_ids,rsids}.tsv` so `gsutil cp -r` of `bm/` from the AoU side picks them up alongside the `.bm/` shards.
**Verification:** Tier 1 read-back + pytest sweep on non-Hail tests (Hail-dependent tests skipped on this devbox; Carter's dev-fire will exercise the Hail path).

### CR-004: ingest rule's manifest filter compares int vs string fragilely; X chr unreachable

**Files modified:** `src/snakemake/rules/m3_ingest_aou_ld.smk`
**Commit:** 336a392
**Applied fix:** (a) Dropped `X` from the `chr` wildcard constraint (now `r"[0-9]+"`) to match the M2 union scope (autosomes only per D-M2-09). (b) Coerced the manifest filter to string comparison on both sides via `manifest["chr"] = manifest["chr"].astype(str)` and `str(wildcards.chr)`. (c) Improved the empty-set error message to disambiguate scope-out-of-bounds from manifest-not-yet-built (now reports `manifest covers chrs {sorted(unique)}`).
**Verification:** All 5 tests in `tests/m3/test_aou_export_landing.py` still pass.

### WR-001: rsids fall-back branch not obviously per-row

**Files modified:** `src/python/aou_ld_panel.py`
**Commit:** 1c713f9 (subsumed by CR-002)
**Applied fix:** The single-struct-collect approach in CR-002 makes the fallback explicit: the `else` branch (no `rsid` in `mt_r.row`) emits `rsid=hl.str("")` per row, so the row count automatically matches `variant_ids` count. This is enforced by the new `assert len(rsids) == n_var` defensive check.

### WR-002: `_load_sidecar` returns 0-d array for single-variant TSV

**Files modified:** `src/python/bm_to_npz.py`
**Commit:** 9e7a161
**Applied fix:** Added `ndmin=1` to the `np.loadtxt(..., dtype=str, delimiter="\t", ndmin=1)` call so single-row TSVs return a 1-D array (length 1) rather than a 0-D scalar. Inline comment documents the rationale.
**Verification:** `python -m ast` passes; static-grep test in `tests/m3/test_ld_npz_to_rds.py` does not pin the loader signature, so still passes.

### WR-003: float32 cast on >10 Mb dense matrix loses precision in symmetry recovery

**Files modified:** `src/scripts/ld_npz_to_rds.R`
**Commit:** e445a5f
**Applied fix:** Added `tri <- (tri + t(tri)) / 2` after the existing `tri + t(tri) - diag(diag(tri))` recovery step. The (M + M^T) / 2 idempotent projection forces exact symmetry post-recovery, suppressing float32 ulp drift on huge HLA / 8p23 matrices that could otherwise leave `isSymmetric(tri) == FALSE` for downstream coloc/SuSiE Cholesky paths.
**Verification:** Tier 1 read-back; non-Rscript tests in `tests/m3/test_ld_npz_to_rds.py` still pass; static-grep test does not pin the recovery line. Note: AOU-LD-PIPELINE.md float32 vs float64 documentation update is deferred to a separate docs commit (out of scope this pass).

### WR-004: `_load_region_to_chr_index` reads manifest at DAG construction time but silently no-ops if missing

**Files modified:** `src/snakemake/rules/m3_ingest_aou_ld.smk`
**Commit:** cdcd2e9
**Applied fix:** Replaced the silent `return _REGION_TO_CHR.get(region_id)` (which returns `None` when manifest is missing) with explicit `WorkflowError` raises: one when the manifest is empty/missing (with full reproduction command), and one when the region_id is absent from the manifest (with the manifest's region count). Removed the now-unreachable `or "UNKNOWN"` fallback in the input lambda. Operators now see "run M3 Wave 0 first" instead of an opaque `MissingInputException` on `aou_export_complete.AFR.UNKNOWN`.
**Verification:** All 5 tests in `tests/m3/test_aou_export_landing.py` still pass (they exercise the happy path where the manifest exists).

### WR-007: ANCESTRY_VALUES rejects EUR_AOU/AFR_AOU but accepts MID/SAS

**Files modified:** `src/python/aou_ld_panel.py`
**Commit:** 3f56280
**Applied fix:** Introduced `SUPPORTED_ANCESTRIES = {"afr", "eur"}` constant alongside the existing `ANCESTRY_VALUES` (which is retained as the documented AoU pred-label space). Tightened `load_qc_cohort` to validate against `SUPPORTED_ANCESTRIES` with a diagnostic that distinguishes "documented AoU pred labels" from "M3-supported ancestries" so a future contributor invoking `load_qc_cohort(ancestry="amr")` gets an immediate `ValueError` rather than a no-op QC chain wasting cluster-hours.
**Verification:** `python -m ast` passes; `tests/m3/test_aou_ld_panel_local.py` 6/6 non-skipped tests pass.

### WR-008: ld_panel resolver does not document pin/strict precedence

**Files modified:** `src/python/ld_panel.py`
**Commit:** 6d2e753 (subsumed by CR-001)
**Applied fix:** Added explicit "Precedence: pin > strict_aou_only > fallback walk" note to the resolver docstring as part of the CR-001 signature update. The four-combination pytest matrix requested by the reviewer was not added — that scaffolding is Info-level and out-of-scope this pass; the docstring is the load-bearing fix.

## Skipped Issues

### WR-005: `m3_aou_npz_arrives` rule has output without producing it

**File:** `src/snakemake/rules/m3_ingest_aou_ld.smk:262-299`
**Reason:** Architectural DAG-semantics change requires plan-level review. The reviewer's proposed refactor (localrule + sentinel file rather than rule-as-file-checker) would alter the dependency graph that just landed in m3-W3-T2 (commit caf57ef). The current rule already fails fast (`set -euo pipefail` + `exit 1` when .npz missing) — it does not loop or retry as the review claims. The `--rerun-triggers mtime` concern is real but a corner case; the architectural fix should be designed alongside the Wave 4 production dispatch policy, not retrofitted in a code-review pass.
**Original issue:** Rule declares `output: npz=...` but its shell block only `touch`es the file if it already exists, and `exit 1` otherwise — Snakemake anti-pattern. Confusing UX during Wave 4 production if .npz files re-fire on `--rerun-triggers mtime`.

### WR-006: liftover `_find_mappable` has off-by-one accounting on `walked`

**File:** `src/python/build_ld_region_manifest.py:140-151`
**Reason:** The current manifest is already built (Wave 0 complete per project state). Raising `max_step_bp` from 1Mb to 5Mb is a scientific-judgment change to liftover policy — the worst case under the current cap is graceful "failed liftover" status (not corruption), and the reviewer concedes "the `max_step_bp=1_000_000` cap mitigates this." Re-running Wave 0 with a wider cap would change the set of regions admitted to the manifest, which is a scientific-content decision (does Carter want to admit endpoints that walk through 1-5 Mb of unmappable centromeric territory?). Defer to Carter for the rigor-vs-coverage trade-off; not a code-review blocker.
**Original issue:** Walking step (1 kb) is small relative to centromeric gaps (~3 Mb); after 1 Mb the function gives up and flags the region as FAILED rather than recovering.

### WR-009: Snakefile m3 includes are unconditional but config block is gated

**File:** `Snakefile:118-122`
**Reason:** Architectural change to top-level Snakefile DAG composition. The m3 includes were intentionally landed unconditionally in m3-W3-T2 (commit caf57ef) so Track A finalization can pick up AFR_aou panels as they stage in (the resolver chain falls through to 1kg when AoU panels are missing — zero behavior change for Track A finalization, per the m3_convert_npz_rds.smk header). Adding an `enable_m3_aou_ld` gate would invert that design intent and disconnect the chain head from Track A workflows, which is a Carter-level decision tied to manuscript-freeze policy.
**Original issue:** Downstream user accidentally invoking `snakemake .aou_export_complete.AFR.16` on a fresh clone would hit the WR-004 cascade. (WR-004 itself is now fixed via WorkflowError, mitigating the worst-case UX.)

---

_Fixed: 2026-05-01_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
