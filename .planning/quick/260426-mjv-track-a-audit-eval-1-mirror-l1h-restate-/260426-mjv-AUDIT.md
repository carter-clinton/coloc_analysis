---
quick_id: 260426-mjv
audit_phase: pre-task
audit_date: 2026-04-26
mirror_precedent: 260426-l1h
total_inventory_lines: 54
files_inventoried: 3
classification_dispositions:
  MATCH: already carries L1H pattern in functional form (skip; no-op)
  DRIFT-A: has SUPERSEDED token but lacks per quick-260425-kki attribution (apply Pattern A upgrade)
  DRIFT-B: discusses 12/96 supersedure but lacks SUPERSEDED token AND surface admits formal annotation (apply if appropriate; SKIP for manuscript abstract/results/discussion prose)
  MATCH-PROSE: uses prose framing appropriate to surface (manuscript abstract/results/discussion); explicit formal annotation would violate original-research framing rule
  N/A: non-comparator context (disk-truth scalar, runtime assertion, historical reconciliation row, ghost-numerics line)
---

# Quick Task 260426-mjv — Pre-Task Site Classification Audit

## Inputs

- Pre-task inventory: `site_inventory_pre.txt` (54 lines, 3 files)
- Pre-task md5s: `md5_pre.txt`, `md5_pre_fig2_L71_82.txt`, `md5_pre_fig2_L99_138.txt`, `md5_pre_manuscript_prose_L28_L82_L138_L216.txt`, `md5_pre_frozen_L1_L200.txt`
- HEAD: `2aef19e23d2b3ff64513ef3f9b41f7ad081685ae`
- Branch: `main`

## Per-site classification table

### File 1 — `docs/manuscript/track_a_pivot.md` (8 inventory lines)

| Inventory line | File line | Context | Snippet (excerpt) | Classification | Rationale |
|---|---|---|---|---|---|
| 45 | L28 | Abstract | "Under matched-coverage identity-LD baseline (k2d full-coverage re-fire, 2026-04-25), SuSiE-RSS yielded 48 of 95 (50.5%) ... 1.06-fold ... The previously cited 4.25-fold contrast against a 12/96 baseline reflected a partial-coverage Stage 1d narrow-validation run ..." | **MATCH-PROSE** | Manuscript abstract — original-research voice. Comparator-tightening narrative present in natural prose form ("previously cited", "partial-coverage Stage 1d narrow-validation run"). Adding `per quick-260425-kki` here would violate Carter framing rule. SKIP. |
| 46 | L80 | Methods §Admissibility | "The k2d identity-LD re-fire (2026-04-25) enumerated 95 of 96 ... `bmi.EUR.APOE_19q13` ... 48 of 95 (50.5%) ... 51 of 96 (53.1%) ... 1.06-fold ratio ..." | **MATCH** | Methods prose; no 12/96 / 4.25 surface; describes only the live K2D matched-coverage comparator. SKIP (no edit needed). |
| 47 | L82 | Results §Yield | "(An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline; that freeze covered only 2 of 10 admissible regions on the identity-LD branch and is not the appropriate matched-coverage comparator. We tightened the comparator to k2d full-coverage and the inflation magnitude shifted from 4.25× to 1.06×.)" | **MATCH-PROSE** | Manuscript Results body — original-research voice. Comparator-tightening narrative present in prose form using anchor language ("we tightened the comparator and the inflation magnitude shifted"). SKIP. |
| 48 | L138 | Headline result | "An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline; that freeze covered only 2 of 10 admissible regions on the identity-LD branch and is not the appropriate matched-coverage comparator. We tightened the comparator and the inflation magnitude shifted ..." | **MATCH-PROSE** | Manuscript Results body — original-research voice. Same comparator-tightening narrative in prose form. SKIP. |
| 49 | L140 | Tier C disclosure | (no 12/96 / 4.25 surface; cites SH2B3 0.0385 and Tier C scalars) | **N/A** | Different subject (Tier C real-LD data-quality disclosure); not Eval-1 comparator. SKIP. |
| 50 | L216 | Discussion | "The earlier 4.25-fold contrast against a 12/96 partial-coverage baseline reflected a Stage 1d narrow-validation comparator; under the tightened k2d full-coverage comparator the operative inflation signal is structural rather than count-level." | **MATCH-PROSE** | Manuscript Discussion body — original-research voice. Comparator-tightening narrative in natural prose. SKIP. |
| 51 | L224 | Discussion §Pathway | "(48/95 identity-LD vs 51/96 real-LD under the matched-coverage k2d full-coverage comparator)" | **MATCH** | Live K2D matched-coverage citation only; no 12/96 / 4.25 surface. SKIP. |
| 52 | L254 | Conclusions bullet | "(1.06-fold count-level differential), but the flagship SH2B3 12q24 EUR trait-pairs ... PP.H4 = 1.00 under identity-LD ..." | **MATCH** | Live K2D matched-coverage citation only; no 12/96 / 4.25 surface. SKIP. |
| 53 | L295 | **Figure 2 caption** | "An earlier Stage 1d narrow-validation freeze had cited 12/96 as the identity-LD baseline (now superseded; see `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` for the audit trail)." | **DRIFT-A** | Figure caption — formal annotation surface. Has SUPERSEDED phrasing ("now superseded; see ... for the audit trail") and audit-trail pointer, but lacks formal `per quick-260425-kki` attribution mirroring L1H Pattern A. **APPLY Pattern A upgrade.** |
| 54 | L297 | Figure 3 caption | (no 12/96 / 4.25 surface; SH2B3 case-study panel A/B descriptors) | **N/A** | Different figure (Fig 3, SH2B3 collapse); not Eval-1 comparator. SKIP. |

