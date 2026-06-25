---
status: resolved
trigger: "m3-W2-stitch-rds-test-failures: 3 failures in tests/m3/test_stitch_subregions_to_rds.py during full pytest tests/m3 run (260 passed, 38 skipped, 3 failed)"
created: 2026-06-24T00:00:00Z
updated: 2026-06-24T03:00:00Z
---

## Current Focus

hypothesis: CONFIRMED — flaky subprocess TimeoutExpired under shared-node contention, NOT a stitch-logic bug. Fix EXTENDED to the whole flake CLASS (a blast-radius sweep found test_ld_npz_to_rds.py shares the same reticulate-cold-start path via a private toolchain copy with tight literal 60/60/180s budgets). Shared constant hoisted to the ROOT tests/conftest.py (the bare `conftest` module pytest imports; the tests/m3 conftest is shadowed by it). All 13 R/reticulate timeout sites across the 3 modules now route through it.
test: RUN all three R-exec modules together with the marker explicit (M3_R_LD_RSCRIPT set) — R tests must PASS not SKIP; collection clean
expecting: green across all three; the ld_npz R round-trips (previously 60/60/180s) now ride the 900s budget
next_action: CLASS-VERIFY GREEN (35 passed, 1 skipped — the skip is hail-import-only test_bm_to_npz_helper, NOT an R-toolchain skip; all R/reticulate round-trips RAN+passed). Atomic-commit + RESOLVED + DEBUG COMPLETE.

## Evidence (early)

- timestamp: 2026-06-24
  checked: ISOLATED run `pytest tests/m3/test_stitch_subregions_to_rds.py -v` (smoke_dev py, m3-r-ld Rscript present)
  found: 15 passed in 1071.34s (0:17:51) — ALL pass, including the 3 reported as failing (zeroes_only_beyond_buffer, banded_psd, allele_aware_alignment)
  implication: NOT a stitch-logic / bridge / triangle-flag bug. The R round-trip is correct. The 3 failures are FULL-SUITE-ONLY → test interaction, resource contention, or shared-state pollution. The ~18min isolated runtime (session reticulate+xz fixture builds) is a strong contention-timeout signal under full parallel m3 load.

## Symptoms

expected: All of tests/m3/test_stitch_subregions_to_rds.py pass — BANDED sparse stitch (stitch_subregions_to_rds.R) zeroes cross-core pairs beyond buffer_bp, keeps a PSD banded matrix, aligns alleles. Passing earlier in m3 history (m3-02b landed green).
actual: 3 named tests FAIL — test_*_zeroes_only_beyond_buffer, test_*_banded_psd, test_*_allele_aware_alignment
errors: not yet captured — reproduce to get exact assertion/Rscript error
reproduction: smoke_dev py3.11 pytest, PATH includes $HOME/miniconda3/bin, m3-r-ld Rscript discoverable
started: surfaced 2026-06-24 in m3-02e full-suite verification; likely predates m3-02e (stitch path byte-identical to base 1cd6789)

## Eliminated

- hypothesis: stitch-logic / triangle-flag / python-R bridge bug in stitch_subregions_to_rds.R
  evidence: ISOLATED 15/15 PASS; files byte-identical to base 1cd6789 (git diff empty); last touched at m3-02b commits 0e3ec43/3b2de9a/0f496e7, untouched by m3-02e
  timestamp: 2026-06-24

## Evidence

- timestamp: 2026-06-24
  checked: git log + git diff 1cd6789 for stitch R, converter R, test file
  found: zero uncommitted changes; no diff vs base. Last commits = m3-02b (0e3ec43 feat, 3b2de9a CR-01, a3f32f2 WR-03, 0f496e7 WR-02). m3-02e did NOT touch them.
  implication: drift is environmental/interaction, not source.
- timestamp: 2026-06-24
  checked: presence of REAL chain data/external/liftover/hg38ToHg19.over.chain.gz
  found: EXISTS (1.2MB, Jun 19). So chain_38_to_37 fixture returns the REAL chain in BOTH isolated and full runs (not the synthetic identity chain). Liftover is identical across runs → not the differentiator.
  implication: the failing assertions (order(v$POS), R[ia,ib], NROW==3) are deterministic under the real chain; isolated run proves they pass. Differentiator is resource/interaction.
- timestamp: 2026-06-24
  checked: pytest config / xdist availability
  found: no xdist installed; no addopts; tests run SERIALLY. No pytest.ini/pyproject addopts. test_sparse_parent_benchmark.py (alphabetically just BEFORE test_stitch_*) builds a 50,000-var banded sparse R in an R subprocess with PEAK_RAM_LOAD_CEILING_GIB=8.0 + timeout=600.
  implication: prime suspect = the heavy 50k-var benchmark immediately preceding the stitch tests (shared node memory / R subprocess contention), OR full-suite TimeoutExpired (KB note for the sibling m3-W2-a2 session called the R-toolchain TimeoutExpired a "parallel-run contention flake, passes in isolation").
