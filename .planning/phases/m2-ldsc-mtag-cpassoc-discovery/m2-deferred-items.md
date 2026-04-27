# M2 Deferred Items Aggregator

**Phase:** m2-ldsc-mtag-cpassoc-discovery
**Closeout date:** 2026-04-27
**Per:** D-M2-06 skip-with-doc + D-M2-Q6 stratum floor + Carter resume queue inheritance from M1

This file aggregates skipped strata, skipped trait cells, the Carter resume
queue inherited from M1, and cross-references the durable M3 supersede
queue (`.planning/m2_post_m3_rerun_queue.tsv`).

---

## Skipped strata (D-M2-Q6 `_MIN_PER_STRATUM = 3` floor)

All 3 strata cleared the floor in Wave 2 (per `m2-02-mtag-3-strata-SUMMARY.md`):

| Stratum | K | Floor cleared? | Notes |
|---------|--:|----------------|-------|
| EUR     | 8 | YES (>= 3)     | All 8 traits present in inventory; cad.EUR + t2d.EUR not in M2 inventory pending DEF-M1-03-02 closure for DIAMANTE EUR |
| AFR     | 6 | YES (>= 3)     | cad.AFR + egfr.AFR + sbp.AFR missing per D-M2-06 skip-with-doc; sbp.AFR per DEC-2026-04-24-02 AoU-AFR-LD fallback |
| TRANS   | 7 | YES (>= 3)     | bmi.TRANS + sbp.TRANS missing per D-M2-06 skip-with-doc |

**No `skipped_strata.tsv` rows emitted** because all 3 strata cleared the floor.
The slicer in `src/python/build_mtag_residcov_slice.py` enumerates only keys
with on-disk munged files, so per-trait skips appear as `skipped_traits.tsv`
header-only files (no rows).

---

## Skipped trait cells (D-M2-06 strict ancestry-stratum match)

Per Wave 2 `data/processed/mtag/{stratum}/skipped_traits.tsv` (gitignored):
all three files are header-only (no rows). The strict-ancestry-match policy
naturally drops cells where the per-(trait, ancestry) `munged_path` is
missing, but Wave 2 enumeration runs only over keys with on-disk munged
files, so no per-trait skip rows are emitted.

The 9-trait amendment §4 inventory minus the per-stratum K (EUR=8, AFR=6,
TRANS=7) yields these cells absent from the M2 MTAG/CPASSOC inputs:

| Trait | Stratum | Reason | Resolution path |
|-------|---------|--------|-----------------|
| cad   | EUR     | Aragam 2022 EUR-stratum sex-strat resume queue | M5 deferred-catalog closure (Carter resume queue) |
| cad   | AFR     | No AFR-specific Aragam stratum in M2 inventory  | M3+: AoU CAD AFR if available |
| egfr  | AFR     | CKDGen 2019 has no AFR-specific release         | M3+: AoU eGFR AFR if available |
| sbp   | AFR     | Giri 2019 D-06 unresolved → DEC-2026-04-24-02 AoU fallback | M3+: AoU SBP AFR derivation |
| bmi   | TRANS   | PAGE 2019 TRANS not in M2 inventory             | M5 deferred-catalog closure |
| sbp   | TRANS   | Evangelou 2018 TRANS not in M2 inventory        | M5 deferred-catalog closure |
| t2d   | (all)   | DIAMANTE not in M2 inventory                    | M5 deferred-catalog closure (Carter resume queue) |

---

## Carter resume queue (M1 inheritance per DEF-M1-03-02 + M0 manifest deferrals)

Per `.planning/phases/m1-sumstats-upgrade-and-harmonization/m1-PHASE-CLOSEOUT.md`
inheritance + Carter's working list of post-M1 portal access actions:

| Item | Source | Status | Resolution path |
|------|--------|--------|-----------------|
| DIAMANTE EUR + AFR + EAS + HIS T2D portal cookies | DUA-pending | resume queue | Carter portal action; M5 catalog re-fresh integrates if landed before M5 freeze |
| GBMI portal × 3 traits (asthma, T2D, …) | Wix portal pending | resume queue | Carter portal action |
| Loh 2018 D-01 unresolved accession | DEF-M1-03-02 | resume queue | Carter dbGaP / EBI access action |
| Klarin 2019 D-03 unresolved | DEF-M1-03-02 | resume queue | Carter portal action |
| Aragam 2022 EUR sex-stratified | DEF-M1-02b-01 | resume queue | Carter portal action; CAD EUR sex-strat is a sensitivity check, not blocking |
| MAGIC 2021 EUR re-fetch (truncation) | DEF-M1-03-02 | resume queue | Carter HM3 re-pull; M2 used pre-truncation file |
| Giri 2019 SBP AFR | DEC-2026-04-24-02 AoU fallback | M3-deferred | AoU AFR SBP derivation per DEC-2026-04-24-02 |

These items DO NOT block M2 closeout. They become M5 catalog refresh inputs
(GWAS Catalog v_lock_M5 follow-up posting per `M2-POST-M3-06`) and M3-stage
analysis-set additions where ancestry-specific.

---

## M3 supersede queue cross-reference

The durable M3 supersede obligations are recorded in
[`.planning/m2_post_m3_rerun_queue.tsv`](../../m2_post_m3_rerun_queue.tsv).
That file is the canonical durable hand-off; this file aggregates the in-phase
skip-with-doc disposition for traceability.

Eight obligations are queued at M2 closeout:

1. `M2-POST-M3-01` (high) — AFR PLINK clumping re-fire under AoU AFR LD (D-M2-02)
2. `M2-POST-M3-02` (high) — AFR LDSC matrix slice re-fire under AoU AFR ld-scores (D-M2-02)
3. `M2-POST-M3-03` (medium) — AFR mtCOJO re-fire under AoU AFR LD (D-M2-02)
4. `M2-POST-M3-04` (low) — TRANS mtCOJO 1000G AFR sensitivity check (D-M2-Q3)
5. `M2-POST-M3-05` (medium) — AFR LD-score re-derivation per Pitfall 11
6. `M2-POST-M3-06` (deferred) — GWAS Catalog v_lock_M5 refresh (D-M2-05)
7. `M2-POST-M3-07` (high) — MTAG `--fdr` LSF re-fire to replace placeholder max_FDR=0.0 (Wave 2 D6)
8. `M2-POST-M3-08` (high) — mtCOJO production sensitivity LSF re-fire for 13 eligible targets (Wave 4 D4)

The two **load-bearing** LSF re-fires queued for immediate post-M2 attention:

- **Wave 2 D6 MTAG `--fdr` re-fire** (`M2-POST-M3-07`): LSF long-queue ~24 hr/stratum × 3 = ~72 hr; replaces `max_FDR = 0.0` placeholder with actual Turley scalars in `data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt`. Wave 4's D4 mtCOJO eligibility selector + Wave 5's Class 1 novelty caller both inherit any change in the surviving SNP set.
- **Wave 4 D4 mtCOJO production re-fire** (`M2-POST-M3-08`): per-target ~10–30 min wall on HM3-intersected COJO inputs; 13 targets × ~30 min ≈ 6.5 hr LSF long-queue. Replaces `sensitivity_flag = FAIL` for all 13 rows with actual `mtcojo_p` values.

Neither re-fire blocks the M2-closeout governance (PHASE-CLOSEOUT.md, OSF
follow-up posting, M3 region-list hand-off). They are durable obligations
recorded in the queue file with priority labels.

---

## Cross-references

- `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-PHASE-CLOSEOUT.md`
  (verifier verdict + deviations log + M3 hand-off)
- `.planning/m2_post_m3_rerun_queue.tsv` (durable M3 supersede queue)
- `.planning/DECISIONS.md` (DEC-2026-04-24-02, DEC-2026-04-25-02, D-M2-02, D-M2-Q2, D-M2-Q3, D-M2-Q5, D-M2-Q6)
- `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-RESEARCH.md` §Pitfall 11 (AFR LD-score cross-ancestry approximation rationale)

---

*Authored 2026-04-27 as part of m2-05-class1-novelty-and-closeout Task 2.*
