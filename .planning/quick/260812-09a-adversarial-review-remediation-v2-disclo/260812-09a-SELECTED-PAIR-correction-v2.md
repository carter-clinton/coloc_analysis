# E-2 SELECTED PAIR **v2** — framing B (CORRECTION), paste-ready

**What this is.** The **v2 selected pair** for E-2 under
`DEC-2026-08-11-e2-framing-correction`: the manuscript paragraph
`ms-correction-v2` and the OSF record body `osf-correction-v2`. Carter chose
framing **B — CORRECTION** on 2026-08-11. This file supersedes the v1 pair.

**Why there is a v2.** The 2026-08-11/12 five-way adversarial review of
`7d575a5..42c060e` (Codex CLI v0.141.0 + four blind read-only investigators)
found that the v1 pair **misstated which join was defective**, **committed to
work that had already shipped**, **mis-scoped the re-report to an ancestry with
no results**, **dropped the manuscript paragraph's bounding sentences**, and
**equivocated tile units for locus units**. Those are corrected here. See
`## §5 — v1 → v2 delta` for the finding-by-finding map.

**v1 is history, not a competitor.** `260811-tf3-SELECTED-PAIR-correction.md`
and the `260811-oku` drafts are left **byte-untouched** as the record of what was
considered. ⛔ **Do not place or post the v1 texts.** v2 is the outgoing text.

**⛔ This file discharges nothing by existing.** The framing choice — obligation
**(3)** — is already **DISCHARGED**, and it discharged in `.planning/DECISIONS.md`,
not here. Obligations **(1)** and **(2)** are **UNDISCHARGED** and are Carter's
external actions. **No agent posts to OSF, edits a manuscript file, or edits the
body of a posted amendment.**

## How this file's fidelity is established

Every figure below is **re-derived at run time from the two measurement TSVs** by
`./260812-09a-check-v2-pair.sh`, not copied from v1 prose. The harness also
asserts each figure **adjacent to its own region label**, so a label swap goes
red; the v1 harness could not have caught one. Run:

```
./260812-09a-check-v2-pair.sh --self-test   # every control OBSERVED red first
./260812-09a-check-v2-pair.sh               # then the real grade
```

⚠ What the harness does **not** establish: that the journal will accept a
"correction" framing on a manuscript in submission. That is the pre-placement
check below, and it is Carter's.

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

## §1 — the manuscript paragraph (`ms-correction-v2`)

**Destination.** The Track A (`id-vs-ref-LD`) manuscript, as a **Methods
correction-and-disclosure note**, with a pointer to it from Limitations — or, if
the pre-placement check above fires, in the Limitations section instead.

**Discharge condition.** This is **obligation (1)**. It discharges when this
paragraph is placed in the Track A manuscript. That placement is **Carter's
external action**; no agent performs it.

<!-- PASTE-BEGIN: ms-correction-v2 -->
We correct and extend the methods record here; the analysis code is unchanged by this disclosure, and the correction is to the record and to the forward analysis plan rather than to any result reported in this manuscript.
The figures below were produced by the pipeline's own shipped allele-aware join, `ld_allele_join_indices()` in `src/snakemake/scripts/ld_allele_join.R`, run over the 207 real region variant catalogs against the variant frames of the sibling ancestry panels, with 206 regions measured per ancestry arm.
That join builds a four-key match on chromosome, position, reference allele and alternate allele; it tries the exact key and the reference-alternate-swapped key, drops palindromic sites, and removes duplicated four-keys from the match table; and it counts every swapped-key binding in its own `flipped` counter, which is the counter that produced every percentage quoted here.
The property we disclose is downstream of that measurement: the orientation the join computes is measured and reported but is deliberately not applied to the QTL effect estimate at the colocalization call site in `src/snakemake/scripts/run_qtl_coloc.R`, which is a recorded internal decision taken because applying it would move numbers in a manuscript under submission, and not an oversight.
A different and earlier join — the fine-mapping side's summary-statistics-to-panel match — did bind on chromosome and position only, without consulting the alleles; that join was made allele-aware for the African-ancestry arm alone, and it remains position-only on the European-ancestry arm today, because the switch that enables it is scoped by ancestry.
Among bindable variants (denominator exact + flipped, not the whole catalog), the transposed share per LOCUS is 0.06% at CXADR_F2RL1_6p21, 0.07% at MC4R_18q21, 2.74% at SH2B3_12q24, 18.41% at APOL1_22q12 and 23.80% at FTO_16q12.
SH2B3_12q24 splits: its two md5-pinned anchor tiles are 0.00% and its third tile is 20.33%.
Across the wider corpus the same measurement gives two pictures depending on the unit, and we state both: per measurement TILE-ROW, 195 of 206 tile-rows carry at least one transposed pair, with a median of 17.82% and a maximum of 38.68%; per LOCUS, collapsing each locus's tile rows into one, 49 of 51 loci are affected, with a median of 0.4234% and a maximum of 38.6824%.
This is the population in which an orientation error can occur, and not a count of realised errors; no posterior probability of colocalization is shown by it to be wrong.
Effect sizes and standard errors are unchanged, so no reported direction of effect moves; posterior inclusion probabilities and credible sets regenerated under an applied orientation would, however, not be comparable to those produced without it.
Every panel measured here is an identity-LD stub (`use_identity` set, no correlation matrix, ancestry directories byte-identical), so these rates quantify variant bookkeeping and must not be read as a real-LD exposure.
This disclosure is a measured property of our own pipeline, found by hypothesis-driven original research and reported by us; it is not a salvage of prior work.
The full measurement, its denominator, the corrections it makes to our internal record and the commitment that follows from it are recorded in the paired entry posted as a supplementary file on osf.io/az52u.
<!-- PASTE-END: ms-correction-v2 -->

