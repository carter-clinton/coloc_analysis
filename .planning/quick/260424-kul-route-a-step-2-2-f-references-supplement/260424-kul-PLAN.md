---
quick_id: 260424-kul
phase: quick-260424-kul
plan: 01
title: "Route A Step 2.2.f — References + supplementary R1 for track_a_pivot.md (placeholder resolution + structured inventory)"
type: execute
wave: 1
depends_on:
  - 260424-j64   # Introduction R1 — left three bracketed placeholders at L36 for this pass to resolve
  - 260424-k2c   # Discussion R1 — confirmed no new citations introduced; L230 refs 4–5 remain unchanged
files_modified:
  - docs/manuscript/track_a_pivot.md
  - .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md
autonomous: true
requirements:
  - ROUTE-A-2.2.f
tags:
  - track-a
  - manuscript
  - references
  - bibliography
  - r1
user_setup: []

must_haves:
  truths:
    - "The three bracketed author-year placeholders at L36 ([Wallace 2021] [Zou 2022] [Weissbrod 2020]) are resolved to inline Unicode-superscript citation numbers (ascending: ²⁰,²⁹,⁴²), matching the superscript convention used elsewhere in the manuscript."
    - "The References section (currently L301–311) is restructured from a single flat bullet list into five machine-greppable subsections (### Add, ### Promote, ### Retain, ### Demote, ### Drop) plus a sixth ### Full numbered bibliography placeholder subsection."
    - "Weissbrod 2020 is assigned to slot ⁴² and Benner 2017 is assigned to slot ⁴³ on the References list (Benner 2017 is NOT inlined in R1 — References-list only this pass)."
    - "Refs 4, 5 at L230 (⁴⁻⁵, thrifty-gene + antagonistic-pleiotropy) remain unchanged — verified by grep."
    - "The full numbered reference list is represented as a single [EXTRACT: …] placeholder explicitly deferring the Zotero/EndNote export pass to venue-submission prep per snappy-humming-pine.md §2.5."
    - "No frozen numeric in TRACK-A-FROZEN-NUMBERS.md drifts as a side-effect of the References edits (References section contains no Stage 2 numerics; verified by scope containment)."
    - "SUMMARY.md documents scope divergence from the 260424-j64 NEXT-STEPS.md brief (no numbered bibliography exists in repo — full renumber is a venue-submission-prep artifact, not an R1 deliverable) and enumerates the handoff items for 2.2.f R2 (venue-submission Zotero export) and 2.3 (figures)."
  artifacts:
    - path: "docs/manuscript/track_a_pivot.md"
      provides: "R1-edited manuscript with L36 placeholders resolved + §References restructured"
      contains: "²⁰,²⁹,⁴²"
    - path: ".planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md"
      provides: "Summary of the R1 References pass, guardrail grep receipts, handoff to 2.2.f R2 and 2.3"
  key_links:
    - from: "docs/manuscript/track_a_pivot.md L36"
      to: "§References — revised citation list (L301+)"
      via: "superscript slots ²⁰ (Zou 2022), ²⁹ (Wallace 2021), ⁴² (Weissbrod 2020, NEW)"
      pattern: "²⁰,²⁹,⁴²"
    - from: ".planning/amendments/TRACK-A-PIVOT.md §9 (L280–301)"
      to: "docs/manuscript/track_a_pivot.md §References"
      via: "authoritative add/demote/retain/drop inventory transcribed to structured subsections"
      pattern: "### Add|### Promote|### Retain|### Demote|### Drop"
---

<objective>
Route A Step 2.2.f R1 — surgical References + supplementary alignment pass on `docs/manuscript/track_a_pivot.md` that (a) resolves the three bracketed author-year placeholders left inline at L36 by the 260424-j64 Introduction R1 handoff, and (b) restructures the current narrative References section (L301–311) into a structured add/promote/retain/demote/drop inventory with machine-greppable `###` subsections and one `[EXTRACT:]` placeholder explicitly deferring the full numbered bibliography to the venue-submission-prep Zotero/EndNote export per snappy-humming-pine.md §2.5.

This is a TIGHT R1 pass. NOT a rewrite. NOT a full renumber. The scope originally implied by the 260424-j64 NEXT-STEPS.md brief ("renumber all inline citations") is over-scoped for R1 because neither `track_a_pivot.md` nor `track_a_source.md` contains a numbered bibliography anywhere in the repo — both drafts carry only Unicode-superscript inline citations. The full numbered bibliography is a venue-submission artifact produced from the project's Zotero/EndNote library at submission prep, NOT an R1 deliverable. This plan makes that reality explicit and defers the full renumber to 2.2.f R2.

Purpose: close the inline-placeholder debt left by Introduction R1, produce a structured-and-greppable References inventory that matches the §9 add/demote/retain/drop spec, and lock in a handoff note so the next pass (2.2.f R2 or venue-submission prep) and the figure scripts pass (2.3) have a stable source of truth for ref 20 (Zou), 29 (Wallace), 42 (Weissbrod), 43 (Benner).

