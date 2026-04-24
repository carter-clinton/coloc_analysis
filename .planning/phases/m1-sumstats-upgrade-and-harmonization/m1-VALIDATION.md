---
phase: m1
slug: sumstats-upgrade-and-harmonization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-24
---

# Phase M1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Filled
> by planner from `m1-RESEARCH.md` `## Validation Architecture` block; the
> nine Dimension-8 acceptance criteria listed there are the phase gate.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python harmonizers + reducers) + Snakemake `--dry-run` + Quarto `--no-execute` |
| **Config file** | `pyproject.toml` (pytest markers), `workflow/Snakefile` (DAG), `envs/m1-*.yml` (conda) |
| **Quick run command** | `pytest tests/m1/ -m "not slow" -q` |
| **Full suite command** | `pytest tests/m1/ -q && snakemake -s workflow/Snakefile --dry-run --cores 1 && quarto check` |
| **Estimated runtime** | Quick ≤ 90 s; full (incl. 1-chrom smoke harmonize) ≤ 15 min |

Snakemake runtime: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Py 3.11). Never invoke from miniconda3 base.

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/m1/<module>.py -q` on the module touched + `snakemake -s workflow/Snakefile --dry-run --cores 1 <rule>` for any rule edit.
- **After every plan wave:** Run full suite + `snakemake -s workflow/Snakefile --list` to confirm DAG parses.
- **Before `/gsd-verify-work`:** Full suite green AND all nine Dimension-8 criteria pass on a 1-chrom smoke (chr22) dry-run AND dual SHA-256 manifests generated without diffs on re-run.
- **Max feedback latency:** 90 s (unit tests) / 15 min (full incl. smoke harmonize).

---

## Per-Task Verification Map

> Planner fills this table per task; status columns updated by executor. Rows
> reference plan file IDs (`m1-XX-<slug>-PLAN.md`) and Dimension-8 criteria
> from RESEARCH.md §Validation Architecture.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD     | TBD  | 0    | REQ-SNAKEMAKE-CI | — | egress + env probes pass | integration | `bash tests/m1/wave0_probes.sh` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/m1/conftest.py` — shared fixtures (chr22 smoke fixture rows from SUMSTATS-UPGRADE.tsv; tmp_path sharding)
- [ ] `tests/m1/test_harmonizer_contract.py` — 10-column schema invariants (runs against any `harmonize_*.py` via `sumstats_utils.validate_canonical_frame`)
- [ ] `tests/m1/test_liftover.py` — b38→b37 liftover helper on known-good synthetic variants + CrossMap chain availability probe
- [ ] `tests/m1/test_palindromic_filter.py` — palindromic-SNP filter on A/T + G/C synthetic variants
- [ ] `tests/m1/test_ldsc_star_reducer.py` — `.log` parser for `gcov_int` from a fixture LDSC log
- [ ] `tests/m1/test_inventory_yaml.py` — `config/trait_inventory.yaml` schema validator
- [ ] `tests/m1/wave0_probes.sh` — MAGIC FTP egress probe; GWAS-Catalog Giri 2019 summary-availability curl probe; LDSC 2-trait smoke benchmark
- [ ] `envs/m1-harmonize.yml`, `envs/m1-munge.yml`, `envs/m1-ldsc-rg.yml`, `envs/m1-qc.yml` — conda env manifests exist and solve
- [ ] `data/reference/chain/hg38ToHg19.over.chain.gz` — staged before any harmonizer runs on b38 rows

*If none of the above exist at phase start: Wave 0 creates all.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GIGASTROKE per-ancestry GCST accession lock (D-02) | REQ-TRAIT-INVENTORY | EBI GWAS-Catalog browse requires human; no API endpoint exposes the series-to-integer mapping | Visit `ebi.ac.uk/gwas/publications/36180795`; pin each `(ancestry, subtype)` to an integer GCST; commit to `SUMSTATS-UPGRADE.tsv` replacing `GCST90104540-series` placeholders |
| Aragam 2022 ZIP unpack verification (D-03) | REQ-TRAIT-INVENTORY | ZIP contents undocumented until opened; AFR branch decision depends on inspection | `unzip -l data/raw/sumstats_v2/Aragam2022/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip > aragam_zip_manifest.txt`; commit manifest; if AFR file absent, route row 23 to Klarin 2018 fallback |
| MVP Giri D-06 primary GWAS-Catalog check | REQ-PUBLIC-DATA-ONLY, REQ-TRAIT-INVENTORY | Publication-page browse; no deterministic API probe that returns sumstat-download state | `curl -sS https://www.ebi.ac.uk/gwas/publications/30578418` then `grep -i "summary statistics"` in the HTML; record primary-attempt outcome in `SUMSTATS-MANUAL-FETCH-STATUS.md` |
| AoU Researcher Workbench AFR-SBP derivation (D-06 fallback) | REQ-PUBLIC-DATA-ONLY | AoU compute runs inside Terra web UI; cannot be scripted from GPFS | Follow `AOU-LD-PIPELINE.md` §2 P1–P7; export summary-level AFR SBP effects only; log in `aou-egress-audit-log.md` |
| OSF amendment posting (M2 gate, not M1 closeout gate) | REQ-OSF-PREREG (M2) | osf.io web UI action | Paste M1 completion date + commit hash + raw SHA-256 manifest into `OSF-AMENDMENT-TEXT-2026-04-22.md` placeholders; submit via osf.io/pvb5j web UI (Carter action) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies declared
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (env YAMLs, chain file, fixture FTP/GWAS-Catalog probes, LDSC benchmark)
- [ ] No `watch`-mode flags (LSF-hostile)
- [ ] Feedback latency < 90 s unit / < 15 min full-smoke
- [ ] All nine Dimension-8 criteria from RESEARCH.md §Validation Architecture have at least one mapped test
- [ ] `nyquist_compliant: true` set in frontmatter after planner fills per-task verification map

**Approval:** pending
