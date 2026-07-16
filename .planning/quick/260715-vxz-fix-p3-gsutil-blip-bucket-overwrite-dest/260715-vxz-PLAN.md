---
quick_id: 260715-vxz
type: execute
mode: quick-full
wave: 1
depends_on: []
autonomous: true
files_modified:
  - src/python/run_native_ld_panel.py
  - tests/m3/test_run_native_ld_panel.py
requirements: [P3a, P3b]

must_haves:
  truths:
    - "An INDETERMINATE gsutil stat on the gs:// panel TSV (any error that is NOT a positive absent signature) RAISES instead of silently starting a fresh 1-row mirror."
    - "A stat that says PRESENT followed by a FAILED seed download RAISES instead of overwriting the known-existing bucket object."
    - "In BOTH refusal cases the bucket panel object is left byte-identical — no `gsutil cp` to the panel URI is issued at all."
    - "A DEFINITIVELY-ABSENT panel object (real gsutil's `No URLs matched: gs://...`, exit 1) still starts a fresh mirror and uploads — the legitimate first-region path does NOT false-trip."
    - "The happy path (present + successful seed) still seeds, appends, uploads, and preserves dedup-by-region_id across a simulated cluster recycle."
    - "`_existing_region_npz_gs` resume behavior is UNCHANGED: a stat error still means recompute (compute cost, no data loss)."
  artifacts:
    - path: "src/python/run_native_ld_panel.py"
      provides: "Tri-state fail-CLOSED classifier for the panel path + refusing seed block in append_panel_row"
      contains: "append_panel_row"
    - path: "tests/m3/test_run_native_ld_panel.py"
      provides: "4 tests (2 RED-first data-loss proofs + 2 regression guards) + _MockGsutil extended to model indeterminate stat, cp failure, and download direction"
      contains: "_MockGsutil"
  key_links:
    - from: "src/python/run_native_ld_panel.py::append_panel_row"
      to: "the new tri-state classifier (NOT _gsutil_object_size)"
      via: "panel-seed branch ~:533-543"
      pattern: "append_panel_row"
    - from: "tests/m3/test_run_native_ld_panel.py"
      to: "drv._run_gsutil"
      via: "monkeypatch (the SOLE gsutil seam — no real network/perimeter contact)"
      pattern: "monkeypatch.setattr\\(drv, \"_run_gsutil\""
    - from: "src/python/run_native_ld_panel.py::_existing_region_npz_gs"
      to: "_gsutil_object_size (UNTOUCHED)"
      via: "resume guard :209 — must stay fail-OPEN"
      pattern: "_gsutil_object_size"
---

<objective>
Fix **P3** — `append_panel_row`'s gs:// mirror-seed block silently destroys every banked
row of the panel TSV when a transient gsutil blip occurs mid-fire.

Purpose: the `.npz` (not the TSV) gates the resume skip, so the fire RUNS TO COMPLETION
looking successful and the provenance loss surfaces only at analysis time — after ~11
billed days. This is a **pre-existing** defect found by the 2026-07-15 blast-radius sweep
and deliberately scoped OUT of quick-260715-u22.

Output: a tri-state fail-CLOSED classifier on the panel path, a refusing seed block, and
4 tests (2 RED-first data-loss proofs + 2 regression guards).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md

Read ONLY these regions — `run_native_ld_panel.py` is ~1008 lines and
`test_run_native_ld_panel.py` is ~1690. Do NOT read either in full.

- `src/python/run_native_ld_panel.py`: `_run_gsutil` ~:176-184, `_gsutil_object_size`
  ~:186-201, `_existing_region_npz_gs` ~:203-217, `_gsutil_upload` ~:219-222,
  `_append_panel_row_local` ~:478-512, `append_panel_row` ~:515-545.
- `tests/m3/test_run_native_ld_panel.py`: `_MockGsutil` :656-688, the `stat_error_uris`
  test at :805-822, `test_gs_panel_tsv_uploaded` :824-845.
