# Phase 2: 3-way QTL Colocalization - Research

**Researched:** 2026-04-12
**Domain:** QTL colocalization (eQTL/pQTL/sQTL), R/Snakemake genetics pipeline, HPC
**Confidence:** MEDIUM-HIGH (data format details verified; some schema columns need first-file validation)

## Summary

Phase 2 converts Phase 1's trait-trait colocalization signals into mechanistic gene-tissue assignments by running pairwise GWAS-vs-QTL colocalization across four QTL sources: GTEx v8 eQTL (54 tissues), UKB-PPP pQTL (~2,923 proteins), GTEx v8 sQTL, and OneK1K single-cell eQTL (14 immune cell types). The central technical challenge is **coordinate harmonization**: the pipeline's GWAS sumstats and Phase 1 .fit.rds objects are on GRCh37, but all four QTL sources are on GRCh38. This requires either lifting GWAS to GRCh38 or QTL to GRCh37 before any coloc.susie call.

The coloc.susie API (coloc v5.2.3, already installed) accepts pre-fitted SuSiE objects from Phase 1 for the GWAS side, but the QTL side needs fresh SuSiE-RSS fitting with an LD matrix matched to the QTL population. For GTEx eQTL (predominantly EUR donors), the UKBB-LD tiled EUR panel from Phase 1 is appropriate. The eQTL Catalogue (EMBL-EBI) provides a uniformly processed, GRCh38-coordinate, tabixed version of GTEx v8 plus OneK1K (Release 7), which eliminates per-source format wrangling and is the recommended data source over raw GTEx Portal downloads.

**Primary recommendation:** Use the eQTL Catalogue (ftp.ebi.ac.uk) as the unified source for GTEx eQTL, sQTL, and OneK1K sc-eQTL. Lift GWAS regions from GRCh37 to GRCh38 (not vice versa) using UCSC chain files via CrossMap or pyliftover, because QTL data is natively GRCh38 and lifting fewer, well-characterized GWAS regions is safer than lifting millions of QTL associations. For UKB-PPP pQTL, download per-protein files from Synapse and harmonize to the same GRCh38 coordinate space.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01a:** GTEx v8 eQTL (54 tissues) as the backbone. All tissues, all loci -- wide-net discovery, post-hoc filtering.
- **D-01b:** UKB-PPP pQTL (Sun et al. 2023, ~2,923 proteins, Synapse) as the primary pQTL source. cis-pQTL only, within the coloc window per locus. Sample size (~54K) and structured download justify selection over deCODE.
- **D-01c:** GTEx v8 sQTL included. Adds splice-level mechanistic layer (exon-skipping, intron retention).
- **D-01d:** deCODE pQTL deferred to Phase 9 replication.
- **D-01e:** OneK1K (Yazar 2022) single-cell eQTL included -- all 14 immune cell types. Broad trigger: always run on all loci regardless of bulk GTEx results.
- **D-01f:** OneK1K hits at PP.H4 >= 0.8 are tier-eligible. QTL-source-agnostic tier system.
- **D-02a:** Primary operating threshold: PP.H4 >= 0.8.
- **D-02b:** Sweep at {0.5, 0.7, 0.8, 0.9} as supplementary sensitivity table.
- **D-02c:** Tier A/B/C definitions are mechanistic and QTL-source-agnostic.
- **D-03a:** Wide-net with post-hoc filtering. All 54 GTEx tissues for all loci.
- **D-03b:** pQTL: cis-only within the coloc window.
- **D-04a:** Three negative control gene sets: HLA-immune, cosmetic, blood group antigens.
- **D-04b:** Null threshold: PP.H4 < 0.8.
- **D-04c:** 100-1000 distance-matched random null loci for empirical calibration.
- **D-05a:** Open Targets L2G as independent corroborating evidence, NOT a gate.
- **D-05b:** Disagreements are findings.
- **D-05c:** Bulk download version-pinned Parquet from GCS.
- **D-06a:** LPA/KIV-2 brought back into Phase 2.
- **D-06b:** chr8 inversion stays deferred.
- **D-06c:** Update susie_policy.yaml with LPA/KIV-2.

### Claude's Discretion
- QTL data harmonization pipeline design (column mapping, coordinate liftover)
- Snakemake rule architecture for tissue-level dispatch (manifest pattern from Phase 1)
- OneK1K data preprocessing pipeline details
- Distance-matched null loci sampling algorithm and parameters (100-1000 range)
- Open Targets L2G version selection and Parquet parsing approach

### Deferred Ideas (OUT OF SCOPE)
- deCODE pQTL integration (Phase 9)
- chr8 inversion (8p23.1)
- Broad single-cell eQTL catalogs beyond OneK1K
- hyprcoloc multi-trait colocalization
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-3 | PP.H4 threshold sweep (not hardcoded >= 0.8) | Tier assignment logic uses config/pph4_thresholds.yaml with {0.5, 0.7, 0.8, 0.9}; coloc.susie output already includes PP.H4.abf per CS pair |
| REQ-7 | Negative-control genes and pathways | Three curated gene sets (HLA, cosmetic, blood group) + 100-1000 distance-matched null loci; bedtools shuffle with gene-density/MAF matching |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| coloc | 5.2.3 | coloc.susie() for GWAS-vs-QTL pairwise coloc | Already installed in envs/r_coloc.yml; Wallace lab standard [VERIFIED: envs/r_coloc.yml] |
| susieR | 0.14.2 | SuSiE-RSS fine-mapping for QTL sumstats | Already installed; runsusie() wrapper in coloc delegates to susie_rss() [VERIFIED: envs/r_coloc.yml] |
| data.table | 1.16.4 | Fast TSV/tabix reading for QTL files | Already installed; fread() handles gzipped TSV [VERIFIED: envs/r_coloc.yml] |
| Snakemake | 7.32.4 | Pipeline orchestration | Project standard; Python 3.11 required [VERIFIED: STATE.md] |
| synapseclient | latest | Download UKB-PPP from Synapse | Python package for programmatic Synapse access [VERIFIED: pypi.org] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| CrossMap | 0.7+ | GRCh37-to-GRCh38 coordinate liftover | Lift GWAS regions to GRCh38 for QTL matching [CITED: crossmap.sourceforge.net] |
| pyliftover | 0.4+ | Python GRCh37/38 liftover (lighter-weight) | Alternative to CrossMap for position-only liftover [CITED: pypi.org/project/pyliftover] |
| pyarrow | 10+ | Read Open Targets L2G Parquet files | Parquet I/O for L2G predictions [ASSUMED] |
| bedtools | 2.31+ | Distance-matched null loci via shuffle | Shuffle regions with constraint matching [CITED: bedtools.readthedocs.io] |
| htslib/tabix | 1.21 | Query eQTL Catalogue tabixed files | Already installed in r_coloc env [VERIFIED: envs/r_coloc.yml] |
| jsonlite | (R) | Read/write coloc output JSON | Already used in Phase 1 run_coloc_susie.R [VERIFIED: run_coloc_susie.R] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| eQTL Catalogue | Raw GTEx Portal files | eQTL Catalogue provides uniform schema, GRCh38, tabixed; raw GTEx requires per-tissue manual parsing and has inconsistent column names |
| CrossMap | pyliftover | CrossMap handles BED/VCF natively; pyliftover is position-only but faster for summary stats |
| synapseclient | AWS CLI (S3) | Synapse CLI handles auth and metadata; S3 requires unsigned access config |

