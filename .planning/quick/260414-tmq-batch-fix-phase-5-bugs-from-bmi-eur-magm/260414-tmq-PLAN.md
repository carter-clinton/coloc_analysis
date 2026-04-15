---
phase: quick-260414-tmq
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/snakemake/rules/pathway.smk
  - envs/gprofiler.yml
autonomous: true
requirements:
  - QUICK-260414-tmq
user_setup: []

must_haves:
  truths:
    - "All 30 `workflow.basedir + ../..` (2-level) python-script-path constructions in `src/snakemake/rules/pathway.smk` resolve to `project_root/src/python/X.py` — real files that exist on disk (verified for all 11 distinct script basenames)."
    - "The 1 `workflow.basedir + ../../..` (3-level) .snakemake/conda path construction at pathway.smk:1164 resolves to `project_root/.snakemake/conda`."
    - "All 5 `_sys.path.insert(0, ...)` calls resolve to `project_root/src/python`."
    - "`envs/gprofiler.yml` declares `r-msigdbr` so `library(msigdbr)` loads in the g:Profiler conda env."
    - "The live conda env at `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` has `r-msigdbr` installed in-place (bypassing the libmamba 2.5 + Anaconda ToS prompt blocker from the 260414-bmi-magma-scout findings)."
    - "`snakemake all_pathway --dry-run` still resolves to 575 jobs (no DAG regression vs 260414-qsk / 260414-rbv baseline; note — orchestrator background text says 575, Task 3 treats 575 as authoritative but accepts 573-577 as non-regressive since download-rule flag-file staging can shift counts ±2)."
    - "`snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda --printshellcmds` produces a clean DAG with zero `..` segments in any rendered shell command path."
  artifacts:
    - path: "src/snakemake/rules/pathway.smk"
      provides: "30 script paths + 5 sys.path inserts + 1 .snakemake/conda path all rebased on Path(workflow.basedir) / 'src' / 'python' (or .snakemake/conda) — no `..` escapes."
      contains: 'Path(workflow.basedir) / "src" / "python"'
    - path: "envs/gprofiler.yml"
      provides: "Augmented dependency list including r-msigdbr for the download_msigdb rule."
      contains: "r-msigdbr"
  key_links:
    - from: "src/snakemake/rules/pathway.smk (28 script= params)"
      to: "src/python/{run_magma,build_magma_geneset,magma_fdr,run_ldsc_partitioned,build_ldsc_annot,run_ldsc_seg,run_hess,build_gprofiler_bg,run_gprofiler,extend_null_genesets,aggregate_pathway_results}.py"
      via: 'str(Path(workflow.basedir) / "src" / "python" / "X.py") assignment in params: blocks'
      pattern: 'Path\(workflow\.basedir\) / "src" / "python" / "[a-z_]+\.py"'
    - from: "src/snakemake/rules/pathway.smk (5 sys.path.insert calls)"
      to: "src/python/ (module import search path at runtime)"
      via: "sys.path.insert(0, str(Path(workflow.basedir) / 'src' / 'python'))"
      pattern: 'sys\.path\.insert\(0, .*Path\(workflow\.basedir\) / "src" / "python"'
    - from: "pathway.smk:download_msigdb rule (conda: GPROFILER_ENV + Rscript -e 'library(msigdbr)')"
      to: "envs/gprofiler.yml dependencies + live env .snakemake/conda/f2752ef7f849ac77376134262def5328_/"
      via: "r-msigdbr package declaration + in-place mamba install -p"
      pattern: "r-msigdbr"
---

<objective>
Batch-fix two classes of bug in Phase 5's `src/snakemake/rules/pathway.smk` surfaced during the
live `bmi.EUR magma_fdr` scout (log:
`.planning/quick/260414-bmi-magma-scout/run_205130_v5.log`). Bug 1 is the same
`workflow.basedir` misunderstanding already fixed for ENV yml paths in quick task 260414-rbv,
but now applied to 30 python-script-path constructions (plus 1 special-case `.snakemake/conda`
lookup). Bug 2 is a missing `r-msigdbr` dependency in the g:Profiler conda env that blocks
`download_msigdb`'s `Rscript -e 'library(msigdbr); msigdbr(...)'` shell-out.

**Bug 1 — script path escape (30 occurrences + 1 special case):**

`workflow.basedir` resolves to the directory of the top-level Snakefile
(= `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis`, the project root), NOT the
directory of the included rule file. The author assumed the latter and compensated with two
`..` segments, producing paths at `/gpfs_common/share01/clintonlab/python/X.py` — outside the
project, where nothing exists. The bug is latent because Snakemake does not validate `script=`
params at DAG-resolve time; it only fails at rule-execution time when the interpreter tries to
locate the file.

Additionally, the author also mis-constructed the path segment: the scripts live at
`project_root/src/python/X.py`, NOT `project_root/python/X.py`. So the fix is **two changes
in one expression**: strip the `..` segments AND insert the `src/` segment.

