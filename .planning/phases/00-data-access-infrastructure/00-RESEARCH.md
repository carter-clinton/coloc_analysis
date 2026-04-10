# Phase 0: Data access + infrastructure - Research

**Researched:** 2026-04-10
**Domain:** Snakemake pipeline infrastructure, conda reproducibility, HPC/LSF integration, GWAS sumstats harmonization
**Confidence:** HIGH

## Summary

Phase 0 is a refactor-and-extend infrastructure phase with two parallel tracks: Track 0a (data registration/downloads -- all same-day except AoU which is already credentialed) and Track 0b (pipeline infrastructure: parameterize 174 hardcoded paths, pin conda envs, build a Snakemake skeleton from legacy rules, create a 3-locus CI smoke test, and submit an OSF pre-registration). The legacy codebase is far more mature than a bare scaffold -- 60+ Python/R scripts, 8 modular Snakemake rules, a working Snakefile, and existing config/dataset YAML files. The infrastructure task is to modernize and decouple this code from hardcoded NCSU-specific paths, pin reproducible environments, and wire it into a top-level Snakefile at the project root.

The existing HPC environment has LSF (bsub/bjobs/bqueues confirmed), conda 26.1.1, Snakemake 7.32.4 in an existing env, R 4.4.2 with coloc 5.2.3 and susieR 0.14.2 in the `la_multitrait_r` env, and Python 3.9.25 in the base environment. The `short` queue is confirmed available with 2560 slots. The critical Snakemake version decision is whether to stay on 7.32.4 (compatible with existing `--cluster` invocation patterns) or upgrade to 8.x (which requires migrating to the executor plugin system). This research recommends staying on Snakemake 7.32.x for Phase 0 stability and deferring the 8.x migration.

**Primary recommendation:** Stay on Snakemake 7.32.x, use the two-file conda pinning strategy (loose YAML + `conda list --export` lockfile), parameterize paths via a hierarchical `config/pipeline.yaml`, and build the smoke test from 3 well-characterized legacy loci (FTO, TCF7L2, SH2B3) with pre-computed expected PP.H4 values from legacy results.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Primary coordinate system is GRCh37 (hg19). Do not migrate to GRCh38 as primary.
- **D-02:** Add a liftover utility for sources only available in GRCh38 (e.g., newer FinnGen R13/R14). Use UCSC liftOver chain files.
- **D-03:** Record genome build per dataset in `data/manifest.yaml`.
- **D-04:** Refactor and modularize the legacy Snakemake workflow -- do not rewrite from scratch. The 8 legacy rules contain tested logic.
- **D-05:** Move refactored rules to `src/snakemake/rules/`. Each rule file is self-contained.
- **D-06:** Add YAML schema validation per trait/ancestry pair using `src/snakemake/schemas/`.
- **D-07:** Top-level `Snakefile` at project root imports all rules. Profile for LSF cluster via `config/cluster_lsf.yaml`.
- **D-08:** Create `config/pipeline.yaml` as single source of truth for all filesystem paths.
- **D-09:** 174 hardcoded paths collapse to ~5-6 root path variables. Scripts access paths through Snakemake `config` dict or R config loader.
- **D-10:** Acceptance test: `grep -r "admixmap|admix_map|/share/clintonlab|/rs1/researchers|/gpfs_common" src/R src/python src/snakemake config` returns 0 matches.
- **D-11:** Maintain symlink strategy -- data stays on `/rs1`, symlinked into `data/`.
- **D-12:** Add `data/manifest.yaml` cataloging all data sources.
- **D-13:** New downloads go to `data/raw/{source_name}/`, processed to `data/processed/{source_name}/`.
- **D-14:** Toy dataset = 3 well-characterized loci with known PP.H4 > 0.8.
- **D-15:** Test lives in `tests/toy_3locus/` with its own `Snakefile.test` and `config_test.yaml`.
- **D-16:** Pass criteria: pipeline completes, PP.H4 within +/-0.05 of legacy, all intermediates exist.
- **D-17:** Run via `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` in under 15 min.
- **D-18:** Fix corrupted Tables 1, 3, S4 per Revision_Plan.md section 10.
- **D-19:** Drop KCNJ11 asthma-HTN Tier-1 signal (n_SNPs=6 < 50 threshold).
- **D-20:** Ingest new sumstats: AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann), AFR T2D, EAS (BBJ), Hispanic (PAGE/HCHS-SOL).
- **D-21:** Add entries to `config/datasets.yaml` with column maps.
- **D-22:** Update `config/pipeline.yaml` to add EAS and HIS to ancestries list.
- **D-23:** Pin all conda envs under `envs/*.yml` with exact versions (`package=version=build`).
- **D-24:** Core envs: `envs/r_coloc.yml`, `envs/python_stats.yml`, `envs/plink.yml`.
- **D-25:** Each Snakemake rule declares `conda:` directive pointing to appropriate env file.
- **D-26:** Submit OSF pre-registration.

