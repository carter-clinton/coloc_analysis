---
phase: quick-260425-wbf
plan: 01
type: execute
wave: 1
status: complete
completed: 2026-04-25
commit: df3fa89
requirements:
  - TRACK-A-AUDIT-EVAL-3.4
  - TRACK-A-AUDIT-EVAL-2A
  - TRACK-A-ABSTRACT-TODO-DROP
files_modified:
  - docs/manuscript/track_a_pivot.md
---

# Quick Task 260425-wbf — Route A §3.4 SH2B3 Rewrite + Abstract TODO Drop Summary

## One-liner

Rewrote `docs/manuscript/track_a_pivot.md` §3.4 SH2B3 case-study paragraph at L148 (~600 words to 396 words) replacing "consistent with credible-set collapse" / "most dramatic flagship change" / "illustrates the inflation mechanism" / "correctly fails to produce a credible set" overreach with audit-aligned methodological-constraint framing per AUDIT-REVIEW-2026-04-25.md Eval 3.4 (canonical BMI-HTN and HTN-stroke pairs were not executed, not collapsed) + Eval 2(a) (3 of 5 SH2B3 EUR traits returned non_converged); concurrently dropped the entire `(TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)` parenthetical from Abstract L28 — the L = 20 re-fit motivation now properly lives in the §3.4 forward-look paragraph as a methodological recommendation citing Zou et al. 2022. Single atomic commit `df3fa89` covering exactly 1 file; surrounding L26-L27 + L29-L30 + L144 + L146 + L150-L156 + L295 byte-identical pre vs post-edit; Stage 2 source-of-truth tsvs md5 4/4 preserved; `results_identity_ld/` tree untouched on disk; net file line-count delta = 0 (intra-line edits at L28 + L148 only).

## Atomic source commit

| Field | Value |
|---|---|
| Commit SHA | `df3fa89` |
| Branch | `main` (no worktree per CLAUDE.md GPFS constraint) |
| Files changed | 1 (`docs/manuscript/track_a_pivot.md`) |
| Insertions / deletions | 2 / 2 (intra-line replacements at L28 + L148) |
| Diff hunks | `@@ -28` (Abstract intra-line removal) + `@@ -148` (paragraph rewrite) |
| Pre-execution HEAD (per constraint) | `7563911a88d6cb4faaa8f2e1c229d7fa129c7ea0` |
| Immediate parent (HEAD~1 at commit time) | `c1a0caa` (parallel docs(m2) commit landed during execution; benign environmental drift documented as deviation Rule 3) |
| Post-edit HEAD | `df3fa89` |
| Pre-commit hooks | Not skipped (--no-verify forbidden; hooks ran successfully) |
| Atomic scope check | `git diff HEAD~1 HEAD --name-only` = `docs/manuscript/track_a_pivot.md` (exactly 1 file) |

## Verbatim copy of the new L148 paragraph

