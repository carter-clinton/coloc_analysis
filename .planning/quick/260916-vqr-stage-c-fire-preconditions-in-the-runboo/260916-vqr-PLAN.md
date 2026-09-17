---
phase: quick-260916-vqr
plan: 01
type: execute
wave: 1
depends_on: []            # ordering is ENFORCED in Task 1 pre-flight: quick-260916-vqp (records) and quick-260916-vqq (Stage C draft v2) must ALREADY be committed
mode: quick-full
branch: m3-W2-aou-deltas
worktree: none            # GPFS: worktrees disabled project-wide. Scratch CLONES (git clone --shared) live OUTSIDE the repo.
autonomous: true
push: false               # commit only; the orchestrator commits PLAN/SUMMARY/VERIFICATION/STATE afterwards
requirements: ["BLAST-B3", "BLAST-B4", "BLAST-B5", "BLAST-B6", "BLAST-B7", "BLAST-B11", "BLAST-B14"]
revision: 1

# RUNBOOK/DOC ONLY. No code, no tests, no config, no workflow.
files_modified:
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md   # B4 (new STEP 9d) + B6 + B3/B5 + B11 + B14
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md  # B4 (new §9d) + B6 + B7 + B3/B5 + B11 + B14
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md  # B14 (header + item 1) + B6 + B4 pointer + B3/B5 (item 10)
  - .claude/skills/aou-ld-pipeline/SKILL.md                                                          # B6 invariant 3 scoping (ADDITIVE ONLY)
  - .planning/quick/260916-vqr-stage-c-fire-preconditions-in-the-runboo/260916-vqr-SUMMARY.md        # CREATED, NOT committed by the executor

files_frozen:
  - src/**                     # FORBIDDEN by scope. No code change is authorized by this task.
  - tests/**                   # FORBIDDEN. tests/m3/test_pairwise_completeness_scan.py READS the AGENT-PROMPT — never edit the test to fit an edit.
  - config/**, workflow/**, bin/**, Snakefile
  - .planning/amendments/**    # posted OSF bodies, NEVER edited
  - .planning/osf_deviations.md
  - .planning/HANDOFF.json
  - .planning/DECISIONS.md
  - .planning/STATE.md         # the ORCHESTRATOR updates STATE.md
  - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT*.md   # the banked Stage C draft(s) — owned by vqq
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/**   # the draft's verifier
  - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/**  # the trsx5 card enforcer
  - .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/**  # the superseded-card enforcer
  - .planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/**  # the SKILL/record sweep harness
  - .planning/quick/260812-ox1-*/260812-ox1-{PLAN,CONTEXT,SUMMARY,VERIFICATION}.md, *-evidence.*     # ox1 task records, not the fire surface
  - .planning/quick/260812-ox1-*/260819-PENDING-PASTE-step5-substitute-and-reboot.md                 # a 4th file in the ox1 dir; NOT one of the three runbooks
  - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md   # see DECISION-1 below: deliberately NOT touched
  - everything else not listed in files_modified

must_haves:
  truths:
    - "Pre-flight passes ONLY when: the tracked tree is clean, vqq's close-out commit is present at HEAD's ancestry, and the BEFORE state of all six enforcers is captured verbatim to the scratchpad before any edit"
    - "A reader of the fire shell block can, in ~10 seconds and at $0, determine that python3 is >= 3.9, that the launcher runs end-to-end and returns a (wall_min, peak_ram_gib) tuple with a small non-zero peak, and that SIGCHLD is not inherited as SIG_IGN — each with an EXPECT derived by measurement and a STOP on anything else"
    - "The behaviour-pinned extractor (DECISION-2: join backslash continuations, keep lines with BOTH run_native_ld_panel.py and --manifest config/ld_regions.tsv, whitespace-collapse) finds EXACTLY 2 sites (AGENT-PROMPT, BROWSER-PASTE; 0 in READY-TO-FIRE), both exactly equal, both starting `timeout 312h nohup python3 src/python/run_native_ld_panel.py`, none starting `nohup`, and the tail after `python3` equal to the same extraction from PRE"
    - "A literal `nohup timeout` count is asserted as an EXACT DERIVED NUMBER N (the A/B probe block + the retired-form prose), never as 0 — a 0-gate is unsatisfiable because both of those must quote form A"
    - "The runbooks carry an in-perimeter SIGHUP property check that PROVES form B survives and form A does not on the VM's own coreutils, with its expected output and a STOP if it does not reproduce"
    - "`$!` still names the timeout process under form B (so `echo \"fire PID: $!\"` keeps its meaning) and the fire log's shape is unchanged — both stated from measurement, not assumption"
    - "The Stage-B gate reading rule states that peak_ram_gib is PLINK-ONLY, that the driver's own in-process dense load is NOT in that column and must be added separately, and that the four pre-fix rows (00001 30.6591, 00017 2.9689, 00040__sub14 26.5745, 00057 26.5745) are not plink-only measurements and must not be mixed with post-fix ones"
    - "BROWSER-PASTE no longer claims wall_min / peak_ram_gib land in the panel TSV 'either way'; it states that a plink failure leaves BOTH None"
    - "READY-TO-FIRE no longer claims post-5284505 commits are `.planning`-only; the clone/pull requirement is stated as a mechanically checkable ancestry property, not as a SHA the document cannot name for itself"
    - "The runbooks carry the three B11 operational notes (launcher-only SIGKILL/OOM orphans plink; `pgrep -x plink1.9`, not `-f`; `-I` can add LC_CTYPE to plink's env) each with its measured scope"
    - "SKILL.md invariant 3 no longer reads as a warrant for the Cloud Analysis VM nohup fire; the correction is ADDITIVE (zero deleted sentences)"
    - "AFTER == BEFORE for every enforcer, compared against the PRE-FLIGHT capture: vbu all-green (exit 0); guk `fire` RESULT: FAILURES PRESENT at **exit 1** with the LINE-NUMBER-NORMALISED fail set unchanged plus F3 count == 3 and F8 count == 9 (AGENT-PROMPT x5, READY-TO-FIRE x4); 09a `skill` PASS (exit 0); 09a `claims` exit 1 with the same mismatch set and no new file in it; the pairwise R6 test passes; kht DEFAULT mode identical to the pre-flight capture"
  artifacts:
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
      provides: "STEP 9d fire-shell preconditions + the SIGHUP property check + form B at STEP 10 + the B3/B5 reading rule at STEP 9/9-GATE + B11 notes + the B14 two-line merge-base ancestry check at STEP 1 (delivered by EDIT 6b — B-4)"
      contains: "STEP 9d"
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md"
      provides: "§9d (same block, paste form) + form B at §10 + the B7 correction at §9b + B11 notes at §9c"
      contains: "## 9d"
    - path: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md"
      provides: "B14 header + item 1 ancestry gate; item 10 form-B ordering (PROSE — RF states no command; the extractor must find 0 sites here), the STEP 9d pointer and the plink-only RAM reading rule"
      contains: "timeout 312h nohup"          # satisfied DELIBERATELY IN PROSE, not by adding a third command site (I-2/M15)
    - path: ".claude/skills/aou-ld-pipeline/SKILL.md"
      provides: "invariant 3 scoped to the Dataproc server-side job, with the measured VM/nohup exception"
      contains: "2026-09-16"                  # I-3: `invariant` is VACUOUS (present pre-edit at SKILL.md:17 and :27). Pin the DATED SCOPING SENTENCE instead — the new text must carry the 2026-09-16 measurement date inside invariant 3
  key_links:
    - from: "260812-ox1-AGENT-PROMPT.md STEP 3 (export PATH)"
      to: "260812-ox1-AGENT-PROMPT.md STEP 9d"
      via: "an explicit same-shell pointer, so the preconditions are run in the shell that fires"
      pattern: "STEP 9d"
    - from: "260812-ox1-AGENT-PROMPT.md STEP 10 fire command"
      to: "260812-ox1-BROWSER-PASTE.md §10 fire command"
      via: "exact-string identity after backslash-continuation normalization"
      pattern: "timeout 312h nohup python3 src/python/run_native_ld_panel.py"
    - from: "260812-ox1-READY-TO-FIRE.md item 10"
      to: "AGENT-PROMPT STEP 9d / BROWSER-PASTE §9d"
      via: "a named pointer so Carter's only checklist reaches the preconditions"
      pattern: "STEP 9d"
---

<objective>
Close the six **next-Stage-C-fire** findings of the 2026-09-16 blast-radius review inside
the fire surface itself: **B4** (fire-shell preconditions), **B6** (the false SIGHUP claim +
command form B), **B3/B5** (plink-only `peak_ram_gib` reading rule), **B7** ("either way"),
**B14** (stale clone target), **B11** (operational notes).

Purpose: the RAM-1 launcher (`9a3eb97`) has never run for real. Its **first real run is the
unattended 11-day Stage C fire**, and panel rows are FIRST-ROW-WINS
(`run_native_ld_panel.py` `append_panel_row`: `if str(out_row["region_id"]) in
set(existing["region_id"].astype(str)): return`), so an environment defect that errors every
region **writes error rows that survive a re-fire**. Ten seconds of precondition at $0 buys
back a $385-1,084 / 11-day run. Separately, the committed fire command's `nohup` is in the
WRONG POSITION to survive a SIGHUP, and three runbooks plus the SKILL assert the opposite.

Output: four edited documents, a SUMMARY carrying every measurement verbatim, and an
AFTER-equals-BEFORE proof over six existing enforcers.

⛔ **RUNBOOK/DOC ONLY. No code. AN AGENT NEVER FIRES ANYTHING.** Nothing in this task runs
gsutil, touches the AoU perimeter, contacts OSF or Seth, or uses the network.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md

THE INPUT (read in full before Task 1):
@/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/blast/260916-BLAST-RADIUS-findings-consolidated.md

THE FIRE SURFACE (the files being edited):
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
@.claude/skills/aou-ld-pipeline/SKILL.md

THE CODE THE EXPECTs MUST BE DERIVED FROM (read-only — never edit):
@src/python/run_native_ld_panel.py        # _PLINK_PEAK_RSS_LAUNCHER, _run_plink, process_region, append_panel_row
@src/python/fire_verifier.py              # check_peak_ram
@src/python/plink_ld_to_npz.py            # read_square_bin, _has_any_nan_blocked
</context>

<orchestrator_decision_carried>
**Command form B is DECIDED by the orchestrator (Carter delegated the SIGHUP choice).**
Adopt `timeout 312h nohup python3 …` (nohup INSIDE timeout). `setsid` was REJECTED: in an
interactive job-control shell it forks, so `$!` would no longer name the fire PID the runbook
prints. This plan does NOT re-open the decision — it implements it, re-measures it, and adds
the in-perimeter property check the decision requires because **the VM's coreutils version is
UNMEASURED**.
</orchestrator_decision_carried>

