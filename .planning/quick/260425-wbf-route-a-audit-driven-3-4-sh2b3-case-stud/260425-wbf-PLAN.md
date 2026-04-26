---
phase: quick-260425-wbf
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/manuscript/track_a_pivot.md
autonomous: true
requirements:
  - TRACK-A-AUDIT-EVAL-3.4
  - TRACK-A-AUDIT-EVAL-2A
  - TRACK-A-ABSTRACT-TODO-DROP
must_haves:
  truths:
    - "L28 Abstract no longer contains the marker token TODO-COMPOSITION-FOLLOWON; surrounding sentence remains grammatical (period after 'follow-on')."
    - "L148 SH2B3 case-study paragraph is replaced with audit-aligned prose 250-400 words that honestly states the canonical BMI-HTN and HTN-stroke trait-pairs at SH2B3 EUR were NOT executed under Stage 2 real-LD (a missing run, not a documented collapse) per AUDIT-REVIEW-2026-04-25.md Eval 3.4."
    - "Rewritten L148 explicitly discloses 3 of 5 SH2B3 EUR traits (BMI, hypertension, stroke) returned convergence_status = non_converged under Stage 2 real-LD per Fig 3 caption commit 2d5f710 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv (asthma + t2d converged); reconciles audit Eval 2(a) text claim of 4/5 to disk-authoritative 3/5 count."
    - "Rewritten L148 cites the L = 20 re-fit recommendation (Zou 2022 PLoS Genet) inline as the methodologically required forward-look at the canonical SH2B3 EUR trait-pairs."
    - "Rewritten L148 reframes the case study as a flagship illustration of the methodological constraint set (under-powered LD reference n = 503; SuSiE-RSS non-convergence; restricted Stage 2 scoping) rather than a colocalization-collapse demonstration; preserves the locked Stage 1d identity-LD PP.H4 = 1.00 baseline at canonical leads + the ATXN2/Adrenal_Gland Tier C PP.H4 = 0.0517 fact + the Stage 2 commit-hash provenance pointers + the pre-registered Supplementary Methods §Post-freeze execution roadmap reference."
    - "Forbidden phrases 'consistent with credible-set collapse' and 'most dramatic flagship change' are removed from the rewritten L148 paragraph."
    - "All new prose / SUMMARY.md / commit message contain zero forbidden-framing tokens (revision / cleanup / fix / fix-up / machine learning / \\bML\\b / thrifty / evolutionary medicine / placeholder / \\bv1\\b / simplified / \\bTBD\\b / for now / static)."
  artifacts:
    - path: "docs/manuscript/track_a_pivot.md"
      provides: "Audit-aligned §3.4 SH2B3 case-study paragraph at L148 + TODO-marker-free Abstract at L28"
      min_lines: 350
      contains: "rewritten paragraph beginning with **SH2B3 12q24, anchor example.**"
    - path: ".planning/quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md"
      provides: "Atomic-task summary with verification gate outcomes; produced by orchestrator/executor at task close"
      min_lines: 30
  key_links:
    - from: "docs/manuscript/track_a_pivot.md L148 (rewritten §3.4 paragraph)"
      to: ".planning/amendments/AUDIT-REVIEW-2026-04-25.md Eval 3.4 + Eval 2(a)"
      via: "inline citation of AUDIT-REVIEW-2026-04-25 + Eval 3.4 + Eval 2(a) anchors"
      pattern: "AUDIT-REVIEW-2026-04-25"
    - from: "docs/manuscript/track_a_pivot.md L148 (rewritten §3.4 paragraph)"
      to: "docs/manuscript/track_a_pivot.md L295 (Fig 3 caption, commit 2d5f710)"
      via: "shared 'non_converged' + per-trait-status (BMI/hypertension/stroke non_converged; asthma + t2d ok) honest-data lock"
      pattern: "non_converged"
    - from: "docs/manuscript/track_a_pivot.md L148 (rewritten §3.4 paragraph)"
      to: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md L51 + L79"
      via: "verbatim citation of locked Stage 1d identity-LD PP.H4 = 1.00 narrative + ATXN2 PP.H4 = 0.0517"
      pattern: "PP.H4 = 1.00|0.0517"
    - from: "docs/manuscript/track_a_pivot.md L28 (Abstract intra-line removal)"
      to: "L148 (where the L = 20 re-fit motivation now properly lives)"
      via: "removed parenthetical's L = 20 / Terminal A LSF gate language migrates to the §3.4 paragraph as a methodological forward-look"
      pattern: "L = 20|L=20"
---

<objective>
Rewrite the SH2B3 case-study paragraph at `docs/manuscript/track_a_pivot.md` L148 (the §3.4 anchor example) so it honestly reflects the AUDIT-REVIEW-2026-04-25.md Eval 3.4 (missing run, not collapse) + Eval 2(a) (3 of 5 traits non_converged under real-LD) findings; and drop the `TODO-COMPOSITION-FOLLOWON` marker parenthetical from the Abstract at L28. Both edits land in a single atomic source commit so the Abstract / Fig 3 caption (L295) / §3.4 paragraph (L148) honest-framing lock chain — currently 5 places per ie0 commit `2d5f710` — extends to 6 places without intra-document drift.

Purpose: the manuscript's flagship case study currently overreaches in two load-bearing ways (1) calling the absence of canonical BMI-HTN and HTN-stroke `coloc.susie` rows from the Stage 2 manifest "consistent with credible-set collapse" when those pairs were simply not executed in this run; and (2) framing this as "the most dramatic flagship change in this dataset" while conflating SuSiE-RSS non-convergence with biological collapse. The audit (committed at `9801e77`) explicitly flags both as overreach. The rewrite preserves every locked-numbers claim that disk evidence supports (Stage 1d identity-LD PP.H4 = 1.00 at canonical leads; ATXN2/Adrenal_Gland real-LD QTL coloc PP.H4 = 0.0517; commit-hash provenance pointers `6de9a88` + `a6e3214` + `7d54183`; pre-registered supplementary re-fire reference) while reframing the case as a methodological-constraint illustration (under-powered LD reference; SuSiE-RSS non-convergence; restricted Stage 2 scoping) rather than as a triumphant inflation-mechanism demonstration.

