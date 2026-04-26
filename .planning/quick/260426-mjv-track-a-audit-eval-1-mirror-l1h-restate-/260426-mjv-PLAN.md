---
quick_id: 260426-mjv
slug: track-a-audit-eval-1-mirror-l1h-restate-to-publication-surfaces
description: "Track A audit Eval-1 — mirror L1H formal SUPERSEDED+kki attribution into the publication trio (track_a_pivot.md L295 figure caption + fig2_cs_yield.R header + TRACK-A-FROZEN-NUMBERS.md reconciliation row). Idempotent shore. Prose-only."
mode: quick
created: 2026-04-26
plan_source: /home/ckclinto/.claude/plans/track-a-audit-eval-1-mirror-l1h-restate-idempotent-shore.md (approved by user 2026-04-26)
mirror_precedent: 260426-l1h (commits 90718dc, 3339d84, 7f75aae)
must_haves:
  - publication_alignment: track_a_pivot.md L295 Figure 2 caption + fig2_cs_yield.R L10-17 header carry the formal "SUPERSEDED 2026-04-25 per quick-260425-kki" attribution mirroring L1H Pattern A
  - matched_coverage_citation: fig2_cs_yield.R header upgraded to L1H Pattern B verbatim "(48/95 vs 51/96 = 1.06x yield)" form
  - manuscript_voice_preserved: docs/manuscript/track_a_pivot.md L28/L82/L138/L216 (abstract/results/headline/discussion) byte-identical — original-research voice preserved per Carter framing rule (`feedback_original_research_framing` user memory)
  - frozen_numbers_appended_only: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md L1–L200 byte-identical; one reconciliation-log row appended in the L201–L212 block
  - audit_traceability: 12/96 / 4.25× preserved verbatim everywhere it appeared pre-task; no deletions of historical scalars
  - disk_truth_untouched: results/, results_identity_ld/, docs/manuscript/figures/ byte-identical (no compute, no figure render); fig2_cs_yield.R disk-truth scalar block L71–82 + runtime assertion block L99–138 byte-identical
  - framing_lock: zero forbidden tokens (revision/cleanup/fix-up/mistake/got this wrong/correction/simplified/placeholder/TBD/for now/v1) in any new content or commit message; `revise(...)` commit-prefix is the established GSD convention from L1H, distinct from forbidden `revision`
  - atomic_commits: 3 atomic prose-only commits, one per file
  - idempotent_audit_recorded: ${QUICK_DIR}/260426-mjv-AUDIT.md classifies every grep-found citation site as MATCH / DRIFT-A / DRIFT-B / MATCH-PROSE / N/A with surface-appropriateness rationale per site
  - pre_post_md5_recorded: ${QUICK_DIR}/md5_pre.txt + md5_post.txt + diff captured; site_inventory_pre.txt + site_inventory_post.txt captured
---

# Quick Task 260426-mjv — Track A Audit Eval-1 Mirror L1H Restate to Publication Surfaces (Idempotent Shore)

## Context

`AUDIT-REVIEW-2026-04-25.md` Eval-1 ("the comparator problem") was closed in two passes:

1. **Quick task `260425-kki`** (commits `884eb3d..f0451b0`, 2026-04-25) restated the **live publication surfaces** — manuscript prose, fig2 R script, frozen-numbers ledger — to the matched-coverage post-k2d 48/95 vs 51/96 = 1.06× comparator.
2. **Quick task `260426-l1h`** (commits `90718dc..7f75aae`, 2026-04-26) propagated the **same restate into the planning ecosystem** at 9 sites across `.planning/amendments/TRACK-A-PIVOT.md`, `.planning/PROJECT.md`, and `.planning/STATE.md` using two formal patterns:
   - **Pattern A (SUPERSEDED + kki attribution):** `(SUPERSEDED 2026-04-25 per quick-260425-kki; narrow-validation 12/96 / 4.25× baseline preserved with full audit trail in 'TRACK-A-FROZEN-NUMBERS.md')`.
   - **Pattern B (matched-coverage K2D citation):** `matched-coverage k2d full-coverage 2026-04-25 re-fire (48/95 vs 51/96 = 1.06×)`.

