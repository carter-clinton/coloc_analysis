---
phase: 4
slug: matched-n-cross-ancestry-concordance
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-15
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python) + testthat (R, via subprocess) |
| **Config file** | tests/conftest.py (phase4 marker registered) |
| **Quick run command** | `pytest tests/test_matched_n_*.py -x -q` |
| **Full suite command** | `pytest tests/test_matched_n_*.py -q && snakemake --dry-run -s Snakefile all_matched_n` |
| **Estimated runtime** | ~4 seconds (unit); ~15 seconds (dry-run integration) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_matched_n_*.py -x -q`
- **After every plan wave:** Run `pytest tests/test_matched_n_*.py -q && snakemake --dry-run -s Snakefile all_matched_n`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 4 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | unit | `python -c "import yaml,jsonschema; c=yaml.safe_load(open('config/matched_n.yaml')); s=yaml.safe_load(open('schemas/matched_n.schema.yaml')); jsonschema.validate(c,s); print('OK')"` | ✅ | ⬜ pending |
| 4-01-02 | 01 | 1 | integration | `snakemake --list -s Snakefile \| grep build_matched_n_manifest` | ✅ | ⬜ pending |
| 4-01-03 | 01 | 1 | unit | `pytest tests/test_matched_n_*.py --collect-only -q` | ✅ Wave-0 stubs | ⬜ pending |
| 4-02-01 | 02 | 2 | unit | `pytest tests/test_matched_n_se_inflation.py -x -q` | ✅ | ⬜ pending |
| 4-02-02 | 02 | 2 | unit+mock | `pytest tests/test_matched_n_bootstrap_driver.py -x -q` | ✅ | ⬜ pending |
| 4-02-03 | 02 | 2 | integration | `snakemake --dry-run -s Snakefile results/matched_n/coloc/t2d/chr10_114p/bootstrap_1/coloc_summary.tsv` | ✅ | ⬜ pending |
| 4-03-01 | 03 | 3 | unit+fixture | `pytest tests/test_matched_n_tier_a.py -x -q` | ✅ | ⬜ pending |
| 4-03-02 | 03 | 3 | integration | `snakemake --dry-run -s Snakefile results/matched_n/tier_a_retention.tsv results/matched_n/jaccard.tsv` | ✅ | ⬜ pending |
| 4-04-01 | 04 | 2 | integration | `snakemake --list -s Snakefile \| grep ldsc_rg` | ✅ | ⬜ pending |
| 4-04-02 | 04 | 2 | unit | `pytest tests/test_matched_n_fdr.py -x -q` | ✅ | ⬜ pending |
| 4-04-03 | 04 | 2 | unit | `pytest tests/test_matched_n_fdr.py::test_rg_matrix_schema -x -q` | ✅ | ⬜ pending |
| 4-04-04 | 04 | 2 | unit | `pytest tests/test_matched_n_detection.py -x -q` | ✅ | ⬜ pending |
| 4-05-01 | 05 | 4 | manual+pilot | `test -f results/matched_n/SMOKE_PILOT_REPORT.md` + human-verify | ⚠ checkpoint | ⬜ pending |
| 4-05-02 | 05 | 4 | unit | `pytest tests/test_matched_n_table2.py tests/test_matched_n_h7.py -x -q` | ✅ | ⬜ pending |
| 4-05-03 | 05 | 4 | integration | `snakemake --dry-run -s Snakefile results/matched_n/supp_violin.pdf` | ✅ | ⬜ pending |
| 4-05-04 | 05 | 4 | integration | `pytest tests/test_matched_n_negcontrol.py -x -q` | ✅ post-launch | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Sampling rate: per-task commit = pytest `-x -q` on that task's test; per-wave = full `tests/test_matched_n_*.py`; phase-gate = full suite + snakemake `--dry-run all_matched_n`.

---

## Wave 0 Requirements

- [ ] `tests/test_matched_n_se_inflation.py` — stubs for D-01a SE inflation
- [ ] `tests/test_matched_n_tier_a.py` — stubs for D-02a Tier A retention
- [ ] `tests/test_matched_n_h7.py` — stubs for D-02d H7 20pp verdict
- [ ] `tests/test_matched_n_detection.py` — stubs for D-05a NCP detection probability
- [ ] `tests/test_matched_n_fdr.py` — stubs for D-04c BH-FDR
- [ ] `tests/test_matched_n_negcontrol.py` — stubs for HLA/pigmentation negative control
- [ ] `tests/test_matched_n_table2.py` — stubs for D-06a Table 2 schema
- [ ] `tests/conftest.py` — phase4 marker registered
- [ ] `tests/fixtures/matched_n/README.md` — synthetic fixture plan

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Smoke pilot timing + convergence review | A-1 compute envelope | Requires human judgment on acceptable wall-clock and LSF topology | Review 04-PILOT.md, approve or adjust |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 4s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
