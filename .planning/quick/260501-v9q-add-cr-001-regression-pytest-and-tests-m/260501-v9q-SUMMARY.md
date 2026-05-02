---
phase: 260501-v9q
plan: 01
subsystem: m3-aou-afr-ld-panel-build (regression scaffold)
tags: [test, regression, ld_panel, CR-001, pytest, m3]
requires:
  - src/python/ld_panel.py (post-CR-001 signature)
  - src/snakemake/rules/finemap.smk (production call site)
  - tests/m3/conftest.py (sys.path shim)
provides:
  - tests/m3/__init__.py (empty package marker, parity with tests/m1/)
  - 3 new regression tests in tests/m3/test_ld_panel_resolver.py
  - Static-grep guard on finemap.smk resolve_ld_path call site
affects:
  - tests/m3/ (8 -> 11 resolver tests)
key-files:
  created:
    - tests/m3/__init__.py
  modified:
    - tests/m3/test_ld_panel_resolver.py
decisions:
  - "Static-grep test uses [^)]* (not [\\s\\S]*?) because production call has no nested parens in the resolve_ld_path arg list."
  - "Regression-bite proof confirmed: 1kg-fallback test fails under pre-fix simulation; AoU-head test does not bite (AoU template is {region_id} only) — kept anyway as documentation/contract."
metrics:
  tests-before: 8
  tests-after: 11
  duration-min: 4
  completed: 2026-05-01
---

# Quick 260501-v9q: CR-001 Regression Tests for ld_panel Resolver Summary

## One-liner

Locked the CR-001 fix (commit 6d2e753) behind 3 hermetic pytest cases plus a `tests/m3/__init__.py` parity scaffold; resolver suite went from 8 -> 11 tests, all green.

## What Was Built

### tests/m3/__init__.py (created, empty)

Empty package marker matching the `tests/m1/__init__.py` precedent.
Parity scaffold only — no behavioral change.

### tests/m3/test_ld_panel_resolver.py (modified)

Added one stdlib import (`import re`) and three new regression tests
appended at end-of-file. The 8 pre-existing tests are byte-identical to
their prior content.

**Test A — `test_resolver_distinct_region_id_and_region_safe_aou_head`**
Exercises DISTINCT `region_id="m2_region_00067"` vs `region_safe="FTO_16q12"`
with only the AoU bucket file present (`base/AFR_aou/m2_region_00067.rds`).
Asserts:

- Returned path equals the AoU path.
- Basename uses region_id naming (not region_safe).
- region_safe slug does NOT leak into the AoU path.

**Test B — `test_resolver_distinct_region_id_and_region_safe_1kg_fallback`**
DISTINCT values; AoU + HGDP buckets empty; only the legacy 1kg bucket has
`base/AFR/FTO_16q12.rds`. Asserts:

- Returned path equals the 1kg path.
- Basename uses region_safe naming (not region_id).
- region_id does NOT leak into the 1kg path.

This is the test that decisively bites pre-CR-001 code (see
"Regression-bite Proof" below).

**Test C — `test_finemap_smk_calls_resolver_with_both_kwargs`**
Static-grep contract test on `src/snakemake/rules/finemap.smk`. Asserts the
production call site contains `resolve_ld_path(...)` with both `region_id=`
and `region_safe=` kwargs. A future refactor that drops one kwarg (and
silently regresses to the back-compat single-value substitution) is caught
at the static-text level before any pipeline run.

## Verification Result

