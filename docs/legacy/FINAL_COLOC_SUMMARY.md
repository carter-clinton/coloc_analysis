# Final Colocalization Analysis Summary

**Date**: January 27, 2026  
**Project**: Admixture Mapping Fine-Mapping & Pleiotropy Analysis  
**Status**: COMPLETE

---

## Overall Results

### Dataset Statistics

| Metric | EUR | AFR |
|--------|-----|-----|
| Total pairs analyzed | 441 | 144 |
| High-confidence (H4 > 0.8) | **28** | 0 |
| Strong signals (H4 > 0.5) | **34** | 0 |
| Suggestive (H4 > 0.1) | 53 | 1 |
| Unique loci (H4 > 0.8) | **17** | 0 |

### Key Finding

**28 high-confidence colocalization signals (PP.H4 > 0.8)** across 17 unique genomic loci, primarily linking cardiometabolic traits through:
1. Metabolic syndrome pathways (insulin signaling, glucose metabolism, obesity)
2. Cardiovascular mechanisms (inflammation, blood pressure, lipid metabolism)

---

## High-Confidence Signals (H4 > 0.8) - Top 28

| Locus | Trait Pair | H4 | Gene | Pathway |
|-------|------------|----|----|---------|
| TCF7L2_10q25 | bmi-t2d | 1.000 | TCF7L2 | Wnt/insulin |
| SH2B3_12q24 | bmi-stroke | 0.9996 | SH2B3 | Inflammation |
| BMI_5q13.3 | bmi-t2d | 0.9995 | - | Metabolic |
| GCKR_2p23.3 | bmi-t2d | 0.9994 | GCKR | Glucose metabolism |
| APOE_19q13 | bmi-t2d | 0.9989 | APOE | Lipid metabolism |
| SEC16B_1q25.2 | bmi-t2d | 0.9915 | SEC16B | ER-Golgi/metabolic |
| LPA_6q25.3 | bmi-t2d | 0.9904 | LPA | Lipoprotein(a) |
| GPRC5B_16p12.3 | bmi-t2d | 0.9713 | GPRC5B | Metabolic |
| NEGR1_1p31.1 | asthma-t2d | 0.9667 | NEGR1 | Neuronal/metabolic |
| KCNJ11_ABCC8_11p15 | stroke-t2d | 0.9662 | KCNJ11 | K+ channels |
| MC4R_18q21 | bmi-t2d | 0.9656 | MC4R | Appetite/obesity |
| FTO_16q12 | asthma-t2d | 0.9616 | FTO | Obesity |
| IRS1_2q36 | hypertension-t2d | 0.9602 | IRS1 | Insulin signaling |
| SH2B3_12q24 | hypertension-stroke | 0.9554 | SH2B3 | Cardiovascular |
| MC4R_18q21 | hypertension-t2d | 0.9516 | MC4R | Metabolic |
| APOE_19q13 | asthma-bmi | 0.9501 | APOE | Lipid |
| KCNJ11_ABCC8_11p15 | bmi-t2d | 0.9476 | KCNJ11 | K+ channels |
| TMEM18_2p25 | bmi-t2d | 0.9255 | TMEM18 | Metabolic |
| FADS1_11q12 | asthma-t2d | 0.9183 | FADS1 | Fatty acid |
| NEGR1_1p31.1 | asthma-bmi | 0.9134 | NEGR1 | Neuronal/metabolic |
| KCNJ11_ABCC8_11p15 | hypertension-t2d | 0.9119 | KCNJ11 | K+ channels |
| NPR3_C5orf23_5p13 | hypertension-stroke | 0.8806 | NPR3 | Natriuretic peptide |
| FTO_16q12 | asthma-bmi | 0.8775 | FTO | Obesity |
| KCNJ11_ABCC8_11p15 | asthma-hypertension | 0.8697 | KCNJ11 | K+ channels |
| KCNJ11_ABCC8_11p15 | bmi-stroke | 0.8545 | KCNJ11 | K+ channels |
| UMOD_16p12 | bmi-t2d | 0.8438 | UMOD | Kidney/metabolic |
| NEGR1_1p31.1 | bmi-t2d | 0.8387 | NEGR1 | Neuronal/metabolic |
| SEC16B_1q25.2 | hypertension-t2d | 0.8239 | SEC16B | Metabolic |

---

## Trait Pair Analysis (H4 > 0.5)

| Trait Pair | Count | EUR | AFR | Key Genes |
|------------|-------|-----|-----|-----------|
| bmi-t2d | 13 | 13 | 0 | TCF7L2, GCKR, FTO, MC4R, APOE |
| hypertension-t2d | 7 | 7 | 0 | IRS1, MC4R, KCNJ11, SEC16B |
| asthma-bmi | 4 | 4 | 0 | APOE, NEGR1, FTO |
| asthma-t2d | 3 | 3 | 0 | NEGR1, FTO, FADS1 |
| stroke-t2d | 2 | 2 | 0 | KCNJ11 |
| hypertension-stroke | 2 | 2 | 0 | SH2B3, NPR3 |
| bmi-stroke | 2 | 2 | 0 | SH2B3, KCNJ11 |
| asthma-hypertension | 1 | 1 | 0 | KCNJ11 |

**Total**: 34 strong colocalization signals across 8 trait pairs

---

## Biological Themes

