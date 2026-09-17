---
phase: quick-260916-vqp
plan: 01
subsystem: planning-records
tags: [records-refresh, blast-radius-review, osf-ledger, handoff, state, decisions, docs-only]
requirements: ["QUICK-260916-vqp"]
basis: 621701c
branch: m3-W2-aou-deltas
pushed: false
commits: [f8f30e3, 5a2b437, 3f418df]
status: COMPLETE (3/3 tasks; 1 FINDING to report, 0 blockers)
duration_utc: 2026-09-17T04:05Z -> 2026-09-17T04:35Z
---

# Quick 260916-vqp: Refresh the records the 2026-09-16 blast-radius review found stale — Summary

**Docs/records only. `$0`. Nothing fired, started, stopped or deleted. No OSF, Seth, cloud,
perimeter or network contact. No code, test, config or posted-amendment byte moved.**

Eleven files changed across three commits: 2 banked review files, 4 insertion-only history records,
3 as-of correction notes, and the 2 resume surfaces. `git diff --name-only 621701c HEAD` is
**exactly** those 11 paths.

---

## 1. The three commits

| # | SHA | What it touched |
|---|-----|-----------------|
| 1 | **`f8f30e3`** | `docs(quick-260916-vqp): bank the 2026-09-16 blast-radius review (byte-identical, as-received) + as-of corrections in the ocb/oyq quick records …` — CREATED `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md` and `.planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md` (byte-identical `cp`, **no banked-by header added**); APPENDED one `## ⚠ AS-OF CORRECTION 2026-09-16` block to each of `260916-ocb-SUMMARY.md`, `260916-ocb-VERIFICATION.md`, `260916-oyq-SUMMARY.md`. 5 files, **299 insertions, 0 deletions**. |
| 2 | **`5a2b437`** | `docs(quick-260916-vqp): insertion-only history records …` — PREPENDED the dated block to `.continue-here.md`; APPENDED `## ⚠ SUPERSEDED 2026-09-16` to the Stage B halt record; INSERTED the `### RESOLVED 2026-08-17` sub-entry inside the trsx5 section of `.planning/osf_deviations.md`; APPENDED `DEC-2026-09-16-ram1-launcher-measurement` at EOF of `.planning/DECISIONS.md`. 4 files, **184 insertions, 0 deletions**. |
| 3 | **`3f418df`** | `docs(quick-260916-vqp): refresh the two resume surfaces …` — `.planning/HANDOFF.json` (8 declared fields + `timestamp` + 2 added keys) and `.planning/STATE.md` (B9 slips, additively). 2 files, 31 insertions, 23 deletions (all 23 are in-place extensions of declared touched lines; see V3). |

