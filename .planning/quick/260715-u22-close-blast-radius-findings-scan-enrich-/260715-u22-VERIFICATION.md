---
phase: 260715-u22
verified: 2026-07-16T03:05:00Z
status: passed
score: 10/10 must-haves verified
overrides_applied: 0
---

# Quick 260715-u22: Close Blast-Radius Findings (scan→enrich seam + panel-TSV header) Verification Report

**Task Goal:** close two PRE-EXISTING blast-radius findings — (1) the scan→enrich seam
key contract in `src/python/occlusion_manifest.py` (a silent-wrong-data defect
blocking m3-07c), and (2) panel-TSV header/arity reconciliation in
`run_native_ld_panel.py::_append_panel_row_local` (a production precondition for the
~11-day billed fire).
**Verified:** 2026-07-16T03:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This verification deliberately did NOT trust the SUMMARY's narrative or the new test
suite's own assertions. Instead, throwaway probe scripts (under the assigned scratchpad)
independently exercised `enrich_occlusion_manifest` and `_append_panel_row_local`
directly with hand-built inputs matching the prompt's four required cases, and — to
verify the SUMMARY's honesty claims about pre-fix REDs — the PRE-FIX version of both
source files (`git show e3075ae:...`) was loaded via `importlib.util` and probed with
the identical inputs.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | present_rate dict keyed `{(chr,pos_grch37): {...}}` populates the matching row | ✓ VERIFIED | Independent probe: `present_rate={(1,5982778):{...}}` → snpC row `traits_present="bmi,ldl"`, `n_traits_present=2.0`; other 4 rows NA |
| 2 | `(chr, pos_grch37)` key derived POST-LIFT inside `enrich_occlusion_manifest` | ✓ VERIFIED | Code: `keys = [_present_rate_key(c,p) for c,p in zip(out["chr"], out["pos_grch37"])]` — `out` is the post-`add_grch37_positions` DataFrame |
| 3 | Row that does not lift → pd.NA in trait columns, deliberately | ✓ VERIFIED | `_present_rate_key` returns `None` when `pos_grch37 is None or pd.isna(...)`; loop writes `pd.NA` for `k is None` |
| 4 | Non-empty present_rate + ≥1 liftable row + 0 matches → raises ValueError naming the contract | ✓ VERIFIED | Independent probe (Case C): `present_rate={(99,1):...}` on the real 5-row liftable manifest → `ValueError: "...must be keyed on (chr, pos_grch37)..."` |
| 5 | Manifest with ZERO liftable rows + non-empty present_rate → does NOT raise | ✓ VERIFIED | Independent probe (Case D): all 5 rows mutated unliftable, legit present_rate `{(1,5982778):...}` → no raise, all `traits_present` NA |
| 6 | Docstring declares the real `{(chr,pos_grch37):...}` GRCh37 post-lift contract + exact raise boundary | ✓ VERIFIED | Read `occlusion_manifest.py:330-353` — states the contract and the three-way boundary verbatim |
| 7 | `_append_panel_row_local` RAISES on stale header, naming both column lists + rotate instruction | ✓ VERIFIED | Independent probe: 8-col header + 9-col row → `ValueError` message includes `found:`/`expected:` lists and "Rotate or delete" |
| 8 | Matching header still appends normally (no false trip) | ✓ VERIFIED | Independent probe: matching 9-col header, append regB → no raise, 2 rows, header appears once, re-append is dedup no-op |
| 9 | 15 m3-07c ModuleNotFoundError failures stay RED; no other test regresses | ✓ VERIFIED | Full `tests/m3` re-run (independent, this session): **15 failed, 401 passed, 31 skipped** in 389.33s; `FAILED` lines belong ONLY to `test_occlusion_lockstep_drop.py` and `test_occlusion_present_rate_scan.py`; split exactly 9/6 by module name |
| 10 | Three frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py) 0-line diff | ✓ VERIFIED | `git diff --stat e3075ae..HEAD -- <3 files>` → empty output |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/occlusion_manifest.py` | joins on `(chr,pos_grch37)` post-lift, liftable-scoped guard, corrected docstring | ✓ VERIFIED | `git show --stat 63bdb59`: +77/-5 lines; diff isolated to `_present_rate_key`, the join block, and the docstring — no other function touched |
| `tests/m3/test_occlusion_manifest.py` | 4 new tests (A/B/C/D) | ✓ VERIFIED | 15 passed (11 baseline + 4), 0 skipped, confirmed by direct pytest run this session |
| `src/python/run_native_ld_panel.py` | `_append_panel_row_local` reconciles header before dedup | ✓ VERIFIED | `git show --stat fe375e7`: +19 lines only, inserted exactly between `existing = pd.read_csv(...)` (line 487) and the dedup read at line 507 |
| `tests/m3/test_run_native_ld_panel.py` | 2 new tests (stale-header raises / matching-header appends) | ✓ VERIFIED | 54 passed (52 baseline + 2), confirmed by direct pytest run this session |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `enrich_occlusion_manifest` | `test_occlusion_present_rate_scan.py:72`'s key shape | `(chr,pos_grch37)` tuple lookup post-lift | ✓ WIRED | The key `(1, 5_982_778)` is byte-identical between the 07c RED and the probe used here; independently confirmed to populate the matching row |
| `enrich_occlusion_manifest` | `ValueError` on zero matches among liftable rows | `keys_present` scoping | ✓ WIRED | Guard reads `keys_present = [k for k in keys if k is not None]`; raise condition is `if keys_present and not any(...)` — confirmed by both probe C (raises) and probe D (does not raise) |
| `_append_panel_row_local` | `_PANEL_COLUMNS` | `list(existing.columns) != _PANEL_COLUMNS` before dedup read | ✓ WIRED | Code ordering confirmed: the raise check (line 497) executes strictly before `existing["region_id"]` access (line 507) — a shifted stale file cannot mask the diagnosis behind a KeyError |

### Pre-fix vs Post-fix Behavioral Trace (independent, not from the test suite)

| Case | Pre-fix (e3075ae, probed directly) | Post-fix (HEAD, probed directly) |
|---|---|---|
| Tuple key `(1,5982778)` lookup | `traits_present = nan` (the bug — silent miss) | `traits_present = "bmi,ldl"` (populates) |
| Wholly-mismatched present_rate on liftable manifest | NO RAISE — silent all-NA (the bug) | `ValueError` naming the `(chr,pos_grch37)` contract |
| Wholly-unliftable manifest + legit present_rate | NO RAISE, all NA (correct, incidental) | NO RAISE, all NA (correct, by design) |
| Stale 8-col header + 9-col row append | NO RAISE — produced `field counts: [8, 8, 9]` (the bug) | `ValueError` naming both column lists, "Rotate or delete" |

This directly reproduces the exact defect described in the task prompt and independently
confirms the SUMMARY's "honest record" claims (see Requirements/Honesty section below).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Seam populates on RED's exact key | probe script, Case A | `traits_present="bmi,ldl"` | ✓ PASS |
| Seam raises on total miss (liftable rows exist) | probe script, Case C | `ValueError` raised | ✓ PASS |
| Seam does not raise on zero-liftable manifest | probe script, Case D | no raise, all NA | ✓ PASS |
| Panel guard raises on stale header | probe script | `ValueError` raised, actionable message | ✓ PASS |
| Panel guard does not false-trip on matching header | probe script | no raise, dedup preserved | ✓ PASS |
| Panel guard does not false-trip on absent file | probe script | file created fresh | ✓ PASS |
| Full suite regression check | `pytest tests/m3 -q` (backgrounded, ~6.5 min) | 15 failed / 401 passed / 31 skipped, split 9/6 | ✓ PASS |
| Pre-fix reproduction of both bugs | probes against `git show e3075ae:...` loaded via importlib | bugs reproduced exactly as SUMMARY claims | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| BR-260715-01 | 260715-u22-PLAN.md | scan→enrich seam key contract (blocks m3-07c) | ✓ SATISFIED | Truths 1-6, key links 1-2 |
| BR-260715-02 | 260715-u22-PLAN.md | panel-TSV header reconciliation (production precondition) | ✓ SATISFIED | Truths 7-8, key link 3 |
| D-M3-10 | 260715-u22-PLAN.md | exclude-in-lockstep provenance is publishable (loud-guard, no silent success) | ✓ SATISFIED | Both new guards raise loudly rather than publish silent pd.NA/ragged data, consistent with the decision |
| REQ-AOU-LD-EGRESS | 260715-u22-PLAN.md | AoU controlled-tier egress rule | ✓ SATISFIED (unaffected) | `git diff` on the `gs://` mirror code path (`append_panel_row`, `_gsutil_object_size`) is empty — no perimeter-adjacent code touched |

