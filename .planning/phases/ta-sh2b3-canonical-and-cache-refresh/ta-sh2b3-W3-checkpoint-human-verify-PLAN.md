---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 3
slug: W3-checkpoint-human-verify
type: execute
wave: 3
depends_on: ["W2"]
files_modified:
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
autonomous: false
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "Carter inspects Wave 2 PP.H4 outcomes (per-pair report TSV + CONTEXT.md D-TA-Wave2-outcomes table) BEFORE any narrative writes"
    - "Carter selects branch (a) collapse / (b) partial / (c) survive for the BMI–HTN canonical pair specifically (per D-TA-Wave3-thresholds: <0.5 / [0.5, 0.8) / ≥0.8)"
    - "Decision recorded in CONTEXT.md as D-TA-WAVE3-OUTCOME-{BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE}"
    - "Wave 4, 5, 6 plans dispatch only after this decision is recorded; Wave 6 narrative branch references {wave3_branch} substitution per D-TA-Wave3-thresholds 'How to apply'"
    - "No narrative writes happen in Wave 3 (the gate is decision-only; writes belong to Wave 6 after Wave 5 disk freeze per invariant 2)"
  artifacts:
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md"
      provides: "Recorded D-TA-WAVE3-OUTCOME-{BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE} decision under <decisions> block"
      contains: "D-TA-WAVE3-OUTCOME-"
  key_links:
    - from: "results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json"
      to: "Carter visual inspection of PP.H4"
      via: "ta-sh2b3-W2-pp-h4-report.tsv presentation"
      pattern: "PP.H4.abf"
    - from: "D-TA-WAVE3-OUTCOME-{X}"
      to: "Wave 6 narrative branch selection"
      via: "{wave3_branch} substitution token"
      pattern: "BRANCH_(A_COLLAPSE|B_PARTIAL|C_SURVIVE)"
---

<objective>
Wave 3 — `checkpoint:human-verify` outcome-branch gate. Carter selects the SH2B3 BMI–HTN reference-LD outcome branch (a/b/c) from Wave-2 disk numbers BEFORE any narrative writes. The decision is recorded as `D-TA-WAVE3-OUTCOME-{BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE}` in CONTEXT.md addendum. Wave 6 narrative branches reference this token via `{wave3_branch}` substitution.

Purpose: Honest-framing-lock invariant 2 — narrative writes happen ONLY at Wave 6, AFTER disk numbers are frozen at Wave 5, AND the outcome branch is human-selected (NOT pre-committed by the planner). The audit-V2 reviewer specifically flagged "non-convergence treated as data" + "manuscript pre-committed before evidence" as the issues to avoid; this gate is the structural mitigation.

Output: A new sub-section in `ta-sh2b3-CONTEXT.md` under `<decisions>` recording the chosen branch + Carter's brief justification + downstream-plan implications.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md
@CLAUDE.md

<interfaces>
<!-- Wave 2 produced these — Wave 3 reads only -->
- results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json (canonical literature claim)
- results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json (canonical literature claim)
- results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json (7 other new pairs)
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv (per-pair PP.H4 + threshold classification)
- D-TA-Wave2-outcomes (CONTEXT.md sub-section) — table of 9 PP.H4 values with threshold class

<!-- Threshold definitions (D-TA-Wave3-thresholds; LOCKED) -->
- (a) BRANCH_A_COLLAPSE: PP.H4 < 0.5 → identity-LD canonical claim does NOT survive matched-LD; flagship demonstrated collapse; strongest finding; Discussion §Identity-LD Inflation is load-bearing
- (b) BRANCH_B_PARTIAL: PP.H4 ∈ [0.5, 0.8) → partial survival; calibration finding; manuscript pivots to "magnitude of inflation, not categorical"
- (c) BRANCH_C_SURVIVE: PP.H4 ≥ 0.8 → canonical claim holds up under matched-LD; SH2B3 anchor flips from "collapse" to "validated"

