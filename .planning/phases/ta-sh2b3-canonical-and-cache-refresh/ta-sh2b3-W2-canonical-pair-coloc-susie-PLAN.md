---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 2
slug: W2-canonical-pair-coloc-susie
type: execute
wave: 2
depends_on: ["W1"]
files_modified:
  - results/multitrait/coloc_manifest_R2.tsv
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_bmi.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_hypertension.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_stroke.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_stroke.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_t2d.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_t2d.json
  - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__stroke_vs_t2d.json
  - logs/wave2_canonical_susie_*.log
autonomous: true
requirements:
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-SUSIE-RSS-POLICY
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "9 SH2B3 EUR canonical-pair coloc.susie outputs land on disk in parallel namespace results/multitrait/coloc_susie_R2/ (NOT in-place coloc_summary.tsv)"
    - "Each per-pair JSON exposes summary.PP.H4.abf as a finite numeric in [0, 1]"
    - "Wave 2 fits run against PRIMARY_L from Wave 1 (consumed via PRIMARY_L env var passed to bin/fire_canonical_susie_pairs.sh)"
    - "Stage 2 md5 invariant on results/multitrait/coloc_summary.tsv preserved (Wave 5 will explicitly re-render this file with documented exemption)"
    - "R2 manifest at results/multitrait/coloc_manifest_R2.tsv enumerates all 9 SH2B3 EUR pair_ids"
  artifacts:
    - path: "results/multitrait/coloc_manifest_R2.tsv"
      provides: "Wave 2 manifest (9-row R2 SH2B3 EUR canonical-pair manifest)"
      contains: "SH2B3_12q24__EUR__bmi_vs_hypertension"
    - path: "results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json"
      provides: "BMI–HTN canonical pair reference-LD coloc.susie output (audit-V2 §HQ#2(iii) closure substrate)"
      contains: '"PP.H4.abf"'
    - path: "results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json"
      provides: "HTN–stroke canonical pair reference-LD coloc.susie output"
      contains: '"PP.H4.abf"'
  key_links:
    - from: "results_lsweep_L${PRIMARY_L}/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.fit.rds"
      to: "results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json"
      via: "coloc.susie consumes Wave 1 fits"
      pattern: "coloc.susie\\(fit1, fit2\\)"
    - from: "results/multitrait/coloc_manifest_R2.tsv"
      to: "Snakemake run_coloc_susie rule"
      via: "manifest-driven dispatch"
      pattern: "pair_id"
---

<objective>
Wave 2 — Canonical SH2B3 EUR coloc.susie production fire. Run coloc.susie on the 9 new SH2B3 EUR canonical trait-pairs (full lattice minus already-on-disk asthma_vs_t2d) against the Wave-1 PRIMARY_L converged fits. Outputs land in a parallel namespace `results/multitrait/coloc_susie_R2/` to preserve the md5 byte-identical invariant on `results/multitrait/coloc_summary.tsv` (Pitfall 3). Wave 5 will explicitly merge the R2 outputs into the canonical summary with a documented exemption.

Purpose: Issue 1 §HQ#2(iii) closure. The manuscript's canonical claims (PP.H4 = 1.00 at rs3184504, rs10774625, rs7137828, rs4766578 for BMI–hypertension and hypertension–stroke under identity-LD) have never been tested under reference-LD; Table 3 currently shows those rows as "not executed". This wave produces the per-pair PP.H4 evidence that Wave 3 presents to Carter for the outcome-branch decision (D-TA-WAVE3-OUTCOME-{A|B|C}).

