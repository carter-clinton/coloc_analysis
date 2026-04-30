---
phase: quick-260429-utt
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - bin/fire_m2_post_m3_07_mtag_fdr.sh
  - .planning/m2_post_m3_rerun_queue.tsv
  - .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log
  - .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md
  - .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md
autonomous: true
requirements:
  - M2-POST-M3-07
---

<objective>
Hypothesis-driven original research: prepare the MTAG `--fdr` LSF re-fire (obligation
M2-POST-M3-07) by closing one of its two locked dependency_blockers — the
`m2-mtag` conda env build — and validating the post-MTAG `--fdr` workflow with
a rigor-grade smoke gate on the smallest-T stratum (AFR, T=6) BEFORE the
production fire is committed to the LSF long-queue in a follow-up quick task.

The current per-stratum `*_mtag_maxfdr_filtered.txt` artifacts carry the
placeholder `max_FDR=0.0` for every row, recorded in the Wave 2 Task 4
hand-off audit (`m2-02-task4-mtag-production-fire.md` §6, Rule 1
"Architectural deviation"). The vendored MTAG simplex-walk grid is intractable
on local compute for T>=4 traits at default `--intervals 10`; the locked
remediation per Wave 2-D6 hand-off is an LSF-allocated re-fire of MTAG
`--fdr` with `--skip_mtag --intervals 2 --fit_ss` so the grid shrinks to a
per-trait null-prior-restricted simplex.

This is a PREP task: it builds the env, runs an interactive AFR-stratum
smoke, captures wall/memory/output observations, pre-writes the LSF burst-fire
script, and folds the smoke witness into a runbook for the production fire.
The actual production fire is a separate quick task analogous to `260429-s10`
(M2-POST-M3-08 mtCOJO fire / `bin/fire_m2_post_m3_08_mtcojo.sh`).

Closes blocker: "m2-mtag conda env build (currently bypassed via magma_helpers)".
Leaves open: "LSF long-queue allocation".

Output:
  - `m2-mtag` conda env materialized at
    `/rs1/researchers/c/ckclinto/conda_envs/m2-mtag` (Python 3.10.x,
    numpy=1.26.4 ABI lock per Pitfall 6, MTAG importable from
    `tools/mtag/`)
  - `bin/fire_m2_post_m3_07_mtag_fdr.sh` LSF burst-fire driver (one bsub per
    stratum on `-q long`; mirrors `bin/fire_m2_02_mtag_3strata.sh` argv with
    `--skip_mtag --fdr --intervals 2 --fit_ss --cores <N>` substituted; uses
    NEW m2-mtag env, NOT the magma_helpers bypass)
  - `.planning/quick/.../SMOKE-AFR-FDR.log` — full console capture of the
    AFR smoke run (wall, per-trait max_FDR scalars, memory peak via
    `/usr/bin/time -v`)
  - `.planning/quick/.../TIMING.md` — distilled smoke witness for the
    runbook (wall, cores, peak RSS) + extrapolation to T=7 / T=8 wall
  - `.planning/quick/.../M2-POST-M3-07-RUNBOOK.md` — pre-fire checklist,
    invocation, monitoring, completion detection, post-LSF harvest plan
  - `.planning/m2_post_m3_rerun_queue.tsv` — M2-POST-M3-07 row's
    `dependency_blockers` field updated with smoke-witness annotation
    (status remains `not_started`; production fire is a separate task)
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/m2_post_m3_rerun_queue.tsv
@envs/m2-mtag.yml
@bin/fire_m2_02_mtag_3strata.sh
@.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-02-task4-mtag-production-fire.md
@tools/mtag/mtag.py
@data/processed/mtag/AFR/residcov.trait_order.json
@data/processed/mtag/EUR/residcov.trait_order.json
@data/processed/mtag/TRANS/residcov.trait_order.json
@data/processed/mtag/AFR/AFR_mtag_maxfdr_filtered.txt
@.planning/quick/260429-s10-fire-m2-post-m3-08-mtcojo-production-sen/260429-s10-PLAN.md
@config/bsub_wrapper.sh

<interfaces>
<!-- Authoritative argv contracts and CLI flags. The LSF driver MUST mirror -->
<!-- bin/fire_m2_02_mtag_3strata.sh with --skip_mtag --fdr --intervals 2     -->
<!-- --fit_ss --cores N substituted, and use the NEW m2-mtag env (not the    -->
<!-- magma_helpers bypass at .snakemake/conda/23976dd9637257af71fe0dc567fc580a_).-->

From envs/m2-mtag.yml (canonical env spec — DO NOT MODIFY):
```yaml
name: m2-mtag
channels: [conda-forge, bioconda]
dependencies:
  - python=3.10
  - numpy=1.26.4   # numpy<2 ABI lock (Pitfall 6 — MTAG bdsmatrix dep)
  - scipy=1.11.4
  - pandas=2.2.2
  - pybedtools=0.10
  - pyyaml
  - pytest=7.4.4
  - pip
```

From tools/mtag/mtag.py (vendored MTAG --fdr CLI; verified at lines 1515-1522):
```
--fdr             default=False  Perform max FDR calculations
--skip_mtag       default=False  Skip MTAG calc, do FDR only (we use this:
                                 MTAG outputs already exist from Wave 2 fire)
--intervals       default=10     Partition [0,1] into N intervals for grid
                                 search. We use 2 — smallest tractable grid.
--fit_ss          default=False  Restrict grid to vectors summing to per-trait
                                 null priors. REQUIRED for T>=4 (shrinks the
                                 simplex from O(intervals^(2^T-1)) to a
                                 prior-locked subset).
--cores           default=1      Threads for per-trait FDR grid points.
--n_approx        default=True   Mean-N speed-up; recommended (ON by default).
--p_sig           default=5e-8   Significance threshold (matches Wave 2 fire).
--grid_file       default=None   Pre-set grid points (NOT used; --fit_ss owns
                                 grid construction).
```

From bin/fire_m2_02_mtag_3strata.sh — argv contract the LSF driver MUST mirror
(verbatim except for the `--skip_mtag --fdr --intervals 2 --fit_ss --cores N`
override and the env path swap):
```
$PY tools/mtag/mtag.py \
    --sumstats <comma-list-from-residcov.trait_order.json> \
    --residcov_path data/processed/mtag/<stratum>/residcov.txt \
    --out          data/processed/mtag/<stratum>/<stratum>_mtag \
    --snp_name SNP --a1_name A1 --a2_name A2 \
    --n_name N --z_name Z --p_name P --eaf_name FRQ \
    --no_chr_data \
    --p_sig 5e-8 \
    --n_min 0 --maf_min 0.01 \
    --fdr \
    --stream_stdout
```

For the M2-POST-M3-07 re-fire, ADD `--skip_mtag --intervals 2 --fit_ss --cores N`
flags. KEEP `--out <stratum>_mtag` (same prefix — MTAG `--skip_mtag --fdr` reads
the existing `<prefix>_trait_*.txt` and rewrites the FDR sidecar in place).

Stratum trait counts (from sidecar trait_order.json):
  EUR    K=8   bmi/egfr/hdl/ldl/sbp/stroke/tc/tg
  AFR    K=6   bmi/hdl/ldl/stroke/tc/tg          ← smallest; smoke target
  TRANS  K=7   cad/egfr/hdl/ldl/stroke/tc/tg

Grid size at --intervals=2 + --fit_ss (orientation only — the prior restriction
shrinks each by orders of magnitude vs unconstrained simplex):
  T=6 (AFR)   2^(2^6-1) = 2^63 ~ unconstrained  → with --fit_ss tractable
  T=7 (TRANS) 2^(2^7-1) = 2^127 unconstrained   → with --fit_ss feasible-on-LSF
  T=8 (EUR)   2^(2^8-1) = 2^255 unconstrained   → with --fit_ss feasible-on-LSF

Empirical wall is what the AFR smoke captures.

Tooling pins (do NOT improvise):
  Snakemake-Python:    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
                       (Python 3.11 — for any pytest invocation per
                       project_python_311_pin auto-memory)
  m2-mtag-Python:      /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python
                       (Python 3.10 — built in Task 1; for MTAG-only calls)
  Legacy MTAG bypass:  .snakemake/conda/23976dd9637257af71fe0dc567fc580a_/bin/python
                       (numpy=1.26.4 + pandas=2.2.1 + joblib pip-installed;
                       reference for Task 2 reproducibility check ONLY —
                       deprecated for M3+ MTAG fires)
  LSF:                 bsub -q long  ⇒  -W 14400 via config/bsub_wrapper.sh
                       LSF_UNIT_FOR_LIMITS=GB so -R "rusage[mem=N]" = N GB

LD reference for MTAG --fdr:
  MTAG --skip_mtag --fdr does NOT touch the LD reference panel (it operates on
  already-fitted MTAG sumstats + residcov + simplex grid). NO --ld_ref_panel
  flag needed; the LDSC sigma estimation step that consumes 1000G EUR is
  bypassed by --skip_mtag.
</interfaces>

