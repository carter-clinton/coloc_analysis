---
phase: 9
slug: replication-in-independent-cohorts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-14
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from 09-RESEARCH.md "Validation Architecture" section (Layers 1/2/3).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (Python; reuses `tests/phase5/` pattern) + testthat 3.x (R; for FIQT + coloc.susie runners) |
| **Config file** | `pyproject.toml` (pytest settings) + `tests/phase9/conftest.py` (Wave 0 fixtures) |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase9 -x -q --tb=short` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase9 -v --tb=short && Rscript -e 'testthat::test_dir("tests/phase9/r")'` |
| **Estimated runtime** | ~60 seconds (Python unit tests); ~90 seconds with testthat suite |

---

## Sampling Rate

- **After every task commit:** Run `{quick run command}` (pytest only — skip testthat for speed)
- **After every plan wave:** Run `{full suite command}` (pytest + testthat)
- **Before `/gsd-verify-work`:** Full suite must be green AND Snakemake `all_replication` dry-run passes
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

> Populated by the planner as Plans are created. Every task needs one row mapping task → test command → file existence.
> Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | — | — | N/A | unit | `pytest tests/phase9/test_cohort_ingest.py -k test_finngen_url_format` | ❌ W0 | ⬜ pending |
| 09-01-02 | 01 | 1 | — | — | N/A | unit | `pytest tests/phase9/test_cohort_ingest.py -k test_mvp_phs_enumeration` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 2 | — | T-09-04 | Validates trait→endpoint mapping; reject unknown endpoint | unit | `pytest tests/phase9/test_trait_harmonization.py` | ❌ W0 | ⬜ pending |
| 09-03-01 | 03 | 3 | — | T-09-05 | FIQT shrinkage monotonicity (z=0 → 0; z→∞ → β_raw) | unit | `Rscript -e 'testthat::test_file("tests/phase9/r/test_fiqt.R")'` | ❌ W0 | ⬜ pending |
| 09-03-02 | 03 | 3 | — | — | Coloc re-estimation on toy TCF7L2/T2D locus → PP.H4 > 0.8 | integration | `Rscript -e 'testthat::test_file("tests/phase9/r/test_coloc_replication.R")'` | ❌ W0 | ⬜ pending |
| 09-04-01 | 04 | 4 | — | — | IVW meta-analysis: same-direction 2-cohort combine | unit | `pytest tests/phase9/test_meta_ivw.py` | ❌ W0 | ⬜ pending |
| 09-04-02 | 04 | 4 | — | T-09-07 | COJO sensitivity: complex locus independent signal detection | unit (mock) | `pytest tests/phase9/test_cojo_sensitivity.py` | ❌ W0 | ⬜ pending |
| 09-05-01 | 05 | 5 | — | — | Master table schema has all 4 effect-size columns | unit | `pytest tests/phase9/test_master_table_schema.py` | ❌ W0 | ⬜ pending |
| 09-05-02 | 05 | 5 | — | — | HLA negative control fails replication (PP.H4 < 0.5) | scientific | `pytest tests/phase9/test_negative_controls.py -k test_hla_fails` | ❌ W0 | ⬜ pending |

*Planner will populate additional rows per-plan as tasks are defined. Above is the minimum skeleton.*

---

## Wave 0 Requirements

Planner creates these during Wave 1 (test scaffolding) before any analytical rules:

- [ ] `tests/phase9/__init__.py`
- [ ] `tests/phase9/conftest.py` — shared fixtures (mock sumstats for 4 cohorts, mock SuSiE fits, mock coloc results)
- [ ] `tests/phase9/test_cohort_ingest.py` — URL format validation, file presence checks
- [ ] `tests/phase9/test_trait_harmonization.py` — trait → endpoint/accession mapping
- [ ] `tests/phase9/test_meta_ivw.py` — IVW meta-analysis correctness
- [ ] `tests/phase9/test_cojo_sensitivity.py` — COJO wrapper invocation (mock GCTA)
- [ ] `tests/phase9/test_master_table_schema.py` — output table column/dtype validation
- [ ] `tests/phase9/test_negative_controls.py` — HLA + cosmetic negative controls (reused from Phase 2/5)
- [ ] `tests/phase9/r/test_fiqt.R` — FIQT shrinkage unit tests (testthat)
- [ ] `tests/phase9/r/test_coloc_replication.R` — coloc.susie replication integration test (TCF7L2/T2D)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| FinnGen R12 data download completes without HTTP 403/404 | — | Requires live GCP bucket access (not reproducible in CI without creds) | On HPC: run `gsutil ls gs://finngen-public-data-r12/summary_stats/finngen_R12_T2D.gz`; if HTTP 200, proceed; if 403/404, re-register at elomake.helsinki.fi |
| MVP dbGaP phs001672 FTP enumeration yields all 5 trait sub-accessions | — | dbGaP directory listing; one-time manual verification | Browse `ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/` and confirm pha IDs for BMI, T2D, HTN, stroke, asthma. Record in `config/cohort_mappings.yaml` |
| Replication master table spot-check: TCF7L2/T2D replicates at PP.H4 > 0.8 in every EUR replication cohort | — | Scientific sanity check, positive control for pipeline correctness | After Plan 05 completes, grep master_table.tsv for TCF7L2 rows; confirm PP.H4 ≥ 0.8 in FinnGen, GBMI-EUR, MVP-EUR. If fails, pipeline has a bug; if passes, ship. |
| HLA region signal fails replication (negative control) | — | Scientific sanity check, negative control | Grep master_table.tsv for HLA-region signals (chr6:28-33Mb); confirm PP.H4 < 0.5 or failed Bonferroni in ≥ 3/4 cohorts. If passes unexpectedly, investigate LD artifact. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-14 by gsd-plan-checker (iteration 2 — 2 BLOCKING + 5 IMPORTANT + 3 MINOR issues addressed in revision commit)