**Installation (new conda env for QTL processing):**
```bash
# New envs/qtl_processing.yml
conda create -n qtl_proc python=3.11 synapseclient crossmap pyarrow pybedtools pysam
# R env already has coloc + susieR + htslib
```

## Architecture Patterns

### Recommended Project Structure
```
config/
  datasets.yaml          # Extended with QTL source stanzas
  pph4_thresholds.yaml   # New: {0.5, 0.7, 0.8, 0.9} sweep config
  negative_controls.yaml # New: 3 curated sets + matched-null spec
  susie_policy.yaml      # Updated: LPA/KIV-2 added to complex_regions
data/
  raw/
    gtex_v8/             # eQTL Catalogue tabixed files (or raw GTEx tar)
    ukbppp/              # Per-protein pQTL files from Synapse
    onek1k/              # OneK1K eQTL files (from eQTL Catalogue or onek1k.org)
    opentargets/         # L2G Parquet files
  processed/
    qtl_harmonized/      # Harmonized QTL sumstats per source/tissue/gene
    liftover/            # GRCh37<->GRCh38 chain files and lifted regions
src/snakemake/
  rules/
    qtl_coloc.smk        # New: QTL colocalization rules
    qtl_download.smk     # New: QTL data download + harmonization
    negative_controls.smk # New: null loci generation + neg control coloc
  scripts/
    run_qtl_coloc.R      # New: GWAS-vs-QTL coloc.susie wrapper
    harmonize_qtl.py     # New: column mapping + liftover
    sample_null_loci.py  # New: distance-matched null sampling
    aggregate_tiers.py   # New or extend filter_finemap_summary.py
    parse_l2g.py         # New: Open Targets L2G Parquet reader
results/
  qtl_coloc/             # Output: per-locus QTL coloc JSONs
  tiers/                 # Output: tier assignment tables
  negative_controls/     # Output: neg control coloc results
  l2g_concordance/       # Output: L2G cross-reference
```

### Pattern 1: Manifest-Driven QTL Dispatch (extends Phase 1 coloc.smk)
**What:** Build a QTL coloc manifest that cross-joins (locus x tissue x gene) for each QTL source. Each row specifies: GWAS .fit.rds path, QTL sumstats path, tissue, gene, ancestry, region.
**When to use:** For all QTL coloc rules. The manifest is the single source of truth for what to run.
**Example:**
```python
# In qtl_coloc.smk -- modeled on coloc.smk:_coloc_manifest_row()
rule build_qtl_coloc_manifest:
    """Cross-join loci x tissues x genes within each QTL source."""
    input:
        regions="config/regions_curated_grch38.csv",  # lifted
        gwas_fits=expand("results/fine_mapping/susie/{trait}/{ancestry}/{region}.fit.rds",
                         zip, trait=TRAITS, ancestry=ANCESTRIES, region=REGIONS),
        qtl_index="data/raw/gtex_v8/qtl_index.tsv",  # tissue -> file path mapping
    output:
        manifest="results/qtl_coloc/qtl_coloc_manifest.tsv",
    # Columns: qtl_coloc_id, gwas_fit_path, qtl_source, tissue, gene_id,
    #          ancestry, region, region_grch38
```

### Pattern 2: Two-Step Coloc (GWAS pre-fitted, QTL fresh-fit)
**What:** Phase 1 already produced GWAS .fit.rds (SuSiE objects). For QTL coloc, pass the GWAS fit directly and fit SuSiE-RSS on QTL sumstats in the same R script, then call coloc.susie(gwas_fit, qtl_fit).
**When to use:** Every QTL coloc call.
**Example:**
```r
# run_qtl_coloc.R (new script)
# Phase 1 GWAS fit is already a "susie" class object
gwas_fit <- readRDS(opt$gwas_fit)  # From Phase 1

# QTL sumstats need SuSiE fitting with LD
qtl_data <- list(
  beta    = qtl_df$beta,
  varbeta = qtl_df$se^2,
  snp     = qtl_df$variant_id,
  position = qtl_df$position,
  type    = "quant",
  N       = tissue_sample_size,    # Single scalar, not per-SNP
  sdY     = 1,                     # GTEx expression is inverse-normal transformed
  LD      = ld_matrix              # Matched to QTL population
)
qtl_fit <- coloc::runsusie(qtl_data, suffix = 2)

# Coloc
res <- coloc::coloc.susie(gwas_fit, qtl_fit)
```

### Pattern 3: Coordinate Liftover Strategy
**What:** Lift GWAS region coordinates from GRCh37 to GRCh38 once (small number of regions), then use GRCh38 coordinates when querying QTL data. Do NOT lift QTL data to GRCh37.
**When to use:** At the start of Phase 2 (before any QTL coloc).
**Why:** GWAS regions are ~50 curated windows; QTL data has millions of rows. Lifting fewer positions is safer and faster.
**Example:**
```python
# harmonize_qtl.py -- lift GWAS regions
from pyliftover import LiftOver
lo = LiftOver('hg19', 'hg38')

# For each region in regions_curated.csv:
# lifted = lo.convert_coordinate(f'chr{chrom}', pos)
# Write to config/regions_curated_grch38.csv
```

