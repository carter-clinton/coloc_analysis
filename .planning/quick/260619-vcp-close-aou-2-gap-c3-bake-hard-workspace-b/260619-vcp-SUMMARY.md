---
phase: quick-260619-vcp
plan: 01
subsystem: m3-aou-ld-panel-build
tags: [aou, dataproc, hail, notebook, env-guards, workspace-bucket, nbformat, tdd]
requires:
  - "feedback_aou_cluster_template_bucket_pollution (WORKSPACE_BUCKET 404 placeholder)"
  - "AOU-1 Cell 1a'' HARD-override precedent (quick 260606-qc1, commit 29d0a1f)"
provides:
  - "AOU-2_per_region_ld.ipynb self-pins WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 BEFORE the bucket is read — a fresh AoU clone no longer writes LD outputs to the cloned-mybucket 404 placeholder"
  - "In-kernel cloned-mybucket assert that hard-fails a still-polluted bind (lost-writes catastrophe guard)"
  - "RED-first notebook-loading guard test pinning the hard-assign literal, not-setdefault contract, pin-before-read ordering, and the placeholder assert"
affects:
  - ".planning/notebooks/AOU-2_per_region_ld.ipynb"
  - "tests/m3/test_aou_ld_panel_local.py"
tech-stack:
  added: []
  patterns:
    - "Edit .ipynb via one-off plain json module (NOT nbformat.write — preserves existing cells byte-for-byte; nbformat.write churns the whole file via the Workbench clean/smudge filter)"
    - "New nbformat-4.5 cell gets a fresh uuid.uuid4().hex[:8] id + metadata:{}; pre-existing id-less cells left untouched (NCSU tree has no server-side clean/smudge filter — no re-dirty)"
key-files:
  created: []
  modified:
    - ".planning/notebooks/AOU-2_per_region_ld.ipynb"
    - "tests/m3/test_aou_ld_panel_local.py"
decisions:
  - "Reworded ONE comment line in the pin cell so it does NOT reproduce the exact literal _normalize_bucket(os.environ[\"WORKSPACE_BUCKET\"]) — the planner's verbatim comment collided with the guard test's read-cell detection substring, making reads[0] match the pin cell itself (pin_idx==read_idx). Rule 1 fix; semantics preserved, contract intact."
  - "Left the 14 pre-existing id-less cells id-less (unlike 260606-qc1's id backfill) — the NCSU GPFS tree has no clean/smudge filter, the git diff is a clean pure-insertion, and a no-op id backfill would needlessly churn the 14 unrelated cells."
metrics:
  duration: ~10m
  completed: 2026-06-19
  tasks: 3
  files: 2
---

# Phase quick-260619-vcp Plan 01: Close AOU-2 gap C3 — bake HARD WORKSPACE_BUCKET pin Summary

Closed the last open gap-C3 row (SKILL.md "Baked-vs-manual edit table"): baked a HARD `os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"` override into `.planning/notebooks/AOU-2_per_region_ld.ipynb` as a new pin cell positioned BEFORE the `WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"])` read, so a fresh AoU clone self-pins the canonical bucket rather than the dead `gs://cloned-mybucket-<project>` 404 placeholder a saved/duplicated Dataproc template injects — every Cell [8] LD `.npz`/`.bm` write and Cell [6] MT read now resolves to the live bucket, with an in-kernel `cloned-mybucket` assert that hard-fails a still-polluted bind (the lost-writes / empty-output catastrophe class). Pinned by a RED-first guard test.

## What Was Done

