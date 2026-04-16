---
phase: 04-matched-n-cross-ancestry-concordance
reviewed: 2026-04-15T00:00:00Z
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
  critical: 1
  warning: 7
  info: 5
  total: 13
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-04-15
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

Phase 4 implements matched-N cross-ancestry concordance via a SE-inflation bootstrap + coloc.susie pipeline feeding into Table 2 and a supplementary violin figure. The statistical core (SE inflation formula, NCP computation, BH-FDR, H7 verdict logic) is mathematically correct and well-tested. The test suite is thorough, with determinism tests, boundary tests, schema guards, and D-02e regression guards.

One critical bug exists in `run_matched_coloc.R`: after the `tryCatch` block returns `result`, the TSV-writing section references `fit_afr` and `fit_eur` directly, but those variables are scoped inside the `tryCatch` expression and are not available in the outer function scope in standard R evaluation. This will produce a "object 'fit_afr' not found" error for every successful run.

Seven warnings cover: a filename-parsing fragility that will silently misparse any trait containing an underscore (only matters if traits are ever renamed), two resource/correctness issues in `bootstrap_driver.py`, a missing `seed_range_collision` guard in the seed formula, an unhandled edge case in `compute_detection_probability.py` when SE is zero, an implicit dependency issue in the Snakemake DAG, and redundant unused file handle in `bootstrap_driver.py`.

---

## Critical Issues

### CR-01: `fit_afr` / `fit_eur` referenced outside `tryCatch` scope in `run_matched_coloc.R`

**File:** `src/snakemake/scripts/run_matched_coloc.R:121-136`

**Issue:** The variables `fit_afr` and `fit_eur` are assigned inside the `tryCatch({...})` expression body (lines 57–58). In R, the tryCatch body is evaluated in a child environment; assignments made inside it do not propagate to the enclosing environment. After the tryCatch block, `result` is available, but `fit_afr` and `fit_eur` are not. Lines 128–135 then directly index `fit_afr$sets$cs` and `fit_eur$sets$cs`:

```r
cs_afr_list <- fit_afr$sets$cs %||% list()   # line 130 — fit_afr is not defined here
cs_eur_list <- fit_eur$sets$cs %||% list()   # line 134 — fit_eur is not defined here
```

Any production run where `result$status == "success"` will immediately error with "object 'fit_afr' not found", silently producing only the failure-path empty TSV.

**Fix:** Hoist the fit objects out of tryCatch by assigning them before the tryCatch and adding the availability check at the top, or store the fits on the result list and reference them via `result`:

```r
# Option A: assign fits before tryCatch, guard availability
fit_afr <- tryCatch(readRDS(opt$afr_fit), error = function(e) NULL)
fit_eur <- tryCatch(readRDS(opt$eur_matched_fit), error = function(e) NULL)

if (is.null(fit_afr) || is.null(fit_eur)) {
  result <- list(status = "error", error_message = "Failed to load fit RDS",
                 n_cs_afr = NA_integer_, n_cs_eur = NA_integer_, summary = NULL)
} else {
  result <- tryCatch({
    # ... existing coloc logic ...
    list(status = "success", ..., fit_afr = fit_afr, fit_eur = fit_eur)
  }, error = function(e) { ... })
}
```

Or (Option B, minimal diff): store fits on the result list and reference via `result$fit_afr`:

```r
# Inside the success branch of tryCatch, add to the returned list:
list(
  status = "success",
  ...
  fit_afr = fit_afr,  # store for outer use
  fit_eur = fit_eur,
  ...
)
# Then in the TSV section:
cs_afr_list <- result$fit_afr$sets$cs %||% list()
cs_eur_list <- result$fit_eur$sets$cs %||% list()
```

---

## Warnings

### WR-01: Filename parser silently misparsed if any trait contains an underscore

**File:** `src/snakemake/scripts/munge_trait_pair_rg.py:86-111`

**Issue:** `parse_filename` splits the log stem with `rsplit("_", 2)`, then splits the `trait_part` with `rsplit("_", 1)`. The 5 current T1 traits (t2d, stroke, hypertension, asthma, bmi) are all single-word, so this works today. However, the comment on line 100 acknowledges the limitation: "traits have underscores." If a trait were ever named (e.g.) `type_2_diabetes`, a filename like `type_2_diabetes_stroke_EUR_AFR.log` would produce `trait1 = "type_2"`, `trait2 = "diabetes"` — a silent wrong parse producing bad rows in `rg_raw.tsv` and corrupting the FDR table. The failure is silent (no ValueError).

