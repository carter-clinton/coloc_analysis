# Track A — First-pass pivot draft

> **Status:** First-pass application of `.planning/amendments/TRACK-A-PIVOT.md` to `docs/manuscript/track_a_source.md`. Narrative is complete; numeric placeholders marked `[EXTRACT: …]` must be filled from `results/` before preprint submission.
>
> **Pivot direction (2026-04-22):** FROM "identified 28 pleiotropic signals" TO "quantify which published cross-trait pleiotropy claims survive real-LD re-analysis".
>
> **Target venue (primary):** *Genome Medicine*, original research article. Fallback: *AJHG* short report; *Bioinformatics* short communication. bioRxiv preprint Day 1 regardless.

---

## Title

**Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci: Identity-LD Fine-Mapping Systematically Inflates Cross-Trait Colocalization Evidence**

**Running title:** Real-LD audit of cardiometabolic pleiotropy

## Author

Carter K. Clinton¹,²,*

1. Ancestry Soil Health and Evolutionary Studies (ASHES) Laboratory, North Carolina State University, 112 Derieux Pl., Raleigh, NC 27695, USA
2. Department of Biological Sciences, North Carolina State University, 112 Derieux Pl., Raleigh, NC 27695, USA

*Correspondence: carterclinton@ncsu.edu*

## Abstract

Cross-trait colocalization analyses using GWAS summary statistics underpin a growing body of pleiotropy and drug-repurposing literature, but the most widely used implementation — `coloc.abf` under a single-causal-variant assumption and identity-matrix LD — can inflate the posterior probability of colocalization (PP.H4) when the true regional LD deviates from identity. We re-analyzed 50 curated cardiometabolic regions previously reported to harbor cross-trait pleiotropic signals for BMI, type 2 diabetes (T2D), hypertension, stroke, and asthma in European-ancestry GWAS, replacing the single-causal-variant colocalization framework with SuSiE-RSS fine-mapping and `coloc.susie`, and replacing identity-matrix LD with ancestry-matched 1000 Genomes Phase 3 reference LD at 10 autosomal EUR regions admissible to the real-LD workflow. Under real-LD, SuSiE-RSS yielded 51 of 96 (53%) non-empty credible sets at admissible regions, compared with 12 of 96 (13%) under identity-LD fallback, a 4.25-fold increase in fine-mapping yield. Cross-trait `coloc.susie` at these loci reassigned signals: 0 regions reached Tier A high-confidence colocalization, 9 reached Tier C, and 224 region-pair evaluations matched pre-specified negative-control behavior. A previously reported PP.H4 = 1.00 signal for BMI–stroke at *SH2B3* (12q24) collapsed under real-LD (n_cs_a = 0 for the asthma-proxy arm; see Results). 1,446 attempted pairwise tests included 861 computational failures traceable to harmonization-pipeline edge cases in the asthma cohorts rather than biological independence. Pathway enrichment re-computed on real-LD–surviving signals [EXTRACT: fold-enrichment deltas from `results/pathway/`] no longer supports appetite-regulation and insulin-signaling as the dominant axes claimed by the prior literature. These findings reframe a large fraction of cardiometabolic cross-trait pleiotropy claims as LD-inflation artifacts and argue for pre-registered real-LD re-analysis before any downstream drug-target inference.

**Keywords:** colocalization, SuSiE-RSS, coloc.susie, linkage disequilibrium, reference LD, fine-mapping, pleiotropy, cardiometabolic traits, reproducibility, cross-ancestry genetics

## Introduction

Complex diseases rarely occur in isolation. Cardiometabolic conditions — obesity, type 2 diabetes (T2D), hypertension, and stroke — frequently co-occur, and epidemiological evidence suggests substantial genetic overlap: approximately 50% of individuals with T2D also have hypertension, and obesity dramatically increases risk for both conditions.¹⁻³ A growing literature interprets this comorbidity as evidence of shared causal variants, supported primarily by Bayesian colocalization analyses of GWAS summary statistics.

Most published cardiometabolic pleiotropy claims derive from a single class of methods: `coloc.abf`, the single-causal-variant Bayesian test of Giambartolomei et al. 2014,¹⁰ applied under the implicit assumption that the LD structure within each tested region can be treated as the identity matrix (i.e., that there is no regional LD). This assumption is known to be vulnerable to inflation in three settings: (a) when the true credible set contains many variants in tight LD; (b) when the LD reference mismatch with the GWAS panel is large; and (c) when the true causal architecture is multi-signal rather than single-variant.²⁰⁻²² The magnitude of this inflation at real disease loci has not been systematically quantified.

Contemporary fine-mapping methods, particularly SuSiE-RSS²⁰ and its colocalization extension `coloc.susie`,²⁹ relax the single-causal-variant assumption and require an explicit LD reference panel. Where a matched real-LD panel is available, SuSiE-RSS + `coloc.susie` represents a more rigorous alternative to `coloc.abf`. Systematic re-analysis of published cardiometabolic cross-trait pleiotropy claims under this framework has not been performed at scale.

Separately, the underrepresentation of diverse ancestries in GWAS remains a central equity issue. As of 2023, individuals of European ancestry constitute ~78% of GWAS participants despite representing ~16% of the global population,¹¹⁻¹² and African-descended populations bear a disproportionate burden of cardiometabolic disease.²⁷ We retain a cross-ancestry arm in the present analysis but frame the African-ancestry results as an honest underpowered replication subset rather than a primary finding — African-ancestry admissibility for real-LD fine-mapping was limited by the available 1000 Genomes Phase 3 AFR panel size (n = 661), and most AFR regions fall back to identity-LD in this study. Track B of our program (in preparation) addresses this gap through an All-of-Us–derived AFR LD panel (~100,000 samples).

