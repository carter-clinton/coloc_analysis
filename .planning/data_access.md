# data_access.md — data access tracker

**Last verified:** 2026-04-09 (contacts and portal URLs confirmed via direct
research; recheck before acting).

## Executive summary (read this first)

The original assumption — that DUAs for 8 data providers would be the longest
critical path in the project — turned out to be **largely wrong**. A
verification pass found that **6 of the 8 sources are open-access for
summary statistics**, which is all we need for the colocalization, MR, and
replication phases. Only 2 real DUAs remain, and neither of them gates a
T1 phase.

| Data source | What we need | Access model | Wait time | Cost |
|---|---|---|---|---|
| UKB-PPP pQTL | sumstats for Phase 2 3-way coloc | Open (Synapse certified user) | Near-instant | $0 |
| deCODE pQTL | sumstats for Phase 2 3-way coloc | Open download | None | $0 |
| GTEx v8 eQTL/sQTL | sumstats for Phase 2 3-way coloc | Open | None | $0 |
| FinnGen R13/R14 | replication (Phase 9) | Click-wrap registration | Same day | $0 |
| Pan-UKBB | trans-ancestry MR instruments (Phase 3) | Open S3 | None | $0 |
| BBJ PheWeb-JP | EAS replication + MR (Phases 3, 9) | Open download | None | $0 |
| MVP (dbGaP phs001672) | replication (Phase 9) | Open dbGaP | None | $0 |
| UK Biobank main | **not needed for sumstats work** | Full DUA | ~15 weeks | £3-9K+ |
| UK Biobank individual-level (if ever needed) | Phase 8 PRS validation (optional) | Full DUA, Tier 2 | ~15 weeks | ~£6K+ |
| All of Us Controlled Tier | Phase 8 PRS validation, Phase 9 replication | Institutional DURA + training | ~2 business days after DURA | $0 + GCP compute |

**Revised critical path:** Phase 2 (3-way QTL coloc) is **not** DUA-gated
anymore — all three QTL sources (GTEx, UKB-PPP, deCODE) are downloadable on
Day 1. Phase 9 replication is not DUA-gated. The only phase with any real
DUA-ish work is Phase 8 (cross-ancestry PRS, T2-gated), which needs an All
of Us Controlled Tier account, which requires NC State to have a signed
institutional DURA — a ~2-day turnaround if the DURA is already in place,
longer if NC State needs to sign one first.

**REQ-1 is softened:** DUAs no longer block T1 phases. See DECISIONS.md
entry "Data access verified 2026-04-09 — critical path dissolves".

---

## Source status

### 1. UKB-PPP (Olink pQTL — for Phase 2)

- **Access URL:** https://www.synapse.org/Synapse:syn51364943
- **Mirror on AWS Open Data:** https://registry.opendata.aws/ukbppp/
- **Interactive browser:** http://ukb-ppp.gwas.eu
- **Gating:** Free Synapse account + one-time certified-user profile (name, institution, brief intended use). No reviewed DUA for the published summary statistics.
- **Prerequisite:** None — the main UK Biobank DUA is **only needed** for individual-level Olink measurements via UKB-RAP, which we do not need.
- **Reference:** Sun et al. Nature 2023 (doi:10.1038/s41586-023-06592-6).
- **Contact:** No dedicated access email. The AWS Open Data Registry lists the data steward as Matthias Arnold (`matthias.arnold@helmholtz-munich.de`), which is a secondary contact rather than a formal access coordinator. Use the Synapse discussion forum for questions.
- **Status:** `open-access` — can be pulled Day 1 of Phase 0 / Phase 2.

### 2. deCODE pQTL (for Phase 2)

- **Access URL:** https://www.decode.com/summarydata/
- **Gating:** Free direct download, no account, no DUA.
- **Papers:** Ferkingstad et al. 2021 (Nat Genet, doi:10.1038/s41588-021-00978-w) — SomaScan v4, 35,559 Icelanders; and Eiriksdottir/Gudjonsson et al. 2023 (Nature, doi:10.1038/s41586-023-06563-x) — Olink + SomaScan cross-comparison.
- **Caveat:** Individual-level Icelander genotypes are **not** released under Icelandic law. We don't need them.
- **Contact:** No public access email. Corresponding author for both papers is Kari Stefansson (`kstefans@decode.is`), but the data availability statements point to the summarydata portal, not email.
- **Verification note:** The research agent could not scrape the decode.com/summarydata page directly (client-side rendering). **Recommended: do a manual browser visit to confirm the dataset inventory before committing pipeline paths.**
- **Status:** `open-access` — pending a one-time browser verification.

### 3. GTEx v8 (eQTL + sQTL — for Phase 2)

- **Access URL:** https://gtexportal.org/home/downloads/adult-gtex/qtl
- **Gating:** Fully open for summary-level QTL files. Individual-level whole-genome sequences + RNA-seq require dbGaP phs000424 access if ever needed.
- **Status:** `open-access`.
- **Note:** Not in the original 8-source list; added here for completeness because it's the first of the three Phase 2 QTL spines.

