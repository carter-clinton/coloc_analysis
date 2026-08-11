# E-2: LIMITATION or CORRECTION? — the decision surface

**What this is.** Obligation (3) of `DEC-2026-08-07-e2-orientation-disposition`
is an open question explicitly recorded as being above an executor's authority:
**is the measured E-2 exposure a LIMITATION or a CORRECTION?** This file exists
so that the question can be answered by reading two concrete, complete texts
rather than by deciding in the abstract.

**Status: DRAFT. Nothing here discharges anything.** The two framings are both
written out in full, in both deliverables. Choosing one selects a matched pair.

---

## The question, stated once

The catalog-to-panel allele join binds a region variant catalog to a reference
panel's `variants` frame at shared coordinates. Measured over the real corpus
with the shipped `ld_allele_join_indices()`, the share of **bindable** variants
bound with transposed REF/ALT is:

| Track A region | exact | flipped | share |
|---|---|---|---|
| `CXADR_F2RL1_6p21` | 28,415 | 18 | 0.06% |
| `MC4R_18q21` | 14,141 | 10 | 0.07% |
| `SH2B3_12q24` | 11,826 | 333 | 2.74% |
| — anchor tiles 1/2 (md5-pinned) | 10,521 | 0 | **0.00%** |
| — tile 3 | 1,305 | 333 | **20.33%** |
| `APOL1_22q12` | 4,910 | 1,108 | **18.41%** |
| `FTO_16q12` | 7,188 | 2,245 | **23.80%** |
| pooled over the Track A set | 66,480 | 3,714 | 5.29% |

Corpus-wide: **195 of 206** measured regions affected, per-region **median
17.82%**, **max 38.68%**. The pooled 5.29% is **dragged down** by the two clean
large regions and is never the honest unit on its own — a fit is per-region.

**So: two of five Track A coloc regions carry ~18-24% transposed variants, a
third has one exposed tile (20.33%) while its md5-pinned anchor is 0.00%, and two
are clean at ~0.06%. Is that a LIMITATION or a CORRECTION?**

---

## What each framing says, in one sentence

### Framing A — LIMITATION

> *"Here is a bounded, measured property of our reference-panel bookkeeping; we
> state it explicitly, and we do not claim it is immaterial."*
> Matched pair: `ms-limitation` (manuscript paragraph) + `osf-limitation` (OSF
> entry).

### Framing B — CORRECTION

> *"The join convention was wrong — it matched on coordinates and ignored the
> alleles — we say so, and we commit to what follows once a real panel exists."*
> Matched pair: `ms-correction` (manuscript paragraph) + `osf-correction` (OSF
> entry).

Choosing a framing selects a complete pair. The texts are in
`260811-oku-e2-manuscript-limitation-drafts.md` and
`260811-oku-e2-osf-entry-drafts.md`; both carry identical numbers, the same
denominator and the same identity-LD-stub caveat.

---

## Side by side

| | **A — LIMITATION** | **B — CORRECTION** |
|---|---|---|
| **What a reviewer likely concludes** | "They measured a bookkeeping exposure, disclosed it honestly, and bounded it. Two regions near 20% is uncomfortable; I may ask whether those two results should be reported at all." | "They found a wrong join convention in their own pipeline, said so unprompted, and committed to re-reporting. The magnitude is bounded by a stub caveat I can check." |
| **Risk of the reviewer going further** | Moderate: a reviewer who reads 18.41% and 23.80% may conclude *for* you that it is a correction, and ask why it was filed as a limitation. That is the worse version of this conversation, because you no longer control the framing. | Low on framing; higher on scope: a reviewer may ask why the affected results are being reported at all in the interim. That question has an answer (BETA/SE do not move; the exposure is a population, not a realised error) but it must be answered. |
| **What it obligates NOW** | Prominent disclosure and **no re-analysis**: the paragraph in Limitations, the entry on the OSF record, and no re-work of already-reported results. | The same disclosure, placed as a Methods correction note rather than a limitation, plus a public commitment to the re-report below. |
| **What it obligates ONCE A REAL PANEL EXISTS** | Nothing formally, though the E-4 bundle already plans a real-LD re-measurement and a further OSF update. | **Regenerating and re-reporting the affected AFR results**, with a before/after comparison, posted whether or not conclusions change. |
| **Effect on Track A's frozen numbers** | None. `TRACK-A-FROZEN-NUMBERS.md` is untouched; no number moves today. | None **today** — identical. The commitment is deferred to the E-4 bundle; the code is not changed under option A either way. |
| **Effect on the pre-registration** | None. No pre-registered number moves, nothing is withdrawn, no prior amendment is superseded. | None. Same. Both are additive supplementary entries on `az52u`. |
| **Risk if the OTHER framing turns out to have been right** | You disclosed a real methods defect as a property of the analysis. If a real panel confirms ~20% and someone else names it a correction later, the record shows you chose the softer word *after* measuring 18.41% and 23.80%. That is the expensive failure. | You called a defect by its name and it turned out to be smaller than feared. Cost: you over-corrected in public. That is cheap, and it is the failure mode this project has repeatedly chosen. |
| **Cost** | Lowest. One paragraph, one OSF file. | One paragraph, one OSF file, plus a tracked obligation carried into the E-4 work. |
| **Process note (verify before relying on it)** | Track A is **in submission**, not published. Neither framing triggers a post-publication correction notice; framing B is an amendment to a submitted methods description, not a *Correction* in the journal's formal sense. Confirm with the target journal's policy before assuming this. | Same. |

---

## The three facts that constrain the choice

