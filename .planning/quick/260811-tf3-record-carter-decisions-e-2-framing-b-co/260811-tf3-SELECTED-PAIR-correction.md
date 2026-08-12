# E-2 SELECTED PAIR — framing B (CORRECTION), paste-ready

**What this is.** The **selected pair** for E-2 under
`DEC-2026-08-11-e2-framing-correction`: the manuscript paragraph
`ms-correction` and the OSF record body `osf-correction`, extracted **verbatim**
from the `260811-oku` drafts. Carter chose framing **B — CORRECTION** on
2026-08-11, delegating to the standing recommendation on the oku decision
surface.

**⛔ This file discharges nothing by existing.** The framing choice — that is
obligation (3) — is already **DISCHARGED**, and it discharged in
`.planning/DECISIONS.md`, not here.
Obligations (1) and (2) are **UNDISCHARGED** and are Carter's external actions.
**No agent posts to OSF, edits a manuscript file, or edits the body of a posted
amendment.**

## How this file's fidelity is established

The two bodies below are **byte-identical** to their oku source blocks. That is
verified mechanically by `./260811-tf3-check.sh --only pair` (clause **SP-02**),
which re-extracts both blocks from the read-only oku drafts at run time with the
**same extractor** the oku harness uses and `cmp`s them. They were produced by
machine splice, never retyped.

**Why byte-identity rather than a re-run of the oku harness.** The oku harness
is *structurally unable* to run against this file: its `group_ms` and `group_osf`
read hard-coded paths, and every clause requires **both** framings
(`ms-limitation` **and** `ms-correction`) to be present exactly once. This file
deliberately carries only the correction halves, so pointing the oku harness at
it would fail `MS-01`/`OSF-01` for a reason that has nothing to do with
fidelity — and bending that harness to accept a half-file would weaken a gate
that is currently green. So the evidence is **inherited by identity** instead:

1. `./260811-oku-check-drafts.sh` was re-run during this task and exited **0**
   (**29 PASS / 0 FAIL**, observed — not copied from a plan).
2. These bodies are byte-identical to the blocks that harness graded.
3. Therefore every clause it asserts about `ms-correction` and `osf-correction`
   holds of the text below **by identity**, not by re-assertion.

⚠ What this does **not** inherit: the oku harness's *file-level* clauses
(`MS-10`, `MS-11`, `OSF-12`, `OSF-13` and siblings) are assertions about the oku
**draft files**, not about the blocks. This file carries its own `SP-04`..`SP-08`
clauses for the parts it must state itself.

## ⚠ PRE-PLACEMENT CHECK — do this first. It is Carter's.

The target journal's editorial policy is the one input to this decision that is
not in this repository, so it could not be settled when the framing was chosen.
Before the paragraph is placed, check it.

**If the journal's process reads a "correction" framing on a manuscript *in
submission* as a formal post-publication correction notice**, then keep the
**CONTENT below** and use framing **A's PLACEMENT** — the Limitations section
rather than a Methods correction note.

That is a **placement** change and nothing more. It does not reopen the framing,
it changes no number, and it changes no sentence of either body below.

---

## §1 — the manuscript paragraph (`ms-correction`)

**Destination.** The Track A (`id-vs-ref-LD`) manuscript, as a **Methods
correction-and-disclosure note**, with a pointer to it from Limitations — or, if
the pre-placement check above fires, in the Limitations section instead.

**Discharge condition.** This is **obligation (1)**. It discharges when this
paragraph is placed in the Track A manuscript. That placement is **Carter's
external action**; no agent performs it.

