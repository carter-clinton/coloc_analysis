---
phase: quick-260426-aow
plan: 01
type: execute
status: complete
completed: 2026-04-26
commits:
  - d93a92b  # Task 1 — PLAN + AOU-WORKBENCH-REGISTRATION.md (the paste-ready deliverable)
  - <task-2-hash>  # Task 2 — SUMMARY + STATE row
audit_items_closed:
  - AOU-WORKBENCH-REGISTRATION-TRACK-B-M3
files_modified:
  - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-PLAN.md          # NEW
  - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md  # NEW (the deliverable)
  - .planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md       # NEW
  - .planning/STATE.md                                                                           # +1 row in Quick Tasks Completed
files_unchanged:
  - .planning/PROJECT.md                                                # cited only
  - .planning/ROADMAP.md                                                # cited only
  - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md   # cited only
  - .planning/amendments/AOU-LD-PIPELINE.md                             # cited only
  - .planning/amendments/SUMSTATS-UPGRADE.tsv                           # cited only
  - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md               # cited only
  - .planning/amendments/TRACK-A-PIVOT.md                               # cited only
  - .claude/settings.json, .planning/config.json                        # pre-existing M preserved
metrics:
  duration_min: ~30
  task_count: 2
  commit_count: 2
  parallel_agent_collisions: 0
---

# Quick Task 260426-aow — AoU Researcher Workbench Workspace Registration (Track B + M3)

## One-liner

Built the paste-ready workspace registration document
[`AOU-WORKBENCH-REGISTRATION.md`](AOU-WORKBENCH-REGISTRATION.md) for All
of Us Researcher Workbench portal workspace creation. Document is scoped
to **Track B + M3 only** (genome-wide cross-trait pleiotropy + novel-
variant discovery across 9 traits × EUR/AFR + the AoU-derived AFR LD
reference panel build); **Track A is explicitly omitted** with a
single-paragraph rationale (1000G Phase 3 EUR real LD on 10 EUR
autosomal regions; no AoU controlled-tier access required; being
submitted to *Genome Medicine* in 2026-05 / 2026-06 ahead of this AoU-
workbench-dependent work). 13 portal-section headers, 46 distinct inline
`[src: ...]` citations, 518 lines. Two atomic commits.

## Atomic Commits

| # | Commit  | Subject                                                                                                            | Files                                                                                                                                                                                                                                                                                                       | Insertions | Deletions |
|---|---------|--------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-----------|
| 1 | `d93a92b` | docs(quick-260426-aow): draft AoU Researcher Workbench workspace registration (Track B + M3)                       | `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-PLAN.md` (NEW), `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` (NEW)                                                                                                          | 662        | 0         |
| 2 | `<task-2-hash>` | docs(quick-260426-aow): close AoU workspace registration quick task (SUMMARY + STATE row)                          | `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/260426-aow-SUMMARY.md` (NEW), `.planning/STATE.md` (+1 row)                                                                                                                                                                                | TBD        | TBD       |

Both commits scoped via explicit `git add <path>` (no `git add -A` /
`git add .`); pre-existing dirty paths (`.claude/settings.json`,
`.planning/config.json`, `.claude/scheduled_tasks.lock`, parallel
quick-task scratch md5 files under
`.planning/quick/260426-06n-*`, untracked `bin/fire_m2_04_mtcojo.sh`,
`bin/track-a-repro-bundle.*`, `src/python/build_*.py`, `src/python/mtcojo_*.py`,
`src/python/select_mtcojo_eligible_targets.py`,
`src/snakemake/rules/m2_*.smk`, `.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md`)
were NOT staged — they belong to other workstreams.

## Open questions resolved with reasonable defaults (auto mode)

