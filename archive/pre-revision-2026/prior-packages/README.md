# archive/pre-revision-2026/prior-packages/

Point-in-time binary bundles recovered from
`/rs1/researchers/c/ckclinto/coloc_analysis/` on **2026-02-11**.
These files are on disk but are **not tracked in git** (see `.gitignore`) —
they're opaque archives, they don't diff well, and they can be regenerated
from `src/legacy/create_reproducibility_package.sh` if ever needed.

## Inventory

| File | Size | Source | What's inside |
|---|---|---|---|
| `coloc_analysis_reproducibility_pkg.zip` | 247 K | `/rs1/.../coloc_analysis/` root | Minimal reproducibility snapshot — Snakefile, configs, small scripts |
| `ml_analysis_package_20260131.zip` | 64 K | `/rs1/.../coloc_analysis/` root | ML scorecard package (gene priority, variant effects, cross-ancestry, coloc error recovery) |
| `methods_parameters_toolchain_20260122_151528.zip` | 90 K | `/rs1/.../region_analysis/` | Methods + parameters + toolchain bundle (likely accompanying the manuscript submission) |
| `admix_map_export_20260122_143826.zip` | 350 K | `/rs1/.../region_analysis/` | Admixture-mapping export bundle |
| `pathway_enrichment_package_2026-01-27.zip` | 617 K | `/rs1/.../region_analysis/` | Pre-revision pathway-enrichment deliverable (MAGMA + ad-hoc enrichment per `Revision_Plan.md` §3.5) |
| `manuscript_package_20260130.zip` | 1.4 M | `/rs1/.../region_analysis/` | Manuscript + supplementary bundle (corresponds to `ajhg_manu_v10.pdf`) |
| `locuszoom_package_2026-01-27.zip` | 7.2 M | `/rs1/.../region_analysis/` | LocusZoom plots for all Tier-1 signals |
| `colocalization_publication_package_2026-01-27.zip` | 8.4 M | `/rs1/.../region_analysis/` | Full publication-quality coloc deliverable |
| `admix_map_report_bundle_2025-12-14.tar.gz` | 24 M | `/rs1/.../region_analysis/` | Admixture-mapping report bundle (pre-coloc-revision) |

## When you might need these

- **Cross-checking reviewer responses** — if a reviewer asks "what was your original position on X," these bundles are the ground truth of the pre-revision state.
- **Regenerating legacy figures** for direct comparison against revised outputs.
- **Tracing scope changes** — the manifest inside each bundle shows what the analysis looked like at a given date.

## What's NOT here

- **`coloc-attempt1-backup.tar.gz` (77 GB)** — full historical backup. Too large
  for the archive; remains at `/rs1/.../coloc_analysis/coloc-attempt1-backup.tar.gz`.
- **`region_analysis/tmp/` (532 GB)** — scratch workspace. Remains on `/rs1`.