All three carry the `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer (verified with
`git log -3 --format='%h %(trailers:key=Co-Authored-By,valueonly)'`). Explicit-path staging only —
never `git add .` / `-A`. **NOT pushed** (`origin/m3-W2-aou-deltas` is still `621701c`).
The PLAN and this SUMMARY are **not committed** (orchestrator's close-out), and **no
`260916-vqp` row was added to STATE.md's quick-task ledger** (asserted by V3).

---

## 2. HANDOFF.json convention table

The file carries TWO history conventions. This plan used both, deliberately.

| Field | Convention used | Why |
|-------|-----------------|-----|
| `headline` | **PRIOR-KEY** — PRE value copied verbatim into the new key `headline_PRIOR_2026_09_16`, placed immediately BEFORE `headline`; new text written into `headline` | The file's own precedent for this field: `headline_PRIOR_2026_09_01/_09_08/_09_09/_09_10` all exist. A headline is a single current-state sentence, so splitting is correct. |
| `resume_on_reconnect[1]` | IN-PLACE DATED ANNOTATION (`⚠ UPDATED 2026-09-16 — …` appended, PRE text kept) | Still contains LIVE open items (the Stage C posture). Splitting it across a PRIOR key would hide the live part from the field a resuming agent reads. |
| `resume_on_reconnect[2]` | IN-PLACE (`✅ DONE 2026-09-16 …` + `⛔ THE RECORDED FIX IS FALSIFIED AND MUST NOT BE REINSTATED`) | The falsified prescription must stay **adjacent** to the text that prescribed it. |
| `resume_on_reconnect[3]` | IN-PLACE (`✅ DONE 2026-09-16 …` + `⚠ THE PREMISE ABOVE IS WRONG AND IS RETAINED AS WRITTEN`) | Same: the wrong premise is only legible next to its correction. |
| `carter_decisions_outstanding[0]` | IN-PLACE (`⚠ UPDATED 2026-09-16`) | Still outstanding — it narrowed, it did not close. |
| `repo_fixes_status[2]` | IN-PLACE (`✅ DISCHARGED 2026-09-16`) | The list is a status ledger; a discharged item stays in place with its outcome. |
| `suite_baselines["tests/m3"]` | ITS OWN DOCUMENTED FORM — new measurement FIRST, then `--- PRIOR ENTRY, RETAINED VERBATIM …` + the PRE text verbatim | That is the shape the field already used for the 1122/1121/1101 lineage. |
| `freeze_state` | IN-PLACE (`⚠ CORRECTED 2026-09-16`) | Matches `gates.m3_04b` / `gates.m3_04c` / `repo_fixes_status[0]`. |
| `resume_entry_point` | IN-PLACE (`⚠ CORRECTED 2026-09-16`) | Ditto; also carries the new STATE-wins tie-break. |
| `timestamp` | REPLACED + one new key `timestamp_reason_2026_09_16_blast_radius` | As planned. |

**Precedent divergence, stated explicitly:** the file uses PRIOR-KEYS for `headline` /
`resume_on_reconnect` / `resume_entry_point` (`*_PRIOR_2026_09_10` etc. all exist) but in-place
`⚠ CORRECTED …` annotations for `gates.*` and `repo_fixes_status[0]`. This task used the PRIOR-key
convention for `headline` ONLY and in-place annotation for the other seven, because those seven
still contain LIVE open items that must not be split across two keys. **No departure from the
plan** — V2's `ADDED` set is exactly `{headline_PRIOR_2026_09_16,
timestamp_reason_2026_09_16_blast_radius}`, as declared.

---

## 3. Re-derivation log — every number written into a record, with its command

The consolidated findings file was treated as **INPUT, never authority**. Everything below was
re-measured at execution time on NCSU login node, `$PY =
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python` (3.11).

| M | Command | Measured output | Agrees with plan? |
|---|---------|-----------------|-------------------|
| M1 | `git log --oneline -3` / `git status --porcelain -uno` / `git rev-parse HEAD origin/m3-W2-aou-deltas` | `621701c / 48b8828 / b709ce1`; status EMPTY; both `621701c8c28168b13f188467670d1ab90502ea06` | ✅ |
| M2 | `git log -1 --format='%h %ad %s' --date=short <sha>` ×11 | all 11 subjects exist; `c93e97b` = 2026-09-16 session close, `bf16289` = 2026-07-16 | ✅ |
| M3 | `git show <rev>:src/python/run_native_ld_panel.py \| wc -l`; `git diff --numstat c93e97b HEAD -- <f>`; `$VQP/linemap.py` | `c93e97b=1344 -> HEAD=1487`; numstat `156 13`; ALL hunks at old `:184-203` (`@@ -184 +184 @@` … `@@ -199,4 +326,20 @@`), i.e. above the earliest cited line `:923` | ✅ |
| M4 | `$VQP/linemap.py` (per-citation re-location by unique line text) | `:923→:1066`, `:939→:1082`, `:961→:1104`, `:965→:1108`*, `:1129→:1272`, `:1139→:1282`*, `:1144→:1287`, `:1145→:1288`, `:1146→:1289`, `:1153→:1296`, `:1278→:1421` — all `+143`. `*` = `:965`/`:1139` are a bare `)` occurring **7×** at HEAD, so OFFSET-DERIVED and confirmed to carry the same text; the prover exits 1 if the offset target text disagrees (rc 0 observed) | ✅ |
| M5 | `$PY .planning/quick/260916-kht-*/260916-kht-verify.py [--live]` | DEFAULT `RESULT GREEN checks=317 parsed=88 table=88 verified=88` rc 0 — before AND after. `--live` **BEFORE** `RESULT RED 31/318 … verified=64` rc 1; **AFTER** `RESULT RED 38/318 … verified=58` rc 1 | ⚠ **FINDING — see §5.1** |
| M6 | `git diff --numstat bf16289 HEAD -- condition_ld_matrix.py write_conditioned_ld_npz.py plink_ld_to_npz.py occlusion_span_filter.py src/R/ld_npz_to_rds.R` | `37 0` clm; `29 0` wcn; the other three report NOTHING = still 0-diff | ✅ |
| M7 | `git diff -U0 48b8828^ HEAD -- <f> \| grep '^@@'` | clm `@@ -2,0 +3,31 @@` and `@@ -124,0 +156,6 @@`; wcn `@@ -3,0 +4,28 @@` and `@@ -85,0 +114 @@` → clm **+31 for old 3-124, +37 from old 125**; wcn **+28 for old 4-85, +29 from old 86** | ✅ |
| M8 | python substring scan (NOT grep) of both modules for `:35`,`:37`,`:39` | tokens appear in **NEITHER** module; `condition_ld_matrix.py:19-21` names the retained rules BY CONTENT; `write_conditioned_ld_npz.py` names them not at all | ✅ |
| M9 | `sed -n '147p' …ocb-VERIFICATION.md`; `sed -n '33p' …oyq-VERIFICATION.md` | ocb: "**checked from the executor's artefacts, not re-run** … I parsed `…/m3-{before,after}.xml` myself by node id", 1187→1212/33, +25. oyq: "I parsed the executor's JUnit files myself … POST `suite_post.xml`: 1262 ids = **1229 passed / 33 skipped** … **ADDED 17**, REMOVED 0, CHANGED 0". **Suite NOT re-run by this task.** | ✅ |
| M10 | `sed -n '398p' .planning/quick/260812-ox1-*/260812-ox1-AGENT-PROMPT.md` | `nohup timeout 312h python3 src/python/run_native_ld_panel.py --manifest … --mode square --ancestry AFR > …` — **no `--fail-fast`** | ✅ |
| M11 | `grep -cE '08-17\|gate-released\|260817' .planning/osf_deviations.md`; `wc -l`; section map | **0** hits; **1022** lines; trsx5 section `## ` at `:133`, `### ` sub-entries at `:190` / `:254`, the ONLY bare `---` in `:133`-`:421` is at **`:344`**, and `:326` is the "None of (1)-(6) has been actioned" line | ✅ |
| M12 | `grep -n 'trsx5-gate-released' .planning/DECISIONS.md`; `wc -l` | `DEC-2026-08-17-trsx5-gate-released` at **`:2030`**; file **2538** lines; last entry at `:2413`; entries separated by a blank line (no `---` rule) — I matched that shape | ✅ |
| M13 | `wc -c` + `md5sum` on the in-repo posted body; `git show 3684413:…260814-u9p-seth-lineage-9907.txt \| wc -c \| md5sum` | posted **9695 B** / `c19be8b2ad7cd6a45fee1d668d8a9cf9`; lineage **9907 B** / `425d925a88ab474ec2396cbea25e665c` | ✅ |
| M14 | `sed -n '108,120p' ocb-PLAN.md`; `sed -n '38,46p' ocb-SUMMARY.md`; `grep -n '11264\|4352'` | PLAN`:112` 3.11 floor = spawner LIFETIME high-water, VmHWM **523060 KiB** (VmRSS 11400), trivial child read **523060 KiB**; PLAN`:113` 3.9 fork floor = spawner CURRENT RSS, `/usr/bin/true` read **413992 KiB**; PLAN`:115` first tiny child **106.8 MiB** (VmHWM 109504); PLAN`:118` `.bim` **20,767,864** lines; PLAN`:121`/`:203` launcher floor **11264 / 4352 KiB**; SUMMARY`:44` NC01 RED **A2 362.59 / A3 362.92 MiB**; SUMMARY`:41`-`:42` post-fix **307.96 → 11.00** and **11.25** MiB | ✅ (note the banked order is **3.11 first**, as B10 says) |
| M15 | `grep -n 'Small launcher process' .planning/quick/260916-ocb-*/*.md` | verbatim `Small launcher process (Recommended)` at `ocb-PLAN.md:14`, `:97`, `ocb-SUMMARY.md:8`, `:70`, `ocb-VERIFICATION.md:15` | ✅ |
| M16 | `$VQP/astdiff2.py` (ast.parse + recursive docstring strip + `ast.dump(include_attributes=False)` per top-level node) | **CHANGED = `['_run_plink']`; ADDED = `['_PLINK_PEAK_RSS_LAUNCHER']`**; top-level node count 59 → 60; the `if __name__` block's dump is **byte-identical** (`A[58]==B[59]` → True) and differs only in its positional key | ✅ |
| M17 | `grep -icE 'peak.?ram\|peak.?rss\|ru_maxrss\|maxrss\|\bRAM\b\|resident set' <each>` | posted trsx5 body **0**; mk7ze amendment **0**; tcujq amendment **0**; trsx5 project copy **0**; `.planning/amendments/AOU-LD-PIPELINE.md` **3** at `:471`/`:488`/`:492` = "~1.6 TB worker RAM", "`n1-highmem-16` … RAM-bound", "fit in one cluster's worth of RAM" — **cluster-sizing prose, not a measurement contract**. I wrote the NARROW claim. | ✅ |
| M18 | `grep -n 'def test_\|BENCHMARK_TSV' tests/m3/test_sparse_parent_benchmark.py` | writer = `test_no_whole_parent_dense_materialization` (`:54`-`:138`, `BENCHMARK_TSV.write_text(header + line)` at `:138`); `test_sparse_parent_benchmark_records_metrics` at `:141` READS only (`:145`-`:148`) | ✅ |
| M19 | the V8 python scan of `tests/**/*.py` | exactly **3** hits, all prose: `tests/m3/source_freeze.py:40`, `tests/m3/test_source_freeze_pins.py:98`, `:188` → **no test run required** | ✅ |
| M20 | `json.dumps(json.load(HANDOFF), indent=2, ensure_ascii=True).encode() == raw` | **True**; **59** top-level keys; **no trailing newline** | ✅ |
| M21 | `md5sum` + `wc -lc` on the LIVE source AND the banked copy, at copy time | source = copy = `3afb70fc3551cc86ae9c6fa9794eea29`, **213 lines / 25,784 B**; `codex-review.md` = `fce1c52d53308ebffb00031714436193`, **28 lines / 5,256 B** (both sides) | ✅ (source had not moved again since revision 1) |
| M22 | `awk` count of `^[0-9]+\. ` items under `### B2.` in the BANKED file | **7** | ✅ |
| extra | `git show 0231cbf:<f> \| wc -l` vs `git show HEAD:<f> \| wc -l` | clm **212 → 249**, wcn **111 → 140**; deltas `+37`/`+29` agree with `git diff --numstat 0231cbf HEAD` (`37 0`, `29 0`) → `260916-oyq-VERIFICATION.md:26`'s `213→250` / `112→141` are off by one | reported, not fixed |
| extra | `sed -n '156,162p' src/python/condition_ld_matrix.py` | `:159`-`:160` = "…the withdrawal: trsx5 / retains the fully-NaN-row drop rule that this raise directs." — confirmed the exact lines cited in the DEC entry | ✅ |
| extra | `grep -n 'def check_peak_ram' src/python/fire_verifier.py` | `:733` (the review's `:735` is its docstring line; I cited the measured `:733`) | narrowed |

**`.planning/STATE.md` was never read whole** (1,087,011 B). It was read with `sed -n '1,100p'`,
verified-unique anchors, and python substring scans, exactly as the plan and orchestrator required.
Likewise `HANDOFF.json` — only the named fields were printed.

---

## 4. Verification results V1-V9 (all run AFTER the last commit)

| ID | Check | Result |
|----|-------|--------|
| **V1** | `python3 -c "import json;json.load(open('.planning/HANDOFF.json'))"` | **PASS** — "V1 OK" |
| **V2** | `$VQP/handoff_check.py` | **PASS rc 0** — `RESULT GREEN handoff_check all assertions passed`. PRE 59 keys → POST 61; `set(PRE) <= set(POST)`; every PRE array kept its length; `CHANGED = {carter_decisions_outstanding, freeze_state, headline, repo_fixes_status, resume_entry_point, resume_on_reconnect, suite_baselines, timestamp}` ⊆ declared; `ADDED = {headline_PRIOR_2026_09_16, timestamp_reason_2026_09_16_blast_radius}` EXACTLY; `REMOVED = {}`; changed element indices exactly `resume_on_reconnect [1,2,3]`, `carter_decisions_outstanding [0]`, `repo_fixes_status [2]`; `POST['headline_PRIOR_2026_09_16'] == PRE['headline']`; every other changed string CONTAINS its PRE text; round-trip **byte-identical**; no trailing newline |
| **V3** | `$VQP/state_check.py` | **PASS rc 0** — all 13 PRESERVED PRE lines survive verbatim (incl. the `:78` regression guard); PRE `last_activity` scalar body (8,962 chars) survives verbatim; **13 `-` lines, every one a declared touched PRE line** (deleted PRE numbers `[7,17,26,39,40,48,49,55,57,59,82,88,89]`; `:15` produced **no** `-` line, allowed); line 1 is `---` and a closing `---` exists (PRE `:24` → POST `:25`, **not pinned**); frontmatter key list unchanged and in order; parse parity `('ParserError', "expected <block end>, but found '<scalar>'")` **identical PRE vs POST**, mark still on `last_activity:` in BOTH (line/col `15/4421` → `16/6309`, **deliberately not pinned**); `"` count in the `last_activity` line unchanged at **4**; `DEC-2026-09-16-ram1-launcher-measurement` 0 → **3**; `260916-BLAST-RADIUS-c93e97b-to-621701c` 0 → **3**; **no** line matches `^\| *260916-vqp *\|` |
| **V3b** | plan's own frontmatter fences | **PASS rc 0** — `bare --- at [1, 100]` |
| **V4** | insertion-only prover on all 7 appended/inserted files + numstat | **PASS** — rc 0 on all 7; numstat deletions column **0** for all 7 (`86 0`, `49 0`, `35 0`, `14 0`, `25 0`, `13 0`, `20 0`) |
| **V5** | banked files byte-identical | **PASS** — `cmp -s` rc 0 both; md5 **equal source-vs-copy** on both (`3afb70fc…`, `fce1c52d…`); sizes equal (213/25,784 and 28/5,256). **No banked-by header was added to either file.** No literal digest from the plan was asserted (M21 live source). |
| **V6** | frozen / forbidden paths | **PASS** — `git status --porcelain -uno -- $FROZEN` EMPTY; `git diff --numstat 621701c HEAD -- $FROZEN` EMPTY; `git diff --name-only 621701c HEAD` = **exactly 11** paths. (Confirmed there is no top-level `workflow/` dir: `ls -d workflow` → No such file. Snakemake lives in `src/snakemake/` + `./Snakefile`, both in the frozen set.) |
| **V7** | kht verifier before/after | **DEFAULT: PASS** — `RESULT GREEN checks=317 parsed=88 table=88 verified=88` rc 0, before AND after. **`--live`: MISMATCH vs the plan's expected string — see FINDING §5.1.** Before `RESULT RED 31/318 … verified=64` rc 1; after `RESULT RED 38/318 … verified=58` rc 1. Still RED, still rc 1, and deliberately NOT "fixed". |
| **V8** | no test reads these records | **PASS rc 0** — exactly 3 hits, all prose: `tests/m3/source_freeze.py:40`, `tests/m3/test_source_freeze_pins.py:98`, `:188`. **No suite run performed.** |
| **V9** | post-commit guard | **PASS** — `git log --oneline -5` shows exactly `3f418df / 5a2b437 / f8f30e3` on top of `621701c / 48b8828`; all 3 carry the Co-Authored-By trailer; `git status --porcelain -uno` EMPTY; **not pushed** (`origin` still `621701c`). |

### Negative controls — every one OBSERVED, pasted verbatim

Prover self-tests (before any repo write):
```
--- smoke A1: unmodified file must FAIL rc1 ---
FAIL .planning/DECISIONS.md: len(post)=203326 <= len(pre)=203326 -- an insertion-only change must GROW the file
rc=1
--- smoke A3: reword-last-line-then-append must FAIL rc1 ---
FAIL /…/gap.md: the last non-empty PRE line is not a WHOLE LINE of POST: b'enforcer").'
rc=1
--- smoke positive: pure append must PASS rc0 ---
OK insertion-only /…/pos.md vs 621701c:.planning/DECISIONS.md -- prefix_k=203326 inserted_bytes=10 tail_bytes=0
rc=0
```
The A3 smoke reproduces the plan-checker's KNOWN GAP (reword the last pre-existing line, then
append) and shows the third assertion closing it — **as a whole-line test, not a substring test**.

