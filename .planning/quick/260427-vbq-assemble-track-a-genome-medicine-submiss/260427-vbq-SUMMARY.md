---
phase: quick-260427-vbq
plan: 01
subsystem: track-a-submission
tags:
  - track-a
  - submission-bundle
  - genome-medicine
  - reproducibility
dependency_graph:
  requires:
    - quick-260427-urj  # venue-lock to Genome Medicine (commit b4f216e)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    - docs/manuscript/track_a_pivot.md
    - docs/manuscript/figures/  # 14 files
    - results/track_a_aggregations/  # 9 TSVs
    - src/R/aggregators/  # 3 files
    - src/R/figures/  # 7 files
    - src/python/aggregate_{coloc_manifest_errors,pathway_results,qtl_coloc}.py
  provides:
    - bin/build_track_a_submission_bundle.sh  # deterministic rebuild
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
  affects:
    - track-a-submission-readiness  # bundle is now ready for journal portal upload
tech_stack:
  added: []
  patterns:
    - "Self-contained bash builder with mktemp staging dir + trap-cleanup"
    - "Pandoc PDF-engine fallback chain (xelatex -> lualatex -> pdflatex -> tectonic -> weasyprint -> HTML)"
    - "Heredoc-generated bundle metadata (README, LICENSE-CODE, LICENSE-MANUSCRIPT-AND-DATA, CITATION.cff)"
    - "Explicit-filename copy lists (no recursive directory copies) to keep Track B legacy out"
    - "In-script post-zip count verification with exact-equal asserts"
key_files:
  created:
    - bin/build_track_a_submission_bundle.sh
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt
  modified: []
decisions:
  - "Render path = HTML fallback (no PDF engine on host); build script tries xelatex/lualatex/pdflatex/tectonic/weasyprint and emits clear log lines for each before falling back. .md source ships alongside the .html so reviewers always have both."
  - "License split: MIT for code (scripts/) + CC-BY-4.0 for manuscript+data (manuscript/, figures/, supplementary/). Both license files live INSIDE the zip only — repo root remains license-free, matching the existing repo state."
  - "ORCID kept as TODO placeholder in CITATION.cff and README.md author section. Carter to fill before journal portal upload (flagged below)."
  - "Bundle version pinned to source commit SHA via git rev-parse HEAD interpolated into README.md at build time, so each rebuild is self-identifying."
metrics:
  duration_seconds: 181
  duration_human: "3.0 min"
  tasks_completed: 2
  files_created: 3
  zip_size_bytes: 4388699
  zip_size_mb: 4.19
  zip_entry_count: 53
  completed_date: "2026-04-28"
---

# Phase quick-260427-vbq Plan 01: Track A Genome Medicine Submission Bundle Summary

Assembled the Track A *Genome Medicine* submission bundle as a single 4.19 MB
zip (53 entries) plus a deterministic bash builder, landing in two atomic
commits with all forbidden-path and disjoint-scope guards honored.

## What was built

### bin/build_track_a_submission_bundle.sh (Task 1, commit `0328db9`)

A 488-line, self-contained bash builder. Highlights:

- `set -euo pipefail` + `set -x` — every command echoed into the build log.
- Locates pandoc at the hard-coded conda path
  (`/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc`),
  with `command -v pandoc` and a hard-fail message as fallbacks.
- Tries 5 PDF engines in order (`xelatex`, `lualatex`, `pdflatex`, `tectonic`,
  `weasyprint`) — each gated by `command -v` so missing binaries are skipped
  silently. On exhaustion, falls back to pandoc HTML rendering with a
  ~30-line `minimal.css` shipped via heredoc next to the HTML.
- Stages everything under `mktemp -d` with `trap`-cleanup so a failed run
  leaves no residue.
- Generates `README.md`, `LICENSE-CODE` (MIT), `LICENSE-MANUSCRIPT-AND-DATA`
  (CC-BY-4.0), and `CITATION.cff` from in-script heredocs — no separate
  template files.
- Copies all 14 figures, all 10 supplementary files (9 TSV + 1 .md),
  and all 13 scripts (3 R aggregators + 7 R figure builders + 3 Python
  aggregators) by **explicit filename**, never by directory recursion. This
  is the safety belt that keeps Track B (`src/legacy/`, `m2_*`, `m3_*`,
  `aggregate_genomewide_results.py`) out of the bundle.
