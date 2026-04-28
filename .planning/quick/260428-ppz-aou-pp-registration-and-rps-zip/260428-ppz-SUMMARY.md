---
phase: quick-260428-ppz
plan: 01
subsystem: track-b-aou-portal
tags:
  - track-b
  - track-b-m3
  - aou-workbench
  - p-and-p-registration
  - rps-registration
  - portal-bundle
  - decisions
dependency_graph:
  requires:
    - quick-260426-aow  # AOU-WORKBENCH-REGISTRATION.md (RPS sub-prompts)
    - .planning/amendments/AOU-LD-PIPELINE.md  # §13 publication policy + §2 P6 + §12 R6
    - .planning/PROJECT.md  # Who / What / Goals / Open human-action items
    - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md  # §3 / §5 / §7 / §9 / §11
  provides:
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/AOU-PP-REGISTRATION.md  # paste-ready P&P doc
    - bin/build_aou_portal_bundle.sh  # deterministic rebuild
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip  # downloadable bundle
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-portal-bundle-build-log.txt
    - DEC-2026-04-28-01  # Sci Data venue commitment for M3 data descriptor
  affects:
    - aou-portal-readiness  # workspace registration + P&P registration both portal-paste-ready
    - track-b-m3-venue  # locked Sci Data via DEC-2026-04-28-01
tech_stack:
  added: []
  patterns:
    - "Self-contained bash builder with mktemp staging + trap cleanup (modeled on quick-260427-vbq)"
    - "Heredoc-generated README with git rev-parse HEAD + ISO-8601 build date interpolated"
    - "Explicit-filename copies (no -r, no directory args) to keep zip scoped to authoritative artifacts"
    - "Post-zip hard-fail asserts on entry count + per-entry presence + unzip -t integrity"
    - "AoU P&P stacked-block format with [src: ...] citation index (mirrors AOU-WORKBENCH-REGISTRATION.md citation discipline)"
key_files:
  created:
    - bin/build_aou_portal_bundle.sh
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/AOU-PP-REGISTRATION.md
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-portal-bundle-build-log.txt
    - .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/260428-ppz-PLAN.md
  modified:
    - .planning/DECISIONS.md  # +DEC-2026-04-28-01 (Sci Data venue commitment)
    - .planning/STATE.md  # +Quick Tasks Completed row + Session Continuity refresh from earlier resume
decisions:
  - "DEC-2026-04-28-01: M3 AoU AFR LD reference panel data descriptor → *Scientific Data*. Five alternatives considered (Genome Research methods note, Bioinformatics applications note, Zenodo-only deposit, defer venue lock until M6, adopted Sci Data). Adopted for FAIR-data alignment + native Zenodo pairing + AoU policy fit."
  - "Two stacked P&P registration blocks (one per anticipated publication: Track B Nature Genetics + M3 Sci Data). Single AOU-PP-REGISTRATION.md file rather than two separate docs — Carter pastes blocks sequentially into the AoU portal, each as its own P&P record."
  - "Bundle README ships INSIDE zip only; repo root remains license-free (matches Track A submission bundle convention from quick-260427-vbq)."
  - "Builder is disjoint from quick-260426-aow source: explicit cp commands read AOU-WORKBENCH-REGISTRATION.md from its existing location at .planning/quick/260426-aow-... rather than copying it into this quick-task dir, so the source-of-truth artifact remains owned by the originating quick task."
metrics:
  duration_seconds: 240
  duration_human: "4.0 min"
  tasks_completed: 4
  files_created: 5
  files_modified: 2
  zip_size_bytes: 23552
  zip_size_kb: 23
  zip_entry_count: 4   # 1 dir + 3 files
  zip_md_files: 3
  completed_date: "2026-04-28"
---

# Phase quick-260428-ppz Plan 01: AoU P&P Registration + RPS Zip Summary

Built the All of Us Researcher Workbench portal-paste bundle as a 23 KB zip
(3 Markdown files inside `aou_portal_bundle/`) plus a deterministic bash
builder, locked the *Scientific Data* venue for the M3 data descriptor in
DECISIONS.md, and closed out across 3 atomic feature commits + 1 docs
close-out commit.

## What was built

### `.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/AOU-PP-REGISTRATION.md` (Task 1, commit `55af8fa`)

Paste-ready Markdown for the AoU P&P portal. Two stacked registration blocks
(one per anticipated publication):

