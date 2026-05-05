---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 4
slug: W4-tier-assignments-hla-reconcile
type: execute
wave: 4
depends_on: ["W2"]
gate_condition: "DEFAULT: SKIPPED. FIRES iff Cowork-side audit decides the cheap fix (manuscript footnote, A9 short version) is INSUFFICIENT and the on-disk file should be regenerated. The Cowork-side decision is recorded in ta-r3-CONTEXT.md as either `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` (DEFAULT; SKIPPED) or `D-TA-R3-W4-RECLASS_FIRED` (W4 dispatches reclassification). The executor agent reads `D-TA-R3-W4-GATE` from ta-r3-CONTEXT.md BEFORE firing any task; if SKIPPED (the default), executor records the deferral and exits cleanly with no LSF dispatch. If FIRES, executor proceeds with reclassification. This wave is `autonomous: false` because the row-count investigation requires inspection + decision-recording that may surface unexpected findings."
files_modified:
  - results/qtl_coloc/tier_assignments.tsv  # MODIFY only if RECLASS_FIRED; else untouched
  - results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv  # NEW only if RECLASS_FIRED
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  - logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
autonomous: false
requirements:
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "W4 gate condition checked BEFORE any task fires: D-TA-R3-W4-GATE in ta-r3-CONTEXT.md must read FIRES; default is SKIPPED (recorded as D-TA-R3-W4-DEFERRED_TO_FOOTNOTE per OSF amendment paragraph (g) option (i))"
    - "Investigation TSV ta-r3-W4-row-investigation.tsv enumerates unique region_ids in tier_assignments.tsv column 1 + cross-references against v5 doc HLA_6p21 claim (current state: grep HLA_6p21 returns 0)"
    - "If RECLASS_FIRED: tier_assignments_hla_fallback_separate.tsv created with HLA-encoded rows split out (NEW file)"
    - "If RECLASS_FIRED: tier_assignments.tsv rebuilt to reflect narrative claim of 200 rows post-HLA-fallback (current 233 - 33 HLA-encoded = 200 expected, OR documented divergence)"
    - "If RECLASS_FIRED: downstream aggregators that consume tier_assignments.tsv re-run (e.g., src/R/aggregators/aggregate_table1_pleiotropic_loci.R per ta-sh2b3-W7 closeout)"
    - "If RECLASS_FIRED: successor row added to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (NEVER overwrite; W4-R3 row appended after the W7 baseline row per plan-of-plans risk register row 5)"
    - "Outcome recorded in ta-r3-CONTEXT.md as exactly one of D-TA-R3-W4-DEFERRED_TO_FOOTNOTE (default) or D-TA-R3-W4-RECLASS_FIRED"
    - "docs/manuscript/id-vs-ref-LD.md md5 unchanged (63fd81385590ffc8d23d45a0f0598959; honest-framing-lock invariant)"
    - "Multi-terminal git staging: explicit `git add <path>` only per .planning/feedback_multi_terminal_staging.md"
  artifacts:
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv"
      provides: "Region-id enumeration in tier_assignments.tsv + cross-reference with v5 narrative HLA_6p21 claim (always written, regardless of RECLASS or DEFERRED)"
      contains: "region_id"
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md"
      provides: "D-TA-R3-W4-DEFERRED_TO_FOOTNOTE or D-TA-R3-W4-RECLASS_FIRED outcome + investigation summary"
      contains: "D-TA-R3-W4-"
    - path: "results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv"
      provides: "HLA-encoded rows split out from main table (NEW; only if RECLASS_FIRED)"
  key_links:
    - from: "Cowork-side audit decision (recorded in ta-r3-CONTEXT.md)"
      to: "D-TA-R3-W4-GATE: SKIPPED or FIRES"
      via: "human-decision token; default SKIPPED"
      pattern: "D-TA-R3-W4-GATE: (SKIPPED|FIRES)"
    - from: "results/qtl_coloc/tier_assignments.tsv (current 233 rows)"
      to: "tier_assignments.tsv (200 rows post-HLA-fallback) + tier_assignments_hla_fallback_separate.tsv (33 HLA rows split out)"
      via: "Reclassification only if RECLASS_FIRED"
      pattern: "tier_assignments_hla_fallback_separate"
    - from: "tier_assignments.tsv md5 (post-reclass)"
      to: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (W4-R3 successor row appended)"
      via: "md5 successor row append (NEVER overwrite per Pitfall 5)"
      pattern: "tier_assignments.tsv.*ta-r3-W4"
---

