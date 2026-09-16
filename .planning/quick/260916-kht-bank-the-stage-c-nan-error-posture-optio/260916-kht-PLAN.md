---
phase: quick-260916-kht
plan: 01
type: execute
wave: 1
depends_on: []
mode: quick-full
branch: m3-W2-aou-deltas
worktree: none            # GPFS: worktrees disabled project-wide
docs_only: true           # src/ tests/ config/ workflow/ bin/ MUST be untouched
autonomous: true
push: false               # commit only; the orchestrator commits PLAN/SUMMARY/STATE afterwards
requirements: ["QUICK-260916-kht"]   # STATE.md RESUME item 1 (Stage C NaN error posture): bank the options draft for brief-blind adjudication

files_modified:
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md                        # CREATED (banked draft) — committed by executor
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py # CREATED (verifier) — committed by executor
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md # CREATED — NOT committed by executor (orchestrator commits it)

files_frozen:
  - src/**
  - tests/**
  - config/**
  - workflow/**
  - bin/**
  - .planning/amendments/**          # posted OSF bodies — NEVER edited
  - .planning/osf_deviations.md
  - .planning/HANDOFF.json
  - .planning/STATE.md               # the ORCHESTRATOR updates STATE.md after execution — never in a task

must_haves:
  truths:
    - "The options draft exists in the repo at .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md and its Status line says: banked in the repo, NOT sent to Seth, NOT decided, no code written"
    - "The banked file differs from the scratchpad source ONLY by the declared permitted edits E1-E17 (class 1 status, class 2 file-path key + bare-ref expansions, class 3 proven citation corrections, class 4 orchestrator-specified factual/citation-completeness/neutrality corrections): forward-applying them to the source is byte-identical to the banked file, and reverse-applying them to the banked file gives 16,817 B / md5 5e11157f3b56addada24134bd7e2225f"
    - "Every citation the parser finds in the banked draft (planner pre-check: 88 = 81 original + 7 added by class-4 edits) resolves to exactly one existing repo file, its quote/token is present inside the cited line range, every quote is bound to the same paragraph as its citation token, and parsed-count == hand-table-count == verified-count"
    - "Each class-3 citation correction is justified by a check that is RED on the pre-edit form and GREEN on the post-edit form, recomputed live by the committed verifier; each class-4 citation added by the orchestrator has its own verified claims row"
    - "The derived numbers (≈13, 0.3-66, ~10.5 h, ≈57.6 GB) are EXTRACTED from the banked text and RECOMPUTED; a regex that fails to match is RED"
    - "mk7ze anchor (lines 168-500 = 22,945 B / 13a49f54…) and trsx5 anchor (9,695 B / c19be8b2…) hold, and each anchor's negative control (lines 167-500; first 9,694 B) does NOT match"
    - "The §1 sweep counts (halt/abort/skip/partial/incomplete/feasib = 0; defer 17/4; raise 3/2) are recomputed from the normalized posted bodies and equal what the banked draft states"
    - "The three fire-path files have no commits since '2026-08-24 00:00:00 -0400', and the same git-log command since '2026-08-01 00:00:00 -0400' is non-empty"
    - "The banked draft contains no recommendation language (normalized screen), names Options A-E, and has exactly five adjudicator questions"
    - "Every check family (a, b, c incl. c-bind/c-hand/new-citation rows, d, e, f, g) has been OBSERVED RED on a deliberately corrupted input via --selftest (33 mutations), with the RED lines pasted verbatim in the SUMMARY"
    - "Zero changes under src/, tests/, config/, workflow/, bin/, .planning/amendments/, .planning/osf_deviations.md, .planning/HANDOFF.json, .planning/STATE.md"
  artifacts:
    - path: ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md"
      provides: "banked brief-blind Stage C NaN error-posture options draft (options + citations + neutral questions, no recommendation)"
      contains: "**Files cited**"
    - path: ".planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py"
      provides: "committed citation re-verifier with --selftest negative controls, --live and --baseline modes"
      contains: "--selftest"
  key_links:
    - from: "260916-kht-verify.py"
      to: ".planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md"
      via: "lines 168-500 byte extract → size 22945 then md5 13a49f543cabcc27ce9f1e589783c060; control lines 167-500 must NOT match"
      pattern: "13a49f543cabcc27ce9f1e589783c060"
    - from: "260916-kht-verify.py"
      to: ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt"
      via: "size 9695 FIRST, then md5 c19be8b2ad7cd6a45fee1d668d8a9cf9; control first 9694 B must NOT match"
      pattern: "c19be8b2ad7cd6a45fee1d668d8a9cf9"
    - from: "260916-kht-verify.py"
      to: ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md"
      via: "citation parser + Files-cited key resolution + positional reconciliation against the hand CLAIMS table"
      pattern: "Files cited"
    - from: "260916-kht-verify.py"
      to: "scratchpad source (md5 5e11157f3b56addada24134bd7e2225f)"
      via: "PERMITTED_EDITS forward identity (with --source) and reverse identity (always)"
      pattern: "5e11157f3b56addada24134bd7e2225f"
---

<objective>
Bank the orchestrator's read-only Stage C NaN error-posture OPTIONS draft into the repo at
`.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md`, changing it ONLY by the declared
permitted edits (status line; file-path key and bare-ref expansions; proven citation corrections;
and the orchestrator-specified class-4 factual, citation-completeness and neutrality corrections
F1/K1-K4/N1-N5), and prove every citation in it with a committed verifier whose every check family
has been observed RED on a corrupted input.

Purpose: the draft goes to an external methodological reviewer (Seth) BRIEF-BLIND, then Carter
decides. A wrong line number, a misquote, or a stray recommendation sentence would either mislead
the adjudicator or leak our reasoning. The citations are the load-bearing content, so they are
re-verified mechanically against the POSTED OSF texts and the shipped code, not by eye.

Output: (1) the banked draft (source + ONLY permitted edits), (2) `260916-kht-verify.py`,
(3) `260916-kht-SUMMARY.md` (not committed by the executor), with baseline REDs, corrections,
`diff -u`, final GREEN output and observed selftest RED lines pasted verbatim.

Out of scope, hard: NO posture code, NO recommendation, NO edit to any posted amendment,
osf_deviations.md, HANDOFF.json or STATE.md, NO cloud/gsutil/gcloud/OSF/network, NO Seth contact,
NO worktree, NO `git add -A`/`git add .`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/STATE.md  (READ ONLY lines 1-63; the file is 3,377 lines)

SOURCE (the draft to bank; outside the repo, read-only):
`/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md`
= 211 lines / 16,817 B / md5 `5e11157f3b56addada24134bd7e2225f`. Below this is `$SRC`.

Destination (banked): `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` (`$BANKED`).
Verifier: `.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py` (`$VER`).
Repo root: `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis` (run everything from here; absolute paths).
Python: `/usr/bin/python3` is **3.9.25** — stdlib only; no `match`, no runtime `X | Y` type unions.
Temp files: `export TMPDIR=<your own session scratchpad>` before any run; never `/tmp`, never inside the repo.

<cited_files>
Short key → full repo-relative path (these are the only files the draft cites):

| key | path |
|---|---|
| AP | `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md` |
| RF | `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md` |
| RN | `src/python/run_native_ld_panel.py` |
| FV | `src/python/fire_verifier.py` |
| PL | `src/python/plink_ld_to_npz.py` |
| OD | `.planning/osf_deviations.md` |
| HA | `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md` |
| DI | `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (NOT any of the other 11 `deferred-items.md` files) |
| MK | `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` (posted mk7ze body = repo lines 168-500; posted line P = repo line R − 167) |
| TR | `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt` (posted trsx5 body, whole file) |
| ST | `.planning/STATE.md` (read ONLY at BASIS, see below) |
| U7 | `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` (repo draft named by the draft as NOT the posted body) |
| TFV | `tests/m3/test_fire_verifier.py` |

All 13 are tracked at `c93e97b` (planner checked `git cat-file -e c93e97b:<path>`).
</cited_files>

<precheck>
PLANNER PRE-CHECK, 2026-09-16, HEAD `c93e97b`, tracked tree clean. These are EXPECTATIONS the
executor must REPRODUCE INDEPENDENTLY with the verifier. Never paste them into a PASS; never
force agreement. If a measured result differs, reconcile BY CLAIM ID and record it.

- mk7ze: `sed -n '168,500p'` = 22,945 B, md5 13a49f543cabcc27ce9f1e589783c060; `167,500` md5 = 8154025b50ef344cd43078f910add359 (≠, control OK).
- trsx5: 9,695 B, md5 c19be8b2ad7cd6a45fee1d668d8a9cf9; first 9,694 B md5 = 0775eef2aa3f4965c42375ed955aced0 (≠, control OK).
- TRAP: `wc -l` on trsx5 prints **58**, but the file has **59** lines (no trailing newline); the draft cites `trsx5:59`. Use `splitlines()`, never `wc -l`.
- Sweep over normalized posted bodies (markdown `*_\`` stripped, whitespace collapsed, lower-cased; hit = `str.count` substring occurrences): halt/abort/skip/partial/incomplete/feasib = 0 in both; defer 17 (mk7ze) / 4 (trsx5); raise 3 / 2; `deferred_infeasible_square` = 0 in both raw-lowercase AND underscore-stripped (`deferredinfeasiblesquare`) forms. All equal the draft.
- `git log --since='2026-08-24 00:00:00 -0400' --format=%H c93e97b -- RN FV PL` → empty, rc 0. Control `--since='2026-08-01 00:00:00 -0400'` → 6 commits (dd8f0b8 e5e7ac7 d7f3b18 d9fbc63 ee16f79 5284505; oldest 5284505). `git diff --quiet 5284505~1 c93e97b -- src/python/run_native_ld_panel.py` → rc 1 (control can fail). `git diff --quiet c93e97b -- RN FV PL` → rc 0.
- Parser (regex below) finds **81** citation tokens in the source and **88** in the banked file (81 + 7 new tokens introduced by class-4 edits E8-E12 — F1/E8 adds two: `run_native_ld_panel.py:806-815` and bare `:866-872`; E17 rewrites text around the existing `fire_verifier.py:335-336` token without adding one).
- Content checks on the SOURCE (table file + parsed range): exactly **2 RED** — **c30** and **c64**:
  - c30 `mk7ze P311 / R478` quotes "A region over the anomaly gate is deferred for re-diagnosis …"; R478 ends at "…is deferred for" and "re-diagnosis" is on R479 (P312). Correction: `mk7ze P311-312 / R478-479`.
  - c64 (Option A) quotes NONE as "the fine-mapping result stand unmodified" at trsx5:43; trsx5:43 reads "…the panel and fine-mapping result stand unmodified." — the quoted string is not a substring. Correction: quote `"the panel and fine-mapping result stand unmodified"`.
- Resolution on the SOURCE: no Files-cited key → every short-name backticked token is unresolved (RED). Nearest-preceding-explicit resolution of bare `:n` refs (with the key present) mismatches, greedily in reading order, at exactly **3** refs: `:1325-1328` (§0 P4; resolves to HA, intended RN), `:1068-1069` (§2 C2; resolves to HA, intended RN), `:967` (§3 Option A; resolves to AP, intended RN). After expanding those 3, the other two mismatches (`:1090` in C2 and `:1090` in Option A) resolve correctly.
- Normalized-.py trap: the quotes at `run_native_ld_panel.py:1325-1328` ("Stage C runs without --fail-fast") and `fire_verifier.py:381-389` span implicit string-literal concatenation (`"…Stage "` newline `"C runs…"`; `f"…report "` newline `f"these…"`). For `.py` haystacks also test a joined form: `re.sub(r'"\s*f?"', '', text)` before normalizing; a match in EITHER form passes.
- AST facts: PL:218 innermost def = `read_square_bin`; RN:1144 innermost def = `process_region`; RN:967 and RN:962-965 lie in the body of `if fired:`; RN:1106 and RN:1136-1139 lie in the body of `if ok:`; RN module constant `_DEFAULT_MAX_N_VAR = 120000`; TFV defines `test_shipped_status_vocabulary_is_covered_by_the_allow_list`.
- Arithmetic: 276/21 = 13.14 → "≈13"; Clopper-Pearson 95% for 1/21 = (0.001205, 0.23816) → ×276 = (0.33, 65.7) → "0.3–66"; 48×276/21/60 = 10.51 h → "~10.5 h"; 120000²×4/1e9 = 57.6 → "≈57.6 GB".
- (g) screen on the source: the only hit for `recommend` is the self-description "with no recommendation" (line 4) → handled by an exact-once exemption. Options A-E present; questions 1-5 present.
- ST (BASIS) frontmatter contains "Runtime 48m" in the 2026-09-01 block; OD line 534 `- **Status:** DRAFTED — NOT POSTED` precedes the cited entry lines 657-704.
- U7 md5 = 2af600e11c568fa14821382e9b4c3e81 (≠ trsx5 posted md5).
- REVISION-1 PRE-CHECK (all 17 edits E1-E17 prototyped against the real source, in list order):
  - every `old` occurs exactly once at its point of application; every `new` occurs exactly once in the result; reverse application in En..E1 order gives 16,817 B / md5 5e11157f…; banked = 223 lines (source 211 + 12 key lines; no class-4 edit changes the line count).
  - K4 exact strings (revision round 2, no nested parens): old `120,000-variant ceiling)` → new ``120,000-variant ceiling; `READY-TO-FIRE.md:369-370`)`` (source §4 X2 lines 192-193 read "…≈57.6 GB at the\n  120,000-variant ceiling) stays in scratch (C3)."; banked reads "…≈57.6 GB at the\n  120,000-variant ceiling; `READY-TO-FIRE.md:369-370`) stays in scratch (C3)."). The H1 bytes regex still matches after this form: (4, 57.6, 120,000).
  - New citation rows, all GREEN at BASIS: n01 `run_native_ld_panel.py:806-815` (parsed position 53, between c52 and c53) and n07 bare `:866-872` (pos 54, before c53); n02 `AGENT-PROMPT.md:393` (pos 71, between c68 and c69; AP:393 = "STEP 10 — GATE: STAGE C, THE FULL FIRE (~11 days, $385–1,084)."); n03 `osf_deviations.md:660-663` (pos 79) and n04 `mk7ze P88-89 / R255-256` (pos 80), both after c75; n05 `mk7ze P88-89 / R255-256` (pos 81, before c76); n06 `READY-TO-FIRE.md:369-370` (pos 86, between c79 and c80; RF:370 = "`--max-n-var` ceiling, default 120000 = the consumer's `m3_convert_max_n_var`)").
  - mk7ze R255 reads "*Pre-committed sample.* A systematic-by-span sample of 21 of the 276 AFR regions (20 selected"; the draft does NOT quote this sentence (K1/K3 cite it for a paraphrase / a count), so n04/n05 are kind **T**, not Q (a Q row would go `c-quote` RED because the words are not in the draft).
  - Greedy bare-ref plan computed on source + every non-bare-ref edit (E1, E2, E6-E17) is still exactly `:1325-1328`, `:1068-1069`, `:967` (parsed positions 23, 47, 68 in the banked order). F1's new bare `:866-872` resolves to `src/python/run_native_ld_panel.py` through the explicit `run_native_ld_panel.py:806-815` immediately before it in the same sentence, so the procedure does NOT expand it (and it must not be expanded); the new explicit tokens change no other bare-ref context.
  - H1 regexes (contract below) match on BOTH the source and the banked text: sample (1, 21); scale (276, 13, 95, 0.3, 66); runtime (21, 48, 10.5); panel 276; bytes (4, 57.6, 120,000); all recompute equal. d:parse terms = halt, abort, skip, partial, incomplete, feasib (all `^[a-z]+$`).
  - Paragraph binding: all 30 Q rows bind on the banked file AND on the source (c64 with its before-quote).
  - H2: `PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE` occurs exactly once in ST@BASIS frontmatter; the block up to the next ` PRIOR: ` contains `Runtime 48m`. H3: OD:532 is `## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure …`; no other `## ` heading follows before EOF (1022); its first `- **Status:**` line (534) contains `DRAFTED — NOT POSTED`; 657-704 lie inside it.
  - F1 code facts (S9, both early returns): RN:806 is `if existing is not None:` whose body ends in `Return` at 815, and the `ast.Try` at 825 (ends 1146) starts after it; RN:866 is `if pre_window_n_var > max_n_var:` whose body ends in `Return` at 872, before the sidecar assignment at 923 and `with open(gate_sidecar, "w")` at 925; the innermost def of 806, 815, 825, 866, 872, 923 and 925 is `process_region`. (Revision round 2 fixed F1's former already-banked gap; there is no open F1 note.)
  - Report-only sweep preview on the banked file: evaluative-word list → only `should` in §5 Q3 ("3. Should the R4-COVERAGE precedent…"); numeric-premise list is noisy (e.g. `STEP 10`, `question 5`, `−1/+1`) and is for the orchestrator to judge.
</precheck>

<verifier_contract>
Everything below is the contract the executor implements in `$VER`. It is written so no codebase
exploration is needed.

**Modes / CLI** (`argparse`):
- default: verify `$BANKED` in BASIS mode. `--draft PATH` overrides the draft.
- `--source PATH`: enables the forward-identity half of (f); asserts SIZE 16,817 first, then md5.
- `--baseline`: the draft IS the unmodified source; skip (f) with an explicit printed `SKIP f: baseline` line; use the CLAIMS table WITHOUT rows tagged with a class-4 edit id, and with each class-3-corrected row's `before` payload (from that edit's evidence). After Task 2 this mode must reproduce Task 1's RED id set EXACTLY (regression proof that banking did not loosen the engine).
- `--live`: read cited files from the WORKING TREE instead of `git show c93e97b:<path>`; (e) uses `HEAD` instead of `c93e97b` for `git log` and adds `git diff --quiet c93e97b -- RN FV PL`. ST is ALWAYS read at BASIS (it is a living log; the draft cites a dated observation in it).
- `--bare-ref-plan`: requires `--source`; applies every NON-bare-ref permitted edit (E1, E2, E6-E17) in memory, then greedily (reading order) finds the first bare `:n` whose resolved file ≠ CLAIMS file, expands it (prefix `run_native_ld_panel.py` / the table file's short name inside the backticks), repeats until none; prints the ordered list. Read-only.
- `--selftest`: see Task 3.
- `--json PATH`: also write all results as a JSON list of `{"status": "PASS"|"RED"|"SKIP"|"INFO", "id": str, "msg": str}` (PATH must be outside the repo; resolve it and refuse a path inside ROOT).
- Output: one line per check: `PASS <id> <msg>` / `RED  <id> <msg>` / `SKIP <id> <msg>`; report-only lines are `INFO <id> <msg>` and are never counted as checks and never affect the exit code; final line `RESULT GREEN checks=<n> parsed=<p> table=<t> verified=<v>` (exit 0) or `RESULT RED <k>/<n> parsed=<p> table=<t> verified=<v>` (exit 1). Never exit 0 with a RED. SKIP is only allowed for `f:forward` without `--source` and `f` under `--baseline`.

**Constants:** `ROOT = Path(__file__).resolve().parents[3]`, assert `(ROOT/'.git').exists()`; `BASIS = "c93e97b"`; `SOURCE_SIZE = 16817`; `SOURCE_MD5 = "5e11157f3b56addada24134bd7e2225f"`; `MK_START, MK_END, MK_SIZE, MK_MD5 = 168, 500, 22945, "13a49f543cabcc27ce9f1e589783c060"`; `TR_SIZE, TR_MD5 = 9695, "c19be8b2ad7cd6a45fee1d668d8a9cf9"`; `OFFSET = 167`; `SINCE = "2026-08-24 00:00:00 -0400"`; `SINCE_CONTROL = "2026-08-01 00:00:00 -0400"` (explicit time + tz; never a bare date). Subprocess ONLY for `git` (`subprocess.run(["git", ...], cwd=ROOT, capture_output=True)` — EVERY git call passes `cwd=ROOT`; check `returncode` explicitly; never `shell=True`). Never import anything from `src/`. Every containment test (temp dir, `--json` path) compares `Path(...).resolve()` against `ROOT.resolve()` (`ROOT.resolve() == p or ROOT.resolve() in p.parents` → refuse).

**Reading:** `read_cited(key)` → bytes via `git show BASIS:<path>` (rc must be 0) or working tree under `--live`; decode UTF-8; lines = `text.splitlines()`; a 1-based inclusive range outside `[1, len(lines)]` is RED (never clamp).

**Normalization** (apply identically to BOTH sides): map `’‘`→`'`, `“”`→`"`; delete every `*`, `_`, `` ` ``; collapse `\s+` → single space; lower-case; strip. For `.py` haystacks ALSO build the joined variant (`re.sub(r'"\s*f?"', '', raw)` then normalize); a needle passes if found in either.

**Quote match (kind Q):** split the needle on `…` → normalized non-empty segments must occur IN ORDER in the haystack. **Token match (kind T):** every normalized token is a substring of the haystack; every `NOT` token is absent.

**Parser (exact regex):**
```python
CITE = re.compile(
    r'`(?P<file>[^`\s:]*(?:\.|…)(?:md|py|txt)):(?P<a>\d+)(?:-(?P<b>\d+))?`'
    r'|`:(?P<ba>\d+)(?:-(?P<bb>\d+))?`'
    r'|\btrsx5:(?P<ta>\d+)(?:-(?P<tb>\d+))?'
    r'|\bmk7ze P(?P<pa>\d+)(?:-(?P<pb>\d+))?(?:\s*/\s*R(?P<ra>\d+)(?:-(?P<rb>\d+))?)?')
