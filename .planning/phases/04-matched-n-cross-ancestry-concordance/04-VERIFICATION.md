---
phase: 04-matched-n-cross-ancestry-concordance
verified: 2026-04-16T03:32:14Z
status: human_needed
score: 11/12
gaps:
human_verification:
  - test: "Run smoke pilot: snakemake --profile config/cluster_lsf --use-conda -s Snakefile results/matched_n/SMOKE_PILOT_REPORT.md (1 trait x 1 region x 5 bootstraps)"
    expected: "SMOKE_PILOT_REPORT.md populated with actual wall_clock_per_bootstrap, susie_convergence, pph4_range, and extrapolated total wall-clock; all PENDING fields replaced with real numbers; GO/NO-GO verdict recorded"
    why_human: "This is a blocking compute gate (autonomous: false in 04-05-PLAN.md). The pilot requires actual LSF job execution and Carter's review of timing + convergence before full production launch. The report currently contains only PENDING template values — the pilot was never run."
  - test: "Review pilot approval signal and authorize full production launch"
    expected: "Carter explicitly signals 'approved for full LSF launch' or 'adjust LSF topology to X concurrent cores' based on pilot timing report"
    why_human: "04-05-PLAN.md T1 is a human-verify checkpoint (gate: blocking). The 04-05-SUMMARY claims approval was received, but SMOKE_PILOT_REPORT.md and 04-PILOT.md both show the pilot is 'awaiting LSF execution' with all fields PENDING."
---

# Phase 04: Matched-N Cross-Ancestry Concordance Verification Report

**Phase Goal:** Replace broken Table 2 with power-corrected cross-ancestry concordance using matched-N bootstrap.
**Verified:** 2026-04-16T03:32:14Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC-1 | EUR down-sampled to match AFR N with 100x bootstrap concordance | VERIFIED | `config/matched_n.yaml` has `bootstrap_n: 100`; `src/python/se_inflation.py` implements `SE_EUR * sqrt(N_EUR / N_AFR)` (D-01a); bootstrap rules `run_matched_bootstrap` + `run_matched_coloc` wired in `matched_n.smk` |
| SC-2 | Expected detection probability under Hou et al. 2023 null computed | VERIFIED | `src/python/compute_detection_probability.py` implements NCP = (beta_hat/SE)^2 -> `scipy.stats.ncx2.sf`; framed as ORIGINAL-RESEARCH CONSTRUCTION per B-2; `compute_detection_probability` rule in `matched_n.smk` |
| SC-3 | LDSC cross-ancestry r_g calculated as global benchmark | VERIFIED | `rule ldsc_rg:` in `matched_n.smk`; `RG_COMBOS` expands to 35 tests (30 cross-trait + 5 same-trait EUR-AFR benchmarks); `is_global_benchmark` flag in `munge_trait_pair_rg.py`; BH-FDR via `apply_fdr.py` |
| SC-4 | New Table 2 generated, replacing old incomparable-trait-pair comparison | PARTIALLY VERIFIED | `src/python/assemble_table2.py` implements 10-column D-06a assembly with H7 verdict; `rule assemble_table2:` wired; `rule plot_violin:` wired. However: **production has not run** — no actual `results/matched_n/table2.tsv` exists because the smoke pilot gate has not been cleared. The code is complete and tested; the Table 2 awaits pilot approval + LSF execution. |

### Must-Have Checklist by Plan

#### Plan 04-01 — Scaffold, config, Wave 0 test stubs

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| config/matched_n.yaml parses with schema validation | VERIFIED | File exists; `bootstrap_n: 100`, `seed_base: 1000`, `h7_reduction_threshold_pp: 20`, `concordance_threshold: 0.8`, `ancestry_pairs:` all present; `schemas/matched_n.schema.yaml` validates |
| src/snakemake/rules/matched_n.smk loads without errors (snakemake --list) | VERIFIED | `rule build_matched_n_manifest:` and `rule all_matched_n:` confirmed present; Snakefile includes `matched_n.smk` |
| 7 test files exist with xfail stubs | VERIFIED | 8 test files total (7 Wave 0 stubs from 04-01 + 1 bootstrap driver test added in 04-02); all 7 original stubs present under `tests/test_matched_n_*.py` |
| bmi.AFR ingestion path documented in data_access.md with MVP/AoU/Pan-UKBB tiered fallback | VERIFIED | `MVP phs002453` and `AoU BMI AFR` both confirmed in `.planning/data_access.md` |
| Snakefile includes matched_n.smk | VERIFIED | `include:.*matched_n\.smk` confirmed in `Snakefile` |
| data_access.md contains MVP phs002453 | VERIFIED | grep confirmed |
| Mahajan 2022 DIAMANTE SE-inflation ref documented | VERIFIED | `Mahajan.*2022.*DIAMANTE` found in `data_access.md` |
| LSF quota documented | VERIFIED | `concurrent.*core` found in `data_access.md` (1024 slots on standard queue) |

