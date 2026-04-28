# All of Us Researcher Workbench — Publications & Presentations (P&P) Registration

> **Paste-ready Markdown for the AoU P&P portal.** This document contains TWO
> distinct P&P registration blocks, one per anticipated publication. Both
> registrations are filed at draft stage in the AoU Researcher Workbench P&P
> portal **before** any external submission, per AoU publication policy and
> per the project's own gating constraint (`AOU-LD-PIPELINE.md` §2 P6 + §12 R6).
>
> **Carter pastes each block section-by-section into the portal**, trimming
> each field to the live AoU character limit. AoU portal field limits vary;
> trim conservatively at paste time. Update the registration at every major
> scope change (per §12 R6); update again at submission with the final author
> list, journal name, and submission date.
>
> **Cross-link:** `AOU-WORKBENCH-REGISTRATION.md` (workspace registration; this
> P&P registration assumes that workspace is live and the Data Use Statement
> is approved).

---

## Block 1 — Track B → *Nature Genetics*

### 1.1 Publication Title (working)

> Genome-wide cross-trait pleiotropy and novel-variant discovery across nine
> complex traits in European and African ancestries using ancestry-matched
> linkage disequilibrium from All of Us whole-genome sequencing.

[src: PROJECT.md "What" §; PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3]

### 1.2 Authors

| Role | Name | Affiliation | ORCID |
|---|---|---|---|
| First / Corresponding | Carter K. Clinton | ASHES Lab, North Carolina State University | TODO — Carter to fill |

[src: PROJECT.md "Who" §; CITATION.cff in Track A submission bundle (`track_a_genome_medicine_submission.zip`) carries the same ORCID-as-TODO placeholder pending Carter portal action]

### 1.3 Anticipated Journal / Venue

> *Nature Genetics* (primary). Fallback ladder is set at the project level
> per Amendment §11 but is not declared on this P&P record; the AoU P&P record
> tracks the primary venue and is updated if the venue changes.

[src: PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §11; PROJECT.md "Goals" §1]

### 1.4 Anticipated Submission Date

> 2027-04 / 2027-05 (per Amendment §11 timeline; downstream of M6 closeout).

[src: PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §11]

### 1.5 Workspace(s) Used

> The Track B + M3 workspace registered per `AOU-WORKBENCH-REGISTRATION.md`.
> Workspace title: as declared in §1 of that document. AoU CDR Release: locked
> at workspace setup; recorded in workspace metadata. AoU Tier: **Controlled**
> (whole-genome sequence access required for AFR LD panel build).

[src: AOU-WORKBENCH-REGISTRATION.md §1; AOU-LD-PIPELINE.md §2 P1–P3]

### 1.6 AoU CDR Release Version

> **TODO — lock at workspace setup.** Anticipated v7 Controlled Tier, Curated
> Data Repository release C2025Q1 or successor. Update this P&P record if the
> CDR release used in the analysis differs from what is locked here.

[src: AOU-LD-PIPELINE.md §13.1 placeholder language; AOU-WORKBENCH-REGISTRATION.md §6 egress plan]

### 1.7 AoU Data Tier

> **Controlled Tier.** Required for whole-genome sequence access used in
> ancestry-matched LD panel construction.

[src: AOU-LD-PIPELINE.md §1 introduction; AOU-WORKBENCH-REGISTRATION.md §6.1 egress plan]

### 1.8 Plain-Language Lay Summary

> Existing publicly-available reference data on patterns of inheritance in
> populations of African ancestry are too small (n=661 in the most widely
> used reference, the 1000 Genomes Project) to allow modern fine-mapping
> methods to pinpoint specific causal genetic variants for traits like
> blood pressure, kidney function, and lipid levels. This work uses All of
> Us whole-genome sequence data from approximately 60,000 to 95,000
> participants of African ancestry to build a much larger, ancestry-matched
> reference resource. We then apply that resource to nine complex traits
> across European and African ancestries to identify new genetic variants
> and previously-unrecognized shared genetic architecture. All All of Us
> outputs are summary-level statistics; no individual-level data leaves the
> Researcher Workbench. Aggregate cell counts below 20 are suppressed.

