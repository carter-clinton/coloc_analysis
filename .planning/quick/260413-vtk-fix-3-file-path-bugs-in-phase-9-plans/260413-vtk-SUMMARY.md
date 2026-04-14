---
phase: quick-260413-vtk
plan: 01
subsystem: planning-artifacts
tags: [phase9, planning, bugfix, path-correction]
dependency_graph:
  requires:
    - Phase 9 plan files (09-01, 09-03, 09-05) post checker iter-1
    - Ground truth verified by ls/grep at plan time (2026-04-13)
  provides:
    - Corrected Phase 9 plan files with real file paths
    - Accurate Phase 1 architecture description for Phase 9 executors to reuse
    - Dependency wiring from Phase 9 COJO to Phase 5 LDSC download
  affects:
    - Phase 9 Plan 01, 03, 05 execution
    - 09-RESEARCH.md stale snippet
tech_stack:
  added: []
  patterns:
    - "Phase 9 Snakefile include directives now match existing convention (full path, project-root Snakefile)"
    - "Phase 9 LD reference path wires through Phase 5 pathway.smk download_ldsc_baseline (no duplicate download rule)"
key_files:
  created:
    - .planning/quick/260413-vtk-fix-3-file-path-bugs-in-phase-9-plans/260413-vtk-SUMMARY.md
  modified:
    - .planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md
    - .planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md
    - .planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md
    - .planning/phases/09-replication-in-independent-cohorts/09-RESEARCH.md
decisions:
  - "Scrub 09-RESEARCH.md line 540 stale COJO snippet alongside 09-05 fixes (research doc paths get copy-pasted into code by executors)"
  - "Add explicit ldsc_flag dependency (data/reference/ldsc/.download_ldsc_baseline.done) to rule run_cojo_slct input block; exact flag filename must be verified at execute time vs pathway.smk"
  - "Do NOT invent new download rule for 1000G PLINK files — Phase 5 pathway.smk download_ldsc_baseline already produces them"
metrics:
  duration: ~10min
  completed: 2026-04-13
---

# Phase quick-260413-vtk Plan 01: Fix 3 File Path Bugs in Phase 9 Plans Summary

Quick task — corrected 3 pre-existing-file-reality mismatches in Phase 9 planning artifacts surfaced by the orchestrator pre-execution scan. Plan document text edits only; no code changes, no new rules, no config changes.

## Scope

Three bugs fixed across four files:

- **BUG-1 (09-01-PLAN.md):** References to nonexistent `src/snakemake/Snakefile`; actual Snakefile is at project root. Also fixed short-form `include: "rules/replication.smk"` to match existing full-path convention.
- **BUG-2 (09-03-PLAN.md):** References to nonexistent `src/snakemake/scripts/run_susie_rss.R`; real Phase 1 entry point is `src/legacy/region_analysis/scripts/run_susie_rss.R` invoked via shell from `src/snakemake/rules/finemap.smk:79`.
- **BUG-3 (09-05-PLAN.md + 09-RESEARCH.md):** References to nonexistent `data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed`; real post-download path is `data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{EUR|AFR}.QC.{chrom}.{bed,bim,fam}` produced by Phase 5 `pathway.smk` rule `download_ldsc_baseline`.

## Changes Applied

### Task 1 — BUG-1 in 09-01-PLAN.md (commit 8264ca5)

7 edits, 7 insertions / 7 deletions:

| Line (approx) | Location | Change |
|---------------|----------|--------|
| 12 | `files_modified` | `src/snakemake/Snakefile` → `Snakefile` |
| 54 | `key_links.from` | `"src/snakemake/Snakefile"` → `"Snakefile"` |
| 300 | Task 2 `<files>` | `src/snakemake/Snakefile` → `Snakefile` |
| 304 | Task 2 `<read_first>` | `src/snakemake/Snakefile (top-level; ...)` → `Snakefile (project root top-level; ... uses full paths like include: "src/snakemake/rules/pathway.smk")` |
| 481 | Task 2 Step 4 action | `Edit src/snakemake/Snakefile to ADD include: "rules/replication.smk"` → `Edit Snakefile (project root) to ADD include: "src/snakemake/rules/replication.smk" ... match that convention` |
| 486 | Task 2 `<automated>` grep | `grep -q 'include: "rules/replication.smk"' src/snakemake/Snakefile` → `grep -q 'include: "src/snakemake/rules/replication.smk"' Snakefile` |
| 495 | Task 2 `<done>` bullet | `Snakefile includes rules/replication.smk` → `Snakefile (project root) includes "src/snakemake/rules/replication.smk" (full path, matching existing convention)` |

