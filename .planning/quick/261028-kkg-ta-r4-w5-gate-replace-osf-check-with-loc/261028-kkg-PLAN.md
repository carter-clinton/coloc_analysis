---
phase: quick-261028-kkg
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/python/ta_r4/r4_lock_gate.py            # new (Task 1)
  - tests/ta_r4/test_lock_gate.py               # new (Task 1), heavy dry-runs added (Task 2)
  - src/python/ta_r4/signoff.py                 # W4b-T3 schema
  - tests/ta_r4/test_signoff.py
  - tests/ta_r4/fixtures/make_fixture_repo.py   # write_fixture_lock helper
  - src/python/ta_r4/r4_osf_gate.py             # git rm (Task 2)
  - tests/ta_r4/test_osf_gate.py                # git rm (Task 2)
  - Snakefile.ta_r4
  - src/snakemake/rules/ta_r4_finemap.smk
  - src/snakemake/rules/ta_r4_coloc.smk
  - bin/r4_fire.sh
  - tests/ta_r4/fixtures/build_toy_workflow.py
  - tests/ta_r4/test_snakemake_toy_e2e.py
  - tests/ta_r4/test_frozen_script_armed_e2e.py
  - tests/ta_r4/test_signoffs.py
  - .planning/DECISIONS.md
  - .planning/osf_deviations.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-VALIDATION.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3d-estimators-and-branch-classifier-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3e-qtl-harmonize-and-group-runner-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4b-amendment-final-and-posting-gate-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5a-eur-production-fits-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5b-eur-production-coloc-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5c-afr-secondary-and-simulation-run-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W6-qtl-layer-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W7-aggregation-figures-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/HANDOFF.json
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "`python -m ta_r4.r4_lock_gate check --stage production` exits 1 on the real repo today with `LockGateError: (a) lock record absent`; `--stage repro` exits 0"
    - "Production passes only when: the git-tracked, committed lock record names a lock_sha that is an ancestor of HEAD; all three lockable configs carry `locked: true` at lock_sha; no LOCKED_PATHS file differs from lock_sha in HEAD, in the working copy, or as an untracked file; and a valid, tracked, committed W4b-T3 sign-off records the same lock_sha"
    - "The gate makes no network call, reads no environment variable, and has no bypass parameter; tests prove it with socket/urllib monkeypatched to raise and an AST import scan"
    - "Negative control seen: blinding the drift check turns the drift tests RED; restoring it turns them green again (byte-identical restore)"
    - "No code path calls the OSF API or writes a receipt: `ta_r4.r4_osf_gate` is no longer importable; bin/r4_fire.sh runs `r4_lock_gate check` instead of `verify-online`"
    - "tests/ta_r4 (quick + heavy) and FULL are green; every test id is reconciled by name against the pre-change run (only removed: test_osf_gate.py ids; only added: test_lock_gate.py / test_signoff(s).py ids)"
    - "DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf is recorded; PLAN-INDEX, CONTEXT, VALIDATION and the W3d/W3e/W4a/W4b/W5a/W5b/W5c/W6/W7 plans make OSF posting optional and never a W5 precondition; W4b still makes lock commit A and writes the lock record"
  artifacts:
    - path: "src/python/ta_r4/r4_lock_gate.py"
      provides: "offline git-lock production gate + CLI (check, paths)"
      exports: ["LOCK_RECORD_REL", "LOCKED_PATHS", "LockGateError", "check_lock_gate", "read_lock_sha"]
    - path: "tests/ta_r4/test_lock_gate.py"
      provides: "RED-first gate tests, no-network proof, Snakefile dry-run refusals/passes"
    - path: ".planning/DECISIONS.md"
      contains: "DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf"
  key_links:
    - from: "Snakefile.ta_r4 gate_input / repro_gate_input"
      to: "ta_r4.r4_lock_gate.check_lock_gate"
      via: "import at DAG time; production rules take LOCK_RECORD_REL as input"
      pattern: "from ta_r4.r4_lock_gate import"
    - from: "r4_lock_gate.check_lock_gate"
      to: "signoffs/W4b-T3.yaml"
      via: "ta_r4.signoff.verify_signoff + lock_sha equality"
      pattern: "verify_signoff"
    - from: "bin/r4_fire.sh (production)"
      to: "ta_r4.r4_lock_gate check --stage production"
      via: "submit-host fail-fast before exec snakemake"
      pattern: "r4_lock_gate check"
---

