---
phase: 260625-r6m
plan: 01
subsystem: m3-aou-afr-ld-panel
tags: [m3-02e, native-plink, ld-panel, resumable, idempotent, content-verify, egress]
requires:
  - aou_ld_panel._existing_region_npz (MED-6 byte-floor resume guard)
  - aou_ld_panel.build_plink_ld_command (--keep-allele-order hardcoded)
  - aou_ld_panel._read_manifest
  - plink_ld_to_npz.plink_ld_to_npz (.ld.bin/.ld.gz -> egress-clean .npz)
provides:
  - src/python/run_native_ld_panel.py (resumable native-plink LD loop driver, STEP 4)
  - run_native_ld_panel / process_region / content_verify_npz / append_panel_row / main
affects:
  - m3-02e-AFR-NATIVE-FIRE-BRIEF.md STEP 4 (re-pointed to the driver; 8-VM fan-out) + STEP 5 (inline verify is primary) + STEP 7 (merge 8 shard TSVs)
provides_added_followup:
  - "src/python/run_native_ld_panel.py: --num-shards/--shard-index static index-sharding + select_shard_region_ids (8-VM Spot fan-out)"
tech-stack:
  added: []
  patterns:
    - "Single subprocess seam (_run_plink) so tests monkeypatch exactly one function."
    - "Reuse the existing MED-6 resume guard (out_bucket=None keeps it hail-free) rather than a bare [ -f ] check."
    - "Per-region content verification (D-M3-10) returns (ok, reason); failures continue the loop, never abort."
    - "Resume-safe TSV append: header once, dedup by region_id."
    - "Static index-sharding (idx %% num_shards == shard_index) over the deterministic, un-re-sorted ancestry-filtered order: disjoint + exhaustive partition across 8 VMs without coordination; outputs + resume guard stay on the SHARED out-dir (sharding partitions WHICH regions, not where outputs land)."
    - "Durable gs:// destination (Dataproc bucket-first): compute into local scratch, content-verify, gsutil-cp the verified .npz/AF up; gs:// resume via gsutil stat + MED-6 floor (hail-free subprocess, NOT the hail hadoop branch); .bed/.bim/.fam never uploaded."
key-files:
  created:
    - src/python/run_native_ld_panel.py
    - tests/m3/test_run_native_ld_panel.py
  modified:
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
decisions:
  - "A corrupt square .ld.bin is rejected at conversion (plink_ld_to_npz's own square checks) -> status='error: ...', a non-ok failure that still continues the loop; the inline content_verify_npz gate is the second, redundant D-M3-10 guard for any .npz that passes conversion. The one-bad-region test accepts either non-ok status."
  - "content_verify_npz returns (ok, reason) instead of raising, so the loop records the per-region status and continues (DoS mitigation T-260625-r6m-05)."
  - "FOLLOW-UP: sharding partitions WHICH regions a VM computes (idx %% num_shards == shard_index) but NOT where outputs land — .npz outputs + the _existing_region_npz resume guard stay on the SHARED out-dir so resume is GLOBAL across the 8 VMs and the egress bundler sees all 276. Per-shard --panel-tsv (8 VMs cannot safely co-append one TSV on a shared FS); the 8 shard TSVs are merged (concat + dedup by region_id) at handback."
