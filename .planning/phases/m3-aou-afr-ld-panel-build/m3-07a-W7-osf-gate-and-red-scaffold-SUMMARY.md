---
phase: m3-aou-afr-ld-panel-build
plan: 07a
subsystem: aou-afr-ld-panel
tags: [ld, occlusion, osf-prereg, red-first, tdd, aou, afr, wave0]
requires:
  - OSF amendment-update POSTED to osf.io/az52u (2026-07-10T13:32:22Z, ac4c990) — PRE-CLOSED gate
  - m3_region1_nan_geometry_verdict.md (4543dcf4…) — the settled mechanism
  - m3_panel_occlusion_policy_decision.md (42d70167…) — the settled policy
provides:
  - RED-first executable spec for the occlusion span-filter (07b) + manifest/scan/lockstep (07c)
  - _REGION1_BIM_ROWS synthetic fixture — the single source of truth for the region-1 topology
  - _MockPlink --exclude + nan_snps seam (models occluded-variant NaN LD)
affects:
  - tests/m3/test_run_native_ld_panel.py (additive only; 45 pre-existing tests stay GREEN)
tech-stack:
  added: []
  patterns:
    - "function-local impl imports keep RED collect-clean (ModuleNotFoundError at call-time)"
    - "cross-test fixture sourcing via importlib file-path load (no coordinate-table duplication)"
key-files:
  created:
    - tests/m3/test_occlusion_span_filter.py
    - tests/m3/test_occlusion_manifest.py
    - tests/m3/test_occlusion_present_rate_scan.py
    - tests/m3/test_occlusion_lockstep_drop.py
  modified:
    - tests/m3/test_run_native_ld_panel.py
decisions:
  - "reason pinned via the module constant REASON_REFERENCE_OCCLUSION, not a literal (source docs disagree on arrow spacing)"
  - "_MockPlink gained nan_snps — without it the 'npz has no NaN' test would pass GREEN for the wrong reason"
  - "region-1 fixture sourced by importlib file-path load, not duplicated (T-m3-07a-02 drift mitigation)"
metrics:
  duration: ~45 min
  completed: 2026-07-15
  tasks: 2 (Task 1 PRE-CLOSED / confirm-only; Task 2 executed)
  commits: 1 (296157a) + tag m3-07a-W7-T-WAVE0
---

# Phase m3 Plan 07a: OSF Gate + Wave 0 RED Scaffold Summary

Wave 0 of the m3-07 occlusion split: the OSF hard gate re-confirmed read-only, and the
complete RED-first executable spec (4 new suites + an extended driver suite, 41 + 52
tests collected, ZERO collection errors) that defines the exclude-in-lockstep behavior
07b/07c must deliver. No implementation module was written — the RED stays RED.

## Task 1 — OSF pre-registration HARD GATE: CONFIRMED (PRE-CLOSED, no action taken)

Task 1 was **PRE-CLOSED and reconciled to reality on 2026-07-15** before execution. Its
`<verify>` block was run as a **read-only confirmation** and returned `GATE_CONFIRMED_OK`
on an unmodified tree. Nothing was drafted, posted, created, or edited.

| Item | Value |
|------|-------|
| Amendment (REAL filename) | `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` |
| Author | Carter (Carter-authored, not Claude-drafted) |
| POSTED to | `osf.io/az52u` at **2026-07-10T13:32:22Z** |
| Recorded in-repo | commit **`ac4c990`** |
| Git tag | `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10` |
| Body anchor 1 (re-verified byte-exact) | `tail -c 5012 m3_region1_nan_geometry_verdict.md` = `4543dcf4a61c3cf79061c8c55b71b316c38c4a938541cf0040c94212c8cdc06a` |
| Body anchor 2 (re-verified byte-exact) | `tail -c 5247 m3_panel_occlusion_policy_decision.md` = `42d701677ac8bc85d3b03f390413c4406ba65f3b11ab085350e560738ab209ef` |
| Verdict | `GATE_CONFIRMED_OK` |

