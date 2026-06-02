---
phase: quick-260601-u1b
plan: 1
slug: harden-chr22-smoke-into-tiered-cheap-first
subsystem: m3-aou-afr-ld-panel
tags: [aou, hail, ld-panel, catastrophe-defense, tdd, tiered-validation, forensics]
requires:
  - "260528-jvd Track-4 defensive-code patches (_assert_checkpoint_nonempty, _validate_checkpoint_populated)"
  - "260601-cca env-derive AUX base + suffix-discovery (untouched here)"
provides:
  - "_interval_scaled_du_floor(interval_filter, *, base_floor_bytes) — pure interval-scaled du soft-floor"
  - "_capture_catastrophe_forensics(uri, *, phase, ...) — standalone best-effort forensic capture (never raises)"
  - "AOU-0.5-mechanism-probe_template.ipynb — Tier 0 synthetic 2048-partition probe"
  - "AOU-1-chr22-smoke_template.ipynb — INTERVAL-parameterized (serves Tier 1 nano + Tier 2 chr22)"
  - "TIERED-VALIDATION-RUNBOOK.md — Gate A/B/C decision tree"
affects:
  - "Wave 2 chr22 platform-validation strategy (cheap-first escalation before full-genome rebuild)"
tech-stack:
  added: []
  patterns:
    - "TDD RED->GREEN with watch-it-fail evidence captured at the RED run"
    - "Pure interval-span-scaled helper (no I/O) for the du soft-floor"
    - "Dependency-injected collaborators (lister/copier/http_getter/now/writer) with prod defaults"
    - "Standalone defensive forensics helper (never raises) wired by notebook try/except, NOT injected into the Track-4 guard"
    - "Notebook = JSON; edited via smoke_dev Python json round-trip preserving nbformat 4.5"
key-files:
  created:
    - ".planning/notebooks/AOU-0.5-mechanism-probe_template.ipynb"
    - ".planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/TIERED-VALIDATION-RUNBOOK.md"
    - ".planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/red_fail_output.txt"
  modified:
    - "src/python/aou_ld_panel.py"
    - "tests/m3/test_aou_ld_panel_local.py"
    - ".planning/notebooks/AOU-1-chr22-smoke_template.ipynb"
decisions:
  - "du-floor helper signature: _interval_scaled_du_floor(interval_filter, *, base_floor_bytes) — the interval-span-scaling shape over the explicit-floor shape"
  - "forensics wiring: STANDALONE (NOT injected into _assert_checkpoint_nonempty) — preserves the Track-4 guard raise contract byte-for-byte"
metrics:
  tasks: 3
  files-changed: 6
  commits: 4
  duration: "~1 session"
  completed: 2026-06-01
---

# Phase quick-260601-u1b Plan 1: Harden chr22 smoke into a tiered cheap-first validation sequence — Summary

Demoted the m3-W1 catastrophe defense from a single expensive chr22 smoke into a
tiered, cheap-first gradient (Tier 0 synthetic probe -> Tier 1 nano -> Tier 2
chr22) plus best-effort forensic capture, so the empty-MT failure mode fails as
cheaply and diagnostically as possible BEFORE the full-genome rebuild is
greenlit — without weakening any Track-4 guard.

## What was built

**Task 1 (TDD, code + tests) — commit `344040e`:**
- `_interval_scaled_du_floor(interval_filter, *, base_floor_bytes) -> int`: pure,
  interval-span-scaled DIAGNOSTIC soft-floor. `None` / whole-chromosome keep the
  full base floor (Tier-2 chr22 check unweakened); a span-bounded interval scales
  the floor down proportionally, clamped into `[MIN_DU_FLOOR_BYTES (2 MB),
  base_floor_bytes]`. Demotes the notebook's hardcoded 50 MB floor that
  false-positived a ~2 Mb nano fire.
- `_capture_catastrophe_forensics(uri, *, phase, lister, copier, http_getter,
  bucket, ...)`: STANDALONE, best-effort, NEVER raises. Records the
  `_SUCCESS`-mtime-vs-part-mtimes `hypothesis_flag`
  (`hail_finalize_on_empty` / `kill_interrupted_write` / `indeterminate`), MT
  listing + entries sizes, a `/tmp/hail.log` preserve, a Spark-REST snapshot, and
  a `_forensics/<phase>_capture.json`. Collaborators injected as kw params with
  prod defaults.
- 8 new tests (4 for A, 4 for B) added RED-first.

