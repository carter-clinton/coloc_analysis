---
phase: m3-aou-afr-ld-panel-build
plan: 02
wave: 2
subsystem: aou-ld-panel-dev-fire-and-validation-harness
status: partial_paused_at_human_gate
nyquist_compliant: true
tags: [m3, aou, ld-panel, wave-2, validation-harness, dev-fire, design-delta, human-gate]
requires:
  - m3-00-W0-foundations-SUMMARY.md  # aou_ld_panel.compute_region_ld(), ld_panel.resolve_ld_path, config/ld_regions_dev.tsv, tests/m3/conftest.py
  - m3-01-W1-aou-cohort-and-hard-gates-SUMMARY.md  # 3 cohort MTs in workspace bucket; AOU-1 template
  - m3-03-W3-ncsu-ingest-and-resolver-SUMMARY.md  # bootstrap .npz→.rds converter used by AOU-4 (W3 wave-promoted early)
  - 51f9ce2 + 0abff84 (260520-s2s) W2 design-delta code commits (idempotent resume + MAF_THRESHOLD_EXPORT)
  - 595d1f3 m3-02-W2-DESIGN-DELTA.md sibling
provides:
  - .planning/notebooks/AOU-2_per_region_ld.ipynb (12 cells; dev fire + Wave 4 production-fire template)
  - .planning/notebooks/AOU-4_validation.ipynb (13 cells; 4-check + sensitivity + signed-r contract)
  - tests/m3/test_validation_check_1_known_locus.py (4 tests, all pass)
  - tests/m3/test_validation_check_2_aou_eur_vs_1kg.py (4 tests, all pass)
  - tests/m3/test_validation_check_3_susie_convergence.py (4 tests, all pass including signed-r regression)
  - tests/m3/test_validation_check_4_identity_ab.py (6 tests, all pass)
  - tests/m3/test_aou_export_landing.py (5 tests, all pass)
  - data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/.touch_dev10 (egress landing dir markers)
  - 4 .gitkeep files at .planning/phases/m3-aou-afr-ld-panel-build/validation/check_{1,2,3,4}*/
affects:
  - m3-04-W4-production-and-egress-PLAN.md (gated on m3_dev_complete.flag — NOT YET TOUCHED; Carter human gate)
  - .planning/STATE.md (Wave 2 position partial; Task 3 awaiting Carter)
  - .planning/ROADMAP.md (Plan 02 status remains in-progress until Carter signoff)
tech-stack-added:
  - Jupyter (Python kernel) for AOU-2 (Hail driver + region loop)
  - Jupyter (R kernel via reticulate) for AOU-4 (Check 1-4 + sensitivity + maf_drop)
  - pytest 8 for synthetic-fixture regression on Checks 1-4 + export landing
patterns:
  - design-delta sibling doc layers W1-derived operational SOP on top of immutable phase plan
  - notebook-content regression tests guard signed-r contract + future re-author drift
  - idempotent .npz existence check keyed off filename for websocket-drop resume
key-files-created:
  - (none — all artifacts already existed from Apr 30 prior execution; this wave amended notebooks + added one regression test)
key-files-modified:
  - .planning/notebooks/AOU-2_per_region_ld.ipynb (8 → 12 cells; +4 design-delta cells + MAF_THRESHOLD_EXPORT import)
  - .planning/notebooks/AOU-4_validation.ipynb (Check 3 cell appended with Q2 signed-r contract section)
  - tests/m3/test_validation_check_3_susie_convergence.py (+1 test: signed-r notebook-content regression)
commit-tokens:
  - e3c29e7 -- feat(m3-W2): inject W2 design-delta cells into AOU-2 notebook (m3-W2-T1)
  - 6962607 -- test(m3-W2): RED -- Q2 signed-r notebook-content regression for Check 3 (m3-W2-T2)
  - 001d8b1 -- feat(m3-W2): GREEN -- inject Q2 signed-r contract into AOU-4 Check 3 cell (m3-W2-T2)
decisions:
  - design-delta-applied: All 5 W1-derived deltas + Q2/Q6 layered onto immutable phase plan via sibling note + atomic commits
  - tdd-red-then-green: New signed-r regression authored RED then made GREEN within Task 2 atomic boundary
  - task-3-checkpoint-returned: Validation memo + flag touch deferred to Carter post-AoU-fire signoff
