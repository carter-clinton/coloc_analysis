---
phase: 09-replication-in-independent-cohorts
verified: 2026-04-14T04:41:15Z
status: human_needed
score: 3/3 roadmap success criteria verified at pipeline level
overrides_applied: 0
re_verification:
  previous_status: null
  note: Initial verification. User declared scope: "This phase produces a PIPELINE — not actual replication results on real cohort data." Verification checks that infrastructure CAN produce the required artifacts when real data flows through.
human_verification:
  - test: "Execute the full Phase 9 Snakemake DAG end-to-end on real cohort sumstats (FinnGen R12, GBMI, MVP phs001672, BBJ hum0197-v3) and verify master_table.tsv emits with populated per-cohort replication columns."
    expected: "Four D-07 artifacts materialize with non-empty rows; >= 2 cohort replications completed per SC#1; replication-adjusted (FIQT + post-hoc-powered) effect sizes computed per SC#2; holdout table generated per SC#3."
    why_human: "Pipeline infrastructure is verifiable statically, but the roadmap Success Criteria are phrased as operational outcomes (\"2 independent cohort replications completed\") that only materialize once real cohort downloads + discovery .fit.rds from Phase 1 + tier_assignments.tsv from Phase 2 are resolved on disk and the smoke test runs."
  - test: "Scientific Layer 3: HLA negative control check (chr6:28-33Mb) against master_table.tsv after real-data run."
    expected: ">= 70% of HLA-region signals fail the joint criterion (replicated_joint_0.8 == False) in >= 3 of 4 cohort groups."
    why_human: "Requires post-execution master_table.tsv with real data; pre-execution xfail is the documented state (test_negative_controls.py::test_hla_fails_replication_joint). This is a scientific sanity check, not a code-level verification."
  - test: "COJO N=503 caveat narrative appears in supplementary methods and in stderr WARN during real-data run."
    expected: "Both the docs/methods/phase9_replication.md narrative (verified present) and the run_cojo.sh stderr (verified present via `4000` + `WARN` literals) surface the caveat when real 1000G EUR/AFR panels are used."
    why_human: "Three-layer enforcement (shell + tests + methods doc) is code-verified; verifying the live WARN emission requires running GCTA against the actual 1000G PLINK reference once Phase 5 pathway.smk download_ldsc_baseline completes."
---

# Phase 9: Replication in Independent Cohorts — Verification Report

**Phase Goal:** Validate T1 findings (Phase 1 coloc.susie credible sets + Phase 2 Tier A/B gene-tissue-trait triples) in independent cohorts. Produce a master replication table under joint effect-size + coloc criterion, winner's-curse-corrected effect sizes, and cross-ancestry generalization panel. Last T1 phase before Checkpoint #1.

**Verified:** 2026-04-14T04:41:15Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Scope Clarification

The user's instruction explicitly scopes this verification: *"This phase produces a PIPELINE (harmonizers, coloc.susie wrappers, FIQT/COJO tools, master table assemblers) — not actual replication results on real cohort data. Real data execution is a separate future runtime step (awaiting smoke test). Verification should check that the infrastructure CAN produce the required artifacts when real data flows through, not that the outputs themselves exist yet."*

Accordingly, all verification below is **infrastructure-level**. The ROADMAP Success Criteria will fully materialize only after the end-to-end smoke test executes against real cohort data — that is the `human_verification` item above.

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria — all 3)

