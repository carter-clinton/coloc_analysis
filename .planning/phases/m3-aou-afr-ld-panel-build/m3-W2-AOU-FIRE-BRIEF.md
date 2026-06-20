# m3-02c AoU Fire Brief — Task 3 (preflight + cost probe), OPTION B

**Generated:** 2026-06-20 · **Branch/commit to clone:** `m3-W2-aou-deltas` @ origin tip (≥ this commit) · **Authorized by:** Carter (option B).

This is the self-contained runbook for the **Workbench-side** execution of m3-02c Task 3.
The NCSU session **cannot** run this (VPC-SC walls the data plane; the highmem cluster must be
provisioned in the Workbench UI). Operating manual = the `aou-ld-pipeline` project skill;
authoritative task spec = `m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md` Task 3.

---

## OPTION B flow (what Carter chose)

```
provision sized cluster → STEP 0 (landmines + quota re-check + Q-RS2 cell)
   → STEP A: cheap preflight COUNT pass over every dev cell → m3-W2-preflight-counts.tsv
   → ⏸ STOP THE CLUSTER  (no idle billing while Carter reviews the counts)
   → Carter reviews counts, gives the STEP-B go
   → RESTART cluster → STEP B: ≥3 billable LD-compute cells (cost-controlled) → m3-W2-cost-probe.tsv
   → STEP C: GUARANTEED shutdown + verify → m3-W2-cluster-shutdown.md
   → commit + push the 3 artifacts; ping NCSU "probe-recorded"
```

The **STOP between STEP A and STEP B is mandatory in this option** — it is the whole point of B
(review the preflight counts without paying ~$25–30/hr idle). Restarting a stopped cluster resumes
it at its saved size in a few minutes.

---

## STEP 0 — provision + pre-flight (re-apply on the fresh cluster)

1. **Provision the sized cluster IN THE WORKBENCH UI** (not `wb cluster start` — that only resumes a
   saved size, and the saved clusters are wrong: one is the *small A3 repro* (do-NOT-start), the other
   `20260617` is standard-family `n2-standard`):
   - Compute type: **Dataproc "Hail Genomics Analysis"** (Verily software-framework = HAIL; Hail
     pre-installed + YARN-wired — do NOT pick the generic "JupyterLab Spark cluster" = no Hail).
   - **Master `n2-highmem-16`**, **workers 24× `n2-highmem-16`** (128 GB each — stops the spill),
     **non-preemptible**, region **us-central1**. vCPU = `min(granted, 400)` = **400**.
   - Confirm in the env panel: workers are **n2-highmem** (NOT n1-highmem) and region == us-central1.
2. **Belt-and-suspenders quota re-check** (Console value can lag; run from the cluster terminal):
   ```bash
   PROJECT=$(gcloud config get-value project 2>/dev/null)   # expect wb-perky-corn-6639
   gcloud compute regions describe us-central1 --project="$PROJECT" \
     --flatten="quotas" --filter="quotas.metric=N2_CPUS" \
     --format="table(quotas.metric, quotas.limit, quotas.usage)"
   ```
   Expect limit ≥ 400. (Grant already recorded in `m3-W2-quota-grant.md`.)
3. **The 3 prep landmines** (SKILL.md "Fresh-clone re-run checklist"):
   - `git checkout m3-W2-aou-deltas` (**NOT main**) → `git pull` → `git checkout -f`
     (the Workbench nbformat filter re-dirties notebooks).
   - **symlink** `~/coloc_analysis` → the synced repo (a cell imports from `~/coloc_analysis`).
   - **`os.chdir(~/coloc_analysis)`** before the per-region loop.
   - **WORKSPACE_BUCKET hard pin** is now BAKED into `AOU-2_per_region_ld.ipynb` cell idx 5
     (260619-vcp): it hard-assigns `gs://rw-migration-aou-rw-476cdac2` and asserts `cloned-mybucket`
     is absent — just confirm the cell echoes the canonical bucket and does NOT halt.
4. **`USE_DEV_SUBSET = True`** (drives the per-region loop off `config/ld_regions_dev.tsv` —
   the 15-cell probe subset, NOT the 434-row production fire).