<objective>
Wave 4 — Tier-assignments HLA_6p21 reconciliation. The 200-vs-224 row count narrative-vs-data mismatch in `results/qtl_coloc/tier_assignments.tsv` flagged in the Cowork-side v5 handoff doc: the manuscript narrative claims 224 rows minus 24 HLA = 200, but the on-disk file currently has 233 data rows + 1 header = 234 lines, AND `grep HLA_6p21 results/qtl_coloc/tier_assignments.tsv` returns 0 matches. The narrative arithmetic does not match the current on-disk state. This wave investigates the discrepancy and reconciles per OSF amendment paragraph (g): either (i) confirm the 233-row count is correct and update the narrative footnote (Cowork-side A9 short path), OR (ii) split HLA-encoded rows out into a sibling file `tier_assignments_hla_fallback_separate.tsv` and rebuild the primary table to match narrative.

**Conditional fire (gated on Cowork-side audit decision):** This wave's `gate_condition` frontmatter field is the authoritative control:
- DEFAULT: `D-TA-R3-W4-GATE: SKIPPED` → record `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` and exit cleanly. The Cowork-side A9 manuscript footnote (cheap path) handles the discrepancy without modifying on-disk files. This is the expected default per OSF amendment paragraph (g).
- ESCALATED: `D-TA-R3-W4-GATE: FIRES` → reclassification dispatches. Cowork-side has decided the footnote is insufficient and the on-disk file should be regenerated. The investigation + reclassification + downstream aggregator re-run + md5 successor row append all execute.

This wave is `autonomous: false` because:
1. Investigation may surface findings that the planner did not anticipate (per plan-of-plans risk register row 5: "tier_assignments.tsv row count investigation reveals systemic bookkeeping drift across multiple aggregators")
2. RECLASS_FIRED branch decision is a Cowork-side human input, not a computed gate
3. Investigation halts on surprise; user decides whether to fire fix or defer to Cowork footnote

Purpose: Closes audit-V2 §HQ#2 negative-control row count reconciliation per OSF amendment paragraph (g). Default behavior preserves the on-disk state (cheap path; A9 footnote suffices). This is audit-driven re-analysis, NOT a fix or revision.

Output (default): Investigation TSV + `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` decision recorded.
Output (if RECLASS_FIRED): Investigation TSV + reclassified `tier_assignments.tsv` + new `tier_assignments_hla_fallback_separate.tsv` + downstream aggregators rebuilt + successor md5 row in `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` + `D-TA-R3-W4-RECLASS_FIRED` decision recorded.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/amendments/osf-amendment-r3-2026-05-04.md
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
@CLAUDE.md

<interfaces>
<!-- W2 produced these — W4 reads -->
- coloc_summary.tsv post-W2 md5 (rebuilt aggregators baseline)
- 28 R1 R-pair JSONs in results/multitrait/coloc_susie/

<!-- W4 gate token -->
- D-TA-R3-W4-GATE: <SKIPPED|FIRES> — read by Task 1 step 1 from ta-r3-CONTEXT.md
- DEFAULT = SKIPPED (per OSF amendment paragraph (g) option (i))

<!-- Existing files Wave 4 reads / mutates -->
- results/qtl_coloc/tier_assignments.tsv — current state: 233 data rows + 1 header = 234 lines; `grep HLA_6p21` returns 0
- src/R/aggregators/aggregate_table1_pleiotropic_loci.R — downstream aggregator that consumes tier_assignments.tsv (per ta-sh2b3-W7 md5 whitelist L329)
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv — schema 4-column (path, md5, rationale, commit_introducing); W4-R3 successor row appended (NEVER overwrite per Pitfall 5)

<!-- Compute envelope -->
- Investigation only: ~5 min (awk + grep + Rscript)
- Reclassification (if RECLASS_FIRED): ~30 min (split + Rscript aggregator re-run; no LSF needed; runs locally on la_multitrait_r env)
- No LSF dispatch in this wave

