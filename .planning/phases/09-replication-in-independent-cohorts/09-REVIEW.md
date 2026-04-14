---
phase: 09-replication-in-independent-cohorts
reviewed: 2026-04-13T23:59:00Z
depth: standard
files_reviewed: 40
files_reviewed_list:
  - config/replication_cohorts.yaml
  - docs/methods/phase9_replication.md
  - envs/gcta.yml
  - envs/r_coloc.yml
  - .gitignore
  - Snakefile
  - src/python/build_cojo_sensitivity_table.py
  - src/python/build_cross_ancestry_panel.py
  - src/python/build_master_replication_table.py
  - src/python/build_replication_holdout.py
  - src/python/build_replication_manifest.py
  - src/python/collect_replication_effect_sizes.py
  - src/python/compute_per_cohort_effect_size_test.py
  - src/python/harmonize_bbj.py
  - src/python/harmonize_finngen.py
  - src/python/harmonize_gbmi.py
  - src/python/harmonize_mvp.py
  - src/python/liftover.py
  - src/python/sumstats_utils.py
  - src/python/validate_replication_sumstats.py
  - src/snakemake/rules/replication.smk
  - src/snakemake/scripts/aggregate_replication_meta.R
  - src/snakemake/scripts/prepare_cojo_ma.py
  - src/snakemake/scripts/run_cojo.sh
  - src/snakemake/scripts/run_fiqt.R
  - src/snakemake/scripts/run_replication_coloc_susie.R
  - src/snakemake/scripts/run_replication_susie.R
  - tests/phase9/conftest.py
  - tests/phase9/fixtures/mock_disc.fit.rds
  - tests/phase9/fixtures/mock_rep.fit.rds
  - tests/phase9/__init__.py
  - tests/phase9/r/gen_coloc_fixtures.R
  - tests/phase9/r/test_coloc_replication.R
  - tests/phase9/r/test_fiqt.R
  - tests/phase9/test_bonferroni.py
  - tests/phase9/test_cohort_ingest.py
  - tests/phase9/test_cojo_sensitivity.py
  - tests/phase9/test_harmonize_bbj.py
  - tests/phase9/test_harmonize_finngen.py
  - tests/phase9/test_harmonize_gbmi.py
  - tests/phase9/test_harmonize_mvp.py
  - tests/phase9/test_master_table_schema.py
  - tests/phase9/test_meta_ivw.py
  - tests/phase9/test_negative_controls.py
  - tests/phase9/test_replication_manifest.py
  - tests/phase9/test_sumstats_utils.py
  - tests/phase9/test_trait_harmonization.py
findings:
  critical: 2
  warning: 11
  info: 7
  total: 20
status: issues_found
---

# Phase 9: Code Review Report

**Reviewed:** 2026-04-13T23:59:00Z
**Depth:** standard
**Files Reviewed:** 40 (tests + source + config)
**Status:** issues_found

## Summary

Phase 9 is a well-structured replication pipeline with broadly solid engineering: canonical sumstats schema is enforced at a single chokepoint (`validate_replication_sumstats`), liftover has an explicit 5% drop-rate guard, `coloc.susie` re-estimation is wrapped in defensive tryCatch for both `readRDS` and the coloc call, and the Bonferroni denominator correctly follows RESEARCH pitfall #4 (per-cohort, not global). Test coverage is strong on the statistical primitives (IVW math, same-direction, posthoc power, FIQT sign/shrinkage, LOCO) and on policy enforcement (Tier C exclusion, BBJ generalization scope, ancestry-matched routing).

Two classes of real issues need attention before a production run:

1. **Security — two zip-slip vulnerabilities.** `harmonize_bbj.extract_bbj_zip` and the identically-patterned Snakemake `extract_bbj_zip` rule use `ZipFile.extractall` on a TSV payload without any path-traversal guard. BBJ payloads are trusted as of 2026, but `extractall` with attacker-controllable archive entry names is a classic CVE pattern and should be replaced with an explicit per-entry safe extractor.