L1H explicitly did NOT touch the publication surfaces (its SUMMARY records `Live publication surfaces byte-identical pre vs post`) because kki had already restated them. **However**, kki's restate predates L1H's formalization of the two patterns — kki used contextual prose forms appropriate to each surface (manuscript prose at L28/L82/L138/L216; figure-caption pointer at L295; code-comment header in fig2 R; reconciliation-log entry in FROZEN-NUMBERS L74/L209). L1H added one formal token absent from kki's prose forms: the explicit `per quick-260425-kki` audit-trail attribution.

**This task mirrors L1H's formal annotation pattern into the publication trio, idempotently** — touching only sites where the L1H pattern is not yet present in functional form, leaving sites verbatim where it is. The result is audit-trail symmetry between the planning ecosystem (post-L1H) and the live publication surfaces.

This is publication-prose-only work — **no compute, no figure renders, no data pipeline runs.**

## Carter framing rules (verbatim from L1H precedent)

- **Anchor language:** "we tightened the comparator and the inflation magnitude shifted"
- **Forbidden tokens** in any new prose, commit messages, or SUMMARY: `revision`, `cleanup`, `fix-up`, `mistake`, `error in the prior`, `we got this wrong`, `placeholder`, `TBD`, `for now`, `v1`, `simplified`, `correction`. (Note: `revise(...)` commit-prefix is the established GSD convention from L1H, distinct from the forbidden `revision` token.)
- **Audit traceability:** 12/96 / 4.25× preserved verbatim under SUPERSEDED markers — never deleted.
- **Original-research framing** (`feedback_original_research_framing` user memory): manuscript prose at the abstract/results/discussion level remains in natural research voice (no planning-file pointers in abstract); formal `per quick-260425-kki` attribution is appropriate ONLY in figure captions, methods footnotes, R-script comments, and FROZEN-NUMBERS reconciliation blocks where audit-trail traceability is the explicit purpose.
- **Idempotent:** pre-task `md5sum` recorded for each file. Sites that already carry the L1H pattern in functional form are no-ops. Final SUMMARY documents which sites were touched and which were classified as already-matching.

## Files in scope (3 — publication trio)

| # | Surface | Path | Role |
|---|---------|------|------|
| 1 | Track A pivot manuscript | `docs/manuscript/track_a_pivot.md` | Live manuscript draft (Nature Genetics target) |
| 2 | Fig2 CS-yield render script | `src/R/figures/fig2_cs_yield.R` | Disk-derived comparator figure builder |
| 3 | Frozen numbers master ledger | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | Single source of truth for manuscript scalars |

**Out-of-scope (explicitly do NOT touch):**

- `.planning/amendments/TRACK-A-PIVOT.md`, `.planning/PROJECT.md`, `.planning/STATE.md` — already restated by L1H on 2026-04-26.
- `AUDIT-REVIEW-2026-04-25.md` — audit-time snapshot; updating erases audit history.
- `results/`, `results_identity_ld/`, fig PNG/PDF outputs, `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` — disk truth; no compute in this task.
- `docs/manuscript/track_a_source.md` — prior draft, read-only reference.
- Other figure scripts (`fig1a_*`, `fig1b_*`, `fig3_*`, `fig5_*`, `fig_h3_*`) — separate slug.

## Pre-task audit (executor MUST run FIRST, before any edit)

Record the pre-task state and classify every grep-found site BEFORE any task edits begin.

```bash
QUICK_DIR=".planning/quick/260426-mjv-track-a-audit-eval-1-mirror-l1h-restate-"

# Pre-task md5 for byte-identical roundtrip verification of unchanged sites
md5sum docs/manuscript/track_a_pivot.md \
       src/R/figures/fig2_cs_yield.R \
       .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
  > "${QUICK_DIR}/md5_pre.txt"

# Inventory every citation site
grep -nE "12 ?/ ?96|4\.25|SUPERSEDED|48 ?/ ?95|51 ?/ ?96|1\.06|k2d|260424-k2d|260425-kki" \
  docs/manuscript/track_a_pivot.md \
  src/R/figures/fig2_cs_yield.R \
  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
  > "${QUICK_DIR}/site_inventory_pre.txt"
```

Then for each line in `site_inventory_pre.txt`, classify into one of:

- **MATCH** — already carries L1H pattern in functional form (skip; record as no-op)
- **DRIFT-A** — has SUPERSEDED token but lacks `per quick-260425-kki` attribution → apply Pattern A upgrade
- **DRIFT-B** — discusses 12/96 ↔ 48/95 supersedure but lacks any SUPERSEDED token AND surface admits formal annotation (apply if surface is figure caption / methods footnote / R-script header / FROZEN-NUMBERS block; SKIP if surface is manuscript abstract/results/discussion prose — those keep natural-voice framing)
- **MATCH-PROSE** — uses prose framing appropriate to surface (manuscript abstract/results/discussion); explicit formal annotation would violate original-research framing rule (skip; record in SUMMARY as intentionally prose-form)
- **N/A** — non-comparator context (e.g., disk-truth scalar, runtime assertion, historical reconciliation row, ghost-numerics line) (skip)

Write the classification table to `${QUICK_DIR}/260426-mjv-AUDIT.md` BEFORE Task 1 begins.

## Task 1 — `docs/manuscript/track_a_pivot.md`

**Pre-task expected sites** (from grep audit, confirmed 2026-04-26):

| Line | Context | Classification |
|------|---------|----------------|
| 28 | Abstract | **MATCH-PROSE** (skip — abstract is original-research voice) |
| 82 | Results §Yield | **MATCH-PROSE** (skip — results body) |
| 138 | Headline result | **MATCH-PROSE** (skip — results body) |
| 216 | Discussion | **MATCH-PROSE** (skip — discussion body) |
| 295 | Figure 2 caption | **DRIFT-A** — has SUPERSEDED phrasing + audit-trail pointer but lacks formal `per quick-260425-kki` attribution. Apply Pattern A upgrade. |

**Edit (Pattern A upgrade at L295 Figure 2 caption ONLY):**

OLD (verbatim from L295):
> An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline (now superseded; see `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` for the audit trail).

NEW:
> An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline (SUPERSEDED 2026-04-25 per quick-260425-kki; narrow-validation 12/96 / 4.25× baseline preserved with full audit trail in `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`).

**Why only L295 changes:** Figure captions are the appropriate manuscript locus for formal audit-trail attribution (cf. existing planning-file pointer already at L295). Abstract/results/discussion sites already convey the comparator-tightening narrative in natural research voice and would violate Carter's original-research framing rule if formalized.

**Verify after edit:**

```bash
# Exactly one new formal attribution in the manuscript, at L295
grep -nE "SUPERSEDED 2026-04-25 per quick-260425-kki" docs/manuscript/track_a_pivot.md
# Expected: exactly 1 hit at L295

# Same 5 sites for 12/96 / 4.25 — no new bare claims, no deletions
grep -nE "12 ?/ ?96|4\.25" docs/manuscript/track_a_pivot.md
# Expected: same 5 hits (L28/L82/L138/L216/L295)

# Sites L28/L82/L138/L216 must remain BYTE-IDENTICAL (MATCH-PROSE)
git diff docs/manuscript/track_a_pivot.md | grep -E "^[+-]" | grep -v "^[+-]{3}" | head
# Expected: only the L295 hunk visible
```

**Commit message:**

```
revise(track-a-eval-1): mirror L1H formal SUPERSEDED+kki attribution to track_a_pivot.md Figure 2 caption (1 site; L28/L82/L138/L216 prose verbatim)

- L295 Figure 2 caption: "(now superseded; see ... for the audit trail)" upgraded to "(SUPERSEDED 2026-04-25 per quick-260425-kki; narrow-validation 12/96 / 4.25x baseline preserved with full audit trail in .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)"
- L28 abstract / L82 Results / L138 Headline / L216 Discussion: prose forms verbatim (MATCH-PROSE; manuscript original-research voice preserved per Carter framing rule)

Mirrors quick-260426-l1h Pattern A. Quick task: 260426-mjv.
```

## Task 2 — `src/R/figures/fig2_cs_yield.R`

**Pre-task expected sites** (from grep audit, confirmed 2026-04-26):

