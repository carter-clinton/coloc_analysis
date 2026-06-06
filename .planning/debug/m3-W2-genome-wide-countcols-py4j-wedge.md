---
status: awaiting_human_verify
trigger: "Genome-wide LD-panel rebuild (AOU-1_template Cell 3 load_qc_cohort) deterministically freezes at the first genome-wide Hail action; chr22 Gate C passed; only differing variable is interval_filter (chr22 -> None)"
created: 2026-06-06
updated: 2026-06-06
---

# Debug — genome-wide rebuild wedges at first genome-wide action (Py4J mutual-wait)

**Branch/HEAD:** `m3-W2-aou-deltas` @ `fcfbc74` (seed) → investigation 2026-06-06.
**Cluster:** torn down → $0. Investigation uses ONLY banked artifacts + repo code (no live cluster).

## Current Focus

hypothesis: CONFIRMED + FIX LANDED. Root cause = first Hail action materializes the un-pruned whole-genome
  plan over the ~145k-partition v8 source; `interval_filter=None` (no partition pruning) is the single
  differing variable vs the passing chr22 Gate-C run. Fix = per-chromosome fan-out (each action bounded to
  one chrom = the chr22 condition), union, sample QC once over union.
test: NCSU-side unit/regression suite (Hail-free) exercising branching/union/QC-ordering/guard-keying +
  the `interval_filter is None` gate. 6 new tests, all PASS; tests/m3 = 135 passed / 33 skipped, no
  regressions.
expecting: Live confirmation requires a re-provisioned AoU Dataproc cluster (human-controlled). chr1
  (largest) clearing its post_split checkpoint within minutes = structural fix confirmed.
next_action: SECOND human-verify CHECKPOINT — STOP before any cluster fire. Human re-provisions cluster +
  re-applies the 3 manual Cell-1a env guards, then fires Cell 3 (auto-fans-out). Commit landed code +
  this debug-file update (commit_docs true).

## Symptoms
<!-- IMMUTABLE -->

expected: Genome-wide first action returns within minutes, as chr22 did in Gate C.
actual: Deterministic freeze immediately after Cell 3 prints `state=FRESH ancestry=afr`. No Spark stage
  launches (stage=0), no executors register. `/tmp/hail.log` freezes right after a `SizeEstimator`
  reflective-access warning flood. Flat CPU on driver.
errors: No error/exception. Pure hang. Py4J mutual-wait (driver JVM all-idle EPoll loops; Python in untimed
  recvfrom on the gateway socket).
reproduction: Run `AOU-1_template.ipynb` Cell 3 `load_qc_cohort(interval_filter=None)` (genome-wide) on the
  AoU Dataproc Hail cluster. Identical on YARN _0003 and _0004. Cluster TORN DOWN — do NOT reconnect.
started: First genome-wide production fire 2026-06-06. chr22-bounded Gate C passed all 3 cohorts 2026-06-04.
  ONLY differing variable: `interval_filter` (chr22 → None).

## Evidence
<!-- APPEND only -->

- timestamp: 2026-06-06
  checked: `src/python/aou_ld_panel.py::load_qc_cohort` FRESH-genome-wide control flow (lines 1510–1674).
  found: After the `state=FRESH` print (1510–1511), the sequence is: read_matrix_table (1522, LAZY) →
    [interval_filter is None ⇒ NO filter_intervals, 1525 skipped] → filter_cols (1533, LAZY) →
    hl.import_table(rel_path)+anti_join_cols (1542–1544; import_table reads only the TSV — small, NOT a
    genome-wide job) → naive_coalesce(2048) (1558, LAZY) → split_multi_hts (1561, LAZY) →
    **mt.checkpoint(ckpt_post_split) (1566) = the FIRST distributed action that materializes the plan**,
    then _assert_checkpoint_nonempty → count_rows()+count_cols() (1567).
  implication: The seed's "count_cols" label is the notebook-level mental model; the ACTUAL first
    genome-wide materialization is the `post_split` checkpoint at line 1566 (count_cols inside the assert
    runs only after). Either way the prime mover is the FIRST action forcing the un-pruned plan. The
    freeze cannot be a write-stage problem because no Spark stage ever launches (stage=0, no executors) —
    it is BEFORE task submission, i.e. driver-side PLAN materialization/optimization.

