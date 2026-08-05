---
phase: 260804-rtc-m3-04b-blast-radius-autonomous-fixes
plan: 01
subsystem: m3-occlusion-lockstep
tags: [d-04b-01, high-4, high-0, blocker-4, low-1, pre-registration, osf]
requires: [m3-04b]
provides:
  - "occlusion_coord_key: the ONE canonical (chr,pos) key + integral-position coercion"
  - "parse-health counters in counts.json and in the catalog's returned dict"
  - "a total-miss guard that keys on scan SUBSTANCE, not key membership"
  - "a region-coverage assertion closing the partial-rollup provenance spoof"
  - "the measured, auditable k/n for rs182965575 (7 of 9)"
affects: [m3-04c, the-aou-fire, osf.io/az52u]
tech-stack:
  added: []
  patterns:
    - "recurrent bug class -> ONE reusable utility + failing-test-first regression"
    - "explicit re.fullmatch over int()/float()-behind-try for untrusted numeric text"
    - "fail-CLOSED on a total parse failure; fail-OPEN per row but COUNTED"
    - "report coverage gaps, never assert a count that a legitimate run can miss"
key-files:
  created:
    - src/python/occlusion_coord_key.py
    - tests/m3/test_occlusion_coord_key.py
    - .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.py
    - .planning/quick/260804-rtc-m3-04b-blast-radius-autonomous-fixes-blo/measure_present_rate_kn.json
  modified:
    - src/python/occlusion_present_rate_scan.py
    - src/python/drop_occluded_from_sumstats.py
    - src/python/occlusion_manifest.py
    - src/python/assemble_occlusion_catalog.py
    - src/python/occlusion_lockstep_cli.py
    - src/snakemake/rules/m3_occlusion_lockstep.smk
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
decisions:
  - "D-04b-01 closed by extraction, not by three in-place patches: the (chr,pos) key now exists in exactly ONE module and the other three delegate"
  - "An integral float POS coerces; a NON-integral one RAISES and is never truncated — a fabricated coordinate deletes the WRONG variant"
  - "'1e6', '1_000' and full-width digits are REJECTED (explicit re.fullmatch), closing two latent int() quirks and refusing a silent widening"
  - "LOW-1 is REPORTED, not fixed: the pre-registered denominator stays a FILE rate; redefining it is Carter's call and is logged to deferred-items.md"
  - "BLOCKER-4 closed by refusal + an explicit opt-in, NOT by a manifest-union (a union would mix provenance_source and bypass the allow_degraded gate)"
  - "n_regions_missing is REPORTED and never asserted: a zero-occlusion region legitimately writes no manifest, so n_regions == 276 is not a valid invariant"
metrics:
  duration: "~34 min"
  completed: 2026-08-05
  tasks: 3
  commits: 3
  tests_added: 52
---

# Quick 260804-rtc: m3-04b Blast-Radius Autonomous Fixes Summary

Closed the four autonomous `$0` correctness defects the m3-04b blast radius cleared —
a bare `int(pos)` that silently under-drops a whole trait, an audit artifact blind to
its own parse failures, a total-miss guard structurally incapable of firing, and a
PARTIAL Stage-A rollup stamped with complete provenance — and measured the
pre-registered present-rate k/n on the real 9-file AFR corpus: **7 of 9, up from the
6 of 9 the code could produce before the fix.**

## Commits

| Task | Commit | What landed |
|---|---|---|
| T1 | `3bb8783` | `occlusion_coord_key` + three delegating call sites (D-04b-01) |
| T2 | `bf963df` | unparseable/truncated counters (HIGH-4) + a substance guard (HIGH-0) |
| T3 | `fac9a93` | region-coverage assertion (BLOCKER-4), LOW-1 visibility, measured k/n |

## The four defects, and what actually changed

### D-04b-01 — a float-formatted POS silently kept the row

