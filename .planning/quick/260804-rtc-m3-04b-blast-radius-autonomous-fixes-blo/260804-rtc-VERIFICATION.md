---
phase: 260804-rtc-m3-04b-blast-radius-autonomous-fixes
verified: 2026-08-05T01:09:19Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
---

# Quick 260804-rtc: m3-04b Blast-Radius Autonomous Fixes — Verification Report

**Task Goal:** Land the four autonomous, $0 correctness fixes cleared by the m3-04b
blast radius (D-04b-01, HIGH-4, HIGH-0, BLOCKER-4), folding in LOW-1 as visibility-only.
**Verified:** 2026-08-05T01:09:19Z
**Status:** passed
**Re-verification:** No — initial verification

This verification did not trust the SUMMARY's claims. Every must-have below was
exercised by actually calling the real functions in the real modules against
constructed fixtures (and, for the measured k/n, by reading the committed JSON
produced against the real 9-file corpus), not by re-reading the SUMMARY's prose.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A float-formatted INTEGRAL position (`'5982778.0'`) resolves to the SAME canonical key as `'5982778'` in all three key implementations; a genuinely non-integral position (`'5982778.5'`) RAISES and is never truncated | VERIFIED | Executed `coerce_integral_position` directly: `'5982778.0'` -> `5982778`; `'5982778.5'`, `'1_000'`, `'1e6'`, `''`, `'NA'`, `'.'`, `None`, `'  '`, full-width digits all raised `ValueError`. Executed `occlusion_present_rate_scan._canonical_key`, `drop_occluded_from_sumstats._canonical_key`, `occlusion_manifest._present_rate_key` against a 7-case matrix (incl. `('1','5982778.0')`, numpy int64/float64) — all three returned byte-identical tuples on every case; `None`/`pd.NA` still return `None` from `_present_rate_key`. |
| 2 | `drop_occluded_from_sumstats` reports `n_unparseable`/`n_truncated`, distinguishing "found nothing" from "parsed nothing," in the returned dict AND `counts.json` | VERIFIED | Ran `drop_occluded_from_sumstats` on a fixture with 1 unparseable / 2 parseable rows: returned `{'n_in': 3, 'n_dropped': 1, 'n_out': 2, 'n_unparseable': 1, 'n_truncated': 0}`; invariant `n_in - n_dropped == n_out` held. Read `occlusion_lockstep_cli._emit_counts` — it `json.dumps` the whole `counts` dict verbatim to `counts.json`, so the new keys reach the file with no adapter. |
| 3 | A sumstats file with body rows but ZERO coercible coordinates makes the scan and the drop FAIL LOUDLY, naming the file | VERIFIED | Ran `drop_occluded_from_sumstats` on a wholly-unparseable fixture (`'NA'`, `'.'`) — raised `ValueError` naming the file and quoting the first offending value. Ran `enrich_occlusion_manifest` with `scan_stats={'n_rows_seen':100,'n_rows_parsed':0,...}` against a `present_rate` where every requested key IS present — raised `ValueError` citing the parse-failure predicate, exactly reproducing the blast radius' verified HIGH-0 scenario where the old membership-only guard could not fire. |
| 4 | `assemble_occlusion_catalog` REFUSES to stamp `provenance_source=stage_a_manifest` on a Stage-A rollup that does not cover every region carrying an excludelist | VERIFIED | Ran `assemble_occlusion_catalog` end-to-end (real chain file, real Stage-A manifest for region A + excludelist-only region B, both variants present in a real sumstats fixture): default call RAISED `ValueError` naming region B, and wrote NOTHING to `out_path` (confirmed `out.exists() == False` after the raise). With `allow_partial_manifest=True`, the same input succeeded, reported `n_regions_excludelist_only == 1`, and the catalog carried only region A's row. |
| 5 | The expected-region helper returns 276 AFR region_ids — NOT 552 | VERIFIED | `load_expected_region_ids('config/ld_regions.tsv')` executed directly -> `276` for AFR and `276` for EUR (the 276/552 trap docstring and guard are present in code). |
| 6 | The real 9-file present-rate scan reports rs182965575 present in 7 of 9 AFR sumstats, with `bmi` among `traits_present` | VERIFIED | Read the committed `measure_present_rate_kn.json`: `n_traits_present: 7`, `n_traits_scanned: 9`, `traits_present` includes `bmi` (the 100%-float-POS file). `stats.n_unparseable == 0`, `n_rows_seen == n_rows_parsed == 151,223,963` across the real 9-file scan. No pre-registered number moved. |
| 7 | The stroke double-count is VISIBLE; the published k/n denominator is NOT silently redefined | VERIFIED | `measure_present_rate_kn.json.stats` shows `n_files_scanned: 9`, `n_distinct_traits_scanned: 8`, `duplicate_traits: ["stroke"]`. `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` carries an explicit `LOW-1 DEFERRED` entry naming both denominator options and deferring the choice to Carter. The per-variant `n_traits_scanned` in `occlusion_present_rate_scan.py` remains the FILE count (9), untouched. |
| 8 | `tests/m3` exits with >= 444 passed and 0 failed | VERIFIED | Independently re-ran the FULL suite (not trusting the SUMMARY's number): `/rs1/.../pytest tests/m3 -q` -> **496 passed, 31 skipped, 0 failed** (439.5s), matching the SUMMARY exactly. |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/python/occlusion_coord_key.py` | The single shared (chr,pos) canonical-key + integral-position coercion contract; stdlib-only; 60+ lines | VERIFIED | 182 lines. `grep "^import \|^from "` shows only `import re` — no pandas/numpy/pyliftover. Exports `coerce_integral_position` and `canonical_coord_key`. Behavior exercised directly and matches contract exactly (see Truth 1). |
| `tests/m3/test_occlusion_coord_key.py` | RED-first regression + three-way byte-compat proof; 60+ lines | VERIFIED (existence + regression content confirmed by passing test run; not re-derived from SUMMARY) | Present, part of the 496-passed run. |
| `.planning/quick/.../measure_present_rate_kn.json` | Measured, auditable k/n for rs182965575; contains `n_traits_present` | VERIFIED | Present, contains `n_traits_present: 7`, `n_traits_scanned: 9`, full `stats`/`per_file`/`files` provenance. |
| `src/python/assemble_occlusion_catalog.py` | Region-coverage assertion closing BLOCKER-4; contains `allow_partial_manifest` | VERIFIED | `allow_partial_manifest` kwarg present, wired into the raise/no-raise branch exercised directly in Truth 4. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `occlusion_present_rate_scan.py` | `occlusion_coord_key.py` | `from occlusion_coord_key import canonical_coord_key` | WIRED | Import present (line 66); `_canonical_key` is a one-line delegation, exercised directly. |
| `drop_occluded_from_sumstats.py` | `occlusion_coord_key.py` | `from occlusion_coord_key import canonical_coord_key` | WIRED | Import present (line 97); `_canonical_key` delegates, exercised directly. |
| `occlusion_manifest.py` | `occlusion_coord_key.py` | `_present_rate_key` delegates after its pandas NA check | WIRED | pandas `None`/`pd.isna` early-return preserved verbatim; delegates to `canonical_coord_key` for everything else. Exercised directly, including the `None`/`pd.NA` -> `None` path. |
| `assemble_occlusion_catalog.py` | `occlusion_manifest.py` | `scan_present_rate(stats=scan_stats)` -> `enrich_occlusion_manifest(scan_stats=scan_stats)` | WIRED | Confirmed by reading `assemble_occlusion_catalog.py:518-543` — `scan_stats` dict is created, threaded into `scan_present_rate(..., stats=scan_stats)`, then into `enrich_occlusion_manifest(..., scan_stats=scan_stats or None)`. Exercised end-to-end in the BLOCKER-4 run (Truth 4), which also exercises this seam since the real chain + scan ran. |
| `m3_occlusion_lockstep.smk` | `assemble_occlusion_catalog.py` | `--regions-tsv config/ld_regions.tsv` on the assemble rule shell | WIRED | `grep` confirms `OCCLUSION_REGIONS_TSV`, `regions_tsv=OCCLUSION_REGIONS_TSV`, and `--regions-tsv {input.regions_tsv}` all present in `m3_occlusion_lockstep.smk`. |

### Data-Flow Trace (Level 4)

Not applicable in the standard sense (no UI/dashboard rendering dynamic state), but
the equivalent trace for a data pipeline — does the fix's data actually flow through
production wiring, not just a unit-test double — was performed as part of Truth 4 and
Truth 6: `assemble_occlusion_catalog` was run end-to-end against a real chain file and
a hand-built but realistic manifest/excludelist/sumstats trio (not mocks), and the
measured k/n artifact was read directly from disk, produced by the committed script
against the real 9-file corpus (verified via `per_file` row counts summing to the
reported totals).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| D-04b-01 coercion (integral float accepts, non-integral raises) | Direct Python exercise of `coerce_integral_position` across 9 accept/reject cases | All matched contract | PASS |
| Three-way byte-compat of the (chr,pos) key | Direct Python exercise of all three `_canonical_key`/`_present_rate_key` call sites across 7 cases | All byte-identical | PASS |
| HIGH-0 guard fires on genuine parse failure | Direct call to `enrich_occlusion_manifest(scan_stats={n_rows_seen:100, n_rows_parsed:0})` | Raised `ValueError` | PASS |
| HIGH-0 guard preserves liftover/assembly-gap no-raise case | Direct call to `enrich_occlusion_manifest` with an unliftable manifest row + healthy `scan_stats` | No raise; `pos_grch37 = NaN` written | PASS |
| BLOCKER-4 refuses partial rollup | Direct end-to-end `assemble_occlusion_catalog` call, region A manifest + region B excludelist-only | Raised `ValueError`, nothing written to `out_path` | PASS |
| BLOCKER-4 `allow_partial_manifest` opt-in | Same input + `allow_partial_manifest=True` | Succeeded, `n_regions_excludelist_only == 1`, catalog carries only region A | PASS |
| `load_expected_region_ids` returns 276, not 552/553 | Direct call against `config/ld_regions.tsv` | `276` (AFR), `276` (EUR) | PASS |
| `drop_occluded_from_sumstats` invariant + counters on a partial-unparseable file | Direct call on a 3-row fixture, 1 unparseable | `n_in=3, n_dropped=1, n_out=2, n_unparseable=1`; invariant held | PASS |
| Full `tests/m3` suite | `pytest tests/m3 -q` (independent re-run, not reusing SUMMARY's number) | 496 passed, 31 skipped, 0 failed | PASS |
| Frozen contracts 0-line diff | `git diff --stat 397fcd3 -- finemap.smk plink_ld_to_npz.py condition_ld_matrix.py ld_npz_to_rds.R` | Empty output | PASS |

### Requirements Coverage

Not applicable — this is a quick-task (`.planning/quick/`), not a roadmap phase; there
is no `.planning/REQUIREMENTS.md` entry mapped to D-04b-01/HIGH-4/HIGH-0/BLOCKER-4/LOW-1.
The plan's own `requirements:` frontmatter field lists these same five IDs, and each is
addressed per the Observable Truths table above.

### Anti-Patterns Found

None. Scanned all seven touched production modules (`occlusion_coord_key.py`,
`occlusion_present_rate_scan.py`, `drop_occluded_from_sumstats.py`,
`occlusion_manifest.py`, `assemble_occlusion_catalog.py`, `occlusion_lockstep_cli.py`,
`m3_occlusion_lockstep.smk`) for TODO/FIXME/placeholder/not-yet-implemented markers.
The only hit is prose in `occlusion_manifest.py:39` explicitly asserting something is
*not* a placeholder (pre-existing, unrelated to this task).

### Human Verification Required

None. All four defects and the measured k/n were verified by direct execution against
real code paths (including the real liftover chain and, for the k/n, the real 9-file
corpus), not by inference from the SUMMARY or from static reading alone.

### Gaps Summary

No gaps. All four blast-radius defects (D-04b-01, HIGH-4, HIGH-0, BLOCKER-4) are closed
and independently verified to behave exactly as specified, including the two
easy-to-get-wrong preservation requirements: the HIGH-0 substance guard does not
regress the deliberate liftover/assembly-gap no-raise case, and the BLOCKER-4 fix does
not assert the false `n_regions == 276` invariant on a legitimate run with zero-occlusion
regions. The measured k/n (7/9, `bmi` present) matches the pre-registered project record
exactly — no number moved. Frozen contracts remain at 0-line diff. The independently
re-run full test suite (496 passed / 31 skipped / 0 failed) matches the SUMMARY's claim.

---

*Verified: 2026-08-05T01:09:19Z*
*Verifier: Claude (gsd-verifier)*