```
Note `(?:\.|…)` — the draft writes `260824-STAGE-B-HALT-…md` with NO dot before `md`; a parser without `…` misses 5 HALT citations (planner's first prototype did; the count reconciliation caught it).

**Resolution:** backticked explicit file → the path itself if `(ROOT/file).is_file()`, else look up the short form in the draft's `**Files cited**` key; unresolved → `None` (RED `c-res:<id>`). Bare `:n` → file of the nearest PRECEDING backticked explicit-file citation (trsx5/mk7ze tokens do NOT change this context). `trsx5:n` → TR. `mk7ze P/R`: if R given, R range; if only P, R = P + 167; if both, assert R == P + 167 at both ends (`c-pr:<id>`).

**Files-cited key parse:** `re.search(r'\*\*Files cited\*\*[^\n]*\n((?:- [^\n]*\n)+)', draft)`; each line `- `short1`, `short2` → `full``; checks (`c-key`): block present; each full path `is_file()` AND `git cat-file -e BASIS:<path>` rc 0; each short fullmatches the path's basename via `'.*' + re.escape(short).replace(re.escape('…'), '.*')`; no short maps to two paths; each short occurs in the draft OUTSIDE the key block.

**Positional reconciliation:** `c-count`: `len(parsed) == len(CLAIMS)` (print both). `c-res:<id>`: resolved file == CLAIMS[i].file for every position. `c:<id>`: content check using CLAIMS[i].file + the PARSED range (so a changed line number in the draft is tested, not masked). For MK claims ALSO check the payload against the posted extract (repo lines 168-500 → list) at the P range (`c:<id>` fails if either fails). `c-quote:<id>`: for kind Q, each quote (as a whole, `…`-segmented) occurs in the normalized draft. `c-bind:<id>`: for kind Q, each quote occurs (normalized, `…`-segmented, in order) inside the PARAGRAPH UNIT that contains the citation token's start offset in the draft. Unit definition (deterministic): split the draft on `\n`; if the token's line starts (after spaces) with `|`, the unit is that line alone; otherwise walk UP from the token's line while the current line is not a list-item/heading start (`^\s*(- |\d+\. |#)`) and the line above is neither blank nor a table line, then walk DOWN while the next line is not blank, not a table line and not a list-item/heading start. `c-pr:<id>` is emitted for EVERY MK row (P-only rows PASS with msg "R derived = P+167"). `verified` = number of `c:<id>` PASS. GREEN requires parsed == table == verified == count(`c-res:*`).

**CLAIMS table** (positional, parsed reading order; transcribe EXACTLY; ids c01..c81; payload strings are raw and get normalized at check time):
```python
CLAIMS = [
 ("c01","AP","T",["run_native_ld_panel.py","--mode square","--ancestry afr"],["--fail-fast"]),  # `260812-ox1-AGENT-PROMPT.md:398`
 ("c02","AP","T",["without --fail-fast"],[]),                      # `:372-373`
 ("c03","AP","T",["without --fail-fast"],[]),                      # `:417`
 ("c04","RF","T",["the loop continues","partial bank"],[]),        # `260812-ox1-READY-TO-FIRE.md:360-366`
 ("c05","RN","Q",["Stage C runs without --fail-fast"],[]),         # `run_native_ld_panel.py:1325-1328`
 ("c06","PL","T",["raise ValueError","square LD carries NaN"],[]), # `plink_ld_to_npz.py:218-228`
 ("c07","RN","T",["plink_ld_to_npz("],[]),                         # `run_native_ld_panel.py:1090-1093`
 ("c08","RN","T",["except Exception","error: {e}"],[]),            # `:1144-1146`
 ("c09","RN","T",["append_panel_row("],[]),                        # `:1148`
 ("c10","RN","T",["if ok:","_gsutil_upload(out_npz"],[]),          # `:1101-1107`
 ("c11","RN","T",["if fail_fast and",'!= "ok"',"RegionGateError"],[]),  # `:1278-1279`
 ("c12","FV","T",["def _stage_c","classify_statuses"],[]),         # `fire_verifier.py:1097-1099`
 ("c13","FV","T",["_FAILURE_STATUSES",'"error:"'],[]),             # `:302-303`
 ("c14","FV","T",["_FAILURE_PREFIXES","STATUS_FAILURE"],[]),       # `:324-326`
 ("c15","FV","Q",["Stage C runs without --fail-fast so the loop continues by design; report these to Carter … Do NOT re-fire blindly"],[]),  # `:381-389`
 ("c16","FV","T",['"exit_code": 0 if not failed else 1'],[]),      # `:976-981`
 ("c17","AP","T",["R8.","exit 1 means STOP and report"],[]),       # `AGENT-PROMPT.md:55-61`
 ("c18","AP","T",["STOP under R8"],[]),                            # `:422-423`
 ("c19","FV","T",["A RED IS A STOP"],[]),                          # `fire_verifier.py:999-1001`
 ("c20","RN","T",["if fail_fast and",'!= "ok"'],[]),               # `run_native_ld_panel.py:1278`
 ("c21","RN","T",['"skipped_idempotent"',"return result"],[]),     # `:806-815`
 ("c22","HA","T",["m2_region_00001","m2_region_00017","m2_region_00040__sub14","all `ok`"],[]),  # `260824-STAGE-B-HALT-…md:20-21`
 ("c23","RN","T",["Deferrals (deferred_infeasible_square","also halt"],[]),  # `:1325-1328`  (EXPANDED in banked, E3)
 ("c24","HA","T",["m2_region_00057","read_square_bin","raised","square LD carries NaN"],[]),  # `260824-STAGE-B-HALT-…md:11-16`
 ("c25","OD","T",["m2_region_00149","offset -1","single survivor"],[]),  # `.planning/osf_deviations.md:657-663`
 ("c26","TR","Q",["The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract."],[]),  # trsx5:39
 ("c27","MK","T",["the raw-panel NaN-raise contract","continues to RAISE on any NaN"],[]),  # mk7ze P321-322 / R488-489
 ("c28","TR","Q",["If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation."],[]),  # trsx5:29
 ("c29","MK","Q",["Deferral remains NOT auto-exclusion. A region over the ceiling …"],[]),  # mk7ze P261 / R428
 ("c30","MK","Q",["A region over the anomaly gate is deferred for re-diagnosis …"],[]),  # mk7ze P311 / R478  (source: RED; banked P311-312 / R478-479, E6)
 ("c31","TR","Q",["the region's occlusion-exclusion count exceeds the anomaly gate"],[]),  # trsx5:47
 ("c32","MK","Q",["NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`"],[]),  # mk7ze P316-318 / R483-485
 ("c33","MK","T",["DEFERRED when EITHER condition holds","n_occluded_sites","n_occluded_rows / n_occluded_sites"],[]),  # mk7ze P155-158 / R322-325
 ("c34","TR","Q",["the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified."],[]),  # trsx5:43
 ("c35","TR","Q",["… fine-mapping proceeds on the reduced variant set"],[]),  # trsx5:45
 ("c36","TR","Q",["All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list."],[]),  # trsx5:49
 ("c37","TR","T",["deviations are logged in .planning/osf_deviations.md","disclosed in the manuscript"],[]),  # trsx5:53
 ("c38","MK","T",["deviation logging",".planning/osf_deviations.md","disclosure in the manuscript"],[]),  # mk7ze P323-324 / R490-491
 ("c39","TR","T",["Realized outcome branches","per-region exclusion manifest","present-rate","follow-up OSF update","closeout"],[]),  # trsx5:59
 ("c40","MK","Q",["Every region computes its own occlusion count AND its own occluded-site inflation during the production run, so both complete distributions fold in at closeout"],[]),  # mk7ze P247-250 / R414-417
 ("c41","TR","T",["correlation fabrication (NaN→0)","prohibited"],[]),  # trsx5:25
 ("c42","MK","T",["correlation","fabrication (NaN→0) both remain prohibited"],[]),  # mk7ze P307-308 / R474-475
 ("c43","TR","Q",["choosing the occlusion criterion to obtain a particular fine-mapping result"],[]),  # trsx5:49
 ("c44","MK","Q",["choosing the occlusion criterion to obtain a particular fine-mapping result"],[]),  # mk7ze P302-305 / R469-472
 ("c45","PL","T",["NaN check FIRST","zero-variance variant"],[]),  # `plink_ld_to_npz.py:213-228`
 ("c46","HA","T",["FALSIFIED","nan_count == 1","diag == 1.0"],[]),  # `260824-STAGE-B-HALT-…md:45-58`
 ("c47","RN","T",['result["n_dropped_occluded"] = n_dropped_occluded'],[]),  # `:1068-1069`  (EXPANDED in banked, E4)
 ("c48","RN","T",["pln.plink_ld_to_npz("],[]),                     # `:1090`
 ("c49","RN","T",['result["status"] = f"error: {e}"',"append_panel_row("],[]),  # `run_native_ld_panel.py:1144-1148`
 ("c50","RN","T",["if ok:","_gsutil_upload(out_npz"],[]),          # `:1101-1107`
 ("c51","RN","T",['if result["status"] == "ok":',"_reclaim_region_scratch("],[]),  # `:1149-1154`
 ("c52","RN","Q",["~30+ GiB/region … overflows any finite scratch disk"],[]),  # `:723-725`
 ("c53","RN","T",["occlusion_gate.json",'"occ_sites"','"n_sites"','"inflation"','"verdict"'],[]),  # `:923-939`
 ("c54","RN","T",["_gsutil_upload(","gate_sidecar"],[]),           # `:961-965`
 ("c55","RN","T",["gate_json","_gsutil_upload("],[]),              # `:1129-1139`
 ("c56","RN","T",["SKIP guard","existing",'"skipped_idempotent"'],[]),  # `:799-815`
 ("c57","FV","T",["def classify_statuses","THE GATES WORKING","FINDING","HARD_STOP","UNRECOGNIZED"],[]),  # `fire_verifier.py:330-399`
 ("c58","FV","T",["test_shipped_status_vocabulary_is_covered_by_the_allow_list"],[]),  # `:309-312`
 ("c59","RN","T",["deferred_infeasible_square","return result"],[]),  # `run_native_ld_panel.py:866-872`
 ("c60","DI","Q",["a DISCLOSURE OBLIGATION — not blocking the fire"],[]),  # `deferred-items.md:1148-1191`
 ("c61","FV","T",["def check_coverage_disclosure_resolved","R4-COVERAGE","deferred-items.md"],[]),  # `fire_verifier.py:875-939`
 ("c62","RF","Q",["a real, reportable outcome"],[]),              # `READY-TO-FIRE.md:360-366`
 ("c63","AP","Q",["a real, reportable outcome"],[]),              # `AGENT-PROMPT.md:424-428`
 ("c64","TR","Q",["the fine-mapping result stand unmodified"],[]),  # trsx5:43 (Option A)  TASK 1 value; TASK 2 sets it to "the panel and fine-mapping result stand unmodified" (E7)
 ("c65","TR","Q",["fine-mapping proceeds on the reduced variant set"],[]),  # trsx5:45
 ("c66","RN","T",["return result"],[]),                            # `:967`  (EXPANDED in banked, E5)
 ("c67","RN","T",["pln.plink_ld_to_npz("],[]),                     # `:1090`
 ("c68","TR","Q",["the three outcome branches … before any occlusion-handling code fires"],[]),  # trsx5:53
 ("c69","FV","T",['"counts": counts','"n_failed"'],[]),            # `fire_verifier.py:363-370`
 ("c70","OD","Q",["no covering record for EITHER member"],[]),    # `osf_deviations.md:703-704`
 ("c71","MK","T",["Clause (a), the occlusion criterion","flagged as an occluder"],[]),  # mk7ze P300-302 / R467-469
 ("c72","MK","Q",["NO new token"],[]),                             # mk7ze P316 / R483
 ("c73","FV","Q",["the gates working"],[]),                        # `fire_verifier.py:335-336`
 ("c74","HA","T",["MECHANISM CONFIRMED","0 of 871","perfectly confounded"],[]),  # `260824-STAGE-B-HALT-…md:150-179`
 ("c75","HA","Q",["`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown per-region failure rate"],[]),  # `260824-STAGE-B-HALT-…md:104-107`
 ("c76","OD","Q",["to be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"],[]),  # `osf_deviations.md:685-689`
 ("c77","OD","Q",["Production tests the rate on BOTH sides"],[]),  # `:682`
 ("c78","OD","Q",["NO PREDICATE CHANGE … calibrate-to-pass at n=1"],[]),  # `osf_deviations.md:670-671`
 ("c79","MK","Q",["both complete distributions fold in at closeout"],[]),  # mk7ze P247-250 (§4 X1)
 ("c80","MK","Q",["NO new token"],[]),                             # mk7ze P316 (§5 Q2)
 ("c81","MK","T",["both complete distributions fold in at closeout"],[]),  # mk7ze P247-250 (§5 Q4, no quote)
]
```
**Class-4 rows (inserted in TASK 2, not Task 1).** Give every CLAIMS row a 6th element `edit` (None for c01-c81). Insert, by parsed position in the banked draft:
```python
 ("n01","RN","T",['"skipped_idempotent"',"return result"],[],"E8"),        # `run_native_ld_panel.py:806-815` (F1)   — after c52
 ("n07","RN","T",["deferred_infeasible_square","return result"],[],"E8"),       # `:866-872` (F1, bare; resolves via n01) — after n01, before c53
 ("n02","AP","T",["~11 days"],[],"E10"),                                        # `AGENT-PROMPT.md:393` (K2)             — after c68, before c69
 ("n03","OD","T",["single survivor","21-region scan"],[],"E9"),                 # `osf_deviations.md:660-663` (K1)       — after c75
 ("n04","MK","T",["A systematic-by-span sample of 21 of the 276 AFR regions"],[],"E9"),   # mk7ze P88-89 / R255-256 (K1) — after n03
 ("n05","MK","T",["A systematic-by-span sample of 21 of the 276 AFR regions"],[],"E11"),  # mk7ze P88-89 / R255-256 (K3) — after n04, before c76
 ("n06","RF","T",["120000","--max-n-var"],[],"E12"),                             # `READY-TO-FIRE.md:369-370` (K4)        — after c79, before c80
