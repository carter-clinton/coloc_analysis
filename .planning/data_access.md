# data_access.md — data access tracker

**Last verified:** 2026-04-10 (HPC connectivity verified for all 8 open-access
sources; contacts and portal URLs confirmed via prior research 2026-04-09).

**OSF pre-registration:** `doi:10.17605/OSF.IO/PVB5J` — submitted 2026-04-10, public, non-embargoed. Registration ID `pvb5j`. Linked OSF project `az52u`. Registration URL: https://osf.io/pvb5j/. Template: OSF Preregistration. Title: *Mechanistic resolution of pleiotropy at cardiometabolic loci: a cross-ancestry framework integrating fine-mapping, three-way QTL colocalization, bidirectional Mendelian randomization, and selection analysis across BMI, type 2 diabetes, hypertension, ischemic stroke, and asthma.* License: CC0 1.0 Universal. Full draft text preserved at `.planning/osf_prereg_draft.md`.

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
| All of Us Controlled Tier | Phase 8 PRS validation, Phase 9 replication | **Already credentialed** | N/A | $0 + GCP compute |

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
- **HPC connectivity:** Verified 2026-04-10 — `curl -sI https://www.synapse.org/Synapse:syn51364943` returned HTTP 200. Portal reachable from NCSU HPC.
- **User access verified 2026-04-10:** Carter passed Synapse Certification Quiz 15/15 on 2026-04-10 19:10 UTC. `syn51364943` project page fully accessible (Wiki, Files, Tables, Discussion tabs visible). S3 bucket `s3://ukbiobank.opendata.sagebase.org/` exposed for direct HPC downloads. **Ready for Phase 2 pQTL coloc.**

### 2. deCODE pQTL (for Phase 2)

- **Access URL:** https://www.decode.com/summarydata/
- **Gating:** **Revised 2026-04-10** — not a simple direct download. User clicks "Summary data (list)" for the Ferkingstad 2021 study, which triggers an email from `noreply-decode@decode.com` with an ephemeral link `https://download.decode.is/folder/<UUID>` **valid for only 5 days**. No account, no DUA, but the link mechanism blocks static-URL Snakemake download rules.
- **Papers:** Ferkingstad et al. 2021 (Nat Genet, doi:10.1038/s41588-021-00978-w) — SomaScan v4, 35,559 Icelanders. (Earlier docs referenced Eiriksdottir/Gudjonsson 2023 — **not present on the portal**; that paper was a methods cross-comparison, not a new release.)
- **Caveat:** Individual-level Icelander genotypes are **not** released under Icelandic law. We don't need them.
- **Contact:** No public access email. Corresponding author is Kari Stefansson (`kstefans@decode.is`), but the data availability statement points to the summarydata portal.
- **Dataset inventory (verified 2026-04-10 via browser):**
  - **24,271 files** — one file per SOMAmer (SomaScan aptamer), ~910 MB each
  - **Total size: ~24 TB**
  - **File naming pattern:** `{SOMAMERID}_{VERSION}_{GENE}_{PROTEIN}.txt.gz` — e.g., `10000_28_CRYBB2_CRBB2.txt.gz`, `10001_7_RAF1_c_Raf.txt.gz`
  - **Index pagination:** 100 files per page, 243 pages total
  - **Separate files:** ReadMe (2 KB, schema docs), Extra annotation (430 MB), Excluded variants (52 MB)
  - **Web UI:** https://download.decode.is/folder/<UUID> with searchable file list, checkbox selection, and "Download Files" button
- **Status:** `open-access` (email-gated ephemeral link) — one-time browser request required per download session.
- **HPC connectivity:** Verified 2026-04-10 — portal page loads (HTTP 200, client-side rendered). Email-delivered folder URL confirmed functional in browser.

**CRITICAL architecture implication for Phase 2:** The original assumption that deCODE pQTL could be pulled via a static Snakemake download rule is **wrong**. Phase 2 must instead use a two-step flow: (1) targeted protein-filter step (derive candidate gene list from lead SNPs at our ~50 pleiotropic loci + literature-curated trait-associated proteins, realistic target ~100-500 proteins), (2) manual re-request of the deCODE portal link when ready, followed by a subset download of only the SOMAmer files matching the target gene list. Bulk 24 TB download is not feasible (download-window-limited and not needed — we only need proteins mapped to our trait loci). Gene name is embedded in the filename, so `grep <gene>` against the file index suffices for filtering.

