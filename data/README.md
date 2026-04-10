# data/

Data is **not committed**. All three subdirectories are `.gitignore`d and
populated by symlinks to `/rs1/researchers/c/ckclinto/coloc_analysis/`
(see `.planning/DECISIONS.md`).

| Subdir | Contents |
|---|---|
| `raw/` | Unmodified upstream GWAS / QTL / single-cell / LD-reference files. One symlink per upstream source. |
| `processed/` | Per-trait × ancestry harmonized sumstats (hg38, aligned effect alleles). Produced by `src/snakemake/rules/sumstats.smk`. |
| `external/` | Auxiliary reference datasets (1000G, HGDP, GTEx, UKB-PPP, deCODE, OneK1K, etc.). Mostly symlinked. |

## New-data ingest checklist

1. Add the source to `config/data_sources.yaml` (trait, ancestry, N, DOI, license, DUA status).
2. Symlink the raw file(s) into `data/raw/<source_id>/`.
3. Add a Snakemake rule under `src/snakemake/rules/sumstats.smk` that harmonizes
   it into `data/processed/<trait>/<ancestry>/sumstats.tsv.gz`.
4. Register it in the `.planning/data_access.md` tracker if it's behind a DUA.

## Storage policy

Anything larger than ~10 MB should stay on `/rs1` and be referenced via symlink,
not copied into GPFS. A 77 GB historical backup tarball
(`coloc-attempt1-backup.tar.gz`) remains at `/rs1` — see `.planning/DECISIONS.md`.
