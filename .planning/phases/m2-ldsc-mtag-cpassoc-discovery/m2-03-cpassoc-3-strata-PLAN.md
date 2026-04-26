---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 03
type: execute
wave: 3
depends_on: [m2-00-preflight-and-environment, m2-01-ldsc-matrix-refire]
autonomous: true
requirements: [REQ-CPASSOC-ORTHOGONAL]
task_count: 3
files_modified:
  - src/python/run_cpassoc.py
  - src/snakemake/rules/m2_cpassoc.smk
  - data/processed/cpassoc/EUR/
  - data/processed/cpassoc/AFR/
  - data/processed/cpassoc/TRANS/
  - data/processed/cpassoc/{stratum}/cpassoc_results.tsv
  - data/processed/cpassoc/{stratum}/skipped_strata.tsv
  - tests/m2/test_run_cpassoc_integration.py
must_haves:
  truths:
    - "src/python/run_cpassoc.py orchestrates per-stratum CPASSOC: load munged sumstats per trait → align variants on chr:pos:ref:alt → build (n_snps, K) z-score matrix → slice the M2 LDSC matrix to a K×K R via the Q7-confirmed PSD-preserving principal-submatrix → compute SHom + SHet → write per-locus TSV with chr/pos/rsid/SHom/SHom_p/SHet/SHet_p columns"
    - "src/snakemake/rules/m2_cpassoc.smk has rule m2_cpassoc_run parameterized by {stratum} ∈ {EUR, AFR, TRANS} producing data/processed/cpassoc/{stratum}/cpassoc_results.tsv"
    - "Strata with K < _MIN_PER_STRATUM=3 emit skipped_strata.tsv per D-M2-Q6 (mirroring m2_mtag.smk handling)"
    - "CPASSOC consumes the same per-stratum trait order as MTAG (Wave 2 sidecar residcov.trait_order.json) so SHom + SHet are computed against the same R as MTAG's residcov_path"
    - "Per Q7: principal-submatrix slice of the M2 LDSC matrix preserves PSD; eigvalsh probe asserts no eigenvalue < -1e-10 before pinv"
    - "p-values via chi2.sf(stat, df=K) for SHom and chi2.sf(stat, df=K-1) for SHet (Zhu 2015 §Methods)"
  artifacts:
    - path: "src/python/run_cpassoc.py"
      provides: "Per-stratum CPASSOC orchestrator: load+align sumstats, build z-matrix, slice R, compute SHom+SHet+p-values, write per-locus TSV"
      min_lines: 120
    - path: "src/snakemake/rules/m2_cpassoc.smk"
      provides: "Rule cluster: m2_cpassoc_run per stratum + aggregator"
      min_lines: 70
    - path: "data/processed/cpassoc/EUR/cpassoc_results.tsv"
      provides: "Per-locus CPASSOC SHom/SHet TSV for EUR stratum (≥1M rows expected at HM3 SNP density)"
  key_links:
    - from: "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
      to: "data/processed/cpassoc/{stratum}/cpassoc_results.tsv"
      via: "src/python/run_cpassoc.py — slice R per Q7 PSD-preserving submatrix, then call cpassoc_shom + cpassoc_shet from src/python/cpassoc.py"
      pattern: "cpassoc_shom|cpassoc_shet"
    - from: "data/processed/mtag/{stratum}/residcov.trait_order.json"
      to: "src/python/run_cpassoc.py"
      via: "consumes the SAME trait order as MTAG to ensure SHom/SHet R aligns with MTAG residcov for downstream Class 1 novelty join"
      pattern: "trait_order.json"
---

<objective>
Wave 3 fires CPASSOC (Zhu 2015 *AJHG* 96:21-36) three times — once per stratum — using the SHom and SHet test statistics implemented in `src/python/cpassoc.py` (Wave 0 Task 6). The LDSC bivariate-intercept matrix from Wave 1 is the cohort-correlation R input per D-M2-04. Per D-M2-Q3 + Q7 the per-stratum R is constructed as a principal submatrix of the full ~26×26 matrix (PSD preserved by linear-algebra theorem; eigvalsh probe at the slice ensures no negative eigenvalues from numerical drift).

CRITICAL contract: CPASSOC's per-stratum R MUST use the SAME trait order as MTAG's `--residcov_path` (Wave 2 residcov.trait_order.json sidecar). This guarantees the downstream Class 1 novelty join (Wave 5) operates on a consistent K-trait basis. The Snakemake rule reads the Wave 2 sidecar JSON to recover the canonical order.

