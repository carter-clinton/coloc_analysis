---
phase: 05
slug: pathway-partitioned-heritability
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-13
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (in smoke_dev) + Rscript (in la_multitrait_r) |
| **Config file** | tests/phase2/conftest.py (existing -- extend for Phase 5) |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -x -q` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -v` |
| **Estimated runtime** | ~30 seconds (unit/smoke); integration deferred to real data |

---

## Sampling Rate

- **After every task commit:** Run `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -x -q --tb=short`
- **After every plan wave:** Run `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green + Snakemake dry-run of pathway.smk
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | REQ-7 | T-05-01 | Validate sumstats columns before MAGMA input | unit | `pytest tests/phase5/test_magma_geneset.py::test_neg_ctrl_sets_included -x` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | SC-1 | — | MAGMA gene-based + gene-set enrichment completed | smoke | `pytest tests/phase5/test_magma_geneset.py -x` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | REQ-7 | T-05-02 | g:Profiler API over HTTPS; schema validation | unit | `pytest tests/phase5/test_gprofiler.py::test_neg_ctrl_enrichment_null -x` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 1 | SC-2 | — | g:Profiler with discoverability-matched background | smoke | `pytest tests/phase5/test_gprofiler.py -x` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | SC-3 | T-05-03 | Validate annotation format before LDSC | unit | `pytest tests/phase5/test_ldsc_partitioned.py::test_neg_ctrl_annotation -x` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | SC-4 | — | LDSC-SEG tissue-specific h2 | smoke | `pytest tests/phase5/test_ldsc_seg.py -x` | ❌ W0 | ⬜ pending |
| 05-04-01 | 04 | 3 | REQ-7 | — | All neg controls q > 0.05 | integration | `pytest tests/phase5/test_negative_controls.py -x` | ❌ W0 | ⬜ pending |
| 05-04-02 | 04 | 3 | SC-5/SC-6 | — | Permutation null computed | smoke | `pytest tests/phase5/test_permutation_null.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase5/` directory — does not exist yet
- [ ] `tests/phase5/conftest.py` — shared fixtures (mock sumstats, mock gene sets, mock MAGMA output)
- [ ] `tests/phase5/test_magma_geneset.py` — MAGMA gene-set file format validation
- [ ] `tests/phase5/test_ldsc_partitioned.py` — LDSC annotation format + munging validation
- [ ] `tests/phase5/test_gprofiler.py` — background construction + API call mock
- [ ] `tests/phase5/test_ldsc_seg.py` — tissue annotation path validation
- [ ] `tests/phase5/test_negative_controls.py` — negative control pipeline integration
- [ ] `tests/phase5/test_permutation_null.py` — permutation gene set generation
- [ ] `envs/magma.yml` — conda env for MAGMA helper scripts
- [ ] `envs/ldsc_py3.yml` — conda env for abdenlab/ldsc-python3
- [ ] `envs/hess_py27.yml` — conda env for HESS (Python 2.7)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MAGMA binary download from CNCR | SC-1 | URL may 301/404; needs manual browser check | Visit ctg.cncr.nl/software/magma, verify v1.10 Linux binary URL |
| HESS LD reference panel genome build | SC-3 | Need to inspect downloaded panel header | Download panel, check SNP positions against GRCh37 reference |
| g:Profiler API availability | SC-2 | External service dependency | `curl -s https://biit.cs.ut.ee/gprofiler/api/util/version` returns 200 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (Plan 01 Task 3 creates all test files)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-04-13 — Wave 0 items created by Plan 01 Task 3. wave_0_complete set to true after Plan 01 execution.
