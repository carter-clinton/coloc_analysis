---
phase: quick-260423-nzu
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - bin/fire_phase2_stage2_refit.sh
  - bin/followup_phase2_stage2_aggregators.sh
  - .claude/settings.json
  - .planning/STATE.md
  - .planning/phases/03-mendelian-randomization/
  - .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md
autonomous: true
requirements:
  - QUICK-260423-NZU-01
  - QUICK-260423-NZU-02
  - QUICK-260423-NZU-03
must_haves:
  truths:
    - "bin/fire_phase2_stage2_refit.sh and bin/followup_phase2_stage2_aggregators.sh are tracked in git with an explanatory commit citing the 2026-04-22 Stage 2 fire (51/96 CS, 0 Tier A)."
    - ".claude/scheduled_tasks.lock remains untracked (runtime lock file, not committed)."
    - ".planning/STATE.md YAML front-matter reports status=post_pivot_m0_in_flight and milestone=m0-pivot-scaffolding."
    - ".planning/STATE.md body shows a fresh 'Current Position' block summarizing the pivot + Stage 2 numbers + Tracks A/B + Routes A+B+C+D."
    - "Pre-pivot Session Continuity entries still exist under an '### Archived sessions (pre-pivot)' footer in STATE.md (preserved, not deleted)."
    - "T1 spine completion narrative preserved as an '### Archived (pre-pivot — T1 spine completed; artifacts reusable per Amendment §8)' subsection."
    - ".planning/phases/03-mendelian-randomization/ no longer exists at the original path."
    - ".planning/phases/_archive/03-mendelian-randomization-pre-pivot/ exists and contains the 5 original PLAN.md files plus a new README.md explaining supersession by M5."
    - "git log --follow on any moved 03-0X-PLAN.md resolves back to its pre-move history (git mv, not cp+rm)."
    - "Working tree is clean after all three commits (modulo .claude/scheduled_tasks.lock which stays untracked)."
  artifacts:
    - path: ".planning/STATE.md"
      provides: "Post-pivot project state"
      contains: "post_pivot_m0_in_flight"
    - path: ".planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md"
      provides: "Supersession notice for 5 pre-pivot MR plans"
      contains: "superseded by M5"
    - path: "bin/fire_phase2_stage2_refit.sh"
      provides: "Stage 2 fire driver (now tracked)"
    - path: "bin/followup_phase2_stage2_aggregators.sh"
      provides: "Stage 2 aggregator driver (now tracked)"
  key_links:
    - from: ".planning/STATE.md body"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md"
      via: "relative markdown link or reference to the amendment's M0–M6 sequence"
      pattern: "PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe"
    - from: ".planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3"
      via: "prose reference citing M5 as the new home for classical MR"
      pattern: "M5"
---

<objective>
Post-pivot infrastructure hygiene: commit the two untracked Stage 2 helper scripts that produced the 2026-04-22 real-LD credible-set yield (51/96 CS, 0 Tier A, SH2B3 collapse), refresh STATE.md to reflect the adopted genome-wide reframe (M0 in-flight), and archive the 5 pre-pivot Phase 03 Mendelian randomization PLAN.md files as superseded by M5 (variant→gene prioritization) per the 2026-04-22 amendment. This is Step 0 (Route D) of the approved three-route parallel execution plan (`/home/ckclinto/.claude/plans/snappy-humming-pine.md`), unblocking subsequent Route A (Track A manuscript push) and Route B (Track B M0 closeout + OSF amendment) work.

Purpose: The repo tree currently mixes committed pivot scaffolding (6 amendment docs + Track A first-pass draft already landed) with two untracked scripts that ran on 2026-04-22 and a STATE.md whose front-matter still declares `status: recovery_stage_2_awaiting_fire` — a status the fire itself invalidated. Leaving this state in place means every subsequent resume routing (`/gsd-*` init scans) will misread the project as blocked on a fire that already ran, and the Phase 03 MR plans will continue to surface as "incomplete execution" warnings even though they have been semantically retired. A single hygiene pass clears all three mismatches.

Output:
  - One commit capturing the two Stage 2 driver scripts + the pending `.claude/settings.json` modification, with a message that records the 2026-04-22 fire numerics inline.
  - One commit rewriting `.planning/STATE.md` to the post-pivot state with both the T1 spine narrative and the pre-pivot Session Continuity history preserved as archival subsections.
  - One commit archiving the Phase 03 MR directory via `git mv` (history preserved) plus a new README explaining the supersession.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md
@/home/ckclinto/.claude/plans/snappy-humming-pine.md
@CLAUDE.md

<!-- Interfaces / key references the executor needs in hand -->
<interfaces>
Current git state (as of plan authorship, 2026-04-23):
```
 M .claude/settings.json
?? .claude/scheduled_tasks.lock    <-- DO NOT COMMIT (runtime lock)
?? bin/fire_phase2_stage2_refit.sh
?? bin/followup_phase2_stage2_aggregators.sh
```