<objective>
Replace the OSF requirement on the ta-r4 production gate with an offline git-lock check, per
Carter's locked decision of 2026-10-28: production is allowed only when the W4b lock commit is an
ancestor of HEAD and no locked analysis file differs from it. No network, no token, fails closed,
no environment-variable bypass. `repro` is unchanged.

Purpose: W5 must not depend on OSF. The public claim for R4 becomes "analysis locked in commit
<sha> before production", not "pre-registered on OSF". Earlier OSF registrations are untouched.
Output: `ta_r4.r4_lock_gate` + tests, call sites switched, OSF gate deleted, records amended, pushed.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@./CLAUDE.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/python/ta_r4/r4_osf_gate.py
@tests/ta_r4/test_osf_gate.py
@tests/ta_r4/test_signoffs.py

Repo root R=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis, branch m3-W2-aou-deltas, base HEAD ac4e5452.
P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 ; SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
QUICK="$PY -m pytest tests/ta_r4 -q -m 'not r4_heavy'" ; HEAVY="$PY -m pytest tests/ta_r4 -q -m r4_heavy -rs"
FULL="$PY -m pytest tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q" (prior FULL at W2c: 1868 ids / 1818 passed / 50 skipped / 0 failed)
After any FULL run: `git restore tests/m3/sparse_parent_benchmark.tsv`.

<lock_mechanism_finding>
Investigated (grep over $P plans, src/python, tests/ta_r4, Snakefile.ta_r4, rules, bin/r4_fire.sh):
NO coded lock mechanism exists. What exists is only planned prose:
- W4b Task 1 makes "commit A" (`chore(ta-r4-W4b): lock pre-registration parameters`, the three
  configs with `locked: true`); its sha is only recorded in the LOG and cited in the amendment.
- W5a Task 1 step 2 is a manual `git merge-base --is-ancestor` + `git diff --stat <commit A> HEAD -- <path list>`
  that W5b/W5c/W6/W7 repeat "with this exact path set".
- `check_locks` (test_signoffs.py) ties `locked: true` configs to the W4a-T3 sign-off values; it
  is a test, not a gate, and knows nothing about a lock commit. `tests/m3/source_freeze.py::assert_code_frozen`
  pins a fixed git ref per symbol for Track B frozen files; it has no lock-record concept.
REUSE: the gate encodes W5a's path list verbatim as `LOCKED_PATHS` (so the manual step becomes code),
targets W4b's existing commit A as lock_sha, and reuses `ta_r4.signoff.verify_signoff` for Carter's
confirmation. No second lock mechanism is invented; `check_locks` stays as is.
</lock_mechanism_finding>

<lock_record_contract>
File: `$P/R4-LOCK.json` (LOCK_RECORD_REL), git-tracked, committed, no working-copy changes.
Body: a JSON object with key `lock_sha` = full 40-char lowercase hex sha of W4b commit A. Other keys ignored.
Writer: W4b Task 2 executor, immediately after commit A (the record cannot live in the commit it names).
Anti-fabrication (replaces the OSF API check): `signoffs/W4b-T3.yaml`, recorded only from Carter's
verbatim reply `carter-approved YYYY-MM-DD` + `lock_sha: <40-hex>`, must verify and its lock_sha must equal the record's.
LOCKED_PATHS (git pathspecs, from W5a Task 1 step 2, unchanged):
  src/snakemake/scripts/ta_r4, src/python/ta_r4, src/snakemake/rules/ta_r4_*.smk, config/ta_r4,
  Snakefile.ta_r4, bin/r4_fire.sh, src/legacy/region_analysis/scripts/run_susie_rss.R,
  src/snakemake/scripts/plink_ld_to_rds.R, src/snakemake/scripts/run_qtl_coloc.R,
  src/snakemake/scripts/ld_allele_join.R, src/python/assign_tiers.py, src/python/aggregate_qtl_coloc.py,
  src/python/harmonize_eqtl.py, src/python/harmonize_sqtl.py, src/python/ld_read_path.py,
  src/python/ld_panel.py, envs, $P/manifests/panels_*.tsv
The gate module itself is under src/python/ta_r4, so the gate (and this list) is frozen by the lock it enforces.
</lock_record_contract>

<interfaces>
Existing (src/python/ta_r4/signoff.py):
  SCHEMAS["W4b-T3"] = {"keys": {"posted": ("yes",)}}   # changes to {"lock_sha": GIT_SHA}
  rule constants TEXT, FLOAT, INT, SHA256, DATE, OSF_URL; _check_value(key, value, rule)
  record_signoff(cid, raw, *, min_date, signoff_dir=SIGNOFF_DIR, extra_required=(), today=None)
  verify_signoff(cid, *, signoff_dir=SIGNOFF_DIR, today=None) -> fields dict; raises SignoffError("WAIT: ...")
