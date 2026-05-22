---
status: diagnosed
trigger: "m3-W1-empty-mt-catastrophe — bucket inspection reveals MTs lack entries/ data despite _SUCCESS markers and ~$2,100 burn"
created: 2026-05-21T00:00:00Z
updated: 2026-05-21T01:00:00Z
mode: find_root_cause_only
symptoms_prefilled: true
---

# Root Cause Analysis: m3-W1 Empty-MT Catastrophe

## Confidence

**HIGH** confidence on the proximate root-cause class (verification-method false-positive) and the operational chain that produced the symptoms.

**MEDIUM-HIGH** confidence on the specific Hail-level mechanism for `mt_afr_qc.mt`'s "_SUCCESS + row stubs + empty entries" state — two plausible mechanisms (a) Hail driver-side finalize firing on tasks-reported-complete signal without contents validation, (b) extreme `spark.executor.memory=5g / cores=1` profile producing silently truncated writes — both produce the observed signature; direct hail.log forensics on the W1 monolithic-run log (NOT just the EUR-cell-truncated `hail.log.pre_pd_migration.20260521T201919Z.log`) would discriminate. The AoU-side Hail read-probe Carter is running will further constrain this.

**LOW** confidence on whether the EUR cell (Cell 5) ever submitted a write at all vs. whether Cell 6/Cell 7 lazy-force triggered re-execution that masqueraded as "Stage 62 EUR write". Bucket evidence shows `mt_eur_qc.mt` directory does not exist — the EUR write never produced even a `_SUCCESS` marker. This contradicts the 2026-05-20 STATE.md claim that "Stage 62 = MT #3 EUR write strongly inferred committed".

---

## Root Cause Statement

The catastrophe is a **verification-method false-positive compounded by Hail lazy-evaluation semantics**, NOT a code defect in `load_qc_cohort` per se. Three pathologies stacked:

