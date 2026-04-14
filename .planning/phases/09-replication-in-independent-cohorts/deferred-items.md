# Phase 9 Deferred Items

## Discovered during Plan 09-02 execution (2026-04-14)

### DEF-09-02-01: Pre-existing Phase 2 test collection failures

- **Where:** `tests/phase2/test_negative_controls.py`, `tests/phase2/test_pph4_sweep.py`, `tests/phase2/test_tier_assignment.py`
- **Error:** `ModuleNotFoundError: No module named 'tests'` — these files do `from tests.phase2.conftest import ...` but the `tests/` directory has no `__init__.py`, so the package path doesn't resolve under pytest.
- **Confirmed pre-existing:** Reproduced after `git stash` of all Plan 09-02 changes — the failure existed before Wave 2 started.
- **Scope:** Out of scope for Plan 09-02 per the Scope Boundary rule. Phase 2 test regressions are not caused by Wave-2 replication harmonizers.
- **Remediation options:**
  1. Add `tests/__init__.py` + `tests/phase2/__init__.py` (lightweight fix).
  2. Refactor the 3 test files to use `sys.path.insert` + `from conftest import ...` (matches the phase9 + most phase5 pattern).
- **Blocking who:** Nobody currently — Phase 2 plans are already complete and marked SUMMARY. Only affects running the phase2 test suite in isolation.