### Claude's Discretion
- Exact choice of 3 toy loci for CI smoke test
- Column mapping specifics for new ancestry GWAS datasets
- R config loader implementation details (`src/R/utils/load_config.R`)
- Snakemake profile specifics for LSF (memory, queue, walltime defaults)
- Whether to use Docker/Singularity containers in addition to conda (nice-to-have, not required)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-1 | Data access runs in parallel from Day 1 -- complete Day-1 action checklist | All 7 open-access sources confirmed reachable (data_access.md verified 2026-04-09). AoU already credentialed. No DUA gates for T1. Track 0a is same-day registration/download work. |
| REQ-9 | Snakemake pipeline has a CI smoke test -- toy 3-locus subset completes in <15 min with pinned envs | Legacy has 8 curated regions and 205 tiled regions with known PP.H4 values. FTO, TCF7L2, SH2B3 recommended as test loci. Snakemake 7.32.4 with `--use-conda` supports per-rule env isolation. |
| REQ-12 | Legacy path references are parameterized -- grep returns 0 matches | 117 hardcoded occurrences across 49 scripts (excluding the 7,150-row manifest TSV). Collapse to ~5-6 root variables in `config/pipeline.yaml`. R scripts need a config loader function. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Snakemake | 7.32.4 | Workflow engine | Already installed and tested; 8.x migration deferred (see Architecture Patterns) [VERIFIED: `/rs1/researchers/c/ckclinto/conda_envs/snakemake/bin/snakemake --version` returns 7.32.4] |
| R | 4.4.2 | Statistical computing | Already installed in `la_multitrait_r` env [VERIFIED: env check] |
| coloc | 5.2.3 | Bayesian colocalization | Installed in `la_multitrait_r`; includes `coloc.susie` [VERIFIED: `packageVersion('coloc')` returns 5.2.3] |
| susieR | 0.14.2 | Sum of Single Effects fine-mapping | Installed in `la_multitrait_r` [VERIFIED: env check] |
| Python | 3.11 | Pipeline scripting | Legacy env spec targets 3.11; base env has 3.9.25 [VERIFIED: base env] |
| conda | 26.1.1 | Environment management | Already installed [VERIFIED: `conda --version`] |
| PLINK 1.9/2.0 | TBD | Genotype processing | Legacy env includes `plink`; not in base PATH [VERIFIED: not in base PATH] |
| bcftools | TBD | VCF/BCF manipulation | Legacy env includes `bcftools` [ASSUMED] |
| htslib (tabix/bgzip) | TBD | Indexed file operations | Legacy R env and Snakemake env both include htslib [VERIFIED: legacy env ymls] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| r-data.table | TBD | Fast tabular I/O in R | Reading large sumstats files [VERIFIED: in legacy r_stats_env.yml] |
| r-optparse | TBD | R CLI argument parsing | All R scripts called from Snakemake shell directives [VERIFIED: in legacy env] |
| pandas | TBD | Python data manipulation | Sumstats harmonization, manifest building [VERIFIED: in legacy snakemake_env.yml] |
| pyarrow | TBD | Columnar data I/O | Fast parquet/feather for large datasets [VERIFIED: in legacy env] |
| pyyaml | TBD | YAML parsing in Python | Reading config files in scripts [VERIFIED: in legacy env] |
| requests | TBD | HTTP downloads | Sumstats download rule [VERIFIED: used in legacy sumstats.smk] |
| loguru | TBD | Python logging | Pipeline diagnostics [VERIFIED: in legacy env via pip] |
| conda-lock | latest | Lockfile generation | Cross-platform reproducible env pinning [ASSUMED -- needs install] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Snakemake 7.32.x | Snakemake 8.x/9.x | 8.x requires executor plugin migration (`--cluster` removed, `--use-conda` deprecated in favor of `--software-deployment-method conda`). Legacy scripts and run_snakemake.sh use 7.x syntax. Upgrade is sound but costs extra refactoring for zero Phase 0 benefit. Defer to Phase 1 if needed. |
| conda-lock | pixi | Pixi is the Snakemake team's preferred direction for env management, but Snakemake 7.x does not support pixi natively. conda-lock generates lockfiles from existing env YAML files, which is what we have. |
| Per-rule conda envs | Single monolithic env | Per-rule envs (D-25) isolate R from Python dependencies, preventing version conflicts between coloc/susieR (R) and pandas/LDSC (Python). Standard Snakemake best practice. |
| MungeSumstats (R) | Custom harmonize_sumstats.py | Legacy already has a working `harmonize_sumstats.py` with per-dataset column maps in `datasets.yaml`. MungeSumstats handles more edge cases but would require rewriting the existing harmonization pipeline. Stick with legacy approach per D-04. |

**Installation (new env creation):**
```bash
# Snakemake orchestrator env (already exists, verify)
conda activate snakemake

# Or create fresh with pinned versions:
conda create -n snakemake_coloc python=3.11 snakemake=7.32.4 pandas numpy scipy pyarrow pyyaml click requests htslib -c conda-forge -c bioconda

# R coloc env (seed from legacy la_multitrait_r, pin versions)
conda create -n r_coloc r-base=4.4.2 r-coloc=5.2.3 r-susieR=0.14.2 r-data.table r-tidyverse r-optparse htslib -c conda-forge -c bioconda

# PLINK env
conda create -n plink_coloc plink plink2 bcftools -c bioconda -c conda-forge
```

## Architecture Patterns

### Recommended Project Structure

```
coloc_analysis/                     # Project root (git root)
|-- Snakefile                       # Top-level: imports rules, defines all targets
|-- config/
|   |-- pipeline.yaml               # Single source of truth for paths (D-08)
|   |-- datasets.yaml               # Per-source column maps (extended from legacy)
|   |-- cluster_lsf.yaml            # LSF profile (seeded from legacy)
|   |-- regions_curated.csv         # 8 curated region definitions
|   |-- regions_tiled.csv           # 205 tiled sub-regions
|-- envs/
|   |-- r_coloc.yml                 # R + coloc + susieR + hyprcoloc (D-24)
|   |-- python_stats.yml            # Python + LDSC + munging (D-24)
|   |-- plink.yml                   # PLINK 1.9 + 2.0 (D-24)
|-- src/
|   |-- snakemake/
|   |   |-- rules/                  # Refactored rules (D-05)
|   |   |   |-- sumstats.smk
|   |   |   |-- regions.smk
|   |   |   |-- ld_reference.smk
|   |   |   |-- finemap.smk
|   |   |   |-- qc.smk
|   |   |   |-- multitrait.smk
|   |   |   |-- mr.smk
|   |   |   |-- pgs.smk
|   |   |-- schemas/                # JSON Schema for config validation (D-06)
|   |   |   |-- pipeline.schema.yaml
|   |   |   |-- datasets.schema.yaml
|   |-- R/
|   |   |-- utils/
|   |   |   |-- load_config.R       # Config loader for R scripts
|   |-- python/
|   |   |-- liftover.py             # GRCh38->GRCh37 liftover (D-02)
|   |   |-- harmonize_sumstats.py   # Refactored from legacy
|   |   |-- dataset_config.py       # Refactored from legacy
|-- scripts/                        # Refactored analysis scripts
|-- tests/
|   |-- toy_3locus/
|   |   |-- Snakefile.test          # Smoke test Snakefile (D-15)
|   |   |-- config_test.yaml        # Override config (D-15)
|   |   |-- data/                   # Subsetted toy sumstats
|   |   |-- expected/               # Expected PP.H4 values for validation (D-16)
|-- data/                           # Symlinks to /rs1 (D-11, gitignored)
|   |-- raw/
|   |-- processed/
|   |-- external/
|   |-- manifest.yaml               # Data catalog (D-12)
|-- results/                        # Pipeline outputs (gitignored)
|-- src/legacy/                     # Read-only legacy reference (D-04)
```