1. **The verification methodology used 2026-05-19/20 (gsutil `_SUCCESS` + `metadata.json.gz` listing for MT #1; Spark UI stack-trace signature matching for MT #2/#3) DOES NOT validate that MT entries/ data exists.** The "canonical 82-task finalize-cascade" pattern fires for ANY Hail write IR submission — populated or empty — because the cascade is the IR-execution scaffolding, not a contents validator. The `feedback_aou_spark_ui_stack_trace_verification` memory baked 2026-05-20 OVERSTATED the discriminative power of this signature.

2. **Hail `mt.checkpoint(uri, overwrite=True)` writes `_SUCCESS` based on driver-side "tasks reported complete" accounting, not contents validation.** Combined with the extreme `spark.executor.cores=1 / spark.executor.memory=5g` profile injected by AOU-1 Cell 1a's PYSPARK_SUBMIT_ARGS (which is necessary for v8 partition-explosion OOM remediation per [[feedback_aou_dataproc_pyspark_submit_args]]), an executor-side write that silently truncates after writing the Parquet schema footer but before writing entries row-group payloads still satisfies the driver-side "tasks-complete" signal — producing the observed mt_afr_qc.mt state (`_SUCCESS` + 2,045 row stubs at ~35 bytes each = exactly the Parquet column-metadata footer size + zero entries/ contents).

3. **The Cell 5 EUR write almost certainly never executed.** The preserved hail.log shows EUR cohort write IR submitted 2026-05-20 19:07:36 then truncated 28 seconds later mid-JIT-compile, with NO Spark stages logged for the EUR write and no "Successfully wrote" line. Carter killed Cell 7 mid-Stage-71 via workbench Pause around 22:30 UTC the same day. The bucket evidence (`mt_eur_qc.mt` directory does not exist AT ALL) corroborates that the EUR write never reached `_SUCCESS`. STATE.md's "Stage 62 = MT #3 EUR write" attribution is incorrect — Stage 62 must have been something else (most plausibly Cell 6's `.s.collect()` over the EUR cohort lineage or a lazy re-execution force from Cell 7's `mt_afr_selfid.count_rows()` traversing the full cohort definition).

The refactored `load_qc_cohort` at HEAD (bd144a6 + 4 helpers + 5 live-Hail resilience tests) **does not defend against this failure mode** — its intermediate checkpoints use the same `mt.checkpoint()` pattern with `_has_checkpoint` (which only checks `_SUCCESS` existence) as the resume gate. The refactor solves a DIFFERENT class of problem (work-loss-on-crash via mid-pipeline resume) and would have IDENTICAL exposure to silent empty-write commits.

The cumulative ~$2,100 burned across 4 sessions produced zero usable cohort MTs. The 67h monolithic run on 2026-05-18 to 2026-05-20 produced visually consistent Spark UI progress that was indistinguishable from a successful run via the operational instrumentation available (iframe + terminal hostile, gsutil-deferred-to-resume).

---

## Evidence Chain

Ordered from operational chain → code-side mechanism → bucket forensics.

### Operational chain (which code path ran where, and why)

1. **The refactored `load_qc_cohort` NEVER executed on AoU.** Per `260518-qcr-SUMMARY.md` operational_context (lines 56-58): `cell_3_state: currently running on un-refactored code path`; `cell_4_plan: will auto-fire after Cell 3; un-refactored`; `cell_5_plan: DEFERRED to refactored code via post-AoU re-clone; halt before Cell 5 auto-fires (Kernel Interrupt at Cell 4 _SUCCESS)`. STATE.md Session-2026-05-20 (line 437): "67h monolithic Cell 3-7 run on un-refactored code". The refactor (chain `2cefa9e..bd144a6` + 5 test commits) landed on origin/main 2026-05-18 evening but the AoU clone was **never `git pull`ed** in time to use it for the monolithic run.

2. **Path B1 selected 2026-05-19 ~14:30 UTC**: let monolithic Cell 3-7 complete instead of kill+refactor at the MT #2/#3 inflection. Per Session 2026-05-20 retrospective: "iframe-broken + cost-neutral analysis + healthy run track record". This decision baked in 3 sequential un-refactored writes for AFR-primary / AFR-sensitivity / EUR-primary.

3. **MT #1 "verification" 2026-05-19 was incomplete**: STATE.md explicitly: "MT #1 (AFR primary) | gs://.../ld/mt_afr_qc.mt/ | DIRECT (gsutil scrollback 2026-05-19: `_SUCCESS` + `metadata.json.gz` parsed clean with canonical Hail MT keys)". Nowhere did the scrollback list `entries/entries/parts/` contents. The same false-positive verification pattern that 2026-05-21 gsutil exposes via `CommandException: One or more URLs matched no objects` against `entries/entries/parts/` would have been INVISIBLE to the 2026-05-19 scrollback.

4. **Stack-signature inference for MT #2/MT #3 was provably non-discriminative**: STATE.md Session-2026-05-20: "Since Stage 36 is a verified successful write, this stack pattern IS what Hail's write looks like (the write/Parquet-encode/GCS-upload operations are JIT-compiled into the `__C*Compile.__m*` bytecode classes themselves, not exposed as separate stack frames). Therefore Stages 45 and 62 (identical stack) are also writes." This reasoning is circular: it assumes Stage 36 represents a populated write (which the current bucket evidence refutes), then propagates that assumption to Stages 45/62. The cascade signature reflects Hail's IR-lowering machinery, not write-contents validity.

5. **EUR write never reached even `_SUCCESS`**: Per symptoms block, preserved hail.log (`hail.log.pre_pd_migration.20260521T201919Z.log`) shows: EUR cohort write IR submitted 2026-05-20 19:07:36; log truncated 19:08:04 mid-JIT-compile (28s later); NO Spark stages logged for EUR write; no `Wrote MatrixTable` / `Successfully wrote` line. Cell 7 (Stage 71 = `mt_afr_selfid.count_rows()`) had ALREADY been firing for >2.7h at this point (per STATE.md timing of velocity-collapse measurements at 2.7h elapsed) — so Cell 5's "completion" recorded earlier in the session was lazy / synthesized; the actual EUR write was never scheduled.

### Code-side mechanism (why mt_afr_qc.mt has _SUCCESS but no entries)

6. **Un-refactored final-checkpoint write contract** (src/python/aou_ld_panel.py:685-688, structurally identical to what ran on AoU):
   ```
   ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
   mt = mt.checkpoint(ckpt, overwrite=True)
   print(f"[load_qc_cohort] wrote final: {ckpt}")
   ```
   Three sequential calls (sensitivity=False/True/False) write to three distinct URIs after `36e8062`'s helper extraction. `overwrite=True` is hardcoded — no defensive failure if a prior partial write exists. The print line is a side-effect AFTER `mt.checkpoint()` returns, so its absence in the hail.log for EUR (preserved snippet shows "submitted... truncated mid-JIT-compile") is consistent with the EUR call never returning.

7. **Cell 7 lazy-force triggers full re-derivation** (`.planning/notebooks/AOU-1_template.ipynb` Cell 7):
   ```
   cohort_summary = pd.DataFrame({
       ...,
       "n_variants": [n_var_afr, mt_afr_selfid.count_rows(), mt_eur.count_rows()],
       ...
   })
   ```
   - `n_var_afr` was eagerly computed in Cell 3 (line `n_var_afr = mt_afr.count_rows()`) — IF the Cell 3 final checkpoint had populated entries, this would have been cheap (cached partition metadata); otherwise Cell 3 itself would have hung or thrown. Cell 3 print line ("AFR PCA cohort: ... samples, ... variants") must have appeared OR else Cell 3 would not have returned to allow Cell 4 to fire. **This is the strongest evidence that mt_afr_qc.mt was POPULATED at end-of-Cell-3** (per the Hail-internal MT object) — but the BUCKET commit may have happened later or never; Hail's `mt.checkpoint()` returns the IN-MEMORY MT that points at the bucket URI, and downstream `count_rows()` can be satisfied from cached partition metadata WITHOUT re-reading the bucket. Cell 3's reported variant count could have come from JVM-side cached IR, NOT from a bucket read-back.
   - `mt_afr_selfid.count_rows()` and `mt_eur.count_rows()` in Cell 7 fire for the FIRST TIME — never invoked in Cells 4 or 5 (which only call `count_cols()`). This is when the lazy IR for the entire ancestry-filter + sample_qc + variant_qc + filter_rows + write chain gets forced. Stage 71's velocity collapse (0.27 t/min for `mt_afr_selfid.count_rows()`) is consistent with Hail being forced to re-execute the entire AFR-sensitivity cohort definition from source because either (i) the prior bucket commit was empty (the write IR no-op'd) or (ii) the bucket write had no entries and Hail's read-back was scanning empty parts.

