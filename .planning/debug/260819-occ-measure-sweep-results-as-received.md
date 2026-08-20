# 21-region occlusion measurement sweep — results as received (2026-08-19 ~21:15 EDT)

> Provenance: ruled measurement pass (pre-committed systematic-by-span sample of 20
> + m2_region_00001 forced), run server-side on VM 20260626b in the Workbench web
> terminal (survived a mid-run session logout), relayed verbatim by Carter from the
> reattached terminal buffer. TSV banked on the VM at
> /home/jupyter/occ_measure/occ_measure_sample.tsv (22 lines = header + 21 rows).
> HARNESS CROSS-CHECK PASSED: m2_region_00001 reproduced occ=231 EXACTLY — all 21
> results are trusted. Detector = frozen occlusion_span_filter via its own
> load_bim_rows, identical code path to the failed STEP 7 gate.

## Verbatim per-region results

    m2_region_00017        small   span=1052797   n=7088    del=573    occ=25   frac=0.3527%  ceil=3.5    defer=True
    m2_region_00033        small   span=2568467   n=19317   del=1472   occ=28   frac=0.1450%  ceil=9.7    defer=True
    m2_region_00064        small   span=3329609   n=24155   del=2208   occ=52   frac=0.2153%  ceil=12.1   defer=True
    m2_region_00042        small   span=4673946   n=43690   del=3320   occ=119  frac=0.2724%  ceil=21.8   defer=True
    m2_region_00053        medium  span=6602233   n=49996   del=4422   occ=105  frac=0.2100%  ceil=25.0   defer=True
    m2_region_00060__sub13 medium  span=7646445   n=69802   del=5364   occ=111  frac=0.1590%  ceil=34.9   defer=True
    m2_region_00062        medium  span=8011252   n=86719   del=5525   occ=200  frac=0.2306%  ceil=43.4   defer=True
    m2_region_00088__sub01 medium  span=10593031  n=89217   del=6399   occ=118  frac=0.1323%  ceil=44.6   defer=True
    m2_region_00111__sub07 medium  span=10595249  n=80102   del=6260   occ=126  frac=0.1573%  ceil=40.1   defer=True
    m2_region_00060__sub12 medium  span=10646435  n=80028   del=6629   occ=119  frac=0.1487%  ceil=40.0   defer=True
    m2_region_00120__sub03 medium  span=10843073  n=81033   del=6565   occ=143  frac=0.1765%  ceil=40.5   defer=True
    m2_region_00120__sub17 medium  span=10843073  n=72598   del=5893   occ=122  frac=0.1680%  ceil=36.3   defer=True
    m2_region_00161__sub13 medium  span=10873010  n=87073   del=7161   occ=188  frac=0.2159%  ceil=43.5   defer=True
    m2_region_00145__sub14 medium  span=10883014  n=77249   del=6781   occ=158  frac=0.2045%  ceil=38.6   defer=True
    m2_region_00040__sub10 medium  span=10934775  n=75741   del=6633   occ=143  frac=0.1888%  ceil=37.9   defer=True
    m2_region_00063        medium  span=14021341  n=109335  del=8554   occ=207  frac=0.1893%  ceil=54.7   defer=True
    m2_region_00027        medium  span=16858255  n=129258  del=11080  occ=237  frac=0.1834%  ceil=64.6   defer=True
    m2_region_00081        medium  span=22846520  n=196219  del=18066  occ=420  frac=0.2140%  ceil=98.1   defer=True
    m2_region_00008        large   span=32784081  n=207147  del=16984  occ=372  frac=0.1796%  ceil=103.6  defer=True
    m2_region_00149        large   span=48473400  n=338354  del=29918  occ=562  frac=0.1661%  ceil=169.2  defer=True
    m2_region_00001        medium  span=13496933  n=102421  del=7951   occ=231  frac=0.2255%  ceil=51.2   defer=True

    SUMMARY n=21: frac min=0.1323% median=0.1888% max=0.3527%; defer_at_0.0005: 21/21
    ceiling x2 (=0.0010): passes 0/21
    ceiling x3 (=0.0015): passes 3/21
    ceiling x4 (=0.0020): passes 12/21
    ceiling x5 (=0.0025): passes 19/21
    ceiling x6 (=0.0030): passes 20/21
    ceiling x8 (=0.0040): passes 21/21
    ceiling x10 (=0.0050): passes 21/21

## What the distribution establishes

1. Geometric occlusion at 0.13-0.35% of variants is the POPULATION NORM of this
   panel's substrate, stable across small/medium/large regions — region 1's 231
   (0.2255%, near median) was REPRESENTATIVE, not an outlier.
2. The pre-registered clause-(d) constant 0.0005 defers 21/21 sampled regions and,
   by extension, essentially all 276: as pre-registered, the fire banks zero. The
   calibration premise (occlusion is ~5-per-100k rare) is dead at population level,
   confirming Seth's §8 confession (n=1, wrong quantity, re-purposed).
3. ⚠ CALIBRATION DISCIPLINE for the amendment: the multiplier table is the
   empirical ANCHOR, not the ANSWER. Picking x8 "because it passes 21/21" would be
   calibrate-to-pass — the same defect shape as the original (fitting a constant to
   one observation set). The re-derived ceiling must state its PURPOSE (flagging
   genuine substrate/representation anomalies relative to the measured population)
   and derive its value from the distribution's shape with declared headroom — to
   be argued in the amendment draft and attacked by Seth brief-blind.
4. STILL GATING THE BRANCH CHOICE: the §5 same-position measurement (PENDING
   PASTE #2) — if same-position composition is large, the problem reassigns from
   calibration to upstream normalization and NO ceiling is recalibrated from this
   distribution until that is adjudicated.
