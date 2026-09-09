# CONTENT SPEC — annotate ONE scope-limited claim in the courier's LIVE body
DOCS-ONLY, additive, tiny. One file:
`.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`

## THE CLAIM
Courier **line ~140, in the LIVE BODY** (NOT the appendix):
  "The dispersion is robust in **DIRECTION** (every correction gives phi > 1.3) but
   **POORLY DETERMINED in magnitude** ..."

## WHY IT NEEDS ANNOTATING, AND WHY NOT A REWRITE
It was TRUE as written and REMAINS true as scoped: it referred to the OVERLAP corrections
(2.36 / 1.97 / 1.99 / 1.52 — all > 1.3). What changed is that a NEW correction set exists
that did not on 2026-09-02: the design-corrected figures (1.931 / 1.652 / 1.564 / **1.249**),
whose minimum falls BELOW 1.3. So the sentence is not false; its SCOPE has narrowed.
A reader now takes it as a general robustness claim, which it no longer supports.

## ADD immediately after that sentence (do NOT rewrite the sentence itself)
  ⚠ **SCOPE-LIMITED 2026-09-08.** That "phi > 1.3" statement was scoped to the OVERLAP
  corrections available on 2026-09-02 (2.36 / 1.97 / 1.99 / 1.52). It is TRUE for those and
  is left unedited for that reason. It does NOT extend to the DESIGN-CORRECTED figures,
  which did not exist when it was written: after correcting for the measured within-window
  clustering (ICC 0.729, c_eff 1.494), the corrections give 1.931 / 1.652 / 1.564 / **1.249**,
  and the last falls BELOW 1.3. See the 2026-09-08 entry in `.planning/osf_deviations.md`:
  **Finding 2 is NOT ESTABLISHED.**

## ⛔ DO NOT
- Do NOT edit the identical sentence inside the byte-frozen VERBATIM APPENDIX (~line 489).
  It is a dated communication record, its md5 is cited in committed artifacts, and it was
  true when written. Re-splice is for text that was FALSE when written; this is not that.
  Annotate the live body only.
- Do NOT rewrite or soften the original sentence — the annotation carries the correction.
- Nothing under `src/` or `tests/`. No OSF, no Seth, no VM contact. No push.
- Explicit git paths only.

## VERIFY
- The appendix region is UNCHANGED: its byte-equality to
  `.planning/quick/260902-vsp-.../CONTENT-SPEC.md` (`## ARTIFACTS` -> EOF) still holds; the
  appendix md5 is unmoved. Prove it, with a negative control seen RED.
- The annotation is present in the live body and ABSENT from the appendix.
- `git status --porcelain -- src tests` EMPTY.
- Normalize + case-insensitive for every phrase check (a literal grep has been blind on
  these files five times).