#### Plan 04-02 — Bootstrap engine

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| SE-inflation math (D-01a) implemented and unit-tested | VERIFIED | `src/python/se_inflation.py::inflate_se` uses `np.sqrt(n_eur / n_afr)`; 11 unit tests pass |
| Z_b ~ N(beta_hat/SE_matched, 1) independent draws per bootstrap (D-01b) | VERIFIED | `draw_z_bootstrap` in `se_inflation.py` uses `rng.normal(loc=mean, scale=1.0)` |
| SuSiE refit per bootstrap via run_susie_rss.R reused verbatim (D-01b) | VERIFIED | `bootstrap_driver.py` greps `run_susie_rss\.R` (4 occurrences); legacy path used |
| coloc.susie re-estimation per bootstrap with AFR discovery .fit.rds held fixed (D-01c) | VERIFIED | `run_matched_coloc.R` uses `readRDS(opt$afr_fit)` on fixed input; `coloc::coloc.susie(fit_afr, fit_eur)` with AFR as dataset 1 |
| Seed determinism: seed = 1000 * trait_id + bootstrap_idx | VERIFIED | `compute_seed(trait_id, bootstrap_idx, seed_base=1000)` in `se_inflation.py`; test confirms `compute_seed(3,7,1000) == 3007` |
| run_matched_coloc.R reuses Phase 1 coloc logic verbatim | VERIFIED | `run_coloc_susie` referenced in script; `lead_sign_agree` column confirmed |

Key link: `run_matched_coloc.R -> readRDS(AFR .fit.rds)`: The plan pattern `readRDS.*AFR.*fit\.rds` does not match on a single line because the file uses `readRDS(opt$afr_fit)` where `afr_fit` is the CLI arg holding the path. The AFR readRDS is confirmed by reading the actual code — the link is WIRED.

#### Plan 04-03 — Concordance metrics

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| Per-trait Tier A retention (D-02a) computed across 100 bootstraps with 95% CI | VERIFIED | `compute_tier_a_retention.R` has `D-02a` header; 95% CI via quantile; test passes with synthetic fixtures |
| Per-trait credible-set Jaccard (D-02b) at PP.H4>=0.5 relaxed threshold | VERIFIED | `compute_jaccard.R` has `D-02b` (4 occurrences) and `PP.H4 >= 0.5` (5 occurrences) |
| Per-locus lead-variant sign agreement (D-02c) reported; flag if not ~100% | VERIFIED | `D-02c` in `compute_jaccard.R` (5 occurrences); WARN if `frac_sign_agree < 0.98` confirmed |
| Phase 9 joint criterion (D-02e) explicitly NOT reused — commented in script header | VERIFIED | `D-02e EXPLICITLY NOT REUSED` header confirmed in `compute_tier_a_retention.R` |
| Unmatched concordance baseline co-computed for H7 verdict | VERIFIED | `unmatched_concordance` (4 occurrences) in `compute_tier_a_retention.R` |

Key link: `compute_tier_a_retention.R -> results/matched_n/coloc/**/coloc_summary.tsv` via glob: confirmed by `coloc_summary\.tsv` grep (4 occurrences) in the script.

