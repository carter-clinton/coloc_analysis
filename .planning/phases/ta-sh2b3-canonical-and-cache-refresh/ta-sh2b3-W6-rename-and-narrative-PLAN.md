---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 6
slug: W6-rename-and-narrative
type: execute
wave: 6
depends_on: ["W3", "W5"]
files_modified:
  - docs/manuscript/track_a_pivot.md  # → docs/manuscript/id-vs-ref-LD.md (git mv)
  - docs/manuscript/id-vs-ref-LD.md  # post-rename target + narrative atomic updates
  - .planning/amendments/TRACK-A-PIVOT.md  # → ID-VS-REF-LD-STRATEGY.md (git mv)
  - .planning/amendments/ID-VS-REF-LD-STRATEGY.md  # post-rename target
  - bin/build_track_a_submission_bundle.sh  # → bin/build_id_vs_ref_ld_submission_bundle.sh (git mv) + heredoc sed
  - bin/build_id_vs_ref_ld_submission_bundle.sh  # post-rename target with updated heredoc
  - src/R/figures/fig1a_pipeline_schematic.R  # reference fix-up
  - src/R/figures/fig1b_locus_panels.R  # reference fix-up
  - src/R/figures/fig2_cs_yield.R  # reference fix-up
  - src/R/figures/fig3_sh2b3_eur_collapse_forest.R  # reference fix-up
  - src/R/figures/fig5_variant_mech_scorecard.R  # reference fix-up
  - src/R/figures/fig_h3_ld_overlap_dose_response.R  # reference fix-up
  - src/R/figures/fig_s2_paired_fit_structural_inflation.R  # reference fix-up
  - src/R/aggregators/aggregate_per_trait_pair_and_hubs.R  # reference fix-up
  - src/R/aggregators/aggregate_table1_pleiotropic_loci.R  # reference fix-up
  - src/R/aggregators/aggregate_table3_admissible_pairs.R  # reference fix-up
  - .planning/STATE.md  # forward refs only
  - .planning/DECISIONS.md  # forward refs only
  - .planning/ROADMAP.md  # forward refs only
  - .planning/PROJECT.md  # forward refs only
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md  # cross-refs only (filename preserved per D-TA-06)
  - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md  # cross-refs only
  - .planning/amendments/AUDIT-REVIEW-2026-04-25.md  # cross-refs only
  - .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md  # cross-refs only
  - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md  # cross-refs only
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt  # NEW: content-anchor capture per checker iter 1 WARNING 3
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt  # NEW: post-rename content-anchor verification
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt  # NEW: pre-Wave-6 forbidden-token count baseline per checker iter 1 WARNING 5
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-PATH-PARAMETERIZATION
  - REQ-SUSIE-RSS-POLICY
  - REQ-PP.H4-THRESHOLD-SWEEP

must_haves:
  truths:
    - "git mv operations preserve file history at new paths (NOT rewriting git history per memory project_track_a_handle.md)"
    - "Honest-framing-lock chain anchors are CONTENT-BASED (not line-based per RESEARCH.md Pitfall 7); 4 anchors are: §3.4 SH2B3 case-study reframe (locked-scalar reference), Figure 2 caption SUPERSEDED block, Discussion §Identity-LD Inflation, Methods §Harmonization-Pipeline Diagnostics. All survive byte-identical content via grep-strip-line-numbers + sort + diff (per checker iter 1 WARNING 3)"
    - "All 17 forward-facing reference fix-ups land (R figure scripts + R aggregators + planning docs + amendment cross-refs)"
    - "~50 .planning/quick/*-PLAN.md / *-SUMMARY.md files NOT modified (historical record per memory project_track_a_handle.md)"
    - "TRACK-A-FROZEN-NUMBERS.md filename PRESERVED (Carter-flagged optional per D-TA-06; cross-refs inside it ARE updated)"
    - "Manuscript narrative atomic updates per D-TA-WAVE3-OUTCOME branch (a/b/c) + D-TA-Wave1-headline outcome materialized at Wave 5"
    - "Pivot-free language audit: future-facing artifacts use 'id-vs-ref-LD' framing; internal planning docs preserve 'pivot' for the 2026-04-22 strategic event only"
    - "Forbidden-token baseline captured pre-Wave-6 (revision/correction/cleanup/fix/audit count in track_a_pivot.md) — Sub-task 2.6 acceptance criterion verifies post-Wave-6 count ≤ baseline (per checker iter 1 WARNING 5)"
    - "Submission bundle build script's heredoc-generated README.md + CITATION.cff content updated (Pitfall 6 mitigation)"
  artifacts:
    - path: "docs/manuscript/id-vs-ref-LD.md"
      provides: "Renamed manuscript with narrative atomic updates per Wave-3 branch + Wave-5 frozen numbers"
      contains: "honest-framing-lock"
    - path: ".planning/amendments/ID-VS-REF-LD-STRATEGY.md"
      provides: "Renamed strategy doc"
    - path: "bin/build_id_vs_ref_ld_submission_bundle.sh"
      provides: "Renamed bundle builder with heredoc README + CITATION.cff updated to post-rename branding"
      contains: "id-vs-ref-LD.md"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt"
      provides: "Pre-rename content-anchor capture for 4 honest-framing-lock anchors (per checker iter 1 WARNING 3)"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt"
      provides: "Post-rename + post-narrative content-anchor capture; compared against _pre.txt with line numbers stripped"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt"
      provides: "Pre-Wave-6 grep -ciE forbidden-token count from track_a_pivot.md (per checker iter 1 WARNING 5)"
  key_links:
    - from: "docs/manuscript/track_a_pivot.md (pre-rename)"
      to: "docs/manuscript/id-vs-ref-LD.md (post-rename)"
      via: "git mv (preserves history)"
      pattern: "git mv docs/manuscript/track_a_pivot.md"
    - from: "Honest-framing-lock content phrases (4 anchors): §3.4 SH2B3 case-study, SUPERSEDED, Identity-LD Inflation, Harmonization-Pipeline Diagnostics"
      to: "post-rename file at id-vs-ref-LD.md"
      via: "grep -A 3 -nE content phrase + strip line numbers + diff (per checker iter 1 WARNING 3)"
      pattern: "honest_framing_anchors_(pre|post).txt"
    - from: "D-TA-WAVE3-OUTCOME branch + Wave-5 frozen numbers"
      to: "manuscript narrative atomic updates"
      via: "Methods/Results/Discussion/Limitations/Abstract/Conclusion-1/captions/tables"
      pattern: "{wave3_branch}.*PRIMARY_L"
    - from: "Pre-Wave-6 forbidden-token count in track_a_pivot.md"
      to: "Post-Wave-6 forbidden-token count in id-vs-ref-LD.md"
      via: "grep -ciE; baseline captured pre-edit"
      pattern: "forbidden_token_baseline.txt"