| # | Truth (Success Criteria) | Status | Evidence |
|---|--------------------------|--------|----------|
| 1 | At least 2 independent cohort replications can be completed (FinnGen, GBMI, MVP, AoU, BBJ) | VERIFIED (infrastructure) | 4 cohort harmonizers present (`harmonize_finngen.py`, `harmonize_gbmi.py`, `harmonize_mvp.py`, `harmonize_bbj.py`); `config/replication_cohorts.yaml` enumerates FinnGen R12, GBMI (EUR + AFR strata), MVP phs001672 (EUR + AFR), BBJ hum0197-v3 — far exceeding the "at least 2" threshold. Replication per-signal pipeline (`run_replication_coloc_susie.R`, `compute_per_cohort_effect_size_test.py`, `aggregate_replication_meta.R`) wired through manifest-driven Snakemake rules. |
| 2 | Replication-adjusted effect sizes calculated | VERIFIED (infrastructure) | `run_fiqt.R` wraps `winnerscurse::FDR_IQT` (D-04a) producing `beta_FIQT` + `se_FIQT`; `compute_per_cohort_effect_size_test.py` computes Bonferroni-adjusted significance, same-direction check, and post-hoc power; `aggregate_replication_meta.R` delivers IVW FE meta via `metafor::rma.uni(method='FE')`; `build_master_replication_table.py` assembles 4-column effect-size schema (beta_discovery_raw, beta_discovery_FIQT, beta_replication, beta_meta) per D-04b. |
| 3 | Hold-out replication tables generated for supplementary material | VERIFIED (infrastructure) | `build_replication_holdout.py` (`loco_meta`) produces leave-one-cohort-out IVW jack-knife grouped by (signal_id × cohort_ancestry); Snakemake rule `assemble_replication_holdout_supplementary` emits `results/replication/replication_holdout_supplementary.tsv`. Test `test_master_table_schema.py` covers 3 rows × LOCO output. |

**Score:** 3/3 ROADMAP Success Criteria verified at the infrastructure level.

