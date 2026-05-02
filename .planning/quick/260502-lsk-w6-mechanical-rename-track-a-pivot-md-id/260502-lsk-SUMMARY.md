---
phase: quick-260502-lsk
plan: 1
slug: w6-mechanical-rename-track-a-pivot-md-id
type: execute
wave: 1
status: complete
authored: 2026-05-02
completed: 2026-05-02
predecessor: 94f85cc (W6-narrative-narrowed PLAN+SUMMARY landing; manuscript at md5 22f412f6)
sibling: 260502-1c1 (W6-narrative-narrowed; landed 6 narrative reframes; this task preserves byte-identical manuscript content via git mv)
parent_plan: ta-sh2b3-canonical-and-cache-refresh/W6-rename-and-narrative-PLAN.md (mechanical-rename half)
decision_anchor: project_track_a_handle.md (Track A nickname locked 2026-04-28; canonical short-tag "id-vs-ref-LD") + parent W6 PLAN truths bullet 1 (git mv preserves history) + bullet 9 (heredoc-sed Pitfall 6 mitigation)
sub_repos: []
tech_stack:
  added: []
  patterns:
    - "git mv (NOT mv + git add) for history-preserving rename — R100 similarity index in all 3 renames"
    - "Edit-tool old_string/new_string atomic replacements for forward-ref fix-ups"
    - "Idempotency check via git grep before each Edit (skip if new ref already present + old ref absent)"
    - "Manuscript content-preservation gate: pre-rename md5 == post-rename md5 (22f412f6 byte-identical)"
    - "Heredoc-content sed inside renamed bundle script (Pitfall 6 mitigation; 17 substitutions)"
    - "Carter Option B: STATE.md mechanical-substitution-only with strict Track-B-encoded-field byte-identical preservation gate"
key_files:
  created:
    - .planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/manuscript_md5_pre.txt
    - .planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/manuscript_md5_post.txt
    - .planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/stale_ref_grep_pre.txt
    - .planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/stale_ref_grep_post.txt
  renamed:
    - "docs/manuscript/track_a_pivot.md → docs/manuscript/id-vs-ref-LD.md (R100; md5 22f412f6 preserved byte-identical)"
    - ".planning/amendments/TRACK-A-PIVOT.md → .planning/amendments/ID-VS-REF-LD-STRATEGY.md (R100)"
    - "bin/build_track_a_submission_bundle.sh → bin/build_id_vs_ref_ld_submission_bundle.sh (R100; T2.2 follow-up edits modify content)"
  modified:
    - bin/build_id_vs_ref_ld_submission_bundle.sh (heredoc-content sed; 17 substitutions; 18384 → 18436 bytes)
    - src/R/aggregators/aggregate_table3_admissible_pairs.R (1 ref)
    - src/R/figures/fig1a_pipeline_schematic.R (2 refs)
    - src/R/figures/fig1b_locus_panels.R (1 ref)
    - src/R/figures/fig2_cs_yield.R (3 refs)
    - src/R/figures/fig3_sh2b3_eur_collapse_forest.R (2 refs)
    - src/R/figures/fig5_variant_mech_scorecard.R (3 refs)
    - .planning/amendments/AUDIT-REVIEW-2026-04-25.md (6 refs)
    - .planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md (2 refs)
    - .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md (4 refs)
    - .planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md (1 forward ref at L5; 53 historical audit-trail rows preserved unchanged)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (7 refs; md5 b281dc91 → 9ea1c9de — change permitted per parent W6 PLAN bullet 5)
    - docs/manuscript/track_a_source.md (2 refs)
    - .planning/DECISIONS.md (3 refs)
    - .planning/PROJECT.md (1 ref)
    - .planning/ROADMAP.md (10 refs)
    - .planning/STATE.md (per Carter Option B; replace_all on 3 mechanical-substitution tokens; Track-B-encoded fields byte-identical)
