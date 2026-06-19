---
created: 2026-06-19T14:07:35.168Z
title: Close A.3 AF sidecar gap (allele_freq for large/xlarge LD regions)
area: general
files:
  - src/python/aou_ld_panel.py (compute_region_ld A.3 branch — export AF sidecar)
  - src/python/bm_to_npz.py:122 (read AF sidecar; write allele_freq= into .npz)
  - src/scripts/ld_npz_to_rds.R (obj$variants$AF consumer)
  - tests/m3/test_ld_npz_to_rds.py (add A.3 AF round-trip test)
---

## Problem

Path A.3 (large/xlarge, >10 Mb) LD regions currently get **NO allele frequency**.
`src/python/bm_to_npz.py` — the A.3 BlockMatrix->.npz converter — writes only `ld` +
`variant_ids` + `rsids` (+ the `lower_triangular` flag added by the BR-01 fix). It writes
NO `allele_freq` key, so `ld_npz_to_rds.R` fills `obj$variants$AF` with NA for every A.3
region. The phase deliverable is "LD + AF metadata", and A.3 IS the large/xlarge regions
(incl. the xlarge-split sub-region windows), so this is a real coverage hole.

Pre-existing gap, NOT a CR-01-fix regression — surfaced and deferred during the m3-02b
BR-01 blast-radius sweep (2026-06-19). A.1/A.2 already carry AF via `_save_npz`; only the
A.3 BlockMatrix-export path is missing it. **PRECONDITION for the m3-04 production A.3
fire — do not ship the A.3 LD panel claiming "LD + AF" until this is closed.**

## Solution

NCSU / in-perimeter code (its own task — do not hand-wave):
1. A.3 branch of `aou_ld_panel.py::compute_region_ld` EXPORTS a row-aligned AF sidecar
   (same `_af_or_nan` collection as A.1/A.2) alongside the variant_ids/rsids sidecars it
   already writes for the exported BlockMatrix.
2. `bm_to_npz.py` READS that AF sidecar and writes `allele_freq=` into the `.npz`
   (NaN for genuinely-missing, per WR-03). Assert row-alignment to variant_ids.
3. Round-trip test: an A.3-style `.npz` carries row-aligned AF into `obj$variants$AF`
   (extend tests/m3/test_ld_npz_to_rds.py).

Trigger: address fully when m3-02c's preflight probes the A.3 sub-regions
(m2_region_00040__sub00, region_00145), or at the latest before m3-04 production.
Detail + rationale: `.planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-BLAST-RADIUS-FIX.md`
(DEFERRED section) + carry-forward note in the m3-02c PLAN.
