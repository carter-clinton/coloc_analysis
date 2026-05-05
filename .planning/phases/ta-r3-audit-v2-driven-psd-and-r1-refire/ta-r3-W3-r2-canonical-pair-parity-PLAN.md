---
phase: ta-r3-audit-v2-driven-psd-and-r1-refire
plan: 3
slug: W3-r2-canonical-pair-parity
type: execute
wave: 3
depends_on: ["W1", "W2"]
gate_condition: "FIRES iff D-TA-R3-W1-BRANCH_PSD_FIRM or D-TA-R3-W1-BRANCH_PSD_PARTIAL recorded in ta-r3-CONTEXT.md; SKIPPED iff D-TA-R3-W1-BRANCH_PSD_COLLAPSE; DEFERRED_TO_TRACK_B iff D-TA-R3-W1-BRANCH_PSD_NON_CONVERGE. The executor agent reads D-TA-R3-W3-GATE token from ta-r3-CONTEXT.md (set by W1 Task 3) BEFORE firing any task; if gate is SKIPPED or DEFERRED_TO_TRACK_B, executor records a skip-with-rationale to ta-r3-CONTEXT.md as `D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME` and exits cleanly (no LSF dispatch, no commits beyond the deferral note)."
files_modified:
  - bin/fire_canonical_susie_pairs.sh  # parameterize --region + --ancestry (backwards-compatible)
  - config/regions_curated.csv  # MAY need 4 new region rows if not already present
  - results/multitrait/coloc_susie_R2_FTO/  # NEW; FTO_16q12 EUR canonical-pair JSONs
  - results/multitrait/coloc_susie_R2_MC4R/  # NEW; MC4R_18q21 EUR canonical-pair JSONs
  - results/multitrait/coloc_susie_R2_APOL1/  # NEW; APOL1_22q12 EUR canonical-pair JSONs
  - results/multitrait/coloc_susie_R2_CXADR/  # NEW; CXADR_F2RL1_6p21 EUR canonical-pair JSONs
  - src/R/aggregators/merge_r2_into_summary.R  # MAY be NEW (write if not present; mirrors SH2B3 R2 merge pattern from /gsd-quick 260501-wdn)
  - results/multitrait/coloc_summary.tsv  # merged with R2-parity rows
  - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  - logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log
autonomous: true
requirements:
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "W3 gate condition checked BEFORE any task fires: D-TA-R3-W3-GATE in ta-r3-CONTEXT.md must read FIRES (set by W1 Task 3 from BRANCH_PSD_FIRM or BRANCH_PSD_PARTIAL); if SKIPPED or DEFERRED_TO_TRACK_B, executor exits cleanly with deferral note"
    - "bin/fire_canonical_susie_pairs.sh accepts --region and --ancestry args in backwards-compatible manner (default region remains SH2B3, default ancestry remains EUR — existing SH2B3 R2 outputs reproduce bit-for-bit per plan-of-plans risk register row 3)"
    - "4 new region rows present in config/regions_curated.csv if not already there: FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 (all EUR ancestry)"
    - "R2 fire produces ≥1 canonical-pair JSON per region in results/multitrait/coloc_susie_R2_{FTO,MC4R,APOL1,CXADR}/"
    - "src/R/aggregators/merge_r2_into_summary.R exists (NEW or pre-existing); merges new R2 parity rows into coloc_summary.tsv"
    - "coloc_summary.tsv after merge contains R2 rows for all 4 new regions (matching pattern (FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21)__EUR__)"
    - "9 SH2B3 R2 rows preserved + 28 R1 W2-rerun rows preserved post-W3 merge (risk register row 4 + W2 W3 ordering invariant)"
    - "post-W3 coloc_summary.tsv md5 differs from post-W2 md5 (intentional shift; W5 captures successor row in md5_baseline.tsv)"
    - "LSF dispatch via Snakemake's LSF profile uses serial queue (per-pair envelope ~2 hr); bsub_wrapper.sh transparently sets -W=5760 (per memory feedback_lsf_queues.md)"
    - "docs/manuscript/id-vs-ref-LD.md md5 unchanged (63fd81385590ffc8d23d45a0f0598959; honest-framing-lock invariant)"
  artifacts:
    - path: "bin/fire_canonical_susie_pairs.sh"
      provides: "Parameterized R2 fire driver: accepts --region {SH2B3_12q24|FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21} + --ancestry {EUR|AFR}; backwards-compatible default = SH2B3 EUR"
      contains: "--region"
    - path: "results/multitrait/coloc_susie_R2_FTO/"
      provides: "FTO_16q12 EUR canonical-pair coloc.susie outputs"
    - path: "results/multitrait/coloc_susie_R2_MC4R/"
      provides: "MC4R_18q21 EUR canonical-pair coloc.susie outputs"
    - path: "results/multitrait/coloc_susie_R2_APOL1/"
      provides: "APOL1_22q12 EUR canonical-pair coloc.susie outputs"
    - path: "results/multitrait/coloc_susie_R2_CXADR/"
      provides: "CXADR_F2RL1_6p21 EUR canonical-pair coloc.susie outputs"
    - path: "src/R/aggregators/merge_r2_into_summary.R"
      provides: "R2 parity merge aggregator (mirrors SH2B3 R2 merge pattern from /gsd-quick 260501-wdn)"
      contains: "coloc_susie_R2_"
    - path: ".planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md"
      provides: "D-TA-R3-W3-OUTCOME recorded with R2 parity rows landed per region"
      contains: "D-TA-R3-W3-OUTCOME"
  key_links:
    - from: "D-TA-R3-W1-BRANCH_PSD_<FIRM|PARTIAL> (ta-r3-CONTEXT.md)"
      to: "W3 gate FIRES → R2 parity at FTO/MC4R/APOL1/CXADR EUR"
      via: "executor reads D-TA-R3-W3-GATE token; FIRES means task dispatch proceeds"
      pattern: "D-TA-R3-W3-GATE: FIRES"
    - from: "bin/fire_canonical_susie_pairs.sh --region <REGION> --ancestry EUR"
      to: "results/multitrait/coloc_susie_R2_<REGION_SHORT>/*.json"
      via: "parameterized driver dispatches per-region canonical-pair coloc.susie"
      pattern: "--region.*--ancestry"
    - from: "results/multitrait/coloc_susie_R2_{FTO,MC4R,APOL1,CXADR}/*.json"
      to: "results/multitrait/coloc_summary.tsv (merged)"
      via: "src/R/aggregators/merge_r2_into_summary.R"
      pattern: "merge_r2_into_summary"
