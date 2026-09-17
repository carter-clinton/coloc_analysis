---
phase: quick-260916-vqp
verified: 2026-09-17T04:55:19Z
status: gaps_found
score: 5/7 must-haves verified (1 FAILED, 1 PARTIAL)
overrides_applied: 0
verifier_basis: HEAD 3f418df (parent 621701c); all probes read-only; no repo byte written except this file
gaps:
  - truth: "Nothing false was written into a record — every factual claim the new text makes is true at HEAD"
    status: failed
    reason: >-
      Two line/number citations written by this task were invalidated by this task's OWN
      later commit and were not reported. Both are in COMMITTED records. Neither is a
      data-integrity failure; both are the same failure class the task existed to fix.
    artifacts:
      - path: ".planning/STATE.md"
        issue: >-
          POST :40 states "Re-measured 2026-09-16 at HEAD `621701c`: ... `--live` is
          `RESULT RED 31/318 parsed=88 table=88 verified=64`". Measured by me at HEAD
          3f418df: `RESULT RED 38/318 parsed=88 table=88 verified=58` (rc 1). That line
          was written in commit 3f418df, AFTER commit 5a2b437 had already changed the
          number, and 621701c was not HEAD at that moment. No committed file contains
          `38/318`, `+35` or `1057` — the correction exists only in the still-untracked
          SUMMARY §5.1.
      - path: ".planning/DECISIONS.md"
        issue: >-
          The new DEC entry cites `.planning/STATE.md:65` for the MAP_SHARED
          naive-probe trap. Correct at commit 5a2b437; commit 3f418df inserted one line
          at STATE.md:16, so the trap is now at :66 and :65 reads "The driver holds the
          cohort `.bim` at spawn, so `Popen` + `os.wait4` would still flat-line the column."
    missing:
      - "A committed record (STATE.md ★ RESUME HERE ★ and/or HANDOFF.json) stating the CURRENT `--live` string `RESULT RED 38/318 parsed=88 table=88 verified=58`, the `+35` shift from `.planning/osf_deviations.md:344`, and that `--live` is still EXPECTED RED and NOT to be fixed."
      - "Correct the DEC entry's `.planning/STATE.md:65` citation to `:66`, or make it basis-qualified (`:65 at 5a2b437`) the way every other citation in that entry is."
  - truth: "STATE.md's `--live` statement is dated and scoped to a basis that a resuming agent can act on"
    status: partial
    reason: >-
      All seven declared STATE.md corrections are present and correct (dated/scoped
      `--live` clause, per-citation bases with HEAD equivalents, two DONE headings, the
      measured two-segment shift, `DEC-2026-09-16-ram1-launcher-measurement` x3,
      `260916-BLAST-RADIUS-c93e97b-to-621701c` x3, and NO `260916-vqp` ledger row).
      The dating/scoping is real, but the NUMBER it scopes is superseded — see the gap
      above. Structural integrity of STATE.md is fully VERIFIED.
    artifacts:
      - path: ".planning/STATE.md"
        issue: "POST :40 sets the reader's expectation to 31/318; the true value at HEAD is 38/318."
    missing:
      - "One additive dated clause on :40 recording the 38/318 re-measurement and its cause."
deferred:
  - truth: "The +35 osf_deviations shift is fully enumerated across the repo"
    addressed_in: "quick-260916-vqq (Stage C draft v2)"
    evidence: >-
      SUMMARY §5.1 and §6 explicitly route the shift to 260916-vqq: \"v2's
      osf_deviations.md citations must either be re-based to +35, or stated as read at
      basis c93e97b\". The actionable citations (the Stage C DRAFT's 5, STATE.md:46) are
      named correctly. See Residual R1 for the full 36-citation count I measured.
human_verification:
  - test: "Decide whether the two gaps warrant a 4th commit now, or a follow-up quick task."
    expected: "Carter/orchestrator decision. The executor deliberately declined a 4th commit to preserve the plan's 'exactly three commits' pin (V9) and to avoid touching frozen files; that reasoning is sound and is recorded in SUMMARY §5.1."
    why_human: "A scope/economy trade-off on a records-only task, not a programmatic fact."
---

# Quick 260916-vqp: Refresh the stale records after the 2026-09-16 blast-radius review — Verification Report

