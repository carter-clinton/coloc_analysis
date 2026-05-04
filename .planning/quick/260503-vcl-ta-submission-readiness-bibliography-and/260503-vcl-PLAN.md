---
id: 260503-vcl
slug: ta-submission-readiness-bibliography-and-decision-items-resolution
mode: quick
status: planned
created: "2026-05-03T22:34:00.000Z"
planner_model: claude-opus-4-7-1m
plans_count: 1
tasks_count: 6
phase_context: ta-id-vs-ref-LD-track-a (post W7-260503-kfq closeout)
related_quick_tasks:
  - 260427-vbq  # original bundle assembly
  - 260427-e8n  # Table 1 empty-row disclosure
  - 260424-mxp  # OSF amendment posted at osf.io/az52u
  - 260424-lpy  # main figure 1A
  - 260424-mqo  # main figure 2
  - 260424-p1b  # main figure 1B
  - 260424-k2f  # Fig 4 -> S5 demotion
  - 260425-1vy  # Fig 1A + Fig 3 builders
  - 260501-wdn  # Wave 5 aggregator freeze (coloc_summary.tsv md5 558fca45...)
  - 260503-kfq  # W7 phase closeout (current bundle baseline sha256 10bd7bc9537a...)
constraint_tags:
  - original_research_framing  # NO revision/cleanup/fix/ML tokens in commits or prose
  - multi_terminal_staging     # explicit `git add <path>` only
  - rigor_over_speed           # prefer DOI pinning + double-source verification over guessing
  - state_md_keep_current      # bump last_updated in Pass 6
halt_conditions:
  - id: pass-3-bibliography-unresolvable
    trigger: ">=5 of unnamed ref slots (1-3, 6-10, 11-12, 17-19, 27) cannot be confidently assigned via WebSearch + inline context"
    action: "STOP execution, chat-report unresolvable slot list with surrounding inline context excerpts. Carter approves missing refs manually rather than guessing them into peer-reviewed submission."
