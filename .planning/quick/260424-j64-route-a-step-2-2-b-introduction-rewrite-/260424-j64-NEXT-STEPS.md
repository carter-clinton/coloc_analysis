# Route A — Remaining Steps After 2.2.b (Hand-Off Brief)

_Generated during /gsd-quick 260424-j64 (2026-04-24). Parent plan:
`/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.2.e–2.4. Source-of-truth
edit specs live in `.planning/amendments/TRACK-A-PIVOT.md`._

## Critical path summary

| Order | Step | Blocking input | Parallel-feasible with |
| --- | --- | --- | --- |
| 1 | 2.2.b (this session, DONE) | — | — |
| 2 | 2.2.e Discussion rewrite | 2.2.b tone | — |
| 3 | Pathway Results re-compute (may need separate /gsd-quick) | real-LD pathway outputs on disk | 2.3 figure 1/2 scripts |
| 4 | 2.2.f References + supplementary | 2.2.e + Methods placeholders | 2.3 figure 3 script |
| 5 | 2.3 Figures × 3 | frozen numbers + pathway re-compute | 2.2.f |
| 6 | 2.4 bioRxiv preprint package + submit | 2.2.e, 2.2.f, 2.3 all DONE | — |

All sumstats and coloc outputs are already on disk; no re-download needed.

---

## 2.2.e — Discussion rewrite (R1)

**Source of truth:** `.planning/amendments/TRACK-A-PIVOT.md` §4.17 (lines 137–144).

**Scope:** refine-don't-rebuild pass over Discussion subsections in
`docs/manuscript/track_a_pivot.md`:
  - Opening paragraph — identity-LD inflation headline; SH2B3 BMI–stroke collapse
    (identity-LD PP.H4 = 1.00 at rs3184504 / rs10774625 → absent from Stage 2
    `coloc.susie` output manifest).
  - Metabolic Syndrome as Pathway-Defined Entity — retain only if pathway
    enrichment survives real-LD; otherwise cut to a one-paragraph null report.
  - Asthma-Metabolic Axis — likely remove entirely (NEGR1/FTO/FADS1
    identity-LD-sourced; drop "omega-3 supplementation" framing regardless).
  - Variant Mechanisms — drop all drug-repurposing claims
    (MC4R-setmelanotide, PCSK9-evolocumab, KCNJ11-sulfonylureas,
    FADS-targeted PUFA therapy). Retain one descriptive paragraph on
    regulatory-dominated architecture from aggregated CADD/PolyPhen/SIFT/GTEx
    annotations.
  - Evolutionary Medicine — demote three paragraphs to a single ~120-word
    speculative paragraph, clearly marked as interpretive context not
    hypothesis-tested claim.
  - Cross-Ancestry Health Equity — remove the "concordant null = shared
    biology" claim; replace with the "concordant nulls are indistinguishable
    from both-ancestry underpowering" disclaimer verbatim.
  - Strengths / Limitations / Future Directions — rewrite per §4.17 final
    bullets; enumerate the six limitations already drafted in the current
    text and verify all survive after 2.2.e.

**Dependencies:** 2.2.b Introduction R1 (for tone consistency — Discussion
opening must match the Introduction's "produces apparent overlap" inflection).

**Estimated effort:** 90–150 min (larger than 2.2.b — more subsections,
some require pathway-result look-ups).

**Proposed command:**
`/gsd-quick Route A Step 2.2.e Discussion rewrite (R1) for docs/manuscript/track_a_pivot.md against TRACK-A-PIVOT.md §4.17`

**Success gate:**
  - `grep -E "setmelanotide|evolocumab|sulfonylurea|omega-3 supplementation"
     docs/manuscript/track_a_pivot.md` returns zero matches in the Discussion
    line range (lines ~212–246).
  - Evolutionary Medicine subsection in Discussion is ≤ 1 paragraph and
    ≤ 150 words.
  - Cross-Ancestry subsection contains the "concordant nulls are
    indistinguishable from both-ancestry underpowering" disclaimer verbatim.
  - Discussion opening paragraph cites the SH2B3 BMI–hypertension /
    hypertension–stroke collapse (identity-LD PP.H4 = 1.00 at canonical leads
    → real-LD trait-pair absent from Stage 2 `coloc.susie` output manifest).
  - No "revision" / "cleanup" framing anywhere in the edited prose.

---

## 2.2.f — References + supplementary

**Source of truth:** `.planning/amendments/TRACK-A-PIVOT.md` §9 (lines 280–301).

**Scope:**
  - **Add:** Giambartolomei 2014 (coloc.abf primary, now framed as the method
    under audit); Wallace 2020 (eliciting priors); Wallace 2021 PLoS Genet
    17:e1009440 (coloc.susie); Zou 2022 PLoS Genet 18:e1010299 (SuSiE-RSS —
    promote to primary); Weissbrod 2020 Nat Genet 52:1355 (functional
    fine-mapping / LD-mismatch); Benner 2016 (FINEMAP comparator); Foley 2021
    Nat Commun 12:764 (multi-trait coloc); Kanai 2022 Cell Genom 2:100210
    (meta-analysis fine-mapping calibration / LD mismatch); plus one 2023–2025
    LD-reference-panel review (Carter to pick at freeze).
  - **Demote / drop:** refs 4–5 (Neel 1962 thrifty-gene, Williams 1957
    antagonistic-pleiotropy) if Evolutionary Medicine is compressed to a
    single paragraph per §4.17; drop all refs formerly supporting "ML-based"
    framing (review refs 37–41 — retain only as annotation sources).
  - **Retain:** GIANT / DIAMANTE / ICBP / GIGASTROKE / TAGC / MEDIA / SIREN /
    CAAPA GWAS sources (these are the provenance of the claims under audit);
    Open Targets, GWAS Catalog, CADD, PolyPhen-2, SIFT, KEGG, Reactome, GO,
    OMIM, ClinVar, Roadmap, STRING, DGIdb, ChEMBL, gnomAD (annotation
    sources); Martin 2019 PRS-transportability (Cross-Ancestry limitation).
  - **Resolve placeholders:** every `[Wallace 2021]` / `[Zou 2022]` /
    `[Weissbrod 2020]` inline bracket left by 2.2.b becomes the final
    superscript number. Introduction currently contains exactly three such
    placeholders (one each) at the end of paragraph 2 (line 36); 2.2.e may
    add more during Discussion rewrite.
  - **Renumber:** every inline citation in Abstract, Introduction, Methods,
    Results, Discussion, Conclusion is re-walked once the final References
    list is locked.
  - **Supplementary tables S1–S6 sanity check:** Table S1 provenance refs,
    Table S6 harmonization-diagnostics per §4.12.

**Dependencies:** 2.2.b (Introduction placeholders to resolve); 2.2.e
(Discussion citations may shift after the rewrite, so run 2.2.f after 2.2.e
to avoid double-renumbering).

**Estimated effort:** 60–120 min (mostly mechanical but error-prone;
recommend a final `grep -nE "\[(Wallace|Zou|Weissbrod)[^]]*\]" docs/manuscript/track_a_pivot.md`
sweep to catch orphan placeholders).

**Proposed command:**
`/gsd-quick Route A Step 2.2.f References renumber + supplementary check against TRACK-A-PIVOT.md §9`

**Success gate:**
  - `grep -c "Wallace 2021\|Zou 2022\|Weissbrod 2020\|Benner 2016\|Kanai 2022"
     docs/manuscript/track_a_pivot.md` ≥ 4 unique author-year matches in the
    References section (Methods + Introduction + Discussion body coverage
    expected via numeric superscripts only).
  - Zero bracketed author-year placeholders remain in the manuscript body:
    `grep -c "\[Wallace\|\[Zou\|\[Weissbrod" docs/manuscript/track_a_pivot.md`
    equals 0.
  - Every numeric superscript in the manuscript body has a matching entry in
    the References section (manual spot-check of the first, middle, last
    five numbers is sufficient).

---

## 2.3 — Figures (three R scripts)

**Source of truth:** `/home/ckclinto/.claude/plans/snappy-humming-pine.md`
§2.3; `.planning/amendments/TRACK-A-PIVOT.md` §5 (figure legends).

**Scope:** three R/ggplot2 build scripts under `src/R/figures/`:
  - **Fig 1 — CS yield (identity-LD vs real-LD).** Inputs:
    `results/fine_mapping/finemap_summary.tsv` +
    `results/fine_mapping/finemap_summary_augmented.tsv`. Headline numbers
    (locked to `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`):
    12/96 identity-LD vs 51/96 real-LD non-empty credible sets at admissible
    regions (4.25× yield).
  - **Fig 2 — SH2B3 12q24 locus plot.** Inputs: `results/multitrait/coloc_susie/`
    (locate SH2B3 JSON or equivalent locus file), Stage 1d identity-LD
    PP.H4 = 1.00 BMI–hypertension / hypertension–stroke at rs3184504 /
    rs10774625 vs Stage 2 real-LD absence from manifest. LocusZoom-style
    panel (GWAS Manhattan, fine-map credible-set shading, recombination
    overlay, identity-vs-real LD matrix diagonals for contrast).
  - **Fig 3 — Pathway enrichment reconfiguration.** Inputs:
    `results/pathway/` (requires pathway Results re-compute on real-LD
    surviving gene set — this re-compute may itself need a separate
    /gsd-quick session before Fig 3 is buildable). Side-by-side
    fold-enrichment (KEGG / Reactome / GO) identity-LD vs real-LD.

**Outputs:** PDF + PNG per figure under `docs/manuscript/figures/`.

**R environment:** first check whether `envs/smoke_dev` already contains
ggplot2, patchwork, scales, and a LocusZoom-compatible panel library (e.g.
`locuszoomr` or a hand-rolled panel constructor). If not, create a new
`envs/figures_R.yml` (R 4.3+, ggplot2, patchwork, scales, cowplot,
data.table, locuszoomr or equivalent). Do NOT add heavy Python deps —
figures are pure R.

**Dependencies:**
  - `TRACK-A-FROZEN-NUMBERS.md` numerics (must not drift — verify each
    figure script reads the TSV directly, not from a second copy of the
    numbers).
  - Pathway Results re-compute (Fig 3 only — may run as a separate
    /gsd-quick before Fig 3 script is written).

**Estimated effort:** ~45–75 min per figure → 3 figures × 3 /gsd-quick
sessions ≈ 2.5–4 hours total. Split across sessions to keep each atomic
and reviewable.

**Proposed commands (three separate sessions):**
  - `/gsd-quick Route A Step 2.3 build Figure 1 (CS yield identity-LD vs real-LD)`
  - `/gsd-quick Route A Step 2.3 build Figure 2 (SH2B3 12q24 locus collapse)`
  - `/gsd-quick Route A Step 2.3 build Figure 3 (pathway enrichment reconfiguration)`

**Success gate (per figure):**
  - `src/R/figures/fig{1,2,3}.R` exits 0 under the pinned R env
    (`envs/smoke_dev` or `envs/figures_R.yml`).
  - Writes both `docs/manuscript/figures/fig{1,2,3}.pdf` AND
    `docs/manuscript/figures/fig{1,2,3}.png`.
  - Headline numbers match TRACK-A-FROZEN-NUMBERS.md verbatim (no drift —
    grep the generated figure caption or metadata against the frozen file).

---

## 2.4 — bioRxiv preprint (package + manual submit)

**Source of truth:** `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.4.

