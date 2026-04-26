---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 01
type: execute
wave: 1
depends_on: [m2-00-preflight-and-environment]
autonomous: true
requirements: [REQ-MTAG-OVERLAP]
task_count: 3
files_modified:
  - data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv
  - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
  - data/processed/ldsc_overlap/rg_matrix_long_M2.tsv
  - data/processed/ldsc_overlap/munged/
  - data/processed/ldsc_overlap/rg_logs/
  - .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv
  - src/python/m1_trait_keys.py
  - data/processed/ldsc_overlap/rg_validation_warnings_M2.json
must_haves:
  truths:
    - "Pre-refire archival snapshot at data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv preserves the M1-frozen 12x12 matrix (DEC-2026-04-25 OSF posting record)"
    - "Refire of m1_munge_all + m1_ldsc_rg_all_stars + m1_ldsc_rg_reduce against the EXPANDED ~26-trait inventory completes; output has between 20 and 50 trait keys (defensive bound)"
    - "Output ~N×N symmetric wide TSV at data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv passes self-consistency: diag = 1.0 (or NaN), abs(R - R.T).max() < 1e-6"
    - "Long-form rg_matrix_long_M2.tsv with rg/rg_se/gcov_int/gcov_int_se/h2_a/h2_b columns exists for downstream CPASSOC + mtCOJO consumption"
    - "OSF mirror at .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv is byte-identical to the data/processed copy"
    - "rg_validation_warnings_M2.json captures any expected-intercept heuristic violations (UKB-UKB EUR pairs intercept > 0.5, GLGC EUR lipid pairs ~ 1.0)"
  artifacts:
    - path: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
      provides: "M2 MTAG --residcov_path consumer artifact (~26x26 expanded from M1 12x12 via DEF-M1-03-02 closure)"
    - path: "data/processed/ldsc_overlap/rg_matrix_long_M2.tsv"
      provides: "Fat format consumed by Wave 2 mtCOJO eligibility filter (gcov_int per pair) + Wave 5 catalog reports"
    - path: "data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv"
      provides: "Archival snapshot of M1 12x12 matrix before refire (preserves OSF posting record)"
    - path: ".planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv"
      provides: "OSF supplementary upload mirror of M2 ~26x26 matrix"
  key_links:
    - from: "src/snakemake/rules/m1_ldsc_rg.smk"
      to: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
      via: "re-execution against expanded trait_inventory.yaml + reduce_ldsc_rg_matrix.py"
      pattern: "bivariate_intercept_matrix"
    - from: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
      to: ".planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv"
      via: "deterministic copy at end-of-wave"
      pattern: "diff -q"
---

