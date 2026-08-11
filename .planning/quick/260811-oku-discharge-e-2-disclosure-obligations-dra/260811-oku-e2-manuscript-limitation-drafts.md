# E-2 manuscript paragraph — both framings (DRAFT)

**What this is.** The manuscript-side half of obligation (1) of
`DEC-2026-08-07-e2-orientation-disposition`: a paragraph carrying the *real*
per-region E-2 numbers, naming `APOL1_22q12` (18.41%) and `FTO_16q12` (23.80%)
explicitly rather than quoting only the flattering pooled figure.

**Status: DRAFT. Obligation (1) is not discharged by this file.** It discharges
when Carter selects a framing and places the selected paragraph in the
manuscript. Nothing here has been placed, posted or submitted.

**Target.** The Track A manuscript (project nickname **id-vs-ref-LD**), which is
in submission. Two framings are supplied because the framing question is itself
an open obligation — obligation (3) — and is Carter's to answer:

| Framing | Where the paragraph goes | Matched OSF entry |
|---|---|---|
| **A — LIMITATION** | the Limitations section, as a stated bounded property of the analysis | `osf-limitation` in `260811-oku-e2-osf-entry-drafts.md` |
| **B — CORRECTION** | a Methods correction-and-disclosure note (with a pointer from Limitations) | `osf-correction` in `260811-oku-e2-osf-entry-drafts.md` |

Choosing a framing selects a complete matched pair: one manuscript paragraph and
one OSF entry. The comparison that supports the choice is in
`260811-oku-e2-framing-decision-surface.md`.

**The two paragraphs differ in posture, not in facts.** Both carry the same
locked numbers, the same denominator and the same bounding caveat.

---

## Framing A — LIMITATION

<!-- PASTE-BEGIN: ms-limitation -->
One bookkeeping property of our reference-panel construction should be stated
explicitly. At each region, colocalization binds a region variant catalog to a
reference panel variant frame at shared coordinates; among the bindable variants
(denominator exact + flipped, not the whole catalog, since ambiguous, palindromic
and unmatched rows are dropped first) a fraction are bound with transposed
reference and alternate alleles. Across the five regions our colocalization
results depend on, that fraction is 0.06% at CXADR_F2RL1_6p21, 0.07% at
MC4R_18q21 and 2.74% at SH2B3_12q24, whose md5-pinned anchor tiles are 0.00%
while its third tile reaches 20.33%; it rises to 18.41% at APOL1_22q12 and 23.80%
at FTO_16q12. Across the wider curated corpus, 195 of the 206 measured regions
contain at least one such pair (per-region median 17.82%, maximum 38.68%). Every
panel measured here is an identity-LD stub (use_identity set, no correlation
matrix, ancestry directories byte-identical), so these are catalog-to-panel-frame
transposition rates for variant bookkeeping rather than a real-LD exposure. They
bound the population in which an orientation error can occur; they are not a
count of realised errors.
<!-- PASTE-END: ms-limitation -->

## Framing B — CORRECTION

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

## Author notes — do NOT paste

**Provenance of every number above.** Measured 2026-08-07 by
`.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-measure.R`, which calls
the **shipped** `ld_allele_join_indices()` from
`src/snakemake/scripts/ld_allele_join.R` (never a reimplementation) over the
**207** real region variant catalogs in
`data/processed/region_analysis/ld_reference/variants/`, against the `variants`
frames of the sibling ancestry panels. Per-region output:
`e2-exposure-real-corpus.tsv` (618 rows = 206 regions x 3 ancestry arms);
Track A roll-up: `e2-exposure-track-a-regions.tsv`. Read-only, $0, no perimeter
contact. Re-derived from the TSVs during this task rather than retyped from prose.

**The full Track A table, including the pooled figure.**

| Track A region | exact | flipped | ratio |
|---|---|---|---|
| `CXADR_F2RL1_6p21` (5 tiles) | 28,415 | 18 | 0.06% |
| `MC4R_18q21` (2 tiles) | 14,141 | 10 | 0.07% |
| `SH2B3_12q24` (3 tiles) | 11,826 | 333 | 2.74% |
| — `__tile1` / `__tile2` (md5-pinned anchor) | 10,521 | 0 | 0.00% |
| — `__tile3` | 1,305 | 333 | 20.33% |
| `APOL1_22q12` (2 tiles) | 4,910 | 1,108 | 18.41% |
| `FTO_16q12` (3 cells) | 7,188 | 2,245 | 23.80% |
| **pooled over the Track A set** | 66,480 | 3,714 | **5.29%** |

The pooled **5.29%** is deliberately absent from both paste blocks. It is
**dragged down** by the two clean large regions (`CXADR_F2RL1_6p21`,
`MC4R_18q21`) and hides that two regions sit near 20%. A fit is per-region, so
the per-region figures are the honest unit. If a reviewer or editor asks for a
single number, quote it only together with the per-region set and this sentence.

**The mechanism, in one honest sentence.** The pre-`o7o` join matched on
`CHR:POS` with REF/ALT ignored, so a transposed pair entered LD with an unflipped
z; the `o7o` fix makes the join allele-aware — it **flips z rather than
dropping** — and drops palindromic sites, a strand-inverted palindrome being a
silently sign-wrong exact match and the only undetectable class.

**Consequences, stated exactly.** Reported **BETA** and SE do not move, so no
published direction of effect changes. PIPs and credible sets regenerated after
the allele-aware join are **not comparable** to ones produced before it. The
measured rate is the population in which an orientation error *can* occur, not a
count of realised sign errors: it does not by itself demonstrate that any
published `PP.H4` is wrong, and equally it means "we checked and it is
immaterial" is **not** a defensible statement for `APOL1_22q12` or `FTO_16q12`.

**⚠ A correction to the internal record, made here for the first time.** The
figure **46/182 = 25.3%**, quoted in earlier internal records, was a **synthetic
acceptance fixture**, not a measurement of anything real. The per-pair receipts
it was said to come from cannot exist yet: the shipped counter path is AFR-gated,
AFR has zero QTL-coloc jobs (**E-4**), and the AoU panel is 0/276. A separate
interim report gave `SH2B3_12q24__tile3` as "0.20%" when it is **20.33%** (a
ratio of 0.2033 misread as a percentage — a 100x error in the reassuring
direction). Neither figure was ever externally reported; both are corrected here
so that no draft inherits them.

**What is fixed and what is deliberately not.** `o7o` made the
GWAS-sumstats-to-panel join allele-aware. **E-2 — the QTL-beta to panel-ALT
orientation — is deliberately left as-is under option A** and is what these
paragraphs disclose. Do not let either paragraph blur the two into "the allele
problem is fixed".

**E-2/E-4 coupling.** The code-side correction (option B) becomes right only
bundled with **E-4**, after a real (non-identity) panel exists, with a real-LD
re-measurement, a before/after comparison and a further OSF disclosure. Today it
is inert: `build_qtl_coloc_manifest.py::_ancestry_for_region` returns `"EUR"`
unconditionally, so zero AFR QTL-coloc jobs exist to exercise it, it would move
Track A numbers mid-submission, and its only validation substrate is the
identity-LD stub tree.

**Acceptance.** `./260811-oku-check-drafts.sh --only ms` must exit 0 against this
file. The clause set and its negative controls are documented at the top of that
script.