### Anti-Patterns to Avoid
- **Lifting millions of QTL associations to GRCh37:** Error-prone, slow, and unnecessary when the alternative is lifting ~50 GWAS regions to GRCh38.
- **Using GTEx signif_variant_gene_pairs only:** These miss sub-threshold variants needed for SuSiE fine-mapping within a window. Use allpairs from eQTL Catalogue or GTEx all_associations tar.
- **Hardcoding tissue sample sizes:** GTEx N varies by tissue (129 for Brain_Amygdala to 706 for Muscle_Skeletal). Use a lookup table, not constants.
- **Running coloc.abf instead of coloc.susie:** Phase 1 established coloc.susie as the standard. Using coloc.abf would be a regression to single-causal-variant assumption.
- **Treating L2G as a validation gate:** Per D-05a, L2G is independent evidence. Do not filter Tier A assignments based on L2G agreement.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| QTL column harmonization | Custom per-source parsers | eQTL Catalogue unified schema | eQTL Catalogue provides standardized columns across GTEx + OneK1K [CITED: ebi.ac.uk/eqtl] |
| Coordinate liftover | Position arithmetic | CrossMap or pyliftover with UCSC chain files | Chain files handle complex rearrangements; manual +/- is wrong for indels and inversions [CITED: crossmap.sourceforge.net] |
| Allele harmonization | String matching on alleles | Standardized variant_id format (chr_pos_ref_alt_b38) | eQTL Catalogue uses consistent variant_id; manual allele flipping misses strand ambiguity [CITED: eQTL Catalogue Columns.md] |
| Distance-matched null sampling | Custom random region generator | bedtools shuffle with -incl/-excl + gene density isochore matching | bedtools shuffle preserves region sizes, supports exclusion zones, and is deterministic with -seed [CITED: bedtools.readthedocs.io] |
| Parquet I/O | CSV export from web UI | pyarrow.parquet.read_table() | L2G data is ~200 Parquet files; pyarrow handles partitioned reads natively [VERIFIED: ftp.ebi.ac.uk listing] |
| SuSiE fitting on QTL data | Direct susieR::susie_rss() calls | coloc::runsusie() wrapper | runsusie() adds SNP column names, retries until convergence, and produces objects coloc.susie() consumes directly [CITED: chr1swallace.github.io/coloc] |
| GTEx tissue sample sizes | Hardcoded values | GTEx Portal tissue summary CSV or eQTL Catalogue metadata | Sample sizes range 70-706 across 49 tissues; must be looked up per analysis [CITED: gtexportal.org/home/tissueSummaryPage] |

**Key insight:** The eQTL Catalogue is the single most important "don't hand-roll" decision for this phase. It eliminates 80% of the data wrangling by providing GTEx v8 eQTL, GTEx v8 sQTL, and OneK1K sc-eQTL in a uniform schema on GRCh38 with tabix indexing. Using raw GTEx Portal + raw OneK1K files separately would triple the harmonization code.

## Common Pitfalls

