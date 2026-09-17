# Blast-radius assessment: branch m3-W2-aou-deltas, range c93e97b..621701c (2026-09-16)

**Scope reviewed:**
- `quick-260916-kht`: Stage C options draft plus its citation checker.
- `quick-260916-ocb`: RAM-1, the `_run_plink` launcher.
- `quick-260916-oyq`: tcujq WITHDRAWN notices plus the freeze-pin rescope.
- The `STATE.md` edits from all three.

**Method:** four independent read-only investigators (D1 fire-path runtime, D2 tests/enforcers, D3 record consistency, D4 pre-registration/science) plus a Codex CLI v0.141.0 adversarial review (read-only sandbox; raw output below). The orchestrator re-checked three load-bearing claims directly:
- `run_native_ld_panel.py:793` keeps the first panel row per region.
- The draft's §4 heading at `:196`.
- `260812-ox1-BROWSER-PASTE.md:386` says RAM lands "either way".

Nothing in the repo was edited during the review. Codex confirmed the tree was unchanged.

**Overall verdict:** no BLOCKER. Code, tests, artifacts and pre-registered behaviour are intact. The problems are in record propagation, in the Seth-bound draft, and in fire-time preconditions.

**Labels:** severity; NEW (introduced by this range) / PRE-EXISTING / PRE-EXISTING-AGGRAVATED; source (D1, D2, D3, D4, CODEX, ORCH).

---

## A. Verified safe (with the load-bearing reason)

- **No pre-registered behaviour moved** (D4, CODEX). Docstring-stripped AST diff: only `_run_plink` and the new `_PLINK_PEAK_RSS_LAUNCHER` differ in `run_native_ld_panel.py`. The code of `condition_ld_matrix.py` and `write_conditioned_ld_npz.py` is identical. These files are untouched: `plink_ld_to_npz.py` (raw NaN-raise), `occlusion_span_filter.py`, `occlusion_gate_constants.py`, `fire_verifier.py`, the PSD R utilities. No POSTED text mentions peak RAM (0 hits for `RAM|peak.?ram|maxrss|resident set` in the posted trsx5 body, the mk7ze posted extract and the tcujq amendment), so RAM-1 needs no deviation-log entry. ⚠ NARROWED 2026-09-16 23:26 by re-measurement: `.planning/amendments/AOU-LD-PIPELINE.md` DOES mention RAM at `:471`, `:488`, `:492` — cluster-sizing prose ("~1.6 TB worker RAM", "RAM-bound"), not a measurement contract, and that file is an internal protocol, not a posted OSF text. Write the narrow claim, never the broad one.
- **Fire artifacts are identical except `wall_min` / `peak_ram_gib`** (D1). An end-to-end run with a fake `plink1.9` compared old vs new: result dicts, file lists, all 5 `.npz` arrays, gate JSON, and the panel header and non-RAM cells all match.
- **Launcher parity with `subprocess.run`** (D1, CODEX):
  - PATH lookup of `plink1.9`, env, argv, fds 0/1/2 only, and exec errors (Errno 2 text identical).
  - 50 MB stdout plus 50 MB stderr: no deadlock.
  - A grandchild holding stdout does not block the call.
  - GNU timeout 8.32: expiry group-SIGTERM parity and SIGHUP parity.
  - No retry path, so no double run.
- **New failures classify as FAILURE `error:`, never UNKNOWN** (D1). `SubprocessError`, `OSError` and `TypeError` all land in `except Exception` (`run_native_ld_panel.py:1287-1288`), and `fire_verifier._FAILURE_PREFIXES = ("error:",)` (`fire_verifier.py:303`). `peak_ram_gib` cannot be None/NaN on an ok row; its floor is the ~0.0107 GiB launcher bias.
- **The in-perimeter pre-fire pytest cannot collect the new test files** (D2, CODEX). `260812-ox1-AGENT-PROMPT.md:198` selects 3 node ids in `test_occlusion_span_filter.py`.
- **New test files are portable and stable** (D2):
  - 81/81 pass on Python 3.9 / 3.10 / 3.12 / 3.13, and 25/25 on 3.11.
  - Stable: 3 back-to-back runs, 4 busy loops, pinned to one contended core.
  - Leave nothing behind.