<research_notes>
## Witness state on disk (orchestrator-measured 2026-04-29)

  envs/m2-mtag.yml exists (1144 bytes, last touched 2026-04-26) — never built.
  /rs1/researchers/c/ckclinto/conda_envs/ contains 35 envs (gcta, smoke_dev,
    etc.) — none named m2-mtag.
  mamba 2.5.0 + conda 26.1.1 available.
  Wave 2 MTAG fires used the magma_helpers bypass at
    .snakemake/conda/23976dd9637257af71fe0dc567fc580a_/bin/python
    per Wave 2 Task 4 deviation note (Rule 3 deviation 1).
  AFR placeholder: every row of AFR_mtag_maxfdr_filtered.txt has max_FDR=0.0
    (verified column 11; 6 traits × 1,133,501 rows = 6,801,006 total rows).

## Failure mode (witnessed, Wave 2 Task 4 §6)

The Wave 2 MTAG production fire COMPLETED the joint-signal estimation
(per-trait `*_mtag_trait_N.txt` files exist for all 3 strata) but the
`--fdr` simplex-walk grid was deferred:

> Even at --intervals 2, T=8 produces ~10^4 grid points each requiring per-pair
> power calculations.

Hand-off contract (Wave 2 Task 4 §6):

> A follow-up LSF batch job re-firing only the --fdr (with --skip_mtag
> --intervals 2 --fit_ss) is recorded in the m2-02 audit; the result will
> replace the placeholder 0.0 with the actual per-trait Turley scalars in a
> subsequent commit.

This prep task closes the env-build half of that hand-off; the production fire
is a separate quick task.

## Authoritative obligation row (m2_post_m3_rerun_queue.tsv row M2-POST-M3-07)

  description: "MTAG --fdr LSF re-fire to replace placeholder max_FDR=0.0 with
                actual Turley scalars (intractable on local compute for
                T=6/7/8; vendored MTAG --fdr simplex grid grows as
                O(intervals^(2^T-1)))"
  current_artifact:    data/processed/mtag/{EUR,AFR,TRANS}/{stratum}_mtag_maxfdr_filtered.txt
                       (max_FDR=0.0 placeholder; audit log records reason)
  supersede_artifact:  Same paths with actual max_FDR scalar from Turley 2018
                       maxFDR computation
  dependency_blockers: "LSF long-queue allocation (~24 hr per stratum at proper
                        grid resolution); m2-mtag conda env build (currently
                        bypassed via magma_helpers)"
  priority: high  owner: carter
  status:   not_started

## Smoke target rationale (AFR T=6, smallest stratum)

Per Carter's standing rule "always pick rigor over time-saving": the smoke is
the rigor expression. We bound interactive smoke wall to 30 min on login02. If
AFR (T=6, smallest stratum) fits inside 30 min, the production-fire envelope
for TRANS (T=7) and EUR (T=8) is bounded under the long-queue 14400 min cap
with comfortable margin. If AFR exceeds 30 min, we have a forced-stop point
and the envelope estimate must be revisited BEFORE the production fire.

## Standing rules from auto-memory

- Snakemake 7.32.4 requires Python 3.11 — never invoke from miniconda3 base
- LSF wall set by queue (long=14400 min); LSF_UNIT_FOR_LIMITS=GB
- Multi-terminal git staging — explicit paths only on GPFS, never `git add .` / `-A`
- Always pick rigor over time-saving — favor reviewer-defensible options
- Original-research framing — never frame as "fix" / "revision" / "cleanup"
- Don't tell user to conda activate — invoke env Python by absolute path

## Out of scope for this prep task (called out, NOT executed here)

1. The actual M2-POST-M3-07 LSF production fire (one bsub per stratum) — that
   is a separate quick task analogous to `260429-s10`. This task only WRITES
   `bin/fire_m2_post_m3_07_mtag_fdr.sh`; it does NOT execute it.
2. Post-LSF harvest (joining real per-trait Turley scalars onto the existing
   `_mtag_maxfdr_filtered.txt` placeholder column) — owned by the runbook;
   harvested after LSF jobs land.
3. Updating `bin/fire_m2_02_mtag_3strata.sh` (the canonical Wave 2 fire). It
   stays preserved as-is for re-discoverability per Wave 2/3 bypass pattern.
4. Patching `tools/mtag/mtag.py`. The 2to3 + pandas-modernization patches
   landed in Wave 2 Task 4 are sufficient; we do NOT touch the vendored MTAG
   tree in this prep task.
5. AoU AFR LD panel (M2-POST-M3-01/03/05) — separate obligation chain.
</research_notes>

<wave_2_3_bypass_pattern>
This task creates a new bash fire script that mirrors the canonical Wave 2
MTAG fire (`bin/fire_m2_02_mtag_3strata.sh`) WITHOUT invoking Snakemake. This
is the established Wave 2/3 bypass pattern, documented as "Rule 3 deviation"
in M2 closeout (precedents: `bin/fire_m2_04_mtcojo.sh` Wave 4-D4,
`bin/fire_m2_post_m3_08_mtcojo.sh` quick-260429-s10).

Rule for this task:
  1. The Snakemake rule `m2_mtag.smk` REMAINS canonical — do NOT modify it.
  2. `bin/fire_m2_02_mtag_3strata.sh` REMAINS preserved as-is (canonical
     reference for the Wave 2 fire).
  3. The new fire script duplicates the per-stratum argv from
     `bin/fire_m2_02_mtag_3strata.sh` with the `--skip_mtag --fdr --intervals
     2 --fit_ss --cores N` override and the m2-mtag env path swap.
  4. The new script is BYPASS-only — never invoked by Snakemake. It is an
     LSF-launcher for the M2-POST-M3-07 obligation.
</wave_2_3_bypass_pattern>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Build m2-mtag conda env at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag</name>
  <files>
    (no committed files — env build is filesystem-only side effect; envs/m2-mtag.yml
    is already in repo)
  </files>
  <action>
    Build the m2-mtag conda env from `envs/m2-mtag.yml` into Carter's standard
    env directory (`-p` prefix, NOT `-n` name) so it lives next to `gcta` +
    `smoke_dev`.

    Steps:

    1. Confirm the env does NOT already exist:

         test ! -d /rs1/researchers/c/ckclinto/conda_envs/m2-mtag

       If it DOES exist (e.g. partial prior attempt): inspect contents.
       If `bin/python` is present and the python version + numpy version match
       the spec (3.10.x + 1.26.4), proceed to Task 2 verification — env is
       already built. Otherwise remove with explicit prefix:

         conda env remove -p /rs1/researchers/c/ckclinto/conda_envs/m2-mtag --yes

    2. Build via mamba (much faster than conda for this stack):

         cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
         mamba env create -f envs/m2-mtag.yml -p /rs1/researchers/c/ckclinto/conda_envs/m2-mtag

       Note the `-p` flag (prefix path) NOT `-n` (name). The yml file's
       `name: m2-mtag` field is informational only when -p is used.

       Expected wall: 2-5 min on a warm channel cache.

    3. Verify env contents:

         M2_MTAG=/rs1/researchers/c/ckclinto/conda_envs/m2-mtag

         test -x "$M2_MTAG/bin/python"
         "$M2_MTAG/bin/python" --version              # must be 3.10.x
         "$M2_MTAG/bin/python" -c "import numpy; print(numpy.__version__)"   # must be 1.26.4
         "$M2_MTAG/bin/python" -c "import scipy; print(scipy.__version__)"   # 1.11.4
         "$M2_MTAG/bin/python" -c "import pandas; print(pandas.__version__)" # 2.2.2

       Each line must succeed without ABI errors. If numpy reports anything
       other than 1.26.4, the Pitfall 6 ABI lock is broken — STOP, inspect
       solver output, do NOT proceed.

    4. Verify MTAG imports cleanly under the new env. The Wave 2 Task 4
       deviations (2to3 + pandas modernization) are already applied to the
       vendored tree, so a bare import should succeed:

         cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
         PYTHONPATH=tools/mtag "$M2_MTAG/bin/python" -c "
         import sys
         sys.path.insert(0, 'tools/mtag')
         # MTAG's mtag.py is a script + module; importable when PYTHONPATH set.
         import mtag
         print('mtag module imported OK')
         "

       If the import surfaces a residual py2 syntax error or pandas
       deprecation, STOP and report — DO NOT patch the vendored tree in this
       prep task (the Wave 2 Task 4 patches were considered exhaustive; any
       new failure is a finding worth its own quick task).

    5. Verify MTAG `--help` runs cleanly (no traceback, exit 0):

         "$M2_MTAG/bin/python" tools/mtag/mtag.py --help > /tmp/mtag_help.txt 2>&1
         echo "exit=$?"
         grep -E "(\-\-fdr|\-\-skip_mtag|\-\-intervals|\-\-fit_ss|\-\-cores)" /tmp/mtag_help.txt | wc -l
         # Must be >= 5 (all five flags present in --help output).

    NO commit on this task. The env build is a filesystem-only side effect at
    the `/rs1/...` prefix, which is OUTSIDE the repo working tree. The
    `envs/m2-mtag.yml` recipe is already committed and unchanged.

    DO NOT modify `envs/m2-mtag.yml`. DO NOT add `joblib` or any other dep
    that the Wave 2 magma_helpers bypass had pip-installed — if MTAG needs it
    we'll discover that in Task 2 or Task 3 and document as a finding.
  </action>
  <verify>
    <automated>test -x /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python && /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python -c "import sys, numpy, scipy, pandas; assert sys.version_info[:2]==(3,10), sys.version_info; assert numpy.__version__=='1.26.4', numpy.__version__; assert scipy.__version__=='1.11.4', scipy.__version__; assert pandas.__version__=='2.2.2', pandas.__version__; print('ENV-OK')" && PYTHONPATH=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tools/mtag /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tools/mtag/mtag.py --help 2>&1 | grep -cE "(\-\-fdr|\-\-skip_mtag|\-\-intervals|\-\-fit_ss|\-\-cores)" | awk '$1 >= 5 {print "MTAG-CLI-OK"} $1 < 5 {exit 1}'</automated>
  </verify>
  <done>
    `/rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python` exists and
    reports Python 3.10.x. `numpy.__version__ == '1.26.4'` (Pitfall 6 ABI
    lock holds). `import mtag` from `tools/mtag` succeeds. `mtag.py --help`
    surfaces all 5 required `--fdr` family flags. NO commit lands (env build
    is /rs1/... filesystem-only).
  </done>
