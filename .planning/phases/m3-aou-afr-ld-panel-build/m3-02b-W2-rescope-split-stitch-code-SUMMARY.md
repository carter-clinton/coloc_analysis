---
phase: m3-aou-afr-ld-panel-build
plan: 02b
subsystem: infra
tags: [aou-ld, susie-rss, banded-stitch, sparse-matrix, hail, reticulate, manifest, dgcmatrix]

requires:
  - phase: m3-aou-afr-ld-panel-build
    provides: "A.3 banded correlation BM fix (_write_a3_banded_correlation_bm), ordering-A locked, 3 cohort MTs, dev-10 capacity-wall diagnosis"
provides:
  - "Overlapping-window xlarge split in build_ld_region_manifest.py (half-open cores tile parent + core+/-buffer compute windows + explicit buffer_bp)"
  - "select_ld_regions_dev.py tuple-resolve + capped __sub expansion (DEV_SUBREGION_CAP=2, no ancestry mixing)"
  - "AF metadata in the .npz/.rds payload (aou_ld_panel.py allele_freq + _save_npz assertion + A.3 sidecar)"
  - "NEW src/scripts/stitch_subregions_to_rds.R: banded (NOT block-diagonal) sparse parent assembly emitting obj$R + obj$variants for the REAL loader"
  - "ld_npz_to_rds.R whole-region payload reconciled to obj$R + obj$variants schema"
  - "A6 real-loader contract test (resolve_ld_path -> load_ld_matrix -> susie_rss) + sparse-parent benchmark (no whole-parent dense)"
  - "AOU-2 notebook Q-RS2 n2-highmem-16 executor-config cell"
affects: [m3-02c, m3-04, m3-05, finemap, susie-rss]

tech-stack:
  added: ["envs/m3-r-ld provisioned (r-reticulate/matrix/jsonlite/digest/data.table/susier/coloc/optparse/yaml + numpy + pyliftover)"]
  patterns:
    - "Overlapping-window split: half-open cores [core_start,core_end) tile parent; compute window = core +/- buffer_bp"
    - "Banded sparse stitch: cross-core pairs within buffer_bp retained at global (i,j); beyond -> structural 0; NOT Matrix::bdiag"
    - "Allele-aware core-ownership de-dup: each variant owned by ONE core; matching on (CHR,POS,REF,ALT) not position-only"
    - "ERROR-not-skip R-toolchain gate (_require_m3_r_toolchain) for the no-skip A6 must_have"

key-files:
  created:
    - "src/scripts/stitch_subregions_to_rds.R"
    - "tests/m3/test_stitch_subregions_to_rds.py"
    - "tests/m3/test_finemap_loader_contract.py"
    - "tests/m3/test_sparse_parent_benchmark.py"
    - "tests/m3/sparse_parent_benchmark.tsv"
  modified:
    - "src/python/build_ld_region_manifest.py"
    - "src/python/select_ld_regions_dev.py"
    - "src/python/aou_ld_panel.py"
    - "src/scripts/ld_npz_to_rds.R"
    - "tests/m3/test_build_ld_region_manifest.py"
    - "envs/m3-r-ld.yml"
    - ".planning/notebooks/AOU-2_per_region_ld.ipynb"

key-decisions:
  - "Banded-within-radius stitch (m3-REVIEWS HIGH#1): cross-core pairs within buffer_bp RETAINED, only beyond zeroed; replaces the refuted block-diagonal design"
  - "buffer_bp default = region radius (min(core_span+500kb,50Mb)); FLAGGED: at the 50Mb default the interior window spans the whole 88.8Mb parent -> the --subregion-buffer-mb 10 (Pan-UKBB) lever is effectively mandatory to realize the split's scratch bound (m3-02c cost gate)"
  - "Provisioned envs/m3-r-ld (added susieR/coloc/digest/optparse/yaml) so the no-skip A6 R families ERROR-not-skip and actually run"
  - "obj$R is a sparse dgCMatrix; SuSiE wrapper densifies lazily per credible-set window (benchmark: M=50k loads at 1.88 GiB vs 18.6 GiB dense)"

patterns-established:
  - "Half-open core ownership tiling for region splits"
  - "Sparse triplet banded assembly with overlap-pair agreement reconciliation"

requirements-completed: [REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION]

duration: 49min
completed: 2026-06-19
---

# Phase m3 Plan 02b: W2 Re-scope Split + Banded Stitch Code Summary

**Overlapping-window xlarge split (half-open cores + core±buffer compute windows), a NEW banded (not block-diagonal) sparse stitch emitting obj$R + obj$variants for the real run_susie_rss.R loader, AF metadata in the .npz/.rds, dev tuple-resolve, the A6 real-loader+susie_rss verify, and the AOU-2 Q-RS2 executor cell — all NCSU-side, no cluster, no cost.**