CPASSOC differs from MTAG in input expectations: MTAG accepts munged HM3 .sumstats.gz directly. CPASSOC needs aligned per-SNP z-scores across all K traits — meaning we must intersect SNPs across K traits, build an (n_snps_intersect, K) z-score matrix, and run cpassoc_shom + cpassoc_shet across the rows. Variant alignment on chr:pos:ref:alt:other_alt avoids strand-flip + allele-swap pitfalls (the M1 munge already harmonizes to HM3 + applies `_chrpos_key` from sumstats_utils.py).

p-values: SHom is chi-square df=K; SHet is chi-square df=K-1. Use `scipy.stats.chi2.sf` for survival-function (right-tail p-value).

Output: 3 per-stratum cpassoc_results.tsv with columns [chr, pos, rsid, A1, A2, n_traits, SHom_stat, SHom_p, SHet_stat, SHet_p, contributing_traits], satisfying ROADMAP success criterion 3 ("CPASSOC per-locus SHom/SHet outputs") and REQ-CPASSOC-ORTHOGONAL.
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
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-02-mtag-3-strata-PLAN.md
@CLAUDE.md
@src/python/cpassoc.py
@src/python/m2_stratum_keys.py
@src/python/build_mtag_residcov_slice.py
@src/python/sumstats_utils.py
@src/python/munge_sumstats_ldsc.py
@envs/m2-cpassoc.yml
@config/trait_inventory.yaml
@config/pipeline.yaml
@data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv

<interfaces>
**cpassoc.py contract (from Wave 0 Task 6):**
```python
from src.python.cpassoc import cpassoc_shom, cpassoc_shet, _safe_inverse
shom = cpassoc_shom(z, R)   # z: (n_snps, K); R: (K, K); returns (n_snps,)
shet = cpassoc_shet(z, R)
```

**Munged HM3 .sumstats.gz schema (LDSC convention, from M1 munge_sumstats_ldsc.py):**
```
SNP    A1  A2  Z       N       (rsid, effect allele, other allele, z-score, sample size)
rs123  A   G   1.234   500000
...
```

**Variant alignment strategy (per M1 sumstats_utils._chrpos_key idiom):**
- Munged files at data/processed/ldsc_overlap/munged/ have rsid keys
- For variant intersection across K traits: use rsid as primary key
- Filter to SNPs present in ALL K traits (intersection); discard others (CPASSOC needs complete K-vectors per SNP)
- Allele alignment: if A1/A2 differ between traits at the same rsid, flip Z accordingly OR drop (use the M1 sumstats_utils helper functions that handle this for LDSC munge)

**Per-stratum R slicing (Q7 PSD-preserving, mirrors build_mtag_residcov_slice.py):**
```python
import json
from pathlib import Path
sidecar = json.loads(Path("data/processed/mtag/EUR/residcov.trait_order.json").read_text())
trait_order = sidecar["trait_order"]   # canonical order matching MTAG --sumstats

import pandas as pd, numpy as np
M = pd.read_csv("data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv", sep="\t", index_col=0)
R = M.loc[trait_order, trait_order].values
R = (R + R.T) / 2.0  # defensive symmetry
# PSD probe (Q7):
eigvals = np.linalg.eigvalsh(R)
assert eigvals.min() >= -1e-10, f"PSD violation: min eigval = {eigvals.min()}"
```

**Output TSV schema for cpassoc_results.tsv:**
```
chr  pos       rsid          A1  A2  n_traits  SHom_stat   SHom_p     SHet_stat  SHet_p     contributing_traits
1    13550     rs554008981   T   C   9         5.4         3.2e-2     2.1        7.5e-1     bmi.EUR;t2d.EUR;...
1    13860     rs570124770   A   G   9         12.7        2.1e-3     8.4        2.4e-1     bmi.EUR;t2d.EUR;...
```