2. **Statistical correctness — winner's curse reproducibility gap AND binary-trait SuSiE N.** The `winnerscurse` GitHub dependency is installed at runtime with `upgrade="never"` but without a pinned commit SHA, so the *first* install on a fresh host is effectively `HEAD`. The methods doc (`phase9_replication.md`) and `envs/r_coloc.yml` comments both advertise SHA pinning to `2ed00bb`; the implementation does not honor either claim. Separately, `run_replication_susie.R` feeds raw median-N into `coloc::runsusie` for binary (case-control) traits instead of effective N — this understates precision at the SuSiE stage for `t2d`, `hypertension`, `stroke`, `asthma`.

The remaining warnings are mostly around fragile URL templates for the automated download rules (GBMI portal path is fabricated; MVP dbGaP FTP layout differs from the template) and defensive-programming gaps in error paths. Tests cover correctness more than shape, which is good, but the HLA negative-control test uses a non-strict comparison chain that could mask a real regression.

## Critical Issues

### CR-01: Zip-slip vulnerability in BBJ extractor

**File:** `src/python/harmonize_bbj.py:46-59` (and `src/snakemake/rules/replication.smk:152-173` which invokes it)

**Issue:** `extract_bbj_zip` calls `zf.extractall(out_dir)` on a hum0197-v3 payload. `ZipFile.extractall` does not defend against path-traversal entries — a zip containing an entry named `../../etc/cron.d/x` or an absolute path (on Windows, or via a crafted `zipfile.ZipInfo.filename`) will write outside `out_dir`. BBJ archives are trusted in this project, but this is a classic CVE pattern (CVE-2007-4559 family) and a linter- and audit-flagged anti-pattern. The docstring's "known filename pattern mitigation for T-09-10" does not actually mitigate zip-slip — it only filters which extracted entry is returned as the payload; all entries are extracted regardless.

**Fix:**
```python
import os

def extract_bbj_zip(zip_path: Path, out_dir: Path) -> Path:
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        candidates = [
            n for n in zf.namelist()
            if n.lower().endswith((".tsv", ".txt")) and "readme" not in n.lower()
        ]
        if not candidates:
            raise ValueError(f"{zip_path}: no .tsv/.txt file found ...")
        for member in zf.namelist():
            # Resolve final path and verify it stays under out_dir (prevents zip-slip).
            target = (out_dir / member).resolve()
            if not str(target).startswith(str(out_dir) + os.sep) and target != out_dir:
                raise ValueError(
                    f"{zip_path}: refusing to extract {member!r} — path traversal detected"
                )
            zf.extract(member, out_dir)
        return out_dir / candidates[0]
```

### CR-02: `winnerscurse` GitHub dependency not pinned; methods doc overstates reproducibility

**File:** `src/snakemake/scripts/run_fiqt.R:27-36` + `docs/methods/phase9_replication.md:62` + `envs/r_coloc.yml:25-28`

**Issue:** `run_fiqt.R` lazy-installs `winnerscurse` via `remotes::install_github("amandaforde/winnerscurse", upgrade = "never", quiet = TRUE)` with **no commit SHA, no tag, no version** — first install on any fresh host resolves to `HEAD`. The methods doc explicitly claims "pinned to commit SHA `2ed00bb` for reproducibility" (line 62) and `envs/r_coloc.yml` documents "the pinned commit SHA is documented in docs/methods_fragment.md after first successful install (currently unpinned)." This is a reproducibility gap with a supply-chain component: a compromised upstream between two replication runs would silently change FIQT corrections without any pipeline trace. `upgrade = "never"` only prevents *subsequent* upgrades on the same host — it does nothing for fresh installs.

This is flagged as Critical rather than Warning because FIQT shrinkage is the central statistical correction reported in the manuscript (D-04a), and the claim-vs-implementation mismatch is a reviewer-visible integrity issue for a solo-author paper.

**Fix:**
```r
# Option A: pin to the SHA the methods doc already claims.
remotes::install_github(
  "amandaforde/winnerscurse",
  ref = "2ed00bb",           # must match docs/methods/phase9_replication.md:62
  upgrade = "never",
  quiet = TRUE
)

# Option B (preferred): move the install into envs/r_coloc.yml as a post-env
# Rscript -e '...' step and fail the env build if the SHA drifts, so the
# pipeline never runs against an unpinned copy. Then make run_fiqt.R a
# pure consumer (requireNamespace -> hard error with install instructions).
```

