---
phase: 02-3-way-qtl-colocalization
plan: 05
subsystem: analysis
tags: [negative-controls, tiers, l2g, sweep, gene-tissue-matrix, coloc, methods]

# Dependency graph
requires:
  - phase: 02-02
    provides: "eQTL harmonization pipeline and qtl_coloc.smk manifest-driven dispatch"
  - phase: 02-03
    provides: "sQTL + pQTL harmonization pipelines (harmonize_sqtl.py, harmonize_pqtl.py, estimate_sdy.py)"
  - phase: 02-04
    provides: "OneK1K sc-eQTL harmonization pipeline (harmonize_onek1k.py, download_onek1k.py)"
provides:
  - "Tier A/B/C confidence assignment logic (assign_tiers.py)"
  - "PP.H4 threshold sweep at {0.5, 0.7, 0.8, 0.9} (REQ-3)"
  - "3 curated negative control gene sets + 500 distance-matched null loci (REQ-7)"
  - "Open Targets L2G concordance computation (parse_l2g.py)"
  - "Gene x tissue x cell-type matrix (build_gene_tissue_matrix.py)"
  - "negative_controls.smk Snakemake rules"
  - "Phase 2 methods fragment for manuscript integration"
affects: [05-pathway-heritability, 09-replication, 11-manuscript]

# Tech tracking
tech-stack:
  added: [bedtools, pyarrow, pybedtools]
  patterns: [tier-assignment-from-config, threshold-sweep-sensitivity, negative-control-validation]

key-files:
  created:
    - src/python/sample_null_loci.py
    - src/python/assign_tiers.py
    - src/python/parse_l2g.py
    - src/python/build_gene_tissue_matrix.py
    - src/snakemake/rules/negative_controls.smk
    - .planning/phases/02-3-way-qtl-colocalization/methods_fragment.md
    - tests/phase2/test_negative_controls.py
    - tests/phase2/test_pph4_sweep.py
    - tests/phase2/test_tier_assignment.py
  modified:
    - src/snakemake/rules/qtl_coloc.smk
    - Snakefile

key-decisions:
  - "assign_tier() is a pure function of (gwas_pph4, qtl_pph4, threshold) with no source argument, enforcing QTL-source-agnostic design (D-02c)"
  - "sweep_tiers() treats PP.H4.abf as both GWAS and QTL metric in simplified sweep mode; full mode uses separate GWAS coloc table"
  - "L2G concordance uses fuzzy region-to-studyLocusId matching (substring) since no direct mapping exists"
  - "Gene-tissue matrix column labels combine tissue.qtl_source for unambiguous identification across 4 QTL sources"
  - "Negative control coloc reuses run_qtl_coloc.R via manifest-based dispatch (no separate pipeline)"

patterns-established:
  - "Tier assignment from YAML config: all thresholds loaded from pph4_thresholds.yaml, never hardcoded"
  - "Negative control manifest: same format as qtl_coloc_manifest.tsv, reusing existing dispatch rules"
  - "L2G as corroboration not gate: disagreements annotated as findings, not failures"

requirements-completed: [REQ-3, REQ-7]

# Metrics
duration: 10min
completed: 2026-04-13
---

# Phase 02 Plan 05: Negative Controls + Tier Assembly + L2G Concordance Summary

**Tier A/B/C confidence assignment from pph4_thresholds.yaml with PP.H4 sweep at 4 thresholds, 3 curated negative control sets + 500 null loci, L2G concordance, and gene-tissue matrix from all 4 QTL sources**

## Performance

- **Duration:** 10 min
- **Started:** 2026-04-13T00:58:10Z
- **Completed:** 2026-04-13T01:08:28Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments
- Tier A/B/C assignment logic that is mechanistic and QTL-source-agnostic (D-02c), with negative control rows appended when provided
- PP.H4 threshold sweep at {0.5, 0.7, 0.8, 0.9} producing per-ancestry tier count table (REQ-3 fully delivered)
- Three curated negative control gene sets (HLA, cosmetic, blood group) + 500 distance-matched null loci via bedtools shuffle (REQ-7 fully delivered)
- Open Targets L2G concordance computation: independent corroboration with disagreements as findings (D-05a/D-05b)
- Gene x tissue x cell-type matrix in wide + long format from all QTL coloc results
- Methods fragment documenting all Phase 2 analytical components for Phase 11 manuscript integration
- 136 Phase 2 tests pass (1 skipped: bedtools not in test env)

## Task Commits

Each task was committed atomically:

1. **Task 1: Negative controls + PP.H4 sweep** - `2942e98` (test) + `4857d37` (feat)
2. **Task 2: Tier A/B/C + gene-tissue matrix + L2G** - `554b5f9` (test) + `fef410c` (feat)
3. **Task 3: Methods fragment** - `b7eb12e` (docs)

## Files Created/Modified
- `src/python/sample_null_loci.py` - Null loci sampler (bedtools shuffle), neg-ctrl manifest builder, coloc runner
- `src/python/assign_tiers.py` - Tier A/B/C assignment + sweep_tiers() + assign_tiers_full() with neg-ctrl support
- `src/python/parse_l2g.py` - Open Targets L2G Parquet reader + concordance computation
- `src/python/build_gene_tissue_matrix.py` - Wide + long format gene x tissue matrix builder
- `src/snakemake/rules/negative_controls.smk` - 4 rules: generate_null_loci, build_neg_ctrl_manifest, run_curated_negative_controls, pph4_threshold_sweep
- `src/snakemake/rules/qtl_coloc.smk` - Extended with 3 rules: assign_tiers, l2g_concordance, build_gene_tissue_matrix
- `Snakefile` - Added include for negative_controls.smk
- `.planning/phases/02-3-way-qtl-colocalization/methods_fragment.md` - Phase 2 methods narrative
- `tests/phase2/test_negative_controls.py` - 19 tests for config, script interface, null loci overlap
- `tests/phase2/test_pph4_sweep.py` - 7 tests for sweep config and logic
- `tests/phase2/test_tier_assignment.py` - 21 tests for tier logic, source-agnosticism, L2G, matrix

## Decisions Made
- assign_tier() is a pure function of (gwas_pph4, qtl_pph4, threshold) -- no source argument, enforcing QTL-source-agnostic design per D-02c
- Gene-tissue matrix column labels use "tissue.qtl_source" format for unambiguous identification across 4 QTL sources
- L2G concordance uses fuzzy substring matching on studyLocusId since Open Targets does not provide direct region-to-locus ID mapping
- Negative control coloc reuses the existing run_qtl_coloc.R pipeline via manifest-based dispatch (same format as qtl_coloc_manifest.tsv)
- NEG_CTRL_DIR re-defined in qtl_coloc.smk for self-contained reference (Snakemake tolerates re-assignment)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 2 (3-way QTL colocalization) is now complete: all 5 plans executed
- All 136 Phase 2 tests pass (1 skipped: bedtools not available in test environment)
- Ready for Phase 5 (pathway-heritability) which consumes tier assignments and gene-tissue matrix
- Ready for Phase 9 (replication) which uses negative control baselines
- Ready for Phase 11 (manuscript) which incorporates the methods fragment

## Self-Check: PASSED

All 10 created files verified present. All 5 commits verified in git log.

---
*Phase: 02-3-way-qtl-colocalization*
*Completed: 2026-04-13*
