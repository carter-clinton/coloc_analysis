# Phase 02 Security Audit: 3-Way QTL Colocalization

**Auditor:** GSD Security Auditor
**Date:** 2026-04-12
**Phase:** 02 -- 3-Way QTL Colocalization
**Plans audited:** 02-01 through 02-05
**Total threats:** 18
**Closed:** 18/18
**Open:** 0/18

## Threat Verification

| Threat ID | Category | Component | Disposition | Evidence |
|-----------|----------|-----------|-------------|----------|
| T-02-01 | Tampering | hg19ToHg38.over.chain.gz | mitigate | `src/python/liftover_regions.py:32` defines `MIN_CHAIN_SIZE = 100_000`; line 42 raises RuntimeError if `size < MIN_CHAIN_SIZE`; docstring line 9 documents expected md5 reference |
| T-02-02 | Tampering | config/*.yaml | mitigate | All 7 YAML load sites use `yaml.safe_load()` (harmonize_eqtl.py:252, harmonize_sqtl.py:185, harmonize_pqtl.py:307, harmonize_onek1k.py:300, sample_null_loci.py:274+456, assign_tiers.py:242); zero `yaml.load()` calls found; `tests/phase2/test_config_validation.py` exists for schema validation |
| T-02-03 | Information Disclosure | envs/qtl_processing.yml | accept | Accepted risk: conda env spec contains only public package names, no secrets. Logged here per disposition. |
| T-02-04 | Tampering | eQTL Catalogue downloaded files | mitigate | `src/snakemake/rules/qtl_download.smk:61-70` validates `[ ! -s {output.tsv} ]` and `[ ! -s {output.tbi} ]` after download with `exit 1` on empty; same pattern repeated for sQTL at lines 159-169 |
| T-02-05 | Tampering | qtl_coloc_manifest.tsv | mitigate | `src/snakemake/rules/qtl_coloc.smk:25-26` sets `wildcard_constraints: qtl_coloc_id=r"[A-Za-z0-9_.\-]+"` preventing path traversal |
| T-02-06 | DoS | eQTL Catalogue FTP rate limiting | mitigate | `src/snakemake/rules/qtl_download.smk:34-71` rule `download_eqtl_catalogue` downloads full files locally via wget; no remote tabix calls in the pipeline; `harmonize_eqtl.py:168-179` uses local pysam TabixFile with pandas fallback |
| T-02-07 | Tampering | run_qtl_coloc.R QTL input | mitigate | `src/snakemake/scripts/run_qtl_coloc.R:195` calls `coloc::check_dataset(qtl_data, req = "LD")`; lines 144 and 164 enforce `n_snps_overlap < 50` guard with early exit |
| T-02-08 | Information Disclosure | Synapse auth token | mitigate | `src/python/download_ukbppp.py:56` reads token via `os.environ.get("SYNAPSE_AUTH_TOKEN")`; no hardcoded tokens in file; `.gitignore:127` contains `.synapseConfig` entry |
| T-02-09 | Tampering | UKB-PPP REGENIE column schema | mitigate | `src/python/harmonize_pqtl.py:48-58` defines `REQUIRED_REGENIE_COLUMNS` set; lines 132-137 compute `missing_cols` and raise `ValueError` if schema mismatch |
| T-02-10 | DoS | UKB-PPP bulk download disk usage | mitigate | `src/python/download_ukbppp.py:72-78` pre-checks disk space via `os.statvfs()` with warning at <1 GB; `src/snakemake/rules/qtl_download.smk:226` downloads per-protein per-chromosome (not bulk tar) |
| T-02-11 | Tampering | sQTL molecular_trait_id format | accept | Accepted risk: splice junction IDs are pass-through from eQTL Catalogue; no security impact from malformed IDs. Logged here per disposition. |
| T-02-12 | Spoofing | OneK1K data source selection | mitigate | `src/python/download_onek1k.py:243-253` attempts eQTL Catalogue first, falls back to onek1k.org only on failure; `src/python/harmonize_onek1k.py:91-108` logs source format used via `logger.info()` |
| T-02-13 | Tampering | OneK1K downloaded files | mitigate | `src/python/download_onek1k.py:142-148` validates file exists and `os.path.getsize() == 0` check; `src/python/harmonize_onek1k.py:78-84` validates input file existence and non-empty size; `src/snakemake/rules/qtl_download.smk:316-321` validates `[ ! -s {output.tsv} ]` after download |
| T-02-14 | DoS | onek1k.org S3 latency | accept | Accepted risk: onek1k.org S3 is a fallback source only; latency is not a security concern; download-once-cache pattern in download_onek1k.py. Logged here per disposition. |
| T-02-15 | Tampering | Open Targets L2G Parquet files | mitigate | `src/python/parse_l2g.py:4` documents version pin to v26.03; lines 77-81 validate schema (`required_cols = {"studyLocusId", "geneId", "score"}`) and raise `ValueError` if columns missing |
| T-02-16 | Repudiation | Tier assignment reproducibility | mitigate | `src/python/assign_tiers.py:137-139` loads `primary_threshold` and `tier_b_min` from `pph4_config` dict (loaded from YAML); `sweep_tiers()` at line 61 accepts `sweep_values` parameter from config; no hardcoded threshold constants in tier logic |
| T-02-17 | Information Disclosure | Methods fragment | accept | Accepted risk: methods fragment is intended for publication; no sensitive data. Logged here per disposition. |
| T-02-18 | Tampering | bedtools shuffle seed | mitigate | `src/python/sample_null_loci.py:107` reads `seed_base` from config; line 177 computes `seed = seed_base + draw_id`; line 215 writes seed to `null_loci_summary.tsv` output |

## Accepted Risks Log

| Threat ID | Category | Component | Rationale |
|-----------|----------|-----------|-----------|
| T-02-03 | Information Disclosure | envs/qtl_processing.yml | No secrets in conda env spec; contains only public package names |
| T-02-11 | Tampering | sQTL molecular_trait_id format | Splice junction IDs are pass-through from eQTL Catalogue; no security impact |
| T-02-14 | DoS | onek1k.org S3 latency | Fallback source only; download-once-cache pattern mitigates repeated access |
| T-02-17 | Information Disclosure | Methods fragment | Content is intended for publication; contains no sensitive data |

## Unregistered Flags

None. No `## Threat Flags` sections found in any SUMMARY.md files (02-01 through 02-05).

## Summary

All 18 registered threats verified: 14 mitigated (evidence confirmed in implementation), 4 accepted (documented above). Zero open threats. Phase 02 security posture is complete.