#### Plan 04-04 — LDSC r_g matrix + detection probability

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| Up to 30 LDSC r_g tests wired (10 trait-pairs x 3 ancestry-pairs per D-04a) | VERIFIED | `rule ldsc_rg:` confirmed; `RG_COMBOS` in `matched_n.smk`; comment documents 30 cross-trait + 5 same-trait = 35 total |
| BH-FDR q<0.05 applied across ALL 30 tests jointly per D-04c | VERIFIED | `apply_fdr.py` uses `multipletests(..., method='fdr_bh')` across all tests; `D-04c` in header |
| Same-trait cross-ancestry r_g flagged as is_global_benchmark=TRUE per D-04b | VERIFIED | `is_global_benchmark` confirmed in `matched_n.smk` (line 218: `D-04b: 5 same-trait EUR-AFR benchmarks (is_global_benchmark=TRUE)`) and `assemble_table2.py` |
| SE>0.3 flagged per research verdict A-2 option (a) minimum-deviation | VERIFIED | `unreliable_se` column in `apply_fdr.py`; `SE > se_flag_threshold` logic confirmed |
| Per-locus detection probability under empirical NCP null (D-05a) | VERIFIED | `per_locus_detection_prob` using `scipy.stats.ncx2.sf` in `compute_detection_probability.py` |
| Trait-level expected concordance via arithmetic mean (D-05b/d) | VERIFIED | `arithmetic mean` in docstring; `('detection_prob', 'mean')` aggregation confirmed |
| ORIGINAL-RESEARCH CONSTRUCTION header (D-05, per RESEARCH B-2) | VERIFIED | `# ORIGINAL-RESEARCH CONSTRUCTION` confirmed (line 5 of `compute_detection_probability.py`) |
| D-05c parametric-prior-exclusion documented and tested | VERIFIED | `Hou et al. 2023 Table S1 is NOT used` confirmed in `compute_detection_probability.py` |
| osf_deviations.md contains B-2 entry | VERIFIED | `.planning/osf_deviations.md` exists; `B-2` pattern confirmed (4 occurrences) |

Plan artifact check for `statsmodels.stats.multitest.multipletests` as a single-line string: NOT matched because `apply_fdr.py` uses a two-line import (`from statsmodels.stats.multitest import multipletests`) + separate call. The functionality is fully present. This is a pattern-matching artefact, not a deficiency.

#### Plan 04-05 — Table 2 assembly + violin + smoke pilot gate

| Must-Have | Status | Evidence |
|-----------|--------|----------|
| Smoke-pilot (1 trait x 1 region x 5 bootstraps) completes and produces convergent .fit.rds | **HUMAN NEEDED** | `results/matched_n/SMOKE_PILOT_REPORT.md` exists but is a TEMPLATE with all fields PENDING. `04-PILOT.md` status is "Wired -- awaiting LSF execution." The pilot was NOT run. |
| Full LSF production launch gated on human review of pilot timing + convergence | **HUMAN NEEDED** | The gate exists correctly (04-05-PLAN `autonomous: false`). But gate cannot be cleared until pilot runs. |
| Table 2 per D-06a assembles with exactly 5 rows and 10 columns | VERIFIED (code) | `assemble_table2.py` implements 10-column D-06a structure; `compute_h7_verdict` with 20pp threshold; 13 tests pass. No actual `results/matched_n/table2.tsv` exists yet (production not run). |
| Jaccard Table 2b per D-06b assembles | VERIFIED (code) | `assemble_table2.py` emits `table2_jaccard.tsv`; `rule assemble_table2:` wired |
| Violin supplementary figure per D-06c assembles (one panel per trait) | VERIFIED (code) | `plot_violin.R` has `geom_violin` and `facet_wrap.*trait`; `rule plot_violin:` wired |
| rg_matrix supplementary per D-06d surfaced in all_matched_n target | VERIFIED (code) | `rule apply_rg_fdr:` outputs `rg_matrix.tsv`; wired into `all_matched_n` target |
| H7 verdict per trait computed with 20pp threshold per D-02d | VERIFIED | `compute_h7_verdict` uses `threshold_pp = cfg['h7_reduction_threshold_pp']` (20); boundary >= semantics tested |
| Negative-control integration test green | VERIFIED | `test_matched_n_negcontrol.py` skips cleanly pre-production; activates post-LSF |
| VALIDATION.md Per-Task Verification Map populated | VERIFIED | 17 entries (4-01-01 through 4-05-04), all marked green; `nyquist_compliant: true` |

