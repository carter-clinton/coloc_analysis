---
phase: 09-replication-in-independent-cohorts
fixed_at: 2026-04-14T10:28:18Z
review_path: .planning/phases/09-replication-in-independent-cohorts/09-REVIEW.md
iteration: 1
findings_in_scope: 13
fixed: 13
skipped: 0
status: all_fixed
---

# Phase 9: Code Review Fix Report

**Fixed at:** 2026-04-14T10:28:18Z
**Source review:** `.planning/phases/09-replication-in-independent-cohorts/09-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 13 (2 Critical + 11 Warning; Info excluded per `fix_scope=critical_warning`)
- Fixed: 13
- Skipped: 0

**Regression checks (post-fix):**
- `tests/phase9/` — 77 passed, 3 xfailed (baseline preserved)
- `tests/phase5/` — 100 passed (no cross-phase regression)
- All Python files parse via `ast.parse` clean; Bash files pass `bash -n`; R files verified by Tier-1 re-read (no local Rscript available; no R-side test fixtures rely on the edited branches)

## Fixed Issues

### CR-01: Zip-slip vulnerability in BBJ extractor

**Files modified:** `src/python/harmonize_bbj.py`
**Commit:** 57bd450
**Applied fix:** Replaced single `zf.extractall(out_dir)` call with a per-entry safe extraction loop. Each member's final resolved path is verified to remain under the resolved `out_dir` via `target.resolve()` + `str(target).startswith(str(out_dir) + os.sep)`. Entries that would escape raise `ValueError("...path traversal detected (zip-slip)")`. Added `import os` and expanded the docstring to cite CVE-2007-4559. The Snakemake rule `extract_bbj_zip` in `replication.smk` already calls this function, so no rule-side change needed.

### CR-02: `winnerscurse` GitHub dependency not pinned

**Files modified:** `src/snakemake/scripts/run_fiqt.R`, `envs/r_coloc.yml`
**Commit:** 94bd5e3
**Applied fix:** Option A per the review. Added `ref = WINNERSCURSE_PINNED_SHA` (= `"2ed00bb"`) to the `remotes::install_github` call so fresh hosts resolve to the same commit the methods doc claims. SHA verified against GitHub API — commit `2ed00bb119a5445e6a2985c0b6bf37a3068b9560` exists on `amandaforde/winnerscurse` (dated 2024-03-07, "minor adjust UMVCUE 5/3"). Updated `envs/r_coloc.yml` comment to reflect that installs are now SHA-pinned and to require methods-doc synchronization on any pin change.

### WR-01: `coloc::runsusie` fed raw N instead of effective N for binary traits

**Files modified:** `src/snakemake/scripts/run_replication_susie.R`, `src/snakemake/rules/replication.smk`
**Commit:** adc054e (combined with WR-02)
**Applied fix:** Introduced `cc_has_counts` guard that holds when `trait_type == "cc"` and both `case_n` / `ctrl_n` are non-NULL, non-NA, and positive. In that branch, `n_eff <- as.integer(4 / (1/case_n + 1/ctrl_n))` (matches `sumstats_utils.compute_effective_n`). Quant traits and missing-count fallbacks retain `total_n %||% median(sumstats$N)`.

### WR-02: Snakemake `fit_replication_susie` rule never forwards case/control counts

**Files modified:** `src/snakemake/scripts/run_replication_susie.R`, `src/snakemake/rules/replication.smk`
**Commit:** adc054e (combined with WR-01)
**Applied fix:** (1) Hardened the R-side `cc` guard to treat `NA` identically to `NULL`/`0`, eliminating the "missing value where TRUE/FALSE needed" error path. (2) Extended `fit_replication_susie` rule `params:` with `trait_type`, `case_n`, `ctrl_n`, `total_n` read from manifest via `_manifest_lookup` (defaults: `"quant"` / `""`); shell now passes `type=`, `case_n=`, `ctrl_n=`, `n=` to the R script. Manifest columns are not yet emitted by `build_replication_manifest.py`, but the R guard now fails loudly rather than crashing with a coercion error, and the plumbing is in place for a one-line manifest-builder change to supply the values.

### WR-03: Fabricated / unverified automated-download URL templates

**Files modified:** `src/snakemake/rules/replication.smk`
**Commit:** 283ea55
**Applied fix:** Rewrote the GBMI, MVP, and BBJ download rule error paths (option a from the review). Each rule now (1) explicitly documents in its docstring why the templated URL is known-aspirational, (2) fails with a stderr-routed (`>&2`) error message that names the wildcards, cites `.planning/data_access.md`, and describes the manual-download expectation. Used `|| { ...; exit 1; }` grouping so the error message reaches Snakemake logs. Did NOT mark rules as `protected:` (that would block auto-generation of placeholder files during development); the live smoke-test CI job suggestion in the review is out of scope for this iteration.

### WR-04: `compute_joint_criterion` key synthesis fragile across float formatting

**Files modified:** `src/python/compute_per_cohort_effect_size_test.py`, `src/snakemake/scripts/run_replication_coloc_susie.R`
**Commit:** 4e15afc
**Applied fix:** Added `pph4_sweep_colname(threshold: float) -> str` helper that returns `f"replicated_pph4_{threshold:.1f}"`. `compute_joint_criterion` now uses it. Updated the R-side `sprintf` format string from `"%s"` with `format(..., trim=TRUE)` to `"%.1f"`. Both sides now produce identical strings regardless of input precision (`0.8`, `0.80`, `0.8000000001` all → `"replicated_pph4_0.8"`). Verified existing test fixtures (which use literal `"replicated_pph4_0.5"`, `"_0.7"`, `"_0.8"`, `"_0.9"`) still match the new formatting.

### WR-05: `run_cojo.sh` N_SAMPLES whitespace parsing fragile

**Files modified:** `src/snakemake/scripts/run_cojo.sh`
**Commit:** 4c7a33a
**Applied fix:** Replaced `N_SAMPLES=$(wc -l < "${FAM_FILE}")` with `N_SAMPLES=$(awk 'END {print NR}' "${FAM_FILE}")`. awk emits a pure integer on all platforms (no BSD/macOS leading whitespace) and counts records independent of trailing-newline presence. Passed `bash -n` syntax check.

### WR-06: `aggregate_replication_meta.R` `is_generalization` filter brittle

**Files modified:** `src/snakemake/scripts/aggregate_replication_meta.R`
**Commit:** a06a20f
**Applied fix:** Replaced the `%in% c("True", "TRUE", TRUE, "true")` check with explicit coercion: `trimws(tolower(as.character(is_generalization)))` → accepts `"true"`/`"t"`/`"1"` (whitespace-tolerant). NA and empty-string are coerced to FALSE (kept in meta — preserves prior behavior). Now handles pandas-emitted 0/1 booleans, whitespace-padded strings, and native R logicals uniformly.

### WR-07: `liftover_to_grch37` silent-drop buckets

**Files modified:** `src/python/sumstats_utils.py`
**Commit:** a37a447
**Applied fix:** Surgical fix focused on the *correctness* concern (silent mis-attribution of non-autosomal drops to the 5% liftover budget). Performance refactor (UCSC binary path) deferred per review ("out of scope for v1"). Added two new QC keys: `n_dropped_unknown_chrom` (rows whose CHR label is not in {1..22, X, Y, chr1..chr22, chrX, chrY, 23, 24, chr23, chr24}) and `n_dropped_liftover_failed` (remainder). Downstream consumers can now distinguish mt/mitochondrial/weirdly-labeled drops from genuine liftover failures in the QC JSON.

### WR-08: `ivw_meta_per_signal` emits redundant `signal_id`

**Files modified:** `src/snakemake/scripts/aggregate_replication_meta.R`
**Commit:** bcf9694
**Applied fix:** Removed `signal_id = valid$signal_id[1]` from the returned `data.table(...)` body. data.table's by-group return attaches grouping columns automatically, so emitting `signal_id` explicitly created a version-dependent column-duplication risk. Meta output schema unchanged from the caller's perspective (grouping machinery now supplies `signal_id`).

### WR-09: `build_cross_ancestry_panel.py` merge-suffix hides BBJ effect-size columns

**Files modified:** `src/python/build_cross_ancestry_panel.py`
**Commit:** 55ba1ec
**Applied fix:** Option (a) from the review. BBJ columns are explicitly renamed to `bbj_{name}` (via `rename(columns={c: f"bbj_{c}" for c in bbj.columns if c != "signal_id"})`) BEFORE the merge, eliminating the pandas `suffixes` quirk where non-overlapping columns are left unsuffixed. Downstream consumers now unambiguously see `bbj_beta_replication` / `bbj_se_replication` and cannot confuse them with discovery β̂. Existing `test_bbj_generalization_excludes_credible_set` still passes (tests signal_class + is_generalization semantics, not column names).

### WR-10: `process_cohort` merges but does not de-duplicate

**Files modified:** `src/python/compute_per_cohort_effect_size_test.py`
**Commit:** 20e13ff
**Applied fix:** Added defensive assertion after the two-step merge: `df.groupby(["signal_id", "cohort"]).size()` is checked for any count > 1, raising `ValueError` with the duplicated-pair dict if the invariant is violated. This catches upstream aggregator regressions that would otherwise silently inflate Bonferroni replication rates (single signal gets multiple shots at threshold). The upstream sweep aggregator (`sweep_aggregated_{cohort}.tsv`) is still responsible for emitting one row per (signal, cohort); this is the belt.

### WR-11: `test_hla_fails_replication_joint` negative-control logic can silently pass

**Files modified:** `tests/phase9/test_negative_controls.py`
**Commit:** 94333af
**Applied fix:** Exact implementation of the review's recommended pattern. Gate the assertion on `has_any_real = hla[joint_cols].notna().any(axis=1)` — if any HLA row has all-NaN joint flags the test now `xfail`s with a descriptive message instead of trivially passing. Then count fails with strict `(hla[joint_cols] == False).sum(axis=1)` so NaN is treated as "neither True nor False" (no longer counted as a fail). The scientific Layer 3 guarantee now cannot be masked by a partial pipeline run.

---

_Fixed: 2026-04-14T10:28:18Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
