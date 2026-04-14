---
phase: quick-260414-rbv
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/snakemake/rules/pathway.smk
autonomous: true
requirements:
  - QUICK-260414-rbv
user_setup: []

must_haves:
  truths:
    - "Snakemake resolves conda env paths for MAGMA/LDSC/HESS/g:Profiler rules to actual files inside project_root/envs/"
    - "`snakemake all_pathway --dry-run` still resolves to 575 jobs (no regression from quick task 260414-qsk)"
    - "`snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda` produces a clean DAG (no WorkflowError on env path)"
  artifacts:
    - path: "src/snakemake/rules/pathway.smk"
      provides: "Corrected ENV constants for MAGMA, LDSC, HESS, g:Profiler using Path(workflow.basedir)/'envs'/X.yml pattern"
      contains: "Path(workflow.basedir)"
  key_links:
    - from: "src/snakemake/rules/pathway.smk"
      to: "envs/{magma,ldsc_py3,hess_py27,gprofiler}.yml"
      via: "MAGMA_ENV / LDSC_ENV / HESS_ENV / GPROFILER_ENV string assignments"
      pattern: "Path\\(workflow\\.basedir\\) / \"envs\" / \".*\\.yml\""
---

<objective>
Fix a latent conda env path bug in `src/snakemake/rules/pathway.smk` (lines 58-61) that computes
`workflow.basedir + ../../../envs/*.yml`, escaping the project root and producing a path at
`/gpfs_common/share01/clintonlab/../../../envs/*.yml` → `/gpfs_common/share01/clintonlab/envs/*.yml`.

`workflow.basedir` resolves to the directory of the top-level Snakefile (= project root), **not**
the directory of the included rule file. Stripping three `..` segments leaves the filesystem
outside the project.

