# M2-POST-M3-08 Harvest Runbook

## Why this exists

Quick task `260429-s10` submitted 13 LSF long-queue jobs (IDs 67672-67684,
submitted 2026-04-29T20:59:43-04:00) for the M2 mtCOJO production sensitivity
re-fire with HM3-intersected COJO inputs. The driver
`bin/fire_m2_post_m3_08_mtcojo.sh` returns immediately after submission. This
runbook documents the steps Carter executes when LSF lands the per-target
results, to migrate outputs into the canonical sensitivity layout, rebuild
the per-stratum `mtcojo_sensitivity.tsv` artifacts, and flip the obligation
queue row from `in_flight` to `completed`.

Pre-flight smoke gate (Task 3, witness:
`.planning/quick/260429-s10-.../SMOKE-PASS.log`) confirmed that HM3
intersection plus auto-pruning of empty covariates (sbp.EUR, stroke.EUR;
both harmonize to non-rsID identifiers) unblocks GCTA's internal LDSC
bivariate-intercept regression. Smoke completed in 2 min 34 sec on login02
with a 1,019,733-row `mtcojo.cma` output.

## 1. Monitoring (during flight)

List all M2-POST-M3-08 jobs:

    bjobs -u $USER -J 'm2p3_08_*' -w

By job ID directly from the manifest:

    bjobs $(awk 'NR>1 {print $2}' data/processed/mtcojo/m2_post_m3_08_bjobs.tsv | tr '\n' ' ')

Tail the LSF stdout for a specific stratum/target (e.g. EUR/bmi):

    tail -f logs/lsf/m2p3_08_EUR_bmi.out

Tail the GCTA log for a specific target:

    tail -f data/processed/mtcojo/EUR/m2p3_08/bmi.EUR.GIANT-UKBB.2018/bmi.EUR.GIANT-UKBB.2018.mtcojo.fire.log

## 2. Detecting completion

Each per-target jobscript writes a `.bjob.done` sentinel as its LAST step
(after the GCTA mtCOJO call AND the `.cojo` canonicalization succeed).

Count complete jobs:

    find data/processed/mtcojo/{EUR,AFR,TRANS}/m2p3_08 -name '*.bjob.done' 2>/dev/null | wc -l

Target: 13. When the count reaches 13, harvest.

Cross-check via LSF:

    bjobs -d $(awk 'NR>1 {print $2}' data/processed/mtcojo/m2_post_m3_08_bjobs.tsv | tr '\n' ' ') | grep -c DONE

Target: 13.

Per-target failure check (residual GCTA LDSC failures, post-HM3):

    for f in data/processed/mtcojo/{EUR,AFR,TRANS}/m2p3_08/*/*.mtcojo.fire.log; do
        if grep -q "no SNP in common" "$f"; then echo "STILL FAILING: $f"; fi
    done

If any line is printed, that target's HM3 intersection did NOT unblock
GCTA. Inspect manually before proceeding.

## 3. Migrating outputs into the canonical sensitivity layout

The driver writes COJO outputs under

    data/processed/mtcojo/<stratum>/m2p3_08/<target>/<target>.mtcojo.cojo

but `src/python/build_mtcojo_sensitivity_table.py` reads from

    data/processed/mtcojo/<stratum>/<target>.mtcojo.cojo

Symlink (preferred — no disk duplication; the `.cojo` files are tens of MB
each) or copy each target's `.cojo` into the canonical location BEFORE
running the aggregator:

    for STRATUM in EUR AFR TRANS; do
        for d in data/processed/mtcojo/$STRATUM/m2p3_08/*/; do
            target=$(basename "$d")
            ln -sf "$(pwd)/${d}${target}.mtcojo.cojo" \
                   "data/processed/mtcojo/$STRATUM/${target}.mtcojo.cojo"
        done
    done

(If the stratum directory still has stale `.cojo` files from the failed
first-pass legacy fire, remove them BEFORE the symlink loop:
`rm -f data/processed/mtcojo/$STRATUM/*.mtcojo.cojo` per stratum.)

## 4. Rebuild the sensitivity tables

