# figures/

Committed figure outputs + the scripts or notebooks that generate them.
Unlike `results/`, figures here are tracked because they're small, they're
published, and they're the manuscript's ground truth.

## Conventions

- One PDF per published figure (vector preferred).
- A `figures/scripts/` subdir holds the generation scripts (R or Python),
  kept next to their inputs via Snakemake rules in `src/snakemake/`.
- `figures/scratch/` and `figures/tmp/` are `.gitignore`d for WIP outputs.
- Name files by figure number + short descriptor:
  `fig01_locus_manhattan.pdf`, `fig02_coloc_heatmap.pdf`, etc.

## Legacy figures

Old figures from the pre-revision submission are under
`archive/pre-revision-2026/prior-packages/publication_package_2026-01-27/`
and should not be reused as-is — most will be regenerated in Phase 11.
