---
phase: 02-3-way-qtl-colocalization
plan: 01
subsystem: infra
tags: [liftover, pyliftover, grch38, config, conda, yaml, pytest, qtl-fixtures]

# Dependency graph
requires:
  - phase: 01-coloc-susie-fine-mapping-spine
    provides: ".fit.rds outputs, susie_policy.yaml, regions_curated.csv"
provides:
  - "GRCh38-lifted region coordinates (config/regions_curated_grch38.csv)"
  - "PP.H4 threshold sweep config (config/pph4_thresholds.yaml)"
  - "Negative control gene sets (config/negative_controls.yaml)"
  - "QTL source metadata (config/qtl_sources.yaml)"
  - "Conda env spec for QTL processing (envs/qtl_processing.yml)"
  - "Variant ID mapping utility (src/python/variant_id_map.py)"
  - "4 synthetic QTL fixture files for integration tests"
  - "LPA/KIV-2 added to susie_policy.yaml complex regions"
affects: [02-02, 02-03, 02-04, 02-05, phase-05, phase-09]

# Tech tracking
tech-stack:
  added: [pyliftover, synapseclient, crossmap, pyarrow, pybedtools, pysam]
  patterns: ["Config-driven YAML with yaml.safe_load() only (T-02-02)", "GRCh37+GRCh38 dual-coordinate CSV schema", "eQTL Catalogue variant_id format: chr{chrom}_{pos}_{ref}_{alt}"]

key-files:
  created:
    - config/regions_curated_grch38.csv
    - config/pph4_thresholds.yaml
    - config/negative_controls.yaml
    - config/qtl_sources.yaml
    - envs/qtl_processing.yml
    - src/python/liftover_regions.py
    - src/python/variant_id_map.py
    - tests/phase2/__init__.py
    - tests/phase2/conftest.py
    - tests/phase2/test_liftover.py
    - tests/phase2/test_config_validation.py
    - tests/phase2/generate_qtl_fixtures.py
    - tests/toy_3locus/data/qtl/eqtl_mock.tsv.gz
    - tests/toy_3locus/data/qtl/sqtl_mock.tsv.gz
    - tests/toy_3locus/data/qtl/pqtl_mock.tsv.gz
    - tests/toy_3locus/data/qtl/sceqtl_mock.tsv.gz
  modified:
    - config/susie_policy.yaml

key-decisions:
  - "pyliftover installed into smoke_dev env to generate actual lifted coordinates rather than hardcoding"
  - "Chain file downloaded from UCSC to data/external/liftover/ (gitignored) with >100KB tamper check"
  - "QTL fixture generator uses seed=42 for reproducibility, 150 rows per file"

patterns-established:
  - "tests/phase2/ test scaffold with conftest.py providing config fixtures via yaml.safe_load()"
  - "Dual-coordinate CSV schema (start_grch37/end_grch37/start_grch38/end_grch38) for cross-build lookups"
  - "QTL fixture format matches real source schemas for downstream integration tests"

requirements-completed: [REQ-3, REQ-7]

# Metrics
duration: 8min
completed: 2026-04-13
---

# Phase 02 Plan 01: Infrastructure Summary

**GRCh37-to-GRCh38 liftover of 12 curated regions, 4 QTL/coloc config files, conda env spec, variant ID mapper, and 4 synthetic QTL fixture files with LPA/KIV-2 complex region policy update**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-13T00:12:22Z
- **Completed:** 2026-04-13T00:20:31Z
- **Tasks:** 2
- **Files modified:** 17

## Accomplishments
- All 12 curated GWAS regions lifted from GRCh37 to GRCh38 with 100% OK status, resolving DEF-01-04
- PP.H4 threshold sweep config (REQ-3) and negative control gene sets (REQ-7) defined in YAML
- QTL source metadata for all 4 sources (GTEx eQTL, GTEx sQTL, UKB-PPP pQTL, OneK1K sc-eQTL) with column mappings
- LPA/KIV-2 added as 5th complex region in susie_policy.yaml (PP.H4=0.990 BMI-T2D anchor from Phase 1)
- 25 tests written and passing for config validation and liftover output

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests** - `fda988f` (test)
2. **Task 1 GREEN: Config files + liftover + conda env** - `842b76b` (feat)
3. **Task 2: susie_policy.yaml + QTL fixtures** - `41c5944` (feat)

## Files Created/Modified
- `config/regions_curated_grch38.csv` - 12 regions with GRCh37 + GRCh38 coordinates and lift_status
- `config/pph4_thresholds.yaml` - PP.H4 sweep [0.5, 0.7, 0.8, 0.9], primary 0.8, tier A/B/C definitions
- `config/negative_controls.yaml` - HLA-immune, cosmetic, blood_group sets + 500-draw matched null spec
- `config/qtl_sources.yaml` - GTEx eQTL/sQTL, UKB-PPP pQTL, OneK1K sc-eQTL with column schemas
- `config/susie_policy.yaml` - Added LPA_KIV2_6q25 to pre_specified complex regions (5 total)
- `envs/qtl_processing.yml` - Python 3.11 + pyliftover + synapseclient + crossmap + pyarrow + pybedtools + pysam
- `src/python/liftover_regions.py` - CLI for GRCh37->GRCh38 region liftover via pyliftover
- `src/python/variant_id_map.py` - rsID to eQTL Catalogue variant_id format converter
- `tests/phase2/conftest.py` - Shared fixtures: config loaders, fixture paths
- `tests/phase2/test_liftover.py` - 8 tests for GRCh38 CSV validity
- `tests/phase2/test_config_validation.py` - 17 tests for YAML schema correctness
- `tests/phase2/generate_qtl_fixtures.py` - Reproducible fixture generator (seed=42)
- `tests/toy_3locus/data/qtl/eqtl_mock.tsv.gz` - 150 rows, eQTL Catalogue format
- `tests/toy_3locus/data/qtl/sqtl_mock.tsv.gz` - 150 rows, splice junction sQTL format
- `tests/toy_3locus/data/qtl/pqtl_mock.tsv.gz` - 150 rows, REGENIE pQTL format
- `tests/toy_3locus/data/qtl/sceqtl_mock.tsv.gz` - 150 rows, sc-eQTL + Mono_C cell_type

## Decisions Made
- Installed pyliftover into existing smoke_dev conda env to perform actual coordinate liftover rather than hardcoding coordinates -- ensures accuracy and reproducibility
- UCSC hg19ToHg38.over.chain.gz downloaded to data/external/liftover/ (gitignored per project conventions); validated at 227,698 bytes (T-02-01 tamper check: >100KB)
- QTL fixture files use seed=42, 50 variants per region per gene, one signal variant per region with |beta| > 0.3 for coloc detection tests

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- GRCh38 coordinates available for all 12 regions -- Plan 02-02 (GTEx eQTL/sQTL download) can proceed
- QTL source metadata defined -- Plan 02-03 (pQTL download) can proceed
- Negative control config ready -- Plan 02-05 (validation) can proceed
- DEF-01-04 (GRCh38 liftover gate) is resolved -- build_hgdp_1kg_ld can now execute end-to-end
- Test fixtures available for integration tests in Plans 02-02 through 02-05

## Self-Check: PASSED

All 17 files verified present. All 3 task commits (fda988f, 842b76b, 41c5944) verified in git log.

---
*Phase: 02-3-way-qtl-colocalization*
*Completed: 2026-04-13*