- Post-zip verification asserts exact file counts (figures=14,
  supplementary=10, scripts=13 split 3/7/3) plus presence of all four
  root metadata files and the rendered manuscript. Hard-fails on any miss.

### Bundle deliverables (Task 2, commit `cd46e5d`)

- `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip` — 4,388,699 bytes (4.19 MB), 53 entries, integrity-tested with `unzip -t` (no errors).
- `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/build_log.txt` — full `set -x` trace plus `EXIT_CODE=0` footer.

## Render-path decision (PDF vs HTML)

**Outcome:** HTML fallback (`html:pandoc-fallback`).

**Evidence from `build_log.txt`:**

```
[INFO] No PDF engine available; rendering HTML fallback.
[INFO] PDF engines tried:
+ /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc docs/manuscript/track_a_pivot.md \
    -o .../manuscript/track_a_pivot.html --standalone --toc \
    --metadata 'title=Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci' \
    --css=minimal.css
[INFO] Manuscript render path: html:pandoc-fallback
```

**Engines tried (all unavailable on this host):** `xelatex`, `lualatex`,
`pdflatex`, `tectonic`, `weasyprint`. The orchestrator confirmed pre-spawn
that none are installed, and the build script logged the same (verifying via
`command -v` rather than just trusting prior context).

**What ships in the zip:**
- `manuscript/track_a_pivot.md` (source — always)
- `manuscript/track_a_pivot.html` (rendered with TOC + serif CSS)
- `manuscript/minimal.css` (~30 lines, readable defaults)

**Implication for journal upload:** Genome Medicine accepts .docx/.pdf/.tex
manuscript uploads, not raw .html. Carter will need to render a PDF separately
(via Word/LaTeX) at portal-upload time, or install one of the PDF engines
locally and re-run `bin/build_track_a_submission_bundle.sh` to regenerate the
zip with a real `track_a_pivot.pdf`. The .md source in the bundle is the
authoritative copy regardless.

## Final zip metrics

- **Path:** `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/track_a_genome_medicine_submission.zip`
- **Size:** 4,388,699 bytes (4.19 MB) — well under the plan's 50 MB cap.
- **Entries:** 53 total (44 files + 9 directory entries).
- **File breakdown:**
  - 4 root metadata files (`README.md`, `LICENSE-CODE`, `LICENSE-MANUSCRIPT-AND-DATA`, `CITATION.cff`)
  - 3 manuscript files (`track_a_pivot.md`, `track_a_pivot.html`, `minimal.css`)
  - 14 figure files (7 builders × {pdf, png})
  - 10 supplementary files (9 TSV + `TRACK-A-FROZEN-NUMBERS.md`)
  - 13 scripts (3 R aggregators + 7 R figure builders + 3 Python aggregators)
- **Integrity:** `unzip -t` returns "No errors detected".

## License choices

| Scope                         | License        | File                          | Rationale                                                                                                                              |
| ----------------------------- | -------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Code (`scripts/` subtree)     | MIT            | LICENSE-CODE                  | Permissive, OSI-approved, near-universal in computational genomics. Lets reviewers/readers reuse the aggregators without restriction.  |
| Manuscript + figures + tables | CC-BY-4.0      | LICENSE-MANUSCRIPT-AND-DATA   | Standard open-access license for academic manuscripts; required-or-recommended by most preprint servers and many journals' OA policies. |

