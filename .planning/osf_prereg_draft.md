# OSF Pre-Registration Draft — coloc_analysis

**Instructions for Carter:** This draft is written to fit the standard **OSF Preregistration** template. On osf.io, select **"OSF Preregistration"** and paste each section below into the matching form field. Section headings map 1:1 to OSF form fields.

After submission, record the DOI in `.planning/data_access.md`, e.g.:

```
**OSF pre-registration:** doi:10.17605/OSF.IO/XXXXX (submitted YYYY-MM-DD)
```

---

## 1. Title

Mechanistic resolution of pleiotropy at cardiometabolic loci: a cross-ancestry framework integrating fine-mapping, three-way QTL colocalization, bidirectional Mendelian randomization, and selection analysis across BMI, type 2 diabetes, hypertension, ischemic stroke, and asthma

---

## 2. Authors

Carter K. Clinton, Principal Investigator, ASHES Lab, Department of Biological Sciences, North Carolina State University, Raleigh, NC, USA. ORCID: 0000-0003-2669-8200.

Sole investigator at the time of pre-registration. Any collaborators added prior to manuscript submission will be disclosed via an OSF pre-registration update.

---

## 3. Description

### 3.1 Scientific background and motivation

Cardiometabolic and respiratory traits — obesity, type 2 diabetes, blood pressure, stroke risk, and asthma — frequently share GWAS-significant loci despite arising from distinct physiological systems. This genetic pleiotropy is a central observation of human complex trait genetics, but its mechanistic basis remains poorly resolved: shared loci may reflect (a) single causal variants acting through a single gene in a single tissue with effects cascading across traits, (b) single causal variants acting through different genes in different tissues, (c) distinct causal variants in tight linkage disequilibrium that merely appear to colocalize at the resolution of single-variant fine-mapping, or (d) evolutionary selection pressures shaping loci at which multiple traits are jointly under balancing or directional selection.

Distinguishing these mechanisms is a prerequisite for translating pleiotropic signals into biology. It also matters for health equity: because most large discovery GWAS are EUR-biased, our current picture of cardiometabolic pleiotropy is anchored in a single continental ancestry, and the ancestry-specific versus ancestry-shared components of pleiotropy at these loci are largely undescribed. A rigorous, cross-ancestry, mechanistically integrated analysis of pleiotropic cardiometabolic loci is therefore both a basic-science priority and a translational-equity priority.

### 3.2 Study aims

This study aims to mechanistically resolve genetic pleiotropy at approximately 50 loci shared across five cardiometabolic and respiratory traits (BMI, type 2 diabetes, hypertension, ischemic stroke, and asthma) using a pre-specified multi-method framework. The study is organized around four integrated analytical spines, each targeting a distinct mechanistic question:

**Spine A — Where and through what gene?** Cross-ancestry fine-mapping with SuSiE-RSS followed by `coloc.susie` (multi-causal-variant colocalization) and three-way QTL colocalization across eQTL, pQTL, and sQTL reference panels (GTEx v8, UKB-PPP, deCODE). Output: per-locus causal gene × tissue × cell-type assignment with explicit uncertainty.

**Spine B — In what direction?** Bidirectional Mendelian randomization across trait pairs using IVW, MR-Egger, weighted median, MR-PRESSO, MR-CAUSE, and MR-RAPS with pre-specified weak-instrument mitigation for AFR and EAS instrument sets.

**Spine C — With what ancestry structure?** Matched-N cross-ancestry concordance with 100× bootstrap resampling, LDSC cross-ancestry genetic correlation, LDSC partitioned heritability across functional annotations, and LDSC-SEG tissue-specific heritability. Cross-ancestry PRS-CSx with full calibration and clinical utility evaluation.

**Spine D — Under what selection pressure?** iHS, SDS, PBS, and XP-EHH selection scans on 1000 Genomes + HGDP reference haplotypes at surviving loci, polygenic selection tests under the Berg & Coop framework, and cell-type-resolved regulatory annotation via single-cell eQTL, Roadmap/EpiMap chromatin states, and ABC enhancer-gene models.

A fifth analytical layer — deep-learning variant effect prediction (Enformer, Borzoi, Sei, AlphaMissense) with overlap against public MPRA datasets — provides a computational complement to experimental functional evidence.

### 3.3 Research questions

The study addresses ten pre-specified research questions, grouped into three tiers that correspond to the analytical spines and are gated on pre-specified checkpoint decisions (see §6 Study Design and §13.1 Pre-registered failure modes). All hypotheses are listed together in §3.4. The tiering is a project-structure device, not a hypothesis-priority device — all ten questions are scientifically motivated a priori.

**Tier 1 questions (Spine A + initial Spine C):**