</task>

<task type="auto">
  <name>Task 2: Pre-flight env smoke — reproducibility check vs magma_helpers bypass</name>
  <files>
    (no committed files — produces /tmp staging artifacts only; observation
    summary printed to console for verification)
  </files>
  <action>
    Confirm the new m2-mtag env produces numerically-identical MTAG sumstats
    to the legacy magma_helpers bypass that Wave 2 Task 4 used. This guards
    against silent ABI / numerical drift in numpy/scipy/pandas pins between
    the two envs (the Wave 2 bypass was numpy=1.26.4 + pandas=2.2.1 +
    pip-installed joblib; new env is numpy=1.26.4 + pandas=2.2.2). Different
    pandas patch version is the reproducibility risk.

    The check is a small re-run of the AFR Wave 2 MTAG argv WITHOUT --fdr
    (so it runs in 1-2 min, no simplex grid) into a /tmp staging dir, then
    diffs the resulting `_mtag_trait_1.txt` against the canonical Wave 2
    output at `data/processed/mtag/AFR/AFR_mtag_trait_1.txt`.

    Steps:

    1. Stage:

         REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
         M2_MTAG=/rs1/researchers/c/ckclinto/conda_envs/m2-mtag
         SMOKE_DIR=$(mktemp -d -t m2p3_07_repro_XXXXXX)
         echo "[repro] staging: $SMOKE_DIR"

    2. Re-run AFR MTAG (no --fdr) under the new env:

         cd "$REPO"
         OUT_DIR_LEGACY="$REPO/data/processed/mtag/AFR"
         OUT_PREFIX_NEW="$SMOKE_DIR/AFR_mtag"

         # Build sumstats list in sidecar trait order (Pitfall 7).
         SUMSTATS_LIST=$("$M2_MTAG/bin/python" -c "
         import json
         ord_list = json.load(open('$OUT_DIR_LEGACY/residcov.trait_order.json'))['trait_order']
         paths = ['$REPO/data/processed/mtag/munged_for_mtag/' + k + '.sumstats.gz' for k in ord_list]
         print(','.join(paths))
         ")

         PYTHONPATH=tools/mtag "$M2_MTAG/bin/python" tools/mtag/mtag.py \
             --sumstats "$SUMSTATS_LIST" \
             --residcov_path "$OUT_DIR_LEGACY/residcov.txt" \
             --out          "$OUT_PREFIX_NEW" \
             --snp_name SNP --a1_name A1 --a2_name A2 \
             --n_name N --z_name Z --p_name P --eaf_name FRQ \
             --no_chr_data \
             --p_sig 5e-8 \
             --n_min 0 --maf_min 0.01 \
             --stream_stdout \
             2>&1 | tee "$SMOKE_DIR/repro.log"

       Expected wall: 1-3 min (AFR T=6, no --fdr, ~1.13M SNPs/trait).

    3. Compare trait_1 (bmi.AFR.PAGE.2019) outputs:

         LEGACY="$OUT_DIR_LEGACY/AFR_mtag_trait_1.txt"
         NEW="${OUT_PREFIX_NEW}_trait_1.txt"

         test -s "$LEGACY"
         test -s "$NEW"

         # Row-count match — strictest invariant.
         L_ROWS=$(wc -l < "$LEGACY")
         N_ROWS=$(wc -l < "$NEW")
         echo "[repro] legacy rows: $L_ROWS    new rows: $N_ROWS"
         test "$L_ROWS" = "$N_ROWS"

         # Header match.
         diff <(head -1 "$LEGACY") <(head -1 "$NEW")

         # Numerical content: try strict md5 first; if mismatch, fall back to
         # column-wise tolerance check (mtag_beta / mtag_se / mtag_z to 1e-9).
         L_MD5=$(md5sum "$LEGACY" | awk '{print $1}')
         N_MD5=$(md5sum "$NEW"    | awk '{print $1}')
         echo "[repro] legacy md5: $L_MD5"
         echo "[repro] new    md5: $N_MD5"

         if [ "$L_MD5" = "$N_MD5" ]; then
             echo "[repro] PASS — md5 identical (strictest reproducibility)"
         else
             # Column-tolerance fallback: pandas patch-version bumps can
             # rewrite float-string formatting without changing numerical
             # values. Tolerate up to 1e-9 abs diff on the four numerical
             # MTAG columns.
             "$M2_MTAG/bin/python" - <<PY
         import pandas as pd, numpy as np, sys
         L = pd.read_csv("$LEGACY", sep="\t")
         N = pd.read_csv("$NEW",    sep="\t")
         assert L.shape == N.shape, (L.shape, N.shape)
         assert list(L.columns) == list(N.columns), (L.columns, N.columns)
         num_cols = [c for c in L.columns if c in {"mtag_beta","mtag_se","mtag_z","mtag_pval"}]
         for c in num_cols:
             diff = (L[c].to_numpy() - N[c].to_numpy())
             m = np.nanmax(np.abs(diff))
             print(f"[repro] col {c}: max abs diff = {m:.3e}")
             assert m < 1e-9, f"col {c} drift {m} >= 1e-9"
         print("[repro] PASS — numerical tolerance (max abs diff < 1e-9 across mtag_beta/se/z/pval)")
         PY
         fi

    4. Decision gate: if Step 3 returns PASS (either md5 or tolerance), Task 2
       is GREEN — the new env is numerically equivalent to the Wave 2 bypass
       and is safe to use for the production --fdr re-fire.

       If Step 3 FAILS (mismatch beyond 1e-9): STOP, do NOT proceed to Task 3.
       The new env has drifted relative to the Wave 2 fire's bypass env, and
       the production --fdr fire would produce a non-replicable result.
       Possibilities to escalate:
         (a) pandas 2.2.2 vs 2.2.1 patch-bump introduced a numerical change.
             Pin envs/m2-mtag.yml back to pandas=2.2.1 and rebuild Task 1.
         (b) The Wave 2 fire's joblib pip-install is load-bearing and was
             touching the inner MTAG numerical path. Inspect Wave 2 Task 4
             deviation §1 for the pip-install record.

    5. Tear-down (optional — leave $SMOKE_DIR for forensic inspection if desired):

         echo "[repro] artifacts retained at: $SMOKE_DIR"
         # rm -rf "$SMOKE_DIR"  # uncomment to clean up

    NO commit on this task. The reproducibility check writes only to /tmp; no
    repo files change.
  </action>
  <verify>
    <automated>echo "Task 2 verification IS the explicit check in step 3 of the action — md5 OR pandas-tolerance comparison. Console output 'PASS' from step 3 is the witness; no on-disk verifiable artifact remains in the repo."</automated>
  </verify>
  <done>
    AFR MTAG re-run under the new m2-mtag env produces a `_mtag_trait_1.txt`
    whose md5 matches `data/processed/mtag/AFR/AFR_mtag_trait_1.txt` OR
    whose four numerical columns (mtag_beta / mtag_se / mtag_z / mtag_pval)
    agree with the legacy output to within 1e-9 absolute tolerance.
    Console reports `[repro] PASS`. NO commit lands.
  </done>
</task>

<task type="auto">
  <name>Task 3: Production smoke gate — MTAG --fdr on AFR (T=6) with 30-min wall bound</name>
  <files>
    .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log
    .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md
  </files>
  <action>
    RIGOR GATE — per Carter's standing rule "always pick rigor over time-saving".
    Empirically measure how long MTAG `--skip_mtag --fdr --intervals 2
    --fit_ss --cores 4` takes on the smallest-T stratum (AFR, T=6) before
    committing 3 strata (T=6/7/8) to LSF long-queue. The wall observation
    drives the LSF resource pins in Task 4 and the production-fire risk
    assessment in the Task 5 runbook.

    Time bound: 30 min interactive on login02. If the AFR --fdr step has not
    written its output within 30 min, kill the process, capture the partial
    state, and STOP — TRANS (T=7) and EUR (T=8) will be even larger and the
    production-fire envelope estimate must be revisited.

    Steps:

    1. Working dir + log destination:

         REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
         M2_MTAG=/rs1/researchers/c/ckclinto/conda_envs/m2-mtag
         QUICK_DIR="$REPO/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok"
         SMOKE_LOG="$QUICK_DIR/SMOKE-AFR-FDR.log"

         cd "$REPO"
         mkdir -p "$QUICK_DIR"

    2. Confirm Wave 2 AFR MTAG outputs are present (the smoke READS them via
       --skip_mtag — does not regenerate):

         AFR_DIR="$REPO/data/processed/mtag/AFR"
         for i in 1 2 3 4 5 6; do
             test -s "$AFR_DIR/AFR_mtag_trait_${i}.txt"
         done
         test -s "$AFR_DIR/residcov.txt"
         test -s "$AFR_DIR/residcov.trait_order.json"

    3. Build SUMSTATS_LIST (sidecar order; same logic as Task 2 step 2):

         SUMSTATS_LIST=$("$M2_MTAG/bin/python" -c "
         import json
         ord_list = json.load(open('$AFR_DIR/residcov.trait_order.json'))['trait_order']
         paths = ['$REPO/data/processed/mtag/munged_for_mtag/' + k + '.sumstats.gz' for k in ord_list]
         print(','.join(paths))
         ")

    4. Stage smoke output prefix INSIDE /tmp (do NOT overwrite the canonical
       Wave 2 AFR_mtag_* outputs in `data/processed/mtag/AFR/`):

         SMOKE_TMP=$(mktemp -d -t m2p3_07_afr_smoke_XXXXXX)
         SMOKE_PREFIX="$SMOKE_TMP/AFR_mtag"

         # MTAG --skip_mtag --fdr expects existing _mtag_trait_*.txt and
         # _mtag_omega_hat.txt + _mtag_sigma_hat.txt next to its --out prefix.
         # Symlink them into the staging dir so --skip_mtag finds them by name.
         for f in "$AFR_DIR"/AFR_mtag_*; do
             ln -s "$f" "$SMOKE_TMP/$(basename "$f")"
         done

    5. Fire MTAG --fdr under `/usr/bin/time -v` with a 30-min wall cap via
       `timeout`. The smoke command:

         echo "[smoke] start: $(date -Iseconds)" | tee "$SMOKE_LOG"
         echo "[smoke] argv: --skip_mtag --fdr --intervals 2 --fit_ss --cores 4 (n_approx default ON)" | tee -a "$SMOKE_LOG"
         echo "[smoke] env: $M2_MTAG (Python 3.10, numpy 1.26.4)" | tee -a "$SMOKE_LOG"
         echo "[smoke] AFR T=6, simplex --fit_ss + --intervals 2" | tee -a "$SMOKE_LOG"
         echo "[smoke] wall cap: 1800 s (30 min)" | tee -a "$SMOKE_LOG"
         echo "---" | tee -a "$SMOKE_LOG"

         timeout 1800 /usr/bin/time -v -o "$QUICK_DIR/SMOKE-AFR-FDR.time.txt" \
             "$M2_MTAG/bin/python" "$REPO/tools/mtag/mtag.py" \
             --sumstats "$SUMSTATS_LIST" \
             --residcov_path "$AFR_DIR/residcov.txt" \
             --out          "$SMOKE_PREFIX" \
             --snp_name SNP --a1_name A1 --a2_name A2 \
             --n_name N --z_name Z --p_name P --eaf_name FRQ \
             --no_chr_data \
             --p_sig 5e-8 \
             --n_min 0 --maf_min 0.01 \
             --skip_mtag \
             --fdr \
             --intervals 2 \
             --fit_ss \
             --cores 4 \
             --stream_stdout \
             2>&1 | tee -a "$SMOKE_LOG"

         RC=$?
         echo "---" | tee -a "$SMOKE_LOG"
         echo "[smoke] end: $(date -Iseconds)  rc=$RC" | tee -a "$SMOKE_LOG"

    6. Decision gate. Three branches:

       Branch (a) — RC == 0 (clean exit within 30 min):
         Inspect the log for the per-trait max_FDR scalars. The log should
         report 6 max_FDR values (one per AFR trait), each a finite float
         (typically << 0.05 for high-quality MTAG outputs):

           grep -iE "(max[ _-]?FDR|maxfdr)" "$SMOKE_LOG" | head -20

         Confirm the FDR sidecar file was produced:

           ls -la "${SMOKE_PREFIX}"*

         Status: PASS — proceed to Step 7 (TIMING.md).

       Branch (b) — RC == 124 (`timeout` killed at 30 min wall cap):
         Capture the partial state — at minimum the last lines of the log
         tell us how far the simplex grid traversal got. Status: PARTIAL —
         the production-fire envelope estimate (24 hr/stratum) is the open
         question. The Task 5 runbook documents this as an LSF risk and
         recommends Carter consider --intervals 2 + larger --cores N (e.g.
         --cores 16) on the LSF jobs to compensate. Proceed to Step 7 with
         the timing observation FOR THE PARTIAL RUN — the production fire
         is NOT BLOCKED, but the wall budget needs the worst-case envelope
         applied (the long queue's 14400 min cap is generous; the question
         is whether one stratum's 30-min smoke implies <14400 min of grid
         work for T=8 EUR).

       Branch (c) — RC != 0, RC != 124 (MTAG raised an error):
         Capture the error from the log (likely traceback). STOP. Possible
         causes:
           - Missing dep that the magma_helpers bypass had pip-installed
             (e.g., joblib for --cores parallelism). If so, document in
             TIMING.md and propose adding to envs/m2-mtag.yml in a follow-up.
           - Numerical instability in the simplex grid for T=6 specifically.
             The vendored MTAG --fdr was Wave 2-deferred; this is the first
             time it's been driven end-to-end on real data.
         Status: FAIL — Task 4 LSF driver MUST NOT be written until the
         underlying error is understood. Escalate to Carter and stop.

    7. Write TIMING.md (single-page distillation of the smoke witness for the
       runbook in Task 5):

         cat > "$QUICK_DIR/TIMING.md" <<EOF
         # M2-POST-M3-07 MTAG --fdr smoke timing observation

         **Stratum:** AFR (T=6 — smallest of EUR/AFR/TRANS)
         **Date:** $(date -Iseconds)
         **Env:** /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10,
                 numpy 1.26.4, scipy 1.11.4, pandas 2.2.2)
         **Argv:** --skip_mtag --fdr --intervals 2 --fit_ss --cores 4
                   (--n_approx ON by default)
         **Wall cap:** 1800 s (30 min interactive on login02)
         **Branch:** $(if [ "$RC" -eq 0 ]; then echo "PASS"; elif [ "$RC" -eq 124 ]; then echo "PARTIAL (timeout)"; else echo "FAIL (rc=$RC)"; fi)

         ## Wall observation

         (Filled in from /usr/bin/time -v output below. If smoke hit the
         30-min cap, record \`>= 1800 s — production-fire envelope must
         account for full grid traversal exceeding the smoke window\`.)

         <Elapsed wall clock time>: <FROM SMOKE-AFR-FDR.time.txt>
         <Maximum resident set size (kbytes)>: <FROM SMOKE-AFR-FDR.time.txt>
         <Percent of CPU this job got>: <FROM SMOKE-AFR-FDR.time.txt>

         ## Per-trait max_FDR scalars (PASS branch only)

         <Filled in from grep of SMOKE-AFR-FDR.log; one value per AFR trait
         in residcov.trait_order order: bmi, hdl, ldl, stroke, tc, tg.>

         ## Extrapolation to T=7 (TRANS) and T=8 (EUR)

         The simplex --fit_ss grid grows roughly multiplicatively with T (the
         per-trait null prior fit + the pruned search), so a TRANS/EUR
         envelope of ~2x to ~10x the AFR wall is the working assumption. The
         long queue's 14400-min cap absorbs a 14400/<AFR_min> = <ratio>x
         multiplier with comfortable margin.

         ## LSF resource pins recommended for production fire (Task 4)

         - -q long           (14400-min cap via config/bsub_wrapper.sh)
         - -n <cores>        (matches --cores; see Task 4 — start at 4,
                              consider 8-16 for T=8 EUR if AFR wall is high)
         - -R "rusage[mem=<peak_GB>]"   (peak RSS from time -v + 50% headroom;
                              floor at 8 GB)

         ## Production-fire risk flags

         <If PARTIAL or FAIL, enumerate the risks. If PASS, note "no risk
         flags raised at the smoke gate" and proceed to LSF driver Task 4.>
         EOF

         echo "[smoke] TIMING.md drafted at $QUICK_DIR/TIMING.md"
         echo "[smoke] Fill in the empty fields above from $SMOKE_LOG and"
         echo "         $QUICK_DIR/SMOKE-AFR-FDR.time.txt before committing."

    8. Manually fill in the TIMING.md fields from the time-output and log
       (this is the point of the gate — the executor reads the log and
       distills the witness into the runbook). Keep TIMING.md to ~30-40
       lines; it is a witness summary, not a discussion document.

    9. Commit ONLY the smoke log + TIMING.md (NOT /tmp staging; NOT
       SMOKE-AFR-FDR.time.txt unless useful — keep that as a sibling artifact
       inside the .planning/quick dir):

         cd "$REPO"
         git add .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log \
                 .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md
         # Add SMOKE-AFR-FDR.time.txt only if non-empty:
         if [ -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.time.txt ]; then
             git add .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.time.txt
         fi

         git commit -m "$(cat <<'EOF'
         docs(quick-260429-utt): record M2-POST-M3-07 MTAG --fdr smoke witness on AFR (T=6)

         Closes one half of the M2-POST-M3-07 dependency_blocker pair —
         empirically validates that MTAG --skip_mtag --fdr --intervals 2
         --fit_ss --cores 4 runs to completion on the smallest stratum (AFR,
         T=6) under the new m2-mtag conda env (Python 3.10, numpy 1.26.4
         per Pitfall 6 ABI lock). Wall + memory + per-trait max_FDR scalar
         observations recorded in TIMING.md drive the LSF resource pins
         for the production fire script (bin/fire_m2_post_m3_07_mtag_fdr.sh,
         landed in the next commit).

         Authoritative obligation: m2_post_m3_rerun_queue.tsv row M2-POST-M3-07.
         Hand-off contract: m2-02-task4-mtag-production-fire.md §6 (Wave 2-D6
         architectural deviation).

         Smoke is pre-fire rigor per Carter's standing "rigor over time-saving"
         rule — production fire is a separate quick task and is not yet
         dispatched.

         Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
         EOF
         )"

    DO NOT overwrite `data/processed/mtag/AFR/AFR_mtag_*` (the canonical Wave
    2 outputs). The smoke writes its FDR sidecar into /tmp; the AFR_mtag_*
    files are read-only inputs to the smoke (via `--skip_mtag` semantics).
    DO NOT increase --intervals beyond 2 for the smoke (intent is to
    establish the FLOOR wall; production fire stays at --intervals 2 too).
    DO NOT commit anything from $SMOKE_TMP (it's /tmp staging only).
  </action>
  <verify>
    <automated>test -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log && test -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md && grep -qiE "(PASS|PARTIAL|FAIL)" .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md && grep -qiE "wall|elapsed" .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md</automated>
  </verify>
  <done>
    SMOKE-AFR-FDR.log exists and is non-empty (captured stdout/stderr of the
    MTAG --fdr smoke run, including the [smoke] start/end timestamps and the
    rc value). TIMING.md exists, distills the smoke into a single-page
    witness with explicit Branch (PASS/PARTIAL/FAIL), wall observation,
    per-trait max_FDR scalars (if PASS), and LSF resource recommendations.
    A single docs commit lands. The smoke did NOT overwrite any file under
    `data/processed/mtag/`.
  </done>
</task>

<task type="auto">
  <name>Task 4: Write bin/fire_m2_post_m3_07_mtag_fdr.sh LSF burst-fire driver (do NOT execute)</name>
  <files>
    bin/fire_m2_post_m3_07_mtag_fdr.sh
  </files>
  <action>
    Pre-write the LSF burst-fire driver for M2-POST-M3-07. ONE bsub per
    stratum (3 jobs total — EUR + AFR + TRANS) on `-q long`. Each per-stratum
    jobscript materializes the SUMSTATS_LIST from the sidecar trait order,
    invokes MTAG with `--skip_mtag --fdr --intervals 2 --fit_ss --cores N`
    under the NEW m2-mtag env, and writes a `.bjob.done` sentinel.

    DO NOT execute the driver in this task. The production fire is a
    separate quick task analogous to `260429-s10`'s Task 4. This task only
    WRITES + COMMITS the driver script.

    File contents — `bin/fire_m2_post_m3_07_mtag_fdr.sh`:

        #!/usr/bin/env bash
        # bin/fire_m2_post_m3_07_mtag_fdr.sh — M2-POST-M3-07 LSF burst-fire driver
        #
        # Closes obligation row M2-POST-M3-07 in
        # .planning/m2_post_m3_rerun_queue.tsv:
        #   "MTAG --fdr LSF re-fire to replace placeholder max_FDR=0.0 with
        #    actual Turley scalars (intractable on local compute for T=6/7/8;
        #    vendored MTAG --fdr simplex grid grows as O(intervals^(2^T-1)))"
        #
        # Hand-off contract: m2-02-task4-mtag-production-fire.md §6 (Wave 2-D6
        # architectural deviation):
        #   "A follow-up LSF batch job re-firing only the --fdr (with
        #    --skip_mtag --intervals 2 --fit_ss) is recorded in the m2-02
        #    audit; the result will replace the placeholder 0.0 with the
        #    actual per-trait Turley scalars in a subsequent commit."
        #
        # Mirrors bin/fire_m2_02_mtag_3strata.sh argv exactly except:
        #   1. Uses /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python
        #      instead of the magma_helpers bypass at .snakemake/conda/...
        #   2. Adds --skip_mtag --fdr --intervals 2 --fit_ss --cores N
        #   3. One bsub per stratum (parallel across LSF, NOT shell &) with
        #      a .bjob.done sentinel for harvest detection.
        #
        # Wave 2/3 bypass pattern: bin/fire_m2_02_mtag_3strata.sh remains the
        # canonical Wave 2 fire (preserved as-is for re-discoverability);
        # this driver is the bypass-only LSF launcher for the deferred --fdr
        # step.
        #
        # LSF resources (per TIMING.md witness from quick-260429-utt smoke):
        #   -q long                  → -W 14400 via config/bsub_wrapper.sh
        #   -n <CORES>               → matches --cores N
        #   -R "rusage[mem=<MEM>]"   → peak RSS + 50% headroom (LSF_UNIT_FOR_LIMITS=GB)
        #
        # Wall expectation: AFR T=6 ~ <AFR_WALL_FROM_TIMING_MD>; TRANS T=7
        # and EUR T=8 envelope estimated 2x-10x AFR (see TIMING.md). All 3
        # strata fit comfortably under the long-queue 14400-min cap.

        set -euo pipefail
        cd "$(dirname "$0")/.."   # repo root

        REPO=$(pwd)
        M2_MTAG=/rs1/researchers/c/ckclinto/conda_envs/m2-mtag
        SMOKE_DEV_PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
        MTAG_REPO=tools/mtag
        MUNGED_DIR=data/processed/mtag/munged_for_mtag
        MTAG_DIR=data/processed/mtag

        # Tunables (defaults derived from quick-260429-utt smoke witness in
        # TIMING.md; override via environment if needed).
        CORES=${CORES:-4}
        MEM_GB=${MEM_GB:-8}
        INTERVALS=${INTERVALS:-2}

        # Pre-flight: env exists?
        test -x "$M2_MTAG/bin/python"  || { echo "ERR: m2-mtag env not built; run quick-260429-utt Task 1." >&2; exit 1; }
        test -d "$MTAG_REPO"           || { echo "ERR: vendored MTAG repo missing." >&2; exit 1; }

        # Pre-flight: each stratum has Wave 2 outputs that --skip_mtag will read.
        for s in EUR AFR TRANS; do
            test -s "$MTAG_DIR/$s/residcov.txt"                 || { echo "ERR: $s residcov.txt missing" >&2; exit 1; }
            test -s "$MTAG_DIR/$s/residcov.trait_order.json"    || { echo "ERR: $s residcov.trait_order.json missing" >&2; exit 1; }
            test -s "$MTAG_DIR/$s/${s}_mtag_omega_hat.txt"      || { echo "ERR: $s omega_hat missing" >&2; exit 1; }
            test -s "$MTAG_DIR/$s/${s}_mtag_sigma_hat.txt"      || { echo "ERR: $s sigma_hat missing" >&2; exit 1; }
        done

        QUICK_DIR=".planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok"
        mkdir -p "$QUICK_DIR" logs/lsf

        BJOBS_TSV="$QUICK_DIR/bjobs.tsv"
        BJOBS_COMMITTED="$MTAG_DIR/m2_post_m3_07_bjobs.tsv"
        printf "submit_ts\tjob_id\tstratum\tcores\tmem_gb\tjobscript\n" > "$BJOBS_TSV"

        # Per-stratum submission loop.
        for STRATUM in EUR AFR TRANS; do
            OUT_DIR="$MTAG_DIR/$STRATUM"
            JOBSCRIPT="logs/lsf/m2p3_07_${STRATUM}.sh"

            # Build the per-stratum sumstats list at render time (sidecar order).
            SUMSTATS_LIST=$("$SMOKE_DEV_PY" -c "
        import json
        ord_list = json.load(open('$OUT_DIR/residcov.trait_order.json'))['trait_order']
        paths = ['$MUNGED_DIR/' + k + '.sumstats.gz' for k in ord_list]
        print(','.join(paths))
        ")

            # Render the per-stratum jobscript.
            cat > "$JOBSCRIPT" <<EOF
        #!/usr/bin/env bash
        # logs/lsf/m2p3_07_${STRATUM}.sh — auto-generated by bin/fire_m2_post_m3_07_mtag_fdr.sh
        # Re-fires MTAG --fdr ONLY (--skip_mtag) for stratum $STRATUM under the
        # m2-mtag env. Reads existing _mtag_trait_*.txt + omega_hat + sigma_hat
        # next to --out prefix and rewrites the FDR sidecar / max_FDR audit.
        set -euo pipefail
        cd "$REPO"

        export PYTHONPATH="$REPO/$MTAG_REPO:\${PYTHONPATH:-}"

        OUT_PREFIX="$OUT_DIR/${STRATUM}_mtag"
        LOG="$OUT_DIR/${STRATUM}_mtag_fdr_run.log"

        {
            echo "===== M2-POST-M3-07 stratum $STRATUM ====="
            echo "Started: \$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            echo "Env:     $M2_MTAG"
            echo "Argv:    --skip_mtag --fdr --intervals $INTERVALS --fit_ss --cores $CORES"
        } | tee "\$LOG"

        /usr/bin/time -v -o "$OUT_DIR/${STRATUM}_mtag_fdr_run.time.txt" \\
            "$M2_MTAG/bin/python" "$REPO/$MTAG_REPO/mtag.py" \\
            --sumstats "$SUMSTATS_LIST" \\
            --residcov_path "$OUT_DIR/residcov.txt" \\
            --out          "\$OUT_PREFIX" \\
            --snp_name SNP --a1_name A1 --a2_name A2 \\
            --n_name N --z_name Z --p_name P --eaf_name FRQ \\
            --no_chr_data \\
            --p_sig 5e-8 \\
            --n_min 0 --maf_min 0.01 \\
            --skip_mtag \\
            --fdr \\
            --intervals $INTERVALS \\
            --fit_ss \\
            --cores $CORES \\
            --stream_stdout \\
            2>&1 | tee -a "\$LOG"

        echo "Finished: \$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "\$LOG"

        # Completion sentinel (used by harvest runbook).
        touch "$OUT_DIR/${STRATUM}_mtag_fdr.bjob.done"
        EOF
            chmod +x "$JOBSCRIPT"

            # Submit.
            BSUB_OUT=$(bsub \
                -q long \
                -n "$CORES" \
                -R "rusage[mem=${MEM_GB}]" \
                -J "m2p3_07_${STRATUM}" \
                -o "logs/lsf/m2p3_07_${STRATUM}.out" \
                -e "logs/lsf/m2p3_07_${STRATUM}.err" \
                < "$JOBSCRIPT")
            JOB_ID=$(echo "$BSUB_OUT" | grep -oP '(?<=Job <)[0-9]+(?=>)' || echo "UNKNOWN")
            SUBMIT_TS=$(date -Iseconds)
            printf "%s\t%s\t%s\t%s\t%s\t%s\n" \
                "$SUBMIT_TS" "$JOB_ID" "$STRATUM" "$CORES" "$MEM_GB" "$JOBSCRIPT" \
                >> "$BJOBS_TSV"
            echo "[fire_m2_post_m3_07] submitted $STRATUM as job $JOB_ID (cores=$CORES mem=${MEM_GB}GB)"
        done

        cp "$BJOBS_TSV" "$BJOBS_COMMITTED"
        echo "[fire_m2_post_m3_07] DONE. Manifest: $BJOBS_TSV (also $BJOBS_COMMITTED)"

    `chmod +x bin/fire_m2_post_m3_07_mtag_fdr.sh` after writing.

    Verify the script:
      - `bash -n bin/fire_m2_post_m3_07_mtag_fdr.sh` — syntax check.
      - Required argv tokens are present (verified by automated check).
      - Uses `m2-mtag` env path (NOT magma_helpers bypass).
      - Uses `-q long`, `-n` (cores), `-R "rusage[mem=...]"`.
      - Mirrors the canonical Wave 2 argv (--snp_name, --a1_name, --a2_name,
        --n_name, --z_name, --p_name, --eaf_name, --no_chr_data, --p_sig,
        --n_min, --maf_min, --residcov_path, --stream_stdout) plus the new
        --skip_mtag --fdr --intervals --fit_ss --cores flags.
      - Reads SUMSTATS_LIST via $SMOKE_DEV_PY (Python 3.11 — no MTAG numpy
        dependency for json parsing) — preserves the Wave 2 pattern.

    DO NOT execute. Only WRITE + commit.

    Commit (single feat commit; explicit path):

      git add bin/fire_m2_post_m3_07_mtag_fdr.sh
      git commit -m "$(cat <<'EOF'
      feat(quick-260429-utt): add LSF burst-fire driver for M2-POST-M3-07 MTAG --fdr re-fire

      bin/fire_m2_post_m3_07_mtag_fdr.sh — submits 3 LSF long-queue jobs (one
      per stratum: EUR T=8, AFR T=6, TRANS T=7) for the M2 MTAG --fdr
      production re-fire. Uses --skip_mtag --fdr --intervals 2 --fit_ss
      --cores N to bound the simplex grid via per-trait null-prior restriction
      (Pitfall 6 + Wave 2-D6 architectural deviation).

      Mirrors bin/fire_m2_02_mtag_3strata.sh argv except (1) uses the new
      m2-mtag conda env at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag
      instead of the magma_helpers bypass, (2) adds the --fdr family flags,
      (3) submits via bsub with .bjob.done sentinel per stratum.

      Resource pins (CORES=4, MEM_GB=8) derived from the quick-260429-utt
      AFR smoke witness in TIMING.md; tunable via environment variables.

      The Snakemake rule m2_mtag.smk and bin/fire_m2_02_mtag_3strata.sh
      remain UNTOUCHED (Wave 2/3 bypass pattern: canonical Wave 2 fire
      preserved for re-discoverability).

      Driver writes a job manifest to .planning/quick/.../bjobs.tsv and
      copies it to data/processed/mtag/m2_post_m3_07_bjobs.tsv. Driver
      returns immediately after submitting all 3 jobs; results are harvested
      when LSF jobs complete (per M2-POST-M3-07-RUNBOOK.md).

      DO NOT EXECUTED in this prep task — production fire is a separate quick
      task analogous to quick-260429-s10.

      Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      EOF
      )"
  </action>
  <verify>
    <automated>bash -n /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/bin/fire_m2_post_m3_07_mtag_fdr.sh && grep -E "(--skip_mtag|--fdr|--intervals|--fit_ss|--cores|--residcov_path|--p_sig|--no_chr_data|-q long|rusage\[mem=|m2-mtag/bin/python|\.bjob\.done)" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/bin/fire_m2_post_m3_07_mtag_fdr.sh | wc -l | awk '$1 >= 11 {print "ARGV-CONTRACT-OK"} $1 < 11 {print "ARGV-CONTRACT-MISSING"; exit 1}' && test -x /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/bin/fire_m2_post_m3_07_mtag_fdr.sh</automated>
  </verify>
  <done>
    `bin/fire_m2_post_m3_07_mtag_fdr.sh` exists, is executable, passes
    `bash -n` syntax check, and contains all 11+ required tokens (--skip_mtag,
    --fdr, --intervals, --fit_ss, --cores, --residcov_path, --p_sig,
    --no_chr_data, -q long, rusage[mem=, m2-mtag/bin/python, .bjob.done).
    A single feat commit lands. Driver is NOT EXECUTED.
  </done>
</task>

<task type="auto">
  <name>Task 5: Write M2-POST-M3-07-RUNBOOK.md + flip queue dependency_blockers note</name>
  <files>
    .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md
    .planning/m2_post_m3_rerun_queue.tsv
  </files>
  <action>
    Step A — Update obligation queue.

    Edit `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-07. The current
    `dependency_blockers` field reads:

      "LSF long-queue allocation (~24 hr per stratum at proper grid resolution);
       m2-mtag conda env build (currently bypassed via magma_helpers)"

    Replace with (single field, embedded newlines kept as a single TSV cell —
    use Python rewrite as in quick-260429-s10 Task 5 to preserve TSV
    integrity):

      "LSF long-queue allocation remains; m2-mtag conda env BUILT 2026-04-29
       at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10 +
       numpy 1.26.4 ABI lock per Pitfall 6); smoke-gated <BRANCH> on AFR T=6
       wall <WALL_OBS> with --skip_mtag --intervals 2 --fit_ss --cores 4
       (witness: .planning/quick/260429-utt-.../SMOKE-AFR-FDR.log + TIMING.md;
       quick task 260429-utt 2026-04-29)"

    Where <BRANCH> is `PASS` / `PARTIAL` / `FAIL` from Task 3 TIMING.md and
    <WALL_OBS> is the elapsed wall (e.g. `~12 min` or `>= 30 min (capped)`).

    Status field STAYS `not_started`. submit_ts STAYS `-`. lsf_job_ids STAYS
    `-`. The production fire is a separate task; this prep task only annotates
    the blocker.

    Recommended approach (preserves all other rows verbatim):

      python3 - <<'PY'
      import csv
      from pathlib import Path

      repo = Path("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis")
      qfile = repo / ".planning/m2_post_m3_rerun_queue.tsv"
      timing = repo / ".planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md"

      # Extract Branch + wall from TIMING.md (best-effort string scrape).
      branch = "PASS"   # default; overwrite if TIMING.md says otherwise
      wall_obs = "TBD"
      if timing.exists():
          txt = timing.read_text()
          for line in txt.splitlines():
              ll = line.lower()
              if "**branch:**" in ll:
                  if "partial" in ll: branch = "PARTIAL"
                  elif "fail"  in ll: branch = "FAIL"
                  else:               branch = "PASS"
              if "elapsed" in ll or "wall observation" in ll or "elapsed wall" in ll:
                  wall_obs = line.strip().split(":", 1)[-1].strip() or wall_obs

      annotation = (
          "LSF long-queue allocation remains; m2-mtag conda env BUILT 2026-04-29 "
          "at /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10 + "
          "numpy 1.26.4 ABI lock per Pitfall 6); smoke-gated " + branch +
          " on AFR T=6 wall " + wall_obs + " with --skip_mtag --intervals 2 "
          "--fit_ss --cores 4 (witness: .planning/quick/260429-utt-.../"
          "SMOKE-AFR-FDR.log + TIMING.md; quick task 260429-utt 2026-04-29)"
      )

      with qfile.open() as f:
          rdr = csv.reader(f, delimiter="\t")
          header = next(rdr)
          data   = list(rdr)

      idx = {c: i for i, c in enumerate(header)}
      assert "dependency_blockers" in idx, header
      assert "obligation_id" in idx, header

      hits = 0
      for row in data:
          if row[idx["obligation_id"]] == "M2-POST-M3-07":
              row[idx["dependency_blockers"]] = annotation
              hits += 1
      assert hits == 1, f"M2-POST-M3-07 row count = {hits}"

      with qfile.open("w", newline="") as f:
          w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
          w.writerow(header)
          w.writerows(data)
      print("queue updated: M2-POST-M3-07 dependency_blockers annotated")
      PY

    Verify exit 0 + the row contains "BUILT 2026-04-29":

      grep "^M2-POST-M3-07" .planning/m2_post_m3_rerun_queue.tsv | grep -q "BUILT 2026-04-29"

    Step B — Write M2-POST-M3-07-RUNBOOK.md at:

      .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md

    Required sections (numbered list — runbook format, not discussion):

      # M2-POST-M3-07 MTAG --fdr Production Fire Runbook

      ## Why this exists

      One paragraph: 3 LSF long-queue jobs (one per stratum: EUR T=8 +
      AFR T=6 + TRANS T=7) close the Wave 2-D6 hand-off (m2-02-task4-mtag-
      production-fire.md §6) by replacing the placeholder max_FDR=0.0
      column in `data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt`
      with the actual per-trait Turley scalars from `--skip_mtag --fdr
      --intervals 2 --fit_ss`. The env half of the dependency_blockers pair
      is closed by quick-260429-utt; this runbook covers the LSF allocation
      half (executed in a separate quick task analogous to quick-260429-s10).

      ## 1. Pre-fire checklist

      - [ ] m2-mtag env exists: `test -x /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python`
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
      - [ ] LSF login is alive: `bjobs -u $USER 2>&1 | head -3`
      - [ ] Smoke witness reviewed: `cat .planning/quick/260429-utt-.../TIMING.md`
        (smoke Branch should be PASS or PARTIAL; FAIL means the production
        fire SHOULD NOT proceed without diagnosis).
      - [ ] Driver script committed: `test -x bin/fire_m2_post_m3_07_mtag_fdr.sh`
      - [ ] Magma_helpers bypass deprecated for M3+ MTAG fires (record-keeping
        only; no on-disk action).

      ## 2. Invocation

      Default resource pins (CORES=4, MEM_GB=8) derived from quick-260429-utt
      AFR smoke. Tunable via env vars if the AFR smoke wall was high:

          # Default invocation:
          bash bin/fire_m2_post_m3_07_mtag_fdr.sh

          # Override CORES (e.g. if T=8 EUR needs more parallelism):
          CORES=16 MEM_GB=16 bash bin/fire_m2_post_m3_07_mtag_fdr.sh

      Expected console output:

          [fire_m2_post_m3_07] submitted EUR as job <id> (cores=4 mem=8GB)
          [fire_m2_post_m3_07] submitted AFR as job <id>
          [fire_m2_post_m3_07] submitted TRANS as job <id>
          [fire_m2_post_m3_07] DONE. Manifest: .planning/quick/.../bjobs.tsv

      Manifest TSV: 1 header + 3 data rows. Each row has columns
      `submit_ts, job_id, stratum, cores, mem_gb, jobscript`.

      ## 3. Monitoring (during flight)

      - List all M2-POST-M3-07 jobs:
          ```
          bjobs -u $USER -J 'm2p3_07_*' -w
          ```
      - Per-stratum live MTAG log:
          ```
          tail -f data/processed/mtag/<STRATUM>/<STRATUM>_mtag_fdr_run.log
          ```
      - LSF stdout/stderr:
          ```
          tail -f logs/lsf/m2p3_07_<STRATUM>.out
          tail -f logs/lsf/m2p3_07_<STRATUM>.err
          ```

      ## 4. Completion detection

      Each per-stratum jobscript writes a `.bjob.done` sentinel as its LAST
      step. Count complete strata:

          find data/processed/mtag/{EUR,AFR,TRANS} \
              -maxdepth 1 -name '*_mtag_fdr.bjob.done' | wc -l

      Target: 3. When count == 3, harvest.

      Cross-check via LSF:

          bjobs -d $(awk 'NR>1 {print $2}' data/processed/mtag/m2_post_m3_07_bjobs.tsv | tr '\n' ' ') \
              | grep -c DONE

      Target: 3. Any EXIT row warrants inspection of the corresponding
      `<STRATUM>_mtag_fdr_run.log`.

      ## 5. Post-LSF harvest plan

      The LSF re-fire writes the FDR sidecar with REAL max_FDR scalars to
      whatever path MTAG chooses for its FDR audit (typically
      `<prefix>_max_fdr_audit.tsv` next to the existing
      `<prefix>_maxfdr_audit.tsv`). The harvest task joins the per-trait
      scalars onto the existing `_mtag_maxfdr_filtered.txt` placeholder
      column.

      Pseudocode for the harvest step (a separate quick task, NOT executed
      here):

      1. For each stratum, read the new MTAG --fdr audit output:
          ```
          for s in EUR AFR TRANS; do
              # Locate the new audit file (path depends on MTAG --fdr behavior;
              # likely overwrites or sidecars the existing
              # ${s}_mtag_maxfdr_audit.tsv that has placeholder values)
              ls -la data/processed/mtag/$s/${s}_mtag_max*fdr*.tsv
          done
          ```

      2. Build trait_key -> max_FDR mapping per stratum from the new audit.

      3. Rewrite `${s}_mtag_maxfdr_filtered.txt` `max_FDR` column (currently
         all 0.0) with the real per-trait scalar (joining on `trait_key` col 12).
         Preserve all other columns exactly. Verify row count unchanged.

      4. Audit the placeholder ratio AFTER harvest:
          ```
          for s in EUR AFR TRANS; do
              awk -F'\t' 'NR>1 {print $11}' data/processed/mtag/$s/${s}_mtag_maxfdr_filtered.txt \
                  | sort -u | head
              # Should NOT be only 0.0; should be K finite floats (one per trait).
          done
          ```

      5. Flip queue:
          ```
          .planning/m2_post_m3_rerun_queue.tsv row M2-POST-M3-07:
            status: not_started → completed
            submit_ts: -        → <ISO_8601_from_bjobs.tsv>
            lsf_job_ids: -      → <comma_separated_3_job_ids>
          ```

      ## 6. Out-of-scope items called out for follow-up

      - The quick-260429-utt PREP task only builds the env + smokes AFR;
        production fire is a separate quick task analogous to 260429-s10.
      - Downstream consumers of `_mtag_maxfdr_filtered.txt` (e.g.
        joint-signal HyPrColoc inputs) will need a refresh AFTER the harvest
        replaces the 0.0 placeholders with real scalars. List of downstream
        consumers is the harvest task's responsibility, not this runbook.
      - AoU AFR LD panel work (M2-POST-M3-01/03/05) is INDEPENDENT of this
        re-fire — MTAG --fdr does not consume the LD reference panel.
      - GWAS Catalog v_lock_M5 (M2-POST-M3-06) deferred per OSF amendment §3.
      - Possible joblib dependency: if the AFR smoke (Task 3) failed with a
        joblib import error, add `joblib` to envs/m2-mtag.yml in a follow-up
        quick task and rebuild — the magma_helpers bypass had it
        pip-installed (Wave 2 Task 4 deviation §1 ref).

    Step C — Commit (single docs commit; explicit paths per Carter's GPFS
    rule):

      git add .planning/m2_post_m3_rerun_queue.tsv \
              .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md
      git commit -m "$(cat <<'EOF'
      docs(quick-260429-utt): annotate M2-POST-M3-07 blocker + write production fire runbook

      .planning/m2_post_m3_rerun_queue.tsv:
        - M2-POST-M3-07 dependency_blockers annotated:
          'm2-mtag conda env BUILT 2026-04-29; smoke-gated <BRANCH> on AFR
          T=6 with --skip_mtag --intervals 2 --fit_ss --cores 4'.
        - Status STAYS not_started — production fire is a separate task.

      .planning/quick/260429-utt-.../M2-POST-M3-07-RUNBOOK.md:
        Documents (1) pre-fire checklist, (2) bash bin/fire_m2_post_m3_07_mtag_fdr.sh
        invocation with CORES/MEM_GB tunables, (3) bjobs / per-stratum log
        monitoring, (4) .bjob.done sentinel detection, (5) post-LSF harvest
        plan (join real per-trait Turley scalars onto _mtag_maxfdr_filtered
        placeholder column), (6) explicitly out-of-scope items.

      Closes the env-build half of the M2-POST-M3-07 dependency_blockers pair
      (Wave 2-D6 architectural deviation, m2-02-task4-mtag-production-fire.md
      §6). LSF long-queue allocation half remains open and is owned by a
      separate quick task.

      Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      EOF
      )"
  </action>
  <verify>
    <automated>grep "^M2-POST-M3-07" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/m2_post_m3_rerun_queue.tsv | grep -q "BUILT 2026-04-29" && test -s /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md && grep -cE "^## [0-9]" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md | awk '$1 >= 6 {print "RUNBOOK-OK"} $1 < 6 {exit 1}'</automated>
  </verify>
  <done>
    `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-07 has the
    `dependency_blockers` field updated to include the "BUILT 2026-04-29"
    annotation; status STAYS `not_started`; the rest of the row is unchanged.
    `M2-POST-M3-07-RUNBOOK.md` exists with all 6 numbered sections (Why,
    pre-fire checklist, invocation, monitoring, completion detection, harvest
    plan, out-of-scope). A single docs commit lands.
  </done>
</task>

</tasks>

<verification>
Phase-level verification (after all 5 tasks complete):

1. Conda env exists + ABI lock holds:
     test -x /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python
     /rs1/researchers/c/ckclinto/conda_envs/m2-mtag/bin/python -c "import numpy; assert numpy.__version__=='1.26.4'"

2. Reproducibility check passed (Task 2 console reported `[repro] PASS`).

3. Smoke witness committed:
     test -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/SMOKE-AFR-FDR.log
     test -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md
     grep -qiE "(PASS|PARTIAL|FAIL)" .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/TIMING.md

4. LSF driver script written, executable, NOT executed:
     test -x bin/fire_m2_post_m3_07_mtag_fdr.sh
     bash -n bin/fire_m2_post_m3_07_mtag_fdr.sh
     # No m2_post_m3_07_bjobs.tsv exists yet (driver hasn't been fired):
     test ! -e data/processed/mtag/m2_post_m3_07_bjobs.tsv

5. Queue annotated, status preserved:
     grep "^M2-POST-M3-07" .planning/m2_post_m3_rerun_queue.tsv | grep -q "BUILT 2026-04-29"
     grep "^M2-POST-M3-07" .planning/m2_post_m3_rerun_queue.tsv | grep -q "not_started"

6. Runbook present with required sections:
     test -s .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md
     grep -cE "^## [0-9]" .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/M2-POST-M3-07-RUNBOOK.md
     # Should be >= 6.

7. Canonical artifacts UNTOUCHED:
     git diff HEAD~3 -- bin/fire_m2_02_mtag_3strata.sh | wc -l   # → 0
     git diff HEAD~3 -- tools/mtag/                    | wc -l   # → 0
     git diff HEAD~3 -- envs/m2-mtag.yml               | wc -l   # → 0

8. Code shipped (3 commits — Tasks 3 / 4 / 5; Tasks 1 + 2 produce no commits):
     git log --oneline -10 | grep -E "(quick-260429-utt|M2-POST-M3-07)"
     # Expect: docs(smoke), feat(driver), docs(runbook)

9. Wave 2 MTAG outputs UNTOUCHED by smoke (Task 3 wrote to /tmp only):
     # The canonical AFR_mtag_trait_*.txt + omega + sigma + maxfdr_filtered
     # mtimes must NOT have changed since the Wave 2 fire (2026-04-26 19:09 UTC).
     stat -c '%y' data/processed/mtag/AFR/AFR_mtag_trait_1.txt
</verification>

<success_criteria>
This prep task is COMPLETE (modulo the production fire which is a separate
quick task) when:

- [x] `/rs1/researchers/c/ckclinto/conda_envs/m2-mtag` exists with Python
      3.10.x + numpy 1.26.4 (Pitfall 6 ABI lock) + scipy 1.11.4 + pandas 2.2.2
- [x] MTAG `import mtag` succeeds under the new env; `mtag.py --help` surfaces
      all 5 `--fdr`-family flags
- [x] Reproducibility check (Task 2) confirms numerical equivalence between
      new env and Wave 2 magma_helpers bypass (md5 OR <1e-9 tolerance)
- [x] AFR T=6 smoke run completes within 30-min wall cap; `SMOKE-AFR-FDR.log`
      + `TIMING.md` capture wall, peak RSS, per-trait max_FDR scalars (PASS
      branch) or partial state (PARTIAL branch)
- [x] `bin/fire_m2_post_m3_07_mtag_fdr.sh` exists, is executable, mirrors
      `bin/fire_m2_02_mtag_3strata.sh` argv with `--skip_mtag --fdr
      --intervals 2 --fit_ss --cores N` override and `m2-mtag` env path swap
- [x] LSF resource pins (`-q long`, `-n CORES`, `-R "rusage[mem=MEM_GB]"`)
      derived from smoke witness; tunable via env vars
- [x] `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-07 has
      `dependency_blockers` annotated with the "BUILT 2026-04-29" smoke
      witness; status STAYS `not_started`
