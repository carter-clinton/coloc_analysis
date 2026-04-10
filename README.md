# coloc_analysis

Cross-ancestry colocalization analysis of 5 cardiometabolic traits (BMI, T2D,
hypertension, stroke, asthma) across ~50 pleiotropic loci.

**Author:** Carter K. Clinton, ASHES Lab, NCSU (solo author)
**Status:** Under revision for a high-impact journal. See `Revision_Plan.md`.
**Data policy:** 100% public data; academic DUAs only. No wet-lab work.

## Where things live

| Path | What |
|---|---|
| `Revision_Plan.md` | 10-phase methodological revision strategy (north-star) |
| `GSD_BRIEFING.md` | Independent evaluation + T1/T2/T3 tiering + gap list |
| `.planning/` | GSD state: `PROJECT.md`, `REQUIREMENTS.md`, `DECISIONS.md`, `ROADMAP.md`, phase plans |
| `src/legacy/` | Prior analysis code recovered from `/rs1/researchers/c/ckclinto/coloc_analysis/` (read-only reference) |
| `src/R/`, `src/python/`, `src/snakemake/` | New/refactored code for the revision |
| `config/` | Pipeline configuration (YAML, p12 grid, PP.H4 sweep, target manifests) |
| `envs/` | Pinned conda environments (one yml per tool family) |
| `data/raw/`, `data/processed/`, `data/external/` | Symlinks to `/rs1` data (git-ignored) |
| `results/` | Regeneratable pipeline outputs (git-ignored) |
| `figures/` | Committed figure PDFs + the scripts that built them |
| `tests/` | Toy 3-locus subset for the nightly Snakemake smoke test |
| `docs/` | Methods notes, figure captions, legacy summary docs |
| `manuscript/` | Manuscript draft + supplementary + response-to-reviewers |
| `archive/pre-revision-2026/` | Pre-revision artifacts: old shadow dirs, pre-built packages (publication/locuszoom/pathway_enrichment/manuscript zips) |

## Upstream data location

The analysis data lives at `/rs1/researchers/c/ckclinto/coloc_analysis/` and is
**symlinked** into `data/` here rather than copied. A full 77 GB backup tarball
(`coloc-attempt1-backup.tar.gz`) and a 532 GB scratch `region_analysis/tmp/` also
remain at that location; see `.planning/DECISIONS.md`.

## Getting started

1. Read `Revision_Plan.md` and `GSD_BRIEFING.md` — in that order.
2. Read `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/DECISIONS.md`,
   and `.planning/ROADMAP.md`.
3. Use GSD v1 slash commands (`/gsd-progress`, `/gsd-plan-phase N`, etc.) to drive
   execution. GSD mode is **solo** with **branch** isolation (GPFS does not
   play well with worktree isolation).

## Environment

- NCSU HPC, GPFS shared filesystem
- Miniconda3 at `/rs1/researchers/c/ckclinto/miniconda3/`
- GSD tools in a dedicated conda env `gsd-tools`: `conda activate gsd-tools`
- Job scheduler: LSF (`bsub`)