The placeholder filename `osf-amendment-panel-occlusion-exclusion-2026-07-10.md` and
placeholder tag `PANEL-OCCLUSION-OSF-AMENDMENT-POSTED-2026-07-10` named in the
pre-reconciliation plan **never existed** and were correctly NOT created. The posted
amendment doc was treated as **READ-ONLY** (threat T-m3-07a-03): the in-repo copy is
byte-identical to what Carter uploaded to OSF, so editing it would silently diverge the
repo from the posted artifact — exactly the provenance failure the gate exists to prevent.

The anchors are verified against their **source docs** (where they hold byte-exactly), not
grepped out of the amendment, which names its supporting docs by filename rather than by
body-SHA. As-posted, the doc does not contain the literal phrase "never zeroing"; it frames
the policy as withdrawing the `tcujq` NaN→0 conditioning. That is the posted reality and
was not "corrected".

**✅ FOLLOW-UP CLOSED 2026-07-15** (was: the OSF direct file GUID/URL had never been
captured, only the activity timestamp). The GUID is **`trsx5`** —
https://osf.io/az52u/files/trsx5 — captured from the OSF file page and filled into the
amendment doc header + `.planning/osf_deviations.md`. **No open items remain on this gate.**

Capture also **verified the append-only commitment**: the update is a SEPARATE NEW FILE,
not a re-version of the amendment it withdraws (`trsx5` = 1 revision, 2026-07-10 13:32;
`tcujq` = still 1 revision, 2026-07-04 04:14, unmodified). The pre-registered "post as a
NEW supplementary file (append-only)" was honored exactly → **no posting deviation to
disclose**.

⚠ `trsx5` (this update) ≠ `tcujq` (`Prereg_Phase1_amendment3.md`, the 2026-07-04 NaN→0
amendment this file WITHDRAWS). `tcujq` was offered for this slot on 2026-07-15 and
refused — writing it would have pointed the withdrawing document at the document it
withdraws. Filling the header GUID does NOT break byte-parity: only the project-side
prepended header changed; the posted body is unchanged (`content-after-header` sha256
`c80d4d26…` identical before/after), mirroring the `tcujq` precedent whose own header
carries a GUID that OSF only assigns at upload.

## Task 2 — Wave 0 RED-first scaffolds: COMPLETE

### Files

| File | Status | Content |
|------|--------|---------|
| `tests/m3/test_occlusion_span_filter.py` | NEW | `_REGION1_BIM_ROWS` fixture + the occlusion rule, pair-4 attribution, boundary/SNV/insertion/chain cases, gated real-window oracle stub |
| `tests/m3/test_occlusion_manifest.py` | NEW | Stage-A schema + ref_span + reason + resume-safe dedup + rollup + Stage-B liftover |
| `tests/m3/test_occlusion_present_rate_scan.py` | NEW | present-rate k/n, absent→0, traits_present, CHR/POS auto-detect |
| `tests/m3/test_occlusion_lockstep_drop.py` | NEW | drop == manifest GRCh37 (CHR,POS); chr-aware; byte-identical survivors; no re-key; idempotent; logged |
| `tests/m3/test_run_native_ld_panel.py` | EXTENDED | `_MockPlink` honors `--exclude` + `nan_snps`; 6 RED occlusion-integration tests + 1 passing boundary guard |

### RED-collection-clean confirmation — ACTUAL pytest output

Plan Task 2 `<automated>` verify block:

```
=========== 4 NEW SUITES (plan Task 2 <automated>) ===========
FAILED tests/m3/test_occlusion_lockstep_drop.py::test_logs_each_drop - Module...
FAILED tests/m3/test_occlusion_lockstep_drop.py::test_result_reports_counts
38 failed, 2 passed, 1 skipped in 1.04s

=========== GATE VERDICT ===========
RED_AS_EXPECTED

=========== DRIVER SUITE ===========
=========================== short test summary info ============================
FAILED tests/m3/test_run_native_ld_panel.py::test_driver_writes_occluded_excludelist_with_exactly_the_occluded_ids
FAILED tests/m3/test_run_native_ld_panel.py::test_exclude_reaches_the_plink_argv
FAILED tests/m3/test_run_native_ld_panel.py::test_keep_allele_order_still_present_alongside_exclude
FAILED tests/m3/test_run_native_ld_panel.py::test_occlusion_filtered_npz_has_no_nan_and_verifies
FAILED tests/m3/test_run_native_ld_panel.py::test_n_dropped_occluded_is_separated_from_n_dropped_monomorphic
FAILED tests/m3/test_run_native_ld_panel.py::test_panel_columns_include_n_dropped_occluded
6 failed, 46 passed in 1.20s
```

Collection is clean — **41 tests collected in 0.06s**, zero errors:

```
$ pytest <4 new suites> --collect-only -q
41 tests collected in 0.06s
```

RED is for the RIGHT reason — a call-time `ModuleNotFoundError`, never a collection error:

```
E       ModuleNotFoundError: No module named 'occlusion_span_filter'
tests/m3/test_occlusion_span_filter.py:210: ModuleNotFoundError
```

The 2 passed = the fixture self-checks (they need no impl and guard the fixture geometry
against drift). The 1 skipped = the gated real-`.bim` oracle stub (no perimeter access).

**Full `tests/m3` suite:** `44 failed, 363 passed, 31 skipped in 486.73s`. The 44 failures
are **exactly** 38 (new suites) + 6 (driver) — i.e. every failure is a new RED test and
**zero pre-existing tests regressed**. The `_MockPlink` extension is behavior-preserving:
all 45 pre-existing driver tests still pass (46 passed = 45 pre-existing + 1 new guard).
The diff is additive only (42 → 49 `def test_`; no existing test modified or removed).

### The region-1 `.bim` fixture coordinates

chr1; deletions carry a multi-char A2/REF of the exact span length; ids = `f"1:{bp}:{A2}:{A1}"`
(= chr:pos:REF:ALT). A1=ALT / A2=REF per the frozen `load_bim` convention.

| bp | role | A1 (ALT) | len(A2/REF) | footprint | outcome |
|----|------|----------|-------------|-----------|---------|
| 1980423 | del1 | G | 60 | [1980423, 1980482] | occluder |
| 1980475 | snpA | A | 1 | — | **OCCLUDED** (by del1) |
| 5733474 | del2 | G | 29 | [5733474, 5733502] | occluder |
| 5733487 | snpB | A | 1 | — | **OCCLUDED** (by del2) |
| 5922716 | del3 | G | 7 | [5922716, 5922722] | occluder — pair-4 |
| 5922718 | snpC | A | 1 | — | **OCCLUDED** by the **UPSTREAM** del3 |
| 5922724 | del4 | G | 31 | [5922724, 5922754] | disjoint; occludes nothing |
| 7492679 | del5 | G | 31 | [7492679, 7492709] | occluder |
| 7492693 | del6 | G | 17 | — | **OCCLUDED** (by del5) — a deletion |
| 8375794 | del7 | G | 29 | [8375794, 8375822] | occluder |
| 8375822 | snpD | A | 1 | — | **OCCLUDED** — boundary (== last covered base) |

**Expected occluded set = `{1980475, 5733487, 5922718, 7492693, 8375822}` (5).**
REF-span inventory = **60/29/7/31/31/17/29 bp** (7 deletions).

**Pair-4 second-order (SETTLED, pinned):** SNP 5922718 is attributed to the **UPSTREAM**
DEL 5922716 (7 bp span → footprint ends 5922722, covering 5922718), **NOT** the downstream
DEL 5922724 (which starts past the SNP, so `POS_D < POS_V` fails). The single 5922718 drop
collapses the 3-record 5922716/5922718/5922724 tangle; neither deletion is excluded.
`edges` must contain `(del3, snpC)` and must **not** contain `(del4, snpC)`.

