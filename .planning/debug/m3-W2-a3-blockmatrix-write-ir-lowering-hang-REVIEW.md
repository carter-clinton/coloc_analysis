---
phase: m3-W2-a3-blockmatrix-write-ir-lowering-hang
reviewed: 2026-06-11T00:00:00Z
depth: deep
files_reviewed: 4
files_reviewed_list:
  - src/python/aou_ld_panel.py
  - tests/m3/test_aou_ld_panel_local.py
  - scripts/a3_blockmatrix_lowering_repro.py
  - .planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
---

# Code Review: A.3 BlockMatrixIR-lowering fix (commit 125b353)

**Reviewed:** 2026-06-11
**Depth:** deep / static analysis against Hail 0.2.135 semantics + project invariants
**Files Reviewed:** 4
**Status:** issues_found

## Summary

The core decomposition is **correct**. Replacing `hl.ld_matrix(...).write()` with
`row_correlation -> checkpoint -> locus_windows -> sparsify_row_intervals(blocks_only=False) -> write`
faithfully reproduces `ld_matrix`'s documented internals: in Hail 0.2.135 `ld_matrix(entry, locus, radius)`
**is** `row_correlation(entry).sparsify_row_intervals(*locus_windows(locus, radius))`. Same Pearson-r
standardization (mean-impute within variant, center, unit-normalize, Gram), same bp→row-index band, same
`blocks_only=False`, same coord handling (no `coord_expr` on either side → bp window). There is **no numerical
drift and no band off-by-one** — the new path calls the identical primitives with identical arguments. The
checkpoint genuinely breaks the fused IR, which is the right mechanism. The MED-4 guard, CR-003 sidecars, and
A.1/A.2 branches are behaviorally unchanged.

**However, there is one CRITICAL scaling defect that the fix's own design record gets wrong** and that turns a
60-min hang into a multi-hundred-GB-to-TB scratch write on the biggest production regions. The fix checkpoints
the FULL DENSE n×n correlation matrix BEFORE banding. The debug record claims the scratch is "radius-banded,
not the full O(n^2) dense" (fix block, lines 130-134) — **this is factually incorrect for the code as written.**
This does not block the *dev-10 cluster repro* (small synthetic n), but it means a green repro will NOT prove
the fix survives the largest production (GATE 3) regions. The repro should be taken to the cluster, but with the
CRITICAL finding understood and a follow-up sizing decision made before GATE 3.

**Overall verdict: SOUND to take to the cluster repro for the dev-10 lowering proof + parity check.
NOT yet sound for the full 322-cell GATE 3 production until CR-01 (full-dense scratch) is addressed.**

## Critical Issues

### CR-01: Checkpointed scratch is the FULL DENSE n×n correlation matrix, not banded — ~2 TB on the largest production region

**File:** `src/python/aou_ld_panel.py:2467-2470`
**Confidence:** HIGH (static + arithmetic; the code order is unambiguous)

The helper checkpoints `corr_bm` **before** applying the band:

```python
corr_bm = hl.row_correlation(mt_r.GT.n_alt_alleles())   # FULL DENSE n x n
corr_bm = corr_bm.checkpoint(scratch_uri, overwrite=True) # <-- materializes the DENSE matrix
starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)
banded = corr_bm.sparsify_row_intervals(starts, stops, blocks_only=False)  # band applied AFTER checkpoint
```

`row_correlation` returns the **complete** n×n Gram matrix (every block dense). The radius banding only
happens at step 4, which reads the already-materialized dense scratch. So the scratch BM written to bucket is
the unbanded dense float32 matrix.

The debug record's tradeoff justification is therefore wrong:
> "For a banded region that is bounded (radius-banded, not the full O(n^2) dense), and it is written by the
> SCALABLE native writer" (fix block, ~line 130)

The scratch is NOT banded — it is exactly the O(n²) dense object the whole A.3 path exists to avoid densifying.

