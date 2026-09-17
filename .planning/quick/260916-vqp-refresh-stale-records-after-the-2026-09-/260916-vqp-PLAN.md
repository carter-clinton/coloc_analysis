---
phase: quick-260916-vqp
plan: 01
type: execute
wave: 1
depends_on: []            # nothing to wait for; ordering INSIDE this plan is Task 1 -> 2 -> 3
mode: quick-full
branch: m3-W2-aou-deltas
worktree: none            # GPFS: worktrees disabled project-wide. Scratch work lives OUTSIDE the repo.
autonomous: true
push: false               # commit only; the orchestrator commits PLAN/SUMMARY/VERIFICATION afterwards
requirements: ["QUICK-260916-vqp"]   # 2026-09-16 blast-radius review findings B1, B8, B9, B10 (record propagation only)
basis: 621701c            # every "PRE" in this plan means `git show 621701c:<path>`

files_modified:
  # Task 1 — bank the review + as-of corrections inside three quick records
  - .planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md                  # CREATED, byte-identical copy
  - .planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md            # CREATED, byte-identical copy
  - .planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-SUMMARY.md        # APPEND ONLY
  - .planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-VERIFICATION.md   # APPEND ONLY
  - .planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-SUMMARY.md        # APPEND ONLY
  # Task 2 — the four history records (INSERTION ONLY, never an edit of existing text)
  - .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md               # PREPEND one dated block
  - .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md   # APPEND one section
  - .planning/osf_deviations.md                                                # INSERT one sub-entry inside the trsx5 section
  - .planning/DECISIONS.md                                                     # APPEND one DEC entry at EOF
  # Task 3 — the two resume surfaces (the only two files edited IN PLACE)
  - .planning/HANDOFF.json
  - .planning/STATE.md
  # written but NOT committed by the executor
  - .planning/quick/260916-vqp-refresh-stale-records-after-the-2026-09-/260916-vqp-SUMMARY.md        # CREATED, orchestrator commits

files_frozen:
  - src/**                     # NOTE: this repo has no top-level workflow/ dir; Snakemake lives in src/snakemake/ + ./Snakefile
  - tests/**
  - config/**
  - bin/**
  - Snakefile
  - .planning/amendments/**    # posted OSF bodies + AOU-LD-PIPELINE.md — READ ONLY, NEVER edited
  - .planning/ROADMAP.md
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md          # the banked Seth-bound draft — do NOT touch
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/**     # incl. 260916-kht-verify.py — RUN it, never edit it
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/**     # the runbooks belong to task 260916-vqr
  - .claude/skills/**                                                          # belongs to task 260916-vqr
  - .planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-VERIFICATION.md   # its off-by-one line counts are REPORTED, not fixed (out of scope)
  - everything else not listed in files_modified

must_haves:
  truths:
    - "Pre-flight passes only when: HEAD is 621701c with the three-commit log below, tracked tree is clean, origin/m3-W2-aou-deltas == HEAD, and 260916-kht-verify.py DEFAULT mode prints `RESULT GREEN checks=317 parsed=88 table=88 verified=88` BEFORE anything is written"
    - "Every number, SHA, line citation and measurement written into a record was RE-DERIVED by the executor at execution time with the command recorded beside it in the SUMMARY — the consolidated findings file is INPUT, never authority (it is itself wrong at least twice, AND its bytes are LIVE: see <input_errata> and M21)"
    - ".planning/HANDOFF.json still parses as JSON, no pre-existing key was dropped (PRE key set is a SUBSET of POST), every pre-existing array kept its length, and the only changed values are headline / resume_on_reconnect[1],[2],[3] / carter_decisions_outstanding[0] / repo_fixes_status[2] / suite_baselines / freeze_state / resume_entry_point / timestamp"
    - "HANDOFF history is PRESERVED, not replaced: `headline`'s PRE value is copied verbatim into the new key `headline_PRIOR_2026_09_16` (the file's own convention — headline_PRIOR_2026_09_01/_09_08/_09_09/_09_10 already exist), and every other edited string CONTAINS its PRE text verbatim as a substring (the file's in-place `⚠ CORRECTED …` / `Body preserved verbatim:` convention used by gates.m3_04b, gates.m3_04c, gates.trsx5_posted_body and repo_fixes_status[0])"
    - "`json.dumps(json.load(HANDOFF), indent=2, ensure_ascii=True)` is BYTE-IDENTICAL to the file on disk both before and after the edit (no trailing newline) — proven, so the diff contains only the intended value changes and no reformatting"
    - "STATE.md: every PRE line the plan touches survives verbatim as a substring of the POST file (only frontmatter `last_updated`'s value is replaced), and every `-` line in `git diff -U0 621701c HEAD -- .planning/STATE.md` is one of the declared touched lines"
    - "STATE.md's YAML frontmatter is no worse than PRE: `yaml.safe_load` still FAILS with the SAME `(type(e).__name__, e.problem)` as PRE and its `problem_mark` still lands on the `last_activity:` scalar in BOTH PRE and POST — the mark's line/column MOVE BY DESIGN (one inserted comment line + a longer scalar; measured PRE line 15/col 4421 -> POST line 16/col 4492) and must NOT be asserted equal; line 1 is the opening YAML fence, a closing fence still follows it (its number moves :24 -> :25 and is NOT pinned), the top-level key list and its order are unchanged, and the count of `\"` inside the `last_activity` scalar is unchanged from PRE (= 4, measured)"
    - "The four history records changed by INSERTION ONLY: for each, post == pre[:k] + INSERT + pre[k:] proven by a script that exits 0/1, whose negative control (one pre-existing byte mutated in a scratch copy) was observed to exit EXACTLY 1, and `git diff --numstat 621701c HEAD -- <file>` reports 0 deletions"
    - "The two banked blast-radius files are BYTE-IDENTICAL to their scratchpad sources, proven by `cmp -s` exit 0 PLUS an md5 measured on the SOURCE and on the BANKED COPY at copy time and found EQUAL — never a comparison against a digest written in this plan: the findings source is LIVE and has been corrected 6+ times on 2026-09-16 (20,410 B / 202 lines / 346a6f87… when this plan was written; 25,784 B / 213 lines / 3afb70fc3551cc86ae9c6fa9794eea29 at plan revision 1; it may move again before execution). codex-review.md read 5,256 B / 28 lines / fce1c52d53308ebffb00031714436193 at both measurements (informational). No banked-by header was added to either"
    - "The frozen/forbidden paths are untouched: `git status --porcelain -- <paths>` is empty AND `git diff --numstat 621701c HEAD -- <paths>` is empty; and `git diff --name-only 621701c HEAD` equals EXACTLY the 11 committed paths in files_modified"
    - "260916-kht-verify.py DEFAULT mode prints `RESULT GREEN checks=317 parsed=88 table=88 verified=88` again AFTER the last commit; `--live` is RED `RESULT RED 31/318 parsed=88 table=88 verified=64` before and after and is deliberately NOT fixed"
    - "No committed test reads any of these six records as a file path (re-derived by scanning tests/**/*.py), so no test run is required; the only references are three prose mentions in tests/m3/source_freeze.py:40 and tests/m3/test_source_freeze_pins.py:98/:188"
    - "Nothing fired: no cloud, no OSF, no Seth, no network, no VM, $0; no posted amendment body was edited"
  artifacts:
    - path: ".planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md"
      provides: "the consolidated 4-investigator + Codex review, banked as-received"
      contains: "Blast-radius assessment: branch m3-W2-aou-deltas, range c93e97b..621701c"
      min_lines: ">= the scratchpad source's `wc -l` MEASURED AT COPY TIME, and equal to it (202 when this plan was written, 213 at plan revision 1 — the source is LIVE, so assert equality with the measurement, never a literal)"
    - path: ".planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md"
      provides: "the Codex CLI v0.141.0 adversarial review referenced by §D of the file above"
      min_lines: 28
    - path: ".planning/DECISIONS.md"
      provides: "DEC-2026-09-16-ram1-launcher-measurement appended at EOF"
      contains: "DEC-2026-09-16-ram1-launcher-measurement"
    - path: ".planning/osf_deviations.md"
      provides: "a RESOLVED pointer sub-entry inside the trsx5 section so the ledger no longer ends on an open STOP"
      contains: "DEC-2026-08-17-trsx5-gate-released"
    - path: ".planning/HANDOFF.json"
      provides: "resume surface with every B1 field refreshed and history preserved"
      contains: "headline_PRIOR_2026_09_16"
    - path: ".planning/STATE.md"
      provides: "★ RESUME HERE ★ block with the B9 slips corrected in place, original wording retained"
      contains: "DEC-2026-09-16-ram1-launcher-measurement"
  key_links:
    - from: ".planning/osf_deviations.md"
      to: ".planning/DECISIONS.md :: DEC-2026-08-17-trsx5-gate-released"
      via: "the appended RESOLVED sub-entry names the DEC id and its line"
      pattern: "DEC-2026-08-17-trsx5-gate-released"
    - from: ".planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md"
      to: ".planning/DECISIONS.md :: DEC-2026-09-16-ram1-launcher-measurement"
      via: "the appended SUPERSEDED section names the DEC id and commit 9a3eb97"
      pattern: "DEC-2026-09-16-ram1-launcher-measurement"
    - from: ".planning/STATE.md"
      to: ".planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md"
      via: "a pointer bullet in the ★ RESUME HERE ★ block"
      pattern: "260916-BLAST-RADIUS-c93e97b-to-621701c"
    - from: ".planning/HANDOFF.json"
      to: ".planning/STATE.md"
      via: "resume_entry_point states that STATE's ★ RESUME HERE ★ block WINS when the two disagree"
      pattern: "STATE.md"
---

<objective>
Refresh the records that the 2026-09-16 blast-radius review found stale, and ONLY those.

Three quick tasks landed on 2026-09-16 (`kht` options draft, `ocb` RAM-1, `oyq` tcujq) and were
pushed at `621701c`. The resume surfaces still describe the world before them: `HANDOFF.json` (last
rewritten at `c93e97b`, untouched by the range) still says the agent must draft the options, still
prescribes a fix that measurement FALSIFIED, and still says docstring edits are free; `STATE.md`
carries an undated self-contradiction, basis-less line citations and two "in progress" headings; the
`.continue-here.md` block and the Stage B halt record still direct a reader to redo finished work
the wrong way; the OSF deviation ledger's trsx5 section still ends on "None of (1)-(6) has been
actioned" although Carter released that gate on 2026-08-17; and three quick SUMMARY/VERIFICATION
files carry as-of statements that are now false.

Purpose: the next session must not redo finished work, must not reinstate a falsified fix, and must
not read the pre-registration ledger as unresolved. The realistic harm of leaving this is redone
work or pressure to weaken tests.

Output: 2 banked review files, 4 insertion-only history records, 3 as-of correction notes, and 2
refreshed resume surfaces — DOCS ONLY. No code, no tests, no config, no posted amendment.

