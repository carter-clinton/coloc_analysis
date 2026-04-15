---
phase: 05
slug: pathway-partitioned-heritability
status: verified
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
last_audited: 2026-04-15
---

# Phase 05 — Validation Strategy

> Per-phase validation contract. Retroactive audit 2026-04-15 reconciled the
> draft map with implementation reality and the 10 issues surfaced by the
> bmi.EUR magma_fdr scout (`.planning/quick/260414-bmi-magma-scout/`).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (in smoke_dev) + Rscript (in r_coloc) |
| **Config file** | `tests/phase5/conftest.py` (project-local fixtures for gmt, sumstats, reference-data mocks) |
| **Quick run command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -x -q` |
| **Full suite command** | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/phase5/ -v` |
| **Current status** | **100 passed in 53.2s** (2026-04-15 audit run) |
| **Estimated runtime** | ~55 seconds (all unit/smoke); integration requires real conda + real data (see Manual-Only) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/phase5/ -x -q --tb=short`
- **After every plan wave:** Run `pytest tests/phase5/ -v`
- **Before `/gsd-verify-work`:** Full suite green + Snakemake dry-run of `pathway.smk`
- **Max feedback latency:** 55 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | REQ-7 | T-05-01 | Neg-ctrl GMT includes required sets | unit | `pytest tests/phase5/test_magma_geneset.py::TestNegCtrlGMT -x` | ✅ | ✅ green |
| 05-01-02 | 01 | 1 | SC-1 | — | MAGMA gene-set infra (custom GMT, effective-N, pval-file format, annotate cmd) | smoke | `pytest tests/phase5/test_magma_geneset.py -x` | ✅ | ✅ green |
| 05-02-01 | 02 | 1 | REQ-7 | T-05-02 | g:Profiler API over HTTPS + negative-ctrl rule wired | unit | `pytest tests/phase5/test_negative_controls.py::TestAllMethodsHaveNegCtrl::test_gprofiler_neg_ctrl_rule -x` | ✅ | ✅ green |
| 05-02-02 | 02 | 1 | SC-2 | — | g:Profiler discoverability-matched background + request schema | smoke | `pytest tests/phase5/test_gprofiler.py -x` | ✅ | ✅ green |
| 05-03-01 | 03 | 2 | SC-3 | T-05-03 | LDSC annotation format validation | unit | `pytest tests/phase5/test_ldsc_partitioned.py -x` | ✅ | ✅ green |
| 05-03-02 | 03 | 2 | SC-4 | — | LDSC-SEG tissue-specific h2 (path, ldcts format, shared tissues, --h2-cts flag, no shell=True) | smoke | `pytest tests/phase5/test_ldsc_seg.py -x` | ✅ | ✅ green |
| 05-04-01 | 04 | 3 | REQ-7 | T-05-18 | HESS: no shell=True (AST-checked); trait pair generation with shared-ancestry filter | unit | `pytest tests/phase5/test_hess.py -x` | ✅ | ✅ green |
| 05-04-02 | 04 | 3 | SC-3 | T-05-17 | HESS: GRCh37 build validation via reference SNP positions | unit | `pytest tests/phase5/test_hess.py::test_validate_panel_build -x` | ✅ | ✅ green |
| 05-05-01 | 05 | 4 | REQ-7 | — | All 5 methods have neg-ctrl rule + threshold validation | integration | `pytest tests/phase5/test_negative_controls.py -x` | ✅ | ✅ green |
| 05-05-02 | 05 | 4 | SC-5/SC-6 | — | Permutation null: matched-N gene sets (length, LD, MAF) with deterministic seed | smoke | `pytest tests/phase5/test_permutation_null.py -x` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All Wave 0 items landed during Plan 05-01 Wave 1 execution (commit history shows the `tests/phase5/` tree created with `01-PLAN.md`). `test_hess.py` was added during Plan 05-04. Reconciled 2026-04-15:

- [x] `tests/phase5/` directory
- [x] `tests/phase5/conftest.py` — shared fixtures
- [x] `tests/phase5/test_magma_geneset.py`
- [x] `tests/phase5/test_ldsc_partitioned.py`
- [x] `tests/phase5/test_gprofiler.py`
- [x] `tests/phase5/test_ldsc_seg.py`
- [x] `tests/phase5/test_negative_controls.py`
- [x] `tests/phase5/test_permutation_null.py`
- [x] `tests/phase5/test_hess.py` *(added Plan 05-04, not in original draft map)*
- [x] `envs/magma.yml`
- [x] `envs/ldsc_py3.yml`
- [x] `envs/hess_py27.yml`
- [x] `envs/gprofiler.yml`
- [x] `envs/python_stats.yml`

---

## Manual-Only Verifications

Expanded 2026-04-15 with the 10 issues surfaced by the bmi.EUR `magma_fdr` scout (see `.planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md`). These are deployment/environment/network concerns that unit tests cannot cover by construction — they require real conda + real data + real upstream APIs.

### Upstream-external (require network / third-party state)

| # | Behavior | Requirement | Why Manual | Test Instructions |
|---|----------|-------------|------------|-------------------|
| 1 | MAGMA binary download from CNCR | SC-1 | JS-gated portal; 301/404 possible; not scriptable without browser | Visit `ctg.cncr.nl/software/magma` in browser, confirm v1.10 Linux binary present; verify with `bin/setup-envs.sh` + `snakemake download_magma_binary` |
| 2 | HESS LD reference panel genome build | SC-3 | Must inspect downloaded panel header | Download panel, verify `rs1 chr1:779322` (GRCh37) — test_hess::test_validate_panel_build encodes the check; manually confirm panel matches |
| 3 | g:Profiler API live availability | SC-2 | External service dependency | `curl -s https://biit.cs.ut.ee/gprofiler/api/util/version` returns 200 + version JSON |
| 4 | msigdbr R package API + content | SC-1 | Package API changed 7.5→10.0→26.1; KEGG split into LEGACY/MEDICUS. Scout issue #8, closed by quick 260414-uqf. | Activate `gprofiler_r` env; `Rscript -e 'library(msigdbr); msigdbr(collection="C2", subcollection="CP:KEGG_LEGACY")'` returns non-empty df |
| 5 | Yengo 2018 BMI sumstats URL (cnsgenomics.com) | REQ-7 | Server throttles after repeated fetches; health fluctuates. Scout issue #9, functionally closed by quick 260414-v4r (mtime-touch on pre-staged bgz). | `curl -sI https://cnsgenomics.com/ukb-bmi/bmi.giant-ukbb.meta-analysis.combined.23May2018.txt.gz` → 200 OK; if 403/throttled, use v4r mtime-touch workaround |

