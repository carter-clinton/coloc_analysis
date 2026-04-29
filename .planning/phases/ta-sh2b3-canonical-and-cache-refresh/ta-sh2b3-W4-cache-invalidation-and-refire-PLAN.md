---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 4
slug: W4-cache-invalidation-and-refire
type: execute
wave: 4
depends_on: ["W0"]
files_modified:
  - results/qtl_coloc/  # rebuilt from scratch by Snakemake re-fire
  - results/qtl_coloc.preFix.bak.*  # timestamped backup of pre-fix cache
  - results/fine_mapping/susie/  # conditionally rebuilt if D-TA-04-DIAGNOSTIC == BOTH_LAYERS or CONSERVATIVE_BOTH
  - results/fine_mapping/susie.preFix.bak.*  # conditional timestamped backup
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  - logs/wave4_qtl_coloc_refresh_*.log
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "Pre-Wave-4 baseline status distribution captured and recorded (1,005 too_few_snps + 32 success + 235 no_qtl_cs + 2 qtl_susie_failed expected)"
    - "results/qtl_coloc/ moved to timestamped backup results/qtl_coloc.preFix.bak.${TS} (NEVER rm; preserves rollback path)"
    - "If D-TA-04-DIAGNOSTIC == BOTH_LAYERS or CONSERVATIVE_BOTH: results/fine_mapping/susie/ also moved to timestamped backup"
    - "Snakemake re-fire of all_qtl_coloc target completes via /rs1/.../coloc_analysis with --use-conda -j 50 on long queue (~10 hr; +5 hr if SuSiE-RSS layer in scope)"
    - "Post-refresh too_few_snps count drops materially from 1,005 baseline: PASS ≤ 200 → continue to Wave 5; FAIL ~1,000 → halt + Wave 4.5 SuSiE-RSS layer fallback fires"
    - "PASS/FAIL outcome recorded in CONTEXT.md as D-TA-WAVE4-OUTCOME-{PASS|FAIL_TO_W4.5}"
    - "LSF dispatch uses long queue with -W=14400 min (240 hr) via bsub_wrapper.sh (per memory feedback_lsf_queues.md + checker iter 1 NIT 3)"
    - "Wave 4.5 fallback is a MANUAL ESCALATION — Carter must re-execute bin/fire_qtl_coloc_cache_refresh.sh with SUSIE_LAYER_SCOPE=yes after seeing the FAIL_TO_W4.5 outcome; the directive in CONTEXT.md is ADVISORY, NOT automated (per checker iter 1 NIT 4)"
  artifacts:
    - path: "results/qtl_coloc.preFix.bak.${TS}/"
      provides: "Timestamped backup of pre-fix cache (rollback path; never deleted in this phase)"
    - path: "results/qtl_coloc/"
      provides: "Post-refresh QTL-coloc cache (rebuilt by Snakemake against HEAD's 069b34f + 7d54183 fixes)"
      contains: '"status"'
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md"
      provides: "Recorded D-TA-WAVE4-OUTCOME with PASS/FAIL evidence (status counts)"
      contains: "D-TA-WAVE4-OUTCOME-"
    - path: "logs/wave4_qtl_coloc_refresh_*.log"
      provides: "LSF dispatch log for the Snakemake re-fire"
  key_links:
    - from: "069b34f + 7d54183 code fixes (HEAD)"
      to: "results/qtl_coloc/*.json post-refresh"
      via: "Snakemake re-fire with --use-conda"
      pattern: '"status":"success"|"no_qtl_cs"|"too_few_snps"'
    - from: "D-TA-04-DIAGNOSTIC outcome (Wave 0)"
      to: "SuSiE-RSS layer in/out scope decision"
      via: "SUSIE_LAYER_SCOPE env var"
      pattern: "SUSIE_LAYER_SCOPE=(yes|no)"
    - from: "config/bsub_wrapper.sh"
      to: "bsub -W=14400 (long queue 240-hr cap)"
      via: "wrapper sets -W based on QUEUE arg"
      pattern: "long.*14400|QUEUE.*long.*14400"
---