**(a) The substrate is an identity-LD stub tree.** Every panel measured has
`use_identity = TRUE`, `R` NULL, `status = "variants_exceed_threshold"`, and the
`EUR/`, `AFR/` and `TRANS/` directories are byte-identical (md5-verified on two
regions). So the measured rate is a **catalog-to-panel-frame transposition rate
for variant bookkeeping**, not a real-LD exposure. This cuts both ways: a
CORRECTION framing risks asserting more than the substrate can currently support,
while a LIMITATION framing risks under-stating an exposure that a real panel may
confirm. **The split that resolves it:** the *join convention* is verifiable in
code and is substrate-independent — it did match on `CHR:POS` and ignore the
alleles; only the *magnitude* is stub-bound. A correction framing that corrects
the convention while carrying the stub caveat on the magnitude claims exactly as
much as is provable, and no more. Both drafted bodies carry that caveat verbatim.

**(b) The number is a population, not a count of realised errors.** It bounds
where an orientation error *can* occur. No published `PP.H4` has been shown
wrong. Equally, **"we checked and it is immaterial" is not defensible** for
`APOL1_22q12` (18.41%) or `FTO_16q12` (23.80%), and neither draft says it.

**(c) The E-4 coupling.** The code-side change (option B of the disposition, not
to be confused with framing B here) is **inert today**:
`build_qtl_coloc_manifest.py::_ancestry_for_region` returns `"EUR"`
unconditionally, so zero AFR QTL-coloc jobs exist to exercise it. A CORRECTION
framing that promises a code change is promising something that cannot be
exercised until **E-4** lands and a real panel exists. Both drafted bodies
therefore phrase the commitment as *bundled with that work*, not as imminent.

---

## What we are NOT proposing to disclose, and why

An interim internal report gave `SH2B3_12q24__tile3` as **"0.20%"** when it is
**20.33%** — a ratio of `0.2033` misread as a percentage, a **100x error in the
reassuring direction**, in the very claim the disposition was first proposed on.
That figure, and the earlier `46/182 = 25.3%` synthetic fixture, were **never
externally reported**. They are therefore internal-record corrections, already
made in `DECISIONS.md`, `deferred-items.md` and both drafted bodies — not
themselves OSF obligations.

**Stated explicitly so Carter can overrule it.** If you would rather the OSF
entry disclose the internal misstatement as such, both bodies already contain the
sentence; nothing needs rewriting, only a decision to keep it prominent.

It is also the strongest available argument for the standing rule that per-region
figures are quoted **with their provenance** rather than a single pooled number:
every one of this project's E-2 numbers that turned out to be wrong was a
summary figure quoted away from its source.

---

## Recommendation

**Recommended: framing B — CORRECTION.** Reasoning:

1. **A limitation is something the data cannot do; this is something the
   pipeline did wrongly.** Matching on coordinates while ignoring alleles is not
   a bounded property of the available substrate — it is an indefensible
   convention that we found in our own code. Filing it under Limitations
   describes it inaccurately, and inaccuracy in the *reassuring* direction is
   exactly the class of error this arc has already committed twice (the 100x
   tile-3 misread; the 46/182 fixture quoted as a measurement).
2. **The magnitude claim is bounded either way.** Both bodies carry the same
   identity-LD-stub caveat and the same "population, not realised errors"
   sentence, so B does not over-claim; it corrects the convention (provable) and
   bounds the magnitude (caveated). Constraint (a) is met by construction.
3. **B's extra obligation is one the E-4 bundle already carries.** The real-LD
   re-measurement, the before/after comparison and the further OSF update are
   already the stated conditions under which the code change becomes right. B
   puts them on the public record instead of in a planning file.
4. **The asymmetry favours B.** Over-correcting costs a paragraph. Under-calling
   a measured 18-24% exposure that a real panel later confirms costs the record
   showing you chose the softer word after measuring it.
5. **Standing project posture.** Rigor over speed, in any gray-area trade-off,
   choose the more reviewer-defensible option.

**What would flip this recommendation to A:**

- If a real (non-identity) panel measurement shows the catalog and panel frames
  agree at these coordinates (near-0% transposition), the affected population is
  effectively empty and the honest framing is a disclosed limitation of the stub
  era, not a correction.
- If the target journal's process makes a "correction" framing on a manuscript
  **in submission** procedurally costly or ambiguous (e.g. it is read as a
  post-publication correction notice), then keep the correction *content* and use
  A's placement. Verify this against the journal's policy — it is the one input
  to this decision that is not in this repository.
- If Carter judges that committing publicly to regenerate AFR results before
  E-4 has a schedule is a promise the project should not make yet.

**This is Carter's choice to make, not an executor's, and it is deliberately left open here.**
The two texts are complete and interchangeable; selecting one is a single
decision, not a drafting task.

---

## What discharges the obligations

| Obligation | Discharges when | Status |
|---|---|---|
| **(1) Manuscript limitation paragraph** | the selected paragraph (`ms-limitation` or `ms-correction`) is placed in the Track A manuscript | **UNDISCHARGED** |
| **(2) OSF record entry** | the selected body (`osf-limitation` or `osf-correction`) is posted as a new supplementary file on `osf.io/az52u` **and** its URL + timestamp are recorded in `.planning/osf_deviations.md` | **UNDISCHARGED** |
| **(3) LIMITATION vs CORRECTION** | the framing is chosen and recorded in `.planning/DECISIONS.md` | **UNDISCHARGED** |

**None of the three is discharged by this plan.** Drafting is not disclosing.
