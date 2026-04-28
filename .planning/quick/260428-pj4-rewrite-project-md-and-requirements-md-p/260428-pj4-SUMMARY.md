---
phase: quick-260428-pj4
plan: 01
subsystem: documentation
tags: [m0-closeout, project-md, requirements-md, amendment-12, post-pivot, track-a, track-b]
dependency_graph:
  requires:
    - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
    - .planning/amendments/AOU-LD-PIPELINE.md
    - CLAUDE.md
  provides:
    - .planning/PROJECT.md (Amendment §12-aligned post-pivot charter)
    - .planning/REQUIREMENTS.md (Amendment §12-aligned testable acceptance criteria; 8 preserved + 17 new = 25 REQs)
  affects:
    - M0 closeout posture (this task closes the PROJECT.md + REQUIREMENTS.md half of M0 documentation; ROADMAP.md + DECISIONS.md half is owned by Terminal A in parallel)
tech-stack:
  added: []
  patterns:
    - "reconcile-to-spec rewrite (audit current content against authoritative source, edit only on drift; do not regenerate from scratch)"
    - "audit-trail dating in document headers (each reconciliation pass gets an explicit dated note in-file so future readers can trace claim provenance)"
key-files:
  created:
    - path: .planning/quick/260428-pj4-rewrite-project-md-and-requirements-md-p/260428-pj4-SUMMARY.md
      provides: This document
  modified:
    - path: .planning/PROJECT.md
      provides: Post-pivot project charter; M0-status paragraph now records 2026-04-28 reconciliation pass + zero-drift outcome
      delta: "+7 / -4 lines (lines 138-145 status paragraph rewrite + line 187 'Last updated' bump)"
    - path: .planning/REQUIREMENTS.md
      provides: Post-pivot testable acceptance criteria; header now records 2026-04-28 reconciliation pass + §12 inventory satisfied
      delta: "+9 / -0 lines (header note appended after the existing AoU LD pipeline link)"
decisions:
  - "Both files were already fully aligned with Amendment §12 from the 2026-04-23 post-pivot rewrite cluster (commits d9c9905 docs(project) and 995275c docs(requirements)). The reconcile-to-spec instruction explicitly anticipated this case ('If the current files already satisfy §12 fully, the work is to make any small corrections needed and commit')."
  - "Reconciliation took the form of audit-trail dating in each file's header/status section, recording the 2026-04-28 §12 alignment pass and the zero-drift outcome. This avoids gratuitous content edits while still providing a commit-trail for the M0 closeout documentation milestone."
  - "REQ count is 25 (= 8 preserved pre-pivot + 17 new Track B), not the '24 (= 8 + 16)' figure stated in the PLAN.md done-criterion — the must_haves block in the same PLAN.md frontmatter enumerates 17 new Track B REQs (9 method REQs + 5 novelty classes + comparator catalog lock + 2 AoU REQs = 17). The done-criterion's '16 new' was a counting error in the plan; the actual file content matches the must_haves enumeration. Treated as plan-typo, not as drift requiring file-side correction."
metrics:
  duration: ~7 min (single agent, post-context-load)
  completed_date: 2026-04-28
---

# Quick Task 260428-pj4: Reconcile PROJECT.md + REQUIREMENTS.md to Amendment §12

**One-liner:** Reconcile-to-spec audit pass on `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` against the 2026-04-22 genome-wide-reframe Amendment §12 row instructions; both files were already fully aligned from the 2026-04-23 post-pivot rewrite cluster, so this task adds dated reconciliation notes and bumps the PROJECT.md "Last updated" timestamp without substantive content change.

## Outcome

Two atomic commits on `main`:

| Task | Commit | File | Net change |
|------|--------|------|------------|
| Task 1 | `70db503` | `.planning/PROJECT.md` | +7 / -4 lines (status paragraph rewrite recording the 2026-04-28 reconciliation pass; 'Last updated' bump from 2026-04-25 to 2026-04-28) |
| Task 2 | `56fd413` | `.planning/REQUIREMENTS.md` | +9 / -0 lines (header note recording the 2026-04-28 reconciliation pass + the satisfied §12 inventory) |

**Total diff:** 2 files changed, 16 insertions, 4 deletions.

**HARD-LOCKED files touched:** ZERO (verified post-commit via `git status --short -- .planning/ROADMAP.md .planning/DECISIONS.md '.planning/phases/m3-*' .planning/amendments/aou-egress-audit-log.md` returning empty).