[src: AOU-LD-PIPELINE.md §2.1 RPS template language; AOU-WORKBENCH-REGISTRATION.md §2 plain-language summary; PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §5]

### 1.9 Methods Summary (using AoU data)

> Ancestry-matched linkage-disequilibrium (LD) reference matrices were
> computed in the All of Us Researcher Workbench from whole-genome sequence
> data on participants with genetically-inferred African ancestry
> (`ancestry_pred == "afr"` per the AoU PCA-based ancestry pipeline) after
> removal of related individuals at KING kinship coefficient ≥ 0.0442.
> Per-variant QC required minor allele frequency ≥ 0.005 in the AFR subset,
> variant call rate ≥ 0.95, Hardy-Weinberg p ≥ 10⁻⁶ in AFR, and removal of
> AoU-flagged variants. Multiallelic sites were decomposed into biallelic
> variants. For each fine-mapping region (±1 Mb around each lead associated
> variant from Track B M2 discovery), Pearson correlation LD matrices were
> computed from allele dosages using Hail v0.2.x (`hl.ld_matrix`). Only
> aggregate (variant × variant) LD matrices were exported from the
> Researcher Workbench; no individual-level genotypes or phenotypes were
> exported. Downstream fine-mapping and colocalization (SuSiE-RSS,
> coloc.susie, HyPrColoc, PolyFun baselineLF2 priors) was run at the
> NCSU institutional HPC on the exported aggregate matrices.

[src: AOU-LD-PIPELINE.md §13.1 Methods paragraph (updated for current pipeline); AOU-WORKBENCH-REGISTRATION.md §3 Scientific Approach + §4 Methods Inventory]

### 1.10 Anticipated Findings

Five pre-registered novel-variant discovery classes per Amendment §7:

1. **Joint-signal pleiotropy variants** — variants reaching genome-wide
   significance in MTAG / CPASSOC joint analysis but not in any single-trait
   analysis.
2. **Ancestry-specific variants** — variants reaching genome-wide significance
   in AFR but absent from EUR-ancestry catalogs.
3. **Secondary independent variants** — conditional / fine-mapped credible-set
   members beyond the published lead at known loci.
4. **Pleiotropy-class variants** — variants reaching ≥3-trait joint signal
   under HyPrColoc with PP > 0.5.
5. **Functional-mechanism variants** — credible-set variants supported by
   matched-tissue eQTL / sQTL / pQTL colocalization.

Yield ranges and locked comparator catalogs (GWAS Catalog, Pickrell 2016,
Watanabe 2019, Open Targets L2G, ClinVar) with SHA-256 version checksums are
documented in the workspace registration and in the Amendment.

[src: PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §7.1–§7.3; AOU-WORKBENCH-REGISTRATION.md §7 Anticipated Findings]

### 1.11 Demographics / Ancestry Usage

> All ancestry assignments are derived from the All of Us PCA-based
> `ancestry_pred` field (i.e., genetically-inferred ancestry from the AoU
> internal PCA pipeline trained against a 1000G + HGDP reference). Self-
> reported race and ethnicity are NOT used for cohort definition or for
> any analytic stratification. The PCA-based AFR cohort is the primary
> analytic stratum; the PCA-based EUR cohort is reported in parallel for
> sensitivity comparison. No analyses condition on age, sex, or
> socioeconomic indicators.

[src: AOU-LD-PIPELINE.md §3.1 AFR-ancestry inclusion logic; AOU-WORKBENCH-REGISTRATION.md §10 Use of Race/Ancestry/Demographics]

### 1.12 Race / Ethnicity Reporting Plan