Additionally: verify the SHA `2ed00bb` actually contains `FDR_IQT`, and add a `packageVersion("winnerscurse")` or SHA print to the QC JSON that `run_fiqt.R` could emit, so each replication run captures its effective FIQT implementation.

## Warnings

### WR-01: `coloc::runsusie` fed raw N instead of effective N for binary traits

**File:** `src/snakemake/scripts/run_replication_susie.R:176-194`

**Issue:** For case-control traits the SuSiE-RSS input should use effective N = `4 / (1/N_case + 1/N_ctrl)` (this is precisely what `sumstats_utils.compute_effective_n` implements). The replication SuSiE fitter computes `n_eff <- total_n %||% as.integer(stats::median(sumstats$N, na.rm = TRUE))` unconditionally, then sets `D$N <- n_eff`. The only case-control-specific step is setting `D$s = case_n / (case_n + ctrl_n)`. For binary-trait replication fits this understates per-variant precision and biases downstream `coloc.susie` PP.H4 estimates — relevant for all four binary cardiometabolic traits (`t2d`, `hypertension`, `stroke`, `asthma`).

**Fix:**
```r
# When trait_type == "cc" and both counts are available, use effective N.
if (trait_type == "cc" && !is.null(case_n) && !is.null(ctrl_n) &&
    case_n > 0 && ctrl_n > 0) {
  n_eff <- as.integer(4 / (1 / case_n + 1 / ctrl_n))
} else {
  n_eff <- total_n %||% as.integer(stats::median(sumstats$N, na.rm = TRUE))
}
D$N <- n_eff
```
Also consider asserting that the CLI caller supplies `case_n`/`ctrl_n` for `type=cc` — currently the case-control branch errors only if both are NULL/0, but no caller in `replication.smk::fit_replication_susie` actually passes them (no `params.case_n`/`ctrl_n`), so this branch is reachable only through the fallback `n_eff` path.

### WR-02: Snakemake `fit_replication_susie` rule never forwards case/control counts

**File:** `src/snakemake/rules/replication.smk:340-363`

**Issue:** `fit_replication_susie` calls `run_replication_susie.R` with only `sumstats=`, `region=`, `ld_panel=`, `policy=`, `out=`. The R script expects `type=`, `case_n=`, `ctrl_n=`, `n=` and silently defaults `type="cc"` with NULL case/ctrl → hits the `stop("trait_type='cc' requires positive case_n and ctrl_n")` for every binary-trait signal, because `case_n == 0` evaluation on `NA_integer_` coerced from missing arg returns `NA`, and `is.null(case_n) || case_n == 0` is `FALSE || NA` = `NA`, which is then used as a logical scalar in `if()`. The `if` may error with "missing value where TRUE/FALSE needed" instead of the intended `stop()`.

**Fix:** (1) pass per-trait `case_n`/`ctrl_n` through the rule params via a config lookup, (2) harden the R-side guard to treat `NA` as missing:
```r
# In replication.smk
params:
    case_n = lambda wc: _case_n_for(wc.signal_id, wc.cohort),
    ctrl_n = lambda wc: _ctrl_n_for(wc.signal_id, wc.cohort),
    trait_type = lambda wc: "cc" if _trait_type(wc.signal_id) == "binary" else "quant",

# In run_replication_susie.R, guard NAs before comparison:
if (trait_type == "cc") {
  if (is.null(case_n) || is.null(ctrl_n) ||
      is.na(case_n) || is.na(ctrl_n) ||
      case_n == 0 || ctrl_n == 0) {
    stop("trait_type='cc' requires positive case_n and ctrl_n")
  }
  D$s <- case_n / (case_n + ctrl_n)
}
```

### WR-03: Fabricated / unverified automated-download URL templates

**File:** `src/snakemake/rules/replication.smk:108-150`