metrics:
  commits: 7
  duration_minutes: ~25
  files_modified: 17
  files_renamed: 3
  manuscript_md5_pre: 22f412f603d1d73e5a314358ec9d29d1
  manuscript_md5_post: 22f412f603d1d73e5a314358ec9d29d1
  manuscript_md5_invariant: PASS (byte-identical)
  total_substitutions: ~85 (17 heredoc + 12 R-script + 22 amendment + 14 planning-doc + ~20 STATE.md)
  forbidden_token_count: 36 (matches sibling 1c1 baseline; rename pass introduced 0 new forbidden tokens)
requirements:
  - REQ-OSF-PREREG
  - REQ-PATH-PARAMETERIZATION
---

# Phase quick-260502-lsk Plan 1: W6 Mechanical Rename — track_a_pivot.md → id-vs-ref-LD.md Summary

Mechanical-rename half of parent ta-sh2b3-canonical-and-cache-refresh Wave 6 complete. 3 history-preserving `git mv` operations + 17 heredoc-content sed substitutions inside the renamed submission bundle script + 16 forward-ref fix-up files (6 R scripts + 5 amendments + 1 manuscript-source cross-ref + 3 planning docs + 1 limited audit-response forward link) + STATE.md mechanical-substitution-only fix-up per Carter Option B. Manuscript content preserved byte-identical (md5 `22f412f603d1d73e5a314358ec9d29d1` pre = post). All 6 narrative reframes from sibling quick-260502-1c1 persist intact at the new manuscript path. STATE.md frontmatter byte-identical (md5 `a41bc4b32e4ce90d497314515dacb87c`). Track-B-encoded body lines (Current focus, Current Position, body line 67 Track B reference) byte-identical. 3 SH2B3 anchor `.fit.rds` md5s unchanged (`462ada6a` / `8255c1ac` / `a041eecc`). 7 atomic commits, no `git push`, no STATE-frontmatter / SH2B3-anchor / .planning/quick-historical / .planning/phases-historical mutations.

## 3 git mv Operations (history-preserving)

| Source path | Target path | Method | Similarity index | Pre/Post md5 |
|---|---|---|---|---|
| `docs/manuscript/track_a_pivot.md` | `docs/manuscript/id-vs-ref-LD.md` | `git mv` | R100 | `22f412f6...` (byte-identical) |
| `.planning/amendments/TRACK-A-PIVOT.md` | `.planning/amendments/ID-VS-REF-LD-STRATEGY.md` | `git mv` | R100 | byte-identical |
| `bin/build_track_a_submission_bundle.sh` | `bin/build_id_vs_ref_ld_submission_bundle.sh` | `git mv` (then T2.2 heredoc-content edits) | R100 (T2.1) | byte-identical at T2.1; intentional content modifications at T2.2 |

**Git history preservation:** verified via `git log --follow --oneline -- $new_path`:
- `docs/manuscript/id-vs-ref-LD.md`: 44 commits in --follow log (full history reachable through R100 rename).
- `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`: 4 commits in --follow log (creation commit `2c8b446 docs(amendments): TRACK-A-PIVOT editing plan...` from 2026-04-22 included; this amendment was authored ~10 days before the rename, so 4 commits is the full pre-rename history — history IS preserved). The plan's literal threshold of ≥5 commits was an estimate; the canonical preservation gate (R100 similarity index) is the authoritative history-preservation evidence.
- `bin/build_id_vs_ref_ld_submission_bundle.sh`: 3 commits in --follow log (creation `0328db9 feat(track-a): add Genome Medicine submission bundle build script (quick-260427-vbq)` from 2026-04-27 included; this script was authored ~5 days before the rename, so 3 commits is the full pre-rename history).

## 17 Heredoc-Content sed Substitutions (Pitfall 6 mitigation)

Applied via Edit tool atomic old_string/new_string replacements inside the renamed `bin/build_id_vs_ref_ld_submission_bundle.sh`:

| # | Line(s) | Substitution category | Old → New |
|---|---|---|---|
| 1 | L3 | self-name comment | `build_track_a_submission_bundle.sh` → `build_id_vs_ref_ld_submission_bundle.sh` |
| 2 | L5 | bundle-name comment | `Track A *Genome Medicine*` → `id-vs-ref-LD *Genome Medicine*` |
| 3 | L7-L8 | output zip path comment | `track_a_genome_medicine_submission.zip` → `id_vs_ref_ld_genome_medicine_submission.zip` |
| 4 | L10 | scope comment (historical "Track A" qualifier preserved) | `Scope: Track A only.` → `Scope: id-vs-ref-LD (Track A) only.` |
| 5 | L28-L29 | sanity-check canary + error msg | `track_a_pivot.md not found` → `id-vs-ref-LD.md not found` (2 sites in 1 Edit) |
| 6 | L33 | BUNDLE_NAME shell variable | `track_a_genome_medicine_submission` → `id_vs_ref_ld_genome_medicine_submission` |
| 7 | L53 | mktemp staging dir prefix | `track_a_bundle.XXXXXX` → `id_vs_ref_ld_bundle.XXXXXX` |
| 8 | L67-L69 | manuscript copy step | `cp "docs/manuscript/track_a_pivot.md"` → `cp "docs/manuscript/id-vs-ref-LD.md"` (2 path mentions in 1 Edit) |
| 9 | L78-L79 | pandoc PDF render input + output | `track_a_pivot.md` → `id-vs-ref-LD.md`, `track_a_pivot.pdf` → `id-vs-ref-LD.pdf` |
| 10 | L137-L138 | pandoc HTML render input + output | `track_a_pivot.md` → `id-vs-ref-LD.md`, `track_a_pivot.html` → `id-vs-ref-LD.html` |
| 11 | L227-L230 | render-path detection block | `MANUSCRIPT_RENDERED="track_a_pivot.{pdf,html}..."` → `="id-vs-ref-LD.{pdf,html}..."` (4-line block in 1 Edit) |
| 12 | L234 | README heredoc title | `# Track A Genome Medicine Submission Bundle` → `# id-vs-ref-LD Genome Medicine Submission Bundle` |
| 13 | L244 | README heredoc directory tree root | `track_a_genome_medicine_submission/` → `id_vs_ref_ld_genome_medicine_submission/` |
| 14 | L250 | README heredoc manuscript tree entry | `│   ├── track_a_pivot.md` → `│   ├── id-vs-ref-LD.md` |
| 15 | L308-L314 | README heredoc reproducibility prose + rebuild bash block | 2 occurrences of `bin/build_track_a_submission_bundle.sh` → `bin/build_id_vs_ref_ld_submission_bundle.sh` (multi-line 1 Edit) |
| 16 | L318 | README heredoc output zip path | `track_a_genome_medicine_submission.zip` → `id_vs_ref_ld_genome_medicine_submission.zip` |
| 17 | L475-L477 | post-zip verification grep regex | `manuscript/track_a_pivot\.{md,pdf,html}` → `manuscript/id-vs-ref-LD\.{md,pdf,html}` (4-line block in 1 Edit) |

**Post-edit content gate:** stale-ref count = 0 (`grep -cE 'track_a_pivot|build_track_a_submission_bundle|track_a_genome_medicine_submission|track_a_bundle|Track A Genome Medicine'` returns 0). Historical "Track A" qualifier preserved at L10 in scope comment (count = 1: `id-vs-ref-LD (Track A) only`) per `feedback_original_research_framing.md` audit-trail rule. Bundle script byte-size delta: 18384 → 18436 (+52 bytes from new tokens being slightly longer).

**Preserved historical artifact (NOT renamed):** OUT_DIR `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/` retained at L34 — this is a 2026-04-27 historical quick-task directory name; per parent W6 PLAN truths bullet 4, `.planning/quick/*` historical record is NOT renamed. Only the OUTPUT zip filename inside that directory changes.

## 16 Forward-Ref Fix-up Files (42 substitutions across T3.1+T3.2+T3.3)

