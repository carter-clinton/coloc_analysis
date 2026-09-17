---
phase: quick-260916-vqq
plan: 01
type: execute
wave: 1
depends_on: []            # ordering constraint ENFORCED in Task 1 pre-flight: quick-260916-vqp (records refresh) close-out must already be committed
mode: quick-full
branch: m3-W2-aou-deltas
worktree: none            # GPFS: worktrees disabled project-wide. Scratch CLONES (git clone --shared) live OUTSIDE the repo.
autonomous: true
push: false               # commit only; the orchestrator commits PLAN/SUMMARY/VERIFICATION/STATE afterwards
requirements: ["QUICK-260916-vqq"]   # blast-radius finding B2 (all 7 sub-items) + B2's LOW framing list; STATE.md RESUME item 1 (Stage C NaN error posture), courier gate
revision: 1                          # plan-checker round 1 adopted in full (5 blockers, 7 warnings, 4 info) — see <revision_log>
subsystem: planning/debug (Stage C NaN error-posture adjudication record, v2)
tags: [stage-c, nan-posture, brief-blind, citations, verifier, docs-only, negative-controls, balance-screen]

files_modified:
  - .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md   # CREATED (Task 1)
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md                                      # CREATED (Task 2)
  - .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py                   # CREATED (Task 2; may be corrected in Task 3)
  - .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-SUMMARY.md                  # CREATED, NOT committed by the executor

