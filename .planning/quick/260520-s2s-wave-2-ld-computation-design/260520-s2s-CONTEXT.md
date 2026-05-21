# Quick Task 260520-s2s: wave 2 LD computation design — Context

**Gathered:** 2026-05-21
**Status:** Ready for planning
**Mode:** `/gsd-quick --discuss` (working-without-stopping directive; decisions made under Claude's Discretion grounded in prior locked decisions + W1 lessons + `feedback_rigor_over_speed`)

<domain>
## Task Boundary

Resolve the **7 Wave-2 LD-computation design questions** posed in `POST-WAVE-1-ROADMAP.md` §4, plus the operational gray areas surfaced by the Wave-1 67h monolithic-fire experience (cluster-sizing, websocket-drop / iframe-hostility, JVM-wedge discriminator, persistent-disk topology).

In scope: design-decision capture, mapping to the existing `m3-02-W2-dev-fire-and-validation-PLAN.md`, and surfacing any **plan-deltas** that the W1 lessons require relative to the pre-W1-fire plan.

Out of scope: actual notebook authoring (that's Wave-2 execution proper — `m3-02-W2-...PLAN.md` Task 1/2/3); MTAG locus-list coordination beyond Q7 design (that's m2-supplementary phase per D-M3-05).

The deliverable of this quick task is a **design-decision document** (this CONTEXT.md) + a small **plan-delta note** capturing where the existing m3-02-W2 plan needs amendment vs ratification.

</domain>

<decisions>
## Implementation Decisions

### POST-WAVE-1-ROADMAP §4 — 7 Design Questions

#### Q1 — Full-genome pre-compute vs locus-by-locus on-demand?

**Status: LOCKED by D-M3-02 — locus-by-locus over a fixed 161-region manifest.**

- D-M3-02 commits to all 161 regions × 2 ancestries = 322 cells in production
- `config/ld_regions.tsv` (Wave 0) is the canonical manifest; `config/ld_regions_dev.tsv` is the 10-row dev subset
- The 161 regions are the **M2 union region list** — pre-computed for the loci MTAG/CPASSOC will surface (the manifest IS the answer to Q7)
- Path A.1/A.2/A.3 per D-M3-09 governs how each region writes (`compute_region_ld()` in `src/python/aou_ld_panel.py`)

**Why:** Not a re-open. The "MTAG-list sequencing" worry resolves into "region manifest IS the MTAG candidate window list" — pre-computed LD is available for every region MTAG would surface. The full-genome path was rejected at D-M3-02 design.

**How to apply:** Wave 2 dev fire iterates the 10 dev rows; Wave 4 production fires the remaining 312.

---

#### Q2 — Which LD metric: r², signed r, or both?

**Decision: SIGNED r (float32), lower-triangular, MAF-filtered.**

- Lower-triangular signed r matrix written as compressed `.npz` (existing AOU-LD-PIPELINE.md §7.2 spec)
- r² derivable downstream via element-wise square (free; no double-storage)
- **Required** for SuSiE-RSS in Validation Check 3 (m3-02-W2 PLAN Task 2 Cells 7-8) — `susieR::susie_rss()` needs signed r, not r²
- Required for hyprcoloc cross-trait coloc downstream (Wave 3 Step 4 in POST-WAVE-1-ROADMAP)

**Why:** Sign is recoverable at zero extra storage cost (same float32). Storing only r² would lose information SuSiE-RSS needs and force a re-fire. Per `feedback_rigor_over_speed.md`: pick the reviewer-defensible option even if file size is slightly larger.

**How to apply:** `compute_region_ld()` already returns `hl.row_correlation` (signed); confirm the `to_numpy()` / `BlockMatrix.write` path preserves sign through the .npz serialization. Add a regression test (`tests/m3/test_ld_panel_signed_r_preservation.py`) — TDD per `feedback_extract_reusable_utilities.md` since this is reviewer-critical correctness.

---

#### Q3 — BlockMatrix `block_size` parameter?

**Decision: Hail default 4096 for Path A.1/A.2 (small/medium regions); Path A.3 fallback for HLA + 8p23 per D-M3-09.**

- W1 ran cleanly at 256 vCPU (16× n1-highmem-16) with default partitioning → no evidence change is warranted
- Path A.3 (`BlockMatrix.write` to bucket, densify deferred to NCSU) absorbs the HLA + 8p23 dense-region OOM risk per AOU-LD-PIPELINE.md §12 R12
- `block_size` tuning is a **runtime fallback** — leave the spec default unless a specific region OOMs the driver, in which case `compute_region_ld()` already has the Path A.3 branch as the escape valve

**Why:** Premature parameter tuning ahead of evidence is anti-rigorous. The dev-10 fire INCLUDES the 2 HLA-stress regions specifically to expose any block-size issue before production. If dev-10 surfaces an issue, then tune. Not before.

**How to apply:** No code change. Document in m3-VALIDATION-MEMO.md Section 8 (Cost & timing) any block-size adjustment if a Path A.3 region OOMs.

---

#### Q4 — Output format for HPC consumption?

**Status: LOCKED — lower-triangular float32 `.npz` per AOU-LD-PIPELINE.md §7.2 + D-M3-02; converted to `.rds` on NCSU via `src/scripts/ld_npz_to_rds.R` (Wave 3).**

- `.npz` is universal across Python/R (via `reticulate` or `np.load`)
- Lower-triangular halves the storage; symmetry recovered at `.rds` conversion
- `.rds` is the Snakemake `ld_panel:` resolver substrate (`data/processed/ld_reference/{AFR_aou,EUR_aou}/{region_id}.rds`)
- Existing Wave 0 ingest rules (`src/snakemake/rules/m3_convert_npz_rds.smk`) handle the conversion

**Why:** Not a re-open. The format chain `.npz` → `.rds` → `coloc::coloc.abf` / `susieR::susie_rss` is locked at D-M3-02 + the m3 phase architecture.

**How to apply:** No design change. Confirm `compute_region_ld()` writes float32 (not float64) to halve the .npz size — verify via `tests/m3/test_ld_panel_signed_r_preservation.py` (assert `.dtype == np.float32`).

---

#### Q5 — Per-population separately or pooled?

**Status: LOCKED by D-M3-07 — per-population, three cohorts.**

- `mt_afr_qc.mt` (AFR primary; n ~50k) → `gs://${WORKSPACE_BUCKET}/ld/AFR_aou/`
- `mt_afr_pca_selfid_qc.mt` (AFR sensitivity; n ~30-45k) → `gs://${WORKSPACE_BUCKET}/ld/AFR_aou_selfid/` (D-M3-07 sensitivity comparator; NOT in production export — sensitivity-correlation table only per Wave 2 Cells 11-12)
- `mt_eur_qc.mt` (EUR replication; n ~150k) → `gs://${WORKSPACE_BUCKET}/ld/EUR_aou/`

**Why:** Not a re-open. The headline contrast IS the result (POST-WAVE-1-ROADMAP §5 Step 5: AFR-LD vs EUR-LD coloc-shift comparison). Pooling would destroy the entire methodological contribution.

**How to apply:** Three separate `compute_region_ld()` driver calls per region (one per MT). Note: AFR sensitivity (`mt_afr_pca_selfid_qc.mt`) feeds the **D-M3-07 sensitivity-correlation table** in AOU-4 Cells 11-12; it does NOT need to fire all 161 regions, only the 5 AFR-known dev regions + 10 lead loci downstream (decision: keep sensitivity fire scoped to dev-10 + later targeted; do NOT do all 161 cells for sensitivity).

---

#### Q6 — Variant frequency (MAF) filter?

**Decision: MAF ≥ 0.005 for INTERNAL compute AND .npz EXPORT (override AOU-LD-PIPELINE.md §7.2 "MAF ≥ 0.01 for export" recommendation).**

- AOU-LD-PIPELINE.md §7.2 default: MAF ≥ 0.01 export / MAF ≥ 0.005 internal
- m3-RESEARCH.md Q10 reports the 0.01-vs-0.005 drop is ~30% of variants in AFR
- M2-novel AFR variants concentrate in the 0.005–0.01 band — dropping them at export forfeits the AFR-specific signal the project exists to capture
- Storage cost: ~30% larger .npz files. For 161 regions × ~50 MB average = ~8 GB total → ~10.5 GB at 0.005 floor. Trivial vs egress / NCSU storage.

**Why:** `feedback_rigor_over_speed.md` — when a gray-area trade-off pits file-size against scientific signal, pick rigor. Reviewers will ask "did you exclude rare-variant LD that drives the AFR-specific signal?" — answer must be "no, we exported down to MAF ≥ 0.005."

**How to apply:** Set `MAF_THRESHOLD_EXPORT = 0.005` as a constant at the top of `src/python/aou_ld_panel.py`; thread through `compute_region_ld()`; document in m3-VALIDATION-MEMO.md §1 Summary (override of spec default, with rationale).

**RESEARCH Q10 halt check still applies:** if a dev-10 region shows > 50% variant-drop at 0.005 vs 0.01 (unexpected; would indicate cohort/variant-pipeline pathology), halt at Carter checkpoint per the existing PLAN.

---

#### Q7 — Coordination with MTAG locus list?

**Status: RESOLVED at D-M3-02 — pre-compute over the 161-region M2-union manifest; MTAG hits → look up LD per surfaced region.**

- The 161-region manifest IS the MTAG candidate window list (M2 union regions = where multi-trait signal will appear)
- Region windows are ±500 kb around lead variants, large enough to capture causal-variant uncertainty
- MTAG runs on HPC (Wave 3 Step 3) reading egressed `.rds` LD; no AoU re-fire needed per surfaced locus

**Why:** Not a re-open. The chicken-and-egg problem from POST-WAVE-1-ROADMAP Q7 is solved by anchoring on M2's region union (which already captures every multi-trait-relevant locus).

**How to apply:** No design change. Wave 3 MTAG output should be cross-referenced against `config/ld_regions.tsv` `region_id` column for the lookup join.

---

### W1-Derived Operational Gray Areas (NEW, not in POST-WAVE-1-ROADMAP §4)

#### W1-G1 — Resume/checkpoint strategy under websocket-drop risk

**Decision: per-region atomic write to bucket; idempotent re-fire skips regions where `.npz` already exists.**

- W1 lesson: `feedback_aou_websocket_drop_zombie_pattern.md` — browser timeouts leave orphan kernels + JVMs
- Wave 2 dev fire is 10 regions × ~5-15 min each = 1-3 hours total — short enough that a single websocket drop forfeits manageable progress, BUT
- `compute_region_ld()` writes one `.npz` per region; if the kernel drops, the loop can be re-fired and an idempotency check (`if gs://...{region_id}.npz exists, skip`) keeps the re-fire cheap
- Production fire (322 cells) makes idempotency **mandatory** — a 30h fire can't tolerate a single websocket drop costing the full run

**Why:** W1 spent ~$2,100 cumulative across 4 sessions partly because of resume-after-failure friction. Per-region atomic + idempotent re-fire is the standard resume protocol.

**How to apply:** Add idempotency guard to `compute_region_ld()`:
```python
out_path = f"{out_bucket}/{region_id}.npz"
if gs_path_exists(out_path) and not force_recompute:
    return {"region_id": region_id, "status": "skipped_idempotent", "n_var": "NA"}
```
Add a TDD regression test (`tests/m3/test_compute_region_ld_idempotent.py`). Per `feedback_extract_reusable_utilities.md`: idempotency is a reusable utility for any future per-region compute.

---

#### W1-G2 — Cluster sizing for Wave 2 dev fire vs production fire

**Decision: dev fire on 8× n1-highmem-16 (128 vCPU); production fire on 16× n1-highmem-16 (256 vCPU; W1-proven).**

- W1 lesson: `feedback_aou_cluster_sizing_for_ld_panel.md` — 256 vCPU is the proven config for full-cohort load_qc_cohort
- Wave 2 reads pre-built MTs (cheap row-iteration) and runs region-bounded `hl.row_correlation` (small matrices per region) — does NOT need 256 vCPU for the dev-10
- 8× n1-highmem-16 (128 vCPU, ~$9.50/hr) gives ample container headroom for region-bounded compute including HLA-stress Path A.3
- Production fire (322 cells, ~5-7 wall days) returns to 256 vCPU (W1 config; proven; quota-respecting at 8-12 concurrent Dataproc jobs ceiling)

**Why:** Save ~$10/hr × 1-3h dev fire = ~$10-30 on dev without sacrificing safety margin. If dev surfaces a sizing issue, autoscale up; W1's sizing memory holds the proven-good upper bound.

**How to apply:** Document cluster config in the AOU-2 notebook Cell 1 markdown:
```
# Wave 2 dev fire: provision 8× n1-highmem-16 (128 vCPU); ~$9.50/hr
# Wave 4 production: provision 16× n1-highmem-16 (256 vCPU); ~$19/hr
```
Carter selects in AoU Workbench env panel before resume.

---

#### W1-G3 — Persistent disk for env resume

**Decision: Reattachable persistent disk (PD), confirm before resume.**

- W1 lesson: `feedback_aou_use_persistent_disk.md` — Standard disk = delete erases everything; ~$4.80/mo for PD is trivial insurance
- Resume from PD preserves `/tmp/hail.log` and any in-flight notebook state from the W1 session
- Pre-resume check: confirm env panel shows "Persistent disk: Reattachable" not "Standard"

**Why:** W1's `feedback_aou_disk_type_check.md` is mandatory pre-resume hygiene. PD also preserves the `.bak` forensic artifact path from `feedback_aou_disk_type_check.md`.

**How to apply:** Wave 2 Task 0 (pre-fire) = workbench dashboard check; confirm disk-type label before resume button. If Standard, halt and migrate to PD before any compute fires.

---

#### W1-G4 — JVM wedge discriminator at Wave 2 fire time

**Decision: bake `feedback_aou_hail_driver_quiet_vs_wedge.md` discriminator into the Wave 2 SOP.**

- W1 lesson: Hail driver-quiet during executor-bound stages looks identical to a true JVM wedge
- Run `jstack <hail_pid>` + Spark REST `stages?status=active` BEFORE any kill decision
- For Wave 2's shorter compute (1-3h dev, 5-7 days production), wedge-vs-progress discrimination is still relevant — a stuck region wastes hours

**Why:** Saved a misread on W1 Cell 7 Stage 71 ($800-9,000 unnecessary burn potential). Same discriminator applies here.

**How to apply:** Add to AOU-2 notebook Cell 6 (post-compute summary): inline reminder text:
```
# DIAGNOSTIC RECIPE for stuck region:
# 1. ps aux | grep -E "java.*hail" → get PID
# 2. jstack $PID → check for live JIT bytecode classes
# 3. Spark UI → click +details on active stage, compare stack signature to known-good
# 4. Only kill if jstack shows true wedge (no progress in JIT classes)
```

---

#### W1-G5 — Compute helper location: extend `aou_ld_panel.py` vs new `ld_matrix_compute.py`?

**Decision: extend the existing `src/python/aou_ld_panel.py` (Wave 0 deliverable); do NOT spawn a new `ld_matrix_compute.py` module.**

- POST-WAVE-1-ROADMAP §6 suggested `src/python/ld_matrix_compute.py + tests/m3/test_ld_matrix_compute_local.py` — but POST-WAVE-1-ROADMAP was drafted during the MT #3 wait without full context of Wave 0's existing helper
- The existing `aou_ld_panel.py::compute_region_ld()` already implements Path A.1/A.2/A.3 branching; it's wired into AOU-2 notebook Cell 4 in the m3-02-W2 PLAN
- Module proliferation is anti-rigorous; the existing helper is the right home for the idempotency guard (W1-G1) + MAF threshold update (Q6) + signed-r preservation test (Q2)

**Why:** `feedback_extract_reusable_utilities.md` — extend, don't fragment. Tests live at `tests/m3/test_aou_ld_panel.py` (existing).

**How to apply:** Plan delta to m3-02-W2 PLAN Task 1: prepend a sub-task "Extend `aou_ld_panel.py` with: (a) MAF_THRESHOLD_EXPORT = 0.005 (override §7.2 default), (b) idempotency guard, (c) float32 dtype assertion. Add 3 regression tests under `tests/m3/test_aou_ld_panel.py`."

---

### Claude's Discretion (gray areas where Carter should redirect if my read is wrong)

All decisions above are **Claude's Discretion under the working-without-stopping directive**. The following are most likely to be overruled and should be flagged:

1. **MAF 0.005 export (Q6)** — overrides spec §7.2 default of 0.01. If Carter wants to keep 0.01 for spec-conformance + smaller files, this single constant flips back. Trade-off: ~30% AFR variant loss in the rare-allele band.

2. **Dev cluster downsize to 8× n1-highmem-16 (W1-G2)** — saves ~$10-30 on dev fire but introduces a config-different-than-production sizing. If Carter prefers single-config simplicity, run dev at 16× too (Wave 1's known-good); cost: ~$20-60 extra on dev fire.

3. **AFR sensitivity (`mt_afr_pca_selfid_qc.mt`) scoped to dev-10 + targeted (Q5)** — does NOT fire all 161 regions for sensitivity. Reviewer-defensibility hinges on D-M3-07 sensitivity-correlation showing r > 0.995 at dev-10 lead loci → "PCA-only sufficient." If r < 0.995 surfaces, full sensitivity fire becomes mandatory (~+$50-200 cost).

4. **Idempotency guard added to existing helper vs separate wrapper (W1-G1, W1-G5)** — I chose extending `aou_ld_panel.py`. If Carter prefers a thin `compute_region_ld_resumable()` wrapper that calls the existing helper, that's a small refactor; functionally equivalent.

</decisions>

<specifics>
## Specific Ideas

- **Module: `src/python/aou_ld_panel.py`** — extend with `MAF_THRESHOLD_EXPORT = 0.005`, idempotency guard, float32 dtype check.
- **Tests: `tests/m3/test_aou_ld_panel.py`** — add three regressions per W1-G1 + Q2 + Q6.
- **Manifest: `config/ld_regions_dev.tsv`** — 10 rows (3 EUR + 5 AFR + 2 HLA-stress) per D-M3-04; no change.
- **Notebook: `.planning/notebooks/AOU-2_per_region_ld.ipynb`** — m3-02-W2 PLAN Task 1 deliverable; design discussion ratifies the existing plan with the W1-G1/G2/G3/G4 SOP additions in notebook markdown cells.
- **Notebook: `.planning/notebooks/AOU-4_validation.ipynb`** — m3-02-W2 PLAN Task 2 deliverable; ratified as-is; Check 3 SuSiE-RSS requires signed r (Q2 decision lands here).
- **Validation memo: `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md`** — must document the MAF 0.005 export override (§1) + cluster sizing actuals (§8) + sensitivity-correlation results (§6).
- **Cluster preset (dev fire):** 8× n1-highmem-16 (128 vCPU) — for Carter's selection at workbench resume.
- **Cluster preset (production fire):** 16× n1-highmem-16 (256 vCPU) — W1-proven config.

</specifics>

<canonical_refs>
## Canonical References

- `POST-WAVE-1-ROADMAP.md` §4 — the 7 design questions framing this discussion (top-level repo file, commit `8073f25`)
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` — locked D-M3-01 through D-M3-09 decisions
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-02-W2-dev-fire-and-validation-PLAN.md` — existing Wave 2 plan (3 tasks); design decisions here are deltas/ratifications against this plan
- `.planning/amendments/AOU-LD-PIPELINE.md` — §7.2 (MAF + .npz format), §9 (4-check validation), §12 R12 (OOM risk)
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md` Q3, Q5, Q10 — open research questions that this discussion partially closes
- `src/python/aou_ld_panel.py` — Wave 0 helper `compute_region_ld()` (extended per W1-G5)
- Memory: `feedback_rigor_over_speed.md`, `feedback_aou_cluster_sizing_for_ld_panel.md`, `feedback_aou_websocket_drop_zombie_pattern.md`, `feedback_aou_hail_driver_quiet_vs_wedge.md`, `feedback_aou_use_persistent_disk.md`, `feedback_extract_reusable_utilities.md`

</canonical_refs>
