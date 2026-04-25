---
phase: quick-260425-ie0
plan: 01
type: execute
wave: 1
status: complete
completed: 2026-04-25
commit: 2d5f710
requirements:
  - TRACK-A-FIG3-CAPTION
files_modified:
  - docs/manuscript/track_a_pivot.md
---

# Quick Task 260425-ie0 — Track A Fig 3 Caption Integration Summary

## One-liner

Replaced the pre-build Fig 3 caption (authored before the figure was built) at `docs/manuscript/track_a_pivot.md` L295 with honest-data-aligned text derived directly from quick-260425-1vy SUMMARY (B's commit `105484d`) and the as-built `fig3_sh2b3_eur_collapse_forest.R` `plot_annotation` block — single-line atomic replacement; surrounding L289-L301 byte-identical; Stage 2 source-of-truth tsvs unchanged.

## Atomic source commit

| Field | Value |
|---|---|
| Commit SHA | `2d5f710` |
| Branch | `main` (no worktree per CLAUDE.md GPFS constraint) |
| Files changed | 1 (`docs/manuscript/track_a_pivot.md`) |
| Insertions / deletions | 1 / 1 |
| Diff hunk | `@@ -292,7 +292,7 @@` (single-line replacement at L295) |
| Pre-edit HEAD | `8e62e26` |
| Post-edit HEAD | `2d5f710` |
| Pre-commit hooks | Not skipped |

## Verbatim copy of the new L295 caption

```
**Figure 3.** Structural credible-set-yield collapse at *SH2B3* 12q24 EUR under real-LD re-analysis. Two-panel composite. **(A)** Per-trait SuSiE-RSS credible-set yield at the SH2B3_12q24 EUR locus across five EUR traits (asthma, BMI, hypertension, stroke, t2d) under identity-LD fallback (gray, leftward bars; k2d re-fire 2026-04-25, sourced from `results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json`) versus real 1000 Genomes Phase 3 EUR LD (blue, rightward bars; Stage 2 production fire 2026-04-22, sourced from `results/fine_mapping/finemap_summary.tsv`). Disk-verified per-trait yields (identity-LD → real-LD): asthma 0 → 1 (status=ok), BMI 3 → 8 (non_converged), hypertension 10 → 4 (non_converged), stroke 10 → 2 (non_converged), t2d 2 → 9 (status=ok); four of five EUR traits at SH2B3 are non_converged under real-LD whereas all five converged under identity-LD. **(B)** Locked PP.H4 narrative side annotations (cited verbatim from `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` lines 51 and 79): BMI × hypertension and hypertension × stroke each carried identity-LD coloc.abf PP.H4 = 1.00 at canonical leads → both pairs are untestable under real-LD (absent from the Stage 2 coloc.susie manifest, consistent with credible-set collapse); asthma × t2d is the sole canonical SH2B3 EUR pair on disk under real-LD with coloc.susie status = no_signal and n_cs_a = 0; *ATXN2* / Adrenal_Gland real-LD QTL coloc PP.H4 = 0.0517 (the sole quantitative real-LD PP.H4 number at SH2B3 EUR; below the Tier C 0.5 threshold). The figure displays no 95% confidence intervals on PP.H4 — PP.H4 is a posterior probability and the Stage 2 production manifest stores no posterior intervals; locked narrative numbers are surfaced as side annotations only. The figure's argument is structural credible-set-yield collapse plus non-convergence under real-LD, not a per-signal interval estimate.
```

Word count: **258** (within hard 100-280 range; surrounding rhythm is Fig 1B ~370 / Fig 2 ~80 / Fig 5 ~140, so 258 sits between Fig 1B and Fig 5; 14 must-have tokens require this density).

## Source-of-truth provenance

Caption text derived directly from quick-260425-1vy SUMMARY (commit `105484d`):

| Anchor in caption | Source SUMMARY line range |
|---|---|
| Per-trait CS counts (asthma 0→1 ok / BMI 3→8 non_converged / hypertension 10→4 non_converged / stroke 10→2 non_converged / t2d 2→9 ok) | quick-260425-1vy SUMMARY.md lines 45-51 (B's disk-verified per-trait CS counts table) |
| Locked PP.H4 narrative (BMI×HTN id-LD=1.00 untestable; HTN×stroke id-LD=1.00 untestable; asthma×t2d real-LD no_signal n_cs_a=0; ATXN2/Adrenal_Gland real-LD PP.H4=0.0517) | quick-260425-1vy SUMMARY.md lines 60-65 (B's locked PP.H4 narrative table) |
| Honest-framing lock ("no 95% CI on PP.H4 — PP.H4 is a posterior probability and the Stage 2 production manifest stores no posterior intervals") | quick-260425-1vy SUMMARY.md lines 67-76 (B's honest-framing lock) |
| Source-of-truth file paths (real-LD `results/fine_mapping/finemap_summary.tsv`; identity-LD `results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json`) | quick-260425-1vy SUMMARY.md lines 54-56 |
| Locked-scalar cross-reference | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` lines 51 + 79 (BMI×HTN PP.H4=1.00 narrative; ATXN2/Adrenal_Gland PP.H4=0.0517) |
| Caption rhythm and tone | `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` lines 351-366 (in-figure `plot_annotation(caption = ...)` block) |

No numbers were recomputed; every quantitative value in the caption is cited verbatim from one of the four locked sources above.

## md5 manifest — Stage 2 source-of-truth tsvs (pre vs post-edit; byte-identical)

| File | Pre md5 | Post md5 | Status |
|---|---|---|---|
| `results/multitrait/coloc_summary.tsv` | `5fa3c4004970c5da711d05947cb1f7d2` | `5fa3c4004970c5da711d05947cb1f7d2` | identical |
| `results/fine_mapping/finemap_summary.tsv` | `8c3e04a202a919d94bd34a3c1d5146a2` | `8c3e04a202a919d94bd34a3c1d5146a2` | identical |
| `results/fine_mapping/finemap_summary_augmented.tsv` | `243bf4dd14bc2c7b67317f5587c74e1d` | `243bf4dd14bc2c7b67317f5587c74e1d` | identical |
| `results/qtl_coloc/tier_assignments.tsv` (4th tsv; present on disk) | `17ff46dbbfe78dd537d6b9bff7f3ae67` | (snapshot pre only — not part of must_haves) | preserved |

`diff /tmp/260425-ie0-stage2-md5-pre.txt /tmp/260425-ie0-stage2-md5-post.txt` — empty diff (zero changes to Stage 2 tsvs).

## results_identity_ld/ output preservation

The k2d identity-LD re-fire output at `results_identity_ld/` (95 JSONs + finemap_manifest.tsv landed 2026-04-25 by `260424-k2d`) is **untouched on disk**. The data files Fig 3 sources at runtime (`results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json`) are byte-identical pre vs post.

**Status drift note vs PLAN.md must_have #10:** The plan expected `git status --short` to show `?? results_identity_ld/` both pre and post-commit. Pre-commit `git status` actually showed:

```
 M .claude/settings.json
 M .gitignore
 M .planning/config.json
?? .claude/scheduled_tasks.lock
?? .planning/quick/260425-ie0-route-a-track-a-fig-3-caption-integratio/
?? .planning/quick/260425-ieh-results-identity-ld-tracking-decision/
```

The `?? results_identity_ld/` line is **absent** because a parallel quick task (`260425-ieh-results-identity-ld-tracking-decision`) updated `.gitignore` line 80 to add `results_identity_ld/`. That decision (whether to git-track or git-ignore the k2d output) was deliberately scoped to that task per STATE.md L27 deferral. The `M .gitignore` entry in `git status` is from `260425-ieh`, not from this task. **Substantive must_have #10 invariant — "k2d output not git-added in this commit" — holds**: this commit's diff scope is exactly 1 file (`docs/manuscript/track_a_pivot.md`); `results_identity_ld/` is neither staged nor committed by `260425-ie0`.

## Greppable check outcomes — new L295 only

### Required tokens (each grep -c >= 1)

| Token | Count |
|---|---|
| `non_converged` | 1 |
| `0.0517` | 1 |
| `results_identity_ld/fine_mapping/susie` | 1 |
| `\*SH2B3\*` | 1 |
| `\*ATXN2\*` | 1 |
| `TRACK-A-FROZEN-NUMBERS` | 1 |
| `finemap_summary.tsv` | 1 |

### Forbidden tokens (each grep -c == 0)

| Pattern | Count |
|---|---|
| `Survival forest \| survival forest plot` | 0 |
| `95% CI \| 95% uncertainty \| credible interval` | 0 |
| `outcome classification colored \| ordered by PP\.H4_identity \| 50 curated regions \| hub-redistribution` | 0 |
| B's inherited regex `revision\|cleanup\|fix-up\|machine learning\|\bML-based\b\|thrifty\|evolutionary medicine\|placeholder\|\bv1\b\|simplified\|\bTBD\b\|for now\|static` | 0 |
| `\bML\b` (per orchestrator constraint) | 0 |

### Caption length

| Metric | Value | Range |
|---|---|---|
| `wc -w` on new L295 | 258 | 100-280 (hard); 150-200 (target — exceeded; rationale in §Word-count rationale below) |

## Surrounding caption-block byte-identity (L289-L294 + L296-L301)

`diff` of pre-snapshot vs post-edit on lines L289-L294 + L296-L301: **empty diff** — surrounding lines byte-identical. Total file line count `355` pre and post (also empty diff).

The diff hunk header confirms single-line scope:

```
@@ -292,7 +292,7 @@ Work currently underway at the ASHES Laboratory is implementing whole-genome-seq
```

`git diff HEAD~1 HEAD --name-only | wc -l` = `1`.

## Forbidden-framing greppable check — new L295, SUMMARY.md narrative, commit message

The forbidden-token regex (per orchestrator constraint and B's inherited guardrail) was applied to all three artifacts:

1. **New L295 caption text — 0 matches** (the load-bearing artifact).
2. **This SUMMARY.md narrative prose — 0 matches outside regex-quoting context.** The literal token strings appear only inside backticks where the regex itself is documented (e.g., line 106 table row + line 129 prose citing the regex pattern); these are documentary citations of the regex, not narrative claims about the new artifact. Narrative-prose references to the prior L295 use B's stricter convention "pre-build caption" / "authored before the figure was built" rather than the bare forbidden token.
3. **Commit message body — 1 occurrence** of the forbidden token "placeholder" inside the section header phrase "Pre-build placeholder removed (factually wrong vs as-built figure)" identifying what was removed. This is documentary identification of the prior text being replaced, paralleling the precedent in `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` Reconciliation log (where prior numbers are explicitly identified before being superseded). The new L295 caption text itself contains zero forbidden tokens. Flagging for orchestrator review; if strict zero-occurrence-anywhere applies, the commit message could be amended in a follow-on commit, but per project rule "NEVER amend an existing commit unless the user explicitly requests a git amend," no amend is performed here.

## Word-count rationale

The plan target was 150-200 words (hard range 100-280). The replacement landed at 258 words — within the hard range but above the target. Rationale: the must_haves require **14 distinct anchor tokens** (per-trait CS table 5 entries × 3 fields each = 15 numeric anchors; locked PP.H4 narrative 4 entries; honest-framing lock 1 sentence; 2 file paths; 1 cross-reference; 7 italic-symbol + grep-pattern requirements). Compressing this to 150-200 words while preserving all 14 anchors verbatim plus the surrounding declarative-prose rhythm of L291 / L293 / L297 / L299 was not achievable without dropping at least one anchor or collapsing the **(A)** / **(B)** panel structure. 258 words preserves all 14 anchors and matches the dense panel-by-panel rhythm of L291 Fig 1B (~370 words) more closely than the terse Fig 2 rhythm. Acceptable per hard range.

## Handoff — Fig 1A caption integration (next /gsd-quick)

Per the constraint "Fig 1A caption discrepancy is OUT-OF-SCOPE — explicitly handoff in SUMMARY.md as next /gsd-quick task; do NOT touch L291 in this commit", the following is the deferred-with-handoff scope:

**Discrepancy at `docs/manuscript/track_a_pivot.md` L291 (Figure 1):**
- Current L291 panel-A description: "(A) Scatter of PP.H4_identity (x-axis) vs PP.H4_real (y-axis), one point per admissible region × trait-pair present in both runs; diagonal reference line indicates no inflation."
- As-built `src/R/figures/fig1a_pipeline_schematic.R` (commit `105484d`): renders a **5-panel pipeline schematic** (geometric primitives only; 2-row 3+2 layout per quick-260425-1vy SUMMARY deviation #2), NOT a scatter.
- Resolution path: Either (i) update L291 panel-A description to match the as-built 5-panel pipeline schematic, OR (ii) re-build a Fig 1A scatter to match the existing L291 description, OR (iii) split the current Fig 1 into a renumbered figure series. Decision is the next quick task's scope.
- Source documents for the next task: quick-260425-1vy SUMMARY.md "Handoff — caption integration (separate /gsd-quick)" section + `src/R/figures/fig1a_pipeline_schematic.R` header comment + `.planning/amendments/TRACK-A-PIVOT.md` §5 5-figure roster.
- L291 was **not touched** by this `260425-ie0` commit; the byte-identity diff on L289-L294 + L296-L301 confirms this.

## Forbidden-framing greppable summary

Across the new L295 caption text and this SUMMARY.md narrative prose, zero forbidden-framing tokens land outside of regex-quoting context (the regex itself is cited verbatim once for documentation; that backtick-quoted citation is not a narrative claim). One occurrence of the forbidden token appears in the commit message body identifying what was replaced; rationale and orchestrator-review flag are in §"Forbidden-framing greppable check" above. Original-research framing per `feedback_original_research_framing` user memory is preserved: Fig 3 is hypothesis-driven structural-collapse evidence at SH2B3 12q24 EUR.

## Self-Check: PASSED

Files verified to exist:
- `docs/manuscript/track_a_pivot.md`: FOUND (L295 contains new caption; surrounding L289-L301 byte-identical pre vs post)
- This SUMMARY.md: FOUND (you are reading it)

Commit verified to exist:
- `2d5f710 docs(quick-260425-ie0): Track A Fig 3 caption — [pre-build text replaced] at track_a_pivot.md L295` (commit subject as authored on disk; FOUND in `git log --oneline -1`)

Stage 2 tsvs verified byte-identical pre vs post (3/3 md5 match).

`git diff HEAD~1 HEAD --name-only` = exactly 1 file = `docs/manuscript/track_a_pivot.md`.

All 14 caption-content + must_have gates PASS (7 required tokens >=1; 4 forbidden-token classes ==0; word count in 100-280; surrounding lines byte-identical; total line count unchanged; Stage 2 md5 identical; commit-message stem matches `quick-260425-ie0` + `Fig 3 caption`; one-file-changed in HEAD).
