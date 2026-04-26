---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 02
type: execute
wave: 2
depends_on: [m2-00-preflight-and-environment, m2-01-ldsc-matrix-refire]
autonomous: true
requirements: [REQ-MTAG-OVERLAP]
task_count: 4
files_modified:
  - src/python/build_mtag_residcov_slice.py
  - src/snakemake/rules/m2_mtag.smk
  - data/processed/mtag/EUR/residcov.txt
  - data/processed/mtag/EUR/residcov.trait_order.json
  - data/processed/mtag/AFR/residcov.txt
  - data/processed/mtag/AFR/residcov.trait_order.json
  - data/processed/mtag/TRANS/residcov.txt
  - data/processed/mtag/TRANS/residcov.trait_order.json
  - data/processed/mtag/EUR/
  - data/processed/mtag/AFR/
  - data/processed/mtag/TRANS/
  - data/processed/mtag/{stratum}/skipped_traits.tsv
  - data/processed/mtag/{stratum}/skipped_strata.tsv
  - tests/m2/test_build_mtag_residcov_slice.py
  - tests/m2/test_mtag_overlap_matrix_format.py
  - tests/m2/test_mtag_maxfdr_filter.py
must_haves:
  truths:
    - "src/python/build_mtag_residcov_slice.py emits a header-less, index-less, whitespace-delimited K×K matrix at data/processed/mtag/{stratum}/residcov.txt AND a sidecar JSON at data/processed/mtag/{stratum}/residcov.trait_order.json (Pitfall 2 + Pitfall 7 — D-M2-10 corrected flag)"
    - "Sidecar JSON's trait order list aligns 1:1 with the row/col order of residcov.txt; both align with the order MTAG sees in --sumstats"
    - "MTAG runs in 3 strata (EUR, AFR, TRANS) per D-M2-03 with --residcov_path pointing at the per-stratum residcov.txt slice (NOT a --overlap flag — D-M2-10 critical correction)"
    - "Each MTAG run produces data/processed/mtag/{stratum}/{trait}_mtag.txt for each trait in the per-stratum --sumstats list"
    - "Post-hoc max_FDR filter via mtag_maxFDR.py (per D-M2-Q1) drops rows with max_FDR ≥ 0.05 per Turley 2018 default; output at data/processed/mtag/{stratum}/{trait}_mtag_maxfdr_filtered.txt"
    - "Strata with fewer than _MIN_PER_STRATUM=3 traits emit a row to data/processed/mtag/{stratum}/skipped_strata.tsv (per D-M2-Q6) and skip the MTAG run"
    - "Per-trait skips within a stratum (e.g. CKDGen has no AFR-specific release) emit rows to data/processed/mtag/{stratum}/skipped_traits.tsv per D-M2-06"
  artifacts:
    - path: "src/python/build_mtag_residcov_slice.py"
      provides: "Slice the M2 LDSC matrix to per-stratum K-trait residual-covariance matrix in MTAG-compatible format (Pitfall 2 + 7)"
      min_lines: 80
    - path: "src/snakemake/rules/m2_mtag.smk"
      provides: "Rule cluster: m2_mtag_residcov_slice + m2_mtag_run + m2_mtag_maxfdr_filter parameterized by {stratum}"
      min_lines: 100
    - path: "data/processed/mtag/EUR/residcov.txt"
      provides: "EUR K×K residual-covariance slice in bare-numeric whitespace format (consumed by mtag.py --residcov_path)"
    - path: "data/processed/mtag/EUR/residcov.trait_order.json"
      provides: "Sidecar listing the canonical trait order matching the matrix rows/cols (Pitfall 7)"
    - path: "data/processed/mtag/EUR/{trait}_mtag.txt"
      provides: "Per-trait MTAG meta-analyzed sumstats (one file per trait in the EUR stratum)"
  key_links:
    - from: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
      to: "data/processed/mtag/{stratum}/residcov.txt"
      via: "build_mtag_residcov_slice.py — slice + reformat to bare-numeric"
      pattern: "build_mtag_residcov_slice|residcov.txt"
    - from: "data/processed/mtag/{stratum}/residcov.txt"
      to: "tools/mtag/mtag.py invocation"
      via: "shell: python tools/mtag/mtag.py --sumstats <comma-list> --residcov_path data/processed/mtag/{stratum}/residcov.txt --out data/processed/mtag/{stratum}/{trait}"
      pattern: "--residcov_path"
    - from: "data/processed/mtag/{stratum}/{trait}_mtag.txt"
      to: "data/processed/mtag/{stratum}/{trait}_mtag_maxfdr_filtered.txt"
      via: "tools/mtag/mtag_maxFDR.py post-hoc filter at threshold 0.05"
      pattern: "mtag_maxFDR|max_FDR"
---

<objective>
Wave 2 fires MTAG (Turley 2018) three times — once per stratum {EUR, AFR, TRANS} per D-M2-03 — using the M2 LDSC bivariate-intercept matrix from Wave 1 as the residual-covariance correction. The CRITICAL D-M2-10 correction is enforced: the MTAG CLI flag is **`--residcov_path`** NOT `--overlap` (RESEARCH Pitfall 1 — `--overlap` is colloquial shorthand; the actual flag is verified in tools/mtag/.git_clone_log from Wave 0 Task 3).

Three structural pieces:

1. **Matrix slice helper** (`src/python/build_mtag_residcov_slice.py`) reads the indexed wide TSV from Wave 1, filters rows/cols to the per-stratum trait keys (from `m2_stratum_keys.py` from Wave 0 Task 7), and emits TWO files: (a) `residcov.txt` — bare-numeric, header-less, index-less, whitespace-delimited K×K matrix that `np.loadtxt` parses cleanly (Pitfall 2); (b) `residcov.trait_order.json` — sidecar listing the canonical trait order so the Snakemake rule constructs the matching `--sumstats` comma-list with EXACTLY the same trait ordering (Pitfall 7 — silent mis-alignment if order diverges).