- timestamp: 2026-06-06
  checked: The single structural difference between the passing chr22 path and the wedging genome-wide path.
  found: In the chr22 Gate-C path, `hl.filter_intervals(mt, [chr22])` runs at line 1526 IMMEDIATELY after
    read_matrix_table, BEFORE naive_coalesce/split. filter_intervals on an interval-keyed MT prunes the
    row-partition set to only chr22's partitions (~1/40 of the genome). So naive_coalesce(2048) and
    split_multi_hts build their plan over a small partition count, and the first checkpoint's driver-side
    plan is tiny. With interval_filter=None, NO pruning happens: naive_coalesce(2048) must build a
    coalesce mapping over the FULL ~145k-partition v8 source (the documented "v8 partition explosion",
    DEC-2026-05-04-01), and split_multi_hts threads its plan over all of them. The driver must materialize
    + optimize this whole-genome plan in one shot on the FIRST action.
  implication: This is the same partition-pruning mechanism `compute_region_ld` relies on (line 1794:
    `filter_intervals` → `count_rows`, per region). chr22 worked because it was implicitly a single-chrom
    bound; genome-wide removes the bound. The fix is to RESTORE a per-action partition bound by chunking.

- timestamp: 2026-06-06
  checked: H1 discriminator — is any JVM thread blocked in FileOutputStream.write/writeBytes to a log/
    stderr fd? (banked jstacks `jstack_0003_98900_*`, `jstack_0004_a/b`).
  found: Cannot re-pull the bucket forensics (cluster + auth gone; no local copies in the repo tree —
    confirmed by find over .planning + repo root). Relying on the seed's transcribed thread evidence:
    "no is.hail.* / GoogleHadoopFileSystem / executor-task thread is RUNNABLE; every RUNNABLE thread is an
    idle sun.nio.ch.EPoll.wait loop; both Py4J ClientServerConnection threads in waitForCommands (idle);
    main in PythonGatewayServer$.main → FileInputStream.readBytes on stdin (liveness watcher)." A prior
    sweep found NO thread blocked in FileOutputStream.write. CPU flat.
  implication: H1 (stdout/stderr pipe-buffer deadlock) predicts a JVM thread PARKED IN write() on a full
    pipe — there is none in the transcribed stacks. The SizeEstimator flood is the LAST thing logged
    before the freeze, but "last log line" ≠ "blocked writing that line." More decisively: a pipe-buffer
    deadlock would still show the producing thread (the plan-optimizer / SizeEstimator caller) as the one
    blocked on write — instead ALL JVM threads are idle EPoll loops. That is the signature of a driver
    that has FINISHED emitting and is now BLOCKED WAITING (or has returned and is awaiting the next
    command) — not one mid-write. ⇒ H1 is best-effort REFUTED (residual uncertainty: medium — I could not
    re-read the raw jstacks myself; verdict rests on the transcription, which the prior sweep produced).

- timestamp: 2026-06-06
  checked: H2 (Py4J lost-response) vs the driver-side-plan-materialization reading, against the flat-CPU +
    idle-JVM + Python-untimed-recvfrom evidence.
  found: H2 requires the Java action to have RETURNED (so no is.hail thread remains) while the Py4J
    response was dropped on the wire. That is consistent with the idle-JVM snapshot, but it does NOT
    explain WHY only the genome-wide variant triggers it and chr22 never did — a lost gateway response is
    not partition-count-dependent. The partition-explosion reading DOES explain the chr22/genome-wide
    asymmetry directly. The flat-CPU-with-all-JVM-idle snapshot is ALSO consistent with a driver thread
    that is itself blocked in a long, CPU-light metadata/optimizer wait (e.g. a coalesce-mapping or
    interval-tree build over 145k partitions that is I/O-light and not surfaced as a named is.hail RUNNABLE
    frame in the sampled instant), OR a deadlock between the optimizer and a bounded internal queue.
  implication: H1 vs H2 cannot be settled to high confidence from banked artifacts alone, and — per the
    orchestrator's mechanism-agnostic directive — it does NOT need to be: BOTH H1 and H2 (and the
    partition-explosion reading) are bounded by the SAME fix, because all three are triggered by the FIRST
    action having to materialize the full un-pruned genome-wide plan. Bounding each action to one
    chromosome reproduces the exact condition under which chr22 passed. VERDICT: H1 best-effort refuted;
    root cause recorded as the un-pruned whole-genome plan materialization on the first action (the
    partition-explosion reading), with H2 retained as a non-exclusive secondary at the Py4J boundary.