- **Block 1 — Track B → *Nature Genetics*** — 18 sub-sections covering
  title, authors, venue, anticipated submission date, workspace, AoU CDR
  release version (TODO at workspace setup), AoU tier (Controlled), plain-
  language lay summary, methods summary using AoU data, anticipated findings
  (5 novel-variant classes), demographics/ancestry usage, race/ethnicity
  reporting plan, required AoU citation, AoU acknowledgments boilerplate,
  Zenodo-anchored data availability statement, cell suppression / egress
  statement, OSF pre-registration cross-reference (osf.io/pvb5j +
  osf.io/az52u), submission readiness checklist.

- **Block 2 — M3 → *Scientific Data*** — same 18-sub-section structure
  scoped to the data descriptor publication. Methods summary cross-references
  Block 1; findings sub-section is reframed as resource artifacts +
  validation findings (per AOU-LD-PIPELINE.md §9 Checks 1–4) rather than
  discovery claims.

Top-of-file paste-time-trim note (AoU portal field char limits vary).
Source-citation index appendix tabulates every cited authoritative artifact
(PROJECT.md, Amendment, AOU-LD-PIPELINE.md §13, AOU-WORKBENCH-REGISTRATION.md,
DECISIONS.md). 22,225 bytes (Markdown source) inside the zip.

### `.planning/DECISIONS.md` — DEC-2026-04-28-01 (Task 2, commit `55af8fa`)

Locks ***Scientific Data*** as the M3 venue. Five alternatives considered
((a) Sci Data adopted, (b) Genome Research methods note rejected, (c)
Bioinformatics applications note rejected, (d) Zenodo-only deposit rejected,
(e) defer venue lock rejected). Why: FAIR-data alignment + native Zenodo
pairing + AoU policy fit + complementary (not competitive) with Track B
Nature Genetics. How-to-apply: Track B Methods + Data Availability cite the
Sci Data deposit; AOU-WORKBENCH-REGISTRATION.md §11 already named Sci Data
at registration-build time and is now locked here; future communications
frame M3 as "data descriptor" with Sci Data as named venue; M3 phase
artifacts structure per-region resource table + validation memo + Zenodo
checksum table to match Sci Data data-descriptor template at submission.

### `bin/build_aou_portal_bundle.sh` (Task 3, commit `6e094c7`)

Self-contained bash builder modeled on `bin/build_track_a_submission_bundle.sh`.
Highlights:

- `set -euo pipefail` + `set -x` — every command echoed into the build log.
- Pre-flight asserts on both source files; hard-fail with `exit 2` if
  missing.
- Stages everything under `mktemp -d` with `trap`-cleanup so a failed run
  leaves no residue.
- Generates `README.md` from heredoc with `git rev-parse HEAD` + ISO-8601
  UTC build date interpolated (every rebuild is self-identifying).
- Copies the two source `.md` files by **explicit filename**, never by
  directory recursion — keeps the zip disjoint from anything else.
- Post-zip verification: exact-equal assert on `.md` entry count (3),
  per-entry presence loop (`unzip -l ... | grep -q ...` per expected path),
  and `unzip -t` integrity check. Hard-fails on any miss.

### Bundle deliverables (Task 3, commit `6e094c7`)

- `.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip` — 23,552 bytes (23 KB), 4 zip entries (1 dir + 3 files; 3 .md content files), `unzip -t` clean.
- `.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-portal-bundle-build-log.txt` — full `set -x` trace + `EXIT_CODE=0`.

Zip contents:
```
aou_portal_bundle/
  AOU-WORKBENCH-REGISTRATION.md  (36,992 bytes — RPS sub-prompts; from quick-260426-aow)
  AOU-PP-REGISTRATION.md         (22,225 bytes — Track B + M3 P&P blocks; from this task)
  README.md                      ( 2,772 bytes — paste-order + lock-time TODOs + provenance)
```

## Atomic commits

| Task | Commit    | Message                                                                                                              |
| ---- | --------- | -------------------------------------------------------------------------------------------------------------------- |
| 1+2  | `55af8fa` | feat(track-b): add AoU P&P registration paste-ready doc + record DEC-2026-04-28-01 Sci Data venue (quick-260428-ppz) |
| 3    | `6e094c7` | feat(track-b): add AoU portal bundle builder + assemble RPS+P&P zip (quick-260428-ppz)                              |
| 4    | (this)    | docs(quick-260428-ppz): close AoU P&P registration + RPS zip task — STATE row + SUMMARY                              |

Tasks 1+2 batched into a single commit because the P&P registration block 2
materially depends on the Sci Data venue commitment in DEC-2026-04-28-01;
landing them separately would leave a transient state where the doc cites a
decision that doesn't yet exist in DECISIONS.md.

## Disjoint-scope verification