## Performance

- **Duration:** ~49 min
- **Started:** 2026-06-19T03:02:21Z
- **Completed:** 2026-06-19T03:51:43Z
- **Tasks:** 3 (all TDD, fully autonomous — no checkpoints)
- **Files modified/created:** 12

## Accomplishments

- **Task 1 — split + dev + AF:** `build_ld_region_manifest.py` gained `--max-subregion-span-mb` (default 10), `--split-classes` (default `xlarge`), `--subregion-buffer-mb` (default = region radius), `split_region_overlapping()` (half-open cores tile the parent exactly; compute window = core ± buffer_bp clamped), and the provenance columns `parent_region_id, subregion_index, n_subregions, core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp` + projection `split_status ∈ {whole, parent, subregion}`. `select_ld_regions_dev.py` resolves `(parent_id, ancestry)` tuples and expands a split parent into the first `DEV_SUBREGION_CAP=2` `__sub` rows for that ancestry only. `aou_ld_panel.py` collects row-aligned `allele_freq` in the single `aggregate_rows` pass (`vqc.AF[1]` or a `call_stats` annotation fallback) and `_save_npz` asserts AF present + length-aligned, writing `allele_freq=` into the .npz + A.3 sidecar.
- **Task 2 — banded stitch + payload reconcile:** new `src/scripts/stitch_subregions_to_rds.R` assembles N overlapping-window `.npz` into ONE sparse **banded** `dgCMatrix` parent `.rds` — cross-core pairs within `buffer_bp` RETAINED at their global (i,j) index, pairs beyond zeroed; allele-aware GRCh38 (chr,pos,ref,alt) ordering; half-open core-ownership de-dup (no variant duplicated across windows); overlap-pair agreement check (`|r1−r2|<1e-4`, keep one); STITCH_INPUT guards (missing/duplicate/extra child, mixed ancestry); emits `obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF)`. `ld_npz_to_rds.R` whole-region payload reconciled to the same `R+variants` schema (back-compat `ld`/`snp_ids` retained).
- **Task 3 — A6 + benchmark + notebook:** `test_finemap_loader_contract.py` answers A6 by EXERCISING `resolve_ld_path → load_ld_matrix() → susieR::susie_rss()` on a stitched parent at the finemap.smk `{ld_dir}/{ancestry}/{region}.rds` layout (returns non-NULL `as.matrix(R)` + variants subset; credible set returned). `test_sparse_parent_benchmark.py` proves no whole-parent dense materialization. AOU-2 notebook carries the Q-RS2 executor cell before the hail import.

## Task Commits

1. **Task 1: overlapping-window split + dev tuple-resolve + AF metadata** — `a17a47a` (feat)
2. **Task 2: banded stitch + real-loader payload reconcile** — `0e3ec43` (feat)
3. **Task 3: A6 real-loader verify + sparse-parent benchmark + AOU-2 Q-RS2 cell** — `908de71` (feat)

_Note: TDD was applied test-and-impl together per family; commits are per-task atomic._

## Split sizing on the REAL m2_region_00040 (SH2B3)

From the existing `m3-region-class-projection.tsv`: `m2_region_00040` spans **88.826 Mb** (GRCh38), region_class **xlarge**.

- At a **10 Mb core**: **N = ceil(88.826/10) = 9** `__sub` compute rows. Cores tile `[start,end)` exactly (half-open).
- Compute-window span + routing (interior core), via the REAL `_route_region_path`:
  - **buffer = 10 Mb** (Pan-UKBB lever) → interior window span **29.9 Mb** → routes **A.3**.
  - **buffer = 50 Mb** (the default = region radius) → interior window span **88.8 Mb** (≈ whole parent) → routes **A.3**.
- Worst-case **window** dense scratch (Wave-0 SIZING bound, conservative HLA-grade 13,000 var/Mb): a 30 Mb window ⇒ ~390k var ⇒ ~565 GiB dense — but that bound uses the HLA density everywhere; for the SH2B3 region at its true (much lower) density the per-window scratch is far smaller. The point of the split is that scratch scales with the **window** n_var, not the 88.8 Mb parent. **The real per-cell density is owned by the m3-02c preflight** (which mandatorily counts region_00145).

## buffer_bp default + research follow-up (FLAGGED per <output>)

**buffer_bp default chosen:** `min(core_span+500kb, 50Mb)` (the region radius) when `--subregion-buffer-mb` is unset.