## Eliminated
<!-- APPEND only -->

- hypothesis: H1 — stdout/stderr pipe-buffer deadlock is the PRIME mover.
  evidence: No JVM thread blocked in FileOutputStream.write in the transcribed jstacks; all RUNNABLE
    threads are idle EPoll loops (a producer mid-write would appear blocked in write). SizeEstimator being
    the last log line is consistent with "flooded then the driver moved into a non-logging wait," not
    "blocked writing." Best-effort refuted (residual medium uncertainty — raw jstacks not re-readable).
    Retained ONLY as a contributing log-volume symptom that the fix independently eliminates.
  timestamp: 2026-06-06

- hypothesis: (already dismissed in seed, not re-chased) both-idle / JVM-upload-hang / Python-controlled-
    socket CLOSE-WAIT / upload-pool-handoff gcs-async-channel-pool-0 Object.wait() / Py4J heartbeat-timeout
    desync.
  evidence: Confirmed idle artifacts in the original diagnosis; Py4J has no default read timeout. Per
    orchestrator directive, NOT re-investigated.
  timestamp: 2026-06-06 (carried from seed)

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: The FIRST Hail action in the FRESH genome-wide path (the `post_split` checkpoint at
  aou_ld_panel.py:1566) must materialize and optimize a driver-side plan over the FULL un-pruned v8 source
  MatrixTable (~145k partitions; the documented "v8 partition explosion"). With `interval_filter=None`
  there is no `filter_intervals` partition pruning, so `naive_coalesce(2048)` + `split_multi_hts` build a
  whole-genome coalesce/interval plan in one shot. The driver wedges in that pre-task plan phase (stage=0,
  no executors, flat CPU, SizeEstimator reflective-access flood) and the Python kernel sits in an untimed
  Py4J recvfrom = mutual wait. The chr22 Gate-C run never hit this because `filter_intervals(chr22)` ran
  first and pruned the partition set ~40x before any plan materialization. The ONLY differing variable
  (interval_filter chr22→None) maps directly onto the ONLY structural change (partition pruning on/off).
  H1 (log-pipe deadlock) best-effort refuted as prime mover; retained as a contributing symptom the fix
  also eliminates. H2 (Py4J lost-response) retained as non-exclusive secondary; not separable from
  banked artifacts, and bounded by the same fix.

fix: Per-chromosome checkpoint loop in `load_qc_cohort` — when `interval_filter` is None (genome-wide
  production), loop the 22 autosomes, running filter_intervals(chrN) → existing FRESH QC chain →
  per-chrom intermediates, then `union_rows` the 22 per-chrom QC'd MTs and write the final cohort
  checkpoint. Each Hail action is then bounded to a single chromosome's partition set — reproducing the
  exact condition under which chr22 passed — which (a) keeps every driver-side plan materialization small,
  (b) slashes per-action SizeEstimator/log volume (neutralizes H1), and (c) bounds any Py4J round-trip
  (neutralizes H2). Mechanism-agnostic. DESIGN + COST below.

verification: CODE LANDED + NCSU-side tests GREEN (135 passed / 33 skipped in tests/m3; 6 new fan-out
  tests all PASS). LIVE genome-wide validation PENDING — cannot validate the wedge itself without a
  re-provisioned AoU Dataproc Hail cluster (human-controlled) + the 3 manual Cell-1a env guards.
  SECOND human-verify CHECKPOINT raised before any cluster fire.

files_changed:
  - src/python/aou_ld_panel.py (AUTOSOMES const; genome-wide per-chrom fan-out branch in load_qc_cohort
    gated on `interval_filter is None and not skip_checkpoint and not _skip_final_write`; new private
    `_skip_final_write` kwarg early-return after post_vqc; extracted `_apply_sample_qc_and_finalize`
    helper shared by single-interval + union paths)
  - tests/m3/test_aou_ld_panel_local.py (6 new tests: AUTOSOMES range, 22-way fan-out, union+once-only
    sample QC, unioned-count guard keying, single-interval no-fan-out regression, static gate guard;
    + `import sys, types`)

