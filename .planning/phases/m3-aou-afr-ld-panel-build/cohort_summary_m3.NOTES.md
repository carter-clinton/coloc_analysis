# cohort_summary_m3.tsv — provenance & status note

**Status:** COMPLETE (3 of 3 cohorts). Written 2026-06-10; `AFR_pca_selfid` recovered + banked 2026-06-11.

`cohort_summary_m3.tsv` is the GPFS-canonical mirror of the genome-wide M3 AoU
cohort build. It holds **3 rows** — `AFR_pca`, `EUR_pca` (the two uncontaminated
genetic-ancestry cohorts) and `AFR_pca_selfid` (the D-M3-07 self-report
sensitivity cohort, recovered 2026-06-11 — see "AFR_pca_selfid recovery" below).
This closes **GATE 1.5** (all 3 cohorts built genome-wide); LD compute (Wave 2)
is unblocked on the cohort axis.

## Cohorts banked (both verified at the data layer, not the notebook print)

| cohort | samples | variants | _SUCCESS (UTC) | entries/rows/parts floor |
|---|---|---|---|---|
| AFR_pca | 73,122 | 20,767,864 | 2026-06-07T15:37:30Z | 1,603.66 GB |
| EUR_pca | 220,098 | 11,375,140 | 2026-06-10T00:03:29Z | 3,433.88 GB (≈3.12 TiB) |
| AFR_pca_selfid | 62,557 | 20,817,925 | promoted 2026-06-11 (rsync ← verified dry-run scratch) | 1,380.19 GB (≈1.38 TB) |

- Counts re-`.count()`ed off the written MatrixTables (self-consistent with the
  files, not transcribed). Both checkpoint paths are the clean `sensitivity=False`
  MTs. `kinship_threshold = 0.0442` (KING), `ancestry_field = ancestry_pred`.
- AFR samples −1.3% vs Gate-C chr22's 74,059, EUR −0.69% vs 221,624 — genome-wide
  `call_rate ≥ 0.98` correctly dropping low-quality samples chr22-alone missed.
- Disjoint check PASSED: `AFR ∩ EUR = ∅` (73,122 + 220,098, zero overlap).
- W1 empty-MT regression guard (Cell 5.5) PASSED for EUR (3,433.88 GB ≫ 1 GB floor).

## AFR_pca_selfid recovery (2026-06-11)

The self-ID sensitivity cohort took two attempts to land:

1. **Contamination (fixed).** The first build (06-07/08) was a silent no-op:
   `sensitivity=True` degraded to the genetic-ancestry-only predicate (AFR-sens ==
   AFR-primary, membership-identical) because `self_report` was never sourced. Root
   cause + TDD fix: `.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md`
   (SENS_FILTER_VERSION=2; match the stable survey code `WhatRaceEthnicity_Black`).
   The clean re-fire proved the fix in-run: **74,576 → 63,312** self-report subset.
   The self-report sidecar was regenerated natively in-perimeter against the v8
   CDR (`wb-silky-artichoke-2408.C2024Q3R8`), sidestepping the VPC-SC-stranded v9
   classic sidecar and version-matching the v8 cohorts.

2. **Empty-final catastrophe (recovered).** The clean re-fire then built all 22
   per-chrom intermediates (~1.29 TB) but the driver was killed mid-finalize-flush
   (root cause **H1** — external kill / stray navigation, NOT a logic/config bug;
   the larger AFR-primary + EUR finalized fine under identical config), leaving a
   lying `_SUCCESS` over a 0-byte final. Diagnosis:
   `.planning/debug/m3-W2-afr-sens-empty-final-merge.md`. Recovery = a finalize-only
   re-drive from the 22 intact intermediates, proven read-only in a `_scratch`
   dry-run (entries ~1.38 TB; cols 62,557; rows 20,817,925; `self_report` present),
   then promoted to the live URI via `gsutil -m rsync -r -d` and re-verified at the
   data layer (live counts identical to scratch; du-floor 1,380.19 GB).

**Banked shape:** 62,557 samples × 20,817,925 variants — a strict subset
(62,557 < 63,312 self-report union < 73,122 AFR-primary; the contamination tell of
a byte-identical 73,122-sample copy is **absent**). `.describe()` confirms
`self_report` sourced as a Column field. Sample-QC dropped 755/63,312 (1.19%) on
call_rate≥0.98 + het±3SD.

The contaminated v1 MT is parked at
`ld/_forensics/contaminated_afr_selfid_noop_20260608/` (~7.8 TiB), awaiting a
**separate green-light** for deletion (not auto-fired). A durable atomic-final-write
fix to close the H1 `_SUCCESS`-before-validate window is designed but not yet
applied — see `DURABLE-FIX-DESIGN-atomic-final-write.md`; route via
`/gsd-plan-phase --gaps`.

## Cluster-side copy

A copy was written cluster-side to
`/home/dataproc/coloc_analysis/.planning/notebooks/cohort_summary_m3.tsv`
(266 bytes, mtime 2026-06-10T02:02:11Z). That copy is incidental (notebook CWD);
THIS file is the canonical record.
