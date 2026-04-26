---
phase: m2-ldsc-mtag-cpassoc-discovery
slug: m2-ldsc-mtag-cpassoc-discovery
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-25
updated: 2026-04-26
---

# Phase M2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Source: `m2-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=7 (existing in M1 conda envs; reuse) |
| **Config file** | `pytest.ini` (existing) + `tests/m2/conftest.py` (NEW Wave 0 — mirrors `tests/m1/conftest.py`) |
| **Quick run command** | `pytest tests/m2/ -x --tb=short` |
| **Full suite command** | `pytest tests/m1/ tests/m2/ tests/phase9/ -x` |
| **Estimated runtime** | ~30s (M2 unit) / ~3 min (M1+M2+phase9 full) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/m2/ -x --tb=short`
- **After every plan wave:** Run `pytest tests/m1/ tests/m2/ tests/phase9/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds (unit) / 3 minutes (full)

---

## Per-Task Verification Map

Per ROADMAP M2 Success Criteria 1–6 (RM-1..RM-6) and the 6 phase REQ IDs.

| Task family | Plan/Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Status |
|-------------|-----------|-------------|------------|-----------------|-----------|-------------------|-------------|
| LDSC matrix refire | Plan 01 / Wave 1 | RM-1 + REQ-MTAG-OVERLAP | T-M2-01 (matrix-bytes integrity) | sha256-frozen output; `1.0` diagonal preserved | unit | `pytest tests/m1/test_reduce_ldsc_rg_matrix.py -x` (REUSE existing M1 test) | ✅ existing |
| MTAG residcov slice | Plan 02 / Wave 0 + 2 | REQ-MTAG-OVERLAP | T-M2-02 (trait-order silent mis-alignment) | sidecar `residcov.trait_order.json` created; matrix shape K×K matches `--sumstats` count | unit | `pytest tests/m2/test_build_mtag_residcov_slice.py tests/m2/test_mtag_overlap_matrix_format.py -x` | ❌ Wave 0 |
| MTAG end-to-end | Plan 02 / Wave 2 | RM-2 + REQ-MTAG-OVERLAP | T-M2-03 (vendored MTAG numpy ABI break) | conda env pin `numpy<2`; smoke run produces `mtag_meta_results.txt` | smoke | `snakemake --use-conda mtag_run --config stratum=EUR --dry-run` | ❌ Wave 2 |
| MTAG max_FDR filter | Plan 02 / Wave 2 | RM-2 + D-M2-Q1 | T-M2-04 (Turley post-hoc filter mis-applied) | filtered table has `max_FDR < 0.05` invariant; row count <= MTAG output | unit | `pytest tests/m2/test_mtag_maxfdr_filter.py -x` | ❌ Wave 0 |
| CPASSOC SHom/SHet | Plan 03 / Wave 3 | RM-3 + REQ-CPASSOC-ORTHOGONAL | T-M2-05 (R-matrix ill-conditioning) | pinv condition number gate; ridge regularization applied when `cond > 1e6` | unit + integration | `pytest tests/m2/test_cpassoc_shom_shet.py tests/m2/test_safe_inverse.py -x` | ❌ Wave 0 |
| PLINK clumping | Plan 04 / Wave 4 | RM-4 (region union input) | T-M2-06 (PLINK 2.0 `--clump` missing) | env pin `plink=1.9`; per-(trait,stratum,chr) BED emitted | unit + smoke | `pytest tests/m2/test_plink_clump_invocation.py -x` + `snakemake --use-conda clump_per_trait_chr --dry-run` | ❌ Wave 0 |
| mtCOJO sensitivity | Plan 04 / Wave 4 | RM-6 + D-M2-Q3 + D-M2-Q5 | T-M2-07 (mtCOJO LD reference mis-match) | extreme-overlap filter applied (gcov_int > 0.1); per-stratum LD ref correct | unit | `pytest tests/m2/test_mtcojo_extreme_overlap_filter.py tests/m2/test_mtcojo_eligible_targets.py -x` | ❌ Wave 0 |
| Region union BED | Plan 04 / Wave 4 | RM-4 | T-M2-08 (BED merge tolerance off-by-one) | bedtools merge default settings; provenance JSON column preserved | unit | `pytest tests/m2/test_build_region_union.py -x` | ❌ Wave 0 |
| Class 1 novelty | Plan 05 / Wave 5 | RM-5 + REQ-NOVELTY-CLASS-1 | T-M2-09 (catalog v_lock churn between M2 and M5) | v_lock_M2 row immutable; SHA-256 frozen; `±500 kb` window invariant | unit + integration | `pytest tests/m2/test_call_class1_novelty.py -x` + `pytest tests/m2/test_call_class1_novelty.py::test_end_to_end_synth -x` | ❌ Wave 0 |
| GWAS Catalog v_lock | Plan 01 / Wave 0 | REQ-CATALOG-VERSION-LOCK | T-M2-10 (catalog ETag drift) | new row `gwas_catalog.v_lock_M2` in `catalog_lock_manifest.tsv` with SHA-256 of `.zip` bytes | unit | `pytest tests/m2/test_catalog_lock_manifest_v_lock_M2.py -x` | ❌ Wave 0 |
| 1000G AFR PLINK build | Plan 01 / Wave 0 | RM-4 (input dependency) | T-M2-11 (AFR bfile not present) | 22 chr `.bed/.bim/.fam` triples land at `data/reference/ldsc/1000G_AFR_Phase3_plink/` | unit + integration | `pytest tests/m2/test_1000g_afr_plink_build.py -x` + `snakemake --use-conda m2_build_1000g_afr_plink` (production fire) | ❌ Wave 0 |
| Per-stratum keys | Plan 02–05 / Wave 0 | RM-1..RM-6 (universal guard) | T-M2-12 (per-stratum trait-count under floor) | `_MIN_PER_STRATUM = 3` per D-M2-Q6; `skipped_strata.tsv` row written if violated | unit | `pytest tests/m2/test_m2_stratum_keys.py -x` | ❌ Wave 0 |
| Snakemake CI smoke | Plan 06 / Wave 5 | REQ-SNAKEMAKE-CI | T-M2-13 (smoke regression) | toy 3-locus smoke finishes < 15 min | integration | `snakemake -s tests/toy_3locus/Snakefile.test --cores 2 --use-conda` (extend existing) | partial — extend |
| OSF prereg | (already satisfied) | REQ-OSF-PREREG | (gate-release) | OSF amendment posted at osf.io/az52u/files/k8w7n; gate-release commit d55c1d1 | manual | git log --grep='M2 gate released' | ✅ done |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · ❌ W0 = Wave-0 dependency*

