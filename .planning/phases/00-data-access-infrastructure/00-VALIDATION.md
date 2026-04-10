---
phase: 0
slug: data-access-infrastructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-09
---

# Phase 0 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Snakemake --dryrun + pytest (for Python utils) + bash assertions |
| **Config file** | tests/toy_3locus/config_test.yaml |
| **Quick run command** | `snakemake --snakefile tests/toy_3locus/Snakefile.test -n --cores 2 --use-conda` |
| **Full suite command** | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` |
| **Estimated runtime** | ~10 minutes (target <15 min per REQ-9) |

---

## Sampling Rate

- **After every task commit:** Run `snakemake -n` dry-run to verify DAG integrity
- **After every plan wave:** Run full toy 3-locus smoke test
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 600 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 00-01-01 | 01 | 1 | REQ-12 | grep | `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config \| wc -l` returns 0 | ⬜ pending |
| 00-01-02 | 01 | 1 | REQ-9 | file-exists | `test -f envs/r_coloc.yml && test -f envs/python_stats.yml && test -f envs/plink.yml` | ⬜ pending |
| 00-02-01 | 02 | 1 | REQ-1 | file-exists | `test -f data/manifest.yaml` | ⬜ pending |
| 00-03-01 | 03 | 2 | REQ-9 | integration | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` exits 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `config/pipeline.yaml` — created with root path variables
- [ ] `tests/toy_3locus/` — directory structure with Snakefile.test and config_test.yaml
- [ ] conda envs resolved and installable

*Existing Snakemake infrastructure covers most framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Data source reachability | REQ-1 | Requires network access + portal authentication | Visit each URL in data_access.md, confirm download starts |
| OSF pre-registration | REQ-1 | Requires OSF account and manual form submission | Submit pre-registration, confirm DOI assigned |
| All of Us DURA status | REQ-1 | Requires contacting NC State Signing Official | Email/call Signing Official, document response |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 600s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
