# Track A working source — preliminary draft (verbatim from ajhg_manu_v10.pdf)

> **This file is the pre-pivot source text, preserved verbatim from `ajhg_manu_v10.pdf`.**
> Editing this file directly is Track A's reframe. Do NOT delete content without
> promoting the replacement to `id-vs-ref-LD.md` first.
>
> **Pivot direction (2026-04-22):**
> FROM: "We identified 28 pleiotropic signals at 50 cardiometabolic loci"
> TO:   "Published cross-trait pleiotropy claims at curated cardiometabolic loci
>        are systematically inflated by identity-LD fine-mapping; we quantify
>        which survive rigorous real-LD re-analysis"
>
> See `.planning/amendments/ID-VS-REF-LD-STRATEGY.md` for the section-by-section editing plan.

---

## Title

Integrative Cross-Ancestry Colocalization and Machine Learning Identify Pleiotropic Loci and Drug Targets Across Cardiometabolic Traits

## Running title

Colocalization and ML in Cardiometabolic Traits

## Author

Carter K. Clinton¹,²,*

1. Ancestry Soil Health and Evolutionary Studies (ASHES) Laboratory, North Carolina State University, 112 Derieux Pl., Raleigh, NC 27695, USA
2. Department of Biological Sciences, North Carolina State University, 112 Derieux Pl., Raleigh, NC 27695, USA

*Correspondence: carterclinton@ncsu.edu

## Abstract

Understanding disease genetic architecture across diverse populations is essential for equitable precision medicine. We performed cross-ancestry colocalization and pathway enrichment analyses, interpreted through an evolutionary medicine framework, to identify shared causal variants among five complex traits (BMI, type 2 diabetes [T2D], hypertension, stroke, and asthma) using GWAS summary statistics from European (EUR) and African (AFR) ancestry populations. Bayesian colocalization across 50 genomic regions identified 28 high-confidence signals (PP.H4 ≥ 0.8) in EUR ancestry, with BMI-T2D showing the most extensive sharing (12 signals). Eight pleiotropic loci harbored signals across multiple trait pairs, led by KCNJ11/ABCC8 (5 pairs). Pathway enrichment revealed convergence on metabolic pathways (63% of pleiotropic genes), with ~40-fold enrichment for appetite regulation and ~13-fold for insulin signaling, consistent with evolutionary predictions regarding ancestral energy homeostasis adaptations. Machine learning–based analyses strengthened these findings: characterization of 861 failed colocalization tests confirmed that the genetic independence of asthma from cardiometabolic traits reflects biology rather than technical limitation; gene prioritization identified eight high-priority candidates including four existing drug targets (MC4R, PCSK9, KCNJ11, LEP); and variant effect prediction classified 91% of signals as regulatory. Cross-ancestry comparison was constrained by smaller AFR GWAS, though concordance at insulin signaling loci (TCF7L2, PPARG) suggests pathway conservation predating population divergence. These findings provide a pathway-level framework for understanding cardiometabolic comorbidity and highlight the imperative for diverse-ancestry genomic studies to achieve equitable precision medicine.

**Keywords:** colocalization, pleiotropy, cardiometabolic traits, cross-ancestry genetics, pathway enrichment, evolutionary medicine, GWAS, type 2 diabetes, metabolic syndrome, machine learning

## Introduction

Complex diseases rarely occur in isolation. Cardiometabolic conditions, including obesity, type 2 diabetes (T2D), hypertension, and stroke, frequently co-occur, a clustering termed metabolic syndrome.¹ Whether this comorbidity reflects shared environmental exposures, correlated lifestyle factors, or shared genetic architecture has been debated for decades.² Epidemiological evidence suggests substantial genetic overlap: approximately 50% of individuals with T2D also have hypertension, and obesity dramatically increases risk for both conditions.³ Yet the specific causal variants driving this comorbidity remain largely unknown.

An evolutionary medicine framework offers a compelling lens for understanding cardiometabolic comorbidity. The "thrifty gene" hypothesis posits that genetic variants promoting efficient energy storage were advantageous during periods of food scarcity but became detrimental in modern environments of caloric excess.⁴ If this hypothesis is correct, we would expect pleiotropic variants to cluster in evolutionarily conserved pathways related to energy homeostasis and metabolism, a prediction testable through systematic colocalization analysis. Similarly, antagonistic pleiotropy, where alleles beneficial for one trait are harmful for another, may explain unexpected connections between metabolic and inflammatory conditions.⁵

Genome-wide association studies (GWAS) have identified hundreds of loci associated with individual cardiometabolic traits.⁶⁻⁹ However, identifying pleiotropic variants is challenging due to linkage disequilibrium (LD), which can create apparent overlap between traits when distinct causal variants happen to be physically close. Statistical colocalization methods, particularly Bayesian approaches such as coloc, address this challenge by formally testing whether two traits share a single causal variant at a given locus.¹⁰ When integrated with fine-mapping to narrow credible sets and pathway enrichment to contextualize shared signals biologically, colocalization analysis can move beyond individual variant identification to reveal the biological architecture of disease comorbidity.

A critical limitation of current research is the underrepresentation of diverse ancestries in GWAS.¹¹ As of 2023, individuals of European ancestry constitute ~78% of GWAS participants despite representing ~16% of the global population.¹² This disparity has direct consequences: polygenic risk scores developed primarily in European cohorts show substantially reduced predictive accuracy in African-descended ancestry populations,¹³ and the genetic architecture of complex traits may differ across ancestries due to distinct LD patterns, allele frequencies, and selective pressures shaped by demographic history and admixture.¹⁴⁻¹⁶ African-descended populations bear a disproportionate burden of cardiometabolic disease, with African Americans experiencing 77% higher T2D prevalence and 50% higher stroke mortality compared to European Americans,²⁷ making cross-ancestry genetic characterization both a scientific and health equity priority. Conducting cross-ancestry colocalization analyses is therefore essential for understanding both the shared and ancestry-specific components of disease genetic architecture and for ensuring that genomic discoveries benefit all populations.

