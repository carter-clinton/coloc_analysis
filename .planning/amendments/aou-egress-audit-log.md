# AoU Egress Audit Log

**Status:** seeded 2026-04-28 by m3-00 Wave 0; HARD GATE row currently
PENDING — populated at Wave 1 once Carter receives written egress
classification ruling from AoU support (AOU-LD-PIPELINE.md §12 R1).

This file is **append-only**. Each entry documents one AoU export request
crossing the AoU Researcher Workbench egress boundary onto NCSU GPFS.

**OSF cross-reference:** `osf.io/az52u` (Project amendment record;
DEC-2026-04-25-02 form).

**M3 egress scope:** 44 export bundles total (22 chromosomes × 2 ancestries
AFR_aou + EUR_aou per D-M3-01 + D-M3-02). M1-supplementary AFR-SBP
derivation (DEC-2026-04-24-02) appends to this log under its own section.

---

## Egress Classification Ruling (HARD GATE)

**Per AOU-LD-PIPELINE.md §12 Risk R1:** before any Dataproc compute fires,
Carter must obtain a written ruling from AoU support classifying
variant×variant LD matrices computed from n ≥ 60k AFR participants as
"aggregate summary statistics" (exportable by default), not "derived
individual-level data" (requires additional review). All 44 production
egress requests inherit this classification.

| Date | Request type | Classifier (AoU support email/case ID) | Ruling | Document |
|------|--------------|----------------------------------------|--------|----------|
| TBD-Wave-1 | Variant×variant LD matrix from n≥60k AFR (also EUR ~130k) | TBD (AoU support case # ____) | PENDING | TBD (link to AoU email or PDF capture) |

**Note:** This row stays as PENDING until Carter completes the Wave 1
human-action gate. It is intentionally left visible so all downstream
egress entries reference the classification ruling that authorizes them.

---

## Per-Bundle Audit Entries

Schema: 13-column table (one row per per-chromosome × ancestry export bundle).

* `Timestamp (ISO-8601 UTC)` — when Carter filed the AoU export request via
  the portal Notebooks/Files UI (Q3 export pathway).
* `Phase` — M3 (this file's primary scope) or M1 (supplementary AFR-SBP).
* `Chr` — autosomal chromosome 1-22.
* `Ancestry` — `AFR_aou` or `EUR_aou`.
* `n_regions` — count of M2 regions in the bundle (per chromosome).
* `Compressed size (GB)` — bundle size after `np.savez_compressed` + AoU
  upload-to-egress staging (per-bundle cap 50 GB per RESEARCH Q4
  recommendation; split within-chromosome if exceeded).
* `AoU export request ID` — assigned by AoU portal upon submission.
* `OSF cross-ref` — `osf.io/az52u` for all M3 entries.
* `SHA-256 manifest path` — per-bundle sub-manifest TSV under
  `.planning/amendments/sha256/m3_chr{N}_{ANCESTRY}.tsv` (created at
  Wave 5 close-out per RESEARCH Q12 recommendation).
* `Bundle content (region_ids)` — comma-separated M2 region IDs in the
  bundle, e.g., `m2_region_00001..m2_region_00014`.
* `Reviewed by AoU on` — date AoU support approved the export.
* `Egressed to NCSU on` — date the bundle landed at
  `data/interim/aou_ld_exports/{ANCESTRY}_aou/`.
* `Notes` — free-form (e.g., "split chr1 into 1a + 1b due to >50 GB").

| Timestamp (ISO-8601 UTC) | Phase | Chr | Ancestry | n_regions | Compressed size (GB) | AoU export request ID | OSF cross-ref | SHA-256 manifest path | Bundle content (region_ids) | Reviewed by AoU on | Egressed to NCSU on | Notes |
|--------------------------|-------|-----|----------|-----------|----------------------|------------------------|---------------|------------------------|------------------------------|--------------------|---------------------|-------|
| _(landed at Wave 4 production fire; first row appears after dev gate clears + production batch dispatched per D-M3-03)_ | | | | | | | | | | | | |

---

## M1-AFR-SBP cross-reference (DEC-2026-04-24-02)

Per DEC-2026-04-24-02 — the M1 AFR-SBP fallback derivation establishes the
AoU compute path scaffolding. M1-supplementary appends per-bundle entries
here under this section, sharing the same egress-classification ruling
above (one written ruling, multiple inheriting derivations).

| Timestamp | Phase | Derivation | AoU request ID | OSF cross-ref | Egressed to | Notes |
|-----------|-------|------------|----------------|---------------|-------------|-------|
| _(M1-supplementary populates; out of M3 scope)_ | M1 | AFR-SBP fallback | | osf.io/az52u | | |

---

## Audit log policy

* **Append-only.** Lines are added; never deleted nor modified after commit.
  An incorrect entry is corrected by a follow-up row tagged `[CORRECTION
  for {original timestamp}]` under Notes.
* **Commit discipline.** Each appended row commits as `docs(m3-W4): record
  AoU egress request {id} for chr{N} {ancestry}` (Wave 4 production fire)
  or `docs(m3-W5): finalize AoU egress audit log monolith SHA-256s`
  (Wave 5 close-out).
* **OSF posting.** This file is included in the Wave 5 OSF supplementary
  upload to osf.io/az52u alongside `m3-VALIDATION.md` (per D-M3-08).

**Last updated:** 2026-04-28 (Wave 0 seed; HARD GATE PENDING)
