# Revision Plan: Cross-Ancestry Cardiometabolic Pleiotropy Manuscript
## Path to a Nature Genetics–Caliber Submission

**Author:** Carter K. Clinton (ASHES Lab, NCSU)
**Current draft:** `ajhg_manu_v10.pdf`
**Target journals (in order):** Nature Genetics → American Journal of Human Genetics → Genome Medicine → Cell Genomics
**Plan date:** April 2026
**Scope constraint:** 100% publicly available data; computational analyses only. No wet-lab, functional validation, or experimental work is part of this plan.
**Timeline constraint:** Execution time is not a binding constraint — the plan is optimized for scientific rigor and impact, not speed.

---

## 0. Executive summary

The current manuscript assembles a useful pipeline and a reproducible package, but the headline contribution as written is largely a re-cataloging of pleiotropic loci that the field already knows about (KCNJ11, TCF7L2, MC4R, FTO, GCKR, APOE, IRS1, PPARG). It is also weakened by methodological choices that competent reviewers will flag immediately: `coloc.abf` instead of `coloc.susie` despite SuSiE outputs already being computed; an ad hoc fold-enrichment "pathway analysis" with no statistical test; a cross-ancestry concordance table that compares different trait pairs at the same locus; "ML" branding for a hand-weighted scorecard; and several broken supplementary files.

This plan pivots the manuscript from a **descriptive pleiotropy catalog** to a **mechanistically and causally resolved cross-ancestry pleiotropy framework** with three linked analytical spines: (1) `coloc.susie` + molecular QTL (eQTL/pQTL/sQTL) three-way colocalization → causal gene + tissue; (2) bidirectional Mendelian randomization → causal direction between trait pairs; (3) matched-N cross-ancestry analysis + LDSC partitioned heritability + selection statistics → rigorous evolutionary and equity story. With those three spines, the contribution becomes about *resolving* the biology rather than tallying it, and the evolutionary medicine framing becomes a tested hypothesis rather than post-hoc storytelling.

**All analyses use publicly available GWAS summary statistics, molecular QTL resources, single-cell atlases, and ancient DNA panels** — there is no wet-lab, experimental, or functional validation component. Every finding in the revised manuscript will be purely computational and fully reproducible from public data.

If executed in full, this revision is competitive at *Nature Genetics* and *Cell Genomics*, with *AJHG* as the conservative fallback.

---

## 1. Diagnosis: what's wrong with the current draft

### 1.1 Methodological problems
1. `coloc.abf` assumes a single causal variant per region; in 1 Mb windows around well-powered GWAS lead variants, multiple independent signals are the norm (Wallace 2020, *PLoS Genet*).
2. Pathway "enrichment" is a ratio of observed to expected genes with no statistical test, no multiple-testing correction, no length/LD/discoverability-matched background (Reimand et al. 2019, *Nat Protoc*; de Leeuw 2015, *PLoS Comput Biol*).
3. Cross-ancestry "concordance" mixes trait pairs at the same locus (e.g., EUR BMI-T2D vs AFR stroke-T2D for TCF7L2). This is a category error.
4. Sample-size asymmetry (EUR ~1.3M vs AFR ~20K–100K) is a quantitative confounder for coloc Bayes factors, not just a "data gap."
5. "Machine learning" gene prioritization is a weighted sum with hand-chosen weights, no training/test split, no cross-validation.
6. No multiple-testing framework for the 585 coloc tests, the pathway enrichment, or the gene scoring.
7. Evolutionary medicine framing is asserted, never tested (no iHS/PBS/SDS/XP-EHH).
8. Drug target claims rest on existing approved therapies for the very traits in question (sulfonylureas → T2D, MC4R agonists → BMI), not target discovery.
9. Variant rs1421085 (FTO/IRX3) and rs12740374 (SORT1) lack primary citations (Claussnitzer 2015 *NEJM*; Musunuru 2010 *Nature*).
10. No replication in an independent cohort.

### 1.2 Data / file issues
1. `Tables/Table1_Top20_Signals.tsv` is corrupted — appears to be `head -20` of an unsorted file; PP.H4 values in the TSV are 1e-5 to 1e-23 while the PDF Table 1 (correctly) shows TCF7L2 = 1.000, SH2B3 = 1.000, etc.
2. `Tables/Table3_Pleiotropic_Loci.tsv` has the header on the last line (row 16) instead of row 1.
3. Tier definitions: methods describe 4 tiers; `TableS4_All_Results.tsv` has 5 (Tier5_Weak is undefined in the manuscript).
4. KCNJ11 asthma–hypertension (Tier1, PP.H4 = 0.87) has only 6 overlapping variants — violates the stated ≥50 overlap QC threshold.
5. Reproducibility README says "8 seed loci / ~200 tiles" while the manuscript says "50 regions / 205 tiles."
6. "76 colocalization signals" denominator in the variant classification section is not defined and does not match any threshold in TableS4 (PP.H4 ≥ 0.1 gives 54).
7. "63% (16/26)" should be 62%; the "26" denominator is not defined.
8. macOS `.DS_Store` and `~$hg_manu_v10.docx` lock files are scattered through the submission package.
9. Reference order: ref 27 is cited before refs 14–26 in the introduction, indicating references were added without renumbering.

### 1.3 Interpretive overreach
1. "91% regulatory" is the base rate for GWAS lead variants (Maurano 2012, *Science*) and is not a finding.
2. "Genetic independence of asthma" from cardiometabolic traits, based on mean PP.H4 = 0.02 in failed tests, is *absence of evidence* framed as *evidence of absence*; LDSC genetic correlations show non-zero rg between asthma and BMI (Ferreira 2019, *Nat Genet*).
3. "Cross-ancestry concordance suggests pathway conservation predating divergence" is unsupported by any selection scan or haplotype analysis.
4. The "metabolic syndrome as pathway-defined entity" claim rests on the (untested) pathway enrichment and would dissolve under proper statistical scrutiny.

---

## 2. Vision for the revised paper

**Working title:** *Causal-gene resolution and cross-ancestry transferability of cardiometabolic pleiotropy: a coloc.susie + Mendelian randomization + selection-aware framework*

**One-sentence pitch:** By resolving 50 cardiometabolic pleiotropic loci to causal genes, causal tissues, causal directions of trait-trait effects, and matched-power cross-ancestry transferability — and by formally testing whether shared metabolic pathways carry signatures of recent selection — we provide a mechanistic and evolutionarily anchored map of cardiometabolic comorbidity that supports both rational drug repurposing and equitable polygenic risk prediction.

