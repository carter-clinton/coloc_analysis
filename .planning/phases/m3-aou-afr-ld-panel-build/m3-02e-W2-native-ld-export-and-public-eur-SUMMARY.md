---
phase: m3-aou-afr-ld-panel-build
plan: 02e
subsystem: infra
tags: [ld-panel, plink, susie, snakemake, aou, egress, public-data, liftover]

requires:
  - phase: m3-02b
    provides: ".npz egress-clean contract + lower_triangular flag (bm_to_npz/_save_npz)"
  - phase: m3-02d
    provides: "per-ancestry buffer manifest (276 AFR/EUR rows), ld_egress_bundle.py, retired Hail A.3 write"
  - phase: m3-03
    provides: "resolve_ld_path resolver, ld_npz_to_rds.R loader/liftover, m3_convert_npz_rds.smk"
provides:
  - "plink_ld_to_npz.py: native plink1.9 square/banded LD -> egress-clean .npz (correct lower_triangular per mode)"
  - "aou_ld_panel.export_cohort_to_plink (one amortized hl.export_plink; .bed in-perimeter) + build_plink_ld_command (--keep-allele-order hardcoded)"
  - "build_public_eur_manifest.py + m3_public_eur_ld.smk: public UKBB 337k EUR LD ($0 compute) into the loader contract"
  - "config/pipeline.yaml EUR chain head = EUR_ukbb_pub; AFR head = AFR_aou (native plink)"
  - "estimate_s z-vs-LD consistency guard (Zou 2022) wired in run_susie_rss.R + captured in finemap.smk"
  - "m3-02e-AFR-NATIVE-FIRE-BRIEF.md: turnkey in-perimeter Task 4 runbook"
affects: [m3-04, m4-finemap-coloc]

tech-stack:
  added: [plink1.9-native-LD, Weissbrod-PolyFun-UKBB-337k-public-EUR-LD, susieR-estimate_s_rss]
  patterns:
    - "Native-plink LD reader mirrors bm_to_npz .npz contract (square=lower_triangular False, banded=True)"
    - "Public-reference EUR LD via existing AWS-S3-UNSIGNED tile scaffold + hg19 manifest columns"
    - "estimate_s per-region z-vs-LD guard serialized in R + captured to a finemap log artifact"

key-files:
  created:
    - src/python/plink_ld_to_npz.py
    - src/python/build_public_eur_manifest.py
    - src/snakemake/rules/m3_public_eur_ld.smk
    - tests/m3/test_plink_ld_to_npz.py
    - tests/m3/test_public_eur_manifest.py
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
  modified:
    - src/python/aou_ld_panel.py
    - src/snakemake/scripts/download_ukbb_ld_tiles.py
    - config/pipeline.yaml
    - Snakefile
    - src/snakemake/rules/finemap.smk
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - tests/m3/test_ld_panel_resolver.py
    - tests/m3/test_finemap_loader_contract.py

key-decisions:
  - "D-02e-01: output mode = square bin4 (default); banded + r2 floor = documented disk-tight alternate"
  - "D-02e-02: EUR reference = Weissbrod/PolyFun UKBB 337k (PRIMARY); Pan-UKBB 420k = documented alternate"
  - "D-02e-03: native tool = plink1.9 (PILOT-validated); LDstore2/emeraLD = alternates only"
  - "Canonical vid (W-3): chr:pos:REF:ALT = chr:pos:A2:A1 (hl.export_plink A1=ALT=alleles[1], A2=REF=alleles[0])"
  - "m3-04 (stale 322-cell Hail LD fire) = SUPERSEDED-PENDING-REPLAN; must consume m3-02e .npz/.rds, not rebuild via Hail"

patterns-established:
  - "Native plink LD -> identical .npz key set so ld_npz_to_rds.R needs no change"
  - "Public EUR LD selects tiles by the manifest's pre-lifted hg19 (GRCh37) window (robust path); liftover_coordinate is the explicit fallback that refuses to mix builds"

requirements-completed:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION
  - REQ-SNAKEMAKE-CI

duration: ~2h
completed: 2026-06-24
---

# Phase m3 Plan 02e: Native-plink AFR LD export + public UKBB 337k EUR LD Summary

**Re-architected M3's LD build around the GREEN native-plink pilot: an NCSU reader
turns native plink1.9 square/banded LD into the existing egress-clean `.npz`
contract, EUR LD becomes the public UKBB 337k reference at $0, and the resolver +
SuSiE-RSS `estimate_s` guard wire both new sources into one downstream contract —
the Hail BlockMatrix path (~34k cluster-h) is retired.**

