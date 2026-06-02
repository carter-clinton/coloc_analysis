---
status: awaiting_human_verify
trigger: "m3-gateb-load-qc-cohort-driver-collect: load_qc_cohort() stalls indefinitely on Hail DRIVER (SpillingCollectIterator) during Gate B chr22 smoke, instead of distributing to executors"
created: 2026-06-02T00:00:00Z
updated: 2026-06-02T00:00:00Z
---

## Current Focus

hypothesis: CONFIRMED (H1) — mt.repartition(2048, shuffle=True) at line 1334, after split_multi_hts and before checkpoint, builds a RangePartitioner by sampling keys across the surviving partitions → driver-side SpillingCollectIterator + TableValue.mapRows. Authoritative Hail-team guidance: never repartition(shuffle=True) before a write; use _n_partitions on read instead.
test: RED-first regression — extract pure Hail-free helper _post_split_read_partitions(); add (a) a static-source check (FRESH path must NOT repartition before the post_split checkpoint write) and (b) a unit test of the helper. RED on current code, GREEN after fix.
expecting: After dropping the pre-write repartition and rebalancing via read-back-with-_n_partitions, no driver gather; FRESH and RESUME both enter Phase 2 from a balanced on-disk read.
next_action: Write RED test, confirm it fails, apply Fix-B (drop repartition + checkpoint-then-reread-with-_n_partitions + named constant), confirm GREEN, run full tests/m3.

## Symptoms

