---
quick_id: 260427-urj
slug: land-track-a-l3-banner-venue-lock-for-ge
phase: quick-260427-urj
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/manuscript/track_a_pivot.md
autonomous: true
requirements:
  - QUICK-260427-URJ-01
tags: [track-a, manuscript, venue-lock, genome-medicine, banner, atomic-edit]
must_haves:
  truths:
    - "Line 3 of docs/manuscript/track_a_pivot.md no longer reads 'First-pass application of `.planning/amendments/TRACK-A-PIVOT.md` to ...'."
    - "Line 3 of docs/manuscript/track_a_pivot.md states the manuscript is ready for *Genome Medicine* submission as an original research article (Option A venue-lock)."
    - "The L3 banner explicitly references the 5-figure main roster + Figs S1-S7 supplementary structure and the results/track_a_aggregations/ supplementary data path."
    - "The L3 banner notes that numeric placeholders were filled per quick-260427-e8n and that the remaining [EXTRACT: ...] at L355 (References) is venue-format-deferred."
    - "The L3 banner reaffirms 'bioRxiv preprint Day 1 regardless.'"
    - "Exactly one line in docs/manuscript/track_a_pivot.md changed (L3) — no whitespace drift, no other lines touched."
    - "git status preserves pre-existing dirty paths (.claude/settings.json, .planning/config.json, .claude/scheduled_tasks.lock) untouched."
    - "A single atomic commit landed with message 'docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)' staging only docs/manuscript/track_a_pivot.md."
  artifacts:
    - path: "docs/manuscript/track_a_pivot.md"
      provides: "Venue-locked L3 banner (Genome Medicine, Option A)"
      contains: "ready for *Genome Medicine* submission"
  key_links:
    - from: "docs/manuscript/track_a_pivot.md L3"
      to: "TRACK-A-PIVOT.md venue ladder (Genome Medicine -> AJHG -> Bioinformatics)"
      via: "explicit venue name + format declaration"
      pattern: "Genome Medicine.*original research article"
    - from: "docs/manuscript/track_a_pivot.md L3"
      to: "results/track_a_aggregations/ (quick-260427-e8n outputs)"
      via: "inline backtick path reference"
      pattern: "results/track_a_aggregations/"
    - from: "docs/manuscript/track_a_pivot.md L3"
      to: "quick-260427-e8n (placeholder-fill closure)"
      via: "explicit cross-reference to the placeholder-fill quick task"
      pattern: "quick-260427-e8n"
---

<objective>
Land the Track A L3 banner venue-lock for *Genome Medicine* (Option A). This is a single-line drop-in replacement of the stale "First-pass application..." banner at line 3 of `docs/manuscript/track_a_pivot.md`, replacing it with the venue-locked status line that reflects (a) Genome Medicine as primary venue with original-research-article format, (b) the 5-figure main roster + Figs S1-S7 supplementary structure, (c) the supplementary data path at `results/track_a_aggregations/`, (d) the placeholder-fill closure landed by quick-260427-e8n, and (e) the venue-format-deferred [EXTRACT: ...] still living at L355 (References). bioRxiv preprint Day 1 commitment is preserved verbatim.

Purpose: The L3 banner currently misrepresents the manuscript's submission readiness. Quick-260427-e8n closed out the numeric placeholder-fill (10 unique placeholders + L362-equivalent stale Decision item deletion + W7 invariant gates, commits 1ec07ca..5c23ec1). Quick-260427-azv landed the audit-v2 comparator-tightening and SH2B3 case study. The manuscript is now submission-ready against the TRACK-A-PIVOT.md venue ladder; the L3 banner must catch up. Carter signed off on Option A (Genome Medicine primary, no AJHG-style trim) in the orchestrator session 2026-04-27.

Output: A single atomic commit on `main` flipping L3 from the stale first-pass banner to the venue-locked status banner, with no other content drift.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@./CLAUDE.md
@docs/manuscript/track_a_pivot.md
@.planning/quick/260427-e8n-track-a-extract-placeholder-fill/260427-e8n-SUMMARY.md
@.planning/amendments/TRACK-A-PIVOT.md

