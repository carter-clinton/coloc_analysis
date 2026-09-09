# CONTENT SPEC — correct the Rao-Scott table's ESTIMATOR
DOCS-ONLY. `.planning/osf_deviations.md` §(10b) and any restatement of the same table.
⛔ Lines 1-531 BYTE-IDENTICAL. Status stays DRAFTED — NOT POSTED. No OSF/Seth/VM contact.

## THE DEFECT
The committed table computed the pooled POST rate ONCE from all 21 regions and reused that
fixed value for every subset. For a chi-square test of HOMOGENEITY among k groups, the null
is that THOSE k groups share a common rate, so the rate must be estimated FROM THE GROUPS
UNDER TEST. Using an externally fixed rate is not the homogeneity test.
This was MY error in the analysis script, not the executor's transcription.

## THE CORRECTED TABLE — replace the numbers, keep the structure and the conclusion
Recomputed in-session with the pooled rate estimated from each subset:

| chr15 overlap treatment            | uncorrected phi | p       | DESIGN-CORRECTED phi | p        |
|------------------------------------|-----------------|---------|----------------------|----------|
| all 21 windows                     | 2.362           | 5.4e-4  | 1.931                | 0.0074   |
| drop `00060__sub13` (the HEADLINE) | **1.988**       | 0.0063  | **1.675**            | **0.0326** |
| drop `00060__sub12` (the MIRROR)   | **1.992**       | 0.0062  | **1.579**            | **0.0517** |
| drop BOTH chr15 windows            | **1.518**       | 0.0732  | **1.241**            | 0.2171   |

⭐ THE CONCLUSION IS UNCHANGED AND SHARPER. The straddle is now **0.0326 vs 0.0517** —
TIGHTER around 0.05 than the figures it replaces (0.0366 vs 0.0556). Two interchangeable
overlap treatments still land on opposite sides of the threshold, so Finding 2 remains
**NOT ESTABLISHED** and the non-robustness is if anything better demonstrated.

## ALSO RESOLVED — a discrepancy flagged and correctly NOT fixed by the previous task
`260908-u5k` deferred item D1 noted that §(10b) said **1.969** for drop-`sub13` while the
courier body says **1.99**. RESOLVED: under the correct subset estimator the value is
**1.988**, so the COURIER was right and §(10b)'s 1.969 was the artifact of the fixed-rate
error. Record that the discrepancy is closed and which side was correct.

## RECORD THE ERROR ITSELF, briefly and without softening
"An earlier draft of this table estimated the pooled rate once from all 21 regions and
reused it for every subset. That is not the homogeneity test being reported: the null is
that the regions UNDER TEST share a common rate, so the rate is estimated from them. The
table above is recomputed correctly. The correction moved every subset figure slightly and
did NOT change the conclusion — the p-value straddle that makes Finding 2 non-robust became
tighter (0.0326 vs 0.0517, previously 0.0366 vs 0.0556)."

## UNCHANGED — do not touch
The clustering finding (c_eff 1.494248, ICC 0.728930, deff 1.360272) is computed from the
measurement and is NOT affected by this estimator: it involves no pooled-rate choice.
Finding 1 unchanged. The conservatism disclosure (five NA regions at deff 1.0) unchanged.
The "failure to exclude, not a demonstration" framing unchanged.

## PART C
Refresh any live pin the edit moves; MEASURE, never copy. Dated task records stay untouched.
