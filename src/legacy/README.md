# src/legacy/

Prior analysis code recovered from `/rs1/researchers/c/ckclinto/coloc_analysis/`
as of **2026-02-11**. This tree is **read-only reference** — refactored output
belongs in `src/R/`, `src/python/`, or `src/snakemake/`.

## What's here

| Subdir | Source | Contents |
|---|---|---|
| `region_analysis/` | `/rs1/.../coloc_analysis/region_analysis/` | 79 script files, full Snakemake workflow (`workflow/Snakefile` + 8 rules: `finemap.smk`, `mr.smk`, `pgs.smk`, `qc.smk`, `ld_reference.smk`, `sumstats.smk`, `regions.smk`, `multitrait.smk`), `config/`, `coloc_batches/`, `genome_wide_analysis/`, `envs/`, top-level `setup_project.sh`, `run_snakemake.sh`, `tmp_run_tiles.py`, `missing_ld_commands.sh`, legacy `README.md` |
| `genome_wide/` | `/rs1/.../coloc_analysis/genome_wide/` | 22 scripts (coloc.abf runner, 7 LSF chunk submitters covering ~7,150 regions, sumstats harmonization, gene annotation, figure generation), `config/` (incl. 7,151-row `genomewide_coloc_manifest.tsv`), `envs/` |
| `ml/` | `/rs1/.../coloc_analysis/ml/` | 5 ML script files + 4 data subdirs (`coloc_recovery/`, `cross_ancestry/`, `gene_prioritization/`, `variant_effects/`) — the hand-weighted scorecard work flagged as methodologically weak in `Revision_Plan.md` §3.5 |
| `create_reproducibility_package.sh` | `/rs1/.../coloc_analysis/` | The script that built `coloc_analysis_reproducibility_pkg.zip` in the pre-revision submission |

Total: **~11.5 MB, 182 files**. No data, no binaries, no LSF log dumps — code
and small config manifests only.

## What's NOT here (lives on /rs1)

- `data_raw/` (21 GB) — symlinked from `data/raw/`
- `data_processed/` (8.6 GB) — symlinked from `data/processed/`
- `results/` (301 MB) — symlinked from `results/legacy/`
- `cache/` (2.3 GB), `logs/` (24 MB), `bin/` (24 MB) — left on /rs1
- `tmp/` (532 GB scratch) — left on /rs1
- `coloc-attempt1-backup.tar.gz` (77 GB full historical backup) — left on /rs1

See `.planning/DECISIONS.md` for the recovery rationale.

## Known issues in the legacy code (audit, don't fix here)

A path-reference audit found **inconsistent hardcoded absolute paths** across
the legacy tree:

- **100 references** to `/share/clintonlab/ckclinto/admix_map/` (the underscore
  path that partially exists on `/share/...`)
- **35 references** to `/share/clintonlab/ckclinto/admixmap/` (the no-underscore
  path that **does not exist anywhere** and produced the broken symlinks in
  the old shadow directories)
- **23 references** to `/gpfs_common/share01/clintonlab/ckclinto`
- **16 references** to `/rs1/researchers/c/ckclinto`

This is a real Phase 0 task: parameterize all of these via
`config/pipeline.yaml` (`data_root`, `legacy_root`, `result_root`) before
any of the legacy scripts can be re-run.

## Method flags from the revision plan that affect this code

Per `Revision_Plan.md` §1 and `GSD_BRIEFING.md` §5.1, the following legacy
files are targets of specific revisions — read the revision plan before
touching any of them:

| Legacy file | Revision target |
|---|---|
| `region_analysis/scripts/run_coloc.R` (uses `coloc::coloc.abf`) | Replace with `coloc.susie` call extended from existing `run_susie_rss.R` (Phase 1) |
| `genome_wide/scripts/run_coloc.R`, `run_coloc_genomewide.R` | Same replacement, genome-wide |
| `region_analysis/scripts/run_susie_rss.R` | Already SuSiE-RSS-based — extend for complex-region policy (REQ-2), not rewrite |
| `region_analysis/scripts/create_mr_design.py`, `workflow/rules/mr.smk` | Stub → full MR pipeline (IVW/Egger/WM/PRESSO/CAUSE/Steiger + weak-instrument mitigation per REQ-4), Phase 3 |
| `region_analysis/scripts/create_pgs_manifest.py`, `workflow/rules/pgs.smk` | Stub → PRS-CSx + calibration + DCA (REQ-6), Phase 8 |
| `ml/scripts/gene_prioritization.py`, `ml/scripts/variant_effect_prediction.py`, `ml/scripts/cross_ancestry_prediction.py` | Hand-weighted scorecard with no train/test split — replace with proper ML or drop entirely, per `Revision_Plan.md` §3.5 |
| `genome_wide/config/genomewide_coloc_manifest.tsv` | Regenerate after sumstats paths are parameterized (Phase 0 task 8) |