```
Final banked order: c01..c52, n01, n07, c53..c68, n02, c69..c75, n03, n04, n05, c76..c79, n06, c80, c81 (88 rows; ids are not sequential — n07 was added in revision round 2). n04/n05 are kind T because the draft paraphrases mk7ze R255 rather than quoting it.

If a table-row RED is caused by the TABLE (payload not what the draft says, shown by `c-quote` RED, or a token the planner chose badly while the cited lines DO support the draft's claim — show the lines verbatim), fix the TABLE and record it in the SUMMARY. A draft correction (class 3) is permitted ONLY when the draft's own quoted words or line numbers are shown, verbatim, not to be inside the cited range. Never edit the draft to make a table token pass.

**Hand-only claims (not parser-derived; each its own id):**
- `a:*` (mk7ze): extract = bytes of lines 168-500 inclusive (split bytes with `splitlines(keepends=True)`; this equals `sed -n '168,500p'`); SIZE first (`a:size`), then md5 (`a:md5`); control 167-500 md5 must NOT equal MK_MD5 (`a:control`; if it matches → RED "control matched: anchor cannot fail"); draft states `22,945 B`, `13a49f543cabcc27ce9f1e589783c060`, `8154025b` (normalized-substring checks, `a:draft`) and the computed control md5 starts with `8154025b` (`a:control-prefix`).
- `b:*` (trsx5): `b:size` FIRST (if it fails, do NOT compute md5; emit `b:md5` as RED "not computed: size failed"); `b:md5`; `b:control`: md5 of first 9,694 B must NOT equal TR_MD5; `b:draft`: draft states `9,695 B` and the md5.
- `c-ast:S1` PL:218 innermost `FunctionDef` (by `lineno`/`end_lineno`) is `read_square_bin`; `S2` RN:1144 → `process_region`; `S3` RN:967 is inside the BODY of an `ast.If` whose `ast.get_source_segment` test == `fired`; `S4` RN:962-965 same (`fired`); `S5` RN:1106 in body of `if ok`; `S6` RN:1136-1139 in body of `if ok`; `S7` RN module-level `_DEFAULT_MAX_N_VAR` literal == 120000; `S8` TFV defines `test_shipped_status_vocabulary_is_covered_by_the_allow_list`; `S9` (F1 evidence, BOTH early returns) RN has (i) an `ast.If` at line 806 whose test source == `existing is not None` and whose body's last statement is `ast.Return` ending at 815, with 815 < the `lineno` (825) of the `ast.Try` whose span contains 866 and 923; and (ii) an `ast.If` at line 866 whose test source == `pre_window_n_var > max_n_var` and whose body's last statement is `ast.Return` ending at 872, with 872 < 923 (sidecar assignment) ≤ 925 (`with open(gate_sidecar, "w")`); the innermost FunctionDef of 806, 815, 866, 872, 923 and 925 is `process_region`; (iii) EXHAUSTIVE (orchestrator revision 2, from checker iteration 2 Info 1): the set of `ast.Return` line numbers whose INNERMOST enclosing FunctionDef is `process_region` and whose line < 923 == {815, 872} exactly (the nested `_site` helper's return at 891 is excluded by the innermost-function rule — assert that exclusion explicitly, so a rule change that starts counting 891 goes RED); and (iv) the only `ast.If`/`ast.Try`/`ast.With`/`ast.For`/`ast.While` nodes whose span encloses line 923 are the `ast.Try` at 825 and the `ast.If` at 850 whose test source == `mode == "square"`. Add selftest mutation ST-s9 (on a temp copy of RN at the basis, insert a new line `        if False:\n            return result` immediately before the sidecar assignment at 923, keeping indentation valid → expect RED `c-ast:S9` naming part (iii)); mutation total becomes 33 wherever the plan states 32. One `c-ast:S9` result; its msg names which part failed.
- `c-hand:H1` arithmetic: EXTRACT every input and every stated value from the NORMALIZED draft with these regexes (each must match exactly once; a non-match or multiple matches → RED `c-hand:H1` naming the regex), then RECOMPUTE — never hardcode an input or a stated value:
  - sample: `r'(\d+) of (\d+) sampled regions'` → x, n
  - scale: `r'scaled to (\d+) that is ≈(\d+) regions, with an exact (\d+)% binomial range of ([\d.]+)–(\d+)'` → N, stated_mid, conf, stated_lo, stated_hi
  - runtime: `r'the (\d+)-region run took (\d+) min \(.*?\), which scales linearly to ~([\d.]+) h'` → n_run, minutes, stated_hours
  - panel: `r'scan across all (\d+) afr regions'` → N_panel
  - bytes: `r'\(nvar² × (\d+) b; ≈([\d.]+) gb at the ([\d,]+)-variant ceiling'` → bytes_per_cell, stated_gb, cap (strip commas)
  - recompute: `round(x/n*N) == stated_mid`; Clopper-Pearson two-sided `conf`% for (x, n) by bisection on the exact binomial CDF (stdlib `math.comb`, alpha = (100-conf)/200): `round(lo*N, 1) == stated_lo` and `round(hi*N) == stated_hi`; `round(minutes*N_panel/n_run/60, 1) == stated_hours`; `round(cap**2*bytes_per_cell/1e9, 1) == stated_gb` and `cap == ` the S7 literal. (Planner validated all five regexes on the source AND the post-edit banked text — K1, K3, K4 do not break them.)
  - `H2` ST at BASIS: frontmatter (text between the first two `---` lines) contains `PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE` EXACTLY once; the BLOCK from that marker to the next occurrence of ` PRIOR: ` (or end of frontmatter) contains `Runtime 48m` (raw, case-sensitive). Marker is a parameter (selftest ST-h2).
  - `H3` OD: line 532 (a parameter; selftest ST-h3) matches `^## `; the ENTRY = lines 532 .. (next `^## ` line − 1, or EOF); the cited range 657-704 lies inside the entry; the entry's FIRST line matching `^- \*\*Status:\*\*` contains `DRAFTED — NOT POSTED`. `H4` U7 exists and its md5 ≠ TR_MD5. `H5` the draft states `Code at HEAD` `c93e97b` and `git merge-base --is-ancestor c93e97b HEAD` rc 0.