Audit of `src/snakemake/rules/pathway.smk` (verified via
`grep -nE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk` — returns 30):

- **28 `script=os.path.join(workflow.basedir, "..", "..", "python", "X.py")` params blocks**
  at lines: 457, 497, 531, 571, 603, 634, 677, 716, 762, 872, 918, 1040, 1076, 1112, 1161,
  1222, 1268, 1519, 1593, 1625, 1690, 1731, 2007 (plus 5 more — the full enumerated list is
  inspectable via the grep command above; the executor must replace ALL of them).
- **5 `_sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))` (or
  `sys.path.insert` variant without underscore)** at lines 978, 1053, 1118, 1325, 1631, 1887.
  (Verified count is actually 6 insertion sites when `sys.path.insert` non-underscore variant
  at 1631 is included — the executor must normalize all of them.)
- **1 SPECIAL CASE at line 1164**: `os.path.join(workflow.basedir, "..", "..", "..",
  ".snakemake", "conda", )` — three `..` segments intended to reach
  `project_root/.snakemake/conda`. Same root-cause misunderstanding (zero `..` segments
  needed).

Correct pattern (matches `coloc.smk` / `mr.smk` / `pgs.smk` / `multitrait.smk` / `ld_reference.smk`
— all five sibling rule files in `src/snakemake/rules/` already use this idiom, per
STATE.md Phase 01-02 and Phase 09 memory):

```python
# For script= params:
script=str(Path(workflow.basedir) / "src" / "python" / "X.py")

# For sys.path.insert:
sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
# (or the equivalent os.path.join(workflow.basedir, "src", "python") — both acceptable;
#  choose whichever matches the surrounding local style at each site)

# For .snakemake/conda (line 1164 only):
os.path.join(workflow.basedir, ".snakemake", "conda")
```

`from pathlib import Path` was already added at line 21 by quick task 260414-rbv — NO new
import is required.

**Bug 2 — missing r-msigdbr (one rule fails at first execution):**

`envs/gprofiler.yml` currently lists:
```
r-base=4.3.1
r-gprofiler2=0.2.2
r-dplyr=1.1.4
r-readr=2.1.5
r-yaml=2.3.8
```

The `download_msigdb` rule in `pathway.smk` uses `conda: GPROFILER_ENV` and runs
`Rscript -e 'library(msigdbr); msigdbr::msigdbr(...)'`. Live failure from scout log:
```
Error in library(msigdbr) : there is no package called 'msigdbr'
```

Fix part A — spec-level (`envs/gprofiler.yml`): add `r-msigdbr` (pin version at the current
bioconda stable; stable-on-bioconda around 7.5.x at Apr 2026 — executor to `mamba search -c
bioconda r-msigdbr | tail -5` and pin to the top result per REQ-9 exact-pin convention
documented at the head of gprofiler.yml). Channel `bioconda` is already present.

Fix part B — live-env (`.snakemake/conda/f2752ef7f849ac77376134262def5328_/`): that directory
was created by `--use-conda` earlier and does NOT have msigdbr. Re-creating it triggers the
libmamba 2.5 + Anaconda ToS prompt blocker already logged in the 260414-bmi-magma-scout
findings. Cleanest in-place fix:

```
mamba install -p .snakemake/conda/f2752ef7f849ac77376134262def5328_ -c bioconda r-msigdbr --yes
```

This preserves all other deps in the already-instantiated env, avoids the ToS prompt, and
makes the next `snakemake --use-conda` dispatch of `download_msigdb` succeed at the
`library(msigdbr)` line. Part B is a mutation of live HPC state, so it is gated behind a
type=auto task that captures the verbatim mamba output for the SUMMARY.

Purpose: Unblock the live `bmi.EUR magma_fdr` narrow-scout run so the Phase 5 branch can
actually execute end-to-end against real data (sumstats already harmonized on disk per Phase 0
first-production launch; MAGMA reference data staged at `data/reference/magma/` per
260414-qhr/qsk; all that remains is the two bugs in this plan).

Output: 2 modified files (`src/snakemake/rules/pathway.smk`, `envs/gprofiler.yml`) + 1 live
in-place conda env augmentation (documented in SUMMARY; no committed state change for the env
directory — `.snakemake/conda/` is gitignored). 1 new SUMMARY.md under the quick-task dir.

Not in scope: any rule outside `pathway.smk`, any python script in `src/python/`, any other
env yml (`magma.yml`, `ldsc_py3.yml`, `hess_py27.yml`, `python_stats.yml` remain untouched),
the `download_sumstats` rule, and recreating any other pre-existing `.snakemake/conda/*`
directory.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@./CLAUDE.md
@.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-PLAN.md
@.planning/quick/260414-rbv-fix-phase-5-conda-env-path-bug-in-pathwa/260414-rbv-SUMMARY.md
@src/snakemake/rules/pathway.smk
@envs/gprofiler.yml