`bmi.AFR.PAGE.2019.GRCh37` writes POS as `'5982778.0'` in **100% of its 17,195,956
rows**. `int(pos)` raised on every one, and both consumers swallowed the raise
fail-open. The `(chr,pos)` key existed in three verbatim copies, so the bug had to be
found and fixed three times.

It now exists in **one** — `src/python/occlusion_coord_key.py`, stdlib-only so
`occlusion_present_rate_scan` keeps its documented "importable without pyliftover"
guarantee — and the three former implementations are one-line delegations. A
parametrized matrix proves all three return byte-identical tuples across `('1','5982778')`,
`(1, 5982778)`, `('chr1', 5982778)`, `('1','5982778.0')`, `('1', 5982778.0)`,
`('1', numpy.int64(...))` and `('X', 100)`, so consolidating the rule did not MOVE the
join.

Coercion is an explicit `re.fullmatch`, deliberately not `int()`/`float()` behind a
`try`: that is what rejects `'1_000'` (which `int()` reads as 1000), full-width digits,
and scientific notation — the latter occurs zero times in the corpus, so accepting it
would have been a silent widening. **A non-integral position raises; it is never
truncated.** The join is drop-only, so a truncated coordinate deletes the wrong
variant's row from real data, which is strictly worse than failing.

Contig normalization is byte-identical to before. `.isdigit()` was deliberately **not**
tightened, and LOW-5 (chrX `'X'` vs `23`) is documented in-code as explicitly out of
scope so a future reader does not "fix" it here by accident.

### HIGH-4 — nothing separated "found nothing" from "parsed nothing"

`drop_occluded_from_sumstats` now returns `n_unparseable` and `n_truncated` on **every**
return path (including the empty-header early return, so the dict shape is uniform),
emits one loud STDERR summary naming the file, the counts and the first offending raw
value, and **raises** when `n_in > 0 and n_unparseable == n_in`. The module docstring now
states plainly that `n_in - n_dropped == n_out` holding is *not* evidence the file
parsed — it is arithmetic over rows read and rows written, and it holds perfectly over a
file in which no coordinate was ever decoded.

`scan_present_rate` gained a kwarg-only `stats` out-param carrying `n_files_scanned`,
`n_distinct_traits_scanned`, `duplicate_traits`, `n_rows_seen`, `n_rows_parsed`,
`n_unparseable`, `n_truncated`, `n_files_empty` and `per_file`. **The per-variant record
is untouched at exactly four keys** — that is the no-adapter contract with
`enrich_occlusion_manifest(present_rate=...)`, which is why the health numbers ride out
separately. All of it accumulates inside the existing single pass.

`counts.json` carries the new fields for free through `_emit_counts`; the test asserts
the **file's** content, not the function's return, because the file is what an auditor
reads later. `assemble_occlusion_catalog` surfaces the scan health as `n_scan_rows_seen`
/ `n_scan_rows_parsed` / `n_scan_unparseable` — `n_scan_*` deliberately, because
`n_unparseable` already means "excludelist LINES that did not parse" and conflating the
two would make the catalog's own audit numbers ambiguous.

### HIGH-0 — the guard could not fire