<verbatim_anchors>
<!-- L3 banner exact-match anchors. The executor MUST treat these as byte-exact. -->
<!-- Confirmed against working tree at planning time (2026-04-27). -->

CURRENT L3 (verbatim, exactly one line, leading "> " blockquote prefix included):

> **Status:** First-pass application of `.planning/amendments/TRACK-A-PIVOT.md` to `docs/manuscript/track_a_source.md`. Narrative is complete; numeric placeholders marked `[EXTRACT: …]` must be filled from `results/` before preprint submission.

REPLACEMENT L3 (verbatim, exactly one line, leading "> " blockquote prefix included):

> **Status:** Research article ready for *Genome Medicine* submission (original research article format; 5-figure main roster + Figs S1–S7 supplementary; supplementary data at `results/track_a_aggregations/`). Numeric placeholders filled from `results/` per quick-260427-e8n; remaining `[EXTRACT: …]` at L355 (References) is venue-format-deferred. bioRxiv preprint Day 1 regardless.

CRITICAL FORMATTING NOTES:
- Both lines preserve the markdown blockquote prefix `> ` (greater-than + space).
- Both lines bold "Status:" via `**Status:**`.
- Both lines use the unicode horizontal ellipsis character `…` (U+2026), NOT three ASCII periods `...`. Confirm by `grep -c $'\xe2\x80\xa6' docs/manuscript/track_a_pivot.md` before/after.
- Replacement uses unicode en-dash `–` (U+2013) in `Figs S1–S7`, NOT ASCII hyphen-minus `-`.
- Replacement italicizes the venue: `*Genome Medicine*`.
- Replacement uses backticks for the inline path: `` `results/track_a_aggregations/` ``.
- L3 is a single physical line in the file (no soft wraps in the source).
</verbatim_anchors>

<must_not_touch>
The following pre-existing dirty paths in `git status` are out-of-scope for this quick task and MUST be preserved as-is. The executor must NEVER use `git add -A`, `git add .`, or `git add -u`. Only `git add docs/manuscript/track_a_pivot.md` is permitted.

- ` M .claude/settings.json`
- ` M .planning/config.json`
- `?? .claude/scheduled_tasks.lock`

After the commit, `git status` MUST still show all three of the above as dirty / untracked.
</must_not_touch>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Replace L3 banner with venue-locked Option A line and commit atomically</name>
  <files>docs/manuscript/track_a_pivot.md</files>
  <action>
Atomic single-line edit to flip the stale first-pass banner at L3 of `docs/manuscript/track_a_pivot.md` to the Option A Genome Medicine venue-lock banner.

Steps (run in order):

1. **Pre-flight verification (do NOT skip)** — confirm the working tree state and the exact L3 byte sequence before making any change:
   - `git rev-parse HEAD` and record the pre-edit HEAD SHA.
   - `git status --short` and confirm the only Track-A-relevant path is clean; confirm the three MUST-NOT-TOUCH paths from `<must_not_touch>` are present and exactly as listed (` M .claude/settings.json`, ` M .planning/config.json`, `?? .claude/scheduled_tasks.lock`).
   - `sed -n '3p' docs/manuscript/track_a_pivot.md` — confirm the printed line matches the CURRENT L3 from `<verbatim_anchors>` byte-for-byte.
   - `grep -c $'\xe2\x80\xa6' docs/manuscript/track_a_pivot.md` — record the pre-edit count of U+2026 horizontal ellipses (the current L3 contains exactly one; the replacement also contains exactly one, so this count must be unchanged after the edit).

2. **Apply the edit using the Edit tool** (NOT sed, NOT awk, NOT a heredoc-rewrite of the file — only the Edit tool with byte-exact `old_string` / `new_string`):

   - `old_string` = the CURRENT L3 from `<verbatim_anchors>`, including the leading `> ` blockquote prefix and the trailing newline implicit in single-line replacement (the Edit tool handles trailing newline preservation automatically; pass the line content only).
   - `new_string` = the REPLACEMENT L3 from `<verbatim_anchors>`, including the leading `> ` blockquote prefix.
   - Both strings use unicode `…` (U+2026) and the replacement uses unicode `–` (U+2013) in `Figs S1–S7`. Copy them verbatim from `<verbatim_anchors>` — do NOT retype.