| Line | Context | Classification |
|------|---------|----------------|
| 5–6 | Header purpose | **MATCH** (matched-coverage K2D citation present) |
| 10–17 | Header "Comparator-tightening note" | **DRIFT-A** — has SUPERSEDED token + FROZEN-NUMBERS pointer but lacks `per quick-260425-kki` attribution |
| 23, 28, 29–30 | Source-pointer comments | **MATCH** (K2D cited) |
| 34 | `.planning/amendments/TRACK-A-PIVOT.md §5` reference | **MATCH** (planning-file pointer to L1H-restated source) |
| 71–82 | Disk-truth scalar block (`N_REAL_LD_NONEMPTY <- 51L` etc.) | **N/A** (machine scalars, not prose; byte-identical) |
| 99–138 | Runtime validation (assertion error templates mentioning 4.25 etc.) | **N/A** (assertion error template; byte-identical) |
| 155, 160, 167, 224, 229, 230, 258 | Diagnostic / plot labels | **MATCH** |

**Edit (Pattern A + Pattern B upgrade at L10–17 header comment ONLY):**

OLD (header lines 10–17, "Comparator-tightening note"):
```
# Comparator-tightening note (2026-04-25, kki):
#   We tightened the comparator from a partial-coverage Stage 1d narrow-
#   validation baseline (12/96, 2 of 10 admissible regions had identity-LD
#   fits) to the k2d full-coverage 2026-04-25 re-fire (48/95, all
#   admissibility-matched regions); the inflation magnitude shifted from
#   4.25x to ~1.06x. The 12/96 baseline is preserved verbatim with a
#   SUPERSEDED 2026-04-25 markup in TRACK-A-FROZEN-NUMBERS.md for audit
#   traceability.
```

NEW (mirror L1H Pattern A — add `per quick-260425-kki` attribution + Pattern B matched-coverage citation; preserve all numerics verbatim):
```
# Comparator-tightening note (2026-04-25, propagated by quick-260425-kki):
#   We tightened the comparator from a partial-coverage Stage 1d narrow-
#   validation baseline (12/96, 2 of 10 admissible regions had identity-LD
#   fits) to the matched-coverage k2d full-coverage 2026-04-25 re-fire
#   (48/95 vs 51/96 = 1.06x yield); the inflation magnitude shifted from
#   4.25x to ~1.06x. The 12/96 baseline is preserved verbatim under a
#   SUPERSEDED 2026-04-25 per quick-260425-kki markup in TRACK-A-FROZEN-
#   NUMBERS.md for audit traceability.
```

**Why only this hunk:** All other K2D mentions in the script are already in canonical "k2d 2026-04-25" / "k2d full-coverage 2026-04-25 re-fire" form (matches L1H Pattern B). Only the SUPERSEDED note carries the supersedure attribution and was missing the kki pointer.

**Do NOT execute the script.** This is prose-only on a header comment; running the renderer is out of scope and would consume LSF.

**Verify after edit:**

```bash
# Exactly one new formal attribution in the script, in the header
grep -nE "SUPERSEDED 2026-04-25 per quick-260425-kki" src/R/figures/fig2_cs_yield.R
# Expected: exactly 1 hit in header L10-17

# Numerics preserved verbatim
grep -cE "12 ?/ ?96|4\.25" src/R/figures/fig2_cs_yield.R
# Expected: same count as pre-task

# Matched-coverage citation strengthened, never weakened
grep -cE "48 ?/ ?95|51 ?/ ?96|1\.06" src/R/figures/fig2_cs_yield.R
# Expected: >= pre-task count

# Disk-truth scalar block at L71-82 must be byte-identical
sed -n '71,82p' src/R/figures/fig2_cs_yield.R | md5sum
# Expected: matches pre-task md5 of same lines (do NOT perturb assertion targets)

# Runtime assertion block at L99-138 must be byte-identical
sed -n '99,138p' src/R/figures/fig2_cs_yield.R | md5sum
# Expected: matches pre-task md5 of same lines

# Script must still parse-check OK (no R execution; static parse only)
Rscript -e 'parse("src/R/figures/fig2_cs_yield.R"); cat("PARSE-OK\n")'
# Expected: PARSE-OK
```

**Commit message:**

