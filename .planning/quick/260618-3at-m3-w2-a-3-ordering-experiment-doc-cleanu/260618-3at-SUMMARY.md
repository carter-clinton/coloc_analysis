---
quick_id: 260618-3at
description: m3-W2 A.3 ordering-experiment doc cleanup — keep ordering A, retire B, reframe CR-01, record cluster validation
date: 2026-06-18
status: complete
commit: docs(quick-260618-3at)
---

# Quick Task 260618-3at — SUMMARY

## Outcome

Documented the result of the A.3 BlockMatrix-write ordering experiment and recorded the
decision: **KEEP ordering A, RETIRE ordering B, reframe CR-01 as ordering-independent.**
Docs-only — no source code changed.

## The experiment (what the docs now record)

Ran on a **16-worker resize of cluster `20260617`** (the 2-worker repro cluster scaled up;
n2-standard-4 locked on resize), `scripts/a3_blockmatrix_lowering_repro.py --skip-old
--n-var 130000 --n-samples 2000 --radius-bp 1000000 --budget-sec 3600`, `MASTER=yarn`,
64 concurrent tasks:

| Ordering | Outcome | Wall-time | Artifact |
|----------|---------|-----------|----------|
| A (dense-then-band, deployed default) | **COMPLETED** | 928.0 s | valid `A/repro_A.bm` |
| B (band-then-checkpoint, Pan-UKBB) | **COMPLETED** | 863.5 s | valid `B/repro_B.bm` |
| OLD | skipped (`--skip-old`) | — | hang already proven (dev-10 + prior 2-worker grind) |

- **First cluster validation of the deployed A.3 fix** (dev-10 paused before ever confirming it).
- **B is hang-free** — its `sparsify→checkpoint` shares the OLD fused-write IR shape but did NOT
  reproduce the driver-collect hang.
- The 2→16 resize succeeding **diagnosed the original 24-worker prod-cluster failure as
  quota/size-bound, not project-level**.
- **DECISIVE (`--report-scratch-size`, full `config/ld_regions.tsv`):** `banded(B) == dense(A)`
  for **all 23 A.3 regions** — the manifest's `radius = span+500kb` (cap 50 Mb) is always
  ≥ span/2, so the band covers ~the whole region everywhere → **B saves scratch NOWHERE**.

## Decision

- **KEEP ordering A** (deployed + now cluster-validated). **RETIRE ordering B** — byte-identical
  numerics, zero scratch benefit, nonzero change-risk.
- **CR-01 is ordering-independent:** region_00145 (~710k var) needs ~1.8 TiB transient GCS scratch
  under A *or* B. The real GATE-3 question is xlarge dense-materialize **compute cost vs
  region-splitting**, not checkpoint ordering.
- The hang bug is FIXED + cluster-confirmed → debug session RESOLVED.

## Files changed (docs only)

- `.planning/phases/m3-aou-afr-ld-panel-build/DRAFT-orderingB-band-before-checkpoint.md` — NOT-LANDED banner + rationale; patch parked.
- `.planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-GATE-READINESS.md` — GATE-3 row + A.3 issue block reframed (CR-01 ordering-independent; B retired; cluster result recorded).
- `.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md` — `status: resolved` + frontmatter `resolution` + a 2026-06-18 RESOLUTION block.
- `.planning/STATE.md` — 2026-06-18 RESUME-HERE block, gate-line flip, Last-activity, Quick Tasks Completed row.
- `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` — 2026-06-18 LATEST block.
- Memory (outside repo): `project_state.md` lead rewritten; new `feedback_verify_assumption_before_shipping.md`; `MEMORY.md` pointers refreshed (+ shrank the megaline project-state pointer; index 26.7KB → 13.6KB).

## Next (not part of this task)

1. **GATE-2 dev-10** may resume on ordering A — re-fire `m2_region_00006`, data-layer-verify the `.bm` → rest of dev-10 → AOU-4 memo.
2. **GATE-3 scoping (ordering-independent):** estimate region_00145's dense-materialize wall-time/cost on the production cluster → decide "accept the ~1.8 TiB transient-GCS cost" vs "split the xlarge (>50 Mb) regions."
3. Stop cluster `20260617` (Carter's trigger).
