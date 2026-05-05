---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 2
slug: W2-r1-trait-pair-coloc-refire
type: execute
wave: 2
depends_on: ["W1"]
files_modified:
  - results/multitrait/coloc_susie/  # 28 R1 JSONs cache-invalidated + re-fired
  - results/multitrait/coloc_susie.preFix.bak.20260504_HHMMSS/  # timestamped backup of pre-W2 R1 cache
  - results/multitrait/coloc_summary.tsv  # rebuilt from re-fired JSONs (md5 will shift)
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  - logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "HEAD ancestor invariant: commits 069b34f + 7d54183 + 02c4404 are all in `git log` (the variant-ID-format-fix substrate the cache invalidation tests against)"
    - "Pre-W2 R1 cache backed up to timestamped path results/multitrait/coloc_susie.preFix.bak.${TS}/ (mv NOT rm; rollback path preserved per Pitfall 5 convention from ta-sh2b3-W4)"
    - "Pre-W2 baseline empty-PP-row count captured (expected baseline: 28/28 empty PP.H3/PP.H4 columns at non-SH2B3 pairs per audit-V2 §HQ#2(iii))"
    - "28 R1 trait-pair targets identified (full coloc_manifest.tsv minus the 9 SH2B3 R2 pairs; written to ta-r3-W2-r1-targets.tsv)"
    - "Snakemake re-fire fires `--forcerun run_coloc_susie` against the 28 R1 targets via /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake (Python 3.11) with --use-conda --conda-prefix .snakemake/conda --jobs 50 --keep-going --rerun-incomplete --latency-wait 120"
    - "Post-refire coloc_summary.tsv rebuilt; md5 captured to ta-r3-W2-post_refire_md5.txt; md5 will SHIFT relative to ta-sh2b3-W7 baseline (this is intentional)"
    - "9 SH2B3 R2 rows in coloc_summary.tsv preserved (W2 force-reruns only the 28 R1 pair targets, NOT the 9 SH2B3 R2 ones — per plan-of-plans risk register row 4)"
    - "W2 outcome classified into exactly one of {BRANCH_R1_BUG, BRANCH_R1_STRUCTURAL} per OSF amendment paragraph (e) decision matrix; written to ta-r3-CONTEXT.md as D-TA-R3-W2-BRANCH_R1_*"
    - "LSF dispatch via Snakemake's LSF profile uses serial queue (per-pair envelope ~10-30 min); bsub_wrapper.sh transparently sets -W=5760 (per memory feedback_lsf_queues.md)"
    - "docs/manuscript/id-vs-ref-LD.md md5 unchanged (63fd81385590ffc8d23d45a0f0598959; honest-framing-lock invariant — manuscript edits OUT of phase scope)"
  artifacts:
    - path: "results/multitrait/coloc_susie.preFix.bak.${TS}/"
      provides: "Timestamped backup of pre-W2 R1 cache (rollback path; NEVER deleted in this phase per Pitfall 5)"
    - path: "results/multitrait/coloc_summary.tsv"
      provides: "Post-refire rebuilt summary (md5 shift expected; W5 captures successor row in md5_baseline.tsv)"
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv"
      provides: "28-pair R1 target manifest (used by Snakemake --forcerun)"
      contains: "pair_id"
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt"
      provides: "Post-refire md5 of coloc_summary.tsv (used by W5 to add successor row to md5_baseline.tsv)"
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md"
      provides: "D-TA-R3-W2-BRANCH_R1_* outcome token recorded"
      contains: "D-TA-R3-W2-BRANCH_R1_"
  key_links:
    - from: "git HEAD ancestors 069b34f + 7d54183 + 02c4404"
      to: "results/multitrait/coloc_susie/*.json (28 R1 JSONs post-refire)"
      via: "Snakemake --forcerun run_coloc_susie under HEAD code"
      pattern: '"PP.H4.abf"'
    - from: "results/multitrait/coloc_summary.tsv (rebuilt)"
      to: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W2-BRANCH_R1_*)"
      via: "non-empty PP-row counter applies amendment paragraph (e) decision matrix"
      pattern: "D-TA-R3-W2-BRANCH_R1_(BUG|STRUCTURAL)"
    - from: "config/bsub_wrapper.sh"
      to: "Snakemake LSF profile bsub -W=5760 (serial queue)"
      via: "wrapper sets -W per QUEUE arg"
      pattern: "serial.*5760|QUEUE.*serial.*5760"
---

