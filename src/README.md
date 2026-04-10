# src/

Active source code for the manuscript revision.

| Subdir | Contents |
|---|---|
| `R/` | R scripts: `coloc`, `susieR`, `TwoSampleMR`, `MRPRESSO`, `MendelianRandomization`, figure generation |
| `python/` | Python scripts: `ldsc`, `PRS-CSx`, `selscan`, Enformer / Borzoi / Sei inference, MAGMA wrappers, harmonization utilities |
| `snakemake/` | `Snakefile`, `rules/*.smk`, `schemas/*.yaml` — the reproducible pipeline glue |
| `legacy/` | Prior analysis code recovered from `/rs1/researchers/c/ckclinto/coloc_analysis/` as of 2026-02-11. **Read-only reference.** Refactored output goes into `R/`, `python/`, or `snakemake/` — not here. |

See `.planning/DECISIONS.md` for the reuse policy (refactor in place, extend
existing Snakemake workflow).
