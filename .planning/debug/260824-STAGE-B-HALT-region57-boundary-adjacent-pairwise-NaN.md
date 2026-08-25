# STAGE B HALT — a CONFINED PAIRWISE NaN at a deletion-span BOUNDARY (m2_region_00057, 2026-08-24)

> Provenance: AoU browser agent's verbatim halt report (~23:18 EDT) plus the read-only forensic
> probes it ran on the NCSU-authored diagnostic (~23:27 EDT). Stage B was fired on Carter's go
> after Stage A passed; `--fail-fast` halted the loop at region 4 of 4. NOTHING was mis-banked:
> 3 regions banked clean, the 4th refused to convert. AS-RECEIVED measurements; the interpretation
> below separates what was MEASURED from what is still HYPOTHESIS.

## The halt

`m2_region_00057` (chr15, n_var 2,854, 0.153 min) — the square `.ld.bin` carried NaN, so
`plink_ld_to_npz.read_square_bin` raised and `--fail-fast` halted the loop:

```
ERROR m2_region_00057: square LD carries NaN for .../m2_region_00057.ld.bin: likely source variant row(s) ranked by NaN count [index: 2532, 2533] — plink --r writes 0/0 -> NaN for a zero-variance variant (monomorphic within the --nonfounders set, all-missing, or all-heterozygous). QC these variants out (MAF/missingness on the actual sample set) or apply an explicit NaN policy BEFORE the .npz; do NOT confuse this with an asymmetry.
__main__.RegionGateError: region gate FAILED at m2_region_00057 ... — halting the native-plink LD loop (fail_fast).
```

**The raise is the pre-registered raw-panel NaN-raise contract WORKING**, and `--fail-fast` halting
a 276-region fire on a bad region is the design. Stage B: **3 banked of 4** (`m2_region_00001`,
`m2_region_00017`, `m2_region_00040__sub14` all `ok`), bucket `.npz` count 3.

## The forensics (MEASURED, verbatim)

```
n_var 2854 | total NaN cells 2 | rows with >=1 NaN 2 | cols 2
row idx: [2532, 2533]
col idx: [2532, 2533]
  row 2532 nan_count 1 diag 1.0
  row 2533 nan_count 1 diag 1.0
PATTERN = confined pair? True
PATTERN = whole-row (zero-variance)? False
```

The two variants (snplist lines 2533/2534 = `.ld.bin` row order):

```
chr15:20394741:AT:A     <- a 1 bp deletion (REF "AT", ALT "A")
chr15:20394743:T:C      <- a SNP
```

Already excluded by the occlusion filter in this region (2 ids):
`chr15:20193458:C:T`, `chr15:20217313:AT:A` — neither is a member of the NaN pair.

## What the data ESTABLISHES

**1. The producer's stated diagnosis is FALSIFIED.** The error text names "a zero-variance variant
(monomorphic within the `--nonfounders` set, all-missing, or all-heterozygous)". A zero-variance
variant NaNs its ENTIRE row and column — ~2,854 NaNs, and typically a NaN diagonal. Measured:
`nan_count == 1` on each row and `diag == 1.0` on both. **Both variants have well-defined marginal
variance.** The message's prescribed remedy (QC out zero-variance variants) would not touch these
two. The text is boilerplate for the more common pattern; the code's own docstring
(`nan_variant_indices`) anticipates both shapes.

*Corroborating detail, from the error string itself:* `nan_variant_indices` collects EVERY row with
≥1 NaN, caps at 32, and appends `...` when >10 are shown. The message printed exactly two indices
with no ellipsis → exactly two rows in the whole matrix carry any NaN. The whole-row hypothesis was
already refutable from the halt message before any probe ran.

**2. It is a single symmetric PAIR** — 2 cells of 8,145,316, at (2532,2533) and (2533,2532). A
**pairwise**-undefined correlation, not a marginal one.

**3. The pair straddles the pre-registered span boundary by ONE BASE.** For
`chr15:20394741:AT:A`: `ref_len = 2`, `span_end = pos + ref_len − 1 = 20394742`. The occlusion rule
is `d.pos < v.pos <= d.span_end` (`occlusion_span_filter.py:250`). A variant at **20394742** IS
occluded; the NaN partner sits at **20394743** — exactly one base past. **The filter behaved
correctly under the pre-registered criterion, and the pair is still undefined.**

## The NEGATIVE CONTROL WE ALREADY OWN — this is NOT a generic boundary property

Region 1 (Stage A, 2026-08-24, banked): **102,421 in-window rows, 7,951 multi-base-REF rows**, 231
occluded and excluded, and the shipped verifier then re-read **38,595,391,746 bytes** and found
**ZERO NaN**. With 7,951 deletions in one window, deletion/flanking-SNP adjacency is certain to
occur there many times over. **It produced no NaN.**