**Quantified worst case (production manifest `config/ld_regions.tsv`):**
- region_00006 (the dev-10 failure): span 17.7 Mb, n_var=122,678 → 122,678² × 4 B ≈ **60.2 GB** dense scratch.
- AFR density ≈ 122,678 / 17.7 Mb ≈ 6,930 variants/Mb.
- Largest production region **m2_region_00145 (AFR)** = **102.5 Mb span** → ≈ 710,000 variants →
  710,000² × 4 B ≈ **~2.0 TB** dense scratch for a single region.
- m2_region_00120 (101.7 Mb) and m2_region_00040 (88.8 Mb) are comparable (~1.9 TB, ~1.5 TB).
- Even discounting the 50-Mb radius cap (which limits the FINAL `.bm` band, NOT the dense scratch — the band
  is applied after the checkpoint), the dense scratch scales with n_var², and n_var is set by the full region
  span, not the radius.

**Why this still passes the cluster repro:** the repro uses `--n-var 400`, where dense 400² × 4 B = 640 KB.
The scratch-size defect is invisible at synthetic scale. A green repro proves the *lowering* is fixed; it does
NOT prove the largest A.3 regions are tractable.

**Risks at production scale:** (a) `row_correlation`'s Gram-matrix compute is itself O(n²) executor work and
the dense materialization may OOM/run very long on a ~710k-variant region; (b) ~2 TB of scratch per region ×
36 large/xlarge regions (written then deleted) is real bucket I/O cost and time; (c) the dense `corr_bm` write
re-introduces a large distributed write — the native writer scales better than the interpreted one, but 2 TB is
still a heavy stage.

**Fix (preferred — band before checkpoint):** apply `sparsify_row_intervals` to the lazy `row_correlation`
result FIRST, then checkpoint the banded matrix, then write. The checkpoint still breaks the fused IR (the
sparsify+correlation fusion is materialized once), but the materialized scratch is the banded matrix, which at a
50-Mb cap is dramatically smaller than dense for the xlarge regions:

```python
corr_bm = hl.row_correlation(mt_r.GT.n_alt_alleles())
starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)
banded = corr_bm.sparsify_row_intervals(starts, stops, blocks_only=False)
banded = banded.checkpoint(scratch_uri, overwrite=True)   # materialize the BANDED matrix
banded.write(bm_uri, overwrite=True, stage_locally=stage_locally)
```

CAVEAT requiring cluster verification: it must be confirmed that checkpointing the
`row_correlation -> sparsify_row_intervals` composition still breaks the fused IR (i.e. that the lowering
warning is ABSENT when the checkpoint sits after the sparsify). The hypothesis is that the warning is triggered
by writing the fused IR, and ANY checkpoint that forces materialization breaks it — band-then-checkpoint should
work and is the canonical pattern. The repro script should be extended to test this ordering on the cluster
BEFORE committing to it. If band-then-checkpoint somehow re-fuses, the alternative is a size guard
(see WR-02) plus keeping dense-then-checkpoint only for regions small enough to tolerate the dense scratch.

**Minimum acceptable action before GATE 3:** either land band-before-checkpoint (verified on the cluster) OR
add an explicit n_var/scratch-size guard + log (WR-02). Do NOT run the full 322-cell production with the current
dense-scratch ordering unverified on a ~700k-variant region.

## Warnings

### WR-01: Repro script cannot detect the CR-01 dense-scratch problem — add a scratch-size assertion

**File:** `scripts/a3_blockmatrix_lowering_repro.py:192-206`
**Confidence:** HIGH