<paths>
**`SCRATCH` (W-4) — use this absolute path VERBATIM. The plan must never depend on an
inherited/exported `$SCRATCH`: under `set -e` an unexpanded glob over an undefined variable
kills the loop and reads as a pass elsewhere.**

```
SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-vqr
```

Set it at the top of every shell block that uses it, `mkdir -p "$SCRATCH/enforcers-before"`
first, and guard every loop with an existence test
(`for f in "$SCRATCH"/enforcers-before/E*.txt; do [ -e "$f" ] || { echo MISSING; exit 1; }; …`).

**`PY` — the only interpreter on this node with pandas:**
`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3` (3.11.15 / pandas 3.0.2).
The system `python3` is 3.9.25 with **no pandas**, so `import run_native_ld_panel` fails there
for an unrelated reason — never let that be mistaken for a VM finding.
</paths>

<planner_measurements>
Every number below was **measured by the planner on the NCSU node, 2026-09-16**, in the
session scratchpad (`sighup_ab.sh`, `sigchld_probe.py`, `bash_sigchld.py`). They are written
here as **ANCHORS THE EXECUTOR MUST RE-DERIVE**, not as values to copy. If a re-run
disagrees with an anchor, the re-run wins and the disagreement goes in the SUMMARY.

**Node:** `Linux 5.14.0-687.42.1.el9_8.x86_64`, `timeout (GNU coreutils) 8.32`,
`bash 5.1.8(1)-release`, system `python3` 3.9.25, project env
`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3` = 3.11.15 / pandas 3.0.2.

**M1 — SIGHUP A/B (pidfile-based; NEVER `pgrep -f`, which self-matches the probing shell):**
| case | `$!` is | SIGHUP → `$!` | SIGHUP → process group | verdict |
|---|---|---|---|---|
| form A `nohup timeout 25 python3 …` | `timeout` | launcher DEAD, child DEAD | (pgrp already gone) | child does NOT survive |
| form B `timeout 25 nohup python3 …` | `timeout` | launcher ALIVE, child ALIVE | launcher ALIVE, child ALIVE | child SURVIVES |

**M2 — expiry control (the 312h backstop must still bite):** plain form A `rc=124`, child
DEAD; plain form B `rc=124`, child DEAD.

**M3 — NEW, not in the brief: under form B the wall-cap SURVIVES the SIGHUP.** A 6 s
`timeout 6 nohup …` was HUP'd at t≈2 s: at t+1 s launcher ALIVE and child ALIVE; at t+9 s
(past the cap) launcher DEAD and child DEAD. So form B does not trade the backstop for
survival — it keeps both. **This strengthens the decision and must be stated in the runbook.**

**M4 — `$!` semantics preserved.** `ps -o comm= -p $!` printed `timeout` under BOTH forms, so
`echo "fire PID: $!"` keeps naming the timeout process. Teardown guidance is unchanged.

**M5 — the fire log's shape is unchanged by the swap.** With job control ON (the interactive
VM terminal case), the log's FIRST line is `nohup: ignoring input` under **both** forms; with
job control off it is absent under both. It is not an error, it does not match
`grep -cE "VERIFY-FAILED|^ERROR"`, and no `nohup.out` is created in the cwd because the
shell's `> …fire.log 2>&1` already owns stdout.

**M6 — the launcher smoke, measured through the shipped seam** (stand-in argv, exit 0):
`_run_plink(["true"])` → `(0.000557565689086914, 0.010986328125)` and
`(0.0006140907605489095, 0.0107421875)`. A 2-tuple `(wall_min, peak_ram_gib)`;
`peak_ram_gib` ≈ **0.0107-0.0110 GiB ≈ 11 MiB** = the 3.11 launcher floor. The shipped
`test_launcher_bias_is_bounded` bounds it at **< 24 MiB (0.0234 GiB)**; the docstring gives
~11 MiB (3.11) / ~4 MiB (3.9).

**M7 — the missing-binary signature is unchanged:** `_run_plink(["plink1.9","--version"])`
with no `plink1.9` on PATH → `FileNotFoundError: [Errno 2] No such file or directory:
'plink1.9'` — exactly the 2026-08-24 Stage A stop.

**M8 — the SIGCHLD hazard, SEEN RED (negative control):** with `SIGCHLD = SIG_IGN` inherited,
`_run_plink(["true"])` raises
`SubprocessError: plink peak-RSS launcher exited 0 without a valid report; refusing to
fabricate wall_min/peak_ram_gib for ['true']` (the launcher's own
`ChildProcessError: [Errno 10] No child processes` goes to stderr). **So the one-line smoke
alone already discriminates this failure mode** — the `/proc` read is the diagnostic that
names WHICH precondition failed.

**M9 — ⚠ REVISED (W-2): the hazard reaches the producer through bash and the read detects
it — but the WHOLE MASK IS SHELL-MODE-DEPENDENT, so only the BIT may ever be an EXPECT.**
Re-measured 2026-09-16 in all four cells (`sigign_modes.py`):

| shell | parent SIGCHLD | `SigIgn` | bit `0x10000` | verdict |
|---|---|---|---|---|
| `bash -c` (non-interactive) | `SIG_DFL` | `0000000000000000` | clear | GREEN |
| `bash -c` (non-interactive) | `SIG_IGN` | `0000000000010000` | **set** | RED |
| `bash -ic` (**interactive — THE FIRE SHELL**) | `SIG_DFL` | `0000000000380000` | clear | GREEN |
| `bash -ic` (**interactive — THE FIRE SHELL**) | `SIG_IGN` | `0000000000390000` | **set** | RED |

`0x380000` = bits 19/20/21 = signals 20/21/22 (`SIGTSTP`/`SIGTTIN`/`SIGTTOU`) — exactly what
an interactive shell ignores. **⛔ A whole-mask EXPECT of `0000000000000000` would FALSE-STOP
the real fire shell, which is interactive.** `SIGCHLD` is signal 17 → mask bit
`1 << 16 = 0x10000` (the brief's bit is correct). The detector is faithful in both modes:
bash PROPAGATES an inherited `SIG_IGN` to its children.

**M10 — ⚠ CONTRADICTS THE BRIEF'S SCOPE: `timeout` NEUTRALIZES an inherited
`SIGCHLD=SIG_IGN`.** Measured on GNU coreutils 8.32: with the parent ignoring SIGCHLD,
`timeout 5 python3 …` → bit 0x10000 **False**; `timeout 5 nohup python3 …` (form B) →
**False**; `nohup timeout 5 python3 …` (form A) → **False**; but bare `python3 …` → **True**
and `nohup python3 …` → **True**. Consequence for the runbook wording: the **Stage C fire
command is already shielded by `timeout` on 8.32**, while **Stage A (STEP 8), Stage B
(STEP 9) and every bare `python3 src/python/…` invocation (including the three
`fire_verifier.py` gate runs) are NOT**. The shell-level check is still the right check: it
is version-independent, it is the only cover for Stage A/B, and it does not assume the VM's
coreutils behaves like 8.32.

**M11 — B11's `-I` / LC_CTYPE claim is TRUE and narrower than stated** (python 3.11.15,
`LANG=C`): plain python + `PYTHONCOERCECLOCALE` unset → `LC_CTYPE=C.UTF-8`; plain python +
`PYTHONCOERCECLOCALE=0` → unset; `-I -S` + unset → `C.UTF-8`; **`-I -S` +
`PYTHONCOERCECLOCALE=0` → `C.UTF-8`** (isolated mode implies `-E`, so the opt-out is
ignored). So the launcher changes plink's env **only** in the `LANG=C` **and**
`PYTHONCOERCECLOCALE=0` case; with the variable unset the driver already coerced before
RAM-1 and plink saw the same value.