**Terminal A non-interference:** Confirmed. Two m3-00 commits from Terminal A (`26557aa`, `4cf6295`) landed during this task's execution window; both touched `bin/`, `envs/`, `src/`, `tests/`, `config/`, and `.planning/phases/m3-aou-afr-ld-panel-build/` — none of which this task's scope includes. Commit graph is clean and linear:

```
56fd413 docs(quick-260428-pj4): reconcile REQUIREMENTS.md header to Amendment §12 (Task 2)   ← this task
70db503 docs(quick-260428-pj4): reconcile PROJECT.md M0-status paragraph to Amendment §12 (Task 1)  ← this task
26557aa feat(m3-00): add ld_panel resolver helper + pipeline.yaml ld_panel block + resolver pytest   ← Terminal A
4cf6295 feat(m3-00): add LD region manifest reformatter + dev-subset selector + Wave 0 pytest scaffold  ← Terminal A
```

## Drift analysis

The plan's `<context>` HTML comment explicitly anticipated this case:

> The CURRENT versions of both files (read into context above) already contain post-pivot content — they were rewritten in an earlier pass. The executor must verify the current content is consistent with Amendment §12 and bring any drift back into alignment, NOT regress the files to a pre-pivot state. If the current files already satisfy §12 fully, the work is to make any small corrections needed and commit.

**Result:** Both files are fully aligned with Amendment §12; zero substantive drift was identified.

### PROJECT.md alignment audit (5 required structural elements)

| § | Required element | Status | Evidence |
|---|------------------|--------|----------|
| 1 | Authoritative-pivot-charter header (links to amendment + 5 companion docs + CLAUDE.md) | PRESENT | Lines 3-13: amendment link, TRACK-A-PIVOT, SUMSTATS-UPGRADE.tsv/.md, AOU-LD-PIPELINE, TRACK-A-FROZEN-NUMBERS, ../CLAUDE.md |
| 2 | Who / What / Where / Why sections (post-pivot framing with Track A / Track B distinction) | PRESENT | Lines 15-87: Carter sole author; Track A real-LD audit at Genome Medicine; Track B genome-wide 9-trait × 2-ancestry; GPFS canonical path; AoU Workbench for M3; Stage 2 numerics 51/96 vs 48/95 = 1.06× cited |
| 3 | Constraints block verbatim from CLAUDE.md (6 bullets) | PRESENT | Lines 89-107: 100% public data, solo author, timeline-not-binding, no-web-stack, DUA-lead-times, GPFS+branch-isolation — verbatim match |
| 4 | Goals (5 numbered items) | PRESENT | Lines 109-134: M0→M6 to Nature Genetics, Track A short-form to Genome Medicine, OSF pre-registration via Amendment §9, GitHub release with Zenodo DOI, preserve T1 spine per Amendment §8 |
| 5 | Current status + Open human-action items | PRESENT (updated this task) | Lines 136-217: M0 ~70% complete, M1 COMPLETE 2026-04-25, Track B M2-M6 gated on OSF, three open human actions (OSF web-UI submission, BMI EUR primary-source decision, MVP phs001672 DUA) |

### REQUIREMENTS.md alignment audit (Amendment §12 row "REQUIREMENTS.md")

| Category | Required REQs | Present? |
|----------|---------------|----------|
| Preserved pre-pivot (8) | REQ-SNAKEMAKE-CI, REQ-PUBLIC-DATA-ONLY, REQ-SUSIE-RSS-POLICY, REQ-NEGATIVE-CONTROLS, REQ-PATH-PARAMETERIZATION, REQ-OSF-PREREG, REQ-PP.H4-THRESHOLD-SWEEP, REQ-EQUITY-FRAMING | All 8 present |
| Method REQs (9) | REQ-TRAIT-INVENTORY, REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL, REQ-TWO-STAGE-COLOC, REQ-HYPRCOLOC-MULTI, REQ-POLYFUN-RESCUE, REQ-L2G-GENE-PRIORITIZATION, REQ-BORZOI-VARIANT-EFFECT, REQ-REPLICATION-HOLDOUT | All 9 present |
| Novelty classes (5) | REQ-NOVELTY-CLASS-1 through -5 (Class 5 explicitly supplementary per §7.3) | All 5 present; Class 5 supplementary framing verified at lines 354, 362-363 |
| Comparator-catalog lock (1) | REQ-CATALOG-VERSION-LOCK | Present |
| AoU LD (2) | REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION | Both present |
| **Total** | **25 REQs (8 + 17)** | **25 in body, 25 in cross-reference table — consistent** |