Phase 03 directory contents (all 9 files move together via `git mv` of the parent dir):
```
.planning/phases/03-mendelian-randomization/
  03-01-PLAN.md
  03-02-PLAN.md
  03-03-PLAN.md
  03-04-PLAN.md
  03-05-PLAN.md
  03-CONTEXT.md
  03-DISCUSSION-LOG.md
  03-RESEARCH.md
  03-VALIDATION.md
```
All 9 files ride along with `git mv` of the parent directory — this is the desired behavior. The README in task 3 specifically enumerates the 5 PLANs as the superseded artifacts, but the supporting CONTEXT / RESEARCH / DISCUSSION-LOG / VALIDATION are also preserved for methodological reference (same reason — readable, not active).

STATE.md YAML front-matter (current, to be replaced):
```yaml
gsd_state_version: 1.0
milestone: v3.1.2
milestone_name: milestone
status: recovery_stage_2_awaiting_fire
stopped_at: "RECOVERY Stage 2 ... (pre-dates 2026-04-22 pivot)"
last_updated: "2026-04-21T23:50:00.000Z"
last_activity: 2026-04-21
progress:
  total_phases: 12
  completed_phases: 6
  total_plans: 30
  completed_plans: 30
  percent: 100
```

STATE.md YAML front-matter (target):
```yaml
gsd_state_version: 1.0
milestone: m0
milestone_name: m0-pivot-scaffolding
status: post_pivot_m0_in_flight
stopped_at: "M0 pivot scaffolding in flight: 6 amendment docs committed, sumstats v2 download driver + manifest committed, Track A first-pass draft committed (bde60e2). Stage 2 drivers + STATE.md refresh + Phase 03 archive committed by this hygiene pass. Remaining M0: PROJECT/ROADMAP/REQUIREMENTS/DECISIONS rewrites per Amendment §12 + OSF amendment posted (gates M2 per §9.1). Stage 2 production fire 2026-04-22 AM via bin/fire_phase2_stage2_refit.sh produced 51/96 real-LD credible sets (up from 12/96 identity-LD baseline), 0 Tier A, SH2B3 × asthma EUR identity-LD PP.H4=1.0 collapsed to n_cs_a=0 under real-LD — motivating pivot from candidate-locus design to genome-wide joint-signal discovery across 9 traits × 2 ancestries."
last_updated: "2026-04-23T21:15:00.000Z"
last_activity: 2026-04-23
progress:
  total_milestones: 7         # M0..M6
  completed_milestones: 0
  current_milestone: m0
  current_milestone_percent: 70
  percent: 10                 # M0 ~70% * 1/7 ≈ 10%
```
(If `gsd-tools` schema rejects the M0/M6 `progress` shape, fall back to keeping the legacy `total_phases / completed_phases / total_plans / completed_plans / percent` keys but set `total_phases: 7`, `completed_phases: 0`, `total_plans: 0`, `completed_plans: 0`, `percent: 10` — verify with `gsd-tools frontmatter validate`.)

Commit authorship: no `--no-verify`, no `--amend`, no push. HEREDOC for commit messages per GSD rules. Branch: main (GPFS project; `git.branching_strategy: none` per project config).

Known safe operations:
- `git add bin/fire_phase2_stage2_refit.sh bin/followup_phase2_stage2_aggregators.sh .claude/settings.json` (explicit file list — no `git add -A`)
- `git mv .planning/phases/03-mendelian-randomization .planning/phases/_archive/03-mendelian-randomization-pre-pivot`
- `git commit -m "$(cat <<'EOF' ... EOF)"` per GSD HEREDOC rule
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Commit Stage 2 driver scripts + .claude/settings.json delta</name>
  <files>bin/fire_phase2_stage2_refit.sh, bin/followup_phase2_stage2_aggregators.sh, .claude/settings.json</files>
  <action>
Commit the two untracked Stage 2 helper scripts and the pending `.claude/settings.json` modification as ONE commit. Do NOT edit the script contents — they are already annotated with the fire rationale (per constraints). Do NOT touch `.claude/scheduled_tasks.lock` (runtime lock file; ignore via explicit file-list staging).

Steps:
1. Verify the three target files are the only ones staged: run `git status --short` and confirm the expected three entries (`M .claude/settings.json`, `?? bin/fire_phase2_stage2_refit.sh`, `?? bin/followup_phase2_stage2_aggregators.sh`) plus the ignorable `?? .claude/scheduled_tasks.lock`.
2. Stage explicitly by name (NOT `git add -A` or `git add .` — per GSD safety protocol this prevents accidental lock-file inclusion):
   ```
   git add bin/fire_phase2_stage2_refit.sh bin/followup_phase2_stage2_aggregators.sh .claude/settings.json
   ```
3. Verify the staged set contains exactly those three files and excludes `.claude/scheduled_tasks.lock`:
   ```
   git diff --cached --name-only
   ```
   Expected output: exactly those three paths, no others.
