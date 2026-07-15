---
status: complete
phase: m3-aou-afr-ld-panel-build
plan: 07a
source: [m3-07a-W7-osf-gate-and-red-scaffold-SUMMARY.md]
started: 2026-07-15
updated: 2026-07-15
verification_mode: automated
note: >
  m3-07a is a headless TDD RED-first deliverable — no UI, no server, no user-clickable
  surface. Every deliverable is machine-verifiable, so verification is AUTOMATED
  (Claude runs the check and records pass/fail) rather than interactive UAT. The
  SUCCESS CRITERION IS THAT THE OCCLUSION TESTS FAIL (RED) for the right reason, not
  that they pass. Accounts for the blast-radius fixes (a1e8693) layered on the
  executor's original RED (296157a).
---

## Current Test

[testing complete]

## Tests

### 1. OSF gate confirms read-only (GATE_CONFIRMED_OK)
expected: The pre-closed OSF gate re-confirms on an unmodified tree — the real amendment
  doc exists (exclusion + provenance + lockstep + tcujq), the tag and commit ac4c990
  resolve, and both settled-science body anchors verify byte-exact in their source docs
  (tail -c 5012 == 4543dcf4…; tail -c 5247 == 42d70167…).
result: pass

### 2. Amendment untouched; no placeholder file/tag created
expected: The posted amendment's last commit is still ac4c990 (never edited — an edit
  would diverge the repo copy from the OSF-posted bytes), and the never-existent
  placeholder file/tag (osf-amendment-panel-occlusion-exclusion / PANEL-OCCLUSION-…)
  were NOT created.
result: pass

### 3. RED-for-the-right-reason (4 new suites)
expected: The 4 occlusion suites COLLECT with zero collection errors and exit non-zero
  (RED); failures are call-time ModuleNotFoundError, not collection/import errors.
  Observed: 41 failed / 2 passed / 1 skipped, zero collection errors. (The 2 passes are
  fixture-shape self-checks on constants; the 1 skip is the gated real-.bim oracle.)
result: pass

### 4. No implementation module exists (RED preserved)
expected: src/python/occlusion_*.py and drop_occluded*.py do NOT exist — Wave 0 is
  failing tests only; the RED must stay RED until 07b is authorized.
result: pass

### 5. Frozen contracts untouched
expected: 0-line diff across the whole session on all 5 frozen files (plink_ld_to_npz.py,
  run_native_ld_panel.py, aou_ld_panel.py, ld_npz_to_rds.R, condition_ld_matrix.py).
result: pass

### 6. Driver suite — pre-existing tests stay GREEN, new tests RED
expected: tests/m3/test_run_native_ld_panel.py = 6 failed / 46 passed. The 45 pre-existing
  driver tests plus the NaN→0 creep-guard stay green; only the 6 new occlusion-integration
  tests are RED. (_MockPlink extension is additive; verified byte-identical for all
  pre-existing callers in the blast-radius sweep.)
result: pass

### 7. Fixture geometry + A1/A2 convention self-checks pass
expected: The two fixture self-check tests pass — the region-1 fixture reproduces the
  settled 60/29/7/31/31/17/29 bp deletion inventory and every row is the canonical
  (chr, id, cm, bp, A1=ALT, A2=REF) shape with id == chr:pos:REF:ALT. (A swapped A1/A2
  is not self-consistently possible — verified in the blast-radius sweep.)
result: pass

### 8. BLOCKER fix — occlusion_order no longer demands the wrong value
expected: test_occlusion_manifest.py no longer asserts snpC == "second_order" (which
  inverted the verdict and was underivable from coordinate geometry, forcing a hardcode).
  The column is now treated as OPTIONAL (RESEARCH §7:296); if present, every value must be
  "direct", matching verdict pair 3 (DEL 5922716 → SNP 5922718 = ref_span_overlap).
result: pass