<!-- Carter selects ONLY for the BMI–HTN canonical pair (per D-TA-Wave3-thresholds 'How to apply') -->
- The other 8 pairs (HTN-stroke + 7 lattice fillers) are observed in the same report; Carter MAY note unexpected outcomes there
- The BRANCH decision drives Wave 6 narrative; HTN-stroke + the 7 other pairs feed Table 3 SH2B3 row symmetrization (Wave 6) but do not select the branch
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 1: Present Wave 2 PP.H4 outcomes + Carter selects branch + record D-TA-WAVE3-OUTCOME</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv (per-pair PP.H4 with threshold classification)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave3-thresholds" + §"D-TA-Wave2-outcomes"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C8 row
  </read_first>
  <what-built>
    Wave 2 fired 9 SH2B3 EUR canonical-pair coloc.susie jobs at Wave-1 PRIMARY_L. Per-pair PP.H4 outcomes are on disk + summarized in `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv` and the `D-TA-Wave2-outcomes` sub-section of CONTEXT.md.

    The manuscript's canonical literature claims under Stage 1d identity-LD were:
    - BMI–hypertension PP.H4 = 1.00 at rs3184504 / rs10774625 / rs7137828 / rs4766578
    - hypertension–stroke PP.H4 = 1.00 at the same 4 lead variants

    Wave 2 tested both under reference-LD with Wave-1 PRIMARY_L converged fits. The PP.H4 values you see in the report are the CORE EVIDENCE for the SH2B3 case-study reframe in the manuscript. They have not yet been written into any narrative — that happens in Wave 6, AFTER you select the branch here.
  </what-built>
  <action>
    See <how-to-verify> below — this is a checkpoint:human-verify task. The user (Carter) executes the verification + decision-recording steps; the executor agent presents the outcome and waits for resume-signal.
  </action>
  <how-to-verify>
    1. **Inspect the per-pair PP.H4 report:**
       ```bash
       cat /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
       ```
       Visually confirm:
       - 9 rows present (one per SH2B3 EUR canonical pair)
       - PP.H4 column populated with finite numerics for all 9
       - Threshold_class column shows one of: COLLAPSE_BELOW_0.5 / PARTIAL_0.5_TO_0.8 / SURVIVE_GE_0.8

    2. **Inspect raw JSON for the two canonical literature claims:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       echo "=== BMI–HTN ==="
       jq '.summary' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json
       echo "=== HTN–stroke ==="
       jq '.summary' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
       ```

    3. **Select the branch based on the BMI–HTN PP.H4 value (D-TA-Wave3-thresholds, the CANONICAL pair):**
       - If BMI–HTN PP.H4 < 0.5 → branch **(a) BRANCH_A_COLLAPSE**
         - Manuscript narrative: "canonical claim does NOT survive matched-LD; flagship demonstrated collapse"
         - Discussion §Identity-LD Inflation is the load-bearing section
       - If BMI–HTN PP.H4 ∈ [0.5, 0.8) → branch **(b) BRANCH_B_PARTIAL**
         - Manuscript narrative: "magnitude of inflation, not categorical"
         - Discussion §Identity-LD Inflation AND §SH2B3 case-study get rewrites of comparable weight
       - If BMI–HTN PP.H4 ≥ 0.8 → branch **(c) BRANCH_C_SURVIVE**
         - Manuscript narrative: "SH2B3 anchor flips from collapse to validated"
         - Manuscript headline narrows; Fig S2 + FTO Tier-C disclosure remain load-bearing

    4. **Append the decision to CONTEXT.md** under `<decisions>` (after `D-TA-Wave2-outcomes`):

       ```markdown
       ### D-TA-WAVE3-OUTCOME-{BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE}: SH2B3 BMI–HTN outcome branch (Wave 3)

       **Recorded:** {timestamp}

       **Selected by Carter:** branch ({a|b|c})

       **Evidence:** BMI–HTN PP.H4 = {value} (range {min}–{max} across 9 SH2B3 EUR pairs).

       **Other canonical pair:** HTN–stroke PP.H4 = {value} (Threshold_class = {class}).

       **Carter's note (optional):** {free-form Carter note on the branch decision; e.g., "BMI–HTN collapsed cleanly to PP.H4 = 0.32, expected"}

       **Wave 6 narrative directive:**
       - {brief restatement of which prose anchors get rewritten per the chosen branch}
       - Manuscript paragraphs to update: {Methods/Results/Discussion/Limitations/Abstract/Conclusion-1/captions/tables}
       ```

       Replace the placeholder `BRANCH_*` token in the heading with the actual selected branch (one of `BRANCH_A_COLLAPSE`, `BRANCH_B_PARTIAL`, `BRANCH_C_SURVIVE`).

    5. **Atomic commit:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W3): record D-TA-WAVE3-OUTCOME-{BRANCH} from Carter human-verify gate"
       ```
       (Substitute the actual `{BRANCH}` token in the commit message.)

    6. **Verify the gate cleared:**
       ```bash
       bin/verify_ta_sh2b3_phase.sh --wave 3
       ```
       C8 must emit PASS.

    **Resume signal:** Type the chosen branch token: `BRANCH_A_COLLAPSE` or `BRANCH_B_PARTIAL` or `BRANCH_C_SURVIVE` (one of the three; Wave 6 narrative depends on it).
  </how-to-verify>
  <acceptance_criteria>
    - `grep -E "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE):" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit (matches one of the three branches).
    - The recorded sub-section includes the BMI–HTN PP.H4 value (numeric).
    - The recorded sub-section includes the HTN–stroke PP.H4 value (numeric).
    - C8 from `bin/verify_ta_sh2b3_phase.sh --wave 3` emits PASS.
    - Atomic commit landed.
    - **NO narrative writes anywhere else** — verify `git diff HEAD~1 -- docs/manuscript/track_a_pivot.md` is empty (or that file isn't modified): `git log --diff-filter=M --name-only HEAD~1..HEAD | grep -c "docs/manuscript/track_a_pivot.md"` returns 0 (invariant 2 preserved).
  </acceptance_criteria>
  <resume-signal>Type one of: `BRANCH_A_COLLAPSE`, `BRANCH_B_PARTIAL`, `BRANCH_C_SURVIVE`</resume-signal>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && [ "$(git log --diff-filter=M --name-only HEAD~1..HEAD 2>/dev/null | grep -c 'docs/manuscript/track_a_pivot.md')" -eq 0 ] && echo PASS</automated>
  </verify>
  <done>
    Carter selected the SH2B3 BMI–HTN reference-LD outcome branch (a/b/c) from Wave 2 disk numbers; D-TA-WAVE3-OUTCOME-{BRANCH} recorded in CONTEXT.md addendum; atomic commit landed. NO narrative writes happened in Wave 3 (invariant 2 preserved). Wave 6 narrative tasks now have a concrete branch to write against. Verifies C8 in VALIDATION.md.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Wave 2 disk numbers ↔ Wave 6 narrative writes | Wave 3 is the structural gate; without it, Wave 6 could pre-commit to a/b/c without evidence |
| Carter's branch selection ↔ CONTEXT.md addendum recording | Decision must be persisted as a grep-able token (D-TA-WAVE3-OUTCOME-X) for downstream consumption |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-03 | T (Tampering) | Honest-framing-lock invariant 2 (narrative writes ONLY at Wave 6 AFTER Wave 5 freeze) | mitigate | Wave 3 acceptance criterion: `git log --diff-filter=M --name-only HEAD~1..HEAD \| grep -c docs/manuscript/track_a_pivot.md` returns 0 |
| T-PROCESS-04 | T (Tampering) | Pre-commitment to a/b/c branch by planner/executor | mitigate | This plan explicitly contains NO branch-specific prose; only the human-verify checkpoint and Carter's selection are recorded |
</threat_model>

<verification>
- D-TA-WAVE3-OUTCOME-{X} token recorded in CONTEXT.md (one of A_COLLAPSE / B_PARTIAL / C_SURVIVE)
- BMI–HTN PP.H4 + HTN–stroke PP.H4 numerics included in the recorded sub-section
- C8 PASS from verification harness
- No narrative file modifications in this wave's commits
- 1 atomic commit landed (the D-TA-WAVE3-OUTCOME recording)
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C8** D-TA-WAVE3-OUTCOME branch recorded — Task 1
</verification_criteria>

<success_criteria>
- Carter selects branch (a/b/c) for BMI–HTN canonical pair
- D-TA-WAVE3-OUTCOME-{BRANCH} recorded in CONTEXT.md as a single grep-able token
- BMI–HTN + HTN–stroke PP.H4 values explicitly cited in the addendum
- C8 emits PASS
- NO docs/manuscript/track_a_pivot.md modifications in this wave (invariant 2 preserved)
- Atomic commit landed via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W3-checkpoint-human-verify-SUMMARY.md` with:
- D-TA-WAVE3-OUTCOME branch selected (one of A/B/C)
- BMI–HTN + HTN–stroke PP.H4 values
- Wave-6 narrative-branch directive (which prose anchors get rewritten + the framing the chosen branch implies)
- Verification dimension D1: branch token recorded; D2: BMI–HTN value cited; D3: HTN–stroke value cited; D4: no premature narrative writes; D5: C8 PASS
- Wave 4 GO status (Wave 4 cache-refresh is independent but commonly fires after Wave 3 in serial-staging order)
</output>