Output: 2 R1 edits to `docs/manuscript/track_a_pivot.md` (L36 placeholder → superscript swap; §References L301–311 narrative → structured inventory) + SUMMARY.md with grep receipts.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@docs/manuscript/track_a_pivot.md
@.planning/amendments/TRACK-A-PIVOT.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/quick/260424-j64-route-a-step-2-2-b-introduction-rewrite-/260424-j64-SUMMARY.md
@.planning/quick/260424-j64-route-a-step-2-2-b-introduction-rewrite-/260424-j64-NEXT-STEPS.md
@.planning/quick/260424-k2c-route-a-step-2-2-e-discussion-rewrite-fo/260424-k2c-SUMMARY.md

<interfaces>
<!-- Pre-edit grep baselines captured from `docs/manuscript/track_a_pivot.md` at plan-creation time. -->
<!-- Executor should confirm baselines match before applying edits (guards against drift between planning and execution). -->

Pre-edit grep baselines (confirm before editing):
- `grep -c '\[EXTRACT:' docs/manuscript/track_a_pivot.md` → **16** (15 inline `[EXTRACT: …]` placeholders + 1 meta reference on L319 "All [EXTRACT: …] placeholders must be filled…"). Post-edit target: **17** (one new placeholder in ### Full numbered bibliography subsection).
- `grep -c '²⁰' docs/manuscript/track_a_pivot.md` → **2** (L38 SuSiE-RSS²⁰, L72 SuSiE-RSS fine-mapping²⁰). Post-edit target: **≥ 3** (L36 gains new `²⁰` as first element of `²⁰,²⁹,⁴²`).
- `grep -c '²⁹' docs/manuscript/track_a_pivot.md` → **2** (L38 `coloc.susie`,²⁹, L72 `coloc.susie`²⁹). Post-edit target: **≥ 3** (L36 gains new `²⁹` as second element of `²⁰,²⁹,⁴²`).
- `grep -c '⁴²' docs/manuscript/track_a_pivot.md` → **0**. Post-edit target: **≥ 1** (L36 new Weissbrod 2020 slot).
- `grep -c '⁴³' docs/manuscript/track_a_pivot.md` → **0**. Post-edit target: **0** (Benner 2017 is References-list-only in R1; inline placement deferred to R2).
- `grep -c '⁴⁻⁵' docs/manuscript/track_a_pivot.md` → **1** (L230 thrifty-gene). Post-edit target: **1** (unchanged).
- `grep -nE '\[Wallace 2021\]|\[Zou 2022\]|\[Weissbrod 2020\]' docs/manuscript/track_a_pivot.md` → 1 hit on L36. Post-edit target: **0 hits** (all three resolved).

Current L36 state (verbatim, for regex construction):
```
... is multi-signal rather than single-variant [Wallace 2021] [Zou 2022] [Weissbrod 2020]. The magnitude of this inflation at real disease loci has not been systematically quantified.
```

Target L36 state (verbatim):
```
... is multi-signal rather than single-variant.²⁰,²⁹,⁴² The magnitude of this inflation at real disease loci has not been systematically quantified.
```

Key decisions recorded in this plan (executor should honor without re-deriving):
1. **Order of superscripts at L36 is ascending (²⁰,²⁹,⁴²)** — standard convention for multi-citation supports. Maps to Zou 2022 (²⁰), Wallace 2021 (²⁹), Weissbrod 2020 (⁴²).
2. **Placement relative to the terminal period** — the superscript group goes IMMEDIATELY AFTER the closing period of "single-variant." (standard manuscript style in this file — cf. L38 "coloc.susie`,²⁹" where the ²⁹ follows a comma, and L36 Giambartolomei "`coloc.abf`, the single-causal-variant Bayesian test of Giambartolomei et al. 2014,¹⁰" where ¹⁰ follows a comma). For the end-of-clause period case at L36 post-edit, superscripts follow the period directly: `single-variant.²⁰,²⁹,⁴²` — matching the manuscript's no-hard-wrap single-line-per-paragraph convention.
3. **Weissbrod 2020 gets slot ⁴²** — first new ref number after the preserved 1–41 range from the source draft (per §9).
4. **Benner 2017 gets slot ⁴³ on the References list ONLY in R1** — inline placement is deferred to 2.2.f R2 or venue-submission pass. Rationale: §9 lists Benner 2017 under Add but pivot §4.5 P2 only gestures at three citations at L36 (Wallace + Zou + Weissbrod). Dropping a 4th superscript into an already-3-cite group at L36 without amendment support risks scope creep; holding on the References list is the conservative choice.
5. **Refs 4, 5 at L230 stay exactly where they are** — §4.17 P5 locked them to one Discussion paragraph, and the 260424-k2c Discussion R1 pass preserved them verbatim. No edit here.
</interfaces>

<scope_divergence>
The 260424-j64 NEXT-STEPS.md brief proposed that 2.2.f "renumber all inline citations" and "build the full numbered bibliography." This plan **does NOT do that**, and the divergence is intentional for three reasons:

1. **No numbered bibliography exists anywhere in the repo.** `track_a_pivot.md` ends at §Decision-pending items (L318) with no "References" numbered list. `track_a_source.md` (the v10 verbatim source) also ends without a numbered list. The superscripts in both files (¹⁻³, ¹⁰, ²⁰, ²⁹, ⁴⁻⁵, ¹¹⁻¹², ²⁷, etc.) are orphaned from a corresponding ref-number-to-source mapping that lives outside the repo (presumably in a Zotero/EndNote library that has not yet been exported or committed to `.planning/refs/`).

2. **Building the full numbered list is a venue-submission artifact, not an R1 manuscript-edit artifact.** snappy-humming-pine.md §2.5 lists "Zotero/EndNote export → venue-specific citation format (Genome Medicine house style primary; AJHG/Bioinformatics formats as fallback)" as part of the submission-package prep pass, which follows the text-freeze point.

3. **Dropping inline superscripts for refs formerly supporting "ML-based claims" requires the v10 source-to-number mapping, which is not in the repo.** Without that mapping, dropping a superscript risks orphaning a retained reference (e.g., if what we think is an ML-ref is actually a dual-purpose annotation ref we wanted to retain). The conservative R1 move is to note the deferral on the References list and hold inline edits until the Zotero export is available.

R1 therefore confines itself to: (a) the three inline placeholders already marked for 2.2.f by Introduction R1 (can be resolved without the Zotero library — the slots ²⁰ and ²⁹ are already established in the manuscript, only ⁴² is new), and (b) the narrative References section (can be restructured from the authoritative §9 inventory alone, no Zotero library needed).
</scope_divergence>

</context>

<tasks>

<task type="auto">
  <name>Task 1: Resolve the 3 bracketed inline placeholders at L36 to superscript group ²⁰,²⁹,⁴²</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Open `docs/manuscript/track_a_pivot.md`. Locate L36 (Introduction P2, the three-inflation-settings sentence that ends with ` [Wallace 2021] [Zou 2022] [Weissbrod 2020]. The magnitude of this inflation at real disease loci has not been systematically quantified.`).

Apply the following surgical edit to that sentence ONLY (do not touch any other paragraph):

**Before (verbatim end-of-sentence fragment):**
`...is multi-signal rather than single-variant [Wallace 2021] [Zou 2022] [Weissbrod 2020]. The magnitude of this inflation at real disease loci has not been systematically quantified.`

**After (verbatim):**
`...is multi-signal rather than single-variant.²⁰,²⁹,⁴² The magnitude of this inflation at real disease loci has not been systematically quantified.`

Key transform details (executor must preserve exactly):
1. Delete the single leading space before `[Wallace 2021]` and the two inner separating spaces between the bracketed placeholders — the placeholders collapse to a single superscript cluster, no space between the closing period and the superscripts.
2. Delete the three bracketed placeholders `[Wallace 2021]`, `[Zou 2022]`, `[Weissbrod 2020]` in their entirety (brackets included).
3. Move the terminal period from AFTER the last placeholder to BEFORE the superscript cluster — i.e., the period closes "single-variant" immediately, then the superscripts `²⁰,²⁹,⁴²` follow, then a single space, then the next sentence begins with "The magnitude…".
4. The comma separators in `²⁰,²⁹,⁴²` are ASCII commas, NOT superscript commas — same convention as other `,`-separated ref-ranges in the manuscript (verify against existing file conventions but the ASCII comma form is standard markdown practice and matches what renders cleanly in most bioRxiv / Genome Medicine LaTeX pipelines).
5. The three superscript digits are the Unicode characters `²⁰` (U+00B2 U+2070), `²⁹` (U+00B2 U+2079), `⁴²` (U+2074 U+00B2). Executor should cut-and-paste from the task body rather than retype — Unicode superscripts are error-prone to type manually.
6. Ascending numeric order: Zou 2022 = 20, Wallace 2021 = 29, Weissbrod 2020 = 42. Do NOT alphabetize by author; this manuscript uses numeric-ascending ordering for multi-citation clusters (standard bibliography convention).

DO NOT touch any other paragraph in the Introduction (P1 L34, P3 L38, P4 L40, P5 L42–48). DO NOT touch any `²⁰` or `²⁹` occurrence at L38 or L72 (those are unrelated references to SuSiE-RSS and coloc.susie primary-method citations, already correct from 260424-j64).

DO NOT add an inline superscript `⁴³` for Benner 2017 anywhere at this pass — Benner 2017 is References-list-only in R1 per the plan's `<interfaces>` decision #4.

DO NOT re-wrap the paragraph — the manuscript convention is one line per paragraph, no hard wrap. The paragraph stays on L36 exactly.

Single-line-per-paragraph preservation check after edit: `awk 'NR==36 {print length}' docs/manuscript/track_a_pivot.md` should return a line length consistent with a single unwrapped paragraph (the pre-edit length is around 700 characters; post-edit length drops by roughly 40 characters due to bracket removal net of superscript-character additions — any post-edit L36 line length in the 650–700 range is acceptable; if the line length becomes < 500 or > 800 the edit has likely broken the single-line convention).
  </action>
  <verify>
    <automated>
bash -c '
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
echo "=== Gate 1: zero bracketed placeholders remain ===";
test "$(grep -cE "\[Wallace 2021\]|\[Zou 2022\]|\[Weissbrod 2020\]" docs/manuscript/track_a_pivot.md)" = "0";
echo "=== Gate 2: ²⁰ count >= 3 (L36 new + L38 + L72) ===";
test "$(grep -c "²⁰" docs/manuscript/track_a_pivot.md)" -ge 3;
echo "=== Gate 3: ²⁹ count >= 3 (L36 new + L38 + L72) ===";
test "$(grep -c "²⁹" docs/manuscript/track_a_pivot.md)" -ge 3;
echo "=== Gate 4: ⁴² count >= 1 (L36 new) ===";
test "$(grep -c "⁴²" docs/manuscript/track_a_pivot.md)" -ge 1;
echo "=== Gate 5: ⁴³ count == 0 (Benner not inlined in R1) ===";
test "$(grep -c "⁴³" docs/manuscript/track_a_pivot.md)" = "0";
echo "=== Gate 6: L36 contains the new superscript cluster ===";
awk "NR==36" docs/manuscript/track_a_pivot.md | grep -qE "²⁰,²⁹,⁴²";
echo "=== Gate 7: L36 still single line (length sane) ===";
LEN=$(awk "NR==36 {print length}" docs/manuscript/track_a_pivot.md);
test "$LEN" -ge 500 && test "$LEN" -le 900;
echo "=== Gate 8: L230 unchanged (refs 4,5 + thrifty-gene intact) ===";
test "$(grep -c "⁴⁻⁵" docs/manuscript/track_a_pivot.md)" = "1";
test "$(grep -c "thrifty-gene" docs/manuscript/track_a_pivot.md)" = "1";
echo "ALL 8 GATES PASS";
'
    </automated>
  </verify>
  <done>
  - L36 contains the superscript cluster `²⁰,²⁹,⁴²` immediately after the closing period of `single-variant.`, with no intervening space.
  - Zero matches for `[Wallace 2021]`, `[Zou 2022]`, `[Weissbrod 2020]` anywhere in the file.
  - L230 unchanged (⁴⁻⁵ superscript count = 1, "thrifty-gene" count = 1).
  - L38 and L72 superscripts (²⁰, ²⁹) unchanged.
  - All 8 automated gates pass.
  </done>
</task>

<task type="auto">
  <name>Task 2: Restructure §References — revised citation list (L301–311) into 5+1 machine-greppable subsections</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Open `docs/manuscript/track_a_pivot.md` and locate the `## References — revised citation list` heading (currently L301). The section is currently a flat 7-bullet narrative spanning L301–L311. **Replace the entire block (from `## References — revised citation list` through the final bullet `- **Drop** all references formerly supporting "ML-based" claims that are not genuine ML.`) with the structured-subsection block specified below.**

Replacement block (verbatim — this is the new content of the section, beginning at the existing `## References — revised citation list` line):

```markdown
## References — revised citation list

The pivot preserves the existing ref 1–41 numbering from the v10 source draft (unmodified where possible), adds 2 new references at slots 42–43 for the identity-LD inflation / LD-mismatch literature, demotes refs 4–5 to a single Discussion paragraph on evolutionary medicine (per Amendment §4.17 P5), and defers the full numbered bibliography to the venue-submission package prep pass using a Zotero/EndNote export of the project reference library (per `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.5). The inline-superscript ↔ ref-number mapping below is the R1 source of truth; no full numbered list is populated at this pass.