---

<objective>
Wave 6 — id-vs-ref-LD nickname rename + manuscript narrative atomic updates against Wave-5 frozen numbers + Wave-3 selected branch. Mechanical rename tasks fire FIRST (zero-narrative); narrative atomic updates fire AFTER. Each rename + narrative atomic update is its own commit. Per D-TA-Wave-6-timing: Wave 6 bundles rename + narrative because it already touches every file in scope.

Purpose: Two combined goals at the disk-then-narrative freeze point:
1. **Rename** (D-TA-06): align file paths with the locked manuscript title "Identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci" and `project_track_a_handle.md` memory. `TRACK-A-FROZEN-NUMBERS.md` filename preserved per Carter's flag.
2. **Narrative atomic updates**: write Methods + Results + Discussion + Limitations + Abstract + Conclusion-1 + captions + tables against the Wave-3 selected branch (a/b/c) + Wave-5 frozen numbers. Honest-framing-lock chain CONTENT phrases (4 anchors: §3.4 SH2B3 case-study reframe, Figure 2 caption SUPERSEDED block, Discussion §Identity-LD Inflation, Methods §Harmonization-Pipeline Diagnostics) preserved byte-identical via content-based capture (NOT line-based — line numbers shift under edits per RESEARCH.md Pitfall 7; this is the checker iter 1 WARNING 3 mitigation).

Output: Renamed files at new paths (history preserved); 17 forward-facing reference fix-ups; manuscript narrative aligned with frozen numbers + chosen branch; ~50 historical quick-task files UNTOUCHED (pre-2026-04-28 record preserved); content-anchor capture file at `honest_framing_anchors_pre.txt` (Task 1 step 0); forbidden-token baseline at `forbidden_token_baseline.txt` (Task 1 step 0).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@CLAUDE.md

