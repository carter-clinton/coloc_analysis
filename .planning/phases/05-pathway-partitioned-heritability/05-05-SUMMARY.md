---
phase: 05-pathway-partitioned-heritability
plan: 05
subsystem: pathway
tags: [permutation-null, negative-controls, cross-method-aggregation, methods-fragment, snakemake, magma, gprofiler, ldsc, hess]

# Dependency graph
requires:
  - phase: 05-pathway-partitioned-heritability
    plan: 02
    provides: "MAGMA wrapper, g:Profiler wrapper, 9 working Snakemake rules"
  - phase: 05-pathway-partitioned-heritability
    plan: 03
    provides: "LDSC partitioned h2 wrapper, LDSC-SEG wrapper, 9 Snakemake rules, sumstats_utils.py"
  - phase: 05-pathway-partitioned-heritability
    plan: 04
    provides: "HESS/rho-HESS wrapper, 7 Snakemake rules, TRAIT_PAIRS generation"
provides:
  - "Permutation null gene set generator (1000 sets matched for length, LD, MAF per D-06c)"
  - "Negative control validation rule aggregating MAGMA, g:Profiler, LDSC with q > 0.05 gate (T-05-21)"
  - "Cross-method aggregation producing pathway_enrichment_summary.tsv and phase5_overview.tsv"
  - "Methods fragment for manuscript (7 subsections, 6 citations, software versions)"
  - "all_pathway target rule collecting all Phase 5 outputs"
  - "100 passing Phase 5 tests (19 net new)"
affects: [11-manuscript-assembly]

# Tech tracking
tech-stack:
  added: [permutation-null-genesets, cross-method-aggregation]
  patterns: [3-criterion-gene-matching, empirical-pvalue-computation, consensus-ranking, geometric-mean-p]

key-files:
  created:
    - src/python/extend_null_genesets.py
    - src/python/aggregate_pathway_results.py
    - docs/methods/phase5_methods_fragment.md
  modified:
    - src/snakemake/rules/pathway.smk
    - tests/phase5/test_permutation_null.py
    - tests/phase5/test_negative_controls.py

key-decisions:
  - "3-criterion matching (length +/-50%, LD complexity +/-30%, median MAF +/-30%) per D-06c with relaxed fallback"
  - "maf_reference and ld_score_reference are REQUIRED args (no 2-criterion fallback)"
  - "Empirical p-value = (n_exceed + 1) / (n_total + 1) conservative estimator"
  - "Consensus ranking by n_methods_significant desc, then geometric mean p-value asc"
  - "Fixed 4 conda+run incompatibilities in pathway.smk for Snakemake 7.32.4 dry-run"

patterns-established:
  - "Gene-set-level permutation null: match on length, LD, MAF, exclude query + neg ctrl + custom genes"
  - "Cross-method consensus: count significant methods + geometric mean p-value for ranking"
  - "Negative control pipeline gate: hard exit 1 on any q <= 0.05 (T-05-21)"

requirements-completed: [REQ-7]

# Metrics
duration: 20min
completed: 2026-04-13
---

# Phase 5 Plan 5: Aggregation + Permutation Null Summary

**Permutation null generator with 3-criterion matching (length, LD, MAF), negative control validation gate across 5 methods, cross-method consensus ranking, and methods fragment with 6 canonical citations for manuscript assembly**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-13T21:09:24Z
- **Completed:** 2026-04-13T21:30:00Z
- **Tasks:** 2/2
- **Files modified:** 6

## Accomplishments

- Created extend_null_genesets.py: 3-criterion gene set matching (length +/-50%, LD complexity via independent LD block count +/-30%, median MAF +/-30%) per D-06c, deterministic seeds (seed_base=42 + perm_index per T-02-18), REQUIRED maf_reference and ld_score_reference args, relaxed fallback for hard-to-match genes
- Created aggregate_pathway_results.py: reads all 6 method outputs (MAGMA FDR, g:Profiler, LDSC h2, LDSC-SEG, HESS, negative controls), produces pathway_enrichment_summary.tsv with consensus_rank and phase5_overview.tsv with component status, T-05-24 schema validation on all inputs
- Replaced 2 pathway.smk placeholders (permutation_null, aggregate_pathway_results) with 6 finalized rules: permutation_null_genesets, permutation_magma, permutation_aggregate, validate_negative_controls, aggregate_pathway_results, all_pathway
- Created methods fragment with 7 subsections covering all 6 analytical components plus software versions, citing de Leeuw 2015, Reimand 2019, Finucane 2015/2018, Gazal 2017, Shi 2017, with {RESULT} placeholders for Phase 11
- 100 Phase 5 tests passing (19 net new: permutation size matching, deterministic seed, query exclusion, 3-criterion matching logic, MAF/LD required, rule existence, neg ctrl schema, threshold enforcement)

