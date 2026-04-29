---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 1
slug: W1-susie-rss-l-sweep
type: execute
wave: 1
depends_on: ["W0"]
files_modified:
  - results_lsweep_L15/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
  - results_lsweep_L15/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
  - results_lsweep_L15/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
  - results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
  - results_lsweep_L20/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
  - results_lsweep_L20/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
  - results_lsweep_L30/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
  - results_lsweep_L30/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
  - results_lsweep_L30/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  - logs/wave1_susie_lsweep_*.log
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "SH2B3 EUR per-trait SuSiE-RSS fits at L=15, L=20, L=30 land on disk for BMI + hypertension + stroke (9 fits total)"
    - "Each per-fit JSON reports L_used = the swept L value (per Pitfall 2 verification)"
    - "Convergence verification per fit: n_CS < L_used AND L_saturated == FALSE AND convergence_status matches ^converged_"
    - "Primary-result L is the lowest L value where ALL 3 SH2B3 EUR traits converge with n_CS < L (most likely L=20; recorded as PRIMARY_L in CONTEXT.md addendum for Wave 2 to consume)"
    - "Headline-numerator decision (D-TA-Wave1-headline) DEFERRED — Wave 1 only reports per-trait convergence outcomes; does NOT update 51/96 headline (per CONTEXT.md invariant 2)"
    - "LSF dispatch uses serial queue with -W set to queue max via bsub_wrapper.sh (5760 min = 96 hr; per memory feedback_lsf_queues.md + checker iter 1 NIT 2)"
  artifacts:
    - path: "results_lsweep_L15/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json"
      provides: "SuSiE-RSS BMI fit at L=15 (D-TA-02 sweep point 1)"
      contains: '"L_used": 15'
    - path: "results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json"
      provides: "SuSiE-RSS BMI fit at L=20 (D-TA-02 sweep point 2; primary candidate)"
      contains: '"L_used": 20'
    - path: "results_lsweep_L30/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json"
      provides: "SuSiE-RSS BMI fit at L=30 (D-TA-02 sweep point 3; upper bound)"
      contains: '"L_used": 30'
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md"
      provides: "PRIMARY_L decision recorded; D-TA-Wave1-headline outcomes recorded (deferred to Wave 6 narrative)"
      contains: "D-TA-Wave1-PRIMARY-L:"
  key_links:
    - from: "bin/fire_susie_lsweep.sh"
      to: "config/pipeline_lsweep_L{15,20,30}_overlay.yaml"
      via: "--configfile"
      pattern: "config/pipeline_lsweep_L\\$\\{L\\}_overlay.yaml"
    - from: "results_lsweep_L20/fine_mapping/susie/*.json"
      to: "Wave 2 canonical-pair coloc.susie input"
      via: "PRIMARY_L env var consumption"
      pattern: "PRIMARY_L=20"
    - from: "config/bsub_wrapper.sh"
      to: "bsub -W queue-max (serial=5760 min)"
      via: "wrapper sets -W based on QUEUE arg"
      pattern: "bsub_wrapper.*serial.*5760"
---

<objective>
Wave 1 — SH2B3 EUR L-sweep SuSiE-RSS re-fits. Re-fit BMI + hypertension + stroke at L ∈ {15, 20, 30} (9 fits) using the per-L policy YAML overlays scaffolded in Wave 0. Verify convergence per Zou et al. 2022 §Discussion (n_CS << L; L_saturated=FALSE; convergence_status starts with `converged_`). Identify the primary-result L (lowest L where all 3 traits converge non-saturated). Record the post-sweep convergence outcomes per trait so Wave 6 can make the D-TA-Wave1-headline narrative decision (recompute 51/96 vs disclose-as-column) — but DO NOT update the 51/96 headline in this wave (deferred per CONTEXT.md invariant 2 + D-TA-Wave1-headline).

Purpose: Issue 1 §HQ#2(i) closure. The audit-V2 reviewer flagged 3 of 5 SH2B3 EUR per-trait fits as non-converged at L=10 / niter=100 (BMI, hypertension, stroke); identity-LD hypertension carries `L_saturated=TRUE`. The L-sweep gives explicit sensitivity evidence per Zou 2022 §Discussion for the Supplementary Methods table. This is the substrate Wave 2 uses for canonical-pair coloc.susie.

