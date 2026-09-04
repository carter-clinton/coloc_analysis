# CONTENT SPEC — quick-260904-dgi
Corrections to the tail disclosure after a 5-reviewer adversarial review
(Codex CLI + 4 blind investigators). DOCS-ONLY. Nothing under src/ or tests/.

⛔ THE DISCLOSURE IS STILL "DRAFTED — NOT POSTED". Nothing is posted by any agent.
⛔ Every replacement below was REPRODUCED IN-SESSION. Copy them; do not recompute.

===============================================================================
# PART A — THE DISCLOSURE (`.planning/osf_deviations.md`, entry at :532-669)

## A1 — BLOCKER: every mk7ze line citation is WRONG (repo lines, not posted lines)
PROVEN: repo lines 168-500 of
`.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md`
reproduce mk7ze's exact OSF md5 `13a49f543cabcc27ce9f1e589783c060`, 22,945 B,
**333 lines**. Posted line = repo line − 167.
  "mk7ze line 275"            -> **mk7ze line 108**
  "clause (a) at line 467"    -> **mk7ze line 300**  (467 DOES NOT EXIST in 333 lines)
  "sweep of the 598-line posted body" -> **the 333-line posted body**
    (598 is the REPO DRAFT file, whose line 1 reads "DRAFT — NOT POSTED" and whose
     lines 502-598 are post-posting status material. The sweep's CONCLUSION is
     unaffected — zero hits over the superset implies zero over the subset — but the
     sentence stated a false fact about what was posted.)
⚠ Cite BOTH forms so a reader can check either: "mk7ze line 108 (repo draft line 275)".

## A2 — BLOCKER: the registered prediction is FALSIFIED by data we already hold
CURRENT (:578-580) says: "Residual undefined-r is expected EXCLUSIVELY at negative
offsets." We hold a POSITIVE-offset case: `m2_region_00057`,
`chr15:20394741:AT:A` (ref_len 2, span_end 20394742) x `chr15:20394743:T:C` — ONE BASE
past the span end, downstream, un-occluded, measured 2026-08-24
(`.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md:62-70`).
And our OWN `.planning/STATE.md:287` already concluded: "It is the −1 mirror of
`m2_region_00057`'s +1 ... so **the residual class is immediately adjacent to the REF
span, EITHER side**, and this sweep could observe only one side."
REPLACE WITH:
  "Within the 21-region pre-committed sample, residual undefined-r was observed ONLY at
   negative offsets. A positive-offset survivor WITHIN that sample would falsify
   downstream predicate completeness for it. ⚠ THIS IS EXPLICITLY SAMPLE-SCOPED: a
   positive-offset case is ALREADY KNOWN out-of-sample — m2_region_00057's +1, which the
   pre-committed 21-region sample does not contain — so the residual class is known to
   sit immediately adjacent to the REF span on EITHER side, and this scan could observe
   only one side. Production tests the rate on both sides."
⛔ Do NOT write "EXCLUSIVELY at negative offsets" unqualified anywhere.

## A3 — BLOCKER: "non-independence cannot CREATE dispersion" is FALSE
The 0.98 simulation tested BETWEEN-window duplication — a structure that provably cannot
inflate E[chi2/dof]; it was guaranteed to return ~1.0 before it ran. The operative
dependence is WITHIN-window: pairs sharing an occluding deletion do not flip
independently, and carrier loss is a property of the deletion. Our OWN record measures
the structure: 22.9% of tail pairs are deletion-deletion neighbours.
REPRODUCED IN-SESSION (equal parent rates, ZERO heterogeneity, clusters of size c):
  c=2, ICC 1.0  -> mean phi 2.032   P(phi >= 1.988) = 0.482
  c=3, ICC 1.0  -> mean phi 2.937   P(phi >= 1.988) = 0.865
  c=2, ICC 0.6  -> mean phi 1.367   P(phi >= 1.988) = 0.050
  c=1 (independent control) -> mean phi 1.011  P = 0.010
