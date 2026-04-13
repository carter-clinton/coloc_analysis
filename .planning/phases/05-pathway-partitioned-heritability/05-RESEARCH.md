# Phase 5: Pathway + Partitioned Heritability - Research

**Researched:** 2026-04-13
**Domain:** Pathway enrichment analysis, partitioned heritability (LDSC/S-LDSC/LDSC-SEG), local genetic covariance (HESS/rho-HESS), gene-set analysis (MAGMA), functional enrichment (g:Profiler)
**Confidence:** MEDIUM-HIGH (tools are well-established in the field; installation details and Python version constraints verified; reference data download URLs confirmed)

## Summary

Phase 5 replaces the legacy ad-hoc fold-enrichment (19 hand-curated pathways, no statistical test, no null) with a multi-method, properly null-controlled pathway architecture analysis. The phase has six analytical components: (1) MAGMA gene-based + gene-set enrichment on full GWAS summary statistics, (2) g:Profiler with discoverability-matched background on the colocalization gene list, (3) LDSC partitioned heritability per pathway per trait, (4) LDSC-SEG tissue-specific heritability enrichment, (5) HESS/rho-HESS local genetic covariance at pleiotropic loci, and (6) permutation null validation with negative controls (REQ-7).

The primary technical challenge is environment setup: MAGMA v1.10 is a standalone Linux binary (NOT available via conda -- the conda `magma` packages are a computer algebra system), LDSC requires a Python 3 fork (the canonical bulik/ldsc is Python 2, bioconda package requires `python <3`), and HESS is Python 2.7-only. Each tool needs its own conda environment. Additionally, ~5 GB of reference data (baseline LD v2.2 annotations, 1000G EUR LD scores, gene location files, MSigDB GMT files, GTEx/Roadmap tissue annotations) must be downloaded before any analysis can run.

**Primary recommendation:** Create 3-4 dedicated conda environments (magma_env for the static binary + helpers, ldsc_env for the Python 3 fork, hess_env for the Python 2.7 HESS tool, and optionally gprofiler_env or reuse la_multitrait_r for g:Profiler R calls). Download all reference data as a Wave 0 prerequisite before any analytical rules execute. Structure Snakemake rules in a new `pathway.smk` file with clear separation of the six analytical components.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: Standard 4 databases (KEGG, Reactome, GO BP, MSigDB Hallmark) + 8 custom cardiometabolic pathway sets for MAGMA gene-set enrichment. Joint FDR correction. GWAS Catalog trait-associated gene sets NOT included.
- D-02: HESS/rho-HESS included in Phase 5 (not deferred). Run rho-HESS per trait pair x ancestry. Compare local covariance at pleiotropic loci vs genome-wide average.
- D-03: 5-trait union background for g:Profiler (genes within 500 kb of any genome-wide significant SNP across all 5 traits). Electronic GO annotation filtering enabled. Input = Tier A + B genes.
- D-04: LDSC baseline v2.2 (Gazal 2017, 97 annotations). EUR LD scores from 1000G Phase 3. Custom pathway gene sets as binary annotations (SNPs within 100 kb of any gene in set).
- D-05: GTEx v8 53-tissue RNA-seq AND Roadmap Epigenomics chromatin state annotations for LDSC-SEG. Test pleiotropic loci in shared tissues between trait pairs. Single-cell annotations NOT included (Phase 7).
- D-06: Reuse Phase 2 negative control gene sets (HLA, cosmetic, blood group) from config/negative_controls.yaml. All must produce enrichment q > 0.05. 1000 permutation null gene sets matched for length, LD, MAF.
- D-07: MAGMA v1.10, g:Profiler via gprofiler2 R package or Python client, LDSC v1.0.1 (Python 3 fork), HESS v0.5.x. All pinned in conda env specs (REQ-9).

### Claude's Discretion
- Specific conda environment organization (how many envs, how to partition tools)
- Snakemake rule file organization (single pathway.smk vs multiple files)
- Reference data download automation strategy
- Exact gene-to-SNP window mapping implementation for LDSC custom annotations
- Testing strategy and validation architecture

### Deferred Ideas (OUT OF SCOPE)
- Multi-ancestry LD scores (S-LDXR) for cross-ancestry partitioned heritability -- revisit at Phase 9 or Checkpoint #1
- Single-cell tissue annotations for LDSC-SEG -- Phase 7 (T3)
- PASCAL pathway-level summary statistics -- possible supplementary in Phase 11
- Per-trait g:Profiler backgrounds -- possible sensitivity analysis in manuscript
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-7 | Negative-control genes and pathways: at least 3 sets tested in Phase 5 pathway enrichment, all must show enrichment q > 0.05 | Existing config/negative_controls.yaml has HLA, cosmetic, blood group sets. Phase 2 sample_null_loci.py provides matched-null infrastructure. All 6 analytical methods (MAGMA, g:Profiler, LDSC-partitioned, LDSC-SEG, HESS, permutation) must include negative control rows. |
</phase_requirements>

## Standard Stack

### Core Tools

