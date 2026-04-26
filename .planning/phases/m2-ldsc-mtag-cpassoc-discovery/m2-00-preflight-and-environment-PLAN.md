---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 00
type: execute
wave: 0
depends_on: []
autonomous: false
requirements: [REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL, REQ-NOVELTY-CLASS-1, REQ-CATALOG-VERSION-LOCK, REQ-SNAKEMAKE-CI]
task_count: 9
files_modified:
  - tests/m2/conftest.py
  - tests/m2/fixtures/.gitkeep
  - tests/m2/test_cpassoc_shom_shet.py
  - tests/m2/test_safe_inverse.py
  - tests/m2/test_build_mtag_residcov_slice.py
  - tests/m2/test_mtag_overlap_matrix_format.py
  - tests/m2/test_mtag_maxfdr_filter.py
  - tests/m2/test_plink_clump_invocation.py
  - tests/m2/test_mtcojo_eligible_targets.py
  - tests/m2/test_mtcojo_extreme_overlap_filter.py
  - tests/m2/test_build_region_union.py
  - tests/m2/test_call_class1_novelty.py
  - tests/m2/test_catalog_lock_manifest_v_lock_M2.py
  - tests/m2/test_1000g_afr_plink_build.py
  - tests/m2/test_m2_stratum_keys.py
  - envs/m2-mtag.yml
  - envs/m2-cpassoc.yml
  - envs/m2-clumping.yml
  - envs/m2-mtcojo.yml
  - envs/m2-regions.yml
  - envs/m2-novelty.yml
  - tools/mtag/
  - data/reference/ldsc/1000G_AFR_Phase3_plink/
  - src/snakemake/rules/m2_reference.smk
  - data/catalogs/gwas-catalog-associations-full.zip
  - data/catalogs/catalog_lock_manifest.tsv
  - src/python/cpassoc.py
  - src/python/m2_stratum_keys.py
must_haves:
  truths:
    - "tests/m2/conftest.py + 13 stub test files exist; pytest collects all tests with 0 import errors"
    - "Six new conda env files exist at envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml; each pins numpy<2 if MTAG/LDSC dependency, plink=1.9 if clumping, gcta if mtcojo, bedtools=2.31 if regions"
    - "tools/mtag/ contains the JonJala/mtag.git clone with mtag.py present and --help runs cleanly listing --residcov_path"
    - "data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam} exist (66 files); built from data/raw/1kg/vcf/chr*.vcf.gz keeping data/raw/1kg/AFR.samples"
    - "data/catalogs/gwas-catalog-associations-full.zip exists; SHA-256 of the zip bytes is recorded in data/catalogs/catalog_lock_manifest.tsv as a new row keyed gwas_catalog.v_lock_M2"
    - "src/python/cpassoc.py exports cpassoc_shom(z, R), cpassoc_shet(z, R), _safe_inverse(R, ridge_floor=1e-4); pytest tests/m2/test_cpassoc_shom_shet.py + test_safe_inverse.py exit 0"
    - "src/python/m2_stratum_keys.py exports keys_for_stratum(inventory_path, stratum) with _MIN_PER_STRATUM = 3, STRATA = ('EUR', 'AFR', 'TRANS'); pytest tests/m2/test_m2_stratum_keys.py exits 0"
  artifacts:
    - path: "src/python/cpassoc.py"
      provides: "Zhu 2015 SHom + SHet test statistics + safe-inverse with conditional ridge fallback"
      min_lines: 60
    - path: "src/python/m2_stratum_keys.py"
      provides: "Deterministic enumeration of (stratum, trait_key) pairs with _MIN_PER_STRATUM=3 floor per D-M2-Q6"
      min_lines: 40
    - path: "envs/m2-mtag.yml"
      provides: "MTAG conda env (numpy<2, scipy, pandas, vendored mtag from tools/mtag/)"
    - path: "envs/m2-clumping.yml"
      provides: "PLINK 1.9 env (plink=1.9 from bioconda — Pitfall 5: PLINK 2.0 has no --clump)"
    - path: "data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.bed"
      provides: "1000G AFR PLINK bfile chr22 (smallest autosome — sentinel for 22-chr completion)"
    - path: "data/catalogs/catalog_lock_manifest.tsv"
      provides: "Manifest with new gwas_catalog.v_lock_M2 row including SHA-256, URL, last_modified, fetch_date"
  key_links:
    - from: "tools/mtag/mtag.py"
      to: "envs/m2-mtag.yml"
      via: "vendored path on PYTHONPATH inside the m2-mtag conda env"
      pattern: "mtag.py|JonJala/mtag"
    - from: "src/python/cpassoc.py"
      to: "tests/m2/test_cpassoc_shom_shet.py"
      via: "import + numerical reproduction of Zhu 2015 Table 1 example values"
      pattern: "cpassoc_shom|cpassoc_shet"
    - from: "data/reference/ldsc/1000G_AFR_Phase3_plink/"
      to: "data/raw/1kg/vcf/chr*.vcf.gz + data/raw/1kg/AFR.samples"
      via: "plink --vcf ... --keep AFR.samples --make-bed per chr"
      pattern: "1000G.AFR.QC.\\d+.bed"
---

<objective>
Wave 0 establishes EVERYTHING that any later M2 wave depends on but does not itself produce discovery output. Per RESEARCH §"Suggested Plan Decomposition" Wave 0 (~1 day), this plan delivers eight atomic deliverables in a single TDD pass: (1) test scaffolding for every M2 unit test family per VALIDATION.md Wave 0 Requirements; (2) six conda env files for the new rule families; (3) MTAG vendoring at tools/mtag/ per RESEARCH Pitfall 6 (`pip install mtag` does not exist); (4) BLOCKING: 1000G AFR PLINK bfile build per RESEARCH Pitfall 3 (only `.frq` files exist; no `.bed/.bim/.fam` for AFR); (5) GWAS Catalog v_lock_M2 fetch per D-M2-05 + Q5 (EBI URL https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip, hash the .zip bytes per Pitfall 10); (6) CPASSOC Python module per D-M2-04 with the Zhu 2015 SHom/SHet formulas and the safe-inverse Q2 conditioning policy; (7) m2_stratum_keys helper per D-M2-06 + D-M2-Q6 with _MIN_PER_STRATUM=3 floor; (8) MTAG residcov-slice tests REDDED so Wave 2 has a target.

Purpose: Every later wave imports from these foundations. The AFR PLINK build alone takes ~3 hrs LSF wall and must complete BEFORE Wave 4 clumping starts; firing it now de-risks the critical path. The GWAS Catalog fetch records last_modified at fetch time, freezing v_lock_M2 reproducibly. CPASSOC + m2_stratum_keys both have unit tests that exercise edge cases (near-singular R, missing strata) before any production wave fires.

Output: 13 unit test stubs (RED), 6 envs/, tools/mtag/ vendored, 22-chr 1000G AFR PLINK bfile tree, GWAS Catalog snapshot + lock manifest row, src/python/cpassoc.py + src/python/m2_stratum_keys.py with their tests GREEN.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md
@.planning/PROJECT.md
@.planning/DECISIONS.md
@.planning/REQUIREMENTS.md
@CLAUDE.md
@src/python/m1_raw_glob.py
@src/python/m1_trait_keys.py
@src/python/reduce_ldsc_rg_matrix.py
@src/snakemake/rules/m1_ldsc_rg.smk
@src/snakemake/rules/m1_munge.smk
@envs/m1-ldsc-rg.yml
@envs/m1-munge.yml
@envs/m1-harmonize.yml
@envs/plink.yml
@envs/gcta.yml
@config/trait_inventory.yaml
@data/catalogs/catalog_lock_manifest.tsv
@tests/m1/conftest.py

<interfaces>
M1 Pattern A — universal DEFERRED guard from src/python/m1_raw_glob.py:
```python
DEFERRED_SENTINEL = "__DEFERRED__"
def resolve_raw_for(source_tag: str, ancestry: str) -> str:
    """Returns path string OR DEFERRED_SENTINEL if upstream .deferred marker present."""
```

M1 Pattern B — m1_trait_keys.py defensive-bound enumeration:
```python
TOKEN_MAP = {"BMI": "bmi", "T2D": "t2d", "hypertension": "sbp", ...}
_MIN_KEYS = 40
_MAX_KEYS = 50
def build_keys(tsv_path: Path) -> list[str]: ...
```

