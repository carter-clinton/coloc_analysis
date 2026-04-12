---
phase: 02
slug: 3-way-qtl-colocalization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python) + testthat 3.x (R) |
| **Config file** | `tests/phase2/conftest.py` (Wave 0 installs) |
| **Quick run command** | `pytest tests/phase2/ -x --tb=short` |
| **Full suite command** | `pytest tests/ -x --tb=short` |
| **Estimated runtime** | ~30 seconds (unit), ~120 seconds (integration with toy_3locus) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/phase2/ -x --tb=short`
- **After every plan wave:** Run `pytest tests/ -x --tb=short`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | — | — | N/A | unit | `pytest tests/phase2/test_liftover.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | — | — | N/A | unit | `pytest tests/phase2/test_config_validation.py -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | — | — | N/A | unit | `pytest tests/phase2/test_harmonize_eqtl.py -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | — | — | N/A | unit | `pytest tests/phase2/test_run_qtl_coloc.py -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 2 | — | — | N/A | R unit | `Rscript tests/testthat-phase2/test_qtl_coloc_dispatch.R` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | — | — | N/A | unit | `pytest tests/phase2/test_harmonize_sqtl.py -x` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 3 | — | — | N/A | unit | `pytest tests/phase2/test_harmonize_pqtl.py -x` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 3 | — | — | N/A | unit | `pytest tests/phase2/test_onek1k_harmonize.py -x` | ❌ W0 | ⬜ pending |
| 02-05-01 | 05 | 4 | REQ-3 | — | N/A | unit | `pytest tests/phase2/test_pph4_sweep.py -x` | ❌ W0 | ⬜ pending |
| 02-05-02 | 05 | 4 | REQ-7 | — | N/A | unit | `pytest tests/phase2/test_negative_controls.py -x` | ❌ W0 | ⬜ pending |
| 02-05-03 | 05 | 4 | — | — | N/A | unit | `pytest tests/phase2/test_tier_assignment.py -x` | ❌ W0 | ⬜ pending |
| 02-05-04 | 05 | 4 | — | — | N/A | integration | `snakemake --configfile tests/toy_3locus/config_test.yaml -n` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase2/__init__.py` — package marker
- [ ] `tests/phase2/conftest.py` — shared fixtures (qtl_fixtures_dir, regions_grch38, variant_id_map, pph4_thresholds)
- [ ] `tests/phase2/test_liftover.py` — GRCh37->GRCh38 coordinate validation
- [ ] `tests/phase2/test_config_validation.py` — pph4_thresholds.yaml, negative_controls.yaml, qtl_sources.yaml loading
- [ ] `tests/toy_3locus/data/qtl/` — synthetic QTL fixture data (eQTL, sQTL, pQTL, sc-eQTL mock files)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| eQTL Catalogue FTP download works | — | Requires network + real FTP server | `wget -q --spider ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/` |
| Synapse auth for UKB-PPP download | — | Requires Synapse credentials | `synapse login --token $SYNAPSE_TOKEN` |
| QC dashboard visual review | — | HTML rendering requires browser | Open `results/qtl_coloc/qc_dashboard.html` in browser |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
