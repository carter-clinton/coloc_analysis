---
quick_id: 260414-clp
status: complete
date: 2026-04-14
---

# Quick Task 260414-clp — Summary

## Description

Fix genome-build config mismatch in Phase 9 cohort registry
(`config/replication_cohorts.yaml`) surfaced by 09-SMOKE.md Finding 1.

## Changes

Single file edited: `config/replication_cohorts.yaml`

**finngen_r12 block:**
- `genome_build: GRCh38` → `genome_build: GRCh37`
- `liftover_required: true` → `liftover_required: false`
- 3-line comment added citing smoke verification evidence

**mvp_phs001672 block:**
- `genome_build: GRCh38` → `genome_build: GRCh37`
- `liftover_required: true` → `liftover_required: false`
- 4-line comment added noting dbGaP header vs actual coord mismatch

**bbj_hum0197_v3:** unchanged (already correctly GRCh38).

## Verification

| Check | Expected | Result |
|-------|----------|--------|
| grep `genome_build: GRCh37` count | 3 (FinnGen + MVP + GBMI) | ✓ 3 |
| grep `genome_build: GRCh38` count | 1 (BBJ only) | ✓ 1 |
| yaml.safe_load roundtrip | no error | ✓ |
| `pytest tests/phase9` | 77 passed, 3 xfailed | ✓ 77 passed, 3 xfailed |

## Impact

Before fix: first Phase 9 first-production run would fail in harmonizer's
`liftover_to_grch37` step for both FinnGen and MVP — the GRCh37→GRCh37 no-op
via hg38ToHg19 chain file would drop 100% of rows, triggering the 5% drop-rate
RuntimeError.

After fix: harmonizer correctly skips liftover for FinnGen + MVP (data is
already GRCh37); applies liftover only to BBJ (correctly GRCh38).

## Files

- `config/replication_cohorts.yaml` (edited)
- `.planning/quick/260414-clp-fix-genome-build-config-mismatch-in-phas/260414-clp-PLAN.md`
- `.planning/quick/260414-clp-fix-genome-build-config-mismatch-in-phas/260414-clp-SUMMARY.md`

## Deferred (per plan Task 3)

Genome-build sanity assertion in `tests/phase9/test_trait_harmonization.py`
deferred — existing pytest coverage + YAML comment are sufficient for this
quick task's scope.
