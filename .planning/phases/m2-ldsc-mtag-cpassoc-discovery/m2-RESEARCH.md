# Phase M2: LDSC + MTAG + CPASSOC discovery — Research

**Researched:** 2026-04-25
**Domain:** Multi-trait joint-signal discovery (MTAG residual-covariance correction, CPASSOC SHom/SHet, mtCOJO sample-overlap sensitivity, PLINK clumping, region union, Class 1 novelty calling) on top of M1 harmonized + LDSC-rg infrastructure
**Confidence:** HIGH on M1-pattern reuse + CPASSOC reimplementation; HIGH on PLINK clumping + region union; **MEDIUM-CRITICAL on MTAG `--overlap` flag terminology** (CONTEXT.md uses colloquial phrasing — actual flag is `--residcov_path`); MEDIUM on mtCOJO trans-ancestry LD reference choice; LOW on AFR PLINK panel availability (must be staged in Wave 0)

## Summary

M2 fires a five-method joint-signal discovery suite over the M1-frozen harmonized inventory: pairwise LDSC rg + intercept matrix expansion (D-M2-01), MTAG (Turley 2018) with residual-covariance correction from the LDSC intercept matrix (D-M2-03 + D-M2-10), CPASSOC (Zhu 2015) SHom/SHet as orthogonal joint-signal test (D-M2-04), mtCOJO (Zhu 2018) sensitivity on extreme-overlap loci (D-M2-08), per-(trait × ancestry) PLINK clumping (D-M2-09), region-union BED construction, and Class 1 novelty calling against a frozen GWAS Catalog v_lock_M2 (D-M2-05). Output is `joint_signal_novel.tsv` per ROADMAP M2 success criterion 5.

The single most important plan-correctness finding the planner must internalize is a **terminology vs flag-name mismatch in the CONTEXT.md decisions**. CONTEXT D-M2-10 + REQ-MTAG-OVERLAP both reference an "MTAG `--overlap`" flag. **MTAG does not expose a `--overlap` argument.** It exposes `--residcov_path` (the path to a pre-computed residual-covariance matrix in `.txt` whitespace-delimited or `.npy` format) and the boolean toggle `--no_overlap` (zeros off-diagonal residual-covariance). The user-intent mapping is unambiguous: M2 will pass the LDSC bivariate-intercept matrix as `--residcov_path` so MTAG skips its internal LDSC-call step. This is verified against `mtag.py::_read_matrix()` which checks the `.npy` / `.txt` extensions and rejects everything else; the matrix is then assertion-checked against the per-trait input-list dimension. The reducer output `bivariate_intercept_matrix_2026-04-M2.tsv` is TSV (tab-separated) — MTAG accepts whitespace-delimited but the planner must emit a header-less, index-less, **whitespace-delimited (space or tab works since `np.loadtxt` is tolerant) numeric-only matrix file** alongside the human-readable indexed matrix.

Phase reuses M1 patterns extensively: `m1_raw_glob.DEFERRED_SENTINEL` universal `.deferred`-marker guard for skipped (trait × stratum) cells; `m1_trait_keys` deterministic enumeration of D-16 keys (M2 needs an analogous `m2_stratum_keys` helper that emits the 9-trait × 3-stratum = 27-cell grid filtered by `qc_status` from `trait_inventory.yaml`); the per-rule conda env partitioning convention from `envs/m1-{download,harmonize,munge,ldsc-rg,qc}.yml` (M2 needs `envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml`); the Snakemake star-pattern + reducer pattern from `m1_ldsc_rg.smk` (M2 D-M2-01 simply re-runs that machinery against the expanded ~26-trait munged set); the SHA-256 freeze pattern from `freeze_sha256_manifest.py` (M2 closeout produces `sha256_manifest_m2_frozen.tsv`); the Quarto QC fallback from `m1_qc_index.qmd` + `render_qc_html_minimal.py` (optional M2 QC report).

