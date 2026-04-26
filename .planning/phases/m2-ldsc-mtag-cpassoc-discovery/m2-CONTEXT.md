# Phase M2: LDSC + MTAG + CPASSOC discovery — Context

**Gathered:** 2026-04-25
**Status:** Ready for planning
**Slug:** m2-ldsc-mtag-cpassoc-discovery
**Discuss round:** R1 (post M1 closeout 2026-04-25; OSF amendment posted at osf.io/az52u/files/k8w7n; Amendment §9.1 hard gate RELEASED via commit d55c1d1)

<domain>
## Phase Boundary

Run the joint-signal discovery suite that the OSF amendment §3 M2 + §6 + §7.1 pre-registers: pairwise LDSC rg + intercept matrix, MTAG (Turley 2018) with `--overlap` correction, CPASSOC (Zhu 2015) SHom/SHet as orthogonal joint-signal test, mtCOJO sensitivity on extreme-overlap loci, PLINK clumping per (trait × ancestry), union-region BED, and the Class 1 (joint-signal) novelty deliverable `joint_signal_novel.tsv` filtered against a frozen GWAS Catalog v_lock.

In scope: M1-deferral closure for the 14 traits whose harmonized+munged outputs landed post-m1-03 (DEF-M1-03-02 expansion to ~26-trait LDSC matrix); 3 MTAG runs (EUR-9, AFR-9, TRANS-9); CPASSOC implementation + per-locus run; PLINK clumping per (trait × ancestry); region union construction; Class 1 novelty calling; mtCOJO sensitivity on extreme-overlap MTAG-novel loci; GWAS Catalog snapshot at M2 kickoff with SHA-256 lock; provisional 1000G AFR LD reference for AFR clumping/LDSC.

Out of scope (belongs to M3+): AoU AFR WGS LD panel build (M3); two-stage coloc + SuSiE-RSS fine-mapping on union regions (M4); HyPrColoc 5-trait shared-architecture (M4); PolyFun baselineLF2 functional priors (M4); locus-to-gene scoring (M5); Class 2 (AFR-specific) / Class 3 (pleiotropy-coloc) / Class 4 (secondary-signal) / Class 5 (functional-mechanism) novelty (M4–M5); manuscript figures (M6).

Gating: M1 verified PASS + OSF amendment posted (both satisfied 2026-04-25). M2 outputs gate M3 (AoU LD priority ordering hand-off) and M4 (union-region BED).
</domain>

<inputs>
## Inputs Available from M1

**Trait inventory:** `config/trait_inventory.yaml` — 47 cells × 24 fields (9 traits × 4–6 ancestries). 26 cells have `sha256_harmonized` populated and a real harmonized `.tsv.bgz`+`.parquet`+`.tbi` triple on disk under `data/processed/sumstats_harmonized*/`. The other 21 cells are deferred per `deferred-items.md` (DIAMANTE × 4 cookie-pending, GBMI × 3 portal-pending, Loh × 2 D-01 unresolved, Klarin × 1 D-03 unresolved, Aragam EUR sex-strat × 1, MAGIC EUR × 1 truncation, Giri AFR-SBP × 1 → DEC-2026-04-24-02 AoU fallback, plus deferred ancestry-specific singletons).

**LDSC bivariate-intercept matrix (M1-frozen):** `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` (12 × 12, symmetric, diag=1.0, 64/66 pairs filled). OSF mirror: `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv`. This is the M2 MTAG `--overlap` consumer artifact at the 12-trait fallback level.

**Munged HM3 sumstats:** `data/processed/ldsc_overlap/munged/*.sumstats.gz` — currently 12 files. After D-M2-01 refire: ~26 files.

**Harmonized full-coverage sumstats:** `data/processed/sumstats_harmonized/*.tsv.bgz` (+ `.tbi` + `.parquet`). 26 cells available; the same set that have `sha256_harmonized` populated.

**SHA-256 manifests (frozen for OSF):** `.planning/amendments/sha256_manifest_m1_frozen.tsv` (45 raw rows) + `.planning/amendments/sha256_manifest_harmonized_m1.tsv` (73 harmonized rows).