**Fix:** Add a post-parse validation step that checks the reconstructed trait names against the known trait list from config:

```python
KNOWN_TRAITS = {"t2d", "stroke", "hypertension", "asthma", "bmi"}

def parse_filename(log_path, known_traits=KNOWN_TRAITS):
    ...
    # After parsing trait1, trait2:
    if known_traits and trait1 not in known_traits:
        raise ValueError(
            f"Parsed trait1='{trait1}' not in known traits {known_traits} "
            f"from {log_path}. Check underscore splitting."
        )
    return trait1, trait2, ancestry1, ancestry2
```

---

### WR-02: Temporary pseudo-sumstats file not deleted on Rscript success path if `os.unlink` silently fails

**File:** `src/snakemake/scripts/bootstrap_driver.py:151-193`

**Issue:** The temp file `tmp_path` is created without `delete=True` (correct for Windows compat, acceptable on Linux) and culled in the `finally` block (line 190). However, the temp file is written in the inner `with` block, but the `finally` clause only runs after `subprocess.run`. If the Rscript call is very long-running and the LSF job is killed (SIGKILL), the `finally` block does not execute, leaving a potentially large pseudo-sumstats file in `output_dir`. With 100k fits on GPFS, this is a real quota concern.

More importantly: the temp file is created in the **output directory** (`dir=str(output_dir)`) on `/rs1`, not in `/tmp`. Since `output_dir.mkdir(parents=True, exist_ok=True)` precedes the temp file write (line 149), there is no issue with directory creation, but leaked files would be in the same directory as the `.fit.rds` outputs, potentially confusing downstream glob-based R scripts.

**Fix:** Use Python's `tempfile.NamedTemporaryFile` with `dir=tempfile.gettempdir()` so leaked files go to `/tmp` (which is periodically cleared), and only write the final output to `/rs1`:

```python
with tempfile.NamedTemporaryFile(
    mode="w", suffix="_pseudo.tsv",
    dir=tempfile.gettempdir(),   # use /tmp, not the output dir
    delete=False, prefix=f"bootstrap_{args.bootstrap_idx}_"
) as tmp:
    tmp_path = tmp.name
    ...
```

---

### WR-03: `compute_detection_probability.py` — division by zero when SE is 0

**File:** `src/python/compute_detection_probability.py:64`

**Issue:** `ncp = (beta_hat / se) ** 2` at line 64. If any row has `se_afr == 0` (e.g., a monomorphic variant or a data ingestion error), this produces `inf` NCP, and `stats.ncx2.sf(threshold, df=1, nc=np.inf)` returns `nan` silently. The NaN then propagates into the arithmetic mean at line 98, making the trait-level expected concordance `nan` without any warning or error. The test suite does not cover this edge case.

**Fix:** Add an explicit guard before the NCP computation:

```python
se = np.asarray(se, dtype=float)
if np.any(se <= 0):
    raise ValueError(
        f"SE must be positive; found {np.sum(se <= 0)} non-positive values. "
        "Check tier_a input for data quality issues."
    )
ncp = (beta_hat / se) ** 2
```

---

### WR-04: Seed formula collision for trait_id=0

**File:** `src/python/se_inflation.py:103-122` and `config/matched_n.yaml:9`

**Issue:** The seed formula is `seed = seed_base * trait_id + bootstrap_idx`. For `trait_id=0` (t2d), the seed equals `bootstrap_idx` directly (e.g., seed=1 for bootstrap 1, seed=2 for bootstrap 2). While these are unique, they are the same small integers that a caller might pass as `seed=1` in ad-hoc testing — increasing the chance of unintentional seed reuse in downstream user code. More critically: if `bootstrap_n` ever exceeds `seed_base` (100 bootstraps today, seed_base=1000 — fine), or if a sixth trait is added with `trait_id=1`, bootstrap 999 of trait_id=1 collides with bootstrap 1999 of trait_id=1 only — no collision between traits. But `trait_id=0, bootstrap_idx=1000` would collide with `trait_id=1, bootstrap_idx=0` (which is never used since bootstrap_idx starts at 1 per the manifest). This is safe today but fragile.

The real concern is that `compute_seed(trait_id=0, bootstrap_idx=1)` returns `1` — a very small seed that will produce the same RNG state as any other caller who happens to use seed=1.

**Fix:** Offset by a large constant to avoid low-seed overlap:

