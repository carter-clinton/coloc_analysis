# Post-migration validation — Legacy Workbench → RW 2.0 (Step 4)

**Migration completed:** 2026-05-29. Status flow STARTING → MIGRATION IN PROGRESS → MIGRATED, no errors. Non-destructive (legacy workspace not locked/deleted).

## New RW 2.0 workspace coordinates

| Field | Legacy (old) | RW 2.0 (new) |
|---|---|---|
| Workspace title | coloc_analysis | coloc_analysis (same) |
| Workspace ID | — | **aou-rw-476cdac2** |
| Workspace UUID | — | 38f1e4ec-399e-4715-9d00-c04e71cae0bc |
| Google project | terra-vpc-sc-fe7a5641 | **wb-perky-corn-6639** |
| Billing pod | — | user-pod-cclinton-2d12 |
| Region | — | us-central1 |
| `WORKSPACE_BUCKET` | gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a | **gs://rw-migration-aou-rw-476cdac2** |
| CDR | cdrv8 R8 | **C2024Q3R9 (cdrv8 – R9)** |
| CLI set-workspace | — | `wb workspace set --id=aou-rw-476cdac2` |

**Bucket structure note:** migrated content sits at the **root** of the new bucket (`gs://rw-migration-aou-rw-476cdac2/<dir>/...`), NOT nested under a `workspace/rw-migration-aou-rw-XXXX/` folder as the generic doc implies.

## Validation results

| Check | Status |
|---|---|
| 5 top-level dirs (forensics, ld, m3-W1-forensics, m3-W2-forensics, notebooks) | ✅ 5/5 present (UI browser) |
| Total bucket size ~74.73 MiB | ⏳ PENDING — UI shows "--" for folder sizes; needs `gsutil du -sh` from a terminal in the new env (allow ~30 min for full GCS population; VPC-SC perimeter caveat) |
| Catastrophe evidence (`ld/mt_*_qc.mt/_SUCCESS`, forensics/) | ⏳ confirm via terminal (dirs present; per-object check pending) |
| Git clone | n/a yet (env not recreated in RW 2.0) |
| Hail/Dataproc image version on RW 2.0 vs Legacy | ⏳ PENDING — capture from first notebook (matters for chr22-smoke planning) |

**Pending size/contents confirmation block** (run in a terminal in the RW 2.0 env, after ~30 min population wait):
```bash
export WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2
gsutil ls "$WORKSPACE_BUCKET/"                 # expect 5 dirs
gsutil du -sh "$WORKSPACE_BUCKET"              # expect ~74.73 MiB
gsutil du -sh "$WORKSPACE_BUCKET"/*            # per-dir breakdown
gsutil ls "$WORKSPACE_BUCKET/ld/mt_afr_qc.mt/_SUCCESS"
gsutil ls "$WORKSPACE_BUCKET/ld/mt_afr_pca_selfid_qc.mt/_SUCCESS"
```

## Code-impact audit (run on NCSU 2026-05-29)

- **`WORKSPACE_BUCKET` change → NO code changes needed.** Code reads it dynamically (`os.environ['WORKSPACE_BUCKET']` / `_require_env`); only `fc-secure` strings in the repo are docstring examples/comments. Notebooks all use `os.environ[...]`. Auto-adapts to the new bucket.
- **CDR R8→R9 → reduced to ONE env-side check (NCSU audit 2026-05-29):**
  - ✅ **CHECK A RESOLVED — no BigQuery/SQL CDR refs.** AOU-1 cohort notebook is pure-Hail (filter_cols ancestry → anti-join relateds → filter_rows flags); `aou_ld_panel.py` has no SQL. So no R9-dataset/new-project SQL updates needed.
  - ✅ `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` (MT input) is AoU-set → auto-adapts. 
  - ⏳ **CHECK B OUTSTANDING (env-side) — `AUX_BASE` is on the cohort's critical path.** `aou_ld_panel.py:85` `AUX_BASE = gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux` feeds `ANCESTRY_PREDS_PATH` (ancestry filter) + `RELATED_SAMPLES_PATH` (relateds anti-join). Path was verified 2026-05-01 on **Legacy/R8**. On RW 2.0 confirm: (1) the path resolves from project `wb-perky-corn-6639`; (2) content is R9-consistent (if R9 uses a different AUX path, update `AUX_BASE`).
  - AOU-0 precheck Cell 2 infers CDR via `/v8/` vs `/v9/` — still reports "v8" (correct) but doesn't distinguish R8/R9; optional enhancement, non-blocking.

## Consolidated env-side block (run once, in RW 2.0 terminal, after ~30 min population)

```bash
export WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2

echo "=== A. workspace bucket: 5 dirs + size (expect ~74.73 MiB) ==="
gsutil ls "$WORKSPACE_BUCKET/"
gsutil du -sh "$WORKSPACE_BUCKET"
gsutil du -sh "$WORKSPACE_BUCKET"/*

echo "=== B. catastrophe evidence intact ==="
gsutil ls "$WORKSPACE_BUCKET/ld/mt_afr_qc.mt/_SUCCESS"
gsutil ls "$WORKSPACE_BUCKET/ld/mt_afr_pca_selfid_qc.mt/_SUCCESS"

echo "=== C. CDR / AUX path check (the one outstanding CDR item) ==="
echo "WGS_ACAF path AoU binds:"; echo "  $WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"
gsutil ls "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv"
gsutil ls "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv"
# If either 404s -> AUX_BASE needs updating for R9 (note the path AoU actually uses).

echo "=== D. Hail version on RW 2.0 (matters for chr22-smoke planning) ==="
python3 -c "import hail as hl; print('Hail', hl.__version__)" 2>/dev/null || echo "(capture from a notebook instead)"
```

## Next steps (post-migration)

1. Recreate env in RW 2.0 (wait ~30 min post-migration); run the pending size/contents block above → confirm 74.73 MiB + `_SUCCESS` markers.
2. Capture Hail version on RW 2.0.
3. CDR-reference verification quick task (AUX_BASE resolves? any SQL CDR refs?).
4. AOU-0 precheck → routing decision.
5. chr22 smoke (256-vCPU Dataproc) → Wave 2 or 1000G safety net.