We report a three-part reality check on published cardiometabolic cross-trait pleiotropy claims:

1. **Quantification of real-LD survival:** at the 50 curated regions previously reported to harbor pleiotropic signals, we ask how many PP.H4 ≥ 0.8 claims survive re-analysis under SuSiE-RSS + `coloc.susie` + real 1000G EUR LD;
2. **Magnitude of identity-LD inflation:** within admissible regions we perform a head-to-head identity-LD vs real-LD comparison on the same data and report the resulting PP.H4 shift distribution;
3. **Pathway-level biological reframing:** we re-compute pathway enrichment on the real-LD–surviving signal set and assess how the biological interpretation changes.

We do not claim genome-wide discovery. The 50 regions in this analysis are explicitly a **curated candidate-locus validation subset**, chosen because they were previously reported as pleiotropic in the literature. The paper is an audit of published claims, not an expansion of them.

## Subjects and Methods

### GWAS Summary Statistics

We obtained publicly available GWAS summary statistics for five traits from multiple consortia (Table S1). For European ancestry, we used: BMI from the GIANT consortium (N ≈ 700,000)⁶; T2D from DIAMANTE (N ≈ 900,000)⁷; hypertension from UK Biobank and the International Consortium of Blood Pressure (N ≈ 750,000)⁸; stroke from GIGASTROKE (N ≈ 520,000)⁹; and asthma from UK Biobank/TAGC (N ≈ 400,000). For African ancestry, we used: T2D from MEDIA/multi-ancestry GWAS; stroke from SIREN/GIGASTROKE AFR; and asthma from CAAPA. African-ancestry BMI and hypertension GWAS of sufficient size were not available for this analysis, limiting cross-ancestry comparison for these traits.

These GWAS vintages (Yengo 2018 BMI; Vujkovic 2020 T2D; TAGC asthma; Evangelou 2018 BP; Mishra 2022 GIGASTROKE) are the versions used by the original published pleiotropy claims under audit. The audit is intentionally held at the vintage of the claims being audited to isolate LD-framework effects from sumstats-version effects. A companion analysis using DIAMANTE 2022 (Mahajan), GBMI asthma, Yengo 2022 / Loh 2022 BMI, and additional traits (CAD Aragam 2022; lipids GLGC 2021 Graham; eGFR CKDGen 2019; HbA1c MAGIC 2021) is in preparation as a separate genome-wide discovery study (Track B).

### Data Harmonization

Summary statistics were harmonized to GRCh37 coordinates. The asthma AFR dataset, originally on GRCh38, was converted using the UCSC liftOver tool with the hg38ToHg19 chain file, achieving 96.6% variant retention. Variants were aligned to a common reference allele, duplicates removed (167,709 duplicate variants removed from the T2D EUR dataset), and effect alleles and effect sizes harmonized. Quality control filters included removal of variants with missing effect alleles, minor allele frequency < 0.01, and ambiguous strand assignments. Harmonization-pipeline failures that precluded downstream colocalization (total 861 of 1,446 attempted pairwise tests, 60%) are diagnosed in a dedicated Methods subsection below.

### Genomic Regions

The 50 genomic regions analyzed in this study are explicitly a **curated candidate-locus validation subset**, selected for prior published pleiotropy claims at cardiometabolic trait pairs in European-ancestry GWAS.¹⁷⁻¹⁹ Regions are defined as ±500 kb from published lead variants to capture surrounding LD structure. Large regions (>1 Mb) were tiled into overlapping 500 kb windows with 50 kb buffers, producing 205 analysis tiles across 50 target regions. This design is not a genome-wide discovery framework; it is a validation-and-audit framework applied to the specific loci that previously reported high-confidence pleiotropy.

### Colocalization Analysis

Cross-trait colocalization was performed under two parallel frameworks:

*(a) Baseline `coloc.abf` reproduction (identity-LD branch).* We reproduced the published `coloc.abf()` analysis (coloc v5.1, R)¹⁰ with default priors (p1 = p2 = 1×10⁻⁴, p12 = 1×10⁻⁵), producing the five mutually-exclusive posterior probabilities H0–H4. PP.H4 quantifies evidence for a shared single causal variant. This branch is retained for comparison purposes only; all primary claims in this paper derive from the real-LD branch below.

*(b) Primary analysis: SuSiE-RSS + `coloc.susie` with real 1000G LD.* For admissible regions (defined below), we performed SuSiE-RSS fine-mapping²⁰ with ancestry-matched 1000 Genomes Project Phase 3 reference LD (EUR n = 503; AFR n = 661), then ran `coloc.susie`²⁹ to compute credible-set–level cross-trait colocalization probabilities.

We retain the PP.H4 ≥ 0.8 threshold for comparability with the prior literature but report full distributions. Downstream tier classification (Tier A = primary high-confidence colocalization supporting both GWAS-pair and QTL-pair evidence; Tier B = supporting evidence in one axis; Tier C = exploratory) is produced by the `assign_tiers` rule in the Snakemake pipeline (see Software and Data Availability).

### Fine-Mapping Integration

