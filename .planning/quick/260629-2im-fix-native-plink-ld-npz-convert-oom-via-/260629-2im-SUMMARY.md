---
phase: quick-260629-2im
plan: 01
subsystem: m3-02e native-plink LD panel (.npz convert/bank step)
tags: [ld, oom, plink, npz, m3-02e, m3-02e-T4]
requires: []
provides:
  - "_is_symmetric_blocked memory-bounded symmetry check in plink_ld_to_npz.py"
  - "read_square_bin OOM-safe at n_var~102,421 on a 64-128 GB VM"
affects:
  - src/python/plink_ld_to_npz.py
  - tests/m3/test_plink_ld_to_npz.py
tech-stack:
  added: []
  patterns:
    - "Blocked/streaming verification of a dense n_var**2 matrix (bound transient to block*n_var*4, never materialize a full-size temporary)"
    - "Reusable utility + failing-first regression for a recurrent bug class (feedback_extract_reusable_utilities)"
key-files:
  created: []
  modified:
    - src/python/plink_ld_to_npz.py
    - tests/m3/test_plink_ld_to_npz.py
decisions:
  - "Fix the symmetry check (the actual OOM source), NOT np.savez_compressed (numpy writes in chunks; it was never the killer)"
  - "Keep the ValueError message byte-identical; the invariant is still ENFORCED in bounded blocks, not skipped"
  - "Carter: also respec the AoU VM to n2-highmem-16 (128 GB) for headroom on any region >~115k variants (the bare dense array scales n_var**2 regardless of the fix)"
metrics:
  tasks: 2
  files: 2
  duration: "~40 min (incl. 35m45s full-suite run)"
  completed: 2026-06-29
---

# Phase quick-260629-2im Plan 01: Fix native-plink LD .npz convert OOM Summary

Memory-bounded the square-LD symmetry check in `read_square_bin` so the
native-plink `.npz` convert/bank step no longer OOM-kills at n_var≈102,421,
unblocking the 276-region AFR LD panel re-fire (m3-02e-T4).

## Root Cause

The OOM was the **full-matrix symmetry check**, NOT `np.savez_compressed`.

In `read_square_bin()`, `np.allclose(m, m.T, atol=1e-4)` (line 156) materializes
several full `n_var**2` float32 temporaries — `m - m.T`, `abs(...)`,
`atol + rtol*abs(b)`, the bool mask — each ~39 GiB at n_var=102,421, **on top of**
the 39 GiB matrix `m` already in memory. Peak blew past 64 GiB → kernel OOM-kill
(`anon-rss ~61 GiB`); region 1 banked **0/276**.

- `np.savez_compressed` is **not** the killer (numpy streams the array into the zip
  in chunks).
- The diagonal check `np.allclose(np.diag(m), 1.0, ...)` is tiny (n_var elements) and
  was always fine.

This is the same dense-collect OOM class the Hail path already guarded against
(`_max_safe_to_numpy_n_var` / `_dense_footprint_bytes`); the native-plink converter
never got that guard. It is the third format/memory bug in this loop (after the
triangle-flag and chr-prefix bugs), so per `[[feedback_extract_reusable_utilities]]`
the fix is a reusable utility with a failing-first regression.

## The Fix

`src/python/plink_ld_to_npz.py` — added a module-level helper and swapped the predicate:

```python
def _is_symmetric_blocked(m: np.ndarray, atol: float, block: int = 1024) -> bool:
    n = m.shape[0]
    for i in range(0, n, block):
        a = m[i:i + block, :]          # row block (view, b×n)
        b = m[:, i:i + block].T        # transposed col block (b×n)
        if not np.allclose(a, b, atol=atol):
            return False
    return True
```