| Tool | Version | Purpose | Installation | Why Standard |
|------|---------|---------|--------------|--------------|
| MAGMA | v1.10 | Gene-based + gene-set analysis of GWAS data | Static Linux binary from ctg.cncr.nl [VERIFIED: web search + CNCR download page] | de Leeuw 2015; field standard for gene-set enrichment from GWAS sumstats; used by FUMA, CTG Lab, Neale Lab |
| LDSC (Python 3 fork) | v2.0.0+ | LD Score Regression: partitioned heritability, genetic correlation | git clone https://github.com/abdenlab/ldsc-python3 + poetry install [VERIFIED: GitHub README] | Bulik-Sullivan 2015; Finucane 2015; canonical tool for partitioned h2; Python 3 fork by abdenlab requires Python >3.10 |
| LDSC-SEG | (same as LDSC) | Tissue-specific heritability enrichment | Same installation as LDSC; uses Multi_tissue_gene_expr + Multi_tissue_chromatin annotations | Finucane 2018; standard tissue enrichment approach |
| HESS | v0.5.4-beta | Local SNP heritability + rho-HESS local genetic covariance | git clone https://github.com/huwenboshi/hess [VERIFIED: GitHub] | Shi 2017 AJHG; only tool for local genetic covariance from sumstats |
| gprofiler2 | CRAN current | g:Profiler REST API for functional enrichment | install.packages("gprofiler2") in R env [VERIFIED: CRAN + Kolberg 2021] | Reimand 2019 Nat Protoc recommended tool; supports custom background |

### Reference Data

| Data | Source | Size (est.) | URL |
|------|--------|-------------|-----|
| Baseline LD v2.2 scores | Broad Institute | ~1.5 GB | https://data.broadinstitute.org/alkesgroup/LDSCORE/1000G_Phase3_baselineLD_v2.2_ldscores.tgz [VERIFIED: LDSC wiki + Zenodo] |
| Regression weights | Broad Institute | ~200 MB | https://data.broadinstitute.org/alkesgroup/LDSCORE/weights_hm3_no_hla.tgz [VERIFIED: LDSC wiki] |
| HapMap3 SNP list | Broad Institute | ~5 MB | https://data.broadinstitute.org/alkesgroup/LDSCORE/w_hm3.snplist.bz2 [VERIFIED: LDSC wiki] |
| 1000G Phase 3 freq files | Broad Institute | ~500 MB | https://data.broadinstitute.org/alkesgroup/LDSCORE/1000G_Phase3_frq.tgz [VERIFIED: LDSC wiki] |
| 1000G Phase 3 plink files | Broad Institute | ~1 GB | https://data.broadinstitute.org/alkesgroup/LDSCORE/1000G_Phase3_plinkfiles.tgz [VERIFIED: LDSC wiki] |
| Multi_tissue_gene_expr LD scores | Broad Institute | ~2 GB | https://data.broadinstitute.org/alkesgroup/LDSCORE/LDSC_SEG_ldscores/Multi_tissue_gene_expr_1000Gv3_ldscores.tgz [VERIFIED: LDSC cell-type wiki] |
| Multi_tissue_chromatin LD scores | Broad Institute | ~3 GB | https://data.broadinstitute.org/alkesgroup/LDSCORE/LDSC_SEG_ldscores/Multi_tissue_chromatin_1000Gv3_ldscores.tgz [VERIFIED: LDSC cell-type wiki] |
| MAGMA gene location (GRCh37) | CNCR | ~1 MB | https://ctg.cncr.nl/software/MAGMA/aux_files/NCBI37.3.gene.loc.gz [CITED: ctg.cncr.nl/software/magma] |
| MAGMA gene location (GRCh38) | CNCR | ~1 MB | https://ctg.cncr.nl/software/MAGMA/aux_files/NCBI38.gene.loc.gz [CITED: ctg.cncr.nl/software/magma] |
| MAGMA 1000G EUR reference | CNCR | ~600 MB | https://ctg.cncr.nl/software/MAGMA/ref_data/g1000_eur.zip [CITED: ctg.cncr.nl/software/magma] |
| MAGMA SNP synonyms | CNCR | ~20 MB | https://ctg.cncr.nl/software/MAGMA/aux_files/dbsnp151.synonyms.zip [CITED: ctg.cncr.nl/software/magma] |
| MSigDB GMT files | Broad/GSEA-MSigDB | ~50 MB total | https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp [VERIFIED: MSigDB website] |
| HESS LD reference panel | UCLA Box | ~2 GB | https://ucla.box.com/shared/static/l8cjbl5jsnghhicn0gdej026x017aj9u.gz [VERIFIED: HESS docs] |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pandas | >=2.0 | Tabular data manipulation | All Python scripts: sumstats munging, result aggregation |
| numpy | >=1.24 | Numerical operations | LDSC, HESS dependencies |
| scipy | >=1.10 | Statistical tests, sparse matrix ops | LDSC, HESS eigendecomposition |
| pyyaml | >=6.0 | Config file parsing | Pipeline config loading |
| requests | >=2.28 | HTTP downloads | g:Profiler API, reference data downloads |
| bedtools | system | BED file operations | Annotation window mapping, null loci sampling |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| abdenlab/ldsc-python3 | bioconda ldsc v1.0.1 | Bioconda package requires Python 2; unsustainable for new environments |
| abdenlab/ldsc-python3 | bulik/ldsc (original) | Original requires Python 2.7 conda env; functional but maintenance risk |
| HESS (Python 2.7) | SUPERGNOVA | SUPERGNOVA does local genetic covariance too but less widely cited; HESS is the Shi 2017 standard |
| gprofiler2 R package | gprofiler Python client | Both use same REST API; R package integrates better with existing la_multitrait_r env |
| MAGMA gene-set analysis | PASCAL | PASCAL does pathway-level analysis from sumstats; deferred per D-07 context |

**Installation commands:**