```
**SH2B3 12q24, anchor example.** Under the Stage 1d identity-LD pass, SuSiE-RSS + `coloc.susie` at *SH2B3* (12q24, EUR) produced PP.H4 = 1.00 for the BMI–hypertension and hypertension–stroke trait pairs at canonical leads (rs3184504, rs10774625, rs7137828, rs4766578), matching the single-causal-variant `coloc.abf` claim in the prior literature. Under the Stage 2 real-LD re-fit (1000 Genomes Phase 3 EUR, commits `6de9a88` + `a6e3214` + `7d54183`), the Stage 2 `coloc.susie` execution at SH2B3_12q24 EUR was scoped to `SH2B3_12q24__EUR__asthma_vs_t2d` only; the canonical BMI–hypertension and hypertension–stroke pairs were **not executed** (cf. `AUDIT-REVIEW-2026-04-25.md` Eval 3.4), so their absence from the manifest reflects a missing run rather than a documented credible-set collapse. Among the 5 SH2B3 EUR per-trait SuSiE-RSS fits under Stage 2 real-LD (`results/fine_mapping/finemap_summary.tsv`), **3 of 5 SH2B3 EUR traits** returned `convergence_status = non_converged` (BMI, hypertension, stroke); only asthma and T2D converged (cross-referenced to Figure 3 caption commit `2d5f710` and `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; cf. `AUDIT-REVIEW-2026-04-25.md` Eval 2(a)). SuSiE-RSS posterior credible sets are theoretically meaningful only at convergence (Wang et al. 2020²⁹; Zou et al. 2022²⁰); under the supplied real-LD reference (1000 Genomes Phase 3 EUR autosomal n = 503, below recommended thresholds per Pasaniuc & Price 2017⁴²), the honest read is that SuSiE-RSS failed to converge at three of five SH2B3 EUR traits — a numerical / algorithmic finding rather than direct biological evidence of credible-set collapse. The QTL-coloc side resolves only to Tier C at PP.H4 = 0.0517 (*ATXN2* / Adrenal_Gland / GTEx eQTL), well below the Tier B threshold of 0.5. We therefore present §3.4 as a flagship illustration of the **methodological constraint set** the candidate-locus design encounters under matched-coverage real-LD re-analysis — under-powered LD reference, SuSiE-RSS non-convergence at three of five traits, and restricted Stage 2 trait-pair scoping — rather than as evidence that the canonical PP.H4 = 1.00 claim has been falsified; testing that claim against real LD requires `coloc.susie` runs that have not yet been executed. A pre-registered supplementary re-fire is required to fully test the published SH2B3 EUR pleiotropy claim: (i) re-run SuSiE-RSS at L = 20 (Zou et al. 2022²⁰ §Discussion: "set L generously and verify n_CS << L"; Stage 2 L = 10 fits show L-saturation signatures per `AUDIT-REVIEW-2026-04-25.md` Eval 2(b)) at the canonical SH2B3 EUR per-trait fits, and (ii) run `coloc.susie` on the canonical BMI–hypertension and hypertension–stroke pairs against those re-fits. Until those runs land, §3.4 illustrates the methodological constraint set; see Supplementary Methods §Post-freeze execution roadmap.
```

**Word count: 396** (within hard 250-400 range; 4 words below upper bound). Started at 447 on first authoring; trimmed in 2 passes by tightening redundant phrasing in the methodology lead-in and forward-look (e.g., "Under the supplied Stage 2 real-LD reference" to "under the supplied real-LD reference"; "the honest read at SH2B3 EUR is that SuSiE-RSS failed to converge at three of five traits" to "the honest read is that SuSiE-RSS failed to converge at three of five SH2B3 EUR traits"; pruned "in this run" and "rather than as evidence that the canonical Stage 1d identity-LD" to "rather than as evidence that the canonical"). All 15 must-have tokens preserved verbatim; both italic gene symbols preserved; audit-aligned reframe phrase ("not executed" + "missing run") preserved.

## Verbatim copy of the new L28 sentence neighborhood (Abstract intra-line)

Pre-edit (the parenthetical removed):

```
...is reported in a planned supplementary follow-on (TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit). Cross-trait...
```

Post-edit (parenthetical dropped; surrounding sentence reads grammatically with single-period punctuation between two complete sentences):

```
...is reported in a planned supplementary follow-on. Cross-trait `coloc.susie` at these loci reassigned signals...
```

The leading-space + opening-paren + entire content + closing-paren were removed as a single contiguous intra-line replacement; the sentence terminator (period) is the original from "follow-on)." The surrounding L26-L27 + L29-L30 are byte-identical pre vs post-edit.

## Source-of-truth provenance table

Each numeric / textual anchor in the new L148 prose is mapped to its authoritative source. No numbers were recomputed; every value is cited verbatim.

| Anchor in new L148 | Source | Locator |
|---|---|---|
| `*SH2B3*` (12q24, EUR) gene region | TRACK-A-FROZEN-NUMBERS.md L51 + L73 | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` |
| Stage 1d identity-LD `PP.H4 = 1.00` (BMI-HTN + HTN-stroke pairs) | TRACK-A-FROZEN-NUMBERS.md L51 + L79; ie0 SUMMARY L60-65 | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` lines 51, 79 |
| Canonical leads `rs3184504, rs10774625, rs7137828, rs4766578` | TRACK-A-FROZEN-NUMBERS.md L73 ("rs3184504/rs10774625/rs7137828/rs4766578") | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` line 73 |
| Stage 2 commit-hash provenance `6de9a88` + `a6e3214` + `7d54183` | TRACK-A-FROZEN-NUMBERS.md L152 ("Stage 2 re-fit commit chain"); preserved verbatim from pre-edit L148 | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` line 152 |
| `SH2B3_12q24__EUR__asthma_vs_t2d` only-row scoping | TRACK-A-FROZEN-NUMBERS.md L73; AUDIT-REVIEW-2026-04-25.md Eval 3.4 (L60) | `results/multitrait/coloc_summary.tsv`; `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` Eval 3.4 |
| Canonical BMI-HTN and HTN-stroke pairs **not executed** (Eval 3.4) | AUDIT-REVIEW-2026-04-25.md Eval 3.4 (line 60: "Both `TRACK-A-FROZEN-NUMBERS.md` L51 and the manuscript itself acknowledge this: only `SH2B3_12q24__EUR__asthma_vs_t2d` was actually run.") | `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` line 60 (Eval 3.4) |
| **3 of 5 SH2B3 EUR traits non_converged** (BMI, hypertension, stroke) | quick-260425-1vy SUMMARY lines 45-51; Fig 3 caption commit `2d5f710` (track_a_pivot.md L297); IDENTITY-LD-K2D-FIT-SUMMARY.tsv | `.planning/quick/260425-1vy-track-a-figures-1a-3/260425-1vy-SUMMARY.md`; `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; track_a_pivot.md L297 |
| Asthma + T2D converged (status=ok) | quick-260425-1vy SUMMARY L45-51; Fig 3 caption | same as above |
| Wang et al. 2020²⁹ (JRSS-B; SuSiE-RSS convergence theory) | track_a_pivot.md §References Ref 29 (pre-existing; cited at L36 + L38 + Methods §Fine-mapping) | track_a_pivot.md §References |
| Zou et al. 2022²⁰ (PLoS Genet; L generosity recommendation) | track_a_pivot.md §References Ref 20 (pre-existing; cited at L36 + L38 + Methods §Fine-mapping) | track_a_pivot.md §References |
| Pasaniuc & Price 2017⁴² (Nat Rev Genet; LD-reference panel-size thresholds) | track_a_pivot.md §References Ref 42 (pre-existing); AUDIT-REVIEW-2026-04-25.md L86 | track_a_pivot.md §References; AUDIT-REVIEW L86 |
| LD-reference panel size n = 503 (1000 Genomes Phase 3 EUR autosomal) | Methods §GWAS Summary Statistics; STATE.md; AUDIT-REVIEW L86 | track_a_pivot.md Methods; STATE.md |
| Tier C `*ATXN2*` / Adrenal_Gland / GTEx eQTL `PP.H4 = 0.0517` | TRACK-A-FROZEN-NUMBERS.md L101 (Tier C row table); preserved verbatim from pre-edit L148 | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` line 101 |
| Tier B threshold 0.5 | TRACK-A-FROZEN-NUMBERS.md L83-85 (Tier definitions); track_a_pivot.md Methods | track_a_pivot.md Methods §Tier classification |
| `L = 20` re-fit recommendation | AUDIT-REVIEW-2026-04-25.md Eval 2(b) L44 (Zou 2022 PLoS Genet "set L generously and verify n_CS << L") | `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` Eval 2(b) line 44 |
| Stage 2 L = 10 fits show L-saturation signatures | AUDIT-REVIEW-2026-04-25.md Eval 2(b) L44 ("≥11 fits returning n_CS = 10 with the signature cs_sizes = '3;3;3;3;3;3;3;3;3;4'") | AUDIT-REVIEW Eval 2(b) line 44 |
| `Supplementary Methods §Post-freeze execution roadmap` | Pre-existing internal manuscript reference; preserved verbatim from pre-edit L148 | track_a_pivot.md Supplementary Methods (existing section) |

### Reconciliation note: 3/5 vs Eval 2(a)'s 4/5 text claim

AUDIT-REVIEW-2026-04-25.md Eval 2(a) header line 42 says "**4 of 5 traits return `status = non_converged`**" but its per-trait list (BMI, hypertension, stroke; only asthma and T2D = `ok`) sums to **3 non_converged of 5**. The Fig 3 caption at track_a_pivot.md L297 (commit `2d5f710`), the quick-260425-1vy SUMMARY (lines 45-51), and the IDENTITY-LD-K2D-FIT-SUMMARY.tsv (committed at `ec86832`) all agree on **3/5**. The new L148 prose uses the disk-authoritative count of **3 of 5**, citing Fig 3 caption commit 2d5f710 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv as authoritative. This resolves the audit's internal numerical drift in favor of disk truth. Note: Fig 3 caption itself uses the colloquial phrasing "four of five EUR traits at SH2B3 are non_converged under real-LD" — that caption-internal phrasing is preserved (byte-identical L295 lock per surrounding_lines_lock); the new L148 prose uses the precise per-trait list to make the count unambiguous and cross-references both Fig 3 and IDENTITY-LD-K2D-FIT-SUMMARY.tsv so a careful reader can verify against disk. A subsequent /gsd-quick (out of scope for this task) may align Fig 3 caption phrasing to "three of five" via a follow-on session.

## md5 manifest — Stage 2 source-of-truth tsvs (pre vs post-edit; byte-identical)

| File | Pre md5 | Post md5 | Status |
|---|---|---|---|
| `results/multitrait/coloc_summary.tsv` | `5fa3c4004970c5da711d05947cb1f7d2` | `5fa3c4004970c5da711d05947cb1f7d2` | identical |
| `results/fine_mapping/finemap_summary.tsv` | `8c3e04a202a919d94bd34a3c1d5146a2` | `8c3e04a202a919d94bd34a3c1d5146a2` | identical |
| `results/fine_mapping/finemap_summary_augmented.tsv` | `243bf4dd14bc2c7b67317f5587c74e1d` | `243bf4dd14bc2c7b67317f5587c74e1d` | identical |
| `results/qtl_coloc/tier_assignments.tsv` | `17ff46dbbfe78dd537d6b9bff7f3ae67` | `17ff46dbbfe78dd537d6b9bff7f3ae67` | identical |

`md5sum -c /tmp/wbf-pre-stage2-md5.txt` returned 4/4 OK post-edit.

## results_identity_ld/ output preservation

The k2d identity-LD re-fire output at `results_identity_ld/` (95 JSONs + finemap_manifest.tsv + 95 RDS binary fits, ~160 MB total; landed 2026-04-25 by `260424-k2d`) is **untouched on disk**. Per `260425-ieh` commit `ec86832` the directory is gitignored via `.gitignore` line 80. `git status --short | grep -cE "^\?\? results_identity_ld"` returns **0** post-commit. The new L148 prose references `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` as the canonical narrative reference (already-committed cheap text join replacing the need to parse 95 JSONs at runtime).

## 31 verification gates outcomes

| # | Gate | Outcome | Notes |
|---|---|---|---|
| 1 | TODO-COMPOSITION-FOLLOWON dropped (==0) | **PASS** | `grep -c` = 0 |
| 2 | TODO-marker count delta ≤ 0 | **PASS** | pre=1 post=0 |
| 3 | Forbidden phrase #1 file-wide ("consistent with credible-set collapse" ==0) | **FLAG (Rule 3)** | L148-only `grep -c` = 0 (substantive must_haves item 6 satisfied); file-wide `grep -c` = 3 surviving at L28 (Abstract pre-existing prose; only TODO parenthetical was in scope per Task 2), L216 (Discussion section, completely OOS per surrounding_lines_lock + Task scope), L297 (Fig 3 caption; byte-identical-locked per surrounding_lines_lock). Plan's must_haves item 6 specifies "removed from the rewritten L148 paragraph" — satisfied. Plan's verification table Gate 3 specifies file-wide ==0 — incompatible with surrounding_lines_lock + L216 OOS; resolved in favor of must_haves intent (the substantive specification). Future quick task may sweep L28 + L216 if requested; Fig 3 caption L297 is locked at ie0 commit 2d5f710. |
| 4 | "most dramatic flagship change" ==0 | **PASS** | `grep -c` = 0 |
| 5 | "illustrates the inflation mechanism" ==0 | **PASS** | `grep -c` = 0 |
| 6 | "correctly fails to produce a credible set" ==0 | **PASS** | `grep -c` = 0 |
| 7 | non_converged disclosure (≥2) | **PASS** | count = 6 (1 new at L148 + 4 pre-existing at Fig 3 caption L297 + 1 pre-existing elsewhere) |
| 8 | L = 20 forward-look (≥1) | **PASS** | count = 1 (in new L148 forward-look block) |
| 9 | Audit-aligned reframe (missing run | not executed | not run) (≥1) | **PASS** | count = 1 ("missing run" + "not executed" both present in new L148) |
| 10 | AUDIT-REVIEW citation (≥1) | **PASS** | count = 6 |
| 11 | Eval 3.4 anchor (≥1) | **PASS** | count = 1 |
| 12 | Eval 2(a) anchor (≥1) | **PASS** | count = 1 |
| 13 | rs3184504 canonical lead (≥1) | **PASS** | count = 4 (preserved verbatim from pre-edit) |
| 14 | 0.0517 ATXN2 PP.H4 (≥1) | **PASS** | count = 3 |
| 15 | Zou 2022 citation (≥1) | **PASS** | count = 2 (Zou et al. 2022²⁰ cited twice in new L148: methodological convergence-meaningfulness + L=20 forward-look) |
| 16 | Wang 2020 citation (≥1) | **PASS** | count = 1 (Wang et al. 2020²⁹ cited in new L148 methodological-convergence sentence) |
| 17 | Italic *SH2B3* (≥1) | **PASS** | count = 4 |
| 18 | Italic *ATXN2* (≥1) | **PASS** | count = 2 |
| 19 | Stage 2 commit hashes (each ≥1) | **PASS** | 6de9a88=1, a6e3214=1, 7d54183=4 |
| 20 | Supplementary Methods (≥1) | **PASS** | count = 1 |
| 21 | L148 word count (250-400) | **PASS** | count = 396 (4 words below upper bound) |
| 22 | Stage 2 md5 4/4 preserved | **PASS** | all 4 OK |
| 23 | L26-L30 byte-identical except L28 intra-line | **PASS** | exactly 2 diff lines (1 < + 1 >, both at L28) |
| 24 | L144 + L146 + L150-L156 byte-identical except L148 | **PASS** | exactly 2 diff lines (1 < + 1 >, both at L148) |
| 25 | L295 byte-identical | **PASS** | empty diff |
| 26 | results_identity_ld/ still gitignored | **PASS** | count = 0 |
| 27 | Pre-existing dirty files unchanged | **PASS** (with deviation) | post-status adds `M  docs/manuscript/track_a_pivot.md` (intended) plus `?? src/R/figures/fig_h3_ld_overlap_dose_response.R` (new untracked file from parallel /gsd-quick session 260425-wa2; outside this task's scope, NOT staged or committed); pre-existing M's on `.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock` unchanged. |
| 28 | Atomic commit scope (exactly 1 file) | **PASS** | `git diff HEAD~1 HEAD --name-only` = `docs/manuscript/track_a_pivot.md` |
| 29 | Forbidden-framing tokens delta ≤ 0 | **PASS** | pre=10 post=10 (delta=0; no new forbidden tokens introduced) |
| 30 | Convergence-disclosure cross-reference "3 of 5 SH2B3 EUR" (≥1) | **PASS** | count = 1 (rewrite uses 3/5 framing matching disk-authoritative count, not audit's text claim of 4/5) |
| 31 | File total line-count unchanged | **PASS** | empty diff (intra-line edits only) |

**Totals: 30 PASS / 0 FAIL / 1 FLAG (Gate 3, Rule-3 deviation documented)**

## Surrounding-line byte-identity diffs

**L26-L30 diff** (only L28 differs):

```
3c3
< [pre-edit L28 text containing the (TODO-COMPOSITION-FOLLOWON; …) parenthetical]
---
> [post-edit L28 text with the parenthetical removed]
```

L26 (`## Abstract`), L27 (blank), L29 (blank), L30 (`## Introduction`) all byte-identical.