must_haves:
  truths:
    - "GitHub URL at L128 of docs/manuscript/id-vs-ref-LD.md points to https://github.com/carter-clinton/coloc_analysis"
    - "osf_deviations.md cross-reference at L128 points to .planning/amendments/osf_deviations.md"
    - "All 6 decision-pending items at L402+ are RESOLVED with provenance documented in .planning/DECISIONS.md and editorial trail at .planning/amendments/track_a_decision_items_resolution_log.md"
    - "Bibliography section contains a numbered Vancouver-style reference list spanning the 32 cited ref-numbers (1-12, 17-23, 27, 29, 34-44 with intentional gaps preserved at 13-16, 24-26, 28, 30-33)"
    - "[EXTRACT:] placeholder at L400 is fully replaced with the rendered numbered bibliography"
    - "R1 editorial subsections (### Add / Promote / Retain / Demote / Drop at L364-399) are removed from manuscript and preserved in .planning/amendments/track_a_references_r1_editorial_trail.md"
    - "Neel/Williams ref-4/ref-5 superscripts at L226-230 remain intact after restructure"
    - "Honest-framing-lock chain holds: NO new occurrences of revision/cleanup/fix/ML tokens introduced into manuscript prose, commit messages, or amendment trail files"
    - "Final residual sweep returns 0 hits except the load-bearing .planning/amendments/osf_deviations.md OSF cross-reference"
    - "Regenerated bundle has new sha256 (different from baseline 10bd7bc9537a...) recorded in bundle_manifest.tsv"
    - "Stage 2 md5 invariant preserved: SH2B3 anchor .fit.rds files unchanged at bmi.EUR=462ada6a, hypertension.EUR=8255c1ac, stroke.EUR=a041eecc"
    - "STATE.md frontmatter last_updated + last_activity bumped to Pass 6 commit time"
    - "All 6 commits use explicit `git add <path>` (NEVER -A or .)"
  artifacts:
    - path: "docs/manuscript/id-vs-ref-LD.md"
      provides: "Genome-Medicine-ready manuscript (URLs aligned, decision-pending section removed, R1 editorial scaffolding replaced with bibliography)"
      modified_in: ["T1-pass-1", "T2-pass-2", "T3-pass-3", "T4-pass-4", "T5-pass-5"]
    - path: ".planning/amendments/track_a_decision_items_resolution_log.md"
      provides: "Editorial provenance trail for all 6 decision-pending items + cross-references to resolution commits"
      created_in: "T2-pass-2"
    - path: ".planning/DECISIONS.md"
      provides: "Append 6 dated decision entries (Item 1 Venue / Item 2 Freeze / Item 3 Repo / Item 4 Table 1 / Item 5 OSF / Item 6 Figures)"
      modified_in: "T2-pass-2"
    - path: "docs/manuscript/refs/track_a_bibliography.md"
      provides: "Standalone Vancouver-style numbered bibliography (32 refs with gaps preserved 1-44)"
      created_in: "T3-pass-3"
    - path: ".planning/amendments/track_a_references_r1_editorial_trail.md"
      provides: "Preserved R1 editorial subsections (### Add / Promote / Retain / Demote / Drop) for audit trail before manuscript restructure"
      created_in: "T4-pass-4"
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip"
      provides: "Regenerated submission bundle with new sha256 (4 of 5 draft-stage gaps closed; ready for scp to local for Carter)"
      modified_in: "T6-pass-6"
    - path: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv"
      provides: "Updated manifest with new sha256 + file count + build_at_iso for Pass-6 regeneration"
      modified_in: "T6-pass-6"
    - path: ".planning/STATE.md"
      provides: "Frontmatter last_updated + last_activity bumped to Pass 6 commit time"
      modified_in: "T6-pass-6"
  key_links:
    - from: "docs/manuscript/id-vs-ref-LD.md L128"
      to: "https://github.com/carter-clinton/coloc_analysis + .planning/amendments/osf_deviations.md"
      via: "Pass 1 alignment"
    - from: "docs/manuscript/id-vs-ref-LD.md L400 [EXTRACT:] slot"
      to: "docs/manuscript/refs/track_a_bibliography.md (rendered inline)"
      via: "Pass 3 paste"
    - from: "docs/manuscript/id-vs-ref-LD.md L222-399 R1 editorial subsections"
      to: ".planning/amendments/track_a_references_r1_editorial_trail.md (preserved) + bibliography prose paragraph + numbered list (replaces inline)"
      via: "Pass 4 restructure"
    - from: "bin/build_id_vs_ref_ld_submission_bundle.sh"
      to: ".planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip + bundle_manifest.tsv"
      via: "Pass 6 builder invocation + 11-step internal verification"
    - from: ".planning/STATE.md frontmatter"
      to: "Pass 6 commit timestamp"
      via: "atomic refresh per feedback_state_md_keep_current"
---

# Quick Task 260503-vcl: Track A Submission Readiness — Bibliography + Decision-Items Resolution

## Goal

Make `docs/manuscript/id-vs-ref-LD.md` ready for *Genome Medicine* submission by closing the 5 draft-stage gaps that would trip peer review of the existing structurally-complete bundle (`.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`, sha256 `10bd7bc9537aa23463014250717c3f3e26714092fb4593aa93ab8222391b0cc7`, built 2026-05-03T19:02:12Z). The 6-pass workflow aligns the GitHub URL + OSF cross-reference at L128, resolves the 6 decision-pending items at L402+ with full DECISIONS.md provenance, assembles the Vancouver-style numbered bibliography at L400 (replacing the `[EXTRACT:]` placeholder), removes the R1 editorial subsections at L364-399 (`### Add / Promote / Retain / Demote / Drop`) while preserving them in an audit-trail amendment file, sweeps for residual draft scaffolding, and regenerates the bundle with a new sha256 — all while preserving the honest-framing-lock chain (NO `revision`/`cleanup`/`fix`/`ML` tokens) and the Stage 2 SH2B3 anchor md5 invariant. Stop after Pass 6 chat report; do NOT push to remote — Carter scp's the regenerated bundle to local.

