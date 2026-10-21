---
phase: ta-r4
slug: ta-r4-head-to-head-reanalysis-and-submission
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-21
---

# Phase ta-r4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `ta-r4-RESEARCH.md` §Validation Architecture. Planner maps tasks into the table below.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (smoke_dev Python 3.11) driving R via `Rscript` (r_coloc env); testthat for pure-R units |
| **Config file** | existing `tests/conftest.py`; new `tests/ta_r4/conftest.py` (W0) |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -x -q` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q` |
| **Estimated runtime** | quick < 120 s; full ≈ 15–20 min (`tests/m3` ≈ 15 min) |

---

## Sampling Rate

- **After every task commit:** quick run + the specific `tests/m3` files the task touches
- **After every plan wave:** full suite; ids/passed/skipped/failed recorded against the W0 baseline in `ta-r4-LOG.md`
- **Before `/gsd-verify-work`:** full suite green, all live gates green, every negative control observed RED once
- **Max feedback latency:** 120 seconds (quick run)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| W0c-T1 | W0c | 3 | D-13 no silent identity | — | N/A | unit + live gate | `pytest tests/ta_r4/test_no_silent_identity.py` | ❌ W0 | ⬜ pending |
| W0c-T2 | W0c | 3 | D-01 matched variant sets | — | N/A | live gate | `pytest tests/ta_r4/test_arm_variant_sets_identical.py` | ❌ W0 | ⬜ pending |
| W0d-T1 | W0d | 4 | D-02 fallback labelled | — | N/A | unit | `pytest tests/ta_r4/test_fallback_labelled.py` | ❌ W0 | ⬜ pending |
| W0d-T1 | W0d | 4 | priors constant | — | N/A | live gate | `pytest tests/ta_r4/test_priors_constant.py` | ❌ W0 | ⬜ pending |
| W0b-T3 | W0b | 2 | D-04/D-15 Track B isolation | — | N/A | dry-run | `pytest tests/ta_r4/test_track_b_isolation.py` | ❌ W0 | ⬜ pending |
| W0b-T3 | W0b | 2 | D-05/D-27 OSF sentinel gate | — | production refuses without sentinel | dry-run | `pytest tests/ta_r4/test_osf_gate.py` | ❌ W0 | ⬜ pending |
| W0a-T1 | W0a | 1 | D-11 storage on /rs1 | — | N/A | unit | `pytest tests/ta_r4/test_storage_on_rs1.py` | ❌ W0 | ⬜ pending |
| W1-T1 | W1 | 5 | D-18 BMI allele restoration | — | N/A | unit | `pytest tests/ta_r4/test_bmi_allele_restoration.py` | ❌ W1 | ⬜ pending |
| W1-T2 | W1 | 5 | D-06 panel REF/ALT emit | — | N/A | unit (R) | `pytest tests/ta_r4/test_plink_ld_to_rds_ref_alt.py` | ❌ W1 | ⬜ pending |
| W1-T3 | W1 | 5 | D-06 QTL orientation | — | N/A | unit (R) | `pytest tests/ta_r4/test_qtl_orient.py` | ❌ W1 | ⬜ pending |
| W2a-T3 | W2a | 6 | D-12a panel known answers | — | N/A | live gate | `pytest tests/ta_r4/test_known_answer_panels.py` | ❌ W2a | ⬜ pending |
| W3a-T3 / W3b-T2 | W3a/W3b | 9/10 | D-12b/D-17 reproduction | — | N/A | live gate | `pytest tests/ta_r4/test_known_answer_repro.py` | ❌ W3a/W3b | ⬜ pending |
| W2b-T2 | W2b | 7 | UKB tile triangle/diag | — | N/A | live gate | `pytest tests/ta_r4/test_ukb_tile_triangle.py` | ❌ W2b | ⬜ pending |
| §C (every plan) | all | 1-22 | Track B unchanged | — | N/A | suite | full `tests/m3` (+ `test_source_freeze_pins`) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/ta_r4/conftest.py` — overlay-merge helper (`snakemake.utils.update_config`), fixture panels and sumstats
- [ ] every `❌ W0` test above, committed RED first with its negative control observed failing
- [ ] re-measured `tests/m3` baseline recorded in `ta-r4-LOG.md`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OSF R4 amendment posted before production | D-05/D-27 | external posting by Carter | Carter posts on osf.io/az52u, records URL+timestamp in `.planning/osf_deviations.md`, commits the sentinel |
| Panel manifest plausibility | D-12a/D-25 | judgement on n_samples / dims / build | Carter reviews W1 panel manifest at checkpoint:human-verify |
| Known-answer findings report | D-12/D-17 | mismatches are findings, not failures | Carter reviews W3 report at checkpoint:human-verify |
| Manuscript scientific accuracy | D-08 | prose claims vs results | brief-blind adversarial review + Carter read |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
