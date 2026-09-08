# CONTENT SPEC — bank the Seth adjudication CLOSURE
DOCS-ONLY, purely ADDITIVE provenance. Nothing already written changes meaning.
⛔ `.planning/osf_deviations.md` lines 1-531 stay BYTE-IDENTICAL.
⛔ Status stays "DRAFTED — NOT POSTED". No OSF contact, no Seth contact, ever.

## WHY THIS MATTERS
The disclosure records that it was CORRECTED after adversarial review, but not that it was
then ADJUDICATED to closure. "Unadjudicated draft" and "adjudicated, no open objection"
are materially different postures for a document headed to OSF. Record the second.

## ADD to the disclosure's status block (after the existing CORRECTED bullet)

- **ADJUDICATED 2026-09-08 — NO OPEN OBJECTION.** The disclosure was reviewed across
  multiple rounds by the project's external reviewer, who then raised **two defects in the
  corrections themselves**:
  - **D8 — ACCEPTED.** The pair-4 citation called it "a NaN pair with no covering deletion."
    FALSE: its NaN-implicated SNP at 5922718 IS covered by a third record, `DEL 5922716`
    (span 5922716-5922722), is therefore EXCLUDED by the predicate, and yields **ZERO
    residual** — a DIFFERENT class from the chr7 survivor, for which no covering record
    exists for EITHER member and which SURVIVES INTO THE PANEL. Corrected in `260908-hv8`.
    ⭐ The mechanism was BROADER than the instance reported: the same phrase occurred
    **three times** — false on pair 4, TRUE on the survivor and on one annotation — and that
    shared phrasing WAS the false equivalence, so correcting only pair 4 would have left it
    reconstructible. All three eliminated. The phrase was also invisible to a literal `grep`
    (line-wrapped AND bolded), so a literal-scoped guard would have reported success while
    leaving the defect standing.
  - **D7 — RAISED, THEN RETRACTED BY THE REVIEWER AFTER HE MEASURED IT.** The charge was
    that our corrected mk7ze line numbers were converted from stale references. Measurement
    showed otherwise: the cited sentences SPAN MULTIPLE LINES (the NaN sentence = posted
    108-110, repo draft 275-277; clause (a) = posted 300-302, repo draft 467-469). We cited
    where each sentence BEGINS; he measured where the phrase he quoted FALLS. Both are
    defensible referents and `275 - 167 = 108` is correct arithmetic on a correct input.
    The real defect was that a SINGLE line number for a MULTI-LINE sentence is AMBIGUOUS —
    which is exactly why two parties measuring the same artifact produced different numbers.
    Fixed as RANGES with the verbatim quotation as the primary locator, since a quote
    survives repagination and a line number does not.
- **REMAINING BEFORE POSTING — ONE MEASUREMENT, NOT AN OBJECTION.** The pairs-per-occluding-
  deletion DISTRIBUTION in the tail, from `pcs_tail_verdicts.tsv` (VM-side; reads the
  emitted TSV only; no re-run, no genotypes). Design effect ~ 1 + (c-1)*ICC. c ~ 2 at high
  ICC reproduces Finding 2's 1.99 headline from a COMPLETELY HOMOGENEOUS panel; c ~ 1 leaves
  the dispersion unexplained and parent heterogeneity live. ⚠ Report the DISTRIBUTION, not
  the mean alone — the design effect is driven by the mean of c WEIGHTED BY CLUSTER SIZE.
  ⚠ The 22.9% deletion-deletion-neighbour figure is NOT a measurement of c: it constrains
  pair COMPOSITION, not cluster SIZE. It makes c > 1 plausible; it does not quantify it.
  **Carter fires this. No agent fires it.** No prediction is offered by either party.

## ALSO RECORD (in the reviewer-accounting part of the heterogeneity section)
The reviewer's own framing of his invalid refutation, adopted over ours because it is
sharper: his SPECIFIC mechanism (sub-window replication) does remain unable to create
dispersion and stays dead; but the GENERAL PRINCIPLE he used to kill it —
"non-independence cannot create dispersion, only amplify it" — was FALSE, and **a false
general principle silently forecloses hypotheses nobody tested**. That is why within-window
clustering went untested while both parties believed the question settled. It cost more
than the specific error did.

## PART C — refresh the resume surface
`.planning/HANDOFF.json` and `.planning/STATE.md`: the Seth loop is CLOSED with no open
objection; the sole remaining pre-posting item is the pairs-per-deletion measurement, which
is Carter's fire. MEASURE any courier/disclosure pin you touch — do not copy a stale value.