3. **Post-edit byte-level verification:**
   - `sed -n '3p' docs/manuscript/track_a_pivot.md` — confirm the printed line matches the REPLACEMENT L3 byte-for-byte.
   - `sed -n '1,7p' docs/manuscript/track_a_pivot.md` — confirm L1 (`# Track A — First-pass pivot draft`), L2 (blank), L4 (`>`), L5 (Pivot direction), L6 (`>`), L7 (Target venue) are all UNCHANGED.
   - `grep -c $'\xe2\x80\xa6' docs/manuscript/track_a_pivot.md` — confirm count is unchanged from the pre-edit value (replacement preserves exactly one U+2026, just as the original did).
   - `git diff --stat docs/manuscript/track_a_pivot.md` — confirm output shows `1 file changed, 1 insertion(+), 1 deletion(-)`. ANY OTHER STAT (e.g. 2/2, 1/0, 0/1) is a failure — abort and investigate before commit.
   - `git diff docs/manuscript/track_a_pivot.md` — confirm the diff hunk shows exactly one `-` line (current L3) and one `+` line (replacement L3), with `@@ -1,7 +1,7 @@` or equivalent narrow context anchored at L3. NO other hunks may appear.

4. **Concurrency safety re-check** — Terminal A is running `/gsd-discuss-phase m3-aou-afr-ld-panel-build` with writes scoped to `.planning/phases/m3-aou-afr-ld-panel-build/`. Confirm `git status --short` does NOT show any new untracked or modified path under `.planning/phases/m3-aou-afr-ld-panel-build/` appearing between pre-flight and post-edit (if it does, that's Terminal A's write — do not stage it; proceed with only the docs path).

5. **Atomic commit** with explicit single-file staging (NEVER `git add -A` / `git add .` / `git add -u`):
   ```
   git add docs/manuscript/track_a_pivot.md
   git commit -m "docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)"
   ```
   Use a HEREDOC for the message body if the executor's commit helper requires multi-line; otherwise the single-line `-m` form above is preferred (the message is intentionally one line — no body).

6. **Post-commit verification:**
   - `git log -1 --format='%H %s'` — confirm the new HEAD's subject is exactly `docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)`.
   - `git show --stat HEAD` — confirm the commit touches exactly one file (`docs/manuscript/track_a_pivot.md`) with `1 insertion(+), 1 deletion(-)`.
   - `git status --short` — confirm the three MUST-NOT-TOUCH paths from `<must_not_touch>` are STILL present and dirty / untracked (they MUST NOT have been swept into the commit).
   - Record the post-commit HEAD SHA for the SUMMARY.md the orchestrator will write.

Why each guardrail:
- Byte-exact `old_string` / `new_string` (Edit tool only) prevents the sed/awk class of bugs where unicode `…` gets ASCII-fied or trailing whitespace silently changes.
- The `1 insertion(+), 1 deletion(-)` gate is the Nyquist invariant — anything else means the edit drifted beyond L3.
- Explicit `git add docs/manuscript/track_a_pivot.md` (no `-A` / `.` / `-u`) is the only way to guarantee the three pre-existing dirty paths from other workstreams stay out of the commit, per Carter's standing rule and per the orchestrator's MUST-NOT-TOUCH list.
- The Terminal A concurrency re-check is defensive only — the path scopes are disjoint, but this catches any unexpected cross-contamination before staging.
  </action>
  <verify>
    <automated>test "$(sed -n '3p' docs/manuscript/track_a_pivot.md)" = '> **Status:** Research article ready for *Genome Medicine* submission (original research article format; 5-figure main roster + Figs S1–S7 supplementary; supplementary data at `results/track_a_aggregations/`). Numeric placeholders filled from `results/` per quick-260427-e8n; remaining `[EXTRACT: …]` at L355 (References) is venue-format-deferred. bioRxiv preprint Day 1 regardless.' && git diff HEAD~1 HEAD --stat docs/manuscript/track_a_pivot.md | grep -q '1 insertion(+), 1 deletion(-)' && git log -1 --format='%s' | grep -qx 'docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)' && git status --short | grep -qE '^ M \.claude/settings\.json$' && git status --short | grep -qE '^ M \.planning/config\.json$' && git status --short | grep -qE '^\?\? \.claude/scheduled_tasks\.lock$' && echo OK</automated>
  </verify>
  <done>