<!-- Pitfall: SH2B3 row count investigation may surface systemic drift (plan-of-plans risk register row 5) -->
- If investigation reveals drift across multiple aggregators (not just tier_assignments.tsv), HALT and surface to user
- Do NOT cascade fixes across aggregators in this wave; that is a multi-wave undertaking
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Read W4 gate; if SKIPPED record D-TA-R3-W4-DEFERRED_TO_FOOTNOTE and exit cleanly. Always write investigation TSV regardless of gate state.</name>
  <files>
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
    logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W4-GATE token; DEFAULT=SKIPPED)
    - results/qtl_coloc/tier_assignments.tsv (read-only inspection target; 233 data rows + 1 header expected)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — Negative-control row-count reconciliation" lines 79-80 (W4 gate spec; option (i) = footnote default; option (ii) = reclass)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 4 Tasks (skeleton)" lines 192-195 (PRIMARY SPEC; investigation source)
  </read_first>
  <action>
    1. **Read W4 gate from ta-r3-CONTEXT.md.** Default disposition is SKIPPED. The Cowork-side audit may have explicitly written `D-TA-R3-W4-GATE: FIRES` to escalate; if absent or set to SKIPPED, default behavior applies.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       mkdir -p logs/ta_r3_W4_hla_reconcile
       LOG=logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
       : > "$LOG"

       GATE=$(grep -oE "D-TA-R3-W4-GATE: (SKIPPED|FIRES)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | grep -oE "(SKIPPED|FIRES)" | head -1)
       if [ -z "$GATE" ]; then
         GATE=SKIPPED  # default per OSF amendment paragraph (g) option (i)
         echo "D-TA-R3-W4-GATE not explicitly set; defaulting to SKIPPED" | tee -a "$LOG"
       fi
       echo "W4 gate: $GATE" | tee -a "$LOG"
       ```

    2. **Always write the investigation TSV** (regardless of gate state — investigation is the source of truth for either branch):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       OUT=.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv

       # Header
       echo -e "metric\tvalue\tnote" > "$OUT"

       # Total lines + data rows
       N_LINES=$(wc -l < results/qtl_coloc/tier_assignments.tsv)
       N_ROWS=$((N_LINES - 1))
       echo -e "total_lines_with_header\t${N_LINES}\tincludes header line" >> "$OUT"
       echo -e "data_rows\t${N_ROWS}\texcludes header" >> "$OUT"

       # v5 doc claim
       echo -e "v5_narrative_claim\t200\tfrom HPC_HANDOFF_v5_2026-05-04.md (224 disk rows minus 24 HLA = 200)" >> "$OUT"
       echo -e "v5_arithmetic_check\t$((224 - 24))\t224 - 24 = 200" >> "$OUT"
       echo -e "discrepancy_disk_vs_v5\t$((N_ROWS - 200))\tcurrent disk rows minus v5 narrative" >> "$OUT"

       # HLA encoding investigation
       N_HLA_6P21=$(grep -c "HLA_6p21" results/qtl_coloc/tier_assignments.tsv 2>/dev/null || echo 0)
       echo -e "grep_HLA_6p21_count\t${N_HLA_6P21}\texpected ≥1 if HLA encoded as HLA_6p21" >> "$OUT"

       # Try alternative HLA encodings
       N_HLA_DRB1=$(grep -c "HLA-DRB1\|HLA_DRB1" results/qtl_coloc/tier_assignments.tsv 2>/dev/null || echo 0)
       echo -e "grep_HLA_DRB1_count\t${N_HLA_DRB1}\talternative encoding HLA-DRB1 / HLA_DRB1" >> "$OUT"

       N_MHC=$(grep -c "MHC" results/qtl_coloc/tier_assignments.tsv 2>/dev/null || echo 0)
       echo -e "grep_MHC_count\t${N_MHC}\talternative encoding MHC" >> "$OUT"

       # Chromosome 6 region (HLA on chr6:28-34 Mb)
       # Identify region_id column (assume col 1 per standard tier_assignments schema)
       N_CHR6_HLA_RANGE=$(awk -F'\t' 'NR>1 && $1 ~ /6p21|chr6:(28|29|30|31|32|33)/' results/qtl_coloc/tier_assignments.tsv | wc -l)
       echo -e "rows_matching_6p21_or_chr6_HLA_range\t${N_CHR6_HLA_RANGE}\trows whose region_id matches 6p21 or chr6 HLA range" >> "$OUT"

       # Unique region_id count
       N_UNIQUE_REGIONS=$(awk -F'\t' 'NR>1 {print $1}' results/qtl_coloc/tier_assignments.tsv | sort -u | wc -l)
       echo -e "unique_region_ids\t${N_UNIQUE_REGIONS}\tdistinct values in column 1" >> "$OUT"

       # Top 20 most-frequent region_ids (helps see whether HLA is encoded under a distinct region_id name)
       echo -e "# Top 20 most-frequent region_ids:" >> "$OUT"
       awk -F'\t' 'NR>1 {print $1}' results/qtl_coloc/tier_assignments.tsv | sort | uniq -c | sort -rn | head -20 | \
         awk '{print "top_freq_region\t"$2"\toccurs "$1" times"}' >> "$OUT"

       cat "$OUT" | tee -a "$LOG"
       ```

    3. **If gate is SKIPPED, record D-TA-R3-W4-DEFERRED_TO_FOOTNOTE and exit cleanly:**

       ```bash
       if [ "$GATE" = "SKIPPED" ]; then
         cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W4-DEFERRED_TO_FOOTNOTE: W4 SKIPPED ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Disposition:** Per OSF amendment paragraph (g) option (i): the 200-vs-224 row count narrative-vs-data discrepancy in results/qtl_coloc/tier_assignments.tsv is reconciled via Cowork-side manuscript footnote (A9 short version). On-disk file remains UNTOUCHED. Reclassification deferred unless Cowork-side audit later escalates.

       **Investigation findings:** See [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv](ta-r3-W4-row-investigation.tsv). Key facts:
       - Current on-disk: $N_ROWS data rows
       - v5 narrative claim: 200 rows
       - Discrepancy: $((N_ROWS - 200)) rows
       - HLA_6p21 grep count: $N_HLA_6P21 (zero matches; HLA may be encoded under different region_id pattern)
       - HLA-DRB1 alternative encoding: $N_HLA_DRB1 matches
       - MHC alternative encoding: $N_MHC matches
       - chr6 HLA range matches: $N_CHR6_HLA_RANGE rows

       **Manuscript implication (informational; OUT of phase scope):** Cowork-side A9 footnote will disclose the row-count reconciliation arithmetic without modifying the on-disk supplementary file. The footnote text references this investigation TSV as the canonical source.

       **Wave 5 implication:** No md5 successor row needed for tier_assignments.tsv (file unchanged in this wave).
       EOF
         git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv \
                 .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md \
                 logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
         git commit -m "docs(ta-r3, W4): SKIPPED — D-TA-R3-W4-DEFERRED_TO_FOOTNOTE (audit-driven re-analysis; row-count reconciliation via Cowork-side A9 footnote; default OSF amendment paragraph (g) option (i))"
         echo "W4 SKIPPED; exit cleanly" | tee -a "$LOG"
         exit 0
       fi
       ```

    4. **If gate is FIRES, halt + surface investigation findings to user before proceeding (autonomous: false; wait for human review):**

       Per plan-of-plans risk register row 5, the investigation may surface systemic bookkeeping drift across multiple aggregators. The user must inspect the investigation TSV and confirm whether to proceed with reclassification (Task 2) or escalate to a multi-aggregator triage. Record the halt + investigation in CONTEXT.md and emit a summary to the user.

       ```bash
       if [ "$GATE" = "FIRES" ]; then
         cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W4-INVESTIGATION-CHECKPOINT: human-verify ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Status:** GATE=FIRES; investigation TSV written. **HALTED for human review** (autonomous: false).

       **Investigation TSV:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv](ta-r3-W4-row-investigation.tsv)

       **Key findings to review:**
       - Current on-disk: $N_ROWS data rows
       - v5 narrative claim: 200 rows
       - Discrepancy: $((N_ROWS - 200)) rows
       - HLA encoding ambiguity: HLA_6p21=$N_HLA_6P21, HLA-DRB1=$N_HLA_DRB1, MHC=$N_MHC, chr6 HLA range=$N_CHR6_HLA_RANGE rows

       **Decision required (Carter):**
       - PROCEED → run Task 2 (reclassification: split HLA-encoded rows out + rebuild tier_assignments.tsv to match narrative)
       - HALT → investigation reveals systemic drift; switch to multi-aggregator triage in a separate phase

       **Resume signal:** Task 2 fires only if Carter has confirmed the investigation findings + the HLA encoding pattern that splits cleanly into 33 (or N) HLA-encoded rows out + leaves 200 (or N - count) primary rows.
       EOF
         git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv \
                 .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md \
                 logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
         git commit -m "docs(ta-r3, W4): GATE=FIRES — investigation TSV written + halted for human review (audit-driven re-analysis; D-TA-R3-W4-INVESTIGATION-CHECKPOINT)"
         echo "W4 GATE=FIRES; investigation halted for human review. Inspect ta-r3-W4-row-investigation.tsv before running Task 2." | tee -a "$LOG"
         # Do NOT exit 1 here — Task 2 will fire when invoked separately
       fi
       ```
  </action>
  <acceptance_criteria>
    - W4 gate read from ta-r3-CONTEXT.md (defaulted to SKIPPED if absent).
    - Investigation TSV written regardless of gate: `[ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv ]` AND `[ "$(wc -l < .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv)" -ge 8 ]` (header + ≥7 metric rows).
    - Investigation TSV references HLA encoding investigation: `grep -cE "HLA_6p21|HLA-DRB1|MHC|6p21" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv` returns ≥ 3.
    - If GATE=SKIPPED: `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE` recorded: `grep -c "D-TA-R3-W4-DEFERRED_TO_FOOTNOTE" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - If GATE=FIRES: `D-TA-R3-W4-INVESTIGATION-CHECKPOINT` recorded with halt-for-human-review status: `grep -c "D-TA-R3-W4-INVESTIGATION-CHECKPOINT" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - tier_assignments.tsv UNTOUCHED in this task (regardless of gate): `md5sum results/qtl_coloc/tier_assignments.tsv` matches whatever value it had pre-Task-1 (no modification).
    - Atomic commit landed (commit message reflects gate state).
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv ] && [ "$(wc -l < .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv)" -ge 8 ] && [ "$(grep -cE 'HLA_6p21|HLA-DRB1|MHC|6p21' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv)" -ge 3 ] && grep -qE "D-TA-R3-W4-(DEFERRED_TO_FOOTNOTE|INVESTIGATION-CHECKPOINT|RECLASS_FIRED)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    W4 gate read from ta-r3-CONTEXT.md. Investigation TSV written with HLA encoding enumeration + row-count discrepancy + top-20 frequent region_ids. If gate is SKIPPED (default): D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded + commit landed + W4 exits cleanly. If gate is FIRES: D-TA-R3-W4-INVESTIGATION-CHECKPOINT recorded with halt-for-human-review status + commit landed + Task 2 must be invoked separately by user. tier_assignments.tsv untouched. Honest-framing-lock manuscript md5 unchanged.
  </done>
