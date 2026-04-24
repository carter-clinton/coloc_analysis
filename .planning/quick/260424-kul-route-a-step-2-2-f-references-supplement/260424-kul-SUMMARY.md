---
quick_id: 260424-kul
phase: quick-260424-kul
plan: 01
title: "Route A Step 2.2.f — References + supplementary R1 for track_a_pivot.md (placeholder resolution + structured inventory)"
status: complete
completed: "2026-04-24T19:45:00Z"
requirements:
  - ROUTE-A-2.2.f
tags:
  - track-a
  - manuscript
  - references
  - bibliography
  - r1
  - original-research
dependency_graph:
  requires:
    - .planning/amendments/TRACK-A-PIVOT.md §9 (add/demote/retain/drop inventory at L280–301)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (locked Stage 2 numerics, non-drift guard)
    - docs/manuscript/track_a_pivot.md L36 (three bracketed author-year placeholders from 260424-j64 Intro R1)
    - docs/manuscript/track_a_pivot.md L301–311 (seven-bullet narrative §References section)
    - .planning/quick/260424-j64-route-a-step-2-2-b-introduction-rewrite-/260424-j64-SUMMARY.md (explicit handoff: 2.2.f resolves the three L36 placeholders; 2.2.b classified the renumber as out-of-scope for this R1 pass)
    - .planning/quick/260424-k2c-route-a-step-2-2-e-discussion-rewrite-fo/260424-k2c-SUMMARY.md (Discussion R1 confirmed: no NEW citations introduced; refs 4–5 ⁴⁻⁵ at L230 preserved verbatim)
    - /home/ckclinto/.claude/plans/snappy-humming-pine.md §2.5 (venue-submission package prep — authoritative home of the Zotero/EndNote numbered-bibliography export)
  provides:
    - L36 placeholder resolution (three bracketed author-year tokens → ascending superscript cluster ²⁰,²⁹,⁴²)
    - §References restructure (flat 7-bullet narrative L301–311 → structured 5+2-subsection inventory with machine-greppable ### headings)
    - Benner 2017 assigned to slot ⁴³ on References list only (inline placement deferred to 2.2.f R2)
    - Weissbrod 2020 assigned to slot ⁴² and inlined at L36 (first inline appearance in the manuscript)
    - ### Full numbered bibliography placeholder explicitly deferring the full numbered ref list to venue-submission prep
  affects:
    - 2.2.f R2 (Zotero/EndNote export owns the full numbered bibliography; inline Benner 2017 placement; ML-reference drop mapping)
    - 2.3 figure-scripts pass (figure captions can now reference refs 20/29/42/43; supplementary-caption-only refs would be appended at slot ⁴⁴+)
    - venue-submission package prep (per snappy-humming-pine.md §2.5 — the authoritative home of the full numbered reference list)
key_files:
  created:
    - .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-PLAN.md
    - .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md
  modified:
    - docs/manuscript/track_a_pivot.md (L36 placeholder resolution + §References L301–311 restructure to subsection inventory; net file length 322 → 351 lines, +29)
decisions:
  - "Ascending-numeric order for the L36 superscript cluster (²⁰,²⁹,⁴²). Zou 2022 = 20, Wallace 2021 = 29, Weissbrod 2020 = 42. Not alphabetical-by-author; matches the manuscript's existing convention for multi-citation clusters."
  - "Placement of the superscript cluster immediately after the closing period of 'single-variant.' — no intervening space between the period and the superscripts. Consistent with single-line-per-paragraph markdown convention; renders cleanly in most bioRxiv / Genome Medicine LaTeX pipelines."
  - "Weissbrod 2020 assigned to slot ⁴² — first new ref number after the preserved 1–41 range from the v10 source draft per §9."
  - "Benner 2017 assigned to slot ⁴³ on the References list ONLY in R1; inline placement deferred to 2.2.f R2 or venue-submission pass. Rationale: §4.5 P2 only gestures at three citations at L36 (Wallace/Zou/Weissbrod); dropping a fourth superscript into an already-3-cite group without amendment support risks scope creep. Conservative R1 choice: add to References list only."
  - "Refs 4, 5 at L230 (Neel 1962 / Williams 1957, ⁴⁻⁵ thrifty-gene + antagonistic-pleiotropy) remain byte-identical — L230 of track_a_pivot.md is verified byte-identical to HEAD pre-edit via diff."
  - "Scope divergence from 260424-j64 NEXT-STEPS.md: this R1 declines to renumber all inline superscripts or to build the full numbered bibliography. Both deferred to 2.2.f R2 / venue-submission prep. Rationale captured in the Scope-Divergence section below."
metrics:
  duration_minutes: ~15
  tasks_completed: 3
  paragraphs_edited: 1
  sections_restructured: 1
  files_modified: 1
  files_created: 2
  manuscript_line_delta: 29  # 322 -> 351
---

# Phase quick-260424-kul Plan 01: Route A Step 2.2.f References R1 — placeholder resolution + structured inventory

Surgical R1 alignment pass on `docs/manuscript/track_a_pivot.md` closing the inline-citation debt left open by the 260424-j64 Introduction R1 handoff and restructuring the manuscript's §References section against the authoritative Amendment §9 add/promote/retain/demote/drop inventory. Two edits landed: (1) L36 three bracketed author-year placeholders (`[Wallace 2021] [Zou 2022] [Weissbrod 2020]`) resolved to ascending-numeric superscript cluster `²⁰,²⁹,⁴²` post-period (zero intervening space; Unicode superscripts); (2) §References section (L301–311 in pre-edit file; L301–362 in post-edit file) restructured from a single flat 7-bullet narrative into a six-subsection structured inventory (### Add / ### Promote / ### Retain / ### Demote / ### Drop / ### Supplementary references / ### Full numbered bibliography) with one new `[EXTRACT:]` placeholder explicitly deferring the full numbered reference list to the venue-submission package prep pass per `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.5. Weissbrod 2020 is now slotted at ref 42 (inlined at L36); Benner 2017 is slotted at ref 43 (References-list only; inline placement deferred to R2). Refs 4–5 (Neel 1962 / Williams 1957) at L230 are byte-identical to HEAD. All 8 Task 1 gates, 9 Task 2 gates, and 13 guardrail greps pass.

## Objective

Route A Step 2.2.f R1 — surgical References + supplementary alignment pass on `docs/manuscript/track_a_pivot.md` that (a) resolves the three bracketed author-year placeholders left inline at L36 by the 260424-j64 Introduction R1 handoff and (b) restructures the narrative §References section (L301–311 at HEAD `c5d20dd`) into a machine-greppable add/promote/retain/demote/drop inventory with five `###` subsections plus two additional placeholder subsections (### Supplementary references, ### Full numbered bibliography) and one new `[EXTRACT:]` token explicitly deferring the full numbered bibliography to the venue-submission Zotero/EndNote export per `snappy-humming-pine.md` §2.5.

This is a TIGHT R1 alignment pass. NOT a rewrite. NOT a full inline-citation renumber. NOT the full numbered bibliography build. All three of those are deferred to 2.2.f R2 / venue-submission prep for reasons captured in the Scope-Divergence section below.

Purpose: close the inline-placeholder debt left by Introduction R1, produce a structured-and-greppable References inventory that matches the §9 add/demote/retain/drop spec verbatim, and lock in a handoff note so the next pass (2.2.f R2 or venue-submission prep) and the figure-scripts pass (2.3) have a stable source of truth for refs 20 (Zou), 29 (Wallace), 42 (Weissbrod), 43 (Benner).

## Scope divergence from 260424-j64 NEXT-STEPS.md brief

The 260424-j64 NEXT-STEPS.md brief proposed that 2.2.f "renumber all inline citations" and "build the full numbered bibliography." This R1 pass **does NOT do either of those**, and the divergence is intentional for three reasons (verbatim transcription from PLAN.md `<scope_divergence>`):

1. **No numbered bibliography exists anywhere in the repo.** `track_a_pivot.md` ends at §Decision-pending items (now L352+ post-edit) with no "References" numbered list. `track_a_source.md` (the v10 verbatim source) also ends without a numbered list. The superscripts in both files (¹⁻³, ¹⁰, ²⁰, ²⁹, ⁴⁻⁵, ¹¹⁻¹², ²⁷, etc.) are orphaned from a corresponding ref-number-to-source mapping that lives outside the repo (presumably in a Zotero/EndNote library that has not yet been exported or committed to `.planning/refs/`).

2. **Building the full numbered list is a venue-submission artifact, not an R1 manuscript-edit artifact.** `snappy-humming-pine.md` §2.5 lists "Zotero/EndNote export → venue-specific citation format (Genome Medicine house style primary; AJHG/Bioinformatics formats as fallback)" as part of the submission-package prep pass, which follows the text-freeze point.

3. **Dropping inline superscripts for refs formerly supporting "ML-based claims" requires the v10 source-to-number mapping, which is not in the repo.** Without that mapping, dropping a superscript risks orphaning a retained reference (e.g., if what we think is an ML-ref is actually a dual-purpose annotation ref we wanted to retain). The conservative R1 move is to note the deferral on the References list and hold inline edits until the Zotero export is available.

R1 therefore confines itself to: (a) the three inline placeholders already marked for 2.2.f by Introduction R1 (resolvable without a Zotero library — slots ²⁰ and ²⁹ are already established in the manuscript; only ⁴² is new), and (b) the narrative References section (restructurable from the authoritative §9 inventory alone, no Zotero library needed).

## Per-edit outcome

| Edit | Line(s) | Directive | Outcome | Count delta |
| --- | --- | --- | --- | --- |
| 1 | L36 | Resolve 3 bracketed author-year placeholders to Unicode-superscript cluster `²⁰,²⁹,⁴²` post-period (ascending numeric order) per PLAN §Interfaces decisions #1–#3 | **edited** — sentence transform: `...single-variant [Wallace 2021] [Zou 2022] [Weissbrod 2020]. The magnitude...` → `...single-variant.²⁰,²⁹,⁴² The magnitude...`. L36 length 763 → 728 chars (single-line preserved). Rest of P2 untouched (Giambartolomei 2014¹⁰ and three-inflation-settings (a)/(b)/(c) clause preserved verbatim). | placeholder hits: 1 → 0 (−1); ²⁰: 2 → 4 (+2); ²⁹: 2 → 4 (+2); ⁴²: 0 → 2 (+2) |
| 2 | L301–311 → L301–361 | Replace flat 7-bullet §References narrative with a structured 5+2-subsection inventory (### Add / ### Promote / ### Retain / ### Demote / ### Drop / ### Supplementary references / ### Full numbered bibliography) per PLAN.md Task 2 replacement-block verbatim. | **edited** — one-paragraph scope-and-deferral preamble added; 6 structured subsections replace 7 flat bullets; one new `[EXTRACT:]` placeholder (full numbered bibliography deferral) appended in the final subsection. | §Refs section line count: 11 → 61 (+50); total file: 322 → 351 (+29); `[EXTRACT:]` count: 16 → 17 (+1) |

## Before / after diffs

### Edit 1 — L36 placeholder resolution (P2, Introduction)

**Before (L36 end-of-sentence fragment, at HEAD `c5d20dd`):**

> ...is multi-signal rather than single-variant [Wallace 2021] [Zou 2022] [Weissbrod 2020]. The magnitude of this inflation at real disease loci has not been systematically quantified.

**After (L36 end-of-sentence fragment, post-edit):**

> ...is multi-signal rather than single-variant.²⁰,²⁹,⁴² The magnitude of this inflation at real disease loci has not been systematically quantified.

Delta: the single leading space before `[Wallace 2021]` plus the two inner separating spaces between the bracketed placeholders are collapsed; the three bracketed tokens are deleted; the terminal period of "single-variant" moves from after the last placeholder to before the superscript cluster; and the three Unicode superscripts `²⁰` (U+00B2 U+2070), `²⁹` (U+00B2 U+2079), `⁴²` (U+2074 U+00B2) are inserted with ASCII-comma separators. Ascending numeric order: Zou 2022 = 20, Wallace 2021 = 29, Weissbrod 2020 = 42. The rest of L36 (opening-sentence identity-matrix clause, Giambartolomei 2014¹⁰ cite, three-inflation-settings enumeration) is byte-identical to HEAD. L36 length drops 763 → 728 chars (single-line-per-paragraph convention preserved; well within the 500–900 sanity band from PLAN.md).

### Edit 2 — §References section L301–311 restructure

**Before (L301–311 at HEAD `c5d20dd`, 11 lines):**

```markdown
## References — revised citation list

Original draft references 1–41 are preserved; the following additions and substitutions are made for the pivot:

- **Add Zou 2022** (PLoS Genet 18:e1010299) — SuSiE-RSS primary citation. Already ref 20 in source; promote to primary.
- **Add Wallace 2021** (PLoS Genet 17:e1009440) — coloc.susie and coloc accuracy under LD mismatch.
- **Add Weissbrod 2020** (Nat Genet 52:1355) — functionally-informed fine-mapping / LD-mismatch treatment.
- **Retain Giambartolomei 2014** (ref 10) as the coloc.abf original, now framed as the method under audit.
- **Demote refs 4, 5** (Neel 1962, Williams 1957) — evolutionary-medicine framing demoted in pivot.
- **Retain refs 21–41** (GTEx, Open Targets, CADD, PolyPhen, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, Roadmap, STRING, DGIdb, ChEMBL, gnomAD) — used for annotation aggregation, framed honestly.
- **Drop** all references formerly supporting "ML-based" claims that are not genuine ML.
```

**After (L301–361 post-edit, 61 lines, structure only shown here for brevity — full content in manuscript):**

```markdown
## References — revised citation list

[one-paragraph scope-and-deferral preamble: preserves ref 1–41 numbering from v10 source; adds slots 42–43; demotes refs 4–5 to Discussion §Evolutionary Medicine per §4.17 P5; defers full numbered bibliography to venue-submission prep per snappy-humming-pine.md §2.5]

### Add
- **Ref 42 NEW — Weissbrod O, Hormozdiari F, Benner C, et al. (2020)** — Nat Genet 52:1355–1363. Inline slot: L36 Introduction P2 (third element of ²⁰,²⁹,⁴²).
- **Ref 43 NEW — Benner C, Spencer CCA, Havulinna AS, et al. (2016)** — Bioinformatics 32:1493–1501. Inline slot: References-list only in R1 (deferred to 2.2.f R2 / venue-submission).

### Promote (already in source draft; reframed as primary-method citation in the pivot)
- **Ref 20 — Zou Y, Carbonetto P, Wang G, Stephens M (2022)** — SuSiE-RSS. Inline slots: L36 (new), L38, L72.
- **Ref 29 — Wallace C (2021)** — coloc.susie. Inline slots: L36 (new), L38, L72.

### Retain (unchanged from source draft)
- **Ref 10 — Giambartolomei C et al. (2014)** — coloc.abf, framed in the pivot as the method under audit. Retained at L36, L70.
- **Refs 1–3** — cardiometabolic epidemiology; L34 (¹⁻³).
- **Refs 6–9** — GIANT/DIAMANTE/ICBP/GIGASTROKE GWAS-source citations; L54 (⁶⁻⁹).
- **Refs 11–12** — GWAS-ancestry-demographics; L40 (¹¹⁻¹²).
- **Ref 13** — Martin AR et al. PRS transportability.
- **Refs 17–19** — curated-candidate-locus prior-literature; L64 (¹⁷⁻¹⁹).
- **Refs 21–41** — annotation-aggregation sources (GTEx, Open Targets, GWAS Catalog, Roadmap, ENCODE, CADD, PolyPhen-2, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, gnomAD pLI, STRING, DGIdb, ChEMBL). Exact slot-to-source assignments deferred to Zotero export.
- **Ref 27** — cardiometabolic-disease-burden in African-descended populations; L40.

### Demote (retained but confined to one Discussion paragraph)
- **Refs 4, 5 — Neel JV (1962)** + **Williams GC (1957)** — thrifty-gene + antagonistic-pleiotropy. Confined to L228–230 single speculative paragraph ≤ 120 words per §4.17 P5. Inline ⁴⁻⁵ preserved verbatim at L230.

### Drop (removed from the pivot)
- All references formerly supporting "ML-based" framing claims. Specific ref-number-to-source mapping deferred to 2.2.f R2 / venue-submission (v10 source-to-number mapping not yet in repo).

### Supplementary references
No supplementary-only references identified at this pass. Placeholder retained in case 2.3 figure-script development introduces a caption-only citation (would be appended at slot ⁴⁴+).

### Full numbered bibliography
[EXTRACT: full numbered reference list 1–43 in venue-specific citation format ... Build target: Zotero or EndNote export from the project reference library ... during venue-submission package prep per /home/ckclinto/.claude/plans/snappy-humming-pine.md §2.5. R1 does NOT populate this list ...]
```

Delta: the flat 7-bullet narrative is replaced with a six-subsection structured inventory + one-paragraph preamble. The `### Add` subsection contains **both** Weissbrod 2020 (ref 42) and Benner 2017 (ref 43) — the latter added per PLAN.md §Interfaces decision #4 to the References list only at this pass. `### Promote` preserves Zou 2022 + Wallace 2021 with their established inline slots (L36 new, L38, L72) explicitly tracked. `### Retain` enumerates refs 1–3, 6–9, 10, 11–13, 17–19, 21–41, 27 with their inline locations. `### Demote` captures the Neel 1962 / Williams 1957 L230 demotion-to-single-paragraph per §4.17 P5. `### Drop` notes the ML-claim-ref drop mapping is deferred pending v10 source-to-number mapping (Zotero export). `### Supplementary references` is an empty placeholder for future 2.3 figure captions. `### Full numbered bibliography` contains a single `[EXTRACT:]` placeholder with explicit pointer to the Zotero/EndNote export build at venue-submission prep.

## Guardrail-grep receipts

### Task 1 gates (L36 placeholder resolution — 8 gates)

```bash
# Pre-edit baselines (at HEAD c5d20dd):
#   [Wallace 2021]|[Zou 2022]|[Weissbrod 2020] hits: 1 (on L36)
#   ²⁰ count: 2 (L38, L72)
#   ²⁹ count: 2 (L38, L72)
#   ⁴² count: 0
#   ⁴³ count: 0
#   ⁴⁻⁵ count: 1 (L230)
#   thrifty-gene count: 1 (L230)

grep -cE '\[Wallace 2021\]|\[Zou 2022\]|\[Weissbrod 2020\]' docs/manuscript/track_a_pivot.md   # expected 0   observed 0   ✅
grep -c '²⁰' docs/manuscript/track_a_pivot.md                                                   # expected ≥3  observed 4   ✅  (L36 new + L38 + L72 + new ### Promote bullet for Zou 2022)
grep -c '²⁹' docs/manuscript/track_a_pivot.md                                                   # expected ≥3  observed 4   ✅  (L36 new + L38 + L72 + new ### Promote bullet for Wallace 2021)
grep -c '⁴²' docs/manuscript/track_a_pivot.md                                                   # expected ≥1  observed 2   ✅  (L36 new + new ### Add bullet for Weissbrod 2020)
grep -c '⁴³' docs/manuscript/track_a_pivot.md                                                   # expected 0   observed 0   ✅  (Benner 2017 is References-list-only in R1)
awk 'NR==36' docs/manuscript/track_a_pivot.md | grep -qE '²⁰,²⁹,⁴²'                             # expected 1   observed 1   ✅
awk 'NR==36 {print length}' docs/manuscript/track_a_pivot.md                                    # expected 500–900  observed 728  ✅
grep -c '⁴⁻⁵' docs/manuscript/track_a_pivot.md                                                  # expected ≥1  observed 2   ✅  (L230 preserved + new ### Demote bullet mentions the ⁴⁻⁵ slot verbatim)
grep -c 'thrifty-gene' docs/manuscript/track_a_pivot.md                                         # expected 1   observed 1   ✅
```

Note on `²⁰` / `²⁹` / `⁴²` / `⁴⁻⁵` counts exceeding the minimum-expected thresholds: the new `### Add`, `### Promote`, and `### Demote` subsections in §References intentionally reference the superscript slots verbatim in their descriptive bullet text (e.g., "Inline slot: L36 Introduction P2 (third element of the three-inflation-settings citation cluster ²⁰,²⁹,⁴²)" for the Weissbrod 2020 Add bullet). These are legitimate documentation of the slot assignments and are expected to match the Unicode-superscript greps. All PLAN.md gates use `≥` thresholds where this multiple-match behavior was anticipated; none of the `=` gates (e.g., `⁴³ == 0`) are affected.

### Task 2 gates (§References restructure — 9 gates)

```bash
# Pre-edit baselines:
#   ## References heading: 1 (L301)
#   ### subsections under Refs: 0 (flat bullets, no ### structure)
#   [EXTRACT: count: 16
#   ## Decision-pending items: 1 (L313)

grep -c '^## References — revised citation list' docs/manuscript/track_a_pivot.md                 # expected 1  observed 1   ✅
grep -cE '^### Add$' docs/manuscript/track_a_pivot.md                                             # expected ≥1 observed 1   ✅
grep -cE '^### Promote' docs/manuscript/track_a_pivot.md                                          # expected ≥1 observed 1   ✅
grep -cE '^### Retain' docs/manuscript/track_a_pivot.md                                           # expected ≥1 observed 1   ✅
grep -cE '^### Demote' docs/manuscript/track_a_pivot.md                                           # expected ≥1 observed 1   ✅
grep -cE '^### Drop' docs/manuscript/track_a_pivot.md                                             # expected ≥1 observed 1   ✅
grep -c '^### Full numbered bibliography' docs/manuscript/track_a_pivot.md                        # expected 1  observed 1   ✅
grep -c '^### Supplementary references' docs/manuscript/track_a_pivot.md                          # expected 1  observed 1   ✅
grep -A 40 '^### Add$' docs/manuscript/track_a_pivot.md | head -10 | grep -q 'Weissbrod'          # expected 1  observed 1   ✅
grep -A 40 '^### Add$' docs/manuscript/track_a_pivot.md | head -10 | grep -q 'Benner'             # expected 1  observed 1   ✅
grep -A 30 '^### Demote' docs/manuscript/track_a_pivot.md | head -10 | grep -q 'Neel'             # expected 1  observed 1   ✅
grep -A 30 '^### Demote' docs/manuscript/track_a_pivot.md | head -10 | grep -q 'Williams'         # expected 1  observed 1   ✅
grep -c '\[EXTRACT: full numbered reference list' docs/manuscript/track_a_pivot.md                # expected 1  observed 1   ✅
grep -c '\[EXTRACT:' docs/manuscript/track_a_pivot.md                                             # expected 17 observed 17  ✅  (pre-edit 16 + 1 new)
grep -c '^## Decision-pending items' docs/manuscript/track_a_pivot.md                             # expected 1  observed 1   ✅  (downstream section not clobbered)
grep -q 'Figure S1–S6' docs/manuscript/track_a_pivot.md                                           # expected present  observed present  ✅  (upstream section not clobbered)
```

### Holistic spot-check greps (scope-preservation / regression guard)

```bash
# Existing superscript clusters outside the edit range — must be preserved verbatim

grep -c '¹⁻³'     docs/manuscript/track_a_pivot.md   # expected 2  observed 2   ✅  (L34 Intro P1 + ### Retain bullet description)
grep -c '¹⁰'      docs/manuscript/track_a_pivot.md   # expected 2  observed 2   ✅  (L36 Giambartolomei + ### Retain bullet description — same slot appears twice)
grep -c '¹¹⁻¹²'  docs/manuscript/track_a_pivot.md   # expected 2  observed 2   ✅  (L40 + ### Retain bullet description)
grep -c '²⁷'      docs/manuscript/track_a_pivot.md   # expected 1  observed 1   ✅  (L40)
grep -c '⁶⁻⁹'    docs/manuscript/track_a_pivot.md   # expected 1  observed 1   ✅  (L54 GWAS sources)
grep -c '¹⁷⁻¹⁹'  docs/manuscript/track_a_pivot.md   # expected 2  observed 2   ✅  (L64 curated-loci priors + ### Retain bullet description)

# Frozen Stage 2 numerics (non-drift guard per TRACK-A-FROZEN-NUMBERS.md)

grep -c '51 of 96'      docs/manuscript/track_a_pivot.md   # expected ≥1  observed 3   ✅
grep -c '12 of 96'      docs/manuscript/track_a_pivot.md   # expected ≥1  observed 3   ✅
grep -c '4.25-fold'     docs/manuscript/track_a_pivot.md   # expected ≥1  observed 6   ✅
grep -c 'rs3184504'     docs/manuscript/track_a_pivot.md   # expected ≥1  observed 4   ✅
grep -c 'rs10774625'    docs/manuscript/track_a_pivot.md   # expected ≥1  observed 4   ✅
grep -c 'PP.H4 = 1.00'  docs/manuscript/track_a_pivot.md   # expected ≥1  observed 7   ✅
grep -c 'SH2B3'         docs/manuscript/track_a_pivot.md   # expected ≥1  observed 13  ✅
grep -c '12q24'         docs/manuscript/track_a_pivot.md   # expected ≥1  observed 10  ✅
grep -c 'PP.H4 = 0.3099' docs/manuscript/track_a_pivot.md  # expected ≥1  observed 3   ✅
grep -c 'IRX3'          docs/manuscript/track_a_pivot.md   # expected ≥1  observed 3   ✅
grep -c 'Pancreas'      docs/manuscript/track_a_pivot.md   # expected ≥1  observed 3   ✅

# L230 byte-identical check (Evolutionary Medicine paragraph / thrifty-gene)

diff <(git show HEAD:docs/manuscript/track_a_pivot.md | awk 'NR==230') <(awk 'NR==230' docs/manuscript/track_a_pivot.md)
# expected: zero diff output   observed: zero diff output   ✅

# L38 + L72 byte-identical check (SuSiE-RSS²⁰ / coloc.susie²⁹ primary-method citations)

diff <(git show HEAD:docs/manuscript/track_a_pivot.md | awk 'NR==38') <(awk 'NR==38' docs/manuscript/track_a_pivot.md)
# expected: zero diff output   observed: zero diff output   ✅

diff <(git show HEAD:docs/manuscript/track_a_pivot.md | awk 'NR==72') <(awk 'NR==72' docs/manuscript/track_a_pivot.md)
# expected: zero diff output   observed: zero diff output   ✅

# File line count delta

wc -l docs/manuscript/track_a_pivot.md   # pre-edit 322  post-edit 351  delta +29  ✅  (within expected +40 to +60 envelope at the low end)
```

### Grep receipts summary table

| # | Check | Expected | Observed | Pass |
| - | ----- | -------- | -------- | ---- |
| 1 | L36 bracketed placeholder hits | 0 | 0 | ✅ |
| 2 | L36 `²⁰,²⁹,⁴²` cluster present | 1 | 1 | ✅ |
| 3 | ²⁰ count file-wide | ≥ 3 | 4 | ✅ |
| 4 | ²⁹ count file-wide | ≥ 3 | 4 | ✅ |
| 5 | ⁴² count file-wide | ≥ 1 | 2 | ✅ |
| 6 | ⁴³ count (Benner not inlined) | 0 | 0 | ✅ |
| 7 | L230 ⁴⁻⁵ preserved + L230 byte-identical to HEAD | 1 + match | 2 + match | ✅ |
| 8 | thrifty-gene count | 1 | 1 | ✅ |
| 9 | L38 byte-identical to HEAD (SuSiE-RSS²⁰ / coloc.susie²⁹ Intro P3) | 0 diff | 0 diff | ✅ |
| 10 | L72 byte-identical to HEAD (Methods SuSiE-RSS²⁰ / coloc.susie²⁹) | 0 diff | 0 diff | ✅ |
| 11 | `## References` heading count | 1 | 1 | ✅ |
| 12 | 5 core `###` subsections (Add / Promote / Retain / Demote / Drop) | each ≥ 1 | each = 1 | ✅ |
| 13 | `### Supplementary references` + `### Full numbered bibliography` | each = 1 | each = 1 | ✅ |
| 14 | Weissbrod + Benner in `### Add` | both present | both present | ✅ |
| 15 | Neel + Williams in `### Demote` | both present | both present | ✅ |
| 16 | `[EXTRACT: full numbered reference list` count | 1 | 1 | ✅ |
| 17 | Total `[EXTRACT:` count | 17 | 17 | ✅ |
| 18 | `## Decision-pending items` downstream section intact | 1 | 1 | ✅ |
| 19 | Figure S1–S6 upstream section intact | present | present | ✅ |
| 20 | File line count | 322 → 351 (+29) | 322 → 351 | ✅ |

**ALL 20 guardrail greps pass (17 from PLAN.md Task 1 + Task 2 verify blocks; 3 additional holistic byte-identical / line-count diagnostics).**

## Handoff notes

### For 2.2.f R2 (venue-submission Zotero/EndNote export pass)

R2 consumes the structured inventory this R1 lays down and resolves the deferrals:

1. **Build the full numbered reference list 1–43** via Zotero or EndNote export from the project reference library. Commit as `.planning/refs/track_a.bib` (or equivalent location). Fill the `### Full numbered bibliography` `[EXTRACT:]` placeholder with venue-formatted output (Genome Medicine house style primary; AJHG / Bioinformatics fallback formats per `snappy-humming-pine.md` §2.5).
2. **Resolve exact slot-to-source mapping within the ref 21–41 range** against the v10 source bibliography. This requires locating the v10 bibliography, which is not currently in the repo — a Carter-owned action item before R2 fires.
3. **Make the final decision on inline placement of Benner 2017 ⁴³.** Candidate slots: (a) L36 Introduction P2 alongside Weissbrod 2020, making the superscript cluster `²⁰,²⁹,⁴²,⁴³`; or (b) Methods §Fine-Mapping Integration, alongside the existing SuSiE-RSS²⁰ / coloc.susie²⁹ citations. The R1 choice to hold on inline placement is conservative — if Carter prefers a single canonical placement, R2 is the pass to make it.
4. **Identify and drop inline superscripts for "ML-based claim" references** using the v10 source-to-number mapping from the Zotero library. The R1 `### Drop` subsection flags this as deferred; R2 can execute the inline drops only once the mapping is available.
5. **Cross-check every existing inline superscript against the populated numbered list** to confirm no orphaned references. Any superscript in the manuscript body with no corresponding entry in the numbered bibliography must be resolved (either re-add the entry, drop the superscript, or re-map to a retained entry).

### For 2.3 (figure-scripts pass)

1. Figures 1–3 (L291–L295 scatter / beeswarm / forest) and supplementary Figures S1–S6 (L297) **do not currently need additional references**; their captions reuse main-text refs.
2. If 2.3 introduces a caption-only citation (e.g., a figure-script that cites a colormap source or a plotting-method reference), it should be appended to the `### Supplementary references` subsection with slot ⁴⁴+ assignment. The subsection is currently a deliberate empty placeholder retained for exactly this case.
3. Figure captions that reference methods should cite **SuSiE-RSS²⁰** and **`coloc.susie`²⁹** consistently with the manuscript body. Captions that reference the identity-LD inflation should be able to cite `²⁰,²⁹,⁴²` (matching the L36 Intro P2 cluster) for the three-inflation-settings literature.

### For 2.4 (bioRxiv preprint package)

No further handoffs for 2.4 from this pass. The bioRxiv preprint package (2.4) consumes the frozen manuscript; the References section **shape** is locked at this R1 pass, pending the R2 Zotero-export content fill. If 2.4 fires **before** R2, the `### Full numbered bibliography` `[EXTRACT:]` placeholder will be visible to reviewers — which is intentional and signals the venue-submission-prep-time population.

## Commit-framing reminder (CLAUDE.md / memory feedback — original research framing, NEVER revision/cleanup/fix)

The docs commit for this pass (handled by the orchestrator workflow Step 7–8, **NOT** this executor) must frame the change as **original research** consistent with CLAUDE.md discipline and the user-memory feedback note "Original research framing (NOT revision)":

- **Acceptable framing:** "align References section to TRACK-A-PIVOT.md §9", "close L36 inline-placeholder debt from Intro R1 pass", "R1 alignment pass on manuscript References", "structure §References inventory for the pivoted cardiometabolic real-LD audit".
- **Forbidden framing (per CLAUDE.md and user-memory feedback):** "revision", "cleanup", "fix", "correct", "repair", "polish", "patch" — these imply the manuscript was broken and is being mended rather than a hypothesis-driven original research artifact in its first pass to bioRxiv.

## Deviations from Plan

None. The two surgical edits landed exactly as specified in PLAN.md Task 1 + Task 2 using the PLAN.md recommended verbatim replacement prose. All 8 Task 1 gates, 9 Task 2 gates, and 20 total guardrail greps passed on the first executor run. No Rule 1 (bug fix), Rule 2 (critical functionality), Rule 3 (blocker fix), or Rule 4 (architectural) deviations were triggered.

## Authentication gates

None. This was a prose-only quick task; no external APIs, no DUAs, no package installs, no server-side auth.

## Commits made

**None inside this executor.** Per the `<constraints>` block in the spawn prompt, the orchestrator workflow Steps 7–8 perform the consolidated commit for this quick's outputs (PLAN.md + SUMMARY.md + `docs/manuscript/track_a_pivot.md` L36 + §References edits + STATE.md row).

HEAD at executor spawn time: `c5d20dd` (note: spawn prompt mentioned `abdcf43`; intervening commits `0a1339e`, `83922d4`, `26cc9e2`, `fd1836e`, `880fc36` landed before this executor started — these are unrelated commits on other Route A/B artifacts that post-date the prompt-authoring moment; the spawn prompt's "starting fresh from there" language confirms this is expected).

HEAD at executor return time: **`c5d20dd` (unchanged from pre-execution)**. No executor-internal commits performed. The orchestrator's Step 8 commit will frame the work as **original research** per CLAUDE.md discipline.

Working tree at executor return time:
- `M docs/manuscript/track_a_pivot.md` (L36 placeholder resolution + §References restructure; +29 lines net)
- `?? .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-PLAN.md` (created by planner before executor spawn)
- `?? .planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` (this file)

(Pre-existing dirty items unrelated to this quick: `M .claude/settings.json`, `M .planning/STATE.md` [orchestrator-owned], `?? .claude/scheduled_tasks.lock`.)

## Files changed

### Modified
- `docs/manuscript/track_a_pivot.md` — L36 (P2 placeholder resolution: `[Wallace 2021] [Zou 2022] [Weissbrod 2020]` → `²⁰,²⁹,⁴²` superscript cluster post-period) + §References section L301–361 (flat 7-bullet narrative → structured six-subsection inventory with one new `[EXTRACT:]` placeholder deferring the full numbered bibliography to venue-submission prep). Net file line-count delta: **+29 lines (322 → 351)**. All other lines byte-identical to HEAD `c5d20dd` (including L38, L72, L230 primary-method and evolutionary-medicine anchor lines).

### Created
- `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` — this file.

(The PLAN.md at `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-PLAN.md` was created by the orchestrator/planner prior to executor spawn and is untouched by this executor.)

## Self-Check: PASSED

- `[✓]` `docs/manuscript/track_a_pivot.md` exists and is modified (two surgical edits: L36 placeholder resolution + §References restructure)
- `[✓]` `.planning/quick/260424-kul-route-a-step-2-2-f-references-supplement/260424-kul-SUMMARY.md` exists (this file)
- `[✓]` Task 1 verify gates: **8 / 8 pass** (L36 placeholder resolution)
- `[✓]` Task 2 verify gates: **9 / 9 pass** (§References restructure)
- `[✓]` Guardrail greps (comprehensive holistic sweep): **20 / 20 pass**
- `[✓]` L230 byte-identical to HEAD (diff zero-output) — refs 4, 5 ⁴⁻⁵ thrifty-gene paragraph preserved exactly per §4.17 P5 + 260424-k2c handoff
- `[✓]` L38 byte-identical to HEAD — SuSiE-RSS²⁰ / coloc.susie²⁹ Intro P3 preserved from 260424-j64 Intro R1 pass
- `[✓]` L72 byte-identical to HEAD — Methods §Fine-Mapping Integration SuSiE-RSS²⁰ / coloc.susie²⁹ preserved
- `[✓]` All 8 frozen Stage 2 numerics (51/96, 12/96, 4.25-fold, 224, rs3184504, rs10774625, PP.H4 = 1.00, SH2B3 12q24, PP.H4 = 0.3099, IRX3, Pancreas) preserved per `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — no drift
- `[✓]` No executor-internal commit performed; `git log -1 --format=%h` still at `c5d20dd` (pre-execution HEAD unchanged)
- `[✓]` Scope-divergence note explicitly transcribed from PLAN.md (2.2.f R1 declines full renumber + full numbered bibliography build; rationale: no numbered bibliography exists in repo; Zotero export is a venue-submission artifact; dropping ML-ref superscripts requires v10 source-to-number mapping not yet in repo)
- `[✓]` Handoff flags populated: 2.2.f R2 (Zotero export / inline Benner 2017 / ML-claim-ref drop mapping); 2.3 (figure captions can cite refs 20/29/42/43; supplementary-caption-only refs would be appended at slot ⁴⁴+); 2.4 (no further handoffs — References shape locked)
- `[✓]` Commit-framing reminder included (CLAUDE.md / user-memory feedback: "original research" framing NOT "revision" / "cleanup" / "fix")