2. **MTAG rule cluster** (`src/snakemake/rules/m2_mtag.smk`) with three rules: `m2_mtag_residcov_slice` (per stratum, builds residcov.txt + sidecar), `m2_mtag_run` (per stratum, fires `python tools/mtag/mtag.py` with `--residcov_path` consuming the slice), `m2_mtag_maxfdr_filter` (per stratum, runs `mtag_maxFDR.py` post-hoc + filters rows with max_FDR ≥ 0.05 per D-M2-Q1).

3. **Production fire** of all 3 strata in parallel on LSF long queue. EUR has 9 traits (densest), AFR is expected 5-7 (per CONTEXT input note line 24), TRANS is expected 6-8. Per D-M2-Q6 strata with < 3 traits skip; per D-M2-06 individual missing trait cells within a stratum skip with `skipped_traits.tsv` rows. Universal DEFERRED guard pattern (Pattern A from M1) applied symmetrically.

Output: 3 stratum directories with residcov.txt + sidecar + per-trait MTAG output + per-trait max_FDR filtered output, satisfying ROADMAP success criterion 2 ("MTAG per-trait outputs with `max_FDR` column per Turley 2018") and REQ-MTAG-OVERLAP.
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
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-01-ldsc-matrix-refire-PLAN.md
@CLAUDE.md
@src/python/m2_stratum_keys.py
@src/python/m1_raw_glob.py
@src/python/reduce_ldsc_rg_matrix.py
@src/snakemake/rules/m1_ldsc_rg.smk
@envs/m2-mtag.yml
@tools/mtag/.git_clone_log
@config/trait_inventory.yaml
@config/pipeline.yaml
@data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv
@.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv

<interfaces>
**MTAG actual CLI flags (VERIFIED in tools/mtag/.git_clone_log from Wave 0 Task 3):**
```
python tools/mtag/mtag.py \
    --sumstats <comma-list of munged paths>  # ORDER MUST MATCH residcov rows/cols (Pitfall 7)
    --residcov_path data/processed/mtag/{stratum}/residcov.txt  # NOT --overlap (D-M2-10 corrected)
    --out data/processed/mtag/{stratum}/{stratum}              # output prefix; emits {prefix}_meta_results.txt + per-trait
    --p_sig 5e-8                                               # genome-wide significance threshold
    --use_beta_se                                              # if munged inputs have BETA/SE not Z
```

The matrix file format MTAG expects (per RESEARCH Q1 + Pitfall 2):
- Bare numeric K×K matrix
- NO header row
- NO row index
- Whitespace-delimited (space or tab — np.loadtxt is tolerant)
- Square symmetric; diag = 1.0
- Row/col order MUST match the order of traits in --sumstats comma list (Pitfall 7 — assertion-based check fires AFTER load, so silent mis-alignment is possible if order diverges)

**Reducer wide TSV input format (consumed by build_mtag_residcov_slice.py):**
```
\t<key1>\t<key2>\t...\t<keyN>           # header row of trait keys (with leading tab for index col)
<key1>\t1.0\t<gcov_int_12>\t...         # per-row index + values
<key2>\t<gcov_int_21>\t1.0\t...
...
```
Read via `pandas.read_csv(path, sep="\t", index_col=0)`; rows + cols indexed by trait key.

**m2_stratum_keys.py contract (from Wave 0 Task 7):**
```python
from src.python.m2_stratum_keys import keys_for_stratum, enforce_stratum_floor, STRATA, _MIN_PER_STRATUM
keys = keys_for_stratum(Path("config/trait_inventory.yaml"), "EUR")
# keys: list[str] — sorted trait keys for the stratum, length 0..9
# enforce_stratum_floor(keys, "EUR")  # raises if len < 3 (D-M2-Q6 floor)
```

**MTAG mtag_maxFDR.py post-hoc filter (per D-M2-Q1):**
- Bundled with MTAG at tools/mtag/mtag_maxFDR.py
- Reads MTAG meta-results table; computes per-locus max_FDR via Turley 2018 Methods §"maxFDR"
- Output adds a max_FDR column; M2 then filters rows to max_FDR < 0.05 in a separate downstream step