reduce_ldsc_rg_matrix.py output schema (consumed by Wave 1 + Wave 2 slice helper):
```
trait_key_a, trait_key_b, ..., trait_key_N        # header row of trait keys
trait_key_a, 1.0, gcov_int_ab, ..., gcov_int_aN   # rows indexed by trait keys
```
Diag = 1.0; symmetric within 1e-6; PSD by construction (covariance matrix).

MTAG actual CLI flags (VERIFIED 2026-04-25, github.com/JonJala/mtag/blob/master/mtag.py):
- --residcov_path <PATH>   # Pre-computed residual covariance (Σ-hat). .npy or whitespace .txt
- --gencov_path <PATH>     # Pre-computed genetic covariance (Ω-hat)
- --no_overlap             # Boolean: zeros off-diagonal Σ-hat
- --p_sig <FLOAT>          # Default 5e-8
- --sumstats <COMMA_LIST>  # Comma-list of munged sumstats; ORDER MUST MATCH residcov rows/cols

Existing 1000G inputs verified on disk:
- data/raw/1kg/AFR.samples (504 sample IDs)
- data/raw/1kg/vcf/chr{1..22}.vcf.gz
- data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.{1..22}.{bed,bim,fam} (already exists)
- data/reference/ldsc/1000G_Phase3_frq_AFR/ (.frq ONLY; no .bed/.bim/.fam — Pitfall 3)

