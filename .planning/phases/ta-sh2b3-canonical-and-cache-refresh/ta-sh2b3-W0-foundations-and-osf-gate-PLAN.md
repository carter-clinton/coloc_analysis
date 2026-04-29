---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 0
slug: W0-foundations-and-osf-gate
type: execute
wave: 0
depends_on: []
files_modified:
  - bin/verify_ta_sh2b3_phase.sh
  - bin/fire_susie_lsweep.sh
  - bin/fire_canonical_susie_pairs.sh
  - bin/fire_qtl_coloc_cache_refresh.sh
  - config/susie_policy_L15.yaml
  - config/susie_policy_L20.yaml
  - config/susie_policy_L30.yaml
  - config/pipeline_lsweep_L15_overlay.yaml
  - config/pipeline_lsweep_L20_overlay.yaml
  - config/pipeline_lsweep_L30_overlay.yaml
  - config/pipeline_canonical_r2_overlay.yaml
  - src/python/build_coloc_manifest_r2.py
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
autonomous: false
requirements:
  - REQ-PATH-PARAMETERIZATION
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-SUSIE-RSS-POLICY

must_haves:
  truths:
    - "Source-repo path /rs1/researchers/c/ckclinto/coloc_analysis/.git resolves on login02 and HEAD matches the GPFS interactive HEAD (D-TA-01)"
    - "Code fixes 069b34f (run_qtl_coloc.R chr:pos tolerance) and 7d54183 (run_susie_rss.R LD-rsid override) are ancestors of HEAD on the current branch (no cherry-pick needed)"
    - "SuSiE-RSS variant-ID format diagnostic recorded as D-TA-04-DIAGNOSTIC-{RSID|CHRPOS|MIXED} in CONTEXT.md addendum from .fit.rds inspection (NOT jq on JSON)"
    - "OSF pre-reg coverage for L-sweep + canonical-pair scope verified (D-TA-OSF-COVERAGE-COVERED) or amendment posted live before Wave 1 fires (HARD GATE)"
    - "Snakefile rule-name surface for QTL-coloc + SuSiE-RSS layers documented (so Wave 4 dispatch + Wave 1 overlay yamls reference correct rules)"
    - "Wave-1/2/4 driver scripts, per-L policy YAML overlays, R2 canonical-pair overlay, and verification harness all exist on disk"
    - "Snakemake config-merge propagation of finemap.policy override verified by single-locus dry-run (per RESEARCH.md Pitfall 2)"
  artifacts:
    - path: "bin/verify_ta_sh2b3_phase.sh"
      provides: "C1-C15 dimension check harness emitting PASS/WARN/FAIL JSON per D1-D7"
      contains: "function check_C1_path_resolves"
    - path: "config/susie_policy_L15.yaml"
      provides: "Wave 1 SuSiE policy override for L=15 (D-TA-02 sweep)"
      contains: "L: 15"
    - path: "config/susie_policy_L20.yaml"
      provides: "Wave 1 SuSiE policy override for L=20 (D-TA-02 sweep primary candidate)"
      contains: "L: 20"
    - path: "config/susie_policy_L30.yaml"
      provides: "Wave 1 SuSiE policy override for L=30 (D-TA-02 sweep upper bound)"
      contains: "L: 30"
    - path: "config/pipeline_lsweep_L15_overlay.yaml"
      provides: "Wave 1 pipeline overlay rebasing results_root + finemap.policy for L=15"
      contains: "results_lsweep_L15"
    - path: "config/pipeline_lsweep_L20_overlay.yaml"
      provides: "Wave 1 pipeline overlay rebasing results_root + finemap.policy for L=20"
      contains: "results_lsweep_L20"
    - path: "config/pipeline_lsweep_L30_overlay.yaml"
      provides: "Wave 1 pipeline overlay rebasing results_root + finemap.policy for L=30"
      contains: "results_lsweep_L30"
    - path: "config/pipeline_canonical_r2_overlay.yaml"
      provides: "Wave 2 overlay rebasing MULTITRAIT_DIR to results/multitrait/coloc_susie_R2/"
      contains: "coloc_susie_R2"
    - path: "bin/fire_susie_lsweep.sh"
      provides: "Wave 1 driver script (per-L Snakemake fire on serial queue with la_multitrait_r env)"
      contains: "config/cluster_lsf"
    - path: "bin/fire_canonical_susie_pairs.sh"
      provides: "Wave 2 driver script (9 SH2B3 EUR canonical pairs against primary-result-L fits)"
      contains: "SH2B3_12q24__EUR__bmi_vs_hypertension"
    - path: "bin/fire_qtl_coloc_cache_refresh.sh"
      provides: "Wave 4 driver script (cache backup mv + Snakemake re-fire --use-conda -j 50)"
      contains: "preFix.bak"
    - path: "src/python/build_coloc_manifest_r2.py"
      provides: "Wave 2 manifest builder (9-row R2 SH2B3 EUR canonical-pair manifest)"
      contains: "SH2B3_12q24"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md"
      provides: "Updated CONTEXT.md addendum with D-TA-04-DIAGNOSTIC + D-TA-OSF-COVERAGE recorded"
      contains: "D-TA-04-DIAGNOSTIC-"
  key_links:
    - from: "bin/fire_susie_lsweep.sh"
      to: "config/pipeline_lsweep_L{15,20,30}_overlay.yaml"
      via: "--configfile"
      pattern: "config/pipeline_lsweep_L\\$\\{L\\}_overlay.yaml"
    - from: "config/pipeline_lsweep_L20_overlay.yaml"
      to: "config/susie_policy_L20.yaml"
      via: "finemap.policy override"
      pattern: "policy.*susie_policy_L20.yaml"
    - from: "bin/verify_ta_sh2b3_phase.sh"
      to: "all C1-C15 verification commands"
      via: "embedded check_Cn functions"
      pattern: "check_C[0-9]+"
---

<objective>
Wave 0 — Foundations + Diagnostics + OSF gate. Build the verification harness, dispatch drivers, per-L policy YAML overlays, R2 manifest builder. Run the SuSiE-RSS variant-ID format diagnostic (drives D-TA-04 cache-layer scope). Verify code-fix ancestry. Verify D-TA-01 source-repo path. Verify Snakemake config-merge propagation via single-locus dry-run (RESEARCH.md Pitfall 2). Carter web-UI verifies OSF pre-reg coverage (D-TA-05 HARD GATE on Wave 1).

Purpose: Wave 0 is the bedrock all subsequent waves stand on. Every Wave 1/2/4 dispatch reaches into infrastructure scaffolded here; without it, Wave 1 fires against the wrong policy file, Wave 2 mutates the md5-locked Stage 2 summary, Wave 4 backs up onto a name collision, and the OSF pre-reg discipline silently fails.

Output: Verification harness, 3 per-L policy YAMLs, 3 per-L pipeline overlays, 1 R2 canonical-pair overlay, 3 driver scripts (Wave 1/2/4), 1 Python manifest builder, plus D-TA-04-DIAGNOSTIC + D-TA-OSF-COVERAGE recorded as new sub-sections in CONTEXT.md addendum.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md
@CLAUDE.md

<interfaces>
<!-- Key existing files the executor needs. Extracted from RESEARCH.md verification. -->
<!-- Use these directly — no codebase exploration needed. -->

CRITICAL PATH CORRECTIONS (CONTEXT.md tokens are WRONG; use these):
- scripts/python/  → src/python/
- scripts/R/       → src/R/{aggregators,figures}/
- workflow/Snakefile → Snakefile (top-level)
- bin/bsub_wrapper.sh → config/bsub_wrapper.sh

EXISTING PRECEDENT FILES (do NOT modify; mirror their pattern):
- scripts/fire_identity_ld_rerun.sh — two-phase Snakemake fire with parallel-output overlay; lines 19-30 dispatch pattern
- bin/fire_phase2_stage2_refit.sh — Stage 2 LSF dispatch driver (proven 2026-04-22)
- config/pipeline_identity_overlay.yaml — overlay-yaml precedent for parallel results_root + ld_reference rebasing
- config/susie_policy.yaml — base policy (L=10 default; copy-with-override pattern for the L-sweep)
- src/legacy/region_analysis/scripts/run_susie_rss.R — fitter; option_list at lines 227-240; --policy flag (no --L flag); writes .fit.rds via coloc:::annotate_susie at line 575
- src/snakemake/rules/finemap.smk — rule run_finemap; line 70-71 hardcodes policy="config/susie_policy.yaml" (Pitfall 2 mitigation target)
- /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake — Snakemake 7.32.4 / Python 3.11
- /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript — SuSiE-RSS / coloc.susie / aggregator R env
- config/cluster_lsf/config.yaml — Snakemake LSF profile (use --profile config/cluster_lsf, NOT --cluster directly)