```python
def compute_seed(trait_id: int, bootstrap_idx: int, seed_base: int = 1000) -> int:
    """seed = seed_base * (trait_id + 1) + bootstrap_idx"""
    # Adding 1 to trait_id ensures trait_id=0 never produces seed=bootstrap_idx
    return seed_base * (trait_id + 1) + bootstrap_idx
```

Note: this is a **pre-registration concern** if the formula was pre-registered. Changing it after OSF registration requires a logged deviation. If the current formula is locked in by pre-registration, document the collision risk with a comment instead of changing the code.

---

### WR-05: Snakemake `compute_tier_a_retention` rule has a proxy input instead of true file dependencies

**File:** `src/snakemake/rules/matched_n.smk:339-345` and `347-379`

**Issue:** The helper function `_expand_bootstrap_coloc_tsvs()` at line 339 is defined but immediately returns only the manifest path — not the actual bootstrap coloc TSVs:

```python
def _expand_bootstrap_coloc_tsvs():
    """Expand all bootstrap coloc_summary.tsv paths for all traits."""
    # This collects the coloc_summary.tsv inputs needed by the retention rule.
    # Actual paths are trait x region x bootstrap, but since we glob at runtime
    # inside the R script, we depend on the manifest as a proxy for completion.
    return str(MATCHED_N_OUT / "manifest.tsv")
```

This function is defined but **never actually called** in the `compute_tier_a_retention` rule input (the rule already lists `manifest` explicitly). More importantly, the rule does not declare the bootstrap coloc TSVs as inputs. The R script globbing over `results/matched_n/coloc/**` at runtime means Snakemake has no DAG edges from `run_matched_coloc` to `compute_tier_a_retention`. If `run_matched_coloc` fails for some bootstraps and Snakemake is rerun, the retention rule will succeed (no missing inputs) but silently produce incorrect concordance estimates from incomplete bootstrap data.

**Fix:** Either (a) enumerate the actual coloc TSV paths as inputs (best for DAG correctness, but requires materializing the manifest before the DAG is constructed — a known Snakemake challenge), or (b) add a sentinel file written by a rule that runs after all bootstrap colocs complete:

```python
# Option B: add a sentinel rule
rule bootstrap_coloc_complete:
    input:
        expand(
            str(MATCHED_N_OUT / "coloc/{trait}/{region}/bootstrap_{b}/coloc_summary.tsv"),
            trait=MATCHED_N_TRAITS,
            region=...,   # from manifest
            b=range(1, BOOTSTRAP_N + 1),
        ),
    output:
        touch(str(MATCHED_N_OUT / "bootstrap_coloc.done")),

# Then compute_tier_a_retention depends on:
# input: ..., done=str(MATCHED_N_OUT / "bootstrap_coloc.done")
```

---

### WR-06: `open_fn` created but never used in `bootstrap_driver.py`

**File:** `src/snakemake/scripts/bootstrap_driver.py:70-71`

**Issue:** Lines 70–71:
```python
open_fn = gzip.open if path.endswith((".gz", ".bgz")) else open
df = pd.read_csv(path, sep="\t", compression="gzip" if path.endswith((".gz", ".bgz")) else None)
```

`open_fn` is assigned and immediately ignored; `pd.read_csv` uses its own `compression` parameter instead. This is harmless but dead code.

**Fix:** Delete the `open_fn` line (line 70):

```python
# Remove:
# open_fn = gzip.open if path.endswith((".gz", ".bgz")) else open
df = pd.read_csv(path, sep="\t", compression="gzip" if path.endswith((".gz", ".bgz")) else None)
```

---

### WR-07: `assemble_table2.py` opens config files without context managers

**File:** `src/python/assemble_table2.py:82-84`

**Issue:**
```python
cfg = yaml.safe_load(open(config_yaml))
ns = yaml.safe_load(open(trait_sample_sizes_yaml))
```

`open()` without a `with` statement leaks file handles. On CPython these are closed by the garbage collector, but on PyPy or under certain LSF environments with high ulimit pressure, unclosed handles accumulate. The `assemble()` function is called once per pipeline run, so the impact is minimal but the pattern is inconsistent with Python best practice.

**Fix:**
```python
with open(config_yaml) as fh:
    cfg = yaml.safe_load(fh)
with open(trait_sample_sizes_yaml) as fh:
    ns = yaml.safe_load(fh)
```

---

## Info

### IN-01: Schema missing `pilot_region` field (present in config but not in schema)

**File:** `schemas/matched_n.schema.yaml` and `config/matched_n.yaml:55`