**Edits required for File 1: 1** (L295 only).

### File 2 — `src/R/figures/fig2_cs_yield.R` (26 inventory lines)

| Inventory line | File line | Context | Snippet (excerpt) | Classification | Rationale |
|---|---|---|---|---|---|
| 1 | L5 | Header purpose | "(48 / 95) vs real 1000G Phase 3 EUR LD (51 / 96)" | **MATCH** | Pattern B citation already present (matched-coverage k2d). SKIP. |
| 2 | L6 | Header purpose | "Under the matched-coverage comparator the contrast is ~1.06x fold" | **MATCH** | Pattern B citation already present. SKIP. |
| 3 | L10 | Header "Comparator-tightening note" — opener | "# Comparator-tightening note (quick-260425-kki, 2026-04-25):" | **DRIFT-A** | Note-block opener cites `quick-260425-kki` as historical event but the SUPERSEDED token below at L15-16 lacks the `per quick-260425-kki` attribution + the matched-coverage citation in the body lacks Pattern B verbatim form `(48/95 vs 51/96 = 1.06x yield)`. **APPLY Pattern A + Pattern B upgrade as a single hunk L10-17.** |
| 4 | L12 | Header note body | "validation baseline (12/96, 2 of 10 admissible regions had identity-LD" | **DRIFT-A** | Inside the L10-17 hunk to upgrade. SUPERSEDED 12/96 baseline preserved verbatim. |
| 5 | L13 | Header note body | "fits) to the k2d full-coverage 2026-04-25 re-fire (48/95, all" | **DRIFT-A** | Inside L10-17 hunk; upgraded to Pattern B verbatim form `(48/95 vs 51/96 = 1.06x yield)`. |
| 6 | L15 | Header note body | "4.25x to ~1.06x. The 12/96 baseline is preserved verbatim with a" | **DRIFT-A** | Inside L10-17 hunk; preserved verbatim under SUPERSEDED markup. |
| 7 | L16 | Header note body | "SUPERSEDED 2026-04-25 markup in TRACK-A-FROZEN-NUMBERS.md for audit" | **DRIFT-A** | Inside L10-17 hunk; SUPERSEDED token has no `per quick-260425-kki` attribution → upgrade to "SUPERSEDED 2026-04-25 per quick-260425-kki markup". |
| 8 | L23 | Source-pointer comment | "(k2d full-coverage identity-LD re-fire, 2026-04-25 — 96 lines = 1 header + 95 fits.)" | **MATCH** | Pattern B citation present. SKIP. |
| 9 | L29 | Source-pointer comment | "(canonical source of the 48 / 95 / 51 / 96 / 1.06x matched-coverage" | **MATCH** | Pattern B citation present. SKIP. |
| 10 | L30 | Source-pointer comment | "contrast; if Stage 2 or k2d numbers ever shift, update that file" | **MATCH** | Pattern B context. SKIP. |
| 11 | L48 | Author byline | "comparator-tightened quick-260425-kki 2026-04-25)" | **MATCH** | Author attribution line — already cites `quick-260425-kki`. SKIP. |
| 12 | L60 | Header design note | "coverage scalars (48 / 95 / 51 / 96 / 1.06x) are anchored at" | **MATCH** | Pattern B citation present. SKIP. |
| 13 | L71 | Disk-truth scalar block header | "# --- Disk-truth scalars (matched-coverage k2d re-fire 2026-04-25) ---" | **N/A** | Inside L71-82 disk-truth scalar block — MUST be byte-identical pre vs post. SKIP. |
| 14 | L73 | Disk-truth scalar block | "below and the assertions hard-fail if any value drifts. If k2d or Stage 2 are" | **N/A** | Inside L71-82 disk-truth scalar block. SKIP. |
| 15 | L77 | Disk-truth scalar block | "# k2d identity-LD full-coverage re-fire (2026-04-25); disk-truth source." | **N/A** | Inside L71-82 disk-truth scalar block. SKIP. |
| 16 | L79 | Disk-truth scalar block | `N_IDENTITY_LD_TOTAL_EXPECTED <- 95L     # k2d enumerated 95 of 96 fits` | **N/A** | Machine scalar inside L71-82 disk-truth block. SKIP. |
| 17 | L116 | Runtime assertion comment | "# Disk-backed derivation for identity-LD baseline (matched-coverage k2d, 2026-04-25)" | **N/A** | Inside L99-138 runtime assertion block — MUST be byte-identical. SKIP. |
| 18 | L132 | Runtime assertion error template | `"expected k2d full-coverage value %d from IDENTITY-LD-K2D-FIT-SUMMARY.tsv. ",` | **N/A** | Inside L99-138 runtime assertion block. SKIP. |
| 19 | L133 | Runtime assertion error template | `"If k2d has been re-fired, update the expected scalar here and TRACK-A-FROZEN-NUMBERS.md ",` | **N/A** | Inside L99-138 runtime assertion block. SKIP. |
| 20 | L155 | Diagnostic message | `message(sprintf("Identity-LD non-empty fits (k2d full-coverage 2026-04-25): %d / %d",` | **MATCH** | Pattern B cited; not in protected block. SKIP. |
| 21 | L160 | Diagnostic message | "Identity-LD baseline (disk-derived from IDENTITY-LD-K2D-FIT-SUMMARY.tsv, k2d full-coverage 2026-04-25)" | **MATCH** | Pattern B cited. SKIP. |
| 22 | L167 | Plot factor label | `lvl_id   <- "Identity-LD fallback\n(k2d 2026-04-25)"` | **MATCH** | Pattern B cited. SKIP. |
| 23 | L224 | Plot subtitle | "Real 1000G Phase 3 EUR LD vs identity-LD fallback (k2d full-coverage 2026-04-25) -- ~1.06x fold increase under matched-coverage comparator" | **MATCH** | Pattern B cited. SKIP. |
| 24 | L229 | Plot caption text | ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (k2d full-coverage identity-LD, 2026-04-25)" | **MATCH** | Pattern B cited. SKIP. |
| 25 | L230 | Plot caption text | "Matched-coverage comparator: 48 of 95 identity-LD fits vs 51 of 96 real-LD fits = ~1.06x yield." | **MATCH** | Pattern B verbatim. SKIP. |
| 26 | L258 | Final diagnostic message | `message(sprintf("fold-change: %.3fx (%d real-LD / %d identity-LD k2d)",` | **MATCH** | Pattern B cited. SKIP. |