**M12 — B14 is WORSE than the brief states.** `git diff --name-only 5284505 HEAD -- src tests
config Snakefile workflow` at `621701c` = **19 files: 9 under `src/python/`, 10 under
`tests/m3/`, 0 under `config/`, `Snakefile` or `workflow/`** — not the two commits the brief
names. So READY-TO-FIRE:5-8's "0 files under `src/`, `tests/`" is false while its "0 files
under `config/`, `Snakefile`" half is still TRUE. `origin/m3-W2-aou-deltas == HEAD ==
621701c`, 0 ahead, at planning time.

**M13 — the driver's own in-process load is a FLOOR, not a measured peak.**
`plink_ld_to_npz.read_square_bin` does `np.fromfile(...)` of the whole `.ld.bin` = one dense
`float32` array of **4 · n_var² bytes**: 102,421 vars → **39.1 GiB**; the `--max-n-var`
ceiling of 120,000 → **53.6 GiB**. The NaN / symmetry / triangle scans are deliberately
BLOCKED (`_has_any_nan_blocked`, block=1024) so they add ~`block · n_var` bytes, not another
n_var². `content_verify_npz` (cite it BY SYMBOL — never `run_native_ld_panel.py:514`, which
drifts, per this plan's own EDIT-1 rule) re-loads the banked array afterwards. **State 4·n_var² as a FLOOR** and say the true peak was not measured here.

**M14 — ⚠ SELF-CORRECTION (W-1): `260814-guk-verify.sh fire` exits `1`, not `0`.** My
round-0 reading of `0` was `$?` of the `tail` at the end of a pipe, not the script's. Measured
directly (`bash … fire >/dev/null 2>&1; echo $?`) → **1**. Companions, same method:
vbu `all` → **0**, 09a `--only skill` → **0**, 09a `--only claims` → **1**. The lesson is in
the plan's own rules: a count/exit through a pipe is a claim about the LAST command.

**M15 — the fire-command extractor, prototyped and RED today (B-1).** Join backslash
continuations (`re.sub(r"\\\n\s*", " ", text)`), keep lines containing BOTH
`run_native_ld_panel.py` and `--manifest config/ld_regions.tsv`, whitespace-collapse. At
`621701c`: **AGENT-PROMPT 1 site, BROWSER-PASTE 1 site, READY-TO-FIRE 0 sites** (I-2 — RF
does NOT state the command); the two are **already exactly equal** pre-edit;
`startswith("timeout 312h nohup python3 src/python/run_native_ld_panel.py")` → **False**
(so the assertion ships with its own control); `any startswith("nohup")` → **True**;
`grep -c "nohup timeout"` across the three runbooks → **2** (one per command site).
⚠ Prose and the A/B probe block never match the extractor — that is the whole point of
pinning behaviour instead of a text count.

**M16 — ⚠ NEW (W-6): the smoke's HAPPY path prints TWO lines, which was never measured
before.** With a banner-printing stand-in named `plink1.9` on PATH (plink inherits fd 1):
```
PLINK v1.90b7.2 64-bit (11 Dec 2023)
(0.0007156729698181152, 0.0107421875)
```
and a **4th signature** for a plink that runs and returns non-zero:
`subprocess.CalledProcessError: Command '['plinkfail']' returned non-zero exit status 3.`
⚠ The pinned v1.90b7.2's own `--version` exit status is **UNMEASURED** (no plink on this
node), so the runbook must name `CalledProcessError` as "plink ran, read its banner" rather
than promise exit 0. Wall time is **tens of milliseconds** (0.00056-0.00089 min = 33-53 ms),
**not "~a second"** (I-4).
</planner_measurements>

<enforcer_baseline>
Six enforcers read the four files this task edits. **FIND THEM, RUN THEM BEFORE, RUN THEM
AFTER.** Baselines below were captured by the planner at `621701c` on a clean tracked tree.
⚠ **Re-capture at pre-flight** — vqp and vqq land first and at least one of them rewrites
the banked Stage C draft that `kht` reads.

| # | Enforcer | Command | BEFORE (planner, 621701c) | Rule for this task |
|---|---|---|---|---|
| E1 | trsx5 §6b card | `bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all` | **ALL CHECKS PASSED**, exit 0 (V0-V7, 3 copies) | MUST stay all-green. The §6b card blocks are extracted `^STEP 6b`→`^STEP 7` (AP), `^## 6b`→`^## 7` (BP), `^## 6b`→`^## 7[.]` (RF) — **do not edit inside them and do not introduce a line matching those end anchors before them** |
| E2 | superseded two-body card | `bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh fire` | `RESULT: FAILURES PRESENT`, **exit 1** (W-1/M14 — NOT 0); **failing set = F3 ×3 (AP:155, BP:141, RF:154) + F8 ×9 (AGENT-PROMPT ×5, READY-TO-FIRE ×4)**; PASS: F1 F2 F4 F5 F6 F7 F9 F10 | ⚠ **"byte-for-byte" MUST NOT be read literally (B-2).** `260814-guk-verify.sh:198` emits `fail "F3 [$(basename "$f"):$n] …"` with a **RUN-TIME line number**, and the advisory hash sits at AP:155 / BP:141 / RF:154 — EDIT 6 edits RF :5-8 and item 1 (:25+), i.e. ABOVE :154, so **RF's F3 string necessarily moves**. Compare the **LINE-NUMBER-NORMALISED** set: `sed -E 's/\.md:[0-9]+\]/.md]/'` then `sort`. Separately assert **F3 count == 3** over {AGENT-PROMPT, BROWSER-PASTE, READY-TO-FIRE} and **F8 count == 9** over {AGENT-PROMPT ×5, READY-TO-FIRE ×4}. ⛔ **Never "fix" F8** — its missing tokens are the WITHDRAWN single-condition ceilings; a *disappearing* F8 is a STOP. **F8 BLOCK BOUNDS, MEASURED (`260814-guk-verify.sh:275-292`, awk start→first end-anchor, END EXCLUSIVE): AP = `STAGE C HOLD LIFTED` (:360) → `^STEP 10 ` (:393); RF = `^\*\*Deferral vocabulary` (:368) → `^## 11\.` (:430).** Inside THOSE TWO BLOCKS ONLY, treat `0.0005`, `60.0`, `51.2`, **`Seth`** and regex `102,?421` (bare `102421` matches too) as **NO-WRITE tokens** — the likeliest accident is `Seth` in a STEP 9d provenance line, not a ceiling. `nothing is lost` / `nothing scientific is lost` stay banned **file-wide** (F10) |
| E3 | SKILL no-deletion | `bash .planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-check-sweep.sh --only skill` | `PASS SKILL-01`, 0 failures | MUST stay PASS. The SKILL edit is **ADDITIVE ONLY** — every historical token (`GATE 1.5/0/1/2/3`, `322 = 161 M2 regions × 2 ancestries`, `Egress = 44 export requests`, `RULED PASS 2026-04-28`, `CLEARED 2026-06-12`, `cohort_summary 3 rows`, `BLOCKED on CR-01`, `FIRED 2026-06-12 → PAUSED`) and every banner element stays |
| E4 | stale-claim residual | `bash .planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-check-sweep.sh --only claims` | `FAIL CLAIM-02` — 7 residual mismatches, ALL in `.planning/STATE.md`, `.planning/HANDOFF.json`, `deferred-items.md`; **none in SKILL.md or the runbooks** | The mismatch list must not gain a new file. **Avoid ALL TEN claim patterns in new text (W-7 — three were missing in round 0):** `0-line diff` (C1); **`zero (carter )?decisions? outstanding` (C2)**; **`three (e-2 …) undischarged` / `three undischarged` (C3)**; `LIMITATION-vs-CORRECTION` (C4); `SR4-OPEN` (C5); `ld_npz_to_rds.R` within 140 chars of `frozen` / `unchanged` / **`byte-unchanged`** (C6); `548 passed` / **`548P`** / **`548/31`** (C7); `per-region median` (C8); `NOT YET IMPLEMENTED` / `OPEN AND DEEPER THAN DIAGNOSED` / `BLOCKED on panel reachability` / `BLOCKED until panel reachability` (C9); **`enforced by …(oku\|29 )` or `(oku\|29 clause)… enforced by`, case-insensitive, 120-char window (C10)**. ⚠ **C10 is the plausible one**: the new text is enforcer-heavy and the runbooks already say "~29+ regions" — never write "enforced by" within 120 chars of a `29`/`oku` token |
| E5 | **the enforcer the brief does not name** — `tests/m3/test_pairwise_completeness_scan.py::test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it` | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3 -m pytest "tests/m3/test_pairwise_completeness_scan.py::test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it" -q` | `1 passed` | It `re.search(r"^R6\.(.*?)^R7\.", AGENT_PROMPT, re.S\|re.M)` and requires `occ_measure`, `2026-08-25`, `quick-260825-qpf` inside that block. **Do not edit the R6 block; do not add a line matching `^R7\.` before the real R7.** ⛔ The test file is FROZEN by scope — if an edit trips it, change the edit |
| E6 | Stage C draft citations | `python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py` (DEFAULT mode) | `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, exit 0 — ⚠ **measured PRE-vqq; the PRE-FLIGHT capture is the only baseline that counts** | DEFAULT mode reads every *cited* file with `git show c93e97b:<path>`, so a working-tree edit to a cited file cannot move it — **prove that from the verifier's own `Reader`/`from_tree` logic, don't assume it**. ⚠ **BUT (W-5) it reads the BANKED DRAFT from the WORKING TREE** (`260916-kht-verify.py:1493`, `(ROOT / BANKED_REL).read_bytes()`), so vqq is upstream of this number. Per vqq's design, v2 is a **SEPARATE file** and v1 is frozen byte-identical (its `imm:` gate), so default mode SHOULD stay GREEN — **assert equality to the pre-flight capture, not to a hard-coded `RESULT GREEN` line**, and if it differs **STOP and report** rather than "fixing" anything. `--live` cites `AP:398 / :372-373 / :393 / :417 / :422-423 / :424-428 / :55-61` and `RF:360-366 / :369-370`; these WILL shift. **Record the drift for the orchestrator; never re-pin BASIS.** ⛔ Never edit the verifier |

**Pre-commit guard:** run whatever the repo's guard is before committing. **GPFS "invalid
object / Error building trees" = STOP** and report (see `reference_gpfs_git_object_store_loss`).
**Explicit-path staging only** — never `git add .` / `-A` on this shared tree.
</enforcer_baseline>

<decisions_recorded>
**DECISION-1 — `deferred-items.md` is deliberately NOT touched.** Scope permits it "if a
runbook-adjacent record needs it". Measured: `COST-1` is not an entry in that file (it lives
in `STATE.md`, which is the orchestrator's), so the B5 reading rule has no home there. Against
that, the file is read by the LIVE enforcer `fire_verifier.check_coverage_disclosure_resolved`
(R4-COVERAGE), which exits 1 today **by design**. Opening it for a note we do not need would
put a cosmetic edit on a gated file — the `freeze_economy_is_not_a_reason_to_take_risk` rule.
The B3/B5 rule goes where it is ACTED ON: the Stage-B gate reading sites in the runbooks.