We hypothesized that (1) substantial pleiotropy exists among cardiometabolic traits reflecting shared biological pathways, (2) pleiotropic genes converge on evolutionarily conserved pathways related to energy homeostasis and metabolism, (3) cross-ancestry colocalization can identify both conserved and population-specific genetic architecture, and (4) systematic characterization of pleiotropic signals, including machine learning–based gene prioritization and variant mechanism classification, can identify therapeutic targets with multi-trait potential. To test these hypotheses, we performed comprehensive Bayesian colocalization analysis across five complex traits and two ancestries, integrated pathway enrichment analysis, and applied ML-based approaches to prioritize candidate genes, classify variant mechanisms, and validate the robustness of our findings.

## Subjects and Methods

### GWAS Summary Statistics

We obtained publicly available GWAS summary statistics for five traits from multiple consortia (Table S1). For European ancestry, we used: BMI from the GIANT consortium (N ≈ 700,000)⁶; T2D from DIAMANTE (N ≈ 900,000)⁷; hypertension from UK Biobank and the International Consortium of Blood Pressure (N ≈ 750,000)⁸; stroke from GIGASTROKE (N ≈ 520,000)⁹; and asthma from UK Biobank/TAGC (N ≈ 400,000). For African ancestry, we used: T2D from MEDIA/multi-ancestry GWAS; stroke from SIREN/GIGASTROKE AFR; and asthma from CAAPA. African ancestry BMI and hypertension GWAS of sufficient size were not available, limiting cross-ancestry comparison for these traits.

### Data Harmonization

Summary statistics were harmonized to GRCh37 coordinates. The asthma AFR dataset, originally on GRCh38, was converted using the UCSC liftOver tool with the hg38ToHg19 chain file, achieving 96.6% variant retention. Variants were aligned to a common reference allele, duplicates removed (167,709 duplicate variants removed from the T2D EUR dataset), and effect alleles and effect sizes harmonized. Quality control filters included removal of variants with missing effect alleles, minor allele frequency < 0.01, and ambiguous strand assignments.

### Genomic Regions

We selected 50 genomic regions previously associated with at least one of the five traits from published GWAS and fine-mapping studies.¹⁷⁻¹⁹ Regions were defined as ±500 kb from lead variants to capture surrounding LD structure. Large regions (>1 Mb) were tiled into overlapping 500 kb windows with 50 kb buffers, producing 205 analysis tiles across 50 target regions.

### Colocalization Analysis

Pairwise colocalization analysis was performed using the coloc package (v5.1) in R.¹⁰ We applied the coloc.abf() function with default priors (p1 = 1×10⁻⁴, p2 = 1×10⁻⁴, p12 = 1×10⁻⁵), which compute posterior probabilities for five mutually exclusive hypotheses: H0 (no association), H1 (association with trait A only), H2 (association with trait B only), H3 (both traits associated with different causal variants), and H4 (both traits share a single causal variant). The posterior probability of H4 (PP.H4) quantifies evidence for colocalization.

We classified colocalization signals using a tiered framework: Tier 1 (High confidence): PP.H4 ≥ 0.8; Tier 2 (Moderate): PP.H4 ≥ 0.5; Tier 3 (Suggestive): PP.H4 ≥ 0.2; Tier 4 (Exploratory): PP.H4 ≥ 0.1. Sensitivity analysis was performed with alternative priors (p12 = 10⁻⁶ and 10⁻⁴) to assess robustness.

### Fine-Mapping Integration

Fine-mapping was performed using SuSiE-RSS²⁰ with ancestry-matched LD reference panels from the 1000 Genomes Project Phase 3 (EUR N = 503; AFR N = 661). Credible sets were constructed at 95% coverage with a maximum of 10 causal variants per region. Lead variants from fine-mapping were cross-referenced with colocalization results. Fine-mapping identified 323 single-variant credible sets (EUR: 234; AFR: 89), with a median credible set size of 12 variants.

### Cross-Ancestry Concordance

Cross-ancestry concordance was assessed by comparing colocalization signals at matched genomic loci between EUR and AFR ancestries. Loci were classified as strongly concordant (EUR PP.H4 ≥ 0.5 and AFR PP.H4 ≥ 0.1), moderately concordant (EUR PP.H4 ≥ 0.5 and AFR PP.H4 ≥ 0.05), or discordant (signal in one ancestry only).

### Pleiotropy Assessment

Pleiotropic loci were defined as genomic regions showing colocalization signals (PP.H4 ≥ 0.1) across two or more trait pairs. Functional annotation was performed using publicly available databases including GTEx v8,²¹ Open Targets,²² and the NHGRI-EBI GWAS Catalog.²³

### Pathway Enrichment Analysis

We performed pathway enrichment analysis on genes harboring high-confidence colocalization signals (PP.H4 ≥ 0.8) to characterize the biological mechanisms underlying shared genetic architecture. Genes were mapped to established pathway databases: KEGG,³⁴ Reactome,³⁵ and Gene Ontology (GO) biological processes.³⁶ Genes were grouped into functional categories, and fold enrichment was calculated as the ratio of observed to expected gene counts in each pathway category, with expected counts derived from the proportion of genes genome-wide assigned to each pathway.

### Machine Learning–Based Enhancement

To strengthen biological interpretation, we applied four complementary ML-based approaches to the colocalization results.

