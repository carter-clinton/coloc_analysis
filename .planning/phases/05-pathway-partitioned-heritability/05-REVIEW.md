---
phase: 05-pathway-partitioned-heritability
reviewed: 2026-04-13T22:45:00Z
depth: standard
files_reviewed: 31
files_reviewed_list:
  - config/pathway_sets/custom_cardiometabolic.gmt
  - config/pathway_sets/negative_controls.gmt
  - config/pipeline.yaml
  - docs/methods/phase5_methods_fragment.md
  - envs/gprofiler.yml
  - envs/hess_py27.yml
  - envs/ldsc_py3.yml
  - envs/magma.yml
  - Snakefile
  - src/python/aggregate_pathway_results.py
  - src/python/build_gprofiler_bg.py
  - src/python/build_ldsc_annot.py
  - src/python/build_magma_geneset.py
  - src/python/extend_null_genesets.py
  - src/python/munge_sumstats_ldsc.py
  - src/python/run_gprofiler.py
  - src/python/run_hess.py
  - src/python/run_ldsc_partitioned.py
  - src/python/run_ldsc_seg.py
  - src/python/run_magma.py
  - src/python/sumstats_utils.py
  - src/snakemake/rules/pathway.smk
  - src/snakemake/schemas/pipeline.schema.yaml
  - tests/phase5/conftest.py
  - tests/phase5/__init__.py
  - tests/phase5/test_gprofiler.py
  - tests/phase5/test_hess.py
  - tests/phase5/test_ldsc_partitioned.py
  - tests/phase5/test_ldsc_seg.py
  - tests/phase5/test_magma_geneset.py
  - tests/phase5/test_negative_controls.py
  - tests/phase5/test_permutation_null.py
findings:
  critical: 2
  warning: 8
  info: 5
  total: 15
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-04-13T22:45:00Z
**Depth:** standard
**Files Reviewed:** 31
**Status:** issues_found

## Summary

Phase 5 implements a pathway and partitioned heritability analysis pipeline
with six analytical components (MAGMA, g:Profiler, LDSC partitioned, LDSC-SEG,
HESS, permutation null). The codebase is well-structured with strong security
discipline: all subprocess calls use list arguments (no shell=True), input
paths are validated before use, and negative controls are properly enforced.

Two critical issues were found: (1) the g:Profiler API response parser
incorrectly assigns p_value to q_value (losing the FDR-corrected value), and
(2) the Snakemake rule for MAGMA gene analysis hard-codes sample size=500000
for all traits, ignoring binary trait effective-N computation. Eight warnings
cover missing conda version pins, a sumstats filename pattern mismatch between
build_gprofiler_bg.py and pathway.smk, and several robustness gaps in error
handling.

## Critical Issues

### CR-01: g:Profiler API response parser assigns p_value to q_value field

**File:** `src/python/run_gprofiler.py:131`
**Issue:** In `_parse_api_results()`, line 131 sets `"q_value": entry.get("p_value", float("nan"))` -- this copies the raw p_value into the q_value field. The g:Profiler API returns FDR-adjusted p-values directly (when `significance_threshold_method: "fdr"` is set, the returned `p_value` IS the adjusted value), but if the API ever returns separate corrected values (e.g., in a different response format), this code would silently lose them. More importantly, the comment says "After FDR" but the code fetches the same field as the raw p_value, making the two columns indistinguishable in the output TSV. Downstream consumers (aggregate_pathway_results.py) reference both `p_value` and `q_value` columns independently, and `_write_results_tsv` writes both to disk. If the API schema changes or a user expects q_value to be independently computed, this creates a silent correctness bug in the cross-method aggregation where MAGMA has true FDR q-values but g:Profiler has duplicated p-values.
**Fix:**
```python
# Line 130-131: Use the correct field for q_value
"p_value": entry.get("p_value", float("nan")),
"q_value": entry.get("p_value", float("nan")),  # g:Profiler FDR-adjusted p_value IS the q_value when significance_threshold_method="fdr"
# TODO: If g:Profiler API adds a separate "adjusted_p_value" field, update this mapping
```
At minimum, add a comment documenting why p_value and q_value are the same. Better: check for a dedicated corrected p-value field in the response and fall back to p_value only if absent:
```python
"q_value": entry.get("adjusted_p_value", entry.get("p_value", float("nan"))),
```