**DECISION-2 — ⚠ REVISED (B-1). The old `grep -c "nohup timeout" == 0` gate was
UNSATISFIABLE and is REPLACED by a behaviour-pinned extractor.** Two reasons it could never
pass: EDIT 1 item 5's A/B property check **must** print the literal `nohup timeout` (it is the
form being falsified), and EDIT 2's retired-form correction **must** quote it too — so
round-0 `must_haves` truths 3 and 4 were mutually exclusive. Byte equality across files is
*also* impossible: `AGENT-PROMPT` states the command on ONE line while `BROWSER-PASTE` states
it `\`-wrapped across 7 lines, and reflowing either would fight the paste ergonomics each
file was built for.

**THE EXTRACTOR (prototyped; see M15).** Join backslash continuations
(`re.sub(r"\\\n\s*", " ", text)`), keep lines containing BOTH `run_native_ld_panel.py`
**and** `--manifest config/ld_regions.tsv`, then whitespace-collapse (`" ".join(ln.split())`).
Assert all five:
1. **exactly 2 sites** — one in AGENT-PROMPT, one in BROWSER-PASTE, **0 in READY-TO-FIRE**
   (prose and the A/B probe never match);
2. the two extracted strings are **exactly equal**;
3. both `.startswith("timeout 312h nohup python3 src/python/run_native_ld_panel.py")`;
4. **none** `.startswith("nohup")`;
5. the tail after `python3` equals the same extraction from `git show PRE:<file>` — so the
   swap provably moved only two words.

It is **RED today** (`form-B=False`), so it ships with its own control.
A count check survives **only as an exact number**: `count("nohup timeout") == N` across the
three runbooks, where **N is exactly what the A/B block plus the retired-form prose
introduce** — the executor derives N, states it, and shows the per-site breakdown. Never `0`.

**DECISION-3 — B14's requirement is stated as an ANCESTRY PROPERTY, not a SHA.** A runbook
cannot name the SHA of the commit that contains it. The requirement Carter's clone must meet
is expressed as `git merge-base --is-ancestor <fix-sha> HEAD` for the fixes that must be
present, plus item 1's existing "push NCSU first" gate for the tip. That is mechanically
checkable in the clone, self-consistent, and immune to the
`fixed_sha_whole_file_pin_is_a_timebomb` failure mode.

**DECISION-4 — the smoke is presented as the PRIMARY check and the `/proc` read as its
DIAGNOSTIC.** M8 shows the one-line smoke already goes red on the SIGCHLD case, on the
`python3 < 3.9` case (`os.waitstatus_to_exitcode` is bound before the spawn), on an odd
`sys.executable`, on a broken import chain, and on a missing `plink1.9`. The `python3 -V` and
`SigIgn` reads exist to say WHICH. Presenting them the other way round would invite an agent
to run the cheap reads and skip the one that actually exercises the seam.
</decisions_recorded>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight — basis, enforcer BEFORE state, and re-derive every EXPECT by measurement</name>
  <files>
    (no repo file is modified in this task)
    scratchpad only: $SCRATCH/{preflight.txt,sighup_ab.out,sigchld.out,smoke.out,enforcers-before/E1..E6.txt}   # ⚠ $SCRATCH already ends in /260916-vqr — do NOT nest it again
  </files>
  <action>
**1a. Basis + sequencing gate (STOP conditions, in this order).**
```
git rev-parse --abbrev-ref HEAD                 # EXPECT m3-W2-aou-deltas (never main)
git rev-parse HEAD; git log --oneline -6
git status --porcelain --untracked-files=no     # EXPECT EMPTY (tracked tree clean)
git log --oneline --all --grep='260916-vqq' | head
git log --oneline --all --grep='260916-vqp' | head
```
STOP and report if: the tracked tree is dirty; the branch is not `m3-W2-aou-deltas`;
**vqq's close-out commit is not in HEAD's ancestry**; or **vqp's close-out commit is not in
HEAD's ancestry (W-8)** — E4's *entire* mismatch set lives in `STATE.md`, `HANDOFF.json` and
`deferred-items.md`, i.e. exactly the files vqp rewrites, so an E4 baseline taken before vqp
lands is worthless. Record HEAD as `PRE` — every `git diff` in Task 3 is against `PRE`.
⚠ Untracked files exist in this tree by design (backup dirs, `targeted_rerun_*`). Use
`--untracked-files=no`; do **not** clean anything.
⚠ Check for a concurrent writer before editing (`feedback_gsd_quick_skill_runs_workflow_twice`):
list the session's subagents dir; if a second runner is executing this same task, STOP.

**1b. Enforcer BEFORE state.** `mkdir -p "$SCRATCH/enforcers-before"` (absolute path from
`<paths>`), run all six from `<enforcer_baseline>`, tee each to
`"$SCRATCH"/enforcers-before/E{n}.txt`, and **capture the exit code SEPARATELY from the
pipeline** — `cmd >file 2>&1; echo "exit=$?"`, never `cmd | tee … ; echo $?`, which reports
`tee`'s status (that is exactly how round 0 recorded guk's exit as 0 instead of 1; see M14).
Record for each: exit code, RESULT line, and — for E2 and E4 — the **exact list of FAIL
lines**, stored BOTH raw and **line-number-normalised** (`sed -E 's/\.md:[0-9]+\]/.md]/' |
sort`, per B-2). The **normalised** lists plus the F3/F8 counts, not the raw strings and not
the exit codes alone, are the AFTER comparison. If any BEFORE differs from the table, do not
proceed on the table's numbers: adopt the freshly measured BEFORE and say so in the SUMMARY.

**1c. Re-run the SIGHUP A/B property test on THIS node.** Write your own probe (do not reuse
the planner's blindly — reproduce it). Requirements:
  - `set -m` so each background job is its own process group and `$!` is its leader.
  - **pidfile-based child identification.** The child writes `os.getpid()` to a file and
    sleeps. ⛔ **Never `pgrep -f <pattern>` that can match your own shell** — that self-match
    already produced one false result today.
  - Cases: form A `nohup timeout N python3 …`, form B `timeout N nohup python3 …`. For each:
    record `ps -o comm= -p $!`; send SIGHUP to `$!`; then to `-$!`; report launcher and child
    liveness (`kill -0`) after each.
  - Controls that must be SEEN: plain expiry `rc=124` with the child DEAD under BOTH forms
    (the backstop still bites), and **expiry AFTER a SIGHUP under form B** (M3).
  - Record `timeout --version | head -1`, `bash --version | head -1`, `uname -srm`.
Compare against M1/M2/M3/M4. **Any disagreement wins over the anchors and is a STOP-and-report
before you write a single EXPECT into a runbook.**

**1d. Re-derive the smoke EXPECT through the shipped seam** using the project env
(`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3` — the system `python3` here
has no pandas, so `import run_native_ld_panel` fails for an unrelated reason; note this in the
SUMMARY so the VM EXPECT is not mistaken for a local one):
```
<PY> -c 'import sys;sys.path.insert(0,"src/python");import run_native_ld_panel as r;print(r._run_plink(["true"]))'   # x2
<PY> -c 'import sys;sys.path.insert(0,"src/python");import run_native_ld_panel as r;print(r._run_plink(["plink1.9","--version"]))'
```
and the **negative control** (M8): the same call with `signal.signal(signal.SIGCHLD,
signal.SIG_IGN)` set first — you must SEE the `SubprocessError: plink peak-RSS launcher
exited 0 without a valid report` red before you are allowed to write "EXPECT a tuple".
**ALSO measure the HAPPY PATH's transcript shape (W-6/M16) — it was never measured before
this revision.** Put a banner-printing stand-in named `plink1.9` on PATH in the scratchpad
(`#!/bin/sh` + `echo "PLINK v1.90b7.2 64-bit (11 Dec 2023)"` + `exit 0`) and run the runbook's
exact one-liner. EXPECT **two lines**: plink's banner (inherited fd 1) THEN the tuple. An
agent told to expect "a 2-tuple" will otherwise read the banner as noise or as a failure.
Then add a **4th signature** with a stand-in that exits non-zero: EXPECT
`subprocess.CalledProcessError: Command '[…]' returned non-zero exit status N` = *plink ran
and returned non-zero, read its banner*. ⚠ Record that the pinned v1.90b7.2's own `--version`
exit status is **UNMEASURED here** (no plink on this node) — the runbook must not promise
exit 0.
Also re-read the `_run_plink` docstring and `tests/m3/test_run_plink_peak_rss.py` for the
bound the shipped test actually enforces (`_BIAS_CEIL_MIB`) — quote the bound from the test,
not from this plan. Note the measured wall time in **milliseconds** (33-53 ms), not seconds.

**1e. Re-derive the SIGCHLD detector in ALL FOUR CELLS** (M9 as revised by W-2). Run the
`/proc/self/status` `SigIgn` read as a child of a bash whose parent has SIGCHLD default and of
one whose parent has `SIG_IGN`, **in BOTH `bash -c` AND `bash -ic` (interactive)** — the fire
shell is interactive. Record all four whole-mask values and all four bit verdicts; they must
reproduce M9's table (`0000000000000000` / `0000000000010000` / `0000000000380000` /
`0000000000390000`). A detector never seen red is not evidence, and **a whole-mask EXPECT is
FORBIDDEN in the runbook** — `0x380000` (SIGTSTP/SIGTTIN/SIGTTOU) is normal for an interactive
shell and a whole-mask EXPECT would FALSE-STOP the real fire. Also re-derive M10 (does
`timeout` reset it?) — the runbook wording depends on it.

**1f. Re-derive M11 (`-I` + LC_CTYPE)** and **M12 (the B14 file counts)**:
```
git diff --name-only 5284505 HEAD -- src tests config Snakefile workflow | sed 's|/[^/]*$||' | sort | uniq -c
git diff --name-only 5284505 HEAD -- config Snakefile workflow | wc -l     # the still-TRUE half
git merge-base --is-ancestor 9a3eb97 HEAD && echo RAM-1-present
git merge-base --is-ancestor 48b8828 HEAD && echo tcujq-present
git rev-parse --short origin/m3-W2-aou-deltas; git rev-list --count origin/m3-W2-aou-deltas..HEAD
```
⚠ Counts are claims (`feedback_a_count_is_a_claim_scope_and_reconcile`): state the scope
(`-- src tests config Snakefile workflow`, at `PRE`) beside every number you write into a
runbook, and reconcile the per-directory counts against the total before shipping.

**1g. Locate every edit site by ANCHOR TEXT, not line number**, and write the site list to
the scratchpad (`grep -n` output for each anchor). The line numbers in the brief are from
`621701c` and vqp/vqq may have moved nothing in these files — verify, don't assume
(`feedback_check_plan_against_red_before_executing`).
  </action>
  <verify>
    <automated>bash -c 'set -e; S=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-vqr; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; test -z "$(git status --porcelain --untracked-files=no)"; git log --oneline --all --grep=260916-vqq | grep -q .; git log --oneline --all --grep=260916-vqp | grep -q .; for n in 1 2 3 4 5 6; do test -s "$S/enforcers-before/E$n.txt"; done; grep -qE "^\[formA\].*child=DEAD" "$S/sighup_ab.out"; grep -qE "^\[formB\].*child=ALIVE" "$S/sighup_ab.out"; grep -q "SubprocessError" "$S/smoke.out"; grep -q "0000000000390000" "$S/sigchld.out"'</automated>
  </verify>
  <done>
`PRE` recorded; tracked tree clean; **both** vqq's and vqp's close-out commits present. All
six enforcer BEFORE outputs captured verbatim, each exit code measured OUTSIDE a pipe, with
E2/E4's FAIL lists stored raw AND line-number-normalised. M1-M16 re-derived on this node:
the SIGHUP probe pidfile-based with **form A's child seen DEAD beside form B's seen ALIVE**;
the smoke's `SubprocessError` negative control SEEN RED; the happy path's **two-line**
transcript and the `CalledProcessError` 4th signature measured with stand-ins; the SIGCHLD
detector seen in **all four** `bash -c` / `bash -ic` × DFL/IGN cells. Every disagreement with
the anchors is written down. No repo file has been modified.
  </done>
</task>

<task type="auto">
  <name>Task 2: Land B4, B6, B3/B5, B7, B14 and B11 in the three runbooks and the SKILL</name>
  <files>
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
.claude/skills/aou-ld-pipeline/SKILL.md
  </files>
  <action>
Write the EXPECTs **from Task 1's measurements**, never from this plan. Every edit is dated
and attributed (`added 2026-09-16, quick-260916-vqr`) in the runbooks' existing house style.
Every edit is **additive or a correction-in-place of a false sentence** — delete no historical
record, retire wording by marking it retired.