**Issue:** `config/matched_n.yaml` defines `pilot_region: TCF7L2_10q25_2` (line 55), but the schema has `additionalProperties: false` and does not include a `pilot_region` property. This means the config will fail schema validation as written. Either the schema validation is not actually run (no error observed yet because validation hasn't been wired into CI), or the schema is never used against the actual config file.

**Fix:** Add to `schemas/matched_n.schema.yaml`:
```yaml
  pilot_region:
    type: string
    minLength: 1
    description: "Pilot region for A-1 smoke calibration gate"
```

---

### IN-02: `rg_ancestry_pairs` comment says "30 tests" but code generates 35

**File:** `config/matched_n.yaml:44-45` and `src/snakemake/rules/matched_n.smk:217-224`

**Issue:** The config comment at line 44 says "D-04a: 3 ancestry-pair strata for r_g matrix" and line 217 comment says "D-04a: 10 cross-trait pairs x 3 ancestry-pair strata = 30 tests." The `collect_rg_logs` rule docstring (line 276) and `apply_rg_fdr` docstring (line 297) correctly say "35 tests," but the comment in `RG_COMBOS` (line 220) says "30 tests" in the inline comment on that line. The FDR correction in `apply_fdr.py` operates on all valid rows regardless of count, so the statistical computation is correct — this is a documentation inconsistency, not a code bug.

**Fix:** Update the `# D-04a:` comment at line 217 to note "30 cross-trait + 5 same-trait = 35 total."

---

### IN-03: `n_sign_agree` uses `sum(valid_signs == 1L)` which will not count `TRUE` booleans

**File:** `src/snakemake/scripts/compute_tier_a_retention.R:203` and `src/snakemake/scripts/compute_jaccard.R:220`

**Issue:** `n_agree <- sum(valid_signs == 1L)`. The `lead_sign_agree` column in `coloc_summary.tsv` is written as `integer()` from `run_matched_coloc.R`, so `1L` comparison is correct for integer values. However, if the TSV is read back by `data.table::fread` and the column is coerced to logical (`TRUE`/`FALSE`) rather than integer (`1L`/`0L`), the comparison `== 1L` would evaluate `TRUE == 1L` as `TRUE` in R (R coerces for comparison), so this will work. The risk is subtle: if fread decides the column is character (e.g., due to a mix of `1` and `NA` in string form), the comparison silently returns `FALSE` for all rows. Adding an explicit `as.integer()` coercion before the sum would be more defensive.

**Fix:**
```r
n_agree <- sum(as.integer(valid_signs) == 1L)
```

---

### IN-04: `test_matched_n_tier_a.py` hardcodes `/rs1` conda env path

**File:** `tests/test_matched_n_tier_a.py:33-36`

**Issue:**
```python
_RSCRIPT_CANDIDATES = [
    "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript",
]
```

This is a hardcoded absolute path to the author's personal conda environment. It will silently skip (via `pytest.skip`) on any machine that does not have this exact path, including CI environments and collaborator machines. The fallback to `shutil.which("Rscript")` is appropriate, but the candidate list should use a relative or environment-variable-driven path.

**Fix:**
```python
import os
_RSCRIPT_CANDIDATES = [
    os.environ.get("RSCRIPT_PATH", ""),
    "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript",
]
_RSCRIPT_CANDIDATES = [c for c in _RSCRIPT_CANDIDATES if c]
```

---

### IN-05: `_write_failure_rds` in `bootstrap_driver.py` embeds raw error string into R code without escaping

**File:** `src/snakemake/scripts/bootstrap_driver.py:202-213`

**Issue:**
```python
r_code = f"""
failure <- list(
    ...
    error = "{error_msg[:200]}",
    ...
)
"""
```

The `error_msg` string is sliced to 200 characters and interpolated directly into R source code. If the error message contains a double-quote, backslash, or newline (common in R error output), this produces syntactically invalid R code and the `subprocess.run` call in `_write_failure_rds` will itself fail, falling through to the empty-file fallback. The `CalledProcessError` in the outer `_write_failure_rds` is silently suppressed (except for the empty-file creation). The downstream effect is an empty `.rds` file rather than a proper failure sentinel, which `run_matched_coloc.R` will fail to `readRDS` with a "not an rds file" error rather than detecting the `susie_failure` class.

**Fix:** Escape the error message for safe R string embedding:
```python
safe_msg = error_msg[:200].replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")
r_code = f"""
failure <- list(
    error = "{safe_msg}",
    ...
)
"""
```

---

_Reviewed: 2026-04-15_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
