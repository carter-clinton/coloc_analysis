---
phase: quick-260916-vqr
plan: 01
subsystem: m3-aou-afr-ld-panel-build / the Stage C fire surface
tags: [runbook, stage-c, sighup, sigchld, ram-1, blast-radius, doc-only]
requires: [quick-260916-vqp, quick-260916-vqq]
provides: ["STEP 9d / §9d fire-shell preconditions", "fire command form B at both sites", "plink-only peak_ram_gib reading rule", "B14 ancestry gate", "B11 launcher operational notes", "SKILL invariant 3 scoping"]
affects: [".planning/quick/260812-ox1-*/", ".claude/skills/aou-ld-pipeline/SKILL.md"]
tech-stack:
  added: []
  patterns: ["behaviour-pinned extractor instead of a grep count", "ancestry property instead of a SHA pin", "bit verdict instead of a whole-mask EXPECT"]
key-files:
  created: []
  modified:
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
    - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
    - .claude/skills/aou-ld-pipeline/SKILL.md
decisions:
  - "Command form B (`timeout 312h nohup python3 …`) adopted at both command sites; setsid rejected (it would break `$!`)"
  - "The SIGCHLD EXPECT is the 0x10000 BIT only — a whole-mask EXPECT would false-STOP the interactive fire shell"
  - "B14 stated as a `git merge-base --is-ancestor` property, not as a SHA the document cannot keep current about itself"
  - "deferred-items.md deliberately NOT touched (DECISION-1) — a cosmetic edit on a live-gated file"
metrics:
  duration: ~75 min
  tasks: 3
  files: 4
  completed: 2026-09-17
commit: 3da858f
basis_PRE: 480feae
---

# quick-260916-vqr: Stage C fire preconditions in the runbooks — Summary

