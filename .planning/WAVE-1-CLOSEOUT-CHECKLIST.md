# Wave 1 Closeout Checklist

> Tactical action sequence for the moment Cell 7 finishes and Cell 3-7 returns control.
>
> Trigger: workbench YARN page shows `Apps Running: 1 → 0` OR `FinalStatus: SUCCEEDED` OR `FinishTime` populated.
>
> Time-pressure level: HIGH for steps 1-4 (env is burning $19.03/hr until paused, and the cohort_summary_m3.tsv on env local disk needs to survive any future env Delete). LOW for steps 5+ (HPC-side, no env dependency).
>
> Written: 2026-05-20 during Stage 71 monitoring.

---

## Pre-trigger watch (right now → Cell 7 finishes)

- Keep workbench YARN page open and refresh every ~10 min
- Watch for one of these definitive signals:
  - `Apps Running` counter: 1 → 0
  - `FinalStatus`: UNDEFINED → SUCCEEDED (or FAILED — if FAILED, switch to incident response path at bottom)
  - `FinishTime`: N/A → a timestamp
  - `Running Containers`: 256 → 0

When you see ANY of these, start the action sequence below.

---

## STEP 1 (T+0 to T+5sec) — Fetch cohort_summary_m3.tsv FIRST

**Why first**: this file is on the AoU env's **local persistent disk**, NOT in the bucket. Cell 7's `cohort_summary.to_csv("cohort_summary_m3.tsv", ...)` writes to the env filesystem. Persistent disk survives Pause/Resume, but **does NOT survive env Delete**. We want this file in a safe location before any destructive operation could happen.

**Three fetch paths in order of preference:**

### Path 1A — Run a one-line cell in the notebook (kernel is idle, iframe MAY work post-Cell-7)

Add a new cell at the end of the notebook (Cell 8) with:

```python
import subprocess, os
ts = subprocess.check_output(['date', '-u', '+%Y%m%dT%H%M%S']).decode().strip()
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True)
r1 = sh(f'gsutil cp cohort_summary_m3.tsv "$WORKSPACE_BUCKET/exports/cohort_summary_m3.tsv"')
r2 = sh(f'gsutil cp /tmp/hail.log "$WORKSPACE_BUCKET/forensics/hail.log.wave1-complete.{ts}.txt"')
print("TSV upload:", r1.returncode, r1.stderr or "OK")
print("hail.log upload:", r2.returncode, r2.stderr or "OK")
```

After the kernel finished Cell 7, iframe interaction may have recovered (kernel-busy state may have been the friction source). Try this path first.

### Path 1B — Open a fresh terminal via env sidebar

If iframe still works for terminal spawning post-Cell-7-completion:

```bash
gsutil cp cohort_summary_m3.tsv "$WORKSPACE_BUCKET/exports/cohort_summary_m3.tsv"
gsutil cp /tmp/hail.log "$WORKSPACE_BUCKET/forensics/hail.log.wave1-complete.$(date -u +%Y%m%dT%H%M%S).txt"
```

### Path 1C — Accept deferred fetch via post-resume

If Path 1A and 1B both fail (iframe still broken):

- Skip directly to Step 2 (pause env)
- Resume env later for Wave 2 (cluster cold-start ~5-10 min)
- Fetch the file then via working terminal
- Persistent disk survives Pause/Resume — file will still be there

**Risk of Path 1C:** if you ever Delete the env (vs just Pause), persistent disk goes with it, file is lost. So don't Delete env until cohort_summary_m3.tsv has been mirrored to bucket OR HPC.

---

## STEP 2 (T+0 to T+30sec after Step 1) — Pause Environment

**Why immediate**: skipping the 30-min auto-pause window saves ~$10. More importantly, it stops the $19.03/hr billing the moment Cell 7's work product is secured.

**Action:**
- Workbench dashboard → Cloud analysis environment panel → **Pause Environment** button (not Delete)
- Confirm any dialog
- Verify status changes from RUNNING to STOPPED/PAUSED within ~5 min