---

## Wave 0 Requirements

- [ ] `tests/m2/conftest.py` — shared M2 fixtures (mirrors `tests/m1/conftest.py`)
- [ ] `tests/m2/test_build_mtag_residcov_slice.py` — REQ-MTAG-OVERLAP / D-M2-10 correction
- [ ] `tests/m2/test_mtag_overlap_matrix_format.py` — REQ-MTAG-OVERLAP residcov format
- [ ] `tests/m2/test_mtag_maxfdr_filter.py` — D-M2-Q1 post-hoc filter
- [ ] `tests/m2/test_cpassoc_shom_shet.py` — REQ-CPASSOC-ORTHOGONAL formulas
- [ ] `tests/m2/test_safe_inverse.py` — pinv + ridge conditioning
- [ ] `tests/m2/test_plink_clump_invocation.py` — PLINK 1.9 clump shell
- [ ] `tests/m2/test_mtcojo_eligible_targets.py` — D-M2-Q5 eligible-target selection
- [ ] `tests/m2/test_mtcojo_extreme_overlap_filter.py` — D-M2-08 + D-M2-Q5 filter
- [ ] `tests/m2/test_build_region_union.py` — D-M2-09 strict union
- [ ] `tests/m2/test_call_class1_novelty.py` — REQ-NOVELTY-CLASS-1 + D-M2-05
- [ ] `tests/m2/test_catalog_lock_manifest_v_lock_M2.py` — REQ-CATALOG-VERSION-LOCK
- [ ] `tests/m2/test_1000g_afr_plink_build.py` — pre-fire smoke for AFR bfile build
- [ ] `tests/m2/test_m2_stratum_keys.py` — D-M2-Q6 floor + universal guard
- [ ] `tests/m2/fixtures/` — synthetic z-score matrices, GWAS Catalog mini-snapshot, MTAG result mini-fixture, mtCOJO output mini-fixture

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OSF amendment paste content matches body source commit `61315de` | REQ-OSF-PREREG | OSF web UI cannot be programmatically diffed | Already verified during 2026-04-25 OSF posting; receipt at `.planning/amendments/osf-amendment-m1-2026-04-25.md` |
| MTAG-novel locus interpretation against contributing single-trait p-values | REQ-NOVELTY-CLASS-1 | Domain interpretation; not formula-checkable | After `joint_signal_novel.tsv` lands, manually inspect top-10 loci against single-trait sumstats for sanity (target: ≤ 1 hr) |
| Carter resume queue items (DIAMANTE cookies, GBMI Wix, Loh D-01, MAGIC EUR re-fetch) | (out of M2 scope) | OSF-portal authentication / external-portal navigation | Items are post-M2 follow-ups recorded in `.planning/m2_post_m3_rerun_queue.tsv` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ Wave-0-blocked references in the verification map
- [ ] No watch-mode flags (pytest -x is fine; no `--watch`)
- [ ] Feedback latency < 30 seconds for unit; < 3 minutes for full
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 completes

**Approval:** pending (awaiting Wave 0 fire)

---

## Wave 0 four-item attestation (CR-checker WR-5)

Attested 2026-04-26 by Carter K. Clinton via /gsd-execute-phase orchestrator approval.

| # | Invariant | Verification command | Result |
|---|-----------|---------------------|--------|
| (a) | AFR PLINK build sample size | `wc -l data/raw/1kg/AFR.samples` AND `wc -l data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.fam` | 504 == 504 (within [490, 520] floor) |
| (b) | GWAS Catalog v_lock_M2 SHA-256 | `sha256sum data/catalogs/gwas-catalog-associations-full.zip` vs manifest row | `652a974d3246748290baa83899d3c8db0027eed76663b767beaee319618961cd` byte-identical (Pitfall 10) |
| (c) | RED tests + pytest collect | `ls tests/m2/test_*.py \| wc -l` AND `pytest tests/m2/ --collect-only` | 13 stub files; 38 tests collected; 0 import errors |
| (d) | MTAG vendored + `--residcov_path` | `cat tools/mtag/.git_pinned_commit` AND `grep -- "--residcov_path" tools/mtag/.git_clone_log` | Pinned `9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc`; flag confirmed (D-M2-10) |