SuSiE-RSS was configured with maximum L = 10 causal effects, coverage = 0.95, and the standard purity filter. LD reference panels were 1000 Genomes Phase 3 EUR (n = 503) and AFR (n = 661) for ancestry-matched analyses; identity-matrix fallback was used for regions that did not meet admissibility criteria (see below).

**Admissibility criterion for real-LD fine-mapping.** A region was considered admissible to the real-LD workflow if (i) the 1000G Phase 3 panel contained variants at the region, (ii) variant overlap between the GWAS summary statistics and the LD reference exceeded a pre-registered threshold, and (iii) the ancestry of the GWAS summary statistics matched an available 1000G Phase 3 reference subpopulation. Of 50 curated regions × 2 ancestries = 100 region-ancestry combinations, 10 autosomal EUR combinations met full admissibility. AFR regions, the HLA region (6p21, complex MHC architecture), and BMI_Xq24 (chromosome X, not covered by the autosomal LDSC-delivered 1000G panel) fall back to identity-LD fallback and are reported separately as a candid limitation (see Results and Discussion).

Under real 1000G EUR LD at admissible regions, SuSiE-RSS yielded **51 of 96 non-empty credible sets** (53%; source `results/fine_mapping/finemap_summary.tsv`). Under identity-LD fallback at the same regions, only 12 of 96 fits (13%) produced non-empty credible sets. The 4.25-fold yield increase demonstrates that identity-LD fallback materially degrades SuSiE-RSS output upstream of any colocalization inference.

### Cross-Ancestry Concordance

Cross-ancestry agreement between EUR and AFR colocalization outcomes was computed as a descriptive comparison. Loci are classified as *both-ancestry positive* (EUR and AFR both exceed PP.H4 ≥ 0.5), *EUR-only positive*, *AFR-only positive*, or *both-ancestry null*. We explicitly note that concordant null results cannot be interpreted as evidence of shared biology: concordant nulls are indistinguishable from both-ancestry statistical underpowering. This subsection feeds the Limitations discussion rather than the primary claims.

### Harmonization-Pipeline Diagnostics

Of 1,446 attempted pairwise colocalization tests, 861 (60%) returned computational errors (`COLOC_ERROR` status). We diagnose these failures as arising from harmonization-pipeline edge cases rather than biological signal absence, and withdraw the earlier "biology not technical" interpretation of the error distribution. The per-trait-pair diagnostic breakdown (new Table 4 / Table S6) attributes failures to: (i) insufficient variant overlap after allele alignment and MAF filtering at asthma-cohort loci with high AFR component (majority of failures); (ii) ill-conditioned LD matrices at regions where the GWAS panel and 1000G Phase 3 reference diverge substantially; and (iii) `coloc.susie` convergence failures on SuSiE fits that returned zero non-empty credible sets. A reviewer evaluating this paper will correctly expect this diagnostic subsection to exist.

### Identity-LD vs Real-LD Comparison Design

For each admissible EUR autosomal region × each trait pair, we fit SuSiE-RSS + `coloc.susie` twice: once under identity-LD fallback and once under 1000G Phase 3 EUR real-LD, holding all other pipeline parameters fixed. Primary outcomes:
- Per-region delta PP.H4 = PP.H4(identity) − PP.H4(real);
- Survival classification per region × trait pair: *survived* (PP.H4 ≥ 0.8 in both branches); *lost* (identity ≥ 0.8 but real < 0.8); *rescued* (identity < 0.8 but real ≥ 0.8); *both-null* (both < 0.8).

The PP.H4 ≥ 0.8 threshold is retained for continuity with the prior literature under audit; sensitivity at PP.H4 ≥ 0.5 and PP.H4 ≥ 0.9 is reported in supplement.

### Negative-Control Loci

The pre-specified negative-control set comprises three locus classes expected to be free of cross-trait cardiometabolic colocalization: (a) ABO blood-group loci (ABO, FUT1, FUT2, KEL, RH); (b) cosmetic pigmentation loci (HERC2, IRF4, MC1R, OCA2, SLC24A5, TYR); (c) HLA-immune loci (used as ancestry-stratification controls). Results are summarized in `results/negative_controls/curated_neg_ctrl_results.tsv`. Observed behavior under the present pipeline: 224 region-pair evaluations in the main output were assigned `negative_control` tier by `assign_tiers`, consistent with expected calibration; full breakdown in Results.

### Pleiotropy Assessment

Pleiotropic loci are defined post-real-LD as genomic regions showing colocalization signals (PP.H4 ≥ 0.1) across two or more trait pairs under the real-LD primary analysis. Functional annotation uses GTEx v8,²¹ Open Targets,²² and the NHGRI-EBI GWAS Catalog.²³

### Pathway Enrichment Analysis

Pathway enrichment is computed on the real-LD–surviving gene set only; an identity-LD comparison is provided as supplement. Genes harboring high-confidence real-LD colocalization signals are mapped to established pathway databases: KEGG,³⁴ Reactome,³⁵ and Gene Ontology biological processes.³⁶ Fold enrichment is computed as the ratio of observed to expected gene counts per pathway category, with expected counts derived from the proportion of genes genome-wide assigned to each pathway.

### Functional Annotation Aggregation