**Verification:**
- Cost meter on dashboard should drop from $19.03/hr to ~$0.14/hr (~99% reduction)
- YARN page becomes inaccessible (cluster is down)
- Bucket data unaffected — all 3 MTs immutable in GCS

**If Pause fails / hangs:**
- Try again
- If still failing: workbench Support → describe the situation
- DO NOT click Delete Environment unless explicitly intending to lose persistent disk

---

## STEP 3 (T+5-10min after pause completes) — Verify bucket assets

These can run from any machine with `gsutil` + workspace bucket access (HPC if you have AoU bucket access there, or AoU env post-resume):

> **CRITICAL — m3-W1 catastrophe lesson (2026-05-21):** `_SUCCESS` marker existence is **NOT sufficient** evidence of populated data. Hail's `mt.checkpoint()` writes `_SUCCESS` based on driver-side tasks-reported-complete accounting WITHOUT validating output contents. Under `spark.executor.cores=1/mem=5g`, executor tasks can silently truncate after writing 35-byte Parquet column-metadata footer stubs — producing an MT directory with `_SUCCESS` + rows-stubs + ABSENT `entries/entries/parts/`. The 2026-05-21 bucket inspection found this exact pattern on `mt_afr_qc.mt` and `mt_afr_pca_selfid_qc.mt` after ~$2,100 of compute had appeared to succeed.
>
> STEP 3 MUST therefore verify `entries/entries/parts/` size, not just `_SUCCESS`. See `.planning/debug/m3-W1-empty-mt-catastrophe.md` + memories `[[feedback_aou_success_marker_not_evidence_of_data]]` + `[[feedback_hail_checkpoint_contract_violation]]`.

```bash
# Verify all 3 MTs have _SUCCESS + parseable metadata + POPULATED entries
BUCKET="gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a"
MIN_ENTRIES_BYTES=$((1024 * 1024 * 1024))  # 1 GB floor for production fires
for mt in mt_afr_qc.mt mt_afr_pca_selfid_qc.mt mt_eur_qc.mt; do
  echo "=== $mt ==="
  # _SUCCESS marker (necessary but NOT sufficient — see W1 catastrophe)
  gsutil ls "${BUCKET}/ld/$mt/_SUCCESS" && echo "  _SUCCESS: OK"
  # metadata.json.gz parseable
  gsutil ls "${BUCKET}/ld/$mt/metadata.json.gz" && echo "  metadata: OK"
  gsutil cat "${BUCKET}/ld/$mt/metadata.json.gz" \
    | gunzip \
    | python3 -c "import json,sys; m=json.load(sys.stdin); print(f'  keys: {list(m.keys())}')"
  # entries/entries/parts/ MUST exist and have GB-scale payload — this is
  # the discriminator that would have caught the W1 catastrophe 36h earlier.
  ENTRIES_SIZE=$(gsutil du -s "${BUCKET}/ld/$mt/entries/entries/parts/" 2>/dev/null | awk '{print $1}')
  if [[ -z "$ENTRIES_SIZE" ]]; then
    echo "  entries/entries/parts/: ABSENT — m3-W1 catastrophe pattern. STOP."
    echo "  (MT directory exists with _SUCCESS but no entries payload.)"
    continue
  fi
  if (( ENTRIES_SIZE > MIN_ENTRIES_BYTES )); then
    printf "  entries/: OK (%.2f GB)\n" "$(echo "scale=2; $ENTRIES_SIZE / 10^9" | bc)"
  else
    printf "  entries/: TOO SMALL (%d bytes < %d GB floor) — m3-W1 catastrophe pattern. STOP.\n" \
      "$ENTRIES_SIZE" "$((MIN_ENTRIES_BYTES / 10**9))"
  fi
done

# Verify cohort_summary_m3.tsv made it to bucket (if Path 1A or 1B ran)
gsutil ls "${BUCKET}/exports/cohort_summary_m3.tsv"
gsutil cat "${BUCKET}/exports/cohort_summary_m3.tsv"
```