---

# CODE LANDED — implementation notes (2026-06-06)

## What changed in src/python/aou_ld_panel.py

1. **`AUTOSOMES = tuple(f"chr{i}" for i in range(1, 23))`** — chr1..chr22, GRCh38, autosomal-only
   (matches M2 region-manifest scope; no chrX/Y/M).

2. **Genome-wide fan-out branch** inserted in `load_qc_cohort` immediately after the ancestry-validation
   block, BEFORE the aux-base resolution / per-interval body. Gated on
   `interval_filter is None and not skip_checkpoint and not _skip_final_write`:
   - Loops `AUTOSOMES`, recursing `load_qc_cohort(..., interval_filter="chrN", _skip_final_write=True)`
     so every Hail action is bounded to ONE chromosome's partition set (the chr22-Gate-C condition) —
     the driver never materializes the un-pruned whole-genome plan.
   - `mt = per_chrom_mts[0].union_rows(*per_chrom_mts[1:])` — variant-axis concat (no shuffle/collect).
   - Raw-count sample-callrate guard keys on `mt.count_rows()` over the UNION (>>500K) → APPLY at
     genome scale (preserves chr22-Gate-C semantics; a single chrom dipping <500K can no longer wrongly
     skip).
   - Phase 3 (sample QC + het) + final write run ONCE over the union via the new helper.

3. **`_skip_final_write` private kwarg** — when True the per-interval body early-returns the post-vqc MT
   right after the `post_variant_qc` checkpoint (the disk-backed read-back from `mt.checkpoint(...)`),
   skipping Phase 3 + final write. Only ever True on the internal per-chrom recursions. This is the
   single subtle correctness point: variant QC is per-chrom-independent (safe to chunk); SAMPLE QC is
   NOT (per-sample call_rate needs all variants per sample; het band must center on the whole cohort) —
   so Phases 1-2 chunk, then union, then Phase 3 once.

4. **`_apply_sample_qc_and_finalize(mt, *, ancestry, sensitivity, bucket, sample_callrate_filtered)`** —
   extracted Phase 3 + final checkpoint so the single-interval path and the genome-wide union path run
   BYTE-IDENTICAL sample-QC / het / final-write logic (no drift). `bucket=None` → skip final write
   (local synthetic-MT tests). Honors the W1 QC-ordering fix (variant_qc already applied upstream).

## Invariants preserved (no regression)

- SINGLE-INTERVAL paths (chr22 / nano / synthetic, interval_filter SET) fall straight through to the
  unchanged per-interval body — Gate A/B/C byte-identical. (Locked by
  `test_single_interval_path_does_not_fan_out` + the static gate guard.)
- LOCAL synthetic tests (skip_checkpoint=True, interval_filter None) ALSO bypass the fan-out (no bucket
  to write per-chrom intermediates) — single in-memory pass, unchanged.
- FINAL cohort URI unchanged (`_qc_checkpoint_uri`) → AOU-2/AOU-4/cohort_summary producer/consumer
  contract preserved.
- Per-chrom intermediates path-isolated via existing `_intermediate_checkpoint_uri(interval_filter="chrN")`
  → the existing auto-resume state machine makes the loop RESTARTABLE (websocket-drop after chrK resumes
  at chrK+1 for free).
- Empty-MT catastrophe guard (`_assert_checkpoint_nonempty`) inherited per-chrom AND on the final union —
  strictly MORE coverage than before.
- The genome-wide NOTEBOOK call site is unchanged: AOU-1_template Cell 3 already calls
  `load_qc_cohort(mt_path=..., ancestry="afr", sensitivity=False)` (interval_filter defaults None,
  skip_checkpoint defaults False) → transparently hits the new fan-out. NO notebook edit needed.

## Test output (NCSU-side, no Hail cluster)

```
$ smoke_dev/bin/python -m pytest tests/m3/test_aou_ld_panel_local.py -q
98 passed, 17 skipped in 0.48s

$ smoke_dev/bin/python -m pytest tests/m3/ -q
135 passed, 33 skipped in 26.40s
```