```bash
# 1. MAGMA v1.10 (static binary -- NOT conda)
wget https://ctg.cncr.nl/software/MAGMA/prog/magma_v1.10.zip
unzip magma_v1.10.zip -d tools/magma_v1.10
chmod +x tools/magma_v1.10/magma

# 2. LDSC Python 3 fork
git clone https://github.com/abdenlab/ldsc-python3.git tools/ldsc
cd tools/ldsc && pip install poetry && poetry install

# 3. HESS (Python 2.7 -- needs dedicated env)
conda create -n hess_env python=2.7 numpy=1.16 pandas=0.24 scipy=1.2 pysnptools=0.3
conda activate hess_env
git clone https://github.com/huwenboshi/hess.git tools/hess

# 4. gprofiler2 (in existing R env or new)
Rscript -e 'install.packages("gprofiler2", repos="https://cloud.r-project.org")'
```

## Architecture Patterns

### Recommended Project Structure

```
src/
  snakemake/
    rules/
      pathway.smk           # NEW: all 6 pathway analysis rules
      envs/
        magma.yml            # NEW: Python helper env (not MAGMA binary itself)
        ldsc_py3.yml         # NEW: Python 3.10+ for abdenlab/ldsc-python3
        hess_py27.yml        # NEW: Python 2.7 for HESS
  python/
    run_magma.py             # NEW: MAGMA wrapper (annotation + gene analysis + gene-set)
    run_ldsc_partitioned.py  # NEW: LDSC partitioned h2 wrapper
    run_ldsc_seg.py          # NEW: LDSC-SEG tissue enrichment wrapper
    run_hess.py              # NEW: HESS/rho-HESS wrapper
    build_gprofiler_bg.py    # NEW: build discoverability-matched background gene list
    build_magma_geneset.py   # NEW: convert GMT + custom pathways to MAGMA .set format
    build_ldsc_annot.py      # NEW: create binary LDSC annotations from pathway gene sets
    extend_null_genesets.py  # NEW: extend sample_null_loci.py for gene-set-level permutation
config/
  pathway_sets/
    custom_cardiometabolic.gmt  # NEW: 8 custom pathway gene sets (D-01b)
    negative_controls.gmt       # NEW: 3 negative control pathway sets (D-06a)
  negative_controls.yaml        # EXISTING: reuse from Phase 2
  pph4_thresholds.yaml          # EXISTING: Tier A/B input threshold
  pipeline.yaml                 # EXISTING: add pathway section
data/
  reference/
    magma/                   # NEW: MAGMA binary + aux files
    ldsc/                    # NEW: baseline LD v2.2, weights, freq, plink files
    ldsc_seg/                # NEW: Multi_tissue_gene_expr + chromatin annotations
    hess/                    # NEW: HESS LD reference panel + partition files
    msigdb/                  # NEW: KEGG, Reactome, GO BP, Hallmark GMT files
results/
  pathway/
    magma/                   # MAGMA gene-based + gene-set results per trait
    gprofiler/               # g:Profiler enrichment results
    ldsc_partitioned/        # per-trait x per-pathway heritability fractions
    ldsc_seg/                # per-trait tissue-specific enrichment
    hess/                    # local genetic covariance per trait pair x ancestry
    permutation_null/        # 1000 permutation results
    negative_controls/       # negative control enrichment results for all methods
```

### Pattern 1: MAGMA Three-Step Workflow

**What:** MAGMA requires three sequential steps: (1) annotation (map SNPs to genes), (2) gene analysis (compute gene-level p-values from GWAS), (3) gene-set analysis (test enrichment). Each step produces files consumed by the next.

**When to use:** Every trait requires its own gene analysis, but annotation is shared across traits (same genome build).

**Example:**
```bash
# Step 1: Annotate SNPs to genes (once per genome build)
# Source: MAGMA manual v1.10 (ctg.cncr.nl/software/MAGMA/doc/manual_v1.10.pdf)
magma --annotate \
  --snp-loc data/reference/magma/g1000_eur.bim \
  --gene-loc data/reference/magma/NCBI37.3.gene.loc \
  --out results/pathway/magma/gene_annotation

# Step 2: Gene analysis (per trait)
magma --bfile data/reference/magma/g1000_eur \
  --pval data/processed/sumstats_harmonized/bmi_EUR.tsv N=XXX \
  --gene-annot results/pathway/magma/gene_annotation.genes.annot \
  --out results/pathway/magma/bmi_EUR

# Step 3: Gene-set analysis
magma --gene-results results/pathway/magma/bmi_EUR.genes.raw \
  --set-annot config/pathway_sets/all_pathways.set \
  --out results/pathway/magma/bmi_EUR_geneset
```
[CITED: ctg.cncr.nl/software/MAGMA/doc/manual_v1.10.pdf]

### Pattern 2: LDSC Partitioned Heritability with Custom Annotations

**What:** Add custom binary annotations (pathway gene sets) on top of the baseline v2.2 model. Each pathway is a 0/1 annotation where SNPs within 100 kb of any gene in the set are coded as 1.

**When to use:** Per-trait heritability fraction explained by each pathway.

**Example:**
```bash
# Source: LDSC wiki (github.com/bulik/ldsc/wiki/Partitioned-Heritability)
# Step 1: Munge sumstats
python ldsc.py --sumstats raw_gwas.txt \
  --merge-alleles w_hm3.snplist \
  --out munged_trait \
  --N XXX

# Step 2: Partitioned h2 with baseline + custom annotations
python ldsc.py --h2 munged_trait.sumstats.gz \
  --ref-ld-chr baseline_v2.2.,custom_pathway. \
  --w-ld-chr weights. \
  --overlap-annot \
  --frqfile-chr 1000G.EUR. \
  --out trait_pathway_h2
```
[CITED: github.com/bulik/ldsc/wiki/Partitioned-Heritability]

