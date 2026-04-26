---
phase: m2-ldsc-mtag-cpassoc-discovery
plan: 00
subsystem: infra
tags: [pytest, conda, mtag, plink, 1000g-afr, gwas-catalog, cpassoc, snakemake, m2-preflight]

# Dependency graph
requires:
  - phase: m1-sumstats-upgrade-and-harmonization
    provides: harmonized 26-trait sumstats inventory + LDSC-ready munged files (input set for Wave 1 LDSC matrix refire)
  - phase: 0-data-access-infrastructure
    provides: data/raw/1kg/vcf/chr*.vcf.gz + data/raw/1kg/AFR.samples (input for AFR PLINK bfile build, Pitfall 3)
provides:
  - "13 RED pytest stubs at tests/m2/test_*.py + tests/m2/conftest.py + tests/m2/fixtures/.gitkeep (38 tests collected, 0 import errors)"
  - "Six new conda env files at envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml (numpy<2 / plink=1.9 / gcta / bedtools=2.31 pinned per Pitfalls 4-6)"
  - "Vendored MTAG at tools/mtag/ pinned to JonJala/mtag commit 9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc with --residcov_path flag confirmed (D-M2-10)"
  - "1000G AFR PLINK bfile tree at data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam} (66 files, 504 samples, Pitfall 3 BLOCKING resolved)"
  - "GWAS Catalog v_lock_M2 at data/catalogs/gwas-catalog-associations-full.zip (SHA-256 = 652a974d3246748290baa83899d3c8db0027eed76663b767beaee319618961cd, 59,182,255 bytes) + manifest row in catalog_lock_manifest.tsv (REQ-CATALOG-VERSION-LOCK, Pitfall 10)"
  - "src/python/cpassoc.py (135 lines) — Zhu 2015 SHom + SHet + _safe_inverse with conditional ridge fallback (D-M2-04, D-M2-Q2)"
  - "src/python/m2_stratum_keys.py (136 lines) — keys_for_stratum() with _MIN_PER_STRATUM=3 floor + STRATA = ('EUR', 'AFR', 'TRANS') (D-M2-06, D-M2-Q6, Pattern B)"
  - "src/snakemake/rules/m2_reference.smk — m2_build_1000g_afr_plink rule (PLINK 1.9 --vcf --keep AFR.samples --make-bed per chr)"
  - "Wave 0 four-item attestation appended to m2-VALIDATION.md (CR-checker WR-5)"
  - "m2-VALIDATION.md frontmatter flipped to nyquist_compliant: true + wave_0_complete: true"
affects: [m2-01-ldsc-matrix-refire, m2-02-mtag-3-strata, m2-03-cpassoc-3-strata, m2-04-clumping-mtcojo-regions, m2-05-class1-novelty-and-closeout, m3-aou-afr-ld-build]

# Tech tracking
tech-stack:
  added: [MTAG (vendored), 1000G AFR PLINK bfiles, GWAS Catalog v_lock_M2 snapshot, CPASSOC SHom/SHet, m2_stratum_keys helper]
  patterns: [Pattern B (deterministic stratum-key enumeration with floor), Pattern D (per-rule conda env with ABI-pinned numpy<2), Pitfall 3 (AFR PLINK from raw VCF), Pitfall 6 (vendor MTAG; pip install mtag does not exist), Pitfall 10 (hash .zip bytes for catalog freeze), CR-checker WR-5 (per-item Wave 0 attestation)]

key-files:
  created:
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
    - tools/mtag/mtag.py (+ vendored repo + .git_pinned_commit + .git_clone_log)
    - data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam} (66 files)
    - src/snakemake/rules/m2_reference.smk
    - data/catalogs/gwas-catalog-associations-full.zip
    - src/python/cpassoc.py
    - src/python/m2_stratum_keys.py
  modified:
    - data/catalogs/catalog_lock_manifest.tsv (new gwas_catalog.v_lock_M2 row)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md (frontmatter flip + Wave 0 attestation section)
    - .planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md (Task 1 acceptance criterion 14 → 13)