```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \
    -m pytest tests/m3/test_ld_panel_resolver.py -v
============================= test session starts =============================
platform linux -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
collected 11 items

tests/m3/test_ld_panel_resolver.py::test_resolver_returns_first_existing_path PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_strict_mode_raises PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_pin_override PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_unknown_ancestry_trans_chain PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_region_id_vs_region_safe_substitution PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_no_match_raises PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_pin_with_unknown_source_raises PASSED
tests/m3/test_ld_panel_resolver.py::test_production_pipeline_yaml_loads PASSED
tests/m3/test_ld_panel_resolver.py::test_resolver_distinct_region_id_and_region_safe_aou_head PASSED   <- NEW
tests/m3/test_ld_panel_resolver.py::test_resolver_distinct_region_id_and_region_safe_1kg_fallback PASSED <- NEW
tests/m3/test_ld_panel_resolver.py::test_finemap_smk_calls_resolver_with_both_kwargs PASSED            <- NEW

============================== 11 passed in 0.50s =============================
```

Pass condition met: **11 passed**.

## Regression-bite Proof (Audit)

Per the plan's optional secondary check, temporarily simulated the pre-fix
code by replacing the `format()` call in `src/python/ld_panel.py` line 85:

- Post-fix (HEAD): `entry["path"].format(region_id=region_id, region_safe=region_safe)`
- Pre-fix sim: `entry["path"].format(region_id=region_id, region_safe=region_id)`

Re-ran pytest:

```
FAILED tests/m3/test_ld_panel_resolver.py::test_resolver_distinct_region_id_and_region_safe_1kg_fallback
========================= 1 failed, 10 passed in 0.20s =========================
```

`test_resolver_distinct_region_id_and_region_safe_1kg_fallback` fired
(FileNotFoundError: "No LD panel found for m2_region_00067 AFR") — correctly
identifying the silent fallback bug CR-001 fixed.

**Nuance — Test A (AoU-head) does NOT bite pre-fix code.** Under the pre-fix
substitution (both placeholders -> region_id), the AoU template
`{region_id}.rds` still resolves to `base/AFR_aou/m2_region_00067.rds`,
which exists in Test A's setup. So Test A passes with both the pre-fix and
post-fix resolver. **Test B is the decisive regression-bite test** — it
exercises the 1kg-fallback path where the legacy bucket only has
`{region_safe}`-named files, so the pre-fix code looks for the wrong
filename and misses.

Test A is retained as a positive contract for the AoU-head behavior under
the post-fix kwarg-passing call form (locks that the resolver correctly
substitutes `region_id` into AoU templates without leaking `region_safe`).
Together with Test C (call-site static guard), this gives full regression
coverage of CR-001 even though Test A alone is not bite-decisive.

ld_panel.py was restored (byte-identical to HEAD) immediately after the
audit; final pytest run confirmed all 11 tests still pass.

## Files Modified

| Path | Change | Lines added |
|------|--------|-------------|
| tests/m3/__init__.py | created (empty) | 0 |
| tests/m3/test_ld_panel_resolver.py | appended 3 tests + `import re` | 139 |

## Commit

- `66d6b8f` test(quick-260501-v9q): add CR-001 regression tests for ld_panel resolver

## Constraints Respected

- Explicit-path staging only (`git add tests/m3/__init__.py tests/m3/test_ld_panel_resolver.py`); no `git add .` / `-A` (GPFS multi-terminal rule).
- No conda activation in commands; used absolute path to smoke_dev Python 3.11.
- Hermetic tests — `tmp_path` + `Path.touch()`; no Hail, AoU, or network calls.
- Existing 8 tests unchanged in behavior or signature.
- `src/python/ld_panel.py` byte-identical to HEAD before commit (audit revert was undone).
- `.planning/STATE.md` and ROADMAP.md NOT modified by executor (orchestrator handles docs commit).

## Self-Check: PASSED

- tests/m3/__init__.py FOUND (0 bytes, mirrors tests/m1/__init__.py).
- tests/m3/test_ld_panel_resolver.py contains 11 `def test_` functions (8 + 3).
- Commit 66d6b8f FOUND in git log.
- pytest run: 11 passed, 0 failed, 0 errors, 0 unexpected warnings.
- Regression-bite proof confirmed (Test B fails under pre-fix simulation).
- ld_panel.py and finemap.smk unchanged on disk.