**RESEARCH FOLLOW-UP FLAGGED (small, targeted) — the correct buffer width could NOT be resolved from existing research and must NOT be guessed:** the 50 Mb default makes the interior compute window span the **entire 88.8 Mb parent** (window = core ± 50 Mb clamped), which DEFEATS the split's scratch-bounding purpose. The Pan-UKBB anchor bands at **10 Mb**, giving a 30 Mb window. The genuinely-correct buffer is the **AFR/EUR LD-decay horizon** (the bp beyond which r²≈0), which is ancestry- and locus-dependent and is NOT the formal 50 Mb radius. **Action for m3-02c:** the cost probe must (a) measure the real per-window throughput/scratch at `--subregion-buffer-mb 10`, and (b) resolve the correct band width from AFR/EUR LD-decay literature (or an empirical decay fit on a dev region) rather than inheriting the 50 Mb radius. The narrow-to-10Mb lever is the YELLOW disposition; **for the production fire `--subregion-buffer-mb 10` is effectively mandatory** to realize the split benefit.

**HLA density flag (per <output>):** `m2_region_00145` (chr6/6p21) spans **102.5 Mb** (xlarge). At the conservative HLA-grade density (13,000 var/Mb), even a **7 Mb** core is ~91k var (>75k), and a 10 Mb core ~130k var. **Flag for the m3-02c probe to set `--max-subregion-span-mb 7` (or lower) on chr6 region_00145** and to count its real density before the production fire.

## A6 result + sparse-parent benchmark numbers

- **A6 (real-loader contract):** `load_ld_matrix()` ACCEPTS the banded sparse `obj$R + obj$variants` (status not `ld_missing`; returns `as.matrix(R)` + variants subset), and `susieR::susie_rss()` runs on the returned slice and `susie_get_cs()` yields a credible set. Verified by `test_resolver_loads_and_susie_runs_on_stitched_parent` (PASSED, not skipped).
- **Sparse-parent benchmark** (`tests/m3/sparse_parent_benchmark.tsv`, M=50,000 banded):
  - rds size **339 KB**; readRDS **1.19 s**; peak RAM on load **1.88 GiB** (a dense M²·8 would be **18.6 GiB**); one ~6,000-var credible-set window densify **0.24 s** at **2.23 GiB** peak. → proves the SuSiE wrapper densifies LAZILY per window, no whole-parent dense materialization.

## Whole-region payload reconciliation