---

<objective>
Wave 3 — R2 canonical-pair parity at FTO_16q12, MC4R_18q21, APOL1_22q12, and CXADR_F2RL1_6p21 EUR. Audit-driven re-analysis: symmetrize the SH2B3 R2 canonical-pair fire (executed in the predecessor `ta-sh2b3-canonical-and-cache-refresh` phase, W2) across the 4 other admissible regions so the manuscript can claim "of N canonical pairs across the 5 admissible regions, M survive at PP.H4 ≥ 0.8 under matched-LD" rather than the SH2B3-only Tier-A pass that currently reads as selectively-fired (audit-V2 §HQ#2(iii) finding; manuscript line 174 currently defers FTO + MC4R: "canonical-pair R2 re-fires have not yet been executed for these hubs").

**Conditional fire (gated on W1 outcome per OSF amendment paragraph (f)):** This wave's `gate_condition` frontmatter field is the authoritative control:
- W1 = BRANCH_PSD_FIRM → W3 FIRES (SH2B3 anchor empirically supported; R2 parity at other regions is informative)
- W1 = BRANCH_PSD_PARTIAL → W3 FIRES (SH2B3 anchor partially supported; R2 parity still informative for downgrade narrative)
- W1 = BRANCH_PSD_COLLAPSE → W3 SKIPPED (SH2B3 anchor itself fails; parity at other regions is moot; record `D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME`)
- W1 = BRANCH_PSD_NON_CONVERGE → W3 DEFERRED_TO_TRACK_B (deeper LD-panel-vs-GWAS-cohort mismatch; defer to Track B in-sample LD via UKB/AoU EUR; record deferral)

The executor agent's first action is to read `D-TA-R3-W3-GATE` from ta-r3-CONTEXT.md (set by W1 Task 3) and branch on its value. If gate is not FIRES, exit cleanly after writing the deferral note.

Purpose: Closes audit-V2 §HQ#2(iii) on R2 canonical-pair parity. Reused substrate: bin/fire_canonical_susie_pairs.sh (the SH2B3 R2 driver) is parameterized additively (--region + --ancestry args; default values = SH2B3 + EUR for backwards-compatibility per plan-of-plans risk register row 3). This is audit-driven re-analysis, NOT a fix or revision.

Output: 4 new R2-region JSONs directories (`results/multitrait/coloc_susie_R2_{FTO,MC4R,APOL1,CXADR}/`); merged `results/multitrait/coloc_summary.tsv`; `D-TA-R3-W3-OUTCOME` recorded in ta-r3-CONTEXT.md.
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
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md
@CLAUDE.md

<interfaces>
<!-- W1 produced these — W3 gate-reads -->
- D-TA-R3-W1-BRANCH_PSD_<FIRM|PARTIAL|COLLAPSE|NON_CONVERGE> — drives W3 gate
- D-TA-R3-W3-GATE: <FIRES|SKIPPED|DEFERRED_TO_TRACK_B> — set by W1 Task 3 step 4

<!-- W2 produced these — W3 reads (no direct dependency, but ordering avoids merge conflicts) -->
- coloc_summary.tsv post-W2 md5 (in ta-r3-W2-post_refire_md5.txt)
- 28 R1 R-pair JSONs in results/multitrait/coloc_susie/

<!-- Existing files Wave 3 reads / mutates -->
- bin/fire_canonical_susie_pairs.sh — pre-W3: hardcodes SH2B3 in pair names per Explore agent finding (per plan-of-plans risk register row 3); W3 parameterizes --region + --ancestry additively
- config/regions_curated.csv — region manifest; W3 verifies 4 new region rows present (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR)
- src/R/aggregators/ — W3 writes merge_r2_into_summary.R if not present (mirrors SH2B3 R2 merge pattern from /gsd-quick 260501-wdn)
- results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json — 9 SH2B3 R2 JSONs (preserved; merge_r2_into_summary.R reads these PLUS the 4 new region directories)
- /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript — R env for fitter + merge aggregator
- /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake — Snakemake 7.32.4 with Python 3.11

<!-- W3 region-canonical-pair scope (from plan-of-plans + amendment paragraph (f)) -->
- FTO_16q12 EUR: canonical pair candidates per regions_curated.csv (typically BMI–T2D)
- MC4R_18q21 EUR: canonical pair candidates per regions_curated.csv (typically BMI–HTN, BMI–T2D)
- APOL1_22q12 EUR: canonical pair candidates per regions_curated.csv (typically eGFR-related; admissible per existing trait inventory)
- CXADR_F2RL1_6p21 EUR: canonical pair candidates per regions_curated.csv

<!-- Compute envelope -->
- ~2-3 hr per region × 4 regions ÷ 4 parallel slots = ~3 hr wall
- Each region runs serially internally per region (canonical-pair coloc.susie ~10-30 min/pair)
- Memory: 32 GB per LSF job
- Queue: serial; -W: 5760 min via bsub_wrapper.sh

<!-- Pre-fire HARD GATE check -->
- W3 reads D-TA-R3-W3-GATE from ta-r3-CONTEXT.md FIRST; if not FIRES, exit cleanly with deferral note
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Read W3 gate from ta-r3-CONTEXT.md; if FIRES proceed; if SKIPPED or DEFERRED_TO_TRACK_B record deferral and exit cleanly. If FIRES, parameterize bin/fire_canonical_susie_pairs.sh additively (--region + --ancestry) backwards-compatibly + verify 4 new region rows in config/regions_curated.csv</name>
  <files>
    bin/fire_canonical_susie_pairs.sh
    config/regions_curated.csv
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (D-TA-R3-W3-GATE token; AUTHORITATIVE for whether this wave fires)
    - bin/fire_canonical_susie_pairs.sh (current state — hardcodes SH2B3 in pair names per plan-of-plans risk register row 3; W3 parameterizes additively)
    - config/regions_curated.csv (region manifest; W3 verifies 4 new region rows + adds if missing)
    - /home/ckclinto/.claude/plans/ta-r3-audit-v2-driven-psd-and-r1-refire-cryptic-rabin.md §"Wave 3 Tasks (skeleton)" lines 156-166 (PRIMARY SPEC; tasks 1-2 source)
    - .planning/amendments/osf-amendment-r3-2026-05-04.md §"New analytical commitments — R2 canonical-pair parity re-fire" lines 75-77 (W3 conditional gate spec; AUTHORITATIVE)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md §"Task 1" (predecessor SH2B3 R2 fire pattern; W3 mirrors but parameterized)
  </read_first>
  <action>
    1. **READ W3 GATE FIRST** (gate_condition enforcement):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       GATE=$(grep -oE "D-TA-R3-W3-GATE: (FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" \
              .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | \
              grep -oE "(FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" | head -1)
       echo "W3 gate: $GATE"

       if [ "$GATE" = "SKIPPED" ]; then
         W1_BRANCH=$(grep -oE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" \
                     .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | \
                     grep -oE "(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" | head -1)
         cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME: W3 SKIPPED ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Reason:** W1 outcome = BRANCH_PSD_${W1_BRANCH}; SH2B3 anchor itself does not survive PSD-regularized re-fit (PP.H4 < 0.5 at all converged lambda values). R2 canonical-pair parity at FTO_16q12 / MC4R_18q21 / APOL1_22q12 / CXADR_F2RL1_6p21 EUR is moot when the SH2B3 anchor cannot serve as a comparator.

       **Manuscript implication (informational; OUT of phase scope):** The Cowork-side v5 manuscript narrative under BRANCH_PSD_COLLAPSE branch already does NOT require R2 parity at the other 4 regions — the SH2B3-only Tier-A claim is reframed as not surviving matched-LD; the other 4 regions are not promoted to Tier-A in this branch.

       **Atomic commit follows; W3 exits cleanly with no LSF dispatch.**
       EOF
         git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
         git commit -m "docs(ta-r3, W3): SKIPPED on W1 outcome BRANCH_PSD_${W1_BRANCH} (audit-driven re-analysis; record D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME)"
         echo "W3 SKIPPED; exit cleanly"
         exit 0
       fi

       if [ "$GATE" = "DEFERRED_TO_TRACK_B" ]; then
         W1_BRANCH=$(grep -oE "D-TA-R3-W1-BRANCH_PSD_(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" \
                     .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | \
                     grep -oE "(FIRM|PARTIAL|COLLAPSE|NON_CONVERGE)" | head -1)
         cat >> .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md <<EOF

       ### D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME: W3 DEFERRED_TO_TRACK_B ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Reason:** W1 outcome = BRANCH_PSD_NON_CONVERGE; even with PSD regularization across all lambda values, per-trait fits remain non-converged — indicates a deeper LD-panel-vs-GWAS-cohort mismatch (1000G EUR LD reference ≠ MVP/UKB/HRC GWAS cohort LD structure for SH2B3 12q24). R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR is deferred to Track B (in-sample LD via UKB or AoU EUR), where the LD reference matches the GWAS cohort.

       **Track B handoff:** R2 canonical-pair parity at the 4 admissible regions becomes Track B M4 substrate (per Amendment §3 M4 — REQ-TWO-STAGE-COLOC + REQ-HYPRCOLOC-MULTI). This deferral is documented in the Cowork-side v5 manuscript as a "future work" pointer.

       **Atomic commit follows; W3 exits cleanly with no LSF dispatch.**
       EOF
         git add .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
         git commit -m "docs(ta-r3, W3): DEFERRED_TO_TRACK_B on W1 outcome BRANCH_PSD_NON_CONVERGE (audit-driven re-analysis; in-sample LD via Track B M4 path)"
         echo "W3 DEFERRED_TO_TRACK_B; exit cleanly"
         exit 0
       fi

       if [ "$GATE" != "FIRES" ]; then
         echo "ABORT: D-TA-R3-W3-GATE token has unexpected value '$GATE'; expected FIRES, SKIPPED, or DEFERRED_TO_TRACK_B"
         exit 1
       fi
       echo "PASS: W3 gate = FIRES; proceeding with parameterization + dispatch"
       ```

    2. **Parameterize bin/fire_canonical_susie_pairs.sh** to accept `--region` and `--ancestry` arguments in a backwards-compatible manner (default `--region SH2B3_12q24` + `--ancestry EUR` so existing SH2B3 R2 outputs reproduce bit-for-bit per plan-of-plans risk register row 3). The current script hardcodes SH2B3 in target pair names; the W3 modification:
       - Accept `--region` and `--ancestry` via getopts or simple arg parsing
       - Default region=SH2B3_12q24, ancestry=EUR
       - Substitute the region/ancestry tokens into the pair_id string template (e.g., `${REGION}__${ANCESTRY}__bmi_vs_hypertension` instead of hardcoded `SH2B3_12q24__EUR__bmi_vs_hypertension`)
       - Output directory becomes `results/multitrait/coloc_susie_R2_${REGION_SHORT}/` (where `REGION_SHORT` is the leading-token of REGION, e.g., `SH2B3` → `SH2B3`, `FTO_16q12` → `FTO`, `MC4R_18q21` → `MC4R`, `APOL1_22q12` → `APOL1`, `CXADR_F2RL1_6p21` → `CXADR`)
       - Backwards compatibility check: invoking with no args produces SH2B3 R2 output identical to pre-W3 (verify md5sum sample on one of the existing R2 JSONs IF feasible, else verify dry-run logs match)

       Use the Edit tool to read the current `bin/fire_canonical_susie_pairs.sh`, then add an arg-parsing block at the top + substitute hardcoded SH2B3 / EUR tokens with `${REGION}` / `${ANCESTRY}` variables. Preserve all other logic (LSF dispatch, conda env, Snakemake invocation patterns).

       After editing, run `--help` to verify the parameterization works:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       chmod +x bin/fire_canonical_susie_pairs.sh
       bash bin/fire_canonical_susie_pairs.sh --help 2>&1 | grep -E "(--region|--ancestry)" || \
         { echo "WARN: --help does not mention --region/--ancestry; verify arg parsing manually"; }
       ```

    3. **Verify 4 new region rows in config/regions_curated.csv** (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR). If missing, append them with the same schema as SH2B3_12q24 EUR (region_id, ancestry, chr, start, end, anchor_gene, canonical_pairs).

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       MISSING_REGIONS=()
       for R in FTO_16q12 MC4R_18q21 APOL1_22q12 CXADR_F2RL1_6p21; do
         if ! grep -qE "^${R},EUR" config/regions_curated.csv; then
           MISSING_REGIONS+=("$R")
         fi
       done
       echo "Missing regions: ${MISSING_REGIONS[*]:-none}"

       # If any missing, the Cowork-side audit is expected to have provided canonical-pair definitions per region.
       # For W3 we add stub rows with placeholders; the canonical-pair enumeration depends on regions_curated.csv schema.
       # If canonical-pair lists are not in the schema, leave as a follow-up note for Cowork-side.
       if [ ${#MISSING_REGIONS[@]} -gt 0 ]; then
         echo "ACTION: append missing region rows to config/regions_curated.csv following the SH2B3_12q24 row schema"
         # The append happens via Edit (preserves existing rows; only adds new ones); see Edit tool invocation below.
       fi
       ```

       If missing, use the Edit tool to append rows to `config/regions_curated.csv` with the same schema as the SH2B3_12q24 EUR row. Use the chr/start/end ranges:
       - FTO_16q12 EUR: chr 16, ~52.5–54.5 Mb (GRCh37); anchor gene FTO; canonical pairs include BMI–T2D
       - MC4R_18q21 EUR: chr 18, ~57.5–59.5 Mb (GRCh37); anchor gene MC4R; canonical pairs BMI–HTN, BMI–T2D
       - APOL1_22q12 EUR: chr 22, ~36.0–37.0 Mb (GRCh37); anchor gene APOL1; canonical pairs (per audit-V2 admissible inventory)
       - CXADR_F2RL1_6p21 EUR: chr 6 (note: CXADR + F2RL1 cluster); anchor genes CXADR + F2RL1; canonical pairs (per audit-V2 admissible inventory)

       Note: if the schema requires explicit canonical-pair enumeration and the audit-V2 admissible inventory does not provide it for the 4 regions in deterministic form, document this as a precondition that Cowork-side must clarify; the W3 task can still parameterize the driver and dispatch, but the canonical-pair selection per region falls back to "all pairwise EUR pairs from existing 5 traits" or the admissible subset documented in audit-V2.

    4. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add bin/fire_canonical_susie_pairs.sh \
               config/regions_curated.csv \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
       git commit -m "feat(ta-r3, W3): parameterize fire_canonical_susie_pairs.sh additively (--region + --ancestry; default SH2B3 EUR backwards-compatible) + verify 4 new region rows in regions_curated.csv (audit-driven re-analysis)"
       ```
  </action>
  <acceptance_criteria>
    - W3 gate read at task start: if SKIPPED or DEFERRED_TO_TRACK_B, the deferral block is appended to ta-r3-CONTEXT.md and Task 1 exits cleanly (no further tasks fire). If FIRES, Task 1 proceeds.
    - When gate is FIRES: bin/fire_canonical_susie_pairs.sh is executable + accepts --region + --ancestry: `bin/fire_canonical_susie_pairs.sh --help 2>&1 | grep -cE "(--region|--ancestry)"` returns ≥ 1 OR the script source contains both arg parses: `grep -cE "\-\-region|\-\-ancestry" bin/fire_canonical_susie_pairs.sh` returns ≥ 2.
    - When gate is FIRES: 4 new region rows in config/regions_curated.csv: `for R in FTO_16q12 MC4R_18q21 APOL1_22q12 CXADR_F2RL1_6p21; do grep -qE "^${R},EUR" config/regions_curated.csv || { echo "MISSING $R"; exit 1; }; done` exits 0.
    - When gate is FIRES: backwards-compatible default (SH2B3 EUR) preserved: `grep -E "REGION=\"?SH2B3_12q24\"?|default.*SH2B3_12q24|--region.*SH2B3" bin/fire_canonical_susie_pairs.sh | wc -l` returns ≥ 1 OR the script preserves the existing SH2B3 R2 fire path semantics.
    - When gate is FIRES: atomic commit landed for parameterization step.
    - When gate is SKIPPED or DEFERRED: deferral block in ta-r3-CONTEXT.md present: `grep -c "D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && GATE=$(grep -oE "D-TA-R3-W3-GATE: (FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | grep -oE "(FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" | head -1) && if [ "$GATE" = "FIRES" ]; then [ -x bin/fire_canonical_susie_pairs.sh ] && [ "$(grep -cE '\-\-region|\-\-ancestry' bin/fire_canonical_susie_pairs.sh)" -ge 2 ] && for R in FTO_16q12 MC4R_18q21 APOL1_22q12 CXADR_F2RL1_6p21; do grep -qE "^${R},EUR" config/regions_curated.csv || { echo "MISSING $R"; exit 1; }; done && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS; else [ "$(grep -c 'D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS; fi</automated>
  </verify>
  <done>
    W3 gate token read from ta-r3-CONTEXT.md. If gate is not FIRES, deferral block appended and W3 exits cleanly. If gate is FIRES, bin/fire_canonical_susie_pairs.sh parameterized additively (backwards-compatible default = SH2B3 EUR per risk register row 3) and 4 new region rows verified/added to config/regions_curated.csv. Honest-framing-lock manuscript md5 unchanged. Atomic commit landed.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: (Gate=FIRES only) Dispatch R2 canonical-pair fire for each of FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR (parallelizable across 4 LSF slots) + write src/R/aggregators/merge_r2_into_summary.R if not present + merge new R2-parity rows into coloc_summary.tsv</name>
  <files>
    results/multitrait/coloc_susie_R2_FTO/
    results/multitrait/coloc_susie_R2_MC4R/
    results/multitrait/coloc_susie_R2_APOL1/
    results/multitrait/coloc_susie_R2_CXADR/
    src/R/aggregators/merge_r2_into_summary.R
    results/multitrait/coloc_summary.tsv
    logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log
    .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md
  </files>
  <read_first>
    - .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md (verify D-TA-R3-W3-GATE = FIRES; if not, abort)
    - bin/fire_canonical_susie_pairs.sh (Task 1 parameterized output; verify --region + --ancestry args work)
    - config/regions_curated.csv (Task 1 verified 4 new region rows)
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json (existing 9 SH2B3 R2 outputs; merge_r2_into_summary.R reads these PLUS the 4 new region directories)
    - src/R/aggregators/ (check if merge_r2_into_summary.R already exists from /gsd-quick 260501-wdn; if yes, reuse; if no, create)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md §"Task 1 step 3-7" (predecessor SH2B3 R2 fire pattern; mirror per-region)
  </read_first>
  <action>
    1. **Re-verify gate is FIRES** (paranoid double-check; Task 1 already exited cleanly if not FIRES):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       GATE=$(grep -oE "D-TA-R3-W3-GATE: (FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md | grep -oE "(FIRES|SKIPPED|DEFERRED_TO_TRACK_B)" | head -1)
       [ "$GATE" = "FIRES" ] || { echo "ABORT: gate is $GATE; Task 2 should not have been invoked"; exit 1; }
       echo "PASS: gate confirmed FIRES"
       ```

    2. **Dispatch R2 canonical-pair fire per region** via the parameterized driver. Each region runs as an independent LSF job; dispatch all 4 in parallel.

       ```bash
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       export LSF_UNIT_FOR_LIMITS=GB
       mkdir -p logs/ta_r3_W3_r2_parity
       LOG=logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log
       : > "$LOG"

       declare -A REGION_SHORT
       REGION_SHORT[FTO_16q12]=FTO
       REGION_SHORT[MC4R_18q21]=MC4R
       REGION_SHORT[APOL1_22q12]=APOL1
       REGION_SHORT[CXADR_F2RL1_6p21]=CXADR

       for region in FTO_16q12 MC4R_18q21 APOL1_22q12 CXADR_F2RL1_6p21; do
         short=${REGION_SHORT[$region]}
         outdir="results/multitrait/coloc_susie_R2_${short}"
         mkdir -p "$outdir"
         jobname="ta_r3_W3_${short}_r2"
         # Each region's driver invocation runs through bsub_wrapper.sh transparently for -W=5760
         QUEUE=serial config/bsub_wrapper.sh \
           bsub -J "$jobname" \
                -q serial \
                -n 1 \
                -R "rusage[mem=32000]" \
                -o "logs/ta_r3_W3_r2_parity/${short}_%J.out" \
                -e "logs/ta_r3_W3_r2_parity/${short}_%J.err" \
                bash bin/fire_canonical_susie_pairs.sh --region "$region" --ancestry EUR \
           | tee -a "$LOG"
       done

       echo "[$(date +%H:%M:%S)] All 4 W3 LSF region jobs submitted." | tee -a "$LOG"
       ```

       Note: each `bin/fire_canonical_susie_pairs.sh --region X --ancestry EUR` invocation may itself submit per-pair sub-jobs via Snakemake. The parent LSF job waits for those sub-jobs OR (more likely per ta-sh2b3-W2 predecessor pattern) the script invokes Snakemake directly without further LSF nesting. Verify via Task 1's --help output what the script does internally.

    3. **Monitor LSF jobs to completion** (~3 hr wall expected for 4 regions x 4 parallel slots):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       while bjobs -J 'ta_r3_W3_*' 2>&1 | grep -qE "PEND|RUN"; do
         echo "[$(date +%H:%M:%S)] still running: $(bjobs -J 'ta_r3_W3_*' 2>&1 | grep -cE 'PEND|RUN')"
         sleep 600  # 10-min poll for long-running wave
       done
       echo "[$(date +%H:%M:%S)] All W3 LSF jobs done."
       ```

    4. **Verify each region produced ≥1 canonical-pair JSON:**

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       for short in FTO MC4R APOL1 CXADR; do
         n=$(ls "results/multitrait/coloc_susie_R2_${short}/"*.json 2>/dev/null | wc -l)
         echo "$short: $n JSONs"
         [ "$n" -ge 1 ] || { echo "WARN: no JSONs for $short; investigate per-pair LSF logs"; }
       done
       ```

    5. **Write src/R/aggregators/merge_r2_into_summary.R** if not present. The aggregator mirrors the SH2B3 R2 merge pattern from `/gsd-quick 260501-wdn` (per plan-of-plans §Reused Existing Substrate). It reads:
       - Existing 9 SH2B3 R2 JSONs at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json`
       - New per-region directories `results/multitrait/coloc_susie_R2_{FTO,MC4R,APOL1,CXADR}/*.json`
       - Existing `results/multitrait/coloc_summary.tsv`
       
       And writes the merged TSV with R2 parity rows appended:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       if [ ! -f src/R/aggregators/merge_r2_into_summary.R ]; then
         mkdir -p src/R/aggregators
         cat > src/R/aggregators/merge_r2_into_summary.R <<'RS'
       #!/usr/bin/env Rscript
       # src/R/aggregators/merge_r2_into_summary.R
       # ta-r3 W3: merge R2 canonical-pair parity rows into coloc_summary.tsv
       # Reads: results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json (9 SH2B3 R2 — existing)
       #        results/multitrait/coloc_susie_R2_FTO/*.json
       #        results/multitrait/coloc_susie_R2_MC4R/*.json
       #        results/multitrait/coloc_susie_R2_APOL1/*.json
       #        results/multitrait/coloc_susie_R2_CXADR/*.json
       #        results/multitrait/coloc_summary.tsv (input)
       # Writes: results/multitrait/coloc_summary.tsv (merged)
       # Mirrors SH2B3 R2 merge pattern from /gsd-quick 260501-wdn.

       suppressPackageStartupMessages({ library(jsonlite); library(data.table) })

       SUMMARY_PATH <- "results/multitrait/coloc_summary.tsv"
       R2_DIRS <- c(
         "results/multitrait/coloc_susie_R2",            # SH2B3 (existing)
         "results/multitrait/coloc_susie_R2_FTO",
         "results/multitrait/coloc_susie_R2_MC4R",
         "results/multitrait/coloc_susie_R2_APOL1",
         "results/multitrait/coloc_susie_R2_CXADR"
       )

       parse_json_to_row <- function(jpath) {
         j <- jsonlite::fromJSON(jpath)
         pair_id <- sub("\\.json$", "", basename(jpath))
         s <- j$summary
         if (is.null(s) || !is.data.frame(s) || nrow(s) == 0) {
           list(pair_id = pair_id, PP.H0 = NA_real_, PP.H1 = NA_real_,
                PP.H2 = NA_real_, PP.H3 = NA_real_, PP.H4 = NA_real_)
         } else {
           idx <- which.max(s[["PP.H4.abf"]])
           list(pair_id = pair_id,
                PP.H0 = s[["PP.H0.abf"]][idx],
                PP.H1 = s[["PP.H1.abf"]][idx],
                PP.H2 = s[["PP.H2.abf"]][idx],
                PP.H3 = s[["PP.H3.abf"]][idx],
                PP.H4 = s[["PP.H4.abf"]][idx])
         }
       }

       # Collect all R2 JSONs
       r2_rows <- list()
       for (d in R2_DIRS) {
         if (!dir.exists(d)) next
         for (f in list.files(d, pattern = "\\.json$", full.names = TRUE)) {
           r2_rows[[length(r2_rows) + 1]] <- parse_json_to_row(f)
         }
       }
       r2_dt <- rbindlist(r2_rows, fill = TRUE)
       cat(sprintf("Collected %d R2 rows from %d directories\n", nrow(r2_dt), length(R2_DIRS)))

       # Read existing coloc_summary.tsv
       existing <- fread(SUMMARY_PATH)
       cat(sprintf("Existing coloc_summary.tsv: %d rows\n", nrow(existing)))

       # Merge: replace rows in existing where pair_id matches an R2 row; append new R2 pair_ids
       schema_cols <- intersect(c("pair_id", "PP.H0", "PP.H1", "PP.H2", "PP.H3", "PP.H4",
                                    "PP.H0.abf", "PP.H1.abf", "PP.H2.abf",
                                    "PP.H3.abf", "PP.H4.abf"),
                                  names(existing))
       # Map r2_dt schema to existing schema (existing may use .abf suffix)
       if ("PP.H0.abf" %in% names(existing)) {
         setnames(r2_dt,
                  c("PP.H0", "PP.H1", "PP.H2", "PP.H3", "PP.H4"),
                  c("PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf"))
       }

       # Replace or append
       existing_pair_ids <- existing$pair_id
       new_pair_ids <- r2_dt$pair_id
       keep_mask <- !(existing$pair_id %in% new_pair_ids)
       merged <- rbind(existing[keep_mask], r2_dt, fill = TRUE)
       cat(sprintf("Merged: %d existing kept + %d R2 = %d total rows\n",
                    sum(keep_mask), nrow(r2_dt), nrow(merged)))

       fwrite(merged, SUMMARY_PATH, sep = "\t", na = "")
       cat(sprintf("WROTE %s\n", SUMMARY_PATH))
       RS
         chmod +x src/R/aggregators/merge_r2_into_summary.R
       fi
       ```

    6. **Run the merge aggregator:**

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript \
         src/R/aggregators/merge_r2_into_summary.R 2>&1 | tee -a "$LOG"
       ```

    7. **Verify post-merge invariants:**
       - 9 SH2B3 R2 rows preserved + 28 R1 rows preserved + ≥4 new R2-parity region rows present in coloc_summary.tsv
       - md5 of coloc_summary.tsv differs from post-W2 md5 (new shift; W5 captures successor row)

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       N_SH2B3=$(awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)
       N_NEW_R2=$(awk -F'\t' 'NR>1 && $1 ~ /^(FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21)__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)
       echo "SH2B3 R2 rows: $N_SH2B3 (must be ≥9)"
       echo "New R2-parity region rows: $N_NEW_R2 (must be ≥4)"
       [ "$N_SH2B3" -ge 9 ] || { echo "ABORT: SH2B3 R2 rows missing post-merge"; exit 1; }
       [ "$N_NEW_R2" -ge 4 ] || { echo "WARN: <4 new R2-parity region rows; some regions may have produced no successful coloc"; }

       POST_W3_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       POST_W2_MD5=$(awk '{print $1}' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W2-post_refire_md5.txt 2>/dev/null)
       echo "post-W3 md5: $POST_W3_MD5"
       echo "post-W2 md5: $POST_W2_MD5"
       [ "$POST_W3_MD5" != "$POST_W2_MD5" ] || \
         echo "WARN: post-W3 md5 unchanged from post-W2; merge may have been a no-op"
       ```

    8. **Append D-TA-R3-W3-OUTCOME to ta-r3-CONTEXT.md** under the existing W3 gate section. Use Edit to append:

       ```markdown
       ### D-TA-R3-W3-OUTCOME: R2 canonical-pair parity FIRED ($(date -u +%Y-%m-%dT%H:%M:%SZ))

       **Per-region R2 parity output:**

       | region | JSONs produced | output directory |
       |---|---|---|
       | FTO_16q12 EUR | <N_FTO> | results/multitrait/coloc_susie_R2_FTO/ |
       | MC4R_18q21 EUR | <N_MC4R> | results/multitrait/coloc_susie_R2_MC4R/ |
       | APOL1_22q12 EUR | <N_APOL1> | results/multitrait/coloc_susie_R2_APOL1/ |
       | CXADR_F2RL1_6p21 EUR | <N_CXADR> | results/multitrait/coloc_susie_R2_CXADR/ |

       **Post-W3 coloc_summary.tsv:**

       | metric | value |
       |---|---|
       | SH2B3 R2 rows preserved | <N_SH2B3> (≥9) |
       | New R2-parity region rows | <N_NEW_R2> (≥4) |
       | R1 W2-rerun rows preserved | <N_R1> |
       | Total rows | <N_TOTAL> |
       | md5 (post-W3) | <POST_W3_MD5> (W5 will append successor row to md5_baseline.tsv) |

       **Manuscript implication (informational; OUT of phase scope):** The Cowork-side v5 manuscript Table 3 can now claim "of N canonical pairs across the 5 admissible regions, M survive at PP.H4 ≥ 0.8 under matched-LD" rather than the SH2B3-only Tier-A pass. Per OSF amendment paragraph (f), the canonical-pair selection across the 4 new regions is determined by the regions_curated.csv canonical_pairs column.
       ```

    9. **Atomic commit** with explicit paths:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add results/multitrait/coloc_summary.tsv \
               src/R/aggregators/merge_r2_into_summary.R \
               .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md \
               logs/ta_r3_W3_r2_parity/r2_parity_dispatch.log
       # Note: results/multitrait/coloc_susie_R2_*/*.json may be gitignored (regenerable);
       # if not, add them explicitly:
       grep -n "results/multitrait/coloc_susie_R2_" .gitignore || \
         git add results/multitrait/coloc_susie_R2_FTO/*.json \
                 results/multitrait/coloc_susie_R2_MC4R/*.json \
                 results/multitrait/coloc_susie_R2_APOL1/*.json \
                 results/multitrait/coloc_susie_R2_CXADR/*.json
       git commit -m "feat(ta-r3, W3): R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR EUR + merge_r2_into_summary.R aggregator (audit-driven re-analysis; SH2B3-only Tier-A pass symmetrized across 5 admissible regions)"
       ```
  </action>
  <acceptance_criteria>
    - Gate confirmed FIRES at task entry: `grep "D-TA-R3-W3-GATE: FIRES" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1 hit (otherwise this task should not have run).
    - 4 region directories exist + each has ≥1 JSON: `for R in FTO MC4R APOL1 CXADR; do [ "$(ls results/multitrait/coloc_susie_R2_${R}/*.json 2>/dev/null | wc -l)" -ge 1 ] || { echo "MISSING $R"; exit 1; }; done` exits 0.
    - src/R/aggregators/merge_r2_into_summary.R exists + executable: `[ -x src/R/aggregators/merge_r2_into_summary.R ]`.
    - Merge aggregator references all 5 R2 directories (existing SH2B3 + 4 new): `grep -cE "coloc_susie_R2_(FTO|MC4R|APOL1|CXADR)|coloc_susie_R2$" src/R/aggregators/merge_r2_into_summary.R` returns ≥ 5.
    - Post-merge coloc_summary.tsv contains R2 rows for all 4 new regions: `awk -F'\t' 'NR>1 && $1 ~ /^(FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21)__EUR__/' results/multitrait/coloc_summary.tsv | wc -l` returns ≥ 4.
    - 9 SH2B3 R2 rows preserved post-merge: `awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l` returns ≥ 9.
    - D-TA-R3-W3-OUTCOME recorded in ta-r3-CONTEXT.md: `grep -c "D-TA-R3-W3-OUTCOME" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` returns ≥ 1.
    - Atomic commit landed: `git log --oneline -1 | grep -E "ta-r3.*W3.*R2 canonical-pair parity.*audit-driven re-analysis"` matches.
    - Honest-framing-lock invariant: `md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1` returns `63fd81385590ffc8d23d45a0f0598959`.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-R3-W3-GATE: FIRES" .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md && for R in FTO MC4R APOL1 CXADR; do [ "$(ls results/multitrait/coloc_susie_R2_${R}/*.json 2>/dev/null | wc -l)" -ge 1 ] || { echo "MISSING $R"; exit 1; }; done && [ -x src/R/aggregators/merge_r2_into_summary.R ] && [ "$(grep -cE 'coloc_susie_R2_(FTO|MC4R|APOL1|CXADR)' src/R/aggregators/merge_r2_into_summary.R)" -ge 4 ] && [ "$(awk -F'\t' 'NR>1 && $1 ~ /^(FTO_16q12|MC4R_18q21|APOL1_22q12|CXADR_F2RL1_6p21)__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)" -ge 4 ] && [ "$(awk -F'\t' 'NR>1 && $1 ~ /^SH2B3_12q24__EUR__/' results/multitrait/coloc_summary.tsv | wc -l)" -ge 9 ] && [ "$(grep -c 'D-TA-R3-W3-OUTCOME' .planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md)" -ge 1 ] && [ "$(md5sum docs/manuscript/id-vs-ref-LD.md | cut -d' ' -f1)" = "63fd81385590ffc8d23d45a0f0598959" ] && echo PASS</automated>
  </verify>
  <done>
    R2 canonical-pair fire dispatched per region (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR); each region produced ≥1 JSON. merge_r2_into_summary.R aggregator landed (NEW or pre-existing) and merged R2 parity rows into coloc_summary.tsv. SH2B3 R2 + R1 W2-rerun + 4 new R2 region rows all present in merged summary. D-TA-R3-W3-OUTCOME recorded in ta-r3-CONTEXT.md. Honest-framing-lock manuscript md5 unchanged. Atomic commit landed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| W3 gate (D-TA-R3-W3-GATE token) ↔ Task 1 + Task 2 dispatch | Task 1 reads gate FIRST; if not FIRES, exits cleanly with deferral note (no LSF dispatch, no further tasks fire) |
| bin/fire_canonical_susie_pairs.sh parameterization ↔ existing SH2B3 R2 reproducibility | Per plan-of-plans risk register row 3: backwards-compatible default (region=SH2B3_12q24, ancestry=EUR) preserves existing SH2B3 R2 outputs bit-for-bit |
| Multi-terminal git staging on GPFS ↔ explicit-path commits | Per `.planning/feedback_multi_terminal_staging.md`: never `git add .` / `-A` |
| coloc_summary.tsv post-W2 md5 ↔ post-W3 md5 (additional shift expected) | Both shifts intentional; W5 captures successor row in md5_baseline.tsv (chain of valid post-Wave md5 values) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-TA-R3-W3-01 | E (Elevation of privilege) | Gate bypassed (W3 fires when W1 returned COLLAPSE/NON_CONVERGE) | mitigate | Task 1 step 1 reads gate token + exits cleanly if not FIRES; Task 2 step 1 re-verifies gate (paranoid double-check) |
| T-TA-R3-W3-02 | T (Tampering) | Existing SH2B3 R2 outputs (9 JSONs) corrupted by parameterization | mitigate | Per plan-of-plans risk register row 3: backwards-compatible default args (--region SH2B3_12q24 --ancestry EUR); existing SH2B3 R2 outputs at coloc_susie_R2/ NOT in W3 modify scope; merge_r2_into_summary.R reads them but does not rewrite them |
| T-TA-R3-W3-03 | I (Information disclosure) | Implicit `git add .` could stage results_identity_ld/ (DEC-2026-04-25-01) | mitigate | All commits use explicit paths only |
| T-TA-R3-W3-04 | I (Information disclosure) | Honest-framing-lock manuscript edit | accept | OUT of phase scope per OSF amendment "What is not changing" |
| T-TA-R3-W3-05 | D (Denial of service) | LSF jobs killed by 30-min queue default RUNLIMIT | mitigate | bsub_wrapper.sh transparently sets -W=5760 for serial queue |
| T-TA-R3-W3-06 | T (Tampering) | merge_r2_into_summary.R drops existing R1/SH2B3 rows in coloc_summary.tsv | mitigate | Aggregator step 7 verifies SH2B3 R2 rows ≥9 + new R2-parity region rows ≥4; failed merge aborts before commit |
</threat_model>

<verification>
- W3 gate read at task entry; if not FIRES, deferral block recorded + exit cleanly (Task 1)
- bin/fire_canonical_susie_pairs.sh parameterized additively (--region + --ancestry) backwards-compatibly (Task 1)
- 4 new region rows verified/added in config/regions_curated.csv (Task 1)
- 4 R2-parity region directories produced ≥1 JSON each (Task 2)
- src/R/aggregators/merge_r2_into_summary.R landed (Task 2)
- coloc_summary.tsv merged with new R2 parity rows; SH2B3 R2 + W2 R1 rows preserved (Task 2)
- D-TA-R3-W3-OUTCOME recorded in ta-r3-CONTEXT.md (Task 2)
- 2 atomic commits landed (Task 1 + Task 2; if FIRES) OR 1 atomic commit (deferral note; if SKIPPED/DEFERRED_TO_TRACK_B)
- Honest-framing-lock manuscript md5 unchanged through all tasks
</verification>

<success_criteria>
- W3 gate enforced at task entry per gate_condition frontmatter (FIRES/SKIPPED/DEFERRED_TO_TRACK_B)
- If FIRES: bin/fire_canonical_susie_pairs.sh parameterized (--region + --ancestry; default SH2B3 EUR backwards-compatible per risk register row 3)
- If FIRES: 4 new region rows in config/regions_curated.csv (FTO_16q12, MC4R_18q21, APOL1_22q12, CXADR_F2RL1_6p21 EUR)
- If FIRES: ≥1 JSON per new region directory + merge_r2_into_summary.R aggregator + coloc_summary.tsv merged
- If FIRES: SH2B3 R2 + R1 W2-rerun rows preserved in merged summary
- If SKIPPED/DEFERRED_TO_TRACK_B: D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME recorded with reason
- bsub_wrapper.sh enforces -W=5760 for serial queue
- Honest-framing-lock manuscript md5 unchanged (63fd81385590ffc8d23d45a0f0598959)
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-W3-r2-canonical-pair-parity-SUMMARY.md` with:
- D1 W3 gate read + branch (FIRES/SKIPPED/DEFERRED_TO_TRACK_B) recorded (PASS/WARN/FAIL)
- D2 (if FIRES) bin/fire_canonical_susie_pairs.sh parameterized additively backwards-compatible (PASS/WARN/FAIL)
- D3 (if FIRES) 4 new region rows in config/regions_curated.csv (PASS/WARN/FAIL)
- D4 (if FIRES) per-region R2 fire produced ≥1 JSON (PASS/WARN/FAIL)
- D5 (if FIRES) merge_r2_into_summary.R aggregator landed (PASS/WARN/FAIL)
- D6 (if FIRES) coloc_summary.tsv merged with new R2 rows; SH2B3 R2 + R1 W2 rows preserved (PASS/WARN/FAIL)
- D7 (if FIRES) D-TA-R3-W3-OUTCOME recorded (PASS/WARN/FAIL)
- D8 If SKIPPED/DEFERRED: D-TA-R3-W3-DEFERRED-ON-W1-OUTCOME recorded with reason (PASS/WARN/FAIL)
- LSF wall-time observed vs projected (~3 hr wall expected if FIRES; 0 if SKIPPED)
- Manuscript md5 invariant preservation (PASS/WARN/FAIL)
- Honest-framing-lock invariant preservation
</output>