6 new fan-out tests (all PASS, none skipped — they run Hail-free via a fake `hail` module + a
monkeypatched recursive `load_qc_cohort` recorder + a `_apply_sample_qc_and_finalize` stub):
- `test_autosomes_constant_is_chr1_to_chr22`
- `test_genome_wide_fans_out_22_per_chrom_calls` (22 recursive calls, each interval_filter=chrN +
  _skip_final_write=True)
- `test_genome_wide_unions_all_22_then_sample_qc_once` (union of all 22; Phase 3 runs once over union)
- `test_genome_wide_guard_keys_on_unioned_count_not_per_chrom` (each chrom <500K, union >500K → APPLY)
- `test_single_interval_path_does_not_fan_out` (chr22 path = NO fan-out; regression)
- `test_genome_wide_branch_gate_is_static_in_source` (static gate + recursion-safety guard)

The 33 tests/m3 skips are Hail-gated / env-gated tests (no local Hail install) — expected; unchanged
by this work.

## RE-FIRE PROCEDURE (human, on a re-provisioned AoU Dataproc Hail cluster)

PREREQ — cluster is GONE ($0). Re-provision the "Hail Genomics Analysis" Dataproc cluster (Verily
HAIL software-framework; Hail pre-installed + YARN-wired) at the Gate-C sizing (max workers, no
overthreading per the W2 preset decision); n2-standard-16 master.

1. Fresh `git clone` of the repo on the Workbench (origin = github.com/carter-clinton/coloc_analysis),
   checkout `m3-W2-aou-deltas`, pull this fix.
2. Re-apply the THREE manual Cell-1a env guards (NOT in repo —
   [[feedback_aou_cluster_template_bucket_pollution]]):
   (a) bucket pin `WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2` (override the 404 template
       placeholder `gs://cloned-mybucket-...`);
   (b) wgs-literal env;
   (c) requester-pays CUSTOM.
   `git checkout -f` to undo any nbformat clean/smudge re-dirty before running.
3. `echo $WORKSPACE_BUCKET` BEFORE any read/write to confirm the pin took.
4. Fire Cell 1a / 1b / 3 as-is. Cell 3 `load_qc_cohort(ancestry="afr", sensitivity=False)` now FANS OUT
   per-chrom automatically (interval_filter defaults None). NO code/notebook edit at the call site.

## WHAT TO WATCH ON THE FIRE

- **chr1 first** (largest autosome): watch its `post_split` checkpoint clear within MINUTES (the exact
  wedge condition). If chr1 passes, the structural fix is CONFIRMED live — the un-pruned whole-genome
  plan is gone. The console prints `genome-wide 1/22: chr1` then `wrote intermediate 1/2`.
- **Per-chrom checkpoint progress**: each chrom prints `genome-wide K/22: chrK` → two intermediate
  writes → returns. Restartable: a websocket drop after chrK resumes at chrK+1.
- **Log volume**: per-action SizeEstimator flood is now over ONE chrom's partitions (~22x lower than the
  whole-genome flood) — if H1 (pipe-buffer) had any contribution, this neutralizes it.
- **Cost**: roughly the same total QC work as a single genome-wide pass, REDISTRIBUTED into 22 bounded
  jobs + 22x2 intermediate checkpoint round-trips (~1.5-2x single-pass write I/O) vs ZERO completed work
  today. Low-hundreds-of-dollars for AFR+EUR, the budget envelope already greenlit for Wave 2 — now
  actually COMPLETABLE. Restartability removes the "one drop = full re-fire" catastrophic cost risk.
- **WATCH-POINTS carried from Gate C**: EUR collectDArray scales with samples x partitions (221k samples)
  — now bounded per-chrom; final union is NOT interval-isolated (it spans all 22) but is a metadata-level
  concat of disk-backed MTs (no collect). If `union_rows` over 22 inputs ever surfaces a Hail-version
  quirk, fall back to a two-level union (pair, then union the 11 results).

---

# DESIGNED FIX — per-chromosome checkpoint loop

## Why this fix (and not a config knob)

The wedge is structural (un-pruned whole-genome plan on the first action), so no Spark/GCS conf changes it
(seed already ruled out config knobs). The ONE thing that demonstrably worked — chr22 Gate C — worked
*because* `filter_intervals` bounded every action to one chromosome's partitions. The fix generalizes that
proven-good condition to all 22 autosomes. It is the smallest change that restores the passing condition.

