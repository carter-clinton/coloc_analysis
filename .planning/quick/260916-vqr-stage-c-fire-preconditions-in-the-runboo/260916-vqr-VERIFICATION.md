---
phase: quick-260916-vqr
verified: 2026-09-17T06:30:00Z
status: gaps_found
score: 12/13 must-haves verified
overrides_applied: 0
gaps:
  - truth: "STEP 9d / §9d can be run in the shell that fires without breaking the step it immediately precedes"
    status: failed
    reason: >-
      Check 4's fenced block opens with `cd /tmp && cat > hupchild.py …` and never returns the
      shell to the clone. The same block's own headline requires all four checks to be run in
      "the SAME SHELL THAT WILL FIRE", and the next step (AGENT-PROMPT STEP 10 / BROWSER-PASTE
      §10) fires with RELATIVE paths (`src/python/run_native_ld_panel.py`,
      `--manifest config/ld_regions.tsv`). Followed literally, the fire command runs from /tmp and
      dies with `can't open file '/tmp/src/python/run_native_ld_panel.py': [Errno 2]` — into the
      redirected fire log, while `echo "fire PID: $!"` still prints a PID, so the agent can report
      the fire as launched. Re-running check 1 after check 4 additionally yields
      `ModuleNotFoundError: No module named 'run_native_ld_panel'`, which the block's own signature
      list routes to "interpreter or environment. Go to check 2" — a wrong diagnosis for a cwd
      problem. MEASURED 2026-09-17 by the verifier (both failure strings reproduced from a non-repo
      cwd); no `cd` back to `~/coloc_analysis` exists anywhere after AGENT-PROMPT:537 /
      BROWSER-PASTE:697.
    artifacts:
      - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
        issue: "STEP 9d check 4 (line 537) does `cd /tmp` with no return; STEP 10's fire command at :585 is cwd-relative"
      - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md"
        issue: "§9d check 4 (line 697) does `cd /tmp` with no return; §10's fire command is cwd-relative"
    missing:
      - "End check 4 with `cd ~/coloc_analysis` (and state the EXPECT `pwd` = the clone), or wrap the probe in a subshell `( cd /tmp && … )`, or write the probe files with absolute /tmp paths without ever cd-ing"
      - "Optionally: add `pwd` to STEP 10's pre-fire confirmation line so the cwd is asserted at the moment of the $385-1,084 command"
human_verification:
  - test: "Read STEP 9d check 4 as the in-perimeter agent would and confirm the cwd fix chosen by the planner is the one that survives a copy-paste of the whole block"
    expected: "After the block, `pwd` prints the clone root and STEP 10's relative-path command resolves"
    why_human: "Ergonomics of a paste-into-chat runbook — which of the three fixes is least likely to be dropped in transcription is a judgement call"
  - test: "Decide whether AGENT-PROMPT's new triple-backtick fences (0 pre-edit -> 12 post-edit) are acceptable in a file whose house style was 2-space indents"
    expected: "A style ruling; the fences are enforcer-neutral (measured) and protect the underscores in `_run_plink` / `sys.path` when pasted into chat"
    why_human: "House-style call for a paste-into-chat runbook; no mechanical check decides it"
---

# quick-260916-vqr: Stage C fire preconditions in the runbooks — Verification Report

**Task goal:** put the Stage C fire preconditions into the live fire runbooks — launcher smoke,
SIGCHLD bit check, `python3 -V`, SIGHUP command form B, plink-only RAM semantics, the
clone/ancestry gate and the operational notes — without breaking any of the six enforcers that
read those files.

