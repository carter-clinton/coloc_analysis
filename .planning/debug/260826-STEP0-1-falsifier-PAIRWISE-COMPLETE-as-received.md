# STEP 0 + STEP 1 — the plink PAIRWISE-COMPLETE FALSIFIER **PASSED**; the instrument's premise is CONFIRMED (as received, 2026-08-26)

> Provenance: AoU browser agent's verbatim reports, pasted by Carter 2026-08-25 ~21:40 and ~21:48 EDT
> (2026-08-26 01:40 / 01:48 UTC), during the VM session Carter started for the pairwise-completeness
> sweep. AS-RECEIVED transcription. This record banks the answer to the question the whole instrument
> rested on — and which the 260825-qpf remediation existed to make testable.

## STEP 0 — freshness + environment (all gates pass)

**Repo.** `git pull --ff-only` fast-forwarded `7c310e5..769afa6` (21 commits, 21 files). HEAD is a
`quick-260825-qpf` commit, so the VM runs the **remediated** instrument, not the reviewed-but-unfixed
one. `src/python/pairwise_completeness_scan.py` = 58,165 B, 1,382 lines; its test file 2,556 lines.

**plink pin**, read off the version line rather than a `which` fallback:

```
/home/jupyter/bin/plink1.9
PLINK v1.90b7.2 64-bit (11 Dec 2023)
```

Exact match to the pin, and it **survived the VM stop/start** because `~/bin` is on the reattached
persistent disk — so no install was needed and the browser agent's download-and-execute refusal
never arose.

**Disk.** 984G total / 417G used / **527G avail** / 45%. The Stage B leftovers, including the
forensic `m2_region_00057.ld.bin`, are untouched.

### ⭐ `.fam` founder count — this CLOSES review finding F1

```
73122
73122
```

**Every sample in the cohort is a founder** (`$3=="0" && $4=="0"`). Codex's F1 warned that plink's LD
considers founders only by default while the scanner counts all `.fam` rows; the accepted answer was
"moot, because production passes `--nonfounders`". The measured answer is **stronger**: with zero
non-founders the two sample sets are *identical*, so the scanner's all-samples policy is correct
whether or not the flag is present. F1 is closed as a live concern **by measurement, not by
reasoning**. The `ast` pin on `build_plink_ld_command` remains valuable as protection if the cohort
substrate ever changes.

## STEP 1 — the falsifier. VERDICT: **PAIRWISE-COMPLETE**

**The three variants** (Z selected empirically, floor 0.80):

```
X = chr15:20394741:AT:A     (the 1 bp deletion; 871 carriers)
Y = chr15:20394743:T:C      (the partner one base past the REF span; 0 of 871 carriers called)
Z = chr15:20394593:T:G      (pos 20394593, n_called 72298, MEASURED retention 0.9724)
```

Snplist line counts 3 / 2 / 2; all three runs reported **0 variants removed by the minor-allele
threshold**, so `--mac 1` was the intended no-op and no matrix was mis-shaped.

**The three matrices** (row order read off each run's own `.snplist` — note Z sorts FIRST in the
3-variant and `xz` runs, so X is row 1 there, not row 0):

```
--- run xyz, ROW ORDER: ['chr15:20394593:T:G', 'chr15:20394741:AT:A', 'chr15:20394743:T:C']
[[1.         0.00745403 0.05612129]
 [0.00745403 1.                nan]
 [0.05612129        nan 1.        ]]

--- run xz,  ROW ORDER: ['chr15:20394593:T:G', 'chr15:20394741:AT:A']
[[1.         0.00745403]
 [0.00745403 1.        ]]

--- run xy,  ROW ORDER: ['chr15:20394741:AT:A', 'chr15:20394743:T:C']
[[ 1. nan]
 [nan  1.]]
```

All diagonals exactly 1.0 in all three runs.

```
OBSERVED  3-var(X,Y)=NaN  3-var(X,Z)=0.007454  3-var(Y,Z)=0.056121
          2-var(X,Z)=0.007454  2-var(X,Y)=NaN
VERDICT: PAIRWISE-COMPLETE
```

### Why this discriminates (each competing hypothesis dies on a specific cell)

| hypothesis | prediction | observed | verdict |
|---|---|---|---|
| **pairwise-complete** | only (X,Y) NaN; others finite | exactly that | **SURVIVES** |
| mean-imputation | NO NaN anywhere | (X,Y) is NaN | REFUTED |
| listwise over the window | (X,Y) **and** (X,Z) both NaN | (X,Z) = 0.007454, finite | REFUTED |
| a merely **mis-selected Z** | (X,Z) NaN in BOTH the 3-var and 2-var runs | finite in both, and **identical** | REFUTED |

The load-bearing cell is `3-var (X,Z) = 0.007454`. Under listwise-over-the-window, Y's missingness
would have stripped X's 871 carriers from the analysis set and forced that cell to NaN. It did not.
And the 2-variant control returning the **identical** value proves `r(X,Z)` does not depend on what
else is in the batch — the signature of pairwise-complete computation. **That second control was
added during the 260825-qpf remediation specifically to separate "real listwise" from "bad Z"; it
earned its place.**

## Consequences

1. **The scanner's premise HOLDS.** plink1.9 `--r` correlates over pairwise-complete observations,
   so the numbers STEP 3 produces are attributable to the right thing.
2. **The 2026-08-24 mechanism reading is retroactively confirmed** from an independent code path:
   the `(X,Y)` NaN is zero variance *within the pair's intersection*, not a marginal defect — the
   same conclusion the `--recode A` joint-callability forensics reached, now reproduced via
   `plink --extract` rather than the region-window path.
3. Region 00057's whole-matrix scan found 2 NaN cells; this falsifier reproduced **exactly that
   pair** through a different route — a free consistency check nobody designed for.

## Limitations, recorded rather than glossed

* **A falsifier can only rule out the hypotheses it enumerates.** Four were tested; a fifth
  behaviour producing this exact pattern is not excluded by this experiment.
* **The ±200 bp flank held exactly ONE Z candidate**, so the 0.80 retention floor was a pass/fail on
  a single option, not a selection. It cleared at **0.9724**, comfortably — so this verdict stands —
  but the design had **no fallback**: had that candidate failed, STEP 1 would have stopped without
  testing the premise at all. **Widen the flank if this falsifier is ever reused.**

## STEP 2 — status per the agent, evidence NOT in hand

The agent reported "STEPs 0/1/2 remain on the record as passed" in its STEP-3 status message. **Its
verbatim STEP 2 output (the 00057 cross-check: offset +1, undefined, `n_both_called 71048`,
`del_carriers_lost 871`) was never pasted into the NCSU session and is therefore NOT banked here.**
Recorded as an assertion, not as evidence. **Ask for it when the sweep results land** — the
cross-check is the guard that the scanner reproduces from genotypes alone what plink independently
confirmed, and it should be in the record with its numbers.
