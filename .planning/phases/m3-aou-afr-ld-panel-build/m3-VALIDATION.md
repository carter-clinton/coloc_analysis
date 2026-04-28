---
phase: m3
slug: m3-aou-afr-ld-panel-build
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-27
---

# Phase M3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Sourced from `m3-RESEARCH.md` § "Validation Architecture" (lines 485-565); the 4-check protocol formalizes REQ-AOU-LD-VALIDATION per `AOU-LD-PIPELINE.md` §9.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x for AoU driver + manifest + resolver unit tests; Snakemake 7.32.4 for end-to-end DAG validation; R `testthat` for `ld_npz_to_rds.R` |
| **Config file** | `pyproject.toml` (root) for pytest; existing top-level `Snakefile` for Snakemake; `tests/m3/conftest.py` (NEW — Wave 0) for shared fixtures |
| **Quick run command** | `pytest tests/m3 -x --tb=short` |
| **Full suite command** | `pytest tests/m3 && snakemake --snakefile Snakefile --cores 4 --use-conda --dry-run m3_dev_complete` |
| **Estimated runtime** | ~30s pytest (synthetic MT); ~2 min Snakemake dry-run; phase gate `m3_dev_complete.flag` is human-touched only after Carter signoff per D-M3-03 |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/m3 -x --tb=short`
- **After every plan wave:** Run `pytest tests/m3 && snakemake --snakefile Snakefile --cores 4 --use-conda --dry-run m3_dev_complete`
- **Before `/gsd-verify-work` (phase gate M3 → M4):** Full suite green + `m3_dev_complete.flag` exists + Carter signoff committed in `m3-VALIDATION.md` (the validation memo, not this strategy doc)
- **Max feedback latency:** ~30 seconds per task commit; ~2 minutes per wave merge

---

## Per-Task Verification Map

> Plan-level task IDs are filled in by the planner during Wave-by-Wave plan emission. The columns below pin the **requirement → check → automated command** triples that planner tasks must satisfy. Format: `m3-{wave}-{plan}-{task}`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| m3-W0-* | 00-* | 0 | REQ-PATH-PARAMETERIZATION | — | `ld_panel:` resolver returns expected path under all chains | unit | `pytest tests/m3/test_ld_panel_resolver.py` | ❌ W0 | ⬜ pending |
| m3-W0-* | 00-* | 0 | REQ-AOU-LD-EGRESS (manifest) | T-M3-S1 | Region manifest schema = AOU §6 (322 rows, GRCh38 liftover, per-region radius) | unit | `pytest tests/m3/test_build_ld_region_manifest.py` | ❌ W0 | ⬜ pending |
| m3-W0-* | 00-* | 0 | REQ-PUBLIC-DATA-ONLY | T-M3-EGR | AoU env scaffolding does not exfiltrate individual-level data | unit | `pytest tests/m3/test_aou_ld_panel_local.py` (synthetic MT only) | ❌ W0 | ⬜ pending |
| m3-W1-* | 01-* | 1 | REQ-AOU-LD-EGRESS (cohort) | T-M3-EGR | AoU cohort definition emits two MTs (PCA + sensitivity); kinship-pruned | integration | `pytest tests/m3/test_aou_ld_panel_local.py -k cohort` | ❌ W0 | ⬜ pending |
| m3-W2-* | 02-* | 2 | REQ-AOU-LD-VALIDATION C1 | — | Known-locus LD pattern matches published (FTO + SORT1) | manual + auto | `pytest tests/m3/test_validation_check_1_known_locus.py` + visual review | ❌ W4 | ⬜ pending |
| m3-W2-* | 02-* | 2 | REQ-AOU-LD-VALIDATION C2 | — | AoU EUR vs 1000G EUR Pearson r ≥ 0.97 for MAF ≥ 0.05 | unit | `pytest tests/m3/test_validation_check_2_aou_eur_vs_1kg.py` | ❌ W4 | ⬜ pending |
| m3-W2-* | 02-* | 2 | REQ-AOU-LD-VALIDATION C3 | — | SuSiE-RSS converges on 16q12 BMI AFR; ≥1 CS @ 0.95; median CS ≤ 30; lead PIP ≥ 0.1 | integration | `pytest tests/m3/test_validation_check_3_susie_convergence.py` | ❌ W4 | ⬜ pending |
| m3-W2-* | 02-* | 2 | REQ-AOU-LD-VALIDATION C4 | — | AoU-AFR vs identity-placeholder A/B yield contrast tabulated | unit + integ | `pytest tests/m3/test_validation_check_4_identity_ab.py` | ❌ W4 | ⬜ pending |
| m3-W3-* | 03-* | 3 | REQ-AOU-LD-EGRESS (.rds) | T-M3-S2 | `.npz → .rds` round-trip preserves symmetry + dimnames | unit | `pytest tests/m3/test_ld_npz_to_rds.py` | ❌ W3 | ⬜ pending |
| m3-W3-* | 03-* | 3 | REQ-PATH-PARAMETERIZATION | — | `ld_panel:` resolver wired into `finemap.smk` against M4 fine-mapping rule | integ | `snakemake --use-conda --dry-run results/finemap/dummy_region.rds` | ❌ W3 | ⬜ pending |
| m3-W4-* | 04-* | 4 | REQ-AOU-LD-EGRESS (export) | T-M3-EGR | Per-chromosome export bundle landing schema verified (44 entries) | integ | `pytest tests/m3/test_aou_export_landing.py` | ❌ W4 | ⬜ pending |
| m3-W5-* | 05-* | 5 | REQ-PUBLIC-DATA-ONLY | T-M3-EGR | OSF posting confirms summary-only artifacts; egress audit log finalized | manual | Wave 5 OSF deposit + Carter signoff | governance | ⬜ pending |
| m3-W5-* | 05-* | 5 | REQ-SNAKEMAKE-CI | — | Toy 3-locus pipeline includes AFR identity-placeholder LD | integ | `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda` | ❌ W5 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

These test artifacts must be created in Wave 0 before any downstream wave fires:

- [ ] `tests/m3/conftest.py` — shared fixtures (synthetic MT loader, region manifest factory, mock AoU env vars)
- [ ] `tests/m3/test_build_ld_region_manifest.py` — Q1 + Q2 reformatter (GRCh37→GRCh38 liftover + per-region radius)
- [ ] `tests/m3/test_ld_panel_resolver.py` — Q7 resolver fallback chain (AFR_aou → AFR_hgdp_1kg → AFR_1kg; EUR_1kg → EUR_aou; `pin:` override; `strict_aou_only` mode)
- [ ] `tests/m3/test_aou_ld_panel_local.py` — Q6 Hail driver runs against synthetic MT (no AoU access)
- [ ] `tests/m3/fixtures/build_synthetic_mt.py` — generates `synthetic_aou.mt` via `hl.balding_nichols_model` (~100 samples × ~1000 variants × 2 chromosomes)
- [ ] Framework install: `envs/m3-aou-dev.yml` includes pytest 8.x + Hail 0.2.x; `envs/m3-r-ld.yml` includes `testthat`

Wave 3 / Wave 4 / Wave 5 follow-up artifacts (created in their own waves):

- [ ] `tests/m3/test_ld_npz_to_rds.py` — Wave 3
- [ ] `tests/m3/test_validation_check_1_known_locus.py` — Wave 4
- [ ] `tests/m3/test_validation_check_2_aou_eur_vs_1kg.py` — Wave 4
- [ ] `tests/m3/test_validation_check_3_susie_convergence.py` — Wave 4
- [ ] `tests/m3/test_validation_check_4_identity_ab.py` — Wave 4
- [ ] `tests/m3/test_aou_export_landing.py` — Wave 4

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| AoU egress classification of variant×variant LD matrices in writing | REQ-AOU-LD-EGRESS | Hard human gate per Risk R1; AoU support ticket return is opaque to automated tests | Submit AoU support request citing AOU-LD-PIPELINE.md §13 framing; archive ruling email to `.planning/amendments/aou-egress-classification-ruling.eml`; commit |
| AoU workspace creation + DUS + RPS + billing + P&P draft | REQ-AOU-LD-EGRESS | Carter portal action; AOU-LD-PIPELINE.md §2 P1-P7 | Paste `AOU-WORKBENCH-REGISTRATION.md` into AoU portal; capture screenshots; commit timestamps to `.planning/amendments/aou-egress-audit-log.md` |
| Carter signoff on Check 1 known-locus heatmap visual review | REQ-AOU-LD-VALIDATION C1 | LD-block-boundary visual comparison vs published figures requires expert eye | Carter compares `validation/check_1_known_locus_heatmaps/{region_id}.png` against Locke 2015 / Teslovich 2010 / PAGE 2017 panels; signoff committed in `m3-VALIDATION.md` (memo) |
| Carter signoff transitioning Wave 2 → Wave 4 (dev → production) | REQ-AOU-LD-VALIDATION | Single-fire-after-dev gate per D-M3-03; explicit human checkpoint | After all 4 checks pass, Carter touches `m3_dev_complete.flag`; commit with `(${padded_phase}-dev-complete)` token |
| Open Issue O1 — region width vs fine-mapping unit | REQ-AOU-LD-EGRESS | Carter must rule on Path A.1/A.2/A.3 acceptance vs region re-merge to ≤10 Mb tiles before Wave 0 commits | Wave 0 task surfaces the 161-region span distribution + per-class compute-cost projection; Carter accepts or directs re-merge; ruling logged in `m3-CONTEXT.md` as D-M3-09 |
| OSF posting of `m3-VALIDATION.md` (memo) to osf.io/az52u | REQ-PUBLIC-DATA-ONLY | Carter portal action; OSF supplementary file upload | Wave 5 emits paste-ready PDF; Carter posts to osf.io/az52u as supplementary file; DOI captured in egress audit log entry |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (synthetic MT fixture, conftest, manifest test, resolver test)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s per task commit
- [ ] `nyquist_compliant: true` set in frontmatter (post Wave 0 fixture commit)

**Approval:** pending (Wave 0 will flip `nyquist_compliant: true` once `tests/m3/conftest.py` + 3 unit-test stubs land)