**Scope:**
  - Build a submission-ready PDF from the Markdown draft (pandoc →
    Genome Medicine-compatible template, LaTeX fallback if pandoc chokes on
    figure embedding).
  - Embed Figures 1–3 at Markdown-referenced anchor points; confirm
    supplementary figures S1–S6 status (build or defer per §4.20).
  - Prepare cover letter, competing-interests statement, funding statement,
    author affiliations (ASHES Lab + NCSU Biological Sciences) — per
    bioRxiv submission UI field names.
  - Manual web-UI submission at biorxiv.org (Carter action — bioRxiv does
    not expose a scripted submission API; `/gsd-quick` stops at package
    preparation).
  - Log the returned DOI + page URL to `.planning/amendments/BIORXIV-TRACK-A.md`
    (create the file if absent) + STATE.md row + repo tag
    `M1-BIORXIV-TRACK-A-POSTED-YYYY-MM-DD` (tag format TBD per
    project conventions).

**Prerequisites (all gate 2.4):**
  - 2.2.b Introduction R1 DONE (this session).
  - 2.2.e Discussion R1 DONE.
  - 2.2.f References + supplementary DONE.
  - 2.3 Figures 1–3 DONE.
  - Every `[EXTRACT: …]` placeholder in `track_a_pivot.md` either resolved
    OR explicitly deferred to venue-specific submission-only fill.