1. **Track A submission tense** → forward-looking ("being submitted in
   2026-05 / 2026-06"), matching the actual ROADMAP Track-A-finalization
   milestone state. (User's command described it as already submitted; the
   ROADMAP shows finalization in active progress as of 2026-04-26.) If
   Track A submission lands before this AoU workspace is filed, swap two
   sentences in §3 of the deliverable.
2. **Scientific Data venue commitment** → committed explicitly per the
   user's command. The project's planning artifacts commit to a Zenodo
   deposit + AoU disclosure language but do not currently commit to a
   standalone *Scientific Data* data-descriptor manuscript. Carter may
   want to record this as a project decision in `.planning/DECISIONS.md`.
3. **Portal field-format granularity** → narrative-Markdown with section
   headers that map 1:1 onto the AoU portal RPS sub-prompts, conservatively
   sized for typical character limits, with a top-of-file paste-time-trim
   note advising the reader to right-size each block before pasting.

## Verification (all checks PASS)

| Check | Expected | Actual | Status |
|---|---|---|---|
| Inline `[src: ...]` citation count | ≥ 20 | **46 distinct** | ✓ |
| Section headers (`## ` markers) | ≥ 11 | **13** | ✓ |
| Track A omission paragraph present | ≥ 1 mention | **9** mentions | ✓ |
| OSF az52u cross-link present | ≥ 1 mention | **4** mentions | ✓ |
| Document length | ≥ 200 lines | **518 lines** | ✓ |
| 9 Track B traits enumerated | BMI, T2D, stroke, SBP, asthma, CAD, lipids, eGFR, HbA1c | All 9 present in §8.1 inventory table | ✓ |
| 11 methods enumerated | Per Amendment §6 method stack | All 11 + Hail = 12 rows in §4 inventory table | ✓ |
| AoU + NCSU side computation split | Both sides documented | 5 inside-AoU + 5 NCSU-side components in §5 | ✓ |
| Egress wording matches OSF amendment | Paragraph (f) verbatim | Quoted block in §6.1 with `[src: ... OSF-AMENDMENT-TEXT-2026-04-22.md paragraph (f)]` footnote | ✓ |
| 5 novel-variant classes with yields | Class 1–5 with order-of-magnitude estimates | Table in §7 with all 5 classes + ranges | ✓ |
| AFR emphasis rationale | LD-calibration gap + population-composition mismatch | §8.2 with explicit two-reason structure citing AOU-LD-PIPELINE §1 | ✓ |
| PCA-based ancestry framing | Not self-ID gate | §10.1, §10.2 with sensitivity-check protocol | ✓ |
| Nature Genetics + Scientific Data + Zenodo | All three named | §11 expected-publications table | ✓ |

## Where the deliverable lives

[`AOU-WORKBENCH-REGISTRATION.md`](AOU-WORKBENCH-REGISTRATION.md) in this
quick-task directory. Carter pastes section-by-section into the AoU
Researcher Workbench portal at workspace-creation time, trimming each
section to the live portal field character limit. Inline citations let
each claim be cross-checked against the planning artifacts before paste.

## Out-of-scope (not modified)

- AoU portal itself (Carter pastes manually).
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`,
  `.planning/amendments/*` — all cited only, none modified.
- `.planning/DECISIONS.md` — the new Scientific Data venue commitment is
  flagged in §11 of the deliverable as something Carter may want to
  record there; no automatic decision row added by this quick task.
- Track A artifacts (`docs/manuscript/track_a_pivot.md`,
  `src/R/figures/*`, `TRACK-A-FROZEN-NUMBERS.md`,
  `TRACK-A-AUDIT-RESPONSE-2026-04-26.md`) — Track A is explicitly
  omitted; no Track A files were touched.
- Parallel-workstream untracked files (m2-04 mtCOJO scripts, track-a
  repro bundle, AUDIT-REVIEW-V2-2026-04-26.md, etc.) — not staged.

## Forward pointer

When Carter is ready to file the AoU workspace:

1. Open the deliverable: `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`
2. Verify all `[src: ...]` citations resolve (`grep -oE '\[src:[^]]+\]' AOU-WORKBENCH-REGISTRATION.md | sort -u`).
3. Map portal sections to RPS sub-prompts; trim each section to the live character limit.
4. Confirm OSF amendment text for paragraph (f) still matches the deliverable's §6.1 quote (no drift).
5. After workspace approval, file P&P draft registration before any Track B Nature Genetics submission (per AOU-LD-PIPELINE.md §2 P6).