```
revise(track-a-eval-1): mirror L1H formal SUPERSEDED+kki attribution to fig2_cs_yield.R header comment (1 hunk; disk-truth scalars verbatim)

- Header L10-17 "Comparator-tightening note": added "propagated by quick-260425-kki" attribution + "SUPERSEDED 2026-04-25 per quick-260425-kki markup" formal phrasing; matched-coverage citation expanded from "(48/95, all admissibility-matched regions)" to "(48/95 vs 51/96 = 1.06x yield)" mirroring L1H Pattern B verbatim
- Disk-truth scalar block L71-82, runtime assertions L99-138, plot/diagnostic labels: byte-identical (no compute, no figure render)

Mirrors quick-260426-l1h Pattern A + Pattern B in code-comment form. Quick task: 260426-mjv.
```

## Task 3 — `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`

**Pre-task expected sites** (from grep audit, confirmed 2026-04-26):

| Line | Context | Classification |
|------|---------|----------------|
| 10 | Live block heading (post-k2d full-coverage 2026-04-25, LIVE) | **MATCH** (Pattern B in heading) |
| 15–18 | Live block table (51/96, 48/95, 1.06× rows) | **MATCH** (Pattern B verbatim) |
| 22 | Headline framing (Carter anchor language verbatim) | **MATCH** |
| 24 | Sources footnote (k2d TSV + Stage 2 manifest) | **MATCH** |
| 26 | Denominator note (95 of 96) | **MATCH** |
| 63 | Stage 2 sub-row (51/96, 53.1%) | **MATCH** |
| 70–75 | **SUPERSEDED block** ("Manuscript edits propagated quick-260425-kki") | **MATCH** — already carries SUPERSEDED token + kki attribution; functionally equivalent to L1H Pattern A |
| 166 | SUPERSEDED HLA-immune block (quick-260425-t9j) | **N/A** (different audit finding, not Eval-1) |
| 209 | Reconciliation log row (quick-260425-kki — Track A audit-driven figure correction pass) | **MATCH** (kki cited) |
| 210 | Reconciliation log row (quick-260426-04b H3 freeze) | **N/A** (different finding) |
| 211 | Reconciliation log row (quick-260425-t9j HLA reclassification) | **N/A** (different finding) |

**Result:** Every Eval-1 site in FROZEN-NUMBERS already carries the L1H pattern in functional form. **The file is byte-identical idempotent for the comparator restate** — no SUPERSEDED-block edits.

**However**, append a single reconciliation-log row documenting this mirror task itself, per FROZEN-NUMBERS L201–L212 convention (every quick task that touches the audit trail records itself for traceability).