5. **Q-RS2 executor cell** (cores=2 / 24g executor / 10g overhead / 24g driver) runs **BEFORE** the
   pyspark/hail import; set `PYSPARK_SUBMIT_ARGS` (NOT `hl.init(spark_conf=...)` — silently overridden
   on YARN). Confirm it bound by printing `PYSPARK_SUBMIT_ARGS`.

---

## STEP A — preflight COUNT pass (cheap, in-perimeter; BEFORE any cost projection)

Run a **count-only** pass (filter the cohort MT to each compute WINDOW + Hail `count_rows`;
**NO correlation compute**) over **every** cell in `config/ld_regions_dev.tsv` (15 rows).
Write `m3-W2-preflight-counts.tsv` with columns:

```
region_id  ancestry  region_class  window_span_mb  n_var  routed_path  est_block_count  est_output_gib  over_threshold
```

- `routed_path` = the **REAL** `_route_region_path(region_class, window_span_mb)` (A.1/A.2/A.3 on the
  **WINDOW** span, not the core span).
- `est_block_count` = `ceil(n_var/4096)^2 / 2` (banded → in-band block count).
- `est_output_gib` = banded nnz × 4 bytes / 1e9.
- `over_threshold` = `(n_var > 75000)`.

### HLA coverage — **143 + 145** (this corrects a stale plan reference)
The plan prose names "HLA `region_00145`", but on the **current** (rqs-regenerated) manifest that ID is
chr6 **68–170 Mb (6q)** — *not* the MHC. The real **MHC / 6p21 (chr6 28–34 Mb)** lives in
**`m2_region_00143`** = chr6 **14.5–58.5 Mb**, which is **`class=large`, `n_sub=1` — a 43.9 Mb UNSPLIT
whole region.** The dev manifest now counts **both** (already added on NCSU):
- `m2_region_00143` (AFR + EUR) — **the real MHC**. Almost certainly `over_threshold == True`.
  **➜ This is the key STEP-A finding: if over_threshold, FLAG it for AUTO-SPLIT before m3-04**
  (re-run `build_ld_region_manifest` / the m3-02b split with a lower `--max-subregion-span-mb`, e.g. 7,
  for chr6). **Do NOT compute-fire `region_00143` whole in STEP B** — a 44 Mb A.3 matrix is exactly the
  blowup the probe exists to expose.
- `m2_region_00145__sub00` (AFR + EUR) — the plan's literal reference (medium, ~19 Mb window).
- Label the MHC row's notes with `HLA`/`MHC` so the row is unambiguous.

Auto-split or FLAG **any** cell with `over_threshold == True` before the cost model (Task 4) consumes it.

---

## ⏸ STOP THE CLUSTER (option B)

After STEP A's TSV is written:
```bash
# from the cluster terminal, or wb cluster stop <id>, or the AoU env Stop-Cluster control
gcloud dataproc clusters stop <CLUSTER_NAME> --region us-central1
```
Confirm the env panel shows **no running cluster** ($0 idle). Carter reviews
`m3-W2-preflight-counts.tsv` and gives the STEP-B go. **Then restart** the same cluster (resumes at the
saved 400-vCPU size).

---

## STEP B — fire ≥3 billable probe cells (with EXECUTABLE cost controls)

**Encode these hard controls in the probe loop BEFORE firing (code, not prose):**
- `MAX_WALL_MIN_PER_CELL = 90` — if a cell exceeds it, **KILL** the job (cancel the Spark stage /
  interrupt the cell) and record `any_spill`/timeout.
- `MAX_PROBE_CREDIT_USD = 60` — track elapsed cluster-hours × rate; if running spend exceeds the cap,
  **STOP** firing further cells and shut down.
- **SPILL/OOM KILL** — if executor spill bytes > 0 at cores=2 **or** an OOM is observed: record it, set
  the production projection to cores=1, and (if OOM) kill + re-fire that cell once at cores=1.

**Mandatory cells:**
1. **WHOLE medium** `m2_region_00006` (AFR, ~122,678 var, 17.7 Mb) — direct comparability with dev-10.
2. **xlarge SUB-REGION** `m2_region_00040__sub00` (AFR, window ~core+buffer) — proves the split makes
   the worst region tractable.