`enrich_occlusion_manifest`'s total-miss guard tested `any(k in present_rate for k in
keys_present)`. But the scan keys are built from the manifest's own lifted rows and the
scan returns a record for **every** requested key, so that test is always True; it could
detect key-*shape* drift and nothing else.

The RED demonstrates this directly: part (a) shows the shipped call writing
`n_traits_present = 0` on every row without raising, over a `present_rate` in which every
requested key is present. Part (b) requires the same call, told the scan parsed nothing,
to refuse.

A substance guard now sits immediately before the membership guard and raises when
`scan_stats["n_rows_seen"] > 0 and scan_stats["n_rows_parsed"] == 0`. **The
liftable-scoping comment at `occlusion_manifest.py:375-383` survives verbatim** and the
assembly-gap no-raise case (zero liftable rows, healthy scan) is pinned by its own test —
that decision is correct, and a guard that false-aborts on it would get ripped out by a
future maintainer, silently restoring the original defect.

### BLOCKER-4 — a PARTIAL rollup wore a complete provenance stamp

The override fired when the rollup was merely non-empty, not when it was complete. The
shipped note — *"the manifests carry strictly more provenance"* — is true **per region**
and false **as a set claim** the moment the manifest set is a subset of the regions with
excludelists. Those regions' occluded variants would then never be dropped from the
sumstats: orphaned variants, wearing a `stage_a_manifest` stamp saying everything is fine.
The triggering state is already coded (`run_native_ld_panel.py:821-831` continues on a
failed manifest append while still writing the excludelist).

`assemble_occlusion_catalog` now refuses, naming the orphaned regions, the consequence
and both remedies; `--allow-partial-manifest` accepts it explicitly and reports
`n_regions_excludelist_only`, so the incompleteness lands *in* the provenance rather than
being inferred from an absence. The STDERR note was rewritten to claim only coverage,
which is what actually justifies ignoring the excludelists.

**Not a union**, and the reasoning is recorded in code: a manifest∪excludelist merge would
produce a MIXED `provenance_source` (a property §1 of the blast radius verified as
currently invariant) and would let degraded rows — which permanently lack the ref-span and
occluding-deletion attribution — ride out without the `allow_degraded` gate the
pre-registration depends on.

`load_expected_region_ids` derives the expected set as `nunique(region_id)` filtered to
ancestry = **276**, and the 276/552 trap is in its docstring and pinned by a test asserting
`== 276` **and** `!= 552` **and** `!= 553`. An observed region outside the expected set
raises (naming drift); a strict subset is **reported** via `n_regions_expected` /
`n_regions_missing` and never asserted — a region with zero occluded variants legitimately
writes no manifest, so `n_regions == 276` is not a valid invariant.

`--regions-tsv` is wired into `rule m3_assemble_occlusion_catalog`, so the check is LIVE in
production rather than merely available. Verified end-to-end on today's tree:

```
n_regions_expected: 276    n_regions_missing: 276    n_regions_excludelist_only: 0
```

## The measured k/n — before and after

Run detached over the real 9 GRCh37 AFR harmonized sumstats (excluding
`asthma.AFR.grch38_backup`, which is build 38), streamed, read-only, `$0`:

| | value |
|---|---|
| **rs182965575 (GRCh37 1:5982778)** | **present in 7 of 9 AFR sumstats** |
| before D-04b-01 was closed | 6 of 9 (the blast radius' measured value) |
| `traits_present` | `asthma`, **`bmi`**, `hdl`, `ldl`, `t2d`, `tc`, `tg` |
| rows seen / parsed | 151,223,963 / 151,223,963 |
| unparseable / truncated / empty files | 0 / 0 / 0 |
| distinct traits | 8 over 9 files (`stroke` duplicated) |
| wall time | 5.0 min (the plan budgeted 1–4 h) |

`bmi` appearing in `traits_present` **is** the D-04b-01 proof: that is the 100%-float-POS
file, which scored absent before this plan. The measured value matches the project record
and the pre-registration exactly, so **no pre-registered number moved**. Artifact:
`measure_present_rate_kn.json`, produced by the committed script against the final tree.

## LOW-1 — reported, deliberately not fixed

The scan resolves **9 files but 8 distinct traits** (`stroke.AFR` and
`stroke.AFR.GIGASTROKE.2022.GRCh37` both report `stroke`), confirmed on real data. A loud
STDERR note now fires and `duplicate_traits` is recorded, but **the denominator is
unchanged**: the pre-registration publishes "present in 7 of 9 AFR *sumstats*" — a FILE
rate. Redefining it to distinct traits (which would make it 7 of 8) moves a pre-registered
number and requires an OSF amendment, so it is logged to
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` as
**`LOW-1 DEFERRED — denominator redefinition (files vs distinct traits) needs Carter`**,
with both options stated neutrally.

## Deviations from Plan

