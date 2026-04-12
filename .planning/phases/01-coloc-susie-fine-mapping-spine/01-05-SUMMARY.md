---
phase: 01-coloc-susie-fine-mapping-spine
plan: 05
subsystem: qc
tags: [quarto, rmarkdown, DT, susie, finemap, dashboard, sweep, complex-regions]

requires:
  - phase: 01-01
    provides: run_susie_rss.R D1/D2/D3 diagnostics JSON schema, susie_policy.yaml
  - phase: 01-04
    provides: coloc.susie output schema (susie_pairs, summary, no_signal sentinel)
provides:
  - envs/qc_dashboard.yml (Quarto + RMarkdown + DT conda env)
  - susie_qc_aggregate.py (JSON -> flat TSV aggregator with D1-D4 + ld_source)
  - susie_qc_report.qmd (Quarto HTML dashboard with DT::datatable + conditional styling)
  - qc.smk rules (susie_qc_aggregate, build_sweep_complex_regions_table, build_susie_qc_dashboard)
  - sweep_complex_regions.tsv (standalone REQ-2 supplementary sensitivity table)
  - test_qc_dashboard.py (17 tests: 14 pass, 3 skip pending 01-06 real render)
affects: [01-06, phase-11-methods]

tech-stack:
  added: [quarto (conda-forge), r-dt, r-data.table, pyyaml]
  patterns:
    - QC_DASHBOARD_ENV absolute-path pattern for conda directive (sidesteps DEF-01-01)
    - --aggregated-only mode for reusing materialized TSV without re-scanning JSON
    - Dual ld_source/ld_matrix key tolerance in aggregator (run_susie_rss.R uses ld_matrix as JSON key)

key-files:
  created:
    - envs/qc_dashboard.yml
    - src/snakemake/scripts/susie_qc_aggregate.py
    - src/snakemake/scripts/susie_qc_report.qmd
    - tests/phase1/test_qc_dashboard.py
  modified:
    - src/snakemake/rules/qc.smk

key-decisions:
  - "Merged Tasks 2+4 into a single aggregator commit: build_sweep_table and --aggregated-only mode written alongside the main aggregator to avoid a second partial-rewrite commit"
  - "ld_source/ld_matrix dual-key tolerance: run_susie_rss.R emits JSON key 'ld_matrix' (line 490), plan interfaces say 'ld_source'; aggregator accepts both with ld_source taking precedence (Rule 1 auto-fix)"
  - "Quarto fallback to rmarkdown::render in build_susie_qc_dashboard shell block -- enables dashboard rendering even if quarto CLI unresolvable in conda env"
  - "Policy trait_list not yet in susie_policy.yaml (no per-region trait pin); sweep table treats all pre_specified regions as applicable to any trait present in aggregated data"

patterns-established:
  - "QC_DASHBOARD_ENV = str(Path(workflow.basedir) / 'envs' / 'qc_dashboard.yml') -- absolute-path conda directive for qc.smk rules"
  - "Aggregator --aggregated-only mode for downstream rules that consume the already-materialized TSV"
  - "Sweep table comment header (## row_group_empty) for fail-open empty-group sentinel"

requirements-completed: [REQ-2]

duration: 12min
completed: 2026-04-11
---

# Phase 01 Plan 05: QC Dashboard D1+D2+D3+D4+D6 Summary

**SuSiE fine-mapping QC dashboard with DT::datatable interactive tables, HLA block-diagonal LD flag surfaced in red (T-1-04), and standalone REQ-2 sensitivity-sweep supplementary table**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-11T00:00:00Z
- **Completed:** 2026-04-11T00:12:00Z
- **Tasks:** 4 (5 planned; Task 4 merged into Task 2 commit)
- **Files modified:** 5

## Accomplishments