---

## §2 — the OSF record entry (`osf-correction-v2`)

**Destination.** A **new supplementary file** on `osf.io/az52u`. ⛔ **Never** a
new version of `trsx5` or `tcujq`: OSF amendment bodies are **append-only**, and
the `tcujq` → `trsx5` precedent is the pattern to follow — a separate new file,
not a new version of what it superseded.

**Discharge condition.** This is **obligation (2)**. It discharges when the body
is posted **and** its resulting URL + timestamp are recorded in
`.planning/osf_deviations.md` — not at posting alone. Both steps are **Carter's
external actions**; no agent performs either.

<!-- PASTE-BEGIN: osf-correction-v2 -->
**Methods correction and disclosure for pre-registration osf.io/pvb5j (posted as a supplementary file on osf.io/az52u): measured variant-orientation exposure, and an orientation that is measured but not applied to the QTL beta**

**Date:** [fill at posting]

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of this entry.** This entry corrects and extends the methods record. It reports how large the population of orientation-transposable variants is, per locus and across the curated corpus; it states precisely which join produced those numbers and which property of the pipeline we are disclosing; and it states what we commit to doing about it. The analysis code is unchanged by this entry: the correction is to the record and to the forward analysis plan, not to any shipped result. No pre-registered number has moved and nothing pre-registered is withdrawn. This is a measured property of our own pipeline, found by hypothesis-driven original research and reported by us; it is not a salvage of prior work.

**The measurement, and which join produced it.** The figures below come from the pipeline's own shipped allele-aware join, `ld_allele_join_indices()` in `src/snakemake/scripts/ld_allele_join.R`, run over the 207 real region variant catalogs against the `variants` frames of the sibling ancestry panels; 206 regions are measured per ancestry arm. That join is a four-key matcher on chromosome, position, reference allele and alternate allele: it attempts the exact key and the reference-alternate-swapped key, drops palindromic sites (A/T, T/A, C/G, G/C), and removes duplicated four-keys from the match table so that no key can bind to more than one panel row. Every swapped-key binding increments its own `flipped` counter, and that counter is the source of every percentage in this entry. In other words, these numbers were produced by the correct join measuring the size of the exposed population — not by a defective join, and not by a coordinate-only match. The denominator is the bindable set, `flipped / (exact + flipped)`, and not the whole catalog, because ambiguous, palindromic, mismatched and unusable rows are dropped before the ratio is formed.

**Per-LOCUS exposure across the five regions on which the reported colocalization results depend.** The table below is in LOCUS units: each row collapses that locus's measurement tile rows into a single ratio.

| Region (LOCUS unit) | exact | flipped | transposed share |
|---|---|---|---|
| CXADR_F2RL1_6p21 (5 tiles) | 28,415 | 18 | 0.06% |
| MC4R_18q21 (2 tiles) | 14,141 | 10 | 0.07% |
| SH2B3_12q24 (3 tiles) | 11,826 | 333 | 2.74% |
| — tiles 1 and 2 (the md5-pinned anchor) | 10,521 | 0 | 0.00% |
| — tile 3 | 1,305 | 333 | 20.33% |
| APOL1_22q12 (2 tiles) | 4,910 | 1,108 | 18.41% |
| FTO_16q12 (3 tiles) | 7,188 | 2,245 | 23.80% |
| pooled over the five loci | 66,480 | 3,714 | 5.29% |

