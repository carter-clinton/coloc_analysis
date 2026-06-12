# Wave 2 readiness review — what stands between "cohort recovered" and "LD compute firing"

**Status:** updated 2026-06-11 — cohort build COMPLETE (GATE 1.5 closed) and GATE 0 confirmed already-resolved. Source: `WAVE-2-PLAN.md` (2026-06-04 audit) cross-checked against the current cohort + `.planning/amendments/` state.

---

## Where the gate sequence actually stands (vs WAVE-2-PLAN §3)

| Gate | What it is | Status NOW | Owner |
|---|---|---|---|
| **GATE 1.5** ✅ | Genome-wide cohort rebuild (3 MTs) — prerequisite for ALL LD compute | **DONE + verified** — AFR-primary 73,122×20,767,864; EUR 220,098×11,375,140; AFR-sens 62,557×20,817,925 (recovered + banked 2026-06-11). `cohort_summary_m3.tsv` = 3 rows. | done |
| **GATE 0** ✅ | AoU egress classification of the variant×variant LD matrices | **RESOLVED — RULED PASS 2026-04-28** (institutional basis; `.planning/amendments/aou-egress-audit-log.md`). LD R matrices are aggregate stats (every cell over n≥60k AFR / n≥130k EUR → clears the n≥20 floor), governed by AoU's standard egress review at export time, NOT a per-data-class letter. WAVE-2-PLAN §3's "unverified" note was stale (never cross-checked the amendments folder). | done |
| **GATE 1** 🟠 | Pre-fire readiness | Code work ✅ DONE. **2 Carter-only items open:** CDR pin (v8 stable, no mid-flight v8→v9), Cost/credit confirmation (~1,117 cluster-h → credit-$ + a cap) | **Carter** |
| **GATE 2** 🟡 | dev-10 LD fire + AOU-4 validation memo (the rigor gate; cheap) | not started — gated behind 1.5 + 1 | next compute step |
| **GATE 3** 🔴 | full 322-cell production fire + 44 egress requests | **BLOCKED on CR-01** (A.3 dense scratch) in addition to 0 + 2 — see the A.3 hardened-issue line below + `.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md` `gate3_blocker`. Resolved by the cluster ordering experiment picking the ordering that COMPLETES within the wall-time budget (NOT the lowering warning — it fires on all writes) and whose worst-case scratch (~2 TB, m2_region_00145) fits cluster scratch capacity; ordering B (Pan-UKBB band-then-checkpoint) is favored. | later |

## The critical-path read

- **GATE 1.5 is CLOSED** — all 3 cohorts banked genome-wide (2026-06-11); the LD-compute substrate exists.
- **GATE 0 is already RESOLVED (RULED PASS 2026-04-28)** — not a blocker. LD-matrix egress is governed by AoU's standard per-file egress review at export time (Wave 4), under the institutional-basis ruling on record (`aou-egress-audit-log.md`). Nothing to file. (Earlier drafts of this doc flagged it open — that propagated WAVE-2-PLAN §3's stale "unverified" note, which was never cross-checked against the amendments folder.)
- **GATE 2 (dev-10) is the next live step** — gated only on GATE 1 (CDR/cost). The cohort substrate is done and GATE 0 is resolved, so once GATE 1 clears the dev-10 rigor fire is unblocked.

## Open decisions for Carter (from WAVE-2-PLAN §5, still open)

1. ~~**[HARD] GATE 0 egress classification ruling**~~ — ✅ RESOLVED (RULED PASS 2026-04-28, `aou-egress-audit-log.md`; institutional basis). Aggregate LD matrices clear the n≥20 floor; standard AoU per-file egress review applies at export time. **No action.**
2. **Cost ceiling / credit balance** — confirm ~1,117 cluster-h fits AoU credits + set a cap (spec R3).
3. **Cluster preset** — 256 vs 384 vCPU (Gate C ran 24×n2-standard-16 = 384; preset already decided "MAX to quota, no overthreading, executor.cores=1").
4. **Export MAF** — keep 0.005 (recommended, preserves AFR rare-allele signal) or revert to spec's 0.01.
5. **Self-ID escalation** — pre-bless the auto-escalate (dev-10 self-ID-vs-PCA LD r < 0.995 → full genome-wide self-ID fire) or require a manual checkpoint. **(Now directly relevant — the self-ID cohort is the one being recovered; D-M3-07 decides whether it stays sensitivity-only or escalates.)**
6. **CDR pin** — confirm v8 stable (the recovery is v8/R8-matched; keep it pinned).