**Verified:** 2026-09-17 · **Basis:** commit `3da858f` on `PRE = 480feae` · **Status:** gaps_found
**Method:** every enforcer, every EXPECT and the command-identity proof were **re-run by the
verifier**, not read from the SUMMARY. The BEFORE state was re-derived independently from a
`git clone --shared` checked out at `480feae` (never from the executor's capture files). Exit codes
were taken outside pipelines throughout. Nothing was fired; no network, no cloud; all probes ran
under `…/scratchpad/ver-vqr` and were deleted afterwards.

## Goal Achievement

### Observable truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Pre-flight ordering: vqq + vqp close-outs in `PRE`'s ancestry, tracked tree clean | ✓ VERIFIED | `PRE = 480feae` **is** the vqq close-out; `merge-base --is-ancestor 74f962d 480feae` rc 0 (vqp); `git status --porcelain -uno` empty before and after |
| 2 | The fire-shell block lets an agent prove, in ~10 s at $0, that the launcher runs end-to-end, `python3` ≥ 3.9 and SIGCHLD is not `SIG_IGN` — each with a measured EXPECT and a STOP | ✓ VERIFIED | All four signatures re-measured (below); `exitcode_of = os.waitstatus_to_exitcode  # bound BEFORE the spawn` at `run_native_ld_panel.py:194`; `_BIAS_CEIL_MIB = 24.0` at `tests/m3/test_run_plink_peak_rss.py:98` |
| 3 | The behaviour-pinned extractor finds EXACTLY 2 sites (AP 1, BP 1, RF 0), equal, both form B, tail == `git show 480feae:` | ✓ VERIFIED | Verifier's own re-implementation: A1 `[1,1,0]`, A2 one distinct string, A3 both `timeout 312h nohup python3 src/python/run_native_ld_panel.py`, A4 none start `nohup`, A5 tail 279 chars byte-identical to PRE |
| 4 | The literal `nohup timeout` count is an EXACT DERIVED N, never 0 | ✓ VERIFIED | N = 5 = AP 2 + BP 2 + RF 1 (2 A/B probe blocks + 3 retired-form prose sites) |
| 5 | The runbooks carry an in-perimeter SIGHUP property check that PROVES form B survives and form A does not, with its expected output and a STOP | ✓ VERIFIED | Check-4 block extracted and run **verbatim** (only paths redirected): `formA launcher=DEAD child=DEAD` / `formB launcher=ALIVE child=ALIVE` / `expiry rc=124` |
| 6 | `$!` still names `timeout` under form B; the fire log's shape is unchanged | ✓ VERIFIED | `ps -o comm= -p $!` = `timeout` under BOTH forms; `nohup: ignoring input` present under both forms with a pty on stdin, absent under both without one; 0 hits for `grep -cE 'VERIFY-FAILED\|^ERROR'`; no `nohup.out` in cwd |
| 7 | The Stage-B reading rule states `peak_ram_gib` is PLINK-ONLY, adds the driver's dense load separately as a FLOOR, and quarantines the four pre-fix rows | ✓ VERIFIED | 4·102,421² = 41,960,244,964 B = **39.0785 GiB**; 4·120,000² = **53.6442 GiB**; `_VM_TOTAL_GIB=120.0` × (1−0.15) = **102.0 GiB**; `read_square_bin` `np.fromfile` and `_has_any_nan_blocked(block=1024)` confirmed in source; rule present at all three reading sites |
| 8 | BROWSER-PASTE no longer claims wall/RAM land in the panel TSV "either way"; a plink failure leaves BOTH `None` | ✓ VERIFIED | `either way` 1 → 0 in BP; `run_native_ld_panel.py:1160-1162` assigns `result["wall_min"]` only AFTER `_run_plink` returns, initialised `None` at `:952/:963` |
| 9 | READY-TO-FIRE states the clone target as a mechanically checkable ancestry property, not a stale claim | ✓ VERIFIED | Header retired-clause replaced; re-derived at `PRE`: **9 `src/python` + 10 `tests/m3` = 19**, `config`+`Snakefile`+`workflow` = **0**; `9a3eb97` (RAM-1) and `48b8828` (tcujq) both ancestors of HEAD |
| 10 | The three B11 operational notes, each with its measured scope | ✓ VERIFIED | Reproduced behaviourally: `pgrep -f plink1.9` matched launcher (PID 2617108) + driver + **the probing shell**, lowest-PID hit ≠ plink; `pgrep -x plink1.9` matched only plink (2617109); SIGKILL of the launcher alone left plink reparented to PID 1 and running while the driver raised `SubprocessError`; LC_CTYPE table reproduced in all four cells |
| 11 | SKILL.md invariant 3 no longer reads as a warrant for the VM nohup fire; correction is ADDITIVE | ✓ VERIFIED | `git diff --numstat` = **1 insertion, 0 deletions**; `2026-09-16` count 0 (pre) → 1 (post) — the R-5 gate had a real control; 09a `--only skill` still `PASS SKILL-01`, exit 0 |
| 12 | AFTER == BEFORE for every one of the six enforcers | ✓ VERIFIED | Full table below; all six re-run by the verifier on both trees |
| 13 | STEP 9d / §9d can be run in the shell that fires without breaking the step it immediately precedes | ✗ FAILED | Check 4 does `cd /tmp` and never returns; STEP 10's command is cwd-relative. See **Gaps**. |

**Score: 12/13**

### Enforcers — BEFORE (independently re-derived at 480feae) vs AFTER (3da858f)

| # | Enforcer | BEFORE | AFTER | Verdict |
|---|----------|--------|-------|---------|
| E1 | vbu `all` | exit **0** · `RESULT: ALL CHECKS PASSED (section: all)` | exit **0** · identical | ✅ |
| E2 | guk `fire` | exit **1** · `RESULT: FAILURES PRESENT (section: fire)` · F3 ×3, F8 ×9 | exit **1** · identical · F3 ×3, F8 ×9 · normalised fail set `diff` clean (rc 0) | ✅ |
| E3 | 09a `--only skill` | exit **0** · `PASS SKILL-01`, 0 clause failures | exit **0** · identical | ✅ |
| E4 | 09a `--only claims` | exit **1** · `FAIL CLAIM-02`, 7 residual mismatches | exit **1** · mismatch line **byte-identical**; all 7 still in `STATE.md` / `HANDOFF.json` / `deferred-items.md`; no runbook, no SKILL.md | ✅ |
| E5 | pairwise R6 pytest | `1 passed` | `1 passed` | ✅ |
| E6 | kht **DEFAULT** | exit **0** · `RESULT GREEN checks=317 parsed=88 table=88 verified=88` | exit **0** · **identical** | ✅ |

**The F3 drift is WIDER than the plan predicted — confirmed.** Raw BEFORE→AFTER:
`AGENT-PROMPT.md:155 → :172`, `READY-TO-FIRE.md:154 → :185`, `BROWSER-PASTE.md:141 → :141`
(unmoved). A raw-string comparison returns rc 1 on **two** files; the line-number-normalised
comparison (`sed -E 's/\.md:[0-9]+\]/.md]/' | sort`, `sort` **not** `sort -u`) is clean. The
executor's finding stands.

### No withdrawn figure smuggled into a guarded block

F8 block bounds reproduced from the shipped `block()` awk in `260814-guk-verify.sh:110-112`
(start-inclusive, end-exclusive):

| Block | Lines | `0.0005` | `60.0` | `51.2` | `Seth` | `102,?421` |
|-------|-------|----------|--------|--------|--------|------------|
| AP `STAGE C HOLD LIFTED` → `^STEP 10 ` (contains all of STEP 9d) | 33 → **172** | 0 | 0 | 0 | 0 | 0 |
| RF `^\*\*Deferral vocabulary` → `^## 11\.` | 62 → 62 | 0 | 0 | 0 | **1** | 0 |

RF's single `Seth` is **pre-existing** — the RF F8 block is **byte-identical pre vs post**
(`diff` rc 0), and guk's BEFORE fail list already omits `Seth` for READY-TO-FIRE. F8 count is
exactly **9** (AP ×5, RF ×4) before and after; F9's `cost-per-bankable-region` and F10's two
patterns are unchanged. The near-miss is real: `0.0005` is a **prefix** of `0.00056`, so writing
the smoke's wall time in decimal minutes would have silently turned an F8 green; the shipped text
says **"measured 33-56 ms"** and the token count is 0.

### Every EXPECT re-measured (the load-bearing ones)

| EXPECT as written | Verifier's measurement | Verdict |
|---|---|---|
| form A child DEAD / form B child ALIVE after SIGHUP to `$!` | `formA launcher=DEAD child=DEAD`; `formB launcher=ALIVE child=ALIVE` (pidfile-based, `set -m`, zombie-aware) | ✓ |
| … and to the process group `-$!` | form A DEAD/DEAD; form B ALIVE/ALIVE | ✓ |
| expiry `rc=124` with the child dead | `rc=124 child=DEAD` under **both** forms | ✓ |
| the 312h cap still bites after a HUP (M3) | 6 s cap, HUP at t=2 s: t+1 s ALIVE/ALIVE, t+9 s DEAD/DEAD | ✓ |
| `ps -o comm= -p $!` = `timeout` | `timeout` under both forms | ✓ |
| smoke prints TWO lines (banner, then tuple) | real PLINK at `/rs1/…/conda_envs/hlp_crossmap/bin/plink` symlinked as `plink1.9`: `PLINK v1.9.0-b.8 64-bit (22 Oct 2024)` then `(0.00082…, 0.0107421875)`, rc 0, stable ×3 | ✓ |
| `peak_ram_gib` ≈ 11 MiB launcher floor, bounded < 24 MiB | 0.0107421875 / 0.010986328125 GiB = 11.0 / 11.25 MiB; `_BIAS_CEIL_MIB = 24.0` | ✓ |
| wall time "tens of milliseconds (33-56 ms)" | 0.00061-0.00093 min = 37-56 ms across 5 runs | ✓ |
| missing-binary signature | `FileNotFoundError: [Errno 2] No such file or directory: 'plink1.9'` | ✓ |
| SIGCHLD `SIG_IGN` signature | `subprocess.SubprocessError: plink peak-RSS launcher exited 0 without a valid report; refusing to fabricate wall_min/peak_ram_gib for ['true']` | ✓ |
| 4th signature | `subprocess.CalledProcessError: Command '['plinkfail']' returned non-zero exit status 3.` | ✓ |
| SigIgn `0000000000000000` (non-interactive) / `0000000000380000` (interactive) green; `…010000` / `…390000` red | **Re-measured with a real pty** (job control ON = the fire shell): the shipped one-liner printed `RESULT SigIgn=0000000000380000  SIGCHLD-OK` and `RESULT SigIgn=0000000000390000  STOP: SIGCHLD is SIG_IGN`. Without a tty the same one-liner reads `…000000` / `…010000`. **Both pairs differ only in bit 0x10000** → the shipped pass condition (the bit) is correct in both environments, and a whole-mask EXPECT of `0…0` WOULD have false-STOPped the real fire shell | ✓ |
| `timeout` neutralises an inherited `SIG_IGN` on 8.32 (M10) | bare `True`, `nohup` `True`; `timeout`, `timeout nohup`, `nohup timeout` all `False` | ✓ |
| driver dense load 39.08 GiB @ 102,421 / 53.64 GiB @ 120,000, gate 102.0 GiB | 39.0785 / 53.6442 / 102.0 | ✓ |
| `-I -S` + `PYTHONCOERCECLOCALE=0` is the only cell where the launcher changes plink's `LC_CTYPE` | 4-cell table reproduced exactly (`C.UTF-8` / `C.UTF-8` / `None` / `C.UTF-8`) | ✓ |

### The command moved only two words

Independent re-implementation of the DECISION-2 extractor (join `\`-continuations → keep lines
with BOTH `run_native_ld_panel.py` and `--manifest config/ld_regions.tsv` → whitespace-collapse):
2 sites (AP 1 / BP 1 / **RF 0**), one distinct normalised string (305 chars), both form B, none
starting `nohup`, tail after `python3` (279 chars) byte-identical to `git show 480feae:`.
`nohup timeout` count = **5**, never 0.

**Three observed REDs** (a green assertion needs a negative control):

| control | result |
|---|---|
| pre-edit tree (`preclone` @ 480feae) | `A3 FAILED: not form B` — both sites `nohup timeout 312h python3 …` |
| mutation 1 — swap the two words back at AP | AssertionError, **measured rc 1** (verifier's script *and* the executor's `fire_cmd_assert.py`) |
| mutation 2 — drop BP's command site | `A1 FAILED {AP:1, BP:0, RF:0}`, **measured rc 1** (both scripts) |

The executor's `$SCRATCH/fire_cmd_assert.py` exists, implements all five assertions plus the
marker/N gates, returns **rc 0** on the real tree and **rc 1** on both mutations.

### The executor's five findings

| # | Claim | Verdict |
|---|---|---|
| a | The guk F3 drift was WIDER than predicted — AP `:155→:172` as well as RF `:154→:185`, BP unmoved | ✓ **CONFIRMED** — raw diff shows exactly those two changed lines |
| b | A real PLINK 1.9 exists on this node; `--version` rc 0, banner `PLINK v1.9.0-b.8` | ✓ **CONFIRMED** at `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink` (direct rc 0) |
| c | kht `--live` drift is **9** citations, not 10; `AP:55-61` did not move; 38/318 verified=58 → 47/318 verified=49 | ✓ **CONFIRMED** — exactly 9 checks moved PASS→RED (`c01 c02 c03 c04 c18 c62 c63 n02 n06`); `c17`/`c-res:c17` (the `:55-61` citation) stayed PASS; `R8.` is at `:55` in both trees; 38+9=47 and 58−9=49 |
| d | `origin` was 9 commits behind HEAD at pre-flight | ✓ **CONFIRMED** — `origin/m3-W2-aou-deltas = 621701c`; `621701c..480feae` = 9, `..3da858f` = 10 |
| e | `nohup: ignoring input` needs a real tty; absent under both forms without one | ✓ **CONFIRMED** — with a pty on stdin both `tA.log` and `tB.log` begin `nohup: ignoring input`; without a tty neither does. (Strictly the condition is "stdin is a terminal", which the runbook renders as "whenever this terminal has job control" — equivalent for the VM terminal case.) |

### R-1 … R-7 (orchestrator addendum)

| Item | Verdict |
|---|---|
| R-1 `fire_cmd_assert.py` created and is what Task 3 runs | ✓ present, 3,859 B, runs green on the tree and red on both mutations |
| R-2 probe output contracts | ✓ `sighup_ab.out` carries `[formA] after SIGHUP to $!: launcher=DEAD child=DEAD` and the formB ALIVE twin; `smoke.out` carries `SubprocessError` ×2; `sigchld.out` carries all four whole masks |
| R-3 `grep '^RESULT' \| tail -1`; `exit=` kept out of `E{n}.txt` | ✓ no `E*.txt` contains `exit=`; `preflight.txt:31-36` carries all six exit codes; `E6-before/after.txt` are single `RESULT` lines |
| R-4 escaped-quote assertion now ENFORCED | ✓ measured on the PLAN: **3** `<automated>` blocks, `\"` count **0** |
| R-5 the two round-0 promises pinned | ✓ both `merge-base --is-ancestor 9a3eb97` and `… 48b8828` in AGENT-PROMPT STEP 1; `2026-09-16` in SKILL.md, pre-edit count **0** (real control) |
| R-6 (ii) smoke EXPECT written as a SHAPE, never a version string | ✓ the runbook prints `<plink's version banner line>` and adds "Do NOT expect a specific banner string, and do NOT assume exit 0" |
| R-6 (iii) F10 both patterns | ✓ `nothing is lost` = 0 and `nothing scientific is lost` = 0 file-wide across the three runbooks |
| R-7 the plan's gate is a real control that fails at the claimed point | ✓ reproduced: on the un-edited tree the assertions pass A1/A2 and fail at `startswith(form B)` with rc 1 |

### Style deviation (asked for explicitly)

AGENT-PROMPT had **0** `^```` fences pre-edit (house style = 2-space indents); post-edit it has
**12** (6 blocks). BROWSER-PASTE 46 → 58, READY-TO-FIRE 20 → 22 (those two already used fences).
**Enforcer-neutral — measured:** the literal ` ``` ` appears 0 times in `260814-guk-verify.sh`,
`260817-vbu-verify.sh`, `260812-09a-check-sweep.sh` and `260916-kht-verify.py`; the single hit in
`tests/m3/test_pairwise_completeness_scan.py` is at `:3188`, inside an unrelated docstring, and
the R6 test matches `^R6\.` … `^R7\.` only. **Verifier's opinion: acceptable, and preferable for
this file.** AGENT-PROMPT is pasted into a chat, where markdown strips `_` pairs — `_run_plink`,
`sys.path`, `_BIAS_CEIL_MIB` and `os.wait4` all appear in the new text, and an unfenced paste
would corrupt exactly the identifiers an agent must type. Raised as a house-style ruling for the
record, not as a defect.

## Gaps

**G-1 — the precondition block leaves the fire shell in `/tmp`.**

`AGENT-PROMPT.md:537` / `BROWSER-PASTE.md:697` open check 4 with `cd /tmp && cat > hupchild.py …`.
No `cd` back exists anywhere after that point in either file (the only other `cd`s are at AP
`:65`, `:105`, `:276`, all far above). The same block's headline is
"**RUN ALL FOUR IN THE SAME SHELL THAT WILL FIRE**", and the step it was inserted directly in
front of fires with relative paths:

```
timeout 312h nohup python3 src/python/run_native_ld_panel.py --manifest config/ld_regions.tsv …
  > /home/jupyter/native_ld_fire.log 2>&1 &
echo "fire PID: $!"
```

Measured consequences (reproduced by the verifier from a non-repo cwd):

* `python3: can't open file '<cwd>/src/python/run_native_ld_panel.py': [Errno 2] No such file or
  directory` — redirected into the fire log, while `echo "fire PID: $!"` still prints a PID. The
  loudest evidence is hidden in the log file the agent is told to check "every 2-3 days".
* Re-running check 1 after check 4 gives `ModuleNotFoundError: No module named
  'run_native_ld_panel'`, which the block's own signature list routes to *"interpreter or
  environment. Go to check 2"* — the wrong branch for a cwd fault.

Not a data-integrity hazard (the driver never starts, so no sticky FIRST-ROW-WINS error rows are
written), but it can burn a fire window on an 11-day, $385-1,084 unattended run and invite a
re-fire. One line fixes it — see the frontmatter `missing:` list.

## Observations (not gaps)

* **"EXPECT, exactly these three lines"** — running check 4 verbatim, bash also emits job-status
  notices (`… Hangup  nohup timeout 40 python3 …`, `… Killed  timeout 40 nohup python3 …`)
  interleaved with the three EXPECT lines. The STOP rule immediately below is correctly scoped to
  three propositions (both survive / both die / expiry ≠ 124), so the decision is safe; the word
  "exactly" is the only loose part. A five-word note ("plus the shell's own job notices") would
  close it.
* **kht `--live` drift table, row c63.** The SUMMARY reports the drifted citation `AP:424-428` as
  now at `AP:633`; the range start is **`AP:630`** (`Liveness = the .npz count CLIMBING …`), with
  the phrase *a real, reportable outcome* at `:633-634`. Every other row uses the range-start
  convention (`c02 → :419`, `c18 → :628`, `c04/c62 → RF:423`, `n06 → RF:431` — all confirmed).
  Informational only: the drift record is for vqq to re-pin, and the load-bearing claims (9 not
  10, `AP:55-61` unmoved, 38+9=47 / 58−9=49) are all exact.

## Diff hygiene

`git diff --numstat 480feae 3da858f` = exactly 4 files, **+549 / −21**
(SKILL 1/0, AP 236/7, BP 242/7, RF 70/7). `git diff --name-only | grep -E '^(src|tests|config|workflow|bin)/'`
is empty (rc 1). No `.planning/amendments/`, `osf_deviations.md`, `HANDOFF.json`, `DECISIONS.md`,
`STATE.md`, `deferred-items.md`, banked draft or verifier was touched. Tracked tree clean; commit
carries the `Co-Authored-By: Claude Opus 5` trailer; **not pushed** (10 ahead of `origin`).

---

_Verified: 2026-09-17 · Verifier: Claude (gsd-verifier). All probes ran under
`…/scratchpad/ver-vqr` and were deleted; no processes left; no network, no cloud, nothing fired._