expected: load_qc_cohort() filters the AoU ACAF-threshold multiMT to the requested interval, runs sample QC, writes the post-split checkpoint MT — heavy work distributed across executors. On 64-vCPU cluster the cohort build completes in minutes.
actual: load_qc_cohort() stalls indefinitely on the Hail driver. jstack of driver JVM shows active thread in SpillingCollectIterator$.apply -> TableValue.mapRows -> ExecuteRelational.execute (<- BackendHttpHandler). Spilling to local /tmp on master node. Over ~38 min driver accumulated only ~1.4s CPU, 0 active executor threads — 2,077 surviving row-partitions funneled to driver via IMPLICIT .collect() re-read from spill. NO explicit .collect() anywhere in cohort path.
errors: No exception — hang/stall, not crash. (Distinct from earlier blocker: n2-standard-2 master OOM-killed driver "Could not find CoarseGrainedScheduler" — fixed by upsizing master to n2-standard-16; CURRENT stall is on the larger master, NOT driver-heap OOM.)
reproduction: Fire Gate B = AOU-1-chr22-smoke notebook with INTERVAL='chr22:16000000-18000000' on AoU Dataproc "Hail Genomics Analysis" cluster; load_qc_cohort runs over ACAF-threshold multiMT (gs://vwb-aou-datasets-controlled/v8/.../acaf_threshold/multiMT/hail.mt, ~145,192 partitions). filter_intervals prunes 143,115 empty partitions -> 2,077 survivors, then stall. NOT reproducible NCSU-side — no Hail, no AoU data access.
started: Surfaced 2026-06-02 on first Gate B fire after Gate A (synthetic-MT write probe) PASSED. naive_coalesce(2048)+repartition(2048) introduced as "Q3 hybrid balanced-QC" remediation (DEC-2026-05-04-01 era) to tame v8 partition explosion. NOT the m3-W1 empty-MT catastrophe.

## Eliminated

- hypothesis: H3 — annotate_cols / ancestry import broadcast collects the cols-side table
  evidence: jstack frame is TableValue.mapRows (ROW side), and the spill is over 2,077 ROW partitions. A TSV import (ancestry_preds.tsv) is a handful of partitions and feeds a cols-side broadcast join (annotate_cols at 1310), not a 2,077-partition row collect. Also the het aggregate_cols (line 1357) is the ONLY explicit aggregate in the path and it is cols-side AND in Phase 2 (AFTER the post_split checkpoint where the stall hits). Row-side collect of 2,077 partitions cannot come from a col-side op.
  timestamp: 2026-06-02T00:30:00Z

- hypothesis: H4 — naive_coalesce(2048) itself collects partition boundaries
  evidence: Hail docs (official): naive_coalesce "simply combines adjacent partitions" with NO shuffle and NO rebalance — it does not sample keys or build a partitioner, so no driver gather. Distinct from repartition. naive_coalesce(2048) over a 2,077-survivor MT is a cheap local combine.
  timestamp: 2026-06-02T00:30:00Z

- hypothesis: H5a — INTERVAL is not being threaded into the load_qc_cohort filter_intervals call (pushdown failure)
  evidence: Code reading REFUTES this: notebook threads INTERVAL as interval_filter= into all 3 load_qc_cohort calls (notebook 174/255/335); load_qc_cohort applies it via hl.filter_intervals at src/python/aou_ld_panel.py:1298-1302 immediately after read_matrix_table. The interval IS applied. (The 2,077-vs-95 partition-count discrepancy is a SEPARATE observation — see Evidence/H5 note — but it does not change the stalling op, and is most consistent with Gate B having been fired at INTERVAL='chr22' whole-chrom, OR coarse position-pruning of the ACAF MT. Either way the repartition→checkpoint driver-collect is the failure.)
  timestamp: 2026-06-02T00:32:00Z

## Evidence

- timestamp: 2026-06-02T00:10:00Z
  checked: Knowledge base (.planning/debug/knowledge-base.md) for keyword overlap
  found: Two entries (qtl_coloc_snp_name_mismatch, ta_r3_w1_snp_id_overlap_zero) — both R/coloc SNP-ID convention drift bugs. ZERO overlap with Hail/driver-collect/repartition/SpillingCollectIterator. No known-pattern candidate.
  implication: Novel bug; proceed with open hypothesis testing.

- timestamp: 2026-06-02T00:12:00Z
  checked: load_qc_cohort FRESH path (src/python/aou_ld_panel.py:1293-1342) — exact op sequence
  found: FRESH ops in order: read_matrix_table(1295) -> filter_intervals(interval_filter)(1298-1302) -> [annotate_cols+filter_cols by ancestry](1305-1311) -> anti_join_cols(1317) -> [optional sensitivity filter_cols](1324) -> naive_coalesce(2048)(1327) -> split_multi_hts(1330) -> repartition(2048)(1334) -> checkpoint(ckpt_post_split)(1339). interval_filter IS threaded into filter_intervals correctly.
  implication: Confirms the prime-suspect op sequence. repartition(2048) at 1334 is REDUNDANT in count (naive_coalesce already set 2048) — exists only for size rebalance post-split. checkpoint immediately follows.

- timestamp: 2026-06-02T00:14:00Z
  checked: Gate B notebook (.planning/notebooks/AOU-1-chr22-smoke_template.ipynb) — how INTERVAL flows + reconcile 2,077 partitions
  found: INTERVAL default = "chr22" (line 144). Runbook note (lines 13-14) distinguishes Tier 1 nano (chr22:16000000-18000000, ~2Mb) from Tier 2 (chr22 whole chrom). INTERVAL is threaded as interval_filter= into all 3 load_qc_cohort calls (notebook 174/255/335). Symptoms say fired with nano INTERVAL but 2,077 surviving partitions = WHOLE-chr22 count (chr22 ~50Mb / ~21kb-per-partition ~= 2,380; a 2Mb window should leave ~95). Notebook line 13: "naive_coalesce(2048)+repartition(2048) are FIXED regardless of interval_filter" — the rebalance to 2048 happens whether nano or whole-chrom.
  implication: H5 PARTIAL: 2,077 is NOT the nano count. EITHER (a) Gate B was actually fired with INTERVAL='chr22' (whole chrom) despite the symptom header, OR (b) ACAF MT partition pruning is coarse. BUT — regardless of which interval, the op that stalls (repartition->checkpoint) is identical, and 2,077 partitions funneled to driver via implicit collect is the SAME bug shape. The interval IS applied (filter_intervals present + threaded); H5a "interval not threaded into the call" is REFUTED by code reading. Whether it was nano or whole-chrom, the driver-collect at repartition/checkpoint is the failure. Need Hail semantics to pin WHICH op lowers to SpillingCollectIterator+TableMapRows.

- timestamp: 2026-06-02T00:28:00Z
  checked: Hail official docs + Hail Discussion forum (WebSearch) for repartition/naive_coalesce semantics + SpillingCollectIterator + RangePartitioner
  found: (1) MatrixTable.repartition(n_partitions, shuffle=True) — shuffle DEFAULTS to True; with shuffle=True Hail does a FULL shuffle creating equal-sized partitions, which requires building a Spark RangePartitioner by SAMPLING the row keys across all input partitions. (2) naive_coalesce only combines adjacent partitions — no shuffle, no sampling, no partitioner rebuild. (3) Hail-team guidance (Tim Poterba, core dev): "Avoid using repartition — instead use _n_partitions on read, as repartition, especially with shuffle=True, is super slow. In general you should repartition AFTER you've written data with too many partitions, NOT before." (4) Multiple forum threads report this exact failure with ~145,000-partition source MTs (same profile as the AoU ACAF MT). (5) "Shuffling and writing a MatrixTable appears to run the shuffle op twice" — repartition(shuffle=True) immediately followed by a write double-runs the shuffle.
  implication: repartition(2048) at line 1334 uses shuffle=True (default). After split_multi_hts (line 1330) re-keys/adds rows, the carried partitioner is invalid; repartition must build a fresh RangePartitioner by sampling keys across the 2,077 surviving partitions. That key-sampling/boundary-computation is what lowers to SpillingCollectIterator + TableValue.mapRows on the DRIVER, spilling to /tmp. This is the implicit collect with no explicit .collect() in code. MATCHES the jstack exactly.

- timestamp: 2026-06-02T00:34:00Z
  checked: hl.read_matrix_table signature (Hail docs) — confirm Fix-B viability
  found: hail.methods.read_matrix_table(path, *, _intervals=None, _filter_intervals=False, _drop_cols=False, _drop_rows=False, _create_row_uids=False, _create_col_uids=False, _n_partitions=None, _assert_type=None, _load_refs=True). _n_partitions exists (internal API, leading underscore). The post_split checkpoint already exists in the path (line 1339 checkpoint, then RESUME_FROM_POST_SPLIT reads it at line 1344).
  implication: The Hail-prescribed pattern (write with current partitioning, then read back with a target partition count) is natively supported. The code ALREADY checkpoints (write+read) at line 1339 then re-reads at 1344 on resume. So the repartition is doubly redundant: naive_coalesce already set count=2048, AND the checkpoint write+reread already produces a clean on-disk partitioner. Removing the pre-write repartition (Fix-A) makes the checkpoint itself the rebalance point — exactly the Hail-recommended "repartition after write, not before" ordering.

## Resolution

root_cause: |
  load_qc_cohort()'s FRESH path calls mt.repartition(2048) at src/python/aou_ld_panel.py:1334 with the DEFAULT shuffle=True, immediately after hl.split_multi_hts(mt) (line 1330) and immediately BEFORE mt.checkpoint(ckpt_post_split) (line 1339). repartition(shuffle=True) performs a full Spark shuffle, which requires building a RangePartitioner by SAMPLING row keys across all input partitions to compute partition boundaries. Because split_multi_hts re-keys and can add rows (multiallelic split), the partitioner inherited from the source/naive_coalesce is invalidated, so Hail must recompute boundaries by gathering key samples. For a source MT with ~145,192 partitions / 2,077 survivors, Hail lowers this boundary computation to a DRIVER-SIDE SpillingCollectIterator (TableValue.mapRows -> ExecuteRelational.execute <- BackendHttpHandler), funneling the surviving partitions' keys to the master node and spilling to local /tmp. The driver does ~all the work (≈1.4s CPU over 38 min = blocked on I/O/spill, 0 active executor threads). This is the implicit collect — there is no explicit .collect() in the code; repartition(shuffle=True)-before-write IS the implicit collect. The op is also REDUNDANT: (a) naive_coalesce(2048) at line 1327 already set the partition count to 2048, and (b) the very next op is a checkpoint (write+read) which on read-back already yields a clean on-disk partitioner. The Hail team explicitly advises against repartition(shuffle=True) and to "repartition AFTER writing, not before" / use _n_partitions on read. The pre-write repartition is over-engineering introduced as the DEC-2026-05-04-01 "Q3 hybrid balanced-QC" remediation; it is the over-engineering that caused the stall.
fix: |
  Fix-B (Hail-team-prescribed "repartition AFTER write, not before"):
  1. Add module constant _COHORT_TARGET_PARTITIONS = 2048 (replaces the two magic 2048 literals; documents the Q3-hybrid target).
  2. Add pure Hail-free helper _post_split_read_partitions(n_target=...) returning the target partition count for the post-split checkpoint read-back (the single, driver-collect-free rebalance point). Unit-testable without Hail.
  3. FRESH path: keep naive_coalesce(_COHORT_TARGET_PARTITIONS) (cheap no-shuffle reduce 145k→2048) + split_multi_hts; DELETE mt.repartition(2048) (line 1334); after checkpoint(ckpt_post_split), re-read with hl.read_matrix_table(ckpt_post_split, _n_partitions=_post_split_read_partitions(...)) so the rebalance happens on READ (uses on-disk partition index, no key-sampling/driver gather). Both FRESH and RESUME_FROM_POST_SPLIT then enter Phase 2 from a balanced on-disk MT.
  Untouched (hard constraints): _assert_checkpoint_nonempty (md5 16caccec...), _validate_checkpoint_populated, du-floor logic, interval-suffix naming, CDR env-derive + suffix-discovery.
verification: |
  STRUCTURAL (NCSU-side, no Hail) — RED→GREEN proven:
  - RED (pre-fix): test_fresh_path_no_repartition_before_post_split_checkpoint failed on `mt = mt.repartition(2048)`; the two helper tests failed with ImportError (_post_split_read_partitions / _COHORT_TARGET_PARTITIONS absent). Proved inline that the tightened static check is RED on the pre-fix snippet (caught=True) and GREEN on the fixed snippet (caught=False).
  - GREEN (post-fix): all 3 new guards pass. Full tests/m3 suite: 112 passed, 27 skipped (Hail-gated skips expected; was 109 pre-change, +3 new tests, zero regressions).
  - Helper boundary behavior verified: None->2048, 145192->2048, 37->37, 0->1, 2048->2048, custom target honored.
  - Hard constraints verified: _assert_checkpoint_nonempty md5 still 16caccec0678a9e57f38569cb3e5b801 (byte-identical); _validate_checkpoint_populated + _interval_scaled_du_floor present; interval-suffix naming intact; CDR env-derive/suffix-discovery untouched; no executable mt.repartition() call remains (only comments).
  LIVE end-to-end proof DEFERRED to the next Gate B re-fire (human holds the trigger; no Hail/AoU access NCSU-side). Expected on re-fire: load_qc_cohort distributes across executors, no SpillingCollectIterator driver stall, post_split checkpoint completes in minutes.
files_changed:
  - src/python/aou_ld_panel.py (drop pre-write repartition; add _COHORT_TARGET_PARTITIONS + _post_split_read_partitions; rebalance via checkpoint read-back with _n_partitions)
  - tests/m3/test_aou_ld_panel_local.py (3 RED-first regression guards)
