---
quick_id: 260619-rqs
type: execute
mode: quick
subsystem: m3-aou-afr-ld-panel-build
tags: [ld-manifest, xlarge-split, path-b-regen, faithfulness, tdd]
requires: [m3-02b overlapping-window split code]
provides:
  - "post-split 20-column config/ld_regions.tsv (434 rows; 8 xlarge parents -> 128 __sub compute rows)"
  - "split_existing_manifest() Path B entrypoint + --split-existing-manifest CLI XOR mode"
  - "shared _assemble_region_rows() helper (single source of split geometry for both build paths)"
  - "regenerated config/ld_regions_dev.tsv (12 rows) + projection + region_id_mapping"
affects: [m3-02c cost probe (consumes the post-split cells)]
key-files:
  created: []
  modified:
    - src/python/build_ld_region_manifest.py
    - tests/m3/test_build_ld_region_manifest.py
    - tests/m3/test_aou_ld_panel_local.py
    - config/ld_regions.tsv
    - config/ld_regions_dev.tsv
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
    - config/region_id_mapping.tsv
decisions:
  - "Faithfulness via a SHARED _assemble_region_rows helper both build_manifest and split_existing_manifest call (extract-method, no behavior change to build_manifest) — proven byte-identical on the shared geometry columns by an assert_frame_equal test."
  - "10 Mb buffer is the cost-probe INPUT (Pan-UKBB lever), NOT the resolved AFR/EUR LD-decay band; m3-02c owns the final width."
metrics:
  tasks: 2
  files_modified: 7
  manifest_rows: 434
  sub_rows: 128
  dev_rows: 12
  completed: 2026-06-20
---

# Quick Task 260619-rqs: Regenerate Post-Split LD Region Manifest Summary

Split the committed OLD 12-column `config/ld_regions.tsv` in place (Path B — the
canonical `--bed`/`--chain` regen inputs are gone: forward `hg19ToHg38` chain
deleted, M2 union BED nowhere on the tree) into the post-split 20-column schema,
unblocking the m3-02c cost probe which preflight-counts + cost-probes the 8
xlarge parents' `__sub` compute cells.

## Entrypoint design

- **`_assemble_region_rows()`** — extracted (pure extract-method, zero behavior
  change to `build_manifest`) the per-region SPLIT-branch + WHOLE-branch row +
  projection assembly into one module-level helper. The WR-01
  `SUBREGION_BUFFER_GUARD` moved inside it so BOTH callers refuse the silent
  50 Mb parent-spanning-window footgun. `build_manifest` now liftover →
  radius/class → calls the helper with `trait_lead_fn = lambda a:
  derive_source_trait_and_lead(prov, a)`.
- **`split_existing_manifest(in_manifest_df, *, subregion_buffer_mb,
  max_subregion_span_mb, split_classes) -> (manifest_df, projection_df)`** — groups
  the existing manifest by `region_id`, reads grch38/grch37/region_class/radius/
  liftover_status straight from each group's first row (no liftover, no
  radius/class recompute — chain gone AND geometry is GRCh38-only), builds a
  per-ancestry `(source_trait, lead_variant)` lookup, and calls the SAME
  `_assemble_region_rows` helper. Outputs the full 20-col `MANIFEST_COLUMNS`
  schema, ADDING the 8 split-provenance columns the OLD rows lacked.