### Pattern 1: Hierarchical Path Configuration (D-08, D-09)

**What:** All filesystem paths are defined in a single `config/pipeline.yaml` with hierarchical keys. Scripts never hardcode absolute paths.

**When to use:** Every script and rule that references a filesystem path.

**Example:**
```yaml
# config/pipeline.yaml
# Source: Derived from legacy config/config.yaml + path audit
project_root: "."  # Resolved at runtime by Snakemake

paths:
  data_root: "data"
  raw_sumstats: "data/raw/sumstats"
  harmonized_sumstats: "data/processed/sumstats_harmonized"
  regions_curated: "config/regions_curated.csv"
  regions_tiled: "config/regions_tiled.csv"
  regions_bed: "data/processed/regions/regions.bed"
  ld_1kg_root: "data/raw/1kg"
  ld_reference: "data/processed/ld_reference"
  results_root: "results"
  finemap_output: "results/fine_mapping"
  cache_downloads: "cache/downloads"
  liftover_chains: "data/external/liftover"

# Legacy path mapping (for migration reference, remove after Phase 0):
# /share/clintonlab/ckclinto/admix_map  ->  {project_root}
# /rs1/researchers/c/ckclinto/...       ->  data/ symlinks
# /gpfs_common/share01/clintonlab/...   ->  {project_root}
```

**In Snakemake rules (Python):**
```python
# Access via config dict -- no absolute paths
HARMONIZED_DIR = config["paths"]["harmonized_sumstats"]
RAW_DIR = config["paths"]["raw_sumstats"]
```

**In R scripts via config loader:**
```r
# src/R/utils/load_config.R
load_pipeline_config <- function(config_path = "config/pipeline.yaml") {
  cfg <- yaml::read_yaml(config_path)
  cfg
}

# Usage in analysis scripts:
cfg <- load_pipeline_config()
sumstats_dir <- cfg$paths$harmonized_sumstats
```

### Pattern 2: Per-Rule Conda Environment Isolation (D-25)

**What:** Each Snakemake rule declares a `conda:` directive pointing to the appropriate env YAML under `envs/`.

**When to use:** Every rule in the pipeline.

**Example:**
```python
# In src/snakemake/rules/finemap.smk
rule run_finemap:
    input: ...
    output: ...
    conda:
        "../../../envs/r_coloc.yml"   # Relative to Snakefile location
    shell:
        "Rscript scripts/run_susie_rss.R ..."
```

[VERIFIED: Legacy already uses this pattern -- `finemap.smk` uses `../../envs/r_stats_env.yml`, `qc.smk` uses `../../envs/snakemake_env.yml`]

### Pattern 3: Config Schema Validation (D-06)

**What:** JSON Schema (YAML format) validates pipeline config before any rule fires.

**When to use:** Top of Snakefile, immediately after `configfile:` directive.

**Example:**
```python
# In Snakefile
from snakemake.utils import validate

configfile: "config/pipeline.yaml"
validate(config, "src/snakemake/schemas/pipeline.schema.yaml")
```

```yaml
# src/snakemake/schemas/pipeline.schema.yaml
# Source: Snakemake docs -- https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html
$schema: "http://json-schema.org/draft-07/schema#"
type: object
required:
  - traits
  - ancestries
  - genome_build
  - paths
properties:
  traits:
    type: array
    items:
      type: string
      enum: [bmi, t2d, hypertension, asthma, stroke]
    minItems: 1
  ancestries:
    type: array
    items:
      type: string
      enum: [EUR, AFR, EAS, HIS]
    minItems: 1
  genome_build:
    type: string
    enum: [GRCh37, GRCh38]
  paths:
    type: object
    required:
      - raw_sumstats
      - harmonized_sumstats
      - regions_curated
      - ld_1kg_root
      - ld_reference
    properties:
      raw_sumstats:
        type: string
      harmonized_sumstats:
        type: string
      regions_curated:
        type: string
```
[CITED: https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html]

### Pattern 4: LSF Cluster Profile (D-07)

**What:** A YAML cluster config maps Snakemake rules to LSF queue/resource specifications.

**When to use:** Running the pipeline on the NCSU HPC cluster via `--cluster` (Snakemake 7.x).

**Example:**
```yaml
# config/cluster_lsf.yaml
# Source: Seeded from src/legacy/region_analysis/config/cluster_lsf.yaml
__default__:
  queue: "short"
  time: "04:00"
  mem_mb: 8000
  threads: 4

download_sumstats:
  time: "02:00"
  mem_mb: 4000
  threads: 1

harmonize_sumstats:
  time: "04:00"
  mem_mb: 8000
  threads: 2

prepare_ld_plink:
  time: "24:00"
  mem_mb: 32000
  threads: 4

run_finemap:
  time: "08:00"
  mem_mb: 16000
  threads: 1
```

**Invocation (Snakemake 7.x):**
```bash
snakemake --cluster "bsub -q {cluster.queue} -W {cluster.time} -n {threads} -R 'rusage[mem={cluster.mem_mb}]'" \
  --cluster-config config/cluster_lsf.yaml \
  --use-conda \
  --jobs 50 \
  --cores 200
```
[VERIFIED: `bsub` at `/usr/local/lsf/10.1/linux3.10-glibc2.17-x86_64/bin/bsub`; `short` queue has 2560 slots]

### Pattern 5: Smoke Test Override Config

**What:** The toy 3-locus test uses a minimal config override that points to pre-subsetted toy data.

**When to use:** CI smoke test (D-14 through D-17).

**Example:**
```yaml
# tests/toy_3locus/config_test.yaml
# Override paths for toy data
traits:
  - bmi
  - t2d
  - hypertension

ancestries:
  - EUR

genome_build: GRCh37

paths:
  raw_sumstats: "tests/toy_3locus/data/raw"
  harmonized_sumstats: "tests/toy_3locus/data/harmonized"
  regions_curated: "tests/toy_3locus/data/regions_toy.csv"
  ld_1kg_root: "tests/toy_3locus/data/1kg"
  ld_reference: "tests/toy_3locus/data/ld_ref"
  results_root: "tests/toy_3locus/results"

# Limit to toy regions only
finemap:
  methods: [susie]
  output_dir: "tests/toy_3locus/results/fine_mapping"
```

