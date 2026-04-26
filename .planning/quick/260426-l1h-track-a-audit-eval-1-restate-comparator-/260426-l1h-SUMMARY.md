---
quick_id: 260426-l1h
slug: track-a-audit-eval-1-restate-comparator
description: "Track A audit Eval-1 — planning-ecosystem comparator restate (k2d 48/95 baseline; SUPERSEDED 12/96 preserved)"
mode: quick
date: 2026-04-26
commits:
  - 90718dc revise(track-a-eval-1) — TRACK-A-PIVOT.md (6 sites)
  - 3339d84 revise(track-a-eval-1) — PROJECT.md (2 sites)
  - 7f75aae revise(track-a-eval-1) — STATE.md L37 (1 current-state site)
status: complete
---

# Quick Task 260426-l1h — Summary

## What landed

Three atomic prose-only commits closing the Track A audit Eval-1 propagation loop into the `.planning/` ecosystem:

| # | Commit | File | Sites | Description |
|---|--------|------|-------|-------------|
| 1 | `90718dc` | `.planning/amendments/TRACK-A-PIVOT.md` | L37, L41, L97, L194, L232, L309 (6 sites) | Strategy-doc restate of abstract draft, parenthetical descriptor, results bullet, Figure 2 spec, frozen-numbers cite item 4, Week 1 checklist completion marker |
| 2 | `3339d84` | `.planning/PROJECT.md` | L60-67 (Stage 2 evidence narrative), L141-150 (Phase 2 spine narrative) | Project-context restate: matched-coverage k2d full-coverage 2026-04-25 re-fire framing in two project-level prose blocks |
| 3 | `7f75aae` | `.planning/STATE.md` | L37 (current-state Stage 2 fire numerics bullet) | State-doc restate of the live Stage 2 fire numerics bullet only; timestamped historical rows preserved verbatim |

**Total: 9 sites restated across 3 files.** Every site honors Carter's framing rule (`feedback_original_research_framing` user memory): the OLD 12/96 / 4.25× baseline is preserved with a `SUPERSEDED 2026-04-25 per quick-260425-kki` audit-trail annotation, not deleted. Anchor language ("previously cited", "matched-coverage k2d full-coverage 2026-04-25 re-fire") used verbatim from `docs/manuscript/track_a_pivot.md` L28 and `TRACK-A-FROZEN-NUMBERS.md` L9-L25.

## Why this task existed

`AUDIT-REVIEW-2026-04-25.md` Eval 1 ("the comparator problem") was the headline-killer audit finding. Quick task `260425-kki` (commits `884eb3d..f0451b0`, 2026-04-25) closed it on the **live publication surfaces** — manuscript at `docs/manuscript/track_a_pivot.md` L28/L82/L138/L216/L295, figure builder at `src/R/figures/fig2_cs_yield.R`, and the canonical frozen-numbers ledger at `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`. But 9 surviving 12/96 / 4.25× citations across 3 `.planning/` files still asserted the SUPERSEDED narrow-validation baseline as if it were the live current-state. An external reader landing in `.planning/amendments/TRACK-A-PIVOT.md` L37 would have seen the OLD abstract; the Figure 2 spec at L194 still asked for "51/96 non-empty vs 12/96 contrast"; the project-context narrative in `PROJECT.md` (L63-67, L143-145) and the Stage 2 numerics block in `STATE.md` (L37) all asserted the SUPERSEDED 4.25× / 12/96 baseline as live current-state.

This task closes that propagation gap. **No live publication surfaces were touched.**

## End-to-end verification (5 gates)

```bash
# Gate 1 — every 12/96 / 4.25 hit in the planning ecosystem is properly framed
grep -nE "12 ?/ ?96|4\.25" .planning/amendments/TRACK-A-PIVOT.md \
  .planning/PROJECT.md .planning/STATE.md
# 17 hits total — all inside SUPERSEDED-annotation, "previously cited",
# "narrow-validation", or timestamped historical context

# Gate 2 — live publication surfaces byte-identical pre vs post
git diff HEAD~3 -- docs/manuscript/track_a_pivot.md \
  src/R/figures/fig2_cs_yield.R \
  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
# 0 lines (PASS)

# Gate 3 — matched-coverage citation pattern present in all 3 planning files
grep -lE "48 ?/ ?95|matched-coverage k2d|1\.06" \
  .planning/amendments/TRACK-A-PIVOT.md \
  .planning/PROJECT.md .planning/STATE.md
# All 3 listed (PASS)

# Gate 4 — forbidden-token sweep on new content
git log -3 --format=%B | grep -ivE "^revise\(" | grep -iE "\b(revision|cleanup|fix-up|mistake|got this wrong|correction|simplified|placeholder|TBD|for now)\b"
# No false positives in new content; the only match is a SUMMARY-block reference
# to the 260425-kki STATE.md row's own description of the supersedure event,
# which is a description of historical fact, not a new claim. (PASS)

# Gate 5 — 3 atomic commits (parallel m2 work commits in interleaved order are disjoint)
git log --oneline --grep="track-a-eval-1"
# 3 commits: 90718dc 3339d84 7f75aae (PASS)
```