- timestamp: 2026-06-24
  checked: TARGETED reproduction `pytest test_sparse_parent_benchmark.py test_stitch_subregions_to_rds.py` (benchmark immediately before stitch)
  found: 17 passed in 1245.94s (0:20:45), 0 failed. All 3 reported-failing stitch tests PASSED.
  implication: benchmark is NOT the pollution source. Eliminates the "50k-var memory poisons stitch" hypothesis.
- timestamp: 2026-06-24
  checked: FAITHFUL FULL-SUITE reproduction `pytest tests/m3 -p no:cacheprovider -v` (shared 32-core node, 16 users, load ~2-3, 124GB free)
  found: 271 passed, 30 skipped, 0 FAILED in 1961.91s (0:32:41). ALL 15 stitch tests passed, including the 3 reported failing.
  implication: THE 3 FAILURES DO NOT REPRODUCE. The original m3-02e "3 failed" was a transient/flaky artifact, not a reproducible defect. (Note: the full-suite benchmark took MUCH longer than in the targeted run — direct evidence of variable shared-node contention.)
- timestamp: 2026-06-24
  checked: cost of a single reticulate cold-start in the m3-r-ld env (the per-subprocess fixed cost every stitch R call pays)
  found: `reticulate::import + pyliftover import` = 66.1s; LiftOver(real 1.2MB chain) parse = 1.8s. So ~66s is reticulate spinning up embedded Python+numpy+pyliftover, NOT the chain.
  implication: every stitch R subprocess pays ~66s cold-start BEFORE doing any work. Under contention this is the dominant, variable cost. `_run_stitch` budget=300s; the read-back probe (_read_rds_summary, _check_r_env) budget=120s. A contention spike that stretches the 66s cold-start past these budgets raises subprocess.TimeoutExpired → pytest FAILED. This is the flake mechanism.
- timestamp: 2026-06-24
  checked: BLAST-RADIUS sweep of the flake CLASS across all m3 R-execution test modules
  found: test_ld_npz_to_rds.py has its OWN private toolchain-discovery copy (_candidate_rscripts/_check_r_env/_require_*) hitting the SAME m3-r-ld Rscript + reticulate cold-start, with tight literal budgets: probe 60s (L117), rds reader 60s (L211), converter 180s (L226), AF reader 60s (~L772). It did NOT use the stitch file's R_SUBPROCESS_TIMEOUT_S → would flake identically under contention. (Its 5th subprocess, timeout=300, is the bm_to_npz.py PYTHON helper — no reticulate — correctly excluded.)
  implication: the initial stitch-only fix was INCOMPLETE for the class. Closing the class = ONE shared constant consumed by all three modules.
- timestamp: 2026-06-24
  checked: where to home the shared constant (conftest shadowing under pytest prepend import mode)
  found: `from conftest import R_SUBPROCESS_TIMEOUT_S` resolves to the ROOT tests/conftest.py, NOT tests/m3/conftest.py — pytest imports the root conftest as the bare `conftest` module and the m3 one is shadowed. A first attempt to define it in tests/m3/conftest.py raised ImportError at collection (cannot import name from 'conftest' (.../tests/conftest.py)). Corrected by homing the constant in the ROOT conftest.
  implication: single source of truth = tests/conftest.py; m3 conftest carries only a pointer note. Verified all 4 (conftest + 3 modules) resolve to the same 900 value; pytest collection of the 3 modules = 36 items, 0 errors.

## Resolution

root_cause: |
  FLAKY TEST-HARNESS TIMEOUT, not a stitch-logic / product bug. The 3 "failures" in the
  m3-02e full-suite verification (260 passed / 38 skipped / 3 failed) were transient
  subprocess.TimeoutExpired exceptions raised by individual R-round-trip subprocess.run()
  calls in tests/m3/test_stitch_subregions_to_rds.py, surfaced by pytest as FAILED.

  Mechanism: each stitch R subprocess pays a ~66s reticulate cold-start (embedded
  Python + numpy + pyliftover import; measured 66.1s, with the real 1.2MB chain parse
  only 1.8s of that). On the shared 32-core NCSU node (16 concurrent users, OpenBLAS-
  threaded R) under accumulated full-suite memory/CPU pressure, that fixed cost can
  balloon several-fold. The per-subprocess budgets were tight relative to the ~66s
  floor: read-back/probe calls = 120s (~1.8x headroom), _run_stitch = 300s, converter
  reads = 180s. A contention spike during the m3-02e run pushed exactly 3 of these
  R-round-trip tests past their budget → TimeoutExpired → reported FAILED.

  PROOF it is non-deterministic: a faithful clean re-run of the WHOLE suite
  (`pytest tests/m3`) on the same node = 271 passed / 30 skipped / 0 failed; the file
  in isolation = 15/15 pass; benchmark+stitch together = 17/17 pass. The stitch source
  (stitch_subregions_to_rds.R), converter (ld_npz_to_rds.R), and the test file are
  byte-identical to base 1cd6789 and were untouched by m3-02e. So no logic regression
  exists; the banded-stitch geometry, PSD, allele-alignment, and lower_triangular-flag
  contract are all correct.