## Plan

<plan id="P1-vcl-submission-readiness" wave="1" autonomous="false">

<task task_id="T1-pass-1" type="auto">
  <name>Pass 1 — Reference URL + path alignment at L128</name>
  <files_to_modify>
    - docs/manuscript/id-vs-ref-LD.md
  </files_to_modify>
  <action>
    On L128 of docs/manuscript/id-vs-ref-LD.md, replace the stale GitHub URL `https://github.com/The-ASHES-Laboratory/colocalization-ml-analysis` with the canonical `https://github.com/carter-clinton/coloc_analysis`, AND replace the stale osf_deviations.md path `` `.planning/osf_deviations.md` `` with `` `.planning/amendments/osf_deviations.md` ``. Use Edit tool with two surgical replacements; do not touch any other line.
  </action>
  <verify>
    Run all four greps and confirm exact counts:
    1. `grep -c 'The-ASHES-Laboratory/colocalization-ml-analysis' docs/manuscript/id-vs-ref-LD.md` → MUST be 0
    2. `grep -c 'carter-clinton/coloc_analysis' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥1
    3. `grep -nP '^\.planning/osf_deviations\.md$|`\.planning/osf_deviations\.md`' docs/manuscript/id-vs-ref-LD.md` → MUST return 0 lines
    4. `grep -c '\.planning/amendments/osf_deviations\.md' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥1
    Honest-framing-lock check: `grep -ciE 'revision|cleanup|fix|\bML\b' docs/manuscript/id-vs-ref-LD.md` → MUST not increase from baseline (capture baseline before edit).
  </verify>
  <done>
    Both URL/path replacements applied at L128 with stale=0 / canonical≥1 grep counts; honest-framing-lock token count unchanged from pre-edit baseline.
  </done>
  <commit_message>
    docs(quick-260503-vcl, T1): align GitHub URL + osf_deviations.md path at id-vs-ref-LD.md L128 (canonical coloc_analysis repo + .planning/amendments/ subdirectory)
  </commit_message>
</task>

<task task_id="T2-pass-2" type="auto">
  <name>Pass 2 — Resolve 6 decision-pending items + remove section + DECISIONS.md provenance</name>
  <files_to_modify>
    - .planning/amendments/track_a_decision_items_resolution_log.md (NEW)
    - .planning/DECISIONS.md
    - docs/manuscript/id-vs-ref-LD.md
  </files_to_modify>
  <action>
    Three sub-steps in order:
    (a) CREATE `.planning/amendments/track_a_decision_items_resolution_log.md` capturing all 6 items + resolution provenance:
        - Item 1 Venue: Genome Medicine locked
        - Item 2 Freeze date: aggregator freeze landed via /gsd-quick 260501-wdn (Wave 5); coloc_summary.tsv md5 558fca45...
        - Item 3 GitHub repo name: canonical URL = https://github.com/carter-clinton/coloc_analysis (recorded today via 7e31815)
        - Item 4 Table 1: empty-row disclosure-honest table per quick-260427-e8n
        - Item 5 OSF amendment text: posted via /gsd-quick 260424-mxp at osf.io/az52u
        - Item 6 Figure generation: all main figures (1A/1B/2/3/4/5) + S2/S7 landed via 260424-lpy/mqo/p1b/k2f + 260425-1vy + 260501-wdn
    (b) APPEND 6 corresponding entries to `.planning/DECISIONS.md` (use existing convention; date = 2026-05-03; ID prefix DEC-2026-05-03-vcl-Item{N}).
    (c) DELETE entire `## Decision-pending items (MUST resolve before submission)` section from `docs/manuscript/id-vs-ref-LD.md` — header + body, contiguous block starting at L402. Use Read first to confirm exact line range, then Edit to remove.
    Use language "lock", "align", "complete", "consolidate", "compile" — NEVER "revision", "cleanup", "fix", "ML".
  </action>
  <verify>
    1. `test -f .planning/amendments/track_a_decision_items_resolution_log.md && wc -l .planning/amendments/track_a_decision_items_resolution_log.md` → file exists, ≥30 lines
    2. `grep -c 'DEC-2026-05-03-vcl-Item' .planning/DECISIONS.md` → MUST be 6
    3. `grep -c '## Decision-pending items' docs/manuscript/id-vs-ref-LD.md` → MUST be 0
    4. `grep -ciE 'revision|cleanup|fix|\bML\b' docs/manuscript/id-vs-ref-LD.md` → MUST not increase from T1-end baseline
    5. `grep -ciE 'revision|cleanup|fix|\bML\b' .planning/amendments/track_a_decision_items_resolution_log.md` → MUST be 0 (log file uses honest framing too)
  </verify>
  <done>
    Resolution log exists with 6-item provenance trail; DECISIONS.md has 6 new dated entries; manuscript has no `## Decision-pending items` section; honest-framing-lock holds across all three modified files.
  </done>
  <commit_message>
    docs(quick-260503-vcl, T2): lock 6 Track A decision-pending items (Venue/Freeze/Repo/Table1/OSF/Figures) + DECISIONS.md provenance + remove section from manuscript
  </commit_message>
