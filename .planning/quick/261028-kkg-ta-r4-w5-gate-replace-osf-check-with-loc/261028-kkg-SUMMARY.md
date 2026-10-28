---
phase: quick-261028-kkg
plan: 01
subsystem: ta-r4 production gate
tags: [ta-r4, gate, git-lock, osf, snakemake]
requires: [ta-r4 W2c complete (ac4e5452)]
provides: [ta_r4.r4_lock_gate, W4b-T3 lock_sha schema, DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf]
affects: [Snakefile.ta_r4, bin/r4_fire.sh, ta-r4 W3d..W7 plans]
tech-stack:
  added: []
  patterns: [offline git-lock gate memoized per (realpath, HEAD), fixture lock under pytest tmp_path]
key-files:
  created:
    - src/python/ta_r4/r4_lock_gate.py
    - tests/ta_r4/test_lock_gate.py
  modified:
    - src/python/ta_r4/signoff.py
    - Snakefile.ta_r4
    - bin/r4_fire.sh
    - src/snakemake/rules/ta_r4_finemap.smk
    - src/snakemake/rules/ta_r4_coloc.smk
    - tests/ta_r4/fixtures/make_fixture_repo.py
    - tests/ta_r4/fixtures/build_toy_workflow.py
    - tests/ta_r4/test_signoff.py
    - tests/ta_r4/test_signoffs.py
    - tests/ta_r4/test_snakemake_toy_e2e.py
    - tests/ta_r4/test_frozen_script_armed_e2e.py
  deleted:
    - src/python/ta_r4/r4_osf_gate.py
    - tests/ta_r4/test_osf_gate.py
decisions:
  - "DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf: ta-r4 production is gated by the git lock; OSF not required; R4 wording 'analysis locked in commit <sha> before production'"
metrics:
  completed: 2026-10-28
  commits: 3
---

# Quick 261028-kkg: ta-r4 production gate is now the offline git lock

`ta_r4.r4_lock_gate` replaces the OSF gate. Production passes only when all of these hold: a tracked, committed `$P/R4-LOCK.json` names a `lock_sha` that is an ancestor of HEAD; the three configs are `locked: true` at that sha; no LOCKED_PATHS file has drifted (committed, working copy or untracked); and Carter's W4b-T3 sign-off records the same `lock_sha`. The gate makes no network calls, reads no environment variables and has no bypass. `repro` is unchanged.

## Commits

| Task | Commit | Subject |
|------|--------|---------|
| 1 | 26b358e2 | feat(ta-r4): offline git-lock production gate (r4_lock_gate) + W4b-T3 lock_sha schema |
| 2 | b119c34e | refactor(ta-r4): production gate uses the git lock, OSF gate removed |
| 3 | d213c86d | docs(ta-r4): record the git-lock gate decision (DEC-2026-10-28) |

These were not pushed: the orchestrator pushes after its docs commit, which includes this PLAN and SUMMARY.

## Evidence

- **RED.** Before the module existed, test_lock_gate.py failed at collection with `ImportError: cannot import name 'r4_lock_gate' from 'ta_r4'`. test_signoff.py gave `2 failed, 36 passed`: `posted: yes` was still accepted and a valid `lock_sha` reply was rejected.
- **Unit negative control.** With checks (g) and (h) blinded, `-k drift` gave `3 failed, 1 passed`. The 1 pass is the edit outside LOCKED_PATHS, which is supposed to pass. After restoring the file (`cmp` identical) and clearing `__pycache__`, the result was `4 passed`.
- **End-to-end negative control.** In a fixture repo the production `r4_gate_probe` dry-run passes after `write_fixture_lock`. An uncommitted edit to `arms.py` then makes it fail with `LockGateError ... drifted`.
- **check_lock_record negative control.** Blinding the lock_sha equality made `test_tracked_lock_record_requires_matching_w4b` fail. After restoring it, the test passed.
- **Reconciliation of tests/ta_r4 by id** (quick + heavy; LSF 430489 before, 430615 after):
  - Before: 390 passed + 4 skipped.
  - Removed: 55 ids, of which 52 are from test_osf_gate.py and 3 were replaced (W4b-T3 `posted: no`, `test_real_repo[check_osf_sentinel]`, `test_tracked_osf_sentinel_requires_w4b`).
  - Added: 51 ids (45 test_lock_gate, 4 test_signoff, 2 test_signoffs).
  - 390 − 55 + 51 = 386 passed. The same 4 tests are skipped for the same W5a/W5b reasons. No other test changed outcome.
- **FULL:** 1814 passed, 50 skipped, 0 failed = 1864 ids, against 1868 / 1818 / 50 / 0 at W2c. Compared with full_W2c.xml by id, the only differences are the same −55/+51; 0 others changed.
- **Other checks:** Pins: 39 passed. `sparse_parent_benchmark.tsv` was restored. `run_susie_rss.R` has a 0-line diff.
- **Real repo:**
  - `r4_lock_gate check --stage production` exits 1 with `LockGateError: (a) lock record absent: ...R4-LOCK.json`; `--stage repro` exits 0.
  - `bash bin/r4_fire.sh production A3_1kg -n r4_gate_probe` exits 1 with the same message.
  - `bash bin/r4_fire.sh repro repro_routeC -n r4_gate_probe_repro` exits 0.

## Deviations from Plan

1. **[Rule 3] test_signoffs rewrite moved from Task 2 into Task 1.** The W4b-T3 schema change broke the old `posted: yes` fixture test, so Task 1 could not end green without it.
2. **[Rule 1] Fixture `.gitignore` now ignores `__pycache__/`.** Without it, Snakemake jobs in the fixture repo would create untracked `__pycache__` files under `src/python/ta_r4`, which the gate correctly treats as drift.
3. **[Rule 1] Toy e2e negative control updated.** `test_negative_control_missing_manifest_row_fails_at_receipt` failed in the first after-run. Its uncommitted edit to `$P/manifests/panels_*.tsv` is a locked path, so the lock gate now refuses first. The test now checks for that refusal, then commits the edit, re-locks with `write_fixture_lock` (which now replaces the fixture sign-off), and reaches `LD_RECEIPT_REFUSED` as before. The first after-run (LSF 430602) was killed and rerun as 430615.
4. **`write_fixture_lock` uses a regex replacement of the `locked:` line instead of yaml load/dump.** This keeps the other config values byte-identical.
5. **Order of steps.** The real-repo fire-script checks (Task 2 step 8) ran after the Task 2 commit. Before it, the fire script's dirty-tree check would have refused first.
6. **Task 3 extras.** "Before the OSF post" wording in PLAN-INDEX upgrades 1–2, W3d, W3e and W7 now reads "before the lock (W4b)". Task 3 has no PLAN/SUMMARY in its commit and nothing was pushed, per the orchestrator's instruction.

## Known Stubs

None.

## Self-Check: PASSED

- The new files exist: `r4_lock_gate.py` and `test_lock_gate.py`. `r4_osf_gate.py` is gone, and `find_spec` returns None for it.
- Commits 26b358e2, b119c34e and d213c86d are present in `git log`.