metrics:
  duration_minutes: ~40
  task_count_executed: 2
  task_count_total: 3
  files_modified: 3
  commits: 3
  tests_added: 1
  tests_pass: 23
  tests_fail: 0
  task_3_status: awaiting_carter_signoff
completed_date: 2026-05-21 (Tasks 1+2 only; Task 3 gated)
---

# Phase m3 Plan 02 (Wave 2): Dev fire + 4-check validation harness Summary

**One-liner:** Layered the m3-02-W2-DESIGN-DELTA.md operational SOP cells (W1-G1 idempotent resume + W1-G2 cluster preset + W1-G3 PD pre-check + W1-G4 JVM-wedge diagnostic + Q6 MAF_THRESHOLD_EXPORT import) onto the immutable phase-plan AOU-2 notebook, and added a TDD-style notebook-content regression guarding the Q2 signed-r contract in the AOU-4 Check 3 SuSiE-RSS cell — closing the only remaining design-delta gap from the 260520-s2s quick task on top of the Apr 30 pre-existing Task 1+2 deliverables. Task 3 is a human-verify checkpoint (Carter must resume AoU env, fire AOU-2 + AOU-4, write m3-VALIDATION-MEMO.md, touch m3_dev_complete.flag) and is intentionally left for Carter — this SUMMARY records progress through Tasks 1+2 with the plan formally still in-flight pending Carter signoff.

## Status

**PARTIAL — paused at Task 3 human-verify checkpoint.**

| Task | Type | Status | Commit(s) |
|------|------|--------|-----------|
| Task 1: AOU-2 per-region LD notebook + .touch_dev10 markers | auto | DONE (design-delta cells added on top of pre-existing Apr 30 baseline) | e3c29e7 |
| Task 2: AOU-4 + 5 pytest scaffolds + 4 .gitkeep + signed-r regression | auto-tdd | DONE (RED then GREEN; 23/23 tests pass) | 6962607 (RED) + 001d8b1 (GREEN) |
| Task 3: Carter signoff on m3-VALIDATION-MEMO.md + touch m3_dev_complete.flag | checkpoint:human-verify, gate:blocking | **AWAITING CARTER** — see Checkpoint section below | — |

Plan formal status remains `in_progress` in STATE.md / ROADMAP.md until Carter completes Task 3.

## Context — what state I inherited

This Wave 2 plan had been partially fired during a prior execution attempt circa 2026-04-30 — the AOU-2 + AOU-4 notebooks, the 5 pytest files, the 4 `.gitkeep` files, the 2 `.touch_dev10` markers, and the 4 validation/ subdirectories all existed on disk and 22/22 pytest tests already passed. What had NOT happened: the W2 design-delta lessons authored 2026-05-20 in the 260520-s2s quick task (and committed at 595d1f3 + 0abff84 + 51f9ce2) had not been layered into the notebooks. The design-delta sibling doc m3-02-W2-DESIGN-DELTA.md explicitly says "before authoring AOU-2 / AOU-4 notebooks, add the markdown SOP cells below" — i.e., the previous fire happened pre-design-delta. This Wave 2 execution closed that gap.

Reasoning: the phase plan is immutable; the design delta is the additive contract. Both must be satisfied before the plan can be considered correctly fired.

## Task 1 — AOU-2 design-delta cells injected

**Pre-existing baseline (committed Apr 30):** 8 cells, all 7 plan acceptance criteria pass (USE_DEV_SUBSET selector, compute_region_ld import, config/ld_regions{_dev}.tsv refs, .touch_dev10 markers).

**Design-delta gaps closed by e3c29e7:**