Output: 9 per-fit JSONs + 9 .fit.rds binaries in parallel-output namespaces `results_lsweep_L{15,20,30}/`; PRIMARY_L recorded in CONTEXT.md; convergence verification report (per-trait per-L) committed to phase summary.
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
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W0-foundations-and-osf-gate-SUMMARY.md
@CLAUDE.md

<interfaces>
<!-- Wave 0 produced these — Wave 1 consumes -->
- bin/fire_susie_lsweep.sh — Wave 1 driver script (executable; mirrors fire_identity_ld_rerun pattern)
- config/susie_policy_L{15,20,30}.yaml — per-L SuSiE policy overlays
- config/pipeline_lsweep_L{15,20,30}_overlay.yaml — per-L pipeline overlays (rebases results_root + finemap.policy)
- bin/verify_ta_sh2b3_phase.sh — verification harness (run with --wave 1)
- D-TA-OSF-COVERAGE: COVERED (or AMENDMENT_POSTED) — Wave 1 HARD GATE cleared
- D-TA-Wave-0-pitfall2: NATIVE_PROPAGATION_WORKS or PATCH_REQUIRED+committed — config-merge propagation verified

<!-- Existing files Wave 1 reads -->
- src/legacy/region_analysis/scripts/run_susie_rss.R — fitter; option_list at lines 227-240; reads --policy YAML; sets L_used field in output JSON
- /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript — R env for fitter + verification
- /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake — Snakemake 7.32.4

<!-- Output JSON schema (per RESEARCH.md sample inspection) -->
- L_used: integer (the L the fit ran with)
- credible_sets: list of CS objects (length = n_CS)
- L_saturated: boolean (true if n_CS == L_used → saturation)
- convergence_status: string ("converged_*" prefix on success)

<!-- Compute envelope (per AUDIT-RESPONSE 2026-04-26 line 260) -->
- ~2-4 hr per fit on serial queue with la_multitrait_r env
- 9 fits aggregate ~12-15 hr; parallelizable across 50 LSF slots → wall ~4 hr