- **Every enforcer reading the changed files still goes RED on a targeted mutation** (D2 NC1–NC10). The rescope lets a docstring-only commit to `condition_ld_matrix.py` through and catches a code edit. The `plink_ld_to_npz.py` byte pin is kept.
- **Suite-level:** only +25 / +17 ids added; 0 outcome changes; 33 skips identical (D2).
- **tcujq notices are true** (D4, CODEX, D3):
  - The quoted sentence is a substring of posted trsx5:19.
  - The posted-body status is settled by `DEC-2026-08-17-trsx5-gate-released`.
  - Timestamps match `osf_deviations.md:104/:155`.
  - 4 raise sites / 2 "pre-registered" / 1 DEFERRED.
  - "NOT called by the pipeline" holds.
- **The `DEC-2026-09-16-condition-ld-matrix-freeze-code-only` entry is accurate** and quotes Carter's choice verbatim (D3, D4).
- **STATE.md numbers verify** (D3): commit SHAs and subjects; tests/m3 1187→1212→1229 / 33; +143 lines; 36/36 contract checks; `git fsck` 194 broken links from 162 trees (0 in HEAD's tree); trsx5 line numbers.

## B. Findings: newly introduced or aggravated (severity order)

### B1. HIGH · PRE-EXISTING-AGGRAVATED · D3, CODEX: stale resume surfaces
- `.planning/HANDOFF.json` (untouched in the range):
  - :256 headline and resume_on_reconnect[1]: "--fail-fast halts the batch … Agent DRAFTS the options".
  - :260: "Fix with Popen + os.wait4" / "agent-doable NOW".
  - :261: "docstring edits are FREE and cannot trip the freeze".
  - resume_entry_point: "items 2-3 are agent-doable immediately".
  - carter_decisions_outstanding[0]: "decide after the agent drafts options".
  - repo_fixes_status[2]: "3. STILL QUEUED — THE ONLY ONE OUTSTANDING".
  - suite_baselines tests/m3: "1122 passed" (now 1229 / 33).
  - freeze_state (~:112): "docstrings … DELIBERATELY FREE".
- `STATE.md:26` still says "`.planning/HANDOFF.json` is CURRENT as of 2026-07-16 and is AUTHORITATIVE for resume".
- `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:13`: "Production still raises … `--fail-fast` halts … (2) RAM-1 fix (TDD, agent-doable) (3) `tcujq` docstring defect (agent-doable, code-pinned so free)". Its frontmatter `status: SWEEP_RUNNING_pid913…` has been stale since 08-26.
- `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`:
  - :118-122: "region 17 → 2.9689 (real, first child) … Region 1's 30.6591 is real because Stage A was its own process".
  - :124: "Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's own".
  - :146: "RAM-1 fix (TDD)".
  - All three are contradicted by ocb-SUMMARY §(j), VERIFICATION NC01, and the measurement that even a first child absorbs the driver's memory.
- **Mitigation:** tests catch the worst wrong action (C1/A2/A3 go RED if Popen+wait4 is reinstated). The realistic harm is redone work or pressure to weaken tests.
- **Gate:** next session resume.

### B2. MEDIUM ×7 · NEW · D4, D3, CODEX, ORCH: Stage C options draft (v1) is not courier-ready (`.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md`)
1. **Basis / line numbers.**
   - :20 "Code at HEAD `c93e97b`" is no longer literally true (the tip is 621701c).
   - All 24 `run_native_ld_panel.py` citations plus AST anchors S3–S6/S9 are +143 at HEAD.
   - `260916-kht-verify.py --live` gives RED 31/318 (verified=64); default mode gives GREEN 317/88.
   - One more RED is `e:log` (true at c93e97b, false at HEAD).
   - The courier caveat lives only under STATE item 2, not item 1's courier step (`STATE.md:55`).
2. **§4 heading is wrong (ORCH-confirmed).** :196 "(A, C, and B unless B's code also uploads evidence)". Uploading evidence fixes only X1. X2 (scratch reclaimed only on `ok`), X3 (a deferred region has no `.npz`, so it is recomputed on every re-fire) and X4 apply to B regardless. The heading tilts toward B.
3. **Option B's readings are one-sided.** :146 gives "*READING:* no." with three supporting bullets and no counter-reading, while A gets two competing readings (:125-131). :156-157 "the mechanism for this class is already established for 00057" stretches n=1 to "this class", and P5 (:63-66) itself says the second case is predicted.
4. **The structure leaks the private recommendation** (A + R4-COVERAGE-style obligation with enforcer, `STATE.md:52`): :133-134 "no registered disclosure obligation or enforcer yet", :209 "R4-COVERAGE has one", :218 the only precedent question.
5. **Option E overstates the posted fence.**
   - :190 "The criterion is unchanged and fenced (T8)". T8/trsx5:49 fences only "choosing the occlusion criterion to obtain a particular fine-mapping result", and mk7ze P302-305 separates that from recalibration.
   - :190-191 cites osf_deviations.md:670-671 ("NO PREDICATE CHANGE … calibrate-to-pass at n=1") without the "DRAFTED — NOT POSTED" label used at :65/:151. The same label is missing at :168.
   - The heading "(listed for completeness)" is a framing cue.
6. **Option D mis-describes the deliverable.** :174-177 promises "a measured list of regions expected to raise" from "the existing pairwise-completeness scan … ~10.5 h".
   - The scan is anchor-relative, so the list needs the separate `pcs_panelwide_reclassify` pass, which is omitted. ⚠ CORRECTED 2026-09-16 23:16 by re-measurement: **1h53m was the 6-region RUN 1** (2026-09-01, 02:29:11Z→04:22:50Z, `260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md:13`; `STATE.md:479` calls it the 6-region / 1,011,893-row banked run). The **21-region reclassify is RUN 2**: launched 2026-09-02 18:26:17Z, written 21:07:03Z = **2h40m46s** (`260902-vsp-*/CONTENT-SPEC.md:10`), and "21 regions" there counts regions CARRYING ROWS, not the scan scope (`:17-18`: `region_ids_selected = 276`). The 48-min figure v1 cites belongs to the *pairwise-completeness scan*, a different instrument. Label every runtime with instrument + run + region count.
   - The cited mk7ze P88-89 describes the 21-region occlusion sample, not this scan.
   - :179 states D's "no amendment" as a flat conclusion where other options get a READING.
7. **Missing content a methodologist would expect.**
   - §1 (T1–T8) omits the retained fully-NaN-row → drop rule (trsx5:37; mk7ze P321), the only posted rule that disposes of NaN-bearing variants.
   - An operational `deferred_*` status not mapped to `BRANCH_AFR_OCC_DEFERRED` (the `deferred_infeasible_square` analogue) is folded into B instead of offered as its own option.
   - LOW omissions: a per-region pairwise-completeness pre-check at fire time (before hours of plink and ~57.6 GB of scratch); re-running on a different sample set, or sample-level QC (would need an amendment); the effect on downstream AFR fine-mapping / coloc denominators.
   - X1 omits that the excludelist and manifest also upload only `if ok:` — at c93e97b the `if ok:` is `:1102`, the excludelist block `:1114-1118`, the manifest `:1123-1128` (an earlier version of this file wrote ":1113-1128"); HEAD equivalents `:1245`, `:1257-1261`, `:1266-1271`, gate sidecar `:1277-1282`.
   - Remaining framing cues (LOW): §0 title "Premise corrections…" (:36) and :68 "not halt versus continue" pre-dismiss C. Option C's "the Stage B halt record already argues against this…" (:165). The C rate (:168-170, 1/21 → ≈13) omits the ledger caveat "this sweep could observe only one side / Production tests the rate on BOTH sides" (osf_deviations.md:680-682).
- **Gate:** Seth courier.

### B3. MEDIUM · NEW · D1, D4: `peak_ram_gib` is now plink-only
- The driver's largest load is in-process: `read_square_bin` → `np.fromfile` of the whole `.ld.bin` (`plink_ld_to_npz.py:205`), then `content_verify_npz`. That is ≈4·n_var² bytes: ≈36–39 GiB for region 1 and ≈53.6 GiB at the 120,000 ceiling.
- No column records it.
- `fire_verifier.check_peak_ram` ("Peak RSS must leave headroom on the VM", `fire_verifier.py:735`) now bounds plink only. Plink reserves about half of detected RAM (a real PLINK 1.9 run here printed "reserving 96221 MB"), so on the 120 GiB VM the check can hardly fail.
- Under 3.11 the pre-fix number sometimes absorbed the driver's peak by accident.
- **Gate:** next Stage C fire (Stage B RAM gate / VM sizing) and COST-1.

### B4. MEDIUM (CODEX rated HIGH) · NEW on a PRE-EXISTING dedup · D1, D2, CODEX: the launcher's first real run would be the unattended Stage C
- Stage A/B regions skip, so Stage C (no `--fail-fast`, 11 days unattended) is the first real launcher run on the VM.
- The VM's `python3` version is UNRECORDED in any as-received record (ORCH grep: 0 hits). The launcher binds `os.waitstatus_to_exitcode` (3.9+) at `run_native_ld_panel.py:194`.
- An inherited SIGCHLD=SIG_IGN makes every call raise `SubprocessError: … exited 0 without a valid report` (D2 measured; `os.wait4` raises ChildProcessError at `:228`). The old `subprocess.run` silently returned 0. ⚠ SCOPE CORRECTED 2026-09-16 23:27 (vqr planner, ORCH-reproduced): GNU coreutils 8.32 `timeout` resets SIGCHLD to SIG_DFL before exec, so this hazard does NOT reach the Stage C fire command (which runs under `timeout`). Measured ignored-bit with the parent ignoring SIGCHLD: bare python3 = 1, `nohup python3` = 1, `timeout 5 python3` = 0, `timeout 5 nohup python3` = 0, `nohup timeout 5 python3` = 0 (control, parent not ignoring: 0). The LIVE exposure is therefore STEP 8 (Stage A), STEP 9 (Stage B) and every bare `python3 src/python/…` invocation including the `fire_verifier.py` gate runs — plus any VM whose coreutils differs. Keep the check; state this scope, do not overclaim.
- An odd `sys.executable` fails closed with an opaque message.
- Any of these errors every region, and panel rows are FIRST-ROW-WINS (`run_native_ld_panel.py:793-794`, `if str(out_row["region_id"]) in set(existing["region_id"]…): return`, ORCH-confirmed), so the error rows survive a re-fire (the `.npz` would bank but its row is lost).
- **Cheap precondition** in the fire shell after `export PATH`:
  - `python3 -V` (≥3.9)
  - `python3 -c 'import sys;sys.path.insert(0,"src/python");import run_native_ld_panel as r;print(r._run_plink(["plink1.9","--version"]))'`
  - the SIGCHLD bit (0x10000) of `SigIgn` in `/proc/self/status` must be 0.
- **Gate:** next Stage C fire.

### B5. MEDIUM · PRE-EXISTING · D1: pre-fix and post-fix `peak_ram_gib` are indistinguishable in the bucket panel TSV
- Rows: 00001 = 30.6591, 00017 = 2.9689, 00040__sub14 = 26.5745 (ok rows that will skip), 00057 = 26.5745 (error row, never replaced).
- No code-version column; nothing enforces "use only post-fix values".
- **Gate:** COST-1 / publication.

### B6. HIGH per D3 (unmeasured on VM) · PRE-EXISTING, newly surfaced · D3, ORCH: the runbook's SIGHUP claim is false for the committed command form
- `260812-ox1-AGENT-PROMPT.md:413` "nohup survives browser disconnects"; `260812-ox1-BROWSER-PASTE.md:544` the same, citing `.claude/skills/aou-ld-pipeline/SKILL.md:27` invariant 3; `260812-ox1-READY-TO-FIRE.md:330` similar.
- **ORCH measurement 2026-09-16 on NCSU (GNU coreutils 8.32), stand-in child:**
  - `nohup timeout 60 python3 …`: SIGHUP to the timeout pid kills the child, and so does SIGHUP to its group.
  - `timeout 60 nohup python3 …`: the child SURVIVES both.
  - Expiry (rc 124) still kills the child for plain `timeout`, form A and form B alike.
- **ORCHESTRATOR DECISION (Carter delegated it):** adopt form B, `timeout 312h nohup python3 …`, plus a 5-second in-perimeter property check on the VM (its coreutils version is unmeasured). **Form B does NOT trade the backstop for survival** (vqr planner, measured): `timeout 6 nohup …` HUP'd at t≈2 s left launcher and child alive at t+1 s and both DEAD past the cap at t+9 s. `ps -o comm= -p $!` prints `timeout` under BOTH forms, so the runbook's printed fire PID semantics are unchanged.
- `setsid` rejected: in an interactive (job-control) shell it forks, so `$!` would not be the fire PID.
- **Gate:** next Stage C fire.

### B7. MEDIUM · PRE-EXISTING · CODEX: the Stage B runbook claims RAM lands "either way"
- `260812-ox1-BROWSER-PASTE.md:386` "(`wall_min` / `peak_ram_gib` land in the panel TSV either way)" is false when plink itself fails: `_run_plink` raises before `result["peak_ram_gib"]` is assigned (`run_native_ld_panel.py:1159-1161`), leaving None.
- `m2_region_00071`'s worst-case RAM would be lost exactly when it matters (disk/RAM failure).
- **Gate:** next Stage C fire / COST-1.

### B8. MEDIUM · PRE-EXISTING · D4: the trsx5 ledger entry has no resolution pointer
- `.planning/osf_deviations.md:190-192` "ADJUDICATED 2026-08-14 — the posted trsx5 body is TRUNCATED … The fire is HELD"; :254 "UNEXPLAINED THIRD BODY"; :325 "None of (1)-(6) has been actioned".
- `grep "08-17|gate-released|260817"` on the ledger gives 0 hits.
- The resolution exists at `.planning/DECISIONS.md` `DEC-2026-08-17-trsx5-gate-released` (~:2030-2070). The oyq DEC cross-refs send readers to the ledger entry.
- **Gate:** OSF deviation log / publication-disclosure.

### B9. MEDIUM/LOW · NEW · D3, D4, CODEX: STATE.md's own slips
- `STATE.md:39` "GREEN in default, `--source` and `--live` modes" vs `:78` "`--live` goes RED 31/318" (undated contradiction). ⚠ CORRECTED 2026-09-16 23:08 by re-measurement: `grep -n '31/318' .planning/STATE.md` returns exactly one line, **78** (an earlier version of this file said :76, which is the SIGHUP bullet). Re-derive every line number in this file before using it.
- `:40/:48/:49` code citations (`run_native_ld_panel.py:1144-1146`, `:1278`, `:923-939`, `:961-965`/`:1129-1139`, `:1153`) carry no basis. At HEAD they are `:1287-1289`, `:1421`, `:1066-1082`, `:1104-1108`/`:1272-1282`, `:1296`.
- `:57` flags only `HANDOFF.json resume_on_reconnect[1]` (under-scoped; see B1).
- Headings still read open: `:59` "RAM-1 — agent-doable now", `:82` "…CODE-pinned, so docstring edits are free", `:88` "**In progress as `quick-260916-oyq`** … executing after this close-out".
- `:89` "(+31 / +28 below the notice)" is wrong below the second insertion. condition_ld_matrix.py shifts +31 for lines 3–124 and +37 from 125 (:153→:190, :200→:237, docstring :130→:167). write_conditioned_ld_npz.py shifts +28 for 4–85 and +29 from 86.
- `:89` "name the retained :35/:37/:39 rules" is wrong twice over (re-measured 2026-09-16 23:26): the tokens `:35`/`:37`/`:39` appear in NEITHER module. `condition_ld_matrix.py:19-21` names the three retained rules BY CONTENT ("the fully-NaN-row drop rule …, the PSD regularization methods, and the raw-panel NaN-raise contract"); `write_conditioned_ld_npz.py`'s notice does NOT name the retained rules at all.
- Frontmatter still says `last_activity: "2026-09-02 (LATEST)"` / `last_updated 2026-09-02T01:35`, and the frontmatter comment says "condition_ld_matrix.py … git-diff EMPTY" (now `37 0`).
- `STATE.md:2223-2226` has four "(prior) … (latest)" lines.
- **Gate:** next session resume.

### B10. LOW · NEW · D3, D4: record slips and missing records
- **SUMMARY/VERIFICATION as-of statements now false:** ocb-SUMMARY:48 "PLAN, this SUMMARY and STATE.md are NOT committed"; ocb-VERIFICATION:135 "not pushed (ahead 4)"; oyq-SUMMARY:37 "Not pushed". ocb-SUMMARY:392 names the wrong benchmark writer; the unconditional one is `test_no_whole_parent_dense_materialization` (`tests/m3/test_sparse_parent_benchmark.py:54-138`). oyq-VERIFICATION:26 line counts are off by one (deltas agree).
- **RAM-1 has no `DEC-*` entry** (a Carter decision changing measurement on the fire path).
- **Blanket freeze claims stay uncorrected:** `tests/m3/test_source_freeze_pins.py:15` "Every pin here is a CODE pin" (directly above its caveat); `tests/m3/source_freeze.py:9-10` "Correcting a wrong comment in a frozen file therefore costs **nothing**"; `HANDOFF.json` freeze_state. All remain false for `plink_ld_to_npz.py` and `occlusion_span_filter.py`. (Test-file prose changes are out of scope for a records-only task; record only.)
- **Function-docstring notice nuance:** `condition_ld_matrix.py:159-160` "trsx5 retains the fully-NaN-row drop rule that this raise directs". In production the retained rule is carried out by `--mac 1` plus the raw NaN-raise, not by this module. (Code-adjacent docstring; record only in this task.)
- **Orchestrator probe values never banked:** STATE.md:62-63 and memory give 413,932 KiB (3.9 fork, memory HELD) and 522,748 KiB (3.11 vfork, memory FREED) — the orchestrator's own 2026-09-16 probe, run in session scratch and not banked. The banked planner measurements are `ocb-PLAN.md:112` = **523,060 KiB (3.11, freed)** and `:113` = **413,992 KiB (3.9, held)** — note the line order is 3.11 first. (An earlier version of this file listed them transposed against their lines.) Label them as orchestrator probe values, or cite the banked ones.
- **Gate:** none / next session.

### B11. LOW · NEW · D1, D2, CODEX: operational notes for the runbooks
- **Launcher-only SIGKILL / OOM orphans plink:** the region records `error:`, the orphaned plink keeps running while the next region's plink starts (two concurrent plinks). Nothing is recorded ok by mistake and nothing runs twice.
- **`pgrep -f plink1.9` / `pkill -f` now also match the launcher** (argv contains the plink argv; the launcher's lower PID is listed first); `pgrep -x plink1.9` matches only plink.
- **`-I` can add `LC_CTYPE=C.UTF-8`** to plink's env ONLY in the `LANG=C` **and** `PYTHONCOERCECLOCALE=0` case (vqr re-measured on 3.11.15: isolated mode implies `-E`, so the opt-out is ignored; with the variable unset the driver already coerced before RAM-1, so nothing changed there).
- **The launcher error messages for `sys.executable = ""`/`None` do not name the launcher.**
- **Gate:** none (runbook note).

### B12. LOW · NEW · D2: tcujq enforcer false-RED classes (not timebombs)
- Plain substring match on non-.py files (`tests/m3/test_tcujq_withdrawal_notices.py:251` `if stem in text:`).
- Any unreadable tracked pipeline file (deleted from the working tree only, non-UTF-8, newer syntax) → FAILED (`:240`).
- Minimum counts (`:444-445`, ≥150 py / ≥100 other) currently 187/161, with `src/legacy` supplying 69/68 (archiving it would trip them).
- Untracked files are invisible (declared in the docstring).
- **Gate:** none (future spurious merge block).

### B13. LOW · PRE-EXISTING · CODEX: textual `nan` in the verifier
- `fire_verifier` fails OPEN on a textual `nan` `peak_ram_gib` (`fire_verifier.py:225` float parse; `:745` `if peak_gib > limit:`). The producer no longer emits NaN.
- **Gate:** none.

### B14. LOW · PRE-EXISTING-AGGRAVATED · D2: `READY-TO-FIRE.md:5-8` is stale
- It still claims later commits are `.planning`-only ("0 files under `src/`, `tests/`"). ⚠ WORSE THAN STATED (vqr measured): `git diff --name-only 5284505 HEAD -- src tests config Snakefile` at 621701c = **19 files (9 under src/python/, 10 under tests/m3/)**, not just the two commits named; the claim's "0 under `config/`, `Snakefile`" half is still TRUE.
- The VM clone must be at or after the new fixes, so the runbook's clone target / `git pull` expectation must be updated. HANDOFF memory rule: push NCSU before any AoU clone fire.
- Line-number citations of the driver in src/test comments (e.g. `fire_verifier.py:703` → `:1161`) were already wrong and are now a further +143 off.
- **Gate:** next Stage C fire.

---

## C. Gate binding summary
- **Merge / push (done):** nothing blocks.
- **Next session resume:** B1, B9, B10.
- **Seth courier:** B2 (draft v2 needed), plus the B1 halt-record annotation (the draft cites that file).
- **Next Stage C fire:**
  - B4 (fire-shell smoke + SIGCHLD + `python3 -V`)
  - B6 (SIGHUP form B + VM property check)
  - B3 (plink-only RAM reading rule)
  - B7 ("either way")
  - B14 (clone target / stale "src unchanged")
  - B11 (runbook notes)
- **COST-1 / publication:** B5, B8, B3.
- **None:** B12, B13.

## C-bis. Checker defects found while planning v2 (2026-09-16 23:16, vqq planner)

- **`c-ast:S2` in `260916-kht-verify.py` is GREEN FOR THE WRONG REASON.** It asserts "innermost def of `RN:1144` == `process_region`". At HEAD line 1144 is an unrelated comment that still falls inside the same long function, so the +143 shift does not turn it red — a line-number proxy too coarse to catch the drift it exists to catch. (v1's `:723` and `:866` citations DO land in the wrong function at HEAD.) v2's anchors must be AST-located on symbol/statement identity, never a bare line number.
- **The "+143 uniform shift" is a coincidence, not a rule.** Every `git diff -U0 c93e97b HEAD` hunk for `run_native_ld_panel.py` sits at c93e97b lines 184-203 and v1's lowest citation is `:723`; that is the only reason one offset fits all. Re-locate per claim — never apply an offset (same failure mode as B9's wrong "+31 / +28").

## C-ter. Tooling gotchas found while planning (2026-09-16)

- **gsd-tools' frontmatter extractor takes the LAST `---`-delimited block in a file**, so a bare `---` horizontal rule anywhere in a PLAN body silently zeroes the frontmatter (`valid:false`, `present:[]`) while PyYAML parses it fine. Use `***` for body dividers. Affects any GSD doc using `---` as a divider (vqr planner hit it).
- **The interactive `grep` is ugrep**, which ERRORS on an ERE back-reference that `/usr/bin/grep` accepts — a verify command that works in a script can fail spuriously when pasted interactively, and vice versa (vqq planner hit it; see memory `reference_interactive_grep_is_wrapper_scripts_get_gnu`).
- **`guk-verify.sh fire` F8 is RED on purpose.** Its missing tokens are the WITHDRAWN single-condition ceilings (`0.0005` / `60.0` / `51.2`); turning F8 green would reintroduce a withdrawn pre-registration figure onto the fire surface. Compare FAIL LISTS, never exit codes, and treat a disappearing F8 as a STOP (vqr).

## D. Codex raw review (verbatim)
See `codex-review.md` beside this file. Its findings map to: HIGH python floor → B4; MEDIUM launcher SIGKILL orphan → B11; MEDIUM "either way" → B7; LOW NaN fail-open → B13; MEDIUM HANDOFF stale → B1; LOW STATE in-progress label → B9; LOW AoU full-suite hazard → D2 OK-VERIFIED (named-id gate); LOW draft stale citations → B2.1; LOW freeze blanket claim → B10.
