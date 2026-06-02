---
phase: 260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir
reviewed: 2026-06-01T00:00:00Z
depth: deep
files_reviewed: 2
files_reviewed_list:
  - src/python/aou_ld_panel.py
  - tests/m3/test_aou_ld_panel_local.py
findings:
  critical: 0
  warning: 0
  info: 3
  total: 3
status: issues_found
---

# Quick 260601-u1b: Code Review Report

**Reviewed:** 2026-06-01
**Depth:** deep (thorough on the two new helpers, per task scope)
**Files Reviewed:** 2 (`src/python/aou_ld_panel.py`, `tests/m3/test_aou_ld_panel_local.py`)
**Status:** issues_found (3 INFO/low only — no blocker/high/medium)

## Summary

The diff (`344040e`, the only source-touching commit in `c89008c..HEAD`) is a
single **purely additive** hunk in `aou_ld_panel.py` (lines 753–1061) plus four
new tests. I verified there are **zero deletions** to existing code — the
`_assert_checkpoint_nonempty` hard gate (count_rows>0 / count_cols>0 →
RuntimeError) is byte-for-byte unchanged, and no existing guard was weakened
(focus area 3 confirmed clean).

I ran the 8 new tests (all PASS under Python 3.11 / pytest 9.0.3) and then
hammered both helpers with adversarial inputs the tests don't cover
(now()-raises, bucket=None + unset env, non-dict listings, missing _SUCCESS,
string/mixed-type mtimes, malformed intervals, writer-raises, every-collaborator-
raises). **The load-bearing never-raise guarantee holds on every path I could
construct, and the partial-JSON best-effort emission works** (collaborators all
raising still produces a parseable `_capture.json` carrying phase + uri + the
three recorded sub-step errors).

**The mtime distinguisher logic is CORRECT and NOT inverted.** I cross-checked
against `feedback_w1_catastrophe_hypothesis_distinguisher`:
- `_SUCCESS` mtime at/after ALL part mtimes → `hail_finalize_on_empty` (marker
  sealed by driver task-accounting without/after real entries write). Correct.
- at least one part mtime AFTER `_SUCCESS` → `kill_interrupted_write` (writes
  continued past the marker). Correct.
- Equal mtimes resolve to `hail_finalize_on_empty` (the "at/after" boundary),
  which is the right default — a tie is the finalize signature, not the kill one.

The du-floor helper correctly returns the **full base** for `None`, bare
`"chr22"`, malformed spans, zero/negative spans, and single-position intervals,
and only scales DOWN for genuine span-bounded sub-chromosomal intervals — so the
Tier-2 chr22 / full-genome check is never weakened (focus areas 1 + 2 confirmed).

No blocker, high, or medium issues. Three low/INFO observations follow; none
compromise the catastrophe-defense contract, but IN-01 is worth a one-line
hardening given how load-bearing the distinguisher is.

## Info

### IN-01: Distinguisher silently degrades to `indeterminate` if Hail returns `modification_time` as a string (or mixed types)

**File:** `src/python/aou_ld_panel.py:1009` (comparison `m > success_mtime`)

**Issue:** The distinguisher does a numeric-style comparison
`any(m > success_mtime for m in usable)`. The tests only ever feed **integer
epochs** (`_mk_listing` uses `2000`, `1500`, etc.), so the comparison path is
exercised only for the homogeneous-int case. But `hl.hadoop_ls` stat dicts do
**not** guarantee an integer epoch for `modification_time` across Hail versions —
historically it has been emitted as a formatted datetime **string**
(`'2026-05-21 14:03:22'`), and the production lister `_hail_hadoop_lister_stat`
passes whatever Hail returns straight through untouched.

I verified the consequences empirically:
- All-string mtimes (same format/length) → comparison works *lexicographically*
  and happens to produce the right flag for same-day timestamps, but this is
  accidental, not designed, and breaks across date/format boundaries.
- **Mixed** types (e.g. `_SUCCESS` string, parts int — or vice versa) →
  `TypeError("'>' not supported between instances of 'int' and 'str'")`. This is
  **caught** by the outer `try/except` at line 1015, so the never-raise contract
  is NOT violated — but the flag silently falls back to `indeterminate` and the
  whole forensic point (which hypothesis fired) is lost at the exact moment it
  matters most.

This is the single mechanism the entire `$2,140`-class re-fire decision hinges
on, so a silent `indeterminate` here is a real (if low-probability) loss of the
artifact's value. It is INFO/low rather than higher only because (a) the
never-raise contract is intact, (b) the raw `success_mtime` + `entries_part_mtimes`
are still recorded verbatim in the JSON so a human can resolve it manually, and
(c) the same physical AoU run already resolved this hypothesis via direct
`gsutil ls -l` (memory note RESOLVED 2026-05-28).

**Fix:** Normalize mtimes to a common comparable type before comparing. Coerce
to float epoch where possible, falling back to string only if all values are
strings:

```python
def _coerce_mtime(v):
    # Hail hadoop_ls modification_time may be int/float epoch (ms or s) or a
    # formatted datetime string depending on version/backend. Coerce to a
    # comparable float; return None if uncoercible so it is dropped from `usable`.
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        try:
            return float(s)                      # numeric-as-string
        except ValueError:
            from datetime import datetime
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    return datetime.strptime(s, fmt).timestamp()
                except ValueError:
                    continue
    return None

# then:
success_cmp = _coerce_mtime(success_mtime)
usable = [c for c in (_coerce_mtime(m) for m in part_mtimes) if c is not None]
if success_cmp is not None and usable:
    if any(c > success_cmp for c in usable):
        capture["hypothesis_flag"] = "kill_interrupted_write"
    else:
        capture["hypothesis_flag"] = "hail_finalize_on_empty"
else:
    capture["hypothesis_flag"] = "indeterminate"
```

