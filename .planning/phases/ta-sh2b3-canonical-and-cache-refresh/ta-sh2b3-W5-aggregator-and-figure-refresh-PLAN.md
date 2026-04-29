---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 5
slug: W5-aggregator-and-figure-refresh
type: execute
wave: 5
depends_on: ["W3", "W4"]
files_modified:
  - results/track_a_aggregations/  # all per-aggregator TSVs refreshed
  - results/multitrait/coloc_summary.tsv  # explicit Wave 5 re-render (md5 invariant exempted in this wave only per RESEARCH.md Pitfall 3)
  - figures/  # Fig S7 + any other refreshed figures
  - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md  # LIVE block updates per Pattern 4
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-PP.H4-THRESHOLD-SWEEP
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "All Wave 5 aggregator outputs have mtime > Wave 4 disk freeze (proves they ran against post-refresh data)"
    - "results/multitrait/coloc_summary.tsv re-rendered to merge Wave 2 R2 outputs into the canonical summary (Pitfall 3 exemption documented in this wave's SUMMARY)"
    - "TRACK-A-FROZEN-NUMBERS.md LIVE blocks at L10 (Stage 2 fine-mapping yield), L30 (H3 dose-response), L83 (pre-bioRxiv placeholder-fill) updated against post-refresh disk"
    - "TRACK-A-FROZEN-NUMBERS.md LIVE blocks at L58 (Paired-fit structural inflation, lines 58-82) and L226 (Negative-control behavior, lines 226-259) BYTE-IDENTICAL pre vs post Wave 5 (md5 captured BEFORE L10/L30/L83 edits, verified AFTER edits)"
    - "Headline numerator decision (D-TA-Wave1-headline) MATERIALIZED at this point if PRIMARY_L convergence outcomes triggered RECOMPUTE branch (else 51/96 preserved with disclosure column added at Wave 6)"
    - "Disk-then-narrative invariant 2 satisfied: Wave 5 freezes all numbers; Wave 6 writes prose against frozen state"
    - "Fig S7 dose-response figure regenerated against post-Wave-4 status distribution"
    - "Table 1 builder, Tier-assignment script, Pathway-disclosure aggregator all refreshed"
    - "Wave 3 outcome branch (D-TA-WAVE3-OUTCOME) RECORDED before Wave 5 freeze lands (frontmatter depends_on: [W3, W4] enforces this in dependency graph)"
  artifacts:
    - path: "results/track_a_aggregations/qtl_coloc_status_distribution.tsv"
      provides: "Updated status distribution (post-refresh too_few_snps + success + no_qtl_cs counts)"
    - path: "results/multitrait/coloc_summary.tsv"
      provides: "Canonical multi-trait coloc summary (re-rendered with Wave 2 R2 outputs merged in)"
      contains: "SH2B3_12q24__EUR__bmi_vs_hypertension"
    - path: ".planning/amendments/TRACK-A-FROZEN-NUMBERS.md"
      provides: "Updated LIVE blocks reflecting post-refresh numerics + Wave 1 headline outcome"
      contains: "Stage 2 fine-mapping yield"
    - path: "figures/fig_h3_ld_overlap_dose_response.{png,pdf}"
      provides: "Refreshed Fig S7 against post-refresh disk numbers"
    - path: "/tmp/L58_block_md5_pre.txt"
      provides: "Pre-edit md5 of L58 LIVE block (lines 58-82) — captured BEFORE L10/L30/L83 edits; verified post-edit byte-identical"
    - path: "/tmp/L226_block_md5_pre.txt"
      provides: "Pre-edit md5 of L226 LIVE block (lines 226-259) — captured BEFORE L10/L30/L83 edits; verified post-edit byte-identical"
  key_links:
    - from: "results/qtl_coloc/*.json (post-Wave-4)"
      to: "src/python/aggregate_qtl_coloc.py output"
      via: "aggregator script reads qtl_coloc cache"
      pattern: "aggregate_qtl_coloc"
    - from: "results/multitrait/coloc_susie_R2/*.json + results/multitrait/coloc_susie/*.json"
      to: "results/multitrait/coloc_summary.tsv (re-rendered)"
      via: "merged manifest aggregation"
      pattern: "merge.*manifests"
    - from: "Pre-edit L58 + L226 LIVE blocks (md5 captured pre-Task-2)"
      to: "Post-edit L58 + L226 LIVE blocks (md5 verified post-Task-2)"
      via: "captured-state md5 comparison (replaces noisy git-diff approach)"
      pattern: "/tmp/L(58|226)_block_md5_pre.txt"
---

