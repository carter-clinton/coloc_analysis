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
commits:
  - 2414ea9  fix(quick-260414-tmq): rebase 30 workflow.basedir path constructions in pathway.smk
  - e193896  fix(quick-260414-tmq): add r-msigdbr=7.5.1 to gprofiler.yml for download_msigdb rule
---

# Quick task 260414-tmq — SUMMARY

## Bugs (two classes, batched)

### Bug 1 — workflow.basedir path escape (30 script-path + 1 .snakemake/conda path)

Same misunderstanding that was fixed for env YAMLs in quick task 260414-rbv, now applied to
the python-script-path constructions and the .snakemake/conda cache path. `workflow.basedir`
resolves to the directory of the top-level `Snakefile` (= project root), NOT the directory
of the included rule file. The author compensated for the wrong mental model by prepending
two `..` segments (producing paths OUTSIDE the project at
`/gpfs_common/share01/clintonlab/python/X.py` — nothing exists there), and additionally
omitted the required `src/` segment so scripts would have resolved to
`project_root/python/X.py` instead of `project_root/src/python/X.py`. The .snakemake/conda
site at line 1164 made the same error three times in one expression (3-level `..`). Latent
failure mode: Snakemake does not validate `script=` params at DAG-resolve time, so the bug
only surfaced when `--use-conda --printshellcmds` rendered real shell commands during the
`bmi.EUR magma_fdr` scout. Fix: drop all `..` segments and (for script paths) insert `src/`.

### Bug 2 — r-msigdbr missing from gprofiler env

The `download_msigdb` rule uses `conda: GPROFILER_ENV` and runs
`Rscript -e 'library(msigdbr); msigdbr::msigdbr(...)'`. `envs/gprofiler.yml` never declared
`r-msigdbr`, so the rule failed at first execution with
`Error in library(msigdbr) : there is no package called 'msigdbr'`. The live conda env at
`.snakemake/conda/f2752ef7f849ac77376134262def5328_/` was instantiated by a previous
`--use-conda` run WITHOUT msigdbr; recreating it triggers the libmamba 2.5 + Anaconda ToS
prompt blocker logged in the 260414-bmi-magma-scout findings. Fix: pin `r-msigdbr=7.5.1`
in the yml (REQ-9 exact-pin convention) AND install msigdbr in place in the live env via
`mamba install -p` to bypass the ToS blocker.

## Fix summary

| File / target | Change | Verified by |
|---------------|--------|-------------|
| src/snakemake/rules/pathway.smk | 23 `script=` Pattern A rewrites + 6 `sys.path.insert` Pattern B rewrites + 1 Pattern C rewrite at line 1164 | Gates 1, 2, 5 |
| envs/gprofiler.yml | +1 line: `- r-msigdbr=7.5.1` | Gate 2 dry-run (spec), Gate 4 (live env) |
| .snakemake/conda/f2752ef7f849ac77376134262def5328_/ (live, gitignored) | `mamba install -p ... -c bioconda -c conda-forge r-msigdbr --yes` → Transaction finished | Gate 4 |

Note on Pattern A/B count distribution: the plan's pre-audit estimated "28 script= + 5-6 sys.path.insert";
actual on-disk distribution was 23 script= + 6 sys.path.insert = 29, plus the 1 Pattern C special
case = 30 total `workflow.basedir, ".."` matches. Total count matches plan; breakdown differs
because the plan estimate conflated some adjacent sys.path.insert occurrences with script=
lines. All 30 sites rewritten.

## Pre-fix audit

```
457:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
497:        script=os.path.join(workflow.basedir, "..", "..", "python", "build_magma_geneset.py"),
531:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
571:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
603:        script=os.path.join(workflow.basedir, "..", "..", "python", "magma_fdr.py"),
634:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
677:        script=os.path.join(workflow.basedir, "..", "..", "python", "build_ldsc_annot.py"),
716:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
762:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
872:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_seg.py"),
...
1731:        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
1887:        _sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
2007:        script=os.path.join(workflow.basedir, "..", "..", "python", "aggregate_pathway_results.py"),
```