<interfaces>
<!-- Wave 5 produced these — Wave 6 reads -->
- TRACK-A-FROZEN-NUMBERS.md L10 + L30 + L83 LIVE blocks updated
- results/track_a_aggregations/*.tsv refreshed
- results/multitrait/coloc_summary.tsv merged with R2 pairs
- D-TA-WAVE3-OUTCOME-{BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE} (Wave 3 selected branch)
- D-TA-Wave1-headline outcome (RECOMPUTE numerator vs PRESERVE-WITH-DISCLOSURE)

<!-- Honest-framing-lock anchors — CONTENT phrases per RESEARCH.md Pitfall 7 (NOT line numbers per checker iter 1 WARNING 3) -->

The 4 honest-framing-lock anchors are CONTENT-defined. Line numbers in the source manuscript may shift under edits; the anchors are identified by SECTION (per CONTEXT.md `<inputs>` section "Honest-framing-lock chain"). Mapping (verified 2026-04-29 via grep against current docs/manuscript/track_a_pivot.md):

| Anchor | Content phrase to grep | Verified line in track_a_pivot.md (2026-04-29) | Section context |
|--------|------------------------|----------------------------------------------------|-----------------|
| §3.4 SH2B3 case-study reframe | grep for `^### .*SH2B3.*case[- ]study` (section header) | Section header exists; spot-check via `grep -nE "^### .*SH2B3.*case[- ]study" docs/manuscript/track_a_pivot.md` | Results §SH2B3 case study (locked-scalar reference subsection) |
| Figure 2 caption SUPERSEDED block | grep for `SUPERSEDED` | L325 (Figure 2 caption: "SUPERSEDED 2026-04-25 per quick-260425-kki; narrow-validation 12/96 / 4.25× baseline preserved with full audit trail") | Figure 2 caption |
| Discussion §Identity-LD Inflation | grep for `Identity-LD Inflation` | L218: "### Identity-LD Inflation and Its Mechanism"; L220 + paragraph body | Discussion §Identity-LD Inflation |
| Methods §Harmonization-Pipeline Diagnostics | grep for `Harmonization-Pipeline Diagnostics` | L88 (Methods §header); L142, L176, L178, L198 (cross-references) | Methods §Harmonization-Pipeline Diagnostics |

The CONTEXT.md `<inputs>` section "Honest-framing-lock chain" identifies these anchors by SECTION not by line number. The original draft used line numbers L148/L295/L220/L90 which had already drifted from CONTEXT.md authoring (2026-04-28) by Wave 6 execution. Replaced with content-based capture (per checker iter 1 WARNING 3).

<!-- Rename-reference enumeration (RESEARCH.md verified 2026-04-29) -->
17 forward-facing files need token updates:
- docs/manuscript/track_a_pivot.md → id-vs-ref-LD.md (git mv)
- .planning/amendments/TRACK-A-PIVOT.md → ID-VS-REF-LD-STRATEGY.md (git mv)
- bin/build_track_a_submission_bundle.sh → bin/build_id_vs_ref_ld_submission_bundle.sh (git mv + heredoc sed)
- 7 R figure scripts in src/R/figures/ (comment-header references)
- 3 R aggregators in src/R/aggregators/ (comment-header references)
- .planning/STATE.md (forward refs)
- .planning/DECISIONS.md (forward refs)
- .planning/ROADMAP.md (forward refs)
- .planning/PROJECT.md (forward refs)
- 5 amendments (TRACK-A-FROZEN-NUMBERS, TRACK-A-AUDIT-RESPONSE-2026-04-26, AUDIT-REVIEW-2026-04-25, AUDIT-REVIEW-V2-2026-04-26, PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe)
- ~50 .planning/quick/*-PLAN.md / *-SUMMARY.md files: SKIP (historical record)

<!-- Forbidden-token baseline (per checker iter 1 WARNING 5) -->
Sub-task 2.6 (Abstract + Conclusion-1 update) acceptance criterion is "no NEW forbidden tokens (revision/correction/cleanup/fix/audit) introduced", which requires capturing pre-Wave-6 count BEFORE any edit. Captured at Task 1 step 0 to `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt`. Without this baseline the Sub-task 2.6 criterion is unverifiable.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Mechanical renames (git mv) + reference fix-ups across 17 forward-facing files (zero narrative changes); content-anchor capture; forbidden-token baseline capture</name>
  <files>
    docs/manuscript/id-vs-ref-LD.md  # from git mv
    .planning/amendments/ID-VS-REF-LD-STRATEGY.md  # from git mv
    bin/build_id_vs_ref_ld_submission_bundle.sh  # from git mv + heredoc sed
    src/R/figures/fig1a_pipeline_schematic.R
    src/R/figures/fig1b_locus_panels.R
    src/R/figures/fig2_cs_yield.R
    src/R/figures/fig3_sh2b3_eur_collapse_forest.R
    src/R/figures/fig5_variant_mech_scorecard.R
    src/R/figures/fig_h3_ld_overlap_dose_response.R
    src/R/figures/fig_s2_paired_fit_structural_inflation.R
    src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
    src/R/aggregators/aggregate_table1_pleiotropic_loci.R
    src/R/aggregators/aggregate_table3_admissible_pairs.R
    .planning/STATE.md
    .planning/DECISIONS.md
    .planning/ROADMAP.md
    .planning/PROJECT.md
    .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
    .planning/amendments/AUDIT-REVIEW-2026-04-25.md
    .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
    .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt  # NEW
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt  # NEW
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-06: id-vs-ref-LD nickname rename" (full per-path table; LOCKED)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"<inputs>" section "Honest-framing-lock chain" (anchors identified by SECTION, not line numbers)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Code Examples → Wave 6: Rename + reference fix-up enumeration" (verified 2026-04-29)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 7: Honest-framing-lock anchor line numbers shift" (CONTENT-based, not line-based)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 6: Wave 6 rename breaks build_track_a_submission_bundle.sh heredoc-generated content"
    - bin/build_track_a_submission_bundle.sh (lines 28, 69, 78, 137, 227-230, 250, 308-314, 475-477 per RESEARCH.md — heredoc references)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (cross-refs to track_a_pivot.md inside; filename itself NOT renamed per D-TA-06)
  </read_first>
  <action>
    **Step 0 (BEFORE git mv): Capture honest-framing-lock anchor CONTENT (per checker iter 1 WARNING 3) and forbidden-token baseline (per checker iter 1 WARNING 5).**

    The original draft used line-number capture (L148/L295/L220/L90 of track_a_pivot.md), but RESEARCH.md Pitfall 7 explicitly requires content-based anchors. Lines may have shifted between CONTEXT.md authoring (2026-04-28) and Wave 6 execution. Replace with content-grep capture:

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    SRC=docs/manuscript/track_a_pivot.md
    {
      echo "## ANCHOR 1: §3.4 SH2B3 case-study reframe (find by section header)"
      grep -A 3 -nE "^### .*SH2B3.*case[- ]study" "$SRC" | head -5
      echo ""
      echo "## ANCHOR 2: Figure 2 caption SUPERSEDED block"
      grep -B 1 -A 3 -n "SUPERSEDED" "$SRC" | head -15
      echo ""
      echo "## ANCHOR 3: Discussion §Identity-LD Inflation"
      grep -A 3 -nE "Identity-LD Inflation" "$SRC" | head -15
      echo ""
      echo "## ANCHOR 4: Methods §Harmonization-Pipeline Diagnostics"
      grep -A 3 -nE "Harmonization-Pipeline Diagnostics" "$SRC" | head -15
    } > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt
    cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt
    ```

    Each anchor section includes the matching content with line-number prefix (from `grep -n`); Task 2 sub-task 2.9 will strip the line-number prefix and compare CONTENT byte-identically.

    **Forbidden-token baseline (per checker iter 1 WARNING 5):**
    Capture the pre-Wave-6 count of forbidden framing tokens (revision/correction/cleanup/fix/audit) in track_a_pivot.md so Sub-task 2.6 can verify the post-Wave-6 count is ≤ baseline:

    ```bash
    grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/track_a_pivot.md > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt
    cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt
    echo "Pre-Wave-6 forbidden-token count baseline captured."
    ```

    NOTE: this baseline counts LINES containing these tokens via `-c`; many of these tokens may be legitimate (e.g., "Limitations bullet 5 ... known harmonized-TSV vs SuSiE-fit variant-ID mismatch that was structurally fixed mid-Stage-2" uses "fixed" / "fix"). The post-Wave-6 acceptance criterion is "no NEW such tokens introduced", i.e., post-count ≤ baseline.

    Execute renames in this exact order (atomic commit per rename + reference fix-up):

    **(1) Rename manuscript file:**
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git mv docs/manuscript/track_a_pivot.md docs/manuscript/id-vs-ref-LD.md
    ```

    **(2) Rename strategy doc:**
    ```bash
    git mv .planning/amendments/TRACK-A-PIVOT.md .planning/amendments/ID-VS-REF-LD-STRATEGY.md
    ```

    **(3) Rename bundle builder + heredoc sed pass (Pitfall 6 mitigation):**
    ```bash
    git mv bin/build_track_a_submission_bundle.sh bin/build_id_vs_ref_ld_submission_bundle.sh

    # Heredoc references inside the script (verified at lines 28, 69, 78, 137, 227-230, 250, 308-314, 475-477 per RESEARCH.md):
    # Replace track_a_pivot.md → id-vs-ref-LD.md and build_track_a_submission_bundle.sh → build_id_vs_ref_ld_submission_bundle.sh
    sed -i.bak 's|track_a_pivot\.md|id-vs-ref-LD.md|g; s|build_track_a_submission_bundle\.sh|build_id_vs_ref_ld_submission_bundle.sh|g' \
        bin/build_id_vs_ref_ld_submission_bundle.sh
    rm -f bin/build_id_vs_ref_ld_submission_bundle.sh.bak
    chmod +x bin/build_id_vs_ref_ld_submission_bundle.sh

    # Verify Pitfall 6 mitigation: no remaining stale tokens in the renamed script
    if grep -nE "track_a_pivot|build_track_a_submission_bundle" bin/build_id_vs_ref_ld_submission_bundle.sh; then
      echo "FAIL: stale tokens remain in bundle builder"
      exit 1
    fi
    ```

    **Single atomic commit for all 3 renames + the captured anchor + forbidden-token baseline files:**
    ```bash
    git add docs/manuscript/id-vs-ref-LD.md \
            .planning/amendments/ID-VS-REF-LD-STRATEGY.md \
            bin/build_id_vs_ref_ld_submission_bundle.sh \
            .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt \
            .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt
    git commit -m "docs(ta-sh2b3, W6-rename): git mv 3 files (manuscript + strategy + bundle builder) + heredoc sed (D-TA-06); content-anchor capture + forbidden-token baseline (checker iter 1 WARNINGs 3 + 5)"
    ```

    **(4) Reference fix-up across 7 R figure scripts + 3 R aggregators (comment-header references):**
    ```bash
    R_FILES=(
      src/R/figures/fig1a_pipeline_schematic.R
      src/R/figures/fig1b_locus_panels.R
      src/R/figures/fig2_cs_yield.R
      src/R/figures/fig3_sh2b3_eur_collapse_forest.R
      src/R/figures/fig5_variant_mech_scorecard.R
      src/R/figures/fig_h3_ld_overlap_dose_response.R
      src/R/figures/fig_s2_paired_fit_structural_inflation.R
      src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
      src/R/aggregators/aggregate_table1_pleiotropic_loci.R
      src/R/aggregators/aggregate_table3_admissible_pairs.R
    )
    for f in "${R_FILES[@]}"; do
      [ -f "$f" ] || { echo "MISSING: $f"; continue; }
      sed -i.bak \
        -e 's|track_a_pivot\.md|id-vs-ref-LD.md|g' \
        -e 's|TRACK-A-PIVOT\.md|ID-VS-REF-LD-STRATEGY.md|g' \
        "$f"
      rm -f "${f}.bak"
    done

    # Verify no remaining stale tokens in R scripts
    grep -lnE "track_a_pivot|TRACK-A-PIVOT" "${R_FILES[@]}" 2>/dev/null && \
      { echo "FAIL: stale tokens in R scripts"; exit 1; }

    git add "${R_FILES[@]}"
    git commit -m "refactor(ta-sh2b3, W6-rename): update 10 R script comment-headers to id-vs-ref-LD branding (D-TA-06)"
    ```

    **(5) Reference fix-up across .planning/ forward-facing docs:**
    ```bash
    PLANNING_FILES=(
      .planning/STATE.md
      .planning/DECISIONS.md
      .planning/ROADMAP.md
      .planning/PROJECT.md
    )
    for f in "${PLANNING_FILES[@]}"; do
      [ -f "$f" ] || continue
      # ONLY update forward-facing path tokens; preserve "pivot" language for the 2026-04-22 strategic event
      # i.e., update path references but NOT prose mentioning the strategic pivot itself
      sed -i.bak \
        -e 's|docs/manuscript/track_a_pivot\.md|docs/manuscript/id-vs-ref-LD.md|g' \
        -e 's|\.planning/amendments/TRACK-A-PIVOT\.md|.planning/amendments/ID-VS-REF-LD-STRATEGY.md|g' \
        -e 's|bin/build_track_a_submission_bundle\.sh|bin/build_id_vs_ref_ld_submission_bundle.sh|g' \
        "$f"
      rm -f "${f}.bak"
    done

    git add "${PLANNING_FILES[@]}"
    git commit -m "docs(ta-sh2b3, W6-rename): update 4 .planning/ forward refs to id-vs-ref-LD paths (D-TA-06)"
    ```

    **(6) Reference fix-up across 5 amendments (cross-refs only; filenames preserved):**
    ```bash
    AMENDMENT_FILES=(
      .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
      .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
      .planning/amendments/AUDIT-REVIEW-2026-04-25.md
      .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
      .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
    )
    for f in "${AMENDMENT_FILES[@]}"; do
      [ -f "$f" ] || continue
      # Update inline cross-refs ONLY; preserve filenames per D-TA-06 (TRACK-A-FROZEN-NUMBERS.md NOT renamed)
      sed -i.bak \
        -e 's|docs/manuscript/track_a_pivot\.md|docs/manuscript/id-vs-ref-LD.md|g' \
        -e 's|\.planning/amendments/TRACK-A-PIVOT\.md|.planning/amendments/ID-VS-REF-LD-STRATEGY.md|g' \
        -e 's|bin/build_track_a_submission_bundle\.sh|bin/build_id_vs_ref_ld_submission_bundle.sh|g' \
        "$f"
      rm -f "${f}.bak"
    done

    git add "${AMENDMENT_FILES[@]}"
    git commit -m "docs(ta-sh2b3, W6-rename): update 5 amendments cross-refs (filenames preserved per D-TA-06)"
    ```

    **(7) Verify .planning/quick/ historical record UNTOUCHED:**
    ```bash
    # Per memory project_track_a_handle.md: pre-2026-04-28 quick-task PLANs/SUMMARYs are HISTORICAL RECORD; NEVER rewrite
    QUICK_DIRTY=$(git diff --cached --name-only 2>/dev/null | grep -c "^\.planning/quick/")
    if [ "$QUICK_DIRTY" -gt 0 ]; then
      echo "FAIL: .planning/quick/ files staged. Per memory project_track_a_handle.md these are historical record."
      exit 1
    fi
    QUICK_MOD=$(git status --porcelain .planning/quick/ 2>/dev/null | wc -l)
    if [ "$QUICK_MOD" -gt 0 ]; then
      echo "WARN: .planning/quick/ files modified in working tree. Reverting:"
      git checkout -- .planning/quick/
    fi
    echo "PASS: .planning/quick/ historical record preserved"
    ```
  </action>
  <acceptance_criteria>
    - 3 git mv operations completed: `git log --diff-filter=R --name-status HEAD~5..HEAD | grep -c "^R"` returns ≥ 3.
    - `[ -f docs/manuscript/id-vs-ref-LD.md ]` AND `[ ! -f docs/manuscript/track_a_pivot.md ]`.
    - `[ -f .planning/amendments/ID-VS-REF-LD-STRATEGY.md ]` AND `[ ! -f .planning/amendments/TRACK-A-PIVOT.md ]`.
    - `[ -x bin/build_id_vs_ref_ld_submission_bundle.sh ]` AND `[ ! -f bin/build_track_a_submission_bundle.sh ]`.
    - Pitfall 6 mitigated: `grep -cE "track_a_pivot|build_track_a_submission_bundle" bin/build_id_vs_ref_ld_submission_bundle.sh` returns 0.
    - 10 R scripts have updated cross-refs: `grep -cE "track_a_pivot|TRACK-A-PIVOT" src/R/figures/*.R src/R/aggregators/*.R 2>/dev/null` returns 0.
    - 4 .planning forward-facing files updated: `grep -cE "track_a_pivot|TRACK-A-PIVOT|build_track_a_submission_bundle" .planning/STATE.md .planning/DECISIONS.md .planning/ROADMAP.md .planning/PROJECT.md 2>/dev/null` returns 0.
    - 5 amendments cross-refs updated (cross-refs to manuscript/strategy/bundle paths only): `grep -cE "docs/manuscript/track_a_pivot|build_track_a_submission_bundle" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md .planning/amendments/AUDIT-REVIEW-2026-04-25.md .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md 2>/dev/null` returns 0.
    - `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` filename PRESERVED (NOT renamed): `[ -f .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ]`.
    - `.planning/quick/` UNTOUCHED: `git status --porcelain .planning/quick/ | wc -l` returns 0.
    - 4 atomic commits landed (one per rename batch + 3 reference-fix-up batches).
    - **Honest-framing-lock content-anchor capture file exists with all 4 anchors (per checker iter 1 WARNING 3):**
      `[ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt ]` AND
      `grep -c "## ANCHOR" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt` returns 4.
    - **Forbidden-token baseline captured (per checker iter 1 WARNING 5):**
      `[ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt ]` AND
      the file contains a single integer line (numeric count): `[[ "$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt)" =~ ^[0-9]+$ ]]`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f docs/manuscript/id-vs-ref-LD.md ] && [ ! -f docs/manuscript/track_a_pivot.md ] && [ -f .planning/amendments/ID-VS-REF-LD-STRATEGY.md ] && [ ! -f .planning/amendments/TRACK-A-PIVOT.md ] && [ -x bin/build_id_vs_ref_ld_submission_bundle.sh ] && [ ! -f bin/build_track_a_submission_bundle.sh ] && [ "$(grep -cE 'track_a_pivot|build_track_a_submission_bundle' bin/build_id_vs_ref_ld_submission_bundle.sh 2>/dev/null)" -eq 0 ] && [ "$(grep -lE 'track_a_pivot|TRACK-A-PIVOT' src/R/figures/*.R src/R/aggregators/*.R 2>/dev/null | wc -l)" -eq 0 ] && [ -f .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ] && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt ] && [ "$(grep -c '## ANCHOR' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt)" -eq 4 ] && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt ] && [[ "$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt)" =~ ^[0-9]+$ ]] && echo PASS</automated>
  </verify>
  <done>
    3 file renames complete via `git mv` (history preserved); heredoc references in renamed bundle builder updated (Pitfall 6 mitigated); 10 R scripts + 4 .planning docs + 5 amendments cross-refs updated; `.planning/quick/` historical record UNTOUCHED. Content-anchor capture file at honest_framing_anchors_pre.txt with all 4 anchors (CONTENT-based, not line-based per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7). Forbidden-token baseline at forbidden_token_baseline.txt (per checker iter 1 WARNING 5; enables Sub-task 2.6 acceptance verification). 4 atomic commits landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Manuscript narrative atomic updates per D-TA-WAVE3-OUTCOME branch + Wave-5 frozen numbers; honest-framing-lock content-anchor verification (post-edit)</name>
  <files>
    docs/manuscript/id-vs-ref-LD.md
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt  # NEW
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-WAVE3-OUTCOME-{BRANCH}" (drives narrative branch)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave1-headline" (drives whether 51/96 recomputes vs preserves with disclosure)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt (captured pre-rename in Task 1 step 0; CONTENT phrases per checker iter 1 WARNING 3)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt (captured pre-rename in Task 1 step 0; per checker iter 1 WARNING 5)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Wave-5 updated LIVE blocks; source of truth for all numerics)
    - docs/manuscript/id-vs-ref-LD.md (post-rename manuscript; current state)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv (per-pair PP.H4 from Wave 2)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv (per-trait per-L convergence)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 7: Honest-framing-lock anchor line numbers shift" (verify by content phrase, NOT line number)
    - memory feedback_original_research_framing.md (NEVER use revision/audit/cleanup framing)
  </read_first>
  <action>
    Read the Wave-3 selected branch token and Wave-1 headline outcome:
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    BRANCH=$(grep -oE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" \
              .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | head -1 | \
              sed 's/D-TA-WAVE3-OUTCOME-//')
    echo "Wave 3 branch: $BRANCH"

    HEADLINE_DECISION=$(grep -A 5 "D-TA-Wave1-headline" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | grep -oE "(RECOMPUTE|PRESERVE-WITH-DISCLOSURE)" | head -1)
    echo "Headline decision: $HEADLINE_DECISION"
    ```

    Use the Edit tool (NOT sed; whitespace-fragile) to update each of the following manuscript sections in `docs/manuscript/id-vs-ref-LD.md`. Each section gets its own atomic commit with `docs(ta-sh2b3, W6-narrative): update {section} per {branch} + Wave-5 frozen numbers` as the commit message.

    **Sub-task 2.1: Methods §Harmonization-Pipeline Diagnostics (anchor: "Harmonization-Pipeline Diagnostics" content phrase)**
    Locate the Methods §Harmonization-Pipeline Diagnostics section via `grep -nE "^### .*Harmonization-Pipeline Diagnostics" docs/manuscript/id-vs-ref-LD.md` (line number may have drifted since L90 was originally captured). Update with Wave-4 post-refresh too_few_snps + success counts (read from `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` L30 LIVE block). PRESERVE the content-anchor phrases verbatim (look up captured anchors in `honest_framing_anchors_pre.txt`).
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update Methods §Harmonization-Pipeline Diagnostics for post-W4 numbers`.

    **Sub-task 2.2: Methods §Fine-Mapping Configuration**
    Add the Wave-1 L-sweep results (per-trait per-L convergence outcomes from `ta-sh2b3-W1-convergence-report.tsv`). Cite Zou et al. 2022 §Discussion `n_CS << L` non-saturation criterion.
    Add a Supplementary Methods table reference: rows = trait (BMI/HTN/stroke); columns = L=15 / L=20 / L=30 with `n_CS` + `convergence_status` per cell.
    Atomic commit: `docs(ta-sh2b3, W6-narrative): add Methods §Fine-Mapping Configuration L-sweep results (D-TA-02)`.

    **Sub-task 2.3: Results §SH2B3 case study (anchor: §3.4 SH2B3 case-study reframe content phrase)**
    Locate the Results §SH2B3 case study section via `grep -nE "^### .*SH2B3.*case[- ]study" docs/manuscript/id-vs-ref-LD.md` (line number drifted from L148).
    Branch on $BRANCH:
    - BRANCH_A_COLLAPSE: write "BMI-HTN canonical claim does NOT survive matched-LD (PP.H4 = {value} < 0.5); flagship demonstrated collapse." Cite Wave 2 R2 outputs at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json`.
    - BRANCH_B_PARTIAL: write "BMI-HTN PP.H4 = {value} ∈ [0.5, 0.8); calibration finding — magnitude of inflation, not categorical."
    - BRANCH_C_SURVIVE: write "BMI-HTN canonical claim survives under matched-LD (PP.H4 = {value} ≥ 0.8); SH2B3 anchor flips from collapse to validated."
    PRESERVE the §3.4 SH2B3 case-study reframe content-anchor (cross-check against `honest_framing_anchors_pre.txt` post-edit via Sub-task 2.9 below).
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update §SH2B3 case-study per ${BRANCH}`.

    **Sub-task 2.4: Discussion §Identity-LD Inflation (anchor: "Identity-LD Inflation" content phrase)**
    Locate via `grep -nE "Identity-LD Inflation" docs/manuscript/id-vs-ref-LD.md` (line number drifted from L220).
    Branch on $BRANCH:
    - BRANCH_A_COLLAPSE: §Identity-LD Inflation is the LOAD-BEARING section; emphasize the canonical-claim collapse demonstration.
    - BRANCH_B_PARTIAL: §Identity-LD Inflation pivots to "magnitude of inflation, not categorical".
    - BRANCH_C_SURVIVE: §Identity-LD Inflation narrows; FTO Tier-C 0.3099 disclosure becomes load-bearing fallback.
    PRESERVE the content-anchor verbatim.
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update Discussion §Identity-LD Inflation per ${BRANCH}`.

    **Sub-task 2.5: Limitations bullet 5 + bullet new (cache invalidation)**
    Update bullet 5 with the post-refresh too_few_snps drop (from {baseline} to {post_refresh}). Reference the cache invalidation as a methodological hygiene fix (NOT new analysis; D-TA-Cache-OSF deviation-log only).
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update Limitations bullet 5 with cache-refresh outcome`.

    **Sub-task 2.6: Abstract + Conclusion-1 (DEPENDS on D-TA-Wave1-headline outcome) + forbidden-token baseline check (per checker iter 1 WARNING 5):**
    Branch on $HEADLINE_DECISION:
    - RECOMPUTE: update Abstract + §Headline + Conclusion-1 with new numerator (e.g., 51/96 → 54/96 if all 3 newly converge).
    - PRESERVE-WITH-DISCLOSURE: keep 51/96; add explicit disclosure note ("3 of 5 SH2B3 EUR per-trait fits at L=10 non-converged; sweep at L ∈ {15, 20, 30} converged X of 3 at PRIMARY_L").
    AND branch on $BRANCH for the SH2B3 anchor framing (collapse / partial / survive language).

    **Forbidden-token baseline verification (per checker iter 1 WARNING 5):**
    ```bash
    BASELINE=$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt)
    POST=$(grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md)
    echo "Pre-Wave-6 forbidden-token count: $BASELINE"
    echo "Post-Wave-6 forbidden-token count: $POST"
    if [ "$POST" -gt "$BASELINE" ]; then
      echo "FAIL: Forbidden framing tokens increased from $BASELINE to $POST during Wave 6 narrative edits."
      echo "      Manuscript may have introduced 'revision' / 'correction' / 'cleanup' / 'fix' / 'audit' framing — review and remove."
      grep -niE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md
      exit 1
    fi
    echo "PASS: forbidden-token count $POST ≤ baseline $BASELINE (no NEW such tokens introduced)"
    ```
    NOTE: The baseline includes legitimate uses of "fix" / "fixed" (e.g., "structurally fixed mid-Stage-2"); the criterion is "≤ baseline", not "0". Some legitimate uses may also need REPLACEMENT during narrative edits (e.g., changing "the fix" → "the variant-ID matcher update"); if so, the post-count may DROP below baseline, which is also fine.
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update Abstract + Conclusion-1 per ${HEADLINE_DECISION} + ${BRANCH} (forbidden-token check ≤ baseline)`.

    **Sub-task 2.7: Figure 2 caption (anchor: "SUPERSEDED" content phrase) + Figure 3 caption + Fig S7 caption + Table 3 SH2B3 rows + Table 4 (n_attempted / n_failed columns):**
    Locate Figure 2 caption SUPERSEDED block via `grep -nB 1 -A 3 "SUPERSEDED" docs/manuscript/id-vs-ref-LD.md`.
    - SUPERSEDED block: PRESERVE verbatim (content-anchor).
    - Fig 3 caption: per $BRANCH, update PP.H4 references for the 9 new SH2B3 EUR pairs.
    - Fig S7 caption: update against post-Wave-4 dose-response numerics.
    - Table 3 SH2B3 rows: add 9 new rows per `coloc_summary.tsv` (post-Wave-5 merge); symmetrize with FTO_16q12.
    - Table 4: update n_attempted = 1274 (or post-refresh count) + n_failed = post-Wave-4 too_few_snps.
    Atomic commit: `docs(ta-sh2b3, W6-narrative): update figure captions + Tables 3/4 per Wave-5 frozen numbers`.

    **Sub-task 2.8: Pivot-free language audit (record outcome in CONTEXT.md):**
    ```bash
    grep -nE "Track A pivot|track[ -]a[ -]pivot" docs/manuscript/id-vs-ref-LD.md \
        bin/build_id_vs_ref_ld_submission_bundle.sh \
        src/R/figures/*.R src/R/aggregators/*.R \
        2>/dev/null | grep -v "^\.planning/quick/"
    ```
    Any remaining "pivot" tokens in FUTURE-FACING (non-quick) artifacts are violations. Fix them via Edit. Internal planning docs (.planning/STATE.md, .planning/DECISIONS.md, .planning/amendments/) MAY retain "pivot" for the 2026-04-22 strategic event itself — that is intentional per D-TA-06.
    Append outcome to CONTEXT.md:
    ```markdown
    ### D-TA-Wave6-pivot-free-audit: Pivot-free language audit outcome (Wave 6)

    **Recorded:** {timestamp}

    **Future-facing artifacts:** {N} files audited; {0|N} remaining "pivot" tokens (must be 0 for FUTURE artifacts; M for intentional internal-planning event refs).

    **Internal planning docs:** {K} occurrences of "pivot" preserved for the 2026-04-22 strategic event reference (intentional per D-TA-06).
    ```
    Atomic commit: `docs(ta-sh2b3, W6-narrative): record pivot-free language audit outcome (D-TA-06)`.

    **Sub-task 2.9: Honest-framing-lock anchor verification — CONTENT-based, not line-based (per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7):**

    The original draft compared anchors by line number (L148/L295/L220/L90), but those line numbers had ALREADY drifted by Wave 6 execution and would drift further during the narrative edits in Sub-tasks 2.1–2.7. The correct verification is content-based:

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    DST=docs/manuscript/id-vs-ref-LD.md
    {
      echo "## ANCHOR 1: §3.4 SH2B3 case-study reframe (find by section header)"
      grep -A 3 -nE "^### .*SH2B3.*case[- ]study" "$DST" | head -5
      echo ""
      echo "## ANCHOR 2: Figure 2 caption SUPERSEDED block"
      grep -B 1 -A 3 -n "SUPERSEDED" "$DST" | head -15
      echo ""
      echo "## ANCHOR 3: Discussion §Identity-LD Inflation"
      grep -A 3 -nE "Identity-LD Inflation" "$DST" | head -15
      echo ""
      echo "## ANCHOR 4: Methods §Harmonization-Pipeline Diagnostics"
      grep -A 3 -nE "Harmonization-Pipeline Diagnostics" "$DST" | head -15
    } > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt
    cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt
    ```

    Compare CONTENT byte-identically (line numbers may shift; CONTENT must match):
    ```bash
    # Strip the line-number prefix from grep -n output (format: "NN:line content" → "line content"); sort; diff
    diff <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt | sort) \
         <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt | sort)
    DIFF_RC=$?
    if [ "$DIFF_RC" -ne 0 ]; then
      echo "FAIL: honest-framing-lock anchors NOT byte-identical pre vs post Wave 6"
      echo "      Some anchor content was modified during narrative edits (Sub-tasks 2.1, 2.3, 2.4, 2.7)."
      echo "      Restore the verbatim content from honest_framing_anchors_pre.txt before re-attempting Sub-task 2.9."
      exit 1
    fi
    echo "PASS: all 4 honest-framing-lock content anchors preserved byte-identical (Pitfall 7 + checker iter 1 WARNING 3 mitigation)"
    ```

    The key insight: `grep -v '^[0-9]*:'` strips the leading line-number prefix from `grep -n` output. After stripping, ONLY the content remains. Sorting both and diffing yields zero output if the content is byte-identical. Line numbers may shift in either file (and they DO shift — pre-rename to post-rename to post-narrative); content must match.

    NOTE: The grep -A 3 in Step 0 + Sub-task 2.9 captures 3 lines AFTER each match. If a narrative edit added/removed text WITHIN the anchor section's first ~3 lines, the match window content would change. This is intentional: the anchor's IMMEDIATE context is what we lock. Edits to surrounding paragraphs (e.g., Sub-task 2.4 Discussion §Identity-LD Inflation paragraph body changes) are EXPECTED and only the anchor sentence itself is locked. If executor finds the diff fails, the executor must inspect which anchor's first 4 lines drifted and either (a) revert that specific change if it's accidental anchor-overwriting, or (b) re-grep with `-A 1` (anchor sentence only) to narrow the comparison window.

    **Sub-task 2.10: Run verification harness for Wave 6 (C13):**
    ```bash
    bin/verify_ta_sh2b3_phase.sh --wave 6
    ```
    C13 must emit PASS.
  </action>
  <acceptance_criteria>
    - Manuscript file at post-rename path: `[ -f docs/manuscript/id-vs-ref-LD.md ]` AND `[ ! -f docs/manuscript/track_a_pivot.md ]`.
    - Branch-specific narrative present: `grep -E "(does NOT survive|magnitude of inflation|survives under matched-LD)" docs/manuscript/id-vs-ref-LD.md` returns ≥ 1 hit consistent with the chosen $BRANCH.
    - Wave-5 frozen numbers cited in Methods §Harmonization-Pipeline Diagnostics (post-refresh too_few_snps): `grep -E "1,?274|too_few_snps" docs/manuscript/id-vs-ref-LD.md` returns ≥ 1 hit.
    - L-sweep results cited in Methods §Fine-Mapping Configuration: `grep -E "L ∈ \{15,?\\s?20,?\\s?30\\}|L-sweep" docs/manuscript/id-vs-ref-LD.md` returns ≥ 1 hit.
    - **Honest-framing-lock content anchors preserved (per checker iter 1 WARNING 3):** `[ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt ]` AND content diff (with line numbers stripped) is empty:
      ```
      diff <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt | sort) \
           <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt | sort)
      ```
      returns exit 0 with empty stdout.
    - C13 PASS from verification harness.
    - **Forbidden-token count ≤ baseline (per checker iter 1 WARNING 5):**
      ```
      BASELINE=$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt)
      POST=$(grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md)
      [ "$POST" -le "$BASELINE" ] || exit 1
      ```
    - Pivot-free audit: `D-TA-Wave6-pivot-free-audit` recorded in CONTEXT.md.
    - 7+ atomic commits landed (one per sub-task, plus pivot-free audit commit).
    - C13 from `bin/verify_ta_sh2b3_phase.sh --wave 6` emits PASS.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f docs/manuscript/id-vs-ref-LD.md ] && grep -qE "(does NOT survive|magnitude of inflation|survives under matched-LD)" docs/manuscript/id-vs-ref-LD.md && grep -qE "1,?274|too_few_snps" docs/manuscript/id-vs-ref-LD.md && grep -qE "L ∈ \{15.*20.*30\}|L-sweep" docs/manuscript/id-vs-ref-LD.md && grep -q "D-TA-Wave6-pivot-free-audit:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt ] && diff <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_pre.txt | sort) <(grep -v '^[0-9]*:' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/honest_framing_anchors_post.txt | sort) > /dev/null 2>&1 && BASELINE=$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/forbidden_token_baseline.txt) && POST=$(grep -ciE "(revision|correction|cleanup|fix|audit)" docs/manuscript/id-vs-ref-LD.md) && [ "$POST" -le "$BASELINE" ] && bin/verify_ta_sh2b3_phase.sh --wave 6 2>/dev/null | jq -e 'select(.check=="C13" and .status=="PASS")' > /dev/null && echo PASS</automated>
  </verify>
  <done>
    Manuscript narrative atomic updates complete per Wave-3 branch + Wave-5 frozen numbers; honest-framing-lock chain at all 4 CONTENT anchors preserved (per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7: content-based via grep-strip-line-numbers + sort + diff, not line-based); forbidden-token count ≤ baseline (per checker iter 1 WARNING 5); pivot-free language audit recorded; ≥7 atomic commits landed (Methods, Fine-Mapping Config, §SH2B3 case-study, Discussion §Identity-LD Inflation, Limitations, Abstract+Conclusion-1, captions+tables, pivot-free audit). C13 PASS. Verifies C13 in VALIDATION.md.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pre-rename git history ↔ post-rename file path | git mv preserves history (`git log --follow id-vs-ref-LD.md` shows full history); per memory project_track_a_handle.md, NEVER rewrite git history |
| Honest-framing-lock anchor CONTENT ↔ Wave 6 narrative edits | Pitfall 7 + checker iter 1 WARNING 3: anchors are content-based, NOT line-based; verify by grep -v '^[0-9]*:' + sort + diff, not by line number |
| Submission bundle heredoc-generated content ↔ rename | Pitfall 6: rename mechanics don't introspect heredoc strings; explicit sed pass on renamed bundle script required |
| Future-facing prose ↔ internal planning prose | D-TA-06: future-facing drops "pivot"; internal planning may keep "pivot" for the 2026-04-22 strategic event |
| Forbidden-token baseline (pre-Wave-6) ↔ post-Wave-6 count | per checker iter 1 WARNING 5: baseline captured in Task 1 step 0; Sub-task 2.6 acceptance verifies post ≤ baseline |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-03 | T (Tampering) | Honest-framing-lock chain at 4 content anchors | mitigate | Task 1 step 0 captures anchor CONTENT pre-rename via grep -A 3 -nE on §3.4 SH2B3 case-study + SUPERSEDED + Identity-LD Inflation + Harmonization-Pipeline Diagnostics; Task 2 sub-task 2.9 verifies post-edit byte-identical (line numbers stripped via `grep -v '^[0-9]*:'`); per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7 |
| T-PROCESS-02 | I (Information disclosure) | `.planning/quick/` historical record (~50 files; pre-2026-04-28 commits) | mitigate | Task 1 step 7 explicit safeguard: `git status --porcelain .planning/quick/` returns 0 before any commit; revert any accidental modifications |
| T-PROCESS-01 | T (Tampering) | Bundle script heredoc-generated content (Pitfall 6) | mitigate | Task 1 step 3 sed pass + grep verification: zero `track_a_pivot|build_track_a_submission_bundle` tokens remain in renamed script |
| T-PROCESS-04 | T (Tampering) | TRACK-A-FROZEN-NUMBERS.md filename (D-TA-06: PRESERVED) | mitigate | Task 1 acceptance criterion: `[ -f .planning/amendments/TRACK-A-FROZEN-NUMBERS.md ]` (NOT renamed); only cross-refs inside are updated |
| T-PROCESS-05 | T (Tampering) | Forbidden framing tokens (revision/correction/cleanup/fix/audit) introduced during narrative edits | mitigate | Task 1 step 0 captures pre-Wave-6 baseline count to forbidden_token_baseline.txt; Task 2 Sub-task 2.6 acceptance criterion: post-count ≤ baseline (per checker iter 1 WARNING 5) |
</threat_model>

<verification>
- 3 file renames complete via `git mv` (Task 1)
- Pitfall 6 mitigated (Task 1, heredoc sed)
- 17 forward-facing reference fix-ups complete (Task 1)
- ~50 .planning/quick/ files UNTOUCHED (Task 1)
- TRACK-A-FROZEN-NUMBERS.md filename PRESERVED (Task 1)
- Honest-framing-lock CONTENT anchors captured pre-rename (Task 1 step 0; per checker iter 1 WARNING 3)
- Forbidden-token baseline captured pre-rename (Task 1 step 0; per checker iter 1 WARNING 5)
- 7+ narrative atomic-update commits landed (Task 2)
- 4 anchor content phrases preserved post-edit via grep-strip-line-numbers + sort + diff (Task 2 sub-task 2.9 + checker iter 1 WARNING 3)
- Forbidden-token count ≤ baseline post-edit (Task 2 Sub-task 2.6 + checker iter 1 WARNING 5)
- Pivot-free language audit recorded (Task 2)
- C13 PASS (Task 2)
- ≥10 atomic commits landed in Wave 6 (4 from Task 1 + 7+ from Task 2)
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C13** Honest-framing-lock anchors preserved byte-identical at 4 CONTENT phrases (NOT line numbers per checker iter 1 WARNING 3) — Task 2 sub-task 2.9
</verification_criteria>

<success_criteria>
- 3 file renames via `git mv` complete (manuscript + strategy doc + bundle builder)
- 17 forward-facing reference fix-ups land (R figures + R aggregators + .planning docs + amendments cross-refs)
- ~50 .planning/quick/ historical record files UNTOUCHED
- TRACK-A-FROZEN-NUMBERS.md filename PRESERVED (Carter-flagged optional per D-TA-06)
- Submission bundle heredoc references updated (Pitfall 6)
- Manuscript narrative atomic updates per D-TA-WAVE3-OUTCOME branch + Wave-5 frozen numbers
- 4 honest-framing-lock content anchors preserved (per checker iter 1 WARNING 3 + RESEARCH.md Pitfall 7: content-based grep + strip-line-numbers + sort + diff)
- Forbidden-token count ≤ pre-Wave-6 baseline (per checker iter 1 WARNING 5)
- Pivot-free language audit recorded
- C13 PASS
- ≥10 atomic commits landed
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W6-rename-and-narrative-SUMMARY.md` with:
- D1 rename completeness (3 git mv operations + heredoc sed)
- D2 reference fix-up completeness (17 forward-facing files)
- D3 historical record preservation (~50 .planning/quick/ untouched)
- D4 TRACK-A-FROZEN-NUMBERS.md preservation (filename intact, cross-refs updated)
- D5 narrative atomic update completeness per branch (sections updated, frozen numbers cited)
- D6 honest-framing-lock anchor preservation (4 CONTENT anchors verified pre vs post via grep-strip-line-numbers + sort + diff; C13 PASS); cross-reference checker iter 1 WARNING 3 mitigation
- D7 pivot-free language audit outcome (future-facing artifacts clean; internal docs preserve event refs); cross-reference forbidden-token baseline check (checker iter 1 WARNING 5)
- Wave 7 GO status (must be GO with all renames + narrative complete for closeout to fire)
</output>