REPLACE WITH:
  "BETWEEN-window duplication cannot create dispersion (simulated 0.98 under equal parent
   rates). It does NOT follow that non-independence cannot: WITHIN-window clustering can
   and does. An average of two co-moving pairs per occluding deletion reproduces the
   observed 1.99 EXACTLY with zero parent-rate heterogeneity. The pairs-per-deletion
   distribution in the tail HAS NOT BEEN MEASURED, so the observed dispersion is NOT yet
   attributable to parent-region heterogeneity rather than to a cluster design effect."
⛔ DELETE "It is STRONGER than an unexamined null because both artifact explanations were
   eliminated." ONE was eliminated; the more plausible one was never tested.

## A4 — BLOCKER: the heterogeneity magnitude is UNIDENTIFIED
REPRODUCED: 95% CI on the overdispersion ~ **[1.13, 4.22]**. Sensitivity to the chr15
overlap correction:
  all 21 windows            phi 2.362  p 5.4e-4
  drop 00060__sub13 (ours)  phi 1.988  p 6.3e-3
  drop 00060__sub12         phi 1.992  p 6.2e-3
  DROP BOTH 00060 windows   phi 1.518  p 0.073   <-- NOT SIGNIFICANT
  merge to 19 parents       phi 2.623  p 2.0e-4
41% of the chi-square comes from 2 of the 19 parent regions.
REPLACE the bare "1.99x" headline WITH:
  "1.99x (95% CI ~1.1-4.2; chi2 37.78, dof 19, p 6.3e-3) under the drop-one-window
   correction. Under the more conservative drop-both-chr15-windows treatment the estimate
   is 1.52 (p 0.073). The dispersion is robust in DIRECTION (every correction gives
   phi > 1.3) but POORLY DETERMINED in magnitude, and its significance is not robust to
   the choice of overlap correction."

## A5 — BLOCKER: the leave-one-out does not rule out an influential unit
The window-level LOO CANNOT remove parent 00060 — its two windows shield each other —
and its minimum (1.988) IS the headline, so it reported the same deletion twice as if it
were independent corroboration. REPRODUCED at parent level:
  drop parent 00060  n=19  phi 1.518  p 0.0732   <-- NOT SIGNIFICANT
  drop parent 00120  n=19  phi 2.412  p 0.0007
  drop parent 00040  n=20  phi 2.075  p 0.0039
REPLACE WITH:
  "Leave-one-WINDOW-out gives 1.99-2.48, but this does not address influence: the two
   chr15 windows shield each other, and the LOO minimum is the headline itself.
   Leave-one-PARENT-out over the 19 distinct parent regions ranges 1.52-2.49 with
   worst-case p 0.073 — one parent region (00060) is influential enough that its removal
   renders the heterogeneity non-significant at alpha 0.05."

## A6 — BLOCKER: "COMPLETE IN ITS OWN DIRECTION" is overclaimed from n=1
REPLACE WITH:
  "Across the 21-region scan, NO positive-offset undefined survivor was observed, and the
   only measured surviving pair was upstream at offset -1. That supports a prospective
   positive-offset falsification check; it is NOT proof of predicate completeness. The
   scanner's own docstring (pairwise_completeness_scan.py:40-45) states that n=1 supplies
   neither prevalence, boundary width, nor one-sidedness."

## A7 — HIGH: the negative result must become an UNDERPOWERED NULL
REPRODUCED (n=21, two-sided Spearman): power 0.127 at rho 0.20; **0.236 at rho 0.30**;
0.597 at rho 0.50; 80% power needs |rho| ~ 0.61. 95% CIs:
  rho -0.199 -> [-0.581, +0.255]  p 0.387
  rho -0.201 -> [-0.59,  +0.27 ]
  rho +0.004 -> [-0.428, +0.435]  p 0.986   (|rho| up to 0.446 is INSIDE this CI)
⚠ The rho=+0.886 "power" comparison is NOT FAIR: it is a COUNT against its own EXPOSURE
  (both scale with window size, so a large rho is near-mechanical), while the nulls are
  SIZE-NORMALIZED PROPORTIONS against size. Different tests.