GWAS Catalog v_lock URL (verified 2026-04-25 via WebFetch):
URL: https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip
Size: 56 MB compressed (~500 MB unzipped TSV)
Last-Modified header: 2026-04-21 13:50 UTC at probe; check at fire time
SHA-256 to be computed on the .zip BYTES (NOT the unpacked TSV — Pitfall 10).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: pytest scaffolding for M2 (RED phase across 14 unit-test files)</name>
  <files>tests/m2/conftest.py, tests/m2/fixtures/.gitkeep, tests/m2/test_cpassoc_shom_shet.py, tests/m2/test_safe_inverse.py, tests/m2/test_build_mtag_residcov_slice.py, tests/m2/test_mtag_overlap_matrix_format.py, tests/m2/test_mtag_maxfdr_filter.py, tests/m2/test_plink_clump_invocation.py, tests/m2/test_mtcojo_eligible_targets.py, tests/m2/test_mtcojo_extreme_overlap_filter.py, tests/m2/test_build_region_union.py, tests/m2/test_call_class1_novelty.py, tests/m2/test_catalog_lock_manifest_v_lock_M2.py, tests/m2/test_1000g_afr_plink_build.py, tests/m2/test_m2_stratum_keys.py</files>
  <read_first>
    - tests/m1/conftest.py (mirror its structure: shared fixtures for project_root, sample TSV paths, mock LDSC matrix)
    - tests/m1/test_reduce_ldsc_rg_matrix.py (mirror parametrize patterns)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md (lines 64-78 — 14 required test files)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Wave 0 Gaps" lines 533-544
    - pytest.ini at project root
  </read_first>
  <behavior>
    - tests/m2/conftest.py exports project_root() fixture pointing at the git root via Path(__file__).resolve().parents[2]
    - conftest exports synthetic_ldsc_matrix() fixture: 5×5 PSD matrix, diag=1.0, off-diag in [0.0, 0.3], seed=42
    - conftest exports synthetic_z_matrix() fixture: (100, 5) z-score grid, seed=42
    - conftest exports trait_inventory_yaml() fixture pointing at config/trait_inventory.yaml
    - Each test_*.py imports its target module behind pytest.importorskip OR a skip-on-ImportError guard so collection succeeds even when the target module does not yet exist
    - test_cpassoc_shom_shet.py — 4 tests: identity case (R=I → SHom = Σ z²), 2-trait analytical case, 5-trait synthetic case, dimension mismatch raises
    - test_safe_inverse.py — 3 tests: well-conditioned R returns pinv(R), near-singular R triggers ridge fallback (cond > 1e6 → R + λI), eigvalsh(result @ R) ≈ I within tolerance
    - test_m2_stratum_keys.py — 4 tests: EUR returns ≥3 keys, AFR returns ≥3 keys, TRANS returns ≥3 keys, _MIN_PER_STRATUM violation raises AssertionError
    - test_build_mtag_residcov_slice.py — 3 tests: slice preserves trait order, sidecar JSON written, output is bare numeric (no header, no index)
    - test_mtag_overlap_matrix_format.py — 2 tests: np.loadtxt round-trip succeeds, shape K×K matches len of trait_order.json
    - test_mtag_maxfdr_filter.py — 2 tests: rows with max_FDR ≥ 0.05 are dropped, max_FDR < 0.05 retained
    - test_plink_clump_invocation.py — 2 tests: shell command contains "--clump" "--clump-p1 5e-8" "--clump-r2 0.01" "--clump-kb 1000"
    - test_mtcojo_eligible_targets.py — 2 tests: only MTAG-novel targets with gcov_int > 0.1 with ANY contributing trait pair are emitted; MTAG-null targets skipped
    - test_mtcojo_extreme_overlap_filter.py — 2 tests: filter on bivariate intercept matrix gcov_int > 0.1; threshold boundary case
    - test_build_region_union.py — 4 tests: strict bedtools merge default, ±1 Mb windows, provenance JSON column preserved, empty input → empty output
    - test_call_class1_novelty.py — 4 tests: MTAG p<5e-8 OR CPASSOC p<5e-8 admitted, max single-trait p ≥ 5e-8 required, ±500 kb GWAS Catalog window enforced, MTAG ∩ CPASSOC tagged confidence=high
    - test_catalog_lock_manifest_v_lock_M2.py — 2 tests: row exists with key=gwas_catalog.v_lock_M2, SHA-256 is 64-hex-char string, last_modified parseable as ISO date
    - test_1000g_afr_plink_build.py — 2 tests: 22 .bed files exist, 22 .bim files exist (each .bim line count > 100k SNPs after MAF/HWE filters)
  </behavior>
  <action>
    Author 14 test files + tests/m2/conftest.py + tests/m2/fixtures/.gitkeep mirroring the M1 pattern. Each test file imports its target module name with a skip-on-missing guard so pytest collection succeeds with 0 errors.

    Concrete conftest.py:
    ```python
    # tests/m2/conftest.py
    from __future__ import annotations
    from pathlib import Path
    import numpy as np
    import pytest

    @pytest.fixture
    def project_root() -> Path:
        return Path(__file__).resolve().parents[2]

    @pytest.fixture
    def synthetic_ldsc_matrix() -> np.ndarray:
        rng = np.random.default_rng(42)
        A = rng.uniform(0.0, 0.3, size=(5, 5))
        R = (A + A.T) / 2.0
        np.fill_diagonal(R, 1.0)
        return R

    @pytest.fixture
    def synthetic_z_matrix() -> np.ndarray:
        rng = np.random.default_rng(42)
        return rng.standard_normal(size=(100, 5))

    @pytest.fixture
    def trait_inventory_yaml(project_root: Path) -> Path:
        return project_root / "config" / "trait_inventory.yaml"
    ```

    Each test_*.py uses the skip-on-missing pattern for its target module:
    ```python
    import pytest
    cpassoc = pytest.importorskip("cpassoc", reason="Wave 0 Task 7 not landed")
    # OR
    try:
        from src.python.build_mtag_residcov_slice import slice_for_stratum
    except ImportError:
        slice_for_stratum = None

    @pytest.mark.skipif(slice_for_stratum is None, reason="Wave 2 Task 1 not landed")
    def test_slice_preserves_trait_order(...):
        ...
    ```

    Atomic commit: `test(m2-00): scaffold pytest M2 RED phase per VALIDATION.md (D-M2-04, D-M2-Q6, REQ-MTAG-OVERLAP)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; pytest tests/m2/ --collect-only 2>&amp;1 | tail -20</automated>
  </verify>
  <acceptance_criteria>
    - File `tests/m2/conftest.py` exists and `grep -c '@pytest.fixture' tests/m2/conftest.py` returns ≥3
    - All 13 `tests/m2/test_*.py` files exist (verify with `ls tests/m2/test_*.py | wc -l` returns 13)
    - `pytest tests/m2/ --collect-only` exits 0 with NO `ERROR` lines (skipped tests are OK)
    - `tests/m2/fixtures/.gitkeep` exists
    - `git log -1 --pretty=%B` matches `test(m2-00): scaffold pytest M2 RED phase`
  </acceptance_criteria>
  <done>tests/m2/ pytest collection succeeds with 0 import errors; 14 stub test files committed atomically; RED phase ready for GREEN landings in later tasks/waves.</done>
</task>

<task type="auto">
  <name>Task 2: Six conda env files (envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml) per Pattern D + Pitfalls 4-6</name>
  <files>envs/m2-mtag.yml, envs/m2-cpassoc.yml, envs/m2-clumping.yml, envs/m2-mtcojo.yml, envs/m2-regions.yml, envs/m2-novelty.yml</files>
  <read_first>
    - envs/m1-harmonize.yml (channels block + dependencies block style reference)
    - envs/m1-ldsc-rg.yml (numpy<2 pin example for LDSC compat)
    - envs/m1-munge.yml
    - envs/plink.yml (existing PLINK pin reference)
    - envs/gcta.yml (existing GCTA pin reference for mtCOJO)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pattern D" lines 442-457
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 4-6"
  </read_first>
  <action>
    Author six new env files. Pin versions exactly per the spec below.

    **envs/m2-mtag.yml** (Pitfall 6: MTAG is git-only, NOT on PyPI; numpy<2 pin):
    ```yaml
    name: m2-mtag
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.10
      - numpy=1.26.4
      - scipy=1.11.4
      - pandas=2.2.2
      - pybedtools=0.10
      - pyyaml
      - pytest=7.4.4
      - pip
    ```
    MTAG is invoked as `python tools/mtag/mtag.py` from this env (vendored in Task 3, not pip-installed).

    **envs/m2-cpassoc.yml** (D-M2-04 Python reimplementation):
    ```yaml
    name: m2-cpassoc
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.11
      - numpy=1.26.4
      - scipy=1.11.4
      - pandas=2.2.2
      - pyarrow=15.0.0
      - pyyaml
      - pytest=7.4.4
    ```

    **envs/m2-clumping.yml** (Pitfall 5: PLINK 2.0 has NO --clump; MUST pin plink=1.9):
    ```yaml
    name: m2-clumping
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.11
      - plink=1.9       # CRITICAL: PLINK 2.0 has no --clump flag
      - pandas=2.2.2
      - pyyaml
      - pytest=7.4.4
    ```

    **envs/m2-mtcojo.yml** (Q4 + Q8 — GCTA bundled mtCOJO):
    ```yaml
    name: m2-mtcojo
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.11
      - gcta=1.94.1
      - pandas=2.2.2
      - pyyaml
      - pytest=7.4.4
    ```

    **envs/m2-regions.yml** (D-M2-09 + Q6 — bedtools default merge):
    ```yaml
    name: m2-regions
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.11
      - bedtools=2.31.1
      - pybedtools=0.10
      - pandas=2.2.2
      - pyarrow=15.0.0
      - pyyaml
      - pytest=7.4.4
    ```

    **envs/m2-novelty.yml** (REQ-NOVELTY-CLASS-1 + D-M2-05 GWAS Catalog parsing):
    ```yaml
    name: m2-novelty
    channels: [conda-forge, bioconda]
    dependencies:
      - python=3.11
      - bedtools=2.31.1
      - pybedtools=0.10
      - pandas=2.2.2
      - pyarrow=15.0.0
      - pyyaml
      - pytest=7.4.4
    ```

    Atomic commit: `chore(m2-00): six conda envs (mtag/cpassoc/clumping/mtcojo/regions/novelty) per Pattern D + Pitfalls 4-6`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; ls envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml &amp;&amp; grep -l "plink=1.9" envs/m2-clumping.yml &amp;&amp; grep -l "numpy=1.26.4" envs/m2-mtag.yml &amp;&amp; grep -l "gcta=1.94" envs/m2-mtcojo.yml &amp;&amp; grep -l "bedtools=2.31" envs/m2-regions.yml &amp;&amp; python -c "import yaml; [yaml.safe_load(open(f'envs/m2-{e}.yml')) for e in ['mtag','cpassoc','clumping','mtcojo','regions','novelty']]"</automated>
  </verify>
  <acceptance_criteria>
    - All 6 files exist (`envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml`)
    - `grep -c "plink=1.9" envs/m2-clumping.yml` returns ≥1 (Pitfall 5)
    - `grep -c "numpy=1.26.4" envs/m2-mtag.yml` returns ≥1 (Pitfall 6 numpy<2)
    - `grep -c "gcta=1.94" envs/m2-mtcojo.yml` returns ≥1
    - `grep -c "bedtools=2.31" envs/m2-regions.yml` returns ≥1
    - `grep -c "bedtools=2.31" envs/m2-novelty.yml` returns ≥1
    - `python -c 'import yaml; [yaml.safe_load(open(f"envs/m2-{e}.yml")) for e in ["mtag","cpassoc","clumping","mtcojo","regions","novelty"]]'` exits 0
    - `git log -1 --pretty=%B` matches `chore(m2-00): six conda envs`
  </acceptance_criteria>
  <done>Six envs/m2-*.yml files exist, parse as valid YAML, pin versions per RESEARCH Pattern D + Pitfalls 4-6, and are committed atomically.</done>
</task>

<task type="auto">
  <name>Task 3: Vendor MTAG at tools/mtag/ + verify --residcov_path flag exists (Pitfall 6, D-M2-10)</name>
  <files>tools/mtag/, tools/mtag/.git_pinned_commit, tools/mtag/.git_clone_log</files>
  <read_first>
    - tools/ldsc/README.md (existing precedent for vendored research-grade tools)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 6" lines 615-625
    - envs/m2-mtag.yml (just authored in Task 2)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q1" lines 105-130 (MTAG flag verification baseline)
  </read_first>
  <action>
    Vendor MTAG via git clone. `pip install mtag` does NOT exist (Pitfall 6).

    Concrete shell sequence:
    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    mkdir -p tools/
    if [ ! -d tools/mtag ]; then
        git clone --depth 1 https://github.com/JonJala/mtag.git tools/mtag
    fi
    cd tools/mtag
    git rev-parse HEAD > .git_pinned_commit
    cd -
    # Verify --help runs cleanly inside the m2-mtag conda env and lists --residcov_path
    source /rs1/researchers/c/ckclinto/miniconda3/etc/profile.d/conda.sh
    if [ ! -d ./.snakemake/conda/m2-mtag-temp ]; then
        conda env create -f envs/m2-mtag.yml -p ./.snakemake/conda/m2-mtag-temp 2>&1 | tail -5
    fi
    PYTHONPATH=tools/mtag ./.snakemake/conda/m2-mtag-temp/bin/python tools/mtag/mtag.py --help 2>&1 | tee tools/mtag/.git_clone_log
    grep -E -- "--residcov_path" tools/mtag/.git_clone_log
    grep -E -- "--no_overlap"   tools/mtag/.git_clone_log
    grep -E -- "--p_sig"        tools/mtag/.git_clone_log
    grep -E -- "--sumstats"     tools/mtag/.git_clone_log
    ```

    Add tools/mtag/.git_pinned_commit + tools/mtag/.git_clone_log to git (the .git_clone_log is the audit record proving the actual MTAG CLI surface area at vendoring time per D-M2-10 correction). Do NOT add tools/mtag/.git/ — it is a nested git checkout; .gitignore should already exclude nested .git dirs.

    If any of the four flag greps fails, ABORT — that means upstream MTAG changed its CLI and Wave 2 needs re-planning.

    Atomic commit: `chore(m2-00): vendor MTAG at tools/mtag/ + verify --residcov_path flag exists (D-M2-10 + Pitfall 6)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f tools/mtag/mtag.py &amp;&amp; test -s tools/mtag/.git_pinned_commit &amp;&amp; grep -E -- "--residcov_path" tools/mtag/.git_clone_log &amp;&amp; grep -E -- "--no_overlap" tools/mtag/.git_clone_log &amp;&amp; grep -E -- "--p_sig" tools/mtag/.git_clone_log</automated>
  </verify>
  <acceptance_criteria>
    - `tools/mtag/mtag.py` exists (file size > 1000 bytes)
    - `tools/mtag/.git_pinned_commit` exists with a 40-char SHA
    - `tools/mtag/.git_clone_log` contains literal `--residcov_path` (CRITICAL — D-M2-10)
    - `tools/mtag/.git_clone_log` contains `--no_overlap`
    - `tools/mtag/.git_clone_log` contains `--p_sig`
    - `tools/mtag/.git_clone_log` contains `--sumstats`
    - `git log -1 --pretty=%B` matches `chore(m2-00): vendor MTAG`
  </acceptance_criteria>
  <done>MTAG vendored at tools/mtag/ at a pinned commit; --residcov_path flag verified present in audit log; D-M2-10 correction documented.</done>
</task>

<task type="auto">
  <name>Task 4: BLOCKING — Build 1000G AFR PLINK bfile tree (Pitfall 3) — m2_reference.smk + production fire</name>
  <files>src/snakemake/rules/m2_reference.smk, data/reference/ldsc/1000G_AFR_Phase3_plink/</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 3" lines 570-593
    - data/raw/1kg/AFR.samples (verify exists; expected 504 sample IDs)
    - data/raw/1kg/vcf/ (verify all 22 chr*.vcf.gz exist)
    - data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.22.bim (mirror filename convention)
    - envs/m2-clumping.yml (just authored in Task 2 — provides plink=1.9)
    - config/pipeline.yaml (path-parameterization roots)
    - src/snakemake/rules/m1_munge.smk (project-root + path-parameterization pattern reference)
    - tests/m2/test_1000g_afr_plink_build.py (the RED test from Task 1)
  </read_first>
  <action>
    Pitfall 3: `data/reference/ldsc/1000G_AFR_Phase3_plink/` does NOT exist on disk. Only `.frq` files at `data/reference/ldsc/1000G_Phase3_frq_AFR/` exist. Build .bed/.bim/.fam triples from `data/raw/1kg/vcf/chr*.vcf.gz` + `data/raw/1kg/AFR.samples`.

    Author `src/snakemake/rules/m2_reference.smk`:

    ```python
    """M2 Wave 0 reference-data builder: 1000G AFR Phase 3 PLINK bfiles.

    Pitfall 3: data/reference/ldsc/1000G_AFR_Phase3_plink/ has NO .bed/.bim/.fam
    on disk; only the LDSC-public .frq files at 1000G_Phase3_frq_AFR/ are present.
    Build the bfile triple per chr from data/raw/1kg/vcf/chr{chr}.vcf.gz keeping
    data/raw/1kg/AFR.samples (504 sample IDs).

    Output: data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{chr}.{bed,bim,fam}
    Filters: --maf 0.005 --geno 0.05 --hwe 1e-6 (per RESEARCH Pitfall 3 spec).
    """
    from pathlib import Path
    import os

    try:
        _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
    except NameError:
        _BASE = Path(os.getcwd())

    _AFR_PLINK_DIR = "data/reference/ldsc/1000G_AFR_Phase3_plink"

    rule m2_build_1000g_afr_plink_chr:
        """Per-chr 1000G AFR PLINK bfile build from VCF + AFR.samples."""
        input:
            vcf="data/raw/1kg/vcf/chr{chr}.vcf.gz",
            keep="data/raw/1kg/AFR.samples",
        output:
            bed=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bed",
            bim=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bim",
            fam=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.fam",
        params:
            out_prefix=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}",
        conda:
            "../../../envs/m2-clumping.yml"
        resources:
            mem_mb=4000,
            runtime=120,
        threads: 2
        shell:
            r"""
            mkdir -p $(dirname {params.out_prefix})
            plink \
                --vcf {input.vcf} \
                --keep {input.keep} \
                --maf 0.005 \
                --geno 0.05 \
                --hwe 1e-6 \
                --make-bed \
                --memory 3500 \
                --out {params.out_prefix}
            test -s {output.bed}
            test -s {output.bim}
            test -s {output.fam}
            """

    rule m2_build_1000g_afr_plink_all:
        """Aggregator — all 22 autosomes built."""
        input:
            expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bed", chr=range(1, 23)),
            expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bim", chr=range(1, 23)),
            expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.fam", chr=range(1, 23)),
        output:
            sentinel=f"{_AFR_PLINK_DIR}/.build_complete",
        shell:
            "touch {output.sentinel}"
    ```

    Production fire (per CLAUDE.md use the smoke_dev snakemake binary with --use-conda):

    ```bash
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
        --use-conda \
        --snakefile src/snakemake/rules/m2_reference.smk \
        --cores 4 \
        --resources mem_mb=16000 \
        m2_build_1000g_afr_plink_all
    ```

    For LSF dispatch: wrap the snakemake call in bsub_wrapper.sh, queue=standard, runtime per chr ~120 min, 22 chr parallelizable. Total wall ~3 hrs. Carter may fire this in background while later tasks proceed; the AFR bfile is consumed only by Wave 4 clumping.

    After fire, update tests/m2/test_1000g_afr_plink_build.py to assert all 22 chr triples exist.

    Atomic commits:
    1. `feat(m2-00): m2_reference.smk for 1000G AFR PLINK bfile build (Pitfall 3)`
    2. `data(m2-00): build 1000G AFR PLINK bfiles 22 chr fire (Pitfall 3)` — after fire completes; data not committed (per .gitignore convention; only the sentinel + test passes)
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/snakemake/rules/m2_reference.smk &amp;&amp; grep -c "rule m2_build_1000g_afr_plink_chr:" src/snakemake/rules/m2_reference.smk &amp;&amp; grep -c -- "--maf 0.005" src/snakemake/rules/m2_reference.smk &amp;&amp; ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.bed &amp;&amp; pytest tests/m2/test_1000g_afr_plink_build.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/snakemake/rules/m2_reference.smk` exists
    - `grep -c "rule m2_build_1000g_afr_plink_chr:" src/snakemake/rules/m2_reference.smk` returns ≥1
    - `grep -c "rule m2_build_1000g_afr_plink_all:" src/snakemake/rules/m2_reference.smk` returns ≥1
    - `grep -c -- "--maf 0.005" src/snakemake/rules/m2_reference.smk` returns ≥1
    - `grep -c -- "--keep {input.keep}" src/snakemake/rules/m2_reference.smk` returns ≥1
    - After fire: `ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.bed | wc -l` returns 22
    - After fire: `ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.bim | wc -l` returns 22
    - After fire: `ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.fam | wc -l` returns 22
    - `wc -l data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.bim` returns ≥100,000 SNPs
    - `pytest tests/m2/test_1000g_afr_plink_build.py -x` exits 0
    - `git log --oneline -5 | grep "1000G AFR PLINK"`
  </acceptance_criteria>
  <done>m2_reference.smk authored; 1000G AFR PLINK bfiles built across 22 autosomes; tests/m2/test_1000g_afr_plink_build.py GREEN; ready for Wave 4 clumping consumption.</done>