### 4. FinnGen (replication for Phase 9 + optional MR cohort)

- **Access URL:** https://www.finngen.fi/en/access_results → application form at https://elomake.helsinki.fi/lomakkeet/124935/lomake.html
- **Contact:** `finngen-info@helsinki.fi`
- **Gating:** Not purely click-through — a lightweight registration form (name, institution, purpose). No reviewed DUA. Download instructions sent by email after form submission. Same-day to next-day access.
- **Current release:** R13/DF13 (Dec 2025). R14 scheduled Feb 2026 per the FinnGen roadmap — check if R14 has dropped by the time we need these.
- **Eligibility:** Academic researchers from US R1 institutions apply directly. Individual-level data goes through Fingenious / FINBB separately (not needed).
- **Cost:** Free. Hosted on Google Cloud Storage.
- **Status:** `registration-required` (click-wrap, not a gate).

### 5. Pan-UKBB (trans-ancestry MR instruments for Phase 3, replication for Phase 9)

- **Access URL:** https://pan.ukbb.broadinstitute.org/downloads
- **Manifest:** https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/phenotype_manifest.tsv.bgz
- **Hail MatrixTable:** GCS bucket referenced from the downloads page
- **Gating:** Fully open anonymous S3 download. CC BY 4.0. No DUA for the published per-phenotype sumstats across AFR, AMR, CSA, EAS, EUR, MID.
- **Prerequisite:** None for sumstats. (UKB Return 2442 — individual ancestry labels and PCs — requires the main UKB DUA, but we don't need that.)
- **Contact:** `ukb.diverse.gwas@gmail.com` (https://pan.ukbb.broadinstitute.org/contact)
- **Coverage:** BMI, T2D, hypertension (ICD10 I10), stroke, asthma all present across all 6 ancestries.
- **Status:** `open-access`.

### 6. BBJ PheWeb-JP (EAS replication for Phases 3, 9)

- **Access URL:** https://pheweb.jp/downloads
- **NBDC mirror:** https://humandbs.dbcls.jp/en/hum0197-v3
- **Gating:** Open. NBDC classifies `hum0197.v3.gwas.v1` as "Un-restricted Access" (released 2021-03-22). Per-phenotype ZIPs are wget-able, e.g. `https://humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.T2D.v1.zip`.
- **Coverage:** BMI, T2D, ischemic stroke, asthma, and blood pressure traits (systolic + diastolic). **Note:** hypertension as a binary disease code is not a standalone file — use BP traits directly or the ICD10 I10 phecode file.
- **Contact:** Open portal, no access contact needed for sumstats. The BBJ office email `shiryo_h@biobankjp.net` is only for individual-level sample/data requests, which we don't need.
- **References:** Ishigaki 2020 Nat Genet (T2D), Sakaue 2021 Nat Genet (BMI/HTN/multi-trait), Kanai 2018 pheweb.
- **Status:** `open-access`.

### 7. MVP (replication for Phase 9)

**CRITICAL finding:** non-VA researchers **cannot** directly apply for
MVP individual-level data. The `research.va.gov/mvp/` page states verbatim:
*"there is no current mechanism for studies led by non-VA researchers"* and
*"Access is only available to VA system users."* This would require a
VA-affiliated PI collaborator, which we don't have and don't want.

**The good news:** MVP cardiometabolic GWAS **summary statistics** are
freely accessible via dbGaP — no VA collaborator needed for the coloc /
MR / replication use case.

- **Access URL:** https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001672
- **dbGaP accession:** `phs001672` (versions v1-v11 as of 2026)
- **Sub-accessions:** T2D at `phs001672.v3.p1` with per-ancestry sub-accessions `pha004943`-`pha004947`; blood pressure, hypertension, CAD, PAD all published
- **Gating:** dbGaP Authorized Access — **public summary statistics** (not individual-level) accessible via the `ftp` browser without a dbGaP DAR application
- **2024 release:** PheWAS results also opened with no application (per NCBI announcement)
- **Contact:** `askmvp@va.gov`, `MVPPO@va.gov`, 1-866-441-6075 — but these are not needed for the dbGaP route
- **Status:** `open-access` via dbGaP for the sumstats we actually need. Individual-level MVP is **blocked** for non-VA researchers but we don't need it.

### 8. All of Us (Researcher Workbench, Controlled Tier — for Phase 8 PRS + Phase 9 replication)

**This is the one real DUA-like gate in the project.**

- **Registration portal:** https://www.researchallofus.org/register/
- **Workbench:** https://workbench.researchallofus.org
- **Gating:** Controlled Tier requires NC State to have a signed **DURA**
  (Data Use and Registration Agreement). Confirm with NC State's Signing
  Official that an AoU DURA is in place — if not, getting one signed is
  the longest step here.
- **Per-researcher steps after the DURA is signed:**
  1. Create Login.gov / ID.me verified account
  2. Complete All of Us Responsible Conduct of Research training (RCR — not CITI)
  3. Sign the Data User Code of Conduct
  4. Apply for Controlled Tier access on the Workbench
  5. ~2 business days for account activation
- **Tier needed:** Controlled Tier (WGS + array + full demographics). Registered Tier only has EHR / survey / wearables / physical measures — insufficient for a cross-ancestry GWAS + PRS.
- **Contact:** No public email. Use https://support.researchallofus.org.
- **Cost:** Workbench access is free. Researchers pay GCP compute (Verily Pre / RW 2.0 as of Feb 2026).
- **Status:** `institutional-DURA-check-first` — this is the one item on the tracker that genuinely needs an early action.

### 9. GBMI (Global Biobank Meta-analysis Initiative, Phase 9)

- **Access URL:** https://www.globalbiobankmeta.org/resources
- **Gating:** Open-access meta-analysis sumstats.
- **Status:** `open-access` — confirmed in the revision plan as a core Phase 9 cohort; not in the original 8-source list but belongs here.

### 10. UK Biobank main DUA (optional — only if we later want individual-level data)

- **Application URL:** https://www.ukbiobank.ac.uk/enable-your-research/apply-for-access
- **AMS portal:** https://ams.ukbiobank.ac.uk/ams/
- **Contact:** `access@ukbiobank.ac.uk`
- **Gating:** Full individual-level DUA, Material Transfer Agreement, tiered fees.
- **Lead time:** Registration review ~10 working days; applications escalated to epidemiologist review within 10 working days; documented average of **~15 weeks** from application submission to actual data release.
- **Cost:** Tiered (GBP, +VAT): Tier 1 ~£3,000, Tier 2 (genotypes/assays) ~£6,000, Tier 3 ~£9,000, +£1,000 per added collaborating institution. Reduced £500 student/LMIC rate. Data flows via UKB-RAP (DNAnexus) with £1,000 platform credits auto-granted through Summer 2026.
- **Prerequisite:** Bona fide researcher at a recognized institution + 5 publications; no UK sponsor needed.
- **Status:** `not-needed-unless`. Only applies if we later decide to run individual-level analyses (e.g., training PRS-CSx in UKB rather than using published sumstats). Revisit at Phase 8 planning.

---

## Action checklist (revised)

**Day 1 (Phase 0 Track 0a):**
- [ ] Register a Synapse account and certify as a researcher (`syn51364943` for UKB-PPP)
- [ ] Download deCODE pQTL sumstats from the summarydata portal **after a manual browser verification** that the dataset inventory matches expectations
- [ ] Register on `finngen.fi/en/access_results` (click-wrap form, same-day)
- [ ] Download GTEx v8 eQTL + sQTL flat files
- [ ] Verify Pan-UKBB manifest + try a tiny download as an S3 connectivity sanity check
- [ ] Download BBJ `hum0197-v3` ZIPs for BMI, T2D, stroke, asthma, BP traits
- [ ] Confirm dbGaP access to MVP `phs001672` summary stats (no DAR needed)
- [ ] **Contact NC State's Signing Official** to confirm whether All of Us DURA is in place for NCSU (if not, start that process — it's the single slowest DUA step in the revised tracker)

**Week 1 of Phase 0:**
- [ ] All of Us account creation + RCR training + Data User Code of Conduct (once DURA is confirmed)
- [ ] Register with GBMI

**Not on Day 1 (deferred until or unless needed):**
- [ ] UK Biobank main DUA — only if Phase 8 PRS decides it needs individual-level data that Pan-UKBB sumstats can't cover. Revisit at Phase 8 planning.

---

## Status legend

- `open-access` — download-and-go, no form, no wait, no fee
- `registration-required` — click-wrap form or account creation, but not a reviewed DUA
- `institutional-DURA-check-first` — gated on NC State having signed an institutional agreement
- `not-needed-unless` — only in scope conditional on a later decision
- `blocked` — inaccessible under current institutional arrangements (e.g. MVP individual-level for non-VA)

## Gates (verified, revised)

| Phase / slice | Blocker | Impact |
|---|---|---|
| Phase 2: UKB-PPP pQTL coloc | Synapse certified-user profile | Same-day |
| Phase 2: deCODE pQTL coloc | Manual portal verification | Same-day |
| Phase 2: GTEx eQTL/sQTL coloc | Download | Same-day |
| Phase 3 (T2): cross-ancestry MR (Pan-UKBB) | Download | Same-day |
| Phase 8 (T2): AoU PRS validation | **NC State AoU DURA check** | Unknown — contact Signing Official first |
| Phase 9: FinnGen replication | Click-wrap registration | Same-day |
| Phase 9: BBJ replication | Download | Same-day |
| Phase 9: MVP replication | dbGaP access | Same-day |
| Phase 9: AoU replication | Same as Phase 8 above | Same as Phase 8 above |
| Phase 9: GBMI replication | Open portal | Same-day |