---

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `config/matched_n.yaml` | VERIFIED | All 6 pre-registered parameters present |
| `schemas/matched_n.schema.yaml` | VERIFIED | Validates config |
| `src/snakemake/rules/matched_n.smk` | VERIFIED | All rules wired: manifest, bootstrap, coloc, retention, jaccard, ldsc_rg, FDR, detection, table2, violin |
| `src/python/se_inflation.py` | VERIFIED | inflate_se, draw_z_bootstrap, compute_seed; D-01a/b math correct |
| `src/snakemake/scripts/bootstrap_driver.py` | VERIFIED | Calls run_susie_rss.R verbatim; inflate_se + compute_seed wired |
| `src/snakemake/scripts/run_matched_coloc.R` | VERIFIED | AFR .fit.rds held fixed; D-02c lead_sign_agree hook present |
| `src/snakemake/scripts/compute_tier_a_retention.R` | VERIFIED | D-02a/d/e; unmatched_concordance; per_bootstrap_retention output |
| `src/snakemake/scripts/compute_jaccard.R` | VERIFIED | D-02b/c; PP.H4 >= 0.5; sign agreement WARN |
| `src/python/apply_fdr.py` | VERIFIED | BH-FDR via multipletests; unreliable_se flag; D-04c |
| `src/python/compute_detection_probability.py` | VERIFIED | ORIGINAL-RESEARCH CONSTRUCTION header; NCP math; D-05c exclusion |
| `src/python/assemble_table2.py` | VERIFIED | 10-col Table 2; H7 verdict; is_global_benchmark filter |
| `src/snakemake/scripts/plot_violin.R` | VERIFIED | geom_violin; facet_wrap; unmatched + Hou overlays |
| `.planning/osf_deviations.md` | VERIFIED | B-2-resolution entry present |
| `tests/test_matched_n_*.py` (8 files) | VERIFIED | All xfail stubs converted to passing tests by Plans 04-02 through 04-05 |
| `tests/fixtures/matched_n/` | VERIFIED | Synthetic bootstrap fixtures present |
| `.planning/phases/04-matched-n-cross-ancestry-concordance/04-VALIDATION.md` | VERIFIED | nyquist_compliant: true; 17 entries all green |
| `results/matched_n/SMOKE_PILOT_REPORT.md` | PARTIAL | File exists but is a template; all timing/convergence fields PENDING — pilot not executed |
| `.planning/phases/04-matched-n-cross-ancestry-concordance/04-PILOT.md` | PARTIAL | Plan wired; execution command documented; status "awaiting LSF execution" |

---

## Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `Snakefile` | `src/snakemake/rules/matched_n.smk` | `include:.*matched_n\.smk` | WIRED |
| `bootstrap_driver.py` | `run_susie_rss.R` | subprocess invocation | WIRED (4 grep matches) |
| `run_matched_coloc.R` | AFR .fit.rds | `readRDS(opt$afr_fit)` | WIRED (confirmed by code inspection) |
| `compute_tier_a_retention.R` | `coloc_summary.tsv` | glob over bootstrap dirs | WIRED (4 grep matches for `coloc_summary.tsv`) |
| `assemble_table2.py` | [tier_a_retention, jaccard, detection_probability, rg_matrix].tsv | `.merge(on='trait')` | WIRED (DataFrame merge confirmed) |
| `plot_violin.R` | `coloc/**/coloc_summary.tsv` | ggplot2 violin | WIRED (geom_violin + facet_wrap confirmed) |

---

## Decision Compliance (D-ID Spot-Checks)

| Decision | Check | Status |
|----------|-------|--------|
| D-01a SE-inflation formula `SE_EUR * sqrt(N_EUR/N_AFR)` | `grep 'sqrt(n_eur / n_afr)' src/python/se_inflation.py` | PASS (2 matches) |
| D-01c AFR discovery .fit.rds immutably fixed | `run_matched_coloc.R` uses `readRDS(opt$afr_fit)` as input-only | PASS |
| D-02d 20pp H7 threshold from config | `threshold_pp = cfg['h7_reduction_threshold_pp']` in `assemble_table2.py` | PASS |
| D-02e Phase 9 joint criterion explicitly NOT reused | `D-02e EXPLICITLY NOT REUSED` header in `compute_tier_a_retention.R` | PASS |
| D-04b same-trait EUR-AFR is_global_benchmark | Line 218 `matched_n.smk`; `is_global_benchmark` in `assemble_table2.py` | PASS |
| D-04c BH-FDR across ALL tests jointly | `method='fdr_bh'` in `apply_fdr.py` | PASS |
| D-05 ORIGINAL-RESEARCH CONSTRUCTION (B-2 resolution) | Header line 5 of `compute_detection_probability.py` | PASS |
| D-05c Hou Table S1 parametric prior NOT used | `Hou et al. 2023 Table S1 is NOT used` in `compute_detection_probability.py` | PASS |
| Seed formula: 1000 * trait_id + bootstrap_idx | `compute_seed` in `se_inflation.py`; test confirms 3007 | PASS |
| osf_deviations.md B-2 entry | File exists; 4 B-2 occurrences | PASS |

---

## Behavioral Spot-Checks

