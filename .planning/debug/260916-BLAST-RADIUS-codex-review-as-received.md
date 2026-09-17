Tests not run: read-only workspace, and targeted pytest can write cache/temp artifacts.

- `[HIGH] [NEW]` Launcher has a new Python-version hard floor that old `subprocess.run(cmd)` did not — evidence `src/python/run_native_ld_panel.py:194` (`exitcode_of = os.waitstatus_to_exitcode  # bound BEFORE the spawn`) and `.planning/STATE.md:74` (`the launcher needs ≥3.9`) — if the AoU VM’s `python3` is 3.8, Stage C fails before first plink although the prior implementation would run — blocks next Stage C fire.

- `[MEDIUM] [NEW]` Unexpected launcher death can orphan plink — evidence `src/python/run_native_ld_panel.py:304` (`with subprocess.Popen(`) and `src/python/run_native_ld_panel.py:218` (`signal.signal(signal.SIGTERM, _kill_child)`) — only handled SIGTERM/SIGINT trigger child kill; if the tiny launcher is SIGKILL/OOM-killed, driver gets no valid report and raises while plink can continue detached, making retry/double-compute possible — blocks next Stage C fire.

- `[MEDIUM] [PRE-EXISTING]` Stage-B runbook falsely says RAM lands “either way” on worst-case failure — evidence `.planning/.../260812-ox1-BROWSER-PASTE.md:386` (`wall_min / peak_ram_gib land in the panel TSV either way`) versus `src/python/run_native_ld_panel.py:963` (`"wall_min": None, "peak_ram_gib": None`) and `src/python/run_native_ld_panel.py:1160` (`wall_min, peak_ram_gib = _run_plink(cmd)`) — if `00071` fails in plink/OOM, no peak is recorded, so the cost gate lacks the worst-case RAM number — blocks next Stage C fire.

- `[LOW] [PRE-EXISTING]` `fire_verifier` fails open on textual `nan` in `peak_ram_gib` — evidence `src/python/fire_verifier.py:225` (`return cast(float(s)) if cast is int else cast(s)`) and `src/python/fire_verifier.py:745` (`if peak_gib > limit:`) — a status-ok panel row with `peak_ram_gib=nan` is parsed as float NaN, `NaN > limit` is false, and the check returns PASS; `_run_plink` does not currently produce this, but a corrupted TSV would pass — blocks next Stage C fire.

- `[MEDIUM] [NEW]` The active handoff is stale on all three new workstreams — evidence `.planning/STATE.md:26` (`HANDOFF.json ... AUTHORITATIVE for resume`), `.planning/HANDOFF.json:259` (`Agent DRAFTS the options`), `.planning/HANDOFF.json:260` (`Fix with Popen + os.wait4`), `.planning/HANDOFF.json:261` (`docstring edits are FREE`) — future resume from the declared authoritative handoff can repeat completed work or apply the falsified RAM fix — blocks next Stage C fire.

- `[LOW] [NEW]` `STATE.md` itself still labels the completed tcujq task as in progress — evidence `.planning/STATE.md:88` (`In progress as quick-260916-oyq`) versus `.planning/STATE.md:2662` (`tcujq CORRECTED`) — a future session can treat closed source edits as still open — blocks none.

- `[LOW] [NEW]` New RAM tests are full-suite AoU false-fail hazards, though the pre-fire named pytest does not collect them — evidence `tests/m3/test_run_plink_peak_rss.py:574` (`pytest.fail("PRECONDITION: GNU timeout not on PATH`) and `tests/m3/test_run_plink_peak_rss.py:636` (`grep "^SigIgn" /proc/self/status`) and `tests/m3/test_run_plink_peak_rss.py:661` (`hold = int(sys.argv[2])`) — a full `tests/m3` run on an AoU VM missing GNU `timeout`, hiding `/proc`, or not satisfying the wait4 premise can fail for environment rather than code; the runbook’s pre-fire gate only runs named occlusion tests — blocks none.

- `[LOW] [NEW]` Stage-C options draft line citations are stale after RAM-1 unless couriered with the basis commit — evidence `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md:20` (`Code at HEAD c93e97b`) and `.planning/STATE.md:78` (`After 9a3eb97 those 24 citations ... sit +143 lines later`) — sending the draft without “read code at c93e97b” makes current-HEAD line lookups misleading — blocks next Stage C fire.

- `[LOW] [NEW]` Source-freeze test prose still contains a false blanket claim — evidence `tests/m3/test_source_freeze_pins.py:15` (`Every pin here is a CODE pin`) and `tests/m3/test_source_freeze_pins.py:20` (`ONE byte-level assertion remains`) — a future editor could rely on the first sentence and wrongly expect docstring edits in the remaining byte-pinned files to pass — blocks none.

Claims I tried to break and could not:

- PATH lookup under `-I -S`: launcher uses `subprocess.Popen(argv)` without overriding `env`, so `PATH="$HOME/bin:$PATH"` still reaches `plink1.9`.
- Wrong-number paths in `_run_plink`: malformed/absent reports raise `SubprocessError`; exec failure raises `OSError`; nonzero plink raises `CalledProcessError`. I found fail-closed behavior, not fabricated 0/None/stale numbers.
- `peak_ram_gib=None` for skipped/error rows: Stage B only checks `status == "ok"` rows, and `None` fails closed.
- tcujq notices: the quoted withdrawal matches posted trsx5 line 19; retained PSD/full-row-drop/raw-raise statements match lines 35/37/39; I did not find a false notice sentence.
- tcujq enforcer vacuity: it anchors posted body size/md5, has AST docstring checks, pipeline-scan floors, positive controls, and negative controls; not just grep.
- Pre-fire pytest collection: the posted pre-fire gate runs three named occlusion tests, not the new RAM test file.
