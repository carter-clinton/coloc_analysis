---
phase: 1
slug: coloc-susie-fine-mapping-spine
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-11
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Full Validation Architecture is in [01-RESEARCH.md#validation-architecture](01-RESEARCH.md) (§848). This file is the execution-time contract the planner and executor consume.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (Python, Snakemake rule/DAG tests) + `testthat` (R script unit tests) + `snakemake --dry-run` (DAG integrity) |
| **Config file** | `tests/toy_3locus/config_test.yaml` (already exists from Phase 0); new `tests/phase1/conftest.py` + `tests/testthat-phase1/` added in Wave 1 |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda --dry-run` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda && pytest tests/phase1/ -x && Rscript -e 'testthat::test_dir("tests/testthat-phase1/")'` |
| **Estimated runtime** | ~15 min (REQ-9 budget for full smoke REAL run) |

---

## Sampling Rate

- **After every task commit:** Run dry-run + relevant pytest/testthat target (~30s)
- **After every plan wave:** Run full smoke DAG dry-run + all Phase 1 unit tests (~3 min)
- **Before `/gsd-verify-work`:** Full smoke REAL run on toy dataset must be green (~15 min)
- **Max feedback latency:** 30 seconds per task, 15 minutes for phase gate

---

## Per-Task Verification Map

> Full task IDs will be assigned by the planner. This table pre-allocates the validation hooks per wave/REQ.

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-00 | 01-01 | 1 | N/A (cache hygiene) | Clean cache before first run | manual | `rm -rf {FINEMAP_DIR}/susie/` (Wave 1 Task 0) | Wave 1 Task 0 | ⬜ pending |
| 1-01-01 | 01-01 | 1 | REQ-2 #1 | policy YAML exists | integration | `test -f config/susie_policy.yaml && snakemake --dry-run` | ❌ Wave 1 creates | ⬜ pending |
| 1-01-02 | 01-01 | 1 | REQ-2 #2 | policy loaded by finemap.smk | unit | `grep -q "susie_policy.yaml" src/snakemake/rules/finemap.smk && grep -q "yaml::read_yaml" src/legacy/region_analysis/scripts/run_susie_rss.R` | ❌ Wave 1 adds | ⬜ pending |
| 1-01-03 | 01-01 | 1 | REQ-2 #3 | min_abs_corr sweep ≥3 values | unit | `pytest tests/phase1/test_susie_sweep.py::test_three_sweep_values -x` | ❌ Wave 1 | ⬜ pending |
| 1-01-04 | 01-01 | 1 | REQ-2 implicit (monotonicity) | `n_CS(0.1) ≥ n_CS(0.5) ≥ n_CS(0.9)` (soft flag) | property | `pytest tests/phase1/test_susie_sweep.py::test_monotonic_or_flag -x` | ❌ Wave 1 | ⬜ pending |
| 1-01-05 | 01-01 | 1 | REQ-2 (convergence) | retry ladder (max_iter → reg LD → flag) | property | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_retry_ladder.R")'` | ❌ Wave 1 | ⬜ pending |
| 1-01-06 | 01-01 | 1 | G1 (fit persistence) | `inherits(readRDS(fit_rds), "susie") == TRUE` | unit | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_fit_roundtrip.R")'` | ❌ Wave 1 | ⬜ pending |
| 1-01-07 | 01-01 | 1 | A6 resolution | `coloc::coloc.susie(readRDS(a), readRDS(b))` no-warning dispatch; fallback to `coloc::runsusie()` if test fails | unit | `Rscript -e 'testthat::test_file("tests/testthat-phase1/test_coloc_susie_dispatch.R")'` | ❌ Wave 1 | ⬜ pending |
| 1-02-01 | 01-02 | 2 | G4 (UKBB-LD) | `{LD_REF_DIR}/EUR_ukbb_ld/{region}.rds` exists; `ld_source` field present | integration | `pytest tests/phase1/test_ld_panels.py::test_ukbb_ld_output -x` | ❌ Wave 2 | ⬜ pending |
| 1-02-02 | 01-02 | 2 | G3 (HLA complex flag) | HLA_6p21 `.rds` metadata: `ld_source = "ukbb_ld_tiled_block_diagonal"` | unit | `pytest tests/phase1/test_ld_hla_flag.py -x` | ❌ Wave 2 | ⬜ pending |
| 1-03-01 | 01-03 | 3 | G4 (HGDP+1kG) | `{LD_REF_DIR}/AFR_hgdp_1kg/{region}.rds` exists; AFR sample count ≈ 730 | integration | `pytest tests/phase1/test_ld_panels.py::test_hgdp_afr_output -x` | ❌ Wave 2 | ⬜ pending |
| 1-04-01 | 01-04 | 4 | Success #4 (no coloc.abf) | `grep -rn "coloc\.abf" src/snakemake/ src/legacy/region_analysis/scripts/` returns only renamed legacy file | unit | `! grep -rn "coloc\.abf" src/snakemake/ && grep -rn "coloc\.abf" src/legacy/region_analysis/scripts/run_coloc_abf_legacy.R` | ❌ Wave 3 | ⬜ pending |
| 1-04-02 | 01-04 | 4 | G1 (coloc.susie output) | `sum(PP.H0..PP.H4) ≈ 1.0 ± 1e-6` per pairwise comparison | property | `pytest tests/phase1/test_coloc_susie_posterior_sum.py -x` | ❌ Wave 3 | ⬜ pending |
| 1-04-03 | 01-04 | 4 | Legacy compat schema | `augment_coloc_summary.py` parses new JSON | integration | `pytest tests/phase1/test_coloc_susie_compat.py -x` | ❌ Wave 3 | ⬜ pending |
| 1-05-01 | 01-05 | 5 | Success #5 (QC dashboard) | `results/finemap/qc_dashboard.html` exists with D1/D2/D3/D4 columns | integration | `pytest tests/phase1/test_qc_dashboard.py::test_dashboard_exists_has_columns -x` | ❌ Wave 5 | ⬜ pending |
| 1-05-04 | 01-05 | 5 | REQ-2 #3 standalone supp table | `results/finemap/sweep_complex_regions.tsv` with `known_complex` + `data_flagged` row groups and `n_CS_macor_{0.1,0.5,0.9}` columns | integration | `grep -q "build_sweep_complex_regions_table" src/snakemake/rules/qc.smk && grep -q "build_sweep_table" src/snakemake/scripts/susie_qc_aggregate.py && python -m py_compile src/snakemake/scripts/susie_qc_aggregate.py` | ❌ Wave 5 | ⬜ pending |
| 1-06-01 | 01-06 | 6 | Success #1 (SuSiE completes all T×A) | Full smoke DAG REAL run exits 0 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` | ⚠ Wave 5 (first REAL) | ⬜ pending |
| 1-06-02 | 01-06 | 6 | G5 D3 (LD quality sanity) | kriging_rss outlier count small on matched LD, large on mismatched | property | `pytest tests/phase1/test_kriging_rss_sanity.py -x` | ❌ Wave 4-5 | ⬜ pending |
| 1-06-03 | 01-06 | 6 | UAT #11 (monotonicity visual) | Dashboard spot-check on complex region | manual | Visual review of `results/finemap/qc_dashboard.html` | ⚠ manual | ⬜ pending |
| 1-06-04 | 01-06 | 6 | UAT #12 (new LD panels in use) | JSON `ld_source` field contains `ukbb_ld_tiled` or `hgdp_1kg` | unit | `pytest tests/phase1/test_ld_source_field.py -x` | ❌ Wave 5 | ⬜ pending |
| 1-06-05 | 01-06 | 6 | Methods fragment | `.planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` exists | manual | `test -f .planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` | ❌ Wave 5 | ⬜ pending |
| 1-06-06 | 01-06 | 6 | OSF amendment (UKBB-LD + 4-region scope) | Amendment note in methods_fragment.md references DOI 10.17605/OSF.IO/PVB5J | manual | `grep -q "10.17605/OSF.IO/PVB5J" .planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md` | ❌ Wave 5 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Phase 0 already shipped `tests/toy_3locus/Snakefile.test` + `config_test.yaml` + `expected_results.yaml` (dry-run verified, 29 jobs / 11 rules). The following Phase 1 test infrastructure is added in Wave 1:

- [ ] `tests/phase1/__init__.py` + `tests/phase1/conftest.py` — pytest fixtures for toy susie fits + mock LD
- [ ] `tests/phase1/test_susie_sweep.py` — sweep value count + monotonicity (soft flag)
- [ ] `tests/phase1/test_coloc_susie_compat.py` — schema compat with `augment_coloc_summary.py`
- [ ] `tests/phase1/test_coloc_susie_posterior_sum.py` — property test on PP sums
- [ ] `tests/phase1/test_qc_dashboard.py` — dashboard existence + column coverage
- [ ] `tests/phase1/test_ld_panels.py` — UKBB-LD and HGDP+1kG output presence
- [ ] `tests/phase1/test_ld_hla_flag.py` — HLA block-diagonal flag
- [ ] `tests/phase1/test_ld_source_field.py` — ld_source field not-identity check
- [ ] `tests/phase1/test_kriging_rss_sanity.py` — matched vs mismatched LD outlier count
- [ ] `tests/testthat-phase1/test_fit_roundtrip.R` — fit .rds roundtrip class check
- [ ] `tests/testthat-phase1/test_retry_ladder.R` — convergence retry ladder synthetic test
- [ ] `tests/testthat-phase1/test_coloc_susie_dispatch.R` — A6 dispatch test (fallback branch pre-spec'd)

Preflight verification commands (run before Wave 1 starts):

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --version   # expect 7.32.4
conda run -n r_coloc Rscript -e 'packageVersion("coloc"); packageVersion("susieR")'   # expect 5.2.3, 0.14.2
curl -I https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/chr1_1000001_4000001.npz   # bucket reachability
curl -I https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/hgdp1kgp_chr22.filtered.SNV_INDEL.phased.shapeit5.bcf   # HGDP+1kG reachability
```

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Complex-region monotonicity visual | REQ-2 #3 | Requires visual inspection of sensitivity table in HTML dashboard | Open `results/finemap/qc_dashboard.html` in browser; filter to 4 G3 complex regions (9p21_CDKN2A, APOE_19q13, HLA_6p21, SLC2A9_urate); confirm `n_CS` columns decrease left-to-right across `{0.1, 0.5, 0.9}` |
| EUR/AFR new LD panels in use | G4 (Option D hybrid) | Spot-check correctness of LD source, not auto-assertable | Pick one EUR region + one AFR region from JSON output; verify `ld_source` contains `ukbb_ld_tiled` for EUR and `hgdp_1kg` for AFR |
| kriging_rss outlier sanity | G5 D3 | Judgement call on "reasonable" threshold | Review kriging_rss outlier counts in dashboard for flagged regions; confirm neither universally zero nor universally massive |
| OSF amendment text | G6 (UKBB-LD substitution) | Requires scientific framing judgment | Review `methods_fragment.md` for clarity on UKBB-LD vs Pan-UKBB substitution and 4-of-6 G3 region scope; confirm it reads as a deliberate methodological choice, not a regression |

---

## Validation Sign-Off

- [ ] All tasks have automated verify command OR manual UAT rationale OR Wave 0 file-exists dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (every wave has at least one `--dry-run` or test gate)
- [ ] Wave 0 / Wave 1 covers all MISSING test infrastructure files (`tests/phase1/` + `tests/testthat-phase1/`)
- [ ] No watch-mode flags (Snakemake is batch, not watch)
- [ ] Feedback latency < 30s per task commit, < 15 min for phase gate (REQ-9)
- [ ] `nyquist_compliant: true` set in frontmatter after planner assigns real task IDs and plan-checker approves

**Approval:** pending