## Performance

- **Duration:** ~2h (autonomous Tasks 1–3 + the Task-4 fire brief)
- **Tasks:** 3 autonomous code+TDD tasks complete; Task 4 = the in-perimeter fire
  (autonomous:false, Carter fires — the brief is the deliverable here)
- **Files:** 14 changed (+1,757 / −4); 7 atomic commits (`fe83e8b`..`e17e77a`)

## Accomplishments (Tasks 1–3, all autonomous)

### Task 1 — `plink_ld_to_npz.py` + native helpers (commit `158a29a`)
- New reader: square `.ld.bin` (float32, `lower_triangular=False`) / banded
  `.ld.gz` (one triangle, `lower_triangular=True`) → the EXACT `_save_npz` key set
  (`ld/variant_ids/rsids/allele_freq/lower_triangular`) — `ld_npz_to_rds.R`
  unchanged. No hail import (runs on the Spot VM / NCSU).
- `load_bim` reconstructs the canonical vid `chr:pos:REF:ALT = chr:pos:A2:A1`
  (W-3; hl.export_plink A1=ALT, A2=REF) — the silent-misalignment vector test
  passes byte-equal.
- `aou_ld_panel.build_plink_ld_command` (`--keep-allele-order` hardcoded; square
  `--r square bin4` / banded `--r gz`) + `export_cohort_to_plink` (one amortized
  `hl.export_plink`; `.bed` documented in-perimeter, never egressed).
- AF sidecar: blank→NaN, length-guard ValueError, omitted→all-NaN+warning.
- **14 tests pass.**

### Task 2 — public UKBB 337k EUR LD ($0) (commit `90e9189`)
- `build_public_eur_manifest.py`: maps all **276** EUR regions to overlapping
  public Weissbrod 337k tile(s) via the manifest's hg19 (GRCh37) window; reuses
  `download_ukbb_ld_tiles.tiles_for_region` (no re-implemented overlap). Pan-UKBB
  420k recorded as a documented alternate; `liftover_coordinate` fallback refuses
  to mix builds.
- `download_ukbb_ld_tiles.py`: additive `EUR_UKBB_PUB_OUT_DIR`/`_BUILD` (hg19) —
  existing rule unchanged.
- `m3_public_eur_ld.smk`: `build_public_eur_manifest` + `build_public_eur_ld`
  rules → `EUR_ukbb_pub/{region_safe}.rds`; AWS S3 boto3 UNSIGNED fetch
  (`ld_build.yml`). Snakefile includes it; Snakemake 7.32.4 parses (rc=0).
- **7 tests pass** (incl. a REAL tile-extraction round-trip on the `.npz`
  fallback + `.meta.json`, never a doc no-op).

### Task 3 — Move 3 downstream wiring (commit `ec01ab3`)
- `config/pipeline.yaml`: `EUR_ukbb_pub` is the EUR chain HEAD ahead of
  EUR_aou/EUR_ukbb/EUR_1kg; AFR head stays `AFR_aou`.
- `run_susie_rss.R`: NEW `estimate_s_rss` serialization (`d3b_ld_z_consistency_s`
  + `ld_source_mismatch_flag`; additive, tryCatch→NA) — Zou 2022 z-vs-LD guard,
  distinct from the pre-existing `kriging_rss`.
- `finemap.smk`: NEW comment block tying `estimate_s` to the two new sources
  (native AFR `--keep-allele-order` + public-EUR liftover) + a per-region log
  capture; **m3-04 recorded SUPERSEDED-PENDING-REPLAN** (consume m3-02e .npz/.rds,
  not rebuild via Hail; 322 = pre-02d 161×2, 276 = post-02d per-ancestry AFR).
- **17 resolver/finemap tests pass.**

### Task 4 deliverable — `m3-02e-AFR-NATIVE-FIRE-BRIEF.md` (commit `e17e77a`)
- 245-line turnkey runbook: preflight → export-once → **production-VM re-measure
  gate** → 276-region plink loop → `plink_ld_to_npz` → D-M3-10 verify → per-chrom
  egress → shutdown → token-free handback. PILOT going-in numbers + the 3 caveats
  as explicit gate conditions.

## Production boundary (EXPLICIT supersede record)