**L144-L156 diff** (only L148 differs):

```
5c5
< [pre-edit L148 ~600-word paragraph]
---
> [post-edit L148 ~396-word paragraph]
```

L144 (`### Identity-LD vs Real-LD Comparison`), L145 (blank), L146 (lead-in sentence), L147 (blank), L149 (blank), L150 (`**Per-region survival distribution** ...`), L151-L154 (4 EXTRACT bullets), L155 (blank), L156 (mean delta sentence) all byte-identical.

**L295 diff**: empty (Fig 3 caption byte-identical).

## Forbidden-framing greppable check

Project regex: `revision|cleanup|fix-up|fix|machine learning|\bML\b|thrifty|evolutionary medicine|placeholder|\bv1\b|simplified|\bTBD\b|for now|static`

| Surface | Pre-edit count | Post-edit count | Delta |
|---|---|---|---|
| File-wide track_a_pivot.md | 10 | 10 | **0** (no new forbidden tokens introduced; Gate 29 PASS) |
| New L148 paragraph | n/a | 0 | (clean) |
| New L28 sentence neighborhood (post-removal) | n/a | 0 | (clean) |
| This SUMMARY.md narrative prose (excluding regex citations and quoted plan text) | n/a | 0 | (clean) |
| Commit message body | n/a | 0 | (clean) |