**Issue:**
- `download_gbmi` templates `{portal}/{trait}/all_ancestries.tsv.gz` — GBMI's official resource page does not serve files at `globalbiobankmeta.org/resources/{trait}/all_ancestries.tsv.gz`. Real GBMI flagship file names are like `GBMI_flagship_<endpoint>_<ancestry>_<release>.tsv.gz` with no `{trait}/all_ancestries` path. The rule will always 404 in practice and then fail with an error message pointing to manual download — good UX for a human operator but means the rule cannot actually materialize files autonomously.
- `download_mvp_phs001672` templates `{ftp_root}/phs001672.{pha_id}.txt.gz` — the real dbGaP file layout is `ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672.v12.p1/analyses/<AnalysisGroup>/<pha_id>/phs001672.<pha_id>.MULTI.txt.gz` (subdirectory by analysis group; filename includes `.MULTI`). Hard-coding the current pattern will 404.
- `download_bbj_hum0197_v3` hits `humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.{trait_code}.v1.zip` — NBDC in 2024-2026 requires a data-transfer-agreement for some hum0197 files; public v3 releases may still be behind a click-through.

These are not logic bugs (curl will fail loudly with `-fsSL`), but they indicate the automated-ingest story is more aspirational than real, and `data_access.md` (referenced by the error message) becomes the load-bearing component.

**Fix:** Either (a) add explicit manual-download fallback notes in the rule docstring with the exact URL and expected filename, (b) replace `curl` with a small Python downloader that performs the real directory traversal for dbGaP, or (c) mark these rules as `protected:` targets that must be hand-populated and the pipeline cannot auto-fetch. Additionally, compute URL correctness via a live smoke-test CI job that just `curl -I`s each expected file and asserts 200, so drift is caught at development time rather than at execution time.

### WR-04: `compute_joint_criterion` key synthesis fragile across float formatting

**File:** `src/python/compute_per_cohort_effect_size_test.py:91` and `src/snakemake/scripts/run_replication_coloc_susie.R:79`

**Issue:** Python synthesizes `f"replicated_pph4_{primary_threshold}"` while R synthesizes `sprintf("replicated_pph4_%s", format(pph4_thresholds, trim = TRUE))`. For the current thresholds `{0.5, 0.7, 0.8, 0.9}` these agree (`"0.5"`, `"0.8"`, ...). But if any future threshold is `0.80` or `0.75`, Python's `f"{0.80}"` → `"0.8"` and R's `format(0.80, trim=TRUE)` → `"0.8"` agree, while `0.75` vs `0.750` would also agree via Python float repr + R trim. However `0.95` passed as numeric `0.95` vs `as.numeric("0.95")` can yield `format(0.9499999999, trim=TRUE)` = `"0.95"` — usually fine, but a caller passing `7/10 - 0` or similar non-exact float could break the join on silence (missing column → `compute_joint_criterion` returns `False`, silently marking a true coloc success as "not replicated").

**Fix:** Centralize the sweep-name formatter so Python and R use the same canonical representation. Either:
```python
def pph4_sweep_colname(threshold: float) -> str:
    # Two-decimal string; matches R sprintf("%.2f", ...).
    return f"replicated_pph4_{threshold:.1f}"
```
And on the R side: `sprintf("replicated_pph4_%.1f", pph4_thresholds)`. Then both sides produce `"replicated_pph4_0.8"` deterministically regardless of input precision. Add an integration test that passes `0.80` and `0.8000000001` through both sides.

### WR-05: `run_cojo.sh` N_SAMPLES whitespace parsing fragile

**File:** `src/snakemake/scripts/run_cojo.sh:45-48`

**Issue:** `N_SAMPLES=$(wc -l < "${FAM_FILE}")`. On GNU coreutils (Linux), `wc -l <` emits pure integer, so `[ "${N_SAMPLES}" -lt 4000 ]` works. On macOS `wc -l < file` emits `       503` (leading whitespace) — `bash [ -lt ]` tolerates leading whitespace in a `"..."`-quoted variable via the arithmetic context but only when the value is a valid decimal after lstrip. Also, if the `.fam` file lacks a trailing newline, `wc -l` undercounts by 1. 1000 Genomes plink `.fam` files are always newline-terminated so the undercount risk is ≈ zero, but fragility remains.

**Fix:**
```bash
# Robust, newline-agnostic line count.
N_SAMPLES=$(awk 'END {print NR}' "${FAM_FILE}")
```
Or `grep -c '' "${FAM_FILE}"`.