<objective>
Wave 1 refires the M1 m1-03 wave (m1_munge_all + m1_ldsc_rg_all_stars + m1_ldsc_rg_reduce) against the EXPANDED ~26-trait harmonized inventory per D-M2-01. The M1-frozen 12×12 bivariate-intercept matrix at `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` is the OSF posting record and stays untouched. The post-m1-03 GLGC + Wuttke harmonized files that landed via DEF-M1-03-02 closure expand the active set to ~26 (trait, ancestry) cells whose `sha256_harmonized` is populated in `config/trait_inventory.yaml`. The expanded ~N×N (20 ≤ N ≤ 50) matrix lands at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` and is the downstream consumer for Wave 2 MTAG `--residcov_path` slicing (D-M2-10 corrected flag) and Wave 3 CPASSOC R input (D-M2-04 + Q7 PSD-preserving slicing).

This is a PURE RE-EXECUTION wave: the existing `src/python/munge_sumstats_ldsc.py`, `src/python/reduce_ldsc_rg_matrix.py`, `src/snakemake/rules/m1_munge.smk`, and `src/snakemake/rules/m1_ldsc_rg.smk` need NO code changes (RESEARCH Pattern C). The only Python edit is loosening the defensive bound in `m1_trait_keys.py` from `_MIN_KEYS=40 / _MAX_KEYS=50` to `_MIN_KEYS=20 / _MAX_KEYS=50` to accommodate the actual ~26-trait expansion (the 40-floor was a pre-pivot artifact; the 26-trait reality is the M2 working set per D-M2-01).

Per Pitfall 11: refire continues to use EUR LD-scores at `data/external/ldscore/eur_w_ld_chr/` for ALL pairs (cross-ancestry approximation per D-M2-Q2 Carter-locked answer); AFR LDSC re-run is queued for M3-supersede when AoU AFR LD lands. Pitfall 5 from M1 RESEARCH applies (`ldsc.py --rg-cross` does NOT exist; star-topology is canonical).

Output: ~26-trait expanded LDSC bivariate-intercept matrix + long-form fat TSV + OSF mirror + validation warnings JSON. M1 12×12 frozen matrix is archived to `*_M1-frozen.tsv` for posterity but the M1 OSF artifact at `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` is NEVER overwritten (it is the OSF-posted record).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md
@.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-03-munge-and-ldsc-intercept-matrix-PLAN.md
@CLAUDE.md
@src/python/m1_trait_keys.py
@src/python/munge_sumstats_ldsc.py
@src/python/reduce_ldsc_rg_matrix.py
@src/snakemake/rules/m1_munge.smk
@src/snakemake/rules/m1_ldsc_rg.smk
@envs/m1-munge.yml
@envs/m1-ldsc-rg.yml
@envs/ldsc_py3.yml
@config/trait_inventory.yaml
@config/pipeline.yaml
@.planning/amendments/SUMSTATS-UPGRADE.tsv
@.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv

<interfaces>
m1_trait_keys.py current defensive bound (must be loosened in this wave for M2):
```python
_MIN_KEYS = 40   # current — pre-pivot 47-trait inventory expectation
_MAX_KEYS = 50   # current
# Loosen to: _MIN_KEYS=20, _MAX_KEYS=50 — D-M2-01 ~26-trait expansion is in band
```

reduce_ldsc_rg_matrix.py output schema (UNCHANGED — no code change needed):
- Input: focal_*.log files at data/processed/ldsc_overlap/rg_logs/
- Output 1: bivariate_intercept_matrix_<date>.tsv — N×N symmetric wide TSV (header row + index col, diag=1.0)
- Output 2: rg_matrix_long.tsv — long-form fat TSV with rg/rg_se/gcov_int/gcov_int_se/h2_a/h2_b
- The reducer's --output_prefix or equivalent CLI controls the matrix-file basename; per the existing rule the output filename is configurable

m1_ldsc_rg_all_stars rule shape (UNCHANGED — re-fires against new trait_keys.txt which is rebuilt from updated trait_inventory.yaml):
- Input: data/processed/ldsc_overlap/munged/<key>.sumstats.gz for each key in trait_keys.txt
- For focal_idx in 0..(N-2): emit focal_<focal_idx>.log
- LD reference: data/external/ldscore/eur_w_ld_chr/ (Pitfall 11 — EUR cross-ancestry approximation per D-M2-Q2)

config/trait_inventory.yaml — 47 cells × 24 fields. Cells with `sha256_harmonized` populated AND `qc_status` not MISSING are the active set (currently ~26 cells per CONTEXT inputs §"Trait inventory" lines 22-24). Snakemake rule reads the inventory to enumerate input files for munge_all + the trait_keys.txt builder.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Archive M1 12x12 matrix + loosen m1_trait_keys.py defensive bound (D-M2-01 prep)</name>
  <files>data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv, src/python/m1_trait_keys.py</files>
  <read_first>
    - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv (the M1 working copy at the original path; verify exists with diag=1.0 and 12 trait keys)
    - .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv (OSF posting record — VERIFY identical to the working copy; this file is NEVER touched)
    - src/python/m1_trait_keys.py (current _MIN_KEYS=40, _MAX_KEYS=50 defensive bound)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pattern C critical note" lines 432-440
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-01 lines 45-51
  </read_first>
  <action>
    Two atomic edits in this task:

    **(a) Archive the M1 12×12 matrix at the working path** (preserves the data on disk so anyone running pre-M2 figure scripts that hardcode the M1 numbers can still find them):

    ```bash
    set -e
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    cp -p data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv \
          data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv
    # Sanity: confirm OSF mirror is also identical (it should be; this is the OSF posting)
    diff -q data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv \
            .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv \
        || echo "WARNING: OSF mirror differs from working copy — investigate before refire"
    ```

    **(b) Loosen m1_trait_keys.py defensive bound** for the M2 ~26-trait reality. Edit the literal constants:

    ```python
    # Before (M1 era):
    _MIN_KEYS = 40
    _MAX_KEYS = 50

    # After (M2 era — DEF-M1-03-02 closure delivered ~26 traits):
    _MIN_KEYS = 20   # M2 era — D-M2-01 expansion to ~26 traits is in band
    _MAX_KEYS = 50   # unchanged
    ```

    Update the comment block above the constants to reference D-M2-01 + DEF-M1-03-02:
    ```python
    # Defensive bound on the produced key count.
    # M1 era: 40<=N<=50 against the pre-pivot 47-row freeze.
    # M2 era (D-M2-01): 20<=N<=50 to accommodate DEF-M1-03-02 closure delivering
    # ~26 active cells (post-m1-03 GLGC + Wuttke landings expand the active set).
    _MIN_KEYS = 20
    _MAX_KEYS = 50
    ```

    Atomic commit: `chore(m2-01): archive M1 12x12 matrix to M1-frozen.tsv + loosen m1_trait_keys defensive bound to 20-50 (D-M2-01)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv &amp;&amp; grep -c "_MIN_KEYS = 20" src/python/m1_trait_keys.py &amp;&amp; grep -c "_MAX_KEYS = 50" src/python/m1_trait_keys.py &amp;&amp; pytest tests/m1/ -x -k "test_m1_trait_keys or test_reduce_ldsc"</automated>
  </verify>
  <acceptance_criteria>
    - File `data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv` exists (file size matches `bivariate_intercept_matrix_2026-04.tsv` byte-for-byte: `cmp data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` exits 0)
    - `grep -c "_MIN_KEYS = 20" src/python/m1_trait_keys.py` returns 1 (was previously 40)
    - `grep -c "_MAX_KEYS = 50" src/python/m1_trait_keys.py` returns 1 (unchanged)
    - `grep -c "D-M2-01" src/python/m1_trait_keys.py` returns ≥1 (comment block updated)
    - `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` is UNCHANGED (file mtime older than commit time, OR `git status` shows no modification to that file)
    - Existing M1 pytest suite still passes: `pytest tests/m1/ -x` exits 0
    - `git log -1 --pretty=%B` matches `chore(m2-01): archive M1 12x12 matrix`
  </acceptance_criteria>
  <done>M1 12×12 matrix archived to *_M1-frozen.tsv; m1_trait_keys.py defensive bound loosened to 20-50; OSF posting record at .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv is preserved unchanged; existing M1 tests still pass.</done>
