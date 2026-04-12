# Phase 1 Deferred Items

Out-of-scope issues discovered during execution that are NOT caused by current plan changes.
Tracked here for future phases; NOT fixed in this plan (scope boundary).

## From Plan 01-01 (Wave 1 execution, 2026-04-12)

### DEF-01-01: `snakemake --use-conda --dry-run` fails on env path resolution

**Discovered by:** Task 1-01-08 dry-run verify step
**Symptom:** Running `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda --dry-run` raises:
```
WorkflowError: Failed to open source file
/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/envs/python_stats.yml
FileNotFoundError: [Errno 2] No such file or directory
```

**Verification this is pre-existing:** `git stash` of my Phase 1 edits, re-run same command, same error. The issue exists on the unmodified finemap.smk from Phase 0.

**Root cause hypothesis:** Snakemake 7.32.4 resolves `conda: "envs/r_coloc.yml"` relative to the *included* rule file at `src/snakemake/rules/finemap.smk`, producing `src/snakemake/rules/envs/python_stats.yml`. The actual conda env files live at `envs/r_coloc.yml` (project root). Fix options:
- Use absolute paths: `conda: str(Path(workflow.basedir) / "envs" / "r_coloc.yml")`
- Symlink `src/snakemake/rules/envs -> ../../../envs`
- Migrate to workflow-profile pattern

**Impact:** Dry-run WITHOUT `--use-conda` works fine (29 jobs, 11 rules, DAG valid). Full conda-driven dry-runs and real runs are blocked until this is fixed.

**Resolution target:** Phase 1 Plan 01-02 or 01-03 (LD + real smoke test plans) — must be fixed before the first real Wave 1 execution.

**Workaround for Wave 1 verification:** Plan 01-01 uses `snakemake --dry-run` (no conda flag) which validates DAG topology including the new `.fit.rds` output and `--policy` CLI flag. This is sufficient for Wave 1 gating since no real R execution happens until Wave 5/smoke.

### DEF-01-02: `envs/r_coloc.yml` is not yet materialized on disk

**Discovered by:** Task 1-01-06 test_fit_roundtrip.R runtime
**Symptom:** No pre-built conda env with the complete R stack (susieR + coloc + testthat + yaml + digest + data.table + Matrix + optparse + jsonlite).

**Workaround applied:** Created `.r_lib_phase1/` (gitignored) as a CRAN-installed `testthat` library path bolted onto the existing `la_multitrait_r` conda env (which has susieR + coloc + yaml + ... but not testthat). Compiled `brio`, `diffobj`, `waldo`, `pkgload`, `testthat` from source using system `gcc` (11.5.0) — conda env shipped without `x86_64-conda-linux-gnu-cc`.

**Usage:**
```bash
export R_LIBS_USER=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.r_lib_phase1
export PHASE1_PROJECT_ROOT=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e 'testthat::test_dir("tests/testthat-phase1")'
```

**Resolution target:** Phase 1 Plan 01-02 or 01-03: materialize `envs/r_coloc.yml` via `conda env create -f envs/r_coloc.yml -p /rs1/researchers/c/ckclinto/conda_envs/r_coloc_phase1` so `--use-conda` can find the env (together with DEF-01-01).

### DEF-01-04: `config/regions_curated.csv` is GRCh37; HGDP+1kG v2 BCFs are GRCh38

**Discovered by:** Plan 01-03 Task 1-03-00 preflight (step 13)
**Symptom:** `config/pipeline.yaml` declares `genome_build: GRCh37` and the
curated-region coordinates in `config/regions_curated.csv` are GRCh37
(FTO ~16:53.8-54.4 Mb, MC4R ~18:56-56.6 Mb, APOE ~19:44-46 Mb etc.), but
the gnomAD v3.1.2 HGDP+1kG v2 phased BCFs use GRCh38 contigs
(`##contig=<ID=chr22>`; chr22 in GRCh38 starts at ~10.5 Mb with different
coordinates).

**Impact:** `build_hgdp_1kg_ld` rule plumbing (Plan 01-03 Task 1-03-02)
can be committed and dry-run-gated without fixing this, but the rule
cannot be executed for real until either:
- (a) curated regions are lifted GRCh37 -> GRCh38 via UCSC liftOver, or
- (b) a per-ancestry region-coordinate layer is added to the pipeline
  schema and the rule consumes lifted coordinates, or
- (c) the panel is treated as GRCh38 and UKBB-LD (GRCh37) vs HGDP+1kG
  (GRCh38) is managed as a two-build pipeline with explicit tagging.

**Why not fix in Plan 01-03:** Rule 4 -- this is architectural (schema +
new liftover stage + policy for mixing builds across panels). Plan 01-03
is a plumbing plan (Rule 2 scope only); a liftover decision affects every
downstream plan that consumes LD and needs its own plan.

**Resolution target:** Plan 01-04 or 01-05 (first plan that actually
executes `build_hgdp_1kg_ld` for real). Likely option (a) -- UCSC liftOver
of `config/regions_curated.csv` to a companion `regions_curated_grch38.csv`
with a `genome_build` column -- is lowest-friction. A deliberate
decision point should be raised there.

**Recorded in:** `01-03-scope-decision.md` Rationale section.

### DEF-01-05: Legacy `build_ld_rds` rule fires for `TRANS` ancestry without a sample list

**Discovered by:** Plan 01-03 Task 1-03-02 full-pipeline dry-run
**Symptom:** `snakemake --dry-run` (no target) raises
`MissingInputException` on `data/raw/1kg/TRANS.samples` because the
legacy `build_ld_rds` rule loops over `config.ancestries + one trait's
trait_ancestries`, picking up `TRANS` from `trait_ancestries.t2d` even
though `ancestries` top-level list excludes it and no
`build_1kg_sample_lists` recipe writes `TRANS.samples`.

**Verification this is pre-existing:** `git stash` reproduction without
Plan 01-03 edits (step run 2026-04-11) hits the same error.

**Impact:** Does NOT block `snakemake --dry-run build_hgdp_1kg_ld`
(single-rule target) which is what the Plan 01-03 verify gate requires.
Only blocks all-target dry-runs.

**Resolution target:** Plan 01-04 or later. Likely fix: add a
`TRANS.samples` stub (meta-ancestry covering all 1kG AFR+EUR+EAS) or
guard the `build_ld_rds` output list with an ancestry filter.

**Recorded in:** `.planning/phases/01-coloc-susie-fine-mapping-spine/deferred-items.md`.

### DEF-01-03: Unrelated unstaged changes in working tree at start of Plan 01-01

**Discovered by:** `git status` at start of execution
**Symptom:** Two files had unstaged modifications unrelated to Plan 01-01:
- `.claude/settings.json`
- `.planning/config.json`

**Action taken:** Left untouched; not staged by any Plan 01-01 commit. No interference with Phase 1 work.

**Resolution target:** Out of scope — user may commit/revert these separately.
