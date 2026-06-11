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
2. **Liveness = GCS object listing / Spark stage advancing, NOT the kernel light or jstack.** For the per-chrom fan-out, poll `gsutil ls …/intermediate/ | grep …post_variant_qc` for chrom deltas. For a finalize, watch the Spark/YARN ResourceManager stage id + completed-tasks climbing. A quiet driver + flat CPU during an I/O/plan phase looks identical to a wedge — don't kill on the kernel light alone. (`[[feedback_aou_fanout_gcs_listing_arbiter]]`, `[[feedback_aou_hail_driver_quiet_vs_wedge]]`)
3. **A clean disconnect does NOT kill the server-side job.** The Dataproc job runs on the master; going home / a websocket drop is survivable (AFR-primary + EUR built across overnight disconnects). On reconnect, `ps`-confirm the kernel + JVM and reattach — **never a reflexive kernel restart.** What DID kill a finalize was a **stray browser navigation** away from the tab mid-write — keep the tab foregrounded during any finalize. (`[[feedback_aou_websocket_drop_zombie_pattern]]`)
4. **`force_fresh=False` on any resume.** `force_fresh=True` re-runs the whole genome from RAW (~15 h + cost). The auto-resume state machine validates intermediates with `_validate_checkpoint_populated` (contents, not marker) and resumes cheaply. Only pass `force_fresh=True` to overwrite known-contaminated checkpoints.
5. **Counts, not markers, gate every step.** A final count BELOW the input is EXPECTED (genome-wide `call_rate≥0.98` sample-QC drop); byte-identical to another cohort is the CONTAMINATION tell. Verify the path-builder, not just the count.

## RW2.0 is a MIRROR of legacy (and the VPC-SC perimeter)

The Researcher Workbench 2.0 (Verily) migration **mirrors** the legacy RW1.0 ("classic") workspace content — so legacy-bucket data is reachable/re-derivable. BUT the classic and Verily environments are **separate VPC-SC perimeters**: cross-perimeter transfer (classic CDR/bucket → Verily bucket) is **blocked on every self-serve path** (gsutil, service-account, project-switch, Console, PET-to-PET IAM — all by design, not a misconfig).

- **Resolution that works = regenerate in-perimeter.** When you need data that's stranded in the classic perimeter, re-derive it natively against the in-perimeter v8 CDR rather than transferring. This is how the self-report sidecar was produced (`extract_aou_self_report.py --cdr-dataset wb-silky-artichoke-2408.C2024Q3R8` → `…/ld/aux/self_report/self_report.tsv`, 633,547 rows / 99,788 `WhatRaceEthnicity_Black`), which ALSO version-matched it to the v8 cohorts (the stranded classic sidecar was v9 → a latent mismatch avoided).
- **Folder Sync** (Workbench UI) is the additive last-resort transfer; re-sync **overwrites** earlier-migrated files, so never point it at the live `…/ld/` MTs. Don't file an AoU cross-bucket ticket for this — in-perimeter regen obviates it.

## Branch trap — do NOT run from `main`