### Pattern 3: LDSC-SEG Tissue-Specific Analysis

**What:** Test heritability enrichment in tissue-specific gene expression and chromatin annotations.

**When to use:** Per-trait tissue enrichment to validate pleiotropic loci fall in expected tissues.

**Example:**
```bash
# Source: LDSC cell-type wiki (github.com/bulik/ldsc/wiki/Cell-type-specific-analyses)
python ldsc.py --h2-cts munged_trait.sumstats.gz \
  --ref-ld-chr baseline_v2.2. \
  --ref-ld-chr-cts Multi_tissue_gene_expr.ldcts \
  --w-ld-chr weights. \
  --out trait_tissue_enrichment
```
[CITED: github.com/bulik/ldsc/wiki/Cell-type-specific-analyses]

### Pattern 4: HESS/rho-HESS Local Genetic Covariance

**What:** Estimate local genetic covariance at specific loci to test whether trait-pair genetic correlation concentrates at colocalized loci.

**When to use:** Per trait pair x ancestry, comparing pleiotropic loci vs genome-wide average.

**Example:**
```bash
# Source: huwenboshi.github.io/hess/local_rhog/
# Step 1: Compute eigenvalues + projections (per trait)
python hess.py --local-rhog chr22 \
  --bfile reference_panel_chr22 \
  --partition partition_chr22.bed \
  --sumstats1 trait1.sumstats \
  --sumstats2 trait2.sumstats \
  --out trait_pair_chr22

# Step 2: Combine across chromosomes
python hess.py --prefix trait_pair \
  --out combined_rhog
```
[CITED: huwenboshi.github.io/hess/local_rhog/]

### Pattern 5: g:Profiler with Discoverability-Matched Background

**What:** Functional enrichment of colocalization gene list with a custom background restricted to genes discoverable by GWAS.

**When to use:** Testing whether coloc genes are enriched for specific pathways beyond what GWAS discoverability alone would predict.

**Example:**
```r
# Source: CRAN gprofiler2 vignette (cran.r-project.org/web/packages/gprofiler2/)
library(gprofiler2)

# Build background: genes within 500kb of any GWS SNP across all 5 traits
background_genes <- build_union_background(traits, window_kb = 500)

# Run enrichment
results <- gost(
  query = tier_ab_genes,
  organism = "hsapiens",
  ordered_query = FALSE,
  multi_query = FALSE,
  sources = c("GO:BP", "KEGG", "REAC"),
  evcodes = TRUE,        # exclude electronic GO annotations
  custom_bg = background_genes,
  domain_scope = "custom",
  correction_method = "fdr",
  significance_threshold = 0.05
)
```
[CITED: cran.r-project.org/web/packages/gprofiler2/vignettes/gprofiler2.html]

### Anti-Patterns to Avoid

- **Hand-rolling fold enrichment without statistical test:** The legacy pathway_enrichment_genomewide.py did exactly this -- counted genes in pathways without any significance test. Every enrichment claim must have a p-value and FDR correction.
- **Using the whole genome as g:Profiler background:** This inflates significance because GWAS-discoverable genes are already biased toward larger, more constrained genes. The 500 kb union background (D-03a) controls for this.
- **Running LDSC partitioned h2 without the baseline model:** Custom annotations alone confound with known functional categories. Always include baseline v2.2 as the joint model.
- **Forgetting --overlap-annot flag in LDSC:** Without this flag, overlapping annotations are not properly handled, producing biased enrichment estimates.
- **Using conda `magma` package:** The conda-forge/bioconda `magma` package is the MAGMA Computer Algebra System, NOT the genetics MAGMA tool. The genetics MAGMA must be downloaded as a static binary from ctg.cncr.nl.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gene-based association test | Custom SNP-to-gene aggregation | MAGMA gene analysis | MAGMA handles LD structure within genes, multi-model testing, sample size weighting |
| Gene-set enrichment from GWAS | Fisher's exact test on top genes | MAGMA gene-set analysis | MAGMA uses a competitive test that accounts for gene size, gene density, LD between genes |
| Partitioned heritability | Custom h2 partition script | LDSC S-LDSC | LDSC properly accounts for LD tagging, annotation overlap, and uses the full polygenic signal |
| Tissue enrichment | Gene-tissue overlap counts | LDSC-SEG | LDSC-SEG uses regression framework that accounts for LD and annotation correlation |
| Local genetic covariance | Manual per-locus rg calculation | HESS/rho-HESS | HESS handles LD eigendecomposition, sampling noise correction, and partition-based estimation |
| Custom background enrichment | Manual hypergeometric test | gprofiler2 with custom_bg | g:Profiler handles gene ID mapping, annotation databases, multiple testing, and background correction |
| Permutation null gene sets | Ad-hoc random sampling | Extend sample_null_loci.py | Existing infrastructure matches on gene density + region size; extend to match gene count + LD + MAF |
| GMT file parsing | Custom parser | MAGMA --set-annot or msigdbr R package | Standard formats; parsers handle edge cases (duplicate genes, aliases) |

**Key insight:** Every component of this phase has a canonical tool with >1000 citations. The risk is not "can we build it" but "can we run the standard tool correctly with proper inputs and reference data." The planner should focus on data flow correctness (correct genome build, correct column names, correct annotation format) rather than algorithm implementation.

## Common Pitfalls