**LSF queue selection (per feedback_lsf_queues memory note):**
- mtag_run: long queue (14400 min ceiling); per stratum wall ~30-60 min for K=9
- mtag_residcov_slice: trivial (<1 min); standard or serial queue
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: src/python/build_mtag_residcov_slice.py + tests GREEN (Pitfall 2, Pitfall 7, D-M2-10)</name>
  <files>src/python/build_mtag_residcov_slice.py, tests/m2/test_build_mtag_residcov_slice.py, tests/m2/test_mtag_overlap_matrix_format.py</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q1" lines 105-130 (full slicing contract)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 2" lines 558-568
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 7" lines 627-635
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §research_surfaced_resolutions §D-M2-10 correction lines 232-241
    - src/python/m2_stratum_keys.py (consumed for stratum key lookup)
    - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv (Wave 1 output — input to this slice helper)
    - tests/m2/test_build_mtag_residcov_slice.py + tests/m2/test_mtag_overlap_matrix_format.py (RED stubs from Wave 0 Task 1)
  </read_first>
  <behavior>
    - slice_for_stratum(matrix_path, stratum, inventory_path, out_dir) does:
      1. Read indexed wide TSV at matrix_path via pandas
      2. Get list of trait keys for stratum via m2_stratum_keys.keys_for_stratum
      3. Filter rows AND columns of the matrix to the intersection of (matrix index) and (stratum keys)
      4. Sort both rows and columns by the same canonical lexicographic order (matches what --sumstats comma-list uses)
      5. Symmetrize defensively: R = (R + R.T) / 2.0
      6. Write residcov.txt at out_dir/residcov.txt — NO header, NO index, np.savetxt with delim=' '
      7. Write residcov.trait_order.json at out_dir/residcov.trait_order.json — JSON list of trait keys in row/col order
      8. Return (matrix, trait_order) tuple for testability
    - If a stratum trait key from m2_stratum_keys.keys_for_stratum does NOT appear in the matrix index (e.g. munged but rg log missing), it is dropped silently AND a warning is appended to a per-stratum log; this is the M1-pattern-A skip-with-doc behavior
    - If the resulting K < _MIN_PER_STRATUM=3, raise ValueError so caller (Snakemake rule) can emit skipped_strata.tsv row
    - residcov.txt MUST round-trip via np.loadtxt with shape (K, K) matching len(trait_order)
  </behavior>
  <action>
    Implement `src/python/build_mtag_residcov_slice.py`:

    ```python
    #!/usr/bin/env python3
    """Slice M2 LDSC bivariate-intercept matrix to per-stratum residcov for MTAG.

    Decision references: D-M2-10 correction (CRITICAL — flag is --residcov_path
    NOT --overlap), D-M2-04 (LDSC matrix as cohort-correlation R), D-M2-Q6
    (_MIN_PER_STRATUM = 3 floor).

    Pitfall 2: MTAG's _read_matrix(file_path) calls np.loadtxt(file_path)
    which fails on header rows or index columns. Output MUST be bare numeric.

    Pitfall 7: trait-key ordering between MTAG --sumstats and --residcov_path
    matrix MUST match. The sidecar residcov.trait_order.json fixes the
    canonical order for the Snakemake rule that builds --sumstats.
    """
    from __future__ import annotations
    import argparse
    import json
    import sys
    from pathlib import Path

    import numpy as np
    import pandas as pd

    # Add src/python to path so m2_stratum_keys is importable
    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_PROJECT_ROOT / "src" / "python"))
    from m2_stratum_keys import keys_for_stratum, _MIN_PER_STRATUM


    def slice_for_stratum(
        matrix_path: Path,
        stratum: str,
        inventory_path: Path,
        out_dir: Path,
    ) -> tuple[np.ndarray, list[str]]:
        """Slice the wide TSV to per-stratum K×K bare numeric matrix + sidecar JSON.

        Returns (matrix, trait_order). Raises ValueError if K < _MIN_PER_STRATUM.
        """
        # 1. Read indexed wide TSV
        M = pd.read_csv(matrix_path, sep="\t", index_col=0)

        # 2. Stratum keys from inventory (m2_stratum_keys helper)
        stratum_keys = keys_for_stratum(inventory_path, stratum)

        # 3. Intersect with matrix index — drop keys that lack a row in the matrix
        keys_in_matrix = [k for k in stratum_keys if k in M.index and k in M.columns]
        dropped = sorted(set(stratum_keys) - set(keys_in_matrix))

        # 4. Canonical sort (lexicographic) for determinism
        keys_in_matrix = sorted(keys_in_matrix)

        # 5. Floor enforcement (Carter D-M2-Q6)
        K = len(keys_in_matrix)
        if K < _MIN_PER_STRATUM:
            raise ValueError(
                f"build_mtag_residcov_slice: stratum {stratum} has K={K} keys "
                f"after filtering (dropped {len(dropped)}); below floor "
                f"_MIN_PER_STRATUM={_MIN_PER_STRATUM} per D-M2-Q6"
            )

        # 6. Slice rows + cols, symmetrize defensively
        R = M.loc[keys_in_matrix, keys_in_matrix].values.astype(float)
        R = (R + R.T) / 2.0  # defensive — reducer should already enforce symmetry

        # 7. Write bare numeric matrix (Pitfall 2 — no header, no index)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_matrix = out_dir / "residcov.txt"
        np.savetxt(out_matrix, R, fmt="%.10g", delimiter=" ")

        # 8. Write sidecar trait_order JSON (Pitfall 7)
        out_sidecar = out_dir / "residcov.trait_order.json"
        out_sidecar.write_text(json.dumps({
            "stratum": stratum,
            "trait_order": keys_in_matrix,
            "K": K,
            "matrix_path": str(matrix_path),
            "inventory_path": str(inventory_path),
            "dropped_for_missing_matrix_row": dropped,
        }, indent=2))

        return R, keys_in_matrix


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--matrix", type=Path, required=True,
                        help="Wide TSV from m1_ldsc_rg_reduce (M2 expanded matrix)")
        ap.add_argument("--stratum", required=True, choices=("EUR", "AFR", "TRANS"))
        ap.add_argument("--inventory", type=Path,
                        default=Path("config/trait_inventory.yaml"))
        ap.add_argument("--out-dir", type=Path, required=True)
        args = ap.parse_args()
        R, keys = slice_for_stratum(args.matrix, args.stratum, args.inventory, args.out_dir)
        print(f"Wrote {R.shape[0]}x{R.shape[1]} residcov for {args.stratum}: {keys}")


    if __name__ == "__main__":
        _main()
    ```

    Update tests/m2/test_build_mtag_residcov_slice.py from RED → GREEN:

    ```python
    import json
    import numpy as np
    import pytest
    from pathlib import Path
    from src.python.build_mtag_residcov_slice import slice_for_stratum

    def test_slice_preserves_trait_order(tmp_path, project_root):
        # Build a synthetic matrix TSV with 5 trait keys
        import pandas as pd
        keys = ["bmi.EUR.GIANT.2018", "t2d.EUR.DIAMANTE.2022", "sbp.EUR.Evangelou.2018",
                "stroke.EUR.GIGASTROKE.2022", "asthma.EUR.GBMI.2022"]
        M = np.eye(5)
        M[0, 1] = M[1, 0] = 0.2
        df = pd.DataFrame(M, index=keys, columns=keys)
        matrix_path = tmp_path / "matrix.tsv"
        df.to_csv(matrix_path, sep="\t")
        # Need m2_stratum_keys to actually return these keys; mock by skipping if it doesn't
        ...

    def test_residcov_round_trip_via_loadtxt(tmp_path):
        # Round-trip via np.loadtxt to mirror MTAG's _read_matrix behavior
        ...

    def test_floor_violation_raises(tmp_path):
        with pytest.raises(ValueError, match="_MIN_PER_STRATUM"):
            ...
    ```

    Update tests/m2/test_mtag_overlap_matrix_format.py — assert np.loadtxt round-trip and shape K×K matches len(trait_order.json["trait_order"]).

    Atomic commit: `feat(m2-02): build_mtag_residcov_slice.py + tests GREEN (D-M2-10 corrected --residcov_path, Pitfall 2 + 7)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/build_mtag_residcov_slice.py &amp;&amp; grep -c "residcov.txt" src/python/build_mtag_residcov_slice.py &amp;&amp; grep -c "trait_order.json" src/python/build_mtag_residcov_slice.py &amp;&amp; pytest tests/m2/test_build_mtag_residcov_slice.py tests/m2/test_mtag_overlap_matrix_format.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/build_mtag_residcov_slice.py` exists ≥80 lines
    - `grep -c "def slice_for_stratum" src/python/build_mtag_residcov_slice.py` returns 1
    - `grep -c "np.savetxt" src/python/build_mtag_residcov_slice.py` returns ≥1
    - `grep -c "residcov.txt" src/python/build_mtag_residcov_slice.py` returns ≥1
    - `grep -c "residcov.trait_order.json" src/python/build_mtag_residcov_slice.py` returns ≥1
    - `grep -c "_MIN_PER_STRATUM" src/python/build_mtag_residcov_slice.py` returns ≥1 (D-M2-Q6 floor)
    - `pytest tests/m2/test_build_mtag_residcov_slice.py -x` exits 0
    - `pytest tests/m2/test_mtag_overlap_matrix_format.py -x` exits 0
    - `git log -1 --pretty=%B` matches `feat(m2-02): build_mtag_residcov_slice.py`
  </acceptance_criteria>
  <done>build_mtag_residcov_slice.py module GREEN; emits bare-numeric K×K matrix at residcov.txt + sidecar JSON; D-M2-10 corrected flag invariants enforced; ready for Snakemake rule consumption.</done>
