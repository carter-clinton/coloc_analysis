---
phase: 04-matched-n-cross-ancestry-concordance
reviewed: 2026-04-16T03:52:49Z
depth: standard
files_reviewed: 22
files_reviewed_list:
  - config/matched_n.yaml
  - schemas/matched_n.schema.yaml
  - src/python/apply_fdr.py
  - src/python/assemble_table2.py
  - src/python/compute_detection_probability.py
  - src/python/se_inflation.py
  - src/snakemake/rules/matched_n.smk
  - src/snakemake/scripts/bootstrap_driver.py
  - src/snakemake/scripts/compute_jaccard.R
  - src/snakemake/scripts/compute_tier_a_retention.R
  - src/snakemake/scripts/munge_trait_pair_rg.py
  - src/snakemake/scripts/plot_violin.R
  - src/snakemake/scripts/run_matched_coloc.R
  - tests/conftest.py
  - tests/fixtures/matched_n/synthetic_bootstraps/create_fixtures.py
  - tests/test_matched_n_bootstrap_driver.py
  - tests/test_matched_n_detection.py
  - tests/test_matched_n_fdr.py
  - tests/test_matched_n_h7.py
  - tests/test_matched_n_negcontrol.py
  - tests/test_matched_n_se_inflation.py
  - tests/test_matched_n_table2.py
  - tests/test_matched_n_tier_a.py
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues_found
---

# Phase 4: Code Review Report (Re-Review)

**Reviewed:** 2026-04-16T03:52:49Z
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

This is a re-review following the application of 7 of 8 fixes from the prior review. All 7 targeted fixes were correctly applied with no regressions introduced. WR-05 (missing DAG edge) remains intentionally skipped as a structural Snakemake change.

One new warning was found during fix verification: a pre-existing logic bug in `run_matched_coloc.R` that was not caught in the prior review. `length(result$n_cs_afr)` in the CS size extraction bounds check is always `1` (length of a scalar in R), which silently produces `NA` for `cs_afr_size` and `cs_eur_size` on all multi-signal coloc pairs where `idx1 >= 2` or `idx2 >= 2`. The bug does not affect `pph4`, Tier A retention, H7 verdicts, or any primary analysis output; it corrupts only the `cs_afr_size` / `cs_eur_size` columns in `coloc_summary.tsv` for multi-signal loci.

The statistical core (SE inflation, NCP computation, BH-FDR, H7 verdict, Tier A retention, Jaccard) remains correct and well-tested. The pipeline is sound for single-signal loci, which are the large majority of T1 GWAS loci.

---

## Fix Verification

| Prior ID | Description | Status |
|----------|-------------|--------|
| CR-01 | `fit_afr`/`fit_eur` scope in `run_matched_coloc.R` | FIXED — stored on result list, accessed via `result$fit_afr` |
| WR-01 | trait validation in `munge_trait_pair_rg.py` `parse_filename` | FIXED — `known_traits` guard added with ValueError on mismatch |
| WR-02 | pseudo-sumstats written to output_dir instead of `/tmp` | FIXED — `tempfile.gettempdir()` used; cleanup in `finally` block |
| WR-03 | SE=0 not guarded in `compute_detection_probability.py` | FIXED — `np.any(se <= 0)` raises `ValueError` before NCP computation |
| WR-04 | seed collision risk undocumented in `compute_seed` | FIXED — `Notes` section added to docstring with safe-range annotation |
| WR-05 | `compute_tier_a_retention` uses manifest as DAG proxy | SKIPPED (intentional — structural Snakemake change deferred) |
| WR-06 | dead `open_fn` variable in `bootstrap_driver.py` | FIXED — variable removed; `pd.read_csv` handles compression directly |
| WR-07 | bare `open()` without context manager in `assemble_table2.py` | FIXED — both config file reads use `with open()` |

---

## Warnings

### WR-01 (new): `length(result$n_cs_afr)` outer guard is always 1, making `cs_afr_size` and `cs_eur_size` NA for all multi-signal pairs

**File:** `src/snakemake/scripts/run_matched_coloc.R:130,136`

**Issue:** The outer bounds check for CS size extraction reads:

```r
cs_afr_size <- if (!is.na(idx1) && idx1 <= length(result$n_cs_afr)) {
```

`result$n_cs_afr` is a scalar integer (e.g., `3` for three credible sets). `length()` of any scalar in R is always `1`. So `idx1 <= length(result$n_cs_afr)` reduces to `idx1 <= 1`. For any coloc signal pair where `idx1 >= 2` (multi-signal loci), the outer condition evaluates `FALSE` and `cs_afr_size` is set to `NA_integer_` without inspecting the credible set list. The same bug appears on line 136 for `cs_eur_size` via `result$n_cs_eur`.

The inner guard on line 133 (`idx1 <= length(cs_afr_list)`) is correct and would properly bound-check against the actual CS count — but it is never reached for `idx1 >= 2` because the outer guard short-circuits first.