### Pitfall 1: GRCh37/GRCh38 Coordinate Mismatch
**What goes wrong:** GWAS sumstats are GRCh37 (pipeline.yaml genome_build: GRCh37); GTEx v8, UKB-PPP, OneK1K, and eQTL Catalogue are all GRCh38. Running coloc with mismatched coordinates produces zero overlapping SNPs and empty results that look like "no colocalization" when actually no comparison was made.
**Why it happens:** Phase 1 operated entirely in GRCh37 space. Phase 2 introduces GRCh38-native QTL data for the first time.
**How to avoid:** Lift GWAS region windows to GRCh38 at the start of Phase 2 (Pattern 3). Create `config/regions_curated_grch38.csv`. Use GRCh38 coordinates for all QTL queries. The LD matrices from Phase 1 (UKBB-LD for EUR) are already coordinate-agnostic (they're SNP-indexed, not position-indexed). **Note:** DEF-01-04 already tracks this liftover need from Phase 1.
**Warning signs:** Zero overlapping SNPs in coloc output; all PP.H4 = 0; "no credible sets found" for every region.

### Pitfall 2: QTL Sample Size (N) Misspecification
**What goes wrong:** GTEx eQTL sample sizes vary dramatically by tissue (70 to 706). Using a wrong N biases the SuSiE-RSS fit and therefore biases PP.H4 estimates. For eQTL data, `sdY = 1` is correct because GTEx uses inverse-normal transformation, but N must be per-tissue.
**Why it happens:** Tutorials often show a single N value. GTEx metadata is in a separate file from the sumstats.
**How to avoid:** Build a tissue-to-N lookup table from GTEx metadata (available at gtexportal.org/home/tissueSummaryPage or in the eQTL Catalogue dataset_metadata.tsv). Pass N as a scalar per coloc call (not per-SNP). For UKB-PPP, N is ~54,219 (or read from the per-protein file header). For OneK1K, N is ~982 donors.
**Warning signs:** Implausibly high or low PP.H4 across all tissues; PP.H4 distribution not matching tissue sample sizes (larger N should give more power).

### Pitfall 3: Using signif_variant_gene_pairs Instead of Allpairs
**What goes wrong:** The signif_variant_gene_pairs files contain only FDR-significant eQTL associations. SuSiE-RSS needs ALL variants in the window (including non-significant) to properly estimate the posterior. Using only significant pairs makes SuSiE think there are very few variants in the region, producing artifactual single-point credible sets.
**Why it happens:** signif_variant_gene_pairs files are 100x smaller and faster to download.
**How to avoid:** Use the all-pairs (allpairs) files from GTEx or the full nominal summary statistics from eQTL Catalogue (*.all.tsv.gz). For GTEx, the allpairs tar is ~462 GB. For eQTL Catalogue, tabix queries on the full files return all variants in a window.
**Warning signs:** All credible sets have exactly 1 SNP; unrealistically tight posterior inclusion probabilities.

### Pitfall 4: LD Matrix Mismatch Between GWAS and QTL Populations
**What goes wrong:** Phase 1 GWAS SuSiE fits used UKBB-LD (EUR) or HGDP+1kG (AFR). If QTL coloc uses a different LD reference for the QTL side, the coloc.susie comparison is invalid because the credible sets were defined under different LD structures.
**Why it happens:** GTEx donors are predominantly European-American but not identical to UK Biobank.
**How to avoid:** Use the same LD panel for the QTL SuSiE fit as was used for the matched GWAS ancestry. For EUR GWAS vs GTEx eQTL, use UKBB-LD tiled EUR for both sides. The coloc.susie API compares credible sets, not raw LD.
**Warning signs:** Credible sets that don't overlap despite the same lead variant; warning messages about mismatched SNP counts.

### Pitfall 5: eQTL Catalogue Rate Limiting
**What goes wrong:** Making many tabix queries to the eQTL Catalogue FTP server triggers rate limiting or IP blacklisting, interpreted as a denial-of-service attack.
**Why it happens:** Running 50 loci x 54 tissues = 2,700 tabix queries in rapid succession.
**How to avoid:** Download the full per-tissue summary statistics files locally first (each ~1-5 GB compressed), then query locally. Do NOT use remote tabix for batch analysis. The eQTL Catalogue documentation explicitly warns about this.
**Warning signs:** HTTP 429 errors; connection refused; IP banned from ftp.ebi.ac.uk.

### Pitfall 6: HLA Region False Positive in Negative Controls
**What goes wrong:** The HLA region (6p21, 25-35 Mb) produces spurious colocalization due to extreme long-range LD, which is the entire reason it's a negative control. But PP.H4 may be nonzero (e.g., 0.3-0.5) without indicating a real problem.
**Why it happens:** Long-range LD in HLA creates correlated credible sets between unrelated traits.
**How to avoid:** The negative control pass criterion is PP.H4 < 0.8 (the operating threshold), NOT PP.H4 = 0. Per D-04b, require < 0.8 not < 0.1. Document HLA PP.H4 distribution explicitly.
**Warning signs:** HLA loci with PP.H4 in the 0.3-0.7 range are expected, not failures.

### Pitfall 7: LPA/KIV-2 Copy Number LD Artifacts
**What goes wrong:** The LPA locus (6q25-26) has KIV-2 copy number variation that creates non-standard LD patterns. SuSiE may produce credible sets that reflect copy number structure rather than single-variant causality.
**Why it happens:** KIV-2 repeat copy number varies 2-40+ copies; standard LD matrices don't capture this.
**How to avoid:** Flag LPA results with the existing complex-region policy from susie_policy.yaml. Use HGDP+1kG AFR LD panel which has better representation of LPA diversity. Report LPA findings with explicit caveats about copy number LD.
**Warning signs:** Unusually large credible sets at LPA; inconsistent results across ancestries at the same locus.

## Code Examples

### Example 1: Querying eQTL Catalogue for a Specific Gene-Tissue Window
```bash
# Source: eQTL Catalogue Data Access documentation
# Download full tissue file first (avoid remote tabix rate limiting)
wget ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000002/QTD000021/QTD000021.all.tsv.gz
wget ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000002/QTD000021/QTD000021.all.tsv.gz.tbi

# Local tabix query for a specific region (GRCh38 coordinates)
tabix QTD000021.all.tsv.gz chr16:53700000-54500000
# Returns: molecular_trait_id, variant, chromosome, position, ref, alt,
#          beta, se, pvalue, maf, an, ac, r2, gene_id, median_tpm, ...
```
[CITED: ebi.ac.uk/eqtl/Data_access/]

### Example 2: GWAS-vs-QTL coloc.susie Call
```r
# Source: coloc package vignette a06_SuSiE + Issue #178 (Chris Wallace)
# Load Phase 1 GWAS SuSiE fit (already has class "susie")
gwas_fit <- readRDS("results/fine_mapping/susie/bmi/EUR/FTO_16q12.fit.rds")
stopifnot("susie" %in% class(gwas_fit))

# Prepare QTL dataset for runsusie()
# GTEx eQTL: type="quant", sdY=1 (inverse-normal transformed), N=per-tissue
qtl_dataset <- list(
  beta     = qtl_df$beta,        # eQTL Catalogue: "beta" column
  varbeta  = qtl_df$se^2,        # eQTL Catalogue: "se" column, squared
  snp      = qtl_df$variant,     # eQTL Catalogue: "variant" column
  position = qtl_df$position,    # GRCh38 position
  type     = "quant",
  N        = 584,                # GTEx Adipose_Subcutaneous N (example)
  sdY      = 1,                  # GTEx uses inverse-normal transformation
  MAF      = qtl_df$maf,         # eQTL Catalogue: "maf" column
  LD       = ld_matrix           # Matched LD panel (UKBB-LD EUR)
)

# Check dataset validity
coloc::check_dataset(qtl_dataset, req = "LD")

# Fit SuSiE on QTL data
qtl_fit <- coloc::runsusie(qtl_dataset, suffix = 2)

# Run pairwise coloc across all credible set pairs
res <- coloc::coloc.susie(gwas_fit, qtl_fit)
# res$summary: data.frame with PP.H0.abf..PP.H4.abf per CS pair
# res$results: SNP-level posteriors assuming H4
```
[CITED: chr1swallace.github.io/coloc/articles/a06_SuSiE.html, github.com/chr1swallace/coloc/issues/178]

### Example 3: Reading Open Targets L2G Predictions
```python
# Source: Open Targets FTP (verified 2026-04-12)
import pyarrow.parquet as pq

# Download: ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/l2g_prediction/
# ~200 Snappy-compressed Parquet files, 2-7.5 MB each
l2g = pq.read_table("data/raw/opentargets/l2g_prediction/")
# Schema (verified from gentropy API docs):
#   studyLocusId: string (non-null)
#   geneId: string (non-null, Ensembl gene ID)
#   score: double (non-null, 0-1 L2G score)
#   features: array<struct{name, value, shapValue}>
#   shapBaseValue: float

# Filter for high-confidence assignments
l2g_high = l2g.filter(l2g['score'] >= 0.5).to_pandas()
```
[VERIFIED: ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/l2g_prediction/]

### Example 4: Distance-Matched Null Loci with bedtools
```bash
# Source: bedtools documentation
# Generate null loci matched by gene density and region size
bedtools shuffle \
  -i config/regions_curated_grch38.bed \
  -g data/external/hg38.chrom.sizes \
  -excl data/external/blacklist_hg38.bed \
  -incl data/external/autosomal_accessible.bed \
  -noOverlapping \
  -seed 42 \
  > results/negative_controls/null_loci_draw_001.bed

# Repeat 100-1000 times with different seeds for empirical distribution
# Post-filter: match gene density within +/- 20% of real loci
```
[CITED: bedtools.readthedocs.io/en/latest/content/tools/shuffle.html]

## Data Source Specifications

### GTEx v8 eQTL (via eQTL Catalogue)
- **FTP:** `ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/` [VERIFIED: ftp.ebi.ac.uk listing]
- **Study IDs:** GTEx_V8 (original) or GTEx (re-processed); check eQTL Catalogue Studies page
- **File format:** tabix-indexed TSV (*.all.tsv.gz + .tbi)
- **Genome build:** GRCh38 [VERIFIED: eQTL Catalogue Columns.md]
- **Variant ID format:** `chr{chrom}_{pos}_{ref}_{alt}` (GRCh38) [VERIFIED: Columns.md]
- **Key columns:** molecular_trait_id, variant, chromosome, position, ref, alt, beta, se, pvalue, maf, an, ac, gene_id, median_tpm, r2, ma_samples, type, rsid [VERIFIED: Columns.md]
- **Sample size (N):** Compute as `an / 2` (an = total allele number). Ranges 70-706 across tissues. [CITED: eQTL Catalogue Columns.md]
- **sdY for coloc:** Set to 1.0 (GTEx uses inverse-normal transformation) [CITED: github.com/chr1swallace/coloc/issues/178]
- **Coverage:** 49 tissues with >= 70 samples [CITED: GTEx 2020 Science]
- **Total download:** ~1.56 GB tar for signif_variant_gene_pairs; ~462 GB for allpairs from GTEx Portal; eQTL Catalogue per-tissue files ~1-5 GB each compressed [ASSUMED: size estimate based on partial info]

### GTEx v8 eQTL (raw from GTEx Portal -- alternative)
- **URL:** `https://storage.googleapis.com/adult-gtex/bulk-qtl/v8/single-tissue-cis-qtl/` [VERIFIED: data_access.md]
- **Files:** `GTEx_Analysis_v8_eQTL.tar` (signif pairs, ~1.56 GB); `GTEx_Analysis_v8_eQTL_all_associations.tar` (allpairs, ~462 GB requester-pays)
- **Format:** gzipped TSV per tissue
- **Columns:** gene_id, variant_id, tss_distance, ma_samples, ma_count, maf, pval_nominal, slope, slope_se [VERIFIED: Hail schema + GTEx README]
- **Variant ID format:** `{chr}_{pos}_{ref}_{alt}_b38` (note: `_b38` suffix) [VERIFIED: GTEx FAQ, web search]
- **Genome build:** GRCh38 [VERIFIED: GTEx v8 README]
- **Mapping to coloc fields:** slope -> beta, slope_se -> se, pval_nominal -> pvalue

### GTEx v8 sQTL
- **Available from:** eQTL Catalogue (uniform format) or GTEx Portal (separate tar)
- **GTEx Portal URL:** `GTEx_Analysis_v8_sQTL.tar` (signif) and `GTEx_Analysis_v8_sQTL_all_associations.tar` (allpairs)
- **Format:** Same column schema as eQTL files [ASSUMED: GTEx uses same pipeline]
- **molecular_trait_id:** Splice junction IDs (not gene IDs) -- maps to exon-skipping and intron-retention events
- **Genome build:** GRCh38 [VERIFIED: same pipeline as eQTL]

### UKB-PPP pQTL (Sun et al. 2023)
- **Synapse ID:** syn51364943 (project); syn51365301 (pGWAS summary stats) [VERIFIED: data_access.md]
- **S3 bucket:** `s3://ukbiobank.opendata.sagebase.org/` [VERIFIED: data_access.md]
- **Organization:** Per-protein files, per-chromosome within each protein: `{protein}/discovery_chr{1-22,X}_{protein_name}.gz` [CITED: cambridge-ceu.github.io/csd3/Python/Synapse.html]
- **Format:** Space-separated (raw) or tab-delimited (reformatted); bgzip-compressed [CITED: cambridge-ceu.github.io]
- **Columns (REGENIE output):** CHROM, GENPOS, ID, ALLELE0, ALLELE1, A1FREQ, INFO, N, BETA, SE, LOG10P [CITED: github.com/Gaulton-Lab/T1D_protein_biomarkers, REGENIE issues]
- **Genome build:** GRCh38 (hg38) [CITED: Gaulton-Lab notebook]
- **Sample size:** ~54,219 total; ~34,557 discovery subset [CITED: Sun 2023 Nature]
- **cis-pQTL identification:** Supplementary Table 16 from Sun 2023 contains Cis/trans classification. Standard definition: variant within ~1 Mb of protein-encoding gene TSS [CITED: Sun 2023 Nature, BMC Bioinformatics 2022]
- **coloc field mapping:** BETA -> beta, SE -> se, 10^(-LOG10P) -> pvalue, A1FREQ -> MAF, N -> N, type="quant", sdY must be estimated (protein levels are not necessarily unit-variance) [ASSUMED: sdY handling needs validation]

### OneK1K (Yazar 2022) single-cell eQTL
- **Primary download:** `onek1k.s3.ap-southeast-2.amazonaws.com` (AWS S3, ap-southeast-2) [VERIFIED: onek1k.org]
- **Alternative:** eQTL Catalogue Release 7+ (study QTS000038, 981 PBMC donors) [CITED: eQTL Catalogue Release notes]
- **File format:** TSV gzipped (.tsv.gz) per cell type + one combined file [VERIFIED: onek1k.org]
- **14 cell types:** CD4 NC, CD4 ET, CD4 SOX4, CD8 NC, CD8 ET, CD8 S100B, NK, NK R, B IN, B Mem, Plasma, Mono C, Mono NC, DC [VERIFIED: onek1k.org]
- **Sample size:** 982 donors [VERIFIED: onek1k.org, Yazar 2022 Science]
- **Genome build:** Likely GRCh37 from original publication; GRCh38 if via eQTL Catalogue [ASSUMED: needs validation at download time]
- **Recommendation:** Use eQTL Catalogue version (QTS000038) if available -- gets uniform GRCh38 schema. Otherwise download from onek1k.org and liftover if needed.

### Open Targets L2G
- **FTP path:** `ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/l2g_prediction/` [VERIFIED: ftp.ebi.ac.uk directory listing]
- **Current release:** 26.03 (latest as of 2026-04-12) [VERIFIED: ftp.ebi.ac.uk/pub/databases/opentargets/platform/]
- **Format:** ~200 Snappy-compressed Parquet files, 2-7.5 MB each [VERIFIED: ftp listing]
- **Schema:** studyLocusId (string), geneId (string, Ensembl), score (double, 0-1), features (array of struct{name, value, shapValue}), shapBaseValue (float) [VERIFIED: opentargets.github.io/gentropy API docs]
- **Score interpretation:** L2G score >= 0.5 is high-confidence gene assignment; >= 0.05 qualifies as evidence [CITED: platform-docs.opentargets.org]
- **Version pinning:** Pin to a specific release (e.g., 26.03) rather than `latest/` for reproducibility

## Coordinate Strategy (CRITICAL)

### The Problem
| Data Source | Native Build | Data Volume |
|------------|-------------|-------------|
| GWAS sumstats (Phase 1) | GRCh37 | ~50 regions x 5 traits x 4 ancestries |
| Phase 1 .fit.rds | GRCh37 | ~50 regions x trait-pair combos |
| config/regions_curated.csv | GRCh37 | 50 rows |
| GTEx v8 eQTL | GRCh38 | Millions of associations per tissue |
| UKB-PPP pQTL | GRCh38 | Millions per protein |
| OneK1K eQTL | GRCh38 (via eQTL Catalogue) | Millions per cell type |
| eQTL Catalogue | GRCh38 | Terabytes total |

### The Solution
**Lift GWAS regions to GRCh38** (not vice versa). Rationale:
1. Lifting ~50 curated regions is trivial and verifiable; lifting millions of QTL rows is error-prone
2. QTL data is natively GRCh38 -- no liftover artifacts
3. DEF-01-04 already tracks this need (GRCh38 liftover of regions_curated.csv)
4. Phase 1 .fit.rds files contain SNP names, not positions -- they can be matched by variant ID after mapping

**Implementation:**
1. Create `config/regions_curated_grch38.csv` by lifting all regions via CrossMap/pyliftover + UCSC hg19-to-hg38 chain file
2. Create a variant ID mapping table: Phase 1 SNP names (rsID or chr:pos format) -> GRCh38 variant_id (chr_pos_ref_alt)
3. For the LD matrix: UKBB-LD tiles are SNP-indexed (rsID or chr:pos), not position-indexed, so they're build-agnostic once SNPs are matched
4. Phase 1 .fit.rds objects have `$pip`, `$sets$cs`, etc. indexed by SNP name (column 1 of the LD matrix). The key is ensuring the same SNP names appear in both the GWAS fit and the QTL data.

**Critical: variant ID matching.** GTEx eQTL Catalogue uses `chr{chrom}_{pos}_{ref}_{alt}` (GRCh38). Phase 1 may use rsIDs or chr:pos (GRCh37). A mapping step is needed: use dbSNP or the eQTL Catalogue's rsid column to bridge the gap.

## Negative Control Implementation

### Curated Gene Sets (from D-04a)
```yaml
# config/negative_controls.yaml
curated_sets:
  hla_immune:
    description: "HLA region -- extreme long-range LD; expected to produce LD artifacts"
    genes: [HLA-A, HLA-B, HLA-C, HLA-DRB1, HLA-DQB1, HLA-DPB1]
    region: {chr: 6, start: 25000000, end: 35000000}  # GRCh37; lift to GRCh38
    expected: "PP.H4 may be elevated (0.3-0.7) due to LD but should not reach 0.8"

  cosmetic:
    description: "Pigmentation + eye color genes -- no cardiometabolic mechanism"
    genes: [OCA2, SLC24A5, MC1R, TYR, HERC2, IRF4]
    expected: "PP.H4 < 0.8 for all cardiometabolic trait pairs"

  blood_group:
    description: "Blood group antigens -- strong GWAS signals, distinct LD, zero cardiometabolic mechanism"
    genes: [ABO, RH, FUT1, FUT2, KEL]
    expected: "PP.H4 < 0.8 for all cardiometabolic trait pairs"
```

### Distance-Matched Null Loci (from D-04c)
**Algorithm:**
1. For each of the ~50 real loci, extract: (a) region size, (b) gene density (genes per Mb), (c) mean MAF of lead variants, (d) LD block size (estimated from LD decay)
2. Use `bedtools shuffle` with `--noOverlapping` and `-excl` (blacklist regions + real loci + centromeres) to generate candidate null regions
3. Post-filter candidates to match real loci on gene density (+/- 20%) and region size (+/- 30%)
4. Repeat with different seeds to generate 100-1000 matched null sets
5. Run the same QTL coloc pipeline on null loci to build an empirical null PP.H4 distribution
6. Report: P(PP.H4 >= 0.8 | null) as the false positive rate estimate

**Matching criteria:** Gene density is the most important confounder (gene-dense regions have more eQTL hits by chance). LD block size matters for SuSiE convergence. MAF matching controls for power differences.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| coloc.abf (single causal variant) | coloc.susie (multi-signal) | coloc v5.0 (2021) | Handles multiple causal variants at same locus; critical for complex regions |
| GTEx v6/v7 eQTL | GTEx v8 (838 donors, 54 tissues) | 2020 Science | 3x more donors, more tissues, better power |
| Per-source manual harmonization | eQTL Catalogue uniform processing | 2021 Nat Genet (Kerimov) | Standardized QTL schema; now includes sc-eQTL (OneK1K) in R7 |
| Distance-to-gene only | L2G machine learning (Open Targets) | 2021 Nat Genet (Mountjoy) | Integrates QTL coloc, VEP, enhancers into a single score; 25.03+ includes SHAP values |
| Ad-hoc QTL source selection | UKB-PPP 2,923 proteins | 2023 Nature (Sun) | Largest pQTL catalog; replaces earlier SOMAscan-based studies |
| Bulk eQTL only | sc-eQTL (OneK1K, eQTLGen Phase II) | 2022 Science (Yazar) | Cell-type-specific eQTL reveals masked signals in bulk tissue |

**Deprecated/outdated:**
- GTEx v7 eQTL files (superseded by v8; fewer samples, GRCh37 native)
- Open Targets Genetics Portal API (deprecated; replaced by Platform bulk downloads)
- SOMAscan-based pQTL catalogs (UKB-PPP Olink platform has higher protein coverage and EUR sample size)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GTEx allpairs from eQTL Catalogue is ~1-5 GB per tissue compressed | Data Source Specifications | Disk allocation may need adjustment; not a methodology risk |
| A2 | OneK1K via onek1k.org is GRCh37; via eQTL Catalogue is GRCh38 | Data Source Specifications | If both are GRCh38, no liftover needed (simplification). If onek1k.org is GRCh38, direct download also works |
| A3 | UKB-PPP sdY is NOT 1.0 (protein levels not necessarily unit-variance) | Data Source Specifications | If protein levels ARE standardized, set sdY=1; otherwise need to estimate from varbeta+MAF. Wrong sdY biases PP.H4 |
| A4 | eQTL Catalogue R7 includes OneK1K as QTS000038 | Data Source Specifications | If not yet released or has different study ID, fall back to onek1k.org direct download |
| A5 | Phase 1 .fit.rds objects use SNP names compatible with variant ID mapping | Coordinate Strategy | If .fit.rds uses positional indices without SNP names, mapping to GRCh38 QTL data requires rebuilding the SNP-to-position bridge |
| A6 | UKB-PPP REGENIE output columns are CHROM, GENPOS, ID, ALLELE0, ALLELE1, A1FREQ, INFO, N, BETA, SE, LOG10P | Data Source Specifications | If column names differ, harmonization script needs adjustment; not a design risk |

## Open Questions (DEFERRED TO EXECUTION -- Plan 02-01, Tasks 1-2)

1. **UKB-PPP sdY estimation**
   - What we know: UKB-PPP measures protein abundance via Olink PEA. REGENIE output includes BETA and SE but not the trait SD.
   - What's unclear: Whether Olink NPX values are rank-inverse-normal transformed (sdY=1) or on a natural log scale (sdY != 1). This affects coloc calibration.
   - Recommendation: Check the Sun 2023 Methods section or UKB-PPP wiki. If transformed, sdY=1. If not, coloc::estimate_sdY() from varbeta+MAF.

2. **eQTL Catalogue OneK1K availability (QTS000038)**
   - What we know: Release 7 (June 2024) added 6 sc-eQTL datasets including OneK1K.
   - What's unclear: Whether the latest eQTL Catalogue release (r8?) includes OneK1K and whether the study ID is QTS000038.
   - Recommendation: Check eQTL Catalogue Studies page at download time. If unavailable, fall back to onek1k.org S3 download.

3. **Phase 1 .fit.rds SNP naming convention**
   - What we know: run_susie_rss.R uses annotate_susie(fit, snp_names, R). The snp_names come from the LD matrix column names.
   - What's unclear: Whether these are rsIDs, chr:pos, or chr_pos_ref_alt format. This determines the variant ID mapping complexity.
   - Recommendation: Inspect a sample .fit.rds file at execution time: `fit <- readRDS("..."); head(colnames(fit$alpha))`.

4. **LD matrix build-agnosticism**
   - What we know: UKBB-LD tiles are stored as scipy sparse matrices with SNP ID indexing.
   - What's unclear: Whether the SNP IDs in UKBB-LD tiles use rsIDs (build-agnostic) or chr:pos (build-specific).
   - Recommendation: Inspect UKBB-LD metadata at execution time. If chr:pos, need to map via dbSNP.


> **Resolution strategy:** All 4 questions are empirical and will be resolved by inspecting actual data files
> during Plan 02-01 execution. Each plan task has conditional branches for each outcome.
> Q1 (sdY): Plan 02-03 Task 1 estimate_sdy.py handles both cases.
> Q2 (OneK1K availability): Plan 02-04 Task 1 download_onek1k.py has eQTL Catalogue primary / onek1k.org fallback.
> Q3 (.fit.rds SNP naming): Plan 02-01 Task 1 variant_id_map.py + Plan 02-02 Task 2 run_qtl_coloc.R handle mapping.
> Q4 (LD tile SNP IDs): Plan 02-02 Task 2 run_qtl_coloc.R inspects LD matrix metadata and maps accordingly.
## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| R + coloc | QTL coloc | Yes | 4.4.2 / 5.2.3 | -- |
| susieR | QTL SuSiE fitting | Yes | 0.14.2 | -- |
| Snakemake | Pipeline | Yes | 7.32.4 | -- |
| synapseclient | UKB-PPP download | Check | -- | pip install synapseclient |
| CrossMap | Liftover | Check | -- | pip install CrossMap; or use pyliftover |
| pyarrow | L2G Parquet | Check | -- | pip install pyarrow |
| bedtools | Null loci | Check | -- | conda install bedtools |
| htslib/tabix | eQTL Catalogue queries | Yes | 1.21 | -- |
| UCSC chain file (hg19ToHg38) | Liftover | Check | -- | Download from hgdownload.cse.ucsc.edu |

**Missing dependencies with no fallback:**
- None blocking. All missing items are pip/conda installable.

**Missing dependencies with fallback:**
- synapseclient, CrossMap, pyarrow, bedtools: all installable. Create new conda env `envs/qtl_processing.yml`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Python) + testthat (R, via Phase 1 pattern) |
| Config file | tests/phase1/conftest.py (extend for phase2) |
| Quick run command | `pytest tests/phase2/ -x --tb=short` |
| Full suite command | `pytest tests/ -x --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-3 | PP.H4 sweep produces tier counts at 4 thresholds | unit | `pytest tests/phase2/test_pph4_sweep.py -x` | Wave 0 |
| REQ-3 | pph4_thresholds.yaml loaded by Snakemake | smoke | `snakemake --configfile config_test.yaml -n qtl_coloc_sweep` | Wave 0 |
| REQ-7 | 3 negative control sets produce PP.H4 < 0.8 | integration | `pytest tests/phase2/test_negative_controls.py -x` | Wave 0 |
| REQ-7 | negative_controls.yaml loaded and validated | unit | `pytest tests/phase2/test_neg_ctrl_config.py -x` | Wave 0 |
| -- | GRCh37-to-GRCh38 liftover produces correct coordinates | unit | `pytest tests/phase2/test_liftover.py -x` | Wave 0 |
| -- | eQTL Catalogue columns parsed correctly | unit | `pytest tests/phase2/test_eqtl_catalogue_schema.py -x` | Wave 0 |
| -- | UKB-PPP columns parsed correctly | unit | `pytest tests/phase2/test_ukbppp_schema.py -x` | Wave 0 |
| -- | coloc.susie GWAS-vs-QTL produces valid output | integration | `Rscript tests/phase2/test_qtl_coloc.R` | Wave 0 |
| -- | Tier A/B/C assignment matches D-02c definition | unit | `pytest tests/phase2/test_tier_assignment.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/phase2/ -x --tb=short`
- **Per wave merge:** `pytest tests/ -x --tb=short`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/phase2/conftest.py` -- shared fixtures (toy QTL data, mock .fit.rds)
- [ ] `tests/phase2/test_liftover.py` -- GRCh37->GRCh38 coordinate validation
- [ ] `tests/phase2/test_eqtl_catalogue_schema.py` -- column parsing
- [ ] `tests/phase2/test_ukbppp_schema.py` -- column parsing
- [ ] `tests/phase2/test_pph4_sweep.py` -- threshold sweep logic
- [ ] `tests/phase2/test_negative_controls.py` -- neg control gene set validation
- [ ] `tests/phase2/test_tier_assignment.py` -- Tier A/B/C logic
- [ ] `envs/qtl_processing.yml` -- new conda env for Python QTL tools

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A -- no user auth in pipeline |
| V3 Session Management | No | N/A |
| V4 Access Control | No | File permissions only (HPC GPFS) |
| V5 Input Validation | Yes | Validate QTL file schemas before processing; reject malformed rows |
| V6 Cryptography | No | No secrets in QTL data |