```
git log -3 --name-only | grep -E '(\.claude/settings\.json|\.planning/config\.json|\.claude/scheduled_tasks\.lock|\.planning/phases/m3-aou-afr-ld-panel-build/)' && echo VIOLATION || echo OK
# Expected: OK
```

Terminal A's m3-phase work landed at commits `4195ca0` (RESEARCH) + `27b0267`
(VALIDATION) **between** the resume read at the top of this session and this
quick task's first commit. Those commits are disjoint with this task's
working set (this task touches only `bin/`, `.planning/DECISIONS.md`,
`.planning/STATE.md`, and `.planning/quick/260428-ppz-...`); no path overlap.

## Pre-existing dirty paths preserved

Per the project's rolling preserved-state convention, the following 3 paths
must remain dirty/untracked and were never staged:

| Path                              | Pre-status    | Post-status   | Touched? |
| --------------------------------- | ------------- | ------------- | -------- |
| `.claude/settings.json`           | ` M` modified | ` M` modified | No       |
| `.planning/config.json`           | ` M` modified | ` M` modified | No       |
| `.claude/scheduled_tasks.lock`    | `??` untracked| `??` untracked| No       |

`.planning/STATE.md` was modified before this task started (resume-session
refresh). The Quick Tasks Completed row append in this Task 4 commit is the
natural close-out vehicle for that pre-existing modification, satisfying the
"Session Continuity must commit" convention without an extra atomic commit.

## ORCID-as-TODO disposition (carried forward)

Same TODO placeholder as the Track A submission bundle (quick-260427-vbq).
ORCID lives at:

1. `aou_portal_bundle/AOU-PP-REGISTRATION.md` §1.2 (Track B authors table)
2. `aou_portal_bundle/AOU-PP-REGISTRATION.md` §2.2 (Sci Data authors table)

Carter populates both before any external submission. Re-running
`bin/build_aou_portal_bundle.sh` after editing the source `.md` regenerates
the zip with the populated ORCID.

## Reproducibility

Carter can regenerate the exact bundle from a clean checkout with:

```bash
git clone <repo-url> coloc_analysis
cd coloc_analysis
bin/build_aou_portal_bundle.sh
# zip lands at .planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/
#   aou-rps-and-pp-registration.zip
```

The bundle's `README.md` interpolates the source commit (`git rev-parse HEAD`
at build time) so each rebuild is self-identifying.

## Self-Check: PASSED

- [x] `bin/build_aou_portal_bundle.sh` exists, executable, passes `bash -n`.
- [x] `aou-rps-and-pp-registration.zip` exists at canonical path (23 KB).
- [x] `aou-portal-bundle-build-log.txt` exists, captures full `set -x` trace + `EXIT_CODE=0`.
- [x] Zip contains exactly 3 `.md` files: AOU-WORKBENCH-REGISTRATION.md, AOU-PP-REGISTRATION.md, README.md (per `unzip -l`).
- [x] `unzip -t` integrity check: no errors detected.
- [x] DECISIONS.md contains DEC-2026-04-28-01 with full alternatives + Why + How-to-apply.
- [x] AOU-PP-REGISTRATION.md contains both Block 1 (Track B Nature Genetics) and Block 2 (M3 Sci Data) headers + 18 sub-sections each + appendix citation index.
- [x] 3 atomic feature commits + 1 docs close-out commit (this commit) — atomic discipline maintained.
- [x] No path under `.planning/phases/m3-aou-afr-ld-panel-build/` staged or committed by this task.
- [x] 3 must-not-touch paths preserved exactly as pre-spawn.
- [x] Builder script's source-file paths point to the canonical quick-260426-aow location for AOU-WORKBENCH-REGISTRATION.md (no copy-into-this-task convention; source-of-truth ownership preserved).

## Carrier-pigeon items for Carter

- **Pull down the zip locally** at `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260428-ppz-aou-pp-registration-and-rps-zip/aou-rps-and-pp-registration.zip` (use `scp` / `rsync` from local).
- **Paste order:** workspace registration first (RPS), then both P&P blocks at draft stage. Workspace must be approved before P&P record references the workspace.
- **Lock at workspace setup:** AoU CDR Release Version → populates `AOU-PP-REGISTRATION.md` §1.6 / §2.6.
- **Lock before submission:** ORCID → populates `AOU-PP-REGISTRATION.md` §1.2 / §2.2 + Track A `CITATION.cff` (separate zip from quick-260427-vbq).
- **Update the P&P record at every major scope change** per AOU-LD-PIPELINE.md §12 R6.
- **Re-verify AoU citation + acknowledgment language** ≤ 1 week before each submission per AOU-LD-PIPELINE.md §12 R11.