*Error characterization.* Of 1,446 colocalization tests attempted, 861 returned errors (COLOC_ERROR). We characterized the distribution of these errors across trait pairs to assess potential bias. Error rates were compared against successful tests for the same trait pairs, and the expected number of missed high-confidence signals was estimated using a binomial model based on per-pair success rates.

*Cross-ancestry validation.* For loci with colocalization results in both ancestries, we classified signals as concordant (both ancestries showing similar evidence), AFR-enriched (AFR signal without EUR counterpart), or power-limited (insufficient AFR statistical power). This analysis quantified the extent to which absent AFR signals reflected statistical power limitations versus genuine biological differences.

*Gene prioritization.* Candidate genes at colocalization loci were ranked using a multi-feature scoring framework incorporating disease relevance (OMIM/ClinVar associations;³⁷ 30% weight), tissue expression specificity (GTEx;²¹ 20%), druggability (ChEMBL/DGIdb; 15%), gene constraint (gnomAD pLI; 15%), biological plausibility (pathway coherence; 10%), and protein-protein interaction connectivity (STRING; 10%). Genes scoring ≥ 0.5 were classified as high priority.

*Variant effect prediction.* Lead variants at colocalization loci were classified by their likely functional mechanism using CADD scores,³⁸ regulatory annotations (Roadmap Epigenomics,³⁹ ENCODE), coding consequence predictions (PolyPhen-2,⁴⁰ SIFT⁴¹), and eQTL evidence (GTEx²¹). Variants were assigned to regulatory (eQTL/enhancer), coding (missense/loss-of-function), or mixed mechanism categories.

### Quality Control

All analyses included stringent quality control measures. Colocalization tests required a minimum of 50 overlapping variants between datasets. Regions with insufficient LD information or poor LD matrix conditioning were excluded. Cross-ancestry comparisons accounted for differences in sample sizes (EUR: N = 400K–1.3M; AFR: N = 20K–100K) and LD structure.

### Software and Data Availability

Analyses were performed using R v4.x with coloc v5.1 and susieR v0.12. LD matrices were computed from 1000 Genomes Phase 3 reference panels. Python (v3.x) with scikit-learn, pandas, and NumPy was used for ML-based analyses. Analysis code is available at https://github.com/The-ASHES-Laboratory/colocalization-ml-analysis. Summary statistics were stored in tabix-indexed bgzip-compressed files for efficient regional queries.

### Ethics Statement

This study used only publicly available, de-identified GWAS summary statistics. No individual-level data were accessed. All source studies obtained appropriate institutional review board approval and informed consent from participants as described in their respective publications.

## Results

### Overview of Colocalization Analysis

We performed 585 pairwise colocalization tests across 50 genomic regions in European (EUR, N = 441 pairs) and African (AFR, N = 144 pairs) ancestries (Figure 1A, Figure S1). In EUR ancestry, we identified 28 high-confidence colocalization signals (PP.H4 ≥ 0.8) and 34 at the moderate threshold (PP.H4 ≥ 0.5), indicating extensive shared genetic architecture among cardiometabolic traits. In AFR ancestry, no signals reached the high-confidence threshold and only one reached the exploratory threshold (PP.H4 ≥ 0.1), reflecting the substantially smaller GWAS sample sizes.

An additional 861 colocalization tests returned computational errors. ML-based characterization revealed that 849 of these errors (98.6%) involved asthma pairs, and successful tests for these same pairs showed minimal colocalization (mean PP.H4 = 0.02). The expected number of missed high-confidence signals among the failed tests was less than one (estimated 0.9), confirming that the errors did not bias our primary findings. Importantly, this analysis demonstrated that the genetic independence of asthma from most cardiometabolic traits represents a genuine biological finding rather than a methodological limitation.

### Trait Pair Distribution of Colocalization Signals

The distribution of high-confidence signals across trait pairs revealed strong clustering around metabolic traits (Figure 1B, Figure S2). BMI-T2D showed the most extensive genetic sharing, with 12 high-confidence signals (43% of total), followed by hypertension-T2D (4 signals) and both asthma-BMI and asthma-T2D (3 signals each). BMI-stroke and hypertension-stroke each showed 2 signals, while stroke-T2D and asthma-hypertension each showed 1 signal. No signals were detected for asthma-stroke.

Asthma, traditionally considered distinct from cardiometabolic conditions, showed unexpected genetic overlap with metabolic traits through three specific loci: NEGR1 (appetite regulation), FTO (obesity), and FADS1 (fatty acid metabolism). These connections, discussed further below, may provide mechanistic insight into the epidemiologically observed obesity-asthma relationship.²⁴

### Top Colocalization Signals

The 20 strongest colocalization signals are presented in Table 1. TCF7L2, a well-established T2D locus, showed complete colocalization for BMI-T2D (PP.H4 = 1.00), indicating the same causal variant influences both traits at this locus (Figure 2A). SH2B3 showed near-complete colocalization for both BMI-stroke (PP.H4 = 1.00) and hypertension-stroke (PP.H4 = 0.96), consistent with its known role in inflammatory signaling linking metabolic and cardiovascular disease.

GCKR, encoding glucokinase regulatory protein, showed near-complete colocalization for BMI-T2D (PP.H4 = 0.999), reflecting its central role in hepatic glucose metabolism. Similarly, APOE demonstrated strong BMI-T2D colocalization (PP.H4 = 0.999) and asthma-BMI colocalization (PP.H4 = 0.950), extending its pleiotropic effects beyond the well-characterized lipid and Alzheimer's disease associations³¹ to broader cardiometabolic and respiratory trait pleiotropy.

To assess robustness, we performed sensitivity analysis using alternative prior specifications (p12 = 10⁻⁶ and 10⁻⁴). Of the 28 high-confidence signals, 26 (93%) remained above the PP.H4 ≥ 0.8 threshold across all priors, and all 28 remained above 0.5 (Table S5).

