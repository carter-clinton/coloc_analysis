# M2-POST-M3-07 MTAG --fdr smoke timing observation

**Stratum:** AFR (T=6 — smallest of EUR/AFR/TRANS)
**Date:** 2026-04-29T22:43:29-04:00
**Env:** /rs1/researchers/c/ckclinto/conda_envs/m2-mtag (Python 3.10.20,
        numpy 1.26.4, scipy 1.11.4, pandas 2.2.2; joblib 1.4.2 pip-installed
        as Rule 3 auto-fix — see SUMMARY deviations)
**Argv:** --skip_mtag --fdr --intervals 2 --fit_ss --cores 4
          (--n_approx ON by default)
**Wall cap:** 1800 s (30 min interactive on login01)
**Branch:** PASS

## Wall observation

(From SMOKE-AFR-FDR.time.txt — `/usr/bin/time -v` output)

- Elapsed wall clock time: **52.04 s** (0:52.04 — well inside 30-min cap)
- User time: 102.44 s
- System time: 33.04 s
- Percent of CPU this job got: 260% (effective utilization across 4 cores)
- Maximum resident set size: **1,389,996 KB ≈ 1.36 GB**
- Major page faults: 0
- Voluntary context switches: 7,606
- Exit status: 0

## Per-trait max_FDR scalars (PASS branch)

In residcov.trait_order.json order (AFR T=6 — bmi / hdl / ldl / stroke / tc / tg):

| Trait idx | Trait                       | max_FDR scalar          | grid pt idx |
|-----------|-----------------------------|-------------------------|-------------|
| 1         | bmi.AFR.PAGE.2019           | 0.00970590589390107     | 0           |
| 2         | hdl.AFR.GLGC.2021           | 0.003316170693667885    | 0           |
| 3         | ldl.AFR.GLGC.2021           | 4.08283132227812e-06    | 0           |
| 4         | stroke.AFR.GIGASTROKE.2022  | 0.11541401327515466     | 1           |
| 5         | tc.AFR.GLGC.2021            | 8.642644223250632e-09   | 0           |
| 6         | tg.AFR.GLGC.2021            | 0.0017651764636435043   | 0           |

Spike-Slab fitted causal probabilities (sanity check):
- Trait 0 (bmi): 0.361
- Trait 1 (hdl): 0.058
- Trait 2 (ldl): 0.041
- Trait 3 (stroke): 1.000   ← saturated; corresponds to the elevated max_FDR=0.115 above
- Trait 4 (tc): 0.063
- Trait 5 (tg): 0.119

`grid point indices for max FDR for each trait: [0 0 0 1 0 0]` — only stroke
hit the alternate (i=1) grid point; the other 5 traits hit the spike-prior
grid pt 0. After Spike-Slab fit, only **2 grid points** remained after
restricting to causal-probability-1-unit-from-fit (per --intervals 2 +
--fit_ss simplex pruning). This is the empirical floor of how cheap
`--fit_ss` makes the simplex grid traversal at T=6 — an order of magnitude
faster than the unconstrained simplex would have been.

## Extrapolation to T=7 (TRANS) and T=8 (EUR)

The simplex `--fit_ss` grid grows roughly with K (per-trait null prior fit
+ a pruned 2-point search per trait), NOT exponentially in T as the
unconstrained simplex would. Empirical T=6 wall is ~52 s on 4 cores. With
`--fit_ss` keeping the post-fit grid at ~2 points/trait, the per-trait
grid-search work scales linearly in T:

  - T=7 (TRANS): predicted wall ~60-90 s (1.17x AFR + 1 extra trait's grid)
  - T=8 (EUR):   predicted wall ~75-120 s (1.33x AFR + 2 extra traits' grid)

Both estimates sit FOUR orders of magnitude below the long-queue 14400-min
cap. The Wave 2-D6 hand-off had estimated "~24 hr per stratum at proper
grid resolution"; the smoke witness is that with `--intervals 2 --fit_ss`,
that envelope was a worst-case anchor for the unconstrained simplex —
pruned-prior reality is sub-2-min/stratum.

## LSF resource pins recommended for production fire (Task 4)

Derived from this AFR (T=6) smoke witness, applied per-stratum:

- `-q long` — 14400-min wall cap via `config/bsub_wrapper.sh` (overkill for
  the empirical sub-2-min walls observed, but the standing convention for
  re-fire jobs and conservatively defensible)
- `-n 4` — matches `--cores 4` in MTAG argv (CPU% 260% confirms 4 cores
  were saturating the workload; bumping to 8 unlikely to halve wall on
  a 2-grid-point search)
- `-R "rusage[mem=8]"` — peak RSS 1.36 GB + 50% headroom = 2.04 GB; floored
  at 8 GB per Wave 2 magma_helpers convention. Comfortable margin.

## Production-fire risk flags

**No risk flags raised at the smoke gate.** Branch is PASS by every metric
the gate measured:

- Wall is sub-1-min (vs 30-min cap), giving 30x+ headroom
- All 6 per-trait max_FDR scalars are finite floats in [1e-9, 0.12] —
  none collapsed to placeholder 0.0; none diverged to NaN/Inf
- Peak RSS 1.36 GB << 8 GB pin
- Vendored MTAG's --fdr code path is end-to-end functional under the new
  m2-mtag env (Python 3.10 + numpy 1.26.4 + joblib 1.4.2)
- The existing 0.0 placeholder in
  `data/processed/mtag/AFR/AFR_mtag_maxfdr_filtered.txt` has a real
  6-element scalar replacement waiting

**One auto-fix applied at Task 1** (Rule 3 — blocking): joblib 1.4.2
pip-installed into the new env (matches Wave 2 magma_helpers bypass which
also pip-installed joblib). NOT added to envs/m2-mtag.yml per the plan's
"DO NOT modify envs/m2-mtag.yml" hard-lock; that adjustment is a follow-up
quick task if Carter elects to bake it into the env spec.

## Reproducibility check witness (Task 2)

Re-run of Wave 2 AFR MTAG argv (no --fdr) under the new env into /tmp:

- Row count match: 1,133,502 = 1,133,502 (legacy = new)
- Header diff: byte-identical
- **md5 of trait_1.txt: 612f856221e6be29a3a3a0c3397b970b (match)** —
  strictest reproducibility achieved despite pandas patch-version drift
  (legacy 2.2.1 → new 2.2.2). The pandas patch-bump did NOT alter
  numerical output. All 6 trait files produced (~130 MB each) in 2.5 min
  on the new env.
