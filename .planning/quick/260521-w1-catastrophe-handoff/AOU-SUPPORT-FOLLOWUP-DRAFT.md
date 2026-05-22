# AoU Support Ticket — Exchange Log + Drafts

**Ticket ID:** request 57144 (Zendesk)
**Filed:** 2026-05-22 morning (workspace: coloc_analysis)
**Channel:** AoU Research Support Bot → "Email support team" intake
**Status (end of Session 2, 2026-05-22):** Awaiting AoU engineering response after Carter's substantive forensic reply

---

## Email constraint (per [[feedback_aou_researcher_email_auth_only]])

- **Correspondence email:** `carterclinton@ncsu.edu` — deliverable, use for ALL reply traffic
- **AoU researcher account identifier:** `cclinton@researchallofus.org` — AUTH-ONLY (Gmail disabled at researchallofus.org org admin level). NEVER CC or set as reply-to. Reference inline in ticket body for account correlation only.

---

## Exchange chain

### 1. Initial filing (2026-05-22, sent by Carter via Zendesk intake)

- Name: Carter Clinton
- Email: carterclinton@ncsu.edu
- Workspace URL: https://workbench.researchallofus.org/...
- Request type: Technical issue or bug
- Description: "Hail mt.checkpoint() wrote _SUCCESS markers on empty (0×0) MatrixTables across 5 Dataproc sessions (~$2,140 lost May 4-21, 2026). Requesting credit recovery; full forensic evidence available in follow-up."

### 2. Tier-1 reply (2026-05-22 ~14:52 CDT) — MISROUTE

AoU support bot replied with canned "$300 initial credits + GCP billing" boilerplate that didn't engage with the technical issue. Treated the ticket as a "ran out of credits" request rather than a platform bug report. We did NOT receive this — Carter pivoted directly to the Abby reply pathway below.

### 3. Abby Doyle's reply (2026-05-22 16:05 CDT) — proper triage

```
Hi Carter,

Thank you for reaching out to Researcher Support. We're sorry you
experience this issue with Dataproc. To help us better understand, could
you please share a bit more detail? We'd be happy to take a closer look
and follow up.

Kind regards,
Abby

All of Us Researcher Workbench Support Team
```

Notice from Zendesk: "Please do not upload or transmit any documents containing participant-level data. All shared materials in your support ticket must comply with the Data User Code of Conduct."

### 4. Carter's substantive reply (sent 2026-05-22 ~17:30 CDT) — what's now in front of AoU engineering