FTO_16q12's three measurement rows are `__tile1`, `__tile2` and one un-suffixed whole-region row; all three are measurement rows of the same locus, and the locus figure is their sum.

The pooled 5.29% is reported here only alongside the per-locus figures, because it is dragged down by the two clean large regions (CXADR_F2RL1_6p21 and MC4R_18q21) and on its own would hide that two loci sit near 20%. A fit is per locus, so the per-locus figures are the honest unit. Two of the five loci are materially exposed: APOL1_22q12 at 18.41% and FTO_16q12 at 23.80%. A third, SH2B3_12q24, splits: its md5-pinned anchor tiles are 0.00% and its third tile is 20.33%.

**Both measurement units, stated explicitly.** The corpus-wide figure depends on the unit, and quoting one unit without naming it is the error we are correcting here. Per measurement TILE-ROW: 195 of the 206 measured tile-rows contain at least one transposed pair, with a median of 17.82% and a maximum of 38.68%. Per LOCUS, collapsing each locus's `__tile` and `__sub` rows into one: 49 of 51 loci are affected, with a median of 0.4234% and a maximum of 38.6824%. The two units differ by roughly forty-fold at the median because a locus's clean tiles dilute its exposed ones, and the five-locus table above is in LOCUS units.

**What the number means, and what it does not.** It is the population in which an orientation error can occur — not a count of realised sign errors. It does not by itself demonstrate that any reported posterior probability of colocalization (PP.H4) is wrong. Equally, it does mean that "we checked and it is immaterial" is not a defensible statement for APOL1_22q12 or FTO_16q12, and we do not make it. Effect sizes and standard errors are unchanged by this entry, so no reported direction of effect moves; posterior inclusion probabilities and credible sets regenerated under an applied orientation would, however, not be comparable to those produced without it.

**The property we disclose, stated precisely.** Three joins must be distinguished, because conflating them is what made an earlier internal draft of this entry wrong. (i) The colocalization-side catalog-to-panel join, `ld_allele_join_indices()`, is allele-aware and has been since it shipped; it is the instrument that produced every number above. (ii) At the colocalization call site in `src/snakemake/scripts/run_qtl_coloc.R`, the orientation that join computes is measured and reported but is deliberately not applied to the QTL effect estimate. That is the property we disclose. It is a recorded internal decision, taken because the pre-existing convention sits on the legacy European-ancestry path and correcting it would move Track A numbers that are in submission — it is not an oversight, and it is not a defect nobody had noticed. (iii) A separate, earlier join on the fine-mapping side — summary statistics to panel — did bind on chromosome and position only, without consulting the alleles. That join was made allele-aware for the African-ancestry arm alone; the switch that enables it is scoped by ancestry, so on the European-ancestry arm the fine-mapping join is position-only today. We state that in the present tense deliberately, because describing it as fixed would be false of the arm that carries the reported results.

**Correction to the internal record.** An earlier internal record quoted this exposure as 46/182 = 25.3%. That figure was a synthetic acceptance fixture, not a measurement of anything real: the per-pair receipts it was said to come from cannot exist yet, because the shipped counter path is gated to the African-ancestry arm, that arm currently has no colocalization jobs at all (internal deferred item E-4), and the panel build is incomplete. A separate interim internal note gave SH2B3_12q24 tile 3 as 0.20% when it is 20.33% — a ratio misread as a percentage, a 100-fold error in the reassuring direction. Neither figure was ever externally reported; both are corrected here so that the public record carries only the measured values.

**The caveat that bounds all of the above.** Every panel measured is an identity-LD stub: `use_identity` is TRUE, the correlation matrix R is NULL, the build status is `variants_exceed_threshold`, and the EUR, AFR and TRANS directories are byte-identical (md5-verified on two regions). The allele question does not depend on R, so these counts are meaningful for the variant bookkeeping — but it is not verified that a real, non-identity panel carries the same `variants` frames. These are catalog-to-panel-frame transposition rates for variant bookkeeping, and must not be read as the real-LD exposure.