### Environment-construction (require real conda create + real `--use-conda`)

| # | Behavior | Requirement | Why Manual | Test Instructions |
|---|----------|-------------|------------|-------------------|
| 6 | conda env creation reaches working prefix | REQ-9 | mamba 2.5 + snakemake 7.32.4 interop bug aborts creation even with correct yaml. Scout issue #4. | Run `bin/setup-envs.sh all_pathway`; verify `.snakemake/conda/<hash>_/conda-meta/` populated for each env yaml |
| 7 | No Anaconda ToS interactive prompt blocks CI | REQ-9 | `defaults` channel triggers Y/n prompt under mamba 2.5. Scout issue #5. | Fresh-host `bin/setup-envs.sh` succeeds non-interactively for all envs **except** `hess_py27` (one-time Y needed — Py2.7 EOL on `defaults` only). Mitigated by quick 260414-wzy dropping `defaults` from 6 yamls. |
| 8 | Script paths resolve inside project root under `--use-conda` | REQ-12 | `workflow.basedir` + n-level `..` constructions silently escape project root; surfaces only on real activation (not dry-run). Scout issues #1/#2, closed by quick 260414-rbv + 260414-tmq. | `snakemake --use-conda --cores 1 <target>` activates an env and runs the script; verify stderr path resolves under project root |
| 9 | In-place env augmentation hash drift | REQ-9 | Editing a yaml changes snakemake's hash → old `mamba install`-augmented prefix is abandoned. Scout issue #7. | Convention (envs/README.md): never `mamba install` into `.snakemake/conda/*_`; edit yaml + rerun `bin/setup-envs.sh` |