4. Commit with HEREDOC:
   ```
   git commit -m "$(cat <<'EOF'
chore(infra): commit Stage 2 fire + aggregator drivers that produced 51/96 CS

Retroactive record of the two helper scripts used for the 2026-04-22 Phase 2
Stage 2 real-LD production fire:

- bin/fire_phase2_stage2_refit.sh — production re-fire driver (ran 10:26 UTC)
- bin/followup_phase2_stage2_aggregators.sh — aggregator follow-up (ran 20:02 UTC)

The fire produced 51/96 non-empty real-LD credible sets (up from 12/96 under
the identity-LD baseline, 4.25× yield), 0 Tier A signals, and the flagship
SH2B3 × asthma EUR identity-LD PP.H4=1.0 coloc collapsed to n_cs_a=0 under
real-LD. These quantitative outcomes motivated the 2026-04-22 genome-wide
reframe (Amendment §2.2).

.claude/settings.json carries a pre-existing pending modification rolled in
here to clear the working tree ahead of the STATE.md refresh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
   ```
5. Confirm `.claude/scheduled_tasks.lock` remains untracked after the commit:
   ```
   git status --short
   ```
   Expected: only `?? .claude/scheduled_tasks.lock` remains.
  </action>
  <verify>
    <automated>git log -1 --name-only HEAD | grep -E "^(bin/fire_phase2_stage2_refit\.sh|bin/followup_phase2_stage2_aggregators\.sh|\.claude/settings\.json)$" | wc -l   # expect 3</automated>
    <automated>git status --short | grep -v "^?? \.claude/scheduled_tasks\.lock$" | wc -l   # expect 0 (tree clean except the ignored lock)</automated>
    <automated>git ls-files bin/fire_phase2_stage2_refit.sh bin/followup_phase2_stage2_aggregators.sh | wc -l   # expect 2 (both tracked)</automated>
  </verify>
  <done>HEAD commit message starts with `chore(infra): commit Stage 2 fire + aggregator drivers that produced 51/96 CS`; commit touches exactly the three listed files; `.claude/scheduled_tasks.lock` remains untracked; no other working-tree changes accidentally included.</done>
</task>

<task type="auto">
  <name>Task 2: Refresh STATE.md to post_pivot_m0_in_flight</name>
  <files>.planning/STATE.md</files>
  <action>
Rewrite `.planning/STATE.md` to reflect the adopted 2026-04-22 pivot. Preserve all pre-pivot narrative as archival subsections — do NOT delete any existing history; the file is a cumulative ledger.

Structural edits:

1. **YAML front-matter** — replace with the "target" block shown in the `<interfaces>` section of this plan's `<context>`. Key changes:
   - `status: post_pivot_m0_in_flight` (was `recovery_stage_2_awaiting_fire`)
   - `milestone: m0` + `milestone_name: m0-pivot-scaffolding` (was `v3.1.2` / `milestone`)
   - `stopped_at:` rewritten to the M0 in-flight narrative (multi-line string OK — quote per current style)
   - `last_updated: "2026-04-23T21:15:00.000Z"` and `last_activity: 2026-04-23`
   - `progress` keys: prefer the M0–M6 shape from the `<interfaces>` target block; if `gsd-tools frontmatter validate .planning/STATE.md --schema state` rejects it, fall back to legacy-key shape (total_phases=7, completed_phases=0, total_plans=0, completed_plans=0, percent=10) and confirm `valid=true`.