**Interaction with the posted occlusion amendment (osf.io/az52u, file trsx5, 2026-07-10).** That update premises a position-based panel-to-summary-statistics join, and commits to excluding an occluded variant in lockstep from the LD panel and from the harmonized summary statistics so that the join carries no variant present on one side and absent on the other. An allele-aware join is not neutral with respect to that premise, and we do not claim it is unaffected: dropping palindromic sites is a one-sided drop class that a position-based join does not have, and the lockstep-exclusion commitment as written does not cover it. We therefore record this as a premise update rather than as "unaffected". The magnitude is bounded and auditable rather than unknown: on the same measurement the shipped join counts 144,176 palindromic drops against 714,382 exact and 31,152 flipped bindings, which is 19.34% of the bindable set, and every one of those drops is recorded in the join's own `dropped_palindromic` counter, so the class is counted rather than silent. The lockstep commitment itself stands. What changes is that when the applied-orientation remedy below lands, palindromic drops must be carried through the same lockstep discipline and the same mandatory provenance manifest that items (b) and (c) of the posted update require for occlusion drops, so that the two sides remain variant-for-variant aligned.

**What does not change.** No pre-registered number has moved. Track A's frozen numbers (TRACK-A-FROZEN-NUMBERS) are untouched by this entry. The pre-registered PSD-regularization commitment is unaffected, and the pre-registered occlusion-exclusion commitment stands with the premise update recorded above. Pre-registration discipline, All of Us controlled-tier handling (aggregate summaries and coordinate geometry egress only; no raw genotypes, no full LD matrices), and public-data-only handling for all non-controlled substrate all stand unchanged.

**What happens next, and what we commit to.** The remedy is not to make the join allele-aware: it already is, and saying otherwise would misdescribe our own code. The remedy has three parts. First, apply the orientation the join already computes to the QTL effect estimate at the colocalization call site, so that a swapped-key binding carries a sign-corrected beta instead of an unreoriented one. Second, reconcile alleles across genome builds on the QTL side, because the QTL frame is GRCh38 while the panel and the region catalogs are GRCh37, so no position-only join is available on the QTL side at all and the reconciliation is a precondition of the first part rather than a refinement of it. Third, gate the change by ancestry if the Track A analysis must not move while it is under submission. Applying the orientation moves the posterior probability of colocalization for any pair containing a transposed variant, and that includes the European-ancestry results, because the African-ancestry arm has no colocalization jobs at all today — the manifest builder assigns European ancestry unconditionally (internal deferred item E-4). We therefore commit to re-measuring the exposure on a real, non-identity panel, and to re-reporting with a before-and-after comparison every affected ancestry's colocalization results that exist at the time the remedy is applied — explicitly including the European-ancestry results that exist today, and not only an African-ancestry arm that does not yet exist. This work is bundled with internal deferred item E-4 and is conditioned on a real non-identity panel existing; we set no schedule for it; and we will post the re-measurement and the comparison as a further update to this record whether or not the reported conclusions change.
<!-- PASTE-END: osf-correction-v2 -->

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
4. Confirm the manuscript half placed is `ms-correction-v2` — the matching half
   of **this** pair, not the v1 half — so the two records agree.
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

**A third standing rule, added by this v2:**

- ⛔ **Never quote a corpus figure without its unit.** 17.82% is the **tile-row**
  median; the **locus** median is 0.4234%. They differ by roughly forty-fold, and
  an unlabelled figure is the exact defect this v2 corrects.

**⚠ Posting makes a currently-internal commitment public.** The
`osf-correction-v2` body closes by committing to an applied orientation with a
build reconciliation, a real-panel re-measurement, and every affected ancestry's
results re-reported with a before-and-after comparison — posted as a further
update whether or not the reported conclusions change. That is an internal
**E-4** obligation today. On posting it must be registered as a tracked
obligation of the E-4 work.

**Not selected.** The `ms-limitation` and `osf-limitation` texts remain in the
oku directory as the record of what was considered. They are not to be posted or
placed. The **v1** correction pair likewise remains in the `260811-tf3`
directory as history, byte-untouched, and is not to be posted or placed.

---

## §5 — v1 → v2 delta

