---
phase: quick-260825-qpf
verified: 2026-08-25T21:00:00Z
status: passed
score: 27/27 checks verified
overrides_applied: 0
---

# Quick Task 260825-qpf: Remediate the adversarial review of the pairwise-completeness scanner — Verification Report

**Task goal:** Remediate an external adversarial review of the pairwise-completeness scanner —
three correctness fixes (F6 normalised seek index, F4 index-based pair_key, F5 exact-AF-tie
max-loss rule), reporting/documentation changes (F2 edge-clip counter, globally-invariant/--mac-1
parity counters, F1 --nonfounders coupling enforcer, F7 required denominators), the plink
pairwise-complete FALSIFIER added to the PENDING PASTE as STEP 1, and the R6 occ_measure/
citation gap. Instrument-only; the paste is EXTENDED but NOT RUN; no criterion change; no result
asserted.

**Verified:** 2026-08-25, HEAD `abd1c01` (branch `m3-W2-aou-deltas`, not ahead of origin)
**Method:** Independent re-derivation against the actual codebase — every claim in the SUMMARY was
re-executed from scratch with fixtures I built myself, not by reading the SUMMARY's assertions as
fact. No edits, no commits, no VM/OSF contact, the PENDING PASTE and the plink falsifier were never
run.

## Summary

Every item the launching agent asked me to spend effort on reproduces correctly against the actual
shipped code, independent of the SUMMARY's own narration. I found **no gaps**. One residual,
inherent limitation of the plink falsifier's design is noted below as an FYI (not a gap — it is a
property of any finite-hypothesis discriminator and is already implicitly covered by the
SUMMARY/HANDOFF's own "the premise is UNCONFIRMED until it runs" framing).

## Cheap Reconfirmation of Facts Already Independently Confirmed by the Launching Agent

| # | Check | Command | Observed | Status |
|---|-------|---------|----------|--------|
| 1 | Frozen-surface guard (incl. `aou_ld_panel.py`) empty vs `e63b9af` | `git diff --stat e63b9af HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/ \| wc -l` | `0` | PASS |
| 2 | Amendment paste block, safe two-step file form | `awk '/PASTE INTO OSF FROM HERE/{f=1;next}/PASTE ENDS HERE/{f=0}f' <amendment> > pb.txt; wc -c < pb.txt; md5sum pb.txt` | `22945` / `13a49f543cabcc27ce9f1e589783c060` | PASS |
| 3 | vbu enforcer | `bash 260817-vbu-verify.sh all` | exit `0`, `2070` bytes, `83d60d91c6861c1f13ac728c059442ba` | PASS |
| 4 | `--collect-only` counts | `pytest tests/m3 --collect-only -q` (full / without new file / new file alone) | `1134` / `1054` / `80` (1054+80=1134) | PASS |
| 5 | All 4 embedded python heredocs in the PENDING PASTE parse clean | extracted both `PYEOF`- and `EOF`-delimited blocks, `ast.parse` each | `found 4 heredoc blocks`, all `ast.parse OK` | PASS |

## Focus Item 1 — The F1 enforcer discriminates (grep green-on-broken; `ast` red-on-broken)

Built a scratch copy of `aou_ld_panel.py`, removed `--nonfounders` from the actual square-branch
argv line (2919) only, leaving the docstring (×2) and the in-code comment intact.