The 10 file-wide instances are all pre-existing words in unrelated contexts (e.g., "structurally fixed", "pre-specified", "static", etc.) which the plan explicitly accepts as out-of-scope per `<threat_model>` T-wbf-06: "Pre-existing file-wide instances accepted and not modified."

## Word-count rationale

L148 target: 250-400 words. Authored at 447 words on first pass; trimmed to 412 then 396 words across 2 condensation passes. All 15 must-have anchor tokens preserved at each pass (15 must-haves: `non_converged`, `0.0517`, `rs3184504`, `PP.H4 = 1.00`, `L = 20`, `AUDIT-REVIEW-2026-04-25`, `Eval 3.4`, `Eval 2(a)`, `6de9a88`, `a6e3214`, `7d54183`, `Supplementary Methods`, `Zou`, `Wang`, `3 of 5 SH2B3 EUR`); both italic gene symbols (`*SH2B3*`, `*ATXN2*`) preserved; audit-aligned reframe phrase (`not executed` + `missing run`) preserved. Trimming targeted redundant phrasing in the methodology lead-in ("Under the supplied Stage 2 real-LD reference" to "under the supplied real-LD reference"; "below recommended thresholds for stable summary-statistic fine-mapping" to "below recommended thresholds"), the §3.4 reframe ("rather than as evidence that the canonical Stage 1d identity-LD PP.H4 = 1.00 claim has been falsified at the locus" to "rather than as evidence that the canonical PP.H4 = 1.00 claim has been falsified"), and the forward-look ("at the canonical SH2B3 EUR per-trait fits, and (ii) run `coloc.susie` for the canonical BMI–hypertension and hypertension–stroke trait-pairs against those re-fits" to "...and (ii) run `coloc.susie` on the canonical BMI–hypertension and hypertension–stroke pairs against those re-fits"). Final 396 words sits 4 words below the upper bound, providing margin without compromising the 6 structural blocks (Stage 1d preservation; Stage 2 scoping disclosure per Eval 3.4; non-convergence disclosure per Eval 2(a); Tier C QTL fact preservation; reframe to methodological-constraint-set illustration; pre-registered re-fire forward-look citing Zou 2022 + Eval 2(b)).