| Finding | v1 said | v2 says | Evidence |
|---|---|---|---|
| **A-BLOCKER-1** | the catalog-to-panel join "matched on coordinates alone and ignored the alleles" | the numbers come from the **shipped allele-aware four-key matcher's own `flipped` counter**; the disclosed property is the **measured-but-not-applied orientation** at the coloc call site; the coordinate-only description is confined to the **fine-map-side** join, present tense for the European arm | `src/snakemake/scripts/ld_allele_join.R:205` (`k4_pan`), `:211-219` (dup-4-key removal), `:221-222` (`k4_exact`/`k4_swap`), `:227-230` (`m_exact`/`m_swap`), `:232-234` + `:239` (palindromes dropped), `:241` (`orient`), `:257-270` (counters); sole call site `run_qtl_coloc.R:471`; the disclosed defect at `run_qtl_coloc.R:478-479`; the fine-map twin at `src/legacy/region_analysis/scripts/run_susie_rss.R:220,:274,:312,:331-332` gated by `config/pipeline.yaml` `ld_read_path` = `{'enabled': True, 'ancestries': ['AFR'], 'allele_aware': True, 'coloc': True}` |
| **A-BLOCKER-2** | commits to "the join is made allele-aware" (already shipped) and to regenerating "the affected African-ancestry results" (no such results exist) | names the **real** three-part remedy — apply the measured orientation to the QTL beta; a GRCh38→GRCh37 allele reconciliation on the QTL side; an ancestry gate if Track A must not move — and scopes the re-report to **all affected ancestries that exist at remediation time, explicitly including EUR**; condition-bounded on E-4 + a real non-identity panel; no schedule | `deferred-items.md:228` fork table (option B: "PP.H4 moves for any pair with transposed variants, **including EUR**"; requires a GRCh38↔GRCh37 reconciliation + an ancestry gate); `src/python/build_qtl_coloc_manifest.py:250,:276` (`_ancestry_for_region` returns `"EUR"` unconditionally) |
| **A-BLOCKER-3** | ms paragraph opened "We report a correction" with no bounding and no code-unchanged statement | ms paragraph carries **all three** restored elements: population-not-realised-errors; **the analysis code is unchanged by this disclosure**, the correction being to the record and the forward analysis plan; and no posterior probability of colocalization is shown to be wrong | `DEC-2026-08-11-e2-framing-correction` (framing B is **not** disposition option B); `DEC-2026-08-07-e2-orientation-disposition` (option A: code unchanged) |
| **A-HIGH-1** | one corpus figure, the tile-row median, carrying a locus-unit word | **both** units, each labelled: per TILE-ROW 195 of 206, median 17.82%, max 38.68%; per LOCUS 49 of 51, median 0.4234%, max 38.6824%; the five-region table labelled LOCUS unit | re-derived from `e2-exposure-real-corpus.tsv` — see `## §6` |
| **A-MEDIUM (a)** | no measurement basis, no provenance pointer in the ms paragraph | ms paragraph names `ld_allele_join_indices()` over the 207 real region variant catalogs, and points at the paired `osf.io/az52u` entry | `e2-exposure-real-corpus.tsv` (618 rows = 206 tile-rows × 3 ancestry arms) |
| **A-MEDIUM (b)** | "published direction of effect" | "**reported** direction of effect" in both bodies | the manuscript is in submission, not published |
| **A-MEDIUM (c)** | asserted the posted occlusion commitment "unaffected" | **reasons** the interaction: the posted body premises a position-based join and lockstep exclusion; palindrome-dropping is a **new one-sided drop class** relative to that premise; recorded as a **premise update**, bounded by 144,176 palindromic drops = 19.34% of the bindable set, counted in `dropped_palindromic` and therefore auditable | `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md:47` (join is position-based `(CHR,POS)`) and `:57` (exclude-in-lockstep, "no variant present on one side and absent on the other"); palindrome magnitude re-derived from `e2-exposure-real-corpus.tsv` |
| **A-MEDIUM (d)** | no original-research framing sentence | both bodies carry one, **adapted** because this is a correction entry: a measured property of our own pipeline, found by hypothesis-driven original research; not a salvage of prior work | posted precedent `.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md:82` |
| **A-MEDIUM (e)** | `FTO_16q12 (3 cells)` | `FTO_16q12 (3 tiles)`, with a footnote stating that the three measurement rows are `__tile1`, `__tile2` and one un-suffixed whole-region row | `e2-exposure-track-a-regions.tsv` |
| **A-HARNESS** | v1 harness: token-presence only; file-scoped pooled guard; no word boundaries on (UN)DISCHARGED; `expect_red` hard-coded to the ms group (4 of 29 clauses ever observed red) | `260812-09a-check-v2-pair.sh`: figure-adjacent-to-its-own-label; **block-scoped** pooled guard; word-boundary (UN)DISCHARGED with a runtime dialect self-check; forbidden-bracket self-check; **`expect_red` coverage for all three clause groups** | see the harness header |

---

## §6 — author notes: how every figure was derived

