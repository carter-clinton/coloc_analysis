# Genome-Wide Colocalization Analysis: Manuscript Summary

## Study Design

| Parameter | Value |
|-----------|-------|
| Analysis type | Genome-wide colocalization |
| Traits | BMI, T2D, Hypertension, Stroke, Asthma |
| Ancestries | EUR, AFR |
| Regions tested | 50 genome-wide significant loci |
| Total tests | 585 successful colocalization analyses |
| Method | coloc (Bayesian colocalization) |

---

## Key Results

### Signal Discovery
| Metric | Count |
|--------|-------|
| High-confidence signals (H4 ≥ 0.8) | **28** |
| Moderate signals (H4 ≥ 0.5) | 34 |
| Suggestive signals (H4 ≥ 0.2) | 44 |
| Pleiotropic loci (≥2 trait pairs) | **8** |

### Signal Quality Summary
- 28 high-confidence colocalization signals identified
- Strong concentration in metabolic trait pairs (BMI-T2D)
- 8 pleiotropic hubs affecting multiple trait combinations

---

## Top Colocalization Signals

### Perfect/Near-Perfect Colocalization (H4 ≥ 0.99)
| Region | Genes | Traits | PP.H4 | Biological Interpretation |
|--------|-------|--------|-------|---------------------------|
| TCF7L2_10q25 | **TCF7L2** | BMI-T2D | 1.0000 | Wnt signaling, insulin secretion |
| SH2B3_12q24 | SH2B3 | BMI-Stroke | 0.9996 | Inflammation, vascular |
| BMI_5q13.3 | intergenic | BMI-T2D | 0.9995 | Novel locus |
| GCKR_2p23.3 | **GCKR** | BMI-T2D | 0.9994 | Glucose metabolism |
| APOE_19q13 | **APOE** | BMI-T2D | 0.9989 | Lipid transport |

### Major Pleiotropic Hubs
| Region | Genes | Trait Pairs | Max H4 |
|--------|-------|-------------|--------|
| KCNJ11_ABCC8_11p15 | KCNJ11, ABCC8 | 5 pairs | 0.9662 |
| NEGR1_1p31.1 | NEGR1 | 3 pairs | 0.9667 |
| APOE_19q13 | APOE | 2 pairs | 0.9989 |
| FTO_16q12 | FTO | 2 pairs | 0.9616 |
| MC4R_18q21 | MC4R | 2 pairs | 0.9656 |
| SH2B3_12q24 | SH2B3 | 2 pairs | 0.9996 |
| PPARG_3p25 | PPARG | 2 pairs | 0.8992 |
| SEC16B_1q25.2 | SEC16B | 2 pairs | 0.9915 |

---

## Trait Pair Patterns

### Colocalization by Trait Pair
| Trait Pair | Total Tests | H4 ≥ 0.8 | H4 ≥ 0.5 | Interpretation |
|------------|-------------|----------|----------|----------------|
| BMI–T2D | 49 | **12** | 13 | Strongest metabolic link |
| Hypertension–T2D | 49 | 4 | 7 | Metabolic syndrome |
| Asthma–T2D | 98 | 3 | 3 | Limited overlap |
| Asthma–BMI | 49 | 3 | 4 | Obesity-inflammation |
| BMI–Stroke | 49 | 2 | 2 | Vascular connection |
| Hypertension–Stroke | 50 | 2 | 2 | Vascular risk pathway |
| Stroke–T2D | 99 | 1 | 2 | Metabolic-vascular |
| Asthma–Hypertension | 48 | 1 | 1 | Limited sharing |
| Asthma–Stroke | 94 | 0 | 0 | No genetic sharing |

### Key Observations
- **BMI-T2D** shows by far the strongest colocalization (12 of 28 high-confidence signals)
- **Asthma-Stroke** shows no colocalization despite epidemiological associations
- Metabolic traits (BMI, T2D, Hypertension) share substantial genetic architecture

---

## Ancestry Comparison

| Ancestry | Tests | H4 ≥ 0.8 | H4 ≥ 0.1 |
|----------|-------|----------|----------|
| EUR | 441 | 28 | 53 |
| AFR | 144 | 0 | 1 |

**Interpretation:** EUR dominance reflects larger GWAS sample sizes, not biological differences. The single AFR signal at exploratory threshold suggests shared architecture with substantially reduced power. Larger diverse GWAS are needed to characterize ancestry-specific effects.

---

## Pathway Enrichment

### Top Enriched Pathways
| Pathway | N Genes | Key Genes |
|---------|---------|-----------|
| Appetite regulation | 6 | MC4R, FTO, NEGR1, TMEM18, SEC16B, GPRC5B |
| Lipid transport | 2 | APOE, LPA |
| Insulin secretion | 1 | KCNJ11 |
| Glucose metabolism | 1 | GCKR |
| Wnt signaling | 1 | TCF7L2 |
| Fatty acid metabolism | 1 | FADS1 |

### Category Distribution
| Category | Gene Count |
|----------|------------|
| Metabolic | 14 |
| Lipid | 4 |
| Cardiovascular | 2 |

### Biological Interpretation
The convergence of signals on metabolic pathways supports:
1. **Metabolic syndrome as genetic entity** - Shared variants link obesity, diabetes, hypertension
2. **Appetite regulation as hub** - Multiple genes in energy homeostasis pathway
3. **Cardiovascular cascade** - Hypertension-stroke link through vascular/inflammatory genes

---

## Conclusions

1. **28 high-confidence colocalization signals identified** across 50 genomic regions

2. **BMI-T2D shows strongest genetic sharing** (12 signals), supporting integrated metabolic disease biology

3. **8 pleiotropic hubs** affect multiple trait pairs, representing priority targets for functional studies:
   - KCNJ11/ABCC8 (5 pairs) - insulin secretion
   - NEGR1 (3 pairs) - appetite regulation
   - APOE, FTO, MC4R, SH2B3, PPARG, SEC16B (2 pairs each)

4. **Asthma genetics largely independent** from cardiometabolic traits despite epidemiological comorbidity

5. **AFR signals limited by power**, highlighting need for larger diverse GWAS

---

## Files Generated

### Tables
- `Table1_HighConfidence_Signals_Annotated.tsv` - 21 high-confidence signals with gene annotations
- `pathway_enrichment_summary.tsv` - Pathway analysis results

### Source Data
- `coloc_summary.tsv` - All 585 colocalization test results
- `coloc_clean_h4.tsv` - Filtered high-quality signals

### Analysis
- `GENOME_WIDE_MANUSCRIPT_SUMMARY.md` - This summary document

---

*Generated: 2026-01-30*
*Analysis pipeline: admix_map colocalization workflow*