| Delta | Section | Cell injected | Purpose |
|-------|---------|---------------|---------|
| W1-G3 | PD pre-check | new Cell 0 | HALT-if-Standard guard; refs `[[feedback_aou_disk_type_check]]` + `[[feedback_aou_use_persistent_disk]]` |
| W1-G2 | Cluster preset | new Cell 2 (before env-config code) | 8×n1-highmem-16 dev (~$9.50/hr, 128 vCPU) vs 16×n1-highmem-16 prod (~$19/hr, 256 vCPU); refs `[[feedback_aou_cluster_sizing_for_ld_panel]]` |
| Q6 lock | MAF_THRESHOLD_EXPORT | env-config code cell modified | `from aou_ld_panel import MAF_THRESHOLD_EXPORT`; print value to ground Validation Memo §1 |
| W1-G1 | Resume protocol | new markdown before region loop | `{region_id}.npz` idempotency; `force_recompute=False`; `skipped_idempotent` status |
| W1-G4 | Stuck-region diagnostic | new markdown after region loop | jstack twice + Spark UI +details + REST stages?status=active; canonical 82-task finalize-cascade discriminator |

**Cell count:** 8 → 12 (well above plan's `>= 8`).

**Verification:** All 7 plan acceptance_criteria checks pass + 5 design-delta substring checks pass (Reattachable, n1-highmem-16, force_recompute, jstack/Spark UI, MAF_THRESHOLD_EXPORT).

## Task 2 — AOU-4 signed-r contract regression (TDD RED → GREEN)

**Pre-existing baseline (committed Apr 30):** AOU-4 had 13 cells, all 7 plan acceptance criteria pass (susie_rss/rs1558902/rs12740374/maf_drop.tsv/sensitivity grep counts; 4 .gitkeep files; 22/22 pytest tests pass).

**Design-delta gap closed by 6962607 + 001d8b1:**

The Q2 lock from 260520-s2s says "AOU-4 Cell 7-8 SuSiE-RSS path requires signed r — note in cell markdown." This phrase was not yet in the AOU-4 notebook. Closed via TDD discipline:

1. **RED (6962607):** Added `test_check_3_notebook_documents_signed_r_contract` to `tests/m3/test_validation_check_3_susie_convergence.py`. Asserts the AOU-4 notebook contains the phrases "signed r"/"signed-r" (case-insensitive) AND a reference to "Q2" or "260520-s2s". Test failed on the unmodified notebook as expected.
2. **GREEN (001d8b1):** Appended a "Q2 design-delta lock: signed r contract (260520-s2s)" section to the AOU-4 Check 3 markdown cell (idx 6) documenting:
   - susieR::susie_rss requires signed Pearson r (NOT r-squared, NOT |r|)
   - Upstream guarantee in `compute_region_ld()` via `hl.ld_matrix(n_alt_alleles, locus)` + float32 dtype assertion in `_save_npz`
   - Sign preservation through `ld_npz_to_rds.R` symmetrization
   - Future r²/|r| swap MUST update upstream + re-RED→GREEN Check 3
   - Regression test name explicitly referenced as the audit-trail guard
3. **Test re-run:** 4 pre-existing Check-3 tests + 1 new signed-r regression = 5 tests all pass. Full W2 pytest run: **23/23 pass**.

**Cell count:** 13 (unchanged; addendum appended to existing Cell 6).

**Verification:** `pytest tests/m3/test_validation_check_*.py tests/m3/test_aou_export_landing.py -v --tb=short` → 23 passed in 26.37s exit 0.

## Task 3 — Carter signoff checkpoint (NOT FIRED)

This task is a `type="checkpoint:human-verify" gate="blocking"` task that **cannot** be completed by an executor agent. The agent's role per the plan: "verify acceptance_criteria after Carter completes the gate."

### What Carter must do (the 7 steps)

1. **Confirm Persistent Disk is Reattachable** on the AoU Workbench env panel (W1-G3 pre-check now in AOU-2 Cell 0).
2. **Select cluster preset** — Wave 2 dev = 8× n1-highmem-16 (128 vCPU, ~$9.50/hr). Validate via `curl http://localhost:8088/ws/v1/cluster/metrics` showing `totalVirtualCores >= 128`.
3. **Resume the AoU Dataproc env** (currently PAUSED at $0.14/hr per STATE.md last-session; m3-W1 closed with all 3 cohort MTs already in bucket).
4. **Mirror AOU-2_per_region_ld.ipynb + AOU-4_validation.ipynb** into the AoU workspace.
5. **Fire AOU-2** — ~1–2 cluster-hours, ~$10–20 in AoU credits. Produces 13 .npz files (10 AFR + 3 EUR) + 2 BlockMatrix-shard dirs (HLA + 8p23, Path A.3) in `gs://${WORKSPACE_BUCKET}/ld/{AFR_aou,EUR_aou}/`.
6. **File 1–2 AoU egress requests** via Notebooks/Files UI; download to `data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/`. Capture export request IDs (will append to aou-egress-audit-log.md in Wave 4).
7. **Bootstrap-convert .npz → .rds** via Wave 3's converter (`src/scripts/ld_npz_to_rds.R`) into `data/processed/ld_reference/{AFR_aou,EUR_aou}/`. (W3 already wave-promoted; converter ready.)
8. **Fire AOU-4** — produces 4-check outputs + `sensitivity_cohort_r.tsv` + `maf_drop.tsv`.
9. **Write `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md`** (≥100 lines, 9-section structure per plan):
   - §1 Summary (per-check pass/fail + Q6 MAF 0.005 override rationale)
   - §2 Check 1 (FTO + SORT1 heatmap visual review vs Locke 2015 / Teslovich 2010)
   - §3 Check 2 (per-region Pearson r at MAF ≥ 0.05, ≥ 0.97 threshold)
   - §4 Check 3 (SuSiE-RSS converged, n_cs, median CS, lead PIP rs1558902)
   - §5 Check 4 (yield contrast table — THE M3 headline figure)
   - §6 Sensitivity-cohort correlation (D-M3-07 PCA-only sufficient?)
   - §7 MAF drop sanity (RESEARCH Q10 — halt if any region > 50%)
   - §8 Cost & timing (cluster-hours, .npz bundle sizes, AoU credits)
   - §9 Signoff statement: "I, Carter Clinton, sign off on the 4-check validation; Wave 4 production fire (322 cells) is unblocked. Path A.1/A.2/A.3 region-class branches per Wave 0 D-M3-09 ruling are accepted. Date: YYYY-MM-DD."
10. **`touch m3_dev_complete.flag`** at project root.
11. **Commit both** with token `(m3-W2-T3)` in the subject.
12. **Respond "approved"** (or describe issues) — Wave 4 unblocked.

### Acceptance criteria the orchestrator will spot-check after "approved"

(verbatim from plan):

- [ ] `test -f m3_dev_complete.flag` exits 0
- [ ] `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` exits 0
- [ ] `wc -l m3-VALIDATION-MEMO.md` returns ≥ 100
- [ ] `grep -c "Section 9.*signoff\|Carter Clinton" m3-VALIDATION-MEMO.md` returns ≥ 1
- [ ] `grep -c "Check 1\|Check 2\|Check 3\|Check 4" m3-VALIDATION-MEMO.md` returns ≥ 4
- [ ] `grep -c "D-M3-09" m3-VALIDATION-MEMO.md` returns ≥ 1
- [ ] `grep -c "rs1558902" m3-VALIDATION-MEMO.md` returns ≥ 1
- [ ] Git log shows a commit with `(m3-W2-T3)` token

### Why I am not writing the memo for Carter

The memo body MUST be grounded in real numbers from the AoU run — actual Pearson r values, actual SuSiE-RSS PIPs, actual yield-contrast cell counts, actual MAF-drop per-region ratios, actual cost figures. Writing the memo against synthetic placeholders would be a fabrication and would corrupt the Wave 4 production-gate audit trail. The flag (`m3_dev_complete.flag`) is similarly Carter's signoff token — touching it without the memo behind it would forge the gate.

## Deviations from Plan

### Auto-fixed Issues

**None.** Per Rule 4 of the deviation contract (architectural fixes need Carter signoff), nothing in Tasks 1–2 required that escalation. The design-delta cells were additive markdown, not structural — they layer onto the immutable phase plan exactly as the design-delta sibling doc specifies.

### Authentication Gates

**None.** No AoU access was required for Tasks 1–2 (notebook authoring + pytest scaffolds use synthetic fixtures only).

### Pre-existing State

Most W2 deliverables existed from a prior Apr 30 execution attempt. This wave **augmented** them with the 260520-s2s design-delta deltas (committed 2026-05-20 as 595d1f3 + 0abff84 + 51f9ce2) rather than recreating them. This is the rigor-defensible move: re-authoring would lose the existing pytest test history.

### Branch divergence note (informational; not in scope for this wave)

Local `main` and `origin/main` have diverged (855 ahead, 846 behind per `git status`). Two parallel commit chains exist for the same logical W2 work — origin chain (cfd59e7 + 1b56ab4 + b4b8a79; design-delta on origin) and local chain (595d1f3 + 0abff84 + 51f9ce2; design-delta on local + this wave's e3c29e7 + 6962607 + 001d8b1). Reconciliation belongs in a separate quick task after Carter Task 3 signoff; both chains converge on the same on-disk artifacts.

## Self-Check

### Files claimed-created (none for this wave) and claimed-modified

```
.planning/notebooks/AOU-2_per_region_ld.ipynb       — MODIFIED (e3c29e7)
.planning/notebooks/AOU-4_validation.ipynb          — MODIFIED (001d8b1)
tests/m3/test_validation_check_3_susie_convergence.py — MODIFIED (6962607 + verified GREEN at 001d8b1)
```

Verification:
- `test -f .planning/notebooks/AOU-2_per_region_ld.ipynb` → FOUND
- `test -f .planning/notebooks/AOU-4_validation.ipynb` → FOUND
- `test -f tests/m3/test_validation_check_3_susie_convergence.py` → FOUND
- `git log --oneline -3 main` → shows 001d8b1 + 6962607 + e3c29e7 in order → FOUND

### Commit-hash verification

- `e3c29e7` (Task 1 — AOU-2 design-delta cells) → FOUND in `git log`
- `6962607` (Task 2 RED — signed-r notebook regression) → FOUND in `git log`
- `001d8b1` (Task 2 GREEN — AOU-4 signed-r markdown) → FOUND in `git log`

### Plan acceptance criteria

**Task 1:**
- `test -f .planning/notebooks/AOU-2_per_region_ld.ipynb` → 0 ✓
- `len(nb['cells']) >= 8` → 12 ✓
- `grep -c "USE_DEV_SUBSET"` → 5 (≥2 required) ✓
- `grep -c "compute_region_ld"` → 6 (≥1 required) ✓
- `grep -c "config/ld_regions_dev.tsv"` → 2 (≥1 required) ✓
- `grep -c "config/ld_regions.tsv"` → 2 (≥1 required) ✓
- `test -d data/interim/aou_ld_exports/AFR_aou && test -d data/interim/aou_ld_exports/EUR_aou` → 0 ✓
- `test -f data/interim/aou_ld_exports/AFR_aou/.touch_dev10 && test -f data/interim/aou_ld_exports/EUR_aou/.touch_dev10` → 0 ✓

**Task 2:**
- `len(nb_aou4['cells']) >= 12` → 13 ✓
- `grep -c "susie_rss|susie\.rss|hyprcoloc"` → 7 (≥1 required) ✓
- `grep -c "rs1558902"` → 11 (≥1 required) ✓
- `grep -c "rs12740374"` → 5 (≥1 required) ✓
- `grep -c "maf_drop.tsv"` → 6 (≥1 required) ✓
- `grep -c "sensitivity"` → 9 (≥1 required) ✓
- `pytest ... -v` → 23 passed exit 0 (≥5 required) ✓
- 4 .gitkeep files exist → 4 ✓

**Task 3:** AWAITING CARTER — checkpoint properly returned; no agent-side acceptance criteria to verify pre-signoff.

## Self-Check: PASSED

All claimed files exist on disk; all 3 claimed commits exist in `git log`; all Task 1 + Task 2 acceptance criteria pass; Task 3 is correctly halted at a `type="checkpoint:human-verify" gate="blocking"` boundary with the structured checkpoint return below.

## Known Stubs

**None.** The validation/ subdirectories contain only `.gitkeep` files — but these are intentional dev placeholders for Carter's Task 3 AOU-4 fire to populate. They are not stubs in the misleading-UI sense (no user-facing dashboards reading empty data); they are gitkeep markers for directory structure preservation, exactly as the plan specifies.

## Threat Flags

None new. The plan's existing threat model (T-M3-EGR-W2, T-M3-S2-W2, T-M3-AUTH-W2) is fully honored. No new security surface introduced by this wave — only markdown additions to notebooks + one pytest assertion.