### Pitfall 1: Genome Build Mismatch Between Tools
**What goes wrong:** MAGMA reference data is on GRCh37; pipeline uses GRCh37 as primary build; but some sumstats may have been lifted over or have mixed builds. LDSC baseline v2.2 is also GRCh37. HESS reference panel may be on a different build.
**Why it happens:** Each tool bundles reference data at a fixed build. Mixing builds silently misassigns SNPs to wrong genes.
**How to avoid:** Verify genome build of every input file. The pipeline.yaml states `genome_build: GRCh37` -- all sumstats must be harmonized to GRCh37 before MAGMA/LDSC input. Confirm HESS reference panel build.
**Warning signs:** Gene analysis produces zero significant genes; annotation step maps suspiciously few SNPs.

### Pitfall 2: LDSC Sumstats Munging Failures
**What goes wrong:** LDSC's munge_sumstats.py is strict about column names (SNP, N, Z, A1, A2, P). If the harmonized sumstats don't match exactly, munging fails silently or drops most SNPs.
**Why it happens:** Different GWAS studies use different column naming conventions.
**How to avoid:** Create a dedicated munging script that reads from the project's harmonized format and outputs LDSC-compatible format. Test with `--n-min 0` initially to ensure no SNPs are dropped for sample-size reasons.
**Warning signs:** Munged sumstats have <<1M SNPs when input had >5M; LDSC intercept is far from 1.0.

### Pitfall 3: HESS Python 2.7 Environment Conflicts
**What goes wrong:** HESS is written for Python 2.7.3 and uses Python 2 print statements, integer division, and older numpy API. Python 3 will fail immediately.
**Why it happens:** HESS was published in 2017 and has not been ported to Python 3.
**How to avoid:** Dedicated conda environment with `python=2.7`. Pin numpy to 1.16.x (last version supporting Python 2.7). Test the environment with `python hess.py --help` before any real analysis.
**Warning signs:** SyntaxError on import; numpy eigendecomposition returns NaN.

### Pitfall 4: MAGMA Sample Size Specification
**What goes wrong:** MAGMA requires either per-SNP sample size (N column) or a fixed N on the command line. Using the wrong N inflates/deflates gene p-values.
**Why it happens:** Meta-analyses have variable N per SNP; binary traits need effective N, not total N.
**How to avoid:** For binary traits (T2D, asthma), use effective N = 4 / (1/N_case + 1/N_ctrl). Prefer per-SNP N if available. Document the N used for each trait-ancestry combination.
**Warning signs:** Lambda_GC for gene analysis is extremely high (>2) or low (<0.8).

### Pitfall 5: g:Profiler Electronic Annotation Filtering
**What goes wrong:** Electronic GO annotations (IEA evidence code) are computationally inferred and can introduce circular enrichment (gene linked to pathway because GWAS variant was near it).
**Why it happens:** Default g:Profiler includes all evidence codes including IEA.
**How to avoid:** D-03b locks in electronic annotation filtering. In gprofiler2, set `evcodes = TRUE` to exclude IEA evidence codes. This is a non-default setting.
**Warning signs:** Very large number of enriched GO terms (>500) with vague descriptions.

### Pitfall 6: MSigDB Registration Requirement
**What goes wrong:** MSigDB GMT downloads require free registration. Automated download scripts fail with 403/redirect.
**Why it happens:** Broad Institute requires GSEA-MSigDB account for downloads.
**How to avoid:** Register at msigdb.org, then download GMT files manually or use msigdbr R package (CRAN) which provides programmatic access without registration.
**Warning signs:** Download returns HTML login page instead of GMT.

### Pitfall 7: Custom Pathway Gene Sets Have Too Few Genes
**What goes wrong:** The 8 custom cardiometabolic pathways may have only 5-20 genes each. MAGMA gene-set analysis loses power with very small sets; LDSC annotation with few genes produces unstable enrichment estimates.
**Why it happens:** Expert-curated pathway gene lists tend to be small and focused.
**How to avoid:** Supplement core pathway genes with literature-curated additions (e.g., KEGG pathway members). Report exact gene counts per set. MAGMA handles small sets better than LDSC -- for sets <20 genes, rely more on MAGMA than LDSC partitioned h2.
**Warning signs:** LDSC partitioned h2 SE for a pathway is larger than the point estimate; MAGMA competitive p-value is non-significant despite descriptive enrichment.

### Pitfall 8: LDSC-SEG .ldcts File Format
**What goes wrong:** The --h2-cts flag requires a `.ldcts` file listing tissue-specific annotation paths. This file format is tab-separated with specific path conventions.
**Why it happens:** Poorly documented format; easy to get path separators wrong.
**How to avoid:** Use the pre-built .ldcts files from the Broad download. If creating custom tissue annotations, follow the exact format: `tissue_name\tpath_to_ld_scores\tpath_to_baseline`.
**Warning signs:** LDSC exits with "No LD scores found" or silently produces all-zero results.

## Code Examples

### MAGMA Gene-Set File Format (.set)
```
# Source: MAGMA manual v1.10
# Format: one line per gene set
# SET_NAME NGENES GENE1 GENE2 GENE3 ...
KEGG_INSULIN_SIGNALING 138 3643 3667 2885 207 208 ...
CUSTOM_APPETITE_REG 8 4160 79068 627 3952 255764 ...
HALLMARK_ADIPOGENESIS 200 154 217 218 220 ...
```
[CITED: ctg.cncr.nl/software/MAGMA/doc/manual_v1.10.pdf]

