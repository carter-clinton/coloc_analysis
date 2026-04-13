---
phase: 02-3-way-qtl-colocalization
plan: 03
subsystem: qtl-harmonization
tags: [sqtl, pqtl, ukbppp, gtex, harmonization, sdy, synapse, regenie]

# Dependency graph
requires:
  - phase: 02-3-way-qtl-colocalization
    provides: "02-02 eQTL backbone: harmonize_eqtl.py, run_qtl_coloc.R, qtl_download.smk, qtl_coloc.smk"
  - plan: 02-01
    provides: "GRCh38 regions, qtl_sources.yaml, mock QTL fixtures (sqtl_mock.tsv.gz, pqtl_mock.tsv.gz)"
provides:
  - "harmonize_sqtl.py: sQTL harmonization from eQTL Catalogue (reuses eQTL core logic)"
  - "harmonize_pqtl.py: UKB-PPP pQTL harmonization from REGENIE format"
  - "estimate_sdy.py: coloc::est_sdY formula for non-unit-variance QTL data"
  - "download_ukbppp.py: Synapse CLI wrapper + S3 fallback for UKB-PPP download"
  - "build_protein_ensembl_map.py: protein-to-Ensembl gene ID lookup builder"
  - "qtl_download.smk: 4 new rules (download_sqtl_catalogue, harmonize_sqtl_region, download_ukbppp_protein, harmonize_pqtl_region)"
affects:
  - "Plan 02-04 (sc-eQTL) extends the same backbone pattern"
  - "Plan 02-05 (tiering/aggregation) consumes sQTL+pQTL harmonized outputs"

# Tech stack
tech-stack:
  added: [synapseclient, boto3]
  patterns: [eqtl-core-reuse, regenie-harmonization, sdy-estimation, token-env-auth]

# Key files
key-files:
  created:
    - src/python/harmonize_sqtl.py
    - src/python/harmonize_pqtl.py
    - src/python/estimate_sdy.py
    - src/python/download_ukbppp.py
    - src/python/build_protein_ensembl_map.py
    - tests/phase2/test_harmonize_sqtl.py
    - tests/phase2/test_harmonize_pqtl.py
  modified:
    - src/snakemake/rules/qtl_download.smk
    - .gitignore

key-decisions:
  - "LOG10P clipped to [0, 300] to handle edge-case negative values; real REGENIE LOG10P is non-negative but clipping prevents invalid pvalues > 1.0"
  - "sQTL reuses harmonize_eqtl core logic (_read_eqtl_file, write_harmonized) since both come from eQTL Catalogue with identical column schema"
  - "pQTL gene_id resolved via protein-to-Ensembl lookup table (not inline HGNC API calls) for reproducibility and offline operation"
  - "sdY test range widened to [0.5, 3.0] after verifying formula: sqrt(2*0.3*0.7*(1000*0.01)) = sqrt(4.2) ~ 2.05 is mathematically correct"

patterns-established:
  - "REGENIE harmonization pattern: space-delimited input, LOG10P conversion, ALLELE0/1 variant_id construction"
  - "Token-from-env pattern: Synapse auth via SYNAPSE_AUTH_TOKEN env var, .synapseConfig in .gitignore"
  - "sdY estimation pattern: coloc::est_sdY formula in Python for non-unit-variance QTL sources"

requirements-completed: [REQ-3]

# Metrics
duration: 9min
completed: 2026-04-13
tasks: 2
files: 9
---

# Phase 02 Plan 03: GTEx v8 sQTL + UKB-PPP pQTL Harmonization Summary

**sQTL harmonization (eQTL core reuse) + pQTL REGENIE harmonization with LOG10P conversion, sdY estimation, and Synapse download utility**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-13T00:34:46Z
- **Completed:** 2026-04-13T00:43:46Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- sQTL harmonization reuses eQTL Catalogue core logic from Plan 02-02, adding splice junction ID handling while preserving Ensembl gene_id for cross-source joins
- pQTL harmonization converts UKB-PPP REGENIE output (LOG10P, ALLELE0/1, A1FREQ, INFO) to the common intermediate TSV format with sdY estimation via coloc::est_sdY formula
- UKB-PPP download utility with Synapse auth from env var + S3 unsigned fallback, per-protein per-chromosome granularity (T-02-10)
- 7 total download/harmonize Snakemake rules (3 eQTL from Plan 02-02 + 4 new sQTL/pQTL), all producing harmonized TSVs consumable by run_qtl_coloc.R
- 73 phase2 tests passing (58 prior + 15 new)

## Task Commits

Each task was committed atomically:

1. **Task 1: sQTL harmonization + pQTL harmonization + sdY estimator** (TDD)
   - `7b47409` (test: TDD RED - 15 failing tests)
   - `0afca37` (feat: TDD GREEN - all 15 passing)
2. **Task 2: UKB-PPP download utility + sQTL/pQTL Snakemake rules** - `acb068d` (feat)

## Files Created/Modified

- `src/python/harmonize_sqtl.py` - sQTL harmonization wrapping eQTL core logic; filters by gene_id, preserves junction IDs
- `src/python/harmonize_pqtl.py` - UKB-PPP REGENIE harmonization with LOG10P conversion, variant_id construction, INFO/MAF filtering
- `src/python/estimate_sdy.py` - sdY estimator implementing coloc::est_sdY formula from summary statistics
- `src/python/download_ukbppp.py` - Synapse download with S3 fallback, auth from env var only
- `src/python/build_protein_ensembl_map.py` - Protein-to-Ensembl lookup builder from UKB-PPP metadata or HGNC API
- `src/snakemake/rules/qtl_download.smk` - Extended with 4 new rules for sQTL download/harmonize and pQTL download/harmonize
- `tests/phase2/test_harmonize_sqtl.py` - 7 tests: columns, sdY, junction IDs, region filter
- `tests/phase2/test_harmonize_pqtl.py` - 8 tests: columns, LOG10P, variant_id format, MAF range, sdY estimation, Ensembl gene_id
- `.gitignore` - Added .synapseConfig to prevent auth token commits

## Decisions Made

- **LOG10P clipping:** Clipped LOG10P to [0, 300] range. Mock data had negative LOG10P values (which would produce pvalue > 1.0). Real REGENIE output has LOG10P >= 0, but the clipping prevents invalid pvalues defensively.
- **sQTL core reuse:** harmonize_sqtl.py imports `_read_eqtl_file` and `write_harmonized` from harmonize_eqtl.py rather than duplicating the file reading/writing logic. The sQTL-specific logic (gene_id vs molecular_trait_id column selection) is implemented directly.
- **pQTL gene_id lookup:** Uses a file-based protein-to-Ensembl map (data/external/ukbppp_protein_to_ensembl.tsv) rather than inline HGNC API calls. This ensures reproducibility and works offline. The map is built by build_protein_ensembl_map.py.
- **sdY test bounds:** Widened from [0.5, 2.0] to [0.5, 3.0] after confirming the formula produces sdY ~ 2.05 for the test inputs, which is mathematically correct.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] LOG10P negative value handling**
- **Found during:** Task 1 (pQTL harmonization tests)
- **Issue:** Mock pQTL data contained negative LOG10P values (e.g., -0.3568), causing 10^(-(-0.3568)) > 1.0, which is an invalid pvalue
- **Fix:** Added `clip(lower=0, upper=300)` to LOG10P before conversion, capping pvalues at [0, 1.0]
- **Files modified:** src/python/harmonize_pqtl.py
- **Verification:** test_log10p_conversion passes, all pvalues in [0, 1.0]
- **Committed in:** 0afca37 (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Single defensive clipping fix for edge-case data. No scope creep.

## Issues Encountered

None -- all planned work executed cleanly after the LOG10P fix.

## Threat Mitigations Implemented

| Threat | Mitigation | File |
|--------|-----------|------|
| T-02-08 | Synapse auth from SYNAPSE_AUTH_TOKEN env var only; .synapseConfig in .gitignore | download_ukbppp.py, .gitignore |
| T-02-09 | Validates REQUIRED_REGENIE_COLUMNS present before processing; raises ValueError on mismatch | harmonize_pqtl.py |
| T-02-10 | Per-protein per-chromosome download (not bulk tar); pre-download disk space check | download_ukbppp.py |
| T-02-11 | Accepted: splice junction IDs are pass-through; no security impact | harmonize_sqtl.py |

## User Setup Required

None -- no external service configuration required for development. Synapse auth token needed only for production UKB-PPP downloads (set SYNAPSE_AUTH_TOKEN env var).

## Next Phase Readiness

- sQTL and pQTL harmonized outputs flow through the existing run_qtl_coloc.R (source-agnostic runner from Plan 02-02)
- Plan 02-04 (OneK1K sc-eQTL) will follow the same eQTL Catalogue harmonization pattern
- Plan 02-05 (tiering/aggregation) can now consume eQTL + sQTL + pQTL coloc results
- 3 of 4 QTL source types now fully implemented (eQTL, sQTL, pQTL); sc-eQTL remaining

## Self-Check: PASSED

All 9 created/modified files verified on disk. All 3 commits (7b47409, 0afca37, acb068d) found in git log.

---
*Phase: 02-3-way-qtl-colocalization*
*Completed: 2026-04-13*