key-decisions:
  - "Wave 0 test stub count fixed at 13 (not 14) — matches must_haves.truths and m2-VALIDATION.md Wave 0 Requirements; plan-text typo corrected at L244 under CR-checker WR-5 per Carter sign-off"
  - "MTAG --help live invocation deferred to Wave 2 conda env build; static-grep verification of --residcov_path argparse entry in tools/mtag/.git_clone_log accepted as functionally equivalent for Wave 0 audit (Task 9 (d))"
  - "GWAS Catalog v_lock_M2 frozen at 2026-04-21_full_release with SHA-256 byte-hash recorded; Pitfall 10 (hash .zip bytes not extracted contents) honored"
  - "Per-item four-attestation pattern (CR-checker WR-5) adopted for high-stakes Wave-0 → Wave-1 gate transitions; Carter approves each invariant separately rather than a single composite checkpoint"

patterns-established:
  - "Pattern B: deterministic stratum-key enumeration with _MIN_PER_STRATUM = 3 floor and skipped_strata.tsv emission on violation (D-M2-Q6)"
  - "Pattern D: per-rule conda env (envs/m2-{family}.yml) with ABI-pinned numpy<2 for MTAG/LDSC compatibility and plink=1.9 for clumping (Pitfalls 4-6)"
  - "CR-checker WR-5: per-item four-attestation for Wave 0 sign-off (Carter explicitly attests (a) AFR PLINK build / (b) GWAS Catalog SHA / (c) RED test count / (d) MTAG vendoring before Wave 1 starts)"
  - "Pitfall 3: AFR PLINK bfiles must be built from raw 1000G VCF + AFR.samples (no AFR .bed/.bim/.fam exists in upstream LDSC distribution; only .frq files)"
  - "Pitfall 6: MTAG must be vendored from JonJala/mtag.git at pinned commit; pip install mtag returns the wrong PyPI package"
  - "Pitfall 10: catalog version-lock hashes .zip bytes (not extracted contents) to freeze GWAS Catalog snapshot reproducibly"

requirements-completed: [REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL, REQ-NOVELTY-CLASS-1, REQ-CATALOG-VERSION-LOCK, REQ-SNAKEMAKE-CI]

# Metrics
duration: ~59 min (Task 1 RED commit at 15:14 → Wave 0 attestation commit at 16:13; includes ~25 min Carter checkpoint review)
completed: 2026-04-26
---

# Phase M2 Plan 00: Preflight and Environment Summary

**Wave 0 foundation for the M2 LDSC + MTAG + CPASSOC discovery phase: 13 RED pytest stubs, 6 conda env files, vendored MTAG (commit `9e17f3cf`), 22-chr 1000G AFR PLINK bfile build (504 samples, Pitfall 3 resolved), GWAS Catalog v_lock_M2 frozen by SHA-256, Zhu 2015 CPASSOC SHom/SHet module, and per-stratum trait-key helper with `_MIN_PER_STRATUM=3` floor — all eight deliverables landed atomically; Carter approved both Wave 0 sign-off checkpoints under CR-checker WR-5.**

## Performance

- **Duration:** ~59 min wall (33 min Tasks 1–7 + 25 min checkpoint review + 1 min closeout)
- **Started:** 2026-04-26T15:14:27Z (Task 1 RED commit `740d8fc`)
- **Completed:** 2026-04-26T16:13:21Z (Wave 0 attestation commit `99c7602`)
- **Tasks:** 9 of 9 (Tasks 1–7 atomic auto, Tasks 8–9 checkpoint:human-verify both APPROVED)
- **Files modified:** 27 created + 3 modified across tests/, envs/, tools/, data/, src/, .planning/

## Accomplishments

- 13 RED pytest stubs covering every Wave 1+ unit test family (REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL, D-M2-Q1, D-M2-Q5, D-M2-Q6, REQ-NOVELTY-CLASS-1, REQ-CATALOG-VERSION-LOCK)
- 22-chr 1000G AFR PLINK bfile tree built from raw 1000G VCF + AFR.samples — closes Pitfall 3 (no upstream AFR `.bed/.bim/.fam`); 504 AFR samples confirmed at chr22.fam matches AFR.samples roster
- GWAS Catalog v_lock_M2 frozen by SHA-256 of `.zip` bytes (Pitfall 10 honored; ETag drift mitigated per T-M2-10)
- MTAG vendored at pinned commit `9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc` with `--residcov_path` flag confirmed via static argparse grep (D-M2-10)
- Zhu 2015 CPASSOC SHom + SHet + `_safe_inverse` (with conditional ridge fallback) module landed (D-M2-04, D-M2-Q2)
- `m2_stratum_keys.keys_for_stratum()` exports `_MIN_PER_STRATUM = 3` per D-M2-Q6 universal-guard pattern
- Wave 1 (`m2-01-ldsc-matrix-refire`) cleared to start; m2-VALIDATION.md frontmatter flipped to `nyquist_compliant: true`

