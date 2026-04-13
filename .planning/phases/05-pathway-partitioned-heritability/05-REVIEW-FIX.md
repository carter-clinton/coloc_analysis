---
phase: 05-pathway-partitioned-heritability
fixed_at: 2026-04-13T23:30:00Z
review_path: .planning/phases/05-pathway-partitioned-heritability/05-REVIEW.md
iteration: 1
findings_in_scope: 10
fixed: 10
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-04-13T23:30:00Z
**Source review:** .planning/phases/05-pathway-partitioned-heritability/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 10 (2 critical, 8 warning; info deferred)
- Fixed: 10
- Skipped: 0
- Pytest (tests/phase5/): 100/100 passing (unchanged from baseline)

## Fixed Issues

### CR-01: g:Profiler API response parser assigns p_value to q_value field

**Files modified:** `src/python/run_gprofiler.py`
**Commit:** 84daabd
**Applied fix:** In `_parse_api_results()` the `q_value` field now prefers the
API's `adjusted_p_value` key when present and falls back to `p_value`. Added a
docstring comment explaining why p_value and q_value coincide in the default
`significance_threshold_method="fdr"` path. This removes the silent correctness
bug where a future schema change would duplicate raw p-values into the q_value
column.

### CR-02: Snakemake magma_gene_analysis rule hard-codes --sample-size 500000 for all traits

**Files modified:** `config/pipeline.yaml`, `src/snakemake/rules/pathway.smk`
**Commit:** 818071f
**Status:** fixed: requires human verification
**Applied fix:** Added `pathway.trait_counts` block to `pipeline.yaml` with per-
trait (type, sample_size | n_case + n_ctrl) values drawn from the published
dataset references. Added `_magma_n_flags(trait)` helper in `pathway.smk` that
emits `--n-case N --n-ctrl N` for binary traits and `--sample-size N` for
quantitative traits. Wired the helper into both `magma_gene_analysis` and
`ldsc_munge` rules, replacing the hard-coded `--sample-size 500000`. The
downstream `run_magma.py` / `run_ldsc_partitioned.py` scripts already compute
`N_eff = 4/(1/n_case + 1/n_ctrl)` via `sumstats_utils.compute_effective_n`.
**Requires verification:** the published n_case/n_ctrl values in
`pathway.trait_counts` are reasonable approximations from the dataset
references and should be refined once post-harmonization per-ancestry counts
are measured from the downloaded sumstats. The *wiring* is correct; the
specific integers will need a small config update before publication.

### WR-01 + WR-08: Sumstats filename pattern mismatch between scripts and pathway.smk

**Files modified:** `src/python/build_gprofiler_bg.py`, `src/python/run_magma.py`,
`src/python/run_hess.py`, `src/snakemake/rules/pathway.smk`
**Commit:** a91deb6
**Applied fix:** Aligned all sumstats path patterns with the canonical
`{trait}.{ancestry}.tsv.bgz` format produced by `sumstats.smk` (dot separator,
bgzipped). Updated four Snakemake rules (`magma_gene_analysis`, `ldsc_munge`,
`hess_format_sumstats`, `build_gprofiler_background`) and the path construction
in `build_gprofiler_bg.py`. Added a `_open_sumstats()` helper to three scripts
(`run_magma.py`, `run_hess.py`, `build_gprofiler_bg.py`) that transparently
handles `.bgz/.gz` via `gzip.open`, since BGZF is gzip-compatible at the read
level. `munge_sumstats_ldsc.py` already had this logic.

### WR-02: Conda environment specs lack version pins

**Files modified:** `envs/gprofiler.yml`, `envs/magma.yml`, `envs/ldsc_py3.yml`
**Commit:** 2492bb4
**Applied fix:** Replaced `>=` and unpinned specs with exact version pins for
all three envs. `envs/hess_py27.yml` was already pinned. Versions chosen to
match the conda-forge / bioconda snapshot at the time of Phase 5 initial build
(April 2026) and noted as such in a header comment referencing REQ-9.

### WR-03: aggregate_pathway_results.py formats NaN floats without guard

