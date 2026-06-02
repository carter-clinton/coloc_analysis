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
| **Cluster** | 4x `n1-highmem-16` = **64 vCPU** (SHARED with Tier 1) |
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
| **Cluster** | SAME 4x `n1-highmem-16` = **64 vCPU** (reuse the Gate-A cluster) |
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
| **Cluster** | 24x `n1-highmem-16` = **384 vCPU** |
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
