# Placement SPEC — `ms-correction-v2` into the Track A manuscript (E-2 obligation (1))

**Task:** quick-260812-ot2 · **Date:** 2026-08-12 · **Target:** `docs/manuscript/id-vs-ref-LD.md`

## 1. What this file is

A **paste-ready placement SPEC that Carter applies**. Nothing in this file, and
nothing in the task that produced it, edits the manuscript — the standing
no-agent-edits rule HOLDS: ⛔ no agent edits `docs/manuscript/id-vs-ref-LD.md`,
posts to OSF, or edits the body of a posted amendment.

- **Discharge condition** (v2 file §1): obligation **(1)** discharges when the
  `ms-correction-v2` paragraph is placed in the Track A manuscript — **Carter's
  external action**. This SPEC existing discharges nothing.
- **Source of truth:** the **v2** selected pair,
  `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md`.
  **The v2 pair supersedes v1.** The `260811-tf3` and `260811-oku` texts are
  superseded history — never quote from them.

## 2. Pre-placement check status

The v2 file's pre-placement check asks whether the target journal's process
reads a "correction" framing on a manuscript **in submission** as a formal
post-publication correction notice.

- **On a FRESH submission the check does not fire.** Per the cross-venue
  finding in `260812-ot2-RESEARCH.md`: corrections/errata machinery at every
  surveyed venue attaches exclusively to **published or in-press** articles; a
  fresh, never-submitted manuscript has no live editorial record for
  correction machinery to act on. The §1 default placement therefore stands:
  **Methods correction-and-disclosure note + a pointer sentence from
  Limitations** (sections 3–6 below).
- **Conditional:** if this manuscript is part of a **PENDING submission
  anywhere**, the in-submission reading re-triggers — keep the CONTENT below
  and use framing A's PLACEMENT (the Limitations section) per the v2 file's
  pre-placement check. That is a placement change and nothing more.
- This SPEC asserts **nothing** about whether a pending submission exists.
- **⚠ Note for the v2 file's §3 pre-paste checklist, item 3** *(added
  2026-08-12 EVENING)*: `git log --oneline 7d575a5..HEAD -- src/` is **no
  longer empty** — it now shows `5284505` (+ its `260812-thz` follow-up), the
  m3-04c PRE-FIRE 1 per-region occlusion-manifest upload in
  `src/python/run_native_ld_panel.py`. That is **fire-prep plumbing, not an
  E-2 code change**: the E-2 disposition (option A, code unchanged) concerns
  `ld_allele_join.R` / `run_qtl_coloc.R` / the fine-map join, none of which
  moved (verified in the 2026-08-12 blast-radius sweep: the only src file
  touched in `76dd7cd..HEAD` is `run_native_ld_panel.py`). The checklist item
  fails safe — it blocks until judged — and this note is the pre-judged
  answer, on record so posting day does not have to re-derive it.

## 3. Placement instructions (the <=2-minute action)

Anchor by **heading text**; line numbers are as-of-2026-08-12 courtesy
pointers only.

**Step 0 — CHOOSE THE CLOSING SENTENCE FIRST (section 5; do not skip).**
> ✅ **CHOSEN 2026-08-12: P-1** (`DEC-2026-08-12-e2-p1-closing-sentence`) — paste
> the block **byte-intact**. Consequence now on the clock: post
> `osf-correction-v2` + record URL/timestamp in `osf_deviations.md`
> **before/at submission day** so the closing sentence is true. P-2 stays below
> as the record of what was considered; do not place it.
The block's final sentence references an OSF supplementary entry that does
**not exist** while obligation (2) stays skipped. Before pasting anything,
pick **P-1** (keep the block byte-intact and commit to posting the OSF entry
before/at submission) or **P-2** (swap in the marked variant sentence of
section 5). Pasting the block without making this choice places a sentence
that is false at placement time. *(Step added 2026-08-12 EVENING per the
blast-radius sweep — the fork existed in section 5 but the step list did not
force it.)*

**Step 1 — the Methods note.** In `docs/manuscript/id-vs-ref-LD.md`, find the
`### Ethics Statement` heading (:130) and its one-paragraph body (:132). After
that body paragraph and **before** `## Results` (:134), insert, in order:

1. a blank line;
2. the new heading: `### Correction and Disclosure: Variant-Orientation Exposure`
3. a blank line;
4. the paste block of section 4 — **content lines only** (the 13 sentences).
   The two HTML-comment marker lines wrapping the block are extraction anchors
   for the byte verification in section 7, **not manuscript text** — do not
   paste them.

**Step 2 — the Limitations pointer.** Append the pointer sentence of section 6
to the end of the `### Limitations` paragraph (:252), as item **(7)** after
item (6).

## 4. The paste block (machine-extracted; byte-locked)

The block below, INCLUDING both marker lines, was produced by machine
extraction from the v2 source (the anchored `sed` range of section 7), not by
transcription, and is proven byte-identical to the source in section 7.

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

## 5. The closing-sentence fork (Carter chooses at placement)