### WR-06: `aggregate_replication_meta.R` `is_generalization` filter brittle

**File:** `src/snakemake/scripts/aggregate_replication_meta.R:83-87`

**Issue:** The exclusion filter
```r
df[!(is_generalization %in% c("True", "TRUE", TRUE, "true"))]
```
attempts to cover CSV roundtripping (`"True"`/`"TRUE"`) and native R logicals (`TRUE`). It misses `"true"` with surrounding whitespace, `1`/`"1"` (pandas sometimes emits booleans as 0/1), and the case where `is_generalization` is `NA` (the `%in%` will return `FALSE` for NA, so NA rows are kept — which is the *safe* default only if NA genuinely means "unknown, include"). The D-05c intent is stricter: NA should be treated as "not generalization" in the primary meta only if we can prove the row came from a cohort_ancestry-matched cohort.

**Fix:**
```r
if ("is_generalization" %in% names(df)) {
  # Coerce to logical safely — handles strings, 0/1, NA.
  df[, is_generalization := as.logical(
      ifelse(is.na(is_generalization), FALSE,
             tolower(as.character(is_generalization)) %in% c("true", "1", "t"))
  )]
  df <- df[is_generalization == FALSE]
}
```

### WR-07: `liftover_to_grch37` uses `df.apply(axis=1)` — scales poorly and obscures errors

**File:** `src/python/sumstats_utils.py:216-219`

**Issue:** `df.apply(lambda r: liftover_coordinates(...), axis=1)` invokes a Python function per row. For a FinnGen R12 file (~20M rows) this is ~hours of wall-time where a vectorized path via the UCSC liftOver binary (as `liftover.py::liftover_sumstats` already implements) would be minutes. It also swallows errors in individual rows by returning `None`, which gets caught by the subsequent `notna()` mask — legitimate `chr0` / `chrM` / `chrMT` entries silently drop without a typed error channel, and the 5% guard is the only signal.

Performance is out of scope for v1, but the silent-drop behavior is a correctness concern: a cohort that uses `chrMT` or `chr23` (X) naming convention could have non-liftover-failure drops that still count against the 5% budget and may invisibly misattribute the cause.

**Fix:** Bucket the failure reasons. Log per-row skip counts for (unknown chromosome, failed liftover, unmapped, multi-mapped) and include them in the QC dict. Consider calling the UCSC `liftOver` binary path for >100k rows.

### WR-08: `aggregate_replication_meta.R` `ivw_meta_per_signal` uses `.SD` `signal_id` incorrectly

**File:** `src/snakemake/scripts/aggregate_replication_meta.R:90-98`

**Issue:** The `by = .(signal_id, cohort_ancestry)` groups rows, so inside `ivw_meta_per_signal(.SD)`, the `.SD` data.table does **not** contain the grouping columns (`.SDcols` includes `signal_id` and `cohort_ancestry`, so it is present — good). But the function returns `signal_id = valid$signal_id[1]` which is redundant with the grouping key; data.table's grouped return already carries grouping cols. This can cause a "duplicated column `signal_id`" on rbind in newer data.table versions, or silently take one column and discard the other. Behavior is version-dependent.

**Fix:**
```r
ivw_meta_per_signal <- function(sub, min_cohorts = 2L) {
  # ... (unchanged guard) ...
  fit <- tryCatch(metafor::rma.uni(yi=valid$beta_replication,
                                   sei=valid$se_replication, method="FE"),
                  error = function(e) NULL)
  if (is.null(fit)) return(NULL)
  # Do NOT return grouping cols; data.table will attach them.
  data.table(
    meta_ancestry = valid$cohort_ancestry[1],
    beta_meta = as.numeric(fit$beta),
    se_meta = as.numeric(fit$se),
    p_meta = as.numeric(fit$pval),
    meta_n_cohorts_contributing = nrow(valid),
    meta_cohorts = paste(valid$cohort, collapse = ",")
  )
}
```

### WR-09: `build_cross_ancestry_panel.py` merge-suffix hides BBJ effect-size columns

**File:** `src/python/build_cross_ancestry_panel.py:66-68`