### LDSC Custom Binary Annotation Format
```python
# Source: LDSC wiki - creating custom annotations
# Each annotation is a column in the .annot file (per chromosome)
# SNP  CHR  BP  CM  baseline_annot1  ...  custom_pathway1  custom_pathway2
import pandas as pd

def create_pathway_annotation(bim_file, gene_loc_file, pathway_genes, window_kb=100):
    """Create binary LDSC annotation: 1 if SNP within window_kb of any pathway gene."""
    bim = pd.read_csv(bim_file, sep='\t', header=None,
                       names=['CHR','SNP','CM','BP','A1','A2'])
    gene_loc = pd.read_csv(gene_loc_file, sep='\t',
                            names=['GENE','CHR','START','END','STRAND','SYMBOL'])
    pathway_locs = gene_loc[gene_loc['SYMBOL'].isin(pathway_genes)]

    annot = pd.Series(0, index=bim.index)
    for _, gene in pathway_locs.iterrows():
        mask = (bim['CHR'] == gene['CHR']) & \
               (bim['BP'] >= gene['START'] - window_kb * 1000) & \
               (bim['BP'] <= gene['END'] + window_kb * 1000)
        annot[mask] = 1
    return annot
```
[CITED: github.com/bulik/ldsc/wiki/Partitioned-Heritability]

### Sumstats to LDSC Munge Format
```python
# Convert project harmonized sumstats to LDSC input format
def harmonized_to_ldsc(input_path, output_path, sample_size):
    """Convert harmonized sumstats TSV to LDSC-compatible format."""
    df = pd.read_csv(input_path, sep='\t')
    ldsc_df = pd.DataFrame({
        'SNP': df['SNP'],       # rs ID required
        'A1': df['ALT'],        # effect allele
        'A2': df['REF'],        # other allele
        'N': sample_size,       # or per-SNP N if available
        'P': df['P'],
        'BETA': df['BETA'],
        'SE': df['SE'],
    })
    ldsc_df.to_csv(output_path, sep='\t', index=False)
```
[ASSUMED -- based on harmonized sumstats column conventions from datasets.yaml]

### g:Profiler Discoverability-Matched Background Construction
```python
def build_union_background(sumstats_paths, p_threshold=5e-8, window_kb=500):
    """Build 5-trait union background: genes within window of any GWS SNP.

    Per D-03a: conservative Reimand 2019 standard.
    """
    import pybedtools
    all_sig_snps = []
    for path in sumstats_paths:
        df = pd.read_csv(path, sep='\t')
        sig = df[df['P'] < p_threshold][['CHR', 'POS']]
        all_sig_snps.append(sig)

    sig_combined = pd.concat(all_sig_snps).drop_duplicates()
    # Extend each SNP to +/- window_kb
    sig_bed = pybedtools.BedTool.from_dataframe(
        sig_combined.assign(
            start=lambda x: (x['POS'] - window_kb * 1000).clip(lower=0),
            end=lambda x: x['POS'] + window_kb * 1000,
        )[['CHR', 'start', 'end']]
    ).sort().merge()

    # Intersect with gene locations to get background gene list
    genes_bed = pybedtools.BedTool('data/reference/magma/NCBI37.3.gene.loc.bed')
    bg_genes = sig_bed.intersect(genes_bed, wa=True, wb=True)
    return list(set(bg_genes.to_dataframe()['gene_symbol']))
```
[ASSUMED -- based on Reimand 2019 recommendation + D-03a decision]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LDSC baseline v1.1 (53 annotations) | Baseline LD v2.2 (97 annotations, includes LD-dependent annotations) | Gazal 2017 | More accurate heritability partitioning; v2.2 is now the minimum standard |
| Python 2 LDSC (bulik/ldsc) | Python 3 fork (abdenlab/ldsc-python3) | 2023-2024 | Python 2 EOL; py3 fork uses Poetry, works with modern numpy/scipy |
| Simple fold enrichment (Fisher test) | MAGMA competitive gene-set test | de Leeuw 2015 | Accounts for gene size, LD, gene density confounds |
| Genome-wide background for pathway enrichment | Discoverability-matched background | Reimand 2019 Nat Protoc | Controls for GWAS ascertainment bias |
| Global genetic correlation (LDSC rg) | Local genetic covariance (HESS/rho-HESS) | Shi 2017 | Identifies loci driving trait correlation; directly tests pathway-defined pleiotropy |

**Deprecated/outdated:**
- bulik/ldsc Python 2 version: Still functional but Python 2 is EOL since 2020. The abdenlab/ldsc-python3 fork is the modern alternative. [VERIFIED: GitHub]
- HESS Python 2.7: No Python 3 port exists. Must use dedicated Python 2.7 environment. [VERIFIED: HESS docs]
- Baseline v1.1 LDSC annotations: Superseded by v2.2 which adds LD-dependent annotations. Using v1.1 would be considered methodologically outdated. [CITED: Gazal 2017]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | MAGMA v1.10 Linux binary available at ctg.cncr.nl/software/MAGMA/prog/magma_v1.10.zip | Standard Stack | LOW -- URL may have changed; CNCR website was in transition (301 redirect observed). Verify download works. |
| A2 | abdenlab/ldsc-python3 supports partitioned heritability and cell-type-specific analyses identically to bulik/ldsc | Standard Stack | MEDIUM -- README confirms support but may have subtle differences. Run a known-result validation. |
| A3 | HESS v0.5.4-beta LD reference panel from UCLA Box link is still active | Standard Stack | MEDIUM -- Academic file hosting can go offline. Have fallback plan (build LD panel from 1000G plink files). |
| A4 | MSigDB GMT files can be accessed programmatically via msigdbr R package without registration | Common Pitfalls | LOW -- msigdbr is CRAN package; should work. |
| A5 | HESS partition files are included in the LD reference download | Architecture | MEDIUM -- HESS docs reference partition files separately. May need separate download. |
| A6 | Harmonized sumstats columns (CHR, POS, REF, ALT, BETA, SE, P, EAF) match what MAGMA/LDSC expect after munging | Code Examples | LOW -- munging scripts will handle conversion, but column name mapping must be tested. |
| A7 | g:Profiler evcodes=TRUE parameter excludes electronic GO annotations (IEA) | Pitfalls | MEDIUM -- gprofiler2 docs confirm evcodes parameter but exact behavior should be verified against API docs. |