### Pleiotropic Loci

Eight genomic loci exhibited colocalization signals (PP.H4 ≥ 0.8) across two or more trait pairs, meeting our definition of high-confidence pleiotropic loci (Figure 2B, Table S3). The most extensively pleiotropic locus was KCNJ11/ABCC8 at 11p15, showing signals across five trait pairs spanning stroke-T2D (PP.H4 = 0.97), BMI-T2D (0.95), hypertension-T2D (0.91), asthma-hypertension (0.87), and BMI-stroke (0.85). KCNJ11 and ABCC8 encode ATP-sensitive potassium channel subunits that regulate insulin secretion in pancreatic β-cells and function in vascular and airway smooth muscle, providing a molecular basis for their broad pleiotropy.

Other notable pleiotropic loci included NEGR1 at 1p31.1 (3 trait pairs: asthma-T2D, asthma-BMI, BMI-T2D), APOE at 19q13 (2 pairs), FTO at 16q12 (2 pairs), MC4R at 18q21 (2 pairs), SH2B3 at 12q24 (2 pairs), PPARG at 3p25 (2 pairs), and SEC16B at 1q25.2 (2 pairs). FADS1 at 11q12 was pleiotropic for 4 trait pairs, consistent with its role in fatty acid metabolism affecting multiple cardiometabolic and respiratory pathways. Novel pleiotropic discoveries included NEGR1 and TMEM18, both with established BMI associations but newly identified connections to asthma and T2D (Figure 3, Figure S3, Figure S4).²⁵

### Pathway Enrichment Analysis

To understand the biological architecture of cardiometabolic pleiotropy, we performed systematic pathway enrichment analysis on the 19 genes harboring high-confidence colocalization signals (Figure 4A and B, Figure S5, Figure S6).

*Metabolic pathway dominance.* Strikingly, 63% of pleiotropic gene annotations (16/26) mapped to metabolic pathways, far exceeding chance expectation and providing strong evidence that cardiometabolic comorbidity reflects shared metabolic etiology rather than coincidental genetic overlap.

*Appetite regulation pathway (~40-fold enrichment).* The most enriched pathway was appetite regulation, with four genes (MC4R, BDNF, NEGR1, FTO) showing ~40-fold enrichment. These genes operate through hypothalamic energy balance circuits: MC4R controls satiety signaling, FTO modulates IRX3/IRX5 expression affecting adipocyte thermogenesis, and NEGR1 regulates neuronal growth factor signaling. Their colocalization across BMI-T2D and BMI-hypertension pairs suggests that central appetite dysregulation is a primary genetic driver of metabolic syndrome.

*Insulin signaling pathway (~13-fold enrichment).* Four genes (IRS1, PPARG, KCNJ11, ABCC8) converged on insulin signaling. Critically, these genes link all three core metabolic traits: IRS1 colocalized for hypertension-T2D, PPARG for hypertension-T2D and BMI-T2D, and KCNJ11/ABCC8 across five trait pairs. This convergence provides genetic evidence that insulin resistance is a central mechanism driving metabolic syndrome comorbidity, consistent with longstanding clinical observations.²⁶

*Glucose metabolism (~13-fold enrichment).* GCKR and TCF7L2 showed strong enrichment for glucose metabolism. GCKR regulates hepatic glucokinase activity, while TCF7L2 controls insulin gene transcription through Wnt signaling, the latter showing perfect colocalization (PP.H4 = 1.00) for BMI-T2D.

*Fatty acid metabolism (~10-fold enrichment).* FADS1 and FADS2 encode fatty acid desaturases that showed colocalization for both T2D and asthma. This pathway finding provides a mechanistic hypothesis for the epidemiologically observed obesity-asthma connection: altered polyunsaturated fatty acid (PUFA) synthesis may simultaneously affect metabolic regulation and inflammatory airway responses.

### Variant Mechanism Classification

ML-based variant effect prediction revealed that the vast majority of colocalization signals (91%, 69/76) operate through regulatory mechanisms, with only 8% (6 signals) having likely coding effects and 1% mixed (Figure 5A). Among the coding variants, the strongest signals were MC4R (CADD = 28.0; missense variants V103I and I251L affecting receptor function), PCSK9 (CADD = 27.0; loss-of-function variants reducing LDL receptor degradation), SLC39A8 (CADD = 25.0; A391T affecting metal transport), and SH2B3 (CADD = 21.0; R262W affecting JAK-STAT signaling). The most prominent regulatory variants included FTO (rs1421085, disrupting an IRX3/IRX5 enhancer), TCF7L2 (rs7903146, altering a beta cell enhancer), and SORT1 (rs12740374, affecting a C/EBP binding site).

The predominance of regulatory mechanisms indicates that most pleiotropic effects operate through gene expression changes in specific tissues, with implications for functional follow-up studies. Enhancer assays and tissue-specific eQTL analyses should be prioritized over protein biochemistry for the majority of loci, while the six coding signals (MC4R, PCSK9, SLC39A8, ABCC8, SH2B3, APOE) have more direct therapeutic paths.

### Gene Prioritization and Therapeutic Targets

ML-based gene prioritization ranked candidate genes using an integrated scoring framework (Figure 5B, Table 2). Eight genes achieved high-priority scores (≥ 0.5), led by KCNJ11 (0.908), TCF7L2 (0.819), LEP (0.816), and PCSK9 (0.787). Among the high-priority genes, four represent existing drug targets with potential for therapeutic expansion beyond current indications: MC4R (setmelanotide, FDA-approved for genetic obesity; colocalized across BMI-T2D with PP.H4 = 0.999), PCSK9 (evolocumab/alirocumab; colocalized across BMI-hypertension with PP.H4 = 0.920), KCNJ11 (sulfonylureas; colocalized across 5 trait pairs), and LEP (metreleptin; BMI-T2D PP.H4 = 0.965).