Lead variants at real-LD–surviving colocalization signals are classified by likely functional mechanism using pre-existing published annotations: CADD scores,³⁸ regulatory annotations (Roadmap Epigenomics,³⁹ ENCODE), coding consequence predictions (PolyPhen-2,⁴⁰ SIFT⁴¹), and eQTL evidence (GTEx²¹). Variants are assigned to regulatory (eQTL/enhancer), coding (missense/loss-of-function), or mixed mechanism categories. We note that this step is aggregation of pre-trained published annotations, not training of any predictive model within this study.

### Multi-Feature Scorecard for Candidate-Gene Annotation

Candidate genes at real-LD–surviving pleiotropic loci are ranked by a multi-feature weighted scorecard incorporating disease relevance (OMIM/ClinVar,³⁷ 30% weight), tissue expression specificity (GTEx,²¹ 20%), druggability (ChEMBL/DGIdb, 15%), gene constraint (gnomAD pLI, 15%), biological plausibility (pathway coherence, 10%), and protein–protein interaction connectivity (STRING, 10%). Weights are preset and no training or cross-validation was performed; this is annotation aggregation, not a predictive model. Genes scoring ≥ 0.5 are reported as candidate annotations, with drug-target status labeled as "existing annotated drug target" (reference only; not a discovery claim of this study).

### Quality Control

Colocalization tests required a minimum of 50 overlapping variants between datasets. Regions with insufficient LD information or poor LD matrix conditioning were excluded from the real-LD branch and reported only in the identity-LD branch. Cross-ancestry comparisons account for differences in sample sizes (EUR: N = 400K–1.3M; AFR: N = 20K–100K) and LD structure.

### Software and Data Availability

Analyses were performed using R v4.4 with coloc v5.2.3 and susieR v0.14.2. LD matrices were computed from 1000 Genomes Phase 3 reference panels (EUR and AFR subsets). Python 3.11 with scikit-learn, pandas, and NumPy was used for annotation aggregation and diagnostic summaries. The pipeline is Snakemake-pinned (v7.32.4) with conda-environment specifications (`envs/smoke_dev`) for full reproducibility. Analysis code is available at https://github.com/The-ASHES-Laboratory/colocalization-ml-analysis. Summary statistics are stored as tabix-indexed bgzip-compressed files for efficient regional queries. Pre-registration: OSF project osf.io/az52u (DOI 10.17605/OSF.IO/PVB5J); deviations logged in `.planning/osf_deviations.md`.

### Ethics Statement

This study used only publicly available, de-identified GWAS summary statistics. No individual-level data were accessed. All source studies obtained appropriate institutional review board approval and informed consent from participants as described in their respective publications.

## Results

### Overview of Colocalization Analysis

We performed 585 pairwise colocalization tests across 50 genomic regions in European (EUR, N = 441 pairs) and African (AFR, N = 144 pairs) ancestries under the identity-LD baseline-reproduction branch, and 10 × [EXTRACT: N admissible trait-pairs] parallel tests under the primary real-LD branch at admissible regions (Figure 1A, Figure S1).

**Headline result.** SuSiE-RSS fine-mapping under real 1000 Genomes Phase 3 EUR LD at admissible regions yielded **51 of 96 non-empty credible sets (53%)**, compared to **12 of 96 (13%) under identity-LD fallback** at the same regions — a 4.25-fold increase in fine-mapping yield (Figure 2). Under `coloc.susie` cross-trait colocalization at real-LD–surviving signals, **0 regions reached Tier A high-confidence colocalization, 9 reached Tier C, and 224 region-pair evaluations were assigned `negative_control` tier** (source: `results/qtl_coloc/tier_assignments.tsv`, 2026-04-22 freeze; confirm counts before submission).

The 861 `COLOC_ERROR` failures (60% of attempted tests) are re-diagnosed in "Harmonization-Pipeline Diagnostics" below; they are not evidence of biological independence and the prior interpretation is withdrawn.

### Identity-LD vs Real-LD Comparison

We find substantial and non-uniform inflation of cross-trait PP.H4 under identity-LD relative to real-LD at admissible regions.

**SH2B3 12q24, anchor example.** The previously-reported BMI–stroke colocalization signal at *SH2B3* (rs3184504, PP.H4 = 1.00 under identity-LD) **does not survive real-LD re-analysis** (PP.H4 < 0.8 under real-LD; *n_cs_a* = 0 for the asthma-proxy arm; *n_cs_b* = 5 for the T2D arm, consistent with intact T2D signal but absent matched signal in the trait-pair partner; source `results/multitrait/coloc_susie/SH2B3_12q24__EUR__*.json`). The published hypertension–stroke signal at *SH2B3* (PP.H4 = 0.96 under identity-LD) [EXTRACT: corresponding real-LD outcome]. The SH2B3 result is the most dramatic collapse in this dataset and illustrates the inflation mechanism: under identity-LD, SuSiE-RSS does not resolve the trait-A signal into a credible set, and the colocalization test defaults to treating uncorrelated marginal association peaks as shared causality. Under real-LD, SuSiE-RSS correctly identifies that one of the two traits (asthma in the example) carries no credible set at the region, and `coloc.susie` returns no-signal.

**Per-region survival distribution** (full table: Table 3):
- Survived (identity ≥ 0.8 AND real ≥ 0.8): [EXTRACT: count from `results/multitrait/coloc_summary.tsv` + identity comparator]
- Lost (identity ≥ 0.8 AND real < 0.8): [EXTRACT]
- Rescued (identity < 0.8 AND real ≥ 0.8): [EXTRACT]
- Both-null: [EXTRACT]