- `d:*` sweep: parse from the normalized draft with `r'and searched\. (.+?): 0 hits in either\. control: defer has (\d+) hits in mk7ze and (\d+) in trsx5; raise has (\d+) and (\d+),'` (RED `d:parse` if no match); split group 1 on `", "`; `d:parse` is RED unless there is ≥ 1 term and every term fullmatches `^[a-z]+$`; recompute on normalized mk7ze extract (lines 168-500) and normalized trsx5 with `str.count`; each zero-term 0 in both (`d:zero:<term>`); `d:defer`, `d:raise` equal the parsed numbers; `d:dis` `deferred_infeasible_square` = 0 in both bodies in raw-lowercase and underscore-stripped forms AND the draft states the route is absent. A mismatch means the DRAFT is wrong (class-3 edit) — never change an expected number.
- `e:*`: `e:log` `git log --since=<SINCE> --format=%H <BASIS|HEAD> -- RN FV PL` (argv element `--since=2026-08-24 00:00:00 -0400`) rc 0 AND stdout empty; `e:control` same with `--since=<SINCE_CONTROL>` rc 0 AND non-empty (the since value is a function parameter so the selftest can swap it) (print count + oldest hash); `e:diff-control` `git diff --quiet <oldest>~1 <BASIS> -- src/python/run_native_ld_panel.py` rc == 1; under `--live` also `e:diff` `git diff --quiet c93e97b -- RN FV PL` rc 0. An rc-0 empty `e:log` is accepted ONLY when `e:control` in the same run is non-empty.
- Result ids are EXACT (the task verify commands look them up): one result each for `a:size a:md5 a:control a:draft a:control-prefix b:size b:md5 b:control b:draft c-count c-key d:parse d:defer d:raise d:dis e:log e:control e:diff-control g:status g:exempt g:recommend g:options g:questions f:forward f:reverse f:bareplan f:classes`; per-item ids are `c:<cid> c-res:<cid> c-quote:<cid> c-bind:<cid> c-pr:<cid> c-ast:S1..S9 c-hand:H1..H5 d:zero:<term> f:unique:E1..E17 f:evidence:E6 f:evidence:E7` (`e:diff` only under `--live`). Expected per-item counts on the banked draft: `c:` 88, `c-res:` 88, `c-quote:` 30, `c-bind:` 30, `c-pr:` 16. A family with several findings still emits ONE result under its exact id, listing every finding in `msg`.
- `g:*` on the normalized draft: `g:status` — the line starting `**Status:**` normalized contains `banked in the repo`, `not sent to seth`, `not decided`, `no code written`, and does NOT contain `not banked`; `g:exempt` — `with no recommendation` occurs EXACTLY once, then remove that one occurrence; `g:recommend` — zero matches for each of: `recommend`, `\bprefer`, `\bsuggest`, `\bpropos(e|es|ed|al)\b`, `\badvis(e|es|ed|able)\b`, `\bbest (option|choice|path|course)\b`, `\b(we|i) (favou?r|endorse|lean|urge|advocate)\b`, `\bin (our|my) (view|opinion|judgement|judgment)\b`, `\b(right|correct) (choice|option|call)\b`, `\bshould (choose|adopt|pick|go with|select)\b`, `\bopt for\b` (print each hit with context); `g:options` — `re.findall(r'(?m)^### Option ([A-E]): ', raw_draft) == ['A','B','C','D','E']`; `g:questions` — in the raw text after `## 5. Questions for the adjudicator`, `re.findall(r'(?m)^(\d)\. ', …) == ['1','2','3','4','5']`.
- `f:*` (Task 2): see Task 2.
- REPORT-ONLY (status INFO, never a gate; emitted in default/`--source`/`--live` runs on the draft, not under `--baseline`): `report:eval:<line>` — for each line of the draft, whole-word, case-insensitive hits from `["not workable", "unworkable", "realistic", "surprise", "only honest", "clearly", "obviously", "should", "better", "worse", "prefer", "simply", "merely", "of course", "naturally"]`, msg = words + the line text; `report:numeric:<line>` — for each line that has NO citation token, is outside the Anchors block and the Files-cited block, after deleting backticked code spans, `[PTCXRQ]\d+` labels, ISO dates `\d{4}-\d{2}-\d{2}` and leading list/heading numbering, the numbers matching `(?<![\w.])[+−-]?\d+(?:,\d{3})*(?:\.\d+)?` that are NOT in the derived-arithmetic set {1, 21, 276, 13, 95, 0.3, 66, 48, 10.5, 4, 57.6, 120,000, 17, 3, 2, 0}; msg = those numbers + the line text.
</verifier_contract>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Build the citation verifier and run the BASELINE against the unmodified source (expect RED, by claim id)</name>
  <files>.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py</files>
  <action>
