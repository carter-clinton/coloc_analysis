---
status: resolved
trigger: "m3-gateb-load-qc-cohort-driver-collect: load_qc_cohort() stalls indefinitely on Hail DRIVER (SpillingCollectIterator) during Gate B chr22 smoke, instead of distributing to executors"
created: 2026-06-02T00:00:00Z
updated: 2026-06-04T18:00:00Z
resolved: 2026-06-04T18:00:00Z
---

> **RESOLVED 2026-06-04 — Gate C live-confirmed.** The read-back rebalance fix (e23c081, drop
> pre-write repartition → read_matrix_table(_n_partitions=)) + the colon-sanitize follow-on
> (a96f2cf) held across all 3 cohorts at whole-chr22 scale. EUR's heavier final-phase
> aggregate_cols collectDArray gather (221,624 samples) completed in ~4 min — a mid-run jstack
> briefly misread it as a wedge; it was in-flight and finished cleanly. WAVE-2 WATCH-POINT:
> driver-side collectDArray scales with samples × partitions; watch EUR genome-wide (see
> [[m3-gatec-sample-callrate-ordering-collapse]] closeout).

## Current Focus

hypothesis: FOLLOW-ON (H6) CONFIRMED by source — the e23c081 driver-collect fix (read_matrix_table(_n_partitions=) read-back at line 1401-1404) held perfectly live, but it routes ckpt_post_split through Hadoop's Path/URI parser, which exposed a LATENT path-sanitization bug: _intermediate_checkpoint_uri (line 352-380) builds interval_suffix = f"_{interval_filter}" at line 376 with NO sanitization. For interval_filter="chr22:16000000-18000000" the colon survives into '.../mt_afr_post_split_chr22:16000000-18000000.mt'. GCS tolerated the colon on WRITE (line 1391 checkpoint succeeded — post_split populated, 120 real row partitions), but the read-back parses 'chr22:' as a URI scheme → java.net.URISyntaxException: Relative path in absolute URI. The Tier-2 'chr22' default (no colon) never triggered it.
test: RED-first regression (pure string builders, NO Hail needed) — DONE.
expecting: RED→GREEN — ACHIEVED. RED reproduced the live URISyntaxException token byte-for-byte NCSU-side; GREEN after adding _sanitize_interval_suffix + using it in _intermediate_checkpoint_uri. Full tests/m3 = 116 passed / 27 skipped (+4, zero regressions). e23c081 read-back UNTOUCHED (md5 + read-back verified).
next_action: COMPLETE pending live re-verify. Both fixes structurally GREEN NCSU-side. Status held at awaiting_human_verify — returns to the human for the NEXT Gate B re-fire to confirm the nano interval now round-trips through the read-back (no URISyntaxException) and the nano cohort completes through both checkpoints. Orchestrator commits code+tests (one commit) and debug-doc (another); orchestrator pushes. Orphan colon-named MT deletion = hygiene only.

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

# ===== FOLLOW-ON FINDING (2026-06-02): colon path-sanitization bug exposed by the e23c081 read-back =====

- timestamp: 2026-06-02T02:00:00Z
  checked: Gate B re-fire on n2-standard-16 cluster (Carter, human-verify checkpoint response)
  found: The e23c081 driver-collect fix WORKED LIVE — state=FRESH wrote the post_split intermediate, NO driver-collect stall, 0 spills, post_split MT populated with 120 real row partitions, ~3 min (not 38), clean driver jstack, empty-MT catastrophe did NOT reproduce. BUT the run then raised a FatalError on the new post-write RE-READ: `java.net.URISyntaxException: Relative path in absolute URI: mt_afr_post_split_chr22:16000000-18000000.mt`. The colon from the nano INTERVAL ('chr22:16000000-18000000') leaked into the intermediate checkpoint path.
  implication: H1/Fix-B (driver-collect) is VERIFIED LIVE and stays. A SEPARATE, latent bug — never exercised by the Tier-2 'chr22' default (no colon) — was EXPOSED by the fix's new read_matrix_table(ckpt_post_split, _n_partitions=...) step, which routes the URI through Hadoop's Path/URI parser. GCS tolerated the colon on WRITE; Hadoop reads 'chr22:' as a URI scheme and throws. New hypothesis H6.

