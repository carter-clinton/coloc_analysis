# m3-02d Task 4 — in-perimeter RE-PROBE brief (completing AFR+EUR cells, ordering A vs B)

**Generated:** 2026-06-22 · **Clone target:** `m3-W2-aou-deltas` @ origin ≥ `19fb1e3` · **autonomous: false (COSTS MONEY).**

This is the Workbench-side runbook for m3-02d Task 4. Tasks 1–3 (NCSU code) are DONE + pushed:
per-ancestry buffer (AFR 3 Mb / EUR 5 Mb, core 5 Mb) regenerated the manifests, ordering-B A.3 write
landed, `redo_ld_cost_model.py` built. The prior m3-02c probe's `cost-probe.tsv` is INTERRUPTED/partial
(no clean rate) — **this re-probe replaces it with COMPLETING cells.** Authoritative spec = the m3-02d
PLAN Task 4. Operating manual = `aou-ld-pipeline` skill. (Supersedes the cluster section of
`m3-W2-AOU-FIRE-BRIEF.md`.)

## Goal
Fire **completing** properly-sized cells → clean `blocks_per_min` for an AFR and a EUR cell, comparing
**ordering A vs ordering B** write wall-clock (B's banded scratch should be ~7× smaller now that
radius≪span). Feed the completing rates into `redo_ld_cost_model.py` (Task 5) → GREEN/RED go/no-go.

## Cluster (the probe PROVED this works)
- **START the existing HAIL cluster `20260604`** (n2-standard-16 ×24, 64 GB, framework=HAIL) via the
  **Apps-panel Start** (NOT gcloud; NOT 20260620/20260617). NO n2-highmem (uncreatable; unnecessary —
  0 spill measured). NO quota ticket.
- Executor config = **cores=1 / executor.memory=11g / memoryOverhead=3g / driver.memory=11g**
  (14336 MB < the 15564 MB YARN container cap). This is the config that ran EUR with 0 spill. Set
  `PYSPARK_SUBMIT_ARGS` BEFORE the hail import; restart the kernel if a prior import bound a stale config.

## STEP 0 — sync + pre-flight
1. `cd ~/coloc_analysis && git pull && git checkout -f && git rev-parse HEAD`  (≥ `19fb1e3`)
2. Confirm Hail: `python3 -c "import hail; print(hail.__version__)"` → 0.2.135; `which hailctl`.
3. Bucket pin echoes `gs://rw-migration-aou-rw-476cdac2`, no halt. `USE_DEV_SUBSET=True`.
4. Load MTs (AFR 73,122 / EUR 220,098).

## STEP A — re-run preflight on the REGENERATED dev manifest (cheap, count-only)
Run `write_preflight_counts` over `config/ld_regions_dev.tsv` → `m3-W2-preflight-counts.tsv`
(overwrites the old one). **Confirm cells now clear the RE-DERIVED thresholds** (m3-02d retired the
75k-var memory proxy): `est_block_count ≤ WRITE_BLOCK_THRESHOLD (150)` AND
`est_output_gib ≤ OUTPUT_GIB_THRESHOLD (10)` → `over_threshold == False` for the probe cells.
Expect AFR core5/buf3 ≈ 80k var / ~109 banded blocks / ~7 GiB; EUR core5/buf5 ≈ 60k var / smaller.

**HLA caveat (executor-flagged):** the dev selector's chr6 slot resolves to `m2_region_00143`, NOT
`m2_region_00145`. region_00145's `__sub` rows ARE in the full `config/ld_regions.tsv` (buffer 3M AFR /
5M EUR) but are not auto-selected into the dev subset. For the mandatory HLA preflight, pull
region_00145's sub-rows from the FULL manifest and include them in the STEP-A count. If any HLA sub-cell
still exceeds the thresholds, finer-split chr6 (`--max-subregion-span-mb 3`) before m3-04 (per the plan's
T-M3RS2-HLA-01).

## STEP B — fire COMPLETING cells (cost controls: 90 min/cell, ~$60 cap, spill/OOM kill)
Fire each to **completion** (they're small enough now) and record the clean rate:
1. **AFR** core5/buf3 sub-cell (e.g. `m2_region_00040__sub00` AFR at the new geometry) — **ordering A**.
2. **same AFR cell — ordering B** (band-before-checkpoint) → compare write wall-clock vs A.
3. **EUR** core5/buf5 sub-cell (`m2_region_00040__sub00` EUR) — **mandatory** (the cost driver); ordering
   B (and A if budget allows) → the measured EUR/AFR factor.
For each: watch spill (expect 0) + capture `block_count`, `stage4_wall_min`, `end_to_end_wall_min`,
`blocks_per_min`, `peak_executor_mem_gib`, `any_spill`. **DATA-LAYER VERIFY** each (D-M3-10): `gsutil du -s`
the `.npz`/`.bm` (≫ 0) + a read-back — `_SUCCESS` is NOT evidence.

**RECORD `m3-W2-cost-probe.tsv`** (REPLACE the interrupted file) — header + one COMPLETED row per fire,
add an `ordering` (A/B) column + `status=COMPLETED`:
`region_id  ancestry  region_class  n_var  block_count  stage4_wall_min  end_to_end_wall_min  blocks_per_min  peak_executor_mem_gib  any_spill  cluster_vcpu  n_workers  cluster_hours  ordering  status`
(cluster_vcpu=384, n_workers=24, cluster_hours = end_to_end_wall_min/60 × 25.)

## STEP C — guaranteed shutdown + verify
STOP `20260604`; write `m3-W2-cluster-shutdown.md` (stop output + timestamp + STOPPED + $0 idle).
Commit + push (explicit paths) the refreshed `m3-W2-preflight-counts.tsv` + `m3-W2-cost-probe.tsv` +
`m3-W2-cluster-shutdown.md`. Ping NCSU **"reprobe-recorded"**.

## Then (NCSU, Task 5)
`redo_ld_cost_model.py` runs on the COMPLETING rates (it rejects INTERRUPTED/NA rows) →
`m3-W2-budget-redo.md` with the `PROJECTED × 1.3 ≤ BUDGET_CAP` GREEN/RED disposition. 322-cell
production stays in m3-04.

## Do-NOT
- Do NOT start 20260620 (no Hail) or 20260617 (16 GB, not HAIL).
- Do NOT use cores=2 (won't fit the 15564 MB container cap) — cores=1/11g/3g.
- Do NOT skip the mandatory EUR cell. Do NOT `git add -A`. Do NOT cross the perimeter from NCSU.