**Five claims the revised paper will defend:**
1. With `coloc.susie` and three-way colocalization against eQTL/pQTL/sQTL, ≥X% of high-confidence pleiotropic loci can be resolved to a single causal gene in a single causal tissue.
2. Bidirectional MR establishes causal directions for ≥Y trait pairs at colocalized loci, distinguishing reverse causation from genuine pleiotropy.
3. After matching EUR and AFR sample sizes, ≥Z% of EUR Tier-1 pleiotropic signals replicate in AFR, quantifying the *power-corrected* concordance and the residual ancestry-specific component.
4. Pleiotropic loci are significantly enriched for selection signatures (iHS, SDS, PBS) in pathways predicted by the thrifty-gene and antagonistic-pleiotropy hypotheses, providing the first formal evolutionary medicine test of cardiometabolic pleiotropy.
5. A pathway-restricted polygenic risk score built from pleiotropic loci shows improved cross-ancestry transferability vs. genome-wide PRS, providing a directly actionable framework for equitable precision medicine.

**Why this is Nature Genetics-caliber:** It combines methodological rigor (coloc.susie + matched-N + replication), mechanistic resolution (three-way coloc + MR), and a novel cross-disciplinary contribution (selection-aware pleiotropy analysis), all anchored by an equity-relevant deliverable (transferable PRS). No existing paper does all five.

---

## 3. Recommended analytical pipeline

### 3.1 Phase 0 — Data and infrastructure (Weeks 1–3)

**Goal:** Fix all data/file issues, expand the GWAS catalog, and lock the analysis environment.

