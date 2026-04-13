# Phase 5 Methods Fragment -- Pathway + Partitioned Heritability Analysis

Prepared for Phase 11 manuscript assembly. This fragment documents the Phase 5
analytical pipeline that converts Phase 2 colocalization-nominated genes into
statistically rigorous pathway enrichment, tissue-specific heritability, and
local genetic covariance results through six complementary analytical methods
with negative controls and permutation null validation.

Original research framing: this is Carter K. Clinton's hypothesis-driven
cross-ancestry colocalization study at the ASHES Lab, NCSU. Phase 5 tests the
"pathway-defined metabolic syndrome" thesis by applying multi-method, properly
null-controlled pathway analysis tied to heritability fractions and tissue
specificity.

## Gene-based and gene-set analysis (MAGMA)

Gene-level and gene-set enrichment analysis was performed using MAGMA v1.10
(de Leeuw et al. 2015, PLoS Comput Biol). The analysis followed the standard
three-step workflow: (1) SNP-to-gene annotation using NCBI37.3 gene boundaries
with a {RESULT} kb window and the 1000 Genomes Phase 3 EUR reference panel for
LD correction; (2) gene-level association testing from full GWAS summary
statistics for each trait-ancestry combination, with sample size specified as
effective N = 4/(1/n_case + 1/n_ctrl) for binary traits; (3) competitive
gene-set analysis testing enrichment of gene-level associations within predefined
gene sets.

Four standard databases were tested: KEGG, Reactome, GO Biological Process,
and MSigDB Hallmark (Subramanian et al. 2005). In addition, 8 custom
cardiometabolic pathway sets were included to directly test the pathway-defined
metabolic syndrome thesis: (1) insulin signaling (INSR, IRS1, IRS2, PIK3CA,
AKT1, AKT2, and {RESULT} additional genes), (2) appetite regulation (MC4R,
FTO, BDNF, LEP, LEPR, and {RESULT} additional genes), (3) glucose metabolism
(GCK, GCKR, HNF1A, TCF7L2, and {RESULT} additional genes), (4) fatty acid
metabolism (FADS1, FADS2, ELOVL2, CPT1A, and {RESULT} additional genes),
(5) inflammation (SH2B3, IL6, IL6R, TNF, NFKB1, and {RESULT} additional genes),
(6) vascular tone (NOS3, EDN1, AGT, ACE, AGTR1, and {RESULT} additional genes),
(7) lipid transport (APOE, APOB, PCSK9, LDLR, and {RESULT} additional genes),
and (8) energy storage (PPARG, CEBPA, ADIPOQ, PLIN1, and {RESULT} additional
genes). Gene set definitions were curated from KEGG pathway annotations and
trait-specific GWAS literature. Benjamini-Hochberg FDR correction was applied
jointly across all gene sets (standard + custom + negative controls) per trait
to control false discovery rate.

## Functional enrichment (g:Profiler)

Functional enrichment of the colocalization-nominated gene list (Tier A + Tier B
genes from Phase 2, defined as genes with PP.H4 >= {RESULT} for at least one QTL
source) was performed using g:Profiler (Reimand et al. 2019, Nat Protoc; Kolberg
et al. 2021). Enrichment was tested against three annotation sources: GO
Biological Process, KEGG, and Reactome.

To avoid discoverable-gene bias, a custom background gene list was constructed
following the Reimand 2019 protocol: all genes within 500 kb of any genome-wide
significant SNP (P < 5 x 10^-8) across all 5 traits (BMI, T2D, hypertension,
asthma, stroke) in the EUR ancestry summary statistics. This 5-trait union
background controls for the fact that genes near GWAS hits for any trait are
more discoverable than random genes (Reimand 2019). Electronic GO annotations
(IEA evidence code) were excluded to retain only experimentally validated
annotations.

## Partitioned heritability (S-LDSC)

Stratified LD Score Regression (S-LDSC; Finucane et al. 2015, Nat Genet) was
used to estimate the proportion of trait heritability attributable to each
pathway gene set. The analysis used the baseline LD model v2.2 (Gazal et al.
2017, Nat Genet) comprising 97 annotations including coding, UTR, promoter,
enhancer, histone marks (H3K4me1, H3K4me3, H3K9ac, H3K27ac), DNase I
hypersensitive sites (DHS), and FANTOM5 enhancers.

Custom binary annotations were added for each of the 8 cardiometabolic pathway
gene sets and 3 negative control sets: SNPs within 100 kb of any gene in the
set were annotated as 1, all others as 0. The --overlap-annot flag was always
included to properly account for overlap between baseline and custom
annotations. Baseline v2.2 LD scores were always listed first in --ref-ld-chr
to ensure correct conditioning. EUR LD scores were computed from 1000 Genomes
Phase 3 plink files. Pre-computed regression weights (weights_hm3_no_hla) and
HapMap3 SNP lists were used for LD score regression. Summary statistics were
munged using the standard LDSC pipeline with HapMap3 merge; a post-munge
validation step warned if fewer than 500,000 SNPs remained.

Heritability enrichment (proportion of h^2 / proportion of SNPs) was computed
for each custom annotation, with enrichment p-values from the coefficient
z-score.

## Tissue-specific enrichment (LDSC-SEG)