(Total: 30 matches; full list captured at `/tmp/tmq_before.txt` during execution.)

## Diff: src/snakemake/rules/pathway.smk

```
 src/snakemake/rules/pathway.smk | 60 ++++++++++++++++++++---------------------
 1 file changed, 30 insertions(+), 30 deletions(-)
```

Specimen hunks (3 representative):

```diff
@@ -454,7 +454,7 @@ rule magma_annotate:
         annot=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation.genes.annot"),
     params:
         out_prefix=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation"),
-        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
+        script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
         snp_loc=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bim",
     conda:
         MAGMA_ENV
```

```diff
     run:
         import sys as _sys
-        _sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
+        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
         from run_ldsc_seg import identify_shared_tissues, parse_seg_results
```

```diff
         script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
         hess_script="tools/hess/hess.py",
         python27=os.path.join(
-            workflow.basedir, "..", "..", "..", ".snakemake", "conda",
+            workflow.basedir, ".snakemake", "conda",
         ),
         bfile=lambda wc: os.path.join(
             PATHWAY_CFG.get("hess_ld_panel", "data/reference/hess/ld_panel"),
             wc.ancestry,
```

## Diff: envs/gprofiler.yml

```diff
diff --git a/envs/gprofiler.yml b/envs/gprofiler.yml
index c19c5bb..3fb05c0 100644
--- a/envs/gprofiler.yml
+++ b/envs/gprofiler.yml
@@ -15,3 +15,4 @@ dependencies:
   - r-dplyr=1.1.4
   - r-readr=2.1.5
   - r-yaml=2.3.8
+  - r-msigdbr=7.5.1
```

## Verification Gate 1 — all_pathway --dry-run (575-job parity)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run
```

Output (tail):
```
summarize_coloc_results              1
summarize_finemap_results            1
validate_negative_controls           1
total                              575

Reasons:
    (check individual jobs above for details)
    input files updated by another job:
        aggregate_pathway_results, aggregate_qtl_coloc, all_pathway, assign_tiers, ...
    missing output files:
        aggregate_pathway_results, aggregate_qtl_coloc, assign_tiers, build_1kg_sample_lists, ...
    updated input files:
        harmonize_sumstats

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Job total: **575** (exact parity with 260414-qsk / 260414-rbv baseline; **PASS**).
Errors encountered: `grep -E 'Error|WorkflowError'` → NO_ERRORS (clean log after `--unlock`
cleared a stale directory lock from an unrelated earlier snakemake invocation).

## Verification Gate 2 — magma_fdr --dry-run --use-conda --printshellcmds

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    results/pathway/magma/bmi_EUR_geneset_fdr.tsv \
    --dry-run --use-conda --printshellcmds
```

Output (tail):
```
[Tue Apr 14 21:45:51 2026]
rule magma_gene_analysis:
    ...
        python /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/run_magma.py --step gene \
            --magma-binary tools/magma_v1.10/magma \
            --bfile data/reference/magma/g1000_eur \
            --pval data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz \
            --gene-annot results/pathway/magma/gene_annotation.genes.annot \
            --trait bmi \
            --sample-size 694649 \
            --out results/pathway/magma/bmi_EUR

[Tue Apr 14 21:45:51 2026]
rule magma_geneset_analysis:
    ...
        python /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/run_magma.py --step geneset \
            --magma-binary tools/magma_v1.10/magma \
            --gene-results results/pathway/magma/bmi_EUR.genes.raw \
            --set-annot results/pathway/magma/all_pathways.set \
            --out results/pathway/magma/bmi_EUR_geneset

[Tue Apr 14 21:45:51 2026]
rule magma_fdr:
    ...
        python /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/magma_fdr.py \
            --gsa results/pathway/magma/bmi_EUR_geneset.gsa.out \
            --out results/pathway/magma/bmi_EUR_geneset_fdr.tsv

