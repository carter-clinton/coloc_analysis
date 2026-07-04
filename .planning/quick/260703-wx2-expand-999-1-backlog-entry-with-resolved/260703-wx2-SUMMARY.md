# Quick Task 260703-wx2 — SUMMARY

**Expand the 999.1 backlog entry with the resolved OSF finding + 6-step work breakdown**

**Date:** 2026-07-04 · **Branch:** m3-W2-aou-deltas · **Mode:** quick (inline exec) · **Docs-only**

## What & why

Seth resolved the open OSF-coverage question on backlog **999.1** (LD NaN→0 + PSD
conditioning) and produced a full design breakdown. This task APPENDS that design detail
to the parked 999.1 entry in `.planning/ROADMAP.md` — **design capture, NOT promotion**
(status stays `parked`; no milestone scheduled, no phase fired).

## The resolved finding (headline)

`osf-amendment-r3-2026-05-04.md` is **EUR-only** — it pre-registers PSD (ridge
λ∈{0.001,0.01,0.1} + eigclip λ_floor=1e-6) for the **1000 Genomes Phase 3 EUR** LD
matrix (`ld_reference/EUR/SH2B3_12q24.rds`, SH2B3 + 4 EUR regions), and its "what is not
changing" clause pins the substrate to the EUR panel. It does **not** cover the AFR
native panel or a NaN→0 step. So the PSD *methods* are reusable, but their
*pre-registration coverage* is not → **999.1 needs a NEW OSF amendment**, and that
governance step (not the small code) is the **true blocker on promotion**.

## What was appended (Seth verbatim, under a new `#### 999.1 design detail` sub-heading)

- **Reuse-not-reinvent** — factor the existing `psd_regularize_ridge` / `psd_regularize_eigclip`
  (`refit_sh2b3_psd_regularized.R`) into a shared `src/R/regularization/psd_utils.R`; no 3rd impl.
- **NaN topology locks the policy** — region-1: 12 NaN, 11 rows, **0 fully-NaN rows** →
  isolated symmetric off-diagonal pairs among clustered low-MAF variants → pairwise-undefined
  `r` → **NaN→0 + PSD, per-region provenance, NOT a variant drop**; util branches on topology
  (a fully-NaN row = zero-variance → drop by QC).
- **Pipeline placement + ordering** — NaN→0 at a recorded conditioning stage (raw `.npz`
  stays NaN-raising); PSD at fit time on the region submatrix (full 102421² eigen ~195 GiB >
  120 GB VM, infeasible). Order fixed: **NaN→0 first, PSD second** (`eigen()` is all-NaN on NaN).
- **OSF gate RESOLVED** — new AFR amendment required (Carter posts; agent only drafts; draft
  before conditioning code so params lock first).
- **Fine-mapping caveats** — unmeasured-independence flag on same-credible-set zeroed pairs +
  PIP sensitivity; record `max|R_reg−R|` + min-eig before/after; λ/method pre-specified.
- **6-step work breakdown** (for `/gsd-plan-phase` when promoted): OSF gate → refactor PSD →
  NaN→0 util → conditioned artifact → fit-time wiring+diagnostics → region-1 verification.
- **Do-NOTs** + design refs (`ticket_999_1_nan_psd_design.md`, the EUR-only amendment, the R module).

## Provenance verified (read-only, this session, at HEAD 7750448)

- FIND anchor unique at `ROADMAP.md:1000`.
- `osf-amendment-r3-2026-05-04.md` exists + confirmed EUR-only (1000G EUR; defers AFR to
  "Track B … All of Us EUR").
- `refit_sh2b3_psd_regularized.R` has `psd_regularize_ridge` (L71) + `psd_regularize_eigclip`
  (L80), applied on `R_sub` (L170/172).

## Verification

- `grep -c "^### 999.1"` == 1 (one entry, no heading break); `#### 999.1 design detail` == 1;
  stub lead line intact; **Status: parked** unchanged; hierarchy `## Backlog → ### 999.1 →
  #### design detail`.
- No milestone/phase promotion added ("`/gsd-plan-phase when promoted`" is a conditional note).

## Boundaries honored

- Docs-only; committed **only** `.planning/ROADMAP.md` + `.planning/STATE.md` (house rule),
  explicit paths. No code, no re-fire, no promotion.