</context>

<defect_is_settled_do_not_re_litigate>
Mechanism verified against live code this session. Do NOT re-investigate; implement.

`append_panel_row`'s gs:// mirror-seed block (~:533-543):

```python
if not local_mirror.exists():
    existing_size = _gsutil_object_size(gs_uri)      # :536
    if existing_size is not None and existing_size > 0:
        try: _run_gsutil(["cp", gs_uri, str(local_mirror)])
        except Exception: pass                        # swallows
_append_panel_row_local(local_mirror, row)
_gsutil_upload(local_mirror, gs_uri)                  # UNCONDITIONAL
```

- **P3a:** `_gsutil_object_size` returns `None` on ANY gsutil error (bare
  `except Exception`) → treated as absent → no seed → `_append_panel_row_local` takes its
  `not tsv_path.exists()` branch → FRESH header + 1 row → `_gsutil_upload` cp's that
  1-row file OVER the bucket object → **every banked row destroyed**.
- **P3b (worse):** stat SUCCEEDS (object exists, size>0) but the `cp` FAILS →
  `except: pass` → same fresh-1-row-then-upload-over. The code KNOWS the object exists
  and overwrites it anyway.
- **Why it's silent:** the `.npz` gates the resume skip (:605-608), so the `.npz` survive
  and the fire completes looking healthy. u22's header guard does NOT catch it (the
  truncated file is written by the CURRENT binary → still 9-col → no schema skew → no
  raise). No pre-flight prevents it (it happens mid-run).

**ROOT CAUSE — the insight that makes the fix minimal:** `_gsutil_object_size` has TWO
callers with OPPOSITE failure-safety requirements.

| Caller | False-absent costs | Correct default |
|--------|--------------------|-----------------|
| `:209` `_existing_region_npz_gs` (resume guard) | COMPUTE (recompute a region). No data loss. | assume absent — its "safer to recompute" docstring is CORRECT here. **Load-bearing for the 276-region skip.** |
| `:536` panel mirror seed | **DATA LOSS** (upload-over) | **REFUSE** — "assume absent" is EXACTLY BACKWARDS |
</defect_is_settled_do_not_re_litigate>

<landmines>
Four landmines are already mapped. Do not rediscover them; honor them.

**1. `_existing_region_npz_gs` MUST NOT CHANGE BEHAVIOR.**
Its only stat-error test is `tests/m3/test_run_native_ld_panel.py:814`
(`_MockGsutil(stat_error_uris={f"{gs_out}/afr_err.npz"})` → asserts
`len(mock_plink2.calls) == 1`, i.e. "stat error -> recompute"). It must stay GREEN and
UNMODIFIED. **Add a NEW fail-CLOSED helper for the panel path and leave
`_gsutil_object_size` + `_existing_region_npz_gs` UNTOUCHED.** Do not refactor the shared
helper. (Verified: `_gsutil_object_size` has exactly 2 callers — :209 and :536.)

**2. THE MOCK CONFLATES THE TWO CASES THE FIX MUST DISTINGUISH.**
`_MockGsutil.__call__` (:670-675):

```python
if uri in self.stat_error_uris or uri not in self.objects:
    raise _sp.CalledProcessError(1, ["gsutil", *args], output="", stderr="No URL matched")
```

Its `stat_error_uris` ("simulate an error") raises the **absent signature**. It therefore
CANNOT currently simulate an INDETERMINATE stat. **EXTEND `_MockGsutil`** with a distinct
capability that raises a genuinely non-absent error — e.g.
`CalledProcessError(1, ..., stderr="ServiceException: 503 Backend Error")` and/or a
non-`CalledProcessError` such as `FileNotFoundError` (gsutil not installed) — while
keeping `stat_error_uris`'s behavior **byte-identical** so :814 stays green.
*Precedent:* m3-07b extended `_MockPlink` exactly this way and a blast-radius sweep
verified the extension was byte-identical for all pre-existing callers. **Do the same and
SAY SO in the summary** — enumerate all 6 existing `_MockGsutil(` call sites
(:705, :735, :775, :799, :814, :838) and state that each is unaffected.

