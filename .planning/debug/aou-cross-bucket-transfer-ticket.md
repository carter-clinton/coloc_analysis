# AoU Support Ticket — cross-perimeter file transfer (MOOT — DO NOT PURSUE)

**Status:** ⛔ MOOT / CLOSED 2026-06-11. The cross-perimeter transfer was OBVIATED:
the self-report sidecar was regenerated natively in-perimeter against the v8 CDR
(`wb-silky-artichoke-2408.C2024Q3R8`), so no classic→Verily transfer was ever
needed. The AFR-sens cohort is built + banked (62,557×20,817,925). **Stop tracking
the AoU reply; do not re-send.** The VPC-SC perimeter knowledge below is preserved
for reference but is now distilled into the `aou-ld-pipeline` skill +
[[reference_aou_rw2_mirror_vpcsc]] — regenerate in-perimeter, never transfer.

---

_Historical (the ticket as sent):_ ✅ SENT 2026-06-08 via the AoU help desk
("Your request was sent. An agent will get back to you soon."). Was the only
remaining blocker for the AFR-sens cohort (D-M3-07); the critical path (EUR + LD
panel) never depended on it.

## Why this ticket exists (one-line)

The validated self-report sidecar TSV sits in the **classic** RW 1.0 workspace
bucket; the AFR-sens re-fire (cluster job, PET SA) reads it from the **migrated
Verily** RW 2.0 bucket. The two buckets are in different VPC-SC perimeters, and
**every self-serve transfer path is confirmed dead** (proven 2026-06-08):
- PET-to-PET copy → IAM 403 (the two PET SAs are mutually walled)
- user CLI as `cclinton@researchallofus.org` (reads BOTH buckets fine) → the
  cross-bucket `gsutil cp` is **VPC-SC-blocked by org policy**
- project switch (`wb-perky-corn-6639`) → same VPC-SC denial (it's the
  perimeter, not the quota project)
- Cloud Console as the same identity → same API → same perimeter block
This is the migration's two-perimeter split working as designed; we did NOT
attempt to bypass it. AoU's sanctioned in-perimeter transfer is the path.

## WHERE TO SEND

AoU Researcher Workbench **"Contact Us" / help desk** (in the workbench UI) or
**support@researchallofus.org**. If there is a separate Verily Workbench support
channel for the migrated workspace, send there too.

## SUBJECT

Sanctioned in-perimeter file transfer between classic RW 1.0 bucket and migrated
Verily Workbench 2.0 bucket (VPC-SC blocks self-serve copy)

## BODY (copy-paste)

> I migrated workspace **aou-rw-476cdac2** ("coloc_analysis") from classic
> Researcher Workbench 1.0 to Verily Workbench 2.0 (project `wb-perky-corn-6639`).
> I need to copy **one researcher-generated derived file** from my classic
> workspace bucket into my migrated Verily workspace bucket. Standard transfer
> fails because the two environments are PET-walled and VPC-SC-protected.
>
> **File:** `self_report.tsv` — ~19.7 MB (20,643,040 bytes), 633,548 rows, two
> columns (`research_id` + self-reported race category). Researcher-generated
> from the controlled-tier CDR `person` table — NOT raw CDR.
>
> **Source (classic bucket):**
> `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/aux/self_report/self_report.tsv`
>
> **Destination (migrated Verily bucket):**
> `gs://rw-migration-aou-rw-476cdac2/ld/aux/self_report/self_report.tsv`
>
> **What I confirmed (so you can route it fast):** as my authenticated AoU user
> identity `cclinton@researchallofus.org` I can `gsutil ls` BOTH buckets
> individually, but a cross-bucket `gsutil cp` is blocked by **VPC Service
> Controls org policy** — a cross-perimeter transfer between
> `terra-vpc-sc-fe7a5641` (classic) and `wb-perky-corn-6639` (Verily). The two
> in-workspace PET service accounts are also mutually walled. I am NOT trying to
> bypass the perimeter; I need the sanctioned in-perimeter mechanism. VPC-SC
> denial references:
> `vpcServiceControlsUniqueIdentifier: 4DqA2GD_xrfSzliJ99zg47wtZ5mPWwt9sdDmGbNl0AnPxSWHNUCOkWwaNedZEKCjShMMYaQmrrdy-SUo`
> `vpcServiceControlsUniqueIdentifier: ttK8pFPawC_d4IhWOktitOnH_CHp3SdoRI4leWqfb3GWOI5XeWenJ21yFw4uPK5e_zQW9RyQQ82lpQ5X`
>
> **My ask — either resolution works:**
> 1. Run the migration/transfer tool (or re-run the classic→Verily migration
>    copy) for this single file; OR
> 2. Grant a scoped, temporary `roles/storage.objectViewer` on the source object
>    to my Verily workspace PET SA
>    (`pet-2766287214923ed0b0e17@wb-perky-corn-6639.iam.gserviceaccount.com`) so
>    my migrated workspace can read it directly.
>
> Workspace namespace: **aou-rw-476cdac2** · Verily project: **wb-perky-corn-6639**.

## AFTER AoU RESOLVES IT

- **If they pick option 2 (IAM grant, no copy):** skip the relay — point the
  re-fire at the classic path directly:
  `self_report_table_path="gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/aux/self_report/self_report.tsv"`
- **If they copy the file (option 1):** it lands at
  `gs://rw-migration-aou-rw-476cdac2/ld/aux/self_report/self_report.tsv` — verify
  size 20,643,040 bytes, then re-fire.

Then (both cases): `mv` the contaminated `mt_afr_pca_selfid_*` (final +
`intermediate/`) to `ld/_forensics/contaminated_afr_selfid_noop_20260608/` →
FRESH re-fire AFR-sens (`sensitivity=True, force_fresh=True,
self_report_table_path=<resolved path>`). Arbiter: `count_cols` STRICTLY < 73,122
AND `.describe()` now shows `self_report`; build prints `N_pre -> N_post`; the
coverage + proper-subset asserts hard-fail loudly if anything is off.

## DATA-VALIDATION RECEIPT (already done, don't re-do)

TSV checks 1–4 all GREEN (2026-06-08): header `research_id<TAB>self_report`;
633,548 rows; 99,788 `WhatRaceEthnicity_Black`; `research_id` == MT `s` key (both
str bare integer person_ids — verified `mt_afr_qc.mt.s.take(5)` = ['1000000',
'1000042', ...] vs TSV ['1447308', ...], same space). Producer↔consumer lockstep
on `WhatRaceEthnicity_Black` confirmed (commit 06b8a97; SENS_FILTER_VERSION=2).