metrics:
  duration: ~70 min initial + ~60 min sharding follow-up + ~60 min gs:// follow-up (each incl. a ~41-48 min full-suite gate)
  completed: 2026-06-26
  tasks: 3 (initial) + 1 (sharding) + 1 (durable gs:// out-dir)
  files: 3
requirements: [REQ-AOU-LD-EGRESS, D-M3-10, MED-6, T-M3-02e-SIGN, D-02e-01]
---

# Phase 260625-r6m Plan 01: Resumable native-plink LD loop driver Summary

Built `src/python/run_native_ld_panel.py` — the turnkey, idempotent, content-verified
loop driver that turns m3-02e STEP 4 (previously hand-described bash) into a single
re-runnable script, the only thing that was blocking the billable STEP-4 AFR LD fire.

## What was built

- **`src/python/run_native_ld_panel.py`** (368 lines, hail-free at module scope).
  Exports `run_native_ld_panel`, `process_region`, `content_verify_npz`,
  `append_panel_row`, `main`. Per region it: skips-if-banked via the REUSED
  `aou_ld_panel._existing_region_npz` (MED-6 `_MIN_REGION_NPZ_BYTES` floor, called
  with `out_bucket=None` to stay on the hail-free local-dir branch); else issues
  plink ONLY through `aou_ld_panel.build_plink_ld_command` (so `--keep-allele-order`
  is always present and the argv is never hand-rolled); builds a window-subset `.bim`
  (so `load_bim` row order == the `.ld.bin` row order) and cross-checks the n_var
  derived from the `.ld.bin` size against the window `.bim` row count; converts via
  `plink_ld_to_npz.plink_ld_to_npz`; content-verifies inline (`content_verify_npz`,
  D-M3-10); and appends a resume-safe row to `m3-W2-native-plink-panel.tsv`. A bad
  region records a non-ok status and the loop CONTINUES.

- **`tests/m3/test_run_native_ld_panel.py`** (396 lines, 11 tests). plink mocked at
  the single `_run_plink` seam (writes a synthetic square `.ld.bin`, records argv).
  Coverage: no-module-scope-hail-import, resume-skip = zero plink work on a second
  run, MED-6 floor rejects a truncated `.npz` (not a bare `[ -f ]`), content-verify
  rejects non-symmetric / wrong-diagonal npz, one bad region does not abort the loop,
  panel TSV append resume-safe (one header, no dup rows, correct columns),
  `--keep-allele-order` on every issued argv + obtained via the helper (AST: not
  hand-rolled), AFR-only filtering, retired-Hail-path absence, no hardcoded abs paths.

- **`m3-02e-AFR-NATIVE-FIRE-BRIEF.md`** STEP 4 re-pointed to a single
  `python src/python/run_native_ld_panel.py` invocation (idempotent across Spot
  preemption); STEP 5 note marks the driver's inline verify as the primary D-M3-10
  gate (the standalone numpy check is now the spot re-check). STEP 0-3 and 6-7 are
  untouched (the production-VM re-measure gate stays a blocking pre-loop step).

## Threat register dispositions (all `mitigate` items satisfied)

- **T-260625-r6m-01** (truncated `.npz` from preemption): REUSED `_existing_region_npz`
  MED-6 floor; `test_skip_uses_existing_region_npz_not_bare_exists` proves a <256-byte
  file recomputes.
- **T-260625-r6m-02** (marker says done, contents wrong): `content_verify_npz`
  float32/square/diag/symmetry per region; status recorded in the panel TSV.
- **T-260625-r6m-03** (LD sign flip vs GWAS z): plink ONLY via `build_plink_ld_command`;
  `test_keep_allele_order_on_every_issued_command` + the AST not-hand-rolled guard.
- **T-260625-r6m-05** (one bad region aborts the loop): `process_region` try/except +
  `content_verify_npz` non-raising; `test_one_bad_region_does_not_abort_loop` proves
  a corrupt region 1 does not block a clean region 2.

## Follow-up: static index-sharding for the 8-VM Spot fan-out (commit cdc2103)

Carter chose to run the 276-region loop across **8 Spot VMs in parallel** rather than
a single VM. Without partitioning, 8 VMs iterating the same manifest in the same order
run in lockstep and duplicate ~8× the compute (the resume guard only skips
ALREADY-BANKED regions, not in-flight ones). Added static index-sharding:

- **`--num-shards N` (default 1) + `--shard-index I` (default 0, 0-based)** on `main`,
  validated `0 <= shard_index < num_shards` (loud `ValueError` via `_validate_shard`).
- After the AFR filter, in the **EXISTING deterministic row order (no re-sort** — all
  VMs must see the identical order so the partition is consistent), this VM processes
  filtered position `idx` ONLY when `idx % num_shards == shard_index`. `num_shards=1`
  (default) processes all 276 (single-VM behavior unchanged). New pure helper
  `select_shard_region_ids` previews a shard's partition without running plink.
- **Outputs + resume guard stay on the SHARED out-dir.** Sharding partitions WHICH
  regions a VM computes, NOT where outputs land — the `.npz` outputs AND the
  `_existing_region_npz` skip-check both point at the one shared out-dir, so the resume
  guard is GLOBAL across all 8 VMs (a region banked by any VM is skipped by all) and
  the egress bundler later sees all 276. The output path is NOT sharded.
- **Per-shard `--panel-tsv`** (already configurable; default the canonical
  `m3-W2-native-plink-panel.tsv`): each VM writes its own
  `...shard0.tsv`..`...shard7.tsv` because 8 VMs concurrently appending to ONE TSV on
  a shared filesystem would interleave/corrupt it; the resume-safe dedup-by-`region_id`
  is preserved WITHIN each file.
- **MERGE NOTE (out of scope here, documented for handback):** at STEP 7 the 8 shard
  TSVs are concatenated (keep one header) + deduped by `region_id` to reconstruct the
  single `m3-W2-native-plink-panel.tsv` cost basis (expect 276 rows, all `status==ok`).
  The fire brief STEP 7 now carries this merge step.
- Invariants intact: `--keep-allele-order` via `build_plink_ld_command`, inline
  `content_verify_npz` (D-M3-10), and the hail-free-at-module-scope guard all still pass.

**Sharding tests (5, RED-first):** `test_sharding_partitions_disjoint_and_exhaustive`
(8-way over 276: pairwise-disjoint, union==all 276, ~34/shard), `..._index_out_of_range_raises`,
`test_num_shards_one_processes_all_regions` (regression), `..._shards_share_resume_guard_across_distinct_panel_tsvs`
(two shards, SAME out-dir, DIFFERENT panel TSV, global resume guard), `..._sharding_args_in_main_signature`.

## Follow-up: durable gs:// out-dir (Dataproc bucket-first; commit 10aaa6f)

The 276-region loop will run on an AoU Dataproc cluster where local disk is ephemeral
(it dies with the cluster — [[feedback_aou_use_persistent_disk]]: bucket-first on
Dataproc). The driver previously wrote `.npz` to a LOCAL `--out-dir` only, so a cluster
recycle forfeited every banked region. Added durable `gs://` destination support:

- **`--out-dir` accepts a `gs://` bucket prefix OR a local path** (local behavior
  byte-identical when local; `test_local_out_dir_unchanged_no_gsutil` asserts a local
  run issues ZERO gsutil calls). `--out-dir`/`--panel-tsv` are no longer `type=Path`
  (Path would collapse `gs://` -> `gs:/`); a `gs://` URI is kept as a string.
- **gs:// per region:** compute plink + `plink_ld_to_npz` into a LOCAL `--scratch-dir`,
  content-verify (existing inline D-M3-10 gate), THEN `gsutil cp` the verified `.npz`
  (and its `.afreq` sidecar if present) to the bucket. The individual-level
  `.bed/.bim/.fam` are NEVER uploaded by the driver — only the aggregate `.npz`/AF cross
  into the bucket (REQ-AOU-LD-EGRESS; `test_gs_out_dir_uploads_verified_npz` asserts no
  `.bed/.bim/.fam` upload).
- **gs:// resume check consults the BUCKET, hail-free:** `_existing_region_npz_gs` runs
  `gsutil stat <region>.npz`, parses `Content-Length`, and skips only when
  `size >= _MIN_REGION_NPZ_BYTES` (same MED-6 floor). A short object OR any gsutil error
  -> recompute (safer than assuming a checkpoint). Does NOT use `_existing_region_npz`'s
  hail hadoop branch. (`test_gs_resume_skips_when_object_meets_floor`,
  `test_gs_resume_recomputes_when_object_short_or_stat_errors`.)
- **gs:// `--panel-tsv`:** mirrored locally in scratch (seeded from the bucket copy on
  first touch so dedup survives a recycle), appended, then `gsutil cp`'d up; resume-safe
  dedup-by-`region_id` preserved within the file (`test_gs_panel_tsv_uploaded`).
