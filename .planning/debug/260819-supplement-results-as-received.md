# §5/§4 supplement results — as received (2026-08-19 ~21:32 EDT)

> Provenance: PENDING PASTE #2 executed on VM 20260626b after the 21-region sweep;
> relayed verbatim by Carter. Working .sp.bim files deleted per R6; the persistent
> record on the VM: occ_measure_sample.tsv, step7_vv.txt, region1_window.bim, the
> failed-notebook Hail record. Interpretation pre-committed to happen jointly with
> Seth — the notes at the bottom are CLAIMS for his attack, not verdicts.

## PART 1a — Seth's §5 one-liners, region-1 window (verbatim)

    $ awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -d | wc -l
    2645
    $ awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -c | sort -rn | head -5
         18 chr1:10700080
         17 chr1:10111044
         15 chr1:5249031
         15 chr1:3538696
         14 chr1:4398515

## PART 1b — same-position composition sweep, all 21 sampled regions (verbatim)

    region_id               n_rows   dup_sites  dup_rows  max_mult
    m2_region_00017         7088     167        495       10
    m2_region_00033         19317    409        1398      16
    m2_region_00064         24155    843        2667      14
    m2_region_00042         43690    997        3172      16
    m2_region_00053         49996    1424       4644      16
    m2_region_00060__sub13  69802    1731       5952      18
    m2_region_00062         86719    2158       6690      19
    m2_region_00088__sub01  89217    2193       7391      17
    m2_region_00111__sub07  80102    1885       6204      21
    m2_region_00060__sub12  80028    2155       7533      21
    m2_region_00120__sub03  81033    2017       6573      15
    m2_region_00120__sub17  72598    1759       5633      18
    m2_region_00161__sub13  87073    2400       7542      16
    m2_region_00145__sub14  77249    2164       7019      17
    m2_region_00040__sub10  75741    1978       6471      15
    m2_region_00063         109335   3218       10527     17
    m2_region_00027         129258   3250       10989     16
    m2_region_00081         196219   6713       21421     16
    m2_region_00008         207147   5590       18145     18
    m2_region_00149         338354   9140       30674     17
    m2_region_00001         102421   2645       8358      18

## PART 2 — §4 chain-vs-span, region 1 (verbatim)

    total_occluded=231 runs>=2: 39; run-length histogram: {2: 24, 3: 8, 4: 3, 5: 2, 6: 1, 7: 1}
    runs with MULTIPLE distinct occluders (chain): 2; single occluder (span): 37

## Planning-side CLAIMS (for Seth's attack — not verdicts)

1. "Same-position = 0" is window-false EVERYWHERE sampled: dup_rows ≈ 7-11% of
   n_rows, stable across sizes; per-site multiplicities up to 21.
2. §4 as stated is REFUTED — span-dominant (37/39), not chain — and the refutation
   VINDICATES the §5 instinct: the two results unify. Seth's density arithmetic
   assumed ~62 bp mean spacing; same-position stacks make local density effectively
   unbounded, so ONE deletion span covering a multiallelic stack yields a long
   consecutive-index run with a single occluder. The runs are single-span over
   same-position stacks.
3. CLAIM: this is NOT the "un-normalized multiallelics -> normalize upstream"
   branch. Split-biallelic rows are the OBLIGATORY plink representation (a .bim
   row is biallelic by construction); multiplicities of 10-21 at indel-adjacent
   sites are ordinary for split WGS callsets. The branch stays CALIBRATION.
4. CONSEQUENCE the amendment must handle: the occlusion COUNT is representation-
   dependent — a deletion covering one multiallelic site occludes k ROWS at that
   site. Row-basis inflates counts relative to site-basis. The re-derived ceiling
   must either (a) define the metric on occluded SITES, or (b) keep row-basis and
   say so explicitly, with the measured population (0.13-0.35% of rows) as its
   anchor. Metric choice + ceiling derivation = Seth's review questions.