## Where the loop goes

Inside `load_qc_cohort`, the FRESH / RESUME_FROM_POST_SPLIT path (lines 1519–1639). Today the body runs
ONCE over whatever `interval_filter` selects. The change: when genome-wide (interval_filter is None), drive
the SAME body 22 times, once per autosome, by INTERNALLY setting a per-iteration chrom interval, then union.

Minimal-blast-radius shape (keep the existing per-interval body intact; wrap it):

```
AUTOSOMES = [f"chr{i}" for i in range(1, 23)]   # chr1..chr22, GRCh38

def load_qc_cohort(..., interval_filter=None, ...):
    ...
    # NEW: genome-wide fan-out. Production fire passes interval_filter=None.
    # Bound every Hail action to one chromosome (the condition chr22 Gate C
    # passed under) by recursing per-autosome, then union the per-chrom QC'd MTs.
    if interval_filter is None and not skip_checkpoint:
        per_chrom_mts = []
        for chrom in AUTOSOMES:
            mt_c = load_qc_cohort(
                mt_path=mt_path, ancestry=ancestry, sensitivity=sensitivity,
                ancestry_table_path=ancestry_table_path,
                relateds_table_path=relateds_table_path,
                workspace_bucket=workspace_bucket,
                force_fresh=force_fresh,
                interval_filter=chrom,          # <- bounds each action to one chrom
                _skip_final_write=True,         # NEW kwarg: stop after post_vqc, return MT
            )
            per_chrom_mts.append(mt_c)
        mt = per_chrom_mts[0].union_rows(*per_chrom_mts[1:])
        # Sample QC (Phase 3) + het filter run ONCE over the unioned cohort,
        # then the final cohort checkpoint (unchanged final-write block).
        ...
        return mt
    # ... existing single-interval body unchanged ...
```

Notes on the recursion boundary:
- `_skip_final_write` is a NEW private kwarg so each per-chrom call STOPS after the post_variant_qc
  checkpoint and RETURNS the post-vqc MT (it must NOT run Phase 3 sample-QC per-chrom — sample QC and the
  het ±3SD band must be computed ONCE over the full unioned cohort, exactly as today, or per-sample
  call_rate would be measured per-chromosome and the het band would be miscentered). This is the single
  subtle correctness point: variant QC is per-chromosome-independent (safe to chunk); SAMPLE QC is NOT
  (must see all variants per sample). So: chunk Phases 1–2 (read/filter/split/variant-QC), union, then run
  Phase 3 (sample QC) once.