**Edits required for File 2: 1 hunk** (L10-17 header "Comparator-tightening note" only).

### File 3 — `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (18 inventory lines)

| Inventory line | File line | Context | Snippet (excerpt) | Classification | Rationale |
|---|---|---|---|---|---|
| 27 | L10 | Live block heading | "## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE" | **MATCH** | Pattern B in heading. SKIP. |
| 28 | L15 | Live block table | `\| Stage 2 non-empty credible sets \| **51 / 96 (53.1%)** \|` | **MATCH** | Pattern B verbatim. SKIP. |
| 29 | L16 | Live block table | `\| Total k2d full-coverage identity-LD fits \| 95 ...` | **MATCH** | Pattern B verbatim. SKIP. |
| 30 | L17 | Live block table | `\| k2d identity-LD non-empty credible sets \| **48 / 95 (50.5%)** \|` | **MATCH** | Pattern B verbatim. SKIP. |
| 31 | L18 | Live block table | `\| **Matched-coverage fold change** \| **51 / 48 = 1.06× yield increase** \|` | **MATCH** | Pattern B verbatim. SKIP. |
| 32 | L19 | Status distribution | `\| Status distribution (k2d identity-LD) \| 65 ok / 24 too_many_variants / 6 no_variants \|` | **MATCH** | Pattern B context. SKIP. |
| 33 | L20 | n_CS distribution | `\| n_CS distribution (k2d identity-LD) \| ...` | **MATCH** | Pattern B context. SKIP. |
| 34 | L22 | Headline framing | "We tightened the comparator from a partial-coverage Stage 1d narrow-validation baseline (12/96, only 2 of 10 admissible regions had identity-LD fits at the time of freeze) to the k2d full-coverage 2026-04-25 re-fire (48/95 ...). The inflation magnitude shifted from 4.25× to 1.06× under the tightened comparator." | **MATCH** | Anchor language verbatim; comparator-tightening narrative present. SKIP. |
| 35 | L24 | Sources footnote | "k2d 2026-04-25 fire summary" | **MATCH** | Pattern B cited. SKIP. |
| 36 | L26 | Denominator note | "The k2d identity-LD re-fire enumerated 95 of 96 region × ancestry × trait fits at admissibility ..." | **MATCH** | Pattern B context. SKIP. |
| 37 | L63 | Stage 2 sub-row | `\| Non-empty credible sets \| **51 / 96 (53.1%)** \|` | **MATCH** | Pattern B verbatim. SKIP. |
| 38 | L70 | SUPERSEDED block (12/96) | "~~Identity-LD baseline (pre-Stage-2): **12 / 96 non-empty credible sets (12.5%)** per prior STATE.md session continuity.~~" | **MATCH** | Inside SUPERSEDED block; preserved verbatim under strikethrough. SKIP. |
| 39 | L72 | SUPERSEDED block (4.25×) | "~~**Headline yield delta**: 12/96 → 51/96 = **4.25× fold increase ...**~~" | **MATCH** | Inside SUPERSEDED block; preserved verbatim under strikethrough. SKIP. |
| 40 | L74 | **SUPERSEDED block kki attribution** | "> **SUPERSEDED 2026-04-25** — preserved verbatim for audit traceability. ... The matched-coverage k2d full-coverage 2026-04-25 re-fire produces 48/95 = 50.5% (see top of this document for the live block). The fold-change shifted from 4.25× to ~1.06× under the tightened comparator. Manuscript edits propagated quick-260425-kki." | **MATCH** | SUPERSEDED token present + `quick-260425-kki` attribution present (in functional form via "Manuscript edits propagated quick-260425-kki"). Already carries L1H Pattern A. SKIP. |
| 41 | L166 | HLA SUPERSEDED block | "> **SUPERSEDED 2026-04-26** — ... Manuscript edits propagated by quick-260425-t9j." | **N/A** | Different audit finding (Eval 3.7/3.8 HLA reclassification, not Eval-1). SKIP. |
| 42 | L209 | Reconciliation log row (kki) | "\| 2026-04-25 \| **Comparator tightened** ... \| quick-260425-kki — Track A audit-driven figure correction pass. ..." | **MATCH** | kki cited; functional form complete. SKIP. |
| 43 | L210 | Reconciliation log row (04b) | "\| 2026-04-26 \| **H3 LD-reference-quality dose-response scalars frozen** ... \| quick-260426-04b ..." | **N/A** | Different finding (H3 dose-response, not Eval-1). SKIP. |
| 44 | L211 | Reconciliation log row (t9j) | "\| 2026-04-26 \| **HLA reclassification + negative-control N restatement** ... \| quick-260425-t9j ..." | **N/A** | Different finding (HLA reclassification, not Eval-1). SKIP. |