<objective>
Wave 5 — Downstream aggregator + figure refresh + frozen-numbers update. Re-run all aggregators against post-Wave-4 disk state. Explicitly merge Wave 2 R2 canonical-pair outputs into the canonical `results/multitrait/coloc_summary.tsv` (with documented Pitfall 3 exemption — Wave 5 is the ONLY wave allowed to mutate this file). Update `TRACK-A-FROZEN-NUMBERS.md` LIVE blocks (L10 + L30 + L83) per Pattern 4 (H2-section markers, NOT sentinel comments). Regenerate Fig S7 dose-response. Build the Wave 6 narrative substrate.

**Frontmatter dependency note (per checker iter 1 WARNING 1):** `depends_on: [W3, W4]` (was `[W4]`). Wave 5 freeze conceptually only requires Wave-4 post-refresh disk + Wave-2 R2 outputs (outcome-agnostic w.r.t. branch); however, listing W3 in `depends_on` makes the intent explicit in the dependency graph and prevents accidental Wave-5-before-Wave-3-recording sequences if a future operator reorders waves. The explicit dependency does NOT change Wave 5's body (still outcome-agnostic at the data level); it only enforces Wave-3-recorded-first in the graph.

Purpose: Disk-then-narrative invariant 2. Wave 5 is the freeze point: numbers land first, narrative writes follow at Wave 6. The audit-V2 reviewer specifically flagged "manuscript pre-committed before evidence" as a methodological issue; this wave is the structural mitigation. The headline numerator decision (D-TA-Wave1-headline) MATERIALIZES here if Wave 1 convergence outcomes triggered the RECOMPUTE branch — Wave 5 produces the recomputed value (e.g., 51 → 54/96 if all 3 newly converge with non-empty CS); Wave 6 then writes prose against that frozen value.

