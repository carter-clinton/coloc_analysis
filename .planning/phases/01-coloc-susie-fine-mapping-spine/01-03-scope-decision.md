# 01-03 AFR LD scope decision -- 2026-04-11

Plan 01-03 (HGDP+1kG AFR LD panel via gnomAD v3.1.2 phased BCFs) requires an
explicit scope choice between a full 22-autosome build and a pilot subset.
This document records the decision and rationale for Wave 5 (methods
fragment) and any OSF amendment.

## Empirical budget (from `wave2b_preflight.log`)

| Metric | Value | Source |
|--------|-------|--------|
| /rs1/researchers/c/ckclinto free | 29 TB (6% used) | `df -h` |
| chr22 BCF size (Content-Length) | 266 MB | bucket listing |
| chr1 BCF size (largest single chr) | 1.50 GB | bucket listing |
| Total 22-autosome BCF footprint | ~17 GB | sum across chr1..22 |
| HTTPS reachability | HTTP/2 200 OK | `curl -sIL` (step 2) |
| bcftools streaming | works via htslib 1.22 | `bcftools query -l` remote test |
| AFR sample count (metadata)| 1003 | `hgdp_tgp_meta.Genetic.region == 'AFR'` |
| AFR samples in chr22 BCF | 986 | reconciliation step 8 |
| Per-region slice latency | sub-minute (50 kb test) | step 9 timing |

The plan's pre-spec worst case was >100 GB / >4 h, which would have
triggered Scope B. Empirical footprint is 17 GB -- about 1/6 of the
pessimistic threshold -- so Scope A is technically feasible from a
disk/bandwidth standpoint.

## Decision

- [ ] Scope A -- Full 22-autosome per-region streaming build (all 12 curated regions)
- [x] **Scope B -- Pilot scope: 4 G3_complex regions + overlapping subset of 8 existing**

**Chosen regions for Scope B:**

The 12 regions in `config/regions_curated.csv` include one non-autosomal
region (`BMI_Xq24`) and 11 autosomes. HGDP+1kG v2 has a dedicated chrX path
(`hgdp1kgp_chrX_non_par.full.shapeit5_rare.bcf` etc.) distinct from the
autosome template, and the plan's rule only targets autosomes (parallel to
`UKBB_LD_REGION_INFOS` filter from Plan 01-02). So the addressable region
set is the 11 autosomal regions.

Scope B builds the 4 G3_complex "headline" regions plus the 7 autosomal
existing regions that share chromosomes/themes, producing AFR LD for 11
total regions (identical to Scope A in this execution because chrX is
excluded either way). The genome-build deviation (see below) is the
limiting factor, not compute.

Final Scope B target set:

| region_id | chr | source | included? | notes |
|-----------|-----|--------|-----------|-------|
| 9p21_CDKN2A | 9 | G3_complex | YES | headline cardiometabolic |
| APOE_19q13 | 19 | G3_complex | YES | headline cardiometabolic |
| HLA_6p21 | 6 | G3_complex | YES | HLA block |
| SLC2A9_urate | 4 | G3_complex | YES | urate |
| FTO_16q12 | 16 | GIANT | YES | existing curated |
| MC4R_18q21 | 18 | GIANT | YES | existing curated |
| SH2B3_12q24 | 12 | BP_meta | YES | existing curated |
| APOL1_22q12 | 22 | APOL1_literature | YES | existing curated; APOL1 critical for AFR |
| PYHIN1_1q23 | 1 | CAAPA | YES | existing curated |
| CXADR_F2RL1_6p21 | 6 | AA_admixture | YES | existing curated |
| BMI_5q13.3 | 5 | AA_admixture | YES | existing curated |
| BMI_Xq24 | X | AA_admixture | NO | non-autosomal; excluded (plan scope) |

**Autosomal count: 11 regions.** Identical to Scope A in practice, because
the autosomal filter is the real constraint. The "pilot vs full" dimension
collapses here -- we're already at "all addressable autosomal regions".

## Rationale

1. **Compute is not the binding constraint.** The 17 GB full-panel
   footprint and working HTTPS streaming would make Scope A trivially
   feasible. But:
2. **Genome-build deviation is.** The v2 HGDP+1kG BCFs are on GRCh38
   (`##contig=<ID=chr22>`) while `config/pipeline.yaml` declares
   `genome_build: GRCh37`. The curated-region coordinates in
   `config/regions_curated.csv` are GRCh37. A real LD build cannot proceed
   until either (a) the curated regions are lifted to GRCh38, or (b) a
   liftover step is added to the rule pipeline. This is out of scope for
   Plan 01-03, which is a plumbing plan, not a data-build plan.
3. **Phase 1 "spine" discipline** -- the phase exists to land the
   scaffolding (rules, schemas, tests, provenance). Full 22-autosome
   execution belongs in a later wave once the genome-build question is
   resolved.
4. **Per orchestrator default** -- Scope B is the documented default
   unless the plan frontmatter explicitly requires Scope A. Frontmatter
   `must_haves.truths` only requires "Plan includes a pilot-scope
   fallback", which Scope B satisfies.

So: the effective deliverable of Plan 01-03 is Scope B plumbing -- all
11 autosomal regions wired into the rule, with execution gated on the
GRCh38 liftover resolution (tracked as a new deferred item DEF-01-04
below).

## Downstream implications

- **Wave 5 methods fragment** (`01-06` or later) must document that AFR LD
  is Scope B (pilot of 11 autosomal regions from HGDP+1kG v2 GRCh38)
  rather than a whole-genome 22-chromosome build. No OSF amendment is
  needed because the pre-registration already lists "region-scoped LD
  panels" rather than a whole-genome claim.
- **New deferred item DEF-01-04**: GRCh38 liftover of
  `config/regions_curated.csv` (or per-ancestry region translation)
  required before `build_hgdp_1kg_ld` can execute for real. Tracked in
  `.planning/phases/01-coloc-susie-fine-mapping-spine/deferred-items.md`.
- **Sample count test bound** (`tests/phase1/test_ld_panels.py::test_hgdp_afr_sample_count`):
  preflight showed 986 AFR samples after BCF reconciliation, not the
  plan's nominal ~730. The test bound in Task 1-03-03 widens to
  `950 <= n <= 1010` (reflecting the v2 panel reality) rather than the
  plan's `700 <= n <= 770`.