| Behavior | Check | Status |
|----------|-------|--------|
| Config schema validation passes | `bootstrap_n: 100`, `seed_base: 1000`, `h7_reduction_threshold_pp: 20`, `concordance_threshold: 0.8`, `ancestry_pairs:` all present | PASS |
| SE-inflation identity at equal N | `inflate_se(se, N=100k, N=100k)` -> factor=1.0 (test exists) | PASS (test confirmed) |
| BH-FDR method parameter | `method='fdr_bh'` confirmed in `apply_fdr.py` | PASS |
| Snakemake loads matched_n.smk rules | `include:.*matched_n\.smk` in Snakefile; `rule build_matched_n_manifest:`, `rule all_matched_n:` present | PASS |
| Smoke pilot report populated | `results/matched_n/SMOKE_PILOT_REPORT.md` | FAIL — template only; all fields PENDING; pilot not run |

---

## Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `results/matched_n/SMOKE_PILOT_REPORT.md` | All timing/convergence/verdict fields are PENDING template values | Warning | The 04-05-SUMMARY claims pilot was approved ("Carter's pilot approval (received)") but the report contradicts this — pilot was never executed. The VALIDATION.md entry marks `4-05-01` as "✅ approved" based on `test -f results/matched_n/SMOKE_PILOT_REPORT.md` (file existence only). This is a false positive for the pilot checkpoint. |

---

## Requirements Coverage

| Requirement ID | Status | Evidence |
|----------------|--------|----------|
| Table-2-replacement | SATISFIED (code complete; production pending pilot gate) | `assemble_table2.py` + `rule assemble_table2:` + H7 verdict logic; 10-column structure tested; pilot + LSF run needed for actual TSV |
| H7-pre-registration | SATISFIED | H7 threshold (20pp) from `config/matched_n.yaml`; `compute_h7_verdict` with `>= threshold_pp` semantics; boundary test frozen |

No REQ-IDs from REQUIREMENTS.md apply directly to Phase 4 (ROADMAP says "none directly; fixes Table 2").

---

## Human Verification Required

### 1. Smoke Pilot Execution

**Test:** Run `snakemake --profile config/cluster_lsf --use-conda -s Snakefile results/matched_n/SMOKE_PILOT_REPORT.md` after Phase 1 AFR `.fit.rds` for t2d/TCF7L2_10q25_2 is confirmed present.

**Expected:**
- `SMOKE_PILOT_REPORT.md` populated with real values for: `wall_clock_per_bootstrap`, `susie_convergence` (target: 5/5), `pph4_range`, `pph4_mean`, `n_signal_rows`, `Estimated wall-clock` extrapolation.
- All GO/NO-GO checkboxes evaluated.
- Wall-clock per bootstrap < 5 minutes (GO threshold).
- Extrapolated total < 14 days at 1024 concurrent LSF slots (GO threshold).
- PP.H4 range stable across 5 bootstraps (range < 0.3).

**Why human:** This is a blocking compute gate (04-05-PLAN.md `autonomous: false`). Requires actual LSF execution and judgment on timing, convergence, and whether production scope adjustment is needed. Cannot be verified by static code inspection.

### 2. Pilot Approval and Full Production Launch Authorization

**Test:** After reviewing the populated SMOKE_PILOT_REPORT.md, Carter signals explicit approval:
- "approved for full LSF launch" (no topology change), OR
- "adjust LSF topology to X concurrent cores" (with specific adjustment)

**Expected:** Full production launch proceeds: `snakemake --profile config/cluster_lsf --use-conda all_matched_n`. After completion, `results/matched_n/table2.tsv`, `results/matched_n/table2_jaccard.tsv`, `results/matched_n/rg_matrix.tsv`, and `results/matched_n/supp_violin.pdf` all exist with real data. The negative-control test (`test_matched_n_negcontrol.py`) activates and passes.

**Why human:** Production launch is explicitly gated on human review. The code is complete and tested; the gate is a methodological quality control point, not a software deficiency.

---

## Gaps Summary

No automated-verification gaps. The phase code is complete and correct across all 5 plans. All 12 main must-haves that can be verified statically are VERIFIED. The single remaining item is the smoke pilot execution gate — a deliberate, pre-registered human checkpoint that has been correctly wired but not yet cleared.

The 04-05-SUMMARY's claim that "Carter's pilot approval (received)" is misleading: the SMOKE_PILOT_REPORT.md and 04-PILOT.md both show the pilot is awaiting LSF execution. The VALIDATION.md marks the pilot entry as approved based on file existence (`test -f`), which does not verify actual pilot execution. This should be corrected when the pilot runs.

**Score rationale:** 11/12 must-haves verified (the smoke pilot execution is the 12th; it is structurally correct but has not been cleared at the human gate).

---

_Verified: 2026-04-16T03:32:14Z_
_Verifier: Claude (gsd-verifier)_