<interfaces>
<!-- The correct patterns, verified in 5 sibling rule files under src/snakemake/rules/ -->
<!-- (coloc.smk, mr.smk, pgs.smk, multitrait.smk, ld_reference.smk) and in the already- -->
<!-- landed 260414-rbv fix to pathway.smk's ENV constants at lines 58-61. -->

# Correct replacement patterns

## Pattern A — script= params in rule params: blocks (28 sites)
BEFORE:
```python
script=os.path.join(workflow.basedir, "..", "..", "python", "X.py"),
```
AFTER:
```python
script=str(Path(workflow.basedir) / "src" / "python" / "X.py"),
```
(keep the trailing comma; keep double quotes to match surrounding style)

## Pattern B — sys.path.insert calls inside run: blocks (5-6 sites)
BEFORE:
```python
_sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
```
AFTER:
```python
_sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
```
(preserve `_sys` vs `sys` local aliasing — if the surrounding code aliases `import sys as _sys`,
keep `_sys`; if the site uses plain `sys.path.insert`, keep `sys`)

## Pattern C — .snakemake/conda special case (pathway.smk:1164 only)
BEFORE:
```python
python27=os.path.join(
    workflow.basedir, "..", "..", "..", ".snakemake", "conda",
),
```
AFTER:
```python
python27=os.path.join(
    workflow.basedir, ".snakemake", "conda",
),
```
(keep the multi-line formatting, keep the trailing comma inside the call,
keep `os.path.join` — do NOT rewrite this one as Path(…) since the surrounding expression
appends more segments at runtime via string concatenation elsewhere — minimal-diff preservation)

# Existing on-disk scripts (all verified present via `ls src/python/`)
- src/python/run_magma.py
- src/python/build_magma_geneset.py
- src/python/magma_fdr.py
- src/python/run_ldsc_partitioned.py
- src/python/build_ldsc_annot.py
- src/python/run_ldsc_seg.py
- src/python/run_hess.py
- src/python/build_gprofiler_bg.py
- src/python/run_gprofiler.py
- src/python/extend_null_genesets.py
- src/python/aggregate_pathway_results.py

# Existing imports at pathway.smk:20-21 (do NOT re-add)
```python
import os
from pathlib import Path
```

# gprofiler.yml current state (envs/gprofiler.yml)
```yaml
name: gprofiler_r
channels:
  - conda-forge
  - bioconda
dependencies:
  - r-base=4.3.1
  - r-gprofiler2=0.2.2
  - r-dplyr=1.1.4
  - r-readr=2.1.5
  - r-yaml=2.3.8
```

# Live conda env directory (already instantiated, do NOT recreate)
`.snakemake/conda/f2752ef7f849ac77376134262def5328_/` — hash corresponds to gprofiler.yml;
mutating it in-place avoids the libmamba 2.5 ToS prompt blocker.

# Snakemake binary (use for dry-run verification; base miniconda3 has Python 3.13, incompatible)
`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake`
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Batch-fix 30+1 workflow.basedir path constructions in pathway.smk (no python scripts touched, no rule bodies altered)</name>
  <files>src/snakemake/rules/pathway.smk</files>
  <action>
Apply three categories of text replacement in `src/snakemake/rules/pathway.smk`. Do NOT touch
any other file. Do NOT touch any `src/python/*.py`. Do NOT touch any other rule's logic,
inputs, outputs, shell blocks, or run-block bodies beyond the specific substrings listed
below.

**Step 1 — Pre-audit (capture baseline counts for SUMMARY):**

Run and capture for the SUMMARY table:
```
grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk
```
Expected: `30`. If not 30, STOP and report — the authoritative audit count was established by
the background briefing and a deviation means someone else modified the file between plan
time and execute time.

Also capture pre-fix line numbers of all 30 matches:
```
grep -nE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk > /tmp/tmq_before.txt
```
Embed the first 10 + last 3 lines of that file in the SUMMARY's "Pre-fix audit" section.

**Step 2 — Apply Pattern A (script= params, 28 sites, 2-level `..`):**

Replace every occurrence of the exact substring:
```
os.path.join(workflow.basedir, "..", "..", "python",
```
with:
```
str(Path(workflow.basedir) / "src" / "python"
```

This substring rewrites the LEADING portion of 28 `script=` assignments. The trailing portion
(the script filename + closing paren + trailing comma) must be adjusted in each of the 28
sites to use `/` path-operator syntax instead of a fresh `os.path.join` argument, i.e.:

BEFORE:
```
script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
```
AFTER:
```
script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
```

**Recommended mechanics** (executor may choose sed, Python, or manual Edits — whichever
produces the cleanest diff):

Option X — single `sed` pass (cleanest, but test on a copy first):
```
sed -E -i 's|os\.path\.join\(workflow\.basedir, "\.\.", "\.\.", "python", ("[a-z_0-9]+\.py")\)|str(Path(workflow.basedir) / "src" / "python" / \1)|g' src/snakemake/rules/pathway.smk
```
After sed, verify:
```
grep -cE 'str\(Path\(workflow\.basedir\) / "src" / "python" / "[a-z_0-9]+\.py"\)' src/snakemake/rules/pathway.smk
```
Expected: `28`.