Seven loci formed a "metabolic syndrome hub" showing colocalization signals linking hypertension to T2D: IRS1 (PP.H4 = 0.96), MC4R (0.95), KCNJ11/ABCC8 (0.91), PPARG (0.68), SH2B3 (0.68), FTO (0.53), and NEGR1 (0.40). These hub loci converge on two interconnected pathways: insulin signaling (IRS1, PPARG, KCNJ11/ABCC8) and appetite regulation (MC4R, FTO, NEGR1), representing the convergence point where obesity genetics meets diabetes genetics. This pathway architecture suggests that therapies targeting these hubs could provide multi-trait benefit rather than single-disease treatment.

### Cross-Ancestry Comparison

Cross-ancestry comparison revealed limited concordance between EUR and AFR colocalization signals, with only two loci showing evidence in both ancestries. TCF7L2 demonstrated strong concordance (EUR PP.H4 = 1.00 for BMI-T2D; AFR PP.H4 = 0.15 for stroke-T2D), and PPARG showed exploratory-level concordance (EUR PP.H4 = 0.68 for hypertension-T2D; AFR PP.H4 = 0.06).

Notably, both concordant loci belong to the insulin signaling/glucose metabolism pathway cluster, suggesting that this pathway may be conserved across ancestries, a hypothesis that requires validation in larger diverse-ancestry cohorts. The remaining 48 loci were classified as discordant, showing strong EUR signals without detectable AFR counterparts.

ML-based cross-ancestry validation provided critical insight into the nature of this discordance. The strongest EUR colocalization signals (BMI-T2D: 12 signals; BMI-hypertension: 4 signals) could not be tested in AFR due to the absence of adequately powered African-ancestry BMI and hypertension GWAS. Among the testable AFR pairs (limited to T2D-stroke, T2D-asthma, and stroke-asthma), 98.5% showed concordant null results, meaning neither ancestry showed colocalization at these loci. Seven loci showed AFR-enriched signals, most notably in the MHC region (chr6: 16–36 Mb) for T2D-stroke (AFR PP.H4 = 0.54 vs. EUR PP.H4 = 0.02), consistent with known population-specific HLA effects.

This analysis demonstrates that the absence of AFR signals for the primary findings reflects the unavailability of large-scale African-ancestry GWAS for BMI and hypertension (a data gap) rather than a biological absence of shared genetic architecture. The concordant null results for testable pairs support the interpretation that shared biology exists but remains statistically undetectable given current sample sizes, reinforcing the imperative for investment in diverse-ancestry GWAS.

## Discussion

We present a comprehensive cross-ancestry colocalization and pathway enrichment analysis, enhanced by machine learning–based gene prioritization and variant classification, that advances our understanding of the genetic architecture underlying cardiometabolic disease comorbidity. The identification of 28 high-confidence colocalization signals, 8 pleiotropic hubs, convergence on metabolic pathways (63% of pleiotropic genes), and 4 existing drug targets at pleiotropic loci provides both biological insight and translational opportunities.

### Metabolic Syndrome as a Pathway-Defined Genetic Entity

The most striking finding is that 63% of pleiotropic genes converge on metabolic pathways, a distribution far exceeding chance expectation. This pathway-level convergence transforms our understanding of metabolic syndrome from a clinical clustering of correlated risk factors to a genetically defined entity rooted in shared biological mechanisms. Rather than being merely a convenient clinical label, metabolic syndrome emerges from our data as a condition with coherent pathway architecture.

The ~13-fold enrichment for insulin signaling genes (IRS1, PPARG, KCNJ11, ABCC8) is particularly illuminating. These genes do not merely associate with T2D; they simultaneously colocalize with hypertension and BMI traits, providing direct genetic evidence for the insulin resistance hypothesis of metabolic syndrome.²⁶ That KCNJ11/ABCC8 shows colocalization across five trait pairs, including asthma-hypertension, suggests the ATP-sensitive potassium channel has broader physiological effects than previously appreciated, extending from β-cell insulin secretion to vascular and airway smooth muscle function.

The ~40-fold enrichment for appetite regulation genes (MC4R, BDNF, NEGR1, FTO) reveals a second pathway hub operating through central nervous system mechanisms. These genes regulate hypothalamic energy balance, and their pleiotropic effects across BMI, T2D, and hypertension suggest that central appetite dysregulation propagates peripheral metabolic consequences through multiple downstream pathways.

### Novel Pathway Discovery: The Asthma-Metabolic Axis

Perhaps the most unexpected finding is the ~10-fold enrichment for fatty acid metabolism genes (FADS1, FADS2) linking T2D and asthma. This pathway connection provides a mechanistic hypothesis for the frequently observed but poorly understood obesity-asthma relationship.²⁴ FADS1 and FADS2 catalyze the desaturation of omega-3 and omega-6 fatty acids, and genetic variants affecting their activity could simultaneously alter metabolic regulation (through effects on insulin sensitivity and lipid metabolism) and airway inflammation (through altered prostaglandin and leukotriene synthesis). This finding suggests that altered PUFA metabolism may create shared susceptibility—a novel direction that omega-3 supplementation or FADS modulation therapies could potentially address.

Our ML-based error characterization reinforced this finding: the near-absence of asthma colocalization signals with cardiometabolic traits (mean PP.H4 = 0.02 for successful asthma tests) was confirmed as biological, not technical. The three exceptions (NEGR1, FTO, and FADS1) are metabolic genes that happen to influence both pathways, supporting the interpretation that asthma-metabolic overlap is mediated by specific shared metabolic mechanisms rather than broad genetic correlation.