## Code-readiness (all NCSU-side fixes already landed — no action)
- HIGH-1 `to_numpy()` driver-OOM span-veto routing — FIXED `c6c32b3` (would have crashed the *first* dev-10 region).
- HIGH-3 xlarge-radius → 50-Mb-banded LD — accepted + documented `c11949e` (downstream SuSiE-RSS must treat the 16 xlarge cells as banded).
- MED-4 `.bm` populated-validation / MED-5 sidecar-upload-raise / MED-6 idempotency-byte-floor — FIXED `c11949e`; A.2/A.3 coverage tests added.
- **A.3 BlockMatrixIR-lowering HANG — FIXED for the HANG; CR-01 scratch scaling OPEN (blocks GATE 3).** The first live A.3 write on dev-10 GATE-2 (m2_region_00006, span 17.7 Mb, n_var=122,678) HUNG 60+ min: `hl.ld_matrix(...).write()` writes a single FUSED, UN-MATERIALIZED `BlockMatrixIR`. **CORRECTED MECHANISM (adversarial review 2026-06-12, Finding A):** the "BlockMatrixIR lowering not yet efficient" warning is NOT specific to this IR and is NOT eliminated by the fix — Hail 0.2.135's `CanLowerEfficiently.scala` fails on EVERY `BlockMatrixWrite` unconditionally, so ALL BlockMatrix writes run INTERPRETED (`LowerOrInterpretNonCompilable.scala` → `Interpret.alreadyLowered`). The hang is from feeding an UN-MATERIALIZED matmul to the interpreted writer → a single driver-side `ContextRDD.collect` (BlockMatrix.scala:978). Fix = reproduce ld_matrix's own internals (`row_correlation` → **`checkpoint`** → `locus_windows` band → `sparsify_row_intervals` → `write`); the checkpoint MATERIALIZES the matmul so the final write reads CONCRETE on-disk blocks (still interpreted, but cheap — NOT "lowers natively"; the warning still fires on all three writes). **Numerically identical** (same Pearson r, same bp-radius band; `blocks_only=False`). A.1/A.2 untouched.
  - **CR-01 (2026-06-11 review): the current ordering (A) checkpoints the FULL DENSE n×n correlation BEFORE banding → O(n_var²) scratch (~60 GB for region_00006; ~2 TB for the largest production region m2_region_00145, ~710k var).** **Ordering B (band-before-checkpoint) is the LEADING production-default candidate (adversarial review 2026-06-12, Finding C):** it is the PROVEN Pan-UKBB pattern (atgu/ukbb_pan_ancestry `compute_ld_matrix.py` does matmul → `_sparsify_row_intervals_expr` → `sparsify_triangle` → checkpoint at biobank scale), it resolves CR-01's dense scratch (banded ~GB vs ~TB), and the earlier "B might re-hang because `.checkpoint()` is a write of the same fused IR" fear was OVER-CAUTIOUS / contradicted by Pan-UKBB. B shrinks scratch most for mid-size regions; for the ~100 Mb xlarge regions the 50-Mb-capped radius bands ~98% of the row so banded ≈ dense (B's value there is completion, not footprint). **IR-shape caveat:** OLD's `ld_matrix().write()` and ordering B's checkpoint are the SAME `BlockMatrixWrite(sparsify(matmul))` shape, so the re-gated repro must EMPIRICALLY show B completes at our 122k²/710k² scale (Pan-UKBB suggests yes). Default ordering code stays A until the repro decides; B is FAVORED.
  - **dev-10 GATE-2 MAY PROCEED on current code (ordering A): ~60 GB scratch for one dev region is tolerable.** Run `scripts/a3_blockmatrix_lowering_repro.py` (a 3-way OLD/A/B ordering experiment, RE-GATED on wall-clock completion — Finding B) then re-fire the previously-hanging A.3 cell; verify at the data layer (gsutil du + `_assert_blockmatrix_written` shape).
  - **GATE 3 (322-cell production) is BLOCKED on CR-01.** It is resolved by the cluster ordering experiment picking the ordering that **COMPLETES within the wall-time budget** at a hang-inducing scale and whose worst-case scratch fits cluster capacity (the discriminator is COMPLETION-TIME + SCRATCH, NOT the lowering warning — the warning fires on all BlockMatrix writes, Finding A/B). Use the repro's `--report-scratch-size` extrapolation + the re-gated decision rubric in its docstring. If the rubric selects ordering B (the favored candidate), re-order `_write_a3_banded_correlation_bm` to band-before-checkpoint and re-verify before the production fire.
  - Pure-Python regression tests added (m3 suite, see session). Session: `.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md` (`gate3_blocker`).

## Sequencing recommendation (when recovery lands)
1. ✅ AFR-sens promoted → 3-row `cohort_summary_m3.tsv` (GATE 1.5 closed 2026-06-11).
2. Carter confirms **GATE 1**: cost/credit (~1,117 cluster-h vs balance + a cap) + CDR v8 pin. (GATE 0 already resolved — no egress filing needed.)
3. dev-10 LD fire (GATE 2) as soon as GATE 1 clears — the next live compute step.
4. Durable atomic-final-write fix via `/gsd-plan-phase --gaps` (design staged — `DURABLE-FIX-DESIGN-atomic-final-write.md`) — slot before GATE 3 production so the 322-cell fire writes under the hardened contract.

## Working-tree note (RESOLVED)
The 54 tracked-file deletions (m1/m2 envs, pathway configs, legacy docs) were committed as intentional cleanup 2026-06-11 (commit `c2dfb08`). The 5 Wave-2-critical configs were already restored and untouched. Closed.