</task>

<task type="auto">
  <name>Task 2: src/snakemake/rules/m2_mtag.smk — three rules: residcov_slice, mtag_run, maxfdr_filter (D-M2-03, D-M2-07, D-M2-Q1, D-M2-10)</name>
  <files>src/snakemake/rules/m2_mtag.smk</files>
  <read_first>
    - src/snakemake/rules/m1_ldsc_rg.smk (Pattern C reference — project-root + path-parameterization + per-stratum rule shape)
    - src/snakemake/rules/m1_munge.smk (Pattern A reference — universal DEFERRED guard shell prelude)
    - src/python/build_mtag_residcov_slice.py (Task 1 output — Snakemake rule invokes it)
    - src/python/m2_stratum_keys.py (consumed for stratum trait-list construction)
    - tools/mtag/.git_clone_log (verify --residcov_path is the actual flag — Wave 0 Task 3)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Wave 2 — MTAG 3 stratum runs" lines 762-771
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 8" (Snakemake 7.32.4 + Python 3.11 pin)
    - envs/m2-mtag.yml (Wave 0 Task 2 — provides numpy<2 + scipy + pandas)
    - feedback_lsf_queues memory note (long queue 14400 min for the longest MTAG call)
  </read_first>
  <action>
    Author `src/snakemake/rules/m2_mtag.smk` with three rules per stratum:

    ```python
    """M2 Wave 2 — MTAG 3 stratum runs.

    Plan: m2-02-mtag-3-strata-PLAN.md.
    Decisions: D-M2-03 (3 strata: EUR-9, AFR-9, TRANS-9),
               D-M2-07 (max_FDR threshold 0.05),
               D-M2-Q1 (mtag_maxFDR.py post-hoc filter),
               D-M2-Q6 (_MIN_PER_STRATUM=3 soft floor),
               D-M2-10 corrected (flag is --residcov_path NOT --overlap).
    Pitfalls: Pitfall 1 (--overlap is colloquial only),
              Pitfall 2 (residcov.txt is bare numeric),
              Pitfall 5 (--rg-cross apocryphal — irrelevant for Wave 2),
              Pitfall 7 (trait-order alignment via residcov.trait_order.json sidecar).
    """
    from pathlib import Path
    import os
    import sys

    try:
        _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
    except NameError:
        _BASE = Path(os.getcwd())

    def _find_project_root(start: Path) -> Path:
        cur = start.resolve()
        for _ in range(6):
            if (cur / "config" / "pipeline.yaml").is_file():
                return cur
            if cur.parent == cur:
                break
            cur = cur.parent
        return start

    _PROJECT_ROOT = _find_project_root(_BASE)
    _SRC_PYTHON = _PROJECT_ROOT / "src" / "python"
    if str(_SRC_PYTHON) not in sys.path:
        sys.path.insert(0, str(_SRC_PYTHON))

    _MATRIX = "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
    _MUNGED_DIR = "data/processed/ldsc_overlap/munged"
    _MTAG_DIR = "data/processed/mtag"
    _MTAG_REPO = "tools/mtag"
    _INVENTORY = "config/trait_inventory.yaml"

    STRATA = ("EUR", "AFR", "TRANS")


    def _stratum_keys_or_skip(stratum):
        """Return list of stratum keys; emit skipped_strata.tsv row if below floor."""
        from m2_stratum_keys import keys_for_stratum, _MIN_PER_STRATUM
        keys = keys_for_stratum(Path(_INVENTORY), stratum)
        if len(keys) < _MIN_PER_STRATUM:
            skip_dir = Path(_MTAG_DIR) / stratum
            skip_dir.mkdir(parents=True, exist_ok=True)
            skip_path = skip_dir / "skipped_strata.tsv"
            with open(skip_path, "a") as fh:
                fh.write(f"{stratum}\t{len(keys)}\tbelow_floor_{_MIN_PER_STRATUM}\tD-M2-Q6\n")
            return []
        return keys


    rule m2_mtag_residcov_slice:
        """Slice M2 LDSC matrix to per-stratum K×K residual-covariance matrix.

        D-M2-10 corrected — output is bare numeric residcov.txt + sidecar JSON.
        Pitfall 2: NO header, NO index, whitespace-delimited.
        """
        input:
            matrix=_MATRIX,
            inventory=_INVENTORY,
        output:
            residcov=f"{_MTAG_DIR}/{{stratum}}/residcov.txt",
            sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        params:
            out_dir=f"{_MTAG_DIR}/{{stratum}}",
        conda:
            "../../../envs/m2-cpassoc.yml"   # numpy + pandas + pyyaml
        resources:
            mem_mb=2000,
            runtime=10,
        shell:
            r"""
            python src/python/build_mtag_residcov_slice.py \
                --matrix {input.matrix} \
                --stratum {wildcards.stratum} \
                --inventory {input.inventory} \
                --out-dir {params.out_dir}
            """


    rule m2_mtag_run:
        """Per-stratum MTAG fire (Turley 2018) with --residcov_path correction.

        D-M2-10 corrected: flag is --residcov_path (NOT --overlap).
        Pitfall 7: trait order in --sumstats MUST match residcov.txt rows/cols.
        D-M2-07: --p_sig 5e-8 (genome-wide significance threshold).
        Wall ~30-60 min on LSF long queue per stratum.
        """
        input:
            residcov=f"{_MTAG_DIR}/{{stratum}}/residcov.txt",
            sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        output:
            meta=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_meta_results.txt",
            log=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_run.log",
        params:
            out_prefix=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag",
            mtag_repo=_MTAG_REPO,
            munged_dir=_MUNGED_DIR,
        conda:
            "../../../envs/m2-mtag.yml"
        resources:
            mem_mb=8000,
            runtime=240,   # 4 hr wall ceiling; expected 30-60 min for K<=9
        threads: 4
        shell:
            r"""
            set -euo pipefail
            # Pitfall 7 — read sidecar for canonical trait order; build --sumstats list in same order
            TRAIT_ORDER=$(python -c "import json; print(','.join(json.load(open('{input.sidecar}'))['trait_order']))")
            SUMSTATS_LIST=$(python -c "
            import json
            ord_list = json.load(open('{input.sidecar}'))['trait_order']
            paths = ['{params.munged_dir}/' + k + '.sumstats.gz' for k in ord_list]
            print(','.join(paths))
            ")
            echo "Stratum {wildcards.stratum} trait order: $TRAIT_ORDER"
            echo "Sumstats list: $SUMSTATS_LIST"

            export PYTHONPATH={params.mtag_repo}:${{PYTHONPATH:-}}
            python {params.mtag_repo}/mtag.py \
                --sumstats "$SUMSTATS_LIST" \
                --residcov_path {input.residcov} \
                --out {params.out_prefix} \
                --p_sig 5e-8 \
                --use_beta_se \
                2>&1 | tee {output.log}

            test -s {output.meta}
            """


    rule m2_mtag_maxfdr_filter:
        """Post-hoc max_FDR filter via tools/mtag/mtag_maxFDR.py per D-M2-Q1.

        Drops rows with max_FDR >= 0.05 per Turley 2018 default (D-M2-07).
        """
        input:
            meta=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_meta_results.txt",
            sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        output:
            filtered=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt",
            log=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr.log",
        params:
            mtag_repo=_MTAG_REPO,
        conda:
            "../../../envs/m2-mtag.yml"
        resources:
            mem_mb=8000,
            runtime=120,
        shell:
            r"""
            set -euo pipefail
            export PYTHONPATH={params.mtag_repo}:${{PYTHONPATH:-}}
            python {params.mtag_repo}/mtag_maxFDR.py \
                --input {input.meta} \
                --output {output.filtered}.raw \
                2>&1 | tee {output.log}

            # Filter to max_FDR < 0.05 (D-M2-07)
            python -c "
            import pandas as pd
            df = pd.read_csv('{output.filtered}.raw', sep='\t')
            assert 'max_FDR' in df.columns, 'Expected max_FDR column from mtag_maxFDR.py'
            kept = df[df['max_FDR'] < 0.05]
            kept.to_csv('{output.filtered}', sep='\t', index=False)
            print(f'maxFDR filter: {{len(df)}} -> {{len(kept)}} rows (dropped {{len(df) - len(kept)}})')
            "
            test -f {output.filtered}
            """


    rule m2_mtag_all_strata:
        """Aggregator — fire all 3 strata."""
        input:
            expand(f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt", stratum=STRATA),
    ```

    Update tests/m2/test_mtag_maxfdr_filter.py from RED → GREEN — assert that running mtag_maxfdr_filter on a synthetic input drops rows with max_FDR ≥ 0.05.

    Atomic commit: `feat(m2-02): m2_mtag.smk — residcov_slice + mtag_run + maxfdr_filter (D-M2-03, D-M2-07, D-M2-Q1, D-M2-10)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/snakemake/rules/m2_mtag.smk &amp;&amp; grep -c "rule m2_mtag_residcov_slice:" src/snakemake/rules/m2_mtag.smk &amp;&amp; grep -c "rule m2_mtag_run:" src/snakemake/rules/m2_mtag.smk &amp;&amp; grep -c "rule m2_mtag_maxfdr_filter:" src/snakemake/rules/m2_mtag.smk &amp;&amp; grep -c -- "--residcov_path" src/snakemake/rules/m2_mtag.smk &amp;&amp; grep -c -- "--p_sig 5e-8" src/snakemake/rules/m2_mtag.smk &amp;&amp; pytest tests/m2/test_mtag_maxfdr_filter.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/snakemake/rules/m2_mtag.smk` exists ≥100 lines
    - `grep -c "rule m2_mtag_residcov_slice:" src/snakemake/rules/m2_mtag.smk` returns 1
    - `grep -c "rule m2_mtag_run:" src/snakemake/rules/m2_mtag.smk` returns 1
    - `grep -c "rule m2_mtag_maxfdr_filter:" src/snakemake/rules/m2_mtag.smk` returns 1
    - `grep -c "rule m2_mtag_all_strata:" src/snakemake/rules/m2_mtag.smk` returns 1
    - `grep -c -- "--residcov_path" src/snakemake/rules/m2_mtag.smk` returns ≥1 (D-M2-10 critical)
    - `grep -E -c -- '(^|[[:space:]])--overlap([[:space:]]|=|$)' src/snakemake/rules/m2_mtag.smk` returns 0 (NEVER use the colloquial flag — word-boundary anchor avoids false-positive collision with legitimate --no_overlap MTAG flag substring)
    - `grep -c -- "--p_sig 5e-8" src/snakemake/rules/m2_mtag.smk` returns ≥1 (D-M2-07)
    - `grep -c "mtag_maxFDR.py" src/snakemake/rules/m2_mtag.smk` returns ≥1 (D-M2-Q1)
    - `grep -c "0.05" src/snakemake/rules/m2_mtag.smk` returns ≥1 (max_FDR threshold per D-M2-07)
    - `pytest tests/m2/test_mtag_maxfdr_filter.py -x` exits 0
    - `git log -1 --pretty=%B` matches `feat(m2-02): m2_mtag.smk`
  </acceptance_criteria>
  <done>m2_mtag.smk authored with three rules, --residcov_path flag enforced (D-M2-10 corrected), --overlap NEVER appears, --p_sig 5e-8 hardcoded (D-M2-07), max_FDR < 0.05 post-hoc filter wired (D-M2-Q1).</done>
