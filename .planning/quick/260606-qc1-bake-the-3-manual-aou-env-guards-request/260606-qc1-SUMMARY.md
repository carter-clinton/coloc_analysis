---
phase: quick-260606-qc1
plan: 01
subsystem: m3-aou-cohort-build
tags: [aou, dataproc, hail, notebook, env-guards, requester-pays, nbformat]
requires:
  - "Gate-C-proven Cell 1a requester-pays pattern (chr22-smoke template)"
  - "feedback_aou_cluster_template_bucket_pollution (WORKSPACE_BUCKET 404 placeholder)"
  - "feedback_aou_dataproc_pyspark_submit_args (PYSPARK_SUBMIT_ARGS lever)"
provides:
  - "AOU-1_template.ipynb with baked env guards — fresh clone runs with ZERO manual cell paste"
  - "Self-documenting cohort-by-cohort RUN PROTOCOL banner"
affects:
  - ".planning/notebooks/AOU-1_template.ipynb"
tech-stack:
  added: []
  patterns:
    - "Edit .ipynb via plain json module (NOT nbformat write helpers) to preserve existing cell ids byte-for-byte"
    - "Backfill nbformat-4.5 id on legacy cells to stop clean/smudge re-dirty"
key-files:
  created: []
  modified:
    - ".planning/notebooks/AOU-1_template.ipynb"
decisions:
  - "Backfilled fresh ids on 5 pre-existing id-less cells (Rule 3 blocking-issue fix) — required by the plan's own must-have + verification that EVERY cell carry an id"
  - "Wrote (B) env-pin block verbatim including the comment word 'setdefault'; the plan's crude substring assertion was superseded by the substantive HARD-override check (no .setdefault() CALL present)"
metrics:
  duration: ~6m
  completed: 2026-06-06
  tasks: 1
  files: 1
---

# Phase quick-260606-qc1 Plan 01: Bake the 3 manual AoU env guards Summary

Baked the three manual AoU env guards into `AOU-1_template.ipynb` so a fresh `git clone` on the AoU Workbench runs the production cohort build with zero manual cell editing — Cell 1a now carries requester-pays GCS billing (CUSTOM mode scoped to `vwb-aou-datasets-controlled`), a new HARD-override env-pin cell hard-sets `WORKSPACE_BUCKET` + the WGS path (defeating the `cloned-mybucket` 404 placeholder pollution), and a RUN PROTOCOL markdown banner self-documents the smallest→largest, confirm-between, no-"Run All" discipline.

## What Was Done

- **Edit (A):** Replaced Cell 1a's `source` in place (id + metadata preserved) with the requester-pays variant — adds `spark.hadoop.fs.gs.requester.pays.{mode=CUSTOM, buckets=vwb-aou-datasets-controlled, project.id={_proj}}` to `PYSPARK_SUBMIT_ARGS`.
- **Insert (B):** New code cell `Cell 1a''` immediately after Cell 1a — HARD `os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"` and the WGS multiMT path (NOT setdefault).
- **Insert (C):** New RUN PROTOCOL markdown banner at index 1 (after the title), with the ⚠ glyph and the cohort run sequence preserved verbatim.
- Notebook went 12 → 14 cells. Cells 1b/3/3.5/4/4.5/5/5.5/6/7/output are byte-identical to HEAD (verified by source diff against `git show HEAD`).
- Edited via a one-off plain-`json` script (`/tmp/edit_aou1_qc1.py`), NOT nbformat helpers, so existing ids stay byte-for-byte. New cells built with explicit 8-hex `id` + `metadata: {}`.
- Verbatim glyphs/tokens preserved: ⚠, em-dashes (—), doubled apostrophe in `1a''`, and the `f"...{_proj}"` f-string in (A).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Backfilled missing nbformat-4.5 `id` on 5 pre-existing cells**
- **Found during:** Task 1 verification (the plan's own automated check `all('id' in c and 'metadata' in c)` failed).
- **Issue:** The committed-baseline notebook already had 5 cells with NO `id` field (committed indices 1/2/4/6/8 = Cell 1a/1b/3.5/4.5/5.5). The Read tool had shown synthetic display ids (`cell-1`, `cell-2`, …) that did not exist in the real JSON. Missing ids both fail the plan's verification AND would trigger the exact MissingIDFieldWarning clean/smudge re-dirty the plan's must-have aims to prevent.
- **Fix:** Added a fresh `uuid.uuid4().hex[:8]` `id` to ONLY the cells lacking one; existing ids preserved byte-for-byte; no `source`/`metadata`/logic touched. The plan instruction "preserve existing ids byte-for-byte" is satisfied (these cells had none to preserve).
- **Files modified:** `.planning/notebooks/AOU-1_template.ipynb`
- **Commit:** 29d0a1f

**2. [Plan-internal conflict resolved] Verbatim (B) comment contains the word "setdefault"**
- **Found during:** Task 1 verification — the plan's assertion `'setdefault' not in src(3)` fired because the mandated verbatim (B) block's explanatory comment says "so setdefault is UNSAFE".
- **Resolution:** Constraints require (B) be written EXACTLY (comment included). The assertion's literal substring check is a planning-time imprecision; its substantive intent — env-pin must be a HARD `os.environ[...] = ...` assignment, not a `.setdefault()` CALL — was verified directly (no `.setdefault(` call anywhere in the cell). Verbatim block wins per the hard constraint.

## Verification

- Notebook re-parses as valid nbformat 4.5 JSON; exactly 14 cells; all cells have unique `id` + `metadata`.
- Index 0 = title (unchanged); index 1 = RUN PROTOCOL banner (⚠ present); index 2 = requester-pays Cell 1a (`requester.pays.buckets=vwb-aou-datasets-controlled`, `{_proj}` f-string present); index 3 = HARD env-pin (`os.environ["WORKSPACE_BUCKET"] = "gs://rw-migration-aou-rw-476cdac2"`, `1a''` apostrophe preserved, no `.setdefault()` call); index 4 = `# Cell 1b` unchanged.
- Downstream cohort cells (3/3.5/4/4.5/5/5.5/6/7/output) source byte-identical to HEAD.
- Committed blob (`git show HEAD:...`) re-verified; working tree clean after commit (clean/smudge filter did NOT re-dirty — the backfilled ids prevented it).
- Explicit-path commit only (`git add .planning/notebooks/AOU-1_template.ipynb`); no `git add -A`/`.` on the GPFS tree.

## Self-Check: PASSED

- FOUND: `.planning/notebooks/AOU-1_template.ipynb` (modified, committed)
- FOUND commit: 29d0a1f