<objective>
Wave 2 — R1 trait-pair coloc.susie audit-driven cache-invalidated re-fire. Re-fire all 28 R1 trait-pair `coloc.susie` attempts (the non-SH2B3 pairs in `results/multitrait/coloc_manifest.tsv`) under git HEAD which now has commits `069b34f` (variant-ID matcher in `run_qtl_coloc.R`) + `7d54183` (LD-panel-rsid override in `run_susie_rss.R`) + `02c4404` (`max_iterations → max_iter`) as ancestors. The audit-V2 finding (HQ#2(iii)) is that the manuscript reframes 28/28 empty PP.H3/PP.H4 columns at non-SH2B3 pairs as Layer-2-attrition-under-real-LD, but the variant-ID-format-fix commits were never re-applied to those 28 pairs. The Wave 2 SH2B3 R2 re-fire produced 9 working PP rows for SH2B3 EUR specifically; without re-firing the same fixes against the 28 non-SH2B3 pairs, the current state reads as result-conditional analysis selection.

Purpose: Falsification test on the Layer-2-attrition-under-matched-LD framing. Two pre-registered outcome branches (per OSF amendment paragraph (e)):
- `BRANCH_R1_BUG` — post-refire produces non-empty PP.H3/PP.H4 rows in the previously-empty 28. Layer-2-attrition framing is empirically refuted; new PP rows replace 28/28 in manuscript Table 3.
- `BRANCH_R1_STRUCTURAL` — post-refire holds at 28/28 empty (or near-empty). Layer-2-attrition framing is empirically supported; the variant-ID-format-fix commits cited as a falsification test that did not falsify.

Either branch is publishable. The current "fixes applied to SH2B3 only" framing is the only branch not on this list. This is audit-driven re-analysis, NOT a fix or revision.

Output: 28 R1 R-fired JSONs at `results/multitrait/coloc_susie/*.json` (cache-invalidated against pre-W2 backup); rebuilt `results/multitrait/coloc_summary.tsv`; post-refire md5 captured; `D-TA-R3-W2-BRANCH_R1_*` recorded in ta-r3-CONTEXT.md.
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
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md
@CLAUDE.md

<interfaces>
<!-- W1 produced these — W2 reads -->
- D-TA-R3-W1-BRANCH_PSD_* — W2 reads this for downstream framing implication only; W2 fires regardless of W1 branch
- ta-r3-CONTEXT.md — W2 appends D-TA-R3-W2-BRANCH_R1_* to existing scaffold

<!-- Existing files Wave 2 reads / mutates -->
- results/multitrait/coloc_manifest.tsv — Stage 2 manifest (28 R1 rows + 9 SH2B3 R2 rows; W2 derives the 28 R1 targets from this)
- results/multitrait/coloc_susie/*.json — 28 R1 JSONs (mutate target; backup via mv before re-fire)
- results/multitrait/coloc_susie_R2/*.json — 9 SH2B3 R2 JSONs (DO NOT TOUCH; W2 only force-reruns the R1 pair targets)
- results/multitrait/coloc_summary.tsv — md5 baseline `558fca45ac37d901028c64429cdecc12` per .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv L2 (will SHIFT in W2; intentional)
- src/snakemake/rules/coloc.smk — rule run_coloc_susie (manifest-driven; reads pair_id wildcard)
- src/snakemake/rules/multitrait.smk — rule build_coloc_manifest + rule summarize_coloc_results
- /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake — Snakemake 7.32.4 with Python 3.11 (per memory project_python_311_pin.md; never invoke from miniconda3 base)
- config/bsub_wrapper.sh — sets -W per queue (serial=5760 min)

<!-- HEAD ancestor invariants (per OSF amendment posting verification) -->
- `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` MUST return 3 at W2 start

<!-- W2 outcome-branch decision matrix (pre-registered in OSF amendment paragraph (e)) -->
- BRANCH_R1_BUG: post-refire produces non-empty PP.H3/PP.H4 rows in any of the previously-empty 28 — counts >9 non-empty PP rows in coloc_summary.tsv (the existing 9 SH2B3 R2 rows are the floor; >9 means new R1 rows non-empty)
- BRANCH_R1_STRUCTURAL: post-refire holds at 9 non-empty PP rows (only the SH2B3 R2 rows; the 28 R1 stay empty) — Layer-2-attrition empirically supported

<!-- Pitfall: cache invalidation overrun risk (security threat model row 3) -->
- Mitigated by: --keep-going + --rerun-incomplete (Snakemake retries failed jobs without aborting batch; partial outputs do not block dispatch); post-fire md5 capture
- Mitigated by: timestamped mv backup (NOT rm) — rollback path preserved on disk

<!-- Compute envelope -->
- ~10-30 min per pair on serial queue with la_multitrait_r env; 28 pairs aggregate ~5-15 hr; parallelizable across 50 LSF slots -> wall ~30 min (most jobs may be no-ops if structurally still empty)
- Memory: 32 GB per Snakemake-dispatched job (matches W4 envelope)

<!-- LSF dispatch (Snakemake LSF profile) -->
- Queue: serial; -W: 5760 min via bsub_wrapper.sh; -n 1; -R "rusage[mem=32000]"
- Profile: config/cluster_lsf (already in repo per ta-sh2b3-W4 PLAN.md L207)
- Snakemake flags: --use-conda --conda-prefix .snakemake/conda --jobs 50 --keep-going --rerun-incomplete --latency-wait 120 --forcerun run_coloc_susie
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Pre-fire HEAD ancestor + cache-backup gate; identify 28 R1 R-pair targets; capture pre-W2 baseline + backup R1 cache to timestamped path</name>
  <files>
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv
    results/multitrait/coloc_susie.preFix.bak.20260504_HHMMSS/
  </files>
  <read_first>
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 2 Tasks (skeleton)" lines 114-128 (PRIMARY SPEC; tasks 1-2 source)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — R1 trait-pair coloc.susie cache-invalidated re-fire" lines 67-73 (W2 outcome-branch decision matrix; AUTHORITATIVE)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md §"Task 1 step 1 + step 3" (predecessor cache-invalidation pattern; mirror Pitfall 5 timestamped backup)
    - results/multitrait/coloc_manifest.tsv (28 R1 + 9 SH2B3 R2 = 37 rows; W2 derives R1 target subset)
    - results/multitrait/coloc_susie_R2/ (9 JSONs to PRESERVE; W2 force-reruns only R1, not R2)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W1-BRANCH_PSD_* MUST be resolved before W2 fires; W1 must have completed)
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks:** Verify W1 outcome recorded (W1 must have completed before W2 starts), HEAD ancestors include the 3 fix commits, bsub_wrapper.sh enforces -W=5760.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # W1 must have resolved its outcome branch
       grep -qE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" \
         .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md || \
         { echo "ABORT: W1 outcome branch not resolved in ta-r3-CONTEXT.md; W2 cannot fire"; exit 1; }
       echo "PASS: W1 outcome resolved"

       # HEAD ancestor invariants (per OSF amendment verification rule)
       N_ANCESTORS=$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')
       [ "$N_ANCESTORS" -eq 3 ] || \
         { echo "ABORT: required commit ancestors missing (need 069b34f + 7d54183 + 02c4404; got $N_ANCESTORS)"; exit 1; }
       echo "PASS: 3/3 commit ancestors verified"

       # LSF wall-time configuration
       grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh || \
         { echo "ABORT: bsub_wrapper.sh does not enforce -W=5760 for serial queue"; exit 1; }
       echo "PASS: bsub_wrapper.sh enforces -W=5760 (96 hr) for serial queue"

       # Snakemake binary
       SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
       [ -x "$SMK" ] || { echo "ABORT: Snakemake binary missing at $SMK (per memory project_python_311_pin.md)"; exit 1; }
       echo "PASS: Snakemake 7.32.4 (Python 3.11) binary available"
       ```

    2. **Identify 28 R1 R-pair targets** by reading `results/multitrait/coloc_manifest.tsv` and excluding the 9 SH2B3 R2 pair_ids (the SH2B3 R2 fire was the W2 work in the predecessor `ta-sh2b3-canonical-and-cache-refresh` phase; those rows must remain untouched per plan-of-plans risk register row 4).

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # Build the SH2B3 R2 exclusion set from the existing R2 outputs
       SH2B3_R2_PAIRS=$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | \
                          sed 's|.*/||; s|\.json$||')
       echo "$SH2B3_R2_PAIRS" | head

       # Build the R1 target list (manifest minus SH2B3 R2 pairs)
       OUT=.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv
       head -1 results/multitrait/coloc_manifest.tsv > "$OUT"
       awk -F'\t' -v exclude="$SH2B3_R2_PAIRS" '
         BEGIN {
           n = split(exclude, arr, "\n")
           for (i=1; i<=n; i++) ex[arr[i]] = 1
         }
         NR > 1 && !($1 in ex) { print }
       ' results/multitrait/coloc_manifest.tsv >> "$OUT"

       # Verify exactly 28 R1 targets
       N_TARGETS=$(awk 'NR>1' "$OUT" | wc -l)
       [ "$N_TARGETS" -eq 28 ] || \
         { echo "WARN: expected 28 R1 targets; got $N_TARGETS. Check coloc_manifest.tsv schema + SH2B3 R2 exclusion logic."; }
       echo "R1 targets: $N_TARGETS rows in $OUT"
       awk -F'\t' 'NR>1 {print $1}' "$OUT" | sort | head -10
       ```

    3. **Capture pre-W2 baseline empty-PP-row count** in `coloc_summary.tsv`. The audit-V2 §HQ#2(iii) baseline claim is 28/28 empty PP.H3/PP.H4 at non-SH2B3 pairs. The 9 SH2B3 R2 rows have non-empty PP. So the baseline for "non-empty PP rows" should be exactly 9 if the audit-V2 narrative is correct.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       BASELINE=.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv
       echo -e "metric\tcount" > "$BASELINE"

       # Total pair rows (excluding header)
       TOTAL_ROWS=$(awk 'NR>1' results/multitrait/coloc_summary.tsv | wc -l)
       echo -e "total_pair_rows\t$TOTAL_ROWS" >> "$BASELINE"

       # Non-empty PP.H4 rows: identify the PP.H4 column and count rows where it's non-empty
       # Schema check: the column index varies by manifest version; scan header to find PP.H4 column
       PPH4_COL=$(head -1 results/multitrait/coloc_summary.tsv | tr '\t' '\n' | grep -n -E "^PP\.H4(\.abf)?$" | head -1 | cut -d: -f1)
       if [ -z "$PPH4_COL" ]; then
         echo "WARN: PP.H4 column not found in header; falling back to column 6 (per common Stage 2 schema)"
         PPH4_COL=6
       fi
       echo -e "PP.H4_column_index\t$PPH4_COL" >> "$BASELINE"

       NONEMPTY_PPH4=$(awk -F'\t' -v c=$PPH4_COL 'NR>1 && $c != "" && $c != "NA" {n++} END {print n+0}' results/multitrait/coloc_summary.tsv)
       echo -e "non_empty_PP.H4_rows\t$NONEMPTY_PPH4" >> "$BASELINE"

       # Capture md5 baseline (pre-W2)
       MD5_BASELINE=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       echo -e "coloc_summary.md5_pre_W2\t$MD5_BASELINE" >> "$BASELINE"

       cat "$BASELINE"
       echo "(Expected: non_empty_PP.H4_rows=9 if audit-V2 §HQ#2(iii) baseline holds; W2 outcome will compare against this)"
       ```

    4. **Backup the R1 cache to a timestamped path** (per Pitfall 5 from ta-sh2b3-W4: timestamped uniqueness, idempotent across phase fires; mv NOT rm). Note: this backs up ONLY the R1 cache (`results/multitrait/coloc_susie/`), NOT the R2 cache (`results/multitrait/coloc_susie_R2/`).

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       TS=$(date +%Y%m%d_%H%M%S)
       BAK="results/multitrait/coloc_susie.preFix.bak.${TS}"

       # Pitfall 5 check: avoid name collision
       if [ -d "$BAK" ]; then
         echo "ABORT: backup path $BAK already exists (timestamp collision)"
         exit 1
       fi

       # Move (NOT rm) the R1 cache to backup
       mv results/multitrait/coloc_susie "$BAK"
       mkdir -p results/multitrait/coloc_susie

       # Verify R2 cache untouched (plan-of-plans risk register row 4)
       N_R2=$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)
       [ "$N_R2" -eq 9 ] || \
         { echo "ABORT: R2 cache count changed (expected 9; got $N_R2); risk register row 4 violation"; exit 1; }
       echo "PASS: R2 cache untouched ($N_R2 SH2B3 R2 JSONs preserved)"
       echo "Pre-W2 R1 backup at: $BAK"
       echo "$BAK" > .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-backup-path.txt
       ```

    5. **Atomic commit** with explicit paths only:

       ```bash
       git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-backup-path.txt
       # Note: results/multitrait/coloc_susie.preFix.bak.* and the empty results/multitrait/coloc_susie/ are NOT committed
       # (large; gitignored or path-tracked via the backup-path.txt sentinel)
       git commit -m "feat(ta-r3, W2): identify 28 R1 R-pair targets + capture pre-W2 baseline + backup R1 cache to timestamped path (audit-driven re-analysis)"
       ```
  </action>
  <acceptance_criteria>
    - W1 outcome resolved before W2 fires: `grep -cE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - HEAD ancestor invariant: `git log --oneline | grep -cE '069b34f|7d54183|02c4404'` returns 3.
    - bsub_wrapper.sh enforces -W=5760 for serial queue: `grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh` returns 0.
    - Snakemake 7.32.4 binary available: `[ -x /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake ]`.
    - R1 target manifest has exactly 28 data rows: `[ "$(awk 'NR>1' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv | wc -l)" -eq 28 ]` (or documented exception if manifest schema changed).
    - No SH2B3 R2 pair_ids in R1 target manifest: `awk -F'\t' 'NR>1 {print $1}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv | grep -c "^SH2B3_12q24__EUR__"` returns 0.
    - Pre-W2 baseline TSV has ≥ 4 rows (header + total_pair_rows + PP.H4_column_index + non_empty_PP.H4_rows + md5).
    - R1 cache backup directory exists with timestamped suffix: `ls -d results/multitrait/coloc_susie.preFix.bak.[0-9_]* 2>/dev/null | wc -l` returns ≥ 1.
    - R2 cache preserved (NOT touched): `ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json | wc -l` returns 9.
    - `results/multitrait/coloc_susie/` exists as empty target dir for re-fire output.
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W2.*identify.*28 R1.*audit-driven re-analysis"` matches.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -qE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && [ "$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')" -eq 3 ] && grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh && [ -x /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake ] && [ "$(awk 'NR>1' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv | wc -l)" -eq 28 ] && [ "$(awk -F'\t' 'NR>1 {print $1}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv | grep -c '^SH2B3_12q24__EUR__')" -eq 0 ] && [ "$(ls -d results/multitrait/coloc_susie.preFix.bak.[0-9_]* 2>/dev/null | wc -l)" -ge 1 ] && [ "$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)" -eq 9 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Pre-fire gates cleared (W1 resolved, HEAD ancestors verified, LSF wrapper config verified). 28 R1 R-pair targets identified (manifest minus 9 SH2B3 R2 pairs). Pre-W2 baseline captured with non-empty PP.H4 row count (expected 9 = SH2B3 R2 rows; the 28 R1 should be empty per audit-V2 §HQ#2(iii)). R1 cache backed up to timestamped path (mv NOT rm; rollback preserved). R2 cache untouched (plan-of-plans risk register row 4 mitigated). Atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Force cache invalidation + Snakemake re-fire of 28 R1 targets via /rs1/.../smoke_dev/snakemake (Python 3.11) on serial LSF queue with --use-conda --jobs 50 --keep-going --rerun-incomplete; rebuild coloc_summary.tsv; capture post-refire md5</name>
  <files>
    results/multitrait/coloc_susie/  # 28 R1 JSONs re-fired
    results/multitrait/coloc_summary.tsv  # rebuilt
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt
    logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv (Task 1 output; the 28 pair_ids to force-rerun)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv (Task 1 output; non-empty PP.H4 baseline = 9)
    - src/snakemake/rules/coloc.smk (rule run_coloc_susie; manifest-driven; reads pair_id wildcard at line 88 per ta-sh2b3-W2 PLAN.md L86)
    - src/snakemake/rules/multitrait.smk (rule summarize_coloc_results; rebuilds coloc_summary.tsv)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md §"Task 1 step 3 + step 4" (predecessor Snakemake re-fire pattern; mirror flag set)
    - config/cluster_lsf (Snakemake LSF profile; transparently sets serial queue + bsub_wrapper -W=5760)
  </read_first>
  <action>
    1. **Re-verify LSF + Snakemake gates** (paranoid double-check from Task 1; both Tasks 1 and 2 may run in different agent invocations):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh || \
         { echo "ABORT: wrapper config drift"; exit 1; }
       SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
       [ -x "$SMK" ] || { echo "ABORT: Snakemake binary missing"; exit 1; }
       echo "PASS: gates re-verified"
       ```

    2. **Force-rerun the 28 R1 trait-pair coloc.susie targets** via Snakemake. The targets are addressed by the Snakemake rule `run_coloc_susie` (per src/snakemake/rules/coloc.smk:88) using pair_id wildcards drawn from `results/multitrait/coloc_manifest.tsv`. The R2 SH2B3 pairs are NOT in `results/multitrait/coloc_susie/` (they live in `coloc_susie_R2/`); the coloc_manifest.tsv may or may not include the R2 pair_ids. To be safe, the Snakemake invocation explicitly enumerates the 28 R1 target paths via `--forcerun results/multitrait/coloc_susie/{pair_id}.json` rather than wildcard expansion.

       ```bash
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       export LSF_UNIT_FOR_LIMITS=GB
       mkdir -p logs/ta_r3_W2_r1_refire

       SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
       LOG=logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log
       : > "$LOG"

       # Build the explicit target list from the R1 targets manifest
       TARGETS=$(awk -F'\t' 'NR>1 {printf "results/multitrait/coloc_susie/%s.json ", $1}' \
                   .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv)
       N_TARGETS=$(echo $TARGETS | tr ' ' '\n' | grep -c "^results/multitrait/coloc_susie/")
       echo "Dispatching $N_TARGETS Snakemake R1 targets" | tee -a "$LOG"

       "$SMK" \
         --profile config/cluster_lsf \
         --use-conda \
         --conda-prefix .snakemake/conda \
         --jobs 50 \
         --keep-going \
         --rerun-incomplete \
         --latency-wait 120 \
         --forcerun run_coloc_susie \
         $TARGETS \
         2>&1 | tee -a "$LOG"

       SNAKE_RC=${PIPESTATUS[0]}
       echo "Snakemake exit code: $SNAKE_RC" | tee -a "$LOG"
       # --keep-going may exit non-zero even if most jobs succeeded; this is INTENTIONAL.
       # Do NOT abort on non-zero; rely on the count check in step 4.
       ```

    3. **Monitor LSF jobs to completion** (Snakemake submits async; poll until no run_coloc_susie jobs remain).

       ```bash
       while bjobs 2>&1 | grep -qE "run_coloc_susie|PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running: $(bjobs 2>&1 | grep -cE 'PEND|RUN')"
         sleep 300  # 5-min poll
       done
       echo "[$(date +%H:%M:%S)] All W2 LSF jobs done." | tee -a "$LOG"
       ```

    4. **Verify all 28 R1 outputs landed** (re-fire success or documented failure per --keep-going semantics):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       missing=0
       partial=0
       while IFS=$'\t' read -r pair_id rest; do
         f="results/multitrait/coloc_susie/${pair_id}.json"
         if [ ! -f "$f" ]; then
           echo "MISSING: $f"
           missing=$((missing+1))
         else
           # JSON well-formed?
           jq empty "$f" 2>/dev/null || { echo "MALFORMED: $f"; partial=$((partial+1)); }
         fi
       done < <(awk 'NR>1' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv)
       echo "missing=$missing; malformed=$partial; expected=28"
       # Note: per --keep-going, missing JSONs are acceptable IF the underlying run_coloc_susie
       # failed legitimately (e.g., insufficient overlap). The W2 BRANCH classification reads
       # what's actually on disk; missing JSONs are treated as "still empty" for the count.
       ```

    5. **Rebuild coloc_summary.tsv** by re-running the Snakemake aggregator rule. The rule `summarize_coloc_results` lives in `src/snakemake/rules/multitrait.smk` and reads all per-pair JSONs in `results/multitrait/coloc_susie/` (and may also consume `results/multitrait/coloc_susie_R2/` per ta-sh2b3-W5 merge). Force a clean rebuild:

       ```bash
       cd /rs1/researchers/c/ckclinto/coloc_analysis
       "$SMK" \
         --profile config/cluster_lsf \
         --use-conda \
         --conda-prefix .snakemake/conda \
         --jobs 1 \
         --forcerun summarize_coloc_results \
         results/multitrait/coloc_summary.tsv \
         2>&1 | tee -a "$LOG"
       ```

       If `summarize_coloc_results` is local-only (not LSF-dispatched), it should complete in a few minutes.

    6. **Capture post-refire md5** of coloc_summary.tsv to a phase-internal txt file. This md5 will SHIFT relative to the ta-sh2b3-W7 baseline `558fca45ac37d901028c64429cdecc12`; the shift is intentional and W5 will append the successor row to `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv`.

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       POST_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       echo "$POST_MD5  results/multitrait/coloc_summary.tsv" > .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt
       cat .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt

       # Verify it differs from ta-sh2b3-W7 baseline (intentional)
       BASELINE_MD5=$(awk -F'\t' '$1 == "results/multitrait/coloc_summary.tsv" {print $2; exit}' \
                      .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv)
       if [ "$POST_MD5" = "$BASELINE_MD5" ]; then
         echo "WARN: post-W2 coloc_summary.tsv md5 matches ta-sh2b3-W7 baseline; aggregator may not have re-fired. Investigate."
       else
         echo "PASS: post-W2 md5 ($POST_MD5) differs from ta-sh2b3-W7 baseline ($BASELINE_MD5); shift is intentional"
       fi
       ```

    7. **Verify R2 cache + 9 SH2B3 R2 rows preserved** (plan-of-plans risk register row 4):

       ```bash
       N_R2=$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)
       [ "$N_R2" -eq 9 ] || \
         { echo "ABORT: R2 cache count changed (expected 9; got $N_R2); risk register row 4 violation"; exit 1; }

       # Count rows in coloc_summary.tsv that match SH2B3_12q24__EUR__ pattern
       N_SH2B3_ROWS=$(awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)
       [ "$N_SH2B3_ROWS" -ge 9 ] || \
         { echo "ABORT: SH2B3 R2 rows missing from rebuilt coloc_summary.tsv (expected ≥9; got $N_SH2B3_ROWS); risk register row 4 violation"; exit 1; }
       echo "PASS: SH2B3 R2 rows preserved ($N_SH2B3_ROWS rows present in rebuilt summary)"
       ```

    8. **Atomic commit** with explicit paths:

       ```bash
       git add results/multitrait/coloc_summary.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt \
               logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log
       # Note: results/multitrait/coloc_susie/*.json (28 R1 re-fired) are typically gitignored
       # (large; regenerable from manifest + HEAD code); commit only summary + md5 + log
       grep -n "results/multitrait/coloc_susie" .gitignore || \
         git add results/multitrait/coloc_susie/*.json
       git commit -m "feat(ta-r3, W2): cache-invalidate + Snakemake re-fire of 28 R1 trait-pair coloc.susie targets (audit-driven re-analysis; HEAD = 069b34f + 7d54183 + 02c4404)"
       ```
  </action>
  <acceptance_criteria>
    - 28 R1 target JSONs attempted (the count of files in `results/multitrait/coloc_susie/*.json` matches the 28 R1 manifest rows, OR --keep-going legitimately produced fewer with documented per-target failures in the log).
    - Snakemake re-fire log committed: `[ -s logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log ]`.
    - Snakemake invocation used the right binary (Python 3.11 pin per memory `project_python_311_pin.md`): `grep -E "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake|smoke_dev.*snakemake" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log` returns ≥ 1 hit.
    - Snakemake invocation used the required flag set: `grep -E "use-conda.*conda-prefix|--keep-going|--rerun-incomplete|--latency-wait" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log` returns ≥ 1 hit.
    - Snakemake invocation used `--forcerun run_coloc_susie`: `grep "forcerun.*run_coloc_susie" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log` returns ≥ 1 hit.
    - Post-refire coloc_summary.tsv exists + non-empty.
    - Post-refire md5 captured: `[ -s .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt ]`.
    - Post-refire md5 differs from ta-sh2b3-W7 baseline (intentional shift): `awk '{print $1}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt` does NOT equal `558fca45ac37d901028c64429cdecc12`.
    - 9 SH2B3 R2 JSONs preserved (untouched): `ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json | wc -l` returns 9.
    - SH2B3 R2 rows preserved in rebuilt summary: `awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l` returns ≥ 9.
    - HEAD ancestor invariant: `git log --oneline | grep -cE '069b34f|7d54183|02c4404'` returns 3.
    - Atomic commit landed.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -s logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log ] && grep -qE "use-conda|--keep-going|--rerun-incomplete" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log && grep -q "forcerun.*run_coloc_susie" logs/ta_r3_W2_r1_refire/r1_refire_dispatch.log && [ -s .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt ] && [ "$(awk '{print $1}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt)" != "558fca45ac37d901028c64429cdecc12" ] && [ "$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)" -eq 9 ] && [ "$(awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)" -ge 9 ] && [ "$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')" -eq 3 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    Cache invalidation complete: 28 R1 R-pair targets force-reran via Snakemake `--forcerun run_coloc_susie` under HEAD code with 069b34f + 7d54183 + 02c4404 ancestors. coloc_summary.tsv rebuilt; md5 SHIFTED (intentional; W5 captures successor row). 9 SH2B3 R2 rows preserved (risk register row 4 mitigated). LSF dispatch log committed. Honest-framing-lock manuscript md5 unchanged.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Classify W2 outcome branch (BRANCH_R1_BUG | BRANCH_R1_STRUCTURAL) per OSF amendment paragraph (e) decision matrix; write D-TA-R3-W2-BRANCH_R1_* to ta-r3-CONTEXT.md</name>
  <files>
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-pre_refire_baseline.tsv (pre-W2 non-empty PP.H4 row count = 9)
    - results/multitrait/coloc_summary.tsv (Task 2 output; rebuilt aggregator)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-targets.tsv (28 R1 pair_ids to evaluate)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — R1 trait-pair coloc.susie cache-invalidated re-fire" lines 67-73 (W2 outcome-branch decision matrix; AUTHORITATIVE)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md §"Task 2 step 3 + step 4" (predecessor outcome-recording pattern; mirror for D-TA-R3-W2-BRANCH_R1_*)
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (target file; use Edit to replace D-TA-R3-W2-BRANCH_R1_*: PENDING placeholder)
  </read_first>
  <action>
    1. **Compute post-refire empty-vs-non-empty PP.H4 row counts** for the 28 R1 pair_ids:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       OUT=.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv
       echo -e "metric\tcount" > "$OUT"

       # Identify PP.H4 column index from coloc_summary.tsv header
       PPH4_COL=$(head -1 results/multitrait/coloc_summary.tsv | tr '\t' '\n' | grep -n -E "^PP\.H4(\.abf)?$" | head -1 | cut -d: -f1)
       [ -z "$PPH4_COL" ] && PPH4_COL=6
       echo -e "PP.H4_column_index\t$PPH4_COL" >> "$OUT"

       # Total non-empty PP.H4 rows post-refire
       POST_NONEMPTY=$(awk -F'\t' -v c=$PPH4_COL 'NR>1 && $c != "" && $c != "NA" {n++} END {print n+0}' results/multitrait/coloc_summary.tsv)
       echo -e "post_refire_non_empty_PP.H4_rows\t$POST_NONEMPTY" >> "$OUT"

       # SH2B3 R2 rows non-empty (must be 9; floor)
       SH2B3_NONEMPTY=$(awk -F'\t' -v c=$PPH4_COL 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/ && $c != "" && $c != "NA" {n++} END {print n+0}' results/multitrait/coloc_summary.tsv)
       echo -e "SH2B3_R2_non_empty_PP.H4_rows\t$SH2B3_NONEMPTY" >> "$OUT"

       # R1 (non-SH2B3) rows non-empty
       R1_NONEMPTY=$(awk -F'\t' -v c=$PPH4_COL 'NR>1 && $1 !~ /^SH2B3_12q24__EUR__/ && $c != "" && $c != "NA" {n++} END {print n+0}' results/multitrait/coloc_summary.tsv)
       echo -e "R1_non_empty_PP.H4_rows\t$R1_NONEMPTY" >> "$OUT"

       cat "$OUT"
       ```

    2. **Apply OSF amendment paragraph (e) decision matrix** to classify the W2 outcome branch:
       - BRANCH_R1_BUG: R1_non_empty_PP.H4_rows ≥ 1 (post-refire produces non-empty PP rows in any of the previously-empty 28)
       - BRANCH_R1_STRUCTURAL: R1_non_empty_PP.H4_rows == 0 (post-refire holds at 0 for the 28 R1 pairs; the 9 SH2B3 R2 rows still non-empty)

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       R1_NONEMPTY=$(awk -F'\t' '$1 == "R1_non_empty_PP.H4_rows" {print $2}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv)
       SH2B3_NONEMPTY=$(awk -F'\t' '$1 == "SH2B3_R2_non_empty_PP.H4_rows" {print $2}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv)

       if [ "$R1_NONEMPTY" -ge 1 ]; then
         BRANCH=BRANCH_R1_BUG
       else
         BRANCH=BRANCH_R1_STRUCTURAL
       fi
       echo "Computed branch: $BRANCH (R1 non-empty = $R1_NONEMPTY; SH2B3 R2 non-empty = $SH2B3_NONEMPTY)"
       ```

    3. **Append D-TA-R3-W2-BRANCH_R1_* to ta-r3-CONTEXT.md** by Editing the existing PENDING placeholder. Use the Edit tool to replace:

       FROM:
       ```
       ### D-TA-R3-W2-BRANCH_R1_*: PENDING (Wave 2 outcome)

       **Status:** PENDING — Wave 2 Task 3 classifies into exactly one of:
       - `BRANCH_R1_BUG` — post-refire produces non-empty PP rows in previously-empty 28
       - `BRANCH_R1_STRUCTURAL` — post-refire holds at 28/28 empty (or near-empty)
       ```

       TO (substitute concrete values):
       ```markdown
       ### D-TA-R3-W2-BRANCH_R1_<BRANCH>: <BRANCH> (Wave 2 outcome)

       **Recorded:** <ISO-8601 timestamp>

       **HEAD ancestors verified:** 069b34f + 7d54183 + 02c4404 (3/3 in `git log` at W2 dispatch time)

       **Pre-refire baseline:**

       | metric | count |
       |---|---|
       | total_pair_rows | <pre_total> |
       | non_empty_PP.H4_rows (pre-W2) | <pre_nonempty> (expected: 9 = SH2B3 R2 rows; 28 R1 empty per audit-V2 §HQ#2(iii)) |
       | coloc_summary.tsv md5 (pre-W2) | <pre_md5> |

       **Post-refire status:**

       | metric | count |
       |---|---|
       | total_pair_rows | <post_total> |
       | non_empty_PP.H4_rows (post-W2) | <post_nonempty> |
       | SH2B3_R2_non_empty_PP.H4_rows | <sh2b3_nonempty> (must be ≥9; risk register row 4) |
       | R1_non_empty_PP.H4_rows | <r1_nonempty> |
       | coloc_summary.tsv md5 (post-W2) | <post_md5> (md5 SHIFTED from baseline; W5 captures successor row) |

       **Detailed numerics:** [.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv](ta-r3-W2-post_refire_outcome.tsv)

       **Cowork-side branch (informational; manuscript edits OUT of phase scope):** Per OSF amendment paragraph (e), the manuscript v5 narrative branches:
       - BRANCH_R1_BUG → Layer-2-attrition-under-matched-LD framing empirically refuted; new PP rows reported in manuscript Table 3 with variant-ID-format-fix commit hashes cited as the propagation gap
       - BRANCH_R1_STRUCTURAL → Layer-2-attrition framing empirically supported; the variant-ID-format-fix commits cited as a falsification test that did not falsify

       **W3 gate implication:** Already resolved by W1 outcome (W3 gate is W1-driven, not W2-driven). W2 outcome flows to manuscript narrative; does NOT change W3 gate disposition.
       ```

       Use the `Edit` tool to perform the replacement (substitute concrete values for all `<...>` placeholders).

    4. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
       git commit -m "docs(ta-r3, W2): record D-TA-R3-W2-${BRANCH} (audit-driven re-analysis; R1 non-empty=${R1_NONEMPTY}, SH2B3 R2 non-empty=${SH2B3_NONEMPTY})"
       ```
  </action>
  <acceptance_criteria>
    - File `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv` exists with ≥ 4 data rows.
    - W2 outcome-branch token recorded in ta-r3-CONTEXT.md with exactly one of BUG, STRUCTURAL: `grep -cE "D-TA-R3-W2-BRANCH_R1_(BUG|STRUCTURAL)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - PENDING placeholder removed: `grep -c "D-TA-R3-W2-BRANCH_R1_\\*: PENDING" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns 0.
    - Pre/post comparison block present: `grep -c "Pre-refire baseline\\|Post-refire status" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 2.
    - HEAD ancestor invariant: `git log --oneline | grep -cE '069b34f|7d54183|02c4404'` returns 3.
    - SH2B3 R2 rows preserved: `awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l` returns ≥ 9 (risk register row 4).
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W2.*D-TA-R3-W2.*audit-driven re-analysis"` matches.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_outcome.tsv ] && [ "$(grep -cE 'D-TA-R3-W2-BRANCH_R1_(BUG|STRUCTURAL)' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(grep -c 'D-TA-R3-W2-BRANCH_R1_\*: PENDING' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -eq 0 ] && [ "$(awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)" -ge 9 ] && [ "$(git log --oneline | grep -cE '069b34f|7d54183|02c4404')" -eq 3 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    W2 outcome branch classified per OSF amendment paragraph (e) decision matrix and recorded in ta-r3-CONTEXT.md. Pre/post comparison block landed with R1 non-empty count + SH2B3 R2 preservation count + md5 shift. SH2B3 R2 rows preserved (risk register row 4). Honest-framing-lock manuscript md5 unchanged. W3 substrate ready (gate already W1-driven; W2 outcome flows to manuscript narrative only).
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pre-W2 R1 cache (results/multitrait/coloc_susie/) ↔ Post-W2 Snakemake re-fire | Timestamped mv backup (NOT rm) preserves rollback path per Pitfall 5; R2 cache (coloc_susie_R2/) untouched |
| HEAD git ancestors (069b34f + 7d54183 + 02c4404) ↔ Snakemake re-fire under HEAD code | HEAD ancestor invariant verified at gate; missing commit aborts non-zero exit |
| Snakemake env pin (smoke_dev / Python 3.11) ↔ miniconda3 base (Python 3.13) | Per memory project_python_311_pin.md: never invoke from miniconda3 base; absolute path to /rs1/.../smoke_dev/bin/snakemake |
| coloc_summary.tsv md5 (W7 baseline 558fca45ac37...) ↔ post-W2 md5 (will SHIFT) | Shift is intentional per OSF amendment "What is not changing" §md5 invariant rule; W5 appends successor row to md5_baseline.tsv (NOT overwrites) |
| Cache-invalidation overrun risk ↔ --keep-going + --rerun-incomplete + post-fire md5 | Snakemake flags ensure partial outputs do not block dispatch; post-fire md5 captured for verification |
| Multi-terminal git staging on GPFS ↔ explicit-path commits | Per `.planning/feedback_multi_terminal_staging.md`: never `git add .` / `-A` |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-TA-R3-W2-01 | T (Tampering) | results/multitrait/coloc_susie/ pre-W2 cache | mitigate | Task 1 step 4 timestamped mv to results/multitrait/coloc_susie.preFix.bak.${TS}/ (Pitfall 5; rollback preserved); never rm |
| T-TA-R3-W2-02 | T (Tampering) | results/multitrait/coloc_susie_R2/ untouched (9 SH2B3 R2 rows preservation) | mitigate | Task 1 step 4 + Task 2 step 7 explicit count check (=9); risk register row 4 |
| T-TA-R3-W2-03 | T (Tampering) | HEAD git ancestors required | mitigate | Tasks 1+2 step 1 explicit `git log | grep -cE '069b34f|7d54183|02c4404'` returns 3; abort otherwise |
| T-TA-R3-W2-04 | I (Information disclosure) | Implicit `git add .` could stage results_identity_ld/ (DEC-2026-04-25-01) | mitigate | Every commit task uses explicit file paths only |
| T-TA-R3-W2-05 | I (Information disclosure) | Honest-framing-lock manuscript edit | accept | OUT of phase scope per OSF amendment "What is not changing" |
| T-TA-R3-W2-06 | D (Denial of service) | Cache-invalidation overrun (long-running rebuild stalls) | mitigate | Snakemake --keep-going + --rerun-incomplete + post-fire md5 capture; partial outputs do not block dispatch (per security_threat_model row in <your_task>) |
| T-TA-R3-W2-07 | D (Denial of service) | LSF jobs killed by 30-min queue default RUNLIMIT | mitigate | bsub_wrapper.sh transparently sets -W=5760 for serial queue; Tasks 1+2 step 1 verify wrapper config |
| T-TA-R3-W2-08 | E (Elevation of privilege) | Outcome-branch classifier silently picks favorable branch | mitigate | Branch decision rule pre-registered in OSF amendment paragraph (e); classifier in Task 3 step 2 reads outcome.tsv counts + applies rule verbatim |
</threat_model>

<verification>
- Pre-fire HEAD ancestor + cache-backup gate enforced (Task 1 step 1)
- 28 R1 R-pair targets identified (excluding 9 SH2B3 R2 pairs; Task 1 step 2)
- Pre-W2 baseline captured with non-empty PP.H4 row count = 9 (Task 1 step 3)
- R1 cache backed up to timestamped path (Task 1 step 4; mv NOT rm)
- Snakemake re-fire of 28 R1 targets via /rs1/.../smoke_dev/snakemake (Python 3.11) with required flag set (Task 2 step 2)
- coloc_summary.tsv rebuilt; md5 SHIFTED from ta-sh2b3-W7 baseline (Task 2 steps 5-6)
- 9 SH2B3 R2 rows preserved (risk register row 4 mitigated; Tasks 1+2 step 7)
- W2 outcome branch classified per OSF amendment paragraph (e) decision matrix (Task 3)
- D-TA-R3-W2-BRANCH_R1_* recorded in ta-r3-CONTEXT.md (Task 3)
- 3 atomic commits landed (Tasks 1, 2, 3)
- Honest-framing-lock manuscript md5 unchanged through all 3 tasks
</verification>

<success_criteria>
- 28 R1 R-pair targets identified + R1 cache backed up to timestamped path
- Snakemake re-fire fires `--forcerun run_coloc_susie` against 28 R1 targets via /rs1/.../smoke_dev/snakemake under HEAD (069b34f + 7d54183 + 02c4404)
- coloc_summary.tsv rebuilt; md5 captured to post_refire_md5.txt; md5 SHIFTED from ta-sh2b3-W7 baseline
- 9 SH2B3 R2 rows preserved (risk register row 4)
- W2 outcome branch (BUG/STRUCTURAL) recorded in ta-r3-CONTEXT.md per OSF amendment paragraph (e)
- bsub_wrapper.sh enforces -W=5760 for serial queue
- HEAD ancestor invariants 069b34f + 7d54183 + 02c4404 hold throughout
- Honest-framing-lock manuscript md5 unchanged (63fd81385590ffc8d23d45a0f0598959)
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-r1-trait-pair-coloc-refire-SUMMARY.md` with:
- D1 pre-fire HEAD ancestor + LSF wrapper gate (PASS/WARN/FAIL)
- D2 28 R1 R-pair targets identified (PASS/WARN/FAIL)
- D3 R1 cache backed up to timestamped path (PASS/WARN/FAIL; Pitfall 5)
- D4 Snakemake re-fire dispatched with required flag set (PASS/WARN/FAIL)
- D5 coloc_summary.tsv rebuilt with md5 shift (PASS/WARN/FAIL)
- D6 SH2B3 R2 rows preserved (PASS/WARN/FAIL; risk register row 4)
- D7 W2 outcome branch classified per OSF amendment paragraph (e) decision matrix (PASS/WARN/FAIL); record exact branch
- LSF wall-time observed vs projected (~30 min wall expected; most jobs may be no-ops if STRUCTURAL)
- Manuscript md5 invariant preservation (PASS/WARN/FAIL)
- post_refire_md5 (used by W5 to add successor row to md5_baseline.tsv)
- W3 GO/NO-GO status (W3 gate is W1-driven, NOT W2-driven; W2 outcome flows to manuscript narrative only)
- Honest-framing-lock invariant preservation
</output>