- L3 of `docs/manuscript/track_a_pivot.md` reads exactly the REPLACEMENT line from `<verbatim_anchors>`.
- L1, L2, L4, L5, L6, L7 are byte-identical to their pre-edit state.
- `git diff HEAD~1 HEAD --stat docs/manuscript/track_a_pivot.md` reports `1 file changed, 1 insertion(+), 1 deletion(-)`.
- HEAD commit subject is exactly `docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)`.
- HEAD commit touches exactly one file (`docs/manuscript/track_a_pivot.md`).
- `.claude/settings.json`, `.planning/config.json`, and `.claude/scheduled_tasks.lock` remain dirty / untracked in `git status` (they were NOT staged into this commit).
- Pre-edit HEAD SHA and post-commit HEAD SHA recorded for the orchestrator's SUMMARY.md.
  </done>
</task>

</tasks>

<verification>
Phase-level invariants (run after Task 1):

1. **L3-only drift gate:** `git diff HEAD~1 HEAD docs/manuscript/track_a_pivot.md` shows exactly one `-` line (the stale first-pass banner) and one `+` line (the Option A venue-lock banner), anchored at L3. No other hunks.

2. **No-other-files gate:** `git show --stat HEAD` shows exactly one file in the commit (`docs/manuscript/track_a_pivot.md`).

3. **MUST-NOT-TOUCH preservation gate:** `git status --short` after the commit still shows all three pre-existing dirty paths:
   - ` M .claude/settings.json`
   - ` M .planning/config.json`
   - `?? .claude/scheduled_tasks.lock`

4. **Banner block coherence gate:** `sed -n '1,9p' docs/manuscript/track_a_pivot.md` shows:
   - L1: `# Track A — First-pass pivot draft` (unchanged; note: the H1 title still says "First-pass" — that's intentional and out-of-scope for this quick; this plan only flips L3)
   - L2: blank
   - L3: REPLACEMENT banner (Genome Medicine venue-lock)
   - L4: `>` (blank blockquote line, unchanged)
   - L5: Pivot direction banner (unchanged)
   - L6: `>` (blank blockquote line, unchanged)
   - L7: Target venue banner (unchanged)
   - L8: blank
   - L9: `---`

5. **Unicode preservation gate:** `grep -c $'\xe2\x80\xa6' docs/manuscript/track_a_pivot.md` returns the same count as before the edit (replacement preserves exactly one U+2026 horizontal ellipsis).

6. **Commit subject gate:** `git log -1 --format='%s'` returns exactly `docs(track-a): venue-lock L3 banner for Genome Medicine submission (Option A; quick-260427-urj)`.
</verification>

<success_criteria>
- Single atomic commit on `main` advancing HEAD by exactly one commit.
- Commit modifies exactly one file (`docs/manuscript/track_a_pivot.md`) with exactly one line changed (L3).
- L3 reads the Option A Genome Medicine venue-lock banner verbatim per `<verbatim_anchors>`.
- All six L3 must-have truths in the frontmatter are observably true post-commit.
- The three MUST-NOT-TOUCH paths are still dirty / untracked in `git status` (not swept into the commit).
- No new files created; no other files modified.
- Concurrent Terminal A `/gsd-discuss-phase m3-aou-afr-ld-panel-build` writes (scoped to `.planning/phases/m3-aou-afr-ld-panel-build/`) are unaffected and unstaged by this commit.
</success_criteria>

<output>
After completion, the orchestrator (this session, per gsd-quick Step 8) will:
1. Write `.planning/quick/260427-urj-land-track-a-l3-banner-venue-lock-for-ge/260427-urj-SUMMARY.md` capturing pre/post HEAD SHAs, the byte-exact diff, and the verification gate results.
2. Append a STATE.md row recording the venue-lock landing.
3. Land the docs commit (PLAN.md + SUMMARY.md + STATE.md row) in a single atomic commit separate from the L3 edit commit.

The executor produces ONLY the L3 edit commit. The executor MUST NOT touch PLAN.md, SUMMARY.md, or STATE.md.
</output>
