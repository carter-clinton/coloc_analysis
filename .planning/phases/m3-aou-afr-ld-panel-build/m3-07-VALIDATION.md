---
phase: m3-07
slug: overlapping-deletion-span-filter-and-provenance
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-10
plan_split: [07a, 07b, 07c]
---

# Phase m3-07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `m3-07-RESEARCH.md` §Validation Architecture. Science settled in the byte-verified
> amendment doc-set; this contract covers the CODE (span-filter + manifest + scan + lockstep drop).
>
> **Plan split (checker iteration 1):** the phase is delivered as THREE plan files along the T1–T4
> boundaries — `m3-07a` (OSF gate + Wave 0 RED scaffold, `wave 1`, `depends_on: []`),
> `m3-07b` (T1 span-filter + T2 manifest, `wave 2`, `depends_on: ["07a"]`),
> `m3-07c` (T3 present-rate + T4 lockstep drop, `wave 3`, `depends_on: ["07b"]`).
> RED tests are authored in 07a; 07b/07c turn their own slices GREEN.

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
- **After every plan wave:** Run the plan's OWN suites (07a: RED-collect-clean; 07b: span_filter + manifest + driver-exclude; 07c: present_rate + lockstep). Do NOT gate 07b on the T3/T4 suites — they stay RED until 07c.
- **Before `/gsd-verify-work`:** Full suite green + `git diff --stat` empty on frozen files
- **Max feedback latency:** ~90 seconds

---

## Per-Task Verification Map

| Task ID | Plan (RED→GREEN) | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------------------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| Wave 0 RED scaffolds collect clean + fail-red | 07a | 1 | REQ-SNAKEMAKE-CI | Tampering (mis-encoded tests) | Function-local import → test failure not collection error | red-gate | see 07a Task 2 verify (RED_AS_EXPECTED, no collection error) | ❌ W0 | ⬜ pending |
| occlusion rule correct on region-1 topology | 07a→07b | 2 | REQ-AOU-LD-VALIDATION | Tampering (over-exclusion) | Deterministic rule pins exact excluded set | unit | `pytest tests/m3/test_occlusion_span_filter.py -x` | ❌ W0 | ⬜ pending |
| `--exclude` reaches plink argv; `--keep-allele-order` preserved | 07a→07b | 2 | REQ-AOU-LD-VALIDATION | Tampering | Exclude before `--r`; NaN-raise never trips | unit | `pytest tests/m3/test_run_native_ld_panel.py -k exclude -x` | ⚠ extend | ⬜ pending |
| excluded window → `.npz` has NO NaN (frozen `read_square_bin` passes) | 07a→07b | 2 | REQ-AOU-LD-VALIDATION | Tampering (NaN reaches fine-mapper) | Occluded record removed upstream of `--r` | integration | `pytest tests/m3/test_run_native_ld_panel.py -k occlusion -x` | ❌ W0 | ⬜ pending |
| manifest Stage-A columns + ref_span + reason; resume-safe dedup | 07a→07b | 2 | REQ-AOU-LD-VALIDATION, REQ-AOU-LD-EGRESS | Info disclosure | Coordinate/id-only, egress-clean | unit | `pytest tests/m3/test_occlusion_manifest.py -x` | ❌ W0 | ⬜ pending |
| b37 liftover matches hinge-check values | 07a→07b | 2 | REQ-AOU-LD-VALIDATION | — | Reuse `ld_npz_to_rds.R` chain + SHA-256 | unit (skip if no chain) | `pytest tests/m3/test_occlusion_manifest.py -k liftover -x` | ❌ W0 | ⬜ pending |
| present-rate k/n on synthetic sumstats | 07a→07c | 3 | REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY | Info disclosure | Runs on public GRCh37 sumstats only | unit | `pytest tests/m3/test_occlusion_present_rate_scan.py -x` | ❌ W0 | ⬜ pending |
| lockstep drop = exactly manifest `(CHR,POS)`; idempotent | 07a→07c | 3 | REQ-AOU-LD-VALIDATION | Tampering (panel↔sumstats desync) | Drop-only, no re-key | unit | `pytest tests/m3/test_occlusion_lockstep_drop.py -x` | ❌ W0 | ⬜ pending |
| frozen contracts byte-unchanged | 07b, 07c | all | REQ-SNAKEMAKE-CI | Tampering | `read_square_bin`/`content_verify_npz`/`ld_npz_to_rds.R` untouched | regression | `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` empty | ✅ existing | ⬜ pending |
| 276-region filter sanity (Nyquist sampling) | 07b | gated | REQ-AOU-LD-VALIDATION | Tampering | Occlusion catalog across all regions | integration/validation | scan all AFR manifest windows for occlusion counts → catalog | ❌ W0 (real run gated) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements (authored in 07a)

- [ ] `tests/m3/test_occlusion_span_filter.py` — occlusion rule (region-1 topology fixture)
- [ ] `tests/m3/test_occlusion_manifest.py` — manifest schema + both-build liftover
- [ ] `tests/m3/test_occlusion_present_rate_scan.py` — present-rate per ancestry
- [ ] `tests/m3/test_occlusion_lockstep_drop.py` — T4 reusable filter
- [ ] extend `tests/m3/test_run_native_ld_panel.py` — `--exclude` argv + integration + `n_dropped_occluded`
- [ ] synthetic region-1 `.bim` fixture helper (`_REGION1_BIM_ROWS`; reproduces a `ref_span_overlap` occlusion)
- [ ] RED semantics: 4 new suites import impl modules INSIDE test bodies so they collect clean and fail as test/assert failures (not collection errors)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Genome-wide 276-region filter correctness against the REAL in-perimeter `.bim` | REQ-AOU-LD-VALIDATION | Requires in-perimeter AoU data + a gated region-1 re-run (out of scope this phase; loop stays untouched) | At the gated re-run: run the span-filter over all 276 region `.bim`s, confirm region-1 NaN cleared and the occlusion catalog is produced; unit-covered on the region-1 fixture now |
| OSF amendment-update posted + recorded (07a Task 1) | REQ-OSF-PREREG | Human action on osf.io; integrity gate, not code | Post the scoped panel overlapping-variant policy amendment-update (exclusion + provenance, never zeroing); record file id/SHA-256/git tag before any fix code lands |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (authored in 07a)
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter (all three plans reference these tests)

**Approval:** approved 2026-07-10 (planner; plan set 07a/07b/07c validated — structure + frontmatter clean)