<objective>
Wave 4 — Variant-ID cache invalidation + Snakemake re-fire. Issue 2 closure. The intermediate `results/qtl_coloc/` cache (1,274 attempts; 1,005 `too_few_snps` baseline = 78.9% failure) was generated BEFORE the variant-ID matcher fixes (`069b34f` chr:pos tolerance, `7d54183` LD-rsid override) landed in HEAD. Wave 0 Task 2 recorded D-TA-04-DIAGNOSTIC = {RSID|CHRPOS|MIXED}, which determines whether the SuSiE-RSS layer also needs invalidation:
- RSID → QTL-coloc only (`SUSIE_LAYER_SCOPE=no`; ~10 hr)
- CHRPOS → both layers (`SUSIE_LAYER_SCOPE=yes`; ~15 hr total)
- MIXED → CONSERVATIVE-BOTH (same as CHRPOS; ~15 hr)

Wave 4 PASS criterion: post-refresh `too_few_snps` count ≤ 200 (target; baseline 1,005). FAIL: stays ~1,000 → SuSiE-RSS layer was the actual problem; trigger Wave 4.5 SuSiE-RSS fallback re-fire (only if SUSIE_LAYER_SCOPE was `no` originally); halt before Wave 5.

**Wave 4.5 fallback is a MANUAL ESCALATION (per checker iter 1 NIT 4):** Carter must explicitly re-execute `bin/fire_qtl_coloc_cache_refresh.sh` with `SUSIE_LAYER_SCOPE=yes` after seeing the FAIL_TO_W4.5 outcome. The directive recorded in CONTEXT.md (Task 2 step 4) is ADVISORY guidance for Carter, NOT automated — the executor agent does NOT auto-trigger Wave 4.5. Carter must read the CONTEXT.md addendum, decide whether to proceed, and manually re-fire the driver. After Wave 4.5 completes, Carter re-runs Task 2's PASS/FAIL evaluation against the post-Wave-4.5 disk and records D-TA-WAVE4.5-OUTCOME (analogous to D-TA-WAVE4-OUTCOME).

Purpose: Close audit-V2 §Eval 3.2 (78.9 % QTL-coloc failure currently disclosed in manuscript Methods L90 + Discussion L220 + Limitations bullet 5 as a "known cache-staleness issue"). The re-fire produces the analysis the pre-registration already covers — methodologically a cache hygiene fix, NOT a new analysis (D-TA-Cache-OSF: deviation-log only, NOT pre-reg amendment).

Output: Refreshed `results/qtl_coloc/` cache (1,274 per-attempt JSONs) under post-fix code; timestamped backup of pre-fix cache; PASS/FAIL outcome recorded; LSF dispatch log committed.
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
@CLAUDE.md

<interfaces>
<!-- Wave 0 produced these — Wave 4 consumes -->
- bin/fire_qtl_coloc_cache_refresh.sh — Wave 4 driver (executable; cache backup `mv` + Snakemake re-fire)
- D-TA-04-DIAGNOSTIC: {RSID|CHRPOS|MIXED} — drives SUSIE_LAYER_SCOPE env var (RSID→no; else→yes)
- D-TA-Wave-0-foundations: Snakefile rule names (drives `all_qtl_coloc` target verification)