Tissue-specific heritability enrichment was assessed using LDSC-SEG (Finucane
et al. 2018, Nat Genet). Two annotation panels were tested: (1) GTEx v8
RNA-seq gene expression across 53 tissues, using pre-computed LD scores from
Multi_tissue_gene_expr; and (2) Roadmap Epigenomics chromatin state annotations
across {RESULT} cell types, using pre-computed LD scores from
Multi_tissue_chromatin.

For each trait-ancestry combination, LDSC-SEG identified tissues with
significant heritability enrichment (coefficient z-score P < 0.05 /
{RESULT} tissues, Bonferroni-corrected). A shared tissue analysis (per D-05b)
identified tissues enriched for heritability in both members of biologically
relevant trait pairs (BMI-T2D, hypertension-stroke, BMI-hypertension,
T2D-stroke, BMI-asthma), providing evidence for shared biological mechanisms.

## Local genetic covariance (HESS/rho-HESS)

Local genetic covariance between trait pairs was estimated using HESS v0.5.4-beta
(Shi et al. 2017, Am J Hum Genet). The analysis quantifies how much genetic
correlation between two traits concentrates at specific genomic loci versus
being distributed uniformly across the genome.

HESS was run for each of the {RESULT} trait pairs (C(5,2) = 10 unique pairs
from 5 traits) for each shared ancestry. For each pair, rho-HESS estimated
local genetic covariance per chromosome, then results were combined genome-wide.
Summary statistics were converted to HESS format (Z = BETA/SE; N = effective
sample size for binary traits) with validation rejecting NaN/Inf Z-scores and
non-positive sample sizes. The HESS LD reference panel (1000 Genomes EUR) was
validated for GRCh37 coordinates using 5 hardcoded reference SNP positions
(rs1, rs12, rs334, rs7412, rs429358).

A pleiotropic enrichment test compared mean local covariance at colocalized
loci (defined by overlap with the {RESULT} curated regions from
config/regions_curated.csv) versus the genome-wide background mean.
The z-score was computed as (mean_pleio - mean_bg) / sqrt(SE_pleio^2 + SE_bg^2)
with a two-sided p-value, testing whether pleiotropic loci show excess local
genetic correlation beyond the polygenic background.

## Negative controls and permutation null

Three curated negative control gene sets were validated across all 5 enrichment
methods (MAGMA, g:Profiler, LDSC partitioned heritability, LDSC-SEG, HESS) to
ensure the pipeline does not produce systematic false positives:

1. **HLA immune region** (HLA-A, HLA-B, HLA-C, HLA-DRB1, HLA-DQB1, HLA-DPB1):
   extreme long-range LD region expected to produce LD artifacts but not genuine
   cardiometabolic enrichment.
2. **Cosmetic/pigmentation genes** (OCA2, SLC24A5, MC1R, TYR, HERC2, IRF4):
   genes with strong GWAS signals but no cardiometabolic mechanism.
3. **Blood group antigens** (ABO, RH, FUT1, FUT2, KEL): strong GWAS signals
   with distinct LD structure and zero cardiometabolic mechanism.

All three negative control sets were required to produce enrichment q > 0.05
across every method tested. The validation rule produced a hard failure (exit 1)
if any negative control set showed significant enrichment in any method, serving
as a pipeline-level quality gate.

For the permutation null, 1000 random gene sets were generated matched to the
colocalization-nominated Tier A+B gene list on three criteria per D-06c:
(a) gene length (+/- 50%), (b) LD complexity (count of independent LD blocks
within gene boundaries, proxied by SNPs with LD score > 2x chromosome mean
from baselineLD_v2.2; +/- 30%), and (c) median minor allele frequency of SNPs
within gene boundaries from 1000 Genomes Phase 3 frequency files (+/- 30%).
Query genes, negative control genes, and custom cardiometabolic pathway genes
were excluded from the candidate pool. Each permutation used a deterministic
seed (seed_base = 42 + permutation_index) for reproducibility. MAGMA gene-set
analysis was run on each of the 1000 null gene sets to generate an empirical
null distribution. The empirical p-value for the real gene set's enrichment was
computed as (n_permutations_exceeding + 1) / (n_total + 1), a conservative
estimator that avoids zero p-values.

## Software versions

| Software | Version | Reference |
|----------|---------|-----------|
| MAGMA | v1.10 | de Leeuw et al. 2015, PLoS Comput Biol |
| LDSC (Python 3 fork) | v2.0+ (abdenlab) | Bulik-Sullivan et al. 2015, Nat Genet; Finucane et al. 2015, Nat Genet |
| Baseline LD model | v2.2 | Gazal et al. 2017, Nat Genet |
| LDSC-SEG | (same as LDSC) | Finucane et al. 2018, Nat Genet |
| HESS | v0.5.4-beta | Shi et al. 2017, Am J Hum Genet |
| g:Profiler | gprofiler2 (CRAN) | Reimand et al. 2019, Nat Protoc; Kolberg et al. 2021 |
| Snakemake | 7.32.4 | Molder et al. 2021, F1000Research |
| Python | 3.11 | Python Software Foundation |

All conda environment specifications are version-pinned (REQ-9) and stored in
envs/*.yml for reproducibility.
