# Quick Task 260428-ppz — AoU P&P Registration + RPS Zip

**Slug:** 260428-ppz-aou-pp-registration-and-rps-zip
**Date:** 2026-04-28
**Author:** Carter K. Clinton (Claude orchestrated)
**Status:** in flight

## Context

Carter accepted the *Scientific Data* venue commitment (flagged during quick-260426-aow build) for the M3 AoU AFR LD panel data descriptor and OK'd both OSF cross-links rendering in the AoU portal. He directed P&P registration and a downloadable zip of the AoU portal-paste artifacts.

Two distinct AoU Publications & Presentations (P&P) registrations are needed before any submission per AOU-LD-PIPELINE.md §2 P6 + §12 R6:

1. **Track B — *Nature Genetics*** — full 9-trait × 2-ancestry joint-signal discovery paper.
2. **M3 — *Scientific Data*** — data descriptor for the AoU-derived AFR LD reference panels (newly committed venue per Carter 2026-04-28).

Both registrations are filed at draft stage and updated at major scope changes per AoU policy. Registration is a Carter web-UI action; this task produces paste-ready Markdown.

## Tasks

### Task 1: Build paste-ready AOU-PP-REGISTRATION.md

Two stacked P&P registration blocks (one per anticipated publication) covering all standard AoU P&P portal fields:

- Publication / Presentation Title
- Authors + ORCIDs + affiliations
- Anticipated Journal / Venue + Submission Date
- Workspace(s) Used (cross-link AOU-WORKBENCH-REGISTRATION.md)
- AoU CDR Release Version (placeholder — Carter to lock at submission)
- AoU Tier (Controlled)
- Plain-language Abstract / Lay Summary
- Methods Summary using AoU data
- Anticipated Findings
- Demographics / Ancestry usage statement
- Race / Ethnicity reporting plan (PCA-based, not self-ID)
- Required AoU citation (verbatim from AOU-LD-PIPELINE §13.3)
- Acknowledgments boilerplate (verbatim from AOU-LD-PIPELINE §13.2 with verify-at-submission flag)
- Data Availability Statement (Zenodo deposit per §13.4)
- Cell suppression statement (no <20 cells; summary-only egress)
- Submission Readiness Checklist

Each block is portal-paste-ready Markdown with explicit `[src: ...]` citations to authoritative artifacts (PROJECT.md, Amendment §3/§7/§11, AOU-LD-PIPELINE.md §13, AOU-WORKBENCH-REGISTRATION.md). Top-of-file paste-time-trim note since AoU portal field char limits vary.

**Commit:** `feat(track-b): add AoU P&P registration paste-ready doc (Track B + M3 Sci Data; quick-260428-ppz)` — file path: `.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/AOU-PP-REGISTRATION.md`

### Task 2: Log DEC-2026-04-28-01 (Sci Data venue commitment)

Append to `.planning/DECISIONS.md`:

- Decision: M3 AoU AFR LD reference panel data descriptor will be submitted to *Scientific Data*.
- Alternatives: *Genome Research* methods note, *Bioinformatics* applications note, Zenodo-only deposit (no peer review).
- Why: Sci Data is the canonical venue for genomic resource data descriptors; pairs with Zenodo deposit; satisfies AoU publication policy; complementary to Track B *Nature Genetics* without competing.
- How to apply: All future Track B/M3 communications cite Sci Data as the M3 deliverable venue. P&P registration block 2 in this task uses Sci Data verbatim.

**Commit:** `docs(decisions): record DEC-2026-04-28-01 — M3 Sci Data data-descriptor venue commitment (quick-260428-ppz)`

### Task 3: Assemble downloadable zip

Build `aou-rps-and-pp-registration.zip` containing:

- `AOU-WORKBENCH-REGISTRATION.md` (from quick-260426-aow; the 13-section RPS sub-prompts)
- `AOU-PP-REGISTRATION.md` (this task's deliverable)
- `README.md` (brief explainer: what's in here, paste order, lock-time decisions)

Builder script: `bin/build_aou_portal_bundle.sh` (modeled on `bin/build_track_a_submission_bundle.sh`). Self-contained bash; mktemp staging + trap cleanup; explicit-filename copies; post-zip count verification with hard-fail asserts. Zip lands at `.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip`.

**Commit:** `feat(track-b): add AoU portal bundle builder + assemble RPS+P&P zip (quick-260428-ppz)`

### Task 4: Close out

- Append STATE.md row for this quick task (Quick Tasks Completed table).
- Write SUMMARY.md per close-out template.
- Final commit: `docs(quick-260428-ppz): close AoU P&P registration + RPS zip task — STATE row + SUMMARY`.

## Constraints

- **Disjoint scope:** Do NOT touch `.planning/phases/m3-aou-afr-ld-panel-build/` (Terminal A active there).
- **Pre-existing dirty paths to preserve:** `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`. These must remain dirty/untracked across all commits. Note: `.planning/STATE.md` is also currently modified (resume-session refresh) — this task's STATE.md row append is the natural close-out commit for it.
- **No LSF, no data egress, no portal action.** Pure docs + bash bundler.
- **Atomic commits:** explicit `git add <path>` per file (no `-A`, no `.`, no `-u`, no directory args).
- **All artifacts referenced by `[src: ...]` citations.** Every claim in AOU-PP-REGISTRATION.md must trace to PROJECT.md / Amendment / AOU-LD-PIPELINE.md / AOU-WORKBENCH-REGISTRATION.md.
- **Carter web-UI actions remain as TODOs** in the deliverable. AoU portal P&P submission, OSF amendment posting, ORCID lookup are all flagged but not auto-completed.

## Verification gates

1. `AOU-PP-REGISTRATION.md` exists and contains both Track B and M3 P&P blocks.
2. `bin/build_aou_portal_bundle.sh` exists, executable, passes `bash -n`.
3. `aou-rps-and-pp-registration.zip` exists at canonical path; contains exactly 3 files (RPS, P&P, README).
4. `unzip -t` returns "No errors detected".
5. DECISIONS.md contains DEC-2026-04-28-01 with full alternatives + Why + How-to-apply.
6. STATE.md Quick Tasks Completed table contains a row for this task.
7. No path under `.planning/phases/m3-aou-afr-ld-panel-build/` staged or committed.
8. No forbidden paths committed (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`).