### CR-02: Snakemake magma_gene_analysis rule hard-codes --sample-size 500000 for all traits

**File:** `src/snakemake/rules/pathway.smk:453`
**Issue:** The `magma_gene_analysis` rule passes `--sample-size 500000` for ALL trait x ancestry combinations. For binary traits (T2D, hypertension, asthma, stroke), the run_magma.py script correctly supports `--trait`, `--n-case`, and `--n-ctrl` flags to compute effective N = 4/(1/n_case + 1/n_ctrl), but the Snakemake rule never passes case/control counts. This means binary traits will use N=500000 instead of the proper effective N, which inflates statistical power for binary traits with imbalanced case/control ratios. The methods fragment (docs/methods/phase5_methods_fragment.md) explicitly states "effective N = 4/(1/n_case + 1/n_ctrl) for binary traits" and the run_magma.py code handles this correctly -- the bug is purely in the Snakemake wiring.
**Fix:** Add per-trait case/control counts from the dataset config and pass `--n-case` and `--n-ctrl` for binary traits:
```python
rule magma_gene_analysis:
    # ...
    params:
        # ... existing params ...
        trait=lambda wc: wc.trait,
        # Add case/control counts from datasets config for binary traits
        n_case=lambda wc: DATASETS_CONFIG.get(wc.trait, {}).get("n_case", ""),
        n_ctrl=lambda wc: DATASETS_CONFIG.get(wc.trait, {}).get("n_ctrl", ""),
    shell:
        """
        python {params.script} --step gene \
            --magma-binary {input.magma} \
            --bfile {params.bfile} \
            --pval {input.sumstats} \
            --gene-annot {input.annot} \
            --trait {params.trait} \
            --n-case {params.n_case} --n-ctrl {params.n_ctrl} \
            --out {params.out_prefix}
        """
```
Similarly, the `ldsc_munge` rule (line 575) also hard-codes `--sample-size 500000` and should use effective N for binary traits.

## Warnings

### WR-01: Sumstats filename pattern mismatch between build_gprofiler_bg.py and pathway.smk

**File:** `src/python/build_gprofiler_bg.py:329` and `src/snakemake/rules/pathway.smk:1289`
**Issue:** `build_gprofiler_bg.py` constructs sumstats paths as `{trait}_{ancestry}.tsv` (underscore separator), but the Snakemake `build_gprofiler_background` rule input uses `{trait}_EUR.tsv`. Meanwhile, the harmonized sumstats directory uses `{trait}.{ancestry}.tsv.bgz` (dot separator, bgzipped). The script's path construction at line 329 (`f"{trait}_{args.ancestry}.tsv"`) will not match the actual files in `data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz`. The Snakemake rule input pattern at line 1289 also uses `{trait}_EUR.tsv` (underscore, no .bgz).
**Fix:** Align the filename pattern. In `build_gprofiler_bg.py` line 329:
```python
sumstats_paths = [
    os.path.join(args.sumstats_dir, f"{trait}.{args.ancestry}.tsv.bgz")
    for trait in traits
]
```
And in `pathway.smk` line 1289:
```python
sumstats=expand(
    os.path.join(config["paths"]["harmonized_sumstats"], "{trait}.EUR.tsv.bgz"),
    trait=config.get("traits", []),
),
```

### WR-02: Conda environment specs lack version pins for most packages

