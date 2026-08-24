---
name: aou-ld-pipeline
description: Use when running, re-running, resuming, monitoring, or debugging the All of Us (AoU) genome-wide cohort build (AOU-1) or per-region LD reference panel (AOU-2) on a Dataproc/Hail cluster — covers the manual edits to re-apply on a fresh clone, env guards, verification discipline, cluster sizing, the RW2.0-mirror / VPC-SC perimeter facts, the Wave 2 gate sequence, and the known catastrophe→recovery recipes. Triggers on: AoU pipeline, AOU-1, AOU-2, cohort build, mt_afr_qc / mt_eur_qc / mt_afr_pca_selfid_qc, LD panel, Dataproc fire, Hail Workbench, self-report sensitivity cohort, empty-MT, finalize catastrophe.
---

# AoU genome-wide LD pipeline — operational runbook

The single source of truth for running the AoU cohort + LD pipeline without repeating past failures. The narrative history lives in `.planning/STATE.md`, `.planning/phases/m3-aou-afr-ld-panel-build/`, and `.planning/debug/`; this skill is the distilled, durable operating manual.

## Coordinates (current, RW2.0 / v8)
- Workspace `aou-rw-476cdac2` · project `wb-perky-corn-6639` (`GOOGLE_PROJECT`)
- **Canonical bucket `gs://rw-migration-aou-rw-476cdac2`** (writes go here; everything under `…/ld/`)
- WGS v8 (requester-pays) `gs://vwb-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt`
- CDR `C2024Q3R8` (v8) — in-perimeter Verily dataset `wb-silky-artichoke-2408.C2024Q3R8`
- Repo `github.com/carter-clinton/coloc_analysis`; **run branch = `m3-W2-aou-deltas`** (see "Branch trap")

## The invariants (these are the mistakes — do not repeat them)

1. **`_SUCCESS` is NOT evidence of data.** Hail writes `_SUCCESS` on driver-side task accounting, not contents. ALWAYS verify a written MT at the data layer: `gsutil du -s …/<mt>/entries/rows/parts/` (≫ 1 GB) **and** `count_cols`/`count_rows` off the MT. The 2026-05-21 empty-MT catastrophe ($2,100) and the 2026-06-10 empty-final catastrophe both passed a `_SUCCESS` check over 0 bytes. (`[[feedback_aou_success_marker_not_evidence_of_data]]`, `[[feedback_hail_checkpoint_contract_violation]]`)
   - ★ **Platform-team CONFIRMED 2026-07-24** (AoU support ticket 57144, K. Actkins),
     verbatim: *"Hail's mt.checkpoint() will still write a dataset and produce
     _SUCCESS markers even if the underlying MatrixTable being checkpointed is
     empty."* Their own recommendation matches ours — verify the MT held data
     **before** the write (`mt.count()`). This invariant is now vendor-confirmed,
     not only our 2026-05-21 forensics. (`DEC-2026-08-16-aou-credit-request-denied`)
2. **Liveness = GCS object listing / Spark stage advancing, NOT the kernel light or jstack.** For the per-chrom fan-out, poll `gsutil ls …/intermediate/ | grep …post_variant_qc` for chrom deltas. For a finalize, watch the Spark/YARN ResourceManager stage id + completed-tasks climbing. A quiet driver + flat CPU during an I/O/plan phase looks identical to a wedge — don't kill on the kernel light alone. (`[[feedback_aou_fanout_gcs_listing_arbiter]]`, `[[feedback_aou_hail_driver_quiet_vs_wedge]]`)
3. **A clean disconnect does NOT kill the server-side job.** The Dataproc job runs on the master; going home / a websocket drop is survivable (AFR-primary + EUR built across overnight disconnects). On reconnect, `ps`-confirm the kernel + JVM and reattach — **never a reflexive kernel restart.** What DID kill a finalize was a **stray browser navigation** away from the tab mid-write — keep the tab foregrounded during any finalize. (`[[feedback_aou_websocket_drop_zombie_pattern]]`)
4. **`force_fresh=False` on any resume.** `force_fresh=True` re-runs the whole genome from RAW (~15 h + cost). The auto-resume state machine validates intermediates with `_validate_checkpoint_populated` (contents, not marker) and resumes cheaply. Only pass `force_fresh=True` to overwrite known-contaminated checkpoints.
5. **Counts, not markers, gate every step.** A final count BELOW the input is EXPECTED (genome-wide `call_rate≥0.98` sample-QC drop); byte-identical to another cohort is the CONTAMINATION tell. Verify the path-builder, not just the count.