Job stats:
job                       count
----------------------  -------
build_magma_set_file          1
download_msigdb               1
download_sumstats             1
harmonize_sumstats            1
magma_annotate                1
magma_fdr                     1
magma_gene_analysis           1
magma_geneset_analysis        1
total                         8
```

No-`..`-in-paths check:
```
grep -E '/[^/]*\.\./[^/]*' /tmp/tmq_verif2.log | grep -v '^\.'
```
→ (empty) → `NO_PATH_DOTDOT` (**PASS**).

The only `..` in the entire log is inside the prose `Building DAG of jobs...` ellipsis (line 1 of verif2.log) — NOT a path. All rendered shell-command script paths are absolute `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/X.py`.

Env-path WorkflowError check: **absent** (**PASS**; confirms 260414-rbv env-path fix held).

Total jobs: 8 (within expected 4-12 for the magma_fdr branch; **PASS**).

## Verification Gate 3 — all 11 script files exist at src/python/

```
ALL_11_SCRIPTS_EXIST
```

(**PASS**; verified via python3 loop over every referenced script basename.)

## Verification Gate 4 — live env msigdbr probe

```
MSIGDBR_OK
```

(**PASS**; `.snakemake/conda/f2752ef7f849ac77376134262def5328_/bin/Rscript -e 'library(msigdbr); cat("MSIGDBR_OK\n")'`.)

## Verification Gate 5 — no `..` in workflow.basedir refs

Command:
```
grep -cE 'workflow\.basedir,\s*"\.\."' src/snakemake/rules/pathway.smk
```

Output: `0` → expected `0` (**PASS**).

Secondary gates (run during Task 1 post-fix audit):
- `grep -cE 'script=str\(Path\(workflow\.basedir\) / "src" / "python" / "[a-z_0-9]+\.py"\)'` → 23 (matches on-disk script= count)
- `grep -cE '_?sys\.path\.insert\(0, str\(Path\(workflow\.basedir\) / "src" / "python"\)\)'` → 6 (matches on-disk sys.path.insert count)
- `grep -cE 'workflow\.basedir, "\.snakemake", "conda"'` → 1 (Pattern C special case)
- Total 23+6+1 = 30, matching the pre-fix audit count.

## Mamba install log tail (Task 2, Step 2)

```
Linking r-progress-1.2.3-r45hc72bb7e_2
Linking r-htmlwidgets-1.6.4-r45h785f33e_4
Linking r-tibble-3.3.1-r45h54b55ab_0
Linking r-vroom-1.7.1-r45h3697838_0
Linking r-dplyr-1.2.1-r45h3697838_0
Linking r-readr-2.2.0-r45h3697838_0
Linking r-tidyr-1.3.2-r45h3697838_0
Linking r-ggplot2-4.0.2-r45h785f33e_0
Linking r-babelgene-22.9-r45hc72bb7e_4
Linking r-plotly-4.12.0-r45hc72bb7e_0
Linking r-msigdbr-26.1.0-r45hc72bb7e_0
Linking r-gprofiler2-0.2.4-r45hc72bb7e_0