The repro proves (a) lowering warning PRESENT(old)/ABSENT(new), (b) valid `.bm` shape + `_SUCCESS`,
(c) r-parity — all correct and useful. But it runs only at n=400, so it gives a false sense of production
readiness: it cannot surface CR-01. Recommend adding, after the NEW write, a probe of the scratch BM size and an
explicit print of the dense-scratch footprint that WOULD be written at production n_var (e.g.
`710000**2 * 4 / 1e12` TB), so the operator sees the extrapolation. Better: add a `--band-before-checkpoint`
flag that exercises the proposed CR-01 fix ordering and re-checks the lowering warning is still ABSENT — that is
the missing cluster proof for the real fix. As written, a green repro would let the still-unscalable
dense-scratch ordering pass to GATE 3.

### WR-02: No size guard / observability log on the A.3 dense materialization

**File:** `src/python/aou_ld_panel.py:2436-2483`
**Confidence:** MEDIUM

Even if band-before-checkpoint (CR-01 fix) is adopted, the helper writes a potentially huge intermediate with
zero logging of its expected size. The pipeline already has the HIGH-1 OOM-veto observability print for routing
(line 2263-2266); A.3 materialization deserves the same. Add a log line in `_write_a3_banded_correlation_bm`
reporting n_var and the estimated dense (n_var²×4) and/or banded footprint, and consider a hard guard that
raises with a clear message if the projected dense scratch exceeds a threshold (e.g. > a few hundred GB) so the
biggest regions surface for review rather than silently writing TBs. This matches the project's "fail loud,
surface for review" discipline (cf. MED-5 sidecar fail-loud, the radius-cap invariant test).

### WR-03: `_a3_scratch_uri` fallback nests scratch under non-`.bm` URIs without a separator

**File:** `src/python/aou_ld_panel.py:2431-2433`
**Confidence:** LOW (defensive only; production URIs always end in `.bm`)

For a `bm_uri` that does NOT end in `.bm` (e.g. `gs://bkt/ld/bm/region_x`), the helper returns
`region_x.corr_scratch.bm`. That is path-isolated (distinct leaf, the test pins it), which is fine. But note the
final `.bm` write goes to `region_x` (no suffix) while scratch goes to `region_x.corr_scratch.bm` — these are
siblings, not nested, so no clobber. The only latent risk: if a future caller passed a `bm_uri` that is itself a
directory prefix containing other regions, the `.corr_scratch.bm` leaf could collide. Not reachable from current
call sites (both pass `.../bm/{rid}.bm`), so LOW. No change required; flagging for awareness.

### WR-04: Scratch cleanup swallows ALL exceptions including the wrong-backend case

**File:** `src/python/aou_ld_panel.py:2480-2483`
**Confidence:** LOW

`hl.current_backend().fs.rmtree(scratch_uri)` in a bare `except Exception` is correct as best-effort cleanup,
and the survival-is-harmless reasoning holds (overwrite=True on re-fire, path-isolated). The only downside: a
persistent cleanup failure leaks one dense-scratch BM per region (≈ up to ~2 TB each under CR-01) until a manual
sweep. If CR-01 is NOT fixed before GATE 3, these orphaned dense scratches across 36 regions could accumulate
significant bucket cost if cleanup repeatedly fails (e.g. a transient FS error). Once CR-01 (band-before-
checkpoint) lands, the leaked footprint shrinks to the banded size and this is genuinely negligible. Consider
logging the leaked URI at WARN (it currently prints, which is adequate) and noting it in the run log so a
post-run sweep can target it.

## Info

### IN-01: A.3 still computes the unused lazy `ld_bm = hl.ld_matrix(...)` (line 2214) — harmless but confusing

**File:** `src/python/aou_ld_panel.py:2214-2218`
**Confidence:** HIGH

`ld_bm = hl.ld_matrix(...)` is built unconditionally at line 2214 and consumed only by the A.1/A.2 branches.
For an A.3 region it is never `.write()`/`.to_numpy()`'d, so it stays a lazy IR and triggers no compute (Hail
BlockMatrix construction is lazy) — genuinely harmless, no double-compute, no re-introduction of the fused-IR
hang (the hang requires `.write()`/materialization of the fused IR, which A.3 no longer does). But it is
confusing to a reader scanning the A.3 branch (the very object the fix avoids is still in scope). Optional:
guard the `ld_bm = hl.ld_matrix(...)` construction behind `if path_a in ("A.1", "A.2")`, or add a one-line
comment at the A.3 branch noting `ld_bm` is intentionally unused there. Not load-bearing; leave if you prefer
minimal diff.