2. **New `## Current Position` block** (replaces the existing `## Current Position` section wholesale — current content becomes archival, see step 4 below). Content to write:

   - One-sentence headline: project pivoted 2026-04-22 from candidate-locus design (50 hand-curated regions, circular per Amendment §2.3) to genome-wide joint-signal discovery across 9 traits × 2 ancestries (Amendment §§2, 4).
   - Stage 2 fire numerics block (bullet list):
     - 2026-04-22 AM production fire via `bin/fire_phase2_stage2_refit.sh` produced 51/96 non-empty real-LD credible sets (4.25× yield vs 12/96 identity-LD baseline).
     - 0 Tier A signals at genome-wide-significance thresholds.
     - Flagship SH2B3 × asthma EUR coloc: identity-LD PP.H4=1.0 → real-LD n_cs_a=0 (Benner 2017 identity-LD inflation, now demonstrated on a canonical-literature signal).
     - 861 hard failures in the pairwise trait-pair sweep (to be quantified in Track A frozen-numbers pass).
   - Two-track split (short paragraph):
     - Track A: short-form real-LD audit paper of candidate-locus design. Venue ladder Genome Medicine → AJHG short report → Bioinformatics Applications Note. First-pass draft landed 2026-04-23 (commit bde60e2) at `docs/manuscript/track_a_pivot.md`.
     - Track B: genome-wide 9-trait × 2-ancestry joint-signal discovery with MTAG + CPASSOC + HyPrColoc + PolyFun + AoU-controlled-tier AFR WGS LD panel. Target Nature Genetics. Planning lives under `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §§3, 5, 6, 7.
   - Three parallel routes (enumerated):
     - Route A — Track A manuscript push (freeze Tier counts → Section 4.1–4.20 edits → figures → bioRxiv).
     - Route B — M0 closeout: PROJECT.md / ROADMAP.md / REQUIREMENTS.md / DECISIONS.md rewrites per Amendment §12, then OSF amendment post (hard gate on M2 per Amendment §9.1).
     - Route C — Track B M1 sumstats upgrade: `bin/download_sumstats_v2.sh` scripted driver already running on URL-fetchable sources (Aragam2022, CKDGen2019, GLGC2021 landed); manual-fetch queue in `.planning/amendments/SUMSTATS-MANUAL-FETCH.md` awaits Carter portal actions.
     - Route D — this hygiene pass (Step 0; fills the gap between 2026-04-21 stale state and the pivot-era repo).
   - M0 progress status: ~70% complete. Done: this hygiene commit cluster + 6 amendment docs + sumstats driver + Track A first-pass. Outstanding: PROJECT/ROADMAP/REQUIREMENTS/DECISIONS rewrites + OSF amendment PDF posted.
   - Pointer line: `See .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3 for M0–M6 milestone sequence.`

3. **Preserve T1 spine narrative** — the existing "Phase 02 (3-way-qtl-colocalization) RECOVERY" + "T1 spine status" + "Recovery progress" + "Post-LSF fire decision matrix" + "Scope caveat for CP#1-final framing" content currently inside the old `## Current Position` block must be moved, not deleted, into a subsection below the new Current Position, headed:

   ```
   ### Archived (pre-pivot — T1 spine completed; artifacts reusable per Amendment §8)
   ```

   Prepend a one-line note above the archived content: "The following narrative reflects the project state immediately before the 2026-04-22 reframe. Phases 0/1/2/5/9 outputs are preserved and repurposed as Track A inputs + Track B candidate-locus validation subset per Amendment §8 — not discarded."

4. **Preserve Session Continuity entries** — the existing `## Session Continuity` block and all its dated subsections (`### This session (2026-04-20) — Resume routing + Option 1/2/3 chain`, `### Launch10-15 drain (2026-04-17 → 2026-04-19)`, `### T1 Phase 2 first-production debug (2026-04-20)`, `### Archived prior session (2026-04-17 PM) — Phase 3 planning commit`, `### Earlier sessions (archived for reference)`, `### Previous session (2026-04-16 PM) — T1 Production Bug-Fix Sprint (archived)`, `### Previous session (2026-04-15 PM)`, `### Earlier in this session (2026-04-15 AM)`, `### Earlier in this session (2026-04-14 PM)`, `### Finding 2026-04-14 PM — Phase 0 idempotency gap`, `### What landed during 2026-04-14 sessions`, etc.) must be preserved in full under a footer heading:

   ```
   ### Archived sessions (pre-pivot)
   ```

   Insert a one-line divider + preamble above the archived content: "All entries below pre-date the 2026-04-22 pivot. Retained for forensic traceability and because some procedural content (Phase 0 idempotency fixes, LDSC custom-LD-score fixes, env yml hardening) is still load-bearing on the T1 spine artifacts that Track A will cite."

5. **Append a new Session Continuity entry for 2026-04-22 + 2026-04-23** at the top of the (now mostly-archived) Session Continuity block, under a new heading:

   ```
   ### This session (2026-04-22 → 2026-04-23) — Pivot adoption + M0 scaffolding + hygiene
   ```

   Content (bullet list, concise):
   - 2026-04-22 AM: Stage 2 production fire via `bin/fire_phase2_stage2_refit.sh` (51/96 CS, 0 Tier A, SH2B3 collapse).
   - 2026-04-22: pivot adopted. 6 amendment docs authored under `.planning/amendments/` (PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe, TRACK-A-PIVOT, SUMSTATS-UPGRADE.md + .tsv, AOU-LD-PIPELINE, SUMSTATS-MANUAL-FETCH).
   - 2026-04-22 / 23: `bin/download_sumstats_v2.sh` driver + manifest committed (`cb2ed78`, `92a64ce`); Track A first-pass manuscript draft committed (`bde60e2`).
   - 2026-04-23: post-pivot hygiene via `/gsd-quick 260423-nzu` (this quick session) — Stage 2 drivers committed, STATE.md refreshed (this edit), Phase 03 MR plans archived.
   - Next: Route A (Track A manuscript edits + Tier-count freeze) in foreground; Route C (sumstats downloads) ticking in background; Route B (M0 closeout + OSF amendment) gated on Route A Tier-count freeze.

