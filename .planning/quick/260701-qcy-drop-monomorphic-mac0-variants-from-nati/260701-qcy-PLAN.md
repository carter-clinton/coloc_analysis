---
phase: quick-260701-qcy
plan: 01
type: tdd
wave: 1
depends_on: []
files_modified:
  - src/python/aou_ld_panel.py
  - src/python/run_native_ld_panel.py
  - tests/m3/test_run_native_ld_panel.py
  - tests/m3/test_plink_ld_to_npz.py
autonomous: true
requirements: [m3-02e-T4-drop-monomorphic-mac0]
must_haves:
  truths:
    - "The SQUARE plink command drops MAC=0 (monomorphic-in-AFR) variants BEFORE `--r square` via `--mac 1`, so the emitted `.ld.bin` is (n_retained)^2 with NO NaN and read_square_bin's symmetry check passes"
    - "The plink command emits `--write-snplist` giving the RETAINED variant IDs in `.ld.bin` row order; the converter aligns to that retained order (n_var == len(retained))"
    - "process_region's `bin_n_var != window_n_var` cross-check compares RETAINED == RETAINED (uses the snplist), NOT the raw in-window .bim count — otherwise it would falsely mismatch on every region"
    - "A genuine bin/window disagreement still raises the BYTE-IDENTICAL `n_var mismatch` ValueError it raises today"
    - "read_square_bin / load_bim / the symmetry+diagonal+OOM-bounded checks in plink_ld_to_npz.py are UNCHANGED (they CAUGHT the bug — they are correct); the banded branch and the resume skip/continue semantics are UNCHANGED"
    - "A NaN-bearing square `.ld.bin` still deterministically RAISES `square LD is not symmetric` (regression that locks the diagnosis)"
    - "The tests/m3 suite stays green (baseline 309 passed / 30 skipped; new tests add to passed)"
  artifacts:
    - path: "src/python/aou_ld_panel.py"
      provides: "build_plink_ld_command SQUARE branch emits `--mac 1 --nonfounders --write-snplist`"
      contains: "--write-snplist"
    - path: "src/python/run_native_ld_panel.py"
      provides: "_retained_window_bim helper that intersects the raw in-window .bim with the plink `.snplist` in snplist order; process_region SQUARE path threads it so n_var==len(retained)"
      contains: "_retained_window_bim"
    - path: "tests/m3/test_run_native_ld_panel.py"
      provides: "_MockPlink honors --write-snplist (drops k monomorphic rows, emits .snplist, sizes .ld.bin to retained^2); failing-first drop/order/flags/status==ok tests"
      contains: "write-snplist"
    - path: "tests/m3/test_plink_ld_to_npz.py"
      provides: "NaN-.ld.bin regression asserting read_square_bin RAISES 'not symmetric'"
      contains: "not symmetric"
  key_links:
    - from: "src/python/aou_ld_panel.py::build_plink_ld_command (square branch)"
      to: "plink argv"
      via: "append --mac 1 --nonfounders --write-snplist"
      pattern: "--write-snplist"
    - from: "src/python/run_native_ld_panel.py::process_region (square branch)"
      to: "_retained_window_bim"
      via: "intersect raw window .bim with {out_prefix}.snplist in snplist order -> retained .bim + n_var"
      pattern: "_retained_window_bim\\("
    - from: "_retained_window_bim"
      to: "plink_ld_to_npz (unchanged)"
      via: "pass retained-order .bim + n_var=len(retained)"
      pattern: "plink_ld_to_npz\\("
---

<objective>
Drop monomorphic (MAC=0-in-AFR) variants from the native-plink LD panel so plink
never emits NaN LD and read_square_bin's symmetry check passes.

Root cause is CONFIRMED (do NOT re-investigate; the earlier "transient short-read"
diagnosis in SUPERSEDED STATE blocks was WRONG, corrected @ c90a629): m3-02e-T4
fire #3 region 1 failed with a REAL, reproducible symmetry-check failure.
`read_square_bin` (plink_ld_to_npz.py:187-191) RAISES `square LD is not symmetric`
on region 1's intact 42 GB `.ld.bin` (deterministic). Pinpoint diagnostic: 12 NaN
entries across 11 rows, clustered in adjacent pairs/triples, diagonals still 1.0 =
the fingerprint of monomorphic (MAC=0 in the 73k-AFR cohort) variants — plink `--r`
computes 0/0 -> NaN for a zero-variance variant, and NaN != NaN breaks the symmetry
equality. SYSTEMIC across the 276 windows. Carter's DECISION (2026-07-01): DROP
MAC=0 variants (standard LD-reference-panel practice; LD to a zero-variance site is
undefined). The retry-on-zero guard @ 27af416 is harmless but does NOT fix this.