Keep storing the **raw** `success_mtime` / `entries_part_mtimes` in the JSON
(as it does now) so the coercion is only for the flag decision. Add one test
that feeds string-format mtimes (and one mixed-type case) and asserts the flag
is still resolved, not `indeterminate`.

### IN-02: Tests do not pin the never-raise contract for the production `WORKSPACE_BUCKET`/no-bucket path, nor assert that partial JSON is still emitted when collaborators raise

**File:** `tests/m3/test_aou_ld_panel_local.py:1325`
(`test_capture_forensics_never_raises_when_collaborators_raise`)

**Issue:** The never-raise test is good as far as it goes — it confirms a dict is
returned and `phase` is recorded when every collaborator raises. But it always
passes an explicit `bucket=`, so two real-world branches stay untested:
1. `bucket=None` with `WORKSPACE_BUCKET` unset → `forensics_dir is None` → the
   `(c)` hail.log-copy and `(e)` json-write blocks are skipped entirely. I
   verified manually this does not raise, but there is no regression pin on it,
   and that is the literal production default-arg path (notebook calls
   `_capture_catastrophe_forensics(uri, phase='afr')` with no bucket).
2. The test asserts a dict comes back but does **not** assert that the
   best-effort *partial JSON* is still written when the non-writer collaborators
   raise. The docstring's load-bearing promise is "still writes whatever partial
   json it could" — that behavior is real (I verified: 3 errors recorded, JSON
   present) but unpinned, so a future refactor could silently drop it.

**Fix:** Extend the existing test (or add a sibling) to (a) call once with
`bucket=None` and `WORKSPACE_BUCKET` removed from `os.environ`
(`monkeypatch.delenv("WORKSPACE_BUCKET", raising=False)`) and assert it returns a
dict without raising; and (b) in the all-collaborators-raise-but-bucket-given
case, assert `<bucket>/ld/_forensics/<phase>_capture.json` exists, round-trips
through `json.loads`, and its `errors` list is non-empty (proving partial
emission).

### IN-03: Dead local variable `success_uri`

**File:** `src/python/aou_ld_panel.py:980`

**Issue:** `success_uri = f"{uri.rstrip('/')}/_SUCCESS"` is assigned but never
read — the `_SUCCESS` mtime is instead found by scanning the `listing` for a
path ending in `_SUCCESS` (lines 986–989). Harmless (no behavioral effect), but
it is dead code in a file that is otherwise meticulous, and it hints the original
intent may have been to stat `_SUCCESS` directly. Either remove it, or — if a
direct stat is actually wanted as a fallback when the top-level `listing` does
not surface `_SUCCESS` — wire it in. (Note: for a real Hail MT dir,
`lister(uri)` does list the top-level `_SUCCESS`, so the scan is sufficient and
the variable is genuinely redundant.)

**Fix:** Delete line 980.

---

## Notes on items explicitly checked and found CLEAN (no finding)

- **Never-raise contract:** every sub-step (`now()`, bucket-resolve,
  listing/distinguisher, hail.log-copy, spark-rest, json-write) is individually
  wrapped; the only unguarded statements are the unconditional `capture` dict
  literal, the default-arg assignments (which reference module-level functions
  that are guaranteed to exist), pure f-strings over already-bound locals, and
  the final `return capture`. None of these can raise. The `except` blocks
  themselves only do `capture["errors"].append(...)` on a key that is
  pre-seeded as a list in the literal — no risk of the except handler raising.
  Verified empirically with every collaborator raising, `now()` raising, and
  `writer` raising.
- **du-floor edge cases:** `None`, `""`, bare `"chr22"` → full base (correct, no
  down-scale). Malformed (`"chr22:abc-def"`), reversed
  (`"chr22:18000000-16000000"` → `span_bp` clamped to 0 → full base),
  single-position (`"chr22:16000000"` → `int("")` raises ValueError → full base),
  zero-span (`"chr22:16000000-16000000"` → full base), extra-colon
  (`"...:extra"` → ValueError → full base) all fall back conservatively to the
  full base. Unknown contig (`"chrZZ:..."`) uses the chr1 default length
  (largest → most conservative under-scaling) and a real nano span clamps up to
  `MIN_DU_FLOOR_BYTES` (2 MB), comfortably above the ~71 KiB footer-stub
  signature. No div-by-zero (`chrom_len > 0` guard + dict values all positive).
  Span scales monotonically and is capped at base. All correct.
- **mtime distinguisher direction:** verified against
  `feedback_w1_catastrophe_hypothesis_distinguisher` — NOT inverted (see Summary).
- **Additive-only:** confirmed via `git diff` hunk header + zero `-` lines of
  real code; `_assert_checkpoint_nonempty` unchanged.
- **No security issues:** the `urllib.request.urlopen` Spark-REST getter targets
  a hardcoded localhost:4040 default and carries a `# nosec B310` justification;
  no injection surface (no shell, no eval, no user-controlled URL in the default
  path). `json.dumps(..., default=str)` cannot raise on un-serializable Hail
  objects. No hardcoded secrets.
- **Test quality (forensics):** the never-raise + both-signature tests use
  real injected collaborators (raising lambdas / mtime-bearing stat dicts), not
  mocks-of-the-function-under-test, and the JSON test reads the actual written
  file back through `json.loads`. They exercise behavior, not tautologies.
- **Test quality (du-floor):** pins both the None / whole-chromosome full-base
  case (`test_..._none_keeps_base`, `test_..._whole_chromosome_keeps_base`) AND
  the nano down-scaled case (`test_..._nano_interval_no_false_positive`,
  asserting `< base` and `>= 1 MB`), plus monotonicity. Good coverage.

---

_Reviewed: 2026-06-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