For each stratum:

    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \
        src/python/build_mtcojo_sensitivity_table.py \
        --stratum <STRATUM> \
        --eligible data/processed/mtcojo/<STRATUM>/mtcojo_eligible_targets.tsv \
        --mtcojo-dir data/processed/mtcojo/<STRATUM> \
        --mtag-filtered data/processed/mtag/<STRATUM>/<STRATUM>_mtag_maxfdr_filtered.txt \
        --out data/processed/mtcojo/<STRATUM>/mtcojo_sensitivity.tsv

Expected: `sensitivity_flag` column has PASS / WARN / FAIL classifications
based on actual `mtcojo_p` vs `mtag_p_original` ratio +
`max_overlapping_intercept` witness — NOT all-FAIL as in the pre-fire
placeholder artifact.

## 5. Verify bmi.EUR is included

Pre-fire placeholder `data/processed/mtcojo/EUR/mtcojo_sensitivity.tsv` had
only 4 EUR rows (hdl/ldl/tc/tg) — bmi.EUR was missing despite being in
`mtcojo_eligible_targets.tsv`. Target post-fire row count = 5 EUR rows.

Open `data/processed/mtcojo/EUR/mtcojo_sensitivity.tsv` and confirm a row
with `trait=bmi.EUR.GIANT-UKBB.2018` exists.

If bmi.EUR is STILL missing post-harvest:

a. Inspect `data/processed/mtcojo/EUR/bmi.EUR.GIANT-UKBB.2018.mtcojo.cojo`
   — is it non-empty? Smoke confirmed GCTA produces a 1,019,733-row
   `.mtcojo.cma` file for bmi.EUR, so the canonical `.cojo` symlink should
   point at a non-empty file. If empty, GCTA failed for bmi.EUR
   specifically — inspect
   `data/processed/mtcojo/EUR/m2p3_08/bmi.EUR.GIANT-UKBB.2018/bmi.EUR.GIANT-UKBB.2018.mtcojo.fire.log`
   for residual issues.

b. If non-empty, the aggregator at line ~63 of
   `build_mtcojo_sensitivity_table.py` emits NO row when no MTAG-novel
   SNP intersects the cojo output. This is by design but produces a
   silent omission. Open a follow-up quick task to add a
   "no-intersect FAIL row" emission so every eligible target appears in
   the table regardless of MTAG-novel intersection. The defect is
   pre-existing — NOT caused by this fire — but is most visible here
   because bmi.EUR has only 1 MTAG-novel hit and an extreme overlap
   (max_overlapping_intercept = 0.1992 with hdl.EUR).

## 6. Status flip in the obligation queue

Once `mtcojo_sensitivity.tsv` has non-FAIL rows in at least one stratum,
edit `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-08:

    status: in_flight  →  completed

Optionally add a `completed_ts` column (the schema is rectangular today
with `status`, `submit_ts`, `lsf_job_ids` only; widening to
`completed_ts` would require backfill on all 8 rows).

## 7. Out-of-scope items called out for follow-up

Items NOT addressed by this re-fire (carry-forward obligations):

- **bmi.EUR-missing-from-sensitivity-table** (see §5b): defect in
  `build_mtcojo_sensitivity_table.py` row-emission logic. Open as a
  separate quick task when confirmed present post-harvest.

- **sbp.EUR / stroke.EUR harmonization namespace mismatch**: these traits
  harmonize to chr:pos (sbp) and chr:pos:A1:A2 (stroke) identifiers, neither
  of which intersects the rsID-keyed HapMap3 list. They were auto-pruned
  from the bmi.EUR mtcojo covariate list during this fire. Re-harmonizing
  to rsIDs would let them participate in HM3-restricted analyses; this is
  an M1 follow-up obligation (separate from the M2-POST-M3-* family).

- **AoU AFR LD panel + ld-score supersede** (M2-POST-M3-01/03/05): NOT
  addressed by this re-fire. AFR rows of the re-fired sensitivity table
  use the cross-ancestry EUR ld-score approximation (D-M2-Q2) and the
  N=504 1000G AFR plink panel. Will need re-derivation under
  M2-POST-M3-05 once AoU AFR ld-scores land.

- **TRANS AFR-LD sensitivity** (M2-POST-M3-04): TRANS rows in this fire
  use 1000G EUR Phase3 plink (D-M2-Q3 primary). The AFR sensitivity
  check is a separate obligation.

- **MTAG --fdr LSF re-fire** (M2-POST-M3-07): not touched.

- **GWAS Catalog v_lock_M5 refresh** (M2-POST-M3-06, deferred).
