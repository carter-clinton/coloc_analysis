# CONTENT SPEC — the measurement landed; Finding 2 is NOT ESTABLISHED
DOCS-ONLY. Edits the tail disclosure entry in `.planning/osf_deviations.md`.
⛔ Lines 1-531 stay BYTE-IDENTICAL. Status stays DRAFTED — NOT POSTED.
⛔ No OSF contact, no Seth contact, no VM, by any agent.

## PROVENANCE OF THE MEASUREMENT (record it)
Read of `/home/jupyter/occ_measure/pcs_tail_verdicts.tsv`, VM-side, 2026-09-08.
Pre-flight matched all four banked anchors BEFORE anything was computed:
  md5 960f283734aea3b2c56c9249cf4fe94b | 1,031,086 B | 3,110 lines | 32 columns
The file was byte-identical after a six-day gap and a VM stop/start (mtime Sep 2 21:07),
so the disclosure's provenance holds against this exact artifact.
No re-run, no genotypes, no scan re-execution. Exit 0. All reconciliations passed.

## NEW FINDING — WITHIN-WINDOW CLUSTERING IS REAL, MEASURED, AND STRONG
This did not exist before 2026-09-08 and is reportable in its own right:
  n_pairs 2521 ; n_pairs_POST 474 ; POST-conflicts within a pair: **0**
    (so the outcome IS a well-defined property of the pair — the analysis is not void)
  n_pairs_dual_anchored 573 = 22.73% (deletion-deletion neighbours, two anchors each)
  n_clusters 2105 ; cluster_size_value_counts {1:1802, 2:239, 3:40, 4:12, 5:4, 6:5, 7:1, 8:2}
  c_mean 1.1976 ; **c_eff = sum(c^2)/sum(c) = 3767/2521 = 1.494248**
  c_max 8, del_vid `chr15:91246748:CT:C` ; 52 clusters span more than one region
  **ICC_hat = 0.728930** (ANOVA over k=303 clusters of size>=2, N=719, c0=2.371745)
  **deff_hat = 1 + (c_eff - 1) * ICC = 1.360272**
INTERPRETATION, stated plainly: pairs sharing an occluding deletion are STRONGLY correlated
in PRE/POST status. That is a structural property of the tail that matters for anyone doing
inference on this panel downstream. Report it as a finding, not merely as a caveat.
⚠ CAVEATS THAT MUST TRAVEL WITH IT:
  - THREE regions return ICC exactly 1.000000 (00027, 00040__sub10, 00161__sub13). That is
    the estimator at its BOUNDARY (zero within-cluster variance), NOT a fitted value.
  - FIVE regions return NA (too few clusters of size >= 2): 00017, 00033, 00053, 00064,
    00088__sub01.
  - Row-level agrees closely (ICC 0.7467, deff 1.3408 over 2601 clusters) — no material
    unit disagreement.
  - CHAINING DIAGNOSTIC IS CLEAN: 2051 connected components, largest 8 pairs (0.32%),
    distribution tracking the single-anchor clusters (2051 vs 2105). The single-anchor
    assignment does NOT understate clustering — the one way this measurement could have
    been biased toward its own conclusion is ruled out.

## FINDING 2 — RESTATE AS **NOT ESTABLISHED**
Because the clustering is MEASURED, the chi-square can be CORRECTED for it directly
(Rao-Scott: divide each region's contribution by its design effect). Computed in-session:

| chr15 overlap treatment            | uncorrected phi | p       | DESIGN-CORRECTED phi | p      |
|------------------------------------|-----------------|---------|----------------------|--------|
| all 21 windows                     | 2.362           | 5.4e-4  | 1.931                | 0.0074 |
| drop `00060__sub13` (the HEADLINE) | 1.969           | 0.0071  | **1.652**            | **0.0366** |
| drop `00060__sub12` (the MIRROR)   | 1.972           | 0.0069  | **1.564**            | **0.0556** |
| drop BOTH chr15 windows            | 1.535           | 0.0678  | 1.249                | 0.2116 |

⭐ **THE DECISIVE OBSERVATION:** dropping `sub13` and dropping `sub12` are INTERCHANGEABLE
choices — the two windows overlap by 6,000,001 bp and neither is privileged. After the
design correction they land at **p 0.0366 and p 0.0556**, STRADDLING 0.05. A coin-flip
between two equally defensible analyses moves the result across the significance threshold.
This separation appears ONLY after the correction, because sub12 and sub13 carry different
measured design effects (1.096 vs 1.359); uncorrected they are indistinguishable (1.969 vs
1.972).

**CONCLUSION: Finding 2 is NOT ESTABLISHED.** State exactly this and do not soften it:
  "The between-region heterogeneity in POST-filter rate is NOT ESTABLISHED. It is not robust
   to the measured within-window design effect combined with defensible handling of the
   chr15 window overlap: two interchangeable overlap treatments straddle p = 0.05 after
   correction (0.0366 vs 0.0556), and correcting for clustering while dropping both
   overlapping windows gives p = 0.21. The DIRECTION is positive under every treatment
   (phi > 1.2 throughout), but the magnitude is unidentified and the significance is an
   artifact of analytic choice."

⚠ CONSERVATISM DISCLOSURE, in our own disfavour: the five NA regions were assigned
deff = 1.0, i.e. NO correction at all. A fuller correction would push phi LOWER still. The
conservative choice ran AGAINST the conclusion now being drawn, which strengthens it.

⚠ WHAT WAS **NOT** SHOWN: the design effect does not by itself explain the whole observed
dispersion (deff 1.360 vs observed 1.99). It does sit INSIDE the observed 95% CI [1.1, 4.2],
so clustering alone remains statistically consistent with the entire effect — but that is a
failure to exclude, NOT a demonstration. Do not write that clustering "explains" Finding 2.

## SETH'S DECISION RULE — record that it did not fire
He set: c ~ 2 at high ICC reproduces 1.99 from a homogeneous panel; c ~ 1 leaves it open.
MEASURED c_eff 1.494 at ICC 0.729 -> deff 1.360. **BETWEEN the branches; neither fired.**
The comparison of point estimates was therefore not the decisive test. The Rao-Scott
correction was — and NEITHER party proposed it. Record that plainly.

## STATUS BLOCK — the outstanding item is now DISCHARGED
Replace "REMAINING BEFORE POSTING — ONE MEASUREMENT, NOT AN OBJECTION" with a
DISCHARGED bullet: the measurement was fired by Carter on 2026-09-08, returned above,
and its result RETRACTS Finding 2's establishment rather than confirming it.
⛔ This is NOT authorization to post. It removes the last OPEN item; the posting decision
remains Carter's alone.

## UNCHANGED, AND SAY SO
Finding 1 is untouched: rows 2560 PRE / 534 POST of 3094 (17.26%); pairs 2047/474 of 2521
(18.80%); 21/21 regions carry tail rows; 0 have zero POST. It is COUNTING, not inference,
and it has now survived five reviewers, two adjudication rounds, and this measurement.
Finding 3's status is unchanged (no association DETECTED, both tests underpowered).

## PART C — resume surface
`.planning/STATE.md` and `.planning/HANDOFF.json`: the measurement is DONE; Finding 2 is
NOT ESTABLISHED; the clustering is a new reportable finding; nothing remains open before a
posting DECISION. MEASURE any pin you touch.