**File:** `envs/gprofiler.yml:10-15`
**Issue:** The gprofiler.yml env has `r-base>=4.2`, `r-gprofiler2`, `r-dplyr`, `r-readr`, and `r-yaml` with no version pins (or only lower bounds). The CLAUDE.md project constraints specify version-pinned conda envs for reproducibility (REQ-9), and the methods fragment explicitly states "All conda environment specifications are version-pinned (REQ-9)". Using `>=` or unpinned specs means builds may resolve differently over time. The `magma.yml` and `ldsc_py3.yml` have similar issues with `>=` bounds instead of exact pins.
**Fix:** Pin exact versions. For example in `envs/gprofiler.yml`:
```yaml
dependencies:
  - r-base=4.3.1
  - r-gprofiler2=0.2.2
  - r-dplyr=1.1.4
  - r-readr=2.1.5
  - r-yaml=2.3.8
```

### WR-03: aggregate_pathway_results.py formats NaN floats without guard on string formatting

**File:** `src/python/aggregate_pathway_results.py:342-352`
**Issue:** Lines 342-352 use f-string formatting like `f"{best_magma['magma_beta']:.4f}"` without checking whether the value is NaN. While Python `float('nan')` does format with `:.4f` (producing "nan"), the resulting string "nan" is inconsistent with the "NA" used elsewhere for missing values. More importantly, if `best_magma` exists but `magma_beta` is NaN, the formatted value becomes "nan" while missing entries produce "NA", creating two different representations of missing data in the output.
**Fix:** Add NaN guards:
```python
"magma_beta": f"{best_magma['magma_beta']:.4f}" if best_magma and not math.isnan(best_magma['magma_beta']) else "NA",
```

### WR-04: extend_null_genesets.py gene.loc parser uses tab split but file is whitespace-delimited

**File:** `src/python/extend_null_genesets.py:64`
**Issue:** `parse_gene_loc()` at line 64 uses `line.split("\t")` to parse the gene.loc file. However, NCBI37.3.gene.loc is whitespace-delimited (often spaces, not tabs). The other parsers in the codebase (`build_gprofiler_bg.py:57`, `build_ldsc_annot.py:44`, `build_magma_geneset.py:49`) correctly use `line.split()` (split on any whitespace). If the gene.loc file has space-delimited fields, this parser will produce a single-element list per line and skip all genes due to `len(parts) < 6`.
**Fix:**
```python
# Line 64: Use whitespace split to match other parsers
parts = line.split()
```

### WR-05: run_gprofiler.py R fallback mode interpolates file path into R script without sanitization

**File:** `src/python/run_gprofiler.py:308-352`
**Issue:** The `run_enrichment_r()` function interpolates `output_path` directly into an R script string via f-string (line 337: `file = "{output_path}"`). While the function is invoked only through the CLI where output_path comes from argparse, if a file path contained R metacharacters (e.g., double quotes or backslashes on Windows-style paths), it could break the R script or cause unintended behavior. Gene symbols are also interpolated into R character vectors without escaping.
**Fix:** Escape the output path and gene symbols for R string safety:
```python
# Escape backslashes and quotes in the output path
safe_output = output_path.replace("\\", "\\\\").replace('"', '\\"')
# Use the escaped version in the R script
```
Or write gene lists to temp files and read them from R, avoiding inline interpolation entirely.

### WR-06: hess_negative_controls rule writes a placeholder instead of actual results

**File:** `src/snakemake/rules/pathway.smk:1215-1218`
**Issue:** The `hess_negative_controls` rule writes only a placeholder comment file instead of actual negative control comparison results. The output file header is written (line 1216), but data rows are just comments (lines 1217-1218). This means the negative control validation pipeline for HESS is incomplete -- the `validate_negative_controls` rule reads this file but will find zero data rows, making HESS negative controls vacuously pass validation.
**Fix:** Implement the actual HESS negative control comparison by mapping negative control gene sets to genomic coordinates and running `compare_pleiotropic_vs_background` with those coordinates instead of the curated regions.

### WR-07: magma_fdr rule imports pandas and statsmodels without conda env