### Anti-Patterns to Avoid

- **Absolute paths in scripts:** Every occurrence of `/share/clintonlab/`, `/rs1/researchers/`, `/gpfs_common/` in a script is a portability violation. Use `config["paths"]` or the R config loader. [VERIFIED: 117 occurrences found in 49 legacy scripts]
- **Unpinned conda envs:** The legacy `envs/*.yml` files specify packages without version pins (e.g., `- plink` not `- plink=1.90b7.2`). This is non-reproducible. [VERIFIED: legacy plink_env.yml has `- plink` with no version]
- **Monolithic Snakemake env:** The legacy `snakemake_env.yml` bundles Python, Snakemake, PLINK, bcftools, htslib, and data science libraries in one env. This causes solver conflicts. Split into purpose-specific envs per D-24.
- **Snakemake 8.x syntax in a 7.x env:** The legacy env yml specifies `snakemake==8.*` but the actual installed version is 7.32.4. Do not mix migration syntax (`--software-deployment-method`, executor plugins) with 7.x.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GWAS column harmonization | Custom column mapper from scratch | Extend legacy `datasets.yaml` column map pattern + `harmonize_sumstats.py` | Legacy already handles 10+ GWAS formats with per-dataset column maps. Adding new datasets means adding YAML entries, not new code. [VERIFIED: datasets.yaml has column_map dicts for 8 datasets] |
| Genome build liftover | Custom coordinate conversion | UCSC liftOver binary + chain files (`hg38ToHg19.over.chain.gz`) | Standard tool, handles edge cases (split/merge/strand). One rule, not a library. [CITED: D-02] |
| JSON Schema validation | Custom config checker | `snakemake.utils.validate()` with JSON Schema Draft-07 YAML | Built into Snakemake. Supports defaults. [CITED: Snakemake docs] |
| Conda env pinning | Manual version tracking | `conda list --export` or `conda-lock` | Captures exact `package=version=build` triples including transitive deps. [CITED: https://pythonspeed.com/articles/conda-dependency-management/] |
| LSF job submission | Custom bsub wrapper scripts | Snakemake `--cluster` with `--cluster-config` (7.x) | Snakemake handles job tracking, retry, dependency DAG. Legacy already uses this pattern. [VERIFIED: legacy cluster_lsf.yaml exists] |
| Tabix/bgzip indexing | Custom index code | htslib `tabix` and `bgzip` via shell | Standard bioinformatics indexing. Already used in legacy `harmonize_sumstats` rule. [VERIFIED: sumstats.smk uses `bgzip` and `tabix`] |

**Key insight:** The legacy codebase has already solved most infrastructure problems. Phase 0 is about parameterizing, pinning, and modularizing -- not building new tools.

## Common Pitfalls

### Pitfall 1: Snakemake 7 vs 8 Version Mismatch
**What goes wrong:** Mixing Snakemake 8.x CLI syntax (`--software-deployment-method`, `--executor`) with a 7.32.x installation causes cryptic argument errors.
**Why it happens:** The legacy `snakemake_env.yml` specifies `snakemake==8.*` but the installed env has 7.32.4.
**How to avoid:** Pin to `snakemake=7.32.4` in the orchestrator env. Use `--use-conda` (7.x) not `--software-deployment-method conda` (8.x). Use `--cluster` (7.x) not `--executor lsf` (8.x). Document the migration path for later.
**Warning signs:** `snakemake: error: unrecognized arguments` at invocation time.
[VERIFIED: installed version is 7.32.4; CITED: https://snakemake.readthedocs.io/en/v8.19.2/getting_started/migration.html]

### Pitfall 2: Conda Relative Path Resolution in Snakemake Rules
**What goes wrong:** `conda:` directives in Snakemake rules resolve paths relative to the Snakefile that _includes_ the rule, not relative to the project root or the rule file itself.
**Why it happens:** Snakemake resolves `conda:` paths relative to the directory containing the Snakefile that includes the rule file via `include:`. When the top-level `Snakefile` at project root includes `src/snakemake/rules/finemap.smk`, the conda path in finemap.smk is resolved relative to project root.
**How to avoid:** Test the conda path resolution with `snakemake --list-conda-envs` before running. Use paths relative to the including Snakefile's location, or use absolute paths via `workflow.source_path()`.
**Warning signs:** `CreateCondaEnvironmentException: Failed to create conda environment` with path-not-found errors.
[ASSUMED -- based on common Snakemake community reports]

### Pitfall 3: GPFS Locking with Conda Environments
**What goes wrong:** Conda environment creation on GPFS shared filesystems can fail or produce corrupted environments due to GPFS file locking semantics.
**Why it happens:** Conda uses file-based locking during env creation; GPFS handles locks differently from local filesystems.
**How to avoid:** Create conda environments on local scratch or `/rs1` first, then reference via absolute paths. Set `CONDA_PKGS_DIRS` to a local directory. Pre-create all envs before running Snakemake with `--use-conda --conda-create-envs-only`.
**Warning signs:** Stalled `conda create` commands, corrupted env directories, "Permission denied" during package extraction.
[VERIFIED: PROJECT.md notes "GPFS filesystem" as a constraint; GSD config uses `git.isolation: branch` to avoid GPFS worktree issues]

### Pitfall 4: Path Parameterization Misses Runtime References
**What goes wrong:** Grep-based path replacement catches static strings in source files but misses paths constructed at runtime (string concatenation, f-strings with variables).
**Why it happens:** Scripts may build paths like `base_dir + "/data/" + trait` where `base_dir` is hardcoded elsewhere, or read paths from the 7,150-row genome-wide manifest TSV.
**How to avoid:** After the grep-based pass (D-10), run the smoke test (D-17) as a functional validation -- if any path resolution fails, the Snakemake run will error. Also audit the genome-wide manifest TSV (`src/legacy/genome_wide/config/genomewide_coloc_manifest.tsv` -- 7,150 rows of hardcoded paths) separately from the script audit.
**Warning signs:** Smoke test passes grep but fails at runtime with `FileNotFoundError`.
[VERIFIED: grep found 7,150 occurrences in the manifest TSV alone]

### Pitfall 5: Conda Environment Solve Failures with R + Bioconda
**What goes wrong:** Pinning R packages from both conda-forge and Bioconda channels causes solver conflicts, especially for packages like `r-coloc` and `r-susieR` that may not be on conda-forge.
**Why it happens:** `coloc` and `susieR` are CRAN/R-universe packages, not always available as conda packages. The legacy env installed them but may have used `install.packages()` inside the env rather than conda.
**How to avoid:** Check if `r-coloc` and `r-susieR` are available on conda-forge/bioconda first. If not, use a two-stage approach: install the conda-available R packages, then use `Rscript -e 'install.packages("coloc")'` or add them via the `pip:` section equivalent for R (post-deploy script). Alternatively, use `r-remotes` to install from CRAN inside the env definition.
**Warning signs:** `PackagesNotFoundError` for `r-coloc` or `r-susieR`.
[VERIFIED: legacy r_stats_env.yml lists `r-susieR` and `r-coloc` -- need to verify they're available as conda packages]

### Pitfall 6: Smoke Test Timing Exceeds 15 Minutes
**What goes wrong:** The 3-locus subset still takes too long because LD matrix computation from 1000G VCFs dominates runtime.
**Why it happens:** Even for 3 loci, extracting genotypes from 1000G VCFs, filtering to the region, and computing pairwise LD can take 5-10 minutes per region per ancestry.
**How to avoid:** Pre-compute the LD matrices and toy sumstats and include them as static test fixtures in `tests/toy_3locus/data/`. The smoke test should only run harmonization + fine-mapping + coloc, not the full LD build pipeline.
**Warning signs:** CI test consistently times out or takes >10 minutes just on LD steps.
[ASSUMED -- based on typical 1000G LD computation times for 500kb regions]

## Code Examples

### R Config Loader (Claude's Discretion)
```r
# src/R/utils/load_config.R
# Loads pipeline.yaml and provides path resolution for R scripts
# Called from Snakemake rules that invoke R scripts

load_pipeline_config <- function(config_path = NULL) {
  if (is.null(config_path)) {
    # When called from Snakemake, config is passed via --config-path arg
    args <- commandArgs(trailingOnly = TRUE)
    idx <- which(args == "--config-path")
    if (length(idx) > 0 && idx < length(args)) {
      config_path <- args[idx + 1]
    } else {
      config_path <- "config/pipeline.yaml"
    }
  }

  if (!requireNamespace("yaml", quietly = TRUE)) {
    stop("Package 'yaml' required. Install with: install.packages('yaml')")
  }

  cfg <- yaml::read_yaml(config_path)
  cfg
}

# Helper: resolve a path key from the config
resolve_path <- function(cfg, ...) {
  keys <- list(...)
  val <- cfg
  for (k in keys) {
    val <- val[[k]]
  }
  val
}
```

### Toy Locus Subsetting Script
```python
# scripts/subset_toy_loci.py
# Creates the 3-locus toy dataset for CI smoke testing
# Run once during Phase 0 setup; output committed to tests/toy_3locus/data/

import pandas as pd
import subprocess
import os

TOY_LOCI = {
    "FTO_16q12": {"chr": "16", "start": 53800000, "end": 54400000},
    "TCF7L2_10q25": {"chr": "10", "start": 114550000, "end": 115150000},
    "SH2B3_12q24": {"chr": "12", "start": 111400000, "end": 112000000},
}

def subset_sumstats(input_bgz, output_tsv, chrom, start, end):
    """Extract rows within a genomic region from a bgzipped, tabix-indexed sumstats file."""
    cmd = f"tabix {input_bgz} {chrom}:{start}-{end}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # Write header + subset
    header_cmd = f"zcat {input_bgz} | head -1"
    header = subprocess.run(header_cmd, shell=True, capture_output=True, text=True)
    with open(output_tsv, "w") as f:
        f.write(header.stdout)
        f.write(result.stdout)
```

### Data Manifest YAML (D-12)
```yaml
# data/manifest.yaml
# Catalog of all data sources with provenance metadata

sources:
  yengo2018_bmi:
    description: "Yengo et al. 2018 BMI meta-analysis (EUR)"
    genome_build: GRCh37
    ancestry: EUR
    trait: bmi
    n_samples: 795640
    local_path: "data/raw/sumstats/bmi.EUR.raw.gz"
    remote_url: "https://cnsgenomics.com/data/yengo_et_al_2018_hmg/Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz"
    doi: "10.1093/hmg/ddy271"
    license: "open-access"
    download_date: null  # Populated on download
    md5: null            # Populated on download

  diamante2022_t2d:
    description: "DIAMANTE 2022 T2D multi-ancestry"
    genome_build: GRCh37
    ancestry: [EUR, TRANS, AFR]
    trait: t2d
    local_path: "data/raw/sumstats/t2d.{ancestry}.raw.gz"
    remote_url: "https://diagram-consortium.org/downloads"
    doi: "10.1038/s41588-022-01058-3"
    license: "open-access"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `--cluster "bsub ..."` (Snakemake 7.x) | `--executor lsf` with `snakemake-executor-plugin-lsf` (8.x+) | Snakemake 8.0 (Jan 2024) | Phase 0 stays on 7.x; migration deferred |
| `--use-conda` | `--software-deployment-method conda` | Snakemake 8.0 | Phase 0 uses `--use-conda` (7.x syntax) |
| `coloc.abf` (single causal variant) | `coloc.susie` (multi-causal) | coloc 5.x (2021) | Phase 1 upgrades; Phase 0 just ensures coloc 5.2.3 is pinned |
| Loose conda YAML (`- package`) | Lockfile pinning (`package=version=build` + lockfile) | conda-lock 1.0 (2022) | Phase 0 implements pinned envs |
| Manual GWAS column mapping | GWAS-SSF standard columns | GWAS Catalog 2023 | Legacy uses custom column maps; aligning to GWAS-SSF naming is recommended but not blocking |
| `subworkflow:` directive | `module:` directive | Snakemake 7.8+ | Already using `include:` which is fine for this project scale |

**Deprecated/outdated:**
- `coloc.abf`: Single-causal-variant assumption is the #1 methodological weakness identified in Revision_Plan.md. Phase 1 replaces with `coloc.susie`. Phase 0 just ensures the library version is correct.
- `snakemake.utils.validate` with JSON Schema 2020-12: Known compatibility issue in Snakemake 8.28+. Use Draft-07 format. [CITED: https://github.com/snakemake/snakemake/issues/3299]

## Snakemake Version Decision: Stay on 7.32.x

**Recommendation:** Stay on Snakemake 7.32.4 for Phase 0.

**Rationale:**
1. The existing `snakemake` conda env has 7.32.4 installed and tested. [VERIFIED]
2. The legacy `run_snakemake.sh` uses 7.x invocation patterns (`--cluster`, `--use-conda`). [VERIFIED]
3. Snakemake 8.x removes `--cluster` in favor of executor plugins (`snakemake-executor-plugin-lsf`). This requires installing a pip package and changing all invocation patterns. [CITED: migration docs]
4. Snakemake 8.x deprecates `--use-conda` in favor of `--software-deployment-method conda`. [CITED: migration docs]
5. The `snakemake-executor-plugin-lsf` (v0.2.6) is available on PyPI and bioconda, but adds untested complexity. [CITED: https://pypi.org/project/snakemake-executor-plugin-lsf/]
6. Phase 0's goal is infrastructure stabilization, not version migration. The 7.x -> 8.x migration can be a Phase 1 pre-task if needed.
7. Snakemake 7.32.4 is the final 7.x release and receives no new features but is stable.

**Migration path (for future):**
- `--use-conda` -> `--software-deployment-method conda`
- `--cluster "bsub ..."` -> `--executor lsf` (with `pip install snakemake-executor-plugin-lsf`)
- `--cluster-config` -> `default-resources` in profile
- `subworkflow:` -> `module:` (not used in this project)
- `dynamic()` -> `checkpoint` (not used in this project)

[CITED: https://snakemake.readthedocs.io/en/v8.19.2/getting_started/migration.html]

## Conda Environment Pinning Strategy (D-23)

**Recommended approach: Two-file strategy with lockfiles.**

For each env, maintain two files:
1. `envs/{name}.yml` -- Human-readable, loose version constraints (e.g., `r-base>=4.4`). This is the "specification" file that declares intent.
2. `envs/{name}.lock` -- Machine-generated, fully pinned (`package=version=build`). This is the "lockfile" that guarantees reproducibility.

**Workflow:**
```bash
# 1. Create env from loose spec
conda env create -f envs/r_coloc.yml -n r_coloc_tmp

# 2. Export fully pinned lockfile
conda list -n r_coloc_tmp --export > envs/r_coloc.lock

# 3. Recreate from lockfile (for reproducibility)
conda create -n r_coloc --file envs/r_coloc.lock
```

**Alternative: conda-lock (recommended for cross-platform):**
```bash
pip install conda-lock
conda-lock -f envs/r_coloc.yml -p linux-64 --lockfile envs/r_coloc.lock.yml
conda-lock install envs/r_coloc.lock.yml -n r_coloc
```

**Snakemake integration:** Snakemake's `--use-conda` uses the `envs/*.yml` files directly. For CI reproducibility, pre-create envs from lockfiles before running Snakemake, or use `--conda-create-envs-only` to build envs first.

[CITED: https://pythonspeed.com/articles/conda-dependency-management/]
[CITED: https://conda.github.io/conda-lock/]

## Toy Locus Selection (Claude's Discretion)

**Recommended 3 loci for CI smoke test:**

| Locus | Region | Chr | Why |
|-------|--------|-----|-----|
| **FTO/IRX3** | FTO_16q12 | 16 | Strongest BMI signal globally. PP.H4 ~1.0 in legacy EUR. Well-characterized multi-signal region. Tests complex-region handling. |
| **TCF7L2** | (add to regions_curated) | 10 | Strongest T2D signal. Known PP.H4 > 0.95 in EUR. Multiple trait colocs (T2D + BMI). |
| **SH2B3/ATXN2** | SH2B3_12q24 | 12 | Multi-trait pleiotropy hub (HTN + stroke + CAD). Tests cross-trait behavior. Already in regions_curated.csv. |

**Rationale:**
- FTO and SH2B3 are already in `regions_curated.csv` [VERIFIED]
- TCF7L2 is referenced in Revision_Plan.md as having PP.H4 = 1.000 in PDF Table 1 [VERIFIED: Revision_Plan.md line 39]
- All three have strong signals in EUR (the primary ancestry for Phase 0 testing)
- Together they cover 3 different traits (BMI, T2D, HTN) which tests the trait-ancestry expansion logic
- Each has known PP.H4 > 0.8 from legacy coloc.abf results, providing ground truth for D-16

**Implementation note:** TCF7L2 needs to be added to `regions_curated.csv` (it appears in the manuscript tables but not in the 8-region curated CSV). Check legacy results for the exact region coordinates and PP.H4 values.

## OSF Pre-Registration Format (D-26)

**Recommended template:** Use the standard "OSF Preregistration" template (not discipline-specific). No computational genomics-specific template exists on OSF.

**Key sections to complete:**
1. **Study information:** Title, authors, hypotheses (5 traits x cross-ancestry x coloc.susie)
2. **Design plan:** Study type (observational, secondary data analysis), blinding (N/A), study design (Snakemake pipeline with pre-specified parameters)
3. **Sampling plan:** Data sources (the 8+ GWAS listed in data_access.md), sample sizes per ancestry
4. **Variables:** Outcome = PP.H4 from coloc.susie; predictors = trait pairs x ancestry x locus
5. **Analysis plan:** PP.H4 threshold sweep {0.5, 0.7, 0.8, 0.9}; tier assignment rules; negative controls
6. **Other:** Replication cohorts (FinnGen, BBJ, MVP, AoU, GBMI); equity framing plan

**Format:** OSF web form (not a paper document). Takes ~2 hours. Results in a time-stamped, DOI-minted registration.

[CITED: https://help.osf.io/article/158-create-a-preregistration]
[CITED: https://www.cos.io/blog/choosing-preregistration-template-guide-for-researchers]

## GWAS Sumstats Harmonization Standard

**Current state:** The legacy uses a custom column mapping system in `datasets.yaml` with per-dataset `column_map` dicts. This is functional and extensible.

**GWAS-SSF standard columns (for reference):**
| Standard Column | Legacy Equivalent | Notes |
|-----------------|-------------------|-------|
| `chromosome` | `CHR` | Legacy uses CHR consistently |
| `base_pair_location` | `POS` | Legacy uses POS |
| `effect_allele` | `ALT` | Legacy maps EA/effect_allele/Allele1 -> ALT |
| `other_allele` | `REF` | Legacy maps NEA/non_effect_allele/Allele2 -> REF |
| `beta` | `BETA` | Consistent |
| `standard_error` | `SE` | Consistent |
| `effect_allele_frequency` | `EAF` | Consistent |
| `p_value` | `P` | Consistent |

**Recommendation:** The legacy internal column names (CHR, POS, REF, ALT, BETA, SE, P, EAF) are close enough to GWAS-SSF that no renaming is needed for Phase 0. The column mapping system in `datasets.yaml` handles per-source variations. For new datasets (D-20), add entries to datasets.yaml following the existing pattern.

[VERIFIED: datasets.yaml column_map dicts confirmed for 8 datasets]
[CITED: https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1.full]

## New Ancestry Dataset Column Maps (D-20, D-21)

**Datasets to ingest:** AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann 2017), AFR T2D expansion (already in datasets.yaml as DIAMANTE AFR), EAS (BBJ), Hispanic (PAGE/HCHS-SOL).

**BBJ column mapping (for datasets.yaml):**
```yaml
bbj_pheweb:
  description: "BioBank Japan PheWeb (EAS)"
  base_url: "https://humandbs.dbcls.jp/files/hum0197"
  defaults:
    compression: "gzip"
    sep: "\t"
    column_map:
      CHR: ["#CHROM", "CHR"]
      POS: ["POS", "BP"]
      REF: ["REF", "A2"]
      ALT: ["ALT", "A1"]
      BETA: ["BETA", "beta"]
      SE: ["SE", "se"]
      P: ["P", "p.value", "P_BOLT_LMM"]
      EAF: ["AF", "Frq"]
      N: ["N", "N_analyzed"]
  traits:
    bmi:
      ancestries:
        EAS:
          path: "hum0197.v3.BBJ.BMI.v1.zip"
    t2d:
      ancestries:
        EAS:
          path: "hum0197.v3.BBJ.T2D.v1.zip"
    # stroke, asthma, BP similar
```
[ASSUMED -- BBJ PheWeb column names need verification from actual downloaded files. The above is an educated guess based on BBJ documentation patterns.]

## Path Parameterization Strategy (REQ-12)

**Scope (verified):**
- 117 hardcoded occurrences across 49 `.R`, `.py`, `.sh`, `.smk`, `.yaml` files (excluding the 7,150-row manifest TSV) [VERIFIED: grep audit]
- The 7,150 occurrences in `genomewide_coloc_manifest.tsv` are a data file, not code -- handle separately (regenerate from config or treat as legacy artifact)
- The patterns to replace: `/share/clintonlab/ckclinto/admix_map`, `/share/clintonlab/ckclinto/admixmap` (typo variant), `/rs1/researchers/c/ckclinto/...`, `/gpfs_common/share01/clintonlab/ckclinto/...`

**Replacement hierarchy (D-09):**
| Old Path Pattern | New Config Key | Resolves To |
|------------------|---------------|-------------|
| `/share/clintonlab/ckclinto/admix_map` | `{project_root}` | `.` (Snakemake working dir) |
| `/share/clintonlab/ckclinto/admixmap` | `{project_root}` | `.` (typo variant of above) |
| `/rs1/researchers/c/ckclinto/coloc_analysis/...` | `config["paths"]["data_root"]` | `data/` (symlinked) |
| `/rs1/researchers/c/ckclinto/conda_envs/...` | Conda `conda:` directive | Per-rule env isolation |
| `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis` | `{project_root}` | `.` |
| `/rs1/researchers/c/ckclinto/miniconda3/...` | System conda | N/A -- removed |

**Important:** The D-10 acceptance test targets `src/R src/python src/snakemake config` directories -- NOT `src/legacy/`. The legacy directory is read-only reference. Hardcoded paths in `src/legacy/` are expected and documented, not bugs.

**Strategy:**
1. Copy scripts from `src/legacy/region_analysis/scripts/` to `scripts/` (or `src/python/`, `src/R/`)
2. Parameterize the copies (never edit `src/legacy/`)
3. Update refactored rule files in `src/snakemake/rules/` to call the parameterized copies
4. Run D-10 acceptance grep on the target directories
5. Run D-17 smoke test as functional validation

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | conda relative path resolution for `conda:` directives is relative to the including Snakefile, not the rule file | Common Pitfalls #2 | Rules would fail to find env files; fixable by testing with `--list-conda-envs` |
| A2 | Pre-computing LD matrices as static fixtures for the smoke test keeps it under 15 min | Common Pitfalls #6 | Smoke test could time out; would need to further subset the toy data or skip LD build |
| A3 | `r-coloc` and `r-susieR` are available as conda packages (conda-forge or bioconda) | Common Pitfalls #5 | Would need to install via `install.packages()` post-env-create, complicating the env yml |
| A4 | BBJ PheWeb column names follow the pattern shown in the datasets.yaml example | New Ancestry Dataset section | Column maps would need correction after downloading actual files |
| A5 | TCF7L2 region coordinates are approximately chr10:114550000-115150000 | Toy Locus Selection | Would need to check legacy results for exact boundaries |

## Open Questions

1. **TCF7L2 region coordinates and legacy PP.H4 values**
   - What we know: TCF7L2 is referenced in the manuscript PDF with PP.H4 = 1.000, and the lead SNP rs7903146 is at chr10:114758349 (GRCh37)
   - What's unclear: Exact region boundaries used in legacy analysis, and whether it's in `regions_tiled.csv`
   - Recommendation: Grep legacy results for TCF7L2 entries before selecting final toy loci

2. **R package availability on conda-forge/bioconda**
   - What we know: Legacy env has `r-coloc` and `r-susieR` listed in the YAML and they're installed
   - What's unclear: Whether these are conda-forge packages or were installed via `install.packages()` inside the env
   - Recommendation: Run `conda search r-coloc -c conda-forge -c bioconda` to verify. If unavailable, use a post-deploy script.

3. **Genome-wide manifest TSV handling**
   - What we know: `genomewide_coloc_manifest.tsv` has 7,150 rows with hardcoded paths
   - What's unclear: Whether this file is regenerated by the pipeline or is a static input
   - Recommendation: Check if `build_run_manifest.py` or similar script generates it. If so, parameterize the generator. If static, regenerate from config during Phase 0.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| conda | Env management | Yes | 26.1.1 | -- |
| Snakemake | Workflow engine | Yes (in env) | 7.32.4 | -- |
| R | Statistical analysis | Yes (in env) | 4.4.2 | -- |
| coloc (R) | Colocalization | Yes (in env) | 5.2.3 | -- |
| susieR (R) | Fine-mapping | Yes (in env) | 0.14.2 | -- |
| Python | Scripting | Yes (base) | 3.9.25 | 3.11 in new env |
| bsub (LSF) | HPC job submission | Yes | LSF 10.1 | -- |
| short queue | Default job queue | Yes | 2560 slots | -- |
| plink | Genotype processing | No (not in PATH) | -- | Install in plink env |
| bcftools | VCF processing | No (not in PATH) | -- | Install in plink env |
| tabix/bgzip | Index sumstats | Likely (in conda envs) | -- | Install in python_stats env |
| conda-lock | Lockfile generation | No | -- | Use `conda list --export` |
| node | GSD tooling | No (not in PATH) | -- | Non-blocking for pipeline |

**Missing dependencies with no fallback:**
- None that block pipeline execution. PLINK, bcftools, tabix are available in conda envs but not base PATH -- this is expected and handled by per-rule conda envs.

**Missing dependencies with fallback:**
- `conda-lock`: Not installed. Fallback is `conda list --export` which produces platform-specific lockfiles (less portable but sufficient for single-cluster use).
- `node`: Not in PATH. Only needed for GSD tooling, not pipeline execution.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Snakemake dry-run + smoke test (no external test framework) |
| Config file | `tests/toy_3locus/config_test.yaml` (Wave 0) |
| Quick run command | `snakemake -n --snakefile tests/toy_3locus/Snakefile.test --configfile tests/toy_3locus/config_test.yaml` (dry run) |
| Full suite command | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda --configfile tests/toy_3locus/config_test.yaml` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-1 | All 7 open-access sources reachable | manual | Manual verification per checklist in data_access.md | N/A |
| REQ-9 | Smoke test completes <15 min, envs pinned | smoke | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` | Wave 0 |
| REQ-9 | PP.H4 values within +/-0.05 of legacy | smoke | `python tests/toy_3locus/validate_results.py` | Wave 0 |
| REQ-12 | Zero hardcoded paths in target dirs | unit | `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` returns 0 | Wave 0 |
| REQ-12 | Pipeline runs with only config values | smoke | Smoke test success implies path parameterization works | Wave 0 |

### Sampling Rate
- **Per task commit:** `snakemake -n --snakefile tests/toy_3locus/Snakefile.test` (dry run, <5 sec)
- **Per wave merge:** Full smoke test (<15 min)
- **Phase gate:** Full smoke test green + REQ-12 grep returns 0

### Wave 0 Gaps
- [ ] `tests/toy_3locus/Snakefile.test` -- smoke test Snakefile
- [ ] `tests/toy_3locus/config_test.yaml` -- test config override
- [ ] `tests/toy_3locus/data/` -- pre-subsetted toy sumstats + LD matrices
- [ ] `tests/toy_3locus/expected/` -- expected PP.H4 values from legacy
- [ ] `tests/toy_3locus/validate_results.py` -- result comparison script
- [ ] `envs/r_coloc.yml` -- pinned R env
- [ ] `envs/python_stats.yml` -- pinned Python env
- [ ] `envs/plink.yml` -- pinned PLINK env
- [ ] `src/snakemake/schemas/pipeline.schema.yaml` -- config schema

## Sources

### Primary (HIGH confidence)
- **Codebase inspection** -- All legacy rule files (`src/legacy/region_analysis/workflow/rules/*.smk`), Snakefile, config files, env YMLs directly read and verified
- **Environment probes** -- conda 26.1.1, Snakemake 7.32.4, R 4.4.2, coloc 5.2.3, susieR 0.14.2, LSF 10.1 all confirmed via CLI
- **LSF queue availability** -- `bqueues` confirmed `short` queue (2560 slots), `shared_memory` queue available
- **Path audit** -- grep confirmed 117 occurrences in 49 code files, 7,150 in manifest TSV

### Secondary (MEDIUM confidence)
- [Snakemake migration docs](https://snakemake.readthedocs.io/en/v8.19.2/getting_started/migration.html) -- Snakemake 7->8 breaking changes (403'd on direct fetch, content from web search summaries)
- [snakemake-executor-plugin-lsf README](https://github.com/befh/snakemake-executor-plugin-lsf) -- LSF plugin config and memory format options
- [conda-lock docs](https://conda.github.io/conda-lock/) -- Lockfile generation strategy
- [GWAS-SSF preprint](https://www.biorxiv.org/content/10.1101/2022.07.15.500230v1.full) -- Standard column naming for GWAS sumstats
- [Snakemake schema validation docs](https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html) -- `validate()` function with JSON Schema Draft-07
- [OSF preregistration guide](https://help.osf.io/article/158-create-a-preregistration) -- Registration workflow and templates

### Tertiary (LOW confidence)
- BBJ PheWeb column names (A4 in Assumptions Log) -- educated guess, needs verification from actual downloaded files
- conda-forge availability of `r-coloc` and `r-susieR` (A3) -- needs `conda search` verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all core tools verified via CLI probes, versions confirmed
- Architecture: HIGH -- legacy codebase provides proven patterns; refactor path is clear
- Pitfalls: MEDIUM -- most are based on direct observation; a few (conda path resolution, LD timing) are experience-based assumptions
- Path parameterization: HIGH -- grep audit provides exact scope; acceptance test is well-defined
- Smoke test: MEDIUM -- locus selection and timing assumptions need validation with actual data

**Research date:** 2026-04-10
**Valid until:** 2026-05-10 (stable domain -- bioinformatics tools move slowly; main risk is Snakemake version updates)