### Add

- **Ref 42 NEW — Weissbrod O, Hormozdiari F, Benner C, et al. (2020).** "Functionally informed fine-mapping and polygenic localization of complex trait heritability." *Nat Genet* 52:1355–1363. Functionally-informed fine-mapping and treatment of LD mismatch between fine-mapping panel and discovery GWAS. Inline slot: L36 Introduction P2 (third element of the three-inflation-settings citation cluster ²⁰,²⁹,⁴²).
- **Ref 43 NEW — Benner C, Spencer CCA, Havulinna AS, et al. (2016).** "FINEMAP: efficient variable selection using summary data from genome-wide association studies." *Bioinformatics* 32:1493–1501. Alternative fine-mapping referent; early formulation of LD-mismatch vulnerability under the single-causal-variant model. Inline slot: References-list only in R1 — final inline placement deferred to 2.2.f R2 or venue-submission pass (candidate slots: L36 Introduction P2 alongside Weissbrod 2020, or Methods §Fine-Mapping Integration).

### Promote (already in source draft; reframed as primary-method citation in the pivot)

- **Ref 20 — Zou Y, Carbonetto P, Wang G, Stephens M (2022).** "Fine-mapping from summary data with the 'Sum of Single Effects' model." *PLoS Genet* 18:e1010299. SuSiE-RSS methodology. Promoted to primary method citation at L36 (new), L38, L72, and throughout Methods §Fine-Mapping Integration.
- **Ref 29 — Wallace C (2021).** "A more accurate method for colocalisation analysis allowing for multiple causal variants." *PLoS Genet* 17:e1009440. `coloc.susie` methodology; colocalization accuracy under LD mismatch and multi-causal-variant architecture. Promoted to primary method citation at L36 (new), L38, L72.