</task>

<task task_id="T3-pass-3" type="auto">
  <name>Pass 3 — Bibliography assembly + paste at L400 [EXTRACT:] slot</name>
  <files_to_modify>
    - docs/manuscript/refs/track_a_bibliography.md (NEW)
    - docs/manuscript/id-vs-ref-LD.md
  </files_to_modify>
  <action>
    Build the Vancouver-style numbered bibliography spanning 32 cited ref-numbers (1-12, 17-23, 27, 29, 34-44 with intentional gaps preserved at 13-16, 24-26, 28, 30-33).

    HIGH-CONFIDENCE ANCHORS (named in manuscript prose — pin directly):
    - Ref 4: Neel JV. Diabetes mellitus: a 'thrifty' genotype rendered detrimental by 'progress'? Am J Hum Genet. 1962;14:353-362.
    - Ref 5: Williams GC. Pleiotropy, natural selection, and the evolution of senescence. Evolution. 1957;11:398-411.
    - Ref 20: Zou Y et al. 2022 (verify via DOI; likely Zou Y et al. PLoS Genet. 2022;18:e1010299)
    - Ref 29: Wang G et al. 2020 J R Stat Soc Series B Stat Methodol. 2020;82:1273-1300 (SuSiE)
    - Ref 42: Pasaniuc B, Price AL. Dissecting the genetics of complex traits using summary association statistics. Nat Rev Genet. 2017;18:117-127.
    - Ref 43: Benner C et al. Prospects of fine-mapping trait-associated genomic regions by using summary statistics from genome-wide association studies. Am J Hum Genet. 2017;101:539-551.

    UNNAMED-SLOT RECOVERY (use WebSearch + inline-context proximity matching):
    - Refs 1-3: Giambartolomei 2014 / Wallace 2020 / Wallace 2021 (foundational coloc family)
    - Refs 6-10: SuSiE-RSS / fine-mapping methodology family (FINEMAP, PolyFun, CAVIAR, PAINTOR candidates)
    - Refs 11-12 at L40: Sirugo G et al. Cell. 2019;177:26-31 + Martin AR et al. Nat Genet. 2019;51:584-591
    - Refs 17-19 at L64: SH2B3/12q24 pleiotropy precursors (Auer/Kraja/Sakaue candidates)
    - Ref 27 at L40: cardiometabolic AFR burden (GBD 2019 / Mensah / Kamiza candidates)

    DATABASE/ANNOTATION SLOTS (refs 21-41, 17 sources): assign via inline-context proximity to which Methods § the superscript appears in: GTEx, Open Targets, GWAS Catalog, Roadmap Epigenomics, ENCODE, CADD, PolyPhen-2, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, gnomAD pLI, STRING, DGIdb, ChEMBL.

    (a) WRITE assembled bibliography to `docs/manuscript/refs/track_a_bibliography.md` (mkdir -p docs/manuscript/refs/ first).
    (b) READ `docs/manuscript/id-vs-ref-LD.md` to locate exact line of `[EXTRACT: full numbered reference list 1–43 ...]` placeholder (orchestrator says L400; verify before edit).
    (c) Edit-replace that placeholder line with the rendered numbered list inline.

    HALT CONDITION: if WebSearch + context fails to confidently assign ≥5 of unnamed slots (1-3, 6-10, 11-12, 17-19, 27), STOP execution. Do NOT commit. Chat-report the unresolvable slot list with surrounding inline-context excerpts (5 lines before/after each superscript). Carter approves missing refs manually rather than guessing them into peer-reviewed submission. Per `feedback_rigor_over_speed`: prefer DOI pinning + double-source verification over guessing.
  </action>
  <verify>
    1. `test -f docs/manuscript/refs/track_a_bibliography.md && wc -l docs/manuscript/refs/track_a_bibliography.md` → file exists, ≥40 lines
    2. `grep -c '^[1-9]\.' docs/manuscript/refs/track_a_bibliography.md` → MUST be 32 (one entry per cited ref-number)
    3. `grep -c 'EXTRACT:' docs/manuscript/id-vs-ref-LD.md` → MUST be 0
    4. `grep -c 'Neel JV' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥1 (ref 4 anchor pasted)
    5. `grep -c 'Williams GC' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥1 (ref 5 anchor pasted)
    6. Honest-framing-lock check: `grep -ciE 'revision|cleanup|fix|\bML\b' docs/manuscript/refs/track_a_bibliography.md` → MUST be 0
  </verify>
  <done>
    Standalone bibliography file exists at docs/manuscript/refs/track_a_bibliography.md with 32 numbered entries (gaps preserved); [EXTRACT:] placeholder fully replaced inline at L400; Neel + Williams anchors verified intact; OR halt condition triggered → chat-report only, no commit.
  </done>
  <commit_message>
    feat(quick-260503-vcl, T3): compile Track A Vancouver-style numbered bibliography (32 refs, gaps 13-16/24-26/28/30-33 preserved) + paste at id-vs-ref-LD.md L400 EXTRACT slot
  </commit_message>