</task>

<task type="auto">
  <name>Task 3: MTAG dry-run smoke test for all 3 strata (D-M2-03)</name>
  <files>data/processed/mtag/EUR/residcov.txt, data/processed/mtag/EUR/residcov.trait_order.json, data/processed/mtag/AFR/residcov.txt, data/processed/mtag/AFR/residcov.trait_order.json, data/processed/mtag/TRANS/residcov.txt, data/processed/mtag/TRANS/residcov.trait_order.json</files>
  <read_first>
    - src/snakemake/rules/m2_mtag.smk (Task 2 output)
    - data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv (Wave 1 input)
    - tools/mtag/.git_clone_log (verify CLI surface area unchanged from Wave 0)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md §"MTAG end-to-end" row T-M2-03
  </read_first>
  <action>
    Smoke-test the 3-stratum DAG end-to-end via Snakemake dry-run + then fire the residcov_slice rule for all 3 strata. The full mtag_run is held back to Task 4 (production fire) so Carter can sanity-check the residcov slice files first.

    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

    # Dry-run all three strata to verify the DAG resolves cleanly
    for stratum in EUR AFR TRANS; do
        /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
            --use-conda \
            --snakefile src/snakemake/rules/m2_mtag.smk \
            --config stratum=$stratum \
            --dry-run \
            m2_mtag_all_strata 2>&1 | tail -10
    done

    # Fire just the residcov_slice rule for all 3 strata (cheap, ~10 sec each)
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_mtag.smk \
        --cores 2 \
        --resources mem_mb=4000 \
        $(for s in EUR AFR TRANS; do echo "data/processed/mtag/$s/residcov.txt"; done)

    # Verify each residcov.txt + sidecar
    for stratum in EUR AFR TRANS; do
        echo "=== Stratum $stratum ==="
        if [ ! -f data/processed/mtag/$stratum/residcov.txt ]; then
            echo "MISSING — likely below _MIN_PER_STRATUM=3 floor; check skipped_strata.tsv"
            continue
        fi
        # Verify it's bare numeric (np.loadtxt round-trip)
        python -c "
        import numpy as np, json
        from pathlib import Path
        R = np.loadtxt('data/processed/mtag/$stratum/residcov.txt')
        sidecar = json.loads(Path('data/processed/mtag/$stratum/residcov.trait_order.json').read_text())
        assert R.ndim == 2 and R.shape[0] == R.shape[1] == sidecar['K'], f'shape={R.shape} K={sidecar[\"K\"]}'
        assert R.shape[0] == len(sidecar['trait_order']), 'shape mismatch with trait_order'
        # Pitfall 2: bare numeric — first byte should be numeric character
        with open('data/processed/mtag/$stratum/residcov.txt', 'rb') as f:
            first = f.read(1)
        assert first in b'-0123456789. \t', f'first byte not numeric: {first!r}'
        print(f'$stratum K={sidecar[\"K\"]} traits={sidecar[\"trait_order\"][:3]}... PASS')
        "
    done
    ```

    Atomic commit: `feat(m2-02): residcov.txt + trait_order.json for 3 strata (D-M2-10 corrected, dry-run clean)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; for s in EUR AFR TRANS; do test -f data/processed/mtag/$s/residcov.txt 2>/dev/null || test -f data/processed/mtag/$s/skipped_strata.tsv; done &amp;&amp; python -c "import numpy as np, json; from pathlib import Path; sidecar = json.loads(Path('data/processed/mtag/EUR/residcov.trait_order.json').read_text()); R = np.loadtxt('data/processed/mtag/EUR/residcov.txt'); assert R.shape[0] == R.shape[1] == sidecar['K'], f'shape={R.shape} K={sidecar[\"K\"]}'; print('EUR OK', R.shape)"</automated>
  </verify>
  <acceptance_criteria>
    - For each stratum in (EUR, AFR, TRANS): EITHER `data/processed/mtag/{stratum}/residcov.txt` exists AND `data/processed/mtag/{stratum}/residcov.trait_order.json` exists, OR `data/processed/mtag/{stratum}/skipped_strata.tsv` exists with a row noting below-floor
    - For EUR: `np.loadtxt(residcov.txt)` returns 2D array; shape K×K matches sidecar `K`; K ≥ 3 (D-M2-Q6 floor)
    - For EUR: `residcov.txt` first byte is one of `-0123456789. \t` (Pitfall 2 — bare numeric, no header)
    - sidecar JSON contains `trait_order` (list of trait keys) AND `K` AND `stratum` AND `matrix_path`
    - Snakemake dry-run for `m2_mtag_all_strata` exits 0 with no errors
    - `git log -1 --pretty=%B` matches `feat(m2-02): residcov.txt`
  </acceptance_criteria>
  <done>residcov.txt + residcov.trait_order.json land for all 3 strata (or skipped_strata.tsv documents below-floor); MTAG DAG dry-run clean; Pitfall 2 + Pitfall 7 invariants verified.</done>