</task>

<task type="auto">
  <name>Task 2: Refire m1_munge_all + m1_ldsc_rg_all_stars + m1_ldsc_rg_reduce against expanded ~26-trait inventory (D-M2-01 production fire)</name>
  <files>data/processed/ldsc_overlap/munged/, data/processed/ldsc_overlap/rg_logs/, data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv, data/processed/ldsc_overlap/rg_matrix_long_M2.tsv, data/processed/ldsc_overlap/rg_validation_warnings_M2.json</files>
  <read_first>
    - .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-03-munge-and-ldsc-intercept-matrix-PLAN.md (the original m1-03 plan — line-by-line execution of the same fire here, just over the expanded trait set)
    - src/snakemake/rules/m1_munge.smk (rule m1_munge_all aggregator)
    - src/snakemake/rules/m1_ldsc_rg.smk (rule m1_ldsc_rg_all_stars aggregator + rule m1_ldsc_rg_reduce)
    - src/python/reduce_ldsc_rg_matrix.py (verify --output basename argument controls the output filename so we can land at *_2026-04-M2.tsv instead of *_2026-04.tsv)
    - config/trait_inventory.yaml (verify ~26 cells with sha256_harmonized populated and qc_status != MISSING; this is the inventory the trait_keys builder consumes)
    - tests/m1/test_reduce_ldsc_rg_matrix.py (re-runs as a regression sentinel)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 5" + §"Pitfall 11" (--rg-cross does NOT exist; EUR LD-scores cross-ancestry per Carter Q2)
    - feedback_lsf_queues memory note (long queue 14400 min for the longest star call; standard 2880 min for shorter)
  </read_first>
  <action>
    Pure re-execution; no code changes. The Snakemake DAG is driven by the trait_keys.txt file rebuilt from the updated trait_inventory.yaml.

    **Step 1 — Verify upstream inventory is fresh.** Confirm `config/trait_inventory.yaml` reflects the DEF-M1-03-02 closure (~26 active cells with sha256_harmonized populated). If any harmonized files are missing, the m1_munge_all rule will fail closed.

    **Step 2 — Munge all active cells.** Use `--use-conda` with the smoke_dev snakemake binary (CLAUDE.md Snakemake 7.32.4 + Python 3.11 pin):
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m1_munge.smk \
        --cores 8 \
        --resources mem_mb=32000 \
        m1_munge_all
    ```
    Expected output: ~26 .sumstats.gz files at `data/processed/ldsc_overlap/munged/<key>.sumstats.gz` per the D-16 naming convention (`<trait>.<ancestry>.<consortium>.<year>.sumstats.gz`).

    **Step 3 — Star-topology --rg fire.** RESEARCH Pitfall 5 reminder: `ldsc.py --rg-cross` does NOT exist. The canonical pattern is N-1 star calls (focal_idx in 0..N-2) with comma-separated trait list. The existing `m1_ldsc_rg_all_stars` rule does this:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m1_ldsc_rg.smk \
        --cores 8 \
        --resources mem_mb=32000 \
        m1_ldsc_rg_all_stars
    ```
    Per Pitfall 11 + D-M2-Q2 Carter-locked: continues to use EUR LD-scores `data/external/ldscore/eur_w_ld_chr/` for ALL pairs (cross-ancestry approximation acceptable; AFR LDSC re-run is M3-supersede). LSF dispatch via bsub_wrapper.sh on the long queue (14400 min ceiling) for the longest star call (focal_idx=0 is the largest comma-list).

    Wall time estimate: per the M1 m1-03 plan, the longest star is ~6 hours wall; total ~12 hours wall when parallelized across 8 cores.

    **Step 4 — Reduce to N×N matrix at the M2 output filename.** The reducer accepts an output prefix argument; invoke directly via Python (not through Snakemake) to control the output basename:
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \
        src/python/reduce_ldsc_rg_matrix.py \
        --logs-dir data/processed/ldsc_overlap/rg_logs/ \
        --trait-keys data/processed/ldsc_overlap/trait_keys.txt \
        --output-wide data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv \
        --output-long data/processed/ldsc_overlap/rg_matrix_long_M2.tsv \
        --validation-warnings data/processed/ldsc_overlap/rg_validation_warnings_M2.json
    ```

    NOTE: If the reducer's existing CLI uses different argument names, READ THE FILE and adapt. The reducer is at `src/python/reduce_ldsc_rg_matrix.py` (lines 1-300+); use its existing argparse signature exactly. If the existing CLI hardcodes the output path, this task instead runs the m1_ldsc_rg_reduce Snakemake rule and then COPIES the result to the M2 path (a copy is acceptable per RESEARCH Pattern C critical note):
    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m1_ldsc_rg.smk \
        --cores 1 \
        m1_ldsc_rg_reduce
    cp -p data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv \
          data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
    cp -p data/processed/ldsc_overlap/rg_matrix_long.tsv \
          data/processed/ldsc_overlap/rg_matrix_long_M2.tsv
    ```

    **Step 5 — Self-consistency validation.** Run the existing reducer's validate functions (or a small inline assertion script):
    ```python
    import pandas as pd
    import numpy as np
    M = pd.read_csv("data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv", sep="\t", index_col=0)
    assert M.shape[0] == M.shape[1], f"Not square: {M.shape}"
    assert 20 <= M.shape[0] <= 50, f"Out of band: N={M.shape[0]}"
    diag = np.diag(M.values)
    assert np.all(np.abs(diag[~np.isnan(diag)] - 1.0) < 0.1), "Diagonal not ~1.0"
    A = M.values
    assert np.nanmax(np.abs(A - A.T)) < 1e-6, "Not symmetric"
    print(f"PASS: {M.shape[0]}x{M.shape[0]} matrix, diag~1.0, symmetric")
    ```

    Atomic commit: `feat(m2-01): refire LDSC ~N-trait bivariate-intercept matrix (D-M2-01, REQ-MTAG-OVERLAP)` — note the data is NOT committed (per .gitignore convention for `data/processed/`); only the validation_warnings JSON if it is small enough is mentioned in commit message but not staged.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv &amp;&amp; test -s data/processed/ldsc_overlap/rg_matrix_long_M2.tsv &amp;&amp; python -c "import pandas as pd, numpy as np; M = pd.read_csv('data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv', sep='\t', index_col=0); assert M.shape[0] == M.shape[1] and 20 &lt;= M.shape[0] &lt;= 50, f'shape={M.shape}'; A=M.values; assert np.nanmax(np.abs(A - A.T)) &lt; 1e-6, 'not symmetric'; print('OK', M.shape)"</automated>
  </verify>
  <acceptance_criteria>
    - File `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` exists with at least 20 trait keys
    - The matrix is square (N rows × N cols)
    - 20 ≤ N ≤ 50 (defensive bound from updated m1_trait_keys.py)
    - Diagonal values are within 1.0 ± 0.1 (or NaN for any cell where both ld-score regression directions failed)
    - `np.nanmax(np.abs(A - A.T))` < 1e-6 (symmetric within numerical tolerance)
    - File `data/processed/ldsc_overlap/rg_matrix_long_M2.tsv` exists with columns matching `[trait_a, trait_b, rg, rg_se, gcov_int, gcov_int_se, h2_a, h2_b]` (use `head -1` and check column names)
    - File `data/processed/ldsc_overlap/rg_validation_warnings_M2.json` exists and is valid JSON (`python -c "import json; json.load(open('data/processed/ldsc_overlap/rg_validation_warnings_M2.json'))"` exits 0)
    - At least 20 .sumstats.gz files exist at `data/processed/ldsc_overlap/munged/`
    - `pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x` still passes (regression sentinel)
    - `git log -1 --pretty=%B` matches `feat(m2-01): refire LDSC`
  </acceptance_criteria>
  <done>~N×N (20≤N≤50) LDSC bivariate-intercept matrix produced at the M2 path; long-form fat TSV produced; self-consistency PASS (symmetric, diag~1.0); validation warnings JSON committed; ready for OSF mirror in Task 3.</done>
