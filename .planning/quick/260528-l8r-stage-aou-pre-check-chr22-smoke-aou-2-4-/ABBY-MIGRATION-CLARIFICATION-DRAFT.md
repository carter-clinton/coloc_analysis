# Zendesk reply draft — migration clarification + engineering response nudge

**Ticket:** AoU Research Support #57144
**Thread parent:** Carter's substantive forensic reply sent 2026-05-22
**Last AoU action:** Abby Doyle (triage) asked for more detail; Carter replied; AWAITING AoU engineering team response
**To address to:** Abby Doyle (same thread)
**From:** `carterclinton@ncsu.edu` (per [[feedback_aou_researcher_email_auth_only]] — researcher account is auth-only)
**Reply draft as of:** 2026-05-28

---

## Why this reply now

1. **Process check.** Carter sent a follow-up to Abby morning of 2026-05-28 (~10-11 ET); no reply yet end of day. A second polite note keeps the ticket warm without being pushy.
2. **Migration deadline discovery.** AoU Researcher Workbench 2.0 migration hard deadline is **2026-06-30** ([support article](https://support.researchallofus.org/hc/en-us/articles/48266066855188)). 33 days from today. Legacy Workbench is being sunset; if AoU engineering wants to reproduce the catastrophe against the original Legacy Dataproc/Hail/Spark image pairing, their window is bounded.
3. **Asset-preservation clarification.** Need explicit confirmation that workspace bucket contents (`gs://${WORKSPACE_BUCKET}/ld/mt_*_qc.mt/` empty MTs + `gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log`) survive the platform migration and remain accessible to the engineering team for their assessment. The substantive evidence should be platform-independent (workspace buckets are stable GCS infrastructure independent of the workbench UI), but a one-line confirmation removes the risk.
4. **Transparent timing.** Carter wants to migrate within the next 1-2 weeks to leave buffer before the 6/30 cutoff. Better to announce this and ask for advice on timing than surprise the engineering team mid-investigation.

## Draft reply

> Hi Abby,
>
> Quick clarification before I migrate my workspace to Researcher Workbench 2.0 ahead of the June 30 deadline.
>
> I want to make sure the engineering team has everything they need from my workspace to assess the credit recovery claim BEFORE I migrate. Two questions:
>
> 1. **Forensic evidence preservation.** I have the following catastrophe evidence in my workspace bucket that the engineering team may want to reference:
>
>    - The empty MatrixTables themselves: `gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt/` and `gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt/` (both with `_SUCCESS` markers + ~2,045 partitions of ~35-byte Parquet footer stubs + absent `entries/entries/parts/` subpaths; `count_cols()=0` and `count_rows()=0` on read-back)
>    - The preserved hail.log from the EUR cell's truncated write attempt: `gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log` (~27 MiB)
>    - The original Dataproc job execution context from the 2026-05-18 → 2026-05-20 monolithic run on Legacy
>
>    Will all of this remain accessible to your engineering team after I migrate to Researcher Workbench 2.0? My understanding is that workspace bucket contents persist across the platform migration since they're GCS-side infrastructure, but I'd like to confirm before acting.
>
> 2. **Timing recommendation.** Is there any reason for me to delay migrating? For example: if the engineering team would prefer to reproduce against the original Legacy Dataproc/Hail/Spark image pairing while Legacy is still live, or if any platform-side log retention is tied to the workspace's Legacy status, I'm happy to hold off until your team has finished their assessment. Otherwise I'd plan to migrate within the next 1-2 weeks to leave buffer before the June 30 cutoff.
>
> No urgency on the engineering team's diagnostic reply — I understand these things take time and I'd rather have a thorough answer than a fast one. But the migration deadline does create a small process question, so any guidance you can offer on the two items above would help me sequence things sensibly.
>
> While I wait, I've landed defensive code patches on my GitHub repo that guard against this failure mode regardless of the underlying mechanism — every `mt.checkpoint()` call now self-validates `count_rows() > 0 AND count_cols() > 0` and the auto-resume gate checks `entries/entries/parts/` size rather than just the `_SUCCESS` marker. So whatever the engineering team's diagnosis turns out to be, my next fire (whenever that happens) won't silently reproduce the catastrophe. Happy to share the commit chain if it's useful.
>
> Thanks again for your patience tracking this with the engineering team.
>
> Best,
> Carter
>
> Carter K. Clinton, PhD
> Assistant Professor & Director, ASHES Laboratory
> Department of Population Health and Pathobiology
> NC State University College of Veterinary Medicine
> Researcher Workbench account: `cclinton@researchallofus.org` (auth-only; please reply to `carterclinton@ncsu.edu`)

## Paste instructions

1. Open Zendesk ticket #57144 in browser
2. Click "Reply" in the same thread (do NOT open a new ticket)
3. Paste the draft above
4. Confirm "From" address is `carterclinton@ncsu.edu` (NOT `cclinton@researchallofus.org` per [[feedback_aou_researcher_email_auth_only]])
5. Send

## What to watch for in Abby's reply

| Abby's response | What it means | Next action |
|---|---|---|
| "Yes, all forensics persist across migration; proceed at your discretion" | Migrate this week or next | Run forensic mirror script first as insurance, then migrate |
| "Engineering would like to reproduce before you migrate" | Hold migration until they're done | Stay on Legacy; risk grows as 6/30 approaches; ask for ETA |
| "Engineering team has completed assessment; here's what they found" | Credit decision pending; act on their finding | Apply their diagnostic; re-plan re-fire strategy |
| "Workspace bucket persists; logs do not" | Mirror everything to NCSU before migrating | Run forensic mirror this week; preserve hail.log especially |
| Silence past 2026-06-08 (10 days from today) | Internal deadline trip — Abby has been informed of urgency | Mirror forensics + migrate + pivot to 1000G AFR substrate for Wave 2 |

## Internal deadline note

Set internal hard deadline of **2026-06-08** for engineering team's substantive reply. If silence past that date, presume credit recovery is unlikely and shift to 1000G AFR safety-net for Wave 2 (free; defended by Track 4 patches; documented "limited LD substrate" deviation in OSF amendment trail). Mirror forensics + migrate any time after 2026-06-08 even without a reply — Carter's audit trail will demonstrate good-faith engagement.