### Variant Mechanisms and Therapeutic Implications

The classification of 91% of colocalization signals as regulatory has important implications for both biological understanding and drug development. Most pleiotropic effects operate through tissue-specific gene expression changes rather than altered protein function, suggesting that the same variant may have different consequences in different tissues, producing obesity through hypothalamic effects, T2D through pancreatic effects, and hypertension through vascular effects. This mechanism could explain why pleiotropic variants tend to cluster in genes with broad tissue expression and regulatory complexity.

The convergence of colocalization signals on existing drug targets offers translational opportunities. MC4R, targeted by setmelanotide for genetic obesity, showed high-confidence colocalization across BMI-T2D (PP.H4 = 0.999), suggesting potential metabolic benefits beyond weight reduction. PCSK9 colocalization across metabolic traits supports cardiovascular benefits of LDL lowering that extend beyond lipid effects alone. The ML-prioritized drug targets, combined with variant mechanism classification, provide a framework for rational drug repurposing: coding variants at MC4R and PCSK9 suggest direct protein targeting, while regulatory variants at TCF7L2 and FTO suggest tissue-specific expression modulation strategies.

The identification of pathway hubs enables three therapeutic strategies. First, indication expansion for existing drugs: sulfonylureas (KCNJ11) and thiazolidinediones (PPARG) may have underappreciated effects on hypertension and cardiovascular outcomes through their pathway connections. Second, pathway-targeted development: the ~40-fold enrichment for appetite regulation suggests this pathway as a high-priority target, with MC4R agonists potentially expandable beyond rare genetic obesity. Third, novel pathway therapeutics: the fatty acid metabolism connection between T2D and asthma suggests that FADS-targeted or PUFA-modulating therapies could provide dual metabolic-respiratory benefit.

### Evolutionary Medicine Perspective

Our pathway findings align remarkably with predictions from evolutionary medicine. The dominance of appetite regulation, insulin signaling, and fatty acid metabolism among pleiotropic genes reflects core systems for energy acquisition, storage, and utilization—the fundamental challenges faced by organisms throughout evolutionary history. The thrifty gene hypothesis predicts exactly this pattern: variants promoting appetite and efficient energy storage would have been advantageous during the food uncertainty characterizing most of human evolution but become pathogenic in modern environments of caloric abundance and physical inactivity.⁴

The FADS1/2 connection between T2D and asthma may reflect antagonistic pleiotropy, where alleles optimizing metabolic efficiency compromise inflammatory regulation.⁵ Such evolutionary trade-offs may partially explain why metabolic syndrome persists at high population frequencies despite its clear health costs; the component alleles were individually advantageous in ancestral environments.

Cross-ancestry concordance at insulin signaling genes (TCF7L2, PPARG) suggests these pathways were under selection before human populations diverged. However, population-specific adaptation following the out-of-Africa migration, combined with differential selective pressures related to diet, climate, and pathogen exposure, may have shaped distinct allele frequency profiles at these loci, a hypothesis our data support but cannot definitively test with current AFR GWAS power.

### Cross-Ancestry Pathway Conservation and Health Equity

A critical finding with profound implications for health equity is the differential power to characterize pathway biology across ancestries. In EUR populations, we comprehensively mapped the pathway architecture of cardiometabolic pleiotropy: insulin signaling, appetite regulation, glucose metabolism, and fatty acid metabolism. In AFR populations, we could only detect suggestive signals at two insulin signaling loci.

Our ML-based cross-ancestry analysis provides essential nuance to this disparity. The primary limitation is not biological absence but data absence: the strongest EUR signals (BMI-T2D, BMI-hypertension) could not be tested in AFR because adequately powered BMI and hypertension GWAS simply do not exist for African-ancestry populations. Among trait pairs testable in both ancestries, the concordant null results (98.5%) support shared underlying biology rather than ancestral differences in genetic architecture. The seven AFR-enriched signals, particularly the MHC region signal for T2D-stroke, hint at population-specific effects that warrant follow-up as larger diverse-ancestry datasets become available.

The stark power disparity (EUR N = 400K–1.3M; AFR N = 20K–100K, with a 65-fold difference for stroke) reflects systemic underinvestment in diverse genomics research. African Americans bear 77% higher T2D rates and 50% higher stroke mortality than European Americans,²⁷ yet the GWAS data needed to characterize the genetic architecture of these conditions in this population remain insufficient. Achieving equitable precision medicine requires not only identifying shared genetic architecture but also characterizing population-specific pathway biology that may be clinically relevant for disease prevention and treatment.

### Strengths, Limitations, and Future Directions

Strengths of our study include the integrated colocalization-pathway-ML approach, systematic analysis across multiple traits and ancestries, rigorous quality control including ML-based error characterization, gene prioritization using multi-feature scoring, and variant mechanism classification that informs therapeutic strategy. The confirmation that 861 computational errors did not bias our findings provides an important quality assurance that is rarely reported in colocalization studies.

Limitations include reliance on summary statistics rather than individual-level data, substantially smaller AFR GWAS sample sizes limiting cross-ancestry pathway comparison, the single causal variant assumption of coloc (which may miss loci with multiple independent signals), restriction of pathway enrichment to well-annotated genes, and the inability to establish causal directionality between traits. Gene prioritization was limited to genes in our curated database (16% of signals were matched), representing a conservative but rigorous annotation approach. Cross-ancestry replication of the primary BMI-T2D and BMI-hypertension signals remains untested due to unavailable African-ancestry GWAS for these traits.

