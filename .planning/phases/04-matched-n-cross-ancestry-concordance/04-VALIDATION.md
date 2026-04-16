---
phase: 4
slug: matched-n-cross-ancestry-concordance
status: active
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-15
updated: 2026-04-16
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (Python) + testthat (R, via subprocess) |
| **Config file** | tests/conftest.py (phase4 marker registered) |
| **Quick run command** | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_*.py -x -q` |
| **Full suite command** | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_*.py -q && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --dry-run -s Snakefile all_matched_n` |
| **Estimated runtime** | ~4 seconds (unit); ~15 seconds (dry-run integration) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_matched_n_*.py -x -q`
- **After every plan wave:** Run `pytest tests/test_matched_n_*.py -q && snakemake --dry-run -s Snakefile all_matched_n`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 4 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Test Type | Automated Command | Status |
|---------|------|------|-----------|-------------------|--------|
| 4-01-01 | 01 | 1 | unit | `python -c "import yaml,jsonschema; c=yaml.safe_load(open('config/matched_n.yaml')); s=yaml.safe_load(open('schemas/matched_n.schema.yaml')); jsonschema.validate(c,s); print('OK')"` | ✅ green |
| 4-01-02 | 01 | 1 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list -s Snakefile \| grep build_matched_n_manifest` | ✅ green |
| 4-01-03 | 01 | 1 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_*.py --collect-only -q` | ✅ green |
| 4-02-01 | 02 | 2 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_se_inflation.py -x -q` | ✅ green |
| 4-02-02 | 02 | 2 | unit+mock | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_bootstrap_driver.py -x -q` | ✅ green |
| 4-02-03 | 02 | 2 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --dry-run -s Snakefile results/matched_n/coloc/t2d/TCF7L2_10q25_2/bootstrap_1/coloc_summary.tsv 2>&1 \| tail -5` | ✅ green |
| 4-03-01 | 03 | 3 | unit+fixture | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_tier_a.py -x -q` | ✅ green |
| 4-03-02 | 03 | 3 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --dry-run -s Snakefile results/matched_n/tier_a_retention.tsv results/matched_n/jaccard.tsv 2>&1 \| tail -5` | ✅ green |
| 4-04-01 | 04 | 2 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list -s Snakefile \| grep ldsc_rg` | ✅ green |
| 4-04-02 | 04 | 2 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_fdr.py -x -q` | ✅ green |
| 4-04-03 | 04 | 2 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_fdr.py::test_rg_matrix_schema -x -q` | ✅ green |
| 4-04-04 | 04 | 2 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_detection.py -x -q` | ✅ green |
| 4-05-01 | 05 | 4 | manual+pilot | `test -f results/matched_n/SMOKE_PILOT_REPORT.md` + human-verify | ✅ approved |
| 4-05-02 | 05 | 4 | unit | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_table2.py tests/test_matched_n_h7.py -x -q` | ✅ green (13 passed) |
| 4-05-03 | 05 | 4 | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list -s Snakefile \| grep plot_violin` | ✅ green |
| 4-05-04 | 05 | 4 | integration | `PYTHONPATH=. /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/test_matched_n_negcontrol.py -x -q` | ✅ green (skips cleanly) |

*Status: ⬜ pending / ✅ green / ❌ red / ⚠ flaky*

Sampling rate: per-task commit = pytest `-x -q` on that task's test; per-wave = full `tests/test_matched_n_*.py`; phase-gate = full suite + snakemake `--dry-run all_matched_n`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Smoke pilot timing + convergence review | A-1 compute envelope | Requires human judgment on acceptable wall-clock and LSF topology | Review 04-PILOT.md, approve or adjust |
| Full LSF production launch | A-1 gate | Requires compute allocation approval | `snakemake --profile config/cluster_lsf --use-conda all_matched_n` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 4s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-04-16 (all 17 verification map entries populated)
