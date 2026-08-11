# E-2 OSF record entry — both framings (DRAFT, paste-ready)

**What this is.** The OSF-side half of obligation (2) of
`DEC-2026-08-07-e2-orientation-disposition`: a record entry disclosing the
measured QTL-beta to panel-ALT variant-orientation exposure in the AFR LD-panel
arm, consistent with the standing "state it, do not let a reader find it by
diffing" discipline.

**Status: DRAFT. Obligation (2) is not discharged by this file.** It discharges
only when **Carter** posts the selected body to OSF and records the resulting
URL and timestamp in `.planning/osf_deviations.md`. No agent posts to OSF.
Nothing here has been posted.

Format follows the precedent of
`.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`:
Pre-Paste Reference (do not paste), the paste body, Post-Paste Reference (do not
paste). Two bodies are supplied, one per framing; they are matched to the two
manuscript paragraphs in `260811-oku-e2-manuscript-limitation-drafts.md`
(`osf-limitation` pairs with `ms-limitation`, `osf-correction` with
`ms-correction`). The framing choice is obligation (3) and is Carter's; see
`260811-oku-e2-framing-decision-surface.md`.

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | `osf.io/az52u` — post as a **new supplementary file** on the existing amendment record. OSF amendment bodies are **append-only**: never edit or re-post the body of `trsx5` or `tcujq`. The `tcujq` -> `trsx5` precedent is the pattern — `trsx5` was confirmed a separate new file, not a new version of what it superseded. |
| Original pre-registration | `osf.io/pvb5j` (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| Entry kind (framing A) | Disclosure entry. Discloses a measured bookkeeping property of the analysis pipeline; withdraws nothing and corrects no pre-registered commitment. |
| Entry kind (framing B) | Methods correction-and-disclosure entry. Corrects the methods record for the catalog-to-panel allele join and commits to what follows once a real panel exists. |
| What is disclosed | The measured share of bindable variants bound with transposed REF/ALT between each region variant catalog and its panel `variants` frame, per Track A region and across the curated corpus; the correction of two internal-record figures; the identity-LD-stub caveat that bounds all of it. |
| What is NOT withdrawn | Nothing. No pre-registered number moves, no pre-registered commitment is withdrawn, and no prior amendment is superseded by this entry. |
| Substrate | 207 region variant catalogs under `data/processed/region_analysis/ld_reference/variants/` and the `variants` frames of the sibling ancestry panels on the NC State tree. Identity-LD stubs (`R` is `NULL`). Aggregate variant-bookkeeping counts only: no genotypes, no per-participant data, no LD values. Read-only, `$0`, zero perimeter contact. |
| Measurement code | `.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-measure.R`, calling the **shipped** `ld_allele_join_indices()` from `src/snakemake/scripts/ld_allele_join.R`. Outputs `e2-exposure-real-corpus.tsv` and `e2-exposure-track-a-regions.tsv`. |
| Pre-post commit gate | Baseline `7d575a5`. Fill with the HEAD of `m3-W2-aou-deltas` at posting time and confirm no E-2 code change has landed (option A leaves the code unchanged, so the diff since baseline must remain docs-only for this item). |
| Expected posting date | **Left for Carter.** Fill the `Date:` line in the body before posting. |
| ⚠ Scope boundary | **This entry does NOT discharge the outstanding Check-2 amendment-update obligation**, which is a separate surviving OSF obligation and stays separate. Do not fold the two together in one posting. |

**Pre-paste checklist (top to bottom before submitting the OSF form):**

1. Choose the framing (obligation 3) and paste **only** the matching body.
2. Fill the `Date:` line and the commit gate (`7d575a5` -> HEAD at posting).
3. Confirm no E-2 code change has landed since the baseline (`git log --oneline 7d575a5..HEAD -- src/`).
4. Confirm the matching manuscript paragraph is the one placed in the Track A manuscript, so the two records agree.
5. Post as a **new supplementary file** on `osf.io/az52u`. Do not create a new version of `trsx5` or `tcujq`.

---

## Framing A — LIMITATION (disclosure entry)

--- PASTE INTO OSF FROM HERE ---

<!-- PASTE-BEGIN: osf-limitation -->
**Disclosure entry for pre-registration osf.io/pvb5j (posted as a supplementary file on osf.io/az52u): measured variant-orientation exposure in the QTL-beta to panel-ALT arm of the LD reference panel**

**Date:** [fill at posting]

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of this entry.** This entry discloses a measured property of our own analysis pipeline. Colocalization and fine-mapping at each region bind a region variant catalog to a reference-panel variant frame at shared coordinates. Where the two frames represent the same coordinate with opposite reference and alternate alleles, the bound pair is transposed. We report here how often that occurs, per region and across the curated corpus, so that the exposure is on the record as a bounded and stated property of the analysis rather than something a reader would have to reconstruct. No pre-registered number has moved and nothing pre-registered is withdrawn.

**The measurement.** Measured with the shipped allele-join routine (`ld_allele_join_indices()`) run over the 207 real region variant catalogs against the `variants` frames of the sibling ancestry panels; 206 regions are measured per ancestry arm. The denominator is the bindable set, `flipped / (exact + flipped)` — that is, variants joinable at a shared coordinate — and not the whole catalog, because ambiguous, palindromic, mismatched and unusable rows are dropped before the ratio is formed. Across the five regions on which the reported colocalization results depend:

| Region | exact | flipped | transposed share |
|---|---|---|---|
| CXADR_F2RL1_6p21 (5 tiles) | 28,415 | 18 | 0.06% |
| MC4R_18q21 (2 tiles) | 14,141 | 10 | 0.07% |
| SH2B3_12q24 (3 tiles) | 11,826 | 333 | 2.74% |
| — tiles 1 and 2 (the md5-pinned anchor) | 10,521 | 0 | 0.00% |
| — tile 3 | 1,305 | 333 | 20.33% |
| APOL1_22q12 (2 tiles) | 4,910 | 1,108 | 18.41% |
| FTO_16q12 (3 cells) | 7,188 | 2,245 | 23.80% |
| pooled over the five regions | 66,480 | 3,714 | 5.29% |

The pooled 5.29% is reported here only alongside the per-region figures, because it is dragged down by the two clean large regions (CXADR_F2RL1_6p21 and MC4R_18q21) and on its own would hide that two regions sit near 20%. A fit is per-region, so the per-region figures are the honest unit. Two of the five regions are materially exposed: APOL1_22q12 at 18.41% and FTO_16q12 at 23.80%. A third, SH2B3_12q24, splits: its md5-pinned anchor tiles are 0.00% and its third tile is 20.33%. Across the wider corpus, 195 of the 206 measured regions contain at least one transposed pair, with a per-region median of 17.82% and a maximum of 38.68%.

**What the number means, and what it does not.** It is the population in which an orientation error can occur — not a count of realised sign errors. It does not by itself demonstrate that any published posterior probability of colocalization (PP.H4) is wrong. Equally, it does mean that "we checked and it is immaterial" is not a defensible statement for APOL1_22q12 or FTO_16q12, and we do not make it.

**Correction to the internal record.** An earlier internal record quoted this exposure as 46/182 = 25.3%. That figure was a synthetic acceptance fixture, not a measurement of anything real: the per-pair receipts it was said to come from cannot exist yet, because the shipped counter path is gated to the African-ancestry arm, that arm currently has no colocalization jobs at all (internal deferred item E-4), and the panel build is incomplete. A separate interim internal note gave SH2B3_12q24 tile 3 as 0.20% when it is 20.33% — a ratio misread as a percentage, a 100-fold error in the reassuring direction. Neither figure was ever externally reported; both are corrected here so that the public record carries only the measured values.

**The caveat that bounds all of the above.** Every panel measured is an identity-LD stub: `use_identity` is TRUE, the correlation matrix R is NULL, the build status is `variants_exceed_threshold`, and the EUR, AFR and TRANS directories are byte-identical (md5-verified on two regions). The allele question does not depend on R, so these counts are meaningful for the variant bookkeeping — but it is not verified that a real, non-identity panel carries the same `variants` frames. These are catalog-to-panel-frame transposition rates for variant bookkeeping, and must not be read as the real-LD exposure.

**Mechanism.** The join matched on CHR:POS with reference and alternate alleles ignored, so a transposed pair entered the reference panel with an unflipped association statistic; an allele-aware join instead flips the statistic rather than dropping the variant, and drops palindromic sites, since a strand-inverted palindrome is a silently sign-wrong exact match and the only undetectable class. Reported BETA and SE do not move, so no published direction of effect changes; posterior inclusion probabilities and credible sets regenerated under an allele-aware join are not comparable to ones produced before it.

**What does not change.** No pre-registered number has moved. Track A's frozen numbers (TRACK-A-FROZEN-NUMBERS) are untouched by this entry. The pre-registered occlusion-exclusion and PSD-regularization commitments are unaffected. Pre-registration discipline, All of Us controlled-tier handling (aggregate summaries and coordinate geometry egress only; no raw genotypes, no full LD matrices), and public-data-only handling for all non-controlled substrate all stand unchanged.

**What happens next.** The code-side orientation change is deliberately not made now. It is coupled to internal deferred item E-4: it cannot be exercised until African-ancestry colocalization jobs exist, and its only available validation substrate today is the identity-LD stub tree described above. It becomes appropriate bundled with that work, once a real non-identity panel exists, together with a real-LD re-measurement, a before-and-after comparison, and a further OSF update reporting both. Under this entry the exposure stands as a disclosed and bounded limitation of the present analysis; no re-analysis of already-reported results is undertaken on the strength of a stub-panel measurement.
<!-- PASTE-END: osf-limitation -->

--- PASTE ENDS HERE ---

---

## Framing B — CORRECTION (methods correction-and-disclosure entry)

--- PASTE INTO OSF FROM HERE ---

<!-- PASTE-BEGIN: osf-correction -->
**Methods correction and disclosure for pre-registration osf.io/pvb5j (posted as a supplementary file on osf.io/az52u): the catalog-to-panel variant-orientation join in the QTL-beta to panel-ALT arm**

**Date:** [fill at posting]

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of this entry.** This entry corrects the methods record. The join that binds each region variant catalog to its reference-panel variant frame matched on coordinates alone and ignored the alleles, so a variant represented with opposite reference and alternate alleles in the two frames was bound without its association statistic being reoriented. That is not a defensible convention, and we state it as a correction rather than as a caveat. This entry also reports how large the affected population is, per region and across the curated corpus, and states what follows from it. No pre-registered number has moved and nothing pre-registered is withdrawn.

**The measurement.** Measured with the shipped allele-join routine (`ld_allele_join_indices()`) run over the 207 real region variant catalogs against the `variants` frames of the sibling ancestry panels; 206 regions are measured per ancestry arm. The denominator is the bindable set, `flipped / (exact + flipped)` — that is, variants joinable at a shared coordinate — and not the whole catalog, because ambiguous, palindromic, mismatched and unusable rows are dropped before the ratio is formed. Across the five regions on which the reported colocalization results depend:

| Region | exact | flipped | transposed share |
|---|---|---|---|
| CXADR_F2RL1_6p21 (5 tiles) | 28,415 | 18 | 0.06% |
| MC4R_18q21 (2 tiles) | 14,141 | 10 | 0.07% |
| SH2B3_12q24 (3 tiles) | 11,826 | 333 | 2.74% |
| — tiles 1 and 2 (the md5-pinned anchor) | 10,521 | 0 | 0.00% |
| — tile 3 | 1,305 | 333 | 20.33% |
| APOL1_22q12 (2 tiles) | 4,910 | 1,108 | 18.41% |
| FTO_16q12 (3 cells) | 7,188 | 2,245 | 23.80% |
| pooled over the five regions | 66,480 | 3,714 | 5.29% |

The pooled 5.29% is reported here only alongside the per-region figures, because it is dragged down by the two clean large regions (CXADR_F2RL1_6p21 and MC4R_18q21) and on its own would hide that two regions sit near 20%. A fit is per-region, so the per-region figures are the honest unit. Two of the five regions are materially exposed: APOL1_22q12 at 18.41% and FTO_16q12 at 23.80%. A third, SH2B3_12q24, splits: its md5-pinned anchor tiles are 0.00% and its third tile is 20.33%. Across the wider corpus, 195 of the 206 measured regions contain at least one transposed pair, with a per-region median of 17.82% and a maximum of 38.68%.

**What the number means, and what it does not.** It is the population in which an orientation error can occur — not a count of realised sign errors. It does not by itself demonstrate that any published posterior probability of colocalization (PP.H4) is wrong. Equally, it does mean that "we checked and it is immaterial" is not a defensible statement for APOL1_22q12 or FTO_16q12, and we do not make it.

**Correction to the internal record.** An earlier internal record quoted this exposure as 46/182 = 25.3%. That figure was a synthetic acceptance fixture, not a measurement of anything real: the per-pair receipts it was said to come from cannot exist yet, because the shipped counter path is gated to the African-ancestry arm, that arm currently has no colocalization jobs at all (internal deferred item E-4), and the panel build is incomplete. A separate interim internal note gave SH2B3_12q24 tile 3 as 0.20% when it is 20.33% — a ratio misread as a percentage, a 100-fold error in the reassuring direction. Neither figure was ever externally reported; both are corrected here so that the public record carries only the measured values.

**The caveat that bounds all of the above.** Every panel measured is an identity-LD stub: `use_identity` is TRUE, the correlation matrix R is NULL, the build status is `variants_exceed_threshold`, and the EUR, AFR and TRANS directories are byte-identical (md5-verified on two regions). The allele question does not depend on R, so these counts are meaningful for the variant bookkeeping — but it is not verified that a real, non-identity panel carries the same `variants` frames. These are catalog-to-panel-frame transposition rates for variant bookkeeping, and must not be read as the real-LD exposure.

**Mechanism.** The join matched on CHR:POS with reference and alternate alleles ignored, so a transposed pair entered the reference panel with an unflipped association statistic; an allele-aware join instead flips the statistic rather than dropping the variant, and drops palindromic sites, since a strand-inverted palindrome is a silently sign-wrong exact match and the only undetectable class. Reported BETA and SE do not move, so no published direction of effect changes; posterior inclusion probabilities and credible sets regenerated under an allele-aware join are not comparable to ones produced before it.

**What does not change.** No pre-registered number has moved. Track A's frozen numbers (TRACK-A-FROZEN-NUMBERS) are untouched by this entry. The pre-registered occlusion-exclusion and PSD-regularization commitments are unaffected. Pre-registration discipline, All of Us controlled-tier handling (aggregate summaries and coordinate geometry egress only; no raw genotypes, no full LD matrices), and public-data-only handling for all non-controlled substrate all stand unchanged.

**What happens next, and what we commit to.** The code-side correction is coupled to internal deferred item E-4: it cannot be exercised today, because the African-ancestry arm has no colocalization jobs, and its only available validation substrate is the identity-LD stub tree described above. Making it against stubs would be less defensible than the defect it corrects. We therefore commit to the following, bundled with that work and once a real non-identity panel exists: the join is made allele-aware; the exposure is re-measured on the real panel; the affected African-ancestry results are regenerated and re-reported with a before-and-after comparison; and both the re-measurement and the comparison are posted as a further update to this record, whether or not the reported conclusions change.
<!-- PASTE-END: osf-correction -->

--- PASTE ENDS HERE ---

---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm OSF created a **new supplementary file** on `az52u` and did **not** add a version to `trsx5` or `tcujq` (open both file pages; each should still show a single version at its original timestamp).
2. Copy the new file URL and the OSF timestamp into `.planning/osf_deviations.md` under a new dated entry. **Obligation (2) discharges at this step, not before.**
3. Record the framing choice in `.planning/DECISIONS.md` as the resolution of obligation (3), citing this entry's URL. **Obligation (3) discharges at this step.**
4. Confirm the matching manuscript paragraph (`ms-limitation` or `ms-correction`) is the one placed in the Track A manuscript. **Obligation (1) discharges at that placement.**
5. Update `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (E-2) and `HANDOFF.json` to show the obligations discharged, with the URL.
6. If framing B was posted, its commitment to regenerate and re-report the affected African-ancestry results becomes a tracked obligation of the E-4 work; register it there so it cannot be lost.

**Rollback:** none. OSF entries are **append-only**; if anything in this entry
later needs correcting, post a further update citing this entry's URL. Do not
delete or edit a posted body.