Output: 9 per-pair coloc.susie JSON outputs at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__{trait1}_vs_{trait2}.json`; R2 manifest at `results/multitrait/coloc_manifest_R2.tsv`; LSF dispatch log committed.
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
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md
@CLAUDE.md

<interfaces>
<!-- Wave 0 + Wave 1 produced these — Wave 2 consumes -->
- bin/fire_canonical_susie_pairs.sh — Wave 2 driver (executable)
- src/python/build_coloc_manifest_r2.py — R2 manifest builder (Python script)
- config/pipeline_canonical_r2_overlay.yaml — overlay rebasing MULTITRAIT_DIR to coloc_susie_R2/
- D-TA-Wave1-PRIMARY-L: {15|20|30} — drives PRIMARY_L env var for the Wave 2 driver
- results_lsweep_L{PRIMARY_L}/fine_mapping/susie/*.fit.rds — Wave 1 fits to be paired

<!-- Existing files Wave 2 reads -->
- results/multitrait/coloc_manifest.tsv — Stage 2 manifest (28 rows; schema reference for R2 builder)
- src/snakemake/rules/coloc.smk line 88 — rule run_coloc_susie (manifest-driven; reads pair_id wildcard)
- src/snakemake/rules/multitrait.smk — rule build_coloc_manifest + rule summarize_coloc_results

<!-- Output JSON schema (per RESEARCH.md sample inspection of existing 28 Stage 2 outputs) -->
- summary.PP.H0.abf, PP.H1.abf, PP.H2.abf, PP.H3.abf, PP.H4.abf — coloc.susie posterior probabilities
- credible_sets.CS{n}.{idx, pip, snp_id} — per-CS member listing

<!-- Compute envelope (per AUDIT-RESPONSE 2026-04-26 estimate) -->
- ~2 hr per pair on serial queue with la_multitrait_r env
- 9 pairs aggregate ~18 hr; parallelizable across LSF slots → wall ~3-4 hr

<!-- Stage 2 md5 byte-identical preservation invariant (Pitfall 3) -->
- DO NOT modify results/multitrait/coloc_summary.tsv in-place during Wave 2
- DO NOT trigger Snakemake rule summarize_coloc_results (which would rebuild coloc_summary.tsv)
- Only the run_coloc_susie rule fires (manifest-driven against R2 manifest)
- Wave 5 explicitly re-renders coloc_summary.tsv with documented exemption
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Build R2 manifest + fire 9 canonical-pair coloc.susie LSF jobs</name>
  <files>
    results/multitrait/coloc_manifest_R2.tsv
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_bmi.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_hypertension.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_stroke.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_stroke.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_t2d.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_t2d.json
    results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__stroke_vs_t2d.json
    logs/wave2_canonical_susie_*.log
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave1-PRIMARY-L" (Wave 1 outcome — gives PRIMARY_L)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-03: Canonical-pair coloc.susie scope"
    - bin/fire_canonical_susie_pairs.sh (Wave 0 Task 5)
    - src/python/build_coloc_manifest_r2.py (Wave 0 Task 5)
    - results/multitrait/coloc_manifest.tsv (28-row Stage 2 manifest schema)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 3: coloc.susie Wave 2 attempts append to coloc_summary.tsv" (KEY: writes to parallel namespace; do NOT trigger summarize_coloc_results)
  </read_first>
  <action>
    1. Pre-fire HARD GATE checks:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       PRIMARY_L=$(grep -A 5 "D-TA-Wave1-PRIMARY-L:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | grep -oE "PRIMARY_L:\*\*\s*(15|20|30)" | grep -oE "(15|20|30)" | head -1)
       if [ -z "$PRIMARY_L" ] || [ "$PRIMARY_L" = "NONE_CONVERGED" ]; then
         echo "ABORT: PRIMARY_L from Wave 1 not usable: '$PRIMARY_L'"
         exit 1
       fi
       echo "Wave 2 dispatching against PRIMARY_L=$PRIMARY_L"
       export PRIMARY_L
       # Capture pre-Wave-2 md5 of coloc_summary.tsv (Pitfall 3 invariant)
       BASELINE_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       echo "Pre-Wave-2 md5(coloc_summary.tsv) = $BASELINE_MD5 (must equal post-Wave-2)"
       echo "$BASELINE_MD5" > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/coloc_summary_md5_baseline.txt
       ```

    2. Build the R2 manifest:
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/python3 src/python/build_coloc_manifest_r2.py
       # Verify the produced manifest:
       wc -l results/multitrait/coloc_manifest_R2.tsv  # expect 10 lines (header + 9 rows)
       awk -F'\t' 'NR>1 {print $1}' results/multitrait/coloc_manifest_R2.tsv | sort
       ```
       The output must show exactly 9 pair_ids matching:
       - SH2B3_12q24__EUR__asthma_vs_bmi
       - SH2B3_12q24__EUR__asthma_vs_hypertension
       - SH2B3_12q24__EUR__asthma_vs_stroke
       - SH2B3_12q24__EUR__bmi_vs_hypertension
       - SH2B3_12q24__EUR__bmi_vs_stroke
       - SH2B3_12q24__EUR__bmi_vs_t2d
       - SH2B3_12q24__EUR__hypertension_vs_stroke
       - SH2B3_12q24__EUR__hypertension_vs_t2d
       - SH2B3_12q24__EUR__stroke_vs_t2d

    3. Fire the Wave 2 driver (runs on /rs1/.../coloc_analysis per D-TA-01):
       ```bash
       export LSF_UNIT_FOR_LIMITS=GB
       export PRIMARY_L
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01
       bash bin/fire_canonical_susie_pairs.sh
       ```
       The driver dispatches 9 LSF jobs (one per pair); `serial` queue + `la_multitrait_r` env. Compute envelope ~2 hr per pair; aggregate ~18 hr but parallelizable → wall ~3-4 hr.

    4. Monitor LSF jobs to completion:
       ```bash
       while bjobs 2>&1 | grep -qE "PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running: $(bjobs | grep -E 'PEND|RUN' | wc -l)"
         sleep 300
       done
       echo "[$(date +%H:%M:%S)] All Wave 2 LSF jobs done."
       ```

    5. Verify all 9 outputs landed:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       PAIRS=(asthma_vs_bmi asthma_vs_hypertension asthma_vs_stroke \
              bmi_vs_hypertension bmi_vs_stroke bmi_vs_t2d \
              hypertension_vs_stroke hypertension_vs_t2d stroke_vs_t2d)
       missing=0
       for p in "${PAIRS[@]}"; do
         f="results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__${p}.json"
         if [ ! -f "$f" ]; then echo "MISSING: $f"; missing=$((missing+1)); fi
       done
       echo "$missing missing of 9"
       ```
       If any are missing, inspect `logs/wave2_canonical_susie_*.log` + per-job LSF .err / .out files, re-run via the driver (Snakemake `--rerun-incomplete`).

    6. Verify Stage 2 md5 invariant (Pitfall 3):
       ```bash
       POST_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       BASELINE_MD5=$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/coloc_summary_md5_baseline.txt)
       if [ "$POST_MD5" != "$BASELINE_MD5" ]; then
         echo "FAIL: coloc_summary.tsv md5 changed during Wave 2 (Pitfall 3 violation)"
         echo "baseline: $BASELINE_MD5; post: $POST_MD5"
         exit 1
       fi
       echo "PASS: Stage 2 md5 invariant preserved"
       ```

    7. Atomic commit (manifest + log; outputs may or may not be committed depending on .gitignore policy):
       ```bash
       git add results/multitrait/coloc_manifest_R2.tsv \
               logs/wave2_canonical_susie_*.log \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/coloc_summary_md5_baseline.txt
       # Decide whether to commit results/multitrait/coloc_susie_R2/*.json:
       grep -n "results/multitrait/coloc_susie_R2" .gitignore || \
         git add results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json
       git commit -m "feat(ta-sh2b3, W2): fire 9 canonical SH2B3 EUR coloc.susie pairs at PRIMARY_L (D-TA-03)"
       ```
  </action>
  <acceptance_criteria>
    - Pre-Wave-2 PRIMARY_L extracted from CONTEXT.md and is in {15, 20, 30}.
    - `results/multitrait/coloc_manifest_R2.tsv` exists with exactly 10 lines (header + 9 data rows).
    - All 9 expected pair_ids present in the manifest: `awk -F'\t' 'NR>1 {print $1}' results/multitrait/coloc_manifest_R2.tsv | sort | wc -l` returns 9.
    - All 9 per-pair JSONs exist: `ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json | wc -l` returns 9.
    - Each per-pair JSON has parseable PP.H4: `for f in results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json; do jq -r '.summary."PP.H4.abf"' "$f"; done` produces 9 numeric values.
    - BMI–HTN PP.H4 specifically parseable (canonical literature claim): `jq '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json` returns numeric in [0, 1].
    - Stage 2 md5 invariant preserved: `md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1` equals baseline (recorded in `coloc_summary_md5_baseline.txt`).
    - All LSF jobs completed exit 0.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f results/multitrait/coloc_manifest_R2.tsv ] && [ "$(wc -l < results/multitrait/coloc_manifest_R2.tsv)" -eq 10 ] && [ "$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)" -eq 9 ] && jq -e '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json >/dev/null && jq -e '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json >/dev/null && [ "$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)" = "$(cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/coloc_summary_md5_baseline.txt)" ] && echo PASS</automated>
  </verify>
  <done>
    9 SH2B3 EUR canonical-pair coloc.susie outputs land on disk in `results/multitrait/coloc_susie_R2/`; R2 manifest in place; PP.H4 parseable per pair; Stage 2 md5 invariant preserved on `results/multitrait/coloc_summary.tsv` (Pitfall 3 mitigated). Verifies C6 + C7 in VALIDATION.md.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Generate Wave 3 outcome-presentation report (PP.H4 per pair, ready for human-verify gate)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json (9 per-pair Wave 2 outputs from Task 1)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave3-thresholds" (collapse <0.5 / partial 0.5-0.8 / survive ≥0.8)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C6, C7 rows
  </read_first>
  <action>
    Generate the per-pair PP.H4 report that Wave 3 will present to Carter for the outcome-branch decision. The report MUST be objective — Wave 2 does NOT pre-commit to a branch (per D-TA-Wave3-thresholds invariant; Wave 3 is the human-verify gate).

    1. Build the TSV report:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS' > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
       library(jsonlite)
       cat("pair_id\tPP.H0.abf\tPP.H1.abf\tPP.H2.abf\tPP.H3.abf\tPP.H4.abf\tThreshold_class\n")
       fits <- Sys.glob("results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json")
       for (f in fits) {
         j <- jsonlite::fromJSON(f, simplifyVector = TRUE)
         s <- j$summary
         pph4 <- s[["PP.H4.abf"]]
         class <- if (is.null(pph4) || !is.finite(pph4)) "MISSING" \
                  else if (pph4 < 0.5) "COLLAPSE_BELOW_0.5" \
                  else if (pph4 < 0.8) "PARTIAL_0.5_TO_0.8" \
                  else "SURVIVE_GE_0.8"
         pair <- sub("\\.json$", "", basename(f))
         cat(sprintf("%s\t%g\t%g\t%g\t%g\t%g\t%s\n",
                     pair,
                     s[["PP.H0.abf"]] %||% NA,
                     s[["PP.H1.abf"]] %||% NA,
                     s[["PP.H2.abf"]] %||% NA,
                     s[["PP.H3.abf"]] %||% NA,
                     pph4 %||% NA,
                     class))
       }
       RS
       cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
       ```
       (If `%||%` not available, swap to `if (is.null(x)) NA else x`.)

    2. Append a Wave 2 outcome summary to CONTEXT.md (under `<decisions>`, after D-TA-Wave1-headline):

       ```markdown
       ### D-TA-Wave2-outcomes: Canonical-pair coloc.susie PP.H4 outcomes (Wave 2)

       **Recorded:** {timestamp}

       **Per-pair PP.H4 outcomes (9 SH2B3 EUR new pairs):**
       | pair_id | PP.H4 | Threshold class |
       |---------|-------|------------------|
       | asthma_vs_bmi | {value} | {class} |
       | asthma_vs_hypertension | {value} | {class} |
       | asthma_vs_stroke | {value} | {class} |
       | bmi_vs_hypertension (CANONICAL) | {value} | {class} |
       | bmi_vs_stroke | {value} | {class} |
       | bmi_vs_t2d | {value} | {class} |
       | hypertension_vs_stroke (CANONICAL) | {value} | {class} |
       | hypertension_vs_t2d | {value} | {class} |
       | stroke_vs_t2d | {value} | {class} |

       Detailed numerics: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv`.

       **Wave 3 gate input:** BMI–HTN PP.H4 = {value}; HTN–stroke PP.H4 = {value}.

       **Wave 2 does NOT pre-commit to a branch** (per D-TA-Wave3-thresholds + invariant 2). Wave 3 (human-verify) records the branch.
       ```

    3. Run verification harness for Wave 2 (C6 + C7):
       ```bash
       bin/verify_ta_sh2b3_phase.sh --wave 2
       ```
       Both C6 (BMI-HTN PP.H4 parseable) and C7 (9 R2 JSONs present) must emit PASS.

    4. Atomic commit:
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W2): record D-TA-Wave2-outcomes — PP.H4 per pair (no branch pre-commit)"
       ```
  </action>
  <acceptance_criteria>
    - File `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv` exists with header `pair_id\tPP.H0.abf\tPP.H1.abf\tPP.H2.abf\tPP.H3.abf\tPP.H4.abf\tThreshold_class` and 9 data rows.
    - Each Threshold_class value is one of: `COLLAPSE_BELOW_0.5`, `PARTIAL_0.5_TO_0.8`, `SURVIVE_GE_0.8`, `MISSING`.
    - `grep "D-TA-Wave2-outcomes:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep "Wave 2 does NOT pre-commit to a branch" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit (invariant preserved).
    - `grep "BMI–HTN PP.H4" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `bin/verify_ta_sh2b3_phase.sh --wave 2` emits C6 PASS and C7 PASS.
    - No D-TA-WAVE3-OUTCOME-* token appears in CONTEXT.md yet (it lands in Wave 3, not here): `grep -c "D-TA-WAVE3-OUTCOME-" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns 0.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv ] && [ "$(wc -l < .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv)" -eq 10 ] && grep -q "D-TA-Wave2-outcomes:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -q "Wave 2 does NOT pre-commit to a branch" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && [ "$(grep -c 'D-TA-WAVE3-OUTCOME-' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md)" -eq 0 ] && echo PASS</automated>
  </verify>
  <done>
    Per-pair PP.H4 report TSV in place (Wave 3 input). D-TA-Wave2-outcomes recorded in CONTEXT.md with explicit "no branch pre-commit" line preserving invariant 2. C6 + C7 PASS. Atomic commit landed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Wave 1 .fit.rds ↔ Wave 2 coloc.susie input | PRIMARY_L env var must match the L-namespace Wave 1 produced; mismatch = wrong-fit pairing |