**Primary recommendation:** Plan 6 waves — (Wave 0) test scaffolding + 6 conda envs + AFR PLINK reference panel build (BLOCKING — `data/reference/ldsc/1000G_EUR_Phase3_plink/` exists but no AFR PLINK; must be derived from `data/raw/1kg/vcf/chr*.vcf.gz` + `data/raw/1kg/AFR.samples`) + GWAS Catalog snapshot fetch + MTAG install + mtCOJO + bedtools availability check + CPASSOC unit tests; (Wave 1) D-M2-01 LDSC matrix refire (~26 trait expansion via DEF-M1-03-02 closure) — pure re-execution of `m1_munge_all` + `m1_ldsc_rg_all_stars` + `m1_ldsc_rg_reduce` against the expanded harmonized set; (Wave 2) MTAG 3 stratum runs (EUR, AFR, TRANS) consuming the M2 matrix as `--residcov_path` + matrix-slicing helper; (Wave 3) CPASSOC Python reimplementation + 3 stratum runs against the same matrix slices; (Wave 4) PLINK clumping + mtCOJO sensitivity + region-union BED; (Wave 5) Class 1 novelty calling against catalog v_lock_M2 + SHA-256 freeze + post-M3-rerun queue + closeout. TDD discipline matches M1 (RED then GREEN, atomic commits per task).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-M2-01 LDSC matrix scope expand to ~26 traits via DEF-M1-03-02 refire before MTAG fires.**
Re-fire `m1_munge_all` + `m1_ldsc_rg_all_stars` + `m1_ldsc_rg_reduce` against the expanded harmonized inventory (GLGC + Wuttke landings post-m1-03 close). The 12×12 frozen matrix at `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` stays as OSF posting record. The ~26×26 matrix lands at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` and `.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv`. Wave 0 of M2 plan refires m1-03 wave with `--reason=DEF-M1-03-02-expansion`.

**D-M2-02 AFR LD reference — provisional 1000G AFR (N=661) for M2; committed re-run after M3 AoU AFR LD lands.**
Use 1000G Phase 3 AFR (N=661) as the LD reference for M2 AFR-stratum PLINK clumping AND for AFR LDSC ld-score regression where AoU LD is unavailable. Document explicitly as PROVISIONAL in DECISIONS.md (will become DEC-2026-04-25-03). Output filenames carry an `LD-1000G-AFR` token. M2 plan adds a closing task that emits a "post-M3 re-run trigger" entry into `.planning/m2_post_m3_rerun_queue.tsv`.

**D-M2-03 MTAG trait grouping — three per-ancestry + TRANS mega-runs (EUR-9, AFR-9, TRANS-9).**
Run MTAG three times: once over all available traits in EUR (using each trait's `.EUR.*` munged file), once over AFR, once over TRANS (or `.MULTI.*` for GBMI). Three sets of MTAG-novel hit lists feed into the union region BED. Snakemake rule `mtag_run` parameterized by `{stratum}` ∈ {EUR, AFR, TRANS}. The `--sumstats` arg builds a comma-list of munged paths; the `--residcov_path` arg consumes the slice of the ~26-trait LDSC intercept matrix matching the input traits.

**D-M2-04 CPASSOC build — Python reimplementation, LDSC intercept matrix as cohort-correlation input.**
Reimplement Zhu 2015's SHom and SHet test statistics directly in Python (~50–100 LoC at `src/python/cpassoc.py`), with the LDSC pairwise bivariate-intercept matrix as the cohort-correlation matrix R. Formulas: SHom = `z' R^-1 z`; SHet = `z' (R^-1 - R^-1 1 (1' R^-1 1)^-1 1' R^-1) z`. Pytest fixtures: 100-SNP synthetic z-score matrix; cross-check against Zhu 2015 paper Table 1 example values where reproducible. Snakemake rule `cpassoc_run` parameterized by `{stratum}` per D-M2-03 grouping; outputs to `data/processed/cpassoc/{stratum}/`.

**D-M2-05 GWAS Catalog v_lock — snapshot at M2 kickoff (~2026-04-26) + refresh at M5.**
Pull a fresh GWAS Catalog snapshot at M2 kickoff. Lock URL + ETag + SHA-256 + fetch-date in `data/catalogs/catalog_lock_manifest.tsv` (new row keyed `gwas_catalog.v_lock_M2`). Compute interim Class 1 novelty for `joint_signal_novel.tsv` using this snapshot. At M5, when M5-deferred catalog rows lock, re-run the novelty filter; report diff as a follow-up OSF update. M2 Wave 0 includes a `download_gwas_catalog_M2` task.

**D-M2-06 Trait stratum selection — strict ancestry match, skip-with-doc when missing.**
EUR cell uses `.EUR.*` munged sumstats; AFR cell uses `.AFR.*`; TRANS cell uses `.TRANS.*` (or `.MULTI.*` for GBMI). Traits without an ancestry stratum (e.g. CKDGen 2019 has no AFR-specific release; Aragam 2022 CAD has no AFR-specific stratum) are skipped from the corresponding MTAG/CPASSOC run with a documented gap entry in `m2-deferred-items.md` and a row in `data/processed/mtag/{stratum}/skipped_traits.tsv`.

**D-M2-07 MTAG max_FDR threshold — Turley default 0.05.**
Apply MTAG `--max-FDR-threshold 0.05` per Turley 2018 default. Hits with `max_FDR < 0.05` qualify for downstream Class 1 novelty consideration; loci above are filtered out before novelty calling. Note: in MTAG argparse this corresponds to a max-FDR threshold; the closely-related `--p_sig` defaults to 5e-8.

**D-M2-08 mtCOJO sensitivity scope — all loci with extreme overlap (gcov_int > 0.1).**
Apply mtCOJO (Zhu 2018) to every MTAG-novel locus where the bivariate-intercept matrix `gcov_int` with any contributing trait exceeds 0.1 (Turley 2018 §"sample overlap" recommended threshold). Snakemake rule `mtcojo_run` consumes the MTAG-novel hit list, joins on the LDSC intercept matrix, filters to loci where any pair has `gcov_int > 0.1`, and runs mtCOJO per-locus. Output sensitivity table at `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv`.

**D-M2-09 Region union policy — strict union of clumped + MTAG-novel + CPASSOC-novel leads, ±1 Mb windows, merged.**
Discovery region BED = strict union of: per-(trait × ancestry) PLINK clumped lead variants (p < 5e-8, r² < 0.01, 1 Mb clump window); MTAG-novel lead variants from each stratum run; CPASSOC-novel lead variants from each stratum run. Each lead carries a ±1 Mb window. Bedtools merge collapses overlapping intervals. Expected output: 1,500–3,000 regions per amendment text. Each region carries a provenance tag set so downstream M4 can prioritize Tier 1 = MTAG ∩ CPASSOC regions.

**D-M2-10 Sample-overlap correction scope — full LDSC pairwise intercept matrix as universal residual-covariance.**
MTAG `--residcov_path` (CONTEXT.md says "--overlap" colloquially — see Pitfall 1 below) consumes the full ~26×26 LDSC bivariate-intercept matrix slice (D-M2-01 refire output) for the universal cohort-overlap correction. Off-diagonal pairs include all overlap structure: UKB ∩ MVP, deCODE ∩ HUNT, ARIC ∩ FHS, GIANT ∩ 23andMe, GLGC ∩ ICBP, etc., as encoded by the bivariate intercepts. No off-diagonal zeroing or thresholding. The reducer `reduce_ldsc_rg_matrix.py` already enforces symmetry and diag=1.0; M2 reuses without modification.

### Claude's Discretion

- Exact wave decomposition and task atomicity (research recommends 6 waves — see "Suggested Plan Decomposition" below).
- Snakemake rule layout across 6 new `.smk` files: `m2_ldsc_refire.smk` (or simply re-use of m1_munge.smk + m1_ldsc_rg.smk via Wave 1 task), `m2_mtag.smk`, `m2_cpassoc.smk`, `m2_clumping.smk`, `m2_mtcojo.smk`, `m2_regions.smk`, `m2_novelty.smk`.
- Conda env partitioning across `envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml`.
- LSF queue selection per rule (follow `feedback_lsf_queues`: serial=5760min, long=14400min, standard=2880min ceilings).
- CPASSOC matrix-conditioning policy (research recommends `numpy.linalg.pinv` with default rcond=1e-15 + a configurable ridge regularization fallback when condition number > 1e6).
- mtCOJO TRANS-stratum LD reference (research recommends 1000G EUR per the convention that trans-ancestry meta-analyses tend to be EUR-dominant; a 1000G AFR sensitivity check on TRANS-stratum mtCOJO-novel loci is a candidate Wave 4 robustness add).
- Class 1 novelty implementation (single Python module `call_class1_novelty.py` joining MTAG hits + CPASSOC hits + GWAS Catalog v_lock + ±500 kb BedTool intersect).
- Per-stratum CPASSOC R matrix slicing (research confirmed PSD is preserved — see Q7 resolution below).
- M2 closeout SHA-256 manifest scope (raw catalog bytes + matrix + region BED + novelty TSV + skipped-traits log).
- Quarto M2 QC report (optional — MTAG QQ plots, CPASSOC SHom/SHet histograms, region density maps; if Quarto unavailable use the M1 minimal HTML fallback pattern).

### Deferred Ideas (OUT OF SCOPE)

- Class 2 (AFR-specific), Class 3 (secondary-signal), Class 4 (pleiotropy-coloc), Class 5 (functional-mechanism) novelty — all M4–M5 scope per Amendment §7.1.
- HyPrColoc 5-trait shared-architecture run — M4 scope.
- Cluster-based MTAG run as robustness check (rg ≥ 0.4 trait clusters) — candidate M5/M6 robustness phase.
- mtCOJO on all MTAG-novel loci regardless of overlap severity — D-M2-08 thresholds at gcov_int > 0.1.
- 45×45 LDSC matrix expansion — gated on Carter resume queue (DIAMANTE cookies, GBMI Wix, Loh D-01, MAGIC EUR re-fetch); future M2-extension phase if needed.
- Borzoi / Enformer functional-mechanism scoring on union regions — M5 scope.
- Two-stage coloc + SuSiE-RSS fine-mapping on union regions — M4 scope.
- Locus-to-gene scoring — M5 scope.
- AoU AFR WGS LD panel build — M3 scope per AOU-LD-PIPELINE.md.

### NON-goals for M2 (per phase description; do NOT research or plan)

- Running coloc / SuSiE-RSS / HyPrColoc.
- Running PolyFun.
- Running L2G / Borzoi / Enformer.
- Class 2/3/4/5 novelty calling.
- Hold-out replication.
- Manuscript figures.
- AoU Workbench compute.

All M3+.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-MTAG-OVERLAP | MTAG with `--overlap` (colloquial; actual flag `--residcov_path`) using the LDSC pairwise intercept matrix; `max_FDR` filter per Turley 2018; mtCOJO sensitivity on extreme-overlap loci. | D-M2-01 (matrix refire) + D-M2-03 (3 stratum runs) + D-M2-07 (max_FDR=0.05) + D-M2-08 (mtCOJO at gcov_int > 0.1) + D-M2-10 (universal correction). Q1 + Q4 + Q8 below resolve flag-name + LD-reference + output-schema details. |
| REQ-CPASSOC-ORTHOGONAL | CPASSOC SHom/SHet as orthogonal joint-signal test for cross-method corroboration. | D-M2-04 (Python reimplementation with LDSC intercept matrix as R input). Q2 + Q7 below resolve matrix-conditioning + per-stratum slicing. Pattern A reused for skip-with-doc on missing strata. |
| REQ-NOVELTY-CLASS-1 | `joint_signal_novel.tsv` with one row per claimed locus; columns for MTAG p, CPASSOC p, max single-trait p, nearest GWAS Catalog v_lock entry, confidence tier (high-confidence subset = MTAG ∩ CPASSOC). | D-M2-05 (catalog v_lock_M2) + D-M2-07 (max_FDR threshold) + Q5 below (catalog URL + ETag stability) + Q6 below (region merge tolerance). |
| REQ-OSF-PREREG | Already satisfied 2026-04-25 by OSF posting at osf.io/az52u/files/k8w7n; M2 inherits. | Gate-release commit d55c1d1 — M2 may now commit. No M2 task required for this REQ. |
| REQ-SNAKEMAKE-CI | M2 Snakemake rules included in main pipeline; smoke-test target added. | Same convention as M1 — extend `tests/toy_3locus/` with a M2 smoke target. Reuse `envs/m2-*.yml` partitioning convention. |
| REQ-CATALOG-VERSION-LOCK | `catalog_lock_manifest.tsv` row `gwas_catalog.v_lock_M2`. | D-M2-05 + Q5 resolution (catalog URL = `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip` per latest EBI directory listing). |
</phase_requirements>

## Open Questions Resolved

### Q1 — MTAG `--overlap` matrix file format → ACTUAL FLAG IS `--residcov_path`

**Status:** RESOLVED with terminology correction. **HIGH confidence.**

**Finding:** [VERIFIED: github.com/JonJala/mtag/blob/master/mtag.py via WebFetch + WebSearch cross-check with Turley 2018 PMC5805593] **MTAG does NOT have a `--overlap` argument.** The CONTEXT.md decisions D-M2-10 + REQ-MTAG-OVERLAP use "--overlap" as colloquial shorthand. The actual MTAG CLI exposes:

- `--residcov_path <PATH>` — Pre-computed residual covariance matrix (Σ-hat in Turley notation). Format: `.npy` or whitespace-delimited `.txt`. Loaded via `_read_matrix(file_path)` which checks `file_path[-4:]` and rejects extensions other than `.npy` / `.txt`.
- `--gencov_path <PATH>` — Pre-computed genetic covariance matrix (Ω-hat). Same format constraints.
- `--no_overlap` — Boolean flag; zeros off-diagonal Σ-hat (assume independent samples).
- `--p_sig <FLOAT>` — P-value threshold (default 5e-8). Note: max-FDR is not a single argument named `--max-FDR-threshold`; it's calculated post-hoc via the maxFDR Tutorial 3 logic. **D-M2-07 phrasing "MTAG `--max-FDR-threshold 0.05`" needs verification** — see Open Questions for Carter §1 below.

**Matrix file schema for `--residcov_path`:**
- Square symmetric `K × K` matrix where `K` = number of input GWAS traits in `--sumstats` comma list.
- **Whitespace-delimited (space or tab works since `np.loadtxt` is tolerant)** OR `.npy` numpy serialized array.
- **No header row, no row index** — pure numeric matrix. The `np.loadtxt` call is unprefixed, so any leading text is parsed as data.
- Row/column ordering must match the order of traits in the `--sumstats` comma-separated list.
- Diagonal = 1.0 (LDSC h2 intercept of self-pair). Off-diagonal = bivariate `gcov_int`.
- Dimension assertion: `args.omega_hat.shape[0] == args.omega_hat.shape[1] == Zs.shape[1] == args.sigma_hat.shape[0] == args.sigma_hat.shape[1]` — fires AFTER load. The planner must emit a **bare numeric matrix** AND ensure trait order in MTAG `--sumstats` exactly matches the matrix row/col order.

**Critical contract for the slice helper:** The reducer's `bivariate_intercept_matrix_2026-04-M2.tsv` is human-readable (header row of trait keys + index column). The MTAG matrix-slice helper (new module `src/python/build_mtag_residcov_slice.py`) must:
1. Read the indexed wide TSV.
2. Filter rows/cols to the trait keys present in the stratum (e.g. all `.EUR.*` keys for EUR-9 run).
3. Sort the slice rows and columns by the same canonical trait-key order used in the `--sumstats` comma list.
4. Emit a **header-less, index-less, whitespace-delimited** `.txt` to `data/processed/mtag/{stratum}/residcov.txt` (or equivalent `.npy`).
5. Emit a sidecar JSON `data/processed/mtag/{stratum}/residcov.trait_order.json` listing the canonical trait order so the planner can construct the matching `--sumstats` arg deterministically.

### Q2 — CPASSOC R inversion conditioning

**Status:** RESOLVED. **MEDIUM-HIGH confidence.**

**Finding:** [CITED: Zhu 2015 *AJHG* 96(1):21–36 + RESEARCHGATE figs review] Zhu 2015 does NOT specify a numerical-conditioning treatment for near-singular R blocks. The recommended Python implementation:

1. **Default path:** `numpy.linalg.pinv(R, rcond=1e-15)` — Moore-Penrose pseudoinverse, drops singular values below `rcond × max(s)`. This is the standard treatment for symmetric positive-semidefinite matrices that are theoretically PSD but numerically rank-deficient. Equivalent to `scipy.linalg.lstsq(R, np.eye(K), cond=1e-15)[0]`.
2. **Conditioning probe:** Compute `numpy.linalg.cond(R)` once per stratum at slice time. If `cond(R) > 1e6`, log a WARN and engage ridge regularization:
3. **Ridge fallback:** `R_ridged = R + λ × I` where `λ = 1e-4 × trace(R) / K`. This is the principled small-ridge regularization matching the bivariate-intercept matrix scale (intercepts are O(1)).
4. **Validation:** unit test against the analytical case where R = I (no overlap) — SHom should reduce to `Σ z_k²` (chi-square df=K), SHet should reduce to chi-square df=K-1 of the centered sum.

**Why pinv over lstsq:** Both give the Moore-Penrose pseudoinverse for symmetric matrices, but `pinv` is purpose-built and ~10% faster for small K. `scipy.linalg.lstsq` is the right tool for non-symmetric or rectangular systems; for our K×K symmetric R, pinv wins.

**Code pattern (D-M2-04 implementation):**

```python
# Source: src/python/cpassoc.py (NEW)
import numpy as np

def _safe_inverse(R: np.ndarray, ridge_floor: float = 1e-4) -> np.ndarray:
    """Pseudoinverse with conditional ridge fallback for near-singular R."""
    cond = np.linalg.cond(R)
    if cond > 1e6:
        K = R.shape[0]
        lam = ridge_floor * np.trace(R) / K
        R = R + lam * np.eye(K)
    return np.linalg.pinv(R, rcond=1e-15)

def cpassoc_shom(z: np.ndarray, R: np.ndarray) -> np.ndarray:
    """SHom test statistic per SNP. Returns chi-square df=K values.

    z: (n_snps, K) z-score matrix
    R: (K, K) cohort-correlation matrix (LDSC bivariate intercept)

    Returns: (n_snps,) chi-square values; df = K
    """
    Rinv = _safe_inverse(R)
    return np.einsum("ij,jk,ik->i", z, Rinv, z)  # z_i' R^-1 z_i per SNP

def cpassoc_shet(z: np.ndarray, R: np.ndarray) -> np.ndarray:
    """SHet test statistic per SNP. Returns chi-square df=K-1 values."""
    Rinv = _safe_inverse(R)
    K = R.shape[0]
    one = np.ones(K)
    denom = one @ Rinv @ one  # scalar
    proj = Rinv - np.outer(Rinv @ one, one @ Rinv) / denom  # (K, K)
    return np.einsum("ij,jk,ik->i", z, proj, z)
```

**Pitfall reference:** the LDSC reducer's `bivariate_intercept_matrix_2026-04.tsv` already passes `validate_self_consistency` (symmetry within 1e-6 + diag~1.0). So R is guaranteed symmetric on input; M2 doesn't need to symmetrize defensively but planner can add a `R = (R + R.T) / 2` safety step at micro-cost.

### Q3 — PLINK clumping memory budget at chr-level on LSF

**Status:** RESOLVED. **HIGH confidence.**

**Finding:** [CITED: PLINK 1.9 docs at cog-genomics.org/plink/1.9/postproc + biostars community reports + Hail batch cookbook] Per-chromosome PLINK 1.9 `--clump` invocations are the canonical batching strategy for whole-genome clumping. Memory + time budget:

| Parameter | Value | Source |
|-----------|-------|--------|
| Memory per chr1 (largest) | ~1500 MB peak | biostars + community LSF logs |
| Memory per chrY (smallest autosome) | ~200 MB | Hail batch cookbook (1Gi default) |
| Memory budget — recommend | `mem_mb=4000` | 2.5× peak headroom; fits LSF standard queue (max 5000 MB per slot) |
| Wall time per (trait × ancestry × chr) | 30 sec – 5 min | Empirical for HM3 SNP density at p < 5e-8 |
| Total invocations | ~26 traits × 3 strata × 22 chr = ~1716, less skipped | D-M2-06 skip-with-doc reduces actual count |
| Total wall time (parallel × 50 LSF slots) | ~3 hours | (1716 × 2 min) / 50 ≈ 70 min wall + queue waits |

**Recommended Snakemake rule shape:**

```python
rule m2_plink_clump:
    """Per-(trait × ancestry × chr) clumping. Rule fires only when the
    matching munged file exists; skipped cells emit a .skipped sentinel.
    """
    input:
        sumstats = "data/processed/sumstats_harmonized/{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz",
        bed = "data/reference/ldsc/1000G_{ldpop}_Phase3_plink/1000G.{ldpop}.QC.{chr}.bed",
        bim = "data/reference/ldsc/1000G_{ldpop}_Phase3_plink/1000G.{ldpop}.QC.{chr}.bim",
        fam = "data/reference/ldsc/1000G_{ldpop}_Phase3_plink/1000G.{ldpop}.QC.{chr}.fam",
    output:
        clumped = "data/processed/clumping/{ancestry}/{trait}.{ancestry}.{consortium}.{year}.LD-1000G-{ldpop}.chr{chr}.clumped",
    params:
        bfile = "data/reference/ldsc/1000G_{ldpop}_Phase3_plink/1000G.{ldpop}.QC.{chr}",
        out_prefix = "data/processed/clumping/{ancestry}/{trait}.{ancestry}.{consortium}.{year}.LD-1000G-{ldpop}.chr{chr}",
    resources:
        mem_mb = 4000,        # Q3: 4000 MB per chr is safe across all 22 autosomes
        runtime = 60,         # 1 hour wall cap; standard queue (LSF max 2880)
    threads: 2
    conda: "../../../envs/m2-clumping.yml"
    shell:
        r"""
        plink --bfile {params.bfile} \
              --clump {input.sumstats} \
              --clump-snp-field SNP --clump-field P \
              --clump-p1 5e-8 --clump-p2 1 --clump-r2 0.01 --clump-kb 1000 \
              --memory 3500 \
              --out {params.out_prefix}
        # Touch output even if no clumps emitted (PLINK skips writing if empty)
        if [ ! -f {output.clumped} ]; then touch {output.clumped}; fi
        """
```

**GCTA-COJO equivalent question:** GCTA `--cojo-slct` performs stepwise model-selection conditional analysis, not LD clumping. It is NOT a faster substitute for `plink --clump`. PLINK 2.0 does not yet implement `--clump` (verified 2026-04-25 — Christopher Chang reply on plink2-users group). Use **PLINK 1.9 `--clump`** as the canonical tool. Already-installed at `envs/plink.yml` (existing).

**Empirical justification for r²<0.01, kb 1000, p1 5e-8:** OSF amendment §7.1 Class 1 spec + REQ-NOVELTY-CLASS-1 demand p < 5e-8 and ±500 kb GWAS-Catalog comparison; clump-kb 1000 (1 Mb) is the Turley 2018 + Pickrell 2016 convention; r²<0.01 is the strictest of the standard tiers (some studies use 0.001 for finer resolution but 0.01 is the Turley default).

### Q4 — mtCOJO reference genotype panel for TRANS-stratum runs

**Status:** RESOLVED with provisional choice + sensitivity-check addendum. **MEDIUM confidence.**

**Finding:** [CITED: Zhu 2018 *Nat Commun* 9:224 mtCOJO methods §"LD reference"] Zhu 2018 does NOT define a recommended trans-ancestry LD reference. The mtCOJO method assumes cohort + LD-reference are population-matched; trans-ancestry meta-analyses break this assumption uniformly. The defensible choices for TRANS:

| Option | Reasoning | Adopted? |
|--------|-----------|----------|
| 1000G EUR | Trans-ancestry meta-analyses are typically EUR-dominant by sample size; using EUR LD as default produces the "right" answer at most loci where EUR effects dominate. | **PRIMARY** — recommended default |
| 1000G AFR | More conservative for AFR-driven loci; would systematically over-correct EUR-driven loci. | Sensitivity check on TRANS-stratum mtCOJO-novel loci |
| Population-stratified meta of 1000G EUR + AFR + EAS | Mixture LD; not implemented in mtCOJO | Out of scope |

**Recommendation:** TRANS mtCOJO uses 1000G EUR PLINK. Add a Wave 4 sensitivity task that re-runs TRANS mtCOJO with 1000G AFR LD on the same MTAG-novel loci; report concordance in `mtcojo_sensitivity.tsv` as `trans_ld_panel_concordance` column. If concordance is high (>95% pass-pass) the EUR-default is fine; if it diverges, Carter receives an interpretation flag for the discussion section. **This is a robustness add, not blocking.**

### Q5 — GWAS Catalog ETag stability and download mechanism

**Status:** RESOLVED. **HIGH confidence.**

**Finding:** [VERIFIED: WebFetch of `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/` 2026-04-25] The canonical URL set:

| Artifact | URL | Size | Last-Modified |
|----------|-----|------|---------------|
| All-associations TSV (full) | `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip` | 56 MB | 2026-04-21 13:50 UTC |
| Associations TSV (split — 1 row per association) | `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-split.zip` | 55 MB | 2026-04-21 13:50 UTC |
| Studies TSV | `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-studies.tsv` | 69 MB | 2026-04-21 13:50 UTC |
| Ancestry TSV | `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-ancestry.tsv` | 47 MB | 2026-04-21 13:50 UTC |
| EFO trait mappings | `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-efo-trait-mappings.tsv` | 19 MB | 2026-04-21 13:50 UTC |

**Important deviation from CONTEXT.md scope hint:** CONTEXT.md mentions "EBI all-associations TSV ~500 MB". The actual M2 download is `gwas-catalog-associations-full.zip` at ~56 MB (compressed) / ~500 MB unzipped. Plan rule downloads the .zip, computes SHA-256 of the zip bytes (matches what's published on the EBI server), unzips inside the rule.

**ETag stability:** [LOW] EBI FTP/HTTPS does NOT consistently expose strong ETag headers — they emit `Last-Modified` (2026-04-21 13:50 above) which is sufficient for SHA-256-pinned reproducibility. The `catalog_lock_manifest.tsv` schema already includes `fetched_date` + `sha256` columns; the `etag` field can stay empty for GWAS Catalog rows (use `last_modified` instead, populated from the HTTP `Last-Modified` header captured at fetch time).

**Recommended Wave 0 task:** `download_gwas_catalog_M2` runs:

```bash
URL="https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/gwas-catalog-associations-full.zip"
DEST="data/catalogs/gwas-catalog-associations-full.zip"
LAST_MOD=$(curl -sI "$URL" | grep -i "^last-modified" | sed 's/^[^:]*: //; s/\r//g')
curl -fsSL --retry 3 -o "$DEST" "$URL"
SHA=$(sha256sum "$DEST" | awk '{print $1}')
SIZE=$(stat --printf='%s' "$DEST")
# Append row to catalog_lock_manifest.tsv:
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "gwas_catalog.v_lock_M2" \
    "$(date -u -d "$LAST_MOD" +%Y-%m-%d)_full_release" \
    "$URL" \
    "$SHA" \
    "$(date -u +%Y-%m-%d)" \
    "$SIZE" \
    "M2-locked" \
    >> data/catalogs/catalog_lock_manifest.tsv
```

**Reproducibility note:** [VERIFIED via project memory `feedback_url_rot_workarounds`] EBI URLs are generally stable but not always — Carter has prior experience with Broad / UCLA Box / CNCR / EBI URL rot. The catalog_lock_manifest pinning is the durable artifact; the URL itself is the recovery hint, not the canonical record.

### Q6 — Region merge tolerance for D-M2-09

**Status:** RESOLVED. **HIGH confidence.**

**Finding:** [CITED: bedtools merge documentation v2.31] `bedtools merge` default behavior collapses any overlapping interval (1 bp overlap suffices). The user-facing flag `-d <int>` extends merge tolerance: `-d 0` (default) requires actual overlap; `-d N` merges intervals within N bp of each other.

**Recommendation:** D-M2-09's "strict union" maps directly to **default `bedtools merge` (no `-d` flag)** — any overlap collapses. The ±1 Mb windows around lead variants will heavily overlap within dense GWAS regions (e.g. 16q12 BMI ~50 lead variants would all collapse to one ~1.5 Mb mega-region), which is exactly the desired behavior for the M3 LD priority and M4 fine-mapping consumer.

**Sensitivity check option (NOT blocking):** Run a second merge pass with `-d 50000` (50 kb tolerance) and compare region counts. If the 50 kb-tolerant pass yields significantly fewer regions than strict, the strict pass produced near-touching disjoint regions that should probably be one. This is a Wave 4 robustness add, not blocking.

**No stranded merge needed:** Genomic regions are unstranded for fine-mapping purposes (LD is symmetric across strands). Skip `-s` flag.

**Output schema for `union_region_list.bed`:**

```
chr1   12345678   13345678   region_001   .   .   {"clump":["bmi.EUR","cad.EUR"],"mtag":["EUR"],"cpassoc":["EUR"],"max_p":1.2e-15}
chr1   ...
```

4-column standard BED (chr, start, end, name) + 3 extension columns (score, strand, JSON provenance). The JSON provenance encodes which methods + strata contributed; M4 reads this to set Tier 1 priority (regions where MTAG ∩ CPASSOC both contributed).

### Q7 — Per-stratum CPASSOC R matrix slicing

**Status:** RESOLVED. **HIGH confidence.**

**Finding:** [VERIFIED: linear algebra theorem — principal submatrices of a PSD matrix are PSD] Slicing the full ~26×26 LDSC intercept matrix to the EUR-only or AFR-only or TRANS-only subset preserves positive-(semi)-definiteness. The full matrix is PSD by construction (it's a covariance matrix), and any principal submatrix (rows AND columns indexed by the same subset) of a PSD matrix is PSD. Therefore CPASSOC's `R^-1` is well-defined on the slice (modulo the same conditioning concerns as Q2).

**Implementation contract:** The CPASSOC slice helper (new module `src/python/build_cpassoc_R_slice.py` — or inlined into `cpassoc.py`) takes the full ~26×26 matrix + the stratum-specific trait-key list and returns the principal submatrix:

```python
def slice_R_for_stratum(full_R: pd.DataFrame, stratum_keys: list[str]) -> np.ndarray:
    """Return the K×K principal submatrix of full_R for the K stratum traits.

    full_R: pd.DataFrame indexed by all ~26 trait keys (rows) × all ~26 (cols)
    stratum_keys: list of trait keys in the stratum (e.g. EUR-9 = 9 keys)

    Returns: numpy array of shape (K, K), preserves PSD.
    """
    K_keys = [k for k in stratum_keys if k in full_R.index]
    R_slice = full_R.loc[K_keys, K_keys].values
    # Defensive symmetry guard (LDSC reducer already passes; safety only):
    R_slice = (R_slice + R_slice.T) / 2.0
    return R_slice
```

**Validation:** unit test — verify `numpy.linalg.eigvalsh(R_slice).min() >= -1e-10` (PSD with floating-point tolerance) for all 3 stratum slices.

### Q8 — mtCOJO output schema and joining keys

**Status:** RESOLVED. **MEDIUM confidence.**

**Finding:** [CITED: GCTA `--mtcojo-file` documentation at yanglab.westlake.edu.cn/software/gcta/#mtCOJO] mtCOJO emits one output file per run (per (target_trait, covariate_traits) tuple), NOT one-per-locus. The output is a multi-column TSV with columns `SNP, A1, A2, freq, b, se, p, N, b_cojo, se_cojo, p_cojo` where:
- `SNP` / `A1` / `A2` / `freq` — variant + allele info
- `b` / `se` / `p` / `N` — original GWAS effect from the target trait
- `b_cojo` / `se_cojo` / `p_cojo` — mtCOJO-conditional effect after sample-overlap correction

**Joining keys for sensitivity table:** Join on `SNP` (rsID) for the trivial case; if the MTAG output uses chr:pos:ref:alt synthetic IDs (Aragam 2022 / GIGASTROKE 2022 path), use `chr:pos` as the join key after splitting both rsID and synthetic IDs (the `_chrpos_key` helper in `munge_sumstats_ldsc.py` handles this).

**Sensitivity table schema (D-M2-08 deliverable):**

```
locus_id  | trait     | mtag_p_original  | mtcojo_p  | max_overlapping_intercept | sensitivity_flag
rs1421085 | bmi       | 1.2e-15          | 3.4e-12   | 0.42 (with sbp)           | PASS
...
```

`sensitivity_flag` is PASS if `mtcojo_p < 5e-8`, WARN if `5e-8 <= mtcojo_p < 1e-5` and the original was significant, FAIL if `mtcojo_p > 1e-5` (sample-overlap-driven false positive).

**One file per stratum:** mtCOJO is invoked per (stratum, target_trait, covariate_traits) — for a 9-trait EUR run, that's 9 mtCOJO invocations (each trait conditioned on the other 8). Output files: `data/processed/mtcojo/EUR/{trait}.EUR.mtcojo.cojo` per-target-trait, plus an aggregator `mtcojo_sensitivity.tsv` joining MTAG-novel loci with the per-target conditional p-values.

## M1 Patterns to Reuse

### A. `m1_raw_glob.DEFERRED_SENTINEL` universal `.deferred`-marker guard

**File:** `src/python/m1_raw_glob.py` line 38.

**Pattern:** When an upstream artifact is absent (cookie-pending, accession-pending, derivation-pending), the resolver returns the sentinel string `"__DEFERRED__"`. Every consumer rule's shell prelude guards with:

```bash
if [ "{params.raw}" = "__DEFERRED__" ] || [ -f "{input}.deferred" ]; then
    mkdir -p $(dirname {output})
    touch {output}.deferred
    touch {output}
    echo "DEFERRED: upstream input absent"
    exit 0
fi
```

**M2 reuse:** Adapt for skipped (trait × stratum) cells per D-M2-06. New module `src/python/m2_stratum_keys.py` enumerates the 9-trait × 3-stratum grid, returns `__SKIPPED__` (or a stratum-specific sentinel) when no `.{stratum}.*` munged file exists for a trait. M2 rules consume the sentinel with the same shell-prelude guard pattern.

### B. `m1_trait_keys` dynamic trait enumeration

**File:** `src/python/m1_trait_keys.py`.

**Pattern:** Reads `SUMSTATS-UPGRADE.tsv`, applies TOKEN_MAP, appends Evangelou SBP-EUR, dedupes + sorts, writes one trait key per line. Defensive bound check (40 ≤ N ≤ 50) catches inventory drift.

**M2 reuse:** New module `src/python/m2_stratum_keys.py` with analogous structure. Reads `config/trait_inventory.yaml` (47 cells × 24 fields), filters cells where:
- `qc_status` is not `MISSING` AND `harmonized_path` exists on disk
- `ancestry` matches the requested stratum (EUR / AFR / TRANS)

Emits one (stratum, trait_key) pair per line per stratum. Defensive bound: 7 ≤ N ≤ 9 traits per stratum (skip-with-doc per D-M2-06 may drop 1-2 traits in AFR; TRANS is sparser).

```python
# src/python/m2_stratum_keys.py (NEW)
"""M2 deterministic (stratum, trait_key) enumeration helper.

Reads config/trait_inventory.yaml. For each stratum {EUR, AFR, TRANS}, returns
the list of trait keys whose harmonized + munged outputs exist and match the
requested ancestry.

Pairs with M2 Snakemake `--config stratum=EUR` to emit the comma-separated
trait list for MTAG --sumstats and the matching residcov_path slice.
"""
from __future__ import annotations
import yaml
from pathlib import Path

STRATA = ("EUR", "AFR", "TRANS")
_MIN_PER_STRATUM = 5  # AFR is the sparsest; below this, abort
_MAX_PER_STRATUM = 9

def keys_for_stratum(inventory_path: Path, stratum: str) -> list[str]:
    """Return the trait keys with available outputs for the given stratum."""
    inv = yaml.safe_load(inventory_path.read_text())["traits"]
    keys = []
    for key, entry in inv.items():
        if entry.get("ancestry") != stratum:
            continue
        if entry.get("qc_status") == "MISSING":
            continue
        if not Path(entry.get("munged_path", "")).exists():
            continue
        keys.append(key)
    keys = sorted(set(keys))
    assert _MIN_PER_STRATUM <= len(keys) <= _MAX_PER_STRATUM, (
        f"m2_stratum_keys: {stratum} has {len(keys)} keys, "
        f"expected {_MIN_PER_STRATUM}<=N<={_MAX_PER_STRATUM}"
    )
    return keys
```

### C. Snakemake star-pattern rule from `m1_ldsc_rg.smk`

**File:** `src/snakemake/rules/m1_ldsc_rg.smk`.

**Pattern:** Path-parameterized roots from `config["paths"]`; project-root + `src/python` PYTHONPATH discovery; deterministic trait-keys file driven by build-helper rule; per-focal-idx star rule + aggregator + reducer rule.

**M2 reuse:** Apply identically to `m2_mtag.smk`, `m2_cpassoc.smk`, `m2_clumping.smk`. The Wave 1 D-M2-01 LDSC matrix refire is a **direct re-execution of `m1_munge_all` + `m1_ldsc_rg_all_stars` + `m1_ldsc_rg_reduce` rules** — the only change is that `m1_trait_keys.py` now reads the expanded inventory (the GLGC + Wuttke files that landed post-m1-03 close are already in `trait_inventory.yaml`). The reducer auto-rebuilds the matrix at the new dimension.

**Critical:** The D-M2-01 refire output filename must be `bivariate_intercept_matrix_2026-04-M2.tsv` (per CONTEXT) — NOT overwriting the M1-frozen `bivariate_intercept_matrix_2026-04.tsv`. Add a Wave 1 task that copies the M1 frozen matrix to a `*_M1-frozen.tsv` archive name BEFORE refiring, so the m1-03 output filename is preserved as a historical record.

### D. Conda env partitioning convention `envs/m1-{download,harmonize,munge,ldsc-rg,qc}.yml`

**Files:** `envs/m1-*.yml` (5 envs, each ~10-30 dependencies).

**Pattern:** Per-rule-family env (one env file per Snakemake rule cluster). Pinned versions match `envs/python_stats.yml` for ABI consistency. `numpy<2` everywhere LDSC fork is a dependency.

**M2 reuse:** New env files:

| Env | Purpose | Key Deps |
|-----|---------|----------|
| `envs/m2-mtag.yml` | MTAG runs (Turley 2018 fork at github.com/JonJala/mtag) | python=2.7 OR python=3.x with mtag's known py3 fork; numpy<1.17 OR mtag's bundled-ldsc compatibility; pandas; scipy. **Pitfall:** MTAG ships its own ldsc_mod which expects Python 2.7 in the upstream repo; verify the fork supports modern Python. May need a separate Python 2.7 conda env for MTAG specifically. |
| `envs/m2-cpassoc.yml` | CPASSOC Python reimplementation | python=3.11; numpy=1.26.4 (matching m1-* convention); pandas=2.2.x; scipy=1.11.x; pytest |
| `envs/m2-clumping.yml` | PLINK 1.9 clumping | plink=1.9 (bioconda); python=3.11 for orchestration |
| `envs/m2-mtcojo.yml` | GCTA mtCOJO | gcta=1.94 (bioconda) — already on disk at /rs1/researchers/c/ckclinto/conda_envs/gcta; python=3.11 |
| `envs/m2-regions.yml` | bedtools + Python region union | bedtools=2.31; python=3.11; pandas; pyarrow |
| `envs/m2-novelty.yml` | GWAS Catalog parser + Class 1 logic | python=3.11; pandas; pyarrow; pybedtools (or shell-out to bedtools intersect) |

### E. SHA-256 freeze pattern from `freeze_sha256_manifest.py`

**File:** `src/python/freeze_sha256_manifest.py`.

**Pattern:** Walk a directory tree, compute SHA-256 of every file (skipping `*.partial`, `*.deferred`, `.download_complete*`), write deterministic TSV (sorted by relative path, optional mtime).

**M2 reuse:** M2 closeout produces `sha256_manifest_m2_frozen.tsv` covering:
- `data/catalogs/gwas-catalog-associations-full.zip` (raw bytes for v_lock_M2)
- `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv`
- `data/processed/mtag/{stratum}/*.txt` (MTAG outputs)
- `data/processed/cpassoc/{stratum}/*.tsv` (CPASSOC outputs)
- `data/processed/clumping/{ancestry}/*.clumped` (PLINK clumped outputs — sample for hash budget)
- `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv`
- `results/regions/union_region_list.bed`
- `results/novelty/joint_signal_novel.tsv`

Mirror to `.planning/amendments/sha256_manifest_m2_frozen.tsv` for OSF supplementary upload (M5 follow-up posting per DEC-2026-04-25-02).

### F. TDD discipline (RED → GREEN → atomic commits per task)

**Pattern:** Each plan task is one atomic commit. Tests for new modules land first (RED), implementation follows (GREEN). Verified by M1 closeout — 22 test modules, 93 tests collected with 0 import errors at m1 closeout.

**M2 reuse:** New tests under `tests/m2/`:
- `tests/m2/test_cpassoc_shom_shet.py` — synthetic z-score matrix; reproduce Zhu 2015 Table 1 example values where reproducible
- `tests/m2/test_build_region_union.py` — strict-union semantics; provenance JSON preservation
- `tests/m2/test_call_class1_novelty.py` — synthetic catalog snapshot + novelty filter
- `tests/m2/test_build_mtag_residcov_slice.py` — matrix-slicing helper preserves trait order
- `tests/m2/test_mtag_overlap_matrix_format.py` — `.txt` whitespace-only, no header, dimension matches len(--sumstats)
- `tests/m2/test_mtcojo_extreme_overlap_filter.py` — gcov_int > 0.1 selection logic
- `tests/m2/test_m2_stratum_keys.py` — defensive bound + skip-with-doc behavior
- `tests/m2/test_safe_inverse.py` — pinv vs ridge fallback for near-singular R

### G. Quarto QC fallback pattern (m1_qc_index.qmd + render_qc_html_minimal.py)

**Files:** `src/R/qc/m1_qc_report.qmd`, `src/R/qc/m1_qc_index.qmd`, `src/python/render_qc_html_minimal.py`.

**Pattern:** Primary path uses Quarto (mixed R + Python engine) for rich plots; fallback path is a pure-Python minimal HTML renderer when Quarto is unavailable in PATH.

**M2 reuse (optional):** A `src/R/qc/m2_qc_report.qmd` covering MTAG QQ plots, CPASSOC SHom/SHet histograms, region density maps. If skipped for time, M2 closeout uses `verify_m1_artifacts.py`-style Python verifier instead — emits a JSON summary with PASS/WARN/FAIL per success criterion. Recommend Python-only verifier `verify_m2_artifacts.py` modeled on `verify_m1_artifacts.py` (492 lines, runs in <2s). Quarto QC can land in a follow-up M2-extension if Carter wants a HTML report for the manuscript.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest >=7 (already in `envs/m1-*.yml`); reuse for M2 |
| Config file | `pytest.ini` at project root (existing); `tests/m2/conftest.py` (NEW; mirrors `tests/m1/conftest.py`) |
| Quick run command | `pytest tests/m2/ -x --tb=short` |
| Full suite command | `pytest tests/m1/ tests/m2/ tests/phase9/ -x` (full project regression) |

### Phase Requirements → Test Map (per ROADMAP M2 Success Criteria 1-6)

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RM-1 | rg_matrix.tsv (~26x26 LDSC pairwise rg + intercept) for all stratum-pairs | unit + integration | `pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x` (existing — REUSED) | ✅ existing |
| RM-2 | MTAG per-trait outputs with `max_FDR` column per Turley 2018 | unit | `pytest tests/m2/test_mtag_overlap_matrix_format.py tests/m2/test_build_mtag_residcov_slice.py -x` | ❌ Wave 0 |
| RM-3 | CPASSOC per-locus SHom/SHet outputs | unit | `pytest tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py -x` | ❌ Wave 0 |
| RM-4 | Genome-wide union region BED (~1500-3000 regions) | unit | `pytest tests/m2/test_build_region_union.py -x` | ❌ Wave 0 |
| RM-5 | `joint_signal_novel.tsv` with MTAG ∩ CPASSOC high-confidence subset | unit + integration | `pytest tests/m2/test_call_class1_novelty.py -x` | ❌ Wave 0 |
| RM-6 | mtCOJO sensitivity table on top-N MTAG-novel loci | unit | `pytest tests/m2/test_mtcojo_extreme_overlap_filter.py -x` | ❌ Wave 0 |
| REQ-MTAG-OVERLAP | MTAG end-to-end on 3 strata with `--residcov_path` consumed | smoke | `snakemake --use-conda mtag_run --config stratum=EUR --dry-run` | ❌ Wave 2 |
| REQ-CPASSOC-ORTHOGONAL | CPASSOC end-to-end on 3 strata | smoke | `snakemake --use-conda cpassoc_run --config stratum=EUR --dry-run` | ❌ Wave 3 |
| REQ-NOVELTY-CLASS-1 | Class 1 novelty filter against catalog v_lock_M2 | smoke | `pytest tests/m2/test_call_class1_novelty.py::test_end_to_end_synth -x` | ❌ Wave 5 |
| REQ-CATALOG-VERSION-LOCK | New row in catalog_lock_manifest.tsv with SHA-256 + URL + fetch_date | unit | `pytest tests/m2/test_catalog_lock_manifest_v_lock_M2.py -x` | ❌ Wave 0 |
| REQ-SNAKEMAKE-CI | M2 toy 3-locus smoke completes < 15 min | integration | `snakemake -s tests/toy_3locus/Snakefile.test --cores 2 --use-conda` (extend existing) | partial — extend existing |
| REQ-OSF-PREREG | OSF amendment posted (already satisfied 2026-04-25) | manual verification | gate-release commit d55c1d1 already landed | ✅ done |

### Sampling Rate

- **Per task commit:** `pytest tests/m2/ -x --tb=short` (< 30 sec for unit tests)
- **Per wave merge:** `pytest tests/m1/ tests/m2/ -x` (full M1 + M2 regression, < 5 min)
- **Phase gate:** Full suite + dry-run smoke (`snakemake --dry-run -s src/snakemake/rules/m2_*.smk --use-conda`) green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/m2/conftest.py` — shared fixtures (mock LDSC matrix, synthetic z-score grid, mock GWAS Catalog tail, mock MTAG output table)
- [ ] `tests/m2/test_cpassoc_shom_shet.py` — covers REQ-CPASSOC-ORTHOGONAL + RM-3
- [ ] `tests/m2/test_safe_inverse.py` — Q2 conditioning policy
- [ ] `tests/m2/test_build_region_union.py` — covers RM-4 + Q6
- [ ] `tests/m2/test_call_class1_novelty.py` — covers REQ-NOVELTY-CLASS-1 + RM-5
- [ ] `tests/m2/test_build_mtag_residcov_slice.py` — covers RM-2 + Q1 trait-order contract
- [ ] `tests/m2/test_mtag_overlap_matrix_format.py` — covers Q1 file format
- [ ] `tests/m2/test_mtcojo_extreme_overlap_filter.py` — covers RM-6 + Q8
- [ ] `tests/m2/test_m2_stratum_keys.py` — covers Pattern B
- [ ] `tests/m2/test_catalog_lock_manifest_v_lock_M2.py` — covers REQ-CATALOG-VERSION-LOCK + Q5

## Implementation Pitfalls (HARDCODE INTO PLANS)

### Pitfall 1: MTAG flag-name terminology mismatch

**What goes wrong:** CONTEXT.md decisions D-M2-10 + REQ-MTAG-OVERLAP both reference an "MTAG `--overlap`" flag. **MTAG does not expose `--overlap`.** A naive plan that emits `mtag.py --overlap path/to/matrix.tsv` will fail with `argparse: unrecognized arguments`.

**Why it happens:** "MTAG --overlap" is a colloquial shorthand for the residual-covariance-matrix-based sample-overlap correction. The actual CLI flag is `--residcov_path`. Multiple GitHub issues, FAQ entries, and user guides use "MTAG --overlap" loosely.

**How to avoid:** Plan tasks reference `--residcov_path` literally in shell invocations. Tests assert the argv list contains `--residcov_path` not `--overlap`.

**Warning signs:** `argparse: unrecognized arguments: --overlap` in the task log.

### Pitfall 2: MTAG matrix file format — header-less + index-less + whitespace-delimited

**What goes wrong:** The reducer's `bivariate_intercept_matrix_2026-04-M2.tsv` is a human-readable indexed wide TSV (header row + index column). MTAG's `_read_matrix(file_path)` calls `np.loadtxt(file_path)` which fails on header rows or index columns (parses them as data → ValueError or wrong dimension).

**Why it happens:** The M1 reducer optimized for human readability. MTAG expects a bare numeric matrix.

**How to avoid:** New helper `src/python/build_mtag_residcov_slice.py` reads the indexed TSV, slices to stratum traits, and emits TWO files:
1. `data/processed/mtag/{stratum}/residcov.txt` — bare numeric matrix, whitespace-delimited, no header, no index. This is what MTAG consumes.
2. `data/processed/mtag/{stratum}/residcov.trait_order.json` — sidecar JSON listing the canonical trait order. The Snakemake rule consumes this to build the matching `--sumstats` comma-separated list.

**Warning signs:** MTAG log message "Number of traits in --sumstats does not match dimensions of --residcov_path"; `np.loadtxt` ValueError on the matrix file.

### Pitfall 3: AFR PLINK reference panel does NOT exist on disk yet

**What goes wrong:** D-M2-02 mandates 1000G AFR (N=661) as the AFR PLINK reference. **Only `.frq` files exist** at `data/reference/ldsc/1000G_Phase3_frq_AFR/`. The `.bed/.bim/.fam` PLINK bfiles for AFR are NOT on disk. Wave 0 must build them from `data/raw/1kg/vcf/chr*.vcf.gz` using `data/raw/1kg/AFR.samples` (504 sample list).

**Why it happens:** The pre-pivot Phase 5 staged EUR PLINK + AFR `.frq` from the LDSC public bundle but did NOT need AFR `.bed/.bim/.fam` (LDSC AFR ld-score regression uses precomputed AFR ld-scores, not raw bfiles).

**How to avoid:** Wave 0 task `m2_build_1000g_afr_plink` runs:

```bash
for chr in {1..22}; do
    plink2 \
        --vcf data/raw/1kg/vcf/chr${chr}.vcf.gz \
        --keep data/raw/1kg/AFR.samples \
        --maf 0.005 \
        --geno 0.05 \
        --hwe 1e-6 \
        --make-bed \
        --out data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.${chr}
done
```

Wall time estimate: ~3 hours total (plink2 vcf→bed at 504 samples). Run once at Wave 0; output is a permanent reference.

**Warning signs:** Snakemake error `MissingInputException: 1000G.AFR.QC.10.bed` at clumping rule fire.

### Pitfall 4: PLINK 1.9 vs PLINK 2.0 — only PLINK 1.9 has `--clump`

**What goes wrong:** PLINK 2.0 does not yet implement `--clump`. A plan that uses `plink2 --clump ...` fails with `Error: Unknown command 'clump'`.

**Why it happens:** PLINK 2.0 is the modern PLINK; PLINK 1.9 is in maintenance mode. PLINK 2.0 prioritized GLM, association tests, and PRS. `--clump` is not yet ported.

**How to avoid:** `envs/m2-clumping.yml` pins `plink=1.9` (the bioconda recipe). Tests assert `plink --version` reports 1.9.

**Warning signs:** `Error: Unknown command 'clump'`; output empty.

### Pitfall 5: LDSC `--rg-cross` does not exist — same as M1 RESEARCH Pitfall #1

**What goes wrong:** Re-using the m1-03 wave for the D-M2-01 refire might be tempting to "optimize" by switching to a single `ldsc.py --rg-cross` call. **`--rg-cross` does not exist in the vendored abdenlab fork.** This was the load-bearing M1 RESEARCH pitfall and is RE-INHERITED by M2.

**Why it happens:** Plausible-sounding but apocryphal flag.

**How to avoid:** D-M2-01 refire uses the EXACT SAME star-topology pattern as m1-03 (44 → ~25 star calls for the expanded ~26-trait inventory). Snakemake rule `m1_ldsc_rg_star` is path-parameterized and trait-list-driven; just re-execute it.

**Warning signs:** `argparse: unrecognized arguments: --rg-cross`; or a hand-rolled subprocess call that bypasses the existing rule.

### Pitfall 6: MTAG installation — `pip install mtag` does NOT exist

**What goes wrong:** MTAG is distributed as a GitHub repo, not a PyPI package. A naive `pip install mtag` in `envs/m2-mtag.yml` fails.

**Why it happens:** MTAG is a research-grade tool; the authors never published to PyPI. The install procedure is `git clone https://github.com/JonJala/mtag` + create a Python 2.7 conda env with the bundled `requirements.txt` (or use the community py3 fork).

**How to avoid:** `envs/m2-mtag.yml` pins MTAG via `pip:` `git+https://github.com/JonJala/mtag.git@<commit>` (lockfile pin). Wave 0 task `m2_install_mtag` git-clones the repo to `tools/mtag/` mirroring the existing `tools/ldsc/` vendoring pattern.

**Note:** MTAG's vendored ldsc_mod expects Python 2.7 in the upstream repo. Verify whether the Carter-installed py3 LDSC fork at `envs/ldsc_py3.yml` is compatible. If not, vendor MTAG with its own py2.7 conda env.

**Warning signs:** `pip install mtag` → `No matching distribution found`; MTAG run → `ImportError: ldsc_mod.ldscore`.

### Pitfall 7: trait-key ordering between MTAG `--sumstats` and `--residcov_path` matrix

**What goes wrong:** MTAG performs an `assert args.omega_hat.shape[0] == args.omega_hat.shape[1] == Zs.shape[1] == args.sigma_hat.shape[0] == args.sigma_hat.shape[1]` AFTER load. If trait-key order in the matrix file doesn't match the order in `--sumstats`, the assertion passes (dimensions match) but the per-trait-pair correlations are silently mismatched — producing meaningless output.

**Why it happens:** MTAG trusts the user to align them. There's no internal sanity check.

**How to avoid:** The matrix-slice helper emits the sidecar JSON `residcov.trait_order.json` listing the canonical order. The Snakemake rule reads the sidecar and constructs the `--sumstats` comma-separated path list in the EXACT SAME order. Add a unit test that verifies the order matches.

**Warning signs:** MTAG runs cleanly but downstream Class 1 novelty calling produces near-zero overlap with single-trait significant hits — symptomatic of mismatched residual-covariance.

### Pitfall 8: Conda env LSF dispatch — Python 3.11 vs Snakemake 7.32.4

**What goes wrong:** Project memory `project_python_311_pin.md` notes Snakemake 7.32.4 requires Python 3.11. Don't invoke `snakemake` from miniconda3 base (Python 3.13). Use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` or `--use-conda`.

**Why it happens:** Mixed conda installs.

**How to avoid:** All M2 fire scripts use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --use-conda` per the M1 convention.

**Warning signs:** Snakemake import errors at LSF job launch.

### Pitfall 9: bedtools strand-aware merge — DON'T use `-s` for genomic regions

**What goes wrong:** `bedtools merge -s` merges intervals only if they share a strand. Lead variants don't have a meaningful strand for fine-mapping; using `-s` would produce empty merges.

**Why it happens:** bedtools defaults are not strand-aware for `merge` (good); `-s` is opt-in (bad if you forget the semantics).

**How to avoid:** D-M2-09 region merge uses bedtools default — no `-s`, no `-d` flag. Strict overlap collapses any 1bp+ overlap.

**Warning signs:** Region count = number of lead variants (no merging happened) — symptomatic of `-s` accidentally enabled.

### Pitfall 10: GWAS Catalog ZIP file → unpack inside the rule, hash the ZIP not the unpacked TSV

**What goes wrong:** `gwas-catalog-associations-full.zip` is a 56 MB compressed archive. The `.zip` SHA-256 is what the EBI server publishes. If the planner hashes the unpacked TSV instead, the SHA mismatches the published value at v_lock refresh.

**Why it happens:** Many manifest workflows hash the "final" content; this convention breaks with recompressed archives.

**How to avoid:** `catalog_lock_manifest.tsv` row for `gwas_catalog.v_lock_M2` records:
- `url` — the .zip URL
- `sha256` — SHA of the .zip BYTES (matches published EBI server hash)
- `size_bytes` — size of the .zip
- The unpacking happens inside a separate Snakemake rule `unzip_gwas_catalog_v_lock_M2`; the unpacked TSV gets a separate `sha256_unpacked` column for QC but is not the canonical lock value.

**Warning signs:** `sha256` hash field in catalog_lock_manifest.tsv differs from EBI server-published value.

### Pitfall 11: AFR LD-score for LDSC matrix refire — D-M2-01 uses EUR LD-scores

**What goes wrong:** The existing `m1_ldsc_rg_star` rule hardcodes `_EUR_REF_LD = "data/external/ldscore/eur_w_ld_chr/"`. The bivariate gcov_int IS theoretically LD-panel-robust (per Bulik-Sullivan 2015 derivation — the intercept measures sample overlap not LD), so using EUR LD-scores for AFR-AFR or cross-ancestry pairs is defensible BUT introduces a known approximation flagged in M1 RESEARCH.

**Why it happens:** AFR LD-scores would require staging `data/external/ldscore/afr_w_ld_chr/` — not currently on disk.

**How to avoid:** D-M2-01 refire continues to use EUR LD-scores per M1 convention. Document the cross-ancestry approximation in `m2_post_m3_rerun_queue.tsv` for an M3-supersede pass: when AoU AFR LD lands, optionally re-derive AFR-AFR bivariate intercepts with AFR LD-scores and compare. Pre-flight: confirm Carter has AFR LD-scores accessible (not currently checked).

**Warning signs:** AFR-AFR bivariate intercepts in the matrix appear systematically high; flagged by `validate_expected_intercept_heuristics` warning.

## Open Questions for Carter (RESOLVED via CONTEXT.md D-M2-Q1..Q6)

These six questions are RESOLVED in CONTEXT.md research_surfaced_resolutions section as D-M2-Q1..Q6. The text below records the original sub-decisions that the research uncovered before they were locked; downstream plans should reference the corresponding D-M2-QN in CONTEXT.md as authoritative.

### 1. MTAG `--max-FDR-threshold 0.05` flag name verification

CONTEXT D-M2-07 + REQ-MTAG-OVERLAP literal text: "MTAG `--max-FDR-threshold 0.05`". Research found:
- MTAG argparse exposes `--p_sig` (default 5e-8) — controls genome-wide significance threshold for output filtering.
- MTAG's "maxFDR" is a post-hoc calculation per Tutorial 3 (the `mtag_maxFDR.py` script) — not a single CLI flag in the main `mtag.py`.

**Question for Carter:** Is "max-FDR-threshold 0.05" referring to (a) post-hoc filter via `mtag_maxFDR.py` requiring max_FDR < 0.05, or (b) a property of `--p_sig` we're meant to interpret as 0.05? I recommend (a) — D-M2-07 implementation runs `mtag_maxFDR.py` after each MTAG run and filters loci to `max_FDR < 0.05` per Turley 2018 Methods §"maxFDR". This requires a second Snakemake rule per stratum. The OSF amendment text reads "max_FDR filter per Turley 2018" which supports this interpretation.

### 2. AFR LDSC ld-score reference availability

D-M2-02 says "1000G AFR (N=661) for M2 AFR-stratum PLINK clumping AND for AFR LDSC ld-score regression where AoU LD is unavailable". The existing M1 LDSC matrix uses EUR ld-scores at `data/external/ldscore/eur_w_ld_chr/` for ALL pairs (cross-ancestry approximation). 

**Question for Carter:** Does Wave 0 need to additionally stage `data/external/ldscore/afr_w_ld_chr/` for an AFR-specific LDSC pass, or is the EUR-LD cross-ancestry approximation acceptable for M2 AFR-stratum? I recommend the latter — staying consistent with M1 convention; the AFR LDSC re-run becomes part of the M3-supersede queue when AoU AFR LD lands. If Carter wants AFR LDSC scores at M2 kickoff, that's an additional Wave 0 task with ~2 hours of staging time.

### 3. mtCOJO TRANS-stratum LD reference choice

Research recommends 1000G EUR for TRANS-stratum mtCOJO with a 1000G AFR sensitivity check on TRANS mtCOJO-novel loci. CONTEXT D-M2-08 doesn't explicitly resolve this.

**Question for Carter:** Is the recommended primary EUR + sensitivity AFR design acceptable, or should TRANS mtCOJO use a different strategy (e.g. pooled 1000G all-pops via custom bfile build)? I recommend the EUR-primary + AFR-sensitivity design.

### 4. M2 QC report scope (Quarto vs Python verifier)

Research recommends a Python-only `verify_m2_artifacts.py` modeled on `verify_m1_artifacts.py` for closeout, with optional Quarto QC report deferred to follow-up.

**Question for Carter:** Is a Python-only M2 verifier acceptable for closeout, or is a Quarto QC HTML required for OSF supplementary upload? CONTEXT.md doesn't specify; the M1 pattern was Quarto HTML + Python verifier in tandem.

### 5. mtCOJO output target trait scope per stratum

D-M2-08 says "mtCOJO sensitivity on top-N MTAG-novel loci". Research clarified that mtCOJO emits one per (target_trait, covariate_traits) tuple. For a 9-trait EUR run, mtCOJO can be invoked 9 times (each trait conditioned on the other 8) OR fewer (only on traits with MTAG-novel loci showing extreme overlap). 

**Question for Carter:** All 9 mtCOJO invocations per stratum × 3 strata = 27 mtCOJO runs total, OR only target-trait-of-interest runs (could be 1-3 per stratum)? I recommend the latter for compute economy — only run mtCOJO for target traits where MTAG produced a novel locus AND extreme overlap is detected; MTAG-null target traits don't need mtCOJO confirmation.

### 6. Per-stratum trait count realism (D-M2-06 + Pattern B `_MIN_PER_STRATUM=5`)

The proposed `m2_stratum_keys._MIN_PER_STRATUM = 5` is conservative. Current trait_inventory.yaml shows 47 cells × 12 traits (mostly EUR + sparse AFR). Concrete EUR-stratum trait count for M2: looks like 9 traits available (BMI/T2D/SBP/stroke/asthma/CAD/lipids/eGFR/HbA1c). AFR: looks like 5-7 traits depending on which AFR cells have qc_status != MISSING.

**Question for Carter:** Do you want a hard floor on AFR-stratum trait count (e.g. ≥6 required, else skip the AFR MTAG run entirely), or proceed with whatever is available (≥3 minimum)?

## Suggested Plan Decomposition

This is researcher's recommendation only — planner has discretion to restructure. The 6-wave decomposition mirrors M1's wave-and-task pattern.

### Wave 0 — Preflight + environment + tests + reference data (≈ 1 day)

Tasks (TDD-first; tests before implementation):

1. **Probe & test scaffolding.** Create `tests/m2/conftest.py` mirroring `tests/m1/conftest.py`. Stub all 10 unit test files listed in "Wave 0 Gaps" above. RED phase complete when all tests fail with NotImplementedError.

2. **Conda envs.** Author 6 new env files (`envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml`) per Pattern D. Pin numpy<2 where MTAG / LDSC fork is involved. Snakemake `--use-conda` smoke test on each env passes.

3. **Build 1000G AFR PLINK bfiles.** Wave 0 fire of `m2_build_1000g_afr_plink` (Pitfall 3). Output: `data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam}`. Wall time ~3 hours.

4. **MTAG vendoring.** `git clone https://github.com/JonJala/mtag` to `tools/mtag/`. Verify import + `python tools/mtag/mtag.py --help` succeeds. Lockfile pin in `envs/m2-mtag.yml`.

5. **mtCOJO + bedtools availability.** Verify `gcta --version` and `bedtools --version` resolve in respective envs.

6. **GWAS Catalog snapshot fetch.** Wave 0 task `download_gwas_catalog_M2` per Q5. Output: `data/catalogs/gwas-catalog-associations-full.zip` + new row `gwas_catalog.v_lock_M2` in `catalog_lock_manifest.tsv`.

7. **CPASSOC unit tests GREEN.** Implement `src/python/cpassoc.py` with `cpassoc_shom`, `cpassoc_shet`, `_safe_inverse`. Tests in `tests/m2/test_cpassoc_shom_shet.py` + `tests/m2/test_safe_inverse.py` GREEN.

8. **Stratum-keys helper GREEN.** Implement `src/python/m2_stratum_keys.py` per Pattern B. Test in `tests/m2/test_m2_stratum_keys.py` GREEN.

### Wave 1 — D-M2-01 LDSC matrix refire (≈ 0.5–1 day)

Tasks:

1. **Archive M1 frozen matrix.** Copy `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` → `data/processed/ldsc_overlap/bivariate_intercept_matrix_M1-frozen.tsv` BEFORE refire (Pattern C critical note).

2. **Refire m1-03 wave.** Re-execute `m1_munge_all` + `m1_ldsc_rg_all_stars` + `m1_ldsc_rg_reduce` (existing rules, no code change) against the expanded ~26-trait inventory. Update `m1_trait_keys.py` defensive bound from `40 ≤ N ≤ 50` to whatever band fits the 26-trait actual count (e.g. `20 ≤ N ≤ 50`).

3. **Rename output.** `bivariate_intercept_matrix_2026-04.tsv` → `bivariate_intercept_matrix_2026-04-M2.tsv` per CONTEXT D-M2-01 naming.

4. **OSF mirror.** Copy to `.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv`.

5. **Validation.** Re-run `validate_self_consistency` + `validate_expected_intercept_heuristics`; commit `rg_validation_warnings.json` updated for the M2 matrix.

### Wave 2 — MTAG 3 stratum runs (≈ 0.5–1 day per stratum, parallel)

Tasks:

1. **Matrix slice helper GREEN.** Implement `src/python/build_mtag_residcov_slice.py` per Q1 + Pitfall 2 + Pitfall 7. Tests in `tests/m2/test_build_mtag_residcov_slice.py` + `tests/m2/test_mtag_overlap_matrix_format.py` GREEN.

2. **m2_mtag.smk rule cluster.** Snakemake rules: `m2_mtag_residcov_slice` (per stratum), `m2_mtag_run` (per stratum, consumes the slice), `m2_mtag_maxfdr_filter` (per stratum, runs `mtag_maxFDR.py` if Carter resolves Q1 above).

3. **Fire EUR + AFR + TRANS in parallel** on LSF long queue. Each stratum: ~30-60 min wall.

4. **Smoke test.** Verify outputs at `data/processed/mtag/{stratum}/{trait}_mtag.txt` exist and contain `max_FDR` column.

### Wave 3 — CPASSOC 3 stratum runs (≈ 0.5 day total, parallel with Wave 2)

Tasks:

1. **R matrix slice helper GREEN.** Either inline in `cpassoc.py` or new `build_cpassoc_R_slice.py` per Q7. Test in `tests/m2/test_cpassoc_r_slice_psd.py` (eigvalsh PSD check).

2. **m2_cpassoc.smk rule cluster.** Per-stratum CPASSOC run: load harmonized sumstats, align variants, build z-score matrix, slice R, compute SHom + SHet, write per-locus TSV.

3. **Fire 3 strata** on LSF standard queue. Each stratum: ~10-30 min wall (Python pinv on K=9 + per-SNP einsum is fast).

### Wave 4 — Clumping + mtCOJO + region union (≈ 1–2 days)

Tasks:

1. **m2_clumping.smk rule cluster.** Per-(trait × ancestry × chr) PLINK 1.9 clump rule per Q3. Aggregator that concatenates all chr outputs per (trait × ancestry) into one BED.

2. **Fire all clump runs** on LSF standard queue at high parallelism. Wall time ~3 hours.

3. **m2_mtcojo.smk rule cluster.** Per (stratum, target_trait) mtCOJO run per Q4 + Q8. Sensitivity table joining MTAG-novel loci with mtCOJO conditional p-values.

4. **Region union builder.** `src/python/build_region_union.py` per D-M2-09 + Q6. Tests in `tests/m2/test_build_region_union.py` GREEN.

5. **Fire region union.** Output: `results/regions/union_region_list.bed` with provenance JSON column.

### Wave 5 — Class 1 novelty + closeout (≈ 0.5–1 day)

Tasks:

1. **Class 1 novelty caller.** `src/python/call_class1_novelty.py` per REQ-NOVELTY-CLASS-1 + Q5 + Q6. Tests in `tests/m2/test_call_class1_novelty.py` GREEN.

2. **Fire novelty call.** Output: `results/novelty/joint_signal_novel.tsv`.

3. **Post-M3-rerun queue.** Emit `.planning/m2_post_m3_rerun_queue.tsv` per D-M2-02.

4. **m2-deferred-items.md.** Document skip-with-doc cells per D-M2-06 + any TRANS coverage gaps.

5. **SHA-256 freeze.** `freeze_sha256_manifest.py` over M2 outputs per Pattern E. Output: `sha256_manifest_m2_frozen.tsv` + mirror to `.planning/amendments/`.

6. **verify_m2_artifacts.py.** Python verifier modeled on `verify_m1_artifacts.py` per Pattern G fallback. Emits Dimension-N PASS/WARN/FAIL JSON + closeout report.

7. **Phase closeout.** `m2-PHASE-CLOSEOUT.md` per M1 closeout template. Atomic commit with closeout artifacts.

### Estimated Total Wall Time

| Wave | Wall Time | Compute Type |
|------|-----------|--------------|
| 0 — Preflight | ~1 day (3 hours AFR PLINK build dominates) | LSF standard + serial |
| 1 — LDSC refire | ~0.5–1 day | LSF long queue (parallel star calls) |
| 2 — MTAG 3 runs | ~0.5–1 day (parallel) | LSF long queue |
| 3 — CPASSOC 3 runs | ~0.5 day (parallel) | LSF standard queue |
| 4 — Clumping + mtCOJO + regions | ~1–2 days | LSF standard queue (high parallelism) |
| 5 — Novelty + closeout | ~0.5–1 day | LSF standard queue |
| **Total wall (assuming Carter resume queue not blocking)** | **~4–7 days** | mix |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | MTAG residcov_path uses `np.loadtxt`-tolerant whitespace, no header, no index | Q1 | HIGH — assertion failure or silent matrix mis-alignment; mitigated by Pitfall 2 + Pitfall 7 unit tests |
| A2 | `numpy.linalg.pinv(R, rcond=1e-15)` is sufficient for Zhu 2015 R-inversion in 99% of cases | Q2 | MEDIUM — extreme cohort overlap (rare in this 9-trait set) could trigger ridge fallback; documented with conditional logic |
| A3 | PLINK 1.9 chr-level clumping at `mem_mb=4000` fits LSF standard queue | Q3 | LOW — empirically tested in pre-pivot Phase 0 + community LSF reports |
| A4 | 1000G EUR is defensible primary LD reference for TRANS mtCOJO | Q4 | MEDIUM — Carter Q3 above for confirmation; sensitivity check covers risk |
| A5 | EBI GWAS Catalog FTP serves `Last-Modified` headers consistently | Q5 | LOW — verified via curl probe; even if header drops, SHA-256 + size_bytes pin is sufficient |
| A6 | bedtools default merge (no -d, no -s) gives "strict union" per D-M2-09 | Q6 | LOW — verified against bedtools v2.31 docs |
| A7 | LDSC bivariate intercept matrix is PSD (preserved under principal-submatrix slicing) | Q7 | LOW — covariance matrices are PSD by construction; eigvalsh probe in Wave 0 test |
| A8 | mtCOJO emits per-target-trait file (not per-locus); join on rsID + chr:pos fallback | Q8 | LOW — confirmed via Yang Lab GCTA docs |
| A9 | `_MIN_PER_STRATUM = 5` is reasonable lower bound for AFR stratum trait count | Pattern B | MEDIUM — Carter Q6 above for confirmation |
| A10 | Carter's existing `tools/ldsc/` py3 fork is compatible with MTAG's bundled ldsc_mod | Pitfall 6 | MEDIUM — may require separate py2.7 conda env for MTAG; Wave 0 task to verify |
| A11 | TRANS-stratum trait count is non-zero (Aragam-CAD-EAS, GBMI-asthma-MULTI, GIGASTROKE-stroke-TRANS, CKDGen-eGFR-TRANS, GLGC-lipids-TRANS land in inventory) | D-M2-03 | LOW — direct inspection of harmonized files shows TRANS cells exist for 5+ traits |
| A12 | D-M2-07 "max-FDR-threshold 0.05" maps to Turley 2018 maxFDR Tutorial 3 post-hoc filter, not a `--p_sig` interpretation | D-M2-07 | MEDIUM — Carter Q1 above for confirmation |
| A13 | mtCOJO is invoked per-target-trait per-stratum (not for every MTAG-novel locus separately) | Q8 | MEDIUM — Carter Q5 above for confirmation |
| A14 | EUR LD-scores acceptable for AFR-AFR LDSC bivariate intercept estimation in M2 (cross-ancestry approximation) | Pitfall 11 | MEDIUM — Carter Q2 above for confirmation; M3-supersede covers risk |

## Sources

### Primary (HIGH confidence)

- [VERIFIED: github.com/JonJala/mtag/blob/master/mtag.py via WebFetch — argparse definitions for `--residcov_path`, `--gencov_path`, `--no_overlap`, `--use_beta_se`, `--p_sig`; `_read_matrix(file_path)` accepts `.npy` or `.txt`]
- [VERIFIED: M1 source code at `src/python/{m1_raw_glob.py, m1_trait_keys.py, sumstats_utils.py, reduce_ldsc_rg_matrix.py, munge_sumstats_ldsc.py, freeze_sha256_manifest.py, render_qc_html_minimal.py}`]
- [VERIFIED: M1 Snakemake rules at `src/snakemake/rules/{m1_ldsc_rg.smk, m1_munge.smk}`]
- [VERIFIED: directory probe of `data/reference/ldsc/1000G_EUR_Phase3_plink/` — 22 chrs of bfiles exist; 489-503 EUR samples per chr; ~510k SNPs/chr]
- [VERIFIED: directory probe of `data/reference/ldsc/1000G_Phase3_frq_AFR/` — only `.frq` files exist; `.bed/.bim/.fam` AFR PLINK MUST BE BUILT in Wave 0]
- [VERIFIED: directory probe of `data/raw/1kg/{AFR.samples, vcf/chr*.vcf.gz}` — 504 AFR samples + 22 chr VCFs available for AFR PLINK build]
- [VERIFIED: existing M1 envs at `envs/m1-{download,harmonize,munge,ldsc-rg,qc}.yml`]
- [VERIFIED: `data/catalogs/catalog_lock_manifest.tsv` schema — 7 columns, 5 data rows; ClinVar M0-locked]
- [VERIFIED: `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` schema — 13 lines × 13 cols; symmetric; diag=1.0]
- [VERIFIED: `https://ftp.ebi.ac.uk/pub/databases/gwas/releases/latest/` directory listing 2026-04-25 — gwas-catalog-associations-full.zip 56 MB; gwas-catalog-studies.tsv 69 MB; etc.]

### Secondary (MEDIUM confidence)

- [CITED: Turley et al. 2018 *Nat Genet* 50:229–237 — MTAG method + maxFDR Tutorial 3 logic]
- [CITED: Zhu et al. 2015 *AJHG* 96(1):21–36 — CPASSOC SHom/SHet test statistic formulas]
- [CITED: Zhu et al. 2018 *Nat Commun* 9:224 — mtCOJO method]
- [CITED: Bulik-Sullivan et al. 2015 *Nat Genet* 47:1236-1241 — LDSC bivariate-intercept derivation; LD-panel robustness]
- [CITED: PLINK 1.9 docs at cog-genomics.org/plink/1.9/postproc — `--clump` flag]
- [CITED: bedtools v2.31 docs — `merge` default behavior + `-d` `-s` flags]
- [CITED: GCTA mtCOJO docs at yanglab.westlake.edu.cn/software/gcta/#mtCOJO]
- [VERIFIED via WebFetch: PLINK 2.0 vs PLINK 1.9 `--clump` support — only PLINK 1.9 has it]

### Tertiary (LOW confidence — needs validation)

- [WebSearch: MTAG installation route — pip vs git clone; py2.7 ldsc_mod compat with py3 — verify in Wave 0]
- [WebSearch: PLINK clump memory benchmarks at 4000 MB headroom — community reports, not officially benchmarked]
- [Assumed via project memory: feedback_lsf_queues — standard=2880min, serial=5760min, long=14400min — verify against `config/cluster_lsf.yaml` at fire time]

## Project Constraints (from CLAUDE.md)

- **100% public data.** All M2 data inputs (LDSC matrix, harmonized sumstats, GWAS Catalog) are derivatives of public DUAs or open-access EBI/PMC artifacts. AoU compute is M3 scope, NOT M2.
- **Solo author + multi-method triangulation.** M2's MTAG ∩ CPASSOC corroboration filter (D-M2-04) is the multi-method triangulation discipline.
- **No web/JS stack.** All M2 code is Python + R + bash + Snakemake.
- **Timeline is not binding constraint.** M2 wall-time estimate (4-7 days) is not optimized for speed — 6-wave decomposition prioritizes test discipline + atomic commits over parallelism.
- **GPFS filesystem.** No worktree isolation. GSD mode `solo` with `git.isolation: branch`.
- **Snakemake 7.32.4 + Python 3.11 pin.** Use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` or `--use-conda`. Per `feedback_no_conda` Carter has gsd-* commands and skips conda activate instructions.
- **Original research framing.** All M2 deliverables framed as hypothesis-driven discovery, not "revision" or "fix" of pre-pivot work.
- **Parallel downloads + max LSF cores.** `xargs -P 5` for any portal download; LSF wall ceilings per `config/cluster_lsf.yaml`.

## Metadata

**Confidence breakdown:**
- M1-pattern reuse (Patterns A–G): HIGH — direct read of M1 source.
- MTAG flag-name + matrix format (Q1, Pitfalls 1–2, 6–7): HIGH on the actual flag (`--residcov_path`); MEDIUM on max-FDR resolution (Carter Q1).
- CPASSOC implementation (Q2, Q7): HIGH — formulas + numerics verified.
- PLINK + bedtools + mtCOJO (Q3, Q4, Q6, Q8): HIGH on PLINK 1.9 + bedtools defaults; MEDIUM on mtCOJO TRANS LD reference choice (Carter Q3).
- GWAS Catalog snapshot (Q5): HIGH — verified URL + size + Last-Modified header pattern.
- AFR PLINK reference build (Pitfall 3): HIGH — gap confirmed via directory probe; build path verified.
- MTAG installation (Pitfall 6): MEDIUM — community-known but not directly tested by this research.

**Research date:** 2026-04-25
**Valid until:** 2026-05-25 (30 days for stable methods + verified URLs; re-verify GWAS Catalog URL + MTAG repo state at M2 fire time).