</task>

<task type="auto">
  <name>Task 4: Production MTAG fire — 3 strata + maxfdr filter (D-M2-03 + D-M2-07 + D-M2-Q1)</name>
  <files>data/processed/mtag/EUR/, data/processed/mtag/AFR/, data/processed/mtag/TRANS/</files>
  <read_first>
    - src/snakemake/rules/m2_mtag.smk (Task 2)
    - data/processed/mtag/{EUR,AFR,TRANS}/residcov.txt (Task 3 outputs)
    - tools/mtag/.git_clone_log (CLI flag audit)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Wave 2" lines 762-771 + §"Pitfall 6" (numpy<2 ABI requirement)
    - feedback_lsf_queues note (long queue 14400 min)
  </read_first>
  <action>
    Fire all 3 strata MTAG runs + maxfdr filter via Snakemake `--use-conda`. Per CLAUDE.md pin: use the smoke_dev snakemake binary. Per Pitfall 8 + project_python_311_pin memory: prepend the smoke_dev path; do NOT invoke from miniconda3 base.

    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

    # LSF dispatch via bsub_wrapper.sh on long queue (14400 min). Per-stratum wall ~30-60 min for K<=9.
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_mtag.smk \
        --cores 12 \
        --resources mem_mb=24000 \
        m2_mtag_all_strata

    # Verify each stratum landed
    for stratum in EUR AFR TRANS; do
        if [ -f data/processed/mtag/$stratum/skipped_strata.tsv ]; then
            echo "$stratum SKIPPED — below _MIN_PER_STRATUM floor:"
            cat data/processed/mtag/$stratum/skipped_strata.tsv
            continue
        fi
        echo "=== $stratum ==="
        ls data/processed/mtag/$stratum/${stratum}_mtag_meta_results.txt
        ls data/processed/mtag/$stratum/${stratum}_mtag_maxfdr_filtered.txt
        wc -l data/processed/mtag/$stratum/${stratum}_mtag_meta_results.txt
        wc -l data/processed/mtag/$stratum/${stratum}_mtag_maxfdr_filtered.txt
        head -1 data/processed/mtag/$stratum/${stratum}_mtag_maxfdr_filtered.txt | tr '\t' '\n' | grep -E "^max_FDR$"
    done
    ```

    If MTAG fails with `argparse: unrecognized arguments: --overlap`, the rule was incorrectly written — STOP and re-audit src/snakemake/rules/m2_mtag.smk for the literal --residcov_path flag (D-M2-10).

    If MTAG fails with `numpy.dtype size changed` or similar ABI break, revisit envs/m2-mtag.yml numpy pin (Pitfall 6 — numpy<2; m2-mtag.yml pins numpy=1.26.4 from Wave 0 Task 2).

    Atomic commit: `data(m2-02): MTAG production fire — 3 strata + max_FDR filter (D-M2-03, D-M2-07, D-M2-Q1)` — note the data outputs land at `data/processed/mtag/` which is git-ignored per project convention; only logs at `data/processed/mtag/{stratum}/{stratum}_mtag_run.log` are quoted in the commit body for audit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; for s in EUR AFR TRANS; do test -f data/processed/mtag/$s/${s}_mtag_meta_results.txt 2>/dev/null || test -f data/processed/mtag/$s/skipped_strata.tsv; done &amp;&amp; for s in EUR AFR TRANS; do if [ -f data/processed/mtag/$s/${s}_mtag_maxfdr_filtered.txt ]; then head -1 data/processed/mtag/$s/${s}_mtag_maxfdr_filtered.txt | grep -E "max_FDR" || true; fi; done &amp;&amp; echo "fire complete"</automated>
  </verify>
  <acceptance_criteria>
    - For each stratum in (EUR, AFR, TRANS): EITHER `data/processed/mtag/{stratum}/{stratum}_mtag_meta_results.txt` exists AND `data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt` exists, OR `data/processed/mtag/{stratum}/skipped_strata.tsv` exists explaining the skip
    - For at least EUR (densest stratum, expected K=9): the MTAG meta file exists AND has > 1000 data lines (genome-wide scale)
    - For EUR maxfdr_filtered.txt: header row contains literal column name `max_FDR`
    - For EUR maxfdr_filtered.txt: every data row has `max_FDR < 0.05` (D-M2-07 invariant)
    - The MTAG run logs at `data/processed/mtag/{stratum}/{stratum}_mtag_run.log` show no `unrecognized arguments` errors and no `argparse` errors
    - Logs confirm `--residcov_path` was the flag passed (NOT `--overlap`)
    - `git log -1 --pretty=%B` matches `data(m2-02): MTAG production fire`
  </acceptance_criteria>
  <done>3 strata MTAG fires complete (or below-floor strata documented); per-stratum max_FDR-filtered tables exist with max_FDR column; D-M2-03 + D-M2-07 + D-M2-Q1 + D-M2-10 corrections all enforced; ROADMAP success criterion 2 satisfied.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| residcov.txt → mtag.py _read_matrix | MTAG silently mis-aligns if trait order in --sumstats differs from matrix row/col order; sidecar JSON is the alignment contract |
| MTAG argparse → CLI flags | --overlap is a false friend (Pitfall 1); only --residcov_path exists; tools/mtag/.git_clone_log is the verification of record |
| numpy version → MTAG ABI | numpy 2.x breaks vendored MTAG dependencies; envs/m2-mtag.yml pins numpy=1.26.4 (Pitfall 6) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-02 | Tampering | Trait-order silent mis-alignment between --sumstats and --residcov_path | mitigate | Sidecar residcov.trait_order.json is single source of truth; Snakemake rule reads it to construct --sumstats list; pytest test_mtag_overlap_matrix_format.py asserts shape K×K matches len(trait_order) |
| T-M2-03 | Tampering | MTAG numpy 2.x ABI break | mitigate | envs/m2-mtag.yml pins numpy=1.26.4 (numpy<2 per Pitfall 6) |
| T-M2-04 | Tampering | Turley post-hoc max_FDR filter mis-applied | mitigate | Filter explicit at threshold 0.05 per D-M2-07; rule's Python filter step asserts `max_FDR < 0.05` invariant on output |
| T-M2-FLAG-NAME | Tampering | --overlap colloquial shorthand reintroduced | mitigate | Plan acceptance criteria assert `grep -c -- "--overlap" m2_mtag.smk` returns 0 (CRITICAL D-M2-10) |
</threat_model>

<verification>
End-of-Wave-2 verifier checks:

```bash
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# Module + rule files exist
test -f src/python/build_mtag_residcov_slice.py
test -f src/snakemake/rules/m2_mtag.smk