**Tasks:**
- Regenerate `Table1_Top20_Signals.tsv` and `Table3_Pleiotropic_Loci.tsv` from `TableS4_All_Results.tsv` with correct sorting and headers.
- Audit deduplication (167K dups removed from DIAMANTE T2D EUR is suspicious — verify it's not collapsing multi-allelic sites incorrectly).
- Re-evaluate the lift-over of CAAPA asthma AFR (96.6% retention; characterize the 3.4% dropped variants by chromosome and MAF; lift-over artifacts disproportionately affect African-ancestry variation per Oudkerk-Pool 2024).
- **Add African-ancestry GWAS that the current draft missed:**
  - BMI: Gurdasani et al. 2019 (*Cell*) AWI-Gen + UK Biobank AFR; Ng et al. 2017 (*Diabetes*) AAGILE meta-analysis.
  - Hypertension: Hoffmann et al. 2017 (*Nat Genet*) million-veteran-program AFR; Giri et al. 2019 (*Nat Genet*) MVP BP AFR.
  - These exist and substantially close the AFR power gap. The current claim that "African ancestry BMI and hypertension GWAS of sufficient size were not available" is no longer correct as of 2024–2026.
- Add **East Asian and Hispanic/Latino ancestries**: BBJ for T2D/BMI/hypertension (Sakaue et al. 2021 *Nat Genet*), PAGE for cross-trait Hispanic/Latino (Wojcik et al. 2019 *Nature*). This converts the paper from "cross-ancestry" (which currently means EUR + a small AFR fragment) to genuinely multi-ancestry.
- Lock the conda environment and re-run all sumstats QC under the same software versions (pin coloc, susieR, MungeSumstats, ldsc, LDSCORE, MR-Base versions).
- Stand up a Snakemake DAG with checkpoints so every step is reproducible and re-runnable.
- Clean macOS `.DS_Store`, lock files, and the obsolete `AJHG_files`–`AJHG_files7` directories from the repo.

### 3.2 Phase 1 — Replace the colocalization spine (Weeks 4–8)

**Goal:** Replace `coloc.abf` with `coloc.susie` as the primary analysis.

**Methods:**
- For every (region × trait_A × trait_B × ancestry) quadruple, run SuSiE-RSS independently per trait per region using ancestry-matched LD reference panels.
- Use 1000 Genomes Phase 3 + HGDP joint reference (Koenig et al. 2024 *Cell Genomics*) for AFR LD; ideally use within-cohort LD (per Benner et al. 2017 *AJHG*) where the underlying GWAS releases LD matrices (DIAMANTE does for some chromosomes; UK Biobank releases LD via PanUKBB).
- Run `coloc.susie` (Wallace 2021 *PLoS Genet*) on the credible sets, returning one PP.H4 per (credible_set_A × credible_set_B) pair.
- Compare against the current `coloc.abf` results in a per-locus supplementary table.
- Apply per-locus prior calibration (`minp12` from Wallace 2020).
- Sensitivity analysis at p12 ∈ {1e-6, 1e-5, 1e-4} reported as full PP.H4 distributions (not just retention counts) in a supplementary figure.

**Software:** R 4.4, coloc v5.2+, susieR v0.12+, Rfast, data.table.

**Expected outputs:**
- Updated TableS4 with credible-set-level PP.H4.
- Identification of loci with multiple independent shared signals (which `coloc.abf` collapses).
- A coloc.abf vs coloc.susie agreement plot.

**Key references:** Wallace 2020, 2021; Zou et al. 2022 *PLoS Genet* (SuSiE-RSS); Foley et al. 2021 *Nat Commun* (coloc QC).

### 3.3 Phase 2 — Mechanistic resolution via molecular QTL three-way coloc (Weeks 9–14)

**Goal:** For every Tier-1 trait-trait colocalization, identify the causal gene and the causal tissue by adding eQTL, pQTL, and sQTL coloc.

**Methods:**
- **eQTL coloc:** GTEx v8 (54 tissues, GTEx 2020 *Science*) cis-eQTL summary statistics; eQTL Catalogue (Kerimov et al. 2021 *Nat Genet*) for additional tissues and conditions.
- **pQTL coloc:** UK Biobank Pharma Proteomics Project (Sun et al. 2023 *Nature*; ~3,000 plasma proteins, ~50K participants) and deCODE (Ferkingstad et al. 2021 *Nat Genet*; ~5K proteins).
- **sQTL coloc:** GTEx v8 sQTLs.
- **Single-cell eQTL:** OneK1K (Yazar et al. 2022 *Science*) and CLUES (Perez et al. 2022 *Science*) for immune cell-type-resolved eQTLs (relevant for the asthma branch of the analysis).
- For each trait-trait colocalized credible set, test colocalization with every cis-eQTL/pQTL/sQTL in a 500 kb window. Report only signals where PP.H4 ≥ 0.8 across at least one trait–molecular layer pair.
- Define **mechanistic confidence**:
  - **Tier A:** trait1 + trait2 + eQTL or pQTL all colocalize (PP.H4 ≥ 0.8) in a tissue/cell type biologically plausible for both traits.
  - **Tier B:** trait1 + trait2 colocalize, plus colocalization with an eQTL/pQTL in *one* relevant tissue.
  - **Tier C:** trait1 + trait2 colocalize but no QTL coloc above threshold.
- Cross-reference with **Open Targets Locus2Gene** scores (Mountjoy et al. 2021 *Nat Genet*) — pre-trained on gold-standard causal gene assignments — as an independent gene assignment line.

**Software:** coloc v5.2, Open Targets Genetics API, GTEx portal API, eQTL Catalogue API.

**Expected outputs:**
- A "causal gene × causal tissue" matrix for each pleiotropic locus.
- For ~30–60% of Tier-1 loci, an unambiguous mechanistic assignment.
- Several novel mechanistic discoveries (the hypothesis is that some "well-known" loci will resolve to a different gene than the obvious one — this happened for FTO/IRX3, SORT1/CELSR2, PPARG/SYN2).

**Key references:** Giambartolomei 2014; Wallace 2021; GTEx 2020; Sun 2023; Ferkingstad 2021; Mountjoy 2021; Claussnitzer 2015 *NEJM*.

### 3.4 Phase 3 — Causal directionality via Mendelian randomization (Weeks 15–18)

**Goal:** For each high-confidence pleiotropic trait pair, test causal direction with bidirectional two-sample MR.

**Methods:**
- Use `TwoSampleMR` (Hemani et al. 2018 *eLife*) and `MendelianRandomization` R packages.
- Instruments: independent (clumped at r² < 0.001, ±10 Mb) genome-wide significant variants for the exposure trait, with F-statistic > 10.
- Methods: inverse-variance weighted (IVW) as primary; MR-Egger, weighted median, weighted mode, and MR-PRESSO (Verbanck et al. 2018 *Nat Genet*) as sensitivity analyses for horizontal pleiotropy.
- **Steiger filtering** (Hemani et al. 2017 *PLoS Genet*) to remove instruments with stronger associations to the outcome than the exposure (rules out reverse causation per instrument).
- **MR-CAUSE** (Morrison et al. 2020 *Nat Genet*) to formally distinguish correlated horizontal pleiotropy from causation.
- **Multivariable MR** (Sanderson et al. 2019 *Int J Epidemiol*) for trait triples (e.g., BMI → T2D conditional on hypertension) to disentangle mediating effects.
- **Locus-specific MR** at each pleiotropic locus using only the colocalized lead variant — this is the cleanest causal claim.
- Cross-ancestry MR using Pan-UKBB and BBJ as outcome cohorts (Lawson et al. 2020 *Nat Rev Genet* for population-stratified MR cautions).

**Software:** TwoSampleMR, MendelianRandomization, MR-PRESSO, MR-CAUSE, RadialMR.

**Expected outputs:**
- A directed causal graph between BMI ↔ T2D ↔ hypertension ↔ stroke ↔ asthma.
- Per-locus causal effect estimates.
- Identification of loci where coloc says "shared" but MR says "reverse causation."

**Key references:** Hemani 2018; Verbanck 2018; Morrison 2020; Sanderson 2019; Lawson 2020; Burgess et al. 2020 *Eur J Epidemiol* (MR best practices guidelines).

### 3.5 Phase 4 — Cross-ancestry transferability with matched power (Weeks 19–22)

**Goal:** Replace the current cross-ancestry concordance section with a methodologically defensible, matched-N analysis that rigorously quantifies what transfers and why.

**Methods:**
- For each trait pair testable in both ancestries (T2D-stroke, T2D-asthma, stroke-asthma, plus the new BMI-* and hypertension-* pairs unlocked by the AFR GWAS additions in Phase 0), run coloc.susie in both ancestries with **matched effective sample size** by down-sampling EUR.
- Repeat the down-sampling 100× and report bootstrap CIs for PP.H4 in EUR-down.
- Compute **expected detection probability** in AFR for every EUR Tier-1 signal under the null of identical effect sizes, given the AFR sample size — this turns "we couldn't test it" into a quantitative statement (Hou et al. 2023 *Nat Genet*).
- Apply **TRACTOR** (Atkinson et al. 2021 *Nat Genet*) to admixed African-American cohorts (PAGE, All of Us AFR) for ancestry-stratified effect size estimation at pleiotropic loci.
- Compute **cross-ancestry rg** with LDSC-XTAR (Brown et al. 2016 *AJHG*) and Popcorn (Brown 2016) as a global benchmark.
- For loci that *don't* transfer even after matched-N, test for ancestry-specific causal variants by examining (a) AFR-specific lead SNPs, (b) ancestry-specific eQTL coloc, (c) frequency differences ≥ 10% in 1000G.
- Add **East Asian and Hispanic/Latino** layers from BBJ and PAGE to convert this into a four-ancestry analysis.

**Software:** coloc v5.2, LDSC, Popcorn, TRACTOR, PRS-CSx (Ruan et al. 2022 *Nat Genet*).

**Expected outputs:**
- A power-corrected concordance table replacing the current Table 2.
- A list of genuinely ancestry-specific pleiotropic signals (with frequency / LD evidence).
- Quantitative attribution of the EUR-AFR gap to (i) sample-size, (ii) LD differences, (iii) effect-size differences, (iv) frequency differences.

**Key references:** Hou 2023; Atkinson 2021; Brown 2016; Wojcik 2019; Sakaue 2021; Martin et al. 2019 *Nat Genet*; Privé et al. 2022 *AJHG*; Mahajan 2022 *Nat Genet*.

### 3.6 Phase 5 — Pathway architecture, properly tested (Weeks 23–25)

**Goal:** Replace the ad hoc fold-enrichment with multi-method, properly null-controlled pathway analysis tied to heritability.

**Methods:**
- **MAGMA gene-based and gene-set analysis** (de Leeuw 2015 *PLoS Comput Biol*) on the full GWAS summary statistics for each trait, with KEGG, Reactome, GO BP, MSigDB Hallmark, and a custom set of 8 cardiometabolic-curated pathways. Bonferroni and FDR correction across all gene sets per trait.
- **g:Profiler** (Reimand 2019 *Nat Protoc*) on the colocalization gene list with electronic-GO-annotation filtering and a **discoverability-matched background** (genes within 500 kb of any genome-wide significant SNP for any of the 5 traits).
- **LDSC partitioned heritability** (Finucane 2015 *Nat Genet*) using the pathway gene sets as binary annotations, computing the per-trait heritability fraction explained by each pathway. This is the strongest quantitative claim available — far more meaningful than fold enrichment.
- **LDSC-SEG** (Finucane 2018 *Nat Genet*) for tissue-specific heritability enrichment per trait, using GTEx 53-tissue RNA-seq and Roadmap chromatin annotations. Then test whether *pleiotropic* loci preferentially fall in tissues shared between trait pairs (e.g., pancreas for BMI-T2D, vascular smooth muscle for hypertension-stroke).
- **HESS / ρ-HESS** (Shi et al. 2017 *AJHG*) for local genetic covariance — quantifies how much of the trait-pair genetic correlation concentrates at the colocalized loci vs the polygenic background.
- Permutation null for the colocalization-derived gene list against 1000 random gene sets matched for length, LD, and MAF.

**Software:** MAGMA v1.10, g:Profiler API, LDSC, sLDSC, LDSC-SEG, HESS, PASCAL.

**Expected outputs:**
- A statistically defensible pathway enrichment table with FDR-corrected p-values.
- Per-trait heritability fractions explained by metabolic, appetite, glucose, fatty acid, and inflammation pathways.
- Tissue-specific enrichment per trait pair, supporting (or refuting) the "pathway-defined metabolic syndrome" thesis.

**Key references:** de Leeuw 2015; Reimand 2019; Finucane 2015, 2018; Shi 2017; Bulik-Sullivan et al. 2015 *Nat Genet*; Holmans 2009 *AJHG*; Taylor-Weiner et al. 2019 *bioRxiv*.

### 3.7 Phase 6 — Selection-aware evolutionary medicine test (Weeks 26–29)

**Goal:** Convert the evolutionary medicine framing from post-hoc storytelling into a formally tested hypothesis.

**Methods:**
- **iHS** (Voight et al. 2006 *PLoS Biol*) and **nSL** (Ferrer-Admetlla et al. 2014 *Mol Biol Evol*) for recent positive selection in 1000G EUR, AFR, EAS, SAS at every pleiotropic lead variant.
- **PBS** (Yi et al. 2010 *Science*) for population-specific selection on three-way comparisons.
- **XP-EHH** (Sabeti et al. 2007 *Nature*) for cross-population haplotype differentiation.
- **SDS** (Field et al. 2016 *Science*) for very recent (last 2,000 years) selection in UK Biobank.
- **Relate / Tsdate** (Speidel et al. 2019 *Nat Genet*; Wohns et al. 2022 *Science*) for genome-wide tree-sequence-based selection inference at the pleiotropic loci.
- **Ancient DNA panels** (Allen Ancient DNA Resource v54, Mallick et al. 2024) — test whether the "thrifty" risk-increasing alleles at appetite/insulin pathway loci changed in frequency through the Holocene transition to agriculture.
- **Polygenic selection test** (Berg & Coop 2014 *PLoS Genet*; Berg et al. 2019 *eLife*; Edge & Coop 2019 *Genetics*): test whether pleiotropic appetite-pathway and insulin-pathway alleles show coordinated frequency shifts among populations beyond drift expectation (with the corrections from Sohail et al. 2019 *eLife* and Berg 2019 *eLife* against UK Biobank stratification artifacts).
- **Antagonistic pleiotropy test** at FADS1/FADS2: do alleles that increase metabolic-trait risk decrease asthma risk (or vice versa)? Test the sign concordance across pleiotropic SNPs and compare to a permutation null.
- Stratify selection signatures by pathway (insulin signaling vs appetite vs fatty acid vs inflammation) and test whether the thrifty-gene prediction (positive selection on energy-storage alleles in populations with historical food scarcity) holds.

**Software:** selscan v2 (iHS, nSL, XP-EHH), Relate, Tsdate, hapne, ChromoPainter, Berg-Coop polygenic selection scripts.

**Expected outputs:**
- Selection statistics at every pleiotropic locus across 4–5 ancestries.
- A formal test of the thrifty-gene hypothesis on the colocalized loci.
- A formal test of antagonistic pleiotropy at the asthma–metabolic axis.
- A novel cross-disciplinary contribution that has not been published for cardiometabolic pleiotropy.

**Key references:** Voight 2006; Sabeti 2007; Yi 2010; Field 2016; Berg & Coop 2014; Sohail 2019; Berg 2019; Speidel 2019; Wohns 2022; Mallick 2024; Hamid et al. 2023 *Nat Rev Genet* (review of polygenic selection methods).

### 3.8 Phase 7 — Single-cell integration and functional annotation (Weeks 30–33)

**Goal:** Resolve causal cell types and provide a path to functional follow-up.

**Methods:**
- **CELLECT / CELLEX** (Timshel et al. 2020 *eLife*) for cell-type prioritization using single-cell expression specificity. Reference atlases: Tabula Sapiens (Tabula Sapiens Consortium 2022 *Science*), Human Cell Atlas pancreas/heart/lung/adipose, HuBMAP.
- **scDRS** (Zhang et al. 2022 *Nat Genet*) for trait-cell association scores at single-cell resolution, applied to all 5 traits.
- **MAGMA-celltyping** (Bryois et al. 2020 *Nat Genet*) as an independent line.
- For each pleiotropic locus, intersect the colocalized credible set with **EpiMap** (Boix et al. 2021 *Nature*) and **ENCODE cCREs** v3 to assign tissue-specific enhancer / promoter status.
- **ABC model** (Fulco et al. 2019 *Nat Genet*; Nasser et al. 2021 *Nature*) for enhancer-gene linking at colocalized loci.
- Cross-reference with **GWAS-eQTL co-localization in cell-type-resolved data**: OneK1K immune (Yazar 2022 *Science*), CLUES lupus immune (Perez 2022 *Science*), Stunnenberg pancreatic islet eQTLs (Viñuela et al. 2020 *Nat Commun*).
- Intersect causal credible sets with **publicly available MPRA catalogs** (e.g., MPRAbase, Tewhey 2016 reprocessed data, Abell et al. 2022 *Nature* saturation MPRA in K562/HepG2, van Arensbergen et al. 2019 SuRE data) to annotate regulatory evidence without running new experiments. This preserves the functional-annotation story while staying fully computational.

**Software:** CELLECT, CELLEX, scDRS, MAGMA-celltyping, EpiMap browser, ABC model.

**Expected outputs:**
- Per-locus causal cell type assignments.
- Tissue-specific enhancer maps for each colocalized credible set.
- A prioritized panel of variants for downstream MPRA validation.

### 3.9 Phase 8 — Pathway-restricted, cross-ancestry polygenic risk scores (Weeks 34–37)

**Goal:** Translate the pathway findings into a directly clinically relevant deliverable: a cross-ancestry-transferable PRS.

**Methods:**
- Build PRS for BMI, T2D, hypertension, stroke, asthma using **PRS-CSx** (Ruan et al. 2022 *Nat Genet*) — multi-ancestry coupled prior.
- Build *three* PRS variants per trait:
  1. **Genome-wide PRS** (baseline).
  2. **Pathway-restricted PRS** using only variants in the high-confidence pleiotropic pathway gene set (insulin signaling, appetite regulation, glucose metabolism, fatty acid metabolism).
  3. **Pleiotropy-augmented PRS** — multi-trait PRS using a coloc.susie-informed prior that upweights variants colocalized across ≥2 traits (related to wMT-SBLUP, Maier et al. 2018 *AJHG*; mtCOJO, Zhu et al. 2018 *Nat Commun*).
- Evaluate transferability in held-out cohorts: UK Biobank (EUR, AFR, EAS, SAS), All of Us, MVP, BBJ, PAGE.
- Metrics: incremental R² (BMI), AUC (binary traits), and partial R²/AUC over age + sex + PC1–10.
- Test the hypothesis: pathway-restricted and pleiotropy-augmented PRS will have **smaller absolute performance** but **smaller cross-ancestry performance gap** than the genome-wide PRS — i.e., trade some accuracy for equity.

**Software:** PRS-CSx, mtCOJO, wMT-SBLUP, PLINK 2, R survey package.

**Expected outputs:**
- Per-trait, per-ancestry PRS performance table.
- A direct test of whether pathway-focused PRS improves equity.
- A clinically actionable deliverable that the precision medicine framing of the abstract has been promising but not delivering.

**Key references:** Ruan 2022; Maier 2018; Zhu 2018; Martin 2019; Privé 2022; All of Us Research Program 2024; Lewis & Vassos 2020 *Genome Med*.

### 3.10 Phase 9 — Replication and external validation (Weeks 38–41)

**Goal:** Replicate the primary colocalization findings in independent cohorts not used in discovery.

**Methods:**
- **FinnGen R12** (or latest release) — independent EUR for T2D, BMI, hypertension, stroke, asthma. Re-run coloc.susie at the 50 regions and compute replication rates per Tier-1 signal.
- **Global Biobank Meta-analysis Initiative** (GBMI; Zhou et al. 2022 *Cell Genomics*) — independent meta-analytic replication.
- **MVP** (Million Veteran Program; Hunter-Zinck et al. 2020 *AJHG*) — independent EUR + AFR.
- **All of Us** v8 — independent multi-ancestry.
- For replication metric: define "replicated" as PP.H4 ≥ 0.5 in the replication cohort for the same trait pair at the same lead variant. Report per-tier replication rate.
- For pathway findings: re-run MAGMA gene-set analysis on the replication summary statistics and report whether the top pathways replicate.
- For MR findings: re-run MR with replication-cohort outcomes.

**Expected outputs:**
- Replication rate per tier (target: >70% for Tier-1).
- Per-locus replication evidence in TableS_replication.
- Pathway replication summary.

### 3.11 Phase 10 — Deep causal-variant prioritization from public resources (Weeks 42–50)

**Goal:** Replace the "functional validation" slot with an all-computational causal variant dissection that exploits every public resource, so the manuscript's mechanistic claims are as strong as they can be without generating new experimental data.

**Methods:**
- **Reprocess public MPRA catalogs** for every variant in every high-confidence credible set: Tewhey et al. 2016 (lymphoblastoid), Abell et al. 2022 *Nature* (K562/HepG2 saturation MPRA), van Arensbergen et al. 2019 *Nat Genet* (SuRE), Ajore et al. 2022 (MPRA across immune variants), GTEx v8 variant functional annotations. Any overlap between a colocalized credible set variant and a published MPRA "functional" allele becomes a supporting line of evidence.
- **CRISPRi/a screen public data** from ENCODE4 (Nasser et al. 2021 *Nature* ABC benchmarks), Gasperini et al. 2019 *Cell*, Fulco et al. 2019 *Nat Genet* — reuse published enhancer-gene links to support causal-gene assignments without running new experiments.
- **Deep-learning variant effect predictors on public models**: Enformer (Avsec et al. 2021 *Nat Methods*), Borzoi (Linder et al. 2025 *Nat Genet*), Sei (Chen et al. 2022 *Nat Genet*), DeepSEA, AlphaMissense (Cheng et al. 2023 *Science*), ESM1v, and PrimateAI (Sundaram et al. 2018 *Nat Genet*) — run each lead and credible-set variant through multiple pretrained models and report the convergent predictions. This is a strong computational substitute for wet-lab validation.
- **Long-read haplotype-resolved public data**: HPRC pangenome (Liao et al. 2023 *Nature*) to characterize structural variation at pleiotropic loci that short-read GWAS may miss.
- **Population-specific chromatin data**: EN-TEx (ENCODE cross-tissue personal genomes, Rozowsky et al. 2023 *Cell*) to annotate allele-specific chromatin accessibility and binding at causal credible set variants.
- **3D chromatin**: Hi-C / micro-C / promoter capture Hi-C from public datasets (4DN Nucleome, ENCODE) to link enhancer credible sets to their target promoters at pleiotropic loci.

**Software:** Enformer, Borzoi, Sei, AlphaMissense, PrimateAI, ABC model, HiC-Pro, 4DN analysis tools.

**Expected outputs:**
- Per-variant composite "functional evidence score" combining MPRA overlap, Enformer/Borzoi score, AlphaMissense score (for coding), and 3D enhancer-promoter links.
- Maximum computational confidence in causal variant + causal gene + causal mechanism for every pleiotropic locus.
- A "functional evidence" figure that carries the mechanistic story without any new experiments.

**Key references:** Avsec 2021; Linder 2025; Chen 2022; Cheng 2023; Sundaram 2018; Abell 2022; van Arensbergen 2019; Nasser 2021; Gasperini 2019; Rozowsky 2023; Liao 2023.

---

## 4. Revised manuscript structure

### Title
*Causal-gene resolution and cross-ancestry transferability of cardiometabolic pleiotropy reveal selection-shaped pathway architecture*

### Abstract structure (250 words)
1. **Background:** cardiometabolic comorbidity, knowledge gaps in causal genes, ancestry, and direction.
2. **Approach:** coloc.susie + 3-way QTL coloc + MR + matched-N cross-ancestry + selection scans + transferable PRS, across 5 traits and 4 ancestries.
3. **Causal-gene findings:** X loci resolved to single causal gene + tissue, with N reassignments from the obvious nearest gene.
4. **Causal-direction findings:** Y trait pairs with directionally resolved causal effects.
5. **Cross-ancestry findings:** Z% replication after matching power; quantitative attribution of the residual gap to LD vs frequency vs effect-size differences.
6. **Selection findings:** formal evidence for selection at insulin/appetite pathway loci; test of thrifty-gene and antagonistic-pleiotropy hypotheses.
7. **Translational deliverable:** pathway-restricted PRS with improved cross-ancestry equity.
8. **Implication:** pathway-anchored, mechanistically resolved, evolutionarily contextualized framework for cardiometabolic precision medicine.

### Main figures (target: 7)
1. **Figure 1.** Study design + coloc.susie vs coloc.abf benchmark. Sankey of GWAS → fine-map → coloc → 3-way QTL → MR → selection → deep-learning variant effect → PRS.
2. **Figure 2.** Causal gene and tissue assignments. Heatmap of (locus × QTL layer × tissue) with mechanistic confidence tiers; LocusZoom of 4 highlighted loci.
3. **Figure 3.** Mendelian randomization causal graph. Directed network of trait-trait causal effects with per-locus MR estimates.
4. **Figure 4.** Cross-ancestry transferability. Matched-N concordance, ancestry-specific signals, and the four-ancestry comparison.
5. **Figure 5.** Pathway architecture and selection. MAGMA-significant pathways, LDSC partitioned heritability, iHS/PBS/SDS at pathway loci, polygenic selection test.
6. **Figure 6.** Deep-learning and public-resource causal variant dissection. Composite functional evidence scores per variant, Enformer/Borzoi/AlphaMissense convergent predictions, MPRA overlap, 3D chromatin links.
7. **Figure 7.** Pathway-restricted PRS performance and cross-ancestry equity gap.

### Main tables (target: 2)
1. **Table 1.** Top resolved pleiotropic loci with causal gene, causal tissue, MR direction, ancestry transferability, drug target status, and selection evidence.
2. **Table 2.** Pathway-level summary with MAGMA p-values, LDSC heritability fraction, gene counts, and PRS contribution.

### Supplementary
- Figures S1–S20, Tables S1–S25 covering all phases above.
- A `coloc.abf` vs `coloc.susie` agreement appendix.
- Power calculations for cross-ancestry analysis.
- Full sensitivity analyses for coloc priors, MR pleiotropy, selection-test stratification.

---

## 5. Sequencing of phases

Execution time is not a binding constraint — the plan is optimized for scientific rigor and impact. The phases below are ordered by logical dependency, not by schedule pressure. Phases marked parallelizable can be run concurrently with other phases once their inputs are available.

| Phase | Dependency | Outputs | Parallelizable? |
|---|---|---|---|
| 0. Data + infrastructure fix | — | Clean data, fixed tables, expanded GWAS catalog (EUR, AFR, EAS, Hispanic/Latino) | No |
| 1. coloc.susie spine | Phase 0 | Replaces TableS4 with credible-set-level PP.H4 | No |
| 2. Three-way QTL coloc (eQTL/pQTL/sQTL) | Phase 1 | Causal gene/tissue matrix per locus | No |
| 3. Mendelian randomization | Phase 1 | Directed causal graph between trait pairs | Yes (with Phase 2) |
| 4. Matched-N cross-ancestry | Phase 1 | Replaces Table 2 with power-corrected concordance | Yes (with Phases 2, 3) |
| 5. Pathway + partitioned heritability | Phase 1 | MAGMA + LDSC + HESS tables | Yes (with Phases 2, 3, 4) |
| 6. Selection scans + polygenic selection test | Phase 0 | Formal evolutionary medicine test | Yes (with Phases 2–5) |
| 7. Single-cell + EpiMap + ABC | Phase 2 | Causal cell types; enhancer-gene links | Yes (with Phases 3–6) |
| 8. Cross-ancestry PRS (PRS-CSx) | Phases 1, 4 | Pathway-restricted PRS and equity-gap analysis | No |
| 9. Replication (FinnGen, MVP, GBMI, All of Us, BBJ) | Phases 1, 2, 3 | Replication tables for all primary findings | Yes (with Phase 8) |
| 10. Deep-learning variant dissection (Enformer/Borzoi/AlphaMissense + public MPRA) | Phase 2 | Composite functional evidence scores per variant | Yes (with Phases 3–9) |
| 11. Writing + internal review + bioRxiv → submission | All | Final manuscript | No |

Because the timeline is flexible, the recommended execution strategy is **do every phase thoroughly rather than trading rigor for speed**. The parallelizable columns exist so that bringing in additional collaborators (suggested below) can shorten the wall-clock time without cutting any analysis.

---

## 6. Risk mitigation

### Analytical risks
- **Coloc.susie may not converge in regions with poor LD reference.** Mitigation: use within-cohort LD where available; mark non-convergent regions clearly; report a coverage statistic.
- **MR assumptions may be violated for highly pleiotropic instruments.** Mitigation: use multiple MR methods, MR-PRESSO outlier removal, MR-CAUSE; restrict to colocalized lead variants for the cleanest causal claim.
- **Selection statistics are noisy at single loci.** Mitigation: focus on pathway-level enrichment of selection signatures, not per-locus claims; use multiple selection statistics in combination.
- **Cross-ancestry PRS may not improve under pathway restriction.** Mitigation: pre-register the hypothesis; report negative results honestly; even a null result is interesting if rigorously demonstrated.

### Resource considerations
- **Compute.** Most analyses (coloc, MR, LDSC, MAGMA, PRS-CSx) run on a standard workstation or a modest HPC allocation. Selection scans at scale (iHS/PBS/XP-EHH/SDS across 1000G + HGDP), Enformer/Borzoi/Sei inference across every credible-set variant, and PRS-CSx cross-ancestry training benefit from GPU-equipped cluster compute. NCSU HPC resources should be sufficient; budget time on a GPU partition for the deep-learning variant effect prediction phase.
- **Data access (all public or controlled-access research use).** UKB-PPP, deCODE pQTL, FinnGen, MVP, All of Us, BBJ, and Pan-UKBB require applications with weeks-to-months lead time. All are available to academic researchers under standard data use agreements; none require industry partnerships. **Apply now**, before starting Phase 2 — data access applications are the longest lead-time item in the entire plan and can run in parallel with Phases 0–1.
- **Analytical bandwidth.** The plan is intentionally parallelizable across phases so a single analyst can work on independent branches concurrently (e.g., selection scans while QTL coloc is running). The phase-dependency table in Section 5 shows which phases can run in parallel.

### Scientific integrity risks
- **Pre-register the analysis plan** on OSF before running the new analyses, to demonstrate the pipeline was not p-hacked.
- **Use a hold-out cohort** never seen during method development for the final replication.

---

## 7. Reproducibility, open science, and process controls

- All code in a single GitHub repository with semantic versioning.
- Snakemake DAG with conda envs pinned to exact versions.
- Container (Docker + Singularity/Apptainer) for the full environment.
- Zenodo DOI for the code release at submission.
- Full TableS4 and replication tables on Figshare.
- Pre-registration on OSF.
- Pre-print on bioRxiv at submission.
- Interactive Shiny browser for the per-locus results (causal gene, tissue, MR, ancestry, selection, PRS contribution).
- DataLad or git-lfs for the LD matrices and intermediate files.
- Data-use statements and accession numbers for every public dataset used (GWAS, QTL panels, single-cell atlases, ancient DNA panels, chromatin/3D datasets).

---

## 8. Solo-author execution strategy

This plan is designed to be executed as a single-author computational study under the ASHES Lab affiliation. To make a sole-author Nature Genetics submission credible to reviewers, the plan compensates for the absence of internal co-author review through rigorous process controls rather than through additional human review:

- **Pre-registration of the analysis plan on OSF** before running the new analyses, with locked primary and sensitivity analyses. This is the strongest defense against post-hoc critique for a sole-author paper.
- **Every methodological choice is tied to a published best-practice reference** (coloc.susie → Wallace 2021; MAGMA → de Leeuw 2015; LDSC-SEG → Finucane 2018; MR best practices → Burgess 2020; polygenic selection test corrections → Sohail 2019). Reviewers accept defensible choices faster than novel ones when the author is solo.
- **Multi-method triangulation at every step.** Anywhere a single method would be enough, use two or three: coloc.abf vs coloc.susie vs SuSiE-coloc triangulation; IVW + MR-Egger + weighted median + MR-PRESSO + MR-CAUSE for every MR claim; MAGMA + g:Profiler + LDSC for pathway claims; Enformer + Borzoi + Sei + AlphaMissense for variant effects. Triangulation substitutes for internal co-author QC.
- **Hold-out replication cohorts never touched during method development.** The FinnGen / GBMI / MVP / All of Us / BBJ replication in Phase 9 is the external validity check.
- **Container-pinned, Snakemake-orchestrated, GitHub-versioned pipeline** so every result is exactly reproducible on request by any reviewer. This removes the single biggest weakness of a sole-author paper: "I can't check the analysis."
- **Bio/statistical methods SOPs** written as `docs/` files in the repo, describing each phase's decisions, justifying each parameter, and recording the rejected alternatives. These become the methods section and the reviewer response document in one.
- **A public bioRxiv preprint before formal submission** to get community feedback and catch errors early.

These process controls collectively substitute for co-author review and make a sole-author submission defensible at *Nature Genetics* level.

---

## 9. Target journal positioning

**Primary target: Nature Genetics.**
- Pitch: first integrative coloc.susie + MR + cross-ancestry + selection-aware framework for cardiometabolic pleiotropy with a directly clinically actionable PRS deliverable.
- Comparable recent NG papers: Mahajan 2022 (DIAMANTE T2D), Vujkovic 2020 (T2D vascular outcomes), Hou 2023 (cross-ancestry), Mountjoy 2021 (Locus2Gene).
- The selection-aware element is the most novel cross-disciplinary hook; flag it in the cover letter.

**Fallback 1: American Journal of Human Genetics.**
- Same paper, slightly less emphasis on the methods novelty, more on the cardiometabolic genetics community.

**Fallback 2: Cell Genomics.**
- Good fit for the integrative + multi-modal angle.

**Fallback 3: Genome Medicine.**
- Best fit if the PRS / clinical translation deliverable becomes the strongest result.

---

## 10. Quick wins to do this week (regardless of long-term plan)

These are zero-regret fixes that improve the manuscript even if the full revision is delayed.

1. Regenerate `Table1_Top20_Signals.tsv` with correct sorting:
   ```bash
   awk -F'\t' 'NR==1 || $NF=="Tier1_HighConf"' TableS4_All_Results.tsv \
     | sort -t$'\t' -k9,9gr | head -21 > Table1_Top20_Signals.tsv
   ```
2. Move the header in `Table3_Pleiotropic_Loci.tsv` to row 1.
3. Reconcile "19 genes" / "20 unique" / "16/26" / "63%" / "76 signals" inconsistencies in the manuscript text.
4. Drop the KCNJ11 asthma–hypertension Tier-1 signal (n_SNPs = 6 < the stated ≥50 QC threshold) or justify the exception.
5. Reconcile "50 regions / 205 tiles" (manuscript) vs "8 seed loci / ~200 tiles" (reproducibility README).
6. Add primary citations for rs1421085/FTO/IRX3 (Claussnitzer 2015 *NEJM*), rs12740374/SORT1 (Musunuru 2010 *Nature*), and APOE-AD (Lambert 2013 *Nat Genet*).
7. Restrict Table 2 to trait pairs testable in both ancestries; drop the "Moderate" / "Exploratory" thresholds at PP.H4 < 0.5.
8. Clean `.DS_Store`, `~$` lock files, and obsolete `AJHG_files*` directories from the repo.
9. Re-order references so that citation order matches in-text appearance.
10. Add the AFR BMI (Gurdasani 2019, Ng 2017) and hypertension (Hoffmann 2017, Giri 2019) GWAS that the current draft missed — even just citing them changes the framing.

---

## 11. Key references for the revision (selected)

### Colocalization methods
- Giambartolomei C et al. (2014) *PLoS Genet* — coloc.abf
- Wallace C (2020) *PLoS Genet* — coloc prior calibration
- Wallace C (2021) *PLoS Genet* — coloc.susie
- Zou Y et al. (2022) *PLoS Genet* — SuSiE-RSS
- Foley CN et al. (2021) *Nat Commun* — coloc QC
- Hukku A et al. (2021) *AJHG* — colocalization with multiple causal variants

### Mendelian randomization
- Hemani G et al. (2018) *eLife* — TwoSampleMR
- Verbanck M et al. (2018) *Nat Genet* — MR-PRESSO
- Morrison J et al. (2020) *Nat Genet* — MR-CAUSE
- Sanderson E et al. (2019) *Int J Epidemiol* — multivariable MR
- Burgess S et al. (2020) *Eur J Epidemiol* — MR best practices
- Lawson DJ et al. (2020) *Nat Rev Genet* — MR in population genetics

### Cross-ancestry methods
- Hou K et al. (2023) *Nat Genet* — power-corrected cross-ancestry
- Atkinson EG et al. (2021) *Nat Genet* — TRACTOR
- Brown BC et al. (2016) *AJHG* — cross-ancestry rg
- Ruan Y et al. (2022) *Nat Genet* — PRS-CSx
- Martin AR et al. (2019) *Nat Genet* — PRS health disparities
- Privé F et al. (2022) *AJHG* — PRS portability
- Mahajan A et al. (2022) *Nat Genet* — DIAMANTE multi-ancestry T2D

### Pathway and heritability
- de Leeuw CA et al. (2015) *PLoS Comput Biol* — MAGMA
- Reimand J et al. (2019) *Nat Protoc* — pathway analysis best practices
- Finucane HK et al. (2015) *Nat Genet* — partitioned heritability
- Finucane HK et al. (2018) *Nat Genet* — LDSC-SEG
- Shi H et al. (2017) *AJHG* — HESS local genetic covariance
- Bulik-Sullivan B et al. (2015) *Nat Genet* — LDSC genetic correlation

### Selection and evolutionary medicine
- Voight BF et al. (2006) *PLoS Biol* — iHS
- Sabeti PC et al. (2007) *Nature* — XP-EHH
- Yi X et al. (2010) *Science* — PBS
- Field Y et al. (2016) *Science* — SDS
- Berg JJ & Coop G (2014) *PLoS Genet* — polygenic selection test
- Sohail M et al. (2019) *eLife* — UKB stratification corrections
- Speidel L et al. (2019) *Nat Genet* — Relate
- Mallick S et al. (2024) *Sci Data* — Allen Ancient DNA Resource
- Hamid I et al. (2023) *Nat Rev Genet* — polygenic selection methods review

### QTL resources
- GTEx Consortium (2020) *Science* — GTEx v8
- Sun BB et al. (2023) *Nature* — UKB-PPP plasma proteomics
- Ferkingstad E et al. (2021) *Nat Genet* — deCODE pQTL
- Yazar S et al. (2022) *Science* — OneK1K single-cell eQTL
- Mountjoy E et al. (2021) *Nat Genet* — Open Targets Locus2Gene

### Functional and cell-type prioritization
- Boix CA et al. (2021) *Nature* — EpiMap
- Fulco CP et al. (2019) *Nat Genet* — ABC model
- Nasser J et al. (2021) *Nature* — ABC enhancer-gene
- Bryois J et al. (2020) *Nat Genet* — MAGMA-celltyping
- Timshel PN et al. (2020) *eLife* — CELLECT
- Zhang MJ et al. (2022) *Nat Genet* — scDRS
- Tabula Sapiens Consortium (2022) *Science*

### Deep-learning variant effect prediction and public functional resources
- Avsec Ž et al. (2021) *Nat Methods* — Enformer
- Linder J et al. (2025) *Nat Genet* — Borzoi
- Chen KM et al. (2022) *Nat Genet* — Sei
- Cheng J et al. (2023) *Science* — AlphaMissense
- Sundaram L et al. (2018) *Nat Genet* — PrimateAI
- Abell NS et al. (2022) *Nature* — saturation MPRA in K562/HepG2 (public)
- Tewhey R et al. (2016) *Cell* — MPRA catalog (public reprocessed)
- van Arensbergen J et al. (2019) *Nat Genet* — SuRE (public)
- Gasperini M et al. (2019) *Cell* — CRISPRi enhancer screens (public)
- Liao W-W et al. (2023) *Nature* — HPRC human pangenome
- Rozowsky J et al. (2023) *Cell* — EN-TEx allele-specific chromatin
- Claussnitzer M et al. (2015) *NEJM* — FTO/IRX3 (primary citation for rs1421085)
- Musunuru K et al. (2010) *Nature* — SORT1/CELSR2 (primary citation for rs12740374)

---

## 12. The single highest-leverage change

If only one of the recommendations above can be implemented before resubmission, it should be **Phase 2: three-way colocalization of trait-trait-eQTL/pQTL using `coloc.susie`**. This single change:
- Fixes the most damaging methodological criticism (single-causal-variant assumption).
- Produces causal gene assignments that make every downstream claim more credible.
- Re-uses infrastructure already built (SuSiE fine-mapping is already running).
- Generates the headline figure for any version of the paper.
- Is the prerequisite for Phases 3, 4, 5, 8.

Phases 6 (selection scans + polygenic selection test) and 8 (cross-ancestry pathway PRS) provide the genuinely novel contributions that elevate the paper from "rigorous AJHG paper" to "Nature Genetics paper." Phase 9 (replication in FinnGen / MVP / GBMI / All of Us / BBJ) is non-negotiable for any high-impact submission. Phase 10 (deep-learning variant effect prediction + public MPRA overlap) provides the strongest computational substitute for wet-lab functional validation and keeps the paper fully computational end-to-end.

---

## 13. Final note on framing

The current draft over-promises on three things — drug target discovery, machine learning, and evolutionary medicine — and under-delivers on the one thing that would actually make the paper unique: **mechanistic resolution of pleiotropy with a quantitative cross-ancestry transferability framework**. The revision plan above re-balances the paper toward what the data and methods can defensibly support, and adds new analyses that turn promised-but-untested claims into tested hypotheses. The result is a paper that is both more honest and more impactful.

The biology is real. The pipeline is sound in skeleton. The infrastructure exists. What's needed is the methodological upgrade, the rigorous statistics, and the honest framing of what's novel versus what's confirmatory. With the plan above, this becomes a major contribution to the field.