**Pass criteria (ALL must pass per MT):**
- `_SUCCESS: OK`
- `metadata: OK` + canonical Hail keys printed
- `entries/: OK (X.YZ GB)` with X.YZ > 1.0 GB
- cohort_summary_m3.tsv listing returns the path + contents look like a 3-row TSV with cohort names

**If anything fails (per-MT):**
- `_SUCCESS` missing → MT didn't fully commit. Resume env, re-fire that specific cell on refactored code with `force_fresh=True`.
- `metadata.json.gz` parse fails → MT corrupted. Same recovery (re-fire on refactored code).
- `entries/entries/parts/` ABSENT or below the 1 GB floor → **m3-W1 empty-MT catastrophe pattern.** Do NOT mark Wave 1 complete; do NOT resume from this checkpoint; treat this as a HONEST_FINDING disposition per `[[feedback_failed_to_honest_finding]]`. Investigation entry point: `.planning/debug/m3-W1-empty-mt-catastrophe.md`. Recovery requires the Track 4 defensive-code patches landed AND a fresh fire on refactored code (the catastrophe-pattern resume-gate guard will auto-force-fresh on this stub MT; do not paper over it).
- TSV not in bucket → Cell 7 may have hit Path 1C (deferred fetch). Plan to fetch on Wave 2 resume.

**Belt-and-suspenders cross-check** — also run a Hail-side read-probe from a fresh Python subprocess (NOT the same kernel that did the write):

```python
import hail as hl
hl.init(default_reference="GRCh38", log="/tmp/hail.log", quiet=True)
for mt_uri in [
    "gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt",
    "gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt",
    "gs://${WORKSPACE_BUCKET}/ld/mt_eur_qc.mt",
]:
    mt = hl.read_matrix_table(mt_uri)
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    assert n_cols > 0 and n_rows > 0, (
        f"empty MT at {mt_uri}: {n_cols} cols x {n_rows} rows — "
        f"m3-W1 catastrophe pattern; see "
        f".planning/debug/m3-W1-empty-mt-catastrophe.md"
    )
    print(f"OK: {mt_uri} = {n_cols} samples x {n_rows} variants")
```

The fresh-subprocess constraint matters: the original Cell 7 read could be satisfied from JVM-side cached IR without re-reading the bucket, which masked the catastrophe. Spawning a clean Python process forces a true bucket read.

---

## STEP 4 (T+10-15min) — Mirror cohort_summary_m3.tsv to HPC

Once it's in the bucket, mirror to HPC GPFS for permanent record:

```bash
gsutil cp "gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/exports/cohort_summary_m3.tsv" \
  /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv
```