`read_square_bin` line 156 now calls `if not _is_symmetric_blocked(m, atol=1e-4):`.
The transient is bounded by `block * n_var * 4` bytes (~420 MB at block=1024,
n_var≈1e5). Peak for region 1 after the fix: ~39 GiB (matrix) + ~0.4 GiB (one
block's allclose temporaries) + overhead ≈ ~45 GiB.

**Invariant preserved, not skipped:** the `ValueError` message is byte-identical;
an asymmetric `.ld.bin` still raises (test below). The diagonal check (line 151) and
the `arr.reshape(...).astype("float32", copy=False)` no-copy view (line 150) are
unchanged.

**Commit:** `3eac803` — `fix(m3-02e): memory-bounded square-LD symmetry check (kills the .npz-convert OOM)`

## TDD (failing-first)

RED → GREEN, proven by reverting only the source fix:

- `test_is_symmetric_blocked_accepts_and_rejects` — symmetric passes; one-sided
  off-diagonal perturbation → False.
- `test_blocked_check_matches_allclose` — blocked verdict == `np.allclose(m, m.T)` for
  symmetric AND asymmetric inputs across edge cases (n=5/17/100, block>n via block=4096).
- `test_read_square_bin_rejects_asymmetric` — `read_square_bin` still raises `ValueError`
  on an asymmetric `.ld.bin` with a unit diagonal (invariant preserved).

Failing-first verification: with the source reverted (`git show HEAD~1:...` over the
file) the two helper tests fail with `AttributeError: module 'plink_ld_to_npz' has no
attribute '_is_symmetric_blocked'`; the preserved-invariant test still passes (it relies
on the old `np.allclose` predicate too). After restoring the fix, all pass.

## Test Results

**Task 1 — targeted gate** (`/rs1/.../smoke_dev/bin/python -m pytest tests/m3/test_plink_ld_to_npz.py -v`):

```
17 passed in 3.18s
```

(the 3 new tests + the existing `test_plink_square_bin_to_npz`,
`test_lower_triangular_flag_correct_per_mode`, `test_npz_keys_match_save_npz_contract`).

**Task 2 — full suite** (`/rs1/.../smoke_dev/bin/python -m pytest tests/m3 -q`):

```
302 passed, 30 skipped in 2145.10s (0:35:45)
```

Above the 287+ baseline; zero failures.

## Environment Used

- **Test runner:** `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python`
  (Python 3.11.15, numpy 2.4.4, pytest 9.0.3) — the `m3-r-ld` env is the R-side env and
  does not carry pytest/numpy on its python.
- **R/reticulate loader tests RAN, not skipped:** the m3 R-execution tests auto-discover
  the pinned `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript`
  (`[[reference_m3_r_ld_conda_env]]`) via their discovery cascade, so the full-suite count
  (302) includes them — this is why the run took ~36 min rather than seconds.
- **The 30 skips are pre-existing and unrelated** to this change: Hail-gated driver tests
  (`pytest.importorskip("hail")` — Hail not installed on the NCSU node), synthetic-MT
  builders, and chain-file fixtures. Not introduced here.

## Re-fire Procedure (for the AoU agent)

1. **Push first, verify origin tip == local HEAD** before any re-fire
   (`[[feedback_push_ncsu_before_aou_clone_fire]]`) — the AoU agent pulls the fix. The orchestrator
   owns the docs commit; the fix is `3eac803` on `m3-W2-aou-deltas`.
2. AoU agent `git pull` the fix commit on the VM.
3. **Respec to n2-highmem-16 (128 GB)** via the AoU UI: VM already STOPPED → edit machine type → start.
   The reattachable PD + 379 GB bfile are on disk and survive a machine-type change untouched.
4. **Pre-flight:** re-confirm region-1 chr1 window count ≈ 102,421 (the chr-prefix fix `a5a5f9f` is already proven).
5. **Re-fire the loop from region 1** (0 banked → clean restart; the MED-6 byte-floor resume guard skips nothing).
6. **Proof point:** region 1 completes → `.npz` count 0→1 in
   `gs://rw-migration-aou-rw-476cdac2/ld/afr_native_panel/*.npz`; `df` flat (the `.ld.bin` is
   reclaimed); panel row `status==ok`, `n_var≈102,421`; peak RSS well under 128 GB; no OOM in `dmesg`.
7. **Liveness = bucket `.npz` count climbing toward 276.** STOP-on-complete (stop ≠ delete) holds —
   at 276 the VM is STOPPED, not deleted (VM + PD + local bfile preserved; any delete is a separate Carter action).

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed; the symmetry-check fix and
failing-first regression match the approved design verbatim.

## Self-Check: PASSED

- `src/python/plink_ld_to_npz.py` — FOUND, contains `_is_symmetric_blocked` (line 136) and
  `read_square_bin` calls it (line 171); ValueError message unchanged.
- `tests/m3/test_plink_ld_to_npz.py` — FOUND, contains the 3 new tests.
- Commit `3eac803` — FOUND in `git log`.