Option Y — per-line manual Edit tool: For each of the 28 lines enumerated in Pattern A of the
interfaces block, use the Edit tool with old_string being the full line and new_string being
the converted line. This is verbose but produces an easily-reviewable diff.

**Step 3 — Apply Pattern B (sys.path.insert, ~5-6 sites, no trailing filename):**

Replace every occurrence of the substring:
```
os.path.join(workflow.basedir, "..", "..", "python")
```
with:
```
str(Path(workflow.basedir) / "src" / "python")
```

`sed` form:
```
sed -E -i 's|os\.path\.join\(workflow\.basedir, "\.\.", "\.\.", "python"\)|str(Path(workflow.basedir) / "src" / "python")|g' src/snakemake/rules/pathway.smk
```

Verify:
```
grep -cE 'sys\.path\.insert\(0, str\(Path\(workflow\.basedir\) / "src" / "python"\)\)' src/snakemake/rules/pathway.smk
```
Expected: matches the pre-fix count of sys.path.insert sites (5 per background briefing; may
be 6 — report actual number to the SUMMARY).

**Step 4 — Apply Pattern C (special case line 1164, 3-level `..` → 0-level):**

This is a single multi-line expression (roughly lines 1163-1165) using the surrounding
`os.path.join(...)` with newlines. Use Edit tool with exact old_string/new_string (do not sed
this one — multi-line sed is fragile).

BEFORE (exact three lines):
```
        python27=os.path.join(
            workflow.basedir, "..", "..", "..", ".snakemake", "conda",
        ),
```
AFTER:
```
        python27=os.path.join(
            workflow.basedir, ".snakemake", "conda",
        ),
```

**Step 5 — Post-fix audit (MUST PASS before task is done):**

```bash
# Primary gate — no `..` segments remain in any workflow.basedir construction:
grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk
# Expected: 0

# Sanity — script= sites correctly rewritten:
grep -cE 'str\(Path\(workflow\.basedir\) / "src" / "python" / "[a-z_0-9]+\.py"\)' src/snakemake/rules/pathway.smk
# Expected: 28

# Sanity — .snakemake/conda special case rewritten:
grep -nE 'workflow\.basedir, "\.snakemake", "conda"' src/snakemake/rules/pathway.smk
# Expected: exactly 1 match at line ~1164

# Sanity — every unique script filename resolves to a real file:
for f in run_magma.py build_magma_geneset.py magma_fdr.py run_ldsc_partitioned.py \
         build_ldsc_annot.py run_ldsc_seg.py run_hess.py build_gprofiler_bg.py \
         run_gprofiler.py extend_null_genesets.py aggregate_pathway_results.py; do
  test -f "src/python/$f" && echo "OK $f" || echo "MISSING $f"
done
# Expected: 11 "OK" lines, 0 "MISSING"
```