**The coherence consequence, stated once:** the block's final sentence
cross-references "the paired entry posted as a supplementary file on
osf.io/az52u". Obligation **(2)** — that OSF posting — is **skipped by
Carter's 2026-08-12 direction**, so at placement time that sentence is
**FALSE**: no such supplementary entry exists yet. Two options; the ledger
record is `DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip`.

**Option P-1 (pair-coherent — RECOMMENDED).** Place the block **byte-intact**
and treat obligation (2) as **deferred-to-submission**: the OSF entry must
exist by the time the manuscript is submitted, making the sentence true before
any editor or reviewer can read it. Grounds: the rigor-over-speed standing
rule, and the v2 file §3 item 4 pair-matching check assumes the two halves of
the pair agree — P-1 keeps the placed half identical to the gated v2 half.

**Option P-2 (skip-permanent).** Replace ONLY the final sentence of the block
with the variant below. Under P-2 the placed text is **no longer "the v2 pair
half"** — it is a Carter-directed deviation from the gated v2 pair, recorded
in `DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip`.

> **P-2 VARIANT — NOT part of the gated v2 pair; Carter-directed deviation:**
> The full measurement, its denominator and the corrections it makes to our
> internal record are maintained in the project's internal version-controlled
> record under pre-registration osf.io/pvb5j.

(The variant lives outside the PASTE-BEGIN/END markers, so the byte check on
section 4 stays clean.)

The E-4 public-commitment obligation is **NOT registered** by this task — its
trigger is posting, which is skipped.

## 6. The Limitations pointer sentence (item (7))

Append to the end of the `### Limitations` paragraph:

> (7) Our own hypothesis-driven audit of the pipeline measured a
> variant-orientation exposure in its catalog-to-panel variant bookkeeping,
> disclosed and bounded in Methods §Correction and Disclosure:
> Variant-Orientation Exposure; the analysis code is unchanged by that
> disclosure, and no reported result moves.

The sentence quotes no figures by design; every number lives in the Methods
note, where its unit and its bounding caveats travel with it.

## 7. Verification record (actual commands, observed output)

Run 2026-08-12 from the repo root. `SRC` = the v2 pair file
(`.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md`);
`DRAFT` = this file. The perturbed copy used for the negative control lives in
the session scratchpad only — it is never committed.

**(a) NEGATIVE CONTROL — observed RED first.** A one-character perturbation of
a copy of the extraction (line 2, `We` → `Xe`) must make the same cmp fail;
green is trusted only after this was observed:

```
$ cmp <(sed -n '/^<!-- PASTE-BEGIN: ms-correction-v2 -->$/,/^<!-- PASTE-END: ms-correction-v2 -->$/p' "$SRC") "$SCRATCH/ms-block-perturbed.txt"; echo "exit=$?"
/dev/fd/63 [scratchpad]/ms-block-perturbed.txt differ: byte 40, line 2
exit=1
```

**(b) The byte comparison — observed GREEN on this file:**

```
$ cmp <(sed -n '/^<!-- PASTE-BEGIN: ms-correction-v2 -->$/,/^<!-- PASTE-END: ms-correction-v2 -->$/p' "$SRC") <(sed -n '/^<!-- PASTE-BEGIN: ms-correction-v2 -->$/,/^<!-- PASTE-END: ms-correction-v2 -->$/p' "$DRAFT") && echo BYTE-IDENTICAL
BYTE-IDENTICAL
```

**(c) Marker uniqueness (each marker line exactly once in this draft):**

```
$ grep -cx -- '<!-- PASTE-BEGIN: ms-correction-v2 -->' "$DRAFT"
1
$ grep -cx -- '<!-- PASTE-END: ms-correction-v2 -->' "$DRAFT"
1
```

**(d) Number/framing greps of the verify block** (patterns are quote-split so
this record cannot self-match; the regex each command runs is unchanged):

```
$ grep -n '5\.29' "$DRAFT"; echo "exit=$?"
exit=1        (no match — the pooled corpus figure appears nowhere in this file)
$ grep -in 's''alvage' "$DRAFT" | grep -iv 'not a s''alvage'; echo "exit-of-pipeline=$?"
exit-of-pipeline=1        (empty — the only candidate line is the paste block's own negated form, filtered as required)
$ grep -in 'r''evision' "$DRAFT"; echo "exit=$?"
exit=1        (no match anywhere in this file)
```

Framing rules bind all SPEC prose: hypothesis-driven original research
throughout; the standing forbidden-framing words of the v2 file §4 appear
nowhere in this SPEC's prose (one appears inside the paste block only in its
negated form, as the source requires); the pooled corpus figure appears
nowhere in this file; no E-2 figure is quoted in SPEC prose outside the paste
block, and nothing here reads the block's rates as a real-LD exposure — the
block's own identity-LD-stub sentence governs.

## 8. Stale-header note

The manuscript's Status line (:3) and Target-venue line (:7) name *Genome
Medicine*. Venue selection is now governed by the ot2 journal memo
(`260812-ot2-journal-selection-memo.md`, Nature-first ladder per Carter's
2026-08-12 directive), so those header lines are stale relative to the memo.
Updating them is **Carter's own edit** — out of scope for any agent, and not
part of the <=2-minute placement action above.