(Adjust HPC path if the m3 phase directory doesn't exist yet — `mkdir -p` it first.)

Commit it (explicit paths per [[feedback_multi_terminal_staging]]):

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
mkdir -p .planning/phases/m3-aou-afr-ld-panel-build
git add .planning/phases/m3-aou-afr-ld-panel-build/cohort_summary_m3.tsv
git commit -m "feat(m3-W1): cohort_summary_m3.tsv from AoU Cell 7 -- audit-driven re-analysis"
```

---

## STEP 5 — STATE.md Wave-1-complete update (HPC side, no env)

Open `.planning/STATE.md` and update:

### Frontmatter changes

- Change status from `m3-W1-IN-PROGRESS` (or whatever current value) to `m3-W1-COMPLETE`
- Update `last_session` timestamp
- Update `current_phase` to reference Wave 2 prep

### Quick Tasks Completed table

Add row: `260518-qcr | refactor not used; monolithic Cell 3-7 ran cleanly | $1,200-1,280 sunk | COMPLETE`

### Session Continuity entry — append new dated section

Outline:

```markdown
## Session Continuity 2026-05-20

**State:** m3-W1 Wave 1 COMPLETE. All 3 cohort MTs in bucket.

### Final asset inventory

| MT | Bucket path | N samples | N variants |
|---|---|---|---|
| MT #1 (AFR primary) | mt_afr_qc.mt/ | [from cohort_summary_m3.tsv] | [from cohort_summary_m3.tsv] |
| MT #2 (AFR sensitivity) | mt_afr_pca_selfid_qc.mt/ | [from cohort_summary_m3.tsv] | [from cohort_summary_m3.tsv] |
| MT #3 (EUR replication) | mt_eur_qc.mt/ | [from cohort_summary_m3.tsv] | [from cohort_summary_m3.tsv] |

### Final cost ledger

- App start: 2026-05-18 03:14 UTC
- App finish: 2026-05-20 [exact UTC from FinishTime]
- Total elapsed: ~65-66h
- Total compute cost: ~$1,235-1,280 (Cell 3-7 monolithic)
- Cumulative m3-W1 (including prior session attempts): ~$830 + $1,250 = ~$2,080

### Path decision retrospective

- Path B1 (let monolithic Cell 3-7 complete) selected over B2 (kill + refactored re-fire) at MT #2/#3 inflection on 2026-05-19 ~14:30 UTC
- Reason: iframe-broken + cost-neutral analysis + healthy run track record
- Refactored code (committed 50f071c) deferred to future Wave 2+ work or any re-derivation trigger

### Wave 2 entry conditions

- All 3 MTs ready in bucket for LD-matrix computation
- 7 design questions per POST-WAVE-1-ROADMAP.md §4 awaiting `/gsd-quick --discuss` resolution
- HPC R coloc stack verification status: [PENDING / PASS / FAIL]
- Wave 2 Hail script status: [NOT STARTED / DRAFTED / READY-TO-FIRE]
```

Commit:

```bash
git add .planning/STATE.md
git commit -m "docs(state): m3-W1 Wave 1 COMPLETE -- all 3 MTs in bucket -- audit-driven re-analysis"
```

---

## STEP 6 (Optional, can defer to next session) — Update memory

Worth a fresh memory bake for future-Carter:

- `project_state.md` update reflecting m3-W1 COMPLETE + Wave 2 entry conditions
- Possibly a new `feedback_aou_*` memory if anything novel surfaced during this session worth preserving

---

## Incident response — if YARN shows `FinalStatus: FAILED`

(Low probability given clean run track record, but worth having the recovery path.)

1. **Do NOT pause env immediately.** Need the env alive to debug.
2. **Read the FinishTime + look at Spark UI for the failed stage** — which stage failed, what was the error?
3. **Check `/tmp/hail.log`** via terminal or notebook subprocess for the actual Python/Hail exception
4. **Determine which MT(s) actually committed** via bucket gsutil — partial success is possible
5. **Forensic preserve hail.log immediately** before any restart action
6. **Then decide**: pause + come back later, vs restart kernel and re-fire failed cells

---

## Time estimate per step

| Step | Duration | Cost burn during step |
|---|---|---|
| 1 (fetch TSV) | 1-3 min if Path 1A/1B works, otherwise deferred | ~$1 |
| 2 (pause env) | 30 sec click + ~5 min for pause to finalize | ~$1.50 |
| 3 (gsutil verify) | 2-3 min | $0 (env paused) |
| 4 (mirror to HPC) | 1 min | $0 |
| 5 (STATE.md update) | 10-15 min | $0 |
| 6 (memory update) | 10 min (or defer) | $0 |
| **Total focused work** | **15-30 min** | **~$3-5** |

---

## TL;DR

```
[ ] Watch YARN for Apps Running: 1→0 OR FinalStatus: SUCCEEDED
[ ] Fetch cohort_summary_m3.tsv to bucket (Path 1A → 1B → 1C)
[ ] Click Pause Environment on workbench dashboard
[ ] gsutil-verify all 3 MTs (_SUCCESS + metadata.json.gz)
[ ] Mirror cohort_summary_m3.tsv to HPC + git commit
[ ] STATE.md Wave-1-complete update + git commit
[ ] (Optional) memory update
```

All steps after step 2 are HPC-side, no time pressure, no env burn. Total focused time: 15-30 min for the full sequence.