PRE-FLIGHT (any failure → STOP and report; do not improvise):
1. `git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis log --oneline -3` and `git status --porcelain --untracked-files=no`. Record `HEAD0 = git rev-parse --short HEAD`. Planner saw HEAD `c93e97b` and an EMPTY tracked status. If HEAD0 ≠ c93e97b or tracked status is non-empty → STOP (another terminal / duplicate runner is writing; see feedback_gsd_quick_skill_runs_workflow_twice).
2. `$BANKED` and `$VER` must NOT exist yet → if either exists, STOP (duplicate runner).
3. `$SRC`: `stat -c %s` must be 16817 (SIZE FIRST), then `md5sum` must be 5e11157f3b56addada24134bd7e2225f. Else STOP.
4. `export TMPDIR=<your session scratchpad>`.

BUILD `$VER` with the Write tool (shebang `#!/usr/bin/env python3`, then `chmod +x`), implementing EVERY element of `<verifier_contract>` except the `f:*` checks and `--selftest` body (stub `--selftest` to print `RED selftest:not-implemented` and exit 1 until Task 3). Structure the checks as functions that RETURN a list of `(status, id, msg)` tuples and take their inputs (draft text, anchor bytes, CLAIMS list, mode) as parameters, so Task 3's selftest can call them on corrupted inputs; printing happens only in `main`. Module docstring must state: purpose (quick-260916-kht); BASIS = c93e97b and why (citations are verified against the immutable drafting basis; `--live` asks whether they are still current, and a `--live` RED after a later edit to a cited file is the CORRECT outcome — re-verify the draft, never re-pin); that `(g)` is a lexical screen that cannot prove neutrality; that ST is read at BASIS only; and the trsx5 `wc -l` = 58 vs 59-lines trap.

Transcribe the CLAIMS table exactly (c64 with its TASK-1 value "the fine-mapping result stand unmodified"). Do not "improve" tokens before the baseline — the baseline must test the table as planned.

RUN THE BASELINE:
`python3 $VER --baseline --draft "$SRC" --json "$TMPDIR/kht-baseline.json"; echo "rc=$?"` — expected rc 1. Save the full stdout to `$TMPDIR/kht-baseline.txt`.

