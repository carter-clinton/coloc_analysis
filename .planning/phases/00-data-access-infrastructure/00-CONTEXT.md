# Phase 0: Data access + infrastructure - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish all data sources, fix legacy issues, build reproducible Snakemake skeleton with CI smoke test. Two parallel sub-tracks: Track 0a (data downloads and registration, non-blocking) and Track 0b (infrastructure — parameterize paths, pin envs, build Snakemake skeleton, create CI smoke test, submit OSF pre-registration). This phase blocks Phase 1.

</domain>

<decisions>
## Implementation Decisions

### Genome build strategy
- **D-01:** Primary coordinate system is **GRCh37** (hg19). Legacy analysis, existing region definitions, and most GWAS sumstats are GRCh37. Do not migrate to GRCh38 as primary.
- **D-02:** Add a liftover utility (`src/python/liftover.py` or Snakemake rule) for sources only available in GRCh38 (e.g., newer FinnGen R13/R14 releases). Use UCSC liftOver chain files.
- **D-03:** Record genome build per dataset in `data/manifest.yaml` so downstream phases know which need liftover.

### Pipeline architecture
- **D-04:** **Refactor and modularize** the legacy Snakemake workflow — do not rewrite from scratch. The 8 legacy rules (`finemap.smk`, `ld_reference.smk`, `mr.smk`, `multitrait.smk`, `pgs.smk`, `qc.smk`, `regions.smk`, `sumstats.smk`) contain tested logic.
- **D-05:** Move refactored rules to `src/snakemake/rules/`. Each rule file is self-contained: reads from `config/pipeline.yaml`, outputs to `results/`.
- **D-06:** Add YAML schema validation per trait/ancestry pair using `src/snakemake/schemas/`. Validate input sumstats columns before any analysis rule fires.
- **D-07:** Top-level `Snakefile` at project root imports all rules. Profile for LSF cluster via `config/cluster_lsf.yaml` (seed from legacy `src/legacy/region_analysis/config/cluster_lsf.yaml`).

### Path parameterization (REQ-12)
- **D-08:** Create `config/pipeline.yaml` as the **single source of truth** for all filesystem paths. Hierarchical keys: `data_root`, `legacy_root`, `result_root`, plus per-source download paths.
- **D-09:** The 174 hardcoded absolute paths in `src/legacy/` collapse to ~5-6 root path variables. All scripts access paths through Snakemake's `config` dict (Python rules) or an R config loader function (`src/R/utils/load_config.R`).
- **D-10:** Acceptance test: `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` returns 0 matches after parameterization.

### Data layout
- **D-11:** Maintain the symlink strategy ��� data stays on `/rs1`, symlinked into `data/`. This is a PROJECT.md constraint (no 30 GB data duplication).
- **D-12:** Add `data/manifest.yaml` cataloging all data sources: source name, local path, remote URL, genome build, file format, checksum (MD5), download date.
- **D-13:** New downloads go to `data/raw/{source_name}/` following existing convention. Processed/harmonized data goes to `data/processed/{source_name}/`.

### CI smoke test (REQ-9)
- **D-14:** Toy dataset = **3 well-characterized loci** from the legacy analysis with known PP.H4 > 0.8 (ground truth from prior coloc.abf results). Subset sumstats to ±500kb around each locus.
- **D-15:** Test lives in `tests/toy_3locus/` with its own `Snakefile.test` and `config_test.yaml` (overrides data paths to toy data).
- **D-16:** Pass criteria: pipeline completes without error; PP.H4 values are within ±0.05 of legacy results for the 3 loci; all intermediate files exist.
- **D-17:** Run via `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` and must complete in under 15 minutes.

### Supplementary table fixes
- **D-18:** Fix corrupted Tables 1, 3, S4 per Revision_Plan.md §10. Audit the DIAMANTE T2D dedup issue (76/63%/26 denominator mismatch) — resolve which number is correct and document in a one-line commit message.
- **D-19:** Drop KCNJ11 asthma-HTN Tier-1 signal (n_SNPs=6 < 50 threshold) from all tables and region lists.

### New ancestry GWAS ingest
- **D-20:** Ingest new sumstats into the pipeline: AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann), AFR T2D expansion, EAS (BBJ), Hispanic (PAGE/HCHS-SOL).
- **D-21:** Add entries to `config/datasets.yaml` with column maps (following legacy convention in `src/legacy/region_analysis/config/datasets.yaml`).
- **D-22:** Update `config/pipeline.yaml` to add `EAS` and `HIS` to the `ancestries` list (currently only EUR, AFR).

