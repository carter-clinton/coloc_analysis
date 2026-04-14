---
phase: 09-replication-in-independent-cohorts
asvs_level: 1
block_on: high
verified_at: 2026-04-13
updated_at: 2026-04-14
verifier: gsd-secure-phase
threats_total: 22
threats_closed: 22
threats_open: 0
status: SECURED
amendment:
  date: 2026-04-14
  threat_id: T-09-01
  action: disposition_change
  from: mitigate
  to: accept
  reason: "Per user decision 2026-04-14 — HPC environment (NCSU NIH-tier) + open-public cohorts + HTTPS in-transit + schema/liftover QC together provide meaningful integrity guarantees that SHA256-at-first-download would not add. See Accepted Risks #4."
---

# Phase 9 — Security Verification Report

**Scope:** 22 threats across 5 plans (09-01…09-05). Each mitigation verified
against its declared pattern in the cited file. Code-review fixes from
`09-REVIEW-FIX.md` (iteration 1, 13/13 fixed) were cross-checked for CR-01
(zip-slip) and CR-02 (winnerscurse SHA pin).

---

## Verification Summary

| Disposition | Count | Verified |
|-------------|-------|----------|
| mitigate    | 18    | 18 closed |
| accept      | 4     | 4 closed (logged below) |
| transfer    | 0     | —                              |
| **Total**   | **22** | **22 closed / 0 open**        |

**Amendment 2026-04-14:** T-09-01 re-disposed from `mitigate` (SHA256 capture) to
`accept` (HPC + open-public cohorts + HTTPS + schema/liftover QC). See
Accepted Risks #4 below.

---

## Closed Threats (21)

