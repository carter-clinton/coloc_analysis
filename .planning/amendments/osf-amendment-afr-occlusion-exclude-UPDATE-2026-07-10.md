> POSTED 2026-07-10T13:32:22Z as a supplementary file on https://osf.io/az52u (filename `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`; direct file GUID/URL to be filled from the OSF file page).

# OSF Amendment-Update — Paste-Ready Text (AFR native-plink LD panel: withdraw NaN→0, adopt occlusion exclude-in-lockstep + provenance manifest)

> **DRAFT for Carter review.** Modeled on `osf-amendment-afr-native-ld-nan-psd-FILLED.md` (the amendment this one updates) — same paste-ready structure. This is a correction / partial-withdrawal amendment-update: the in-perimeter diagnostics run after the prior amendment posted established that the AFR panel NaN entries are NOT benign pairwise degeneracies but structurally undefined LD from overlapping-deletion occlusion, which makes the pre-registered NaN→0 treatment directionally wrong. It withdraws NaN→0 and pre-registers the replacement (exclude-in-lockstep + mandatory provenance manifest). Nothing here fires code or compute. This must post to OSF BEFORE any occlusion exclude/normalization code is written or run, and before any NaN→0 conditioning output is banked (the withdrawal must be on the record before the replacement executes).

> **Posting-target reconciliation (the new-file vs withdrawal-note question):** OSF amendments are append-only, so this posts as a new supplementary file on the existing `osf.io/az52u` record (consistent with the M1 / r3 / tcujq pattern) — AND it carries explicit supersedes semantics: it withdraws the NaN→0 policy of file tcujq (posted 2026-07-04) and directs that a superseded-by pointer be added at the top of the project-side copy of the prior amendment. New file for the mechanism; withdrawal semantics for the policy. Both, not either.

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | `osf.io/az52u` — post as a NEW supplementary file on the existing parent amendment record (append-only; same pattern as tcujq). |
| Amendment kind | Methods amendment-update (correction + partial withdrawal). Withdraws the NaN→0 off-diagonal conditioning of the 2026-07-04 AFR amendment (az52u file tcujq) and pre-registers the replacement treatment for occlusion-undefined LD entries. |
| Prior amendment being updated | `osf.io/az52u` file tcujq (AFR native-plink LD panel: NaN→0 + PSD conditioning), posted 2026-07-04T04:14:46Z. |
| Original pre-registration | `osf.io/pvb5j` (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| What is withdrawn | ONLY the NaN→0 off-diagonal conditioning of isolated pairwise-undefined entries (prior amendment items (a)-isolated-pair-branch and (b) the zeroing ceiling) and its three BRANCH_AFR_COND_* outcomes. |
| What is retained unchanged | The PSD regularization methods and λ (prior item (c) / r3 `psd_regularize_eigclip` λ_floor=1e-6 primary, `psd_regularize_ridge` λ∈{0.001,0.01,0.1} robustness) for the fit-time region submatrix; the fully-NaN-row → drop rule (it converges with the new policy); the raw-panel NaN-raise contract; pre-registration discipline; AoU controlled-tier handling. |
| Posting gate | BEFORE any occlusion exclude / span-filter / lockstep-sumstats-drop code fires, and before any NaN→0-conditioned AFR output is banked. |
| Substrate | All of Us AFR WGS native-plink LD panel (`gs://…/ld/afr_native_panel/`, 276 regions). Controlled-tier: only aggregate summaries + coordinate geometry egress; no raw genotypes, no full LD matrix. |
| Pre-execute commit gate | `5fd58a5` — fill with the current HEAD of `m3-W2-aou-deltas` AFTER the four amendment docs land (scientific review `3516c18`, hinge check `c4e0875`, policy `8f36fdf`, geometry verdict `5fd58a5`). Confirm no occlusion-exclude code has landed at posting time. |
| Expected posting date | `2026-07-10` (actual OSF activity timestamp 2026-07-10T13:32:22Z). |

**Pre-paste checklist (top-to-bottom before submitting the OSF form):**

1. Fill `5fd58a5` (current HEAD of `m3-W2-aou-deltas` after the four amendment docs land + push) and the `2026-07-10` posting date.
2. Confirm no occlusion exclude / span-filter / lockstep-drop code has landed at posting time (`git log --oneline` since the four amendment docs shows docs-only): the withdrawal + replacement policy must be on the OSF record BEFORE the replacement executes.
3. Confirm the four supporting docs are committed and (ideally) pushed to origin, so the record URLs resolve: `m3_nan_conditioning_scientific_review.md`, `m3_region1_occlusion_hinge_check.md`, `m3_panel_occlusion_policy_decision.md`, `m3_region1_nan_geometry_verdict.md`.
4. After OSF posts, copy the new file URL + OSF timestamp into `.planning/osf_deviations.md` under a new dated entry, and add a superseded-by pointer to the top of the project-side copy of the prior amendment (tcujq body).

--- PASTE INTO OSF FROM HERE ---

**Amendment-update to pre-registration osf.io/pvb5j (updating osf.io/az52u file tcujq): AFR native-plink LD panel — withdrawal of the NaN→0 conditioning policy and pre-registration of overlapping-deletion occlusion exclude-in-lockstep**

**Date:** 2026-07-10

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of amendment-update:** This update withdraws the off-diagonal NaN→0 conditioning policy pre-registered on 2026-07-04 for the African-ancestry (AFR) native-plink LD panel (osf.io/az52u, file tcujq), and pre-registers the replacement treatment. In-perimeter aggregate diagnostics run after that amendment posted established that the panel's pairwise-NaN entries are not benign pairwise-undefined degeneracies but a structured variant-representation artifact: an overlapping deletion whose reference-allele interval physically spans a neighboring variant's position makes that neighbor uncallable on the deletion haplotype, so the pairwise correlation is structurally undefined, not merely 0/0 by small-sample coincidence. Setting such an entry to 0 asserts statistical independence between two physically co-located, high-linkage-disequilibrium variants — a directionally wrong value placed exactly where fine-mapping resolution is load-bearing. The replacement is to exclude the occluded variant in lockstep from both the LD panel and the harmonized summary statistics, with a mandatory auditable provenance manifest — never to fabricate a correlation value.

**Evidence establishing the mechanism (aggregate / coordinate egress only, no genotypes):**

- Mechanism, region 1, resolved 6 of 6 NaN pairs on hard coordinates. The 12 NaN cells (6 symmetric pairs across 11 index-adjacent variants) are: 5 pairs where a deletion's reference-allele interval demonstrably covers the partner variant's base-pair position (ref_span_overlap), and 1 pair resolved as a second-order consequence of the same three-record locus (a SNP already occluded by an upstream deletion). Zero pairs are same-position multiallelic records — so allele-merge normalization (bcftools norm -m +) resolves none of them. Region 1 alone contains 7 distinct overlapping deletions (60/29/7/31/31/17/29 bp).
- Arithmetic refuting the benign interpretation. At the reported cohort dimensions (N ≈ 73000; MAF 0.005–0.02; per-variant missingness ≤ 0.05), the probability that a variant is monomorphic on the pairwise-complete subset by independent chance is ~10⁻⁹⁴⁷ to 10⁻³⁷²⁹. The NaN therefore cannot be random pairwise degeneracy; it requires the near-perfectly correlated missingness that co-located overlapping-deletion occlusion produces.
- Join-impact confirmation (the treatment-deciding fact). A read-only lift-over + summary-statistics scan of the region-1 occlusion locus established that the panel↔sumstats join is position-based ((CHR,POS)), and that while the occluding deletion is absent from the GWAS, the occluded SNP is present in the harmonized sumstats (region-1 example: rs182965575, MAF ≈ 0.014, present in 7 of 9 AFR traits with genuine effect estimates). A variant that is testable in the GWAS but uncallable in the LD reference is exactly the asymmetry that makes both NaN→0 and panel-only exclusion unsafe.

**What is withdrawn:**

The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries (prior amendment tcujq item (a) isolated-off-diagonal-pair branch and item (b) the per-region zeroing ceiling), together with its BRANCH_AFR_COND_CLEAN / BRANCH_AFR_COND_APPLIED / BRANCH_AFR_COND_DEFERRED outcome branches, is withdrawn. Rationale: for occlusion-undefined entries, 0 is a fabricated correlation asserting independence between high-LD co-located variants; it can split one true fine-mapping signal into two or move posterior-inclusion mass onto the wrong variant, and PSD projection then propagates the fabricated value across the submatrix.

**New analytical commitments — overlapping-deletion occlusion handling (replacement):**

(a) Occlusion detection (coordinate-only, egress-safe). At panel build, for every region, a variant record is flagged as an occluder when its reference-allele interval [POS, POS + len(REF) − 1] covers the position of a neighboring variant (the occluded variant). This is a pure .bim-coordinate operation — no genotypes — applied uniformly across all 276 regions rather than as a per-region patch.

(b) Exclude-in-lockstep. An occluded variant whose pairwise LD is structurally undefined is excluded from the LD panel and, in lockstep, from the harmonized summary statistics at the harmonization step, so the position-based panel↔sumstats join carries no variant present on one side and absent on the other. Panel-only exclusion (which would orphan a sumstats-present variant) and correlation fabrication (NaN→0) are both prohibited. An occluded variant's LD is genuinely undefined, so it cannot be validly fine-mapped at that locus regardless; lockstep exclusion is the honest realization of that fact.

(c) Mandatory provenance manifest (load-bearing, not optional). Every excluded variant is recorded in a per-variant manifest: variant ID and position (both genome builds), the occluding deletion and its reference span, the locus, the traits in which the variant was present in the sumstats, and the reason (reference-occlusion → undefined LD). A lockstep exclusion without a manifest entry is prohibited — the manifest is what keeps every dropped variant auditable and recoverable, and prevents the silent-drop failure mode the withdrawn NaN→0 policy was itself meant to avoid.

(d) Anomaly gate (per region). If the count of occlusion-excluded variants in a region exceeds 0.05 percent of the region's variant count (n_excluded ≤ 0.0005 × n_var; the same fractional gate as the withdrawn ceiling, re-purposed to exclusions), the region is treated as a substrate anomaly: it is NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation. A large excluded fraction indicates an LD-construction or variant-representation problem beyond isolated occlusion.

(e) Genome-wide present-rate reporting. For the genome-wide scan, the per-ancestry fraction of occluded variants that are PRESENT vs ABSENT in the harmonized sumstats is reported. This quantifies how much real, testable signal the artifact removes (many-present → the artifact removes substantial fine-mappable signal in the affected ancestry; mostly-absent → the exclusion is largely matrix hygiene).

**What is retained unchanged from the prior amendment:**

- PSD regularization (prior item (c)): the fit-time region-submatrix regularization by eigenvalue-clip (λ_floor = 10⁻⁶, primary) with the ridge sweep (λ ∈ {0.001, 0.01, 0.1}, robustness companion) — the r3 psd_regularize_eigclip / psd_regularize_ridge implementations — is retained without change. It addresses ordinary finite-sample indefiniteness of the fit submatrix, a separate matter from occlusion; with occluded variants excluded rather than zeroed, PSD regularization no longer has fabricated zeros to propagate.
- The fully-NaN-row → drop rule (prior item (a) first branch): a variant row that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF / missingness QC. This converges with the new exclude policy and is retained.
- The raw-panel NaN-raise contract. The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract.

**Outcome branches (pre-registered, replacing the withdrawn BRANCH_AFR_COND_*):**

- BRANCH_AFR_OCC_NONE — the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified.
- BRANCH_AFR_OCC_EXCLUDED — the region contains ≥ 1 occluded variant under the anomaly gate; the occluded variant(s) are excluded in lockstep (panel + sumstats) with manifest entries, and fine-mapping proceeds on the reduced variant set; the manifest of excluded variants is reported with the result.
- BRANCH_AFR_OCC_DEFERRED — the region's occlusion-exclusion count exceeds the anomaly gate; the region is deferred, not auto-excluded, and disclosed as a deviation with its occlusion count.

All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list.

**What is not changing (program-level):**

- Pre-registration discipline: the occlusion criterion, the lockstep-exclusion rule, the manifest requirement, the anomaly gate, and the three outcome branches are fixed before any occlusion-handling code fires; deviations are logged in .planning/osf_deviations.md and disclosed in the manuscript.
- All of Us controlled-tier data handling: only aggregate summaries and coordinate geometry egress the perimeter; no raw genotypes and no full LD matrices. No wet-lab validation; public-data-only for all non-AoU substrate.
- Multi-method triangulation and honest reporting of nulls; honest-original-research framing (this is pre-registered original methodology, not a fix, cleanup, or salvage).

**Expected timeline:** This amendment-update is posted before any occlusion exclude / span-filter / lockstep-drop code is written or run, and before any NaN→0-conditioned AFR output is banked. The pre-execute hard gate is repository commit 5fd58a5. Realized outcome branches, the per-region exclusion manifest, and the genome-wide present-rate are added as a follow-up OSF update at the panel-rebuild closeout.

--- PASTE ENDS HERE ---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm the OSF timestamp precedes any commit containing occlusion-exclude outputs or any newly-banked NaN→0-conditioned .npz/.rds. If precedence is violated, log a deviation in .planning/osf_deviations.md immediately.
2. Copy the new file URL + OSF timestamp into .planning/osf_deviations.md under a new dated entry.
3. Add a superseded-by pointer to the top of the project-side copy of the prior amendment body (the tcujq text): "The NaN→0 conditioning policy in this amendment is WITHDRAWN by <new file URL> (<timestamp>); see that update for the replacement (occlusion exclude-in-lockstep + manifest)."
4. Tag the pre-execute gate commit: `git tag AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`.
5. Update STATE.md / DECISIONS.md with the coverage decision so the panel-rebuild plan has a hard-gate target.
6. If any commitment changes between posting and closeout: pause at the next wave boundary, log the deviation, and if an outcome-branch rule changes, post a subsequent amendment-update citing this record URL.

**Rollback:** Do not delete this file. OSF amendments are append-only; this file itself supersedes tcujq's NaN→0 policy via the pointer in step 3, not by deletion.