`origin/main` is a STALE, UNRELATED parallel history (re-init'd root, **no merge base** with the working line; frozen 2026-05-18) — it lacks the fan-out fix (`ab0853a`), the LD OOM-routing fix (`c6c32b3`), and the baked env guards. **A clone-from-`main` re-run wedges deterministically** on the first genome-wide action and/or OOMs the first dev-10 A.2 region. A merge is impossible across the unrelated histories; the resolution (chosen 2026-06-11, non-destructive) is to **flip the GitHub default branch to `m3-W2-aou-deltas`** (repo Settings → Branches). Until that flip lands, every re-run MUST `git checkout m3-W2-aou-deltas`, and SEED-001 auto-clone (pulls the default branch) stays dormant.

## Fresh-clone re-run checklist (before "Run All")

> AOU-1 has a **DO NOT Run-All** protocol: run cohorts smallest→largest, stop and confirm each validation cell (3.5 / 4.5 / 5.5) before proceeding.

1. **Env panel (before Resume):** "Hail Genomics Analysis" Dataproc cluster (Hail pre-installed + YARN-wired; NOT a generic Spark cluster). Master `n2-standard-16` (64 GB floor); workers `n2-standard-16` to the vCPU quota, non-preemptible. (Dataproc has no persistent disk → bucket-first discipline.)
2. `git clone` → **`git checkout m3-W2-aou-deltas`** → **`git checkout -f`** (the Workbench's Jupyter clean/smudge filter re-dirties notebooks on every git op; `-f` is the only clean switch — note: this filter is Workbench-side, NOT a committed repo `.gitattributes`).
3. **Confirm the baked Cell-1a guards survived the filter** (see table). Run Cell 1a → 1a'' → 1b. Cell 1b ASSERTS `spark.executor.cores == '1'` and HALTS if the lever didn't bind.
4. **`echo $WORKSPACE_BUCKET`** in a terminal → must be `gs://rw-migration-aou-rw-476cdac2`, NOT a `gs://cloned-mybucket-…` placeholder.
5. **Sensitivity cohort only — the manual Cell 4 edits (NOT baked):** ensure the self-report sidecar exists at `…/ld/aux/self_report/self_report.tsv`; add `self_report_table_path=` (canonical path) to the Cell 4 `load_qc_cohort(...)` call; on a post-contamination rebuild also add `force_fresh=True` (after purging `mt_afr_pca_selfid_*`).
6. Run smallest→largest, verifying each at the data layer: Cell 3→3.5 (AFR primary) → 4→4.5 (AFR sens) → 5→5.5 (EUR) → 6 (disjoint AFR∩EUR=∅) → 7 (`cohort_summary_m3.tsv`).
7. **AOU-2:** run in the same kernel as AOU-1 (so `WORKSPACE_BUCKET` is pinned) OR `export WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2` first — AOU-2 does NOT pin it itself (gap C3). Set `USE_DEV_SUBSET` (`True`=dev-10/GATE 2, `False`=full 322/GATE 3).

## Baked-vs-manual edit table

| Edit | Where | Status | Without it |
|---|---|---|---|
| `PYSPARK_SUBMIT_ARGS` `spark.executor.cores=1`/`memory=5g`/`driver.cores=1` (before pyspark import) | AOU-1 Cell 1a | **BAKED** `29d0a1f` | v8 partition-explosion RegionPool OOM kills the driver; `hl.init(spark_conf=)` is silently dropped on YARN |
| Requester-pays CUSTOM (`mode=CUSTOM`, `buckets=vwb-aou-datasets-controlled`, `project.id={GOOGLE_PROJECT}`) | AOU-1 Cell 1a | **BAKED** `29d0a1f` | WGS reads 400 "requester pays … no user project" |
| `WORKSPACE_BUCKET` **HARD** override (`os.environ[…] = …`, not `setdefault`) | AOU-1 Cell 1a'' | **BAKED** `29d0a1f` | saved template injects dead `gs://cloned-mybucket-…` 404 → all writes lost |
| `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` literal backfill | AOU-1 Cell 1a'' | **BAKED** `29d0a1f` | Cell 3 `mt_path` KeyErrors (migrated cluster doesn't auto-set it) |
| **`self_report_table_path=` (sensitivity)** | AOU-1 Cell 4 | **MANUAL** ⚠️ | code default resolves under the read-only controlled-tier aux base → sens build fails / silently no-ops (the contamination bug) |
| **`force_fresh=True` (post-contamination sens rebuild only)** | AOU-1 Cell 4 | **MANUAL** ⚠️ | auto-resume re-ships the contaminated checkpoint |
| `WORKSPACE_BUCKET` pin for AOU-2 | AOU-2 setup | **GAP (manual)** ⚠️ | LD `.npz`/`.bm` written to the 404 placeholder if run in a fresh kernel |
| `git checkout -f` | terminal | **MANUAL** | Workbench filter re-dirties notebooks, can strip baked guards |

> **Smoke-template trap:** `AOU-1-chr22-smoke_template.ipynb` Cell 1a'' uses the UNSAFE `os.environ.setdefault(...)`. Use the **production** `AOU-1_template.ipynb` (hard assign). Never copy the bucket line from the smoke notebook.

## Cohort build (AOU-1) — specifics
- **Use the production template** (genome-wide, `interval_filter=None`). The bucket MTs after a chr22 smoke are chr22-ONLY — re-running the smoke overwrites the production paths.
- **Per-chrom fan-out** (`ab0853a`): `count_cols`/Py4J mutual-wait on the un-pruned genome-wide plan is resolved by recursing 22× (one autosome each), `union_rows`, then sample-QC ONCE over the union. Arbiter = `intermediate/…post_variant_qc_chrN` listing → 22.
- **EUR is the long pole** — watch the GC-heavy `aggregate_cols`/`collectDArray` driver gather (scales with samples × partitions; partition-capped 2048). Judge by the `entries/rows/parts/` write timestamp + assertion, not thread state.
- **Expected shapes:** AFR_pca 73,122 × 20,767,864 · EUR_pca 220,098 × 11,375,140 · AFR_pca_selfid 62,557 × 20,817,925 (strict subset; `self_report` present).

## LD compute (AOU-2) — specifics
- **Region set = `config/ld_regions.tsv`** (322 = 161 M2 regions × 2 ancestries), **NOT** `regions_curated_grch38.csv` (pre-reframe candidate set). `USE_DEV_SUBSET=True` → `config/ld_regions_dev.tsv` (10).
- **Path routing `_route_region_path` (`c6c32b3`):** any A.1/A.2 region with span > 10 Mb → A.3 `BlockMatrix.write` (driver-OOM span-veto). `region_class` labels are advisory only.
- **Export MAF 0.005** (preserves AFR rare-allele signal; overrideable to spec's 0.01). Signed Pearson **r** float32. Per-region radius = span + 500 kb, capped 50 Mb → **the 16 xlarge cells are 50-Mb-BANDED; downstream `ld_npz_to_rds.R` / SuSiE-RSS must treat them as banded.**
- **Halt-checks:** Q10 (>50% variant drop at MAF 0.005 vs 0.01 → halt); D-M3-07 (dev-10 self-ID-vs-PCA LD r < 0.995 → escalate self-ID to a full fire).
- **Egress = 44 export requests** (22 chr × 2 anc) via Files UI, each a Carter human action (~2–5 business-day SLA each), logged to `.planning/amendments/aou-egress-audit-log.md`. **Gated on GATE 0.**

## Wave 2 gate sequence
- ✅ **GATE 1.5** — genome-wide cohort rebuild (3 MTs). DONE + verified (cohort_summary 3 rows).
- 🔴 **GATE 0** — AoU egress classification ruling (written) for the variant×variant LD matrices. The HARD gate; longest external SLA; **NOT on the cohort path → file/confirm in parallel ASAP.**
- 🟠 **GATE 1** — Carter-only: CDR pin (v8, no mid-flight v8→v9), cost/credit confirmation (~1,117 cluster-h). Code work done.
- 🟡 **GATE 2** — dev-10 LD fire + AOU-4 validation memo. Needs GATE 1, **not** GATE 0. First live A.2/A.3 + first `.bm` write.
- 🟢 **GATE 3** — full 322-cell production + 44 egress. Land the durable atomic-final-write fix first.

## Catastrophe → recovery recipes
- **Empty final MT** (`_SUCCESS` over 0-byte; H1 = driver killed mid-finalize-flush, often a stray navigation): intermediates are intact → **finalize-only re-drive** from the 22 `…post_variant_qc_chrN` (minutes, not 15 h). Prove with a read-only `_scratch` dry-run, verify cols/rows/du, then `gsutil -m rsync -r -d` scratch→live and re-verify. Do NOT `force_fresh=True`. (`.planning/debug/m3-W2-afr-sens-empty-final-merge.md`)
- **Sensitivity == primary (byte-identical, silent no-op):** the self-report filter never sourced. Fix = source `self_report_table_path` + `SENS_FILTER_VERSION=2` matching `WhatRaceEthnicity_Black`; verify path-builder isolation (`_pca_selfid` token), not just the count. (`.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md`)
- **`count_cols` wedge (Py4J mutual-wait) on the first genome-wide action:** the un-pruned plan; fixed by the per-chrom fan-out (`ab0853a`). (`.planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md`)
- **Sample-axis collapse (N×0 after sample-QC):** variant_qc must run BEFORE sample_qc so `call_rate` is measured over QC-passing variants. (`resolved/m3-gatec-sample-callrate-ordering-collapse.md`)

## Known surviving risk
The final-output write (`aou_ld_panel.py:1971–1975`) validates AFTER `_SUCCESS`, and consumers (AOU-2/AOU-4) read the final with **no contents gate** — a future bad final could propagate silently. The durable atomic-final-write fix is designed (`.planning/phases/m3-aou-afr-ld-panel-build/DURABLE-FIX-DESIGN-atomic-final-write.md`) but **not yet applied**; land it via `/gsd-plan-phase --gaps` before GATE 3.