Output: 1 atomic source commit modifying exactly 1 file (`docs/manuscript/track_a_pivot.md`); 1 paragraph rewritten at L148 (~250-400 words, down from ~600); 1 intra-line parenthetical removal at L28 (TODO marker dropped per Interpretation B — the entire `(TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)` parenthetical is removed; the L = 20 re-fit motivation migrates to L148 where it methodologically belongs). Surrounding L26-L27 + L29-L30 + L144 + L146 + L150-L156 byte-identical pre vs post-edit. Stage 2 real-LD source-of-truth tsvs (`results/multitrait/coloc_summary.tsv`, `results/fine_mapping/finemap_summary.tsv`, `results/fine_mapping/finemap_summary_augmented.tsv`) byte-identical (md5 4/4 preserved). `results_identity_ld/` tree untouched on disk and remains gitignored per ieh's commit `ec86832` (no `??` line in `git status` post-commit). Pre-existing dirty files (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`) untouched; STATE.md row + this PLAN.md/SUMMARY.md committed by the orchestrator in a separate docs commit per Step 8.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/STATE.md
@.planning/amendments/AUDIT-REVIEW-2026-04-25.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/quick/260425-1vy-track-a-figures-1a-3/260425-1vy-SUMMARY.md
@.planning/quick/260425-ie0-route-a-track-a-fig-3-caption-integratio/260425-ie0-SUMMARY.md
@docs/manuscript/track_a_pivot.md

<authoritative_facts>
<!-- Pre-extracted from AUDIT-REVIEW-2026-04-25.md + TRACK-A-FROZEN-NUMBERS.md + Fig 3 caption (commit 2d5f710) + IDENTITY-LD-K2D-FIT-SUMMARY.tsv + 1vy SUMMARY. Cite these verbatim; do NOT recompute. -->

**Per-trait SuSiE-RSS convergence status at SH2B3_12q24 EUR under Stage 2 real-LD** (disk-authoritative; cited verbatim from quick-260425-1vy SUMMARY lines 45-51 cross-referenced to Fig 3 caption at track_a_pivot.md L295 commit 2d5f710):

| Trait | Identity-LD n_CS | Real-LD n_CS | Real-LD status |
|---|---|---|---|
| asthma | 0 | 1 | ok |
| BMI | 3 | 8 | non_converged |
| hypertension | 10 | 4 | non_converged |
| stroke | 10 | 2 | non_converged |
| t2d | 2 | 9 | ok |

Authoritative count: **3 of 5 SH2B3 EUR traits return non_converged under Stage 2 real-LD** (BMI, hypertension, stroke); asthma + t2d converge. AUDIT-REVIEW Eval 2(a) text says "4 of 5" but its per-trait list (BMI, hypertension, stroke; only asthma and t2d = ok) sums to 3/5 — caption + 1vy SUMMARY + IDENTITY-LD-K2D-FIT-SUMMARY.tsv all agree on 3/5. Use 3/5 in the rewrite.

**Stage 2 manifest scoping at SH2B3_12q24 EUR** (TRACK-A-FROZEN-NUMBERS.md L51 + 73; quick-260425-1vy SUMMARY L60-65):

The only SH2B3 EUR trait-pair row in `results/multitrait/coloc_summary.tsv` is `SH2B3_12q24__EUR__asthma_vs_t2d` with empty PP.H3/PP.H4/n_snps columns. The canonical BMI-HTN and HTN-stroke trait-pairs were **not executed** in Stage 2 — their absence reflects a missing run (Eval 3.4), not a documented collapse.

**Locked Stage 1d identity-LD PP.H4 narrative** (TRACK-A-FROZEN-NUMBERS.md L51 + L79; quick-260425-1vy SUMMARY L60-65; cited verbatim wherever this claim appears in the manuscript):

| Pair | Stage 1d identity-LD claim |
|---|---|
| BMI × hypertension at SH2B3 EUR | PP.H4 = 1.00 at canonical leads rs3184504, rs10774625, rs7137828, rs4766578 |
| hypertension × stroke at SH2B3 EUR | PP.H4 = 1.00 at canonical leads (same lead-variant set) |
| ATXN2 / Adrenal_Gland real-LD QTL coloc | PP.H4 = 0.0517 (below Tier C 0.5 threshold; second-highest Tier C in the entire run) |

**Stage 2 commit-hash provenance** (currently cited at L148): `6de9a88` + `a6e3214` + `7d54183`. Preserve verbatim.

**LD-reference panel size** (Methods §GWAS Summary Statistics + STATE.md): 1000 Genomes Phase 3 EUR n = 503 (autosomal). Pasaniuc & Price *Nat Rev Genet* 2017 cited at AUDIT-REVIEW L86 documents this is below recommended thresholds for stable summary-statistic fine-mapping.

**L = 10 saturation + L = 20 forward-look** (AUDIT-REVIEW-2026-04-25.md Eval 2(b) at L44; Zou 2022 PLoS Genet §Discussion: "set L generously and verify n_CS << L"; Wang 2020 JRSS-B). The pre-registered supplementary re-fire at the canonical SH2B3 EUR trait-pairs requires SuSiE-RSS at L = 20 to test the actual published claim under real-LD; until that runs, the SH2B3 case study is presented as a flagship illustration of the methodological constraint set, not as a colocalization-collapse demonstration.

**§References §Refs (referenced inline at L148 rewrite):** Zou 2022 PLoS Genet is Ref 20 in the existing §References block (already cited inline at L36 + L38 + Methods §Fine-mapping); Wang 2020 JRSS-B is Ref 29 (already cited inline at L36 + L38 + Methods). Both are pre-existing References — the L148 rewrite cites them inline using existing superscript numbering, no new bibliography entries needed.

**Fig 3 caption convention to mirror** (L295, commit 2d5f710): "displays no 95% confidence intervals on PP.H4 — PP.H4 is a posterior probability and the Stage 2 production manifest stores no posterior intervals" / "the figure's argument is structural credible-set-yield collapse plus non-convergence under real-LD, not a per-signal interval estimate." The L148 rewrite must align with this framing (no inflation-mechanism overreach; structural / non-convergence argument lock).

