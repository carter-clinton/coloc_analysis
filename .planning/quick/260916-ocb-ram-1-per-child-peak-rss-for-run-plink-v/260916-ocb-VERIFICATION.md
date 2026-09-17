---
phase: quick-260916-ocb
verified: 2026-09-17T00:01:40Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
basis: 11f61e8
head: 9a3eb97
commits_verified: [f8ff9cd, 9a3eb97]
---

# Quick task 260916-ocb (RAM-1): verification report

**Goal:** RAM-1. `_run_plink` in `src/python/run_native_ld_panel.py` must report the peak RSS of each region's own plink child, not a high-water mark that only ever rises. The requirements:
- Use Carter's chosen design (2026-09-16, "Small launcher process (Recommended)").
- Keep contract, signal and timeout behaviour the same as `subprocess.run`.
- Work test-first (TDD) and reconcile the full suite.
- No cloud work and no fire.

**Verified:** 2026-09-17T00:01:40Z (2026-09-16 20:01 EDT), NCSU login node, on branch `m3-W2-aou-deltas` at HEAD `9a3eb97`.
**Status:** passed
**Re-verification:** No. This is the first verification.

**How this was checked:**
- Every result below comes from running code at HEAD, not from the SUMMARY.
- The repo was treated as read-only. Probes, mutants and exported copies lived only in the session scratchpad (`…/scratchpad/ocbv/`), which was deleted afterwards.
- I did not run the full `tests/m3` suite. I ran single test files only; the full-suite reconciliation was checked from the executor's saved junit XML files (see truth 9).

## Goal Achievement

### Observable Truths

| # | Truth (PLAN must_haves) | Status | Evidence (observed by the verifier) |
|---|---|---|---|
| 1 | No inheritance across calls; launcher bias pinned below 24 MiB | VERIFIED | `tests/m3/test_run_plink_peak_rss.py` at HEAD gives **25 passed in 6.16s**, including A1 and A6. Probe `probe_rss.py` on 3.11 with the real `import run_native_ld_panel`: `true` read 11.00 MiB and `python -c pass` read 11.00–11.25 MiB. |
| 2 | Memory the driver freed (its high-water mark) and memory it still holds are not charged to plink | VERIFIED | **Probe on BOTH interpreters, while the driver holds 256 MiB of private, touched bytearray heap** (Private_Dirty 319648 / 272056 / 271640 KiB). Tiny child read through the launcher: 3.11 import **11.25**, 3.11 extract **11.00**, 3.9 extract **7.00** MiB, all under 24 MiB. `true` read 11.00 / 11.00 / **4.19** MiB. After the driver freed the memory, the launcher read 11.00 / 11.00 / 7.00 MiB. A2 and A3 are GREEN. |
| 3 | A grandchild that plink waited for counts; one it did not wait for does not | VERIFIED | B2 and A4 are GREEN at HEAD. The same tests read 363.65 MiB on the pre-fix driver: A4 was RED, as declared. |
| 4 | Non-zero exit raises CalledProcessError with the original cmd. SIGTERM gives -15. Exec-failure exception is identical to `subprocess.run`'s | VERIFIED | Probe `probe_contract.py` compares against a live `subprocess.run(check=True)`. Result: **36/36 on 3.11 (import) and 36/36 on 3.9 (extract)**. Details under Behavioral Spot-Checks. |
| 5 | Same fd set and ignored-signal mask as `subprocess.run`; stdio uncaptured and in order; modules in the cwd cannot shadow the stdlib; no leaks | VERIFIED | B6, B8, B9, B12 and B13 are GREEN. The contract probe also matched `subprocess.run` exactly on: fd targets, SigIgn/SigBlk/SigCgt, full environment, cwd, pgid/sid and umask, on both interpreters. |
| 6 | SIGTERM and timeout behaviour no worse than before (group SIGTERM, driver-only SIGTERM, SIGINT) | VERIFIED | B7, B10 and B11 are GREEN at HEAD **and** on the pre-fix driver (16 GREEN there). NC04 (B7), NC07 (B10) and NC08 (B4/B7/B11/B13) were re-run independently and each failed exactly its declared set. |
| 7 | A launcher that gives no valid report raises exactly `SubprocessError`. A missing `os.waitstatus_to_exitcode` fails before plink is spawned | VERIFIED | A5×3 and A7 are GREEN; A7 includes the addendum A-3 `capfd` reason check. NC11 re-run: A7 RED on `CHILD-STARTED`, as declared. |
| 8 | The recorded fix goes RED on its declared set. All 12 negative controls hit their declared sets exactly. The premise-monitor test exists | VERIFIED | **All 12 negative controls re-run by the verifier** on a scratch copy of HEAD, with the whole test file each time: **12/12 EQUAL**, collected=25, and every restore was byte-identical. NC01 (the recorded fix) failed 10 / passed 15, with A2 at **368.41 MiB** and A3 at **366.63 MiB**. C1 is present and GREEN. |
| 9 | Suites reconcile to baseline plus the 25 new tests. Freeze pins GREEN. kht default GREEN. `--live` RED rows are all in this file at lines ≥ 184. All changed lines of the old file are within 183–202 | VERIFIED | Freeze pins: **39 passed** (re-run). kht default: **RESULT GREEN checks=317 parsed=88 table=88 verified=88**, exit 0 (re-run). kht `--live`: RED 31/318, all in `run_native_ld_panel.py`, lowest cited start line 723. Diff hunks all inside 183–202 (re-run). Full-suite reconciliation: taken from the executor's XML files, not re-run (see Requirements and Gaps). |