> The manuscript reports cohort sizes by genetically-inferred ancestry
> (PCA-based; AFR primary, EUR sensitivity). Self-reported race and
> ethnicity are not analytically used and are not reported as analytic
> variables. The methods section explicitly states the PCA-based
> definition and the rationale for not using self-reported race for
> ancestry stratification.

[src: AOU-WORKBENCH-REGISTRATION.md §10.1–§10.2 PCA-based ancestry framing + WILL/WILL-NOT lists]

### 1.13 Required AoU Citation

> The All of Us Research Program (ClinicalTrials.gov Identifier: NCT03658122).

[src: AOU-LD-PIPELINE.md §13.3 verbatim; verify current AoU citation language ≤ 1 week before submission per §12 R11]

### 1.14 Acknowledgments Boilerplate

> The All of Us Research Program is supported by the National Institutes of
> Health, Office of the Director: Regional Medical Centers: 1 OT2 OD026549;
> 1 OT2 OD026554; 1 OT2 OD026557; 1 OT2 OD026556; 1 OT2 OD026550;
> 1 OT2 OD 026552; 1 OT2 OD026553; 1 OT2 OD026548; 1 OT2 OD026551;
> 1 OT2 OD026555; IAA #: AOD 16037; Federally Qualified Health Centers:
> HHSN 263201600085U; Data and Research Center: 5 U2C OD023196; Biobank:
> 1 U24 OD023121; The Participant Center: U24 OD023176; Participant
> Technology Systems Center: 1 U24 OD023163; Communications and Engagement:
> 3 OT2 OD023205; 3 OT2 OD023206; and Community Partners: 1 OT2 OD025277;
> 3 OT2 OD025315; 1 OT2 OD025337; 1 OT2 OD025276. In addition, the All of
> Us Research Program would not be possible without the partnership of its
> participants.

> **Verify current funding acknowledgment text at submission — AoU updates
> this periodically.**

[src: AOU-LD-PIPELINE.md §13.2 verbatim; verify-at-submission flag carried forward per §12 R11]

### 1.15 Data Availability Statement

> Aggregate linkage-disequilibrium matrices derived from All of Us data
> will be deposited in Zenodo at publication, after All of Us review and
> approval, under a DOI captured at deposit time. The matrices are also
> the subject of a separate *Scientific Data* data-descriptor publication
> (P&P registration Block 2 of this record). Individual-level All of Us
> data are not publicly available; qualified researchers may apply for
> controlled-tier access at researchallofus.org.

[src: AOU-LD-PIPELINE.md §13.4 (extended to cite Sci Data data descriptor per DEC-2026-04-28-01); AOU-WORKBENCH-REGISTRATION.md §11 Expected Publications]

### 1.16 Cell Suppression / Egress Statement

> No cell counts below 20 are emitted in any aggregate output. Only
> summary-level (variant × variant) LD matrices and summary statistics
> tables are exported from the Researcher Workbench. No individual-level
> genotypes, phenotypes, or identifiers leave the workbench.

[src: AOU-WORKBENCH-REGISTRATION.md §6 Data Use & Egress Plan (mirrors OSF amendment paragraph (f) verbatim); AOU-LD-PIPELINE.md §2.1 anticipated outcomes]

### 1.17 OSF Pre-Registration Cross-Reference

| Record | OSF ID | DOI | Role |
|---|---|---|---|
| Root pre-registration | `osf.io/pvb5j` | `10.17605/OSF.IO/PVB5J` | Original Track B pre-registration |
| Amendment record | `osf.io/az52u` | (linked from root) | 2026-04-22 genome-wide reframe + 2026-04-25 M1 supplementary upload |

[src: PROJECT.md "Open human-action items" (a); both render in the AoU portal per Carter 2026-04-28]

### 1.18 Submission Readiness Checklist (Track B)

