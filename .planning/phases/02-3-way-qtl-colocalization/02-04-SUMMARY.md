---
phase: 02-3-way-qtl-colocalization
plan: 04
subsystem: qtl-coloc-backbone
tags: [onek1k, sceqtl, single-cell, harmonization, eqtl-catalogue, yazar2022]

# Dependency graph
requires:
  - plan: 02-02
    provides: "harmonize_eqtl.py core logic, _read_eqtl_file, write_harmonized, OUTPUT_COLUMNS"
  - plan: 02-03
    provides: "sQTL/pQTL harmonization pattern, qtl_download.smk with 7 rules"
provides:
  - "harmonize_onek1k.py: OneK1K sc-eQTL -> common intermediate TSV for 14 cell types"
  - "download_onek1k.py: dual-source download (eQTL Catalogue QTS000038 primary, onek1k.org S3 fallback)"
  - "qtl_download.smk: 9 rules total (2 new OneK1K rules added)"
affects:
  - "Plan 02-05 (tiering/aggregation) consumes OneK1K coloc results via qtl_coloc_summary.tsv"

# Tech stack
tech-stack:
  added: []
  patterns: [eqtl-catalogue-reuse, dual-source-download-fallback, cell-type-as-tissue]

# Key files
key-files:
  created:
    - src/python/harmonize_onek1k.py
    - src/python/download_onek1k.py
    - tests/phase2/test_onek1k_harmonize.py
  modified:
    - src/snakemake/rules/qtl_download.smk

key-decisions:
  - "OneK1K eQTL Catalogue format reuses harmonize_eqtl() directly (identical column schema); cell_type maps to tissue column"
  - "Dual-source download: eQTL Catalogue (QTS000038) primary with automatic fallback to onek1k.org S3 (GRCh37 + liftover)"
  - "sdY=1.0 universally (eQTL Catalogue inverse-normal); N=an/2 with 982 fallback from config"

patterns-established:
  - "cell-type-as-tissue: sc-eQTL cell types (e.g., Mono_C) stored in the tissue column of common intermediate TSV"
  - "dual-source-download: primary source with automatic fallback, source provenance logged"

requirements-completed: [REQ-3]

# Metrics
duration: 6min
completed: 2026-04-13
tasks: 1
files: 4
---

# Phase 02 Plan 04: OneK1K Single-Cell eQTL Harmonization Summary

**OneK1K sc-eQTL harmonization via eQTL Catalogue reuse for 14 immune cell types with dual-source download fallback**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-13T00:48:28Z
- **Completed:** 2026-04-13T00:54:06Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 4

## Accomplishments
- OneK1K sc-eQTL is the fourth and final QTL source in the Phase 2 pipeline
- Harmonization reuses harmonize_eqtl() core logic since eQTL Catalogue OneK1K has identical column schema
- 14 immune cell types (CD4_NC, CD4_ET, CD4_SOX4, CD8_NC, CD8_ET, CD8_S100B, NK, NK_R, B_IN, B_Mem, Plasma, Mono_C, Mono_NC, DC) supported per D-01e
- Dual-source download: eQTL Catalogue QTS000038 (primary, GRCh38) with onek1k.org S3 fallback (GRCh37 + liftover)
- All 90 Phase 2 tests pass (17 new + 73 existing)

## Task Commits

Each task was committed atomically (TDD):

1. **Task 1 RED: Failing tests** - `664a662` (test)
2. **Task 1 GREEN: Implementation** - `05d5890` (feat)

**Plan metadata:** (pending docs commit)

## Files Created/Modified
- `src/python/harmonize_onek1k.py` - OneK1K sc-eQTL harmonization to common intermediate TSV; reuses harmonize_eqtl for eQTL Catalogue format, custom parser for onek1k.org format with liftover
- `src/python/download_onek1k.py` - Dual-source download with eQTL Catalogue (QTS000038) primary and onek1k.org S3 fallback; validates file integrity
- `src/snakemake/rules/qtl_download.smk` - Extended with download_onek1k_cell_type and harmonize_onek1k_region rules (9 total rules)
- `tests/phase2/test_onek1k_harmonize.py` - 17 tests: output columns, sdY=1.0, N=982, cell_type in tissue, region filter, config validation (14 cell types), download fallback, Snakemake rules

## Decisions Made
- OneK1K eQTL Catalogue format reuses harmonize_eqtl() directly -- identical column schema to GTEx eQTL (same approach as sQTL reuse in 02-03)
- Cell type name (e.g., "Mono_C") stored in the "tissue" column of the common intermediate TSV, consistent with GTEx tissue naming
- Dual-source download with automatic fallback: eQTL Catalogue preferred for known provenance (T-02-12), onek1k.org S3 as backup requiring GRCh37->GRCh38 liftover
- N = an/2 (from file) with 982 fallback (from config); sdY = 1.0 universally for eQTL Catalogue data

## Deviations from Plan

None -- plan executed exactly as written.

## Threat Mitigations Implemented

| Threat | Mitigation | File |
|--------|-----------|------|
| T-02-12 | Prefer eQTL Catalogue (known provenance); log source format used | harmonize_onek1k.py, download_onek1k.py |
| T-02-13 | Validate file exists + size > 0 before processing; tabix validation | harmonize_onek1k.py, download_onek1k.py, qtl_download.smk |
| T-02-14 | Accepted: onek1k.org S3 latency is fallback only; download-once-cache pattern | download_onek1k.py |

## Test Coverage

| Test File | Tests | Description |
|-----------|-------|-------------|
| test_onek1k_harmonize.py | 17 | Output columns, sdY, N, tissue=cell_type, region filter, 14 cell types config, download fallback, eqtl reuse, Snakemake rules |
| **Phase 2 total** | **90** | All passing (73 prior + 17 new) |

## Issues Encountered
None

## User Setup Required
None -- no external service configuration required.

## Next Phase Readiness
- All four QTL sources now have harmonization pipelines (eQTL, sQTL, pQTL, sc-eQTL)
- Plan 02-05 (tiering and aggregation) can consume coloc results from all sources via qtl_coloc_summary.tsv
- OneK1K broad trigger: manifest will include sc-eQTL rows for ALL loci (not conditional on bulk eQTL results) per D-01e

---
*Phase: 02-3-way-qtl-colocalization*
*Completed: 2026-04-13*
