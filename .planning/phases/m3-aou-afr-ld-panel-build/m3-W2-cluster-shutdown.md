# m3-W2 cluster shutdown — 20260604

**stop_command:** `gcloud dataproc clusters stop jupyterlabsparkclusterforaouspark20260604 --region us-central1`
**stop_initiated:** 2026-06-22 19:35:13 UTC
**state_confirmed:** STOPPED (Apps panel; "Start" button shown — only stopped clusters show Start)
**idle_cost:** $0 (Apps panel "Current cost: --")
**confirmed_at:** ~2026-06-22 19:40 UTC

All other clusters also Stopped (20260605, AoU_Jupyter_ComputeEngine_20260608). Meter OFF.

## STEP B (minimal EUR probe) outcome — the load-bearing findings

The single EUR cell `m2_region_00040__sub00` (78,730 var, A.3 banded correlation) was fired on
20260604 (n2-standard-16 ×24, 64 GB, executor cores=1 / 11g / 3g) and **interrupted at ~56 min**
(Option 1, per the 90-min wall control) — it was write-bound, NOT failed.

- **ZERO spill** — memSpill=0 / diskSpill=0 across **every** stage incl. the correlation matmul
  (STAGE 18, 1080 tasks, completed ~16 min) and the write (STAGE 19). This **overturns the
  pre-probe fear** that a single EUR block-pair (~14 GiB assumed) wouldn't fit a ~15 GB executor.
  → **64 GB HAIL clusters at cores=1 are viable for EUR (no spill).**
- **Master stable** ~48 GB available throughout the ~25 GB dense-correlation checkpoint — **no
  dev-10 master-OOM**.
- **Bottleneck = the A.3 write (STAGE 19), not memory/matmul.** Matmul finished clean in ~16 min;
  the write was at **4/400 tasks in ~26 min** at interrupt (slow ~14-min waves) → projected well
  past 90 min. Real data was landing (`gs://rw-migration-aou-rw-476cdac2/ld/EUR_aou/bm/m2_region_00040__sub00.corr_scratch.bm/parts/`
  grew 0 → ~119 MB before interrupt). This is the CR-01 / ordering-A dense-write territory.

## Caveats on m3-W2-cost-probe.tsv (PRELIMINARY)

- 1 row, `status=INTERRUPTED_write_bound`. The cell did **not** complete, so there is **no clean
  end-to-end `blocks_per_min`** (NA) — the write bottleneck was never fully sampled.
- `peak_executor_mem_gib=NA` (not transcribed from the Spark UI before the master gateway tore down);
  but `any_spill=False` bounds it ≤ the 11 g executor heap.
- `block_count=200` = the STEP-A banded estimate; the write stage materialized as 400 tasks.
- `stage4_wall_min=16` (matmul); `end_to_end_wall_min=56` (partial, at interrupt);
  `cluster_hours=23.3` (partial = 56/60 × 25, master-inclusive).
- **A finalizable cost rate needs a COMPLETING cell on a properly-sized (re-split) region** — see the
  replan note in STATE.md. This artifact is a preliminary datapoint, not the go/no-go cost basis.

## Provenance note

`m3-W2-cost-probe.tsv` was written live on 20260604 but the master gateway tore down during the stop
before it could be git-committed; it survives on the cluster's persistent disk. The committed copy here
was **reconstructed on NCSU from the measured values reported during the run** (faithful to the Spark-UI
observations above). If the exact on-disk bytes are ever needed, they are recoverable on the next start
of 20260604.
