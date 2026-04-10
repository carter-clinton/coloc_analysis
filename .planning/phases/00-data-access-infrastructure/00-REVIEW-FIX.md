---
phase: 00-data-access-infrastructure
fixed_at: 2026-04-10T22:20:20Z
review_path: .planning/phases/00-data-access-infrastructure/00-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 0: Code Review Fix Report

**Fixed at:** 2026-04-10T22:20:20Z
**Source review:** .planning/phases/00-data-access-infrastructure/00-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8
- Fixed: 8
- Skipped: 0

## Fixed Issues

### CR-01: Test Snakefile missing FINEMAP_MANIFEST and HARMONIZED_ALL before include

**Files modified:** `tests/toy_3locus/Snakefile.test`
**Commit:** 6e3dc66
**Applied fix:** Moved `HARMONIZED_ALL` list comprehension and `FINEMAP_CONFIG`/`FINEMAP_METHODS`/`FINEMAP_DIR`/`FINEMAP_MANIFEST`/`UNIQUE_TRAIT_ANC` definitions above all `include:` statements. Removed the duplicate `HARMONIZED_ALL` and `UNIQUE_TRAIT_ANC` definitions that previously appeared after the includes. Both variables are now defined before `finemap.smk` is parsed, preventing `NameError` at Snakemake parse time.

### CR-02: HIS ancestry has no 1000 Genomes population mapping -- LD pipeline will fail

**Files modified:** `config/pipeline.yaml`, `Snakefile`, `tests/toy_3locus/Snakefile.test`
**Commit:** 1c6fea2
**Applied fix:** Applied both Option A and Option B from the review. Added `HIS: ["MXL", "PUR", "CLM", "PEL"]` (AMR super-population proxy) to `onekg.populations` in pipeline.yaml. Also added defensive `LD_ANCESTRIES` filtering in both the production and test Snakefiles to only generate LD targets for ancestries that have population mappings, protecting against future additions of unmapped ancestries.

### CR-03: Two Snakemake rules invoke scripts without passing I/O arguments

**Files modified:** `src/snakemake/rules/multitrait.smk`
**Commit:** 8dec9bd
**Applied fix:** Verified the actual CLI interfaces of both legacy scripts before applying the fix. `build_coloc_clean_sets.py` accepts `--input`, `--out-clean`, `--out-clean-h4`. `build_coloc_h4_reports.py` accepts `--coloc-augmented`, `--clean-h4`, `--out-main`, `--out-candidate`, `--out-counts`. Passed all Snakemake-declared inputs and outputs to the scripts via their actual argparse flags. Also added `clean_h4` as an explicit input to `build_coloc_h4_reports` since the script reads it, creating a proper DAG dependency.

### WR-01: Shell injection via string formatting in subprocess call

**Files modified:** `scripts/subset_toy_loci.py`
**Commit:** 688725c
**Applied fix:** Replaced `bash -c "zcat '{}' | head -1".format(input_bgz)` shell command with Python's `gzip.open()` to read the header line. Moved `import gzip` to the top-level imports and removed the inline import. The `subprocess` import is retained for the tabix calls which are safe (no string interpolation into shell).

### WR-02: chrX region in regions_curated.csv has no LD panel coverage

**Files modified:** `Snakefile`, `tests/toy_3locus/Snakefile.test`
**Commit:** 1ae8e0f
**Applied fix:** Added chromosome-level filtering for LD target generation. Both Snakefiles now compute `ONEKG_CHROMS` from `config["onekg"]["chromosomes"]` and filter `REGION_INFOS` to `LD_REGION_INFOS` (only regions whose chromosome has a 1000G VCF). The chrX `BMI_Xq24` region is automatically excluded from LD targets since "X" is not in the chromosomes list. The region remains available for non-LD analyses.

### WR-03: r-hyprcoloc conda package may not exist in specified channels

**Files modified:** `envs/r_coloc.yml`
**Commit:** f017415
**Applied fix:** Confirmed via `conda search` that `r-hyprcoloc` is not available in conda-forge, bioconda, or defaults channels. Removed the `r-hyprcoloc=1.0` dependency (which would cause env creation failure) and replaced with `r-remotes` to enable GitHub installation. Added a comment documenting the post-env-create install command: `Rscript -e 'remotes::install_github("jrs95/hyprcoloc")'`.

### WR-04: Snakemake validate_sumstats rule uses fragile inline Python with Snakemake interpolation

**Files modified:** `src/snakemake/rules/sumstats.smk`, `src/python/validate_sumstats.py`
**Commit:** bf65f0c
**Applied fix:** Extracted the inline Python code from the shell directive into a new standalone script `src/python/validate_sumstats.py` with a proper argparse CLI (`--input`, `--output`, `--trait`, `--ancestry`). Updated the rule's shell directive to call the script with explicit arguments. This eliminates the risk of Snakemake wildcard interpolation breaking Python string literals.

### WR-05: DATASETS_CONFIG loaded without schema validation in main Snakefile

**Files modified:** `Snakefile`
**Commit:** 81ab1eb
**Applied fix:** Added `validate(DATASETS_CONFIG, "src/snakemake/schemas/datasets.schema.yaml")` immediately after loading datasets.yaml. The `validate` import and the `datasets.schema.yaml` file both already exist in the codebase. Malformed datasets config will now be caught at Snakefile parse time rather than surfacing as cryptic runtime errors.

---

_Fixed: 2026-04-10T22:20:20Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