RECONCILE BY CLAIM ID against `<precheck>` (not by count):
- Expected RED: `c:c30`, `c:c64`, `c-key` (no key block), `c-res:*` for every unresolved short-name token (and any bare-ref mismatches), `g:status` (source says "not banked").
- Expected PASS: all `a:*`, `b:*`, `c-count` (81 = 81), every other `c:*` (79 of 81 verified), all `c-pr:*`, all `c-quote:*`, all `c-bind:*` (c64 binds with its source quote), all `c-ast:*` (incl. S9), all `c-hand:*` (H1 regexes match the source text too), all `d:*`, all `e:*`, `g:exempt`, `g:recommend`, `g:options`, `g:questions`.
- If c30 or c64 PASSES: the engine is too lax (e.g. range clamped, quote not segmented in order, haystack wider than the range) → FIX THE ENGINE and re-run; never proceed on a green that should be red.
- If any OTHER `c:*` is RED: print the cited lines verbatim (`sed -n 'a,bp'` on `git show c93e97b:<path>`), then classify per the rule under the CLAIMS table (table error → fix table + record; draft defect → class-3 candidate for Task 2 with verbatim evidence). Record every such case for the SUMMARY.
- If `c-count` ≠ 81/81: the parser or the table is wrong — print the parsed token list and fix; do not proceed until parsed == table.
- If any `d:*` count differs: the DRAFT is wrong (class-3 candidate); never edit the expected number.
Also run `python3 $VER --baseline --live --draft "$SRC"` and confirm the SAME RED id set (tree == basis today).
  </action>
  <verify>
    <automated>: "${TMPDIR:?export TMPDIR=your session scratchpad first}" && cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && SRC=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md && VER=.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py && python3 $VER --baseline --draft "$SRC" --json "$TMPDIR/kht-baseline.json" >/dev/null; rc=$?; python3 -c "import json,sys; r=json.load(open(sys.argv[1])); red={x['id'] for x in r if x['status']=='RED'}; c={i for i in red if i.startswith('c:')}; bad=[i for i in red if i.split(':')[0] in ('a','b','d','e','c-count','c-pr','c-quote','c-bind','c-ast','c-hand') or i in ('g:exempt','g:recommend','g:options','g:questions')]; ok=(int(sys.argv[2])==1 and c=={'c:c30','c:c64'} and 'g:status' in red and any(i.startswith('c-key') for i in red) and not bad); print('baseline-reconciled' if ok else ('MISMATCH c=%s bad=%s rc=%s'%(sorted(c),bad,sys.argv[2]))); sys.exit(0 if ok else 1)" "$TMPDIR/kht-baseline.json" "$rc"</automated>
  </verify>
  <done>`$VER` exists (executable, stdlib-only, no src imports, no network, git-only subprocess). The baseline on the unmodified source exits 1 with RED set = {c:c30, c:c64, c-key, c-res:* (short names / bare refs), g:status} and PASS everywhere else, including a/b anchors with controls not matching, c-count 81=81, d sweep counts equal to the draft, e (empty since '2026-08-24 00:00:00 -0400', non-empty control since '2026-08-01 00:00:00 -0400', diff control rc 1), c-bind all PASS. Any divergence from `<precheck>` is reconciled by claim id and recorded for the SUMMARY (or the task STOPPED). Nothing committed; nothing under the repo created other than `$VER`.</done>
</task>

<task type="auto">
  <name>Task 2: Bank the draft with ONLY the permitted edits, encode them in the verifier with forward/reverse identity and live correction evidence, and reach GREEN</name>
  <files>.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md, .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py</files>
  <action>
STEP A — declare the permitted edits in `$VER` as an ordered list `PERMITTED_EDITS` of dicts `{id, cls, old, new, why, evidence}` (exact strings; `old` must occur EXACTLY once in the source, `new` EXACTLY once in the banked file). Start with E1 and E2 only:

E1 (class 1, Status line; per task constraint (1)) — source line 3:
old: `**Status:** DRAFT, not banked in the repo, no code written, **no decision made.** Built for review by`
new: `**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by`
(Do NOT touch line 4's "with no recommendation" or any other word of the Status paragraph.)

E2 (class 2, Files-cited key; per task constraint (2)) — old: "- Code at HEAD `c93e97b`.\n" ; new: old + the block below (it begins with a blank line; every line ends with `\n`; the existing blank line and `---` that follow stay untouched):
```

**Files cited** (short form used below → full repo-relative path):
- `260812-ox1-AGENT-PROMPT.md`, `AGENT-PROMPT.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`
- `260812-ox1-READY-TO-FIRE.md`, `READY-TO-FIRE.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
- `260824-STAGE-B-HALT-…md` → `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`
- `run_native_ld_panel.py` → `src/python/run_native_ld_panel.py`
- `fire_verifier.py` → `src/python/fire_verifier.py`
- `plink_ld_to_npz.py` → `src/python/plink_ld_to_npz.py`
- `osf_deviations.md` → `.planning/osf_deviations.md`
- `deferred-items.md` → `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`
- `STATE.md` → `.planning/STATE.md`
- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`
```

STEP B — implement `--bare-ref-plan` (it applies E1, E2 and the class-3/class-4 edits E6-E17 in memory before the greedy pass, so declare STEP C and STEP C2 edits first if you prefer; the planner verified the plan is identical either way) and run `python3 $VER --bare-ref-plan --source "$SRC"`. Paste its output into the SUMMARY. Planner expectation (reproduce, don't copy): exactly 3 expansions, in order, `:1325-1328` → `run_native_ld_panel.py:1325-1328`, `:1068-1069` → `run_native_ld_panel.py:1068-1069`, `:967` → `run_native_ld_panel.py:967`. Encode ONE class-2 edit per printed expansion with a unique context string, i.e. (if the plan output agrees):
- E3: old "It also halts on every deferral (`:1325-1328`)" → new "It also halts on every deferral (`run_native_ld_panel.py:1325-1328`)"
- E4: old "(set at `:1068-1069`" → new "(set at `run_native_ld_panel.py:1068-1069`"
- E5: old "returns at `:967`" → new "returns at `run_native_ld_panel.py:967`"
If the printed plan differs, encode what it prints and record the difference.

STEP C — class-3 corrections (per task constraint (3)): one edit per Task-1 draft-defect RED, each with `evidence = {"claim": id, "file": key, "before": {...}, "after": {...}}` giving the range(s) and payload before/after. Planner expectation:
- E6 (c30): old "mk7ze P311 / R478" → new "mk7ze P311-312 / R478-479"; evidence before = MK R478-478 AND posted P311-311 with quote "A region over the anomaly gate is deferred for re-diagnosis …"; after = R478-479 AND P311-312, same quote.
- E7 (c64): old `NONE needs "the fine-mapping result stand unmodified"` → new `NONE needs "the panel and fine-mapping result stand unmodified"`; evidence before = TR 43-43 quote "the fine-mapping result stand unmodified"; after = TR 43-43 quote "the panel and fine-mapping result stand unmodified". Update CLAIMS c64 payload to the "after" quote.
Do NOT rewrap lines.

STEP C2 — class 4 = ORCHESTRATOR-SPECIFIED factual, citation-completeness and neutrality corrections (revision round 1, 2026-09-16). Encode EXACTLY these ten edits, as Python string literals (`\n` = the source's real line break; continuation lines carry exactly two leading spaces), with `cls=4`, `label` (F1/K1…/N5) and `origin="orchestrator-specified, quick-260916-kht revision 1"`:
```python
E8  = ("F1", "is written locally for every square region before plink.",
             "is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:806-815`, an infeasible one at `:866-872`).")
E9  = ("K1", "rate:* 1 of 21 sampled regions carries a surviving pair. The sample was systematic-by-span, not\n  random,",
             "rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:660-663`). The sample was systematic-by-span, not\n  random (mk7ze P88-89 / R255-256),")
E10 = ("K2", "for the rest of the ~11 days.",
             "for the rest of the ~11 days (`AGENT-PROMPT.md:393`).")
E11 = ("K3", "scan across all 276 AFR regions before",
             "scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before")
E12 = ("K4", "120,000-variant ceiling)",
             "120,000-variant ceiling; `READY-TO-FIRE.md:369-370`)")
E13 = ("N1", "*READING 2 (the counter-reading, to be tested):*",
             "*READING 2:*")
E14 = ("N2", "literal `--fail-fast` is not workable (P4). The realistic form is the operator stopping\n  the fire at the first `error:` row.",
             "literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so\n  this option means the operator stopping the fire at the first `error:` row.")
E15 = ("N3", "turns a surprise into a pre-declared, measured set. Needs VM time (Carter).",
             "the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).")
E16 = ("N4", "A full-panel\n  scan *is* that test. Running D before the disclosure is posted would use up the prediction, unless\n  the prediction is explicitly retired first.",
             "A full-panel\n  scan would measure that same both-sides rate before production does; whether that uses up the\n  prediction is question 5.")
E17 = ("N5", 'A contract raise gets counted as "the gates working"\n  (`fire_verifier.py:335-336`), which is not the rationale that PASS was built on.',
             'A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"\n  (`fire_verifier.py:335-336`).')
```
Evidence to record per class-4 edit (SUMMARY §3b, and in the edit's `why`): F1 → `c-ast:S9` + rows n01, n07 (RN:806-815 returns `skipped_idempotent` before the `try:` at :825; RN:866-872 returns `deferred_infeasible_square` before the sidecar write at :923-939); K1 → rows n03, n04; K2 → n02; K3 → n05; K4 → n06; N1-N5 → "neutrality: orchestrator-specified", plus the post-edit `g:*` and report-only sweep outputs. Then insert CLAIMS rows n01-n07 (contract) at their positions. If any class-4 `old` does NOT occur exactly once in the source at its point of application, STOP and report the mismatch verbatim — never invent a variant.

No other edit of any kind. If you believe another change is warranted but it is neither a proven citation defect nor one of E8-E17, do NOT make it — list it in the SUMMARY under "Observations not acted on".

STEP D — create `$BANKED`: `cp "$SRC" .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md`, confirm md5 = 5e11157f…, then apply E1..E17 with the Edit tool as exact unique replacements, in list order E1, E2, …, E17 (Read the file first; for the multi-line class-4 edits make sure the Edit strings carry the real line break and the two-space indent). Expected result: 223 lines (source 211 + 12 key-block lines).

STEP E — implement the `f:*` checks in `$VER`:
- `f:unique:<Eid>` — `old` occurs exactly once in the source (when `--source`) and `new` exactly once in the banked draft.
- `f:forward` — with `--source` (size 16,817 then md5 checked first): applying E1..En in order to the source bytes == banked bytes exactly; without `--source` emit `SKIP f:forward no --source`.
- `f:reverse` — ALWAYS: reverse-applying En..E1 (`new` → `old`) to the banked draft gives SIZE 16,817 first, then md5 5e11157f3b56addada24134bd7e2225f. (This is the permanent must-be-identity proof; it does not need the scratchpad.)
- `f:evidence:<Eid>` — for each class-3 edit: the check on `before` is RED and on `after` is GREEN, recomputed live via the same content-check function (a before-GREEN means the edit was not needed → RED).
- `f:bareplan` — the greedy bare-ref plan recomputed from the reverse-applied source equals exactly the ordered class-2 bare-ref edits (E3..E5).
- `f:classes` — every edit has cls in {1,2,3,4}; exactly one cls-1 edit (E1); E2 is the only edit whose `new` has a different `\n` count from its `old` (+12); every cls-3 edit has `evidence`; every cls-4 edit has `label` and `origin`; ids are exactly E1..E17 in application order.

STEP F — reach GREEN, all three ways, each rc 0 with `parsed=88 table=88 verified=88` on the RESULT line:
`python3 $VER --source "$SRC"` ; `python3 $VER --live --source "$SRC"` ; `python3 $VER`.
Then the baseline regression: `python3 $VER --baseline --draft "$SRC" --json "$TMPDIR/kht-baseline2.json"` must exit 1 with a RED id set IDENTICAL to Task 1's `$TMPDIR/kht-baseline.json`.
Then `diff -u "$SRC" .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` and keep the full output for the SUMMARY (expected hunks only at: line 3, the insertion after line 20, and the lines carrying E3-E17). Capture every `INFO report:*` line for the SUMMARY.
  </action>
  <verify>
    <automated>: "${TMPDIR:?export TMPDIR=your session scratchpad first}" && cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && SRC=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md && VER=.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py && python3 $VER --source "$SRC" --json "$TMPDIR/kht-src.json" > "$TMPDIR/kht-src.txt" && python3 $VER --live --source "$SRC" --json "$TMPDIR/kht-live.json" > "$TMPDIR/kht-live.txt" && python3 $VER --json "$TMPDIR/kht-def.json" > "$TMPDIR/kht-def.txt" && { python3 $VER --baseline --draft "$SRC" --json "$TMPDIR/kht-baseline2.json" > /dev/null; echo $? > "$TMPDIR/kht-baseline2.rc"; } && python3 -c '
import json, os, re, sys
T = sys.argv[1]
ld = lambda n: json.load(open(os.path.join(T, n)))
FIXED = ["a:size","a:md5","a:control","a:draft","a:control-prefix","b:size","b:md5","b:control","b:draft","c-count","c-key","d:parse","d:defer","d:raise","d:dis","e:log","e:control","e:diff-control","g:status","g:exempt","g:recommend","g:options","g:questions","f:forward","f:reverse","f:bareplan","f:classes","f:evidence:E6","f:evidence:E7"]
FIXED += ["c-ast:S%d" % i for i in range(1, 10)] + ["c-hand:H%d" % i for i in range(1, 6)] + ["d:zero:" + t for t in ("halt","abort","skip","partial","incomplete","feasib")] + ["f:unique:E%d" % i for i in range(1, 18)]
bad = []
for js, txt, want_skip, extra in (("kht-src.json","kht-src.txt",set(),[]), ("kht-live.json","kht-live.txt",set(),["e:diff"]), ("kht-def.json","kht-def.txt",{"f:forward"},[])):
    st = {x["id"]: x["status"] for x in ld(js) if x["status"] != "INFO"}
    red = sorted(i for i, v in st.items() if v == "RED")
    skip = {i for i, v in st.items() if v == "SKIP"}
    miss = [i for i in FIXED + extra if i not in st]
    last = open(os.path.join(T, txt)).read().strip().splitlines()[-1]
    m = re.fullmatch(r"RESULT GREEN checks=(\d+) parsed=(\d+) table=(\d+) verified=(\d+)", last)
    cnt = lambda p, v=None: sum(1 for i, s in st.items() if i.startswith(p) and (v is None or s == v))
    ok = (not red and skip == want_skip and not miss and m is not None
          and int(m.group(2)) == int(m.group(3)) == int(m.group(4)) == cnt("c:", "PASS") == cnt("c-res:") == 88
          and cnt("c-quote:") == 30 and cnt("c-bind:") == 30 and cnt("c-pr:") == 16
          and (js == "kht-def.json" or st.get("f:forward") == "PASS"))
    if not ok:
        bad.append((js, red, sorted(skip), miss, last, cnt("c:", "PASS")))
b1 = {x["id"] for x in ld("kht-baseline.json") if x["status"] == "RED"}
b2 = {x["id"] for x in ld("kht-baseline2.json") if x["status"] == "RED"}
if open(os.path.join(T, "kht-baseline2.rc")).read().strip() != "1" or b1 != b2:
    bad.append(("baseline-regression", sorted(b1 ^ b2)))
print("green-full-id-set" if not bad else "FAIL %r" % (bad,))
sys.exit(0 if not bad else 1)
' "$TMPDIR"</automated>
  </verify>
  <done>`$BANKED` exists (223 lines) and equals the source plus ONLY E1 (status), E2 (Files-cited key), the greedy bare-ref expansions E3-E5 printed by `--bare-ref-plan`, the class-3 corrections proven by `f:evidence` (E6 c30 range, E7 c64 quote), and the ten class-4 orchestrator-specified edits E8-E17 with rows n01-n07. `$VER` is GREEN (rc 0) in `--source` and `--live --source` modes with ZERO SKIP and `f:forward` PASS, and in default mode with SKIP set exactly {f:forward}; every fixed id in the contract is present; RESULT parsed == table == verified == PASS `c:*` == `c-res:*` == 88; `c-quote:` 30, `c-bind:` 30, `c-pr:` 16; `f:reverse` = 16,817 B / 5e11157f…; `--baseline` reproduces Task 1's RED id set exactly. `diff -u` and all INFO report lines are captured. Nothing committed yet.</done>
</task>

<task type="auto">
  <name>Task 3: Implement and RUN --selftest (every check family observed RED), guard the scope, make the ONE atomic commit, re-verify at the new HEAD, write the SUMMARY</name>
  <files>.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py, .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md</files>
  <action>
STEP A — implement `--selftest` in `$VER` (replace the stub). Rules:
- Work only in `tempfile.mkdtemp(prefix="kht-selftest-")` under `$TMPDIR`; assert the temp dir is NOT inside ROOT by comparing `Path(tmp).resolve()` with `ROOT.resolve()` (GPFS paths can be reached through symlinks, so never compare unresolved strings); delete it at the end (`shutil.rmtree` in `finally`).
- POSITIVE CONTROL first: all checks on the real inputs + `$BANKED` (BASIS mode, no `--source`) must have ZERO RED; otherwise print `SELFTEST RED positive-control` and exit 1.
- Every mutation is an exact string/byte replacement that ASSERTS the `old` occurs exactly once and that the mutated input ≠ the original (a mutation that changes nothing must fail the selftest, never pass silently).
- A mutation counts only if at least one RED id STARTS WITH its declared family prefix; print `SELFTEST OBSERVED <ST-id> -> <that RED line verbatim>`; otherwise `SELFTEST NOT-OBSERVED <ST-id>` and the selftest exits 1.
- Final line `SELFTEST GREEN positive-control=GREEN observed=<k>/<k>` → exit 0.

Mutations (all 33 required):
| ST | input change | expected RED prefix |
|---|---|---|
| ST-a1 | MK bytes with `b"\n"` inserted at offset 0 | `a:` |
| ST-a2 | anchor called with start=169 on the real MK bytes | `a:` |
| ST-a3 | control range set to 168-500 (the real anchor) | `a:control` |
| ST-b1 | TR bytes + 1 trailing byte | `b:size` |
| ST-b2 | TR bytes with byte 100 changed (same size) | `b:md5` |
| ST-b3 | control length set to 9,695 | `b:control` |
| ST-c1 | draft: `` `:417` `` → `` `:422` `` | `c:c03` |
| ST-c2 | draft: in the T1 quote, `RAISE on any NaN rather` → `RAISE on every NaN rather` (must be unique; if not, widen context) | `c-quote:c26` |
| ST-c3 | CLAIMS copy: c26 payload `continues to RAISE` → `continued to RAISE` | `c:c26` |
| ST-c4 | draft: delete `` (`fire_verifier.py:363-370`) `` | `c-count` |
| ST-c5 | draft key: the `deferred-items.md` line's path → `.planning/quick/260908-n48-bank-the-seth-adjudication-closure-no-op/deferred-items.md` | `c-res:c60` |
| ST-c6 | draft: `mk7ze P261 / R428` → `mk7ze P262 / R428` | `c-pr:c29` |
| ST-c7 | AST check S2 expected name `main` | `c-ast:S2` |
| ST-d1 | draft: `17 hits in mk7ze` → `18 hits in mk7ze` | `d:defer` |
| ST-c8 | banked: `whose stated reason is "the gates working"` → `whose stated reason is "the gate outcome"` (the quote still exists in the C6 row, so only the binding breaks) | `c-bind:c73` |
| ST-n1 | banked: `` `AGENT-PROMPT.md:393` `` → `` `AGENT-PROMPT.md:398` `` (new class-4 citation row) | `c:n02` |
| ST-n2 | banked: `random (mk7ze P88-89 / R255-256)` → `random (mk7ze P88-89 / R256-257)` | `c-pr:n04` |
| ST-d2 | banked: `` `feasib`: **0 hits `` → `` `defer`: **0 hits `` | `d:zero:defer` |
| ST-h1 | banked: `≈13 regions` → `≈14 regions` | `c-hand:H1` |
| ST-h2 | H2 block marker := `PRIOR: 2026-09-01 — NO SUCH BLOCK` | `c-hand:H2` |
| ST-h3 | H3 entry heading line := 533 | `c-hand:H3` |
| ST-e1 | `e:control` run with since=`2026-08-24 00:00:00 -0400` (empty window) | `e:control` |
| ST-e2 | `e:log` run with since=`2026-08-01 00:00:00 -0400` (non-empty window) | `e:log` |
| ST-f1 | banked: `run the card as committed` → `run the card exactly as committed` | `f:reverse` |
| ST-f2 | E6 evidence with `after` := `before` | `f:evidence` |
| ST-f3 | banked + the E8 (F1) `new` sentence appended again at EOF | `f:unique:E8` |
| ST-s9 | temp copy of RN at the basis with `        if False:\n            return result` inserted immediately before the sidecar assignment (line 923) | `c-ast:S9` (part iii) |
| ST-g1 | banked + `\nWe recommend Option B.\n` appended | `g:recommend` |
| ST-g2 | banked + `\nmy **recom**mendation is Option A\n` appended | `g:recommend` |
| ST-g3 | banked: remove the `### Option E: ` heading line | `g:options` |
| ST-g4 | banked: remove the line beginning `5. Does a full-panel scan` | `g:questions` |
| ST-g5 | banked: Status line reverted to the E1 `old` | `g:status` |
| ST-g6 | banked + ` with no recommendation` appended | `g:exempt` |

(Adjust a mutation's exact string ONLY if its uniqueness assertion fails; keep the family and record the change.)

STEP B — RUN: `python3 $VER --selftest 2>&1 | tee "$TMPDIR/kht-selftest.txt"; echo "rc=${PIPESTATUS[0]}"  (PIPESTATUS, not $? — $? would be tee's)` → rc 0. Then re-run the three Task-2 GREEN commands (the selftest code must not have changed any verdict).

STEP C — SCOPE + MULTI-TERMINAL GUARD (any unexpected output → STOP and report, do not commit):
- `git log --oneline -3` → top commit still HEAD0 (c93e97b).
- `git status --porcelain --untracked-files=no` → EMPTY.
- `git status --porcelain --untracked-files=all -- src tests config workflow bin .planning/amendments .planning/osf_deviations.md .planning/HANDOFF.json .planning/STATE.md` → EMPTY.
- `git status --porcelain --untracked-files=all -- .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/` → shows `$BANKED`, `$VER` (and PLAN.md, which you do NOT stage).

STEP D — ONE ATOMIC COMMIT (explicit paths only; never `git add -A` / `git add .`):
`git add -- .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py`
`git diff --cached --name-only` → EXACTLY those 2 paths (else `git restore --staged` the extras and STOP).
Write the message to `$TMPDIR/kht-commit-msg.txt` and `git commit -F` it. Subject: `docs(quick-260916-kht): bank the Stage C NaN error-posture options draft (brief-blind, docs-only; <v> citations re-verified at c93e97b with observed-RED negative controls; <k> citation(s) corrected)` using MEASURED v and k. Body: what was banked, the permitted-edit classes with ids, the corrections (before → after, one line each), "NOT sent to Seth, NOT decided, no code written, no recommendation", and the verifier modes. Last line exactly: `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`
If the commit fails with "invalid object" / "Error building trees" (GPFS object-store loss) → STOP and report; do not improvise a recovery.

STEP E — POST-COMMIT: `test "$(git rev-parse HEAD~1)" = "$(git rev-parse c93e97b)"` (the new commit's parent must be c93e97b; this is the full-hash form of `git rev-parse --short HEAD~1` = c93e97b, immune to abbreviation length) — if it fails because the orchestrator or another writer moved HEAD, STOP and report; do not reset, rebase or force anything. Then `git show --stat --format='%h %s' HEAD` → exactly 2 files, both added; `python3 $VER` → rc 0 at the new HEAD (`H5` ancestry and `e:*` still hold); `python3 $VER --selftest` → rc 0.

STEP F — write `260916-kht-SUMMARY.md` (per the summary template; do NOT stage or commit it) containing, VERBATIM where marked:
1. HEAD0, commit hash, `git show --stat` output (verbatim).
2. Baseline on the source: the RED lines (verbatim) and the by-claim-id reconciliation against `<precheck>`, including any table fixes made and why.
3. Corrections table: Eid | claim | before | after | evidence (verbatim cited lines from `git show c93e97b:<path>` for the before/after ranges).
3b. Class-4 table: Eid | label | old | new (exact, as encoded) | evidence (F1: S9 + n01/n07 verbatim lines RN:806-815, :825, :866-872 and :923-939; K1-K4: rows n02-n06 with verbatim cited lines; N1-N5: "orchestrator-specified neutrality") — and the K4 exact old/new used.
4. `--bare-ref-plan` output (verbatim) and the class-2 edits it produced.
5. `diff -u "$SRC" "$BANKED"` (verbatim, complete).
6. Final GREEN RESULT lines for default / `--source` / `--live --source` (verbatim) with parsed / table / verified counts.
7. `--selftest` output (verbatim, every `SELFTEST OBSERVED` line + the final line).
8. The `e:*` lines (verbatim), including the non-empty control count and oldest hash.
9. Scope-guard outputs (verbatim).
10. Limits, stated plainly: `(g)` is a lexical screen, not a proof of neutrality (the brief-blind structure is the real safeguard); default-mode verdicts are pinned to the immutable basis c93e97b and `--live` will go RED when a cited file changes — that means re-verify the draft's line numbers before sending, not re-pin; `f:forward` needs the scratchpad source, `f:reverse` does not; ST is read at BASIS only.
11. "Observations not acted on" (if any).
11b. Report-only sweeps (not gates): every `INFO report:eval:*` and `INFO report:numeric:*` line from the final default run, verbatim, with banked line numbers, for the orchestrator to judge.
12. Status line for the orchestrator: banked, NOT sent to Seth, NOT decided, no posture code; STATE.md NOT touched (orchestrator updates it).
  </action>
  <verify>
    <automated>set -o pipefail && : "${TMPDIR:?export TMPDIR=your session scratchpad first}" && cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && VER=.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py && python3 $VER --selftest | tail -1 | grep -qx 'SELFTEST GREEN positive-control=GREEN observed=33/33' && python3 $VER | tail -1 && test "$(git rev-parse HEAD~1)" = "$(git rev-parse c93e97b)" && test "$(git show --name-only --format= HEAD | LC_ALL=C sort | tr '\n' ' ')" = ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py " && git log -1 --format=%B HEAD | sed '/^$/d' | tail -1 | grep -qx 'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>' && test -z "$(git status --porcelain --untracked-files=all -- src tests config workflow bin .planning/amendments .planning/osf_deviations.md .planning/HANDOFF.json .planning/STATE.md)" && test -f .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md && echo task3-ok</automated>
  </verify>
  <done>`--selftest` exits 0 with the positive control GREEN and all 33 mutations OBSERVED RED in their declared families (a, b, c incl. c-bind / c-hand / new class-4 rows, d, e, f, g all represented), output pasted verbatim in the SUMMARY. Exactly one new commit whose parent is c93e97b (`HEAD~1` checked by full hash), containing exactly `$BANKED` and `$VER`, message ending with the Co-Authored-By line. Post-commit default run and selftest both rc 0. Frozen paths untouched. SUMMARY written (not committed) with all 12 sections.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| session scratchpad → repo | the source draft lives outside version control and could be altered between drafting and banking |
| repo → external adjudicator (Seth) | the banked file will later be read brief-blind; any leak of our preferred option defeats the adjudication |
| posted OSF bodies (mk7ze, trsx5) → draft citations | the draft's authority rests on quoting the POSTED text, not the repo drafts |
| shipped fire-path code → draft CODE claims | line-cited behaviour must match the code that would actually run in Stage C |
| multi-terminal GPFS tree → commit | another terminal or a duplicate skill runner can write the same tree |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-kht-01 | Tampering | `$SRC` scratchpad draft | mitigate | SIZE-then-md5 pin (16,817 / 5e11157f…) before use; `f:forward` byte identity; `f:reverse` must-be-identity md5 committed in `$VER` |
| T-kht-02 | Tampering | banked draft wording drift | mitigate | `PERMITTED_EDITS` E1-E17 with exact-once old/new; forward and reverse identity; class-3 edits require live `f:evidence` (before RED, after GREEN); class-4 edits are exact orchestrator-specified strings with label/origin, and every citation they add has its own verified row |
| T-kht-03 | Information disclosure | recommendation leaking to the adjudicator | mitigate | `g:recommend` normalized lexical screen with exact-once exemption; observed RED on injected and markdown-split recommendations (ST-g1/g2/g6); limit stated in SUMMARY |
| T-kht-04 | Spoofing | citing a repo draft as the posted body | mitigate | anchors a/b with negative controls; mk7ze P/R double check (posted extract AND repo line, R = P + 167); H4 asserts the 07-10 repo draft ≠ posted md5 |
| T-kht-05 | Repudiation | "citations were verified" without evidence | mitigate | committed verifier + JSON/stdout evidence; selftest RED lines verbatim in SUMMARY; BASIS-pinned default mode stays reproducible |
| T-kht-06 | Tampering | concurrent writer on the GPFS tree | mitigate | pre-flight and pre-commit HEAD/tracked-status checks, destination-must-not-exist check, explicit-path staging, `git diff --cached --name-only` exactness, STOP on GPFS object-store errors |
| T-kht-07 | Elevation of privilege | agent drifting into cloud/OSF/Seth actions | accept | docs-only task; no credentials used; verifier subprocess limited to `git`; out-of-scope list in objective |
</threat_model>

<verification>
Phase-level checks (all from repo root):
1. `python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py` → `RESULT GREEN … parsed=88 table=88 verified=88`, rc 0, SKIP set exactly {f:forward}.
2. Same with `--live --source "$SRC"` → rc 0 (tree == basis today; forward identity holds).
3. `--selftest` → `SELFTEST GREEN positive-control=GREEN observed=33/33`, rc 0.
4. `git show --name-only --format= HEAD` → exactly the banked draft and the verifier; `git rev-parse HEAD~1` == `git rev-parse c93e97b`.
5. `git status --porcelain --untracked-files=all -- src tests config workflow bin .planning/amendments .planning/osf_deviations.md .planning/HANDOFF.json .planning/STATE.md` → empty.
6. The banked Status line reads: banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written.
</verification>

<success_criteria>
- The draft is banked at `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` with only the permitted edits E1-E17 (incl. the ten orchestrator-specified class-4 corrections), proven by forward and reverse identity.
- Every parsed citation (88) is resolved, verified inside its cited range against basis c93e97b, bound to its paragraph when quoted, and reconciled positionally against the hand table (parsed == table == verified).
- Every citation correction is justified live by a before-RED / after-GREEN check and recorded with verbatim evidence.
- Anchors, sweep counts, git freeze facts (explicit-tz since), AST facts (incl. S9) and arithmetic (extracted from the text, recomputed) all agree with what the draft states; report-only evaluative/numeric sweeps are in the SUMMARY for the orchestrator.
- No recommendation language; options A-E and questions 1-5 present.
- Every check family was seen RED on a corrupted input (selftest), with the RED lines in the SUMMARY.
- One atomic docs commit (2 files), Co-Authored-By trailer, no frozen path touched, nothing sent, nothing decided, no posture code.
</success_criteria>

<output>
After completion, create `.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md` (do NOT commit it; the orchestrator commits PLAN.md, SUMMARY.md and STATE.md).
</output>