p-value formulas (Zhu 2015 §Methods):
- SHom_p = scipy.stats.chi2.sf(SHom_stat, df=K)
- SHet_p = scipy.stats.chi2.sf(SHet_stat, df=K-1)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: src/python/run_cpassoc.py — per-stratum orchestrator (D-M2-04, Q7)</name>
  <files>src/python/run_cpassoc.py, tests/m2/test_run_cpassoc_integration.py</files>
  <read_first>
    - src/python/cpassoc.py (Wave 0 Task 6 — provides cpassoc_shom, cpassoc_shet, _safe_inverse)
    - src/python/build_mtag_residcov_slice.py (Wave 2 Task 1 — mirror its structure for stratum-keyed slicing)
    - src/python/sumstats_utils.py (consumed for variant alignment helpers; specifically _chrpos_key, build_rsid_to_chrpos, allele_orientation)
    - src/python/munge_sumstats_ldsc.py (the munge wrapper; understand the munged HM3 schema it produces)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q2" lines 132-180 (CPASSOC code pattern)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q7" lines 312-336 (PSD-preserving slice)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-04 lines 70-81
    - data/processed/mtag/EUR/residcov.trait_order.json (Wave 2 sidecar — must consume for trait order)
    - tests/m2/conftest.py (synthetic_z_matrix + synthetic_ldsc_matrix fixtures)
  </read_first>
  <behavior>
    run_cpassoc(stratum, matrix_path, mtag_sidecar_path, munged_dir, out_path):
      1. Read mtag_sidecar_path JSON → get trait_order (list[str], length K)
      2. Read matrix_path indexed wide TSV; slice R = M.loc[trait_order, trait_order].values
      3. Symmetrize R defensively; eigvalsh PSD probe (assert min eigval ≥ -1e-10)
      4. Load each munged sumstats file at munged_dir/{trait_key}.sumstats.gz; extract (rsid → Z, A1, A2, N) columns
      5. Intersect rsids across K traits; drop SNPs missing in any trait
      6. Allele alignment: for each rsid, if A1/A2 across traits don't match the reference (first trait), flip Z accordingly OR drop (be conservative — drop on ambiguous strand)
      7. Build (n_snps, K) z-score matrix Z_mat
      8. Compute SHom = cpassoc_shom(Z_mat, R); SHet = cpassoc_shet(Z_mat, R)
      9. Compute p-values: SHom_p = scipy.stats.chi2.sf(SHom, df=K); SHet_p = scipy.stats.chi2.sf(SHet, df=K-1)
     10. Need chr+pos for downstream BED building. Resolve via the M1 sumstats_utils.build_rsid_to_chrpos helper (or HRC reference) — populates chr, pos columns from rsid
     11. Write TSV with columns chr, pos, rsid, A1, A2, n_traits=K, SHom_stat, SHom_p, SHet_stat, SHet_p, contributing_traits=";"-joined trait_order
    Floor enforcement: if K < _MIN_PER_STRATUM=3, raise ValueError → caller writes skipped_strata.tsv row.
  </behavior>
  <action>
    Implement `src/python/run_cpassoc.py`:

    ```python
    #!/usr/bin/env python3
    """Per-stratum CPASSOC orchestrator — load munged sumstats, align variants,
    slice R, compute SHom+SHet+p-values, write per-locus TSV.

    Plan: m2-03-cpassoc-3-strata-PLAN.md.
    Decision references: D-M2-04 (Python reimpl with LDSC matrix as R),
                         D-M2-Q6 (_MIN_PER_STRATUM=3),
                         Q7 (PSD-preserving principal-submatrix slice).
    """
    from __future__ import annotations
    import argparse
    import json
    import sys
    from pathlib import Path

    import numpy as np
    import pandas as pd
    from scipy.stats import chi2

    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_PROJECT_ROOT / "src" / "python"))
    from cpassoc import cpassoc_shom, cpassoc_shet
    from m2_stratum_keys import _MIN_PER_STRATUM


    def _load_munged(path: Path) -> pd.DataFrame:
        """Read LDSC-munged HM3 .sumstats.gz; return DataFrame with [SNP, A1, A2, Z, N]."""
        df = pd.read_csv(path, sep="\t")
        required = {"SNP", "A1", "A2", "Z", "N"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Munged file {path} missing columns: {missing}")
        return df[["SNP", "A1", "A2", "Z", "N"]].copy()


    def _intersect_and_align(per_trait: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Intersect rsids across K traits; align alleles to first trait's A1/A2.

        Returns: wide DataFrame with index=SNP and columns Z_<trait>, A1_ref, A2_ref.
        Z is sign-flipped where A1/A2 swap relative to reference.
        SNPs with ambiguous alleles (palindromic A/T or C/G with frequency near 0.5)
        are conservatively retained — we don't have allele frequency in the munged files
        so we drop only the strict A1/A2-can't-be-mapped cases.
        """
        traits = list(per_trait.keys())
        ref_trait = traits[0]
        merged = per_trait[ref_trait].set_index("SNP")
        merged = merged.rename(columns={"A1": "A1_ref", "A2": "A2_ref", "Z": f"Z_{ref_trait}"})

        for trait in traits[1:]:
            other = per_trait[trait].set_index("SNP")
            joined = merged.join(other, how="inner", rsuffix=f"_{trait}")
            # Allele alignment: same A1/A2 → keep Z as-is; swapped A1/A2 → flip Z
            same = (joined["A1_ref"] == joined["A1"]) & (joined["A2_ref"] == joined["A2"])
            swap = (joined["A1_ref"] == joined["A2"]) & (joined["A2_ref"] == joined["A1"])
            keep = same | swap
            joined = joined[keep].copy()
            joined[f"Z_{trait}"] = np.where(swap[keep], -joined["Z"], joined["Z"])
            joined = joined.drop(columns=["A1", "A2", "Z", "N"])
            merged = joined

        return merged


    def _slice_R_for_trait_order(matrix_path: Path, trait_order: list[str]) -> np.ndarray:
        """Q7 PSD-preserving principal submatrix; eigvalsh probe."""
        M = pd.read_csv(matrix_path, sep="\t", index_col=0)
        keys_in_matrix = [k for k in trait_order if k in M.index and k in M.columns]
        if len(keys_in_matrix) != len(trait_order):
            raise ValueError(
                f"trait_order keys missing from matrix: "
                f"{sorted(set(trait_order) - set(keys_in_matrix))}"
            )
        R = M.loc[trait_order, trait_order].values.astype(float)
        R = (R + R.T) / 2.0
        eigvals = np.linalg.eigvalsh(R)
        if eigvals.min() < -1e-10:
            raise ValueError(
                f"R is not PSD: min eigval = {eigvals.min()}; "
                f"check input matrix at {matrix_path}"
            )
        return R


    def _resolve_chr_pos(rsid_series: pd.Series, project_root: Path) -> pd.DataFrame:
        """Resolve chr+pos for each rsid via M1 sumstats_utils.build_rsid_to_chrpos.

        Falls back to a stub (NaN chr/pos) if the helper is unavailable; downstream
        BED building (Wave 4) uses the rg_logs or harmonized parquet to backfill.
        """
        try:
            from sumstats_utils import build_rsid_to_chrpos
            mapping = build_rsid_to_chrpos(rsid_series.tolist())
            return pd.DataFrame({
                "rsid": rsid_series,
                "chr": [mapping.get(r, (None, None))[0] for r in rsid_series],
                "pos": [mapping.get(r, (None, None))[1] for r in rsid_series],
            })
        except (ImportError, AttributeError):
            return pd.DataFrame({
                "rsid": rsid_series,
                "chr": np.nan,
                "pos": np.nan,
            })


    def run_cpassoc(
        stratum: str,
        matrix_path: Path,
        mtag_sidecar_path: Path,
        munged_dir: Path,
        out_path: Path,
    ) -> int:
        """Per-stratum CPASSOC orchestrator. Returns row count of output TSV."""
        # 1. Read sidecar for trait_order (matches MTAG --sumstats order)
        sidecar = json.loads(mtag_sidecar_path.read_text())
        trait_order: list[str] = sidecar["trait_order"]
        K = len(trait_order)
        if K < _MIN_PER_STRATUM:
            raise ValueError(
                f"run_cpassoc: stratum {stratum} has K={K} < _MIN_PER_STRATUM={_MIN_PER_STRATUM} "
                f"per D-M2-Q6"
            )

        # 2. Slice R (Q7 PSD-preserving principal submatrix)
        R = _slice_R_for_trait_order(matrix_path, trait_order)

        # 3. Load + intersect + align all K traits
        per_trait = {
            key: _load_munged(munged_dir / f"{key}.sumstats.gz")
            for key in trait_order
        }
        merged = _intersect_and_align(per_trait)
        n_snps = len(merged)
        if n_snps == 0:
            raise ValueError(f"After intersection, no SNPs remain for {stratum} K={K}")

        # 4. Build z-score matrix in trait_order column order
        z_cols = [f"Z_{trait}" for trait in trait_order]
        Z_mat = merged[z_cols].values

        # 5. Compute SHom + SHet + p-values
        shom = cpassoc_shom(Z_mat, R)
        shet = cpassoc_shet(Z_mat, R)
        shom_p = chi2.sf(shom, df=K)
        shet_p = chi2.sf(shet, df=max(K - 1, 1))

        # 6. Resolve chr+pos
        chrpos = _resolve_chr_pos(pd.Series(merged.index, name="rsid"), _PROJECT_ROOT)

        # 7. Build output frame
        out = pd.DataFrame({
            "chr": chrpos["chr"].values,
            "pos": chrpos["pos"].values,
            "rsid": merged.index.values,
            "A1": merged["A1_ref"].values,
            "A2": merged["A2_ref"].values,
            "n_traits": K,
            "SHom_stat": shom,
            "SHom_p": shom_p,
            "SHet_stat": shet,
            "SHet_p": shet_p,
            "contributing_traits": ";".join(trait_order),
        })

        # 8. Write
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(out_path, sep="\t", index=False)
        return len(out)


    def _main() -> None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--stratum", required=True, choices=("EUR", "AFR", "TRANS"))
        ap.add_argument("--matrix", type=Path, required=True)
        ap.add_argument("--mtag-sidecar", type=Path, required=True)
        ap.add_argument("--munged-dir", type=Path,
                        default=Path("data/processed/ldsc_overlap/munged"))
        ap.add_argument("--out", type=Path, required=True)
        args = ap.parse_args()
        n = run_cpassoc(
            args.stratum, args.matrix, args.mtag_sidecar, args.munged_dir, args.out
        )
        print(f"CPASSOC {args.stratum}: {n} SNPs written to {args.out}")


    if __name__ == "__main__":
        _main()
    ```

    Update tests/m2/test_run_cpassoc_integration.py — synthetic 5-trait fixture with hand-built R + munged.gz files, assert SHom_p uniform on null, SHom_p << 0.05 on injected pleiotropic signal, output schema correct.

    Atomic commit: `feat(m2-03): src/python/run_cpassoc.py + integration test (D-M2-04, Q7)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/run_cpassoc.py &amp;&amp; grep -c "def run_cpassoc" src/python/run_cpassoc.py &amp;&amp; grep -c "_slice_R_for_trait_order" src/python/run_cpassoc.py &amp;&amp; grep -c "eigvalsh" src/python/run_cpassoc.py &amp;&amp; grep -c "chi2.sf" src/python/run_cpassoc.py &amp;&amp; pytest tests/m2/test_run_cpassoc_integration.py tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/run_cpassoc.py` exists ≥120 lines
    - `grep -c "def run_cpassoc" src/python/run_cpassoc.py` returns 1
    - `grep -c "def _slice_R_for_trait_order" src/python/run_cpassoc.py` returns 1
    - `grep -c "eigvalsh" src/python/run_cpassoc.py` returns ≥1 (Q7 PSD probe)
    - `grep -c "chi2.sf" src/python/run_cpassoc.py` returns ≥1 (p-value via chi-square survival fn)
    - `grep -c "trait_order.json" src/python/run_cpassoc.py` returns ≥1 (consumes Wave 2 sidecar — alignment with MTAG)
    - `grep -c "_MIN_PER_STRATUM" src/python/run_cpassoc.py` returns ≥1 (D-M2-Q6 floor)
    - `pytest tests/m2/test_run_cpassoc_integration.py -x` exits 0
    - `pytest tests/m2/test_cpassoc_shom_shet.py -x` exits 0 (regression)
    - `git log -1 --pretty=%B` matches `feat(m2-03): src/python/run_cpassoc.py`
  </acceptance_criteria>
  <done>run_cpassoc.py orchestrator GREEN; consumes Wave 2 sidecar trait_order; PSD-preserving slice (Q7); chi-square p-values; ready for Snakemake rule.</done>