| R2 parallel namespace `coloc_susie_R2/` ↔ canonical `coloc_susie/` | Pitfall 3: must NOT trigger summarize_coloc_results (would mutate coloc_summary.tsv md5) |
| Wave 2 PP.H4 outputs ↔ Wave 3 outcome-branch decision | Wave 2 reports objectively; never pre-commits to a/b/c per invariant 2 |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-04 | T (Tampering) | results/multitrait/coloc_summary.tsv md5 invariant | mitigate | Pre/post md5sum baseline check in Task 1 acceptance criteria; parallel namespace coloc_susie_R2/ avoids in-place mutation per Pitfall 3 |
| T-PROCESS-01 | T (Tampering) | LSF dispatch cwd | mitigate | Wave 2 driver explicitly cd's to /rs1/.../coloc_analysis (D-TA-01); PRIMARY_L env var sourced from CONTEXT.md decision token (no hardcoding) |
| T-PROCESS-03 | I (Information disclosure / pre-commitment) | Branch (a/b/c) decision | mitigate | Wave 2 records D-TA-Wave2-outcomes with "Wave 2 does NOT pre-commit" anchor; Wave 3 is the gate |
</threat_model>

<verification>
- 9 SH2B3 EUR coloc.susie outputs in coloc_susie_R2/ (Task 1)
- R2 manifest with 9 pair_ids (Task 1)
- coloc_summary.tsv md5 unchanged from baseline (Task 1, Pitfall 3 mitigation)
- Per-pair PP.H4 report TSV with threshold classification (Task 2)
- D-TA-Wave2-outcomes recorded in CONTEXT.md with no branch pre-commit (Task 2)
- C6, C7 PASS from verification harness
- 2 atomic commits landed
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C6** BMI–HTN reference-LD coloc.susie produced — Task 1 + Task 2
- **C7** All 9 SH2B3 EUR new pairs produced — Task 1
</verification_criteria>

