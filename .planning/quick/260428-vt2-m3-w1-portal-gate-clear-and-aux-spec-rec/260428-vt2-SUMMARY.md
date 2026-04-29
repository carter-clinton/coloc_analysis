---
quick_id: 260428-vt2
description: m3-W1-portal-gate-clear-and-aux-spec — record M3 Wave 1 portal pre-conditions cleared (NCSU faculty controlled-tier basis) + pre-stage AUX path verification spec
date: 2026-04-29
status: complete
ruling_token: m3-W1-portal-cleared
commit: __SAME_COMMIT_AS_THIS_FILE__
related_phase: m3-aou-afr-ld-panel-build
related_plan: m3-01-W1-aou-cohort-and-hard-gates (pre-fire pre-conditions)
---

# Quick Task 260428-vt2: M3 Wave 1 Portal-Gate Clear + AUX Spec — SUMMARY

## What landed

Three deliverables in a single atomic commit (token
`(m3-W1-portal-cleared)`):

1. **Egress HARD GATE flipped PASS** in
   [aou-egress-audit-log.md](../../amendments/aou-egress-audit-log.md):
   Status header, table row, and a new structured ruling block all
   reflect the 2026-04-28 NCSU-faculty-basis ruling (variant×variant LD
   R matrices = aggregate / derived statistics governed by standard AoU
   egress review at egress-request time, NOT by per-data-class custom
   ruling letters).
2. **Paste-ready AUX path verification spec** at
   [m3-W1-AUX-PATH-VERIFICATION.md](../../phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md):
   the load-bearing artifact Carter executes from inside an AoU
   Workbench Jupyter terminal session — Step 2 canonical literal-path
   `gsutil ls` command, Step 4 `gsutil stat` filename pin, Step 1+3
   shell-environment sanity checks, three failure modes with
   remediation (env-var unset / filename mismatch / access denied),
   3-item Carter-signoff verification checklist, Run Log template
   pre-formatted for paste-and-commit.
3. **STATE.md refresh:** frontmatter `stopped_at` updated to "M3 Wave 0
   closed; Wave 1 portal pre-conditions all PASS; AUX path verification
   awaits Carter Workbench session" + `last_updated` /
   `last_activity` refreshed; new `### Prior session (2026-04-28
   evening — m3-W1 portal cleared + AUX spec staged, quick-260428-vt2)`
   entry appended under `## Session Continuity` (below the existing
   top "Last session" block, preserving room for Terminal C to update
   the top block later if needed).

## Tasks completed

| # | Action | Files | Result |
|---|--------|-------|--------|
| 1 | Egress audit log Status header rewrite (PENDING → PASS framing) | `.planning/amendments/aou-egress-audit-log.md` lines 3–5 | PASS — header now reads "HARD GATE PASS as of 2026-04-28 (NCSU faculty controlled-tier... Carter PI confirmation 2026-04-28 via quick task 260428-vt2)" |
| 2 | Egress audit log §Egress Classification Ruling section rewrite (table row PENDING → PASS + new structured ruling block + Note paragraph rewrite) | `.planning/amendments/aou-egress-audit-log.md` lines 19–66 (post-edit) | PASS — table row now `2026-04-28 \| ... \| PASS \| ...`; ruling block contains all 6 fields (Status / Date / Basis / Provenance / Re-open conditions / Cross-reference) |
| 3 | Egress audit log Last-updated line refresh | `.planning/amendments/aou-egress-audit-log.md` last line | PASS — now reads "2026-04-28 (HARD GATE ruled PASS under NCSU faculty controlled-tier basis; quick task 260428-vt2 commit `(m3-W1-portal-cleared)`)" |
| 4 | New AUX path verification spec | `.planning/phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md` | PASS — file exists; Step 2 carries the canonical literal path `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/`; 3 failure modes (i) / (ii) / (iii) all present with full remediation including `(m3-W1-aux-path-fix)` commit recipe; 3-checkbox Carter-signoff verification checklist present; Run Log template ready for paste |
| 5 | STATE.md frontmatter `stopped_at` + `last_*` refresh | `.planning/STATE.md` lines 6–8 | PASS — `stopped_at` matches Carter directive verbatim |
| 6 | STATE.md `## Session Continuity` append | `.planning/STATE.md` after line 370 | PASS — new `### Prior session (2026-04-28 evening — m3-W1 portal cleared + AUX spec staged, quick-260428-vt2)` entry inserted; existing top "Last session" block (`2026-04-28T03:05:00.000Z` / quick-260428-ppz close) intact |
| 7 | Quick-task PLAN.md + SUMMARY.md | `.planning/quick/260428-vt2-.../{PLAN,SUMMARY}.md` | PASS — both authored |
| 8 | Single atomic commit with `(m3-W1-portal-cleared)` token in subject | All five files above | PASS — see commit hash in this SUMMARY's frontmatter `commit:` field |

## Carter-delivered facts (2026-04-28 coordinator chat — recorded for provenance)

* **NCSU faculty controlled-tier AoU access:** NCSU faculty
  appointment (ASHES Laboratory, Department of Biological Sciences)
  grants Carter controlled-tier AoU Researcher Workbench access. P1
  workspace creation + P2 DUS + P3 RPS + P4 billing profile + P6 P&P
  draft registration are all auto-approved at his access tier (no
  per-gate manual review). Billing profile is attached with initial
  credits active.
* **R1 egress classification:** variant×variant LD R matrices computed
  from n ≥ 60k AFR (and EUR ~130k) participants are aggregate /
  derived statistics carrying no individual-level information. They
  are governed by standard AoU egress review (automated + manual
  reviewer pipeline) at egress-request time, NOT by per-data-class
  custom ruling letters. The original M3 plan's expectation of a
  written ruling letter is superseded — no such letter is required
  under standard NCSU-faculty egress procedures.