8. **Hail `mt.checkpoint()` write-contract weakness**:
   - Hail's writer driver-side `finalize()` (which writes `_SUCCESS`) is invoked when all executor tasks report "complete" status to the driver. It does NOT validate output contents.
   - The 2,045 row-stub files at ~35 bytes each match exactly the Parquet column-metadata footer size for an empty row group. This is consistent with executor task code: (a) opened the output Parquet file, (b) wrote the schema/footer, (c) was killed/no-op'd before writing row-group entries data, (d) returned "complete" to driver anyway.
   - The injected `spark.executor.cores=1` + `spark.executor.memory=5g` profile (via AOU-1 Cell 1a PYSPARK_SUBMIT_ARGS) creates extreme memory pressure on per-executor JVM heaps for entries-write tasks. If YARN killed an executor mid-entries-write but the task had already partially reported progress, the task could appear "complete" to the driver while leaving truncated bucket output.
   - 2,045 partitions matches `naive_coalesce(2048)` minus a few empty partitions — every partition produced a footer-only stub.

### Bucket forensics

9. **Bucket arithmetic precludes hidden populated data**: bucket-wide ~71 MiB total; 27 MiB is the forensic hail.log preserve; ~44 MiB remaining. A populated MT for ~91k AFR samples × ~50-100M variants would be tens of GB minimum. There is NO place where populated entries could be hiding.

10. **mt_eur_qc.mt does not exist as a directory** (0 objects from `gsutil ls`). Cell 5 either (i) never executed its `mt.checkpoint()` call because Cell 4's lazy completion blocked it, or (ii) executed it but the bucket write IR was killed before even the `_SUCCESS` write could happen (consistent with the 28-second JIT-truncate window in the preserved hail.log).

11. **mt_afr_pca_selfid_qc.mt has `_SUCCESS` marker** (per symptoms block) but bucket-total arithmetic dictates it cannot contain populated entries either. Same failure mode as mt_afr_qc.mt.

---

## Critical Question Answers

### Q1: What is the actual data state of all three MTs?

Per symptoms (bucket inspection 2026-05-21):
- **mt_afr_qc.mt**: `_SUCCESS` + `metadata.json.gz` + `README.txt` + `rows/rows/parts/` with 2,045 stub files (~35 bytes each = Parquet footers only); `entries/entries/parts/` **absent**. ~tens of KB total. NO usable data.
- **mt_afr_pca_selfid_qc.mt**: `_SUCCESS` marker present; bucket-total arithmetic precludes populated entries. Pending Hail-side `entries/entries/parts/` probe to confirm.
- **mt_eur_qc.mt**: directory does NOT exist. NO data of any kind.

Carter's Hail read-probe (incoming to parent context) will further constrain MT #2's state and may also report what `hl.read_matrix_table(mt_afr_qc.mt).count_cols()` returns — that result will reveal whether the MT skeleton is even Hail-loadable.

### Q2: Code-path root cause — why row stubs but no entries with `_SUCCESS`?

The un-refactored final-checkpoint path (`src/python/aou_ld_panel.py:685-688`) is:
```
ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
mt = mt.checkpoint(ckpt, overwrite=True)
print(f"[load_qc_cohort] wrote final: {ckpt}")
```
The code does NOT touch `_SUCCESS` itself — Hail's writer does that during driver-side `finalize()`. The bug is at the Hail/Spark layer: `_SUCCESS` is written based on tasks-reported-complete accounting, not contents validation. Under extreme `cores=1 / mem=5g` per-executor pressure, tasks can report complete after writing only Parquet schema footers (the row-stub state we observe), leaving entries empty. The code does NOT write rows separately from entries — that decomposition is Hail-internal — but ALSO does NOT add any post-write contents validation (no `count_cols()` / `count_rows()` / `entries-dir-exists` assertion after `mt.checkpoint()` returns).

The un-refactored vs refactored versions are NOT meaningfully different on this axis. The refactor adds intermediate checkpoints to enable resume-from-mid-pipeline, but the intermediate writes use the SAME `mt.checkpoint()` contract and would have the SAME failure mode.

### Q3: Notebook-fire root cause — what cells actually fired?

- AOU-1 template was fired (the live AoU notebook is a mirror of `.planning/notebooks/AOU-1_template.ipynb` with Cell 1a/1b PYSPARK_SUBMIT_ARGS / direct `hl.init` patches per `260512-ldj` sync).
- Cells fired during 2026-05-18 → 05-20 monolithic run: Cell 1a + Cell 1b (init) + Cell 3 (AFR primary load_qc_cohort + count_cols + count_rows) + Cell 4 (AFR sensitivity load_qc_cohort + count_cols) + Cell 5 (EUR load_qc_cohort + count_cols) + Cell 6 (disjoint check via `.s.collect()`) + Cell 7 (cohort_summary DataFrame build + `mt_afr_selfid.count_rows()` then `mt_eur.count_rows()` then to_csv).
- Writes were invoked via the UN-refactored `load_qc_cohort` (refactor never re-pulled into AoU clone before the monolithic run).
- Cell 7 was killed mid-Stage-71 (Carter clicked workbench Pause Environment ~22:30 UTC after seeing velocity collapse to 0.27 t/min projecting $800-9000 additional burn). `cohort_summary_m3.tsv` was never written to the env local disk or bucket.