</task>

<task task_id="T4-pass-4" type="auto">
  <name>Pass 4 — References section restructure (replace R1 editorial subsections L222-399)</name>
  <files_to_modify>
    - .planning/amendments/track_a_references_r1_editorial_trail.md (NEW)
    - docs/manuscript/id-vs-ref-LD.md
  </files_to_modify>
  <action>
    (a) Read docs/manuscript/id-vs-ref-LD.md L222-399 to capture current contents of R1 editorial subsections (`### Add` / `### Promote` / `### Retain` / `### Demote` / `### Drop`). Note: Pass 3 inserted the bibliography in the middle of this range — re-locate the exact L-range of the 5 editorial subsection headers + their bodies before editing.
    (b) WRITE captured contents verbatim to `.planning/amendments/track_a_references_r1_editorial_trail.md` with header explaining provenance ("Preserved R1 editorial scaffolding from docs/manuscript/id-vs-ref-LD.md prior to Pass-4 References section restructure for Genome Medicine submission readiness").
    (c) REPLACE the editorial-subsections block in manuscript with EXACTLY two elements in order:
        1. One short prose paragraph (3-5 sentences) describing reference scope. Template: "The 32 references span colocalization methodology (refs 1-3, 6-10), LD-reference theory (refs 20, 42-43), evolutionary medicine framing (refs 4-5), GWAS diversity (refs 11-12), candidate-locus pleiotropy precedent (refs 17-19), cardiometabolic disease burden (ref 27), and annotation databases (refs 21-41). Numbering preserved from inline superscript clusters; gaps at refs 13-16, 24-26, 28, 30-33 are intentional reservation slots."
        2. The numbered bibliography from Pass 3 (already pasted at the EXTRACT slot in Pass 3 — verify it remains in correct location, do not duplicate).
    (d) Verify Neel/Williams superscripts ⁴⁻⁵ at L226-230 area remain intact (load-bearing surviving content from §Demote).
    Use language "lock", "align", "complete", "consolidate", "compile" — NEVER "revision", "cleanup", "fix", "ML".
  </action>
  <verify>
    1. `test -f .planning/amendments/track_a_references_r1_editorial_trail.md && wc -l .planning/amendments/track_a_references_r1_editorial_trail.md` → file exists, ≥30 lines (preserves all 5 subsections)
    2. `grep -cE '^### (Add|Promote|Retain|Demote|Drop)$' docs/manuscript/id-vs-ref-LD.md` → MUST be 0 (all 5 editorial subsections removed)
    3. `grep -c '32 references span' docs/manuscript/id-vs-ref-LD.md` → MUST be 1 (prose paragraph inserted)
    4. `grep -c 'Neel' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥2 (1 ref entry + ≥1 inline superscript context line; superscript context preserved)
    5. `grep -c 'Williams' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥2 (same pattern)
    6. Honest-framing-lock check: `grep -ciE 'revision|cleanup|fix|\bML\b' docs/manuscript/id-vs-ref-LD.md` → MUST not increase from T3-end baseline
    7. Honest-framing-lock check: `grep -ciE 'revision|cleanup|fix|\bML\b' .planning/amendments/track_a_references_r1_editorial_trail.md` → header text MUST be 0; preserved subsection content may legitimately contain these tokens IF they were present in the original R1 scaffolding (record exact count for traceability — do NOT scrub historical content)
  </verify>
  <done>
    R1 editorial trail preserved at amendments/; manuscript References section restructured to (prose paragraph + numbered bibliography); Neel/Williams superscripts intact; honest-framing-lock holds in manuscript and new amendment header (preserved content may carry historical tokens — that is correct for an audit trail).
  </done>
  <commit_message>
    docs(quick-260503-vcl, T4): consolidate Track A References section (preserve R1 editorial scaffolding to amendments trail + replace with scope paragraph + numbered bibliography)
  </commit_message>