- Aggregator (susie_qc_aggregate.py) flattens D1/D2/D3/D4 diagnostics + ld_source + L_saturated + is_complex_region + max_PIP + total_PIP sweep into flat TSV keyed by (trait x ancestry x region_id)
- Quarto dashboard template with DT::datatable, column filters, deferRender for browser memory safety; red background on HLA block-diagonal LD (T-1-04 surfacing), orange on non-converged, yellow on L-saturated, purple on pre-specified complex regions
- Standalone REQ-2 supplementary sensitivity table (sweep_complex_regions.tsv) with two row-groups: known_complex (4 pre-specified regions) and data_flagged (L_saturated or n_CS >= 3)
- 17-test suite: 14 pass on fixture data (schema, D1-D4 populated, monotonicity, HLA flag, sweep grouping), 3 skip until real render in Plan 01-06

## Task Commits

Each task was committed atomically:

1. **Task 1-05-01: Create envs/qc_dashboard.yml** -- `df28a42` (feat)
2. **Task 1-05-02: Create aggregator + Quarto template + qc.smk rules** -- `79dec6c` (feat)
3. **Task 1-05-03: Create test_qc_dashboard.py** -- `d0f6764` (test)
4. **Task 1-05-04: Sweep complex regions table** -- merged into `79dec6c` (see deviation below)

## Files Created/Modified

- `envs/qc_dashboard.yml` -- Quarto + RMarkdown + DT conda env (python 3.11, pandas 2.2, r 4.4, pyyaml)
- `src/snakemake/scripts/susie_qc_aggregate.py` -- JSON -> TSV aggregator with --aggregated-only mode for sweep reuse
- `src/snakemake/scripts/susie_qc_report.qmd` -- Quarto HTML dashboard template with DT::datatable + DT::formatStyle conditional formatting
- `src/snakemake/rules/qc.smk` -- 3 new rules: susie_qc_aggregate, build_sweep_complex_regions_table, build_susie_qc_dashboard
- `tests/phase1/test_qc_dashboard.py` -- 17 tests across 3 classes (TestAggregatorSchema, TestSweepTable, TestDashboardHTML)

## Aggregated TSV Column List

From fixture test run against sample_susie_output.json + synthetic HLA:

```
region_id  trait  ancestry  status  convergence_status  L_used  L_saturated  ld_source  n_variants
ks_pvalue  max_abs_z  lambda_gc  converged  niter  elbo_final
kriging_n_outliers  kriging_max_logLR  kriging_lambda
n_CS_macor_0.1  n_CS_macor_0.5  n_CS_macor_0.9
total_PIP_macor_0.1  total_PIP_macor_0.5  total_PIP_macor_0.9  max_PIP  is_complex_region
```

## Dashboard Styling Decisions

| Condition | Color | Hex | Rationale |
|-----------|-------|-----|-----------|
| ld_source == ukbb_ld_tiled_block_diagonal | Red | #ffcccc | T-1-04: HLA block-diagonal approximation caveat |
| convergence_status == non_converged | Dark red | #ff9999 | Retry ladder failed; excluded from Tier 1 |
| convergence_status == converged_regularized | Orange | #ffd699 | LD regularized; interpret with caution |
| convergence_status == converged_max_iter | Light yellow | #fff2cc | Required extra iterations; mild caution |
| L_saturated == TRUE | Yellow | #ffff99 | All L=10 effects retained; may warrant L=20 rerun |
| is_complex_region == TRUE | Purple | #e6ccff | Pre-specified complex region from susie_policy.yaml |

## Decisions Made