<!-- LSF wall-time configuration (per checker iter 1 NIT 2) -->
- bsub_wrapper.sh sets -W based on QUEUE arg: serial=5760 min (96 hr), long=14400 min (240 hr), standard=2880 min (48 hr)
- Wave 1 uses serial queue (1-slot, no time cap when -W=5760 is set; per memory feedback_lsf_queues.md)
- The wrapper enforces this; per-driver scripts do NOT need explicit -W stanzas (the wrapper adds it)
- Acceptance check verifies the wrapper config: `grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh`
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Fire L-sweep — 3 traits × 3 L values = 9 SuSiE-RSS fits on LSF (serial queue with -W=5760 min via bsub_wrapper.sh)</name>
  <files>
    results_lsweep_L15/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
    results_lsweep_L15/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
    results_lsweep_L15/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
    results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
    results_lsweep_L20/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
    results_lsweep_L20/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
    results_lsweep_L30/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
    results_lsweep_L30/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json
    results_lsweep_L30/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
    logs/wave1_susie_lsweep_*.log
  </files>
  <read_first>
    - bin/fire_susie_lsweep.sh (Wave 0 Task 5 produced; verify executable)
    - config/pipeline_lsweep_L20_overlay.yaml (verify it points to config/susie_policy_L20.yaml)
    - config/bsub_wrapper.sh (verify -W=5760 for serial queue per checker iter 1 NIT 2)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-OSF-COVERAGE" (must show CLEARED before firing)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Code Examples → Wave 1: SuSiE-RSS L-sweep dispatch"
  </read_first>
  <action>
    1. Pre-fire HARD GATE checks (verify before launching):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       grep -q "Wave 1 status:.*CLEARED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md || \
         { echo "ABORT: D-TA-OSF-COVERAGE not CLEARED. Wave 1 blocked."; exit 1; }
       grep -qE "D-TA-Wave-0-pitfall2:.*Outcome:.*(NATIVE_PROPAGATION_WORKS|PATCH_REQUIRED)" \
         .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md || \
         { echo "ABORT: Pitfall 2 not verified."; exit 1; }
       [ -x bin/fire_susie_lsweep.sh ] || { echo "ABORT: driver not executable"; exit 1; }

       # LSF wall-time configuration check (per checker iter 1 NIT 2):
       # bsub_wrapper.sh must set -W to queue max (5760 min for serial). The wrapper enforces this for ALL bsub calls.
       grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh || \
         { echo "ABORT: bsub_wrapper.sh does not enforce -W=5760 for serial queue (per checker iter 1 NIT 2)"; exit 1; }
       echo "PASS: bsub_wrapper.sh enforces -W=5760 (96 hr) for serial queue"
       ```

    2. Fire the L-sweep driver (runs on /rs1/.../coloc_analysis per D-TA-01):
       ```bash
       export LSF_UNIT_FOR_LIMITS=GB
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       bash bin/fire_susie_lsweep.sh
       ```
       The driver dispatches 3 LSF jobs per L (one per trait); 9 jobs total. Each job uses `serial` queue + `la_multitrait_r` env (per memory feedback_lsf_queues.md + AUDIT-RESPONSE line 260). The bsub_wrapper.sh transparently sets -W=5760 (96-hr cap, well above the ~2-4 hr per-fit envelope). Compute envelope ~2-4 hr per fit; aggregate ~12-15 hr but parallelizable across LSF slots → wall ~4 hr.

    3. Monitor LSF jobs to completion:
       ```bash
       # Watch jobs (LSF job names are set by the Snakemake LSF profile + per-job rule)
       bjobs -a | head
       # Loop until no PEND or RUN jobs remain
       while bjobs 2>&1 | grep -qE "PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running:"
         bjobs | grep -E "PEND|RUN" | wc -l
         sleep 300  # 5-min poll
       done
       echo "[$(date +%H:%M:%S)] All Wave 1 LSF jobs done."
       ```

    4. Verify all 9 outputs landed:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       for L in 15 20 30; do
         for T in bmi hypertension stroke; do
           f="results_lsweep_L${L}/fine_mapping/susie/${T}.EUR.SH2B3_12q24.json"
           if [ ! -f "$f" ]; then
             echo "MISSING: $f"
           else
             echo "OK: $f ($(stat -c '%s' "$f") bytes)"
           fi
         done
       done
       ```
       If any of the 9 are MISSING, inspect `logs/wave1_susie_lsweep_*.log` + the per-job LSF .err / .out files in `logs/lsf/` for failures. Re-run only the missing target via `bin/fire_susie_lsweep.sh` (Snakemake `--rerun-incomplete` handles this idempotently).

    5. Atomic commit (driver script + log; the .json/.fit.rds outputs go in their own commit per Task 2):
       ```bash
       git add logs/wave1_susie_lsweep_*.log
       # NOTE: results_lsweep_L*/ may be gitignored or committed depending on project policy.
       # Per RESEARCH.md, parallel-output namespaces (e.g., results_identity_ld/) ARE gitignored per DEC-2026-04-25-01.
       # Verify whether results_lsweep_L*/ should be committed by checking .gitignore:
       grep -n "results_lsweep" .gitignore || echo "(not gitignored — commit outputs)"
       # If gitignored: only commit the log; the artifacts live on disk only (regenerable).
       # If NOT gitignored: include the json files in this commit.
       git commit -m "feat(ta-sh2b3, W1): fire L-sweep SuSiE-RSS — 3 traits × 3 L values (D-TA-02)"
       ```
  </action>
  <acceptance_criteria>
    - 9 per-fit JSON files exist on disk: 3 traits × 3 L values at `results_lsweep_L{15,20,30}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.json`.
    - Each per-fit JSON's `L_used` field equals the swept L: `jq '.L_used' results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json` returns 20 (and 15/30 for the L=15/L=30 namespaces).
    - All LSF jobs completed with exit code 0: `bhist -a -J 'ta_sh2b3_W1_*' 2>&1 | grep -c "Done successfully"` ≥ 9 (or equivalent via grep on the LSF logs).
    - Driver log file exists: `ls logs/wave1_susie_lsweep_*.log | wc -l` ≥ 1.
    - **LSF wall-time configuration verified (per checker iter 1 NIT 2):** `grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh` returns 0 (the wrapper enforces -W=5760 for serial queue).
    - Atomic commit landed; git log shows `feat(ta-sh2b3, W1): fire L-sweep SuSiE-RSS — 3 traits × 3 L values (D-TA-02)`.
    - No file contention: `git status` shows clean tree (or only the wave-2 expected artifacts not yet committed).
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -qE "serial.*5760|QUEUE.*serial.*5760" config/bsub_wrapper.sh && for L in 15 20 30; do for T in bmi hypertension stroke; do f="results_lsweep_L${L}/fine_mapping/susie/${T}.EUR.SH2B3_12q24.json"; [ -f "$f" ] || { echo "MISSING $f"; exit 1; }; got_L=$(jq -r '.L_used' "$f" 2>/dev/null); [ "$got_L" = "$L" ] || { echo "L_used mismatch in $f: got $got_L expected $L"; exit 1; }; done; done && echo PASS</automated>
  </verify>
  <done>
    All 9 SuSiE-RSS L-sweep fits complete on disk with `L_used` matching swept L; driver log committed; bsub_wrapper.sh confirmed to enforce -W=5760 for serial queue (per checker iter 1 NIT 2). The `results_lsweep_L20/` namespace is now Wave 2's substrate. Verifies REQ-SUSIE-RSS-POLICY (D-TA-02 sweep delivered).
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Convergence verification + record PRIMARY_L + D-TA-Wave1-headline outcome (DEFERRED per invariant)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-02" + §"D-TA-Wave1-headline" (KEY: Wave 1 only REPORTS outcomes, does NOT update headline numerator)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Code Examples → Wave 1: Per-fit convergence verification"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C5 row
  </read_first>
  <action>
    1. Build the per-fit convergence report (TSV) by reading all 9 JSONs:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS' > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv
       library(jsonlite)
       cat("trait\tL_swept\tL_used\tn_CS\tL_saturated\tconvergence_status\tn_CS_LT_L\tconverged_ok\n")
       for (L in c(15, 20, 30)) {
         for (t in c("bmi", "hypertension", "stroke")) {
           f <- sprintf("results_lsweep_L%d/fine_mapping/susie/%s.EUR.SH2B3_12q24.json", L, t)
           if (!file.exists(f)) {
             cat(sprintf("%s\t%d\tNA\tNA\tNA\tMISSING\tFALSE\tFALSE\n", t, L))
             next
           }
           j <- jsonlite::fromJSON(f)
           ncs <- length(j$credible_sets)
           sat <- isTRUE(j$L_saturated)
           conv <- grepl("^converged", j$convergence_status %||% "")
           ncs_lt_l <- ncs < (j$L_used %||% 0L)
           ok <- conv && !sat && ncs_lt_l
           cat(sprintf("%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\n",
                       t, L, j$L_used, ncs, sat, j$convergence_status, ncs_lt_l, ok))
         }
       }
       RS
       cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv
       ```
       (If R version doesn't support `%||%`, swap for `if (is.null(x)) y else x`.)

    2. Identify PRIMARY_L (the lowest L where ALL 3 traits show converged_ok=TRUE):
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS'
       df <- read.delim(".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv", stringsAsFactors=FALSE)
       primary_L <- NA
       for (L in c(15, 20, 30)) {
         sub <- df[df$L_swept == L, ]
         if (nrow(sub) == 3 && all(sub$converged_ok == "TRUE")) { primary_L <- L; break }
       }
       cat(sprintf("PRIMARY_L=%s\n", if (is.na(primary_L)) "NONE_CONVERGED" else as.character(primary_L)))
       RS
       ```
       Capture the PRIMARY_L token. Most likely outcome (per AUDIT-RESPONSE projection): PRIMARY_L=20. Possible alternatives: 15 (best case, all converge at L=15) or 30 (some saturate at L=20) or NONE_CONVERGED (escalate).

    3. Append to CONTEXT.md (under `<decisions>` block, after D-TA-OSF-COVERAGE):

       ```markdown
       ### D-TA-Wave1-PRIMARY-L: SuSiE-RSS L-sweep convergence outcome (Wave 1)

       **Recorded:** {timestamp}

       **Per-trait per-L convergence (n_CS < L_used AND L_saturated=FALSE AND converged_*):**
       | trait | L=15 | L=20 | L=30 |
       |-------|------|------|------|
       | bmi | {OK|FAIL} | {OK|FAIL} | {OK|FAIL} |
       | hypertension | {OK|FAIL} | {OK|FAIL} | {OK|FAIL} |
       | stroke | {OK|FAIL} | {OK|FAIL} | {OK|FAIL} |

       Detailed numerics: see `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv`.

       **PRIMARY_L:** {15|20|30|NONE_CONVERGED}

       **Wave 2 directive:** Use PRIMARY_L={value} fits (`results_lsweep_L{value}/fine_mapping/susie/`) as input for canonical-pair coloc.susie.

       ### D-TA-Wave1-headline: Headline-numerator decision (DEFERRED to Wave 6 per CONTEXT.md invariant 2)

       **Per-trait convergence outcome at PRIMARY_L:**
       - bmi: {converged|non-converged}
       - hypertension: {converged|non-converged}
       - stroke: {converged|non-converged}

       **Newly converged count (was non-converged at L=10, now converged at PRIMARY_L):** {0..3}

       **Wave 6 narrative branch:**
       - If all 3 newly converge → Wave 6 RECOMPUTES headline numerator from `(51 + 3 - X)/96` where X = number of newly empty CS sets. Updates Abstract + §Headline + Fig 2 caption + TRACK-A-FROZEN-NUMBERS.md L10 LIVE block + Conclusion-1.
       - If some still don't converge → Wave 6 keeps 51/96 as headline + ADDS non-convergence disclosure column to Fig 3 (analogous to existing disclosure sub-table). Updates Limitations bullet + Methods §Fine-Mapping Configuration; does NOT touch the 51/96 headline.

       **HEADLINE_VALUE:** UNCHANGED (Wave 1 does not modify the 51/96 headline; Wave 6 does, conditional on this outcome.)
       ```

    4. Run the verification harness for Wave 1 (C5):
       ```bash
       PRIMARY_L={value} bin/verify_ta_sh2b3_phase.sh --wave 1
       ```
       C5 must emit PASS. If FAIL, escalate (the Wave-1-headline branch will need to be FAIL-disclosure, not RECOMPUTE).

    5. Atomic commit:
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv
       git commit -m "docs(ta-sh2b3, W1): record PRIMARY_L + D-TA-Wave1-headline (deferred to W6 per invariant)"
       ```
  </action>
  <acceptance_criteria>
    - File `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv` exists with header `trait\tL_swept\tL_used\tn_CS\tL_saturated\tconvergence_status\tn_CS_LT_L\tconverged_ok` and 9 data rows (3 traits × 3 L values).
    - For each L value, the corresponding 3 traits' rows show `L_used` matching the swept L (i.e., L_used=20 in the L_swept=20 rows).
    - PRIMARY_L recorded in CONTEXT.md: `grep "D-TA-Wave1-PRIMARY-L:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - PRIMARY_L value is one of {15, 20, 30, NONE_CONVERGED}: `grep -E "PRIMARY_L:.*\\*\\*(15|20|30|NONE_CONVERGED)\\*\\*" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - D-TA-Wave1-headline DEFERRED to Wave 6: `grep "HEADLINE_VALUE:.*UNCHANGED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - C5 from `bin/verify_ta_sh2b3_phase.sh --wave 1` emits PASS (or escalation documented if FAIL).
    - Atomic commit landed.
    - The 51/96 numerator in `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` is UNCHANGED (verify via `md5sum .planning/amendments/TRACK-A-FROZEN-NUMBERS.md` matches pre-Wave-1 baseline).
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv ] && [ "$(wc -l < .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-convergence-report.tsv)" -eq 10 ] && grep -q "D-TA-Wave1-PRIMARY-L:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "PRIMARY_L:.*\*\*(15|20|30|NONE_CONVERGED)\*\*" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -q "HEADLINE_VALUE:.*UNCHANGED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    Per-fit convergence report TSV in place; PRIMARY_L identified and recorded as `D-TA-Wave1-PRIMARY-L`; D-TA-Wave1-headline deferred to Wave 6 with HEADLINE_VALUE=UNCHANGED preserved (per CONTEXT.md invariant 2). 51/96 frozen-numbers headline UNTOUCHED. Atomic commit landed. Verifies C5 in VALIDATION.md.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| LSF dispatch ↔ /rs1 working tree | D-TA-01 enforces canonical path; mismatched cwd = wrong-tree dispatch |
| Per-L policy YAML ↔ run_susie_rss.R --policy reading | Pitfall 2 was mitigated in W0; Wave 1 verifies via L_used==L per fit |
| Pre-Wave-1 frozen 51/96 headline ↔ Wave 1 convergence report | Wave 1 reports outcomes only; D-TA-Wave1-headline DEFERRED to Wave 6 (invariant 2) |
| LSF wall-time enforcement ↔ bsub_wrapper.sh | Per checker iter 1 NIT 2: wrapper sets -W=5760 for serial queue (96-hr cap, well above ~2-4 hr per-fit envelope) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-01 | T (Tampering) | Fits land in `results_lsweep_L*/` parallel namespace, not `results/fine_mapping/susie/` | mitigate | Per-L overlay yamls rebase results_root explicitly; Stage 2 frozen `results/fine_mapping/susie/` UNTOUCHED — verifiable via md5sum manifest in Wave 7 |
| T-PROCESS-04 | T (Tampering) | TRACK-A-FROZEN-NUMBERS.md 51/96 headline | mitigate | Wave 1 only records D-TA-Wave1-headline DEFERRED; HEADLINE_VALUE=UNCHANGED; md5sum check in acceptance criteria |
| T-PROCESS-02 | I (Information disclosure) | Implicit `git add .` could stage `results_identity_ld/` (DEC-2026-04-25-01) or unintended files | mitigate | Every commit task uses explicit file paths |
| T-PROCESS-06 | D (Denial of service) | LSF jobs could be killed by 30-min queue default RUNLIMIT if -W not set | mitigate | bsub_wrapper.sh enforces -W=5760 for serial queue (per checker iter 1 NIT 2); Task 1 step 1 acceptance check verifies wrapper config |
</threat_model>

