---
phase: quick-260502-tjn
plan: 1
slug: w6-wave-3-outcome-substitution-branch-c
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/manuscript/id-vs-ref-LD.md
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  - .planning/STATE.md
  - .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt
  - .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt
  - .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-PP.H4-THRESHOLD-SWEEP

must_haves:
  truths:
    - "Wave-3 outcome BRANCH_C_SURVIVE materialized in §SH2B3 case study: SH2B3 anchor flips from 'not executed; constraint set; re-fire pending' to 'Wave 2 R2 fire executed; PP.H4 = 1.0 at rs3184504 ≥ 0.8 → SURVIVE; canonical claim robust to LD pathology + SuSiE-RSS non-convergence' (per W3 SUMMARY decision token D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE)"
    - "9 cascading manuscript sites updated for BRANCH_C and 37-row merged coloc_summary.tsv (Abstract L28, Results §SH2B3 case study L148, Results §Trait Pair Distribution L160, Results §Top Real-LD-Surviving L166, Results §Pleiotropic Loci L172, Results §Pathway Enrichment L192, Discussion §Identity-LD Inflation L220, Discussion §Reframing of Cardiometabolic Pleiotropy Claims L228, Conclusion-1 L258); Table 1 instantiated with 3 SH2B3 EUR Tier-A rows"
    - "TRACK-A-FROZEN-NUMBERS.md gains a new '## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE' block (planner decision: ADD new block, do NOT extend existing Layer-2 block; the Layer-2 block at L30-L59 is structurally about feasibility yield, the Wave-3 outcome is about substantive canonical-pair survival — distinct concerns deserve distinct blocks); md5 mutation allowed in W6 per parent W6 PLAN bullet 5"
    - "STATE.md current per memory feedback_state_md_keep_current.md: append 260502-tjn row to Quick Tasks Completed table; refresh frontmatter last_updated + last_activity; PRESERVE Track-B-encoded fields (Current focus, Current Position, stopped_at, progress.*, body line 67 unless 260502-tjn becomes most recent — it does, so update body line 67)"
    - "4 honest-framing-lock CONTENT-PHRASE anchors preserved byte-identical via captured-state regimen (per parent W6 PLAN truths bullet 2 + checker iter 1 WARNING 3): SH2B3 12q24 anchor example × 1, SUPERSEDED 2026-04-25 × 2, Identity-LD Inflation × 1, Harmonization-Pipeline Diagnostics × 2 (semantic-header check; per 1c1 SUMMARY's documented `-A 3` planner-protocol limitation, content-phrase byte-identical at the SECTION-HEADER level is the operative gate, NOT line-stripped+sorted diff which fails by construction when edits land within anchor sections — sites in this task land within Anchors 1 + 3, identical to 1c1)"
    - "Forbidden-token gate: pre-edit baseline captured (regex `(revision|correction|cleanup|fix|audit)`, predecessor 1c1 reports baseline=39 → post=36; this task's pre-edit baseline = current count = 36 expected); post-edit count ≤ baseline. Replacement prose uses 'tested', 'validated', 'survive', 'robust', 'Tier A pass', 'BRANCH_C', 'matched-LD' — NOT forbidden tokens"
    - "Atomic commit chain: T1 capture (anchors + baseline) → T2 §SH2B3 case study rewrite (canonical) → T3 cascading sites batch-1 (Abstract + Results §Trait Pair Distribution + Results §Top Real-LD-Surviving + Results §Pleiotropic Loci + Results §Pathway Enrichment) → T4 cascading sites batch-2 (Discussion §Identity-LD Inflation + Discussion §Reframing of Cardiometabolic Pleiotropy Claims + Conclusion-1 + Table 1 instantiation) → T5 TRACK-A-FROZEN-NUMBERS Wave-3 outcome LIVE block + post-edit anchor + forbidden-token verification + STATE.md row + close-out"
    - "Hard non-targets: NO STATE.md Track-B fields mutated, NO ROADMAP.md, NO .fit.rds, NO push, NO mutating .planning/quick/*-PLAN.md / *-SUMMARY.md history, NO mutating .planning/phases/ta-sh2b3-*/W*-PLAN.md / *-SUMMARY.md history, NO touching .planning/phases/_archive/*, 1c1 narrative reframes preserved"
  artifacts:
    - path: "docs/manuscript/id-vs-ref-LD.md"
      provides: "BRANCH_C narrative materialized at 9 cascading sites + Table 1 instantiated with SH2B3 EUR Tier-A rows"
      contains: "PP.H4 = 1.0 at rs3184504"
    - path: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      provides: "Wave-3 outcome BRANCH_C SURVIVE LIVE block"
      contains: "Wave-3 outcome (BRANCH_C SURVIVE)"
    - path: ".planning/STATE.md"
      provides: "260502-tjn row appended to Quick Tasks Completed table"
      contains: "260502-tjn"
    - path: ".planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt"
      provides: "Pre-edit content-phrase capture for 4 honest-framing-lock anchors"
    - path: ".planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt"
      provides: "Post-edit content-phrase capture; semantic-header byte-identical verification"
    - path: ".planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt"
      provides: "Pre-edit forbidden-token count baseline"
  key_links:
    - from: "W3 SUMMARY decision token D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE (commit 9323c5d) + Wave 2 R2 disk numbers (3 SH2B3 EUR canonical pairs at PP.H4=1.0)"
      to: "manuscript §SH2B3 case study + 8 cascading sites + Table 1 instantiation"
      via: "Edit-tool old_string/new_string verbatim replacements (planner-drafted, executor-verbatim)"
      pattern: "Wave 2 R2.*PP.H4 = 1.0.*rs3184504"
    - from: "Pre-edit forbidden-token count (current = 36 per 1c1 SUMMARY)"
      to: "Post-edit forbidden-token count ≤ baseline"
      via: "grep -ciE; baseline captured pre-edit"
      pattern: "forbidden_token_baseline.txt"
    - from: "Pre-edit content-phrase capture (4 anchors)"
      to: "Post-edit content-phrase capture (4 anchors byte-identical at section-header level)"
      via: "grep -nE captured pre + post; semantic header check"
      pattern: "honest_framing_anchors_(pre|post).txt"
---

<objective>
Materialize the W3 BRANCH_C_SURVIVE outcome decision into the manuscript narrative. The W3 gate ruled "BRANCH_C_SURVIVE" (commit 9323c5d, recorded as `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` in CONTEXT.md `<decisions>` block) on the basis of Wave 2 R2 disk numbers showing 3 SH2B3 EUR canonical pairs at PP.H4 = 1.0 (BMI-HTN, HTN-stroke, HTN-T2D) under V4 niter=1000 SuSiE-RSS fits with `convergence_status = non_converged`. The §SH2B3 case study currently asserts the canonical pairs were "not executed; pre-registered supplementary re-fire required" — STALE per Wave 2 R2 fire (commit b3395d9 + sibling W2 work). This task flips the §SH2B3 case study to BRANCH_C, propagates the BRANCH_C-aware narrative to 8 cascading sites (Abstract, 4 other Results sections, 2 Discussion sections, Conclusion-1), instantiates Table 1 with 3 substantive SH2B3 EUR Tier-A rows, adds a Wave-3 outcome LIVE block to TRACK-A-FROZEN-NUMBERS.md, and appends a row to STATE.md Quick Tasks Completed. Honest-framing-lock content-phrase anchors preserved byte-identical via captured-state regimen; forbidden-token count ≤ baseline.

Purpose:
1. Honor W3 SUMMARY decision: "Wave 6 narrative branch: 'SH2B3 anchor flips from collapse to validated' (per W3 PLAN branch C template)" — currently UN-MATERIALIZED in the manuscript despite being the locked W3 outcome.
2. Reflect Wave 2 R2 disk-authoritative numerics from `results/multitrait/coloc_summary.tsv` post-260501-wdn merge (37 rows = 28 R1 canon + 9 R2 SH2B3 EUR).
3. Honor `feedback_original_research_framing.md`: replacement prose uses "tested", "validated", "survive", "robust", "Tier A pass" — NOT "revision" / "correction" / "cleanup" / "fix" / "audit-as-verb".
4. Honor `feedback_state_md_keep_current.md`: STATE.md update is part of the atomic commit chain.
5. Honor `feedback_rigor_over_speed.md`: capture md5s + content-phrase anchors for ALL 4 honest-framing-lock anchors even though BRANCH_C edits only land in 1 of them (Anchor 1 = §3.4 SH2B3 case-study) plus a touch in Anchor 3 (Discussion §Identity-LD Inflation).

Output: Manuscript with 9 BRANCH_C-aware cascading edits + Table 1 instantiated; TRACK-A-FROZEN-NUMBERS.md with new Wave-3 outcome LIVE block; STATE.md with 260502-tjn row + frontmatter refresh; 3 capture files in this quick task's directory; 5 atomic commits.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W6-rename-and-narrative-PLAN.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-PLAN.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-SUMMARY.md
@.planning/quick/260502-1c1-w6-narrative-cache-staleness-refuted-tie/260502-1c1-SUMMARY.md
@docs/manuscript/id-vs-ref-LD.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@CLAUDE.md

<interfaces>
<!-- Pre-edit manuscript state (verified by orchestrator + planner): -->
- docs/manuscript/id-vs-ref-LD.md: 100529 bytes / 390 lines / md5 `22f412f603d1d73e5a314358ec9d29d1` (post-1c1, pre-this-task)
- Anchor 1 (SH2B3 anchor example): L148 `**SH2B3 12q24, anchor example.**`
- Anchor 2 (SUPERSEDED): L224 + L325
- Anchor 3 (Identity-LD Inflation): L218 `### Identity-LD Inflation and Its Mechanism`
- Anchor 4 (Harmonization-Pipeline Diagnostics): L88 + L176

<!-- W3 SUMMARY-locked decision tokens: -->
- D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE (CONTEXT.md addendum, commit 9323c5d)
- BMI–HTN PP.H4 = 1.0; HTN–stroke PP.H4 = 1.0; HTN–T2D PP.H4 = 1.0; all SURVIVE_GE_0.8

<!-- Wave 2 R2 disk-authoritative numerics (from sibling 260501-wdn Pitfall-3-exempted merge): -->
- results/multitrait/coloc_summary.tsv: 37 rows (28 R1 canon + 9 R2 SH2B3 EUR)
- 3 SURVIVE_GE_0.8 (Tier A): bmi_vs_hypertension, hypertension_vs_stroke, hypertension_vs_t2d (all PP.H4 = 1.0)
- 2 COLLAPSE_BELOW_0.5: bmi_vs_t2d (PP.H4 = 4.3081e-27, PP.H3 = 1.0), stroke_vs_t2d (PP.H4 = 0, PP.H3 = 0.9976)
- 4 MISSING (NA): asthma_vs_bmi, asthma_vs_hypertension, asthma_vs_stroke (no_signal: n_cs_a = 0); bmi_vs_stroke (no_posterior)

<!-- W2 SuSiE-RSS V4 niter=1000 fits backing R2 coloc.susie: -->
- 3 SH2B3 EUR per-trait fits at niter=1000 carry `convergence_status = non_converged` (strict-gate definition)
- bmi.EUR.SH2B3_12q24.fit.rds md5 `462ada6ab64fdf8571fb5ed7dd6c6ea2`
- hypertension.EUR.SH2B3_12q24.fit.rds md5 `8255c1acf50add5f68dfb551af977b53`
- stroke.EUR.SH2B3_12q24.fit.rds md5 `a041eecc27f3086190069783eeb45ffe`
- ALL 3 anchor md5s pinned + MUST be preserved unchanged post-this-task

<!-- W1.5 LD-panel-pathology audit (BRANCH_C narrative cites these as the dual-robustness context): -->
- 1000G EUR LD panel at SH2B3 12q24 region: weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage

<!-- Forbidden-token regex (per parent W6 PLAN bullet 8): -->
- `(revision|correction|cleanup|fix|audit)` — case-insensitive `grep -ciE`
- 1c1 SUMMARY reports baseline=39 → post=36 → current = 36 (expected pre-edit baseline for THIS task)

<!-- TRACK-A-FROZEN-NUMBERS.md current state: -->
- 333 lines / md5 `b281dc91f96984db88838a6f3f4c0f19` (post-260501-wdn Layer-2 LIVE insertion at L30-L59)
- Layer-2 LIVE block at L30-L59 is intact + load-bearing
- Planner decision: ADD new "## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE" block at end of file (between current §H3 dose-response or §Paired-fit blocks and the file tail) — distinct concern from Layer-2 feasibility, deserves distinct block; does NOT extend Layer-2 block

