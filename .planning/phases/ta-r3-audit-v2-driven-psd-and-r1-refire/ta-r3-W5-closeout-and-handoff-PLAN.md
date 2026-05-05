---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 5
slug: W5-closeout-and-handoff
type: execute
wave: 5
depends_on: ["W1", "W2", "W3", "W4"]
files_modified:
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv  # successor rows for files whose md5 shifted in W1/W2/W3/W4 (NEVER overwrite W7 row)
  - .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md
  - .planning/STATE.md  # GATED on Terminal A no longer active on m3 (per multi-terminal-staging memory)
  - .planning/ROADMAP.md  # mark phase COMPLETE
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "ta-r3-VERIFICATION.md exists with PASS/WARN/FAIL JSON-style entries for dimensions D1-DN (mirroring ta-sh2b3-VALIDATION.md format), covering all wave outcome branches recorded in ta-r3-CONTEXT.md"
    - "Successor md5 rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv for any files whose md5 shifted in W1-W4 (coloc_summary.tsv post-W2/W3, tier_assignments.tsv if W4 fired); W7 baseline rows preserved per Pitfall 5"
    - "Cowork-side handoff brief written at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md listing branches landed, outcome each ticket fell into, commit hashes, LSF job IDs, md5 invariants, artifact zip path"
    - "Phase commit hash range recorded in handoff brief (first..last from `git log --oneline`)"
    - "All 4 W1 outcome branches enumerated in handoff brief; all 2 W2 outcome branches enumerated; W3 + W4 gate dispositions enumerated"
    - "OSF amendment record URL referenced; OSF outcome-branch follow-up update prepared (per OSF amendment §Note on outcome-branch verification follow-up)"
    - "STATE.md update gated on Terminal A NOT active on m3 path (per .planning/feedback_multi_terminal_staging.md): pre-write check verifies absence of an `m3-*` lock file or mid-quick-task indicator. If Terminal A active, STATE.md write deferred to a follow-up /gsd-quick task; phase still closes via ROADMAP.md status update."
    - "ROADMAP.md Track-A-R3-audit-v2-driven-psd-and-r1-refire status field updated to COMPLETE with closure date + bundle/handoff path references"
    - "docs/manuscript/id-vs-ref-LD.md md5 unchanged (63fd81385590ffc8d23d45a0f0598959; honest-framing-lock invariant preserved through all 5 waves)"
    - "Multi-terminal git staging: explicit `git add <path>` only per .planning/feedback_multi_terminal_staging.md"
  artifacts:
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md"
      provides: "Phase-wide PASS/WARN/FAIL JSON evidence for dimensions D1-DN (mirrors ta-sh2b3-VALIDATION.md format)"
      contains: "D1\\|D2\\|D3\\|D4\\|D5\\|D6\\|D7"
    - path: ".planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md"
      provides: "Cowork-side handoff brief: branches landed + commit range + LSF job IDs + md5 invariants + artifact paths"
      contains: "BRANCH_PSD"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv"
      provides: "Updated md5 baseline with W1-W4 successor rows (W7 baseline preserved; chain of valid post-Wave md5 values)"
      contains: "ta-r3-W"
    - path: ".planning/ROADMAP.md"
      provides: "Phase status updated to COMPLETE"
      contains: "Track-A-R3-audit-v2-driven-psd-and-r1-refire"
  key_links:
    - from: "Wave 1-4 outcome branches (ta-r3-CONTEXT.md)"
      to: "ta-r3-VERIFICATION.md PASS/WARN/FAIL JSON"
      via: "verification dimensions D1-DN"
      pattern: "D[1-9]+"
    - from: "Files whose md5 shifted in W1-W4"
      to: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (successor rows appended)"
      via: "Append (NEVER overwrite) per Pitfall 5"
      pattern: "ta-r3-W[1-4]"
    - from: "Phase outputs (W1-W4 SUMMARYs + bundle paths)"
      to: ".planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md"
      via: "Cowork-side handoff for v5 *Genome Medicine* submission bundle ship"
      pattern: "HPC_DELIVERABLE"
    - from: "STATE.md write"
      to: "Terminal A m3 lock file absence check"
      via: "explicit pre-write gate: `[ ! -f .claude/m3-*.lock ] && [ ! -f .planning/quick/*m3*/IN_PROGRESS ]`"
      pattern: "m3-.*lock"
---

<objective>
Wave 5 — Phase closeout. Aggregator refresh (if W2 outcome was BRANCH_R1_BUG; new PP rows mean Table 3 + summary statistics shift). Freeze new md5 baseline by appending successor rows to `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` for any files whose md5 shifted in W1/W2/W3/W4 (NEVER overwrite the W7 baseline row per Pitfall 5). Produce `ta-r3-VERIFICATION.md` with PASS/WARN/FAIL JSON-style evidence per dimension. Write the Cowork-side handoff brief listing branches landed, outcome each ticket fell into, commit hashes, LSF job IDs, md5 invariants, and the artifact zip path.

Update STATE.md to mark phase closed (GATED on Terminal A NOT active on m3 path; if active, defer STATE.md write to follow-up /gsd-quick — phase still closes via ROADMAP.md status update). Update ROADMAP.md Track-A-R3-audit-v2-driven-psd-and-r1-refire entry status to COMPLETE.