3. **MANDATORY EUR SUB-REGION** `m2_region_00040__sub00` (EUR, 220,098 samples) — the spill-risk + cost
   driver; the EUR/AFR factor is **MEASURED** here, not assumed 3.01×. **Do NOT skip this cell.**
4. **HLA (optional compute):** if you want a measured HLA compute point, fire `m2_region_00145__sub00`
   (AFR, medium) — cheap. Otherwise accept STEP A's HLA counts as the HLA input and note it.
   **`region_00143` stays count-only** (see above).

**Validate the executor config on the probe:** watch for executor spill at cores=2, especially on EUR.
If EUR spills, record it and set the production config to cores=1 (record which cores value the
projection assumes).

**DATA-LAYER VERIFY each fired cell (D-M3-10 — `_SUCCESS` is NOT evidence):**
`gsutil du -s` the produced `.npz`/`.bm` under
`gs://rw-migration-aou-rw-476cdac2/ld/{AFR_aou,EUR_aou}/` (must be ≫ 0) **AND** a Hail/np read-back
count, before recording the cell complete.

**Write `m3-W2-cost-probe.tsv`** (one row per fired cell) with EXACTLY:
```
region_id  ancestry  region_class  n_var  block_count  stage4_wall_min  end_to_end_wall_min  blocks_per_min  peak_executor_mem_gib  any_spill  cluster_vcpu  n_workers  cluster_hours
```
- `blocks_per_min = block_count / stage4_wall_min`
- `end_to_end_wall_min` = FULL cell wall incl. filtering / count_rows / variant collection / checkpoint
  / writes / sidecars / retries (NOT just Stage-4).
- `cluster_hours = (end_to_end_wall_min / 60) × (n_workers + 1)` — **MASTER-INCLUSIVE**.
- Capture `peak_executor_mem` + `any_spill` from the Spark UI; tag each row by (ancestry, region_class).

---

## STEP C — GUARANTEED shutdown + verification artifact

After the probe (or on any cost-control trip): **STOP the cluster** and write
`m3-W2-cluster-shutdown.md` carrying:
- the stop command + **its output**,
- the timestamp,
- the cluster state == **STOPPED/DELETED** confirmation,
- a **$0 / idle billing check** (env panel shows no running cluster).

A prose "I stopped it" does **not** satisfy this — the artifact must carry the stop confirmation +
the idle-billing check.

---

## Hand-back to NCSU

1. Commit the 3 artifacts with **explicit paths** (never `git add -A` on the shared tree):
   ```
   .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv
   .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv
   .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md
   ```
2. `git push` from the AoU side.
3. Ping the NCSU session **"probe-recorded"** → NCSU pulls, then builds + runs Task 4
   (`redo_ld_cost_model.py`): real-count extrapolation, 3 separate totals, master-inclusive
   end-to-end cluster-hours, contingency + egress projection, and the
   `PROJECTED × 1.3 ≤ BUDGET_CAP_CLUSTER_H` go/no-go gate → `m3-W2-budget-redo.md`.

---

## Acceptance (what Task 3 is checked against)

- `m3-W2-preflight-counts.tsv`: header has `n_var, routed_path, est_block_count, over_threshold`;
  ≥ 4 data rows; ≥ 1 HLA row (`region_00145` / `region_00143` tagged `HLA`/`6p21`/`MHC`).
- `m3-W2-cost-probe.tsv`: header has `region_id, ancestry, region_class, block_count, blocks_per_min,
  end_to_end_wall_min, cluster_hours`; ≥ 3 data rows incl. **EUR**, `m2_region_00006`,
  `m2_region_00040__sub00`; `any_spill` column present.
- `m3-W2-cluster-shutdown.md`: contains the stop confirmation **and** the $0 / idle-billing check.

## Do-NOT list

- Do NOT start the **small A3 repro** cluster (wrong size).
- Do NOT compute-fire `region_00143` whole (44 Mb MHC — count-only; flag for auto-split).
- Do NOT skip the mandatory **EUR** cell — it is the load-bearing cost input.
- Do NOT `git add -A` on the GPFS tree — explicit paths only.
- Do NOT leave the cluster running between STEP A and STEP B (option B requires the stop).
