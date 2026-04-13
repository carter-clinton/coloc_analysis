# Phase 5 Security Verification — Pathway + Partitioned Heritability

**Phase:** 05 — pathway-partitioned-heritability
**ASVS Level:** 1
**Block On:** critical, high
**Verified:** 2026-04-13
**Threats Verified:** 24 / 24 (closed)
**Open Threats:** 0
**Unregistered Flags:** 0

## Scope

Verifies that all 24 threats declared across plans 05-01 through 05-05 have
mitigations present in the implementation, or are documented as accepted /
transferred risks.

Trust boundaries (per plans):
- External HTTPS downloads of reference data (MAGMA, LDSC, HESS panels)
- Harmonized sumstats to tool-specific format conversion
- g:Profiler REST API (external service)
- MAGMA / LDSC / HESS subprocess invocation
- Cross-Python-version subprocess (Python 3 to Python 2.7 HESS)
- Curated gene sets committed to git

## Threat Verification — Closed (Mitigate)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-05-01 | Tampering (MAGMA binary download) | mitigate | `src/snakemake/rules/pathway.smk:65-88` — download_magma_binary includes file-size validation (>1 MB), wget --max-redirect=3 --timeout=300; T-05-01 comment on line 65. |
| T-05-02 | Tampering (LDSC baseline download) | mitigate | `src/snakemake/rules/pathway.smk:148-201` — download_ldsc_baseline includes FSIZE check > 1 GB (line 176); non-empty validation at line 138-144 for magma_ref. |
| T-05-03 | Tampering (HESS panel download) | mitigate | `src/snakemake/rules/pathway.smk:302-343` — download_hess_panel validates .bim file count (>= 22 expected) at line 338-341. |
| T-05-04 | Tampering (LDSC sumstats munging) | mitigate | `src/python/munge_sumstats_ldsc.py:43,94-98` — LDSC_COLS validation; rejects input missing required columns with explicit error message (T-05-04 comment on line 23-24). |
| T-05-05 | Injection (pathway.smk shell blocks) | mitigate | `src/snakemake/rules/pathway.smk:17` — T-05-05 declared; no `shell=True` found in any Python wrapper (grep across src/python); shell blocks use config-derived paths only. |
| T-05-06 | DoS (download rules) | mitigate | `src/snakemake/rules/pathway.smk:18` — wget --max-redirect=3 --timeout=300 present on all download rules (verified on lines 80, 122, 128, 134, 172, 183, 189, 195, 201, 227, 233, and --max-redirect=5 --timeout=600 for HESS lines 324, 330). |
| T-05-08 | Tampering (g:Profiler JSON response) | mitigate | `src/python/run_gprofiler.py:85-102` — `_validate_response()` requires `"result"` key; raises on malformed; HTTPS enforced via `GPROFILER_API_URL = "https://..."` (line 56). |
| T-05-10 | Injection (run_magma.py subprocess) | mitigate | `src/python/run_magma.py:38-56` — `_validate_file()` checks os.path.exists + non-empty; `_run_command()` uses list-arg `subprocess.run(cmd, ...)` (line 80); no shell=True. |
| T-05-11 | Info Disclosure (MAGMA pval temp file) | mitigate | `src/python/run_magma.py:155-184,330-346` — `_create_pval_file()` extracts only SNP+P columns into `tempfile.mkdtemp`; `finally` block at line 343 `shutil.rmtree(tmpdir)` with T-05-11 comment. |
| T-05-12 | DoS (g:Profiler rate limit) | mitigate | `src/python/run_gprofiler.py:60,201,245` — `RETRY_DELAYS = [2, 4, 8]` exponential backoff; 3 retry attempts with `time.sleep(delay)`; T-05-12 comment on line 15. |
| T-05-13 | Tampering (.ldcts file paths) | mitigate | `src/python/run_ldsc_seg.py:111-192` — `validate_ldcts_file()` + `fix_ldcts_paths()` rewrite/validate paths; `rule fix_ldcts_paths` at pathway.smk:924. |
| T-05-14 | Injection (run_ldsc_partitioned.py subprocess) | mitigate | `src/python/run_ldsc_partitioned.py:11,92-107` — list-arg `subprocess.run` in `_run_command()`; no shell=True; T-05-14 banner comment. |
| T-05-15 | DoS (LDSC memory) | mitigate | `src/snakemake/rules/pathway.smk:621,645,663,694` — `mem_mb=8000` resource directive on all LDSC rules; T-05-15 comment on line 621, 663. |
| T-05-16 | Tampering (munged sumstats) | mitigate | `src/python/run_ldsc_partitioned.py:61-62,247` — `MIN_MUNGED_SNPS = 500000`; post-munge SNP count warning (T-05-16 comment at line 17 and 247). |
| T-05-17 | Tampering (HESS LD panel build) | mitigate | `src/python/run_hess.py:67-150` — `validate_hess_panel_build()` checks SNP positions against hardcoded GRCh37 reference; `rule hess_validate_panel` exists in pathway.smk. |
| T-05-18 | Injection (run_hess.py subprocess) | mitigate | `src/python/run_hess.py:13,343,362,412` — list-arg subprocess.run; T-05-18 banner + inline comment "list args only, no shell=True" at line 343. |
| T-05-19 | Tampering (HESS sumstats format) | mitigate | `src/python/run_hess.py:217-255` — Z = BETA/SE computation; `math.isnan` rejection at line 225, 230; N-positivity check at line 254-255; T-05-19 comments throughout. |
| T-05-21 | Tampering (neg-ctrl validation) | mitigate | `src/python/extend_null_genesets.py:577-602` — `validate_negative_controls()` with `sys.exit(1)` hard fail at line 602 (T-05-21 comment); called from `rule validate_negative_controls` (pathway.smk:1753-1754). |
| T-05-22 | Repudiation (permutation seed) | mitigate | `src/python/extend_null_genesets.py:15,30,480-481,637-638` — deterministic `seed + perm_idx`; T-02-18 pattern; `--seed` default 42; seed logged in per-permutation summary row (line 539). |
| T-05-24 | Tampering (aggregate_pathway_results) | mitigate | `src/python/aggregate_pathway_results.py:14,44,47,77,108,137` — `_validate_columns()` helper rejects unexpected schema; T-05-24 module docstring + inline. |

