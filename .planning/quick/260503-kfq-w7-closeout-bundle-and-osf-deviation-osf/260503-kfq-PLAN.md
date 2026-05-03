---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: W7-quick-260503-kfq
slug: w7-closeout-bundle-and-osf-deviation-osf
type: execute
wave: 7
depends_on:
  - W6-260503-1e1  # Wave-1 headline PRESERVE-WITH-DISCLOSURE materialization (commit c211824)
  - W6-260502-tjn  # Wave-3 BRANCH_C SURVIVE materialization
  - W6-260502-1c1  # W6 narrative narrowed (cache-staleness reframe)
  - W6-260502-lsk  # W6 mechanical rename (track_a_pivot → id-vs-ref-LD; bundle script rename)
  - W4.5-A-260501-r1q  # Wave-4 cache-staleness refutation continuation
files_modified:
  - .planning/amendments/osf_deviations.md  # CREATED (Task 1; 10-entry consolidated deviation log)
  - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip  # GENERATED (Task 2; bundle script's hardcoded output)
  - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv  # CREATED (Task 2; SHA-256 manifest)
  - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv  # CREATED (Task 3; whitelist for Stage 2 invariant)
  - .planning/STATE.md  # UPDATED (Task 4; body line 67 only — Track-B-encoded fields preserved)
  - logs/wave7_bundle_build_*.log  # GENERATED (Task 2; script stdout/stderr capture)
  - .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-PLAN.md  # this file
  - .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md  # GENERATED (Task 4)
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - ".planning/amendments/osf_deviations.md exists and consolidates entries 8-17 (10 total entries; canonical in-tree OSF deviation log)"
    - "Bundle script bin/build_id_vs_ref_ld_submission_bundle.sh exits 0 — its 11-step internal verification (figures=14, supplementary=10, scripts=13, root files, manuscript render) all PASS"
    - "Generated bundle ZIP at .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip is valid (unzip -t exit 0) and contains post-rename branding only (no track_a_pivot / build_track_a_submission_bundle tokens)"
    - "bundle_manifest.tsv at the same path captures sha256 + size_bytes + built_at_iso for the new bundle"
    - "md5_baseline.tsv at .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv enumerates the extended whitelist (parent W7 PLAN narrow regex globs + W4.5-A + W5 + W6 sub-task extensions)"
    - "Stage 2 md5 invariant verification HARD FAILS (exit 1) on unwhitelisted file changes per checker iter 1 WARNING 4 — narrow regex globs anchored to specific files, NOT broad directory-prefix exclusions"
    - "results_identity_ld/ NOT staged (DEC-2026-04-25-01 invariant; .gitignore-enforced)"
    - "STATE.md body line 67 (Last activity:) updated; frontmatter Track-B-encoded fields (status / stopped_at / Current focus / Current Position / progress.*) UNTOUCHED per memory feedback_state_md_keep_current.md"
    - ".planning/ROADMAP.md NOT modified (out of scope per Carter; phase closeout ROADMAP update deferred to a separate gating action)"
    - "No git push; commits land locally only"
  artifacts:
    - path: ".planning/amendments/osf_deviations.md"
      provides: "Canonical in-tree OSF deviation log (NEW file)"
      contains: "Cache invalidation"
      min_lines: 200
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip"
      provides: "Genome Medicine resubmission bundle (post-rename, post-W6-narrative-reframe)"
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv"
      provides: "Bundle SHA-256 + size + build-time manifest"
      contains: "id_vs_ref_ld_genome_medicine_submission.zip"
    - path: ".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv"
      provides: "Stage 2 md5 invariant whitelist (extended scope; covers all phase-rewritten files across W0-W6 + W7)"
      contains: "rationale"
  key_links:
    - from: "bin/build_id_vs_ref_ld_submission_bundle.sh"
      to: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip"
      via: "script's hardcoded OUT_DIR (line 34) + ZIP_PATH (line 429)"
      pattern: "id_vs_ref_ld_genome_medicine_submission\\.zip"
    - from: "DEC-2026-05-01-02 (cache-staleness refuted; Layer-2 canonical 78.9%)"
      to: ".planning/amendments/osf_deviations.md entry_12 (W4 disposition revision)"
      via: "deviation-log entry; HONEST_FINDING disposition recorded"
      pattern: "DEC-2026-05-01-02|HONEST_FINDING"
    - from: "Pre-phase frozen state (commit cacdbfe) ↔ HEAD (c211824)"
      to: "Stage 2 md5 invariant whitelist + HARD FAIL on unwhitelisted file changes"
      via: "git diff --name-only cacdbfe..HEAD + comm -23 against narrow regex globs"
      pattern: "unwhitelisted_changes\\.txt"
---

<objective>
W7 phase closeout — final wave of phase ta-sh2b3-canonical-and-cache-refresh. Four atomic deliverables: (1) consolidated 10-entry OSF deviation log capturing W4 cache-invalidation + W4.5-A continuation + W5 aggregator + 4 W6 narrative-narrowed/rename/cascade quick tasks; (2) regenerated Genome Medicine submission bundle via the renamed builder script (post-W6 manuscript content + post-rename branding); (3) extended Stage 2 md5 invariant whitelist + HARD FAIL verification covering all files this phase rewrote across all sub-tasks; (4) STATE.md body line 67 update + atomic commit chain.

Purpose: Phase gating-out artifact. Carter takes the regenerated bundle to the *Genome Medicine* journal portal for resubmission. The consolidated deviation log is the canonical in-tree source for all 10 methodological deviations from the OSF pre-registration that accumulated during this phase. The Stage 2 md5 invariant verification ensures no files outside the curated rewrite-whitelist were inadvertently mutated by phase work — replacing the parent W7 PLAN's WARN-only semantics with HARD FAIL (exit 1) per checker iter 1 WARNING 4, and replacing broad directory-prefix exclusions with NARROW regex globs anchored to specific files.

Output: 4 atomic git commits + 3 NEW files + 1 GENERATED bundle ZIP + 1 NEW manifest TSV + STATE.md body-line-67 mutation. No push. ROADMAP untouched. Track B (m3) artifacts untouched. results_identity_ld/ NOT staged.

Hard non-targets (carry forward):
- DO NOT push (no `git push`)
- DO NOT update ROADMAP.md (out of scope this task)
- DO NOT update STATE.md frontmatter (Track-B-encoded; preserve exactly)
- DO NOT update STATE.md Track-B-encoded body fields (Current focus / Current Position / stopped_at / progress.*)
- DO NOT mutate any prior `.planning/quick/*-PLAN.md` or `*-SUMMARY.md` (other tasks)
- DO NOT mutate parent W7 PLAN at `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md` (read-only INPUT)
- DO NOT mutate any prior W0-W6 SUMMARY/PLAN files
- DO NOT touch `results/fine_mapping/susie/*.fit.rds` (96 V4 niter=1000 fits; 3 SH2B3 anchor md5s pinned: 462ada6a / 8255c1ac / a041eecc)
- DO NOT alter prior W6 narrative reframes (1c1 + lsk + tjn + 1e1 changes preserved exactly)
- DO NOT stage `results_identity_ld/` (DEC-2026-04-25-01 invariant; .gitignore enforces)
- DO NOT touch m3 / Track B artifacts (recent commits 2bf54fd + 66d6b8f + 94f85cc; another terminal active)
- DO NOT delete the pre-existing `track_a_genome_medicine_submission.zip` in the same target directory (separate artifact from a separate quick task; out of scope)
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/W4-DISPOSITION-REVISED.md
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v7.json
@.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/DECISIONS.md
@bin/build_id_vs_ref_ld_submission_bundle.sh
@CLAUDE.md

<environment_facts>
Verified at planner init time (2026-05-03 ~18:42 UTC):

- Working dir: /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
- HEAD = c2118248 (W6 W1-headline 260503-1e1 close-out)
- HEAD is 32 commits ahead of origin/main (no push planned)
- Frozen reference commit cacdbfe (2026-04-27) = original Track A bundle commit; canonical Stage-2-frozen-state reference
- Pandoc 3.8.3 PRESENT at /rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc (executable; --version OK)
- ALL 5 PDF engines ABSENT on PATH (xelatex / lualatex / pdflatex / tectonic / weasyprint)
  → Bundle script's 5-engine fallback chain will fall through to RENDER_PATH="html:pandoc-fallback" (HTML only, NOT PDF)
  → This is BY DESIGN per RESEARCH.md "5-engine PDF fallback chain → HTML"; script accepts pdf OR html (line 478)
  → NOT a Rule-3 BLOCKING; surface in SUMMARY as documented fact
- Bundle script (488 lines, 18,436 bytes) hardcodes:
  - OUT_DIR = ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss" (line 34)
  - BUNDLE_NAME = "id_vs_ref_ld_genome_medicine_submission" (line 33)
  - ZIP_PATH = "$ABS_OUT_DIR/$BUNDLE_NAME.zip" (line 429)
  - mkdir -p "$ABS_OUT_DIR" (line 37; auto-creates)
  - rm -f "$ZIP_PATH" before zip (line 431; idempotent re-runs)
- Output dir already exists with pre-existing artifacts (260427-vbq-PLAN.md / -SUMMARY.md / build_log.txt / track_a_genome_medicine_submission.zip-OLD); none touched by new build
- Script self-verification (lines 451-485): figures=14, supplementary=10, scripts/R/aggregators=3, scripts/R/figures=7, scripts/python=3, README.md, LICENSE-CODE, LICENSE-MANUSCRIPT-AND-DATA, CITATION.cff, manuscript/id-vs-ref-LD.md, manuscript/id-vs-ref-LD.(pdf|html). Script EXIT=0 ⇒ all pass.
- W6 rename targets all PRESENT on disk:
  - docs/manuscript/id-vs-ref-LD.md (114306 bytes; modified 2026-05-03 01:34 by 260503-1e1)
  - .planning/amendments/ID-VS-REF-LD-STRATEGY.md (57112 bytes)
  - bin/build_id_vs_ref_ld_submission_bundle.sh (18436 bytes; executable)
- .planning/amendments/osf_deviations.md ABSENT (Task 1 creates)
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv ABSENT (Task 3 creates)
- .planning/quick/260427-.../bundle_manifest.tsv ABSENT (Task 2 creates)
- Pre-existing dirty (NOT phase-generated; carried through baseline regardless): .claude/settings.json + .planning/config.json
</environment_facts>

<canonical_numerics>
From planning_context live-state block (verified) + DECISIONS.md DEC-2026-05-01-02:

Wave 4 status distribution (1,274 total attempts):
- Pre-Wave-4 baseline (V1 cache mtime 2026-04-30T00:30): 1005 too_few_snps + 32 success + 235 no_qtl_cs + 2 qtl_susie_failed
- Post-W4.5-A continuation: SAME 1005/32/235/2 (Δ = 0; cache-staleness hypothesis REFUTED)
- Mechanical PASS gate ("too_few_snps ≥ 800"): FAILED
- Strategic disposition: HONEST_FINDING (DEC-2026-05-01-02) — Layer-2 canonical 78.9%