Insertion-only NCs (single pre-existing byte mutated in a scratch copy, mutation PROVEN to have
moved the bytes, length unchanged):
```
  mutated line 5 col 1: b'tags: [ram-1' -> b'uags: [ram-1'
FAIL …/nc2_t1_1.md: suffix mismatch -- post does not end with pre[119:] (35885 bytes). NOT insertion-only.   rc=1
  mutated line 5 col 1: b'score: 9/9 m' -> b'tcore: 9/9 m'
FAIL …/nc2_t1_2.md: suffix mismatch -- post does not end with pre[74:] (18237 bytes). NOT insertion-only.    rc=1
  mutated line 5 col 1: b'tags: [tcujq' -> b'uags: [tcujq'
FAIL …/nc2_t1_3.md: suffix mismatch -- post does not end with pre[115:] (14357 bytes). NOT insertion-only.   rc=1
  mutated line 5 col 1: b'task: null' -> b'uask: null'
FAIL …/nc2_t2_1.md: suffix mismatch -- post does not end with pre[60:] (176875 bytes). NOT insertion-only.   rc=1
  mutated line 5 col 3: b'> after Stage ' -> b'> bfter Stage '
FAIL …/nc2_t2_2.md: suffix mismatch -- post does not end with pre[295:] (16026 bytes). NOT insertion-only.   rc=1
  mutated line 6 col 5: b'## Clarification' -> b'## Cmarification'
FAIL …/nc2_t2_3.md: suffix mismatch -- post does not end with pre[211:] (78933 bytes). NOT insertion-only.   rc=1   (.planning/osf_deviations.md)
  mutated line 5 col 2: b'Carter and fu' -> b'Cbrter and fu'
FAIL …/nc2_t2_4.md: suffix mismatch -- post does not end with pre[167:] (203159 bytes). NOT insertion-only.  rc=1   (.planning/DECISIONS.md)
```