6. **Leave `## Performance Metrics`, `## Accumulated Context` (Decisions / Pending Todos / Blockers / Quick Tasks Completed), and `## Phase 0 Closeout Artifacts` blocks unchanged** — decisions ledger is cumulative and will get Track-B decisions appended in Route B (Step 3 of snappy-humming-pine.md, not this plan). Quick Tasks Completed table gets a new row appended for this hygiene pass:

   ```
   | 260423-nzu | Post-pivot hygiene: commit Stage 2 drivers, refresh STATE.md, archive Phase 03 MR plans | 2026-04-23 | (fill in HEAD SHA at commit time) | [260423-nzu-post-pivot-hygiene-commit-stage-2-driver](./quick/260423-nzu-post-pivot-hygiene-commit-stage-2-driver/) |
   ```

   Leave the commit-SHA column as a placeholder literal `_see-commit_` — it will be filled by the execute-phase summary writer. Don't block the commit on SHA resolution.

After edits:
- Run `node $HOME/.claude/get-shit-done/bin/gsd-tools.cjs frontmatter validate .planning/STATE.md --schema state` (fall through to legacy-shape fallback if schema rejects the M0 keys — document the fallback choice in the commit message).
- Commit with HEREDOC:
  ```
  git add .planning/STATE.md
  git commit -m "$(cat <<'EOF'
docs(state): refresh STATE.md to post_pivot_m0_in_flight — Stage 2 fire complete (51/96 CS), pivot adopted

YAML front-matter:
- status: recovery_stage_2_awaiting_fire → post_pivot_m0_in_flight
- milestone: m0-pivot-scaffolding (was v3.1.2)
- last_updated / last_activity bumped to 2026-04-23
- progress reset to M0–M6 shape (M0 ~70% complete)

Body:
- New "Current Position" block summarizing 2026-04-22 pivot, Stage 2 numerics
  (51/96 CS, 0 Tier A, SH2B3 identity-LD → real-LD collapse), two-track split
  (Track A short-form real-LD audit + Track B genome-wide 9-trait discovery),
  and four parallel routes (A + B + C + D).
- T1 spine completion narrative preserved verbatim under "### Archived (pre-pivot —
  T1 spine completed; artifacts reusable per Amendment §8)".
- Pre-pivot Session Continuity entries preserved verbatim under
  "### Archived sessions (pre-pivot)".
- New 2026-04-22 → 2026-04-23 Session Continuity entry added at top describing
  pivot adoption, M0 scaffolding, hygiene commits.
- Quick Tasks Completed row added for 260423-nzu.

Authoritative pivot charter: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
  ```
  </action>
  <verify>
    <automated>grep -m1 "^status: post_pivot_m0_in_flight" .planning/STATE.md   # present in front-matter</automated>
    <automated>grep -m1 "^milestone_name: m0-pivot-scaffolding" .planning/STATE.md   # present in front-matter</automated>
    <automated>grep -m1 "last_activity: 2026-04-23" .planning/STATE.md   # date bumped</automated>
    <automated>grep -c "### Archived (pre-pivot — T1 spine completed" .planning/STATE.md   # expect >= 1</automated>
    <automated>grep -c "### Archived sessions (pre-pivot)" .planning/STATE.md   # expect >= 1</automated>
    <automated>grep -c "### This session (2026-04-22 → 2026-04-23)" .planning/STATE.md   # expect >= 1</automated>
    <automated>grep -c "51/96" .planning/STATE.md   # Stage 2 numerics preserved in the new block</automated>
    <automated>grep -c "PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe" .planning/STATE.md   # amendment pointer present</automated>
    <automated>grep -c "Recovery trigger" .planning/STATE.md   # T1 recovery narrative preserved under archive</automated>
    <automated>grep -c "Launch10-15 drain" .planning/STATE.md   # pre-pivot session entry preserved</automated>
    <automated>git log -1 --format=%s HEAD | grep -q "docs(state): refresh STATE.md to post_pivot_m0_in_flight"</automated>
    <automated>node $HOME/.claude/get-shit-done/bin/gsd-tools.cjs frontmatter validate .planning/STATE.md --schema state 2>&1 | grep -E '"valid":\s*true' || echo "LEGACY_FALLBACK_NEEDED"</automated>
  </verify>
  <done>STATE.md front-matter declares `post_pivot_m0_in_flight` + `m0-pivot-scaffolding` + `2026-04-23` timestamps; body has a new Current Position block citing 51/96 CS + Tracks A/B + 4 routes; T1 spine narrative preserved under an Archived subsection; pre-pivot Session Continuity preserved under an Archived sessions footer; new 2026-04-22 → 2026-04-23 Session Continuity entry appended at top; `gsd-tools frontmatter validate` returns valid=true (M0 shape or legacy fallback); commit `docs(state): refresh STATE.md to post_pivot_m0_in_flight — Stage 2 fire complete (51/96 CS), pivot adopted` landed on main.</done>
</task>

<task type="auto">
  <name>Task 3: Archive pre-pivot Phase 03 MR plans as superseded by M5</name>
  <files>.planning/phases/03-mendelian-randomization/ (→ moved), .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md (new)</files>
  <action>
Archive the entire pre-pivot Phase 03 directory — 5 PLAN.md files + 4 supporting docs (03-CONTEXT.md, 03-DISCUSSION-LOG.md, 03-RESEARCH.md, 03-VALIDATION.md) — to the `_archive/` tree using `git mv` to preserve per-file history. Add a README.md that explains the supersession.