**Files modified:** `src/python/aggregate_pathway_results.py`
**Commit:** d4ed3ca
**Applied fix:** Replaced the bare f-string format calls with a local `_fmt()`
helper that returns `"NA"` when the value is `None` or `NaN`, producing a
consistent missing-value representation across every output column (previously
NaN values would render as the string `"nan"` while missing dict entries
rendered as `"NA"`).

### WR-04: extend_null_genesets.py gene.loc parser uses tab split

**Files modified:** `src/python/extend_null_genesets.py`
**Commit:** a0eb372
**Applied fix:** Changed `line.split("\t")` to `line.split()` in
`parse_gene_loc()`, matching the whitespace-split convention used by the other
three gene.loc parsers in the codebase. The NCBI37.3.gene.loc file is
whitespace-delimited (often spaces), and the previous tab-only split would
have silently produced zero genes.

### WR-05: run_gprofiler.py R fallback mode interpolates paths without sanitization

**Files modified:** `src/python/run_gprofiler.py`
**Commit:** 25c8812
**Applied fix:** Added a local `_r_str()` escape helper that escapes backslashes
and double quotes before interpolating strings into the R script template.
Applied it to the output path, query gene list, background gene list, and
source list. This prevents R script breakage if a path ever contains a quote or
backslash.

### WR-06: hess_negative_controls rule writes a placeholder

**Files modified:** `src/snakemake/rules/pathway.smk`
**Commit:** d2b1305
**Status:** fixed: requires human verification
**Applied fix:** Replaced the placeholder write with a real implementation that
(1) parses `NCBI37.3.gene.loc` into a symbol->coordinate map, (2) iterates over
each row of the negative-control GMT file, (3) maps member gene symbols to
genomic coordinates with a +/- `snp_gene_window_kb` window, (4) writes a
temporary regions CSV per set, (5) invokes
`run_hess.compare_pleiotropic_vs_background` against that CSV, and (6) writes
one TSV row per negative-control set with mean_pleio/mean_bg/ratio/z_score/
p_value and a `significant_at_0.05` flag. Gracefully handles empty mappings
and overlap-error cases by emitting NA rows.
**Requires verification:** the implementation is end-to-end but has not been
exercised against real HESS output (the upstream `hess_local_rhog` rule is not
yet end-to-end tested in CI). A human should spot-check the first real run to
confirm z-scores and p-values land in the expected non-significant range.

### WR-07: magma_fdr rule imports pandas and statsmodels without conda env

**Files modified:** `envs/magma.yml`, `src/python/magma_fdr.py` (new),
`src/snakemake/rules/pathway.smk`
**Commit:** 1903fc3
**Applied fix:** Extracted the FDR logic from the `run:` block into a new
standalone script `src/python/magma_fdr.py` with a `--gsa / --out` CLI.
Converted the `magma_fdr` rule to `shell:` + `conda: MAGMA_ENV` and added
`statsmodels=0.14.1` and `scipy=1.11.4` to `envs/magma.yml`. This ensures the
dependencies come from the pinned conda env rather than the host interpreter.

## Verification

- **Pytest baseline:** 100/100 passing before fixes
- **Pytest after fixes:** 100/100 passing (no regressions)
- **Syntax checks:** All modified Python files pass `ast.parse`; all YAML
  files pass `yaml.safe_load`; `pathway.smk` parses via `snakemake --list`
- **Atomic commits:** each finding has a dedicated commit (WR-01 and WR-08
  were combined into a single commit because they describe the same underlying
  file-pattern mismatch and the fix touches the same scripts/rules)

## Skipped Issues

None.

## Info findings (out of scope)

Not addressed this iteration per `fix_scope: critical_warning`: IN-01
(schema missing `pathway` from required), IN-02 and IN-03 (trailing empty lines
in GMTs), IN-04 (unused `_header` variable in `extend_null_genesets.py`),
IN-05 (`import shutil` inside `run_magma.run_gene_analysis` finally block --
this one was incidentally resolved when `shutil` was moved to the top of the
file as part of the WR-01/WR-08 commit).

---

_Fixed: 2026-04-13T23:30:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