BR-260715-01/02 are quick-task-local finding IDs (not present in `.planning/REQUIREMENTS.md`,
which is expected — they are blast-radius-sweep findings, not phase-level roadmap
requirements). No orphaned requirements found.

### Anti-Patterns Found

None. Scanned all 4 modified files for TODO/FIXME/placeholder/empty-return patterns.
The one grep hit (`occlusion_manifest.py:39`: "...and that is not a placeholder") is a
docstring explicitly *disclaiming* placeholder status for an unrelated pre-existing
field — a false positive, not a defect.

### Scope Discipline

- **07c containment:** `src/python/occlusion_present_rate_scan.py` and
  `src/python/drop_occluded_from_sumstats.py` confirmed absent (`ls` → "No such file or
  directory" for both). `tests/m3/test_occlusion_present_rate_scan.py` has a 0-line diff
  (`git diff --stat e3075ae..HEAD` → empty). The 15 ModuleNotFoundError failures are
  unchanged and split exactly 9/6 as pinned.
- **`_PANEL_COLUMNS` unchanged:** its definition block (`run_native_ld_panel.py:101-103`)
  has no diff; the session diff on this file touches ONLY the new guard block. Pinned
  tests `:1281` (n_dropped_monomorphic) and `:1590` (n_dropped_occluded) both assert the
  leading-7/trailing positions and both pass.
- **Frozen contracts:** `plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`
  all 0-line diff.
- **P3 (gsutil-blip bucket overwrite, `run_native_ld_panel.py:514-524`) NOT silently
  absorbed.** Confirmed by direct diff: the `gs://`-mirror code path
  (`append_panel_row`'s `_gsutil_object_size`/`_run_gsutil`/`_gsutil_upload` block) has
  a 0-line diff — genuinely untouched. The SUMMARY explicitly flags P3 as "REAL and
  still open" / "Deliberately not touched here (the plan scopes it out)" under its own
  "Out of Scope — NOT absorbed" section. This matches the code exactly: scope
  discipline held.
- **No AoU perimeter contact:** no gsutil/gcloud/network calls were made during this
  verification. m3-06 was not touched. No loop re-fire.

### Honesty Check on the SUMMARY's RED-first Record

The SUMMARY claims Tests A and C were the "true REDs," Test D "passed pre-fix by design"
(pinning, not driving), and Test B is "RED, but not for the reason its name suggests"
(passes its primary NA-assertion pre-fix trivially, but fails on an added positive-control
assertion). This verification independently probed the PRE-FIX module directly (loaded via
`importlib.util` from `git show e3075ae:...`, bypassing the fixed HEAD module entirely) and
confirmed:

- Pre-fix, the tuple-key lookup on the target row yields `nan` (Test A's failure mode,
  confirmed).
- Pre-fix, a wholly-mismatched present_rate on a liftable manifest does NOT raise —
  silent bug, confirmed (Test C's failure mode).
- Pre-fix, a wholly-unliftable manifest + legitimate present_rate does NOT raise — this
  matches Test D passing pre-fix incidentally, confirmed.
- Since pre-fix the tuple-key lookup misses on EVERY row (confirmed nan on the target),
  Test B's own "unlifted row is NA" assertion is trivially true pre-fix (everything is
  NA), while its added "target still joins" assertion would fail — exactly the nuance the
  SUMMARY discloses.

**This disclosure is accurate, not flattering.** No place was found where the SUMMARY
claims more than the code delivers.

### Human Verification Required

None. All must-haves are mechanically verifiable (pytest + direct probes) and were
verified programmatically.

### Gaps Summary

No gaps. All 10 must-have truths verified against the real codebase (not just against the
new test suite's own assertions — independent probes were run against both the post-fix
and pre-fix code). Both commits (`63bdb59`, `fe375e7`) are atomic, independently
revertible, touch only their declared files, and the full `tests/m3` regression run
matches the plan's exact expected counts (15F/401P/31S, split 9/6). Scope was held: 07c
remains unbuilt, frozen contracts are untouched, `_PANEL_COLUMNS` is untouched, and P3 was
explicitly left open and disclosed rather than silently absorbed.

---

*Verified: 2026-07-16T03:05:00Z*
*Verifier: Claude (gsd-verifier)*
