# CONTENT SPEC — RUN 2 STEP 2 courier to Seth

Every number below is MEASURED and VERIFIED. Copy them; do not recompute,
re-derive, or "tidy" them. If a number here disagrees with anything else in
the repo, STOP and report — do not reconcile silently.

## ARTIFACTS (on the AoU VM, not in this repo)
pcs_tail_verdicts.tsv  md5 960f283734aea3b2c56c9249cf4fe94b  1031086 B
pcs_tail_summary.json  md5 bd74c0d502d15ac4e2fb5e1bdafc72b1    38548 B
both written 2026-09-02T21:07:03Z; launched 18:26:17Z; 2 h 40 m 46 s wall.

## PROVENANCE (run-level; there is NO per-region provenance block)
bim_sha256        9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99  (20,767,864 lines)
pairs_tsv_sha256  eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583  (353,090 lines)
regions_tsv_sha256 e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a
  -> VERIFIED IN THIS SESSION to equal `sha256sum config/ld_regions.tsv` at HEAD.
ancestry AFR. region_ids_selected = 276 = the ancestry-resolved MANIFEST size.
  ⚠ 276 is NOT the number of regions carrying rows. 21 regions carry rows. Say this explicitly.
region_ids_out_of_scope = [] (empty).

## COMPLETION CHECK — all three PASS
n_tail_rows_in               measured 3094  expected 3094  PASS
n_tail_rows_out_of_scope     measured 0     expected 0     PASS
n_defined_rows_out_of_scope  measured 0     expected 0     PASS

⚠ THESE THREE ARE **NOT** A PRE-REGISTRATION, and the record must NOT call them one.
They were stated before the run finished, but they were never uncertain:
  - 3094 was ALREADY MEASURED — the smoke on m2_region_00149 returned 456 in-scope
    + 2,638 out-of-scope = 3,094. It was CARRIED FORWARD, not predicted.
  - the two zeros follow BY CONSTRUCTION once all 21 regions are in scope.
What they establish is that the run COMPLETED rather than RAISED at the runtime
`_reconcile_against_scanner_summary` check (pcs_panelwide_reclassify.py:1106), which
closes this run's tail predicate against the SCANNER'S OWN n_defined_lost_frac_ge_0p9
across all 21 regions and writes nothing on disagreement. That is a real and useful
guarantee. It is an INVARIANT CHECK, not a prediction that could have come out otherwise.