## RW2.0 is a MIRROR of legacy (and the VPC-SC perimeter)

The Researcher Workbench 2.0 (Verily) migration **mirrors** the legacy RW1.0 ("classic") workspace content — so legacy-bucket data is reachable/re-derivable. BUT the classic and Verily environments are **separate VPC-SC perimeters**: cross-perimeter transfer (classic CDR/bucket → Verily bucket) is **blocked on every self-serve path** (gsutil, service-account, project-switch, Console, PET-to-PET IAM — all by design, not a misconfig).

- **Resolution that works = regenerate in-perimeter.** When you need data that's stranded in the classic perimeter, re-derive it natively against the in-perimeter v8 CDR rather than transferring. This is how the self-report sidecar was produced (`extract_aou_self_report.py --cdr-dataset wb-silky-artichoke-2408.C2024Q3R8` → `…/ld/aux/self_report/self_report.tsv`, 633,547 rows / 99,788 `WhatRaceEthnicity_Black`), which ALSO version-matched it to the v8 cohorts (the stranded classic sidecar was v9 → a latent mismatch avoided).
- **Folder Sync** (Workbench UI) is the additive last-resort transfer; re-sync **overwrites** earlier-migrated files, so never point it at the live `…/ld/` MTs. Don't file an AoU cross-bucket ticket for this — in-perimeter regen obviates it.

## Branch trap — do NOT run from `main`