* **Re-open conditions (preserved as future-Carter directive):** if
  standard AoU egress review at any future egress-request time flags
  a specific variant×variant LD matrix file for additional review,
  document the per-file event in `aou-egress-audit-log.md` under
  `## Per-Bundle Audit Entries` with the AoU reviewer's specific
  concern + resolution. **Do NOT pre-emptively re-open this HARD
  GATE absent a triggering event.** Per-file egress-review events are
  routine and do not retroactively invalidate the 2026-04-28 PASS
  ruling.

## Wave 1 readiness — current state

Of the 7 readiness items in
[m3-00-W0-foundations-SUMMARY.md](../../phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md)
"Wave 1 Readiness Checklist", **6 are now PASS** and **1 is
pre-staged but un-executed**:

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | **D-M3-09** O1 ruling (region-width acceptance) | ✅ **PASS** | quick-260428-stv (`b7beef8` + `5dd9548`); m3-CONTEXT.md `<decisions>` D-M3-09 block + `<assumptions>` #9 echo |
| 2 | **P1** AoU workspace creation | ✅ **PASS** (2026-04-28) | NCSU faculty controlled-tier basis; this quick task |
| 3 | **P2** DUS approval | ✅ **PASS** (2026-04-28) | NCSU faculty controlled-tier basis; this quick task |
| 4 | **P3** RPS approval | ✅ **PASS** (2026-04-28) | NCSU faculty controlled-tier basis; this quick task; portal paste from quick-260428-ppz `aou-rps-and-pp-registration.zip` available if asked to re-submit |
| 5 | **P4** Billing profile attached | ✅ **PASS** (2026-04-28) | NCSU faculty controlled-tier basis; initial credits active per Carter PI confirmation |
| 6 | **P6** P&P draft registration filed | ✅ **PASS** (2026-04-28) | NCSU faculty controlled-tier basis; this quick task |
| 7 | **R1 (HARD GATE)** Egress classification | ✅ **PASS** (2026-04-28) | aou-egress-audit-log.md Egress Classification Ruling section rewritten with structured ruling block; basis = NCSU faculty controlled-tier + standard AoU egress review |
| 8 | **AUX path verification** | ⏳ **PRE-STAGED** | spec at m3-W1-AUX-PATH-VERIFICATION.md awaits Carter Workbench session; ~30 sec when fired |

**When AUX gate clears:** Wave 1 unblocked → `/gsd-execute-phase
m3-aou-afr-ld-panel-build` fires the m3-01 plan (AOU-1 cohort
definition notebook → 3 checkpointed MTs:
`mt_afr_qc.mt` + `mt_afr_pca_selfid.mt` + `mt_eur_qc.mt` per D-M3-07 +
D-M3-01).

## Verification (all must-haves passed pre-commit)

* [x] aou-egress-audit-log.md Status header reads "HARD GATE PASS as
  of 2026-04-28"
* [x] aou-egress-audit-log.md HARD GATE table row shows
  `2026-04-28 | ... | PASS | ...` (no remaining PENDING / TBD-Wave-1)
* [x] aou-egress-audit-log.md ruling block contains all 6 fields
  (Status, Date, Basis, Provenance, Re-open conditions, Cross-reference)
* [x] m3-W1-AUX-PATH-VERIFICATION.md exists with all 4 steps + 3
  failure modes + 3-item checklist + Run Log template
* [x] STATE.md frontmatter `stopped_at` matches Carter directive verbatim
* [x] STATE.md `## Session Continuity` has new `### Prior session`
  entry below the existing top "Last session" block (top block
  preserved intact)
* [x] Single atomic commit with `(m3-W1-portal-cleared)` token in subject
* [x] No file outside `.planning/` touched (per Carter directive scope)
* [x] No file under `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/`
  touched (Terminal C scope respected)
* [x] No file under `docs/manuscript/` touched (Track A scope respected)

## Out of Scope (explicit non-deliverables)

* **Wave 1 firing.** `/gsd-execute-phase m3-aou-afr-ld-panel-build`
  fires AFTER AUX path verification clears.
* **`src/python/aou_ld_panel.py` edit.** The `ANCESTRY_PREDS_PATH`
  constant remains at its inferred value
  (`gs://.../aux/ancestry/ancestry_preds.tsv`); if the actual on-bucket
  filename differs, the path-fix-up commit `(m3-W1-aux-path-fix)`
  lands during Carter's Workbench session per Failure Mode (ii) of
  the AUX spec.
* **Wave 0 SUMMARY checklist update.** The m3-00 Wave 0 SUMMARY is a
  frozen artifact of when Wave 0 closed
  (status: complete since `b7beef8`); updating its readiness
  checkboxes now would rewrite phase-artifact history. Current state
  is recorded canonically in `aou-egress-audit-log.md` + `.planning/STATE.md`.
* **m3-01 ROADMAP plan-list line.** Still `[ ]`; flips to `[x]` when
  Wave 1 actually fires and m3-01 plan completes (post-Wave 1
  closeout, NOT here).
* **Track A R2 (`ta-sh2b3-canonical-and-cache-refresh`) scope.**
  Terminal C is in `/gsd-discuss-phase` for that phase; disjoint file
  scope from this task; no edits to that phase's directory.
* **STATE.md "Quick Tasks Completed" table append.** Carter directed a
  "single atomic commit with token `(m3-W1-portal-cleared)`" with
  three deliverables only — the standard /gsd-quick STATE.md "Quick
  Tasks Completed" table append is intentionally omitted to keep this
  task scoped to Carter's three deliverables. Future quick-task table
  consumers can grep `git log --grep "(m3-W1-portal-cleared)"` to
  locate this work.

## Self-Check: PASSED