**Edits required for File 3: 1 row append** (one new 2026-04-26 reconciliation-log row in the L201–L212 block, inserted as the last 2026-04-26 row to preserve chronological+slug order). The L1-L200 content remains byte-identical.

## Summary across files

| File | Sites inventoried | MATCH | DRIFT-A | DRIFT-B | MATCH-PROSE | N/A | Edits |
|---|---|---|---|---|---|---|---|
| `docs/manuscript/track_a_pivot.md` | 10 | 3 | 1 | 0 | 4 | 2 | 1 (L295 Figure 2 caption) |
| `src/R/figures/fig2_cs_yield.R` | 26 | 14 | 5 (single hunk L10-17) | 0 | 0 | 7 | 1 hunk (L10-17 header note) |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | 18 | 13 | 0 | 0 | 0 | 5 | 1 row append in L201-L212 block |
| **TOTAL** | **54** | **30** | **6 (in 2 hunks)** | **0** | **4** | **14** | **3 atomic commits** |

## Conclusions

1. **DRIFT-A sites** are confined to two surfaces appropriate for formal annotation:
   - `docs/manuscript/track_a_pivot.md` L295 Figure 2 caption (formal-annotation surface; figure captions admit `per quick-260425-kki` attribution).
   - `src/R/figures/fig2_cs_yield.R` L10-17 header "Comparator-tightening note" (R-script comment header; admits formal annotation per Carter framing rule).
