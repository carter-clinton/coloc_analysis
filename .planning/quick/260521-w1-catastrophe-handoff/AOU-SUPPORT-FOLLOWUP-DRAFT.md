# AoU Support Follow-up Email Draft

**Purpose:** When AoU Research Support replies to the initial Zendesk ticket (filed 2026-05-22, ticket subject: "Hail mt.checkpoint() empty-MT failure on Dataproc — ~$2,140 lost, requesting credit recovery"), paste this as the reply with the full forensic evidence chain.

**Initial filing** (already sent 2026-05-22):
- Workspace: coloc_analysis
- Correspondence email: carterclinton@ncsu.edu (deliverable; use this for ALL reply traffic)
- AoU researcher account identifier: cclinton@researchallofus.org (AUTH-ONLY — not a deliverable mailbox; Workspace Admin has Gmail disabled for the researchallofus.org domain. Reference this in the ticket body for account correlation but do NOT CC it on emails or expect replies to land there.)
- Request type: Technical issue or bug
- Description: "Hail mt.checkpoint() wrote _SUCCESS markers on empty (0×0) MatrixTables across 5 Dataproc sessions (~$2,140 lost May 4-21, 2026). Requesting credit recovery; full forensic evidence available in follow-up."

---

## Reply text (paste when AoU asks for detail)

Hi [AoU Support agent name from their reply],

Thank you for getting back to me. Here's the full forensic detail on the failure.

## Summary

I was running cohort definition (`load_qc_cohort`) against the v8 `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` MatrixTable on Dataproc clusters across five sessions between 2026-05-04 and 2026-05-21. Hail's `mt.checkpoint(uri, overwrite=True)` operations completed and wrote full `_SUCCESS` marker stacks (root + cols + entries + globals + rows subtables) to my workspace bucket. A direct Hail read-probe on 2026-05-21 shows the resulting MatrixTables are **0×0 empty schema-only skeletons** — proper schema, 2,045 partitions, every `_SUCCESS` marker present, but `count_cols() = 0` and `count_rows() = 0`. No usable data was produced.

## Forensic evidence (in my workspace bucket, available for your team to verify directly)

- `gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt/` — full schema + all 5 `_SUCCESS` markers, but Hail probe returns `count_cols=0, count_rows=0`
- `gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt/` — same pattern
- `gs://${WORKSPACE_BUCKET}/ld/mt_eur_qc.mt/` — directory does not exist (Cell 5 EUR write IR submitted 2026-05-20 19:07:36 UTC, log truncated 28 seconds later mid-JIT compile, no Spark stages executed)
- `gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log` (~27 MiB) — preserved hail.log from the May 19-20 monolithic run, showing the truncation pattern
- Bucket-wide total: ~71 MiB (most of which is the forensic preserve itself — impossible to contain populated WGS MTs which would be hundreds of GB)

The 2,045 row partition files at the bucket are each ~35 bytes — consistent with Parquet column-metadata footers only, no row-group payloads.

## Root cause (my analysis, happy to be wrong)

Hail's `mt.checkpoint()` appears to write `_SUCCESS` markers based on driver-side task-completion accounting, not on validating that contents committed to GCS. Combined with the `spark.executor.cores=1 / spark.executor.memory=5g` profile required for v8 partition-explosion OOM remediation (documented in my 2026-05-04 postmortem dump), executor-side writes appear to have silently truncated after committing only the Parquet schema footers, while the driver-side finalize still wrote the full `_SUCCESS` marker stack. The failure was invisible to standard `_SUCCESS`-marker-based verification.

## What I'm asking for

A review for compute credit recovery on the ~$2,140 lost to this issue. If full refund isn't possible, even replacement compute credits to re-run the cohort definition with verification guards in place would be greatly appreciated.

I'm implementing defensive code patches on my end (`_validate_checkpoint_populated()` helper + post-write `count_rows() > 0` assertions) to prevent recurrence. I'm happy to share these with your Hail/Dataproc tooling team if that's useful for platform-side documentation.

I can also share my full forensic root-cause analysis (40 KB markdown) and the complete 2026-05-04 OOM postmortem dump (forensic JSON + hail logs, ~12 MB) if your team would like to review them.

## Cost ledger (approximate; exact figures available via AoU billing console)

| Date | Session | Approx cost |
|---|---|---|
| 2026-05-04 | OOM diagnostic fire (un-remediated cluster) | ~$10 |
| 2026-05-14 | Bucket-prefix bug surfaced + fixed; env recreate | ~$10 |
| 2026-05-17 | Cell 3 re-fire halted on cluster mis-sizing | $17 |
| 2026-05-18 to 05-20 | 67h monolithic Cell 3-7 run, produced empty MTs | ~$1,275 |
| 2026-05-21 | Diagnostic session confirming the catastrophe; cluster deleted | ~$30 |
| **Total** | | **~$1,342 to ~$2,142 depending on prior session attribution** |

Workspace: **coloc_analysis**
AoU researcher account (auth-only identifier; not a deliverable mailbox): cclinton@researchallofus.org
Correspondence email: **carterclinton@ncsu.edu** (please direct all replies here; the researchallofus.org account has Gmail disabled at the workspace level)

Thanks again for taking a look. Happy to provide any additional forensic detail your team needs, and to coordinate with the Hail/Dataproc tooling team if helpful.

Best regards,
Carter K. Clinton, PhD
Assistant Professor & Director, ASHES Laboratory
North Carolina State University
carterclinton@ncsu.edu

---

## Attachments to offer (if Zendesk thread supports them)

- `.planning/debug/m3-W1-empty-mt-catastrophe.md` (40 KB — full forensic root-cause analysis)
- `.planning/quick/260511-aou-w2-oom-fix/forensics/2026-05-04-stage8-regionpool-oom/` directory (~12 MB zipped — original OOM postmortem dump with JSON + hail logs)
- `.planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md` (next-session work plan)

## Pre-send checklist

- [ ] Replace placeholder agent name with their actual name
- [ ] Verify the cost ledger against AoU billing console (your numbers may differ slightly)
- [ ] Adjust the "happy to be wrong" framing if you want a firmer technical stance
- [ ] Attach forensic files if Zendesk supports it
- [ ] DO NOT CC `cclinton@researchallofus.org` — that account has Gmail disabled (AUTH-ONLY identifier). Reference it inline for account correlation but keep all delivery to `carterclinton@ncsu.edu`.