Mechanism (RESEARCH.md, HIGH confidence): plink1.9 order-of-operations
(--chr/--from-bp/--to-bp -> --maf/--mac -> --write-snplist -> --r) means `--mac 1`
drops MAC=0 variants BEFORE `--r square`, so the `.ld.bin` is (n_retained)^2 with no
NaN; `--write-snplist` emits the retained IDs in `.ld.bin` row order. Per-region
`--mac 1` + snplist-threading is preferred over a one-time bfile pre-filter (the
loop VM's 1TB PD is ~588 GB used; a 2nd ~354 GB bfile is infeasible).
</objective>

<task id="1" type="tdd-red">
**Wave 0 — extend _MockPlink for --write-snplist + RED tests**

files:
  - tests/m3/test_run_native_ld_panel.py
  - tests/m3/test_plink_ld_to_npz.py

action:
  - Extend the `_MockPlink` monkeypatch fixture to honor `--write-snplist`: given a
    window of N variants with k designated monomorphic, drop those k rows, write
    `{out_prefix}.snplist` (bare one-ID-per-line, RETAINED IDs in .bim order), and
    size the emitted `{out_prefix}.ld.bin` to (N-k)^2 float32 (symmetric, unit
    diagonal, no NaN).
  - RED tests (failing-first, must fail before Task 2):
    (a) build_plink_ld_command SQUARE argv CONTAINS `--mac 1`, `--nonfounders`,
        `--write-snplist` (and still `--keep-allele-order`, `--r square bin4`); the
        BANDED argv does NOT gain `--mac`.
    (b) process_region on a window with k=2 monomorphic -> status==ok, n_var ==
        retained count (N-k), the produced .npz variant list == retained IDs in
        snplist order, matrix is (N-k)^2 with NO NaN.
    (c) the retained window .bim row order == the .snplist order.
    (d) NaN regression (test_plink_ld_to_npz.py): a square `.ld.bin` containing a
        NaN makes read_square_bin RAISE `square LD is not symmetric` (locks WHY the
        drop is needed; read_square_bin itself is NOT modified).
    (e) GUARD-PRESERVATION integration test (checker warning 1): a process_region
        SQUARE call where the raw window .bim read returns 0 on the FIRST attempt then
        the real count on retry (transient) STILL self-heals through the retry guard
        AND then threads the retained snplist -> status==ok (NOT an n_var mismatch
        error). This is an integration-level test through process_region, distinct
        from the existing unit-level `_window_bim_n_var_retry_on_zero` tests which
        stay green even if the square path stopped routing through the guard.

verify:
  - `pytest tests/m3/test_run_native_ld_panel.py tests/m3/test_plink_ld_to_npz.py -x`
    shows the NEW tests RED (assertion failures on the missing flags / mismatch),
    NOT collection/import errors.

done: New tests exist and FAIL for the right reason (flags absent / threading absent), proving the gap before the fix.
</task>

<task id="2" type="tdd-green">
**GREEN — emit the flags + thread the retained snplist**

files:
  - src/python/aou_ld_panel.py
  - src/python/run_native_ld_panel.py

action:
  - `build_plink_ld_command` (aou_ld_panel.py), SQUARE branch ONLY: append
    `--mac 1 --nonfounders --write-snplist`. Do NOT add `--mac` to the banded
    branch. Keep `--keep-allele-order` and `--r square bin4` unchanged.
  - `process_region` (run_native_ld_panel.py), SQUARE path: add a reusable helper
    `_retained_window_bim(raw_window_bim, snplist_path)` that intersects the raw
    in-window .bim with `{out_prefix}.snplist`, RE-ORDERED to snplist order,
    returning (retained_n_var, retained_window_bim_path). Use it in place of the
    raw-window count: window_n_var = retained_n_var; feed the retained .bim +
    n_var=retained_n_var to plink_ld_to_npz (UNCHANGED). The existing
    `if bin_n_var != window_n_var: raise ValueError(...)` then compares
    retained==retained; keep the ValueError message BYTE-IDENTICAL.
  - **PRESERVE THE 27af416 TRANSIENT GUARD (checker warning 1 — load-bearing):** the
    existing `_window_bim_n_var_retry_on_zero(...)` call (run_native_ld_panel.py
    ~514-516) MUST remain the producer of `raw_window_bim` — retry-on-zero semantics
    INTACT. `_retained_window_bim` consumes that already-retry-read raw window .bim;
    only the CROSS-CHECK OPERAND moves from the raw count to `retained_n_var`. Do NOT
    replace the guarded read with `_retained_window_bim`. (Dropping the guard would
    silently regress the transient short-read heal that banked 0/276 three times, and
    the existing unit-level guard tests would stay GREEN and miss it.)
  - Update docstrings/comments where per-region n_var is described to note it now
    legitimately EXCLUDES monomorphic (MAC=0) variants.
  - Do NOT touch plink_ld_to_npz.py readers/checks, content_verify_npz, the banded
    path, the retry-on-zero guard, or the resume skip/continue semantics.

verify:
  - `pytest tests/m3/test_run_native_ld_panel.py tests/m3/test_plink_ld_to_npz.py`
    -> all GREEN (Task 1 tests now pass).

done: Flags emitted on the square branch; the snplist is threaded so n_var==retained and the converter aligns; all Task-1 tests pass.
</task>

<task id="3" type="verify-suite">
**Full-suite green + atomic commits**

files: [] (validation + commits only)

action:
  - Run the FULL `tests/m3` suite; confirm >= 310 passed / 30 skipped (baseline
    309 + the new tests). Report the exact pytest summary line as evidence.
  - Commit atomically with EXPLICIT paths (never `git add .`/`-A`): Task 1 (tests)
    as one commit, Task 2 (impl) as one commit — TDD RED then GREEN visible in
    history.
  - **STATE/HANDOFF refresh (checker warning 2 — feedback_state_md_keep_current):**
    update `.planning/STATE.md` + `.planning/HANDOFF.json` to reflect "drop-monomorphic
    fix LANDED + green; re-fire PENDING = push origin -> AoU `git pull` >= new HEAD on
    the SAME n1-standard-32 (NO respec) -> REGION-1-ONLY re-run passes read_square_bin
    -> full 276". Commit with explicit paths. (The orchestrator may instead fold this
    into the close-out docs commit — either way it MUST land so a disconnect resumes
    to the correct state, not the pre-fix "do not fire" block.)

