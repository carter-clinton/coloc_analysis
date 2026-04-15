# Quick Task wzy — SUMMARY

**ID:** 260414-wzy
**Status:** ✅ Complete
**Date:** 2026-04-15

## Scope

Codify env workarounds from scout issues #4–#7 so they survive fresh-host rebuilds.

## Changes

### Env yaml edits — dropped `defaults` from 6 files

Channels edited (added comment referencing quick 260414-wzy + scout issue #5):

| File | Channels after |
|---|---|
| envs/python_stats.yml | conda-forge, bioconda |
| envs/magma.yml | conda-forge |
| envs/ldsc_py3.yml | conda-forge |
| envs/plink.yml | bioconda, conda-forge |
| envs/qtl_processing.yml | conda-forge, bioconda |
| envs/r_coloc.yml | conda-forge, bioconda |

Unchanged:

| File | Why |
|---|---|
| envs/hess_py27.yml | Python 2.7 only on `defaults` (EOL); existing comment already explains |
| envs/gprofiler.yml, envs/ld_build.yml, envs/gcta.yml, envs/qc_dashboard.yml | Never had `defaults` |

### New file — `bin/setup-envs.sh`

Executable shell script that pre-creates all Snakemake conda envs:

- Invokes `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --use-conda --conda-create-envs-only --cores 1 <target>` first (best effort)
- Falls through to direct `mamba env create` per staged yaml if the wrapper hits scout issue #4 (libmamba 2.5 interop bug)
- Removes empty stub prefixes that snakemake leaves behind before bailing (so mamba doesn't refuse "Non-conda folder exists at prefix")
- Idempotent; skips prefixes with valid `conda-meta/`
- Default target `all_pathway`; overrideable with single CLI arg
- Syntax-checked with `bash -n` ✓

### Doc rewrite — `envs/README.md`

Replaced stale "Planned environments" table (listed coloc_r/ldsc/prscsx/etc. that never landed) with accurate 11-env inventory + explicit pitfalls section covering:

1. libmamba 2.5 interop bug (scout issue #4) — with workaround pointer to setup-envs.sh
2. Anaconda ToS interactive prompt (scout issue #5) — with status: dropped from 6 yamls, required by hess_py27
3. Hash drift after in-place env edits (scout issue #7) — with convention: edit yaml, don't `mamba install` into staged prefix
4. hyprcoloc/winnerscurse GitHub-only — with SHA pin pointer

## Validation

- All 7 edited yamls parse cleanly via `yaml.safe_load` ✓
- `bin/setup-envs.sh` passes `bash -n` syntax check ✓
- No existing `.snakemake/conda/*_` env on disk is disturbed (edits only take effect on next hash-changing rebuild)

## Out of scope / deferred

- **Running** `bin/setup-envs.sh` to validate it end-to-end on a fresh host — deferred because the goal here was to codify workarounds, not re-rebuild envs. First real run will happen at next fresh checkout or `.snakemake/conda/` wipe.
- gprofiler.yml pins (already relaxed by 260414-uqf; no further action needed)
- python_stats symlink (scout issue #6 operational workaround) — now unnecessary since python_stats.yml no longer references `defaults`

## Coverage mapping (scout issues addressed)

| Scout issue | Action |
|---|---|
| #4 libmamba interop | Codified in `bin/setup-envs.sh` (direct-mamba fallback) + documented in envs/README.md |
| #5 Anaconda ToS prompt | `defaults` dropped from 6 yamls (only unavoidable use-case — hess_py27 — documented) |
| #6 python_stats symlink | Obsoleted (python_stats.yml no longer triggers ToS prompt) |
| #7 hash drift | Convention documented in envs/README.md: edit yaml, don't in-place install |
