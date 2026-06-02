# Tiered cheap-first AoU chr22 validation runbook (m3-W2)

**Quick task:** 260601-u1b
**Predecessor:** 260601-cca (env-derive AUX base + suffix-discovery)
**Status:** repo artifact — launches NOTHING, spends NOTHING. Carter holds every
launch / compute / $ trigger.

This runbook gates the AoU AFR/EUR LD-panel platform validation into a
**tiered, cheap-first sequence** so the m3-W1 empty-MT catastrophe ($2,140 burn
producing 0x0 schema-only MTs) fails **as cheaply and as diagnostically as
possible** BEFORE the expensive full-genome rebuild is greenlit.

---

## 0. Cluster provisioning — READ FIRST (2026-06-02, web-verified, high-confidence)

**Use the Hail-preinstalled cluster — do NOT pip-install Hail.** AoU RW 2.0
(Verily Workbench) offers a dedicated **"Hail Genomics Analysis"** cloud
environment (Verily backend: a Dataproc cluster with **`software-framework =
HAIL`**) where **Hail is pre-installed and correctly YARN-wired**. Pick that and
the entire pip / Spark-version problem disappears.

> The generic **"JupyterLab Spark cluster for AoU (Dataproc)"** is the
> `software-framework = NONE` variant — **no Hail bundled.** That was the
> 2026-06-02 blocker (a 64-vCPU NONE cluster was spun, found Hail-less, and
> deleted). Do **not** pick it.

**Cluster spec (all tiers):**
- Worker **Machine type: `n2-standard-16`** — Verily's Dataproc UI lists ONLY the
  `n2-standard` family (NO `n1-highmem`). Gate A+B = **4× n2-standard-16 = 64 vCPU**;
  Gate C = **24× n2-standard-16 = 384 vCPU**. Secondary/preemptible workers **0**.
- Standard-memory node is fine: the `PYSPARK_SUBMIT_ARGS` lever (Cell 1a)
  **forces `spark.executor.memory=5g`** regardless of node family, so YARN
  memory-binds to ~9-10 executors/node at 5g (some cores idle) — the per-executor
  1-core/5g catastrophe profile is **preserved**, NOT downgraded to 3.5-4 GB.
- Image (if a selector appears): **Dataproc 2.2 (Spark 3.5)** — matches the bundled
  Hail 0.2.135. (Dataproc 2.1 = Spark 3.3.2 = incompatible with Hail 0.2.135.)
- **Version:** use the env's pre-installed Hail (the platform version; CHECK D =
  0.2.135). Do **NOT** pip-pin on the Hail Genomics cluster.
- **Master/driver node: `n2-highmem-4` (32 GB) minimum — `n2-highmem-8` (52 GB)
  to carry Gate C + the full fire.** The default `n2-standard-2` (8 GB / 2 vCPU)
  **OOM-kills the Hail driver during query compilation** (`__C4Compile.<init>`) —
  surfaces as `Could not find CoarseGrainedScheduler` + py4j RemoteDisconnected
  with a CLEAN hail.log (no executor-lost / no container-killed). Gate A's
  synthetic write doesn't exercise driver-side compilation; Gate B's real WGS read
  does. Master size is fixed at cluster-create → size it right up front
  (2026-06-02 finding).