- **`--split-existing-manifest IN.tsv` CLI mode** — argparse XOR with
  `--bed`/`--chain` (post-parse `p.error()`: errors if both given, or if neither
  mode's required inputs present). The function is the unit-test surface; the CLI
  mode is the regen surface.

## Faithfulness result

`test_split_existing_matches_build_manifest_faithfulness` **PASSES**:
`build_manifest` (via an identity-chain one-row bed) and `split_existing_manifest`
(from the equivalent existing-manifest rows) produce `__sub` manifests that are
`assert_frame_equal`-identical on the 14 shared geometry columns
(`region_id, chr, ancestry, parent_region_id, subregion_index, n_subregions,
core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38,
buffer_bp, start_grch38, end_grch38, region_class`). The shared helper is the
single source of split geometry — Path B cannot drift from the canonical path.

## Regenerated row counts

| Artifact | Rows | Notes |
|----------|------|-------|
| `config/ld_regions.tsv` | **434** data rows | was 322; 16 whole xlarge cells retired, **128 `__sub` compute rows** added (306 whole + 128 sub) |
| `__sub` compute rows | **128** | every one has `buffer_bp == 10_000_000` (NOT 50 Mb) |
| projection TSV | 225 | 8 parent rows + 64 subregion rows + 153 whole |
| `config/ld_regions_dev.tsv` | **12** | see below |

Math check: 322 − 16 (whole xlarge cells) + 128 (`__sub`) = **434**. ✓

### Per-parent `n_subregions` (at 10 Mb core)

| Parent | chr | n_subregions |
|--------|-----|--------------|
| m2_region_00040 (SH2B3) | 12 | **9** |
| m2_region_00060 | 15 | 7 |
| m2_region_00088 | 2 | 6 |
| m2_region_00111 | 3 | 6 |
| m2_region_00120 | 4 | 11 |
| m2_region_00145 (HLA) | 6 | **11** |
| m2_region_00146 | 7 | 6 |
| m2_region_00161 | 9 | 8 |

### Dev manifest new row set (12 rows)

`m2_region_00006` (AFR), `m2_region_00027` (AFR), `m2_region_00040__sub00`
(AFR+EUR), `m2_region_00040__sub01` (AFR+EUR), `m2_region_00067` (AFR+EUR),
`m2_region_00083` (AFR+EUR), `m2_region_00143` (AFR, chr6 HLA-stress overlap),
`m2_region_00153` (AFR, chr8 8p23-stress overlap).

The split parent `m2_region_00040` resolves to its first **DEV_SUBREGION_CAP=2**
`__sub` rows per ancestry (sub00/sub01, AFR+EUR — never mixing ancestries). The
chr6/chr8 HLA-stress picks are the selector's deterministic first interval-overlap
winners (`00143`/`00153`); the xlarge `m2_region_00145` is split so its windows are
not the overlap winner — selector behavior unchanged.

## 10 Mb-buffer caveat (for m3-02c)

The **10 Mb buffer is the cost-probe INPUT** — the documented Pan-UKBB AFR/EUR LD
anchor band and the effectively-mandatory split-realizing value (the radius-based
default would trip the WR-01 guard). It is **NOT** the resolved AFR/EUR LD-decay
band. m3-02c owns resolving the correct width (it may demand
`--max-subregion-span-mb 7` for the chr6 `m2_region_00145` HLA density) and
measuring the real per-cell cost. Do not silently treat 10 Mb as final.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected stale `test_ld_regions_radius_cap_only_affects_xlarge`**
- **Found during:** Task 2 (full tests/m3 after regen)
- **Issue:** the test (m3-W2 HIGH-3) encoded the PRE-split invariant "only whole
  xlarge rows are radius-capped (16 cells)". The m3-02b overlapping-window split
  RETIRED the whole xlarge compute rows and replaced them with `__sub` windows
  whose `region_class` is the window class (medium/large) and whose
  `radius_bp == buffer_bp` (the explicit band knob). So `radius < window-span` is
  now BY DESIGN for every `__sub` row (that IS the banded compute window). Both
  the `banded_nonxlarge` assertion and the `n_banded == 16` count were
  invalidated by the legitimate new design — a stale test, not a regression in the
  regen.
- **Fix:** renamed to `test_ld_regions_radius_cap_only_affects_split_subregions`;
  new invariant = a banded row MUST be a `__sub` compute row (non-empty
  `parent_region_id`), NO whole row may be banded; sanity count = `n_banded ==
  n_sub` (all `__sub` rows banded, > 0). Verified: 128 banded, all `__sub`, 0
  whole banded.
- **Files modified:** tests/m3/test_aou_ld_panel_local.py
- **Commit:** 388ea3f

## Verification

- `verify_regen.py` → `MANIFEST_REGEN_OK manifest_rows=434 dev_rows=12` (all 6
  must-have invariants hold: m2_region_00040__sub00 AFR+EUR, region_00145 __sub
  present, all __sub buffer_bp==10000000, m2_region_00006 whole medium, dev
  carries m2_region_00040__sub00 AFR+EUR).
- `pytest tests/m3/test_build_ld_region_manifest.py` → 18 passed / 10 skipped
  (12 pre-existing build_manifest tests + 6 new split-existing incl. faithfulness).
- Full `pytest tests/m3` → **204 passed / 0 failed / 30 skipped** (baseline 198 +
  6 new split-existing; radius-cap test renamed, not added).

## Commits

- `abf79c3` feat(260619-rqs): add split_existing_manifest (Path B) via shared _assemble_region_rows
- `388ea3f` feat(260619-rqs): regenerate post-split LD manifest + dev + projection + mapping (Path B)

## Self-Check: PASSED

All 7 modified files present; both commits (`abf79c3`, `388ea3f`) in history;
`split_existing_manifest` + `_assemble_region_rows` present in source;
`m2_region_00040__sub00` present in the regenerated `config/ld_regions.tsv`.