`ld_npz_to_rds.R` now emits `list(R=<dgCMatrix>, variants=<data.frame CHR,POS,REF,ALT,SNP_ID,AF>, snp_ids=<b37, back-compat>, ld=<dense, back-compat>, provenance=...)`. The old payload had `obj$R == NULL` → the real loader rejected it. **Downstream that read the old keys:** `tests/m3/test_ld_npz_to_rds.py` reads `obj$ld` + `obj$snp_ids` (both retained → 3/3 static tests still pass; the 7 R-execution tests in that file remain pre-existing skips because that file's own discovery does not pin `RETICULATE_PYTHON` — see Deviations). No production consumer read the old `ld` key directly (the loader uses `obj$R`).

## Test pass matrix (NO skip on the R families in the M3 env)

| Family file | Named families | Result |
|---|---|---|
| `test_build_ld_region_manifest.py` (m3-W2) | xlarge_split, core_half_open_tile, window_overlaps_buffer, buffer_bp_explicit, nonxlarge_whole, subregion_provenance, window_routes_via_real_router, dev_resolves_tuples_caps, npz_has_allele_freq (+ save_npz AF assert, sub-suffix, buffer default) | **11 PASS** (AF-via-Hail test skips only where Hail absent; AF assertion verified directly) |
| `test_stitch_subregions_to_rds.py` | cross_core_band_retained, zeroes_only_beyond_buffer, banded_psd, allele_aware_alignment, no_duplicate_variant, overlap_pair_agreement, sparse_payload, loader_accepts_stitched_payload, whole_region_reconciled (+ static_grep, disagreement_raises) | **11 PASS, 0 skip** |
| `test_finemap_loader_contract.py` | loader_contract_no_skip_in_m3_env, resolver_loads_and_susie_runs | **2 PASS, 0 skip** |
| `test_sparse_parent_benchmark.py` | no_whole_parent_dense, benchmark_records_metrics | **2 PASS, 0 skip** |

Full suite: `pytest tests/m3` = **181 passed, 36 skipped, 0 failed**. The 36 skips are in OTHER files (chain-file-absent liftover tests, Hail-absent driver tests, and that-file-specific R discovery) — **none in the m3-02b no-skip stitch/loader/sparse families**.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Provisioned envs/m3-r-ld + augmented the spec for the no-skip A6 families**
- **Found during:** Tasks 2 & 3 (the no-skip R families have no usable Rscript otherwise)
- **Issue:** The project-pinned `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld` did not exist; `r_coloc` lacked reticulate/digest; the spec lacked susieR/coloc/digest/optparse/yaml needed by the loader-contract test (`run_susie_rss.R`'s top library block + `load_ld_matrix → susie_rss`).
- **Fix:** Built `envs/m3-r-ld.yml` into `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld` (corrected `bioconductor-coloc` → `r-coloc`); added `r-digest, r-susier, r-coloc, r-optparse, r-yaml` to the spec; tests pin `RETICULATE_PYTHON=<env>/bin/python` (the env's own python carries numpy+pyliftover; reticulate otherwise picks a uv python without pyliftover).
- **Files modified:** `envs/m3-r-ld.yml`
- **Verification:** All 26 m3-02b R families run (not skip) against the env; full suite 181 passed.
- **Committed in:** `a17a47a` / `0e3ec43` (env spec staged with the tasks that need it)

**2. [Rule 1 - Bug] call_stats AF fallback must be an annotate_rows pass, not inside hl.agg.collect**
- **Found during:** Task 1 (AF aggregate_rows collection)
- **Issue:** `hl.agg.call_stats` is itself an entry aggregator and cannot live inside `hl.agg.collect`; the first draft would have errored when the MT had no `vqc.AF`.
- **Fix:** Materialize `_af` via `annotate_rows(hl.agg.call_stats(...).AF[1])` BEFORE the collect, then read the row field in the collect (preserves row order). Preferred source is `vqc.AF[1]` when present.
- **Files modified:** `src/python/aou_ld_panel.py`
- **Verification:** `test_save_npz_raises_on_missing_or_misaligned_af` + the AF assertion path; the synthetic-MT AF test runs where Hail is installed.
- **Committed in:** `a17a47a`

**3. [Rule 3 - Blocking] Self-contained synthetic identity chain + functions-only loader source + tests/m3 on sys.path**
- **Found during:** Tasks 2 & 3
- **Issue:** (a) the real `hg38ToHg19` chain is not on disk (would have skipped the no-skip R families on a missing data fixture); (b) `source()`-ing the whole `run_susie_rss.R` triggers its top-level `parse_args()`/main; (c) cross-test sibling import (`from test_stitch_subregions_to_rds import ...`) failed in isolated collection.
- **Fix:** (a) tests write a minimal UCSC identity chain over chr12/chr16 (banding is GRCh38-pos based, chain-agnostic); (b) `_loader_functions_only()` sources only the function-definition prefix and the test defines the `MIN_LD_*` policy constants; (c) prepend `tests/m3` to `sys.path`.
- **Files modified:** `tests/m3/test_stitch_subregions_to_rds.py`, `tests/m3/test_finemap_loader_contract.py`, `tests/m3/test_sparse_parent_benchmark.py`
- **Verification:** All families pass with no external chain download and no main-block execution.
- **Committed in:** `0e3ec43` / `908de71`

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 bug)
**Impact on plan:** All necessary to make the no-skip A6 must_have real and to keep the families self-contained on the NCSU node. No scope creep — the plan's <critical_environment_intelligence> anticipated the env-provisioning gap and authorized provisioning `envs/m3-r-ld.yml`.

## Issues Encountered

- The default buffer (= 50 Mb region radius) makes the compute window span the whole parent — surfaced during the real-region sizing for the SUMMARY. This is documented as the flagged research follow-up for m3-02c rather than silently changing the default (the default stays the conservative radius; the narrow lever is the probe's call). Not a code defect — the split + banding are correct; the buffer width is the open cost-vs-correctness knob the probe owns.

## User Setup Required

None — NCSU-side code/test only. No external service configuration, no AoU perimeter, no cost.

## Next Phase Readiness

- **m3-02c (cost probe):** ready to consume the post-split manifest + the banding buffer knob. MUST (a) measure real per-window throughput/scratch at `--subregion-buffer-mb 10`, (b) resolve the correct AFR/EUR LD-decay band width, (c) count region_00145 (chr6) density and set `--max-subregion-span-mb 7` if it risks >75k var.
- **m3-04 (production):** the stitch + loader contract + AF metadata + Q-RS2 executor config are in place; for the production fire `--subregion-buffer-mb 10` is effectively mandatory to realize the bounded-scratch benefit.
- No blockers introduced; the 3 cohort MTs, ordering-A, and the A.3 fix remain untouched (LOCKED).

## Self-Check: PASSED

All created files present on disk; all 3 task commits (`a17a47a`, `0e3ec43`, `908de71`) exist in git history. The no-skip A6 R families (stitch / loader-contract / sparse-payload) all RAN (not skipped) and PASSED against the provisioned `m3-r-ld` env; full `pytest tests/m3` = 181 passed, 0 failed.

---
*Phase: m3-aou-afr-ld-panel-build*
*Completed: 2026-06-19*