</task>

<task type="auto">
  <name>Task 5: GWAS Catalog v_lock_M2 snapshot fetch + manifest row (D-M2-05, REQ-CATALOG-VERSION-LOCK, Pitfall 10)</name>
  <files>data/catalogs/gwas-catalog-associations-full.zip, data/catalogs/catalog_lock_manifest.tsv</files>
  <read_first>
    - data/catalogs/catalog_lock_manifest.tsv (existing schema — read column header line so the new row matches the existing column order EXACTLY)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q5" lines 250-289 (URL + bash recipe)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pitfall 10" lines 657-669 (hash the .zip not the unpacked TSV)
    - tests/m2/test_catalog_lock_manifest_v_lock_M2.py (the RED test from Task 1)
  </read_first>
  <action>
    Download `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip` (~56 MB), capture HTTP `Last-Modified` header, compute SHA-256 of the .zip BYTES (Pitfall 10), append a row to `data/catalogs/catalog_lock_manifest.tsv` keyed `gwas_catalog.v_lock_M2`.

    First read the existing manifest header so the row column order matches exactly:
    ```bash
    head -1 data/catalogs/catalog_lock_manifest.tsv
    ```

    Concrete bash recipe (adapt the printf to the discovered column order):
    ```bash
    set -euo pipefail
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    mkdir -p data/catalogs
    URL="https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip"
    DEST="data/catalogs/gwas-catalog-associations-full.zip"

    # Capture Last-Modified header
    LAST_MOD=$(curl -sI "$URL" | awk -v IGNORECASE=1 '/^last-modified:/ {sub(/^[^:]*: */, ""); sub(/\r$/, ""); print}')

    # Download with retries
    curl -fsSL --retry 3 -o "$DEST" "$URL"

    # Hash the ZIP BYTES (Pitfall 10)
    SHA=$(sha256sum "$DEST" | awk '{print $1}')
    SIZE=$(stat --printf='%s' "$DEST")
    FETCH_DATE=$(date -u +%Y-%m-%d)
    LAST_MOD_ISO=$(date -u -d "$LAST_MOD" +%Y-%m-%d 2>/dev/null || echo "$LAST_MOD")

    # Inspect existing schema
    HDR=$(head -1 data/catalogs/catalog_lock_manifest.tsv)
    echo "Existing schema: $HDR"

    # Adapt to existing column order. Most plausible schema (from CONTEXT/RESEARCH):
    #   key  version  url  sha256  fetch_date  size_bytes  status
    # Adjust the field count + order to match the actual `head -1` output.
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "gwas_catalog.v_lock_M2" \
        "${LAST_MOD_ISO}_full_release" \
        "$URL" \
        "$SHA" \
        "$FETCH_DATE" \
        "$SIZE" \
        "M2-locked" \
        >> data/catalogs/catalog_lock_manifest.tsv
    ```

    The new row MUST contain (column-name agnostic):
    - key column = literal `gwas_catalog.v_lock_M2`
    - URL = the literal EBI URL above
    - SHA-256 = 64-hex-char hash of the .zip BYTES (Pitfall 10 — NEVER hash the unpacked TSV)
    - last_modified or fetch_date = the captured Last-Modified header from the EBI server (date-only, ISO format)
    - size_bytes = stat output

    Update tests/m2/test_catalog_lock_manifest_v_lock_M2.py from RED → GREEN: assert the row exists, SHA-256 matches re-computation of the .zip on disk, last_modified parses as ISO date.

    Atomic commit: `feat(m2-00): GWAS Catalog v_lock_M2 fetch + manifest row (D-M2-05, REQ-CATALOG-VERSION-LOCK, Pitfall 10)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -s data/catalogs/gwas-catalog-associations-full.zip &amp;&amp; grep -c "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv &amp;&amp; pytest tests/m2/test_catalog_lock_manifest_v_lock_M2.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `data/catalogs/gwas-catalog-associations-full.zip` exists with size > 40 MB (RESEARCH reports 56 MB; 40 MB lower bound for drift tolerance)
    - `grep -c "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv` returns 1
    - The matching row contains the literal URL `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip`
    - The SHA-256 field in the row is exactly 64 hex chars
    - Re-computing `sha256sum data/catalogs/gwas-catalog-associations-full.zip` produces the same hash recorded in the manifest row
    - `pytest tests/m2/test_catalog_lock_manifest_v_lock_M2.py -x` exits 0
    - `git log -1 --pretty=%B` matches `feat(m2-00): GWAS Catalog v_lock_M2`
  </acceptance_criteria>
  <done>GWAS Catalog .zip on disk; v_lock_M2 row appended to catalog_lock_manifest.tsv with SHA-256 hash of .zip bytes; test GREEN; REQ-CATALOG-VERSION-LOCK satisfied for M2.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 6: src/python/cpassoc.py — Zhu 2015 SHom + SHet + safe-inverse (D-M2-04, Q2)</name>
  <files>src/python/cpassoc.py, tests/m2/test_cpassoc_shom_shet.py, tests/m2/test_safe_inverse.py</files>
  <read_first>
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Q2" lines 132-180 (full code pattern + safe-inverse spec)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-04 lines 70-81
    - tests/m2/conftest.py (uses synthetic_z_matrix and synthetic_ldsc_matrix fixtures)
    - src/python/m1_raw_glob.py (style reference: shebang, future annotations, docstring)
  </read_first>
  <behavior>
    cpassoc_shom: For R = identity (no overlap), SHom(z) returns Σ z_i² (chi-square df=K) — analytical truth.
    cpassoc_shet: For R = identity, SHet(z) returns Σ z_i² − (Σ z_i)² / K (chi-square df=K-1).
    _safe_inverse: For well-conditioned R (cond < 1e6), returns numpy.linalg.pinv(R, rcond=1e-15). For near-singular R (cond > 1e6), applies ridge regularization R + λI where λ = 1e-4 × trace(R) / K BEFORE pinv. The eigenvalues of (result @ R) cluster around 1.0 within tolerance for well-conditioned cases.
  </behavior>
  <action>
    Implement `src/python/cpassoc.py` per RESEARCH Q2 code pattern (lines 144-178). Concrete module:

    ```python
    #!/usr/bin/env python3
    """CPASSOC SHom + SHet test statistics (Zhu 2015 *AJHG* 96:21-36).

    M2 plan reference: m2-03-cpassoc-3-strata-PLAN.md.
    Decision references: D-M2-04 (Python reimpl with LDSC intercept matrix as R),
    D-M2-Q2 (numpy.linalg.pinv with conditional ridge fallback when cond > 1e6).

    Formulas:
      SHom = z' R^-1 z                                          # chi-square df=K
      SHet = z' (R^-1 - R^-1 1 (1' R^-1 1)^-1 1' R^-1) z        # chi-square df=K-1

    where R is the cohort-correlation matrix (LDSC bivariate-intercept matrix from M1)
    and z is the per-SNP K-vector of trait z-scores.
    """
    from __future__ import annotations
    import numpy as np

    _COND_THRESHOLD = 1e6
    _RIDGE_FLOOR_DEFAULT = 1e-4
    _PINV_RCOND = 1e-15


    def _safe_inverse(R: np.ndarray, ridge_floor: float = _RIDGE_FLOOR_DEFAULT) -> np.ndarray:
        """Pseudoinverse with conditional ridge fallback for near-singular R.

        Per D-M2-Q2: if cond(R) > 1e6, apply ridge regularization R + λI where
        λ = ridge_floor * trace(R) / K before inversion.
        """
        R = (R + R.T) / 2.0  # defensive symmetry guard
        cond = float(np.linalg.cond(R))
        if cond > _COND_THRESHOLD:
            K = R.shape[0]
            lam = ridge_floor * float(np.trace(R)) / K
            R = R + lam * np.eye(K)
        return np.linalg.pinv(R, rcond=_PINV_RCOND)


    def cpassoc_shom(z: np.ndarray, R: np.ndarray) -> np.ndarray:
        """SHom test statistic per SNP. Returns chi-square df=K values.

        Parameters
        ----------
        z : np.ndarray, shape (n_snps, K)
            Per-SNP K-trait z-score matrix.
        R : np.ndarray, shape (K, K)
            Cohort-correlation matrix (LDSC bivariate-intercept).

        Returns
        -------
        np.ndarray, shape (n_snps,)
            SHom chi-square statistic per SNP (df = K).
        """
        if z.ndim != 2:
            raise ValueError(f"z must be 2D (n_snps, K), got shape {z.shape}")
        if R.shape[0] != R.shape[1]:
            raise ValueError(f"R must be square, got shape {R.shape}")
        if z.shape[1] != R.shape[0]:
            raise ValueError(f"K mismatch: z has K={z.shape[1]}, R is {R.shape}")
        Rinv = _safe_inverse(R)
        return np.einsum("ij,jk,ik->i", z, Rinv, z)


    def cpassoc_shet(z: np.ndarray, R: np.ndarray) -> np.ndarray:
        """SHet test statistic per SNP. Returns chi-square df=K-1 values."""
        if z.ndim != 2:
            raise ValueError(f"z must be 2D (n_snps, K), got shape {z.shape}")
        if R.shape[0] != R.shape[1]:
            raise ValueError(f"R must be square, got shape {R.shape}")
        if z.shape[1] != R.shape[0]:
            raise ValueError(f"K mismatch: z has K={z.shape[1]}, R is {R.shape}")
        Rinv = _safe_inverse(R)
        K = R.shape[0]
        one = np.ones(K)
        denom = float(one @ Rinv @ one)
        proj = Rinv - np.outer(Rinv @ one, one @ Rinv) / denom
        return np.einsum("ij,jk,ik->i", z, proj, z)
    ```

    Update tests/m2/test_cpassoc_shom_shet.py from RED → GREEN. Concrete tests (analytical truth values):

    ```python
    import numpy as np
    import pytest
    from src.python.cpassoc import cpassoc_shom, cpassoc_shet, _safe_inverse

    def test_shom_identity_R_equals_sum_z_squared():
        z = np.array([[1.0, 2.0, 3.0]])
        R = np.eye(3)
        # SHom = z' I z = 1 + 4 + 9 = 14
        assert cpassoc_shom(z, R)[0] == pytest.approx(14.0, abs=1e-10)

    def test_shet_identity_R_equals_centered_sum():
        z = np.array([[1.0, 2.0, 3.0]])
        R = np.eye(3)
        # SHet = sum(z²) - (sum z)² / K = 14 - 36/3 = 14 - 12 = 2.0
        assert cpassoc_shet(z, R)[0] == pytest.approx(2.0, abs=1e-10)

    def test_5_trait_synthetic(synthetic_z_matrix, synthetic_ldsc_matrix):
        out_shom = cpassoc_shom(synthetic_z_matrix, synthetic_ldsc_matrix)
        out_shet = cpassoc_shet(synthetic_z_matrix, synthetic_ldsc_matrix)
        assert out_shom.shape == (100,)
        assert out_shet.shape == (100,)
        assert (out_shom >= 0).all()
        assert (out_shet >= 0).all()

    def test_dimension_mismatch_raises():
        with pytest.raises(ValueError):
            cpassoc_shom(np.array([[1.0, 2.0]]), np.eye(3))
    ```

    Update tests/m2/test_safe_inverse.py from RED → GREEN:

    ```python
    import numpy as np
    import pytest
    from src.python.cpassoc import _safe_inverse

    def test_well_conditioned_returns_pinv(synthetic_ldsc_matrix):
        Rinv = _safe_inverse(synthetic_ldsc_matrix)
        np.testing.assert_allclose(
            Rinv @ synthetic_ldsc_matrix, np.eye(5), atol=1e-8
        )

    def test_near_singular_triggers_ridge():
        # Construct a near-singular matrix: rank-1 + tiny noise
        v = np.array([1.0, 1.0, 1.0])
        R = np.outer(v, v) + 1e-15 * np.eye(3)
        Rinv = _safe_inverse(R, ridge_floor=1e-4)
        # No NaN/Inf even though raw pinv would explode
        assert np.all(np.isfinite(Rinv))

    def test_eigvalsh_psd_tolerance():
        np.random.seed(42)
        A = np.random.uniform(0.0, 0.3, size=(5, 5))
        R = (A + A.T) / 2.0
        np.fill_diagonal(R, 1.0)
        Rinv = _safe_inverse(R)
        assert np.all(np.linalg.eigvalsh((Rinv + Rinv.T) / 2.0) > -1e-10)
    ```

    Atomic commit: `feat(m2-00): src/python/cpassoc.py SHom + SHet + safe-inverse (D-M2-04, D-M2-Q2)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/cpassoc.py &amp;&amp; grep -c "def cpassoc_shom" src/python/cpassoc.py &amp;&amp; grep -c "def cpassoc_shet" src/python/cpassoc.py &amp;&amp; grep -c "def _safe_inverse" src/python/cpassoc.py &amp;&amp; pytest tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/cpassoc.py` exists with min 60 lines
    - `grep -c "^def cpassoc_shom" src/python/cpassoc.py` returns 1
    - `grep -c "^def cpassoc_shet" src/python/cpassoc.py` returns 1
    - `grep -c "^def _safe_inverse" src/python/cpassoc.py` returns 1
    - `grep -c "np.linalg.pinv" src/python/cpassoc.py` returns ≥1
    - `grep -c "np.linalg.cond" src/python/cpassoc.py` returns ≥1
    - `pytest tests/m2/test_cpassoc_shom_shet.py -x` exits 0
    - `pytest tests/m2/test_safe_inverse.py -x` exits 0
    - `git log -1 --pretty=%B` matches `feat(m2-00): src/python/cpassoc.py`
  </acceptance_criteria>
  <done>cpassoc.py module GREEN; SHom + SHet + safe-inverse implemented per D-M2-04 + Q2; tests pass; ready for Wave 3 consumption.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 7: src/python/m2_stratum_keys.py — deterministic stratum enumeration with _MIN_PER_STRATUM=3 (D-M2-06, D-M2-Q6, Pattern B)</name>
  <files>src/python/m2_stratum_keys.py, tests/m2/test_m2_stratum_keys.py</files>
  <read_first>
    - src/python/m1_trait_keys.py (Pattern B reference — defensive bound + TOKEN_MAP + dedupe-and-sort idiom)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md §"Pattern B" lines 393-430 (full code pattern; note _MIN_PER_STRATUM was 5 in research recommendation but D-M2-Q6 LOCKED IT AT 3)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-06 lines 90-96
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-CONTEXT.md §D-M2-Q6 lines 272-276 (CARTER LOCKED _MIN_PER_STRATUM=3)
    - config/trait_inventory.yaml (47 cells × 24 fields; ancestry field; qc_status field; munged_path field)
  </read_first>
  <behavior>
    - keys_for_stratum(yaml_path, "EUR") returns sorted list of trait keys with ancestry=EUR AND qc_status != MISSING AND munged_path exists on disk
    - keys_for_stratum(yaml_path, "AFR") returns AFR-stratum trait keys; expected count 3-9
    - keys_for_stratum(yaml_path, "TRANS") returns TRANS+MULTI stratum trait keys (treat MULTI as TRANS per CONTEXT D-M2-06 "TRANS or MULTI for GBMI")
    - When a stratum has < _MIN_PER_STRATUM=3 cells, the function does NOT raise; instead it returns the partial list AND the caller (Snakemake rule) is responsible for emitting a row to skipped_strata.tsv. This matches the soft-floor semantics of D-M2-Q6.
    - Provide a separate helper enforce_stratum_floor(keys, stratum) that DOES raise AssertionError with a descriptive message if len(keys) < _MIN_PER_STRATUM, for use by tests + production fire validators.
    - _MIN_PER_STRATUM = 3 (locked by Carter in D-M2-Q6; NOT 5 from RESEARCH defensive default)
    - _MAX_PER_STRATUM = 9 (the locked 9-trait inventory)
    - STRATA = ("EUR", "AFR", "TRANS")
    - "MULTI" ancestry maps to TRANS for stratum purposes (GBMI naming convention per CONTEXT D-M2-06)
  </behavior>
  <action>
    Implement `src/python/m2_stratum_keys.py` per RESEARCH Pattern B code pattern, with **D-M2-Q6 LOCK**: `_MIN_PER_STRATUM = 3` (NOT 5). Concrete module:

    ```python
    #!/usr/bin/env python3
    """M2 deterministic (stratum, trait_key) enumeration helper.

    Reads config/trait_inventory.yaml. For each stratum {EUR, AFR, TRANS},
    returns the list of trait keys whose harmonized + munged outputs exist
    on disk and match the requested ancestry.

    Decision references:
      D-M2-06 — strict ancestry match, skip-with-doc when missing
      D-M2-Q6 — _MIN_PER_STRATUM = 3 (Carter-locked; soft floor)
      Pattern B (m1_trait_keys.py) — same defensive-bound idiom

    "MULTI" ancestry (GBMI naming convention) maps to TRANS stratum.
    """
    from __future__ import annotations
    from pathlib import Path
    from typing import Iterable
    import yaml

    STRATA: tuple[str, ...] = ("EUR", "AFR", "TRANS")
    _MIN_PER_STRATUM: int = 3   # D-M2-Q6 Carter-locked (NOT 5 research default)
    _MAX_PER_STRATUM: int = 9   # 9-trait inventory locked per Amendment §4

    # GBMI ancestry MULTI is logically TRANS for stratum purposes
    _ANCESTRY_TO_STRATUM = {
        "EUR": "EUR",
        "AFR": "AFR",
        "TRANS": "TRANS",
        "MULTI": "TRANS",
    }


    def _is_active(entry: dict) -> bool:
        """Cell is active if qc_status != MISSING AND munged_path exists on disk."""
        if entry.get("qc_status") == "MISSING":
            return False
        munged = entry.get("munged_path", "")
        if not munged:
            return False
        return Path(munged).exists()


    def keys_for_stratum(inventory_path: Path, stratum: str) -> list[str]:
        """Return sorted list of trait keys for the given stratum.

        Soft floor: if len < _MIN_PER_STRATUM, returns the partial list anyway;
        the caller is responsible for skip-with-doc handling per D-M2-06.
        Use enforce_stratum_floor() to raise instead.
        """
        if stratum not in STRATA:
            raise ValueError(f"stratum must be one of {STRATA}; got {stratum!r}")

        with open(inventory_path) as f:
            inv = yaml.safe_load(f)

        # config/trait_inventory.yaml top-level shape from M1: { traits: { key: {...}, ... } }
        # OR { key: {...}, ... } directly. Handle both.
        cells = inv.get("traits", inv)

        keys: list[str] = []
        for key, entry in cells.items():
            ancestry = entry.get("ancestry", "")
            cell_stratum = _ANCESTRY_TO_STRATUM.get(ancestry)
            if cell_stratum != stratum:
                continue
            if not _is_active(entry):
                continue
            keys.append(key)

        return sorted(set(keys))


    def enforce_stratum_floor(keys: Iterable[str], stratum: str) -> None:
        """Raise AssertionError if len(keys) < _MIN_PER_STRATUM.

        Production-fire validator. NOT used by Snakemake rules directly
        (they emit skipped_strata.tsv per D-M2-06 instead).
        """
        keys = list(keys)
        assert len(keys) >= _MIN_PER_STRATUM, (
            f"m2_stratum_keys: stratum {stratum} has {len(keys)} keys, "
            f"below floor _MIN_PER_STRATUM={_MIN_PER_STRATUM}. "
            f"Carter-locked at 3 per D-M2-Q6."
        )
        assert len(keys) <= _MAX_PER_STRATUM, (
            f"m2_stratum_keys: stratum {stratum} has {len(keys)} keys, "
            f"above ceiling _MAX_PER_STRATUM={_MAX_PER_STRATUM}. "
            f"9-trait inventory locked per Amendment §4."
        )


    def _main() -> None:
        import argparse
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("--inventory", type=Path,
                        default=Path("config/trait_inventory.yaml"))
        ap.add_argument("--stratum", required=True, choices=STRATA)
        ap.add_argument("--out", type=Path, required=True)
        args = ap.parse_args()
        keys = keys_for_stratum(args.inventory, args.stratum)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(keys) + ("\n" if keys else ""))
        print(f"Wrote {len(keys)} {args.stratum} keys to {args.out}")


    if __name__ == "__main__":
        _main()
    ```

    Update tests/m2/test_m2_stratum_keys.py from RED → GREEN:

    ```python
    import pytest
    from pathlib import Path
    from src.python.m2_stratum_keys import (
        keys_for_stratum, enforce_stratum_floor,
        STRATA, _MIN_PER_STRATUM, _MAX_PER_STRATUM,
    )

    def test_min_per_stratum_locked_at_3():
        # D-M2-Q6 — Carter-locked floor at 3, NOT 5
        assert _MIN_PER_STRATUM == 3
        assert _MAX_PER_STRATUM == 9

    def test_strata_locked():
        assert STRATA == ("EUR", "AFR", "TRANS")

    def test_eur_returns_at_least_3_keys(trait_inventory_yaml):
        keys = keys_for_stratum(trait_inventory_yaml, "EUR")
        # EUR is the densest stratum; expected 5-9 active EUR cells
        assert len(keys) >= 3, f"EUR keys={keys}"

    def test_invalid_stratum_raises():
        with pytest.raises(ValueError):
            keys_for_stratum(Path("config/trait_inventory.yaml"), "FOO")

    def test_floor_violation_raises():
        with pytest.raises(AssertionError):
            enforce_stratum_floor(["x", "y"], "AFR")

    def test_floor_satisfied_passes():
        enforce_stratum_floor(["x", "y", "z"], "AFR")  # ==3, OK
    ```

    Atomic commit: `feat(m2-00): src/python/m2_stratum_keys.py with _MIN_PER_STRATUM=3 (D-M2-06, D-M2-Q6, Pattern B)`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f src/python/m2_stratum_keys.py &amp;&amp; grep -c "_MIN_PER_STRATUM = 3" src/python/m2_stratum_keys.py &amp;&amp; grep -c "STRATA" src/python/m2_stratum_keys.py &amp;&amp; pytest tests/m2/test_m2_stratum_keys.py -x</automated>
  </verify>
  <acceptance_criteria>
    - File `src/python/m2_stratum_keys.py` exists, ≥40 lines
    - `grep -c "_MIN_PER_STRATUM\s*[:=]\s*3" src/python/m2_stratum_keys.py` returns ≥1 (D-M2-Q6 lock — NOT 5)
    - `grep -c "STRATA" src/python/m2_stratum_keys.py` returns ≥1
    - `grep -c '"MULTI"' src/python/m2_stratum_keys.py` returns ≥1 (GBMI ancestry mapping)
    - `grep -c "def keys_for_stratum" src/python/m2_stratum_keys.py` returns 1
    - `grep -c "def enforce_stratum_floor" src/python/m2_stratum_keys.py` returns 1
    - `pytest tests/m2/test_m2_stratum_keys.py -x` exits 0
    - `python src/python/m2_stratum_keys.py --stratum EUR --out /tmp/eur_keys.txt && wc -l /tmp/eur_keys.txt` reports ≥3 lines
    - `git log -1 --pretty=%B` matches `feat(m2-00): src/python/m2_stratum_keys.py`
  </acceptance_criteria>
  <done>m2_stratum_keys.py module GREEN; _MIN_PER_STRATUM=3 (Carter-locked per D-M2-Q6); MULTI→TRANS mapping handles GBMI; ready for Wave 2/3 stratum-based MTAG/CPASSOC orchestration.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 8: Wave 0 sign-off — pytest M2 collection clean + AFR PLINK fire complete + GWAS Catalog locked</name>
  <what-built>
    Wave 0 deliverables:
    - 14 pytest test files at tests/m2/ + conftest.py + fixtures/
    - 6 conda env files at envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml
    - tools/mtag/ vendored at pinned commit with --residcov_path verified
    - 22-chr 1000G AFR PLINK bfile tree at data/reference/ldsc/1000G_AFR_Phase3_plink/
    - GWAS Catalog v_lock_M2 row in data/catalogs/catalog_lock_manifest.tsv with SHA-256 of .zip bytes
    - src/python/cpassoc.py + src/python/m2_stratum_keys.py (both with tests GREEN)
  </what-built>
  <how-to-verify>
    Carter manually verifies four invariants before unblocking Wave 1:

    1. **AFR PLINK fire complete:**
       ```
       ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.bed | wc -l
       # MUST output: 22
       ```

    2. **GWAS Catalog snapshot frozen:**
       ```
       grep "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv
       sha256sum data/catalogs/gwas-catalog-associations-full.zip
       # The hash printed MUST match the SHA-256 column in the manifest row
       ```

    3. **MTAG vendored cleanly:**
       ```
       grep -E -- "--residcov_path" tools/mtag/.git_clone_log
       # Must find a match (D-M2-10 critical correction verified)
       ```

    4. **All Wave 0 unit tests GREEN:**
       ```
       pytest tests/m2/ -x --tb=short
       # All non-skipped tests pass; skipped tests are OK (Wave 1+ targets)
       ```

    If all four pass, type "approved" or "Wave 0 sign-off". If any fails, describe the blocker.
  </how-to-verify>
  <files>.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md</files>
  <action>
    Carter manually inspects the four invariants enumerated in <how-to-verify>. On approval Claude flips `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md` frontmatter from `wave_0_complete: false` / `nyquist_compliant: false` to `wave_0_complete: true` / `nyquist_compliant: true`, and commits with message `docs(m2-00): Wave 0 sign-off — VALIDATION.md flipped to nyquist_compliant: true`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -E "^wave_0_complete: true$" .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md &amp;&amp; grep -E "^nyquist_compliant: true$" .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md</automated>
  </verify>
  <done>Carter signed off on Wave 0 invariants; VALIDATION.md frontmatter advanced; M2 ready for Wave 1 LDSC matrix refire.</done>
  <acceptance_criteria>
    - Carter has reviewed the four invariants above
    - Carter has typed "approved" or equivalent sign-off
    - No blockers identified
    - VALIDATION.md frontmatter `wave_0_complete: false` flipped to `true` and `nyquist_compliant: true` set
  </acceptance_criteria>
  <resume-signal>Type "approved" or "Wave 0 sign-off" to proceed to Wave 1; or describe specific issues for course-correction.</resume-signal>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 9: Wave 0 → Wave 1 explicit sign-off gate (CR-checker WR-5; per-item attestation)</name>
  <what-built>
    This is the natural Wave 0 → Wave 1 gate. Carter must explicitly attest to FOUR
    enumerated invariants below before Wave 1 (LDSC matrix refire) starts. Task 8
    flipped VALIDATION.md frontmatter; this Task 9 is the per-item human attestation
    that goes alongside the frontmatter flip. Both Task 8 (broad sign-off) and Task 9
    (granular four-item attestation) gate Wave 1 — Wave 1 cannot start until both pass.
  </what-built>
  <how-to-verify>
    Carter explicitly attests to all FOUR invariants below. Each must be confirmed
    out loud (not just nodded through) before Wave 1 fires.

    **(a) AFR PLINK build sample size (~504 AFR samples expected):**
    ```
    wc -l data/raw/1kg/AFR.samples
    # Expected: ~504 (1000G AFR sample count)

    head -1 data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.fam | awk '{print NF}'
    # Expected: 6 (PLINK fam format: FID IID PID MID SEX PHENO)

    wc -l data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.fam
    # Expected: ~504 (one row per kept sample)
    ```
    PASS criterion: AFR.samples line count is in [490, 520] AND .fam line count matches AFR.samples line count within ±2.

    **(b) GWAS Catalog v_lock_M2 SHA-256 frozen:**
    ```
    grep "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv
    sha256sum data/catalogs/gwas-catalog-associations-full.zip
    ```
    PASS criterion: SHA-256 in manifest row equals re-computed sha256sum (byte-identical to fetch-time hash; Pitfall 10).

    **(c) All 14 RED tests in place:**
    ```
    ls tests/m2/test_*.py | wc -l
    # Expected: 14

    pytest tests/m2/ --collect-only 2>&1 | tail -5
    # Expected: 0 ERROR lines; collected count > 14 (each test_*.py has multiple tests)
    ```
    PASS criterion: 14 test files exist AND `pytest --collect-only` exits 0 with 0 import errors.

    **(d) MTAG installed and importable:**
    ```
    test -f tools/mtag/mtag.py && echo "vendored OK"
    grep -E -- "--residcov_path" tools/mtag/.git_clone_log
    cat tools/mtag/.git_pinned_commit
    ```
    PASS criterion: tools/mtag/mtag.py exists AND `--residcov_path` literal appears in audit log AND .git_pinned_commit is a 40-char SHA.

    If all four pass, type "Wave 0 four-item attestation approved" or equivalent.
    If any fails, describe the blocker; Wave 1 stays blocked.
  </how-to-verify>
  <files>.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md</files>
  <action>
    Carter manually walks the four invariants above. On approval, Claude appends a one-line attestation row to .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md under a new `## Wave 0 four-item attestation` section recording (a) AFR sample count, (b) GWAS Catalog SHA-256, (c) test file count + pytest collection result, (d) MTAG pinned commit SHA. Commits with message `docs(m2-00): Wave 0 four-item attestation per CR-checker WR-5`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -E "Wave 0 four-item attestation" .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md</automated>
  </verify>
  <done>Carter attested per-item to all four Wave 0 invariants; attestation row appended to VALIDATION.md; Wave 1 cleared to start.</done>
  <acceptance_criteria>
    - Carter has explicitly confirmed each of the four enumerated invariants (a, b, c, d)
    - Carter has typed "Wave 0 four-item attestation approved" or equivalent
    - VALIDATION.md contains a new `## Wave 0 four-item attestation` section with the four recorded values
    - No blockers identified across any of the four items
  </acceptance_criteria>
  <resume-signal>Type "Wave 0 four-item attestation approved" to clear Wave 1 to start; or describe specific failing item (a/b/c/d) for course-correction.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| EBI FTP → local disk | Untrusted external server providing GWAS Catalog .zip; SHA-256 + Last-Modified pin mitigates drift |