files_frozen:
  # ⛔ IMMUTABLE — asserted byte-unchanged BEFORE and AFTER every task (family `imm:`)
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md        # v1: md5 763f412bb1a8dbdb38f2cc332ed5a21d, 223 lines
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/**   # kht checker: 260916-kht-verify.py md5 50a4de7a954db77a6f162b9dcb573504
  # ⛔ NO CODE ANYWHERE
  - src/**
  - tests/**
  - config/**
  - workflow/**
  - bin/**
  - scripts/**
  - Snakefile
  # ⛔ posted / owned-elsewhere records
  - .planning/amendments/**                  # posted OSF bodies, NEVER edited
  - .planning/osf_deviations.md              # vqp appends; vqq only READS
  - .planning/HANDOFF.json
  - .planning/STATE.md                       # the ORCHESTRATOR updates STATE.md
  - .planning/DECISIONS.md
  - .planning/ROADMAP.md
  - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt
  - .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
  - everything else not listed in files_modified

user_setup: []            # none: no cloud, no OSF, no network, no external service

must_haves:
  truths:
    - "Pre-flight passes ONLY when: `git status --porcelain --untracked-files=no` is empty (TRACKED-clean; the tree carries long-standing untracked artifacts which are NOT a blocker); a commit whose subject starts `docs(quick-260916-vqp)` exists AND is an ancestor of HEAD; v1 and 260916-kht-verify.py hash to their pinned md5s (size checked FIRST); and `260916-kht-verify.py` (default mode) is GREEN. Any failure STOPS the task with no file written."
    - "BASIS is `git rev-parse HEAD` captured at pre-flight and recorded as a FULL 40-char SHA plus its short form. Every code/repo citation in v2 is verified at BASIS and nowhere else. `c93e97b` appears in v2 ONLY inside the sentence explaining what changed since v1 — never as the basis of a live citation."
    - "EVERY claim carried over from v1 is RE-DERIVED at BASIS by re-locating its verbatim quote/token in the file, NOT by adding a constant offset and NOT by copying v1's checker constants. The re-derivation record names, per claim: v1 range -> BASIS range, the delta, and the verdict (HOLDS / MOVED / FALSE)."
    - "`.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` and `.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py` are byte-identical before and after the whole task, in the working tree AND at BASIS (`git diff --quiet BASIS -- <both>` rc 0), with a negative control proving the `imm:` check can fail."
    - "v2 is a NEW file `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md` whose status block says it SUPERSEDES v1 for couriering, names v1's repo-relative path, and gives a ONE-LINE reason that is itself brief-blind-safe: it carries NO defect count and NO option letter (`sup:noleak`). v1 is NOT annotated (annotating it would break immutability); the supersession is recorded in v2 and in the executor's report for the SUMMARY/STATE."
    - "Reverse-applying v2's declared edit ledger (En..E1) to v2 reproduces v1's bytes EXACTLY (size THEN md5 == 763f412bb1a8dbdb38f2cc332ed5a21d). Forward-applying E1..En to v1 reproduces v2's bytes EXACTLY. Every `old` occurs exactly once at its point of application and every `new` exactly once in v2. Nothing in v2 is outside the ledger."
    - "Every review defect R1-R9 (and every sub-item) is closed by EITHER a named ledger edit on v2 OR — for R9, the STATE.md hand-off sub-item, which cannot be closed in v2 because STATE.md is frozen and orchestrator-owned — a named hand-off item carrying verbatim replacement text in the executor's report. The closure map states which of the two applies for each sub-item. No sub-item is deferred, softened or partially closed."
    - "v2's §1 row for the RETAINED fully-NaN-row -> drop rule quotes trsx5:37 and mk7ze P321 / R488 verbatim, verified against the POSTED bodies (mk7ze = repo lines 168-500, size THEN md5; trsx5 = the 9,695 B byte-exact reconstruction), with each anchor's negative control observed non-matching."
    - "v2 carries SIX options A-F, each with the SAME labelled sub-field set, each with at least one explicitly labelled READING for its pre-registration answer, and a per-option READING-count spread of at most 1. No option's pre-registration answer is a flat conclusion."
    - "The `bal:` balance family MEASURES that no option is pre-favoured by emphasis, at BOTH the option level and the WITHIN-option level: (fields) identical labelled sub-field sets; (reading) per-option READING label count >= 1 with spread <= 1; (readweight) per-READING word counts printed with within-option max/min <= 2.0, each READING scored INCLUDING its attributed sub-bullets; (words) per-option heading+body word counts printed with max/min <= 3.0; (eval) zero hits of the PLAN-DECLARED evaluative-cue list across every option HEADING AND body; (precedent) the R4-COVERAGE precedent named in section 4 and in EXACTLY the declared fitting set {A, C, F}, and its section-5 question occupying neither the first nor the last slot with its index printed; (questions) every option A-F named in >= 1 section-5 question with the question->option map printed. Both declared bands (3.0 and 2.0) and both screen lists are fixed in THIS plan BEFORE authoring. Every `bal:` check is observed RED under `--selftest`, and `bal:eval` additionally passes a REAL-TEXT discrimination control on v1's own Option C and Option E at BASIS."
    - "`g:recommend` is 0 hits over its normalized pattern set with the single declared exemption, and `--selftest` observes it RED on at least two distinct injected recommendation forms (one plain, one markdown-obfuscated)."
    - "`260916-vqq-verify.py` default mode prints a GREEN RESULT line with parsed == table == verified == c-res count, emits JSON on `--json` (refusing any path inside the repo), and has NO duplicate result ids."
    - "`--baseline` runs the citation families against **v1** at BASIS and its RED id set is reconciled by SET EQUALITY (not by count) against Task 1's MOVED/FALSE verdict set. A set mismatch in either direction is a FINDING to report, never a number to adjust."
    - "`c-halt:` asserts every claim range into `.planning/debug/260824-STAGE-B-HALT-…md` is DISJOINT from the two passages quick-260916-ocb falsified (the RAM-inheritance measurement and the `Popen` + `os.wait4` \"clean fix\", plus the `RAM-1 fix (TDD)` line), with the ranges RE-LOCATED BY CONTENT at BASIS because vqp inserts an annotation into that file. Observed RED under `--selftest` by injecting a citation into a falsified range."
    - "`--selftest` reports a GREEN positive control on the real inputs and then observes EVERY check family RED on a deliberately corrupted input, with the mutation count stated and each mutation proven to have changed something. A NOT-OBSERVED family BLOCKS close-out."
    - "Nothing under src/, tests/, config/, workflow/, bin/, scripts/ or Snakefile is added, modified or deleted: `git diff --name-only BASIS HEAD` lists only the four files in files_modified (minus the SUMMARY) and `git status --porcelain --untracked-files=no` is empty at close-out."
    - "Zero network, zero cloud, zero OSF, zero Seth contact, zero posture code. $0."
  artifacts:
    - path: ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md"
      provides: "brief-blind Stage C NaN error-posture options draft v2: basis-pinned citations, six options, corrected D/E, new drop-rule TEXT row, new Option F, balanced structure"
      contains: "SUPERSEDES"
      min_lines: 260
    - path: ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py"
      provides: "basis-pinned citation + edit-ledger + immutability + balance + neutrality re-verifier with --selftest, --live, --source, --json"
      contains: "SELFTEST"
      min_lines: 1400
    - path: ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md"
      provides: "BASIS commit record + per-claim v1->BASIS re-derivation table + the new-fact measurements v2 needs"
      contains: "BASIS"
      min_lines: 80
  key_links:
    - from: ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md"
      to: ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py"
      via: "BANKED_REL default --draft target; the checker's BASIS constant equals the basis v2 states"
      pattern: "260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2\\.md"
    - from: ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py"
      to: ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md"
      via: "f:reverse must-be-identity target + imm: byte pin"
      pattern: "763f412bb1a8dbdb38f2cc332ed5a21d"
    - from: ".planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py"
      to: ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt"
      via: "posted-body anchor: size THEN md5, with a negative control"
      pattern: "c19be8b2ad7cd6a45fee1d668d8a9cf9"

metrics:
  estimated_tasks: 4   # Task 2 split into 2a/2b per revision round 1 W8 (kht's proven seam)
  context_target: "~50%"
---

<objective>
Produce **v2** of the brief-blind Stage C NaN error-posture options draft, built and verified against a
basis commit captured at EXECUTION time, closing all seven sub-items of blast-radius finding **B2**
plus its LOW framing list — and a NEW checker that proves it mechanically.

Purpose: v1 is banked but not courier-ready. Its code citations were written at `c93e97b`; the driver
has since gained 143 lines, so its 24 `run_native_ld_panel.py` citations point at the wrong text. A
four-investigator + Codex blast-radius review also found a wrong §4 heading, a one-sided Option B, a
structure that leaks the private recommendation, an overstated posted fence, a mis-described Option D
deliverable, missing content a methodologist would expect, and residual framing cues. The draft goes
**brief-blind** to an external adjudicator; each defect either misleads them or leaks our reasoning.

Output: three committed docs-only files (basis/re-derivation record, v2 draft, v2 checker). v1 and the
kht checker are byte-unchanged. No code anywhere. No network, no cloud, no OSF, no Seth.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md
@.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py
@.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md

<project_rules>
- **GSD mode `solo`, `git.isolation: branch`. NO worktrees on GPFS.** Scratch clones for negative
  controls use `git clone --shared` into `$TMPDIR`, never the working tree.
- **Node.js PATH on HPC:** `export PATH="$HOME/miniconda3/bin:$PATH"` before any GSD CLI call.
- **Multi-terminal git staging:** NEVER `git add .` or `git add -A`. Explicit paths only.
- **GPFS git object-store loss:** if a commit fails with "invalid object" / "Error building trees",
  **STOP and report** — do not improvise a recovery.
- **Always fence code pastes** in the report.
- **Interactive grep is a wrapper; scripts get GNU 3.6.** Measure regex dialect in the runtime that
  executes the guard (shebang -> `/usr/bin/grep`), never the interactive shell. The checker uses
  Python `re`, not shell grep, for every gate.
- **Project skills:** `.claude/skills/aou-ld-pipeline` and `.claude/skills/close-session` exist.
  Neither applies: this task fires nothing, touches no AoU surface and runs no cloud command.
  Do NOT load `AGENTS.md`.
</project_rules>

<measured_at_planning_time>
Measured by the planner on 2026-09-16 at HEAD `621701c` (BEFORE vqp). These are ORIENTATION, not
values to copy. Task 1 RE-DERIVES every one of them at BASIS; a disagreement is a FINDING to report,
never a number to adjust.

- v1 `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md`: 223 lines,
  md5 `763f412bb1a8dbdb38f2cc332ed5a21d`.
- `260916-kht-verify.py`: md5 `50a4de7a954db77a6f162b9dcb573504`. Default mode:
  `RESULT GREEN checks=317 parsed=88 table=88 verified=88` (rc 0).
- Posted anchors reproduce: mk7ze repo lines 168-500 = 22,945 B / `13a49f543cabcc27ce9f1e589783c060`;
  control lines 167-500 = `8154025b50ef344cd43078f910add359`. trsx5 = 9,695 B /
  `c19be8b2ad7cd6a45fee1d668d8a9cf9`; control first 9,694 B = `0775eef2aa3f4965c42375ed955aced0`.
  ⚠ trsx5 TRAP: `wc -l` prints 58; the file has **59** lines (no trailing newline). Count with
  `str.splitlines()`.
- `src/python/run_native_ld_panel.py` 1344 -> 1487 lines (net **+143**). `git diff -U0` hunk headers
  are ALL at c93e97b lines **184-203** (`_run_plink` + the new `_PLINK_PEAK_RSS_LAUNCHER`). v1's
  lowest RN citation is `:723`, so **every** RN citation in v1 is uniformly +143 at HEAD — but this
  is a MEASURED coincidence of where the insertions landed, not a rule. Re-derive per citation.
- `src/python/fire_verifier.py` and `src/python/plink_ld_to_npz.py` are **byte-unchanged**
  c93e97b..HEAD, so v1's FV and PL citations still hold.
- ⚠ **c-ast:S2 in the kht checker is GREEN FOR THE WRONG REASON at HEAD.** It asserts
  "innermost def of RN:1144 == process_region". At HEAD, line 1144 is an unrelated comment inside the
  same (long) function, so the +143 shift does NOT turn it red. The v2 checker must anchor AST checks
  on an AST-located symbol/statement, never on a line number that merely falls inside a long function.
  (This is why the blast-radius review lists S3-S6/S9 but not S2.)
- ⚠ At HEAD, v1's `:723-725` lands inside `_retained_window_bim` and `:866-872` inside
  `_reclaim_region_scratch` — both wrong content.
- **trsx5:37 (verbatim):** "The fully-NaN-row → drop rule (prior item (a) first branch): a variant row
  that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF /
  missingness QC. This converges with the new exclude policy and is retained."
- **mk7ze P321-322 / R488-489 (verbatim):** "- **The fully-NaN-row → drop rule** and **the raw-panel
  NaN-raise contract** (the raw per-region `.npz` reader continues to RAISE on any NaN rather than
  silently coercing it)." The drop rule is named on **P321 / R488** alone.
- **mk7ze P302-305 / R469-472 (verbatim):** "UNTOUCHED. The 2026-07-10 record fences *"choosing the
  occlusion criterion to obtain a particular fine-mapping result"*; the anomaly GATE is a different
  object from the CRITERION, and recalibrating the gate against a measured population is not that
  prohibited act. The criterion is not modified here in any way."
- `.planning/osf_deviations.md` at HEAD: entry heading `## 2026-09-03 —` at **:532**, its
  `- **Status:** DRAFTED — NOT POSTED` at **:534**; `⛔ NO PREDICATE CHANGE` at **:670-671**; the
  one-sided-sweep caveat + "**Production tests the rate on BOTH sides.**" at **:680-682**; "to be
  pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing" at
  **:685-689**; "no covering record for EITHER member" at **:703-704**. ⚠ vqp APPENDS to this file.
- `src/python/fire_verifier.py:300-303`: `_OK_STATUSES = ("ok", "skipped_idempotent")`;
  `_DEFERRAL_PREFIXES = ("deferred_infeasible_square", "deferred_occlusion_anomaly")`;
  `_FAILURE_PREFIXES = ("error:",)`. This grounds Option F.
- At HEAD the `if ok:` block is `run_native_ld_panel.py:1245`; inside it the **excludelist** upload is
  `:1257-1261`, the **occlusion manifest** `:1266-1271`, the **gate sidecar** `:1277-1282` (c93e97b
  equivalents 1102 / 1114-1118 / 1123-1128 / 1134-1139). The brief's "(c93 :1113-1128)" is
  approximate at its start; re-derive.
**Added in revision round 1 (measured by the planner, same caveat — RE-DERIVE at BASIS):**

- **v1's own balance numbers, measured** (body = the lines between an option heading and the next
  heading, heading excluded, `str.split()` tokenization):
  `A 296 w / 2 READING labels · B 208 / 1 · C 136 / 0 · D 165 / 0 · E 49 / 0`; **max/min = 296/49 =
  6.04**. ⚠ The revision brief quotes **208 as 204** and the ratio as **5.53**; both differ from my
  measurement, which is why **the counting contract below is DECLARED rather than assumed**. A word
  count is a claim: whatever the checker computes, it must print its own span and tokenization rules
  so the number is reconcilable. Report the discrepancy; do not silently adopt either figure.
- **kht's `EVAL_WORDS` list is provably NON-DISCRIMINATING here:** it scores **0 hits in ALL FIVE**
  of v1's option bodies. `.planning/STATE.md` (the "NEXT (Carter)" item, currently `:54`) says so in
  as many words — the two residual cues are ones *"no word screen catches"*.
- ⚠ **`listed for completeness` is in Option E's HEADING (`v1:187`), NOT in its body.** So a
  body-only eval screen CANNOT catch it, and the revision brief's proposed real-text control would
  half-fail as written. `bal:eval` therefore scans **heading + body**, and the control is specified
  accordingly below.
- ⚠ **v1's §5 questions name their options by SUBSTANCE, not by label** (measured: only Q5 contains a
  literal option letter — "(D)"). So a name-matching `bal:questions` gate would be vacuous unless v2
  is AUTHORED to tag each question with its option(s). That authoring requirement is in R4(vi).
- **The falsified halt-record passages, located by content at HEAD:** `:118-125` (the
  `ru_maxrss`-inheritance measurement — "region 17 → 2.9689 (real, first child) … Region 1's 30.6591
  is real because Stage A was its own process" — and "Clean fix: `subprocess.Popen` +
  `os.wait4(pid, 0)`") and `:146` ("4. Separately and independently: **RAM-1** fix (TDD) …").
  **None of v1's five citations into that file (`:11-16`, `:20-21`, `:45-58`, `:104-107`, `:150-179`)
  intersects either**, so `c-halt:` is cheap. ⚠ vqp inserts a "⚠ SUPERSEDED 2026-09-16" annotation
  into this file, which may SHIFT these line numbers — re-locate by content at BASIS.
- **`imm:` sizes, measured:** v1 = **18,309 B / 223 lines**; `260916-kht-verify.py` = **88,899 B /
  1,711 lines**. (Both agree with the revision brief.)
- **The STATE.md hand-off lines for R9, located at HEAD** (⚠ vqp rewrites STATE.md — re-locate every
  one of these by CONTENT at BASIS, never by line number):
  - `:39` — "**88 citations re-verified** … GREEN in default, `--source` and `--live` modes" — the
    `--live` half is now FALSE.
  - `:54` — "Judge two residual framing cues no word screen catches: Option C's … and Option E's
    heading …" — both are CLOSED by R8(iii) and R5(i).
  - `:55` — "2. Courier the banked file to Seth, brief-blind." — carries **no** basis caveat.
  - `:78` — "⚠ The banked Stage C options draft cites `run_native_ld_panel.py` at basis `c93e97b`
    … Courier the draft with 'read the code at commit `c93e97b`', or re-base the citations first
    (Carter's call)." — the re-base is what this task DOES.
  (`:39` and `:78` also contradict each other on `--live`, which is blast-radius finding B9.)

- ⚠⚠ **THE BRIEF'S OPTION-D RUNTIME IS WRONG — measure it yourself.** The brief says the
  `pcs_panelwide_reclassify` pass is "1h53m for 21 regions". Measured:
  - **1h53m** (02:29:11Z -> 04:22:50Z, exit 0) is **RUN 1**, 2026-09-01
    (`.planning/quick/260831-kw8-.../260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md:13`).
    `.planning/STATE.md:479` and `.planning/quick/260901-rvu-.../260901-rvu-PLAN.md:620` both describe
    it as the **6-region** / 1,011,893-row banked run; rvu-PLAN.md:709 contrasts "21 vs 6 excludelists".
  - The **21-region** reclassify pass is **RUN 2**, 2026-09-02: launched 18:26:17Z, outputs written
    21:07:03Z, **2 h 40 m 46 s** wall
    (`.planning/quick/260902-vsp-.../CONTENT-SPEC.md:10`). That file also states
    `region_ids_selected = 276` (the ancestry-resolved manifest size) with "⚠ 276 is NOT the number of
    regions carrying rows. **21 regions carry rows.**"
  - The 21-region **pairwise-completeness scan** (a different instrument) took **48 min**
    (`.planning/STATE.md` frontmatter, marker `PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE`, "Runtime 48m").
  Whatever v2 states must be re-measured at BASIS and must name WHICH instrument, WHICH run and
  WHICH region count.
</measured_at_planning_time>

<declared_screens>
## DECLARED BEFORE AUTHORING — bands, spans and screen lists

Everything in this block is fixed NOW, before a word of v2 exists, for the same reason the 3.0 band
was: a screen authored after the text it screens is calibrate-to-pass. **Do not extend, trim or
re-tokenize any of it to make v2 green.** If v2 cannot satisfy a band, that is a STOP-and-report
(see `<escape_hatch>`), never a band edit.

### S-1. The counting contract (declared because two independent counts of v1 already disagreed)

- **Option span** = from the `### Option X: …` heading line through the line before the next `###`
  heading or before `## 4.`, whichever comes first.
- **Option body** = the span minus the heading line. **`bal:words` scores heading + body**;
  `bal:eval` also scores heading + body. The heading is where v1's `(listed for completeness)` cue
  lived, so excluding it would blind the screen.
- **Tokenization** = Python `str.split()` on the raw span (no markdown stripping), so the number is
  reproducible by `python3 -c` from the file alone.
- **Excluded from every `bal:` count:** the `LOW` subsection (it is not an option body), the
  `Files cited` key block, the anchors block, and §1/§2's tables.
- The checker **PRINTS** its span line ranges and per-unit counts on every run. A `bal:` number that
  is not printed alongside its span is not evidence.

### S-2. Bands

| Band | Value | Scope |
|---|---|---|
| `bal:words` | `max/min <= 3.0` | across the six option units (heading + body) |
| `bal:readweight` | `max/min <= 2.0` | **within** each option, across that option's READINGs |

**`bal:readweight` attribution rule (this is the whole point of the check).** v1's tilt lived in the
BULLETS, not the labels: Option A's READING 2 is followed by supporting sub-bullets while Option B's
single READING carries three. So a READING's weight = the words from its `*READING …:*` label up to
the next `*READING` label, the next sub-field label (`**Consequences:**` etc.), or the end of the
option — **including every sub-bullet in between**. Print each READING's label, its line range and
its word count. An option with exactly one READING is RED under `bal:reading` (which requires the
spread to be <= 1 and every option to have >= 1) — so `bal:readweight` always has >= 2 to compare
wherever any option has 2.

### S-3. `EVAL_CUES` — the evaluative-cue screen for `bal:eval`

kht's list is inherited as a base **and is known to score 0/5 on v1's option bodies**, so it is
extended with the cue CLASSES the blast-radius review actually found. Declared set:

```
# inherited from 260916-kht-verify.py EVAL_WORDS (base; non-discriminating on its own)
not workable, unworkable, realistic, surprise, only honest, clearly, obviously, should,
better, worse, prefer, simply, merely, of course, naturally
# added in revision round 1 — the cue classes the review actually found
listed for completeness, for completeness, already argues, already established, a formality,
in practice, the obvious, in any case
# added: editorial verbs (the reviewer's own vocabulary for v1's defects)
argues against, stretches, overstates
```

Matching: normalized (smart quotes folded, `[*_`]` stripped, whitespace collapsed, lower-cased);
single words on word boundaries, multi-word cues as normalized substrings.

**REAL-TEXT DISCRIMINATION CONTROL (required — stronger than an injected synthetic word).** Run
`bal:eval` against **v1's own Option C and Option E units at BASIS** and OBSERVE RED:
  - Option C body -> `already argues` and `argues against`  (measured present);
  - Option E **heading** -> `listed for completeness`  (measured present in the HEADING, `v1:187`).
If either does not go RED, the screen is not discriminating and the task STOPS.

### S-4. `G_PATTERNS` — the recommendation screen for `g:recommend`

Inherited verbatim from `260916-kht-verify.py:1096-1099` (11 patterns), plus additions:

```
recommend | \bprefer | \bsuggest | \bpropos(e|es|ed|al)\b | \badvis(e|es|ed|able)\b
\bbest (option|choice|path|course)\b | \b(we|i) (favou?r|endorse|lean|urge|advocate)\b
\bin (our|my) (view|opinion|judgement|judgment)\b | \b(right|correct) (choice|option|call)\b
\bshould (choose|adopt|pick|go with|select)\b | \bopt for\b
# added in revision round 1
\bthe (default|obvious|natural) (option|choice|course)\b | \bleast bad\b | \bthe way to go\b
\bwe would\b | \bour (view|position|preference)\b
```

Single declared exemption: the phrase `with no recommendation`, which must occur **exactly once**
(`g:exempt`). Observed RED under `--selftest` on two forms: plain and markdown-obfuscated.

### S-5. The precedent fitting set (gated on EXACTLY this set, not on ">= 2")

The R4-COVERAGE-shaped disclosure obligation fits **exactly the options that leave a raising region
unbanked: {A, C, F}**. `bal:precedent` asserts the precedent is named in §4 and in exactly those
three option units — not two, not all six. If authoring reveals it also fits another option, that is
a FINDING to report with its reason, not a set to widen silently.
</declared_screens>

<escape_hatch>
**If a declared band cannot be met without adding material the evidence does not support: STOP and
report.** Do not pad an option, do not widen a band, do not invent a citation, do not delete
substance from a long option to shorten it. A declared STOP naming the band, the measured numbers and
what material would have been required is an ACCEPTABLE close-out for Tasks 2b/3 — the automated
verify accepts it via the `VQQ-BAND-STOP` marker described in Task 2b. The planner's estimate is that
~2.1 is reachable once Option E gains the four sub-fields and Option F is authored, but that is an
ESTIMATE, not a target to hit by padding.
</escape_hatch>

<interfaces>
<!-- The kht checker's proven contract. REUSE THE DESIGN, RE-DERIVE EVERY VALUE.
     Do NOT import from it and do NOT copy its constants. -->

`260916-kht-verify.py` (stdlib only, py3.9-compatible, `git` is the only subprocess, cwd=ROOT,
never `shell=True`, no `src/` import, no network):

```
ROOT = Path(__file__).resolve().parents[3]           # asserted to contain .git
BASIS, SOURCE_SIZE, SOURCE_MD5
MK_START, MK_END, MK_SIZE, MK_MD5, OFFSET=167, MK_CONTROL, MK_CONTROL_PREFIX
TR_SIZE, TR_MD5, TR_CONTROL_LEN
PATHS: {short key -> repo-relative path};  SHORT: {key -> backticked short form}
CLAIMS  = [(id, file key, kind "Q"|"T", payload[], NOT-tokens[], edit-id|None), ...]   # POSITIONAL
PERMITTED_EDITS = [{id, cls, old, new, why, [bare_ref], [evidence], [label], [origin]}, ...]

class Reader:  raw/text/lines, `git show BASIS:<path>` by default, working tree under --live,
               ST always at BASIS, `overrides` for selftest
norm(s)        -> smart quotes folded, [*_`] stripped, whitespace collapsed, lower-cased
seg_in(q, hay) -> "…"-separated normalized segments occur IN ORDER
CITE regex     -> explicit `file.ext:a-b` | bare `:a-b` | `trsx5:n` | `mk7ze Pa-b / Ra-b`
parse_key / keymap_of / resolve   -> bare refs inherit the nearest preceding explicit resolution
unit_for_offset(draft, off)       -> the paragraph/table-row unit a quote must be BOUND to
content_check(...)                -> payload inside a 1-based inclusive range, NEVER clamped;
                                     MK claims checked at BOTH the repo range and the posted P range
apply_edits(text, edits, reverse) -> exact replacement, each required to occur EXACTLY ONCE
summarize(...)                    -> GREEN iff no RED and parsed == table == verified == c-res count;
                                     SKIP is RED unless explicitly allowed; duplicate ids are RED
```

Check families and their meaning:

| id prefix | proves |
|---|---|
| `a:` | mk7ze posted extract: size THEN md5, plus a control range that must NOT match, plus the draft states both |
| `b:` | trsx5 posted body: size THEN md5, plus a truncated control, plus the draft states both |
| `c-key` | the Files-cited key maps every short form to exactly one tracked path, each used outside the key |
| `c-count` | parsed citation tokens == CLAIMS rows (positional) |
| `c-res:` | each parsed token resolves to the path its CLAIMS row names |
| `c:` | the payload really is inside the cited range |
| `c-quote:` | a quoted string appears in the draft |
| `c-bind:` | the quote is in the SAME paragraph unit as its citation (not a far-away token) |
| `c-pr:` | mk7ze `P + 167 == R` |
| `c-ast:` | structural facts about the shipped code (AST, not line numbers) |
| `c-hand:` | every hand-computed number recomputed from its stated inputs |
| `d:` | the "posted text does not say X" sweep recomputed, with control terms that DO appear |
| `e:` | git freeze facts about the fire-path files, with a control window that is non-empty |
| `f:` | permitted-edit ledger: classes, forward identity, REVERSE must-be-identity, per-edit uniqueness, class-3 before-RED/after-GREEN evidence, bare-ref plan |
| `g:` | neutrality screen (status line, single exemption, recommendation patterns, option set, question set) |
| `report:` | INFO-only sweeps, never a gate |
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight, BASIS capture, and the v1->BASIS re-derivation + new-fact measurement record</name>
  <files>.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md</files>
  <action>
**No v2 text and no checker in this task.** This task MEASURES; Task 2 authors.

**(1) PRE-FLIGHT — every check STOPS the task on failure, with nothing written.**
  a. `cd` to the repo root. `export PATH="$HOME/miniconda3/bin:$PATH"`.
  b. `git rev-parse --abbrev-ref HEAD` == `m3-W2-aou-deltas`.
  c. `git status --porcelain --untracked-files=no` is EMPTY. (TRACKED-clean only — the tree carries
     long-standing untracked artifacts, listed in the session git status; they are NOT a blocker and
     must NOT be added, cleaned or committed.)
  d. **vqp gate.** `git log --format='%H %s' | grep -E '^[0-9a-f]{40} docs\(quick-260916-vqp\)'`
     must yield >= 1 line, and the newest such commit must satisfy
     `git merge-base --is-ancestor <sha> HEAD` (rc 0). If ZERO matches -> **STOP**: "quick-260916-vqp
     has not landed; vqq's basis would be captured before the records refresh." Report the newest 10
     commit subjects so the orchestrator can see what is actually there.
  e. **Immutability, size THEN md5** (a size check first, so a same-size corruption still fails at
     md5 and a size failure never silently produces a hash — the same shape as the posted anchors):
       - `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` -> **18,309 B /
         223 lines** / md5 `763f412bb1a8dbdb38f2cc332ed5a21d`.
       - `.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py`
         -> **88,899 B / 1,711 lines** / md5 `50a4de7a954db77a6f162b9dcb573504`.
       **RE-MEASURE both; do not copy these figures forward if your measurement disagrees — report
       the disagreement.** Also `git diff --quiet HEAD -- <both paths>` rc 0.
  f. **kht checker positive control:** run it in DEFAULT mode; it must print a GREEN RESULT line and
     exit 0. Record the line verbatim. (If it is RED at pre-flight, STOP and report — something
     upstream moved.)
  g. **Halt-record annotation gate (B5).** `.planning/debug/260824-STAGE-B-HALT-…md` carries two
     passages that quick-260916-ocb FALSIFIED, and vqp appends a "⚠ SUPERSEDED 2026-09-16"
     annotation to that record. **ASSERT the annotation is present at BASIS** (search for it by
     content, case-sensitively, and print the matching line(s) with their numbers). If it is ABSENT
     -> **STOP**: "vqp's SUPERSEDED annotation is not in the halt record; v2 would cite a file whose
     falsified passages are unmarked." Then locate, BY CONTENT, the two falsified ranges (the
     `ru_maxrss`-inheritance measurement through the `Popen` + `os.wait4` "clean fix", and the
     "RAM-1 fix (TDD)" line) and record their BASIS line numbers — these become `c-halt:`'s
     forbidden ranges. Orientation at HEAD: `:118-125` and `:146`; the annotation may shift them.
  h. **Capture BASIS** = `git rev-parse HEAD` (FULL 40 chars) + `git rev-parse --short HEAD`.
     Record the subject line too. From here on, BASIS is the ONLY basis; `HEAD` is never cited.

**(2) RE-DERIVE EVERY v1 CLAIM AT BASIS — by re-location, not by offset.**
  For each of the 88 positional CLAIMS rows in `260916-kht-verify.py` (ids c01..c81, n01..n07):
    - read the cited file **at BASIS** (`git show BASIS:<path>`);
    - find the row's payload by searching for its normalized token(s)/quote in the file — the SAME
      `norm()` + `seg_in()` semantics the kht checker uses — and report the 1-based inclusive line
      range where it is found;
    - report: `claim id | file key | v1 range | BASIS range | delta | verdict`.
  Verdicts: **HOLDS** (same range, payload present), **MOVED** (payload found at a different range),
  **FALSE** (payload not found anywhere at BASIS, or found more than once ambiguously).
  ⚠ Do NOT assume a uniform +143. Compute each delta and then state, as a measured observation,
  whether the deltas are uniform per file and where any non-uniformity is.
  ⚠ A MOVED/FALSE verdict is a FINDING. Record it; do not adjust v1 and do not adjust the payload to
  make it match.
  Also re-derive, at BASIS, and record:
    - the kht checker's AST anchors S1-S9 (which still hold, which are GREEN-for-the-wrong-reason —
      see the S2 note in `<measured_at_planning_time>`);
    - the `c-hand` inputs (H1's numbers, H2's STATE.md frontmatter marker + "Runtime 48m", H3's
      `## 2026-09-03 —` entry start line found by HEADING SEARCH not by literal, H4's U7-vs-trsx5 md5
      inequality, H5's basis statement);
    - the `d:` sweep counts (the six 0-hit terms; the `defer` and `raise` control counts in both
      posted bodies; `deferred_infeasible_square` raw and underscore-stripped);
    - the `e:` git-freeze facts. ⚠ The kht `SINCE = 2026-08-24` is now FALSE (the RAM-1 commit touched
      `run_native_ld_panel.py` on 2026-09-16). Re-derive the freeze property: the newest commit
      touching `src/python/{run_native_ld_panel,fire_verifier,plink_ld_to_npz}.py` at BASIS, and a
      SINCE just after it that yields 0 commits, plus a control window that yields >= 1. Record both.

**(3) MEASURE THE NEW FACTS v2 NEEDS.** Each with its BASIS file:line and a verbatim quote:
  - **N1 — retained fully-NaN-row -> drop rule.** trsx5:**37** (count lines with `splitlines()`),
    and mk7ze **P321 / R488** located by verbatim search, not by subtracting 167 by hand. Quote both.
  - **N2 — the fence scope.** trsx5:**49** (what is actually fenced) and mk7ze **P302-305 / R469-472**
    (the GATE-vs-CRITERION separation). Quote both.
  - **N3 — DRAFTED — NOT POSTED.** The `## 2026-09-03 —` entry start line and its first
    `- **Status:** DRAFTED — NOT POSTED` line, plus the entry's end line, proving `:660-663`,
    `:670-671`, `:680-682`, `:685-689` and `:703-704` all fall INSIDE that entry. ⚠ vqp appended to
    this file — re-derive every line number.
  - **N4 — the C-rate caveat.** The osf_deviations lines carrying "this sweep could observe only one
    side" and "**Production tests the rate on BOTH sides.**". Quote verbatim.
  - **N5 — Option D's real deliverable.** (i) the pairwise-completeness scan's ANCHOR-RELATIVE
    limitation and where it is stated; (ii) `src/python/pcs_panelwide_reclassify.py` as the separate
    pass that answers "does the pair reach the matrix"; (iii) the MEASURED runtimes and their region
    counts — RUN 1 and RUN 2 as described in `<measured_at_planning_time>` — each re-derived from its
    own record, each labelled with instrument + run + region count. (iv) the 21-region
    pairwise-completeness scan's 48 min. **If your measurement disagrees with the brief's
    "1h53m for 21 regions", say so explicitly; do not reconcile silently.**
  - **N6 — mk7ze P88-89 / R255-256 scope.** Quote it and state, as a measured fact, what it describes
    (the pre-committed systematic-by-span 21-of-276 occlusion SAMPLE) so v2 attaches it to the sample
    sentence and not to the scan.
  - **N7 — X1 completeness.** At BASIS: the `if ok:` line, and the excludelist, occlusion-manifest and
    gate-sidecar upload blocks inside it, with line ranges.
  - **N8 — Option F's ground.** At BASIS: `_OK_STATUSES`, `_DEFERRAL_PREFIXES`, `_FAILURE_PREFIXES` in
    `fire_verifier.py`, the `deferred_infeasible_square` producer site in `run_native_ld_panel.py`,
    and the R4-COVERAGE registration in `deferred-items.md` with its named enforcer.
  - **N9 — the LOW items' ground.** Any BASIS citation available for: a per-region
    pairwise-completeness pre-check at fire time (and the scratch/plink cost it would precede);
    re-running on a different sample set or sample-level QC; the downstream AFR fine-mapping / coloc
    denominator effect. If a LOW item has NO citable ground at BASIS, say so — v2 will then state it
    as an uncited LOW option explicitly labelled as such rather than inventing a citation.

**(3b) THE MOVED/FALSE VERDICT SET IS A DELIVERABLE.** Emit it as an explicit, sorted set of claim
ids (not a count). Task 2a re-computes the same set mechanically via `--baseline` and asserts SET
EQUALITY against it. Two opposite-sign component errors cancel in a count and survive it, so the
count alone is not the reconciliation (memory: `feedback_aggregate_agreement_hides_component_errors`).

**(4) WRITE THE RECORD** to `260916-vqq-BASIS-AND-REDERIVATION.md`:
  BASIS (full + short SHA + subject); the vqp gate evidence; the pre-flight immutability sizes/md5s;
  the kht positive-control line verbatim; the full re-derivation table; the AST/hand/sweep/git
  re-derivations; N1-N9 with verbatim quotes; and a HEADLINE list of every v1 claim whose verdict is
  MOVED or FALSE. Every number in it must be one you measured in this task.

**(5) COMMIT** — explicit path only:
  `git add .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md`
  `git commit -m "docs(quick-260916-vqq): BASIS <short> + v1->BASIS re-derivation of all 88 citations + the new-fact measurements for draft v2 (docs-only; nothing under src/ or tests/)" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"`
  Re-assert immutability (e) AFTER the commit. If the commit fails with "invalid object" / "Error
  building trees" -> **STOP and report** (GPFS object-store loss).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test "$(md5sum .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md | cut -d' ' -f1)" = 763f412bb1a8dbdb38f2cc332ed5a21d &amp;&amp; test "$(md5sum .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | cut -d' ' -f1)" = 50a4de7a954db77a6f162b9dcb573504 &amp;&amp; git diff --name-only HEAD~1 HEAD | grep -qxF '.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md' &amp;&amp; test "$(git diff --name-only HEAD~1 HEAD | wc -l)" = 1 &amp;&amp; test -z "$(git status --porcelain --untracked-files=no)" &amp;&amp; echo TASK1-OK</automated>
  </verify>
  <done>
BASIS captured as a full 40-char SHA with vqp proven to be its ancestor; all 88 v1 claims re-derived
at BASIS by re-location with per-claim verdicts; the `e:` freeze property re-derived (the kht
`SINCE = 2026-08-24` is recorded as no longer true); N1-N9 measured with verbatim quotes; the record
committed as the ONLY file in its commit; v1 and the kht checker byte-unchanged before and after.
  </done>
</task>

<task type="auto">
  <name>Task 2a: Build the vqq checker and prove its engine on v1 (--baseline RED, set-equal to Task 1)</name>
  <files>.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py</files>
  <action>
**The engine before the artifact it grades.** This task builds the checker and proves the citation
engine independently reproduces Task 1's findings — BEFORE a word of v2 exists to be graded, so the
engine cannot be shaped around the text. (kht's proven seam; its checker is 1,711 lines for FEWER
families than this one, so budget accordingly.)

**(C) THE CHECKER `260916-vqq-verify.py`.** Build on the kht contract in `<interfaces>`. **Stdlib
only; py3.9-compatible; the only subprocess is `git` with `cwd=ROOT` and never `shell=True`; nothing
imported from `src/`; no network; `--json` refuses any path inside the repo.** Modes: default (BASIS),
`--live` (working tree; ST always at BASIS), `--source <v1 path>` (forward identity),
`--bare-ref-plan`, `--selftest`, `--json`.
**Re-derive every constant from Task 1. Do NOT copy a value from the kht checker because it was
green there.** In particular `BASIS`, `SINCE`/`SINCE_CONTROL`, `H3_LINE`, `H2_MARKER`, every CLAIMS
range, and the AST anchors are all new values.
Families: `a: b: c-key c-count c-res: c: c-quote: c-bind: c-pr: c-ast: c-hand: d: e: f: g:` as in
kht, PLUS:
  - **`imm:`** — v1 and `260916-kht-verify.py` byte-unchanged: **size THEN md5** (declared: v1 =
    18,309 B / 223 lines / `763f412bb1a8dbdb38f2cc332ed5a21d`; kht checker = 88,899 B / 1,711 lines /
    `50a4de7a954db77a6f162b9dcb573504` — **re-measure at BASIS, do not copy**), in the working tree
    AND at BASIS (`git diff --quiet BASIS -- <both>` rc 0). Same size-then-md5 shape as the posted
    anchors, for the same reason: a size failure must never silently produce a hash.
    ⚠ The negative control is NOT "a one-byte-altered copy hashes differently" — that proves md5 is
    injective, not that the CHECK can fail. The control is Task 3's form: run the `imm:` check
    function against an OVERRIDDEN path pointing at an altered copy and OBSERVE the `imm:` RED id.
  - **`sup:`** — `sup:names` v2's status block names v1's repo-relative path and contains
    SUPERSEDES with a one-line reason; `sup:untouched` v1's path is NOT in
    `git diff --name-only BASIS HEAD`; **`sup:noleak`** the supersession sentence contains NO defect
    COUNT (no digit-word or numeral quantifying defects, e.g. `seven`, `7 defects`) and NO option
    letter — telling a brief-blind adjudicator "seven defects" invites "which ones?", and one of them
    is that the structure leaked our recommendation.
  - **`basis:`** — v2 states the full 40-char BASIS SHA; the checker's `BASIS` equals it;
    `git merge-base --is-ancestor BASIS HEAD` rc 0; the newest `docs(quick-260916-vqp)` commit is an
    ancestor of BASIS; `c93e97b` occurs in v2 at most once and only in the supersession sentence.
  - **`bal:`** — the balance screen, MEASURED not asserted. Spans, tokenization, bands and screen
    lists are all fixed in `<declared_screens>`; every check PRINTS its spans and numbers.
      * `bal:fields` — options A-F have the identical labelled sub-field set (print the per-option
        field lists).
      * `bal:reading` — per-option READING label count >= 1 and `max - min <= 1` (print the counts).
      * **`bal:readweight`** — per-READING word counts printed with their label and line range;
        **within each option** `max/min <= 2.0`, each READING scored INCLUDING its attributed
        sub-bullets per the S-2 attribution rule. **This is the check that catches the actual B2.3
        defect:** `bal:reading` counts LABELS and `bal:words` counts WHOLE OPTIONS, so a v2 whose
        Option B carries an 8-word READING 1 and a 90-word READING 2 would pass both while being as
        one-sided as v1. It does not pass `bal:readweight`.
      * `bal:words` — per-option heading+body word counts printed; `max/min <= 3.0`.
      * `bal:eval` — 0 hits of the DECLARED `EVAL_CUES` list across every option **heading AND
        body** (in kht this was INFO-only and scored 0/5 on v1; here it is a GATE with a real-text
        discrimination control, S-3).
      * `bal:precedent` — the R4-COVERAGE precedent is named in §4 and in **exactly** the declared
        fitting set `{A, C, F}` (S-5); and its §5 question occupies **neither the first nor the last
        slot**, with its index PRINTED. (Screening only the last slot would let the precedent be
        promoted to Q1 — more prominent by primacy, not less.)
      * **`bal:questions`** — every option A-F is named in at least one §5 question; the
        question -> option map is PRINTED; RED if any option is unnamed. ⚠ This is only meaningful
        because R4(vi) requires v2 to TAG each question with its option(s): measured, v1's questions
        name options by substance and only Q5 contains a literal letter, so a name-match gate on v1
        would be vacuous. v1 interrogates A, B, the precedent, X1 and D — and never C or E, from
        which an adjudicator can infer the live candidates with no evaluative word present.
  - **`c-halt:`** — every claim range into `.planning/debug/260824-STAGE-B-HALT-…md` is DISJOINT from
    the passages quick-260916-ocb FALSIFIED: the `ru_maxrss`-inheritance measurement and the
    "Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`" prescription (HEAD `:118-125`) and the
    "RAM-1 fix (TDD)" line (HEAD `:146`). ⚠ **Re-locate both by CONTENT at BASIS** — vqp inserts a
    "⚠ SUPERSEDED 2026-09-16" annotation into that file which may shift the line numbers; a
    hard-coded 118-125 would be a fixed-line pin on a file that just moved. Print the located ranges.
    Measured: none of v1's five citations into that file intersects either passage, so this is cheap.
  - `g:options` must now assert `["A","B","C","D","E","F"]`; `g:questions` asserts the actual
    question set v2 carries (numbering only — the SUBSTANTIVE question check is `bal:questions`,
    because asserting `["1".."5"]` alone is tautological).
  - **`--baseline` mode (restored from kht, W7).** Runs the citation families against **v1** at
    BASIS and prints its RED id set. The task then asserts **SET EQUALITY** between that id set and
    Task 1's MOVED/FALSE verdict set — not equality of counts. Aggregate-count agreement is the
    weaker form and can hide two opposite-sign component errors (memory:
    `feedback_aggregate_agreement_hides_component_errors`). A mismatch in EITHER direction is a
    FINDING to report.
`c-ast` anchors must be AST-located (symbol, enclosing function, statement identity) — **never** a
bare line number that merely falls inside a long function. Task 1's S2 finding is the reason.
`c-hand` must recompute every stated number from its stated inputs, including the new Option D
runtime scalings and the region counts.

**(C2) WHAT IS FINALIZED HERE vs IN TASK 2b.**
  - **Finalized in 2a:** every constant re-derived in Task 1 (`BASIS`, the anchors and their
    controls, `PATHS`, `SINCE`/`SINCE_CONTROL`, the OD entry line found by heading search, the
    STATE.md marker, the `c-halt:` forbidden ranges); `Reader`; `norm`/`seg_in`; the `CITE` regex,
    key parsing and bare-ref resolution; `content_check`; and the IMPLEMENTATION of every family
    (`a: b: c-* c-ast: c-hand: c-halt: d: e: f: g: imm: sup: basis: bal:`); the declared
    `EVAL_CUES` and `G_PATTERNS` lists from `<declared_screens>`; both declared bands; `--baseline`,
    `--live`, `--source`, `--bare-ref-plan`, `--json` and the `--selftest` scaffold.
  - **Left for 2b:** the POSITIONAL `CLAIMS` table for v2 and `PERMITTED_EDITS`. In 2a the
    `--baseline` CLAIMS table is v1's 88 citations at their Task-1-re-derived BASIS ranges.

**(C3) RUN `--baseline` AND RECONCILE BY SET EQUALITY.** Run the citation families against **v1** at
BASIS. Expect RED. Then assert **set equality** between the RED claim-id set and Task 1's
MOVED/FALSE verdict set — ids, not counts. Print both sets and their symmetric difference. A
non-empty symmetric difference in EITHER direction is a **FINDING**: report it and STOP rather than
adjusting either side. This is the engine's positive control: it must find, on its own, exactly what
Task 1 found by hand.

**(C4) COMMIT** the checker alone, explicit path:
  `git add .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`
  `git commit -m "docs(quick-260916-vqq): the v2 re-verifier, constants re-derived at BASIS <short>; --baseline against v1 is RED and set-equal to the hand re-derivation" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"`
  Re-assert `imm:` after the commit. "invalid object" / "Error building trees" -> **STOP and report**.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; export PATH="$HOME/miniconda3/bin:$PATH" &amp;&amp; D=$(mktemp -d) &amp;&amp; python3 .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py --baseline --draft .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md &gt; "$D/base.txt" ; tail -2 "$D/base.txt" ; grep -qE '^RESULT RED ' "$D/base.txt" &amp;&amp; grep -qE 'baseline-set-equal' "$D/base.txt" &amp;&amp; test "$(md5sum .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md | cut -d' ' -f1)" = 763f412bb1a8dbdb38f2cc332ed5a21d &amp;&amp; test "$(md5sum .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | cut -d' ' -f1)" = 50a4de7a954db77a6f162b9dcb573504 &amp;&amp; test -z "$(git log --format=%H --grep='^docs(quick-260916-vqq)' | while read h; do git diff --name-only "$h~1" "$h" -- src tests config workflow bin scripts Snakefile; done)" &amp;&amp; test -z "$(git status --porcelain --untracked-files=no)" &amp;&amp; rm -rf "$D" &amp;&amp; echo TASK2A-OK</automated>
  </verify>
  <done>
The checker exists with every constant re-derived at BASIS (none copied from kht because it was green
there); all families including `c-halt:`, `imm:`, `sup:`, `basis:` and the seven `bal:` checks are
implemented against the declared screens and bands; `--baseline` against v1 is RED and its RED
claim-id set is SET-EQUAL to Task 1's MOVED/FALSE set with the symmetric difference printed as empty
(the line carries a `baseline-set-equal` marker); the checker is committed alone; v1 and the kht
checker are byte-unchanged.
  </done>
</task>

<task type="auto">
  <name>Task 2b: Author draft v2 as a declared edit ledger over v1; reach GREEN with forward + reverse byte identity</name>
  <files>.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md, .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py</files>
  <action>
Author v2 **as a declared edit ledger over v1** (so nothing changes outside the ledger and v1's bytes
are recoverable by reversing it), then fill the checker's v2 `CLAIMS` table and `PERMITTED_EDITS` and
reach GREEN. The engine was already proven in 2a; **do not weaken any check, band or screen list to
reach GREEN.**

**(A) THE EDIT LEDGER (`PERMITTED_EDITS`).** Same mechanics as kht: ordered `E1..En`, each with
`{id, cls, old, new, why}`; every `old` occurs EXACTLY ONCE at its point of application in the
running text and every `new` EXACTLY ONCE in v2. Classes:
  - **cls 1** — status / supersession block.
  - **cls 2** — basis + anchors + Files-cited key + bare-ref expansions.
  - **cls 3** — citation corrections proven by live before-RED / after-GREEN `evidence` (every claim
    Task 1 marked MOVED or FALSE lands here).
  - **cls 4** — the review closures R1-R8, each carrying `label` (the review item) and `origin`
    (`"blast-radius 260916 finding B2, item <n>"`).
`f:reverse` reverse-applies `En..E1` to v2 and MUST reproduce v1 byte-exactly (size THEN md5
`763f412bb1a8dbdb38f2cc332ed5a21d`). `f:forward` applies `E1..En` to v1 and must reproduce v2's bytes.

**(B) WHAT v2 MUST SAY.** Every item below is mandatory; none may be deferred or softened.
R1-R8 and R8b are closed by ledger edits on v2; **R9 is closed by a hand-off item in the report**
because its defect lives in the frozen, orchestrator-owned `.planning/STATE.md`.

  **R1 — basis.** (i) Replace "Code at HEAD `c93e97b`" with a BASIS statement giving the FULL 40-char
  SHA and its short form, the branch, and a reader-actionable reproduction instruction
  (`git show <short>:<path>`) plus the checker's path and how to re-run it. (ii) EVERY code/repo
  citation is the BASIS range from Task 1. (iii) `c93e97b` may appear ONLY in the one sentence that
  explains what changed since v1. (iv) The status block states, in one line, that v2 **SUPERSEDES**
  `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` for couriering. ⚠ **The reason
  must itself be brief-blind-safe: NO defect count and NO option letter.** Telling a brief-blind
  adjudicator "seven defects were found" invites "which ones?" — and one of them is that the
  structure leaked our recommendation. Use this shape: *"the code basis moved, so all citations were
  re-derived at a stated commit; the options section was restructured for symmetry."* Gated by
  `sup:noleak`. ⚠ v1 is NOT edited — an in-file "SUPERSEDED BY v2" pointer would break immutability;
  the supersession lives in v2 and in the report.

  **R2 — §4 heading.** Replace "(A, C, and B unless B's code also uploads evidence)". Uploading
  evidence fixes **X1 only**; X2 (scratch reclaimed only on `ok`), X3 (a deferred region has no `.npz`
  so it is recomputed on every re-fire) and X4 apply to B regardless. The new heading must scope B
  correctly and must include the new Option F wherever F leaves a region unbanked.

  **R3 — Option B.** (i) Add a counter-READING of the SAME weight as Option A's second reading, so B
  carries two competing readings rather than one flat "no". The counter-reading must be built from
  cited posted text (e.g. that mk7ze's "NO fourth branch and NO new token" is itself a commitment
  against token proliferation, which a reader could take as directing non-NONE/non-EXCLUDED
  dispositions to the SAME token rather than to a new one — state it as a READING, with its citation,
  and state the scope limit that the sentence is written about the companion condition). (ii) Remove
  the overreach "the mechanism for this class is already established for 00057": a mechanism is
  measured for ONE member (`m2_region_00057`); the second (`m2_region_00149`) is predicted, not
  observed (P5). Replace with the n=1-scoped statement and leave "is 're-diagnosis' already
  discharged for this class?" as an open question, not a finding.

  **R4 — re-balance.** (i) Every option A-F gets the SAME labelled sub-field set:
  **Behaviour / Code needed / Already pre-registered? / Consequences**. (ii) Every option's
  "Already pre-registered?" answer is an explicitly labelled **READING** (no flat conclusions), and
  the per-option READING count spread is at most 1. (iii) Per-option heading+body word counts must
  satisfy `max/min <= 3.0` — **this band, its span and its tokenization are declared in
  `<declared_screens>` S-1/S-2, before authoring; do not widen the band and do not re-tokenize to fit
  the text you wrote.** If an option cannot carry that much material without padding, invoke
  `<escape_hatch>`: STOP and report. (iv) The R4-COVERAGE precedent (the `deferred_infeasible_square`
  disclosure obligation with its named enforcer) is presented as ONE precedent attached to **exactly
  the options it fits — the unbanked set {A, C, F}** (S-5) — named in §4 and in those three option
  units; and its §5 question occupies **neither the first nor the last slot** (last = recency,
  first = primacy; both are emphasis). (v) No cue from the declared `EVAL_CUES` list appears in any
  option **heading or body** — this includes v1's two surviving cues, Option C's "already argues"
  and Option E's heading "(listed for completeness)". (vi) **Every §5 question carries an explicit
  option tag** (e.g. a trailing `(Options A, C, F)`) and the union of tags over all questions is
  exactly `{A,…,F}`, so no option is silently left un-interrogated. Measured: v1 interrogates A, B,
  the precedent, X1 and D and never C or E, which lets an adjudicator infer the live candidates
  without a single evaluative word. (vii) **Within each option the READINGs are balanced too:** per
  the S-2 attribution rule (sub-bullets count toward their READING) the within-option `max/min` must
  be `<= 2.0`. A two-label option whose second READING carries all the supporting bullets is the v1
  defect wearing a label. (viii) One neutral sentence states that the **A-F labels are inherited and
  alphabetical, carry no ranking, and §3's order is not a preference**.

  **R5 — Option E.** (i) Drop the heading cue "(listed for completeness)". (ii) Replace "The criterion
  is unchanged and fenced (T8)" with what the posted text actually says: trsx5:49 fences *choosing the
  occlusion criterion to obtain a particular fine-mapping result*, and mk7ze P302-305 explicitly
  separates recalibrating the GATE from that prohibited act — so "would changing the criterion for a
  stated methodological reason be the fenced act?" is an open question, not a closed one. (iii) Label
  `osf_deviations.md:670-671` **DRAFTED — NOT POSTED** where it is cited, and add the same label at
  the C-rate citation (v1 :168) — use the BASIS line numbers from Task 1 N3.

  **R6 — Option D.** (i) The pairwise-completeness scan alone is ANCHOR-RELATIVE; the list of regions
  expected to RAISE needs the separate `pcs_panelwide_reclassify` pass. Say both, with BASIS
  citations. (ii) State the MEASURED runtimes with instrument + run + region count (Task 1 N5) —
  **not** the brief's "1h53m for 21 regions". Any scaled number must be recomputed by the checker from
  its stated inputs. (iii) Move the mk7ze P88-89 / R255-256 citation onto the sentence it actually
  supports (the pre-committed 21-of-276 occlusion SAMPLE) and off the scan. (iv) D's "no amendment"
  becomes a labelled READING like every other option's.

  **R7 — missing content.** (i) A new §1 TEXT row for the RETAINED fully-NaN-row -> drop rule quoting
  **trsx5:37** and **mk7ze P321 / R488** verbatim (Task 1 N1) — the only posted rule that disposes of
  NaN-bearing variants. ⚠ **APPEND it as T9. Do NOT renumber T1-T8**: their ids are referenced by
  name throughout §3, §4 and §5, and renumbering would silently invalidate every one of those
  references. The checker carries a NAMED assertion that the **T1-T8 row text is byte-identical to
  v1's** (`f:` covers the file as a whole, but an invariant needs its own named enforcer). (ii) A new **Option F**: an operational `deferred_*` status NOT mapped to
  `BRANCH_AFR_OCC_DEFERRED`, on the `deferred_infeasible_square` analogue (Task 1 N8) — same four
  sub-fields, its own READING(s), its own consequences (verifier vocabulary, disclosure obligation,
  what it does and does not claim about the posted branch list). (iii) X1 gains the fact that the
  **excludelist and the occlusion manifest also upload only under `if ok:`** (Task 1 N7), so the
  closeout distributions lose more than the sidecar. (iv) A clearly labelled **LOW** subsection
  carrying three further options, each one or two sentences, each labelled LOW and each cited or
  explicitly marked uncited (Task 1 N9): a per-region pairwise-completeness pre-check at fire time
  (before hours of plink and the scratch cost); a re-run on a different sample set or with
  sample-level QC (which would need an amendment); and the effect on downstream AFR fine-mapping and
  coloc denominators. ⚠ The LOW subsection is EXCLUDED from the `bal:` per-option word counts — it is
  not an option body — and the checker must implement that exclusion explicitly.

  **R8b — the falsified halt-record passages (B5).** v2 cites
  `.planning/debug/260824-STAGE-B-HALT-…md` five times. Two passages in that file were FALSIFIED by
  quick-260916-ocb: the `ru_maxrss`-inheritance measurement plus the "Clean fix: `subprocess.Popen` +
  `os.wait4(pid, 0)`" prescription, and the "RAM-1 fix (TDD)" action line. Add **one line to v2's
  Files-cited key** stating that those RAM-measurement passages were falsified (pointing at the
  SUPERSEDED annotation vqp added to that file) and that **no citation in v2 depends on them**. The
  `c-halt:` gate proves the disjointness mechanically. Do NOT restate or rely on any number from
  those passages.

  **R8 — framing cues.** (i) Retitle §0 away from "Premise corrections…" to a neutral measured-premise
  heading. (ii) Replace "So the open question is not halt versus continue" — state that BOTH questions
  are open (C addresses the halt/continue question; A/B/F address the disposition question) without
  pre-dismissing either. (iii) Remove Option C's "the Stage B halt record already argues against
  this…": cite the halt record's sentence as TEXT, with no editorial verb. (iv) The C rate
  (1 of 21 -> ~13 of 276) must carry the ledger's OWN caveat that this sweep could observe only one
  side and that production tests the rate on BOTH sides (Task 1 N4), alongside the existing
  systematic-by-span and predicted-not-observed caveats.

  **R9 — hand-off closure. ORCHESTRATOR-OWNED, NOT a ledger edit.** B2 item 1's fifth sub-item —
  *"the courier caveat lives only under STATE item 2, not item 1's courier step"* — **cannot be
  closed inside v2**, because it is a defect in `.planning/STATE.md`, which is frozen and the
  orchestrator's. Closing it by editing STATE.md would violate `files_frozen`; leaving it unmentioned
  would make the closure map dishonest. So the executor closes it by **carrying verbatim replacement
  text in the report**, for the orchestrator to apply:
  ⚠ **Re-locate all four by CONTENT at BASIS, never by line number — vqp rewrites STATE.md.** The
  HEAD line numbers below are orientation only.
    - **`:39`** (the "OPTIONS DRAFT BANKED" bullet) — it says the kht checker is *"GREEN in default,
      `--source` and `--live` modes"*. The `--live` half is now FALSE. Supply replacement text that
      drops `and --live` and states that `--live` is RED **by design and permanently** (the checker is
      pinned at `c93e97b`, which is frozen), so no future reader mistakes it for a regression.
    - **`:54`** (the "judge two residual framing cues no word screen catches" item) — supply
      replacement text recording both cues as **CLOSED in v2** by R8(iii) (Option C's "already
      argues") and R5(i) (Option E's "(listed for completeness)" heading), and that both are now
      MACHINE-SCREENED by `bal:eval` with a real-text discrimination control.
    - **`:55`** (the bare "Courier the banked file to Seth, brief-blind") — supply replacement text
      adding the basis-commit courier caveat and pointing at **v2** as the file to courier.
    - **`:78`** (the "cites `run_native_ld_panel.py` at basis `c93e97b` … or re-base the citations
      first (Carter's call)") — supply replacement text recording that the re-base is **DONE** in
      v2 at BASIS, and that v1 plus its checker remain byte-frozen as the historical record.
  Each item in the report must be labelled `R9-<line>` with the OLD text quoted verbatim and the NEW
  text ready to paste. The closure map marks these `hand-off (orchestrator)`, not `ledger edit`.

  **Preserved from v1 and re-verified, not assumed:** the TEXT/CODE/READING label convention; the
  posted-anchor block (size THEN md5 with its control); the "what the posted text does NOT say" sweep;
  the Files-cited key; the single "with no recommendation" exemption phrase. Nothing that is still
  true is rewritten for its own sake.

  **⛔ BRIEF-BLIND.** v2 contains options, evidence, citations and neutral questions. NO
  recommendation, NO ranking, NO "we recommend / prefer / should", no option presented as the
  default, no option presented as a formality.

**(D) RUN IT.** Default mode must print a GREEN RESULT line (`parsed == table == verified ==` c-res
count) and exit 0. `--source <v1>` must additionally show `f:forward` PASS. Record both lines
verbatim. `--live` is expected GREEN at close-out too (v2 is written against BASIS == HEAD at this
point); if it is RED, report the RED ids rather than re-pinning BASIS.

**(D2) IF A DECLARED BAND CANNOT BE MET.** Invoke `<escape_hatch>`: print a line containing the
literal marker `VQQ-BAND-STOP` naming the band, the measured per-unit numbers, and what material
would have been required to meet it. Then STOP and report. Do NOT pad an option, widen a band,
re-tokenize, invent a citation, or cut substance from a long option. A declared `VQQ-BAND-STOP` is an
acceptable close-out; a silently-widened band is not.

**(E) COMMIT** — explicit paths only, both files in ONE commit:
  `git add .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`
  `git commit -m "docs(quick-260916-vqq): Stage C NaN error-posture options draft v2 (brief-blind; supersedes v1 for couriering; all citations re-derived at BASIS <short>; closes blast-radius B2 items 1-7) + its re-verifier" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"`
  Re-assert `imm:` after the commit. "invalid object" / "Error building trees" -> **STOP and report**.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; export PATH="$HOME/miniconda3/bin:$PATH" &amp;&amp; D=$(mktemp -d) &amp;&amp; python3 .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py &gt; "$D/default.txt" ; tail -1 "$D/default.txt" ; { grep -qE '^RESULT GREEN ' "$D/default.txt" || grep -qF 'VQQ-BAND-STOP' "$D/default.txt" ; } &amp;&amp; test "$(md5sum .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md | cut -d' ' -f1)" = 763f412bb1a8dbdb38f2cc332ed5a21d &amp;&amp; test "$(md5sum .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | cut -d' ' -f1)" = 50a4de7a954db77a6f162b9dcb573504 &amp;&amp; test -z "$(git log --format=%H --grep='^docs(quick-260916-vqq)' | while read h; do git diff --name-only "$h~1" "$h" -- src tests config workflow bin scripts Snakefile; done)" &amp;&amp; test -z "$(git status --porcelain --untracked-files=no)" &amp;&amp; echo TASK2B-OK</automated>
  </verify>
  <done>
v2 exists as a NEW file stating its BASIS and its supersession of v1 (with a reason carrying no
defect count and no option letter); the edit ledger reverse-applies to v1's exact bytes and
forward-applies to v2's; every R1-R8 and R8b sub-item is closed by a named ledger edit and R9 by a
named hand-off item in the report; the checker is GREEN in default mode with
`parsed == table == verified == c-res`; `imm:`, `sup:` (all three sub-checks), `basis:`, `c-halt:`
and all SEVEN `bal:` checks PASS — **or** a `VQQ-BAND-STOP` line is printed naming the band and its
measured numbers, with nothing padded and no band widened; v1 and the kht checker are byte-unchanged;
the commit touches no path under src/, tests/, config/, workflow/, bin/, scripts/ or Snakefile.
  </done>
</task>

<task type="auto">
  <name>Task 3: --selftest — every check family observed RED on a corrupted input; close-out assertions</name>
  <files>.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py</files>
  <action>
A GREEN is evidence ONLY because the engine has been seen to fail. Run and, if necessary, repair the
`--selftest` until every family is OBSERVED RED.

**(1) POSITIVE CONTROL FIRST.** `--selftest` must begin by running the real inputs and printing a
GREEN positive-control line. A RED positive control aborts the selftest.

**(2) MUTATIONS — at least one per family, ALL observed RED.** Each mutation must be proven to have
changed something (a mutation whose `old` does not occur exactly once, or that changes nothing, is a
selftest ERROR, not a pass). Work in a `tempfile.mkdtemp` directly under `$TMPDIR`, asserted to be
OUTSIDE the repo; refuse to run if `TMPDIR` is unset. Never mutate a file in the working tree.
Required coverage:
  - `a:` size, `a:` md5, `a:control` (a control range that DOES match must be RED — proving the
    anchor could otherwise not fail).
  - `b:` size, `b:md5`, `b:control`.
  - `c-key`, `c-count`, `c-res:`, `c:`, `c-quote:`, `c-bind:`, `c-pr:`.
  - `c-ast:` — at least one mutation that an old-style bare-line-number anchor would have MISSED
    (e.g. inserting an early return, or moving the anchored statement), proving the AST anchoring is
    strictly stronger than a line number.
  - `c-hand:` — a stated number altered by one.
  - `d:` — a stated sweep count altered by one, and a 0-hit term replaced by a term that DOES occur.
  - `e:` — the SINCE window widened so the log is non-empty, and the control window narrowed so it is
    empty (an empty control must be RED: an empty log proves nothing).
  - `f:` — `f:reverse` (any byte of v2 altered outside the ledger), `f:forward`, `f:unique:<Eid>`,
    `f:evidence:<Eid>` (a class-3 edit whose `after` equals its `before` must be RED),
    `f:bareplan`.
  - `g:status`, `g:exempt`, `g:options`, `g:questions`, and **`g:recommend` on TWO distinct injected
    forms** — one plain ("We recommend Option B.") and one markdown-obfuscated (e.g.
    `my **recom**mendation is Option A`), proving the normalization is doing work.
  - `imm:` — a one-byte-altered copy of v1 and of the kht checker each observed RED.
  - `sup:names` — the SUPERSEDES sentence removed.
  - `bal:fields` — one option's sub-field removed.
  - `bal:reading` — one option's READING label removed (spread goes to 2).
  - `bal:words` — one option unit padded/halved until the 3.0 band breaks.
  - **`bal:readweight`** — **halve one READING** inside an option that has two (and, separately,
    move that READING's sub-bullets under its sibling) until the within-option 2.0 band breaks.
    This is the mutation that would have caught the v1 defect, so it must be OBSERVED.
  - `bal:eval` — an injected cue, **PLUS the REAL-TEXT discrimination control (S-3)**: run
    `bal:eval` against v1's own Option C unit and Option E unit at BASIS and observe RED on
    `already argues` / `argues against` and on the HEADING cue `listed for completeness`. A synthetic
    injection alone is NOT sufficient — kht's inherited list scores 0/5 on v1 and would have passed
    a synthetic-only control while catching nothing real.
  - **`bal:precedent`** — two mutations: the precedent moved into the **final** question, and the
    precedent moved into the **first** question (primacy). Plus one that names it in a fourth option
    unit, breaking the exact `{A, C, F}` set.
  - **`bal:questions`** — one option's tag removed from every question, so the union is no longer
    `{A,…,F}`.
  - **`c-halt:`** — a citation injected into a falsified halt-record range (and one just outside it,
    which must stay GREEN, so the boundary is proven and not merely assumed).
  - **`imm:`** — for BOTH targets, run the `imm:` check function against an OVERRIDDEN path pointing
    at an altered copy and observe the `imm:` RED id. ⚠ Showing that "a one-byte-altered copy hashes
    differently" is NOT this control — that proves md5 is injective, not that the check can fail.
  - **`sup:noleak`** — a defect count injected into the supersession sentence ("seven defects"), and
    separately an option letter.
  - **`basis:`** — the stated BASIS SHA altered by one character; a `c93e97b` occurrence injected
    outside the supersession sentence.
  - **`--baseline` set equality** — one id removed from the expected MOVED/FALSE set, observed RED
    (so the reconciliation itself is proven able to fail, not just the families it reconciles).
Print `SELFTEST OBSERVED <id> -> <the RED line>` for each, and a final
`SELFTEST GREEN positive-control=GREEN observed=n/n`. Any NOT-OBSERVED family **BLOCKS close-out**:
fix the checker (never the assertion's expected value) and re-run.

**(3) CLOSE-OUT ASSERTIONS.**
  - `--json <path outside the repo>` writes valid JSON; re-running with a path INSIDE the repo is
    refused (rc 1, nothing written).
  - No duplicate result ids in any mode.
  - Default mode and `--live` both re-run and their RESULT lines recorded verbatim.
  - `imm:` re-asserted: v1 = `763f412bb1a8dbdb38f2cc332ed5a21d` / 223 lines; kht checker =
    `50a4de7a954db77a6f162b9dcb573504`.
  - `git diff --name-only <BASIS> HEAD` lists EXACTLY the three committed files and nothing else;
    `git status --porcelain --untracked-files=no` is empty.
  - Nothing fired: no network, no `gcloud`/`gsutil`/`wb`, no VM, no OSF, no Seth. $0.

**(4) COMMIT — only if the checker changed in this task.** Explicit path; message
`docs(quick-260916-vqq): selftest — every check family observed RED on a corrupted input (n mutations; positive control GREEN)`
with the `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer. If the checker is unchanged,
make NO commit and say so; the selftest evidence goes in the report.

**(5) REPORT** — for the orchestrator's SUMMARY: BASIS; the vqp gate evidence; the full list of v1
claims whose verdict was MOVED or FALSE with before/after; the R1-R8 closure map naming the ledger
edit that closes each sub-item; every RESULT line verbatim; the selftest observed/not-observed
counts; the per-option `bal:` numbers; the supersession statement; and anything measured that
contradicts the brief (notably the Option D runtime).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; export PATH="$HOME/miniconda3/bin:$PATH" &amp;&amp; D=$(mktemp -d) &amp;&amp; python3 .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py --selftest &gt; "$D/selftest.txt" ; VQQ_D="$D" python3 -c "import re,sys,os; t=open(os.environ['VQQ_D']+'/selftest.txt').read(); m=re.search(r'(?m)^SELFTEST GREEN positive-control=GREEN observed=(\d+)/(\d+)$',t); sys.exit(0 if (m and m.group(1)==m.group(2) and int(m.group(1))&gt;0 and 'NOT-OBSERVED' not in t) else 1)" &amp;&amp; python3 .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py --json "$D/vqq.json" &gt; "$D/json-run.txt" ; { grep -qE '^RESULT GREEN ' "$D/json-run.txt" || grep -qF 'VQQ-BAND-STOP' "$D/json-run.txt" ; } &amp;&amp; VQQ_D="$D" python3 -c "import json,os;json.load(open(os.environ['VQQ_D']+'/vqq.json'))" &amp;&amp; test "$(md5sum .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md | cut -d' ' -f1)" = 763f412bb1a8dbdb38f2cc332ed5a21d &amp;&amp; test "$(md5sum .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | cut -d' ' -f1)" = 50a4de7a954db77a6f162b9dcb573504 &amp;&amp; test -z "$(git log --format=%H --grep='^docs(quick-260916-vqq)' | while read h; do git diff --name-only "$h~1" "$h" -- src tests config workflow bin scripts Snakefile; done)" &amp;&amp; test -z "$(git status --porcelain --untracked-files=no)" &amp;&amp; rm -rf "$D" &amp;&amp; echo TASK3-OK</automated>
  </verify>
  <done>
`--selftest` prints a GREEN positive control and then OBSERVED RED for every check family including
all SEVEN `bal:` checks (with `bal:readweight` observed by halving one READING and by moving its
sub-bullets to its sibling, and `bal:eval` observed on v1's OWN Option C and Option E units at
BASIS — the real-text discrimination control), `c-halt:` with an in-range positive and a
just-outside negative control, `sup:noleak`, `bal:questions`, the `--baseline` set-equality
reconciliation, both `g:recommend` forms and both `imm:` targets via the overridden-path form, with
`observed == total`;
`--json` works outside the repo and is refused inside it; no duplicate ids; v1 and the kht checker
byte-unchanged; the BASIS..HEAD diff lists exactly the three committed docs files; the report carries
BASIS, the MOVED/FALSE list with before/after, the R1-R8 closure map and every RESULT line verbatim.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| posted OSF bodies -> v2 | A misquote or a mis-scoped fence becomes a false statement about a public pre-registration, carried to an external adjudicator. |
| repo at BASIS -> v2's citations | A stale or re-located citation points the adjudicator at the wrong code; this is exactly the defect v1 shipped. |
| v2 -> external adjudicator (Seth) | Any recommendation, ranking or emphasis asymmetry destroys the brief-blindness that is the whole point of the review. |
| checker -> reader of a GREEN | A check that cannot fail is a false assurance; a GREEN with no observed RED is not evidence. |
| this task -> v1 + the kht checker | An accidental edit to an immutable record destroys the reproducibility of the banked v1 verification. |
| this task -> src/, tests/, the fire path | Any code change here would enter the $385-1,084 Stage C fire path unreviewed. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-vqq-01 | Tampering | v1 draft + `260916-kht-verify.py` | mitigate | `imm:` family: size THEN md5 in the working tree AND at BASIS, plus `git diff --quiet BASIS -- <both>`, asserted before and after every task, with a one-byte negative control observed RED. `files_frozen` lists them; Task 1/2/3 verifies re-assert. |
| T-vqq-02 | Spoofing | citation ranges (a line number that "looks right") | mitigate | Every claim re-located by verbatim quote at BASIS, never by adding an offset; `c-bind:` binds each quote to its own paragraph unit; `c-pr:` re-derives mk7ze `P+167 == R`; MOVED/FALSE verdicts are findings, never adjustments. |
| T-vqq-03 | Repudiation | "what changed between v1 and v2" | mitigate | The edit ledger: `f:reverse` must-be-identity back to v1's exact bytes, `f:forward` to v2's, `f:unique` per edit — so nothing in v2 is undeclared and the delta is reconstructible forever. |
| T-vqq-04 | Information disclosure | our private recommendation leaking to the adjudicator | mitigate | `g:recommend` normalized pattern screen with a single declared exemption AND two observed-RED forms (plain + markdown-obfuscated); plus the `bal:` family measuring structural emphasis (fields, READING symmetry, word band, evaluative words, precedent placement) — because the v1 leak was structural, not lexical. |
| T-vqq-05 | Tampering | the fire path / any code | mitigate | `files_frozen` covers `src/ tests/ config/ workflow/ bin/ scripts/ Snakefile`; every task's automated verify asserts the BASIS..HEAD diff contains no such path and the tracked tree is clean; explicit-path staging only (never `git add .`). |
| T-vqq-06 | Elevation of privilege | a check that silently cannot fail (a green proxy) | mitigate | `--selftest` observes EVERY family RED, including `a:control` / `b:control` / `e:control` mutations whose whole purpose is to prove the control can match; a NOT-OBSERVED family blocks close-out; `SKIP` is treated as RED unless explicitly allowed; duplicate result ids are RED. |
| T-vqq-07 | Spoofing | a stale basis (citing HEAD while HEAD moves) | mitigate | `basis:` family: v2 states the full 40-char SHA, the checker's `BASIS` equals it, `merge-base --is-ancestor` to HEAD, and the vqp close-out commit must be an ancestor of BASIS. `c93e97b` is allowed at most once, only in the supersession sentence. |
| T-vqq-08 | Denial of service | the declared bands (3.0 option / 2.0 within-option) forcing artificial padding | mitigate | Both bands are declared in `<declared_screens>` BEFORE authoring, so they constrain the text rather than being fitted to it. The contract is closed at both ends: `<escape_hatch>` makes a declared `VQQ-BAND-STOP` (naming the band and its measured numbers) an ACCEPTABLE close-out, and Task 2b's `<verify>` accepts that marker as an alternative to GREEN — so the plan no longer demands GREEN while also blessing a STOP. Padding, band-widening, re-tokenizing and citation invention are all named prohibited. |
| T-vqq-11 | Spoofing | a screen authored after the text it screens (calibrate-to-pass) | mitigate | `EVAL_CUES`, `G_PATTERNS`, both bands, the span rules and the tokenization are all fixed in `<declared_screens>` before v2 exists; Task 2a builds and proves the engine BEFORE Task 2b writes a word of v2; and `bal:eval` must pass a REAL-TEXT discrimination control on v1's own Option C and Option E rather than only a synthetic injection. Measured motivation: kht's inherited `EVAL_WORDS` scores 0 hits on all five v1 option bodies. |
| T-vqq-12 | Tampering | citing a falsified passage of the Stage B halt record | mitigate | Pre-flight (g) STOPS unless vqp's "⚠ SUPERSEDED 2026-09-16" annotation is present at BASIS; the falsified ranges are re-located BY CONTENT (not hard-coded, because the annotation shifts the line numbers — memory `feedback_fixed_sha_whole_file_pin_is_a_timebomb` in spirit); `c-halt:` gates every claim range into that file for disjointness with an in-range positive control AND a just-outside negative control; and R8b requires v2's Files-cited key to say no citation depends on them. |
| T-vqq-09 | Information disclosure | egress / external contact | mitigate | Docs-only, stdlib-only, `git` as the only subprocess with `cwd=ROOT` and never `shell=True`, `--json` refuses any path inside the repo, no `src/` import, no network. No cloud, no OSF, no Seth, $0. |
| T-vqq-10 | Tampering | GPFS git object-store loss mid-commit | transfer | Known GPFS failure mode: "invalid object" / "Error building trees" -> STOP and report; recovery is the operator's documented recipe, not an improvised fix inside this task. |
</threat_model>

<verification>
1. `git status --porcelain --untracked-files=no` empty at every task boundary.
2. `git diff --name-only <BASIS> HEAD` lists EXACTLY:
   `.planning/quick/260916-vqq-.../260916-vqq-BASIS-AND-REDERIVATION.md`,
   `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md`,
   `.planning/quick/260916-vqq-.../260916-vqq-verify.py` — and nothing under
   `src/ tests/ config/ workflow/ bin/ scripts/ Snakefile`.
3. v1 md5 `763f412bb1a8dbdb38f2cc332ed5a21d` / 223 lines and kht checker md5
   `50a4de7a954db77a6f162b9dcb573504`, before AND after.
4. `260916-vqq-verify.py` default mode GREEN with `parsed == table == verified ==` c-res count —
   or a declared `VQQ-BAND-STOP`; `--source <v1>` adds `f:forward` PASS; `--live` recorded.
5. `--baseline` against v1 is RED and SET-EQUAL (ids, symmetric difference empty and printed) to
   Task 1's MOVED/FALSE verdict set.
6. `--selftest`: positive control GREEN, then `observed == total` with every family named, including
   **all seven** `bal:` checks (`fields reading readweight words eval precedent questions`),
   `c-halt:` with both an in-range and a just-outside control, `sup:noleak`, both `g:recommend`
   forms and both `imm:` targets via the overridden-path form.
7. `bal:eval`'s REAL-TEXT discrimination control on v1's Option C and Option E units at BASIS is
   observed RED.
8. `260916-kht-verify.py` default mode still GREEN (v1's banked verification is untouched), and the
   report states that its `--live` is RED **by design and permanently** and that its
   `SINCE = 2026-08-24` constant is now false.
9. Every R1-R8 and R8b sub-item mapped to a named ledger edit, and R9's four items mapped to named
   hand-off entries with verbatim replacement text, in the report; none deferred.
10. §1 rows T1-T8 byte-identical to v1's; the drop-rule row appended as T9 with no renumbering.
11. Zero network / cloud / OSF / Seth contact; $0.
</verification>

<success_criteria>
- A courier-ready v2 exists that an adjudicator can act on: it names its basis commit, every citation
  resolves at that commit, and it supersedes v1 with a stated reason.
- All seven B2 sub-items and the LOW framing list are closed, each by a named edit, none partially.
- Brief-blindness is MEASURED, not asserted: the recommendation screen and the five-check balance
  family are each observed able to fail.
- v1 and its checker are provably byte-unchanged, and v2's delta from v1 is fully declared and
  reversible to v1's exact bytes.
- No code changed anywhere; nothing fired; $0.
</success_criteria>

<output>
After completion, create
`.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-SUMMARY.md`
(NOT committed by the executor — the orchestrator commits PLAN/SUMMARY/VERIFICATION/STATE).
The report must carry:
- BASIS (full + short SHA); the vqp gate evidence; the halt-record SUPERSEDED-annotation evidence.
- Every v1 claim whose verdict was MOVED or FALSE, with before/after, **as a sorted id set**, plus
  the `--baseline` symmetric-difference line proving set equality.
- The **R1-R9 closure map**, each row marked `ledger edit` or `hand-off (orchestrator)`.
- **R9's four hand-off items** (`R9-39`, `R9-54`, `R9-55`, `R9-78`), each with the OLD STATE.md text
  quoted verbatim and the NEW text ready to paste — re-located by CONTENT at BASIS.
- Every RESULT / SELFTEST / `--baseline` line verbatim; the observed/not-observed counts.
- The per-option and per-READING `bal:` numbers with their printed spans, and an explicit note on
  whether they agree with the planner's v1 measurements (`A 296 / B 208 / C 136 / D 165 / E 49`,
  ratio 6.04) and with the revision brief's differing figures (208 vs 204, 6.04 vs 5.53).
- The supersession statement, and confirmation that its reason carries no defect count and no option
  letter.
- **A standing note for future readers:** `260916-kht-verify.py --live` is RED **by design and
  permanently** — it is pinned at the frozen `c93e97b`, so a RED there is the correct outcome and
  not a regression; and its `SINCE = 2026-08-24` constant is now false (RAM-1 touched
  `run_native_ld_panel.py` on 2026-09-16). Never re-pin it to make it green.
- Every measurement that contradicts the brief or the revision brief.
</output>

<revision_log>
## Revision round 1 (adopted in full)

Planner re-measured 15 coordinator claims before adopting. **12 reproduced exactly. 3 required
correction, and the corrections are in the plan text above:**

1. ⚠ **`listed for completeness` is in Option E's HEADING (`v1:187`), not its body.** The proposed
   real-text control ("run `bal:eval` against v1's Option C and Option E **bodies**") would have
   half-failed as written. Adopted with the mechanism corrected: `bal:eval` (and `bal:words`) scan
   **heading + body**, declared in S-1.
2. ⚠ **v1's §5 questions name options by SUBSTANCE, not by label** — measured, only Q5 contains a
   literal letter ("(D)"). A name-matching `bal:questions` gate would therefore have been vacuous.
   Adopted with the missing precondition added as **R4(vi)**: v2 must TAG each question with its
   option(s), which is what makes the gate real.
3. ⚠ **v1's word numbers differ from the brief's.** Measured (heading excluded, `str.split()`):
   `A 296 / B 208 / C 136 / D 165 / E 49`, **ratio 6.04**. The brief says B = 204 and ratio 5.53.
   Neither figure is adopted as authoritative; instead the **counting contract (span + tokenization
   + printed spans) is DECLARED in S-1**, because two independent counts of the same file already
   disagreeing is the definition of an unscoped count.

Also corrected while adopting: the `c-halt:` forbidden ranges are **re-located by content at BASIS**
rather than hard-coded at `:118-125`/`:146`, because vqp's annotation is inserted into that same
file and will shift them — a hard-coded range would be a fixed-line pin on a file that just moved.

**Blockers adopted:** B1 `bal:readweight` (+ the S-2 sub-bullet attribution rule, 2.0 band declared
pre-authoring, selftest mutation). B2 `EVAL_CUES` + `G_PATTERNS` declared in S-3/S-4 with the
real-text discrimination control. B3 `bal:precedent` first-AND-last + printed index, new
`bal:questions`, exact `{A, C, F}` fitting set in S-5. B4 new **R9** hand-off closure with four
verbatim STATE.md replacements + the honest closure-map must_have. B5 pre-flight annotation gate,
**R8b** Files-cited-key line, `c-halt:` gate with in-range and just-outside controls.

**Warnings adopted:** W6 `imm:` sizes declared (18,309 B / 223 lines; 88,899 B / 1,711 lines,
re-measure not copy). W7 `--baseline` restored with **set-equality** reconciliation. W8 Task 2 split
into **2a** (engine, proven on v1) and **2b** (author v2, reach GREEN). W9 band contradiction closed
via `<escape_hatch>` + the `VQQ-BAND-STOP` marker accepted by Tasks 2b/3 `<verify>`, and T-vqq-08
re-dispositioned `accept` -> `mitigate`. W10 T9 appended, T1-T8 no renumber + named enforcer. W11
supersession reason neutralised + `sup:noleak`. W12 `imm:` negative-control wording fixed to the
overridden-path form.

**Info adopted:** I13 neutral A-F label sentence (R4 viii). I14 floors raised (checker >= 1,400;
v2 >= 260). I15 standing note that kht `--live` is RED by design forever and its `SINCE` is false.
I17 `mktemp -d` replaces fixed names under the shared `$TMPDIR`.

**One tension flagged for the orchestrator:** W8's split takes the plan to **4 tasks**, above the
original "1-3 tasks" constraint. The ADOPT-ALL directive was taken as superseding it; if the 3-task
cap is hard, merge 2a and 2b back and keep 2a's `--baseline` step as its first numbered action.
Two threats were added: T-vqq-11 (calibrate-to-pass screens) and T-vqq-12 (citing a falsified
passage).
</revision_log>

<orchestrator_addendum date="2026-09-17" source="plan-checker iteration 2 (0 blockers / 3 warnings / 5 info) — ALL adopted under --auto --chain">
BINDING; overrides any conflicting text above. Record each in the SUMMARY with before/after.

**A-1 (W-A — the live leak channel).** `bal:eval` scans the **WHOLE draft**, not only option units: §0, §4, §5 and the LOW subsection included. (The LOW/table exclusions apply to `bal:words` / `bal:readweight` COUNTS only.) Reason, measured on v1: of its four residual framing cues, TWO sit outside any option unit — `v1:36` (§0 title "Premise corrections…") and `v1:68` ("the open question is not halt versus continue") — and v2 REWRITES exactly that prose (R8 i/ii, R4 vi tags, the precedent move). Add a `--selftest` mutation injecting an `EVAL_CUES` term into §0 and observe RED.

**A-2 (W-B — green-over-nothing).** The hardened "no code changed" gate PASSES with zero matching commits (measured: `git log --grep='^docs(quick-260916-vqq)'` empty → `test -z ""` → PASS). Append a non-empty assertion at every site: `&& test "$(git log --format=%H --grep='^docs(quick-260916-vqq)' | wc -l)" -ge N` with **N=1 in Task 2a**, **N=2 in Task 2b and Task 3**. This is the project's own baked failure mode (a check that collected zero keys and did not raise).

**A-3 (W-C — `bal:readweight` vacuity + S-2's false guarantee).** S-2's claim that `bal:reading` makes a single-READING option RED is FALSE: if all six options carry exactly one READING, `min == max == 1`, spread 0, `bal:reading` PASSES and `bal:readweight` has nothing to compare. Add: **RED unless at least one option carries >= 2 READINGs, AND Option B specifically carries >= 2; print the set of options actually compared.** Selftest: collapse B's two READINGs into one → observe RED.

**A-4 (W-C bis — anchor ambiguity).** Task 1(g)'s prose anchor `"RAM-1 fix (TDD)"` does NOT occur literally (the file has `**RAM-1** fix (TDD)`), and bare `RAM-1` is AMBIGUOUS (2 hits: `:112` NOT falsified, `:146` falsified). Rule: every `c-halt:` content anchor is matched under `norm()` and **asserted UNIQUE (hit count == 1) before use**; bare `RAM-1` is explicitly rejected.

**A-5 (I-1 — apples-to-oranges reconciliation).** `<output>`/`<revision_log>` tell the executor to reconcile `bal:words` against `A 296 / B 208 / C 136 / D 165 / E 49, ratio 6.04`, but those are **body-only** while S-1 declares `bal:words` scores **heading + body** = `A 307 / B 219 / C 147 / D 176 / E 60, ratio 5.12`. Quote BOTH rows, labelled `heading+body (what bal:words scores)` and `body-only (orientation only)`. Re-measure both under S-1 rather than copying either.

**A-6 (I-2..I-5 — small but real).** (i) Author the LOW subsection as its own `### ` heading so the span rule terminates naturally, and have `bal:words` assert no option span contains the token `LOW`. (ii) S-2's "etc." is closed: the terminators are exactly the four declared sub-field labels in R4(i), and S-1's `str.split()` tokenization applies to EVERY `bal:` count, `bal:readweight` included. (iii) Stale counts: wherever the plan says "the five-check balance family" read **seven-check**; wherever it says "the R1-R8 closure map" read **R1-R9 + R8b closure map**. (iv) Pre-flight (g) must key on the ASCII `SUPERSEDED 2026-09-16` (no glyph), matching vqp's own enforcer exactly.

**A-7 (residual leak channels — close two, record two).** (i) Extend R4(viii)'s neutral sentence to §5: "the question order follows the option order and carries no ranking" (primacy on Q1 is otherwise unscreened). (ii) Add to the LOW subsection: "brevity here reflects how much cited ground exists at BASIS, not a ranking" — and do NOT phrase it "for completeness" (now an `EVAL_CUE`). (iii) RECORD ON THE RECORD, in v2's own methods line and the SUMMARY, that §4 membership and per-option citation density are deliberately NOT screened because both are factually determined — balancing them would be falsification. (iv) Add an INFO-only `report:` sweep printing per-option citation counts so Carter can see the asymmetry without it becoming a gate.

**A-8 (keep in the record).** §5's Q3 contains the token `C7` (the CODE claim id for the `deferred_infeasible_square` precedent). A naive option-letter matcher would FALSE-MATCH Option C there and report C as interrogated when Q3 is the precedent question — which is precisely why R4(vi)'s author-time tags, not a regex, are what make `bal:questions` real. Say this in the SUMMARY so the reason survives.
</orchestrator_addendum>