<verification>
- 9 JSON outputs present + L_used matches swept L per fit (Task 1 acceptance)
- Convergence report TSV well-formed with 9 data rows (Task 2 acceptance)
- PRIMARY_L identified and recorded (Task 2 acceptance)
- C5 from `bin/verify_ta_sh2b3_phase.sh --wave 1` emits PASS
- TRACK-A-FROZEN-NUMBERS.md unchanged (md5sum baseline preservation)
- bsub_wrapper.sh enforces -W=5760 for serial queue (per checker iter 1 NIT 2)
- 2 atomic commits landed (Task 1 + Task 2)
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C5** SuSiE-RSS converges at chosen L for SH2B3 EUR BMI/HTN/stroke — Task 2
</verification_criteria>

<success_criteria>
- 9 SuSiE-RSS fits land on disk in parallel namespaces with correct L_used field per fit
- D-TA-Wave1-PRIMARY-L recorded in CONTEXT.md addendum
- D-TA-Wave1-headline DEFERRED with HEADLINE_VALUE=UNCHANGED (invariant 2 preserved)
- Convergence report TSV produced as Wave 6 narrative input
- C5 emits PASS from verification harness
- TRACK-A-FROZEN-NUMBERS.md md5sum unchanged
- bsub_wrapper.sh enforces -W=5760 for serial queue (per checker iter 1 NIT 2)
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md` with:
- Per-fit convergence outcomes (D1-D7 dimensions: D1 dispatch success, D2 L_used field correctness, D3 convergence per Zou 2022, D4 L-saturation absence, D5 PRIMARY_L identification, D6 D-TA-Wave1-headline DEFERRED status, D7 frozen-numbers preservation)
- LSF wall-time observed vs projected (~4 hr wall expected; -W=5760 cap applied)
- PRIMARY_L value (drives Wave 2 dispatch)
- Wave-6-narrative branch (RECOMPUTE vs DISCLOSE-AS-COLUMN) the headline outcome implies
- Wave 2 GO/NO-GO status (must be GO with PRIMARY_L != NONE_CONVERGED for Wave 2)
</output>