### Data-schema compatibility (require real sumstats)

| # | Behavior | Requirement | Why Manual | Test Instructions |
|---|----------|-------------|------------|-------------------|
| 10 | Column alias acceptance in `run_magma.py` | REQ-7 | Harmonized sumstats use `SNP_ID`; MAGMA wrapper historically required `SNP`. Scout issue #10, closed by quick 260414-vro. | Point `run_magma.py` at real harmonized bgz (e.g. `data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz`); `magma_gene_analysis` produces `.genes.raw` |

---

## Scout-proof artifacts (end-to-end on real data)

Recorded 2026-04-15. Demonstrates the MAGMA branch has passed every Manual-Only check above (items 1, 2, 4, 5, 6, 7, 8, 10):

| Artifact | Size | Provenance |
|---|---|---|
| `results/pathway/magma/gene_annotation.genes.annot` | 103 MB | scout v6 (2026-04-14 21:54) — magma_annotate on real 1000G EUR + NCBI37.3 |
| `results/pathway/magma/bmi_EUR.genes.raw` | 9.1 MB | scout v9 (2026-04-14 23:39) |
| `results/pathway/magma/bmi_EUR_geneset.gsa.out` | 1.4 MB | scout v9 (2026-04-14 23:40) |
| `results/pathway/magma/bmi_EUR_geneset_fdr.tsv` | 1.3 MB, 9617 rows, 194 FDR<0.05, top hit CUSTOM_APPETITE_REGULATION q=7.25e-11 | scout v9 (2026-04-14 23:40) |

**Branches still requiring scout coverage on real data:** g:Profiler, LDSC partitioned h², LDSC-SEG, HESS. Queued as follow-on work at Step 5 in STATE.md next-session moves.

---

## Validation Sign-Off

- [x] All tasks have automated verify or Manual-Only justification
- [x] Sampling continuity: 0 tasks without automated verify (all 10 map to pytest classes)
- [x] Wave 0 covers all missing test files (Plan 05-01 Task 3 + Plan 05-04)
- [x] No watch-mode flags
- [x] Feedback latency 55s < target threshold
- [x] `nyquist_compliant: true` — automated pytest suite covers all 10 requirement-task pairs
- [x] Integration concerns (items 1–10 in Manual-Only) explicitly documented with test-instruction blocks
- [x] MAGMA branch scout-proofed on real data (commits `7a3aa5a` (vro) + `7f97a20` (ww3))

**Approval:** 2026-04-13 draft → 2026-04-15 verified. Retroactive audit reconciled 8→10 task rows (HESS split into 05-04-01/02 + Plan 05-05 renumbered to 05-05-01/02) and expanded Manual-Only from 3→10 items with concrete reproduction steps keyed to scout issues.

---

## Validation Audit 2026-04-15

| Metric | Count |
|--------|-------|
| Tasks in draft map | 8 |
| Tasks in audited map | 10 (added HESS 05-04-01/02; Plan 05-05 split) |
| File-Exists ❌ → ✅ | 8 (all Wave 0 items landed) |
| Status ⬜ → ✅ | 10 |
| Manual-Only rows | 3 → 10 (+7 scout-surfaced integration items) |
| New tests needed | 0 (100/100 green in 53.2s) |
| Gaps escalated | 0 |
| Compliance verdict | **nyquist_compliant: true** |