The M3 **LD-build is COMPLETE within m3-02e**: AFR LD = the ~276 native-plink
per-ancestry windows (Task 4 in-perimeter fire) + EUR LD = the public UKBB 337k
panel (Task 2, $0). `m3-04-W4-production-and-egress-PLAN.md` (the stale 322-cell
HAIL LD production fire) is **SUPERSEDED-PENDING-REPLAN** — it must be re-planned
to consume m3-02e's AFR-native `.npz` + public EUR `.rds`, NOT to rebuild LD via
Hail. 322 = pre-m3-02d 161 union regions × 2 ancestries; 276 = the post-m3-02d
per-ancestry AFR window count. The downstream coloc/SuSiE fine-mapping fire is a
separate M4 concern, unaffected. Recorded in `finemap.smk` + the ROADMAP m3-04
bullet + the plan frontmatter `supersedes_note`.

## Decisions

- **D-02e-01** square bin4 default (banded alternate). **D-02e-02** Weissbrod 337k
  primary (Pan-UKBB 420k alternate). **D-02e-03** plink1.9. All auto-selected from
  `--auto`; Carter may override any.

## Verification

- **38 new m3-02e tests pass** (14 plink_ld_to_npz + 7 public-EUR + 17
  resolver/finemap), run in the `smoke_dev` py3.11 env.
- All Task 1–3 acceptance criteria + the 9 phase-level checks pass.
- Snakemake 7.32.4 parses the full workflow with the new include + the new
  `finemap.smk` log directive (rc=0).
- **Full `pytest tests/m3` (47 min, with the `m3-r-ld` Rscript env present):
  260 passed, 38 skipped, 3 FAILED.** All 3 failures are in
  `test_stitch_subregions_to_rds.py` (`test_stitch_zeroes_only_beyond_buffer`,
  `test_stitch_banded_psd`, `test_stitch_allele_aware_alignment`) and are
  **PRE-EXISTING, independent of m3-02e** — proof: every file they exercise
  (`src/scripts/stitch_subregions_to_rds.R`, `src/scripts/ld_npz_to_rds.R`,
  the test, `conftest.py`) is BYTE-IDENTICAL to the pre-m3-02e base `1cd6789`
  (`git diff --quiet 1cd6789..HEAD` clean for each); the tests invoke only
  `STITCH_R` (`stitch_subregions_to_rds.R`, untouched) via `_run_stitch`, and the
  one R file m3-02e DID change (`run_susie_rss.R`'s `estimate_s_rss` at line 628)
  is far BELOW the loader-extraction marker `option_list <- list(` at line 234,
  so the stitch test's `_loader_functions_only` never sees it. The earlier
  probe-failing run mis-reported these as 18 environmental `errors`; with the R
  env actually present they are 3 real but PRE-EXISTING stitch-path failures.

## Issues Encountered

- **3 PRE-EXISTING stitch-R failures (NOT m3-02e regressions)** surfaced when the
  full suite ran with the `m3-r-ld` Rscript env. They live entirely in the
  `stitch_subregions_to_rds.R` path (zeroes-beyond-buffer / banded-PSD /
  allele-aware alignment) — all exercised files byte-identical to base `1cd6789`,
  none in m3-02e's dependency path. A modified-but-uncommitted
  `tests/m3/sparse_parent_benchmark.tsv` (from m3-02b commit `908de71`) was
  already present at session start, corroborating a pre-existing stitch-path
  drift. **Recommend a separate `/gsd-debug` on the stitch path** (likely a
  susieR/Matrix version-drift or PSD/allele-alignment assertion) — out of scope
  for m3-02e, which is clean (38/38 new + 0 introduced regressions).

## Next Phase Readiness

- **Gated next step (the ONLY billable task):** Carter fires
  `m3-02e-AFR-NATIVE-FIRE-BRIEF.md` in the AoU perimeter. The production-VM wall
  re-measure (Step 3) is a BLOCKING stop-gate before the full 276-region loop.
- **Post-fire (written by the handback):** `m3-W2-native-plink-panel.tsv` (real
  per-region walls/RAM/output/n_var vs the pilot going-in numbers) +
  `m3-02e-cluster-shutdown.md` (verified $0 idle). These are NOT created yet —
  they are produced when the fire runs.
- **m3-04** must be RE-PLANNED to consume m3-02e outputs (not rebuild LD via Hail).

## Open Risks

- Production-VM re-measure outcome (pilot ran n2-standard-16 but rates labelled
  n2-highmem-64) — re-measure-before-commit gate covers it.
- Banded vs square disk footprint (~4.2 vs ~4.6 TB ×276).
- Public-EUR liftover anchor verification (robust path uses the manifest's
  pre-lifted hg19 columns; rsID matching downstream).