⚠ These are the commands, not a transcription. Re-running them is the check.
`R` below is `.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-real-corpus.tsv`
and `A` is `.planning/phases/m3-aou-afr-ld-panel-build/e2-exposure-track-a-regions.tsv`.
Both are read-only inputs; nothing here contacts a perimeter and nothing costs money.

**The five-locus table and the pooled row** (LOCUS unit, from `A`):

```
awk -F'\t' 'NR>1{e[$1]+=$3; f[$1]+=$4} END{for(k in e){d=e[k]+f[k];
  printf "%s\texact=%d\tflipped=%d\tpct=%.4f\n", k, e[k], f[k], f[k]/d*100;
  te+=e[k]; tf+=f[k]} printf "POOLED\texact=%d\tflipped=%d\tpct=%.4f\n", te, tf, tf/(te+tf)*100}' "$A"
```

Measured: `CXADR_F2RL1_6p21` 28,415 / 18 / 0.0633% → **0.06%**; `MC4R_18q21`
14,141 / 10 / 0.0707% → **0.07%**; `SH2B3_12q24` 11,826 / 333 / 2.7387% →
**2.74%**; `APOL1_22q12` 4,910 / 1,108 / 18.4114% → **18.41%**; `FTO_16q12`
7,188 / 2,245 / 23.7994% → **23.80%**; pooled 66,480 / 3,714 / 5.2911% →
**5.29%**.

**The SH2B3 anchor-vs-tile-3 split** (from `A`): tiles 1 + 2 = 10,521 exact /
0 flipped = **0.00%**; tile 3 = 1,305 / 333 = 20.3297% → **20.33%**.

**Per TILE-ROW, European arm** (from `R`):

```
awk -F'\t' 'NR>1 && $1=="EUR"{n++; if($4>0) aff++; d=$3+$4; if(d>0) print $4/d*100}' "$R" \
  | sort -g | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2;
      printf "rows=%d median=%.4f max=%.4f\n", NR, m, a[NR]}'
```

Measured: 206 tile-rows, **195** with at least one transposed pair, median
17.8240% → **17.82%**, maximum 38.6824% → **38.68%**.

**Per LOCUS, European arm** (from `R`, collapsing the `__tile`/`__sub` suffix):

```
awk -F'\t' 'NR>1 && $1=="EUR"{r=$2; sub(/__tile[0-9]+$/,"",r); sub(/__sub[0-9]+$/,"",r);
  e[r]+=$3; f[r]+=$4} END{for(k in e) printf "%s\t%.4f\n", k, f[k]/(e[k]+f[k])*100}' "$R" \
  | sort -k2,2g | awk -F'\t' '{n++; if($2>0) aff++; a[n]=$2}
      END{m=(n%2)?a[(n+1)/2]:(a[n/2]+a[n/2+1])/2;
          printf "loci=%d affected=%d median=%.4f max=%.4f\n", n, aff, m, a[n]}'
```

Measured: **51** loci, **49** affected, median **0.4234%**, maximum
**38.6824%** (`RAD50_peak`). The two unaffected loci are `ANGPTL3_1p31_1` and
`BMI_Xq24`.

**Palindrome-drop magnitude, European arm** (from `R`, needed to bound the
occlusion-amendment premise update):

```
awk -F'\t' 'NR>1 && $1=="EUR"{e+=$3; f+=$4; p+=$6}
  END{printf "exact=%d flipped=%d dropped_palindromic=%d pal_pct=%.4f\n", e, f, p, p/(e+f)*100}' "$R"
```

Measured: exact **714,382**, flipped **31,152**, `dropped_palindromic`
**144,176** = **19.3386%** → **19.34%** of the bindable set.

**Agreement with the plan's `<interfaces>` block.** Every value above agrees with
the value planning obtained, to the digit, with one presentational note: the
tile-row median measures as 17.8240% and is quoted as 17.82%, and the tile-row /
locus maxima are the same number (38.6824%) because the maximal locus,
`RAD50_peak`, is a single-tile locus. **No discrepancy was found, so nothing was
adopted over the TSVs.**

**On block length.** The v1 `ms` clause capped the manuscript block at 120–200
words. The v2 content required by A-BLOCKER-1 (the mechanism triple), A-BLOCKER-3
(three restored bounding elements), A-HIGH-1 (both labelled units) and A-MEDIUM
(a) (measurement basis + provenance pointer) cannot fit that bound. **The bound
was raised deliberately, and the reason is recorded in the harness header next to
the new bound.** ⛔ No required clause was dropped to fit an inherited bound.