| GitHub HTTPS → local disk | Untrusted external (JonJala/mtag.git); pinned commit SHA in tools/mtag/.git_pinned_commit |
| 1000G VCFs → PLINK bfile | Local file → derived artifact; integrity guaranteed by raw 1KG SHA-256 manifest from earlier phases |
| User-supplied YAML → Python parser | config/trait_inventory.yaml → m2_stratum_keys; PyYAML safe_load mitigates code injection |

## STRIDE Threat Register (T-M2-01..T-M2-13 per VALIDATION map)

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M2-09 | Tampering / Drift | data/catalogs/gwas-catalog-associations-full.zip | mitigate | Hash .zip bytes (Pitfall 10), record SHA-256 + Last-Modified at fetch time in catalog_lock_manifest.tsv |
| T-M2-10 | Tampering | EBI ETag drift | accept | EBI does not consistently expose strong ETag; Last-Modified + SHA-256 sufficient (Q5 LOW risk) |
| T-M2-11 | Information disclosure (missing artifact) | 1000G_AFR_Phase3_plink/ | mitigate | Wave 0 BLOCKING build from raw VCFs (Pitfall 3); fail closed via Snakemake MissingInputException if absent |
| T-M2-03 | Tampering / DLL hell | MTAG numpy ABI break | mitigate | envs/m2-mtag.yml pins numpy=1.26.4 (numpy<2 per Pitfall 6) |
| T-M2-06 | Tampering | PLINK 2.0 silently lacks --clump | mitigate | envs/m2-clumping.yml pins plink=1.9 (Pitfall 5); test asserts `plink --version` reports 1.9 |
| T-M2-12 | Denial-of-service (skipped strata) | _MIN_PER_STRATUM violation | mitigate | enforce_stratum_floor raises with descriptive message; production rules emit skipped_strata.tsv per D-M2-06 |
| T-M2-05 | Repudiation | CPASSOC R inversion silently produces NaN | mitigate | _safe_inverse with cond-probe + ridge fallback (Q2); pytest covers near-singular path |
</threat_model>

