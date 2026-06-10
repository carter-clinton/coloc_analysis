# cohort_summary_m3.tsv — provenance & status note

**Status:** INTERIM (2 of 3 cohorts). Written 2026-06-10.

`cohort_summary_m3.tsv` is the GPFS-canonical mirror of the genome-wide M3 AoU
cohort build. It currently holds **2 rows** — `AFR_pca` and `EUR_pca` — the two
uncontaminated, genetic-ancestry cohorts. The third row, **`AFR_pca_selfid`**
(the D-M3-07 self-report sensitivity cohort), is **DEFERRED** — see below.

## Cohorts banked (both verified at the data layer, not the notebook print)

| cohort | samples | variants | _SUCCESS (UTC) | entries/rows/parts floor |
|---|---|---|---|---|
| AFR_pca | 73,122 | 20,767,864 | 2026-06-07T15:37:30Z | 1,603.66 GB |
| EUR_pca | 220,098 | 11,375,140 | 2026-06-10T00:03:29Z | 3,433.88 GB (≈3.12 TiB) |

- Counts re-`.count()`ed off the written MatrixTables (self-consistent with the
  files, not transcribed). Both checkpoint paths are the clean `sensitivity=False`
  MTs. `kinship_threshold = 0.0442` (KING), `ancestry_field = ancestry_pred`.
- AFR samples −1.3% vs Gate-C chr22's 74,059, EUR −0.69% vs 221,624 — genome-wide
  `call_rate ≥ 0.98` correctly dropping low-quality samples chr22-alone missed.
- Disjoint check PASSED: `AFR ∩ EUR = ∅` (73,122 + 220,098, zero overlap).
- W1 empty-MT regression guard (Cell 5.5) PASSED for EUR (3,433.88 GB ≫ 1 GB floor).

## Why the AFR_pca_selfid row is deferred (not missing-by-error)

The first sensitivity build (06-07/06-08) was a **silent no-op**: `sensitivity=True`
degraded to the genetic-ancestry-only predicate (AFR-sens == AFR-primary,
membership-identical) because the `self_report` column was never sourced. Root
cause + TDD fix: `.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md`
(SENS_FILTER_VERSION=2; match the stable survey code `WhatRaceEthnicity_Black`).

The contaminated `mt_afr_pca_selfid_qc.mt` (v1) remains **parked in the live path,
untouched**, awaiting green-light for a `ld/_forensics/` move — held until a clean
re-fire is staged.

The clean re-fire needs a `research_id → self_report` sidecar TSV. The validated
v9 sidecar is stranded in the **classic** RW 1.0 bucket; cross-perimeter transfer
to the Verily 2.0 bucket is VPC-SC-blocked on every self-serve path (AoU ticket
open; Folder Sync is the additive fallback). **Preferred path: regenerate the
sidecar natively in Verily against the in-perimeter v8 CDR** — which also fixes a
latent version mismatch (cohorts are v8 / C2024Q3R8; the stranded sidecar is v9 /
C2024Q3R9). When that lands, re-fire `sensitivity=True` (expect
`0 < N_sens < 73,122`, strict subset), then **backfill this file to 3 rows**.

## Cluster-side copy

A copy was written cluster-side to
`/home/dataproc/coloc_analysis/.planning/notebooks/cohort_summary_m3.tsv`
(266 bytes, mtime 2026-06-10T02:02:11Z). That copy is incidental (notebook CWD);
THIS file is the canonical record.