- **Task 1 (RED, commit `88fa55d`):** Appended `test_aou2_workspace_bucket_hard_pin` to `tests/m3/test_aou_ld_panel_local.py` (after `test_normalize_bucket_aou2_production_value_single_prefix`). It loads the AOU-2 notebook via plain `json` (PROJECT_ROOT-relative; no nbformat dep), then asserts (a) the EXACT hard-assign literal is present in some code cell, (a') the pin cell is NOT a `.setdefault(` CALL, (b) the pin cell index is STRICTLY less than the `_normalize_bucket(os.environ[...])` read-cell index (pin-before-read), and (c) the pin cell contains the `cloned-mybucket` placeholder assert. Confirmed FAILING (RED) against the un-edited 14-cell notebook — failure on `pins == []` (no hard-assign).
- **Task 2 (GREEN, commit `c3a3292`):** Inserted ONE new code cell at index 5 (after the index-4 Q-RS2 `PYSPARK_SUBMIT_ARGS` config, before the index-5 `_normalize_bucket` read cell, which shifts to index 6) via a one-off plain-`json` script (NOT nbformat.write). The cell is AOU-2-scoped — bucket ONLY, NO `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` (AOU-2 reads MTs, not the WGS multiMT). Cell carries a fresh 8-hex id (`90109046`), `metadata: {}`, `execution_count: null`, `outputs: []`, and source split on newlines with the nbformat trailing-`\n` convention. Guard test now PASSES (GREEN).
- **Task 3 (regression + commit discipline):** Ran the FULL `tests/m3` suite — 0 failures, new test among the passes. Both files committed to `m3-W2-aou-deltas` via explicit-path `git add` (each in its own RED/GREEN commit); no `git add -A`/`.`; no pre-existing clutter staged.

## Cell-count + byte-identity verification (requested)

- **New cell count: 15** (was 14). New pin cell at index 5; the `_normalize_bucket` read cell shifted to index 6 → pin-before-read holds (`5 < 6`).
- **14 original cells byte-identical to HEAD: CONFIRMED.** Programmatic check against `git show HEAD:.planning/notebooks/AOU-2_per_region_ld.ipynb` (new cells minus index 5, in order) — `source`, `metadata`, `outputs`, `execution_count`, `cell_type`, and `id` all identical for every one of the 14 originals (the originals were and remain id-less).
- `git diff` is a clean pure-insertion: 25 lines added, 0 removed. Working tree shows the two edited files committed clean (no clean/smudge re-dirty on the NCSU tree).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reworded a pin-cell comment line to avoid a guard-test substring collision**
- **Found during:** Task 2 verification — the first GREEN run still FAILED on `pin_idx < read_idx` (`5 < 5`).
- **Issue:** The planner's verbatim pin-cell comment included the line `# AOU-2's next cell reads WB = _normalize_bucket(os.environ["WORKSPACE_BUCKET"]);`, which reproduces the EXACT literal the guard test uses to detect the read cell. So `reads[0]` matched the pin cell itself (index 5) instead of the real read cell (index 6) → `pin_idx == read_idx`, falsely failing the pin-before-read assertion.
- **Fix:** Reworded that one comment line to `# AOU-2's next cell normalizes the bucket out of os.environ;` — semantics preserved, no longer reproduces the detection substring. All other pin-cell lines (hard-assign, print, `cloned-mybucket` assert, the `feedback_aou_cluster_template_bucket_pollution` reference, the "setdefault is UNSAFE" rationale, the AOU-1 Cell 1a'' mirror note) are verbatim per the plan.
- **Files modified:** `.planning/notebooks/AOU-2_per_region_ld.ipynb`
- **Commit:** `c3a3292`

**2. [Plan-internal decision] Left the 14 pre-existing id-less cells id-less (no backfill)**
- **Context:** 260606-qc1 had to backfill ids on AOU-1's id-less cells to stop the Workbench clean/smudge filter re-dirtying them. The plan said to backfill ONLY IF the post-write working-tree check showed a re-dirty.
- **Resolution:** No re-dirty occurred — the NCSU GPFS tree has no server-side clean/smudge filter (that filter is Workbench-side only). The `git diff` is a clean pure-insertion and the 14 originals are byte-identical. Backfilling ids would have needlessly churned 14 unrelated cells, so it was correctly NOT done.

## Test counts

- **Targeted:** `pytest tests/m3/test_aou_ld_panel_local.py::test_aou2_workspace_bucket_hard_pin` — FAILED (RED) before the notebook edit; PASSED (GREEN, 1 passed in 0.03s) after.
- **Full suite:** `pytest tests/m3 -q` → **205 passed, 0 failed, 30 skipped** (414.25s). Exactly +1 over the 204/0/30 baseline (the new test); no regression.

## Notebook NOT executed

Per VPC-SC / NCSU constraint, the notebook was NOT run — this is a static raw-JSON content edit only (the `cloned-mybucket` assert needs a live AoU kernel to exercise).

## Orchestrator follow-ups (NOT done by executor, per plan)

- **Push** `m3-W2-aou-deltas` to origin (`github.com/carter-clinton/coloc_analysis`) so the AoU Workbench `git clone` target picks up the baked pin. The default branch is already `m3-W2-aou-deltas`, so a fresh clone lands on the working line with the new cell.
- **Update SKILL.md** "Baked-vs-manual edit table" gap-C3 row for AOU-2 from `GAP (manual) ⚠️` to `BAKED` + commit sha `c3a3292`. (Step 7 of the fresh-clone re-run checklist — "AOU-2 does NOT pin it itself (gap C3)" — should also be updated to reflect that it now self-pins.)

## Commits

- `88fa55d` — `test(260619-vcp): RED — AOU-2 gap-C3 WORKSPACE_BUCKET hard-pin guard`
- `c3a3292` — `feat(260619-vcp): GREEN — bake AOU-2 gap-C3 WORKSPACE_BUCKET hard pin`

## Self-Check: PASSED

- FOUND: `.planning/notebooks/AOU-2_per_region_ld.ipynb` (modified, committed `c3a3292`)
- FOUND: `tests/m3/test_aou_ld_panel_local.py` (modified, committed `88fa55d`)
- FOUND commit: `88fa55d`
- FOUND commit: `c3a3292`