### Q4: Stage-signature failure mode — is the 82-task cascade reliable?

**NO.** Per memory `feedback_aou_spark_ui_stack_trace_verification` baked 2026-05-20, the canonical 82-task finalize-cascade was treated as the operational discriminator for successful MT writes. The current bucket evidence proves this is incorrect: the cascade can fire for ANY Hail write IR — including writes where the entries body is empty (either because upstream filtering pruned all entries, OR because executor-side writes silently truncated). The cascade signature reflects Hail's IR-lowering scaffolding (collectDArray → JIT compile → executor distribution → driver finalize), NOT the contents validity of the bucket-side commit.

This is a structural weakness of any inference-based verification: stack signatures are necessary but not sufficient. The memory should be amended to caveat the discriminator.

### Q5: Quick-task forensic trail

The "Wave-1 COMPLETE" claim in STATE.md was based on these specific pieces of evidence (per Session 2026-05-20 entry):
1. Stage 36/45/62 stack-trace signatures matching the "verified" Stage 36 reference (circular: Stage 36's "verification" was itself only `_SUCCESS + metadata.json.gz`).
2. Canonical 82-task finalize-cascades after each wide stage (Stages 36/45/62) — see Q4 above for why this is non-discriminative.
3. The MT #1 gsutil scrollback 2026-05-19 listing `_SUCCESS` + `metadata.json.gz` — which does NOT list `entries/entries/parts/` contents.

**No quick task in `.planning/quick/260512-*` through `260520-s2s-*` actually inspected `entries/entries/parts/` for any of the 3 MTs.** The forensic trail confirms the verification was inferential throughout.

### Q6: AOU-LD-PIPELINE.md §11.0 — was the 256-vCPU minimum validated against MT data?

Per `AOU-LD-PIPELINE.md` line 462-482 (§11.0): "Empirically derived 2026-05-17 (m3-W1 Cell 3 cluster-mis-sizing incident, $87-97 sunk discovering this)". The empirical validation referenced the FAILURE of an under-sized cluster (n1-highmem-4 × 16 = 64 vCPU; 3779 pending containers vs ~32 running; projected 70h+ per ancestry). The validation showed the cluster could RUN the load_qc_cohort workload without YARN-pending-container starvation — it did NOT validate that the resulting MT contained populated entries. The minimum-cluster recommendation stands as a NECESSARY condition for the workload, but is NOT a sufficient condition for correct writes.

### Q7: Premature `_SUCCESS` hypothesis

`_SUCCESS` is written by **Hail's writer during driver-side `finalize()`**, NOT by the notebook code or by load_qc_cohort. Specifically:
- `aou_ld_panel.py` has NO explicit `_SUCCESS` touch — neither in `load_qc_cohort` nor in any helper. The only `_SUCCESS`-related code is `_has_checkpoint(uri)` which READS the marker.
- AOU-1 notebook has NO explicit `_SUCCESS` touch.
- No hand intervention during prior sessions (per STATE.md narrative; only Carter actions were workbench-panel Pause clicks and a near-miss-delete that was averted).
- The refactor's auto-recovery path does not write `_SUCCESS` as a sentinel (it only reads it).

The `_SUCCESS` markers in the bucket must have been written by Hail's `finalize()` accounting on driver-side after tasks reported "complete". The race condition is between (a) driver finalize firing when tasks report complete, and (b) tasks having actually completed contents writes. Hail does not enforce (b) — see Q2 above for the failure mechanism.

### Q8: Does the refactored `load_qc_cohort` prevent this failure mode?

**NO.** The refactor at HEAD (commit `bd144a6` body refactor + 4 helpers + 5 live-Hail resilience tests inside `tests/m3/test_aou_ld_panel_local.py:494-681`):
- Adds 2 intermediate `mt.checkpoint()` writes (post_split.mt + post_sample_qc.mt) before the final write, each with sidecar provenance metadata.
- Adds an auto-resume state machine that detects intermediates via `_has_checkpoint(uri)` (which only checks `_SUCCESS` existence — same trap).
- The 5 live-Hail resilience tests inside the test file verify:
  - `test_load_qc_cohort_auto_resume_from_post_split` — resume from intermediate 1
  - `test_load_qc_cohort_auto_resume_from_post_sample_qc` — resume from intermediate 2
  - `test_load_qc_cohort_force_fresh_bypasses_auto_resume` — force_fresh override
  - `test_load_qc_cohort_raises_on_sidecar_mismatch` — parameter mismatch detection
  - `test_load_qc_cohort_auto_recovers_from_orphan_mt` — sidecar-absent → auto-force-fresh

**NONE of these tests verify "empty-entries with `_SUCCESS`"** — the test fixture uses `synthetic_mt_path` (a balding-nichols fixture with 100 samples × 1500 variants) where the AFR ancestry filter survives non-zero rows, so the test's `mt.checkpoint()` produces a NON-empty MT, and the test never re-reads the bucket to assert entries-dir existence. The orphan-MT test sets up a "sidecar-absent-but-MT-exists" condition — but the MT in that test IS populated (the first fire wrote real data), so the orphan-recovery path is exercised against a healthy MT, not against an empty-entries pathology.

**Worse: the 5 resilience tests have NEVER actually executed in CI.** Per `260518-qcr-SUMMARY` `tdd_evidence` line: "5 new live-Hail tests SKIP via `_require_hail()` since Hail is not installed in /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/". On HPC they SKIP (no Hail); on AoU they were supposed to fire as part of the validation gate that never happened. Their PASS status is theoretical.

The refactor's auto-resume state machine will HAPPILY resume from a bucket that has `_SUCCESS` + empty entries — `_has_checkpoint()` returns True, sidecar exists with matching params, state transitions to `RESUME_FROM_POST_SAMPLE_QC`, and Phase 3 fires `variant_qc` on an empty MT, producing another empty `_SUCCESS`-marked MT. **The rebuild would burn another $1500+ producing identical failures.**

---

## Failure Mode Reconstruction

Timeline mapped to bucket state:

1. **2026-05-12** (first fire): AOU-1 Cell 3 fired on un-refactored code with the `_qc_checkpoint_uri` naming-collision bug (sensitivity flag ignored). Bug surfaced mid-flight. Remediated under TDD (commit `36e8062`); helper extracted; AoU clone pulled; Cell 4 fired with distinct URIs. RegionPool OOM on v8 partition-explosion encountered → DEC-2026-05-04-01 remediation re-applied (commit `8cc6f64`) → PYSPARK_SUBMIT_ARGS Cell 1a pattern baked. **This session's MT outputs (if any) were overwritten by subsequent sessions.**

2. **2026-05-14** (second fire): Bucket prefix bug surfaced (`gs://gs://` double-prefix from prefixed `WORKSPACE_BUCKET`). Remediated under TDD (commits `779fe84` / `243ebae`). Near-miss env Delete averted (Carter realized disk-type was Standard not Reattachable; baked feedback memory). **Session ended; MT outputs from this session, if any, were overwritten.**

3. **2026-05-17** (third fire): Cluster mis-sizing diagnosed (n1-highmem-4 × 16 = 64 vCPU, NOT 256). $87 burned. Env DELETED. AOU-LD-PIPELINE.md §11.0 amended to spec the 16× n1-highmem-16 = 256 vCPU minimum.

4. **2026-05-18 03:14 UTC** (fourth fire = monolithic Cell 3-7): Refactored `load_qc_cohort` complete on HPC (commit `bd144a6` head) but NOT pushed to origin/main yet. AoU clone still has UN-refactored code. Cell 3 fired via "Run All Below" queuing Cells 3-7.

5. **2026-05-18 — 2026-05-19**: Cell 3 ran ~18h on un-refactored code (Stage 19 alone took ~18h due to partition skew). Stage 36 fired (cohort_summary stage cascade for AFR primary) ~7.7h. Cell 3 returned with `n_afr` and `n_var_afr` printed (per AOU-1 Cell 3 code structure). Refactor pushed to origin/main 2026-05-18 evening as `50f071c`-adjacent (actual head `bd144a6`); AoU clone never `git pull`ed.

6. **2026-05-19**: Cell 4 fires sequentially. Stage 45 (~9.5h, 4090 tasks) interpreted as MT #2 write. Path B1 selected ~14:30 UTC (let monolithic complete; refactor benefit deferred). MT #1 "verified" via gsutil scrollback (`_SUCCESS` + `metadata.json.gz` listing — entries/ NOT inspected).

7. **2026-05-19 — 2026-05-20**: Cell 5 fires. Stage 62 (~16.5h, 4090 tasks) interpreted as MT #3 EUR write via stack-trace signature matching to Stage 36.

8. **2026-05-20 19:07:36 UTC**: hail.log records "EUR cohort write IR submitted". 19:08:04 UTC: log truncated mid-JIT-compile. The 28-second gap is consistent with a JVM event (OOM, executor disconnect, or kernel-signal) that terminated logging. The EUR write IR never produced a Spark stage. Stage 62 must have been something else (most plausibly Cell 6's `mt.s.collect()` over the EUR cohort lineage forcing a full re-derive from source — Cell 6 fires `set(afr_samples) & set(eur_samples)` arithmetic that requires both cohort's sample lists materialized).

9. **2026-05-20 ~21:00 UTC**: Cell 7 fires. `n_var_afr` is in-Python-memory from Cell 3. `mt_afr_selfid.count_rows()` is invoked for the FIRST TIME — Stage 71 starts. 4090 tasks. Velocity starts at 2.12 t/min (slow but progressing); drops to 0.27 t/min at 3.5h elapsed → 8× deceleration. Projection: 9-43h more for Stage 71 alone. The full-row scan of the AFR sensitivity cohort is dragging because Hail is forced to re-read entries from a bucket that has NONE — every task is reading footer-only Parquet stubs and trying to materialize a row count.

10. **2026-05-20 ~22:30 UTC**: Carter clicks workbench Pause Environment. Cell 7 killed mid-Stage-71. `cohort_summary_m3.tsv` never written. Env paused at $0.14/hr.

11. **2026-05-20 — 2026-05-21**: STATE.md updated to "Wave-1 COMPLETE" based on stack-signature inference. `WAVE-1-CLOSEOUT-CHECKLIST.md` written but only the bucket-marker verification step (STEP 3) was prescribed — NOT entries/ inspection.

12. **2026-05-21**: Wave 2 resume — Carter fires direct gsutil inspection. Discovers (a) bucket total is ~71 MiB (~27 MiB hail.log preserve, ~44 MiB everything else), (b) `mt_eur_qc.mt` directory does not exist, (c) `mt_afr_qc.mt/entries/entries/parts/` is genuinely absent, (d) row stubs are ~35 bytes each (Parquet footers only). The catastrophe is exposed.

---

## Why Inference Was Wrong

The 2026-05-19 stack-signature inference and 2026-05-20 "Wave-1 COMPLETE" claim were over-confident because:

1. **Stack signatures cannot discriminate write contents.** Hail's IR-execution scaffolding (collectDArray → JIT bytecode → executor task distribution → driver finalize) is universal across writes/counts/aggregates. The same scaffolding fires for a populated write, an empty-entries write, a no-op write, or even a write to `/dev/null`. The `feedback_aou_spark_ui_stack_trace_verification` memory should have caveated that the discriminator is necessary-but-not-sufficient.

2. **The "DIRECT verify" of MT #1 was not direct.** Listing `_SUCCESS` + `metadata.json.gz` is a structural check, not a contents check. The verifying command never traversed into `entries/entries/parts/`. A trivial `gsutil du -s gs://.../ld/mt_afr_qc.mt/entries/` (or even `gsutil ls .../entries/entries/parts/ | head`) would have exposed the catastrophe 36h earlier and saved the entire 2026-05-19 and 2026-05-20 sessions.

3. **Lazy evaluation in Hail produces "completion" signals that are not commitment signals.** Cell 3/4/5's return-to-the-next-cell ONLY signals that the IR for the write was submitted and the driver finalized accounting. It does not signal that bucket data is committed. Cell 7's `count_rows()` invocations were the FIRST operations that would have forced contents materialization — and they collapsed exactly because contents were missing.

4. **Cost-EV reasoning under iframe-hostility biased toward "let it complete"**. Path B1 was selected on the assumption that the un-refactored monolithic run was producing valid outputs. If the verification methodology had been able to detect empty-entries earlier, Path B2 (kill + refactor) would have been the obvious choice.

The evidence needed but not gathered:
- A `gsutil ls -r gs://.../ld/mt_afr_qc.mt/entries/entries/parts/ | head` check after Cell 3 returned.
- A `gsutil du -s gs://.../ld/mt_afr_qc.mt/` check (would have shown ~tens of KB, not GB).
- An eager `hl.read_matrix_table(gs://.../ld/mt_afr_qc.mt).count_cols()` from a fresh terminal/subprocess on the env (would have either hung, thrown, or returned 0).
- A `tail -200 /tmp/hail.log` check between cells for "Successfully wrote" / "Wrote MatrixTable" lines vs JIT-compile-truncation patterns.

---

## Refactored Code Verdict

The refactored `load_qc_cohort` at HEAD does **NOT** prevent this failure mode and would reproduce it if fired.

Specific evidence:
- `tests/m3/test_aou_ld_panel_local.py:358-381` `test_has_checkpoint_returns_*` tests verify the `_has_checkpoint(uri)` contract only checks `_SUCCESS` existence; it does NOT distinguish "stub MT" from "populated MT". Test at line 372: `test_has_checkpoint_returns_false_when_mt_dir_exists_but_no_success` covers the "interrupted write" case (no `_SUCCESS`), but there is NO test for "MT dir exists AND has `_SUCCESS` AND has stub entries". This is the exact pathology that struck on AoU.
- `tests/m3/test_aou_ld_panel_local.py:638-681` `test_load_qc_cohort_auto_recovers_from_orphan_mt` exercises the sidecar-absent-MT-present recovery path — but the MT in that test setup IS populated (the first fire wrote real data against the synthetic fixture). The test never sets up the "empty-entries with `_SUCCESS`" condition.
- `aou_ld_panel.py:687` final `mt = mt.checkpoint(ckpt, overwrite=True)` has NO post-write contents validation. No `count_cols()`, no `count_rows()`, no `assert hl.hadoop_is_dir(ckpt + "/entries")`.
- The auto-resume state machine at lines 540-590 will detect a stub MT with `_SUCCESS` + matching sidecar and transition to `RESUME_FROM_POST_SAMPLE_QC` (deepest valid state), skipping Phase 1 + Phase 2 and re-running Phase 3's `variant_qc` on the empty MT. The result is another empty-`_SUCCESS`-marked MT.

**The refactor needs an additional patch before any rebuild fires** (see Fix Strategy below).

---

## Fix Strategy (high-level only)

Mode: `find_root_cause_only` — parent orchestrator plans the rebuild. This section provides guidance only.

### Code patches needed (mandatory before rebuild)

1. **`src/python/aou_ld_panel.py`:**
   - Add helper `_validate_checkpoint_populated(uri) -> bool` that:
     - Confirms `_SUCCESS` exists (existing `_has_checkpoint` check)
     - Confirms `entries/entries/parts/` directory exists AND has at least 1 file > minimum-byte-size (e.g., 1 KB to filter out stub footers)
     - Optionally confirms `hl.read_matrix_table(uri).count_cols() > 0` (more rigorous but adds a Spark job per check)
   - Modify `_has_checkpoint(uri)` callers in the auto-resume state machine (lines 552-587) to use `_validate_checkpoint_populated` instead. A stub MT with `_SUCCESS` but empty entries should NOT trigger RESUME — it should trigger auto-force-fresh recovery (WARN + treat as orphan).
   - Modify `load_qc_cohort` intermediate checkpoint writes (lines 641, 667) and final checkpoint write (line 687) to add a post-write assertion:
     ```
     mt = mt.checkpoint(uri, overwrite=...)
     # Post-write contents validation — defense against the W1 empty-entries pathology.
     assert _validate_checkpoint_populated(uri), \
         f"checkpoint write completed _SUCCESS but entries are missing or stub-only at {uri}; refusing to proceed"
     ```
   - This assertion failing should raise loudly inside `load_qc_cohort`, NOT silently continue.

2. **`tests/m3/test_aou_ld_panel_local.py`:**
   - Add pure-Python test `test_validate_checkpoint_populated_rejects_stub_entries` that creates a fake MT directory with `_SUCCESS` + tiny-stub rows files + NO entries directory; asserts `_validate_checkpoint_populated` returns False.
   - Add pure-Python test `test_validate_checkpoint_populated_rejects_empty_entries_dir` similar but with an empty entries/ directory present.
   - Add pure-Python test `test_has_checkpoint_vs_validate_diverge_on_stub_mt` documenting the contract.
   - Add live-Hail test (will SKIP on HPC, run on AoU): `test_load_qc_cohort_post_write_assertion_fires` that monkeypatches `mt.checkpoint()` to produce a stub MT and confirms `load_qc_cohort` raises.

3. **`.planning/notebooks/AOU-1_template.ipynb`:** add a new Cell 3.5 / Cell 4.5 / Cell 5.5 between each load_qc_cohort call, fired immediately after the cell returns, with:
   ```python
   # Mandatory post-write bucket-contents validation (m3-W1-empty-mt-catastrophe regression guard).
   import subprocess
   bucket_uri = _qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], 'afr', False)  # match cell
   r = subprocess.run(['gsutil', 'du', '-s', bucket_uri], capture_output=True, text=True)
   assert r.returncode == 0, f"bucket inspection failed: {r.stderr}"
   size_bytes = int(r.stdout.split()[0])
   assert size_bytes > 10**9, f"MT at {bucket_uri} is only {size_bytes} bytes — expected GB-scale; refusing to proceed"
   print(f"OK: {bucket_uri} populated ({size_bytes / 10**9:.1f} GB)")
   ```
   This is independent of the Python `load_qc_cohort` assertion — it's a notebook-side fail-fast gate that operates on bucket state directly, not on Hail-internal state.

### Pre-fire validation requirements (mandatory)

Before ANY $1500+ rebuild fires:
- All new tests pass on HPC (the pure-Python ones).
- Manual fresh-fire chr22 smoke test on AoU (per `260518-qcr-DESIGN.md` §5.2) using `interval_filter="chr22"` — produces small `_chr22`-suffixed intermediates that can be inspected directly via gsutil within minutes; confirms the new assertions fire correctly under live Hail.
- Hail repo issue scan for "_SUCCESS empty entries partition" — confirm the proximate Hail mechanism is documented; consider opening a Hail issue if it isn't.
- Confirm CDR version (`v8` per `CDR_VERSION` constant) and AUX paths still resolve.
- Confirm 16× n1-highmem-16 (256 vCPU) cluster sizing per AOU-LD-PIPELINE.md §11.0.
- Confirm Reattachable PD per `feedback_aou_use_persistent_disk`.

### Per-MT post-write verification steps (mandatory between MTs)

Run AS PART OF the notebook, NOT as an after-the-fact human-eyeball check:
1. `gsutil du -s gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}{_sens}_qc.mt/` — assert > 1 GB (AFR sens cohort smallest, expect ~5-20 GB; AFR primary ~10-40 GB; EUR primary ~20-100 GB).
2. `gsutil ls gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}{_sens}_qc.mt/entries/entries/parts/ | wc -l` — assert > 100 part files.
3. `gsutil cat gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}{_sens}_qc.mt/metadata.json.gz | gunzip | python -c "import json,sys; m=json.load(sys.stdin); assert 'n_partitions' in m or 'partitions' in str(m), m"` — assert metadata is well-formed.
4. From a fresh Python subprocess (NOT the same kernel that did the write): `hl.read_matrix_table(uri).count_cols()` — assert returns expected sample count ±10%.
5. Write a per-MT validation log entry to `gs://${WORKSPACE_BUCKET}/forensics/mt_validation_${ancestry}_${timestamp}.txt` capturing all 4 checks.

These checks happen BEFORE the next cell fires.

### Cost expectations

- Pre-fire chr22 smoke test: ~$10-20 (small Dataproc fire, ~30 min).
- Production rebuild for all 3 cohorts on 16×n1-highmem-16 (256 vCPU): ~$1500-2500 (matches symptom block estimate).
- Post-write validation overhead: ~$5-15 per MT (3 fresh-subprocess count_cols calls = 3 short Spark jobs).
- Risk-mitigation: chr22 smoke catches the empty-entries pathology BEFORE production spend.

### Risk register for the rebuild

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Empty-entries pathology recurs on refactored code | HIGH (refactor doesn't defend) | $1500-2500 wasted | Code patches above (mandatory) + chr22 smoke pre-fire |
| Different Hail-internal mechanism produces a NEW failure mode | MEDIUM (we don't yet know the exact root cause of the empty-write) | $1500-2500 wasted | hail.log forensics on the W1 monolithic-run log (NOT just the truncated EUR snippet) to identify the exact write-truncation mechanism; consider opening Hail issue |
| 2026-05-21 Hail read-probe reveals MT #1 is unreadable (not just empty) | MEDIUM | Need to re-investigate root cause | Wait for parent-context probe results before finalizing rebuild plan |
| Cluster sizing assumption wrong for refactored intermediate-checkpoint cycle (more I/O than monolithic) | LOW-MEDIUM | Longer runtime, higher cost | Budget 1.5× expected cost; provision Dataproc autoscaling headroom |
| AoU clone re-pull doesn't get the refactor (git workflow issue) | LOW | Refactor not actually used, identical failure | Pre-fire: verify AoU clone HEAD matches origin/main and includes `_validate_checkpoint_populated` helper |
| New post-write assertions fire on legitimate Hail edge cases (e.g., an ancestry filter that produces zero rows for some chrom) | LOW | False-positive halt | Tune size thresholds based on chr22 smoke results; document override path |

---

## Files Inspected

Absolute paths of files read or git-inspected during this investigation:

- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/aou_ld_panel.py (1052 lines; FULL file read)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/notebooks/AOU-1_template.ipynb (full; 9 cells)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_aou_ld_panel_local.py (810 lines; FULL file read)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-SUMMARY.md (211 lines; FULL)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-PLAN.md (partial)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/phases/m3-aou-afr-ld-panel-build/m3-01-W1-aou-cohort-and-hard-gates-SUMMARY.md (194 lines; FULL — note this is the 2026-04-30 governance/notebook-authoring SUMMARY, NOT the AoU fire SUMMARY)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/WAVE-1-CLOSEOUT-CHECKLIST.md (254 lines; FULL)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/STATE.md (read via persisted output: lines 1-200 + key W1 entries lines 429-560)
- /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/amendments/AOU-LD-PIPELINE.md (§11.0 lines 462-494)
- Git commits inspected via `git show --stat`:
  - 50f071c (docs stub — NOT the refactor)
  - bd144a6 (refactor body head)
  - 36e8062 (checkpoint-suffix bug fix 2026-05-12)
  - 8cc6f64 (RegionPool OOM remediation)
  - a17b714, 589e004 (resilience test cherry-picks)
  - 4beeb26 (WAVE-1-CLOSEOUT-CHECKLIST commit)
- Git history scans:
  - `git log --oneline -- src/python/aou_ld_panel.py` (full evolution)
  - `git log --oneline -- .planning/notebooks/AOU-1_template.ipynb`
  - `git log --oneline 'origin/main' --since="2026-05-12" --until="2026-05-21"`

Memory files cross-referenced (via project memory bake at session start):
- feedback_aou_dataproc_pyspark_submit_args.md
- feedback_aou_websocket_drop_zombie_pattern.md
- feedback_aou_cluster_sizing_for_ld_panel.md
- feedback_aou_hail_driver_quiet_vs_wedge.md
- feedback_aou_spark_ui_stack_trace_verification.md (← the memory whose discriminator claim this investigation REFUTES)
- feedback_aou_use_persistent_disk.md
- feedback_extract_reusable_utilities.md

Files NOT inspected (deemed unnecessary given evidence):
- .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
- .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
- .planning/phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md
- .planning/quick/260512-* / 260514-* / 260517-* sub-directories (forensic trail confirmed via STATE.md narratives)

---

## Resolution

root_cause: |
  Verification-method false-positive (gsutil `_SUCCESS` + `metadata.json.gz` listing
  and Spark UI stack-trace signature matching do NOT validate MT entries-data
  existence) compounded by Hail `mt.checkpoint()`'s driver-side `finalize()` writing
  `_SUCCESS` based on tasks-reported-complete accounting without contents validation,
  under extreme `spark.executor.cores=1 / mem=5g` per-executor pressure that can
  silently truncate writes after Parquet schema footers. The refactored
  load_qc_cohort at HEAD does NOT defend against this failure mode and would
  reproduce it. The EUR (Cell 5) write almost certainly never executed at all
  (hail.log truncated 28s after IR submit; no Spark stages for EUR write;
  mt_eur_qc.mt directory absent from bucket).

fix: |
  HIGH-LEVEL ONLY (mode = find_root_cause_only). Three code patches required
  before any rebuild fires:
  (1) src/python/aou_ld_panel.py — add _validate_checkpoint_populated helper,
      replace _has_checkpoint uses in auto-resume state machine, add post-write
      assertion after every mt.checkpoint() call.
  (2) tests/m3/test_aou_ld_panel_local.py — add regression tests for stub-entries
      detection.
  (3) .planning/notebooks/AOU-1_template.ipynb — insert Cell 3.5/4.5/5.5 gsutil-du
      assertions between cells.
  Plus chr22 smoke fire (per 260518-qcr DESIGN §5.2) before production rebuild.

verification: |
  Not applicable — find_root_cause_only mode. Parent orchestrator will plan
  the rebuild and the rebuild's verification.

files_changed: []