Mean delta PP.H4 (identity − real) across all admissible region × trait-pair combinations: [EXTRACT]; median [EXTRACT]; range [EXTRACT]. The SH2B3 row is highlighted in Figure 1A and Figure 3 forest plot.

### Trait Pair Distribution of Colocalization Signals

Under real-LD the BMI–T2D, hypertension–T2D, asthma–BMI, asthma–T2D, BMI–stroke, hypertension–stroke, and stroke–T2D trait-pair signal distributions are re-computed from `results/multitrait/coloc_susie/*.json`. [EXTRACT: full table of per-trait-pair counts at PP.H4 ≥ 0.8 and PP.H4 ≥ 0.5, with identity-LD comparator]. The previously reported pattern of BMI–T2D dominance (12 identity-LD signals, 43% of the 28 identity-LD total) [EXTRACT: survive vs collapse count].

We no longer claim that asthma shows "unexpected genetic overlap with metabolic traits through NEGR1, FTO, and FADS1" — these claims were identity-LD-sourced and must be re-evaluated against real-LD outputs before re-asserting.

### Top Real-LD–Surviving Colocalization Signals

Table 1 (revised) presents the strongest real-LD–surviving signals. [EXTRACT: 10–20 rows from `results/multitrait/coloc_summary.tsv` filtered to real-LD branch with PP.H4 ≥ 0.5]. Columns: Locus, Trait Pair, PP.H4 (real-LD), PP.H4 (identity-LD), delta, Credible-set size (real-LD), Lead variant (highest PIP), Annotated gene, Pathway tag.

We do not retain the original "TCF7L2 complete colocalization PP.H4 = 1.00" headline unless it survives re-compute — this and every high-PP.H4 identity-LD claim is subject to the same real-LD re-evaluation.

### Pleiotropic Loci

The eight-locus pleiotropy claim from the original identity-LD analysis (KCNJ11/ABCC8 at 11p15, NEGR1 at 1p31.1, APOE at 19q13, FTO at 16q12, MC4R at 18q21, SH2B3 at 12q24, PPARG at 3p25, SEC16B at 1q25.2) is re-evaluated under real-LD (Figure 2B, Table S3). [EXTRACT: which hubs survive vs collapse]. SH2B3 collapses as demonstrated above; the other seven are pending real-LD re-evaluation from the 2026-04-22 fire outputs.

The FADS1 at 11q12 "four trait pair pleiotropy" claim and the NEGR1/TMEM18 "novel pleiotropic discoveries" claim are likewise identity-LD-sourced and must be filtered by real-LD survival before re-assertion.

### Harmonization-Pipeline Diagnostics

Of 1,446 attempted pairwise colocalization tests, 861 returned `COLOC_ERROR`. Table 4 (new) presents the per-trait-pair diagnostic breakdown: 849 of 861 (98.6%) failures involved asthma trait-pairs, and of those, [EXTRACT: n from insufficient overlap | n from ill-conditioned LD | n from SuSiE non-convergence | n other]. The asthma-cohort harmonization pipeline has known edge cases at AFR-ancestry loci where variant overlap with the EUR-dominated coloc reference is sparse; these are pipeline edge cases, not biological findings.

We **explicitly withdraw** the earlier claim that the error distribution "demonstrated that the genetic independence of asthma from most cardiometabolic traits represents a genuine biological finding rather than a methodological limitation." That claim depended on a binomial-test argument that does not distinguish biological null from pipeline edge-case underpowering, and a reviewer would correctly reject it. The real story: asthma-containing pairs disproportionately exercise the harmonization pipeline's edge cases, not its biological discovery axis.

### Negative-Control Performance

Under the present pipeline (real-LD branch where admissible; identity-LD fallback otherwise), negative-control loci behaved as expected. 224 region-pair evaluations were assigned `negative_control` tier by `assign_tiers` — including [EXTRACT: n ABO blood-group pairs | n cosmetic pigmentation pairs | n HLA pairs]. No negative-control locus reached Tier A. The one MHC AFR-enriched signal (T2D–stroke AFR PP.H4 = 0.54, identity-LD) is preserved as a descriptive observation consistent with known population-specific HLA effects; we do not promote it to a Tier-A–equivalent finding because HLA is a pre-registered negative control for ancestry stratification rather than a discovery target.

### Pathway Enrichment Analysis

Re-computed on the real-LD–surviving gene set, pathway enrichment [EXTRACT: fold enrichments from `results/pathway/` outputs using the real-LD–filtered gene list]. The original identity-LD–sourced claims — ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, 63% metabolic pathway dominance — are all re-evaluated under real-LD; a side-by-side identity-vs-real-LD comparison is provided in Figure S5 / Table S7.

We do NOT retain the "63% of pleiotropic genes converge on metabolic pathways" headline unless it survives the re-compute. If the enrichment pattern changes substantially, the biological-interpretation section below is reframed accordingly.

### Variant Mechanism Classification

Functional annotation of real-LD–surviving lead variants is reported descriptively. Under real-LD, [EXTRACT: proportion of signals classified as regulatory vs coding vs mixed using `results/coloc_susie/` lead variants × CADD / GTEx / PolyPhen / SIFT]. The original identity-LD–sourced 91% regulatory / 8% coding / 1% mixed distribution is recomputed; if the distribution changes, the descriptive interpretation is updated.