# CRITICAL D-M2-10 invariant — flag is --residcov_path NOT --overlap
grep -- "--residcov_path" src/snakemake/rules/m2_mtag.smk
! grep -E -- '(^|[[:space:]])--overlap([[:space:]]|=|$)' src/snakemake/rules/m2_mtag.smk  # must NOT match (word-boundary anchor avoids false-positive collision with legitimate --no_overlap)

# residcov slice + sidecar exist for at least one stratum (EUR is densest, expected to clear floor)
test -f data/processed/mtag/EUR/residcov.txt
test -f data/processed/mtag/EUR/residcov.trait_order.json

# Bare numeric matrix round-trip
python -c "
import numpy as np, json
from pathlib import Path
R = np.loadtxt('data/processed/mtag/EUR/residcov.txt')
assert R.shape[0] == R.shape[1] >= 3, f'shape={R.shape}'
sidecar = json.loads(Path('data/processed/mtag/EUR/residcov.trait_order.json').read_text())
assert R.shape[0] == sidecar['K'] == len(sidecar['trait_order'])
print(f'EUR PASS: K={R.shape[0]}')
"

# MTAG outputs land for at least one stratum
test -f data/processed/mtag/EUR/EUR_mtag_meta_results.txt
test -f data/processed/mtag/EUR/EUR_mtag_maxfdr_filtered.txt