Transaction finished
```

Fallback to `conda install` triggered: **no** — the `mamba install --yes` path landed cleanly on first attempt.

**Notable solver behavior (deviation from plan assumption):** mamba resolved the combined
environment to **r-msigdbr=26.1.0 against R 4.5.3**, not the `r-msigdbr=7.5.1` pin we declared
in the yml. Reason: the live env's existing packages (r-gprofiler2, r-dplyr, r-readr, etc.)
did not have satisfiable r-base=4.3 builds for the latest r-msigdbr, so mamba upgraded the
entire R stack to 4.5 and pulled in r-msigdbr 26.1.0 (the newest noarch build). The `--yes`
flag forced acceptance of this cascade. The live env is a gitignored disposable cache, so
this is acceptable — the spec (`envs/gprofiler.yml`) remains pinned to `r-msigdbr=7.5.1` and
will be honoured the next time the env is recreated from the yml (e.g. via
`snakemake --conda-create-envs-only` or first `--use-conda` on a fresh hash directory). The
spec vs live-env drift is documented here; no repo commit is affected.

## Scope boundary check

Files touched (git status):
```
?? .planning/quick/260414-tmq-batch-fix-phase-5-bugs-from-bmi-eur-magm/
```
(Both committed source files — `src/snakemake/rules/pathway.smk` and `envs/gprofiler.yml` —
already consumed by commits `2414ea9` and `e193896` respectively; no uncommitted modifications
remain. The untracked planning directory contains PLAN.md + SUMMARY.md + any orchestrator
artifacts and is handled by the orchestrator's final docs commit.)

Files NOT touched (spot-check via `git log --oneline --name-only` HEAD~2..HEAD):
- `src/python/*.py` — no modifications
- `envs/magma.yml`, `envs/ldsc_py3.yml`, `envs/hess_py27.yml`, `envs/python_stats.yml` — no mods
- Any rule file outside `pathway.smk` — no mods
- `download_sumstats` rule body (inside `pathway.smk` at the harmonize/download boundary) — no mods
  (diff only touches the 30 path-construction lines; verified by `git diff HEAD~2 src/snakemake/rules/pathway.smk | grep -E '^[+-]' | grep -v -E '^(\+\+\+|---|\+.*str\(Path|\+.*workflow\.basedir, "\.snakemake"|-.*os\.path\.join\(workflow\.basedir, "\.\.")'` → 0 lines)

## Notes

- STATE memory cross-reference: Phase 01-02 / Phase 09 "envs/ paths use
  `Path(workflow.basedir)/'envs'/...` (no `.parent.parent`)" idiom is now extended uniformly
  to `src/python` scripts and the `.snakemake/conda` cache path. Completes the architectural
  fix started in 260414-rbv for env YAMLs.
- Live-run precondition for `bmi.EUR magma_fdr` scout is now satisfied: (1) ENV paths
  resolve (260414-rbv), (2) script paths resolve (this task), (3) `r-msigdbr` importable
  from R under `GPROFILER_ENV` (this task — both spec + live env).
- Recreating `.snakemake/conda/f2752ef7f849ac77376134262def5328_/` from scratch (e.g. by
  deleting and re-running `snakemake --use-conda`) is still blocked by the libmamba 2.5
  Anaconda-ToS prompt blocker per 260414-bmi-magma-scout findings — Carter will address
  that environment-wide issue out of scope. The in-place `mamba install -p` sidesteps it
  for this env specifically.
- No conda environments rebuilt from scratch (dry-run verification only; only the live
  gprofiler env was augmented in-place via `mamba install -p`).
- Spec-vs-live-env drift logged: yml pins `r-msigdbr=7.5.1` (R 4.3.1) but live env now has
  `r-msigdbr=26.1.0` (R 4.5.3). When the env is recreated cleanly, yml pins take effect.
- No new deferred items surfaced during Gate 1/Gate 2 dry-runs. All Phase 5 DAG-resolution
  blockers previously logged (DEF-RO7-01, DEF-RO7-02, DEF-RO7-03) remain deferred per the
  2026-04-13 decision.

## Self-Check

- [x] Gate 1 PASS (575 jobs exact parity, no WorkflowError)
- [x] Gate 2 PASS (no env-path WorkflowError, no `..` in rendered shell paths, magma_fdr DAG resolves in 8 jobs)
- [x] Gate 3 PASS (all 11 scripts exist at `src/python/X.py`)
- [x] Gate 4 PASS (MSIGDBR_OK emitted by live env Rscript)
- [x] Gate 5 PASS (0 matches for `workflow.basedir, ".."` pattern)
- [x] Scope boundary: only `pathway.smk` + `gprofiler.yml` modified (2 commits, 31 insertions, 30 deletions total)