- timestamp: 2026-06-02T02:10:00Z
  checked: _intermediate_checkpoint_uri (src/python/aou_ld_panel.py:352-380 pre-fix) line-by-line vs the existing sanitization convention
  found: Line 376 built `interval_suffix = f"_{interval_filter}"` with NO sanitization → for interval_filter='chr22:16000000-18000000' yields '.../mt_afr_post_split_chr22:16000000-18000000.mt' (colon intact). The EXISTING convention sanitizes BOTH colon and dash to underscore: the AOU-1 smoke notebook (.planning/notebooks/AOU-1-chr22-smoke_template.ipynb:149) does `_suffix = "_" + INTERVAL.replace(":", "_").replace("-", "_")` and the final cohort MTs are named '..._chr22_16000000_18000000.mt'. _intermediate_checkpoint_uri was the LONE builder missing it — its docstring example only ever passed a clean "chr22", so the colon case was never exercised. _interval_scaled_du_floor (line 834) PARSES the colon for span math but never builds a path, so no risk there.
  implication: H6 CONFIRMED at source. Fix = sanitize interval_filter inside _intermediate_checkpoint_uri to match the established notebook convention. Extract the reusable _sanitize_interval_suffix() helper (per [[feedback_extract_reusable_utilities]] "recurrent bug class → reusable utility + failing-test-first regression") encapsulating exactly `.replace(":", "_").replace("-", "_")`.

- timestamp: 2026-06-02T02:20:00Z
  checked: RED-first regression (NCSU-side, no Hail — pure string builders). Added 3 tests + ran on PRE-fix code.
  found: RED confirmed exactly. test_intermediate_checkpoint_uri_sanitizes_colon_nano_interval FAILED showing leaked colon 'mt_afr_post_split_chr22:16000000-18000000.mt' (byte-identical to the live URISyntaxException token). The sensitivity=True variant FAILED identically with the _pca_selfid infix. test_sanitize_interval_suffix_helper FAILED with ImportError (helper absent). test_intermediate_checkpoint_uri_clean_chr22_unchanged PASSED (existing 'chr22' contract preserved). 3 failed, 1 passed.
  implication: The RED reproduces the live failure deterministically NCSU-side. Proceed to GREEN.

- timestamp: 2026-06-02T02:35:00Z
  checked: SCOPE SCAN — grep every Hadoop reader/writer (read_matrix_table / read_table / import_table / checkpoint / write / hadoop_open) and cross-reference against interval_filter flow. Confirm _intermediate_checkpoint_uri is the lone affected builder.
  found: (1) read_matrix_table(mt_path) (1386) — source ACAF path, not interval-derived. (2) checkpoint/read of ckpt_post_split/ckpt_post_sqc (1430/1440/1448/1454/1473) — derive SOLELY from _intermediate_checkpoint_uri (1310-1312), now sanitized. (3) final checkpoint(ckpt) (1494) — from _qc_checkpoint_uri (NO interval param → no colon; notebook adds its own sanitized _suffix). (4) import_table(anc_path/rel_path), ld_bm.write, hadoop_open(capture_json_uri) — none interval-derived. EVERY non-path use of interval_filter is correct: filter_intervals/parse_locus_interval (1389-1392) consume it as a LOCUS where the colon is REQUIRED; provenance dict (475) is a JSON value; _interval_scaled_du_floor (890/912) parses for span math → integer. PRODUCER/CONSUMER CONTRACT NOTE: _qc_checkpoint_uri final outputs carry NO interval suffix while intermediates DO — this is INTENDED, not a latent mismatch (notebook lines 201-202 explicitly: "_qc_checkpoint_uri itself does NOT honor interval_filter (that's intermediate-only); we suffix manually"; the notebook adds _suffix at line 212). NOT a bug; recorded as the established contract.
  implication: _intermediate_checkpoint_uri is the ONLY affected builder. No scope expansion needed; the producer/consumer split is by design.