***
**EDIT 1 (B4 + B6) — the new precondition block. AGENT-PROMPT: `STEP 9d`, inserted
immediately BEFORE the line `STEP 10 — GATE: STAGE C, THE FULL FIRE`. BROWSER-PASTE: the same
block as `## 9d — FIRE-SHELL PRECONDITIONS`, immediately before `## 10 — STEP B: THE FIRE`.**

⚠ **B-3: `STEP 9d` LANDS INSIDE guk's AP F8 BLOCK.** Measured: that block runs
`STAGE C HOLD LIFTED` (:360) → `^STEP 10 ` (:393), end-exclusive, so anything inserted
"immediately before STEP 10" is inside it. Inside this block the five F8 tokens are
**NO-WRITE**: `0.0005`, `60.0`, `51.2`, **`Seth`** and `102,?421`/`102421`. The realistic
accident is **`Seth`** in a provenance line — attribute the 2026-09-16 measurements to
"the orchestrator's NCSU measurement" / "quick-260916-vqr", never by that name, anywhere in
STEP 9d. Adding an F8 token would make a *pre-existing* FAIL disappear, which this plan
treats as a STOP. Do not introduce a line matching `^STEP 10 ` either (it is the block's end
anchor AND F9's is `STAGE C HOLD LIFTED`; see GUARDRAILS).

Both copies carry, in this order:

1. **WHY, in one line each** (this is what makes an agent run it instead of skipping it):
   - *The launcher has never run for real.* Stage A and Stage B regions auto-skip, so
     Stage C — 11 days, unattended, no `--fail-fast` — is `_run_plink`'s first real run.
   - *Errors are sticky.* Panel rows are FIRST-ROW-WINS (`run_native_ld_panel.py`
     `append_panel_row`, the `if str(out_row["region_id"]) in set(existing["region_id"]…):
     return` early return — cite it by SYMBOL and quote the line, **not** by a bare line
     number, which drifts). An environment defect that errors every region writes error rows
     that a re-fire will not replace, while the `.npz` banks and its row is lost.
2. **THE SMOKE (primary).** One line, run in the shell that will fire, after `export PATH`:
   `python3 -c 'import sys;sys.path.insert(0,"src/python");import run_native_ld_panel as r;print(r._run_plink(["plink1.9","--version"]))'`
   **EXPECT — TWO LINES, not one (W-6/M16).** plink's own banner arrives first on the
   inherited fd 1, then the tuple:
   ```
   PLINK v1.90b7.2 64-bit (11 Dec 2023)
   (<wall_min>, <peak_ram_gib>)
   ```
   `wall_min` is a small fraction of a minute; `peak_ram_gib` is a SMALL NON-ZERO value on the
   order of the launcher floor (state the measured NCSU value and the bound the shipped
   `test_launcher_bias_is_bounded` enforces; both from Task 1d). Say explicitly that **the
   banner is expected** — an agent told only "a 2-tuple" will read it as noise or as failure.
   **ANYTHING ELSE IS A STOP**, and name the **four** signatures the agent will actually see:
   `FileNotFoundError: [Errno 2] … 'plink1.9'` (PATH — go back to STEP 3's pinned install);
   `SubprocessError: plink peak-RSS launcher exited 0 without a valid report` (SIGCHLD or an
   odd `sys.executable` — go to check 4); `AttributeError` / `ModuleNotFoundError` on import
   (interpreter or environment — go to check 3); and **`CalledProcessError: … returned
   non-zero exit status N`** = *plink ran and returned non-zero — read its banner and report*.
   ⚠ Do NOT promise the pinned v1.90b7.2 `--version` exits 0: that is **UNMEASURED** (no plink
   at NCSU). If it exits non-zero, `CalledProcessError` is the EXPECTED happy outcome and the
   banner is the evidence — say so, so the agent reports instead of improvising.
   Say explicitly: **this check spawns plink for tens of milliseconds** (33-53 ms measured)
   **and computes nothing** — it is $0 (I-4).
3. **`python3 -V`.** RECORD IT (it has never been recorded in any as-received record).
   **≥ 3.9 is REQUIRED** — the launcher binds `os.waitstatus_to_exitcode` BEFORE the spawn so
   that an interpreter without it fails before plink runs rather than after hours of compute.
   Below 3.9 → STOP.
4. **SIGCHLD.** `grep '^SigIgn' /proc/self/status` in the fire shell; bit `0x10000`
   (SIGCHLD = 17 → `1 << 16`) MUST be 0. Give the copy-paste **arithmetic** form that prints a
   verdict word (e.g. read the hex field, `$(( 0x$V & 0x10000 ))`, print `SIGCHLD-OK` or
   `STOP`).
   ⛔ **BINDING (W-2): the EXPECT is the BIT VERDICT ONLY. A whole-mask EXPECT is FORBIDDEN.**
   Measured (Task 1e): a non-interactive shell reads `0000000000000000` but **the fire shell is
   INTERACTIVE and reads `0000000000380000`** (SIGTSTP/SIGTTIN/SIGTTOU — normal). Publishing
   `0000000000000000` as the EXPECT would **FALSE-STOP the real fire**. State both observed
   masks as *informational*, and make only `bit 0x10000 == 0` the pass condition. WHY: an
   inherited `SIG_IGN` makes
   `os.wait4` raise `ChildProcessError`, so **every region raises** — and the old
   `subprocess.run` silently returned 0, so nothing else in the pipeline notices.
   ⚠ State the SCOPE honestly per M10/Task 1e: on GNU coreutils 8.32 `timeout` resets SIGCHLD
   to `SIG_DFL` before exec, so the Stage C command is additionally shielded — but **Stage A
   (STEP 8), Stage B (STEP 9) and every bare `python3 src/python/…` run, including the three
   `fire_verifier.py` gates, are NOT**, and the VM's coreutils version is unmeasured. The
   shell-level check is the version-independent cover.
5. **THE SIGHUP PROPERTY CHECK (B6), ~10 s, $0, in-perimeter.** A/B with a stand-in child,
   **pidfile-based** (say in the text why: `pgrep -f` matches the probing shell itself).
   EXPECT, from Task 1c: form A's child DEAD after SIGHUP, form B's child ALIVE, and — the
   negative control that makes the green mean something — **form A is expected to fail; if
   BOTH forms survive or BOTH die, the property did not reproduce → STOP and report, do not
   fire.** Include the expiry control (`rc=124`, child dead) and M3 (under form B the cap
   still fires after a SIGHUP) so the check proves the backstop was not traded away.
   State WHY it is here: **the VM's coreutils version is UNMEASURED**; the decision was made
   on GNU coreutils 8.32 at NCSU.

**EDIT 2 (B6) — the fire command itself, at EVERY site that states it.**
⚠ **THE SITE INVENTORY IS MEASURED AND CLOSED (I-2/M15): there are EXACTLY TWO — AGENT-PROMPT
and BROWSER-PASTE. `READY-TO-FIRE` does NOT state the command** (0 extractor hits); it
describes the shape in prose. **Do not add a third site.** The two are already
normalized-identical *before* this edit, so the only change is the two-word swap at each.
RF's `contains: "timeout 312h nohup"` is satisfied **deliberately in prose** (item 10's
ordering sentence), not by introducing a command block.
- `AGENT-PROMPT` STEP 10: `nohup timeout 312h python3 …` → **`timeout 312h nohup python3 …`**,
  everything after `python3` byte-unchanged, including `> /home/jupyter/native_ld_fire.log
  2>&1 &` and the following `echo "fire PID: $!"`.
- `BROWSER-PASTE` §10: the same swap on the first line of the `\`-wrapped block.
- Correct the three false claims **in place, marked as corrected**, never deleted:
  - `AGENT-PROMPT` "Everything already banked auto-skips. nohup survives browser
    disconnects; the 312h timeout is the wall-cap backstop"
  - `BROWSER-PASTE` "`nohup` survives browser disconnects (the SKILL's invariant 3 …)"
  - `READY-TO-FIRE` item 10 "`nohup` plus `timeout 312h` (13-day wall-cap), **server-side**"
  The replacement says, from measurement: *`nohup` survives a disconnect **only in form B**.
  In the previously committed form A (`nohup timeout …`), `nohup`'s ignore-SIGHUP applies to
  `timeout`, which forwards the signal to the child — MEASURED 2026-09-16 on GNU coreutils
  8.32: the child DIED. In form B the child ignores SIGHUP and SURVIVES, `$!` still names the
  `timeout` process, and the 312h wall-cap remains armed after the SIGHUP.* Keep "teardown is
  UI-only" and the wall-cap framing intact.
- Note M5 so a check-in agent does not misread it: with job control on, the fire log's first
  line is `nohup: ignoring input`; that is normal, form-independent, and does not match the
  `grep -cE "VERIFY-FAILED|^ERROR"` monitor.

**EDIT 3 (B6) — `SKILL.md` invariant 3.** ADDITIVE ONLY. Keep every existing sentence of
invariant 3 (it is TRUE of the Dataproc/Hail server-side job). Append a dated, scoped
correction: invariant 3 is about the **Dataproc master-side job**; it is **NOT** a warrant for
the Cloud Analysis VM native-plink fire, whose survival depends on the command form. Name form
B, name the measurement and its date, and point at the runbooks' property check. Do not touch
any GATE row, banner or historical token (E3).

**EDIT 4 (B3 + B5) — the plink-only RAM reading rule, at the Stage-B gate reading sites**
(`AGENT-PROMPT` STEP 9 rollup + STEP 9-GATE; `BROWSER-PASTE` §9b's rollup + stage-b gate;
`READY-TO-FIRE` item 10's mechanical-gates paragraph).

✅ **B-3(b): these sites are OUTSIDE the F8 blocks, so the `102,421` ban does NOT apply here**
— which resolves the round-0 contradiction between this EDIT (which needs to name n_var
102,421 to derive the 39.1 GiB floor) and the blanket GUARDRAILS ban. **Measured safe sites:**
`AGENT-PROMPT` STEP 9 / STEP 9-GATE = **:295-359**, i.e. before the AP F8 block's
`STAGE C HOLD LIFTED` start at :360; `READY-TO-FIRE`'s `**MECHANICAL GATES for this stage**`
= **:335-341**, i.e. before the RF F8 block's `^\*\*Deferral vocabulary` start at :368.
⚠ AP's STEP 9 region IS inside guk **F9's** cost block (`^STEP 9 ` :295 →
`STAGE C HOLD LIFTED` :360), so preserve `cost-per-bankable-region` (AP:311, uppercase) and
introduce no line matching `STAGE C HOLD LIFTED` (W-9).

Say, at each:
- `peak_ram_gib` is **plink's OWN peak RSS** since `9a3eb97` (launcher floor ≈ the measured
  bias; quote Task 1d's number and the shipped bound).
- **The driver's own largest load is NOT in that column.** `plink_ld_to_npz.read_square_bin`
  `np.fromfile`s the whole `.ld.bin` in-process — **≈ 4 · n_var² bytes** (give the two derived
  figures: n_var 102,421 and the 120,000 ceiling) — and `content_verify_npz` re-loads the
  banked array afterwards. State it as a **FLOOR**; the true driver peak has not been measured.
- Therefore `fire_verifier.check_peak_ram` (15% headroom on 120 GiB = 102.0 GiB) now bounds
  **plink only**. Plink reserves about half of detected RAM, so a pass there is not headroom
  evidence for the driver. **Add the driver term separately** when reading the Stage-B gate,
  sizing the VM, or computing COST-1.
- **B5:** the four rows already in the bucket panel TSV — `00001 30.6591`, `00017 2.9689`,
  `00040__sub14 26.5745`, `00057 26.5745` — are **PRE-FIX**: they are not plink-only
  measurements, there is no code-version column, nothing mechanically separates them, and they
  **must not be mixed with post-fix values**. COST-1 uses post-fix rows only; if a class has
  no post-fix row, say so rather than substituting a pre-fix one.

**EDIT 5 (B7) — `BROWSER-PASTE` §9b.** Replace
"(`wall_min` / `peak_ram_gib` land in the panel TSV either way)" with the measured truth:
if **plink itself** fails, `_run_plink` **raises before** `result["wall_min"]` /
`result["peak_ram_gib"]` are assigned, so **BOTH stay `None`** and the row records
`error: …`. Say what that costs: `m2_region_00071`'s worst-case RAM/wall — the whole reason
it is in Stage B — is exactly what is lost when it fails. Keep the surrounding FINDING framing
(a Stage-B failure bounds the 28-region large class; it does not block the other 248).
Cite `_run_plink` and `process_region` by SYMBOL.

**EDIT 6 (B14) — `READY-TO-FIRE` header (:5-8) and item 1.**
- Keep the verification basis (`5284505`, "agent-verifiable rows green as of 2026-08-12",
  the evidence TSV). **Correct the false clause**: mark "any commits after that HEAD are
  `.planning`-only — 0 files under `src/`, `tests/`, `config/`, `Snakefile`" as **retired**
  and replace it with Task 1f's measured statement — N files under `src/python/` and M under
  `tests/m3/` have changed since `5284505` (give the scope and the date), while `config/`,
  `Snakefile` and `workflow/` are still 0. Name RAM-1 (`9a3eb97`, the `_run_plink` launcher)
  and tcujq (`48b8828`) as the changes that matter to the fire.
- Item 1 (the push/pull gate): the clone/`git pull` target is **the tip Carter pushes from
  NCSU immediately before the fire** — state it as "at or after the tip at fire time" and
  give the in-clone verification that does not depend on a SHA the document cannot name for
  itself (DECISION-3): `git log --oneline -1` plus
  `git merge-base --is-ancestor 9a3eb97 HEAD` and `… 48b8828 HEAD`, each with its STOP.
  Keep the existing "`git push` does NOT push tags" warning and the never-run-from-`main` rule.
  ⛔ Do **not** add, remove or renumber any `## N.` heading in this file (E2/F7).

**EDIT 6b (B14, REQUIRED — this is the half that actually runs) — `AGENT-PROMPT` STEP 1.**
⚠ Round 0 promised B14 in `files_modified` and in the AGENT-PROMPT artifact's `provides` but
**no edit delivered it**: EDIT 6 is READY-TO-FIRE-only, and RF item 1 is *Carter's checklist*
while **AP STEP 1 (:63-72) is the step the in-perimeter agent actually executes**. Add to
STEP 1's RUN block, after the existing `git checkout -f` / `git branch --show-current` lines:
```
git merge-base --is-ancestor 9a3eb97 HEAD && echo "RAM-1 present"
git merge-base --is-ancestor 48b8828 HEAD && echo "tcujq present"
```
EXPECT **both** lines print (both ancestries verified present at `621701c`; re-verify at
Task 1f). If either is silent the clone predates a fix that changes the fire path → **STOP
under R3**, do not proceed to STEP 2. Name what each is: `9a3eb97` = the `_run_plink`
peak-RSS launcher (RAM-1), `48b8828` = the tcujq withdrawal notices.
⚠ STEP 1 is far above the §6b card and the F8/F9 blocks, so no anchor rail applies here — but
do not introduce a line matching `^STEP 7`, `^R7\.` or `^STEP 10 `.

**EDIT 7 (B11) — operational notes.** Put them where they are used: `AGENT-PROMPT` STEP 10's
monitoring block and `BROWSER-PASTE` §9c. Three notes, each with its scope:
- **A launcher-only SIGKILL / OOM orphans plink.** The region records `error:`, the orphaned
  plink keeps running while the next region's plink starts (two concurrent plinks, and the
  scratch of both). Say the reassuring half too: **nothing is recorded `ok` by mistake and
  nothing runs twice** — there is no retry path.