Future directions should prioritize: (1) large-scale diverse-ancestry GWAS enabling pathway characterization across populations, particularly for BMI and hypertension in African-ancestry cohorts; (2) functional validation of pathway connections through cellular and animal models, prioritizing enhancer assays for the 91% of signals classified as regulatory; (3) Mendelian randomization to establish causal relationships between colocalized traits; (4) single-cell studies at pleiotropic loci to resolve tissue-specific regulatory mechanisms; and (5) clinical trials exploring indication expansion for drugs targeting pleiotropic hubs.

## Conclusion

The genetic architecture of cardiometabolic comorbidity, as delineated here, implicates evolutionarily ancient systems governing energy homeostasis as the molecular substrate of metabolic syndrome. The convergence of pleiotropic genes on appetite regulation, insulin signaling, and fatty acid metabolism establishes that this shared architecture is embedded within pathways under strong selective constraint. Cross-ancestry concordance at insulin signaling loci, TCF7L2 and PPARG, is consistent with conservation of pathway architecture predating population divergence, an interpretation supported by the deep evolutionary conservation of insulin signaling across vertebrate lineages but requiring validation through haplotype-level analyses in whole-genome sequencing data from diverse populations. If the genetic substrates governing insulin sensitivity, glucose homeostasis, and energy storage are fundamentally conserved, as comparative genomic evidence and the present data jointly suggest, then the marked disparities in cardiometabolic disease burden borne by African-descended populations are unlikely to be principally attributable to differences in underlying pathway biology. Rather, these disparities implicate environmental, behavioral, and structural determinants, including caloric excess coupled with food insecurity, reduced access to preventive care and chronic psychosocial stress. To the extent that pathway conservation holds, it sharpens the case for non-genetic causation.

Several advances would strengthen this framework: whole-genome sequencing in diverse cohorts to resolve fine-mapping limitations inherent to array-based GWAS, particularly where shorter African-ancestry linkage disequilibrium blocks demand denser variant coverage; multi-ancestry colocalization at scale to determine whether European-ancestry pleiotropic hubs are fully conserved, partially shared, or supplemented by population-specific loci; and functional validation of immune and metabolic pathway connections through cellular assay systems. Work currently underway at the Ancestry, Soil, Health, and Evolutionary Studies (ASHES) Laboratory is implementing whole-genome sequencing and functional assay approaches in diverse cohorts to address these gaps directly. In parallel, clinical investigation of indication expansion for drugs targeting pleiotropic hubs, particularly MC4R agonists, PCSK9 inhibitors, sulfonylureas, and leptin analogs, should be evaluated in diverse patient populations to ensure that multi-trait therapeutic strategies do not recapitulate the ancestry biases of existing genomic research.

Ultimately, the convergence of pleiotropic signals on conserved metabolic pathways suggests that the biology of cardiometabolic disease is largely shared across human populations. That the burden is not similarly shared implicates the environments in which that biology operates—a gap that extends well beyond African-descended populations to the global majority. Equitable precision medicine demands investment not only in diverse genomics but in integrating social and environmental determinants into risk models, and in addressing the structural conditions that convert shared genetic susceptibility into inequitable disease outcomes.

## Tables

### Table 1. Top 20 high-confidence colocalization signals in European ancestry.

| Rank | Locus | Trait Pair | PP.H4 | Gene | Lead Variant (PIP) | Pathway |
|---|---|---|---|---|---|---|
| 1 | 10q25 | BMI-T2D | 1.000 | TCF7L2 | rs7903146 (0.998) | Glucose metabolism |
| 2 | 12q24 | BMI-Stroke | 1.000 | SH2B3 | rs3184504 (0.995) | Inflammation |
| 3 | 5q13.3 | BMI-T2D | 1.000 | Novel | — | Metabolic |
| 4 | 2p23.3 | BMI-T2D | 0.999 | GCKR | rs1260326 (0.992) | Glucose metabolism |
| 5 | 19q13 | BMI-T2D | 0.999 | APOE | — | Lipid transport |
| 6 | 1q25.2 | BMI-T2D | 0.992 | SEC16B | — | ER-Golgi transport |
| 7 | 6q25.3 | BMI-T2D | 0.990 | LPA | — | Lipoprotein(a) |
| 8 | 16p12.3 | BMI-T2D | 0.971 | GPRC5B | — | Metabolic |
| 9 | 1p31.1 | Asthma-T2D | 0.967 | NEGR1 | — | Appetite regulation |
| 10 | 11p15 | Stroke-T2D | 0.966 | KCNJ11 | — | Insulin signaling |
| 11 | 18q21 | BMI-T2D | 0.966 | MC4R | rs17782313 (0.976) | Appetite regulation |
| 12 | 16q12 | Asthma-T2D | 0.962 | FTO | rs9939609 (0.987) | Appetite regulation |
| 13 | 2q36 | HTN-T2D | 0.960 | IRS1 | — | Insulin signaling |
| 14 | 12q24 | HTN-Stroke | 0.955 | SH2B3 | rs3184504 (0.995) | Inflammation |
| 15 | 18q21 | HTN-T2D | 0.952 | MC4R | rs17782313 (0.976) | Appetite regulation |
| 16 | 19q13 | Asthma-BMI | 0.950 | APOE | — | Lipid transport |
| 17 | 11p15 | BMI-T2D | 0.948 | KCNJ11 | — | Insulin signaling |
| 18 | 2p25 | BMI-T2D | 0.926 | TMEM18 | — | Adipogenesis |
| 19 | 11q12 | Asthma-T2D | 0.918 | FADS1 | — | Fatty acid metabolism |
| 20 | 1p31.1 | Asthma-BMI | 0.913 | NEGR1 | — | Appetite regulation |