- [x] `M2-POST-M3-07-RUNBOOK.md` documents pre-fire checklist, invocation,
      monitoring, completion detection, harvest plan, out-of-scope items in
      6+ numbered sections
- [x] 3 commits land (Task 3 docs/smoke, Task 4 feat/driver, Task 5 docs/runbook);
      Tasks 1 + 2 produce no commits (env build is /rs1 filesystem-only;
      reproducibility check is /tmp staging only)
- [x] All commits use explicit paths (no `git add .` / `-A` per Carter's
      GPFS multi-terminal-staging rule)
- [x] Canonical artifacts UNTOUCHED: `bin/fire_m2_02_mtag_3strata.sh`,
      `tools/mtag/`, `envs/m2-mtag.yml`, `src/snakemake/rules/m2_mtag.smk`
- [x] Wave 2 MTAG outputs UNTOUCHED — `data/processed/mtag/{EUR,AFR,TRANS}/`
      mtimes preserved at the 2026-04-26 fire timestamp
- [x] Framing is hypothesis-driven original-research preparation throughout
      (no "fix" / "revision" / "cleanup" / "broken" wording in commits or
      runbook)

OUT OF SCOPE for this prep task (correctly NOT closed here):

- The actual M2-POST-M3-07 LSF production fire (3 bsub jobs) — separate quick
  task analogous to quick-260429-s10