### Task 2 — BUG-2 + BUG-3 + 09-RESEARCH scrub (commit ea9ddd2)

**09-03-PLAN.md** (3 edits):

| Line | Change |
|------|--------|
| 71 | `@src/snakemake/scripts/run_susie_rss.R` → `@src/legacy/region_analysis/scripts/run_susie_rss.R` |
| 86-90 | Interfaces block: invented `source_susie_policy()` helper replaced with accurate description of real Phase 1 architecture (finemap.smk shells to legacy script at line 79; inline `yaml::read_yaml` pattern) |
| 353 | read_first: `src/snakemake/scripts/run_susie_rss.R (Phase 1 — reuse runsusie pattern, retry ladder, policy loader)` → `src/legacy/region_analysis/scripts/run_susie_rss.R (Phase 1 legacy — real runsusie entry point; retry ladder + policy loading live inline, no helper function)` |

**09-05-PLAN.md** (5 edits):

| Line | Change |
|------|--------|
| 54-57 | `key_links` entry: `data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed` → `data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{EUR\|AFR}.QC.{chrom}.bed`; via clause now references Phase 5 `download_ldsc_baseline` |
| 111 | Task 2 `<read_first>`: documented dependency on Phase 5 `pathway.smk` rule `download_ldsc_baseline`; explicit "DO NOT add a new download rule" |
| 158 | Shell script comment example: `data/processed/ld_reference/1kg_eur/chr10` → `data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.10` |
| 244 | Rule `run_cojo_slct` input: path fix + new sibling `ldsc_flag = "data/reference/ldsc/.download_ldsc_baseline.done"` |
| ~266 | Inserted wildcard_constraints note before Step 5: `{ancestry}` must be upper-case (EUR\|AFR); flag path must be verified vs pathway.smk at execute time |

**09-RESEARCH.md** (1 edit):

| Line | Change |
|------|--------|
| 540 | `gcta --bfile data/processed/ld_reference/1kg_EUR/chr${CHR} \` → `gcta --bfile data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.${CHR} \` |

## Verification

### Residual grep sweep (final)

```
=== BUG-1 residual (src/snakemake/Snakefile) ===
clean
=== BUG-2 residual (src/snakemake/scripts/run_susie_rss.R) ===
clean
=== BUG-3 residual (data/processed/ld_reference/1kg_) ===
clean
=== Short-form include residual ===
clean
```

All four zero-match constraints satisfied.

### Corrected-path presence (count)

```
.planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md: 4 matches
.planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md: 7 matches
.planning/phases/09-replication-in-independent-cohorts/09-RESEARCH.md: 1 match
.planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md: 2 matches
```

Union pattern: `src/legacy/region_analysis/scripts/run_susie_rss.R|1000G_Phase3_plinkfiles|download_ldsc_baseline|include: "src/snakemake/rules/replication.smk"`.

### Success criteria check

- [x] BUG-1 applied in 09-01 (7 sites patched)
- [x] BUG-2 applied in 09-03 (3 sites patched; interfaces block fully rewritten)
- [x] BUG-3 applied in 09-05 (5 sites patched; new ldsc_flag input + wildcard note added)
- [x] 09-RESEARCH.md line 540 scrubbed
- [x] Zero grep hits for the three old paths + short-form include
- [x] Corrected paths present in all expected files
- [x] rule `run_cojo_slct` declares dependency on Phase 5 `download_ldsc_baseline` flag file (no new download rule invented)
- [x] No code changes, no new rules, no config changes — plan documents only

## Deviations from Plan

None — plan executed exactly as written.

One observation worth recording for future plan checkers: the plan's `replace_all=false` edit for the first `- src/snakemake/Snakefile` occurrence initially matched 2 sites in 09-01-PLAN.md; I performed the second match via `replace_all=true` after confirming only one residual occurrence remained (the other had already been replaced). Net result identical to plan intent.

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | `8264ca5` | fix(quick-260413-vtk-01): correct Snakefile path + include directive in 09-01-PLAN.md |
| 2 | `ea9ddd2` | fix(quick-260413-vtk-01): correct run_susie_rss.R path + LD reference paths in Phase 9 plans |

## Self-Check: PASSED

- Created file: `.planning/quick/260413-vtk-fix-3-file-path-bugs-in-phase-9-plans/260413-vtk-SUMMARY.md` — FOUND
- Commit `8264ca5` — FOUND
- Commit `ea9ddd2` — FOUND
- All four residual-grep checks print `clean`
- All four corrected-path groups present across expected files
