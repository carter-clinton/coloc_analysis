---
phase: quick-260611-tbw
plan: 01
subsystem: aou-ld-pipeline
tags: [aou, ld, notebook, bucket-prefix, regression]
requirements: [GAP-C3]
requires:
  - "src/python/aou_ld_panel.py::_normalize_bucket (existing helper, lines 405-433)"
provides:
  - "AOU-2 per-region LD notebook with normalized WORKSPACE_BUCKET in cells 3/4/6 (single gs:// prefix)"
  - "_normalize_bucket AOU-2 production-value single-prefix regression guard"
affects:
  - ".planning/notebooks/AOU-2_per_region_ld.ipynb"
  - "tests/m3/test_aou_ld_panel_local.py"
tech-stack:
  added: []
  patterns:
    - "Reuse aou_ld_panel._normalize_bucket at every WORKSPACE_BUCKET URI-builder boundary (mirrors CLI pattern at aou_ld_panel.py:2474)"
key-files:
  created: []
  modified:
    - ".planning/notebooks/AOU-2_per_region_ld.ipynb"
    - "tests/m3/test_aou_ld_panel_local.py"
decisions:
  - "Surgical raw-JSON edit (mutate only the 3 cells' source lists, re-dump indent=1) instead of nbformat.read/write — nbformat.write churns the whole file (adds id fields, reorders keys, re-splits markdown), violating the nbformat-preserving constraint"
metrics:
  duration: ~6m
  tasks: 2
  files: 2
  completed: 2026-06-11
---

# Phase quick-260611-tbw: Fix AOU-2 WORKSPACE_BUCKET Double-Prefix Summary

Closed gap C3: AOU-2 cells 3/4/6 now normalize the gs://-prefixed `$WORKSPACE_BUCKET` via the shared `_normalize_bucket` helper, so cohort-read and LD-output URIs prepend `gs://` exactly once instead of producing malformed `gs://gs://.../ld/...` paths on the first Wave 2 fire.

## What Was Done

**Task 1 — Normalize WORKSPACE_BUCKET in AOU-2 cells 3/4/6** (commit `7e29cd4`)
- Cell 3: extended the import to include `_normalize_bucket`; added one line after `init_hail()` binding `WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])` with a gap-C3 explanatory comment.
- Cell 4: both `read_final_cohort_mt(...)` calls now read from `f"gs://{WB}/ld/mt_afr_qc.mt"` / `...mt_eur_qc.mt"`.
- Cell 6: `OUT_BUCKET_AFR` / `OUT_BUCKET_EUR` now built from `f"gs://{WB}/ld/AFR_aou"` / `EUR_aou`.
- nbformat-preserving: only the `source` of the 3 target cells changed; no `execution_count`/`outputs`/other-cell churn (7 insertions / 7 deletions total).
- Notebook NOT executed (VPC-SC walls AoU data ops from this HPC node — by design).

**Task 2 — Confirm/extend `_normalize_bucket` regression coverage** (commit `c1c7735`)
- The 5 pre-existing `_normalize_bucket` tests (strips_prefix, keeps_bare, strips_trailing_slash, idempotent, handles_malformed_extra_slash) already cover the requested assertions — NOT duplicated.
- Added one AOU-2-specific guard, `test_normalize_bucket_aou2_production_value_single_prefix`, asserting the exact production bucket `gs://rw-migration-aou-rw-476cdac2` normalizes and re-prefixes to a single `gs://`.
- Suite run: `6 passed, 124 deselected` under the project python.

## Verification

- `nbformat.validate` passes; import extended, `WB` bound, 4 `gs://{WB}/ld/` f-strings present, zero remaining `gs://{os.environ[...]}` double-prefix f-strings.
- `pytest tests/m3/test_aou_ld_panel_local.py -k normalize_bucket -v` → 6 passed.
- Git staging used explicit paths only (no `git add -A`).

## Deviations from Plan

None functionally. One implementation-detail adjustment: the plan suggested `nbformat.read(..., as_version=4)` / `nbformat.write`, but `nbformat.write` re-serializes the entire notebook (injects `id` fields on every cell, reorders metadata/execution_count keys, re-splits a markdown cell's `\n\n`), which violated the "only touch the source of the 3 target cells" constraint. Switched to a surgical raw-JSON edit (verified byte-identical round-trip with `json.dumps(indent=1)` before applying), yielding a 7-line minimal diff. This is a Rule 3 blocking-issue resolution (the prescribed tool would have failed the nbformat-preserving constraint), not a scope change.

One cosmetic note in cell 3: the original `source` list split `print(...to_string(index=False))` (no trailing `\n`) from the following comment line as separate list elements; `"".join(source)` made them one logical line, so re-splitting with `splitlines(keepends=True)` rejoined them on one physical line. The executable Python (`"".join(source)`) is byte-identical to before — no behavior change.

## Self-Check: PASSED
- FOUND: .planning/notebooks/AOU-2_per_region_ld.ipynb
- FOUND: tests/m3/test_aou_ld_panel_local.py
- FOUND commit 7e29cd4
- FOUND commit c1c7735
