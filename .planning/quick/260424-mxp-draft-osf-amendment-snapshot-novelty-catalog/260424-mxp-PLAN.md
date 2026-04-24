---
phase: quick-260424-mxp
plan: 01
type: execute
wave: 1
depends_on:
  - quick-260423-osk  # Route B M0 closeout rewrite must be on main first
files_created:
  - data/catalogs/catalog_lock_manifest.tsv
  - data/catalogs/README.md
  - .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
  - .planning/quick/260424-mxp-draft-osf-amendment-snapshot-novelty-catalog/260424-mxp-PLAN.md
  - .planning/quick/260424-mxp-draft-osf-amendment-snapshot-novelty-catalog/260424-mxp-SUMMARY.md
files_modified:
  - .gitignore
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-CATALOG-VERSION-LOCK    # REQUIREMENTS.md lines 367–379
  - AMEND-2026-04-22-SEC7       # 5 novel-variant discovery classes + catalog drift policy (§7.2)
  - AMEND-2026-04-22-SEC9       # OSF amendment plan — paste-ready text + §9.1 timing gate
  - ROADMAP-M1-SUCCESS-4        # sumstats checksums frozen for OSF amendment
  - ROADMAP-M5-SUCCESS-4        # catalog_lock_manifest.tsv with SHA-256 + URL per catalog
  - SKIP-OSF-SUBMISSION         # draft only; posting remains gated on M1 closeout
must_haves:
  truths:
    - "data/catalogs/catalog_lock_manifest.tsv is a 7-column TSV with 1 header + 5 catalog rows (clinvar, pickrell, gwas_catalog, opentargets_l2g, watanabe)"
    - "Exactly one row has status=M0-locked (clinvar_variant_summary with a 64-char hex SHA-256 and non-empty fetched_date + size_bytes)"
    - "The four remaining rows have status=M5-deferred with URL + version anchor present but sha256 empty"
    - ".gitignore excludes data/catalogs/* payload but tracks catalog_lock_manifest.tsv + README.md via negation rules"
    - "data/catalogs/README.md documents schema, M0/M5 lock policy, exact retrieval commands, and M5 handoff checklist"
    - ".planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md contains exactly one --- PASTE INTO OSF FROM HERE --- / --- PASTE ENDS HERE --- paired marker"
    - "The paste block contains three intentional placeholders (M1 completion date, M1 commit hash, M5-locked catalog commit hash) and zero other bracketed TODOs/FIXMEs"
    - "The paste block names all 5 comparator catalogs (GWAS Catalog, Pickrell 2016, Watanabe 2019, Open Targets Genetics L2G, ClinVar) and references data/catalogs/catalog_lock_manifest.tsv by relative path"
    - "The paste block's 'What is not changing' paragraph preserves the four original-prereg commitments: pre-registration discipline, multi-method triangulation, public-data-only constraint, hold-out replication strata"
    - "STATE.md Quick Tasks Completed table has a new row for 260424-mxp with commit range 0a1339e..<commit3>; Session Continuity is refreshed"
    - "Three atomic commits on main, no push, no worktree, no --amend, no --no-verify"
    - "No OSF submission performed — draft only, gated on M1 per Amendment §9.1"
  artifacts:
    - path: "data/catalogs/catalog_lock_manifest.tsv"
      provides: "M0 pre-registration anchor for the 5 comparator catalogs; SHA-256 for ClinVar; URL + version anchors for 4 deferred catalogs"
      contains: "M0-locked"
    - path: "data/catalogs/README.md"
      provides: "Manifest schema, M0/M5 lock policy, retrieval recipes per catalog, M5 handoff checklist, Pickrell POW-deferral rationale"
      contains: "M5 handoff checklist"
    - path: ".planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md"
      provides: "OSF web-UI paste-ready body for the Route B genome-wide reframe amendment, with pre-paste and post-paste reference blocks"
      contains: "--- PASTE INTO OSF FROM HERE ---"
    - path: ".planning/STATE.md"
      provides: "Quick Tasks Completed row for 260424-mxp + Session Continuity pointer to remaining human-action items"
      contains: "260424-mxp"
  key_links:
    - from: ".planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md paste block"
      to: "data/catalogs/catalog_lock_manifest.tsv"
      via: "explicit relative-path reference including the ClinVar SHA-256 anchor"
      pattern: "catalog_lock_manifest\\.tsv"
    - from: ".planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md"
      to: ".planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md"
      via: "pre-paste reference block identifies the design-rationale doc"
      pattern: "PROJECT-AMENDMENT-2026-04-22"
    - from: ".planning/STATE.md Session Continuity"
      to: "Route B Step 3.3 (OSF posting)"
      via: "refreshed continuity marker flagging remaining human-action item"
      pattern: "Route B Step 3.3"