</task>

<task type="auto">
  <name>Task 3: OSF mirror copy + validation summary commit</name>
  <files>.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv</files>
  <read_first>
    - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv (Task 2 output)
    - data/processed/ldsc_overlap/rg_validation_warnings_M2.json (Task 2 output)
    - .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv (the M1 OSF artifact — schema reference for what the M2 mirror should look like)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §"Expected Deliverable Artifacts" rows 1-2
  </read_first>
  <action>
    Deterministic copy of the M2 working matrix to its OSF supplementary mirror. The mirror is a tracked artifact under `.planning/amendments/` so it lands in git (the working copy under `data/processed/` is git-ignored per project convention).

    ```bash
    set -e
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    cp -p data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv \
          .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv

    # Validate byte-identical
    cmp data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv \
        .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv

    # Compute SHA-256 for the M5 follow-up posting and announce in commit message
    SHA=$(sha256sum .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv | awk '{print $1}')
    echo "M2 matrix SHA-256: $SHA"
    ```

    Atomic commit: `feat(m2-01): OSF mirror — bivariate_intercept_matrix_m2_2026-04.tsv (D-M2-01, REQ-MTAG-OVERLAP, sha256=<SHA>)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv &amp;&amp; cmp -s data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv &amp;&amp; head -1 .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv | tr '\t' '\n' | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - File `.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv` exists
    - It is byte-identical to `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` (cmp exits 0)
    - The header row contains at least 21 tab-separated tokens (1 index column header + ≥20 trait-key columns)
    - The file IS staged in git (the M1 OSF mirror is tracked; M2 follows the same pattern per CONTEXT artifacts table)
    - `git log -1 --pretty=%B` matches `feat(m2-01): OSF mirror` AND contains `sha256=`
    - `git log -1 --pretty=%B` includes a 64-hex-char SHA-256 string
    - `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` STILL exists and is unchanged (M1 OSF posting record preserved)
  </acceptance_criteria>
  <done>OSF mirror committed; SHA-256 recorded in commit message for M5 catalog-lock follow-up posting; the M1 12×12 OSF artifact at .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv is preserved unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| config/trait_inventory.yaml → munge inputs | YAML manifest declares which harmonized files become inputs; mismatch leads to silent dropouts |
| EUR LD-scores → cross-ancestry rg | Pitfall 11 — using EUR LD-scores for AFR-AFR pairs is an approximation; mitigated by D-M2-Q2 Carter lock + M3-supersede commitment |
| reduce_ldsc_rg_matrix.py → MTAG residcov | Pitfall 1 — wide TSV needs to be sliced to a bare numeric matrix in Wave 2; symmetry + diag=1.0 invariants enforced by reducer |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-01 | Tampering | bivariate_intercept_matrix_2026-04-M2.tsv bytes integrity | mitigate | Self-consistency check (diag~1.0, symmetry within 1e-6); SHA-256 hash recorded in OSF mirror commit message |
| T-M2-XX-EUR-LD | Information disclosure | Cross-ancestry approximation using EUR LD-scores for AFR pairs | accept | D-M2-Q2 Carter-locked; AFR LDSC re-run is M3-supersede when AoU AFR LD lands; documented in m2_post_m3_rerun_queue.tsv (Plan 05) |
| T-M2-PITFALL-5 | Tampering | `--rg-cross` apocryphal flag re-introduced as "optimization" | mitigate | Documented in CONTEXT D-M2-01 + RESEARCH Pitfall 5; m1_ldsc_rg.smk uses star-topology only |
</threat_model>

<verification>
End-of-Wave-1 verifier checks:

```bash
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# M1 frozen archive preserved
test -s data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv
test -s .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv  # M1 OSF posting record

