# envs/

One pinned conda environment per tool family. Every dependency gets an exact
or floored version. These `*.yml` files are the single source of truth for the
pipeline's runtime — anything not in an env file does not exist.

## Current environments

| File | Channels | Purpose |
|---|---|---|
| `python_stats.yml` | conda-forge, bioconda | Snakemake orchestrator + pandas/numpy/scipy + pyarrow + htslib. Phase 1+. |
| `r_coloc.yml` | conda-forge, bioconda | R + `coloc`, `susieR`, `data.table`, `metafor` (P9), `remotes` for hyprcoloc/winnerscurse. Phase 1/2/9. |
| `ld_build.yml` | conda-forge, bioconda | Python + R + bcftools + plink2 for LD panel construction. Phase 1 Waves 2/3. |
| `qtl_processing.yml` | conda-forge, bioconda | QTL download/harmonize (synapseclient, pyliftover, pysam, pybedtools). Phase 2. |
| `qc_dashboard.yml` | conda-forge, bioconda | R + Quarto/RMarkdown for fine-mapping QC dashboard. Phase 1 Wave 5. |
| `magma.yml` | conda-forge | Python helpers for MAGMA rules (binary is external). Phase 5. |
| `gprofiler.yml` | conda-forge, bioconda | r-gprofiler2 + r-msigdbr (>=10.0 since 260414-uqf). Phase 5. |
| `ldsc_py3.yml` | conda-forge | Py3-modernized LDSC fork (abdenlab/ldsc-python3). Phase 5. |
| `hess_py27.yml` | **defaults**, conda-forge, bioconda | HESS requires Python 2.7 (EOL). Phase 5. |
| `gcta.yml` | bioconda, conda-forge | GCTA 1.94.1 for COJO sensitivity. Phase 9 Plan 09-05. |
| `plink.yml` | bioconda, conda-forge | PLINK 1.9 + PLINK2 + bcftools. Used across multiple phases. |

All envs except `hess_py27.yml` resolve via `conda-forge` + `bioconda` only — no
`defaults` channel — so fresh-host creation does not hit the Anaconda ToS
interactive prompt (see Pitfalls below).

## Creating envs for a Snakemake run

Preferred path — let Snakemake manage env lifetimes keyed to yaml hashes:

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
  --use-conda \
  --conda-frontend mamba \
  --conda-create-envs-only \
  --cores 1 all_pathway
```

If you hit scout issue #4 (libmamba 2.5 interop bug), use the setup script:

```bash
bin/setup-envs.sh                 # default target: all_pathway
bin/setup-envs.sh pathway_aggregate
```

The script runs snakemake's creation path first, then falls back to direct
`mamba env create` for any staged yamls that didn't produce a working prefix.
Idempotent; safe to re-run.

## Known pitfalls

### libmamba 2.5 interop bug (scout issue #4)

**Symptom:** Running `snakemake --use-conda --conda-create-envs-only` aborts with

```
error libmamba Non-conda folder exists at prefix - aborting
```

even when the target prefix does not exist.

**Root cause:** Snakemake's conda wrapper creates an empty prefix directory
before shelling out to `mamba env create --prefix X`. mamba 2.5 detects the
empty directory as a "non-conda folder" and refuses.

**Workaround:** `bin/setup-envs.sh` handles this. It removes the empty stub
prefix and calls `mamba env create` directly, which works fine.

### Anaconda ToS interactive prompt (scout issue #5)

**Symptom:** Creating any env that references the `defaults` channel triggers

```
Confirm changes: [Y/n]
```

which neither `--quiet`, `--yes`, nor stdin redirection bypasses under
mamba 2.5. Blocks non-interactive CI.

**Workaround:** We dropped `defaults` from every env where conda-forge +
bioconda suffices (6 yamls, all updated in quick 260414-wzy). `hess_py27.yml`
still needs `defaults` because Python 2.7 is only hosted there — answer `Y`
once on first creation and it's cached.

### Hash drift after in-place env edits (scout issue #7)

**Symptom:** Edit a yaml → snakemake computes a new hash → asks to create a
new prefix → your augmented-in-place env is abandoned.

**Convention:** Never `mamba install` into an existing `.snakemake/conda/*_`
prefix. Edit the yaml and let the setup script create the new prefix. If you
must patch in-place for a one-off, delete the old prefix afterward so the next
pipeline run regenerates it cleanly.

### hyprcoloc / winnerscurse are GitHub-only

These R packages aren't on conda. `r_coloc.yml` installs `r-remotes` and the
calling scripts (`run_fiqt.R`, etc.) lazy-install from GitHub on first use.
winnerscurse is SHA-pinned to `2ed00bb` — see `r_coloc.yml` for the rationale.

## Provenance

Pinning is **REQ-9** (CI reproducibility). Env files are under version control;
lock files are optional until Phase 11 submission package.
