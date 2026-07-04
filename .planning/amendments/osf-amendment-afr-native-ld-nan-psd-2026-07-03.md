> POSTED 2026-07-04T04:14:46Z as https://osf.io/az52u/files/tcujq

# OSF Amendment — Paste-Ready Text (AFR native-plink LD panel: NaN→0 + PSD conditioning)

> **DRAFT for Carter review.** Modeled on `osf-amendment-r3-2026-05-04.md` (same
> paste-ready structure). The design rationale lives in the 999.1 backlog entry
> (`.planning/ROADMAP.md`) and the Science-side ticket `ticket_999_1_nan_psd_design.md`.
> This file contains the OSF web-UI paste-ready body bracketed by
> `--- PASTE INTO OSF FROM HERE ---` / `--- PASTE ENDS HERE ---`.
> **Nothing here fires code or compute. This document must post to OSF BEFORE any
> AFR NaN→0 / PSD conditioning code is written or run** (pre-registration discipline:
> the λ/method/ceiling/outcome-branches lock before the fit can influence them).

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | `osf.io/az52u` — post as supplementary file on the existing parent amendment record (matches the M1 + r3 pattern: body uploaded as a file on `az52u` rather than a new record). |
| Amendment kind | Methods amendment. Extends the multi-ancestry / genome-wide reframe (2026-04-25, Track B) to the **AFR** native-plink LD panel: adds a pairwise-NaN conditioning policy (`NaN→0` + `n_zeroed` ceiling) and re-uses the r3 PSD methods (ridge / eigenvalue-clip) for the AFR panel, which r3 itself does NOT cover (r3 is EUR-only). |
| Original pre-registration being amended | `osf.io/pvb5j` (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| Supersedes-but-incorporates | Extends the 2026-04-25 genome-wide/Track-B reframe and the r3 PSD-regularization amendment (`osf-amendment-r3-2026-05-04.md`, EUR-only). r3 is NOT retracted; this amendment reuses its `psd_regularize_ridge`/`psd_regularize_eigclip` methods and extends their pre-registered scope to AFR. |
| Posting gate | BEFORE any AFR conditioning code fires (before `src/R/regularization/psd_utils.R` is sourced by an AFR fit, and before any `condition_ld_matrix` output is banked). The NaN→0 policy, `n_zeroed` ceiling, PSD method + λ, and outcome branches are fixed BEFORE discovery, not after. |
| Substrate | All of Us AFR WGS native-plink LD panel (`gs://…/ld/afr_native_panel/{region}.npz`, 276 regions). Controlled-tier: only aggregate summaries egress; no raw genotypes, no full LD matrix. |
| Expected posting date | `2026-07-03` — fill with actual posting date before paste. |

**Pre-paste checklist (top-to-bottom before submitting the OSF form):**

1. Fill the `2026-07-03` placeholders (Date field + the pre-execute commit gate).
2. Confirm the pre-execute gate commit `0f3c68b` is still HEAD of `m3-W2-aou-deltas` at posting time (no AFR conditioning code has landed since): `git rev-parse --short HEAD` must return `0f3c68b`. If HEAD has advanced with unrelated commits, update the two `0f3c68b` references to the new HEAD before posting.
3. Confirm the r3 PSD functions still resolve at HEAD: `grep -l "psd_regularize_ridge\|psd_regularize_eigclip" src/R/regularization/*.R` returns the source file.
4. After OSF posts, copy the amendment record URL + OSF timestamp into `.planning/osf_deviations.md` under a new dated entry; the timestamp MUST precede any AFR conditioning-output commit.

---

--- PASTE INTO OSF FROM HERE ---

**Amendment to pre-registration osf.io/pvb5j: AFR native-plink LD panel — pairwise-NaN conditioning and PSD regularization for colocalization / fine-mapping**

**Date:** 2026-07-03

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of amendment:** This amendment pre-registers a linkage-disequilibrium conditioning policy for the African-ancestry (AFR) native-plink LD panel built from All of Us whole-genome sequencing, used as the LD reference for colocalization and SuSiE-RSS fine-mapping in the multi-ancestry arm. It specifies (a) an off-diagonal `NaN→0` policy for pairwise-undefined correlation entries, with a pre-registered per-region ceiling above which a region is deferred rather than conditioned, and (b) reuse of the positive-semi-definite (PSD) regularization methods already pre-registered for EUR under the 2026-05-04 amendment (`osf.io/az52u`, ridge and eigenvalue-clip), now extended in scope to the AFR panel. The allowable outcome branches are locked ahead of execution so the fine-mapping narrative cannot be conditioned on the result.

**Motivation:** The AFR native-plink LD panel (plink1.9 `--r square bin4`, `--keep-allele-order`, `--mac 1`, per 276 genomic regions) emits `NaN` for a small number of pairwise correlation entries. An in-perimeter aggregate diagnostic of the first region (n_var = 102421 variants; only counts, variant IDs, and MAF/missingness egressed — no genotypes) found 12 `NaN` cells across 11 variant rows, occurring exclusively as symmetric off-diagonal pairs between index-adjacent low-minor-allele-frequency variants (MAF 0.005–0.02, missingness ≤ 0.05, no all-heterozygous signature), clustered in five tight base-pair windows. These are **pairwise-undefined correlations** — the correlation `r` for that specific variant pair is `0/0` on the subset of samples non-missing for both variants — and are NOT zero-variance (monomorphic) variants and NOT a demonstrated software defect. Discarding the 11 variants would remove genuine low-frequency signal; the appropriate handling is to condition the matrix (set the undefined off-diagonal entries to zero, then regularize to PSD) rather than to drop variants. Because `eigen()` cannot decompose a matrix containing `NaN`, and because zeroing off-diagonal entries can introduce mild indefiniteness, PSD regularization is required downstream. A pre-registered policy is needed so the conditioning parameters are not chosen to fit a fine-mapping result.

**New analytical commitments — AFR native-panel NaN conditioning:**

(a) **Topology branch.** For each region LD matrix, `NaN` entries are classified before conditioning:
- If any variant row is *entirely* `NaN` (a zero-variance / monomorphic-within-analysis-set source variant), that variant is DROPPED by minor-allele-frequency / missingness quality control on the actual analysis sample set, and the drop is recorded — it is NOT zero-conditioned.
- Otherwise (isolated off-diagonal `NaN` pairs, the observed case), the undefined off-diagonal entries are set to `0.0` (the diagonal is unaffected; it is 1.0 by construction).

(b) **Zeroing ceiling (pre-registered, per region).** Off-diagonal `NaN→0` is applied only when the number of zeroed pairs in a region does not exceed **0.05 percent of the region's variant count** (`n_zeroed_pairs ≤ 0.0005 × n_var`; e.g. ≤ 51 pairs at n_var = 102421, against an observed 6 in region 1). A region exceeding this ceiling is treated as a substrate anomaly, is NOT conditioned, and is deferred for re-diagnosis and disclosed as a deviation — a large `NaN` fraction indicates an LD-construction problem, not a conditioning case.

(c) **PSD regularization (reuse of the r3 methods, extended to AFR).** After `NaN→0`, the region correlation submatrix used for fine-mapping is regularized to positive-semi-definite form by the eigenvalue-clip method (Hutchinson 2020: clip eigenvalues to floor `λ_floor = 10⁻⁶`, reconstruct, row-and-column normalize), with the Wen et al. 2017 ridge addition `R_reg = R + λI` (swept `λ ∈ {0.001, 0.01, 0.1}`) run as a robustness companion — the identical implementations pre-registered for EUR in the 2026-05-04 amendment (`psd_regularize_eigclip`, `psd_regularize_ridge`). Eigenvalue-clip at `λ_floor = 10⁻⁶` is the primary (least aggressive: it perturbs only genuinely negative eigenvalues); the ridge sweep is the robustness comparison. PSD regularization is applied to the fine-mapping **region submatrix** at fit time, not to the full per-region panel matrix (a full-panel eigen-decomposition at n_var ≈ 10⁵ is computationally infeasible and analytically unnecessary).

(d) **Provenance (recorded per region, egress-safe aggregates).** For each region: `n_zeroed_pairs`, the zeroed variant-pair indices, the `NaN` policy label, the PSD method and λ used, and — per fine-mapping region submatrix — `max|R_reg − R|` and the minimum eigenvalue before and after regularization. These aggregate diagnostics are the only conditioning outputs that egress the All of Us perimeter; no raw genotypes or full LD matrices leave.

**Outcome branches (pre-registered, per fine-mapping region that consumes a conditioned AFR submatrix):**

- `BRANCH_AFR_COND_CLEAN` — the region contains no zeroed pair (no NaN in its submatrix); conditioning is a no-op and the fine-mapping result stands unmodified.
- `BRANCH_AFR_COND_APPLIED` — the region contains ≥ 1 zeroed pair under the ceiling and the post-PSD submatrix is positive-semi-definite (minimum eigenvalue ≥ 0); the fine-mapping result is reported WITH the conditioning provenance, and for any credible set overlapping a zeroed pair a posterior-inclusion-probability sensitivity (fit with vs without the affected variants) is reported alongside.
- `BRANCH_AFR_COND_DEFERRED` — the region exceeds the `n_zeroed` ceiling (substrate anomaly); the region is deferred, not conditioned, and disclosed as a deviation with its `NaN` count.

All three outcomes are reportable; conditioning a region silently, or choosing λ/method to obtain a particular fine-mapping result, is the only path not on this list.

**What is superseded by this amendment:**

- AFR native-plink LD panel used for colocalization / fine-mapping with unhandled `NaN` correlation entries → pre-registered `NaN→0` + PSD conditioning with a per-region ceiling and recorded provenance.
- PSD regularization scope limited to the EUR 1000 Genomes reference panel (r3) → the same ridge / eigenvalue-clip methods extended, under this amendment, to the AFR native panel.

**What is not changing:**

- Pre-registration discipline. The `NaN→0` policy, the `n_zeroed` ceiling, the PSD method and λ values, and the three outcome branches are fixed before any conditioning code fires; the manuscript narrative commits to the empirical branch, not the rhetorically convenient one. Deviations are logged in `.planning/osf_deviations.md` and disclosed in the manuscript's "Deviations from pre-registration" section.
- The PSD implementations themselves. `psd_regularize_ridge` and `psd_regularize_eigclip` are the same functions pre-registered in the 2026-05-04 amendment; this amendment reuses them (factored into a shared utility) and does not alter their numerics.
- Multi-method triangulation and honest reporting of nulls. A conditioned-LD colocalization or fine-mapping signal is corroborated by the same triangulation scaffold used elsewhere in the program; a signal that appears only under one λ/method is reported as fragile.
- All of Us controlled-tier data handling. Only aggregate summaries egress the perimeter; no raw genotypes and no full LD matrices. No wet-lab validation; public-data-only for all non-AoU substrate.
- Honest-original-research framing. This is pre-registered original conditioning methodology for the AFR panel, not a fix, cleanup, correction, or salvage of prior work.

**Expected timeline:** This amendment is posted at the start of the AFR native-panel conditioning work (999.1), before any conditioning code is sourced by a fit or any conditioned output is banked. The pre-execute hard gate is repository commit `0f3c68b`. Realized outcome branches and the per-region conditioning provenance are added as a follow-up OSF update at the conditioning-phase closeout.

--- PASTE ENDS HERE ---

---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm the OSF timestamp precedes any commit containing AFR conditioning outputs (no conditioned `.npz`/`.rds` and no `condition_ld_matrix` provenance on disk at posting time). If precedence is violated, log a deviation in `.planning/osf_deviations.md` immediately.
2. Copy the amendment record URL + OSF timestamp into `.planning/osf_deviations.md` under a new dated entry.
3. Tag the pre-execute gate commit: `git tag AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-03`.
4. Update STATE.md / DECISIONS.md with the coverage decision (`D-AFR-NANPSD-OSF-COVERAGE: COVERED at <timestamp>`) so the 999.1 W1 plan has a hard-gate target.

**If any commitment changes between posting and closeout:** pause at the next wave boundary, log the deviation, and if an outcome-branch rule changes, post a subsequent amendment-update citing this record URL.

**Rollback:** Do not delete this file. OSF amendments are append-only; if retracted, add a superseded-by pointer at the top.