NON-GOALS (deliberately out of scope — REPORT, do not fix):
- the Seth-bound Stage C options draft (review finding B2) — `260916-vqr`/a v2 task owns it;
- the `260812-ox1` runbooks and `.claude/skills/**` (B4/B6/B7/B11/B14) — task `260916-vqr`;
- the blanket freeze prose inside `tests/m3/test_source_freeze_pins.py` / `source_freeze.py` (B10)
  — touches `tests/`, forbidden here;
- `260916-oyq-VERIFICATION.md:26`'s off-by-one line counts (deltas agree) — report only;
- the `condition_ld_matrix.py:159-160` function-docstring nuance (B10): it says "trsx5 retains the
  fully-NaN-row drop rule that this raise directs", but in PRODUCTION that retained rule is
  carried out by `--mac 1` plus the raw NaN-raise, NOT by this module. It is a code-adjacent
  docstring in a frozen file, so it cannot be fixed here: name it in the SUMMARY's OPEN list AND
  record it (cheaply, one line) in the `DEC-2026-09-16-ram1-launcher-measurement` entry's
  "Consequences recorded, not decided" section so the observation is not lost;
- the STATE.md:62-63 orchestrator-probe-vs-banked-value labelling and STATE.md:2223-2226's four
  "(prior)…(latest)" lines — not in this task's scope list; name them in the SUMMARY as open.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
- `.planning/STATE.md` — ⚠ **1,087,011 B (~294k tokens). NEVER read whole; an `@`-include exhausts
  the window before Task 1 writes a byte.** Read `sed -n '1,100p' .planning/STATE.md` (frontmatter +
  the ★ RESUME HERE ★ block = everything this task edits) and reach anything else through the
  verified-unique anchors in STEP 3 or `python3` substring scans. Same for
  `git show 621701c:.planning/STATE.md` — always pipe it through a line filter.
- `.planning/HANDOFF.json` — 90,305 B. Do NOT `@`-include: the key accounting happens inside
  `handoff_check.py`; read only the fields STEP 2 names.

READ BEFORE WRITING ANYTHING (the input, in full):
- `/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/blast/260916-BLAST-RADIUS-findings-consolidated.md`
- `/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/blast/codex-review.md`

READ AS NEEDED (all read-only):
- `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md` (first 60 lines + frontmatter)
- `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md` (:100-150)
- `.planning/osf_deviations.md` (:133-344 = the whole trsx5 section)
- `.planning/DECISIONS.md` (:2030-2100 = DEC-2026-08-17-trsx5-gate-released; :2413-EOF = the entry
  format to copy)
- `.planning/quick/260916-ocb-*/260916-ocb-{PLAN,SUMMARY,VERIFICATION}.md`
- `.planning/quick/260916-oyq-*/260916-oyq-{SUMMARY,VERIFICATION}.md`

<scratch>
All temporary scripts, copies and negative-control mutants go OUTSIDE the repo:

    export VQP=/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch
    mkdir -p "$VQP"

Never `/tmp`. Never inside the repo. Never `git add .` / `git add -A` (GPFS multi-terminal rule).
</scratch>

<measured_facts>
Every fact below was MEASURED at plan time on this node with the command shown. The executor MUST
RE-DERIVE each one it writes into a record and record the command + output in the SUMMARY. If a
re-derivation disagrees with this table, that is a FINDING — report it, do not "adjust" the record.