- [ ] Workspace registered + DUS approved + RPS finalized (per AOU-WORKBENCH-REGISTRATION.md).
- [ ] AoU CDR release version locked in workspace metadata (Section 1.6).
- [ ] OSF amendment record (`osf.io/az52u`) reflects the analyses in this manuscript.
- [ ] ORCID populated (Section 1.2).
- [ ] AoU citation language verified ≤ 1 week before submission (Section 1.13; per §12 R11).
- [ ] AoU acknowledgment text re-verified at AoU policy page (Section 1.14).
- [ ] Zenodo DOI captured for the LD matrix deposit (Section 1.15).
- [ ] *Scientific Data* data-descriptor P&P registration (Block 2) filed and updated to cross-reference this record.

---

## Block 2 — M3 → *Scientific Data* (data descriptor)

### 2.1 Publication Title (working)

> Ancestry-matched linkage-disequilibrium reference panels for African and
> European ancestries from All of Us whole-genome sequencing.

[src: AOU-LD-PIPELINE.md §1 introduction; PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §5; AOU-WORKBENCH-REGISTRATION.md §11 (Sci Data committed per DEC-2026-04-28-01)]

### 2.2 Authors

| Role | Name | Affiliation | ORCID |
|---|---|---|---|
| First / Corresponding | Carter K. Clinton | ASHES Lab, North Carolina State University | TODO — Carter to fill |

[src: PROJECT.md "Who" §]

### 2.3 Anticipated Journal / Venue

> ***Scientific Data*** (committed venue per DEC-2026-04-28-01).

[src: DECISIONS.md DEC-2026-04-28-01; AOU-WORKBENCH-REGISTRATION.md §11 Expected Publications (committed venue)]

### 2.4 Anticipated Submission Date

> Submitted concurrent with or shortly after the Track B *Nature Genetics*
> submission per Amendment §11 (2027-04 / 2027-05). Sequencing the data
> descriptor with the discovery paper allows the Track B manuscript to cite
> the data descriptor at submission.

[src: PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §11; AOU-WORKBENCH-REGISTRATION.md §11]

### 2.5 Workspace(s) Used

> Same workspace as Block 1 (Track B). The data descriptor reports the
> exact pipeline used to generate the LD matrices that Track B consumes.

[src: AOU-WORKBENCH-REGISTRATION.md §1; AOU-LD-PIPELINE.md §2 P1–P3]

### 2.6 AoU CDR Release Version

> **TODO — lock at workspace setup; will match Block 1 because the LD
> matrices in the data descriptor are the same matrices used by Track B.**

[src: AOU-LD-PIPELINE.md §13.1]

### 2.7 AoU Data Tier

> **Controlled Tier.**

[src: AOU-LD-PIPELINE.md §1 introduction]

### 2.8 Plain-Language Lay Summary

> Modern statistical fine-mapping of genetic variants for diseases like
> hypertension, diabetes, and chronic kidney disease requires a "reference
> panel" — a database of how variants are inherited together within a
> population. The reference panels currently available for populations of
> African ancestry are based on only a few hundred individuals (1000
> Genomes Project, n = 661), which is too small for current methods to
> resolve causal variants reliably. This data descriptor publishes new
> ancestry-matched reference panels built from approximately 60,000 to
> 95,000 All of Us participants of African ancestry, plus a parallel
> European-ancestry panel for sensitivity comparison. Other researchers
> can use these panels (deposited at Zenodo) for their own fine-mapping
> studies. Only summary (variant × variant) statistics are released; no
> individual-level data leaves the All of Us Researcher Workbench.

[src: AOU-LD-PIPELINE.md §2.1 RPS template + §13.4 data availability]

### 2.9 Methods Summary

> Same methods as Block 1 §1.9 (cohort definition, QC, LD matrix
> computation in Hail). The data descriptor adds a comprehensive
> validation memo (per AOU-LD-PIPELINE.md §9 Checks 1–4): comparison
> against 1000G EUR for the EUR panel (sanity check), AFR LD decay
> structure relative to 1000G AFR (decay-matched but higher-resolution),
> per-region matrix rank diagnostics, and HLA / 8p23 inversion stress
> tests. The descriptor reports cohort N, per-chromosome variant counts,
> region-level matrix metadata (region ID, chr, start, end, n_variants,
> n_samples, MAF cutoff applied), and integrity checksums (SHA-256) for
> every deposited file.

