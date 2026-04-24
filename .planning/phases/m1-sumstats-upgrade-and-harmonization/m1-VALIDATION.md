---
phase: m1
slug: sumstats-upgrade-and-harmonization
status: draft
nyquist_compliant: true
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
> from RESEARCH.md §Validation Architecture. Automated commands copied verbatim
> from each task's `<automated>` verify block in the corresponding PLAN.md.
> security_enforcement is disabled for this phase (data-pipeline only); Threat
> Ref column shows `—` and Secure Behavior shows `data-pipeline integrity`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| m1-00-T1 | m1-00 | 0 | REQ-SNAKEMAKE-CI | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/ --collect-only 2>&1 \| grep -E "collected\|error" && for f in envs/m1-*.yml; do test -f "$f" \|\| exit 1; done && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_palindromic_filter.py tests/m1/test_harmonizer_contract.py -x 2>&1 \| tail -3` | ❌ W0 | ⬜ pending |
| m1-00-T2 | m1-00 | 0 | REQ-SNAKEMAKE-CI | — | data-pipeline integrity | smoke | `test -f data/external/liftover/hg38ToHg19.over.chain.gz && gzip -t data/external/liftover/hg38ToHg19.over.chain.gz && test -d data/external/ldscore/eur_w_ld_chr && test -f data/external/ldscore/w_hm3.snplist && test -f tests/m1/wave0_probes.sh && test -f tests/m1/wave0_probes.log && grep -q "Wave 0 pre-flight" .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md` | ❌ W0 | ⬜ pending |
| m1-00-T3 | m1-00 | 0 | REQ-TRAIT-INVENTORY | — | N/A (human-gated decision) | smoke | `! grep -q "GCST90104540-series" .planning/amendments/SUMSTATS-UPGRADE.tsv && grep -q "DEC-2026-04-24-01" .planning/DECISIONS.md && grep -q "DEC-2026-04-24-02" .planning/DECISIONS.md && test -f data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt` | ❌ W0 | ⬜ pending |
| m1-01-T1 | m1-01 | 1 | REQ-PUBLIC-DATA-ONLY | — | data-pipeline integrity | unit | `bash bin/download_sumstats_v2.sh --help 2>&1 \| grep -q manifest && test -f config/download_manifest_m1_portal.tsv && awk -F'\t' 'NR>1 {print NF}' config/download_manifest_m1_portal.tsv \| sort -u \| wc -l \| grep -q '^1$' && test -f src/snakemake/rules/m1_download.smk && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_freeze_sha256_manifest.py -x 2>&1 \| tail -3 && grep -r "/rs1/researchers\|/gpfs_common\|/share/clintonlab" src/snakemake/rules/m1_download.smk bin/download_sumstats_v2.sh config/download_manifest_m1_portal.tsv src/python/freeze_sha256_manifest.py \| grep -v "^Binary" && echo "FAIL: hardcoded path found" && exit 1 \|\| echo "path-parameterization OK"` | ❌ W0 | ⬜ pending |
| m1-01-T2 | m1-01 | 1 | REQ-PUBLIC-DATA-ONLY | — | data-pipeline integrity | integration | `test -f data/raw/sumstats_v2/sha256_manifest.tsv && [ $(wc -l < data/raw/sumstats_v2/sha256_manifest.tsv) -ge 28 ] && test -f .planning/amendments/sha256_manifest_m1_frozen.tsv` | ❌ W0 | ⬜ pending |
| m1-02a-T1 | m1-02a | 2 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_yengo.py tests/m1/test_harmonize_glgc.py -x --tb=short 2>&1 \| tail -5 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import sys; sys.path.insert(0, 'src/python'); from sumstats_utils import build_rsid_to_chrpos, CANONICAL_COLS, filter_palindromic_ambiguous, liftover_to_grch37; print('OK')" && grep -c "^def " src/python/harmonize_yengo.py \| awk '$1 >= 2' && grep -c "^def " src/python/harmonize_glgc.py \| awk '$1 >= 2'` | ❌ W0 | ⬜ pending |
| m1-02a-T2 | m1-02a | 2 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_wuttke.py tests/m1/test_harmonize_magic.py -x --tb=short 2>&1 \| tail -5 && test -f src/snakemake/rules/m1_harmonize.smk && grep -cE "^rule harmonize_(yengo\|glgc\|wuttke\|magic)" src/snakemake/rules/m1_harmonize.smk \| awk '$1 >= 4' && grep -q "harmonized_sumstats:" config/pipeline.yaml && grep -q "harmonized_parquet:" config/pipeline.yaml && ! grep -rE "/rs1/researchers\|/gpfs_common\|/share/clintonlab" src/python/harmonize_yengo.py src/python/harmonize_glgc.py src/python/harmonize_wuttke.py src/python/harmonize_magic.py src/snakemake/rules/m1_harmonize.smk` | ❌ W0 | ⬜ pending |
| m1-02b-T1 | m1-02b | 2 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_diamante.py tests/m1/test_harmonize_gigastroke.py tests/m1/test_harmonize_aragam.py -x --tb=short 2>&1 \| tail -5 && test -f src/python/harmonize_diamante.py && test -f src/python/harmonize_gigastroke.py && test -f src/python/harmonize_aragam.py && grep -q "_branch_for_afr" src/python/harmonize_aragam.py && grep -q "GCST90104540-series" src/python/harmonize_gigastroke.py` | ❌ W0 | ⬜ pending |
| m1-02b-T2 | m1-02b | 2 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_harmonize_gbmi_liftover.py tests/m1/test_verify_evangelou_sbp.py -x --tb=short 2>&1 \| tail -5 && grep -q "liftover-chain" src/python/harmonize_gbmi.py && grep -q "hg38ToHg19" src/python/harmonize_gbmi.py && test -f src/python/verify_evangelou_sbp.py && grep -q "m1_freeze_harmonized_sha256_manifest" src/snakemake/rules/m1_harmonize.smk && grep -q "verify_evangelou_sbp" src/snakemake/rules/m1_harmonize.smk` | ❌ W0 | ⬜ pending |
| m1-03-T1 | m1-03 | 3 | REQ-SNAKEMAKE-CI | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_reduce_ldsc_rg_matrix.py tests/m1/test_m1_trait_keys.py -x --tb=short 2>&1 \| tail -5 && test -f src/snakemake/rules/m1_munge.smk && test -f src/snakemake/rules/m1_ldsc_rg.smk && test -f src/python/reduce_ldsc_rg_matrix.py && test -f src/python/m1_trait_keys.py && ! grep -q "rg-cross" src/snakemake/rules/m1_ldsc_rg.smk src/python/reduce_ldsc_rg_matrix.py && grep -q "comma-separated" src/snakemake/rules/m1_ldsc_rg.smk \|\| grep -q -- "--rg " src/snakemake/rules/m1_ldsc_rg.smk && ! grep -r "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/snakemake/rules/m1_munge.smk src/snakemake/rules/m1_ldsc_rg.smk src/python/reduce_ldsc_rg_matrix.py src/python/m1_trait_keys.py` | ❌ W0 | ⬜ pending |
| m1-03-T2 | m1-03 | 3 | REQ-SNAKEMAKE-CI | — | data-pipeline integrity | integration | `test -f data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv && test -f data/processed/ldsc_overlap/rg_matrix_long.tsv && test -f data/processed/ldsc_overlap/rg_validation_warnings.json && MATRIX_ROWS=$(wc -l < data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv) && [ "$MATRIX_ROWS" -ge 20 ] && LOG_COUNT=$(ls data/processed/ldsc_overlap/rg_logs/focal_*.log 2>/dev/null \| wc -l) && [ "$LOG_COUNT" -ge 1 ] && MUNGED_COUNT=$(ls data/processed/ldsc_overlap/munged/*.sumstats.gz 2>/dev/null \| wc -l) && [ "$MUNGED_COUNT" -ge 30 ]` | ❌ W0 | ⬜ pending |
| m1-04-T1 | m1-04 | 4 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | unit | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_build_trait_inventory.py -x --tb=short 2>&1 \| tail -3 && test -f src/R/qc/m1_qc_report.qmd && test -f src/R/qc/m1_qc_index.qmd && test -f src/R/qc/control_loci.csv && test -f src/python/build_trait_inventory.py && test -f src/snakemake/rules/m1_qc.smk && grep -q "m1_qc_per_trait" src/snakemake/rules/m1_qc.smk && grep -q "m1_qc_index" src/snakemake/rules/m1_qc.smk && grep -q "m1_build_trait_inventory" src/snakemake/rules/m1_qc.smk && [ $(wc -l < src/R/qc/control_loci.csv) -ge 13 ] && quarto check src/R/qc/m1_qc_report.qmd 2>&1 \| grep -qi "ok\|pass\|version"` | ❌ W0 | ⬜ pending |
| m1-04-T2 | m1-04 | 4 | REQ-TRAIT-INVENTORY | — | data-pipeline integrity | integration | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/test_verify_m1_artifacts.py -x --tb=short 2>&1 \| tail -5 && test -f src/python/verify_m1_artifacts.py && test -f config/trait_inventory.yaml && test -f .planning/amendments/sha256_manifest_m1_frozen.tsv && test -f .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md && grep -q "Dimension-8 Acceptance Criteria" .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md && grep -q "Overall M1 Closeout Verdict" .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "import yaml; d = yaml.safe_load(open('config/trait_inventory.yaml')); assert 'traits' in d and len(d['traits']) >= 30"` | ❌ W0 | ⬜ pending |
| m1-04-T3 | m1-04 | 4 | REQ-OSF-PREREG (M2 gate) | — | N/A (manual OSF web-UI submission) | smoke | `test -f .planning/amendments/osf-amendment-m1-*.md && grep -q "M2 unblocked\|OSF amendment posted" .planning/STATE.md` | ❌ W0 | ⬜ pending |

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

- [x] All tasks have `<automated>` verify or Wave 0 dependencies declared
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (env YAMLs, chain file, fixture FTP/GWAS-Catalog probes, LDSC benchmark)
- [x] No `watch`-mode flags (LSF-hostile)
- [x] Feedback latency < 90 s unit / < 15 min full-smoke
- [x] All nine Dimension-8 criteria from RESEARCH.md §Validation Architecture have at least one mapped test
- [x] `nyquist_compliant: true` set in frontmatter after planner fills per-task verification map

**Approval:** planner-complete (2026-04-24); awaiting Wave 0 execution to flip `wave_0_complete: true`.