**Score:** 9/9 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tests/m3/test_run_plink_peak_rss.py` | RED-first tests: 21 functions / 25 items, at least 350 lines, contains `drv._run_plink(` | VERIFIED | 674 lines, 21 `def test_`, 25 collected, `drv._run_plink(` appears 21 times. Imports the real driver through the repo bootstrap (`PROJECT_ROOT/src/python`). Unchanged since the RED commit (`git diff --quiet f8ff9cd HEAD -- tests/`). |
| `src/python/run_native_ld_panel.py` | `_run_plink` runs through the isolated launcher and `os.wait4`; contains `_PLINK_PEAK_RSS_LAUNCHER` | VERIFIED | 1344 → 1487 lines (+143). md5 `de5352822a6a092d80b0a26b19bb4eae`, which matches the SUMMARY's GREEN snapshot. The launcher program and `_run_plink` body match PLAN §(b)/(c). Banner line 184 is 79 characters. No TODO, FIXME or placeholder text. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `process_region` | `_run_plink` | unchanged call site | WIRED | `:1160 wall_min, peak_ram_gib = _run_plink(cmd)`. This is basis line :1017 plus 143, and the text is identical. |
| `_run_plink` | `_PLINK_PEAK_RSS_LAUNCHER` | Popen of `sys.executable -I -S -c` with `pass_fds` | WIRED | `:305`. Mutation NC03 (dropping `-I`) makes B9 RED. |
| launcher | plink's own rusage | `os.wait4(child.pid, 0)`; exit-code helper bound before the spawn | WIRED | `:228`, `:194`. Mutation NC11 makes A7 RED. |
| test file | the real `_run_plink` | direct calls plus harness subprocesses | WIRED | 21 direct `drv._run_plink(` calls. The seam is never monkeypatched; only the launcher constant is, in A5 and A7. |
| `fire_verifier.check_peak_ram` | panel column `peak_ram_gib` | consumer unchanged | WIRED | `fire_verifier.py:733` is unchanged (not in `git diff --name-only 11f61e8..HEAD`). `test_fire_verifier.py`: 91 passed, 1 skipped. |

### Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Real data? | Status |
|---|---|---|---|---|
| `_run_plink` return `[1]` | `record[2]` (KiB) | the launcher's `os.wait4` `usage.ru_maxrss` for the plink pid, sent over the report pipe | Yes. A 300 MiB child reads ≥ 250 MiB (A1, B2); a tiny child reads about 11 MiB | FLOWING |
| panel `peak_ram_gib` | `round(peak_ram_gib, 4)` | `_run_plink(cmd)[1]` at `:1160-1162` | Yes, same function | FLOWING |

### Behavioral Spot-Checks (verifier-run)

**1. Driver memory is excluded, on both interpreters** (`probe_rss.py`, run 3 ways).

| Mode | Driver state while holding | Launcher: tiny / `true` | Direct Popen+wait4: tiny / `true` | After free: launcher / direct | Result |
|---|---|---|---|---|---|
| 3.11.15, real import | VmRSS 372512 KiB | 11.25 / 11.00 MiB | **363.19 / 363.19 MiB** | 11.00 / 363.19 MiB | PASS |
| 3.11.15, AST-extract of HEAD | VmRSS 278816 KiB | 11.00 / 11.00 MiB | **271.82 / 271.82 MiB** | 11.00 / 271.82 MiB | PASS |
| 3.9.25, AST-extract of HEAD | VmRSS 277576 KiB | 7.00 / 4.19 MiB | **265.64 / 265.65 MiB** | 7.00 / 9.64 MiB | PASS |

- The premise still holds: a direct wait4 reads at least 250 MiB on both interpreters.
- The difference after a free is visible here: 3.11 (vfork) charges the driver's lifetime high-water mark, while 3.9 (fork) charges only its current resident size.
- **The probe can fail.** Pointed at a scratch copy of the recorded fix (NC01), the launcher rows went to 273.63 MiB (3.11) and 265.75 MiB (3.9), and the probe returned PROBE-RSS FAIL on both.

**2. Contract parity with `subprocess.run(check=True)`** (`probe_contract.py`): **36/36 on 3.11 import, 36/36 on 3.9 extract.**
- **Non-zero exit (rc 3, 1, 255):** CalledProcessError with the same returncode. `.cmd` equals the original cmd and is the same object; `.output` and `.stderr` are None; `str()` is identical.
- **Killed by a signal:** returncodes -15, -9 and -2, with identical `str()`.
- **Exec failures:** tested with a missing name on PATH, a missing absolute path, a non-executable file, a directory, and the literal `plink1.9`. Type, args, errno, strerror, filename, filename2 and `str()` were all identical (FileNotFoundError and PermissionError).
- **stdio:** with the harness writing stdout and stderr to files, the byte streams were identical to `subprocess.run` and in order (`H-BEFORE, CHILD-OUT 0..2, H-AFTER`).
- **Inherited state:** fd targets, SigIgn/SigBlk/SigCgt, environment, cwd, pgid/sid and umask were all identical.
- **The probe can fail:** scratch mutant NC02 gave 27/36 (`.cmd` and `str` mismatches) and NC06 gave 31/36 (all 5 exec-failure cases).
- One probe bug of my own was fixed. My first SIGKILL case called `signal.signal(9, …)`, which raises EINVAL. Both paths returned rc 1 identically, so parity held even then.

**3. Tests at HEAD, one file per run** (PYTHONDONTWRITEBYTECODE=1, `-p no:cacheprovider`):

| File | Result |
|---|---|
| `test_run_plink_peak_rss.py` | 25 passed in 6.16s |
| `test_source_freeze_pins.py` | 39 passed |
| `test_run_native_ld_panel.py` | 75 passed |
| `test_fire_verifier.py` | 91 passed, 1 skipped |
| `test_occlusion_gate_constants.py` | 10 passed |
| `test_pairwise_completeness_scan.py` | 115 passed |

The five neighbour files add up to 330 passed and 1 skipped, which matches SUMMARY §(c).

**4. RED re-observed.** The committed test file (HEAD, byte-identical to `f8ff9cd`) was run against a `git archive 11f61e8 src/python` copy in scratch: **9 failed, 16 passed**. The FAILED set is exactly A1, A2, A3, A4, A5×3, A6, A7.

**5. Negative controls, all 12 re-run on a scratch copy of HEAD.** Every run was EQUAL to its declared set, collected 25, and restored the file cmp-identical.

| NC | Failed (declared = observed) | Key observed value | Time |
|---|---|---|---|
| NC01 | A1, A2, A3, A4, A5×3, A6, A7, B7 | A1 122.18, **A2 368.41**, **A3 366.63**, A4 122.93, A6 122.93 MiB; B7 TimeoutExpired | 66.4 s |
| NC02 | B3 | cmd mismatch | 7.1 s |
| NC03 | B9 | launcher exited 99 | 6.7 s |
| NC04 | B7 | TimeoutExpired | 67.5 s |
| NC05 | B8 | n0 4 / n1 5 | 6.5 s |
| NC06 | B5×3 | filename None | 6.6 s |
| NC07 | B10 | Traceback | 6.7 s |
| NC08 | B4, B7, B11, B13 | SigIgn 0x4003; group-SIGTERM survivor | 97.5 s |
| NC09 | B12, B13 | fds `0 1 2 3 4`; SigIgn 0x180000003 | 6.5 s |
| NC10 | A6 | 43.31 MiB (A1 GREEN) | 7.0 s |
| NC11 | A7 | CHILD-STARTED | 7.1 s |
| NC12 | B13 | SigIgn 0x1 | 6.7 s |

**6. Scope** (re-run).
- **Changed files:** `git diff --name-only 11f61e8 HEAD` lists exactly `src/python/run_native_ld_panel.py` and `tests/m3/test_run_plink_peak_rss.py`.
- **Diff hunks:** the old-side ranges from `git diff -U0` are `-184`, `-186,0`, `-188`, `-190,4`, `-195`, `-197` and `-199,4`. All lie inside 183–202 under both the default and patience diff algorithms.
- **Line alignment:** basis lines 1..183 equal HEAD 1..183, and basis 203..1344 equal HEAD 346..1487.
- **AST check:** 58 non-seam top-level nodes and the module docstring are identical. HEAD adds exactly one Assign, `_PLINK_PEAK_RSS_LAUNCHER`. As a negative control, changing one constant in a copy produced 1 difference.
- **Commits:**
  - `f8ff9cd` (parent `11f61e8`) touches only the test file, +674 lines.
  - `9a3eb97` (parent `f8ff9cd`) touches only the source file, +156/−13.
  - Both end with the `Co-Authored-By: Claude Opus 5` trailer.
- **Worktree:** tracked status is empty; not pushed (ahead 4).
- **Python 3.9:** `compile()` of the HEAD file succeeds.

**7. kht verifier** (re-run, `TMPDIR` in scratch).
- **Default mode:** `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, exit 0. Once 40-hex hashes are normalised, this output is byte-identical to the executor's `kht-default-before.txt`.
- **`--live` mode:** `RESULT RED 31/318 parsed=88 table=88 verified=64`, exit 1. This output is byte-identical to the executor's `kht-live-after.txt`.

### Requirements Coverage

| Requirement | Source | Description | Status | Evidence |
|---|---|---|---|---|
| RAM-1 | defect record `260824-STAGE-B-HALT…md:112-125` | `peak_ram_gib` must be a per-region (own-plink) measurement before Stage C | SATISFIED | Truths 1–3 and spot-checks 1 and 5. The record's "clean fix" (`Popen` + `os.wait4` from the driver) was independently observed RED on both interpreters (spot-check 1 negative control) and as NC01. |
| QUICK-260916-ocb | PLAN frontmatter | TDD, parity, scope, reconciliation | SATISFIED | Truths 4–9. The full-suite reconciliation was **checked from the executor's artefacts, not re-run** (the constraint forbids a full `tests/m3` run). I parsed `/gpfs_common/share01/clintonlab/ckclinto/tmp/260916-ocb/m3-{before,after}.xml` myself by node id: before `passed=1187 skipped=33`, after `passed=1212 skipped=33`, added 25 (all in the new file, all passed), removed 0, changed 0. `p2`: 136/1 before and after, 0/0/0. The `m3-after.xml` timestamp is 19:17:43 EDT, which is after the fix commit at 23:17:15Z. |

REQUIREMENTS.md has no RAM-1 row (it is a quick task tracked in STATE and the defect record), so no requirement is orphaned.

### SUMMARY findings checked (orchestrator item 4)

| SUMMARY claim | Verdict | Evidence |
|---|---|---|
| kht `--live` RED rows are only in `run_native_ld_panel.py`: 24 citations, 5 `c-ast`, plus `e:log` and `e:diff` | ACCURATE | **24 citation rows.** Ids c05 c07 c08 c09 c10 c11 c20 c21 c23 c47 c48 c49 c50 c51 c52 n01 n07 c53 c54 c55 c56 c59 c66 c67. Each has a PASS `c-res` resolving to `src/python/run_native_ld_panel.py`, and these are all 24 of that file's citations. Start lines run from 723 to 1325. **5 `c-ast` rows:** S3, S4, S5, S6 and S9, all on RN. **`e:log`:** its single commit is `9a3eb97`. **`e:diff`:** `git diff --name-only c93e97b -- RN FV PL` lists only RN. No RED row names another file. |
| Every RED citation's text is unchanged, only shifted by the file's growth | ACCURATE (+143) | **Unchanged file:** RN at `c93e97b` is identical to RN at `11f61e8`. **Citation windows:** for all 24 RED citations, the basis window L..M equals the `c93e97b` window equals HEAD L+143..M+143. **Anchors:** the S3/S4/S5/S6/S9 anchor lines (967, 962-965, 1106, 1136-1139, 806, 866, 923-925) also equal HEAD +143. S9's own message shows the shift (815→958, 872→1015, 923→1066, 825→968, 850→993). |
| A full `tests/m3` run rewrites the tracked `tests/m3/sparse_parent_benchmark.tsv` | ACCURATE (one misattribution) | Confirmed from the test source; the suite was not run. `tests/m3/test_sparse_parent_benchmark.py:138` does `BENCHMARK_TSV.write_text(header + line)` unconditionally with fresh R timings, and `BENCHMARK_TSV` is the tracked `tests/m3/sparse_parent_benchmark.tsv` (`:37`). **Correction:** the unconditional writer is `test_no_whole_parent_dense_materialization` (`:54`). The SUMMARY names `test_sparse_parent_benchmark_records_metrics` (`:141`), which only regenerates the file when it is absent. The tracked TSV is currently clean. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `src/python/run_native_ld_panel.py` | 80 | `import resource` is now unused | Info | Left on purpose so lines 1–182 keep their numbering. Recorded in SUMMARY §(k). |
| `tests/m3/test_run_native_ld_panel.py` | 14 | stale "SOLE subprocess seam" wording | Info | File is frozen for this task. Recorded in SUMMARY §(k). |
| `260916-ocb-SUMMARY.md` | Deviations §1 | names the wrong test as the benchmark-TSV writer | Info | Documentation only; the substance is correct (see above). |

There are no TODO, FIXME or placeholder markers, no `skip` or `xfail` in the new test file, and no stub returns.

### Human Verification Required

None for this task's goal. Everything was checked by running code.

### Gaps Summary

**No gaps.**
- **Measurement:** `_run_plink` reports plink's own peak RSS through the isolated launcher. The driver's held or freed memory does not leak into the reading on Python 3.11 or 3.9, and the recorded direct-wait4 fix was observed contaminated on both.
- **Contract:** results, exceptions, fds, signal masks, environment, stdio and process group all match `subprocess.run`.
- **Controls and scope:** all 12 negative controls reproduce their declared sets, and the change is confined to basis lines 183–202.

**Follow-ups, not gaps** (outside this task, already listed in SUMMARY §(k)/(l)):
1. **The banked Stage C NaN-posture draft is stale against the working tree.** kht `--live` is RED 31/318 because of the +143 line shift. Default mode, pinned to `c93e97b` and stated in the draft as "Code at HEAD c93e97b", stays GREEN. If the draft goes to the adjudicator with live line numbers, its 24 citations to `run_native_ld_panel.py` and the S3–S6/S9 anchors need +143. The draft is frozen here, so this is Carter's call.
2. **Pre-fire:** record `python3 -V` on the AoU VM, since `os.waitstatus_to_exitcode` needs Python 3.9 or later. A7 guarantees an older interpreter fails at region 1, before any plink compute.
3. **Orchestrator:** update the RAM-1 wording in STATE.md and HANDOFF.json to "small isolated launcher + os.wait4 (direct wait4 measured contaminated)".
4. **COST-1:** use post-fix `peak_ram_gib` readings only. Do not quote any Stage A/B `peak_ram_gib` value as a plink measurement.
5. **Fire command (for Carter; the launcher neither adds nor removes this):** `nohup timeout 312h python3 …` does not protect the driver from SIGHUP.

---

_Verified: 2026-09-17T00:01:40Z_
_Verifier: Claude (gsd-verifier)_

---

## ⚠ AS-OF CORRECTION 2026-09-16 (appended by quick-260916-vqp; nothing above is edited)

Appended by `quick-260916-vqp` after the 2026-09-16 blast-radius review (finding B10). Nothing
above this heading is edited.

**`:135` is now FALSE.** It reads "**Worktree:** tracked status is empty; not pushed (ahead 4)."
That was true at verification time. The branch has since been pushed: re-measured 2026-09-16,
`git rev-parse HEAD origin/m3-W2-aou-deltas` prints
`621701c8c28168b13f188467670d1ab90502ea06` twice, so `origin/m3-W2-aou-deltas == HEAD == 621701c`
and nothing is ahead. The tracked tree is still clean (`git status --porcelain -uno` is empty).