<verification>
End-of-Wave-0 phase verifier checks:

```bash
# Wave 0 invariants verifier (run before Wave 1 start)
set -e
test -f tests/m2/conftest.py
ls tests/m2/test_*.py | wc -l | grep -q "^14$"
ls envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml
test -f tools/mtag/mtag.py
grep -E -- "--residcov_path" tools/mtag/.git_clone_log
ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.bed | wc -l | grep -q "^22$"
ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.bim | wc -l | grep -q "^22$"
ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.fam | wc -l | grep -q "^22$"
test -s data/catalogs/gwas-catalog-associations-full.zip
grep -q "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv
test -f src/python/cpassoc.py
test -f src/python/m2_stratum_keys.py
pytest tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py tests/m2/test_m2_stratum_keys.py tests/m2/test_catalog_lock_manifest_v_lock_M2.py tests/m2/test_1000g_afr_plink_build.py -x
echo "Wave 0 PASS"
```
</verification>

<success_criteria>
- 14 pytest stub files committed; pytest collection clean (0 errors)
- 6 envs/m2-*.yml committed and parse as valid YAML
- tools/mtag/ vendored at a pinned commit with audit log proving --residcov_path flag exists
- 1000G AFR PLINK bfile tree complete: 66 files (.bed/.bim/.fam × 22 chr)
- GWAS Catalog v_lock_M2 row in catalog_lock_manifest.tsv with SHA-256 of .zip bytes (Pitfall 10)
- src/python/cpassoc.py + src/python/m2_stratum_keys.py with their tests GREEN
- Wave 0 sign-off (Task 8 checkpoint) approved
- Atomic commit per task; commit messages follow convention `feat|chore|test(m2-00): <summary>`
</success_criteria>

<output>
After completion, create `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-SUMMARY.md` documenting:
- Pinned MTAG commit SHA from tools/mtag/.git_pinned_commit
- AFR PLINK fire wall time + LSF job id
- GWAS Catalog v_lock_M2 SHA-256 + Last-Modified date
- pytest counts (collected, passed, skipped) at end-of-wave
- Any deviations from the plan (e.g., env solver issues requiring pin loosening)
</output>