## Task Commits

Each task was committed atomically:

1. **Task 1: pytest scaffolding for M2 (RED phase, 13 unit-test files + conftest + fixtures/)** — `740d8fc` (test)
2. **Task 2: Six conda env files (envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml)** — `cf6d989` (chore)
3. **Task 3: Vendor MTAG at tools/mtag/ + verify --residcov_path** — `6586994` (chore)
4. **Task 4a: m2_reference.smk for 1000G AFR PLINK bfile build** — `7eb2048` (feat)
5. **Task 4b: Build 1000G AFR PLINK bfiles 22 chr fire (66 files, 504 samples)** — `b1e730a` (data)
6. **Task 5: GWAS Catalog v_lock_M2 fetch + manifest row** — `d90c21e` (feat)
7. **Task 6: src/python/cpassoc.py SHom + SHet + safe-inverse** — `c3b38c5` (feat)
8. **Task 7: src/python/m2_stratum_keys.py with _MIN_PER_STRATUM=3** — `fc01a48` (feat)
9. **Task 8: Wave 0 broad sign-off checkpoint** — `a26872d` (docs; VALIDATION.md frontmatter flipped to `nyquist_compliant: true` + `wave_0_complete: true`)
10. **Task 9: Per-item four-attestation (CR-checker WR-5)** — `99c7602` (docs; `## Wave 0 four-item attestation` section appended to m2-VALIDATION.md)

**Plan-text typo correction (Rule 1 deviation):** `8b27d7f` (docs; Task 1 acceptance criterion 14 → 13 to match `must_haves.truths`).

**Plan metadata commit:** _to be appended after STATE.md + ROADMAP.md updates_.

## Files Created/Modified

### Created (27)

- `tests/m2/conftest.py` — shared M2 pytest fixtures (project_root, synthetic_ldsc_matrix, synthetic_z_matrix, trait_inventory_yaml)
- `tests/m2/fixtures/.gitkeep` — empty fixtures directory placeholder
- `tests/m2/test_*.py` × 13 — RED stubs with skip-on-missing import guards (38 tests collected, 0 import errors)
- `envs/m2-mtag.yml` — numpy<2 + scipy + pandas (Pitfall 6 ABI lock)
- `envs/m2-cpassoc.yml` — numpy + scipy + pandas
- `envs/m2-clumping.yml` — plink=1.9 from bioconda (Pitfall 5 — PLINK 2.0 has no `--clump`)
- `envs/m2-mtcojo.yml` — gcta + plink=1.9
- `envs/m2-regions.yml` — bedtools=2.31
- `envs/m2-novelty.yml` — pandas + scipy
- `tools/mtag/` — vendored JonJala/mtag.git at pinned commit `9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc`; provenance in `.git_pinned_commit` + `.git_clone_log`
- `data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam}` — 66 files; chr22.fam = 504 samples
- `src/snakemake/rules/m2_reference.smk` — `m2_build_1000g_afr_plink` rule
- `data/catalogs/gwas-catalog-associations-full.zip` — 59,182,255 bytes; SHA-256 frozen
- `src/python/cpassoc.py` — 135 lines; Zhu 2015 SHom + SHet + `_safe_inverse(R, ridge_floor=1e-4)`
- `src/python/m2_stratum_keys.py` — 136 lines; `keys_for_stratum()` + `_MIN_PER_STRATUM = 3` + `STRATA = ('EUR', 'AFR', 'TRANS')`

### Modified (3)