- timestamp: 2026-06-02T02:45:00Z
  checked: GREEN — added _sanitize_interval_suffix + used it in _intermediate_checkpoint_uri; updated docstring example to include the colon-bearing nano interval. Ran targeted + full tests/m3.
  found: All 3 new guards + the clean-chr22 + the existing intermediate/qc URI-builder tests pass (14/14 targeted). Full suite: 116 passed, 27 skipped (was 112+27 after e23c081; +4 new string tests, ZERO regressions, zero new skips). NOTE: caught a defect in my OWN first-draft test (an over-broad `'-' not in uri` assertion matched the dash in the bucket name 'fc-secure-XXX'); tightened to scope colon/dash to the MT filename basename (a bucket name may legitimately contain '-', e.g. 'rw-migration-aou-rw-476cdac2'; the exact-equality `uri ==` assertion is the real lock). HARD CONSTRAINTS verified: _assert_checkpoint_nonempty md5 still 16caccec0678a9e57f38569cb3e5b801 (byte-identical Track-4 guard); e23c081 read-back intact (zero executable mt.repartition(); _n_partitions=_post_split_read_partitions read-back present at 1442/1450; naive_coalesce(_COHORT_TARGET_PARTITIONS) at 1422).
  implication: H6 fix GREEN and isolated. The change only alters how the URI STRING is built upstream; the verified-live e23c081 read-back mechanism is untouched.

- timestamp: 2026-06-02T02:50:00Z
  checked: Orphan-MT hygiene reasoning (for orchestrator report) — does the post-fix resume guard pick up the malformed colon-named MT from the failed re-fire?
  found: The resume guard (lines 1310-1312) calls the SAME _intermediate_checkpoint_uri(..., interval_filter) builder. Post-fix, for interval_filter='chr22:16000000-18000000', it computes the UNDERSCORE name 'mt_afr_post_split_chr22_16000000_18000000.mt' and probes THAT path. The orphaned colon-named 'mt_afr_post_split_chr22:16000000-18000000.mt' (+ its .meta.json sidecar) has a DIFFERENT name → the resume guard will neither find nor resume from it; the next FRESH fire writes to the new underscore name from scratch.
  implication: Deleting the orphaned colon-named MT + sidecar is HYGIENE, not a correctness requirement. Confirmed. (Carter may gsutil rm it at leisure; leaving it does not affect resume correctness or risk a stale-resume.)

## Resolution

root_cause: |
  load_qc_cohort()'s FRESH path calls mt.repartition(2048) at src/python/aou_ld_panel.py:1334 with the DEFAULT shuffle=True, immediately after hl.split_multi_hts(mt) (line 1330) and immediately BEFORE mt.checkpoint(ckpt_post_split) (line 1339). repartition(shuffle=True) performs a full Spark shuffle, which requires building a RangePartitioner by SAMPLING row keys across all input partitions to compute partition boundaries. Because split_multi_hts re-keys and can add rows (multiallelic split), the partitioner inherited from the source/naive_coalesce is invalidated, so Hail must recompute boundaries by gathering key samples. For a source MT with ~145,192 partitions / 2,077 survivors, Hail lowers this boundary computation to a DRIVER-SIDE SpillingCollectIterator (TableValue.mapRows -> ExecuteRelational.execute <- BackendHttpHandler), funneling the surviving partitions' keys to the master node and spilling to local /tmp. The driver does ~all the work (≈1.4s CPU over 38 min = blocked on I/O/spill, 0 active executor threads). This is the implicit collect — there is no explicit .collect() in the code; repartition(shuffle=True)-before-write IS the implicit collect. The op is also REDUNDANT: (a) naive_coalesce(2048) at line 1327 already set the partition count to 2048, and (b) the very next op is a checkpoint (write+read) which on read-back already yields a clean on-disk partitioner. The Hail team explicitly advises against repartition(shuffle=True) and to "repartition AFTER writing, not before" / use _n_partitions on read. The pre-write repartition is over-engineering introduced as the DEC-2026-05-04-01 "Q3 hybrid balanced-QC" remediation; it is the over-engineering that caused the stall.
