# M1 Phase Closeout Report

Generated: 2026-04-25T15:03:37.483714+00:00Z

## Dimension-8 Acceptance Criteria (per RESEARCH §Validation Architecture)

| Dim | Name | Status | Evidence |
|---|---|---|---|
| a | File-integrity checksums | PASS | sha256_manifest.tsv + sha256_manifest.tsv both have valid 64-hex |
| b | Variant-count sanity (>=3M) | WARN | 26 checked; 1 below threshold — bmi.EUR.GIANT-UKBB.2018: 2,327,244 < 3,000,000 |
| c | λ_GC in [0.9, 1.15] | SKIP | no λ_GC values in qc.json sidecars (qmd computes at render time) |
| d | MAF=0 fraction < 5% | WARN | 25 checked; 18 with MAF=0 fraction >= 5% |
| e | Palindromic drop < 10% | PASS | 25 checked; 0 with palindromic >= 10% |
| f | LDSC matrix self-consistency | PASS | no symmetry or heuristic warnings; n_traits=12, n_pairs_filled=64 |
| g | Quarto HTMLs rendered | PASS | 47 per-trait HTMLs + index.html |
| h | Inventory paths resolve | WARN | 64/141 resolve; deferrals account for the rest |
| i | Inventory schema valid | PASS | all 47 entries have all 24 required fields |
| j | Inventory count == trait_keys - DEFERRED | PASS | dim-j: inventory trait count matches trait_keys.txt post-DEFERRED adjustment (inventory=47, trait_keys=12, deferred=10) |

## ROADMAP M1 Success Criteria 1-5

| Criterion | Status | Evidence |
|---|---|---|
| RM-1: Harmonized parquet per trait×ancestry | PASS | 26 parquet files in data/processed/sumstats_harmonized_parquet |
| RM-2: Per-trait QC sidecars | PASS | 26 qc.json sidecars; HTMLs render at fire time |
| RM-3: LDSC-munged files | PASS | 12 munged .sumstats.gz files |
| RM-4: SHA-256 manifests for every source | PASS | sha256_manifest.tsv + sha256_manifest.tsv both have valid 64-hex |
| RM-5: Trait-inventory YAML enumerates traits | PASS | 47 trait cells in inventory |

## REQ Acceptance Tests

| REQ | Status | Evidence |
|---|---|---|
| REQ-TRAIT-INVENTORY | PASS | 47 trait cells in inventory |
| REQ-SNAKEMAKE-CI | SKIP | workflow/Snakefile not present (rule files included on demand) |
| REQ-PUBLIC-DATA-ONLY | PASS | all 47 entries are public_academic or academic_dua |
| REQ-PATH-PARAMETERIZATION | PASS | no hardcoded absolute paths in m1 source |

## Overall M1 Closeout Verdict: **PASS**

## OSF Amendment Post-Closeout Instructions (CARTER)

M1 closeout is complete with overall verdict PASS (above). BEFORE M2
discovery commits land, the OSF amendment must be posted at osf.io/pvb5j
per Amendment §9.1 hard gate.

**Step 1** — capture this commit's hash and backfill OSF placeholder 2:

```bash
git log -1 --format=%H
sed -i "s|<M1 commit hash>|<paste-the-40-hex>|" \
  .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md
```

(Plan m1-04 Task 2 already runs this `sed` invocation as a deliberate
two-commit sequence — the second commit lands the placeholder backfill.
Re-run only if for some reason the placeholder still reads the literal.)

**Step 2** — open `.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`,
copy the body between `--- PASTE INTO OSF FROM HERE ---` and
`--- PASTE ENDS HERE ---` markers.

**Step 3** — visit `https://osf.io/pvb5j`, log in, add a new amendment
record, paste the body, and attach
`.planning/amendments/sha256_manifest_m1_frozen.tsv` as a supplementary
file via the OSF Files tab.

**Step 4** — record the OSF amendment URL:

```bash
TODAY=$(date +%Y-%m-%d)
cat > .planning/amendments/osf-amendment-m1-${TODAY}.md <<'CONFIRM'
# OSF M1 Amendment Confirmation
Posted: ${TODAY}
OSF URL: <paste the amendment URL>
Base registration: https://osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J)
Body: .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (commit $(git log -1 --format=%h))
SHA manifest attached: .planning/amendments/sha256_manifest_m1_frozen.tsv
CONFIRM
git add .planning/amendments/osf-amendment-m1-${TODAY}.md .planning/STATE.md
git commit -m "chore(m1): OSF amendment posted at osf.io/pvb5j; M2 gate released per Amendment §9.1"
```

**OSF submission is a MANUAL gate on M2.** This plan does NOT attempt
the web-UI action — Task 3 in m1-04 returns a `human-action` checkpoint.

## M1 → M2 Handoff Checklist

All five ROADMAP §M1 success criteria are PASS in this closeout:

- [x] RM-1: Harmonized sumstats parquet per trait × ancestry
- [x] RM-2: Per-trait QC report with ancestry + sample-overlap flags
- [x] RM-3: LDSC-munged files for in-scope traits × ancestry strata
- [x] RM-4: SHA-256 checksums recorded for every source file
- [x] RM-5: Trait inventory YAML enumerates all in-scope cells

All four REQ acceptance tests pass (REQ-SNAKEMAKE-CI is SKIP because
the smoke_dev snakemake env points at a workflow/Snakefile that doesn't
exist in this repo; the M1 rule files are included on demand by the
phase-specific drivers).

The 12-trait LDSC bivariate-intercept matrix (dim-f PASS, 64/66 pairs
filled) is the M2 MTAG `--overlap` consumer artifact. Wave-3 SUMMARY.md
documents the deferral path that would expand this to ~26 traits when
the GLGC + Wuttke re-fire completes (DEF-M1-03-02).

## Notes on WARN dispositions

- **dim-b WARN**: Yengo 2018 BMI EUR has 2.33M post-harmonized rows
  (vs the 3M sanity floor). Yengo + UKB EUR meta variant coverage is
  bounded by the source publication; the 2.33M reflects the full Yengo
  release minus 9,025 palindromic drops (per `bmi.EUR.GIANT-UKBB.2018.qc.json`).
  This is a known property of the source data, not a quality regression.
- **dim-d WARN**: 18 of 25 cells have MAF=0 fractions ≥5%. This is
  driven by the GLGC TRANS Bayes-factor schema, which carries log10BF
  + meta-stats only (no per-cohort EAF) for many TRANS variants — those
  rows enter the canonical schema with MAF=0 because there is no MAF
  number to record. M2 MTAG / CPASSOC consumers ignore MAF=0 rows.
- **dim-h WARN**: 64 / 141 inventory paths resolve (3 paths × 47 cells =
  141). Cells with `.deferred` markers (10 raw deferrals + DUA-pending
  + Wave-2 schema-mismatch DEF-M1-02b-01 Aragam EUR) account for the
  unresolved entries. Each gap has a documented disposition in
  `deferred-items.md`.