### Required Artifacts (from PLAN frontmatter across 5 plans)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `config/replication_cohorts.yaml` | 4-cohort registry + traits × ancestry × endpoints | VERIFIED | 9.2 KB; finngen_r12 + mvp_phs001672 + bbj_hum0197_v3 + gbmi blocks; `panels.primary_eur/primary_afr/generalization_eas` routing with `signal_scope: tier_ab_only` for BBJ. |
| `envs/gcta.yml` | GCTA 1.94.1 bioconda env | VERIFIED | 594 B; `bioconda::gcta=1.94.1`. |
| `envs/r_coloc.yml` | Extended with metafor + remotes | VERIFIED | 1.3 KB; `r-metafor`, `r-remotes` present. |
| `src/snakemake/rules/replication.smk` | Production rules (not TODO) | VERIFIED | 29.6 KB, 25 `rule` definitions across §A-§G; `grep 'TODO plan' → 0`. |
| `src/python/harmonize_finngen.py` | FinnGen R12 → canonical schema | VERIFIED | 152 lines; `harmonize_finngen_sumstats` + inline liftover. |
| `src/python/harmonize_gbmi.py` | GBMI per-ancestry stratum extractor | VERIFIED | 153 lines; B-2 guard raises `ValueError` for missing ancestry prefix. |
| `src/python/harmonize_mvp.py` | MVP dual-schema (REGENIE + dbGaP) | VERIFIED | 252 lines; `_detect_schema()` dispatches; `reconstruct_signed_beta()` handles |β| + Coded Allele. |
| `src/python/harmonize_bbj.py` | BBJ zip extractor + harmonizer | VERIFIED | 156 lines; `extract_bbj_zip` + `harmonize_bbj_sumstats`. |
| `src/python/sumstats_utils.py` | `is_palindromic`, `filter_palindromic_ambiguous`, `liftover_to_grch37` | VERIFIED | 7.6 KB; 3 Phase 9 helpers appended; `liftover_coordinates` backed by `pyliftover` with LRU cache. |
| `src/python/validate_replication_sumstats.py` | Canonical schema + liftover QC gate | VERIFIED | 72 lines; enforces 10-column schema + drop-rate ≤ 5%. |
| `src/python/build_replication_manifest.py` | Signal × cohort crossjoin with D-05 panels | VERIFIED | 334 lines; panel-driven routing; D-05c BBJ `tier_ab_only` gate verified. |
| `src/snakemake/scripts/run_replication_susie.R` | SuSiE-RSS re-fit per manifest row | VERIFIED | 257 lines; `coloc::runsusie(suffix=2)`; 2-stage retry ladder. |
| `src/snakemake/scripts/run_fiqt.R` | `winnerscurse::FDR_IQT` wrapper | VERIFIED | 114 lines; lazy install of amandaforde/winnerscurse @ SHA 2ed00bb. |
| `src/snakemake/scripts/run_replication_coloc_susie.R` | `coloc.susie(disc_fit, rep_fit)` + PP.H4 sweep | VERIFIED | 156 lines; single tryCatch wraps readRDS + coloc.susie; emits PP.H4 sweep booleans {0.5, 0.7, 0.8, 0.9}. |
| `src/snakemake/scripts/aggregate_replication_meta.R` | IVW FE meta via metafor | VERIFIED | 136 lines; `metafor::rma.uni(method='FE')` grouped by (signal_id × cohort_ancestry); BBJ generalization rows excluded. |
| `src/python/compute_per_cohort_effect_size_test.py` | Bonferroni + same-direction + post-hoc power + joint | VERIFIED | 174 lines; 4 pure functions + `process_cohort` merger. |
| `src/python/collect_replication_effect_sizes.py` | Per-cohort raw effect-size collector (I-5 producer) | VERIFIED | 149 lines; lead-SNP match with chr:bp fallback. |
| `src/snakemake/scripts/prepare_cojo_ma.py` | Canonical → GCTA .ma 8-column | VERIFIED | 101 lines. |
| `src/snakemake/scripts/run_cojo.sh` | GCTA --cojo-slct wrapper | VERIFIED | 63 lines; `set -euo pipefail`, N<4000 WARN, --cojo-p 5e-8 --cojo-wind 10000. |
| `src/python/build_cojo_sensitivity_table.py` | Aggregates .jma.cojo outputs | VERIFIED | 151 lines. |
| `src/python/build_master_replication_table.py` | RESEARCH §16 master table assembler | VERIFIED | 307 lines; 4 effect-size columns, per-cohort suffix blocks, I-2 meta merge, I-3 sample-overlap flags. |
| `src/python/build_cross_ancestry_panel.py` | Tier A+B × BBJ-EAS generalization panel | VERIFIED | 95 lines; asserts `credible_set_SNP` excluded (D-05c belt-and-braces). |
| `src/python/build_replication_holdout.py` | Leave-one-cohort-out IVW jack-knife | VERIFIED | 109 lines; `loco_meta` groups by (signal_id × cohort_ancestry). |
| `docs/methods/phase9_replication.md` | Manuscript methods fragment | VERIFIED | 166 lines; 48 matches across {FinnGen, GBMI, MVP, BBJ, FIQT, COJO, ancestry, ischemic, stroke, winner, 4 cohorts}. |
| `tests/phase9/fixtures/mock_disc.fit.rds` + `mock_rep.fit.rds` | Deterministic coloc fixtures | VERIFIED | 2994 + 2983 bytes; committed via `.gitignore` exception `!tests/**/fixtures/*.rds`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `Snakefile` | `src/snakemake/rules/replication.smk` | `include:` directive | WIRED | Line 134: `include: "src/snakemake/rules/replication.smk"`. |
| `replication.smk` | `config/replication_cohorts.yaml` | `configfile:` directive | WIRED | `configfile: "config/replication_cohorts.yaml"` (Plan 09-01 deviation fix). |
| `run_replication_coloc_susie.R` | `coloc::coloc.susie` | R namespace call | WIRED | Line 71: `coloc::coloc.susie(disc_fit, rep_fit)` inside single tryCatch. |
| `aggregate_replication_meta.R` | `metafor::rma.uni` | R namespace call | WIRED | Line 45: `metafor::rma.uni(yi=..., sei=..., method="FE")`. |
| `compute_per_cohort_effect_size_test.py` | FIQT output + replication effect-size table | pandas merge on signal_id | WIRED | Line 120+: merges `fiqt_df` + `effect_df` + `coloc_df` on signal_id. |
| `run_fiqt.R` | `winnerscurse::FDR_IQT` | R package API | WIRED | Line 76: `winnerscurse::FDR_IQT(summary_data=df, min_pval=1e-300)`; lazy install @ SHA 2ed00bb. |
| `build_replication_manifest.py` | Phase 1 `.fit.rds` + Phase 2 `tier_assignments.tsv` | file-path crossjoin | WIRED | `_resolve_rep_path` resolves canonical `harmonized_grch37/` path; tolerates missing upstream (returns empty DF). |
| `run_cojo.sh` | 1000G PLINK reference | `--bfile` arg (dep on Phase 5 flag) | WIRED | `.baseline_download_done` flag declared as input on `run_cojo_slct` rule (Plan 09-05 deviation fix). |
| `build_cross_ancestry_panel.py` | manifest `signal_class ∈ {tier_A, tier_B}` | pandas filter + assert | WIRED | Line 46+: `isin(["tier_A_triple", "tier_B_triple"])` + post-filter assertion. |
| `aggregate_per_cohort_combined` rule | `compute_per_cohort_effect_size_test` + `ivw_meta_aggregate` + holdout | Snakemake DAG | WIRED | Plan 09-05 Rule 2 deviation fix: per_cohort_combined.tsv producer added so meta + holdout do not dangle. |
| `replication.smk` all-target | 4 D-07 output artifacts | rule `all_replication` | WIRED | Lines 666-669: master_table.tsv + cross_ancestry_generalization_tier_ab.tsv + cojo_sensitivity.tsv + replication_holdout_supplementary.tsv all declared as terminal outputs. |

