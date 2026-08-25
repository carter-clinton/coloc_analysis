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

---

# MECHANISM CONFIRMED (2026-08-24 ~23:38 EDT) — deletion-linked missingness, PERFECTLY confounded

The joint-callability dump for the pair, verbatim from the VM:

```
dosage columns: chr15:20394741:AT:A_A  chr15:20394743:T:C_C
joint (A,B) dosage table incl NA: {('0','0'): 70232, ('0','NA'): 570, ('0','1'): 816,
                                   ('1','NA'): 871, ('NA','NA'): 598, ('NA','1'): 14, ('NA','0'): 21}
N non-missing at BOTH: 71048
A values within that intersection: Counter({'0': 71048})
B values within that intersection: Counter({'0': 70232, '1': 816})
```

NCSU-side reconciliation:

| Quantity | Value | Note |
|---|---|---|
| Joint table total | **73,122** | exactly the cohort `.fam` count — the table is complete |
| A (deletion): hom-ref / het / NA | 71,618 / **871** / 633 | no homozygous carriers |
| **A carriers CALLED at B** | **0 of 871** | cells `('1','0')` and `('1','1')` are ABSENT ENTIRELY |
| A marginal allele frequency | 871 / (2 × 72,489) = **0.601%** | healthy; A is nowhere near monomorphic |
| Intersection (both called) | 70,232 + 816 = **71,048** | matches the dump |
| A within the intersection | **constant 0** | → zero variance → `0/0` → NaN |
| B within the intersection | 70,232 ref / 816 het | **B is variable — only A collapses** |

**The mechanism, stated exactly:** carrying the deletion and being no-called at the neighbouring
site are **perfectly confounded, 871 of 871**. The missingness removes precisely and only the
carriers, so the pairwise-complete intersection retains no copy of the deletion allele; A is
invariant *within the intersection* while its marginal variance is perfectly healthy. plink writes
`0/0 → NaN`.

So the producer's message was right that a zero-variance condition caused it and **wrong about the
scope**: it is zero variance *within the pair's intersection*, induced by deletion-linked
missingness — not zero variance on the analysis set. Its prescribed remedy (QC out zero-variance
variants on the actual sample set) would never flag A.

**This is the occlusion mechanism** — a deletion rendering a neighbouring site unreadable —
occurring **one base beyond the REF span** that the pre-registered criterion tests. The rule
correctly declined to exclude the pair, and the pair still carries structurally undefined LD *for
exactly the reason the amendment describes*.

## ⚠ SECOND-ORDER CONSEQUENCE — the NaN raise only catches the knife-edge

Perfect confounding (871/871) is the **boundary case** that yields NaN. **Partial** confounding does
not: if even a handful of carriers are called at the flanking site, the intersection retains some
variance, plink returns a **finite** `r`, and **no NaN check anywhere in the pipeline fires** — yet
that `r` was computed on a **biased, non-random subsample** that systematically under-represents
deletion carriers. It banks silently.

Therefore: **region 1 passing NaN-free does NOT establish that region 1 is free of deletion-linked
missingness bias.** It establishes only that region 1 contained no *perfectly* confounded pair.
Those are very different claims, and the stronger one is the tempting misreading of the Stage A
falsification. The Stage A result stands exactly as written — occlusion accounted for 100% of
region 1's *NaN* — and says nothing about defined-but-biased correlations.

The prevalence sweep must therefore measure the **distribution** of confounding, not merely count
NaN: for each candidate pair, the intersection size and the fraction of one member's carriers lost
to the other's missingness. A long tail of near-complete confounding would be a data-quality caveat
for the panel as a whole, not just a NaN-policy question. Whether such a tail exists is **unknown**.

## PREVALENCE SWEEP — design (measure the PROPERTY, not a proxy; no LD compute)

The undefined-LD condition is a **pure genotype property** and needs no `--r` at all:

> for a pair (X, Y), the correlation is undefined ⟺ within `called(X) ∩ called(Y)`, X or Y is invariant.

For the deletion-boundary class this reduces to a set test — `carriers(X) ⊆ missing(Y)` (or the
symmetric case) — computable from carrier/missing bitsets straight off the `.bed`. Design points:

1. **Sweep the offset; do not assume +1.** For each deletion D (`span_end = pos + ref_len − 1`) and
   each variant V at `offset = V.pos − span_end`, record the offset alongside the outcome. The
   empirical offset distribution **gives the boundary width** instead of us guessing it. This is the
   "scope the guard to the property, not the proxy" rule applied to the fix itself.
2. **Both sides.** The pre-registered rule is one-sided (`d.pos < v.pos`), but alignment ambiguity at
   an indel is **not directional** — include negative offsets (variants upstream of `d.pos`). If
   upstream pairs also fail, the current rule is under-covering in a second, unnoticed direction.
3. **Both members.** Test invariance of X *and* of Y within the intersection; do not assume the
   deletion is always the collapsing member.
4. **Record the gradient, not just the binary.** Per candidate pair: intersection size, carriers of
   each member, carriers lost to the other's missingness. That is what surfaces the partial-confounding
   tail described above.
5. **Scale is small.** Region 1 carries 7,951 multi-base-REF rows at ~7.6 variants/kb, so a ±25 bp
   window yields on the order of a few thousand candidate pairs per large region — bitset set-ops over
   73,122 samples, i.e. minutes per region, no LD recompute, no 42 GB matrices.
6. **Build it TDD at NCSU first ($0).** The detector is pure logic over `.bed`/`.bim` and is fully
   testable on synthetic fixtures — exactly how `occlusion_span_filter` was built — then run
   in-perimeter over the pre-committed 21-region sample.
7. **Context per hit.** Record each hit's coordinates. Region 00057's pair sits at chr15 ~20.39 Mb,
   pericentromeric; region 1 (chr1:10,000–13,506,933) showed none. Whether these cluster in
   segdup/pericentromeric territory is a **hypothesis to test**, not a finding — but if they do, both
   the disclosure and the remedy differ from a uniformly-distributed artifact.

## What is settled, and what is still open

**SETTLED:** the mechanism for this pair (perfect carrier-missingness confounding → intersection-
invariant → NaN); that the occlusion filter behaved correctly under the posted criterion; that the
producer's stated diagnosis and remedy do not fit.

**OPEN — and not settleable from n=1:** (a) the prevalence of perfectly-confounded pairs across the
panel; (b) the true boundary width and whether it is one-sided; (c) whether a partial-confounding
tail exists and how large; (d) the response — a criterion extension, an explicit pairwise-completeness
policy, or something else. (d) is a **pre-registration** question, because the exclusion criterion is
what `trsx5` posts. None of these may be answered by inference from this one pair.
