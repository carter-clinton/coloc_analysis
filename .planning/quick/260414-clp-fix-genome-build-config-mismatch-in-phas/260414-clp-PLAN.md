---
quick_id: 260414-clp
description: fix genome-build config mismatch in Phase 9 cohort registry
date: 2026-04-14
type: quick
scope: config-only
---

# Quick Task 260414-clp — Fix genome-build config mismatch

## Context

Per 09-SMOKE.md Finding 1, empirical verification at rs7903146 (TCF7L2) across
the 4 cohorts shows:
- FinnGen R12: chr10:112998590 (GRCh37) despite config saying `GRCh38`
- MVP phs001672: chr10:112998589 (GRCh37) despite dbGaP file header claiming "build 38"
- BBJ hum0197-v3: chr10:114758349 (GRCh38) — correct

Impact if unfixed: harmonizers' `liftover_to_grch37` would attempt GRCh37→GRCh37
no-op via hg38ToHg19 chain, fail on 100% of rows, hit the 5% drop-rate RuntimeError.

## Task 1: Correct FinnGen + MVP genome_build in config/replication_cohorts.yaml

Two YAML blocks to edit:

**finngen_r12:**
- `genome_build: GRCh38` → `genome_build: GRCh37`
- `liftover_required: true` → `liftover_required: false`
- Add comment: `# Empirically verified GRCh37 in Phase 9 smoke 2026-04-14 (rs7903146 at chr10:112998590); see 09-SMOKE.md Finding 1.`

**mvp_phs001672:**
- `genome_build: GRCh38` → `genome_build: GRCh37`
- `liftover_required: true` → `liftover_required: false`
- Add comment: `# dbGaP file header claims 'Human genome build: 38' but coords are actually GRCh37 (rs7903146 at chr10:112998589). Verified in Phase 9 smoke 2026-04-14; see 09-SMOKE.md Finding 1.`

**bbj_hum0197_v3:** No change. Already correctly GRCh38.

Verification:
```bash
grep -c "GRCh37" config/replication_cohorts.yaml  # expect ≥ 2 new occurrences
grep -c "GRCh38" config/replication_cohorts.yaml  # expect 1 (BBJ only)
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import yaml; c=yaml.safe_load(open('config/replication_cohorts.yaml')); print('finngen_r12:', c['cohorts']['finngen_r12']['genome_build'], 'liftover:', c['cohorts']['finngen_r12']['liftover_required']); print('mvp:', c['cohorts']['mvp_phs001672']['genome_build'], 'liftover:', c['cohorts']['mvp_phs001672']['liftover_required']); print('bbj:', c['cohorts']['bbj_hum0197_v3']['genome_build'])"
# expect: finngen_r12: GRCh37 liftover: False  /  mvp: GRCh37 liftover: False  /  bbj: GRCh38
```

## Task 2: Regression sanity — Phase 9 tests still pass

```bash
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase9 -q --tb=short
# expect: 77 passed, 3 xfailed (baseline preserved)
```

## Task 3 (optional): Add genome-build sanity assertion in tests/phase9/test_trait_harmonization.py

Low priority — deferred. The YAML fix + existing pytest coverage is sufficient
for this quick task's scope. Noted as future enhancement.

## Constraints (per CLAUDE.md + request)

- Only `config/replication_cohorts.yaml` modified
- No changes to harmonizer Python code
- No downloads, no Snakemake runs
- 77/3 pytest baseline preserved
