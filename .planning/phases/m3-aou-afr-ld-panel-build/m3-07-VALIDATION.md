---
phase: m3-07
slug: overlapping-deletion-span-filter-and-provenance
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-10
---

# Phase m3-07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `m3-07-RESEARCH.md` §Validation Architecture. Science settled in the byte-verified
> amendment doc-set; this contract covers the CODE (span-filter + manifest + scan + lockstep drop).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (py3.11 `smoke_dev`) + base-R `stopifnot` for any R-side (mirrors `tests/testthat-phase1`) |
| **Config file** | none dedicated; `tests/m3/conftest.py` + root `tests/conftest.py` |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/<task-test>.py -x -q` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q` |
| **Estimated runtime** | ~30–90 seconds (unit) |

---

## Sampling Rate

- **After every task commit:** Run the task's targeted `pytest tests/m3/<task-test>.py -x -q`
- **After every plan wave:** Run `pytest tests/m3 -q` (full suite green, no frozen-module regressions)
- **Before `/gsd-verify-work`:** Full suite green + `git diff --stat` empty on frozen files
- **Max feedback latency:** ~90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| occlusion rule correct on region-1 topology | 07 | 1 | REQ-AOU-LD-VALIDATION | Tampering (over-exclusion) | Deterministic rule pins exact excluded set | unit | `pytest tests/m3/test_occlusion_span_filter.py -x` | ❌ W0 | ⬜ pending |
| `--exclude` reaches plink argv; `--keep-allele-order` preserved | 07 | 1 | REQ-AOU-LD-VALIDATION | Tampering | Exclude before `--r`; NaN-raise never trips | unit | `pytest tests/m3/test_run_native_ld_panel.py -k exclude -x` | ⚠ extend | ⬜ pending |
| excluded window → `.npz` has NO NaN (frozen `read_square_bin` passes) | 07 | 1 | REQ-AOU-LD-VALIDATION | Tampering (NaN reaches fine-mapper) | Occluded record removed upstream of `--r` | integration | `pytest tests/m3/test_run_native_ld_panel.py -k occlusion -x` | ❌ W0 | ⬜ pending |
| manifest Stage-A columns + ref_span + reason; resume-safe dedup | 07 | 1 | REQ-AOU-LD-VALIDATION, REQ-AOU-LD-EGRESS | Info disclosure | Coordinate/id-only, egress-clean | unit | `pytest tests/m3/test_occlusion_manifest.py -x` | ❌ W0 | ⬜ pending |
| b37 liftover matches hinge-check values | 07 | 1 | REQ-AOU-LD-VALIDATION | — | Reuse `ld_npz_to_rds.R` chain + SHA-256 | unit (skip if no chain) | `pytest tests/m3/test_occlusion_manifest.py -k liftover -x` | ❌ W0 | ⬜ pending |
| present-rate k/n on synthetic sumstats | 07 | 2 | REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY | Info disclosure | Runs on public GRCh37 sumstats only | unit | `pytest tests/m3/test_occlusion_present_rate_scan.py -x` | ❌ W0 | ⬜ pending |
| lockstep drop = exactly manifest `(CHR,POS)`; idempotent | 07 | 2 | REQ-AOU-LD-VALIDATION | Tampering (panel↔sumstats desync) | Drop-only, no re-key | unit | `pytest tests/m3/test_occlusion_lockstep_drop.py -x` | ❌ W0 | ⬜ pending |
| frozen contracts byte-unchanged | 07 | all | REQ-SNAKEMAKE-CI | Tampering | `read_square_bin`/`content_verify_npz`/`ld_npz_to_rds.R` untouched | regression | `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` empty | ✅ existing | ⬜ pending |
| 276-region filter sanity (Nyquist sampling) | 07 | gated | REQ-AOU-LD-VALIDATION | Tampering | Occlusion catalog across all regions | integration/validation | scan all AFR manifest windows for occlusion counts → catalog | ❌ W0 (real run gated) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/m3/test_occlusion_span_filter.py` — occlusion rule (region-1 topology fixture)
- [ ] `tests/m3/test_occlusion_manifest.py` — manifest schema + both-build liftover
- [ ] `tests/m3/test_occlusion_present_rate_scan.py` — present-rate per ancestry
- [ ] `tests/m3/test_occlusion_lockstep_drop.py` — T4 reusable filter
- [ ] extend `tests/m3/test_run_native_ld_panel.py` — `--exclude` argv + integration + `n_dropped_occluded`
- [ ] synthetic region-1 `.bim` fixture helper (coordinate-space; reproduces a `ref_span_overlap` occlusion)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Genome-wide 276-region filter correctness against the REAL in-perimeter `.bim` | REQ-AOU-LD-VALIDATION | Requires in-perimeter AoU data + a gated region-1 re-run (out of scope this phase; loop stays untouched) | At the gated re-run: run the span-filter over all 276 region `.bim`s, confirm region-1 NaN cleared and the occlusion catalog is produced; unit-covered on the region-1 fixture now |
| OSF amendment-update posted + recorded | REQ-OSF-PREREG | Human action on osf.io; integrity gate, not code | Post the scoped panel overlapping-variant policy amendment-update (exclusion + provenance, never zeroing); record hash/tag before any fix code lands |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter (set by planner once tasks reference these tests)

**Approval:** pending