### Known Threat Patterns for R/Snakemake/HPC Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed QTL file injection | Tampering | Schema validation on download; checksum verification |
| Synapse credential exposure | Information Disclosure | Use synapseclient token auth; never commit tokens; .gitignore .synapseConfig |
| Path traversal in manifest | Tampering | Whitelist-validate pair_id format (existing wildcard_constraints pattern) |
| Disk exhaustion from allpairs download | Denial of Service | Pre-check disk quota; download per-tissue not bulk tar |

## Sources

### Primary (HIGH confidence)
- [eQTL Catalogue Columns.md](https://github.com/eQTL-Catalogue/eQTL-Catalogue-resources/blob/master/tabix/Columns.md) -- complete column schema for QTL summary statistics
- [coloc vignette a06_SuSiE](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html) -- coloc.susie workflow and runsusie() usage
- [coloc Issue #178](https://github.com/chr1swallace/coloc/issues/178) -- Chris Wallace guidance on MAF, N, sdY for eQTL data
- [coloc source R/susie.R](https://rdrr.io/cran/coloc/src/R/susie.R) -- verified `"susie" %in% class()` check for pre-fitted objects
- [GTEx v8 README](https://github.com/broadinstitute/gtex-v8/blob/master/README.md) -- GRCh38 build, file types
- [GTEx v8 eQTL schema (Hail)](https://hail.is/docs/0.2/datasets/schemas/GTEx_eQTL_Stomach_all_snp_gene_associations.html) -- variant_id, gene_id, slope, slope_se, maf columns
- [Open Targets FTP](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/) -- verified l2g_prediction directory with Parquet files
- [Open Targets L2G schema](https://opentargets.github.io/gentropy/python_api/datasets/l2g_prediction/) -- studyLocusId, geneId, score schema
- [OneK1K website](https://onek1k.org/) -- S3 download paths, 14 cell types, file format
- [eQTL Catalogue Release notes](https://www.ebi.ac.uk/eqtl/Release_notes/) -- R7 includes OneK1K (QTS000038)
- [envs/r_coloc.yml](envs/r_coloc.yml) -- verified coloc 5.2.3, susieR 0.14.2
- [data_access.md](.planning/data_access.md) -- GTEx, UKB-PPP, OneK1K access status

### Secondary (MEDIUM confidence)
- [cambridge-ceu Synapse guide](https://cambridge-ceu.github.io/csd3/Python/Synapse.html) -- UKB-PPP file organization (per-protein, per-chromosome)
- [Gaulton-Lab T1D notebook](https://github.com/Gaulton-Lab/T1D_protein_biomarkers/blob/main/TwoSampleMR_pQTL_T1D_no_UKB_SuSiE.ipynb) -- UKB-PPP column names, GRCh38 build
- [bychen9 eQTL_colocalizer](https://github.com/bychen9/eQTL_colocalizer) -- GTEx coloc pipeline methodology
- [bedtools shuffle docs](https://bedtools.readthedocs.io/en/latest/content/tools/shuffle.html) -- null region generation
- [CrossMap docs](https://crossmap.sourceforge.net/) -- liftover best practices

### Tertiary (LOW confidence)
- UKB-PPP allpairs file size estimate (~462 GB) -- based on web forum mentions, not official docs
- OneK1K genome build from original publication (GRCh37) -- inferred from eQTL Catalogue needing to re-process to GRCh38

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified in existing conda env or official packages
- Architecture: HIGH -- extends proven Phase 1 manifest-driven dispatch pattern
- Data formats: MEDIUM-HIGH -- eQTL Catalogue schema verified from Columns.md; UKB-PPP schema verified from multiple secondary sources but first-file validation needed
- Coordinate strategy: HIGH -- GRCh37-to-GRCh38 liftover is well-established; DEF-01-04 already tracks this
- Pitfalls: HIGH -- based on published coloc best practices and Phase 1 lessons learned
- Negative controls: MEDIUM -- methodology established (bedtools + gene-density matching) but parameters need tuning at runtime

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (30 days -- stable domain; eQTL Catalogue may release r8 with updated OneK1K)