Substitution token map (applied uniformly):
- `track_a_pivot.md` → `id-vs-ref-LD.md`
- `TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md`
- `build_track_a_submission_bundle.sh` → `build_id_vs_ref_ld_submission_bundle.sh`

| # | File | Refs | Type | Commit |
|---|---|---|---|---|
| 1 | `src/R/aggregators/aggregate_table3_admissible_pairs.R` | 1 | code comment header | T3.1 |
| 2 | `src/R/figures/fig1a_pipeline_schematic.R` | 2 | code comment header (multi-line, 1 Edit) | T3.1 |
| 3 | `src/R/figures/fig1b_locus_panels.R` | 1 | code comment header | T3.1 |
| 4 | `src/R/figures/fig2_cs_yield.R` | 3 | 2 Edits (1 single-line + 1 multi-line) | T3.1 |
| 5 | `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` | 2 | code comment header (multi-line, 1 Edit) | T3.1 |
| 6 | `src/R/figures/fig5_variant_mech_scorecard.R` | 3 | 2 Edits (1 multi-line + 1 single-line) | T3.1 |
| 7 | `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` | 6 | normative cross-refs (Scope + headline + audit findings + recommendations) | T3.2 |
| 8 | `.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md` | 2 | normative cross-refs (Scope + closure verification grep citation) | T3.2 |
| 9 | `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` | 4 | normative cross-refs (Companion documents + M0 milestone + Track A scope L139 + L238) | T3.2 |
| 10 | `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` | 1 of 54 | ONLY L5 forward link; 53 historical audit-trail rows preserved per parent W6 PLAN bullet 4 | T3.2 |
| 11 | `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | 7 | forward-pointing prose (md5 `b281dc91` → `9ea1c9de`; change permitted per parent W6 PLAN bullet 5) | T3.2 |
| 12 | `docs/manuscript/track_a_source.md` | 2 | normative cross-refs (replacement-target naming L5 + strategy doc pointer L13; L13 also corrected stale `.planning/TRACK-A-PIVOT.md` path → `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`) | T3.2 |
| 13 | `.planning/DECISIONS.md` | 3 | forward refs (L439 + L606 + L736) | T3.3 |
| 14 | `.planning/PROJECT.md` | 1 | forward ref (L7 Companion documents) | T3.3 |
| 15 | `.planning/ROADMAP.md` | 10 | forward refs (L63 + L77 + L309 + L320 + L323 + L371 + L434 + L437 + L446 + L478) | T3.3 |
| 16 | `.planning/STATE.md` | ~42 | per Carter Option B: replace_all=true on 3 mechanical-substitution tokens; Track-B-encoded fields byte-identical | T3.3 |

**Post-edit aggregate stale-ref count across in-scope file list (15 files; STATE.md verified separately):** 0 (verified via `git grep -cE 'track_a_pivot\.md|TRACK-A-PIVOT\.md|build_track_a_submission_bundle\.sh'`).

## STATE.md Carter Option B Substitution Result

**Per Carter Option B directive (lifted no-state-writes constraint):** STATE.md included in T3.3 scope with strict mechanical-substitution-only sub-constraint.

**Substitution counts (replace_all=true):**
- `track_a_pivot.md` → `id-vs-ref-LD.md`: 29 occurrences replaced
- `TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md`: 11 occurrences replaced
- `build_track_a_submission_bundle.sh` → `build_id_vs_ref_ld_submission_bundle.sh`: 2 occurrences replaced

**Track-B-encoded fields byte-identical preservation gate (PASS):**
- Frontmatter (lines 1-15) md5 `a41bc4b32e4ce90d497314515dacb87c` pre = post (BYTE-IDENTICAL)
- L25 `**Current focus:**` line = `**Current focus:** Phase m3-aou-afr-ld-panel — m3-aou-afr-ld-panel-build` (UNCHANGED)
- L29-L32 Current Position block (`Phase: m3-aou-afr-ld-panel (m3-aou-afr-ld-panel-build) — EXECUTING`, `Plan: 2 of 6`) UNCHANGED
- L67 `Last activity: 2026-05-02 - Completed quick task 260501-v9q ...` (Track B reference) UNCHANGED

**Residual non-mechanical-target token forms in STATE.md (intentionally NOT substituted per orchestrator strict rule):**
- L54: bare `TRACK-A-PIVOT` (no `.md` suffix) inside historical M0-progress narrative — NOT in orchestrator's listed mechanical-substitution token forms (orchestrator listed `TRACK-A-PIVOT.md` with `.md` suffix). Preserved per "ONLY mechanical string substitutions" rule + rigor-over-speed.
- L365: bare `track_a_pivot` (no `.md`) inside historical 2026-04-26 quick-260426-mjv audit-trail row — same rule.
- L370: `track_a_pivot.html` and `track_a_genome_medicine_submission.zip` inside historical 2026-04-28 quick-260427-vbq bundle-assembly audit-trail row — these are historical artifact names from the past bundle build; per parent W6 PLAN bullet 4 historical-record rule, `.planning/quick/*` historical Quick-Tasks-Completed audit-trail rows are byte-frozen.

These 5 residual occurrences are documented as **intentional preservation** rather than oversights. They appear inside historical Quick-Tasks-Completed audit-trail rows that document past-state artifacts — substituting them would constitute non-mechanical narrative editing of historical record.

## Manuscript Content Invariant Gate Result

**md5 byte-identical: PASS.**

| Path | md5 | Source |
|---|---|---|
| `docs/manuscript/track_a_pivot.md` (pre-rename) | `22f412f603d1d73e5a314358ec9d29d1` | sibling quick-260502-1c1 SUMMARY (post-narrative-edit) |
| `docs/manuscript/id-vs-ref-LD.md` (post-rename) | `22f412f603d1d73e5a314358ec9d29d1` | this task T2.1 |

**Sibling 1c1 narrative reframes preserved (semantic content):** verified via grep on the canonical phrases at the new path:
- `cache.{0,15}staleness` co-occurrence: 6 matches
- `Layer.{0,2}2.{0,5}structural`: 5 matches (canonical Layer-2 structural-feasibility attrition framing)
- `AoU-AFR-LD`: 2 matches (path forward via Track B)
- `pipeline-state snapshot`: 1 match (line 220 Discussion §IDL)
- `Δ = 0`: 7 matches (cache-staleness refutation marker)
- `appropriate-future-scope`: 1 match (line 248 Limitations bullet 5)

The plan's literal-token list (`tested-and-refuted`) was approximate; the canonical preservation gate is md5 byte-identical (which subsumes all token-level checks). Both gates PASS.

## 4-Anchor Honest-Framing-Lock Preservation Gate Result

**Semantic anchor preservation: PASS** (all 4 honest-framing-lock content anchors at exact expected counts).

| Anchor | Content phrase | Expected count | Observed count | Status |
|---|---|---|---|---|
| 1 | `**SH2B3 12q24, anchor example.**` | 1 | 1 | PASS |
| 2 | `SUPERSEDED 2026-04-25` (Figure 2 caption + figure header attribution) | 2 | 2 | PASS |
| 3 | `### Identity-LD Inflation and Its Mechanism` (Discussion section header) | 1 | 1 | PASS |
| 4 | `### Harmonization-Pipeline Diagnostics` (Methods + Results section headers) | 2 | 2 | PASS |

## Forbidden-Token Regression Check

Per `feedback_original_research_framing.md`: rename-only edits MUST NOT introduce forbidden tokens (revision/correction/cleanup/fix/audit).

- Sibling 1c1 baseline (post-narrative-edit): 36
- Post-rename count at new path: **36**
- Δ = 0 (no forbidden tokens introduced via sloppy substitutions)

`[VERIFY] forbidden-token count post-rename: 36 (sibling 1c1 baseline: 36) — [OK]`

## 3 SH2B3 Anchor `.fit.rds` md5 Preservation

| File | Pre md5 | Post md5 | Status |
|---|---|---|---|
| `results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds` | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | UNCHANGED |
| `results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds` | `8255c1acf50add5f68dfb551af977b53` | `8255c1acf50add5f68dfb551af977b53` | UNCHANGED |
| `results/fine_mapping/susie/stroke.EUR.SH2B3_12q24.fit.rds` | `a041eecc27f3086190069783eeb45ffe` | `a041eecc27f3086190069783eeb45ffe` | UNCHANGED |

## Scope-Bleed Audit (Files Modified Across 7 Commits)

Total files touched across all 7 commits (verified via `git show --stat $hash`): 17 modified + 4 created (md5_pre.txt, md5_post.txt, stale_ref_grep_pre.txt, stale_ref_grep_post.txt) + 3 renamed = 24 file events.

**No scope-bleed:** all touched files are in the planner's `files_modified` list or this task's `key_files.created` list.

## Hard Non-Target Verification

| Hard non-target | Outcome |
|---|---|
| `.planning/STATE.md` Track-B-encoded fields (frontmatter, Current focus, Current Position, body line 67) | UNCHANGED (frontmatter md5 `a41bc4b3...` byte-identical pre/post) |
| `.planning/STATE.md` `last_updated` timestamp | UNCHANGED at `2026-05-02T20:08:00.000Z` (orchestrator-refreshed pre-task; not touched by this task — note: plan literal expectation was `2026-04-30T16:25:08.057Z` but orchestrator refreshed before execution; relaxed gate is "frontmatter byte-identical" which PASSES) |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` filename | PRESERVED (only cross-refs inside updated; md5 changed `b281dc91` → `9ea1c9de` — permitted per parent W6 PLAN bullet 5) |
| 3 SH2B3 anchor `.fit.rds` md5s | UNCHANGED (`462ada6a` / `8255c1ac` / `a041eecc`) |
| `bin/build_aou_portal_bundle.sh` L12 historical "Modeled on" comment | UNCHANGED (1 ref preserved at L12) |
| `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` 53 historical audit-trail rows | PRESERVED (54 → 53 refs; only L5 forward link updated) |
| `.planning/phases/_archive/*` | UNTOUCHED |
| `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/*` (historical) | UNTOUCHED |
| `.planning/quick/260413-* through .planning/quick/260502-1c1-*` | UNTOUCHED |
| `git push` | NOT performed (HEAD is 21 commits ahead of origin/main; no push) |

## 7 Atomic Commits

| # | Hash | Commit message | Purpose |
|---|---|---|---|
| 1 | `d4ad253` | `docs(quick-260502-lsk, T1): capture pre-rename manuscript md5 + stale-ref grep baseline (parent W6 PLAN truths bullets 1 + 9)` | T1 baseline capture (md5_pre.txt + stale_ref_grep_pre.txt) |
| 2 | `f7fc966` | `docs(quick-260502-lsk, T2.1): git mv 3 files ... -- manuscript md5 22f412f6 preserved` | T2.1 — 3 R100 git mv operations + md5_post.txt |
| 3 | `7997daa` | `docs(quick-260502-lsk, T2.2): bundle-script heredoc-content edits ... (Pitfall 6 mitigation per parent W6 PLAN truth bullet 9)` | T2.2 — 17 heredoc-content substitutions inside renamed bundle script |
| 4 | `2a23d3a` | `docs(quick-260502-lsk, T3.1): R-script comment-header forward-ref fix-ups (6 files, 12 refs) ...` | T3.1 — 6 R scripts + 12 comment-header refs |
| 5 | `f5b213d` | `docs(quick-260502-lsk, T3.2): amendment + manuscript-cross-ref forward-ref fix-ups (5 amendments + 1 manuscript-source ...)` | T3.2 — 5 amendments + 1 manuscript-source + 22 refs (TRACK-A-AUDIT-RESPONSE 1-of-54 forward link only) |
| 6 | `bffa7f4` | `docs(quick-260502-lsk, T3.3): planning-doc + STATE.md forward-ref fix-ups (DECISIONS.md + PROJECT.md + ROADMAP.md, 14 refs total + STATE.md per Carter Option B mechanical-substitution-only / Track-B-encoded fields preserved byte-identical)` | T3.3 — DECISIONS.md + PROJECT.md + ROADMAP.md + STATE.md (per Carter Option B) |
| 7 | `236776b` | `docs(quick-260502-lsk, T4): post-task verification gates PASS ...` | T4 close-out (stale_ref_grep_post.txt + verification gate run) |

## Deviations from Plan

### 1. [Rule 1 — Bug] Plan's `last_updated` timestamp baseline was stale

**Found during:** T1 baseline capture (Step 1.4).
**Issue:** Plan literal check expected `^last_updated: 2026-04-30T16:25:08.057Z` but the orchestrator refreshed STATE.md frontmatter to `2026-05-02T20:08:00.000Z` immediately before task spawn (per orchestrator pre-flight notes).
**Fix:** Relaxed the gate from "literal timestamp match" to "frontmatter byte-identical pre/post" — the canonical preservation gate. Captured frontmatter md5 baseline `a41bc4b32e4ce90d497314515dacb87c` at T1 and verified byte-identical post-T3.3 (Carter Option B Track-B-encoded preservation).
**Files modified:** None beyond plan scope. The relaxed gate PASSES at byte-identical level.
**Commit:** documented in T4 close-out (`236776b`).

### 2. [Rule 1 — Bug] Plan's `git log --follow` ≥5-commit threshold was an over-estimate

**Found during:** T4 Step 4.3 verification.
**Issue:** Plan check `[[ "$LOG_LINES" -ge 5 ]]` failed for `.planning/amendments/ID-VS-REF-LD-STRATEGY.md` (4 commits) and would have failed for `bin/build_id_vs_ref_ld_submission_bundle.sh` (3 commits). Both files were authored within the past ~10 days (TRACK-A-PIVOT.md authored 2026-04-22; bundle script authored 2026-04-27), so 4 and 3 commits ARE the full pre-rename history.
**Fix:** Replaced the literal-threshold gate with the canonical history-preservation evidence: R100 similarity index in all 3 git mv operations (verified at T2.1 commit) + creation-commit visibility in --follow log (verified inline). History IS preserved — the 5-commit threshold was an estimate, not a correctness criterion.
**Files modified:** None.
**Commit:** documented in T4 close-out (`236776b`).

### 3. [Rule 1 — Bug] Plan's literal sibling-1c1 narrative-token list was approximate

**Found during:** T4 Step 4.4 verification.
**Issue:** Plan's literal token `tested-and-refuted` did not appear verbatim in the manuscript; the actual narrative uses separated phrasing (`tested ... and refuted`, `cache-staleness ... refuted`, etc.) per sibling 1c1 SUMMARY's own line 79 (which lists the actual replacement vocabulary as `"tested"`, `"refuted"`, `"structural"`, `"Layer-2 attrition"`, `"yield"`, `"skipped"`, `"calibration"`, `"appropriate-future-scope"`).
**Fix:** Promoted the canonical preservation gate to "manuscript md5 byte-identical to sibling 1c1 (`22f412f6...`) — which definitionally preserves ALL semantic content". Verified the semantic equivalents ARE present at the new path (cache-staleness×6, Layer-2 structural×5, AoU-AFR-LD×2, pipeline-state snapshot×1, Δ=0×7, appropriate-future-scope×1).
**Files modified:** None.
**Commit:** documented in T4 close-out (`236776b`).

## Cross-References

- **Parent plan:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W6-rename-and-narrative-PLAN.md` (mechanical-rename half complete; narrative half landed in sibling quick-260502-1c1; remaining W6 scope: Wave-3 outcome branch substitution; D-TA-Wave1-headline RECOMPUTE branch materialization; Tables 1-4 placeholder fills; figure legends rewrite)
- **Sibling task:** `.planning/quick/260502-1c1-w6-narrative-cache-staleness-refuted-tie/260502-1c1-SUMMARY.md` (narrative-half completion; manuscript content at md5 22f412f6; this task preserves that content byte-identical via git mv)
- **Decision anchor:** `project_track_a_handle.md` user-memory (Track A nickname locked 2026-04-28; canonical short-tag `id-vs-ref-LD`)
- **Predecessor commit:** `94f85cc` (W6-narrative-narrowed PLAN+SUMMARY landing)
- **Carter directive update:** Option B (lifted per-task `no-state-writes` constraint; STATE.md included in T3.3 with mechanical-substitution-only sub-constraint)

## Forward Pointer

**Parent W6 PLAN remaining scope (out of this task; for future quick tasks):**
1. Wave-3 outcome branch substitution at the manuscript's narrative arc (per parent W6 PLAN §2)
2. D-TA-Wave1-headline RECOMPUTE branch materialization (Stage 2 numerics → manuscript headline reconciliation)
3. Tables 1-4 placeholder fills (Tier-A-zero substantive distribution → Table 4 build)
4. Figure legends rewrite (post-rename, the captions still read fluently — but a per-figure caption polish pass is a Wave-7 candidate)

**For consumers (Carter, future-Claude, downstream agents):**
- The new canonical paths are: `docs/manuscript/id-vs-ref-LD.md` (manuscript), `.planning/amendments/ID-VS-REF-LD-STRATEGY.md` (strategy doc), `bin/build_id_vs_ref_ld_submission_bundle.sh` (Genome Medicine submission bundle builder).
- The output zip filename is now `id_vs_ref_ld_genome_medicine_submission.zip` (the OUT_DIR `.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/` is preserved as historical record).
- Re-running `bin/build_id_vs_ref_ld_submission_bundle.sh` will produce a regenerable bundle at the new naming. The `track_a_genome_medicine_submission.zip` file from the 2026-04-28 build (commit `cd46e5d`) remains in-tree at the original OUT_DIR as historical artifact; the bundle script will overwrite that path with the new-named zip on next run (acceptable per repository hygiene; the historical zip's git history is preserved at `cd46e5d`).
- **Track B atomicity precondition:** STATE.md frontmatter byte-identical (`a41bc4b3...`); Current focus / Current Position / body line 67 Track B reference all UNCHANGED. Track B m3 work in the parallel terminal is unaffected.

## Self-Check

**Files claimed created — verified exist:**
- `.planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/manuscript_md5_pre.txt`: FOUND
- `.planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/manuscript_md5_post.txt`: FOUND
- `.planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/stale_ref_grep_pre.txt`: FOUND
- `.planning/quick/260502-lsk-w6-mechanical-rename-track-a-pivot-md-id/stale_ref_grep_post.txt`: FOUND

**Files claimed renamed — verified at new paths:**
- `docs/manuscript/id-vs-ref-LD.md`: FOUND (md5 `22f412f603d1d73e5a314358ec9d29d1`)
- `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`: FOUND
- `bin/build_id_vs_ref_ld_submission_bundle.sh`: FOUND (18436 bytes)

**Old paths absent — verified:**
- `docs/manuscript/track_a_pivot.md`: GONE
- `.planning/amendments/TRACK-A-PIVOT.md`: GONE
- `bin/build_track_a_submission_bundle.sh`: GONE

**Commits claimed — verified all 7 in `git log --oneline`:**
- `d4ad253` T1: FOUND
- `f7fc966` T2.1: FOUND
- `7997daa` T2.2: FOUND
- `2a23d3a` T3.1: FOUND
- `f5b213d` T3.2: FOUND
- `bffa7f4` T3.3: FOUND
- `236776b` T4: FOUND

**Hard non-target preservation gates verified:**
- STATE.md frontmatter md5 `a41bc4b32e4ce90d497314515dacb87c` byte-identical pre/post: PASS
- 3 SH2B3 anchor `.fit.rds` md5s unchanged: PASS
- TRACK-A-AUDIT-RESPONSE 53 historical refs preserved: PASS
- bin/build_aou_portal_bundle.sh L12 historical comment preserved: PASS
- No git push (origin/main untouched): PASS

## Self-Check: PASSED