**End-to-end test:** A reader searching the planning ecosystem for "12/96" or "4.25" now finds only properly-framed `SUPERSEDED 2026-04-25` audit-trail annotations or timestamped historical-row references. The matched-coverage k2d full-coverage 2026-04-25 baseline (48/95 vs 51/96 = 1.06× yield) is the only live current-state comparator headline across the entire `.planning/` ecosystem; this aligns with `docs/manuscript/track_a_pivot.md` L28 verbatim.

## Historical rows preserved verbatim (audit traceability)

Per Carter's framing rule, timestamped state snapshots must be preserved verbatim — they are audit history, not live claims. The following STATE.md rows / blocks were left unchanged:

- L69 — Recovery trigger narrative (2026-04-20 snapshot: "only 12/96 Phase 1 SuSiE fits have credible sets" — Phase 1 fit-yield diagnostic, distinct from comparator headline)
- L308 — 260424-lpy quick-task log row (Stage 1d narrow-validation Figure 1 build using 12L hardcode)
- L309 — 260424-mqo quick-task log row (Figure number alignment pass, preserves the as-built scalar bar plot description verbatim)
- L319 — 260425-kki quick-task log row (the row that itself describes the 4.25× → 1.06× supersedure event; verbatim preservation is the authoritative audit narrative)
- L320 — 260425-t9j quick-task log row (HLA reclassification, references the 12/96 → 48/95 supersedure pattern as precedent)
- L324 — 260426-04b quick-task log row (H3 figure polish)
- L355 — 2026-04-23 freeze narrative (key-numerics record from initial Stage 2 freeze)

In `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`, the SUPERSEDED 12/96 block at L57-L73 (with strikethroughs and SUPERSEDED 2026-04-25 annotation) and the reconciliation-log row at L208 are also preserved verbatim — these are the canonical audit-trail artifacts that all the new SUPERSEDED-annotation pointers reference.

## Out-of-task observations (not bundled)

1. **STATE.md L40 — "861 hard failures" reference.** Quick task 260425-kki commit `58a5e2d` purged the "1,446" / "861" ghost numerics from `.planning/amendments/TRACK-A-PIVOT.md` (per FROZEN-NUMBERS L188-189 the disk shows 1,242 QTL-coloc failures or 28 trait-pair failures — neither matches 861). STATE.md L40 still cites "861 hard failures in the pairwise trait-pair sweep (to be quantified in Track A frozen-numbers pass)". Left verbatim per disjoint-scope rule (this task is comparator-headline restate, not ghost-numerics purge); flagged here as a clean follow-on candidate for a future `/gsd-quick`.

2. **`fig2_cs_yield.R` header-comment 12/96 / 4.25× references at L12, L15.** These are the kki-installed "Comparator-tightening note" audit-trail comments documenting the supersedure history. They are intentional and correctly framed; not in scope for this task. Left untouched.

3. **`AUDIT-REVIEW-2026-04-25.md` itself** still cites "12/96" / "4.25×" as the audit's original finding (L11, L25, L28, L32, L96). This is correct — the audit document is meant to capture the audit's findings as observed at audit time (2026-04-25 morning, pre-kki). Updating it would erase the audit history. Left untouched per audit-traceability principle.

## Outstanding audit follow-ons (out of scope; recorded in STATE.md row 319 from kki)

- **Audit High-Quality #2** — SH2B3 EUR L=20 re-fit on BMI/HTN/stroke + canonical BMI×HTN / HTN×stroke `coloc.susie` runs (Terminal A LSF compute slot)
- **Eval 2a** — drop / flag non-converged fits in 51/96 headline (needs `/gsd-discuss-phase`)
- **Eval 2c** — PP.H4 posterior intervals for `coloc.susie` (algorithmic; SuSiE-RSS does not store credible-set-level posteriors by default)
- **Eval 3.3** — 28/28 empty `coloc.susie` outputs interpretation (entangled with Eval 2a)
- **PIP-shift / lead-variant rank stability composition analysis** — gated on L=20 re-fit (TODO-COMPOSITION-FOLLOWON marker installed by kki, since dropped per quick-260425-wbf)
- **Pathway-enrichment recompute** on the post-kki + post-t9j signal set — separate `/gsd-quick` slug
- **Submission-venue decision** — 1.06× framing may shift target *Genome Medicine* → *Bioinformatics* Applications Note (`/gsd-discuss-phase` decision)

## Files changed

| Type | Path | Lines changed |
|------|------|---------------|
| edit | `.planning/amendments/TRACK-A-PIVOT.md` | +6 / -6 |
| edit | `.planning/PROJECT.md` | +17 / -9 |
| edit | `.planning/STATE.md` | +5 / -5 (L37 only; Quick Tasks Completed table append + Last activity update land in final docs commit) |
| new | `.planning/quick/260426-l1h-.../260426-l1h-PLAN.md` | new file |
| new | `.planning/quick/260426-l1h-.../260426-l1h-SUMMARY.md` | new file (this) |

Live publication surfaces (`docs/manuscript/track_a_pivot.md`, `src/R/figures/fig2_cs_yield.R`, `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`, `results/`, `results_identity_ld/`): byte-identical pre vs post.

## Source plan

[/home/ckclinto/.claude/plans/track-a-audit-eval-1-restate-comparator-cuddly-pond.md](/home/ckclinto/.claude/plans/track-a-audit-eval-1-restate-comparator-cuddly-pond.md) (approved by Carter via ExitPlanMode 2026-04-26).