**Task Goal:** Refresh the records the 2026-09-16 blast-radius review found stale — HANDOFF.json's
stale resume fields, STATE.md's own slips, `.continue-here.md`, the Stage B halt record's falsified
RAM-1 remedy, the trsx5 ledger's missing resolution pointer, a DEC entry for RAM-1's launcher
decision, the two banked review records, and as-of correction notes in three quick-task files.
DOCS/RECORDS ONLY.

**Verified:** 2026-09-17T04:55:19Z
**Status:** gaps_found (2 gaps, both minor, both "stale citation created by this task's own later commit")
**Re-verification:** No — initial verification.

Everything below was RE-DERIVED by me by running code against the repo. The SUMMARY was read as a
set of claims to test, never as authority. My checkers are my own (`h_check.py`, `s_check.py`,
`ins.py`); I did not reuse the executor's scripts for any assertion, only for re-running its
preserved negative-control artefacts. Probes lived under
`…/scratchpad/ver-vqp` and were deleted. No cloud, no network, no processes left behind.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **Nothing was lost.** HANDOFF keys/values/round-trip; insertion identity on the append-only files; 0 deletions | ✓ VERIFIED | See §1. 31/32 independent assertions OK; the 1 exception (`timestamp`) is a by-design replacement matching the file's own 5-precedent convention |
| 2 | **Nothing false was written** (≥10 factual claims spot-checked) | ✗ FAILED | 20+ claims re-derived and TRUE; 2 stale citations created by this task's own commit 3f418df — see Gaps |
| 3 | **The stale statements no longer instruct** the live HANDOFF fields | ✓ VERIFIED | See §3. Live projection proven non-empty (49 live keys / 172 strings / 78,425 chars) with positive controls; all 6 stale strings retained verbatim BY DESIGN (plan must_have #4) and each dominated by an adjacent dated correction |
| 4 | **STATE.md**: dated/scoped `--live`, citation bases, DONE headings, two-segment shift, both new ids, no `260916-vqp` ledger row | ⚠ PARTIAL | All 7 sub-items present and correct; the NUMBER the `--live` clause scopes is superseded (same root cause as Gap 1) |
| 5 | **Banked records byte-identical to their live sources** (cmp + equal md5 both ways, no pinned digest) | ✓ VERIFIED | See §5 |
| 6 | **The executor's three findings are accurate** (+35/38-318; 2026-09-17 wall clock; the caught false green) | ✓ VERIFIED | All three reproduced firsthand — see §6 |
| 7 | **14 negative controls at rc exactly 1**; re-run ≥4 | ✓ VERIFIED | 18 observed at rc exactly 1, plus positive controls at rc 0 on all three checkers — see §7 |

**Score:** 5/7 truths verified (1 FAILED, 1 PARTIAL)

---

## 1. Nothing was lost

### 1a. `.planning/HANDOFF.json` (my own `h_check.py`, 32 assertions)

| Assertion | Result |
|---|---|
| PRE top-level keys == 59 | OK |
| POST top-level keys == 61 | OK |
| `REMOVED = set(PRE) - set(POST)` empty | OK (`[]`) |
| `ADDED` EXACTLY `{headline_PRIOR_2026_09_16, timestamp_reason_2026_09_16_blast_radius}` | OK |
| `CHANGED` ⊆ the 8 declared fields | OK (`carter_decisions_outstanding, freeze_state, headline, repo_fixes_status, resume_entry_point, resume_on_reconnect, suite_baselines, timestamp`) |
| all 10 PRE arrays kept their exact length | OK (5,5,9,8,2,4,2,3,6,9) |
| changed element indices exactly `resume_on_reconnect[1,2,3]`, `carter_decisions_outstanding[0]`, `repo_fixes_status[2]` | OK |
| `POST['headline_PRIOR_2026_09_16'] == PRE['headline']` verbatim | OK |
| every PRE string of every changed field present verbatim in the POST **file text** (JSON-escaped form) | OK for 9/9 — the 10th is `timestamp`, see below |
| `json.dumps(POST, indent=2, ensure_ascii=True).encode() == raw` | OK — byte-identical, 100,000 B |
| no trailing newline | OK |
| PRE also round-trips byte-identically (writer-fidelity baseline) | OK |

**The single non-preserved PRE value is `timestamp`** (`2026-09-16T18:40:00Z` → `2026-09-17T04:20:01Z`);
the old value appears nowhere in the file. This is **by design and matches the file's own convention**:
the file carries five prior `timestamp_reason_<date>` keys (`_08_12`, `_08_12_evening`, `_08_14`,
`_08_16`, `_08_26`) and **none** of them preserves a prior timestamp value. PLAN step 11 mandates the
replacement, and V2's containment list explicitly excludes `timestamp`. **Not a gap.**
`headline_PRIOR_2026_09_16` sits immediately before `headline` in key order, as planned.

### 1b. Insertion-only identity on the 7 append/insert files

My prover is **stricter** than the plan's: besides `post == pre[:k] + INSERT + pre[k:]` and the
last-non-empty-PRE-line-as-a-WHOLE-LINE test, it asserts **every** non-empty PRE line survives as a
whole line of POST. All 7 pass at rc 0:

| File | prefix_k | inserted B | tail B | numstat |
|---|---|---|---|---|
| `260916-ocb-SUMMARY.md` | 36,004 | 1,608 | 0 | `25  0` |
| `260916-ocb-VERIFICATION.md` | 18,311 | 661 | 0 | `13  0` |
| `260916-oyq-SUMMARY.md` | 14,472 | 1,231 | 0 | `20  0` |
| `.continue-here.md` (PREPEND) | 377 | 2,738 | 176,558 | `14  0` |
| `260824-STAGE-B-HALT-…md` | 16,321 | 3,376 | 0 | `49  0` |
| **`.planning/osf_deviations.md` (INSERT)** | **25,783** | **2,925** | **53,361** | `35  0` |
| `.planning/DECISIONS.md` | 203,326 | 6,197 | 0 | `86  0` |

The osf_deviations **insertion identity** is therefore proven explicitly:
`post == pre[:25783] + INSERT(2925 B) + pre[25783:]` with a 53,361-byte intact tail.
First divergent line = `:344` exactly (the section-closing `---`), as the plan directed.
Measured line-by-line: **every PRE line from `:344` onward sits at exactly `+35` in POST** and
every PRE line below `:344` is unshifted. `git diff --numstat` deletions column is **0** for all 7.

`git diff --name-only 621701c HEAD` = exactly **11** paths. Tracked tree clean. All three commits
carry the `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer. Not pushed
(`origin/m3-W2-aou-deltas` = `621701c`).

---

## 2. Nothing false was written — 20+ claims re-derived

| # | Claim (where it is written) | Re-derived result |
|---|---|---|
| 1 | 13 commit SHAs + subjects (`f09535c 11f61e8 f8ff9cd 9a3eb97 0231cbf b6b1f70 b709ce1 48b8828 621701c c93e97b bf16289 3684413 1333f3f`) | ✓ all resolve with matching subjects; `c93e97b` = 2026-09-16 session close, `bf16289` = 2026-07-16 |
| 2 | **Suite provenance** — `ocb-VERIFICATION.md:147` | ✓ verbatim: "checked from the executor's artefacts, **not re-run** … I parsed `…/m3-{before,after}.xml` myself by node id: before `passed=1187 skipped=33`, after `passed=1212 skipped=33`, added 25" |
| 3 | **Suite provenance** — `oyq-VERIFICATION.md:33` | ✓ verbatim: "I parsed the executor's JUnit files myself … POST `suite_post.xml`: 1262 ids = **1229 passed / 33 skipped** … **ADDED 17**, REMOVED 0, CHANGED 0" |
| 4 | HANDOFF `suite_baselines` says the verifiers **RECONCILED BY TEST ID** and **NOT re-run** | ✓ present, with the ⛔ do-NOT-write warning; `1122` now sits inside `--- PRIOR ENTRY, RETAINED VERBATIM …` with 1229/33/0 stated first |
| 5 | **Narrow peak-RAM claim** — `AOU-LD-PIPELINE.md:471/:488/:492` are cluster-sizing prose | ✓ ":471 = ~1.6 TB worker RAM", ":488 = `n1-highmem-16` … RAM-bound", ":492 = fit in one cluster's worth of RAM"; 0 hits in the posted trsx5 body, mk7ze, tcujq and the trsx5 project copy (measured with GNU grep from a script) |
| 6 | RAM-1 numbers: VmHWM **523,060** KiB (VmRSS 11,400), trivial child **523,060**; 3.9 fork **413,992**; first tiny child **106.8 MiB** (VmHWM 109,504); `.bim` **20,767,864** lines; launcher floor **11,264 / 4,352** KiB | ✓ all at `ocb-PLAN.md:112`, `:113`, `:115`, `:118`, `:121` (and `:203` for the bias table) |
| 7 | NC01 RED **A2 362.59 / A3 362.92** MiB (`ocb-SUMMARY.md:44`); post-fix **307.96 → 11.00**, **11.25** (`:41`-`:42`) | ✓ exact lines |
| 8 | Carter's verbatim choice `Small launcher process (Recommended)` | ✓ `ocb-PLAN.md:14`, `:97`; also `ocb-SUMMARY.md:8`, `:70`, `ocb-VERIFICATION.md:15` |
| 9 | Halt record `:118`-`:122` ("region 17 → 2.9689 (real, first child) … Region 1's 30.6591 is real") and `:124` ("Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`") and `:146` | ✓ exact at 621701c |
| 10 | **trsx5 resolution quote** — `:326` "None of (1)-(6) has been actioned" at 621701c | ✓ exact |
| 11 | `grep -cE '08-17\|gate-released\|260817' osf_deviations.md` = **0** at 621701c | ✓ 0 (now 6 — self-referentially, because of this insertion; the prose frames it as the pre-insertion state) |
| 12 | **`DEC-2026-08-17-trsx5-gate-released` at `.planning/DECISIONS.md:2030`** | ✓ exact; its `:2032` reads "Decision (CARTER, 2026-08-17 22:32 EDT, verbatim)" — matches the "22:32 EDT" written into the ledger |
| 13 | Posted body **9,695 B** / `c19be8b2ad7cd6a45fee1d668d8a9cf9`; lineage at `3684413` **9,907 B** / `425d925a88ab474ec2396cbea25e665c` | ✓ both re-measured |
| 14 | **Two-segment notice shift** — hunks `@@ -2,0 +3,31 @@` / `@@ -124,0 +156,6 @@` and `@@ -3,0 +4,28 @@` / `@@ -85,0 +114 @@` | ✓ exact; clm `:153→:190`, `:200→:237`, `:130→:167` (all +37, all ≥125); wcn `:4→:32` and `:85→:113` (+28), `:86→:115` (+29). The old blanket "+31 / +28" is correctly superseded |
| 15 | M8 — the tokens `:35`/`:37`/`:39` appear in **NEITHER** module; `condition_ld_matrix.py:19-21` names the retained rules BY CONTENT | ✓ python substring scan: `{':35':0, ':37':0, ':39':0}` in both; `:19-21` = "trsx5 RETAINS, unchanged, the fully-NaN-row drop rule …, the PSD regularization methods, and the raw-panel NaN-raise contract" |
| 16 | M6 — `bf16289..HEAD` numstat: clm `37 0`, wcn `29 0`, and plink_ld_to_npz / occlusion_span_filter / ld_npz_to_rds.R report NOTHING | ✓ exact |
| 17 | **`condition_ld_matrix.py:159-160` nuance** ("trsx5 retains the fully-NaN-row drop rule that this raise directs") | ✓ exactly lines 159-160; recorded as one line in the DEC's "Consequences recorded, not decided", not edited (frozen) |
| 18 | M3/M4 line map — 1344 → 1487 lines, numstat `156 13`, **all 7 hunks at old `:184-203`**, every one of the 11 citations at **+143**; `:965`/`:1139` non-unique (7× each) and offset-derived | ✓ reproduced exactly, including the two non-unique lines and the offset-target text match |
| 19 | M10 — the committed Stage C command at `260812-ox1-AGENT-PROMPT.md:398` has **no `--fail-fast`** | ✓ exact (`nohup timeout 312h python3 … --mode square --ancestry AFR > …`) |
| 20 | M16 — docstring-stripped top-level AST diff = 1 CHANGED (`_run_plink`) + 1 ADDED (`_PLINK_PEAK_RSS_LAUNCHER`), 0 REMOVED | ✓ reproduced. Node count: I measure `len(ast.parse().body)` **59 → 60** raw (58 → 59 if the module-docstring node is also dropped). The DEC's "59 → 60" is correct under the natural reading and is internally consistent with the SUMMARY's `A[58]==B[59]`. **Not a defect.** |
| 21 | M18 — the benchmark writer is `test_no_whole_parent_dense_materialization` (`:54`-`:138`, `write_text` at `:138`); `…_records_metrics` at `:141` only READS (`:145`-`:148`) | ✓ exact — the `ocb-SUMMARY:392` correction is right |
| 22 | `fire_verifier.check_peak_ram` at `src/python/fire_verifier.py:733` (review said `:735`) | ✓ `:733` |
| 23 | `oyq-VERIFICATION.md:26` off-by-one: `213→250`/`112→141` written, `wc -l` gives `212→249`/`111→140`; deltas `+37`/`+29` correct | ✓ reproduced; reported-not-fixed, as scoped |
| 24 | M22 — `§B2` of the banked file lists exactly **7** numbered items ("MEDIUM ×7") | ✓ 7 (`:72,:78,:79,:80,:81,:85,:89` under the `### B2` heading at `:71`) |
| 25 | `tests/m3` blanket freeze prose still false for the two byte-pinned modules (`source_freeze.py:9-10`, `test_source_freeze_pins.py:15`) | ✓ "Correcting a wrong comment in a frozen file therefore costs **nothing**" — correctly reported as OPEN, untouched |
| 26 | `osf_deviations.md:133` / `:166` (cited in HANDOFF text) | ✓ both correct and both below `:344`, therefore unaffected by the +35 shift |

**The two that are NOT true at HEAD** are in §Gaps.

---

## 3. The stale statements in the HANDOFF live fields

**Projection proven non-empty first** (so the absence/adjacency assertions are not vacuous):
49 live top-level keys (every key without `_PRIOR`), 172 strings, **78,425 chars**; positive
controls `"Stage C"`, `"RESUME"`, `"NaN"` all present.

**Finding of method:** all six stale strings **do survive in live fields**. That is **required by
the plan**, not a defect — must_have truth #4 mandates the file's IN-PLACE DATED ANNOTATION
convention ("every other edited string CONTAINS its PRE text verbatim"), which is the convention
`gates.m3_04b`, `gates.m3_04c`, `gates.trsx5_posted_body` and `repo_fixes_status[0]` already use. A
literal-absence test would contradict the plan. I therefore tested the operative property: **is the
stale text still an INSTRUCTION, or is it dominated by an adjacent dated correction in the same
field?**

| Stale string | Live field | Correction that follows it IN THE SAME FIELD |
|---|---|---|
| `Fix with Popen + os.wait4` | `resume_on_reconnect[2]` | `✅ DONE 2026-09-16 …` then `⛔ THE RECORDED FIX IS FALSIFIED AND MUST NOT BE REINSTATED` + the M14 numbers + NC01 RED + `tests/m3/test_run_plink_peak_rss.py` goes RED if anyone does |
| `Agent DRAFTS the options` | `resume_on_reconnect[1]` | `⚠ UPDATED 2026-09-16 … 'Agent DRAFTS the options' is DONE. The draft IS banked (f09535c …)` |
| `docstring edits are FREE` | `resume_on_reconnect[3]` | `✅ DONE 2026-09-16 …` + `⚠ THE PREMISE ABOVE IS WRONG AND IS RETAINED AS WRITTEN` |
| `items 2-3 are agent-doable immediately` | `resume_entry_point` | `⚠ CORRECTED 2026-09-16 …: items 2-3 are DONE … and are NO LONGER 'agent-doable immediately'` + the STATE-wins tie-break |
| `STILL QUEUED` / `THE ONLY ONE OUTSTANDING` | `repo_fixes_status[2]` | `✅ DISCHARGED 2026-09-16 … NOTHING IS OUTSTANDING IN THIS LIST ANY MORE` |
| `1122` suite baseline | `suite_baselines["tests/m3"]` | Not followed by a marker — instead it is **relocated behind** `--- PRIOR ENTRY, RETAINED VERBATIM …`, with `1229 passed / 33 skipped / 0 failed (1262 ids collected) at 621701c` stated FIRST. Correct form. |

**Verdict: ✓ VERIFIED.** No live field reads as a current instruction to do the falsified thing, and
the history is preserved exactly as the file's conventions require.

---

## 4. STATE.md (structural + content)

Read with `sed -n`/substring scans only — the file was never read whole (1,087,011 B).

| Check | Result |
|---|---|
| all 13 PRESERVED PRE lines survive verbatim (incl. the `:78` regression guard) | ✓ |
| PRE `:17` `last_activity` scalar **body** (8,962 chars) survives verbatim | ✓ |
| `"` count inside `last_activity` unchanged at **4** (PRE and POST) | ✓ |
| every `-` line in `git diff -U0` is a PRE line in ALLOWED_DELETIONS | ✓ 13 `-` lines, PRE numbers `[7,17,26,39,40,48,49,55,57,59,82,88,89]` |
| `:78` produced **no** `-` line | ✓ |
| line 1 is `---`; a closing `---` exists (moved `:24 → :25`, **not pinned**) | ✓ |
| frontmatter key list unchanged and in order | ✓ `gsd_state_version, milestone, milestone_name, status, stopped_at, last_updated, last_activity, progress` |
| yaml parse **parity** — still RAISES; same type; same `e.problem`; mark still on `last_activity:` in BOTH | ✓ `ParserError` / `"expected <block end>, but found '<scalar>'"`; mark `15/4421 → 16/6309` (moves by design, correctly not pinned — note the PLAN's *predicted* `16/4492` was a plan-checker simulation and is superseded by the measurement, exactly as the plan allowed) |
| `DEC-2026-09-16-ram1-launcher-measurement` present | ✓ ×3 (PRE ×0) |
| `260916-BLAST-RADIUS-c93e97b-to-621701c` present | ✓ ×3 (PRE ×0); `…codex-review-as-received` ×2 (PRE ×0) |
| **NO** `^\| *260916-vqp *\|` ledger row | ✓ none (4 prose mentions only — expected) |
| `--live` statement is dated/scoped | ✓ dated and basis-named … ⚠ but the NUMBER is superseded — **Gap 1** |
| code citations carry their basis | ✓ `:1144-1146 (at c93e97b; :1287-1289 at HEAD 621701c)` form used throughout; `:965`/`:1139` explicitly flagged as offset-derived and non-unique |
| two completed items marked DONE | ✓ `:60` (RAM-1, naming the DEC id) and `:83` (tcujq, flagging the corrected premise) |
| `+31/+28` corrected to the two-segment form | ✓ `:90` carries the additive two-corrections clause with the measured hunks |

---

## 5. Banked records byte-identical

| File | `cmp -s` | md5 (source) | md5 (banked copy) | `wc -lc` | header added? |
|---|---|---|---|---|---|
| `260916-BLAST-RADIUS-findings-consolidated.md` → `…c93e97b-to-621701c.md` | rc 0 | `3afb70fc3551cc86ae9c6fa9794eea29` | **same** | 213 / 25,784 both sides | **No** — first line is the source's own `# Blast-radius assessment: branch m3-W2-aou-deltas, range c93e97b..621701c (2026-09-16)` |
| `codex-review.md` → `…codex-review-as-received.md` | rc 0 | `fce1c52d53308ebffb00031714436193` | **same** | 28 / 5,256 both sides | **No** |

Asserted as **source == copy**, never against a digest written in the plan (M21: live source).
Negative control on my own `cmp` gate: a 1-byte-prefixed copy returns rc 1. The banked file's `§D`
"See `codex-review.md` beside this file" reference exists, and the rename mapping is recorded
outside the frozen files (STATE.md, ×2), as the plan required.

`min_lines`/`contains` artifact assertions: banked file contains
`Blast-radius assessment: branch m3-W2-aou-deltas, range c93e97b..621701c`; 213 lines == source's
measured `wc -l`; codex copy 28 lines.

---

## 6. The executor's three findings — all three reproduced firsthand

**(a) The `+35` shift and 31/318 → 38/318 — CONFIRMED, and my run is byte-identical to theirs.**

- `.planning/osf_deviations.md` **1022 → 1057** lines; first divergence at `:344`; **every** PRE
  line from `:344` onward is at `+35`; every PRE line below `:344` is unshifted.
- I ran the frozen `260916-kht-verify.py` myself (read-only paths only; `write_bytes` lives solely
  inside `selftest`, which I did not run; tracked tree still clean afterwards):
  - DEFAULT → `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, **rc 0**
  - `--live` → `RESULT RED 38/318 parsed=88 table=88 verified=58`, **rc 1**
- `diff` of the executor's saved BEFORE (at 621701c) against **my fresh** run: exactly **8** changed
  lines — 7 checks (`c:c25`, `c:c70`, `c:n03`, `c:c76`, `c:c77`, `c:c78`, `c-hand:H3`) and the
  RESULT line. **Every one of the 7 cites `.planning/osf_deviations.md`.** No non-OD check moved.
- My fresh `--live` output is **byte-identical** to the executor's saved AFTER file; the executor's
  DEFAULT before == after == my fresh run.
- Their "now at" table is exact: `657→692`, `703→738`, `660→695`, `685→720`, `670→705`, and the
  quoted POST `:670` really does now read `  significance.`.

**(b) Wall clock 2026-09-17 — CONFIRMED.** `date -u` at verification = `2026-09-17`; the three
commits are dated `2026-09-17 00:11:10 / 00:18:10 / 00:27:34 -0400`. Prose labels are `2026-09-16`
by design (load-bearing for must_haves and V3); the two MEASURED timestamps record the truth
(`HANDOFF.timestamp = 2026-09-17T04:20:01Z`, `STATE.md:7 = "2026-09-17T04:20:00.000Z"`).

**(c) The false green they caught — CONFIRMED, firsthand.** `.planning/osf_deviations.md` line 5 IS
blank. Their first-batch mutant `nc_t2_3.md` is **byte-identical** to the committed POST file — the
mutator silently no-op'd — and **my own prover returns rc 0 on it**. The other first-batch mutants
(`nc_t1_1`, `nc_t2_1`, `nc_t2_2`) are real mutants at rc 1. The rewritten
`mutate_one_byte.py` does exactly what §5.3 describes: scans forward from index ≥ 4, and asserts
both `out != b` and `len(out) == len(b)`. This is a textbook
`[[feedback_green_assertion_needs_a_negative_control]]` catch.

---

## 7. Negative controls — 18 observed at rc exactly 1

| Batch | Controls | Observed |
|---|---|---|
| Executor's 7 insertion-only NC artefacts, re-run through **my** prover | `nc2_t1_{1,2,3}`, `nc2_t2_{1,2,3,4}` | **rc 1 ×7**; each verified to differ from the committed POST by exactly **1 byte at equal length** |
| **Fresh mutants I built myself** (flip one pre-existing byte in the PRE prefix region) | `osf_deviations.md`, `DECISIONS.md`, halt record, `.continue-here.md` | **rc 1 ×4** |
| HANDOFF | NC-H1 (key deleted), NC-H2 (PRE sentence removed from `resume_on_reconnect[2]`), **NC-H3 (mine: drop `headline_PRIOR_2026_09_16`)** | **rc 1 ×3** — H3 fired 4 distinct assertions incl. the history-preservation one |
| STATE | NC-S1 (`:26` removed), NC-S2 (`:78` guard removed), NC-S3 (a `260916-vqp` ledger row appended, caught at line 3438), **NC-S4 (mine: strip the DEC id)** | **rc 1 ×4** |
| Positive controls (proving no checker is stuck at 1) | pure append → prover rc 0; real HANDOFF → 31 OK; real STATE → `RESULT GREEN` rc 0; `cmp` gate on a mutated banked copy → rc 1 | ✓ |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| QUICK-260916-vqp | `260916-vqp-PLAN.md` | Blast-radius findings B1/B8/B9/B10 — record propagation only | **SATISFIED with 2 minor defects** | B1 (HANDOFF + `.continue-here`) ✓; B8 (trsx5 ledger pointer) ✓; B9 (STATE slips) ✓ except the superseded `--live` number; B10 (as-of notes + the missing DEC entry) ✓ except the `STATE.md:65` off-by-one |

## Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `.planning/osf_deviations.md` | `DECISIONS.md :: DEC-2026-08-17-trsx5-gate-released` | named sub-entry + line `:2030` | ✓ WIRED (id present; `:2030` re-derived correct) |
| halt record | `DECISIONS.md :: DEC-2026-09-16-ram1-launcher-measurement` | ⚠ SUPERSEDED section names the id + `9a3eb97` | ✓ WIRED |
| `.planning/STATE.md` | `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md` | pointer bullet 8 in the ★ RESUME HERE ★ block | ✓ WIRED (×3, plus the codex sibling ×2) |
| `.planning/HANDOFF.json` | `.planning/STATE.md` | `resume_entry_point` STATE-wins tie-break | ✓ WIRED ("⭐ AND, WHERE THIS FILE AND THE ★ RESUME HERE ★ BLOCK … DISAGREE, STATE.md WINS") |

## Frozen / forbidden paths

`git status --porcelain -uno -- $FROZEN` EMPTY; `git diff --numstat 621701c HEAD -- $FROZEN` EMPTY
(`src tests config bin .claude/skills .planning/amendments ROADMAP.md`, the Stage C draft, the kht
dir, the ox1 dir, `oyq-VERIFICATION.md`, `Snakefile`). `git diff --name-only 621701c HEAD` = exactly
**11** paths. No test reads any of these six records as a path — exactly **3** prose hits
(`tests/m3/source_freeze.py:40`, `tests/m3/test_source_freeze_pins.py:98`, `:188`), so **no suite
run was required and none was performed**.

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `.planning/STATE.md` | 40 | superseded measurement presented as current at "HEAD `621701c`" | ⚠️ Warning | A resuming agent that runs `--live` gets 38/318 and finds no committed explanation — Gap 1 |
| `.planning/DECISIONS.md` | DEC entry | `.planning/STATE.md:65` off by one after the task's own STATE insertion | ⚠️ Warning | Gap 2 |
| `.planning/osf_deviations.md` | new sub-entry | "a search of THIS FILE … returns **ZERO hits** … re-measured 2026-09-16" is written in the present tense but is now 6 (self-referentially) | ℹ️ Info | Context makes the pre-insertion framing clear; no action |

## Residuals (informational — measured by me, NOT reported by the executor)

**R1 — the `+35` blast radius is wider than the SUMMARY enumerates.** Scanning all tracked
`.md/.py/.json/.txt/.R/.yaml` files: **36** citations of `osf_deviations.md` at/after `:344` across
**7** files are now stale, not the 6 the SUMMARY lists. Beyond the Stage C DRAFT (5) and
`STATE.md:46` (1): `260916-kht-verify.py` itself (6 — the mechanism of the RED),
`260916-kht-PLAN.md` (6), `260916-kht-SUMMARY.md` (11), `260908-hv8-…/SUMMARY.md:50`, and 2
self-references inside the newly banked blast-radius file. All but the DRAFT and `STATE.md:46` are
historical quick records, so the practical impact is low and the actionable ones were named
correctly — but the count in §5.1 understates the surface.

**R2 — the `.continue-here.md` PREPEND shifted that file by +14**, invalidating line citations into
it that were valid at `621701c`: `.planning/DECISIONS.md:1482` (`:57` → now `:71`) and the banked
blast-radius file `:62` (`:13` → now `:27`), plus older quick records. This file's own convention is
to prepend, so line citations into it are structurally transient; low severity, unreported.

## Gaps Summary

The integrity properties this task was built to protect all hold, exactly: no HANDOFF key or value
was lost, the JSON writer is byte-faithful, all seven append/insert files pass a **stricter**
insertion-only proof than the plan asked for with 0 deletions, the osf_deviations pre-registration
ledger satisfies the explicit insertion identity, both banked review files are byte-identical to
their live sources with no header, STATE.md's frontmatter is no worse than PRE, and every one of the
executor's three self-reported findings is true — including the false green it caught itself, which
I reproduced. Eighteen negative controls fired at rc exactly 1, with positive controls proving none
of my checkers is stuck.

What is wrong is narrow and is the same failure class the task existed to eliminate: **this task's
own commits invalidated two citations/numbers that this task itself had just written.** Commit
`5a2b437` (the osf_deviations insertion) changed `kht --live` from `31/318` to `38/318`, and then
commit `3f418df` wrote `31/318` into STATE.md's ★ RESUME HERE ★ block labelled "at HEAD `621701c`";
and commit `3f418df`'s one-line STATE.md insertion moved the `MAP_SHARED` line from `:65` to `:66`
after `5a2b437`'s DEC entry had cited `:65`. No committed record carries the correction — it lives
only in the untracked SUMMARY §5.1.

The executor's reasoning for not opening a fourth commit (it would have required touching the frozen
Stage C draft or the frozen kht verifier, or breaking the plan's "exactly three commits" pin and V9)
is sound and is documented. The decision of whether to close these now or route them to
`260916-vqq` is Carter's / the orchestrator's — flagged under `human_verification`.

---

_Verified: 2026-09-17T04:55:19Z_
_Verifier: Claude (gsd-verifier) — all assertions re-derived by running code; scratch probes deleted._