**1. [Additive] Extra cases in the three-way byte-compat matrix.** The plan's matrix
(`('1','5982778')`, `(1,5982778)`, `('chr1',5982778)`, `('1', numpy.int64(...))`,
`('1', 5982778.0)`, `('X',100)`) would have passed on the pre-fix tree — it is a compat
pin, not a RED. Added `('1','5982778.0')` so the matrix is a genuine failing-test-first
regression across all three implementations, and split the numpy case into its own test
(parametrize IDs cannot carry a numpy scalar cleanly). Also added `'1E6'`, `'1.5e6'`,
`'chr1'`, `'-'` and a full-width-digit case to the rejection set, all named in the plan's
prose as things that must not be accepted.

**2. [Additive] `regions_excludelist_only` in the returned dict.** The plan requires
`n_regions_excludelist_only`; the region *ids* are also returned so an operator can act on
the report without re-deriving it. Purely additive.

**3. [Scope] The measurement log is not committed** — `*.log` is gitignored. The script
and the JSON (which carries the full `stats`, the file list and the elapsed time) are
committed as specified; the log was left as untracked runtime output rather than
force-added against the repo's own convention.

**4. [Timing] The measurement ran twice.** The first run (5 min, not the budgeted 1–4 h)
predated the LOW-1 STDERR note, so it was re-run against the final tree to keep the
artifact's provenance identical to the shipped code. Both runs returned 7 of 9.

No auto-fix rules fired: no bugs, missing critical functionality or blockers were
encountered outside the four the plan targets.

## STOP-and-surface decisions raised

**None.** No existing test contradicted a required change and no test was edited to force
green. Every pre-existing assertion in the five touched suites passes unmodified,
including the three pinned raise-boundary tests in `test_occlusion_manifest.py` and the
`params.region_id` / `REGION_SAFE_TO_ID` pins in `test_occlusion_lockstep_wiring.py`.

## Verification

| Check | Result |
|---|---|
| Full `tests/m3` | **496 passed, 31 skipped, 0 failed** (baseline 444/31/0; +52 tests) |
| Frozen contracts (`finemap.smk`, `plink_ld_to_npz.py`, `condition_ld_matrix.py`, `ld_npz_to_rds.R`) | `git diff --stat` **EMPTY** |
| `load_expected_region_ids('config/ld_regions.tsv')` | **276** (not 552/553) |
| `measure_present_rate_kn.json` | **7 / 9** |
| `NaN->0` revived / `condition_ld_matrix` imported | **No** — the only hits are pre-existing docstring prose describing the *retired* approach; m3-06 stays HELD |
| `int(pos)` / `int(pos_grch37)` call sites in the three modules | **0** (remaining grep hits are docstring prose naming the closed defect) |
| `m3_occlusion_lockstep.smk` parses | `snakemake --list` OK |
| Assembler CLI with `--regions-tsv`, live | OK — `n_regions_expected: 276` |
| Staging | explicit paths only; `sparse_parent_benchmark.tsv` benchmark churn deliberately not staged |

## Self-Check: PASSED

All four declared artifacts exist on disk; all three commit hashes resolve; every
declared key-link grep is non-zero; `occlusion_coord_key.py` (181 lines) and
`test_occlusion_coord_key.py` (275 lines) both exceed their 60-line minimums.

## What this unblocks, and what it does not

**Unblocked (per the blast radius' gate table):**
- *Trusting the post-fire catalog as a drop key* — BLOCKER-4 closed.
- *Publishing the pre-registered k/n* — HIGH-0, HIGH-4 and D-04b-01 closed; LOW-1 is
  visible and deferred with the number itself untouched.

**Still blocked, untouched by this plan:**
- **BLOCKER-1** — `{input.ld_matrix}` is a DAG declaration only; `run_susie_rss.R`
  rebuilds its own path and never sees `AFR_aou/`. The ~11-day, ~$385–1,084 fire stays
  HALTED pending Carter's LD read-path decision.
- BLOCKER-2 / BLOCKER-3 (the m3-04c merge), HIGH-1, HIGH-2, HIGH-3, MEDIUM-8/9/10.