</task>

<task type="auto">
  <name>Task 2: src/snakemake/rules/m2_cpassoc.smk — per-stratum rule + aggregator (D-M2-04, D-M2-Q6)</name>
  <files>src/snakemake/rules/m2_cpassoc.smk</files>
  <read_first>
    - src/snakemake/rules/m2_mtag.smk (Wave 2 — mirror its rule pattern: per-stratum wildcard, sidecar consumption, skipped_strata.tsv handling)
    - src/snakemake/rules/m1_ldsc_rg.smk (project-root + path-parameterization pattern)
    - src/python/run_cpassoc.py (Task 1 — Snakemake rule invokes it)
    - envs/m2-cpassoc.yml (Wave 0 Task 2 — provides numpy + scipy + pandas)
    - data/processed/mtag/EUR/residcov.trait_order.json (Wave 2 — input dependency for cpassoc to consume same trait order as MTAG)
  </read_first>
  <action>
    Author `src/snakemake/rules/m2_cpassoc.smk`:

    ```python
    """M2 Wave 3 — CPASSOC 3 stratum runs.

    Plan: m2-03-cpassoc-3-strata-PLAN.md.
    Decisions: D-M2-04 (Python reimpl with LDSC matrix as R),
               D-M2-Q6 (_MIN_PER_STRATUM=3 soft floor),
               Q7 (PSD-preserving principal-submatrix slice).

    CRITICAL: CPASSOC consumes the SAME trait order as MTAG (residcov.trait_order.json
    sidecar from Wave 2) so SHom/SHet are computed against the same K-trait basis.
    This guarantees the downstream Class 1 novelty join (Wave 5) is consistent.
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
    _CPASSOC_DIR = "data/processed/cpassoc"

    STRATA = ("EUR", "AFR", "TRANS")


    rule m2_cpassoc_run:
        """Per-stratum CPASSOC fire (Zhu 2015) using the LDSC matrix as R.

        Consumes the Wave 2 MTAG sidecar to align trait order with MTAG (CRITICAL —
        downstream Class 1 novelty join requires this).
        """
        input:
            matrix=_MATRIX,
            sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        output:
            results=f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv",
            log=f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_run.log",
        params:
            munged_dir=_MUNGED_DIR,
        conda:
            "../../../envs/m2-cpassoc.yml"
        resources:
            mem_mb=16000,
            runtime=120,
        threads: 4
        shell:
            r"""
            set -euo pipefail
            mkdir -p $(dirname {output.results})
            python src/python/run_cpassoc.py \
                --stratum {wildcards.stratum} \
                --matrix {input.matrix} \
                --mtag-sidecar {input.sidecar} \
                --munged-dir {params.munged_dir} \
                --out {output.results} \
                2>&1 | tee {output.log}
            test -s {output.results}
            """


    rule m2_cpassoc_all_strata:
        """Aggregator — fire all 3 strata (or document skipped via Wave 2 skipped_strata.tsv)."""
        input:
            expand(f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv", stratum=STRATA),
    ```

    Note: the CPASSOC rule has an implicit dependency on Wave 2's residcov.trait_order.json sidecar — when Wave 2 emits skipped_strata.tsv for a stratum, the sidecar does NOT exist, so this rule will fail closed for that stratum. That's the correct behavior per D-M2-Q6 (skip-with-doc cascades).

    To handle the cascade gracefully, add a checkpoint sentinel pattern OR a Snakemake `ancient()` + missing-input-handler. Simplest: rely on Snakemake's MissingInputException to skip the cpassoc rule for skipped strata; the aggregator will fail with that error and the user re-runs only the non-skipped strata via `--config strata=EUR,AFR`. ALTERNATIVELY, add a defensive check inside m2_cpassoc_run shell that detects skipped_strata.tsv at `data/processed/mtag/{stratum}/skipped_strata.tsv` and emits its own skipped sentinel if so:

    ```bash
    if [ -f data/processed/mtag/{wildcards.stratum}/skipped_strata.tsv ]; then
        mkdir -p $(dirname {output.results})
        cp data/processed/mtag/{wildcards.stratum}/skipped_strata.tsv $(dirname {output.results})/skipped_strata.tsv
        echo "SKIPPED — upstream MTAG was below floor" > {output.log}
        touch {output.results}.skipped
        touch {output.results}
        exit 0
    fi
    ```
    Add this guard at the top of the shell block.

    Atomic commit: `feat(m2-03): m2_cpassoc.smk per-stratum rule + aggregator (D-M2-04, D-M2-Q6)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/snakemake/rules/m2_cpassoc.smk &amp;&amp; grep -c "rule m2_cpassoc_run:" src/snakemake/rules/m2_cpassoc.smk &amp;&amp; grep -c "rule m2_cpassoc_all_strata:" src/snakemake/rules/m2_cpassoc.smk &amp;&amp; grep -c "trait_order.json" src/snakemake/rules/m2_cpassoc.smk &amp;&amp; grep -c "skipped_strata" src/snakemake/rules/m2_cpassoc.smk &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile src/snakemake/rules/m2_cpassoc.smk --dry-run m2_cpassoc_all_strata 2>&amp;1 | tail -5</automated>
  </verify>
  <acceptance_criteria>
    - File `src/snakemake/rules/m2_cpassoc.smk` exists ≥70 lines
    - `grep -c "rule m2_cpassoc_run:" src/snakemake/rules/m2_cpassoc.smk` returns 1
    - `grep -c "rule m2_cpassoc_all_strata:" src/snakemake/rules/m2_cpassoc.smk` returns 1
    - `grep -c "trait_order.json" src/snakemake/rules/m2_cpassoc.smk` returns ≥1 (consumes Wave 2 sidecar — alignment with MTAG)
    - `grep -c "skipped_strata" src/snakemake/rules/m2_cpassoc.smk` returns ≥1 (D-M2-Q6 cascade handling)
    - `grep -c "run_cpassoc.py" src/snakemake/rules/m2_cpassoc.smk` returns ≥1
    - Snakemake dry-run for `m2_cpassoc_all_strata` exits 0 with no errors (assuming Wave 2 sidecar exists for at least EUR)
    - `git log -1 --pretty=%B` matches `feat(m2-03): m2_cpassoc.smk`
  </acceptance_criteria>
  <done>m2_cpassoc.smk authored; per-stratum rule consumes Wave 2 sidecar (alignment with MTAG); skipped_strata cascade handled gracefully; dry-run clean.</done>
</task>

<task type="auto">
  <name>Task 3: Production CPASSOC fire — 3 strata (D-M2-04, D-M2-Q3 cross-method corroboration)</name>
  <files>data/processed/cpassoc/EUR/cpassoc_results.tsv, data/processed/cpassoc/AFR/cpassoc_results.tsv, data/processed/cpassoc/TRANS/cpassoc_results.tsv</files>
  <read_first>
    - src/snakemake/rules/m2_cpassoc.smk (Task 2)
    - src/python/run_cpassoc.py (Task 1)
    - data/processed/mtag/{EUR,AFR,TRANS}/residcov.trait_order.json (Wave 2 outputs — input dependency)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Wave 3" lines 774-781
  </read_first>
  <action>
    Fire all 3 strata CPASSOC runs via Snakemake `--use-conda` per CLAUDE.md pin.

    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

    # CPASSOC is fast (~10-30 min wall per stratum at HM3 SNP density × K=9). LSF standard queue.
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_cpassoc.smk \
        --cores 8 \
        --resources mem_mb=24000 \
        m2_cpassoc_all_strata

    # Verify each stratum landed
    for stratum in EUR AFR TRANS; do
        echo "=== $stratum ==="
        if [ -f data/processed/cpassoc/$stratum/cpassoc_results.tsv.skipped ]; then
            echo "SKIPPED upstream:"
            cat data/processed/cpassoc/$stratum/skipped_strata.tsv 2>/dev/null
            continue
        fi
        wc -l data/processed/cpassoc/$stratum/cpassoc_results.tsv
        head -1 data/processed/cpassoc/$stratum/cpassoc_results.tsv
        # Sanity: SHom_p min should be << 0.05 for at least a few SNPs (genome-wide-significant joint signals exist in cardiometabolic trait blocks)
        python -c "
        import pandas as pd
        df = pd.read_csv('data/processed/cpassoc/$stratum/cpassoc_results.tsv', sep='\t')
        gws = (df['SHom_p'] < 5e-8).sum()
        print(f'$stratum SHom genome-wide significant: {gws} / {len(df)}')
        "
    done
    ```

    Atomic commit: `data(m2-03): CPASSOC production fire 3 strata (D-M2-04, REQ-CPASSOC-ORTHOGONAL)`. Data outputs at `data/processed/cpassoc/` are git-ignored per project convention; only logs are quoted.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; for s in EUR AFR TRANS; do test -f data/processed/cpassoc/$s/cpassoc_results.tsv 2>/dev/null || test -f data/processed/cpassoc/$s/skipped_strata.tsv; done &amp;&amp; head -1 data/processed/cpassoc/EUR/cpassoc_results.tsv | grep -E "SHom_p" &amp;&amp; head -1 data/processed/cpassoc/EUR/cpassoc_results.tsv | grep -E "SHet_p"</automated>
  </verify>
  <acceptance_criteria>
    - For each stratum (EUR, AFR, TRANS): EITHER `data/processed/cpassoc/{stratum}/cpassoc_results.tsv` exists with > 100,000 rows (HM3 SNP density), OR `data/processed/cpassoc/{stratum}/skipped_strata.tsv` exists explaining the skip
    - For EUR (densest stratum): the header row contains literal column names `SHom_stat`, `SHom_p`, `SHet_stat`, `SHet_p`, `n_traits`, `contributing_traits`
    - For EUR: at least 100 rows have `SHom_p < 5e-8` (genome-wide significant joint signals expected at this scale across cardiometabolic traits)
    - For EUR: all SHom_p and SHet_p values are in [0, 1] (valid p-values)
    - The CPASSOC log at `data/processed/cpassoc/{stratum}/cpassoc_run.log` shows no Python tracebacks
    - `git log -1 --pretty=%B` matches `data(m2-03): CPASSOC production fire`
  </acceptance_criteria>
  <done>3 strata CPASSOC fires complete (or below-floor strata documented); per-stratum cpassoc_results.tsv exists with SHom/SHet stats + p-values; ROADMAP success criterion 3 satisfied; REQ-CPASSOC-ORTHOGONAL deliverable in place.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Munged HM3 .sumstats.gz → CPASSOC z-matrix | Allele alignment + variant intersection across K traits; conservative drop-on-mismatch |