Output: Refreshed aggregator TSVs + figures + canonical multi-trait coloc summary + updated TRACK-A-FROZEN-NUMBERS.md LIVE blocks. All under post-Wave-4 + post-Wave-2 disk state.
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
<!-- Wave 4 produced this — Wave 5 reads -->
- results/qtl_coloc/*.json — refreshed cache (post 069b34f + 7d54183)
- D-TA-WAVE4-OUTCOME: PASS (CLEARED gate to proceed)
- D-TA-Wave2-outcomes (Wave 2 PP.H4 per pair)
- D-TA-Wave1-PRIMARY-L + D-TA-Wave1-headline (drives whether 51/96 recomputes or stays unchanged with disclosure column)
- D-TA-WAVE3-OUTCOME-{BRANCH} (recorded; informs Wave 6 narrative but Wave 5 only updates frozen-numbers per outcome-agnostic data; explicit depends_on [W3, W4] enforces Wave-3-recorded-first in the graph per checker iter 1 WARNING 1)

<!-- Existing aggregator scripts -->
- src/python/aggregate_qtl_coloc.py — Python aggregator producing results/track_a_aggregations/qtl_coloc_status_distribution.tsv (and pph4_threshold_sweep.tsv per REQ-PP.H4-THRESHOLD-SWEEP)
- src/python/aggregate_pathway_results.py — pathway disclosure aggregator
- src/python/aggregate_coloc_manifest_errors.py — error-class aggregator
- src/R/aggregators/aggregate_table1_pleiotropic_loci.R — Table 1 builder
- src/R/aggregators/aggregate_table3_admissible_pairs.R — Table 3 builder (Tier-assignment)
- src/R/aggregators/aggregate_per_trait_pair_and_hubs.R — per-trait-pair + hubs aggregator
- src/R/figures/fig_h3_ld_overlap_dose_response.R — Fig S7 builder

<!-- Pattern 4 — TRACK-A-FROZEN-NUMBERS.md LIVE blocks -->
LIVE blocks marked by H2 headers ending in `— LIVE`. Block boundaries verified 2026-04-29 against current TRACK-A-FROZEN-NUMBERS.md:
- L10:  ## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE  [UPDATE if D-TA-Wave1-headline triggered RECOMPUTE; block spans L10-L29]
- L30:  ## H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE  [UPDATE with post-refresh success count from Wave 4; block spans L30-L57]
- L58:  ## Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE  [UNCHANGED this phase; block spans L58-L82]
- L83:  ## Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE  [UPDATE 28 attempted → updated count + 9 new SH2B3 EUR pairs; block spans L83-L147]
- L226: ## Negative-control behavior (post-t9j HLA reclassification 2026-04-26) — LIVE  [UNCHANGED this phase; block spans L226-L259]

<!-- Pitfall 3 exemption -->
results/multitrait/coloc_summary.tsv md5 IS allowed to change in Wave 5 (this is the ONLY wave with explicit exemption); document the exemption in Wave 5 SUMMARY

<!-- Captured-state verification (per checker iter 1 WARNING 2) -->
The original draft used a `git diff HEAD~1` inspection to verify L58 + L226 unchanged, which is noisy when 3 OTHER blocks change in the same commit. Replaced with: capture md5 of L58 + L226 blocks BEFORE the L10/L30/L83 edits (Task 2 step 0), then verify byte-identical AFTER edits. This makes the verification deterministic and decoupled from git-diff noise.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Re-run all aggregators + merge R2 coloc.susie outputs into canonical summary</name>
  <files>
    results/track_a_aggregations/qtl_coloc_status_distribution.tsv
    results/track_a_aggregations/pph4_threshold_sweep.tsv
    results/track_a_aggregations/table1_pleiotropic_loci.tsv
    results/track_a_aggregations/table3_admissible_pairs.tsv
    results/track_a_aggregations/per_trait_pair_and_hubs.tsv
    results/track_a_aggregations/pathway_disclosure.tsv
    results/track_a_aggregations/coloc_manifest_errors.tsv
    results/multitrait/coloc_summary.tsv
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-WAVE4-OUTCOME" (must show PASS for this wave to fire)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-WAVE3-OUTCOME-" (must be RECORDED — frontmatter depends_on enforces but plan double-checks)
    - src/python/aggregate_qtl_coloc.py (full file; understand the schema produced)
    - src/R/aggregators/aggregate_table1_pleiotropic_loci.R (signature + dependencies)
    - src/R/aggregators/aggregate_table3_admissible_pairs.R
    - src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
    - src/snakemake/rules/multitrait.smk §rule summarize_coloc_results (line 151 per RESEARCH.md; understand the canonical summary build mechanism)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pitfall 3" (Wave 5 exemption documented here; the merge-and-rerender is intentional)
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks (verify both W3 outcome RECORDED and W4 PASS — per frontmatter depends_on [W3, W4]):**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       grep -qE "Wave 5 gate:.*CLEARED" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md || \
         { echo "ABORT: Wave 5 gate not CLEARED. Wave 4 PASS not recorded."; exit 1; }
       # Also enforce Wave 3 outcome RECORDED (per frontmatter depends_on W3 — checker iter 1 WARNING 1)
       grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" \
            .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md || \
         { echo "ABORT: D-TA-WAVE3-OUTCOME not recorded. Wave 5 freeze cannot land before Wave 3 records branch."; exit 1; }
       ```

    2. **Capture pre-Wave-5 mtimes for the canonical summary file (Pitfall 3 exemption tracking):**
       ```bash
       PRE_W5_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       echo "Pre-Wave-5 md5(coloc_summary.tsv) = $PRE_W5_MD5"
       ```

    3. **Re-run Python aggregators (against post-Wave-4 disk):**
       ```bash
       PYR=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/python3
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       mkdir -p results/track_a_aggregations
       $PYR src/python/aggregate_qtl_coloc.py
       $PYR src/python/aggregate_pathway_results.py
       $PYR src/python/aggregate_coloc_manifest_errors.py
       ls -lt results/track_a_aggregations/*.tsv | head -10
       ```

    4. **Merge Wave 2 R2 outputs into canonical multi-trait summary (Pitfall 3 exemption — DOCUMENTED):**
       The summarize_coloc_results rule (multitrait.smk line 151) reads coloc_manifest.tsv and builds coloc_summary.tsv from per-pair JSONs in results/multitrait/coloc_susie/. Wave 2 wrote 9 R2 pairs to a parallel namespace coloc_susie_R2/. Wave 5 must merge.

       Build a merged manifest + re-render the canonical summary. Use whatever pattern matches the schema (probably append the R2 manifest rows + run summarize_coloc_results, or do an explicit Python merge):
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/python3 - <<'PY'
       import pandas as pd
       from pathlib import Path

       repo = Path("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis")
       canon_manifest = repo / "results/multitrait/coloc_manifest.tsv"
       r2_manifest = repo / "results/multitrait/coloc_manifest_R2.tsv"
       merged_manifest = repo / "results/multitrait/coloc_manifest_merged.tsv"

       canon = pd.read_csv(canon_manifest, sep="\t")
       r2 = pd.read_csv(r2_manifest, sep="\t")
       # Avoid duplicate pair_ids (asthma_vs_t2d already in canon)
       merged = pd.concat([canon, r2[~r2["pair_id"].isin(canon["pair_id"])]], ignore_index=True)
       merged.to_csv(merged_manifest, sep="\t", index=False)
       print(f"Merged manifest: {len(canon)} canon + {len(r2)} R2 - dups → {len(merged)} rows")
       PY
       ```

       Then build coloc_summary.tsv from per-pair JSONs in BOTH directories:
       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS'
       library(jsonlite); library(data.table)
       # Read both per-pair JSON sets
       canon_jsons <- list.files("results/multitrait/coloc_susie", pattern = "\\.json$", full.names = TRUE)
       r2_jsons    <- list.files("results/multitrait/coloc_susie_R2", pattern = "\\.json$", full.names = TRUE)
       all_jsons <- c(canon_jsons, r2_jsons)

       rows <- list()
       for (f in all_jsons) {
         j <- jsonlite::fromJSON(f, simplifyVector = TRUE)
         pair_id <- sub("\\.json$", "", basename(f))
         s <- j$summary
         rows[[length(rows) + 1L]] <- data.table(
           pair_id = pair_id,
           PP.H0.abf = s[["PP.H0.abf"]] %||% NA_real_,
           PP.H1.abf = s[["PP.H1.abf"]] %||% NA_real_,
           PP.H2.abf = s[["PP.H2.abf"]] %||% NA_real_,
           PP.H3.abf = s[["PP.H3.abf"]] %||% NA_real_,
           PP.H4.abf = s[["PP.H4.abf"]] %||% NA_real_
         )
       }
       df <- rbindlist(rows, fill = TRUE)
       # De-dup: prefer R2 outputs over canon if pair_id collides (only asthma_vs_t2d possible)
       df <- df[, .SD[.N], by = pair_id]  # keep last (R2 since concat)
       fwrite(df, "results/multitrait/coloc_summary.tsv", sep = "\t")
       cat(sprintf("Wrote %d rows to results/multitrait/coloc_summary.tsv\n", nrow(df)))
       RS
       ```
       (If `%||%` not available, use `if (is.null(x)) NA_real_ else x`.)

       Verify canonical summary now contains the 9 SH2B3 EUR R2 pairs:
       ```bash
       grep -c "SH2B3_12q24__EUR__" results/multitrait/coloc_summary.tsv
       # Expected: 1 (existing asthma_vs_t2d) + 9 (R2) = 10 rows total under SH2B3_12q24__EUR
       ```

    5. **Re-run R aggregators (Table 1, Table 3, per-trait-pair):**
       ```bash
       RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       $RSCRIPT src/R/aggregators/aggregate_table1_pleiotropic_loci.R
       $RSCRIPT src/R/aggregators/aggregate_table3_admissible_pairs.R
       $RSCRIPT src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
       ls -lt results/track_a_aggregations/*.tsv | head -10
       ```

    6. **Verify Wave 5 mtime invariant (C10 partial):**
       ```bash
       NEWEST_QTL=$(stat -c '%Y' results/qtl_coloc/*.json | sort -n | tail -1)
       OLDEST_AGG=$(stat -c '%Y' results/track_a_aggregations/*.tsv | sort -n | head -1)
       echo "newest qtl_coloc JSON: $NEWEST_QTL ($(date -d @$NEWEST_QTL '+%Y-%m-%d %H:%M:%S'))"
       echo "oldest aggregator TSV: $OLDEST_AGG ($(date -d @$OLDEST_AGG '+%Y-%m-%d %H:%M:%S'))"
       [ "$OLDEST_AGG" -ge "$NEWEST_QTL" ] && echo "PASS: aggregators refreshed post-Wave-4" || echo "FAIL: aggregators stale"
       ```

    7. **Atomic commit (Pitfall 3 exemption — coloc_summary.tsv intentional re-render):**
       ```bash
       POST_W5_MD5=$(md5sum results/multitrait/coloc_summary.tsv | cut -d' ' -f1)
       git add results/track_a_aggregations/*.tsv \
               results/multitrait/coloc_summary.tsv \
               results/multitrait/coloc_manifest_merged.tsv
       git commit -m "feat(ta-sh2b3, W5): refresh aggregators + merge R2 outputs into coloc_summary.tsv (Pitfall 3 exemption — Wave 5 only)"
       echo "coloc_summary.tsv md5: $PRE_W5_MD5 → $POST_W5_MD5 (intentional)"
       ```
  </action>
  <acceptance_criteria>
    - All Wave 5 aggregator TSVs in `results/track_a_aggregations/` exist post-run.
    - `results/multitrait/coloc_summary.tsv` contains all 9 SH2B3 EUR R2 pairs: `grep -c "^SH2B3_12q24__EUR__" results/multitrait/coloc_summary.tsv` returns ≥ 10 (1 existing asthma_vs_t2d + 9 new R2 pairs).
    - All aggregator TSV mtimes > newest qtl_coloc/*.json mtime: `[ "$(stat -c '%Y' results/track_a_aggregations/*.tsv | sort -n | head -1)" -ge "$(stat -c '%Y' results/qtl_coloc/*.json | sort -n | tail -1)" ]` returns 0.
    - `results/multitrait/coloc_manifest_merged.tsv` exists with at least 28 + 9 = 37 rows (or more if Stage 2 had grown beyond 28).
    - Wave 3 outcome RECORDED (frontmatter depends_on W3 enforced): `grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns 0.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f results/track_a_aggregations/qtl_coloc_status_distribution.tsv ] && [ -f results/multitrait/coloc_summary.tsv ] && [ "$(grep -c 'SH2B3_12q24__EUR__' results/multitrait/coloc_summary.tsv)" -ge 10 ] && [ -f results/multitrait/coloc_manifest_merged.tsv ] && [ "$(stat -c '%Y' results/track_a_aggregations/qtl_coloc_status_distribution.tsv)" -ge "$(stat -c '%Y' results/qtl_coloc/*.json | sort -n | tail -1)" ] && grep -qE "D-TA-WAVE3-OUTCOME-(BRANCH_A_COLLAPSE|BRANCH_B_PARTIAL|BRANCH_C_SURVIVE)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    All aggregators re-run against post-Wave-4 disk; canonical multi-trait coloc summary re-rendered to merge Wave 2 R2 outputs (Pitfall 3 exemption documented in commit message + this wave's SUMMARY). Aggregator mtimes prove they ran post-Wave-4. Wave 3 outcome confirmed recorded (frontmatter depends_on W3 enforced). Atomic commit landed. Verifies C10 (partial) in VALIDATION.md.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Regenerate Fig S7 + update TRACK-A-FROZEN-NUMBERS.md LIVE blocks (with captured-state pre-edit md5 for L58 + L226)</name>
  <files>
    figures/fig_h3_ld_overlap_dose_response.png
    figures/fig_h3_ld_overlap_dose_response.pdf
    .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    /tmp/L58_block_md5_pre.txt
    /tmp/L226_block_md5_pre.txt
  </files>
  <read_first>
    - src/R/figures/fig_h3_ld_overlap_dose_response.R (Fig S7 builder)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (full file; understand H2-section LIVE-block structure per Pattern 4)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave1-headline" (drives whether L10 LIVE block recomputes or just adds disclosure)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Pattern 4: LIVE-block update in TRACK-A-FROZEN-NUMBERS.md"
  </read_first>
  <action>
    **Step 0: Capture pre-edit md5 of L58 + L226 LIVE blocks BEFORE any edits (per checker iter 1 WARNING 2).**

    The L58 LIVE block ("Paired-fit structural inflation") spans lines 58-82 (verified 2026-04-29 against current TRACK-A-FROZEN-NUMBERS.md; ends at line 82, with the next H2 header at L83 "Pre-bioRxiv placeholder-fill"). The L226 LIVE block ("Negative-control behavior") spans lines 226-259 (ends at line 259, with the next H2 header at L260 "QTL coloc scope"). Both blocks must be byte-identical pre vs post Wave 5.

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    # Capture pre-edit md5 of the L58 LIVE block (lines 58-82)
    awk 'NR>=58 && NR<=82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum > /tmp/L58_block_md5_pre.txt
    cat /tmp/L58_block_md5_pre.txt
    # Capture pre-edit md5 of the L226 LIVE block (lines 226-259)
    awk 'NR>=226 && NR<=259' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum > /tmp/L226_block_md5_pre.txt
    cat /tmp/L226_block_md5_pre.txt
    ```

    Sanity-check the line ranges by spot-printing the first + last line of each block:
    ```bash
    echo "L58 first line: $(awk 'NR==58' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)"
    echo "L82 last line:  $(awk 'NR==82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)"
    echo "L226 first line: $(awk 'NR==226' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)"
    echo "L259 last line:  $(awk 'NR==259' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)"
    # Expected:
    #   L58 starts with "## Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE"
    #   L82 is the last line before L83 "## Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE"
    #   L226 starts with "## Negative-control behavior (post-t9j HLA reclassification 2026-04-26) — LIVE"
    #   L259 is the last line before L260 "## QTL coloc scope (per-ID JSON tally across 1,274 attempted)"
    ```

    If line ranges have drifted (any executor running this plan after future TRACK-A-FROZEN-NUMBERS.md edits), the executor MUST re-run `grep -nE "^## "` to find the actual H2 boundaries and update the awk ranges before capturing md5. The principle is: "block ends at the line before the NEXT H2 header"; line numbers may shift but block boundaries are content-defined.

    **Step 1: Regenerate Fig S7:**
    ```bash
    RSCRIPT=/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    $RSCRIPT src/R/figures/fig_h3_ld_overlap_dose_response.R
    ls -lt figures/fig_h3_ld_overlap*
    ```

    **Step 2: Update TRACK-A-FROZEN-NUMBERS.md LIVE block at L10 (Stage 2 fine-mapping yield):**
    Read the D-TA-Wave1-headline outcome from CONTEXT.md to determine whether to RECOMPUTE numerator or PRESERVE-WITH-DISCLOSURE:
    ```bash
    NEW_CONVERGED=$(grep -A 5 "Newly converged count" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md | grep -oE '[0-9]+' | head -1)
    echo "Newly converged at PRIMARY_L: $NEW_CONVERGED of 3"
    ```

    Use the Edit tool (NOT sed; whitespace-fragile per RESEARCH.md Pattern 4) to update the L10 LIVE block. The block starts with `## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE` and ends at the next `## ` H2 header (or end of file). Replace the body in-place.

    Branch:
    - If NEW_CONVERGED == 3 (all 3 SH2B3 EUR newly converge with non-empty CS) → RECOMPUTE: 51/96 → 54/96 (or whatever the recomputed value is per Wave 1 + Wave 2 outcomes)
    - If NEW_CONVERGED < 3 → PRESERVE 51/96 + add disclosure note: "3 of 5 SH2B3 EUR per-trait fits at L=10 non-converged; sweep at L ∈ {15, 20, 30} converged X of 3 at PRIMARY_L; non-converged disclosed as a column in Fig 3 (Wave 6)."

    Either way, the LIVE block must reflect:
    - Updated Stage 2 numerator/denominator
    - Reference to D-TA-Wave1-PRIMARY-L outcome
    - Reference to Wave 4 cache refresh outcome (e.g., "post-cache-refresh too_few_snps = X / 1,274; success = Y / 1,274 (was 32 baseline)")

    **Step 3: Update L30 LIVE block (H3 LD-reference-quality dose-response):**
    Read the post-refresh status counts from `results/track_a_aggregations/qtl_coloc_status_distribution.tsv` and update the L30 block to reflect the new "success" count (was 32; now whatever the post-refresh value is per Wave 4 PASS criterion).

    Use Edit tool to update the body of `## H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE`. Reference Fig S7 regeneration date.

    **Step 4: Update L83 LIVE block (Pre-bioRxiv placeholder-fill):**
    The current L83 block reports "28 attempted" Stage 2 trait-pairs. Wave 2 added 9 new SH2B3 EUR pairs; the new count is 37 (or whatever the merged manifest shows). The block also needs updating to surface the 9 new SH2B3 EUR pairs' PP.H4 values inline.

    Use Edit tool to update the body of `## Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE`. Reference Wave 2 outputs at `results/multitrait/coloc_susie_R2/`.

    **Step 5: Verify other LIVE blocks (L58 + L226) are UNCHANGED via captured-state md5 comparison (per checker iter 1 WARNING 2):**

    The original draft used `git diff HEAD~1` to inspect L58 + L226 unchanged, which is noisy when 3 OTHER blocks (L10/L30/L83) change in the same commit. The captured-state approach is deterministic:

    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    POST_L58=$(awk 'NR>=58 && NR<=82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum)
    PRE_L58=$(cat /tmp/L58_block_md5_pre.txt)
    if [ "$POST_L58" != "$PRE_L58" ]; then
      echo "FAIL: L58 LIVE block (Paired-fit structural inflation) md5 changed"
      echo "  pre:  $PRE_L58"
      echo "  post: $POST_L58"
      diff <(awk 'NR>=58 && NR<=82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md) \
           <(git show HEAD:.planning/amendments/TRACK-A-FROZEN-NUMBERS.md | awk 'NR>=58 && NR<=82')
      exit 1
    fi

    POST_L226=$(awk 'NR>=226 && NR<=259' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum)
    PRE_L226=$(cat /tmp/L226_block_md5_pre.txt)
    if [ "$POST_L226" != "$PRE_L226" ]; then
      echo "FAIL: L226 LIVE block (Negative-control behavior) md5 changed"
      echo "  pre:  $PRE_L226"
      echo "  post: $POST_L226"
      diff <(awk 'NR>=226 && NR<=259' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md) \
           <(git show HEAD:.planning/amendments/TRACK-A-FROZEN-NUMBERS.md | awk 'NR>=226 && NR<=259')
      exit 1
    fi
    echo "PASS: L58 + L226 LIVE blocks byte-identical (captured-state verification)"
    ```

    NOTE: If L10/L30/L83 edits caused line numbers to shift (e.g., L83 block grew/shrank), the awk ranges for L226 must be re-derived against the post-edit file. The principle is content-defined: "block N starts at H2 header N, ends at the line before H2 header N+1". If line drift occurred, the executor uses `grep -n "^## Negative-control behavior"` to find the new start line, and `grep -n "^## QTL coloc scope"` to find the new end (next H2). The pre-edit md5 captures the BLOCK CONTENT as a byte string, independent of where in the file it lives, so the post-edit recomputation just needs the new line range.

    Under the W5-defined edits (Pattern 4 in-place body replacements; H2 headers and number-of-LIVE-blocks invariant), L10/L30/L83 blocks change in CONTENT but the L58 and L226 line ranges should be unchanged because no block boundaries shift. If any of the 3 edited blocks added or removed lines, the L226 check should be:

    ```bash
    # Auto-derive new L226 range based on H2 headers in post-edit file
    L226_NEW_START=$(grep -nE "^## Negative-control behavior" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | head -1 | cut -d: -f1)
    L226_NEW_END=$(awk -v s="$L226_NEW_START" 'NR>s && /^## / { print NR-1; exit }' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md)
    POST_L226_AUTO=$(awk -v s="$L226_NEW_START" -v e="$L226_NEW_END" 'NR>=s && NR<=e' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum)
    [ "$POST_L226_AUTO" = "$PRE_L226" ] || { echo "FAIL: L226 block content drifted after auto-rerange"; exit 1; }
    ```

    **Step 6: Run verification harness for Wave 5 (C10, C11):**
    ```bash
    bin/verify_ta_sh2b3_phase.sh --wave 5
    ```
    C10 (aggregator mtimes) + C11 (LIVE block exists) must emit PASS.

    **Step 7: Atomic commit:**
    ```bash
    git add figures/fig_h3_ld_overlap_dose_response.png \
            figures/fig_h3_ld_overlap_dose_response.pdf \
            .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
    git commit -m "feat(ta-sh2b3, W5): regenerate Fig S7 + update TRACK-A-FROZEN-NUMBERS LIVE blocks (L10 + L30 + L83); L58 + L226 byte-identical (md5 captured-state)"
    ```
  </action>
  <acceptance_criteria>
    - `figures/fig_h3_ld_overlap_dose_response.{png,pdf}` exist with mtimes post-Wave-4.
    - L10 LIVE block in TRACK-A-FROZEN-NUMBERS.md mentions either the recomputed numerator (e.g., "54/96") OR explicit disclosure: `grep -A 30 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -E "(/96|disclosure|non-converged|Wave-1)"` returns ≥ 1 hit.
    - L30 LIVE block reflects post-refresh `success` count: `grep -A 30 "H3 LD-reference-quality dose-response" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -E "/1,?274|too_few_snps|success"` returns ≥ 1 hit.
    - L83 LIVE block mentions the 9 SH2B3 EUR R2 pairs: `grep -A 50 "Pre-bioRxiv placeholder-fill" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -E "SH2B3.*EUR|9 new|coloc_susie_R2"` returns ≥ 1 hit.
    - **L58 LIVE block byte-identical (captured-state md5 verification per checker iter 1 WARNING 2):**
      ```
      [ "$(awk 'NR>=58 && NR<=82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum)" = "$(cat /tmp/L58_block_md5_pre.txt)" ] || exit 1
      ```
    - **L226 LIVE block byte-identical (captured-state md5 verification per checker iter 1 WARNING 2):**
      ```
      [ "$(awk 'NR>=226 && NR<=259' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum)" = "$(cat /tmp/L226_block_md5_pre.txt)" ] || exit 1
      ```
      (If line drift occurred during L10/L30/L83 edits — e.g., block 83 grew — the executor uses the auto-rerange variant in Action Step 5 to re-derive the new line range based on H2 header positions. The pre-edit md5 captures block CONTENT; only the lookup range needs to track post-edit line numbers.)
    - C10 + C11 from verification harness emit PASS.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f figures/fig_h3_ld_overlap_dose_response.png ] && [ -f figures/fig_h3_ld_overlap_dose_response.pdf ] && grep -A 30 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -qE "(/96|disclosure|non-converged|Wave-1)" && grep -A 30 "H3 LD-reference-quality dose-response" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -qE "(/1,?274|too_few_snps|success)" && grep -A 50 "Pre-bioRxiv placeholder-fill" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | grep -qE "(SH2B3.*EUR|9 new|coloc_susie_R2)" && [ -f /tmp/L58_block_md5_pre.txt ] && [ -f /tmp/L226_block_md5_pre.txt ] && L58_NOW=$(awk 'NR>=58 && NR<=82' .planning/amendments/TRACK-A-FROZEN-NUMBERS.md | md5sum) && L58_PRE=$(cat /tmp/L58_block_md5_pre.txt) && [ "$L58_NOW" = "$L58_PRE" ] && echo PASS</automated>
  </verify>
  <done>
    Fig S7 regenerated + 3 LIVE blocks (L10/L30/L83) updated against post-refresh disk. L58 + L226 LIVE blocks byte-identical (captured-state md5 verification per checker iter 1 WARNING 2; replaces noisy `git diff HEAD~1` approach). Captured md5 baselines at /tmp/L58_block_md5_pre.txt and /tmp/L226_block_md5_pre.txt. Wave 5 disk-freeze complete; Wave 6 narrative writes can now proceed against frozen numbers. Verifies C10 + C11 in VALIDATION.md.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Wave 4 refreshed disk ↔ Wave 5 aggregator inputs | All aggregators must read the refreshed `results/qtl_coloc/` (post-Wave-4); mtime check verifies |
| Wave 2 R2 outputs ↔ canonical coloc_summary.tsv | Wave 5 explicitly merges (Pitfall 3 exemption); the merge is the disk-then-narrative gate |
| TRACK-A-FROZEN-NUMBERS LIVE blocks ↔ Wave 6 narrative | LIVE blocks are the source of truth for manuscript text; Wave 5 freezes; Wave 6 reads |
| Pre-edit L58 + L226 block md5 ↔ post-edit L58 + L226 block md5 | Captured-state verification (replaces noisy `git diff` approach per checker iter 1 WARNING 2) |
| Wave 3 outcome RECORDED ↔ Wave 5 freeze lands | Frontmatter `depends_on: [W3, W4]` enforces Wave-3-recorded-first in dependency graph (per checker iter 1 WARNING 1) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-04 | T (Tampering) | results/multitrait/coloc_summary.tsv md5 invariant | mitigate (with documented exemption) | Wave 5 Task 1 captures pre/post md5; documents the exemption in commit message + SUMMARY; Wave 7 verification has explicit whitelist for this file |
| T-PROCESS-04 | T (Tampering) | TRACK-A-FROZEN-NUMBERS.md L58 + L226 LIVE blocks (out of scope) | mitigate | Wave 5 Task 2 step 0: capture pre-edit md5 of L58 (lines 58-82) + L226 (lines 226-259) blocks BEFORE the L10/L30/L83 edits; acceptance criterion verifies byte-identical post-edit (per checker iter 1 WARNING 2 — replaces noisy `git diff` approach) |
| T-PROCESS-03 | T (Tampering) | Disk-then-narrative invariant 2 | mitigate | Wave 5 freezes ALL numbers; Wave 6 narrative tasks read frozen state; no narrative writes in Wave 5 |
| T-PROCESS-05 | T (Tampering) | Wave-5-before-Wave-3-recording dependency-graph hole | mitigate | Frontmatter `depends_on: [W3, W4]` (was `[W4]` per checker iter 1 WARNING 1); Task 1 step 1 explicit grep -qE for D-TA-WAVE3-OUTCOME-* before any Wave 5 work |
</threat_model>

<verification>
- All aggregator TSVs refreshed (mtime > Wave 4 newest qtl_coloc JSON)
- coloc_summary.tsv contains 9 SH2B3 EUR R2 pairs
- 3 LIVE blocks updated (L10 + L30 + L83) in TRACK-A-FROZEN-NUMBERS.md
- 2 LIVE blocks byte-identical (L58 + L226) per captured-state md5 verification
- Fig S7 regenerated
- Wave 3 outcome recording confirmed before any Wave 5 work
- C10 + C11 PASS from verification harness
- 2 atomic commits landed
- Pitfall 3 exemption documented (intentional coloc_summary.tsv md5 change)
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C10** Wave-5 aggregator outputs refreshed — Task 1 + Task 2
- **C11** TRACK-A-FROZEN-NUMBERS LIVE block updated — Task 2
</verification_criteria>

<success_criteria>
- All Wave 5 aggregator outputs refreshed against post-Wave-4 disk
- coloc_summary.tsv re-rendered to merge Wave 2 R2 outputs (Pitfall 3 exemption)
- TRACK-A-FROZEN-NUMBERS LIVE blocks at L10, L30, L83 updated
- L58 + L226 LIVE blocks byte-identical (captured-state md5 per checker iter 1 WARNING 2)
- Wave 3 outcome RECORDED before Wave 5 freeze (frontmatter depends_on [W3, W4] per checker iter 1 WARNING 1)
- Fig S7 regenerated
- C10 + C11 PASS
- All commits via explicit paths
- Wave 6 narrative substrate complete (frozen numbers in place)
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W5-aggregator-and-figure-refresh-SUMMARY.md` with:
- D1 aggregator refresh evidence (mtime checks)
- D2 coloc_summary.tsv re-render evidence (md5 baseline → updated)
- D3 Pitfall 3 exemption documentation (which file, which wave, rationale)
- D4 LIVE block update evidence (which 3 blocks, what changed)
- D5 LIVE block preservation evidence (L58 + L226 captured-state md5; pre vs post comparison)
- D6 Fig S7 regeneration evidence
- D7 frozen-number summary (final post-refresh values for too_few_snps, success, no_qtl_cs)
- Wave 6 GO status (must be GO with all numbers frozen for narrative tasks to fire)
- Cross-reference to checker iter 1 WARNINGs 1 + 2 mitigations
</output>
</output>