[src: AOU-LD-PIPELINE.md §9 four-check validation; AOU-LD-PIPELINE.md §13.1 Methods paragraph; AOU-WORKBENCH-REGISTRATION.md §4 Methods Inventory]

### 2.10 Anticipated Findings

> The data descriptor is a methods + resource publication; "findings" are
> the released artifacts and their validation metrics rather than discovery
> claims.

> **Resource artifacts:** ~1500–3000 region-level LD matrices per panel
> (AFR primary; EUR sensitivity). Aggregate file size, per-region cohort
> N, MAF distribution, and validation checks are tabulated in the data
> descriptor's resource table.

> **Validation findings:** quantitative metrics from §9 Checks 1–4
> (1000G EUR concordance, AFR LD decay structure, matrix rank diagnostics,
> HLA / 8p23 stress test outcomes). Reported as descriptive metrics, not
> as inferential claims.

[src: AOU-LD-PIPELINE.md §9; AOU-WORKBENCH-REGISTRATION.md §7 (this Block's analogue is the resource-deposit framing, not the discovery-class framing)]

### 2.11 Demographics / Ancestry Usage

> Same as Block 1 §1.11. PCA-based `ancestry_pred` only; no self-reported
> race or ethnicity used for cohort definition or analytic stratification.

[src: AOU-LD-PIPELINE.md §3.1; AOU-WORKBENCH-REGISTRATION.md §10]

### 2.12 Race / Ethnicity Reporting Plan

> The data descriptor reports cohort sizes by PCA-based ancestry only.
> Self-reported race and ethnicity are not analytically used. The methods
> section explicitly states the PCA-based ancestry definition.

[src: AOU-WORKBENCH-REGISTRATION.md §10.1–§10.2]

### 2.13 Required AoU Citation

> The All of Us Research Program (ClinicalTrials.gov Identifier: NCT03658122).

[src: AOU-LD-PIPELINE.md §13.3 verbatim; verify ≤ 1 week before submission per §12 R11]

### 2.14 Acknowledgments Boilerplate

Same verbatim NIH/AoU acknowledgment block as Block 1 §1.14, with the
"Verify current funding acknowledgment text at submission" reminder.

[src: AOU-LD-PIPELINE.md §13.2 verbatim]

### 2.15 Data Availability Statement

> All deposited LD matrices are released under a Zenodo DOI (captured at
> deposit time) under a CC-BY-4.0 license, after All of Us review and
> approval. The deposited files comprise variant × variant correlation
> matrices and accompanying metadata tables (region ID, chr, start, end,
> n_variants, n_samples, MAF cutoff, SHA-256 integrity checksums); no
> individual-level data are deposited. The Track B *Nature Genetics*
> manuscript (P&P registration Block 1 of this record) consumes these
> matrices as the LD reference for fine-mapping and colocalization.
> Source code for the pipeline is released under MIT license at the
> project's GitHub repository at acceptance.

[src: AOU-LD-PIPELINE.md §13.4; PROJECT.md "Goals" §4 reproducible release; AOU-WORKBENCH-REGISTRATION.md §11]

### 2.16 Cell Suppression / Egress Statement

> Same as Block 1 §1.16. No cell counts below 20; only summary
> (variant × variant) LD matrices and summary metadata exported.

[src: AOU-WORKBENCH-REGISTRATION.md §6; AOU-LD-PIPELINE.md §2.1]

### 2.17 OSF Pre-Registration Cross-Reference

Same OSF cross-references as Block 1 §1.17 (`osf.io/pvb5j` root + `osf.io/az52u`
amendment record). The data descriptor is covered by the Track B
pre-registration scope as a methods deliverable.

[src: PROJECT.md "Open human-action items" (a); PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §9.1]

### 2.18 Submission Readiness Checklist (M3 Sci Data)

- [ ] All Block 1 §1.18 items satisfied (workspace, CDR lock, OSF,
      ORCID, AoU citation language, AoU acknowledgment).
- [ ] §9 Checks 1–4 validation memo committed and approved by Carter
      (per AOU-LD-PIPELINE.md §14 week 3 exit criterion).
- [ ] Per-region resource table generated (region ID, chr, start, end,
      n_variants, n_samples, MAF cutoff, SHA-256).
- [ ] Zenodo deposit completed and DOI captured (Section 2.15).
- [ ] Track B P&P registration (Block 1) cross-references this Block's
      P&P record in §1.15 / §1.18.
- [ ] *Scientific Data* venue commitment recorded in DECISIONS.md
      (DEC-2026-04-28-01) — **DONE** as part of quick-260428-ppz.

---

## Pre-paste reminders (both blocks)

1. **AoU portal field char limits vary.** Trim each pasted block to the live
   limit at paste time. The plain-language lay summary, methods summary, and
   acknowledgments are the most likely fields to require trimming.

2. **Update at every major scope change.** Per AOU-LD-PIPELINE.md §12 R6, the
   P&P record must be updated when the workspace, methods, target venue,
   author list, or anticipated findings change materially. Re-paste from this
   document and edit in place.

3. **CDR release version is locked at workspace setup, not here.** Sections
   1.6 / 2.6 carry placeholders. Update both blocks once the workspace's
   CDR lock decision is made.

4. **ORCID population gates submission, not registration.** Sections
   1.2 / 2.2 carry TODO placeholders that are acceptable for draft P&P
   registration but must be filled before any external submission. The
   same TODO is carried in the Track A submission bundle's CITATION.cff
   and is part of the final pre-submission checklist for both tracks.

5. **AoU citation + acknowledgment text is moving target.** §1.13 / §1.14
   and §2.13 / §2.14 carry verbatim text from AOU-LD-PIPELINE.md §13.2 / §13.3
   as of this document's authoring (2026-04-28). AoU updates the
   acknowledgment NIH grant numbers periodically. Re-verify the live AoU
   policy page text ≤ 1 week before each submission per §12 R11.

6. **OSF cross-link readiness.** Carter confirmed 2026-04-28 that both
   `osf.io/pvb5j` and `osf.io/az52u` render in the AoU portal. The
   amendment-record link in §1.17 / §2.17 should resolve to a live
   amendment record by the time M2 MTAG / CPASSOC discovery commits, per
   the OSF gating constraint at Amendment §9.1.

---

## Source-citation index

This document cites the following authoritative artifacts (all under
`.planning/` of the canonical repo at
`/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/`):

| Citation | File | Section(s) cited |
|---|---|---|
| PROJECT.md "Who" / "What" / "Goals" / "Open human-action items" | `.planning/PROJECT.md` | 1.1, 1.2, 2.1, 2.2, 1.17, 2.17, 2.15 |
| Genome-wide reframe amendment | `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` | 1.1, 1.3, 1.4, 1.10, 2.1, 2.4, 2.17 (§3, §5, §7.1–§7.3, §9.1, §11) |
| AoU LD pipeline plan | `.planning/amendments/AOU-LD-PIPELINE.md` | 1.6–1.9, 1.13–1.16, 2.6–2.9, 2.10, 2.13–2.16 (§1, §2 P1–P3 / P6, §2.1, §3.1, §9, §12 R6 / R11, §13.1–§13.4, §14 week 3) |
| Workspace registration (RPS) | `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` | 1.5, 1.8, 1.10–1.12, 1.15, 1.16, 1.18, 2.5, 2.10, 2.11, 2.12, 2.15, 2.16 (§1, §2, §3, §4, §6, §7, §10, §11) |
| DECISIONS — Sci Data venue | `.planning/DECISIONS.md` (DEC-2026-04-28-01) | 2.3, 2.18 |
