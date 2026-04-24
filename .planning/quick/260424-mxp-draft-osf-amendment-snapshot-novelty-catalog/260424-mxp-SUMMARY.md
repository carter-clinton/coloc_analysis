# Quick Task 260424-mxp — SUMMARY

**Objective**: M0 Route B follow-through — (a) snapshot the novelty cross-reference catalog checksums and (b) draft a standalone paste-ready OSF amendment text. Per the approved plan at [/home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md](../../../../../../home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md).

**Status**: ✅ Complete — 3/3 atomic commits on `main`. OSF amendment NOT posted; posting remains gated on M1 sumstats closeout per Amendment §9.1.

## Deliverables

| # | File | Commit | Delta |
|---|---|---|---|
| 1 | [data/catalogs/catalog_lock_manifest.tsv](../../../data/catalogs/catalog_lock_manifest.tsv) + [data/catalogs/README.md](../../../data/catalogs/README.md) + [.gitignore](../../../.gitignore) | `0a1339e` | +134 / −0 — 5-row manifest (1 M0-locked, 4 M5-deferred), schema + retrieval recipes + M5 handoff checklist, .gitignore rules mirroring `data/raw/*` convention |
| 2 | [.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md](../../amendments/OSF-AMENDMENT-TEXT-2026-04-22.md) | `fd1836e` | +128 / −0 — standalone paste-ready OSF body with pre-paste + post-paste reference blocks; 3 intentional placeholders; ClinVar SHA-256 anchor inline; 4-commitment "What is not changing" paragraph preserving original-prereg discipline |
| 3 | [.planning/quick/260424-mxp-…/PLAN.md](./260424-mxp-PLAN.md) + [SUMMARY.md](./260424-mxp-SUMMARY.md) + [.planning/STATE.md](../../STATE.md) | `<commit3>` | quick-task artifacts + STATE.md Quick Tasks row + Session Continuity refresh |

## Catalog lock state (snapshot 2026-04-24)

| Catalog | Status | Version | SHA-256 (raw bytes) | Size | URL |
|---|---|---|---|---|---|
| ClinVar `variant_summary.txt.gz` | **M0-locked** | `2026-04-20_weekly_release` | `3be9939676e44a79e906dd167caec45e6e871be55db1a4ddb9269ebf0828e58e` | 436,222,584 B (8,920,417 rows raw) | `ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz` |
| Pickrell 2016 supplement | M5-deferred | `pmc_PMC5207801_NIHMS780506-supplement-2` | — | — | `pmc.ncbi.nlm.nih.gov/articles/PMC5207801/` |
| GWAS Catalog associations | M5-deferred | `pending_M5_pin` | — | — | `ebi.ac.uk/gwas/api/search/downloads/alternative` |
| Open Targets Genetics L2G | M5-deferred | `pending_M5_pin` | — | — | `ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/etl/parquet/` |
| Watanabe 2019 GWAS Atlas | M5-deferred | `pending_M5_pin` | — | — | `atlas.ctglab.nl/about/download` |

**Pickrell deferral rationale**: NCBI PMC's `cloudpmc-viewer-pow` JavaScript challenge blocked `curl` on 2026-04-24; OA-package fallback at `ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/fe/19/PMC5207801.tar.gz` also inaccessible. Rather than implement POW-solving during M0, the supplement is deferred to M5 with a documented 4-step retrieval recipe in `data/catalogs/README.md` (browser download → headless-chromium → Nature CDN → author/Zenodo request).

## Guardrails honored

- **Framing**: zero "revision / cleanup / fix" language in the amendment body; framed as hypothesis-driven scope expansion.
- **Pre-registration discipline**: amendment explicitly preserves the four original-prereg commitments (pre-registration discipline, multi-method triangulation, public-data-only, hold-out replication).
- **OSF not posted**: draft only, per §9.1 timing gate (post after M1 sumstats checksums frozen, before M2 MTAG/CPASSOC).
- **Atomic commits**: three separate `main` commits, no push, no worktree, no `--amend`, no `--no-verify`.
- **No M5 work pulled forward**: `data/catalogs/` contains only `catalog_lock_manifest.tsv`, `README.md`, and the ClinVar payload (gitignored). No per-trait novelty calls, no cross-reference outputs.
- **GPFS convention**: no worktree isolation; GSD mode `solo` with `git.isolation: branch` per CLAUDE.md.

## Downstream (remaining Route B human-action items)

- **Route B Step 3.3 (Carter manual action)**: at M1 closeout, fill the 3 placeholders in [OSF-AMENDMENT-TEXT-2026-04-22.md](../../amendments/OSF-AMENDMENT-TEXT-2026-04-22.md) and paste the body between the markers into the OSF web UI at `osf.io/az52u`. Add new DECISIONS.md entry + STATE.md update + repo tag `M1-OSF-AMENDMENT-POSTED-YYYY-MM-DD` afterward.
- **M5 lock refresh**: at the M5 cross-reference date, populate SHA-256 for the 4 deferred catalogs per `data/catalogs/README.md` handoff checklist; re-verify ClinVar; commit as `data(catalogs): M5 lock — populate SHA-256 for deferred catalogs + re-verify ClinVar`; update the amendment text's `<M5-locked catalog commit hash>` placeholder.

## Source

Parent plan: [/home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md](../../../../../../home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md). Upstream: [quick-260423-osk](../260423-osk-route-b-m0-closeout-rewrite-project-road/) (Route B M0 closeout rewrite, commit range `d9c9905..880fc36`).
