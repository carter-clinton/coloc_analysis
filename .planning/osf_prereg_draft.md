# OSF Pre-Registration Draft — coloc_analysis revision

**Instructions for Carter:** This draft is written to fit the standard **OSF Preregistration** template (the general one, not AsPredicted and not a domain-specific template). When you create the pre-registration on osf.io, select **"OSF Preregistration"** and paste each section below into the matching form field. Section headings map 1:1 to OSF form fields.

After submission, record the DOI (OSF assigns one automatically upon submission) in `.planning/data_access.md` at the top of the file under "Last verified", e.g.:

```
**OSF pre-registration:** doi:10.17605/OSF.IO/XXXXX (submitted YYYY-MM-DD)
```

---

## 1. Title

Cross-ancestry colocalization, bidirectional Mendelian randomization, and selection analysis of five cardiometabolic traits at pleiotropic loci: a multi-method framework with pre-specified tiered analyses

---

## 2. Authors

Carter K. Clinton, Assistant Professor / Principal Investigator, ASHES Lab, Department of Biological Sciences, North Carolina State University, Raleigh, NC, USA. ORCID: *[insert ORCID iD]*.

**Note on authorship:** Sole investigator for this pre-registration. No co-authors at pre-registration time. Collaborators added to any resulting manuscript will be disclosed on OSF via a pre-registration update before manuscript submission.

---

## 3. Description

### Background

Existing cross-ancestry colocalization studies of cardiometabolic traits rely on single-causal-variant assumptions (`coloc.abf`), EUR-heavy discovery cohorts, and ad-hoc pathway enrichment without formal statistical tests. A prior draft manuscript by the investigator (internal version `ajhg_manu_v10.pdf`) applied `coloc.abf` to BMI, type 2 diabetes (T2D), hypertension, ischemic stroke, and asthma at ~50 pleiotropic loci with a small AFR fragment. Self-review and independent reviews identified eight methodological weaknesses: (1) single-causal-variant assumption, (2) ad-hoc pathway enrichment without formal testing, (3) cross-ancestry concordance mixing incomparable trait pairs at the same locus, (4) corrupted supplementary tables with inconsistent signal counts, (5) absence of replication in independent cohorts, (6) no causal direction testing (Mendelian randomization), (7) no formal selection-scan test of evolutionary medicine hypotheses, and (8) a hand-weighted ML scorecard with no train/test split.

This revision reframes the study from a descriptive pleiotropy catalog into a mechanistically resolved cross-ancestry framework with three integrated analytical spines: (A) `coloc.susie` + three-way QTL colocalization → causal gene and tissue assignment; (B) bidirectional Mendelian randomization → causal direction; (C) matched-N cross-ancestry + LDSC partitioned heritability + selection scans → evolutionary and equity analysis.

### Research Questions

1. **Colocalization.** After replacing `coloc.abf` with `coloc.susie` (allowing multiple causal variants per region) and applying an explicit policy for complex regions (convergence failures, `L` cap, `min_abs_corr` sensitivity), how many and which of the previously identified pleiotropic signals at the ~50 cardiometabolic loci survive as Tier A / B / C evidence across a pre-specified PP.H4 threshold sweep (0.5, 0.7, 0.8, 0.9)?

2. **Causal gene and tissue assignment.** Integrating three-way QTL colocalization (eQTL, pQTL, sQTL) from GTEx v8, UKB-PPP, and deCODE, which causal genes and tissues are implicated at the surviving loci? Are negative-control gene sets (HLA, pigmentation, eye-color) null as expected?

3. **Pathway enrichment.** Using MAGMA, g:Profiler with discoverability-matched backgrounds, LDSC partitioned heritability, and LDSC-SEG tissue-specific heritability, which pathways and tissues are enriched for the five cardiometabolic traits? Do negative-control pathway sets remain null?

4. **Replication.** Do the surviving Tier A signals replicate in at least two independent cohorts (selected from FinnGen R12, GBMI, MVP dbGaP phs001672, All of Us Controlled Tier, BBJ PheWeb-JP)?