<success_criteria>
- 9 SH2B3 EUR per-pair coloc.susie JSONs land in `results/multitrait/coloc_susie_R2/`
- R2 manifest at `results/multitrait/coloc_manifest_R2.tsv` enumerates exactly 9 pair_ids
- BMI–HTN PP.H4 + HTN–stroke PP.H4 parseable as numerics
- Stage 2 md5 invariant on `results/multitrait/coloc_summary.tsv` PRESERVED
- D-TA-Wave2-outcomes recorded in CONTEXT.md with explicit "no branch pre-commit"
- C6 + C7 emit PASS from verification harness
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-SUMMARY.md` with:
- Per-pair PP.H4 outcomes (D1-D7 dimensions: D1 manifest construction, D2 dispatch success, D3 9-pair completeness, D4 PP.H4 parseability, D5 Stage 2 md5 invariant preservation, D6 BMI-HTN canonical claim observed value, D7 HTN-stroke canonical claim observed value)
- LSF wall-time observed vs projected (~3-4 hr wall expected)
- Threshold classification per pair (collapse/partial/survive)
- Wave 3 GO/NO-GO status (must be GO with all 9 PP.H4 parseable for Wave 3 human-verify gate to fire)
- Pitfall 3 verification evidence (md5sum match)
</output>