## Threat Verification — Closed (Accept)

| Threat ID | Category | Disposition | Evidence |
|-----------|----------|-------------|----------|
| T-05-07 | Tampering (config/pipeline.yaml pathway section) | accept | Declared in 05-01-PLAN.md threat register. Config committed to git; pipeline.yaml not user-editable at runtime. Accepted risk: developer modifies config intentionally. No runtime enforcement needed. |
| T-05-09 | Spoofing (g:Profiler endpoint) | accept | Declared in 05-02-PLAN.md threat register. Using official academic URL `https://biit.cs.ut.ee/gprofiler/`; HTTPS enforced in `run_gprofiler.py:56`. LOW residual risk for academic service. |
| T-05-20 | DoS (HESS per-chromosome memory) | accept | Declared in 05-04-PLAN.md threat register. HESS requires ~4 GB per chromosome for eigendecomposition; documented via `mem_mb=4000` resource directives on HESS rules in pathway.smk. Expected cost, not exploitable. |
| T-05-23 | Info Disclosure (methods fragment) | accept | Declared in 05-05-PLAN.md threat register. `docs/methods/phase5_methods_fragment.md` documents software versions and parameters; this is an intentional publication disclosure, not a leak. |

## Accepted Risks Log

All four accepted-risk threats (T-05-07, T-05-09, T-05-20, T-05-23) are
explicitly declared with rationale in the corresponding PLAN.md threat
registers. No additional accepted risks discovered during implementation
verification.

## Unregistered Threat Flags

None. SUMMARY.md files for 05-01 through 05-05 contain no `## Threat Flags`
section. No new attack surface declared by the executor beyond the registered
threat model.

## Coverage Summary

| Plan | Threats Declared | Closed-mitigate | Closed-accept | Open |
|------|------------------|-----------------|---------------|------|
| 05-01 | 7 (T-05-01..07) | 6 | 1 (T-05-07) | 0 |
| 05-02 | 5 (T-05-08..12) | 4 | 1 (T-05-09) | 0 |
| 05-03 | 4 (T-05-13..16) | 4 | 0 | 0 |
| 05-04 | 4 (T-05-17..20) | 3 | 1 (T-05-20) | 0 |
| 05-05 | 4 (T-05-21..24) | 3 | 1 (T-05-23) | 0 |
| **Total** | **24** | **20** | **4** | **0** |

## Verdict

SECURED. All 24 threats for Phase 5 are closed (20 mitigated, 4 accepted).
No critical or high-severity gaps. No unregistered attack surface reported
by executors. Phase may proceed under block_on=critical,high gate.
