---
task: 260414-rbv
title: fix Phase 5 conda env path bug in pathway.smk:58-61
date: 2026-04-14
status: complete
files_modified: [src/snakemake/rules/pathway.smk]
commit: 0f1f248
---

# Quick task 260414-rbv — SUMMARY

## Bug

`src/snakemake/rules/pathway.smk` lines 58-61 computed conda env paths as
`os.path.join(workflow.basedir, "..", "..", "..", "envs", X.yml)`.
`workflow.basedir` already resolves to the project root
(`/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis`), so stripping
three `..` segments escapes the project and produces
`/gpfs_common/share01/clintonlab/envs/X.yml` — a directory outside the repo
where no env files exist. The bug was latent because `--dry-run` skips
conda-env file-existence validation; `--use-conda` invokes DAG-time env-file
validation and surfaces `WorkflowError: Failed to open source file
/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/../../../envs/magma.yml`.
Five other rule files in `src/snakemake/rules/` (ld_reference, coloc, mr, pgs,
multitrait) already use the correct `Path(workflow.basedir) / "envs" / X.yml`
idiom, per the Phase 01-02 and Phase 09 STATE memory "DEF-01-02 pattern".

## Fix

5-line diff applied to `src/snakemake/rules/pathway.smk` (commit `0f1f248`):

```diff
 import os
+from pathlib import Path

 PATHWAY_CFG = config.get("pathway", {})
 ...
 # Conda env paths (absolute, per DEF-01-02 pattern)
-MAGMA_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "magma.yml"))
-LDSC_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "ldsc_py3.yml"))
-HESS_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "hess_py27.yml"))
-GPROFILER_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "gprofiler.yml"))
+MAGMA_ENV = str(Path(workflow.basedir) / "envs" / "magma.yml")
+LDSC_ENV = str(Path(workflow.basedir) / "envs" / "ldsc_py3.yml")
+HESS_ENV = str(Path(workflow.basedir) / "envs" / "hess_py27.yml")
+GPROFILER_ENV = str(Path(workflow.basedir) / "envs" / "gprofiler.yml")
```

`git diff --stat`: `1 file changed, 5 insertions(+), 4 deletions(-)`.
`import os` retained (still used by `os.path.join` / `os.path.exists`
elsewhere in the module).

## Verification 1 — baseline `all_pathway --dry-run` (no regression)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run
```

Output (tail — Job stats summary table):
```
Job stats:
job                              count
-----------------------------  -------
aggregate_pathway_results            1
aggregate_qtl_coloc                  1
all_pathway                          1
assign_tiers                         1
build_1kg_sample_lists               1
build_coloc_manifest                 1
build_finemap_manifest               1
build_gprofiler_background           1
build_ld_rds                        24
build_magma_set_file                 1
build_neg_ctrl_manifest              1
build_qtl_coloc_manifest             1
build_tissue_n_lookup                1
collect_region_variants             12
download_msigdb                      1
download_sumstats                    8
extract_tier_ab_genes                1
filter_finemap_summary               1
gprofiler_enrichment                 1
gprofiler_negative_controls          1
harmonize_sumstats                   8
hess_aggregate                       1
hess_combine                        13
hess_compare_pleio                  13
hess_format_sumstats                 8
hess_local_rhog                    286
hess_validate_panel                  1
ldsc_aggregate_h2                    1
ldsc_build_custom_annotations        1
ldsc_compute_custom_ld_scores       22
ldsc_munge                           8
ldsc_partitioned_h2                  8
ldsc_seg_chromatin                   8
ldsc_seg_gene_expr                   8
ldsc_seg_shared_tissues              1
magma_annotate                       1
magma_fdr                            8
magma_gene_analysis                  8
magma_geneset_analysis               8
permutation_aggregate                1
permutation_null_genesets            1
run_curated_negative_controls        1
run_finemap                         96
summarize_coloc_results              1
summarize_finemap_results            1
validate_negative_controls           1
total                              575

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Job total: **575** (matches 260414-qsk baseline — no regression). No WorkflowError.

## Verification 2 — `magma_fdr --dry-run --use-conda` (originally-failing command)

Command:
```
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv --dry-run --use-conda
```

Output (tail — Job stats summary table):
```
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

Reasons:
    (check individual jobs above for details)
    input files updated by another job:
        build_magma_set_file, harmonize_sumstats, magma_fdr, magma_gene_analysis, magma_geneset_analysis
    missing output files:
        build_magma_set_file, download_msigdb, download_sumstats, magma_annotate, magma_gene_analysis, magma_geneset_analysis
    updated input files:
        harmonize_sumstats

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Exit code: **0**. No `WorkflowError: Failed to open source file .../envs/magma.yml`.
Env path now resolves to `project_root/envs/magma.yml` (and siblings
`ldsc_py3.yml`, `hess_py27.yml`, `gprofiler.yml`), all of which exist on disk
per `ls envs/`.

## Notes

- STATE memory cross-reference: Phase 01-02 "DEF-01-02 pattern" and Phase 09
  "envs/ paths use `Path(workflow.basedir)/'envs'/...` (no .parent.parent)" —
  same idiom, now consistently applied across all of `src/snakemake/rules/*.smk`.
- No other rule files touched; no other `pathway.smk` lines touched beyond the
  1 import + 4 ENV constants.
- A separate line (pathway.smk:1164) contains
  `workflow.basedir, "..", "..", "..", ".snakemake", "conda"` for a conda-cache
  path lookup — this is **unrelated to env yml resolution** and out of scope
  for this quick task (constraint: "DO NOT touch any other line of pathway.smk").
- No conda environments built (dry-run only — Carter will build envs on demand
  at real-data launch per STATE directive).
- Phase 5 real-data execution — whether via narrow `magma_fdr` target or full
  `all_pathway` LSF launch — is now free of this particular latent env-path
  bug.

## Self-Check: PASSED

- File `src/snakemake/rules/pathway.smk` modified (5 lines changed — 1 import
  added, 4 ENV constants rewritten).
- Commit `0f1f248` present in `git log`.
- `grep -nE 'str\(Path\(workflow\.basedir\) / "envs"' src/snakemake/rules/pathway.smk | wc -l` → `4`.
- `grep -n 'from pathlib import Path' src/snakemake/rules/pathway.smk` → 1 match (line 21).
- Both verification gates PASS: 575-job parity + magma_fdr --use-conda exit 0.
