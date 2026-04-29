---
quick_id: 260428-stv
description: D-M3-09 ruling — Resolution 1 (accept wide regions; Path A.3 for >10 Mb) — Wave 0 Task 5 close
date: 2026-04-29
status: complete
ruling_token: m3-W0-T5
ruling_commit: b7beef8
docs_commit: __FILLED_BY_FINAL_COMMIT__
related_phase: m3-aou-afr-ld-panel-build
related_plan: m3-00-W0-foundations
---

# Quick Task 260428-stv: D-M3-09 Ruling — Resolution 1 — SUMMARY

## What landed

**Decision committed:** D-M3-09 = Resolution 1 (accept wide regions;
Path A.3 for > 10 Mb regions). Wave 0 Task 5 (Carter human-action gate)
closed; Wave 0 plan flipped to `status: complete`; Wave 1 portal
pre-conditions are now the outstanding M3 work.

## Tasks completed

| # | Action | Files | Commit |
|---|--------|-------|--------|
| 1 | D-M3-09 block appended to m3-CONTEXT.md `<decisions>` section per ruling template (Decision + Why + How to apply) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` | b7beef8 |
| 2 | D-M3-09 echo added to `<assumptions>` section as assumption #9 (matches D-M3-03 echo pattern at #7) — gets `grep -c "D-M3-09"` to 2, satisfying Wave 0 verification check #6 | `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` | docs commit |
| 3 | Wave 0 SUMMARY frontmatter `status: partial` → `status: complete`; `blocking_gate` cleared (was `O1-region-width-acceptance`) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` | b7beef8 |
| 4 | Wave 0 SUMMARY Tasks Completed Task 5 row updated (PENDING → b7beef8) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` | docs commit |
| 5 | Wave 0 SUMMARY Phase-Level Check Results check #6 row updated (PENDING → 2) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` | docs commit |
| 6 | STATE.md frontmatter `stopped_at` refreshed to "M3 Wave 0 closed; Wave 1 portal pre-conditions outstanding" | `.planning/STATE.md` | b7beef8 |
| 7 | Ruling commit landed: `decision(m3-W0-T5): D-M3-09 ruling — Resolution 1 (accept wide regions; Path A.3 for >10 Mb)` | (above three files) | b7beef8 |
| 8 | gsd-tools roadmap update fired (m3-00-W0-foundations marked completed in ROADMAP.md plan-list) | `.planning/ROADMAP.md` | docs commit |
| 9 | STATE.md Quick Tasks Completed table appended; Last activity line + frontmatter `last_updated` + `last_activity` refreshed | `.planning/STATE.md` | docs commit |

## Decision rationale

Carter chose Resolution 1 over Resolution 2 in response to a 6-point
rigor-vs-time-saving trade-off presented at quick-task open. Verbatim
Carter response (2026-04-28):

> "i want th more rigorous/ defensible option, I don't care about time."
> "Then let's go with Resolution 1. And for the record, I always want
> the most rigorous option over time saving option. make sure to update
> this in the state or memory or wherever needs to be updated"

Six-point rigor argument grounding the decision (full text in
m3-CONTEXT.md D-M3-09 block):

1. M2 region union remains the canonical fine-mapping unit across
   M2 → M3 → M4 → M5; no tile/region asymmetry between milestones; no
   translation table needed.
2. Tile cut points (lowest-LD-density-valley heuristic) have no
   biological basis and create defensible-question vectors for
   reviewers.
3. Cross-tile LD truncation at fine-mapping is a real statistical loss
   for the 8 xlarge regions (chr2 50.5 Mb, chr3 50.5 Mb, chr4 101.7 Mb,
   chr6 102.5 Mb MHC-spanning, chr7 58.0 Mb, chr9 73.1 Mb, chr12 88.8 Mb,
   chr15 65.1 Mb).
4. Path A.3 BlockMatrix-write produces the same LD matrix as `to_numpy()` —
   engineering plumbing already coded in `src/python/aou_ld_panel.py`,
   not a statistical compromise.