**Repo-root scope:** No `LICENSE` was added at the repo root — both license
files exist *only inside the bundle zip*. The repo's existing license-free
state is preserved (orchestrator confirmed pre-flight: "NO existing LICENSE
file at repo root; bundle ships MIT (code) + CC-BY-4.0 (manuscript+data)
INSIDE zip only").

## ORCID-as-TODO disposition

**Placeholder locations** (Carter to fill before journal portal upload):

1. `track_a_genome_medicine_submission/CITATION.cff`:
   ```yaml
   orcid: "TODO"  # placeholder — replace before submission
   ```
2. `track_a_genome_medicine_submission/README.md`, "Author" section:
   `Carter K. Clinton — NCSU ASHES Lab — ORCID: TODO (placeholder).`

To fix: edit either `bin/build_track_a_submission_bundle.sh` (replacing both
`TODO` strings in the heredocs with the real ORCID identifier) and re-run
the script, or post-edit the extracted bundle by hand. Re-running the script
is preferred to keep regenerable parity.

## Pre-existing dirty paths preserved

Per constraint, the following 3 paths must remain dirty/untracked across both
commits and were never staged. Confirmed post-commit via `git status --porcelain`:

| Path                              | Pre-status    | Post-status   | Touched? |
| --------------------------------- | ------------- | ------------- | -------- |
| `.claude/settings.json`           | ` M` modified | ` M` modified | No       |
| `.planning/config.json`           | ` M` modified | ` M` modified | No       |
| `.claude/scheduled_tasks.lock`    | `??` untracked| `??` untracked| No       |

**Disjoint scope:** Nothing under `.planning/phases/m3-aou-afr-ld-panel-build/`
was staged or committed by this executor. Terminal A appears to have committed
that directory in parallel during this run (it transitioned from untracked to
tracked between Task 1 staging and final status), which is expected and
unrelated.

## Self-check (`git status --porcelain` post-Task 2)

```
 M .claude/settings.json
 M .planning/config.json
?? .claude/scheduled_tasks.lock
?? .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/260427-vbq-PLAN.md
```

**Reading:**
- 3 of 3 must-not-touch paths preserved exactly as found (✓).
- 1 extra line: `260427-vbq-PLAN.md` — the plan file itself, intentionally
  left untracked because the executor's constraints explicitly say "Do NOT
  commit docs artifacts (SUMMARY.md, STATE.md, PLAN.md) — the orchestrator
  handles the docs commit in Step 8." This is the expected hand-off state.

No unexpected paths surfaced.

## Forbidden-path guard on commits

```
git log -2 --name-only | grep -E '(\.claude/settings\.json|\.planning/config\.json|\.claude/scheduled_tasks\.lock|\.planning/phases/m3-aou-afr-ld-panel-build/)' && echo VIOLATION || echo OK
# Output: OK — no forbidden paths in last 2 commits
```

## Atomic commits

| Task | Commit    | Message                                                                                |
| ---- | --------- | -------------------------------------------------------------------------------------- |
| 1    | `0328db9` | feat(track-a): add Genome Medicine submission bundle build script (quick-260427-vbq)   |
| 2    | `cd46e5d` | feat(track-a): assemble Genome Medicine submission bundle zip (quick-260427-vbq)       |

Each commit was staged with explicit `git add <path>` per file (no `-A`,
no `.`, no `-u`, no directory args). `git status --porcelain` was checked
before each commit and contained only the task-scoped paths plus the
preserved must-not-touch lines.

## Deviations from Plan

**None.** Plan executed exactly as written. The only "branch" exercised was
the documented PDF→HTML fallback, which is part of the plan's explicit design
(not a deviation).

## Reproducibility

Carter can regenerate the exact bundle from a clean checkout with:

```bash
git clone https://github.com/carter-clinton/coloc_analysis.git
cd coloc_analysis
bin/build_track_a_submission_bundle.sh
# zip lands at .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/
#   track_a_genome_medicine_submission.zip
```

To produce a PDF-rendered bundle, install one of {xelatex, lualatex, pdflatex,
tectonic, weasyprint} on the build host first; the script auto-detects and
prefers PDF over HTML when any engine is present.

## Self-Check: PASSED

- [x] `bin/build_track_a_submission_bundle.sh` exists, executable, passes `bash -n`.
- [x] `track_a_genome_medicine_submission.zip` exists at canonical path (4.19 MB).
- [x] `build_log.txt` exists, captures full `set -x` trace + EXIT_CODE=0.
- [x] Zip contains exactly 14 figures, 10 supplementary, 13 scripts, all 4 root metadata files, both manuscript .md + .html.
- [x] `unzip -t` integrity check: no errors detected.
- [x] Two atomic commits landed (`0328db9`, `cd46e5d`).
- [x] No forbidden path staged/committed (verified via `git log -2 --name-only` grep).
- [x] 3 must-not-touch paths preserved exactly as pre-spawn.
- [x] No path under `.planning/phases/m3-aou-afr-ld-panel-build/` staged/committed by this executor.
- [x] Track B legacy code (`src/legacy/`, `aggregate_genomewide_results.py`, `m2_*`, `m3_*`) NOT in zip.