1. Of the approximately 50 cardiometabolic pleiotropic loci under study, how many and which support a causal gene and tissue assignment under a pre-specified PP.H4 threshold sweep (0.5, 0.7, 0.8, 0.9) in `coloc.susie` and three-way QTL colocalization across GTEx v8 (eQTL/sQTL), UKB-PPP (pQTL), and deCODE (pQTL)?

2. At loci with a supported causal gene assignment, which pathways are over-represented relative to per-trait discoverability-matched null backgrounds (MAGMA, g:Profiler), and which functional annotations and tissues contribute disproportionately to the traits' heritability (LDSC partitioned heritability, LDSC-SEG)?

3. Do signals with a supported causal gene assignment replicate in independent cohorts drawn from FinnGen R12, GBMI, MVP dbGaP phs001672, All of Us (Controlled Tier), BBJ PheWeb-JP, and Pan-UKBB?

**Tier 2 questions (Spine B + remaining Spine C):**

4. Which trait pairs show evidence of directed causal relationships under three-method Mendelian randomization agreement (IVW, MR-Egger, weighted median) with robust outlier diagnostics (MR-PRESSO, MR-CAUSE) and weak-instrument mitigation (MR-RAPS) for AFR and EAS?

5. What is the true cross-ancestry concordance of causal signals at these loci after power-matching EUR discovery cohorts to AFR sample sizes via 100× bootstrap resampling, benchmarked against LDSC cross-ancestry genetic correlation?

6. What are the discrimination (R², AUC, incremental C-statistic), calibration (Hosmer-Lemeshow test, calibration slope and intercept, observed-vs-expected plots), and clinical utility (NRI, decision-curve net benefit) properties of cross-ancestry PRS-CSx transfer from EUR discovery to AFR, EAS, and Hispanic validation cohorts — and what is the quantified trade-off between accuracy and equity across these transfers?

**Tier 3 questions (Spine D + deep-learning layer):**

7. At loci with supported causal gene assignments, is there locus-level and/or polygenic evidence of recent positive or balancing selection in AFR, EUR, or EAS ancestries (iHS, SDS, PBS, XP-EHH, Berg & Coop polygenic selection)?

8. What fraction of credible-set variants at these loci show regulatory activity predicted by deep-learning sequence models (Enformer, Borzoi, Sei), and how does this overlap with experimental MPRA readout from Abell 2022, Tewhey 2016, and comparable published datasets?

9. Which cell types and chromatin states at these loci are implicated by single-cell eQTL data (OneK1K, CLUES where available), Roadmap/EpiMap enhancer/promoter annotations, and ABC enhancer-gene linking?

10. Integrating signals across Spines A–D and the deep-learning layer, what is the composite mechanistic profile of each locus — expressed as a transparent, sensitivity-swept combination of evidence across colocalization posteriors, pathway membership, regulatory activity, and selection signatures — and how does this profile stratify the ~50 loci into distinct mechanistic classes?

### 3.4 Hypotheses

Hypotheses are stated as positive scientific predictions, each tied to specific pre-registered inference criteria (§12.3) and pre-registered failure modes (§13.1).

**Tier 1 — Colocalization and causal gene assignment (confirmatory).**

- **H1 (causal gene assignment).** At least one-quarter of the approximately 50 pleiotropic cardiometabolic loci will receive a plausible causal gene assignment at Tier A confidence (PP.H4 ≥ 0.9 robust across all four thresholds in the sweep, with ≥ 2 of 3 QTL sources — eQTL, pQTL, sQTL — supporting the same gene at PP.H4 ≥ 0.7). We commit in advance to reporting the full denominator (number of loci tested) and the full numerator (number with Tier A assignment) regardless of outcome.

- **H2 (tissue heterogeneity).** Conditional on H1, causal tissue assignments at Tier A loci will be heterogeneous rather than concentrated in a single tissue: no single tissue will account for more than 40% of Tier A gene-tissue pairs across the five traits. A concentrated tissue distribution would be a positive finding about shared physiology and is explicitly *not* predicted here.

- **H3 (pathway structure).** Pathways implicated by the Tier A gene set will include at least one immunometabolic pathway (e.g., IL-6 / JAK-STAT, complement, or TNF signaling), at least one insulin/glucose-signaling pathway (e.g., INSR/IRS1, PI3K-AKT), and at least one adipocyte-development pathway (e.g., PPARG, BMP) at a per-database FDR of q < 0.05 with discoverability-matched backgrounds.

- **H4 (negative control, kill switch).** HLA genes, pigmentation genes (OCA2, SLC24A5, MC1R), and eye-color genes will *not* colocalize with any of the five cardiometabolic traits at Tier A, and will *not* be enriched in any pathway analysis (q > 0.05 for all three sets). A non-null negative control is a pre-registered pipeline failure that blocks manuscript submission (§13.1).