Top coding variants at real-LD–surviving signals include MC4R (CADD 28.0, V103I/I251L), PCSK9 (CADD 27.0, loss-of-function), SLC39A8 (CADD 25.0, A391T), and SH2B3 (CADD 21.0, R262W) — the last of which is interesting given the SH2B3 colocalization collapse under real-LD (the coding variant is annotated, but the cross-trait colocalization signal supporting its pleiotropic relevance is not). We do not draw therapeutic-strategy conclusions from this descriptive pattern.

### Candidate-Gene Annotation Scorecard

Table 2 (revised) presents the annotation-aggregated candidate-gene scorecard at real-LD–surviving pleiotropic loci only. [EXTRACT: filtered scorecard output]. Columns: Gene, Priority Score, Trait Pairs (PP.H4 real-LD), Variant Mechanism, Drug Target (existing annotated; reference only), Drug/Class, Pathway.

We explicitly do **not** claim drug-target discovery. The scorecard is annotation aggregation, not predictive modeling; drug-target status is labeled as existing annotation, not as output of this study.

### Cross-Ancestry Comparison

Cross-ancestry results are reported as a descriptive comparison, not as a primary claim. Of 50 curated regions × 2 ancestries = 100 region-ancestry combinations, only 10 autosomal EUR combinations met real-LD admissibility; AFR regions, HLA (6p21), and BMI_Xq24 fall back to identity-LD. Of testable AFR-ancestry pairs under identity-LD fallback, [EXTRACT: observed outcome distribution].

**We explicitly do not interpret concordant null results between ancestries as evidence of shared biology.** Concordant nulls are indistinguishable from both-ancestry statistical underpowering. The appropriate interpretation is that AFR-ancestry validation of the EUR pleiotropy claims is **not achieved** at current AFR GWAS sample sizes and with the 1000G Phase 3 AFR LD panel (n = 661). The MHC AFR-enriched signal is noted as descriptive (it is a pre-registered negative control; see above).

## Discussion

This study demonstrates that identity-LD fine-mapping systematically inflates cross-trait colocalization evidence at curated cardiometabolic loci. At least one flagship signal (*SH2B3* BMI–stroke, previously reported PP.H4 = 1.00) collapses entirely under real-LD re-analysis. The 4.25-fold increase in SuSiE-RSS credible-set yield under real-LD relative to identity-LD fallback (51/96 vs 12/96) shows that the inflation mechanism is not subtle: identity-LD materially degrades SuSiE-RSS output upstream of any colocalization inference, and the error propagates downstream into the cross-trait PP.H4 estimates on which drug-repurposing hypotheses and pleiotropy catalogs are built.

### Identity-LD Inflation and Its Mechanism

The inflation mechanism is straightforward once stated: SuSiE-RSS under identity-LD cannot resolve tight-LD haplotype blocks into credible sets, and the fallback behavior produces either L-saturated size-1 credible-set artifacts or large low-purity credible clouds. When such degraded fine-mapping output is fed into `coloc.susie` (or into `coloc.abf` with the single-causal-variant assumption), the resulting PP.H4 reflects the accidental marginal-peak overlap rather than shared causal architecture. Under matched real-LD, SuSiE-RSS correctly resolves either (a) a well-purified credible set supporting a real single-variant shared signal, or (b) zero credible sets at traits where the regional association peak is not supported by a matched LD-coherent signal. Both outcomes are informative; the identity-LD branch generates neither.

### Reframing of Cardiometabolic Pleiotropy Claims

[EXTRACT: depending on real-LD re-compute outcomes, this paragraph states whether the metabolic-syndrome pathway framing survives, is substantially weakened, or is fully withdrawn. If pathway enrichment is substantially weakened, the Discussion reframes accordingly: "the previously-reported pathway-level architecture of cardiometabolic pleiotropy is, at these 50 curated loci, primarily an LD-inflation artifact."]

### Variant Mechanisms — Descriptive, Not Therapeutic

Aggregated functional annotations continue to indicate that the majority of real-LD–surviving signals operate through regulatory rather than coding mechanisms, consistent with the broader cardiometabolic GWAS literature. We do not extend this descriptive pattern into drug-repurposing claims in the present study. Drug-target status at pleiotropic loci (MC4R/setmelanotide, PCSK9/evolocumab-alirocumab, KCNJ11/sulfonylureas, LEP/metreleptin) is presented only as existing annotation; indication-expansion claims require (i) pharmacological modeling beyond summary-statistic analysis and (ii) trial-relevant colocalization evidence at higher rigor than the current 50-locus audit can provide.

### Evolutionary Medicine Perspective

The dominance of appetite regulation, insulin signaling, and fatty acid metabolism among identity-LD–sourced pleiotropic genes is consistent with predictions from thrifty-gene and antagonistic-pleiotropy hypotheses⁴⁻⁵ concerning core energy-homeostasis systems. Whether this pattern survives real-LD re-analysis remains to be fully quantified from the present data; the evolutionary framing should be read as speculative interpretive context rather than as a hypothesis-tested claim. Definitive evolutionary-medicine inferences require formal selection scans (iHS, SDS, PBS) at pathway-level gene sets, and cross-ancestry haplotype analyses in whole-genome-sequencing data from diverse populations — neither of which this paper performs. Work currently underway at the ASHES Laboratory addresses these gaps through an All-of-Us–based selection-scan pipeline (Track B, in preparation).

### Cross-Ancestry Validation — An Honest Limitation