HANDOFF NCs:
```
NC-H1 (one pre-existing key 'freeze_state' DELETED):      RESULT RED  2 failure(s)   rc=1
NC-H2 (PRE sentence 'Fix with Popen + os.wait4.' removed from resume_on_reconnect[2]):
      FAIL: resume_on_reconnect[2]: PRE text is not a substring of POST
      RESULT RED  1 failure(s)   rc=1
```

STATE NCs:
```
NC-S1 (touched PRE line :26 text removed):
      FAIL: PRE line :26 no longer present verbatim: '> **NOTE:** the `status` / `stopped_at` …'
      RESULT RED  1 failure(s)   rc=1
NC-S2 (the :78 REGRESSION-GUARD line removed — it is never edited):
      FAIL: PRE line :78 no longer present verbatim: '  - ⚠ **The banked Stage C options draft cites …'
      RESULT RED  1 failure(s)   rc=1
NC-S3 (a 260916-vqp quick-ledger TABLE ROW appended):
      FAIL: a 260916-vqp quick-ledger TABLE ROW exists at lines [3438] -- that row is the orchestrator's
      RESULT RED  1 failure(s)   rc=1
```

---

## 5. FINDINGS

### 5.1 ⚠ PRIMARY FINDING — the `osf_deviations.md` insertion shifts every citation at or after `:344` by **+35**, and that moved 7 `kht --live` checks from PASS to RED