- `data/catalogs/catalog_lock_manifest.tsv` — appended `gwas_catalog.v_lock_M2` row (SHA `652a974d3246...961cd`, fetch_date 2026-04-26, M2-locked)
- `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VALIDATION.md` — frontmatter flipped to `nyquist_compliant: true` + `wave_0_complete: true` + `updated: 2026-04-26`; appended `## Wave 0 four-item attestation` section
- `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md` — Task 1 acceptance criterion `14 → 13` typo fix at L244

## Decisions Made

- **13-not-14 test stub count is canonical.** `must_haves.truths` ("13 stub test files exist") and m2-VALIDATION.md Wave 0 Requirements (13 distinct test files listed) both specified 13; the four occurrences of `14` in the plan body (L190 action, L244 acceptance, L249 done, L1083/L1086/L1089/L1091 Task 9 how-to-verify, L1153 verification) were drafting drift. Carter accepted the 13-truth interpretation; only the load-bearing acceptance-criterion line at L244 was patched in this plan to keep the deviation surface minimal.
- **Static-grep accepted for MTAG `--residcov_path` verification.** Live `mtag.py --help` invocation requires the `m2-mtag` conda env (Wave 2 build); for Wave 0 audit purposes, grep-confirmation that the literal `--residcov_path` flag appears in the vendored MTAG argparse entries (recorded in `tools/mtag/.git_clone_log`) is functionally equivalent. Live `--help` deferred to Wave 2 conda env build.
- **CR-checker WR-5 per-item attestation pattern adopted.** Rather than a single composite Wave 0 sign-off checkpoint, Carter attests each of the four invariants (a) AFR PLINK build / (b) GWAS Catalog SHA / (c) RED test count / (d) MTAG vendoring separately. This gives finer-grained recovery if any single invariant fails post-hoc.
- **GWAS Catalog v_lock_M2 hashed at `.zip`-byte level.** Pitfall 10: extracting the zip first and hashing contents would silently change with EBI re-packaging; `.zip` byte-hash is the only stable freeze. SHA-256 = `652a974d3246748290baa83899d3c8db0027eed76663b767beaee319618961cd`, 59,182,255 bytes, fetched 2026-04-26.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed plan-text typo: Task 1 acceptance criterion test count 14 → 13**
- **Found during:** Task 1 verification (RED scaffolding produced 13 test files matching the `must_haves.truths` enumeration, but plan acceptance criterion at L244 demanded `wc -l` returns 14)
- **Issue:** Plan body had four occurrences of `14` (L190 action narrative, L244 acceptance criterion, L249 done criterion, L1083/L1086/L1089/L1091 Task 9 how-to-verify, L1153 verification block) that contradicted the plan's own `must_haves.truths` field ("13 stub test files exist") and m2-VALIDATION.md Wave 0 Requirements (13 distinct test files explicitly listed). Disk truth: 13 test files were authored matching the VALIDATION list verbatim.
- **Fix:** Patched the load-bearing acceptance criterion at L244 (`14 → 13` and matching grep-target `14 → 13`). Other 14-references in narrative + Task 9 verification stayed in place — Carter accepted via the WR-5 attestation that the 13-count is canonical, and the in-body Task 9 how-to-verify language was satisfied at attestation time by Carter manually noting "13 RED tests + 38 collected" rather than the literal "14".
- **Files modified:** `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-00-preflight-and-environment-PLAN.md`
- **Verification:** `grep -nE "ls tests/m2/test_\*\.py \| wc -l\` returns 14" PLAN` returns zero matches post-fix; `ls tests/m2/test_*.py | wc -l` on disk returns `13`
- **Committed in:** `8b27d7f` (post-checkpoint, after Carter sign-off)

---

**Total deviations:** 1 auto-fixed (1 plan-text bug)
**Impact on plan:** Single-line correction to align acceptance criterion with `must_haves.truths` and disk truth. Zero scope creep; no functional code changed; test count was correct on disk throughout. Authentication gates: none (no external auth required for any task).

## Issues Encountered

- None during Tasks 1–7 (Carter spot-check confirmed all artifacts on disk before checkpoint return).
- The `tools/mtag/.git_pinned_commit` content (40-char SHA) and `.git_clone_log` (with `--residcov_path` argparse entry) were verified statically rather than via live `mtag.py --help` invocation — `mtag.py --help` requires the `m2-mtag` conda env which is built in Wave 2 (D-M2-10 pinned-vendor pattern). This is documented as a deliberate decision (above), not a deviation.

