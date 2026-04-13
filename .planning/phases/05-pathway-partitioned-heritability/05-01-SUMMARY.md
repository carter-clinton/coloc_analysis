---
phase: 05-pathway-partitioned-heritability
plan: 01
subsystem: pathway
tags: [magma, ldsc, hess, gprofiler, gmt, conda, snakemake, partitioned-heritability]

# Dependency graph
requires:
  - phase: 02-qtl-colocalization
    provides: "QTL coloc results, negative_controls.yaml gene sets, harmonized sumstats format"
provides:
  - "4 conda env specs (MAGMA, LDSC, HESS, g:Profiler) for Phase 5 tools"
  - "8 custom cardiometabolic pathway GMT gene sets curated from KEGG + GWAS literature"
  - "3 negative control GMT gene sets (HLA, cosmetic, blood group) from neg_ctrl config"
  - "3 utility scripts: GMT-to-MAGMA .set converter, LDSC annotation builder, sumstats munger"
  - "sumstats_utils.py shared module with compute_effective_n for cross-method use"
  - "pathway.smk Snakemake rule skeleton: 6 download rules + 10 placeholder analysis rules"
  - "pipeline.yaml pathway section with all reference data paths and analysis parameters"
  - "35 passing Phase 5 tests across 6 test modules"
affects: [05-02-magma-gene-set-analysis, 05-03-ldsc-partitioned-h2, 05-04-hess-gprofiler, 05-05-aggregation-permutation]

# Tech tracking
tech-stack:
  added: [magma-v1.10, ldsc-python3, hess-py27, gprofiler2-r, msigdbr]
  patterns: [GMT gene set format, MAGMA .set format, LDSC binary annotation, effective-N computation]

key-files:
  created:
    - envs/magma.yml
    - envs/ldsc_py3.yml
    - envs/hess_py27.yml
    - envs/gprofiler.yml
    - config/pathway_sets/custom_cardiometabolic.gmt
    - config/pathway_sets/negative_controls.gmt
    - src/python/sumstats_utils.py
    - src/python/build_magma_geneset.py
    - src/python/build_ldsc_annot.py
    - src/python/munge_sumstats_ldsc.py
    - src/snakemake/rules/pathway.smk
    - tests/phase5/conftest.py
    - tests/phase5/test_magma_geneset.py
    - tests/phase5/test_ldsc_partitioned.py
    - tests/phase5/test_gprofiler.py
    - tests/phase5/test_ldsc_seg.py
    - tests/phase5/test_negative_controls.py
    - tests/phase5/test_permutation_null.py
  modified:
    - config/pipeline.yaml
    - src/snakemake/schemas/pipeline.schema.yaml
    - Snakefile

key-decisions:
  - "HESS env uses defaults channel first (conda-forge dropped Python 2.7)"
  - "sumstats_utils.py as shared module prevents effective-N reimplementation across methods"
  - "Placeholder rules use pass in run block (not empty shell) for Snakemake compatibility"
  - "Test files define PROJECT_ROOT locally instead of importing from conftest to avoid missing tests/__init__.py"

patterns-established:
  - "GMT format for pathway gene sets: SET_NAME<tab>DESCRIPTION<tab>GENE1<tab>GENE2..."
  - "Conda env naming: tool_name (magma_helpers, ldsc_py3, hess_py27, gprofiler_r)"
  - "Download rules: wget --max-redirect=3 --timeout=300 + size/checksum validation"
  - "Phase 5 test pattern: PROJECT_ROOT defined per-file, src/python on sys.path"

requirements-completed: [REQ-7]

# Metrics
duration: 14min
completed: 2026-04-13
---

# Phase 5 Plan 1: Infrastructure Summary

**4 conda envs, 11 GMT pathway gene sets, 4 utility scripts, 16-rule pathway.smk skeleton, and 35 passing tests for pathway + partitioned heritability analysis**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-13T20:16:19Z
- **Completed:** 2026-04-13T20:30:35Z
- **Tasks:** 3/3
- **Files modified:** 22

## Accomplishments
- Created conda environment specs for all 4 analytical tools (MAGMA Py3.11, LDSC Py3.11 via abdenlab fork, HESS Py2.7, g:Profiler R 4.2+)
- Curated 8 custom cardiometabolic pathway gene sets from KEGG + GWAS literature with 15-18 genes each
- Built 3 utility scripts (build_magma_geneset.py, build_ldsc_annot.py, munge_sumstats_ldsc.py) with shared effective-N logic
- Established pathway.smk with 6 download rules (MAGMA binary, MAGMA ref, LDSC baseline, LDSC-SEG, MSigDB, HESS) and 10 placeholder analysis rules
- Extended pipeline.yaml with all 20+ pathway reference data paths and analysis parameters
- Full test scaffolding: 35 tests across 6 modules, all passing under smoke_dev pytest

## Task Commits

Each task was committed atomically:

1. **Task 1: Conda environments + pipeline.yaml + schema + Snakefile** - `e349129` (feat)
2. **Task 2: GMT gene sets + utility scripts + pathway.smk skeleton** - `5c5f386` (feat)
3. **Task 3: Test scaffolding for all Phase 5 components** - `3e112c5` (test)

## Files Created/Modified
- `envs/magma.yml` - MAGMA Python helper environment (Py3.11, pandas, numpy)
- `envs/ldsc_py3.yml` - LDSC Python 3 fork environment (abdenlab/ldsc-python3)
- `envs/hess_py27.yml` - HESS Python 2.7 isolated environment (numpy 1.16, scipy 1.2)
- `envs/gprofiler.yml` - g:Profiler R environment (r-base 4.2+, r-gprofiler2)
- `config/pathway_sets/custom_cardiometabolic.gmt` - 8 curated cardiometabolic pathway gene sets
- `config/pathway_sets/negative_controls.gmt` - 3 negative control gene sets (HLA, cosmetic, blood group)
- `config/pipeline.yaml` - Extended with pathway section (20+ reference data paths, analysis params)
- `src/snakemake/schemas/pipeline.schema.yaml` - Added optional pathway object schema
- `Snakefile` - Added pathway.smk include
- `src/python/sumstats_utils.py` - Shared effective-N computation and TRAIT_TYPE mapping
- `src/python/build_magma_geneset.py` - GMT-to-MAGMA .set converter with gene.loc mapping
- `src/python/build_ldsc_annot.py` - Gene-set-to-LDSC binary annotation builder (per-chrom .annot.gz)
- `src/python/munge_sumstats_ldsc.py` - Harmonized sumstats to LDSC format with T-05-04 validation
- `src/snakemake/rules/pathway.smk` - 16 Snakemake rules (6 download + 10 placeholder)
- `tests/phase5/conftest.py` - Shared fixtures (mock sumstats, gene.loc, bim, GMT paths)
- `tests/phase5/test_magma_geneset.py` - 9 tests for GMT format and MAGMA .set conversion
- `tests/phase5/test_ldsc_partitioned.py` - 10 tests for munge, effective-N, annotation format
- `tests/phase5/test_gprofiler.py` - 5 tests for background construction and evcodes config
- `tests/phase5/test_ldsc_seg.py` - 4 tests for tissue annotation paths
- `tests/phase5/test_negative_controls.py` - 3 tests for method coverage and gene overlap (REQ-7)
- `tests/phase5/test_permutation_null.py` - 4 tests for permutation config and rule existence

## Decisions Made
- HESS env uses `defaults` channel first because conda-forge dropped Python 2.7 support
- Created sumstats_utils.py as a shared module to prevent reimplementation of effective-N computation across MAGMA, LDSC, and HESS wrappers
- Placeholder analysis rules use `pass` in `run:` block (not empty `shell:`) for Snakemake compatibility
- Test files define PROJECT_ROOT locally to avoid dependency on tests/__init__.py package structure

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] GMT files missing trailing newlines**
- **Found during:** Task 2 verification
- **Issue:** `wc -l` reported 7 and 2 instead of 8 and 3 because files lacked POSIX trailing newlines
- **Fix:** Appended trailing newlines to both GMT files
- **Files modified:** config/pathway_sets/custom_cardiometabolic.gmt, config/pathway_sets/negative_controls.gmt
- **Verification:** `wc -l` now returns 8 and 3 as expected
- **Committed in:** 5c5f386 (part of Task 2 commit)

**2. [Rule 3 - Blocking] Test import failures from `tests.phase5.conftest`**
- **Found during:** Task 3 pytest execution
- **Issue:** `from tests.phase5.conftest import PROJECT_ROOT` failed because `tests/` has no `__init__.py`
- **Fix:** Replaced conftest imports with local `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` in each test file
- **Files modified:** All 6 test files
- **Verification:** All 35 tests pass
- **Committed in:** 3e112c5 (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (2 blocking issues)
**Impact on plan:** Both auto-fixes necessary for correctness. No scope creep.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| 10 placeholder `pass` rules | src/snakemake/rules/pathway.smk | Intentional: analysis rules to be implemented in Plans 05-02 through 05-05 |

These stubs are intentional infrastructure per the plan objective ("establishes the foundation without running any analysis") and do not block the plan's goal.

## Issues Encountered
None beyond the two auto-fixed blocking issues documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 4 conda env specs ready for `conda env create` in Plans 02-05
- Reference data download rules ready to populate data/reference/ directories
- Utility scripts ready for integration into analysis rules
- 35 tests provide regression safety for subsequent plan implementations
- Plan 05-02 (MAGMA gene-set analysis) can proceed immediately

## Self-Check: PASSED

- 18/18 created files found
- 3/3 task commits found (e349129, 5c5f386, 3e112c5)
- 35/35 tests passing

---
*Phase: 05-pathway-partitioned-heritability*
*Completed: 2026-04-13*