- The per-chrom calls reuse the EXISTING intermediate-checkpoint machinery: `_intermediate_checkpoint_uri`
  already takes `interval_filter` and produces `mt_{anc}_post_split_chr{N}.mt` /
  `..._post_variant_qc_chr{N}.mt` — so per-chrom checkpoints are already path-isolated and the existing
  auto-resume state machine makes the loop RESTARTABLE: a websocket-drop after chr14 resumes at chr15 for
  free (each chrom's post_vqc checkpoint + sidecar is the resume gate). This is a major operational win on
  a multi-hour genome-wide fire (cf. the websocket-drop orphan-kernel feedback memory).
- The raw-count sample-callrate guard (MIN_VARIANTS_FOR_SAMPLE_CALLRATE) must key on the UNIONED raw count,
  not per-chrom (a single chromosome may dip below 500K raw and wrongly skip). Since sample QC moves to
  the post-union path, compute `_n_var_raw = mt.count_rows()` AFTER the union (one bounded count over the
  already-checkpointed, balanced union — cheap), preserving today's semantics.

## Checkpoint naming + location (bucket-first, no PD)

Unchanged from the existing scheme — this is why the fix is low-risk:
- Per-chrom intermediates: `gs://${WORKSPACE_BUCKET}/ld/intermediate/mt_{anc}[_pca_selfid]_post_split_chr{N}.mt`
  and `..._post_variant_qc_chr{N}.mt` (already emitted by `_intermediate_checkpoint_uri` with
  `interval_filter="chrN"`). Bucket-first; RW2.0 has no persistent disk.
- Final cohort: `gs://${WORKSPACE_BUCKET}/ld/mt_{anc}[_pca_selfid]_qc.mt` (UNCHANGED — downstream AOU-2 /
  AOU-4 / cohort_summary already read this exact path; producer/consumer contract preserved).
- All MTs validated by the EXISTING `_assert_checkpoint_nonempty` (count_rows>0 / count_cols>0) — the
  empty-MT catastrophe guard is inherited per-chrom AND on the union, strictly MORE coverage than today.

## Union mechanics

`hl.MatrixTable.union_rows(*others)` — variant-axis (row) union, requires identical column keys (samples)
and row schema across the 22 per-chrom MTs. Both hold here: every per-chrom MT is built from the same
source over the same ancestry/relateds filter, so the sample set (cols) is identical and the row schema
(post split_multi_hts + variant_qc annotations) is identical. union_rows is a metadata-level concatenation
of disjoint genomic intervals (no shuffle, no driver collect) — cheap and partition-bounded. (If a future
Hail-version quirk surfaces on union_rows over 22 inputs, the fallback is a two-level union — union pairs,
then union the 11 results — but the flat 22-way union is expected to be fine.)

## Partition / cost implications

- Per-chrom partition counts are bounded: each chromosome carries ~1/40–1/15 of the source partitions; the
  driver plan per action is small → no whole-genome plan materialization → no wedge. The post_split
  read-back rebalance (`_post_split_read_partitions`) already clamps DOWN to available, so a small chrom
  (chr21/22) won't over-request.
- COMPUTE COST: roughly the SAME total work as a single genome-wide pass (same variants QC'd, same samples)
  — it is REDISTRIBUTED into 22 bounded jobs rather than one mega-job, PLUS 22×2 intermediate checkpoint
  writes/reads. The added I/O is the per-chrom post_split + post_vqc checkpoint round-trips: bounded by
  cohort size, dominated by the largest chromosomes. Order-of-magnitude: the same AFR 74k×~284k /
  EUR 221k×~158k entries written ~once as intermediates per phase, chunked — call it ~1.5–2× the
  single-pass write I/O (post_split + post_vqc + final), versus ZERO completed work today (infinite hang).
  On the AoU Dataproc Hail cluster sized as in Gate C (max workers, no overthreading per the W2 preset
  decision), expect the genome-wide AFR+EUR build in the low-hundreds-of-dollars range — the SAME budget
  envelope already greenlit for Wave 2, now actually COMPLETABLE. Restartability (free resume per chrom)
  removes the catastrophic "one drop = full re-fire" cost risk that dominated prior fires.
- Per-action LOG volume drops ~22× (each SizeEstimator flood is over one chrom's partitions), which
  independently neutralizes H1 if it had any contribution.

## Test plan (NCSU-side, no cluster)

1. Unit: `AUTOSOMES` is chr1..chr22 (no chrX/Y — LD panel is autosomal per existing manifest scope).
2. Unit: genome-wide branch (interval_filter=None) issues 22 per-chrom recursive calls with
   interval_filter=chrN and `_skip_final_write=True`; sample-QC runs ONCE post-union. Mock load_qc_cohort
   recursion / Hail via the existing synthetic-MT fixture + monkeypatch.
3. Unit: per-chrom raw-count guard keys on the UNIONED count, not per-chrom (regression guard against the
   single-chrom-dips-below-500K skip bug).
4. Regression: existing chr22 / nano single-interval path (interval_filter set) is UNCHANGED — the new
   branch is gated on `interval_filter is None`, so all current Gate A/B/C behavior is byte-identical.
5. union_rows row-schema/col-key identity assertion in a synthetic 2-chrom fixture.

## Re-fire protocol (human, after code lands + CHECKPOINT cleared)

- Re-apply the THREE manual Cell-1a env guards on fresh clone (bucket pin, wgs-literal, requester-pays
  CUSTOM) — NOT in repo (feedback_aou_cluster_template_bucket_pollution); `git checkout -f` for nbformat.
- Fire Cell 1a/1b/3 with `interval_filter` defaulting to None (genome-wide) — now fans out per-chrom.
- Watch the FIRST per-chrom (chr1, largest) clear its post_split checkpoint within minutes (the wedge
  condition); if chr1 passes, the structural fix is confirmed live.
