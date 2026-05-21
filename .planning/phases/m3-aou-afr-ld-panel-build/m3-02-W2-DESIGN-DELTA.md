# m3-02-W2 Wave 2 — Design Delta Note

**Quick task:** `260520-s2s` (wave 2 LD computation design)
**Authored:** 2026-05-20
**Status:** Active — applies before m3-02-W2 Task 1 notebook authoring
**Base commit:** d4c8005 (pre-quick HEAD)
**Code commits:** 51f9ce2 (T1 RED) + 0abff84 (T2 GREEN)

## Purpose

This note records design deltas and ratifications produced by the
`/gsd-quick 260520-s2s` discussion (see
`.planning/quick/260520-s2s-wave-2-ld-computation-design/260520-s2s-CONTEXT.md`)
against the existing immutable phase plan
`.planning/phases/m3-aou-afr-ld-panel-build/m3-02-W2-dev-fire-and-validation-PLAN.md`.

The phase plan itself is NOT edited (phase-plan immutability). This sibling
note tells the Wave 2 executor: "before authoring AOU-2 / AOU-4 notebooks,
add the markdown SOP cells below; these reflect lessons learned from the
67h Wave 1 fire that the original phase plan could not anticipate."

## Decisions ratified against m3-02-W2 PLAN

### POST-WAVE-1-ROADMAP §4 — 7 design questions

| Q  | Topic                              | Status                                              | Lock site                | Notebook impact                                                                                       |
|----|------------------------------------|-----------------------------------------------------|--------------------------|-------------------------------------------------------------------------------------------------------|
| Q1 | Full-genome vs locus-by-locus      | LOCKED by D-M3-02                                   | m3-CONTEXT.md            | None (already in PLAN; 161 regions × 2 ancestries × cohorts = 322 production cells)                   |
| Q2 | Signed r vs r²                     | DECIDED: signed r, float32                          | 260520-s2s-CONTEXT.md    | AOU-4 Cell 7-8 SuSiE-RSS path requires signed r — note in cell markdown                               |
| Q3 | BlockMatrix block_size             | DECIDED: Hail default (no tuning)                   | 260520-s2s-CONTEXT.md    | None (revisit only if dev-10 Path A.3 OOMs HLA / 8p23)                                                |
| Q4 | Output format                      | LOCKED by D-M3-02 (.npz lower-triangular float32)   | m3-CONTEXT.md            | None (already in PLAN); float32 contract now defensively asserted in `_save_npz`                      |
| Q5 | Per-population vs pooled           | LOCKED by D-M3-07 (per-pop, 3 cohorts)              | m3-CONTEXT.md            | AFR sensitivity scoped to dev-10 + targeted (not all 161)                                             |
| Q6 | MAF filter                         | DECIDED: 0.005 export (override §7.2 0.01)          | 260520-s2s-CONTEXT.md    | Validation Memo §1 must document the override + rationale; `MAF_THRESHOLD_EXPORT` constant exposed    |
| Q7 | MTAG locus coordination            | RESOLVED at D-M3-02 (manifest IS the locus list)    | m3-CONTEXT.md            | None                                                                                                  |

### W1-Derived operational gray areas (NEW additive content)

These are NOT in the immutable m3-02-W2 PLAN because they emerged from
the W1 fire experience. They land as additive markdown cells in the
notebooks AOU-2 (Task 1) and AOU-4 (Task 2) at authoring time.

#### W1-G1 — Idempotent resume (CODE DELTA + notebook markdown)

- **Code delta (applied this quick task — commit 0abff84):**
  - `compute_region_ld()` accepts new keyword-only param `force_recompute=False`
  - New helper `_existing_region_npz(region_id, out_bucket, out_local_dir)` checks
    GCS via `hl.hadoop_is_file` and local fallback via `Path.is_file`
  - Guard at top of `compute_region_ld` short-circuits with
    `status='skipped_idempotent'` when `{region_id}.npz` already exists and
    `force_recompute=False`
  - Path A.3 (`.bm` BlockMatrix) idempotency is DEFERRED (dev-10 has only 2
    Path A.3 regions; `BlockMatrix.write(overwrite=True)` keeps re-fires
    correct, just wasteful)
- **Notebook markdown delta (AOU-2 Cell 4 — region loop):** add a comment cell
  BEFORE the loop reading:
  > **Resume protocol:** if this notebook is re-fired after a websocket drop, the
  > loop is idempotent — completed regions return `status='skipped_idempotent'`
  > without re-running `hl.ld_matrix`. To force-recompute a single region, call
  > `compute_region_ld(..., force_recompute=True)`. Idempotency keyed off
  > `{region_id}.npz` existence at the target bucket/path; Path A.3
  > BlockMatrix regions re-run safely via `overwrite=True`.

#### W1-G2 — Cluster sizing (notebook markdown only — code N/A)

- **Notebook markdown delta (AOU-2 Cell 1 — env config):** add a cell:
  > **Cluster preset:**
  > - Wave 2 dev fire: 8× n1-highmem-16 (128 vCPU; ~$9.50/hr)
  > - Wave 4 production fire: 16× n1-highmem-16 (256 vCPU; ~$19/hr; W1-proven config)
  >
  > Select via AoU Workbench env panel BEFORE clicking Resume. See
  > `feedback_aou_cluster_sizing_for_ld_panel.md`.

