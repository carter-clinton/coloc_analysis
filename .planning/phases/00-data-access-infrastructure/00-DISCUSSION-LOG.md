# Phase 0: Data access + infrastructure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-09
**Phase:** 00-data-access-infrastructure
**Mode:** --auto --chain (all decisions auto-selected with recommended defaults)
**Areas discussed:** Genome build, Pipeline architecture, Path parameterization, Data layout, CI smoke test, Supplementary table fixes, New ancestry GWAS ingest, Conda environment pinning, OSF pre-registration

---

## Genome Build Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Stay GRCh37 with liftover support | Keep hg19 primary, add liftover for GRCh38-only sources | ✓ |
| Migrate to GRCh38 | Lift all legacy data to GRCh38, use as primary | |
| Dual-build pipeline | Maintain both coordinate systems throughout | |

**User's choice:** [auto] Stay GRCh37 with liftover support (recommended default)
**Notes:** Legacy analysis is GRCh37, most GWAS sumstats are GRCh37. Liftover for GRCh38-only sources minimizes disruption.

---

## Pipeline Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Refactor and modularize | Preserve legacy rule logic, restructure into new skeleton | ✓ |
| Rewrite from scratch | Clean-room implementation, discard legacy code | |
| Wrapper approach | Keep legacy as-is, add thin wrapper layer | |

**User's choice:** [auto] Refactor and modularize (recommended default)
**Notes:** 8 legacy rules contain tested logic. Full rewrite wastes proven code.

---

## Path Parameterization

| Option | Description | Selected |
|--------|-------------|----------|
| Single config/pipeline.yaml | Hierarchical keys, ~5-6 root variables | ✓ |
| Environment variables | Set paths via env vars, no config file | |
| Per-script config | Each script has its own path config | |

**User's choice:** [auto] Single config/pipeline.yaml (recommended default)
**Notes:** Collapses 174 hardcoded paths to ~5-6 root variables. Snakemake `config` dict natively supports YAML.

---

## Data Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Maintain symlink + manifest | Keep /rs1 symlinks, add data/manifest.yaml | ✓ |
| Copy data locally | Mirror data into GPFS | |
| Remote data access | Access /rs1 directly without symlinks | |

**User's choice:** [auto] Maintain symlink + manifest (recommended default)
**Notes:** PROJECT.md constraint: no 30 GB data duplication. Symlinks are already in place.

---

## CI Smoke Test

| Option | Description | Selected |
|--------|-------------|----------|
| 3 well-characterized loci | Subset legacy loci with known PP.H4 > 0.8, regression test | ✓ |
| Synthetic data | Generate fake sumstats for testing | |
| Single-locus minimal | Just 1 locus for speed | |

**User's choice:** [auto] 3 well-characterized loci (recommended default)
**Notes:** Ground truth from legacy results enables regression testing. 3 loci provides coverage without excessive runtime.

---

## Claude's Discretion

- Exact choice of 3 toy loci
- Column mapping specifics for new GWAS datasets
- R config loader implementation
- LSF profile specifics
- Container strategy (nice-to-have)

## Deferred Ideas

None — discussion stayed within phase scope.