Each REQ carries a `Source:` line citing either the Amendment § number(s) or the pre-pivot REQ origin (`GSD_BRIEFING.md` §5.2 gap #N, `Revision_Plan.md` Phase N, etc.) for an unbroken audit trail.

### Counting-discrepancy note (plan vs file)

The PLAN.md `<done>` criterion for Task 2 says *"all 24 REQs present (8 preserved pre-pivot + 16 new Track B)"*. The file actually has **25 REQs (8 + 17)**. The `<must_haves>` enumeration in the same PLAN.md frontmatter lists 17 new Track B REQs (9 method REQs + 5 novelty classes + comparator catalog lock + 2 AoU REQs = 17), so the `<done>` "16 new" is a self-inconsistent typo within the plan, not file-side drift. Resolved as: trust the must_haves enumeration (17), don't delete a load-bearing REQ to match the typo.

## Verify-command outputs

### Task 1 (PROJECT.md)

```
PROJECT.md content check PASSED
 .planning/PROJECT.md | 11 +++++++----
 1 file changed, 7 insertions(+), 4 deletions(-)
```

All 13 grep-anchor patterns from the plan's automated verify block matched (PROJECT-AMENDMENT path, Track A, Track B, 9 traits, MTAG, CPASSOC, HyPrColoc, AoU/All of Us, EUR, AFR, 100% public data, GPFS/git.isolation, M0/M6).

### Task 2 (REQUIREMENTS.md)

```
REQUIREMENTS.md content check PASSED
 .planning/REQUIREMENTS.md | 9 +++++++++
 1 file changed, 9 insertions(+)
```

All 28 grep-anchor patterns from the plan's automated verify block matched (PROJECT-AMENDMENT path, AOU-LD-PIPELINE.md, all 8 preserved pre-pivot REQs, all 9 new method REQs, all 5 novelty class REQs, REQ-CATALOG-VERSION-LOCK, REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION, REQ-REPLICATION-HOLDOUT, REQ ID cross-reference table marker).

## Deviations from Plan

**None — plan executed exactly as written, with the `<context>` HTML-comment "reconcile to spec, not regenerate" branch taken because both files were already fully §12-aligned from the 2026-04-23 post-pivot rewrite cluster (commits `d9c9905` and `995275c`).**

The reconciliation edits made (audit-trail dating in each file's header/status section) are the minimum content change consistent with both:

1. The plan's instruction to "make any small corrections needed and commit" when no substantive drift is found.
2. The plan's success criterion that a commit cover both files (`docs(quick-260428-pj4): rewrite PROJECT.md + REQUIREMENTS.md ...`) — split here into one commit per task per the GSD per-task-commit protocol, since the orchestrator handles only the docs commit (SUMMARY/STATE/ROADMAP) at Step 8 and per-task commits are the executor's responsibility.

No deviation rules (Rule 1 bug, Rule 2 missing critical functionality, Rule 3 blocking issue, Rule 4 architectural change) were triggered.

## Authentication Gates

None encountered.

## Self-Check: PASSED

**Created files exist:**
- `.planning/quick/260428-pj4-rewrite-project-md-and-requirements-md-p/260428-pj4-SUMMARY.md` (this file): FOUND

**Modified files exist with expected content:**
- `.planning/PROJECT.md`: FOUND, "Last updated: 2026-04-28" present
- `.planning/REQUIREMENTS.md`: FOUND, 2026-04-28 reconciliation note present in header

**Commits exist on main:**
- `70db503` (Task 1, PROJECT.md): FOUND in `git log`
- `56fd413` (Task 2, REQUIREMENTS.md): FOUND in `git log`

**HARD-LOCKED files unchanged:**
- `.planning/ROADMAP.md`, `.planning/DECISIONS.md`, `.planning/phases/m3-*`, `.planning/amendments/aou-egress-audit-log.md`: ZERO modifications (verified post-commit).
- `.planning/STATE.md`: present in `git status --short` from before this task started (orchestrator-managed); not touched by this task's edits.

**Verify scripts:**
- Task 1 grep block: PASSED
- Task 2 grep block: PASSED