The bug was latent: `--dry-run` skips conda-env file-existence validation, so every prior planning
dry-run (including 260414-qsk's 575-job resolution check) passed. `--use-conda` triggers
DAG-time validation and surfaces the WorkflowError:

```
WorkflowError: Failed to open source file
/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/../../../envs/magma.yml
```

(reproduced via `snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --use-conda`).

Five other ENV constants elsewhere in `src/snakemake/rules/` (e.g. `LD_BUILD_ENV` in ld_reference
rules, per STATE memory Phase 01-02) already use the correct pattern:

```python
LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")
```

This is the same idiom recorded in the Phase 9 STATE memory: "envs/ paths use
`Path(workflow.basedir)/'envs'/...` (no .parent.parent)". Same memory, same fix.

Purpose: Restore live-execution validity of Phase 5 conda-backed pathway rules (MAGMA, LDSC
partitioned/SEG, HESS, g:Profiler) so real-data branches like `magma_fdr` can actually run,
without regressing the 575-job DAG resolution established by quick task 260414-qsk.

Output: 1 modified file (`src/snakemake/rules/pathway.smk`), 1 line added (`from pathlib import Path`),
4 ENV constant lines rewritten (lines 58-61).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@./CLAUDE.md
@src/snakemake/rules/pathway.smk
@src/snakemake/rules/coloc.smk

<interfaces>
<!-- The correct pattern, verified in 5 other rule files across src/snakemake/rules/ -->
<!-- (ld_reference.smk / coloc.smk / mr.smk / pgs.smk / multitrait.smk per Phase 01-02 STATE memory). -->
<!-- Executor should apply this pattern verbatim — no codebase exploration needed. -->

Correct ENV constant pattern (Python, Snakemake 7.32.4):
```python
from pathlib import Path
MAGMA_ENV = str(Path(workflow.basedir) / "envs" / "magma.yml")
```

Current (broken) pattern at src/snakemake/rules/pathway.smk:58-61:
```python
MAGMA_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "magma.yml"))
LDSC_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "ldsc_py3.yml"))
HESS_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "hess_py27.yml"))
GPROFILER_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "gprofiler.yml"))
```

Current imports at src/snakemake/rules/pathway.smk top (~line 20-22):
```python
"""Pathway + partitioned heritability analysis rules (Phase 5).
...docstring...
"""
import os
```

Existing envs on disk (confirmed via `ls envs/`):
- envs/magma.yml
- envs/ldsc_py3.yml
- envs/hess_py27.yml
- envs/gprofiler.yml
(plus gcta.yml, ld_build.yml, plink.yml, python_stats.yml, qc_dashboard.yml, qtl_processing.yml, r_coloc.yml, README.md)

STATE memory (Phase 01-02 & Phase 09):
"envs/ paths use Path(workflow.basedir)/'envs'/... (no .parent.parent)"

workflow.basedir resolves to: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis (project root)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Replace 4 ENV constants with Path(workflow.basedir)/'envs'/X.yml pattern and add Path import</name>
  <files>src/snakemake/rules/pathway.smk</files>
  <action>
Make exactly two edits to `src/snakemake/rules/pathway.smk`. Do NOT touch any other line.

**Edit 1 — Add `pathlib.Path` import.** The file currently imports only `os` at line ~21.
Add `from pathlib import Path` immediately after the `import os` line so the imports block becomes:

```python
import os
from pathlib import Path
```

Keep `import os` — it is still used elsewhere in the file (e.g. `os.path.join(MULTITRAIT_DIR, ...)`
patterns if present, and other `os.path.exists` / `os.path.join` calls later in the module). Do NOT
remove `import os`.

**Edit 2 — Rewrite lines 58-61.** Replace the four broken `MAGMA_ENV` / `LDSC_ENV` / `HESS_ENV` /
`GPROFILER_ENV` assignments with the pattern used by `LD_BUILD_ENV` in ld_reference rules
(confirmed via STATE memory Phase 01-02, Phase 09, and sibling rule files in
`src/snakemake/rules/`).

The comment on line 57 (`# Conda env paths (absolute, per DEF-01-02 pattern)`) should be kept as-is
— it already references the correct provenance (DEF-01-02 is the Phase 01-02 memory that
established this idiom). Replace lines 58-61 **only**:

```python
# Conda env paths (absolute, per DEF-01-02 pattern)
MAGMA_ENV = str(Path(workflow.basedir) / "envs" / "magma.yml")
LDSC_ENV = str(Path(workflow.basedir) / "envs" / "ldsc_py3.yml")
HESS_ENV = str(Path(workflow.basedir) / "envs" / "hess_py27.yml")
GPROFILER_ENV = str(Path(workflow.basedir) / "envs" / "gprofiler.yml")
```

**Do NOT:**
- Modify any other rule file (coloc.smk, mr.smk, pgs.smk, multitrait.smk, ld_reference.smk,
  finemap.smk, Snakefile, etc. — they already use the correct pattern).
- Modify any other line of pathway.smk beyond the `import` addition and the 4 ENV constants.
- Rename the constants.
- Alter the `# Conda env paths (absolute, per DEF-01-02 pattern)` comment on line 57.
- Change the quote style (keep double quotes to match the rest of the file).
- Touch `TRAIT_COUNTS`, `TRAITS`, `ANCESTRIES`, `TRAIT_ANCESTRIES`, `TRAIT_PAIRS`, or any rule body.

**Why this fix and not others:** `Path(workflow.basedir) / "envs" / X.yml` produces
`/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/envs/X.yml` (project_root/envs/X.yml),
which matches the actual on-disk location. All 4 target env YAMLs are confirmed present.
The `str(...)` wrapper preserves string-valued constants that Snakemake's `conda:` directive
expects (it accepts both str and PosixPath but str matches the existing legacy pattern
elsewhere in the codebase).
  </action>
  <verify>
    <automated>grep -nE '^(MAGMA_ENV|LDSC_ENV|HESS_ENV|GPROFILER_ENV) = str\(Path\(workflow\.basedir\) / "envs" / "[a-z0-9_]+\.yml"\)$' src/snakemake/rules/pathway.smk | wc -l</automated>
    Expected output: `4` (exactly four matching lines).
    Also verify: `grep -n '^from pathlib import Path$' src/snakemake/rules/pathway.smk` returns 1 match, and `grep -n '"\.\.", "\.\.", "\.\."' src/snakemake/rules/pathway.smk` returns 0 matches.
  </verify>
  <done>
    - `src/snakemake/rules/pathway.smk` has `from pathlib import Path` added after `import os`.
    - Lines 58-61 use `str(Path(workflow.basedir) / "envs" / "X.yml")` for all four ENV constants.
    - No `..` segments remain in any ENV path.
    - `import os` is still present (still used elsewhere in the file).
    - No other lines in pathway.smk are modified.
    - No other files are modified.
  </done>
</task>

<task type="auto">
  <name>Task 2: Verify no dry-run regression AND env path resolves under --use-conda; capture both outputs verbatim</name>
  <files>.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md</files>
  <action>
Run the two mandated verification commands and embed their verbatim output into SUMMARY.md.

**Verification 1 — No regression on baseline all_pathway DAG (must still be 575 jobs):**

Use the pinned Snakemake binary from smoke_dev (Python 3.11 env — base miniconda3 has Python 3.13
which is incompatible with Snakemake 7.32.4 per STATE memory `project_python_311_pin.md`):

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | tail -80
```

Capture the tail of the output — specifically the final "Job counts" / "Job stats" summary table and
any leading WorkflowError. Expected: no WorkflowError, total jobs = 575 (same as quick task
260414-qsk established).

**Verification 2 — magma_fdr branch DAG resolves under --use-conda (the originally-failing command):**

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
  results/pathway/magma/bmi_EUR_geneset_fdr.tsv \
  --dry-run --use-conda 2>&1 | tail -60
```

Expected: no `WorkflowError: Failed to open source file .../../envs/magma.yml`. Clean DAG of
~8 jobs for the magma_fdr branch (download_magma_binary → download_magma_ref_files →
download_msigdb → harmonize_sumstats → magma_annotate → magma_gene_analysis →
magma_gene_set_analysis → magma_fdr, or similar — exact count may vary ±2 based on whether
download flag files exist on disk).

**SUMMARY.md structure (use the GSD quick-task summary template):**

```markdown
---
task: 260414-rbv
title: fix Phase 5 conda env path bug in pathway.smk:58-61
date: 2026-04-14
status: complete
files_modified: [src/snakemake/rules/pathway.smk]
---

# Quick task 260414-rbv — SUMMARY

## Bug

[1-paragraph restatement of root cause from <objective>]

## Fix

[Show the 5-line diff: +from pathlib import Path, and the 4 rewritten ENV constants.]

## Verification 1 — baseline all_pathway --dry-run (no regression)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run
```

Output (tail):
```
<VERBATIM OUTPUT FROM VERIFICATION 1>
```

Job total: <N> (expected 575, matches 260414-qsk baseline)

## Verification 2 — magma_fdr --dry-run --use-conda (originally-failing command)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda
```

Output (tail):
```
<VERBATIM OUTPUT FROM VERIFICATION 2>
```

Env path check: no "Failed to open source file" WorkflowError. Env path resolves to
project_root/envs/magma.yml (and siblings).

## Notes

- STATE memory cross-reference: Phase 01-02 "DEF-01-02 pattern" and Phase 09 "envs/ paths use
  Path(workflow.basedir)/'envs'/... (no .parent.parent)" — same idiom, now consistently applied
  across all of src/snakemake/rules/*.smk.
- No other rule files touched; no other pathway.smk lines touched.
- No conda environments built (dry-run only — Carter will build envs on demand at real-data launch).
```

**If Verification 1 shows ≠ 575 jobs** → STOP and report as regression. Do not proceed.

**If Verification 2 shows `WorkflowError: Failed to open source file .../envs/magma.yml`** →
STOP. The fix did not land correctly; re-inspect pathway.smk for syntax errors in the Path
expression.

**If Verification 2 shows a DIFFERENT WorkflowError** (e.g. config/input-file-missing error
unrelated to env paths) → this is expected for some target permutations and NOT a regression of
the fix under scope. Capture verbatim in SUMMARY anyway so the orchestrator can see.

Do NOT attempt to actually build any conda environments (`--conda-create-envs-only` etc.) — this
plan is dry-run scope only per the constraints.
  </action>
  <verify>
    <automated>test -f .planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md && grep -q "Verification 1" .planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md && grep -q "Verification 2" .planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md && grep -q "575" .planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md</automated>
    SUMMARY.md exists, contains both verifications, and references the 575-job baseline.
  </verify>
  <done>
    - SUMMARY.md created at `.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md`.
    - Verification 1 output embedded verbatim; confirms 575 jobs (no regression).
    - Verification 2 output embedded verbatim; confirms no env-path WorkflowError.
    - Diff of the 5-line change shown in the "Fix" section.
    - STATE memory cross-reference called out.
  </done>
</task>

</tasks>

<verification>
Whole-plan verification:

1. `grep -nE 'str\(Path\(workflow\.basedir\) / "envs"' src/snakemake/rules/pathway.smk | wc -l` → `4`
2. `grep -n 'from pathlib import Path' src/snakemake/rules/pathway.smk` → 1 match
3. `grep -c '"\\.\\."' src/snakemake/rules/pathway.smk` → `0` (no `..` segments remain anywhere in the file)
4. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run` resolves to **575 jobs** (matches 260414-qsk post-condition — no regression)
5. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda` does NOT emit `WorkflowError: Failed to open source file .../envs/magma.yml`
6. `git diff --stat src/snakemake/rules/pathway.smk` shows exactly 5 lines changed (1 import added, 4 ENV constants rewritten) — no other hunks
7. `git status` shows only `src/snakemake/rules/pathway.smk` modified and the two new files in `.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/` (PLAN.md, SUMMARY.md)
</verification>

<success_criteria>
- `pathway.smk` ENV constants resolve to `project_root/envs/{magma,ldsc_py3,hess_py27,gprofiler}.yml` — real files that exist on disk.
- Baseline `snakemake all_pathway --dry-run` still produces 575 jobs (verified parity with quick task 260414-qsk).
- The originally-failing command (`snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --use-conda`) is unblocked at the DAG-validation layer: no `WorkflowError: Failed to open source file` on env paths.
- Both verification commands' verbatim output captured in SUMMARY.md so the orchestrator (and future audits) can confirm without re-running.
- Phase 5 real-data execution — whether via narrow `magma_fdr` target or full `all_pathway` LSF launch — is now free of this particular latent env-path bug.
- Plan touches exactly one source file (`src/snakemake/rules/pathway.smk`) + writes one new SUMMARY.md under the quick-task directory.
</success_criteria>

<output>
After completion, create `.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md` with verbatim verification outputs embedded (see Task 2 for the required structure).
</output>