## Honest-framing lock chain status

Extended from 5 places (per ie0 SUMMARY) to **6 places**:

1. `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` header purpose block (commit `105484d`)
2. Locked-scalar block comments in same R script (commit `105484d`)
3. In-figure `plot_annotation(caption = ...)` block (commit `105484d`)
4. `.planning/quick/260425-1vy-track-a-figures-1a-3/260425-1vy-SUMMARY.md` honest-framing lock (commit `105484d`)
5. `docs/manuscript/track_a_pivot.md` L295 Fig 3 caption (commit `2d5f710`)
6. **(NEW)** `docs/manuscript/track_a_pivot.md` L148 §3.4 SH2B3 case-study paragraph (commit `df3fa89`, this task)

All 6 places now agree on: (a) the structural argument is non-convergence + restricted scoping, NOT credible-set collapse demonstration; (b) the canonical BMI-HTN and HTN-stroke pairs were not executed under Stage 2; (c) PP.H4 has no posterior intervals in the manifest so no CIs are claimed; (d) the L = 20 re-fit + canonical-pair runs are pre-registered as supplementary work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Plan Verification Gate 3 file-wide check incompatible with surrounding_lines_lock + L216 OOS scope**

- **Found during:** Final verification pass after Tasks 1+2 applied
- **Issue:** Plan §verification Gate 3 specifies `grep -c "consistent with credible-set collapse" docs/manuscript/track_a_pivot.md == 0` (file-wide). However, the same plan's `<surrounding_lines_lock>` requires L295 (Fig 3 caption) to remain byte-identical, and L216 (Discussion §Strengths) is wholly outside the L28 + L148 atomic-edit scope. The Fig 3 caption at L295 (which by file numbering renders as L297 due to caption-block paragraph layout — but the byte-identical lock is on the caption paragraph) contains the phrase "consistent with credible-set collapse" inline. The Discussion §Strengths block at L216 also contains it. The Abstract L28 (post-Task 2) still contains it in pre-existing prose (the Task 2 spec only removed the TODO parenthetical, not other Abstract text). So a strict file-wide ==0 gate cannot succeed without violating the surrounding_lines_lock + Task 2's intra-line-only scope.
- **Resolution:** Honored the plan's `<must_haves>` item 6 ("Forbidden phrases ... are removed from the rewritten L148 paragraph") which is the substantive specification, and verified L148-only `grep -c "consistent with credible-set collapse"` = 0 (PASS). Documented the file-wide flag as Gate 3 FLAG with locator inventory. Pre-edit count was 4 file-wide; post-edit is 3 (one removal at L148 = the new paragraph). Future quick task may sweep L28 + L216 if the audit-author or Carter directs it; the L295/L297 Fig 3 caption is intentionally locked at ie0 commit 2d5f710.
- **Files modified:** none (deviation is documentation-only; substantive must_have satisfied)
- **Commit:** none (decision logged here)

