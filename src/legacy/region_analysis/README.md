# Summary-statistics-based multi-trait workflow (Snakemake + LSF)

This repo is a project skeleton for:

- Summary-statistics-based multi-trait analyses as the main “real-data” engine.
- Re-usable slots for:
  - Local-ancestry-based region definitions (from AA admixture hits),
  - PGS/PRS-CSx,
  - MR and multi-trait colocalization.

## Layout

See `config/config.yaml` for traits, ancestries, and paths.

Key dirs:

- `config/` : global config, datasets, curated regions (incl. APOL1), LSF cluster config.
- `envs/`   : conda envs (Snakemake core, R stats, plink/bcftools).
- `data_raw/` and `data_processed/` : raw / processed GWAS & LD data.
- `scripts/` : Python + shell helpers.
- `workflow/` : main `Snakefile` and modular `rules/`.

## Quickstart

Create env:

```bash
mamba env create -f envs/snakemake_env.yml
conda activate la_multitrait
snakemake --cores 4 --use-conda
```

Replace the env name / working directory reference above with whatever you actually use on your system.

### Configure data sources

1. `config/datasets.yaml` already lists the current sources mentioned in the project brief (GBMI asthma, Yengo 2018 BMI, DIAMANTE 2022 T2D, Evangelou 2018 BP, and MEGASTROKE stroke). Update the `md5`, `path`, or `zip_member` fields if you mirror the files elsewhere or if the upstream archives change layout. The `column_map` entries describe how raw column names map to the harmonized schema—tweak them if any dataset deviates.
2. `config/config.yaml` controls the trait list, per-trait dataset priority, the `trait_ancestries` matrix (e.g., BMI currently has EUR only, while asthma has EUR+AFR), and toggles like `enable_ld_pipeline` (set to `false` by default to avoid the heavy 1000G download/PLINK prep when running in a restricted environment).
3. To add additional loci/regions, extend `config/regions_curated.csv` and re-run `snakemake make_regions_from_loci`.

Need a smoke-test without downloading the large public files? Run:

```bash
python scripts/stage_mock_sumstats.py --config config/config.yaml --output-dir data_raw/sumstats
```

This creates tiny gzipped GWAS files for every trait/ancestry pair so the Snakemake DAG can be exercised end-to-end.

### Workflow modules

- **Summary stats** (`workflow/rules/sumstats.smk`): downloads raw files via `requests`, transparently extracts `.zip` archives, and feeds them into `scripts/harmonize_sumstats.py`, which uses `config/datasets.yaml` metadata to standardize column names. Once harmonized, `workflow/rules/qc.smk` summarizes each file (N variants, missingness, allele-frequency range) at `results/qc/harmonized_summary.tsv`.
- **Region prep** (`workflow/rules/regions.smk`): converts curated loci into BED files.
- **Multitrait planning** (`workflow/rules/multitrait.smk`): `scripts/create_multitrait_manifest.py` records which harmonized file pairs feed each region-based analysis.
- **LD + PGS scaffolding** (`workflow/rules/ld_reference.smk` / `workflow/rules/pgs.smk`): `download_1kg_vcf` pulls per-chromosome 1000G Phase 3 vcfs + tbi files, `build_1kg_sample_lists.py` generates ancestry-specific KEEP files from the panel, `prepare_ld_plink` builds filtered PLINK references, and `scripts/create_pgs_manifest.py` enumerates PRS-CSx/LDpred2 jobs across ancestries. A placeholder rule (`run_pgs_placeholder`) reports how many jobs would run.
- **MR design** (`workflow/rules/mr.smk`): `scripts/create_mr_design.py` cross-references harmonized files with the hypotheses listed under the `mr:` block in `config/config.yaml`, and `run_mr_placeholder` prints the ready vs missing hypotheses count.
- **Multitrait execution placeholder** (`run_multitrait_placeholder`) consumes the manifest and echoes the number of planned region-trait analyses—swap this out with SuSiE/FINEMAP/coloc runners once the LD matrices are ready.
- **Fine-mapping** (`workflow/rules/finemap.smk`): When `finemap.methods` is non-empty, `scripts/create_finemap_tasks.py` enumerates every trait × ancestry × region × method combination, and `scripts/run_finemap_placeholder.py` records JSON placeholders under `results/fine_mapping/<method>/...`. Replace that script with your actual SuSiE/FINEMAP/coloc harness when LD references are available. (`finemap.methods` defaults to an empty list so this module is disabled until you’re ready.)

After editing the configs above, `snakemake --cores <N> --use-conda` will pull raw summary stats, harmonize them, and emit planning manifests under `results/`.