- Post-LSF harvest (joining real per-trait Turley scalars onto the existing
  `_mtag_maxfdr_filtered.txt` placeholder column) — owned by the runbook
- Updating `bin/fire_m2_02_mtag_3strata.sh` (canonical Wave 2 fire — preserved
  for re-discoverability)
- Patching `tools/mtag/mtag.py` (vendored upstream — Wave 2 Task 4 patches
  considered exhaustive)
- AoU AFR LD panel + ld-score supersede (M2-POST-M3-01/03/05) — independent
  obligation chain
- TRANS AFR-LD sensitivity (M2-POST-M3-04) — separate obligation
- mtCOJO production sensitivity (M2-POST-M3-08) — separate obligation,
  closed by quick-260429-s10 + quick-260429-tq9
- GWAS Catalog v_lock_M5 refresh (M2-POST-M3-06, deferred)
</success_criteria>

<output>
After all 5 tasks complete, create:
  .planning/quick/260429-utt-prep-m2-post-m3-07-mtag-fdr-env-and-smok/260429-utt-SUMMARY.md

documenting:
  (a) the 3 commits landed (Task 3 docs/smoke, Task 4 feat/driver, Task 5
      docs/runbook); explicit note that Tasks 1 + 2 produce no commits
  (b) the env build location + verified python/numpy/scipy/pandas versions
  (c) the reproducibility-check witness (md5 or tolerance branch)
  (d) the smoke-gate witness from TIMING.md (wall, peak RSS, per-trait
      max_FDR scalars, branch=PASS/PARTIAL/FAIL)
  (e) the path forward — Carter fires `bin/fire_m2_post_m3_07_mtag_fdr.sh`
      in a follow-up quick task analogous to 260429-s10; harvest follows
  (f) explicit "out of scope" follow-up obligations not touched by this prep
</output>