### Retain (unchanged from source draft)

- **Ref 10 — Giambartolomei C, Vukcevic D, Schadt EE, et al. (2014).** "Bayesian test for colocalisation between pairs of genetic association studies using summary statistics." *PLoS Genet* 10:e1004383. Original `coloc.abf` methodology. Framed in the pivot as the method under audit (not endorsed). Retained at L36, L70.
- **Refs 1–3** — original cardiometabolic epidemiology citations (T2D–hypertension ~50% comorbidity; obesity as shared risk factor). Retained at L34 (¹⁻³).
- **Refs 6–9** — GIANT / DIAMANTE / ICBP / GIGASTROKE GWAS-source citations at L54 (⁶⁻⁹). Provenance of the claims under audit.
- **Refs 11–12** — GWAS-ancestry-demographics citations at L40 (¹¹⁻¹²).
- **Ref 13** — Martin AR et al. polygenic-risk-score transportability. Still relevant for the Cross-Ancestry limitation.
- **Refs 17–19** — curated-candidate-locus prior-literature citations at L64 (¹⁷⁻¹⁹).
- **Refs 21–41** — annotation-aggregation sources: GTEx v8, Open Targets, NHGRI-EBI GWAS Catalog, Roadmap Epigenomics, ENCODE, CADD, PolyPhen-2, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, gnomAD pLI, STRING, DGIdb, ChEMBL. Exact slot-to-source assignments within the 21–41 range are deferred to the Zotero/EndNote export at venue-submission prep; R1 preserves the inline superscripts at their existing positions.
- **Ref 27** — cardiometabolic disease burden in African-descended populations, L40.