# Tests
pytest tests/m2/test_build_mtag_residcov_slice.py tests/m2/test_mtag_overlap_matrix_format.py tests/m2/test_mtag_maxfdr_filter.py -x

echo "Wave 2 PASS"
```
</verification>

<success_criteria>
- src/python/build_mtag_residcov_slice.py + tests GREEN; D-M2-10 corrected flag enforced
- src/snakemake/rules/m2_mtag.smk authored with 3 stratum rules + aggregator
- Per-stratum residcov.txt + sidecar trait_order.json land for all eligible strata (those clearing _MIN_PER_STRATUM=3 floor)
- 3 MTAG runs fire (or skip with documented skipped_strata.tsv); per-trait *_mtag_meta_results.txt + *_mtag_maxfdr_filtered.txt land
- max_FDR < 0.05 invariant holds in filtered tables (D-M2-07)
- --residcov_path flag verified literal across all rules; --overlap NEVER appears (D-M2-10)
- ROADMAP M2 success criterion 2 satisfied: "MTAG per-trait outputs with `max_FDR` column per Turley 2018"
- All commits atomic per task; convention `feat|data(m2-02): <summary>`
</success_criteria>

<output>
After completion, create `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-02-SUMMARY.md` documenting:
- Per-stratum K (trait count after slice + floor enforcement)
- Per-stratum MTAG wall time
- Per-stratum row count of meta_results.txt vs maxfdr_filtered.txt (drop count by D-M2-07 filter)
- Any skipped strata + reason rows from skipped_strata.tsv
- Any --overlap argparse errors or numpy ABI errors (should be zero — Pitfalls 1 + 6 mitigated)
</output>