## User Setup Required

None — all artifacts built from public-data sources (1000G VCFs, EBI GWAS Catalog, JonJala/mtag.git on GitHub) using existing conda envs. No DUA-gated data, no portal authentication, no external service configuration. The Carter web-UI OSF amendment paste (M2 hard gate per Amendment §9.1) was completed on 2026-04-25 and is independent of this plan.

## Next Phase Readiness

- **Wave 1 cleared to start.** `m2-01-ldsc-matrix-refire` can now consume:
  - The expanded ~26-trait inventory from M1 (already on disk)
  - The 13 RED test stubs (Wave 1 will GREEN `tests/m2/test_build_mtag_residcov_slice.py` + `tests/m2/test_mtag_overlap_matrix_format.py`)
  - The 1000G AFR PLINK bfile tree (consumed by Wave 4 clumping; built early to de-risk LSF wall-clock)
- **Wave 2 (`m2-02-mtag-3-strata`) gated on Wave 1 LDSC bivariate-intercept matrix output** — no new blockers from this plan.
- **All Wave 1+ targets RED on disk awaiting GREEN fires.**
- **Hand-off note:** Wave 0 unblocked Wave 1 (m2-01-ldsc-matrix-refire). All Wave 1+ targets RED on disk awaiting GREEN fires.

## Self-Check

Verified post-creation:

- `tests/m2/test_*.py | wc -l` → **13** (matches `must_haves.truths`)
- `pytest tests/m2/ --collect-only` → **38 tests collected, 0 import errors**
- `wc -l data/raw/1kg/AFR.samples` → **504** (within [490, 520] floor)
- `wc -l data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.22.fam` → **504** (matches AFR.samples)
- `ls data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{1..22}.{bed,bim,fam}` → **66 files** (22 chr × 3 file types)
- `cat tools/mtag/.git_pinned_commit` → **`9e17f3cf1fbcf57b6bc466daefdc51fd0de3c5dc`**
- `grep "gwas_catalog.v_lock_M2" data/catalogs/catalog_lock_manifest.tsv` → row present with SHA `652a974d3246748290baa83899d3c8db0027eed76663b767beaee319618961cd`, 59,182,255 bytes
- `wc -l src/python/cpassoc.py` → **135** (above min_lines: 60)
- `wc -l src/python/m2_stratum_keys.py` → **136** (above min_lines: 40)
- `ls envs/m2-{mtag,cpassoc,clumping,mtcojo,regions,novelty}.yml` → all 6 present
- `ls src/snakemake/rules/m2_reference.smk` → present
- m2-VALIDATION.md frontmatter: `nyquist_compliant: true`, `wave_0_complete: true`, `updated: 2026-04-26` — confirmed
- m2-VALIDATION.md body: `## Wave 0 four-item attestation` section appended with all four invariants recorded — confirmed
- All 10 task commits present in `git log --oneline -15` (Tasks 1–7 = 8 commits inc. 4a/4b split, Tasks 8–9 = 2 commits, plus 1 typo-fix commit)
- All success_criteria from orchestrator prompt satisfied:
  - [x] Plan typo fix commit landed (14 → 13) — `8b27d7f`
  - [x] m2-VALIDATION.md frontmatter flipped (`wave_0_complete: true`, `nyquist_compliant: true`) and committed — `a26872d`
  - [x] m2-VALIDATION.md `## Wave 0 four-item attestation` section appended and committed — `99c7602`
  - [x] m2-00-preflight-and-environment-SUMMARY.md authored (this file)
  - [ ] STATE.md M2 row updated to mark m2-00 complete — _next step_
  - [ ] ROADMAP.md m2-00 plan progress = completed — _next step_
  - [ ] Final return to orchestrator includes post-checkpoint commit SHAs — _final step_

**Self-Check: PASSED** (all 12 invariant verifications pass; remaining 3 success criteria are the closeout STATE/ROADMAP/return steps that follow this SUMMARY commit).

---

*Phase: m2-ldsc-mtag-cpassoc-discovery*
*Plan: 00-preflight-and-environment*
*Completed: 2026-04-26*
