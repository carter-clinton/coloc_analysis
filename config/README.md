# config/

Pipeline configuration. Everything here is committed.

| File (planned) | Purpose |
|---|---|
| `pipeline.yaml` | Top-level Snakemake config (paths, cluster profile, trait/ancestry lists) |
| `data_sources.yaml` | Registry of upstream sumstats / QTL / cohort sources (DOI, license, DUA status) |
| `traits.yaml` | 5 trait definitions: BMI, T2D, hypertension, stroke, asthma |
| `ancestries.yaml` | Ancestry labels, LD reference paths, LDSC weights, 1000G / HGDP mappings |
| `regions.tsv` | 50 pleiotropic loci (chr, start, end, lead variant, source) |
| `coloc_priors.yaml` | `p12` sensitivity sweep: `{1e-6, 1e-5, 1e-4}` (REQ-1 in REQUIREMENTS.md) |
| `pph4_thresholds.yaml` | PP.H4 sweep for tier assignment: `{0.5, 0.7, 0.8, 0.9}` (REQ-3) |
| `susie_policy.yaml` | SuSiE `L`, `min_abs_corr`, convergence/failure rules for complex regions (REQ-2) |
| `negative_controls.yaml` | HLA / pigmentation / eye-color gene + pathway sets (REQ-7) |

New config files must round-trip through the Snakemake schema validator
under `src/snakemake/schemas/` before being used by a rule.
