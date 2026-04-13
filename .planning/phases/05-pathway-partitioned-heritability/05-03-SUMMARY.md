---
phase: 05-pathway-partitioned-heritability
plan: 03
subsystem: pathway
tags: [ldsc, partitioned-heritability, ldsc-seg, tissue-enrichment, snakemake, subprocess]

# Dependency graph
requires:
  - phase: 05-pathway-partitioned-heritability
    plan: 01
    provides: "Conda envs, GMT pathway gene sets, utility scripts, pathway.smk skeleton, sumstats_utils.py"
  - phase: 05-pathway-partitioned-heritability
    plan: 02
    provides: "MAGMA wrapper, g:Profiler wrapper, 9 working Snakemake rules"
provides:
  - "LDSC partitioned h2 wrapper (munge/compute-ld-scores/h2) with baseline v2.2 + custom annotations"
  - "LDSC-SEG tissue enrichment wrapper (GTEx 53-tissue + Roadmap chromatin)"
  - "Shared tissue identification across trait pairs (D-05b)"
  - ".ldcts path fixing for downloaded annotation files (T-05-13)"
  - "9 new Snakemake rules replacing 3 placeholders (ldsc_munge, build_annotations, compute_ld_scores, partitioned_h2, aggregate_h2, seg_gene_expr, seg_chromatin, seg_shared_tissues, fix_ldcts_paths)"
  - "72 passing Phase 5 tests (19 new: 6 LDSC partitioned + 13 LDSC-SEG)"
affects: [05-05-aggregation-permutation]

# Tech tracking
tech-stack:
  added: [ldsc-partitioned-h2, ldsc-seg, ldcts-path-fix]
  patterns: [subprocess-list-args, post-munge-snp-validation, overlap-annot-enforcement, baseline-first-ref-ld, bonferroni-shared-tissues]

key-files:
  created:
    - src/python/run_ldsc_partitioned.py
    - src/python/run_ldsc_seg.py
  modified:
    - src/snakemake/rules/pathway.smk
    - tests/phase5/test_ldsc_partitioned.py
    - tests/phase5/test_ldsc_seg.py

key-decisions:
  - "Always include --overlap-annot in LDSC h2 step (anti-pattern prevention per LDSC wiki)"
  - "Baseline v2.2 always first in --ref-ld-chr comma-separated list (D-04a)"
  - "Post-munge SNP count validation warns at < 500K threshold (Pitfall 2 / T-05-16)"
  - "Bonferroni correction across tissues for shared tissue identification (D-05b)"
  - ".ldcts path rewriting extracts basenames and prepends local annot_dir (T-05-13)"
  - "AST-based shell=True detection in tests (avoids false positives from docstrings)"

patterns-established:
  - "LDSC h2 pattern: --overlap-annot always present, baseline first in --ref-ld-chr"
  - "LDSC-SEG pattern: --h2-cts (not --h2), .ldcts validation before invocation"
  - "Post-processing pattern: parse .results and .cell_type_results.txt via csv.DictReader"
  - "Shared tissue pattern: Bonferroni-corrected P-value comparison across trait pairs"

requirements-completed: [REQ-7]

# Metrics
duration: 7min
completed: 2026-04-13
---

# Phase 5 Plan 3: LDSC Partitioned Heritability + LDSC-SEG Summary

**LDSC partitioned h2 with baseline v2.2 + custom pathway annotations and LDSC-SEG tissue-specific enrichment with GTEx 53-tissue + Roadmap chromatin, shared tissue analysis, and .ldcts path fixing**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-13T20:49:03Z
- **Completed:** 2026-04-13T20:56:38Z
- **Tasks:** 2/2
- **Files modified:** 5

## Accomplishments

- Created run_ldsc_partitioned.py: 3-step LDSC wrapper (munge, compute-ld-scores, h2) with subprocess list args (T-05-14), --overlap-annot enforcement (anti-pattern), baseline-first --ref-ld-chr (D-04a), post-munge SNP count validation (T-05-16), .results parsing
- Created run_ldsc_seg.py: LDSC-SEG tissue enrichment wrapper using --h2-cts (NOT --h2), .ldcts file validation and path fixing (T-05-13 / Pitfall 8), .cell_type_results.txt parsing, identify_shared_tissues() for cross-trait tissue overlap (D-05b)
- Replaced 3 placeholder Snakemake rules with 9 working rules: 5 LDSC partitioned (munge, build_custom_annotations, compute_custom_ld_scores, partitioned_h2, aggregate_h2) + 4 LDSC-SEG (seg_gene_expr, seg_chromatin, seg_shared_tissues, fix_ldcts_paths)
- 72 Phase 5 tests passing (19 new tests validating command construction, overlap-annot, baseline ordering, results parsing, .ldcts validation, path fixing, shared tissues, h2-cts flag, no shell=True)

## Task Commits

Each task was committed atomically:

1. **Task 1: LDSC partitioned h2 wrapper + annotation building + Snakemake rules** - `e66fc67` (feat)
2. **Task 2: LDSC-SEG tissue-specific enrichment wrapper + Snakemake rules** - `f0ff317` (feat)

## Files Created/Modified

- `src/python/run_ldsc_partitioned.py` - LDSC 3-step wrapper: munge, compute-ld-scores, h2 with anti-pattern guards
- `src/python/run_ldsc_seg.py` - LDSC-SEG tissue enrichment wrapper with .ldcts path fixing and shared tissue analysis
- `src/snakemake/rules/pathway.smk` - 9 new working rules replacing 3 placeholders + 4 LDSC-SEG rules added
- `tests/phase5/test_ldsc_partitioned.py` - 17 tests: munging, effective-N, annotations, overlap-annot, baseline-first, results parsing
- `tests/phase5/test_ldsc_seg.py` - 16 tests: .ldcts format, path fixing, results parsing, shared tissues, h2-cts flag

## Decisions Made

- --overlap-annot always included in LDSC partitioned h2 command (prevents the known anti-pattern of omitting it, which invalidates enrichment estimates for overlapping annotations)
- Baseline v2.2 LD scores always first in --ref-ld-chr comma-separated argument (D-04a compliance)
- Post-munge SNP count threshold set at 500,000 (LDSC expects ~1.2M HapMap3 SNPs; < 500K indicates column mismatch or excessive filtering)
- Bonferroni correction applied across tissues for shared tissue identification (conservative per D-05b)
- .ldcts path fixing extracts basenames from absolute paths and prepends local annotation directory (handles Broad download path conventions)
- AST-based shell=True detection in tests avoids false positives from docstring mentions

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| 2 placeholder `pass` rules | src/snakemake/rules/pathway.smk | Intentional: HESS and permutation rules for Plans 05-04 and 05-05 |

These stubs are intentional infrastructure for future plans and do not block Plan 03's goal.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- LDSC partitioned h2 and LDSC-SEG pipelines fully implemented
- 2 remaining placeholder rules (HESS, permutation) ready for Plans 05-04 and 05-05
- Plan 05-04 (HESS local heritability) can proceed immediately
- All 72 Phase 5 tests provide regression safety

## Self-Check: PASSED

- 2/2 created files found (run_ldsc_partitioned.py, run_ldsc_seg.py)
- 3/3 modified files verified (pathway.smk, test_ldsc_partitioned.py, test_ldsc_seg.py)
- 2/2 task commits found (e66fc67, f0ff317)
- 72/72 tests passing

---
*Phase: 05-pathway-partitioned-heritability*
*Completed: 2026-04-13*