---

# Quick Task 260424-mxp — PLAN

## Objective

Execute the two outstanding Route B M0 deliverables that were scoped out of the 260423-osk closeout rewrite:

1. **Snapshot the novelty cross-reference catalog** — write `data/catalogs/catalog_lock_manifest.tsv` as a pre-registration anchor for the 5 comparator catalogs the 5 novelty classes depend on. Per user directive 2026-04-24 ("small catalogs now, defer large to M5"): lock ClinVar SHA-256 today, scaffold M5-deferred rows for the rest.
2. **Promote the OSF amendment body to a standalone paste-ready file** — extract the draft text at [PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §9.3](../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md) into `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` so Carter can copy-paste into `osf.io/az52u` without re-reading the 260-line design doc at post time.

Posting is NOT performed — remains gated on M1 sumstats harmonization closeout per Amendment §9.1.

## Execution (3 atomic commits)

### Commit 1 — `data(catalogs): M0 Route B snapshot — lock ClinVar SHA-256; scaffold M5-deferred rows`

1. `mkdir -p data/catalogs/`
2. Download ClinVar `variant_summary.txt.gz` from `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz`; compute SHA-256 via `sha256sum`; record byte size via `stat --printf='%s'`; capture `Last-Modified` HTTP header as version string.
3. Attempt Pickrell 2016 supplement fetch via PMC (`PMC5207801`). If PMC's `cloudpmc-viewer-pow` JavaScript challenge blocks `curl` (it does as of 2026-04-24), fall back per plan's URL-rot clause: flip to `M5-deferred`, record the PMC page URL as the M5 retrieval anchor, document the POW blocker in README.
4. Write `catalog_lock_manifest.tsv` with 7 columns (name, version, url, sha256, fetched_date, size_bytes, status) × 5 rows: 1 `M0-locked` (ClinVar), 4 `M5-deferred` (Pickrell, GWAS Catalog, Open Targets L2G, Watanabe 2019 GWAS Atlas) with documented URL anchors.
5. Write `data/catalogs/README.md` covering: schema, M0/M5 lock policy + rationale (cite Amendment §7.2 on catalog drift), exact retrieval command for ClinVar, deferred-catalog recipes (4-step recipe for Pickrell including POW workaround, release-date-pinning for GWAS Catalog / Open Targets / Watanabe), M5 handoff checklist.
6. Add `data/catalogs/*` to `.gitignore` with negation exceptions for `catalog_lock_manifest.tsv` and `README.md`, matching the existing `data/raw/*` / `data/processed/*` convention.
7. Stage: `.gitignore`, `data/catalogs/catalog_lock_manifest.tsv`, `data/catalogs/README.md`. Commit.

**Landed:** `0a1339e` (3 files changed, 134 insertions).

### Commit 2 — `docs(amendments): promote §9.3 to standalone OSF paste-ready text`