5. Novelty-class definitions (REQ-NOVELTY-CLASS-2 AFR-specific) stay
   region-anchored under R1; under R2 they require re-derivation and
   tile→region translation at every cross-milestone reasoning step.
6. Carter standing preference (memory file
   `feedback_rigor_over_speed.md`, 2026-04-28; project-level CLAUDE.md
   "Timeline is not a binding constraint. Rigor and impact matter more
   than speed.") — in any gray-area trade-off, choose rigor.

R2's only advantage was wall-clock saving (~3 wall days at AoU's 8–12
concurrent Dataproc quota), which is not a binding constraint per
PROJECT.md.

## Cost projection (carried forward into Wave 4 production)

| Region class | n | Path-A | Per-region cluster-h | Per-ancestry cluster-h |
|---|---|---|---|---|
| small (≤ 5 Mb) | 45 | A.1 | 0.5 | 22.5 |
| medium (5–25 Mb) | 80 | A.2 | 1.5 | 120.0 |
| large (25–50 Mb) | 28 | A.3 | 8.0 | 224.0 |
| xlarge (> 50 Mb) | 8 | A.3 | 24.0 | 192.0 |
| **Total per ancestry** | **161** | | | **558.5** |

AFR + EUR: ~1,117 cluster-h ≈ 5–7 wall days at AoU's 8–12 concurrent
Dataproc quota. The 102 Mb chr4 (m2_region_00120) and 102.5 Mb chr6
MHC-spanning (m2_region_00145) are the largest single-job loads, firing
as A.3 streaming-writes.

## Memory updates (out-of-repo)

- `feedback_rigor_over_speed.md` (NEW) — Carter standing preference: in
  any gray-area trade-off between rigor/defensibility and time/compute
  saving, always recommend and proceed with the rigor option. Captured
  2026-04-28 from Carter's verbatim ruling. Indexed in `MEMORY.md`.

## Wave 1 readiness (next-step inventory)

Per `m3-00-W0-foundations-SUMMARY.md` "Wave 1 Readiness Checklist", the
following are now the outstanding M3 work items:

- [ ] **P1** AoU workspace creation (paste from
  `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`)
- [ ] **P2** DUS approval
- [ ] **P3** RPS approval
- [ ] **P4** Billing profile attached
- [ ] **P6** P&P draft registration filed
- [ ] **R1 (HARD GATE)** Egress classification of variant×variant LD
  matrices in writing (AoU support email or portal-issued ruling letter);
  populates the HARD GATE row in
  `.planning/amendments/aou-egress-audit-log.md`.
- [ ] **AUX path verification** (`gsutil ls $AUX_BASE/ancestry/` from
  inside AoU workspace; if `ancestry_preds.tsv` filename differs from
  the inferred path, update `ANCESTRY_PREDS_PATH` in
  `src/python/aou_ld_panel.py`).
- [x] **D-M3-09 — O1 ruling** (closed by this quick task).

Wave 1 cannot fire until R1 (egress hard gate) lands. None of P1–P6
require additional planning artifacts on Carter's side — they are all
AoU portal actions tracked in
`m3-01-W1-aou-cohort-and-hard-gates-PLAN.md`.

## Verification (all must-haves passed)

- [x] `grep -c "### D-M3-09" m3-CONTEXT.md` == 1
- [x] `grep -c "D-M3-09" m3-CONTEXT.md` ≥ 2
- [x] Wave 0 SUMMARY `status: complete`; `blocking_gate: none`
- [x] Wave 0 SUMMARY Task 5 row shows commit b7beef8 (not PENDING)
- [x] Wave 0 SUMMARY check #6 row shows count = 2 (not PENDING)
- [x] STATE.md frontmatter `stopped_at` = "M3 Wave 0 closed; Wave 1 portal pre-conditions outstanding"
- [x] ROADMAP.md m3-00 plan-list line shows `[x]`
- [x] git log shows commit b7beef8 with `(m3-W0-T5)` token in subject
- [x] STATE.md Quick Tasks Completed table has 260428-stv row

## Self-Check: PASSED