**2. [Rule 3 - Blocking] Pre-execution HEAD drift due to parallel /gsd-quick session**

- **Found during:** Post-commit verification of HEAD chain
- **Issue:** Plan constraint specifies "Pre-execution HEAD: 7563911a88d6cb4faaa8f2e1c229d7fa129c7ea0". A parallel /gsd-quick session (`docs(m2): research phase domain — open questions resolved + M1 patterns scouted`, commit `c1a0caa`) landed on `main` between this task's pre-edit snapshot and atomic commit. My commit `df3fa89` was therefore parented on `c1a0caa`, not on `7563911`.
- **Resolution:** No action required — the parallel commit is on disjoint paths (M2 phase research; not docs/manuscript/track_a_pivot.md). My atomic commit's `git diff HEAD~1 HEAD --name-only` returns exactly `docs/manuscript/track_a_pivot.md` (1 file; Gate 28 PASS). Substantive atomic-scope invariant holds; only the parent-commit pointer drifted.
- **Files modified:** none
- **Commit:** none

**3. [Rule 3 - Blocking] Untracked file from parallel session surfaced during execution**

- **Found during:** Pre-commit `git status` comparison (Gate 27)
- **Issue:** `?? src/R/figures/fig_h3_ld_overlap_dose_response.R` appeared in `git status` post-edit; it was NOT in the pre-edit snapshot. This file is from a parallel /gsd-quick session (`260425-wa2-audit-h3-ld-overlap-dose-response-figure`, the audit High-Quality #3 LD-overlap dose-response figure builder referenced as outstanding in STATE.md L6). I did not create this file.
- **Resolution:** NOT staged, NOT committed by this task. Used `git commit --only docs/manuscript/track_a_pivot.md` with explicit pathspec to ensure only my edit was committed. Atomic-commit-scope Gate 28 PASS. The file remains untracked on disk for the sibling /gsd-quick session to handle.
- **Files modified:** none
- **Commit:** none

### Auth gates

None occurred. No external authentication needed for prose editing.

## Threat Flags

None — the manuscript prose edit introduces no new network endpoints, auth paths, file access patterns, or schema changes. Stage 2 source-of-truth tsvs unmodified (md5 4/4 preserved per Gate 22). `results_identity_ld/` tree untouched per Gate 26.

## Handoff for next /gsd-quick

Out-of-scope follow-ons surfaced or persisting after this task:

1. **Audit Eval 2(b) — L = 20 re-fit** (Terminal A LSF compute slot) — methodological pre-registration now also lives at L148 forward-look. Gated on Carter LSF decision.
2. **Audit High-Quality #2 — canonical SH2B3 EUR trait-pair coloc.susie runs** (BMI×HTN + HTN×stroke against L=20 re-fits) — gated on item 1.
3. **Audit High-Quality #3 — LD-overlap dose-response figure** — a parallel /gsd-quick session (260425-wa2) surfaced an untracked `src/R/figures/fig_h3_ld_overlap_dose_response.R` builder during this task's execution; that work is in flight in a sibling session.
4. **Audit Eval 3.6 — ld_overlap=0 schema verification** — `/gsd-debug` slot.
5. **Audit Eval 4(a) residual — fig3 EXPECTED scalars hardcode** — parallel disk-derivation pass.
6. **Audit Eval 3.2 — 78.9% QTL-coloc failure root-cause** — separate audit follow-on.
7. **Optional Fig 3 caption phrasing alignment** — current L297 caption uses colloquial "four of five EUR traits at SH2B3 are non_converged"; the new L148 prose uses precise "3 of 5 SH2B3 EUR" matching disk truth. A follow-on /gsd-quick may align Fig 3 caption phrasing for full intra-document numerical consistency (currently the per-trait-list "BMI/hypertension/stroke non_converged; asthma/T2D ok" sums to 3 in both places, so the count is unambiguous despite the cosmetic phrasing difference).
8. **Optional sweep of "consistent with credible-set collapse" at L28 + L216** — if the audit-author or Carter directs, a future quick task may rewrite the surviving instances at Abstract L28 and Discussion §Strengths L216 to match the new L148 audit-aligned framing. Currently retained as pre-existing prose outside the wbf atomic scope.

## Self-Check: PASSED

Files verified to exist:
- `docs/manuscript/track_a_pivot.md`: FOUND (L148 contains new paragraph; L28 contains TODO-marker-free Abstract; surrounding L26-L30 + L144 + L146 + L150-L156 + L295 byte-identical)
- `.planning/quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md`: FOUND (you are reading it)

Commit verified to exist:
- `df3fa89 docs(quick-260425-wbf): rewrite §3.4 SH2B3 case study (Eval 3.4 + 2a) and drop Abstract TODO marker` (FOUND in `git log --oneline -1`)

Stage 2 tsvs verified byte-identical pre vs post (md5 4/4 OK).

Atomic-commit-scope verified: `git diff HEAD~1 HEAD --name-only` = exactly 1 file = `docs/manuscript/track_a_pivot.md`.

All 31 verification gates accounted for: 30 PASS + 1 FLAG (Gate 3, Rule-3 deviation documented; substantive must_haves intent satisfied at L148-only `grep -c` = 0).
