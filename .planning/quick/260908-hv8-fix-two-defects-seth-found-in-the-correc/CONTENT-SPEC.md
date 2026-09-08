# CONTENT SPEC — Seth's two defects in the corrections themselves
DOCS-ONLY. Edits `.planning/osf_deviations.md` (the disclosure entry, still
DRAFTED — NOT POSTED) and, if the same text appears there, the courier record.
⛔ `.planning/osf_deviations.md` lines 1-531 stay BYTE-IDENTICAL (pre-registration chain).

===============================================================================
## D8 — SERIOUS: the pair-4 citation OVER-CLAIMS and creates a FALSE EQUIVALENCE
The disclosure currently calls region-1 pair 4 "a NaN pair with **NO covering deletion**".
**That is FALSE as stated**, and the correct facts are in our own geometry verdict
`.planning/amendments/m3_region1_nan_geometry_verdict.md:19-20, 30-37`:
  - pair 3: `DEL 5922716 (7bp) -> SNP 5922718`, `ref_span_overlap` — the deletion spans the SNP
  - pair 4: `SNP 5922718 -> DEL 5922724 (31bp)`, `disjoint`, annotated
    "**2nd-order: SNP already occluded by DEL@5922716**"
  - verbatim: "SNP@5922718 DOES sit inside DEL@**5922716** (span 5922716-5922722)"
So pair 4's NaN-implicated SNP **IS covered** by a THIRD record, **IS excluded by the
predicate**, and yields **ZERO residual**. The chr7 survivor has **no covering record for
either member** and therefore **survives into the panel**. DIFFERENT CLASSES.
As written, a reader concludes the survivor's class was documented before posting. IT WAS NOT.

REPLACE the pair-4 sentence with (adopted from Seth's proposed wording):
  "region-1 pair 4 — a NaN pair whose two members are not in a coverage relation (the
   NaN-implicated SNP at 5922718 is covered by a THIRD record, DEL 5922716 spanning
   5922716-5922722, and is therefore EXCLUDED by the predicate with NO residual) — was
   documented BEFORE posting and DELIBERATELY EXCLUDED from the 5-member expectation set.
   ⚠ It is DISTINCT from the residual class reported here, in which NO covering record
   exists for EITHER member and the pair SURVIVES INTO THE PANEL.
   pair 4 = known, handled, zero residual. The chr7 survivor = unhandled, in-panel residual."
⚠ The §(4) scoping repair STILL HOLDS and must be kept: pair 4's two members not being in a
coverage relation is exactly what shows the narrow reading of line 275 was what the
expectation set was built on. The citation is sound FOR THAT PURPOSE; only the
"no covering deletion" gloss and the implied equivalence are wrong.

===============================================================================
## D7 — the mk7ze line citations are AMBIGUOUS (cite RANGES, and lead with the quote)
⚠ DIAGNOSIS, stated precisely — do NOT record this as "the numbers were wrong again":
Both cited sentences SPAN MULTIPLE LINES. MEASURED directly in the posted body
(`awk 'NR>=168 && NR<=500'` of the amendment = mk7ze exactly: md5
`13a49f543cabcc27ce9f1e589783c060`, 22,945 B, 333 lines):
  the NaN sentence  -> posted lines **108-110**  (repo draft 275-277)
  clause (a)        -> posted lines **300-302**  (repo draft 467-469)
We cited 108 and 300 (where each sentence BEGINS). Seth measured 110 and 301 (where the
phrase HE quoted appears). BOTH are defensible referents. The defect is that a single line
number for a multi-line sentence is AMBIGUOUS — not that either arithmetic was wrong.
FIX: cite the RANGE, and keep the verbatim quotation as the primary locator, since a quote
survives repagination and a line number does not.
  "mk7ze lines 108-110 (repo draft 275-277)"
  "clause (a) at mk7ze lines 300-302 (repo draft 467-469)"
`mk7ze line 104` (the "settled 5-member expectation" quote) is CORRECT — verify and leave it.

===============================================================================
## D9 — state the `undefined` sweep result explicitly (Seth asked; it is cheap and it helps)
The word `undefined` occurs EXACTLY ONCE in the posted body, at posted line 82:
"policy for an occluded variant is unaffected: its LD is structurally undefined."
ADD, in the silence section:
  "The sweep also covered the word `undefined`, which occurs exactly ONCE in the posted body
   (line 82). Its implication runs **occluded -> undefined**, NOT undefined -> occluded, so it
   makes no completeness claim over undefined r and there is nothing there for the tail
   finding to falsify. Recorded because a sweep that omits the one relevant term is not a sweep."

===============================================================================
## D10 — the §(3) heading still oversells what its own body withdraws
Heading reads "THE SURVIVOR GEOMETRY — a HEADLINE, and a POSITIVE result for the rule",
but the body correctly withdraws the completeness promotion. Retitle to:
  "### (3) ⭐ THE SURVIVOR GEOMETRY — a HEADLINE, and what it does and does NOT establish"

===============================================================================
## WHAT MUST NOT CHANGE
- Status stays "DRAFTED — NOT POSTED". No OSF contact, no Seth contact by any agent.
- Lines 1-531 of osf_deviations.md byte-identical.
- Nothing under src/ or tests/. The two-file tcujq docstring defect stays DEFERRED.
- PART D (pairs-per-deletion measurement) stays QUEUED, not executed — Carter fires.
- Do NOT reintroduce: `complete in its own direction`, `non-independence cannot create`,
  `unrelated constants`, `register this as a negative result`, `2.62`.