3 SH2B3 anchor .fit.rds md5s (post-W4 V4 niter=1000; PIN; out of W7 mutation scope):
- 462ada6a (BMI fit)
- 8255c1ac (HTN fit)
- a041eecc (stroke fit)

Wave 1 L-sweep (preserved per W6-260503-1e1):
- 51/96 = 53.1% headline VALUE preserved (PRESERVE-WITH-DISCLOSURE)
- L-sweep at L∈{15,20,30} niter=1000: NONE_CONVERGED at strict gate (per W6-260503-1e1 / TRACK-A-FROZEN L370-L398)

Wave 3 outcome (preserved per W6-260502-tjn):
- BRANCH_C SURVIVE: BMI-HTN, HTN-stroke, HTN-T2D all PP.H4=1.0 at rs3184504 under matched-LD R2 canonical-pair coloc.susie (commit b3395d9)

Track A frozen-numbers ledger (load-bearing; do NOT mutate this phase):
- Layer-2 LIVE block at TRACK-A-FROZEN-NUMBERS.md L30-L59
- Wave-3 outcome LIVE block at L338-L369
- Wave-1 L-sweep LIVE block at L370-L398
</canonical_numerics>

<consolidated_deviation_entries>
W7 osf_deviations.md must enumerate 10 entries (entry_8 through entry_17). Entry shape per parent W7 PLAN Task 1 + D-TA-Cache-OSF directive:
- header: Entry N: <title> (Phase ta-sh2b3-canonical-and-cache-refresh, <wave>) — <discovery date>
- Discovery date / Root cause / Invalidation rationale / Before-after numerics (where applicable)
- Commit pointers / OSF cross-reference / Manuscript disclosure (where applicable)
- Cross-reference to other entries via "See entry_N below/above" where they cascade

Entry mapping (chronological by recorded-date):

| # | wave | decision token | one-line summary |
|---|---|---|---|
| 8 | W4 | D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH | V4 dispatch: SuSiE-RSS rebuild at niter=1000 (3 SH2B3 anchor md5s); QTL-coloc rebuild deferred to W4.5 |
| 9 | W4.5 | D-TA-WAVE4-5-A-OUTCOME = W4.5-a | 2-pass qtl_coloc rebuild via fire_w4_5_qtl_coloc_only.sh (commit b368e0e) |
| 10 | W4.5-A | D-TA-WAVE4-5-A-SCOPE-CORRECTION | T1 production scope re-locked to phase2_enabled_sources: [gtex_eqtl, gtex_sqtl] (commit 986af29) |
| 11 | W4.5-A | re-fire outcome | Supervisor PID 2670648 99.6% complete; 260501-r1q drained 4 missing + 3rd-pass aggregator |
| 12 | W4 | DEC-2026-05-01-02 disposition revision | Mechanical FAILED → strategic HONEST_FINDING; 78.9% Layer-2 canonical; W4.5-B skipped |
| 13 | W6 | 260502-1c1 narrative narrowing | 6 manuscript sites: cache-staleness-as-fact → cache-staleness-tested-and-refuted |
| 14 | W6 | 260502-lsk mechanical rename | 3 git mv at R100; 17 forward-ref fix-ups; STATE.md ref-fixups (Carter Option B) |
| 15 | W6 | D-TA-WAVE3-OUTCOME = BRANCH_C_SURVIVE (260502-tjn) | Wave 2 R2 canonical-pair coloc.susie all PP.H4=1.0 at rs3184504 (commit b3395d9) |
| 16 | W6 | D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE (260503-1e1) | L-sweep NONE_CONVERGED at strict gate; 51/96 headline preserved + Supplementary Methods Table SX |
| 17 | W7 | D-TA-Cache-OSF (this task) | Anchor entry: cache-invalidation re-fire = cache-hygiene-fix + cache-staleness-hypothesis-test (Δ = 0 refutes) |

Entry 17 is the ANCHOR (originally-anticipated W7 deviation per parent W7 PLAN Task 1); entries 8-16 are the cascade. Entries chronologically order by recorded-date but cross-reference via prefix "(see entry_N)" within prose.
</consolidated_deviation_entries>

<extended_md5_whitelist>
Parent W7 PLAN whitelist (lines 70-85 / 113-130) + sub-task extensions per planner:

Whitelisted file paths (md5_baseline.tsv schema: path<TAB>md5<TAB>rationale<TAB>commit_introducing):

W5 (parent W7 PLAN whitelist):
- results/multitrait/coloc_summary.tsv
- .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (Wave-5 + later Wave-1/Wave-3 LIVE blocks)

W6 rename targets (parent + extensions):
- docs/manuscript/id-vs-ref-LD.md
- .planning/amendments/ID-VS-REF-LD-STRATEGY.md
- bin/build_id_vs_ref_ld_submission_bundle.sh

W6 R-script comment-header reference fix-ups (parent W7 PLAN — list verbatim):
- src/R/figures/fig1a_pipeline_schematic.R
- src/R/figures/fig1b_locus_panels.R
- src/R/figures/fig2_cs_yield.R
- src/R/figures/fig3_sh2b3_eur_collapse_forest.R
- src/R/figures/fig5_variant_mech_scorecard.R
- src/R/figures/fig_h3_ld_overlap_dose_response.R
- src/R/figures/fig_s2_paired_fit_structural_inflation.R
- src/R/aggregators/aggregate_per_trait_pair_and_hubs.R
- src/R/aggregators/aggregate_table1_pleiotropic_loci.R
- src/R/aggregators/aggregate_table3_admissible_pairs.R

W6 .planning/ forward-facing reference fix-ups:
- .planning/STATE.md (body line 67 only this phase touches; frontmatter Track-B-encoded preserved)
- .planning/DECISIONS.md (DEC-2026-05-01-01, DEC-2026-05-01-02 added)
- .planning/PROJECT.md
- .planning/ROADMAP.md (forward-ref fix-up only; phase-status COMPLETE update is OUT OF SCOPE this task)

W6 cross-ref updates:
- .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md
- .planning/amendments/AUDIT-REVIEW-2026-04-25.md
- .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md
- .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md

Possibly-touched W6 cascade:
- docs/manuscript/track_a_source.md  (only if 1c1 or 1e1 wrote to it; verified at task time via git diff)

W7 NEW files (this task):
- .planning/amendments/osf_deviations.md
- .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv

Pre-existing dirty (not phase-generated, but in working tree at commit time; planner exempts from invariant):
- .claude/settings.json
- .planning/config.json

Narrow regex globs (used at verification time as -vE chains; each documented inline in Task 3):

(1)  Wave 1 L-sweep outputs:           ^results_lsweep_L(15|20|30)/fine_mapping/susie/SH2B3_12q24__EUR__(bmi|hypertension|stroke)\.(json|fit\.rds|log)$
(1b) Wave 1 L-sweep backup directories: ^results_lsweep_L(15|20|30)\.pre(Fix|Niter500)\.bak\.[0-9_]+/   ← present in git status; W6-260503-1e1 generated
(2)  Wave 2 R2 coloc outputs:          ^results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__[a-z]+_vs_[a-z]+\.json$
(3)  Wave 4 cache backup dirs:         ^results/qtl_coloc\.preFix\.bak\.[0-9_]+/
(4)  Wave 4 refreshed cache:           ^results/qtl_coloc/[A-Za-z0-9_.]+\.json$
(5)  SuSiE-RSS conditional backups:    ^results/fine_mapping/susie\.preFix\.bak\.[0-9_]+/
(6)  Wave 4 refreshed susie layer:     ^results/fine_mapping/susie/[A-Za-z0-9_.]+\.(json|fit\.rds|log)$
(7)  Phase-generated logs:             ^logs/(lsf/[A-Za-z0-9_.]+|wave[0-9]+_[A-Za-z0-9_]+_[0-9]+\.log)$
(8)  Wave 5 aggregator outputs:        ^results/track_a_aggregations/[a-z_]+\.tsv$
(9)  Wave 5 figures:                   ^figures/fig_h3_ld_overlap_dose_response\.(png|pdf)$
(10) Wave 7 bundle outputs:            ^\.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/(id_vs_ref_ld_genome_medicine_submission\.zip|bundle_manifest\.tsv)$
(11) Phase-internal scaffold:          ^bin/(fire_susie_lsweep|fire_canonical_susie_pairs|fire_qtl_coloc_cache_refresh|fire_w4_5_qtl_coloc_only|verify_ta_sh2b3_phase)\.sh$
(12) Phase config overlays:            ^config/(susie_policy_L(15|20|30)|pipeline_lsweep_L(15|20|30)_overlay|pipeline_canonical_r2_overlay)\.yaml$
(13) Phase python builder:             ^src/python/build_coloc_manifest_r2\.py$
(14) Phase planning subdir:            ^\.planning/phases/ta-sh2b3-canonical-and-cache-refresh/
(15) Quick-task artifacts (this + W4.5 + W6 cascade): ^\.planning/quick/2605(0[12]|03)-(r1q|vxi|wdn|1c1|lsk|tjn|1e1|kfq)-[a-z0-9-]+/
(16) New W7 deviation log:             ^\.planning/amendments/osf_deviations\.md$
(17) Wave 2 R2 manifest TSV:           ^results/multitrait/coloc_manifest(_R2|_merged)?\.tsv$
(18) Pre-existing dirty:               ^(\.claude/settings\.json|\.planning/config\.json)$
</extended_md5_whitelist>

<interfaces>
From bin/build_id_vs_ref_ld_submission_bundle.sh (488 lines, executable; verified):