## Open Questions

1. **HESS LD reference panel genome build**
   - What we know: HESS documentation references LD panels but does not clearly state the genome build
   - What's unclear: Whether the UCLA Box download is GRCh37 or GRCh38
   - Recommendation: Download and inspect the .bim file header. If GRCh38, will need liftover or a GRCh37 panel built from 1000G plink files.

2. **MAGMA CNCR website availability**
   - What we know: ctg.cncr.nl redirects to cncr.nl/ctg/. Direct download URLs may still work.
   - What's unclear: Whether the download path ctg.cncr.nl/software/MAGMA/prog/magma_v1.10.zip is still active after the redirect
   - Recommendation: Test download in Wave 0. Have GitHub mirror as fallback (several exist, e.g., Benjamin-JHou/MAGMA_Mac).

3. **LDSC Python 3 fork Poetry vs conda integration**
   - What we know: abdenlab/ldsc-python3 uses Poetry for dependency management. Snakemake --use-conda expects conda envs.
   - What's unclear: Whether Poetry-installed LDSC works inside a conda environment activated by Snakemake
   - Recommendation: Create a conda env with Python 3.11 + pip-install the Poetry dependencies directly. Test `python ldsc.py --h2 --help` works in the conda env.

4. **Custom cardiometabolic pathway gene list curation**
   - What we know: D-01b specifies 8 custom pathways. CONTEXT.md gives example genes for insulin signaling (INSR, IRS1, IRS2, PIK3CA, AKT1, AKT2).
   - What's unclear: Complete gene lists for all 8 pathways. Legacy script has partial overlap but uses different pathway names.
   - Recommendation: Curate from KEGG pathway definitions (kegg.jp). The custom_cardiometabolic.gmt file is a Wave 0 deliverable requiring literature review.

5. **HESS rho-HESS compute scaling**
   - What we know: D-02b says "moderate compute cost (~1 run per trait pair x ancestry)". 5 traits = 10 pairs, 4 ancestries = 40 runs, each across 22 chromosomes.
   - What's unclear: Per-run wall time and memory on this HPC
   - Recommendation: Pilot one trait pair x one ancestry x one chromosome. Estimate total from pilot.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| MAGMA v1.10 (genetics) | Gene-based + gene-set analysis | NO (static binary not installed; /usr/local/bin/magma is CAS, not genetics) | -- | Download from ctg.cncr.nl |
| LDSC (Python 3) | Partitioned h2, LDSC-SEG | NO (not installed) | -- | Clone abdenlab/ldsc-python3 |
| HESS | Local genetic covariance | NO (not installed) | -- | Clone from GitHub |
| gprofiler2 R package | Functional enrichment | NO (not in la_multitrait_r) | -- | install.packages() |
| Python 3.11 | LDSC Python 3 fork, Snakemake | YES (smoke_dev) | 3.11.15 | -- |
| Python 2.7 | HESS | NO (not available in current envs) | -- | conda create -n hess_env python=2.7 |
| R (with coloc, susieR) | gprofiler2 installation target | YES (la_multitrait_r) | -- | -- |
| bedtools | Null loci sampling, annotation | YES (in PATH or conda) | -- | -- |
| scipy | LDSC, HESS | NO (not in smoke_dev) | -- | Add to ldsc conda env |
| pandas | Data wrangling | YES (smoke_dev) | 3.0.2 | -- |
| numpy | Numerical ops | YES (smoke_dev) | 2.4.4 | -- |
| pyyaml | Config parsing | YES (smoke_dev) | 6.0.3 | -- |
| requests | HTTP downloads | YES (smoke_dev) | 2.33.1 | -- |
| LSF scheduler (bsub) | HPC job submission | YES | 10.1 | -- |
| GPFS filesystem | Storage | YES (169 TB free) | -- | -- |

**Missing dependencies with no fallback:**
- NONE -- all missing tools can be installed without admin privileges (static binaries, conda envs, git clones)

