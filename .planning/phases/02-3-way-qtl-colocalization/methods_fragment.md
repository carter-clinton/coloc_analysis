# Phase 2 Methods Fragment -- 3-Way QTL Colocalization

Prepared for Phase 11 manuscript assembly. This fragment documents the Phase 2
analytical pipeline that converts Phase 1 trait-trait colocalization signals into
mechanistic gene-tissue-cell-type assignments through four QTL data sources,
tiered confidence levels, negative controls, and independent validation via
Open Targets Locus2Gene.

Original research framing: this is Carter K. Clinton's hypothesis-driven
cross-ancestry colocalization study at the ASHES Lab, NCSU. Phase 2 extends the
coloc.susie fine-mapping spine from Phase 1 into a gene-resolution mechanistic
framework by integrating expression, splicing, and protein QTL evidence with
single-cell resolution.

## QTL colocalization analysis

### Data sources

Four QTL data sources provide complementary mechanistic layers:

1. **GTEx v8 eQTL** (49 tissues with sample size >= 70; via eQTL Catalogue,
   EMBL-EBI, study QTS000002). Inverse-normal transformed expression; sdY = 1.0.
   Per-tissue sample sizes range from 73 (Cells_Leukemia_cell_line_CML) to 706
   (Muscle_Skeletal). All tissues are tested at all loci (wide-net discovery per
   D-03a); post-hoc filtering identifies the resolving tissue(s).

2. **GTEx v8 sQTL** (splice quantitative trait loci; via eQTL Catalogue,
   same study). Molecular trait ID encodes the splice junction. Adds a
   splicing-level mechanistic layer (exon-skipping, intron retention, alternative
   donor/acceptor) orthogonal to expression-level eQTL.

3. **UKB-PPP pQTL** (Sun et al. 2023; approximately 2,923 proteins measured by
   Olink NPX in 54,219 individuals; cis-pQTL only, within 1 Mb of gene TSS).
   Downloaded from Synapse (syn51364943) or the corresponding S3 open data
   bucket. sdY is estimated from summary statistics (SE, MAF, N) because Olink
   NPX values may not be unit-variance. REGENIE output format: LOG10P is
   converted to p-value via 10^(-LOG10P), with LOG10P clipped to [0, 300] to
   prevent invalid p-values.

4. **OneK1K sc-eQTL** (Yazar et al. 2022; 14 immune cell types in 982 donors;
   via eQTL Catalogue QTS000038 or onek1k.org S3 fallback). Cell types: CD4_NC,
   CD4_ET, CD4_SOX4, CD8_NC, CD8_ET, CD8_S100B, NK, NK_R, B_IN, B_Mem, Plasma,
   Mono_C, Mono_NC, DC. Provides cell-type resolution within immune compartment,
   complementing bulk GTEx tissue resolution. All cell types are tested at all
   loci (broad trigger per D-01e).

### Coordinate harmonization

All QTL data sources are natively on GRCh38. GWAS summary statistics and Phase 1
.fit.rds objects are on GRCh37. Region coordinates are lifted from GRCh37 to
GRCh38 using pyliftover (v0.4+) with the UCSC hg19-to-hg38 chain file. Lifting
the fewer, well-characterized GWAS regions (12 curated loci) to GRCh38 is safer
than lifting millions of QTL associations in the reverse direction.

Chain file integrity is verified at download: file size must exceed 100 KB
(tamper check). Lifted coordinates are recorded in config/regions_curated_grch38.csv
with lift_status="OK" for all 12 regions.

### Harmonized intermediate format

Per-source harmonization scripts (harmonize_eqtl.py, harmonize_sqtl.py,
harmonize_pqtl.py, harmonize_onek1k.py) convert each QTL source to a common
tab-separated intermediate with standardized columns: variant_id, chr, position,
beta, se, maf, pvalue, N, sdY, gene_id, tissue. This format is consumed by
run_qtl_coloc.R without source-specific conditional logic.

### coloc.susie workflow

GWAS-vs-QTL colocalization uses coloc::coloc.susie (coloc v5.2.3). The GWAS
side is represented by pre-fitted SuSiE objects (.fit.rds files from Phase 1),
avoiding redundant re-fitting. The QTL side is fitted fresh via
coloc::runsusie(suffix=2) with SuSiE-RSS and an LD matrix matched to the QTL
study population. For GTEx and OneK1K (predominantly European donors), the
UKBB-LD tiled EUR panel from Phase 1 is used.

The pipeline is manifest-driven: a QTL coloc manifest cross-joins
(locus x tissue x gene x QTL_source x ancestry), and each row dispatches to a
single run_qtl_coloc.R invocation. Output is a JSON containing the summary
posterior (PP.H0 through PP.H4), pairwise credible-set comparisons, and metadata
(n_cs_gwas, n_cs_qtl, n_snps_overlap).

### Sample sizes and sdY

- GTEx eQTL/sQTL: per-tissue N from eQTL Catalogue metadata (an / 2).
- UKB-PPP pQTL: N = 54,219. sdY estimated from summary statistics.
- OneK1K sc-eQTL: N = 982. sdY = 1.0 (inverse-normal transformed by eQTL
  Catalogue processing pipeline).

## Tier assignment

Loci are assigned to three confidence tiers based on the combination of
trait-trait and QTL colocalization evidence. Tier definitions are mechanistic
and QTL-source-agnostic (D-02c): the tier system evaluates whether the causal
gene and tissue/cell-type are resolved, not which dataset resolved them.

- **Tier A:** Trait-trait coloc PP.H4 >= 0.8 AND QTL coloc PP.H4 >= 0.8, fully
  resolving causal gene and tissue/cell-type. Records the resolving gene,
  tissue, QTL source, and all supporting QTL sources.