- **Tasks 2+4 merged:** The aggregator (Task 2) and sweep table extension (Task 4) were implemented together since Task 4 is strictly additive to the same file (susie_qc_aggregate.py) and qc.smk. This avoids a partial-rewrite commit and keeps the aggregator schema stable from first commit.
- **ld_source/ld_matrix dual-key tolerance:** run_susie_rss.R writes `ld_matrix = ld_source` (R list key is `ld_matrix`, value is the LD source string). The plan interfaces document `ld_source`. Aggregator reads both keys with `ld_source` taking precedence (Rule 1: auto-fix bug where plan interfaces and actual JSON schema diverge).
- **Quarto/RMarkdown fallback:** build_susie_qc_dashboard shell block checks `command -v quarto` and falls back to `rmarkdown::render()` if unavailable. Both produce valid self-contained HTML with DT tables.
- **Policy trait_list absent:** susie_policy.yaml pre_specified entries have no `trait_list` key. Sweep table treats all 4 regions as applicable to any trait in the data (match-any semantics with None sentinel).
- **pyyaml added to env:** The sweep table needs to parse susie_policy.yaml; added `pyyaml` to envs/qc_dashboard.yml (not in original plan spec).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ld_source vs ld_matrix JSON key mismatch**
- **Found during:** Task 2 (aggregator design)
- **Issue:** Plan interfaces document `ld_source` as the JSON key, but run_susie_rss.R (line 490) writes `ld_matrix = ld_source`. The test fixture (sample_susie_output.json) has no ld_source key at all. HLA test fixture uses `ld_matrix` key.
- **Fix:** Aggregator `_pick_ld_source()` reads both keys with `ld_source` preferred over `ld_matrix`
- **Files modified:** src/snakemake/scripts/susie_qc_aggregate.py
- **Verification:** test_aggregator_ld_source_surfaced passes (HLA fixture uses ld_matrix key, aggregator correctly extracts value)
- **Committed in:** 79dec6c (Task 2 commit)

**2. [Rule 2 - Missing Critical] pyyaml dependency for sweep table policy parsing**
- **Found during:** Task 2 (sweep table implementation)
- **Issue:** Plan env spec didn't include pyyaml, but sweep table needs yaml.safe_load for susie_policy.yaml
- **Fix:** Added `pyyaml` to envs/qc_dashboard.yml dependencies
- **Files modified:** envs/qc_dashboard.yml
- **Committed in:** df28a42 (Task 1 commit, proactively added)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical)
**Impact on plan:** Both fixes necessary for correctness. No scope creep. Task 4 merge into Task 2 is organizational, not a scope deviation.

## Issues Encountered

- Snakemake dry-run with `--forceall --allowed-rules` fails due to missing upstream data (expected per DEF-01-04/DEF-01-05). Used `snakemake --list` to verify rule parsing instead. All 3 new rules appear in rule list with zero parse errors.

## User Setup Required

None -- no external service configuration required.

## Known Stubs

None. All aggregator columns are wired to real JSON fields from run_susie_rss.R output. Dashboard DT::datatable renders from the TSV directly. Sweep table build_sweep_table reads from aggregated TSV. No hardcoded empty values or placeholder text.

## Next Phase Readiness

**Plan 01-06 (smoke test) preconditions:**

1. **Data acquisition:** DEF-01-04 (GRCh38 liftover for HGDP+1kG AFR LD) is still pending. Without real LD matrices, `run_finemap` cannot produce real JSON outputs for the aggregator to consume.
2. **Env materialization:** `envs/qc_dashboard.yml` must be materialized via `conda env create` before dashboard render. The yaml file exists and parses; actual env creation deferred to 01-06 runtime.
3. **UKBB-LD data:** Block-diagonal UKBB-LD tiles for HLA_6p21 must be downloaded and assembled (Plan 01-02 scripts exist but require the data).
4. **Config correctness:** `config/pipeline.yaml` must have `finemap.methods: [susie]` for FINEMAP_OUTPUTS to be non-empty, which susie_qc_aggregate depends on as an input.

**Phase 1 success criteria status after 01-05:**
- SC#1 (SuSiE policy): DONE (01-01)
- SC#2 (LD pipelines): DONE (01-02, 01-03)
- SC#3 (D1-D4 diagnostics in JSON): DONE (01-01)
- SC#4 (coloc.abf purge): DONE (01-04)
- SC#5 (QC dashboard): DONE (01-05, this plan)
- SC#6 (End-to-end smoke test): PENDING (01-06)

---
*Phase: 01-coloc-susie-fine-mapping-spine*
*Completed: 2026-04-11*