1. Extract Amendment §9.3 verbatim-intent paragraphs from [PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md).
2. Write `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` with three top-level sections:
   - Pre-paste reference (target OSF project, supersedes-but-incorporates prior amendments, posting gate, catalog lock manifest commit hash, pre-paste checklist).
   - `--- PASTE INTO OSF FROM HERE ---` block — paste-ready body with 3 intentional placeholders (`[M1 completion YYYY-MM-DD]`, `<M1 commit hash>`, `<M5-locked catalog commit hash>`), inline reference to `data/catalogs/catalog_lock_manifest.tsv` including the ClinVar SHA-256 as a concrete M0 anchor, and an expanded "What is not changing" paragraph preserving the four original-prereg commitments.
   - Post-paste reference (OSF timestamp verification, repo tag convention, rollback policy).
3. Stage the file. Commit.

**Landed:** `fd1836e` (1 file changed, 128 insertions).

### Commit 3 — `docs(quick-260424-mxp): quick-task artifacts + STATE.md refresh`

1. Create `.planning/quick/260424-mxp-draft-osf-amendment-snapshot-novelty-catalog/` with `260424-mxp-PLAN.md` (this file) and `260424-mxp-SUMMARY.md`.
2. Append a new row to STATE.md "Quick Tasks Completed" table following the format of 260423-osk + 260423-nzu (columns: #, Description, Date, Commit range, Directory link).
3. Refresh STATE.md "Session Continuity" section to record that Route B Step 3.3 (OSF posting at `osf.io/az52u`) is the sole remaining Route B human-action item, with paste-ready text + M0 catalog anchors now available for posting at M1 closeout.
4. Stage all three. Commit.

## Verification

Run after Commit 3 lands:

1. `awk -F'\t' 'NR==1{print NF}' data/catalogs/catalog_lock_manifest.tsv` → `7`.
2. `awk -F'\t' 'NR>1{print $7}' data/catalogs/catalog_lock_manifest.tsv | sort | uniq -c` → `1 M0-locked`, `4 M5-deferred`.
3. `awk -F'\t' 'NR>1 && $7=="M0-locked" && length($4)!=64' data/catalogs/catalog_lock_manifest.tsv` → empty.
4. `awk -F'\t' 'NR>1 && $7=="M5-deferred" && $4!=""' data/catalogs/catalog_lock_manifest.tsv` → empty.
5. `grep -c -- '--- PASTE INTO OSF FROM HERE ---' .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` → `1`.
6. `grep -c -- '--- PASTE ENDS HERE ---' .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md` → `1`.
7. `awk '/--- PASTE INTO OSF FROM HERE ---/{flag=1;next} /--- PASTE ENDS HERE ---/{flag=0} flag' .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md | grep -cE 'MTAG|CPASSOC|AFR|9 traits|catalog_lock_manifest'` → `≥ 5`.
8. `git log --oneline main -4` shows `0a1339e`, `fd1836e`, Commit 3, with 83922d4 (260423-osk) as the preceding anchor.
9. `grep -c '260424-mxp' .planning/STATE.md` ≥ 2 (Quick Tasks row + Session Continuity).
10. `find data/catalogs/ -type f` lists exactly `catalog_lock_manifest.tsv`, `README.md`, and `variant_summary.txt.gz` (the last is gitignored but present locally for M5 re-verification).

## Constraints honored

- **Public data only.** ClinVar is public. Deferred catalogs (Pickrell supplement, GWAS Catalog, Open Targets, Watanabe GWAS Atlas) are all public at the URLs recorded.
- **No worktree.** GSD mode is `solo` with `git.isolation: branch` per CLAUDE.md.
- **Atomic commits.** Three separate `main` commits; no amendment; no force-push.
- **OSF posting not performed.** Draft-only per plan Question 3 answer and Amendment §9.1 timing gate.
- **Framing: original hypothesis-driven research.** The amendment text does not use "revision" / "cleanup" / "correct the" language.

## Source

Parent plan: [/home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md](../../../../../../home/ckclinto/.claude/plans/m0-route-b-draft-generic-kernighan.md).

Upstream dependency (already on main): quick task [260423-osk](../260423-osk-route-b-m0-closeout-rewrite-project-road/) — PROJECT / ROADMAP / REQUIREMENTS / DECISIONS rewritten to the M0–M6 two-track framing this task depends on.