Steps:

1. Create the archive parent directory (only if it doesn't already exist) and perform the directory-level `git mv`:
   ```
   mkdir -p .planning/phases/_archive
   git mv .planning/phases/03-mendelian-randomization .planning/phases/_archive/03-mendelian-randomization-pre-pivot
   ```
   A directory-level `git mv` preserves history for every contained file (equivalent to `git mv` on each file individually but atomic). Verify with `git status`:
   ```
   git status --short
   ```
   Expected: 9 renamed entries (R  .planning/phases/03-mendelian-randomization/... → .planning/phases/_archive/03-mendelian-randomization-pre-pivot/...) plus potentially one untracked lock file. NO deletions (D) expected — `git mv` stages renames, not delete+add.

2. Write the README at the new archive path. Use the `Write` tool with absolute path `.planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md` and the following content (verbatim, including the front matter and the 4-point structure specified in task_boundary):

   ```markdown
   ---
   archived: true
   archived_date: 2026-04-23
   archival_reason: superseded-by-m5
   original_path: .planning/phases/03-mendelian-randomization/
   new_home_reference: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3 M5
   authored_pre_pivot: 2026-04-17
   ---

   # Phase 03 Mendelian Randomization — Archived pre-pivot

   ## Status

   **Archived.** The 5 plans in this directory (`03-01-PLAN.md` through `03-05-PLAN.md`) and their 4 supporting documents (`03-CONTEXT.md`, `03-DISCUSSION-LOG.md`, `03-RESEARCH.md`, `03-VALIDATION.md`) were authored on 2026-04-17 under the pre-pivot candidate-locus scope, which was abandoned on 2026-04-22. These plans are preserved for methodological reference and historical completeness — they are not active work.

   ## Why

   1. **Pre-pivot authorship.** All 5 PLAN.md files were drafted 2026-04-17 as Phase 03 of the T1/T2/T3 tier structure that preceded the 2026-04-22 genome-wide reframe. That tier structure has been retired.

   2. **Classical bidirectional MR folded into M5.** Under the adopted milestone sequence (M0–M6 per `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3), classical bidirectional Mendelian randomization is no longer a standalone phase. It is one axis of **M5 — variant→gene prioritization + novelty cross-reference**, alongside L2G (Open Targets), eQTL/pQTL coloc refresh, Borzoi variant-effect scoring, and the 5-class novel-variant cross-reference pipeline (§7). M5's MR component inherits the methods stack from these archived plans (TwoSampleMR, MR-PRESSO, Steiger filtering, hyprcoloc-adjacent two-sample coloc) but operates on the genome-wide region list produced by M2 (LDSC+MTAG+CPASSOC), not on the 50 candidate loci these plans targeted.

   3. **Fresh M5 plans will be drawn at M5 kickoff.** When the M5 slot opens (estimated 2027-02 per Amendment §11 timeline), a new `.planning/phases/` directory will be created under a name aligned with the M0–M6 convention (e.g., `.planning/phases/M5-variant-gene-prioritization/`). The M5 planning cycle will cite these archived plans as prior art, but will not reuse them verbatim — the scope change from 50 candidate loci to genome-wide Tier A coloc signals + AFR-specific credible sets changes the instrument-variant selection logic, the population-stratification guards, and the pleiotropy-sensitivity sweep substantially.

   4. **Content remains readable.** Nothing is deleted. All 9 files remain accessible at this archive path for (a) reviewing the pre-pivot MR methodology when drafting M5, (b) citation in the Track A manuscript if the candidate-locus MR framing is discussed as part of the superseded design, and (c) forensic traceability of the pivot decision itself. `git log --follow <filename>` resolves back to the pre-move history for every file.

   ## Original scope snapshot

   - Target: classical two-sample + bidirectional MR across 5 trait pairs (bmi↔t2d, bmi↔hypertension, asthma↔stroke, plus permutations) within the 50 pre-registered candidate regions.
   - Methods stack: TwoSampleMR (inverse-variance weighted, MR-Egger, weighted median, weighted mode), MR-PRESSO for pleiotropy, Steiger directionality filtering, hyprcoloc as a pleiotropy-sanity secondary.
   - Instrument selection: genome-wide-significant SNPs from discovery sumstats within each candidate region, LD-clumped r² < 0.01.
   - 5 plans: 03-01 (instrument harvesting + harmonization), 03-02 (primary bidirectional MR), 03-03 (sensitivity + pleiotropy), 03-04 (hyprcoloc secondary), 03-05 (aggregation + validation per 03-VALIDATION.md contract).
   - Execution gate at authorship time: CP#1-final (T1 first-production Tier A resolution). That gate never cleared under the pre-pivot design — the 2026-04-22 Stage 2 real-LD fire resolved 0 Tier A and triggered the pivot instead.

   ## What replaces this

   `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3 (M5 row) describes the successor scope. Key differences relative to this archive:

   - **Scope**: genome-wide Tier A + AFR-specific signals from M4, not 50 candidate regions.
   - **MR as one axis among several**: L2G + eQTL/pQTL coloc + Borzoi + MR, with MR positioned as directional-evidence triangulation, not as the primary discovery engine.
   - **Novelty cross-reference integrated**: M5 cross-references Tier A coloc loci against locked exports of Pickrell 2016, Watanabe 2019 GWAS Atlas, Open Targets Genetics L2G top-3, GWAS Catalog, and ClinVar + PubMed for functional-mechanism novelty (Classes 4 + 5 per Amendment §7).
   - **Pre-registration**: M5's scope is covered by the forthcoming OSF amendment (posted end-of-M1 per Amendment §9.1), not by the original osf.io/pvb5j candidate-locus pre-reg.

   ## Pointers

   - Pivot charter: [../../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](../../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md)
   - M0–M6 roadmap summary: Amendment §3
   - Preserved artifacts manifest: Amendment §8
   - Track A (real-LD audit of candidate-locus claims): [../../../amendments/TRACK-A-PIVOT.md](../../../amendments/TRACK-A-PIVOT.md)
   - Session-continuity context for the 2026-04-22 pivot: `.planning/STATE.md` `### This session (2026-04-22 → 2026-04-23)` block.
   ```

3. Stage the new README and the renames together, then commit:
   ```
   git add .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md
   git status --short   # sanity-check: 9 renames (R) + 1 new file (A or ??), no D entries
   git commit -m "$(cat <<'EOF'
