# Deferred Items — RO7 (Phase 5 DAG wiring)

Out-of-scope issues discovered during execution. These are NOT caused by RO7's
pathway.smk edits; they are pre-existing issues in OTHER Snakemake files that
surface only once pathway.smk's download→consumer DAG edges resolve.

## DEF-RO7-01: TRANS ancestry sample list missing in ld_reference.smk

- **Discovered during:** Task 1 dry-run after pathway.smk wiring completed.
- **File:** `src/snakemake/rules/ld_reference.smk`, rule `build_ld_rds`
  (line 168).
- **Error:**
  ```
  MissingInputException in rule build_ld_rds:
    affected files: data/raw/1kg/TRANS.samples
    wildcards: ancestry=TRANS, region=FTO_16q12
  ```
- **Root cause:** `rule build_1kg_sample_lists` writes per-ancestry .samples
  files, but the `TRANS` pseudo-ancestry (configured for `t2d` in
  `config/pipeline.yaml` line 46) is not produced by any rule. The sample-list
  builder appears to cover EUR/AFR/EAS/AMR but not a combined TRANS list.
- **Why deferred:** The RO7 plan explicitly scopes the diff to
  `src/snakemake/rules/pathway.smk` only and forbids config edits
  (success_criteria line 299). Fixing this requires editing
  `ld_reference.smk` and/or `build_1kg_sample_lists.py`, which is outside
  the plan's allowed surface.
- **Impact:** End-to-end `snakemake all_pathway --dry-run` still exits
  non-zero, but all of the MissingInputException cases the plan explicitly
  enumerated (g1000_eur.bim, baselineLD.*, weights.*, 1000G.EUR.QC.*,
  Multi_tissue_*.ldcts, hess_ld_panel.*) are now resolved.
- **Recommended follow-up:** Open a new quick task scoped to
  `ld_reference.smk` that either (a) adds a `TRANS.samples` generator
  (union of EUR+AFR+EAS+AMR) or (b) gates the ancestry list to only the
  four continental labels at DAG-expand time.