5. **(T2, conditional on Checkpoint #1)** Causal direction via bidirectional Mendelian randomization with weak-instrument mitigation (MR-RAPS, IVW-with-correction) for AFR and EAS.

6. **(T2, conditional on Checkpoint #1)** Matched-N cross-ancestry concordance replacing the prior Table 2 with power-corrected bootstrap comparisons and an LDSC cross-ancestry genetic correlation benchmark.

7. **(T2, conditional on Checkpoint #1)** Cross-ancestry polygenic risk scores via PRS-CSx with calibration (Hosmer-Lemeshow, slope, intercept) and clinical utility (NRI, decision-curve analysis) metrics, and quantification of the equity-vs-accuracy trade-off.

8. **(T3, conditional on Checkpoint #2)** Formal selection scans (iHS, SDS, PBS, XP-EHH) and polygenic selection tests of the evolutionary-medicine hypothesis, with a pre-specified fallback framing (see Analysis Plan §10.5).

9. **(T3, conditional on Checkpoint #2)** Single-cell and chromatin-state integration (single-cell eQTL, Roadmap/EpiMap, ABC enhancer-gene model, CELLECT/scDRS).

10. **(T3, conditional on Checkpoint #2)** Deep-learning variant effect prediction (Enformer, Borzoi, Sei, AlphaMissense) with overlap against public MPRA datasets (Abell 2022, Tewhey 2016).

### Hypotheses

**Primary (T1, confirmatory):**

- **H1:** Replacing `coloc.abf` with `coloc.susie` will reduce the number of signals at the highest confidence tier (PP.H4 ≥ 0.9) because the multi-causal-variant assumption disambiguates previously-collapsed credible sets. We pre-specify this as **directional but not quantitative**, because the prior draft's Tier A count is known to the investigator and the revision's Tier A count is not.

- **H2:** Three-way QTL colocalization will assign a **plausible causal gene** (defined as gene prioritized by ≥ 2 of eQTL, pQTL, sQTL coloc at PP.H4 ≥ 0.7) at a minority of surviving Tier A loci. We do **not** pre-specify a proportion, because base rates for three-way QTL concordance at this scale are not well-characterized in the literature.

- **H3 (negative control):** HLA, pigmentation, and eye-color gene sets will show PP.H4 < 0.7 at surviving loci, and will not be enriched in pathway analysis (q > 0.05). A non-null result in any of these negative controls is a pre-registered failure of the pipeline that blocks the manuscript from being submitted.

- **H4 (replication):** ≥ 50% of Tier A signals (PP.H4 ≥ 0.9) will replicate in ≥ 1 independent cohort at a nominal significance threshold (P < 0.05 with concordant effect direction). This is a weak pre-specification because cross-cohort effect-size attenuation is not well-characterized for all five traits.

**Secondary (T2, gated, confirmatory):**

- **H5:** Bidirectional MR will identify ≥ 1 trait pair with evidence of causal direction (three-method agreement across IVW, MR-Egger, weighted median, with non-significant MR-PRESSO global test) and ≥ 1 trait pair with bidirectional effects.

- **H6:** Matched-N bootstrap will reduce apparent cross-ancestry concordance compared to the unmatched baseline, quantifying the power-inflation artifact in the prior draft's Table 2.

- **H7:** PRS-CSx transfer from EUR to AFR/EAS/Hispanic will show reduced discrimination (AUC), reduced calibration (slope deviation from 1), and worse clinical utility (NRI, net benefit) compared to EUR baseline — framed as a quantified equity-vs-accuracy trade-off, **not** as an equity win.

**Tertiary (T3, gated, exploratory-confirmatory hybrid):**

- **H8:** At least one cardiometabolic trait will show locus-level evidence of recent positive selection (iHS ≥ 2, SDS ≥ 2, or PBS ≥ 99th percentile) at a surviving Tier A locus. **Fallback framing (pre-registered):** a null polygenic selection result does **not** invalidate single-locus selection signatures. If polygenic tests are null, the evolutionary-medicine narrative is reframed around single-locus signatures only.

---

## 4. Study Type

**Observational study.** Secondary analysis of publicly available summary statistics (and, for Phase 8, individual-level genotypes inside the All of Us Researcher Workbench under Controlled Tier credentials). No new data collection, no human subjects contact, no biological samples.

---

## 5. Blinding

Not applicable. This is a computational re-analysis of pre-existing summary statistics. However:

- **Methodological blinding commitment:** All analysis code, parameter choices, and statistical thresholds are specified in this pre-registration **before** any coloc.susie or MR runs on the new cohort data. The investigator will not inspect PP.H4 values, MR P-values, or selection-scan statistics prior to fixing the analysis plan. Intermediate QC outputs (harmonization success rate, fine-mapping convergence) will be inspected, but primary results will not be unblinded until all code is pinned and the analysis plan is registered.

- **Negative-control blinding:** The negative-control gene sets (HLA, pigmentation, eye-color) are pre-specified in `config/negative_controls.yaml` and will be tested alongside all primary analyses. A non-null negative control blocks submission.

---

## 6. Study Design

Multi-stage tiered framework with three decision gates (Checkpoint #0 = this pre-registration; Checkpoint #1 = T1 → T2 gate; Checkpoint #2 = T2 → T3 gate). Each phase has a written success criterion that must be met before the next phase begins.

| Phase | Goal | Tier |
|---|---|---|
| 0 | Data access, infrastructure, Snakemake skeleton, CI smoke test, this pre-registration | T1 (prerequisite) |
| 1 | SuSiE-RSS + coloc.susie fine-mapping (replaces coloc.abf) | T1 |
| 2 | Three-way QTL colocalization (eQTL + pQTL + sQTL) | T1 |
| 5 | Pathway enrichment (MAGMA, g:Profiler, LDSC partitioned h², LDSC-SEG) | T1 |
| 9 | Replication in independent cohorts | T1 |
| **CP#1** | **T1 → T2 gate decision** | **Gate** |
| 3 | Bidirectional Mendelian randomization | T2 (gated) |
| 4 | Matched-N cross-ancestry concordance (replaces Table 2) | T2 (gated) |
| 8 | Cross-ancestry PRS-CSx with calibration and clinical utility | T2 (gated) |
| **CP#2** | **T2 → T3 gate decision** | **Gate** |
| 6 | Selection scans (iHS, SDS, PBS, XP-EHH) and polygenic selection | T3 (gated) |
| 7 | Single-cell + EpiMap + ABC enhancer-gene integration | T3 (gated) |
| 10 | Deep-learning variant effect (Enformer, Borzoi, Sei, AlphaMissense) | T3 (gated) |
| 11 | Manuscript, figures, submission | M (parallel from Phase 9) |

**Gate decision criteria (pre-registered):**

- **CP#1 (T1 → T2):** T2 is activated if and only if: (a) ≥ 1 Tier A signal (PP.H4 ≥ 0.9 across all four thresholds) survives with a plausible causal gene and tissue; (b) ≥ 50% of Tier A signals replicate in ≥ 1 independent cohort; (c) all three negative-control gene sets are null; (d) at least one ancestry-matched analysis slice retains adequate power under Hou et al. 2023-style matched-N preview. If any of (a)-(d) fail, the project stops at T1, is submitted to AJHG with an honest accounting of what was found, and T2 is not planned.

- **CP#2 (T2 → T3):** T3 is activated if and only if: (a) MR identifies ≥ 1 causally-directed trait pair with three-method agreement; (b) matched-N concordance reveals a clearly-quantified power inflation in the prior Table 2; (c) PRS-CSx produces interpretable calibration + clinical utility metrics in ≥ 3 ancestries; (d) the project's cumulative findings are judged (by the investigator in a written memo) to be a plausible Nature Genetics submission. If any of (a)-(d) fail, the project is submitted with T1+T2 to Nature Metabolism or AJHG without T3, and T3 is not planned.

---

## 7. Randomization

Not applicable. This is a secondary observational study; participants were enrolled in their respective biobank cohorts under those cohorts' own protocols.

---

## 8. Existing Data

**Registration timing:** *Registration prior to analysis of the data.*

**Explanation.** The investigator has previously analyzed a prior version of a subset of this data using `coloc.abf` and the draft manuscript `ajhg_manu_v10.pdf` records those results. **This pre-registration covers entirely new analyses:**

1. **New method:** `coloc.susie` replaces `coloc.abf`. The investigator has not run `coloc.susie` on any of the trait pairs at any of the loci in this project prior to this registration.

2. **New cohorts:** The revision adds AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann), AFR T2D, EAS (BBJ Sakaue 2021), Hispanic (PAGE/HCHS), Pan-UKBB trans-ancestry sumstats, deCODE pQTL, UKB-PPP pQTL, and GTEx v8 sQTL. None of these have been analyzed in the context of the current pre-registered analysis plan.

3. **New analyses:** Three-way QTL colocalization, MR, matched-N concordance, PRS-CSx, LDSC partitioned heritability, LDSC-SEG, selection scans, Enformer/Borzoi inference, MPRA overlap, and single-cell integration are all new to this project.

4. **Data access status at registration:** Open-access summary statistics for 6 of the 8 primary data sources have been confirmed reachable from the investigator's HPC environment but have not been downloaded in full or harmonized. UKB-PPP Synapse certification is complete; deCODE portal inventory has been verified (~4,907 aptamers × SomaScan v4); FinnGen R12 registration is complete with confirmed bucket URLs; GTEx v8, Pan-UKBB, BBJ, MVP dbGaP phs001672 summary statistics are reachable. All of Us Researcher Workbench credentials are active (Controlled Tier), used only for Phase 8 PRS validation. UK Biobank main DUA is not required and is not held.

5. **Prior-draft disclosure:** The full draft manuscript `ajhg_manu_v10.pdf` (coloc.abf-based) exists in the investigator's local files and will be disclosed as a "prior version" in the revised manuscript's methods section and cover letter. No quantitative results from the prior draft are being reused in the new submission; the revision is a methodological ground-up rewrite.

---

## 9. Data Collection Procedures

No new data collection. All data are pre-existing publicly available summary statistics (or individual-level genotypes inside the All of Us Researcher Workbench for Phase 8). Full source inventory, access models, and HPC connectivity verification dates are recorded in `.planning/data_access.md` in the project repository.

**Data sources (summary):**

| Source | Role | Access model |
|---|---|---|
| UKB-PPP (Sun 2023) | Phase 2 pQTL coloc | Synapse syn51364943, certified-user (verified 2026-04-10) |
| deCODE pQTL (Ferkingstad 2021) | Phase 2 pQTL coloc | decode.com/summarydata/, ephemeral email-gated download (verified 2026-04-10) |
| GTEx v8 | Phase 2 eQTL + sQTL coloc | Open GCS bucket, no registration |
| FinnGen R12 | Phase 9 replication + MR | elomake.helsinki.fi click-wrap, registered 2026-04-10 |
| Pan-UKBB | Phase 3 trans-ancestry MR, Phase 9 replication | Open S3, CC-BY-4.0 |
| BBJ PheWeb-JP (Sakaue 2021, Ishigaki 2020) | Phase 3/9 EAS | Open NBDC hum0197-v3 |
| MVP dbGaP phs001672 | Phase 9 replication | Open dbGaP, no DAR required for sumstats |
| All of Us | Phase 8 PRS validation, Phase 9 replication | Controlled Tier (credentialed) |
| GBMI | Phase 9 replication | Open meta-analysis portal |
| 1000 Genomes / HGDP | LD reference, selection scans (Phase 6, T3) | Open |

---

## 10. Sample Size and Sample Size Rationale

Sample sizes are **fixed by the underlying data releases** and are not subject to investigator choice. The investigator does not select participants; all summary statistics are used as released by each consortium for the five traits of interest.

**Trait-level ancestry-stratified sample sizes** (approximate, as of release versions cited):

- **BMI:** GIANT (EUR ~700K), Pan-UKBB (AFR ~6K, EAS ~2K, AMR/HIS ~1K), BBJ (EAS ~160K), Gurdasani 2019 (AFR ~14K).
- **T2D:** DIAMANTE (EUR ~900K), Mahajan 2022 multi-ancestry (AFR, EAS, SAS, HIS), BBJ (EAS ~210K), MVP (EUR, AFR, HIS).
- **Hypertension:** Pan-UKBB (all 6 ancestries), BBJ (EAS), Hoffmann (AFR).
- **Ischemic stroke:** MEGASTROKE (EUR ~520K), Pan-UKBB, BBJ, GIGASTROKE multi-ancestry 2022.
- **Asthma:** Demenais 2018 (EUR ~135K), TAGC multi-ancestry, Pan-UKBB, BBJ.

**Power considerations:** Minimum ancestry sample sizes for credible set detection in SuSiE-RSS are documented in Wang et al. 2020; the project explicitly does not attempt to compensate for under-powered slices and instead reports "insufficient power" as a valid outcome where applicable (REQ-4 enforces weak-instrument diagnostic tables per ancestry per trait pair in Phase 3).

**Stopping rule.** Not applicable — no enrollment. The stopping rule for the project as a whole is governed by the tiered checkpoints (§6).

---

## 11. Variables

### Manipulated variables

None. This is an observational secondary analysis.

### Measured variables

**Primary outcomes:**

1. **Colocalization posterior probabilities (PP.H0, PP.H1, PP.H2, PP.H3, PP.H4)** from `coloc.susie` for every trait pair × ancestry × locus combination, with four PP.H4 thresholds {0.5, 0.7, 0.8, 0.9} used for tier assignment.

2. **Credible sets** from SuSiE-RSS fine-mapping per trait × ancestry × locus: credible set size, `min_abs_corr`, convergence status, `L` used vs `L` cap.

3. **QTL colocalization tier per gene per tissue per cell type** from three-way (eQTL, pQTL, sQTL) coloc.

4. **Pathway enrichment q-values** from MAGMA, g:Profiler (with discoverability-matched per-trait backgrounds), and LDSC partitioned heritability.

5. **Replication statistics** per Tier A signal: lookup P-value and beta direction in each replication cohort.

**Secondary outcomes (T2, gated):**

6. **MR causal estimates** (IVW, MR-Egger, weighted median, MR-PRESSO, MR-CAUSE, MR-RAPS for AFR/EAS) per trait pair per ancestry, with weak-instrument diagnostics (F-statistic, I², Q-statistic).

7. **Matched-N bootstrap concordance** (100 iterations) between EUR and AFR for each trait, and LDSC cross-ancestry genetic correlation `r_g` as a global benchmark.

8. **PRS metrics** per ancestry: discrimination (R², AUC, incremental C-statistic), calibration (Hosmer-Lemeshow, slope, intercept, observed-vs-expected), clinical utility (NRI, decision-curve net benefit).

**Tertiary outcomes (T3, gated):**

9. **Selection scan statistics** (iHS, SDS, PBS, XP-EHH) at surviving Tier A loci, and polygenic selection test statistics (e.g., Berg & Coop 2014, sBayesS).

10. **Deep-learning variant effect scores** (Enformer, Borzoi, Sei, AlphaMissense) at credible-set variants, with overlap against public MPRA datasets.

### Indices

A **composite functional-evidence score** per variant (T3, Phase 10) combining: (i) three-way QTL coloc max PP.H4, (ii) pathway enrichment q-value for the variant's gene, (iii) Enformer regulatory track score, (iv) Sei regulatory activity score, (v) AlphaMissense score (for coding variants), (vi) MPRA functional classification. Exact weighting is **not** pre-specified and will be reported as a sensitivity sweep rather than a single combined number, because the literature lacks consensus on how to weight these components.

---

## 12. Analysis Plan

### 12.1 Statistical models

**Fine-mapping (Phase 1):** SuSiE-RSS with `L = 10`, min_abs_corr = 0.5 as the baseline, with a pre-registered sensitivity sweep at min_abs_corr ∈ {0.1, 0.5, 0.9} for complex regions. Convergence failure policy (pre-registered in `config/susie_policy.yaml`): regions that fail to converge under `L = 10` are re-run with `L = 5` and then `L = 3`; regions failing all three are reported as "unresolved" in the supplementary table and excluded from colocalization downstream.

**Colocalization (Phase 1, Phase 2):** `coloc.susie` with default priors (p1 = p2 = 10⁻⁴, p12 = 10⁻⁵). PP.H4 threshold sweep at {0.5, 0.7, 0.8, 0.9}. Tier assignment: Tier A = PP.H4 ≥ 0.9 across all four thresholds; Tier B = PP.H4 ≥ 0.7 at ≥ 3 thresholds; Tier C = PP.H4 ≥ 0.5 at ≥ 2 thresholds.

**Pathway enrichment (Phase 5):** MAGMA gene-based and gene-set enrichment with 1000G EUR LD panel for EUR analyses and matched ancestry panels where available. g:Profiler with discoverability-matched per-trait backgrounds. LDSC partitioned heritability across the Finucane 2015 baseline and pathway-stratified annotations. LDSC-SEG for tissue-specific heritability. Permutation null (N = 1000) for colocalization gene lists.

**Replication (Phase 9):** Lookup of Tier A signals in FinnGen R12, GBMI, MVP phs001672, BBJ, and All of Us (via summary-stat export from the Workbench). Replication = P < 0.05 with concordant effect direction at the locus-level sentinel variant.

**Mendelian randomization (Phase 3, T2, gated):** IVW, MR-Egger, weighted median (three-method triangulation). MR-PRESSO and MR-CAUSE for outlier robustness. MR-RAPS for weak-instrument mitigation in AFR and EAS. Ancestry-specific vs trans-ancestry instrument choice made **per trait pair** with pre-registered criteria: ancestry-specific when F-statistic ≥ 10 per ancestry, trans-ancestry when F-statistic < 10 per ancestry.

**Matched-N concordance (Phase 4, T2, gated):** 100× bootstrap resampling of EUR down to AFR sample size, re-running coloc.susie on each bootstrap, reporting mean and 95% CI for cross-ancestry concordance. LDSC cross-ancestry `r_g` as a complementary benchmark.

**PRS (Phase 8, T2, gated):** PRS-CSx trained on EUR discovery sumstats with AFR, EAS, and Hispanic transfer. Discrimination: R² (liability scale), AUC, incremental C-statistic vs clinical baseline. Calibration: Hosmer-Lemeshow test, calibration slope (target = 1), calibration intercept (target = 0), observed-vs-expected deciles plot. Clinical utility: NRI at pre-specified risk threshold, decision-curve analysis, net benefit vs "treat all"/"treat none".

**Selection scans (Phase 6, T3, gated):** iHS and XP-EHH computed via selscan 2.0 on phased 1000G + HGDP reference haplotypes. SDS computed via sds-wrapper. PBS (Yi et al. 2010 style) on 1000G super-populations. Polygenic selection: Berg & Coop 2014 framework.

### 12.2 Transformations

- **Sumstats harmonization:** Effect allele alignment to the hg38 reference, liftover from hg19 where needed, effect direction alignment, flipping strand-ambiguous SNPs (A/T, C/G with MAF > 0.4) excluded, MAF filter ≥ 0.01.
- **deCODE pQTL Beta:** Already in standard-deviation units per the deCODE README; no additional transformation.
- **Liability-scale PRS:** Transformed from observed-scale via population prevalence estimates from the trait's source cohort.

### 12.3 Inference criteria

- **Phase 1 (fine-mapping):** Primary credible set per region = the SuSiE credible set with minimum size and maximum `min_abs_corr`.
- **Phase 2 (coloc):** Primary tier = Tier A as defined in §12.1. Full threshold sweep reported in supplementary.
- **Phase 3 (MR, gated):** Causal claim requires three-method agreement (IVW, MR-Egger, weighted median all P < 0.05 with concordant direction), non-significant MR-PRESSO global test (P > 0.05), and F-statistic ≥ 10 for the instrument set.
- **Phase 5 (enrichment):** Pathway claim requires q < 0.05 after Benjamini-Hochberg correction within the pathway database used, and null result for all three negative-control pathway sets.
- **Phase 9 (replication):** Replication claim requires nominal P < 0.05 with concordant direction at the sentinel variant in ≥ 1 independent cohort.

### 12.4 Data exclusion

- **Locus exclusions (pre-registered):** Complex regions with SuSiE convergence failure at `L = 3` are excluded from primary coloc (reported as "unresolved").
- **Variant exclusions:** Strand-ambiguous SNPs with MAF > 0.4 are excluded. The KCNJ11 asthma-HTN Tier-1 signal from the prior draft is dropped (n_SNPs = 6 < 50 threshold) — already committed as a decision in `.planning/DECISIONS.md`. The DIAMANTE T2D dedup issue flagged in the prior draft's 76/63%/26 denominator mismatch has been audited and resolved at the position-level dedup stage (commit `81611aa` in the repo).
- **Trait exclusions:** None at pre-registration. If a trait fails to harmonize across all five ancestries (no trait has SNPs in > 2 ancestries), it will be reported as excluded in a supplementary note.

### 12.5 Missing data

- **Cross-cohort missingness:** If a sentinel variant is absent from a replication cohort, the next-best proxy variant (r² > 0.8 in the relevant ancestry) is used. Proxy substitution is reported per Tier A signal.
- **Ancestry missingness:** Traits with no AFR or EAS sumstats available are marked "EUR-only" and excluded from matched-N analyses.
- **QTL missingness:** Genes with no GTEx v8 eQTL signal (e.g., low-expression tissues) are reported as "no eQTL evidence" and do not contribute to three-way QTL scoring.

### 12.6 Exploratory analyses

All analyses beyond those listed above are exploratory and will be labeled as such in the manuscript. Specifically:

- Single-cell eQTL integration (OneK1K, CLUES) if data are available by Phase 2 execution.
- Additional pQTL cohorts beyond UKB-PPP and deCODE (e.g., ARIC, INTERVAL) if time permits.
- ML scorecard refinement from the prior draft — **not** planned for the revision; the prior ML scorecard is dropped per `DECISIONS.md`.
- Trait-level subgroup analyses (sex-stratified, age-stratified) — not planned at pre-registration.

---

## 13. Other

### 13.1 Pre-registered failure modes

The following pre-specified outcomes trigger specific responses, not post-hoc reframing:

1. **All negative controls non-null.** Pipeline failure. Submission blocked. Investigation and re-pre-registration required.
2. **< 1 surviving Tier A signal after Phase 2.** T2/T3 not activated; T1 alone is submitted to AJHG with an honest accounting titled "Cross-ancestry colocalization at cardiometabolic loci: a negative result".
3. **< 50% Tier A replication in Phase 9.** T2/T3 not activated; manuscript discusses replication failure as the primary finding.
4. **MR finds no causally-directed trait pairs.** T3 not activated; the MR result is reported as "null" rather than reframed.
5. **PRS transfer fails to produce interpretable calibration.** T3 not activated; the PRS result is reported with the equity-vs-accuracy trade-off framed even if the absolute performance is poor.
6. **Polygenic selection test is null (T3).** Fallback framing (pre-registered in §3, H8) activates: single-locus selection signatures are the primary selection finding, not polygenic selection.

### 13.2 Deviation policy

Any deviation from this pre-registration will be disclosed in the manuscript's Methods section under a subsection titled "Deviations from pre-registration" with explicit rationale per deviation. Deviations made **after** looking at primary results will be flagged as such. A companion "deviation log" will be committed to the project repository at `.planning/osf_deviations.md` with date-stamped entries.

### 13.3 Timeline

**Not pre-registered as a constraint.** The project has no external deadline. Rigor is prioritized over speed per the project charter.

### 13.4 Code and reproducibility

- **Repository:** `github.com/[user]/coloc_analysis` (will be made public on first submission).
- **Snakemake pipeline:** All analyses run via Snakemake 7.32.4 with conda environments pinned to exact versions in `envs/*.yml`.
- **Containers:** Docker and Singularity images built per phase and published via Zenodo with DOI on first submission.
- **CI:** Nightly 3-locus toy smoke test runs via LSF cron on the NCSU HPC (will migrate to GitHub Actions on public release).
- **Data transformations:** All harmonization, liftover, and QC scripts are in `src/python/` and `src/R/` and are the only artifacts allowed between raw downloads and analytical inputs.

### 13.5 Ethical considerations

No human subjects contact, no wet-lab work, no individual-level data outside the All of Us Researcher Workbench (Controlled Tier, used only for Phase 8 PRS validation under NCSU's institutional data use agreement). No identifiable data. All data sources either carry open-access licenses or have been accessed under standard academic credentials disclosed in §9.

### 13.6 Conflicts of interest

None.

### 13.7 Funding

*[Insert funding statement if applicable. If no external funding for this work specifically, state "This work was conducted with internal NCSU ASHES Lab resources and has no external funding for the pre-registered analyses."]*

### 13.8 Target journals

Primary: Nature Genetics (T1+T2+T3). Secondary: American Journal of Human Genetics (T1 only). Tertiary: Nature Metabolism (T1+T2). Cover letters are versioned per target journal at `manuscript/cover_letter/` per `REQ-10`.

---

## End of pre-registration draft

**Checklist before submitting to OSF:**

- [ ] Fill in `[insert ORCID iD]` in §2.
- [ ] Fill in §13.7 funding statement.
- [ ] Verify the GitHub repo name in §13.4 if different from placeholder.
- [ ] Confirm OSF account is active and you can create a new project.
- [ ] In OSF: create a new project titled "coloc_analysis revision" (or similar). Add this investigator as the contributor.
- [ ] From that project, create a pre-registration using the "OSF Preregistration" template.
- [ ] Paste each section above into the matching OSF form field. OSF field names map 1:1 to section headings 1-13.
- [ ] Upload supporting files as attachments: `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `DECISIONS.md`, `data_access.md` (these give reviewers the full planning context).
- [ ] Submit. OSF issues the DOI immediately.
- [ ] Record the DOI in `.planning/data_access.md` at the top of the file.
- [ ] Commit the DOI update and delete this draft file (or keep as historical record — your call).
