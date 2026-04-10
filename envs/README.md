# envs/

One pinned conda environment per tool family. Every dependency gets an exact
version. These `*.yml` files are the single source of truth for the pipeline's
runtime — anything not in an env file does not exist.

## Planned environments

| File (planned) | Covers |
|---|---|
| `coloc_r.yml` | R + `coloc`, `susieR`, `TwoSampleMR`, `MendelianRandomization`, `MRPRESSO`, `hyprcoloc`, data.table |
| `ldsc.yml` | Python 2/3 split: LDSC, LDSC-SEG, stratified LDSC, HESS |
| `magma.yml` | MAGMA CLI + g:Profiler `gprofiler-official` + ref sets |
| `prscsx.yml` | PRS-CSx + PLINK2 + pandas |
| `selscan.yml` | selscan, hapne, Relate (if T3 lights up) |
| `deep_learning.yml` | Enformer / Borzoi / Sei / AlphaMissense inference (if T3 lights up) |
| `snakemake.yml` | Snakemake, DataLad, conda-lock, pytest |
| `base.yml` | bcftools, samtools, htslib, PLINK, PLINK2, tabix, bgzip |

## Build + lock

```bash
# create and activate
conda env create -f envs/coloc_r.yml
conda activate coloc_r

# regenerate a lock (for reproducibility — optional until Phase 0 pins)
conda-lock lock -f envs/coloc_r.yml --platform linux-64
```

Pinning these is **Phase 0 task 4** (`.planning/REQUIREMENTS.md` REQ-9 — CI
reproducibility).
