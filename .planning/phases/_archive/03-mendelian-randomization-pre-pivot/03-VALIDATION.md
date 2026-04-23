---
phase: 03
slug: mendelian-randomization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python) + testthat (R) |
| **Config file** | tests/conftest.py (root), tests/phase3/ (phase-specific) |
| **Quick run command** | `pytest tests/phase3/ -x -q --tb=short` |
| **Full suite command** | `pytest tests/ -x -q --tb=short -m "not slow"` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/phase3/ -x -q --tb=short`
- **After every plan wave:** Run `pytest tests/ -x -q --tb=short -m "not slow"`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *Populated by planner* | | | REQ-4 | — | N/A | unit | `pytest tests/phase3/` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase3/` — directory + conftest with phase3 marker
- [ ] `tests/phase3/test_mr_instruments.py` — stubs for instrument extraction
- [ ] `tests/phase3/test_mr_methods.py` — stubs for MR method invocations
- [ ] `tests/phase3/test_mr_diagnostics.py` — stubs for F-stat, Steiger, pleiotropy tests

*Existing infrastructure: root conftest.py with phase markers (created in Phase 4).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MR results biologically coherent | REQ-4 | Causal direction interpretation requires domain knowledge | Review bidirectional graph: BMI→T2D positive, T2D→BMI null expected |
| Real-data MR execution on LSF | REQ-4 | Requires actual GWAS sumstats + SuSiE fits | `snakemake --profile config/cluster_lsf all_mr` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