Full text of what Carter actually sent (preserved for reference when Abby's team responds):

---

Hi Abby,

Thanks for the quick reply. For the record this is strictly aggregate and orchestration data only.

The short version: across multiple sessions between May 17 and May 21, 2026, I ran cohort-definition operations against the v8 controlled-tier WGS MatrixTable using Hail's load_qc_cohort → hl.MatrixTable.checkpoint. Each session appeared to complete successfully from the outside (the workspace bucket contained the expected MT directory structures with _SUCCESS markers on all five subtable paths). But when I returned on May 21 to use those MTs in downstream analysis, a direct Hail read-probe showed they are all 0×0 schema-only skeletons. mt.count_cols() returns 0, mt.count_rows() returns 0, despite the full _SUCCESS marker stack on each. Both AFR MTs (mt_afr_qc.mt and mt_afr_pca_selfid_qc.mt) show this pattern. The EUR cohort directory (mt_eur_qc.mt) doesn't exist at all — Cell 5's write IR was submitted at 2026-05-20 19:07:36 UTC and the hail.log truncated mid-JIT 28 seconds later with no Spark stages logged, so the EUR write never reached executor task dispatch.

If it would help your team's triage, the bucket paths in workspace coloc_analysis are all available for direct inspection. The two AFR MT directories at gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt/ and gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt/ each have full schema, _SUCCESS markers, and 2,045 partition entries, but gsutil du -s entries/entries/parts/ returns only ~72 KB (each of the 2,045 part files is about 35 bytes, consistent with Parquet schema footers only and no row-group payloads). The bucket-wide total is ~71 MiB, which obviously can't contain populated WGS cohort MatrixTables that would be hundreds of GB. The preserved hail.log from the final session is at gs://${WORKSPACE_BUCKET}/forensics/hail.log.pre_pd_migration.20260521T201919Z.log — none of these artifacts contain participant-level data, they're orchestration state only.

For cluster context, I ran a 16× n1-highmem-16 worker + 1× n1-highmem-8 master Dataproc cluster (~256 vCPU, ~1.7 TB RAM total). Hail version 0.2.134-952ae203dbbe; Spark version 3.5.3 from the Dataproc image. Worth flagging that Hail itself prints an explicit warning at init: "This Hail JAR was compiled for Spark 3.5.0, running with Spark 3.5.3. Compatibility is not guaranteed." The memory profile was spark.executor.cores=1 / spark.executor.memory=5g, which I'd added as remediation for a Stage 8 RegionPool OOM we hit on v8's 290,384-partition source MT ( documented in my 2026-05-04 internal postmortem if useful).

I have two competing hypotheses about the failure mode, and I'd value your perspective on which is more likely, as to optimize in the future.
1. silent executor-side write truncation: Hail's mt.checkpoint() appears to finalize _SUCCESS markers based on driver-side accounting that tasks reported complete, but under the aggressive cores=1/mem=5g profile, executor JVMs may be hitting memory limits during Parquet row-group encoding, silently truncating their writes to just the column metadata footer (~35 bytes), then reporting "task complete" to the driver without actually committing row data. The driver finalizes _SUCCESS based on the task-completion signal, producing the observed pattern. The 35-byte per-partition payload is suspiciously close to a typical Parquet footer-only size, which would corroborate this.

2.  Hail IR-lowering issue on v8 data. My 2026-05-04 forensic log captured a separate failure mode where after 13h17m of v8 compute ([collectDArray|table_aggregate]: executed 290384 tasks), Hail logged "error while applying lowering 'LowerOrInterpretNonCompilable'" followed by "error while applying lowering 'EvalRelationalLets'". If something similar happens during the checkpoint writes, without producing visible errors in the preserved logs, the bytecode emitted might process zero rows through some IR-internal path while still completing the Spark tasks. Both hypotheses produce identical signatures from outside the cluster. Unfortunately the full hail.log from the 67-hour May 19-20 fire (which would likely have distinguished them) was lost when the env was paused and resumed; only the truncated EUR-attempt tail survived to the bucket preserve.

A few specific things would help me a lot if your Hail/Dataproc tooling team can look at this. First, is it expected behavior for mt.checkpoint() to finalize _SUCCESS without contents validation under any executor profile, or is this an anomaly tied to specific Spark/Hail version pairings? Second, is there a known-safe memory profile for v8-scale Hail MatrixTable writes? The cores=1/mem=5g profile resolved the original RegionPool OOM but may itself be the cause of write truncation, which puts me in a tough spot if both extremes fail. Third, is there a newer Hail version available for AoU researchers that resolves the "compiled for Spark 3.5.0, running 3.5.3" warning (the 2026-05-04 IR-lowering errors might be linked to this version mismatch). And fourth, I'm implementing a _validate_checkpoint_populated() helper on my end that verifies entries/entries/parts/ size after every mt.checkpoint() call as a defensive guard; happy to share the implementation if it would be useful as a recommended pattern for other AoU researchers using Hail.

For documentation, I have a 40 KB markdown root-cause analysis I authored after discovering the catastrophe yesterday, plus the original 2026-05-04 postmortem dump (~12 MB of Spark UI JSONs + YARN REST + Hail driver logs + git state + process snapshots). Neither contains participant-level data — they're orchestration and state forensics only. Happy to attach to this ticket or share via whatever channel you prefer.

One secondary topic, deferred until the technical investigation has clarity: once we understand the failure mode, I'd like to revisit the compute credit question for the ~$2,140 billed to my linked GCP account on these failed runs. That's downstream of the technical resolution though. What matters most right now is understanding whether this is reproducible.

Workspace is coloc_analysis. My AoU researcher account is cclinton@researchallofus.org. GCP billing was linked around 2026-04-28.

Sorry for the long message but I wanted to be as comprehensive as possible. Thank you in advance for your help and I look forward to the resolution!

Best,

---

### 5. AWAITING AoU engineering response

- ETA: 3-7 business days after 2026-05-22 (holiday weekend started 2026-05-22 evening)
- Realistic window: 2026-05-26 through 2026-05-29 (or later if escalation queue is deep)
- **Next-session action when reply arrives:** read the response, paste into Claude conversation along with this HANDOFF.md reference, and recommend the next move based on what engineering said. Decision tree is documented in [`HANDOFF.md`](HANDOFF.md) "LD panel decision" section.

---

## Voice notes for any future drafts I generate as Carter

Based on Carter's substantive reply (the one sent above), his preferred email register:

- Tight intro: "For the record this is strictly aggregate and orchestration data only" — direct, no fluff
- Numbered lists for hypotheses + asks rather than narrative paragraphs (more scannable for engineers)
- Less hedging — "I'd value your perspective on which is more likely, as to optimize in the future" stays; "happy to be wrong" cuts
- Warm closing without overdoing it — "Sorry for the long message but I wanted to be as comprehensive as possible. Thank you in advance for your help and I look forward to the resolution!"
- Signs off "Best," minimalist (no embedded title block)
- Mid-prose technical detail acceptable (doesn't need every fact in a bullet)

If I draft for him in future, match this register.

---

## What to do if/when the AoU reply lands

1. Open the reply in Zendesk or email
2. Open Claude in this directory, paste:

   > Read .planning/quick/260521-w1-catastrophe-handoff/HANDOFF.md and .planning/quick/260521-w1-catastrophe-handoff/AOU-SUPPORT-FOLLOWUP-DRAFT.md, then read this fresh AoU reply: [paste content]. Recommend the next move per the LD panel decision tree.

3. Claude routes to the correct branch (chr22 smoke / 1000G pivot / further dialogue with AoU) based on the response.

If no reply after 5-7 business days, consider polite Zendesk follow-up in the same ticket thread. Don't open a new ticket — keep the conversation in request 57144.

## Resolved sub-issues (handled in Session 2)

- ~~CC researcher account email on follow-up~~ — no, that account has Gmail disabled
- ~~PhD Candidate signature~~ — corrected to "Assistant Professor & Director, ASHES Laboratory, NC State University"
- ~~"May 4 to May 21" date range~~ — narrowed to "May 17 to May 21" to match the actual bulk-burn window
- ~~$2,140 figure verification~~ — Carter to verify against AoU billing console before any future credit-recovery follow-up; current ticket asks for the technical investigation first