</task>

<task type="checkpoint:human-verify" gate="conditional">
  <name>Task 2: (Gate=FIRES + human-confirmed only) Split HLA-encoded rows out into tier_assignments_hla_fallback_separate.tsv + rebuild tier_assignments.tsv to match narrative + re-run downstream aggregators + append successor md5 row to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (NEVER overwrite W7 row)</name>
  <files>
    results/qtl_coloc/tier_assignments.tsv
    results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-row-investigation.tsv (Task 1 output; identifies HLA encoding pattern)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W4-GATE must read FIRES + D-TA-R3-W4-INVESTIGATION-CHECKPOINT must exist)
    - results/qtl_coloc/tier_assignments.tsv (current 233-row file)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (4-column schema; W4-R3 successor row appended; W7 row preserved per Pitfall 5)
    - src/R/aggregators/aggregate_table1_pleiotropic_loci.R (downstream aggregator that consumes tier_assignments.tsv per ta-sh2b3-W7 md5 whitelist L329)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — Negative-control row-count reconciliation" line 80 (option (ii) reclass spec)
  </read_first>
  <what-built>
    Task 1 wrote the investigation TSV and halted for human review (autonomous: false). Task 2 only fires after Carter has reviewed the investigation findings and confirmed:
    1. The HLA encoding pattern that splits 233 rows cleanly into N HLA-encoded + (233 - N) primary rows, ideally yielding 200 primary rows per the v5 narrative claim
    2. The downstream aggregators that consume tier_assignments.tsv (likely just src/R/aggregators/aggregate_table1_pleiotropic_loci.R per ta-sh2b3-W7 md5 whitelist; verify before running)
    3. The successor md5 row format for .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (4-column schema; W4-R3 row appended; W7 row preserved)
  </what-built>
  <action>
    See <how-to-verify> below — this is a checkpoint:human-verify task. Carter executes the verification + decision-recording steps; the executor agent presents the outcome and waits for resume-signal.
  </action>
  <how-to-verify>
    1. **Re-verify gate is FIRES + investigation halt landed:**

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       grep -q "D-TA-R3-W4-GATE: FIRES" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md || \
         { echo "ABORT: gate not FIRES"; exit 1; }
       grep -q "D-TA-R3-W4-INVESTIGATION-CHECKPOINT" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md || \
         { echo "ABORT: Task 1 investigation halt not recorded; Task 1 must run first"; exit 1; }
       ```

    2. **Decide HLA encoding pattern from investigation TSV.** Read the top-20 frequent region_ids + HLA encoding counts. The likely pattern is one of:
       - HLA-DRB1 / HLA_DRB1 → if HLA-DRB1 count is non-trivial
       - MHC → if MHC count is non-trivial
       - chr6:NN-NN range encoded as `chr6_28000000_34000000` or similar → if chr6 HLA range count is non-trivial
       - Region IDs starting with `6p21_` → if any 6p21 prefix appears in top-20

       Carter selects the encoding pattern + records it as a regex in `HLA_REGEX` env var, e.g.:
       ```bash
       export HLA_REGEX='^(HLA-DRB1|MHC|6p21_HLA|chr6:(28|29|30|31|32|33))'
       ```

    3. **Split tier_assignments.tsv** using the chosen HLA_REGEX:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       BAK_TS=$(date +%Y%m%d_%H%M%S)
       cp results/qtl_coloc/tier_assignments.tsv results/qtl_coloc/tier_assignments.tsv.preW4.bak.${BAK_TS}

       # Header
       head -1 results/qtl_coloc/tier_assignments.tsv > /tmp/tier_header.txt

       # HLA-encoded rows
       (cat /tmp/tier_header.txt; awk -F'\t' -v re="$HLA_REGEX" 'NR>1 && $1 ~ re' results/qtl_coloc/tier_assignments.tsv) \
         > results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv

       # Non-HLA rows (replaces tier_assignments.tsv)
       (cat /tmp/tier_header.txt; awk -F'\t' -v re="$HLA_REGEX" 'NR>1 && $1 !~ re' results/qtl_coloc/tier_assignments.tsv) \
         > /tmp/tier_assignments_new.tsv
       mv /tmp/tier_assignments_new.tsv results/qtl_coloc/tier_assignments.tsv

       N_HLA=$(awk 'NR>1' results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv | wc -l)
       N_REMAINING=$(awk 'NR>1' results/qtl_coloc/tier_assignments.tsv | wc -l)
       echo "HLA-encoded rows split out: $N_HLA"
       echo "Remaining rows in tier_assignments.tsv: $N_REMAINING"
       echo "(Target: $N_REMAINING == 200 per v5 narrative claim)"
       ```

    4. **Re-run downstream aggregators** (per plan-of-plans skeleton task 3 + ta-sh2b3-W7 md5 whitelist L329):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
         src/R/aggregators/aggregate_table1_pleiotropic_loci.R 2>&1 | tee -a logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
       ```

       If additional aggregators consume tier_assignments.tsv (search via grep), re-run each:
       ```bash
       grep -lE "tier_assignments\.tsv|tier_assignments_hla_fallback_separate" src/R/aggregators/*.R
       ```

    5. **Append W4-R3 successor row to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv** (NEVER overwrite the W7 baseline row per Pitfall 5):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       NEW_MD5=$(md5sum results/qtl_coloc/tier_assignments.tsv | cut -d' ' -f1)
       NEW_HLA_MD5=$(md5sum results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv | cut -d' ' -f1)

       # Schema: path \t md5 \t rationale \t commit_introducing
       # Append W4-R3 rows (NEVER overwrite existing W7 row)
       cat >> .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv <<EOF
       results/qtl_coloc/tier_assignments.tsv	$NEW_MD5	W4-R3 (ta-r3) HLA reclassification: 233 -> $N_REMAINING rows post-HLA-fallback split	UNTRACKED
       results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv	$NEW_HLA_MD5	W4-R3 (ta-r3) NEW: $N_HLA HLA-encoded rows split out from primary tier_assignments.tsv	UNTRACKED
       EOF

       # Verify W7 row preserved (NOT overwritten)
       awk -F'\t' '$1 == "results/qtl_coloc/tier_assignments.tsv"' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l
       # Expected: 1 W7 row (if it existed pre-W4) + 1 new W4-R3 row = 2 (or just 1 W4-R3 if no W7 row existed)
       ```

    6. **Append D-TA-R3-W4-RECLASS_FIRED to ta-r3-CONTEXT.md** (under <decisions> section):

       ```markdown
       ### D-TA-R3-W4-RECLASS_FIRED: HLA reclassification fired ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Disposition:** Per OSF amendment paragraph (g) option (ii) — Carter escalated from default footnote (option (i)) to on-disk reclassification.

       **HLA encoding pattern used:** `<HLA_REGEX>`

       **Reclassification result:**
       - Pre-reclass tier_assignments.tsv data rows: 233
       - HLA-encoded rows split out: $N_HLA (now in tier_assignments_hla_fallback_separate.tsv)
       - Post-reclass tier_assignments.tsv data rows: $N_REMAINING
       - v5 narrative target: 200 rows
       - Match: $([ "$N_REMAINING" -eq 200 ] && echo "EXACT" || echo "DIVERGENCE ($N_REMAINING vs 200; document in cell)")

       **Backup preserved:** results/qtl_coloc/tier_assignments.tsv.preW4.bak.$BAK_TS

       **Downstream aggregators re-run:** src/R/aggregators/aggregate_table1_pleiotropic_loci.R + any others matching `grep -lE "tier_assignments" src/R/aggregators/*.R`

       **md5 successor rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv:**
       - tier_assignments.tsv: $NEW_MD5
       - tier_assignments_hla_fallback_separate.tsv: $NEW_HLA_MD5
       (W7 baseline row preserved per Pitfall 5; never overwritten.)

       **Manuscript implication (informational; OUT of phase scope):** Cowork-side v5 manuscript Table S<N> footnote updated to disclose: "Tier assignments are reported in the primary table for 200 non-HLA loci; 33 HLA-encoded loci (region 6p21) are reported separately in tier_assignments_hla_fallback_separate.tsv as a fallback artifact reflecting standard HLA-region coloc avoidance per REQ-NEGATIVE-CONTROLS."
       ```

    7. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add results/qtl_coloc/tier_assignments.tsv \
               results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md \
               logs/ta_r3_W4_hla_reconcile/hla_reconcile.log
       # Note: results/qtl_coloc/tier_assignments.tsv.preW4.bak.${TS} typically NOT committed (large; on-disk rollback path)
       git commit -m "feat(ta-r3, W4): RECLASS_FIRED — HLA reclassification (233 -> $N_REMAINING primary rows + $N_HLA HLA-fallback rows; audit-driven re-analysis; md5 successor rows appended NEVER overwrite W7)"
       ```

    **Resume signal:** Type `RECLASS_OK` if the reclassification yielded the expected 200 primary rows + 33 HLA-fallback rows, or `RECLASS_DIVERGENCE` if the row counts diverged from expectation (Cowork-side narrative may need updating).
  </how-to-verify>
  <acceptance_criteria>
    - Gate confirmed FIRES + investigation halt recorded at task entry.
    - tier_assignments_hla_fallback_separate.tsv exists: `[ -f results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv ]`.
    - tier_assignments.tsv row count reduced (HLA rows split out): `[ "$(awk 'NR>1' results/qtl_coloc/tier_assignments.tsv | wc -l)" -lt 233 ]`.
    - HLA-fallback file has at least 1 data row: `[ "$(awk 'NR>1' results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv | wc -l)" -ge 1 ]`.
    - tier_assignments.tsv post-reclass row count + HLA-fallback row count = 233 (no rows lost): the sum of the two file row counts equals the pre-W4 row count.
    - md5_baseline.tsv has W4-R3 successor rows: `awk -F'\t' '$3 ~ /W4-R3 \(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l` returns ≥ 2.
    - md5_baseline.tsv W7 baseline row preserved (NEVER overwritten): the file has more total lines post-W4 than pre-W4 (rows appended, not replaced).
    - D-TA-R3-W4-RECLASS_FIRED recorded: `grep -c "D-TA-R3-W4-RECLASS_FIRED" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - Atomic commit landed.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <resume-signal>Type `RECLASS_OK` (200 primary + N HLA-fallback rows match v5 narrative) or `RECLASS_DIVERGENCE` (Cowork-side narrative may need updating to reflect actual reclass row count)</resume-signal>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-R3-W4-GATE: FIRES" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && [ -f results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv ] && [ "$(awk 'NR>1' results/qtl_coloc/tier_assignments.tsv | wc -l)" -lt 233 ] && [ "$(awk 'NR>1' results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv | wc -l)" -ge 1 ] && [ "$(awk -F'\t' '$3 ~ /W4-R3 \(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l)" -ge 2 ] && [ "$(grep -c 'D-TA-R3-W4-RECLASS_FIRED' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Reclassification fired (only if gate FIRES + Carter resumed): tier_assignments.tsv split into primary (post-HLA) + tier_assignments_hla_fallback_separate.tsv (HLA-encoded rows). Downstream aggregators re-run. Successor md5 rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (NEVER overwrite W7 row). D-TA-R3-W4-RECLASS_FIRED recorded in ta-r3-CONTEXT.md. Honest-framing-lock manuscript md5 unchanged.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| W4 gate (D-TA-R3-W4-GATE token; default SKIPPED) ↔ Task dispatch | Task 1 reads gate FIRST; SKIPPED records DEFERRED_TO_FOOTNOTE and exits cleanly; FIRES halts for human review |
| tier_assignments.tsv (233 rows) ↔ post-reclass primary + HLA-fallback split | Backup preserved at tier_assignments.tsv.preW4.bak.${TS} (rollback path); split MUST conserve row count (no rows lost) |
| .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv W7 baseline ↔ W4-R3 successor rows | Per Pitfall 5: NEVER overwrite W7 row; append W4-R3 rows after the existing baseline (chain of valid post-Wave md5 values) |
| Multi-terminal git staging on GPFS ↔ explicit-path commits | Per `.planning/feedback_multi_terminal_staging.md`: never `git add .` / `-A` |
| Cowork-side audit decision (Carter human input) ↔ executor automated dispatch | Task 2 is checkpoint:human-verify; cannot proceed without explicit Carter resume-signal (RECLASS_OK / RECLASS_DIVERGENCE) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-TA-R3-W4-01 | E (Elevation of privilege) | Reclassification fired without Cowork-side approval | mitigate | Task 1 reads D-TA-R3-W4-GATE token; default SKIPPED; FIRES requires explicit Cowork-side write to ta-r3-CONTEXT.md; Task 2 is checkpoint:human-verify (autonomous: false) |
| T-TA-R3-W4-02 | T (Tampering) | tier_assignments.tsv rows lost during split | mitigate | Acceptance criterion: pre-W4 row count = post-W4 primary + HLA-fallback row count (conservation invariant); pre-W4 backup preserved at tier_assignments.tsv.preW4.bak.${TS} |
| T-TA-R3-W4-03 | T (Tampering) | md5_baseline.tsv W7 baseline overwritten | mitigate | Per Pitfall 5: append-only; Task 2 step 5 explicitly uses `cat >> ... <<EOF` (append redirect, never `>` overwrite); acceptance criterion verifies W7 row preserved |
| T-TA-R3-W4-04 | T (Tampering) | Systemic bookkeeping drift across multiple aggregators (plan-of-plans risk register row 5) | mitigate | Task 1 step 4 halts for human review when gate=FIRES; Carter inspects investigation TSV before Task 2 fires; if drift surfaces, Carter halts to multi-aggregator triage in separate phase |
| T-TA-R3-W4-05 | I (Information disclosure) | Implicit `git add .` could stage results_identity_ld/ (DEC-2026-04-25-01) | mitigate | All commits use explicit paths only |
| T-TA-R3-W4-06 | I (Information disclosure) | Honest-framing-lock manuscript edit | accept | OUT of phase scope per OSF amendment "What is not changing" |
</threat_model>

<verification>
- W4 gate read at task entry; default SKIPPED (Task 1 step 1)
- Investigation TSV always written (Task 1 step 2)
- If SKIPPED: D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded + W4 exits cleanly (Task 1 step 3)
- If FIRES: investigation halt recorded for human review (Task 1 step 4)
- Task 2 is checkpoint:human-verify (autonomous: false) — fires only after Carter resumes with HLA encoding pattern
- If Task 2 fires: tier_assignments.tsv split + HLA-fallback file created + downstream aggregators re-run + md5 successor rows appended to ta-sh2b3 W7 baseline (NEVER overwrite)
- D-TA-R3-W4-DEFERRED_TO_FOOTNOTE or D-TA-R3-W4-RECLASS_FIRED recorded
- Atomic commit landed
- Honest-framing-lock manuscript md5 unchanged through all tasks
</verification>

<success_criteria>
- W4 gate enforced at task entry per gate_condition frontmatter (DEFAULT SKIPPED; FIRES requires Cowork-side escalation)
- Investigation TSV always written; HLA encoding ambiguity enumerated
- If SKIPPED: D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded; on-disk file UNTOUCHED
- If FIRES + Carter resumes: tier_assignments.tsv split + HLA-fallback created; downstream aggregators re-run; W4-R3 successor md5 rows appended to ta-sh2b3-W7 baseline (NEVER overwrite)
- Honest-framing-lock manuscript md5 unchanged (63fd81385590ffc8d23d45a0f0598959)
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md` with:
- D1 W4 gate read + branch (SKIPPED/FIRES) recorded (PASS/WARN/FAIL)
- D2 Investigation TSV written with HLA encoding ambiguity enumeration (PASS/WARN/FAIL)
- D3 If SKIPPED: D-TA-R3-W4-DEFERRED_TO_FOOTNOTE recorded; on-disk file UNTOUCHED (PASS/WARN/FAIL)
- D4 If FIRES + Carter resumes: tier_assignments.tsv split + HLA-fallback created (PASS/WARN/FAIL)
- D5 If RECLASS_FIRED: row-count conservation invariant (pre = post primary + HLA-fallback) (PASS/WARN/FAIL)
- D6 If RECLASS_FIRED: downstream aggregators re-run (PASS/WARN/FAIL)
- D7 If RECLASS_FIRED: md5 successor rows appended to ta-sh2b3-W7 baseline (NEVER overwrite) (PASS/WARN/FAIL)
- Manuscript md5 invariant preservation (PASS/WARN/FAIL)
- Honest-framing-lock invariant preservation
- Total duration (~5 min if SKIPPED; ~30 min if RECLASS_FIRED)
</output>