**Subject categories (bioRxiv web UI):** primary = Genetics; secondary =
Genomics.

**Dependencies:** 2.2.e, 2.2.f, 2.3 all complete. Carter's bioRxiv
account + institutional affiliation must be pre-registered (check before
starting 2.4).

**Estimated effort:**
  - Package prep (/gsd-quick): 60–120 min.
  - Carter web-UI submission: 30–60 min (outside the /gsd-quick command).

**Proposed command:**
`/gsd-quick Route A Step 2.4 prepare bioRxiv submission package for track_a_pivot.md`

**Success gate:**
  - `docs/manuscript/track_a_pivot.pdf` exists and is human-readable.
  - All three figures embedded at marker locations.
  - `docs/manuscript/cover_letter.pdf`, `docs/manuscript/coi_statement.md`,
    `docs/manuscript/funding_statement.md` exist.
  - After Carter's manual web-UI submission: bioRxiv DOI + page URL logged
    to `.planning/amendments/BIORXIV-TRACK-A.md`; STATE.md row appended;
    repo tag pushed.

---

## Parallelism notes

  - 2.2.f References renumber and 2.3 Figure 3 pathway script are both
    gated on the pathway Results re-compute. Sequence: pathway re-compute
    first → then 2.2.f and Fig 3 in parallel is safe (disjoint file sets).
  - Fig 1 and Fig 2 have no shared inputs with 2.2.f or 2.2.e — buildable
    in parallel with those prose edits if a second terminal is convenient.
  - 2.4 is a hard fan-in — all upstream steps must DONE.

## STATE.md integration

Each step closeout should:
  1. Append a row to `.planning/STATE.md` under the same Session Continuity
     pattern used by 260423-osk and 260424-mxp.
  2. Append a DEC entry to `.planning/DECISIONS.md` IF a substantive
     scope/framing decision was made inside the step (not for routine
     edits).
  3. Update `.planning/STATE.md` `Last session:` timestamp and
     `Stopped at:` line per the project convention.
