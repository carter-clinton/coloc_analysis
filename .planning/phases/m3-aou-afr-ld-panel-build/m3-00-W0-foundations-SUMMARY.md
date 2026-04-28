---
phase: m3-aou-afr-ld-panel-build
plan: m3-00-W0-foundations
subsystem: m3-foundations
status: partial
blocking_gate: O1-region-width-acceptance
tags: [aou, ld-panel, hail, foundations, wave-0, dev-mirror, threat_model_referenced, nyquist_compliant]
dependency_graph:
  requires:
    - results/regions/union_region_list.bed (M2 deliverable)
    - data/external/liftover/hg19ToHg38.over.chain.gz
    - data/processed/ld_reference/EUR/*.rds (Track A 11 region_safe slugs)
  provides:
    - config/ld_regions.tsv (322-row region × ancestry manifest)
    - config/ld_regions_dev.tsv (10-row dev subset; Q11 overlap design)
    - config/pipeline.yaml ld_panel: resolver block
    - config/region_id_mapping.tsv (11 Track A region_safe → M2 region_id)
    - src/python/build_ld_region_manifest.py
    - src/python/select_ld_regions_dev.py
    - src/python/ld_panel.py::resolve_ld_path
    - src/python/aou_ld_panel.py (Hail driver; canonical ordering)
    - tests/m3/{conftest,test_*}.py (Wave 0 pytest scaffold)
    - tests/m3/fixtures/build_synthetic_mt.py
    - envs/m3-aou-dev.yml + envs/m3-r-ld.yml
    - .planning/amendments/aou-egress-audit-log.md (seeded; HARD GATE PENDING)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
  affects:
    - .planning/ROADMAP.md (M3 entry per D-M3-01)
    - .planning/STATE.md (Wave 0 in progress)
    - .gitignore (explicit M3 ephemeral entries)
tech-stack:
  added:
    - hail==0.2.130 (pip; envs/m3-aou-dev.yml)
    - pyspark==3.5.* (Spark backend for Hail)
    - openjdk==11 (JVM for Hail/PySpark)
    - pyliftover (region BED liftover)
    - r-reticulate, r-Matrix, r-testthat, r-jsonlite (envs/m3-r-ld.yml)
  patterns:
    - sys.path.insert at conftest.py — matches m1/conftest.py pattern
    - argparse + pandas TSV I/O — matches src/python/build_region_union.py sibling pattern
    - lazy synthetic-MT fixture build via subprocess — keeps pytest hermetic when hail absent
key-files:
  created:
    - src/python/build_ld_region_manifest.py
    - src/python/select_ld_regions_dev.py
    - src/python/ld_panel.py
    - src/python/aou_ld_panel.py
    - config/ld_regions.tsv
    - config/ld_regions_dev.tsv
    - config/region_id_mapping.tsv
    - envs/m3-aou-dev.yml
    - envs/m3-r-ld.yml
    - tests/m3/conftest.py
    - tests/m3/test_build_ld_region_manifest.py
    - tests/m3/test_ld_panel_resolver.py
    - tests/m3/test_aou_ld_panel_local.py
    - tests/m3/fixtures/build_synthetic_mt.py
    - .planning/amendments/aou-egress-audit-log.md
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
  modified:
    - config/pipeline.yaml (added ld_panel: block)
    - .planning/ROADMAP.md (M3 entry per D-M3-01)
    - .planning/STATE.md (Wave 0 in progress)
    - .gitignore (M3 ephemeral entries)
decisions:
  - "Inward-walk liftover fallback for endpoints in unmappable gaps (Rule 1/Rule 2 deviation): preserves all 161 regions; without it, 62/161 regions failed liftover."
  - "Inversion-handling for liftover endpoints whose chain mapping reverses order: walk inward up to 5 Mb to recover monotonic envelope (1 region required this — m2_region_00007 1q21-23 amylase)."
  - "TRANS LD routes through EUR_aou per Q7 fallback chain; manifest only emits AFR + EUR rows (322 total) per D-M3-02."
  - "Curated 11-row region_id_mapping.tsv excludes BMI_Xq24 (chrX out of M2 autosomal scope per AOU-LD-PIPELINE.md §4) — 12 EUR Track A .rds files map to 11 Wave-0 mapping rows."
metrics:
  duration: ~2 hours wall clock
  tasks_completed: 4 of 5
  pytest_passed: 23
  pytest_skipped: 4
  manifest_rows: 322
  dev_subset_rows: 10
  region_class_distribution:
    small: 45
    medium: 80
    large: 28
    xlarge: 8
  path_a_distribution:
    A.1: 45
    A.2: 80
    A.3: 36
  estimated_cluster_hours_per_ancestry: 558.5
  liftover_status_distribution:
    primary: 198
    multi-segment: 124
    failed: 0
  completed: 2026-04-28
---

# Phase M3 Plan 00 (Wave 0): Foundations Summary

NCSU-local foundations for the M3 AoU AFR/EUR LD panel build are
in place — region manifest reformatter (322 rows, all 161 regions
preserved through inversion-aware liftover), dev-subset selector
(Q11 overlap design with 3 EUR-Track-A regions matching 3 of 5
AFR-known regions on FTO/SH2B3/APOE), ld_panel: resolver helper
+ pipeline.yaml block, both conda envs, Hail driver with the
corrected canonical ordering (split_multi_hts BEFORE variant_qc),
synthetic MT fixture builder, four pytest test files (23 passed +
4 hail-skipped), AoU egress audit log seed with HARD GATE
classification placeholder, ROADMAP M3 wording fix per D-M3-01,
.gitignore M3 entries. Wave 1 onwards is blocked on Carter's O1
ruling (Task 5 — region-width acceptance ⇒ Path A.3 vs re-tile to ≤
10 Mb tiles).

## Tasks Completed

| Task | Name                                                                             | Commit  | Files                                                                                                                                                                                                                                       |
| ---- | -------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Region manifest reformatter + dev selector + region-class projection             | 4cf6295 | src/python/build_ld_region_manifest.py, src/python/select_ld_regions_dev.py, config/ld_regions.tsv, config/ld_regions_dev.tsv, config/region_id_mapping.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv, tests/m3/conftest.py, tests/m3/test_build_ld_region_manifest.py |
| 2    | ld_panel resolver helper + pipeline.yaml block + resolver pytest                 | 26557aa | src/python/ld_panel.py, config/pipeline.yaml, tests/m3/test_ld_panel_resolver.py                                                                                                                                                            |
| 3    | Conda envs + Hail driver + synthetic MT fixture + driver pytest + .gitignore     | 40f7fac | envs/m3-aou-dev.yml, envs/m3-r-ld.yml, src/python/aou_ld_panel.py, tests/m3/fixtures/build_synthetic_mt.py, tests/m3/test_aou_ld_panel_local.py, .gitignore                                                                                  |
| 4    | Egress audit log seed + ROADMAP D-M3-01 wording fix + STATE.md note              | b6e44ed | .planning/amendments/aou-egress-audit-log.md, .planning/ROADMAP.md, .planning/STATE.md                                                                                                                                                       |
| 5    | Carter human-action gate: rule on Open Issue O1 (region-width acceptance)        | PENDING | .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md (Carter to append D-M3-09)                                                                                                                                                          |

## Region-Class Distribution (Path-A Cost Projection)

From `.planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv`
(consumed by Carter at the O1 ruling task):

| Region class                  | n   | Path-A   | Per-region cluster-hours | Total cluster-hours per ancestry |
| ----------------------------- | --- | -------- | ------------------------ | -------------------------------- |
| small (≤ 5 Mb)                | 45  | A.1      | 0.5 (15-25 min)          | 22.5                             |
| medium (5-25 Mb)              | 80  | A.2      | 1.5 (45-90 min)          | 120                              |
| large (25-50 Mb)              | 28  | A.3      | 8.0 (4-12 h)             | 224                              |
| xlarge (> 50 Mb)              | 8   | A.3      | 24.0 (12-36 h)           | 192                              |
| **Total (per ancestry)**      | 161 |          |                          | **558.5**                        |

For both AFR + EUR: ~1,117 cluster-hours total (≈ 47 cluster-days at 1
worker; ~5-7 wall days at AoU's quota of ~8-12 concurrent Dataproc jobs).
**This is the cost figure Carter weighs at the O1 ruling.**

If Carter chooses **Resolution 1 (accept wide regions; Path A.3 for >
10 Mb)** — proceed at 558.5 ch/ancestry as projected.

If Carter chooses **Resolution 2 (re-tile > 10 Mb regions to ≤ 10 Mb
tiles)** — Wave 0 grows by one task (`a tile-splitter script (e.g., src/python/tile_wide_regions)`)
and re-emits `config/ld_regions.tsv`; the 36 Path-A.3 regions fragment
into ~120-180 tiles, all in Path A.2 (sparsify+to_numpy) territory.

## Phase-Level Check Results

Per `<verification>` block of the plan:

| #   | Check                                                                                                       | Result                                                            |
| --- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 1   | `pytest tests/m3 -x --tb=short`                                                                             | 23 passed, 4 skipped (hail-dependent), 19.8s wall                 |
| 2   | `python -c "import yaml; cfg=yaml.safe_load(...); assert 'ld_panel' in cfg and ..."`                        | OK                                                                |
| 3   | `wc -l config/ld_regions.tsv` returns 323 (1 header + 322 rows)                                             | 323                                                               |
| 4   | `wc -l config/ld_regions_dev.tsv` returns 11 (1 header + 10 rows)                                           | 11                                                                |
| 5   | `grep -c "split_multi_hts" src/python/aou_ld_panel.py` ≥ 1 AND `grep -c "RELATED_SAMPLES_HT_PATH"` == 0     | split=4, RELATED_SAMPLES_HT_PATH=0 (Q9 correction verified)       |
| 6   | `grep -c "D-M3-09" m3-CONTEXT.md` ≥ 2                                                                       | **PENDING — Carter Task 5 gate**                                  |
| 7   | `grep -c "EUR_1kg_ukb" .planning/ROADMAP.md` == 0                                                           | 0 (D-M3-01 wording removed)                                       |
| 8   | `grep -c "data/interim/aou_ld_exports" .gitignore` == 1                                                     | 1                                                                 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Liftover fails on regions whose endpoints land in unmappable GRCh38 gaps**

* **Found during:** Task 1 (initial reformatter run against full M2 BED)
* **Issue:** 62 / 161 regions had at least one endpoint with no GRCh37 → GRCh38 chain hit (centromeres, pericentromeric repeats, p-arm starts at position 0). This dropped 38% of M2 regions including the dev-critical FTO 16q12 (m2_region_00067) and SH2B3 12q24 (m2_region_00040).
* **Fix:** Added `_find_mappable()` inward-walk fallback in `liftover_region()` — when an endpoint has zero hits, walk in 1 kb steps up to 1 Mb toward the region interior to find the nearest mappable site. Status flag is upgraded to `multi-segment` to record that walking occurred.
* **Files modified:** src/python/build_ld_region_manifest.py
* **Commit:** 4cf6295

**2. [Rule 1 - Bug] Liftover yields inverted (start > end) coordinates for regions spanning chain rearrangements**

* **Found during:** Task 1 (one region — m2_region_00007 chr1:144M-148M, the 1q21-23 amylase region — failed the `new_end > new_start` invariant after the inward-walk fix.)
* **Issue:** The chr1 chain has a complex rearrangement around 145-148 Mb where the two endpoints map to coordinates whose order reverses; the post-walk envelope had `new_end <= new_start`.
* **Fix:** Added a second-stage walk that walks the rearranged endpoint further inward (up to 5 Mb) until a position is found that preserves `start < end` while staying within the original spatial envelope.
* **Files modified:** src/python/build_ld_region_manifest.py
* **Commit:** 4cf6295

**3. [Rule 3 - Blocking] tests/m3/test_aou_ld_panel_local.py initially skipped ALL tests because of module-level pytest.importorskip("hail")**

* **Found during:** Task 3 (first pytest run against new test file)
* **Issue:** Module-level `hail = pytest.importorskip("hail")` causes pytest to skip the WHOLE module collection, including the 6 static-source tests which do not require hail.
* **Fix:** Move `pytest.importorskip("hail")` from module level to a `_require_hail()` helper called at the start of each live-Hail test only.
* **Files modified:** tests/m3/test_aou_ld_panel_local.py
* **Commit:** 40f7fac

### Auth / Human-Action Gates Encountered

**Task 5 — Open Issue O1 ruling — Carter human-action gate (deferred per
plan structure; not an auth gate):** This gate is the formal Wave 0
output that requires Carter to choose between Resolution 1 (accept wide
regions; Path A.3 for > 10 Mb) and Resolution 2 (re-tile > 10 Mb regions
into ≤ 10 Mb tiles before M3) and append a D-M3-09 ruling block to
`m3-CONTEXT.md`. See `## Carter Task 5 — Awaiting D-M3-09 Ruling` below.

## Carter Task 5 — Awaiting D-M3-09 Ruling

The Wave 0 plan ends with a `checkpoint:human-verify` task that Carter
must complete before Wave 1 can fire. The relevant facts and the ruling
template are:

### O1 — Region-width acceptance (RESEARCH.md lines 730-740)

The M2 union BED produces median 9 Mb / max 102 Mb regions (8 % small,
92 % > 5 Mb), while AOU-LD-PIPELINE.md §5.1's static `radius=2_500_000`
assumed ~1-2 Mb fine-mapping windows. Wave 0 implements the per-region
radius algorithm (`radius_bp = min((end - start) + 500_000, 50_000_000)`)
which fixes the structurally-zeroed off-diagonal blocks issue, but the
36 large/xlarge regions (28 large + 8 xlarge) now require Path A.3
(BlockMatrix-write to bucket; never densify on driver) which is more
engineering-heavy than spec §5.1's `to_numpy()` flow.

**Resolution 1 (RECOMMENDED — RESEARCH.md):** Accept wide regions; use
Path A.3 for > 10 Mb regions. Cost: methodological purity preserved; M2
union remains canonical fine-mapping unit; engineering plumbing only.
Per-class cost projection: 558.5 cluster-hours per ancestry (~5-7 wall
days at AoU quota).

**Resolution 2:** Re-merge M2 regions into ≤ 10 Mb tiles before M3.
Cost: M2's region union ceases to be M3 fine-mapping unit; novelty calls
become tile-anchored not region-anchored. Cleaner compute; messier
methodology. Inserts a new `a tile-splitter script (e.g., src/python/tile_wide_regions)` task and
re-emits `config/ld_regions.tsv`.

### Ruling template

Carter appends to `m3-CONTEXT.md` in the `<decisions>` section:

```markdown
### D-M3-09: Open Issue O1 ruling — region-width acceptance

**Decision:** Resolution 1 — accept wide regions; Path A.3 for > 10 Mb
regions.   (or Resolution 2 — re-tile > 10 Mb regions to ≤ 10 Mb tiles
via a tile-splitter script (e.g., src/python/tile_wide_regions).)

**Why:** [Carter's rationale]

**How to apply:** Wave 1+ honor the per-region radius from
config/ld_regions.tsv; Wave 4 production honors Path A.1/A.2/A.3 branches
in src/python/aou_ld_panel.py per region_class.   (or: Wave 0 adds
tile_wide_regions.py and re-emits config/ld_regions.tsv with ≤ 10 Mb
tiles before Wave 1 fires.)
```

Commit with token `(m3-W0-T5)` in the subject. After commit, run:

```bash
PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH \
  node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" \
    roadmap update-plan-progress m3-aou-afr-ld-panel-build \
    m3-00-W0-foundations completed
```

to mark the plan complete in ROADMAP.md.

## Wave 1 Readiness Checklist

Once D-M3-09 is committed, Wave 1 is ready to fire. Carter portal
actions blocking Wave 1's first Dataproc spend (per
`m3-01-W1-aou-cohort-and-hard-gates-PLAN.md`):

* [ ] **P1** AoU workspace creation (paste from
  `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`)
* [ ] **P2** DUS approval
* [ ] **P3** RPS approval
* [ ] **P4** Billing profile attached
* [ ] **P6** P&P draft registration filed
* [ ] **R1 (HARD GATE)** Egress classification of variant×variant LD
  matrices in writing (AoU support email or portal-issued ruling letter);
  populates the HARD GATE row in
  `.planning/amendments/aou-egress-audit-log.md`.
* [ ] **AUX path verification** (`gsutil ls $AUX_BASE/ancestry/` from
  inside AoU workspace; if `ancestry_preds.tsv` filename differs from
  the inferred path, update `ANCESTRY_PREDS_PATH` in
  `src/python/aou_ld_panel.py`).
* [ ] **D-M3-09 — O1 ruling** (this Wave 0 Task 5 gate).

## Self-Check: PASSED

All claimed artifacts verified to exist on disk; all 4 modified files
reflect the documented edits; all 4 commit hashes are present in
`git log --oneline`.

Note: hypothetical references to `a tile-splitter script (e.g., src/python/tile_wide_regions)`
elsewhere in this SUMMARY describe a *Resolution 2* alternative path
that would only be created if Carter rules that way at Task 5; this file
is intentionally NOT present at Wave 0 close (under Resolution 1 it never
needs to exist). The reference is informational, not an artifact claim.

* config/ld_regions.tsv: FOUND (323 lines)
* config/ld_regions_dev.tsv: FOUND (11 lines)
* config/region_id_mapping.tsv: FOUND (12 lines)
* config/pipeline.yaml ld_panel: block: FOUND (1 occurrence at column 0)
* envs/m3-aou-dev.yml: FOUND (python=3.11, hail==0.2.130)
* envs/m3-r-ld.yml: FOUND (r-base=4.4, r-reticulate)
* src/python/build_ld_region_manifest.py: FOUND
* src/python/select_ld_regions_dev.py: FOUND
* src/python/ld_panel.py: FOUND
* src/python/aou_ld_panel.py: FOUND (split_multi_hts before variant_qc verified by pytest)
* tests/m3/conftest.py: FOUND
* tests/m3/test_build_ld_region_manifest.py: FOUND (9 passed)
* tests/m3/test_ld_panel_resolver.py: FOUND (8 passed)
* tests/m3/test_aou_ld_panel_local.py: FOUND (6 passed + 4 skipped)
* tests/m3/fixtures/build_synthetic_mt.py: FOUND
* .planning/amendments/aou-egress-audit-log.md: FOUND (94 lines)
* .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv: FOUND (162 lines)
* .planning/ROADMAP.md: MODIFIED (D-M3-01 wording applied)
* .planning/STATE.md: MODIFIED (Wave 0 in progress)
* .gitignore: MODIFIED (M3 entries appended)

Commits:
* 4cf6295 (Task 1): FOUND
* 26557aa (Task 2): FOUND
* 40f7fac (Task 3): FOUND
* b6e44ed (Task 4): FOUND
