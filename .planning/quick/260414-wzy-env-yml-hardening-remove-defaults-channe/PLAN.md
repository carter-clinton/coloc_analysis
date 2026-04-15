# Quick Task wzy: Env YAML hardening + libmamba interop workaround

**ID:** 260414-wzy
**Date:** 2026-04-15
**Goal:** Codify the env workarounds surfaced by the bmi.EUR magma_fdr scout so they survive the next fresh-host env rebuild.

## Context

SCOUT-FINDINGS.md issues #4–#7 documented operational workarounds that were applied in-session but not committed:

- **#4** mamba 2.5 + snakemake 7.32.4 interop bug: `mamba env create --prefix X` aborts from snakemake's wrapper
- **#5** Anaconda ToS interactive prompt triggered by any env touching `defaults` channel
- **#6** `python_stats.yml` uses `defaults` → triggers #5 (symlinked prefix to `smoke_dev` in-session)
- **#7** gprofiler env hash drift after `r-msigdbr` augmentation (symlinked hash to hash)

## Plan

1. **Drop `defaults` channel from 6 env yamls** where feasible (all deps available on conda-forge + bioconda):
   - python_stats.yml
   - magma.yml
   - ldsc_py3.yml
   - plink.yml
   - qtl_processing.yml
   - r_coloc.yml
   - KEEP `defaults` in `hess_py27.yml` (Python 2.7 only available there — intentional, EOL)
2. **Create `bin/setup-envs.sh`** that pre-creates all project envs, with a direct-mamba fallback when snakemake's wrapper hits the libmamba 2.5 interop bug
3. **Rewrite `envs/README.md`** to reflect the actual 11-env inventory + Setup & known pitfalls section (libmamba 2.5 bug + ToS prompt)
4. Commit

## Acceptance

- [ ] 6 yamls no longer list `defaults`; `hess_py27.yml` retains it with explicit comment
- [ ] `bin/setup-envs.sh` exists, is executable, uses smoke_dev's pinned snakemake, has mamba-direct fallback
- [ ] `envs/README.md` lists the real 11 envs + libmamba pitfalls
- [ ] No existing env on disk is affected (the edits take effect on next hash-changing rebuild)