Purpose: Hand off the substrate the Cowork-side v5 manuscript revision (audit items A1, A2, A3, A6-stats, A7, A8, A9 — explicitly OUT of this phase's scope) draws on. This wave gates-out the phase. After W5 closeout, a separate Cowork-side session ships the v5 *Genome Medicine* submission bundle.

Output: ta-r3-VERIFICATION.md with PASS/WARN/FAIL evidence; appended successor md5 rows in ta-sh2b3-W7 baseline; Cowork handoff brief at `.planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md`; ROADMAP.md status COMPLETE; STATE.md updated (or deferral note if Terminal A active).
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
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W1-sh2b3-psd-regularized-refit-SUMMARY.md
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md
@.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W4-tier-assignments-hla-reconcile-SUMMARY.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
@CLAUDE.md

<interfaces>
<!-- W1-W4 produced these — W5 reads -->
- D-TA-R3-W1-BRANCH_PSD_<FIRM|PARTIAL|COLLAPSE|NON_CONVERGE>
- D-TA-R3-W2-BRANCH_R1_<BUG|STRUCTURAL>
- D-TA-R3-W3-OUTCOME (FIRES or DEFERRED-ON-W1-OUTCOME)
- D-TA-R3-W4-DEFERRED_TO_FOOTNOTE (DEFAULT) or D-TA-R3-W4-RECLASS_FIRED
- ta-r3-W2-post_refire_md5.txt (post-W2 coloc_summary.tsv md5)

<!-- Existing files Wave 5 reads / mutates -->
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv — schema 4-column (path, md5, rationale, commit_introducing); W5 appends ta-r3 W1-W4 successor rows (NEVER overwrite per Pitfall 5)
- .planning/STATE.md — GATED write per Terminal A m3 active check
- .planning/ROADMAP.md §"### Track-A-R3-audit-v2-driven-psd-and-r1-refire" lines 494-589 — status field update
- .planning/quick/260504-XXX-ta-r3-cowork-handoff/ — NEW directory; handoff brief location

<!-- ta-sh2b3-W7-VERIFICATION.md format (mirror) -->
- PASS/WARN/FAIL per dimension Dn
- JSON-style: `{ "check": "Dn", "status": "PASS|WARN|FAIL", "evidence": "..." }`
- Per-dimension evidence references files + grep commands

<!-- Compute envelope -->
- ~10 min for VERIFICATION.md generation (read all SUMMARYs + summarize)
- ~5 min for md5_baseline.tsv successor row append
- ~10 min for handoff brief
- ~5 min for STATE.md update (gated)
- Aggregator refresh (if W2 = BRANCH_R1_BUG): ~30 min for Rscript aggregator re-run

<!-- STATE.md contention check -->
- Per .planning/feedback_multi_terminal_staging.md: STATE.md is the multi-terminal contention point
- Pre-write check: `[ ! -f .claude/m3-*.lock ] && ! ls .planning/quick/*m3*/IN_PROGRESS 2>/dev/null | grep -q "."`
- If contended: defer STATE.md write to a follow-up /gsd-quick task; phase still closes via ROADMAP.md status update
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Aggregator refresh (if W2 = BRANCH_R1_BUG) + freeze new md5 baseline (append successor rows for W1-W4 file shifts; NEVER overwrite W7 row per Pitfall 5)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
    results/track_a_aggregations/  # MAY MODIFY only if W2 = BRANCH_R1_BUG (new PP rows shift Table 3 numbers)
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (read all D-TA-R3-W*-* outcome tokens)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt (post-W2 coloc_summary.tsv md5)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (4-column schema; W7 baseline rows must be preserved per Pitfall 5)
    - results/track_a_aggregations/ (existing aggregator outputs; mutated only if W2 = BRANCH_R1_BUG)
    - src/R/aggregators/aggregate_table3_admissible_pairs.R (if W2 = BRANCH_R1_BUG, this aggregator must be re-run because Table 3 PP rows shifted)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md §"Task 2 step 5" (predecessor md5 successor row pattern; mirror)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 5 Tasks (skeleton)" lines 224-237 (PRIMARY SPEC; tasks 1-3 source)
  </read_first>
  <action>
    1. **Read W1-W4 outcome tokens** to determine which files' md5 shifted:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       W1_BRANCH=$(grep -oE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | head -1)
       W2_BRANCH=$(grep -oE "D-TA-R3-W2-BRANCH_R1_(BUG|STRUCTURAL)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | head -1)
       W3_OUTCOME=$(grep -oE "D-TA-R3-W3-(OUTCOME|DEFERRED-ON-W1-OUTCOME)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | head -1)
       W4_OUTCOME=$(grep -oE "D-TA-R3-W4-(DEFERRED_TO_FOOTNOTE|RECLASS_FIRED)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | head -1)
       echo "W1: $W1_BRANCH"
       echo "W2: $W2_BRANCH"
       echo "W3: $W3_OUTCOME"
       echo "W4: $W4_OUTCOME"
       ```

    2. **Aggregator refresh (only if W2 outcome = BRANCH_R1_BUG):** New non-empty PP rows in coloc_summary.tsv mean downstream aggregators that consume PP rows (e.g., src/R/aggregators/aggregate_table3_admissible_pairs.R) must re-run. If W2 = BRANCH_R1_STRUCTURAL, no aggregator refresh needed (PP rows still empty for the 28 R1 pairs).

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       if [ "$W2_BRANCH" = "D-TA-R3-W2-BRANCH_R1_BUG" ]; then
         echo "W2 = BRANCH_R1_BUG: re-running downstream aggregators that consume coloc_summary.tsv"
         AGGS=$(grep -lE "coloc_summary\.tsv|results/multitrait/coloc_summary" src/R/aggregators/*.R 2>/dev/null)
         for agg in $AGGS; do
           echo "Re-running: $agg"
           /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript "$agg" 2>&1 | tee -a logs/ta_r3_W5_closeout/aggregator_refresh.log
         done
       else
         echo "W2 = $W2_BRANCH: no aggregator refresh needed (PP rows still empty for 28 R1 pairs)"
       fi
       ```

    3. **Append successor md5 rows to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv** for any files whose md5 shifted in W1/W2/W3/W4. Schema: `path \t md5 \t rationale \t commit_introducing`. NEVER overwrite W7 baseline rows (per Pitfall 5).

       Files to consider for successor rows:
       - `results/multitrait/coloc_summary.tsv` (md5 shifted in W2 + W3 — append BOTH successor rows or the final post-W3 row if W3 fired)
       - `results/multitrait/coloc_manifest_R2.tsv` (preserved unchanged from W7; verify md5 matches W7 baseline; do NOT append a successor row if unchanged)
       - `results/qtl_coloc/tier_assignments.tsv` (md5 shifted ONLY if W4 = RECLASS_FIRED — already appended in W4 Task 2 step 5; W5 verifies the row is present, does not duplicate)
       - `bin/fire_canonical_susie_pairs.sh` (md5 shifted in W3 if FIRES — parameterized additively; W5 appends successor row referencing the parameterization)
       - `config/regions_curated.csv` (md5 shifted in W3 if FIRES — 4 new region rows added)
       - `src/R/aggregators/merge_r2_into_summary.R` (NEW file in W3 if FIRES; append md5 row marking it as introduced)
       - `src/R/regularization/refit_sh2b3_psd_regularized.R` (NEW file in W1; append md5 row)

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       MD5_BASE=.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv

       # Verify W7 row preservation pre-append
       PRE_LINES=$(wc -l < "$MD5_BASE")
       echo "Pre-append md5_baseline.tsv lines: $PRE_LINES"

       # Build append list
       APPEND_TMP=/tmp/ta_r3_W5_md5_append.tsv
       : > "$APPEND_TMP"

       # 1. coloc_summary.tsv (post-W3 if W3 fired; else post-W2)
       if [ -f results/multitrait/coloc_summary.tsv ]; then
         CS_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
         W7_MD5=$(awk -F'\t' '$1 == "results/multitrait/coloc_summary.tsv" {print $2; exit}' "$MD5_BASE")
         if [ "$CS_MD5" != "$W7_MD5" ]; then
           if [ "$W3_OUTCOME" = "D-TA-R3-W3-OUTCOME" ]; then
             RATIONALE="W1-W4 (ta-r3) post-W3 R2-parity merge: SH2B3+R1+FTO+MC4R+APOL1+CXADR rows"
           else
             RATIONALE="W1-W4 (ta-r3) post-W2 R1 cache-invalidated re-fire (W3 SKIPPED/DEFERRED on W1 outcome)"
           fi
           echo -e "results/multitrait/coloc_summary.tsv\t$CS_MD5\t$RATIONALE\tUNTRACKED" >> "$APPEND_TMP"
         else
           echo "(coloc_summary.tsv md5 unchanged from W7 baseline; no successor row needed)"
         fi
       fi

       # 2. NEW files from W1
       if [ -f src/R/regularization/refit_sh2b3_psd_regularized.R ]; then
         RR_MD5=$(md5sum src/R/regularization/refit_sh2b3_psd_regularized.R | cut -d' ' -f1)
         echo -e "src/R/regularization/refit_sh2b3_psd_regularized.R\t$RR_MD5\tW1 (ta-r3) NEW: Wen 2017 ridge + Hutchinson 2020 eigclip PSD regularization fitter\tUNTRACKED" >> "$APPEND_TMP"
       fi

       # 3. NEW files from W3 (only if W3 fired)
       if [ -f src/R/aggregators/merge_r2_into_summary.R ] && [ "$W3_OUTCOME" = "D-TA-R3-W3-OUTCOME" ]; then
         MR_MD5=$(md5sum src/R/aggregators/merge_r2_into_summary.R | cut -d' ' -f1)
         echo -e "src/R/aggregators/merge_r2_into_summary.R\t$MR_MD5\tW3 (ta-r3) NEW: R2 canonical-pair merge aggregator (mirrors /gsd-quick 260501-wdn pattern)\tUNTRACKED" >> "$APPEND_TMP"
       fi

       # 4. Modified bin/fire_canonical_susie_pairs.sh (only if W3 fired)
       if [ "$W3_OUTCOME" = "D-TA-R3-W3-OUTCOME" ] && [ -f bin/fire_canonical_susie_pairs.sh ]; then
         FCS_MD5=$(md5sum bin/fire_canonical_susie_pairs.sh | cut -d' ' -f1)
         W7_FCS_MD5=$(awk -F'\t' '$1 == "bin/fire_canonical_susie_pairs.sh" {print $2; exit}' "$MD5_BASE")
         if [ "$FCS_MD5" != "$W7_FCS_MD5" ]; then
           echo -e "bin/fire_canonical_susie_pairs.sh\t$FCS_MD5\tW3 (ta-r3) parameterized additively: --region + --ancestry args (backwards-compatible default SH2B3 EUR)\tUNTRACKED" >> "$APPEND_TMP"
         fi
       fi

       # 5. Modified config/regions_curated.csv (only if W3 fired)
       if [ "$W3_OUTCOME" = "D-TA-R3-W3-OUTCOME" ] && [ -f config/regions_curated.csv ]; then
         RC_MD5=$(md5sum config/regions_curated.csv | cut -d' ' -f1)
         W7_RC_MD5=$(awk -F'\t' '$1 == "config/regions_curated.csv" {print $2; exit}' "$MD5_BASE")
         if [ "$RC_MD5" != "$W7_RC_MD5" ]; then
           echo -e "config/regions_curated.csv\t$RC_MD5\tW3 (ta-r3) added 4 new region rows: FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR\tUNTRACKED" >> "$APPEND_TMP"
         fi
       fi

       # 6. tier_assignments.tsv: W4 already appended its row(s) in W4 Task 2 step 5 (if RECLASS_FIRED).
       #    W5 does not duplicate — it just verifies presence.
       if [ "$W4_OUTCOME" = "D-TA-R3-W4-RECLASS_FIRED" ]; then
         W4_ROWS=$(awk -F'\t' '$3 ~ /W4-R3 \(ta-r3\)/' "$MD5_BASE" | wc -l)
         [ "$W4_ROWS" -ge 2 ] || \
           { echo "WARN: W4 RECLASS_FIRED but md5_baseline.tsv missing W4-R3 successor rows (expected ≥2)"; }
       fi

       # 7. ta-r3-CONTEXT.md (NEW from W1; tracks all wave outcome decisions)
       if [ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md ]; then
         CTX_MD5=$(md5sum .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | cut -d' ' -f1)
         echo -e ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md\t$CTX_MD5\tW1-W4 (ta-r3) phase context: D-TA-R3-OSF-COVERAGE + W1/W2/W3/W4 outcome decisions\tUNTRACKED" >> "$APPEND_TMP"
       fi

       # Append (>> NOT > per Pitfall 5)
       echo "Appending $(wc -l < "$APPEND_TMP") successor rows to $MD5_BASE"
       cat "$APPEND_TMP" >> "$MD5_BASE"

       # Verify W7 baseline rows preserved
       POST_LINES=$(wc -l < "$MD5_BASE")
       echo "Post-append md5_baseline.tsv lines: $POST_LINES (was $PRE_LINES)"
       [ "$POST_LINES" -gt "$PRE_LINES" ] || \
         { echo "ABORT: append did not increase line count; redirect may have failed"; exit 1; }

       # Sanity: no duplicate lines
       SORT_DUPS=$(sort "$MD5_BASE" | uniq -d | wc -l)
       [ "$SORT_DUPS" -eq 0 ] || \
         { echo "WARN: $SORT_DUPS duplicate lines in $MD5_BASE; investigate"; }
       ```

    4. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
       # Aggregator refresh outputs (only if W2 = BRANCH_R1_BUG):
       if [ "$W2_BRANCH" = "D-TA-R3-W2-BRANCH_R1_BUG" ] && [ -d results/track_a_aggregations ]; then
         git add results/track_a_aggregations/*.tsv 2>/dev/null || true
       fi
       mkdir -p logs/ta_r3_W5_closeout
       [ -f logs/ta_r3_W5_closeout/aggregator_refresh.log ] && \
         git add logs/ta_r3_W5_closeout/aggregator_refresh.log
       git commit -m "feat(ta-r3, W5): append successor md5 rows for W1-W4 file shifts (NEVER overwrite W7 baseline; audit-driven re-analysis)"
       ```
  </action>
  <acceptance_criteria>
    - W1-W4 outcome tokens all read from ta-r3-CONTEXT.md (4 separate tokens; the executor agent's branch decisions are based on these).
    - md5_baseline.tsv has more lines post-append than pre-append: line count increased.
    - W7 baseline row(s) preserved: `awk -F'\t' '$3 ~ /^W[0-7]/ || $3 ~ /Pitfall|rename target|reference fix-up/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l` returns ≥ 1 (predecessor W7 rows still present).
    - Successor rows for W1-W4 added: `awk -F'\t' '$3 ~ /\(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l` returns ≥ 2 (NEW W1 fitter + W1-W4 CONTEXT.md at minimum).
    - No duplicate lines: `sort .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | uniq -d | wc -l` returns 0.
    - If W2 = BRANCH_R1_BUG: aggregator refresh log exists: `[ -s logs/ta_r3_W5_closeout/aggregator_refresh.log ]`.
    - If W3 fired: bin/fire_canonical_susie_pairs.sh successor row present: `awk -F'\t' '$1 == "bin/fire_canonical_susie_pairs.sh" && $3 ~ /W3 \(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l` returns ≥ 1.
    - Atomic commit landed.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(awk -F'\t' '$3 ~ /\(ta-r3\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | wc -l)" -ge 2 ] && [ "$(sort .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | uniq -d | wc -l)" -eq 0 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Aggregator refresh fired (only if W2 = BRANCH_R1_BUG). Successor md5 rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv for files whose md5 shifted in W1/W2/W3/W4 (per Pitfall 5: append-only; never overwrite W7 baseline). No duplicate lines. Honest-framing-lock manuscript md5 unchanged. Atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Write ta-r3-VERIFICATION.md with PASS/WARN/FAIL JSON-style entries for dimensions D1-DN (mirrors ta-sh2b3-VALIDATION.md format) + write Cowork-side handoff brief at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md</name>
  <files>
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md
    .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md
    .planning/quick/260504-XXX-ta-r3-cowork-handoff/STATE.md
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (all wave outcome decisions)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W{1,2,3,4}-*-SUMMARY.md (wave summaries; D1-DN evidence sources)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md (predecessor VALIDATION.md format; mirror PASS/WARN/FAIL evidence per dimension)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"Note on outcome-branch verification follow-up" lines 125-134 (OSF outcome-branch follow-up update spec)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md §"Task 2 step 8 + Task 4" (predecessor closeout pattern; mirror)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 5 Tasks (skeleton)" lines 224-237 (PRIMARY SPEC; tasks 3-4 source)
  </read_first>
  <action>
    1. **Write ta-r3-VERIFICATION.md** with PASS/WARN/FAIL JSON-style evidence per dimension. Mirror the predecessor `ta-sh2b3-VALIDATION.md` format (C-row table + per-row PASS/WARN/FAIL evidence + verification command).

       Dimensions to cover:
       - D1 OSF coverage gate cleared pre-W1 (`grep "D-TA-R3-OSF-COVERAGE: COVERED at" ta-r3-CONTEXT.md`)
       - D2 W1 PSD-regularized fitter landed + 15 fits on disk (`ls results/fine_mapping_psd_regularized/*.fit.rds | wc -l ≥ 15`)
       - D3 W1 LD pathology numbers within 1.0 pp of v2-audit baseline (`awk on results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv`)
       - D4 W1 outcome branch resolved (`grep -E "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)"`)
       - D5 W2 R1 cache-invalidated re-fire complete (`grep -E "D-TA-R3-W2-BRANCH_R1_(BUG|STRUCTURAL)"`)
       - D6 W2 SH2B3 R2 rows preserved (`awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l ≥ 9`)
       - D7 W3 gate disposition recorded (`grep -E "D-TA-R3-W3-(OUTCOME|DEFERRED-ON-W1-OUTCOME)"`)
       - D8 W3 (if FIRES) 4 R2-parity region directories produced ≥1 JSON each
       - D9 W4 gate disposition recorded (`grep -E "D-TA-R3-W4-(DEFERRED_TO_FOOTNOTE|RECLASS_FIRED)"`)
       - D10 md5_baseline.tsv successor rows appended; W7 baseline preserved
       - D11 honest-framing-lock manuscript md5 unchanged through all 5 waves
       - D12 HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold
       - D13 OSF amendment posting timestamp predates first W1 LSF dispatch

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       OUT=.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md
       cat > "$OUT" <<'EOF'
       # ta-r3 Phase Verification — D1-D13 PASS/WARN/FAIL evidence

       **Phase:** ta-r3-audit-v2-driven-psd-and-r1-refire
       **Closeout date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
       **OSF amendment:** posted at osf.io/az52u (file ID per .planning/osf_deviations.md)
       **Manuscript md5 invariant (honest-framing-lock):** 63fd81385590ffc8d23d45a0f0598959 (UNCHANGED through all 5 waves)

       ---

       ## Verification dimensions (per ta-sh2b3-VALIDATION.md pattern)

       | dim | description | check command | status |
       |---|---|---|---|
       | D1 | OSF coverage gate cleared pre-W1 LSF dispatch | `grep "D-TA-R3-OSF-COVERAGE: COVERED at" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` | <PASS|WARN|FAIL> |
       | D2 | W1 PSD-regularized fitter landed + 15 fits on disk | `ls results/fine_mapping_psd_regularized/*.fit.rds \| wc -l` ≥ 15 | <PASS|WARN|FAIL> |
       | D3 | W1 LD pathology numbers within 1.0 pp of v2-audit baseline | `awk on results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv` | <PASS|WARN|FAIL> |
       | D4 | W1 outcome branch resolved (FIRM\|PARTIAL\|COLLAPSE\|NON_CONVERGE) | `grep -E "D-TA-R3-W1-BRANCH_PSD_(FIRM\|PARTIAL\|COLLAPSE\|NON_CONVERGE)" ta-r3-CONTEXT.md` | <PASS|WARN|FAIL> |
       | D5 | W2 R1 cache-invalidated re-fire outcome (BUG\|STRUCTURAL) | `grep -E "D-TA-R3-W2-BRANCH_R1_(BUG\|STRUCTURAL)" ta-r3-CONTEXT.md` | <PASS|WARN|FAIL> |
       | D6 | W2 SH2B3 R2 rows preserved (≥9) post-W2 cache-invalidation | `awk -F'\t' 'NR>1 && \$1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv \| wc -l` ≥ 9 | <PASS|WARN|FAIL> |
       | D7 | W3 gate disposition recorded | `grep -E "D-TA-R3-W3-(OUTCOME\|DEFERRED-ON-W1-OUTCOME)" ta-r3-CONTEXT.md` | <PASS|WARN|FAIL> |
       | D8 | W3 (if FIRES) 4 R2-parity region directories ≥1 JSON each | `for R in FTO MC4R APOL1 CXADR; do ls results/multitrait/coloc_susie_R2_${R}/*.json 2>/dev/null \| wc -l; done` ≥ 1 each | <PASS|WARN|FAIL\|N/A_SKIPPED> |
       | D9 | W4 gate disposition recorded (DEFERRED_TO_FOOTNOTE default OR RECLASS_FIRED) | `grep -E "D-TA-R3-W4-(DEFERRED_TO_FOOTNOTE\|RECLASS_FIRED)" ta-r3-CONTEXT.md` | <PASS|WARN|FAIL> |
       | D10 | md5_baseline.tsv successor rows appended (≥2 ta-r3 rows); W7 baseline preserved | `awk -F'\t' '\$3 ~ /\(ta-r3\)/' md5_baseline.tsv \| wc -l` ≥ 2 | <PASS|WARN|FAIL> |
       | D11 | Honest-framing-lock manuscript md5 unchanged | `md5sum docs/manuscript/id-vs-ref-LD.md \| cut -d' ' -f1` = 63fd81385590ffc8d23d45a0f0598959 | <PASS|WARN|FAIL> |
       | D12 | HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold | `git log --oneline \| grep -cE '069b34f\|7d54183\|02c4404'` = 3 | <PASS|WARN|FAIL> |
       | D13 | OSF amendment posting timestamp predates first W1 LSF dispatch | manual cross-check vs `bjobs -a -J 'ta_r3_W1_*' \| head` job submission times | <PASS|WARN|FAIL> |

       ---

       ## Per-dimension JSON-style evidence

       ### D1 PASS/WARN/FAIL evidence

       ```json
       {"check": "D1", "status": "<PASS|WARN|FAIL>", "evidence": "grep returned <N> hit(s) for D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>"}
       ```

       ### D2 PASS/WARN/FAIL evidence

       ```json
       {"check": "D2", "status": "<PASS|WARN|FAIL>", "evidence": "ls results/fine_mapping_psd_regularized/*.fit.rds | wc -l = <N>; expected ≥15"}
       ```

       <... continue for D3-D13 with the same JSON format, substituting concrete values from the actual run ...>

       ---

       ## Wave outcome summary

       | wave | outcome | evidence |
       |---|---|---|
       | W1 | <FIRM\|PARTIAL\|COLLAPSE\|NON_CONVERGE> | ta-r3-CONTEXT.md D-TA-R3-W1-BRANCH_PSD_<value>; primary lambda <value> |
       | W2 | <BUG\|STRUCTURAL> | ta-r3-CONTEXT.md D-TA-R3-W2-BRANCH_R1_<value>; R1 non-empty PP rows = <N> |
       | W3 | <FIRES\|SKIPPED\|DEFERRED_TO_TRACK_B> | ta-r3-CONTEXT.md D-TA-R3-W3-OUTCOME or D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME |
       | W4 | <DEFERRED_TO_FOOTNOTE\|RECLASS_FIRED> | ta-r3-CONTEXT.md D-TA-R3-W4-<token> |

       ---

       ## OSF outcome-branch follow-up (per OSF amendment §Note on outcome-branch verification follow-up)

       The realized W1 + W2 outcomes + W3 gate state + W4 reconciliation choice are appended as a follow-up OSF update at the same parent record (osf.io/az52u). Key fields:

       - Realized W1 outcome branch: <FIRM\|PARTIAL\|COLLAPSE\|NON_CONVERGE>
       - Realized W2 outcome branch: <BUG\|STRUCTURAL>
       - Realized W3 conditional gate state: <fired\|deferred-on-W1-outcome>
       - Realized W4 reconciliation choice: <footnote\|reclass-fired>
       - R3 phase commit hash range: <first..last from `git log --oneline ...`>
       - Post-W5 md5 invariants: ≥2 ta-r3 rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
       - Cowork-side v5 submission bundle sha256: TBD (deferred; not in this phase's scope; will be in the follow-up update written at v5 ship time)
       EOF
       cat "$OUT"
       ```

    2. **Write Cowork-side handoff brief** at `.planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-XX.md`. Mirror the v5 handoff doc format (HPC_HANDOFF_v5_2026-05-04.md). Include: branches landed, outcome each ticket fell into, commit hashes, LSF job IDs, md5 invariants, artifact zip path.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       HANDOFF_DIR=.planning/quick/260504-XXX-ta-r3-cowork-handoff
       mkdir -p "$HANDOFF_DIR"
       BRIEF=$HANDOFF_DIR/HPC_DELIVERABLE_$(date +%Y-%m-%d).md

       cat > "$BRIEF" <<EOF
       # HPC Deliverable — Track A R3 Audit-Driven Re-analysis (HPC-side closeout)

       **Phase:** ta-r3-audit-v2-driven-psd-and-r1-refire
       **Closeout:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
       **OSF amendment:** osf.io/az52u (per .planning/amendments/osf-amendment-r3-2026-05-04.md)
       **Cowork-side scope (NOT in this deliverable):** A1 / A2 / A3 / A6-stats / A7 / A8 / A9 manuscript edits + v5 submission bundle ship — execute after this handoff lands.

       ---

       ## Wave outcome branches (pre-registered in OSF amendment paragraphs (c) + (e) + (f) + (g))

       | wave | outcome | implication |
       |---|---|---|
       | W1 | $W1_BRANCH | <SH2B3 anchor empirically supported / partially supported / fails / non-converged> |
       | W2 | $W2_BRANCH | <Layer-2-attrition framing refuted / supported> |
       | W3 | $W3_OUTCOME | <R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR fired / skipped / deferred to Track B> |
       | W4 | $W4_OUTCOME | <Tier-assignments HLA reconcile via footnote / on-disk reclass> |

       ---

       ## Phase commit hash range

       \`\`\`bash
       git log --oneline --since="<W1 first commit date>" --until="$(date -I)" | head -20
       \`\`\`

       Recorded range: \`<first_commit>..<last_commit>\` ($(git rev-list --count HEAD ^<first_commit> 2>/dev/null) commits).

       ---

       ## LSF job IDs (for cross-reference with bjobs/bhist post-closeout)

       - W1: dispatch log at logs/sh2b3_psd_refit/sh2b3_psd_refit_dispatch.log; jobnames matching \`ta_r3_W1_*\`
       - W2: dispatch log at logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log; jobnames matching Snakemake-dispatched rule names + \`ta_r3_W2_*\`
       - W3 (if fired): dispatch log at logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log; jobnames matching \`ta_r3_W3_{FTO,MC4R,APOL1,CXADR}_r2\`
       - W4 (if RECLASS_FIRED): no LSF; runs locally

       ---

       ## md5 invariants (post-W5 baseline)

       Successor rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv:

       \`\`\`bash
       awk -F'\\t' '\$3 ~ /\\(ta-r3\\)/' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
       \`\`\`

       W7 baseline rows preserved (Pitfall 5: append-only, never overwrite).

       Honest-framing-lock manuscript md5: \`63fd81385590ffc8d23d45a0f0598959\` (UNCHANGED through all 5 waves).

       ---

       ## Artifact paths (for Cowork-side v5 manuscript edits)

       - **W1 PSD-regularized fits:** results/fine_mapping_psd_regularized/{asthma,bmi,hypertension,stroke,t2d}.EUR.SH2B3_12q24.lambda{0.001,0.01,0.1}.fit.rds (15 files)
       - **W1 PP table:** results/fine_mapping_psd_regularized/sh2b3_psd_pph4_summary.tsv
       - **W1 LD pathology:** results/fine_mapping_psd_regularized/sh2b3_psd_ld_pathology.tsv
       - **W2 28 R1 R-pair JSONs:** results/multitrait/coloc_susie/*.json (post 069b34f + 7d54183 + 02c4404 cache invalidation)
       - **W2 + W3 rebuilt summary:** results/multitrait/coloc_summary.tsv (md5 SHIFTED from W7 baseline; successor row in md5_baseline.tsv)
       - **W3 R2-parity outputs (if fired):** results/multitrait/coloc_susie_R2_{FTO,MC4R,APOL1,CXADR}/*.json
       - **W4 reclass outputs (if RECLASS_FIRED):** results/qtl_coloc/tier_assignments.tsv (post-reclass) + results/qtl_coloc/tier_assignments_hla_fallback_separate.tsv (NEW)
       - **Verification:** .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md
       - **Phase context:** .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (all decision tokens)
       - **Submission bundle:** Cowork-side will rebuild via bin/build_id_vs_ref_ld_submission_bundle.sh against post-W5 disk numbers (NOT in this deliverable; executed in Cowork session after handoff).

       ---

       ## Cowork-side TODO list (informational; OUT of HPC scope)

       1. **A1 / A2 / A3:** Manuscript text edits (re-title, captions, references)
       2. **A6 statistical formalization:** McNemar, bootstrap, BH-FDR per audit-V2
       3. **A7:** Redact internal-state-machine references
       4. **A8:** Promote Fig S2 to main-text Fig 4
       5. **A9:** Manuscript footnote (negative-control narrative — uses W4 deferral or reclass output as substrate)
       6. **v5 submission bundle ship:** Build via bin/build_id_vs_ref_ld_submission_bundle.sh; SHA-256 manifest update; OSF deviation log entry; submit to *Genome Medicine* portal.
       7. **OSF outcome-branch follow-up update:** Append realized W1/W2/W3/W4 outcomes to osf.io/az52u parent record per OSF amendment §Note on outcome-branch verification follow-up.

       ---

       **Honest-framing-lock reminder:** Per .planning/feedback_original_research_framing.md: every artifact this phase + Cowork-side touched frames the work as **"audit-driven re-analysis"**, NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot".
       EOF

       cat "$BRIEF" | head -50
       ```

    3. **Write a brief STATE.md for the handoff /gsd-quick task** (so the next Cowork session has a starting STATE.md that knows the handoff is complete):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       cat > $HANDOFF_DIR/STATE.md <<EOF
       ---
       quick_task: 260504-XXX-ta-r3-cowork-handoff
       phase_handoff_from: ta-r3-audit-v2-driven-psd-and-r1-refire
       status: handoff_landed
       last_activity: $(date -u +%Y-%m-%dT%H:%M:%SZ)
       ---

       # ta-r3 Cowork-side handoff state

       The HPC-side ta-r3 phase closed at $(date -u +%Y-%m-%dT%H:%M:%SZ). Wave outcomes:
       - W1: $W1_BRANCH
       - W2: $W2_BRANCH
       - W3: $W3_OUTCOME
       - W4: $W4_OUTCOME

       Next Cowork-side action: read HPC_DELIVERABLE_$(date +%Y-%m-%d).md + execute Cowork-side TODO list (A1-A9 manuscript edits + v5 bundle ship).
       EOF
       ```

    4. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md \
               $HANDOFF_DIR/HPC_DELIVERABLE_*.md \
               $HANDOFF_DIR/STATE.md
       git commit -m "docs(ta-r3, W5): write VERIFICATION.md (D1-D13 PASS/WARN/FAIL) + Cowork-side handoff brief at .planning/quick/260504-XXX-ta-r3-cowork-handoff/ (audit-driven re-analysis)"
       ```
  </action>
  <acceptance_criteria>
    - File `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md` exists.
    - VERIFICATION.md has ≥ 13 PASS/WARN/FAIL/N_A markers (one per dimension D1-D13): `grep -cE "(PASS|WARN|FAIL|N/A_SKIPPED)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md` returns ≥ 13.
    - VERIFICATION.md references all 4 wave outcome tokens: `grep -cE "D-TA-R3-W[1-4]" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md` returns ≥ 4.
    - Handoff brief exists: `[ -f .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md ]`.
    - Handoff brief enumerates all 4 W1 outcome branches: `grep -cE "(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md` returns ≥ 4.
    - Handoff brief enumerates 2 W2 outcome branches: `grep -cE "(BUG|STRUCTURAL)" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md` returns ≥ 2.
    - Handoff brief references OSF amendment URL: `grep -c "osf.io/az52u" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md` returns ≥ 1.
    - Handoff brief includes honest-framing-lock reminder: `grep -c "audit-driven re-analysis" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md` returns ≥ 1.
    - Handoff brief explicitly forbids stale-framing tokens (defensive): `grep -cE "\\\"fix\\\"|\\\"revision\\\"|\\\"cleanup\\\"|\\\"pivot\\\"" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md` (mention OK in framing-lock-reminder context; absolute count not strict).
    - Handoff STATE.md exists: `[ -f .planning/quick/260504-XXX-ta-r3-cowork-handoff/STATE.md ]`.
    - Atomic commit landed.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md ] && [ "$(grep -cE '(PASS|WARN|FAIL|N/A_SKIPPED)' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md)" -ge 13 ] && [ "$(grep -cE 'D-TA-R3-W[1-4]' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md)" -ge 4 ] && ls .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md >/dev/null 2>&1 && [ "$(grep -cE '(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)' .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md)" -ge 4 ] && [ "$(grep -cE '(BUG|STRUCTURAL)' .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md)" -ge 2 ] && grep -q "osf.io/az52u" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md && grep -q "audit-driven re-analysis" .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_*.md && [ -f .planning/quick/260504-XXX-ta-r3-cowork-handoff/STATE.md ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    ta-r3-VERIFICATION.md written with D1-D13 PASS/WARN/FAIL JSON-style evidence (mirrors ta-sh2b3-VALIDATION.md format). Cowork-side handoff brief at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_<date>.md enumerates all wave outcomes + commit range + LSF job IDs + md5 invariants + artifact paths. Honest-framing-lock reminder included. Handoff STATE.md scaffolded for next Cowork session. Honest-framing-lock manuscript md5 unchanged. Atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Update ROADMAP.md status to COMPLETE; update STATE.md GATED on Terminal A NOT active on m3 path (per multi-terminal-staging memory); record D-TA-R3-W5-PHASE-CLOSURE in ta-r3-CONTEXT.md</name>
  <files>
    .planning/ROADMAP.md
    .planning/STATE.md
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  </files>
  <read_first>
    - .planning/ROADMAP.md §"### Track-A-R3-audit-v2-driven-psd-and-r1-refire" lines 494-589 (status field; update to COMPLETE)
    - .planning/STATE.md (current state — read frontmatter shape; check whether Terminal A is mid-/gsd-quick on m3 path)
    - .planning/feedback_multi_terminal_staging.md (NEVER `git add .` / `-A`; explicit paths only; STATE.md is the contention point)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md §"Task 4 step 2 + step 3" (predecessor STATE.md + ROADMAP.md update pattern; mirror)
  </read_first>
  <action>
    1. **Update ROADMAP.md status field for the ta-r3 phase entry to COMPLETE.** Use the Edit tool to replace the existing `**Status**:` line in the Track-A-R3-audit-v2-driven-psd-and-r1-refire section (currently "scaffolded 2026-05-04 with v2-audit-driven scope baked in...") with:

       ```
       **Status**: COMPLETE — closed $(date +%Y-%m-%d); Wave outcomes: W1=$W1_BRANCH, W2=$W2_BRANCH, W3=$W3_OUTCOME, W4=$W4_OUTCOME; Cowork-side handoff at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_$(date +%Y-%m-%d).md; OSF amendment posted at osf.io/az52u; honest-framing-lock manuscript md5 (63fd81385590ffc8d23d45a0f0598959) unchanged through all 5 waves.
       ```

       Use the Edit tool to perform the replacement. Mirror the predecessor `ta-sh2b3-canonical-and-cache-refresh` status update format (per ta-sh2b3-W7 PLAN.md L546-547).

       Also update the Plans line in ROADMAP.md from `Plans: 0 plans (W1–W5 PLAN.md files produced by /gsd-plan-phase)` to enumerate the 5 PLAN.md files produced:

       ```
       Plans:
       - [x] ta-r3-W1-sh2b3-psd-regularized-refit-PLAN.md — W1 PSD-regularized SuSiE-RSS re-fit + canonical-pair coloc.susie outcome-branch classification
       - [x] ta-r3-W2-r1-trait-pair-coloc-refire-PLAN.md — W2 R1 trait-pair coloc.susie cache-invalidated re-fire (069b34f + 7d54183 + 02c4404 ancestors)
       - [x] ta-r3-W3-r2-canonical-pair-parity-PLAN.md — W3 R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR (gated on W1 outcome)
       - [x] ta-r3-W4-tier-assignments-hla-reconcile-PLAN.md — W4 tier_assignments.tsv HLA reconcile (gated on Cowork-side audit; default DEFERRED_TO_FOOTNOTE)
       - [x] ta-r3-W5-closeout-and-handoff-PLAN.md — W5 phase closeout + Cowork-side handoff brief
       ```

    2. **STATE.md GATE check** (per `.planning/feedback_multi_terminal_staging.md` — STATE.md is the multi-terminal contention point):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # Check whether Terminal A is mid-/gsd-quick on m3 path
       M3_LOCK_FILES=$(ls .claude/m3-*.lock 2>/dev/null | wc -l)
       M3_INPROGRESS=$(ls .planning/quick/*m3*/IN_PROGRESS 2>/dev/null | wc -l)
       SCHED_LOCK=$(ls .claude/scheduled_tasks.lock 2>/dev/null)

       echo "m3 lock files: $M3_LOCK_FILES"
       echo "m3 in-progress: $M3_INPROGRESS"
       echo "scheduled_tasks.lock: $SCHED_LOCK"

       # Treat scheduled_tasks.lock as DEAD if older than 7 days (per memory feedback_multi_terminal_staging.md note about Apr 22 stale lock)
       if [ -n "$SCHED_LOCK" ]; then
         LOCK_AGE_DAYS=$(( ( $(date +%s) - $(stat -c %Y "$SCHED_LOCK") ) / 86400 ))
         echo "scheduled_tasks.lock age (days): $LOCK_AGE_DAYS"
         if [ "$LOCK_AGE_DAYS" -gt 7 ]; then
           echo "(scheduled_tasks.lock considered DEAD; >7 days old)"
           SCHED_LOCK=""
         fi
       fi

       if [ "$M3_LOCK_FILES" -gt 0 ] || [ "$M3_INPROGRESS" -gt 0 ] || [ -n "$SCHED_LOCK" ]; then
         echo "WARN: Terminal A may be active on m3 path; STATE.md write DEFERRED to follow-up /gsd-quick task"
         STATE_WRITE_OK=false
       else
         echo "PASS: Terminal A NOT active on m3 path; STATE.md write proceeds"
         STATE_WRITE_OK=true
       fi
       ```

    3. **STATE.md write (only if STATE_WRITE_OK):**

       If safe to write, use the Edit tool on `.planning/STATE.md` to update the frontmatter `status:` field with a one-line phase closure summary, and update `last_activity:` with the closure date:

       Frontmatter update target:
       ```yaml
       status: ta-r3-audit-v2-driven-psd-and-r1-refire CLOSED ($(date +%Y-%m-%d)); routing next to Cowork session for v5 manuscript revision (A1-A9 + bundle ship)
       last_activity: $(date -u +%Y-%m-%dT%H:%M:%SZ) — ta-r3 W5 closeout (audit-driven re-analysis); Wave outcomes: W1=$W1_BRANCH, W2=$W2_BRANCH, W3=$W3_OUTCOME, W4=$W4_OUTCOME
       ```

    4. **STATE.md deferral note (only if NOT STATE_WRITE_OK):**

       If unsafe to write, append a deferral note to ta-r3-CONTEXT.md indicating the STATE.md update is deferred:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W5-STATE-DEFERRED: STATE.md write deferred ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Reason:** Terminal A appears active on m3 path (m3 lock files: $M3_LOCK_FILES; m3 in-progress: $M3_INPROGRESS; scheduled_tasks.lock: $SCHED_LOCK). Per .planning/feedback_multi_terminal_staging.md, STATE.md is the multi-terminal contention point and must NOT be written while another terminal holds it.

       **Deferral mechanism:** A follow-up /gsd-quick task (e.g., /gsd-quick 260504-XXX-ta-r3-state-md-update or similar) will update STATE.md frontmatter once Terminal A releases m3 lock.

       **Current ROADMAP.md status:** Already updated to COMPLETE in this commit (ROADMAP.md is not the contention point); phase IS closed even without the STATE.md frontmatter update.

       **Handoff impact:** Cowork-side session reads ta-r3-CONTEXT.md + HPC_DELIVERABLE_$(date +%Y-%m-%d).md directly — STATE.md is not on the critical path for handoff.
       EOF
       ```

    5. **Append D-TA-R3-W5-PHASE-CLOSURE to ta-r3-CONTEXT.md:**

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W5-PHASE-CLOSURE: phase closed ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Final wave outcomes:**
       - W1: $W1_BRANCH
       - W2: $W2_BRANCH
       - W3: $W3_OUTCOME
       - W4: $W4_OUTCOME

       **Verification:** ta-r3-VERIFICATION.md D1-D13 evidence
       **Cowork-side handoff:** .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_$(date +%Y-%m-%d).md
       **OSF outcome-branch follow-up:** queued for posting to osf.io/az52u parent record (per OSF amendment §Note on outcome-branch verification follow-up)
       **md5 invariants:** ≥2 ta-r3 successor rows in .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (W7 baseline preserved per Pitfall 5)
       **Honest-framing-lock:** docs/manuscript/id-vs-ref-LD.md md5 = 63fd81385590ffc8d23d45a0f0598959 (UNCHANGED through all 5 waves)
       **STATE.md write status:** $([ "$STATE_WRITE_OK" = "true" ] && echo "WROTTEN" || echo "DEFERRED — Terminal A active on m3 path; follow-up /gsd-quick will update")

       **Routing next:** Cowork session executes A1-A9 manuscript edits + v5 *Genome Medicine* bundle ship; this HPC phase is closed.
       EOF
       ```

    6. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/ROADMAP.md \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
       if [ "$STATE_WRITE_OK" = "true" ]; then
         git add .planning/STATE.md
       fi
       git commit -m "docs(ta-r3, W5): close phase ta-r3-audit-v2-driven-psd-and-r1-refire (W1=$W1_BRANCH, W2=$W2_BRANCH, W3=$W3_OUTCOME, W4=$W4_OUTCOME; audit-driven re-analysis; STATE.md $([ "$STATE_WRITE_OK" = "true" ] && echo "updated" || echo "deferred — Terminal A active"))"
       ```
  </action>
  <acceptance_criteria>
    - ROADMAP.md Track-A-R3-audit-v2-driven-psd-and-r1-refire status field reflects COMPLETE: `grep -E "Track-A-R3-audit-v2-driven-psd-and-r1-refire" .planning/ROADMAP.md | head -50; grep -A 5 "Track-A-R3-audit-v2-driven-psd-and-r1-refire" .planning/ROADMAP.md | grep -c "COMPLETE\\|closed"` returns ≥ 1.
    - Plans line in ROADMAP.md updated to enumerate 5 PLAN.md files: `grep -cE "ta-r3-W[1-5]-.*-PLAN\\.md" .planning/ROADMAP.md` returns ≥ 5.
    - D-TA-R3-W5-PHASE-CLOSURE recorded in ta-r3-CONTEXT.md: `grep -c "D-TA-R3-W5-PHASE-CLOSURE" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - All 4 wave outcomes referenced in D-TA-R3-W5-PHASE-CLOSURE block: `grep -cE "W[1-4]: " .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 4.
    - STATE.md updated OR deferral note recorded: either `grep -E "ta-r3.*CLOSED|ta-r3.*W5.*closeout" .planning/STATE.md | wc -l` ≥ 1 OR `grep -c "D-TA-R3-W5-STATE-DEFERRED" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` ≥ 1.
    - Atomic commit landed.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
    - HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 still hold: `git log --oneline | grep -cE '069b34f|7d54183|02c4404'` returns 3.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ "$(grep -A 5 'Track-A-R3-audit-v2-driven-psd-and-r1-refire' .planning/ROADMAP.md | grep -cE 'COMPLETE|closed')" -ge 1 ] && [ "$(grep -cE 'ta-r3-W[1-5]-.*-PLAN\.md' .planning/ROADMAP.md)" -ge 5 ] && [ "$(grep -c 'D-TA-R3-W5-PHASE-CLOSURE' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && { [ "$(grep -cE 'ta-r3.*CLOSED|ta-r3.*W5.*closeout' .planning/STATE.md 2>/dev/null)" -ge 1 ] || [ "$(grep -c 'D-TA-R3-W5-STATE-DEFERRED' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ]; } && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && [ "$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')" -eq 3 ] && echo PASS</automated>
  </verify>
  <done>
    ROADMAP.md Track-A-R3 entry status updated to COMPLETE with closure date + wave outcomes + Cowork-side handoff path. Plans line enumerates 5 PLAN.md files. STATE.md frontmatter updated (if Terminal A NOT active on m3) OR D-TA-R3-W5-STATE-DEFERRED note recorded (if active; follow-up /gsd-quick handles STATE.md). D-TA-R3-W5-PHASE-CLOSURE recorded in ta-r3-CONTEXT.md with all 4 wave outcomes + verification + handoff + OSF follow-up + md5 invariants + honest-framing-lock status. Honest-framing-lock manuscript md5 unchanged. HEAD ancestors invariant. Atomic commit landed. Phase ta-r3-audit-v2-driven-psd-and-r1-refire formally closed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| W1-W4 outcome decisions (ta-r3-CONTEXT.md) ↔ ta-r3-VERIFICATION.md PASS/WARN/FAIL JSON | VERIFICATION.md is read-only consumer of CONTEXT.md decisions; cannot retroactively change wave outcomes |
| md5_baseline.tsv W7 baseline ↔ W1-W4 successor rows | Per Pitfall 5: NEVER overwrite W7 row; append W1-W4 successor rows after the W7 baseline (chain of valid post-Wave md5 values) |
| Multi-terminal git staging on GPFS ↔ explicit-path commits | Per `.planning/feedback_multi_terminal_staging.md`: never `git add .` / `-A` |
| STATE.md write ↔ Terminal A m3 active check | Per multi-terminal-staging memory: STATE.md is the contention point; W5 gates write on absence of m3 lock + Terminal A in-progress markers; if contended, defer to follow-up /gsd-quick (phase still closes via ROADMAP.md) |
| ROADMAP.md ↔ STATE.md routing fields | ROADMAP.md is NOT contended (single writer per phase); STATE.md IS contended (multi-terminal) |
| Honest-framing-lock manuscript md5 (63fd81385590...) ↔ all 5 waves | docs/manuscript/id-vs-ref-LD.md md5 verified unchanged in every task acceptance criteria |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-TA-R3-W5-01 | T (Tampering) | md5_baseline.tsv W7 baseline overwritten | mitigate | Per Pitfall 5: append-only; Task 1 step 3 explicit `cat >> ... `; acceptance criterion verifies W7 row preserved + total line count increased |
| T-TA-R3-W5-02 | T (Tampering) | STATE.md mid-write race with Terminal A | mitigate | Task 3 step 2 explicit gate check (m3 lock files + IN_PROGRESS markers + stale-lock heuristic); if contended, defer to follow-up /gsd-quick (phase closes via ROADMAP.md only) |
| T-TA-R3-W5-03 | I (Information disclosure) | Implicit `git add .` could stage results_identity_ld/ (DEC-2026-04-25-01) or other untracked files | mitigate | All commits use explicit paths only |
| T-TA-R3-W5-04 | I (Information disclosure) | Honest-framing-lock manuscript edit | accept | OUT of phase scope per OSF amendment "What is not changing"; verified md5 unchanged in every task acceptance criteria |
| T-TA-R3-W5-05 | E (Elevation of privilege) | VERIFICATION.md silently passes a failed dimension | mitigate | PASS/WARN/FAIL evidence is read from CONTEXT.md decision tokens (which are pre-registered per OSF amendment) + measurable file checks; cannot retroactively reframe outcome |
| T-TA-R3-W5-06 | I (Information disclosure) | Cowork-side handoff brief leaks pre-registration deviations | accept | All deviations are pre-registered in OSF amendment and recorded in CONTEXT.md as decision tokens; the handoff brief is the canonical handoff record |
</threat_model>

<verification>
- W1-W4 outcome tokens read from ta-r3-CONTEXT.md (Task 1 step 1)
- Aggregator refresh fired only if W2 = BRANCH_R1_BUG (Task 1 step 2)
- Successor md5 rows appended to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv (Task 1 step 3); W7 baseline preserved per Pitfall 5
- ta-r3-VERIFICATION.md written with D1-D13 PASS/WARN/FAIL JSON-style evidence (Task 2 step 1)
- Cowork-side handoff brief at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_<date>.md (Task 2 step 2)
- Handoff STATE.md scaffolded for next Cowork session (Task 2 step 3)
- ROADMAP.md status updated to COMPLETE; Plans line enumerates 5 PLAN.md files (Task 3 step 1)
- STATE.md GATED on Terminal A m3-active check (Task 3 step 2-4); written or deferred
- D-TA-R3-W5-PHASE-CLOSURE recorded in ta-r3-CONTEXT.md (Task 3 step 5)
- 3 atomic commits landed (Tasks 1, 2, 3)
- Honest-framing-lock manuscript md5 unchanged through all 5 waves
</verification>

<success_criteria>
- ta-r3-VERIFICATION.md with D1-D13 PASS/WARN/FAIL JSON-style evidence
- md5_baseline.tsv successor rows for W1-W4 file shifts (≥2 ta-r3 rows); W7 baseline preserved per Pitfall 5
- Cowork-side handoff brief at .planning/quick/260504-XXX-ta-r3-cowork-handoff/HPC_DELIVERABLE_<date>.md (enumerates all wave outcomes + commit range + LSF job IDs + md5 invariants + artifact paths)
- ROADMAP.md status COMPLETE with closure date + wave outcomes; Plans line enumerates 5 PLAN.md files
- STATE.md updated OR D-TA-R3-W5-STATE-DEFERRED note recorded (Terminal A m3-active gate)
- D-TA-R3-W5-PHASE-CLOSURE recorded in ta-r3-CONTEXT.md with all 4 wave outcomes
- Honest-framing-lock manuscript md5 unchanged (63fd81385590ffc8d23d45a0f0598959) through all 5 waves
- HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold throughout
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W5-closeout-and-handoff-SUMMARY.md` with:
- D1 W1-W4 outcome tokens read (PASS/WARN/FAIL)
- D2 Aggregator refresh fired (only if W2 = BRANCH_R1_BUG) (PASS/WARN/FAIL/N/A)
- D3 Successor md5 rows appended (≥2 ta-r3 rows) without overwriting W7 baseline (PASS/WARN/FAIL)
- D4 ta-r3-VERIFICATION.md with D1-D13 evidence (PASS/WARN/FAIL)
- D5 Cowork-side handoff brief written enumerating all wave outcomes (PASS/WARN/FAIL)
- D6 ROADMAP.md status updated to COMPLETE; Plans line enumerates 5 PLAN.md files (PASS/WARN/FAIL)
- D7 STATE.md updated OR deferral note recorded per Terminal A gate (PASS/WARN/FAIL)
- D8 D-TA-R3-W5-PHASE-CLOSURE recorded with all 4 wave outcomes (PASS/WARN/FAIL)
- D9 Honest-framing-lock manuscript md5 unchanged through all 5 waves (PASS/WARN/FAIL)
- D10 HEAD ancestor invariants hold (PASS/WARN/FAIL)
- Final wave outcome summary (W1/W2/W3/W4 branches)
- OSF outcome-branch follow-up update queued
- Cross-reference to handoff brief path

Plus a phase-of-summaries integration: aggregate per-wave SUMMARYs into a single phase narrative for Carter's hand-off to Cowork-side v5 manuscript revision. Reference each wave SUMMARY by path. List all artifact paths prominently. Include OSF outcome-branch follow-up checklist.
</output>