**Migrated-Verily env deltas — now BAKED into AOU-0.5 + AOU-1 (Cells 1a / 1a' / 1a''),
so a fresh clone + `git pull` runs with no manual env setup:**
1. HOME is `/home/dataproc`, not `/home/jupyter` → portable `sys.path` (Cell 1a',
   `os.path.expanduser("~/coloc_analysis/src/python")`).
2. `WORKSPACE_BUCKET` NOT auto-set → Cell 1a'' `os.environ.setdefault(...)`
   (`gs://rw-migration-aou-rw-476cdac2`).
3. `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` NOT auto-set → Cell 1a'' setdefault
   (`gs://vwb-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt`;
   verified readable 2026-06-02).
4. The controlled WGS bucket is **requester-pays** → Cell 1a sets
   `spark.hadoop.fs.gs.requester.pays.mode=CUSTOM` +
   `.buckets=vwb-aou-datasets-controlled` (NAME only, **no `gs://`**) +
   `.project.id=$GOOGLE_PROJECT`. If reads still 400, the env forced
   `STORAGE_CLIENT` → add `--conf spark.hadoop.fs.gs.client.type=HTTP_API_CLIENT`.

Only `GOOGLE_PROJECT` is auto-set on this cluster. The classic AoU Hail Genomics
image pre-set all of the above in spark-defaults; the migrated Verily image does not.

**Run sequence (Gate A; same shape for B/C with the right INTERVAL + cluster):**
1. Terminal: `git clone https://github.com/carter-clinton/coloc_analysis.git ~/coloc_analysis 2>/dev/null; cd ~/coloc_analysis && git checkout m3-W2-aou-deltas && git pull origin m3-W2-aou-deltas` → confirm `git rev-parse --short HEAD` = **e0f4182**.
2. Open `AOU-0.5-mechanism-probe_template.ipynb` on the **Hail / PySpark kernel** (NOT plain Python3). Fresh kernel → run **Cell 1a FIRST**, then **Cell 1b**.
3. **Verify YARN-not-local** (paste as a new cell after 1b — the single check that prevents a silently-invalid probe; a local backend runs only on the master, defeats the cluster, and does not reproduce the distributed write):
   ```python
   sc = hl.spark_context()
   print("master   :", sc.master)                                    # MUST start 'yarn' (not 'local')
   print("appId    :", sc.applicationId)                              # 'application_...' = YARN
   print("executors:", sc._jsc.sc().getExecutorMemoryStatus().size()) # > 1
   print("exec mem :", sc.getConf().get('spark.executor.memory'))     # '5g'
   print("hail ver :", hl.__version__)                                # ~0.2.135
   ```
   `yarn` + executors>1 + `5g` → run the probe cell. `local[...]` → STOP.
4. Run the probe cell → `GATE A PASS` or a traceback (→ §2 decision rule).

**pip FALLBACK — ONLY if the wizard has no Hail option.** Cluster image MUST be
Dataproc 2.2; `<kernel sys.executable> -m pip install hail==0.2.135`; then
`pip uninstall -y pyspark` (the wheel's toy pyspark shadows the cluster Spark);
wire `<site-packages>/hail/backend/hail-all-spark.jar` onto executors via `--jars`
+ `spark.executor.extraClassPath=./hail-all-spark.jar` in PYSPARK_SUBMIT_ARGS.
Full recipe + failure modes in `[[project_aou_dataproc_hail_install]]`. This is the
rabbit hole the Hail Genomics cluster avoids.

**`wb` CLI note:** the UI cannot set Dataproc data-disk size; `wb resource create
dataproc-cluster --software-framework=HAIL ...` can — relevant for the eventual
genome-wide build, not for Gate A/B/C.

---

## 1. Purpose + rigor framing

The catastrophe is a **Hail checkpoint write-finalization failure** under
`spark.executor.cores=1` / `executor.memory=5g`: Hail's `mt.checkpoint()` writes
the `_SUCCESS` marker on **driver-side task-completion accounting** without
validating that executor tasks actually wrote row-group payloads. The
hypothesis distinguisher (`[[feedback_w1_catastrophe_hypothesis_distinguisher]]`)
resolved this in favor of the Hail-finalize-on-empty theory: both surviving MTs'
`_SUCCESS` markers predate the kill by 20h-1.8d.

**KEY VERIFIED FACT.** Partition count is **FIXED** at
`naive_coalesce(2048)` + `repartition(2048)` (`aou_ld_panel.py`, the W2 anchor)
**regardless of `interval_filter`**. So a sub-chromosomal nano-interval keeps the
**exact catastrophe-triggering 2048-partition profile** (FAITHFUL) while making
per-partition data trivial (plausibly runs on a far smaller / cheaper cluster).

**The tiers form a memory-pressure gradient:**

- A cheap tier **FAILING** definitively rules the catastrophe **IN** (a cheap
  win — we learn the rebuild will fail again without spending the full envelope).
- A cheap tier **PASSING does NOT exonerate.** Only the chr22 (Tier 2) /
  full-genome fire reaches **genome-scale memory pressure**.

> **RIGOR CAVEAT (load-bearing).** Never label a cheap-tier pass "validated."
> Label it: **"no cheap failure mode reproduced, escalating to the real test."**
> (`[[feedback_rigor_over_speed.md]]`.)

**All guards stay intact and are layered (cheapest gate first):**

1. **HARD gate (interval-agnostic):** `_assert_checkpoint_nonempty(mt, uri, *,
   phase)` raises `RuntimeError` if `count_rows()==0` or `count_cols()==0` at
   every `mt.checkpoint()` site inside `load_qc_cohort`. **UNCHANGED** by this
   task — byte-identical body (md5 `16caccec0678a9e57f38569cb3e5b801`).
2. **SOFT signal:** an **INTERVAL-scaled** `gsutil du` byte-floor
   (`_interval_scaled_du_floor(INTERVAL, base_floor_bytes=50 MB)`). Demoted from
   the old hardcoded 50 MB floor, which false-positived a ~2 Mb nano fire. The
   du-floor is diagnostic only; the `count>0` assertion is the real gate.
3. **FORENSICS:** on any Track-4 halt, `_capture_catastrophe_forensics(uri, *,
   phase)` (best-effort, never raises) captures the
   `_SUCCESS`-mtime-vs-part-mtimes hypothesis flag + MT listing + a
   `/tmp/hail.log` preserve + a Spark-REST snapshot + a
   `_forensics/<phase>_capture.json`.

---

## 2. Gate A — Tier 0 mechanism probe (`AOU-0.5-mechanism-probe_template.ipynb`)

| | |
|---|---|
| **Cluster** | 4x `n2-standard-16` = **64 vCPU** (SHARED with Tier 1) |
| **Workers** | **NON-preemptible** (spot would muddy the kill-interrupted-write hypothesis) |
| **Cost** | **~$1-3** |
| **Compute** | a synthetic `range_matrix_table(50_000, 2_000).repartition(2048)` write under cores=1/5g; ZERO source read, ZERO QC |
| **AOU-0 precheck?** | **NO** — Gate A is a compute fire, not part of the compute-free AOU-0 precheck |

**What it isolates.** ONLY the Hail checkpoint write/finalize path on a faithful
2048-partition profile — the exact step that produced the empty MTs.

**Decision rule:**

- **PASS** (synthetic MT writes with `count_rows>0`/`count_cols>0`; few-MB
  entries) -> proceed to **Tier 1 (nano) on the SAME 64-vCPU cluster**. PASS =
  "no cheap failure mode reproduced."
- **FAIL** (`_assert_checkpoint_nonempty` raises / sub-floor entries) -> the
  catastrophe is **ruled IN at the pure-write path** -> pivot Wave 2 to **1000G
  AFR** (only ~$1-3 spent). Inspect `_forensics/probe_capture.json` for the
  `hypothesis_flag`.

**Honest caveat.** A Gate-A PASS rules out **only** the pure-write-path failure
mode. It does NOT rule out memory-pressure truncation during the real QC
pipeline over genome-scale data.

---

## 3. Gate B — Tier 1 nano (`AOU-1`, `INTERVAL = "chr22:16000000-18000000"`)

| | |
|---|---|
| **Cluster** | SAME 4x `n2-standard-16` = **64 vCPU** (reuse the Gate-A cluster) |
| **Workers** | **NON-preemptible** |
| **Cost** | **~$1-3** (shares the Gate-A cluster envelope) |
| **Interval** | `chr22:16000000-18000000` — ~2 Mb, gene-dense, a strict subset of chr22 |
| **Profile** | FAITHFUL 2048-partition / cores=1,5g (partition count is fixed regardless of interval); trivial per-partition data |

**Outputs** (INTERVAL-suffixed; do NOT collide with chr22):
`mt_afr_qc_chr22_16000000_18000000.mt`,
`mt_afr_pca_selfid_qc_chr22_16000000_18000000.mt`,
`mt_eur_qc_chr22_16000000_18000000.mt`,
`cohort_summary_m3_chr22_16000000_18000000.tsv`.

**Decision rule:**

- **PASS** (all 3 cohorts non-empty; du soft-floor clears the INTERVAL-scaled
  threshold) -> **tear down the cluster** + Carter sign-off to spin the **Tier-2
  chr22 cluster**. PASS = "no cheap failure mode reproduced, escalating to the
  real test" — **NOT "validated."**
- **FAIL-empty** (`_assert_checkpoint_nonempty` raises, or du below the scaled
  floor) -> catastrophe **IN** -> pivot to **1000G AFR**. Read
  `_forensics/<phase>_capture.json` for the hypothesis flag.
- **FAIL-wedge** (Spark stall / no progress) -> escalate cluster sizing — this
  is a **real data point on the sizing requirement** per
  `[[feedback_aou_cluster_sizing_for_ld_panel]]` (load_qc_cohort demands ~3800
  containers genome-wide; a wedge on 64 vCPU informs the Tier-2 minimum, it does
  NOT by itself rule the catastrophe in).

---

## 4. Gate C — Tier 2 chr22 (`AOU-1`, `INTERVAL = "chr22"` — the default)

| | |
|---|---|
| **Cluster** | 24x `n2-standard-16` = **384 vCPU** |
| **Workers** | **NON-preemptible** |
| **Cost** | **~$35-80**, ~2h wall |
| **Interval** | `chr22` (whole chromosome) — the first tier that approaches genome-scale memory pressure |

**Outputs** (chr22-suffixed): `mt_afr_qc_chr22.mt`,
`mt_afr_pca_selfid_qc_chr22.mt`, `mt_eur_qc_chr22.mt`,
`cohort_summary_m3_chr22.tsv`.

**Decision rule:**

- **PASS** (all 3 chr22 cohorts non-empty + du clears the full base floor) ->
  **full-genome rebuild greenlit** (Wave 2; ref
  `.planning/notebooks/AOU-2-AOU-4-TRACK-4-PATTERN.md`). This is the first tier
  whose PASS carries genome-scale-pressure evidence.
- **FAIL** -> **1000G AFR safety net.** This is a **documented fallback only** —
  do NOT propose it proactively (`[[feedback_no_1000g_ld_pivot]]`); ~11
  candidate-locus `.rds` files already sit at
  `data/processed/ld_reference/AFR/`. Document the Wave 2 deviation in the OSF
  amendment trail.

---

## 5. Watchpoints

- **Orphan-kernel billing.** Browser/websocket drops leave orphan Python kernels
  + Hail JVM children burning compute + billing
  (`[[feedback_aou_websocket_drop_zombie_pattern]]`). Detect via `ps`; preserve
  `hail.log` to the bucket; kill the JVM before any re-fire.
- **Delete each Dataproc cluster the MOMENT its tier finishes.** Do not leave a
  384-vCPU cluster idle between gates. RW 2.0 has **no persistent disks** and
  Dataproc compute is bucket-first.
- **Preserve `/tmp/hail.log` on any stall.** `_capture_catastrophe_forensics`
  copies it to `gs://<bucket>/ld/_forensics/<phase>_hail.log` automatically on a
  Track-4 halt; for a wedge (no exception), copy it manually before kill.
- **NON-preemptible workers for ALL validation tiers** (A, B, C). Spot/preemptible
  muddies the kill-interrupted-write hypothesis and risks a mid-write
  preemption that looks like the catastrophe. Reserve spot for the eventual
  **production full-fire only**.
- **Carter holds every launch / compute / $ trigger.** Nothing in this sequence
  auto-fires.
- **AoU disk-type / env discipline.** Per `[[feedback_aou_disk_type_check]]` +
  `[[feedback_aou_use_persistent_disk]]`: read the env-panel disk-type label
  before any destructive env action (Dataproc clusters do not offer reattachable
  PD — bucket-first discipline applies).

---

## 6. Forensics + hypothesis distinguisher

On any Track-4 halt, the du-floor cells (AOU-1 Cells 3.5/4.5/5.5) and the
AOU-0.5 probe cell call `_capture_catastrophe_forensics(uri, phase=...)` BEFORE
re-raising. It is **best-effort and NEVER raises** — the re-raise is what halts
the cell; the capture only adds diagnostics.

It writes `gs://<bucket>/ld/_forensics/<phase>_capture.json` with a
**`hypothesis_flag`** derived from the `_SUCCESS`-mtime-vs-`entries/entries/parts/`-
part-mtimes test (`[[feedback_w1_catastrophe_hypothesis_distinguisher]]`):

| `hypothesis_flag` | meaning |
|---|---|
| `hail_finalize_on_empty` | `_SUCCESS` mtime at/after ALL part mtimes — Hail wrote the marker on driver-side accounting after the executors (the debug-doc theory; the W1 verdict) |
| `kill_interrupted_write` | at least one part mtime AFTER `_SUCCESS` — writes continued past the marker (Carter's kill-as-culprit theory) |
| `indeterminate` | listing / mtimes unavailable |

It also records the MT listing + entries-part sizes, the `/tmp/hail.log`
preserve URI, and a Spark-REST active-stages snapshot (best-effort).

> **The Track-4 patches defend against BOTH hypotheses** (the `count_rows>0` /
> `count_cols>0` assertion + the entries-dir du check catch a zero-content MT
> regardless of cause). So the distinguisher affects the **re-fire STRATEGY**
> (which platform/config to retry, or whether to pivot to 1000G), **NOT the
> patch strategy** (`[[feedback_w1_catastrophe_hypothesis_distinguisher]]`).

---

## Escalation map (cheap -> expensive)

```
Gate A (Tier 0 probe, $1-3, 64 vCPU)
   PASS -> Gate B (Tier 1 nano, $1-3, SAME 64 vCPU)
              PASS -> Gate C (Tier 2 chr22, $35-80, 384 vCPU)
                         PASS -> full-genome rebuild (Wave 2; AOU-2-AOU-4-TRACK-4-PATTERN.md)
                         FAIL -> 1000G AFR (documented fallback)
              FAIL-empty -> 1000G AFR
              FAIL-wedge -> escalate cluster sizing, then retry Gate B/C
   FAIL -> 1000G AFR (catastrophe ruled IN at the pure-write path)
```

`1000G` AFR LD is the smoke-failure **safety net only**, not the genome-wide
substrate (`[[feedback_no_1000g_ld_pivot]]`): AoU AFR WGS remains the committed
genome-wide substrate (138x power vs 1000G AFR).