**Honest-framing lock chain**: 5 places after ie0 (R-script header + locked-scalar block + in-figure plot_annotation + 1vy SUMMARY + L295 manuscript caption); the L148 rewrite extends this to 6 places (paragraph #6 = the §3.4 prose).
</authoritative_facts>

<surrounding_lines_lock>
The following lines must remain BYTE-IDENTICAL pre vs post-edit (Edit-tool replacements at L28 and L148 only; no other lines touched):

| Line | Content (verbatim) |
|---|---|
| L26 | `## Abstract` |
| L27 | (blank) |
| L29 | (blank) |
| L30 | `## Introduction` |
| L144 | `### Identity-LD vs Real-LD Comparison` |
| L146 | `We find substantial and non-uniform inflation of cross-trait PP.H4 under identity-LD relative to real-LD at admissible regions.` |
| L150 | `**Per-region survival distribution** (full table: Table 3):` |
| L151 | `- Survived (identity ≥ 0.8 AND real ≥ 0.8): [EXTRACT: count from results/multitrait/coloc_summary.tsv + identity comparator]` |
| L152 | `- Lost (identity ≥ 0.8 AND real < 0.8): [EXTRACT]` |
| L153 | `- Rescued (identity < 0.8 AND real ≥ 0.8): [EXTRACT]` |
| L154 | `- Both-null: [EXTRACT]` |
| L156 | `Mean delta PP.H4 (identity − real) across all admissible region × trait-pair combinations: [EXTRACT]; median [EXTRACT]; range [EXTRACT]. The SH2B3 row is highlighted in Figure 1A and Figure 3 forest plot.` |

L295 (Fig 3 caption, ie0 commit 2d5f710) and L291 (Fig 1A caption discrepancy, deferred per ie0 SUMMARY §Handoff) ALSO untouched.
</surrounding_lines_lock>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite §3.4 SH2B3 case-study paragraph at L148 (audit-aligned)</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Rewrite the single logical line at `docs/manuscript/track_a_pivot.md` L148 — the paragraph beginning with `**SH2B3 12q24, anchor example.**` and currently running ~600 words ending with `...see Supplementary Methods §Post-freeze execution roadmap.` — replacing it with an audit-aligned 250-400 word paragraph that:

**1. Pre-edit snapshot (mandatory, for byte-identity verification of surrounding lines + Stage 2 md5 preservation):**

```bash
sed -n '26,30p' docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-L26-30.txt
sed -n '144,156p' docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-L144-156.txt
md5sum results/multitrait/coloc_summary.tsv results/fine_mapping/finemap_summary.tsv results/fine_mapping/finemap_summary_augmented.tsv > /tmp/wbf-pre-stage2-md5.txt
git status --short > /tmp/wbf-pre-status.txt
```

**2. Read the current L148 verbatim** (single logical line; ~600 words) before authoring the replacement, so the Edit tool's `old_string` is exactly correct on the first try (Edit fails if `old_string` does not match disk byte-for-byte).

**3. Author the replacement paragraph** following this structure (target 250-400 words; match the rhythm of L146 lead-in and L150-L156 sub-blocks; preserve §3.4 voice):

- **Opening claim (preserved from existing prose):** Under the Stage 1d identity-LD pass, SuSiE-RSS + `coloc.susie` at *SH2B3* (12q24, EUR) produced PP.H4 = 1.00 for the BMI-hypertension and hypertension-stroke trait pairs at canonical leads (rs3184504, rs10774625, rs7137828, rs4766578), matching the canonical single-causal-variant `coloc.abf` claim in the prior literature.

- **Stage 2 scoping disclosure (REWRITTEN per Eval 3.4):** Under the Stage 2 real-LD re-fit (1000G Phase 3 EUR, commits `6de9a88` + `a6e3214` + `7d54183`), the Stage 2 `coloc.susie` execution at the SH2B3_12q24 EUR region was scoped to `SH2B3_12q24__EUR__asthma_vs_t2d` only — the canonical BMI-hypertension and hypertension-stroke trait pairs at SH2B3 EUR were **not executed** in this run (cf. AUDIT-REVIEW-2026-04-25.md Eval 3.4). The absence of canonical-pair rows from the Stage 2 `coloc.susie` output manifest reflects a missing run, not a documented credible-set collapse.

- **Non-convergence disclosure (NEW per Eval 2(a)):** Of the 5 SH2B3 EUR per-trait SuSiE-RSS fits under Stage 2 real-LD (`results/fine_mapping/finemap_summary.tsv`), 3 returned `convergence_status = non_converged` (BMI, hypertension, stroke); only asthma and T2D converged (cross-referenced to the per-trait yields surfaced at Figure 3, caption commit `2d5f710`, and to `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`). SuSiE-RSS posterior credible sets are theoretically meaningful only at convergence (Wang et al. 2020 *JRSS-B* Ref 29; Zou et al. 2022 *PLoS Genet* Ref 20); the honest read at SH2B3 EUR under the supplied Stage 2 real-LD reference (1000 Genomes Phase 3 EUR, n = 503 autosomal — below recommended thresholds for stable summary-statistic fine-mapping per Pasaniuc & Price 2017 Ref 42) is that SuSiE-RSS failed to converge at three of five SH2B3 EUR traits, a numerical / algorithmic finding rather than direct biological evidence of credible-set collapse.

- **Tier C QTL fact (preserved):** The QTL-coloc side at SH2B3_12q24 EUR resolves only to Tier C at PP.H4 = 0.0517 (*ATXN2* / Adrenal_Gland / GTEx eQTL) — well below the Tier B threshold of 0.5.

- **Reframing (NEW; replaces "most dramatic flagship change" overreach):** The §3.4 SH2B3 case study is presented as a flagship illustration of the **methodological constraint set** — under-powered LD reference, SuSiE-RSS non-convergence at three of five traits, and restricted Stage 2 trait-pair scoping — that the candidate-locus design encounters under matched-coverage real-LD re-analysis. It is **not** presented as evidence that the canonical Stage 1d identity-LD PP.H4 = 1.00 claim has been falsified at the locus; testing that claim against real LD requires the `coloc.susie` runs that have not yet been executed at the canonical trait-pairs.

- **Forward-look (NEW per Eval 2(a) + Eval 2(b)):** A pre-registered supplementary re-fire is required to fully test the published SH2B3 EUR pleiotropy claim under real LD: (i) re-run SuSiE-RSS at L = 20 (Zou et al. 2022 §Discussion: "set L generously and verify n_CS << L"; the Stage 2 fits at L = 10 show signatures of L-saturation per AUDIT-REVIEW Eval 2(b)) at the canonical SH2B3 EUR per-trait fits; and (ii) run `coloc.susie` for the canonical BMI-hypertension and hypertension-stroke trait-pairs against the L = 20 re-fits. Until those runs land, the §3.4 SH2B3 case study illustrates the methodological constraint set rather than a colocalization collapse; see Supplementary Methods §Post-freeze execution roadmap.

**4. Forbidden phrases to NOT include in the rewrite:**
- "consistent with credible-set collapse" (Eval 3.4 calls this overreach)
- "most dramatic flagship change in this dataset" (Eval 3.4 + Eval 2(a) calls this overreach)
- "illustrates the inflation mechanism" (the canonical pairs to demonstrate the mechanism were not run)
- "SuSiE-RSS correctly fails to produce a credible set" (conflates non-convergence with collapse)
- "or produces one so small that `coloc.susie` returns no-signal" (same conflation)
- Any forbidden-framing token from the project regex: `revision|cleanup|fix-up|fix|machine learning|\bML\b|thrifty|evolutionary medicine|placeholder|\bv1\b|simplified|\bTBD\b|for now|static`

**5. Required tokens in the rewrite (each `grep -c` ≥ 1 against the rewritten paragraph):**
- `*SH2B3*` (italic gene symbol, surrounding-caption convention)
- `*ATXN2*` (italic gene symbol)
- `0.0517` (ATXN2/Adrenal_Gland Tier C PP.H4)
- `PP.H4 = 1.00` (Stage 1d identity-LD locked-narrative claim)
- `rs3184504` (canonical lead variant — at minimum this one; the rs10774625 / rs7137828 / rs4766578 set may be retained verbatim from the existing prose if length permits)
- `non_converged` (per-trait status disclosure)
- `not executed` OR `missing run` OR `not run` (audit-aligned reframe of the manifest absence)
- `L = 20` (methodological forward-look; mirror the L295 caption convention of using `L = 20` with surrounding spaces, NOT `L=20`)
- `Zou` AND (`2022` or `et al.`) — Zou 2022 PLoS Genet citation; cite as `Zou et al. 2022²⁰` using the existing §References Ref 20 superscript
- `Wang` AND (`2020` or `et al.`) — Wang 2020 JRSS-B; cite as `Wang et al. 2020²⁹` using the existing §References Ref 29 superscript
- `AUDIT-REVIEW-2026-04-25` (cite the audit document as provenance for Eval 3.4 + Eval 2(a))
- `Eval 3.4` (explicit audit-eval anchor)
- `Eval 2(a)` (explicit audit-eval anchor)
- `6de9a88` (Stage 2 commit-hash provenance preserved)
- `a6e3214` (Stage 2 commit-hash provenance preserved)
- `7d54183` (Stage 2 commit-hash provenance preserved)
- `Supplementary Methods §Post-freeze execution roadmap` (pre-registered re-fire reference preserved)

**6. Apply via Edit tool** with:
- `old_string` = the verbatim L148 paragraph (read from disk in step 2; ~600 words)
- `new_string` = the new paragraph authored in step 3 (~250-400 words)

The Edit tool replaces a single logical line; the surrounding lines L144 + L146 + L150-L156 + L295 + every other line in the file remain byte-identical. Verify post-edit:

```bash
diff /tmp/wbf-pre-L26-30.txt <(sed -n '26,30p' docs/manuscript/track_a_pivot.md)        # expect empty
diff /tmp/wbf-pre-L144-156.txt <(sed -n '144,156p' docs/manuscript/track_a_pivot.md)    # expect L148-only diff
md5sum -c /tmp/wbf-pre-stage2-md5.txt                                                    # expect 3/3 OK
wc -w <(sed -n '148p' docs/manuscript/track_a_pivot.md)                                  # expect 250-400
```

  </action>
  <verify>
    <automated>
      bash -c '
        # Required tokens (each must be ≥ 1)
        for tok in "non_converged" "0.0517" "rs3184504" "PP.H4 = 1.00" "L = 20" "AUDIT-REVIEW-2026-04-25" "Eval 3.4" "Eval 2(a)" "6de9a88" "a6e3214" "7d54183" "Supplementary Methods" "Zou" "Wang"; do
          n=$(grep -cF "$tok" docs/manuscript/track_a_pivot.md);
          [ "$n" -ge 1 ] || { echo "FAIL required token missing: $tok (count=$n)"; exit 1; };
        done;
        # Italic gene symbols
        grep -cE "\*SH2B3\*" docs/manuscript/track_a_pivot.md | grep -qE "^[1-9]" || { echo "FAIL *SH2B3* italic"; exit 1; };
        grep -cE "\*ATXN2\*" docs/manuscript/track_a_pivot.md | grep -qE "^[1-9]" || { echo "FAIL *ATXN2* italic"; exit 1; };
        # Audit-aligned reframe phrase (any of the three)
        n=$(grep -cE "(not executed|missing run|not run)" docs/manuscript/track_a_pivot.md);
        [ "$n" -ge 1 ] || { echo "FAIL audit-aligned reframe missing"; exit 1; };
        # Forbidden phrases must be absent from the rewritten L148 (file-wide check is acceptable since these phrases existed only at L148 pre-edit)
        for forb in "consistent with credible-set collapse" "most dramatic flagship change" "illustrates the inflation mechanism" "correctly fails to produce a credible set"; do
          n=$(grep -cF "$forb" docs/manuscript/track_a_pivot.md);
          [ "$n" -eq 0 ] || { echo "FAIL forbidden phrase still present: $forb (count=$n)"; exit 1; };
        done;
        # Forbidden-framing regex (file-wide; pre-existing instances may remain outside §3.4 / Abstract — adjust if false positives surface, but the project standard is zero in NEW prose)
        n=$(grep -cE "revision|cleanup|fix-up|machine learning|\bML\b|thrifty|evolutionary medicine|placeholder|\bv1\b|simplified|\bTBD\b|for now|static" docs/manuscript/track_a_pivot.md || true);
        # Pre-existing instances acceptable; the gate is "no INCREASE from pre-edit baseline"; verify by snapshotting pre-edit count and comparing — handled in SUMMARY
        # L148 word count in 250-400
        wc=$(awk "NR==148 { n=split(\$0, a, /[ \t]+/); print n }" docs/manuscript/track_a_pivot.md);
        [ "$wc" -ge 250 ] && [ "$wc" -le 400 ] || { echo "FAIL L148 word count $wc out of 250-400"; exit 1; };
        # Surrounding lines byte-identical (read pre-snapshots from /tmp)
        diff -q /tmp/wbf-pre-L26-30.txt <(sed -n "26,30p" docs/manuscript/track_a_pivot.md) || { echo "FAIL L26-L30 drift"; exit 1; };
        # L144-L156 diff allowed at L148 only
        diff /tmp/wbf-pre-L144-156.txt <(sed -n "144,156p" docs/manuscript/track_a_pivot.md) | grep -E "^[<>]" | grep -vE "^[<>] \*\*SH2B3 12q24" || true;
        # Stage 2 md5 preserved
        md5sum -c /tmp/wbf-pre-stage2-md5.txt || { echo "FAIL Stage 2 md5 drift"; exit 1; };
        # results_identity_ld/ still gitignored (no ?? in git status)
        git status --short | grep -E "^\?\? results_identity_ld" && { echo "FAIL results_identity_ld/ surfaced as untracked"; exit 1; } || true;
        echo "OK Task 1 verification gates passed";
      '
    </automated>
  </verify>
  <done>
- L148 paragraph replaced with audit-aligned 250-400 word version
- All 14 required tokens present (each `grep -c` ≥ 1)
- All 4 forbidden phrases absent (each `grep -c` == 0)
- Italic gene symbols `*SH2B3*` and `*ATXN2*` present
- Audit-aligned reframe phrase ("not executed" OR "missing run" OR "not run") present ≥ 1
- L26-L30, L144, L146, L150-L156 byte-identical pre vs post-edit
- L295 (Fig 3 caption) byte-identical pre vs post-edit
- Stage 2 source-of-truth tsv md5 4/4 preserved (3 tsvs hashed; the 4th is `tier_assignments.tsv`, also unchanged)
- `results_identity_ld/` does NOT appear as `??` in `git status` (still gitignored per ec86832)
- Pre-existing dirty files (`.claude/settings.json`, `.planning/config.json`, `.claude/scheduled_tasks.lock`) untouched and unstaged
  </done>
</task>

<task type="auto">
  <name>Task 2: Drop TODO-COMPOSITION-FOLLOWON parenthetical from Abstract at L28</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Apply Interpretation B per the planning brief (drop the entire parenthetical, not just the marker token; rationale: Abstracts should not contain TODO-style internal-routing language; the L = 20 motivation properly migrates to L148 via Task 1's forward-look paragraph).

**1. Read L28 verbatim** to confirm the exact-byte content to remove. The current L28 contains the substring:

```
 (TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)
```

(note the leading space before the opening paren — that space is part of the removal so the resulting prose has `follow-on. Cross-trait` with single spacing).

**2. Apply Edit tool with:**
- `old_string` = ` (TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)` (exact-byte; leading space included; trailing closing-paren included; no trailing space)
- `new_string` = `` (empty string)

The result transforms the surrounding sentence from:

```
...is reported in a planned supplementary follow-on (TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit). Cross-trait...
```

into:

```
...is reported in a planned supplementary follow-on. Cross-trait...
```

**3. Verify post-edit:**
- `grep -c "TODO-COMPOSITION-FOLLOWON" docs/manuscript/track_a_pivot.md` == 0
- `grep -cE "TODO[A-Z-]*" docs/manuscript/track_a_pivot.md` returns ≤ pre-edit count (i.e., no NEW TODO markers introduced; existing markers elsewhere in the document — if any — may remain, but the count must not increase)
- L28 still contains the surrounding sentence `is reported in a planned supplementary follow-on. Cross-trait`
- L26 (`## Abstract`), L27 (blank), L29 (blank), L30 (`## Introduction`) byte-identical pre vs post-edit
- Total file line count unchanged (the edit is intra-line; no line breaks added or removed)
- L148 (rewritten by Task 1) and L295 (Fig 3 caption) byte-identical with Task 1's post-edit state

**4. NOT to be touched in this task:**
- Any TODO marker outside the §Abstract L28 location (project-wide grep for `TODO[A-Z-]*` may surface other markers in source files — those are out of scope)
- L291 (Fig 1A caption discrepancy, deferred per ie0 SUMMARY §Handoff)
- L295 (Fig 3 caption, ie0 commit `2d5f710`)
- Any line modified by Task 1 (Task 1 lands first; Task 2 is a disjoint intra-line edit at L28)

  </action>
  <verify>
    <automated>
      bash -c '
        # TODO marker dropped
        n=$(grep -c "TODO-COMPOSITION-FOLLOWON" docs/manuscript/track_a_pivot.md);
        [ "$n" -eq 0 ] || { echo "FAIL TODO-COMPOSITION-FOLLOWON still present (count=$n)"; exit 1; };
        # Abstract sentence punctuation valid post-removal
        grep -F "is reported in a planned supplementary follow-on. Cross-trait" docs/manuscript/track_a_pivot.md > /dev/null || { echo "FAIL Abstract sentence not found post-edit"; exit 1; };
        # Surrounding lines byte-identical
        diff /tmp/wbf-pre-L26-30.txt <(sed -n "26,30p" docs/manuscript/track_a_pivot.md) | grep -E "^[<>]" | grep -vE "^[<>] Cross-trait colocalization analyses" || true;
        # No new TODO markers introduced (delta ≤ 0; the dropped marker means count goes down by 1)
        # File line count unchanged
        pre_lc=$(wc -l < /tmp/wbf-pre-L26-30.txt);
        # We snapshot only L26-L30 pre-edit; the file-wide line count is checked via a separate snapshot
        [ -f /tmp/wbf-pre-file-linecount.txt ] || wc -l docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-file-linecount.txt 2>/dev/null;
        # Stage 2 md5 still preserved (Task 1 already verified; re-check after Task 2 to be safe)
        md5sum -c /tmp/wbf-pre-stage2-md5.txt || { echo "FAIL Stage 2 md5 drift after Task 2"; exit 1; };
        echo "OK Task 2 verification gates passed";
      '
    </automated>
  </verify>
  <done>
- TODO-COMPOSITION-FOLLOWON marker removed from L28 (file-wide grep count == 0)
- Surrounding Abstract sentence reads grammatically: `...is reported in a planned supplementary follow-on. Cross-trait...`
- L26, L27, L29, L30 byte-identical pre vs post-edit
- L148 (Task 1 output) and L295 (Fig 3 caption) byte-identical with their respective pre-Task-2 states
- File total line count unchanged (intra-line edit only)
- No new TODO markers introduced anywhere in the file
- Stage 2 source-of-truth tsv md5 4/4 still preserved (re-checked after Task 2)
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|---|---|
| Editor → manuscript file | Single-file Edit tool replacements at L28 + L148; no execution of new code, no new dependencies, no network I/O, no PII. |
| Manuscript ↔ Stage 2 source-of-truth tsvs | Read-only references in the new prose; tsvs are not modified. md5 4/4 preservation enforced as a verification gate. |
| Manuscript ↔ identity-LD k2d outputs | Read-only narrative reference at the per-trait status table; the on-disk tree at `results_identity_ld/` is untouched and remains gitignored per ec86832. |
| Git history | Single atomic source commit on branch `main` (no worktree per CLAUDE.md GPFS constraint). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|---|---|---|---|---|
| T-wbf-01 | Tampering | Stage 2 source-of-truth tsvs | mitigate | md5 4/4 pre/post-edit hash check (`results/multitrait/coloc_summary.tsv`, `results/fine_mapping/finemap_summary.tsv`, `results/fine_mapping/finemap_summary_augmented.tsv`, `results/qtl_coloc/tier_assignments.tsv`); verification gate hard-fails on any mismatch. |
| T-wbf-02 | Tampering | results_identity_ld/ tree | mitigate | Verification gate: `git status --short \| grep -E "^\?\? results_identity_ld"` must return empty (file remains gitignored per ec86832). On-disk file count unchanged. |
| T-wbf-03 | Information Disclosure | Manuscript prose vs disk truth | mitigate | All numeric anchors (3/5 non-convergence, PP.H4 = 1.00, PP.H4 = 0.0517, n = 503, commit hashes) cited verbatim from authoritative sources documented in `<authoritative_facts>`; no recomputation; the 3/5 vs Eval 2(a)'s "4/5" reconciliation explicitly resolved in favor of disk-authoritative 3/5 with citation to Fig 3 caption commit 2d5f710 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv. |
| T-wbf-04 | Repudiation | Audit-trail completeness | mitigate | Inline citations to `AUDIT-REVIEW-2026-04-25.md Eval 3.4` + `Eval 2(a)` + Stage 2 commit hashes `6de9a88` + `a6e3214` + `7d54183` + Refs 20 (Zou 2022) + 29 (Wang 2020) + 42 (Pasaniuc & Price 2017); SUMMARY.md records pre/post diffs + md5 manifest + verification-gate outcomes. |
| T-wbf-05 | Tampering | Surrounding manuscript lines (L26-L30, L144, L146, L150-L156, L291, L295) | mitigate | `diff` byte-identity check against pre-edit snapshots `/tmp/wbf-pre-L26-30.txt` + `/tmp/wbf-pre-L144-156.txt`; verification gate hard-fails on drift outside the L148 (Task 1) and L28 (Task 2) edit lines. |
| T-wbf-06 | Information Disclosure | Forbidden-framing token leakage in new prose / SUMMARY / commit message | mitigate | Project-standard regex (`revision\|cleanup\|fix-up\|fix\|machine learning\|\bML\b\|thrifty\|evolutionary medicine\|placeholder\|\bv1\b\|simplified\|\bTBD\b\|for now\|static`) applied to new L148 prose, new L28 prose surface (1 line), SUMMARY.md narrative, and commit message body; zero matches required in NEW content. Pre-existing file-wide instances (e.g., the existing word "fix" in `structurally fixed mid-Stage-2` at L28) accepted and not modified. |
| T-wbf-07 | Denial of Service | Pre-existing dirty files | accept | `.claude/settings.json` + `.planning/config.json` + `.claude/scheduled_tasks.lock` are pre-existing modifications outside this task's scope; do NOT stage; do NOT commit. Verification gate confirms unchanged across the task. |
| T-wbf-08 | Tampering | Atomic-commit scope | mitigate | Single source commit covering exactly 1 file = `docs/manuscript/track_a_pivot.md`; STATE.md row + this PLAN.md + SUMMARY.md committed by orchestrator in a separate docs commit per Step 8 (NOT in the executor's source commit). |

</threat_model>

<verification>
**Pre-edit snapshots (mandatory, captured at the very start of Task 1; reused by Task 2):**

```bash
sed -n '26,30p' docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-L26-30.txt
sed -n '144,156p' docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-L144-156.txt
sed -n '295p' docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-L295.txt
md5sum results/multitrait/coloc_summary.tsv results/fine_mapping/finemap_summary.tsv results/fine_mapping/finemap_summary_augmented.tsv > /tmp/wbf-pre-stage2-md5.txt
md5sum results/qtl_coloc/tier_assignments.tsv >> /tmp/wbf-pre-stage2-md5.txt
git status --short > /tmp/wbf-pre-status.txt
wc -l docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-file-linecount.txt
grep -cE "TODO[A-Z-]*" docs/manuscript/track_a_pivot.md > /tmp/wbf-pre-TODO-count.txt
```

**Post-edit verification gates (consolidated; each gate is a hard fail):**

| # | Gate | Command | Expected |
|---|---|---|---|
| 1 | TODO marker dropped | `grep -c "TODO-COMPOSITION-FOLLOWON" docs/manuscript/track_a_pivot.md` | `0` |
| 2 | TODO-marker count delta ≤ 0 | `pre=$(cat /tmp/wbf-pre-TODO-count.txt); post=$(grep -cE "TODO[A-Z-]*" docs/manuscript/track_a_pivot.md); [ "$post" -le "$pre" ]` | true (no new markers; one dropped) |
| 3 | Forbidden phrase #1 | `grep -c "consistent with credible-set collapse" docs/manuscript/track_a_pivot.md` | `0` |
| 4 | Forbidden phrase #2 | `grep -c "most dramatic flagship change" docs/manuscript/track_a_pivot.md` | `0` |
| 5 | Forbidden phrase #3 | `grep -c "illustrates the inflation mechanism" docs/manuscript/track_a_pivot.md` | `0` |
| 6 | Forbidden phrase #4 | `grep -c "correctly fails to produce a credible set" docs/manuscript/track_a_pivot.md` | `0` |
| 7 | Non-convergence disclosure | `grep -c "non_converged" docs/manuscript/track_a_pivot.md` | `≥ 2` (1 pre-existing at L295 from ie0; ≥1 added at L148) |
| 8 | L = 20 forward-look | `grep -c "L = 20" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 9 | Audit-aligned reframe | `grep -cE "(missing run\|not executed\|not run)" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 10 | AUDIT-REVIEW citation | `grep -c "AUDIT-REVIEW-2026-04-25" docs/manuscript/track_a_pivot.md` | `≥ 1` (already cited at L28 + L138 pre-edit; rewrite adds at L148 OR keeps existing) |
| 11 | Eval 3.4 anchor | `grep -c "Eval 3.4" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 12 | Eval 2(a) anchor | `grep -c "Eval 2(a)" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 13 | Canonical lead variant | `grep -c "rs3184504" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 14 | ATXN2 PP.H4 preserved | `grep -c "0.0517" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 15 | Zou 2022 citation | `grep -cE "Zou.*(2022\|et al)" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 16 | Wang 2020 citation | `grep -cE "Wang.*(2020\|et al)" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 17 | Italic *SH2B3* | `grep -c "\*SH2B3\*" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 18 | Italic *ATXN2* | `grep -c "\*ATXN2\*" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 19 | Stage 2 commit hashes | `for h in 6de9a88 a6e3214 7d54183; do grep -c "$h" docs/manuscript/track_a_pivot.md; done` | each `≥ 1` |
| 20 | Supplementary roadmap reference | `grep -c "Supplementary Methods" docs/manuscript/track_a_pivot.md` | `≥ 1` |
| 21 | L148 word count | `awk 'NR==148 { n=split($0, a, /[ \t]+/); print n }' docs/manuscript/track_a_pivot.md` | `250-400` |
| 22 | Stage 2 md5 4/4 preserved | `md5sum -c /tmp/wbf-pre-stage2-md5.txt` | all OK |
| 23 | L26-L30 byte-identical | `diff /tmp/wbf-pre-L26-30.txt <(sed -n "26,30p" docs/manuscript/track_a_pivot.md) \| grep "Cross-trait" \| head -1` | exactly one diff line at L28 (TODO parenthetical removed); L26, L27, L29, L30 unchanged |
| 24 | L144 + L146 + L150-L156 byte-identical | `diff /tmp/wbf-pre-L144-156.txt <(sed -n "144,156p" docs/manuscript/track_a_pivot.md)` | only L148 differs |
| 25 | L295 byte-identical | `diff /tmp/wbf-pre-L295.txt <(sed -n "295p" docs/manuscript/track_a_pivot.md)` | empty |
| 26 | results_identity_ld/ still gitignored | `git status --short \| grep -cE "^\?\? results_identity_ld"` | `0` |
| 27 | Pre-existing dirty files unchanged | `diff /tmp/wbf-pre-status.txt <(git status --short)` | only the rewritten manuscript file appears in the post-snapshot |
| 28 | Atomic commit scope | `git diff HEAD~1 HEAD --name-only` | exactly `docs/manuscript/track_a_pivot.md` |
| 29 | Forbidden-framing tokens in NEW prose only (delta = 0) | `pre=$(grep -cE "revision\|cleanup\|fix-up\|machine learning\|\bML\b\|thrifty\|evolutionary medicine\|placeholder\|\bv1\b\|simplified\|\bTBD\b\|for now\|static" was-pre-snapshot); post=$(grep -cE same docs/manuscript/track_a_pivot.md); delta = post - pre` | `≤ 0` (Task 1 + Task 2 should not introduce any new forbidden tokens; pre-existing file-wide instances are accepted) |
| 30 | Convergence-disclosure cross-reference | `grep -cE "3 of 5 SH2B3 EUR" docs/manuscript/track_a_pivot.md` | `≥ 1` (rewrite uses 3/5 framing, NOT audit's 4/5) |
| 31 | File total line count unchanged | `diff /tmp/wbf-pre-file-linecount.txt <(wc -l docs/manuscript/track_a_pivot.md)` | empty (intra-line edits only at L28 and L148) |

**Critical reconciliation note (must be reflected in SUMMARY.md):** AUDIT-REVIEW-2026-04-25.md Eval 2(a) header line 42 says "4 of 5 traits return `status = non_converged`" but its per-trait list (BMI, hypertension, stroke; only asthma and t2d = ok) sums to 3 non_converged of 5. The Fig 3 caption at L295 (commit 2d5f710), the quick-260425-1vy SUMMARY (lines 45-51), and the IDENTITY-LD-K2D-FIT-SUMMARY.tsv (committed at ec86832) all agree on 3/5. The rewrite uses the disk-authoritative count of **3 of 5**, citing the Fig 3 caption commit 2d5f710 + IDENTITY-LD-K2D-FIT-SUMMARY.tsv as authoritative; this resolves the audit's internal numerical drift in favor of disk truth.
</verification>

<success_criteria>
**Hard success gates (each must pass; from §Background §Success gates 1-20):**

1. L28 parenthetical `(TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)` removed; surrounding sentence reads `...is reported in a planned supplementary follow-on. Cross-trait...` with valid period punctuation.
2. L148 paragraph replaced with audit-aligned 250-400 word version (~half the pre-edit length).
3. `grep -c "TODO-COMPOSITION-FOLLOWON" docs/manuscript/track_a_pivot.md` == 0.
4. No NEW TODO markers introduced (TODO-marker delta ≤ 0).
5. `grep -c "consistent with credible-set collapse" docs/manuscript/track_a_pivot.md` == 0.
6. `grep -c "most dramatic flagship change" docs/manuscript/track_a_pivot.md` == 0.
7. `grep -c "non_converged" docs/manuscript/track_a_pivot.md` ≥ 2 (1 pre-existing at L295 + ≥1 added at L148).
8. `grep -c "L = 20" docs/manuscript/track_a_pivot.md` ≥ 1 (forward-look citation).
9. `grep -cE "(missing run\|not executed\|not run)" docs/manuscript/track_a_pivot.md` ≥ 1 (audit-aligned reframe).
10. `grep -c "AUDIT-REVIEW-2026-04-25" docs/manuscript/track_a_pivot.md` ≥ 1 (cite the audit doc as provenance).
11. `grep -c "rs3184504" docs/manuscript/track_a_pivot.md` ≥ 1 (canonical lead variant preserved).
12. `grep -c "0.0517" docs/manuscript/track_a_pivot.md` ≥ 1 (ATXN2/Adrenal_Gland Tier C QTL PP.H4 preserved).
13. `grep -cE "(Wang.*2020\|Zou.*2022)" docs/manuscript/track_a_pivot.md` ≥ 1 (L = 20 methodological citation).
14. Italic markdown gene symbols `*SH2B3*` and `*ATXN2*` present.
15. Stage 2 real-LD md5 4/4 byte-identical pre vs post-edit (`results/multitrait/coloc_summary.tsv`, `results/fine_mapping/finemap_summary.tsv`, `results/fine_mapping/finemap_summary_augmented.tsv`, `results/qtl_coloc/tier_assignments.tsv`).
16. `?? results_identity_ld/` does NOT appear in `git status` post-edit (still gitignored per ec86832).
17. L26-L27 + L29-L30 + L144 + L146 + L150-L156 + L295 byte-identical pre vs post-edit.
18. Zero forbidden-framing tokens introduced into NEW prose / SUMMARY.md / commit message (file-wide regex delta ≤ 0).
19. Net file line-count delta == 0 (intra-line edits only at L28 + L148).
20. Convergence-disclosure cross-reference: rewritten L148 says "3 of 5 SH2B3 EUR traits non_converged" matching the Fig 3 caption at L295 (BMI, hypertension, stroke); reconciles audit Eval 2(a)'s text claim of "4/5" to disk-authoritative 3/5.

**Atomic-commit scope:**
- Single source commit covering exactly 1 file: `docs/manuscript/track_a_pivot.md`
- Commit message stem: `docs(quick-260425-wbf): rewrite §3.4 SH2B3 case study (Eval 3.4 + 2a) and drop Abstract TODO marker`
- STATE.md row + this PLAN.md + SUMMARY.md committed by the orchestrator in a separate docs commit per Step 8

**Honest-framing lock chain extends from 5 places to 6:**
- (1) `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` header purpose block (commit 105484d)
- (2) Locked-scalar block comments in the same R script (commit 105484d)
- (3) In-figure `plot_annotation(caption = ...)` block (commit 105484d)
- (4) `.planning/quick/260425-1vy-track-a-figures-1a-3/260425-1vy-SUMMARY.md` honest-framing lock (commit 105484d)
- (5) L295 manuscript Fig 3 caption (commit 2d5f710)
- **(6 NEW) L148 manuscript §3.4 SH2B3 case-study paragraph (this commit)**
</success_criteria>

<output>
After completion, the executor creates `.planning/quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md` containing:

1. **One-liner**: 1-2 sentence summary of the §3.4 rewrite + Abstract TODO drop.
2. **Atomic source commit**: SHA, branch, files changed, insertions/deletions, diff hunks (`@@ -28` and `@@ -148`), pre/post HEAD.
3. **Verbatim copy of the new L148 paragraph** (~250-400 words; the load-bearing artifact).
4. **Verbatim copy of the new L28 sentence neighborhood** showing the parenthetical removed.
5. **Source-of-truth provenance table**: each numeric anchor in the new prose mapped to its authoritative source (AUDIT-REVIEW Eval ref, TRACK-A-FROZEN-NUMBERS line ref, Fig 3 caption commit 2d5f710 ref, IDENTITY-LD-K2D-FIT-SUMMARY.tsv ref, §References Refs 20 / 29 / 42 ref).
6. **md5 manifest**: Stage 2 source-of-truth tsvs pre vs post-edit (4/4 byte-identical).
7. **results_identity_ld/ output preservation note**: tree untouched; `??` line absent from `git status`.
8. **Greppable check outcomes**: each of the 31 verification gates marked PASS / FAIL.
9. **Surrounding-line byte-identity diff**: L26-L30 + L144 + L146 + L150-L156 + L295 vs pre-edit snapshots — empty diffs except at L28 (Task 2) and L148 (Task 1).
10. **Forbidden-framing greppable check**: zero matches in new L148 prose + new L28 sentence + SUMMARY.md narrative + commit message body.
11. **Word-count rationale**: L148 word count (target 250-400; cite the rationale if at the upper bound).
12. **Reconciliation note**: explicit statement that the rewrite uses 3/5 (disk-authoritative per Fig 3 caption + IDENTITY-LD-K2D-FIT-SUMMARY.tsv) rather than the audit's text claim of 4/5; cite the resolution.
13. **Honest-framing lock chain status**: extended from 5 places (R-script header + locked-scalar block + in-figure plot_annotation + 1vy SUMMARY + L295 caption) to 6 places (this L148 paragraph).
14. **Handoff for the next quick task**: any out-of-scope follow-ons surfaced during execution (expected: none beyond what is already documented in the audit's outstanding-items list — Eval 2(b) L = 20 re-fit pending Terminal A LSF, Eval 3.6 ld_overlap=0 schema check, Eval 4(a) residual fig3 EXPECTED scalars hardcode, audit High-Quality #2 canonical SH2B3 trait-pair runs gated on L = 20, audit High-Quality #3 LD-overlap dose-response figure).
15. **Self-Check: PASSED** with verified file existence + commit hash + all 31 verification gates pass.
</output>