**File:** `src/snakemake/rules/pathway.smk:497-542`
**Issue:** The `magma_fdr` rule uses a `run:` block (not `shell:` with `conda:`) that imports `pandas`, `scipy.stats`, and `statsmodels.stats.multitest`. Since `run:` blocks execute in the host Snakemake environment (not a conda env), these packages must be available in the base environment. The magma.yml conda env does not include `statsmodels` or `scipy`, and the `run:` block cannot use conda environments in Snakemake 7.x. If the host env lacks statsmodels, this rule will fail at runtime.
**Fix:** Either convert to a `shell:` + `conda:` rule that calls a standalone Python script, or add `statsmodels` and `scipy` to the magma.yml env and convert the rule to use `script:` or `shell:`.

### WR-08: Sumstats file pattern inconsistency in Snakemake rules

**File:** `src/snakemake/rules/pathway.smk:433`
**Issue:** The `magma_gene_analysis` rule expects input sumstats at `{trait}_{ancestry}.tsv` (underscore separator, no compression extension), but the harmonized sumstats are stored as `{trait}.{ancestry}.tsv.bgz` (dot separator, bgzipped). This pattern mismatch appears in multiple rules (`hess_format_sumstats` at line 1006, `ldsc_munge` at line 552). These rules will fail to find their input files unless there is an intermediate rule that creates the underscore-named copies.
**Fix:** Update the input patterns to match the actual harmonized sumstats format:
```python
sumstats=os.path.join(
    config["paths"]["harmonized_sumstats"], "{trait}.{ancestry}.tsv.bgz"
),
```

## Info

### IN-01: pipeline.schema.yaml does not require the pathway section

**File:** `src/snakemake/schemas/pipeline.schema.yaml:8`
**Issue:** The `pathway` section is defined in the schema (line 231) but is not listed in the top-level `required` array (line 8). If `pipeline.yaml` omits the `pathway` section entirely, schema validation will pass but `pathway.smk` will silently use empty defaults from `config.get("pathway", {})`. This is by design (Phase 5 is optional), but worth noting as it means misconfiguration (e.g., typo `pathways:` instead of `pathway:`) would be silently ignored.
**Fix:** If Phase 5 is intended to always run, add `"pathway"` to the required list. Otherwise, add a validation check at the top of `pathway.smk`:
```python
if not PATHWAY_CFG:
    logger.warning("No pathway section in pipeline.yaml; Phase 5 rules will use defaults")
```

### IN-02: custom_cardiometabolic.gmt has trailing empty line

**File:** `config/pathway_sets/custom_cardiometabolic.gmt:9`
**Issue:** Line 9 of the GMT file is empty. While the GMT parsers correctly handle empty lines (they skip them), this adds a trailing blank that could confuse line-count-based assertions. The test `test_custom_gmt_has_8_sets` correctly filters empty lines.
**Fix:** Remove the trailing empty line from the GMT file.

### IN-03: negative_controls.gmt has trailing empty line

**File:** `config/pathway_sets/negative_controls.gmt:4`
**Issue:** Same as IN-02: trailing empty line. Parsers handle it, but cleaner without.
**Fix:** Remove trailing empty line.

### IN-04: Unused `_header` variable in extend_null_genesets.py

**File:** `src/python/extend_null_genesets.py:124`
**Issue:** In `_parse_frq_file()` (line 124), the variable `header = f.readline()` is assigned but never used. Similarly in `_parse_frq_file_gz()` at line 143.
**Fix:** Replace with `_ = f.readline()` or `f.readline()` to indicate intentional discard.

### IN-05: run_magma.py imports shutil inside a try block

**File:** `src/python/run_magma.py:345`
**Issue:** `import shutil` is placed inside the `finally` block of `run_gene_analysis()` rather than at the top of the file. While this works, top-level imports are the Python convention and make dependencies visible.
**Fix:** Move `import shutil` to the top of the file with the other imports.

---

_Reviewed: 2026-04-13T22:45:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