VARIANT-ID DIAGNOSTIC SOURCE (for D-TA-04):
- The .json fit files do NOT have a top-level variant_ids key. The format token lives in:
  fit.rds → colnames(fit$alpha) (SuSiE Σ matrix column names) AND/OR names(fit$pip)
- Sample these 3 fits: bmi.EUR.SH2B3_12q24, bmi.EUR.FTO_16q12, hypertension.EUR.SH2B3_12q24

LSF DISPATCH SHAPE (D-TA-01 + memory feedback_lsf_queues.md):
- Source path on cluster: /rs1/researchers/c/ckclinto/coloc_analysis (D-TA-01 canonical)
- Wave 1 + Wave 2: serial queue, -W 5760 (96 hr), 32 GB mem
- Wave 4: long queue, -W 14400 (240 hr), 32 GB mem
- LSF_UNIT_FOR_LIMITS=GB
- Job naming: -J ta_sh2b3_W{wave}_{job_token} for bjobs/bkill filtering

COMMIT POLICY (memory feedback_multi_terminal_staging.md):
- NEVER `git add .` or `-A` on GPFS shared tree
- ALWAYS pass explicit file paths to git add
- One atomic commit per task
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Verify D-TA-01 source-repo path + code-fix ancestry + Snakefile rule names</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md (locked decisions D-TA-01, code-fix substrate)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 1" + §"Code Examples → Wave 0: Code-fix ancestry verification" + §"Open Questions #1"
    - Snakefile (read top-to-bottom to enumerate rule names; ≤212 lines per RESEARCH.md)
    - src/snakemake/rules/qtl_coloc.smk (extract `rule run_qtl_coloc` name + QTL_COLOC_OUTPUTS pattern)
    - src/snakemake/rules/finemap.smk (extract `rule run_finemap` name + line 70-71 policy declaration)
  </read_first>
  <action>
    Run these commands in this exact order:

    1. Path resolution check (D-TA-01) — try locally then on login02:
       ```bash
       echo "GPFS HEAD: $(git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis rev-parse HEAD)"
       if [ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ]; then
         echo "/rs1 HEAD: $(git -C /rs1/researchers/c/ckclinto/coloc_analysis rev-parse HEAD)"
       else
         echo "/rs1/.../coloc_analysis NOT present on this node — try login02:"
         ssh login02.hpc.ncsu.edu '[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && git -C /rs1/researchers/c/ckclinto/coloc_analysis rev-parse HEAD || echo "ABSENT_ON_LOGIN02"'
       fi
       ```
       If /rs1/.../coloc_analysis is absent on login02 too, this is a Carter-mediated investigation (per RESEARCH.md Open Question #1): pause and ask Carter whether to clone the repo to /rs1/.../coloc_analysis or symlink the GPFS path.

    2. Code-fix ancestry check (C2):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git merge-base --is-ancestor 069b34f HEAD && echo "069b34f: ancestor (PASS)" || echo "069b34f: NOT ancestor (cherry-pick required)"
       git merge-base --is-ancestor 7d54183 HEAD && echo "7d54183: ancestor (PASS)" || echo "7d54183: NOT ancestor (cherry-pick required)"
       ```
       Both MUST return ancestor. (Verified during research 2026-04-29; this is a cheap re-verify at execute time.) If either is NOT ancestor, halt and `git cherry-pick` the missing commit on the current branch BEFORE proceeding.

    3. Snakefile rule-name surface (drives Wave 4 dispatch target):
       ```bash
       grep -nE "^rule [a-zA-Z_]+:" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile
       grep -nE "^rule [a-zA-Z_]+:" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/qtl_coloc.smk
       grep -nE "^rule [a-zA-Z_]+:" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/snakemake/rules/finemap.smk
       ```
       Record the rule names (e.g., `run_qtl_coloc`, `run_finemap`, `all_qtl_coloc`) — Wave 4 driver dispatches against these.

    4. Append a new sub-section to ta-sh2b3-CONTEXT.md (under `<decisions>`, after the existing D-TA-Wave-6-timing entry but before the closing `</decisions>` tag) with this exact heading and content shape:

       ```markdown
       ### D-TA-Wave-0-foundations: Path + ancestry + rule-name verification (Wave 0 outcome)

       **Recorded:** {timestamp}

       **D-TA-01 path:** {PASS|INVESTIGATE} — `/rs1/.../coloc_analysis/.git` HEAD = `{sha}`; GPFS HEAD = `{sha}` ({match|mismatch}).

       **Code-fix ancestry (C2):** 069b34f = {ancestor|cherry-picked@<new-sha>}; 7d54183 = {ancestor|cherry-picked@<new-sha>}.

       **Snakefile rule-name surface:**
       - QTL-coloc dispatch target: `{rule_name}` (e.g., `all_qtl_coloc`)
       - SuSiE-RSS rule: `{rule_name}` (e.g., `run_finemap`)
       - All-targets aggregate: `{rule_name}` (e.g., `ALL_TARGETS`)
       ```

    5. Atomic commit (D-TA-01 invariant — explicit file paths):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W0): verify D-TA-01 path + code-fix ancestry + Snakefile rule names"
       ```
  </action>
  <acceptance_criteria>
    - `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ]` either returns 0 with HEAD matching GPFS, OR a Carter-mediated investigation outcome is documented in CONTEXT.md addendum (NOT silently skipped).
    - `git merge-base --is-ancestor 069b34f HEAD` returns exit 0.
    - `git merge-base --is-ancestor 7d54183 HEAD` returns exit 0.
    - `grep "D-TA-Wave-0-foundations:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep "Snakefile rule-name surface" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - Atomic commit landed; `git log -1 --pretty=%s` matches `docs(ta-sh2b3, W0): verify D-TA-01 path + code-fix ancestry + Snakefile rule names`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git merge-base --is-ancestor 069b34f HEAD && git merge-base --is-ancestor 7d54183 HEAD && grep -q "D-TA-Wave-0-foundations:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -q "Snakefile rule-name surface" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    D-TA-01 path verified (or escalated for Carter); code-fix ancestry verified (both 069b34f + 7d54183 are HEAD ancestors); Snakefile rule-name surface enumerated and recorded as `D-TA-Wave-0-foundations` in CONTEXT.md addendum; atomic commit landed. Verifies C1 + C2 in VALIDATION.md.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Run SuSiE-RSS variant-ID format diagnostic (D-TA-04)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-04: Cache-layer scope for Issue 2 re-fire"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 4: variant-ID diagnostic reads .json instead of .fit.rds — gives no signal" (CRITICAL — the JSON has no `variant_ids` top-level key; format token lives in .fit.rds via colnames(fit$alpha) / names(fit$pip))
    - Verify the .fit.rds files exist: `ls /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/results/fine_mapping/susie/{bmi,hypertension}.EUR.SH2B3_12q24.fit.rds /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds`
  </read_first>
  <action>
    Run the diagnostic as Rscript (NOT jq — the JSON has no variant_ids key):

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS' | tee logs/wave0_diagnostic_$(date +%Y%m%d_%H%M%S).log
    fits <- c(
      "results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds",
      "results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds",
      "results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds"
    )
    results <- character()
    for (path in fits) {
      if (!file.exists(path)) { cat(sprintf("%s\tMISSING\n", path)); next }
      fit <- readRDS(path)
      ids <- if (!is.null(fit$alpha) && !is.null(colnames(fit$alpha))) {
        colnames(fit$alpha)
      } else if (!is.null(names(fit$pip))) {
        names(fit$pip)
      } else NULL
      ids_no_null <- ids[!is.null(ids) & ids != "null" & !is.na(ids)]
      fmt <- if (any(grepl("^rs[0-9]+$", ids_no_null))) {
        if (any(grepl("^[0-9XY]+:[0-9]+$", ids_no_null))) "MIXED" else "RSID"
      } else if (any(grepl("^[0-9XY]+:[0-9]+$", ids_no_null))) "CHRPOS" else "UNKNOWN"
      cat(sprintf("%s\t%s\t%s\n", path, fmt, paste(head(ids_no_null, 3), collapse=",")))
      results <- c(results, fmt)
    }
    aggregate <- if (all(results == "RSID")) "RSID" else if (all(results == "CHRPOS")) "CHRPOS" else "MIXED"
    cat(sprintf("\nAGGREGATE\t%s\n", aggregate))
    cat(sprintf("CACHE_SCOPE\t%s\n",
                if (aggregate == "RSID") "QTL_COLOC_ONLY"
                else if (aggregate == "CHRPOS") "BOTH_LAYERS"
                else "CONSERVATIVE_BOTH"))
    RS
    ```

    Capture the AGGREGATE token (`RSID` / `CHRPOS` / `MIXED`) and the CACHE_SCOPE token (`QTL_COLOC_ONLY` / `BOTH_LAYERS` / `CONSERVATIVE_BOTH`).

    Append to CONTEXT.md (under the `<decisions>` block, after Task 1's `D-TA-Wave-0-foundations` sub-section):

    ```markdown
    ### D-TA-04-DIAGNOSTIC: Variant-ID format outcome (Wave 0)

    **Recorded:** {timestamp}

    **Diagnostic outcome (per .fit.rds inspection of 3 sample fits):**
    - bmi.EUR.SH2B3_12q24: {RSID|CHRPOS|MIXED|UNKNOWN}
    - bmi.EUR.FTO_16q12: {RSID|CHRPOS|MIXED|UNKNOWN}
    - hypertension.EUR.SH2B3_12q24: {RSID|CHRPOS|MIXED|UNKNOWN}

    **Aggregate:** {RSID|CHRPOS|MIXED}

    **D-TA-04 cache-scope decision:** `{QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH}` (drives Wave 4 SuSiE-RSS layer in/out).

    **Wave 4 plan:**
    - QTL_COLOC_ONLY → Wave 4 backs up only `results/qtl_coloc/`; SuSiE-RSS layer untouched.
    - BOTH_LAYERS → Wave 4 backs up both `results/qtl_coloc/` AND `results/fine_mapping/susie/`.
    - CONSERVATIVE_BOTH → same as BOTH_LAYERS (mixed format edge case).
    ```

    Atomic commit:
    ```bash
    git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
    git commit -m "docs(ta-sh2b3, W0): record D-TA-04-DIAGNOSTIC variant-ID format outcome"
    ```
  </action>
  <acceptance_criteria>
    - The Rscript snippet returned an `AGGREGATE` token of one of `RSID` / `CHRPOS` / `MIXED` for all 3 fits.
    - `grep "D-TA-04-DIAGNOSTIC:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep -E "Aggregate:.*(RSID|CHRPOS|MIXED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - `grep -E "D-TA-04 cache-scope decision: \`(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)\`" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - Atomic commit landed; `git log -1 --pretty=%s` matches `docs(ta-sh2b3, W0): record D-TA-04-DIAGNOSTIC variant-ID format outcome`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-04-DIAGNOSTIC:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "D-TA-04 cache-scope decision:.*(QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    D-TA-04 variant-ID format diagnostic recorded in CONTEXT.md with explicit per-fit format tokens + aggregate decision + Wave 4 cache scope. Verifies C3 in VALIDATION.md. Drives Wave 4 dispatch.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Scaffold per-L policy YAMLs + per-L pipeline overlays + R2 canonical-pair overlay</name>
  <files>
    config/susie_policy_L15.yaml
    config/susie_policy_L20.yaml
    config/susie_policy_L30.yaml
    config/pipeline_lsweep_L15_overlay.yaml
    config/pipeline_lsweep_L20_overlay.yaml
    config/pipeline_lsweep_L30_overlay.yaml
    config/pipeline_canonical_r2_overlay.yaml
  </files>
  <read_first>
    - config/susie_policy.yaml (full content; copy-with-override-only-on-L pattern)
    - config/pipeline_identity_overlay.yaml (full content; PRECEDENT for parallel-output overlay rebasing paths.results_root + ld_reference)
    - config/pipeline.yaml (top-level; understand the schema for results_root + finemap.policy + finemap.output_dir + MULTITRAIT_DIR)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pattern 2: SuSiE policy override via --policy" + §"Pitfall 2: L-sweep policy YAML override doesn't propagate"
  </read_first>
  <action>
    Create 7 config files. Each must be byte-faithful to the precedent files.

    **(1) `config/susie_policy_L15.yaml`** — copy `config/susie_policy.yaml` and change ONLY the `susie.L` value to 15. Preserve every other field (coverage, max_iter_primary, max_iter_retry, ld_regularization_eps, min_abs_corr_default, min_abs_corr_sweep, min_ld_overlap, min_ld_coverage, min_ld_min_use, l_saturation, convergence_failure, complex_regions). Add a comment at the top:

    ```yaml
    # config/susie_policy_L15.yaml — Wave 1 L-sweep override (D-TA-02)
    # Copy of config/susie_policy.yaml with susie.L: 15.
    # Used by Wave 1 driver via:
    #   snakemake --configfile config/pipeline_lsweep_L15_overlay.yaml
    # Phase: ta-sh2b3-canonical-and-cache-refresh (D-TA-02)
    susie:
      L: 15
      coverage: <copy from susie_policy.yaml>
      ...
    ```

    Repeat for L=20 (`config/susie_policy_L20.yaml`) and L=30 (`config/susie_policy_L30.yaml`), each with `susie.L: 20` and `susie.L: 30` respectively.

    **(2) `config/pipeline_lsweep_L15_overlay.yaml`** — pipeline overlay that:
    - Rebases `paths.results_root` to `results_lsweep_L15/`
    - Sets `finemap.policy: "config/susie_policy_L15.yaml"`
    - Sets `finemap.output_dir: "results_lsweep_L15/fine_mapping"` (so output paths land in the parallel namespace)

    Pattern (mirror `config/pipeline_identity_overlay.yaml` shape):

    ```yaml
    # config/pipeline_lsweep_L15_overlay.yaml — Wave 1 L-sweep parallel-output overlay (D-TA-02)
    # Phase: ta-sh2b3-canonical-and-cache-refresh
    # Used in conjunction with config/pipeline.yaml + bin/fire_susie_lsweep.sh
    paths:
      results_root: "results_lsweep_L15"
    finemap:
      policy: "config/susie_policy_L15.yaml"
      output_dir: "results_lsweep_L15/fine_mapping"
    ```

    Repeat for L=20 (`config/pipeline_lsweep_L20_overlay.yaml`) and L=30 (`config/pipeline_lsweep_L30_overlay.yaml`).

    **(3) `config/pipeline_canonical_r2_overlay.yaml`** — Wave 2 overlay that rebases the multitrait coloc.susie output dir:

    ```yaml
    # config/pipeline_canonical_r2_overlay.yaml — Wave 2 canonical-pair R2 parallel-output overlay (D-TA-03)
    # Phase: ta-sh2b3-canonical-and-cache-refresh
    # Used by bin/fire_canonical_susie_pairs.sh to write 9 SH2B3 EUR canonical pairs to a parallel namespace
    # (preserves Stage 2 md5 byte-identical invariant on results/multitrait/coloc_summary.tsv per Pitfall 3)
    multitrait:
      output_dir: "results/multitrait/coloc_susie_R2"
    ```
    (Adjust the field name to match the actual config schema discovered in step 0; if the canonical key is `MULTITRAIT_DIR` use that.)

    Atomic commit (explicit file paths):
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add config/susie_policy_L15.yaml config/susie_policy_L20.yaml config/susie_policy_L30.yaml \
            config/pipeline_lsweep_L15_overlay.yaml config/pipeline_lsweep_L20_overlay.yaml config/pipeline_lsweep_L30_overlay.yaml \
            config/pipeline_canonical_r2_overlay.yaml
    git commit -m "feat(ta-sh2b3, W0): scaffold per-L policy YAMLs + pipeline overlays for D-TA-02 + D-TA-03"
    ```
  </action>
  <acceptance_criteria>
    - 7 YAML files exist on disk: `config/susie_policy_L{15,20,30}.yaml`, `config/pipeline_lsweep_L{15,20,30}_overlay.yaml`, `config/pipeline_canonical_r2_overlay.yaml`.
    - `grep "L: 15" config/susie_policy_L15.yaml`, `grep "L: 20" config/susie_policy_L20.yaml`, `grep "L: 30" config/susie_policy_L30.yaml` all return ≥ 1 hit.
    - `grep "results_lsweep_L15" config/pipeline_lsweep_L15_overlay.yaml` returns ≥ 1 hit (rebased results_root).
    - `grep "susie_policy_L20.yaml" config/pipeline_lsweep_L20_overlay.yaml` returns ≥ 1 hit (finemap.policy override propagated).
    - `grep "coloc_susie_R2" config/pipeline_canonical_r2_overlay.yaml` returns ≥ 1 hit.
    - Each policy YAML preserves all non-L fields from `config/susie_policy.yaml` (verify via diff: `diff <(grep -v '^susie:\|^  L:' config/susie_policy.yaml) <(grep -v '^susie:\|^  L:' config/susie_policy_L20.yaml)` returns no substantive differences).
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f config/susie_policy_L15.yaml ] && [ -f config/susie_policy_L20.yaml ] && [ -f config/susie_policy_L30.yaml ] && [ -f config/pipeline_lsweep_L15_overlay.yaml ] && [ -f config/pipeline_lsweep_L20_overlay.yaml ] && [ -f config/pipeline_lsweep_L30_overlay.yaml ] && [ -f config/pipeline_canonical_r2_overlay.yaml ] && grep -q "L: 15" config/susie_policy_L15.yaml && grep -q "L: 20" config/susie_policy_L20.yaml && grep -q "L: 30" config/susie_policy_L30.yaml && grep -q "results_lsweep_L20" config/pipeline_lsweep_L20_overlay.yaml && grep -q "susie_policy_L20.yaml" config/pipeline_lsweep_L20_overlay.yaml && grep -q "coloc_susie_R2" config/pipeline_canonical_r2_overlay.yaml && echo PASS</automated>
  </verify>
  <done>
    7 config YAMLs exist with correct L overrides + parallel results_root/output_dir rebasing. Atomic commit landed. Wave 1 + Wave 2 dispatch can now reference these files. Verifies REQ-SUSIE-RSS-POLICY scaffolding.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Snakemake config-merge propagation dry-run (Pitfall 2 mitigation)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
    src/snakemake/rules/finemap.smk  # MAY be modified if dry-run fails
  </files>
  <read_first>
    - src/snakemake/rules/finemap.smk lines 60-95 (rule run_finemap; line 70-71 hard-codes policy="config/susie_policy.yaml")
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 2: L-sweep policy YAML override doesn't propagate" (the entire pitfall is mandatory reading)
    - config/pipeline_lsweep_L20_overlay.yaml (just created in Task 3)
  </read_first>
  <action>
    Run a single-locus dry-run against the L=20 overlay. The objective is to verify `--configfile config/pipeline_lsweep_L20_overlay.yaml` causes the produced JSON's `L_used` field to be 20, NOT 10.

    1. Dry-run a single locus (use `--dry-run` first to see what Snakemake plans to do):
       ```bash
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
       $SMK \
         --configfile config/pipeline.yaml \
         --configfile config/pipeline_lsweep_L20_overlay.yaml \
         --dry-run --quiet \
         -s Snakefile \
         results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json 2>&1 | tee logs/wave0_pitfall2_dryrun.log
       ```
       Inspect the dry-run output for the rule's input policy file. If the dry-run shows `policy="config/susie_policy.yaml"` (the hardcoded value) instead of `config/susie_policy_L20.yaml`, the overlay is NOT propagating — proceed to step 3.

    2. Execute the single-locus fire:
       ```bash
       $SMK \
         --configfile config/pipeline.yaml \
         --configfile config/pipeline_lsweep_L20_overlay.yaml \
         --profile config/cluster_lsf \
         --jobs 4 --keep-going --use-conda --conda-prefix .snakemake/conda --latency-wait 120 \
         -s Snakefile \
         results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json
       ```
       Wait via `bjobs -J 'ta_sh2b3_W0_*' -a` until DONE. Then:
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e \
         'j <- jsonlite::fromJSON("results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json"); cat(sprintf("L_used=%d\n", j$L_used))'
       ```
       If `L_used=20` → propagation works; record outcome and skip step 3.
       If `L_used=10` → propagation FAILS; proceed to step 3.

    3. **Fallback patch** (only if step 2 returned `L_used=10`):
       Edit `src/snakemake/rules/finemap.smk` line 70-71 (or wherever `policy=` appears as a static input) to read:

       ```python
       policy = config.get("finemap", {}).get("policy", "config/susie_policy.yaml")
       ```

       And substitute that variable into the rule's `input.policy` declaration. Re-run step 2. If now `L_used=20`, commit the patch:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add src/snakemake/rules/finemap.smk
       git commit -m "fix(ta-sh2b3, W0): make finemap.smk policy config-aware (Pitfall 2 mitigation)"
       ```

    4. Append to CONTEXT.md (under `<decisions>`):

       ```markdown
       ### D-TA-Wave-0-pitfall2: Snakemake config-merge propagation outcome

       **Recorded:** {timestamp}

       **Outcome:** {NATIVE_PROPAGATION_WORKS | PATCH_REQUIRED}

       **Evidence:** L=20 single-locus dry-run produced bmi.EUR.SH2B3_12q24.json with `L_used = {20|10}` (expected 20).

       {If patch required:}
       **Patch commit:** {sha} — finemap.smk line {N} now reads `config.get("finemap", {}).get("policy", "config/susie_policy.yaml")`
       ```

    5. Atomic commit for the addendum:
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W0): record Pitfall 2 (config-merge propagation) outcome"
       ```
  </action>
  <acceptance_criteria>
    - Single-locus dry-run produced `results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json` with `L_used == 20` (per Rscript verification).
    - If `L_used == 10`, finemap.smk was patched to read `config.get("finemap", {}).get("policy", ...)` and the re-run produced `L_used == 20`.
    - `grep "D-TA-Wave-0-pitfall2:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep -E "Outcome:.*NATIVE_PROPAGATION_WORKS|Outcome:.*PATCH_REQUIRED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches one of the two outcomes.
    - LSF job for the dry-run completed with exit code 0 (`bhist -l ${JOB_ID}` shows DONE).
    - Wave 1 driver in Task 5 references whichever path was unblocked (no hardcoded fallback assumption).
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e 'j <- jsonlite::fromJSON("results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json"); stopifnot(j$L_used == 20); cat("PASS\n")' && grep -q "D-TA-Wave-0-pitfall2:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md</automated>
  </verify>
  <done>
    Snakemake config-merge propagation of `finemap.policy` override verified by single-locus dry-run; `L_used == 20` confirmed in the produced JSON. If propagation didn't work natively, finemap.smk was patched + committed. Wave 1 dispatch is now safe. RESEARCH.md Pitfall 2 mitigated.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: Scaffold dispatch driver scripts (Wave 1 + Wave 2 + Wave 4)</name>
  <files>
    bin/fire_susie_lsweep.sh
    bin/fire_canonical_susie_pairs.sh
    bin/fire_qtl_coloc_cache_refresh.sh
    src/python/build_coloc_manifest_r2.py
  </files>
  <read_first>
    - scripts/fire_identity_ld_rerun.sh (full content — PRECEDENT for two-phase Snakemake fire with overlay)
    - bin/fire_phase2_stage2_refit.sh (full content — Stage 2 dispatch driver pattern)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Code Examples → Wave 1: SuSiE-RSS L-sweep dispatch" + §"Code Examples → Wave 2: Canonical-pair coloc.susie LSF dispatch" + §"Code Examples → Wave 4: QTL-coloc cache re-fire"
    - results/multitrait/coloc_manifest.tsv (28-row Stage 2 manifest — schema reference for the R2 builder)
  </read_first>
  <action>
    Create 4 driver scripts.

    **(1) `bin/fire_susie_lsweep.sh`** — Wave 1 L-sweep driver. Mirror the pattern in `scripts/fire_identity_ld_rerun.sh` but parameterize over L ∈ {15, 20, 30} and target the 3 SH2B3 EUR traits:

    ```bash
    #!/bin/bash
    # bin/fire_susie_lsweep.sh — Wave 1 driver (D-TA-02)
    # Phase: ta-sh2b3-canonical-and-cache-refresh
    # Fires SuSiE-RSS at L ∈ {15, 20, 30} for SH2B3 EUR BMI + hypertension + stroke
    # Compute envelope: ~4 hr per fit on serial queue with la_multitrait_r env (per AUDIT-RESPONSE 2026-04-26 line 260)
    # 9 fits = 3 traits × 3 L values; aggregate ~12-15 hr (parallel across LSF slots → wall ~4 hr)

    set -euo pipefail
    cd /rs1/researchers/c/ckclinto/coloc_analysis        # D-TA-01

    SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
    LOG="logs/wave1_susie_lsweep_$(date +%Y%m%d_%H%M%S).log"
    mkdir -p logs/lsf logs

    L_VALUES=(15 20 30)
    TRAITS=(bmi hypertension stroke)
    REGION=SH2B3_12q24
    POP=EUR

    for L in "${L_VALUES[@]}"; do
      echo "[$(date +%H:%M:%S)] L=${L} fire starting" | tee -a "$LOG"
      TARGETS=()
      for T in "${TRAITS[@]}"; do
        TARGETS+=("results_lsweep_L${L}/fine_mapping/susie/${T}.${POP}.${REGION}.json")
      done
      $SMK \
        --configfile config/pipeline.yaml \
        --configfile "config/pipeline_lsweep_L${L}_overlay.yaml" \
        --profile config/cluster_lsf \
        --jobs 50 --keep-going --rerun-incomplete --use-conda \
        --conda-prefix .snakemake/conda --latency-wait 120 \
        -s Snakefile \
        "${TARGETS[@]}" \
        2>&1 | tee -a "$LOG"
      echo "[$(date +%H:%M:%S)] L=${L} fire done" | tee -a "$LOG"
    done

    echo "[$(date +%H:%M:%S)] All L-sweep fires complete. Run convergence verification next." | tee -a "$LOG"
    ```

    **(2) `bin/fire_canonical_susie_pairs.sh`** — Wave 2 driver. Targets 9 SH2B3 EUR canonical pairs:

    ```bash
    #!/bin/bash
    # bin/fire_canonical_susie_pairs.sh — Wave 2 driver (D-TA-03)
    # Phase: ta-sh2b3-canonical-and-cache-refresh
    # Fires coloc.susie on 9 new SH2B3 EUR canonical trait-pairs against Wave-1 converged fits
    # at the primary-result-L (set via PRIMARY_L env var; default 20)

    set -euo pipefail
    cd /rs1/researchers/c/ckclinto/coloc_analysis        # D-TA-01

    SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
    LOG="logs/wave2_canonical_susie_$(date +%Y%m%d_%H%M%S).log"
    mkdir -p logs/lsf logs

    PRIMARY_L="${PRIMARY_L:-20}"
    PAIRS=(
      SH2B3_12q24__EUR__asthma_vs_bmi
      SH2B3_12q24__EUR__asthma_vs_hypertension
      SH2B3_12q24__EUR__asthma_vs_stroke
      SH2B3_12q24__EUR__bmi_vs_hypertension
      SH2B3_12q24__EUR__bmi_vs_stroke
      SH2B3_12q24__EUR__bmi_vs_t2d
      SH2B3_12q24__EUR__hypertension_vs_stroke
      SH2B3_12q24__EUR__hypertension_vs_t2d
      SH2B3_12q24__EUR__stroke_vs_t2d
    )
    TARGETS=()
    for p in "${PAIRS[@]}"; do
      TARGETS+=("results/multitrait/coloc_susie_R2/${p}.json")
    done

    echo "[$(date +%H:%M:%S)] Wave 2 fire starting (PRIMARY_L=${PRIMARY_L})" | tee -a "$LOG"
    $SMK \
      --configfile config/pipeline.yaml \
      --configfile config/pipeline_canonical_r2_overlay.yaml \
      --profile config/cluster_lsf \
      --jobs 50 --keep-going --rerun-incomplete --use-conda \
      --conda-prefix .snakemake/conda --latency-wait 120 \
      -s Snakefile \
      "${TARGETS[@]}" \
      2>&1 | tee -a "$LOG"
    echo "[$(date +%H:%M:%S)] Wave 2 fire done" | tee -a "$LOG"
    ```

    **(3) `bin/fire_qtl_coloc_cache_refresh.sh`** — Wave 4 driver. Cache backup `mv` + Snakemake re-fire. SuSiE-RSS layer conditional on `SUSIE_LAYER_SCOPE` env var (set by Wave 4 plan from D-TA-04-DIAGNOSTIC outcome):

    ```bash
    #!/bin/bash
    # bin/fire_qtl_coloc_cache_refresh.sh — Wave 4 driver (D-TA-04)
    # Phase: ta-sh2b3-canonical-and-cache-refresh
    # Cache invalidation + Snakemake re-fire post 069b34f + 7d54183 code fixes
    # Compute envelope: ~10 hr at 50 LSF cores for ~1,274 QTL-coloc attempts; +5 hr if SUSIE_LAYER_SCOPE=yes

    set -euo pipefail
    cd /rs1/researchers/c/ckclinto/coloc_analysis        # D-TA-01

    SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
    LOG="logs/wave4_qtl_coloc_refresh_$(date +%Y%m%d_%H%M%S).log"
    mkdir -p logs/lsf logs

    # Backup with timestamp (Pitfall 5: idempotent backup-name uniqueness)
    TS=$(date +%Y%m%d_%H%M%S)
    BACKUP_QTL="results/qtl_coloc.preFix.bak.${TS}"
    BACKUP_SUSIE="results/fine_mapping/susie.preFix.bak.${TS}"

    if [ ! -d "results/qtl_coloc" ]; then
      echo "ERROR: results/qtl_coloc does not exist. Wave 4 has nothing to invalidate." | tee -a "$LOG"
      exit 1
    fi
    echo "[$(date +%H:%M:%S)] Backing up results/qtl_coloc → ${BACKUP_QTL}" | tee -a "$LOG"
    mv results/qtl_coloc "${BACKUP_QTL}"

    if [ "${SUSIE_LAYER_SCOPE:-no}" = "yes" ]; then
      if [ -d "results/fine_mapping/susie" ]; then
        echo "[$(date +%H:%M:%S)] Backing up results/fine_mapping/susie → ${BACKUP_SUSIE}" | tee -a "$LOG"
        mv results/fine_mapping/susie "${BACKUP_SUSIE}"
      fi
    fi

    # Snakemake re-fire — target 'all_qtl_coloc' rule (verify rule name in Wave 0 Task 1 Snakefile rule-name surface)
    echo "[$(date +%H:%M:%S)] Snakemake re-fire starting" | tee -a "$LOG"
    $SMK \
      --configfile config/pipeline.yaml \
      --profile config/cluster_lsf \
      --jobs 50 --keep-going --rerun-incomplete --use-conda \
      --conda-prefix .snakemake/conda --latency-wait 120 \
      -s Snakefile \
      all_qtl_coloc \
      2>&1 | tee -a "$LOG"
    echo "[$(date +%H:%M:%S)] Wave 4 re-fire done. Run PASS/FAIL verification next." | tee -a "$LOG"
    ```

    **(4) `src/python/build_coloc_manifest_r2.py`** — Manifest builder for the 9 R2 SH2B3 EUR canonical pairs. The Wave 2 driver targets `results/multitrait/coloc_susie_R2/{pair_id}.json`; the `run_coloc_susie` rule (per RESEARCH.md, in `coloc.smk` line 88) reads from a manifest. This script generates a parallel manifest:

    ```python
    #!/usr/bin/env python3
    """
    src/python/build_coloc_manifest_r2.py
    Wave 2 manifest builder (D-TA-03)

    Filters the existing results/multitrait/coloc_manifest.tsv to the 9 SH2B3 EUR
    canonical trait-pairs (lattice minus already-on-disk asthma_vs_t2d) and writes
    a parallel manifest at results/multitrait/coloc_manifest_R2.tsv.
    """
    from pathlib import Path
    import pandas as pd

    REPO_ROOT = Path("/rs1/researchers/c/ckclinto/coloc_analysis")
    SOURCE_MANIFEST = REPO_ROOT / "results/multitrait/coloc_manifest.tsv"
    R2_MANIFEST = REPO_ROOT / "results/multitrait/coloc_manifest_R2.tsv"

    R2_PAIRS = {
        "SH2B3_12q24__EUR__asthma_vs_bmi",
        "SH2B3_12q24__EUR__asthma_vs_hypertension",
        "SH2B3_12q24__EUR__asthma_vs_stroke",
        "SH2B3_12q24__EUR__bmi_vs_hypertension",
        "SH2B3_12q24__EUR__bmi_vs_stroke",
        "SH2B3_12q24__EUR__bmi_vs_t2d",
        "SH2B3_12q24__EUR__hypertension_vs_stroke",
        "SH2B3_12q24__EUR__hypertension_vs_t2d",
        "SH2B3_12q24__EUR__stroke_vs_t2d",
    }


    def main() -> None:
        if not SOURCE_MANIFEST.exists():
            raise FileNotFoundError(f"{SOURCE_MANIFEST} not present; cannot build R2 manifest")
        src = pd.read_csv(SOURCE_MANIFEST, sep="\t")
        # The pair_id column name should match the source manifest schema; verify at runtime
        if "pair_id" not in src.columns:
            raise KeyError(f"Source manifest missing 'pair_id' column. Columns: {list(src.columns)}")
        # Filter to the 9 R2 pair IDs. Some may not exist in the source manifest (Stage 2 only had 28 attempts);
        # for missing ones, build a synthetic row by cloning the schema from an existing SH2B3 EUR row.
        existing = src[src["pair_id"].isin(R2_PAIRS)]
        missing = R2_PAIRS - set(existing["pair_id"].tolist())
        if missing:
            template_rows = src[src["pair_id"].str.startswith("SH2B3_12q24__EUR__")]
            if template_rows.empty:
                raise RuntimeError(
                    f"Cannot synthesize missing R2 pairs {missing}: no SH2B3 EUR template row in source manifest"
                )
            template = template_rows.iloc[0].copy()
            for pid in sorted(missing):
                row = template.copy()
                row["pair_id"] = pid
                # Update trait1 / trait2 columns from the pair_id
                if "trait1" in src.columns and "trait2" in src.columns:
                    parts = pid.split("__")[2].split("_vs_")
                    row["trait1"] = parts[0]
                    row["trait2"] = parts[1]
                existing = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
        existing = existing.sort_values("pair_id").reset_index(drop=True)
        R2_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        existing.to_csv(R2_MANIFEST, sep="\t", index=False)
        print(f"Wrote {len(existing)} rows to {R2_MANIFEST}")


    if __name__ == "__main__":
        main()
    ```

    Make all 3 driver scripts executable: `chmod +x bin/fire_susie_lsweep.sh bin/fire_canonical_susie_pairs.sh bin/fire_qtl_coloc_cache_refresh.sh`.

    Atomic commit (explicit file paths):
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add bin/fire_susie_lsweep.sh bin/fire_canonical_susie_pairs.sh bin/fire_qtl_coloc_cache_refresh.sh src/python/build_coloc_manifest_r2.py
    git commit -m "feat(ta-sh2b3, W0): scaffold W1/W2/W4 dispatch drivers + R2 manifest builder"
    ```
  </action>
  <acceptance_criteria>
    - 4 files exist on disk: `bin/fire_susie_lsweep.sh`, `bin/fire_canonical_susie_pairs.sh`, `bin/fire_qtl_coloc_cache_refresh.sh`, `src/python/build_coloc_manifest_r2.py`.
    - 3 bin/ scripts are executable: `[ -x bin/fire_susie_lsweep.sh ]`, etc.
    - `grep "L_VALUES=(15 20 30)" bin/fire_susie_lsweep.sh` returns ≥ 1 hit.
    - `grep "SH2B3_12q24__EUR__bmi_vs_hypertension" bin/fire_canonical_susie_pairs.sh` returns ≥ 1 hit.
    - `grep "preFix.bak" bin/fire_qtl_coloc_cache_refresh.sh` returns ≥ 1 hit.
    - `grep "SUSIE_LAYER_SCOPE" bin/fire_qtl_coloc_cache_refresh.sh` returns ≥ 1 hit (conditional SuSiE-RSS layer logic present).
    - `python -c "import ast; ast.parse(open('src/python/build_coloc_manifest_r2.py').read())"` returns exit 0 (Python syntax valid).
    - `grep -c "SH2B3_12q24__EUR__" src/python/build_coloc_manifest_r2.py` ≥ 9 (all 9 pairs enumerated).
    - Each driver's first non-shebang line is `cd /rs1/researchers/c/ckclinto/coloc_analysis` (D-TA-01 invariant).
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -x bin/fire_susie_lsweep.sh ] && [ -x bin/fire_canonical_susie_pairs.sh ] && [ -x bin/fire_qtl_coloc_cache_refresh.sh ] && [ -f src/python/build_coloc_manifest_r2.py ] && grep -q "L_VALUES=(15 20 30)" bin/fire_susie_lsweep.sh && grep -q "SH2B3_12q24__EUR__bmi_vs_hypertension" bin/fire_canonical_susie_pairs.sh && grep -q "preFix.bak" bin/fire_qtl_coloc_cache_refresh.sh && grep -q "SUSIE_LAYER_SCOPE" bin/fire_qtl_coloc_cache_refresh.sh && python3 -c "import ast; ast.parse(open('src/python/build_coloc_manifest_r2.py').read())" && [ "$(grep -c 'SH2B3_12q24__EUR__' src/python/build_coloc_manifest_r2.py)" -ge 9 ] && echo PASS</automated>
  </verify>
  <done>
    All 3 dispatch drivers + the R2 manifest builder land on disk, executable, with explicit `/rs1/.../coloc_analysis` cwd (D-TA-01) + correct queue/env references + cache backup logic. Atomic commit landed. Wave 1, Wave 2, Wave 4 can now invoke their drivers without further scaffolding.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 6: Scaffold C1-C15 verification harness (bin/verify_ta_sh2b3_phase.sh)</name>
  <files>
    bin/verify_ta_sh2b3_phase.sh
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md (full file — every C-row's automated command goes into this script)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Validation Architecture → Phase Requirements → Test Map" (mirrors VALIDATION.md)
  </read_first>
  <action>
    Create `bin/verify_ta_sh2b3_phase.sh` — a shell harness that runs all C1–C15 dimension checks and emits PASS/WARN/FAIL JSON. Each check is a function `check_C{N}` returning 0/1/2 (PASS/WARN/FAIL) and printing a JSON-line.

    ```bash
    #!/bin/bash
    # bin/verify_ta_sh2b3_phase.sh — Phase ta-sh2b3 C1-C15 verification harness
    # Usage:
    #   ./bin/verify_ta_sh2b3_phase.sh [--wave N]   # run only checks for wave N
    #   ./bin/verify_ta_sh2b3_phase.sh              # run all checks
    # Output: one JSON-line per check at stdout; exit code = number of FAILures

    set -uo pipefail
    REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    cd "$REPO"
    JSON_OUT=()
    FAIL_COUNT=0

    emit_json() {
      local cid="$1" wave="$2" status="$3" msg="$4"
      JSON_OUT+=("{\"check\":\"$cid\",\"wave\":$wave,\"status\":\"$status\",\"msg\":\"$msg\"}")
      [ "$status" = "FAIL" ] && FAIL_COUNT=$((FAIL_COUNT+1))
    }

    # C1: D-TA-01 path resolves on login02
    check_C1() {
      if [ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ]; then
        local rs1_head gpfs_head
        rs1_head=$(cd /rs1/researchers/c/ckclinto/coloc_analysis && git rev-parse HEAD 2>/dev/null || echo "ERR")
        gpfs_head=$(git rev-parse HEAD 2>/dev/null || echo "ERR")
        if [ "$rs1_head" = "$gpfs_head" ]; then
          emit_json C1 0 PASS "rs1 HEAD = GPFS HEAD = $rs1_head"
        else
          emit_json C1 0 FAIL "rs1 HEAD ($rs1_head) != GPFS HEAD ($gpfs_head)"
        fi
      else
        emit_json C1 0 WARN "/rs1/.../coloc_analysis/.git not present on this node — verify on login02"
      fi
    }

    # C2: 069b34f + 7d54183 are HEAD ancestors
    check_C2() {
      git merge-base --is-ancestor 069b34f HEAD 2>/dev/null && \
      git merge-base --is-ancestor 7d54183 HEAD 2>/dev/null && \
        emit_json C2 0 PASS "069b34f + 7d54183 both HEAD ancestors" || \
        emit_json C2 0 FAIL "code-fix ancestry failed"
    }

    # C3: D-TA-04 diagnostic recorded in CONTEXT addendum
    check_C3() {
      grep -q "D-TA-04-DIAGNOSTIC:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && \
        emit_json C3 0 PASS "D-TA-04-DIAGNOSTIC sub-section present in CONTEXT" || \
        emit_json C3 0 FAIL "D-TA-04-DIAGNOSTIC not yet recorded"
    }

    # C4: D-TA-05 OSF coverage recorded
    check_C4() {
      grep -q "D-TA-OSF-COVERAGE:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && \
        emit_json C4 0 PASS "D-TA-OSF-COVERAGE outcome recorded" || \
        emit_json C4 0 FAIL "D-TA-OSF-COVERAGE not yet recorded"
    }

    # C5: SuSiE-RSS converges at chosen L for SH2B3 EUR BMI/HTN/stroke
    check_C5() {
      local primary_l="${PRIMARY_L:-20}"
      local out
      out=$(/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript -e "
        library(jsonlite)
        traits <- c('bmi','hypertension','stroke')
        all_pass <- TRUE
        for (t in traits) {
          f <- sprintf('results_lsweep_L%d/fine_mapping/susie/%s.EUR.SH2B3_12q24.json', $primary_l, t)
          if (!file.exists(f)) { cat(sprintf('%s: MISSING\\n', f)); all_pass <- FALSE; next }
          j <- jsonlite::fromJSON(f)
          ncs <- length(j\$credible_sets)
          conv <- grepl('^converged', j\$convergence_status)
          sat  <- isTRUE(j\$L_saturated)
          ok   <- (ncs < $primary_l) && conv && !sat
          cat(sprintf('%s: L_used=%d n_CS=%d conv=%s sat=%s ok=%s\\n', basename(f), j\$L_used, ncs, j\$convergence_status, sat, ok))
          if (!ok) all_pass <- FALSE
        }
        cat(sprintf('AGG=%s\\n', if (all_pass) 'PASS' else 'FAIL'))
      " 2>&1)
      if echo "$out" | grep -q "AGG=PASS"; then
        emit_json C5 1 PASS "all 3 SH2B3 EUR fits converged at L=$primary_l with n_CS<L"
      else
        emit_json C5 1 FAIL "SuSiE-RSS convergence FAIL: $(echo "$out" | tr '\n' ';')"
      fi
    }

    # C6: BMI–HTN reference-LD coloc.susie produced
    check_C6() {
      local f="results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json"
      if [ -f "$f" ]; then
        local pp
        pp=$(jq -r '.summary."PP.H4.abf"' "$f" 2>/dev/null || echo "ERR")
        if [[ "$pp" =~ ^[0-9.eE+-]+$ ]]; then
          emit_json C6 2 PASS "BMI-HTN PP.H4 = $pp"
        else
          emit_json C6 2 FAIL "PP.H4 unparseable: $pp"
        fi
      else
        emit_json C6 2 FAIL "BMI-HTN R2 JSON missing"
      fi
    }

    # C7: All 9 SH2B3 EUR new pairs produced
    check_C7() {
      local n
      n=$(ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json 2>/dev/null | wc -l)
      if [ "$n" -eq 9 ]; then
        emit_json C7 2 PASS "9 SH2B3 EUR pair JSONs present"
      else
        emit_json C7 2 FAIL "$n / 9 SH2B3 EUR pair JSONs present"
      fi
    }

    # C8: D-TA-WAVE3-OUTCOME branch recorded
    check_C8() {
      if grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" \
        .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md; then
        emit_json C8 3 PASS "D-TA-WAVE3-OUTCOME branch recorded"
      else
        emit_json C8 3 FAIL "D-TA-WAVE3-OUTCOME not recorded as A/B/C"
      fi
    }

    # C9: Cache refresh produces materially different numerics
    check_C9() {
      local n
      n=$(grep -h '"status"' results/qtl_coloc/*.json 2>/dev/null | grep -c '"too_few_snps"' || echo 0)
      if [ "$n" -le 200 ]; then
        emit_json C9 4 PASS "too_few_snps=$n (PASS, baseline 1005, target ≤200)"
      elif [ "$n" -ge 800 ]; then
        emit_json C9 4 FAIL "too_few_snps=$n still ~baseline; SuSiE-RSS layer fallback (W4.5) needed"
      else
        emit_json C9 4 WARN "too_few_snps=$n (intermediate; investigate)"
      fi
    }

    # C10: Wave-5 aggregator outputs refreshed (mtime check)
    check_C10() {
      local oldest_tsv newest_json
      oldest_tsv=$(stat -c '%Y' results/track_a_aggregations/*.tsv 2>/dev/null | sort -n | head -1)
      newest_json=$(stat -c '%Y' results/qtl_coloc/*.json 2>/dev/null | sort -n | tail -1)
      if [ -z "$oldest_tsv" ] || [ -z "$newest_json" ]; then
        emit_json C10 5 WARN "missing aggregator TSVs or qtl_coloc JSONs"
      elif [ "$oldest_tsv" -ge "$newest_json" ]; then
        emit_json C10 5 PASS "aggregator TSVs refreshed post-Wave-4"
      else
        emit_json C10 5 FAIL "aggregator TSVs older than qtl_coloc JSONs"
      fi
    }

    # C11: TRACK-A-FROZEN-NUMBERS LIVE block updated
    check_C11() {
      grep -A 20 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md 2>/dev/null | grep -q "LIVE" && \
        emit_json C11 5 PASS "L10 LIVE block present" || \
        emit_json C11 5 FAIL "L10 LIVE block missing"
    }

    # C12: Stage 2 md5 invariant preserved (whitelist check)
    check_C12() {
      # Whitelist of files this phase intentionally rewrites
      local WHITELIST=(
        "results/multitrait/coloc_summary.tsv"      # Wave 5 explicit re-render
        ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      )
      # NOTE: this check needs a baseline manifest; Wave 7 closeout supplies it.
      if [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv ]; then
        emit_json C12 7 PASS "baseline manifest present (compare in Wave 7)"
      else
        emit_json C12 7 WARN "md5 baseline manifest not yet captured"
      fi
    }

    # C13: Manuscript anchors preserved post-rename
    check_C13() {
      local manuscript=docs/manuscript/id-vs-ref-LD.md
      if [ -f "$manuscript" ]; then
        # Anchor phrases are populated at Wave 6; placeholder check
        local hits=0
        for phrase in "honest-framing-lock" "SUPERSEDED" "Identity-LD Inflation" "Harmonization-Pipeline Diagnostics"; do
          grep -nF "$phrase" "$manuscript" >/dev/null 2>&1 && hits=$((hits+1))
        done
        if [ "$hits" -ge 4 ]; then
          emit_json C13 6 PASS "all 4 honest-framing-lock anchors found"
        else
          emit_json C13 6 FAIL "$hits/4 honest-framing-lock anchors found"
        fi
      else
        emit_json C13 6 WARN "id-vs-ref-LD.md not yet in place (pre-Wave-6)"
      fi
    }

    # C14: Bundle is reproducible and clean
    check_C14() {
      local bundle
      bundle=$(ls -t bundles/*.zip 2>/dev/null | head -1)
      if [ -n "$bundle" ] && unzip -t "$bundle" >/dev/null 2>&1; then
        emit_json C14 7 PASS "bundle $bundle integrity OK"
      else
        emit_json C14 7 WARN "bundle not yet built or unzip -t failed"
      fi
    }

    # C15: OSF deviation log entry added
    check_C15() {
      local f=.planning/amendments/osf_deviations.md
      if [ -f "$f" ] && grep -qE "Cache invalidation|2026-04-(28|29)" "$f"; then
        emit_json C15 7 PASS "deviation entry present"
      elif [ -f "$f" ]; then
        emit_json C15 7 FAIL "osf_deviations.md exists but no cache-invalidation entry"
      else
        emit_json C15 7 WARN "osf_deviations.md not yet created (pre-Wave-7)"
      fi
    }

    # Dispatch
    WAVE_FILTER="${1:-all}"
    if [ "$WAVE_FILTER" = "--wave" ]; then WAVE_FILTER="$2"; fi

    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "0" ] && { check_C1; check_C2; check_C3; check_C4; }
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "1" ] && check_C5
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "2" ] && { check_C6; check_C7; }
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "3" ] && check_C8
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "4" ] && check_C9
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "5" ] && { check_C10; check_C11; }
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "6" ] && check_C13
    [ "$WAVE_FILTER" = "all" ] || [ "$WAVE_FILTER" = "7" ] && { check_C12; check_C14; check_C15; }

    printf '%s\n' "${JSON_OUT[@]}"
    exit "$FAIL_COUNT"
    ```

    Make executable: `chmod +x bin/verify_ta_sh2b3_phase.sh`.

    Run the harness once to verify it executes cleanly (some C-rows will emit WARN since Wave 1+ outputs don't yet exist; this is expected):
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    bin/verify_ta_sh2b3_phase.sh 2>&1 | head -20
    ```

    Atomic commit:
    ```bash
    git add bin/verify_ta_sh2b3_phase.sh
    git commit -m "feat(ta-sh2b3, W0): scaffold C1-C15 verification harness"
    ```
  </action>
  <acceptance_criteria>
    - `bin/verify_ta_sh2b3_phase.sh` exists and is executable.
    - Running it without args produces ≥ 4 JSON-lines (C1, C2, C3, C4 minimum) on stdout.
    - Output JSON-lines are well-formed: `bin/verify_ta_sh2b3_phase.sh 2>/dev/null | jq -r '.check' | sort -u | wc -l` returns ≥ 4.
    - C1 + C2 emit PASS (verified in Task 1).
    - C3 emits PASS (D-TA-04-DIAGNOSTIC recorded in Task 2).
    - The script contains all 15 `check_C{N}` function definitions: `grep -c "^check_C" bin/verify_ta_sh2b3_phase.sh` returns 15.
    - Wave-filter flag works: `bin/verify_ta_sh2b3_phase.sh --wave 0` only emits C1-C4.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -x bin/verify_ta_sh2b3_phase.sh ] && [ "$(grep -c '^check_C' bin/verify_ta_sh2b3_phase.sh)" -eq 15 ] && bin/verify_ta_sh2b3_phase.sh --wave 0 2>/dev/null | jq -r '.check' | grep -q "C1" && bin/verify_ta_sh2b3_phase.sh --wave 0 2>/dev/null | jq -r '.check' | grep -q "C4" && echo PASS</automated>
  </verify>
  <done>
    Verification harness `bin/verify_ta_sh2b3_phase.sh` lands on disk, executable, contains all 15 C-row check functions. Wave 0 checks (C1-C4) pass. Atomic commit landed. Phase-wide verification rail is now in place.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 7: D-TA-05 OSF pre-registration coverage check (HARD GATE on Wave 1)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-05: OSF pre-registration coverage check"
    - .planning/REQUIREMENTS.md §"REQ-OSF-PREREG"
  </read_first>
  <what-built>
    Carter (web-UI on the OSF portal) verifies that the OSF pre-registration at `osf.io/pvb5j` (Methods) and the closeout PDF at `osf.io/az52u` cover the Wave 1 + Wave 2 scope decisions:
    - **(i) L-sweep wording (D-TA-02):** Methods §Fine-Mapping Configuration phrase "an L-sweep re-fit at L ∈ {15, 20, 30} is pre-registered as a follow-on supplementary analysis"
    - **(ii) Canonical-pair scope (D-TA-03):** Pre-registration of HQ#2(iii) re-fire on the 9 SH2B3 EUR canonical trait-pairs

    Wave 0 Tasks 1-6 have completed: source-repo path verified, code-fix ancestry confirmed, D-TA-04 variant-ID format diagnostic recorded, per-L policy YAMLs + dispatch drivers + verification harness scaffolded, Snakemake config-merge propagation verified.
  </what-built>
  <action>
    See <how-to-verify> below — this is a checkpoint:human-verify task. The user (Carter) executes the verification + decision-recording steps; the executor agent presents the outcome and waits for resume-signal.
  </action>
  <how-to-verify>
    1. Open https://osf.io/pvb5j in your browser. Navigate to the Methods §Fine-Mapping Configuration section.
    2. Search the Methods text (or attached PDF) for these phrases:
       - "L-sweep" or "L sweep"
       - "{15, 20, 30}" or "L ∈ {15, 20, 30}" or "L = 15, 20, 30"
       - "L = 20" (single-shot fallback)
       - "canonical pair" / "canonical-pair"
       - "BMI-HTN" / "BMI–hypertension"
       - "HTN-stroke" / "hypertension–stroke"
    3. Open https://osf.io/az52u in your browser (the M1 closeout PDF amendment). Search for the same 6 phrases.
    4. Decide:
       - **COVERED** → all 6 phrases present in either osf.io/pvb5j Methods OR osf.io/az52u closeout PDF
       - **PARTIALLY_COVERED** → some phrases present (e.g., L=20 yes, L-sweep no)
       - **UNCOVERED** → none of the canonical phrases present
    5. If COVERED: append the following to .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md (under `<decisions>`, after D-TA-04-DIAGNOSTIC sub-section):

       ```markdown
       ### D-TA-OSF-COVERAGE: OSF pre-registration coverage outcome (D-TA-05)

       **Recorded:** {timestamp}

       **Outcome:** COVERED

       **Evidence:** {brief description of which phrases were found at which OSF deposit; e.g., "L-sweep + {15, 20, 30} in osf.io/pvb5j Methods §Fine-Mapping Configuration; canonical-pair + BMI-HTN + HTN-stroke in osf.io/az52u closeout PDF p. 7"}

       **Wave 1 status:** CLEARED to fire.
       ```

       Atomic commit: `git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && git commit -m "docs(ta-sh2b3, W0): record D-TA-OSF-COVERAGE=COVERED — Wave 1 cleared"`

    6. If PARTIALLY_COVERED or UNCOVERED: post an OSF amendment as an addendum to osf.io/az52u closeout PDF (~30 min web-UI). The amendment text should rider on the existing closeout and add:
       - L-sweep {15, 20, 30} pre-registered as Wave 1 supplementary analysis
       - 9 SH2B3 EUR canonical trait-pairs re-fire pre-registered as Wave 2 (HQ#2(iii) closure)
       Then append the same `D-TA-OSF-COVERAGE` sub-section to CONTEXT.md but with `**Outcome:** AMENDMENT_POSTED` and the URL/timestamp of the addendum. **Wave 1 remains BLOCKED until you confirm the amendment is live on the OSF portal (visible to the public).**

    **Resume signal:** Type `OSF_COVERED` (Wave 1 cleared) or `OSF_AMENDED` (Wave 1 cleared after amendment confirmed live) or `OSF_BLOCKED` (further investigation needed; pause planning).
  </how-to-verify>
  <acceptance_criteria>
    - `grep "D-TA-OSF-COVERAGE:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep -E "Outcome:.*(COVERED|AMENDMENT_POSTED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - `grep "Wave 1 status:.*CLEARED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - Atomic commit landed.
    - Wave 1 plan can now fire without violating REQ-OSF-PREREG.
  </acceptance_criteria>
  <resume-signal>Type `OSF_COVERED` to clear Wave 1, `OSF_AMENDED` after posting + verifying the amendment, or `OSF_BLOCKED` to pause</resume-signal>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-OSF-COVERAGE:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "Outcome:.*(COVERED|AMENDMENT_POSTED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -q "Wave 1 status:.*CLEARED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    OSF pre-registration coverage verified by Carter web-UI; outcome (COVERED or AMENDMENT_POSTED) recorded in CONTEXT.md addendum; Wave 1 HARD GATE cleared. Verifies C4 in VALIDATION.md. REQ-OSF-PREREG honored. Phase invariant 6 satisfied.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GPFS interactive shell ↔ /rs1 LSF compute | D-TA-01 path verification crosses this; mismatched HEAD = silent wrong-tree dispatch |
| Repo working tree ↔ pre-fix cache (`results/qtl_coloc/`) | Code fixes 069b34f + 7d54183 are in HEAD but caches are pre-fix; Wave 0 only verifies the diagnostic, Wave 4 invalidates |
| In-tree pre-reg draft ↔ OSF portal deposits | D-TA-05 verification crosses this; in-tree text may differ from publicly posted PDF |
| Per-L policy YAML overlays ↔ rule-input declarations | Pitfall 2: Snakemake config-merge may not propagate finemap.policy override into static rule inputs |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-01 | T (Tampering) | Pre-fix `results/qtl_coloc/*.json` cache | mitigate | Wave 0 Task 2 records D-TA-04-DIAGNOSTIC; Wave 4 invalidates with `mv` (not `rm`) preserving rollback path; never modifies in-place |
| T-PROCESS-02 | I (Information disclosure) | Implicit `git add .` could stage `results_identity_ld/` (DEC-2026-04-25-01) | mitigate | Every commit task in Wave 0 uses explicit file paths; verification harness Task 6 scaffolded; Wave 7 final gate `git diff --cached --name-only \| grep -c results_identity_ld` returns 0 |
| T-PROCESS-04 | T (Tampering) | Stage 2 md5 invariant on non-target files | mitigate | Wave 0 Task 6 builds the C12 check function in verify_ta_sh2b3_phase.sh; Wave 7 baseline-and-diff against curated whitelist |
</threat_model>

<verification>
Run `bin/verify_ta_sh2b3_phase.sh --wave 0` and confirm:
- C1: PASS (path resolves; HEADs match)
- C2: PASS (069b34f + 7d54183 are HEAD ancestors)
- C3: PASS (D-TA-04-DIAGNOSTIC recorded)
- C4: PASS (D-TA-OSF-COVERAGE recorded with outcome COVERED or AMENDMENT_POSTED)

Plus:
- All 7 config YAMLs exist (`ls config/susie_policy_L{15,20,30}.yaml config/pipeline_lsweep_L{15,20,30}_overlay.yaml config/pipeline_canonical_r2_overlay.yaml`)
- All 3 dispatch drivers exist + executable (`ls -l bin/fire_susie_lsweep.sh bin/fire_canonical_susie_pairs.sh bin/fire_qtl_coloc_cache_refresh.sh` shows `-rwx`)
- Manifest builder exists (`[ -f src/python/build_coloc_manifest_r2.py ]`)
- Verification harness exists + executable (`[ -x bin/verify_ta_sh2b3_phase.sh ]`)
- Snakemake config-merge propagation verified (single-locus dry-run produced `L_used=20`)
- 6+ atomic commits landed in this wave (one per task)
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C1** D-TA-01 path resolves on login02 — Task 1
- **C2** Code fixes 069b34f + 7d54183 are HEAD ancestors — Task 1
- **C3** Variant-ID format diagnostic recorded — Task 2
- **C4** OSF pre-reg coverage verified — Task 7
- Wave 0 scaffolds the C5–C15 verification commands in `bin/verify_ta_sh2b3_phase.sh` (Task 6) for downstream waves
</verification_criteria>

<success_criteria>
- All 7 tasks complete with atomic commits per task
- D-TA-Wave-0-foundations + D-TA-04-DIAGNOSTIC + D-TA-Wave-0-pitfall2 + D-TA-OSF-COVERAGE all recorded in CONTEXT.md addendum under `<decisions>` block
- Wave 1 HARD GATE (D-TA-05) cleared
- 7 config YAMLs + 3 dispatch drivers + 1 manifest builder + 1 verification harness all on disk + executable + committed
- C1, C2, C3, C4 emit PASS from `bin/verify_ta_sh2b3_phase.sh --wave 0`
- All commits land via `git add <explicit paths>` — never `git add .` / `-A`
- No `results_identity_ld/` files in `git diff --cached`
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W0-foundations-and-osf-gate-SUMMARY.md` with:
- Per-task PASS/FAIL evidence (D1-D7 dimensions: D1 path verification, D2 code-fix ancestry, D3 variant-ID diagnostic, D4 config scaffolding, D5 dispatch drivers, D6 verification harness, D7 OSF gate)
- Recorded decisions (D-TA-Wave-0-foundations, D-TA-04-DIAGNOSTIC, D-TA-Wave-0-pitfall2, D-TA-OSF-COVERAGE)
- Snakefile rule-name surface enumeration (drives Wave 4 dispatch)
- LSF dispatch envelope projections for Wave 1/2/4 (validated against existing precedent)
- Wave 1 GO/NO-GO status (must be GO for Wave 1 to fire)
</output>