| # | Fact | How to re-derive |
|---|------|------------------|
| M1 | HEAD `621701c`, tracked tree clean, `origin/m3-W2-aou-deltas == HEAD` | `git log --oneline -3`; `git status --porcelain -uno`; `git rev-parse HEAD origin/m3-W2-aou-deltas` |
| M2 | Commit subjects exist for `f09535c`,`11f61e8`,`f8ff9cd`,`9a3eb97`,`0231cbf`,`b6b1f70`,`b709ce1`,`48b8828`,`621701c`,`c93e97b`(2026-09-16 session close = HANDOFF's last write),`bf16289`(2026-07-16) | `git log -1 --format='%h %ad %s' --date=short <sha>` |
| M3 | `run_native_ld_panel.py` 1344 lines at `c93e97b` -> 1487 at HEAD; numstat `156 13`. Every STATE-cited line was **RE-LOCATED PER CITATION** and each landed at **+143**; one offset fits all of them because EVERY hunk of `c93e97b..HEAD` sits at old **`:184-203`** (`@@ -184 +184 @@` … `@@ -199,4 +326,20 @@`), far above the earliest cited line (`:923`). ⚠ **Word the record as "+143 fits every citation because all hunks sit at old :184-203", NOT "the file shifted uniformly by +143".** | `git show <rev>:src/python/run_native_ld_panel.py \| wc -l`; `git diff --numstat c93e97b HEAD -- src/python/run_native_ld_panel.py`; line-by-line map (script in Task 3) |
| M4 | HEAD equivalents: `:1144-1146`->`:1287-1289`, `:1278`->`:1421`, `:923-939`->`:1066-1082`, `:961-965`->`:1104-1108`, `:1129-1139`->`:1272-1282`, `:1153`->`:1296` | the same map; each old line text is UNIQUE in the new file except `:965`/`:1139` (a bare `)`) — for those confirm by the +143 offset |
| M5 | kht DEFAULT: `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, rc 0. kht `--live`: `RESULT RED 31/318 parsed=88 table=88 verified=64`, rc 1 | `<smoke_dev python> .planning/quick/260916-kht-*/260916-kht-verify.py [--live]` |
| M6 | `git diff --numstat bf16289 HEAD` — condition_ld_matrix.py `37 0`; write_conditioned_ld_npz.py `29 0`; **plink_ld_to_npz.py, occlusion_span_filter.py and src/R/ld_npz_to_rds.R report NOTHING = still 0-diff** | `git diff --numstat bf16289 HEAD -- src/python/condition_ld_matrix.py src/python/write_conditioned_ld_npz.py src/python/plink_ld_to_npz.py src/python/occlusion_span_filter.py src/R/ld_npz_to_rds.R` |
| M7 | Notice insertion hunks: condition_ld_matrix.py `@@ -2,0 +3,31 @@` and `@@ -124,0 +156,6 @@`; write_conditioned_ld_npz.py `@@ -3,0 +4,28 @@` and `@@ -85,0 +114 @@`. **So the shift is TWO-SEGMENT: clm +31 for old 3-124 and +37 from old 125 (:153->:190, :200->:237, :130->:167); wcn +28 for old 4-85 and +29 from old 86** | `git diff -U0 48b8828^ HEAD -- <file> \| grep '^@@'` |
| M8 | The notices name the retained rules only in ONE module and never by line number: `condition_ld_matrix.py:19-21` names them BY CONTENT ("the fully-NaN-row drop rule …, the PSD regularization methods, and the raw-panel NaN-raise contract"); `write_conditioned_ld_npz.py`'s notice does NOT name them at all; the token `:35`/`:37`/`:39` appears in NEITHER file | `python3` substring scan of both files for `:35`, `:37`, `:39` and for `RETAINS` (use python, NOT grep — see the repo's grep-dialect rule) |
| M9 | `tests/m3` collects **1262** ids at HEAD in ~2.5 s = 1229 passed + 33 skipped. ⚠ The 1229/33 split was produced by quick-260916-ocb/oyq and **independently RECONCILED BY TEST ID from the executors' JUnit XMLs — NOT RE-RUN — by each task's verifier** (`260916-ocb-VERIFICATION.md:147`, `260916-oyq-VERIFICATION.md:33`). **This task does not re-run the suite and must never write "re-run by an independent verifier".** The 1262 figure is citable straight from `oyq-VERIFICATION.md:33`. | `sed -n '147p' …260916-ocb-VERIFICATION.md`; `sed -n '33p' …260916-oyq-VERIFICATION.md`; optional `<smoke_dev python> -m pytest tests/m3 --collect-only -q \| tail -1` |
| M10 | The committed Stage C command has NO `--fail-fast`: `260812-ox1-AGENT-PROMPT.md:398` | `sed -n '398p' .planning/quick/260812-ox1-*/260812-ox1-AGENT-PROMPT.md` |
| M11 | `grep -nE '08-17\|gate-released\|260817' .planning/osf_deviations.md` returns **0 hits**; the trsx5 section runs `:133`-`:343` and ends at the `---` on `:344`; the ledger is 1022 lines | `grep -c ...`; `grep -n '^## ' .planning/osf_deviations.md` |
| M12 | `DEC-2026-08-17-trsx5-gate-released` is at `.planning/DECISIONS.md:2030`; DECISIONS.md is 2538 lines; entries are appended at EOF as `## YYYY-MM-DD — DEC-…: <title>` | `grep -n 'trsx5-gate-released' .planning/DECISIONS.md`; `wc -l` |
| M13 | The posted trsx5 body in-repo: 9695 B / `c19be8b2ad7cd6a45fee1d668d8a9cf9`. The complete 9,907-B lineage IS in the object store: `git show 3684413:.planning/quick/260814-u9p-*/260814-u9p-seth-lineage-9907.txt` = 9907 B / `425d925a88ab474ec2396cbea25e665c` | `wc -c` + `md5sum` on both |
| M14 | RAM-1 falsification measurements (banked, `260916-ocb-PLAN.md:112-113`): 3.11 vfork/posix_spawn floor = the spawner's LIFETIME high-water — parent VmHWM **523060 KiB** (VmRSS 11400) and a trivial child read **523060 KiB**; 3.9 fork floor = the spawner's CURRENT RSS — parent holding 400 MiB, `/usr/bin/true` read **413992 KiB**. Launcher floor **11264 KiB (3.11) / 4352 KiB (3.9)**. NC01 (the recorded fix) observed RED at A2 **362.59** / A3 **362.92** MiB (`260916-ocb-SUMMARY.md:44`). Post-fix: 300 MiB child then tiny child reads 307.96 then **11.00** MiB (old code read 308 then 308); tiny child with the driver holding 256 MiB reads **11.25** MiB (old ~363) | `sed -n '110,118p' .planning/quick/260916-ocb-*/260916-ocb-PLAN.md`; `sed -n '40,44p' …SUMMARY.md` |
| M15 | Carter's verbatim choice: `Small launcher process (Recommended)` (`260916-ocb-PLAN.md:14`,`:97`; `SUMMARY.md:8`,`:70`) | `grep -n 'Small launcher process' .planning/quick/260916-ocb-*/*.md` |
| M16 | Docstring-stripped top-level AST diff `c93e97b` vs HEAD on `run_native_ld_panel.py`: exactly ONE changed node (`_run_plink`) + ONE added node (`_PLINK_PEAK_RSS_LAUNCHER`); the `if __name__` block differs only in its line-number key | script in Task 2 (ast.parse + strip docstrings + compare top-level nodes) |
| M17 | **No posted/pre-registered body registers a peak-RAM measurement.** 0 case-insensitive hits for `peak.?ram\|peak.?rss\|ru_maxrss\|maxrss\|\bRAM\b\|resident set` in the posted trsx5 body, the mk7ze amendment, the tcujq amendment and the trsx5 project copy. `⚠ .planning/amendments/AOU-LD-PIPELINE.md has 3 `RAM` hits (:471,:488,:492) but they are CLUSTER-SIZING prose ("~1.6 TB worker RAM", "n1-highmem-16 … RAM-bound"), not a measurement contract` | `grep -icE '…' <each file>` then read the 3 hits |
| M18 | `test_no_whole_parent_dense_materialization` (`tests/m3/test_sparse_parent_benchmark.py:54-138`) is the writer — `BENCHMARK_TSV.write_text(header + line)` at `:138`. `test_sparse_parent_benchmark_records_metrics` (`:141`) only READS it (`:145-148`) | `grep -n 'def test_\|BENCHMARK_TSV' tests/m3/test_sparse_parent_benchmark.py` |
| M19 | No committed test reads HANDOFF.json / STATE.md / osf_deviations.md / DECISIONS.md / .continue-here.md as a path — only 3 prose mentions (`tests/m3/source_freeze.py:40`, `tests/m3/test_source_freeze_pins.py:98`,`:188`) | the python scan in <verification> |
| M20 | HANDOFF.json: 59 top-level keys, no trailing newline, and `json.dumps(obj, indent=2, ensure_ascii=True).encode()` is BYTE-IDENTICAL to the file | the round-trip check in Task 3 |
| M21 | ⚠ **LIVE SOURCE — THE ONLY ROW IN THIS TABLE THAT IS NOT PINNED, AND THE ONLY ONE WHERE A MISMATCH IS *NOT* AN "anything unexpected = STOP" TRIGGER.** The orchestrator is still correcting the findings file (6+ corrections on 2026-09-16): it read **20,410 B / 202 lines / `346a6f8707a48874618e4a28e1a24b39`** when this plan was written and **25,784 B / 213 lines / `3afb70fc3551cc86ae9c6fa9794eea29`** at plan revision 1, and it **may move again before execution**. So: MEASURE `md5sum` + `wc -lc` on the source at copy time, RECORD the measured values in the SUMMARY, and assert only `cmp -s src dst` + equal md5 on both sides. `codex-review.md` read 5,256 B / 28 lines / `fce1c52d53308ebffb00031714436193` at BOTH measurements (informational, still true). | `md5sum` + `wc -lc` on the SOURCE **and** the banked copy, at copy time |
| M22 | `§B2` of the banked review lists exactly 7 numbered courier-readiness findings against the v1 Stage C draft (labelled "MEDIUM ×7") | count the `^1.`..`^7.` items under `### B2` in the banked file |
</measured_facts>

<input_errata>
The consolidated findings file is INPUT, not authority. Two of its claims were measured WRONG at
plan time. Do not propagate them:
1. **B9 cites `STATE.md:76` for the "`--live` goes RED 31/318" sentence. It is `STATE.md:78`.**
   (`:76` is the `nohup timeout 312h` SIGHUP bullet.) Use `:78`.
2. **A/B3's "No posted text … mentions peak RAM" is too broad.** It holds for every POSTED body,
   but `.planning/amendments/AOU-LD-PIPELINE.md:471/:488/:492` do say "RAM" — as cluster-sizing
   prose, not as a measurement contract. Write the narrow, true claim (M17), not the broad one.
**3. The findings file itself is LIVE.** The orchestrator has corrected it 6+ times on 2026-09-16:
20,410 B / 202 lines / `346a6f87…` when this plan was written, 25,784 B / 213 lines /
`3afb70fc3551cc86ae9c6fa9794eea29` at plan revision 1, and it may move again. **RE-READ it before
deriving any record content from it, bank whatever it reads AT COPY TIME, and record the measured
md5/size.** A digest different from M21 is EXPECTED and is NOT an "anything unexpected = STOP"
trigger — M21 is explicitly exempted from that rule.

Also note the findings file's own §D says the Codex review lives in "`codex-review.md` beside this
file"; after banking, that sibling is
`.planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md`. Record that mapping in STATE.md
(the banked files are byte-frozen, so the pointer cannot be fixed inside them).
</input_errata>

<conventions_to_follow>
- **HANDOFF.json** has TWO history conventions and this plan uses BOTH, deliberately:
  (a) for `headline`, the PRIOR-KEY convention — copy the PRE value verbatim into a NEW key
      `headline_PRIOR_2026_09_16` placed immediately BEFORE `headline`, then write the new
      `headline` (the file already carries `headline_PRIOR_2026_09_01/_09_08/_09_09/_09_10`);
  (b) for every other field, the IN-PLACE DATED ANNOTATION convention — keep the PRE text verbatim
      and append `⚠ CORRECTED 2026-09-16 — …` / `✅ DONE 2026-09-16 — …` (as
      `gates.m3_04b`, `gates.m3_04c`, `gates.trsx5_posted_body` and `repo_fixes_status[0]` do).
  `suite_baselines["tests/m3"]` uses its own documented form: new measurement FIRST, then
  `--- PRIOR ENTRY, RETAINED …` before the existing text.
  **State in the SUMMARY which convention you followed for each field and why.**
- **osf_deviations.md / DECISIONS.md / the halt record / .continue-here.md**: INSERTION ONLY.
  Never edit, soften, reword or delete an existing line. Every one of these files already says so
  about itself ("Appended, never rewritten: every pre-existing line of this section survives
  unchanged").
- **.continue-here.md** prepends the newest block directly under the frontmatter. There is already
  a `2026-09-16 (★ LATEST ★ …)` block: do NOT re-label it. The new block's own header must say it
  supersedes the block below, which is retained verbatim.
- **STATE.md** edits are in-place corrections that KEEP the original wording (`(kept as written)`,
  `Body preserved verbatim`, strikethrough + a dated bullet — all already used in this file).
- Commits: `docs(quick-260916-vqp): …`, explicit paths only, ending with
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
</conventions_to_follow>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight + bank the review record + three as-of correction notes</name>
  <files>
.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md (CREATE)
.planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md (CREATE)
.planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-SUMMARY.md (APPEND)
.planning/quick/260916-ocb-ram-1-per-child-peak-rss-for-run-plink-v/260916-ocb-VERIFICATION.md (APPEND)
.planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-SUMMARY.md (APPEND)
$VQP/insert_only.py (scratch, not committed)
  </files>
  <action>
**STEP 0 — PRE-FLIGHT GUARD. Anything unexpected = STOP and report; do not "work around" it.**
```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
export VQP=/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch && mkdir -p "$VQP"
export PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
git log --oneline -3                       # MUST be 621701c / 48b8828 / b709ce1
git status --porcelain -uno                # MUST be empty (untracked files are expected and ignored)
git rev-parse HEAD origin/m3-W2-aou-deltas # MUST be the same sha twice
K=$(ls -d .planning/quick/260916-kht-*/260916-kht-verify.py)   # resolve the glob ONCE
# ⚠ `$PY … | tail -1` takes TAIL's rc and asserts nothing. Assert the STRING:
OUT=$($PY "$K" | tail -1); echo "$OUT"
[ "$OUT" = "RESULT GREEN checks=317 parsed=88 table=88 verified=88" ] \
  || { echo "KHT DEFAULT NOT GREEN — STOP"; exit 1; }
```
If any GPFS `invalid object` / `Error building trees` appears at ANY point in this task: STOP,
report, and follow memory `reference_gpfs_git_object_store_loss` — do not improvise.

**STEP 1 — write the insertion-only prover** at `$VQP/insert_only.py`. It takes
`<repo-relative path> <git ref> [file-to-test]`, reads PRE via `git show <ref>:<path>` in BINARY,
reads the file to test in BINARY, and proves `post == pre[:k] + INSERT + pre[k:]` for the single
greedy common-prefix `k`: fail if `len(post) <= len(pre)`; compute `k` as the longest common
prefix; let `tail = len(pre)-k`; fail if `tail and post[len(post)-tail:] != pre[k:]`. Print a
one-line verdict and **`sys.exit(0)` on success, `sys.exit(1)` on any failure** — never print a
bare True/False and never exit 0 on failure.

⚠ **KNOWN GAP — and why the numstat check is LOAD-BEARING, not belt-and-braces.** The plan-checker
prototyped this exact spec and found ONE false pass: *reword the LAST pre-existing line, then
append* -> rc 0, because the greedy prefix stops at the reworded line and the entire remainder is
attributed to the "insertion". Close it BOTH ways and treat neither as optional:
1. add a THIRD assertion to the prover — the last NON-EMPTY line of PRE must appear as a **WHOLE
   LINE** of POST: `last_nonempty(pre) in post.split(b"\n")`, **NOT a substring test** (a substring
   test PASSES on "<that line> REWORDED" and reopens the very gap this assertion closes — measured
   by the plan-checker) (exit 1 if not);
2. keep `git diff --numstat 621701c HEAD -- <file>` with a **deletions column of 0** as a REQUIRED
   companion for every file, and say in the SUMMARY that it is the check that actually catches
   this class. ⚠ Note the `awk '$2!=0{…}'` guard **passes on an EMPTY numstat** (a file that was
   never changed at all), so it is only meaningful together with the prover's
   `len(post) <= len(pre) -> exit 1` rule — which must therefore run on EVERY file, not only the
   ones you expect to have grown.

**STEP 2 — bank the review, byte-identical.** Copy (`cp`, do NOT retype, do NOT add a header):
- `<blast>/260916-BLAST-RADIUS-findings-consolidated.md` -> `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`
- `<blast>/codex-review.md` -> `.planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md`
where `<blast>` is the scratchpad dir named in `<context>`. ⚠ **RE-READ the findings source first**
(it is LIVE — see M21) so the banked bytes and any record content derived from it are the same
generation. Then prove byte identity BOTH ways: `md5sum` the SOURCE and the DESTINATION at copy
time and require them EQUAL to each other, and `cmp -s src dst` must exit 0 for both.
**Do NOT compare against the digests in M21** — the findings file has been corrected 6+ times today
(20,410 B / 202 lines / `346a6f87…` when this plan was written; 25,784 B / 213 lines / `3afb70fc…`
at revision 1). Whatever it reads at copy time IS the value: measure it, record md5 + `wc -lc` for
both files on both sides in the SUMMARY, and bank that. **A digest different from M21 is EXPECTED
and is not a STOP.**

**STEP 3 — append the three as-of correction notes.** Each is a short block APPENDED at EOF of an
existing file, under a heading of the form
`## ⚠ AS-OF CORRECTION 2026-09-16 (appended by quick-260916-vqp; nothing above is edited)`.
Do not rewrite the bodies. Content, all re-derived first:

(a) `260916-ocb-SUMMARY.md` — two corrections:
  - `:47`-`:48` ("Two commits …, not pushed." / "PLAN, this SUMMARY and STATE.md are NOT committed.")
    are now FALSE: the close-out landed at `0231cbf` and the branch is PUSHED —
    `git rev-parse HEAD origin/m3-W2-aou-deltas` both `621701c…` (re-derive and quote the full sha).
  - `:392` names the WRONG benchmark writer. Per M18 the unconditional writer is
    `test_no_whole_parent_dense_materialization` (`tests/m3/test_sparse_parent_benchmark.py:54-138`,
    `BENCHMARK_TSV.write_text(header + line)` at `:138`);
    `test_sparse_parent_benchmark_records_metrics` (`:141`) only READS it at `:145-148`.
    The recorded remedy (`git checkout -- tests/m3/sparse_parent_benchmark.tsv` after a full run)
    is UNCHANGED and still correct.
(b) `260916-ocb-VERIFICATION.md` — `:135` "not pushed (ahead 4)" is now false: pushed, origin ==
    HEAD == `621701c`.
(c) `260916-oyq-SUMMARY.md` — `:37` "Not pushed." is now false: `621701c` pushed, origin == HEAD.
    (Also state, WITHOUT fixing it, that `260916-oyq-VERIFICATION.md:26`'s two line counts are off
    by one — `213->250` / `112->141` where `wc -l` gives `212->249` / `111->140`; the deltas
    `+37`/`+29` are correct and agree with `git diff --numstat`. Re-derive both before writing.)

**STEP 4 — prove and commit.** For each of the three appended files run
`$PY $VQP/insert_only.py <path> 621701c` and require rc 0; then run the NEGATIVE CONTROL: `cp` the
file to `$VQP`, mutate ONE pre-existing byte inside it (e.g. change a character on line 5), re-run
the prover against the copy and require **rc exactly 1** (`test $rc -eq 1 || exit 1`). Then:
```bash
git diff --numstat 621701c HEAD -- <the 3 appended paths>   # deletions column MUST be 0 for each
git add <the 5 explicit paths>                              # NEVER git add . / -A
git commit -m "docs(quick-260916-vqp): bank the 2026-09-16 blast-radius review (byte-identical, as-received) + as-of corrections in the ocb/oyq quick records (pushed at 621701c; ocb-SUMMARY:392 named the wrong benchmark writer)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && S=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/blast && cmp -s "$S/260916-BLAST-RADIUS-findings-consolidated.md" .planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md && cmp -s "$S/codex-review.md" .planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md && md5sum .planning/debug/260916-BLAST-RADIUS-*.md && for f in .planning/quick/260916-ocb-*/260916-ocb-SUMMARY.md .planning/quick/260916-ocb-*/260916-ocb-VERIFICATION.md .planning/quick/260916-oyq-*/260916-oyq-SUMMARY.md; do /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch/insert_only.py "$f" 621701c || exit 1; done && git diff --numstat 621701c HEAD -- .planning/quick/260916-ocb-*/260916-ocb-SUMMARY.md .planning/quick/260916-ocb-*/260916-ocb-VERIFICATION.md .planning/quick/260916-oyq-*/260916-oyq-SUMMARY.md | awk '$2!=0{print "DELETIONS FOUND: "$0; exit 1}' && echo "TASK1 OK"</automated>
  </verify>
  <done>Both banked files are byte-identical to their sources: `cmp -s` exit 0 and the md5 measured on the SOURCE at copy time equals the md5 measured on the BANKED COPY, for both files, with both measured values recorded in the SUMMARY (the findings source is LIVE, so no literal digest is asserted; `codex-review.md` is expected to read `fce1c52d…`). The three quick records each gained exactly one appended correction block, proven insertion-only with an observed rc==1 negative control and 0 deletions in numstat. One commit, explicit paths, Co-Authored-By trailer present.</done>
</task>

<task type="auto">
  <name>Task 2: The four history records — .continue-here prepend, halt-record append, trsx5 ledger pointer, RAM-1 DEC</name>
  <files>
.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md
.planning/osf_deviations.md
.planning/DECISIONS.md
  </files>
  <action>
All four changes are INSERTION ONLY. Re-derive M2, M6, M7, M10, M11, M12, M13, M14, M15, M16, M17
BEFORE writing; put the commands and their outputs in the SUMMARY.

**(A) `.continue-here.md` — PREPEND one dated block** immediately after the frontmatter `---` and
its blank line (i.e. above the existing `> **2026-09-16 (★ LATEST ★ …)**` block, which is NOT
re-labelled and NOT touched). Use the file's `>` block-quote style.
⚠ **The header must be UNAMBIGUOUS against that older SAME-DAY block, which still calls itself
`★ LATEST ★`.** A bare `2026-09-16` header would leave two same-day blocks and no way to order
them. Use this shape:
`> **2026-09-16 (LATER — ★★ THIS IS THE CURRENT BLOCK ★★; it SUPERSEDES the 2026-09-16 block below
that is still labelled "★ LATEST ★", retained verbatim and unedited): …**`
Content:
- ⭐ **Stage C NaN posture — still the blocker, but the options draft is BANKED and NOT SENT**:
  `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` (`quick-260916-kht`,
  `f09535c`), brief-blind, 88 citations verified. What remains is Carter's: judge the two residual
  framing cues, courier it, decide after Seth. ⚠ The 2026-09-16 blast-radius review lists **7**
  MEDIUM courier-readiness findings against the v1 draft (`§B2` of
  `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md` — re-derive the count, M22): courier a
  v2, or courier v1 with the basis caveat. Either way the draft's citations are read at `c93e97b`.
- ✅ **RAM-1 DONE 2026-09-16 via a LAUNCHER**, not the recorded fix: `f8ff9cd` (RED) + `9a3eb97`
  (fix) + `0231cbf` (close-out), verified 9/9. ⛔ The recorded `Popen` + `os.wait4` fix is
  **FALSIFIED by measurement and must not be reinstated** (see `DEC-2026-09-16-ram1-launcher-measurement`
  and the ⚠ SUPERSEDED section appended to the halt record).
- ✅ **tcujq DONE 2026-09-16**: `b6b1f70` + `b709ce1` + `48b8828` + `621701c`, verified 11/11.
  Items (2) and (3) of the block below are therefore CLOSED.
- ⚠ **The committed Stage C command has NO `--fail-fast`** (`260812-ox1-AGENT-PROMPT.md:398`,
  re-derive). The block below's "`--fail-fast` halts" describes a command form that is not the
  committed one: a raising region records `error:` and the loop CONTINUES
  (`run_native_ld_panel.py:1287-1289`, `:1421` at `621701c`; `:1144-1146`, `:1278` at `c93e97b`).
- ⚠ **This file's frontmatter `status: SWEEP_RUNNING_pid913…` is HISTORICAL** — stale since
  2026-08-26; nothing is running; the frontmatter is deliberately left unedited as the record of
  what it said. An agent never fires, starts, stops or deletes anything.

**(B) Halt record — APPEND at EOF** a section
`## ⚠ SUPERSEDED 2026-09-16 — RAM-1's DIAGNOSIS held; its PRESCRIBED FIX is falsified`.
State first that nothing above is edited. Then, each item naming the line it supersedes:
- **`:118-122`** — "region 17 -> 2.9689 (real, first child) … Region 1's 30.6591 is real because
  Stage A was its own process" is SUPERSEDED. A first child is not clean either: at exec Linux
  folds the SPAWNER's memory into the child's `ru_maxrss` (M14 — 3.11 vfork floor = the spawner's
  lifetime high-water, 523,060 KiB read by a trivial child; 3.9 fork floor = the spawner's current
  RSS, 413,992 KiB with 400 MiB held; and the unmodified `_run_plink`'s FIRST tiny child read
  106.8 MiB, the importer's own numpy/pandas footprint). **Consequence: no pre-fix `peak_ram_gib`
  value is a proven plink-only measurement — region 17's 2.9689 and region 1's 30.6591 included.**
  The DEFECT this record diagnosed (a monotone `RUSAGE_CHILDREN` high-water) is CONFIRMED and
  unchanged; only the "real" labels and the remedy are wrong.
- **`:124`** — "Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's
  own" is **FALSIFIED**. It was implemented as negative control NC01 and observed RED (A2 362.59 /
  A3 362.92 MiB, `260916-ocb-SUMMARY.md:44`). **Do not reinstate it** — `tests/m3/test_run_plink_peak_rss.py`
  goes RED if anyone does. What landed instead (Carter, 2026-09-16, verbatim "Small launcher process
  (Recommended)"): `_run_plink` reads plink's own `rusage` inside a small isolated `-I -S` launcher,
  bias ~11 MiB (3.11) / ~4 MiB (3.9). Commit `9a3eb97`; decision record
  `DEC-2026-09-16-ram1-launcher-measurement`.
- **`:146`** — "Separately and independently: RAM-1 fix (TDD) and the 00071 anchor": RAM-1 is DONE
  (`9a3eb97`); **COST-1 / `m2_region_00071` is still open** and still needs a Carter fire.
- A closing line: this record is CITED by the banked Stage C options draft, so a courier of that
  draft should carry this annotation with it.

**(C) `.planning/osf_deviations.md` — INSERT one sub-entry INSIDE the trsx5 section**, after the
last line of the `### RECHARACTERIZED 2026-08-14 …` sub-entry and BEFORE the `---` that closes the
section (M11: the section is `:133`-`:343`, the `---` is `:344`). Re-derive those line numbers
before inserting — insert by locating the `---` that precedes the
`### REQ-AOU-LD-VALIDATION Check 2 …` heading, never by a hard-coded offset.
⚠ This file is the pre-registration ledger: **do not rewrite one existing line.**
Heading: `### RESOLVED 2026-08-17 — the trsx5 body question is settled; pointer recorded here 2026-09-16`.
Content:
- **Why this pointer exists (and why it is only a pointer).** This section previously ended on
  "None of (1)-(6) has been actioned" (`:326` at `621701c` — re-derive), and a search of THIS FILE
  for `08-17` / `gate-released` / `260817` returns ZERO hits (re-measured 2026-09-16), so a reader
  of the ledger alone could not learn the outcome. Nothing above is re-adjudicated, edited or
  softened; the 2026-08-13 / 2026-08-14 readings stay as the honest state of knowledge at their
  dates.
- **The resolution.** The posted **9,695-B** body is a **byte-exact plain-text rendering of the
  COMPLETE 9,907-B lineage** — not a truncation and not a third body. Seth published the 6-step
  transform first; we replicated it firsthand from the git object store at `3684413` (source
  **9,907 B / `425d925a88ab474ec2396cbea25e665c`** — re-derive with
  `git show 3684413:.planning/quick/260814-u9p-*/260814-u9p-seth-lineage-9907.txt | wc -c` and
  `| md5sum`), implemented from his prose spec alone, run once, no fitting; output 9,695 B /
  `c19be8b2ad7cd6a45fee1d668d8a9cf9`, which is also Carter's own firsthand 2026-08-16 OSF download
  measurement. The in-repo copy of the posted body is
  `.planning/quick/260817-vbu-*/260817-vbu-trsx5-posted-9695-reconstructed.txt`
  (**re-measure its size and md5 and quote the measured values**).
- **Consequence for the pre-registration record.** All three bodies carry the same pre-registration
  prose; the 212-B and 149-B deltas are pure markup; the public record is substantively correct and
  complete. The "unexplained third body" characterization is RETIRED — by the person who coined it
  and by our own replication — while the heading above that coined it stays as written.
- **The gate.** RELEASED BY CARTER ON SUBSTANCE, 2026-08-17 22:32 EDT:
  `DEC-2026-08-17-trsx5-gate-released` in `.planning/DECISIONS.md` (`:2030` — re-derive). Re-post
  NOT taken: optional legibility only, per Seth's withdrawn "re-post required". The recommendation
  lists' "(1)-(6) not actioned" was TRUE when written and is superseded by a resolution that
  reached the same question by a different route — characterize the posted body rather than
  re-post it.
- **Provenance.** Appended by `quick-260916-vqp` on 2026-09-16 after the blast-radius review
  (finding B8); banked at `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`. No OSF
  contact, no Seth contact, no agent posted anything, `$0`. Appended, never rewritten: every
  pre-existing line of this section survives unchanged.

**(D) `.planning/DECISIONS.md` — APPEND at EOF** an entry in the house format (copy the shape of
the last entry, `:2413`ff):
`## 2026-09-16 — DEC-2026-09-16-ram1-launcher-measurement: RAM-1's recorded Popen+os.wait4 fix is falsified by measurement; _run_plink measures plink's own peak RSS in an isolated launcher`
- **Decision (CARTER, 2026-09-16, AskUserQuestion):** quote the chosen option label **verbatim** —
  `Small launcher process (Recommended)` (M15; cite `260916-ocb-PLAN.md:14`/`:97`).
- **The falsified premise, with its measurements.** `.planning/debug/260824-STAGE-B-HALT-…md:124`
  prescribed `subprocess.Popen` + `os.wait4(pid, 0)` "whose `rusage` is that child's own". That is
  false in this environment — write the M14 numbers with their source lines, and the reason: the
  driver holds the cohort `.bim` at spawn (`_window_bim_n_var` reads 20,767,864 lines) and converts
  `.ld.bin` in-process afterwards, so the column would flat-line again. Record the negative control:
  NC01 implemented the recorded fix and was observed RED (A2 362.59 / A3 362.92 MiB). Record the
  naive-probe trap: a `MAP_SHARED` probe does NOT show the 3.9 effect (fork does not copy shared
  page tables), so a naive probe "refutes" a true premise.
- **What changes.** `_run_plink` starts an isolated `-I -S` Python launcher which forks plink from
  its own small image, `os.wait4`s it and returns plink's `ru_maxrss` over a pipe; bias 11,264 KiB
  (3.11) / 4,352 KiB (3.9). `subprocess.run(check=True)` contract, fd and signal-disposition parity,
  SIGTERM/`timeout` behaviour preserved and pinned. Commits `f8ff9cd` (RED, 25 items, 9 red on the
  pre-fix driver) and `9a3eb97` (fix), close-out `0231cbf`, verified 9/9 by an independent verifier.
- **What does NOT change.** Re-derive M16 and M17 and write them:
  - No pre-registered behaviour moved. Docstring-stripped top-level AST diff `c93e97b` vs HEAD on
    `run_native_ld_panel.py` = exactly one changed node (`_run_plink`) + one added node
    (`_PLINK_PEAK_RSS_LAUNCHER`).
  - **No deviation-log entry is required.** No posted or pre-registered body registers a peak-RAM
    measurement or its column (0 hits across the posted trsx5 body, mk7ze, tcujq and the trsx5
    project copy). State the ONE nuance honestly: `.planning/amendments/AOU-LD-PIPELINE.md`
    :471/:488/:492 mention "RAM" as **cluster-sizing prose** (worker RAM, `n1-highmem-16`), which is
    not a measurement contract. `.planning/osf_deviations.md` is therefore NOT amended by this
    decision.
  - `fire_verifier.check_peak_ram` is an UNCHANGED consumer; it now receives plink-only values.
- **Consequences recorded, not decided (for Carter).** `condition_ld_matrix.py:159-160` says trsx5
  "retains the fully-NaN-row drop rule that this raise directs", but in PRODUCTION that rule is
  carried out by `--mac 1` + the raw NaN-raise, NOT by this module (frozen file; B10, report-only).
  COST-1 must use post-fix `peak_ram_gib`
  only — no pre-fix value (region 17's 2.9689, region 1's 30.6591, sub14/00057's 26.5745) is a
  proven plink-only measurement. Record `python3 -V` on the AoU VM before Stage C (the launcher
  binds `os.waitstatus_to_exitcode`, 3.9+). `pgrep -f` / `pkill -f plink1.9` now also match the
  launcher; `pgrep -x plink1.9` matches only plink.
- **Cross-refs:** `.planning/debug/260824-STAGE-B-HALT-…md` (its ⚠ SUPERSEDED 2026-09-16 section);
  `quick-260916-ocb` PLAN/SUMMARY/VERIFICATION; `DEC-2026-09-16-condition-ld-matrix-freeze-code-only`
  (its sibling from the same day); `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`;
  `[[feedback_error_message_named_cause_is_not_the_measurement]]`;
  `[[feedback_green_assertion_needs_a_negative_control]]`.

**(E) Prove and commit.** For each of the four files: `$PY $VQP/insert_only.py <path> 621701c`
(rc 0 required) plus the mutated-copy negative control requiring **rc exactly 1**, plus
`git diff --numstat 621701c HEAD -- <path>` with a deletions column of 0. Then `git add` the four
explicit paths and commit:
`docs(quick-260916-vqp): insertion-only history records — .continue-here 2026-09-16 block, halt-record ⚠ SUPERSEDED (Popen+os.wait4 falsified), trsx5 ledger pointer to DEC-2026-08-17-trsx5-gate-released, DEC-2026-09-16-ram1-launcher-measurement`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && P=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python && for f in .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md .planning/osf_deviations.md .planning/DECISIONS.md; do $P /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch/insert_only.py "$f" 621701c || exit 1; done && git diff --numstat 621701c HEAD -- .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md .planning/osf_deviations.md .planning/DECISIONS.md | awk '$2!=0{print "DELETIONS FOUND: "$0; exit 1}' && grep -c 'DEC-2026-08-17-trsx5-gate-released' .planning/osf_deviations.md && grep -c 'DEC-2026-09-16-ram1-launcher-measurement' .planning/DECISIONS.md && $P -c "
import subprocess,sys
pre=subprocess.run(['git','show','621701c:.planning/osf_deviations.md'],capture_output=True,text=True).stdout.split(chr(10))
post=open('.planning/osf_deviations.md').read()
bad=[i+1 for i,l in enumerate(pre) if l.strip() and l not in post]
print('PRE lines no longer present verbatim:',bad); sys.exit(1 if bad else 0)" && echo "TASK2 OK"</automated>
  </verify>
  <done>All four records changed by insertion only (prover rc 0, negative control rc exactly 1, 0 deletions in numstat, every PRE line of osf_deviations.md still present verbatim). The ledger now points at `DEC-2026-08-17-trsx5-gate-released`; DECISIONS.md carries `DEC-2026-09-16-ram1-launcher-measurement` with re-derived measurements and the narrow, true "no deviation-log entry" claim. One commit, explicit paths.</done>
</task>

<task type="auto">
  <name>Task 3: Refresh the two resume surfaces — HANDOFF.json and STATE.md</name>
  <files>
.planning/HANDOFF.json
.planning/STATE.md
$VQP/handoff_check.py, $VQP/state_check.py, $VQP/linemap.py (scratch)
  </files>
  <action>
⚠ **STATE.md is edited and COMMITTED BY THIS EXECUTOR** (it is inside this task's scope). The
orchestrator will afterwards commit only PLAN / SUMMARY / VERIFICATION. Do NOT add a row to
STATE.md's quick-task ledger table for `260916-vqp` — that row needs the close-out sha and the
verifier result, and it belongs to the orchestrator's close-out.

**STEP 1 — build the line map** (`$VQP/linemap.py`). *(You MAY build and run this during Task 2
instead — Task 2's `.continue-here.md` block already needs the HEAD-vs-`c93e97b` citations — and
then re-use its recorded output here. Either order is fine; record which you chose.)* For
`src/python/run_native_ld_panel.py`,
`git show c93e97b:` vs `git show HEAD:`, and for each old line of interest
(923, 939, 961, 965, 1129, 1139, 1144, 1145, 1146, 1153, 1278) print the new line number. Expect a
**+143 for every one** (M3/M4) — and say WHY in the SUMMARY: all `c93e97b..HEAD` hunks sit at old
`:184-203`, above every cited line, so a single offset fits all. This is RE-LOCATION PER CITATION,
not a claim that the whole file shifted. Two old lines (`:965`, `:1139`) are a bare `)` and are not unique — take
their new numbers from the +143 offset and SAY SO in the SUMMARY. Do not write a citation you have
not mapped.

**STEP 2 — `.planning/HANDOFF.json`.** Edit it with Python: `json.load` -> mutate -> write
`json.dumps(obj, indent=2, ensure_ascii=True)` with **NO trailing newline**. Prove first (M20) that
this exact call reproduces the PRE file byte-for-byte; if it does not, STOP — the writer is not
faithful and any diff would be unreadable. Rebuild the dict preserving key order, inserting
`headline_PRIOR_2026_09_16` immediately before `headline`.

The eight changes (plus `timestamp` and one new `timestamp_reason_*` key):

1. `headline_PRIOR_2026_09_16` = the PRE `headline` value, **verbatim, unaltered** (new key).
2. `headline` (new text): resume at Stage C's NaN error posture, **and the options draft is already
   BANKED (`f09535c`) and NOT sent**; steps 1-2 done, step 3 undecided. ⚠ CORRECTED 2026-09-16: the
   committed Stage C command has **no** `--fail-fast` (`260812-ox1-AGENT-PROMPT.md:398`), so a
   raising region records `error:` and the loop CONTINUES (`run_native_ld_panel.py:1287-1289`,
   `:1421` at `621701c`; `:1144-1146`, `:1278` at `c93e97b`) — the PRE headline's "a 276-region run
   under `--fail-fast` will halt" describes a command form that is not the committed one, and is
   preserved verbatim in `headline_PRIOR_2026_09_16`. RAM-1 and tcujq are **DONE** (`f8ff9cd`/
   `9a3eb97`/`0231cbf`; `b6b1f70`/`b709ce1`/`48b8828`/`621701c`). Nothing is running; only app
   `20260626b`, STOPPED.
3. `resume_on_reconnect[1]` — KEEP the text, APPEND `⚠ UPDATED 2026-09-16 —` : the draft IS banked
   (`f09535c`, brief-blind, 88 citations, NOT sent, NOT decided); "Agent DRAFTS the options" is
   DONE and retained as written; what remains is Carter's (two framing judgements -> courier ->
   decide after Seth); the courier must cite the code at `c93e97b` **or** re-base first, because
   the 24 driver citations sit **+143** lines later at HEAD; and the banked review's `§B2` lists 7
   MEDIUM courier-readiness findings against v1.
4. `resume_on_reconnect[2]` — KEEP the text, APPEND `✅ DONE 2026-09-16 …` + `⛔ THE RECORDED FIX
   IS FALSIFIED AND MUST NOT BE REINSTATED`, with the M14 numbers, Carter's verbatim choice, the
   launcher bias, NC01's RED, and a pointer to `DEC-2026-09-16-ram1-launcher-measurement`. Carry the
   three Carter follow-ups (VM `python3 -V` >= 3.9; COST-1 post-fix values only; `pgrep -f` now
   matches the launcher).
5. `resume_on_reconnect[3]` — KEEP the text, APPEND `✅ DONE 2026-09-16 …` + `⚠ THE PREMISE ABOVE
   IS WRONG AND IS RETAINED AS WRITTEN`: "docstring edits are FREE and cannot trip the freeze" was
   false — `condition_ld_matrix.py` was ALSO whole-file numstat-pinned, so a committed docstring
   edit went RED. Now CODE-only for `condition_ld_matrix.py` ONLY
   (`DEC-2026-09-16-condition-ld-matrix-freeze-code-only`); `plink_ld_to_npz.py` and
   `occlusion_span_filter.py` KEEP the whole-file pin, so docstrings are NOT free for them (M6).
   Add the two-segment line shift from M7.
6. `carter_decisions_outstanding[0]` — KEEP the text, APPEND `⚠ UPDATED 2026-09-16`: the agent HAS
   drafted the options; outstanding = judge the two framing cues, courier brief-blind with the
   basis caveat, decide after Seth; the banked review's `§B2` argues for a v2 first.
7. `repo_fixes_status[2]` — KEEP the text, APPEND `✅ DISCHARGED 2026-09-16`: both files carry
   additive WITHDRAWN-by-trsx5 notices, `condition_ld_matrix.py`'s pin is rescoped to CODE-only, and
   the named enforcer `tests/m3/test_tcujq_withdrawal_notices.py` was committed RED (3F/14P) before
   it went green (`b6b1f70`/`b709ce1`/`48b8828`). Nothing is outstanding in this list any more.
8. `suite_baselines["tests/m3"]` — new measurement FIRST, then
   `--- PRIOR ENTRY, RETAINED …` + the PRE text verbatim. ⛔ **DO NOT write "each re-run by an
   independent verifier" — that is FALSE and this is HANDOFF's most-read numeric field.** Neither
   verifier re-ran the suite; both tasks' constraints forbade a full run. Write this instead:
   `1229 passed / 33 skipped / 0 failed` (1262 ids collected) at `621701c`, arrived at as
   1187 -> 1212 (quick-260916-ocb, +25 by test id) -> 1229 (quick-260916-oyq, +17 by test id), and
   **independently RECONCILED BY TEST ID from the executors' JUnit XMLs by a separate verifier in
   each task — NOT re-run by either verifier.** Cite both lines:
   `260916-ocb-VERIFICATION.md:147` ("the full-suite reconciliation was **checked from the
   executor's artefacts, not re-run** (the constraint forbids a full `tests/m3` run). I parsed
   `…/m3-{before,after}.xml` myself by node id") and `260916-oyq-VERIFICATION.md:33` ("I parsed the
   executor's JUnit files myself … POST `suite_post.xml`: 1262 ids = **1229 passed / 33 skipped**
   … **ADDED 17**, REMOVED 0, CHANGED 0"). **quick-260916-vqp did not re-run it either
   (docs-only)**: cite the 1262 figure from `oyq-VERIFICATION.md:33`, optionally corroborated by
   `pytest tests/m3 --collect-only -q` = 1262 (the planner measured that in 2.46 s). Keep the
   "skips must STAY at 33" rule intact.
9. `freeze_state` — KEEP the text, APPEND `⚠ CORRECTED 2026-09-16`: "Comments, docstrings … are now
   DELIBERATELY FREE" holds for `run_susie_rss.R`'s code pin but was FALSE for the three files named
   in the next sentence (all three were also whole-file numstat-pinned vs `bf16289`). Fixed for
   `condition_ld_matrix.py` only since `b6b1f70` (measured `37 0` vs `bf16289` at `621701c`, pin
   GREEN); `plink_ld_to_npz.py` and `occlusion_span_filter.py` keep the byte pin BY DECISION.
10. `resume_entry_point` — KEEP the text, APPEND `⚠ CORRECTED 2026-09-16`: items 2-3 are DONE and
    are no longer "agent-doable immediately"; **and, where this file and the `★ RESUME HERE ★`
    block at the top of `.planning/STATE.md` disagree, STATE.md WINS** (it is refreshed every
    session close; this file was last rewritten at `c93e97b`).
11. `timestamp` -> the executor's measured `date -u +%Y-%m-%dT%H:%M:%SZ`; add ONE new key
    `timestamp_reason_2026_09_16_blast_radius` recording that `quick-260916-vqp` refreshed the B1
    fields after the blast-radius review and naming the banked record.

**STEP 3 — `.planning/STATE.md`.** In-place corrections that KEEP the original wording. Locate each
line by its text, never by a hard-coded number — and ⚠ **use BACKTICK-FREE ANCHORS.** Two obvious
literals do NOT exist byte-exactly, because the file wraps names in backticks: there is no
`In progress as quick-260916-oyq` and no `GREEN in default, --source` in the file. Verified-unique
anchors (n = 1 each, measured 2026-09-16): `In progress as ` -> `:88`,
`executing after this close-out` -> `:88`, `GREEN in default` -> `:39`. **Assert the match count is
exactly 1 for every anchor before editing with it.** Then apply:
- **frontmatter `last_updated` (`:7`)** -> current UTC in the existing `"…T…:…:00.000Z"` shape.
  This is the ONLY value in the whole file that is replaced rather than extended.
- **frontmatter `last_activity` (`:17`)** -> PREPEND a new `2026-09-16 (LATEST) — quick-260916-vqp:
  …` segment followed by ` PRIOR: ` and then the existing content **verbatim**, on ONE line.
  ⛔ Do not introduce a single `"` character into the new text (the scalar already fails
  `yaml.safe_load` because of embedded quotes — HANDOFF `prep_landmines[0]`; do not make it worse).
  Use backticks and single quotes only.
- **after frontmatter comment `:15`** (`Frozen contracts byte-unchanged (… condition_ld_matrix.py
  all git-diff EMPTY)`) — INSERT **exactly ONE physical line**: a single long `#` comment, NOT
  wrapped. This is load-bearing: both the frontmatter-fence check and the touched/allowed-deletion
  line sets in V3 assume the insertion is ONE line. Consequences, both EXPECTED and both
  deliberately NOT pinned in V3: the closing `---` moves `:24` -> `:25`, and `last_activity` moves
  `:17` -> `:18`. Content (ONE line; re-derive M6 first):
  `# ⚠ SUPERSEDED 2026-09-16: condition_ld_matrix.py is NO LONGER git-diff EMPTY vs bf16289 — measured 37 0 at 621701c (48b8828, docstring-only, additive, CODE-INERT); its freeze is now CODE-only per DEC-2026-09-16-condition-ld-matrix-freeze-code-only. plink_ld_to_npz.py and src/R/ld_npz_to_rds.R ARE still 0-diff vs bf16289 (measured 2026-09-16). Line 15 is kept as written.`
- **`:26`** — keep the sentence; append: `⚠ CORRECTED 2026-09-16 — HANDOFF.json was last rewritten
  at c93e97b and its stale fields were refreshed by quick-260916-vqp. **Where this note, HANDOFF.json
  and the ★ RESUME HERE ★ block below disagree, the ★ RESUME HERE ★ block WINS** — it is refreshed
  at every session close.`
- **`:39`** — locate by the backtick-free anchor `GREEN in default` (n = 1); keep the existing
  clause (`GREEN in default, \`--source\` and \`--live\` modes`) BYTE-INTACT; append the date + scope:
  measured at `f09535c` against basis `c93e97b`; at HEAD `621701c` `--live` is RED
  `RESULT RED 31/318 parsed=88 table=88 verified=64` (re-measured 2026-09-16) purely because of the
  `+143` driver-line shift from `9a3eb97`, while default stays
  `RESULT GREEN checks=317 parsed=88 table=88 verified=88`. **`--live` is EXPECTED RED and is NOT to
  be "fixed", and the draft's BASIS `c93e97b` must NEVER be re-pinned to a moving HEAD.**
- **`:40`, `:48`, `:49`** — give every code citation its basis and its HEAD equivalent, e.g.
  `run_native_ld_panel.py:1144-1146 (at c93e97b; :1287-1289 at HEAD 621701c)`, and likewise
  `:1278 -> :1421`, `:923-939 -> :1066-1082`, `:961-965 -> :1104-1108`, `:1129-1139 -> :1272-1282`,
  `:1153 -> :1296` (each RE-LOCATED per citation, each landing at +143 — M3/M4, re-derive with
  `$VQP/linemap.py`; do NOT word it as "the file shifted uniformly by +143").
- **`:55`** (item 1 step 2, "Courier the banked file to Seth, brief-blind.") — append the courier
  caveat that currently lives only under item 2 at `:78`: courier with "read the code at commit
  `c93e97b`" or re-base the 24 driver citations first (Carter's call), and note that the banked
  review's `§B2` lists 7 MEDIUM courier-readiness findings against v1.
- **`:57`** — widen the flag: it is not only `resume_on_reconnect[1]`. The full stale set was
  `headline`, `resume_on_reconnect[1]/[2]/[3]`, `resume_entry_point`,
  `carter_decisions_outstanding[0]`, `repo_fixes_status[2]`, `suite_baselines["tests/m3"]` and
  `freeze_state`. Mark it **✅ REFRESHED 2026-09-16 by quick-260916-vqp** (history preserved in
  `headline_PRIOR_2026_09_16` and in the in-place annotations).
- **`:59`** — prefix the heading with `✅ DONE 2026-09-16 —` while keeping `**2. RAM-1 —
  agent-doable now (NCSU, TDD, before Stage C).**` readable as written, **and name the decision
  record on the same line: `DEC-2026-09-16-ram1-launcher-measurement`.** That id appears **0 times
  in STATE.md today** (measured) while `must_haves.artifacts[".planning/STATE.md"].contains`
  requires it — this edit is what satisfies that must-have, and V3 asserts it.
- **`:82`** — same treatment for `**3. tcujq docstring defect — agent-doable, cheap.**`, and mark
  the "CODE-pinned, so docstring edits are free" clause as the corrected premise (the correction
  already sits below it at `:84`).
- **`:88`** — locate by the backtick-free anchor `executing after this close-out` (n = 1) and append
  after it `(✅ COMPLETE 2026-09-16 — commits b6b1f70/b709ce1/48b8828/621701c; see the DONE bullet
  below)`. ⛔ Do NOT search for `In progress as quick-260916-oyq` as one literal — in the file the
  task name is backticked, so that string does not exist.
- **`:89`** — two corrections, both additive:
  (i) `(+31 / +28 below the notice)` is wrong below the SECOND insertion. Measured from the
  `48b8828` hunks: `condition_ld_matrix.py` **+31 for old lines 3-124 and +37 from old line 125**
  (`:153 -> :190`, `:200 -> :237`, docstring `:130 -> :167`); `write_conditioned_ld_npz.py`
  **+28 for old 4-85 and +29 from old 86**.
  (ii) `name the retained :35/:37/:39 rules` overstates. Measured: only the
  `condition_ld_matrix.py` notice names them, and it names them **by content** at `:19-21` ("the
  fully-NaN-row drop rule …, the PSD regularization methods, and the raw-panel NaN-raise
  contract"); the token `:35`/`:37`/`:39` appears in NEITHER module; the
  `write_conditioned_ld_npz.py` notice does not name the retained rules at all (M8).
- **Add ONE short pointer bullet** at the end of the `★ RESUME HERE ★` block's numbered list (a new
  item, e.g. `8. **Blast-radius review (2026-09-16) — banked, no blocker.**`): name
  `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md` and
  `.planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md` (= the "codex-review.md beside
  this file" that §D of the banked file refers to); state the verdict (no BLOCKER; code, tests,
  artifacts and pre-registered behaviour intact; the findings are record propagation, the
  Seth-bound draft and fire-time preconditions); and state what THIS task did and did NOT close —
  B1/B8/B9/B10 records refreshed here; **B2 (draft v2), B3/B4/B5/B6/B7/B11/B14 (next Stage C fire /
  COST-1 / the runbooks + skills) remain OPEN and belong to other tasks.** Keep it to a handful of
  lines; the banked file carries the detail.

**STEP 4 — prove and commit.** Write and run `$VQP/handoff_check.py` and `$VQP/state_check.py`
exactly as specified in `<verification>` below, each with its observed-RED negative control, then:
```bash
git add .planning/HANDOFF.json .planning/STATE.md
git commit -m "docs(quick-260916-vqp): refresh the two resume surfaces — HANDOFF.json B1 fields (history preserved; headline_PRIOR_2026_09_16; recorded Popen+os.wait4 fix recorded FALSIFIED) + STATE.md B9 slips (dated --live scope, citation bases, DONE headings, measured two-segment line shift)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && python3 -c "import json;json.load(open('.planning/HANDOFF.json'))" && echo "HANDOFF parses" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch/handoff_check.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python /gpfs_common/share01/clintonlab/ckclinto/tmp/260916-vqp-scratch/state_check.py && OUT=$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python $(ls -d .planning/quick/260916-kht-*/260916-kht-verify.py) | tail -1) && echo "$OUT" && [ "$OUT" = "RESULT GREEN checks=317 parsed=88 table=88 verified=88" ] && echo "TASK3 OK"</automated>
  </verify>
  <done>HANDOFF.json parses, keeps all 59 pre-existing keys and every array length, changes only the 8 declared fields + `timestamp`, preserves every PRE string verbatim (headline via `headline_PRIOR_2026_09_16`), and still round-trips byte-identically under `json.dumps(indent=2, ensure_ascii=True)`. STATE.md's touched PRE lines all survive verbatim, every `-` line in the diff is a declared touched line, the frontmatter is no worse than PRE, and no new `"` was introduced into a frontmatter scalar. kht default is GREEN again. One commit, explicit paths.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| scratchpad -> repo (Task 1) | externally-authored text is copied into the repo; the integrity property is BYTE IDENTITY to the source, proven by `cmp` + md5 on both sides, not by reading it |
| agent -> pre-registration ledger | `.planning/osf_deviations.md` is the public-facing pre-registration record; the integrity property is APPEND-ONLY |
| agent -> resume surfaces | `HANDOFF.json` / `STATE.md` drive the next session's actions; a silent deletion here causes wrong work later |
| (none) | no network, no OSF, no Seth, no cloud, no perimeter, no code path — this task cannot move a scientific number |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-vqp-01 | Tampering | `.planning/osf_deviations.md` (pre-registration ledger) | mitigate | insertion-only prover (`post == pre[:k]+INS+pre[k:]`, exit 0/1) + numstat deletions == 0 + a per-line "every PRE line still present verbatim" scan; negative control observed at rc exactly 1 |
| T-vqp-02 | Tampering | `.planning/DECISIONS.md`, halt record, `.continue-here.md` | mitigate | same prover + negative control; history blocks are never re-labelled |
| T-vqp-03 | Tampering | `.planning/HANDOFF.json` | mitigate | PRE key set must be a SUBSET of POST; array lengths pinned; every edited string must CONTAIN its PRE text; `headline`'s PRE value stored verbatim under a PRIOR key; writer fidelity proven by a byte-identical round trip |
| T-vqp-04 | Tampering | `.planning/STATE.md` | mitigate | every `-` line in `git diff -U0` must be a PRE line in `ALLOWED_DELETIONS` (which includes `:7`/`:17` and excludes `:78`); `PRESERVED` lines must survive as substrings; frontmatter key list + fence EXISTENCE (never its line number) checked; parse-failure CAUSE (`type`, `e.problem`, mark still on `last_activity:`) equal PRE vs POST, mark line/col explicitly NOT pinned |
| T-vqp-05 | Information disclosure / integrity | the banked review copies | mitigate | byte-identical copy, no header, md5 + `cmp` both directions; the §D sibling-name mismatch is recorded OUTSIDE the frozen files (in STATE.md) |
| T-vqp-06 | Tampering | frozen/forbidden paths (`src/`, `tests/`, `config/`, `bin/`, `.claude/skills/`, `.planning/amendments/`, ROADMAP, the Stage C draft, the kht verifier, the ox1 runbooks) | mitigate | `git status --porcelain -- <paths>` empty AND `git diff --numstat 621701c HEAD -- <paths>` empty AND `git diff --name-only 621701c HEAD` equals exactly the 11 allowed paths |
| T-vqp-07 | Repudiation | a record claim that was never measured | mitigate | every written number carries the command that produced it in the SUMMARY; the findings file is declared INPUT and is corrected twice in `<input_errata>` |
| T-vqp-08 | Denial of service | GPFS loose-object loss mid-commit | accept (with a stop rule) | a commit failure with `invalid object` / `Error building trees` is an immediate STOP + report, per memory `reference_gpfs_git_object_store_loss`; no recovery is improvised inside this task |
| T-vqp-09 | Elevation of privilege | none — no executable artifact is produced or modified | accept | docs-only; the scratch scripts live outside the repo and are never committed |
</threat_model>

<verification>
Run AFTER the last commit. Every check must pass; a failure is reported, never worked around.

**V1 — HANDOFF validity, exactly as required by the brief:**
```bash
python3 -c "import json;json.load(open('.planning/HANDOFF.json'))" && echo "V1 OK"
```

**V2 — `$VQP/handoff_check.py` (write it to do all of this, exit 0/1):**
- PRE = `git show 621701c:.planning/HANDOFF.json`, POST = the file on disk.
- `set(PRE) <= set(POST)` — **no pre-existing key dropped** (print any missing).
- every PRE list keeps its exact length in POST.
- **split the key accounting into three sets; do not conflate them:**
  - `CHANGED = {k for k in set(PRE) & set(POST) if PRE[k] != POST[k]}` must be a SUBSET of
    `{headline, resume_on_reconnect, carter_decisions_outstanding, repo_fixes_status,
    suite_baselines, freeze_state, resume_entry_point, timestamp}`;
  - `ADDED = set(POST) - set(PRE)` must EQUAL exactly
    `{headline_PRIOR_2026_09_16, timestamp_reason_2026_09_16_blast_radius}` — no more, no fewer.
    (If the executor departs from the PRIOR-key convention for `headline`, it must update this
    set AND justify the departure in the SUMMARY's convention table.)
  - `REMOVED = set(PRE) - set(POST)` must be EMPTY.
- changed array ELEMENT indices are exactly: `resume_on_reconnect [1,2,3]`,
  `carter_decisions_outstanding [0]`, `repo_fixes_status [2]`.
- history preservation: `POST['headline_PRIOR_2026_09_16'] == PRE['headline']` exactly; and for
  every other changed string (incl. the three arrays' changed elements, `freeze_state`,
  `resume_entry_point`, `suite_baselines['tests/m3']`), `PRE_text in POST_text` is True.
- writer fidelity: `json.dumps(POST, indent=2, ensure_ascii=True).encode() == open(...,'rb').read()`.
- **negative control:** run the same script against a scratch copy with one pre-existing key
  deleted; require **rc exactly 1**.

**V3 — `$VQP/state_check.py` (exit 0/1):**
- PRE = `git show 621701c:.planning/STATE.md`. **Two DISTINCT sets, kept distinct:**
  - `PRESERVED = {15,26,39,40,48,49,55,57,59,78,82,88,89}` — for each, the PRE line text must be a
    substring of the POST file. `:78` is in here as a **REGRESSION GUARD**: no STEP 3 action edits
    it, so it must survive untouched. For `:17` (`last_activity`) assert the PRE **scalar body**
    (everything after the first `"` up to the final `"`) is a substring of POST. `:7`
    (`last_updated`) is the single exempt line — its value is replaced by design.
  - `ALLOWED_DELETIONS = {7,15,17,26,39,40,48,49,55,57,59,82,88,89}` — **this is the set the diff
    is judged against. It INCLUDES `:7` and `:17`** (both are edited in place, so both legitimately
    appear as `-` lines — omitting them was a bug in revision 0) and **EXCLUDES `:78`** (never
    edited, so a `-` line for it is a FAIL). It is an UPPER BOUND: `:15` may produce no `-` line at
    all, which is fine.
- `git diff -U0 621701c HEAD -- .planning/STATE.md`: every `-` line (excluding the `---`/`+++`
  file headers) must EQUAL a PRE line whose number is in `ALLOWED_DELETIONS`. Print any that do
  not, and FAIL.
- frontmatter integrity — ⛔ **do NOT pin the fence to a line number.** The frontmatter is the block
  between line 1's `---` and the FIRST `---` after line 1, and that closing fence MOVES BY DESIGN
  (`:24` -> `:25`) because STEP 3 inserts exactly ONE comment line below `:15`. Assert instead:
  (a) line 1 is `---`; (b) a closing `---` exists after line 1 (find it, do not assume its number);
  (c) the top-level frontmatter key list is UNCHANGED, same members and same order —
  `gsd_state_version, milestone, milestone_name, status, stopped_at, last_updated, last_activity,
  progress`.
- frontmatter parse parity — ⛔ **the MARK moves; the CAUSE must not.** The plan-checker simulated
  STEP 3's edits and measured PRE
  `('ParserError', "expected <block end>, but found '<scalar>'", line 15, col 4421)` -> POST
  `('ParserError', same problem, line 16, col 4492)` — the move is caused by the one inserted
  comment line and the longer `last_activity` scalar, so a line/column equality check is
  **unsatisfiable** and must not be written. Assert exactly this:
  (i) `yaml.safe_load` on the frontmatter still RAISES;
  (ii) `type(e).__name__` is EQUAL PRE vs POST;
  (iii) `e.problem` is EQUAL PRE vs POST;
  (iv) in BOTH PRE and POST, the frontmatter body line at `e.problem_mark.line` satisfies
       `startswith("last_activity:")` — i.e. the offending scalar is still the SAME scalar.
  A parse that now SUCCEEDS, or fails with a different `problem`, or whose mark lands on a
  different key, is a FAIL to report (it would mean the historical scalar was rewritten).
- count of `"` characters inside the `last_activity` scalar is UNCHANGED from PRE — **PRE count on
  STATE.md:17 is 4** (measured 2026-09-16). This is the check that proves no new quote was
  introduced; it is independent of the parse-parity check above.
- **`contains` / key_link assertions — nothing else in the repo enforces these.** In POST
  STATE.md: `text.count("DEC-2026-09-16-ram1-launcher-measurement") >= 1` AND
  `text.count("260916-BLAST-RADIUS-c93e97b-to-621701c") >= 1`. Both are **0 in PRE** (measured),
  so these are real, falsifiable checks, not tautologies. They pin
  `must_haves.artifacts[".planning/STATE.md"].contains` and both STATE `key_links` patterns.
- **the quick-task ledger row is the ORCHESTRATOR's.** Assert that NO line of POST STATE.md
  matches the regex `^\| *260916-vqp *\|` (i.e. no quick-ledger table row for this task; the
  string appears 0 times in PRE). Prose mentions of `quick-260916-vqp` inside the corrected lines
  (`:26`, `:57`) are EXPECTED and are not table rows — scope the assertion to table rows only.
- **negative control:** run against a scratch copy with one touched PRE line's text removed;
  require **rc exactly 1**.

**V4 — insertion-only proofs (all 7 appended/inserted files), each with its rc==1 negative control:**
```bash
for f in .planning/quick/260916-ocb-*/260916-ocb-SUMMARY.md \
         .planning/quick/260916-ocb-*/260916-ocb-VERIFICATION.md \
         .planning/quick/260916-oyq-*/260916-oyq-SUMMARY.md \
         .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md \
         .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md \
         .planning/osf_deviations.md .planning/DECISIONS.md; do
  $PY $VQP/insert_only.py "$f" 621701c || { echo "INSERT-ONLY FAILED: $f"; exit 1; }
done
git diff --numstat 621701c HEAD -- <those 7 paths> | awk '$2!=0{print "DELETIONS: "$0; exit 1}'
```
Negative control (must be observed, not assumed): for `.planning/osf_deviations.md` and
`.planning/DECISIONS.md`, copy to `$VQP`, mutate one pre-existing byte, re-run the prover against
the copy, and assert `rc -eq 1` — **never** a bare truthy/falsey echo.

**V3b — the plan's own frontmatter fences (C-ter enforcer; claimed in rev 1, unenforced until now):**
```bash
python3 -c "import sys;L=open('.planning/quick/260916-vqp-refresh-stale-records-after-the-2026-09-/260916-vqp-PLAN.md').read().split(chr(10));f=[i+1 for i,l in enumerate(L) if l.strip()=='---'];print('bare --- at',f);sys.exit(0 if f==[1,100] else 1)"
#   exactly two bare `---`: the opening fence (1) and the closing fence (100). A bare `---`
#   divider in the BODY makes gsd-tools read the LAST block as frontmatter (valid:false).
```

**V5 — banked files byte-identical:**
```bash
BLAST=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/blast   # ⚠ was undefined in rev 1 -> V5 false-RED under set -u
cmp -s "$BLAST/260916-BLAST-RADIUS-findings-consolidated.md" .planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md
cmp -s "$BLAST/codex-review.md" .planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md
md5sum "$BLAST/260916-BLAST-RADIUS-findings-consolidated.md" .planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md
#   the two md5s MUST be EQUAL TO EACH OTHER. The VALUE is not pinned (live source).
md5sum "$BLAST/codex-review.md" .planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md
#   equal to each other; expected fce1c52d53308ebffb00031714436193
```
⚠ **Never compare a banked md5 against a digest written in this plan** — the findings source is
live (M21). The assertion is source-vs-copy equality plus `cmp`. Record the measured values.
No banked-by header was added to either file; say so explicitly in the SUMMARY.

**V6 — frozen / forbidden paths untouched:**
```bash
FROZEN="src tests config bin .claude/skills .planning/amendments .planning/ROADMAP.md \
  .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md \
  .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio \
  .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r \
  .planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-VERIFICATION.md"
git status --porcelain -uno -- $FROZEN     # MUST be empty
git diff --numstat 621701c HEAD -- $FROZEN # MUST be empty
git diff --name-only 621701c HEAD          # MUST be EXACTLY the 11 committed paths, no more
```
(NOTE: there is no top-level `workflow/` dir in this repo — Snakemake lives in `src/snakemake/` and
`./Snakefile`, both covered above. Record that in the SUMMARY.)

**V7 — the kht verifier, before and after (already run at pre-flight; re-run now):**
```bash
K=$(ls -d .planning/quick/260916-kht-*/260916-kht-verify.py)
# DEFAULT — assert the exact string AND rc 0. (A bare `| tail -1` takes tail's rc: asserts nothing.)
$PY "$K" > "$VQP/kht-default-after.txt"; RC=$?
OUT=$(tail -1 "$VQP/kht-default-after.txt"); echo "$OUT   rc=$RC"
[ "$OUT" = "RESULT GREEN checks=317 parsed=88 table=88 verified=88" ] && [ "$RC" -eq 0 ] || exit 1
# --live — EXPECTED RED. Assert the exact RED string AND rc 1. It is NOT to be "fixed".
$PY "$K" --live > "$VQP/kht-live-after.txt"; RC=$?
OUT=$(tail -1 "$VQP/kht-live-after.txt"); echo "$OUT   rc=$RC"
[ "$OUT" = "RESULT RED 31/318 parsed=88 table=88 verified=64" ] && [ "$RC" -eq 1 ] || exit 1
```

**V8 — no test reads these records (so no suite run is required):**
```bash
$PY - <<'EOF'
import pathlib,re,sys
pat=re.compile(r'(HANDOFF\.json|STATE\.md|osf_deviations\.md|DECISIONS\.md|\.continue-here)')
hits=[f"{p}:{i}" for p in pathlib.Path('tests').rglob('*.py')
      for i,l in enumerate(p.read_text(errors='replace').split('\n'),1) if pat.search(l)]
print(hits)
# EXPECT exactly 3, all PROSE (source_freeze.py:40, test_source_freeze_pins.py:98, :188).
sys.exit(0 if len(hits)==3 else 1)
EOF
```
If this returns anything else, a test DOES depend on a record: run that test file with the
smoke_dev python and report the result.

**V9 — post-commit guard:** `git log --oneline -5` shows exactly the three new
`docs(quick-260916-vqp): …` commits on top of `621701c`, each with the `Co-Authored-By: Claude
Opus 5 <noreply@anthropic.com>` trailer (`git log -3 --format='%h %(trailers:key=Co-Authored-By)'`);
`git status --porcelain -uno` is empty; **do not push** (the orchestrator decides).
</verification>

<success_criteria>
- [ ] Pre-flight guard passed (HEAD `621701c`, clean tracked tree, origin == HEAD, kht default GREEN)
- [ ] V1-V9 all pass; every negative control was OBSERVED (rc exactly 1), not assumed
- [ ] Both blast-radius files banked byte-identically, no header added
- [ ] `.planning/osf_deviations.md` and `.planning/DECISIONS.md` changed by insertion only, with
      every PRE line still present verbatim
- [ ] `.planning/HANDOFF.json` keeps all 59 pre-existing keys, all array lengths, all PRE strings;
      `headline_PRIOR_2026_09_16` holds the old headline verbatim; the recorded `Popen` + `os.wait4`
      fix is recorded FALSIFIED and flagged do-not-reinstate
- [ ] `.planning/STATE.md` B9 slips corrected additively; frontmatter no worse than PRE; the
      executor committed STATE.md itself
- [ ] Three commits, `docs(quick-260916-vqp): …`, explicit paths only, trailer present, not pushed
- [ ] Every record claim carries its re-derivation command in the SUMMARY; disagreements with the
      findings file are reported as FINDINGS (see `<input_errata>` — two are already known)
- [ ] Out-of-scope items named in the SUMMARY as OPEN: B2 draft v2; B3/B4/B5/B6/B7/B11/B14; the
      `tests/m3` freeze-prose blanket claims; `260916-oyq-VERIFICATION.md:26`; the
      `condition_ld_matrix.py:159-160` docstring nuance (recorded as a DEC cross-ref line);
      STATE.md:62-63 probe labelling; STATE.md:2223-2226; the `260916-vqp` quick-ledger row
      (orchestrator's close-out)
- [ ] $0. Nothing fired, started, stopped or deleted. No OSF, Seth, cloud or network contact.
</success_criteria>

<output>
Write `.planning/quick/260916-vqp-refresh-stale-records-after-the-2026-09-/260916-vqp-SUMMARY.md`
(do NOT commit it — the orchestrator commits PLAN/SUMMARY/VERIFICATION afterwards).

It must contain:
1. The three commit shas + what each touched.
2. **The convention table**: for each HANDOFF field, which history convention was used
   (PRIOR-key vs in-place dated annotation) and why — and **note the PRECEDENT DIVERGENCE
   explicitly**: the file uses PRIOR-KEYS for `headline` / `resume_on_reconnect` /
   `resume_entry_point` (`*_PRIOR_2026_09_10` etc. all exist) but IN-PLACE `⚠ CORRECTED …`
   annotations for `gates.*` and `repo_fixes_status[0]`. This plan deliberately uses PRIOR-key for
   `headline` ONLY and in-place annotation for the other seven, because those seven still contain
   LIVE open items that must not be split across two keys. If the executor departs from that,
   V2's `ADDED` set must be updated and the departure justified here.
3. **The re-derivation log**: every number/SHA/line citation written into a record, with the
   command that produced it and its output.
4. The verification results V1-V9, with each negative control's observed rc.
5. Findings: anything measured that contradicted the findings file or this plan.
6. The OPEN list from `<success_criteria>`, unresolved and named.
</output>
