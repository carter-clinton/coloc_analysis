# M2-POST-M3-07 MTAG --fdr Production Fire Runbook

## Why this exists

Three LSF long-queue jobs (one per stratum: EUR T=8 + AFR T=6 + TRANS T=7)
close the Wave 2-D6 hand-off (`m2-02-task4-mtag-production-fire.md` §6) by
replacing the placeholder `max_FDR=0.0` column in
`data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt` with the
actual per-trait Turley scalars from `--skip_mtag --fdr --intervals 2
--fit_ss`. The env-build half of the dependency_blockers pair is closed
by quick-260429-utt (this runbook's parent task); this runbook covers the
LSF allocation half (executed in a separate quick task analogous to
quick-260429-s10).

Pre-fire smoke gate (Task 3, witness:
`.planning/quick/260429-utt-.../SMOKE-AFR-FDR.log` + `TIMING.md`)
confirmed that MTAG `--skip_mtag --fdr --intervals 2 --fit_ss --cores 4`
runs to completion on AFR (T=6) in **52.04 s wall** with **peak RSS
1.36 GB**, producing all 6 per-trait max_FDR scalars as finite floats in
[1e-9, 0.12] (none collapsed to placeholder 0.0; none diverged to
NaN/Inf). The `--fit_ss` simplex pruning collapsed the post-Spike-Slab
grid from 2^63 unconstrained points to **2 grid points** for T=6 — an
empirical demonstration that the Wave 2-D6 "~24 hr per stratum" envelope
estimate was a worst-case anchor for the unconstrained simplex; the
pruned-prior reality is sub-2-min per stratum.

## 1. Pre-fire checklist

- [ ] m2-mtag env exists:
      ```
      test -x /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python
      /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python -c "import numpy; assert numpy.__version__=='1.26.4'"
      /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python -c "import joblib; print(joblib.__version__)"  # 1.4.2
      ```

- [ ] Wave 2 outputs present for all 3 strata:
      ```
      for s in EUR AFR TRANS; do
          for f in residcov.txt residcov.trait_order.json \
                   ${s}_mtag_omega_hat.txt ${s}_mtag_sigma_hat.txt; do
              test -s data/processed/mtag/$s/$f || echo MISSING $s/$f
          done
          for i in 1 2 3 4 5 6 7 8; do
              f=data/processed/mtag/$s/${s}_mtag_trait_${i}.txt
              [ -f "$f" ] && echo OK $s/$i
          done
      done
      ```
      Expected: 8 EUR + 6 AFR + 7 TRANS trait files.

- [ ] LSF login is alive:
      ```
      bjobs -u $USER 2>&1 | head -3
      ```

- [ ] Smoke witness reviewed:
      ```
      cat .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md
      ```
      Smoke Branch is **PASS** (52.04 s wall on AFR T=6); production fire
      is unblocked. FAIL or PARTIAL would mean the fire SHOULD NOT
      proceed without diagnosis.

- [ ] Driver script committed:
      ```
      test -x bin/fire_m2_post_m3_07_mtag_fdr.sh
      bash -n bin/fire_m2_post_m3_07_mtag_fdr.sh
      ```

- [ ] Magma_helpers bypass deprecated for M3+ MTAG fires (record-keeping
      only; the Wave 2 canonical fire `bin/fire_m2_02_mtag_3strata.sh`
      remains UNTOUCHED for re-discoverability).

## 2. Invocation

Default resource pins (CORES=4, MEM_GB=8) derived from quick-260429-utt
AFR smoke. Tunable via env vars if Carter elects to throw more parallelism
at T=8 EUR (smoke says it's not needed — sub-2-min walls expected):

    # Default invocation:
    bash bin/fire_m2_post_m3_07_mtag_fdr.sh

    # Override CORES (e.g. if T=8 EUR is being given more parallelism):
    CORES=16 MEM_GB=16 bash bin/fire_m2_post_m3_07_mtag_fdr.sh

    # Override INTERVALS (default 2 — DO NOT CHANGE without re-running smoke):
    INTERVALS=4 bash bin/fire_m2_post_m3_07_mtag_fdr.sh

Expected console output:

    [fire_m2_post_m3_07] submitted EUR as job <id> (cores=4 mem=8GB)
    [fire_m2_post_m3_07] submitted AFR as job <id> (cores=4 mem=8GB)
    [fire_m2_post_m3_07] submitted TRANS as job <id> (cores=4 mem=8GB)
    [fire_m2_post_m3_07] DONE. Manifest: .planning/quick/.../bjobs.tsv

Manifest TSV: 1 header + 3 data rows. Each row has columns
`submit_ts, job_id, stratum, cores, mem_gb, jobscript`. The manifest is
also copied to `data/processed/mtag/m2_post_m3_07_bjobs.tsv` for
post-LSF harvest cross-reference.

## 3. Monitoring (during flight)

List all M2-POST-M3-07 jobs:

    bjobs -u $USER -J 'm2p3_07_*' -w

By job ID directly from the manifest:

    bjobs $(awk 'NR>1 {print $2}' data/processed/mtag/m2_post_m3_07_bjobs.tsv | tr '\n' ' ')

Per-stratum live MTAG log:

    tail -f data/processed/mtag/<STRATUM>/<STRATUM>_mtag_fdr_run.log

LSF stdout/stderr:

    tail -f logs/lsf/m2p3_07_<STRATUM>.out
    tail -f logs/lsf/m2p3_07_<STRATUM>.err

## 4. Completion detection

Each per-stratum jobscript writes a `.bjob.done` sentinel as its LAST
step. Count complete strata:

    find data/processed/mtag/{EUR,AFR,TRANS} \
        -maxdepth 1 -name '*_mtag_fdr.bjob.done' | wc -l

Target: **3**. When count == 3, harvest.

Cross-check via LSF:

    bjobs -d $(awk 'NR>1 {print $2}' data/processed/mtag/m2_post_m3_07_bjobs.tsv | tr '\n' ' ') \
        | grep -c DONE

Target: 3. Any EXIT row warrants inspection of the corresponding
`<STRATUM>_mtag_fdr_run.log` for the per-trait grid traversal trace —
the AFR smoke established that for T=6 the grid is 2 points after
Spike-Slab fit; T=7/T=8 should be of the same order with `--fit_ss`.

## 5. Post-LSF harvest plan

The LSF re-fire writes the FDR audit with REAL max_FDR scalars to:

  - `data/processed/mtag/<STRATUM>/<STRATUM>_mtag.FDR.log` (full FDR
    calculation log; mirrors AFR smoke's `AFR_mtag.FDR.log` produced in
    /tmp staging)
  - `data/processed/mtag/<STRATUM>/<STRATUM>_mtag_fdr_mat.txt` (grid-point
    FDR matrix)
  - `data/processed/mtag/<STRATUM>/<STRATUM>_mtag_prob_grid.txt` (prob
    grid points after --fit_ss restriction)

The harvest task joins the per-trait scalars onto the existing
`_mtag_maxfdr_filtered.txt` placeholder column.

Pseudocode for the harvest step (a separate quick task, NOT executed
here):

1. For each stratum, read the new MTAG --fdr audit output:

       for s in EUR AFR TRANS; do
           # Locate the new audit file (path depends on MTAG --fdr behavior;
           # check the log for actual output path)
           ls -la data/processed/mtag/$s/${s}_mtag*FDR* \
                  data/processed/mtag/$s/${s}_mtag_fdr_mat.txt \
                  data/processed/mtag/$s/${s}_mtag_prob_grid.txt
       done

2. Build trait_key -> max_FDR mapping per stratum from the new audit. The
   AFR smoke witness (TIMING.md) shows the expected output structure:
   one finite float per trait, parsed from the `FDR of Trait N: ...` log
   lines (e.g. AFR `[0.00970590589390107, 0.003316170693667885,
   4.08283132227812e-06, 0.11541401327515466, 8.642644223250632e-09,
   0.0017651764636435043]` for bmi/hdl/ldl/stroke/tc/tg).

3. Rewrite `${s}_mtag_maxfdr_filtered.txt` `max_FDR` column (currently
   all 0.0) with the real per-trait scalar (joining on `trait_key` col 12).
   Preserve all other columns exactly. Verify row count unchanged.

4. Audit the placeholder ratio AFTER harvest:

       for s in EUR AFR TRANS; do
           awk -F'\t' 'NR>1 {print $11}' data/processed/mtag/$s/${s}_mtag_maxfdr_filtered.txt \
               | sort -u | head
           # Should NOT be only 0.0; should be K finite floats (one per trait).
       done

5. Flip queue. Edit `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-07:

       status:      not_started → completed
       submit_ts:   -            → <ISO_8601_from_bjobs.tsv>
       lsf_job_ids: -            → <comma_separated_3_job_ids>

   (Prefer Python TSV rewrite over manual edit; sister-task quick-260429-s10
   §6 documents this pattern.)

## 6. Out-of-scope items called out for follow-up

- The quick-260429-utt PREP task only builds the env + smokes AFR;
  production fire is a separate quick task analogous to quick-260429-s10.
  This runbook is the production fire's pre-fire reference.

- Downstream consumers of `_mtag_maxfdr_filtered.txt` (e.g. joint-signal
  HyPrColoc inputs, Phase 2 MTAG-novel SNP inheritance, CPASSOC overlap
  table) will need a refresh AFTER the harvest replaces the 0.0
  placeholders with real scalars. List of downstream consumers is the
  harvest task's responsibility, not this runbook.

- AoU AFR LD panel work (M2-POST-M3-01/03/05) is INDEPENDENT of this
  re-fire — MTAG `--skip_mtag --fdr` does not consume the LD reference
  panel. The simplex grid + per-trait Turley scalar computation is purely
  a function of the existing `_mtag_omega_hat.txt`, `_mtag_sigma_hat.txt`,
  and per-trait `_mtag_trait_*.txt` files produced by the Wave 2 fire.

- GWAS Catalog v_lock_M5 refresh (M2-POST-M3-06) deferred per OSF
  amendment §3.

- Possible joblib spec hardening: joblib 1.4.2 was pip-installed into the
  m2-mtag env at quick-260429-utt Task 1 (Rule 3 auto-fix; matches Wave 2
  magma_helpers bypass which also pip-installed joblib). The env spec
  `envs/m2-mtag.yml` was NOT modified per the prep task's hard-lock on
  that file. If Carter elects to bake joblib into the spec for full
  reproducibility, that's a follow-up quick task: add
  `- joblib=1.4.2` under `dependencies:` and rebuild via
  `mamba env update -f envs/m2-mtag.yml -p /rs1/.../m2-mtag --prune`.

- Production-fire `--intervals` choice: quick-260429-utt locked
  `--intervals 2` per Wave 2-D6 hand-off. If Carter wants `--intervals 10`
  (default) for tighter Turley scalars, the smoke gate must be re-run on
  AFR first — `--intervals 10` with `--fit_ss` could expand the post-fit
  grid by ~5x for T=6 (still tractable but worth re-witnessing the wall
  before committing 3 LSF jobs to it).

- Production-fire `--cores` choice: smoke witnessed 4 cores at 260% CPU
  (effective utilization). Bumping to `--cores 8` or 16 unlikely to halve
  wall on a 2-grid-point search; the wall floor is the per-trait
  Spike-Slab optimization (~30 s for T=6 with 100-iteration MLE), not the
  grid traversal (0.029 min). If T=8 EUR grid expands more than expected,
  re-evaluate.