**Liftover anchors — independently re-verified against the real chain** (`pyliftover`,
`data/external/liftover/hg38ToHg19.over.chain.gz`, `convert_coordinate("chr1", pos−1)`, `+1` out):
`5922716 → 5982776`, `5922718 → 5982778`, `5922724 → 5982784`. Reproduced byte-exact.

**Gated real-window oracle (documented, out of scope for the synthetic unit):** occluded set
`{10328, 44784, 46714, 59097, 66730}`; 7-deletion inventory `60/29/7/31/31/17/29 bp`;
0 same-position. Pinned as module constants + a skip-gated stub — the concrete expected
answer for the gated 276-region real-`.bim` check. Seth's full detector prototype is noted
in the module docstring as a **READ-ONLY reference, NOT committed**.

## Deviations from Plan

### Auto-fixed / design resolutions

**1. [Rule 2 — missing critical functionality] `_MockPlink` gained `nan_snps`**
- **Found during:** Task 2, authoring driver test (d)
- **Issue:** The plan specifies extending `_MockPlink` only for `--exclude`. But test (d)
  ("the resulting `.npz` has NO NaN and passes `content_verify_npz`") would then pass
  **GREEN today, with no implementation** — the mock never emits NaN, so the assertion
  would be vacuous. That directly violates the plan's own controlling constraint
  (RED-for-the-right-reason) and would ship a test that can never fail.
- **Fix:** `_MockPlink` now models the mechanism the phase exists for — an occluded variant
  surviving into the LD step makes plink `--r` emit a NaN row/col with the diagonal still
  1.0 (the real m3-02e-T4 fire-#3 fingerprint documented in `test_nan_guard.py`). Defaults
  to empty → all pre-existing tests unaffected.
- **Evidence it works:** the driver now errors with the real NaN guard's message, naming
  NaN rows `[1, 3, 5, 8, 10]` — **exactly** the 5 occluded fixture rows (and `[1,3,5,7,9]`
  once the monomorphic del4 is dropped). The fixture geometry is validated end-to-end.
- **Files:** `tests/m3/test_run_native_ld_panel.py`

**2. [Design resolution] `reason` pinned via constant, not a string literal**
- **Issue:** The source doc-set renders the reason string BOTH ways — RESEARCH §4 as
  `reference-occlusion → undefined-LD` (spaced), the plan's `<what-built>` as
  `reference-occlusion→undefined-LD` (unspaced). Pinning either rendering would bake a
  coin-flip into the contract and cause a spurious 07b failure.
- **Resolution:** the test asserts against the module's exported
  `REASON_REFERENCE_OCCLUSION` constant and checks the SEMANTICS
  (`"reference-occlusion" in reason`; `"undefined-LD" in reason.replace(" ", "")`). Pins the
  meaning, leaves 07b free to choose the rendering. Documented in-test.

**3. [Design resolution] Region-1 fixture sourced, not duplicated**
- **Issue:** `test_occlusion_manifest.py` and `test_run_native_ld_panel.py` both need the
  region-1 topology, whose canonical home is `_REGION1_BIM_ROWS` in
  `test_occlusion_span_filter.py`. Re-typing an 11-row coordinate table twice more is
  precisely the drift T-m3-07a-02 warns about (a mis-encoded fixture lets a WRONG impl pass).
- **Resolution:** both consumers load the canonical constant via an `importlib`
  **file-path** load (robust to pytest's package/rootdir import mode — note `tests/` has no
  `__init__.py` while `tests/m3/` does, so a plain package import would be fragile). Safe to
  exec because that module's impl imports are all function-local. Single source of truth, zero duplication.

**4. [Scope guard] Extra boundary-regression test added**
- `test_no_nan_to_zero_conditioning_in_the_driver` asserts the driver never references
  `condition_ld_matrix` / `write_conditioned_ld_npz` / `nan_to_num`. It passes today and
  keeps the retired NaN→0 path (m3-06, FROZEN/HELD) from creeping back in during 07b.
  Mirrors the existing retired-Hail-A.3 boundary guard.

### Trap avoided (as briefed)

`conftest.chain_fixture` was **not** reused for the liftover test: it points at
`hg19ToHg38.over.chain.gz`, which is the **wrong direction** AND absent (it would always
skip, silently). `test_occlusion_manifest.py` carries its own skip-if-absent guard against
the hg38ToHg19 chain — the only chain present, and the correct direction.

### Not deviations (confirmed untouched)

`condition_ld_matrix.py` FROZEN, m3-06 HELD, no NaN→0 revival, no AoU perimeter contact, no
LD-loop re-fire, no implementation module written, 07b/07c not started. Entirely NC-State,
code-only, **$0**.

## GPFS object-store hazard

**Did NOT recur.** The commit (`296157a`, 5 files, 1432 insertions) and the annotated tag
both succeeded first try. No guarded blob recovery was needed. The 194 pre-existing broken
links reported by `git fsck` in older, already-pushed history were left alone as briefed.

## Commits

| Commit | Description |
|--------|-------------|
| `296157a` | `test(m3-07a): Wave 0 RED scaffolds for the panel occlusion span-filter + provenance` |
| tag `m3-07a-W7-T-WAVE0` | → `296157a` |

Staged with **explicit paths only** (never `git add -A`/`.`) — the shared multi-terminal
GPFS tree's pre-existing dirt (`sparse_parent_benchmark.tsv`, `.claude/settings.json`, the
`targeted_rerun_*` and `results_lsweep_*` trees) was left untouched.