**Edit (append one row to the reconciliation log in the L201–L212 block, dated 2026-04-26 with this quick-task's slug):**

Executor confirms placement by reading L201–L212 in full and inserting chronologically (after the existing 2026-04-26 04b row, before the 2026-04-26 t9j row — or as the last 2026-04-26 row depending on the convention observed in that block).

```
| 2026-04-26 | **L1H formal-pattern mirror to publication surfaces (idempotent shore)**: docs/manuscript/track_a_pivot.md L295 Figure 2 caption upgraded to formal `(SUPERSEDED 2026-04-25 per quick-260425-kki; ... preserved with full audit trail in TRACK-A-FROZEN-NUMBERS.md)`; src/R/figures/fig2_cs_yield.R header L10-17 upgraded to formal `SUPERSEDED 2026-04-25 per quick-260425-kki` attribution + matched-coverage `(48/95 vs 51/96 = 1.06x yield)` Pattern B citation. Manuscript prose at L28/L82/L138/L216 (abstract/results/headline/discussion) verbatim — original-research voice preserved per Carter framing rule. TRACK-A-FROZEN-NUMBERS.md content byte-identical (already carried L1H pattern in functional form at L70-75 SUPERSEDED block + L209 reconciliation row); only this audit-trail row appended. | quick-260426-mjv — mirrors quick-260426-l1h formal pattern to publication trio for audit-trail symmetry between planning ecosystem and live publication surfaces. |
```

**Verify after edit:**

```bash
# Numerics verbatim — no deletions
grep -nE "12 ?/ ?96|4\.25" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: same count as pre-task

# kki citation count unchanged (this task adds NO new kki citations to FROZEN-NUMBERS;
# it adds an mjv self-row that REFERENCES kki, which counts but is acceptable)
grep -cE "quick-260425-kki" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: pre-task count + 1 (the new mjv row references kki by name)

# Exactly one mjv self-row in reconciliation log
grep -nE "quick-260426-mjv" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: exactly 1 hit in reconciliation log block (L201-L212)

# All non-reconciliation-log content (L1-L200) byte-identical pre vs post
diff <(sed -n '1,200p' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md) \
     <(git show HEAD:.planning/amendments/TRACK-A-FROZEN-NUMBERS.md | sed -n '1,200p')
# Expected: 0 lines (only the reconciliation-log table appended to)
```

**Commit message:**

```
revise(track-a-eval-1): append L1H-mirror reconciliation row to TRACK-A-FROZEN-NUMBERS.md (1 row; live + SUPERSEDED blocks verbatim)

- Reconciliation log L201-212: appended one 2026-04-26 row documenting the L1H formal-pattern mirror to track_a_pivot.md L295 + fig2_cs_yield.R header for audit-trail symmetry
- All other content (live block L10-26, Stage 2 sub-row L63, SUPERSEDED block L70-75, HLA SUPERSEDED block L166, prior reconciliation rows L209-211): byte-identical (already carried L1H pattern in functional form)

Mirrors quick-260426-l1h. Quick task: 260426-mjv.
```

## End-to-end verification (7 gates, mirroring + extending L1H's 5-gate harness)

After all 3 task commits land, executor runs:

```bash
QUICK_DIR=".planning/quick/260426-mjv-track-a-audit-eval-1-mirror-l1h-restate-"

# Gate 1 — every 12/96 / 4.25 site in publication trio is properly framed
grep -nE "12 ?/ ?96|4\.25" \
  docs/manuscript/track_a_pivot.md \
  src/R/figures/fig2_cs_yield.R \
  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: same count as pre-task (no deletions, no new bare claims);
# every hit either (a) inside SUPERSEDED-annotated context, (b) in
# MATCH-PROSE original-research voice with the comparator-tightening
# narrative, or (c) in disk-truth/assertion code blocks

# Gate 2 — formal "per quick-260425-kki" attribution now present in publication trio
# at exactly the upgraded sites
grep -lE "SUPERSEDED 2026-04-25 per quick-260425-kki" \
  docs/manuscript/track_a_pivot.md \
  src/R/figures/fig2_cs_yield.R \
  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: 2 files listed (track_a_pivot.md L295, fig2_cs_yield.R header).
# FROZEN-NUMBERS.md does NOT need to appear — its existing L70-75 SUPERSEDED
# block + L209 kki reconciliation row already carry the pattern functionally.

# Gate 3 — matched-coverage K2D Pattern B citation present in all 3 files (idempotent)
grep -lE "48 ?/ ?95|matched-coverage k2d|1\.06" \
  docs/manuscript/track_a_pivot.md \
  src/R/figures/fig2_cs_yield.R \
  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# Expected: all 3 listed (PASS — already true pre-task; idempotent gate)

# Gate 4 — forbidden-token sweep on new commit messages and SUMMARY
git log -3 --format=%B \
  | grep -ivE "^revise\(" \
  | grep -iE "\b(revision|cleanup|fix-up|mistake|got this wrong|correction|simplified|placeholder|TBD|for now)\b"
# Expected: empty (the only legitimate "kki" / "supersedure" mentions are inside
# content that quotes the historical 260425-kki STATE.md rows or describes the
# supersedure event as historical fact, not as a new claim)

# Gate 5 — exactly 3 atomic commits, one per file
git log --oneline --grep="track-a-eval-1.*mirror\|track-a-eval-1.*L1H"
# Expected: 3 commits (track_a_pivot.md / fig2_cs_yield.R / TRACK-A-FROZEN-NUMBERS.md)

# Gate 6 — pre-task md5 vs post-task md5 (idempotent verification)
md5sum docs/manuscript/track_a_pivot.md \
       src/R/figures/fig2_cs_yield.R \
       .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
  > "${QUICK_DIR}/md5_post.txt"
diff "${QUICK_DIR}/md5_pre.txt" "${QUICK_DIR}/md5_post.txt"
# Expected: all 3 files differ (md5 changed) — confirms intentional edits landed;
# but each diff is small and confined to documented hunks (no collateral churn).

# Gate 7 — byte-identical safety: results/, results_identity_ld/, fig PNG/PDF
git diff HEAD~3 -- results/ results_identity_ld/ docs/manuscript/figures/
# Expected: 0 lines (no compute, no figure render, no disk-truth perturbation)
```

**Pass criterion:** Gates 1, 3, 4, 5, 7 all PASS; Gate 2 finds exactly 2 files; Gate 6 confirms all 3 files changed (intentional landings).

**Audit-trail symmetry test (end-to-end):** A reader landing in any Eval-1 publication-surface site that mentions 12/96 / 4.25× now finds either (a) original-research voice with the comparator-tightening narrative (manuscript prose at L28/L82/L138/L216), (b) formal `SUPERSEDED 2026-04-25 per quick-260425-kki` annotation (figure caption L295 + R script header L10–17 + FROZEN-NUMBERS SUPERSEDED block L70–75), or (c) timestamped reconciliation-log entry (FROZEN-NUMBERS L201–L212 block) — matching the symmetry now present in `.planning/amendments/TRACK-A-PIVOT.md`, `.planning/PROJECT.md`, `.planning/STATE.md` post-L1H.

## Out-of-task follow-ons (do NOT bundle)

Carry-forward from L1H SUMMARY (preserved here for traceability — these remain open):

- **STATE.md L40 — "861 hard failures" reference** (ghost-numerics purge follow-on; out of comparator scope)
- **`AUDIT-REVIEW-2026-04-25.md`** — audit-time snapshot, never updated by design
- **Audit High-Quality #2** — SH2B3 EUR L=20 re-fit + canonical BMI×HTN / HTN×stroke `coloc.susie` (Terminal A LSF compute slot)
- **Eval 2a** — drop / flag non-converged fits in 51/96 headline (`/gsd-discuss-phase`)
- **Eval 2c** — PP.H4 posterior intervals (algorithmic; SuSiE-RSS storage limitation)
- **Eval 3.3** — 28/28 empty `coloc.susie` outputs interpretation (entangled with Eval 2a)
- **Pathway-enrichment recompute** on the post-kki + post-t9j signal set (separate slug)
- **Submission-venue decision** — 1.06× framing may shift target *Genome Medicine* → *Bioinformatics* Applications Note (`/gsd-discuss-phase`)
- **Other figure scripts missing K2D citation** (per Agent 3 K2D-citation audit): `fig1a_pipeline_schematic.R`, `fig5_variant_mech_scorecard.R`, `fig_h3_ld_overlap_dose_response.R`, `fig1b_locus_panels.R` TODO-K2D markers — separate `/gsd-quick` slug if/when those figures need K2D framing.

## Critical files (paths the executor will edit, with line anchors)

| File | Lines touched | Lines preserved verbatim |
|------|---------------|--------------------------|
| `docs/manuscript/track_a_pivot.md` | L295 (Figure 2 caption hunk) | L28, L82, L138, L216 (manuscript prose), all other lines |
| `src/R/figures/fig2_cs_yield.R` | L10–17 (header "Comparator-tightening note" hunk) | L1–9, L18–264 (all disk-truth scalars at L71–82, all runtime assertions at L99–138, plot logic, diagnostic labels) |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | one new reconciliation-log row appended in the L201–L212 block | L1–L200 (live block, Stage 2 sub-row, SUPERSEDED blocks, prior reconciliation rows) |

**Existing reusable patterns leveraged (no new code):**

- L1H Pattern A annotation template (from `.planning/amendments/TRACK-A-PIVOT.md` L37 post-L1H, commit `90718dc`): `(SUPERSEDED 2026-04-25 per quick-260425-kki; ... preserved with full audit trail in 'TRACK-A-FROZEN-NUMBERS.md')`
- L1H Pattern B citation template (from `docs/manuscript/track_a_pivot.md` L82 verbatim): `matched-coverage k2d full-coverage 2026-04-25 re-fire (48/95 vs 51/96 = 1.06× yield)`
- FROZEN-NUMBERS reconciliation-log row template (existing L209–L211 convention)
- L1H 5-gate verification harness (extended here to 7 gates with md5 + byte-identical safety)