fix: |
  Fix-B (Hail-team-prescribed "repartition AFTER write, not before"):
  1. Add module constant _COHORT_TARGET_PARTITIONS = 2048 (replaces the two magic 2048 literals; documents the Q3-hybrid target).
  2. Add pure Hail-free helper _post_split_read_partitions(n_target=...) returning the target partition count for the post-split checkpoint read-back (the single, driver-collect-free rebalance point). Unit-testable without Hail.
  3. FRESH path: keep naive_coalesce(_COHORT_TARGET_PARTITIONS) (cheap no-shuffle reduce 145k→2048) + split_multi_hts; DELETE mt.repartition(2048) (line 1334); after checkpoint(ckpt_post_split), re-read with hl.read_matrix_table(ckpt_post_split, _n_partitions=_post_split_read_partitions(...)) so the rebalance happens on READ (uses on-disk partition index, no key-sampling/driver gather). Both FRESH and RESUME_FROM_POST_SPLIT then enter Phase 2 from a balanced on-disk MT.
  Untouched (hard constraints): _assert_checkpoint_nonempty (md5 16caccec...), _validate_checkpoint_populated, du-floor logic, interval-suffix naming, CDR env-derive + suffix-discovery.
root_cause_followon_h6: |
  H6 (colon path-sanitization) — EXPOSED by the e23c081 driver-collect fix's new
  read-back, CONFIRMED at source. _intermediate_checkpoint_uri
  (src/python/aou_ld_panel.py) built `interval_suffix = f"_{interval_filter}"` with
  NO sanitization. For the Tier-1 nano interval_filter='chr22:16000000-18000000' this
  produced '.../ld/intermediate/mt_afr_post_split_chr22:16000000-18000000.mt' with the
  colon intact. GCS tolerated the colon on the checkpoint WRITE (the post_split MT wrote
  fine — 120 real row partitions), but the fix's new
  `hl.read_matrix_table(ckpt_post_split, _n_partitions=...)` re-read routes the URI
  through Hadoop's Path/URI parser, which reads 'chr22:' as a URI SCHEME and raises
  `java.net.URISyntaxException: Relative path in absolute URI`. The Tier-2 'chr22'
  default (no colon) never exercised it; the bug was latent until the read-back made
  the intermediate path round-trip through a Hadoop reader. _intermediate_checkpoint_uri
  was the LONE builder missing the sanitization the rest of the system already applies
  (the AOU-1 notebook's _suffix and the final cohort MT names use
  .replace(":","_").replace("-","_")). This one function feeds BOTH ckpt_post_split AND
  ckpt_post_sqc (lines 1310-1312), and sidecar URIs derive from it via _sidecar_uri.