**Issue:**
```python
out = tier_ab_bbj.merge(
    bbj, on="signal_id", how="left", suffixes=("", "_bbj")
)
```
When `tier_ab_bbj` already carries columns like `beta_replication`, `se_replication` (it does, because the manifest is joined with cohort-level data upstream in assemble_master_table but not here — here it's pure manifest), only truly-overlapping columns get the `_bbj` suffix. For non-overlapping BBJ-specific columns (`beta_replication`, `se_replication`) they end up unsuffixed. This means the output's `beta_replication` column contains BBJ-EAS β̂, not the discovery β̂ — which the downstream generalization table consumer may not expect. The D-05c narrative in the methods doc does not actually disambiguate which β̂ ends up in which column in the generalization TSV.

**Fix:** Either (a) always suffix BBJ columns via explicit rename before merge:
```python
bbj_renamed = bbj.rename(columns={c: f"bbj_{c}" for c in bbj.columns if c != "signal_id"})
out = tier_ab_bbj.merge(bbj_renamed, on="signal_id", how="left")
```
or (b) document the column semantics in the `framing_note` column so downstream consumers know `beta_replication` is BBJ-EAS. Add a schema test analogous to `test_master_table_schema_complete` that pins the exact column names in the generalization TSV.

### WR-10: `compute_per_cohort_effect_size_test.process_cohort` merges but does not de-duplicate

**File:** `src/python/compute_per_cohort_effect_size_test.py:116-119`

**Issue:** The merge
```python
df = effect_df.merge(fiqt_df, on="signal_id", how="left") \
              .merge(coloc_df, on=["signal_id", "cohort"], how="left")
```
assumes `coloc_df` has at most one row per `(signal_id, cohort)` pair. If upstream aggregation produces duplicates (e.g., multiple credible-set pairs per signal from `coloc.susie`), the merge cross-joins and the subsequent `n_in_cohort = df["signal_id"].nunique()` and `p_replication < alpha_bonf` are applied to a bloated frame — the Bonferroni threshold itself uses `.nunique()` (defensive) but the final p-test runs on every row, so a single signal with 3 coloc pairs gets 3 shots at the Bonferroni threshold (unintended multiple-comparison inflation).

**Fix:** Either deduplicate upstream (the coloc aggregator should emit one row per (signal_id, cohort) with the best pph4_best already applied to the sweep booleans — this appears to be the intent of `sweep_aggregated_{cohort}.tsv`), or add a defensive assertion:
```python
dup = df.groupby(["signal_id", "cohort"]).size()
if (dup > 1).any():
    raise ValueError(
        f"process_cohort: duplicated (signal_id, cohort) rows after merge: "
        f"{dup[dup > 1].to_dict()}"
    )
```

### WR-11: `test_hla_fails_replication_joint` negative-control logic can silently pass

**File:** `tests/phase9/test_negative_controls.py:43-47`

**Issue:**
```python
n_fail = (hla[joint_cols].fillna(False).astype(bool) == False).sum(axis=1)
assert (n_fail >= 3).mean() > 0.7
```
This replaces NaN with False then counts "False" values as failures. If `master_table.tsv` is populated but the `*_replicated_joint_0.8` columns are all NaN (e.g., a partial run), `n_fail` will equal the number of cohorts for every row → assertion trivially passes. The test is intended to catch real HLA replication but cannot distinguish "HLA genuinely failed" from "columns not populated". This weakens the scientific Layer 3 guarantee.

**Fix:** Require that at least one cohort produced a non-NaN joint flag per HLA row, otherwise `xfail`:
```python
has_any_real = hla[joint_cols].notna().any(axis=1)
if not has_any_real.all():
    pytest.xfail(
        f"{(~has_any_real).sum()} HLA rows have no populated joint column — "
        "cannot validate scientific Layer 3 negative control"
    )
n_fail = (hla[joint_cols] == False).sum(axis=1)  # NaN treated as neither T nor F
assert (n_fail >= 3).mean() > 0.7
```

## Info

### IN-01: `download_gbmi` rule catches curl failure with `|| (echo ... && exit 1)`

**File:** `src/snakemake/rules/replication.smk:119-126`

**Issue:** The `|| (... && exit 1)` pattern works but masks the original curl exit code (always becomes 1). Use `|| { ... ; exit $?; }` or just let `-f` fail loudly.

**Fix:** `"curl -fsSL '...' -o {output} || { echo 'ERROR: ...' >&2; exit 1; }"` — note the `>&2` so the error shows in Snakemake logs.

### IN-02: `validate_harmonized_sumstats` reads only 100 rows

**File:** `src/python/validate_replication_sumstats.py:25-37`

**Issue:** Schema validation uses `pd.read_csv(..., nrows=100)`. This catches column-presence errors but not empty-body files (a TSV with only a header row passes validation but has 0 data rows). For a paper-grade pipeline, an explicit minimum-row check would be valuable.

**Fix:** Add `min_rows` param (default 1000) and assert `len(df) >= min_rows` on a second streaming read, or check `os.path.getsize` exceeds a cohort-specific floor.

### IN-03: `build_replication_manifest.py` has hardcoded paths

**File:** `src/python/build_replication_manifest.py:46-47`

**Issue:** `PHASE1_FIT_GLOB` and `HARMONIZED_BASE` are module-level string constants, not read from config. REQ-12 in CLAUDE.md mandates no hardcoded paths. These are arguably structural layout conventions, but still.

**Fix:** Read from `config/pipeline.yaml::paths` or accept as CLI flags.

### IN-04: `harmonize_mvp.py` dbGaP schema — CHR type is string vs int inconsistency

**File:** `src/python/harmonize_mvp.py:125-127`

**Issue:** `out["CHR"] = df["Chr ID"].astype(str)` while `out["BP"] = df["Chr Position"].astype(int)` — CHR is string, BP is int. Canonical sumstats elsewhere (see `harmonize_finngen`, `harmonize_bbj`) rely on `liftover_to_grch37` which calls `str(r[chr_col])`, so this works. Inconsistent across harmonizers, though — FinnGen's CHR may be int after `rename` while MVP is always str. Pin a single convention.

**Fix:** Assert `df["CHR"] = df["CHR"].astype(str).str.replace("^chr", "", regex=True)` in `filter_palindromic_ambiguous` or `liftover_to_grch37` entry.

### IN-05: Unused import / dead code in `validate_replication_sumstats.py`

**File:** `src/python/validate_replication_sumstats.py:18`

**Issue:** `import sys` is imported but used only via `sys.exit(_main())` at the bottom — fine.  No actual finding; dropping placeholder.

(Retained as Info only to verify nothing stale; no change required.)

### IN-06: `liftover.py` `tempfile.TemporaryDirectory` + writing BED per-row with `df.iterrows()`

**File:** `src/python/liftover.py:111-120`

**Issue:** `for idx, row in df.iterrows():` then `fh.write(f"{row['_chr_bed']}\t{pos - 1}\t{pos}\t...")`. For ~20M-row sumstats, iterrows is O(hours). `liftover.py` is currently the "standalone script" fallback — the inline liftover path via `sumstats_utils.liftover_to_grch37` is what harmonizers actually use — so this is low-impact, but if `liftover.py` is ever re-enabled for a production run it will be slow.

**Fix:** Replace iterrows with vectorized string assembly:
```python
bed_df = pd.DataFrame({
    "chr": df["_chr_bed"],
    "start": df["POS"].astype(int) - 1,
    "end": df["POS"].astype(int),
    "name": df["_original_index"],
})
bed_df.to_csv(bed_in, sep="\t", header=False, index=False)
```

### IN-07: `build_cojo_sensitivity_table.py` trait fallback is silent

**File:** `src/python/build_cojo_sensitivity_table.py:116-119`

**Issue:** `trait = m.get("discovery_trait", m.get("trait", "trait"))` silently falls back to the literal string `"trait"` when the manifest has neither column. This produces `.jma.cojo` lookup paths like `{cohort}_trait_{stub}.jma.cojo`, which will always miss — the row is silently skipped at the `if not jma.exists(): continue` guard. A missing manifest schema is masked.

**Fix:**
```python
trait = m.get("discovery_trait") or m.get("trait")
if trait is None:
    raise ValueError(
        f"cojo manifest row missing discovery_trait/trait column for signal={sig}"
    )
```

---

_Reviewed: 2026-04-13T23:59:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