- **H5 (replication).** At least half of Tier A signals will replicate at nominal P < 0.05 with concordant effect direction in at least one independent cohort. We commit to reporting the full set of lookup results (replicated, non-replicated, and cohort-missing) as a supplementary table regardless of outcome.

**Tier 2 — Causal direction, cross-ancestry concordance, PRS (confirmatory, gated on CP#1).**

- **H6 (directional MR).** At least one cardiometabolic trait pair will show three-method MR agreement with F-statistic ≥ 10 and non-significant MR-PRESSO global test (P > 0.05), supporting a directed causal effect. We further predict at least one trait pair will show evidence of bidirectional causal effects.

- **H7 (matched-N concordance).** Cross-ancestry concordance under matched-N bootstrap resampling will be substantially lower than unmatched concordance, consistent with power inflation as the primary driver of apparent ancestry differences at power-limited loci. "Substantially lower" is pre-specified as ≥ 20% absolute reduction in mean concordance after matching; a smaller reduction is reported as "concordance is real, not a power artifact".

- **H8 (PRS transfer equity trade-off).** Cross-ancestry PRS-CSx transfer from EUR discovery to AFR, EAS, and Hispanic validation cohorts will produce quantifiable differences in both discrimination (AUC, R²) and calibration (slope and intercept), with at least one ancestry showing calibration slope deviation > 0.2 from unity. The study's framing treats this as a quantified equity-versus-accuracy trade-off to be measured, not as a finding to be predicted as either a "win" or a "failure". The manuscript will *not* claim "equitable polygenic risk prediction" as a positive finding and *will* report the underlying disparities regardless of their size.

**Tier 3 — Selection, deep-learning, cell-type integration (confirmatory-exploratory hybrid, gated on CP#2).**

- **H9 (locus-level selection signatures).** At least one cardiometabolic trait will show locus-level evidence of recent positive selection (iHS ≥ 2, SDS ≥ 2, or PBS ≥ 99th percentile) at ≥ 1 Tier A locus in at least one continental ancestry. A null locus-level result is a valid outcome and is reported as such.

- **H10 (polygenic selection, with pre-registered fallback framing).** Polygenic selection tests under the Berg & Coop framework will identify at least one trait with directional allele-frequency shifts consistent with polygenic adaptation. **Pre-registered fallback:** a null polygenic selection result does *not* invalidate the locus-level signatures of H9, and the evolutionary-medicine narrative in the manuscript will be reframed around locus-level selection only if the polygenic test is null. This fallback is committed in advance because polygenic selection tests are historically difficult to replicate across ancestries and reference panels, and we do not want a null polygenic result to force post-hoc reinterpretation of locus-level findings.

- **H11 (deep-learning regulatory evidence).** A substantial fraction of credible-set variants at Tier A loci (pre-specified as ≥ 20%) will show concordant regulatory activity predictions between Enformer/Borzoi tracks and public MPRA data, providing computational triangulation of regulatory mechanism. Concordance is defined as same-direction effect at FDR < 0.1 in both methods.

---

## 4. Study Type

Observational study. Secondary analysis of publicly available genome-wide association summary statistics and quantitative trait loci reference data. Phase 8 (PRS validation, Tier 2) uses individual-level genotypes inside the All of Us Researcher Workbench under the investigator's existing Controlled Tier credentials. No new primary data collection, no human subjects contact, no biological samples.

---

## 5. Blinding

Not applicable in the clinical-trials sense. However, the following methodological blinding commitments are pre-registered:

- **Analytical code is frozen at registration.** All analysis code, parameter choices, priors, and statistical thresholds are specified in this pre-registration and committed to the project repository prior to running any of the analyses listed in §12 on the primary analytical cohorts. Code commits pinning the analysis plan are tagged at pre-registration time.

- **Results are not inspected prior to registration.** The investigator has not run `coloc.susie`, three-way QTL colocalization, the pre-registered MR pipeline, matched-N bootstrap, PRS-CSx cross-ancestry transfer, selection scans, or deep-learning inference on any of the pre-registered primary analytical cohorts prior to this registration.

- **Intermediate QC is inspected but scoped.** Harmonization success rates, fine-mapping convergence status, and pipeline integrity checks are inspected during Phase 0 and Phase 1 and do not constitute primary-result inspection. A written "QC inspection log" is maintained in the project repository at `.planning/qc_inspection_log.md` and committed at the time of each inspection.

- **Negative controls are tested alongside all primary analyses.** The negative-control gene sets (HLA, pigmentation genes, eye-color genes) are pre-specified in `config/negative_controls.yaml` and run in every colocalization and enrichment analysis. A non-null negative control blocks submission (§13.1).

---

## 6. Study Design

Multi-phase analytical framework with three tiers (T1, T2, T3) and two decision gates (CP#1 between T1 and T2; CP#2 between T2 and T3). Each phase has a written success criterion that must be met before the next phase begins.

| Phase | Goal | Tier |
|---|---|---|
| 0 | Data access, infrastructure, Snakemake skeleton, CI smoke test, pre-registration (this document) | T1 prerequisite |
| 1 | SuSiE-RSS fine-mapping and `coloc.susie` colocalization | T1 |
| 2 | Three-way QTL colocalization (eQTL + pQTL + sQTL) | T1 |
| 5 | Pathway enrichment and partitioned heritability | T1 |
| 9 | Replication in independent cohorts | T1 |
| **CP#1** | **T1 → T2 gate decision** | **Gate** |
| 3 | Bidirectional Mendelian randomization | T2 (gated) |
| 4 | Matched-N cross-ancestry concordance | T2 (gated) |
| 8 | Cross-ancestry PRS-CSx with calibration and clinical utility | T2 (gated) |
| **CP#2** | **T2 → T3 gate decision** | **Gate** |
| 6 | Selection scans and polygenic selection | T3 (gated) |
| 7 | Single-cell + EpiMap + ABC enhancer-gene integration | T3 (gated) |
| 10 | Deep-learning variant effect (Enformer, Borzoi, Sei, AlphaMissense) and MPRA overlap | T3 (gated) |
| 11 | Manuscript preparation, figures, submission | parallel from Phase 9 |

**Gate criteria are pre-registered and are themselves confirmatory:**

- **CP#1 (T1 → T2).** Tier 2 is activated if and only if: (a) at least one Tier A signal survives the PP.H4 sweep with a supported causal gene assignment; (b) at least half of Tier A signals replicate in at least one independent cohort; (c) all three negative-control gene sets are null across colocalization and pathway enrichment; (d) at least one ancestry-matched analytical slice retains adequate statistical power under matched-N preview using Hou et al. 2023 effect-size framework. Failure on any of (a)–(d) stops the project at T1 and the resulting manuscript is submitted with a scope and framing commensurate with the Tier 1 findings alone.

- **CP#2 (T2 → T3).** Tier 3 is activated if and only if: (a) MR identifies at least one causally-directed trait pair with three-method agreement; (b) matched-N concordance produces an interpretable quantitative comparison to unmatched concordance; (c) PRS-CSx produces interpretable calibration and clinical utility metrics in at least three ancestries including AFR and Hispanic; (d) the investigator judges, in a written memo committed to the repository, that cumulative T1+T2 findings motivate the additional scientific risk of T3. Failure on any of (a)–(d) terminates scope at T2.

---

## 7. Randomization

Not applicable. All summary statistics are used as released by each consortium for the five traits of interest. Participant selection within each cohort follows each consortium's protocols.

---

## 8. Existing Data

**Registration timing:** *Registration prior to analysis of the data.*

**Explanation.** The analyses pre-registered here have not been conducted. Specifically, none of the following have been run on any of the pre-registered primary analytical cohorts prior to this registration: SuSiE-RSS fine-mapping with the pre-specified policy, `coloc.susie`, three-way QTL colocalization (eQTL + pQTL + sQTL), bidirectional Mendelian randomization with the pre-specified triangulation, matched-N cross-ancestry bootstrap, LDSC partitioned heritability or LDSC-SEG, PRS-CSx cross-ancestry transfer with calibration and clinical utility evaluation, iHS / SDS / PBS / XP-EHH selection scans, polygenic selection tests, Enformer / Borzoi / Sei / AlphaMissense inference, or MPRA overlap analysis.

**Prior exploratory work disclosure.** The investigator has previously conducted exploratory colocalization work using the single-causal-variant `coloc.abf` method on a subset of the trait–trait combinations at a subset of the candidate loci, restricted to publicly available EUR summary statistics and a small AFR slice. That exploratory work used different analytical methods, different cohort subsets, and a descriptive (rather than mechanistically integrated) analytical frame. It is disclosed here for full transparency and does not constitute a pre-tested version of the analyses pre-registered in this document. No quantitative results from the exploratory work are carried forward into this study.

**Data access status at registration:**

- Open-access summary statistics for seven of the primary data sources have been confirmed reachable from the investigator's HPC environment. Specifically: UKB-PPP Synapse certification is complete (verified 2026-04-10); deCODE summary data portal inventory has been verified via browser (verified 2026-04-10, ~4,907 aptamers × SomaScan v4); FinnGen R12 registration is complete with confirmed bucket URLs (registered 2026-04-10); GTEx v8 eQTL and sQTL GCS buckets are reachable; Pan-UKBB S3 bucket is reachable; BBJ PheWeb-JP hum0197-v3 is reachable; MVP dbGaP phs001672 summary statistics are accessible without a Data Access Request.
- All of Us Researcher Workbench Controlled Tier credentials are active and will be used only for Phase 8 PRS validation under NCSU's institutional data use agreement. All individual-level data remain inside the Workbench.
- UK Biobank main Data Use Agreement (individual-level) is *not* held and is *not* required for any pre-registered analysis.

---

## 9. Data Collection Procedures

No primary data collection. All data are pre-existing publicly available summary statistics or, for Phase 8 PRS validation, individual-level genotypes within the All of Us Researcher Workbench (Controlled Tier, investigator-credentialed).

**Data sources:**

| Source | Role in study | Access model at registration |
|---|---|---|
| UKB-PPP (Sun et al. 2023) | Phase 2 pQTL colocalization | Synapse syn51364943, Certified User (verified 2026-04-10) |
| deCODE pQTL (Ferkingstad et al. 2021) | Phase 2 pQTL colocalization | decode.com/summarydata/, ephemeral download (verified 2026-04-10) |
| GTEx v8 | Phase 2 eQTL and sQTL colocalization | Open GCS bucket, no registration |
| FinnGen R12 | Phase 9 replication, Phase 3 MR | elomake.helsinki.fi click-wrap, registered 2026-04-10 |
| Pan-UKBB | Phase 3 trans-ancestry MR, Phase 9 replication | Open S3, CC-BY-4.0 |
| BBJ PheWeb-JP (Sakaue 2021, Ishigaki 2020) | Phase 3 MR, Phase 9 replication | Open NBDC hum0197-v3 |
| MVP dbGaP phs001672 | Phase 9 replication | Open dbGaP, no DAR required for summary statistics |
| All of Us Researcher Workbench (Controlled Tier) | Phase 8 PRS validation, Phase 9 replication | Credentialed |
| GBMI | Phase 9 replication | Open meta-analysis portal |
| 1000 Genomes + HGDP | LD reference, selection scans (Phase 6, T3) | Open |
| Roadmap / EpiMap / ABC | Phase 7 regulatory integration (T3) | Open |
| Published MPRA (Abell 2022, Tewhey 2016) | Phase 10 overlap (T3) | Open supplementary data |

Trait-specific GWAS sources include GIANT (BMI), DIAMANTE and Mahajan 2022 (T2D), MEGASTROKE and GIGASTROKE (ischemic stroke), Demenais 2018 and TAGC (asthma), and ancestry-expansion cohorts including Gurdasani 2019 (AFR BMI), Hoffmann (AFR hypertension), and PAGE/HCHS (Hispanic multi-trait).

---

## 10. Sample Size and Sample Size Rationale

Sample sizes are determined by the underlying GWAS and QTL releases and are not subject to investigator adjustment.

**Representative ancestry-stratified sample sizes** (approximate, as of release versions cited):

- **BMI.** GIANT (EUR ~700,000), Pan-UKBB (AFR ~6,000, EAS ~2,000, AMR/Hispanic ~1,000), BBJ (EAS ~160,000), Gurdasani 2019 (AFR ~14,000).
- **Type 2 diabetes.** DIAMANTE (EUR ~900,000), Mahajan 2022 multi-ancestry (AFR, EAS, SAS, Hispanic), BBJ (EAS ~210,000), MVP (EUR, AFR, Hispanic).
- **Hypertension.** Pan-UKBB (all six ancestries), BBJ (EAS), Hoffmann (AFR).
- **Ischemic stroke.** MEGASTROKE (EUR ~520,000), Pan-UKBB, BBJ, GIGASTROKE multi-ancestry 2022.
- **Asthma.** Demenais 2018 (EUR ~135,000), TAGC multi-ancestry, Pan-UKBB, BBJ.

**QTL reference sample sizes.** GTEx v8 (EUR, ~700 donors across ~50 tissues); UKB-PPP (~54,000 UK Biobank participants, ~2,900 Olink proteins); deCODE (~36,000 Icelanders, ~5,000 SomaScan aptamers).

**Power considerations.** The study explicitly does not attempt to remediate under-powered ancestry slices. Power diagnostics (F-statistic, I², Q-statistic for MR; effective sample size per ancestry for colocalization; per-ancestry LD matrix conditioning diagnostics for fine-mapping) are reported per trait per ancestry in supplementary tables. "Insufficient power" is a pre-registered valid outcome for any ancestry-specific analysis; no post-hoc ancestry exclusions will be made on the basis of power alone.

**Stopping rule.** Not applicable (no participant enrollment). Project scope is governed by the pre-registered checkpoint gates (§6).

---

## 11. Variables

### 11.1 Manipulated variables

None. This is an observational secondary analysis.

### 11.2 Measured variables

**Tier 1 primary variables:**

1. **Colocalization posteriors** (PP.H0, PP.H1, PP.H2, PP.H3, PP.H4) from `coloc.susie` for every trait pair × ancestry × locus combination, with four PP.H4 thresholds {0.5, 0.7, 0.8, 0.9} used for tier assignment.

2. **Credible set properties** from SuSiE-RSS per trait × ancestry × locus: credible set size, min_abs_corr, convergence status, L value (baseline and fallback), and locus-level identifiability diagnostic.

3. **QTL coloc tier per gene per tissue per cell type** from three-way (eQTL, pQTL, sQTL) colocalization, expressed as a gene × tissue × trait matrix.

4. **Pathway enrichment q-values** from MAGMA, g:Profiler (with discoverability-matched per-trait backgrounds), and LDSC partitioned heritability across the Finucane 2015 baseline and pathway-stratified annotations.

5. **Replication statistics** per Tier A signal: lookup P-value, beta direction, and proxy variant used if the sentinel is missing.

**Tier 2 primary variables (gated):**

6. **MR causal estimates** per trait pair per ancestry, across IVW, MR-Egger, weighted median, MR-PRESSO, MR-CAUSE, and MR-RAPS.

7. **Weak-instrument diagnostics** (F-statistic, I², Q-statistic) per ancestry per trait pair.

8. **Matched-N bootstrap concordance** (100 iterations) between EUR and AFR for each trait, with mean and 95% CI.

9. **LDSC cross-ancestry genetic correlation** (r_g) per trait pair of ancestries.

10. **PRS metrics per ancestry.** Discrimination: R² on the liability scale, AUC, incremental C-statistic versus clinical baseline. Calibration: Hosmer-Lemeshow test, calibration slope, calibration intercept, observed-vs-expected deciles. Clinical utility: NRI at pre-specified risk threshold, decision-curve analysis, net benefit versus "treat all" and "treat none".

**Tier 3 primary variables (gated):**

11. **Selection scan statistics.** iHS, SDS, PBS, XP-EHH at surviving Tier A loci per continental ancestry.

12. **Polygenic selection test statistics** under Berg & Coop 2014 and sBayesS frameworks.

13. **Deep-learning variant effect scores.** Enformer track predictions, Borzoi predictions, Sei regulatory activity scores, AlphaMissense scores for coding variants.

14. **MPRA overlap classifications** per credible-set variant at Tier A loci.

### 11.3 Indices

A **composite mechanistic profile** per locus (Phase 10 and Phase 11) is constructed by transparent combination of Spine A–D evidence. The composite is reported as a **sensitivity sweep** across plausible weightings rather than a single combined score, because the field lacks consensus on relative weights for these evidence classes. The sensitivity sweep is pre-specified (§12.1); the choice to report a sweep rather than a single number is pre-registered.

---

## 12. Analysis Plan

### 12.1 Statistical models

**Fine-mapping (Phase 1).** SuSiE-RSS with baseline L = 10 and min_abs_corr = 0.5. Pre-registered sensitivity sweep: min_abs_corr ∈ {0.1, 0.5, 0.9} for all regions flagged as "complex" per a pre-specified complexity rule (≥ 3 credible sets at L = 10 or max credible-set size > 50). Convergence failure policy committed in `config/susie_policy.yaml`: regions failing to converge at L = 10 are re-run at L = 5, then L = 3; regions failing all three are reported as "unresolved" in the supplementary table and excluded from downstream colocalization.

**Colocalization (Phases 1 and 2).** `coloc.susie` with default priors (p1 = p2 = 1e−4, p12 = 1e−5). PP.H4 threshold sweep {0.5, 0.7, 0.8, 0.9}. Tier assignment: **Tier A** = PP.H4 ≥ 0.9 across all four thresholds; **Tier B** = PP.H4 ≥ 0.7 at ≥ 3 of 4 thresholds; **Tier C** = PP.H4 ≥ 0.5 at ≥ 2 of 4 thresholds.

**QTL integration (Phase 2).** Three-way colocalization across GTEx v8 eQTL per tissue, GTEx v8 sQTL per tissue, UKB-PPP pQTL, and deCODE pQTL. Genes are prioritized when two or more of the three QTL modalities support the same gene at PP.H4 ≥ 0.7, with cross-referencing to Open Targets Locus2Gene as an external independent prioritization layer. Negative-control gene sets are tested in the same pipeline.

**Pathway enrichment (Phase 5).** MAGMA gene-based and gene-set enrichment with ancestry-matched LD panels (1000G EUR, AFR, EAS as available). g:Profiler with per-trait discoverability-matched background (gene universe restricted to genes with ≥ 1 SNP genome-wide-significant at P < 5e−8 in the trait's discovery GWAS). LDSC partitioned heritability across the Finucane 2015 baseline annotations plus pathway-stratified annotations. LDSC-SEG for tissue-specific heritability. Permutation null (N = 1000) for colocalization gene lists tested against pathway databases.

**Replication (Phase 9).** Sentinel-variant lookup in FinnGen R12, GBMI, MVP phs001672, BBJ, All of Us (via summary statistics exported from the Workbench), and Pan-UKBB (where not already used in discovery). Replication call: nominal P < 0.05 with concordant effect direction at the locus-level sentinel variant, or at a proxy variant with r² > 0.8 in the relevant ancestry if the sentinel is missing.

**Mendelian randomization (Phase 3, T2, gated).** Triangulation across IVW, MR-Egger, and weighted median as the three primary estimators. MR-PRESSO for outlier detection and global pleiotropy testing. MR-CAUSE for confounded-pleiotropy robustness. MR-RAPS for weak-instrument mitigation in AFR and EAS. Instrument choice (ancestry-specific vs. trans-ancestry) is made per trait pair with pre-registered criteria: ancestry-specific instruments when F-statistic ≥ 10 in the ancestry-specific instrument set, trans-ancestry instruments when F-statistic < 10 per ancestry.

**Matched-N concordance (Phase 4, T2, gated).** 100× bootstrap resampling of EUR down to AFR sample size, re-running `coloc.susie` on each bootstrap. Reported as mean and 95% CI for cross-ancestry concordance. LDSC cross-ancestry r_g is reported as a complementary global benchmark.

**PRS (Phase 8, T2, gated).** PRS-CSx trained on EUR discovery summary statistics with AFR, EAS, and Hispanic transfer. Discrimination, calibration, and clinical utility metrics as listed in §11.2 #10. Pathway-restricted PRS (using the Tier A pathway set from Phase 5) is compared to genome-wide PRS per ancestry.

**Selection scans (Phase 6, T3, gated).** iHS and XP-EHH via selscan 2.0 on phased 1000 Genomes + HGDP haplotypes. SDS via the standard sds-wrapper pipeline. PBS (Yi et al. 2010) on 1000 Genomes super-populations. Polygenic selection via the Berg & Coop 2014 framework and sBayesS.

### 12.2 Transformations

- **Summary statistics harmonization.** Effect allele alignment to the hg38 reference, liftover from hg19 where needed via CrossMap, effect direction alignment, exclusion of strand-ambiguous SNPs (A/T and C/G) with MAF > 0.4, minor allele frequency filter ≥ 0.01.
- **deCODE pQTL Beta.** Already reported in standard-deviation units per the deCODE README; no additional transformation applied.
- **PRS liability scale.** Transformation from observed scale via population prevalence estimates from each trait's source cohort and Lee 2011 liability-scale correction.

### 12.3 Inference criteria

- **Phase 1 (fine-mapping).** Primary credible set per region is the SuSiE credible set with minimum size and maximum min_abs_corr at baseline L = 10.
- **Phase 2 (colocalization).** Primary tier is Tier A as defined in §12.1. Full threshold sweep is reported in supplementary tables.
- **Phase 3 (MR, gated).** Causal claim requires three-method agreement (IVW, MR-Egger, weighted median all at P < 0.05 with concordant effect direction), non-significant MR-PRESSO global test (P > 0.05), and F-statistic ≥ 10 for the instrument set.
- **Phase 5 (pathway enrichment).** Pathway claim requires q < 0.05 after Benjamini-Hochberg correction within each pathway database, and null results for all three negative-control pathway sets.
- **Phase 9 (replication).** Replication claim requires P < 0.05 with concordant effect direction at the sentinel variant (or proxy) in ≥ 1 independent cohort.

### 12.4 Data exclusion

- **Locus-level exclusions.** Complex regions with SuSiE convergence failure at L = 3 are excluded from primary colocalization and reported as "unresolved" in a supplementary table.
- **Variant-level exclusions.** Strand-ambiguous SNPs (A/T, C/G) with MAF > 0.4 are excluded from all analyses.
- **Pre-registered low-power exclusion.** Any candidate pleiotropic signal with fewer than 50 SNPs in the relevant locus window in the relevant ancestry is excluded from primary analysis. This threshold is set a priori based on fine-mapping literature (SuSiE-RSS requires adequate LD matrix conditioning at the regional scale).
- **Trait-level exclusions.** None at pre-registration. If a trait fails to harmonize across all five ancestries, it is reported as excluded in a supplementary note with the harmonization failure mode documented.

### 12.5 Missing data

- **Cross-cohort missingness.** Sentinel variants missing from a replication cohort are proxied by the highest-r² variant in the relevant ancestry (r² > 0.8 required). Proxy substitution is reported per Tier A signal.
- **Ancestry missingness.** Traits without AFR or EAS summary statistics are marked "EUR-only" and excluded from matched-N analyses (Phase 4, T2).
- **QTL missingness.** Genes with no GTEx v8 eQTL signal (low-expression tissues, expression-filtered genes) are reported as "no eQTL evidence" and do not contribute to three-way QTL scoring at the affected tissues.

### 12.6 Exploratory analyses

The following are explicitly exploratory and will be labeled as such in the manuscript:

- Single-cell eQTL integration (OneK1K, CLUES) if data coverage is sufficient at Phase 2 execution time.
- Additional pQTL cohorts beyond UKB-PPP and deCODE (e.g., ARIC, INTERVAL) if harmonization effort is tractable.
- Sex-stratified and age-stratified subgroup analyses (not planned at pre-registration; added only if reviewer-requested).
- Pathway-restricted PRS alternatives beyond the Tier A pathway set.

---

## 13. Other

### 13.1 Pre-registered failure modes

The following outcomes trigger pre-specified responses without post-hoc reinterpretation:

1. **Negative control non-null.** Any of the three negative-control gene sets (HLA, pigmentation, eye-color) showing Tier A colocalization or q < 0.05 enrichment is a pipeline failure. The manuscript is not submitted until the source of the false positive is identified, fixed, and re-verified.

2. **Zero Tier A signals after Phase 2.** CP#1 fails; T2 and T3 are not activated. The manuscript is framed around negative findings with explicit power and method diagnostics.

3. **Replication failure (< 50% of Tier A signals replicate in ≥ 1 cohort).** CP#1 fails; T2 and T3 are not activated. Replication failure is discussed as a primary finding.

4. **MR identifies no causally-directed trait pairs.** CP#2 fails; T3 is not activated. The MR result is reported as null, not reframed.

5. **PRS transfer produces uninterpretable calibration.** CP#2 fails; T3 is not activated. The PRS result is reported with the equity-vs-accuracy trade-off framed regardless of absolute performance.

6. **Polygenic selection is null (T3).** Pre-registered fallback in §3.4 H10 activates: single-locus selection signatures become the primary selection finding.

### 13.2 Deviation policy

Deviations from this pre-registration are disclosed in the Methods section of the resulting manuscript under a subsection titled "Deviations from pre-registration" with per-deviation rationale. Deviations made after looking at primary results are flagged as post-hoc. A deviation log is maintained in the project repository at `.planning/osf_deviations.md` with date-stamped entries and is included as supplementary material.

### 13.3 Timeline

Not pre-registered as a constraint. Rigor is prioritized over speed.

### 13.4 Code and reproducibility

- **Repository.** `github.com/[insert username]/coloc_analysis` (made public on first submission).
- **Pipeline.** Snakemake 7.32.4 orchestrates all analyses. All conda environments are pinned to exact package versions in `envs/*.yml`.
- **Containers.** Docker and Singularity images are built per phase and published on Zenodo with DOIs on first manuscript submission.
- **Continuous integration.** Nightly 3-locus toy smoke test runs via LSF cron on the NCSU HPC through Phase 0; migrates to GitHub Actions on public release.
- **Harmonization.** All harmonization, liftover, and QC scripts are tracked in `src/python/` and `src/R/` and are the only permitted transformations between raw downloads and analytical inputs.
- **Data provenance.** All data source URLs, access models, download dates, file checksums, and version strings are tracked in `.planning/data_access.md` with per-source verification dates.

### 13.5 Ethical considerations

No human subjects contact, no wet-lab work, no biological samples. Individual-level data usage is restricted to the All of Us Researcher Workbench under the investigator's existing Controlled Tier credentials and NCSU's institutional data use agreement; no individual-level data leave the Workbench. No identifiable data are handled outside the Workbench. All summary statistics sources are publicly licensed or accessed under standard academic credentials as documented in §9.

### 13.6 Conflicts of interest

None.

### 13.7 Funding

*[Insert funding statement. If no external funding for this specific work, state: "This work was conducted with internal NCSU ASHES Lab resources and has no external funding for the pre-registered analyses."]*

### 13.8 Target journals

Primary: Nature Genetics. Secondary (conditional on scope): American Journal of Human Genetics, Nature Metabolism, Cell Genomics, Genome Medicine. Target journal choice depends on cumulative scope at submission time and is documented per-version in `manuscript/cover_letter/`.

---

## End of pre-registration draft

**Pre-submission checklist:**

- [ ] Fill in `[insert ORCID iD]` in §2.
- [ ] Fill in `[insert username]` in §13.4 or leave as placeholder if the repository is not yet public.
- [ ] Fill in §13.7 funding statement.
- [ ] Log in at https://osf.io and create a new OSF project titled "Mechanistic resolution of pleiotropy at cardiometabolic loci" (or your preferred title).
- [ ] From the project, create a pre-registration and select the **"OSF Preregistration"** template.
- [ ] Paste each section above into the matching OSF form field. Section numbers map 1:1 to the OSF template.
- [ ] Attach the following planning artifacts as supporting files so reviewers can see the full analytical framework: `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `DECISIONS.md`, `data_access.md`.
- [ ] Submit. OSF mints a DOI immediately.
- [ ] Record the DOI in `.planning/data_access.md` at the top of the file.
- [ ] Commit the DOI update and either archive or delete this draft file.