</task>

<task task_id="T5-pass-5" type="auto">
  <name>Pass 5 — Final residual sweep</name>
  <files_to_modify>
    - docs/manuscript/id-vs-ref-LD.md (only if residual hits found)
  </files_to_modify>
  <action>
    (a) Run residual sweep: `grep -nP 'EXTRACT:|TODO|FIXME|\.claude/plans|/home/ckclinto' docs/manuscript/id-vs-ref-LD.md`
    (b) Acceptable matches: ONLY `.planning/amendments/osf_deviations.md` at L128 (load-bearing OSF cross-reference; this match should NOT appear under the regex above but capture it explicitly to confirm the pattern doesn't accidentally match it).
    (c) Anything else → residual draft scaffolding from R0/R1 cycles → fix in this pass (Edit tool, surgical replacements).
    (d) Verify no broken section anchors after Pass 4 restructure: `grep -nE '^## (Discussion|Conclusion|Tables|Figure legends)' docs/manuscript/id-vs-ref-LD.md` → all 4 section headers MUST still be present.
    (e) Verify L128 alignment from Pass 1 still holds (no regression): `grep -c 'carter-clinton/coloc_analysis' docs/manuscript/id-vs-ref-LD.md` ≥1; `grep -c 'The-ASHES-Laboratory' docs/manuscript/id-vs-ref-LD.md` = 0.
    Commit ONLY if residual matches were found and corrected; if sweep is clean, skip commit and note "no residuals" in chat report for Pass 5.
  </action>
  <verify>
    1. `grep -nP 'EXTRACT:|TODO|FIXME|\.claude/plans|/home/ckclinto' docs/manuscript/id-vs-ref-LD.md` → MUST return 0 hits (or only documented load-bearing exceptions)
    2. `grep -cE '^## (Discussion|Conclusion|Tables|Figure legends)' docs/manuscript/id-vs-ref-LD.md` → MUST be 4 (all section anchors intact)
    3. `grep -c 'carter-clinton/coloc_analysis' docs/manuscript/id-vs-ref-LD.md` → MUST be ≥1
    4. `grep -c 'The-ASHES-Laboratory' docs/manuscript/id-vs-ref-LD.md` → MUST be 0
    5. Honest-framing-lock check (final): `grep -ciE 'revision|cleanup|fix|\bML\b' docs/manuscript/id-vs-ref-LD.md` → MUST not exceed T1-baseline
  </verify>
  <done>
    Residual sweep returns 0 unexpected hits; 4 critical section anchors present; L128 alignment holds; honest-framing-lock unbroken. Commit only if residuals were corrected.
  </done>
  <commit_message>
    docs(quick-260503-vcl, T5): complete final residual sweep on id-vs-ref-LD.md (residuals captured + corrected; section anchors intact)
    [SKIP COMMIT IF SWEEP CLEAN — note in chat report only]
  </commit_message>
</task>

<task task_id="T6-pass-6" type="auto">
  <name>Pass 6 — Bundle regenerate + 11-step verify + STATE.md frontmatter bump</name>
  <files_to_modify>
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip
    - .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv
    - .planning/STATE.md
  </files_to_modify>
  <action>
    (a) Invoke builder: `bash bin/build_id_vs_ref_ld_submission_bundle.sh`. Expect exit 0; expect HTML render path (per W7-260503-kfq baseline — all 5 PDF engines absent, RENDER_PATH=html:pandoc-fallback).
    (b) Confirm internal 11-step verification reports all PASS (script's own checker; capture pass/fail per step in chat report).
    (c) Capture new sha256 + file count + build_at_iso to `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv` (overwrite existing manifest with new values; preserve schema).
    (d) Verify Stage 2 md5 invariant — 3 SH2B3 anchor `.fit.rds` md5s MUST remain preserved:
        - bmi.EUR `.fit.rds` md5 = `462ada6a...`
        - hypertension.EUR `.fit.rds` md5 = `8255c1ac...`
        - stroke.EUR `.fit.rds` md5 = `a041eecc...`
        Use HARD FAIL semantics per W7-260503-kfq checker iter 1 WARNING 4.
    (e) Verify NEW sha256 differs from baseline `10bd7bc9537aa23463014250717c3f3e26714092fb4593aa93ab8222391b0cc7` (Pass 1-5 changed manuscript content → bundle hash MUST change).
    (f) STATE.md frontmatter atomic update: bump `last_updated` and `last_activity` to Pass 6 commit time (UTC ISO8601 for last_updated; YYYY-MM-DD for last_activity). Per `feedback_state_md_keep_current` — write STATE.md as part of this atomic commit, do not defer.
    Per `feedback_multi_terminal_staging`: stage with explicit `git add` of the 3 paths above only — NEVER `-A` or `.`.
    Stop after this pass + chat report; do NOT push to remote.
  </action>
  <verify>
    1. Builder exit: `bash bin/build_id_vs_ref_ld_submission_bundle.sh; echo "exit=$?"` → exit=0
    2. Bundle exists: `test -f .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`
    3. New sha256 captured: `sha256sum .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip` → record value, MUST != `10bd7bc9537aa23463014250717c3f3e26714092fb4593aa93ab8222391b0cc7`
    4. Manifest updated: `grep -c '^sha256\b' .planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/bundle_manifest.tsv` → ≥1; new sha256 value present
    5. SH2B3 md5 invariant: extract bundle, compute md5sum on the 3 SH2B3 .fit.rds files, confirm prefixes `462ada6a` / `8255c1ac` / `a041eecc` (HARD FAIL if any drift)
    6. STATE.md frontmatter: `head -20 .planning/STATE.md | grep -E 'last_updated|last_activity'` → both fields show today's date (2026-05-03) with last_updated bumped to Pass 6 commit time
    7. Git staging check before commit: `git diff --cached --name-only` → MUST list exactly the 3 paths above (no surprise additions from `-A` regression)
  </verify>
  <done>
    Bundle regenerated with new sha256 (different from 10bd7bc9537a... baseline); 11-step internal verification all PASS; SH2B3 anchor md5 invariant preserved (HARD FAIL semantics held); bundle_manifest.tsv updated with new values; STATE.md frontmatter atomically refreshed; explicit-path staging held; ready for Carter to scp `id_vs_ref_ld_genome_medicine_submission.zip` to local; NO push.
  </done>
  <commit_message>
    feat(quick-260503-vcl, T6): regenerate id-vs-ref-LD Genome Medicine bundle (new sha256 post-Pass1-5 alignment) + bundle_manifest.tsv + STATE.md last_updated bump
  </commit_message>
</task>

</plan>

## Halt Conditions (explicit)

| ID | Trigger | Action |
|----|---------|--------|
| pass-3-bibliography-unresolvable | ≥5 of unnamed ref slots (1-3, 6-10, 11-12, 17-19, 27) cannot be confidently assigned via WebSearch + inline context | STOP execution. Do NOT commit Pass 3. Chat-report unresolvable slot list with 5-lines-before/after inline-context excerpts. Carter approves missing refs manually rather than guessing them into peer-reviewed submission. Per `feedback_rigor_over_speed`. |
| stage-2-md5-drift | Any of 3 SH2B3 anchor .fit.rds md5s drift from `462ada6a` / `8255c1ac` / `a041eecc` after Pass 6 bundle rebuild | STOP execution. HARD FAIL semantics per W7-260503-kfq checker iter 1 WARNING 4. Investigate before any commit. |
| honest-framing-lock-break | Token count of `revision|cleanup|fix|\bML\b` in manuscript prose, commit messages, or new amendment trail headers EXCEEDS pre-pass baseline | STOP execution. Per `feedback_original_research_framing`: all public artifacts must frame coloc_analysis as hypothesis-driven original research. Identify offending insertion, replace with `lock`/`align`/`complete`/`consolidate`/`compile` synonyms before re-attempting commit. |
| multi-terminal-staging-violation | Any commit's `git diff --cached --name-only` includes paths NOT in the task's `files_to_modify` list (`-A` / `.` regression) | STOP execution. Per `feedback_multi_terminal_staging`: 2026-04-28 collision baked the rule. Reset stage, redo with explicit `git add <path>` only. |

## Constraint Compliance Self-Check

- [ ] **original_research_framing**: All 6 commit messages use `feat`/`docs` + neutral verbs (`align`, `lock`, `compile`, `consolidate`, `complete`, `regenerate`, `bump`). NO `revision`/`cleanup`/`fix`/`ML` in any commit message draft above. Verified.
- [ ] **multi_terminal_staging**: Each task's `files_to_modify` list is explicit; T6 verify step #7 explicitly checks `git diff --cached --name-only` matches the 3 paths only. No `-A` or `.` anywhere in any task action.
- [ ] **rigor_over_speed**: Pass 3 halt condition forbids guessing missing refs into peer-reviewed submission; explicit DOI-pinning + double-source verification mandate per task action body.
- [ ] **state_md_keep_current**: T6 atomically bumps STATE.md frontmatter `last_updated` + `last_activity` as part of the Pass 6 commit (not deferred to a later pass).

## Stop-After Condition

After T6 chat report (with new sha256, file count, build_at_iso, 11-step verification per-step results, SH2B3 md5 invariant confirmation), STOP. Do NOT push to remote. Carter scp's `id_vs_ref_ld_genome_medicine_submission.zip` from `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/` to local machine for *Genome Medicine* submission portal upload.