### IN-02: `stage_locally=True` is a sound default; document it survives the scratch write too

**File:** `src/python/aou_ld_panel.py:2437, 2478`
**Confidence:** MEDIUM

`stage_locally=True` on the final `banded.write` is reasonable per Hail BlockMatrix docs (reduces the
distributed-write shuffle). Note it is applied to the FINAL write only; the scratch `checkpoint` uses Hail's
default staging. If CR-01's dense-scratch write becomes the dominant cost, consider whether the checkpoint write
also benefits from local staging (checkpoint does not expose `stage_locally`, so this is informational). No
action needed.

### IN-03: Regression confirmation — A.1/A.2, MED-4 guard, CR-003 sidecars UNCHANGED

**File:** `src/python/aou_ld_panel.py:2268-2276, 2300-2346, 2383-2407`
**Confidence:** HIGH

Verified behaviorally identical to pre-125b353:
- **A.1** (line 2269): `ld_bm.to_numpy().astype("float32")` + `_save_npz` — untouched.
- **A.2** (line 2271-2276): `ld_bm.sparsify_triangle(lower=True).to_numpy()` + `_save_npz(lower_triangular=True)`
  — untouched.
- **`_route_region_path`** (line 325-353): byte-identical; the OOM-veto routing test still applies.
- **MED-4 `_assert_blockmatrix_written`** (line 2383): unchanged; still re-reads shape `(n_var, n_var)` and
  raises on read failure/mismatch — correctly preserved as the "_SUCCESS is not data" guard for A.3, and it now
  validates the FINAL banded `.bm` (not the scratch), which is the right object to validate.
- **CR-003 sidecars** (local 2303-2312, bucket 2328-2346): variant_ids/rsids emission + MED-5 fail-loud upload
  RuntimeError unchanged. Row-order alignment (the single-`aggregate_rows` CR-002 fix, line 2229) is preserved
  and remains consistent with the new path: `row_correlation(mt_r...)` and `locus_windows(mt_r.locus)` both
  index off the SAME `mt_r` row ordering as the sidecar `aggregate_rows`, so the 1:1 variant alignment the
  `.npz`/`.bm` consumers assume still holds. The IR-003 `len == n_var` asserts (line 2252-2257) still gate it.

## Hail 0.2.135 semantic verification (for the record)

- **Standardization parity:** `hl.ld_matrix(entry, locus, radius)` is documented and implemented as
  `row_correlation(entry).sparsify_row_intervals(*locus_windows(locus, radius))`. Calling `row_correlation`
  directly is therefore EXACTLY ld_matrix's standardization (within-variant mean-imputation of missing GT,
  centering, unit-normalization, then Gram → Pearson r). No hand-rolled covariance, no drift. ✓
- **Band parity:** both old and new paths call `locus_windows(locus, radius)` with NO `coord_expr` → identical
  bp-position windows → identical half-open `[starts[i], stops[i])` row intervals → identical band. No
  off-by-one (same primitive, same args). ✓
- **`blocks_only=False`** matches ld_matrix's default → exact in-band r values (correct for SuSiE-RSS). ✓
- **Checkpoint breaks the fusion:** `BlockMatrix.checkpoint` materializes via the native distributed writer and
  returns a read-backed BM, so the subsequent write IR is `read(checkpoint) + sparsify` — small, lowers
  natively. Mechanism is sound. The ONLY structural caveat is CR-01: the checkpoint is placed on the DENSE
  correlation, not the banded one.

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep (static analysis; Hail not runtime-testable on NCSU HPC node)_