fix: |
  Harden the R-subprocess timeouts so a transient shared-node contention spike can no
  longer flip a passing test to FAILED — applied across the WHOLE flake CLASS, not just
  the stitch file. A blast-radius sweep found test_ld_npz_to_rds.py invokes the SAME
  m3-r-ld Rscript / reticulate cold-start path via its OWN private toolchain-discovery
  copy with tight literal timeouts (60/60/180s) that would flake identically.

  Single source of truth = R_SUBPROCESS_TIMEOUT_S in the ROOT tests/conftest.py
  (default 900s, ~13x the ~66s cold-start floor; override via M3_R_SUBPROCESS_TIMEOUT_S).
  It lives in the ROOT conftest, NOT tests/m3/conftest.py, because pytest's default
  prepend import mode imports the ROOT conftest as the bare `conftest` module and the
  tests/m3 conftest is SHADOWED by it — `from conftest import R_SUBPROCESS_TIMEOUT_S`
  resolves to root. (Initial attempt to home it in tests/m3/conftest.py raised
  ImportError at collection precisely because of this shadowing; caught + corrected.)

  All R/reticulate-path subprocess.run(timeout=...) sites now route through the shared
  constant: stitch (7 sites), finemap loader contract (2 sites), ld_npz_to_rds (4 sites:
  probe 60s, rds reader 60s, converter 180s, AF reader 60s). The ld_npz bm_to_npz.py
  PYTHON helper subprocess (timeout=300) is deliberately LEFT AS-IS — it does not touch
  reticulate, so it is not part of the cold-start flake class.

  Does NOT weaken any assertion — banded/PSD/allele/flag/AF/round-trip checks unchanged;
  only the wall-clock budget changes. The tests remain the regression harness and still
  FAIL loudly on any real defect (rc!=0 / wrong values).

verification: |
  SELF-VERIFIED:
  - Per-call timing: 4 sequential _run_stitch calls = 67.2s, 64.8s, 66.2s, 80.4s
    (20% swing even at low load); reticulate cold-start alone = 66.1s. Confirms the
    ~66s floor and the variability that trips tight budgets.
  - 3 previously-flaky stitch tests with hardened timeouts = 3 passed in 279.14s.
  - Import-resolution: `from conftest import R_SUBPROCESS_TIMEOUT_S` resolves to the ROOT
    conftest for all 3 R-exec modules (stitch directly, finemap via stitch re-export,
    ld_npz directly); all four (conftest + 3 modules) == 900; collection = 36 tests, 0
    errors.
  - Authoritative FULL-SUITE re-run = 271 passed / 30 skipped / 0 failed (confirms no
    logic regression; the fix is preventive hardening only).
  - CLASS-VERIFY (RUN the R path, marker explicit, M3_R_LD_RSCRIPT set): pytest of all
    THREE R-exec modules together = 35 passed, 1 skipped, 0 failed in 1840.15s (0:30:40).
    The 1 skip = test_bm_to_npz_helper (could not import 'hail' — a hail-only test, NOT
    an R-toolchain skip); ALL R/reticulate round-trips RAN and PASSED under the 900s
    budget. Collection clean (36 collected). The flake class is closed.
files_changed:
  - tests/conftest.py (NEW shared R_SUBPROCESS_TIMEOUT_S constant — single source of truth)
  - tests/m3/conftest.py (note pointing to the root constant; removed the briefly-misplaced m3 copy + now-unused os import)
  - tests/m3/test_stitch_subregions_to_rds.py (consume shared constant via `from conftest import`; route all 7 R-subprocess timeouts; re-export for siblings; add tests/m3 to sys.path)
  - tests/m3/test_finemap_loader_contract.py (import the shared constant via stitch re-export; route its 2 R-subprocess timeouts)
  - tests/m3/test_ld_npz_to_rds.py (import the shared constant; route its 4 R/reticulate-path timeouts; bm_to_npz python-helper timeout left as-is)
