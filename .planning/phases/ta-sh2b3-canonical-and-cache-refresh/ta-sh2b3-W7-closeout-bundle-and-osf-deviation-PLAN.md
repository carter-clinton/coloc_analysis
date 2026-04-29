---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 7
slug: W7-closeout-bundle-and-osf-deviation
type: execute
wave: 7
depends_on: ["W6"]
files_modified:
  - .planning/amendments/osf_deviations.md  # CREATED in Wave 7 (does not yet exist)
  - bundles/track_a_genome_medicine_submission_R2.zip  # rebuilt via renamed bundle script
  - bundles/bundle_manifest.tsv  # SHA-256 manifest update
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv  # md5 invariant whitelist
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - ".planning/amendments/osf_deviations.md exists with cache-invalidation entry per D-TA-Cache-OSF (file did NOT exist pre-Wave-7)"
    - "New submission bundle built via bin/build_id_vs_ref_ld_submission_bundle.sh (renamed builder); ZIP integrity clean"
    - "SHA-256 manifest updated with bundle hash"
    - "Stage 2 md5 invariant verified: only intentionally-rewritten files in curated whitelist have changed md5"
    - "C12 (Stage 2 md5 invariant) + C14 (bundle integrity) + C15 (deviation log) all emit PASS from verification harness"
    - "results_identity_ld/ NOT staged in any phase commit (DEC-2026-04-25-01 invariant)"
    - "Carter optionally appends the cache-invalidation deviation entry to osf.io/az52u closeout PDF (web-UI; in-tree entry is canonical source)"
  artifacts:
    - path: ".planning/amendments/osf_deviations.md"
      provides: "OSF deviation log (NEW file; cache-invalidation entry per D-TA-Cache-OSF)"
      contains: "Cache invalidation"
    - path: "bundles/track_a_genome_medicine_submission_R2.zip"
      provides: "New submission bundle from renamed builder + post-Wave-5 disk numbers"
    - path: "bundles/bundle_manifest.tsv"
      provides: "Updated SHA-256 manifest"
      contains: "track_a_genome_medicine_submission_R2.zip"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv"
      provides: "Curated whitelist of intentionally-rewritten files for Stage 2 md5 invariant verification"
  key_links:
    - from: "bin/build_id_vs_ref_ld_submission_bundle.sh (renamed)"
      to: "bundles/track_a_genome_medicine_submission_R2.zip"
      via: "build script invocation"
      pattern: "build_id_vs_ref_ld_submission_bundle"
    - from: "D-TA-Cache-OSF (CONTEXT.md)"
      to: ".planning/amendments/osf_deviations.md"
      via: "deviation-log entry creation"
      pattern: "Cache invalidation"
---

<objective>
Wave 7 — Phase closeout. Build new submission bundle via the renamed `bin/build_id_vs_ref_ld_submission_bundle.sh` against post-Wave-5 frozen numbers + post-Wave-6 manuscript narrative. Append cache-invalidation deviation entry to `.planning/amendments/osf_deviations.md` (NEW file; per D-TA-Cache-OSF). Verify Stage 2 md5 byte-identical preservation rule across the curated whitelist. Update SHA-256 manifest. Run final phase-wide verification dimension D1–D7 PASS/WARN/FAIL JSON sweep. Carter optionally posts deviation entry to OSF portal.

Purpose: Phase gating-out artifact. Carter takes the new submission bundle to *Genome Medicine* journal portal for resubmission. The deviation-log entry closes audit-V2 §Eval 3.2 + D-TA-Cache-OSF (cache hygiene fix is methodologically a deviation, NOT a new analysis; pre-reg amendment is NOT required per Carter's command-args). The Stage 2 md5 invariant verification ensures no files outside the curated rewrite-whitelist were inadvertently mutated by this phase.

Output: New bundle ZIP at `bundles/track_a_genome_medicine_submission_R2.zip` + bundle_manifest.tsv with SHA-256; osf_deviations.md with cache-invalidation entry; phase-wide D1–D7 JSON sweep.
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
<!-- Wave 6 produced these — Wave 7 reads -->
- bin/build_id_vs_ref_ld_submission_bundle.sh — renamed bundle builder (executable)
- docs/manuscript/id-vs-ref-LD.md — renamed + narrative-updated manuscript
- .planning/amendments/ID-VS-REF-LD-STRATEGY.md — renamed strategy doc
- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md — Wave-5 LIVE blocks updated
- D-TA-Wave6-pivot-free-audit recorded
- All 4 honest-framing-lock anchors content-preserved

<!-- Pre-existing files Wave 7 reads -->
- bin/build_track_a_submission_bundle.sh (pre-rename) — referenced for compute envelope (488 lines per RESEARCH.md)
- 5-engine PDF fallback chain (xelatex → lualatex → pdflatex → tectonic → weasyprint → HTML; per RESEARCH.md)
- Submission bundle commit cacdbfe (frozen reference; NOT modified in this phase)

<!-- D-TA-Cache-OSF deviation-log convention -->
- File: .planning/amendments/osf_deviations.md (does NOT yet exist; Wave 7 creates)
- Entry shape per CONTEXT.md D-TA-Cache-OSF "How to apply": discovery date + root cause + invalidation rationale + before/after numerics + commit pointers + OSF deposit cross-reference

<!-- Stage 2 md5 invariant whitelist (intentionally-rewritten files in this phase) -->
- results/multitrait/coloc_summary.tsv (Wave 5 explicit re-render — Pitfall 3 exemption)
- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Wave 5 LIVE block updates)
- docs/manuscript/id-vs-ref-LD.md (Wave 6 narrative + rename target)
- bin/build_id_vs_ref_ld_submission_bundle.sh (Wave 6 rename target + heredoc sed)
- .planning/amendments/ID-VS-REF-LD-STRATEGY.md (Wave 6 rename target)
- 10 R script comment-headers (Wave 6 reference fix-ups)
- 4 .planning/ forward-facing files (Wave 6 reference fix-ups)
- 5 amendments (Wave 6 cross-refs)