### Conda environment pinning (REQ-9)
- **D-23:** Pin all conda envs under `envs/*.yml` with exact versions (`package=version=build`). Seed from legacy `src/legacy/region_analysis/envs/` but update to current versions.
- **D-24:** Core envs needed: `envs/r_coloc.yml` (R + coloc + susieR + hyprcoloc), `envs/python_stats.yml` (Python + LDSC + munging), `envs/plink.yml` (PLINK 1.9 + 2.0).
- **D-25:** Each Snakemake rule declares `conda:` directive pointing to the appropriate env file.

### OSF pre-registration
- **D-26:** Submit pre-registration on OSF (Open Science Framework) documenting: the 5 traits, the analytical phases, the PP.H4 threshold sweep values, the replication cohorts, and the equity framing plan. This anchors the analytical plan before any results are generated.

### Claude's Discretion
- Exact choice of 3 toy loci for CI smoke test (should be well-characterized with clear signals)
- Column mapping specifics for new ancestry GWAS datasets
- R config loader implementation details (`src/R/utils/load_config.R`)
- Snakemake profile specifics for LSF (memory, queue, walltime defaults)
- Whether to use Docker/Singularity containers in addition to conda (nice-to-have, not required for Phase 0)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project strategy
- `Revision_Plan.md` — Full 559-line revision strategy. §10 covers supplementary table fixes. §7 covers reproducibility requirements.
- `GSD_BRIEFING.md` — Independent evaluation + gap analysis. §5.2 lists all 11 gaps. §5.3 covers tier gating.
- `.planning/PROJECT.md` — Project context, constraints (solo author, public data only, no web stack, GPFS filesystem)
- `.planning/DECISIONS.md` — 8+ load-bearing decisions. "Data access verified 2026-04-09" entry is critical for understanding Track 0a scope.

### Requirements
- `.planning/REQUIREMENTS.md` — REQ-1 (data access), REQ-9 (CI smoke test), REQ-12 (path parameterization) are Phase 0 deliverables.
- `.planning/data_access.md` — Detailed tracker with verified URLs, access models, and contacts for all 8+ data sources.

### Legacy codebase (to refactor from)
- `src/legacy/region_analysis/config/config.yaml` — Legacy pipeline config (traits, ancestries, paths, 1000G setup)
- `src/legacy/region_analysis/config/datasets.yaml` — Legacy download sources with column maps
- `src/legacy/region_analysis/config/cluster_lsf.yaml` — LSF cluster profile
- `src/legacy/region_analysis/workflow/rules/` — 8 legacy Snakemake rules (finemap, ld_reference, mr, multitrait, pgs, qc, regions, sumstats)
- `src/legacy/region_analysis/envs/` — Legacy conda env files (plink_env.yml, r_stats_env.yml, snakemake_env.yml)
- `src/legacy/region_analysis/scripts/` — Legacy analysis scripts (Python + R)

### New pipeline skeleton (to build into)
- `src/snakemake/rules/` — Empty rules directory for new modular pipeline
- `src/snakemake/schemas/` — Empty schemas directory for input validation

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Legacy Snakemake rules** (8 rules): Tested logic for sumstats processing, LD reference building, region extraction, QC, fine-mapping. Core logic should be preserved during refactor.
- **Legacy config/datasets.yaml**: Column mapping system for harmonizing diverse GWAS sumstats formats. Extensible for new datasets.
- **Legacy config/config.yaml**: Trait/ancestry/path configuration structure. Good template for new `config/pipeline.yaml`.
- **Legacy envs/**: 3 conda env YAML files. Need version pinning but provide the dependency list.

### Established Patterns
- **Snakemake rules pattern**: Each rule in its own `.smk` file, included from a central Snakefile.
- **Config-driven**: Traits and ancestries are config arrays — rules expand over them. This scales to EAS/HIS.
- **GWAS column mapping**: `datasets.yaml` defines per-source column aliases. Harmonization scripts use this.
- **LSF cluster**: `cluster_lsf.yaml` maps rules to queues/resources. Proven pattern for HPC submission.

### Integration Points
- **Top-level Snakefile** at project root (to create) imports `src/snakemake/rules/*.smk`
- **config/pipeline.yaml** (to create) replaces all hardcoded paths
- **data/ symlinks** already point to `/rs1` data — new downloads follow same pattern
- **tests/toy_3locus/** (to create) uses same Snakemake rules with overridden config

</code_context>

<specifics>
## Specific Ideas

- Legacy pipeline is more mature than initially assumed (182 files, 8 modular rules) — this is a refactor-and-extend, not a clean-room build
- The DIAMANTE T2D dedup issue (76/63%/26) is a known data quality problem that must be resolved with an explicit documented decision
- deCODE summarydata portal needs manual browser verification (client-side rendering blocked automated scraping)
- All of Us Controlled Tier is already credentialed per data_access.md — only question is compute cost on GCP

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 00-data-access-infrastructure*
*Context gathered: 2026-04-09*