fix: |
  TWO fixes, both verified NCSU-side (live e2e is Carter's next Gate B re-fire):

  Fix-B (H1 driver-collect — VERIFIED LIVE on the re-fire, UNCHANGED here):
  1. Module constant _COHORT_TARGET_PARTITIONS = 2048.
  2. Pure Hail-free helper _post_split_read_partitions(n_target=...).
  3. FRESH: naive_coalesce + split_multi_hts; NO pre-write repartition; rebalance via
     hl.read_matrix_table(ckpt_post_split, _n_partitions=_post_split_read_partitions(...))
     after the checkpoint write. RESUME reads the same way. (e23c081.) DO NOT REVERT.

  Fix-H6 (colon path-sanitization — THIS session, GREEN NCSU-side):
  1. New reusable helper _sanitize_interval_suffix(interval_filter) -> str encapsulating
     the established `.replace(":", "_").replace("-", "_")` convention (single
     sanitization point per [[feedback_extract_reusable_utilities]]).
  2. _intermediate_checkpoint_uri now builds
     interval_suffix = f"_{_sanitize_interval_suffix(interval_filter)}" so the nano
     interval yields the URI-safe '.../mt_afr_post_split_chr22_16000000_18000000.mt'
     (consistent with the notebook's final-output naming). Docstring example updated to
     include the colon-bearing nano interval so the case is documented + locked.
  Scope scan confirmed _intermediate_checkpoint_uri is the LONE affected builder; the
  _qc_checkpoint_uri-has-no-interval-suffix split is an INTENDED producer/consumer
  contract (notebook suffixes manually), not a latent mismatch.

  Untouched (hard constraints): _assert_checkpoint_nonempty (md5 16caccec0678a9e57f38569cb3e5b801),
  _validate_checkpoint_populated, du-floor logic, the e23c081 _n_partitions read-back,
  CDR env-derive + suffix-discovery.
verification: |
  STRUCTURAL (NCSU-side, no Hail) — RED→GREEN proven for BOTH fixes:
  - Fix-B (prior session): test_fresh_path_no_repartition_before_post_split_checkpoint +
    2 helper tests; full tests/m3 was 112 passed / 27 skipped. VERIFIED LIVE on the
    Gate B re-fire (state=FRESH, no driver-collect stall, 0 spills, post_split populated
    with 120 row partitions, ~3 min, clean jstack, empty-MT catastrophe did NOT recur).
  - Fix-H6 (this session): RED first — the 2 colon-nano tests (sens=False + sens=True)
    FAILED showing the leaked colon 'mt_afr_post_split_chr22:16000000-18000000.mt'
    (byte-identical to the live URISyntaxException token); the helper test FAILED with
    ImportError; the clean-'chr22' test PASSED (existing contract preserved). GREEN after
    fix — all pass. Full tests/m3 suite: 116 passed, 27 skipped (+4 new string tests over
    the 112 baseline, ZERO regressions, zero new skips).
  - Caught + corrected a defect in my own first-draft test (over-broad `'-' not in uri`
    matched the bucket-name dash 'fc-secure-XXX'); scoped colon/dash to the MT filename
    basename; the exact-equality `uri ==` assertion is the authoritative lock.
  - Hard constraints verified: _assert_checkpoint_nonempty md5 still
    16caccec0678a9e57f38569cb3e5b801 (byte-identical Track-4 guard); e23c081 read-back
    intact (no executable mt.repartition(); _n_partitions=_post_split_read_partitions
    read-back at 1442/1450; naive_coalesce(_COHORT_TARGET_PARTITIONS) at 1422).
  - Orphan hygiene: post-fix resume guard probes the UNDERSCORE name, so the orphaned
    colon-named MT + .meta.json from the failed re-fire is NOT picked up — deletion is
    hygiene, not a correctness requirement.
  LIVE end-to-end proof for Fix-H6 DEFERRED to the next Gate B re-fire (human holds the
  trigger; no Hail/AoU access NCSU-side). Expected: the post-write read-back succeeds
  (no URISyntaxException), the nano cohort completes through both checkpoints.
files_changed:
  - src/python/aou_ld_panel.py (Fix-B prior: drop pre-write repartition + _COHORT_TARGET_PARTITIONS + _post_split_read_partitions + _n_partitions read-back. Fix-H6 this session: add _sanitize_interval_suffix; sanitize interval_suffix in _intermediate_checkpoint_uri; docstring example with colon-bearing nano interval)
  - tests/m3/test_aou_ld_panel_local.py (Fix-B prior: 3 driver-collect guards. Fix-H6 this session: 3 colon-sanitization regression guards + 1 clean-chr22 preservation guard)