2. **MATCH-PROSE sites** are confined to manuscript abstract (L28), Results body (L82, L138), and Discussion body (L216) — original-research voice locked per Carter framing rule. These are byte-identical pre vs post.
3. **MATCH sites** already carry the L1H pattern in functional form. Includes the FROZEN-NUMBERS L74 SUPERSEDED block (already carries kki attribution as "Manuscript edits propagated quick-260425-kki") and the L209 reconciliation row (kki cited).
4. **N/A sites** are protected — disk-truth scalar block (fig2 L71-82), runtime assertion block (fig2 L99-138), and historical reconciliation rows for non-Eval-1 audits (FROZEN-NUMBERS L210 = 04b H3, L211 = t9j HLA, L166 = HLA SUPERSEDED block).
5. **No DRIFT-B sites detected** — every Eval-1 12/96 / 4.25 mention either carries the comparator-tightening narrative (manuscript prose) or sits inside an already-functional SUPERSEDED context.

## Edit plan (3 atomic commits)

1. Task 1: `docs/manuscript/track_a_pivot.md` L295 only — Pattern A upgrade.
2. Task 2: `src/R/figures/fig2_cs_yield.R` L10-17 only — Pattern A + Pattern B upgrade as a single hunk.
3. Task 3: `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — append one 2026-04-26 reconciliation-log row in L201-L212 block.