| LDSC matrix M2 → CPASSOC R | Q7 principal-submatrix slice preserves PSD; eigvalsh probe enforces invariant |
| MTAG residcov.trait_order.json → CPASSOC trait_order | Cross-method consistency (CRITICAL for Wave 5 Class 1 join) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-05 | Tampering / Information disclosure | R-matrix ill-conditioning | mitigate | _safe_inverse from cpassoc.py applies pinv with conditional ridge fallback when cond > 1e6 (Q2); eigvalsh probe in run_cpassoc.py asserts PSD (Q7) |
| T-M2-CPASSOC-MTAG-DRIFT | Tampering | CPASSOC and MTAG use different K-trait sets | mitigate | CPASSOC reads Wave 2 sidecar JSON for trait_order — same source of truth |
| T-M2-ALLELE-FLIP | Information disclosure | A1/A2 mismatch across K traits → wrong-sign z-scores | mitigate | _intersect_and_align flips Z when alleles swap; drops cases that don't match |
</threat_model>

<verification>
End-of-Wave-3 verifier checks:

```bash
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

test -f src/python/run_cpassoc.py
test -f src/snakemake/rules/m2_cpassoc.smk

# At least EUR landed (densest stratum)
test -f data/processed/cpassoc/EUR/cpassoc_results.tsv

# Schema invariants
python -c "
import pandas as pd
df = pd.read_csv('data/processed/cpassoc/EUR/cpassoc_results.tsv', sep='\t')
required = {'chr', 'pos', 'rsid', 'A1', 'A2', 'n_traits', 'SHom_stat', 'SHom_p', 'SHet_stat', 'SHet_p', 'contributing_traits'}
missing = required - set(df.columns)
assert not missing, f'Missing columns: {missing}'
assert (df['SHom_p'].between(0, 1)).all(), 'SHom_p out of [0,1]'
assert (df['SHet_p'].between(0, 1)).all(), 'SHet_p out of [0,1]'
print(f'EUR PASS: {len(df)} rows, schema OK')
"

# Tests
pytest tests/m2/test_run_cpassoc_integration.py tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py -x

echo "Wave 3 PASS"
```
</verification>