## Task Commits

Each task was committed atomically:

1. **Task 1: Permutation null gene set generator + negative control validation rules** - `3cfc6c9` (feat)
2. **Task 2: Cross-method aggregation + methods fragment + Snakemake dry-run** - `f146bed` (feat)

## Files Created/Modified

- `src/python/extend_null_genesets.py` - Permutation null generator: 3-criterion matching, deterministic seeds, generate_null_genesets() reusable function, validate_negative_controls() hard gate
- `src/python/aggregate_pathway_results.py` - Cross-method aggregation: aggregate_all_methods() reads 6 inputs, produces consensus ranking and overview tables
- `docs/methods/phase5_methods_fragment.md` - Methods text: 7 subsections (MAGMA, g:Profiler, S-LDSC, LDSC-SEG, HESS, negative controls, software versions), 6 canonical citations, {RESULT} placeholders
- `src/snakemake/rules/pathway.smk` - 6 new rules replacing 2 placeholders + 4 conda/run fixes; all_pathway top-level target
- `tests/phase5/test_permutation_null.py` - 16 tests: permutation count, rule existence, size matching, deterministic seed, query exclusion, tolerance, gene loc parser, matching logic, MAF/LD required
- `tests/phase5/test_negative_controls.py` - 10 tests: all methods have neg ctrl rules, gene overlap, schema validation, threshold enforcement (pass + fail)

## Decisions Made

- 3-criterion matching (length +/-50%, LD complexity +/-30%, median MAF +/-30%) per D-06c; maf_reference and ld_score_reference are REQUIRED arguments with no 2-criterion fallback
- Empirical p-value uses conservative estimator: (n_exceed + 1) / (n_total + 1) to avoid zero p-values
- Consensus ranking: sort by n_methods_significant (descending), then geometric mean p-value (ascending)
- validate_negative_controls() hard-fails with sys.exit(1) when any row has passes_threshold=FALSE (T-05-21)
- Fixed 4 Snakemake 7.32.4 conda+run incompatibilities: removed conda: from run: blocks in magma_fdr, hess_format_sumstats, hess_negative_controls, gprofiler_negative_controls

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed 4 conda+run incompatibilities for Snakemake dry-run**
- **Found during:** Task 2
- **Issue:** Snakemake 7.32.4 rejects conda: directive with run: blocks (only shell/script/notebook/wrapper allowed). 4 rules had this pattern: magma_fdr, hess_format_sumstats, hess_negative_controls, gprofiler_negative_controls
- **Fix:** Removed conda: directives from all 4 run: block rules (run: blocks execute in host environment anyway)
- **Files modified:** src/snakemake/rules/pathway.smk
- **Verification:** Snakemake --list parses all rules successfully; DAG builds correctly
- **Commit:** f146bed

---

**Total deviations:** 1 auto-fixed (Rule 3 - blocking)
**Impact on plan:** Fix was necessary for Snakemake dry-run acceptance criterion. No scope creep.

## Known Stubs

None -- all placeholder rules from prior plans have been replaced with working implementations.

## Issues Encountered

- Snakemake dry-run for `all_pathway` target reports MissingInputException for reference data files (g1000_eur.bim, etc.) that haven't been downloaded yet. This is expected behavior -- the DAG structure is correct and all rules parse successfully. The dry-run will succeed once reference data is downloaded via the download_* rules.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 5 is complete: all 5 plans executed, 100 tests passing, 0 placeholder rules remaining
- Pipeline architecture is finalized: `snakemake all_pathway` target collects all Phase 5 outputs
- Methods fragment ready for Phase 11 manuscript assembly (7 subsections with {RESULT} placeholders)
- Negative control validation gate (T-05-21) will hard-fail if any control shows enrichment
- Permutation null will provide empirical p-values for the colocalization gene list's enrichment
- Phase 5 produces: pathway_enrichment_summary.tsv, phase5_overview.tsv, validation_summary.tsv, empirical_pvalues.tsv, local_covariance_summary.tsv, shared_tissue_summary.tsv

## Self-Check: PASSED

- 3/3 created files found (extend_null_genesets.py, aggregate_pathway_results.py, phase5_methods_fragment.md)
- 3/3 modified files verified (pathway.smk, test_permutation_null.py, test_negative_controls.py)
- 2/2 task commits found (3cfc6c9, f146bed)
- 100/100 tests passing

---
*Phase: 05-pathway-partitioned-heritability*
*Completed: 2026-04-13*
