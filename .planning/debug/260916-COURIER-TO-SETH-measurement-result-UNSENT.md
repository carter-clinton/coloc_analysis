# Courier to Seth — the pairs-per-deletion measurement result (⛔ UNSENT)

**Status:** DRAFTED 2026-09-14, **NOT SENT**. No agent contacts Seth — Carter sends it.
**Uses the CORRECTED Rao-Scott table** (pooled rate estimated from the subset under test, quick
`260908-uer`). ⛔ Do NOT send the superseded figures `1.652/0.0366`, `1.564/0.0556`, `1.969`.
**Source of every number:** `.planning/osf_deviations.md`, the 2026-09-03 tail-disclosure entry §(10),
as amended through `7c92f27`.
**Seth's last state:** adjudication CLOSED with no open objection (D8 accepted; D7 raised then retracted by
him after measuring). He has NOT seen this measurement.

---

````
Seth — the measurement landed. It does not confirm Finding 2; it removes its robustness.
Finding 2 is NOT ESTABLISHED. One correction to my own analysis is included below.

PRE-FLIGHT: all four banked anchors matched before anything was computed —
md5 960f283734aea3b2c56c9249cf4fe94b, 1,031,086 B, 3,110 lines, 32 columns. Byte-identical
after a six-day gap and a VM stop/start. No re-run, no genotypes, exit 0, all reconciliations
pass, and ZERO POST-conflicts within any pair — so the outcome is a well-defined property of
the pair and the analysis is not void.

1. YOUR DECISION RULE DID NOT FIRE.
  c_eff = sum(c^2)/sum(c) = 3767/2521 = 1.494248
  ICC_hat = 0.728930        (ANOVA, k=303 clusters of size>=2, N=719, c0=2.371745)
  deff_hat = 1 + (c_eff-1)*ICC = 1.360272
BETWEEN your branches — c~2-explains-it and c~1-leaves-it-open both missed. So comparing
point estimates was never going to decide it, and that was the test we both designed.

2. THE TEST THAT SETTLED IT WAS PROPOSED BY NEITHER OF US.
Because the clustering is MEASURED rather than assumed, the chi-square can be corrected for
it directly (Rao-Scott: divide each region's contribution by its design effect):

  chr15 treatment              uncorrected  p        DESIGN-CORRECTED  p
  all 21 windows               2.362        5.4e-4   1.931             0.0074
  drop 00060__sub13 (headline) 1.988        0.0063   1.675             0.0326
  drop 00060__sub12 (mirror)   1.992        0.0062   1.579             0.0517
  drop BOTH chr15 windows      1.518        0.0732   1.241             0.2171

THE DECISIVE OBSERVATION: sub13 and sub12 are INTERCHANGEABLE — 6,000,001 bp of overlap,
neither privileged. After correction they land at p 0.0326 and p 0.0517, STRADDLING 0.05. A
coin flip between two equally defensible analyses moves the result across the threshold.
That separation appears ONLY after correction, because the two windows carry different
measured design effects (1.096 vs 1.359); uncorrected they are indistinguishable.

FINDING 2 IS NOT ESTABLISHED. Direction stays positive under every treatment (phi > 1.2
throughout), magnitude is unidentified, significance is an artifact of analytic choice.

3. A CORRECTION TO MY OWN ANALYSIS, and your instinct about the courier was right.
My first Rao-Scott pass estimated the pooled POST rate ONCE from all 21 regions and reused
that fixed value for every subset. Wrong: for a homogeneity test the null is that the groups
UNDER TEST share a rate, so it must be estimated from them. The table above is recomputed
correctly. Four numbers moved; the conclusion did not, and the straddle TIGHTENED (0.0326 /
0.0517, previously 0.0366 / 0.0556).
It surfaced only because the fixed-rate pass produced 1.969 for drop-sub13 where the courier
said 1.99 — a 0.02 mismatch that someone flagged and declined to reconcile. Under the correct
estimator it is 1.988. THE COURIER WAS RIGHT; my table carried the artifact.

4. AGAINST MY OWN CASE.
Five regions have too few multi-pair clusters to estimate an ICC (00017, 00033, 00053, 00064,
00088__sub01). I assigned them deff = 1.0 — NO correction at all. A fuller correction pushes
phi LOWER still. Three regions return ICC exactly 1.000000 (00027, 00040__sub10,
00161__sub13): that is the estimator at its BOUNDARY, zero within-cluster variance, not a
fitted value, and I am not treating it as one.

5. WHAT WAS *NOT* SHOWN, explicitly.
deff 1.360 against observed 1.99. Clustering does NOT explain Finding 2. It sits inside the
observed 95% CI [1.1, 4.2], so clustering alone remains statistically consistent with the
whole effect — but that is a FAILURE TO EXCLUDE, not a demonstration. The disclosure does
not say clustering explains it, and neither do I.

6. A GENUINELY NEW FINDING, and the credit is yours.
Within-window clustering is real, measured, strong: ICC 0.729. Pairs sharing an occluding
deletion are heavily correlated in PRE/POST status. 573 of 2521 pairs (22.7%) dual-anchored;
largest cluster 8 pairs, chr15:91246748:CT:C. This was not knowledge before 2026-09-08. It
goes in as a finding, not a caveat.
Your specific hypothesis stayed dead and the general principle you used to kill it was false
— but the mechanism you pointed at after that, within-window structure, is the one that was
live. The measurement exists because you pushed there.

CHAINING DIAGNOSTIC CLEAN: 2051 components, largest 8 pairs (0.32%), tracking the
single-anchor clusters (2051 vs 2105). The one way this measurement could have been biased
toward its own conclusion is ruled out.

7. FINDING 1 UNTOUCHED. 2560/534 rows (17.26%), 2047/474 pairs (18.80%), 21/21 regions with
tail rows, 0 with zero POST. Counting, not inference. Five reviewers, two adjudication
rounds, and a measurement built to break it.

All of the above is in the disclosure, still DRAFTED — NOT POSTED. Nothing is open before a
posting decision, and that is not authorization to post.
````