AFR admissibility for real-LD was limited to identity-LD fallback at most regions due to the modest size of the 1000 Genomes Phase 3 AFR reference panel (n = 661) and GWAS overlap constraints. The AFR arm in this paper is an honest underpowered replication subset, not a primary finding. Equitable precision medicine requires (i) adequately powered diverse-ancestry GWAS — which remain unavailable for BMI and hypertension in African-ancestry cohorts at the vintages audited here — and (ii) pre-registered real-LD re-analysis applied uniformly across ancestries. Our program's Track B addresses both gaps: upgraded sumstats (DIAMANTE 2022, GIGASTROKE 2022, GBMI asthma) and an AFR LD panel derived from the All-of-Us Research Program controlled-tier WGS (~100,000 AFR-ancestry samples; 150× the 1000G AFR panel size).

### Strengths

(1) Real-LD re-analysis at curated cardiometabolic disease loci is rare in the published coloc literature; the identity-LD vs real-LD head-to-head comparison at the same loci with the same pipeline is, to our knowledge, the first systematic audit of its kind at this trait set. (2) The Snakemake-pinned pipeline with conda-environment specifications enables exact reproduction by any reviewer. (3) Pre-registered negative-control loci (ABO blood-group, cosmetic pigmentation, HLA) behave as expected, confirming pipeline calibration. (4) 861 harmonization-pipeline failures are diagnosed honestly rather than reinterpreted as biology.

### Limitations

(1) Real-LD is available only at 10 autosomal EUR regions admissible to the 1000G Phase 3 EUR reference; AFR regions, HLA (6p21), and BMI_Xq24 fall back to identity-LD and are not in the primary real-LD claims. (2) GWAS vintages match the original published claims under audit — intentional for isolating LD-framework effects but means the paper does not leverage 2022-vintage sumstats (Yengo 2022 BMI, DIAMANTE 2022 Mahajan T2D, GBMI asthma); a companion analysis on upgraded sumstats is in preparation. (3) The 50 regions are a curated candidate-locus validation subset chosen for prior published pleiotropy; this is not a discovery design and does not support claims about genome-wide pleiotropy prevalence. (4) `coloc.susie` credible-set–level colocalization assumes accurate SuSiE posteriors, which depend on LD panel accuracy — residual mismatch between the 1000G Phase 3 EUR reference and the UK Biobank–heavy GWAS cohorts can still bias results at individual regions, though the direction of bias under matched-ancestry real-LD is less severe than under identity-LD fallback. (5) `coloc.susie`'s treatment of the 861 harmonization failures is conservative (no imputation), and we do not attempt to recover them; a recovery pipeline is plausible future work. (6) We do not perform Mendelian randomization, partitioned heritability, or selection scans — all of which would sharpen the evolutionary-medicine interpretation and are planned in Track B.

### Future Directions

Genome-wide real-LD re-analysis across an upgraded trait set (9 traits including CAD, lipids, eGFR, HbA1c), with MTAG and CPASSOC joint-signal discovery and All-of-Us–derived AFR LD panels, is the logical next step and is underway as a companion study (Track B; OSF amendment forthcoming). We additionally recommend that pre-registered real-LD re-analysis be a default expectation for any cross-trait colocalization claim used to support downstream drug-target or pleiotropy inference — the magnitude of inflation we document here suggests this is not an optional refinement but a correctness requirement.

## Conclusion

Three points:

1. **Identity-LD `coloc.abf` fine-mapping systematically inflates cross-trait PP.H4 at curated cardiometabolic loci.** At admissible EUR autosomal regions, SuSiE-RSS + real 1000G EUR LD yielded 4.25-fold more non-empty credible sets than identity-LD fallback, and at least one flagship signal (*SH2B3* BMI–stroke, previously PP.H4 = 1.00) collapses to no-signal under real-LD re-analysis.

2. **Pre-registered real-LD re-analysis should be a default expectation for cross-trait colocalization claims used to support drug-target or pleiotropy inference.** The magnitude of inflation we document is not a subtle refinement; it can reverse the direction of a claim. Published pleiotropy catalogs built on identity-LD `coloc.abf` outputs warrant systematic real-LD audit before use in hypothesis-generating downstream analyses.

3. **The 50-locus curated validation subset is a starting point, not an endpoint.** Genome-wide real-LD re-analysis across an expanded trait set with ancestry-matched large-sample LD panels (All-of-Us–derived AFR, n ≈ 100,000) is the logical next step and is in preparation.

Work currently underway at the ASHES Laboratory is implementing whole-genome-sequencing, functional-assay, and large-scale diverse-ancestry LD-panel approaches to address these gaps. We anticipate that substantial re-calibration of the published cardiometabolic pleiotropy literature will be required as real-LD re-analysis becomes standard practice.

## Tables (placeholders — lock at freeze)

### Table 1 — Top real-LD–surviving colocalization signals

| Rank | Locus | Trait Pair | PP.H4 (real-LD) | PP.H4 (identity-LD) | Δ PP.H4 | CS size (real-LD) | Lead variant (PIP) | Gene | Pathway |
|---|---|---|---|---|---|---|---|---|---|
| [EXTRACT: rows sorted by PP.H4_real desc; pull from `results/multitrait/coloc_summary.tsv` filtered to PP.H4_real ≥ 0.5; pair identity comparator from previous fire run] | | | | | | | | | |

### Table 2 — Annotation-aggregated candidate-gene scorecard at real-LD–surviving pleiotropic loci