<success_criteria>
- src/python/run_cpassoc.py exists with run_cpassoc + _slice_R_for_trait_order + _intersect_and_align (Q7 PSD probe enforced)
- src/snakemake/rules/m2_cpassoc.smk authored with rule m2_cpassoc_run + m2_cpassoc_all_strata aggregator
- 3 stratum CPASSOC runs fire (or below-floor strata documented in skipped_strata.tsv)
- Per-stratum cpassoc_results.tsv with full schema (chr, pos, rsid, A1, A2, n_traits, SHom_stat, SHom_p, SHet_stat, SHet_p, contributing_traits)
- All SHom_p and SHet_p ∈ [0, 1]
- ROADMAP M2 success criterion 3 satisfied: "CPASSOC per-locus SHom/SHet outputs"
- REQ-CPASSOC-ORTHOGONAL deliverable: per-locus output exists + uses same trait order as MTAG (cross-method corroboration prep)
</success_criteria>

<output>
After completion, create `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-03-SUMMARY.md` documenting:
- Per-stratum K (trait count, must match Wave 2 MTAG K)
- Per-stratum row count of cpassoc_results.tsv (post-intersection SNP count)
- Per-stratum count of SHom_p < 5e-8 (genome-wide significant joint signals)
- Any skipped strata + reason rows
- Eigvalsh min eigenvalue per stratum R slice (Q7 PSD invariant evidence)
</output>