verify:
  - `pytest tests/m3` summary line shows >= 310 passed / 30 skipped, 0 failed.
  - `git log --oneline -3` shows the RED then GREEN commits (explicit-path) + STATE/HANDOFF refresh.

done: Full suite green above baseline; changes committed atomically; ready for push + the post-land AoU gate.
</task>

<post_land_operational note="NOT an NCSU task — for the AoU agent AFTER this fix pushes">
VERIFICATION BEFORE FULL FIRE (de-risks the ~11-day / ~$400 run):
1. Push origin m3-W2-aou-deltas; verify origin tip == local HEAD.
2. AoU agent: `git pull` the fix on the VM (n1-standard-32, NO respec).
3. Re-gate: `md5sum src/python/aou_ld_panel.py` + `grep -n "write-snplist" src/python/aou_ld_panel.py`.
4. Fire pre-flight sanity: run REGION 1 ONLY, then confirm on the emitted artifacts:
   - `head -3 /home/jupyter/native_ld_scratch/m2_region_00001.snplist` (bare one-ID/line)
   - `awk '{print $6}' /home/jupyter/afr_cohort.fam | sort -u` (founder col; `--nonfounders` makes `--mac` count all samples)
   - re-run `read_square_bin` on the region-1 `.ld.bin` -> PASSES (no NaN, symmetric); panel row status==ok; n_var slightly < 102,421 (monomorphic dropped).
5. ONLY THEN launch the full 276-region loop (same loop_command, liveness = bucket .npz -> 276).
</post_land_operational>