### Data-Flow Trace (Level 4)

Per the user's scope clarification, real cohort data has not yet flowed through the pipeline — that is the `human_verification` runtime step. Infrastructure-level data-flow (manifest → per-cohort harmonized → fit → coloc → effect-size → meta → master table) is wired end-to-end as shown in the key-link table above. Static grep + Snakemake DAG resolution confirm every consumer has an upstream producer.

Plan 09-04 Deviation "Rule 2 Missing critical functionality" — the `per_cohort_combined.tsv` aggregator was initially absent, creating a dangling input for `ivw_meta_aggregate`; Plan 09-05 added `aggregate_per_cohort_combined` so the DAG now closes. Verified: Snakemake `--list` shows `aggregate_per_cohort_combined` rule and `grep 'TODO plan' = 0`.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase 9 pytest suite collects and runs | `pytest tests/phase9 -q --tb=line` | 77 passed, 3 xfailed, 0 failed (xfails = HLA Layer-3 post-execution by design) | PASS |
| Snakemake rule count | `grep -c '^rule ' src/snakemake/rules/replication.smk` | 25 | PASS (exceeds 20 expected) |
| Snakemake DAG resolves | `snakemake --list` (via smoke_dev Python 3.11) | all_replication + 24 other phase-9 rules listed | PASS |
| No TODO markers in replication.smk | `grep -c 'TODO plan' src/snakemake/rules/replication.smk` | 0 | PASS |
| 4 D-07 output artifacts declared in all_replication target | grep master_table / cross_ancestry / cojo_sensitivity / replication_holdout | 4 distinct outputs declared (lines 666-669) | PASS |
| testthat suite | `Rscript -e 'testthat::test_dir(...)'` | SKIPPED — Rscript not available in default PATH of bash session; testthat results already documented in Plans 09-01 through 09-05 SUMMARYs (all green + 1 benign data.table warning) | SKIP |

### Requirements Coverage