<!-- Existing files Wave 4 reads / mutates -->
- results/qtl_coloc/*.json — 1,274 pre-fix per-attempt JSONs (1,005 too_few_snps baseline)
- results/fine_mapping/susie/*.{json,fit.rds} — 192 files (96+96); conditionally invalidated
- src/snakemake/rules/qtl_coloc.smk — rule run_qtl_coloc + all_qtl_coloc aggregator
- src/snakemake/scripts/run_qtl_coloc.R — uses 069b34f chr:pos tolerance fix

<!-- Compute envelope -->
- ~10 hr at 50 LSF cores for ~1,274 QTL-coloc attempts (mirrors fire_phase2_stage2_refit envelope)
- +~5 hr for SuSiE-RSS re-fits if SUSIE_LAYER_SCOPE=yes (total ~15 hr)
- long queue, -W 14400 (240 hr cap), 32 GB mem (per memory feedback_lsf_queues.md)

<!-- LSF wall-time configuration (per checker iter 1 NIT 3) -->
- bsub_wrapper.sh sets -W based on QUEUE arg: long=14400 min (240 hr)
- Wave 4 uses long queue (per memory feedback_lsf_queues.md)
- The wrapper enforces this; per-driver scripts do NOT need explicit -W stanzas
- Acceptance check verifies the wrapper config: `grep -qE "long.*14400|QUEUE.*long.*14400" config/bsub_wrapper.sh`

<!-- Pitfall 5 (RESEARCH.md) -->
- Cache backup uses TIMESTAMPED naming: `results/qtl_coloc.preFix.bak.${TS}` (not bare .preFix.bak; idempotent across phase fires)
- Verify pre-existing backup directories before mv: `ls -d results/qtl_coloc.preFix.bak* 2>/dev/null`

<!-- Wave 4 PASS/FAIL branching -->
- PASS: too_few_snps ≤ 200 → Wave 5 cleared
- FAIL: too_few_snps ~1,000 (≥800) → halt; Wave 4.5 SuSiE-RSS fallback fires (only if SUSIE_LAYER_SCOPE was 'no'); do NOT proceed to Wave 5/6
- INTERMEDIATE: 200-800 → WARN; investigate; Carter decides

<!-- Wave 4.5 fallback (per checker iter 1 NIT 4) -->
- Wave 4.5 is a MANUAL ESCALATION, NOT an automated continuation.
- The CONTEXT.md addendum (D-TA-WAVE4.5-DIRECTIVE in Task 2 step 4) is ADVISORY guidance for Carter.
- Carter sees the FAIL_TO_W4.5 outcome → reads the directive → manually re-executes `bin/fire_qtl_coloc_cache_refresh.sh` with `SUSIE_LAYER_SCOPE=yes`.
- After Wave 4.5 completes, Carter re-runs Task 2's evaluation against post-Wave-4.5 disk, records D-TA-WAVE4.5-OUTCOME, and decides Wave 5 GO/NO-GO.
- The executor agent does NOT auto-trigger Wave 4.5 from within the Wave 4 task; the directive is human-actionable.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Capture baseline + fire Wave 4 cache invalidation + Snakemake re-fire (long queue with -W=14400 min via bsub_wrapper.sh)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv
    results/qtl_coloc/  # rebuilt
    results/qtl_coloc.preFix.bak.*  # timestamped backup
    results/fine_mapping/susie/  # conditional rebuild
    results/fine_mapping/susie.preFix.bak.*  # conditional timestamped backup
    logs/wave4_qtl_coloc_refresh_*.log
  </files>
  <read_first>
    - bin/fire_qtl_coloc_cache_refresh.sh (Wave 0 Task 5)
    - config/bsub_wrapper.sh (verify -W=14400 for long queue per checker iter 1 NIT 3)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-04-DIAGNOSTIC" (drives SUSIE_LAYER_SCOPE env var)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 5: Wave 4 cache invalidation backs up to wrong path" + §"Code Examples → Wave 4: QTL-coloc cache re-fire"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C9 row
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # D-TA-04-DIAGNOSTIC must be recorded
       grep -qE "D-TA-04 cache-scope decision:.*(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)" \
         .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md || \
         { echo "ABORT: D-TA-04-DIAGNOSTIC not recorded"; exit 1; }

       # LSF wall-time configuration check (per checker iter 1 NIT 3):
       # bsub_wrapper.sh must set -W=14400 for long queue (the wave's compute envelope is ~10-15 hr; 240-hr cap is well above)
       grep -qE "long.*14400|QUEUE.*long.*14400" config/bsub_wrapper.sh || \
         { echo "ABORT: bsub_wrapper.sh does not enforce -W=14400 for long queue (per checker iter 1 NIT 3)"; exit 1; }
       echo "PASS: bsub_wrapper.sh enforces -W=14400 (240 hr) for long queue"

       # Extract SUSIE_LAYER_SCOPE from D-TA-04 outcome
       SCOPE_TOKEN=$(grep -oE "D-TA-04 cache-scope decision:.*\`(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)\`" \
                      .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | \
                     grep -oE "(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)" | head -1)
       if [ "$SCOPE_TOKEN" = "QTL_COLOC_ONLY" ]; then
         export SUSIE_LAYER_SCOPE=no
       else
         export SUSIE_LAYER_SCOPE=yes
       fi
       echo "SUSIE_LAYER_SCOPE=$SUSIE_LAYER_SCOPE (driven by D-TA-04 = $SCOPE_TOKEN)"

       # Pre-fire any conflicting backup-name check (Pitfall 5)
       PRE_BAK=$(ls -d results/qtl_coloc.preFix.bak* 2>/dev/null | wc -l)
       echo "Pre-existing qtl_coloc backups: $PRE_BAK (will be additional, not overwritten)"
       ```

    2. **Capture baseline status distribution (must record BEFORE the mv):**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       BASELINE_TSV=.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv
       echo -e "metric\tcount" > "$BASELINE_TSV"
       echo -e "total_attempts\t$(ls results/qtl_coloc/*.json 2>/dev/null | wc -l)" >> "$BASELINE_TSV"
       grep -h '"status"' results/qtl_coloc/*.json 2>/dev/null \
         | sort | uniq -c \
         | awk '{ status=$2; sub(/^"status":"/, "", status); sub(/"$/, "", status); printf "%s\t%d\n", status, $1 }' \
         >> "$BASELINE_TSV" || true
       cat "$BASELINE_TSV"
       # Expected baseline:
       # total_attempts  1274
       # too_few_snps    1005
       # success         32
       # no_qtl_cs       235
       # qtl_susie_failed 2
       ```

    3. **Fire the Wave 4 driver (cache backup + Snakemake re-fire):**
       ```bash
       export LSF_UNIT_FOR_LIMITS=GB
       export SUSIE_LAYER_SCOPE  # set in step 1
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01
       bash bin/fire_qtl_coloc_cache_refresh.sh
       ```
       The driver:
       - Backs up `results/qtl_coloc/` → `results/qtl_coloc.preFix.bak.$(date +%Y%m%d_%H%M%S)` (Pitfall 5: timestamped uniqueness)
       - Conditionally backs up `results/fine_mapping/susie/` if SUSIE_LAYER_SCOPE=yes
       - Fires Snakemake re-fire: `--profile config/cluster_lsf -j 50 --use-conda --rerun-incomplete --conda-prefix .snakemake/conda --latency-wait 120 -s Snakefile all_qtl_coloc`
       - Each Snakemake-dispatched LSF job picks up the long queue per cluster_config.yaml (run_qtl_coloc rule); bsub_wrapper.sh transparently sets -W=14400.

    4. **Monitor LSF jobs to completion (~10 hr expected; up to ~15 hr if SuSiE-RSS layer):**
       ```bash
       while bjobs 2>&1 | grep -qE "PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running: $(bjobs | grep -E 'PEND|RUN' | wc -l)"
         sleep 600  # 10-min poll for long-running wave
       done
       echo "[$(date +%H:%M:%S)] All Wave 4 LSF jobs done."
       ```

    5. **Verify outputs landed:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       NEW_COUNT=$(ls results/qtl_coloc/*.json 2>/dev/null | wc -l)
       echo "Post-refresh attempts: $NEW_COUNT (baseline 1274)"
       if [ "$NEW_COUNT" -lt 1000 ]; then
         echo "WARN: dramatically fewer attempts post-refresh; investigate manifest changes"
       fi
       ```

    6. **Atomic commit (driver script + baseline TSV + log; the qtl_coloc/*.json may be gitignored or committed depending on policy — check .gitignore):**
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv \
               logs/wave4_qtl_coloc_refresh_*.log
       grep -n "results/qtl_coloc" .gitignore || echo "(not gitignored — commit only baseline + log; Wave 5 aggregator outputs are the canonical artifacts to commit)"
       git commit -m "feat(ta-sh2b3, W4): fire cache invalidation + Snakemake re-fire (D-TA-04 = $SCOPE_TOKEN)"
       ```
  </action>
  <acceptance_criteria>
    - `wave4_baseline.tsv` exists with at least 5 rows: total_attempts (≈1274), too_few_snps (≈1005), success (≈32), no_qtl_cs (≈235), qtl_susie_failed (≈2). Numbers may differ slightly from baseline values if any pre-Wave-4 fires altered them; the actual recorded baseline is the source of truth.
    - Backup directory exists with timestamped suffix: `ls -d results/qtl_coloc.preFix.bak.*` returns ≥ 1 entry.
    - If `SUSIE_LAYER_SCOPE=yes`: backup of SuSiE-RSS layer also exists: `ls -d results/fine_mapping/susie.preFix.bak.*` returns ≥ 1 entry.
    - `results/qtl_coloc/` exists post-refresh with 1,000+ JSONs.
    - All LSF jobs completed exit 0: `bhist -a 2>&1 | grep -c "Done successfully"` reflects the wave's job count or equivalent.
    - Driver log file exists: `ls logs/wave4_qtl_coloc_refresh_*.log | wc -l` ≥ 1.
    - **LSF wall-time configuration verified (per checker iter 1 NIT 3):** `grep -qE "long.*14400|QUEUE.*long.*14400" config/bsub_wrapper.sh` returns 0.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -qE "long.*14400|QUEUE.*long.*14400" config/bsub_wrapper.sh && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv ] && [ "$(wc -l < .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv)" -ge 5 ] && [ "$(ls -d results/qtl_coloc.preFix.bak.* 2>/dev/null | wc -l)" -ge 1 ] && [ "$(ls results/qtl_coloc/*.json 2>/dev/null | wc -l)" -ge 1000 ] && echo PASS</automated>
  </verify>
  <done>
    Pre-Wave-4 baseline recorded in TSV. `results/qtl_coloc/` invalidated via timestamped `mv` to backup (Pitfall 5 mitigated). Conditional SuSiE-RSS layer backup landed if SUSIE_LAYER_SCOPE=yes. Snakemake re-fire complete with new per-attempt JSONs in place. bsub_wrapper.sh confirmed to enforce -W=14400 for long queue (per checker iter 1 NIT 3). Atomic commit landed. Wave 4 PASS/FAIL evaluation (Task 2) can now run.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Wave 4 PASS/FAIL evaluation + record D-TA-WAVE4-OUTCOME (gates Wave 5); Wave 4.5 fallback is MANUAL ESCALATION (per checker iter 1 NIT 4)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv (Task 1 produced)
    - results/qtl_coloc/*.json (Task 1 refreshed)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-04: Cache-layer scope" (PASS/FAIL definitions: PASS too_few_snps ≤ 200; FAIL ≈ 1,000)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Code Examples → Wave 4: PASS / FAIL verification"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C9 row
  </read_first>
  <action>
    1. **Capture post-refresh status distribution:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       POST_TSV=.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv
       echo -e "metric\tcount" > "$POST_TSV"
       echo -e "total_attempts\t$(ls results/qtl_coloc/*.json 2>/dev/null | wc -l)" >> "$POST_TSV"
       grep -h '"status"' results/qtl_coloc/*.json 2>/dev/null \
         | sort | uniq -c \
         | awk '{ status=$2; sub(/^"status":"/, "", status); sub(/"$/, "", status); printf "%s\t%d\n", status, $1 }' \
         >> "$POST_TSV"
       cat "$POST_TSV"
       ```

    2. **Compute PASS/FAIL outcome:**
       ```bash
       BASELINE_TFS=$(awk -F'\t' '$1 == "too_few_snps" { print $2 }' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv)
       POST_TFS=$(awk -F'\t' '$1 == "too_few_snps" { print $2 }' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv)
       BASELINE_TFS=${BASELINE_TFS:-0}
       POST_TFS=${POST_TFS:-0}
       echo "Baseline too_few_snps: $BASELINE_TFS"
       echo "Post-refresh too_few_snps: $POST_TFS"

       if [ "$POST_TFS" -le 200 ]; then
         OUTCOME="PASS"
         W5_GATE="CLEARED"
       elif [ "$POST_TFS" -ge 800 ]; then
         OUTCOME="FAIL_TO_W4.5"
         W5_GATE="BLOCKED"
       else
         OUTCOME="WARN_INTERMEDIATE"
         W5_GATE="CARTER_DECIDES"
       fi
       echo "OUTCOME=$OUTCOME; W5_GATE=$W5_GATE"
       ```

    3. **Append D-TA-WAVE4-OUTCOME to CONTEXT.md** under `<decisions>` (after D-TA-WAVE3-OUTCOME):

       ```markdown
       ### D-TA-WAVE4-OUTCOME-{PASS|FAIL_TO_W4.5|WARN_INTERMEDIATE}: Cache-refresh PASS/FAIL evaluation (Wave 4)

       **Recorded:** {timestamp}

       **Pre-Wave-4 baseline (status distribution):**
       | metric | count |
       |---|---|
       | total_attempts | {baseline_total} |
       | too_few_snps | {baseline_tfs} |
       | success | {baseline_success} |
       | no_qtl_cs | {baseline_no_cs} |
       | qtl_susie_failed | {baseline_failed} |

       **Post-refresh status distribution:**
       | metric | count |
       |---|---|
       | total_attempts | {post_total} |
       | too_few_snps | {post_tfs} |
       | success | {post_success} |
       | no_qtl_cs | {post_no_cs} |
       | qtl_susie_failed | {post_failed} |

       **Outcome:** {PASS | FAIL_TO_W4.5 | WARN_INTERMEDIATE}

       **Cache-scope used (D-TA-04):** {QTL_COLOC_ONLY | BOTH_LAYERS | CONSERVATIVE_BOTH}

       **Wave 5 gate:** {CLEARED | BLOCKED | CARTER_DECIDES}

       **Δ too_few_snps:** {baseline_tfs} → {post_tfs} ({absolute drop} attempts; {percent drop}% reduction)

       **Branch implications:**
       - PASS → Wave 5 fires (downstream aggregator + figure refresh against post-refresh disk)
       - FAIL_TO_W4.5 → Wave 4.5 SuSiE-RSS fallback fires (ONLY if D-TA-04 was QTL_COLOC_ONLY originally; if BOTH_LAYERS already in scope, root-cause investigation needed instead). **NOTE: Wave 4.5 is a MANUAL ESCALATION, NOT automated — Carter must read this directive, decide, and re-execute the driver explicitly (per checker iter 1 NIT 4).**
       - WARN_INTERMEDIATE → Carter inspects WAR sub-classifications (which regions still failing? sparse-QTL coverage vs cache staleness?) before deciding Wave 5 vs Wave 4.5
       ```

    4. **Conditional Wave 4.5 fallback DIRECTIVE recording (only if OUTCOME == FAIL_TO_W4.5 AND original SUSIE_LAYER_SCOPE was 'no'):**

       **CRITICAL: This step ONLY records an ADVISORY directive in CONTEXT.md (per checker iter 1 NIT 4). The executor agent does NOT auto-fire `bin/fire_qtl_coloc_cache_refresh.sh` with `SUSIE_LAYER_SCOPE=yes`.** Wave 4.5 requires:
       1. Carter sees the FAIL_TO_W4.5 outcome (after Task 2 commits)
       2. Carter reads the D-TA-WAVE4.5-DIRECTIVE addendum
       3. Carter manually re-executes `bin/fire_qtl_coloc_cache_refresh.sh` with `SUSIE_LAYER_SCOPE=yes` (the original Wave 4 driver, re-fired with widened scope)
       4. The driver backs up `results/fine_mapping/susie/` to a NEW timestamped backup AND backs up the (already-refreshed) `results/qtl_coloc/` to ANOTHER timestamped backup
       5. After Wave 4.5 completes (~15 hr), Carter re-runs the post-refresh capture + PASS/FAIL evaluation (Task 2 steps 1-2 of THIS plan; informally, since the Wave 4.5 task isn't a separate plan)
       6. Carter records D-TA-WAVE4.5-OUTCOME in CONTEXT.md (analogous to D-TA-WAVE4-OUTCOME)
       7. Wave 5 gate CLEARED only if D-TA-WAVE4.5-OUTCOME = PASS

       The executor agent's responsibility ends at recording the directive; Carter's responsibility begins.

       ```bash
       if [ "$OUTCOME" = "FAIL_TO_W4.5" ]; then
         # Check whether original D-TA-04 was QTL_COLOC_ONLY (i.e., we DIDN'T already invalidate SuSiE-RSS layer)
         SCOPE_USED=$(grep -oE "D-TA-04 cache-scope decision:.*\`(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)\`" \
                      .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | \
                      grep -oE "(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)" | head -1)
         if [ "$SCOPE_USED" = "QTL_COLOC_ONLY" ]; then
           echo "FAIL: too_few_snps stays high. Recording Wave 4.5 SuSiE-RSS fallback DIRECTIVE (manual escalation per checker iter 1 NIT 4)."
           # Append a Wave 4.5 directive to CONTEXT.md (does NOT auto-execute; Carter triggers separately)
           cat >> .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md <<EOF

       ### D-TA-WAVE4.5-DIRECTIVE: SuSiE-RSS layer fallback re-fire (post-W4 FAIL) — MANUAL ESCALATION

       **Recorded:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

       **Trigger:** Wave 4 outcome = FAIL_TO_W4.5; original D-TA-04 was QTL_COLOC_ONLY.

       **STATUS: ADVISORY DIRECTIVE — NOT AUTOMATED (per checker iter 1 NIT 4).**

       **Required action (Carter — manual, NOT automated by the executor agent):**
       1. Re-fire \`bin/fire_qtl_coloc_cache_refresh.sh\` with \`SUSIE_LAYER_SCOPE=yes\` (override the ENV var that was 'no' on Wave 4):
          \`\`\`bash
          export SUSIE_LAYER_SCOPE=yes
          bash bin/fire_qtl_coloc_cache_refresh.sh
          \`\`\`
       2. The driver will back up results/fine_mapping/susie/ to a NEW timestamped directory (the QTL-coloc backup from Wave 4 is preserved separately). It will also re-back-up the already-refreshed QTL-coloc cache because the Snakemake re-fire is "both layers" scope.
       3. Monitor LSF jobs (~15 hr wall on long queue with -W=14400).
       4. Re-run the post-refresh capture + PASS/FAIL evaluation (analogous to Task 2 steps 1-2 of Wave 4 plan).
       5. Record D-TA-WAVE4.5-OUTCOME in CONTEXT.md (analogous to D-TA-WAVE4-OUTCOME).
       6. Wave 5 gate CLEARED only if D-TA-WAVE4.5-OUTCOME = PASS.

       **Wave 5 gate:** BLOCKED until Wave 4.5 completes AND post-Wave-4.5 too_few_snps ≤ 200.
       EOF
         else
           echo "FAIL: too_few_snps stays high even though SuSiE-RSS layer was already in scope. ROOT-CAUSE INVESTIGATION needed before Wave 5."
           cat >> .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md <<EOF

       ### D-TA-WAVE4-ROOTCAUSE: Both layers refreshed but too_few_snps stays high — MANUAL TRIAGE

       **Recorded:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

       **STATUS: ADVISORY DIRECTIVE — NOT AUTOMATED (per checker iter 1 NIT 4).**

       **Required action (Carter — manual triage):** Halt phase. Root-cause investigation needed (ld panel/coverage? manifest definition? per-region SNP density?). Carter to triage. The executor agent does NOT auto-investigate; Carter inspects the cache directly + Snakemake DAG + per-region log files.

       **Wave 5 gate:** BLOCKED.
       EOF
         fi
       fi
       ```

    5. **Run verification harness for Wave 4 (C9):**
       ```bash
       bin/verify_ta_sh2b3_phase.sh --wave 4
       ```
       C9 emits PASS if too_few_snps ≤ 200; WARN if 200-800; FAIL if ≥800.

    6. **Atomic commit:**
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W4): record D-TA-WAVE4-OUTCOME-${OUTCOME} ({baseline}→{post} too_few_snps)"
       ```
       (Substitute the actual `${OUTCOME}` token + numerics into the commit message.)
  </action>
  <acceptance_criteria>
    - `wave4_post_refresh.tsv` exists with the same schema as the baseline TSV (`metric\tcount` header + ≥ 5 rows).
    - `grep -E "D-TA-WAVE4-OUTCOME-(PASS|FAIL_TO_W4.5|WARN_INTERMEDIATE):" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - The recorded sub-section includes both pre and post status distributions.
    - The recorded sub-section includes the explicit Wave 5 gate disposition (CLEARED / BLOCKED / CARTER_DECIDES).
    - If OUTCOME == FAIL_TO_W4.5: a `D-TA-WAVE4.5-DIRECTIVE` or `D-TA-WAVE4-ROOTCAUSE` sub-section is appended to CONTEXT.md, AND it MUST contain the phrase "MANUAL ESCALATION" or "ADVISORY DIRECTIVE — NOT AUTOMATED" (per checker iter 1 NIT 4): `grep -E "(MANUAL ESCALATION|ADVISORY DIRECTIVE.*NOT AUTOMATED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit when FAIL_TO_W4.5.
    - C9 from `bin/verify_ta_sh2b3_phase.sh --wave 4` emits PASS, WARN, or FAIL consistent with the recorded outcome.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv ] && grep -qE "D-TA-WAVE4-OUTCOME-(PASS|FAIL_TO_W4\.5|WARN_INTERMEDIATE)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "Wave 5 gate:.*(CLEARED|BLOCKED|CARTER_DECIDES)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    Post-Wave-4 status distribution captured and recorded; D-TA-WAVE4-OUTCOME-{PASS|FAIL_TO_W4.5|WARN_INTERMEDIATE} recorded in CONTEXT.md addendum with full pre vs post status comparison + Wave 5 gate disposition. If FAIL: Wave 4.5 fallback directive recorded with explicit "MANUAL ESCALATION" labeling (per checker iter 1 NIT 4 — clarifies the directive is advisory, NOT automated). C9 emits the corresponding harness status. Atomic commit landed. Verifies C9 in VALIDATION.md.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pre-fix `results/qtl_coloc/` cache ↔ Post-fix Snakemake re-fire | Wave 4 invalidation crosses this; mv (not rm) preserves rollback |
| D-TA-04-DIAGNOSTIC outcome ↔ SUSIE_LAYER_SCOPE env var | Wrong env var = under-invalidation (potentially still stale results) or over-invalidation (extra ~5 hr) |
| Snakemake re-fire ↔ canonical Snakefile + HEAD code | All_qtl_coloc target dispatches against HEAD's 069b34f + 7d54183 fixed code |
| Wave 4.5 directive recording ↔ Wave 4.5 manual execution | Per checker iter 1 NIT 4: the directive is ADVISORY; Carter must manually re-execute the driver after seeing FAIL_TO_W4.5 |
| LSF wall-time enforcement ↔ bsub_wrapper.sh | Per checker iter 1 NIT 3: wrapper sets -W=14400 for long queue (240-hr cap, well above ~10-15 hr per-fire envelope) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-01 | T (Tampering) | results/qtl_coloc/ pre-fix cache | mitigate | Timestamped `mv` to .preFix.bak.${TS} (Pitfall 5 mitigation); never `rm`; rollback path preserved |
| T-PROCESS-02 | I (Information disclosure) | Implicit `git add .` could stage results/qtl_coloc/*.json (large; may be gitignored intentionally) | mitigate | Wave 4 commits use explicit paths: baseline.tsv + post_refresh.tsv + CONTEXT.md + log only; per-attempt JSONs left to .gitignore policy |
| T-PROCESS-04 | T (Tampering) | results/multitrait/coloc_summary.tsv md5 invariant | mitigate | Wave 4 does NOT touch coloc_summary.tsv; only QTL-coloc layer (and conditionally SuSiE-RSS layer) is in scope |
| T-PROCESS-07 | E (Elevation of privilege) | Wave 4.5 fallback misinterpreted as automated continuation | mitigate | Per checker iter 1 NIT 4: directive labeled "MANUAL ESCALATION" / "ADVISORY DIRECTIVE — NOT AUTOMATED" in CONTEXT.md; acceptance criterion grep verifies the labeling; must_haves.truths explicit |
| T-PROCESS-06 | D (Denial of service) | LSF jobs killed by 30-min queue default RUNLIMIT | mitigate | bsub_wrapper.sh enforces -W=14400 for long queue (per checker iter 1 NIT 3); Task 1 step 1 acceptance check verifies wrapper config |
</threat_model>

<verification>
- Pre-Wave-4 baseline status distribution captured in wave4_baseline.tsv (Task 1)
- Cache backup with timestamped suffix exists (Task 1)
- Snakemake re-fire complete (Task 1)
- bsub_wrapper.sh enforces -W=14400 for long queue (per checker iter 1 NIT 3)
- Post-Wave-4 status distribution captured in wave4_post_refresh.tsv (Task 2)
- D-TA-WAVE4-OUTCOME recorded with PASS/FAIL/WARN evaluation (Task 2)
- Wave 4.5 fallback directive (if FAIL) appended to CONTEXT.md with MANUAL ESCALATION labeling (Task 2; per checker iter 1 NIT 4)
- C9 emits PASS/WARN/FAIL from verification harness consistent with outcome
- 2 atomic commits landed
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C9** Cache refresh produces materially different numerics — Task 1 + Task 2
</verification_criteria>

<success_criteria>
- Pre-Wave-4 baseline + post-Wave-4 status distributions recorded as TSVs
- results/qtl_coloc/ refreshed by Snakemake under HEAD's 069b34f + 7d54183 code
- Timestamped backup of pre-fix cache preserved (rollback path)
- D-TA-WAVE4-OUTCOME-{PASS|FAIL_TO_W4.5|WARN_INTERMEDIATE} recorded in CONTEXT.md
- Wave 5 gate disposition explicit (CLEARED / BLOCKED / CARTER_DECIDES)
- Wave 4.5 fallback directive (if applicable) appended with MANUAL ESCALATION labeling (per checker iter 1 NIT 4)
- C9 emits PASS for too_few_snps ≤ 200
- bsub_wrapper.sh enforces -W=14400 for long queue (per checker iter 1 NIT 3)
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md` with:
- Pre/post status distribution tables
- Compute envelope observed (~10 hr expected for QTL-coloc only; ~15 hr if SuSiE-RSS layer)
- Wave 4 outcome (PASS/FAIL/WARN)
- Wave 5 gate disposition
- D1 cache-backup integrity verified (mv preserved data; not rm)
- D2 SUSIE_LAYER_SCOPE applied per D-TA-04
- D3 Snakemake re-fire used HEAD code (069b34f + 7d54183 ancestors)
- D4 too_few_snps drop magnitude
- D5 PASS/FAIL/WARN classification
- D6 Wave 4.5 fallback DIRECTIVE recorded (or not); explicitly note that the directive is MANUAL ESCALATION per checker iter 1 NIT 4
- D7 commit hygiene (explicit paths)
- Cross-reference to checker iter 1 NIT 3 + NIT 4 mitigations
</output>
