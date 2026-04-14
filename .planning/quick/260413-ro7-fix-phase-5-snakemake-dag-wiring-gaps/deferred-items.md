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

## DEF-RO7-02: pathway rules iterate config trait_ancestries beyond disk availability

- **Discovered during:** 2026-04-13 post-RO7 smoke-test triage (narrowing
  dry-run to per-branch targets after DEF-RO7-01 surfaced).
- **File:** `src/snakemake/rules/sumstats.smk` (`dataset_descriptor` at
  line 34, lambda at line 135); also affects `src/snakemake/rules/pathway.smk`
  expand() calls at lines 752-753, 908-909, 916-917, 1709.
- **Error (from LDSC/LDSC-SEG/HESS per-branch dry-run):**
  ```
  File src/snakemake/rules/sumstats.smk, line 135, in <lambda>
  File src/snakemake/rules/sumstats.smk, line 34, in dataset_meta
  File src/legacy/region_analysis/scripts/dataset_config.py, line 61, in dataset_descriptor
  # triggered by wildcards trait=bmi, ancestry=AFR
  ```
- **Root cause:** `config/pipeline.yaml` declares `trait_ancestries` that
  include combos not harmonized on disk (e.g., `bmi: [EUR, AFR, EAS]` — only
  `bmi.EUR.tsv.bgz` exists). Pathway rules expand across the full config,
  so Snakemake tries to produce the missing files via `harmonize_sumstats`,
  which raises because no source is registered for those combos.
- **Harmonized sumstats actually on disk** (at `data/processed/region_analysis/sumstats_harmonized_fixed/`):
  asthma.{EUR,AFR}, bmi.EUR, hypertension.EUR, stroke.{EUR,AFR}, t2d.{EUR,AFR,TRANS}.
- **Why deferred:** Outside RO7 scope (RO7 = single-file fix to pathway.smk).
  This is a cross-file iteration policy issue that needs a design decision
  (iterate config vs. disk vs. explicit allowlist).
- **Impact:** Blocks per-branch smoke testing of MAGMA / LDSC partitioned /
  LDSC-SEG / HESS in isolation — even though those branches don't need
  tier_ab data or LD reference matrices.
- **Recommended follow-up:** A follow-up quick task to either (a) filter
  pathway expand() calls to trait×ancestry combos that have harmonized
  files on disk, or (b) add an explicit allowlist in pipeline.yaml
  (e.g., `pathway.smoke_trait_ancestries`) that defaults to the intersection
  of config and disk.

## DEF-RO7-03: config harmonized_sumstats path mismatch

- **Discovered during:** 2026-04-13 post-RO7 prerequisite assessment.
- **File:** `config/pipeline.yaml`, key `paths.harmonized_sumstats`.
- **Issue:** Config declares `harmonized_sumstats: "data/processed/sumstats_harmonized"`
  but actual data lives at `data/processed/region_analysis/sumstats_harmonized_fixed/`.
  The `use_fixed_sumstats: true` flag elsewhere in config should be controlling
  this but isn't applied to `paths.harmonized_sumstats`.
- **Why deferred:** RO7 forbids config edits.
- **Impact:** Will surface only after DEF-RO7-02 is resolved — at that point,
  any pathway rule consuming the config path will fail to find files. Not
  the proximate cause of current smoke-run failures.
- **Recommended follow-up:** A single-line config fix (or resolve
  `use_fixed_sumstats` conditionally) in the same quick task that addresses
  DEF-RO7-02.

---

## Smoke-testing blockers — summary

Full `snakemake all_pathway --dry-run` is blocked by three pre-existing
(non-RO7) issues, in the order they surface:

1. **DEF-RO7-02** blocks 4 of 6 branches (MAGMA, LDSC partitioned, LDSC-SEG,
   HESS) — surfaces immediately via trait×ancestry expand().
2. **DEF-RO7-01** blocks the g:Profiler branch + `all_pathway` aggregate —
   surfaces via Phase 2 tier_assignments → Phase 1 LD reference → TRANS.samples.
3. **DEF-RO7-03** will surface after DEF-RO7-02 is fixed.

Decision (2026-04-13): Defer smoke testing until Phase 9 planning. The
pathway.smk DAG wiring is confirmed correct by RO7 (no pathway.smk rules
produce MissingInputException after RO7). Unit tests pass (100/100).
Phase 9 replication will force re-exercising Phase 0/1/2 data paths,
at which point these deferred items will surface in natural context
with relevant data on hand.