#### W1-G3 — Persistent disk pre-check (notebook markdown only — code N/A)

- **Notebook markdown delta (AOU-2 Cell 0 — pre-fire checks):** add a cell at the very top:
  > **PRE-FIRE: Confirm Persistent Disk is Reattachable.**
  > 1. Open AoU Workbench env panel.
  > 2. Confirm "Persistent disk: Reattachable" — NOT "Standard".
  > 3. If Standard, HALT and migrate to PD before clicking Resume.
  >
  > See `feedback_aou_disk_type_check.md` + `feedback_aou_use_persistent_disk.md`.

#### W1-G4 — JVM wedge discriminator (notebook markdown only — code N/A)

- **Notebook markdown delta (AOU-2 Cell 6 — post-loop diagnostics):** add a cell:
  > **DIAGNOSTIC RECIPE — stuck region**
  > Hail driver-quiet during executor-bound stages looks identical to a true JVM
  > wedge. Before any kill decision:
  > 1. `ps aux | grep -E "java.*hail"` → get PID
  > 2. `jstack $PID` → check for live JIT bytecode classes (progress) vs. true wedge
  > 3. Spark UI → click +details on the active stage and compare its stack signature
  >    against a known-good stage from a completed region
  > 4. Only kill if `jstack` shows no progress in JIT classes for > 5 min
  >
  > See `feedback_aou_hail_driver_quiet_vs_wedge.md` +
  > `feedback_aou_spark_ui_stack_trace_verification.md`.

#### W1-G5 — Code lives in `aou_ld_panel.py`, NOT a new module

- POST-WAVE-1-ROADMAP §6 suggested `src/python/ld_matrix_compute.py` +
  `tests/m3/test_ld_matrix_compute_local.py`; this discussion overrides →
  extend `aou_ld_panel.py` and `tests/m3/test_aou_ld_panel_local.py`.
- Rationale: module proliferation is anti-rigorous; `compute_region_ld()` is
  already the right home. `feedback_extract_reusable_utilities.md` —
  extend, don't fragment.
- Tests live at `tests/m3/test_aou_ld_panel_local.py` (not a new module).
- **Code delta applied this quick task (commits 51f9ce2 RED + 0abff84 GREEN).**

## Claude's-Discretion flags (overruleable by Carter)

The following decisions were made under the working-without-stopping directive
and are the most likely to be redirected. If Carter overrules any, the
corresponding code/notebook delta is reverted.

1. **MAF 0.005 export (Q6)** — overrides spec §7.2. If reverted to 0.01:
   change `MAF_THRESHOLD_EXPORT = 0.01` in `src/python/aou_ld_panel.py`; trade-off
   is ~30% AFR variant loss in the rare-allele band.
2. **Dev cluster downsize (W1-G2)** — saves ~$10–30 on dev fire; if reverted,
   run dev at 16× (Wave 1's known-good).
3. **AFR sensitivity scope (Q5)** — sensitivity fire restricted to dev-10 + targeted;
   if D-M3-07 sensitivity-correlation < 0.995, full sensitivity fire becomes
   mandatory (~+$50–200).
4. **Idempotency in existing helper vs separate wrapper (W1-G1/G5)** — chose
   extension; alternative is a thin `compute_region_ld_resumable()` wrapper.
   Functionally equivalent; the chosen approach matches
   `feedback_extract_reusable_utilities.md` extend-don't-fragment rule.

## Relationship to existing PLAN tasks

| m3-02-W2 PLAN task                | Delta source                | Concrete change                                                                                                                                                                                |
|-----------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Task 1 (AOU-2 notebook authoring) | W1-G1/G2/G3/G4 + Q6         | Add markdown cells listed in W1-G1..G4 sections above; import `MAF_THRESHOLD_EXPORT` from `aou_ld_panel` for the Validation Memo §1 reference; pass `force_recompute=False` (default) in the loop |
| Task 2 (AOU-4 validation notebook)| Q2                          | Reference signed-r contract in Check 3 SuSiE-RSS cell markdown                                                                                                                                 |
| Task 3 (bucket integrity check)   | (none)                      | Ratified as-is                                                                                                                                                                                 |

## Audit trail

- 260520-s2s discussion outputs: `.planning/quick/260520-s2s-wave-2-ld-computation-design/260520-s2s-CONTEXT.md`
- 260520-s2s execution plan: `.planning/quick/260520-s2s-wave-2-ld-computation-design/260520-s2s-PLAN.md`
- Code deltas (this quick task):
  - 51f9ce2 — test(m3): add 3 W2 design-delta regression tests (RED) (260520-s2s-T1)
  - 0abff84 — feat(m3): apply W2 design-delta code changes (GREEN) (260520-s2s-T2)
- Phase plan: `.planning/phases/m3-aou-afr-ld-panel-build/m3-02-W2-dev-fire-and-validation-PLAN.md` (NOT edited; immutability preserved)
