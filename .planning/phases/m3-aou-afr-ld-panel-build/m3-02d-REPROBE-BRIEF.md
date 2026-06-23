# m3-02d Task 4 — in-perimeter RE-PROBE brief (completing AFR+EUR cells, ordering A vs B)

**Generated:** 2026-06-22 · **Updated:** 2026-06-23 (v2 — see UPDATE block) · **Clone target:** `m3-W2-aou-deltas` @ origin ≥ `31d6e6c` · **autonomous: false (COSTS MONEY).**

This is the Workbench-side runbook for m3-02d Task 4. Tasks 1–3 (NCSU code) are DONE + pushed:
per-ancestry buffer (AFR 3 Mb / EUR 5 Mb, core 5 Mb) regenerated the manifests, ordering-B A.3 write
landed, `redo_ld_cost_model.py` built. The prior m3-02c probe's `cost-probe.tsv` is INTERRUPTED/partial
(no clean rate) — **this re-probe replaces it with COMPLETING cells.** Authoritative spec = the m3-02d
PLAN Task 4. Operating manual = `aou-ld-pipeline` skill. (Supersedes the cluster section of
`m3-W2-AOU-FIRE-BRIEF.md`.)

## ⚠ UPDATE 2026-06-23 (re-probe v1 fired; this is now the v2 brief)
The first re-probe (committed `210e66c`) delivered **only a partial result** — read this before re-firing:
- **EUR `m2_region_00040__sub01` (60,606 var, A.3 ordering-B): COMPLETED** — 4.85 blocks/min, 0 spill,
  15.6 GiB banded `.bm`, read-back OK. **BUT it ran 180.6 min — blew the 90-min/cell cap** (the A.3
  write is a slow long-tail). It completed on its own between polls.
- **AFR `m2_region_00040__sub00` (64,176 var): INTERRUPTED** — it **routed to A.2** (span 7.93 Mb ≤ 10 Mb)
  and OOMed the driver in `to_numpy()` (float64 dense collect 32.9 GB ≫ 11 GiB heap). **NO AFR rate.**
- **ROOT-CAUSE FIXED on NCSU (`31d6e6c`):** `_route_region_path` now has a **density-axis OOM veto** —
  any A.1/A.2 cell whose `n_var²×8` dense collect exceeds 40% of the driver heap (n_var > **24,301**) is
  demoted to **A.3**. After `git pull ≥ 31d6e6c`, the AFR `__sub00` cell (and ~100 other dense-narrow
  cells) **routes A.3** automatically and will complete like the EUR cell did.

**v2 goal = get the missing CLEAN AFR completing rate** (and re-confirm EUR), so Task 5 has a real
AFR reference. Two changes from v1:
1. **RAISE the per-cell wall cap to ≥ 200 min** (or remove it) — the A.3 write long-tail means a
   completing cell legitimately exceeds 90 min; the v1 cap would kill a cell that is healthily writing.
   Confirm 0 spill + steady block progress instead of wall-clock-killing. (Carter sets the $ cap.)
2. The AFR cell now routes A.3 (was A.2). **There is no ordering-A comparison to run** — A.3 is hard-locked to ordering B at this HEAD (A was retired as hang-prone). Fire AFR ordering B only. See the ⚠ note in STEP B.

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
1. `cd ~/coloc_analysis && git pull && git checkout -f && git rev-parse HEAD`  (≥ `31d6e6c` — includes the density-veto routing fix)
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

## STEP B — fire the COMPLETING AFR cell (cost controls: ≥200 min/cell — see v2 UPDATE, ~$ cap Carter sets, spill/OOM kill)

**⚠ ORDERING A IS RETIRED — do NOT attempt it (v2.1 correction, 2026-06-23).** At HEAD ≥ `31d6e6c`,
`compute_region_ld`'s A.3 branch is hard-locked to **ordering B** (band via `sparsify_row_intervals` →
`checkpoint` → `write`), guarded by `test_a3_band_before_checkpoint_ordering`. Ordering A (the
un-materialized matmul through the driver `ContextRDD.collect`) was deliberately removed as hang-prone;
the A-vs-B question was already decided in B's favor. **Firing "ordering A" would require re-adding the
removed hang-prone path on a billable run — do NOT do it.** The A-vs-B comparison collapses to B.

Fire **ONE** cell to **completion** and record the clean rate. **Do NOT wall-clock-kill a cell that is
writing with 0 spill + steady block progress** — the A.3 write is a legitimate long-tail (v1 EUR took
180 min). Kill only on spill / OOM / a stalled block counter.
1. **AFR** core5/buf3 sub-cell (`m2_region_00040__sub00` AFR, 64,176 var — routes **A.3** post-fix) —
   **ordering B** (the only supported A.3 ordering). **This is the whole point: the v1-missing clean AFR rate.**
2. **EUR re-confirm — SKIP (optional).** v1 already captured a clean EUR-B rate (`m2_region_00040__sub01`,
   4.85 blocks/min, COMPLETED). With both AFR-B and EUR-B, Task 5 upgrades from the 3.01 *assumed* factor
   to a **measured** EUR/AFR factor. Only fire EUR if budget is ample and you want the same-geometry pair.
For the AFR cell: watch spill (expect 0) + capture `block_count`, `stage4_wall_min`, `end_to_end_wall_min`,
`blocks_per_min`, `peak_executor_mem_gib`, `any_spill`. **DATA-LAYER VERIFY** (D-M3-10): `gsutil du -s`
the `.bm` (≫ 0) + a read-back — `_SUCCESS` is NOT evidence.

**RECORD `m3-W2-cost-probe.tsv`** (REPLACE the interrupted file) — header + one COMPLETED row per fire,
`ordering` column = **B**, `status=COMPLETED`:
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
- Do NOT attempt ordering A — it's retired/hang-prone and would need a source edit on a billable run (see STEP B ⚠).
- Do NOT `git add -A`. Do NOT cross the perimeter from NCSU.