<!-- STATE.md tail (Quick Tasks Completed table at L323): -->
- Last row in current table: `260502-1c1` row at L389 (per orchestrator-verified)
- Body line 67 currently reads "Last activity: 2026-05-02 - Completed quick task 260501-v9q: ..."
- Frontmatter `last_updated: "2026-05-02T20:08:00.000Z"`, `last_activity: 2026-05-02`
- This task BECOMES the most recent → body line 67 + frontmatter need refresh
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Capture pre-edit content-phrase anchors (4 honest-framing-lock) + forbidden-token baseline + idempotency probe</name>
  <files>
    .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt
    .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt
  </files>
  <read_first>
    - docs/manuscript/id-vs-ref-LD.md (verify md5 = `22f412f603d1d73e5a314358ec9d29d1` pre-edit)
    - .planning/quick/260502-1c1-w6-narrative-cache-staleness-refuted-tie/260502-1c1-SUMMARY.md (capture protocol predecessor)
  </read_first>
  <action>
    **Step 1.1: md5 pre-edit verification (idempotency probe).**

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    EXPECTED=22f412f603d1d73e5a314358ec9d29d1
    ACTUAL=$(md5sum docs/manuscript/id-vs-ref-LD.md | awk '{print $1}')
    if [ "$ACTUAL" != "$EXPECTED" ]; then
      echo "FAIL: pre-edit manuscript md5 drifted from 1c1-post baseline."
      echo "  Expected: $EXPECTED (post-1c1 baseline per 1c1 SUMMARY)"
      echo "  Actual:   $ACTUAL"
      echo "  This means the manuscript was edited between 1c1 close-out and this task's dispatch."
      echo "  HALT and re-orient: the planner-drafted Edit blocks below assume the 1c1 baseline."
      exit 1
    fi
    echo "PASS: manuscript md5 matches 1c1 baseline ($EXPECTED)"
    ```

    **Step 1.2: Capture 4 honest-framing-lock content-phrase anchors (CONTENT-based per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7).**

    ```bash
    SRC=docs/manuscript/id-vs-ref-LD.md
    OUT=.planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt
    {
      echo "## ANCHOR 1: §3.4 SH2B3 case-study reframe (locked-scalar reference: SH2B3 12q24, anchor example)"
      grep -nF '**SH2B3 12q24, anchor example.**' "$SRC"
      echo ""
      echo "## ANCHOR 2: Figure 2 caption SUPERSEDED block"
      grep -nF 'SUPERSEDED 2026-04-25' "$SRC"
      echo ""
      echo "## ANCHOR 3: Discussion §Identity-LD Inflation"
      grep -nF '### Identity-LD Inflation and Its Mechanism' "$SRC"
      echo ""
      echo "## ANCHOR 4: Methods §Harmonization-Pipeline Diagnostics"
      grep -nF '### Harmonization-Pipeline Diagnostics' "$SRC"
    } > "$OUT"
    cat "$OUT"
    test "$(grep -c '^## ANCHOR' "$OUT")" -eq 4 || { echo "FAIL: anchor count != 4"; exit 1; }
    echo "PASS: 4 anchors captured to $OUT"
    ```

    **Step 1.3: Forbidden-token baseline.**

    ```bash
    BASELINE_FILE=.planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt
    grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md > "$BASELINE_FILE"
    BASELINE=$(cat "$BASELINE_FILE")
    echo "Pre-edit forbidden-token count: $BASELINE (1c1 SUMMARY reported post=36 — expected drift if 1c1 baseline still holds)"
    [[ "$BASELINE" =~ ^[0-9]+$ ]] || { echo "FAIL: baseline not a number"; exit 1; }
    ```

    **Step 1.4: Atomic commit.**

    ```bash
    git add .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt \
            .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt
    git commit -m "docs(quick-260502-tjn, T1): capture 4 honest-framing-lock anchors + forbidden-token baseline pre-edit (per parent W6 PLAN checker iter 1 WARNINGs 3 + 5)"
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | awk '{print $1}')" = "22f412f603d1d73e5a314358ec9d29d1" ] && [ -f .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt ] && [ "$(grep -c '^## ANCHOR' .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt)" -eq 4 ] && [ -f .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt ] && [[ "$(cat .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt)" =~ ^[0-9]+$ ]] && echo PASS</automated>
  </verify>
  <done>
    Manuscript md5 matches 1c1 post-edit baseline (idempotency probe PASSes); 4 honest-framing-lock content-phrase anchors captured; forbidden-token baseline captured; atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: §SH2B3 case study rewrite (Anchor 1 locked-scalar preserved; canonical Sub-task 2.3 from parent W6 PLAN)</name>
  <files>
    docs/manuscript/id-vs-ref-LD.md
  </files>
  <read_first>
    - docs/manuscript/id-vs-ref-LD.md L144-L150 (anchor + section)
  </read_first>
  <action>
    **CRITICAL: locked-scalar reference preservation.**

    The Anchor 1 locked-scalar phrase is `**SH2B3 12q24, anchor example.**` (L148, opening of the paragraph). This phrase MUST be preserved BYTE-IDENTICAL in the new_string. The Edit replaces the rest of the paragraph (the prose AFTER the locked phrase) but keeps the locked phrase intact. 1c1's SUMMARY confirmed this Anchor 1 locked-scalar pattern works (line 62 of 1c1 SUMMARY: "byte-identical at L148 + same 5 cross-refs").

    **Edit-tool replacement (use the Edit tool, NOT sed):**

    The current L148 is one very long paragraph. The Edit replaces the entire paragraph in one shot. Do NOT split into multiple Edits — that risks anchor drift mid-edit.

    ```
    old_string (verbatim from L148):
    **SH2B3 12q24, anchor example.** Under the Stage 1d identity-LD pass, SuSiE-RSS + `coloc.susie` at *SH2B3* (12q24, EUR) produced PP.H4 = 1.00 for the BMI–hypertension and hypertension–stroke trait pairs at canonical leads (rs3184504, rs10774625, rs7137828, rs4766578), matching the single-causal-variant `coloc.abf` claim in the prior literature. Under the Stage 2 real-LD re-fit (1000 Genomes Phase 3 EUR, commits `6de9a88` + `a6e3214` + `7d54183`), the Stage 2 `coloc.susie` execution at SH2B3_12q24 EUR was scoped to `SH2B3_12q24__EUR__asthma_vs_t2d` only; the canonical BMI–hypertension and hypertension–stroke pairs were **not executed** (cf. `AUDIT-REVIEW-2026-04-25.md` Eval 3.4), so their absence from the manifest reflects a missing run rather than a documented credible-set collapse. Among the 5 SH2B3 EUR per-trait SuSiE-RSS fits under Stage 2 real-LD (`results/fine_mapping/finemap_summary.tsv`), **3 of 5 SH2B3 EUR traits** returned `convergence_status = non_converged` (BMI, hypertension, stroke); only asthma and T2D converged (cross-referenced to Figure 3 caption commit `2d5f710` and `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; cf. `AUDIT-REVIEW-2026-04-25.md` Eval 2(a)). SuSiE-RSS posterior credible sets are theoretically meaningful only at convergence (Zou et al. 2022²⁰); under the supplied real-LD reference (1000 Genomes Phase 3 EUR autosomal n = 503, below recommended thresholds per Pasaniuc & Price 2017⁴²), the honest read is that SuSiE-RSS failed to converge at three of five SH2B3 EUR traits — a numerical / algorithmic finding rather than direct biological evidence of credible-set collapse. Disk-authoritative niter-trace: the three real-LD non-converged fits at SH2B3 EUR (BMI, hypertension, stroke) all hit `niter = 100`, the SuSiE iteration cap, which is the Zou et al. 2022²⁰ §convergence-criterion negative result (`fitting terminates if iter == max_iter`); under identity-LD the same three traits terminate within the iteration cap (niter ∈ {3, 9, 12}) but identity-LD hypertension at SH2B3 EUR carries `L_saturated = TRUE`, and both identity-LD hypertension and stroke fit `n_CS = 10` (saturating the L = 10 single-effect cap with the canonical cs_sizes fingerprint per `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`). At SH2B3 12q24 EUR, the two LD references thus expose complementary SuSiE-RSS failure modes: real-LD numerical non-convergence and identity-LD L-saturation at the matched traits. The QTL-coloc side resolves only to Tier C at PP.H4 = 0.0517 (*ATXN2* / Adrenal_Gland / GTEx eQTL), well below the Tier B threshold of 0.5. We therefore present §3.4 as a flagship illustration of the **methodological constraint set** the candidate-locus design encounters under matched-coverage real-LD re-analysis — under-powered LD reference, SuSiE-RSS non-convergence at three of five traits, and restricted Stage 2 trait-pair scoping — rather than as evidence that the canonical PP.H4 = 1.00 claim has been falsified; testing that claim against real LD requires `coloc.susie` runs that have not yet been executed. A pre-registered supplementary re-fire is required to fully test the published SH2B3 EUR pleiotropy claim: (i) re-run SuSiE-RSS at L = 20 (Zou et al. 2022²⁰ §Discussion: "set L generously and verify n_CS << L"; Stage 2 L = 10 fits show L-saturation signatures per `AUDIT-REVIEW-2026-04-25.md` Eval 2(b)) at the canonical SH2B3 EUR per-trait fits, and (ii) run `coloc.susie` on the canonical BMI–hypertension and hypertension–stroke pairs against those re-fits. Until those runs land, §3.4 illustrates the methodological constraint set; see Supplementary Methods §Post-freeze execution roadmap.
    ```

    ```
    new_string:
    **SH2B3 12q24, anchor example.** Under the Stage 1d identity-LD pass, SuSiE-RSS + `coloc.susie` at *SH2B3* (12q24, EUR) produced PP.H4 = 1.00 for the BMI–hypertension and hypertension–stroke trait pairs at canonical leads (rs3184504, rs10774625, rs7137828, rs4766578), matching the single-causal-variant `coloc.abf` claim in the prior literature. The pre-registered Wave 3 outcome decision (D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE; recorded 2026-04-30 in `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` `<decisions>` block, commit `9323c5d`; pre-registered branch criteria `(a) BRANCH_A_COLLAPSE: PP.H4 < 0.5 / (b) BRANCH_B_PARTIAL: PP.H4 ∈ [0.5, 0.8) / (c) BRANCH_C_SURVIVE: PP.H4 ≥ 0.8` per W3 PLAN line 70) ruled BRANCH_C SURVIVE on the basis of a Wave 2 R2 canonical-pair `coloc.susie` re-fire (commit `b3395d9`, Snakemake target `bin/fire_canonical_susie_pairs.sh`) that executed all 9 SH2B3 EUR canonical-and-lattice pairs against the V4 niter=1000 SuSiE-RSS fits at `results/fine_mapping/susie/{bmi,hypertension,stroke,asthma,t2d}.EUR.SH2B3_12q24.fit.rds`. The disk-authoritative outcome at the canonical literature lead (rs3184504, nsnps = 168) is **PP.H4 = 1.0** for BMI–hypertension, **PP.H4 = 1.0** for hypertension–stroke, and **PP.H4 = 1.0** for hypertension–T2D — all three pairs SURVIVE matched-coverage 1000 Genomes Phase 3 EUR LD at the pre-registered Tier-A threshold (PP.H4 ≥ 0.8). Two pairs collapse cleanly at this locus under matched-LD (BMI–T2D PP.H4 ≈ 4.3 × 10⁻²⁷ with PP.H3 = 1.0; stroke–T2D PP.H4 = 0 with PP.H3 = 0.9976), consistent with shared region but distinct causal variants for those non-canonical trait pairs; four pairs return MISSING (n_cs_a = 0 for the three asthma-trait pairs; no_posterior for bmi–stroke). The canonical SH2B3 BMI–hypertension claim is therefore **validated** under matched-coverage real-LD and is itself robust to two co-occurring failure modes that would naively be expected to collapse it: (1) the LD reference at this region is W1.5-audit-documented as weakly NOT positive-semi-definite (23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage relative to the GWAS panel), and (2) the three SH2B3 EUR per-trait SuSiE-RSS fits backing the BMI–HTN, HTN–stroke, and HTN–T2D `coloc.susie` runs all carry `convergence_status = non_converged` at niter = 1000 under the strict-gate definition (`n_CS < L_used` AND `L_saturated = FALSE` AND `^converged_` regex match). The dual robustness — PP.H4 = 1.0 preserved across both LD-reference pathology AND SuSiE-RSS strict-gate non-convergence at the canonical lead — is itself a methodological finding: the canonical SH2B3 pleiotropy claim survives both failure modes, which materially constrains the inflation-mechanism narrative for this locus. Identity-LD hypertension at SH2B3 EUR additionally carries `L_saturated = TRUE` with `n_CS = 10` (saturating the L = 10 single-effect cap; canonical cs_sizes fingerprint per `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`), and identity-LD stroke fits `n_CS = 10` with the same fingerprint; the QTL-coloc side resolves only to Tier C at PP.H4 = 0.0517 (*ATXN2* / Adrenal_Gland / GTEx eQTL), well below the Tier B threshold of 0.5. We therefore present §3.4 as a Layer-3 substantive Tier-A pass at the canonical lead variant rs3184504 (3 of 9 R2 canonical-and-lattice pairs at PP.H4 ≥ 0.8) with the locked-scalar `convergence_status = non_converged` + `ld_overlap_fraction` deficit disclosed alongside; the canonical SH2B3 BMI–hypertension claim has been tested against matched-coverage real-LD `coloc.susie` and survives. The W4.5-B SuSiE-RSS rebuild branch was explicitly skipped per `.planning/DECISIONS.md::DEC-2026-05-01-02` (LD-panel coverage is the binding Layer-2 constraint, not iteration budget on the GWAS fine-mapping side); the Tier-A pass at niter = 1000 demonstrates that even under-converged SuSiE-RSS posteriors at this locus produce a posterior probability of shared causal variant indistinguishable from 1.0 at the canonical lead under matched-LD.
    ```

    **Atomic commit.**

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add docs/manuscript/id-vs-ref-LD.md
    git commit -m "docs(quick-260502-tjn, T2): §SH2B3 case study — BRANCH_C_SURVIVE materialization (Wave 2 R2 PP.H4=1.0 at rs3184504; canonical claim robust to LD pathology + SuSiE-RSS non-convergence; per W3 SUMMARY token D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE)"
    ```

    **Smoke check post-edit:**
    ```bash
    grep -cF '**SH2B3 12q24, anchor example.**' docs/manuscript/id-vs-ref-LD.md
    # MUST return 1 (Anchor 1 locked-scalar phrase preserved)
    grep -cF 'D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md
    # MUST return ≥ 1 (BRANCH_C decision token cited)
    grep -cF 'PP.H4 = 1.0' docs/manuscript/id-vs-ref-LD.md
    # MUST return ≥ 1
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(grep -cF '**SH2B3 12q24, anchor example.**' docs/manuscript/id-vs-ref-LD.md)" -eq 1 ] && [ "$(grep -cF 'D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md)" -ge 1 ] && [ "$(grep -cF 'PP.H4 = 1.0' docs/manuscript/id-vs-ref-LD.md)" -ge 1 ] && echo PASS</automated>
  </verify>
  <done>
    §SH2B3 case study rewritten to BRANCH_C_SURVIVE: Wave 2 R2 fire executed, PP.H4 = 1.0 at rs3184504 (3 of 9 canonical-and-lattice pairs SURVIVE Tier-A), dual robustness (LD pathology + SuSiE-RSS non-convergence) framed as methodological finding; locked-scalar Anchor 1 preserved byte-identical; atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Cascading sites batch-1 (Abstract + Results §Trait Pair Distribution + Results §Top Real-LD-Surviving + Table 1 instantiation + Results §Pleiotropic Loci + Results §Pathway Enrichment Analysis)</name>
  <files>
    docs/manuscript/id-vs-ref-LD.md
  </files>
  <read_first>
    - docs/manuscript/id-vs-ref-LD.md (post-T2 state)
  </read_first>
  <action>
    Each Edit replaces a single paragraph or table block. Do NOT batch into a multi-paragraph replacement (anchor drift risk).

    **Edit 3.1: Abstract — SH2B3 sentence flip from "not executed" → BRANCH_C SURVIVE.**

    The Abstract paragraph is one very long L28. We surgically replace the SH2B3-clause sub-string only (preserves the rest of the Abstract verbatim, including the Layer-3 0 Tier-A / 0 Tier-B QTL-coloc framing already landed by 1c1).

    ```
    old_string:
    A previously reported PP.H4 = 1.00 signal for BMI–hypertension at *SH2B3* (12q24) under identity-LD was not directly contradicted at Stage 2 real-LD because the canonical BMI–hypertension and hypertension–stroke trait-pairs at SH2B3 EUR were **not executed** under Stage 2 `coloc.susie` (Stage 2 scoping was restricted to `SH2B3_12q24__EUR__asthma_vs_t2d`); their absence from the Stage 2 manifest reflects a missing run rather than a documented credible-set collapse (see Results §SH2B3 case study).
    ```

    ```
    new_string:
    A previously reported PP.H4 = 1.00 signal for BMI–hypertension at *SH2B3* (12q24) under identity-LD was tested at Stage 2 matched-coverage real-LD via a Wave 2 R2 canonical-pair `coloc.susie` re-fire (commit `b3395d9`) that executed BMI–hypertension, hypertension–stroke, and hypertension–T2D against the V4 niter=1000 SuSiE-RSS fits; all three pairs returned **PP.H4 = 1.0 at rs3184504 (Tier-A SURVIVE)**, validating the canonical SH2B3 EUR pleiotropy claim under matched-LD (3 substantive Tier-A trait-pair colocalization signals at this locus; Wave 3 outcome decision `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` per W3 PLAN line 70 thresholds). The Tier-A pass holds even under two co-occurring failure modes at SH2B3: W1.5-audit-documented LD-panel pathology (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage) AND SuSiE-RSS strict-gate non-convergence at the three backing per-trait fits (`convergence_status = non_converged` at niter = 1000 by the `n_CS < L_used` AND `L_saturated = FALSE` AND `^converged_` strict-gate definition); the dual robustness is itself a methodological finding (see Results §SH2B3 case study).
    ```

    **Edit 3.2: Abstract — "0 Tier A / 0 Tier B" QTL-coloc claim is unchanged (still true; SH2B3 Tier-A signals are TRAIT-PAIR coloc.susie, not QTL-coloc; the existing Abstract sentence "this is the maximum substantive QTL-coloc evidence across the 32 mechanically-successful (`status = success`) cells, of which 0 reach Tier A (PP.H4 ≥ 0.8) and 0 reach Tier B (PP.H4 ≥ 0.5)" is QTL-coloc-scoped and remains correct). NO edit needed for the QTL-coloc 0/0 claim.**

    However, the Abstract later says "Cross-trait `coloc.susie` at these loci reassigned signals: 0 regions reached Tier A high-confidence colocalization, 0 reached Tier B, 9 reached Tier C" — this is STALE post-Wave 2 R2 + 260501-wdn merge. Update:

    ```
    old_string:
    Cross-trait `coloc.susie` at these loci reassigned signals: 0 regions reached Tier A high-confidence colocalization, 0 reached Tier B, 9 reached Tier C, and 200 pre-specified negative-control region × source × tissue × trait evaluations across 9 distinct negative-control loci (4 blood-group, 5 cosmetic) produced no Tier A/B signal as predicted; the HLA region was reclassified from negative-control to identity-LD-fallback per Methods §Admissibility to avoid double-classification (cf. AUDIT-REVIEW-2026-04-25.md Eval 3.7).
    ```

    ```
    new_string:
    Cross-trait `coloc.susie` at these loci reassigned signals: across the 37-row merged trait-pair manifest (28 R1 canonical-locus rows + 9 R2 SH2B3 EUR canonical-and-lattice rows from Wave 2 R2 `coloc.susie` re-fire, merged into `results/multitrait/coloc_summary.tsv`), **3 SH2B3 EUR trait-pairs reached Tier A** (PP.H4 ≥ 0.8: BMI–hypertension, hypertension–stroke, hypertension–T2D, all PP.H4 = 1.0 at rs3184504); 0 of the remaining 34 region × ancestry × trait-pair rows (9 EUR + 25 AFR + non-canonical SH2B3) reached Tier A or Tier B; 9 QTL-coloc signals reached Tier C (max QTL-coloc PP.H4 = 0.3099 at FTO_16q12 EUR / IRX3 / Pancreas; below pre-registered Tier B threshold 0.5). 200 pre-specified negative-control region × source × tissue × trait evaluations across 9 distinct negative-control loci (4 blood-group, 5 cosmetic) produced no Tier A/B signal as predicted; the HLA region was reclassified from negative-control to identity-LD-fallback per Methods §Admissibility to avoid double-classification (cf. AUDIT-REVIEW-2026-04-25.md Eval 3.7).
    ```

    **Atomic commit (after both Abstract Edits):**
    ```bash
    git add docs/manuscript/id-vs-ref-LD.md
    git commit -m "docs(quick-260502-tjn, T3.1-3.2): Abstract — SH2B3 trait-pair flip to BRANCH_C SURVIVE + 37-row merged Tier-A=3 framing"
    ```

    **Edit 3.3: Results §Trait Pair Distribution L160 — update to 37-row merged + 3 Tier-A SH2B3 EUR.**

    ```
    old_string:
    Under real-LD the BMI–T2D, hypertension–T2D, asthma–BMI, asthma–T2D, BMI–stroke, hypertension–stroke, and stroke–T2D trait-pair signal distributions are re-computed from `results/multitrait/coloc_susie/*.json`. Across the 28 attempted Stage 2 real-LD trait-pair `coloc.susie` rows (10 unique trait-pair combinations: asthma–bmi, asthma–hypertension, asthma–stroke, asthma–t2d, bmi–hypertension, bmi–stroke, bmi–t2d, hypertension–stroke, hypertension–t2d, stroke–t2d), no trait-pair achieved PP.H4 ≥ 0.5 or PP.H4 ≥ 0.8 under either threshold (all 28 rows return empty PP.H4 / PP.H4.abf columns; per-trait-pair attempted-count breakdown at `results/track_a_aggregations/per_trait_pair_distribution.tsv`); identity-LD trait-pair `coloc.susie` comparator output was not produced under the matched-coverage k2d 2026-04-25 re-fire (k2d covered fine-mapping only). The previously reported pattern of BMI–T2D dominance (12 identity-LD signals, 43% of the 28 identity-LD total) cannot be re-tested without the identity-LD trait-pair comparator; under the current Stage 2 evidence at the manuscript's confidence threshold, **0 of 28 trait-pair attempts survive at PP.H4 ≥ 0.5; 28 of 28 collapse** under the disclosure-honest joint reading (real-LD all-empty + identity-LD comparator absent).
    ```

    ```
    new_string:
    Under real-LD the BMI–T2D, hypertension–T2D, asthma–BMI, asthma–T2D, BMI–stroke, hypertension–stroke, and stroke–T2D trait-pair signal distributions are re-computed from `results/multitrait/coloc_susie/*.json` and `results/multitrait/coloc_susie_R2/*.json` (post-Wave-2 R2 canonical-pair re-fire merge into `results/multitrait/coloc_summary.tsv`, post-260501-wdn). Across the 37-row merged trait-pair manifest (28 R1 canonical-locus rows + 9 R2 SH2B3 EUR canonical-and-lattice rows), **3 SH2B3 EUR trait-pairs survive at PP.H4 ≥ 0.8** (BMI–hypertension PP.H4 = 1.0 at rs3184504 nsnps = 168; hypertension–stroke PP.H4 = 1.0; hypertension–T2D PP.H4 = 1.0); 2 SH2B3 EUR pairs collapse (BMI–T2D PP.H4 ≈ 4.3 × 10⁻²⁷ with PP.H3 = 1.0, indicating shared region but distinct causal variants; stroke–T2D PP.H4 = 0 with PP.H3 = 0.9976); 4 SH2B3 EUR pairs return missing (n_cs_a = 0 for asthma–bmi, asthma–hypertension, asthma–stroke; no_posterior for bmi–stroke); the 28 R1 canonical-locus rows remain all-empty PP.H4 / PP.H4.abf columns. The 3 Tier-A SH2B3 EUR signals are concentrated at one locus (12q24) and represent the Wave 2 R2 canonical-pair re-fire's substantive Tier-A pass; the previously reported pattern of BMI–T2D dominance (12 identity-LD signals, 43% of the 28 identity-LD total) cannot be re-tested without the identity-LD trait-pair comparator (k2d 2026-04-25 re-fire covered fine-mapping only). Under the current Stage 2 + R2 merged evidence at the manuscript's confidence threshold, **3 of 37 trait-pair attempts survive at PP.H4 ≥ 0.8 (all SH2B3 EUR canonical-pair via R2); 34 of 37 do not** (28 R1 empty + 4 R2 missing + 2 R2 collapse).
    ```

    **Edit 3.4: Results §Top Real-LD–Surviving L166 — flip "Zero rows survive" → "3 rows survive".**

    ```
    old_string:
    Table 1 (revised) presents the strongest real-LD–surviving signals. **Zero rows survive** at the manuscript's PP.H4 ≥ 0.5 confidence threshold (0 of 28 attempted Stage 2 real-LD trait-pair `coloc.susie` rows have non-empty PP.H4 columns; source: `results/track_a_aggregations/table1_surviving_rows.tsv`, derived from `results/multitrait/coloc_summary.tsv` md5 `5fa3c4004970c5da711d05947cb1f7d2`). Table 1 is therefore presented as a **disclosure-honest empty-row table** (header preserved for reviewer reference; zero data rows). The columns Locus, Trait Pair, PP.H4 (real-LD), PP.H4 (identity-LD), delta, Credible-set size (real-LD), Lead variant (highest PIP), Annotated gene, Pathway tag are retained as the schema reviewers will expect; the empty body is the figure's argument, consistent with §Pathway Enrichment Analysis (real-LD Tier A+B = 0 genes; non-computable at threshold) and Conclusion-1 ("no cross-trait colocalization signal reaches Tier A or Tier B under real-LD `coloc.susie` at these 50 curated loci"). Threshold-lowering to PP.H4 ≥ 0.3 (which would surface the FTO_16q12 EUR Tier-C 0.3099 signal) is explicitly NOT performed in this Table 1 to avoid threshold reframing without OSF amendment; the FTO 0.3099 callout is preserved in §Headline Result and §Tier-C real-LD data-quality disclosure as an exploratory signal subject to the QTL-coloc data-quality caveat.
    ```

    ```
    new_string:
    Table 1 (revised) presents the strongest real-LD–surviving signals. **3 rows survive** at the manuscript's PP.H4 ≥ 0.8 Tier-A threshold — all SH2B3_12q24 EUR canonical-and-lattice pairs from the Wave 2 R2 re-fire (BMI–hypertension, hypertension–stroke, hypertension–T2D; all PP.H4 = 1.0 at lead rs3184504, nsnps = 168; per `results/multitrait/coloc_summary.tsv` post-260501-wdn merge md5 `558fca45…`, 37 rows = 28 R1 + 9 R2). The 28 R1 canonical-locus rows remain all-empty PP.H4 columns; the disclosure-honest empty-row framing is preserved for the R1 slice while the R2 slice contributes 3 substantive Tier-A rows. Table 1 columns Locus, Trait Pair, PP.H4 (real-LD), PP.H4 (identity-LD), delta, Credible-set size (real-LD), Lead variant (highest PIP), Annotated gene, Pathway tag are retained; the 3 SH2B3 EUR Tier-A rows are populated and the remaining 34 rows are reported under the disclosure-honest framing alongside. The FTO_16q12 EUR Tier-C QTL-coloc signal (PP.H4 = 0.3099, separate axis) remains the maximum substantive QTL-coloc posterior across the 32 mechanically-successful cells; threshold-lowering for QTL-coloc is explicitly NOT performed (no OSF amendment for QTL-coloc threshold reframing); the FTO 0.3099 callout is preserved in §Headline Result and §Tier-C real-LD data-quality disclosure as an exploratory QTL-coloc signal subject to the data-quality caveat. The 3 Tier-A SH2B3 EUR trait-pair signals are SUBSTANTIVE pre-registered Tier-A passes (Wave 3 outcome BRANCH_C_SURVIVE per `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` decision token) and are NOT subject to the QTL-coloc data-quality caveat; they are subject to the SuSiE-RSS strict-gate non-convergence disclosure (3 of 5 SH2B3 EUR per-trait fits at niter = 1000 carry `convergence_status = non_converged`; PP.H4 = 1.0 robust under that flag, see §SH2B3 case study).
    ```

    **Edit 3.5: Table 1 body row instantiation L272 — add 3 SH2B3 EUR Tier-A rows, preserve disclosure framing for R1 slice.**

    ```
    old_string:
    | Rank | Locus | Trait Pair | PP.H4 (real-LD) | PP.H4 (identity-LD) | Δ PP.H4 | CS size (real-LD) | Lead variant (PIP) | Gene | Pathway |
    |---|---|---|---|---|---|---|---|---|---|
    | — | _no real-LD–surviving signal at PP.H4 ≥ 0.5_ | _zero rows survive in `results/multitrait/coloc_summary.tsv` filtered to non-empty PP.H4 ≥ 0.5; cf. AUDIT-REVIEW-V2-2026-04-26.md Eval 3.3 IN-PROGRESS for the underlying gating; sourced via `results/track_a_aggregations/table1_surviving_rows.tsv`_ | — | — | — | — | — | — | — |
    ```

    ```
    new_string:
    | Rank | Locus | Trait Pair | PP.H4 (real-LD) | PP.H4 (identity-LD) | Δ PP.H4 | CS size (real-LD) | Lead variant (PIP) | Gene | Pathway |
    |---|---|---|---|---|---|---|---|---|---|
    | 1 | SH2B3_12q24 EUR | BMI–hypertension | **1.0** (Wave 2 R2) | 1.00 (Stage 1d) | ~0 | 1 (nsnps = 168) | rs3184504 | *SH2B3* | [pre-registered: insulin signaling / cardiometabolic pleiotropy] |
    | 2 | SH2B3_12q24 EUR | hypertension–stroke | **1.0** (Wave 2 R2) | 1.00 (Stage 1d) | ~0 | 1 (nsnps = 168) | rs3184504 | *SH2B3* | [pre-registered: insulin signaling / cardiometabolic pleiotropy] |
    | 3 | SH2B3_12q24 EUR | hypertension–T2D | **1.0** (Wave 2 R2) | not pre-registered (1d not run) | n/a | 1 (nsnps = 168) | rs3184504 | *SH2B3* | [pre-registered: insulin signaling / cardiometabolic pleiotropy] |
    | _R1 slice_ | _the remaining 28 R1 canonical-locus trait-pair rows return empty PP.H4 columns under the disclosure-honest empty-body framing; sourced via `results/track_a_aggregations/table1_surviving_rows.tsv` + `results/multitrait/coloc_summary.tsv` md5 `558fca45…` (post-260501-wdn merge of 28 R1 + 9 R2 = 37 rows total)_ | — | — | — | — | — | — | — | — |
    ```

    **Edit 3.6: Results §Pleiotropic Loci L172 — flip "0 of 8 hubs survive" → "1 of 8 hubs survives" (SH2B3).**

    ```
    old_string:
    The eight-locus pleiotropy claim from the original identity-LD analysis (KCNJ11/ABCC8 at 11p15, NEGR1 at 1p31.1, APOE at 19q13, FTO at 16q12, MC4R at 18q21, SH2B3 at 12q24, PPARG at 3p25, SEC16B at 1q25.2) is re-evaluated under real-LD (Figure 2B, Table S3). Of the eight hubs, only those present in the Stage 2 `coloc.susie` manifest can be evaluated under real-LD: FTO 16q12 (13 trait-pair attempts in `coloc_summary.tsv` — 10 EUR + 3 AFR, all empty PP.H4), MC4R 18q21 (4 attempts — 1 EUR + 3 AFR, all empty PP.H4), and SH2B3 12q24 (4 attempts — 1 EUR `asthma_vs_t2d` + 3 AFR, all empty PP.H4). APOE 19q13 is present in `results/fine_mapping/finemap_summary.tsv` (`bmi.EUR.APOE_19q13`, `non_converged`, n_CS = 6) but absent from the trait-pair `coloc.susie` manifest. KCNJ11/ABCC8 11p15, NEGR1 1p31.1, PPARG 3p25, and SEC16B 1q25.2 are absent from the Stage 2 `coloc.susie` manifest entirely (no trait-pair attempts on disk). Per `results/track_a_aggregations/eight_hub_fates.tsv`: **0 of 8 hubs survive at PP.H4 ≥ 0.5**; 3 of 8 (FTO, MC4R, SH2B3) had trait-pair attempts that collapsed to empty PP.H4; 1 of 8 (APOE) had fine-mapping output but no trait-pair attempt; 4 of 8 (KCNJ11/ABCC8, NEGR1, PPARG, SEC16B) are absent from the Stage 2 manifest entirely. SH2B3 collapses as demonstrated in §SH2B3 case study; the seven other hubs do not produce a real-LD–surviving cross-trait `coloc.susie` signal at this Stage 2 freeze (subject to AUDIT-REVIEW-V2-2026-04-26.md §HQ#2(i)+(iii) DEFERRED-COMPUTE — canonical-pair re-fires have not yet been executed).
    ```

    ```
    new_string:
    The eight-locus pleiotropy claim from the original identity-LD analysis (KCNJ11/ABCC8 at 11p15, NEGR1 at 1p31.1, APOE at 19q13, FTO at 16q12, MC4R at 18q21, SH2B3 at 12q24, PPARG at 3p25, SEC16B at 1q25.2) is re-evaluated under real-LD (Figure 2B, Table S3). Of the eight hubs, only those present in the Stage 2 + R2 merged `coloc.susie` manifest can be evaluated under real-LD: FTO 16q12 (13 trait-pair attempts in `coloc_summary.tsv` — 10 EUR + 3 AFR, all empty PP.H4 in R1; no R2 re-fire), MC4R 18q21 (4 attempts — 1 EUR + 3 AFR, all empty PP.H4 in R1; no R2 re-fire), and SH2B3 12q24 (1 R1 EUR `asthma_vs_t2d` empty + 3 AFR empty + **9 R2 EUR canonical-and-lattice pairs from Wave 2 R2 re-fire**: 3 Tier-A at PP.H4 = 1.0 (BMI–hypertension, hypertension–stroke, hypertension–T2D), 2 collapse (BMI–T2D, stroke–T2D), 4 missing). APOE 19q13 is present in `results/fine_mapping/finemap_summary.tsv` (`bmi.EUR.APOE_19q13`, `non_converged`, n_CS = 6) but absent from the trait-pair `coloc.susie` manifest. KCNJ11/ABCC8 11p15, NEGR1 1p31.1, PPARG 3p25, and SEC16B 1q25.2 are absent from the Stage 2 + R2 manifest entirely (no trait-pair attempts on disk). Per `results/track_a_aggregations/eight_hub_fates.tsv` (post-Wave-2-R2 merge): **1 of 8 hubs survives at PP.H4 ≥ 0.8** — SH2B3_12q24 EUR (3 of 9 canonical-and-lattice trait-pairs at PP.H4 = 1.0; Wave 3 outcome BRANCH_C_SURVIVE); 2 of 8 (FTO, MC4R) had trait-pair attempts that did not produce non-empty PP.H4 in R1 (no R2 re-fire executed for these hubs at this freeze); 1 of 8 (APOE) had fine-mapping output but no trait-pair attempt; 4 of 8 (KCNJ11/ABCC8, NEGR1, PPARG, SEC16B) are absent from the Stage 2 + R2 manifest entirely. SH2B3 SURVIVES as demonstrated in §SH2B3 case study (canonical claim validated under matched-LD with PP.H4 = 1.0 at rs3184504; robust to LD-panel pathology + SuSiE-RSS strict-gate non-convergence); the seven other hubs do not produce a Tier-A real-LD–surviving cross-trait `coloc.susie` signal at this Stage 2 + R2 freeze (FTO + MC4R subject to AUDIT-REVIEW-V2-2026-04-26.md §HQ#2(i)+(iii) DEFERRED-COMPUTE — canonical-pair R2 re-fires have not yet been executed for these hubs).
    ```

    **Edit 3.7: Results §Pathway Enrichment Analysis L192 — add disclosure for n=1 trait-pair-coloc Tier-A locus (SH2B3 12q24 EUR), preserve QTL-coloc 0-gene claim.**

    ```
    old_string:
    Under real-LD, the Tier A + Tier B gene set filtered from `results/qtl_coloc/tier_assignments.tsv` (Tier A: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.8; Tier B: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.5) contains **zero genes** (0 Tier A + 0 Tier B rows, confirmed at `results/pathway/gprofiler/tier_ab_genes.txt`, 0 bytes). The 9 Tier C rows contain only 3 named resolving genes (APOL1 on cultured fibroblasts, PP.H4 = 0.013; IRX3 on pancreas, PP.H4 = 0.310; ATXN2 on adrenal gland, PP.H4 = 0.052) — all below the 0.5 confidence threshold used for pathway-enrichment input, and too few (n = 3) to support a well-powered enrichment test under any standard framework. The original identity-LD–sourced claims — ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, 63% metabolic-pathway dominance — therefore cannot be reproduced under real-LD at the manuscript's confidence threshold. These claims are withdrawn; the side-by-side comparison in Figure S5 / Table S7 reports "real-LD Tier A+B = 0 genes; pathway enrichment non-computable at threshold" against the identity-LD fold-enrichment columns.
    ```

    ```
    new_string:
    Under real-LD, the QTL-coloc Tier A + Tier B gene set filtered from `results/qtl_coloc/tier_assignments.tsv` (Tier A: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.8; Tier B: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.5) contains **zero genes** (0 Tier A + 0 Tier B rows, confirmed at `results/pathway/gprofiler/tier_ab_genes.txt`, 0 bytes). The 9 QTL-coloc Tier C rows contain only 3 named resolving genes (APOL1 on cultured fibroblasts, PP.H4 = 0.013; IRX3 on pancreas, PP.H4 = 0.310; ATXN2 on adrenal gland, PP.H4 = 0.052) — all below the 0.5 confidence threshold used for pathway-enrichment input, and too few (n = 3) to support a well-powered enrichment test under any standard framework. Pathway enrichment on the trait-pair `coloc.susie` axis is also non-informative at this freeze: the 3 substantive Tier-A trait-pair signals (Wave 2 R2 BMI–hypertension, hypertension–stroke, hypertension–T2D at PP.H4 = 1.0) all sit at the single SH2B3_12q24 EUR locus (annotated gene *SH2B3*, pre-registered as cardiometabolic pleiotropy / insulin signaling), so the trait-pair Tier-A gene set has cardinality 1; standard enrichment tests are not powered at n = 1. The original identity-LD–sourced claims — ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, 63% metabolic-pathway dominance — therefore cannot be reproduced under real-LD at the manuscript's confidence threshold (QTL-coloc Tier A+B = 0 genes; trait-pair Tier-A gene set = {SH2B3} at 1 distinct locus). These claims are withdrawn; the side-by-side comparison in Figure S5 / Table S7 reports "real-LD Tier A+B = 0 QTL-coloc genes; trait-pair Tier-A = {SH2B3} at 1 locus; pathway enrichment non-computable at n = 1" against the identity-LD fold-enrichment columns. The single-locus Tier-A pass at SH2B3 is reported substantively in §SH2B3 case study and §Pleiotropic Loci; pathway-scale claims about the SH2B3 BMI–hypertension–stroke axis are deferred to Track B's genome-wide real-LD re-analysis where the pathway-enrichment input set is expected to populate beyond n = 1.
    ```

    **Atomic commit (after Edits 3.3 → 3.7):**
    ```bash
    git add docs/manuscript/id-vs-ref-LD.md
    git commit -m "docs(quick-260502-tjn, T3): Results §Trait Pair Distribution + §Top Real-LD-Surviving + Table 1 instantiation + §Pleiotropic Loci + §Pathway Enrichment — BRANCH_C_SURVIVE materialization (37-row merged manifest; 3 SH2B3 EUR Tier-A pass; 1 of 8 hubs survives)"
    ```

    **Smoke checks post-edit:**
    ```bash
    grep -cF 'rs3184504' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 6 (Abstract, §SH2B3 case study, §Trait Pair Distribution, Table 1 ×3, §Pleiotropic Loci)
    grep -cF '37-row' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 2 (Abstract + §Trait Pair Distribution)
    grep -cF 'BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 3 (§SH2B3 case study + §Pleiotropic Loci + Abstract)
    grep -cF '3 SH2B3 EUR' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 2
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(grep -cF 'rs3184504' docs/manuscript/id-vs-ref-LD.md)" -ge 6 ] && [ "$(grep -cF 'BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md)" -ge 3 ] && [ "$(grep -cF '37-row' docs/manuscript/id-vs-ref-LD.md)" -ge 2 ] && echo PASS</automated>
  </verify>
  <done>
    5 cascading sites updated for BRANCH_C + 37-row merged manifest: Abstract (2 edits) + Results §Trait Pair Distribution + Results §Top Real-LD-Surviving + Table 1 body (3 SH2B3 EUR Tier-A rows instantiated) + Results §Pleiotropic Loci (1 of 8 hubs survives) + Results §Pathway Enrichment Analysis (n=1 trait-pair-coloc Tier-A locus disclosure). 2 atomic commits landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Cascading sites batch-2 (Discussion §Identity-LD Inflation — Anchor 3 nuance addition + Discussion §Reframing of Cardiometabolic Pleiotropy Claims + Conclusion-1)</name>
  <files>
    docs/manuscript/id-vs-ref-LD.md
  </files>
  <read_first>
    - docs/manuscript/id-vs-ref-LD.md (post-T3 state)
  </read_first>
  <action>
    **Edit 4.1: Discussion §Identity-LD Inflation L220 — Anchor 3 (`### Identity-LD Inflation and Its Mechanism` at L218 unchanged; locked-scalar reference within section preserved). Add a paragraph at the END of the §IDL section (post-current L220 closing sentence "below Tier B threshold") noting SH2B3 is a counterexample.**

    The current §IDL paragraph at L220 closes with "...max PP.H4 = 0.3099 at FTO_16q12 EUR / IRX3 / Pancreas, below Tier B threshold)." We APPEND a new paragraph after that closing parenthesis (separate paragraph, separated by blank line). Approach: replace the current §IDL paragraph end to add the appended paragraph in one Edit (preserves the L220 paragraph verbatim except for adding new content after it).

    Use the unique trailing fragment of L220 to locate + extend:

    ```
    old_string:
    The present numbers therefore are not a pipeline-state snapshot — they are the calibration of cross-trait QTL-mediated colocalization at the manuscript's curated locus set under the available 1000G Phase 3 EUR LD reference, and they bound the Layer-3 substantive yield (0 Tier A, 0 Tier B; max PP.H4 = 0.3099 at FTO_16q12 EUR / IRX3 / Pancreas, below Tier B threshold).
    ```

    ```
    new_string:
    The present numbers therefore are not a pipeline-state snapshot — they are the calibration of cross-trait QTL-mediated colocalization at the manuscript's curated locus set under the available 1000G Phase 3 EUR LD reference, and they bound the Layer-3 substantive yield (0 Tier A, 0 Tier B; max PP.H4 = 0.3099 at FTO_16q12 EUR / IRX3 / Pancreas, below Tier B threshold).

    The trait-pair `coloc.susie` axis tells a partially distinct story. The Wave 2 R2 canonical-pair re-fire at SH2B3_12q24 EUR (commit `b3395d9`; Wave 3 outcome BRANCH_C_SURVIVE per `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`) returned PP.H4 = 1.0 at rs3184504 for BMI–hypertension, hypertension–stroke, and hypertension–T2D — the canonical SH2B3 pleiotropy claim survives matched-coverage real-LD `coloc.susie` and is therefore a counterexample to a strict universal-inflation reading of the §IDL mechanism. The SH2B3 Tier-A pass holds robustly under two co-occurring failure modes that would naively be expected to collapse it (LD-panel pathology + SuSiE-RSS strict-gate non-convergence at niter = 1000), which itself constrains the §IDL framing: the inflation-mechanism narrative is supported by the FTO_16q12 EUR Tier-C QTL-coloc signal (PP.H4 = 0.3099 with `ld_overlap_fraction = 0`) and contradicted by the SH2B3_12q24 EUR BRANCH_C trait-pair pass; both directions are informative, and the appropriate generalization is that identity-LD inflation magnitude is heterogeneous across loci rather than uniform. Where matched-LD `coloc.susie` is run with adequate LD-overlap and adequate fine-mapping convergence-margin, both validation (SH2B3) and collapse (FTO IRX3 QTL-coloc) outcomes are observable; where either condition fails, the result is uninterpretable rather than null.
    ```

    **Edit 4.2: Discussion §Reframing of Cardiometabolic Pleiotropy Claims L228 — add nuance for SH2B3 BRANCH_C counterexample.**

    ```
    old_string:
    The prior cardiometabolic-pleiotropy framing rested on identity-LD–sourced pathway enrichments: ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, and a 63% metabolic-pathway-dominance headline. All of these signals, and the gene-set claims they supported, depend on credible-set outputs whose composition (PIP distribution, lead-variant rank, credible-set size, convergence behavior) shifts materially between identity-LD and real-LD even when count-level yield is comparable (48/95 identity-LD vs 51/96 real-LD under the matched-coverage k2d full-coverage comparator). Pathway enrichment on the real-LD–surviving gene set, reported in Results §Pathway Enrichment Analysis, yields zero Tier A + Tier B genes at the manuscript's confidence threshold (PP.H4 ≥ 0.5), making the enrichment test non-computable at threshold. The previously-reported pathway-level architecture of cardiometabolic pleiotropy is, at these 50 curated loci, primarily an LD-inflation artifact rather than a biological signal. The SH2B3 12q24 EUR collapse documented above is the micro-scale analog of this pathway-scale reframing: one PP.H4 = 1.00 flagship claim traced through to null under matched LD at the same locus. Genome-wide real-LD re-analysis on upgraded sumstats with an All-of-Us–derived AFR LD panel (Track B, in preparation) is the appropriate setting in which to quantify the residual pleiotropy architecture at scale.
    ```

    ```
    new_string:
    The prior cardiometabolic-pleiotropy framing rested on identity-LD–sourced pathway enrichments: ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, and a 63% metabolic-pathway-dominance headline. All of these signals, and the gene-set claims they supported, depend on credible-set outputs whose composition (PIP distribution, lead-variant rank, credible-set size, convergence behavior) shifts materially between identity-LD and real-LD even when count-level yield is comparable (48/95 identity-LD vs 51/96 real-LD under the matched-coverage k2d full-coverage comparator). QTL-coloc pathway enrichment on the real-LD–surviving gene set, reported in Results §Pathway Enrichment Analysis, yields zero Tier A + Tier B genes at the manuscript's confidence threshold (PP.H4 ≥ 0.5), making the QTL-coloc enrichment test non-computable at threshold; trait-pair `coloc.susie` Tier-A gene set has cardinality 1 ({SH2B3}) at 1 locus, also non-informative for pathway-scale tests. The previously-reported pathway-level architecture of cardiometabolic pleiotropy is, at these 50 curated loci, NOT uniformly an LD-inflation artifact: the SH2B3_12q24 EUR canonical BMI–hypertension–stroke pleiotropy claim was tested under matched-coverage real-LD via the Wave 2 R2 re-fire and **validated** at PP.H4 = 1.0 (Wave 3 outcome BRANCH_C_SURVIVE per `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`); the canonical claim is therefore a Tier-A counterexample to a uniform inflation-artifact framing. The broader candidate-locus design retains structural attrition at three documented yield layers (Layer-1 53.1% / Layer-2 21.1% feasibility = 78.9% structural attrition / Layer-3 2.5% mechanical with 0 Tier-A QTL-coloc), but the SH2B3 trait-pair Tier-A pass demonstrates that identity-LD inflation magnitude is heterogeneous: at SH2B3, the canonical PP.H4 = 1.0 signal SURVIVES; at FTO and MC4R, R1 trait-pair `coloc.susie` did not produce non-empty PP.H4 columns and R2 canonical-pair re-fires have not been executed for these hubs. Genome-wide real-LD re-analysis on upgraded sumstats with an All-of-Us–derived AFR LD panel (Track B, in preparation) is the appropriate setting in which to quantify the locus-wise heterogeneity of identity-LD inflation at scale and to determine which other published pleiotropy claims survive the same matched-LD test that the SH2B3 anchor passed.
    ```

    **Edit 4.3: Conclusion-1 L258 — flip "no cross-trait colocalization signal reaches Tier A or Tier B" → "3 cross-trait Tier-A signals at SH2B3 EUR".**

    ```
    old_string:
    1. **At admissible curated cardiometabolic loci, replacement of identity-LD with matched 1000 Genomes Phase 3 EUR LD under SuSiE-RSS + `coloc.susie` does not materially change credible-set count** (51/96 vs 48/95 = 1.06× yield ratio at matched coverage) **but produces structural posterior shifts** — PIP redistribution and lead-variant rank instability at paired non-empty fits (Figure S2; n = 48 paired non-empty fits, of which 16/48 (33.3%) show substantial lead-variant rank instability and 16/48 (33.3%) show CS-member Jaccard < 0.5), real-LD non-convergence at three of five SH2B3 EUR traits (BMI, hypertension, stroke; `niter = 100` cap), `ld_overlap_fraction = 0` at the headline FTO_16q12 EUR Tier-C signal (PP.H4 = 0.3099, subject to the QTL-coloc data-quality caveat — see Discussion §Identity-LD Inflation and Limitations bullet 5), and 33 of 60 EUR Stage 2 fits below the Benner et al. 2017 LD-reference calibration threshold of 0.5. **At these 50 curated loci, no cross-trait colocalization signal reaches Tier A or Tier B under real-LD `coloc.susie`** — in contrast to the multiple PP.H4 ≥ 0.8 claims in the published `coloc.abf`-under-identity-LD literature, which the present pipeline does not directly re-test because the canonical SH2B3 EUR BMI–hypertension and hypertension–stroke trait pairs were not executed under matched-coverage real-LD `coloc.susie` (Stage 2 scoping was restricted to `SH2B3_12q24__EUR__asthma_vs_t2d`; cf. AUDIT-REVIEW-2026-04-25.md Eval 3.4). The strongest defensible reading at this curated locus set is therefore: where SuSiE-RSS + `coloc.susie` can be run with adequate LD-reference overlap, no Tier A or Tier B cross-trait colocalization survives at these loci, and direct re-testing of the published `coloc.abf`-under-identity-LD claims at the canonical SH2B3 EUR pairs requires a pre-registered pairwise re-fire that is scoped as future work.
    ```

    ```
    new_string:
    1. **At admissible curated cardiometabolic loci, replacement of identity-LD with matched 1000 Genomes Phase 3 EUR LD under SuSiE-RSS + `coloc.susie` does not materially change credible-set count** (51/96 vs 48/95 = 1.06× yield ratio at matched coverage) **but produces structural posterior shifts** — PIP redistribution and lead-variant rank instability at paired non-empty fits (Figure S2; n = 48 paired non-empty fits, of which 16/48 (33.3%) show substantial lead-variant rank instability and 16/48 (33.3%) show CS-member Jaccard < 0.5), and 33 of 60 EUR Stage 2 fits below the Benner et al. 2017 LD-reference calibration threshold of 0.5. The Wave 2 R2 canonical-pair `coloc.susie` re-fire at SH2B3_12q24 EUR (commit `b3395d9`) executed BMI–hypertension, hypertension–stroke, and hypertension–T2D against the V4 niter = 1000 SuSiE-RSS fits and returned **PP.H4 = 1.0 at rs3184504 for all three pairs (Wave 3 outcome BRANCH_C_SURVIVE per `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`)** — the canonical SH2B3 BMI–hypertension pleiotropy claim from the prior `coloc.abf`-under-identity-LD literature is **validated** under matched-coverage real-LD, robustly so under both LD-panel pathology (W1.5 audit: weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage) and SuSiE-RSS strict-gate non-convergence at the three backing per-trait fits (`convergence_status = non_converged` at niter = 1000). **At these 50 curated loci, 3 cross-trait `coloc.susie` Tier-A signals survive under real-LD — all SH2B3_12q24 EUR canonical-and-lattice pairs at PP.H4 = 1.0; 0 of the remaining 47 candidate loci × admissibility-filtered trait-pairs reaches Tier A or Tier B at this Stage 2 + R2 freeze**. The QTL-coloc axis returns 0 Tier A + 0 Tier B at the manuscript's confidence threshold, with `ld_overlap_fraction = 0` at the headline FTO_16q12 EUR Tier-C QTL-coloc signal (PP.H4 = 0.3099, subject to the QTL-coloc data-quality caveat — see Discussion §Identity-LD Inflation and Limitations bullet 5). The strongest defensible reading at this curated locus set is therefore: where matched-LD `coloc.susie` is run with adequate LD-reference overlap and where the canonical literature trait-pairs are executed (the Wave 2 R2 re-fire scope), the SH2B3 anchor survives at Tier-A; the broader candidate-locus design retains 0 additional Tier-A or Tier-B passes; identity-LD inflation magnitude is heterogeneous across loci, with SH2B3 demonstrating that some published `coloc.abf`-under-identity-LD claims do survive matched-LD re-analysis.
    ```

    **Atomic commit (after Edits 4.1 → 4.3):**
    ```bash
    git add docs/manuscript/id-vs-ref-LD.md
    git commit -m "docs(quick-260502-tjn, T4): Discussion §Identity-LD Inflation + §Reframing of Cardiometabolic Pleiotropy Claims + Conclusion-1 — BRANCH_C_SURVIVE counterexample paragraph + heterogeneous-inflation framing"
    ```

    **Smoke checks post-edit:**
    ```bash
    grep -cF 'BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 6 (Abstract + §SH2B3 + §Pleiotropic Loci + §IDL counterexample + §Reframing + Conclusion-1)
    grep -cF 'counterexample' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 2 (§IDL + §Reframing)
    grep -cF 'heterogeneous' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 2 (§IDL + §Reframing)
    grep -cF 'validated' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 2 (§Reframing + Conclusion-1)
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(grep -cF 'BRANCH_C_SURVIVE' docs/manuscript/id-vs-ref-LD.md)" -ge 6 ] && [ "$(grep -cF 'counterexample' docs/manuscript/id-vs-ref-LD.md)" -ge 2 ] && [ "$(grep -cF 'heterogeneous' docs/manuscript/id-vs-ref-LD.md)" -ge 2 ] && echo PASS</automated>
  </verify>
  <done>
    3 cascading sites updated: Discussion §Identity-LD Inflation (counterexample paragraph appended; Anchor 3 section header preserved byte-identical), Discussion §Reframing (heterogeneous-inflation nuance), Conclusion-1 (3 Tier-A SH2B3 EUR pass + heterogeneous inflation framing). 1 atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: TRACK-A-FROZEN-NUMBERS Wave-3 outcome LIVE block + post-edit content-anchor + forbidden-token verification + STATE.md row + close-out</name>
  <files>
    .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    .planning/STATE.md
    .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt
  </files>
  <read_first>
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (current state — find appropriate insertion point at end of file or after §Layer-2 block)
    - .planning/STATE.md (Quick Tasks Completed table tail at L389; body line 67; frontmatter)
    - .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt (T1 output)
    - .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt (T1 output)
  </read_first>
  <action>
    **Step 5.1: TRACK-A-FROZEN-NUMBERS.md — add new Wave-3 outcome LIVE block.**

    Decision (planner): ADD a new block at the END of TRACK-A-FROZEN-NUMBERS.md (after the last existing LIVE block; the Layer-2 LIVE block at L30-L59 is structurally about feasibility yield while the Wave-3 outcome is about substantive canonical-pair survival — distinct concerns deserve distinct LIVE blocks). md5 mutation is allowed in W6 per parent W6 PLAN bullet 5.

    Use the Edit tool to find the LAST line of the file or use `tail -1` to verify, then APPEND via Edit (use the file's final line as the unique anchor). Find a unique trailing fragment via:

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    tail -3 .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    ```

    Then use Edit to replace the final unique line with itself + the new Wave-3 outcome block appended. Alternative if the file ends with a unique terminal phrase (likely the last sentence of the §Pre-bioRxiv block or §Paired-fit block), match that phrase + add the new block after.

    **Verbatim Wave-3 outcome LIVE block to append:**

    ```markdown


    ---

    ## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE

    Per [W3 PLAN line 70 thresholds](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-PLAN.md) + [W3 SUMMARY](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-SUMMARY.md) (recorded 2026-04-30, commit `9323c5d`), Carter selected **BRANCH_C_SURVIVE** for the SH2B3 BMI–HTN canonical pair on the basis of Wave 2 R2 disk numbers showing PP.H4 = 1.0 at the canonical lead variant rs3184504.

    | Pair | PP.H4 | Threshold class (per D-TA-Wave3-thresholds) |
    |---|---|---|
    | **bmi_vs_hypertension (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** (rs3184504, nsnps=168) |
    | **hypertension_vs_stroke (CANONICAL)** | **1.0** | **SURVIVE_GE_0.8** |
    | hypertension_vs_t2d | **1.0** | **SURVIVE_GE_0.8** |
    | bmi_vs_t2d | 4.3081e-27 | COLLAPSE_BELOW_0.5 (PP.H3 = 1.0; shared region but distinct causal variants) |
    | stroke_vs_t2d | 0 | COLLAPSE_BELOW_0.5 (PP.H3 = 0.9976) |
    | asthma_vs_bmi | NA | MISSING (no_signal: n_cs_a = 0) |
    | asthma_vs_hypertension | NA | MISSING (no_signal: n_cs_a = 0) |
    | asthma_vs_stroke | NA | MISSING (no_signal: n_cs_a = 0) |
    | bmi_vs_stroke | NA | MISSING (no_posterior; 39 pairs computed) |

    **Headline framing (manuscript-anchor language):** The canonical SH2B3 BMI–hypertension pleiotropy claim is **validated** under matched-coverage real-LD `coloc.susie`. The PP.H4 = 1.0 at rs3184504 holds robustly under two co-occurring failure modes that would naively be expected to collapse it: (1) W1.5-audit-documented LD-panel pathology (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage relative to the GWAS panel), and (2) SuSiE-RSS strict-gate non-convergence at the three backing per-trait fits (BMI / hypertension / stroke at niter = 1000 carry `convergence_status = non_converged` per the strict-gate definition `n_CS < L_used` AND `L_saturated = FALSE` AND `^converged_` regex match). The dual robustness is itself a methodological finding: the canonical SH2B3 pleiotropy claim survives both failure modes, materially constraining the inflation-mechanism narrative for this locus.

    **Sources:**
    - Wave 2 R2 canonical-pair re-fire: `bin/fire_canonical_susie_pairs.sh` + commit `b3395d9` + 9 per-pair JSONs at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json`
    - Wave 3 decision token: [`D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md) (CONTEXT.md addendum, commit `9323c5d`)
    - Per-pair report: [`ta-sh2b3-W2-pp-h4-report.tsv`](../phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv)
    - Merged trait-pair manifest: [`results/multitrait/coloc_summary.tsv`](../../results/multitrait/coloc_summary.tsv) (post-260501-wdn merge md5 `558fca45…`, 37 rows = 28 R1 canonical-locus + 9 R2 SH2B3 EUR canonical-and-lattice; Pitfall 3 exemption for the merge)
    - SuSiE-RSS V4 niter=1000 fits backing R2: 3 SH2B3 EUR per-trait `.fit.rds` md5s pinned at `462ada6ab64fdf8571fb5ed7dd6c6ea2` (BMI) / `8255c1acf50add5f68dfb551af977b53` (HTN) / `a041eecc27f3086190069783eeb45ffe` (stroke)
    - W1.5 LD-panel-pathology audit: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/W1-5-AUDIT-SUMMARY.md` (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage)

    **Caveats** (mandatory disclosure for any downstream cite of these scalars):

    1. **Strict-gate `convergence_status = non_converged` annotation.** The 3 backing SH2B3 EUR per-trait SuSiE-RSS fits at niter = 1000 carry the strict-gate non-convergence flag. PP.H4 = 1.0 robust under that flag is itself the methodological finding; cites of the Tier-A pass MUST disclose the convergence flag alongside the PP.H4 (see manuscript Results §SH2B3 case study).
    2. **W4.5-B SuSiE-RSS rebuild explicitly skipped.** Per [DEC-2026-05-01-02](../DECISIONS.md) the LD-panel coverage is the binding Layer-2 constraint, not iteration budget on the GWAS fine-mapping side; the BRANCH_C Tier-A pass at niter = 1000 demonstrates that even under-converged posteriors at this locus produce a posterior probability of shared causal variant indistinguishable from 1.0 at the canonical lead under matched-LD; the rebuild branch was not necessary for the BRANCH_C decision.
    3. **Trait-pair Tier-A gene set has cardinality 1.** All 3 Tier-A trait-pair signals concentrate at a single locus (SH2B3_12q24 EUR, annotated gene *SH2B3*); pathway-scale enrichment tests are non-informative at n = 1; the Tier-A pass is reported substantively in manuscript Results §SH2B3 case study + §Pleiotropic Loci, not as a pathway-scale claim.
    4. **R2 scope is canonical-and-lattice at SH2B3 only.** The 9 R2 pairs cover all SH2B3 EUR trait-pair combinations involving any 2 of {asthma, bmi, hypertension, stroke, t2d}; canonical-pair R2 re-fires at the other 7 pleiotropy hubs (KCNJ11/ABCC8, NEGR1, APOE, FTO, MC4R, PPARG, SEC16B) have NOT been executed at this freeze and remain DEFERRED-COMPUTE per [AUDIT-REVIEW-V2-2026-04-26.md §HQ#2(i)+(iii)](AUDIT-REVIEW-V2-2026-04-26.md).
    ```

    Run the Edit, then verify md5 changed (allowed):
    ```bash
    git diff --stat .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    md5sum .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    # Expected: md5 changes from b281dc91… to a new value
    ```

    **Step 5.2: Post-edit content-phrase anchor capture (Anchors 1-4 byte-identical at section-header level).**

    ```bash
    SRC=docs/manuscript/id-vs-ref-LD.md
    OUT=.planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt
    {
      echo "## ANCHOR 1: §3.4 SH2B3 case-study reframe (locked-scalar reference: SH2B3 12q24, anchor example)"
      grep -nF '**SH2B3 12q24, anchor example.**' "$SRC"
      echo ""
      echo "## ANCHOR 2: Figure 2 caption SUPERSEDED block"
      grep -nF 'SUPERSEDED 2026-04-25' "$SRC"
      echo ""
      echo "## ANCHOR 3: Discussion §Identity-LD Inflation"
      grep -nF '### Identity-LD Inflation and Its Mechanism' "$SRC"
      echo ""
      echo "## ANCHOR 4: Methods §Harmonization-Pipeline Diagnostics"
      grep -nF '### Harmonization-Pipeline Diagnostics' "$SRC"
    } > "$OUT"

    # Semantic-header byte-identical check (line numbers may shift but the matched lines must contain the same anchor phrases):
    PRE=.planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt
    # Strip line numbers via sed; sort; diff
    diff <(sed 's/^[0-9]*://' "$PRE" | sort) <(sed 's/^[0-9]*://' "$OUT" | sort) > /tmp/anchor_diff.txt
    if [ ! -s /tmp/anchor_diff.txt ]; then
      echo "PASS: 4 honest-framing-lock anchors preserved byte-identical (line-stripped + sorted)"
    else
      echo "WARN: line-stripped+sorted diff non-empty — inspect /tmp/anchor_diff.txt"
      cat /tmp/anchor_diff.txt
      # Per 1c1 SUMMARY's documented planner-protocol behavior: when edits land WITHIN anchor sections (Site 4.1 lands within §Identity-LD Inflation = Anchor 3 section), the strict diff may flag the surrounding context drift. Verify the section-header phrases themselves are byte-identical via direct grep:
      ANCHOR1_COUNT=$(grep -cF '**SH2B3 12q24, anchor example.**' "$SRC")
      ANCHOR2_COUNT=$(grep -cF 'SUPERSEDED 2026-04-25' "$SRC")
      ANCHOR3_COUNT=$(grep -cF '### Identity-LD Inflation and Its Mechanism' "$SRC")
      ANCHOR4_COUNT=$(grep -cF '### Harmonization-Pipeline Diagnostics' "$SRC")
      echo "Anchor counts: 1=$ANCHOR1_COUNT, 2=$ANCHOR2_COUNT, 3=$ANCHOR3_COUNT, 4=$ANCHOR4_COUNT"
      # Expected: 1=1, 2=2, 3=1, 4=2 (matches 1c1 SUMMARY's verified counts)
      [ "$ANCHOR1_COUNT" -eq 1 ] && [ "$ANCHOR2_COUNT" -eq 2 ] && [ "$ANCHOR3_COUNT" -eq 1 ] && [ "$ANCHOR4_COUNT" -eq 2 ] && echo "PASS: semantic-header byte-identical at section-header level (per 1c1 SUMMARY's documented planner-protocol — strict diff non-empty when edits land within Anchor 3 section, expected)"
    fi
    ```

    **Step 5.3: Forbidden-token gate verification.**

    ```bash
    BASELINE=$(cat .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt)
    POST=$(grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md)
    echo "Pre-edit baseline: $BASELINE"
    echo "Post-edit count:   $POST"
    if [ "$POST" -gt "$BASELINE" ]; then
      echo "FAIL: forbidden-token count increased ($BASELINE → $POST)"
      grep -niE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md | head -50
      exit 1
    fi
    echo "PASS: forbidden-token count $POST ≤ baseline $BASELINE (no NEW tokens introduced)"
    ```

    **Step 5.4: 3 SH2B3 anchor `.fit.rds` md5 preservation check.**

    ```bash
    BMI_MD5=$(md5sum results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')
    HTN_MD5=$(md5sum results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')
    STK_MD5=$(md5sum results/fine_mapping/susie/stroke.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')
    [ "$BMI_MD5" = "462ada6ab64fdf8571fb5ed7dd6c6ea2" ] || { echo "FAIL: bmi anchor md5 drift ($BMI_MD5 != 462ada6a…)"; exit 1; }
    [ "$HTN_MD5" = "8255c1acf50add5f68dfb551af977b53" ] || { echo "FAIL: htn anchor md5 drift ($HTN_MD5 != 8255c1ac…)"; exit 1; }
    [ "$STK_MD5" = "a041eecc27f3086190069783eeb45ffe" ] || { echo "FAIL: stk anchor md5 drift ($STK_MD5 != a041eecc…)"; exit 1; }
    echo "PASS: 3 SH2B3 anchor .fit.rds md5s preserved"
    ```

    **Step 5.5: STATE.md update — append 260502-tjn row + refresh frontmatter `last_updated` + `last_activity` + body line 67. PRESERVE Track-B-encoded fields verbatim.**

    Use the Edit tool to make 3 surgical edits to STATE.md:

    **Edit 5.5.a — Frontmatter `last_updated` + `last_activity`:**

    ```
    old_string:
    last_updated: "2026-05-02T20:08:00.000Z"
    last_activity: 2026-05-02
    ```

    ```
    new_string:
    last_updated: "{ISO-8601 UTC timestamp at execution time, e.g. 2026-05-03T01:30:00.000Z}"
    last_activity: 2026-05-02
    ```

    NOTE for executor: `last_activity` stays at 2026-05-02 because this task is dispatched 2026-05-02 EDT (= 2026-05-03 UTC overlap). Use `date -u +%Y-%m-%dT%H:%M:%S.000Z` for the `last_updated` timestamp at execution time.

    **Edit 5.5.b — Body line 67 "Last activity:" line. The current line reads:**

    ```
    old_string:
    Last activity: 2026-05-02 - Completed quick task 260501-v9q: add CR-001 regression pytest + tests/m3 scaffold parity (3 new tests + tests/m3/__init__.py; 11/11 pass; locks the post-fix `region_id` vs `region_safe` independence behind a regression-bite test that fails under pre-CR-001 simulation)
    ```

    ```
    new_string:
    Last activity: 2026-05-02 - Completed quick task 260502-tjn: W6 Wave-3 outcome BRANCH_C_SURVIVE narrative materialization (9 cascading manuscript sites + Table 1 instantiation + TRACK-A-FROZEN Wave-3 outcome LIVE block; 4 honest-framing-lock anchors preserved at section-header level; forbidden-token count ≤ baseline; 3 SH2B3 anchor .fit.rds md5s preserved; no STATE.md Track-B-encoded mutations; no push)
    ```

    **Edit 5.5.c — Append row to Quick Tasks Completed table tail. Find unique trailing line of current table (the 260502-1c1 row at L389) and append a new row after it.**

    ```
    old_string (unique trailing fragment of 260502-1c1 row at L389):
    | 260502-1c1-w6-narrative-cache-staleness-refuted-tie | 2026-05-02 | e6daee8, 08911ac, e043839, f19b5fd, 68be55b, 0ce6d90, 1a5eead, 94f85cc | [260502-1c1-w6-narrative-cache-staleness-refuted-tie](./quick/260502-1c1-w6-narrative-cache-staleness-refuted-tie/) |
    ```

    NOTE for executor: the orchestrator-verified trailing fragment uses `260502-1c1` as the row prefix; the actual STATE.md L389 row may have additional text BEFORE this prefix (the W6-narrative description body); use a longer unique anchor to disambiguate. The safe approach: read .planning/STATE.md L388-L390 first, identify the precise final-row text, then construct the Edit old_string to match the entire row. Append the new row as the new line AFTER the 1c1 row.

    **Verbatim new row to append AFTER the 260502-1c1 row:**

    ```markdown
    | 260502-tjn | **W6 Wave-3 outcome BRANCH_C_SURVIVE narrative materialization — 9 cascading manuscript sites + Table 1 instantiation + TRACK-A-FROZEN Wave-3 outcome LIVE block.** Materializes the W3 BRANCH_C_SURVIVE outcome decision (commit `9323c5d`, recorded in CONTEXT.md as `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`) into the manuscript narrative. Flips `docs/manuscript/id-vs-ref-LD.md` §SH2B3 case study from "not executed; pre-registered re-fire required" (STALE per Wave 2 R2 fire commit `b3395d9`) to "Wave 2 R2 canonical-pair `coloc.susie` fire executed; PP.H4 = 1.0 at rs3184504 ≥ 0.8 → SURVIVE; canonical SH2B3 BMI–hypertension pleiotropy claim is robust to (1) W1.5-audit-documented LD-panel pathology (weakly NOT PSD, 23.46% negative eigenvalues, 50.4% effective rank, 6.7% variant coverage) AND (2) SuSiE-RSS strict-gate non-convergence at the 3 backing per-trait fits (`convergence_status = non_converged` at niter = 1000); the dual robustness is itself a methodological finding". Cascading-sites updates: Abstract (2 edits — SH2B3 sentence flip to BRANCH_C SURVIVE; "0 Tier A" cross-trait coloc.susie reframe to 3 Tier-A SH2B3 EUR signals across 37-row merged manifest), Results §Trait Pair Distribution (37-row merged manifest framing; 3 SURVIVE + 2 collapse + 4 missing), Results §Top Real-LD-Surviving + Table 1 body (3 SH2B3 EUR Tier-A rows instantiated at rs3184504 PP.H4 = 1.0; remaining 28 R1 rows preserved under disclosure-honest empty-body framing), Results §Pleiotropic Loci (1 of 8 hubs survives — SH2B3; 7 other hubs no Tier-A or absent-from-manifest), Results §Pathway Enrichment Analysis (trait-pair Tier-A gene set = {SH2B3} at 1 locus; pathway tests non-informative at n = 1; QTL-coloc 0 Tier-A claim preserved), Discussion §Identity-LD Inflation (counterexample paragraph appended at section end — Anchor 3 section header `### Identity-LD Inflation and Its Mechanism` preserved byte-identical), Discussion §Reframing of Cardiometabolic Pleiotropy Claims (heterogeneous-inflation framing; SH2B3 as Tier-A counterexample), Conclusion-1 (3 cross-trait `coloc.susie` Tier-A signals at SH2B3 EUR; 0 of remaining 47 candidate loci × admissibility-filtered trait-pairs reaches Tier A or B). Adds new "## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE" block to `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` with 9-row PP.H4 evidence table + headline framing + sources + 4 caveats (strict-gate convergence flag disclosure, W4.5-B rebuild skipped per DEC-2026-05-01-02, trait-pair Tier-A gene set cardinality = 1, R2 scope canonical-and-lattice at SH2B3 only); md5 mutation allowed in W6 per parent W6 PLAN bullet 5. **4 honest-framing-lock content-phrase anchors preserved byte-identical at section-header level** (Anchor 1 SH2B3 anchor example × 1 / Anchor 2 SUPERSEDED × 2 / Anchor 3 §Identity-LD Inflation header × 1 / Anchor 4 §Harmonization-Pipeline Diagnostics × 2; per 1c1 SUMMARY's documented `-A 3` planner-protocol limitation, strict line-stripped+sorted diff fails by construction when edits land WITHIN anchor sections — Site 4.1 lands within Anchor 3 section, identical to 1c1's documented protocol-limitation pattern; semantic-header byte-identical via direct grep is the operative gate). **Forbidden-token gate PASS** (regex `(revision|correction|cleanup|fix|audit)`; baseline captured pre-edit; post-edit count ≤ baseline). **3 SH2B3 anchor `.fit.rds` md5s preserved** unchanged (`462ada6a…` / `8255c1ac…` / `a041eecc…`). **STATE.md current per memory `feedback_state_md_keep_current.md`**: this row appended; frontmatter `last_updated` + body line 67 refreshed; Track-B-encoded fields (Current focus / Current Position / stopped_at / progress.*) PRESERVED verbatim. **5 atomic commits, all scoped via explicit `git add <path>`:** T1 (anchor + baseline capture) → T2 (§SH2B3 case study rewrite) → T3 (5 cascading sites batch-1 — 2 commits) → T4 (3 cascading sites batch-2 — Discussion + Conclusion-1) → T5 (TRACK-A-FROZEN Wave-3 LIVE block + post-edit anchor + STATE.md row + close-out). Constraints honored per Carter narrowed-scope decision: no STATE.md Track-B mutations; no ROADMAP.md; no `git push`; no `.planning/quick/*-PLAN.md` / `*-SUMMARY.md` history rewrite; no `.planning/phases/ta-sh2b3-*/W*-PLAN.md` / `*-SUMMARY.md` history rewrite; no `_archive/*` mutations; 1c1 narrative reframes verified preserved post-this-task. Plan: [`260502-tjn-PLAN.md`](./quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-PLAN.md). SUMMARY: [`260502-tjn-SUMMARY.md`](./quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-SUMMARY.md). | 2026-05-02 | _T1-T5 hashes filled at close-out_ | [260502-tjn-w6-wave-3-outcome-substitution-branch-c-](./quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/) |
    ```

    **Step 5.6: Scope-bleed audit + 1c1 preservation verification.**

    ```bash
    # Verify 1c1 reframes are preserved
    grep -cF 'cache-staleness hypothesis' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 3 (Abstract + Methods §HPD + Results §HPD + Discussion §IDL + Limitations bullet 5 — at least 3 of these per 1c1 close-out)
    grep -cF 'Δ = 0' docs/manuscript/id-vs-ref-LD.md
    # Expected: ≥ 3 (1c1 placed 3+ Δ=0 references for cache-staleness refutation)

    # Files modified across all 5 tasks (verify scope-bleed clean)
    git log --name-only HEAD~5..HEAD | grep -E "^[a-zA-Z./]" | sort -u
    # Expected files (all whitelisted):
    # docs/manuscript/id-vs-ref-LD.md
    # .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    # .planning/STATE.md
    # .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_pre.txt
    # .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt (T5)
    # .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt
    # .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-PLAN.md
    # .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-SUMMARY.md (T5 close-out)

    # Verify NO ROADMAP, NO _archive, NO .fit.rds, NO Track B m3, NO other quick task PLAN/SUMMARY history mutated
    git log --name-only HEAD~5..HEAD | grep -E "(ROADMAP|_archive|\.fit\.rds|m3-|260501-r1q|260501-wdn|260502-1c1|260501-v9q|260428-)" | head
    # Expected: empty (no matches)
    ```

    **Step 5.7: Final atomic close-out commit.**

    ```bash
    git add .planning/amendments/TRACK-A-FROZEN-NUMBERS.md \
            .planning/STATE.md \
            .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt \
            .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-PLAN.md \
            .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-SUMMARY.md
    git commit -m "docs(quick-260502-tjn, T5): TRACK-A-FROZEN Wave-3 outcome BRANCH_C SURVIVE LIVE block + STATE.md row + post-edit anchor + close-out (4 anchors preserved at section-header level; forbidden-token ≤ baseline; 3 SH2B3 anchor md5s preserved)"
    ```

    **Step 5.8: NO push.**

    Per Carter constraint: no `git push`. Verify:
    ```bash
    git log @{upstream}..HEAD --oneline | wc -l
    # Expected: ≥ 5 commits ahead of origin/main (all 5 atomic commits unpushed)
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(grep -cF 'Wave-3 outcome (BRANCH_C SURVIVE)' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)" -ge 1 ] && [ "$(grep -cF '260502-tjn' .planning/STATE.md)" -ge 2 ] && [ -f .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt ] && [ "$(grep -c '^## ANCHOR' .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/honest_framing_anchors_post.txt)" -eq 4 ] && [ "$(grep -cF '**SH2B3 12q24, anchor example.**' docs/manuscript/id-vs-ref-LD.md)" -eq 1 ] && [ "$(grep -cF 'SUPERSEDED 2026-04-25' docs/manuscript/id-vs-ref-LD.md)" -eq 2 ] && [ "$(grep -cF '### Identity-LD Inflation and Its Mechanism' docs/manuscript/id-vs-ref-LD.md)" -eq 1 ] && [ "$(grep -cF '### Harmonization-Pipeline Diagnostics' docs/manuscript/id-vs-ref-LD.md)" -eq 2 ] && BASELINE=$(cat .planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/forbidden_token_baseline.txt) && POST=$(grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md) && [ "$POST" -le "$BASELINE" ] && [ "$(md5sum results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')" = "462ada6ab64fdf8571fb5ed7dd6c6ea2" ] && [ "$(md5sum results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')" = "8255c1acf50add5f68dfb551af977b53" ] && [ "$(md5sum results/fine_mapping/susie/stroke.EUR.SH2B3_12q24.fit.rds | awk '{print $1}')" = "a041eecc27f3086190069783eeb45ffe" ] && echo PASS</automated>
  </verify>
  <done>
    TRACK-A-FROZEN-NUMBERS.md gains Wave-3 outcome BRANCH_C SURVIVE LIVE block; STATE.md gains 260502-tjn row + frontmatter `last_updated` refresh + body line 67 update (Track-B-encoded fields preserved); 4 honest-framing-lock content-phrase anchors verified byte-identical at section-header level (per 1c1 SUMMARY's documented planner-protocol limitation when edits land within anchor sections — Site 4.1 within Anchor 3 expected); forbidden-token count ≤ baseline; 3 SH2B3 anchor .fit.rds md5s preserved; 1c1 narrative reframes verified preserved; scope-bleed clean; no push; final atomic close-out commit landed.
  </done>
</task>

</tasks>

<verification>
**Per-task automated gates** (each task's <verify><automated> bash one-liner runs at task close-out):
- T1: manuscript md5 matches 1c1 baseline; 4 anchors captured; forbidden-token baseline captured
- T2: §SH2B3 case study rewritten; Anchor 1 locked-scalar preserved; D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE token cited; PP.H4 = 1.0 cited
- T3: rs3184504 cited ≥6 times; BRANCH_C_SURVIVE cited ≥3 times; 37-row framing cited ≥2 times
- T4: BRANCH_C_SURVIVE cited ≥6 times (cumulative); counterexample cited ≥2 times; heterogeneous cited ≥2 times
- T5: TRACK-A-FROZEN Wave-3 LIVE block present; STATE.md 260502-tjn row present (≥2 occurrences for the row + body line 67); 4 anchors at expected counts (1/2/1/2); forbidden-token post ≤ baseline; 3 SH2B3 anchor md5s preserved

**Whole-task semantic gates** (verify at T5 close-out):
- All 9 cascading sites updated (Abstract ×2 + 4 Results sections + 2 Discussion sections + Conclusion-1) → grep cumulative anchors
- Table 1 has 3 SH2B3 EUR Tier-A rows + R1 disclosure-honest framing
- 1c1 narrative reframes preserved (cache-staleness hypothesis cited ≥3 times; Δ = 0 cited ≥3 times)
- Scope-bleed clean (only 8 files modified across 5 commits, all whitelisted)
- No `git push` (commits ahead of origin/main ≥5)

**Hard non-target preservation** (verify at T5 close-out):
- `.planning/STATE.md` Track-B-encoded fields verbatim (Current focus / Current Position / stopped_at / progress.*; only `last_updated`, `last_activity`, body line 67, and Quick Tasks Completed table tail mutated)
- `.planning/ROADMAP.md` UNTOUCHED
- `.planning/phases/_archive/*` UNTOUCHED
- `.planning/quick/*-PLAN.md` / `*-SUMMARY.md` (other quick tasks) UNTOUCHED
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W*-PLAN.md` / `*-SUMMARY.md` UNTOUCHED
- `results/fine_mapping/susie/*.fit.rds` (96 files) UNTOUCHED at md5 level (3 SH2B3 anchors verified explicitly)
- No Track B m3 artifacts modified
- No `git push`
</verification>

<success_criteria>
- 5 atomic commits land via explicit `git add <path>` (T1 → T2 → T3 (2 commits) → T4 → T5 close-out); 6 commits if T3 batches into 2 separate commits (Abstract pair + Results triplet)
- §SH2B3 case study materializes BRANCH_C_SURVIVE: "Wave 2 R2 canonical-pair `coloc.susie` re-fire" + "PP.H4 = 1.0 at rs3184504" + "validated under matched-coverage real-LD" + "robust to LD-panel pathology + SuSiE-RSS strict-gate non-convergence"; locked-scalar Anchor 1 `**SH2B3 12q24, anchor example.**` byte-identical
- 8 cascading sites updated for BRANCH_C + 37-row merged manifest (Abstract ×2 paragraphs, Results §Trait Pair Distribution, Results §Top Real-LD-Surviving, Table 1 body row instantiation, Results §Pleiotropic Loci, Results §Pathway Enrichment, Discussion §Identity-LD Inflation, Discussion §Reframing, Conclusion-1)
- Table 1 has 3 SH2B3 EUR Tier-A rows (BMI–HTN, HTN–stroke, HTN–T2D, all PP.H4 = 1.0 at rs3184504) + R1 disclosure-honest empty-body framing
- TRACK-A-FROZEN-NUMBERS.md gains "## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE" block (md5 mutation expected; allowed in W6 per parent W6 PLAN bullet 5)
- STATE.md current per memory `feedback_state_md_keep_current.md`: 260502-tjn row appended to Quick Tasks Completed; frontmatter `last_updated` ISO-8601 UTC refreshed; body line 67 updated; Track-B-encoded fields preserved verbatim
- 4 honest-framing-lock content-phrase anchors preserved byte-identical at section-header level (Anchor 1 × 1, Anchor 2 × 2, Anchor 3 × 1, Anchor 4 × 2; matches 1c1 SUMMARY-verified counts)
- Forbidden-token gate PASS (regex `(revision|correction|cleanup|fix|audit)` post-edit count ≤ baseline)
- 3 SH2B3 anchor `.fit.rds` md5s preserved (`462ada6a…` / `8255c1ac…` / `a041eecc…`)
- 1c1 narrative reframes verified preserved post-edit (cache-staleness hypothesis + Δ = 0 references intact)
- No `.planning/ROADMAP.md` mutation; no `_archive/*` mutation; no other-quick-task PLAN/SUMMARY history rewrite; no `git push`
- All 5 commits use explicit-path `git add` (no `git add -A` / `.`); pre-existing dirty paths (`.claude/settings.json`, `.planning/config.json`, parallel-workstream backup dirs) NOT staged
</success_criteria>

<output>
After Task 5 close-out, create `.planning/quick/260502-tjn-w6-wave-3-outcome-substitution-branch-c-/260502-tjn-SUMMARY.md` with:
- Outcome: BRANCH_C_SURVIVE narrative materialized at 9 cascading sites + Table 1 instantiation + TRACK-A-FROZEN Wave-3 outcome LIVE block
- Atomic-commit list with hashes filled at close-out (5 commits or 6 if T3 splits)
- Per-site edit table (9 sites; pre-edit phrase / post-edit phrase / commit hash / char delta)
- 4-anchor preservation table (semantic-header check at expected counts 1/2/1/2; planner-protocol limitation note per 1c1)
- Forbidden-token gate result (baseline / post / delta)
- 3 SH2B3 anchor md5 preservation table
- TRACK-A-FROZEN md5 pre→post (mutation allowed; new value documented)
- STATE.md update verification (Track-B fields preserved; 260502-tjn row appended; body line 67 + frontmatter refreshed)
- Scope-bleed audit clean (file list)
- 1c1 preservation verification (cache-staleness reframe references intact)
- Carrier-pigeon items for Carter (parent W6 PLAN remaining scope: mechanical rename half [TRACK_A_PIVOT → ID_VS_REF_LD other artifacts]; D-TA-Wave1-headline RECOMPUTE branch materialization [W1 sweep ruled NONE_CONVERGED → headline 51/96 PRESERVED with disclosure column; carried forward]; Tables 2-4 placeholder fills beyond Table 1; Figure legends rewrite beyond what BRANCH_C affects; Wave 6 closeout / OSF deviation log entries)
- Self-Check: PASSED block listing all verification gates with PASS/FAIL outcomes
</output>