### 9. HIGH fix — gated oracle compares row indices, not bp
expected: The gated real-window oracle compares enumerate() ROW INDICES against
  {10328,44784,46714,59097,66730} (renamed …_ROW_INDICES), not absolute bp via _pos_of.
  The prior bp comparison could never hold for a correct detector (region-1 spans
  ~1.98M–8.38M bp) and would fail a good impl at the gated run.
result: pass

### 10. MEDIUM fixes — four discriminating tests added
expected: New tests close contract holes that region-1's topology couldn't expose:
  same-position variant NOT occluded (strict-left < vs <=), doubly-occluded variant
  appears exactly once (no set()-hidden duplicate) with deterministic attribution,
  producer→consumer seam composition (build → lift → drop), and substring/token egress
  matching (n_samples/genotype_ac can no longer ride out). All present and RED-right.
result: pass

### 11. Full tests/m3 regression — failures == exactly the new tests
expected: Full tests/m3 fails on ONLY the new occlusion tests (no pre-existing breakage).
  After the blast-radius fixes: 47 failed / 363 passed / 31 skipped, where 47 == 41 (new
  occlusion-suite failures) + 6 (new driver failures). Every legacy test stays green.
result: pass
observed: "47 failed, 363 passed, 31 skipped in 401.77s" — 47 == 41 + 6 exactly. passed(363)
  and skipped(31) are IDENTICAL to the pre-blast-radius-fix run, so the 3 added tests
  contributed exactly 3 failures and broke nothing. Zero pre-existing regressions.

## Summary

total: 11
passed: 11
issues: 0
pending: 0
skipped: 0

## Gaps

[none — all 11 verified deliverables pass]

## Verdict

m3-07a **VERIFIED**. The phase goal (OSF gate honored + a RED-first executable spec that
defines the exclude-in-lockstep behavior 07b/07c must deliver) is achieved:

- The OSF hard gate is cleared and re-confirms read-only; the posted amendment was never
  edited, preserving byte-parity with the OSF copy.
- The RED is stable and RED for the RIGHT reason (zero collection errors, call-time
  ModuleNotFoundError), with no implementation module in the tree.
- No production code was touched (all 5 frozen contracts: 0-line diff) and no legacy test
  regressed (363 passed unchanged).
- The test CONTRACT — the actual downstream consumer of this wave, since 07b is built
  against it — was found defective by the blast-radius sweep and has been corrected
  (a1e8693): the occlusion_order inversion that would have forced a hardcoded
  false provenance label across all 276 regions, the gated oracle that could never pass a
  correct detector, and four holes region-1's topology could not expose.

⚠ CARRY-FORWARD for 07b (from the blast-radius sweep, LOW severity — recorded, not fixed):
1. `_MockPlink` banded mode RECORDS an `--exclude` it silently discards (the `--r gz`
   early-return never consumes the filtered window). A banded test asserting
   `exclude_calls == occluded_ids` would pass while modelling ZERO exclusion.
2. `_n_var_in_window` is exclude-blind dead code; a 07b test reaching for it to compute an
   expected size would silently contradict the mock.
3. `corrupt_regions` overwrites the NaN fingerprint (`m[0,0]=0.2`) if ever combined with
   `nan_snps` — no current test combines them.
4. The shared `_REGION1_BIM_ROWS` importlib load is safe ONLY because the payload is tuples
   of primitives (compared by value, defensively copied at both call sites). If 07b converts
   it to a dataclass/NamedTuple, class identity differs across the two module objects and
   isinstance/equality can silently fail.
5. The gated oracle's index ORIGIN (0- vs 1-based) is assumed 0-based; confirm against the
   real region-1 `.bim` header before trusting the equality at the gated run.

✅ CLOSED 2026-07-15 (was the last open non-blocking item): the OSF direct file GUID is
`trsx5` — https://osf.io/az52u/files/trsx5 — now filled into the amendment header and
`osf_deviations.md`. Capture also VERIFIED the append-only commitment: the update is a
SEPARATE NEW FILE, not a re-version of the amendment it withdraws (`trsx5` 1 revision;
`tcujq` still 1 revision, unmodified) → no posting deviation.