Closed the six next-Stage-C-fire findings of the 2026-09-16 blast-radius review
**inside the fire surface itself** — B4 (fire-shell preconditions), B6 (the false
SIGHUP claim + command form B), B3/B5 (plink-only `peak_ram_gib`), B7 ("either
way"), B14 (stale clone target), B11 (launcher operational notes) — with every
EXPECT re-derived by measurement on this node and every enforcer proven
AFTER == BEFORE. **Doc/runbook only. Nothing under `src/`, `tests/`, `config/`,
`workflow/` or `bin/`. Nothing fired, no network, no cloud.**

**Commit:** `3da858f` — 4 files, **549 insertions, 21 deletions**. Not pushed.

---

## 1. Pre-flight (Task 1)

| item | measured |
|---|---|
| branch | `m3-W2-aou-deltas` (never `main`) |
| `PRE` (HEAD at start) | `480feae53d6cfa367dc116b41e808e9466a7e006` |
| tracked tree | clean (`git status --porcelain --untracked-files=no` → empty) |
| vqq close-out in ancestry | `480feae` — `merge-base --is-ancestor` rc 0 ✅ |
| vqp close-out in ancestry | `74f962d` — `merge-base --is-ancestor` rc 0 ✅ |
| concurrent runner | none — one project session (`--resume=bd0cb7c3`), no second skill-runner |
| node | `Linux 5.14.0-687.42.1.el9_8.x86_64`, `timeout (GNU coreutils) 8.32`, `GNU bash 5.1.8(1)-release` |
| interpreters | system `python3` = 3.9.25 (**no pandas**); `PY` = `/rs1/…/smoke_dev/bin/python3` = 3.11.15 |

⚠ The system `python3` here fails `import run_native_ld_panel` with
`ModuleNotFoundError: No module named 'pandas'` — an **unrelated local** reason.
That is recorded so it is never mistaken for a VM finding.

---

## 2. Every measurement, verbatim

### 2a. SIGHUP A/B (M1/M2/M3/M4) — `$SCRATCH/sighup_ab.out`

Pidfile-based (never `pgrep -f`, which self-matches the probing shell), `set -m`,
zombie-aware liveness (an unreaped zombie counts DEAD).

```
=== env ===
Linux 5.14.0-687.42.1.el9_8.x86_64 x86_64
timeout (GNU coreutils) 8.32
GNU bash, version 5.1.8(1)-release (x86_64-redhat-linux-gnu)
Python 3.9.25

formA: $!=2589541 comm=timeout  child=2589544 comm=python3
formA: pre-HUP launcher=ALIVE child=ALIVE
[formA] after SIGHUP to $!: launcher=DEAD child=DEAD
[formA] after SIGHUP to -$! (process group): launcher=DEAD child=DEAD
formB: $!=2589600 comm=timeout  child=2589602 comm=python3
formB: pre-HUP launcher=ALIVE child=ALIVE
[formB] after SIGHUP to $!: launcher=ALIVE child=ALIVE
[formB] after SIGHUP to -$! (process group): launcher=ALIVE child=ALIVE

[control-expiry formA] rc=124 child=DEAD
[control-expiry formB] rc=124 child=DEAD

[control-M3 formB] t=+1s after HUP (cap 6s): launcher=ALIVE child=ALIVE
[control-M3 formB] t=+9s after HUP (past the 6s cap): launcher=DEAD child=DEAD
```

- **M1 reproduced.** form A's child DEAD beside form B's child ALIVE — the
  negative control that makes form B's green mean something.
- **M2 reproduced.** `rc=124`, child DEAD, under **both** forms: the 312h backstop
  still bites.
- **M3 reproduced.** Under form B the wall-cap **survives the SIGHUP** and still
  fires. Form B does not trade the backstop for survival.
- **M4 reproduced.** `ps -o comm= -p $!` printed `timeout` under **both** forms,
  so `echo "fire PID: $!"` keeps its meaning and teardown guidance is unchanged.

### 2b. M5 — the fire log's shape (measured under a REAL tty, which the round-0 probe was not)

```
stdin is a tty? YES
--- jcA.log (form A) ---
nohup: ignoring input
HELLO-FROM-CHILD
--- jcB.log (form B) ---
nohup: ignoring input
HELLO-FROM-CHILD
nohup.out in cwd? NO
monitor grep -cE 'VERIFY-FAILED|^ERROR' on jcA/jcB: 0 / 0
```

Form-**independent**; not an error; does not match the monitor regex; no
`nohup.out` in the cwd because the shell's `> …fire.log 2>&1` already owns stdout.
⚠ Without a tty the line is absent under both forms — so the claim is scoped to
"whenever this terminal has job control", which is the VM terminal case.

### 2c. M6/M7/M8 — the smoke through the shipped seam (`$SCRATCH/smoke.out`)

```
--- _run_plink(['true']) x2 ---
(0.000678245226542155, 0.0107421875)
(0.0006255944569905599, 0.010986328125)
--- _run_plink(['plink1.9','--version']) with NO plink1.9 on PATH (signature 1) ---
FileNotFoundError: [Errno 2] No such file or directory: 'plink1.9'
--- NEGATIVE CONTROL: SIGCHLD=SIG_IGN inherited (signature 2) ---
ChildProcessError: [Errno 10] No child processes
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "…/src/python/run_native_ld_panel.py", line 336, in _run_plink
    raise subprocess.SubprocessError(
subprocess.SubprocessError: plink peak-RSS launcher exited 0 without a valid report; refusing to fabricate wall_min/peak_ram_gib for ['true']
```

**The `SubprocessError` negative control was SEEN RED before any "EXPECT a tuple"
was written into a runbook.** The shipped bound quoted from the test, not from the
plan: `tests/m3/test_run_plink_peak_rss.py:98` `_BIAS_CEIL_MIB = 24.0`, asserted by
`test_launcher_bias_is_bounded` ("A6: bare `true` reads < 24 MiB").

### 2d. M16 / R-6(ii) — the HAPPY path, measured with a **real** PLINK 1.9

⚠ The plan's M16 said "no plink on this node". **That is FALSE** — a real PLINK
1.9 lives at `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink`. I
symlinked it as `plink1.9` and ran the runbook's exact one-liner:

```
PLINK v1.9.0-b.8 64-bit (22 Oct 2024)
(0.0009279330571492513, 0.0107421875)
   ^ run 1 rc=0
PLINK v1.9.0-b.8 64-bit (22 Oct 2024)
(0.0008142232894897461, 0.0107421875)
   ^ run 2 rc=0
PLINK v1.9.0-b.8 64-bit (22 Oct 2024)
(0.0008147239685058593, 0.0107421875)
   ^ run 3 rc=0

=== plink --version own exit status (direct, no launcher) ===
PLINK v1.9.0-b.8 64-bit (22 Oct 2024)
direct rc=0

=== stand-in banner (v1.90b7.2 text, exit 0) ===
PLINK v1.90b7.2 64-bit (11 Dec 2023)
(0.0007155776023864746, 0.0107421875)

=== 4th signature: plink RAN and returned non-zero (exit 3) ===
subprocess.CalledProcessError: Command '['plinkfail']' returned non-zero exit status 3.
```

**TWO lines on the happy path** (banner on the inherited fd 1, then the tuple),
stable ×3, rc 0. Wall time **33–56 ms** (0.00056–0.00093 min) — *tens of
milliseconds*, not "~a second". ⚠ Per R-6(ii) the runbook EXPECT is written as a
**SHAPE** ("plink's version banner line, then the tuple"), never a version string:
the VM's pinned **v1.90b7.2** prints a different banner and **its own `--version`
exit status remains genuinely UNMEASURED** (this node has 1.9.0-b.8, a different
build).

### 2e. M9 / W-2 — the SIGCHLD detector in **all four** cells (`$SCRATCH/sigchld.out`)

```
bash -c  (non-interactive) | parent=SIG_DFL | SigIgn=0000000000000000 | bit 0x10000 clear | GREEN
bash -c  (non-interactive) | parent=SIG_IGN | SigIgn=0000000000010000 | bit 0x10000 set | RED (SIGCHLD ignored)
bash -ic (INTERACTIVE)     | parent=SIG_DFL | SigIgn=0000000000380000 | bit 0x10000 clear | GREEN   [stderr: bash: no job control in this shell]
bash -ic (INTERACTIVE)     | parent=SIG_IGN | SigIgn=0000000000390000 | bit 0x10000 set | RED (SIGCHLD ignored)
```

All four reproduce M9 exactly. `0x380000` = bits 19/20/21 =
`SIGTSTP`/`SIGTTIN`/`SIGTTOU` — normal for an interactive shell. **A whole-mask
EXPECT of `0000000000000000` would FALSE-STOP the real (interactive) fire shell**,
so the shipped pass condition is the `0x10000` bit alone.

### 2f. M10 — does `timeout` neutralise an inherited `SIGCHLD=SIG_IGN`? (parent = `SIG_IGN`)

```
bare python3                      | SigIgn=0000000001011000 | bit 0x10000 = True
nohup python3                     | SigIgn=0000000001011001 | bit 0x10000 = True
timeout 5 python3                 | SigIgn=0000000001001000 | bit 0x10000 = False
timeout 5 nohup python3 (form B)  | SigIgn=0000000001001001 | bit 0x10000 = False
nohup timeout 5 python3 (form A)  | SigIgn=0000000001001000 | bit 0x10000 = False
```

Verdicts identical to M10. **Note the masks themselves differ from 2e** (this
parent is python, which ignores `SIGPIPE` 0x1000 and `SIGXFSZ` 0x1000000; `nohup`
adds `SIGHUP` 0x1) — a second, independent demonstration that **only the bit may
ever be an EXPECT**. Consequence written into the runbooks: on coreutils 8.32 the
Stage C command is additionally shielded, while Stage A (STEP 8), Stage B (STEP 9)
and every bare `python3 src/python/…` run — **including the three
`fire_verifier.py` gates** — are not, and the VM's coreutils version is unmeasured.

### 2g. M11 — `-I` / `LC_CTYPE`, re-derived (python 3.11.15, `LANG=C`)

| mode | `PYTHONCOERCECLOCALE` | child's `LC_CTYPE` |
|---|---|---|
| plain | unset | `'C.UTF-8'` |
| `-I -S` | unset | `'C.UTF-8'` |
| plain | `0` | `None` |
| **`-I -S`** | **`0`** | **`'C.UTF-8'`** |

M11 confirmed and narrower than the brief: the launcher changes plink's env
**only** in the `LANG=C` **and** `PYTHONCOERCECLOCALE=0` cell (isolated mode
implies `-E`, so the opt-out is ignored).

### 2h. M12 — the B14 counts, with their scope

Scope: `git diff --name-only 5284505 HEAD -- src tests config Snakefile workflow`,
at `PRE = 480feae`, 2026-09-16.

```
      9 src/python
     10 tests/m3
--- total --- 19
--- config + Snakefile + workflow --- 0
RAM-1-present (9a3eb97)
tcujq-present (48b8828)
```

**Reconciled: 9 + 10 = 19.** The header's `config/` / `Snakefile` half was still
TRUE; the `src/` / `tests/` half was FALSE. ⚠ **Drift vs the plan:** the planner
measured `origin == HEAD, 0 ahead` at planning time; **at my pre-flight HEAD was 9
ahead of `origin/m3-W2-aou-deltas` (`621701c`)** — vqp + vqq landed in between.
This strengthens rather than weakens item 1's "push NCSU first" gate, and it is
exactly why B14 is stated as an ancestry property rather than a SHA.

### 2i. M13 — the driver's dense in-process load (a FLOOR)

```
n_var=102,421  4*n_var^2 = 41,960,244,964 bytes = 39.0785 GiB  (39.08)
n_var=120,000  4*n_var^2 = 57,600,000,000 bytes = 53.6442 GiB  (53.64)
```

`fire_verifier.py:111 _VM_TOTAL_GIB = 120.0`, `:114 _DEFAULT_HEADROOM_FRAC = 0.15`
→ 102.0 GiB. `plink_ld_to_npz._has_any_nan_blocked(m, block=1024)` keeps the scans
blocked; `content_verify_npz` (cited **by symbol**) re-loads the banked array.

### 2j. M15 — the extractor, RED on the pre-edit tree (the control it ships with)

```
site counts: [1, 1, 0]
distinct normalized strings: 1
all startswith form B? False   <-- MUST BE False PRE-EDIT
any startswith nohup? True   <-- MUST BE True PRE-EDIT
tails equal across the 2 sites? True
literal 'nohup timeout' count across the 3 runbooks PRE-EDIT: 2   (AP 1, BP 1, RF 0)
```

---

## 3. What was written (Task 2 — all eight edits)

| edit | where | what |
|---|---|---|
| 1 (B4+B6) | AP `STEP 9d` (new, before `STEP 10 `), BP `## 9d` (new, before `## 10`) | WHY (launcher never ran for real; FIRST-ROW-WINS cited by symbol) + 4 checks: smoke (primary, two-line EXPECT, 4 signatures), `python3 -V` ≥ 3.9, SIGCHLD **bit** verdict, the SIGHUP A/B property check with form A's death as its negative control and an expiry control |
| 2 (B6) | AP STEP 10, BP §10 (commands); AP/BP/RF (the three false sentences) | `nohup timeout 312h` → **`timeout 312h nohup`** at both sites, everything after `python3` byte-unchanged; the three claims corrected **in place and marked retired**, never deleted |
| 3 (B6) | `SKILL.md` invariant 3 | ADDITIVE dated scoping sub-bullet (Dataproc master-side only; not a warrant for the VM fire) — **0 deleted lines** |
| 4 (B3/B5) | AP STEP 9-GATE, BP §9b, RF item 10 | the plink-only reading rule + the driver-term FLOOR + the four pre-fix rows quarantined |
| 5 (B7) | BP §9b | "…land in the panel TSV **regardless of outcome**" replaced by the measured truth (both stay `None`) — and the literal `either way` is **gone from BP** |
| 6 (B14) | RF header + item 1 | retired clause replaced by the measured counts; clone target as an ancestry property |
| **6b** (B14) | **AP STEP 1** | the two `merge-base --is-ancestor` lines in the RUN block — *the half that actually runs* |
| 7 (B11) | AP STEP 10 monitoring, BP §9c | the three operational notes, each with its measured scope |

Plus the **key_link** the plan required: an explicit same-shell pointer from AP
STEP 3's `export PATH` to STEP 9d.

### The `nohup timeout` count — the EXACT DERIVED N, never 0

```
  260812-ox1-AGENT-PROMPT.md: 2
      :545  nohup timeout 40 python3 /tmp/hupchild.py /tmp/pidA > /tmp/hupA.log 2>&1 &     <- A/B probe
      :590  `nohup timeout 312h python3 …`. THAT WAS FALSE, and it is retired rather        <- retired-form prose
  260812-ox1-BROWSER-PASTE.md: 2
      :705  nohup timeout 40 python3 /tmp/hupchild.py /tmp/pidA > /tmp/hupA.log 2>&1 &     <- A/B probe
      :762  A, `nohup timeout 312h python3 …`. **That was false**, and it is retired rather  <- retired-form prose
  260812-ox1-READY-TO-FIRE.md: 1
      :364  previously committed form A (`nohup timeout 312h python3 …`) does **NOT** survive a
  N = 5
```

**N = 5 = 2 A/B probe blocks + 3 retired-form prose sites**, exactly as derived
before the edits. A `== 0` gate would have been unsatisfiable (B-1).

### Edit-site list, final line numbers (post-edit)

AP: STEP 1 `:63`, STEP 3 pointer `:97`, STEP 9-GATE rule `:335`+, **STEP 9d `:440`**,
STEP 10 `:579`, fire command `:585`, B11 notes at end of file.
BP: §9b B7 `:386`+, §9b B3/B5 after the stage-b gate, §9c note 6, **§9d**,
§10 command `:~742`.
RF: header `:5`+, item 1 ancestry gate `:33`+, item 10 form-B prose `:330`+,
item 10 B3/B5 rule after the mechanical-gates paragraph.

---

## 4. Enforcers — AFTER == BEFORE (Task 3b)

Exit codes measured **outside a pipe** (`cmd >file 2>&1; echo "exit=$?"`), the
`exit=` line kept out of `E{n}.txt` per R-3.

| # | enforcer | BEFORE (re-captured at pre-flight) | AFTER | verdict |
|---|---|---|---|---|
| E1 | vbu `all` | exit **0** · `RESULT: ALL CHECKS PASSED (section: all)` | exit **0** · identical | ✅ |
| E2 | guk `fire` | exit **1** · `RESULT: FAILURES PRESENT (section: fire)` · F3 ×3, F8 ×9 | exit **1** · identical · F3 ×3, F8 ×9 · **normalised fail set IDENTICAL** | ✅ |
| E3 | 09a `--only skill` | exit **0** · `PASS SKILL-01 no historical row deleted; …` | exit **0** · identical | ✅ |
| E4 | 09a `--only claims` | exit **1** · `FAIL CLAIM-02` · 7 mismatches | exit **1** · **byte-identical mismatch line**; no new file | ✅ |
| E5 | pairwise R6 pytest | `1 passed` | `1 passed` | ✅ |
| E6 | kht **DEFAULT** | exit **0** · `RESULT GREEN checks=317 parsed=88 table=88 verified=88` | exit **0** · identical to the **pre-flight capture** | ✅ |

⚠ **E2's raw F3 lines moved, exactly as B-2 predicted a comparison must tolerate:**

```
BEFORE: FAIL  F3 [260812-ox1-AGENT-PROMPT.md:155] …
        FAIL  F3 [260812-ox1-BROWSER-PASTE.md:141] …
        FAIL  F3 [260812-ox1-READY-TO-FIRE.md:154] …
AFTER:  FAIL  F3 [260812-ox1-AGENT-PROMPT.md:172] …
        FAIL  F3 [260812-ox1-BROWSER-PASTE.md:141] …
        FAIL  F3 [260812-ox1-READY-TO-FIRE.md:185] …
```

**Finding vs the plan:** the plan predicted only **RF's** F3 line would move.
**AP's moved too** (`:155` → `:172`) — the STEP 3 same-shell pointer at `:97` sits
above AP's advisory hash. BP's did not move (`:141` → `:141`), because every BP
edit is below it. A raw-string comparison would have false-STOPped on *two* files,
not one. The line-number-normalised set (`sed -E 's/\.md:[0-9]+\]/.md]/' | sort`,
**`sort`, not `sort -u`**, so a new F3 in the same file still changes the multiset)
is **identical**, and `diff` returned clean.

**F8 stayed RED at exactly 9 (AGENT-PROMPT ×5, READY-TO-FIRE ×4)** — that is
correct and required. Its missing tokens are the **WITHDRAWN** single-condition
ceilings; a *disappearing* F8 would have been the stop. Guardrail check on the
final tree, inside the AP F8 block (`STAGE C HOLD LIFTED` → `^STEP 10 `, 172
lines, which now contains all of STEP 9d):

```
  '0.0005' -> 0     '60.0' -> 0     '51.2' -> 0     'Seth' -> 0     102,?421 -> 0
```

All five NO-WRITE tokens absent, as required. (This is why STEP 9d attributes its
measurements to "quick-260916-vqr" and never by name, and why the wall time is
given in **milliseconds** — the decimal form `0.00056` would have contained the
banned literal `0.0005` and silently turned an F8 green.)

F9's AP cost block still carries `COST-PER-BANKABLE-REGION` (1 hit); F10's two
patterns are 0 file-wide in all three runbooks.

### E6 — the mechanism, PROVEN from the verifier's own reader (not assumed)

`260916-kht-verify.py:321` `class Reader`, `raw()`:

```python
from_tree = bool(self.live and not at_basis and rel != PATHS["ST"])
...
if from_tree:  self._cache[key] = (ROOT / rel).read_bytes()
else:          r = git("show", "%s:%s" % (BASIS, rel))
```

In DEFAULT mode `self.live` is `False`, so `from_tree` is **always** `False` and
every *cited* file is resolved with `git show c93e97b:<path>` (`BASIS = "c93e97b"`,
`:58`). **A working-tree edit to a cited file therefore cannot move the default
result** — proven, not asserted. Separately (W-5) the **banked draft** is read from
the working tree (`:1493` / `--draft` default `ROOT / BANKED_REL`, `:73` = the **v1**
draft, which vqq froze byte-identical), which is why the baseline had to be
vqq-relative.

### kht `--live` citation drift — recorded for the orchestrator, NOT fixed

I measured the BEFORE myself rather than trusting a supplied number, using a
`git clone --shared` of the repo at `480feae` **outside** the working tree:

```
PRE  tree : RESULT RED 38/318 parsed=88 table=88 verified=58    (0 ox1-runbook REDs)
HEAD tree : RESULT RED 47/318 parsed=88 table=88 verified=49    (9 ox1-runbook REDs)
```

**Reconciled both ways: 38 + 9 = 47 and 58 − 9 = 49.** The nine, with their new
line numbers:

| check | citation (PRE) | now at |
|---|---|---|
| c01 | `AGENT-PROMPT.md:398` (the fire command) | **AP:585** |
| c02 | `AP:372-373` (`without --fail-fast`) | **AP:419** |
| c03 | `AP:417` (`without --fail-fast`) | **AP:623** |
| c18 | `AP:422-423` (`STOP under R8`) | **AP:628** |
| c63 | `AP:424-428` (`a real, reportable outcome`) | **AP:633** |
| n02 | `AP:393` (`~11 days`) | **AP:579** |
| c04 | `READY-TO-FIRE.md:360-366` | **RF:423** |
| c62 | `RF:360-366` (`a real, reportable outcome`) | **RF:423** |
| n06 | `RF:369-370` (`120000`, `--max-n-var`) | **RF:431** |

⚠ The plan also listed `AP:55-61` as expected to drift. **It did not** — it is
still GREEN, because `R8.` is at `:55` both before and after (my first AP edit is
at `:63`). Nine, not ten. **Changing the banked draft is vqq's job; BASIS was not
re-pinned, the verifier was not edited, the draft was not touched.**

### vqq's verifier (orchestrator-flagged, read-only)

```
PRE  clone : RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112   exit 0
HEAD tree  : RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112   exit 0
```

**No drift at all** — it cites at BASIS `74f962d`, so working-tree edits do not
reach it, and draft v2 is untouched.

---

## 5. The fire-command identity proof (Task 3a) and its negative controls

```
OK fire_cmd_assert: 2 sites (AP 1 / BP 1 / RF 0), equal, form B,
tail == PRE(480feae); nohup-timeout N=5
{'260812-ox1-AGENT-PROMPT.md': 2, '260812-ox1-BROWSER-PASTE.md': 2, '260812-ox1-READY-TO-FIRE.md': 1}
```

All five assertions hold: (1) exactly 2 sites, **RF 0** (it states no command —
its `contains: "timeout 312h nohup"` is satisfied deliberately **in prose**);
(2) the two normalized strings exactly equal; (3) both start
`timeout 312h nohup python3 src/python/run_native_ld_panel.py`; (4) none start
`nohup`; (5) **the tail after `python3` is byte-identical to the same extraction
from `git show 480feae:<file>`** — the swap provably moved only two words.

**Three observed reds** (a green assertion needs a negative control):

| control | observed |
|---|---|
| the pre-edit tree (free, M15) | `all startswith form B? False` |
| mutation 1 — swap the two words back | `AssertionError: ('A3 not form B', [...])` · **measured rc=1** |
| mutation 2 — drop BP's command site | `AssertionError: ('A1 site counts', {... 'BROWSER-PASTE.md': [], ...})` · **measured rc=1** |

Per **R-1**, the script that Task 3's `<automated>` runs (`$SCRATCH/fire_cmd_assert.py`)
was **created** — it reuses Task 2's python body verbatim and adds assertion 5.
Without it `set -e` would have killed Task 3 on its first command.

---

## 6. Diff hygiene (Task 3c)

```
1	0	.claude/skills/aou-ld-pipeline/SKILL.md
236	7	…/260812-ox1-AGENT-PROMPT.md
242	7	…/260812-ox1-BROWSER-PASTE.md
70	7	…/260812-ox1-READY-TO-FIRE.md
```

- Exactly **four** files. `git diff --name-only 480feae | grep -E '^(src|tests|config|workflow|bin)/'` → **empty**.
- No `.planning/amendments/`, `osf_deviations.md`, `HANDOFF.json`, `DECISIONS.md`,
  `STATE.md`, `deferred-items.md`, banked draft (v1 or v2) or any verifier touched.
- **SKILL.md: 1 insertion, 0 deletions** — additive, as required by E3.
- **The 21 deleted runbook lines are all accounted for**: the two command-site
  lines being swapped; the three false "nohup survives disconnects" sentences; the
  false "land in the panel TSV either way" parenthetical; the false `.planning`-only
  header clause; and four lines re-emitted verbatim as part of an in-place
  correction (AP STEP 1's EXPECT, AP's "accepted. On his explicit go, RUN:" and
  "Check-ins every 2-3 days…"). Nothing historical was deleted.
- Tracked tree clean after the commit; **not pushed** (10 commits ahead of
  `origin/m3-W2-aou-deltas`).

---

## 7. Deviations from plan

### Auto-fixed / applied under the addendum

**1. [R-1] `fire_cmd_assert.py` created.** Task 3's `<automated>` ran a script the
plan never created. Written to `$SCRATCH/fire_cmd_assert.py`, reusing Task 2's
body verbatim plus assertion 5. Applied.

**2. [R-2] Probe output contracts honoured.** `sighup_ab.out` emits one line per
case in exactly `[formA] after SIGHUP to $!: launcher=… child=…`; `smoke.out`
carries the `SubprocessError`; `sigchld.out` carries all four whole-mask values —
so Task 1's gate greps could not false-RED.

**3. [R-3] `grep '^RESULT' … | tail -1`** used in both E6 comparisons, and the
`exit=` lines were written to `preflight.txt`, never into `E{n}.txt`.

**4. [R-4] The unenforced invariant made enforced.** The claimed "no `<automated>`
block contains an escaped quote" assertion did not exist. **Measured:** 3
`<automated>` blocks, **count of `\"` across them = 0 → GREEN**. It is now a
measurement in this record rather than a belief.

**5. [R-5] Both round-0 promises pinned and green:**
`"merge-base --is-ancestor 9a3eb97" in ap and "…48b8828" in ap` ✅ and
`"2026-09-16" in SKILL.md` ✅ (pre-edit count of `2026-09-16` in SKILL.md was **0**,
so that gate had a real control).

**6. [R-6] (i)** both vqp and vqq ancestry gates enforced; **(ii)** the real PLINK
binary used, and the runbook EXPECT written as a **shape**, not a version string;
**(iii)** `nothing scientific is lost` added to the F10 assertion (both patterns
now 0); **(iv)** noted in §4.

### Findings (re-run wins over the anchor)

**7. [FINDING] M16's "(no plink on this node)" is FALSE.** A real PLINK 1.9 is at
`/rs1/…/hlp_crossmap/bin/plink` (banner `PLINK v1.9.0-b.8 64-bit (22 Oct 2024)`,
`--version` rc **0**, stable ×3). The pinned **v1.90b7.2**'s exit status is still
unmeasured — a *different build* — so the runbook still refuses to promise exit 0.

**8. [FINDING] The guk F3 drift is wider than the plan predicted.** AP's F3 line
moved as well as RF's (§4). The normalised comparison absorbed it; a byte-for-byte
one would have false-STOPped twice.

**9. [FINDING] `origin` is 9 commits behind HEAD at pre-flight** (plan measured 0).
Recorded; it makes item 1's push-first gate load-bearing rather than ceremonial.

**10. [FINDING] The kht `--live` drift is 9 citations, not the 10 the plan listed**
— `AP:55-61` did not move. Reconciled arithmetically both ways (§4).

**11. [FINDING] M5 needed a tty to reproduce.** Under `set -m` *without* a
terminal on stdin the `nohup: ignoring input` line is **absent under both forms**.
Re-measured under a real pty; the runbook claim is scoped to "whenever this
terminal has job control".

**12. [FINDING] M10's masks differ from M9's** (python parent ignores `SIGPIPE` /
`SIGXFSZ`; `nohup` adds `SIGHUP`) while the bit verdicts match exactly — a second,
independent reason the EXPECT must be the bit and never the mask.

### Deliberate non-actions

- **DECISION-1 honoured:** `deferred-items.md` NOT touched (it is gated by the live
  `R4-COVERAGE` enforcer; the B3/B5 rule went where it is acted on instead).
- **No third command site** added to READY-TO-FIRE (I-2/M15): its
  `contains: "timeout 312h nohup"` is met in prose.
- **Nothing "fixed"** in guk F8, the kht BASIS, the banked drafts or any verifier.

### Style note

AGENT-PROMPT had **0** fenced code blocks pre-edit (house style = 2-space indents).
The plan's GUARDRAILS require triple-backtick fences on every code paste, so the new
STEP 9d blocks are fenced. This is enforcer-neutral (verified) and protects the
underscores in `_run_plink` / `sys.path` when the prompt is pasted into a chat.

---

## 8. Success criteria

| criterion | status |
|---|---|
| An agent can prove the launcher works end-to-end, SIGCHLD is clean and the fire survives a disconnect **on this VM's coreutils**, in under a minute at $0, each with a measured EXPECT and an explicit STOP | ✅ STEP 9d / §9d, four checks |
| Every site that states the fire command states form B, identically | ✅ 2/2, normalized-equal, tail identical to `PRE` |
| Stage-B RAM read as plink-only, driver term separate, four pre-fix rows quarantined | ✅ all three reading sites |
| Clone target is a checkable property, not a stale claim | ✅ AP STEP 1 **and** RF item 1 |
| Six enforcers exactly as green (and exactly as red) as before | ✅ §4 |

## Self-Check: PASSED

- All four modified files exist and are in commit `3da858f` (verified with
  `git diff --name-only HEAD~1 HEAD`).
- Commit `3da858f` exists in `git log`; tracked tree clean afterwards; not pushed.
- No file under `src/`, `tests/`, `config/`, `workflow/` or `bin/` appears in the
  commit.

## Known Stubs

None. No placeholder, empty-value or TODO construct was introduced; every EXPECT
in the new runbook text traces to a measurement recorded verbatim above.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern or schema change —
this task is doc/runbook text only. T-vqr-01 … T-vqr-07 were all mitigated as
planned (see §4, §5, §6).

---

## ORCHESTRATOR CORRECTION (appended 2026-09-17 at close-out, after the independent verifier)

**G-1 — STEP 9d check 4 left the fire shell in `/tmp`. FIXED in a follow-up commit.**
The check opened with `cd /tmp && cat > hupchild.py …` and never returned, while the block's own
headline says "RUN ALL FOUR IN THE SAME SHELL THAT WILL FIRE" and the very next step fires with
RELATIVE paths (`src/python/run_native_ld_panel.py`, `config/ld_regions.tsv`). Measured by the
verifier from a non-repo cwd: `python3: can't open file '<cwd>/src/python/run_native_ld_panel.py'`
goes into the fire log while `echo "fire PID: $!"` **still prints a PID** — the fire reads as
launched and the fault would surface only at a 2-3 day check-in. Re-running check 1 afterwards
gives `ModuleNotFoundError`, which the block's own signature list routes to "interpreter or
environment → go to check 2" — the wrong branch for a cwd fault.

**Fix applied to both AGENT-PROMPT and BROWSER-PASTE:** `REPO=$PWD` before the `cd /tmp`, and
`cd "$REPO" && pwd` as the last line of the probe. The EXPECT block now reads "these three
propositions, in this order, followed by the repo path", carries the `/tmp` STOP condition, and
scopes the line count (bash interleaves its own `Hangup`/`Killed` job notices — the verifier
observed both). Re-checked after the edit: the five F8 NO-WRITE tokens are still 0 inside the AP
block (now 182 lines), and the guk normalised fail set is **byte-identical before vs after**
(F3=3, F8=9), with vbu 0 / 09a-skill 0 / 09a-claims 1 unchanged.

**Recorded, not fixed (verifier's minor observation 2):** this SUMMARY's `--live` drift table row
`c63` gives `AP:633`; the range start is `AP:630` (the phrase falls at `:633-634`). Every other row
uses the range start.