**Task 2 (notebooks) — commit `4c2ad70`:**
- NEW `AOU-0.5-mechanism-probe_template.ipynb` (Tier 0): byte-faithful cores=1/5g
  lever; synthetic `range_matrix_table(50_000, 2_000).repartition(2048)` write
  (ZERO source read / ZERO QC); `_assert_checkpoint_nonempty(phase='probe')` HARD
  gate; a few-MB (NOT 50 MB) scaled du SOFT-floor; forensic-capture-on-fail;
  honest-caveat + Gate-A markdown.
- `AOU-1` parameterized by a single `INTERVAL` variable (Cell 1c) threaded into
  all 3 `load_qc_cohort` interval-filter args + all 3 du-floor cells (Task-1 floor
  wired in; cells RETAINED, INTERVAL-derived `_suffix`) + INTERVAL-aware Cell 7 /
  summary. du-floor asserts wrapped in forensic-capture-on-fail. All Track-4 cells
  retained. Tiered rigor caveat in Cell 0 + closing markdown.

**Task 3 (runbook) — commit `f69a04f`:**
- `TIERED-VALIDATION-RUNBOOK.md`: Gate A (Tier 0 probe, 64 vCPU, ~$1-3), Gate B
  (Tier 1 nano, same 64 vCPU, ~$1-3), Gate C (Tier 2 chr22, 384 vCPU, ~$35-80),
  cluster specs, $ envelopes, NON-preemptible discipline, decision rules,
  watchpoints, the forensics/hypothesis-distinguisher section, and the cheap->
  expensive escalation map ending in the full-genome rebuild or the 1000G AFR
  documented fallback.

## TDD watch-it-fail evidence (quoted from `red_fail_output.txt`)

The RED output was captured AT the moment of the failing run, before ANY
implementation. Both helper sets failed with `ImportError` (the import does not
exist yet) — confirming the tests genuinely fail pre-implementation.

**RED (A) — `_interval_scaled_du_floor`** (`4 failed, 72 deselected in 0.17s`):
```
E   ImportError: cannot import name '_interval_scaled_du_floor' from 'aou_ld_panel' (/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/aou_ld_panel.py)
```
(all 4 of: `test_interval_scaled_du_floor_nano_interval_no_false_positive`,
`..._whole_chromosome_keeps_base`, `..._none_keeps_base`, `..._scales_with_span`.)

**RED (B) — `_capture_catastrophe_forensics`** (`4 failed, 72 deselected in 0.09s`):
```
E   ImportError: cannot import name '_capture_catastrophe_forensics' from 'aou_ld_panel' (/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/aou_ld_panel.py)
```
(all 4 of: `test_capture_forensics_flags_hail_finalize_signature`,
`..._flags_kill_interrupted_signature`, `..._never_raises_when_collaborators_raise`,
`..._writes_parseable_capture_json`.)

After implementing both helpers to GREEN, the scoped runs returned `4 passed`
each.

## Final test count

`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_aou_ld_panel_local.py -q`
(Python 3.11):

> **65 passed, 11 skipped in 0.27s**

Baseline pre-task was 57 passed + 11 skipped; the +8 are the new RED-then-GREEN
tests. Zero failures, zero regressions.

## Chosen du-floor helper signature + rationale

**`_interval_scaled_du_floor(interval_filter: str | None, *, base_floor_bytes: int)
-> int`** — the **interval-span-scaling** shape (NOT the explicit pass-through
`_du_floor_for_tier`). Rationale: it makes the floor interval-agnostic and
self-scaling from the single `INTERVAL` notebook variable, so the notebook does
not have to encode a separate per-tier floor constant — one `INTERVAL` knob
drives the call sites, the suffix, AND the floor. Whole-chromosome / `None`
return `base_floor_bytes` unchanged so Tier-2 chr22 is never down-scaled; a
span-bounded interval scales by `span_bp / chrom_len_bp` clamped to
`[2 MB, base]`. Pure, monotonic in span, fully unit-tested.

## Forensics wiring decision + rationale

**STANDALONE** — `_capture_catastrophe_forensics` is invoked by the notebook
cells inside `except Exception: _capture_catastrophe_forensics(...); raise`, and
is **NOT** injected into `_assert_checkpoint_nonempty`. Rationale (the
lower-risk option, documented in the helper docstring + the never-raise test):
keeping it standalone means the Track-4 guard's hard-fail/raise contract
(`count_rows()==0 or count_cols()==0` -> `RuntimeError`) is **byte-for-byte
unchanged**. The notebook `raise` is what halts the cell; the capture only adds
diagnostics and is wrapped so it can never take down the cell it is diagnosing
(every sub-step is `try/except`; on total collaborator failure it still returns
a sentinel dict carrying `phase` + `uri`).

## Track-4 guard NOT weakened (git-diff confirmation)

`_assert_checkpoint_nonempty` body is **byte-identical** pre/post task:

- Baseline (commit `c89008c`, pre-task) md5 of the function block:
  `16caccec0678a9e57f38569cb3e5b801`
- Current (`HEAD`/`f69a04f`) md5 of the same block:
  `16caccec0678a9e57f38569cb3e5b801`
- **Verdict: BYTE-IDENTICAL.**
- `git diff c89008c HEAD -- src/python/aou_ld_panel.py` is **purely additive**
  (no removed lines); the diff hunk begins `@@ -753,6 +753,314 @@` (insertions
  start immediately after the guard's closing line at 753). The only diff matches
  on `_assert_checkpoint_nonempty` / `count_rows()` / `count_cols()` are inside
  the NEW helper docstrings/comments (references to the guard), not edits to it.
- The 260601-cca env-derive / suffix-discovery code (`_resolve_aux_base`,
  `_resolve_aux_file`, `_intermediate_checkpoint_uri`) is untouched (no signature
  changes; verified via scoped diff).

## Deviations from Plan

None — the plan executed exactly as written. The du-floor helper signature and
the forensics wiring were planner-delegated judgment calls; both are recorded
above with rationale.

## Known Stubs

None. The notebooks are templates Carter fires later (by design — this task
launches nothing and spends nothing); the synthetic-MT probe and the
INTERVAL-parameterized cells are fully wired (no hardcoded empty data, no
placeholder text). The forensic helper writes real capture JSON in tests.

## Repo-only confirmation

This task produced REPO ARTIFACTS ONLY (2 helpers + 8 tests + 2 notebooks +
1 runbook + RED evidence). It launched NOTHING on AoU and spent NOTHING. No
Hail / gsutil / cloud command was run. Carter holds every launch / compute / $
trigger.

## Commits

- `344040e` — feat(quick-260601-u1b): interval-scaled du-floor + standalone catastrophe-forensics helpers (TDD)
- `4c2ad70` — feat(quick-260601-u1b): add Tier-0 AOU-0.5 mechanism probe + parameterize AOU-1 by INTERVAL
- `f69a04f` — docs(quick-260601-u1b): author tier-gated chr22 validation runbook (Gate A/B/C)

## Self-Check: PASSED

All claimed artifacts verified on disk and all commits verified in git history:
- FOUND: `src/python/aou_ld_panel.py` (+ symbols `_interval_scaled_du_floor`, `_capture_catastrophe_forensics`)
- FOUND: `tests/m3/test_aou_ld_panel_local.py`
- FOUND: `.planning/notebooks/AOU-0.5-mechanism-probe_template.ipynb`
- FOUND: `.planning/notebooks/AOU-1-chr22-smoke_template.ipynb`
- FOUND: `.planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/TIERED-VALIDATION-RUNBOOK.md`
- FOUND: `.planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/red_fail_output.txt`
- FOUND: `.planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/260601-u1b-SUMMARY.md`
- FOUND commits: `344040e`, `4c2ad70`, `f69a04f`

---

## Remediation (post-verify/review)

A verification + code-review pass found 1 runtime BLOCKER and 3 INFO review items. All four fixed in two atomic commits (`c522032` notebook, `867d30a` code+tests).

### FIX 1 — BLOCKER (verifier): AOU-1 du-floor cells referenced undefined `_MIN_BYTES`
The three du-floor cells (3.5 / 4.5 / 5.5; notebook cell indices 5 / 7 / 9) asserted `_size_bytes > _MIN_BYTES`, but the floor variable was renamed to `_DU_FLOOR_BYTES` (computed in the INTERVAL/setup cell, Cell 1c). `_MIN_BYTES` was never assigned anywhere in the notebook → `NameError` at runtime, halting the cell BEFORE the forensic-capture-on-fail branch and disabling the soft-floor check on every tier fire.
- **Fix:** replaced all 6 occurrences (`assert` + f-string message × 3 cells) `_MIN_BYTES` → `_DU_FLOOR_BYTES` via a raw byte-level substitution (`_DU_FLOOR_BYTES` is a strict superset string and `_MIN_BYTES` appears only in the three du-floor cell sources). Original JSON encoding preserved (em-dash `—` escapes intact, no `id`-field churn) → minimal **6-line diff**. nbformat re-validated VALID. The `count_rows>0/count_cols>0` hard gate is unaffected.
- **Proof:** json round-trip asserts `'_MIN_BYTES' not in source`, each du-floor cell (5/7/9) contains `assert _size_bytes > _DU_FLOOR_BYTES` + the message reference (≥2 `_DU_FLOOR_BYTES` per cell), and `_DU_FLOOR_BYTES` is assigned in the setup cell. All PASS.
- **Commit:** `c522032`. The one-shot edit was an inline `python -` heredoc — no stray `_edit_notebooks.py` left behind.

### FIX 2 — IN-01 (code, TDD RED→GREEN): coerce Hail string/mixed-type mtimes in the distinguisher
`_capture_catastrophe_forensics` compared part mtimes vs the `_SUCCESS` mtime with a naive numeric `m > success_mtime`, assuming int/float epochs. `hl.hadoop_ls` (Hail 0.2.x) can return `modification_time` as a FORMATTED STRING. Two failure modes resulted: (a) a mixed str-vs-int pair raised `TypeError`, caught by the outer never-raise guard → `hypothesis_flag` silently degraded to `'indeterminate'`; (b) same-format strings compared LEXICOGRAPHICALLY, which inverts the flag across digit-length / date boundaries. This destroys the W1-catastrophe diagnostic exactly when it matters.
- **RED fail line (appended to `red_fail_output.txt` under `### IN-01 mtime-coerce RED`, captured at the moment of the RED run, pre-implementation):**
  `AssertionError: mixed str/int mtimes must coerce + resolve kill_interrupted_write (not indeterminate via TypeError); got 'indeterminate'` — plus the uneven-epoch-string inversion failure (`test_capture_forensics_flags_finalize_with_uneven_epoch_strings`). `2 failed, 81 deselected`.
- **GREEN:** added `_coerce_mtime(value) -> float | None` applied to BOTH sides before comparison. The raw mtimes are still stored verbatim in the capture JSON; coercion is only for the flag decision. The normalizer NEVER raises (every parse guarded); an uncoercible value returns `None` and is dropped from the comparable set; `'indeterminate'` remains only when nothing is comparable.
- **`_coerce_mtime` formats supported:** `int`/`float` epochs (verbatim → float); numeric-as-string epochs (`'1700000000'`, any digit-length — compared numerically, NOT lexically); `'%Y-%m-%d %H:%M:%S'` (the historical Hail space form); ISO `'%Y-%m-%dT%H:%M:%S'`; a trailing `Z` (UTC designator, stripped before parse); and the `.%f` microsecond variants of both the space and `T` forms. `bool` is explicitly rejected (returns `None`, not `1.0`/`0.0`). Returns `None` for empty/garbage strings and any other type.
- **Commit:** `867d30a`.

### FIX 3 — IN-02 (tests): pin uncovered production no-bucket + partial-JSON never-raise paths
- (a) `test_capture_forensics_never_raises_with_bucket_none_and_env_unset` — `bucket=None` with `WORKSPACE_BUCKET` removed via `monkeypatch.delenv(...)` (the literal notebook default-arg path) → returns a best-effort partial dict carrying `phase` + `uri`, `forensics_dir is None`, no raise.
- (b) `test_capture_forensics_writes_partial_json_when_collaborators_raise` — when lister/copier/http_getter all raise, the `_forensics/<phase>_capture.json` is STILL written, round-trips through `json.loads`, and its `errors` list is non-empty (the partial-JSON promise).
- **Commit:** `867d30a`.

### FIX 4 — IN-03 (cleanup): deleted dead local `success_uri`
`success_uri = f"{uri.rstrip('/')}/_SUCCESS"` was assigned but never read (the `_SUCCESS` mtime is found by scanning the listing). Removed. **Commit:** `867d30a`.

### New tests + final suite count
**+7 new tests** (5 IN-01 string/mixed-type/uneven-epoch + 2 IN-02 production-path pins). Full suite re-run:
`/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/ -q` → **109 passed / 27 skipped** (was 102 passed / 27 skipped at remediation entry; +7 new, all green, zero regressions).

### Constraint re-confirmation
- **`_assert_checkpoint_nonempty` is byte-identical** — extracted from `HEAD` and the working tree and md5-compared: both `16caccec0678a9e57f38569cb3e5b801`. Zero lines of the guard touched (the only source removals are the dead `success_uri` line and the 3-line pre-coercion comparison block, both inside `_capture_catastrophe_forensics`; everything else is additive).
- **260601-cca functions untouched** — `git diff` confirms zero changes to `_resolve_aux_base` / `_resolve_aux_file` / `_intermediate_checkpoint_uri`.
- Explicit git paths only (no `git add -A/.`); `Co-Authored-By` trailer on both commits; launches nothing, spends nothing.

### Remediation commits
- `c522032` — fix(quick-260601-u1b): AOU-1 du-floor cells reference `_DU_FLOOR_BYTES` not undefined `_MIN_BYTES`
- `867d30a` — fix(quick-260601-u1b): coerce Hail mtime strings in forensics distinguisher + drop dead `success_uri` (TDD)
