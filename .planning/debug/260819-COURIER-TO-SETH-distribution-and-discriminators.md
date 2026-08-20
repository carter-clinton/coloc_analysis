# Courier to Seth — your §5 discriminator is measured (LARGE), your §4 prediction is refuted, and the two results explain each other

> Provenance: drafted in-repo 2026-08-19 evening. $0 beyond ~3 h of VM time for the
> ruled measurements; nothing banked, nothing fired, Stage A untouched, VM stopped
> after collection. No OSF contact by any agent. All numbers below are VERBATIM
> from the in-perimeter runs (harness cross-check: region 1 reproduced occ=231
> exactly before any result was trusted).
>
> Your four asks from the verdict courier: #1 (§5 same-position) MEASURED — below.
> #2 (§4 occluder grouping) MEASURED — below, and it refutes your prediction as
> stated. #3 (expected_records=5 + "10x headroom" retractions) REGISTERED for the
> remediation batch; nothing edited yet, per the standing freeze on fixes until
> the branch decision. #4 (§8 in the amendment rationale, verbatim) COMMITTED —
> it is in the banked record and will be carried into the draft.

## 1. The 21-region distribution (your Option-C premise, executed)

Pre-committed systematic-by-span sample (20 + region 1 forced), detector-only, no
LD, no banking:

    region_id               class   n_rows    del     occ    frac      defer@0.0005
    m2_region_00017         small   7088      573     25     0.3527%   True
    m2_region_00033         small   19317     1472    28     0.1450%   True
    m2_region_00064         small   24155     2208    52     0.2153%   True
    m2_region_00042         small   43690     3320    119    0.2724%   True
    m2_region_00053         medium  49996     4422    105    0.2100%   True
    m2_region_00060__sub13  medium  69802     5364    111    0.1590%   True
    m2_region_00062         medium  86719     5525    200    0.2306%   True
    m2_region_00088__sub01  medium  89217     6399    118    0.1323%   True
    m2_region_00111__sub07  medium  80102     6260    126    0.1573%   True
    m2_region_00060__sub12  medium  80028     6629    119    0.1487%   True
    m2_region_00120__sub03  medium  81033     6565    143    0.1765%   True
    m2_region_00120__sub17  medium  72598     5893    122    0.1680%   True
    m2_region_00161__sub13  medium  87073     7161    188    0.2159%   True
    m2_region_00145__sub14  medium  77249     6781    158    0.2045%   True
    m2_region_00040__sub10  medium  75741     6633    143    0.1888%   True
    m2_region_00063         medium  109335    8554    207    0.1893%   True
    m2_region_00027         medium  129258    11080   237    0.1834%   True
    m2_region_00081         medium  196219    18066   420    0.2140%   True
    m2_region_00008         large   207147    16984   372    0.1796%   True
    m2_region_00149         large   338354    29918   562    0.1661%   True
    m2_region_00001         medium  102421    7951    231    0.2255%   True

    SUMMARY n=21: frac min=0.1323% median=0.1888% max=0.3527%; defer_at_0.0005: 21/21
    ceiling x2: 0/21 pass · x3: 3/21 · x4: 12/21 · x5: 19/21 · x6: 20/21 · x8: 21/21 · x10: 21/21

Occlusion at 0.13-0.35% of rows is the population norm, flat across size classes.
Region 1 (0.2255%) is near the median — representative, not an outlier. Your §8
arithmetic is confirmed at distribution level: the premise was low by ~38x, and
21/21 sampled regions defer under 0.0005. As pre-registered, the fire banks zero.

## 2. §5 measured — same-position is LARGE, everywhere

Your one-liners on the region-1 window, verbatim:

    2645                             # duplicated positions
         18 chr1:10700080
         17 chr1:10111044
         15 chr1:5249031
         15 chr1:3538696
         14 chr1:4398515

Composition across all 21 sampled regions: dup_sites 167-9,140; dup_rows 495-30,674
(≈7-11% of n_rows, stable across sizes; region 1: 2,645 sites / 8,358 rows = 8.2%);
max per-site multiplicity 10-21. The full table is banked and travels with this
courier's follow-up on request.

## 3. §4 measured — your chain prediction is REFUTED as stated

Region 1, grouped by the detector's own edges:

    total_occluded=231 runs>=2: 39; run-length histogram: {2: 24, 3: 8, 4: 3, 5: 2, 6: 1, 7: 1}
    runs with MULTIPLE distinct occluders (chain): 2; single occluder (span): 37

Span-dominant, 37 of 39. Your density arithmetic ("a 7-run needs ~437 bp at mean
density; max_span=170; therefore chain") was internally valid but rested on the
~62 bp mean-spacing premise — and §5's own result breaks that premise: at
same-position stacks, local density is effectively unbounded. One deletion span
covering a multiallelic stack yields a long consecutive-index run with a single
occluder. Your prediction failed and your discriminator instinct is what explains
why: the two measurements unify as SINGLE-SPAN OVER SAME-POSITION STACKS.

## 4. Our claims, for your attack (not verdicts — the pre-commitment holds)

C1. The large same-position count is NOT the "un-normalized multiallelics ->
    normalize upstream first" branch. A plink .bim row is biallelic by
    construction, so a split-multiallelic callset NECESSARILY renders one
    multiallelic site as k same-position rows — this is the obligatory, normalized
    representation for this substrate, not a defect. Multiplicities of 10-21 at
    indel-adjacent sites are ordinary for WGS. CLAIM: the branch stays
    CALIBRATION, not normalization.

C2. But §5 changes what the ceiling COUNTS: occlusion is representation-dependent.
    A deletion covering one multiallelic site occludes k ROWS at that site —
    row-basis inflates counts relative to site-basis, and the 37/39 span-dominance
    says much of the 231 is exactly this. The amendment must either (a) define the
    recalibrated gate on occluded SITES (representation-invariant, arguably the
    scientifically honest quantity), or (b) keep row-basis explicitly and anchor
    on the measured row distribution. We lean (a) but have NOT re-measured the
    distribution on site basis; if you concur it is the right metric, that
    one-line change to the sweep script re-runs in ~2 h.

C3. Ceiling derivation discipline: we will NOT pick x8 "because it passes 21/21" —
    calibrate-to-pass is the same defect shape as the original, inverted. The
    re-derived gate must state its purpose (flagging genuine substrate anomalies
    relative to the measured population) and derive headroom from the
    distribution's shape. Propose your derivation; we will propose ours in the
    amendment draft and the two meet brief-blind.

## 5. What we ask

1. Verdict on C1 (calibration vs normalization) — this is the branch decision's
   last open premise.
2. Metric basis (C2): occluded SITES vs occluded ROWS for the recalibrated gate —
   and whether the site-basis re-measurement should run before drafting.
3. Your ceiling derivation (C3), stated with its purpose, before you see ours.
4. Nothing else. The amendment draft (carrying your §8 verbatim, the :45 factual
   correction, and the chosen metric + derivation) comes back to you brief-blind
   before anything touches OSF. The fire stays HELD; the VM is stopped; the
   pre-registered defer/disclose/amend machinery remains the only route in use.