<!-- Out of whitelist (must remain md5 byte-identical) -->
- All other R scripts (logic body)
- All Snakemake .smk files (except finemap.smk if Pitfall 2 patch fired)
- All config/ files (except 7 added in W0; existing files untouched)
- src/snakemake/scripts/run_qtl_coloc.R (069b34f committed; not modified in this phase)
- src/legacy/region_analysis/scripts/run_susie_rss.R (7d54183 committed; not modified in this phase)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Create osf_deviations.md + append cache-invalidation deviation entry (D-TA-Cache-OSF)</name>
  <files>
    .planning/amendments/osf_deviations.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Cache-OSF: OSF treatment of Issue 2 cache invalidation re-fire"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_baseline.tsv (pre-Wave-4 status distribution)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_post_refresh.tsv (post-Wave-4 status distribution)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-WAVE4-OUTCOME-PASS" (must be PASS to fire Wave 7)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C15 row
  </read_first>
  <action>
    Create the file (does NOT exist pre-Wave-7) at `.planning/amendments/osf_deviations.md`:

    ```markdown
    # OSF Deviations Log — id-vs-ref-LD project

    **Project:** Identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci
    **OSF deposits:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) — pre-registration; osf.io/az52u — closeout PDF amendments
    **Purpose:** Single canonical log of methodological deviations from the OSF pre-registration. Cache-hygiene fixes, infrastructure changes, and other non-analytical adjustments are recorded here (NOT as pre-registration amendments).

    ---

    ## Entry 2026-04-{29|30}: Variant-ID matcher cache invalidation re-fire (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4)

    **Discovery date:** 2026-04-28 (audit-V2 §Eval 3.2 review)

    **Root cause:** The intermediate QTL-coloc cache at `results/qtl_coloc/` (1,274 per-attempt JSONs; 1,005 / 1,274 = 78.9 % `too_few_snps` failure rate) was generated BEFORE the variant-ID matcher fixes landed in HEAD:
    - Commit `069b34f` (2026-04-21): `run_qtl_coloc.R` extended to tolerate chr:pos-formatted variant IDs (added candidate-based best-overlap match: rsid / chrpos / variant_id).
    - Commit `7d54183` (2026-04-21): `run_susie_rss.R` LD-panel-rsid override added when LD has rsids and sumstats has chr:pos.

    Pre-fix code rejected ~78.9 % of QTL-coloc attempts owing to harmonized-TSV vs SuSiE-fit variant-ID format mismatch (chr:pos vs rsid). The `too_few_snps` status was a CACHE staleness, not a code bug.

    **Invalidation rationale:** This is a methodological **cache hygiene fix**, NOT a new analysis. The same code (post-`069b34f` + `7d54183`) + same data + same params produces the analysis the OSF pre-registration already covers. Per D-TA-Cache-OSF (locked decision in CONTEXT.md): treat as **deviation-log entry only** — NOT a pre-registration amendment.

    **Before/after numerics (post-Wave-4 cache refresh):**
    | metric | pre-fix cache | post-refresh |
    |---|---|---|
    | total_attempts | 1,274 | {post_total} |
    | too_few_snps | 1,005 (78.9 %) | {post_tfs} ({percent}%) |
    | success | 32 (2.5 %) | {post_success} |
    | no_qtl_cs | 235 | {post_no_cs} |
    | qtl_susie_failed | 2 | {post_failed} |

    **Cache-scope used (D-TA-04 diagnostic):** {QTL_COLOC_ONLY|BOTH_LAYERS|CONSERVATIVE_BOTH} — driven by Wave-0 SuSiE-RSS variant-ID format diagnostic on `results/fine_mapping/susie/*.fit.rds`.

    **Cache backup preservation:** Pre-fix cache moved (NOT deleted) to `results/qtl_coloc.preFix.bak.${TS}` (timestamped per RESEARCH.md Pitfall 5); rollback path preserved on disk. Identical convention applied to `results/fine_mapping/susie/` if SuSiE-RSS layer was in scope.

    **Commit pointers:**
    - Code fixes (already in HEAD): `069b34f`, `7d54183`
    - Cache invalidation + Snakemake re-fire: see Wave 4 atomic commits in phase ta-sh2b3-canonical-and-cache-refresh
    - Aggregator refresh: see Wave 5 atomic commits

    **OSF cross-reference:** Linked to `osf.io/az52u` closeout PDF amendment chain. This deviation entry is the canonical in-tree source. Carter optionally appends a brief abstract of this entry to the osf.io/az52u closeout PDF (web-UI workflow).

    **Manuscript disclosure:** The methodological description of this cache invalidation is integrated into:
    - `docs/manuscript/id-vs-ref-LD.md` Methods §Harmonization-Pipeline Diagnostics (Wave 6 narrative update)
    - `docs/manuscript/id-vs-ref-LD.md` Discussion §Identity-LD Inflation (Wave 6 narrative update; per D-TA-WAVE3-OUTCOME branch)
    - `docs/manuscript/id-vs-ref-LD.md` Limitations bullet 5 (Wave 6 narrative update)

    ---
    ```

    Substitute the actual numerics from `wave4_post_refresh.tsv` and the actual D-TA-04 cache-scope token from CONTEXT.md.

    Atomic commit:
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add .planning/amendments/osf_deviations.md
    git commit -m "docs(ta-sh2b3, W7): create osf_deviations.md + append cache-invalidation deviation entry (D-TA-Cache-OSF)"
    ```
  </action>
  <acceptance_criteria>
    - `[ -f .planning/amendments/osf_deviations.md ]` (file did NOT exist pre-Wave-7).
    - `grep -E "Cache invalidation|2026-04-(28|29|30)" .planning/amendments/osf_deviations.md` returns ≥ 1 hit.
    - `grep "069b34f" .planning/amendments/osf_deviations.md` returns ≥ 1 hit (commit pointer).
    - `grep "7d54183" .planning/amendments/osf_deviations.md` returns ≥ 1 hit (commit pointer).
    - `grep -E "78\.9 ?%" .planning/amendments/osf_deviations.md` returns ≥ 1 hit (baseline failure rate).
    - `grep "deviation-log entry only" .planning/amendments/osf_deviations.md` returns ≥ 1 hit (D-TA-Cache-OSF directive).
    - `grep "osf.io/az52u" .planning/amendments/osf_deviations.md` returns ≥ 1 hit (cross-reference).
    - C15 from `bin/verify_ta_sh2b3_phase.sh --wave 7` emits PASS.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/amendments/osf_deviations.md ] && grep -qE "Cache invalidation" .planning/amendments/osf_deviations.md && grep -q "069b34f" .planning/amendments/osf_deviations.md && grep -q "7d54183" .planning/amendments/osf_deviations.md && grep -qE "78\.9 ?%" .planning/amendments/osf_deviations.md && grep -q "deviation-log entry only" .planning/amendments/osf_deviations.md && grep -q "osf.io/az52u" .planning/amendments/osf_deviations.md && bin/verify_ta_sh2b3_phase.sh --wave 7 2>/dev/null | jq -e 'select(.check=="C15" and .status=="PASS")' > /dev/null && echo PASS</automated>
  </verify>
  <done>
    `.planning/amendments/osf_deviations.md` created with cache-invalidation deviation entry per D-TA-Cache-OSF directive. All required tokens present (commit pointers, baseline failure rate, deviation-log directive, OSF cross-reference). C15 emits PASS. Atomic commit landed. Verifies C15 in VALIDATION.md.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Build new submission bundle (R2) via renamed builder + verify integrity + update SHA-256 manifest</name>
  <files>
    bundles/track_a_genome_medicine_submission_R2.zip
    bundles/bundle_manifest.tsv
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
  </files>
  <read_first>
    - bin/build_id_vs_ref_ld_submission_bundle.sh (Wave 6 renamed builder; verify executable + heredoc sed clean)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Wave-0-foundations" (Snakefile rule-name surface; sanity check)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-RESEARCH.md §"Don't Hand-Roll → 5-engine PDF fallback chain"
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md C12 + C14 rows
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       [ -x bin/build_id_vs_ref_ld_submission_bundle.sh ] || \
         { echo "ABORT: renamed builder not executable"; exit 1; }
       [ -f docs/manuscript/id-vs-ref-LD.md ] || \
         { echo "ABORT: post-rename manuscript missing"; exit 1; }
       [ -f .planning/amendments/ID-VS-REF-LD-STRATEGY.md ] || \
         { echo "ABORT: post-rename strategy doc missing"; exit 1; }

       # Verify Pitfall 6 mitigation: no stale tokens in bundle script
       grep -nE "track_a_pivot|build_track_a_submission_bundle" bin/build_id_vs_ref_ld_submission_bundle.sh && \
         { echo "ABORT: stale tokens in bundle script"; exit 1; }
       ```

    2. **Build the bundle (uses 5-engine PDF fallback chain per RESEARCH.md):**
       ```bash
       export LSF_UNIT_FOR_LIMITS=GB
       cd /rs1/researchers/c/ckclinto/coloc_analysis  # D-TA-01 canonical
       mkdir -p bundles
       BUNDLE_OUT=bundles/track_a_genome_medicine_submission_R2.zip

       # The script may default to a different output path; pass it explicitly or rely on defaults
       bash bin/build_id_vs_ref_ld_submission_bundle.sh 2>&1 | tee logs/wave7_bundle_build_$(date +%Y%m%d_%H%M%S).log

       # Locate the produced bundle (the script may write under bundles/ or other directory; verify)
       ls -lt bundles/*.zip | head -3
       ```

       If the bundle script writes to a different path, locate the latest .zip and rename to `track_a_genome_medicine_submission_R2.zip`:
       ```bash
       LATEST=$(ls -t bundles/*.zip 2>/dev/null | head -1)
       if [ -n "$LATEST" ] && [ "$LATEST" != "bundles/track_a_genome_medicine_submission_R2.zip" ]; then
         mv "$LATEST" bundles/track_a_genome_medicine_submission_R2.zip
       fi
       ```

    3. **Verify bundle integrity (C14):**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       BUNDLE=bundles/track_a_genome_medicine_submission_R2.zip
       unzip -t "$BUNDLE" > logs/wave7_bundle_unzip_test.log 2>&1 && echo "PASS: unzip -t clean" || \
         { echo "FAIL: bundle integrity"; exit 1; }

       # Inspect bundle contents for Pitfall 6 verification (no stale track_a_pivot.md inside)
       unzip -l "$BUNDLE" | grep -E "track_a_pivot|build_track_a_submission_bundle" && \
         { echo "FAIL: bundle contains stale rename tokens"; exit 1; }
       unzip -l "$BUNDLE" | grep "id-vs-ref-LD" && echo "PASS: bundle uses post-rename branding"
       ```

    4. **Update SHA-256 manifest:**
       ```bash
       BUNDLE_HASH=$(sha256sum "$BUNDLE" | cut -d' ' -f1)
       BUNDLE_SIZE=$(stat -c '%s' "$BUNDLE")
       BUNDLE_NENT=$(unzip -l "$BUNDLE" | tail -1 | awk '{print $2}')

       MANIFEST=bundles/bundle_manifest.tsv
       if [ ! -f "$MANIFEST" ]; then
         echo -e "bundle_filename\tsha256\tsize_bytes\tnum_entries\tbuilt_at" > "$MANIFEST"
       fi
       printf "%s\t%s\t%s\t%s\t%s\n" \
         "track_a_genome_medicine_submission_R2.zip" \
         "$BUNDLE_HASH" "$BUNDLE_SIZE" "$BUNDLE_NENT" \
         "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$MANIFEST"
       cat "$MANIFEST"
       ```

    5. **Build the Stage 2 md5 invariant whitelist + verify (C12):**
       ```bash
       MD5_BASE=.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
       echo -e "file_path\twave_modified\trationale" > "$MD5_BASE"
       cat >> "$MD5_BASE" <<EOF
       results/multitrait/coloc_summary.tsv	W5	Pitfall 3 exemption: Wave 5 explicitly merges R2 outputs into canonical summary
       .planning/amendments/TRACK-A-FROZEN-NUMBERS.md	W5	LIVE blocks at L10/L30/L83 updated against post-refresh disk
       docs/manuscript/id-vs-ref-LD.md	W6	rename target (was track_a_pivot.md) + narrative atomic updates
       .planning/amendments/ID-VS-REF-LD-STRATEGY.md	W6	rename target (was TRACK-A-PIVOT.md)
       bin/build_id_vs_ref_ld_submission_bundle.sh	W6	rename target + heredoc sed (Pitfall 6)
       src/R/figures/fig1a_pipeline_schematic.R	W6	comment-header reference fix-up
       src/R/figures/fig1b_locus_panels.R	W6	comment-header reference fix-up
       src/R/figures/fig2_cs_yield.R	W6	comment-header reference fix-up
       src/R/figures/fig3_sh2b3_eur_collapse_forest.R	W6	comment-header reference fix-up
       src/R/figures/fig5_variant_mech_scorecard.R	W6	comment-header reference fix-up
       src/R/figures/fig_h3_ld_overlap_dose_response.R	W6	comment-header reference fix-up
       src/R/figures/fig_s2_paired_fit_structural_inflation.R	W6	comment-header reference fix-up
       src/R/aggregators/aggregate_per_trait_pair_and_hubs.R	W6	comment-header reference fix-up
       src/R/aggregators/aggregate_table1_pleiotropic_loci.R	W6	comment-header reference fix-up
       src/R/aggregators/aggregate_table3_admissible_pairs.R	W6	comment-header reference fix-up
       .planning/STATE.md	W6	forward-facing reference fix-up
       .planning/DECISIONS.md	W6	forward-facing reference fix-up
       .planning/ROADMAP.md	W6	forward-facing reference fix-up
       .planning/PROJECT.md	W6	forward-facing reference fix-up
       .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md	W6	cross-ref update (filename preserved)
       .planning/amendments/AUDIT-REVIEW-2026-04-25.md	W6	cross-ref update
       .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md	W6	cross-ref update
       .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md	W6	cross-ref update
       .planning/amendments/osf_deviations.md	W7	NEW file (cache-invalidation deviation entry)
       .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md	W0-W6	addendum sub-sections (D-TA-04-DIAGNOSTIC, D-TA-OSF-COVERAGE, D-TA-Wave1-PRIMARY-L, D-TA-Wave2-outcomes, D-TA-WAVE3-OUTCOME, D-TA-WAVE4-OUTCOME, D-TA-Wave6-pivot-free-audit)
       EOF
       cat "$MD5_BASE"
       ```

       Verify the whitelist is complete (no unintended file modifications outside whitelist):
       ```bash
       # Compute md5 diff between phase start (commit cacdbfe) and HEAD for tracked files
       FIRST_COMMIT=$(git log --oneline | grep -E "ta-sh2b3" | tail -1 | awk '{print $1}')
       FROZEN_COMMIT=cacdbfe  # frozen submission bundle reference
       git diff --name-only "$FROZEN_COMMIT"..HEAD | sort > /tmp/changed_files_post_phase.txt
       awk -F'\t' 'NR>1 {print $1}' "$MD5_BASE" | sort > /tmp/whitelist.txt

       # Files changed but not in whitelist
       UNWHITELISTED=$(comm -23 /tmp/changed_files_post_phase.txt /tmp/whitelist.txt | grep -v "^results_lsweep_" | grep -v "^logs/" | grep -v "^results/qtl_coloc/" | grep -v "^results/fine_mapping/susie" | grep -v "^results/multitrait/coloc_susie_R2/" | grep -v "^results/multitrait/coloc_manifest_R2.tsv" | grep -v "^results/multitrait/coloc_manifest_merged.tsv" | grep -v "^results/track_a_aggregations/" | grep -v "^figures/" | grep -v "^bundles/" | grep -v "^bin/fire_susie_lsweep.sh" | grep -v "^bin/fire_canonical_susie_pairs.sh" | grep -v "^bin/fire_qtl_coloc_cache_refresh.sh" | grep -v "^bin/verify_ta_sh2b3_phase.sh" | grep -v "^src/python/build_coloc_manifest_r2.py" | grep -v "^config/susie_policy_L" | grep -v "^config/pipeline_lsweep_L" | grep -v "^config/pipeline_canonical_r2_overlay" | grep -v "^.planning/phases/ta-sh2b3-")
       if [ -n "$UNWHITELISTED" ]; then
         echo "WARN: files changed outside whitelist:"
         echo "$UNWHITELISTED"
         # Carter judgment call: are these legitimate? document in SUMMARY.
       else
         echo "PASS: Stage 2 md5 invariant respected (only whitelisted files changed)"
       fi
       ```

    6. **Verify results_identity_ld/ NOT staged anywhere in this phase (DEC-2026-04-25-01 invariant):**
       ```bash
       UNWANTED=$(git diff --cached --name-only 2>/dev/null | grep -c "^results_identity_ld" || echo 0)
       UNWANTED_HISTORY=$(git log --since=2026-04-28 --oneline --diff-filter=A --name-only 2>/dev/null | grep -c "^results_identity_ld" || echo 0)
       [ "$UNWANTED" -eq 0 ] && [ "$UNWANTED_HISTORY" -eq 0 ] || \
         { echo "FAIL: results_identity_ld/ staged or committed"; exit 1; }
       echo "PASS: results_identity_ld/ NOT staged or committed (DEC-2026-04-25-01 preserved)"
       ```

    7. **Run verification harness Wave 7:**
       ```bash
       bin/verify_ta_sh2b3_phase.sh --wave 7
       ```
       C12 + C14 + C15 must all emit PASS.

    8. **Atomic commit:**
       ```bash
       git add bundles/track_a_genome_medicine_submission_R2.zip \
               bundles/bundle_manifest.tsv \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv \
               logs/wave7_bundle_build_*.log
       git commit -m "feat(ta-sh2b3, W7): build R2 submission bundle + SHA-256 manifest + md5 whitelist"
       ```
  </action>
  <acceptance_criteria>
    - `bundles/track_a_genome_medicine_submission_R2.zip` exists.
    - `unzip -t bundles/track_a_genome_medicine_submission_R2.zip` returns exit 0.
    - Bundle ZIP contents do NOT contain pre-rename tokens: `unzip -l bundles/track_a_genome_medicine_submission_R2.zip | grep -cE "track_a_pivot|build_track_a_submission_bundle"` returns 0.
    - Bundle ZIP contents include post-rename branding: `unzip -l bundles/track_a_genome_medicine_submission_R2.zip | grep -c "id-vs-ref-LD"` returns ≥ 1.
    - `bundles/bundle_manifest.tsv` exists with header + ≥ 1 data row.
    - `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` exists with ≥ 25 whitelist rows.
    - `git diff --cached --name-only` shows zero `results_identity_ld/` paths.
    - `git log --since=2026-04-28 --oneline --diff-filter=A --name-only | grep -c "^results_identity_ld"` returns 0.
    - C12 + C14 + C15 from `bin/verify_ta_sh2b3_phase.sh --wave 7` all emit PASS.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f bundles/track_a_genome_medicine_submission_R2.zip ] && unzip -t bundles/track_a_genome_medicine_submission_R2.zip > /dev/null 2>&1 && [ "$(unzip -l bundles/track_a_genome_medicine_submission_R2.zip | grep -cE 'track_a_pivot|build_track_a_submission_bundle')" -eq 0 ] && [ "$(unzip -l bundles/track_a_genome_medicine_submission_R2.zip | grep -c 'id-vs-ref-LD')" -ge 1 ] && [ -f bundles/bundle_manifest.tsv ] && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv ] && [ "$(git diff --cached --name-only 2>/dev/null | grep -c '^results_identity_ld')" -eq 0 ] && bin/verify_ta_sh2b3_phase.sh --wave 7 2>/dev/null | jq -e 'select(.check=="C14" and .status=="PASS")' > /dev/null && echo PASS</automated>
  </verify>
  <done>
    New submission bundle built via renamed builder + integrity verified; SHA-256 manifest updated; Stage 2 md5 invariant whitelist captured; results_identity_ld/ confirmed NOT staged anywhere (DEC-2026-04-25-01 preserved); C12 + C14 + C15 all PASS. Atomic commit landed. Phase ready for Carter to take bundle to Genome Medicine portal for resubmission.
  </done>
</task>

<task type="checkpoint:human-verify" gate="optional">
  <name>Task 3: Carter optionally posts cache-invalidation deviation entry to OSF closeout PDF (osf.io/az52u)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  </files>
  <read_first>
    - .planning/amendments/osf_deviations.md (Task 1 produced)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Cache-OSF" (in-tree entry is canonical; OSF post is optional)
  </read_first>
  <what-built>
    Task 1 created `.planning/amendments/osf_deviations.md` with the cache-invalidation deviation entry per D-TA-Cache-OSF. The in-tree entry IS the canonical source. Carter optionally appends a brief abstract of this entry to the existing osf.io/az52u closeout PDF as an addendum (web-UI workflow, ~15 min). This step is OPTIONAL — the in-tree entry suffices for the OSF deviation-log discipline; the OSF-portal post is a courtesy for OSF reviewers reading the closeout PDF without checking the GitHub repo.
  </what-built>
  <action>
    See <how-to-verify> below — this is a checkpoint:human-verify task. The user (Carter) executes the verification + decision-recording steps; the executor agent presents the outcome and waits for resume-signal.
  </action>
  <how-to-verify>
    1. **(Optional)** Open https://osf.io/az52u in your browser. Append a brief addendum to the closeout PDF amendment chain (web-UI workflow):

       ```
       Cache-invalidation deviation (2026-04-29)

       During audit-V2 review, the QTL-coloc cache at `results/qtl_coloc/` (1,274 attempts; 78.9 % too_few_snps baseline) was identified as pre-dating the variant-ID matcher fixes (commits 069b34f + 7d54183). Cache invalidation + Snakemake re-fire executed. Status distribution post-refresh: too_few_snps {pre} → {post}; success {pre} → {post}.

       Treated as cache hygiene deviation (not pre-registration amendment) per project methodology (in-tree canonical record at .planning/amendments/osf_deviations.md).
       ```

    2. **Append confirmation to CONTEXT.md** (under `<decisions>`) once posted (or document if skipped):

       ```markdown
       ### D-TA-Wave7-osf-post: OSF closeout PDF deviation entry status (Wave 7)

       **Recorded:** {timestamp}

       **Status:** {POSTED | SKIPPED}

       **OSF link:** {URL of the addendum revision on osf.io/az52u, or N/A if SKIPPED}

       **Note:** In-tree canonical source at `.planning/amendments/osf_deviations.md` is sufficient per D-TA-Cache-OSF; OSF closeout PDF post is courtesy.
       ```

    3. **Atomic commit:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
       git commit -m "docs(ta-sh2b3, W7): record D-TA-Wave7-osf-post status (POSTED or SKIPPED)"
       ```

    **Resume signal:** Type `OSF_POSTED` if you posted to osf.io/az52u, or `OSF_SKIPPED` if you decided in-tree entry is sufficient.
  </how-to-verify>
  <acceptance_criteria>
    - `grep "D-TA-Wave7-osf-post:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` returns ≥ 1 hit.
    - `grep -E "Status:.*(POSTED|SKIPPED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` matches.
    - Atomic commit landed.
    - This task is OPTIONAL; SKIPPED is a valid resolution.
  </acceptance_criteria>
  <resume-signal>Type `OSF_POSTED` or `OSF_SKIPPED`</resume-signal>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q "D-TA-Wave7-osf-post:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "Status:.*(POSTED|SKIPPED)" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && echo PASS</automated>
  </verify>
  <done>
    Carter recorded OSF closeout PDF post status (POSTED or SKIPPED) in CONTEXT.md addendum. Atomic commit landed. This is the final wave-7 task; phase is closeable.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Final phase-wide D1-D7 verification sweep + close phase</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
    .planning/STATE.md
    .planning/ROADMAP.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-VALIDATION.md (full file; all C1-C15 rows + Validation Sign-Off checklist)
    - bin/verify_ta_sh2b3_phase.sh (Wave 0 Task 6 produced)
    - .planning/STATE.md (frontmatter shape)
    - .planning/ROADMAP.md §"### Track-A-R2-sh2b3-canonical-and-cache-refresh" (status field update)
  </read_first>
  <action>
    1. **Full phase-wide C1-C15 sweep:**
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       bin/verify_ta_sh2b3_phase.sh > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.jsonl 2> .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.stderr
       FAIL_COUNT=$?
       echo "Final FAIL count: $FAIL_COUNT"
       cat .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.jsonl | jq -s '.' > .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json
       jq '[.[] | {check, status}] | group_by(.status) | map({status: .[0].status, count: length})' \
          .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json
       ```
       Target: 13+ PASS, ≤ 2 WARN, 0 FAIL.

    2. **Update ROADMAP.md status:**
       Use the Edit tool on `.planning/ROADMAP.md` §"### Track-A-R2-sh2b3-canonical-and-cache-refresh" to update the `**Status:**` line (currently "not planned; routed next to `/gsd-discuss-phase") to:
       ```
       **Status**: COMPLETE — closed {YYYY-MM-DD}; new submission bundle at bundles/track_a_genome_medicine_submission_R2.zip; SHA-256 in bundles/bundle_manifest.tsv; cache-invalidation deviation logged at .planning/amendments/osf_deviations.md
       ```

    3. **Update STATE.md frontmatter** (per memory feedback_multi_terminal_staging.md — explicit paths only):
       Update `status:` field with brief one-line phase closure summary; update `last_activity:` with the closure date + brief description.

    4. **Append final phase closeout note to CONTEXT.md:**
       ```markdown
       ### D-TA-Wave7-phase-closure: Phase ta-sh2b3-canonical-and-cache-refresh closed (Wave 7)

       **Recorded:** {timestamp}

       **Final verification: {N} PASS / {K} WARN / {J} FAIL** (target: 13+ PASS, ≤ 2 WARN, 0 FAIL)

       **Verification dimensions D1-D7 PASS/WARN/FAIL:**
       - D1 path + ancestry verification (C1, C2): {PASS|WARN|FAIL}
       - D2 cache-layer diagnostic (C3): {PASS|WARN|FAIL}
       - D3 OSF coverage gate (C4): {PASS|WARN|FAIL}
       - D4 SuSiE-RSS L-sweep convergence (C5): {PASS|WARN|FAIL}
       - D5 canonical-pair coloc.susie (C6, C7): {PASS|WARN|FAIL}
       - D6 Wave-3 outcome branch + Wave-4 cache refresh (C8, C9): {PASS|WARN|FAIL}
       - D7 Wave-5 aggregator refresh + Wave-6 narrative + Wave-7 closeout (C10, C11, C12, C13, C14, C15): {PASS|WARN|FAIL}

       **Phase output:**
       - 9 SH2B3 EUR canonical-pair coloc.susie outputs at `results/multitrait/coloc_susie_R2/`
       - 9 SuSiE-RSS L-sweep fits at `results_lsweep_L{15,20,30}/`
       - Refreshed `results/qtl_coloc/` cache (post 069b34f + 7d54183)
       - Updated TRACK-A-FROZEN-NUMBERS.md LIVE blocks (L10/L30/L83)
       - Renamed manuscript at `docs/manuscript/id-vs-ref-LD.md`; renamed strategy at `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`; renamed bundle builder at `bin/build_id_vs_ref_ld_submission_bundle.sh`
       - New submission bundle at `bundles/track_a_genome_medicine_submission_R2.zip`
       - OSF deviation log at `.planning/amendments/osf_deviations.md`
       ```

    5. **Atomic commit:**
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json \
               .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md \
               .planning/STATE.md \
               .planning/ROADMAP.md
       git commit -m "docs(ta-sh2b3, W7): close phase ta-sh2b3-canonical-and-cache-refresh ({N} PASS / {K} WARN / {J} FAIL)"
       ```
  </action>
  <acceptance_criteria>
    - `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json` exists with valid JSON structure containing all 15 C-row checks.
    - All Wave 0-7 C-row checks return either PASS or documented WARN (no FAIL): `jq '[.[] | select(.status == "FAIL")] | length' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json` returns 0 (or escalation documented in CONTEXT.md).
    - At least 13 of 15 C-rows PASS: `jq '[.[] | select(.status == "PASS")] | length' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json` returns ≥ 13.
    - ROADMAP.md `**Status**:` for this phase reflects COMPLETE.
    - `D-TA-Wave7-phase-closure:` recorded in CONTEXT.md.
    - Atomic commit landed.
  </acceptance_criteria>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json ] && [ "$(jq '[.[] | select(.status == "FAIL")] | length' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json)" -eq 0 ] && [ "$(jq '[.[] | select(.status == "PASS")] | length' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-final-verification.json)" -ge 13 ] && grep -q "D-TA-Wave7-phase-closure:" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md && grep -qE "Status.*COMPLETE" .planning/ROADMAP.md && echo PASS</automated>
  </verify>
  <done>
    Final phase-wide C1-C15 sweep complete with 13+ PASS / 0 FAIL; ROADMAP.md + STATE.md updated to reflect phase closure; D-TA-Wave7-phase-closure recorded in CONTEXT.md. Atomic commit landed. Phase ta-sh2b3-canonical-and-cache-refresh formally closed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pre-phase frozen state (commit cacdbfe) ↔ Post-phase HEAD | Stage 2 md5 invariant: only whitelisted files differ |
| In-tree osf_deviations.md ↔ OSF portal closeout PDF | In-tree entry is canonical; OSF portal post is optional courtesy |
| Bundle ZIP ↔ post-rename file paths | Pitfall 6 mitigation propagates: bundle contents must be post-rename only |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-04 | T (Tampering) | Stage 2 md5 invariant on non-target files | mitigate | Wave 7 Task 2 builds curated whitelist + diffs against frozen commit cacdbfe; out-of-whitelist file changes flagged for Carter |
| T-PROCESS-02 | I (Information disclosure) | results_identity_ld/ accidentally staged | mitigate | Wave 7 Task 2 explicit checks: `git diff --cached --name-only \| grep -c '^results_identity_ld'` returns 0; `git log --since=2026-04-28 --diff-filter=A --name-only \| grep -c '^results_identity_ld'` returns 0 |
| T-PROCESS-01 | T (Tampering) | Bundle ZIP contains stale rename tokens (Pitfall 6 propagation) | mitigate | Wave 7 Task 2 explicit `unzip -l \| grep -cE 'track_a_pivot|build_track_a_submission_bundle'` returns 0 |
| T-PROCESS-04 | I (Information disclosure) | Bundle SHA-256 not recorded | mitigate | Wave 7 Task 2 updates bundles/bundle_manifest.tsv with sha256sum; Wave 7 final verification (C14) checks |
</threat_model>

<verification>
- osf_deviations.md created with cache-invalidation entry (Task 1)
- Submission bundle R2 built + integrity clean + post-rename branding only (Task 2)
- SHA-256 manifest updated (Task 2)
- Stage 2 md5 invariant whitelist captured (Task 2)
- results_identity_ld/ NOT staged or committed (Task 2; DEC-2026-04-25-01 invariant)
- C12 + C14 + C15 all PASS (Task 2)
- Carter optionally posted to osf.io/az52u (Task 3)
- Final phase-wide D1-D7 sweep: 13+ PASS / 0 FAIL (Task 4)
- ROADMAP + STATE updated to reflect closure (Task 4)
- 4 atomic commits landed
</verification>

<verification_criteria>
This plan covers the following C-rows from VALIDATION.md:
- **C12** Stage 2 md5 invariant preserved on non-target files — Task 2
- **C14** Bundle is reproducible and clean — Task 2
- **C15** OSF deviation log entry added — Task 1
- Plus phase-wide C1-C15 final sweep — Task 4
</verification_criteria>

<success_criteria>
- .planning/amendments/osf_deviations.md created with cache-invalidation deviation entry (D-TA-Cache-OSF)
- New submission bundle at bundles/track_a_genome_medicine_submission_R2.zip with integrity clean
- Bundle ZIP contents post-rename branding only (Pitfall 6 propagation verified)
- SHA-256 manifest updated
- Stage 2 md5 invariant whitelist captured + non-target files preserved
- results_identity_ld/ NOT staged or committed (DEC-2026-04-25-01)
- Carter optional OSF closeout PDF post status recorded
- Final phase-wide C1-C15 sweep: 13+ PASS / 0 FAIL
- ROADMAP.md + STATE.md updated to phase COMPLETE
- All commits via explicit paths
</success_criteria>

<output>
After completion, create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-SUMMARY.md` with:
- D1 osf_deviations.md created with all required tokens (PASS/WARN/FAIL)
- D2 submission bundle integrity (PASS/WARN/FAIL via unzip -t + post-rename branding check)
- D3 SHA-256 manifest updated (PASS/WARN/FAIL)
- D4 Stage 2 md5 invariant respected (PASS/WARN/FAIL based on whitelist diff)
- D5 results_identity_ld/ NOT staged (PASS/WARN/FAIL; DEC-2026-04-25-01)
- D6 C1-C15 final sweep status (count of PASS/WARN/FAIL)
- D7 ROADMAP + STATE updated (PASS/WARN/FAIL)

Plus a phase-of-summaries integration: aggregate per-wave SUMMARYs into a single phase narrative for Carter's hand-off to Genome Medicine resubmission. Reference each wave SUMMARY by path. List the new bundle path + SHA-256 prominently.
</output>
