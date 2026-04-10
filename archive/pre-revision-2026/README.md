# archive/pre-revision-2026/

Frozen snapshot of pre-revision artifacts. **Do not edit anything here.** If
you need something from this directory, copy it out and modify the copy.

| Subdir | Contents |
|---|---|
| `prior-packages/` | Zipped deliverables recovered from `/rs1/researchers/c/ckclinto/coloc_analysis/` as of 2026-02-11: publication package, locuszoom package, pathway enrichment package, methods/parameters/toolchain bundle, manuscript package, admix_map export, reproducibility package, ML analysis package. Each is a point-in-time snapshot of the pre-revision analysis. |
| `shadow-dirs/` | The near-empty `genome_wide/`, `ml/`, `region_analysis/` directories that existed in the GPFS working directory before the canonical repo was created. Preserved for audit trail; contains only htslib build artifacts, broken symlinks, conda caches, and an upstream `hyprcoloc_src` checkout. |

## What lives elsewhere (not here)

- **Full historical backup:** `/rs1/researchers/c/ckclinto/coloc_analysis/coloc-attempt1-backup.tar.gz` (~77 GB). Left in place.
- **Scratch workspace:** `/rs1/researchers/c/ckclinto/coloc_analysis/region_analysis/tmp/` (~532 GB). Left in place.
- **Raw analysis code:** recovered into `src/legacy/` in the root of this repo, not here.