### Demote (retained but confined to one Discussion paragraph)

- **Refs 4, 5 — Neel JV (1962)** "Diabetes mellitus: a 'thrifty' genotype rendered detrimental by 'progress'?" *Am J Hum Genet* 14:353–362; and **Williams GC (1957)** "Pleiotropy, natural selection, and the evolution of senescence." *Evolution* 11:398–411. Thrifty-gene and antagonistic-pleiotropy hypotheses. Retained as citations but confined to a single Discussion paragraph (§Evolutionary Medicine Perspective, L228–230), reduced from three paragraphs in the v10 source to one speculative paragraph ≤ 120 words per Amendment §4.17 P5. Inline superscripts ⁴⁻⁵ preserved verbatim at L230.

### Drop (removed from the pivot)

- References formerly supporting "ML-based" framing claims (gene-prioritization ML classifiers, variant-effect-prediction ML scoring, cross-ancestry-ML-validation claims) that are not preserved in the pivoted manuscript. Specific ref-number-to-source mapping is deferred to 2.2.f R2 / venue-submission prep once the Zotero library export is available — dropping inline superscripts without the source-to-number mapping risks orphaning a retained reference. The pivot-as-a-whole drops ML-framing claims in §Discussion and §Variant Mechanisms per Amendment §4.17; the inline-superscript cleanup is the last step before the Zotero export consolidates the numbered list.

### Supplementary references

No supplementary-only references have been identified at this pass. The Figure S1–S6 captions (L297) and Table S1–S7 captions throughout the manuscript all cite main-text references; no supplementary-unique bibliography entries are required. This subsection is retained as a placeholder in case 2.3 figure-script development (Route A Step 2.3) introduces a supplementary-caption-only citation — in that case it would be appended here with a slot ⁴⁴+ assignment.

### Full numbered bibliography