- **Tier B:** Trait-trait coloc PP.H4 >= 0.8 AND QTL coloc PP.H4 >= 0.5 but
  < 0.8. Evidence exists for a causal gene/tissue but not all lines of evidence
  converge at the operating threshold.

- **Tier C:** Trait-trait coloc PP.H4 >= 0.8 only. No QTL support at the
  operating threshold. These loci have trait-level pleiotropic evidence but
  unresolved causal mechanism.

All thresholds are loaded from config/pph4_thresholds.yaml (T-02-16 mitigation:
no hardcoded thresholds).

### PP.H4 threshold sweep

A sensitivity analysis computes tier counts at four PP.H4 threshold values:
{0.5, 0.7, 0.8, 0.9} (REQ-3). The sweep table reports n_tier_a, n_tier_b,
n_tier_c per ancestry per threshold. This addresses the methodological concern
that PP.H4 = 0.8 is a convention (Wallace 2021), not a natural cutoff, and
demonstrates how tier assignments shift under alternative thresholds. The
primary analysis uses 0.8; the sweep is reported as a supplementary sensitivity
table.

## Negative controls

Three curated negative control gene sets and a distance-matched null locus
distribution provide empirical validation that the PP.H4 threshold discriminates
real colocalization from spurious signals (REQ-7).

### Curated negative control sets

1. **HLA-immune** (6 genes: HLA-A, HLA-B, HLA-C, HLA-DRB1, HLA-DQB1, HLA-DPB1;
   chr6:25-35 Mb). Expected behavior: PP.H4 may be elevated (0.3-0.7) due to
   extreme long-range LD in the MHC region, but must not reach the 0.8 operating
   threshold. This set tests the complex-region SuSiE policy.

2. **Cosmetic/pigmentation** (6 genes: OCA2, SLC24A5, MC1R, TYR, HERC2, IRF4).
   Expected behavior: PP.H4 < 0.8 for all cardiometabolic trait pairs. These
   loci have strong GWAS associations for non-cardiometabolic phenotypes (eye
   color, skin pigmentation) with distinct LD structure.

3. **Blood group antigens** (5 genes: ABO, RH, FUT1, FUT2, KEL). Expected
   behavior: PP.H4 < 0.8 for all cardiometabolic trait pairs. Well-mapped
   loci with strong GWAS signals but zero cardiometabolic mechanism.

### Distance-matched null loci

500 sets of distance-matched null loci are generated via bedtools shuffle
(seed_base = 42 + draw_id for reproducibility; T-02-18 mitigation). Null loci
are matched to real curated loci on region size (tolerance +/- 30%) and gene
density (tolerance +/- 20%). Exclusion zones prevent overlap with real loci,
centromeres, and ENCODE hg38 blacklist regions.

The matched null distribution provides an empirical PP.H4 null for estimating
the false positive rate at any threshold. Pass criterion: curated negative
control sets show PP.H4 < 0.8 for all cardiometabolic trait pairs.

## Locus2Gene concordance

Open Targets Locus2Gene (L2G) v26.03 predictions provide independent
corroboration of causal gene assignments (D-05a). L2G predictions are
downloaded as version-pinned Parquet files and filtered to high-confidence
assignments (score >= 0.5).

For each Tier A locus, the L2G top gene (highest score at that locus) is
compared to the QTL coloc resolving gene. Concordance rate is computed as the
fraction of Tier A loci where the QTL coloc gene matches the L2G top gene.

Disagreements are interpreted as findings, not failures (D-05b). A Tier A locus
where QTL coloc assigns a non-nearest gene while L2G assigns the nearest gene
may indicate distal enhancer-driven regulation -- a mechanistically interesting
result. These cases are annotated as "distal_enhancer_candidate" in the
concordance table.

## Gene x tissue x cell-type matrix

The final Phase 2 output is a gene x tissue x cell-type matrix assembling all
QTL coloc results above the PP.H4 threshold. The matrix is produced in two
formats:

1. **Wide format** (heatmap-ready): rows = (gene_id, region), columns =
   (tissue.qtl_source), values = max PP.H4 across credible set pairs. Column
   labels combine tissue/cell_type with QTL source for unambiguous identification
   (e.g., "Adipose_Subcutaneous.gtex_eqtl", "CD4_NC.onek1k_sceqtl").

2. **Long format** (analysis-ready): gene_id, region, tissue, qtl_source,
   PP.H4.abf. Supports downstream filtering, grouping, and statistical testing.

The matrix columns span up to 49 GTEx tissues (eQTL), 49 GTEx tissues (sQTL),
approximately 2,923 proteins (pQTL), and 14 OneK1K immune cell types (sc-eQTL).

## Complex regions

LPA/KIV-2 (6q25-26) is reintroduced in Phase 2 with an explicit caveat about
KIV-2 copy number variation creating LD artifacts. The existing BMI-T2D anchor
from Phase 1 (PP.H4 = 0.990, rank 7) provides trait-trait evidence; QTL coloc
adds gene-level resolution. Results are flagged with the susie_policy.yaml
pre-specified complex region entries.

HLA (6p21) is included as a negative control. The block-diagonal LD
approximation from Phase 1 (UKBB-LD tiled) is reused; this limitation is
documented in the methods and per-locus QC dashboard.

## Software and versions

- R 4.4.2 (coloc 5.2.3, susieR 0.14.2)
- Python 3.11 (pandas, pybedtools, pyarrow, pyyaml, pyliftover)
- Snakemake 7.32.4
- bedtools 2.31+
- eQTL Catalogue FTP (ftp.ebi.ac.uk)
- Synapse Python client (synapseclient) for UKB-PPP download
- Open Targets L2G v26.03 Parquet