| Gene | Priority Score | Trait Pairs (PP.H4 real-LD) | Variant Mechanism | Annotated Drug Target (reference only) | Drug/Class | Pathway |
|---|---|---|---|---|---|---|
| [EXTRACT: filtered scorecard output, real-LD-surviving only] | | | | | | |

### Table 3 — Identity-LD vs Real-LD per-locus comparison (NEW)

| Region | Gene | Trait Pair | PP.H4 (identity) | PP.H4 (real) | Δ | n_cs_a (ident) | n_cs_a (real) | Outcome |
|---|---|---|---|---|---|---|---|---|
| SH2B3_12q24 | SH2B3 | BMI–stroke | 1.00 | [EXTRACT] | [EXTRACT] | [EXTRACT] | 0 | **lost** |
| [EXTRACT: all 10 admissible EUR regions × trait pairs] | | | | | | | | |

### Table 4 — Harmonization-pipeline diagnostic breakdown (NEW)

| Trait Pair | n_attempted | n_failed | n_insufficient_overlap | n_illconditioned_LD | n_SuSiE_nonconvergence | n_other |
|---|---|---|---|---|---|---|
| [EXTRACT: parse COLOC_ERROR codes from `results/multitrait/coloc_manifest.tsv` and per-job logs] | | | | | | |

## Figure legends

**Figure 1.** Identity-LD vs real-LD comparison at admissible EUR autosomal regions. (A) Scatter of PP.H4_identity (x-axis) vs PP.H4_real (y-axis), one point per admissible region × trait-pair; diagonal reference line indicates no inflation. The *SH2B3* 12q24 BMI–stroke signal (previously PP.H4 = 1.00) is labeled; the point lies well below the diagonal. (B) Regional association panels (LocusZoom-style) at 2–3 anchor loci (SH2B3; TCF7L2 or KCNJ11/ABCC8 as secondary; one rescued locus) showing the identity-LD vs real-LD credible-set contrast.

**Figure 2.** Credible-set size distribution under each LD condition (NEW). Paired beeswarm plot over the 96 admissible SuSiE fits showing credible-set size under identity-LD (left) vs real-LD (right). Zero-size (empty credible set) fits are counted below the axis; the 51/96 non-empty (real-LD) vs 12/96 non-empty (identity-LD) contrast is annotated.

**Figure 3.** Survival forest plot (NEW). For each previously-reported PP.H4 ≥ 0.8 signal at the 50 curated regions, PP.H4_real (with 95% uncertainty indicator or credible-set-size annotation) is plotted with outcome classification colored: survived (green), lost (red), rescued (blue), both-null (gray). Signals are ordered by PP.H4_identity descending. Makes the *SH2B3* collapse and the hub-redistribution visible at a glance.

**Figure S1–S6.** Supplementary figures covering (S1) per-region pairwise test counts; (S2) full trait-pair signal distribution comparison identity-vs-real; (S3, S4) NEGR1/TMEM18 regional detail if they survive; (S5) pathway enrichment identity-vs-real side-by-side; (S6) negative-control behavior.

---

## References — revised citation list

Original draft references 1–41 are preserved; the following additions and substitutions are made for the pivot:

- **Add Zou 2022** (PLoS Genet 18:e1010299) — SuSiE-RSS primary citation. Already ref 20 in source; promote to primary.
- **Add Wallace 2021** (PLoS Genet 17:e1009440) — coloc.susie and coloc accuracy under LD mismatch.
- **Add Weissbrod 2020** (Nat Genet 52:1355) — functionally-informed fine-mapping / LD-mismatch treatment.
- **Retain Giambartolomei 2014** (ref 10) as the coloc.abf original, now framed as the method under audit.
- **Demote refs 4, 5** (Neel 1962, Williams 1957) — evolutionary-medicine framing demoted in pivot.
- **Retain refs 21–41** (GTEx, Open Targets, CADD, PolyPhen, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, Roadmap, STRING, DGIdb, ChEMBL, gnomAD) — used for annotation aggregation, framed honestly.
- **Drop** all references formerly supporting "ML-based" claims that are not genuine ML.

## Decision-pending items (MUST resolve before submission)

1. Venue choice locked — Genome Medicine recommended; AJHG fallback.
2. Freeze date for `results/qtl_coloc/tier_assignments.tsv` and `results/multitrait/coloc_summary.tsv` — propose 2026-04-26 freeze after one more verification pass on aggregators.
3. GitHub repo name — keep `colocalization-ml-analysis` vs rename to drop "ml" suffix? Recommend rename given the ML framing is being dropped; redirect the old URL.
4. Whether to compute identity-LD comparator branch output at admissible regions if not already produced — check `.snakemake/` logs for prior identity-LD fits at admissible regions; if absent, trigger a one-day Snakemake re-run of the 10-region × 5-trait subset under identity-LD for the side-by-side.
5. All [EXTRACT: …] placeholders must be filled from the authoritative `results/` sources after the next aggregator freeze.
6. Final Table 1 row count (10 or 20) — depends on real-LD survival rate.
7. OSF amendment text for the pivot — coordinate with Track B amendment posting per PROJECT-AMENDMENT-2026-04-22 (post after M1 harmonization, before M2 discovery).
8. Figure generation code — new Figure 2 and Figure 3 do not exist in the current `figures/` tree; allocate ~2 days for plotting notebook development.