REPLACE "Register this as a negative result" WITH:
  "Three structural correlates were measured: rho -0.199 [-0.58, +0.26], -0.201, and
   +0.004 [-0.43, +0.44]. At n=21 the design has 80% power only for |rho| >~ 0.61 and 24%
   power at rho 0.30, so these exclude only STRONG correlates and remain consistent with
   moderate ones — for the cleanest of them, |rho| up to 0.446 is inside the interval.
   This is an UNDERPOWERED NULL, not a negative result. The rho=+0.886 comparison is a
   count against its own exposure and does not calibrate power for a size-normalized rate."
⛔ Do NOT register a negative result. Do NOT pre-register a dispersion figure.

## A8 — HIGH: the rho +0.173 independence claim, and OUR OWN INVERSION
REPRODUCED: rho +0.173, n=21 -> 95% CI [-0.280, +0.563], **p 0.453**. The PRE/POST 2x2 we
told Seth to REJECT is chi2 2.914, **p 0.088** — i.e. we steered from the STRONGER
evidence to the WEAKER one while lecturing about absence-of-evidence.
REPLACE WITH:
  "No association between the definitional axis and the PRE/POST axis was DETECTED
   (rho +0.173, 95% CI [-0.28, +0.56], p 0.45; 2x2 chi2 p 0.088). BOTH tests are
   underpowered at n=21 and NEITHER establishes independence. The two axes are reported
   separately because no association was detected, not because none exists.
   ⚠ Recorded against ourselves: we previously argued the rho was the stronger evidence
   and the 2x2 should not be used. The rho is the WEAKER of the two (p 0.45 vs p 0.088).
   That correction was itself an absence-of-evidence error."

## A9 — HIGH: "NO claim whatsoever" is too broad
mk7ze DOES retain a raw-panel NaN-raise contract (repo :488-489 = posted :321-322).
REPLACE WITH:
  "mk7ze does not claim that undefined or degraded r is EXHAUSTED by the occlusion
   predicate, and it does not discuss the measured degraded defined-row class."

## A10 — HIGH: the SILENCE SWEEP MISSED THE WORD THAT MATTERS
The sweep tested `defined row`, `finite r`, `degraded`, `precision`, `SE(` — all 0. It
never tested **`undefined`**, which occurs EXACTLY ONCE in the posted body, at repo :249
(posted :82): "The exclusion policy for an occluded variant is unaffected: **its LD is
structurally undefined**". That is a DIRECTIONAL claim (occluded => LD undefined) and it
runs the OTHER way from the tail finding, so it is not falsified — but it must be
disclosed as swept and considered, not silently omitted.
ADD the term to the recorded sweep and state the finding explicitly.

## A11 — HIGH: "(recorded as pre-registered here)" cannot be true
The entry is marked DRAFTED — NOT POSTED, and the prediction is POST HOC relative to the
21-region scan. REPLACE WITH:
  "Prospective production prediction, to be pre-registered IF AND WHEN this disclosure is
   posted, and posted BEFORE production testing. It is post hoc relative to the
   21-region scan and is not a pre-registration today."