**Measured, not inferred.** `.planning/osf_deviations.md` went **1022 → 1057** lines; the new
sub-entry was inserted before the section-closing `---` at `:344` (exactly where the plan directed),
so **every line from old `:344` onward is now at `+35`**. Confirmed on a specific citation:

```
PRE  621701c :670-671  = "- ⛔ **NO PREDICATE CHANGE.** Extending to offset -1 … calibrate-to-pass at n=1."
POST        :670-671  = "  significance." / "- **Permutation confirmation:** …"      <-- a stale citation now reads the wrong text
POST        :705-706  = "- ⛔ **NO PREDICATE CHANGE.** …"                            <-- where it actually moved to
```

`kht --live` therefore went `RESULT RED 31/318 … verified=64` → `RESULT RED 38/318 … verified=58`.
**The whole delta is those 7 checks and nothing else** (`diff` of the two 326-line outputs shows
only these 8 changed lines):

```
RED  c:c25   `.planning/osf_deviations.md:657-663`  missing ['m2_region_00149', 'offset -1', 'single survivor']
RED  c:c70   `osf_deviations.md:703-704`            missing ['no covering record for EITHER member']
RED  c:n03   `osf_deviations.md:660-663`            missing ['single survivor', '21-region scan']
RED  c:c76   `osf_deviations.md:685-689`            missing ['to be pre-registered IF AND WHEN this disclosure is posted, …']
RED  c:c77   `:682`                                 missing ['Production tests the rate on BOTH sides']
RED  c:c78   `osf_deviations.md:670-671`            missing ['NO PREDICATE CHANGE … calibrate-to-pass at n=1']
RED  c-hand:H3  OD line 532 is not a `## ` heading
```

**Why this is NOT a correctness failure, and what it IS:**
- **DEFAULT mode is unchanged and still GREEN** (`RESULT GREEN checks=317 parsed=88 table=88
  verified=88`, rc 0) — the banked Stage C draft's citations are read at BASIS `c93e97b`, where
  `osf_deviations.md` is untouched by this task. The draft is not invalidated.
- `--live` was ALREADY deliberately RED and explicitly "not to be fixed". It is still RED and still
  rc 1. **I did not re-pin the draft's basis to a moving HEAD** (the plan forbids it), and I did not
  edit the kht verifier (frozen).
- But the plan's V7 asserts the `--live` string is identical "before and after". **That assertion
  is now false**, and I am reporting it rather than adjusting anything.

**What the orchestrator / downstream tasks must know** (this is the actionable part — it is the
same failure class as B9's wrong "+31 / +28"):

| Record | Cites | Now at |
|--------|-------|--------|
| `260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md:65` | `osf_deviations.md:657` | `:692` |
| `…-DRAFT.md:150` | `:703` | `:738` |
| `…-DRAFT.md:168` | `:660` | `:695` |
| `…-DRAFT.md:182` | `:685` | `:720` |
| `…-DRAFT.md:191` | `:670` | `:705` |
| `.planning/STATE.md:46` (was `:45` pre-insert; **not in this task's scope list**) | `:685-689` | `:720-724` |

`260916-vqq` (Stage C draft v2) should carry this: v2's `osf_deviations.md` citations must either be
re-based to `+35`, or stated as read at basis `c93e97b`. Citations **below `:344`** (e.g. the
findings file's `osf_deviations.md:104`/`:155`/`:190-192`/`:254`/`:325`) are **unaffected**.

**I deliberately did not "fix" this here.** Fixing it would mean (a) editing the frozen Stage C
draft, (b) editing the frozen kht verifier, or (c) adding an unplanned 4th commit / unplanned
STATE.md content — all three are out of scope, and (c) would break the plan's "exactly three
commits" pin and V9. Recorded for Carter's / the orchestrator's decision.

### 5.2 The wall-clock date at execution is **2026-09-17**, not 2026-09-16

`date -u` = `Thu Sep 17 04:20:11 AM UTC 2026`; `TZ=America/New_York date` = `Thu Sep 17 12:20:11 AM
EDT 2026`. The session rolled past midnight **in both zones**. Consequences, both deliberate:
- Every **prose** label is `2026-09-16` exactly as the plan mandates (`## ⚠ AS-OF CORRECTION
  2026-09-16`, `## ⚠ SUPERSEDED 2026-09-16`, `DEC-2026-09-16-…`, `headline_PRIOR_2026_09_16`,
  `⚠ CORRECTED 2026-09-16`). These are load-bearing: `must_haves`, V3 and **`260916-vqq`'s
  pre-flight** all key on them, and they name the work-session date of the reviewed material.