Existing call sites of the OSF gate (complete list, from grep):
  Snakefile.ta_r4:19  `from ta_r4.r4_osf_gate import SENTINEL_REL, check_osf_gate`; gate_input returns [SENTINEL_REL] for production
  src/snakemake/rules/ta_r4_finemap.smk:17, ta_r4_coloc.smk:5,25 (comments "OSF gate first")
  bin/r4_fire.sh:61-67 (DIRTY check message "the receipt binds HEAD"; verify-online; "Do not commit ... receipt head_sha")
  tests/ta_r4/fixtures/build_toy_workflow.py:222-247 (sentinel + verify_online fake fetch)
  tests/ta_r4/fixtures/make_fixture_repo.py:9,25,36 (SENTINEL_NAME)
  tests/ta_r4/test_snakemake_toy_e2e.py:118-127, test_frozen_script_armed_e2e.py:~271 (assert "OsfGateError" and "sentinel absent")
  tests/ta_r4/test_signoffs.py:SENTINEL_REL, check_osf_sentinel, test_tracked_osf_sentinel_requires_w4b
New (src/python/ta_r4/r4_lock_gate.py):
  LOCK_RECORD_REL = f"{PHASE_REL}/R4-LOCK.json"; SIGNOFF_REL = f"{PHASE_REL}/signoffs"
  LOCKABLE = ("coloc_priors", "decision_rules", "simulation"); LOCKED_PATHS: tuple[str, ...]; STAGES = ("repro", "production")
  class LockGateError(RuntimeError)
  read_lock_sha(repo) -> str          # checks (a)-(d)
  check_lock_gate(repo_root, stage) -> None   # repro: return; production: (a)-(i), memoized per (realpath, HEAD)
  _clear_cache()
  CLI: python -m ta_r4.r4_lock_gate check --stage {repro,production}  (exit 0 OK / 1 "LockGateError: ..." on stderr)
       python -m ta_r4.r4_lock_gate paths   (prints LOCKED_PATHS, one per line)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED-first tests, then the offline git-lock gate module and the W4b-T3 schema</name>
  <files>tests/ta_r4/test_lock_gate.py, src/python/ta_r4/r4_lock_gate.py, src/python/ta_r4/signoff.py, tests/ta_r4/test_signoff.py, tests/ta_r4/fixtures/make_fixture_repo.py</files>
  <behavior>
    Fixture: tmp_path git repo with `src/python/ta_r4/arms.py` stub and the three `config/ta_r4/*.yaml`
    with `locked: true`, committed as lock commit L; then R4-LOCK.json {"lock_sha": L} and a W4b-T3
    sign-off (record_signoff, raw `carter-approved <today>\nlock_sha: L\n`, min_date 2026-10-01) committed on top.
    - valid fixture, stage production → passes (positive control)
    - stage repro → None even with no record; unknown stage ("", "prod", "Production", None) → ValueError
    - (a) record absent → "lock record absent"
    - (b) record present, untracked → "lock record untracked"
    - (c) record tracked with working-copy edit → "lock record has uncommitted changes"
    - (d) not JSON / not an object / lock_sha missing / 7-char / uppercase → "lock_sha"
    - (e) lock_sha is a commit on a side branch (not ancestor of HEAD), and a non-existent sha → "not an ancestor of HEAD"
    - (f) lock_sha points at a commit where any of the three configs has locked: false → "not locked: true"
    - (g) committed drift: edit + commit `src/python/ta_r4/arms.py` after L → "drifted" and names the file
    - (h) working-copy drift: same edit uncommitted → "drifted" (working copy); a new untracked file
          `src/python/ta_r4/new_mod.py` → "drifted" (untracked); an edit OUTSIDE LOCKED_PATHS (e.g. README) → still passes
    - (i) W4b-T3 sign-off absent → "W4b-T3"; sign-off lock_sha != record → "W4b-T3 lock_sha"; sign-off untracked → "W4b-T3"
    - memo: second check on the same HEAD makes zero subprocess.run calls; a failure is not memoized
    - no network: monkeypatch `socket.socket.connect`, `socket.create_connection` and `urllib.request.urlopen`
      to raise; the valid fixture still passes; AST scan: module imports none of urllib, socket, http, requests
    - no bypass: AST scan finds no `os.environ` / `getenv`; setting OSF_*/R4_*/GATE_* env vars changes neither refusal nor pass;
      `check_lock_gate` signature is exactly (repo_root, stage)
    - CLI: `check --stage production` on the real repo exits 1 with "LockGateError" and "lock record absent" on stderr while
      $P/R4-LOCK.json is untracked/absent (conditional real-repo test, same shape as the old test_real_repo_state;
      when tracked, it asserts read_lock_sha succeeds); `paths` prints exactly LOCKED_PATHS
    - signoff: `carter-approved 2026-10-28\nlock_sha: <40 lowercase hex>` parses for W4b-T3; `posted: yes`, a 7-char sha and
      an uppercase sha all raise SignoffError("WAIT:...")
  </behavior>
  <action>
    0. Baseline before any edit: `cd $R && $PY -m pytest tests/ta_r4 -q -rA -p no:cacheprovider > <scratchpad>/ta_r4_before.txt 2>&1`
       (quick + heavy together; record the PASSED/SKIPPED/FAILED lines by id). `git status --porcelain` for
       files_modified must be empty; `git fsck --connectivity-only` clean.
    1. RED: write `tests/ta_r4/test_lock_gate.py` covering every behavior bullet (reuse the `git()` helper
       pattern and `_raises(repo, needle)` from test_osf_gate.py; autouse fixture calls `g._clear_cache()`).
       Add `write_fixture_lock(repo, *, locked=True)` to `tests/ta_r4/fixtures/make_fixture_repo.py`: sets
       `locked: <bool>` in the repo's three config yamls via yaml load/dump, commits them, writes R4-LOCK.json
       with that commit's full sha, records W4b-T3 via `record_signoff(..., signoff_dir=repo/SIGNOFF_REL)`,
       `git add` those two explicit paths, commits; returns the lock sha. Update the W4b-T3 cases in
       `tests/ta_r4/test_signoff.py` (replace the `posted: no` case with the three invalid replies above; add
       one valid parse). Run `$PY -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_signoff.py -q` and
       paste the failure summary (ImportError for ta_r4.r4_lock_gate + the schema failures) as the RED record.
    2. GREEN: in `signoff.py` add rule constant `GIT_SHA = "git_sha"` (`[0-9a-f]{40}` in `_check_value`) and set
       `SCHEMAS["W4b-T3"] = {"keys": {"lock_sha": GIT_SHA}}`. Create `src/python/ta_r4/r4_lock_gate.py`
       (new file; leave r4_osf_gate.py untouched in this task so every call site stays green). Docstring: two
       lines — what it checks, then "Fails closed. Offline: no network, reads no environment variables, no bypass."
       Implement checks in this order with the message prefixes `(a)`..`(i)`:
       (a)-(c) record exists / `git ls-files --error-unmatch` / `git status --porcelain` empty;
       (d) JSON object, `lock_sha` matches `^[0-9a-f]{40}$`;
       (e) `git merge-base --is-ancestor <sha> HEAD` rc 0;
       (f) for each LOCKABLE: `git show <sha>:config/ta_r4/<n>.yaml` parses and `locked is True`;
       (g) `git diff --name-only <sha> HEAD -- *LOCKED_PATHS` empty;
       (h) `git diff --name-only <sha> -- *LOCKED_PATHS` empty AND `git ls-files --others --exclude-standard -- *LOCKED_PATHS` empty;
       (i) W4b-T3 sign-off file tracked + clean, `verify_signoff("W4b-T3", signoff_dir=repo/SIGNOFF_REL)` succeeds
           (SignoffError → LockGateError), and its `lock_sha` == record.
       Memoize production checks with lru_cache keyed on (realpath, HEAD), as in r4_osf_gate. CLI per <interfaces>.
       No imports of urllib/socket/http/json-over-network, no `os.environ`.
    3. Run the tests to green. NEGATIVE CONTROL (required): copy r4_lock_gate.py to <scratchpad>, replace the (g)
       and (h) checks' bodies with `pass`, run `$PY -m pytest tests/ta_r4/test_lock_gate.py -q -k drift` and paste
       the RED count; restore from the copy, `cmp` the file against the copy (identical), delete `__pycache__`
       for ta_r4 (bytecode-cache trap), re-run → green. Record both outputs for the SUMMARY.
    4. Run $QUICK and `$PY -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_signoff.py tests/ta_r4/test_signoffs.py -q`.
       test_signoffs must still pass (W4b-T3 is not recorded in the real repo). Commit with explicit paths only:
       `feat(ta-r4): offline git-lock production gate (r4_lock_gate) + W4b-T3 lock_sha schema` (rationale in the
       commit body, not in the code). fsck before and after the commit; GPFS "invalid object / Error building trees" = STOP and report, never reset.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_signoff.py tests/ta_r4/test_signoffs.py -q && cd src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_lock_gate check --stage production; test $? -eq 1 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_lock_gate check --stage repro && echo LOCK_GATE_CLOSED_REPRO_OPEN</automated>
  </verify>
  <done>RED was observed before the module existed; every behavior bullet passes; the drift tests were seen RED with the drift check blinded and green after a byte-identical restore; the real repo refuses production with "(a) lock record absent" and passes repro.</done>