<!-- PASTE-BEGIN: ms-correction -->
We report a correction to the methods record. The join binding each region
variant catalog to its reference panel variant frame matched on coordinates alone
and ignored the alleles, so a variant whose reference and alternate alleles are
transposed between the two frames was bound without its association statistic
being reoriented. Among bindable variants (denominator exact + flipped, not the
whole catalog) the transposed share is 0.06% at CXADR_F2RL1_6p21, 0.07% at
MC4R_18q21 and 2.74% at SH2B3_12q24, whose md5-pinned anchor tiles are 0.00%
while its third tile reaches 20.33%, rising to 18.41% at APOL1_22q12 and 23.80%
at FTO_16q12; corpus-wide, 195 of 206 measured regions are affected (median
17.82%, maximum 38.68%). Reported effect sizes and standard errors are unchanged,
so no published direction of effect moves; posterior inclusion probabilities and
credible sets regenerated under an allele-aware join are, however, not comparable
to those produced before it. Every panel measured here is an identity-LD stub
(use_identity set, no correlation matrix, ancestry directories byte-identical),
so the rates quantify variant bookkeeping rather than a real-LD exposure.
<!-- PASTE-END: ms-correction -->

---

## §2 — the OSF record entry (`osf-correction`)

**Destination.** A **new supplementary file** on `osf.io/az52u`. ⛔ **Never** a
new version of `trsx5` or `tcujq`: OSF amendment bodies are **append-only**, and
the `tcujq` → `trsx5` precedent is the pattern to follow — a separate new file,
not a new version of what it superseded.

**Discharge condition.** This is **obligation (2)**. It discharges when the body
is posted **and** its resulting URL + timestamp are recorded in
`.planning/osf_deviations.md` — not at posting alone. Both steps are **Carter's
external actions**; no agent performs either.

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

---

## §3 — before pasting

The authoritative checklist is the **Pre-Paste Reference** in
`.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-osf-entry-drafts.md`.
Use it there rather than a copy here — a second copy is a second source of truth
waiting to drift. The items that need a human decision or a fresh measurement:

1. Fill the `**Date:**` line in the body before posting.
2. Fill the commit gate: baseline `7d575a5` → the HEAD of `m3-W2-aou-deltas` at
   posting time.
3. Confirm no E-2 **code** change has landed since that baseline
   (`git log --oneline 7d575a5..HEAD -- src/`). The disposition is option A, so
   the code is unchanged and the diff for this item must remain docs-only.
4. Confirm the manuscript half placed is `ms-correction` — the matching half of
   this pair — so the two records agree.
5. Post as a **new supplementary file** on `osf.io/az52u`.

⚠ **Scope boundary.** This entry does **not** discharge the separate outstanding
Check-2 amendment-update obligation. It stays separate; do not fold the two into
one posting.

## §4 — status

| Obligation | Status |
|---|---|
| **(3)** LIMITATION vs CORRECTION | ✅ **DISCHARGED** — `DEC-2026-08-11-e2-framing-correction` |
| **(1)** manuscript paragraph | ⛔ **UNDISCHARGED** — discharges at Carter's placement |
| **(2)** OSF record entry | ⛔ **UNDISCHARGED** — discharges at Carter's posting **and** the URL + timestamp record |

⛔ **No agent posts to OSF, edits a manuscript file, or edits the body of a
posted amendment.** Obligations (1) and (2) discharge only by Carter's own
external actions, and this file existing changes neither of them.

**Two standing number rules, which apply to anything quoted out of the bodies
above:**

- ⛔ **Never quote the pooled 5.29% alone.** It is **dragged** down by the two
  clean large regions; name 18.41% (`APOL1_22q12`) and 23.80% (`FTO_16q12`) in
  the same breath. Both bodies above already do this correctly.
- ⛔ **Never cite these as the real-LD exposure.** Every panel measured is an
  identity-LD stub, so they are catalog↔panel-frame transposition rates for
  variant bookkeeping.

**⚠ Posting makes a currently-internal commitment public.** The `osf-correction`
body closes by committing to an allele-aware join, a real-panel re-measurement,
and affected African-ancestry results regenerated and re-reported with a
before-and-after comparison — posted as a further update whether or not the
reported conclusions change. That is an internal **E-4** obligation today. On
posting it must be registered as a tracked obligation of the E-4 work.

**Not selected.** The `ms-limitation` and `osf-limitation` texts remain in the
oku directory as the record of what was considered. They are **not** to be
posted or placed.