**Missing dependencies with fallback:**
- All 4 core tools (MAGMA, LDSC, HESS, gprofiler2) must be installed. Installation is well-documented and does not require root access.
- HESS requires Python 2.7 which is available via conda create but no longer maintained. Risk: future conda solver may not resolve Python 2.7 envs.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (in smoke_dev) + Rscript (in la_multitrait_r) |
| Config file | tests/phase2/conftest.py (existing -- extend for Phase 5) |
| Quick run command | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -x -q` |
| Full suite command | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-7-P5-01 | MAGMA gene-set enrichment includes negative control sets | unit | `pytest tests/phase5/test_magma_geneset.py::test_neg_ctrl_sets_included -x` | Wave 0 |
| REQ-7-P5-02 | g:Profiler enrichment includes negative control sets | unit | `pytest tests/phase5/test_gprofiler.py::test_neg_ctrl_enrichment_null -x` | Wave 0 |
| REQ-7-P5-03 | LDSC partitioned h2 includes negative control annotations | unit | `pytest tests/phase5/test_ldsc_partitioned.py::test_neg_ctrl_annotation -x` | Wave 0 |
| REQ-7-P5-04 | All 3 negative control sets produce enrichment q > 0.05 | integration | `pytest tests/phase5/test_negative_controls.py::test_all_methods_null -x` | Wave 0 |
| SC-1 | MAGMA gene-based + gene-set enrichment completed | smoke | `pytest tests/phase5/test_magma_geneset.py -x` | Wave 0 |
| SC-2 | g:Profiler run with discoverability-matched null | smoke | `pytest tests/phase5/test_gprofiler.py -x` | Wave 0 |
| SC-3 | LDSC partitioned h2 reported per pathway per trait | smoke | `pytest tests/phase5/test_ldsc_partitioned.py -x` | Wave 0 |
| SC-4 | LDSC-SEG tissue-specific h2 completed | smoke | `pytest tests/phase5/test_ldsc_seg.py -x` | Wave 0 |
| SC-5 | Negative-control pathway set is null (q > 0.05) | integration | `pytest tests/phase5/test_negative_controls.py -x` | Wave 0 |
| SC-6 | Permutation null for coloc gene list computed | smoke | `pytest tests/phase5/test_permutation_null.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/phase5/ -x -q --tb=short` (fast failing)
- **Per wave merge:** `pytest tests/phase5/ -v` (full verbose)
- **Phase gate:** Full suite green + Snakemake dry-run of pathway.smk before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/phase5/` directory -- does not exist yet
- [ ] `tests/phase5/conftest.py` -- shared fixtures (mock sumstats, mock gene sets, mock MAGMA output)
- [ ] `tests/phase5/test_magma_geneset.py` -- MAGMA gene-set file format validation
- [ ] `tests/phase5/test_ldsc_partitioned.py` -- LDSC annotation format + munging validation
- [ ] `tests/phase5/test_gprofiler.py` -- background construction + API call mock
- [ ] `tests/phase5/test_ldsc_seg.py` -- tissue annotation path validation
- [ ] `tests/phase5/test_negative_controls.py` -- negative control pipeline integration
- [ ] `tests/phase5/test_permutation_null.py` -- permutation gene set generation
- [ ] `envs/magma.yml` -- conda env for MAGMA helper scripts
- [ ] `envs/ldsc_py3.yml` -- conda env for abdenlab/ldsc-python3
- [ ] `envs/hess_py27.yml` -- conda env for HESS (Python 2.7)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A -- no user auth in this pipeline |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A -- all public data |
| V5 Input Validation | Yes | Validate sumstats column names/types before MAGMA/LDSC input; validate GMT file format; validate gene IDs against NCBI reference |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for This Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Command injection via file paths in subprocess calls | Tampering | Use subprocess list args (no shell=True); validate file paths before passing to MAGMA/LDSC CLI |
| Corrupted reference data (tampered downloads) | Tampering | MD5/SHA256 checksum verification after download; document expected checksums |
| g:Profiler API response spoofing | Tampering | LOW risk -- HTTPS enforced by gprofiler2; verify response schema |
| Unbounded file downloads (DoS on disk) | Denial of Service | Set explicit size limits on reference data downloads; check disk space before download |

## Sources

### Primary (HIGH confidence)
- [LDSC GitHub Wiki - Partitioned Heritability](https://github.com/bulik/ldsc/wiki/Partitioned-Heritability) -- download URLs, command syntax, reference data requirements
- [LDSC GitHub Wiki - Cell-type-specific analyses](https://github.com/bulik/ldsc/wiki/Cell-type-specific-analyses) -- LDSC-SEG download URLs, .ldcts format
- [abdenlab/ldsc-python3 GitHub](https://github.com/abdenlab/ldsc-python3) -- Python 3 fork installation, Poetry workflow, Python >3.10 requirement
- [HESS documentation](https://huwenboshi.github.io/hess/) -- Python 2.7 requirement, dependencies, LD reference panel URL
- [HESS GitHub](https://github.com/huwenboshi/hess) -- release versions (v0.5.4-beta latest)
- [CRAN gprofiler2 vignette](https://cran.r-project.org/web/packages/gprofiler2/vignettes/gprofiler2.html) -- custom_bg parameter, evcodes, domain_scope
- [MSigDB Collections](https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp) -- GMT download, Hallmark/KEGG/Reactome collections
- [MAGMA manual v1.10 PDF](https://ctg.cncr.nl/software/MAGMA/doc/manual_v1.10.pdf) -- three-step workflow, .set format, annotation syntax

### Secondary (MEDIUM confidence)
- [GWASTutorial - Gene and gene-set analysis](https://cloufield.github.io/GWASTutorial/09_Gene_based_analysis/) -- MAGMA installation walkthrough, reference data download
- [S-LDSC pipeline tutorial](https://kevinlkx.github.io/analysis_pipelines/sldsc_pipeline.html) -- end-to-end S-LDSC workflow reference
- [Zenodo S-LDSC reference files](https://zenodo.org/records/10515792) -- alternative download for baseline LD v2.2

### Tertiary (LOW confidence)
- [MAGMA CNCR download page](https://ctg.cncr.nl/software/magma) -- site was in transition (301 redirect); download URLs need re-verification

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM-HIGH -- all tools are established (>1000 citations each), versions verified via official sources. MAGMA download URL needs re-verification due to CNCR website transition.
- Architecture: MEDIUM -- Snakemake rule patterns follow project conventions from Phase 1/2. Multi-environment strategy is well-established in bioinformatics. Exact file formats for LDSC custom annotations should be validated with a pilot run.
- Pitfalls: HIGH -- all pitfalls are based on verified documentation, known Python 2/3 incompatibilities, and genome build coordination issues that are universally recognized in the field.

**Research date:** 2026-04-13
**Valid until:** 2026-05-13 (30 days -- tools are stable, reference data URLs change infrequently)