- **`pgrep -f plink1.9` / `pkill -f plink1.9` now ALSO match the launcher** (the launcher's
  argv carries the plink argv; its lower PID lists first). Use **`pgrep -x plink1.9`** — it
  matches the plink process only. ⚠ And the trap that already cost a false result today: a
  `-f` pattern can match the probing shell itself.
- **`-I` can add `LC_CTYPE=C.UTF-8` to plink's env**, but only in the `LANG=C` **and**
  `PYTHONCOERCECLOCALE=0` case (M11/Task 1f): isolated mode implies `-E`, so the opt-out is
  ignored; with the variable unset the driver already coerced before RAM-1.
Optionally note that the launcher's messages for a broken `sys.executable` do not name the
launcher — which is why check 2's signature list exists.

***
**GUARDRAILS while editing** (all from `<enforcer_baseline>`):

**The no-introduce anchor rail — never add a line matching any of these above its real one:**
`^STEP 6b`, `^STEP 7`, `^## 6b`, `^## 7`, `^## 7.`, `^R7\.` (E1/E5), **`^STEP 10 `**
(F8's AP end anchor), **`STAGE C HOLD LIFTED`** (F8's AP start AND **F9's AP cost-block end**
anchor — W-9; EDIT 4 writes at :295-359 and EDIT 1 at :393, adjacent to both), and
`^\*\*Deferral vocabulary` / `^## 11\.` (F8's RF bounds).
- Never edit inside a §6b card block; never edit the `^R6.`…`^R7.` block.
- No `## N.` heading added/removed/renumbered in READY-TO-FIRE (F7).
- **SCOPED token bans (B-3) — the blanket round-0 ban was wrong and blocked EDIT 4:**
  - **Inside the two F8 blocks ONLY** (AP `STAGE C HOLD LIFTED`:360 → `^STEP 10 `:393;
    RF `^\*\*Deferral vocabulary`:368 → `^## 11\.`:430) — NO-WRITE: `0.0005`, `60.0`,
    `51.2`, **`Seth`**, `102,?421`/`102421`. ⚠ STEP 9d is inside the AP one.
  - **File-wide** — NO-WRITE: `nothing is lost`, `nothing scientific is lost` (F10) and all
    ten 09a claim patterns from E4 (**especially C10: never "enforced by" within 120 chars of
    a `29`/`oku` token** — the new text is enforcer-heavy and the runbooks say "~29+ regions").
  - **Everywhere else `102,421` is FINE and EDIT 4 needs it** (:295-359 AP, :335-341 RF).
- ✅ `nohup timeout` is **REQUIRED** in EDIT 1 item 5 and EDIT 2's retired-form prose. There is
  **no zero-count gate** (B-1); the gate is the extractor plus an exact derived count N.
- Keep `cost-per-bankable-region` inside BROWSER-PASTE's `**Cost-refinement gate` → `**Stage C`
  block, READY-TO-FIRE's `- **C —` → `- **D —` block, and AGENT-PROMPT's `^STEP 9 ` →
  `STAGE C HOLD LIFTED` block (AP:311, uppercase) (E2/F9).
- Fence every code paste in triple backticks (`feedback_code_paste_fences`).
  </action>
  <verify>
    <automated>bash -c 'set -e; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; D=.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3 - <<"PYEOF"
import re, sys
D = ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/"
F = ["260812-ox1-AGENT-PROMPT.md", "260812-ox1-BROWSER-PASTE.md", "260812-ox1-READY-TO-FIRE.md"]
def sites(t):
    j = re.sub(r"\\\n\s*", " ", t)
    return [" ".join(l.split()) for l in j.split("\n")
            if "run_native_ld_panel.py" in l and "--manifest config/ld_regions.tsv" in l]
S = {f: sites(open(D + f).read()) for f in F}
assert [len(S[f]) for f in F] == [1, 1, 0], S
flat = S[F[0]] + S[F[1]]
assert len(set(flat)) == 1, flat
P = "timeout 312h nohup python3 src/python/run_native_ld_panel.py"
assert all(x.startswith(P) for x in flat), flat
assert not any(x.startswith("nohup") for x in flat), flat
ap = open(D + F[0]).read(); bp = open(D + F[1]).read()
assert "STEP 9d" in ap and "## 9d" in bp
assert "either way" not in bp
assert sum(open(D + f).read().lower().count("nothing is lost") for f in F) == 0
print("OK extractor+markers")
PYEOF'</automated>
  </verify>
  <done>
All eight edits (1, 2, 3, 4, 5, 6, **6b**, 7) landed across the four files. The extractor
finds exactly 2 sites, both form B, both equal, 0 in READY-TO-FIRE; `STEP 9d` / `## 9d` exist;
`either way` is gone from BROWSER-PASTE; the SKILL edit deleted nothing; AP STEP 1 carries the
two `merge-base --is-ancestor` lines (B14 actually delivered). The literal `nohup timeout`
count equals the derived N with its per-site breakdown recorded. Every EXPECT traces to a
Task 1 measurement in the scratchpad; the SigIgn EXPECT is a BIT verdict, not a whole mask;
no scoped or file-wide banned token was introduced.
  </done>
</task>

<task type="auto">
  <name>Task 3: Prove AFTER == BEFORE, prove the fire command is identical at every site, record the kht drift, and commit</name>
  <files>
.planning/quick/260916-vqr-stage-c-fire-preconditions-in-the-runboo/260916-vqr-SUMMARY.md   (created; the orchestrator commits it)
  </files>
  <action>
**3a. The fire-command identity proof — the most load-bearing check in this task
(DECISION-2 / B-1).** Run the five-part extractor assertion: (1) exactly 2 sites — AP 1,
BP 1, **RF 0** (I-2); (2) the two extracted strings exactly equal; (3) both
`.startswith("timeout 312h nohup python3 src/python/run_native_ld_panel.py")`; (4) none
`.startswith("nohup")`; (5) the tail after `python3` equal to the same extraction from
`git show PRE:<file>`, so the swap provably moved only two words.
Then the **exact count**: `count("nohup timeout")` across the three runbooks == the N derived
in Task 2, with the per-site breakdown (A/B probe block + retired-form prose) listed in the
SUMMARY. ⛔ **Never assert 0** — EDIT 1 item 5 and EDIT 2 must both quote form A.
**Prove the comparator can fail**: run it against a deliberately altered copy in the
scratchpad (swap the two words back, and separately drop one site) and SEE both reds before
trusting the green (`feedback_green_assertion_needs_a_negative_control`). It was already
observed RED on the pre-edit tree (`form-B=False`, M15), which is the first control for free.
⛔ Pin behaviour, not a grep count alone (`feedback_grep_gate_matches_text_not_meaning`).

**3b. Re-run all six enforcers (E1-E6) and diff against Task 1b**, not against this plan:
- E1 vbu `all` → must be ALL CHECKS PASSED, **exit 0**.
- E2 guk `fire` → `RESULT: FAILURES PRESENT`, **exit 1** (W-1). ⚠ **Compare the
  LINE-NUMBER-NORMALISED set, not the raw strings (B-2)**: `sed -E 's/\.md:[0-9]+\]/.md]/' |
  sort`, then require equality with the BEFORE normalised set. RF's F3 line number **WILL**
  move (EDIT 6 edits :5-8 and item 1, above the advisory hash at :154) and that is EXPECTED —
  a raw-string comparison would false-STOP by construction. Separately assert **F3 count == 3**
  and **F8 count == 9** (AGENT-PROMPT ×5, READY-TO-FIRE ×4). Any NEW FAIL is a STOP; any FAIL
  that **disappeared** is a STOP — a vanished F8 means a withdrawn ceiling was reintroduced.
- E3 09a `--only skill` → PASS SKILL-01, **exit 0**.
- E4 09a `--only claims` → **exit 1** with the same mismatch set as BEFORE; no new file in it.
- E5 the pairwise R6 pytest → `1 passed`.
- E6 kht **DEFAULT** → the RESULT line must be **identical to the Task 1b PRE-FLIGHT
  CAPTURE** — ⛔ **not** to a hard-coded `RESULT GREEN checks=317 …` (W-5). Then **prove why**
  it is unaffected rather than asserting it: show that default mode resolves *cited* files with
  `git show <BASIS>:<path>` (the verifier's own `Reader`/`from_tree` logic) so a working-tree
  edit to a cited file cannot reach it. ⚠ It nonetheless reads the **banked draft from the
  working tree** (`260916-kht-verify.py:1493`, `(ROOT / BANKED_REL).read_bytes()`), which is
  why the baseline must be vqq-relative. If AFTER != the capture: **STOP and report**; do not
  re-pin BASIS, do not edit the verifier, do not "fix" the draft.
- **kht `--live` drift, for the orchestrator:** run `--live`, record its RESULT line, and list
  the citations whose line numbers this task moved — the AP citations (`:398`, `:372-373`,
  `:393`, `:417`, `:422-423`, `:424-428`, `:55-61`) and the RF citations (`:360-366`,
  `:369-370`) — with their NEW line numbers at HEAD. Report the delta; **changing the banked
  draft is vqq's job, not this task's**.

**3c. Diff hygiene.** `git diff --numstat PRE -- <the four files>` → exactly four files, no
others. `git diff PRE -- .planning/quick/260812-ox1-*/` must show **0 deleted lines** in
SKILL.md; for the runbooks, every deleted line must be a false sentence this plan names
(list them in the SUMMARY with the replacement). Confirm `src/`, `tests/`, `config/`,
`workflow/`, `bin/`, `.planning/amendments/`, `osf_deviations.md`, `HANDOFF.json`,
`DECISIONS.md`, `STATE.md` and the banked draft are all untouched:
`git diff --name-only PRE | grep -E '^(src|tests|config|workflow|bin)/' ` must be empty.

**3d. SUMMARY.** Create `260916-vqr-SUMMARY.md` (do NOT commit it — the orchestrator does)
carrying, verbatim:
- the Task 1c SIGHUP A/B transcript (observed output pasted, not paraphrased);
- the Task 1d smoke tuple, the TWO-LINE happy-path transcript, the `CalledProcessError`
  4th signature, and the SubprocessError negative control;
- the Task 1e SIGCHLD detector in ALL FOUR cells (`bash -c` / `bash -ic` x DFL/IGN) with
  both whole masks AND both bit verdicts, and the Task 1e/M10 `timeout` result;
- the Task 1f LC_CTYPE table and the B14 file counts with their scope;
- the BEFORE/AFTER enforcer table with exit codes measured OUTSIDE a pipe, and E2/E4's
  FAIL lists raw AND line-number-normalised, plus the F3/F8 counts;
- the derived `nohup timeout` count N with its per-site breakdown;
- the kht `--live` citation drift list;
- **anything that contradicted the planner's anchors M1-M16** (M14-M16 were added in the
  round-1 revision: guk's real exit code, the extractor prototype, the two-line happy path);
- the edit-site list with final line numbers.

**3e. Commit.** Explicit paths only (⛔ never `git add .` / `-A` on this shared GPFS tree):
```
git add .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md \
        .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md \
        .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md \
        .claude/skills/aou-ld-pipeline/SKILL.md
```
Message: `docs(quick-260916-vqr): Stage C fire preconditions — launcher smoke + SIGCHLD +
python3 -V (B4), SIGHUP command form B with an in-perimeter property check (B6), plink-only
peak_ram_gib reading rule (B3/B5), the "either way" correction (B7), the clone-target ancestry
gate (B14) and the launcher operational notes (B11)` + the body naming each finding, the
enforcer BEFORE/AFTER result and the measurements. End with the `Co-Authored-By: Claude Opus 5
<noreply@anthropic.com>` trailer. **Do not push** (the orchestrator closes out).
⚠ If the commit fails with GPFS "invalid object / Error building trees": **STOP**, do not
retry blindly, report (recovery recipe in `reference_gpfs_git_object_store_loss`).
  </action>
  <verify>
    <automated>bash -c 'set -e; S=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-vqr; cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3 "$S/fire_cmd_assert.py"; bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all >/dev/null; bash .planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-check-sweep.sh --only skill >/dev/null; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3 -m pytest "tests/m3/test_pairwise_completeness_scan.py::test_r6_records_the_occ_measure_allowance_and_all_three_runbooks_cite_it" -q >/dev/null; bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh fire > "$S/E2-after.txt" 2>&1; test "$(grep -c "^FAIL  F3" "$S/E2-after.txt")" = 3; test "$(grep -c "^FAIL  F8" "$S/E2-after.txt")" = 9; sed -E "s/\.md:[0-9]+\]/.md]/" "$S/E2-after.txt" | grep "^FAIL" | sort > "$S/E2-after.norm"; sed -E "s/\.md:[0-9]+\]/.md]/" "$S/enforcers-before/E2.txt" | grep "^FAIL" | sort > "$S/E2-before.norm"; diff -q "$S/E2-before.norm" "$S/E2-after.norm"; python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | tail -1 > "$S/E6-after.txt"; diff -q <(tail -1 "$S/enforcers-before/E6.txt") "$S/E6-after.txt"; test -z "$(git diff --name-only HEAD~1 HEAD | grep -E "^(src|tests|config|workflow|bin)/")"'</automated>
  </verify>
  <done>
E1 exit 0 all-green; E3 exit 0 PASS; E5 `1 passed`; **E2 exit 1 with the
LINE-NUMBER-NORMALISED fail set equal to BEFORE plus F3 count 3 / F8 count 9**; **E4 exit 1
with the same mismatch set and no new file**; **E6 DEFAULT identical to the PRE-FLIGHT
capture** with the basis-read mechanism proven from the verifier's own reader. The extractor's
five assertions pass, with the comparator SEEN RED on two mutated copies (word-swap-back and
site-dropped) in addition to its pre-edit red. The `nohup timeout` count equals the derived N,
never 0. The `--live` citation drift is recorded for the orchestrator. Exactly four files
changed, none under `src/`, `tests/`, `config/`, `workflow/` or `bin/`. SUMMARY written with
every transcript verbatim; one `docs(quick-260916-vqr): …` commit with the trailer, not pushed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| runbook text → an unattended $385-1,084 / 11-day irreversible spend | Every EXPECT here is executed by an agent inside the AoU perimeter that is instructed to prize execution fidelity over judgment. A wrong EXPECT is acted on, not questioned |
| NCSU measurement (coreutils 8.32, py 3.11/3.9) → the AoU VM (versions UNMEASURED) | A property proven here can silently not hold there |
| planner brief → runbook | Numbers copied from a brief instead of measured are unowned claims |
| shared GPFS working tree ↔ concurrent executors | Other terminals write this branch; a second skill-runner can duplicate this task |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-vqr-01 | Tampering | the Stage C fire command | mitigate | Only the two words `nohup`/`timeout` swap; Task 3a proves the rest of the command is byte-identical to `git show PRE:` after normalization, at both sites, with the comparator seen RED on a mutated copy |
| T-vqr-02 | Spoofing (a green that means nothing) | the new EXPECTs | mitigate | Each is re-derived in Task 1 on this node AND observed failing: the smoke's `SubprocessError` under SIG_IGN, the SIGCHLD detector under both parents, form A's child dying beside form B's surviving |
| T-vqr-03 | Information disclosure (a false property carried across a boundary) | the SIGHUP guarantee on the VM | mitigate | The guarantee is not asserted for the VM — the runbook carries a ~10 s in-perimeter A/B property check with an explicit STOP if it does not reproduce, because the VM's coreutils version is unmeasured |
| T-vqr-04 | Denial of service (a weakened enforcer) | vbu / guk / 09a / pairwise / kht | mitigate | BEFORE state captured verbatim in Task 1b; Task 3b compares FAIL LISTS, not exit codes; the plan forbids editing any enforcer and forbids "fixing" guk F8, whose green would mean reintroducing the withdrawn ceilings |
| T-vqr-05 | Repudiation | the B14 clone target | mitigate | Stated as a `git merge-base --is-ancestor` property checkable inside the clone rather than as a SHA the document cannot name for itself, so it cannot go stale-green |
| T-vqr-06 | Elevation (scope creep onto the fire path) | `src/`, `tests/`, the banked draft, `deferred-items.md` | mitigate | `files_frozen`; Task 3c asserts `git diff --name-only PRE` has zero entries under `src/`, `tests/`, `config/`, `workflow/`, `bin/`; DECISION-1 records why `deferred-items.md` (gated by the live R4-COVERAGE enforcer) stays closed |
| T-vqr-07 | Tampering | concurrent writers on the GPFS tree | accept | Pre-flight checks for a duplicate runner and requires a clean tracked tree; explicit-path staging only. Residual risk is another terminal committing mid-task, which the `PRE`-anchored diff surfaces |
</threat_model>

<verification>
- Pre-flight: tracked tree clean, branch `m3-W2-aou-deltas`, vqq close-out present, `PRE` recorded.
- Six enforcer BEFORE outputs captured; AFTER compared by FAIL LIST, not exit code.
- SIGHUP A/B re-run on this node, pidfile-based, with form A's death as the negative control.
- Smoke tuple + `SubprocessError` negative control observed; SIGCHLD detector observed both ways.
- `nohup timeout` count == the EXACT DERIVED N (⛔ NEVER 0 — the A/B block and the retired-form
  prose must BOTH quote form A; this line carried round 0's unsatisfiable gate and is corrected);
  the extractor finds 2 sites (AP 1, BP 1, RF 0), both equal, both form B; `timeout 312h nohup`
  at both sites; command tail byte-identical to `PRE`;
  normalized command strings exactly equal; command tail byte-identical to `PRE`.
- `either way` absent from BROWSER-PASTE; `STEP 9d` / `## 9d` present; SKILL edit has 0 deletions.
- kht DEFAULT RESULT line identical to BEFORE, with the basis-read mechanism proven, and the
  `--live` citation drift listed for the orchestrator.
- `git diff --name-only PRE` shows exactly the four files, none under `src/`, `tests/`,
  `config/`, `workflow/`, `bin/`.
</verification>

<success_criteria>
An agent standing in the fire shell can, in under a minute and at $0, prove the launcher works
end-to-end on this VM's interpreter, that SIGCHLD is not poisoned, and that the fire will
survive a browser disconnect **on this VM's own coreutils** — each with a measured EXPECT and
an explicit STOP. Every site that states the fire command states form B, identically. The
Stage-B gate's RAM number is read as plink-only with the driver's dense load accounted
separately and the four pre-fix rows quarantined. The clone target is a checkable property
instead of a stale claim. Six existing enforcers are exactly as green (and exactly as red) as
they were before the task.
</success_criteria>

<revision_log>
**Round 1 (checker feedback, all ADOPTED).** The checker independently re-measured all 13
round-0 physics anchors and confirmed every one, and confirmed the enforcer inventory is
complete. All four blockers were the same class: *the plan's own STOP firing on work the plan
ordered*.
- **B-1** the `grep -c "nohup timeout" == 0` gate was unsatisfiable (EDIT 1 item 5 and EDIT 2
  must both quote form A; truths 3 and 4 were mutually exclusive) → replaced by the
  behaviour-pinned extractor (DECISION-2, M15), plus an exact derived count N. Never 0.
- **B-2** "byte-for-byte identical FAIL list" false-STOPs because guk emits run-time line
  numbers and EDIT 6 edits above RF:154 → line-number-normalised set + F3 count 3 / F8 count 9.
- **B-3** the F8 block bounds were unnamed and STEP 9d lands inside the AP one → bounds
  printed, five tokens marked NO-WRITE **inside those blocks only**, `102,421` un-banned at
  EDIT 4's measured-safe sites (resolving the EDIT-4-vs-GUARDRAILS contradiction).
- **B-4** B14 was promised but undelivered (EDIT 6 was RF-only, and AP STEP 1 is the step the
  agent runs) → new **EDIT 6b** adds the two `merge-base --is-ancestor` lines to AP STEP 1.
- **W-1** guk `fire` exits **1**, not 0 (my round-0 `0` was `tail`'s status — M14).
- **W-2** the SigIgn EXPECT was specified for the wrong shell mode: the fire shell is
  interactive and reads `0000000000380000`. A whole-mask EXPECT is now FORBIDDEN; only the
  `0x10000` bit verdict is the pass condition. All four cells re-measured (M9).
- **W-3/W-4/W-5** verify gates now pin both SIGHUP directions, `SCRATCH` is an absolute path
  defined once in `<paths>`, and the kht assertion compares to the pre-flight capture (kht
  reads the banked draft from the working tree at `:1493`).
- **W-6** the smoke's happy path prints **two** lines (banner + tuple) and has a 4th signature
  (`CalledProcessError`); v1.90b7.2's `--version` exit status is unmeasured (M16).
- **W-7/W-8/W-9** added claim patterns C2/C3/C10 (+C6 `byte-unchanged`, C7 `548P`), added
  **vqp** to the ancestry STOP, and added `STAGE C HOLD LIFTED` / `^STEP 10 ` to the
  no-introduce anchor rail.
- **I-1..I-5** the extractor is in Task 3's `<automated>`; RF states no command (2 sites only,
  do not add a third); SKILL's vacuous `contains: "invariant"` replaced with the dated
  scoping sentence; the smoke is "tens of milliseconds"; `content_verify_npz` cited by symbol.

I re-verified every checker measurement myself before adopting: guk/vbu/09a exit codes
(1/0/0/1), all four `SigIgn` cells, the F8/F9 block bounds and their line numbers, guk:198's
run-time-line-number `fail` string, the extractor prototype (2 sites / RF 0 / equal /
form-B False / count 2), and the two-line happy path plus `CalledProcessError`.
</revision_log>

<output>
After completion, create
`.planning/quick/260916-vqr-stage-c-fire-preconditions-in-the-runboo/260916-vqr-SUMMARY.md`
(the orchestrator commits PLAN / SUMMARY / VERIFICATION / STATE.md).
</output>

<orchestrator_addendum date="2026-09-17" source="plan-checker iteration 2 (0 blockers / 7 warnings / 4 info) — ALL adopted under --auto --chain">
BINDING; overrides any conflicting text above. Record each in the SUMMARY. ⚠ W-1 and W-3 are ALREADY APPLIED in place above (the `<verification>` zero-count line and the double-nested `$SCRATCH` path); the rest are below.

**R-1 (W-2 — Task 3 dies on its first command).** `$S/fire_cmd_assert.py` is RUN at Task 3's `<automated>` but never CREATED (the string appears on that one line only). Add to **Task 3a**: "Write the five assertions (plus the `git show PRE:` tail comparison) to `$SCRATCH/fire_cmd_assert.py` — it is the script Task 3's `<automated>` runs. Reuse Task 2's `<automated>` python body VERBATIM and add assertion 5." Without this, `set -e` kills Task 3 immediately.

**R-2 (W-4 — Task 1's gate pins an output contract the action never states).** Task 1's gate greps `^\[formA\].*child=DEAD`, `^\[formB\].*child=ALIVE`, `0000000000390000` and `SubprocessError` in `sighup_ab.out` / `sigchld.out` / `smoke.out`, but 1c/1d/1e never name those files or that line format → guaranteed false-RED on first run. Add to **1c**: "Write the probe transcript to `$SCRATCH/sighup_ab.out`, ONE LINE PER CASE in exactly this form: `[formA] after SIGHUP to $!: launcher=<ALIVE|DEAD> child=<ALIVE|DEAD>` (same for `[formB]`) — Task 1's gate greps it." Add the analogous sentence to **1d** (`smoke.out`) and **1e** (`sigchld.out`, which must contain all four whole-mask values).

**R-3 (W-5 — the E6 comparison is fragile against 1b's own capture convention).** Task 1b mandates `cmd >file 2>&1; echo "exit=$?"`; if that `echo` lands in `E6.txt`, `tail -1` returns `exit=0` and the diff false-REDs. In BOTH places use `grep '^RESULT' <file> | tail -1`, and state in 1b that the `exit=` line goes to `preflight.txt`, NEVER into `E{n}.txt`. (E2 is immune — it filters on `^FAIL`.)

**R-4 (W-6 — a claimed invariant with no enforcer).** The revision claims it "added an assertion that no `<automated>` block contains an escaped quote"; that assertion does NOT exist in the plan (the checker swept all three plans: the defect itself is genuinely absent everywhere). Either add to Task 3d / `<verification>`: assert the count of `\"` across this PLAN's `<automated>` blocks is 0 — or change the revision-log line to "fixed; **UNENFORCED — belief only**". Do not leave it as a claimed-but-unenforced invariant.

**R-5 (W-7 — pin the two things round 0 promised and failed to deliver).** Add to Task 2's python gate:
`assert "merge-base --is-ancestor 9a3eb97" in ap and "merge-base --is-ancestor 48b8828" in ap`
`assert "2026-09-16" in open(".claude/skills/aou-ld-pipeline/SKILL.md").read()`
This is the exact "promised in `provides`, absent from the file" class that produced blocker B-4.

**R-6 (I-1..I-4).** (i) must_haves truth 1 and `<verification>` name only vqq — add "and vqp's" to both (Task 1a and Task 1 `<done>` already require both). (ii) M16's "(no plink on this node)" is FALSE — a real PLINK 1.9 lives at `/rs1/researchers/c/ckclinto/conda_envs/hlp_crossmap/bin/plink`; the checker symlinked it as `plink1.9` and got banner `PLINK v1.9.0-b.8 64-bit (22 Oct 2024)` then `(0.0008885423342386881, 0.010986328125)`, rc 0, stable ×3. In **1d** prefer the real binary and record both; and write the runbook EXPECT as a SHAPE ("plink's version banner line, then the `(wall_min, peak_ram_gib)` tuple"), NEVER a specific version string — the VM's pinned v1.90b7.2 prints a different banner and its `--version` exit status remains genuinely unmeasured. (iii) add `and "nothing scientific is lost"` to Task 2's F10 assertion (the existing check covers only one of F10's two patterns). (iv) T-vqr-04 append ", **line-number-normalised**, plus F3 count 3 / F8 count 9".

**R-7 (keep in the record).** The checker reproduced Task 2's gate VERBATIM on the un-edited tree: it passes the site-count and equality assertions and fails at `assert all(x.startswith(P))` with rc 1 — the control is real and fails at the claimed point. It also confirmed the plan uses `sort`, NOT `sort -u`, so a NEW F3 at a different line in the same file still changes the multiset and is caught.
</orchestrator_addendum>