**Do NOT:**
- Modify any python script in `src/python/` (the path fix means Snakemake will now LOCATE them
  correctly — their contents don't need changes).
- Touch `envs/gprofiler.yml` in this task (Task 2 owns that).
- Rewrite line 1164 using Path() syntax (preserve the `os.path.join` form to minimize diff
  noise and because downstream expression may concatenate more segments via different
  mechanisms).
- Remove or reorder any rule.
- Change quote style (use double quotes throughout).
- Touch `MAGMA_ENV` / `LDSC_ENV` / `HESS_ENV` / `GPROFILER_ENV` at lines 58-61 — those were
  already fixed by 260414-rbv.

**If the post-fix audit primary gate (`grep -cE 'workflow\.basedir,\s*"\.\."'` = 0) fails**:
STOP, do not commit, surface the remaining sites to the user. Do not attempt a second sed
pass to clean up leftovers without explicit direction — a residual match likely means the
substring was embedded in a different-than-expected surrounding context that wasn't audited.
  </action>
  <verify>
    <automated>grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk</automated>
    Expected: `0` (zero `..` segments remain after any `workflow.basedir` reference).
    Secondary: `grep -cE 'str\(Path\(workflow\.basedir\) / "src" / "python" / "[a-z_0-9]+\.py"\)' src/snakemake/rules/pathway.smk` → `28`.
    Tertiary: `grep -cE 'workflow\.basedir, "\.snakemake", "conda"' src/snakemake/rules/pathway.smk` → `1`.
  </verify>
  <done>
    - `grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk` returns 0.
    - 28 `script=str(Path(workflow.basedir) / "src" / "python" / "X.py")` params blocks present.
    - 5 (or 6) `sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))` calls present.
    - 1 `os.path.join(workflow.basedir, ".snakemake", "conda", )` at or near line 1164 (line ± 2 acceptable, since Edits may shift line numbers slightly).
    - All 11 distinct referenced script files exist at `src/python/X.py` (verified via file-exists loop above).
    - No other files modified.
    - `import os` and `from pathlib import Path` still present at pathway.smk:20-21 (not re-added, not removed).
  </done>
</task>

<task type="auto">
  <name>Task 2: Add r-msigdbr to envs/gprofiler.yml spec + in-place augment the live conda env</name>
  <files>envs/gprofiler.yml</files>
  <action>
Two sub-steps — one is a committed file change; the other is a live HPC state mutation that is
captured in SUMMARY but not committed (the `.snakemake/conda/` directory is gitignored and
treated as cache).

**Step 1 — Augment the spec (`envs/gprofiler.yml`):**

Pin-lookup first. Run:
```bash
mamba search -c bioconda r-msigdbr 2>&1 | tail -10
```

Capture the stable bioconda top match. As of Apr 2026 the expected version is `r-msigdbr=7.5.x`
(e.g. `7.5.1`). Exact version depends on bioconda snapshot — pin to the top version string
from the search output, consistent with the existing file's REQ-9 exact-pin convention
(documented in the header comment at envs/gprofiler.yml:10-12: "REQ-9: exact version pins for
reproducibility").

Edit `envs/gprofiler.yml` to append one dependency line after `r-yaml=2.3.8`. The resulting
`dependencies:` block should read (replace `<VERSION>` with the concrete version from
mamba search):

```yaml
dependencies:
  # REQ-9: exact version pins for reproducibility. Versions chosen to match
  # the conda-forge/bioconda snapshot at the time of Phase 5 initial build
  # (Apr 2026). Bump via a deliberate decision, not drift.
  - r-base=4.3.1
  - r-gprofiler2=0.2.2
  - r-dplyr=1.1.4
  - r-readr=2.1.5
  - r-yaml=2.3.8
  - r-msigdbr=<VERSION>
```

Preserve:
- The YAML `---` header (if present — check before editing).
- All comment lines.
- The channels block (`conda-forge` + `bioconda`).
- Trailing newline at end of file.

Do NOT alter any other dependency's pin. Do NOT reorder. Do NOT change quote style (the file
uses bare scalars).

**Step 2 — In-place-augment the live conda env (mutation, captured in SUMMARY):**

The env directory `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` was instantiated by a
previous `--use-conda` run WITHOUT msigdbr. Recreating it would trigger the libmamba 2.5 +
Anaconda ToS prompt blocker logged in the 260414-bmi-magma-scout findings. Instead, install
in place:

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# Guard: confirm target dir exists BEFORE mutating.
test -d .snakemake/conda/f2752ef7f849ac77376134262def5328_ || {
  echo "ENV DIR MISSING — abort Step 2 and report"; exit 1;
}

# Install msigdbr in place. --yes avoids interactive prompts.
mamba install -p .snakemake/conda/f2752ef7f849ac77376134262def5328_ \
  -c bioconda -c conda-forge \
  r-msigdbr --yes 2>&1 | tee /tmp/tmq_mamba_install.log
```

Capture the full stdout+stderr into `/tmp/tmq_mamba_install.log` and embed the tail
(final ~30 lines showing the transaction summary + "Transaction finished" or analogue) into
the SUMMARY.

**Verify Step 2** (inline, before moving to Task 3):

```bash
.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/R --version
.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/Rscript -e 'library(msigdbr); cat("MSIGDBR_OK\n")'
```

Expected second command output: a single line `MSIGDBR_OK` (possibly preceded by standard R
package-load messages like "Attaching package: 'msigdbr'"). If instead the output is
`Error in library(msigdbr) : there is no package called 'msigdbr'`, STOP — Step 2 did not
land; report the mamba install log tail and do not proceed to Task 3.

**If `mamba install` fails** with a solver error (version conflict, unsatisfiable deps, or the
libmamba 2.5 ToS prompt despite `--yes`): fall back to the safer "conda" front-end:
```bash
conda install -p .snakemake/conda/f2752ef7f849ac77376134262def5328_ \
  -c bioconda -c conda-forge r-msigdbr --yes 2>&1 | tee -a /tmp/tmq_mamba_install.log
```
If THAT also fails, STOP and surface to the user. Do not attempt a `conda env update` or
`mamba env update -f envs/gprofiler.yml` — that will either recreate the env (triggering the
ToS prompt) or aggressively re-solve all pins.

**Do NOT:**
- Modify any other `envs/*.yml` file.
- Recreate the env directory.
- Touch `pathway.smk` in this task.
- Invoke `snakemake --conda-create-envs-only`.
- Delete any file under `.snakemake/conda/`.
  </action>
  <verify>
    <automated>grep -c 'r-msigdbr' envs/gprofiler.yml</automated>
    Expected: ≥ 1 (r-msigdbr dependency line present in spec).
    Plus (executed as a follow-up): `.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/Rscript -e 'library(msigdbr); cat("MSIGDBR_OK\n")'` emits `MSIGDBR_OK`.
  </verify>
  <done>
    - `envs/gprofiler.yml` has `r-msigdbr=<concrete-version>` pinned in dependencies (version from mamba search top match at run time).
    - Channels block unchanged (conda-forge + bioconda).
    - No other dependency pin altered.
    - Live env at `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` has msigdbr importable from Rscript (verified via MSIGDBR_OK probe).
    - Mamba/conda install log tail embedded in SUMMARY (for Task 3).
    - Fallback to `conda install` was documented if it was triggered; otherwise fallback section states "not triggered".
  </done>
</task>

<task type="auto">
  <name>Task 3: Run both dry-run verification gates + write SUMMARY.md with verbatim verification output</name>
  <files>.planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md</files>
  <action>
Run the two mandated dry-run verifications plus the scripts-exist probe and the live-env
msigdbr probe, then write SUMMARY.md with all verbatim outputs embedded.

**Verification Gate 1 — No regression on `all_pathway` DAG (575-job parity):**

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 \
  | tee /tmp/tmq_verif1.log | tail -60
```

Expected: "total" row in the Job stats table shows **575** (matching 260414-qsk / 260414-rbv
baseline). If the count is 573-577 AND no WorkflowError is present, treat as non-regressive
(download-rule flag-file staging can shift ±2 — the background briefing notes this). If the
count is outside 573-577, STOP and report.

**Verification Gate 2 — `magma_fdr` branch resolves under `--use-conda --printshellcmds`, no `..` in rendered shell paths:**

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
  results/pathway/magma/bmi_EUR_geneset_fdr.tsv \
  --dry-run --use-conda --printshellcmds 2>&1 \
  | tee /tmp/tmq_verif2.log | tail -120
```

Then:
```bash
# Sanity: no `..` anywhere in the rendered shell commands.
grep -cE '\.\.' /tmp/tmq_verif2.log || echo "0"
```

Expected:
- No `WorkflowError: Failed to open source file .../envs/*.yml` (fixed by 260414-rbv).
- No `WorkflowError` whatsoever tied to script paths, sys.path inserts, or .snakemake/conda.
- Total jobs between 4 and 12 (magma_fdr branch; exact count depends on download-flag staging).
- `grep -cE '\.\.' /tmp/tmq_verif2.log` → 0 (no `..` escapes in rendered shell commands).
  Note: if a `..` appears inside a PROSE part of the output (e.g. "..." ellipsis in a Snakemake
  status line) that isn't inside a path, document it — the real check is that no path
  contains `..`. A stricter form:
  `grep -E '/[^/]*\.\./[^/]*' /tmp/tmq_verif2.log | grep -v '^\.' || echo "NO_PATH_DOTDOT"`.

**Verification Gate 3 — All referenced scripts exist at `src/python/`:**

```bash
python3 -c "
import os, sys
scripts = ['run_magma.py', 'magma_fdr.py', 'build_magma_geneset.py',
           'run_ldsc_partitioned.py', 'build_ldsc_annot.py', 'run_ldsc_seg.py',
           'run_hess.py', 'build_gprofiler_bg.py', 'run_gprofiler.py',
           'extend_null_genesets.py', 'aggregate_pathway_results.py']
missing = [s for s in scripts if not os.path.exists(os.path.join('src', 'python', s))]
assert not missing, f'MISSING: {missing}'
print(f'ALL_{len(scripts)}_SCRIPTS_EXIST')
" 2>&1 | tee /tmp/tmq_verif3.log
```

Expected: `ALL_11_SCRIPTS_EXIST`.

**Verification Gate 4 — Live env msigdbr probe (re-run post-Task-2):**

```bash
.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/Rscript \
  -e 'library(msigdbr); cat("MSIGDBR_OK\n")' 2>&1 | tee /tmp/tmq_verif4.log
```

Expected final line: `MSIGDBR_OK`.

**Verification Gate 5 — No `..` segments anywhere in pathway.smk workflow.basedir refs:**

```bash
grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk 2>&1 \
  | tee /tmp/tmq_verif5.log
```

Expected: `0`.

**Write SUMMARY.md** at `.planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md` with this structure:

```markdown
---
task: 260414-tmq
title: batch fix Phase 5 bugs from bmi.EUR magma_fdr scout (30 script-path bugs + r-msigdbr env augment)
date: 2026-04-14
status: complete
files_modified:
  - src/snakemake/rules/pathway.smk
  - envs/gprofiler.yml
live_state_mutations:
  - ".snakemake/conda/f2752ef7f849ac77376134262def5328_/  (r-msigdbr installed in-place via mamba; not committed — directory is gitignored)"
---

# Quick task 260414-tmq — SUMMARY

## Bugs (two classes, batched)

### Bug 1 — workflow.basedir path escape (30 script-path + 1 .snakemake/conda path)

[1-paragraph restatement of root cause. Emphasize: same misunderstanding as 260414-rbv, but
for python scripts (not env YAMLs). workflow.basedir resolves to project root; author added
2 `..` segments (plus `src/` segment missing) for scripts, and 3 `..` segments for .snakemake/conda.]

### Bug 2 — r-msigdbr missing from gprofiler env

[1-paragraph restatement. download_msigdb rule uses conda: GPROFILER_ENV + Rscript -e
'library(msigdbr)'. The env yml didn't declare msigdbr, so `library(msigdbr)` fails at first
execution. Live env at .snakemake/conda/f2752ef7f849ac77376134262def5328_/ was built without
msigdbr; recreating triggers libmamba 2.5 ToS prompt blocker; fix is in-place mamba install.]

## Fix summary

| File / target | Change | Verified by |
|---------------|--------|-------------|
| src/snakemake/rules/pathway.smk | 28 script= Pattern A rewrites + {N} sys.path.insert Pattern B rewrites + 1 Pattern C rewrite at line ~1164 | Gate 1, 2, 5 |
| envs/gprofiler.yml | +1 line: `- r-msigdbr=<VERSION>` | Gate 2, 4 |
| .snakemake/conda/f2752ef7f849ac77376134262def5328_/ (live, gitignored) | `mamba install -p ... r-msigdbr --yes` | Gate 4 |

## Pre-fix audit

```
<verbatim head+tail of /tmp/tmq_before.txt showing 30 matches>
```

## Diff: src/snakemake/rules/pathway.smk

```
<git diff --stat src/snakemake/rules/pathway.smk>
```

Specimen hunks (3 representative):

```diff
<first script= rewrite — e.g. line 457 run_magma.py>
<first sys.path.insert rewrite — e.g. line 978>
<the line 1164 .snakemake/conda rewrite>
```

## Diff: envs/gprofiler.yml

```diff
<full unified diff — single +1 line>
```

## Verification Gate 1 — all_pathway --dry-run (575-job parity)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run
```

Output (tail):
```
<verbatim last 40-60 lines of /tmp/tmq_verif1.log — must include the Job stats table>
```

Job total: **<N>** (expected 575 ± 2; {PASS/FAIL} vs 260414-qsk / 260414-rbv baseline).

## Verification Gate 2 — magma_fdr --dry-run --use-conda --printshellcmds

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda --printshellcmds
```

Output (tail):
```
<verbatim last 60-100 lines of /tmp/tmq_verif2.log>
```

No-`..`-in-paths check: `<output from the grep -E '/[^/]*\.\./[^/]*' probe>` → `NO_PATH_DOTDOT` ({PASS/FAIL}).

Env-path WorkflowError check: {absent/present} ({PASS/FAIL}).

## Verification Gate 3 — all 11 script files exist at src/python/

```
<verbatim /tmp/tmq_verif3.log — one line "ALL_11_SCRIPTS_EXIST">
```

## Verification Gate 4 — live env msigdbr probe

```
<verbatim /tmp/tmq_verif4.log — ending with MSIGDBR_OK>
```

## Verification Gate 5 — no `..` in workflow.basedir refs

Command:
```
grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk
```

Output: `<verbatim>` → expected `0` ({PASS/FAIL}).

## Mamba install log tail (Task 2, Step 2)

```
<last 30 lines of /tmp/tmq_mamba_install.log — transaction summary>
```

Fallback to `conda install` triggered: {yes/no, with reason if yes}.

## Scope boundary check

Files touched (git status):
```
<verbatim `git status --short` output>
```

Expected: exactly
- M src/snakemake/rules/pathway.smk
- M envs/gprofiler.yml
- (plus new files under .planning/quick/260414-tmq-.../ : PLAN.md, SUMMARY.md)

Files NOT touched (spot-check):
- src/python/*.py — no modifications (verified via `git status`)
- envs/magma.yml, envs/ldsc_py3.yml, envs/hess_py27.yml, envs/python_stats.yml — no mods
- Any rule file outside pathway.smk — no mods
- download_sumstats rule body — no mods (verified via `git diff src/snakemake/rules/pathway.smk` — the diff touches only the 30+1 path-construction lines)

## Notes

- STATE memory cross-reference: Phase 01-02 / Phase 09 "envs/ paths use
  Path(workflow.basedir)/'envs'/... (no .parent.parent)" idiom is now extended uniformly to
  src/python scripts and the .snakemake/conda cache path. Completes the architectural fix
  started in 260414-rbv.
- Live-run precondition for `bmi.EUR magma_fdr` scout is now satisfied: (1) ENV paths resolve
  (260414-rbv), (2) script paths resolve (this task), (3) r-msigdbr importable from R under
  GPROFILER_ENV (this task — both spec + live env).
- Recreating `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` (e.g. by deleting and
  re-running `snakemake --use-conda`) is still blocked by libmamba 2.5 ToS prompt per
  260414-bmi-magma-scout findings — Carter will address that environment-wide issue out of
  scope. The in-place mamba install sidesteps it for this env specifically.
- No conda environments rebuilt (dry-run verification only; only the live gprofiler env was
  augmented in-place).

## Self-Check

- [ ] Gate 1 PASS (575 ± 2 jobs, no WorkflowError)
- [ ] Gate 2 PASS (no env-path WorkflowError, no `..` in rendered shell paths, magma_fdr DAG resolves)
- [ ] Gate 3 PASS (all 11 scripts exist)
- [ ] Gate 4 PASS (MSIGDBR_OK emitted)
- [ ] Gate 5 PASS (0 matches for `workflow.basedir, ".."` pattern)
- [ ] Scope boundary: only pathway.smk + gprofiler.yml modified
```

**If ANY gate fails**: mark the corresponding self-check item as FAIL, include the failing
output verbatim, and in the SUMMARY `status:` frontmatter field use `blocked` instead of
`complete`. Do not commit. Surface to user.

**If ALL gates pass**: status=complete, all self-check boxes ticked, SUMMARY written.
  </action>
  <verify>
    <automated>test -f .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md && grep -q "Verification Gate 1" .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md && grep -q "Verification Gate 2" .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md && grep -q "Verification Gate 4" .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md && grep -q "MSIGDBR_OK" .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md && grep -q "575" .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md</automated>
    SUMMARY.md exists, contains all 5 verification gates, references the 575-job baseline, and embeds MSIGDBR_OK probe output.
  </verify>
  <done>
    - SUMMARY.md created with all 5 verification gates + verbatim outputs.
    - All 5 gates PASS (or any failures explicitly documented with status=blocked).
    - Diff hunks of pathway.smk (3 specimens) and gprofiler.yml (full) embedded.
    - Mamba install log tail embedded.
    - Scope-boundary `git status` output embedded showing only the two source files + planning files modified.
    - Self-check section present.
  </done>
</task>

</tasks>

<verification>
Whole-plan verification (all MUST pass; any failure = plan incomplete):

1. `grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk` → `0`
   (no `..` segments remain in any `workflow.basedir` reference — closes Bug 1 entirely)
2. `grep -cE 'str\(Path\(workflow\.basedir\) / "src" / "python" / "[a-z_0-9]+\.py"\)' src/snakemake/rules/pathway.smk` → `28`
   (28 script= sites rewritten to correct idiom)
3. `grep -cE 'workflow\.basedir, "\.snakemake", "conda"' src/snakemake/rules/pathway.smk` → `1`
   (single .snakemake/conda site rewritten)
4. `grep -c 'r-msigdbr' envs/gprofiler.yml` → `≥ 1`
   (spec augmented)
5. `.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/Rscript -e 'library(msigdbr); cat("MSIGDBR_OK\n")'` →
   output contains `MSIGDBR_OK` (live env augmented)
6. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run` →
   total 575 ± 2 jobs, NO WorkflowError (no DAG regression)
7. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda --printshellcmds` →
   clean DAG, no env-path WorkflowError, no `..` in any rendered shell command path
8. All 11 distinct referenced script filenames exist at `src/python/X.py`
9. `git status --short` shows exactly 2 modified source files (`pathway.smk`, `gprofiler.yml`)
   plus new planning artifacts under `.planning/quick/260414-tmq-.../`
10. `git diff --stat src/snakemake/rules/pathway.smk envs/gprofiler.yml` shows only the
    expected hunks — no accidental changes to rule bodies, shell blocks, dependency pins
    other than the +r-msigdbr line, or unrelated imports
</verification>

<success_criteria>
- Phase 5 live-run scout (`bmi.EUR magma_fdr` and siblings) is unblocked on both bug classes:
  (a) script-path escapes (30 sites) and (b) missing msigdbr in GPROFILER_ENV (1 rule).
- All 30 `workflow.basedir + "..", ".."` script-path constructions in `pathway.smk` rewritten
  to `Path(workflow.basedir) / "src" / "python" / X.py`.
- Line 1164 special case (`workflow.basedir + "..", "..", ".."`) rewritten to
  `os.path.join(workflow.basedir, ".snakemake", "conda")`.
- `envs/gprofiler.yml` declares `r-msigdbr` at a concrete pinned version (REQ-9 convention).
- Live conda env at `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` has msigdbr
  importable — verified via MSIGDBR_OK probe.
- Baseline `all_pathway --dry-run` job count within 575 ± 2 (no DAG regression vs
  260414-qsk / 260414-rbv baseline).
- `magma_fdr --dry-run --use-conda --printshellcmds` produces a clean DAG with no `..` in
  rendered shell command paths (independent observable confirming Bug 1 fix).
- Plan touches exactly two source files (`pathway.smk`, `gprofiler.yml`) + one new
  SUMMARY.md; no python script modified; no other rule file modified; no other env yml
  modified; `download_sumstats` untouched; no other `.snakemake/conda/` directory recreated
  or deleted.
- SUMMARY.md embeds verbatim output from all 5 verification gates + mamba install log tail +
  `git status --short` scope-boundary evidence.
- Phase 5 remaining live-execution blockers (beyond this plan's scope) — if any surface
  during the Gate 2 dry-run — are noted in SUMMARY "Notes" section for the next quick task to
  pick up.
</success_criteria>

<output>
After completion, create `.planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/260414-tmq-SUMMARY.md`
with verbatim verification outputs embedded (see Task 3 for the required structure).
</output>