PP.H4, posterior probability of shared causal variant; PIP, posterior inclusion probability from SuSiE fine-mapping; HTN, hypertension; T2D, type 2 diabetes. Full results in Table S4.

### Table 2. ML-prioritized genes and therapeutic targets at pleiotropic loci.

| Gene | Priority Score | Trait Pairs (PP.H4) | Variant Mechanism | Drug Target | Drug/Class | Pathway |
|---|---|---|---|---|---|---|
| KCNJ11 | 0.908 | BMI-T2D (0.95), Stroke-T2D (0.97), HTN-T2D (0.91), Asthma-HTN (0.87), BMI-Stroke (0.85) | Coding (CADD 24) | Yes | Sulfonylureas | Insulin signaling |
| TCF7L2 | 0.819 | BMI-T2D (1.00) | Regulatory (enhancer) | — | — | Wnt/Glucose metabolism |
| LEP | 0.816 | BMI-T2D (0.97) | Regulatory (eQTL) | Yes | Metreleptin | Appetite regulation |
| PCSK9 | 0.787 | BMI-HTN (0.92) | Coding (CADD 27) | Yes | Evolocumab, Alirocumab | Cholesterol metabolism |
| IRS1 | 0.781 | HTN-T2D (0.96) | Regulatory (eQTL) | — | — | Insulin signaling |
| SH2B3 | 0.676 | BMI-Stroke (1.00), HTN-Stroke (0.96) | Coding (R262W, CADD 21) | — | — | JAK-STAT/Inflammation |
| MC4R | 0.669 | BMI-T2D (1.00), HTN-T2D (0.95) | Coding (V103I, CADD 28) | Yes | Setmelanotide | Appetite regulation |
| SORT1 | 0.552 | BMI-HTN (0.99) | Regulatory (C/EBP site) | — | — | Lipid transport |

Priority scores integrate disease relevance (30%), tissue expression (20%), druggability (15%), gene constraint (15%), biological plausibility (10%), and PPI connectivity (10%). CADD, Combined Annotation Dependent Depletion score; HTN, hypertension; T2D, type 2 diabetes; eQTL, expression quantitative trait locus; PPI, protein-protein interaction.

## Figure Legends (preserved for reference)

**Figure 1.** Top colocalization signals and regional association evidence. (A) Lollipop plot showing PP.H4 values for the 20 strongest colocalization signals in European ancestry, colored by trait pair. TCF7L2 (BMI–T2D) shows complete colocalization (PP.H4 = 1.00). Dashed line indicates the high-confidence threshold (PP.H4 = 0.8). (B) Regional association plots (LocusZoom) at the four strongest colocalization loci: TCF7L2 (BMI–T2D, PP.H4 = 1.00), SH2B3 (BMI–Stroke, PP.H4 = 0.9996), GCKR (BMI–T2D, PP.H4 = 0.9994), and IRS1 (Hypertension–T2D, PP.H4 = 0.96). Each panel shows -log10(P) for both traits, with lead variants in purple. Linkage disequilibrium (r²) is color-coded from navy (0.0–0.2) to red (0.8–1.0). Overlapping peak positions confirm shared causal variants.

**Figure 2.** Pleiotropic loci spanning multiple trait pairs. Horizontal bar chart showing genomic loci with high-confidence colocalization signals (PP.H4 ≥ 0.8) across two or more trait pairs. Bars are stacked by ancestry: European (blue) and African (orange). KCNJ11/ABCC8 (11p15) shows the broadest pleiotropy (7 trait pairs), followed by FADS1 (11q12, 4 pairs). Gene symbols with chromosomal locations are indicated. TCF7L2 (10q25) is the only locus with African-ancestry evidence.

**Figure 3.** Gene–trait colocalization network. Bubble chart showing PP.H4 values for 14 pleiotropic genes across 5 disease traits. Bubble size corresponds to PP.H4 magnitude, and color indicates biological pathway assignment (Adipogenesis, Appetite, Fatty acid, Glucose, Inflammation, Insulin, Lipid, Wnt/Insulin). MC4R, NEGR1, and TCF7L2 show the broadest trait involvement, with colocalization signals spanning BMI, hypertension, and T2D. Insulin-related genes (IRS1, KCNJ11, PPARG, TCF7L2) cluster around hypertension and T2D, supporting the metabolic syndrome hub identified in the main analysis.

**Figure 4.** Pathway enrichment analysis of pleiotropic genes. (A) Pathway category distribution showing the number of colocalization genes per biological category. Metabolic pathways dominate (n = 15 genes, 63%), followed by Lipid (n = 4), Immune (n = 3), and Cardiovascular (n = 2). (B) Fold enrichment for specific biological pathways relative to genome-wide expectation. Appetite regulation shows the strongest enrichment (~40-fold), followed by insulin signaling and glucose metabolism (~13-fold each), lipid metabolism (~10-fold), and inflammation (~6-fold). Gene counts per pathway are annotated.

**Figure 5.** Variant mechanism classification and gene prioritization. (A) Donut chart showing the distribution of variant mechanisms among 76 colocalization signals: 91% regulatory (eQTL/enhancer disruption), 8% coding (missense/loss-of-function), and 1% mixed. Inset lists the top coding variants with CADD scores: MC4R (28.0), PCSK9 (27.0), SLC39A8 (25.0), SH2B3 (21.0). (B) ML-based gene priority scores for the top 10 ranked candidate genes. Scores integrate disease relevance, tissue expression, druggability, gene constraint, and biological plausibility. Stars (*) indicate existing drug targets (KCNJ11/sulfonylureas, LEP/metreleptin, PCSK9/evolocumab, MC4R/setmelanotide). Dashed line indicates the high-priority threshold (score ≥ 0.5).