- The two **measured** timestamps are the real clock: `HANDOFF.timestamp = 2026-09-17T04:20:01Z` and
  `STATE.md:7 last_updated = "2026-09-17T04:20:00.000Z"`. The plan said "the executor's measured
  `date -u`" / "current UTC", so I wrote the truth rather than back-dating.
- So `STATE.md`'s `last_updated` (2026-09-17) and its `last_activity` prefix (`2026-09-16
  (LATEST)`) differ by one calendar day **by design**. Flagging it so no future reader reads it as
  drift.

### 5.3 My first negative-control attempt produced a FALSE GREEN, and the assertion caught it

The first NC mutator edited "line 5" only if it found a lowercase byte there. On
`.planning/osf_deviations.md` line 5 is blank, so it **silently no-op'd**, the file was unchanged,
and the prover returned **rc 0** — a green I had not seen fail. The `[ $rc -eq 1 ] || exit 1` guard
fired. I rewrote the mutator to (i) scan forward for the first mutable line, (ii) `assert out != b`,
and (iii) `assert len(out) == len(b)`, then **re-ran ALL SEVEN** NCs (Task 1's included) under the
proven mutator; all seven observed rc 1. Directly on point for
`[[feedback_green_assertion_needs_a_negative_control]]`.

### 5.4 Smaller measured disagreements

1. **`<input_errata>` item 1 confirmed independently.** The findings file's own `⚠ CORRECTED
   2026-09-16 23:08` at `:143` already says `:78`, not `:76`. I wrote `:78` in STATE.md's `:57`
   correction prose.
2. **`<input_errata>` item 2 confirmed.** A/B3's broad "no posted text mentions peak RAM" is false
   for `.planning/amendments/AOU-LD-PIPELINE.md:471/:488/:492`. The narrow M17 claim is what I wrote
   into the DEC entry, with the nuance stated explicitly.
3. **`260916-oyq-VERIFICATION.md:26` off-by-one confirmed:** `213→250` / `112→141` written;
   `wc -l` gives **212→249** / **111→140**. Deltas `+37`/`+29` are correct. Reported in the
   appended note in `260916-oyq-SUMMARY.md`; the VERIFICATION file itself was **not** edited
   (frozen for this task).
4. **`fire_verifier.check_peak_ram` is at `:733`**, not the review's `:735` (that is its docstring
   line). I cited the measured `:733`.
5. **`DECISIONS.md` entry separator:** the immediately preceding entry is separated by a blank line,
   **not** a `---` rule. I dropped the `---` from my draft to match the house shape — this also
   avoids adding a bare `---` that could confuse the gsd-tools frontmatter extractor (C-ter).
6. **M4's two non-unique lines:** `:965` and `:1139` are a bare `)` occurring **7×** at HEAD. Their
   HEAD numbers are offset-derived and the prover confirms the offset target carries the same text.
   Said so in `STATE.md:49`'s appended clause, and never worded as "the file shifted uniformly".
7. **M21 did not move again** — the live findings source read the revision-1 digest at copy time.

**No GPFS `invalid object` / `Error building trees` occurred at any point.**
**No tool-hook timeouts occurred**; Read/Write/Edit and heredoc/python writers all worked.

---

## 6. OPEN — named, unresolved, and belonging elsewhere

- **B2** — the Stage C options draft (v1) is not courier-ready: **7** MEDIUM findings (§B2 of the
  banked file, count re-derived). Needs a **v2**, or a v1 courier with the basis caveat →
  `260916-vqq`. ⚠ **Add §5.1's `+35` `osf_deviations.md` shift to v2's scope.**
- **B3 / B5** — `peak_ram_gib` is now plink-only; pre- and post-fix values are indistinguishable in
  the bucket panel TSV → next Stage C fire / COST-1.
- **B4 / B6 / B7 / B11 / B14** — fire-shell preconditions (`python3 -V`, SIGCHLD bit, `_run_plink`
  smoke), the SIGHUP form-B decision, the `BROWSER-PASTE.md:386` "either way" claim, the runbook
  operational notes, and `READY-TO-FIRE.md:5-8`'s stale "src unchanged" → **`260916-vqr`** (the
  `260812-ox1` runbooks and `.claude/skills/**` were FORBIDDEN here and are untouched).
- **B10 residue, report-only:** the blanket freeze prose in `tests/m3/test_source_freeze_pins.py:15`
  and `tests/m3/source_freeze.py:9-10` ("Correcting a wrong comment in a frozen file therefore costs
  **nothing**") is still false for `plink_ld_to_npz.py` and `occlusion_span_filter.py` — touches
  `tests/`, forbidden here.
- **`260916-oyq-VERIFICATION.md:26`** — off-by-one line counts; deltas agree; reported, not fixed.
- **`condition_ld_matrix.py:159-160`** — the function-docstring nuance (in production the retained
  fully-NaN-row drop rule is carried out by `--mac 1` + the raw NaN-raise, not by that module).
  Frozen file; recorded as one line in the DEC entry's "Consequences recorded, not decided".
- **`STATE.md:62-63`** — orchestrator-probe values (413,932 / 522,748 KiB) vs the banked planner
  values (`ocb-PLAN.md:112` = 523,060 / `:113` = 413,992 KiB); the labelling is still ambiguous. Not
  in this task's scope list.
- **`STATE.md:2223-2226`** — the four "(prior) … (latest)" lines. Not in scope.
- **The `260916-vqp` quick-ledger row in STATE.md** — deliberately NOT written by me; it needs the
  close-out sha and the verifier result and belongs to the orchestrator's close-out (V3 asserts no
  such row exists).
- **Push** — not done. The orchestrator decides. (Memory rule: push NCSU before any AoU clone fire.)

---

## Self-Check

Created files:
```
FOUND: .planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md
FOUND: .planning/debug/260916-BLAST-RADIUS-codex-review-as-received.md
```
Commits: `f8f30e3`, `5a2b437`, `3f418df` all FOUND in `git log` on `m3-W2-aou-deltas`; tracked tree
clean; `git diff --name-only 621701c HEAD` = exactly the 11 declared paths; frozen/forbidden paths
untouched (status + numstat both empty).

## Self-Check: PASSED
