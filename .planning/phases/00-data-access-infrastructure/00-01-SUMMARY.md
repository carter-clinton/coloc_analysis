---
phase: 00-data-access-infrastructure
plan: 01
subsystem: infra
tags: [snakemake, conda, yaml, config, gwas, sumstats, lsf, json-schema]

# Dependency graph
requires: []
provides:
  - "config/pipeline.yaml: single source of truth for all filesystem paths and pipeline parameters"
  - "config/datasets.yaml: per-source column maps for 12 GWAS datasets (8 legacy + 4 new ancestry)"
  - "config/cluster_lsf.yaml: LSF cluster profile for Snakemake HPC submission"
  - "envs/r_coloc.yml, envs/python_stats.yml, envs/plink.yml: pinned conda environments"
  - "src/R/utils/load_config.R: R config loader for pipeline.yaml"
  - "data/manifest.yaml: 20-source data catalog with genome build and liftover annotations"
  - "src/snakemake/schemas/pipeline.schema.yaml + datasets.schema.yaml: JSON Schema validation"
affects: [00-02, 00-03, 00-04, 01-sumstats-harmonization, 02-qtl-coloc]

# Tech tracking
tech-stack:
  added: [json-schema-draft-07, r-yaml]
  patterns: [hierarchical-yaml-config, column-map-aliases, per-rule-conda-envs]

key-files:
  created:
    - config/pipeline.yaml
    - config/datasets.yaml
    - config/cluster_lsf.yaml
    - envs/r_coloc.yml
    - envs/python_stats.yml
    - envs/plink.yml
    - src/R/utils/load_config.R
    - data/manifest.yaml
    - src/snakemake/schemas/pipeline.schema.yaml
    - src/snakemake/schemas/datasets.schema.yaml
  modified: []

key-decisions:
  - "Removed hardcoded rscript_bin path from finemap config -- Snakemake conda envs handle R resolution (D-25)"
  - "Fixed legacy Snakemake version pin from 8.* to 7.32.4 in python_stats.yml (actual installed version)"
  - "Used =version format (not =version=build) for conda pins to allow platform-specific build resolution"
  - "Added helper functions get_traits, get_ancestries, get_trait_ancestries to R config loader beyond plan spec"

patterns-established:
  - "Pattern: All paths relative to project root in config/pipeline.yaml, never hardcoded absolute"
  - "Pattern: Column map aliases in datasets.yaml as arrays of candidate column names per canonical field"
  - "Pattern: Per-rule conda environment isolation via envs/*.yml files"
  - "Pattern: Data manifest tracks genome_build + needs_liftover for every source"

requirements-completed: [REQ-1, REQ-9, REQ-12]

# Metrics
duration: 11min
completed: 2026-04-10
---

# Phase 0 Plan 1: Config Foundation Summary

**10-file config layer with pipeline.yaml single source of truth, 12-dataset column maps (4 new ancestry), 3 pinned conda envs, R config loader, 20-source data manifest, and JSON Schema validation**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-10T18:36:44Z
- **Completed:** 2026-04-10T18:48:12Z
- **Tasks:** 2
- **Files created:** 10

## Accomplishments
- Created the single source of truth config layer (pipeline.yaml) with GRCh37 primary build, 4 ancestries (EUR/AFR/EAS/HIS), and all paths relative
- Extended legacy datasets.yaml from 8 to 12 entries by adding BBJ EAS, Gurdasani AFR BMI, Hoffmann AFR HTN, and PAGE Hispanic datasets
- Pinned all conda environments with exact versions, fixing the legacy Snakemake 8.* bug to 7.32.4
- Built a comprehensive 20-source data manifest tracking genome build, liftover needs, and access model for every data source in the project

## Task Commits

Each task was committed atomically:

1. **Task 1: Create config/pipeline.yaml, config/datasets.yaml, config/cluster_lsf.yaml, and validation schemas** - `3986b91` (feat)
2. **Task 2: Create pinned conda environments and R config loader** - `a3511e3` (feat)

## Files Created/Modified
- `config/pipeline.yaml` - Single source of truth for all paths, traits, ancestries, and pipeline parameters
- `config/datasets.yaml` - 12 dataset entries with column maps for GWAS sumstats harmonization
- `config/cluster_lsf.yaml` - LSF cluster profile with defaults + 7 per-rule resource allocations
- `src/snakemake/schemas/pipeline.schema.yaml` - JSON Schema Draft-07 for pipeline config validation
- `src/snakemake/schemas/datasets.schema.yaml` - JSON Schema Draft-07 for datasets config validation
- `envs/r_coloc.yml` - Pinned R 4.4.2 + coloc 5.2.3 + susieR 0.14.2 + hyprcoloc 1.0 environment
- `envs/python_stats.yml` - Pinned Python 3.11 + Snakemake 7.32.4 environment (fixes legacy 8.* bug)
- `envs/plink.yml` - Pinned PLINK 1.9 + 2.0 + bcftools 1.21 environment
- `src/R/utils/load_config.R` - R config loader with load_pipeline_config(), resolve_path(), and helper functions
- `data/manifest.yaml` - 20-source data catalog with genome build, liftover, and access annotations

## Decisions Made
- **Removed rscript_bin:** Legacy config had a hardcoded `/share/clintonlab/...` path for Rscript. Removed entirely per D-25 (Snakemake conda envs handle R resolution).
- **Fixed Snakemake version:** Legacy env pinned `snakemake==8.*` but actual installed version is 7.32.4. Fixed to `snakemake=7.32.4` per RESEARCH.md recommendation to defer 8.x migration.
- **Conda pin format:** Used `=version` format (not `=version=build`) for cross-platform portability on the NCSU HPC cluster.
- **Extended R config loader:** Added `get_traits()`, `get_ancestries()`, and `get_trait_ancestries()` helper functions beyond the plan's minimal spec for better downstream usability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added file existence check to load_pipeline_config()**
- **Found during:** Task 2
- **Issue:** Plan's R config loader template did not check whether the config file actually exists before trying to read it
- **Fix:** Added `if (!file.exists(config_path)) stop(...)` check before yaml::read_yaml()
- **Files modified:** src/R/utils/load_config.R
- **Verification:** Function will now give a clear error message instead of a cryptic yaml parsing error
- **Committed in:** a3511e3 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Defensive programming addition; no scope creep.

## Issues Encountered
None

## Known Stubs
None -- all files contain complete, functional content. No placeholder values that affect downstream operation.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Config layer complete: Plan 03 (Snakemake rule refactoring) can wire `validate()` calls against the new schemas
- Plan 03 can reference `config/pipeline.yaml` paths in all Snakemake rules
- Plan 02 (data registration/downloads) can use `data/manifest.yaml` as the authoritative source catalog
- Conda environments ready for Plan 03's `conda:` directives in Snakemake rules
- No blockers for any downstream plans in Phase 0

## Self-Check: PASSED

All 10 created files verified present on disk. Both task commits (3986b91, a3511e3) verified in git log.

---
*Phase: 00-data-access-infrastructure*
*Completed: 2026-04-10*