```bash
# Hardcoded bundle config (lines 33-37):
BUNDLE_NAME="id_vs_ref_ld_genome_medicine_submission"
OUT_DIR=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss"
ABS_OUT_DIR="$ABS_REPO_ROOT/$OUT_DIR"
mkdir -p "$ABS_OUT_DIR"

# Hardcoded pandoc + 5-engine fallback (lines 40-49 + 77-142):
PANDOC_HARDCODED="/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc"
# Engines tried: xelatex → lualatex → pdflatex → tectonic → weasyprint → HTML
# Final fallback: RENDER_PATH="html:pandoc-fallback"

# ZIP creation (lines 429-435):
ZIP_PATH="$ABS_OUT_DIR/$BUNDLE_NAME.zip"
rm -f "$ZIP_PATH"  # idempotent
( cd "$STAGING" && zip -r -q "$ZIP_PATH" "$BUNDLE_NAME" )

# Self-verification (lines 451-485):
# - figures count == 14 (FAIL exit 1 if mismatch)
# - supplementary count == 10
# - scripts/R/aggregators == 3
# - scripts/R/figures == 7
# - scripts/python == 3
# - README.md, LICENSE-CODE, LICENSE-MANUSCRIPT-AND-DATA, CITATION.cff (FAIL if missing)
# - manuscript/id-vs-ref-LD.md required
# - manuscript/id-vs-ref-LD.(pdf|html) required (either accepted)
# - 50 MB cap → WARN but NOT FAIL above 52428800 bytes
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Create .planning/amendments/osf_deviations.md with consolidated 10-entry deviation log (entries 8-17)</name>
  <files>
    .planning/amendments/osf_deviations.md
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/W4-DISPOSITION-REVISED.md (anchor narrative for entry_12 cache-staleness refutation)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave4_dispatch_tracker_v7.json (FAILED + outcome_disposition=HONEST_FINDING; verbatim source for entry_12)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md (V1 → W4.5-A chronology; canonical numerics for entry_8 / entry_9 / entry_10 / entry_11)
    - .planning/DECISIONS.md §DEC-2026-05-01-02 (verbatim disposition revision narrative)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md §"D-TA-Cache-OSF" + §"D-TA-WAVE4-OUTCOME" + §"D-TA-Wave3-OUTCOME" + §"D-TA-Wave1-headline" (decision tokens)
  </read_first>
  <action>
    Use the Write tool to create `.planning/amendments/osf_deviations.md` with this exact structure (substitute documented numerics where bracketed):

    ```markdown
    # OSF Deviations Log — id-vs-ref-LD project (Track A)

    **Project:** Identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci
    **OSF deposits:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) — pre-registration; osf.io/az52u — closeout PDF + amendment chain
    **Purpose:** Single canonical in-tree log of methodological deviations from the OSF pre-registration that accumulated during Phase ta-sh2b3-canonical-and-cache-refresh (Waves 0-7). Cache-hygiene fixes, infrastructure changes, narrative reframings, and other non-analytical adjustments are recorded here per project methodology (NOT as pre-registration amendments). Per D-TA-Cache-OSF: deviation-log-only entries; Carter optionally appends abstracts to osf.io/az52u closeout PDF (web-UI workflow).

    **Phase scope:** Waves 0-7 of phase `ta-sh2b3-canonical-and-cache-refresh`; pre-phase frozen reference = commit `cacdbfe` (2026-04-27); post-phase HEAD ≈ `c211824` (2026-05-03 + W7 commits land on top).

    **Cascade structure:** Entry 17 is the methodological ANCHOR (originally-anticipated cache-invalidation deviation per parent W7 PLAN). Entries 8-16 are chronological cascade entries that emerged during phase execution. Cross-references appear inline as "(see entry_N)".

    ---

    ## Entry 8 — V4 dispatch CONSERVATIVE_BOTH override (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4)

    **Discovery date:** 2026-04-29 (Wave 0 SuSiE-RSS variant-ID format diagnostic)

    **Root cause:** Wave 0 diagnostic on `results/fine_mapping/susie/*.fit.rds` confirmed BOTH layers (SuSiE-RSS layer + QTL-coloc cache layer) carried pre-fix variant-ID format (chr:pos vs rsid mismatch). Per `D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH`: rebuild both layers (NOT QTL-coloc-only).

    **Invalidation rationale:** Cache-hygiene rebuild against post-fix code (commits `069b34f` + `7d54183`); same data + same params; methodological deviation only.

    **Execution:** V4 dispatch fired in two phases:
    - SuSiE-RSS rebuild at `niter=1000` confirmed by 3 SH2B3 anchor md5 changes (BMI fit `462ada6a`, HTN fit `8255c1ac`, stroke fit `a041eecc`).
    - QTL-coloc rebuild deferred to W4.5 wave (see entry_9) due to driver scope constraints.

    **Commit pointers:** Wave 4 V4 atomic commits in phase ta-sh2b3-canonical-and-cache-refresh (per W4 SUMMARY `ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md`).

    ---

    ## Entry 9 — W4.5 wave creation: 2-pass QTL-coloc rebuild driver (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5)

    **Discovery date:** 2026-04-30 (W4 SuSiE-RSS layer landed, QTL-coloc cache rebuild needed driver outside W4 scope)

    **Root cause:** `qtl_coloc.smk` 2-pass design (per Snakemake DAG semantics) requires re-firing without invoking the full pipeline driver. Created `bin/fire_w4_5_qtl_coloc_only.sh` to bypass driver per `D-TA-WAVE4-5-A-OUTCOME = W4.5-a`.

    **Invalidation rationale:** Methodological — cache-hygiene re-fire of QTL-coloc layer only; SuSiE-RSS layer (entry_8) preserved at niter=1000.

    **Commit pointers:** `b368e0e` (`bin/fire_w4_5_qtl_coloc_only.sh` driver added).

    ---

    ## Entry 10 — W4.5-A scope correction: T1 production lock recovery (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5-A)

    **Discovery date:** 2026-04-30 ~16:35 EDT (initial W4.5-a dispatch fired with broader phase2 source list; aborted at 1692-job mark)

    **Root cause:** Initial W4.5-a fire used the post-pivot expanded `phase2_enabled_sources` list (1692 jobs); per `D-TA-WAVE4-5-A-SCOPE-CORRECTION` and the original Phase 2 production lock, T1 scope is `[gtex_eqtl, gtex_sqtl]` only (1275 jobs).

    **Invalidation rationale:** Scope-correction; did NOT change methodology — only restored the pre-registered T1 production source set.

    **Execution:** Aborted 1692-job dispatch at 16:35 EDT 2026-04-30; re-fired with `pipeline.yaml::phase2_enabled_sources: [gtex_eqtl, gtex_sqtl]` at 1275 jobs (commit `986af29`).

    **Commit pointers:** `986af29` (pipeline.yaml scope re-lock).

    ---

    ## Entry 11 — W4.5-A continuation re-fire outcome (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5-A continuation)

    **Discovery date:** 2026-05-01 (supervisor PID 2670648 exited at 99.6% complete, 1270/1275 done; 4 missing run_qtl_coloc + aggregator 3rd-pass)

    **Root cause:** Supervisor exit before final 4 `run_qtl_coloc` jobs completed; aggregator never re-ran a 3rd pass against the updated cache.

    **Invalidation rationale:** Methodological — completion of in-progress cache-hygiene rebuild started in entry_9 / entry_10. NO new analytical decisions.

    **Execution:** Quick task `260501-r1q` drained the 4 missing `run_qtl_coloc` outputs and executed the aggregator 3rd pass. Cache-staleness hypothesis was tested AND refuted in this step (Δ status distribution = 0; see entry_12 for disposition).

    **Numerics (post W4.5-A continuation, 1,274 attempts):**
    | metric | pre-fix V1 cache | post-W4.5-A continuation | Δ |
    |---|---|---|---|
    | total_attempts | 1,274 | 1,274 | 0 |
    | too_few_snps | 1,005 (78.9 %) | 1,005 (78.9 %) | 0 |
    | success | 32 | 32 | 0 |
    | no_qtl_cs | 235 | 235 | 0 |
    | qtl_susie_failed | 2 | 2 | 0 |

    **Commit pointers:** `260501-r1q` quick task atomic commits (see `.planning/quick/260501-r1q-*-SUMMARY.md`).

    ---

    ## Entry 12 — W4 disposition revision: mechanical FAILED → strategic HONEST_FINDING (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4) — DEC-2026-05-01-02

    **Discovery date:** 2026-05-01

    **Root cause:** The Wave 4 mechanical PASS gate (`too_few_snps ≥ 800`) FAILED at the post-W4.5-A continuation distribution (1005/32/235/2 unchanged from V1). The cache-staleness hypothesis (that pre-fix code rejected ~78.9 % of attempts owing to chr:pos vs rsid mismatch) was tested in entry_11 AND refuted (Δ = 0). Continuing to W4.5-B (a SuSiE-RSS rebuild) was considered and rejected: LD coverage is the constraint, not iteration budget; rebuild risks breaking the TRACK-A-FROZEN md5 invariant on the 3 SH2B3 anchor `.fit.rds` files (`462ada6a` / `8255c1ac` / `a041eecc`).

    **Invalidation rationale:** Methodological re-disposition. The 78.9 % rate is now adopted as the **canonical Layer-2 finding** parallel to the 53.1 % Layer-1 SuSiE convergence rate (Layer-1 finding from W6-260503-1e1; see entry_16). Both rates are real constraints of the curated-locus design under matched-LD, NOT artifacts of broken code.

    **Disposition recorded:**
    - tracker v7: `outcome_disposition: HONEST_FINDING` + historical_outcome block preserves mechanical FAILED label
    - DECISIONS.md: `DEC-2026-05-01-02`
    - W4-DISPOSITION-REVISED.md: canonical narrative + 3-layer architecture (Layer-1 SuSiE convergence; Layer-2 QTL-coloc rate; Layer-3 substantive Tier-A distribution)

    **W4.5-B explicitly skipped:** SuSiE-RSS rebuild risks md5 break on canonical anchors with no expected change in Layer-2 outcome.

    **Commit pointers:** Tracker v7 + W4-DISPOSITION-REVISED.md atomic commits in phase ta-sh2b3-canonical-and-cache-refresh; DEC-2026-05-01-02 entry in `.planning/DECISIONS.md`.

    ---

    ## Entry 13 — W6 narrative narrowing: cache-staleness reframe (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-1c1

    **Discovery date:** 2026-05-02

    **Root cause:** Following entry_12 (DEC-2026-05-01-02), 6 sites in the manuscript draft `docs/manuscript/id-vs-ref-LD.md` framed cache-staleness as a hypothesis-of-fact (i.e., "78.9 % failure rate was caused by code-data mismatch"). Post-refutation, those framings are factually inconsistent with the disposition.

    **Invalidation rationale:** Documentation-only narrative correction. NO numerical change. The substantive Layer-3 distribution (Tier-A = 0) is now made explicit at all 6 manuscript reframe sites.

    **Execution:** 6 manuscript sites reframed: cache-staleness-as-fact → cache-staleness-tested-and-refuted. Tier-A = 0 substantive Layer-3 distribution explicit. Manuscript size 95,614 → 100,529 bytes.

    **Commit pointers:** Quick task `260502-1c1` atomic commits (see `.planning/quick/260502-1c1-*-SUMMARY.md`).

    ---

    ## Entry 14 — W6 mechanical rename: track_a_pivot → id-vs-ref-LD (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-lsk

    **Discovery date:** 2026-05-02

    **Root cause:** "Track A pivot" framing was historical scaffolding from the 2026-04-22 strategic split; for resubmission to *Genome Medicine*, the project needs a non-pivot, non-revision public handle. Per memory `feedback_original_research_framing.md` and Carter's directive: rename to `id-vs-ref-LD` (factual, scientific).

    **Invalidation rationale:** Mechanical rename — no content change at byte level for the renamed manuscript at the new path (md5 22f412f6 byte-identical pre/post rename); 17 forward-ref fix-ups across R scripts + .planning/ files updated reference paths only.

    **Execution:** 3 `git mv` at R100 (rename detection threshold):
    - `track_a_pivot.md` → `docs/manuscript/id-vs-ref-LD.md`
    - `TRACK-A-PIVOT.md` → `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`
    - `build_track_a_submission_bundle.sh` → `bin/build_id_vs_ref_ld_submission_bundle.sh`

    Plus 17 forward-reference fix-ups + STATE.md ref-fixups per Carter Option B.

    **Rule-1 deviation acknowledged:** Per `feedback_original_research_framing.md` Rule-1, "track_a" tokens are forbidden in framing prose; factual filename references (e.g., the OLD `track_a_pivot.md` filename appearing in a `git mv` command in this entry's Execution block) are exempt as historical-record-preserving references.

    **Commit pointers:** Quick task `260502-lsk` atomic commits.

    ---

    ## Entry 15 — W6 BRANCH_C SURVIVE: Wave-3 outcome materialization (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-tjn

    **Discovery date:** 2026-05-02

    **Root cause:** Wave 3 of the original phase plan was conditional on Wave 2 R2 canonical-pair coloc.susie outcomes. Wave 2 R2 fire (commit `b3395d9`) produced PP.H4 = 1.0 for BMI-HTN, HTN-stroke, HTN-T2D at rs3184504 under matched-LD. Per `D-TA-WAVE3-OUTCOME = BRANCH_C_SURVIVE`: SH2B3 anchor flips from "collapse / not executed" to "validated under matched-LD."

    **Invalidation rationale:** Materialization of pre-registered branch outcome. NO methodological deviation; the outcome WAS pre-registered as a possible W3 branch.

    **Execution:** 11 manuscript sites reframed; new "## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE" block appended at `TRACK-A-FROZEN-NUMBERS.md` lines 338-369.

    **Commit pointers:** Quick task `260502-tjn` atomic commits + Wave 2 fire commit `b3395d9`.

    ---

    ## Entry 16 — W6 Wave-1 L-sweep PRESERVE-WITH-DISCLOSURE (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260503-1e1

    **Discovery date:** 2026-05-03

    **Root cause:** Wave 1 L-sweep at L ∈ {15, 20, 30} with niter=1000 returned NONE_CONVERGED at strict gate for all 9 (3 traits × 3 L-values) configurations. The 51/96 = 53.1 % headline value (Layer-1 SuSiE convergence rate at the original niter=500 run) was at risk of being undermined or replaced. Per `D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE`: preserve the 51/96 numerator as the canonical Layer-1 rate AND disclose the L-sweep null-convergence outcome at strict gate.

    **Invalidation rationale:** Methodological disclosure. Per Zou 2022 §Discussion (n_CS << L behavior), strict-gate FAIL at L ∈ {15, 20, 30} niter=1000 is consistent with structural sparsity, not pipeline failure. NO numerator change.

    **Execution:**
    - 4 manuscript narrative sites updated (preserve 51/96; disclose L-sweep null-convergence; cite Zou 2022)
    - 1 Supplementary Methods Table SX added (per-trait per-L convergence details)
    - Concurrent L216 residual-staleness fix (orthogonal site that still framed cache-staleness as fact)
    - 4 honest-framing-lock anchors preserved at section-header level
    - Forbidden-token count ≤ baseline 35 (per `feedback_original_research_framing.md` constraint)
    - 3 SH2B3 anchor `.fit.rds` md5s preserved exactly (`462ada6a` / `8255c1ac` / `a041eecc`)
    - L-sweep disclosure column added to canonical results table
    - New "## Wave-1 L-sweep convergence outcomes (PRESERVE-WITH-DISCLOSURE) — LIVE" block at `TRACK-A-FROZEN-NUMBERS.md` lines 370-398
    - No STATE.md Track-B-encoded mutations
    - No push

    **Commit pointers:** Quick task `260503-1e1` atomic commits (HEAD ≈ `c211824` pre-W7).

    ---

    ## Entry 17 — Cache-invalidation deviation (ANCHOR; D-TA-Cache-OSF) (Phase ta-sh2b3-canonical-and-cache-refresh, Waves 0-4 + W4.5)

    **Discovery date:** 2026-04-28 (audit-V2 §Eval 3.2 review)

    **Root cause:** The intermediate QTL-coloc cache at `results/qtl_coloc/` (1,274 per-attempt JSONs; 1,005 / 1,274 = 78.9 % `too_few_snps` failure rate at V1 cache mtime 2026-04-30T00:30) was generated BEFORE the variant-ID matcher fixes landed in HEAD:
    - Commit `069b34f` (2026-04-21): `run_qtl_coloc.R` extended to tolerate chr:pos-formatted variant IDs (added candidate-based best-overlap match: rsid / chrpos / variant_id).
    - Commit `7d54183` (2026-04-21): `run_susie_rss.R` LD-panel-rsid override added when LD has rsids and sumstats has chr:pos.

    **Two-fold methodological treatment:**
    1. **Cache-hygiene fix:** rebuild cache against post-fix code; same data + same params + post-fix code = the analysis the OSF pre-registration already covers.
    2. **Cache-staleness hypothesis test:** the 78.9 % rate predicted to drop substantially if pre-fix code was rejecting attempts owing to format mismatch.

    **Invalidation rationale:** Methodological **cache hygiene fix + falsifiable hypothesis test**, NOT a new analysis. Per D-TA-Cache-OSF (locked decision in CONTEXT.md): treat as **deviation-log entry only** — NOT a pre-registration amendment.

    **Test outcome:** The cache-staleness hypothesis was REFUTED. Δ status distribution = 0 across all 4 status categories at the post-W4.5-A continuation distribution (see entry_11). The 78.9 % rate is a real constraint of the harmonized-locus design, NOT a software artifact. See entry_12 for the full disposition (HONEST_FINDING, Layer-2 canonical adoption, W4.5-B skip).

    **Cache backup preservation:** Pre-fix cache moved (NOT deleted) to `results/qtl_coloc.preFix.bak.${TS}` (timestamped per RESEARCH.md Pitfall 5); rollback path preserved on disk. Identical convention applied to `results/fine_mapping/susie/` (SuSiE-RSS layer in scope per `D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH`; see entry_8).

    **Commit pointers:**
    - Code fixes (already in HEAD, NOT this phase): `069b34f`, `7d54183`
    - V4 dispatch (entry_8): Wave 4 atomic commits
    - W4.5-a driver (entry_9): `b368e0e`
    - W4.5-A scope correction (entry_10): `986af29`
    - W4.5-A continuation (entry_11): quick task `260501-r1q` commits
    - Disposition revision (entry_12): tracker v7 + W4-DISPOSITION-REVISED.md commits + DEC-2026-05-01-02

    **OSF cross-reference:** Linked to `osf.io/az52u` closeout PDF amendment chain. This deviation entry is the canonical in-tree source. Carter optionally appends a brief abstract of this entry (or the entire 10-entry log) to the osf.io/az52u closeout PDF (web-UI workflow; OUT OF SCOPE for this task).

    **Manuscript disclosure:** The methodological description of this cache invalidation, the cache-staleness hypothesis test, and its refutation, are integrated at:
    - `docs/manuscript/id-vs-ref-LD.md` Methods §Harmonization-Pipeline Diagnostics (per W6-260502-1c1; see entry_13)
    - `docs/manuscript/id-vs-ref-LD.md` Discussion §Identity-LD Inflation (per W6-260502-tjn BRANCH_C reframe; see entry_15)
    - `docs/manuscript/id-vs-ref-LD.md` Limitations bullets (per W6-260502-1c1 + 260503-1e1; see entries 13, 16)

    ---

    ## Phase summary block

    | Entry | Wave | Decision token | Disposition |
    |---|---|---|---|
    | 8 | W4 | D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH | applied; 3 SH2B3 anchor md5s changed |
    | 9 | W4.5 | D-TA-WAVE4-5-A-OUTCOME = W4.5-a | driver landed (b368e0e) |
    | 10 | W4.5-A | D-TA-WAVE4-5-A-SCOPE-CORRECTION | scope re-locked (986af29) |
    | 11 | W4.5-A | continuation outcome | 1270/1275 + 4 drained; 3rd-pass aggregator |
    | 12 | W4 | DEC-2026-05-01-02 (disposition revision) | mechanical FAILED → HONEST_FINDING |
    | 13 | W6 | 260502-1c1 narrative narrowing | 6 sites reframed |
    | 14 | W6 | 260502-lsk mechanical rename | 3 git mv at R100 |
    | 15 | W6 | D-TA-WAVE3-OUTCOME = BRANCH_C_SURVIVE (260502-tjn) | 11 sites reframed |
    | 16 | W6 | D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE (260503-1e1) | 5 sites + Sup Table SX |
    | 17 | W7 | D-TA-Cache-OSF (anchor) | this log file created |

    **Total atomic commits across phase Waves 0-7 (estimated):** 32+ (per HEAD-vs-cacdbfe ahead-count).

    **End of consolidated deviation log.**
    ```

    Atomic commit (explicit path; no `git add -A`):
    ```bash
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
    git add .planning/amendments/osf_deviations.md
    git commit -m "docs(ta-sh2b3, W7-260503-kfq): create osf_deviations.md with consolidated 10-entry deviation log (entries 8-17 per D-TA-Cache-OSF + W4.5-A + W6 cascade)"
    ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
      [ -f .planning/amendments/osf_deviations.md ] && \
      [ "$(wc -l < .planning/amendments/osf_deviations.md)" -ge 200 ] && \
      grep -qE "^## Entry 8 " .planning/amendments/osf_deviations.md && \
      grep -qE "^## Entry 17 " .planning/amendments/osf_deviations.md && \
      grep -q "069b34f" .planning/amendments/osf_deviations.md && \
      grep -q "7d54183" .planning/amendments/osf_deviations.md && \
      grep -q "b368e0e" .planning/amendments/osf_deviations.md && \
      grep -q "986af29" .planning/amendments/osf_deviations.md && \
      grep -q "b3395d9" .planning/amendments/osf_deviations.md && \
      grep -qE "78\.9 ?%" .planning/amendments/osf_deviations.md && \
      grep -q "deviation-log entry only" .planning/amendments/osf_deviations.md && \
      grep -q "HONEST_FINDING" .planning/amendments/osf_deviations.md && \
      grep -q "DEC-2026-05-01-02" .planning/amendments/osf_deviations.md && \
      grep -q "BRANCH_C_SURVIVE" .planning/amendments/osf_deviations.md && \
      grep -q "PRESERVE-WITH-DISCLOSURE" .planning/amendments/osf_deviations.md && \
      grep -q "osf.io/az52u" .planning/amendments/osf_deviations.md && \
      grep -q "Cache invalidation" .planning/amendments/osf_deviations.md && \
      git log -1 --format="%s" | grep -q "W7-260503-kfq" && \
      echo PASS</automated>
  </verify>
  <done>
    `.planning/amendments/osf_deviations.md` exists at the canonical in-tree path with all 10 entries (8-17), all required commit pointers (`069b34f`, `7d54183`, `b368e0e`, `986af29`, `b3395d9`), all key decision tokens (`HONEST_FINDING`, `DEC-2026-05-01-02`, `BRANCH_C_SURVIVE`, `PRESERVE-WITH-DISCLOSURE`), and the OSF cross-reference (`osf.io/az52u`). File is ≥ 200 lines. Atomic commit landed via explicit path. Anchor (entry 17) cross-references the W4.5-A continuation outcome (entry 11) and the disposition revision (entry 12) inline. Per `feedback_original_research_framing.md` Rule-1 deviation: factual filename references in entry 14 git mv lines are exempt and documented as such.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Pre-build pandoc/engine probes + run renamed bundle script + verify integrity + create bundle_manifest.tsv (SHA-256)</name>
  <files>
    .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip
    .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv
    logs/wave7_bundle_build_*.log
  </files>
  <read_first>
    - bin/build_id_vs_ref_ld_submission_bundle.sh (488 lines; verify executable + hardcoded paths line 33-37 + ZIP_PATH line 429)
  </read_first>
  <action>
    1. **Pre-fire HARD GATE checks** (script readiness + W6 rename targets present):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # Script + W6 rename targets present
       [ -x bin/build_id_vs_ref_ld_submission_bundle.sh ] || { echo "ABORT: bundle script not executable"; exit 1; }
       [ -f docs/manuscript/id-vs-ref-LD.md ] || { echo "ABORT: post-rename manuscript missing"; exit 1; }
       [ -f .planning/amendments/ID-VS-REF-LD-STRATEGY.md ] || { echo "ABORT: post-rename strategy doc missing"; exit 1; }

       # Pitfall 6 mitigation: no stale tokens in script body
       if grep -nE "track_a_pivot|build_track_a_submission_bundle" bin/build_id_vs_ref_ld_submission_bundle.sh; then
           echo "ABORT: stale rename tokens in bundle script body (line numbers above)"
           exit 1
       fi

       # Pandoc probe
       PANDOC_PATH="/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc"
       [ -x "$PANDOC_PATH" ] || { echo "ABORT: pandoc absent at hardcoded path $PANDOC_PATH"; exit 1; }
       "$PANDOC_PATH" --version | head -1

       # PDF engine probe (informational; HTML fallback expected per environment_facts)
       echo "[INFO] PDF engine availability probe (HTML fallback expected):"
       for engine in xelatex lualatex pdflatex tectonic weasyprint; do
           P=$(command -v $engine 2>/dev/null || true)
           if [ -n "$P" ]; then echo "  $engine: $P"; else echo "  $engine: ABSENT"; fi
       done
       echo "[INFO] All engines absent ⇒ script falls through to RENDER_PATH=html:pandoc-fallback (BY DESIGN)"
       ```

       If ANY hard-gate check above exits 1, HALT to Carter (do NOT proceed to step 2).

    2. **Run the bundle script** (script handles staging + render + zip + self-verification; capture log):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       mkdir -p logs
       BUILD_LOG="logs/wave7_bundle_build_$(date -u +%Y%m%d_%H%M%SZ).log"

       # Script's hardcoded output:
       #   OUT_DIR     = .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss
       #   BUNDLE_NAME = id_vs_ref_ld_genome_medicine_submission
       #   ZIP_PATH    = $OUT_DIR/$BUNDLE_NAME.zip
       # Script does mkdir -p $OUT_DIR (line 37) and rm -f $ZIP_PATH (line 431) — re-runs are idempotent.

       bash bin/build_id_vs_ref_ld_submission_bundle.sh 2>&1 | tee "$BUILD_LOG"
       SCRIPT_EXIT="${PIPESTATUS[0]}"

       if [ "$SCRIPT_EXIT" -ne 0 ]; then
           echo "ABORT: bundle script exited $SCRIPT_EXIT"
           echo "Last 50 lines of build log:"
           tail -50 "$BUILD_LOG"
           exit 1
       fi
       echo "[INFO] Bundle script exit 0 — internal 11-step verification (figures=14 / supplementary=10 / scripts=13 / root files / manuscript render) all PASS"
       ```

    3. **External integrity verification** (NOT covered by script self-check; planner adds Pitfall 6 propagation check):
       ```bash
       BUNDLE=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip"
       [ -f "$BUNDLE" ] || { echo "ABORT: bundle not at expected path: $BUNDLE"; exit 1; }

       # unzip -t (CRC + structural integrity)
       unzip -t "$BUNDLE" > "logs/wave7_bundle_unzip_test.log" 2>&1 || { echo "FAIL: bundle integrity (unzip -t)"; tail -20 logs/wave7_bundle_unzip_test.log; exit 1; }
       echo "PASS: unzip -t clean"

       # Pitfall 6 propagation: ZIP contents must NOT carry pre-rename tokens
       N_STALE=$(unzip -l "$BUNDLE" | grep -cE "track_a_pivot|build_track_a_submission_bundle" || true)
       [ "$N_STALE" -eq 0 ] || { echo "FAIL: bundle contents contain $N_STALE pre-rename tokens"; unzip -l "$BUNDLE" | grep -E "track_a_pivot|build_track_a_submission_bundle"; exit 1; }
       echo "PASS: no pre-rename tokens in bundle contents"

       # Post-rename branding sanity check
       N_BRAND=$(unzip -l "$BUNDLE" | grep -cE "id[-_]vs[-_]ref[-_]LD|id_vs_ref_ld" || true)
       [ "$N_BRAND" -ge 1 ] || { echo "FAIL: no post-rename branding in bundle contents"; exit 1; }
       echo "PASS: $N_BRAND post-rename branding entries"
       ```

    4. **Create bundle_manifest.tsv** (SHA-256 + size + build-time; explicit path):
       ```bash
       MANIFEST=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv"
       BUNDLE_HASH=$(sha256sum "$BUNDLE" | cut -d' ' -f1)
       BUNDLE_SIZE=$(stat -c '%s' "$BUNDLE")
       BUILT_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
       BUNDLE_BASENAME=$(basename "$BUNDLE")

       # 4-column schema per orchestrator: path<TAB>size_bytes<TAB>sha256<TAB>built_at_iso
       printf "path\tsize_bytes\tsha256\tbuilt_at_iso\n" > "$MANIFEST"
       printf "%s\t%s\t%s\t%s\n" \
           "$BUNDLE_BASENAME" \
           "$BUNDLE_SIZE" \
           "$BUNDLE_HASH" \
           "$BUILT_AT" \
           >> "$MANIFEST"

       echo "[INFO] bundle_manifest.tsv contents:"
       cat "$MANIFEST"

       # Sanity: manifest has exactly 2 lines (header + 1 data row)
       [ "$(wc -l < "$MANIFEST")" -eq 2 ] || { echo "FAIL: manifest line count != 2"; exit 1; }

       # Record manifest hash + bundle hash for SUMMARY
       echo "[FACT] bundle sha256 = $BUNDLE_HASH"
       echo "[FACT] bundle size = $BUNDLE_SIZE bytes"
       echo "[FACT] bundle built at = $BUILT_AT"
       ```

    5. **Verify results_identity_ld/ NOT staged** (DEC-2026-04-25-01 invariant):
       ```bash
       UNWANTED_STAGED=$(git diff --cached --name-only 2>/dev/null | grep -c '^results_identity_ld' || echo 0)
       [ "$UNWANTED_STAGED" -eq 0 ] || { echo "FAIL: results_identity_ld/ staged in git index"; exit 1; }
       echo "PASS: results_identity_ld/ NOT staged (DEC-2026-04-25-01 preserved)"
       ```

    6. **Atomic commit** (explicit paths; per memory `feedback_multi_terminal_staging.md` — never `git add -A`):
       ```bash
       git add ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip" \
               ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv" \
               logs/wave7_bundle_build_*.log \
               logs/wave7_bundle_unzip_test.log

       git commit -m "feat(ta-sh2b3, W7-260503-kfq): regenerate id-vs-ref-LD Genome Medicine bundle + SHA-256 manifest (script exit 0; HTML fallback render path; sha256=${BUNDLE_HASH:0:12}…)"
       ```

       NOTE: If `BUNDLE_HASH` is not exported into the commit message context (variable lifetime across heredoc/here-doc shells), substitute its actual first-12-char prefix from step 4 before invoking the commit; the commit message format is non-load-bearing — only the message prefix `feat(ta-sh2b3, W7-260503-kfq):` matters for traceability.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
      BUNDLE=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip" && \
      MANIFEST=".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv" && \
      [ -f "$BUNDLE" ] && \
      unzip -t "$BUNDLE" > /dev/null 2>&1 && \
      [ "$(unzip -l "$BUNDLE" | grep -cE 'track_a_pivot|build_track_a_submission_bundle')" -eq 0 ] && \
      [ "$(unzip -l "$BUNDLE" | grep -cE 'id[-_]vs[-_]ref[-_]LD|id_vs_ref_ld')" -ge 1 ] && \
      [ -f "$MANIFEST" ] && \
      [ "$(wc -l < "$MANIFEST")" -eq 2 ] && \
      head -1 "$MANIFEST" | grep -q "^path	size_bytes	sha256	built_at_iso$" && \
      tail -1 "$MANIFEST" | awk -F'\t' '{ exit !($1=="id_vs_ref_ld_genome_medicine_submission.zip" && $2 ~ /^[0-9]+$/ && $3 ~ /^[a-f0-9]{64}$/ && $4 ~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/) }' && \
      [ "$(git diff --cached --name-only 2>/dev/null | grep -c '^results_identity_ld')" -eq 0 ] && \
      git log -1 --format="%s" | grep -q "W7-260503-kfq" && \
      echo PASS</automated>
  </verify>
  <done>
    Bundle script exit 0 (its 11-step internal verification — figures=14, supplementary=10, scripts=13, root files, manuscript render — all PASS). Generated bundle ZIP at the script's hardcoded path is unzip -t clean, contains zero pre-rename tokens (Pitfall 6 propagation verified), and contains ≥ 1 post-rename branding entry. bundle_manifest.tsv at the same path captures sha256 (64-hex) + size_bytes + built_at_iso (UTC ISO 8601). PDF engines absent ⇒ script's HTML fallback (`RENDER_PATH=html:pandoc-fallback`) used by design — manuscript ships as `.html` not `.pdf` (acceptable per script line 478). results_identity_ld/ confirmed NOT staged. Atomic commit landed via explicit paths. Build log + unzip test log captured under `logs/wave7_*`.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Build extended md5_baseline.tsv whitelist + Stage 2 md5 invariant HARD FAIL verification (per checker iter 1 WARNING 4)</name>
  <files>
    .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
  </files>
  <read_first>
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md §<interfaces> lines 113-130 (parent W7 PLAN narrow regex globs verbatim)
  </read_first>
  <action>
    1. **Construct extended whitelist** (parent W7 PLAN whitelist + W4.5-A + W5 + W6 cascade extensions):

       Use the Write tool to create `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` with this exact content:

       ```
       path	md5	rationale	commit_introducing
       results/multitrait/coloc_summary.tsv	{md5}	W5 explicit re-render (Pitfall 3 exemption)	{commit}
       results/multitrait/coloc_manifest_R2.tsv	{md5}	Wave 2 R2 manifest builder output	{commit}
       .planning/amendments/TRACK-A-FROZEN-NUMBERS.md	{md5}	W5+W6 LIVE block updates (L30/L83/L338-369/L370-398)	{commit}
       docs/manuscript/id-vs-ref-LD.md	{md5}	W6 rename target + W6-260502-1c1 + W6-260502-tjn + W6-260503-1e1 narrative atomic updates	{commit}
       .planning/amendments/ID-VS-REF-LD-STRATEGY.md	{md5}	W6-260502-lsk rename target (was TRACK-A-PIVOT.md)	{commit}
       bin/build_id_vs_ref_ld_submission_bundle.sh	{md5}	W6-260502-lsk rename target + heredoc sed (Pitfall 6); W7 invocation does NOT mutate	{commit}
       src/R/figures/fig1a_pipeline_schematic.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig1b_locus_panels.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig2_cs_yield.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig3_sh2b3_eur_collapse_forest.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig5_variant_mech_scorecard.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig_h3_ld_overlap_dose_response.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/figures/fig_s2_paired_fit_structural_inflation.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/aggregators/aggregate_per_trait_pair_and_hubs.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/aggregators/aggregate_table1_pleiotropic_loci.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       src/R/aggregators/aggregate_table3_admissible_pairs.R	{md5}	W6-260502-lsk comment-header reference fix-up	{commit}
       .planning/STATE.md	{md5}	W6+W7 forward-facing reference fix-up + Last-activity body line 67 (Track-B-encoded fields preserved)	{commit}
       .planning/DECISIONS.md	{md5}	DEC-2026-05-01-01 + DEC-2026-05-01-02 entries (W4 disposition revision; CDR v7→v8)	{commit}
       .planning/PROJECT.md	{md5}	W6-260502-lsk forward-facing reference fix-up	{commit}
       .planning/ROADMAP.md	{md5}	W6-260502-lsk forward-facing reference fix-up (phase-status COMPLETE update DEFERRED to separate task)	{commit}
       .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md	{md5}	W6-260502-lsk cross-ref update (filename preserved)	{commit}
       .planning/amendments/AUDIT-REVIEW-2026-04-25.md	{md5}	W6-260502-lsk cross-ref update	{commit}
       .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md	{md5}	W6-260502-lsk cross-ref update	{commit}
       .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md	{md5}	W6-260502-lsk cross-ref update	{commit}
       docs/manuscript/track_a_source.md	{md5}	W6 cascade source-doc cross-ref update (filename retains track_a per Rule-1 factual-filename exemption)	{commit}
       .planning/amendments/osf_deviations.md	{md5}	W7-260503-kfq NEW file (consolidated 10-entry deviation log)	{commit}
       .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md	{md5}	W0-W6 addendum sub-sections (D-TA-04-DIAGNOSTIC, D-TA-OSF-COVERAGE, D-TA-Wave1-PRIMARY-L, D-TA-Wave2-outcomes, D-TA-WAVE3-OUTCOME, D-TA-WAVE4-OUTCOME, D-TA-Wave6-pivot-free-audit, D-TA-Wave1-headline)	{commit}
       .claude/settings.json	{md5}	pre-existing dirty (NOT phase-generated; carried in working tree at phase start)	{commit}
       .planning/config.json	{md5}	pre-existing dirty (NOT phase-generated; carried in working tree at phase start)	{commit}
       ```

       Then materialize the actual md5/commit values via shell:

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       MD5_BASE=".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv"

       # Iterate over rows after header; for each path that exists on disk, fill md5 + commit
       awk -F'\t' 'NR>1 {print $1}' "$MD5_BASE" | while read -r p; do
           if [ -e "$p" ]; then
               H=$(md5sum "$p" 2>/dev/null | cut -d' ' -f1)
               # Last commit that touched this path (returns empty if untracked / never committed)
               C=$(git log -1 --format=%h -- "$p" 2>/dev/null || true)
               [ -z "$C" ] && C="UNTRACKED"
               # In-place sed substitution, escaping path slashes
               PE=$(printf '%s' "$p" | sed 's|/|\\/|g')
               sed -i "s|^${PE}\t{md5}\t|${PE}\t${H}\t|" "$MD5_BASE"
               sed -i "s|\t${PE}_PLACEHOLDER_COMMIT||" "$MD5_BASE"  # no-op safety
               sed -i "/^${PE}\t/ s|\t{commit}$|\t${C}|" "$MD5_BASE"
           else
               # Path doesn't exist (e.g., pre-existing dirty file deleted; or not yet created)
               PE=$(printf '%s' "$p" | sed 's|/|\\/|g')
               sed -i "/^${PE}\t/ s|\t{md5}\t|\tABSENT\t|" "$MD5_BASE"
               sed -i "/^${PE}\t/ s|\t{commit}$|\tABSENT|" "$MD5_BASE"
           fi
       done

       # Sanity: no remaining {md5} or {commit} placeholders
       if grep -E "\{md5\}|\{commit\}" "$MD5_BASE"; then
           echo "FAIL: unfilled placeholders remain in $MD5_BASE"
           exit 1
       fi

       echo "[INFO] md5_baseline.tsv contents:"
       cat "$MD5_BASE"

       # Sanity: row count >= 25 (header + 29 data rows expected, but lower bound is 25)
       N_ROWS=$(wc -l < "$MD5_BASE")
       [ "$N_ROWS" -ge 25 ] || { echo "FAIL: md5_baseline.tsv has $N_ROWS lines (< 25)"; exit 1; }
       echo "[INFO] $N_ROWS lines in whitelist (header + $((N_ROWS-1)) data rows)"
       ```

    2. **Stage 2 md5 invariant verification — HARD FAIL on unwhitelisted file changes** (per checker iter 1 WARNING 4):

       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       FROZEN_COMMIT=cacdbfe  # canonical Stage-2-frozen-state reference (per CONTEXT.md D-TA-cacdbfe)

       # All files changed (added / modified / deleted) between frozen ref and HEAD
       git diff --name-only "$FROZEN_COMMIT"..HEAD | sort -u > /tmp/changed_files_post_phase.txt
       N_CHANGED=$(wc -l < /tmp/changed_files_post_phase.txt)
       echo "[INFO] $N_CHANGED files changed between $FROZEN_COMMIT..HEAD"

       # Whitelisted file paths (column 1 of md5_baseline.tsv, skip header)
       awk -F'\t' 'NR>1 {print $1}' .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv | sort -u > /tmp/whitelist_paths.txt

       # Subtract whitelist from changed; remaining are "unwhitelisted candidates"
       comm -23 /tmp/changed_files_post_phase.txt /tmp/whitelist_paths.txt > /tmp/unwhitelisted_candidates.txt

       # Now apply NARROW regex globs (per checker iter 1 WARNING 4 fix — anchored to specific files,
       # NOT broad directory-prefix exclusions). Each grep -vE is documented with its rationale.
       cat /tmp/unwhitelisted_candidates.txt | \
         grep -vE "^results_lsweep_L(15|20|30)/fine_mapping/susie/SH2B3_12q24__EUR__(bmi|hypertension|stroke)\.(json|fit\.rds|log)$" | \
         grep -vE "^results_lsweep_L(15|20|30)\.pre(Fix|Niter500)\.bak\.[0-9_]+/" | \
         grep -vE "^results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__[a-z]+_vs_[a-z]+\.json$" | \
         grep -vE "^results/qtl_coloc\.preFix\.bak\.[0-9_]+/" | \
         grep -vE "^results/qtl_coloc/[A-Za-z0-9_.]+\.json$" | \
         grep -vE "^results/fine_mapping/susie\.preFix\.bak\.[0-9_]+/" | \
         grep -vE "^results/fine_mapping/susie/[A-Za-z0-9_.]+\.(json|fit\.rds|log)$" | \
         grep -vE "^logs/(lsf/[A-Za-z0-9_.]+|wave[0-9]+_[A-Za-z0-9_]+_[0-9]+\.log)$" | \
         grep -vE "^results/track_a_aggregations/[a-z_]+\.tsv$" | \
         grep -vE "^figures/fig_h3_ld_overlap_dose_response\.(png|pdf)$" | \
         grep -vE "^\.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/(id_vs_ref_ld_genome_medicine_submission\.zip|bundle_manifest\.tsv)$" | \
         grep -vE "^bin/(fire_susie_lsweep|fire_canonical_susie_pairs|fire_qtl_coloc_cache_refresh|fire_w4_5_qtl_coloc_only|verify_ta_sh2b3_phase)\.sh$" | \
         grep -vE "^config/(susie_policy_L(15|20|30)|pipeline_lsweep_L(15|20|30)_overlay|pipeline_canonical_r2_overlay)\.yaml$" | \
         grep -vE "^src/python/build_coloc_manifest_r2\.py$" | \
         grep -vE "^\.planning/phases/ta-sh2b3-canonical-and-cache-refresh/" | \
         grep -vE "^\.planning/quick/2605(0[12]|03)-(r1q|vxi|wdn|1c1|lsk|tjn|1e1|kfq)-[a-z0-9-]+/" | \
         grep -vE "^\.planning/amendments/osf_deviations\.md$" | \
         grep -vE "^results/multitrait/coloc_manifest(_R2|_merged)?\.tsv$" | \
         grep -vE "^logs/wave7_bundle_(build|unzip_test)[A-Za-z0-9_.]*\.log$" \
         > /tmp/unwhitelisted_changes.txt

       # HARD FAIL on any remaining entries (per checker iter 1 WARNING 4 — replaces WARN-only semantics)
       if [ -s /tmp/unwhitelisted_changes.txt ]; then
           echo "===== BLOCKER: Stage 2 md5 invariant violated ====="
           echo "Unwhitelisted file changes (per checker iter 1 WARNING 4 — HARD FAIL):"
           cat /tmp/unwhitelisted_changes.txt
           echo "==================================================="
           echo ""
           echo "Triage:"
           echo "  (a) If a file is a legitimate phase output not in whitelist → add a row to md5_baseline.tsv with rationale + last-touching commit"
           echo "  (b) If a file is unintended phase mutation → revert via 'git checkout cacdbfe -- <path>'"
           echo "  (c) If a file matches a NEW namespace not in the regex chain above → extend the chain (anchored, narrow regex) and document inline"
           echo "  Do NOT silently broaden via directory-prefix patterns (broken by design — per checker iter 1 WARNING 4)"
           exit 1
       fi
       echo "PASS: Stage 2 md5 invariant respected (whitelist + narrow regex globs cover all changes)"
       ```

       NOTE: If the HARD FAIL fires during plan execution, the executor MUST stop and surface to Carter for triage decision (per "Triage" options a/b/c above). Adding rows to `md5_baseline.tsv` is the correct response if the file is a legitimate phase output — NOT silently broadening the regex chain.

    3. **Atomic commit** (explicit path):
       ```bash
       git add .planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv
       git commit -m "feat(ta-sh2b3, W7-260503-kfq): create md5_baseline.tsv extended whitelist + verify Stage 2 md5 invariant (HARD FAIL semantics per checker iter 1 WARNING 4; narrow regex globs)"
       ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
      MD5_BASE=".planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv" && \
      [ -f "$MD5_BASE" ] && \
      [ "$(wc -l < $MD5_BASE)" -ge 25 ] && \
      head -1 "$MD5_BASE" | grep -q "^path	md5	rationale	commit_introducing$" && \
      ! grep -qE "\{md5\}|\{commit\}" "$MD5_BASE" && \
      grep -q "^\.planning/amendments/osf_deviations\.md	" "$MD5_BASE" && \
      grep -q "^docs/manuscript/id-vs-ref-LD\.md	" "$MD5_BASE" && \
      grep -q "^bin/build_id_vs_ref_ld_submission_bundle\.sh	" "$MD5_BASE" && \
      grep -q "^\.planning/amendments/TRACK-A-FROZEN-NUMBERS\.md	" "$MD5_BASE" && \
      [ ! -s /tmp/unwhitelisted_changes.txt ] && \
      git log -1 --format="%s" | grep -q "W7-260503-kfq" && \
      echo PASS</automated>
  </verify>
  <done>
    `md5_baseline.tsv` enumerates ≥ 25 rows covering all phase-rewritten files (parent W7 PLAN whitelist + W4.5-A + W5 + W6 sub-task extensions + 2 pre-existing dirty exemptions); each row has actual md5 + last-touching commit (no `{md5}` / `{commit}` placeholders remain). Stage 2 md5 invariant verification passes via narrow regex globs (per checker iter 1 WARNING 4) — HARD FAIL exit 1 fires on any unwhitelisted file change. `/tmp/unwhitelisted_changes.txt` is empty. Atomic commit landed via explicit path.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Update STATE.md body line 67 (Last activity) + create 260503-kfq SUMMARY.md + atomic commit</name>
  <files>
    .planning/STATE.md
    .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md
  </files>
  <read_first>
    - .planning/STATE.md (verify body line 67 shape: `Last activity: YYYY-MM-DD - <description>`; verify frontmatter Track-B-encoded fields untouched)
  </read_first>
  <action>
    1. **Update STATE.md body line 67 ONLY** (per memory `feedback_state_md_keep_current.md` + `feedback_state_md_keep_current.md` pattern; preserve everything else):

       Use the Edit tool on `.planning/STATE.md`. Find line 67 (current value):
       ```
       Last activity: 2026-05-03 - Completed quick task 260503-1e1: W6 D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE materialization (4 manuscript narrative sites + 1 Supplementary Methods Table SX added + concurrent L216 residual-staleness fix; TRACK-A-FROZEN Wave-1 L-sweep LIVE block appended at file tail; 51/96 headline numerator preserved; strict-gate FAIL 0/9 at niter=1000 disclosed per Zou 2022 §Discussion n_CS << L; 4 honest-framing-lock anchors preserved at section-header level; forbidden-token count ≤ baseline 35; 3 SH2B3 anchor .fit.rds md5s preserved; no STATE.md Track-B-encoded mutations; no push)
       ```

       Replace with (single line, exact format):
       ```
       Last activity: 2026-05-03 - Completed quick task 260503-kfq: W7 phase closeout (osf_deviations.md 10-entry consolidated log entries 8-17 created at .planning/amendments/; id-vs-ref-LD Genome Medicine bundle regenerated via renamed builder script — sha256 in bundle_manifest.tsv at .planning/quick/260427-vbq-...; HTML render path used by design — all 5 PDF engines absent, RENDER_PATH=html:pandoc-fallback; md5_baseline.tsv extended whitelist 29 rows at .planning/phases/ta-sh2b3-canonical-and-cache-refresh/; Stage 2 md5 invariant HARD FAIL semantics per checker iter 1 WARNING 4 — narrow regex globs PASS; results_identity_ld/ NOT staged DEC-2026-04-25-01; ROADMAP UNTOUCHED phase-COMPLETE update deferred; 4 atomic commits; no push; STATE.md frontmatter Track-B-encoded fields preserved exactly)
       ```

       HARD VERIFY immediately after the Edit:
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

       # Frontmatter Track-B-encoded fields MUST be byte-identical pre/post Edit
       grep -q "^milestone: v3.1.2" .planning/STATE.md || { echo "FAIL: frontmatter milestone mutated"; exit 1; }
       grep -q "^milestone_name: milestone" .planning/STATE.md || { echo "FAIL: frontmatter milestone_name mutated"; exit 1; }
       grep -q "^status: \"recovery_stage_2_awaiting_fire" .planning/STATE.md || { echo "FAIL: frontmatter status mutated"; exit 1; }
       grep -q "^stopped_at: Completed m3-aou-afr-ld-panel-build" .planning/STATE.md || { echo "FAIL: frontmatter stopped_at mutated"; exit 1; }
       grep -q "^  total_phases: 12" .planning/STATE.md || { echo "FAIL: frontmatter progress.total_phases mutated"; exit 1; }
       grep -q "^  completed_phases: 6" .planning/STATE.md || { echo "FAIL: frontmatter progress.completed_phases mutated"; exit 1; }
       grep -q "^  percent: 100" .planning/STATE.md || { echo "FAIL: frontmatter progress.percent mutated"; exit 1; }

       # Body Track-B-encoded fields MUST be byte-identical
       grep -q "^\*\*Current focus:\*\* Phase m3-aou-afr-ld-panel" .planning/STATE.md || { echo "FAIL: body Current focus mutated"; exit 1; }
       grep -q "^Phase: m3-aou-afr-ld-panel" .planning/STATE.md || { echo "FAIL: body Current Position Phase mutated"; exit 1; }
       grep -qE "^Plan: 2 of 6" .planning/STATE.md || { echo "FAIL: body Current Position Plan mutated"; exit 1; }

       # Last activity line — MUST contain new task signature
       grep -q "260503-kfq" .planning/STATE.md || { echo "FAIL: Last activity not updated to 260503-kfq"; exit 1; }
       grep -q "W7 phase closeout" .planning/STATE.md || { echo "FAIL: Last activity W7 marker missing"; exit 1; }

       echo "PASS: STATE.md frontmatter + Track-B-encoded fields preserved; body line 67 updated"
       ```

    2. **Create quick-task SUMMARY** at `.planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md`:

       Use the Write tool. Content:

       ```markdown
       ---
       quick_task: 260503-kfq
       slug: w7-closeout-bundle-and-osf-deviation-osf
       phase_role: W7-closeout (final wave of ta-sh2b3-canonical-and-cache-refresh)
       date: 2026-05-03
       atomic_commits: 4
       pushed: false
       ---

       # Quick Task 260503-kfq SUMMARY — W7 phase closeout: bundle + osf_deviations + md5 invariant

       ## Scope delivered

       - **Task 1:** `.planning/amendments/osf_deviations.md` created with 10-entry consolidated deviation log (entries 8 through 17) covering W4 cache-invalidation cascade + W4.5-A continuation + W5 aggregator + 4 W6 narrative-narrowed/rename/cascade sub-tasks. Anchor entry 17 = D-TA-Cache-OSF (cache-hygiene fix + falsifiable hypothesis test; cascade entries 8-16 chronologically ordered with cross-references).
       - **Task 2:** Genome Medicine submission bundle regenerated via `bin/build_id_vs_ref_ld_submission_bundle.sh`. Bundle ZIP at script's hardcoded path `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`. SHA-256 + size + build-time captured in `bundle_manifest.tsv` (sibling). Bundle script's 11-step internal verification (figures=14, supplementary=10, scripts=13, root files, manuscript render) all PASS. PDF engines absent ⇒ HTML fallback used by design (`RENDER_PATH=html:pandoc-fallback`). Pitfall 6 propagation verified (zero pre-rename tokens in ZIP contents).
       - **Task 3:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` created with 29 rows (extended whitelist covering W0-W6 + W7 phase-rewritten files + 2 pre-existing dirty exemptions). Stage 2 md5 invariant verified HARD FAIL (exit 1) on unwhitelisted changes per checker iter 1 WARNING 4 — narrow regex globs anchored to specific files. `/tmp/unwhitelisted_changes.txt` empty.
       - **Task 4:** STATE.md body line 67 updated; Track-B-encoded fields (frontmatter + body Current focus / Current Position / progress.*) preserved byte-identical per memory `feedback_state_md_keep_current.md`. ROADMAP.md UNTOUCHED (phase-COMPLETE update deferred to separate gating action).

       ## Out of scope

       - OSF closeout PDF post (osf.io/az52u web-UI workflow; in-tree `osf_deviations.md` is canonical source)
       - Phase-wide D1-D7 verification harness JSON sweep (deferred; Stage 2 md5 invariant + bundle integrity gates suffice for closeout)
       - ROADMAP.md phase-status COMPLETE update
       - Track B (m3) artifacts — untouched

       ## Atomic commits

       1. `docs(ta-sh2b3, W7-260503-kfq):` create osf_deviations.md (Task 1)
       2. `feat(ta-sh2b3, W7-260503-kfq):` regenerate bundle + manifest (Task 2)
       3. `feat(ta-sh2b3, W7-260503-kfq):` md5_baseline.tsv whitelist + Stage 2 invariant (Task 3)
       4. `docs(ta-sh2b3, W7-260503-kfq):` STATE.md body-line-67 update + this SUMMARY (Task 4)

       ## Numerics + facts

       - Bundle path: `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`
       - Bundle SHA-256: `{captured_in_bundle_manifest.tsv}`
       - Bundle size: `{captured_in_bundle_manifest.tsv}` bytes
       - Render path: `html:pandoc-fallback` (all 5 PDF engines absent: xelatex / lualatex / pdflatex / tectonic / weasyprint)
       - Manuscript file in bundle: `manuscript/id-vs-ref-LD.md` + `manuscript/id-vs-ref-LD.html` (NOT .pdf)
       - md5_baseline.tsv rows: 29 (header + 28 data rows; exact count to be confirmed at execution time)
       - Frozen reference commit: `cacdbfe` (2026-04-27 original Track A bundle)
       - HEAD before W7: `c211824` (W6-260503-1e1 close-out)
       - HEAD after W7: 4 commits ahead

       ## Cross-references

       - Parent W7 PLAN: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md` (read-only INPUT)
       - W4 SUMMARY: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md`
       - W4 disposition: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/W4-DISPOSITION-REVISED.md`
       - DEC-2026-05-01-02 (cache-staleness refuted; HONEST_FINDING): `.planning/DECISIONS.md`
       - TRACK-A-FROZEN-NUMBERS.md LIVE blocks: L30-59 (Layer-2), L338-369 (Wave-3 BRANCH_C), L370-398 (Wave-1 PRESERVE-WITH-DISCLOSURE)

       ## Honored constraints

       - 100% public data (no wet-lab; standard academic DUAs)
       - Solo author (rigor via multi-method triangulation, OSF pre-registration)
       - GPFS filesystem (no worktree isolation; `solo` mode + `git.isolation: branch`)
       - Original-research framing per `feedback_original_research_framing.md` (Rule-1 factual filename references exempt as documented)
       - State preservation per `feedback_state_md_keep_current.md` (Track-B-encoded fields preserved)
       - Multi-terminal staging per `feedback_multi_terminal_staging.md` (explicit paths only; never `git add -A`)
       - No push per Carter directive
       ```

       Substitute the actual SHA-256 + size + manifest row count from Task 2 + Task 3 outputs at execution time.

    3. **Atomic commit** (explicit paths):
       ```bash
       cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
       git add .planning/STATE.md \
               .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md \
               .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-PLAN.md
       git commit -m "docs(ta-sh2b3, W7-260503-kfq): STATE.md body-line-67 + 260503-kfq SUMMARY (W7 phase closeout — bundle + osf_deviations + md5 invariant; 4 atomic commits; no push)"
       ```

       NOTE: 260503-kfq-PLAN.md (this file) is staged in this final commit if not already staged in an earlier ad-hoc commit. The orchestrator may have staged it pre-execution; the `git add` above is idempotent.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
      grep -q "260503-kfq" .planning/STATE.md && \
      grep -q "W7 phase closeout" .planning/STATE.md && \
      grep -q "^milestone: v3.1.2" .planning/STATE.md && \
      grep -q "^milestone_name: milestone" .planning/STATE.md && \
      grep -q "^stopped_at: Completed m3-aou-afr-ld-panel-build" .planning/STATE.md && \
      grep -q "^\*\*Current focus:\*\* Phase m3-aou-afr-ld-panel" .planning/STATE.md && \
      grep -qE "^Plan: 2 of 6" .planning/STATE.md && \
      [ -f .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md ] && \
      grep -q "atomic_commits: 4" .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md && \
      grep -q "pushed: false" .planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md && \
      [ "$(git log --oneline c211824..HEAD | wc -l)" -ge 4 ] && \
      [ "$(git log --since='2026-05-03 18:00 UTC' --oneline | grep -c 'W7-260503-kfq')" -ge 4 ] && \
      [ "$(git log -1 --format='%s')" != "" ] && \
      echo PASS</automated>
  </verify>
  <done>
    STATE.md body line 67 updated to reflect 260503-kfq W7 closeout completion; frontmatter Track-B-encoded fields + body Current-focus / Current-Position / progress.* preserved byte-identical (no Track-B mutation per memory `feedback_state_md_keep_current.md`). 260503-kfq-SUMMARY.md created with 4-atomic-commits + pushed:false metadata + Tasks 1-4 outcome blocks. 4 atomic commits land on top of c211824 (W7-260503-kfq commits): osf_deviations.md (Task 1) + bundle (Task 2) + md5_baseline (Task 3) + STATE.md+SUMMARY+PLAN (Task 4). No push. ROADMAP untouched. Track B (m3) artifacts untouched. Phase ta-sh2b3-canonical-and-cache-refresh's W7 deliverable bundle is closeout-ready for Carter's Genome Medicine resubmission portal action.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pre-phase frozen state (commit cacdbfe) ↔ Post-phase HEAD | Stage 2 md5 invariant: only whitelisted files differ; HARD FAIL on unwhitelisted changes per checker iter 1 WARNING 4 |
| In-tree osf_deviations.md ↔ OSF portal closeout PDF (osf.io/az52u) | In-tree entry is canonical; portal post is optional courtesy and OUT OF SCOPE for this task |
| Bundle ZIP ↔ post-rename file paths | Pitfall 6 mitigation: bundle contents must be post-rename only; pre-rename tokens forbidden |
| STATE.md body ↔ STATE.md Track-B-encoded fields | Only line 67 (Last activity) mutable per memory `feedback_state_md_keep_current.md`; all other fields invariant across this task |
| Track A artifacts ↔ Track B (m3) artifacts | Track B active in another terminal; commits 2bf54fd / 66d6b8f / 94f85cc must remain intact |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-PROCESS-04 | T (Tampering) | Stage 2 md5 invariant on non-target files | mitigate | Task 3 builds 29-row extended whitelist + diffs against frozen commit cacdbfe; HARD FAIL (exit 1) on unwhitelisted file changes per checker iter 1 WARNING 4 (replaces parent W7 PLAN's WARN-only); NARROW regex globs anchored to specific files (replaces broad directory-prefix exclusions); 19 documented exclusion patterns with inline rationale |
| T-PROCESS-02 | I (Information disclosure) | results_identity_ld/ accidentally staged | mitigate | Task 2 step 5 explicit check: `git diff --cached --name-only \| grep -c '^results_identity_ld'` returns 0; .gitignore enforces independently |
| T-PROCESS-01 | T (Tampering) | Bundle ZIP contains stale rename tokens (Pitfall 6 propagation) | mitigate | Task 2 step 1 pre-fire script-body grep (`track_a_pivot|build_track_a_submission_bundle`); Task 2 step 3 post-build ZIP listing grep with HARD FAIL exit 1 on N_STALE > 0 |
| T-STATE-01 | T (Tampering) | STATE.md frontmatter or Track-B-encoded body fields mutated | mitigate | Task 4 step 1 explicit grep checks for milestone / milestone_name / stopped_at / Current focus / Current Position / progress.total_phases / progress.completed_phases / progress.percent; HARD FAIL on any mutation; only body line 67 (Last activity) mutable |
| T-PROCESS-05 | I (Information disclosure) | Bundle SHA-256 not recorded | mitigate | Task 2 step 4 creates bundle_manifest.tsv with sha256 (64-hex validated) + size_bytes + built_at_iso (UTC ISO 8601) |
| T-PROCESS-06 | T (Tampering) | Bundle script HTML fallback not surfaced as known-by-design | accept | Task 2 step 1 informational probe documents engine absence; bundle script line 478 accepts pdf OR html; SUMMARY explicitly notes RENDER_PATH=html:pandoc-fallback was used by design — not a failure |
| T-PROCESS-07 | T (Tampering) | osf_deviations.md misses an entry from the 10-entry cascade | mitigate | Task 1 verify block enforces grep-presence of all 10 entry headers (entry 8, entry 17) + 5 commit pointers (069b34f / 7d54183 / b368e0e / 986af29 / b3395d9) + 4 decision tokens (HONEST_FINDING / DEC-2026-05-01-02 / BRANCH_C_SURVIVE / PRESERVE-WITH-DISCLOSURE); ≥ 200 lines lower bound; consolidated_deviation_entries source-table in plan context block prevents drift |
| T-PROCESS-08 | I (Information disclosure) | Phase ROADMAP-status update happens silently | accept | ROADMAP.md is OUT OF SCOPE per Carter; phase-status COMPLETE update deferred to a separate gating task; this task does NOT mutate ROADMAP.md |
| T-PROCESS-09 | T (Tampering) | Track B (m3) artifacts mutated by W7 work | mitigate | Hard non-targets in objective explicitly forbid m3 artifact touching; explicit `git add` paths in all 4 tasks limit staging to Track A files only |
</threat_model>

<verification>
- osf_deviations.md created with 10 entries + all 5 commit pointers + 4 decision tokens + osf.io/az52u cross-reference (Task 1)
- Bundle script exit 0 → 11-step internal verification all PASS (Task 2)
- Bundle ZIP unzip -t clean (Task 2)
- Bundle ZIP contents zero pre-rename tokens (Pitfall 6 propagation; Task 2)
- bundle_manifest.tsv with 4-column schema + 64-hex sha256 + ISO 8601 built_at (Task 2)
- results_identity_ld/ NOT staged (Task 2; DEC-2026-04-25-01 invariant)
- md5_baseline.tsv ≥ 25 rows; no remaining placeholders (Task 3)
- Stage 2 md5 invariant HARD FAIL on unwhitelisted changes (Task 3; per checker iter 1 WARNING 4)
- /tmp/unwhitelisted_changes.txt empty (Task 3)
- STATE.md body line 67 updated to 260503-kfq W7 closeout (Task 4)
- STATE.md frontmatter Track-B-encoded fields byte-identical (Task 4)
- STATE.md body Current focus / Current Position / progress.* byte-identical (Task 4)
- 260503-kfq-SUMMARY.md created with atomic_commits:4 + pushed:false (Task 4)
- 4 atomic commits land via explicit paths (no `git add -A`)
- ROADMAP.md NOT modified (out of scope)
- No git push
</verification>

<success_criteria>
- 4 NEW/GENERATED files: `.planning/amendments/osf_deviations.md`, bundle ZIP, `bundle_manifest.tsv`, `.planning/phases/.../md5_baseline.tsv`
- 1 UPDATED file: `.planning/STATE.md` (body line 67 only)
- 1 NEW SUMMARY file: `260503-kfq-SUMMARY.md`
- 1 NEW PLAN file (this): `260503-kfq-PLAN.md`
- 4 atomic git commits land (all carry `W7-260503-kfq` marker)
- Bundle is regenerated cleanly (script exit 0 + unzip -t clean + zero pre-rename tokens + post-rename branding present)
- Stage 2 md5 invariant HARD FAIL semantics enforced (per checker iter 1 WARNING 4 — narrow regex globs)
- DEC-2026-04-25-01 invariant preserved (results_identity_ld/ NOT staged)
- STATE.md Track-B-encoded fields preserved byte-identical (per `feedback_state_md_keep_current.md`)
- ROADMAP.md NOT mutated
- No `git push`
- Track B (m3) artifacts untouched (commits 2bf54fd / 66d6b8f / 94f85cc intact)
- 3 SH2B3 anchor `.fit.rds` md5s preserved exactly (`462ada6a` / `8255c1ac` / `a041eecc`)
- Phase ta-sh2b3-canonical-and-cache-refresh closeout deliverable (regenerated bundle + canonical deviation log) ready for Carter's Genome Medicine resubmission portal action
</success_criteria>

<output>
After completion, the orchestrator's quick-task SUMMARY is `.planning/quick/260503-kfq-w7-closeout-bundle-and-osf-deviation-osf/260503-kfq-SUMMARY.md` (created in Task 4). Reference paths in SUMMARY:

- New OSF deviation log: `.planning/amendments/osf_deviations.md`
- New submission bundle: `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`
- Bundle SHA-256 manifest: `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv`
- md5 invariant whitelist: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv`

Optional follow-ups (NOT this task):
- Carter posts deviation entries to osf.io/az52u closeout PDF (web-UI; OUT OF SCOPE)
- Separate gating task updates ROADMAP.md `### Track-A-R2-sh2b3-canonical-and-cache-refresh` `**Status**:` to COMPLETE (OUT OF SCOPE)
- Phase-wide D1-D7 verification harness JSON sweep (`bin/verify_ta_sh2b3_phase.sh` full-run; OUT OF SCOPE)
- `git push` after Carter reviews local 4-commit chain (OUT OF SCOPE)
</output>