**Phase 0 downloads (completed 2026-04-10):**
- [x] ReadMe file — saved to `/rs1/researchers/c/ckclinto/coloc_analysis/data/raw/decode_pqtl/README.txt` (symlinked from `data/raw/decode_pqtl/`)
- [x] 3 test SOMAmer files — all gzip-intact after re-download of ZNF41: `10000_28_CRYBB2_CRBB2.txt.gz` (910 MB), `10001_7_RAF1_c_Raf.txt.gz` (909 MB), `10003_15_ZNF41_ZNF41.txt.gz` (909 MB). `gzip -t` passes for all three (verified 2026-04-10).

**⚠ Schema documentation bug (deCODE README):** The deCODE README lists column 9 as `min_log10_pval`, but the actual file header uses `minus_log10_pval`. Phase 2 `config/datasets.yaml` `column_map` for deCODE **must use the real column name** (`minus_log10_pval`). Verified 2026-04-10 via `zcat 10000_28_CRYBB2_CRBB2.txt.gz | head -1`. Actual 12-column schema: `Chrom  Pos  Name  rsids  effectAllele  otherAllele  Beta  Pval  minus_log10_pval  SE  N  ImpMAF`.

**File count anomaly to investigate in Phase 2:** README says 4,907 aptamers, but the download portal listed 24,271 files. ~5× discrepancy — possibly multiple SeqId versions per aptamer or per-chromosome splits. Worth confirming before building the protein-filter step.

### 3. GTEx v8 (eQTL + sQTL — for Phase 2)

- **Access URL:** https://gtexportal.org/home/downloads/adult-gtex/qtl
- **Gating:** Fully open for summary-level QTL files. Individual-level whole-genome sequences + RNA-seq require dbGaP phs000424 access if ever needed.
- **Status:** `open-access`.
- **Note:** Not in the original 8-source list; added here for completeness because it's the first of the three Phase 2 QTL spines.
- **HPC connectivity:** Verified 2026-04-10 — GTEx portal page (`https://gtexportal.org/home/downloads/adult-gtex/qtl`) returned HTTP 200. GCS bucket confirmed reachable: `https://storage.googleapis.com/adult-gtex/bulk-qtl/v8/single-tissue-cis-qtl/GTEx_Analysis_v8_eQTL.tar` returned HTTP 200 (1.56 GB tar). **Note:** Correct GCS path prefix is `bulk-qtl/v8/`, not `bulk-gex/v8/` as some references state.

### 4. FinnGen (replication for Phase 9 + optional MR cohort)

- **Access URL:** https://www.finngen.fi/en/access_results → application form at https://elomake.helsinki.fi/lomakkeet/124935/lomake.html
- **Contact:** `finngen-info@helsinki.fi`
- **Gating:** Not purely click-through — a lightweight registration form (name, institution, purpose). No reviewed DUA. Download instructions sent by email after form submission. Same-day to next-day access.
- **Current release:** **R12** — confirmed 2026-04-10 via registration email from `elomake@helsinki.fi` / `finngen-servicedesk@helsinki.fi`. (Earlier research assumed R13/R14 would be live; actual current public release is R12. Revisit before Phase 9 in case R13+ drops.)
- **Eligibility:** Academic researchers from US R1 institutions apply directly. Individual-level data goes through Fingenious / FINBB separately (not needed).
- **Cost:** Free. Hosted on Google Cloud Storage.
- **Status:** `registration-required` (click-wrap, not a gate). **Registered 2026-04-10.**
- **HPC connectivity:** Verified 2026-04-10 — R10 sumstats bucket reachable (legacy check). Actual R12 URLs now confirmed via post-registration email (see User access below).
- **User access verified 2026-04-10:** Carter completed the elomake.helsinki.fi registration form (lomake 124935) on 2026-04-10 ~19:15 UTC. Confirmation email received immediately from `finngen-servicedesk@helsinki.fi`. Confirmed R12 download endpoints:
  - **Web browser:** `https://console.cloud.google.com/storage/browser/finngen-public-data-r12/summary_stats/`
  - **Additional folders:** `/finemap/`, `/annotations/`, `/hla/`, `/meta_analysis/ukbb/`, `/lof/`, `/lab_values/`
  - **Direct HTTP download (wget/curl):** `https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release/finngen_R12_<PHENOTYPE>.gz`
  - **GCS native path:** `gs://finngen-public-data-r12/...`
  - **Example phenotype file:** `finngen_R12_AB1_ACTINOMYCOSIS.gz`
  - **Ready for Phase 9 replication.** Phase 9 Snakemake download rules should use the `finngen-public-data-r12` bucket name and the `summary_stats/release/` path prefix.

