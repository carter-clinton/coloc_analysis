---
phase: 04-matched-n-cross-ancestry-concordance
fixed_at: 2026-04-15T00:00:00Z
review_path: .planning/phases/04-matched-n-cross-ancestry-concordance/04-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 7
skipped: 1
status: partial
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-04-15
**Source review:** .planning/phases/04-matched-n-cross-ancestry-concordance/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (1 critical, 7 warnings)
- Fixed: 7
- Skipped: 1

## Fixed Issues

### CR-01: `fit_afr` / `fit_eur` referenced outside `tryCatch` scope in `run_matched_coloc.R`

**Files modified:** `src/snakemake/scripts/run_matched_coloc.R`
**Commit:** 2b30eff
**Applied fix:** Stored `fit_afr` and `fit_eur` on the result list inside the tryCatch success path, then changed all downstream references (CS size extraction, lead sign agreement) to use `result$fit_afr` and `result$fit_eur`. Note: the reviewer's claim that tryCatch creates a child environment in R is technically incorrect (tryCatch evaluates expr in the calling frame), so the original code likely worked. However, storing fits on the result list is defensive best practice and eliminates any ambiguity about variable scope. Status: fixed: requires human verification.

### WR-01: Filename parser silently misparsed if any trait contains an underscore

**Files modified:** `src/snakemake/scripts/munge_trait_pair_rg.py`
**Commit:** e4db3a6
**Applied fix:** Added `KNOWN_TRAITS` set and post-parse validation in `parse_filename()` that raises `ValueError` if parsed trait1 or trait2 is not in the known trait list. The `known_traits` parameter allows tests to override or disable the check.

### WR-02: Temporary pseudo-sumstats file not deleted on SIGKILL; written to output dir

**Files modified:** `src/snakemake/scripts/bootstrap_driver.py`
**Commit:** 9e36f75
**Applied fix:** Changed `NamedTemporaryFile` dir parameter from `str(output_dir)` to `tempfile.gettempdir()` so leaked temp files go to `/tmp` (periodically cleared) instead of the GPFS output directory.

### WR-03: `compute_detection_probability.py` -- division by zero when SE is 0

**Files modified:** `src/python/compute_detection_probability.py`
**Commit:** 4f063b9
**Applied fix:** Added explicit guard before NCP computation that raises `ValueError` if any SE values are non-positive, with a count of offending values and diagnostic message.

### WR-04: Seed formula collision for trait_id=0

**Files modified:** `src/python/se_inflation.py`
**Commit:** ddfca50
**Applied fix:** Documented the collision risk in the `compute_seed` docstring (Notes section) rather than changing the formula, because the formula is pre-registered on OSF and changing it would require a logged deviation. The documentation notes: (1) trait_id=0 produces low seed values, (2) bootstrap_n exceeding seed_base causes cross-trait collisions, and (3) current config (bootstrap_n=100, seed_base=1000) is safe.

### WR-06: `open_fn` created but never used in `bootstrap_driver.py`

**Files modified:** `src/snakemake/scripts/bootstrap_driver.py`
**Commit:** 8fd24d1
**Applied fix:** Removed the dead `open_fn` assignment on the line before `pd.read_csv`, which already handles compression via its own `compression` parameter.

### WR-07: `assemble_table2.py` opens config files without context managers

**Files modified:** `src/python/assemble_table2.py`
**Commit:** 5034c3d
**Applied fix:** Wrapped both `open(config_yaml)` and `open(trait_sample_sizes_yaml)` calls with `with` context managers to ensure file handles are properly closed.

## Skipped Issues

### WR-05: Snakemake `compute_tier_a_retention` rule has a proxy input instead of true file dependencies

**File:** `src/snakemake/rules/matched_n.smk:339-345`
**Reason:** The fix requires either enumerating all bootstrap coloc TSVs as Snakemake inputs (which requires materializing the manifest before DAG construction -- a known Snakemake checkpoint challenge) or adding a sentinel rule that depends on dynamically-expanded paths. Both are structural changes to the Snakemake workflow DAG that carry significant risk of breaking the pipeline and cannot be safely validated without running the full DAG. The helper function `_expand_bootstrap_coloc_tsvs()` is also never called (dead code), and the manifest-as-proxy pattern is documented with an explanatory comment. This is best addressed as a deliberate refactoring task with DAG dry-run validation.
**Original issue:** The `compute_tier_a_retention` rule depends on the manifest as a proxy for bootstrap coloc completion, rather than declaring the actual coloc TSVs as inputs. This means Snakemake has no DAG edge from `run_matched_coloc` to `compute_tier_a_retention`, so incomplete bootstrap data could silently produce incorrect concordance estimates.

---

_Fixed: 2026-04-15_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