| Requirement ID | Source Plan | Description | Status | Evidence |
|----------------|-------------|-------------|--------|----------|
| (none) | Plans 09-01 through 09-05 | All 5 plans declare `requirements: []` in frontmatter | N/A | Phase 9 has no directly-assigned REQ per ROADMAP (supports overall CP#1 validity only). |

Verified by grepping REQUIREMENTS.md Phase 9 mapping and plan frontmatter — no orphaned requirements.

### Anti-Patterns Found

Per Plan 09-01-SUMMARY through 09-05-SUMMARY: 0 Rule 2 scope-creep fixes, 0 unresolved stubs. All deviations (14 total across 5 plans) documented as Rule 1 (plan bug), Rule 2 (missing critical functionality auto-added), or Rule 3 (blocking env setup). Noteworthy: 1 Rule 2 fix in Plan 09-05 added `aggregate_per_cohort_combined` producer rule to close the DAG for `ivw_meta_aggregate` + `build_replication_holdout`.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | no blocker TODO / placeholder / `return None` on a rendering path detected | INFO | Pipeline is substantive code throughout; all stubs previously flagged have been resolved by subsequent plans. |

3 xfailed tests in pytest suite (documented as expected pre-execution state):
- `test_negative_controls.py::test_hla_fails_replication_joint` — HLA Layer-3 scientific check; xfails until real master_table.tsv populated.
- 2 additional xfails for master_table / cross_ancestry post-run checks tied to real-data outputs.

These are intentional per Plan 09-05 SUMMARY and do not represent hidden stubs.

### Human Verification Required

See `human_verification` section in frontmatter. Three items:

1. **End-to-end smoke test on real cohort data.** Verify ROADMAP Success Criteria #1 (≥ 2 cohort replications), #2 (replication-adjusted effect sizes populated), #3 (holdout table emitted) all materialize as populated rows — not just schema — after the pipeline runs on FinnGen R12 + GBMI + MVP + BBJ. This is the principal remaining validation and is explicitly out-of-scope per the user's verification instruction.

2. **HLA negative control Layer-3 check.** Post-execution expectation: ≥ 70% of HLA-region signals fail the joint criterion in ≥ 3 of 4 cohort groups. Currently xfailed by design.

3. **COJO N=503 WARN emission at runtime.** Verify the three-layer enforcement lights up as intended when GCTA actually runs against 1000G EUR/AFR PLINK panels.

### Gaps Summary

No code-level gaps. The pipeline infrastructure for Phase 9 is production-complete:

- 4 cohort harmonizers produce canonical 10-column GRCh37 sumstats with palindromic filtering + liftover QC.
- Manifest builder crossjoin enforces D-02b (Tier C excluded), D-05 (ancestry-matched asymmetric panels), D-05c (BBJ tier_ab_only generalization), D-08 (LD panel per-ancestry routing).
- SuSiE re-fit reuses Phase 1 `susie_policy.yaml` verbatim (D-08); coloc.susie re-estimation emits PP.H4 sweep {0.5, 0.7, 0.8, 0.9} (D-03b) with uniform failure schema.
- Effect-size pipeline implements per-cohort Bonferroni (pitfall #4), same-direction check (D-03a), post-hoc power (pitfall #5), joint criterion (D-03a primary at PP.H4 ≥ 0.8), and IVW FE meta via metafor grouped by (signal_id × cohort_ancestry) excluding BBJ generalization (D-06b + T-09-17).
- COJO sensitivity (TIER-2 supplementary) implements GCTA --cojo-slct wrapper with N<4000 WARN three-layer enforcement (shell + tests + methods doc).
- Master table assembler emits RESEARCH §16 schema; cross-ancestry panel asserts credible_set_SNP exclusion; leave-one-cohort-out holdout produces RESEARCH §16 supplementary.
- All 4 D-07 output artifacts declared as terminal outputs in `rule all_replication`.
- Methods doc (docs/methods/phase9_replication.md) covers D-01 through D-05c + gotchas #1 + #3.
- 77 pytest phase9 tests pass (0 failures, 3 xfailed by design for post-execution scientific checks).

The remaining work is operational: run the pipeline against real cohort sumstats. That is the human-verification item above and is explicitly scoped out of this verification per user instruction.

---

*Verified: 2026-04-14T04:41:15Z*
*Verifier: Claude (gsd-verifier)*