## A12 — the two SCOPING REPAIRS that strengthen §(4) (reviewer-identified, adopted)
(a) ADD line 275's PROVENANCE: it descends from `.planning/debug/fire-morning-occlusion-
    oracle-vs-geometry.md:227-233`, whose conclusion was stated BROADLY ("Every
    NaN-producing pair is geometrically occluded"). State that plainly — claiming a scope
    for a sentence while withholding its own drafting record is the weakest available
    position, and mk7ze §(e) set the house standard of carrying provenance verbatim.
(b) ADD region-1 pair 4: `.planning/amendments/m3_region1_nan_geometry_verdict.md:20,30-37`
    records a NaN pair whose geometry is **`disjoint`** — a NaN pair with NO covering
    deletion, documented BEFORE posting and DELIBERATELY EXCLUDED from the 5-member
    expectation set (mk7ze repo :271 says "a settled 5-member expectation" against SIX
    observed NaN pairs). This converts "the narrow reading is grammatically available"
    into "the narrow reading is what the expectation set was actually built on."

## A13 — FREE WIN: add the permutation confirmation
"Verified against a 40,000-resample Monte Carlo permutation test: p = 0.0072 (asymptotic
chi-square p 6.3e-3; the asymptotic value is mildly anti-conservative, conclusion
unchanged). ⚠ The permutation test permutes PAIRS and therefore assumes exchangeable
independent pairs — it validates the asymptotics, NOT the independence assumption at
issue in the clustering caveat above."

===============================================================================
# PART B — THE COURIER RECORD
`.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`

## B1 — "different, unrelated constants" is FALSE HISTORICALLY (we over-corrected)
mk7ze's own text (repo :438, :445) says 0.0005 "was calibrated against observed NaN count"
and that the amendment used "**the same fractional gate as the withdrawn ceiling,
re-purposed to exclusions**". So the occlusion bound was TRANSPLANTED FROM the
NaN-conditioning ceiling; the shared value is causal, not coincidental.
REPLACE WITH:
  "The two current 0.0005 occurrences are DISTINCT LIVE PARAMETERS with NO RUNTIME
   COUPLING: _OCCLUSION_ANOMALY_FRACTION is removed from src/ and tests/ (0 hits) and
   pairwise_completeness_scan.py:45 is correct to call the occlusion bound withdrawn.
   ⚠ But they are NOT 'unrelated': mk7ze records that the occlusion gate reused 'the same
   fractional gate as the withdrawn ceiling, re-purposed to exclusions', so the shared
   value has a documented COMMON ORIGIN. The original ACTION ITEM was wrong to call this a
   live contradiction; the first correction was wrong to call the constants unrelated."

## B2 — apply the SAME statistical restatements as A3, A4, A5, A7, A8
The courier carries these claims too. Every replacement above applies verbatim.
⛔ If the appendix carries any of them, FIX AT SOURCE in
   `.planning/quick/260902-vsp-.../CONTENT-SPEC.md` and RE-SPLICE (the ee3af4b pattern),
   then re-anchor. Do NOT add a supersession note.

===============================================================================
# PART C — REPO HYGIENE (blocks nothing external; misleads a resuming session)
C1. `.planning/HANDOFF.json:209` and
    `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:15` still pin the
    courier at "491 lines, md5 e2c0b544…". TRUE VALUE: re-measure at task end and write
    the measured value. (It was 542 / c8525e26 before THIS task; this task changes it
    again — MEASURE, do not copy.)
C2. `.planning/quick/260903-ict-.../deferred-items.md` declares "F-3a is CLOSED … Do not
    re-open" while enumerating only 3 of the 5 sites that pin the courier. Correct it to
    name all sites, or reopen it.
C3. `.planning/STATE.md:54` asserts `collaps`/`parent`/`2.62`/`leave-one-out`/`2.48`/
    `0.0063` are "all 0 hits across its 491 lines". `9ce807f` ITSELF introduced `parent`,
    `leave-one-out`, `2.48` and `0.0063` into the courier. Add an AS-OF qualifier naming
    the pre-9ce807f state, or restate.
C4. `.planning/HANDOFF.json:220` key `three_repo_fixes_QUEUED_NOT_DONE` — fixes 1 and 2
    ARE DONE (by 260903-ict). Rename/restate; keep fix 3 (the two-file tcujq docstring
    defect) as the only one queued.
C5. `.planning/quick/260902-vsp-.../deferred-items.md:7` and `…/260902-vsp-SUMMARY.md:17,
    :252-256` still assert the 0.0005 "LIVE CONTRADICTION" as fact and cite a courier
    heading that no longer exists. Add a dated SUPERSEDED clause — do NOT rewrite the
    historical description (that would falsify the log).

===============================================================================
# PART D — QUEUE THE MEASUREMENT THAT SETTLES A3
Record in deferred-items.md, NOT executed here (needs the VM; CARTER FIRES, never an agent):
  "MEASURE the pairs-per-deletion distribution in the tail from
   /home/jupyter/occ_measure/pcs_tail_verdicts.tsv (already on the VM; no re-run, no
   genotypes, reads the emitted TSV only). Group tail rows by del_vid and report the
   cluster-size distribution. Design effect ~ 1 + (c-1)*ICC. THIS DECIDES whether the
   observed overdispersion is parent-region heterogeneity or a within-window cluster
   effect. Until measured, Finding 2's magnitude is NOT attributable."