| Check | Command | Observed | Status |
|-------|---------|----------|--------|
| grep count on the ORIGINAL file | `grep -c -- "--nonfounders" aou_ld_panel.py` | `4` (2 docstring + 1 comment + 1 argv) | — |
| grep count AFTER removing the flag from the argv only | same, on the scratch copy | `3` — **green-on-broken confirmed**: a textual pin would stay GREEN with the coupling broken | PASS |
| `ast`-based pin (the shipped enforcer's exact logic), reproduced by hand against the scratch copy | parse `build_plink_ld_command`, isolate the `mode == "square"` branch, collect string constants, assert `"--nonfounders" in emitted` | `emitted constants: ['--mac', '--r', '--write-snplist', '1', 'bin4', 'square']` → assertion **RAISES** (`AST-PIN-RED`) | PASS — the `ast` form correctly goes RED when the grep form stays green |

**Conclusion:** the claim that the executor correctly rejected a textual grep pin in favor of an
`ast` pin is verified by direct reproduction of both halves, not by reading the SUMMARY's narration.

## Focus Item 2 — The three correctness fixes actually fix the defects

All four fixtures below were constructed independently (not copied from the test file) and run
against the actual shipped module (`src/python/pairwise_completeness_scan.py` at HEAD).

| Fix | Fixture (built independently) | Command | Observed | Status |
|-----|-------------------------------|---------|----------|--------|
| **F6** (seek index) | 3-variant fixture, distinguishable blocks | `read_variant(1)` vs `read_variant("1")` vs `read_variant(1.0)` | all three dosage arrays IDENTICAL (`[1,2,2,2]`) | PASS |
| **F6** (non-integral raises) | same fixture | `read_variant(1.5)` | raises `ValueError: non-integral variant index 1.5: ...` | PASS |
| **F4** (pair-key undercount) | one deletion, two partners BOTH carrying vid `.`, one pair undefined, one defined | `scan_region(...)`, `summarize(...)` | `n_distinct_pairs=2`, `n_undefined_distinct_pairs=1`; the OLD vid-keyed scheme applied by hand to the same rows collapses to `n_distinct_pairs=1` | PASS |
| **F5** (exact-tie max-loss) | 8 samples, deletion A1 dosages `[2,2,2,2,0,0,0,0]` (`af_a1` exactly `0.5`), partner missing at 3 of the 4 A2-carriers | `evaluate_pair` via `scan_region` | `del_carriers_marginal=4`, `del_carriers_lost=3`, `del_carriers_lost_frac=0.75`, `del_minor_allele_tie=True`, `undefined=False`, binned into `(0.5,0.9]` (not `"0"`) | PASS |
| **F7** (explicit-or-raise) | — | `pcs.summarize("R", [])` | `TypeError: summarize() missing 2 required keyword-only arguments: 'n_deletions' and 'n_candidates_edge_clipped'` | PASS |
| Regression (F4) | pre-existing `test_deletion_deletion_neighbour_emits_two_rows_one_pair_key` | `pytest -k ...` | 1 passed | PASS |
| Regression (F5) | 4 pre-existing genotype tests (00057-mirror, partial-confounding, zero-gradient, lost-frac-1.0) | `pytest -k "MIRRORS_A_MEASURED_CASE or partial_confounding_is_DEFINED or fully_defined_pair_has_zero_gradient or lost_frac_one_implies_undefined"` | 4 passed | PASS |

## Focus Item 3 — F2 is counted, not changed

Diffed `enumerate_candidates` / `iter_bim_windows` against `e63b9af` directly (not via the test
suite):

- `iter_bim_windows(..., pad_bp=0)`: the new code computes `start_bp - pad, end_bp + pad` with
  `pad = int(pad_bp)`; at `pad_bp=0` this is algebraically **identical** to the old unconditional
  `start_bp, end_bp` — confirmed by reading both function bodies side by side.
- `enumerate_candidates(..., region_bounds=None)`: the new `_in_bounds(pos, region_bounds)` helper
  returns `True` unconditionally when `region_bounds is None`; the two new `continue` guards
  (deletion-side and partner-side) are therefore **no-ops** when called with the default, leaving
  the `bisect_left`/`bisect_right` windowing logic byte-identical to the pre-remediation function.
  The only real change to the emitted rows is the `pair_key` computation (F4, verified above).
- **Fresh negative control (also serves as Focus Item 8, see below):** built an independent
  region-boundary fixture and ran it through the actual CLI `main()` (not `enumerate_candidates`
  directly) — confirms the clip counter and the emitted-set invariant end-to-end, including the
  `n_deletions` denominator excluding an out-of-region deletion.

| Check | Command | Observed | Status |
|-------|---------|----------|--------|
| Regression: 2 pre-existing one-pass tests | `pytest -k "..."` | (exercised as part of the full suite below; both green) | PASS |

## Focus Item 4 — The falsifier's logic

Re-derived the 4-hypothesis table by hand from the sample-set algebra:

- **pairwise-complete**: `(X,Y)` and `(X,Z)` are each computed only over their own pair's
  called-intersection, independent of which other variants are in the run → `(X,Y)` NaN (X
  invariant there, per the MEASURED halt record), `(X,Z)` finite (Z chosen for high retention),
  `(Y,Z)` finite, and the 2-variant reruns reproduce the SAME per-pair answer as the 3-variant run
  (pairwise semantics don't depend on run size). Matches the paste's table row exactly.
- **mean-imputation**: no missingness constraint survives at all → everything finite in every run.
  Matches.
- **listwise-over-the-window**: the surviving sample set is the intersection of ALL variants in the
  CURRENT RUN. In the 3-variant run, `(X,Z)` is evaluated over `called(X)∩called(Y)∩called(Z)`,
  which is a *subset* of the already-invariant `called(X)∩called(Y)` — still invariant, still NaN.
  Dropping Y from the run (the 2-variant `{X,Z}` run) removes that extra restriction, restoring the
  `called(X)∩called(Z)` set where X is NOT invariant → finite. This is exactly the discriminator
  the paste calls out, and the algebra checks out.
- **Z mis-selected**: if X is invariant in `called(X)∩called(Z)` regardless of Y (i.e., the
  retention floor should have failed), pairwise-complete semantics make `(X,Z)` NaN in BOTH the
  3-variant and 2-variant runs — the 2-variant cell is what tells this apart from real listwise.
  Matches.
- All four rows differ from each other in at least the `2-var (X,Z)` cell, and the verdict code
  (`if nan(xy3) and not nan(xz3) ...`) requires an EXACT match on all 5 cells before printing
  `PAIRWISE-COMPLETE` — any other combination falls through to `UNCLASSIFIED`, itself a STOP.

| Check | Evidence | Status |
|-------|----------|--------|
| Z selected empirically with a fail-safe STOP | 1a's `assert best_ret >= FLOOR` raises `AssertionError` naming the failure mode as FAIL-SAFE if no candidate clears 0.80; read directly in the paste | PASS |
| STEP order: falsifier → 00057 cross-check → sweep | `_STEP_FALSIFIER`/`_STEP_CROSSCHECK`/`_STEP_SWEEP` constants match the paste's actual `=== STEP 1/2/3 ===` headings verbatim; `text.index()` ordering asserted and exercised live | PASS (test run, see below) |
| 2-variant `{X,Z}` control separates real listwise from a mis-selected Z | confirmed by hand-derivation above — it is the only cell that differs between those two hypotheses | PASS |
| Discard-on-mismatch consequence is unambiguous | STEP 1d: "STOP. Paste everything verbatim. DISCARD THE SWEEP. Do NOT run STEP 2. Do NOT run STEP 3." — read directly in the paste, and pinned by a newline-tolerant regex test | PASS |
| Live test run of all T3 assertions | `pytest tests/m3/test_pairwise_completeness_scan.py -k "falsifier or no_longer_claims or r6_records or ..."` | `17 passed` | PASS |
| Look hard for a FALSE PASS | See "Noted limitation" below | see note |

**Noted limitation (not a gap):** the falsifier's verdict logic can only distinguish among the
finite set of hypotheses it explicitly enumerates (pairwise-complete / mean-imputation /
listwise-over-the-window / Z-mis-selected). A conceivable fifth plink missingness semantics that
happens to coincidentally reproduce the exact same 5-cell NaN/finite pattern as pairwise-complete
would not be caught. This is an inherent property of any finite-hypothesis discriminator, not a
defect in this remediation, and it is already effectively disclosed by the SUMMARY's own framing
("the premise is UNCONFIRMED until it runs") — I flag it here only because the task asked me to
look hard for a false-pass path, not because it changes the verification outcome. Any observed
pattern that doesn't exactly match one of the 4 rows already falls through to `UNCLASSIFIED`,
which is itself a STOP, so the design is fail-closed against the hypotheses it does *not* consider
being silently accepted as pairwise-complete.

## Focus Item 5 — R6 amendment honesty

| Check | Command | Observed | Status |
|-------|---------|----------|--------|
| R6 block (scoped `^R6.` … `^R7.`) names `occ_measure` | `re.search(r"^R6\.(.*?)^R7\.", ...)` then inspect | block reads: adds `/home/jupyter/occ_measure/` + measurement-sweep outputs + falsifier working files, with dated provenance `(added 2026-08-25, quick-260825-qpf: this RECORDS an allowance already exercised with Carter's explicit go from 2026-08-19 onward ... It grants no new directory and no new deletion right.)` | PASS |
| No new directory beyond `occ_measure/` | read the full R6 block | only `/home/jupyter/occ_measure/` is newly named; the pre-existing 5 paths + R8 gate artifacts are unchanged | PASS |
| No new deletion right | read the full R6 block + the `ONE NARROW DELETION EXCEPTION` sentence immediately below it | untouched — still scoped only to "the .npz copy you yourself downloaded into native_ld_scratch/" | PASS |
| vbu §6b card untouched | (1) code inspection: `section_card()` in `260817-vbu-verify.sh:183` extracts `block "$AP" '^STEP 6b' '^STEP 7'` — R6 sits at line 32, `STEP 6b` near line 128, an insertion above the block cannot shift a relative line number; (2) re-ran `bash 260817-vbu-verify.sh all` myself | exit `0`, `2070` bytes, `83d60d91c6861c1f13ac728c059442ba` — byte-identical to the pre-remediation baseline | PASS |

## Focus Item 6 — No result asserted anywhere; three OPEN questions stay OPEN

| Check | Command | Observed | Status |
|-------|---------|----------|--------|
| No asserted prevalence/boundary/tail value | `grep -rIn "prevalence is\|boundary width is\|tail is [0-9]" .planning/quick/260825-qpf-*/ .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` | only hit is the PLAN's own verify-command documentation string (a grep pattern, not an asserted value) | PASS |
| OPEN / UNCONFIRMED language present | grep for `OPEN` / `UNCONFIRMED` in the paste and SUMMARY | present, describing all three open questions and the falsifier's unconfirmed status | PASS |

## Focus Item 7 — Full `tests/m3` run, myself

Ran the complete suite myself in one invocation (13:50 min), matching the documented ~13-14 min
runtime:

```
1101 passed, 33 skipped, 4 warnings in 830.54s (0:13:50)
```

| Check | Expected (SUMMARY/HANDOFF claim) | Observed (my own run) | Status |
|-------|-----------------------------------|------------------------|--------|
| passed | 1101 | 1101 | PASS |
| skipped | 33 | 33 | PASS |
| failed | 0 | 0 | PASS |
| collected | 1134 | 1134 (via `--collect-only`) | PASS |
| component-exact reconciliation | 1083+18=1101 passed; 1116+18=1134 collected; 1054+80=1134 (new-file-isolated count) | all three identities confirmed independently (see cheap-reconfirmation table, #4) and the 18 named tests in `HANDOFF.json` match the ones actually collected in the new file | PASS |

`tests/m3/sparse_parent_benchmark.tsv` was dirtied with fresh timing noise by my run (pre-existing
behavior, documented and expected — `test_sparse_parent_benchmark.py` is its only writer). Restored
with `git checkout -- tests/m3/sparse_parent_benchmark.tsv`; confirmed clean afterward.
`git status -sb` shows no `ahead` and no changes beyond the pre-existing untracked paths that were
present before this verification began.

## Focus Item 8 — Fresh negative control of my own

Targeted F2 (the edge-clip counter), judged the highest-risk item since it is a "re-dispositioned,
reported-not-changed" area rather than a straightforward bug fix. Built an independent fixture —
4 variants, region bounds `[1000,1010]`, a boundary deletion at `1008` (span_end `1010`,
`window_bp=5`), one in-bounds partner at `1005`, one out-of-bounds partner at `1012`, and a
completely separate interior deletion at `1050` (outside this region entirely) — and drove it
through the actual CLI (`pcs.main([...])`), not through internal functions directly.

```
n_deletions               = 1   (the interior deletion at 1050 does NOT inflate this)
n_candidate_rows          = 1
n_candidates_edge_clipped = 1   (the out-of-bounds partner at 1012 IS counted)
1 row emitted: DEL_EDGE x PARTNER_IN (1008, 1005) — the clipped partner (1012) does not appear
```

Result: **PASS** — the out-of-bounds partner is counted but never emitted, the emitted set is
exactly the in-bounds candidate, and the denominator correctly excludes the out-of-region deletion.

## Overall Assessment

| Category | Result |
|----------|--------|
| Correctness fixes (F4, F5, F6, F7) | All reproduce correctly on independently-built fixtures |
| F1 enforcer discrimination | Confirmed both halves (grep green-on-broken; `ast` red-on-broken) |
| F2 re-dispositioning | Confirmed behavior-preserving by direct code diff + a fresh end-to-end CLI negative control |
| Falsifier (F3) | Logic re-derived and checked by hand; step order, Z-selection fail-safe, and discard consequence all confirmed; one inherent (non-blocking) limitation noted |
| R6 amendment | Confirmed to record, not grant; vbu card provably undisturbed |
| No result asserted | Confirmed |
| Suite | 1101 passed / 33 skipped / 0 failed / 1134 collected, reproduced live, component-exact |
| Repo hygiene | No `ahead`, no unintended changes, pre-existing dirty file restored |

No gaps found. No human verification items — every claim in scope was independently
programmatically re-derivable, and nothing here depends on running the (deliberately unrun) plink
falsifier.

**Score: 27/27 checks verified**

---

_Verified: 2026-08-25T21:00:00Z_
_Verifier: Claude (gsd-verifier)_