`origin/main` is a STALE, UNRELATED parallel history (re-init'd root, **no merge base** with the working line; frozen 2026-05-18) — it lacks the fan-out fix (`ab0853a`), the LD OOM-routing fix (`c6c32b3`), and the baked env guards. **A clone-from-`main` re-run wedges deterministically** on the first genome-wide action and/or OOMs the first dev-10 A.2 region. A merge is impossible across the unrelated histories; the resolution was to **flip the GitHub default branch to `m3-W2-aou-deltas`** — ✅ **DONE 2026-06-11.** Fresh `git clone` + SEED-001 auto-clone now land on the working line. Old `main` remains as a frozen orphan (do not use it). Still good practice before any fire: `git branch --show-current` (expect `m3-W2-aou-deltas`) + `git pull`.

## Fresh-clone re-run checklist (before "Run All")

> AOU-1 has a **DO NOT Run-All** protocol: run cohorts smallest→largest, stop and confirm each validation cell (3.5 / 4.5 / 5.5) before proceeding.

1. **Env panel (before Resume):** "Hail Genomics Analysis" Dataproc cluster (Hail pre-installed + YARN-wired; NOT a generic Spark cluster). Master `n2-standard-16` (64 GB floor); workers `n2-standard-16` to the vCPU quota, non-preemptible. (Dataproc has no persistent disk → bucket-first discipline.)
2. `git clone` → **`git checkout m3-W2-aou-deltas`** → **`git checkout -f`** (the Workbench's Jupyter clean/smudge filter re-dirties notebooks on every git op; `-f` is the only clean switch — note: this filter is Workbench-side, NOT a committed repo `.gitattributes`).
3. **Confirm the baked Cell-1a guards survived the filter** (see table). Run Cell 1a → 1a'' → 1b. Cell 1b ASSERTS `spark.executor.cores == '1'` and HALTS if the lever didn't bind.
4. **`echo $WORKSPACE_BUCKET`** in a terminal → must be `gs://rw-migration-aou-rw-476cdac2`, NOT a `gs://cloned-mybucket-…` placeholder.
5. **Sensitivity cohort only — the manual Cell 4 edits (NOT baked):** ensure the self-report sidecar exists at `…/ld/aux/self_report/self_report.tsv`; add `self_report_table_path=` (canonical path) to the Cell 4 `load_qc_cohort(...)` call; on a post-contamination rebuild also add `force_fresh=True` (after purging `mt_afr_pca_selfid_*`).
6. Run smallest→largest, verifying each at the data layer: Cell 3→3.5 (AFR primary) → 4→4.5 (AFR sens) → 5→5.5 (EUR) → 6 (disjoint AFR∩EUR=∅) → 7 (`cohort_summary_m3.tsv`).
7. **AOU-2:** the `WORKSPACE_BUCKET` hard pin is now **BAKED** into AOU-2 (cell index 5, before the `_normalize_bucket` read; quick `c3a3292`, gap C3 closed) — it hard-assigns `gs://rw-migration-aou-rw-476cdac2` and asserts in-kernel that it is NOT the `cloned-mybucket` placeholder. Confirm that cell ran (echoes the canonical bucket) before Cell 6/8. Set `USE_DEV_SUBSET` (`True`=dev-10/GATE 2, `False`=full 322/GATE 3).

- ⚠ **NEW 2026-08-24 (Cloud Analysis VM, native-plink producer) — `plink1.9` is NOT on the VM image.** `run_native_ld_panel.py` shells out to the literal `plink1.9` (`aou_ld_panel.build_plink_ld_command`, no flag); the image ships only `/opt/workbench-tools/binaries/bin/plink`, so Stage A stopped on `[Errno 2] 'plink1.9'` before any banking. On EVERY fresh VM, in the SAME shell that runs the producer: `mkdir -p ~/bin && cd ~/bin && wget -q https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20231211.zip && unzip -o plink_linux_x86_64_20231211.zip plink && mv -f plink plink1.9 && chmod +x plink1.9 && cd ~/coloc_analysis; export PATH="$HOME/bin:$PATH"; plink1.9 --version` → must print `PLINK v1.90b7.2 64-bit (11 Dec 2023)` (the pilot/fire-brief pin). Never shim a PLINK 2.x binary (`--r square bin4` semantics differ); `which plink || which plink1.9` is a WRONG check (passes on the wrong binary). Also check `/home/jupyter/native_ld_scratch/m3-W2-native-plink-panel.tsv` — a stale June-era 7-column mirror makes the producer fail-close; ROTATE it (`mv … .STALE.<UTC>`), never delete. Record: `.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md`; runbooks fixed `ed2924e`.

## Baked-vs-manual edit table

| Edit | Where | Status | Without it |
|---|---|---|---|
| `PYSPARK_SUBMIT_ARGS` `spark.executor.cores=1`/`memory=5g`/`driver.cores=1` (before pyspark import) | AOU-1 Cell 1a | **BAKED** `29d0a1f` | v8 partition-explosion RegionPool OOM kills the driver; `hl.init(spark_conf=)` is silently dropped on YARN |
| Requester-pays CUSTOM (`mode=CUSTOM`, `buckets=vwb-aou-datasets-controlled`, `project.id={GOOGLE_PROJECT}`) | AOU-1 Cell 1a | **BAKED** `29d0a1f` | WGS reads 400 "requester pays … no user project" |
| `WORKSPACE_BUCKET` **HARD** override (`os.environ[…] = …`, not `setdefault`) | AOU-1 Cell 1a'' | **BAKED** `29d0a1f` | saved template injects dead `gs://cloned-mybucket-…` 404 → all writes lost |
| `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` literal backfill | AOU-1 Cell 1a'' | **BAKED** `29d0a1f` | Cell 3 `mt_path` KeyErrors (migrated cluster doesn't auto-set it) |
| **`self_report_table_path=` (sensitivity)** | AOU-1 Cell 4 | **MANUAL** ⚠️ | code default resolves under the read-only controlled-tier aux base → sens build fails / silently no-ops (the contamination bug) |
| **`force_fresh=True` (post-contamination sens rebuild only)** | AOU-1 Cell 4 | **MANUAL** ⚠️ | auto-resume re-ships the contaminated checkpoint |
| `WORKSPACE_BUCKET` **HARD** override (`os.environ[…] = …`, not `setdefault`) + `cloned-mybucket` assert | AOU-2 cell idx 5 (before `_normalize_bucket`) | **BAKED** `c3a3292` (gap C3 closed) | LD `.npz`/`.bm` + MT reads resolve to the 404 placeholder in a fresh kernel → lost writes |
| `git checkout -f` | terminal | **MANUAL** | Workbench filter re-dirties notebooks, can strip baked guards |

> **Smoke-template trap:** `AOU-1-chr22-smoke_template.ipynb` Cell 1a'' uses the UNSAFE `os.environ.setdefault(...)`. Use the **production** `AOU-1_template.ipynb` (hard assign). Never copy the bucket line from the smoke notebook.

## Cohort build (AOU-1) — specifics
- **Use the production template** (genome-wide, `interval_filter=None`). The bucket MTs after a chr22 smoke are chr22-ONLY — re-running the smoke overwrites the production paths.
- **Per-chrom fan-out** (`ab0853a`): `count_cols`/Py4J mutual-wait on the un-pruned genome-wide plan is resolved by recursing 22× (one autosome each), `union_rows`, then sample-QC ONCE over the union. Arbiter = `intermediate/…post_variant_qc_chrN` listing → 22.
- **EUR is the long pole** — watch the GC-heavy `aggregate_cols`/`collectDArray` driver gather (scales with samples × partitions; partition-capped 2048). Judge by the `entries/rows/parts/` write timestamp + assertion, not thread state.
- **Expected shapes:** AFR_pca 73,122 × 20,767,864 · EUR_pca 220,098 × 11,375,140 · AFR_pca_selfid 62,557 × 20,817,925 (strict subset; `self_report` present).

## LD compute (AOU-2) — specifics
- **Region set = `config/ld_regions.tsv`** (322 = 161 M2 regions × 2 ancestries), **NOT** `regions_curated_grch38.csv` (pre-reframe candidate set). `USE_DEV_SUBSET=True` → `config/ld_regions_dev.tsv` (10).
  - ⚠ **BANNER 2026-08-12 — the `322 = 161 × 2` figure DESCRIBES THE RETIRED HAIL A.3 PRODUCER.** Measured at HEAD, `config/ld_regions.tsv` carries **552 data rows = 276 region_ids × 2 ancestries** (`AFR` 276, `EUR` 276), not 322. **The current producer is `src/python/run_native_ld_panel.py` — native plink1.9, Hail-free, ONE stopped Cloud Analysis VM, AFR-only, 276 regions**, writing per-region `.npz` directly to `gs://<bucket>/ld/AFR_aou/`. `USE_DEV_SUBSET` and the AOU-2 notebook belong to the retired path. The line above is preserved as the historical record of the A.3 scoping.
- **Path routing `_route_region_path` (`c6c32b3`):** any A.1/A.2 region with span > 10 Mb → A.3 `BlockMatrix.write` (driver-OOM span-veto). `region_class` labels are advisory only.
- **A.3 write must NOT be `hl.ld_matrix(...).write()` (2026-06-12 lowering hang, commits `125b353`/`a554c26`).** The fused `ld_matrix` IR write runs INTERPRETED (per Hail `CanLowerEfficiently.scala` *every* `BlockMatrixWrite` is interpreted — the "BlockMatrixIR lowering not yet efficient/scalable" warning fires on ALL writes and is NOT a pass/fail signal) and drives an un-materialized matmul through a single driver-side `ContextRDD.collect` → hangs (region_00006: 736/900 blocks in ~73 min). Fix = `_write_a3_banded_correlation_bm`: `row_correlation → checkpoint(scratch) → locus_windows → sparsify_row_intervals(blocks_only=False) → write(stage_locally=True)`; the checkpoint materializes the matmul so the final write reads CONCRETE blocks (cheap). Byte-identical numerics to `ld_matrix`. **OPEN (CR-01, GATE-3 blocker):** ordering A (checkpoint dense correlation, then band) writes the full O(n²) dense correlation to scratch (~2 TB for the ~710k-var region). Pan-UKBB uses ordering B (band-then-checkpoint, ~GB) at scale → B is the leading default; the `scripts/a3_blockmatrix_lowering_repro.py` cluster experiment (gated on WALL-CLOCK COMPLETION, not the warning) decides A vs B before the production fire. (`.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md` + `-REVIEW.md`)
- **Export MAF 0.005** (preserves AFR rare-allele signal; overrideable to spec's 0.01). Signed Pearson **r** float32. Per-region radius = span + 500 kb, capped 50 Mb → **the 16 xlarge cells are 50-Mb-BANDED; downstream `ld_npz_to_rds.R` / SuSiE-RSS must treat them as banded.**
- **Halt-checks:** Q10 (>50% variant drop at MAF 0.005 vs 0.01 → halt); D-M3-07 (dev-10 self-ID-vs-PCA LD r < 0.995 → escalate self-ID to a full fire).
- **Egress = 44 export requests** (22 chr × 2 anc) via Files UI, each a Carter human action (~2–5 business-day SLA each), logged to `.planning/amendments/aou-egress-audit-log.md`. **Gated on GATE 0.**
  - ⚠ **BANNER 2026-08-12 — the `44 export requests` figure DESCRIBES THE RETIRED HAIL A.3 PRODUCER.** The current native-plink path is **AFR-only**, so egress is redefined to **at most 22 AFR chromosome groups plus within-chromosome size splits** (`.planning/amendments/m3-egress-and-validation-protocol-addendum.md` §(a), *"44 → at most 22"*). The Files-UI mechanics, the SLA, the audit-log discipline and the GATE 0 dependency all still apply unchanged. The line above is preserved as the historical record.

## Wave 2 gate sequence

> ⚠ **BANNER 2026-08-12 — READ BEFORE USING THIS TABLE. It is SPLIT BY ROW, not stale as a whole.**
>
> - **GATE 0, GATE 1 and GATE 1.5 are LIVE and AUTHORITATIVE.** They are *institutional* gates (egress classification, CDR pin + cost/credit, cohort rebuild) and they survive the producer rescope untouched.
> - **GATE 2 and GATE 3 DESCRIBE THE RETIRED HAIL `BlockMatrix` PATH-A.3 PRODUCER**, which was **re-scoped away**. The A.3 lowering hang, the CR-01 ~2 TB dense-scratch ordering question, `USE_DEV_SUBSET`, the dev-10 fire, *"full 322-cell production + 44 egress"* and the atomic-final-write Phase-2 dependency all belong to that dead path. **Do NOT present them as live blockers.**
> - **The current producer is `src/python/run_native_ld_panel.py`** — native plink1.9, **Hail-free**, ONE STOPPED Cloud Analysis VM, **AFR-only**, **276 regions** (`config/ld_regions.tsv` = 552 rows = 276 × 2 ancestries), writing per-region `.npz` directly to `gs://<bucket>/ld/AFR_aou/`. Egress is at most 22 AFR chromosome groups plus size splits.
> - **The current gate surface is the READY-TO-FIRE runbook — `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md` (2026-08-12 EVENING; 11 Carter-only items in fire order), which WRAPS the corrected `.planning/quick/260811-rcw-…/260811-rcw-PRE-FIRE-GATE-REVIEW.md`.** Enter through the runbook, never the review directly: the review's §2/§5/§6 "PRE-FIRE 1 ⛔ OPEN, a Carter decision" rows are **SUPERSEDED — PRE-FIRE 1 LANDED 2026-08-12 (`5284505`, per-region occlusion-manifest upload), so 1b branch (i) is the live default**, and its §4-row-4 index-origin question is settled code-side (runbook item 8: run the gated test; never hand-compare line numbers). The review's `## Corrections (2026-08-12)` section still applies (its v1 liveness-poll command was double-prefixed and would have FALSE-PASSED its own pre-fire check).
> - ⚠ **`GATE 1.5`'s cohort MTs are MUTABLE state the fire reads.** Re-verify them at gate time per invariant 1 (`du` **and** `count_cols`/`count_rows`) — a `_SUCCESS` marker is not evidence of data.
>
> No row below is deleted; every historical row is preserved.

- ✅ **GATE 1.5** — genome-wide cohort rebuild (3 MTs). DONE + verified (cohort_summary 3 rows). **[LIVE 2026-08-12 — but re-verify the MT contents at gate time; see the banner.]**
- ✅ **GATE 0** — **[LIVE 2026-08-12]** AoU egress classification of the LD matrices. **RESOLVED: RULED PASS 2026-04-28** (institutional basis; `.planning/amendments/aou-egress-audit-log.md`). Aggregate stats (every cell over n≥60k AFR / n≥130k EUR → clears the n≥20 floor) → standard AoU **per-file egress review at export time**, NOT a per-data-class letter. Not a blocker; append each of the 44 export bundles to the audit log as they're reviewed at Wave 4.
- ✅ **GATE 1** — **[LIVE 2026-08-12]** CDR pin (v8) + cost/credit. **CLEARED 2026-06-12.** ⚠ The cost/credit half is a live balance — check it in the Workbench billing panel before a $385–1,084 commit.
- 🟠 **GATE 2** — ⚠ **RETIRED PRODUCER (banner 2026-08-12): this row describes the killed Hail A.3 path and is NOT a live blocker.** dev-10 LD fire + AOU-4 memo. **FIRED 2026-06-12 → PAUSED:** region_00006 hit the A.3 lowering hang (above). Fix landed + double-reviewed; **open = the `a3_blockmatrix_lowering_repro.py` cluster ordering experiment (A vs B) then re-fire region_00006.** Cluster STOPPED ($0); needs a restart.
- 🔴 **GATE 3** — ⚠ **RETIRED PRODUCER (banner 2026-08-12): this row describes the killed Hail A.3 path and is NOT a live blocker.** The current equivalent is m3-04c Task 3 via the 260812-ox1 READY-TO-FIRE runbook, which wraps the corrected 260811-rcw PRE-FIRE gate review (native plink, AFR-only, 276 regions, ≤22 egress groups; PRE-FIRE 1 landed 2026-08-12). full 322-cell production + 44 egress. **BLOCKED on CR-01** (the A.3 ~2 TB dense-scratch ordering question) + land the durable atomic-final-write fix first.

## Catastrophe → recovery recipes
- **Empty final MT** (`_SUCCESS` over 0-byte; H1 = driver killed mid-finalize-flush, often a stray navigation): intermediates are intact → **finalize-only re-drive** from the 22 `…post_variant_qc_chrN` (minutes, not 15 h). Prove with a read-only `_scratch` dry-run, verify cols/rows/du, then `gsutil -m rsync -r -d` scratch→live and re-verify. Do NOT `force_fresh=True`. (`.planning/debug/m3-W2-afr-sens-empty-final-merge.md`)
- **Sensitivity == primary (byte-identical, silent no-op):** the self-report filter never sourced. Fix = source `self_report_table_path` + `SENS_FILTER_VERSION=2` matching `WhatRaceEthnicity_Black`; verify path-builder isolation (`_pca_selfid` token), not just the count. (`.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md`)
- **`count_cols` wedge (Py4J mutual-wait) on the first genome-wide action:** the un-pruned plan; fixed by the per-chrom fan-out (`ab0853a`). (`.planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md`)
- **Sample-axis collapse (N×0 after sample-QC):** variant_qc must run BEFORE sample_qc so `call_rate` is measured over QC-passing variants. (`resolved/m3-gatec-sample-callrate-ordering-collapse.md`)
- **A.3 BlockMatrix write hang (`hl.ld_matrix(...).write()` interpreted/driver-bound):** does NOT complete at large `n_var` (122k+); the driver `main` parks in a Py4J recv while a single `ContextRDD.collect` grinds the interpreted `BlockMatrixWrite`. The lowering warning is NOT the signal (it fires on every write). Kill via **Spark-UI job-kill** (`POST /jobs/job/kill/?id=<n>` direct to the driver UI; a soft kernel interrupt won't take through the Py4J block), which raises a clean SparkException and frees the kernel/JVM session. Delete the orphan partial `.bm` (no `_SUCCESS`). Fix = `_write_a3_banded_correlation_bm` (materialize the correlation via `checkpoint` before the banded write). (`.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md`)

## Known surviving risk (durable atomic-final-write fix — PHASE 1 landed, PHASE 2 pending)
The final-output write validates AFTER `_SUCCESS`. **Phase 1 (landed 2026-06-11):** `_apply_sample_qc_and_finalize` now stamps a `_VALIDATED` marker after the non-empty assert, and `_final_is_trustworthy()` (contents-only gate; the marker is documentation, never a trust fast-path — a stale marker must not vouch for re-emptied contents) is available for consumers. **Phase 2 (PENDING, needs the cluster):** the protective value is unrealized until the **AOU-2 / AOU-4 notebook readers call `_final_is_trustworthy(final_uri)` and raise on False** before `hl.read_matrix_table` — until then consumers still read the final blind. Land Phase 2 + chr22 smoke before GATE 3. See `.planning/phases/m3-aou-afr-ld-panel-build/DURABLE-FIX-DESIGN-atomic-final-write.md`.