### Plan 09-01 (Ingest + config + MVP inventory)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-09-02 | Tampering | mitigate | `tests/phase9/conftest.py:27` uses `yaml.safe_load`; `src/python/build_replication_manifest.py:184` same. `tests/phase9/test_cohort_ingest.py:14-17` validates required keys (`file_pattern`, `traits.t2d.endpoint`, etc.) |
| T-09-03 | Information Disclosure | accept | MVP phs001672 is open-access; no sample-level data, only URLs + citations in `config/replication_cohorts.yaml` + `mvp_phs001672_inventory.md`. (Accepted risk #1 below.) |
| T-09-04 | Validation | mitigate | `tests/phase9/test_cohort_ingest.py:16` asserts `cfg["traits"]["stroke"]["endpoint"] == "I9_STR_EXH"` (primary); `config/replication_cohorts.yaml:38` explicitly declares `sensitivity_endpoint: "I9_STR"` |
| T-09-11 | Denial of Service | accept | `tests/phase9/conftest.py` uses `tmp_path` mock fixtures; no live HTTP in test suite. (Accepted risk #2 below.) |

### Plan 09-02 (Harmonization)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-09-05 | Tampering | mitigate | `src/python/harmonize_finngen.py:73` / `harmonize_gbmi.py:85` / `harmonize_mvp.py:183` use `low_memory=False`. `harmonize_gbmi.py:101-106` raises on missing columns. `sumstats_utils.liftover_to_grch37` (line 246) raises `RuntimeError` when drop_rate > 5%. |
| T-09-06 | Integrity | mitigate | `src/python/sumstats_utils.py:204-252` `liftover_to_grch37` emits QC dict (n_input, n_lifted, n_dropped, drop_rate, n_dropped_unknown_chrom, n_dropped_liftover_failed) and raises `RuntimeError` at drop_rate > max_drop_rate=0.05. WR-07 bucketing adds unknown-chrom disambiguation. |
| T-09-08 | Validation | mitigate | `src/python/sumstats_utils.py:123-161` `filter_palindromic_ambiguous` drops A/T & C/G pairs where MAF ∈ [0.48, 0.52]. Called from each harmonizer (`harmonize_bbj.py:131`, etc.). |
| T-09-09 | Tampering | accept | All four download rules in `src/snakemake/rules/replication.smk` (lines 104-166) use `curl -fsSL <https://…>`; no secrets in URL patterns. (Accepted risk #3 below.) |
| T-09-10 | Integrity | mitigate | `src/python/harmonize_bbj.py:34-78` `extract_bbj_zip`: skips `readme` entries, restricts to `.tsv`/`.txt`. **CR-01 fix (commit 57bd450)** added per-entry resolved-path check — raises `ValueError` on zip-slip (CVE-2007-4559). |

### Plan 09-03 (Manifest + SuSiE fit)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-09-05 (manifest) | Validation | mitigate | `src/snakemake/rules/replication.smk:314-330` `_replication_manifest_row` + `_manifest_lookup` dispatch; Snakemake fails at rule-eval when `input:` paths (lines 368-394, 408-422) do not exist. `src/python/build_replication_manifest.py:201-205` enforces Tier A+B only. |
| T-09-12 | Tampering | mitigate | `src/snakemake/scripts/run_fiqt.R:35-46` pins `WINNERSCURSE_PINNED_SHA <- "2ed00bb"`; `remotes::install_github(..., ref = WINNERSCURSE_PINNED_SHA, upgrade = "never", quiet = TRUE)`. **CR-02 fix (commit 94bd5e3)** + envs/r_coloc.yml comment synchronised with `docs/methods/phase9_replication.md`. |
| T-09-13 | Validation | mitigate | `tests/phase9/test_replication_manifest.py:36` `test_tier_c_excluded`; `:81` `test_bbj_only_for_tier_ab`; `:142` `test_afr_never_finngen`. All three enforce D-02b / D-05. |
| T-09-14 | Integrity | mitigate | `src/snakemake/scripts/run_replication_susie.R:215-236` primary `coloc::runsusie` wrapped in `tryCatch`; on error retries with `min_abs_corr = 0.1` (Phase 1 precedent). |

### Plan 09-04 (coloc + Bonferroni + meta)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-09-15 | Validation | mitigate | `src/python/compute_per_cohort_effect_size_test.py:35-47` `compute_bonferroni` uses per-cohort `n_signals_in_cohort`; `tests/phase9/test_bonferroni.py:23-29` asserts `compute_bonferroni(20) == 0.0025`, `compute_bonferroni(100) == 0.0005`. |
| T-09-16 | Integrity | mitigate | `src/snakemake/scripts/run_replication_coloc_susie.R:61-75` `tryCatch` wraps `readRDS` + `coloc.susie`; JSON emits `coloc_succeeded=FALSE` with error message + sweep columns set to NA (lines 84-100). |
| T-09-17 | Validation | mitigate | `src/snakemake/scripts/aggregate_replication_meta.R:107-115` groups by `.(signal_id, cohort_ancestry)` so EUR/AFR never enter same meta row. `is_generalization=TRUE` (BBJ) excluded at lines 94-104. |
| T-09-18 | Validation | mitigate | `apply_fiqt` is defined only in `src/snakemake/scripts/run_fiqt.R:65`. Grep of entire `src/` confirms no call site passes `beta_replication` — `compute_per_cohort_effect_size_test.py` only reads `beta_discovery_FIQT` (lines 158, 167) as input for power calc, never re-computes FIQT on replication β. |

### Plan 09-05 (COJO + aggregation)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-09-07 | Validation | mitigate | `src/snakemake/scripts/run_cojo.sh:24` `set -euo pipefail`; lines 31-34 assign positional args to `MA`, `PLINK_PREFIX`, `LOCUS_SNPS`, `OUT_PREFIX`; all subsequent GCTA invocations (lines 61-67) double-quote each variable. No shell expansion of user input beyond quoted positional args. |
| T-09-19 | Compliance | mitigate | `docs/methods/phase9_replication.md:13-21` cites Zhou 2022 (GBMI), Kurki 2023 (FinnGen), Sakaue 2021 (BBJ); `:159-166` references block lists identical canonical citations + MVP phs001672 dbGaP. |
| T-09-20 | Validation | mitigate | `src/python/build_master_replication_table.py` consumes `data/processed/replication/manifest.tsv` as single source of truth; `build_replication_manifest.py:201-205` drops Tier C and enforces D-05 ancestry routing upstream — transitively inherited. |
| T-09-21 | Integrity | mitigate | `tests/phase9/test_negative_controls.py:21-59` `test_hla_fails_replication_joint` — asserts `(n_fail >= 3).mean() > 0.7` on HLA 6:28-33Mb rows. **WR-11 fix (commit 94333af)** hardened gate via `has_any_real` precondition so all-NaN joint matrices xfail instead of trivially passing. |
| T-09-22 | Validation | mitigate | `src/snakemake/scripts/run_cojo.sh:49-52` emits `WARN: LD reference … has N=${N_SAMPLES} (< 4000 GCTA threshold). COJO results are TIER-2 SENSITIVITY per RESEARCH §6 Option D / gotcha #1.` to stderr. `docs/methods/phase9_replication.md` methods block embeds the caveat. |

---

## Open Threats (0)

None. T-09-01 re-disposed to `accept` on 2026-04-14 — see Accepted Risk #4 below.

---

## Accepted Risks (logged per disposition)

1. **T-09-03 — MVP phs001672 dbGaP inventory (Info Disclosure).**
   Justification: phs001672 is an **open-access** dbGaP study (no DAR); all
   metadata captured in `mvp_phs001672_inventory.md` consists of pha IDs,
   trait codes, citations, and public URLs — no sample-level genotypes or
   phenotypes. Accepted per project constraint "100% public data".
   Review cadence: re-verify on Phase 11 manuscript-prep if MVP changes
   access tier.

2. **T-09-11 — Repeated portal hits during testing (Denial of Service).**
   Justification: The Phase 9 pytest suite uses `tmp_path` mock fixtures
   (see `tests/phase9/conftest.py`) + local `tests/phase9/fixtures/*.rds`.
   No test shell-invokes `curl`/`wget`. Live downloads only occur via the
   Snakemake `download_*` rules during pipeline execution, not in CI.
   Accepted; review if CI ever gains a live-smoke step.

3. **T-09-09 — Subprocess curl/wget invocation (Tampering).**
   Justification: All four download rules use `curl -fsSL <https://…>`;
   URLs sourced from `config/replication_cohorts.yaml` (version-controlled
   + safe_load-parsed); no secrets in URL query strings; no shell
   interpolation of user input beyond config-loaded constants. HTTPS
   provides in-transit integrity. Accepted; schema gate catches post-
   download corruption.

4. **T-09-01 — Cohort download integrity (Tampering).** [Amended 2026-04-14]
   Original disposition `mitigate` called for SHA256 checksum capture on
   first download per cohort. Re-disposed to `accept` after analysis.
   Justification:
   - **HPC environment.** Project runs on NCSU HPC with NIH-tier security
     controls. At-rest tampering of downloaded files is not a realistic
     threat within this environment.
   - **Open-public cohort sources.** FinnGen R12 (GCP bucket), GBMI (portal),
     MVP phs001672 (dbGaP FTP), BBJ hum0197-v3 (NBDC) all serve over HTTPS
     from established academic/government endpoints. In-transit integrity
     is provided by TLS (transitively addressed by accepted T-09-09).
   - **No canonical hash available.** None of the 4 cohort providers publish
     SHA256 digests on a separate channel, so a locally-captured hash would
     only record what we downloaded — not verify against an independent
     truth. SHA256-at-first-download in this setting is security theater.
   - **Schema + liftover QC remain in place.** Tampering that breaks the
     10-column canonical schema (`validate_replication_sumstats.py:25-37`)
     or coordinate plausibility (`sumstats_utils.liftover_to_grch37`
     drop_rate > 5% triggers `RuntimeError`) would be caught. Subtle
     β-perturbation attacks are the residual risk and are not meaningful
     under this threat model.
   - **Reviewer-facing provenance.** The manuscript cites Kurki 2023 (FinnGen),
     Zhou 2022 (GBMI), Sakaue 2021 (BBJ), and phs001672 (MVP). Any reviewer
     can independently re-download and compare.

   Accepted per user decision 2026-04-14 ("HPC is as secure as NIH").
   Review cadence: re-verify if any cohort moves to a controlled-access
   tier or if providers begin publishing canonical hashes.

---

## Unregistered Threat Flags

None. SUMMARY.md files for Plans 09-01 through 09-05 do not contain a
`## Threat Flags` section, so no out-of-band flags required reconciliation.

---

## Code-Review-Fix Cross-Checks

The code-review-fix iteration (`09-REVIEW-FIX.md`, 2026-04-14T10:28Z,
13/13 findings fixed) was re-verified in-line for threats it transitively
touches:

- **CR-01 (zip-slip)** → T-09-10 closed: `harmonize_bbj.py:68-77` now
  performs per-entry `target.resolve()` + prefix check.
- **CR-02 (winnerscurse SHA pin)** → T-09-12 closed: `run_fiqt.R:35` pins
  SHA `2ed00bb`; `envs/r_coloc.yml` comment + methods doc synchronised.
- **WR-11 (negative-control silent pass)** → T-09-21 closed: all-NaN
  joint matrices now xfail instead of trivially passing.
- **WR-10 (process_cohort duplicates)** → strengthens T-09-15 by catching
  upstream regressions that would inflate replication rates.
- **WR-07 (liftover drop buckets)** → strengthens T-09-06 by
  disambiguating "unknown chromosome label" from genuine liftover failure
  in QC JSON.

All five cross-checks confirm the code-review-fix iteration preserved or
strengthened the declared mitigations.

---

## Verdict

**Status:** `SECURED` (22/22 threats closed — 18 mitigated, 4 accepted).

**Blocks phase completion:** NO.

**Audit trail:**
- 2026-04-13 initial audit: 21 closed + 1 open (T-09-01 Medium).
- 2026-04-14 amendment: T-09-01 re-disposed `mitigate` → `accept` per user
  decision citing HPC security tier + open-public cohort provenance.
  See Accepted Risk #4 for full justification.

**Review cadence:**
- T-09-03 / T-09-11 / T-09-09 / T-09-01: re-verify at Phase 11
  manuscript-prep if any cohort changes access tier, or if providers
  begin publishing canonical SHA256 digests.
