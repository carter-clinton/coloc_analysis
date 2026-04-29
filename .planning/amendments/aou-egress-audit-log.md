# AoU Egress Audit Log

**Status:** HARD GATE PASS as of 2026-04-28 (NCSU faculty controlled-tier
AoU Researcher Workbench access; institutional DUS/RPS/P&P coverage; LD R
matrices governed by standard AoU egress review — automated + manual
reviewer pipeline — at egress-request time). Carter PI confirmation
2026-04-28 via quick task 260428-vt2.

This file is **append-only**. Each entry documents one AoU export request
crossing the AoU Researcher Workbench egress boundary onto NCSU GPFS.

**OSF cross-reference:** `osf.io/az52u` (Project amendment record;
DEC-2026-04-25-02 form).

**M3 egress scope:** 44 export bundles total (22 chromosomes × 2 ancestries
AFR_aou + EUR_aou per D-M3-01 + D-M3-02). M1-supplementary AFR-SBP
derivation (DEC-2026-04-24-02) appends to this log under its own section.

---

## Egress Classification Ruling (HARD GATE) — RULED PASS 2026-04-28

**Per AOU-LD-PIPELINE.md §12 Risk R1 (original framing):** the M3 plan
seeded this gate expecting a written per-data-class ruling letter from
AoU support classifying variant×variant LD matrices computed from
n ≥ 60k AFR participants as "aggregate summary statistics" (exportable
by default), not "derived individual-level data" (requires additional
review). On 2026-04-28 Carter PI established that no such custom ruling
letter is required: variant×variant LD R matrices are aggregate /
derived statistics carrying no individual-level information and pass
through standard AoU egress review (automated + manual reviewer
pipeline) at egress-request time, governed by Carter's institutional
NCSU faculty controlled-tier access — not by per-data-class custom
rulings. All 44 production egress requests inherit this classification
under standard egress review.

| Date | Request type | Classifier (AoU support email/case ID) | Ruling | Document |
|------|--------------|----------------------------------------|--------|----------|
| 2026-04-28 | Variant×variant LD matrix from n≥60k AFR (also EUR ~130k) | NCSU faculty controlled-tier AoU access; institutional DUS/RPS/P&P coverage; standard AoU egress review applies (no per-data-class custom letter required) | **PASS** | This audit log row + ruling block below; Carter PI confirmation 2026-04-28; quick task 260428-vt2 commit (m3-W1-portal-cleared) |

### Ruling block — 2026-04-28

* **Status:** **PASS**
* **Date:** 2026-04-28
* **Basis:** NCSU faculty controlled-tier AoU Researcher Workbench
  access; institutional Data Use Statement / Research Purpose Statement /
  Privacy & Permissions registrations covered at faculty access tier;
  billing profile attached with initial credits active. Variant×variant
  LD R matrices are aggregate / derived statistics (no individual-level
  information) governed by **standard AoU egress review** (automated +
  manual reviewer pipeline) at egress-request time, NOT by
  per-data-class custom ruling letters. Carter PI confirmation
  2026-04-28.
* **Provenance:** AoU Researcher Workbench account, NC State University
  faculty appointment (ASHES Laboratory, Department of Biological
  Sciences). Workspace creation + billing verification + DUS/RPS/P&P
  acceptance all flowed through the standard NCSU-faculty controlled-tier
  pathway (no individualized AoU support case opened).
* **Re-open conditions:** if standard AoU egress review at any future
  egress-request time flags a specific variant×variant LD matrix file
  for additional review, document the per-file event in this audit log
  with the AoU reviewer's specific concern + resolution. Do **NOT**
  pre-emptively re-open this HARD GATE absent a triggering event;
  per-file egress-review events are routine and append under
  `## Per-Bundle Audit Entries` below, not under this ruling block.
* **Cross-reference:** OSF pre-registration `osf.io/pvb5j`
  (DOI 10.17605/OSF.IO/PVB5J); closeout amendment `osf.io/az52u`;
  `.planning/STATE.md` Wave 1 Readiness Checklist row;
  `.planning/phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md`
  (the only remaining Wave 1 pre-condition: per-region-LD AUX path
  verification, gated on Carter Workbench session).

**Note:** All 44 M3 production egress bundles + any M1-supplementary
AFR-SBP egress bundles inherit this PASS ruling under standard AoU
egress review. Per-bundle entries below populate at Wave 4 production
fire (per D-M3-03 dev-to-production gate).

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

**Last updated:** 2026-04-28 (HARD GATE ruled **PASS** under NCSU faculty
controlled-tier basis; standard AoU egress review applies at
egress-request time; quick task 260428-vt2 commit `(m3-W1-portal-cleared)`)