### 5. Pan-UKBB (trans-ancestry MR instruments for Phase 3, replication for Phase 9)

- **Access URL:** https://pan.ukbb.broadinstitute.org/downloads
- **Manifest:** https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/phenotype_manifest.tsv.bgz
- **Hail MatrixTable:** GCS bucket referenced from the downloads page
- **Gating:** Fully open anonymous S3 download. CC BY 4.0. No DUA for the published per-phenotype sumstats across AFR, AMR, CSA, EAS, EUR, MID.
- **Prerequisite:** None for sumstats. (UKB Return 2442 — individual ancestry labels and PCs — requires the main UKB DUA, but we don't need that.)
- **Contact:** `ukb.diverse.gwas@gmail.com` (https://pan.ukbb.broadinstitute.org/contact)
- **Coverage:** BMI, T2D, hypertension (ICD10 I10), stroke, asthma all present across all 6 ancestries.
- **Status:** `open-access`.
- **HPC connectivity:** Verified 2026-04-10 — `curl -sI https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/phenotype_manifest.tsv.bgz` returned HTTP 200. S3 bucket accessible from NCSU HPC with no authentication.

### 6. BBJ PheWeb-JP (EAS replication for Phases 3, 9)

- **Access URL:** https://pheweb.jp/downloads
- **NBDC mirror:** https://humandbs.dbcls.jp/en/hum0197-v3
- **Gating:** Open. NBDC classifies `hum0197.v3.gwas.v1` as "Un-restricted Access" (released 2021-03-22). Per-phenotype ZIPs are wget-able, e.g. `https://humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.T2D.v1.zip`.
- **Coverage:** BMI, T2D, ischemic stroke, asthma, and blood pressure traits (systolic + diastolic). **Note:** hypertension as a binary disease code is not a standalone file — use BP traits directly or the ICD10 I10 phecode file.
- **Contact:** Open portal, no access contact needed for sumstats. The BBJ office email `shiryo_h@biobankjp.net` is only for individual-level sample/data requests, which we don't need.
- **References:** Ishigaki 2020 Nat Genet (T2D), Sakaue 2021 Nat Genet (BMI/HTN/multi-trait), Kanai 2018 pheweb.
- **Status:** `open-access`.
- **HPC connectivity:** Verified 2026-04-10 — `curl -sI https://humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.T2D.v1.zip` returned HTTP 200. File size ~1.6 GB confirmed. NBDC server accessible from NCSU HPC.

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
- **HPC connectivity:** Verified 2026-04-10 — `curl -sI https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001672` returned HTTP 302 (expected redirect for NCBI CGI). Study page accessible from NCSU HPC.

### 8. All of Us (Researcher Workbench, Controlled Tier — for Phase 8 PRS + Phase 9 replication)

**Carter already has Controlled Tier access.** This is no longer a gate.

- **Workbench:** https://workbench.researchallofus.org
- **Tier:** Controlled Tier (WGS + array + full demographics).
- **Cost:** Workbench access is free. Researchers pay GCP compute.
- **Contact:** https://support.researchallofus.org if issues arise.
- **Architecture:** Individual-level data stays inside the workbench.
  Summary stats and aggregate metrics (R², AUC, calibration plots, etc.)
  can be exported. See DECISIONS.md entry "All of Us: workbench-in /
  summary-out strategy" for the Phase 8 / Phase 9 design.
- **Status:** `credentialed` — no action needed.

### 9. GBMI (Global Biobank Meta-analysis Initiative, Phase 9)

- **Access URL:** https://www.globalbiobankmeta.org/resources
- **Gating:** Open-access meta-analysis sumstats.
- **Status:** `open-access` — confirmed in the revision plan as a core Phase 9 cohort; not in the original 8-source list but belongs here.
- **HPC connectivity:** Verified 2026-04-10 — `curl -sI https://www.globalbiobankmeta.org/resources` returned HTTP 200. Portal accessible from NCSU HPC (Wix-hosted site).

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
- [x] Register a Synapse account and certify as a researcher (`syn51364943` for UKB-PPP) — *Completed 2026-04-10: Certification Quiz passed 15/15; syn51364943 project page fully accessible; S3 bucket `s3://ukbiobank.opendata.sagebase.org/` confirmed reachable*
- [x] Verify deCODE summarydata portal inventory in browser — *Completed 2026-04-10: 24,271 SOMAmer files confirmed (24 TB total); ephemeral download link mechanism confirmed (5-day validity); file naming pattern `{SOMAMERID}_{VERSION}_{GENE}_{PROTEIN}.txt.gz` captured. **Phase 2 architecture impact recorded** — see dataset inventory entry above.*
- [ ] Phase 2 targeted deCODE download (deferred) — will re-request the portal link when Phase 2 is ready to consume pQTL; filter to ~100-500 trait-relevant proteins before downloading
- [x] Register on `finngen.fi/en/access_results` (click-wrap form, same-day) — *Completed 2026-04-10: form submitted via elomake (lomake 124935); confirmation email received from finngen-servicedesk@helsinki.fi; **actual current release is R12** (not R13/R14); bucket `finngen-public-data-r12` with `summary_stats/release/` path prefix; ready for Phase 9*
- [x] Download GTEx v8 eQTL + sQTL flat files — *HPC connectivity verified 2026-04-10: GCS bucket reachable at `bulk-qtl/v8/single-tissue-cis-qtl/` (HTTP 200, 1.56 GB tar confirmed). Correct path prefix is `bulk-qtl/`, not `bulk-gex/`. Ready for Snakemake download rule.*
- [x] Verify Pan-UKBB manifest + try a tiny download as an S3 connectivity sanity check — *verified 2026-04-10: phenotype_manifest.tsv.bgz returned HTTP 200 from S3*
- [x] Download BBJ `hum0197-v3` ZIPs for BMI, T2D, stroke, asthma, BP traits — *HPC connectivity verified 2026-04-10: hum0197.v3.BBJ.T2D.v1.zip returned HTTP 200 (~1.6 GB). NBDC server accessible.*
- [x] Confirm dbGaP access to MVP `phs001672` summary stats (no DAR needed) — *verified 2026-04-10: study page returns HTTP 302 (expected NCBI redirect). Accessible from HPC.*
- [x] ~~Contact NC State's Signing Official about AoU DURA~~ — **Carter already has Controlled Tier access (confirmed 2026-04-09)**

**Week 1 of Phase 0:**
- [x] Register with GBMI — *HPC connectivity verified 2026-04-10: resources page HTTP 200. Open-access meta-analysis sumstats, no registration gate.*
- [x] ~~All of Us account creation~~ — already credentialed

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
| Phase 8 (T2): AoU PRS validation | Already credentialed | Upload PRS weights, score inside workbench |
| Phase 9: FinnGen replication | Click-wrap registration | Same-day |
| Phase 9: BBJ replication | Download | Same-day |
| Phase 9: MVP replication | dbGaP access | Same-day |
| Phase 9: AoU replication | Already credentialed | Export GWAS sumstats from workbench |
| Phase 9: GBMI replication | Open portal | Same-day |

---

## bmi.AFR (Phase 4 dependency, 2026-04)

**Context:** Phase 4 matched-N cross-ancestry concordance requires AFR BMI
summary statistics for the EUR->AFR bootstrap. Pan-UKBB AFR BMI (N~6k) is
insufficient — SE-inflation ratio sqrt(700k/6k) = 10.8x pushes bootstrap into
noise-dominated regime. Per RESEARCH C-1 (SUPERSEDED), MVP or AoU provide
~9x larger AFR BMI samples.

### Tier 1: MVP phs002453 (preferred)

- **Accession:** dbGaP phs002453
- **Build:** GRCh38 (requires liftover to GRCh37 per Phase 1 LD panel convention)
- **N_AFR:** ~55,525 (Huang et al. 2022 Nat Commun s41467-022-35553-2)
- **SE-inflation ratio:** sqrt(700k/55.5k) = 3.55x (comparable to other 4 traits)
- **Access:** dbGaP public release 2024-07-22 (NCBI Insights announcement).
  No DAR required for summary statistics.
- **Next action:**
  - [ ] Verify phs002453 BMI AFR sumstats are downloadable without DAR
  - [ ] If accessible: download + harmonize via Phase 9 MVP harmonizer pattern
  - [ ] Liftover GRCh38 -> GRCh37 inline per Phase 9 09-02 harmonizer convention

### Tier 2: AoU BMI AFR (alternative)

- **Source:** All of Us Researcher Workbench
- **Build:** GRCh38
- **N_AFR:** ~54,940 (Nat Commun 2025 s41467-025-58420-2)
- **SE-inflation ratio:** sqrt(700k/54.9k) = 3.57x
- **Access:** AoU Researcher Workbench (Carter credentialed per CLAUDE.md).
  Sumstats exportable; individual-level stays on Workbench.
- **Next action:**
  - [ ] If Tier 1 (MVP) not accessible: export BMI AFR sumstats from AoU Workbench
  - [ ] Harmonize to project schema + liftover GRCh38 -> GRCh37

### Tier 3: Pan-UKBB AFR BMI field 21001 (last-resort fallback)

- **Source:** Pan-UKBB S3 bucket (pan.ukbb.broadinstitute.org)
- **Build:** GRCh37
- **N_AFR:** ~6,000 (phenotype manifest field 21001)
- **SE-inflation ratio:** sqrt(700k/6k) = 10.8x (noise-dominated — H7 verdict
  loses scientific grip per RESEARCH C-1)
- **Access:** Open S3, anonymous download, CC BY 4.0.
- **Next action:**
  - [ ] Only use if Tier 1 AND Tier 2 both fail
  - [ ] Flag in Table 2 per D-03c / Deferred-d: "AFR-unavailable at scale"
  - [ ] Report global LDSC r_g (AFR vs EUR BMI) as proxy instead of matched-N bootstrap

---

## SE-inflation reference resolution (RESEARCH Q1)

**Resolved:** 2026-04-16

The SE-inflation formula `SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR)` is the
analytic consequence of how Z-scores and beta/SE scale under reduced N with
fixed per-variant effect size. This is a standard analytic rescaling documented
across multiple references:

- **Primary support:** Mahajan et al. 2022 Nature Genetics (DIAMANTE-AFR),
  Methods section describes SE-inflation for cross-ancestry power matching at
  T2D loci (DOI 10.1038/s41588-022-01058-3, PMID 35551307).
- **Secondary support:** Zou et al. 2022 (SuSiE-RSS, PLOS Genet PMC9337707) —
  supports independent-Z resampling with fixed R for SuSiE refit.
- **Tertiary support:** MultiSuSiE 2025 (Nat Genet s41588-025-02450-5) —
  confirms calibration of SuSiE refit under resampled Z in multi-ancestry
  simulation.

**Status:** Accept as established methodology. The formula is first-principles
derivable (Var(beta_hat) scales as 1/N, so SE scales as sqrt(1/N), giving
the ratio SE_matched/SE_full = sqrt(N_full/N_target)). No single paper
"owns" this formula — it is textbook statistical genetics.

---

## NCSU LSF compute quota (RESEARCH Q4)

**Queried:** 2026-04-16 via `bqueues -u ckclinto`

### Standard partition (primary for Phase 4 bootstrap)

| Property | Value |
|----------|-------|
| Queue name | `standard` |
| Max concurrent slots (JL/U) | **1024** per user |
| Queue-level max slots | unlimited |
| Current load | 96 running / 79 pending (low contention) |
| Priority | 64 |

### Other relevant queues

| Queue | JL/U | Max run time | Notes |
|-------|------|-------------|-------|
| `short` | 1024 | 2 hours | Good for bootstrap pilot (100 fits < 1 hr) |
| `long` | 512 | 5 days | Fallback if standard wall-clock too tight |
| `serial` | 1024 | 10 days | Single-core, longest wall-clock |
| `debug` | 64 | 4 hours | Quick testing only |

### Compute envelope calibration for Phase 4

With 1024 concurrent slots on `standard`:
- 300k SuSiE fits / 1024 parallel = ~293 sequential batches
- At ~30 seconds/fit (Zou 2022 SuSiE-RSS benchmark, 1k SNPs/region): ~8,790 seconds = ~2.4 hours
- At ~2 min/fit (conservative, larger regions): ~9,840 min / 1024 = ~9.6 hours
- **Estimated wall-clock: 3-24 hours** depending on per-fit runtime, which the pilot
  (1 trait x 10 regions x 10 bootstraps = 100 fits) will calibrate.
- **A-1 RESEARCH verdict:** 3-5 day estimate is achievable under 1024-slot quota.
  The original concern about needing 2000+ cores (RESEARCH A-1) is resolved — 1024
  concurrent slots is sufficient.

**Next action for Plan 04-05 T1:** Run pilot (100 fits) on `short` queue to
measure per-fit wall-clock and extrapolate to full 300k launch.