## depends_on chain

**07b depends_on 07a; 07c depends_on 07b.** 07a is the ROOT and is now COMPLETE:

- OSF hard gate (Task 1) — **CLEARED** 2026-07-10, re-confirmed read-only 2026-07-15.
- Wave 0 RED spec (Task 2) — **LANDED** at `296157a` / tag `m3-07a-W7-T-WAVE0`.

**07b and 07c are UNBLOCKED but NOT AUTHORIZED** — Carter's standing instruction is
"07a then PAUSE". 07b (production code: `occlusion_span_filter.py`, `run_native_ld_panel.py`
+ `aou_ld_panel.py` `--exclude` wiring, `_PANEL_COLUMNS`) and 07c (`occlusion_manifest.py`,
`occlusion_present_rate_scan.py`, `drop_occluded_from_sumstats.py`) await explicit go.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| Gated real-`.bim` oracle test skips | `tests/m3/test_occlusion_span_filter.py::test_region1_real_window_known_answer_gated` | INTENTIONAL. No AoU perimeter access this phase; the real region-1 window `.bim` is absent NC-State. The SETTLED oracle `{10328,44784,46714,59097,66730}` + inventory are pinned as constants so the gated 276-region run has a concrete expected answer. Resolved at the gated in-perimeter validation, not by 07b/07c. |

The 4 impl modules are absent **by design** — Wave 0 is failing tests ONLY.

## Self-Check: PASSED

- `tests/m3/test_occlusion_span_filter.py` — FOUND
- `tests/m3/test_occlusion_manifest.py` — FOUND
- `tests/m3/test_occlusion_present_rate_scan.py` — FOUND
- `tests/m3/test_occlusion_lockstep_drop.py` — FOUND
- `tests/m3/test_run_native_ld_panel.py` — FOUND (modified)
- commit `296157a` — FOUND
- tag `m3-07a-W7-T-WAVE0` → `296157a9a86621dd6010617b36cf1eb9e495f236` — FOUND
- OSF gate `GATE_CONFIRMED_OK` — CONFIRMED
- RED verdict `RED_AS_EXPECTED`, 41 collected, zero collection errors — CONFIRMED