[EXTRACT: full numbered reference list 1–43 in venue-specific citation format (Genome Medicine house style primary; AJHG / Bioinformatics fallback formats). Build target: Zotero or EndNote export from the project reference library at `.planning/refs/track_a.bib` or equivalent, during venue-submission package prep per `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.5. R1 does NOT populate this list; the inline-superscript ↔ ref-number mapping in the ### Add / ### Promote / ### Retain / ### Demote / ### Drop subsections above is the source of truth until the export lands.]
```

End of replacement block.

Implementation notes for the executor:
1. Preserve the three horizontal-rule / blank-line separators around the section — the preceding section (Figures S1–S6 at L297) ends with a `---` divider at L299 in the current file, and the subsequent section (`## Decision-pending items` at L313) should stay at its current-or-shifted line depending on the new section length. The new References section will be LONGER than the current 11-line version (approximately 50–60 lines). Recalculate downstream line numbers only as an after-effect of the insertion; do not add or remove dividers.
2. The replacement is idempotent if rerun: it replaces the `## References — revised citation list` block through the last bullet of that block. If the executor runs into a conflict (e.g., the block has already been partially edited), STOP and surface the conflict rather than overwriting partial edits.
3. DO NOT touch the `## Decision-pending items (MUST resolve before submission)` section (currently L313+). DO NOT touch `**Figure S1–S6.**` at L297.
4. Keep the existing `---` horizontal rule between the figure-captions section and the `## References — revised citation list` section if present (it provides visual separation and matches the rest of the manuscript's section convention).
5. Manuscript convention is single line per paragraph, no hard wrap. Preserve that in the new subsections — each bullet is a single unwrapped line even if it goes to 400+ characters.
  </action>
  <verify>
    <automated>
bash -c '
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
echo "=== Gate 1: §References heading present exactly once ===";
test "$(grep -c "^## References — revised citation list" docs/manuscript/track_a_pivot.md)" = "1";
echo "=== Gate 2: five expected ### subsections present ===";
for h in "^### Add$" "^### Promote" "^### Retain" "^### Demote" "^### Drop"; do
  test "$(grep -cE "$h" docs/manuscript/track_a_pivot.md)" -ge 1;
done;
echo "=== Gate 3: ### Full numbered bibliography subsection present ===";
test "$(grep -c "^### Full numbered bibliography" docs/manuscript/track_a_pivot.md)" = "1";
echo "=== Gate 4: ### Supplementary references subsection present ===";
test "$(grep -c "^### Supplementary references" docs/manuscript/track_a_pivot.md)" = "1";
echo "=== Gate 5: key cited authors present in correct subsections ===";
grep -A 40 "^### Add$" docs/manuscript/track_a_pivot.md | head -10 | grep -q "Weissbrod";
grep -A 40 "^### Add$" docs/manuscript/track_a_pivot.md | head -10 | grep -q "Benner";
grep -A 30 "^### Demote" docs/manuscript/track_a_pivot.md | head -10 | grep -q "Neel";
grep -A 30 "^### Demote" docs/manuscript/track_a_pivot.md | head -10 | grep -q "Williams";
echo "=== Gate 6: [EXTRACT: full numbered reference list appears exactly once ===";
test "$(grep -c "\[EXTRACT: full numbered reference list" docs/manuscript/track_a_pivot.md)" = "1";
echo "=== Gate 7: total [EXTRACT: count increased by exactly 1 ===";
# Pre-edit baseline was 16 — post-edit expect exactly 17
test "$(grep -c "\[EXTRACT:" docs/manuscript/track_a_pivot.md)" = "17";
echo "=== Gate 8: §Decision-pending items section still exists (not clobbered) ===";
test "$(grep -c "^## Decision-pending items" docs/manuscript/track_a_pivot.md)" = "1";
echo "=== Gate 9: §Figures S1–S6 mention still exists (upstream section not clobbered) ===";
grep -q "Figure S1–S6" docs/manuscript/track_a_pivot.md;
echo "ALL 9 GATES PASS";
'
    </automated>
  </verify>
  <done>
  - `## References — revised citation list` heading present exactly once (unchanged position or shifted only by net line-count change of this edit).
  - Six `###` subsections under it in order: Add, Promote, Retain, Demote, Drop, Supplementary references, Full numbered bibliography.
  - Weissbrod 2020 and Benner 2017 both appear in ### Add.
  - Zou 2022 and Wallace 2021 both appear in ### Promote.
  - Giambartolomei 2014 and refs 1–3, 6–9, 10, 11–12, 13, 17–19, 21–41, 27 appear in ### Retain.
  - Neel 1962 and Williams 1957 appear in ### Demote.
  - One `[EXTRACT: full numbered reference list` placeholder in ### Full numbered bibliography.
  - Total `[EXTRACT:` count in file = 17 (pre-edit 16 + 1 new).
  - Downstream `## Decision-pending items` section still intact.
  - Upstream Figure S1–S6 caption still intact.
  - All 9 automated gates pass.
  </done>
</task>

<task type="auto">
  <name>Task 3: Write 260424-kul-SUMMARY.md with grep receipts, scope-divergence note, and 2.2.f R2 / 2.3 handoff</name>
  <files>.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md</files>
  <action>
Create `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` following the standard quick-task SUMMARY.md shape (frontmatter + narrative sections). Use the template-style structure consistent with 260424-j64-SUMMARY.md and 260424-k2c-SUMMARY.md (both referenced in `<context>` for shape reference).

Required content sections (in order):

1. **Frontmatter** with: `quick_id: 260424-kul`, `phase: quick-260424-kul`, `plan: 01`, `title` matching the PLAN.md title, `status: complete`, `completed: "2026-04-24T<HH:MM>:00Z"` (fill HH:MM at execution time), `requirements: [ROUTE-A-2.2.f]`, `tags: [track-a, manuscript, references, bibliography, r1]`, `dependency_graph:` with `requires:` (TRACK-A-PIVOT.md §9, track_a_pivot.md L36+L301–311, 260424-j64 / 260424-k2c handoffs) and `provides:` (L36 placeholder resolution, §References structured inventory, Benner 2017 + Weissbrod 2020 on References list) and `affects:` (2.2.f R2 — Zotero export; 2.3 — figure scripts that may cite refs 20/29/42/43; venue-submission package prep), `key_files:` with `modified: [docs/manuscript/track_a_pivot.md]` and `created: [PLAN, SUMMARY]`, `decisions:` list capturing the 5 decisions from the `<interfaces>` block (ascending numeric ordering; superscript placement after terminal period; Weissbrod = 42; Benner = 43 References-list-only; refs 4,5 at L230 unchanged), `metrics:` (duration_minutes, tasks_completed: 3, paragraphs_edited: 1, sections_restructured: 1, files_modified: 1, files_created: 2).

2. **Headline** (first `#` heading): "Phase quick-260424-kul Plan 01: Route A Step 2.2.f References R1 — placeholder resolution + structured inventory"

3. **One-paragraph summary** — what was changed (L36 three bracketed placeholders → `²⁰,²⁹,⁴²` superscript cluster; §References section L301–311 flat narrative → 5+1 structured subsection inventory with 1 new `[EXTRACT:]` placeholder deferring the full numbered bibliography to venue-submission prep). State explicitly that R1 did NOT perform a full inline-citation renumber and did NOT build the full numbered bibliography.

4. **Scope-divergence note** — verbatim transcription of the `<scope_divergence>` block from the PLAN, stated plainly: the 260424-j64 NEXT-STEPS.md brief proposed that 2.2.f renumber all inline citations and build the full numbered bibliography; this R1 pass declines both because (a) no numbered bibliography exists anywhere in the repo, (b) building the full list is a venue-submission artifact per snappy-humming-pine.md §2.5, and (c) dropping inline superscripts for "ML-based claim" references without the v10 source-to-number mapping risks orphaning retained refs. R1 therefore confines itself to what can be resolved without a Zotero library export.

5. **Guardrail grep receipts** — capture the ACTUAL grep outputs produced by the two verify blocks (Tasks 1 and 2). Include each gate's grep command and its observed result. Format as a fenced `bash` code block with the grep invocations and a comment-tagged expected vs observed count for each gate. At minimum include these post-edit greps:
   - `grep -cE '\[Wallace 2021\]|\[Zou 2022\]|\[Weissbrod 2020\]' docs/manuscript/track_a_pivot.md` → 0
   - `grep -c '²⁰' docs/manuscript/track_a_pivot.md` → ≥ 3
   - `grep -c '²⁹' docs/manuscript/track_a_pivot.md` → ≥ 3
   - `grep -c '⁴²' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '⁴³' docs/manuscript/track_a_pivot.md` → 0
   - `grep -c '⁴⁻⁵' docs/manuscript/track_a_pivot.md` → 1 (unchanged)
   - `grep -c 'thrifty-gene' docs/manuscript/track_a_pivot.md` → 1 (unchanged)
   - `grep -c '^### Add$' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '^### Promote' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '^### Retain' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '^### Demote' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '^### Drop' docs/manuscript/track_a_pivot.md` → ≥ 1
   - `grep -c '^### Full numbered bibliography' docs/manuscript/track_a_pivot.md` → 1
   - `grep -c '^### Supplementary references' docs/manuscript/track_a_pivot.md` → 1
   - `grep -c '\[EXTRACT: full numbered reference list' docs/manuscript/track_a_pivot.md` → 1
   - `grep -c '\[EXTRACT:' docs/manuscript/track_a_pivot.md` → 17 (pre-edit 16 + 1 new)

6. **Before/after diff** for L36 — show the one-line verbatim pre-edit and post-edit strings side-by-side (matching the 260424-j64 SUMMARY's "Before / after diffs" style).

7. **Handoff to 2.2.f R2 (venue-submission pass)** — explicit bulleted list:
   - Build full numbered reference list 1–43 via Zotero/EndNote export; commit as `.planning/refs/track_a.bib` (or equivalent) and fill the `### Full numbered bibliography` `[EXTRACT:]` placeholder with venue-formatted output.
   - Resolve exact slot-to-source mapping within ref 21–41 range against the v10 source bibliography (requires locating the v10 bibliography, which is not currently in the repo).
   - Make the final decision on inline placement of Benner 2017 ⁴³ (candidates: L36 alongside Weissbrod 2020; or Methods §Fine-Mapping Integration).
   - Identify and drop inline superscripts for "ML-based claim" references using the v10 source-to-number mapping from the Zotero library.
   - Cross-check every existing inline superscript against the populated numbered list to confirm no orphaned references.

8. **Handoff to 2.3 (figures)** — bullet points noting that:
   - Figures 1–3 (L291–L295 scatter / beeswarm / forest) and supplementary Figures S1–S6 (L297) do not currently need additional references; captions reuse main-text refs.
   - If 2.3 introduces a caption-only citation it should be appended to the `### Supplementary references` subsection with slot ⁴⁴+ assignment.
   - Figure captions that reference methods should cite SuSiE-RSS²⁰ and `coloc.susie`²⁹ consistently with the manuscript body.

9. **No further handoffs for 2.4** — the bioRxiv preprint package (2.4) consumes the frozen manuscript; References section shape locked at this pass.

10. **Commit framing reminder** — state that the docs commit for this pass (handled by the orchestrator, NOT this plan) should frame the change as original research framing ("align References section to TRACK-A-PIVOT.md §9"), NEVER as "revision" / "cleanup" / "fix".

Length target: ~250–400 lines (comparable to 260424-j64-SUMMARY.md and 260424-k2c-SUMMARY.md). Do NOT add content beyond what this action specifies — this is an R1 summary, not a narrative essay.
  </action>
  <verify>
    <automated>
bash -c '
set -e
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
SUMMARY=.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md
echo "=== Gate 1: SUMMARY.md exists ===";
test -f "$SUMMARY";
echo "=== Gate 2: frontmatter fields present ===";
grep -q "^quick_id: 260424-kul" "$SUMMARY";
grep -q "^phase: quick-260424-kul" "$SUMMARY";
grep -q "^status: complete" "$SUMMARY";
grep -q "ROUTE-A-2.2.f" "$SUMMARY";
echo "=== Gate 3: required narrative sections present ===";
grep -q "[Ss]cope" "$SUMMARY";
grep -q "[Hh]andoff" "$SUMMARY" || grep -q "[Hh]and-off" "$SUMMARY";
grep -q "Zotero" "$SUMMARY";
grep -q "snappy-humming-pine" "$SUMMARY";
grep -q "Weissbrod" "$SUMMARY";
grep -q "Benner" "$SUMMARY";
echo "=== Gate 4: grep receipts include key expectations ===";
grep -q "²⁰,²⁹,⁴²" "$SUMMARY";
grep -q "grep" "$SUMMARY";
echo "=== Gate 5: length sanity ===";
LINES=$(wc -l < "$SUMMARY");
test "$LINES" -ge 100 && test "$LINES" -le 600;
echo "ALL 5 GATES PASS";
'
    </automated>
  </verify>
  <done>
  - `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` exists.
  - Frontmatter populated (quick_id, phase, status, requirements, tags, dependency_graph, key_files, decisions, metrics).
  - Body contains: headline, one-paragraph summary, scope-divergence note, guardrail grep receipts, before/after L36 diff, handoff to 2.2.f R2, handoff to 2.3, commit-framing reminder.
  - File length in the 100–600 line range (sanity guard).
  - All 5 automated gates pass.
  </done>
</task>

</tasks>

<verification>

**Post-implementation holistic checks (after all 3 tasks complete):**

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# Check 1: Forbidden framing words absent from edited regions
# (Per CLAUDE.md / user profile feedback: NEVER frame as "revision" / "cleanup" / "fix" in docs artifacts.)
# This is a heuristic check — the SUMMARY should use "R1 pass" / "alignment" / "original-research" framing only.
grep -iE "\brevision\b|\bcleanup\b|\bfix(ing|es|ed)?\b" \
  .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md \
  && echo "WARN: forbidden framing word present — inspect and edit" \
  || echo "OK: no forbidden framing words"

# Check 2: Frozen numerics in TRACK-A-FROZEN-NUMBERS.md did not drift
# (References section touches no Stage 2 numerics, but defensive grep.)
for n in "51/96" "12/96" "4.25" "1,274" "0.3099" "224" "9 Tier C"; do
  BEFORE=$(git show HEAD:docs/manuscript/track_a_pivot.md 2>/dev/null | grep -c "$n" || echo 0)
  AFTER=$(grep -c "$n" docs/manuscript/track_a_pivot.md)
  if [ "$BEFORE" != "$AFTER" ]; then
    echo "WARN: count drift for \"$n\": before=$BEFORE after=$AFTER"
  fi
done

# Check 3: Line-count delta in the manuscript is reasonable
# Expect: +40 to +60 net lines (References section grew from ~11 lines to ~60 lines; L36 edit is net-zero line count)
git diff --stat docs/manuscript/track_a_pivot.md 2>/dev/null || echo "No git diff available (pre-stage)"
```

**Regression watch (should be no-op — verified by Task 1 Gate 8):**
- L230 thrifty-gene paragraph and ⁴⁻⁵ superscripts unchanged.
- L38 SuSiE-RSS²⁰ + coloc.susie²⁹ primary-method citations unchanged.
- L72 Methods-section citations unchanged.

</verification>

<success_criteria>

- [ ] L36 bracketed placeholders `[Wallace 2021] [Zou 2022] [Weissbrod 2020]` replaced with superscript cluster `²⁰,²⁹,⁴²` (ascending numeric order, post-period placement, no intervening space).
- [ ] §References — revised citation list restructured into 5+2 subsections: Add, Promote, Retain, Demote, Drop, Supplementary references, Full numbered bibliography.
- [ ] Weissbrod 2020 assigned to slot ⁴² and inlined at L36; Benner 2017 assigned to slot ⁴³ on References list only (NOT inlined).
- [ ] Zou 2022 (ref 20) and Wallace 2021 (ref 29) recorded under ### Promote with existing inline slots (L36, L38, L72) explicitly tracked.
- [ ] Giambartolomei 2014 (ref 10) and refs 1–3, 6–9, 11–12, 13, 17–19, 21–41, 27 recorded under ### Retain.
- [ ] Neel 1962 and Williams 1957 (refs 4, 5) recorded under ### Demote with L230 inline slot preserved.
- [ ] One `[EXTRACT: full numbered reference list …]` placeholder in ### Full numbered bibliography subsection; total `[EXTRACT:` count in file = 17 (pre-edit 16 + 1).
- [ ] Refs 4, 5 at L230 (⁴⁻⁵) unchanged — verified by grep (count = 1).
- [ ] No frozen numeric from TRACK-A-FROZEN-NUMBERS.md drifts.
- [ ] SUMMARY.md explicitly states scope divergence from 260424-j64 NEXT-STEPS.md (no full renumber at R1 because no numbered bibliography exists yet) and enumerates handoff to 2.2.f R2 (Zotero export) and 2.3 (figures).
- [ ] All automated gates in Tasks 1, 2, 3 pass.
- [ ] Docs commit is handled by the orchestrator in workflow Step 8 (NOT by this plan); commit message frames the change as original research ("align References to TRACK-A-PIVOT.md §9"), NEVER "revision" / "cleanup" / "fix".

</success_criteria>

<output>
After completion:
- Docs artifact: `docs/manuscript/track_a_pivot.md` (modified at L36 and §References section; orchestrator commits).
- Planning artifact: `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` (created; orchestrator commits).
- No ROADMAP.md update (quick tasks are outside phase plans).
- No STATE.md update at plan level — STATE.md row for 260424-kul is added by the orchestrator after commit (matching the 260424-j64 and 260424-k2c pattern at STATE.md lines 275, 276).
</output>
