# Site-basis occlusion sweep (PENDING PASTE #3) — results as received (2026-08-20 ~20:11 EDT)

> Provenance: ruled site-basis sweep run on VM 20260626b (same pre-committed 21-region
> sample; detector = frozen occlusion_span_filter via load_bim_rows; occluded SITES =
> distinct (chr,pos) among occluded rows; total sites = distinct (chr,pos) in the window),
> relayed verbatim by Carter. TSV banked on the VM at
> /home/jupyter/occ_measure/occ_measure_sitebasis.tsv (22 lines = header + 21).
> HARNESS CROSS-CHECK PASSED: region 1 reproduced occ_rows == 231 EXACTLY (the assert
> precedes the summary; the summary printed). This is the FIFTH supporting record the
> amendment's pre-paste checklist requires; its summary block is the SOLE source for the
> amendment's Class-M slots.

## Per-region table (verbatim; columns: region_id, n_rows, n_sites, occ_rows, occ_sites, row_frac_pct, site_frac_pct, inflation)

    m2_region_00017         7088    6760    25   14   0.3527  0.2071  1.79
    m2_region_00033         19317   18328   28   25   0.1450  0.1364  1.12
    m2_region_00064         24155   22331   52   38   0.2153  0.1702  1.37
    m2_region_00042         43690   41515   119  112  0.2724  0.2698  1.06
    m2_region_00053         49996   46776   105  98   0.2100  0.2095  1.07
    m2_region_00060__sub13  69802   65581   111  103  0.1590  0.1571  1.08
    m2_region_00062         86719   82187   200  173  0.2306  0.2105  1.16
    m2_region_00088__sub01  89217   84019   118  113  0.1323  0.1345  1.04
    m2_region_00111__sub07  80102   75783   126  118  0.1573  0.1557  1.07
    m2_region_00060__sub12  80028   74650   119  112  0.1487  0.1500  1.06
    m2_region_00120__sub03  81033   76477   143  119  0.1765  0.1556  1.20
    m2_region_00120__sub17  72598   68724   122  102  0.1680  0.1484  1.20
    m2_region_00161__sub13  87073   81931   188  172  0.2159  0.2099  1.09
    m2_region_00145__sub14  77249   72394   158  122  0.2045  0.1685  1.30
    m2_region_00040__sub10  75741   71248   143  117  0.1888  0.1642  1.22
    m2_region_00063         109335  102026  207  174  0.1893  0.1705  1.19
    m2_region_00027         129258  121519  237  207  0.1834  0.1703  1.14
    m2_region_00081         196219  181511  420  378  0.2140  0.2083  1.11
    m2_region_00008         207147  194592  372  311  0.1796  0.1598  1.20
    m2_region_00149         338354  316820  562  494  0.1661  0.1559  1.14
    m2_region_00001         102421  96708   231  196  0.2255  0.2027  1.18

## Summary block (verbatim — the Class-M slot source)

    SITE-BASIS SUMMARY n=21: min=0.1345% median=0.1685% max=0.2698%; robust_sigma(1.4826*MAD)=0.0274%
    CANDIDATE CEILING (Seth C3, 3x site-basis median): 0.5056%
    margin over observed site-basis max: 1.87x
    mean row/site inflation across sample: 1.18x (Seth's run-collapse estimate was ~1.42x for region 1)

    $ wc -l /home/jupyter/occ_measure/occ_measure_sitebasis.tsv
    22 /home/jupyter/occ_measure/occ_measure_sitebasis.tsv

## Measurement-level observations (agent's, no adjudication)

- Site-basis distribution is TIGHTER than row-basis (0.1345-0.2698% vs 0.1323-0.3527%); the
  region-00017 row-basis outlier largely collapses on site basis (1.79x inflation there vs a
  1.18x sample mean; Seth's ~1.42x region-1 run-collapse estimate was approximate — measured
  region-1 inflation is 1.18x).
- 3x site-basis median = 0.5056% clears the observed site-basis max by 1.87x; on this sample
  it would spuriously defer 0/21 while sitting ~3x above typical.