**Pre-registration:** OSF amendment body at [osf.io/az52u/files/k8w7n](https://osf.io/az52u/files/k8w7n) (commit `61315de`). Local source: `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`.

**Decisions inheriting into M2:**
- DEC-2026-04-24-01 (GRCh37 canonical) — all M2 LD reference panels and clumping must use GRCh37 coordinates
- DEC-2026-04-24-02 (AoU AFR-SBP M2 fallback for Giri 2019 D-06) — sbp.AFR cell will land via AoU derivation, not portal download; M2 may proceed without sbp.AFR until that derivation completes
- DEC-2026-04-25-01 (results_identity_ld/ tracking) — orthogonal to M2; informs the .gitignore policy for M2 large output trees
- DEC-2026-04-25-02 (OSF posting form) — defines the cite-pattern for M2 papers
</inputs>

<decisions>
## Locked Decisions (M2 gray-area resolutions, 2026-04-25)

### D-M2-01: LDSC matrix scope — expand to ~26 traits via DEF-M1-03-02 refire before MTAG fires

**Decision:** Re-fire `m1-03-munge-and-ldsc-intercept-matrix` wave (m1_munge.smk + m1_ldsc_rg.smk) against the expanded harmonized inventory (DEF-M1-03-02 GLGC + Wuttke completions that landed post-m1-03 close) to produce a ~26-trait LDSC bivariate-intercept matrix. This becomes the M2 MTAG `--overlap` consumer artifact, replacing the 12×12 frozen artifact for downstream use. The 12×12 stays in `.planning/amendments/bivariate_intercept_matrix_m1_2026-04.tsv` as the OSF posting record; the ~26×26 lands at `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` with a separate OSF-paste mirror `.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv`.

**Alternatives:** (a) 12-trait now as-is (fastest; lowest coverage); (b) full 45×45 (clean but blocks weeks on Carter resume queue); (c) Mix: 26-trait MTAG plus a second-pass M2-extension at M5 against a closed-deferral 45-trait matrix. Rejected (a) for too-sparse joint-signal discovery; rejected (b) for unacceptable timeline cost given the 21 deferrals; rejected (c) as scope creep — M2 produces one MTAG run per the locked grouping (D-M2-03), the matrix can refresh at M5 without triggering an M2 re-fire.

**How to apply:** Wave 0 of M2 plan refires m1-03 wave with `--reason=DEF-M1-03-02-expansion`. Reducer (`reduce_ldsc_rg_matrix.py`) re-runs against the expanded log set. Wave 1 of M2 reads the ~26×26 matrix as the MTAG `--overlap` input.

### D-M2-02: AFR LD reference — provisional 1000G AFR (N=661) for M2; committed re-run after M3 AoU AFR LD lands

**Decision:** Use 1000G Phase 3 AFR (N=661) as the LD reference panel for M2 AFR-stratum PLINK clumping AND for AFR LDSC ld-score regression where AoU LD is unavailable. Document explicitly as PROVISIONAL in DECISIONS.md (will become DEC-2026-04-25-03). Commit M3 hand-off requirement: after M3 lands the AoU AFR WGS LD panel (~100k samples per AOU-LD-PIPELINE.md), re-run AFR clumping + AFR LDSC steps with the AoU panel; supersede M2 AFR results. Both result sets are kept on disk; the AoU-AFR-LD set is canonical for M4+ downstream consumers and for manuscript reporting.

**Alternatives:** (a) Serial: defer M2-AFR until M3 done — adds months delay; (b) EUR + TRANS only — drops Class 2 prep entirely; (c) 1000G AFR with no M3 re-run commitment — breaks amendment §3(f). Adopted middle path.

**How to apply:** M2 Snakemake rules for AFR clumping declare `lref: data/external/1000G/phase3/AFR/{chr}` as the LD-reference path (existing pre-pivot infra). Output filenames carry an `LD-1000G-AFR` token so the M3-superseding outputs (`LD-AoU-AFR`) are easy to distinguish. M2 plan adds a closing task that emits a "post-M3 re-run trigger" entry into a new `.planning/m2_post_m3_rerun_queue.tsv` so the dependency is durable.

### D-M2-03: MTAG trait grouping — three per-ancestry + TRANS mega-runs (EUR-9, AFR-9, TRANS-9)

**Decision:** Run MTAG three times: once over all 9 traits in EUR (using each trait's `.EUR.*` munged file), once over all 9 traits in AFR (using `.AFR.*` munged where available; per D-M2-06 skip-with-doc traits without an AFR stratum), and once over all 9 traits in TRANS (using `.TRANS.*` or `.MULTI.*` munged where available). Three sets of MTAG-novel hit lists feed into the union region BED.

**Alternatives:** (a) Per-ancestry only (EUR + AFR, no TRANS) — simpler but loses trans-ancestry joint-signal coverage; (b) Cluster-based on rg ≥ 0.4 — better-conditioned MTAG covariance but harder to interpret novelty by cluster; (c) Per-trait-pair rolling sets — 36+ runs per ancestry, not the canonical Turley use. Carter overrode the Recommended (a) in favor of broader ancestry coverage.

**How to apply:** M2 Snakemake rule `mtag_run` parameterized by wildcard `{stratum}` ∈ {EUR, AFR, TRANS}. MTAG `--sumstats` arg builds a comma-list of munged paths for the 9 traits filtered by stratum availability. The `--overlap` arg consumes the slice of the ~26-trait LDSC intercept matrix matching the input traits. Output goes to `data/processed/mtag/{stratum}/` per-trait `.txt` tables (Turley convention). Union-region BED ingests MTAG-novel leads from all 3 strata.

### D-M2-04: CPASSOC build — Python reimplementation, LDSC intercept matrix as cohort-correlation input

**Decision:** Reimplement Zhu 2015's SHom and SHet test statistics directly in Python (~50–100 LoC at `src/python/cpassoc.py`), with the LDSC pairwise bivariate-intercept matrix from M1 (re-fired in D-M2-01 to ~26-trait) as the cohort-correlation matrix R. Formulas:

- SHom: `z' R^-1 z` (chi-square, df=K, tests homogeneous pleiotropic effect)
- SHet: `z' (R^-1 - R^-1 1 (1' R^-1 1)^-1 1' R^-1) z` (chi-square, df=K-1, tests heterogeneous pleiotropic effect)

LDSC intercept matrix is mathematically equivalent (Bulik-Sullivan derivation) to Zhu's null-SNP empirical correlation, with the advantage that it's already estimated and frozen. No MATLAB port, no R port, no separate empirical-correlation estimation step.

**Alternatives:** (a) Reimplement Python + null-SNP empirical R (re-derives information already in hand); (b) Port Zhu MATLAB → R/Python (1–2 weeks for negligible numerical-identity gain); (c) Reimplement R + LDSC intercept (splits M2 across languages — MTAG/PLINK are CLI, downstream M4 coloc/SuSiE is R, but M2 itself is best kept Python).

**How to apply:** New module `src/python/cpassoc.py` with `cpassoc_shom(z, R)` and `cpassoc_shet(z, R)` functions vectorized over SNPs. Pytest fixtures: 100-SNP synthetic z-score matrix with ground-truth R; cross-check against Zhu 2015 paper Table 1 example values where reproducible. Snakemake rule `cpassoc_run` parameterized by `{stratum}` per D-M2-03 grouping; outputs per-locus SHom/SHet `.tsv` tables to `data/processed/cpassoc/{stratum}/`.

### D-M2-05: GWAS Catalog v_lock — snapshot at M2 kickoff (~2026-04-26) + refresh at M5

**Decision:** Pull a fresh GWAS Catalog snapshot at M2 kickoff. Lock the URL + ETag + SHA-256 + fetch-date in `data/catalogs/catalog_lock_manifest.tsv` (the existing M0 manifest gains a new row keyed `gwas_catalog.v_lock_M2`). Compute interim Class 1 novelty for M2's `joint_signal_novel.tsv` deliverable using this snapshot. At M5, when the M5-deferred catalog rows lock per the OSF amendment closing disclosure, re-run the novelty filter against the M5-locked GWAS Catalog version; report the diff (additions, drops, churn) as a follow-up OSF update.

**Alternatives:** (a) Wait for M5 lock — produces no Class 1 novelty deliverable in M2, breaks success criterion #5 (`joint_signal_novel.tsv`); (b) Snapshot now as final — deviates from amendment's M5-deferred catalog disclosure. Adopted middle path.

**How to apply:** M2 Wave 0 includes a download task `download_gwas_catalog_M2` that pulls the EBI all-associations TSV, computes SHA-256, appends a row to `data/catalogs/catalog_lock_manifest.tsv` with key `gwas_catalog.v_lock_M2`, fetch-date, URL, ETag, SHA-256. M2 novelty rule reads only the v_lock_M2 row. M5 will append a `gwas_catalog.v_lock_M5` row + a `gwas_catalog_lock_diff_M2_to_M5.tsv` artifact.

### D-M2-06: Trait stratum selection — strict ancestry match, skip-with-doc when missing

**Decision:** EUR cell uses `.EUR.*` munged sumstats; AFR cell uses `.AFR.*`; TRANS cell uses `.TRANS.*` (or `.MULTI.*` for GBMI). Traits without an ancestry stratum (e.g. CKDGen 2019 has no AFR-specific release; Aragam 2022 CAD has no AFR-specific stratum) are skipped from the corresponding MTAG/CPASSOC run with a documented gap entry in `m2-deferred-items.md` and a row in `data/processed/mtag/{stratum}/skipped_traits.tsv`.

**Alternatives:** (a) Fall back to TRANS where ancestry missing — mixes ancestry semantics in stratum runs, complicates Class 2 AFR-specific novelty; (b) Per-ancestry priority list — most explicit but requires manual curation upfront. Adopted strict + skip.

**How to apply:** Snakemake rule generation iterates the 9-trait × 3-stratum grid (27 cells) and skips cells where the matching `munged_path` from `trait_inventory.yaml` has `qc_status: MISSING` or no stratum-matching file exists. Skipped cells emit a row to `skipped_traits.tsv` with reason field linking to `deferred-items.md` or `trait_inventory.yaml`.

### D-M2-07: MTAG max_FDR threshold — Turley default 0.05

**Decision:** Apply MTAG `--max-FDR-threshold 0.05` per the Turley 2018 default. Hits with `max_FDR < 0.05` qualify for downstream Class 1 novelty consideration; loci above are filtered out before novelty calling.

**Alternatives:** (a) 0.01 stricter (may filter borderline novel loci); (b) sweep both 0.05 and 0.01 (post-hoc filter, negligible compute cost) — defensible but adds an interpretation column. Adopted default per literature convention and amendment text "max_FDR filter per Turley 2018".

**How to apply:** Snakemake rule `mtag_run` adds `--max-FDR-threshold 0.05` to the MTAG CLI invocation. Post-MTAG novelty filter (`call_class1_novelty.py`) reads `max_FDR` column and filters at the same threshold for self-consistency.

### D-M2-08: mtCOJO sensitivity scope — all loci with extreme overlap (gcov_int > 0.1)

**Decision:** Apply mtCOJO (Zhu 2018) to every MTAG-novel locus where the bivariate-intercept-matrix gcov_int with any contributing trait exceeds 0.1 (Turley 2018 §"sample overlap" recommended threshold). Data-driven; if 5 loci qualify, that's how many; if 80 do, that's how many. Avoids arbitrary truncation by p-value rank.

**Alternatives:** (a) Top-20 / top-50 by p-value (arbitrary, may skip overlap-extreme loci with mid-tier p-values); (b) all MTAG-novel regardless (mostly redundant where intercepts are near zero, longer wall time). Adopted threshold-driven.

**How to apply:** Snakemake rule `mtcojo_run` consumes the MTAG-novel hit list, joins on the LDSC bivariate-intercept matrix, filters to loci where any (trait, contributing-trait) pair has `gcov_int > 0.1`, and runs mtCOJO per-locus. Output sensitivity table at `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv` with columns: locus_id, MTAG_p_original, mtCOJO_p, max_overlapping_intercept, sensitivity_flag (PASS / WARN / FAIL).

### D-M2-09: Region union policy — strict union of clumped + MTAG-novel + CPASSOC-novel leads, ±1 Mb windows, merged

**Decision:** Discovery region BED = strict union of:
- Per-(trait × ancestry) PLINK clumped lead variants (p < 5e-8, r² < 0.01, 1 Mb clump window) → 9 traits × 3 strata = up to 27 cells (less for skipped per D-M2-06)
- MTAG-novel lead variants from each of the 3 stratum runs (D-M2-03)
- CPASSOC-novel lead variants from each of the 3 stratum runs (per D-M2-04)

Each lead carries a ±1 Mb window. Bedtools merge collapses overlapping intervals. Expected output: 1,500–3,000 regions per amendment text. Each region carries a provenance tag set so downstream M4 can prioritize Tier 1 = MTAG ∩ CPASSOC regions.

**Alternatives:** (a) Tiered-only (no strict union, just provenance tags) — strictly more information than union but partially redundant; (b) Intersection-only — contradicts amendment text "union". Adopted strict union per amendment, with provenance tags as a free-add column.

**How to apply:** New module `src/python/build_region_union.py`. Inputs: clumped lead BEDs from all (trait × stratum) cells, MTAG-novel lead lists from 3 strata, CPASSOC-novel lead lists from 3 strata. Output: `results/regions/union_region_list.bed` (4-column BED + provenance JSON column) per ROADMAP success criterion 4. Provenance JSON encodes which of {clump, mtag, cpassoc} contributed and at which stratum.

### D-M2-10: Sample-overlap correction scope — full LDSC pairwise intercept matrix as universal --overlap

**Decision:** MTAG `--overlap` consumes the full ~26×26 LDSC bivariate-intercept matrix (D-M2-01 refire output) for the universal cohort-overlap correction. Off-diagonal pairs include all overlap structure: UKB ∩ MVP per REQ-MTAG-OVERLAP literal text, plus deCODE ∩ HUNT, ARIC ∩ FHS, GIANT ∩ 23andMe, GLGC ∩ ICBP, etc., as encoded by the bivariate intercepts.

**Alternatives:** (a) UKB/MVP only per REQ literal — under-corrects by ignoring all other shared cohorts; (b) threshold intercept > 0.05 — introduces a non-standard parameter. Adopted Turley-recommended approach.

**How to apply:** MTAG `--overlap` flag set to the path of the full ~26×26 matrix. No off-diagonal zeroing or thresholding. The LDSC intercept matrix derivation in M1 (`reduce_ldsc_rg_matrix.py`) already enforces symmetry and diag=1.0 invariants; M2 reuses it without modification.
</decisions>

<artifacts>
## Expected Deliverable Artifacts (per ROADMAP M2 + amendment §3)

| # | Path | Source | Class |
|---|------|--------|-------|
| 1 | `data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv` | D-M2-01 refire (~26×26) | reproducibility |
| 2 | `.planning/amendments/bivariate_intercept_matrix_m2_2026-04.tsv` | OSF mirror of #1 | reproducibility |
| 3 | `data/processed/mtag/{EUR,AFR,TRANS}/{trait}_mtag.txt` | D-M2-03 × D-M2-07 | discovery |
| 4 | `data/processed/cpassoc/{EUR,AFR,TRANS}/{trait}_cpassoc.tsv` | D-M2-04 | discovery |
| 5 | `data/processed/clumping/{ancestry}/{trait}_clump.bed` | PLINK clump per (trait × ancestry) | discovery |
| 6 | `data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv` | D-M2-08 | sensitivity |
| 7 | `results/regions/union_region_list.bed` | D-M2-09 | M3+M4 hand-off |
| 8 | `results/novelty/joint_signal_novel.tsv` | Class 1 per D-M2-05 + D-M2-07 | novelty deliverable |
| 9 | `data/catalogs/catalog_lock_manifest.tsv` row `gwas_catalog.v_lock_M2` | D-M2-05 | reproducibility |
| 10 | `.planning/m2_post_m3_rerun_queue.tsv` | D-M2-02 | M3 hand-off |
| 11 | `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md` | D-M2-06 + others | gap log |
| 12 | `.planning/amendments/sha256_manifest_m2_frozen.tsv` | M2 closeout SHA-256 freeze | OSF |
| 13 | `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md` | M2 verifier output | governance |

## Test artifacts

| Path | Purpose |
|------|---------|
| `tests/m2/test_cpassoc_shom_shet.py` | Cross-check D-M2-04 reimplementation against Zhu 2015 paper values |
| `tests/m2/test_build_region_union.py` | Strict-union semantics + provenance tag preservation |
| `tests/m2/test_call_class1_novelty.py` | Class 1 filter logic against synthetic catalog snapshot |
| `tests/m2/test_mtag_overlap_matrix_slice.py` | Matrix slicing for the per-stratum trait subset |
| `tests/m2/test_mtcojo_extreme_overlap_filter.py` | gcov_int > 0.1 selection logic |
</artifacts>

<requirements_traceability>
## Requirement-ID Coverage

| REQ ID | M2 deliverable that closes it | Notes |
|--------|------------------------------|-------|
| REQ-MTAG-OVERLAP | mtag/*.txt + mtcojo_sensitivity.tsv | D-M2-07 max_FDR + D-M2-08 mtCOJO + D-M2-10 universal correction |
| REQ-CPASSOC-ORTHOGONAL | cpassoc/*.tsv + joint_signal_novel.tsv (MTAG ∩ CPASSOC subset) | D-M2-04 |
| REQ-NOVELTY-CLASS-1 | joint_signal_novel.tsv | D-M2-05 (catalog v_lock) + D-M2-07 (max_FDR) |
| REQ-OSF-PREREG | Already satisfied 2026-04-25 by OSF posting at osf.io/az52u/files/k8w7n; M2 inherits | Gate-release commit d55c1d1 |
| REQ-SNAKEMAKE-CI | M2 Snakemake rules included in main pipeline; smoke-test target added | Same convention as M1 |
| REQ-CATALOG-VERSION-LOCK | catalog_lock_manifest.tsv row gwas_catalog.v_lock_M2 | D-M2-05 |
</requirements_traceability>

<deferred_ideas>
## Deferred Ideas (out of M2 scope; capture for backlog)

- **Class 2 AFR-specific novelty pre-call.** D-M2-09 produces the union region list and annotates AFR-stratum lead variants. The Class 2 actual call (AFR PP.H4 ≥ 0.8 + |CS| ≤ 25) is M4 scope per amendment §7.1.
- **HyPrColoc 5-trait shared-architecture run.** M4 scope.
- **Cluster-based MTAG run as a robustness check.** Could re-run MTAG on rg ≥ 0.4 trait clusters as a sensitivity analysis; noted as a candidate M5/M6 robustness-check phase.
- **mtCOJO on all MTAG-novel loci regardless of overlap severity.** D-M2-08 thresholds at gcov_int > 0.1; a future re-run could expand this for completeness. Not blocking M2.
- **45×45 LDSC matrix expansion.** Once Carter resume queue clears (DIAMANTE cookies, GBMI Wix, Loh D-01 accession, MAGIC EUR re-fetch, Aragam EUR sex-strat, Klarin), refire m1-03 wave once more. Triggers a M2 re-fire with the larger matrix; reported as a follow-up.
- **Borzoi / Enformer functional-mechanism scoring on union regions.** M5 scope (REQ-NOVELTY-CLASS-5).
</deferred_ideas>

<assumptions>
## Assumptions Carter has validated

1. **MTAG, CPASSOC, mtCOJO are public open-source.** MTAG: github.com/JonJala/mtag. CPASSOC: paper-supplied MATLAB → reimplemented per D-M2-04. mtCOJO: bundled with GCTA. All install via conda or pip; no DUA.
2. **PLINK clumping with 1000G EUR / AFR LD reference panels is sufficient for M2 discovery clumping**, with the M3-supersede commitment (D-M2-02) for AFR. EUR is final at M2.
3. **The 12-trait LDSC matrix is sparser than M2 needs but the ~26-trait expansion (D-M2-01) is achievable in 1 day LSF wall** since GLGC + Wuttke harmonized files already landed and only the m1-03 munge + LDSC star-pattern needs to refire.
4. **GWAS Catalog snapshot fetch is deterministic and < 1 hour** (the EBI all-associations TSV is ~500 MB; SHA-256 logged for reproducibility).
5. **The ~1,500–3,000 region count from amendment §3 is approximate and the actual count drives M3 + M4 compute budget downstream**; a count of 500 or 5,000 is fine — the count is reported in M2 closeout.
6. **The "skip-with-doc" pattern from D-M2-06 + the universal `m1_raw_glob.py`-style guard from M1 are reusable for M2.** Same pattern; M2 plan references M1 implementation.
</assumptions>

<open_questions>
## Open Questions for Research / Planning Agents (NOT for Carter)

These are technical-implementation choices the research agent should answer when it scouts:

1. **MTAG `--overlap` matrix file format.** MTAG accepts a TSV path; check that the `reduce_ldsc_rg_matrix.py` output format matches MTAG's expected schema (column order, header convention, off-diagonal symmetry).
2. **CPASSOC R inversion conditioning.** When the LDSC intercept matrix has near-rank-deficient blocks, R^-1 may need pseudo-inversion or ridge regularization. Research agent: investigate whether Zhu 2015 specifies a conditioning treatment, and what `numpy.linalg.pinv` vs `scipy.linalg.lstsq` give us numerically.
3. **PLINK clumping memory budget at chr-level.** ~26 traits × 3 strata × 22 chromosomes = 1,716 PLINK invocations. Research agent: what's the per-job memory ceiling, can we batch by chromosome on LSF standard queue, and is there a faster GCTA-COJO equivalent for clumping that we should use instead?
4. **mtCOJO reference genotype panel.** mtCOJO needs an LD reference. EUR uses 1000G EUR (existing). AFR per D-M2-02 uses 1000G AFR. TRANS — research agent: check Zhu 2018 for the recommended trans-ancestry reference; if undefined, the simplest defensible default is 1000G EUR per the convention that trans-ancestry meta-analyses tend to be EUR-dominant.
5. **GWAS Catalog ETag stability and download mechanism.** Research agent: confirm the EBI all-associations TSV download URL is stable + check ETag header support so the catalog_lock_manifest entry can use the same sha256-freeze pattern as M1's SUMSTATS-UPGRADE.tsv.
6. **Region merge tolerance.** D-M2-09 uses bedtools merge on ±1 Mb windows around lead variants. Research agent: should the merge be strict (any overlap collapses) or stranded/min-overlap? Default to strict per bedtools default.
7. **Per-stratum CPASSOC R matrix slicing.** The full ~26×26 R applies across all traits; per-stratum CPASSOC needs the slice corresponding to the traits in that stratum's mega-run. Research agent: confirm the slicing is preserves positive-definiteness (it should, since principal submatrices of a PSD matrix are PSD).
8. **mtCOJO output schema and joining keys.** Research agent: confirm mtCOJO output column names so the sensitivity-table builder joins correctly.
</open_questions>

<next_step>
## Next Step

Run `/gsd-plan-phase m2-ldsc-mtag-cpassoc-discovery` to:
1. Spawn `gsd-phase-researcher` agent to investigate the 8 open_questions above + scout existing patterns (M1 m1_raw_glob.py, m1_trait_keys.py, sumstats_utils.py, snakemake rule conventions)
2. Spawn `gsd-planner` agent to break M2 into atomic plans + waves consistent with the locked decisions in this CONTEXT.md
3. Spawn `gsd-plan-checker` agent for goal-backward review

The OSF amendment §9.1 hard gate is RELEASED (commit d55c1d1, 2026-04-25). M2 may now commit.
</next_step>

<research_surfaced_resolutions>
## Research-Surfaced Resolutions (added 2026-04-25 post-research)

The gsd-phase-researcher agent (commit `c1a0caa`, output at `m2-RESEARCH.md`) surfaced 1 critical correction + 6 sub-decisions not anticipated in the original 10 D-M2-XX gray areas. All are resolved here.

### CRITICAL — D-M2-10 flag-name correction

**Issue:** D-M2-10 (and the prose throughout this CONTEXT.md) refers to "MTAG `--overlap`" as the cohort-overlap correction flag. **MTAG does NOT have a `--overlap` flag.** The actual MTAG CLI flag is **`--residcov_path`** — a path to a `.npy` or whitespace-delimited `.txt` file containing a bare numeric K×K matrix (no header, no row index).

**Resolution:** All M2 plans MUST use `--residcov_path` as the actual MTAG CLI flag. The colloquial name "--overlap" appearing in CONTEXT.md, REQ-MTAG-OVERLAP, and OSF amendment text is fine for human-language description but the implementation MUST emit:
- A bare numeric K×K matrix file (slice of the M1 ~26×26 LDSC bivariate-intercept matrix matching the K traits in this stratum's MTAG run) at `data/processed/mtag/{stratum}/residcov.txt`
- A sidecar `data/processed/mtag/{stratum}/residcov.trait_order.json` recording the trait-order alignment with `--sumstats` (Pitfall 7 in m2-RESEARCH.md — silent mis-alignment if order diverges between `--sumstats` and `--residcov_path`).

A new helper module `src/python/build_mtag_residcov_slice.py` is the M2 plan task that performs this slicing.

### D-M2-Q1 — MTAG max-FDR threshold implementation

**Decision:** Apply `mtag_maxFDR.py` post-hoc filter on each MTAG run output, dropping loci with `max_FDR ≥ 0.05` per Turley 2018 Methods §"maxFDR". This is a SECOND Snakemake rule per stratum (one for the main MTAG run, one for the post-hoc filter). Aligns with research recommendation (a). NOT `--p_sig` interpretation.

**How to apply:** Snakemake DAG: `mtag_run` → emits `mtag_meta_results.txt`; `mtag_maxfdr_filter` → reads MTAG output and `mtag_maxFDR.py`-script output and writes filtered table. Class 1 novelty consumer reads the filtered table.

### D-M2-Q2 — AFR LDSC ld-score reference (Carter answered)

**Decision:** Stay with EUR cross-ancestry approximation (using existing `data/external/ldscore/eur_w_ld_chr/`) for ALL ancestries' h2/rg estimates in M2 — including the AFR-stratum LDSC matrix slice. Matches M1 convention (the M1 12-trait matrix already used EUR ld-scores cross-ancestry). AFR LDSC re-run with proper AFR ld-scores enters the M3-supersede queue when the AoU AFR LD panel lands.

**Rationale:** The OSF amendment §3 (f) commits to AoU AFR WGS LD as the canonical AFR LD reference. M2's AFR LDSC is provisional and gets superseded at M3 anyway; staging 1000G AFR ld-scores at M2 Wave 0 just adds work that gets thrown away.

### D-M2-Q3 — mtCOJO TRANS-stratum LD reference

**Decision:** TRANS-stratum mtCOJO uses 1000G EUR as the primary LD reference, with a 1000G AFR sensitivity check on TRANS-stratum mtCOJO-novel loci. Aligns with research recommendation. EUR-dominant trans-ancestry meta-analyses make EUR the defensible primary; AFR sensitivity catches loci where the EUR LD assumption fails.

**How to apply:** Snakemake `mtcojo_run` rule has wildcard `{stratum}` ∈ {EUR, AFR, TRANS}. For TRANS, the rule fires twice — once with `--ref-ld-chr 1000G_EUR_Phase3_plink/` (primary), once with `--ref-ld-chr 1000G_AFR_Phase3_plink/` (sensitivity, optional). Sensitivity table joins both on locus_id and reports concordance.

### D-M2-Q4 — M2 closeout QC report scope (Carter answered)

**Decision:** Python verifier only (`src/python/verify_m2_artifacts.py`). Quarto HTML deferred to a follow-up phase or rolled into M6 manuscript figures. Matches research recommendation.

**How to apply:** M2 plan adds one closeout task `verify_m2_artifacts` modeled directly on `verify_m1_artifacts.py`. No `m2_qc_report.qmd` task; no `envs/m2-qc.yml`. Saves ~1 day of plan work.

### D-M2-Q5 — mtCOJO target-trait scope per stratum

**Decision:** Run mtCOJO ONLY for target traits where MTAG produced a novel locus AND the bivariate-intercept-matrix gcov_int with any contributing trait exceeds 0.1 (D-M2-08 threshold). MTAG-null target traits do not get mtCOJO confirmation. Aligns with research recommendation.

**How to apply:** Wave 4 task `mtcojo_eligible_targets` reads MTAG-novel hit lists + LDSC intercept matrix, emits a TSV of (target_trait, stratum) tuples that need mtCOJO. The downstream `mtcojo_run` rule iterates only these tuples. Worst case ~3 mtCOJO invocations per stratum × 3 strata = 9 runs total; expected fewer.

### D-M2-Q6 — Per-stratum trait-count floor (Carter answered)

**Decision:** Soft floor of ≥3 traits per stratum. AFR MTAG fires with whatever is available, minimum 3 traits. Aligns with research recommendation. AFR-stratum joint-signal discovery is sparser than EUR; coverage improves at M3 (AoU LD) and M5 (deferred-trait closure).

**How to apply:** `src/python/m2_stratum_keys.py` helper has `_MIN_PER_STRATUM = 3` (not the research's defensive 5). Strata with fewer than 3 traits emit a `skipped_strata.tsv` row with reason and skip the MTAG/CPASSOC run. EUR will always have 9; AFR is expected to have 5–7; TRANS expected 6–8.

### Summary table

| ID | Source | Decision | Status |
|----|--------|----------|--------|
| D-M2-10 correction | RESEARCH Pitfall 1 | MTAG flag is `--residcov_path`, not `--overlap`. Implement bare-matrix output + sidecar trait_order.json. | CRITICAL — resolved |
| D-M2-Q1 | RESEARCH Q1 | `mtag_maxFDR.py` post-hoc filter on each MTAG run | resolved (research recommended) |
| D-M2-Q2 | RESEARCH Q2 | EUR ld-scores for ALL ancestries (M1 convention); AFR LDSC re-run is M3-supersede | resolved (Carter) |
| D-M2-Q3 | RESEARCH Q3 | 1000G EUR primary + 1000G AFR sensitivity for TRANS mtCOJO | resolved (research recommended) |
| D-M2-Q4 | RESEARCH Q4 | Python verifier only; defer Quarto QC | resolved (Carter) |
| D-M2-Q5 | RESEARCH Q5 | mtCOJO only for MTAG-novel target traits with extreme overlap | resolved (research recommended) |
| D-M2-Q6 | RESEARCH Q6 | Soft floor `_MIN_PER_STRATUM = 3` | resolved (Carter) |
</research_surfaced_resolutions>
