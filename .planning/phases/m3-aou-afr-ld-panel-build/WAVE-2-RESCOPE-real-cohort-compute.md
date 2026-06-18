# Wave-2 RE-SCOPE — real-cohort LD compute is intractable on the dev cluster

**Created:** 2026-06-18 (after the dev-10 fire was killed). **Status:** finding recorded; needs `/gsd-plan-phase` for the cluster-sizing + xlarge-region-splitting + cost-model redo before any re-fire.

## The finding (what the dev-10 fire proved)

dev-10 (AOU-2, `USE_DEV_SUBSET=True`) was fired on cluster `20260617` (16× n2-standard-4 = 64 vCPU / 16 GB workers, master n2-standard-16). **It is operationally intractable on this cluster** and was killed with **zero regions completed**:

- `region_00006` (the *cheapest* A.3 region: n_var=122,678, AFR n_samples=73,122) ran its 900-block Stage-4 at **~0.9–2.1 blocks/min** — vs **~66 blocks/min** for the synthetic repro (`--n-var 130000`, **1024 blocks**, 928 s) on the *same* cluster.
- The **driver CRASHED** during region_00006's dense-scratch phase (dense scratch reached **~65 GiB**; the banded final `.bm` was never produced) — the kernel restarted on its own.
- Extrapolated: `region_00040` (xlarge, ~615k var, ~22,500 blocks, runs ×2 AFR+EUR) ≈ **~weeks per cell** at this rate. The full 10-cell loop could not finish.

## Root cause — the repro measured the operation, not the cost

The repro used **`--n-samples 2000`** (synthetic). The real cohorts are **AFR 73,122 / EUR 220,098** samples. The correlation is `standardized_GT @ standardized_GT.T`, whose **inner dimension IS the sample count**, so each block's matmul is **~36× (AFR) to ~110× (EUR) heavier on real data** than the repro measured. Plus the **16 GB workers spill** on sample-heavy partitions (~another 2×), and the **64 GB master can't sustain** the dense-scratch materialization (the crash). The repro correctly proved the **A.3 fix's correctness** (blocks advance, no driver-collect *hang*) — but its 928 s wall-time was **never representative of real-cohort cost**, and we sized the fire off it. Lesson banked: [[feedback_size_cost_experiments_on_real_data_dimensions]].

## Re-scope — three coupled changes (do via /gsd-plan-phase)

### 1. Cluster sized for real-cohort compute
| | dev cluster (intractable) | re-fire target |
|---|---|---|
| Workers | 16× n2-standard-4 (16 GB) | **n2-highmem-16 (128 GB)** — stop the spill; sized for 73k–220k-sample partitions |
| vCPU | 64 | **256–384** (push to the AoU vCPU quota; resolve the cap that blocked the original 24-worker build) |
| Master | n2-standard-16 (crashed) | **n2-highmem-16** — the dense-scratch phase destabilized a 64 GB master |
- Even at 384 vCPU + no spill (~12× throughput), the **normal/medium/large regions become tractable** (region_00006 ≈ ~40 min), but **xlarge stays ~15 hr/cell** → still needs splitting (#2).

### 2. Split the xlarge regions (the structural fix — solves compute + scratch + driver stability)
- ~16 xlarge cells (span >50 Mb / n_var >~300k: `00040, 00120, 00145, 00161, 00060, 00146, 00111, 00088, 00149, 00002, 00143, 00067, 00108`, …).
- Split each into sub-regions of a tractable size (≤~75–100k variants each → ≈ region_00006-scale). `region_00040` (615k var) → ~6–8 sub-regions.
- **Drop cross-sub-region LD beyond the 50 Mb radius** — it's ≈0, and this is *already* the accepted/documented treatment (WAVE-2 HIGH-3: long-range LD≈0 / full-radius intractable; downstream treats xlarge as 50-Mb-banded). Splitting just formalizes a decision already on the books.
- Each sub-region's dense intermediate shrinks with n_var² → no 65 GiB+ scratch, no driver crash, tractable wall-time.
- **Touches:** `src/python/build_ld_region_manifest.py` (region set), `compute_region_ld` / `_route_region_path` (routing), the downstream `ld_npz_to_rds.R` assembly (banded block-diagonal stitch).

### 3. Redo the Wave-2 cost model
The ~1,117 cluster-h estimate predates this real-sample data point and is almost certainly **low** for the xlarge cells. Re-derive from real per-region rates measured on the sized cluster (a single representative region at real sample counts), THEN price the 322-cell production. EUR (220k samples) is ~3× AFR per block — weight accordingly.

## What is NOT in question (don't relitigate)
- The **A.3 fix is correct** — `_write_a3_banded_correlation_bm` (materialize-then-band) advances blocks distributed with no driver-collect *hang*. Confirmed on the repro (130k/928s) and on region_00006 (blocks advancing before the cluster gave out). The problem is **capacity**, not the fix.
- **Ordering A vs B is settled** (keep A) — banded==dense under the span+500kb radius scheme, so B saves nothing; splitting (#2), not re-ordering, is what shrinks the dense intermediate.
- **Cohorts are intact** — mt_afr_qc.mt / mt_eur_qc.mt / mt_afr_pca_selfid_qc.mt untouched; read-gate + bucket wiring proven (AFR 73,122 / EUR 220,098 read live).

## State at handoff
- dev-10 KILLED, 0 regions completed, orphan dense scratch (`…/ld/AFR_aou/bm/m2_region_00006.corr_scratch.bm`, 520 objects ~65 GiB) DELETED, cluster `20260617` STOPPED (billing halted; synced repo + hail==0.2.135 preserved if the boot disk persists — else re-sync via GitHub ZIP).
- The 3 prep landmines (symlink `~/coloc_analysis`, pin `WORKSPACE_BUCKET`, `os.chdir` before the loop) still apply to any re-fire — see HANDOFF.json.