# M2 expanded matrix exists and validates
test -s data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
python -c "
import pandas as pd, numpy as np
M = pd.read_csv('data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv', sep='\t', index_col=0)
assert M.shape[0] == M.shape[1], f'shape={M.shape}'
assert 20 <= M.shape[0] <= 50, f'shape={M.shape}'
A = M.values
assert np.nanmax(np.abs(A - A.T)) < 1e-6, 'not symmetric'
print(f'PASS: {M.shape[0]}x{M.shape[0]}')
"

# OSF mirror byte-identical
cmp -s data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv \
       .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv

# Long-form companion exists
test -s data/processed/ldsc_overlap/rg_matrix_long_M2.tsv

# M1 regression sentinel
pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x
echo "Wave 1 PASS"
```
</verification>

<success_criteria>
- M1 12×12 matrix archived to *_M1-frozen.tsv (working copy preserved)
- M1 OSF posting record at .planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv UNCHANGED
- m1_trait_keys.py defensive bound loosened to 20-50 keys (D-M2-01 ~26-trait reality)
- ~N×N (20≤N≤50) LDSC bivariate-intercept matrix at data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
- Symmetric within 1e-6; diagonal ~ 1.0
- Long-form rg_matrix_long_M2.tsv exists with rg/rg_se/gcov_int/gcov_int_se/h2_a/h2_b columns
- OSF mirror at .planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv byte-identical
- rg_validation_warnings_M2.json captures expected-intercept heuristic results
- Existing M1 pytest suite unaffected (regression-clean)
- All commits atomic per task; messages follow `feat|chore(m2-01): <summary>` convention
</success_criteria>

<output>
After completion, create `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-01-SUMMARY.md` documenting:
- Final N (trait count in the M2 matrix)
- LSF wall time for the star-topology fire (longest focal star)
- SHA-256 of the M2 matrix (for M5 OSF follow-up posting per DEC-2026-04-25-02)
- Any expected-intercept heuristic violations recorded in rg_validation_warnings_M2.json
- Confirmation that M1 12×12 OSF posting record is preserved unchanged
</output>