- **Hail-free invariant intact:** `gsutil` is a plain subprocess (sole seam
  `_run_gsutil`), NOT a hail import — `test_module_imports_without_hail` still passes and
  a clean-subprocess import confirms `hail not in sys.modules`. `--keep-allele-order` via
  `build_plink_ld_command`, inline `content_verify_npz`, and the disjoint sharding are
  all unchanged.
- New helpers: `_is_gs_uri`, `_gs_join`, `_run_gsutil` (sole gsutil seam),
  `_gsutil_object_size`, `_existing_region_npz_gs`, `_gsutil_upload`; refactored
  `append_panel_row` (local core `_append_panel_row_local` + gs:// mirror/upload) and
  `process_region` (compute-dir vs destination split). New `--scratch-dir` CLI arg.

**gs:// tests (6, RED-first; gsutil mocked, no real GCS):** upload-after-verify (+ no
`.bed`/`.bim`/`.fam` upload), resume skip when bucket object >= floor, recompute when
object < floor OR `gsutil stat` errors, panel-TSV upload, local-out-dir-untouched
regression, `_is_gs_uri` helper.

## Verification

- `pytest tests/m3/test_run_native_ld_panel.py` -> **11 passed** (initial) ->
  **16 passed** (sharding follow-up) -> **22 passed** (gs:// follow-up; 6 new tests).
- `pytest tests/m3` (full-suite gate, smoke_dev py3.11, R `m3-r-ld` env active):
  initial **282 passed, 30 skipped**; sharding follow-up **287 passed, 30 skipped**;
  gs:// follow-up **293 passed, 30 skipped, 0 failed** in 2431.89s (~41 min). No
  regression; the R stitch tests all ran and passed (the 3 PRE-EXISTING stitch failures
  previously tracked in STATE.md were the flaky reticulate cold-start class, already
  resolved at 80fbb9a — they did NOT recur).
- `grep run_native_ld_panel.py m3-02e-AFR-NATIVE-FIRE-BRIEF.md` -> STEP 4 re-pointed
  (8-VM fan-out + durable gs:// out-dir subsection).
- Pushed to origin: `origin/m3-W2-aou-deltas == local HEAD == 10aaa6f` (verified).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Test expectation] one-bad-region status widened to accept `error:`**
- **Found during:** Task 1 (`test_one_bad_region_does_not_abort_loop`).
- **Issue:** A corrupt square `.ld.bin` is rejected inside `plink_ld_to_npz`'s own
  square-matrix checks (same diag/symmetry invariants as `content_verify_npz`) BEFORE
  reaching the inline verify gate, so the status is `error: ...` rather than
  `verify_failed`. Both outcomes satisfy the must-have (region marked failed, loop
  continues, corrupt region not banked).
- **Fix:** Broadened the assertion to accept `verify_failed` OR an `error`-prefixed
  status, and added `assert not (out_dir/'regBAD.npz').is_file()` to prove the corrupt
  region was not banked. No production-code change.
- **Commit:** 35361e5

**2. [Rule 1 - Boundary guard] reworded the retired-path docstring**
- **Found during:** Task 2 (`test_driver_does_not_touch_retired_hail_path`).
- **Issue:** The driver's "does NOT touch the retired Hail path" docstring listed the
  retired symbol names verbatim, which tripped the substring-absence guard (the guard
  scans the whole source, mirroring the sibling test in test_plink_ld_to_npz.py).
- **Fix:** Reworded the docstring to describe the boundary without naming the retired
  symbols; the guarantee is unchanged and the test now passes.
- **Commit:** 1a1a361

## Self-Check: PASSED

- FOUND: src/python/run_native_ld_panel.py
- FOUND: tests/m3/test_run_native_ld_panel.py
- FOUND: .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md (STEP 4 8-VM fan-out + durable gs:// out-dir + STEP 7 merge)
- FOUND commit 35361e5 (Task 1)
- FOUND commit 1a1a361 (Task 2)
- FOUND commit cdc2103 (sharding follow-up)
- FOUND commit 10aaa6f (durable gs:// out-dir follow-up); pushed, origin == local HEAD