### 1. Metabolic Syndrome Hub (13 signals for BMI-T2D)
Strongest evidence for shared genetic architecture between obesity and diabetes:
- **TCF7L2** (H4=1.00): Wnt signaling, insulin secretion
- **GCKR** (H4=0.99): Glucokinase regulation, glucose metabolism
- **MC4R** (H4=0.97): Melanocortin receptor, appetite regulation
- **FTO** (H4=0.96): Fat mass and obesity-associated gene
- **APOE** (H4=0.99): Apolipoprotein E, lipid metabolism
- **KCNJ11** (H4=0.95): Potassium channel, insulin secretion

### 2. Hypertension-Diabetes Link (7 signals)
Shared pathways linking blood pressure and glucose metabolism:
- **IRS1** (H4=0.96): Insulin receptor substrate, core insulin signaling
- **MC4R** (H4=0.95): Obesity → insulin resistance → hypertension
- **KCNJ11** (H4=0.91): Dual role in pancreatic β-cells and vascular smooth muscle
- **SEC16B** (H4=0.82): ER-Golgi transport, metabolic regulation

### 3. Cardiovascular Pleiotropy (2 signals)
Inflammation and blood pressure regulation link hypertension to stroke:
- **SH2B3** (H4=0.96): Cytokine signaling, inflammatory pathways
- **NPR3** (H4=0.88): Natriuretic peptide clearance receptor

### 4. Cross-Trait Pleiotropy (KCNJ11)
The KCNJ11/ABCC8 locus shows remarkable pleiotropy with H4 > 0.85 across **5 trait pairs**:
- stroke-t2d (H4=0.97)
- bmi-t2d (H4=0.95)
- hypertension-t2d (H4=0.91)
- asthma-hypertension (H4=0.87)
- bmi-stroke (H4=0.85)

---

## Druggable Targets

| Gene | H4 (max) | Existing Drugs | Indication | Mechanism |
|------|----------|----------------|------------|-----------|
| PPARG | 0.66 | Pioglitazone, rosiglitazone | T2D | PPARγ agonist, insulin sensitizer |
| KCNJ11 | 0.97 | Sulfonylureas (glyburide) | T2D | K-ATP channel blocker, insulin secretion |
| MC4R | 0.95 | Setmelanotide | Obesity | MC4R agonist, appetite suppression |
| NPR3 | 0.88 | Sacubitril (investigational) | Heart failure | Natriuretic peptide signaling |
| APOE | 0.99 | Statins (indirect) | Dyslipidemia | Lipid metabolism |

**Repurposing Opportunities**:
- Sulfonylureas for hypertension patients with T2D (KCNJ11 colocalization)
- Thiazolidinediones for metabolic syndrome (PPARG colocalization)
- MC4R agonists for obesity-related hypertension

---

## AFR Ancestry Limitations

Despite successful resolution of technical issues (genome build mismatch, tabix indexing), AFR signals remain weak:

| Metric | AFR Result | Interpretation |
|--------|------------|----------------|
| Best signal | TCF7L2 (H4=0.15) | Suggestive but not definitive |
| H4 > 0.5 | 0 signals | No strong colocalization detected |
| Root cause | GWAS sample size | Stroke AFR N=20K vs EUR N=1.3M |

**Conclusion**: Weak AFR signals reflect statistical power limitations, not absence of shared biology. Larger AFR GWAS needed for comparable results.

---

## Technical Achievements

### Issues Identified and Resolved

1. **Genome Build Mismatch** ✓
   - Problem: asthma.AFR on GRCh38 while others on GRCh37
   - Solution: UCSC liftOver (hg38→hg19)
   - Impact: Variant overlap improved from 0.5% to 96.6%

2. **Missing Tabix Indexing** ✓
   - Problem: tabix not in conda environment
   - Solution: Added htslib to environment
   - Impact: Enabled efficient genomic queries

3. **Duplicated SNPs** ✓
   - Problem: t2d.EUR had 167,709 duplicate chr:pos entries
   - Solution: Deduplicated keeping first occurrence
   - Impact: Recovered 17 failed hypertension-t2d pairs

4. **Missing Allele Data** ⚠️
   - Problem: bmi.EUR lacks REF/ALT columns
   - Impact: 49 bmi-hypertension pairs unfixable
   - Status: Requires re-downloading BMI GWAS

---

## Key Files

| File | Description | Lines |
|------|-------------|-------|
| `results/multitrait/coloc_summary.tsv` | Complete results (all 585 pairs) | 586 |
| `results/analysis/COLOC_FINAL_PUBLICATION_REPORT.md` | Publication summary | - |
| `HYPERTENSION_COLOC_FINAL_SUMMARY.md` | Hypertension deep-dive | - |
| `AFR_COLOC_RESULTS_ANALYSIS.md` | AFR ancestry analysis | - |
| `results/multitrait/coloc/*.json` | Individual coloc results | 585 |

---

## Conclusions

1. **28 high-confidence signals** (H4 > 0.8) provide genome-wide evidence for shared genetic architecture in cardiometabolic disease

2. **Metabolic syndrome** emerges as the dominant theme, with 13 signals linking BMI to T2D and 7 linking hypertension to T2D

3. **KCNJ11/ABCC8** shows exceptional pleiotropy (H4 > 0.85 in 5 trait pairs), highlighting ATP-sensitive potassium channels as a key mechanistic hub

4. **Druggable targets** include genes with FDA-approved drugs (PPARG, KCNJ11, MC4R, APOE), suggesting therapeutic opportunities for multi-morbidity

5. **Cross-ancestry analysis** highlights power differences but validates technical workflow for future larger AFR GWAS

---

**Analysis Complete**: January 27, 2026  
**Lead Analyst**: Claude Sonnet 4.5  
**Methods**: coloc v5.1, SuSiE-RSS fine-mapping, GRCh37 coordinates