So deletion-boundary adjacency is **necessary-at-most, not sufficient**. Whatever makes the 00057
pair undefined is CONDITIONAL on something further — most plausibly the joint missingness pattern
(if every carrier of the deletion is no-called at the flanking SNP, the pairwise-complete
intersection contains only non-carriers, at which point the deletion site is invariant *within that
intersection* and plink writes 0/0 → NaN while both marginal variances remain fine). That is a
HYPOTHESIS consistent with all measurements so far; **it has not been measured** (see below).

## What is NOT known, and must NOT be assumed

- **The mechanism is unconfirmed.** The joint-callability table for the pair (how many samples are
  non-missing at BOTH, and whether the deletion is invariant within that intersection) was NOT
  captured — the `--freq counts` / `--missing` / `--hardy` probe was not pasted back. One cheap
  read-only command settles it (below).
- **The PREVALENCE is unknown, and n=1 cannot supply it.** 1 of 4 fired regions carries this; region
  1 with 7,951 deletions carries none. Those two facts do not determine a rate.
  ⛔ **Do not calibrate any rule, threshold, or criterion change on this single region.** That is
  precisely the error that produced the withdrawn `0.0005` constant — a bound derived at n=1 and
  wrong by ~38× when finally measured. The pre-registered criterion may need revision; it may not;
  **the measurement decides, and the measurement does not exist yet.**
- **A 1 bp widening of the span is a PROXY patch, not a fix.** The pre-registered criterion uses the
  REF span as a proxy for the real property (joint uncallability). If the proxy under-covers at the
  boundary, widening it by one base is another proxy with an unmeasured cutoff — alignment ambiguity
  near indels is not guaranteed to stop at +1. The property itself ("the pairwise-complete
  intersection is invariant") is directly detectable. See memory
  `feedback_scope_a_guard_to_the_property_not_a_proxy`.

## Consequence for the fire

`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown
per-region failure rate: a 1-in-N rate halts an ~11-day serial fire repeatedly. Either the rate is
shown negligible, or the criterion/policy is revised (with pre-registration), or Stage C's
error-handling posture is decided explicitly. **Stage C is not discussable until the prevalence
number exists.**

## Two further findings from the same batch

**RAM-1 — `peak_ram_gib` is NOT a per-region measurement (CONFIRMED defect).**
`run_native_ld_panel._run_plink` computes `peak_kib = max(rss_after - rss_before, rss_after)`. Since
`rss_before >= 0`, the delta is always ≤ `rss_after`, so **the `max()` collapses to `rss_after`
every time** and the docstring's "DELTA" never happens. `resource.getrusage(RUSAGE_CHILDREN).ru_maxrss`
is a MONOTONE high-water mark across all children in the process (verified empirically at NCSU: a
300 MB child then a 5 MB child leaves the reading at the 300 MB mark, delta 0). Observed exactly:
region 17 → 2.9689 (real, first child), sub14 → 26.5745 (real, larger), **00057 → 26.5745
(inherited; a 2,854-variant region cannot use 26.6 GiB)**. Region 1's 30.6591 is real because Stage A
was its own process. Impact: the panel's RAM column flat-lines at the running max — over 276 serial
regions it becomes a constant, destroying the per-region RAM record and any "is this region heavy?"
monitoring, and `fire_verifier stage-b`'s per-region RAM bound evaluates a contaminated series
(conservative — it over-reports, so it risks a spurious halt rather than letting danger through).
Clean fix: `subprocess.Popen` + `os.wait4(pid, 0)`, whose `rusage` is that child's own. OFF the LD
path (measurement wrapper only), but it must land before Stage C.

**COST-1 — the worst-case anchor is missing.** `m2_region_00071` (the deliberately-chosen worst case)
never ran; `--fail-fast` halted before it. The Stage-B cost/RAM extrapolation to Stage C cannot be
completed without it.

## State at this record

Stage B HALTED, 3 of 4 banked, bucket `.npz` count 3, STEP 9-GATE deliberately NOT run (it would
evaluate an incomplete, error-bearing batch). No retry, no edit, no NaN-policy improvisation, no
criterion change. VM idle. Nothing fires. **An agent never fires.**

## Next (in order)

1. **Confirm the mechanism** on the banked pair — one read-only command, seconds (joint-callability
   table from a 2-variant `--recode A` dump).
2. **Measure the prevalence** across the pre-committed 21-region sample with a properly designed
   probe — candidate pairs are geometric (deletion span_end + 1 .. + K) and `r` for a pair is
   independent of the other variants, so a candidate-only `--r` on a few hundred variants per region
   answers it in minutes, with no full-region LD recompute. **Design it before firing it.**
3. Only then: adjudicate the criterion/policy (with Seth, brief-blind) and decide Stage C's posture.
4. Separately and independently: **RAM-1** fix (TDD) and the **00071** anchor.