chore(planning): archive pre-pivot Phase 03 MR plans (superseded by M5)

The 5 Phase 03 Mendelian randomization plans (03-01 through 03-05) plus their
4 supporting docs (CONTEXT / DISCUSSION-LOG / RESEARCH / VALIDATION) were
authored 2026-04-17 under the pre-pivot candidate-locus scope. That scope was
abandoned 2026-04-22 when the Stage 2 real-LD production fire (51/96 CS, 0
Tier A, SH2B3 identity-LD → real-LD collapse) demonstrated the candidate-locus
design was circular by construction.

Under the adopted M0–M6 milestone sequence (Amendment §3), classical
bidirectional MR is folded into M5 (variant→gene prioritization) as one
axis of directional-evidence triangulation alongside L2G, eQTL/pQTL coloc,
Borzoi variant-effect scoring, and the 5-class novel-variant cross-reference
pipeline. Fresh M5 plans will be drawn at M5 kickoff (~2027-02 per Amendment
§11 timeline), citing these archived plans as prior art but not reusing them
verbatim — the scope change from 50 candidate loci to genome-wide Tier A +
AFR-specific signals changes the instrument-selection logic materially.

All 9 files preserved under .planning/phases/_archive/ via git mv — per-file
history is intact; git log --follow resolves across the rename. A new README
at the archive root explains the supersession and points to Amendment §3
and §8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
   ```

4. Post-commit sanity:
   ```
   ls .planning/phases/03-mendelian-randomization/ 2>&1   # expect: No such file or directory
   ls .planning/phases/_archive/03-mendelian-randomization-pre-pivot/ | wc -l   # expect: 10 (5 PLANs + 4 supporting + README)
   git log --follow --oneline .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-01-PLAN.md | wc -l   # expect: >= 2 (original authorship commit + this archive commit)
   ```
  </action>
  <verify>
    <automated>test ! -e .planning/phases/03-mendelian-randomization   # original path must not exist</automated>
    <automated>test -f .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-01-PLAN.md</automated>
    <automated>test -f .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-05-PLAN.md</automated>
    <automated>test -f .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-CONTEXT.md</automated>
    <automated>test -f .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-VALIDATION.md</automated>
    <automated>test -f .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md</automated>
    <automated>ls .planning/phases/_archive/03-mendelian-randomization-pre-pivot/ | wc -l   # expect 10</automated>
    <automated>grep -c "superseded by M5" .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md   # expect >= 1</automated>
    <automated>grep -c "PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe" .planning/phases/_archive/03-mendelian-randomization-pre-pivot/README.md   # expect >= 1</automated>
    <automated>git log --follow --oneline .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-01-PLAN.md | wc -l   # expect >= 2 (history preserved across rename)</automated>
    <automated>git log -1 --format=%s HEAD | grep -q "chore(planning): archive pre-pivot Phase 03 MR plans (superseded by M5)"</automated>
    <automated>git status --short | grep -v "^?? \.claude/scheduled_tasks\.lock$" | wc -l   # expect 0 (tree clean after all 3 commits)</automated>
  </verify>
  <done>Original `.planning/phases/03-mendelian-randomization/` path does not exist; all 9 pre-existing files live under `.planning/phases/_archive/03-mendelian-randomization-pre-pivot/` plus a new README.md; `git log --follow` on any moved file resolves to its pre-move history (proves git mv not cp+rm); README cites both "superseded by M5" and the amendment filename; commit message starts with `chore(planning): archive pre-pivot Phase 03 MR plans (superseded by M5)`; working tree clean modulo the untracked `.claude/scheduled_tasks.lock`.</done>
</task>

</tasks>

<verification>
End-to-end checks for the whole quick pass (after all 3 commits land):

1. **Git tree:**
   - `git status --short` returns at most the single untracked line `?? .claude/scheduled_tasks.lock`.
   - `git log --oneline -5` shows the three new commits at HEAD~2..HEAD with the expected subject lines in order:
     1. `chore(infra): commit Stage 2 fire + aggregator drivers that produced 51/96 CS`
     2. `docs(state): refresh STATE.md to post_pivot_m0_in_flight — Stage 2 fire complete (51/96 CS), pivot adopted`
     3. `chore(planning): archive pre-pivot Phase 03 MR plans (superseded by M5)`
   - (Commit 1 may land before or after commit 2 in time, but all three must be present at HEAD~2..HEAD with `bde60e2` as HEAD~3.)

2. **STATE.md coherence check:**
   - `head -20 .planning/STATE.md` shows the new front-matter (`status: post_pivot_m0_in_flight`, `milestone_name: m0-pivot-scaffolding`, `last_activity: 2026-04-23`).
   - `grep -c "51/96" .planning/STATE.md` returns >= 1.
   - `grep -c "Track A" .planning/STATE.md` returns >= 1.
   - `grep -c "Track B" .planning/STATE.md` returns >= 1.
   - `grep -c "PROJECT-AMENDMENT-2026-04-22" .planning/STATE.md` returns >= 1.
   - `grep -c "Archived (pre-pivot" .planning/STATE.md` returns >= 1 (T1 archive subsection).
   - `grep -c "Archived sessions (pre-pivot)" .planning/STATE.md` returns >= 1 (session archive footer).

3. **Phase 03 archival:**
   - `test ! -e .planning/phases/03-mendelian-randomization` passes.
   - `ls .planning/phases/_archive/03-mendelian-randomization-pre-pivot/ | wc -l` returns 10.
   - `git log --follow --oneline .planning/phases/_archive/03-mendelian-randomization-pre-pivot/03-01-PLAN.md | wc -l` returns >= 2 (history preserved).

4. **GSD init resume consistency (forward-looking):**
   - `node $HOME/.claude/get-shit-done/bin/gsd-tools.cjs init resume 2>&1 | grep -iE "(phase 03|mendelian|recovery_stage_2_awaiting_fire)" | wc -l` returns 0 — the stale-state warnings no longer surface.
   - `node $HOME/.claude/get-shit-done/bin/gsd-tools.cjs frontmatter validate .planning/STATE.md --schema state 2>&1 | grep -E '"valid":\s*true'` returns a match (or the legacy-shape fallback was used, also valid).

5. **Stage 2 driver scripts:**
   - `git ls-files bin/fire_phase2_stage2_refit.sh bin/followup_phase2_stage2_aggregators.sh | wc -l` returns 2.
   - `file bin/fire_phase2_stage2_refit.sh` still reports an executable shell script (content not mutated).
</verification>

<success_criteria>
- Three commits land on main (no push) in this working session, with the subject lines above, in any order:
  1. `chore(infra): commit Stage 2 fire + aggregator drivers that produced 51/96 CS`
  2. `docs(state): refresh STATE.md to post_pivot_m0_in_flight — Stage 2 fire complete (51/96 CS), pivot adopted`
  3. `chore(planning): archive pre-pivot Phase 03 MR plans (superseded by M5)`
- `.claude/scheduled_tasks.lock` is NEVER staged or committed.
- STATE.md preserves T1 spine narrative AND pre-pivot Session Continuity entries verbatim under clearly labeled Archived subsections — no history deleted.
- Phase 03 MR plans move via `git mv` (history preserved) with a README.md at the new archive root explaining supersession and pointing to Amendment §3 M5.
- Working tree is clean after the three commits modulo the untracked lock file.
- Subsequent `/gsd-*` init scans no longer surface `recovery_stage_2_awaiting_fire` or "Phase 03 incomplete execution" warnings.
</success_criteria>

<output>
After completion, create `.planning/quick/260423-nzu-post-pivot-hygiene-commit-stage-2-driver/260423-nzu-SUMMARY.md` with:
- Three commit SHAs (from `git log --oneline -3` after all commits land).
- STATE.md byte-size before/after and grep-counts for the key markers (`51/96`, `Track A`, `Track B`, `Archived (pre-pivot`).
- Post-move directory listing at `.planning/phases/_archive/03-mendelian-randomization-pre-pivot/` (10 files).
- Quick-tasks-completed row to append to STATE.md's `Quick Tasks Completed` table (with the HEAD-2 commit SHA of the STATE.md refresh commit, or HEAD of the archive commit, filled in — executor's choice, document in summary).
- Any deviations (e.g., `progress` key legacy fallback if gsd-tools schema rejected the M0 shape).
- Confirmation that Route A (Track A manuscript push per snappy-humming-pine.md Step 2) is now unblocked.
</output>
