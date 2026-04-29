---
quick_id: 260428-stv
description: D-M3-09 ruling — Resolution 1 (accept wide regions; Path A.3 for >10 Mb) — Wave 0 Task 5 close
date: 2026-04-29
related_phase: m3-aou-afr-ld-panel-build
related_plan: m3-00-W0-foundations
ruling_token: m3-W0-T5
ruling_commit: b7beef8
---

# Quick Task 260428-stv: D-M3-09 Ruling — Resolution 1

## Goal

Close M3 Wave 0 Task 5 (the Carter human-action gate from
`.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-PLAN.md`)
by ruling on Open Issue O1 (region-width acceptance) and updating the
phase + project bookkeeping accordingly.

## Inputs Read

1. `.planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv` —
   161-row region-class projection (45 small / 80 medium / 28 large /
   8 xlarge; 558.5 cluster-h per ancestry total).
2. `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` —
   "Carter Task 5 — Awaiting D-M3-09 Ruling" section + ruling template
   (lines 197–255).
3. `.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md` lines 730–740 —
   O1 background + Resolution 1 / Resolution 2 trade-off + RESEARCH
   recommendation.

## Decision

**Resolution 1 — accept wide regions; Path A.3 for > 10 Mb.**

Carter ruled 2026-04-28 in response to a 6-point rigor-vs-time-saving
trade-off presentation. Decision driven by: M2 region union remains
canonical fine-mapping unit across milestones; no artificial tile cut
points; no cross-tile LD truncation for the 8 xlarge regions
(chr2/3/4/6/7/9/12/15); Path A.3 is engineering plumbing not statistics;
novelty calls stay region-anchored. RESEARCH.md recommendation
(Resolution 1) confirmed.

Carter standing preference captured in auto-memory:
`feedback_rigor_over_speed.md` (out-of-repo).

## Tasks

| # | Action | Files | Done when |
|---|--------|-------|-----------|
| 1 | Append D-M3-09 block to `m3-CONTEXT.md` `<decisions>` section per Wave 0 SUMMARY ruling template | `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` | `grep -c "### D-M3-09" m3-CONTEXT.md` == 1 |
| 2 | Echo D-M3-09 in `<assumptions>` section as load-bearing decision (matches D-M3-03 echo pattern at assumption #7) | `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` | `grep -c "D-M3-09" m3-CONTEXT.md` ≥ 2 (satisfies Wave 0 check #6) |
| 3 | Flip Wave 0 SUMMARY frontmatter `status: partial` → `complete` and clear `blocking_gate` | `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` | YAML frontmatter shows `status: complete` |
| 4 | Fill in Tasks Completed table Task 5 row (PENDING → ruling commit hash) and update Phase-Level Check Results check #6 PENDING → PASS | `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` | Table row shows commit hash; check #6 row shows count ≥ 2 |
| 5 | Refresh STATE.md frontmatter `stopped_at` to "M3 Wave 0 closed; Wave 1 portal pre-conditions outstanding" | `.planning/STATE.md` | `grep` matches new value in frontmatter |
| 6 | Commit ruling artifacts with `(m3-W0-T5)` token in subject | (above three files) | `git log --oneline --grep "(m3-W0-T5)"` returns one commit |
| 7 | Run `gsd-tools.cjs roadmap update-plan-progress m3-aou-afr-ld-panel-build m3-00-W0-foundations completed` | `.planning/ROADMAP.md` | ROADMAP m3-00 line shows `[x]` |
| 8 | Update STATE.md Quick Tasks Completed table + Last activity line + frontmatter `last_updated` + `last_activity` | `.planning/STATE.md` | New row references quick task `260428-stv` |
| 9 | Final docs commit closing the quick task | All artifacts | `docs(quick-260428-stv): ...` lands |

## Verification (must-haves)

- [x] `grep -c "### D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` == 1
- [x] `grep -c "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` ≥ 2
- [x] Wave 0 SUMMARY frontmatter shows `status: complete` and `blocking_gate: none ...`
- [x] Wave 0 SUMMARY Task 5 row shows commit hash (not PENDING)
- [x] Wave 0 SUMMARY check #6 row shows PASS (count ≥ 2)
- [x] STATE.md frontmatter `stopped_at` shows "M3 Wave 0 closed; Wave 1 portal pre-conditions outstanding"
- [x] ROADMAP.md m3-00 plan-list line shows `[x]`
- [x] STATE.md Quick Tasks Completed table has new row for 260428-stv
- [x] git log shows one `(m3-W0-T5)` commit and one `docs(quick-260428-stv)` commit

## Out of Scope

- Wave 1 portal pre-conditions (P1–P6 + R1 hard gate + AUX path verification)
  — these are AoU-portal Carter actions tracked in
  `.planning/phases/m3-aou-afr-ld-panel-build/m3-01-W1-aou-cohort-and-hard-gates-PLAN.md`.
- M2-supplementary phase scoping (D-M3-05 follow-on) — separate phase.
- Tile-splitter implementation — explicitly rejected by this ruling
  (Resolution 2 not chosen).