For single-signal loci (`idx1 = 1, idx2 = 1`), which are the majority of T1 GWAS loci, this bug is silent. For multi-signal loci, `cs_afr_size` and `cs_eur_size` are incorrectly `NA` in `coloc_summary.tsv`, which propagates to the supplementary table. The primary metrics (`pph4`, Tier A retention, H7 verdict) are not affected.

**Fix:** Replace `length(result$n_cs_afr)` with `result$n_cs_afr` (and similarly for `n_cs_eur`):

```r
cs_afr_size <- if (!is.na(idx1) && idx1 <= result$n_cs_afr) {
  cs_afr_list <- result$fit_afr$sets$cs %||% list()
  if (idx1 <= length(cs_afr_list)) length(cs_afr_list[[idx1]]) else NA_integer_
} else NA_integer_

cs_eur_size <- if (!is.na(idx2) && idx2 <= result$n_cs_eur) {
  cs_eur_list <- result$fit_eur$sets$cs %||% list()
  if (idx2 <= length(cs_eur_list)) length(cs_eur_list[[idx2]]) else NA_integer_
} else NA_integer_
```

### WR-02 (carry-over): Missing DAG edge — `compute_tier_a_retention` uses manifest as bootstrap proxy

**File:** `src/snakemake/rules/matched_n.smk:339-345, 347-379`

**Issue:** `_expand_bootstrap_coloc_tsvs()` returns only the manifest path rather than the actual `coloc_summary.tsv` outputs. If `run_matched_coloc` jobs fail silently (writing empty TSVs), Snakemake will consider `compute_tier_a_retention` ready as soon as the manifest exists, without verifying bootstrap coloc outputs are present and non-empty. This was WR-05 in the prior review and remains intentionally skipped.

**Status:** Skipped per prior decision. Documented here for completeness.

---

## Info

### IN-01: `pilot_region` in `config/matched_n.yaml` not declared in schema

**File:** `schemas/matched_n.schema.yaml` and `config/matched_n.yaml:55`

**Issue:** `config/matched_n.yaml` defines `pilot_region: TCF7L2_10q25_2` (line 55). The schema has `additionalProperties: false` and does not include `pilot_region` in `properties`. Any YAML schema validator applied to the config will reject it as invalid.

**Fix:** Add to `schemas/matched_n.schema.yaml` under `properties` (no need to add to `required`):

```yaml
pilot_region:
  type: string
  minLength: 1
  description: "Single region for A-1 smoke pilot calibration gate"
```

### IN-02: Comment in `config/matched_n.yaml` says "30 r_g tests" but there are 35

**File:** `config/matched_n.yaml:23`

**Issue:** Line 23 reads `# D-04c: BH-FDR q<0.05 across ALL 30 r_g tests`. The actual count is 35: 30 cross-trait pairs (10 × 3 strata) plus 5 same-trait EUR-AFR benchmarks. The Snakemake rule correctly documents 35 at `matched_n.smk:209`. The discrepancy creates ambiguity when auditing the config against the pre-registration.

**Fix:** Update the comment: `# D-04c: BH-FDR q<0.05 across ALL 35 r_g tests (30 cross-trait + 5 same-trait EUR-AFR benchmarks)`

### IN-03: Hardcoded `/rs1` Rscript path in `test_matched_n_tier_a.py`

**File:** `tests/test_matched_n_tier_a.py:33-35`

**Issue:** `_RSCRIPT_CANDIDATES` hardcodes `/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript`. The test falls back to `shutil.which("Rscript")` if the path does not exist, so CI on other systems is not broken. Acceptable for the solo HPC context; no action required.

### IN-04: `_write_failure_rds` embeds raw error string into R code without escaping

**File:** `src/snakemake/scripts/bootstrap_driver.py:205,210-212`

**Issue:** `error_msg[:200]` and `output_path` are interpolated directly into an f-string that becomes R source code passed to `Rscript -e`. If `error_msg` contains a double-quote, backslash, or newline (all common in R error messages), the generated R code is syntactically invalid and the failure RDS is not written. The `except CalledProcessError` fallback touches an empty file, which is safe for Snakemake but loses the error message. This was IN-05 in the prior review.

**Fix:** Sanitize both strings before interpolation:

```python
safe_msg = (error_msg[:200]
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", " "))
safe_path = output_path.replace("\\", "\\\\").replace('"', '\\"')
r_code = f"""
failure <- list(
    status = "susie_failure",
    bootstrap_idx = {bootstrap_idx}L,
    error = "{safe_msg}",
    converged = FALSE,
    sets = list(cs = list())
)
class(failure) <- c("susie_failure", "list")
dir.create(dirname("{safe_path}"), recursive = TRUE, showWarnings = FALSE)
saveRDS(failure, "{safe_path}")
cat("Wrote failure RDS:", "{safe_path}", "\\n")
"""
```

---

_Reviewed: 2026-04-16T03:52:49Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