## THE TWO PRE-REGISTRATIONS — name them separately, never merge them
(1) `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
    §(e) is a GENUINE pre-registration: n_undefined_rows 15, n_undefined_distinct_pairs 13,
    already_occluded 10 / not 3, offset histogram {-14:1,-9:1,-6:1,-3:1,-1:1,0:10},
    POOLED candidate rows 353089, wc -l 353090. It was answered by RUN 1 and CONFIRMED
    5/5 + histogram with ZERO adjustments on 2026-09-01.
    ⛔ It contains NONE of n_tail_rows_in / n_tail_rows_out_of_scope /
      n_defined_rows_out_of_scope — verified, zero occurrences of each. Do NOT write any
      sentence claiming it pre-registered 3094/0/0.
(2) `.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`
    governs THIS run, and at :211-216 it DELIBERATELY DECLINES to state an expectation:
      "### NO EXPECTED VALUE IS STATED
       Not for `n_tail_rows_in`, not for either side of the split, not for any
       percentile. The whole point is that this quantity has never been computed. A
       mismatch against an expectation nobody wrote down cannot be a finding, and an
       expectation written down now would be a number picked from what we hope passes."
    QUOTE THIS IN THE RECORD and say what it covers. The PRE/POST split, the
    heterogeneity and the definitional-disagreement axis are therefore MEASURED-NOT-
    PREDICTED. That refusal is a STRENGTH — it is why none of the three findings below
    can have been shaped by an expectation — and the record must present it as one, not
    apologise for it.

## FINDING 1 — the tail is PRE-filter dominant, POST-filter residual in every region
ROWS   2560 PRE / 534 POST of 3094   POST = 17.26%
PAIRS  2047 PRE / 474 POST of 2521   POST = 18.80%
regions with tail rows = 21 ; regions with ZERO POST rows = 0
Pooled DEFINED: n_rows_in_tsv 353089; n_defined_rows_in 353074; n_undefined_rows_in 15;
  n_defined_rows_member_occluded_panelwide 7475; n_defined_rows_reaching_matrix 345599;
  n_pairs_with_ambiguous_member_id 0.

## FINDING 2 — the regions do NOT share a common POST rate (heterogeneity)
Pair-level, all 21 :   chi2 47.24  dof 20  p 5.4e-4   overdispersion 2.36
Pair-level, dropping m2_region_00060__sub13 (78.5% inside sub12's window):
                       chi2 37.78  dof 19  p 6.3e-3   overdispersion 1.99   <-- QUOTE THIS ONE
Row-level, all 21  :   chi2 51.25  dof 20  p 1.5e-4   overdispersion 2.56
Row-level POST fraction range 8.33% - 36.36%; CV 0.365.
⚠ Quote the REDUCED (1.99x) figure as the headline. The all-21 figure is inflated by the
  chr15 overlap, whose two regions rank 2nd and 3rd on POST fraction and are largely one locus.
⚠ THE MAGNITUDE IS NOT IDENTIFIED. Quote 1.99x WITH its interval and its fragility:
  1.99x (95% CI ~1.1-4.2; chi2 37.78, dof 19, p 6.3e-3) under the drop-one-window correction.
  Under the more conservative drop-both-chr15-windows treatment the estimate is 1.52 (p 0.073).
  The dispersion is robust in DIRECTION (every correction gives phi > 1.3) but POORLY
  DETERMINED in magnitude, and its significance is not robust to the choice of overlap
  correction.
NO STRUCTURAL COVARIATE WAS FOUND TO ACCOUNT FOR IT — but this is an UNDERPOWERED NULL, not
a negative result. Three structural correlates were measured. Every interval below is a
95% CI, Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3):
  spearman(POST frac, window rows)      = -0.199   95% CI [-0.590, +0.267]   p 0.387
  spearman(POST frac, occluded ids)     = -0.201   95% CI [-0.591, +0.266]
  spearman(POST frac, occlusion density)= +0.004   95% CI [-0.440, +0.446]   p 0.986
At n=21 the design has 80% power only for |rho| >~ 0.61, and 24% power at rho 0.30. These
therefore exclude only STRONG correlates and remain consistent with moderate ones — for the
cleanest of them, |rho| up to 0.446 is INSIDE this CI.
⚠ The rho = +0.886 figure (spearman(tail rows, window rows)) does NOT calibrate the power of
  these three. It is a COUNT against its own EXPOSURE — both scale with window size, so a
  large rho is near-mechanical — while the nulls are SIZE-NORMALIZED PROPORTIONS against size.
  Different tests. It does not calibrate power for a size-normalized rate.

## FINDING 3 — definitional disagreement, a SEPARATE and independent axis
informative_carriers_rarer != informative_carriers_min
  in tail      :  751 / 3094      = 24.27%
  below tail   : 1826 / 349980    =  0.52%
  enrichment   : 46.5x
NOT a tie artifact: rarer_by_maf_tie is False for ALL 3094 tail rows.
NO ASSOCIATION DETECTED between the definitional axis and the PRE/POST axis:
  spearman(POST frac, disagree frac) = +0.173 over 21 regions, 95% CI [-0.292, +0.572]
    (Fisher z with the Bonett-Wright Spearman standard error 1.03/sqrt(n-3)), p 0.453.
  PRE-vs-POST 2x2: 606/2560 = 23.67% vs 145/534 = 27.15%, chi2 2.914 p 0.088,
    Fisher p 0.096, POST trending HIGHER.
BOTH tests are underpowered at n=21 and NEITHER establishes independence. The two axes are
reported separately because no association was DETECTED, not because none exists.
⚠ RECORDED AGAINST OURSELVES: we previously argued the rho was the stronger evidence and that
  the 2x2 should not be used. The rho is the WEAKER of the two (p 0.45 vs p 0.088). Steering
  from the 2x2 to the rho was itself an absence-of-evidence error.
Also heterogeneous, but less so: chi2 37.80 dof 20 p 0.0094 overdispersion 1.89; CV 0.196.
Tail disagreement spread by region: 13.7% - 32.1%.
Definitions: "rarer" is decided by *_maf_marginal (each member's MAF over its OWN called
set), never by carrier counts, because n_called_del != n_called_partner IS the phenomenon
under study. informative_carriers_min = min(del_retained, partner_retained). They are
emitted side by side because SE(r) ~ 1/sqrt(m) binds on the MINIMUM while the rarer-variant
definition is the scientifically motivated one.

## ALSO BANK
- Seth's class (i) is EMPTY.
- The ONE surviving pair:
    region m2_region_00149
    deletion chr7:89454077:GCGTA:G   partner chr7:89454076:C:T
    offset -1, side upstream, already_occluded False, pair_key 9776035|9776036
  Offset histogram {-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}. NO positive offset anywhere.
- chr7:89454077 CANNOT be sited as at-signal vs cold-sequence. No genome-wide fine-mapping
  exists (only Track A candidate-locus results/multitrait/coloc_susie_R2*; NO MTAG outputs).
  It is BLOCKED ON THIS PANEL, not skipped. State plainly.
- Informative-carrier distribution (percentiles p0/p1/p5/p10/p25/p50/p75/p90/p99/p100):
    defined_rows      1 / 413 / 792 / 907 / 1419 / 3239 / 7959 / 15948 / 39551 / 54843
    reaching_matrix   2 / 728 / 813 / 934 / 1461 / 3314 / 8074 / 16098 / 39630 / 54843
  Low-tail cumulative: defined_rows n_le_1=4, n_le_100=1938, n_gt_100=351136 (sum 353074 OK)
                       reaching_matrix n_le_1=0, n_le_100=313, n_gt_100=345286 (sum 345599 OK)
  NO row has zero informative carriers; the matrix-reaching set has NO singletons.
  NO CARRIER FLOOR IS PROPOSED. The tool emits the distribution only.

## CORRECTION — the 0.0005 "contradiction" was FALSE; the constants are DISTINCT but SHARE AN ORIGIN
The action item previously recorded here alleged that the 0.0005 bound was self-contradictory
across modules. IT IS FALSE and it is WITHDRAWN. The two current 0.0005 occurrences are
DISTINCT LIVE PARAMETERS with NO RUNTIME COUPLING.
- `_OCCLUSION_ANOMALY_FRACTION = 0.0005` (commit d9fbc63) was the OCCLUSION gate. It was
  genuinely withdrawn, and it is REMOVED: 0 hits in src/ and tests/. It was replaced by the
  POSTED two-condition gate (mk7ze):
    OCCLUSION_SITE_FRACTION_CEILING = 0.005056
    OCCLUSION_INFLATION_CEILING     = 3.42
  both of which live in src/python/occlusion_gate_constants.py.
- condition_ld_matrix.py `ceiling_frac = 0.0005` is the LD-MATRIX NaN-ZEROING ceiling
  (n_zeroed_pairs <= ceiling_frac * n_var). That file contains the string `occlu` ZERO times.
Therefore pairwise_completeness_scan.py:45 calling the occlusion bound "withdrawn" is CORRECT.
The two statements are about two different quantities, so they do not conflict at runtime.
⚠ BUT THE SHARED VALUE IS NOT A COINCIDENCE, and the first correction overshot in implying it
  was. mk7ze's own text records that 0.0005 was "calibrated against observed NaN count"
  (mk7ze line 271, repo draft line 438) and that the amendment used "the same fractional gate
  as the withdrawn ceiling, re-purposed to exclusions" (mk7ze line 278, repo draft line 445).
  The occlusion bound was therefore TRANSPLANTED FROM the NaN-conditioning ceiling: the two
  parameters are distinct and uncoupled at runtime, but they have a documented COMMON ORIGIN.
ROOT CAUSE, stated plainly: the original ACTION ITEM grepped the literal 0.0005 and treated
textual co-occurrence as semantic identity — it was wrong to call this a live contradiction.
The first correction then made the mirror-image error: it treated the absence of runtime
coupling as the absence of any relationship, and was wrong to call the two values unrelated.

A SEPARATE, REAL defect remains and is recorded as DEFERRED (do NOT fix here, it touches
src/): condition_ld_matrix.py:3-4 and :153 cite
osf-amendment-afr-native-ld-nan-psd-2026-07-03.md (OSF tcujq) as PRE-REGISTERING the NaN->0
policy, but .planning/osf_deviations.md:133 and :166 record that the 2026-07-10 update (OSF
trsx5) WITHDRAWS exactly that policy. Accurate label: "parameter of a withdrawn policy,
retained in a frozen module, not called in production."

## SCOPE CAVEATS — state these plainly, do NOT bury them
1. n_tail_distinct_pairs_in = 2521 is the SUM of per-region distinct pairs, NOT a
   panel-wide dedup. Verified identical to the per-region column sum.
2. pair_key is INDEX-keyed DELIBERATELY (pairwise_completeness_scan.py:508). A vid key
   would UNDERCOUNT, because two .bim rows can share an id. 564 of 2461 panel-wide pairs
   (22.9%) are DELETION-DELETION NEIGHBOURS contributing two anchored rows each — a
   STRUCTURAL property of the tail, NOT a defect. Closure verified: 1897 + 2*564 = 3025,
   + 69 cross-region = 3094 tail rows.
   ⚠ already_occluded is ANCHOR-RELATIVE, so the two anchored rows of one such pair SHOULD
     differ. That is not a conflict.
3. chr15 overlap: m2_region_00060__sub12 x __sub13 share 6,000,001 bp (78.5% of sub13,
   56.4% of sub12). This is the ONLY overlap among the 21 — all 210 pairs enumerated
   against config/ld_regions.tsv. 69 ordered rows are adjudicated TWICE under two DIFFERENT
   excludelists built over two DIFFERENT row sets; 69/69 agree on the exact
   (del_occ, partner_occ) tuple, zero disagreements. "Final for its region" holds where testable.
4. n_defined_rows_rarer_and_min_definitions_disagree has NO per-region emission. The
   per-region spread is available for the TAIL only (from the TSV). The 1826 below-tail
   disagreements have NO regional attribution in this artifact.
5. Provenance is RUN-LEVEL only. Per-region monotonicity conditions attach via
   n_rows_in_window against ONE shared bim_sha256.
6. MONOTONICITY: occlusion is monotone in the row set, so an OCCLUDED verdict on a subset
   is SOUND while a NOT-OCCLUDED verdict on a subset is CONDITIONAL. Each region's window
   is COMPLETE at pad_bp=0 against fixed manifest bounds with ONE excludelist per region,
   so these verdicts are FINAL for their region and do NOT shrink as regions are added.

## HONEST LIMITATIONS — do not soften
The run finished during a VM blackout (machine rebooted; `uptime` showed 14 min against a
21:07:03Z write). The full stdout and the exit status $? are UNRECOVERABLE and were NEVER
SEEN by anyone. The completion verdict rests entirely on the three
COMPLETION-CHECK values (see that section — they are NOT a pre-registration)
plus the artifacts. There is NO pre-reboot hash, so the recorded md5s anchor FORWARD, not
backward — they cannot prove byte-identity to what was written at 21:07:03Z. What they do
establish is that a damaged file would not have parsed and summed to exactly 3094/0/0.