</task>

<task type="auto">
  <name>Task 2: Switch every call site to the lock gate, delete the OSF gate, reconcile the suite by name</name>
  <files>Snakefile.ta_r4, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, bin/r4_fire.sh, tests/ta_r4/fixtures/build_toy_workflow.py, tests/ta_r4/fixtures/make_fixture_repo.py, tests/ta_r4/test_snakemake_toy_e2e.py, tests/ta_r4/test_frozen_script_armed_e2e.py, tests/ta_r4/test_signoffs.py, tests/ta_r4/test_lock_gate.py, src/python/ta_r4/r4_osf_gate.py, tests/ta_r4/test_osf_gate.py</files>
  <action>
    Module choice: rename, no compat shim. Every importer is in-repo and enumerated in <interfaces>; a shim would
    keep a second, misleadingly named entry point to the production gate alive. Proof of removal is behavioural:
    a test asserts `importlib.util.find_spec("ta_r4.r4_osf_gate") is None`.
    1. `Snakefile.ta_r4`: import `LOCK_RECORD_REL, check_lock_gate` from `ta_r4.r4_lock_gate`; gate_input calls
       `check_lock_gate(Path(workflow.basedir), STAGE)` and returns `[LOCK_RECORD_REL]` for production; docstring
       "Offline lock gate at DAG time (memoized per process). Production rules take this as input."; repro_gate_input
       calls check_lock_gate(..., "repro"). In the two .smk files change "OSF gate" to "lock gate" in the comments only.
    2. `bin/r4_fire.sh`: keep the DIRTY check, change its message to "(production runs committed, locked code)";
       replace the verify-online line with `(cd src/python && "$PY" -m ta_r4.r4_lock_gate check --stage production)`
       (set -euo pipefail already aborts on rc 1); replace the receipt echo with
       "Do not commit locked paths until this fire ends: in-job gate checks re-diff them against the lock commit."
    3. Fixtures/e2e: `make_fixture_repo.py` ignores and asserts the absence of `R4-LOCK.json` (rename SENTINEL_NAME →
       LOCK_RECORD_NAME); `build_toy_workflow.py` drops the amendment/sentinel/fake-fetch/verify_online block and calls
       `write_fixture_lock(repo)` after committing the toy inputs (docstrings updated to "lock record + W4b-T3 fixture
       sign-off, under tmp_path only"). In `test_snakemake_toy_e2e.py` and `test_frozen_script_armed_e2e.py` the
       refusal assertions become `"LockGateError" in out and "lock record absent" in out`.
    4. Move the Snakemake dry-run tests from test_osf_gate.py into test_lock_gate.py (r4_heavy): fixture has no lock
       record; production `r4_gate_probe` refuses with LockGateError "lock record absent"; repro targets pass; after
       `write_fixture_lock(repo)` production passes; then an uncommitted edit to the fixture's
       `src/python/ta_r4/arms.py` makes the production dry-run refuse with "drifted" (end-to-end negative control).
       Add the find_spec test. Then `git rm src/python/ta_r4/r4_osf_gate.py tests/ta_r4/test_osf_gate.py`.
    5. `test_signoffs.py`: replace SENTINEL_REL/check_osf_sentinel with `LOCK_RECORD_REL` (import from r4_lock_gate)
       and `check_lock_record(repo)`: if the record is git-tracked → W4b-T3 must verify and its `lock_sha` must equal
       the record's lock_sha (else a problem string). Replace the fixture test: untracked → []; tracked without
       sign-off → problem; mismatched lock_sha → problem; matching → []. CHECKS uses check_lock_record.
    6. `grep -rn "r4_osf_gate\|verify_online\|verify-online\|OsfGateError\|OSF-R4-POSTED" Snakefile.ta_r4 src bin tests/ta_r4`
       → empty (supporting evidence only; the find_spec test is the enforcer).
    7. Suites: `rm -rf src/python/ta_r4/__pycache__ tests/ta_r4/__pycache__`; run
       `$PY -m pytest tests/ta_r4 -q -rA -p no:cacheprovider > <scratchpad>/ta_r4_after.txt 2>&1`; reconcile by id
       against ta_r4_before.txt (sorted `PASSED|SKIPPED|FAILED|ERROR` id lists, `comm`): removed ids ⊆
       test_osf_gate.py; added ids ⊆ test_lock_gate.py / test_signoff.py / test_signoffs.py; every other id has the
       same outcome; 0 failed. Show the arithmetic (before − removed + added = after). Then `$PY -m pytest
       tests/m3/test_source_freeze_pins.py -q` (green), `time $FULL 2>&1 | tail -5` vs 1868/1818/50/0 (difference
       explained by the reconciled ta_r4 ids only), then `git restore tests/m3/sparse_parent_benchmark.tsv`.
       `git diff --quiet HEAD -- src/legacy/region_analysis/scripts/run_susie_rss.R` rc 0 (frozen file 0-diff).
    8. `bash bin/r4_fire.sh production A3_1kg -n r4_gate_probe; echo $?` on the real repo → non-zero with
       "lock record absent"; `bash bin/r4_fire.sh repro repro_routeC -n r4_gate_probe_repro; echo $?` → 0. Paste both.
    9. fsck; commit explicit paths (including the two `git rm`s): `refactor(ta-r4): production gate uses the git lock, OSF gate removed`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_signoffs.py tests/ta_r4/test_snakemake_toy_e2e.py tests/ta_r4/test_frozen_script_armed_e2e.py -q && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4 -q -m 'not r4_heavy' && ! bash bin/r4_fire.sh production A3_1kg -n r4_gate_probe >/dev/null 2>&1 && echo PROD_REFUSED</automated>
  </verify>
  <done>No OSF code path remains; Snakefile/rules/fire script use r4_lock_gate; the end-to-end drift negative control refuses; tests/ta_r4 and FULL are green and reconciled by id against the pre-change run; sparse_parent_benchmark.tsv restored; run_susie_rss.R 0-diff.</done>
</task>

<task type="auto">
  <name>Task 3: Records — DEC, deviations note, PLAN-INDEX + downstream plans, LOG, HANDOFF, STATE; push</name>
  <files>.planning/DECISIONS.md, .planning/osf_deviations.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-CONTEXT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-VALIDATION.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3d-estimators-and-branch-classifier-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3e-qtl-harmonize-and-group-runner-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4b-amendment-final-and-posting-gate-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5a-eur-production-fits-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5b-eur-production-coloc-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W5c-afr-secondary-and-simulation-run-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W6-qtl-layer-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W7-aggregation-figures-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/HANDOFF.json, .planning/STATE.md</files>
  <action>
    Keep edits short (the fix, not an essay); rationale lives in the DEC and commit message. Do not edit any
    SUMMARY file or completed plan (W0a–W2c): they are history.
    1. `.planning/DECISIONS.md`: append `## 2026-10-28 — DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf: the ta-r4
       production gate is the git lock (lock commit ancestor of HEAD + no locked file drift + Carter's W4b-T3 lock_sha); OSF is not required`
       in the format of the 2026-10-21 entries: Decider Carter 2026-10-28 (no OSF token, does not want one);
       supersedes D-05/D-27 and rigor upgrade 3 for production gating; repro unchanged; consequence accepted by
       Carter: R4 cannot claim "pre-registered on OSF" — public wording is "analysis locked in commit <sha> before
       production"; earlier OSF registrations (pvb5j, az52u, k8w7n) untouched; OSF posting of the R4 amendment is
       optional and never blocks W5; implementing commits = the Task 1 and Task 2 shas.
    2. `.planning/osf_deviations.md`: append a short dated R4 entry pointing to the DEC: the R4 amendment is no
       longer an OSF posting precondition; if Carter posts it, the URL is recorded here; no OSF record is changed.
    3. `ta-r4-PLAN-INDEX.md`: rigor upgrade 1 — "W5a–W6 refuse to fire" is now enforced by `r4_lock_gate`
       (LOCKED_PATHS, lock record `$P/R4-LOCK.json`); rigor upgrade 3 — rewrite as the git-lock gate (record tracked
       + committed, lock_sha ancestor, configs locked at lock_sha, no drift committed/working/untracked, W4b-T3
       lock_sha matches; offline, no network, no env bypass; DEC id); §A fire line "and for production runs
       `r4_lock_gate check` first"; Stages line "(gated by the lock gate, DEC-…)"; rule 11 add the public-wording
       sentence; rule 12 — never post to OSF on Carter's behalf; never create `$P/R4-LOCK.json` except in W4b Task 2
       with lock_sha = commit A; never write signoffs/W4b-T3.yaml except via `signoff record` from Carter's verbatim
       reply; fixture lock records only under pytest tmp_path; rule 14 — reason becomes "in-job gate checks re-diff
       the locked paths against the lock commit"; §D code-level sentinel bullet for the gate rewritten; tracked
       sentinel ⇒ W4b-T3 becomes tracked lock record ⇒ W4b-T3 with equal lock_sha; REQ-OSF-PREREG row: W0b2 (original
       gate), quick-261028-kkg (lock gate), W4a (amendment + locks), W4b (lock commit A + lock record + W4b-T3),
       W5a–W6 (gate exercised), W9; D-05 and D-27 coverage rows: description amended to the lock gate with the DEC id.
    4. `ta-r4-CONTEXT.md`: add one line under D-05 and under D-27: "Superseded for production gating 2026-10-28 by
       DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf." (do not rewrite the decisions).
    5. Plans (pending only):
       - W4b: objective/truths/Task 2/Task 3/threat model/key_links — commit A unchanged; Task 2 also writes and commits
         `$P/R4-LOCK.json` {"lock_sha": <commit A full sha>}, and its closed-gate proof expects "(i) W4b-T3" (not
         "sentinel absent"); the Pre-Paste checklist becomes optional (Carter may upload PUBLIC to OSF; if he does,
         record the URL in osf_deviations.md; nothing reads it); Task 3 becomes "LOCK GATE — Carter confirms the lock
         commit" (human-action, resume `carter-approved YYYY-MM-DD` + `lock_sha: <40-hex>`), verify = `signoff verify
         W4b-T3 && r4_lock_gate check --stage production && echo GATE_OPEN`; delete the sentinel/verify-online/no-Claude-
         trailer criteria; the amendment cites commit A as "analysis locked in commit <sha> before production".
       - W4a: truth "NEVER creates OSF-R4-POSTED.json" → "never posts to OSF; the R4 amendment text must not claim R4
         was pre-registered on OSF (wording per DEC-2026-10-28-…)".
       - W5a Task 1: steps 1–3 → `r4_lock_gate check --stage production` (+ `signoff verify W4b-T3`); step 2 keeps the
         ancestry check of every sha the FINAL amendment cites and pastes `git diff --stat <lock_sha> HEAD -- $($PY -m
         ta_r4.r4_lock_gate paths)` (the list now lives in the code); real-repo test takes its "lock record tracked"
         branch; update interfaces, truths, verify (drop verify-online), threat row.
       - W5b, W5c, W6: "gate checks (verify-online, check)" → "lock gate check"; W7: its lock-diff refusal reuses
         `r4_lock_gate paths`/check. W3d: FINAL labelling needs "a passing lock gate (fixture lock record + W4b-T3
         fixture sign-off via write_fixture_lock)" and read_first → r4_lock_gate.py. W3e step 5: "refuses at the fire
         script's lock-gate check (lock record absent)" and "fails with LockGateError".
       - VALIDATION.md: W5a-T1 row command → lock gate; replace `test_osf_gate.py` with `test_lock_gate.py` in rows
         that are not ✅.
       Then `grep -n "verify-online\|OSF-R4-POSTED\|r4_osf_gate\|OsfGateError" $P/ta-r4-PLAN-INDEX.md $P/ta-r4-VALIDATION.md
       $P/ta-r4-W3d*PLAN.md $P/ta-r4-W3e*PLAN.md $P/ta-r4-W4*PLAN.md $P/ta-r4-W5*PLAN.md $P/ta-r4-W6*PLAN.md $P/ta-r4-W7*PLAN.md`
       and account for every remaining hit (only ✅ VALIDATION rows or explicit "superseded" pointers may remain).
    6. `ta-r4-LOG.md`: append `## 2026-10-28 — quick-261028-kkg: production gate = git lock (DEC-…)` with the Task 1/2
       shas, RED output, both negative controls (blinded drift RED; e2e drift dry-run refusal), the by-id
       reconciliation arithmetic, the FULL counts, and the two real-repo fire-script outputs.
    7. `.planning/HANDOFF.json`: load, copy current `status` → `status_PRIOR_2026_10_28` and `headline` →
       `headline_PRIOR_2026_10_28`, set new `status` ("ta-r4 W2c COMPLETE at ac4e5452; production gate is now the
       git lock (DEC-2026-10-28-…); NEXT = W3a (W2d is a no-op: native/full)") and a short `headline`; update
       `timestamp`; keep every other key and its order. Write with the file's existing indent and ensure_ascii as it is
       today; confirm `git diff --stat .planning/HANDOFF.json` touches only those keys (if json.dump reformats other
       lines, do a surgical text edit instead).
    8. `.planning/STATE.md`: insert above the current top block `## 2026-10-28 — **TRACK A ta-r4: W2c COMPLETE
       (ac4e5452). PRODUCTION GATE = GIT LOCK (quick-261028-kkg). NEXT = W3a (W2d no-op: native/full). NOTHING
       RUNNING.** (★ RESUME HERE — LATEST ★)` with 3–5 bullets (W2c-T4 recorded; gate change + DEC id + commit shas;
       FULL counts; next step); change the previous block's marker to `(SUPERSEDED by the block above)`.
    9. fsck; commit explicit paths (plus this quick task's PLAN/SUMMARY): `docs(ta-r4): record the git-lock gate decision (DEC-2026-10-28)`;
       fsck; `git push` (origin is SSH); paste the push result and `git status -sb` showing 0 ahead.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -c "DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf" .planning/DECISIONS.md .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md .planning/osf_deviations.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json;d=json.load(open('.planning/HANDOFF.json'));assert 'status_PRIOR_2026_10_28' in d and 'headline_PRIOR_2026_10_28' in d and 'W3a' in d['status'];print('HANDOFF_OK')" && git status -sb | head -1</automated>
  </verify>
  <done>The decision and its consequence for public wording are recorded; no pending plan makes OSF a W5 precondition; W4b still makes lock commit A and writes the lock record; HANDOFF/STATE point at W3a; everything is pushed (0 ahead of origin).</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| executor/agent → production gate | an agent could try to open production without Carter or after editing analysis code |
| working copy → LSF jobs | jobs run whatever is on disk, not only what is committed |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-kkg-01 | Spoofing | fabricated lock record | mitigate | check (i): a tracked, verifying W4b-T3 sign-off from Carter's verbatim reply must carry the same lock_sha; §B.12/§B.15 forbid authoring either by hand |
| T-kkg-02 | Tampering | analysis code edited after the lock | mitigate | checks (g)/(h): committed, working-copy and untracked drift over LOCKED_PATHS; the gate module is itself inside LOCKED_PATHS |
| T-kkg-03 | Tampering | lock_sha moved to a pre-lock or unrelated commit | mitigate | check (e) ancestry + check (f) all three configs `locked: true` at lock_sha + Carter confirms the sha in W4b-T3 |
| T-kkg-04 | Elevation of privilege | env-var or parameter bypass | mitigate | AST test: no os.environ/getenv; signature (repo_root, stage); env vars tested to change nothing |
| T-kkg-05 | Repudiation | loss of the external public timestamp OSF gave | accept | Carter's decision (DEC-2026-10-28); public wording limited to "analysis locked in commit <sha> before production"; commit A is pushed to the public GitHub remote before W5 |
| T-kkg-06 | Denial of service | gate fails open on a git error | mitigate | every git call's non-zero rc raises LockGateError; failures are not memoized |
</threat_model>

<verification>
- Real repo: `r4_lock_gate check --stage production` exits 1 "(a) lock record absent"; `--stage repro` exits 0; fire script refuses production and passes repro.
- Drift negative controls: unit (blinded check → RED, restore → green) and end-to-end (uncommitted edit → dry-run refuses).
- No-network test green with socket/urllib patched to raise; `ta_r4.r4_osf_gate` not importable.
- tests/ta_r4 reconciled by id vs the pre-change run; FULL green; sparse_parent_benchmark.tsv restored; run_susie_rss.R 0-diff; test_source_freeze_pins green.
</verification>

<success_criteria>
W5 production can open with no OSF dependency, only through the pushed lock commit, an unmodified locked tree and Carter's recorded lock_sha confirmation; every planning record says so; three commits pushed.
</success_criteria>

<output>
After completion, create `.planning/quick/261028-kkg-ta-r4-w5-gate-replace-osf-check-with-loc/261028-kkg-SUMMARY.md`
</output>