**3. THE MOCK LIES ABOUT REAL gsutil.**
It emits `stderr="No URL matched"` (**singular URL**). Real `gsutil stat` on a missing
object emits **`No URLs matched: gs://...`** (**plural URLs**) and exits 1. If the
absent-detection matches only the real string, existing tests break; if it matches only
the mock's, PRODUCTION never classifies absent and **every first region raises**. This is
the SAME bug class as P3 itself (a test that doesn't model reality). Do BOTH:
- (a) make detection robust to the real tool's actual output AND tolerant of the singular
  form — a case-insensitive `no url(s)? matched` match (regex, or lowercase substring
  check against both spellings; `re` is NOT currently imported — either add it or use the
  substring form, your call);
- (b) CORRECT the mock's stderr to real gsutil's plural string.
Changing the mock string is SAFE for :814 because `_gsutil_object_size` catches ALL
exceptions and returns `None` regardless of stderr — **state that reasoning in the
summary.**

**4. (found this session) THE MOCK CANNOT MODEL A DOWNLOAD.**
Its `cp` verb does `self.objects[dst] = Path(src).stat().st_size` — upload-only. A
download (`cp gs://… /local`) would call `Path("gs://…").stat()` → `FileNotFoundError`.
The download-seed path has **NEVER been exercised**: every existing call site leaves the
panel URI un-prestaged, so `_gsutil_object_size` returns `None` and the `cp` download
never fires. Consequence: **test (d) is impossible without extending the mock** to (i)
dispatch on direction (src `gs://` → download: write the stored object to the local dst;
else upload) and (ii) store CONTENTS, not just size — the "bucket unchanged" assertions
in (a)/(b) need bytes.
*Suggested backward-compatible shape (verify, don't assume):* keep
`self.objects: dict[uri, int]` exactly as-is so `prestaged={uri: <int>}` at :775/:799
stays byte-identical, and add a parallel `self.contents: dict[uri, bytes]` populated on
upload and consulted on download, plus a `prestaged_contents=` kwarg that sets both.
</landmines>

<the_fix>
**INVARIANT:** never `gsutil cp` the local mirror OVER the bucket object unless we have
POSITIVELY established the mirror contains everything the bucket object contains — i.e.
either (a) we successfully downloaded it, or (b) it DEFINITIVELY does not exist. If the
bucket state is INDETERMINATE → **RAISE**. Do not guess.

1. **Tri-state classifier for the panel path** — PRESENT(+size) / DEFINITIVELY-ABSENT /
   INDETERMINATE. `_run_gsutil` uses `check=True` → a non-zero exit raises
   `subprocess.CalledProcessError` carrying `.returncode`/`.stderr` (str, since
   `capture_output=True, text=True`).
   - ABSENT = a `CalledProcessError` whose stderr carries the no-url(s)-matched signature.
   - **Anything else** — another `CalledProcessError` (503, 403 AccessDenied, 404
     BucketNotFound), or any non-`CalledProcessError` (e.g. `FileNotFoundError` = gsutil
     not installed) — is INDETERMINATE.
   - stat exits 0 but no parseable `Content-Length` → INDETERMINATE (not absent).
   - **Be conservative: if you cannot POSITIVELY classify it as ABSENT, it is
     INDETERMINATE. Fail closed.**
2. **Panel seeding becomes:**
   - PRESENT (size > 0) → the `cp` MUST succeed; a cp failure → **RAISE** (never
     overwrite a known-existing bucket copy). Also assert the mirror actually landed:
     if the cp "succeeds" but `local_mirror` does not exist → RAISE (same data loss
     through a different door).
   - PRESENT (size == 0) → an empty object holds no rows → start fresh (today's
     `> 0` behavior; lossless — preserve it).
   - DEFINITIVELY-ABSENT → start fresh (today's behavior, correct — the legitimate
     first-region path).
   - INDETERMINATE → **RAISE**.
3. **The error must be ACTIONABLE and must DISTINGUISH the two causes** (P3a
   indeterminate-stat vs P3b cp-failed). Say: the bucket panel TSV may hold banked
   provenance; proceeding would overwrite it; re-run once connectivity/auth is restored;
   the panel TSV is rebuildable from the banked per-region `.npz`. Chain the cause
   (`raise ... from exc`).
4. **NO auto-repair, NO retry-forever.** Refuse and escalate — a guard that silently
   repairs HIDES the bug (this mirrors u22's header-guard REFUSE stance at :495-506). A
   bounded retry is acceptable ONLY if it still RAISES on exhaustion, but **the simplest
   correct fix is to raise immediately. Prefer the simplest.**
</the_fix>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Fail closed on an indeterminate/failed panel-TSV seed instead of overwriting banked provenance</name>

  <files>src/python/run_native_ld_panel.py, tests/m3/test_run_native_ld_panel.py</files>

  <behavior>
Write these 4 tests FIRST, in `tests/m3/test_run_native_ld_panel.py`, in the gs:// section
near the existing panel-TSV tests (~:824). Call `drv.append_panel_row(gs_panel, row,
scratch_dir=...)` directly — unit-level at the seam, no full-driver setup needed.
`monkeypatch.setattr(drv, "_run_gsutil", <mock>)` is the SOLE seam; **no real
gsutil/gcloud/network — zero AoU perimeter contact.**

- **(a) RED — P3a:** stat raises an INDETERMINATE error (NOT the absent signature; e.g.
  `CalledProcessError(1, ..., stderr="ServiceException: 503 Backend Error")`) against a
  **POPULATED** bucket panel TSV → must RAISE, **and MUST NOT upload — assert the bucket
  object is UNCHANGED (byte/size identical to the pre-call value). This assertion IS the
  data-loss proof; without it the test is theatre.** Also assert no `cp` with
  `dst == gs_panel` appears in `mock.calls`.
- **(b) RED — P3b:** stat says PRESENT (populated) but the seed `cp` FAILS → must RAISE
  and MUST NOT upload (bucket byte-identical; no `cp` to `gs_panel`).
- **(c) GREEN/regression:** object DEFINITIVELY absent — real gsutil's
  `No URLs matched: gs://...` + exit 1 → fresh mirror + upload proceeds exactly as today.
  **No false trip on a legitimate first region** — this is the one that would break the
  whole fire if the detection is wrong.
- **(d) GREEN/regression:** happy path (present + `cp` succeeds) → seeds, appends,
  uploads, **dedup preserved across a simulated recycle** — call `append_panel_row` once
  with scratch A, then again with a FRESH scratch B (an empty local scratch = a recycled
  cluster) for the SAME `region_id`, and assert the uploaded object still holds ONE row
  for that region (header + 1). This pins the EXISTING gs:// resume behavior unchanged.
  Requires the landmine-4 mock download extension.

**Record the OBSERVED pre-fix result of EACH honestly. Do NOT contrive a failure.**
Expected (verify, do not assume): (a) and (b) FAIL pre-fix — the bucket gets clobbered
and nothing raises. (c) and (d) likely PASS pre-fix — (c) is today's correct path; (d)
pins behavior that was intended but, per landmine 4, has never actually been exercised by
any test. Report exactly what you observe; if something incidentally passes pre-fix, SAY
SO rather than faking a RED.
  </behavior>

  <action>
1. **RED first.** Extend `_MockGsutil` per landmines 2/3/4:
   - a capability to raise a genuinely non-absent stat error (INDETERMINATE), distinct
     from `stat_error_uris`;
   - a capability to make a `cp` fail;
   - direction dispatch on `cp` (src `gs://` → download; else upload) + contents storage;
   - CORRECT the absent stderr to real gsutil's plural `No URLs matched: gs://...`;
   - keep `stat_error_uris` and `prestaged={uri: <int>}` **byte-identical** for the 6
     pre-existing call sites (:705, :735, :775, :799, :814, :838).
   Add tests (a)-(d). Run the single file, record observed pre-fix results.

2. **GREEN.** In `src/python/run_native_ld_panel.py`, add a NEW fail-CLOSED tri-state
   classifier (do NOT touch `_gsutil_object_size` or `_existing_region_npz_gs` — landmine
   1). Rewrite ONLY the seed block in `append_panel_row` (~:533-543) per `<the_fix>`.
   Give the new helper a docstring that states WHY it is fail-CLOSED while
   `_gsutil_object_size` is fail-OPEN (the two callers' opposite failure-safety
   requirements — the root cause above). Actionable, cause-distinguishing error text;
   `raise ... from exc`.

3. Do NOT change or reorder `_PANEL_COLUMNS`. Do NOT weaken u22's header guard
   (`fe375e7`, :488-506). Do NOT touch the m3-07a RED. Tests :392/:1281/:1590 stay green.

4. **STOP conditions** — halt and report, do not improvise:
   - the full-suite FAILED count drops below 15 (→ m3-07c was built — see
     `<forbidden_scope>`);
   - any failure OTHER than the 15 known `ModuleNotFoundError` appears (→ regression);
   - :814 or any of the 6 `_MockGsutil` call sites changes behavior.
  </action>

  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_run_native_ld_panel.py -q</automated>
    <automated>git diff --stat -- src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R src/python/condition_ld_matrix.py   # MUST be EMPTY (frozen contracts, 0-line diff)</automated>
    <automated>git diff -- tests/m3/test_run_native_ld_panel.py | grep -n "^-" | grep -v "^-  *#" || true   # inspect: NO deletion may alter :814's stat_error_uris semantics</automated>
    <automated># FULL suite ~6.5 min — EXCEEDS a 120s Bash timeout. MUST be backgrounded (run_in_background=true) or nohup'd to a log and polled; do NOT run it in the foreground.
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q</automated>
  </verify>

  <done>
- Single file `tests/m3/test_run_native_ld_panel.py` GREEN, including :814 (unmodified)
  and :392/:1281/:1590.
- Tests (a) and (b) each assert BOTH `raises` AND bucket-object-unchanged (byte/size
  identical) AND no `cp` to the panel URI.
- Test (c) proves no false trip on the legitimate first region (real gsutil plural
  `No URLs matched:` signature).
- Test (d) proves dedup survives a simulated recycle via a real (mocked) download seed.
- Observed pre-fix result of each of (a)-(d) recorded honestly in the summary.
- **FULL `tests/m3`: `15 failed / 401+N passed / 31 skipped`** where N = the number of new
  tests added (expected 4 → **15 failed / 405 passed / 31 skipped**). Baseline at HEAD
  `606f293` was **15 failed / 401 passed / 31 skipped**. The 15 failures MUST remain the
  same 15 `ModuleNotFoundError`s, split exactly **9 + 6**. Any OTHER failure = regression
  → STOP. A count BELOW 15 → 07c was built → STOP.
- Frozen contracts: 0-line diff.
- `_gsutil_object_size` and `_existing_region_npz_gs` UNCHANGED (`git diff` shows no hunk
  touching :186-217).
- Summary enumerates all 6 `_MockGsutil(` call sites and states why the extension is
  byte-identical for each (the m3-07b `_MockPlink` precedent), including the explicit
  reasoning that the stderr string change is safe for :814 because `_gsutil_object_size`
  catches ALL exceptions and returns None regardless of stderr.
- ONE atomic commit, **explicit paths only**:
  `git add src/python/run_native_ld_panel.py tests/m3/test_run_native_ld_panel.py`
  — NEVER `git add -A` / `git add .` on this GPFS tree.
  </done>
</task>

</tasks>

<forbidden_scope>
- **Do NOT start m3-07c.** Do NOT create `occlusion_present_rate_scan.py` or
  `drop_occluded_from_sumstats.py`. The 15 `ModuleNotFoundError` failures MUST STAY RED,
  split exactly **9 + 6**. **A DROP BELOW 15 FAILED = 07c was built → STOP.**
- **Do NOT touch the AoU perimeter** — no real gsutil/gcloud/network. Everything through
  the monkeypatched `drv._run_gsutil` seam.
- **FROZEN CONTRACTS, 0-line diff:** `src/python/plink_ld_to_npz.py`,
  `src/scripts/ld_npz_to_rds.R`, `src/python/condition_ld_matrix.py`.
- Do NOT change/reorder `_PANEL_COLUMNS`. Do NOT touch the m3-07a RED. Do NOT weaken
  u22's header guard (`fe375e7`).
- **Pre-existing dirty — do NOT stage:** `.claude/settings.json`,
  `.planning/quick/260625-r6m-*/260625-r6m-SUMMARY.md`, `tests/m3/sparse_parent_benchmark.tsv`.
</forbidden_scope>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| driver → GCS bucket (`gsutil` subprocess) | The bucket's state is untrusted/indeterminate under transient failure; today the driver infers "absent" from an unclassified error and destroys durable state on that inference. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-vxz-01 | Tampering (destructive overwrite of durable provenance) | `append_panel_row` seed block ~:533-543 | mitigate | Tri-state fail-CLOSED classification; RAISE on INDETERMINATE; never `cp` over the bucket object without a positively-established seed. |
| T-vxz-02 | Tampering (known-present object overwritten after a failed seed) | `append_panel_row` `except Exception: pass` :540-541 | mitigate | Remove the swallow; a cp failure against a PRESENT object RAISES. Post-cp existence assertion closes the "cp succeeded but no file" door. |
| T-vxz-03 | Repudiation (loss surfaces only at analysis time; the fire self-reports success) | `.npz`-gated resume skip :605-608 | accept | Out of scope for this fix — the `.npz` gate is load-bearing and correct. Mitigated indirectly: the panel TSV is rebuildable from the banked `.npz`, and the fix converts a silent loss into a loud, actionable, zero-cost refusal. |
| T-vxz-04 | Denial of Service (a fail-CLOSED guard false-tripping halts an ~11-day fire at region 1) | new absent-signature detection | mitigate | Test (c) pins the legitimate first-region path against **real** gsutil's `No URLs matched:` output; detection tolerates singular+plural, case-insensitively; the mock's stderr is corrected to the real string so the test models reality (landmine 3). |
</threat_model>

<verification>
- `git diff` on `src/python/run_native_ld_panel.py` shows **no hunk** touching :186-217
  (`_gsutil_object_size` / `_existing_region_npz_gs`).
- `tests/m3/test_run_native_ld_panel.py:814` is textually unmodified and GREEN.
- Frozen contracts: `git diff --stat` empty for all three.
- Full `tests/m3` (backgrounded): 15 failed / 405 passed / 31 skipped; the 15 are the
  same `ModuleNotFoundError`s, 9 + 6.
</verification>

<success_criteria>
P3a and P3b are both closed by a fail-CLOSED refusal proven by two tests that assert the
bucket object is byte-unchanged; the legitimate first-region and happy-path/recycle-dedup
behaviors are pinned unchanged by two regression tests; `_existing_region_npz_gs`'s
fail-OPEN resume semantics are untouched; the 07c RED stays exactly 15 (9 + 6); frozen
contracts have a 0-line diff; one atomic explicit-path commit.
</success_criteria>

<output>
After completion, write `.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-SUMMARY.md`.
Record: the observed pre-fix result of each of tests (a)-(d) **honestly** (do not fake a
RED); the 6-call-site `_MockGsutil` byte-identical blast-radius enumeration; the exact
before/after full-suite counts.
</output>
</content>
</invoke>
