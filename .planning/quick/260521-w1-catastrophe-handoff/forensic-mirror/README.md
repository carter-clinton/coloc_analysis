# m3-W1 Catastrophe Forensic Mirror

> NCSU-side immutable copy of the AoU workspace-bucket forensic evidence from the 2026-05-18 → 2026-05-20 m3-W1 catastrophe ($2,140 lost; 3 cohort MTs returned empty with `_SUCCESS` markers).
>
> Insurance against any AoU platform-side change (Researcher Workbench 2.0 migration deadline 2026-06-30; possible bucket-data lifecycle / retention changes; possible loss of access to engineering-team-side reproduction context).

## Status

**EMPTY at task creation 2026-05-28.** Populated when Carter runs `run_forensic_mirror.sh` from inside the AoU env (paused-cluster compatible; gsutil + bash only) and commits the resulting bundle to this directory.

## Why this directory exists

1. **Track 1 (AoU credit recovery) evidence preservation.** The empty `mt_*_qc.mt/` directories in `gs://${WORKSPACE_BUCKET}/ld/` are the substantive evidence for the ~$2,100 credit claim filed with AoU Research Support (Zendesk ticket #57144). Workspace buckets are stable GCS infrastructure and almost certainly survive the Researcher Workbench 2.0 platform migration unchanged — but an NCSU-side mirror removes the residual risk and gives Carter independent forensic standing.

2. **[[feedback_w1_catastrophe_hypothesis_distinguisher]] resolution.** The `_SUCCESS` file mtimes captured by the mirror script (Section 1 of MANIFEST) resolve Carter's "kill is the culprit" hypothesis vs the debug doc's "Hail finalize fires on empty contents" hypothesis. Specifically:
   - If `mt_afr_qc.mt/_SUCCESS` mtime is on **2026-05-19 14:30 ± a few hours UTC** → matches Stage 36's expected completion → debug-doc Hail-finalize hypothesis HOLDS for MT #1.
   - If mtime is **at or after 2026-05-20 22:30 UTC** (workbench Pause kill time) → Carter's kill-as-culprit hypothesis HOLDS.
   - Same logic for `mt_afr_pca_selfid_qc.mt/_SUCCESS` against Stage 45's expected window.
   - `mt_eur_qc.mt/_SUCCESS` is expected to be absent (Cell 5 EUR write IR submitted 19:07:36 then truncated 19:08:04; kill at 22:30 sealed it).

3. **Independent of AoU engineering reply.** Even if Abby's team's diagnostic reply takes weeks (or never arrives), this mirror gives Carter a complete, immutable, repo-versioned record of the bucket state that no future AoU action can invalidate.

## Layout (expected after population)

```
forensic-mirror/
├── README.md                                                    (this file; committed at task creation)
├── MANIFEST-YYYYMMDDTHHMMSSZ.txt                                (timestamped manifest from run_forensic_mirror.sh)
├── hail.log.pre_pd_migration.20260521T201919Z.log               (27 MiB copy of the bucket-side preserve)
└── forensic_mirror_YYYYMMDDTHHMMSSZ.tar.gz                      (gz-bundled MANIFEST + hail.log; the upload-ready artifact)
```

## How to populate (Carter user-action)

The script that produces this mirror lives at:

  `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh`

End-to-end procedure (~5 min if env already running; ~15 min including env recreate-and-pause):

1. **Recreate AoU env** (Researcher Workbench → coloc_analysis workspace → Cloud analysis environment → Create with preset matching prior config — Dataproc, 16 workers, persistent disk Reattachable per `[[feedback_aou_use_persistent_disk]]`; leave cluster paused at $0.14/hr after creation).
2. **`git pull`** in the AoU clone to pick up the latest scripts:
   ```bash
   cd /home/jupyter/coloc_analysis
   git pull origin m3-W2-aou-deltas
   ```
3. **Make script executable + fire it:**
   ```bash
   chmod +x .planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh
   .planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh
   ```
4. **Read the hypothesis-distinguisher output** at the bottom of the script's stdout. This is the moment you learn whether your kill-as-culprit hypothesis is correct or the debug doc's Hail-finalize hypothesis is correct.
5. **Mirror to NCSU** using either path:
   - **Path A — through workspace bucket:**
     ```bash
     gsutil cp /tmp/forensic_mirror/forensic_mirror_*.tar.gz gs://${WORKSPACE_BUCKET}/forensics/
     ```
     Then from any NCSU terminal with AoU bucket access (or via the Workbench Files UI download):
     ```bash
     # Inside the AoU env Files UI: download forensic_mirror_*.tar.gz to your laptop
     # Then scp from laptop:
     scp forensic_mirror_*.tar.gz ckclinto@your-ncsu-host:/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
     ```
   - **Path B — direct download via Workbench Files UI:**
     Open `/tmp/forensic_mirror/` in the Workbench Files panel; download the tarball + manifest + hail.log to your laptop; scp to NCSU GPFS into this directory.
6. **Untar + commit + push from NCSU:**
   ```bash
   cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
   tar xzf forensic_mirror_*.tar.gz
   cd ../../../..
   git add .planning/quick/260521-w1-catastrophe-handoff/forensic-mirror/
   git commit -m "docs(m3-W1): mirror catastrophe forensic evidence to NCSU (pre-RW2.0-migration insurance)"
   git push origin m3-W2-aou-deltas
   ```
7. **Reply in Zendesk #57144** noting that you've preserved an independent copy of the workspace-bucket evidence (this strengthens any future audit trail of the claim).
8. **Pause AoU env** (Workbench → Cloud analysis environment → Pause Environment). Now you can migrate to RW 2.0 at your convenience without losing the forensic context.

## Cost expectation

- AoU env recreation paused: ~$0.14/hr × however long it takes to recreate + run script + Pause = ~$1
- `gsutil cp` of 27 MiB hail.log into bucket: ~$0 (intra-cluster GCS)
- `gsutil cp` of 27 MiB hail.log from bucket to NCSU (if using Path A): ~$0.01-0.05 GCS egress; AoU's standard egress policy applies (hail.log is debug output, not controlled data; should be cleanly egressable)
- Workbench Files UI download via Path B: free (count against AoU's standard user-egress allowance)
- Total: **< $2**.

## What to do if the script fails

Likely failure modes and remediation:

| Failure mode | Remediation |
|---|---|
| `gsutil ls` returns no objects (bucket purged before mirror) | Track 1 evidence already lost on the AoU side. Mirror the local NCSU-side hail.log preserve at `.planning/quick/260511-aou-w2-oom-fix/forensics/` (from earlier Stage 8 OOM postmortem) which still contains pre-catastrophe-execution context. Update Zendesk #57144 noting the bucket has been purged + ask Abby's team for any AoU-internal log copies they retain. |
| `gsutil` errors with auth failure | Re-init gcloud auth via `gcloud auth login` in the AoU env terminal. Workspace bucket auth is in-env only. |
| Script runs but bundle is empty (0 bytes in entries dirs, 0 byte hail.log) | Confirm the bucket actually contains the catastrophe artifacts (some other process may have purged them between 2026-05-21 inspection and today's mirror). Compare bundle MANIFEST against bucket state in debug doc §Bucket forensics. |
| Workbench Files UI doesn't see `/tmp/forensic_mirror/` | The env's `/tmp` is sometimes hidden from the Files panel. Move the bundle to `/home/jupyter/forensic_mirror/` first (`mv /tmp/forensic_mirror /home/jupyter/`) which is always visible. |

## Cross-references

- `.planning/debug/m3-W1-empty-mt-catastrophe.md` — root cause analysis (40 KB)
- `.planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md` — 4-track plan
- `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/run_forensic_mirror.sh` — the script that populates this dir
- `.planning/quick/260528-l8r-stage-aou-pre-check-chr22-smoke-aou-2-4-/MIGRATION-PLAYBOOK.md` — the full RW 2.0 migration sequence (this mirror is Step 0 of that playbook)
- `[[feedback_w1_catastrophe_hypothesis_distinguisher]]` — the mtime test rule
- AoU Researcher Workbench 2.0 migration article: https://support.researchallofus.org/hc/en-us/articles/48266066855188
