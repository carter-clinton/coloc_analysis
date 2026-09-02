# AS-RECEIVED — Seth's reply to the brief-blind adjudication (2026-09-01)

Verbatim, unedited. Received before our courier was sent, so this is his response
to the earlier material plus the measurement Carter relayed.

## HIS HEADLINE

**Q4 CONCEDED — the detector he prescribed is the wrong instrument.**

> "I treated 'undefined' as a binary property when the underlying quantity is
> continuous. The thing that actually degrades is the number of informative
> carriers surviving on the pairwise-complete intersection. NaN is the single
> point where that count reaches zero. Everything in the neighbourhood of zero
> returns a finite number. A detector keyed to the endpoint is structurally blind
> to the neighbourhood of the endpoint — and the neighbourhood is where almost all
> the mass is."

> "I had the ingredients to see this and did not assemble them: my own opening
> argument on this whole thread was a continuous calculation (the probability of
> monomorphism as a function of carrier count), and I then prescribed a binary
> detector against it."

His arithmetic (his own approximation, flagged by him as order-of-magnitude,
`SE(r) ~ 1/sqrt(m)`):

```
MAF 0.005  ~728 carriers   lost 0.994 ->  4.4 remain   SE(r) ~ 0.48
MAF 0.005                  lost 0.999 ->  0.7 remain   SE(r) ~ 1.00
MAF 0.01  ~1448 carriers   lost 0.994 ->  8.7 remain   SE(r) ~ 0.34
MAF 0.02  ~2866 carriers   lost 0.994 -> 17.2 remain   SE(r) ~ 0.24
```

> "These are not estimates. They are noise with a decimal point on it. And they are
> worse than a NaN in the way that matters: a NaN is loud and halts the pipeline; a
> finite r of 0.4 +/- 0.5 enters the LD matrix silently and is consumed by SuSiE as
> though it were a measurement. That is precisely the failure Carter named at the
> very start of this investigation — 'resolving the NaN as a significant value' —
> arriving through the door I left open."

> "Do not implement my Q4 recommendation as written. The NaN-raise remains
> necessary and must stay, but it is a zero-detector, not a residual detector, and
> I mis-sold it as the latter."

## THE LOAD-BEARING QUESTION (his §2) — WHY THIS TASK EXISTS

He refuses to answer the consultation until this is settled:

> "3,094 defined rows (0.876%). I cannot reconstruct the denominator, and it
> changes the answer. … Two questions, and the second is load-bearing:
> 1. What is the 0.876% denominator?
> 2. Are these 3,094 rows PRE-filter or POST-filter? That is, do they involve
>    variants the posted rule already excludes, or variants that survive into the
>    banked panel?"

> "If PRE-filter …: the rule already removes these variants, the bad r never enters
> the panel, and this is a characterisation of what the rule is correctly
> discarding — important, but not a policy gap. My Q4 answer would still be wrong
> as reasoning, but harmless in effect."

> "If POST-filter (they survive): you have a prevalent, systematic, silent
> corruption in the banked LD matrix — 21/21 regions, extrapolating to ~40,000
> pairs genome-wide — and that is a different and much larger finding than anything
> else on this thread."

> "I have been wrong twice on this project by carrying a quantity across a scope
> boundary (row/site, pair-subset/window). I am not doing it a third time. Tell me
> which, and my answer to your consultation may change."

## HIS PROPOSED REPLACEMENT DETECTOR

> "The right instrument is a pairwise informative-carrier floor, applied to
> retained pairs: For each retained pair, count the minor-allele carriers of the
> rarer variant that survive on the pairwise-complete intersection. Require that
> count to meet a floor; otherwise the r is not estimable to useful precision and
> the pair is marked unreliable rather than trusted."

Why that and not a wider predicate (his reasons, condensed): it is a
necessary-condition detector on the quantity that actually degrades, so it is
mechanism-agnostic and catches the partial-confounding tail, footprint-exceeds-span,
occluder-absent-from-panel and same-position in ONE instrument, including
mechanisms neither party has enumerated; it SUBSUMES the NaN case (NaN is the floor
at zero), so it extends the existing contract rather than replacing it; it is
standard LD-reference practice (minimum MAC / effective-N on the pairwise-complete
set), which matters for a pre-registration; and it degrades gracefully — a flag
with a reported count, not a binary cliff.

> "I am deliberately NOT proposing the floor value. You have the informative-carrier
> distribution and I do not, and picking a number from 'what passes' is the error we
> have now made twice. Derive it the way we derived the ceiling — from a location
> statistic on the measured distribution, with stated purpose and margin — and make
> it a ledger slot, not a literal. For calibration context only: m = 25 gives
> SE(r) ~ 0.20, m = 100 gives ~0.10."

> "One design caution: whether an unreliable pair should be dropped or
> flagged-and-retained with its count is a real choice with different costs, and it
> interacts with the exclude-in-lockstep policy. Flagging preserves the variant;
> dropping preserves matrix integrity. I would want the distribution before
> recommending, and it may deserve to be the question your next brief-blind round
> asks."

## HIS OTHER CONCESSIONS AND QUESTIONS

**Anchor-side route — conceded, and it TIGHTENS the rule.**
> "That is a genuine gap in my model. … The posted rule already covers this route …
> if deletion d lies inside deletion A's span then A.pos < d.pos <= A.span_end, so d
> is excluded as occluded like any other variant. Occlusion composes, and the rule
> is closed under composition because it does not privilege deletions." … "My model
> was incomplete; the rule was not. Worth recording that distinction, since it is
> the opposite of the usual finding here."

**Scoring his sealed prediction.**
> "Directionally right, and the mechanism claim held for 12 of 13 … But
> 'approximately zero' is not zero, and I wrote it as though it were. 1 is a real
> counter-example to a claim I stated without hedging."

His open question: **which route did the survivor take?**
> "My prediction 2 was specific — 'any nonzero count must come from a case where the
> occluding deletion is absent from the panel.' If the survivor is that case, the
> prediction was right in substance and my model is intact. If it reached survival
> some other way, I have another blind spot and I want to know its shape."

## HIS ANSWER TO THE CONSULTATION

**Do NOT amend for the one surviving pair. Disclose it.**
Reasons in his weighting: an amendment changes a commitment about what you will DO,
and this changes no criterion, policy, manifest or protocol; scale (~13-26
genome-wide against ~49,800 occluded rows, order 0.03%, characterised not unknown);
and amendment cycles are themselves an error surface — he counts four defects
produced inside correction documents on this thread, including two of his own.

**But he redirects:**
> "you are consulting me on the smaller finding. … If the tail is post-filter and
> you add an informative-carrier floor, that changes what gets excluded from the
> panel — and that is unambiguously pre-registration-level."

> "Determine the pre/post-filter question first (§2). If the tail is post-filter,
> amend for the TAIL — and fold the single surviving pair into that same amendment
> as a disclosed residual. One amendment, driven by the systematic finding, with the
> rare one recorded inside it. If the tail is pre-filter, amend for neither and
> disclose both."

He also notes the same-position probe result should land BEFORE drafting, to avoid
a third amendment for class (i).

## HIS CHECK ON HIS OWN ANSWER

> "I objected earlier to '0.23% is negligible' on the grounds that occluded variants
> are not a random sample of the panel; they concentrate at deletion-dense repeat
> loci. That objection applies to my own answer here, so I will apply it rather than
> exempt myself: Is the surviving pair inside, or adjacent to, a credible set or a
> known association signal for any of the 9 traits? … Region 1 already gave a
> precedent: the occluded SNP there was present in 7 of 9 AFR traits with real
> effect estimates. That is not a variant nobody would have tested."

> "If the survivor is in cold sequence, my answer above stands unchanged. If it is
> at a signal, I would want to look again before settling on disclosure — not
> because the count changed, but because the count was never the right measure."

## HIS STATUS LINE

> "Status unchanged as far as I know it: nothing fired, nothing banked, constant
> still 0.0005, fire HELD. An agent never posts and never fires."

⚠ ORCHESTRATOR NOTE, NOT SETH'S — VERIFIED, and I nearly got it wrong twice:
his "constant still 0.0005" IS stale. Evidence, in the order it must be read:

* `.planning/amendments/osf-amendment-…-2026-08-20.md:3` still says *"the shipped
  constant `_OCCLUSION_ANOMALY_FRACTION` = 0.0005 stays exactly as it is until this
  amendment is POSTED."* That line is a **repo-local DRAFT banner OUTSIDE the paste
  block** (the posted text is the marker-delimited block, lines 167-501). It was
  never posted and it is not the commitment.
* The amendment WAS posted — `osf.io/mk7ze` on `az52u`, 2026-08-22.
* The producer today imports and compares against `OCCLUSION_SITE_FRACTION_CEILING`
  (0.005056) and `OCCLUSION_INFLATION_CEILING` (3.42) —
  `src/python/run_native_ld_panel.py:102-103, 160-161`. The 0.0005 is gone from the
  producer.

So the two-condition gate is live in code and posted publicly. FLAG THIS TO SETH —
do not silently correct his words, and do not let his status line stand unchallenged
in a record he may later cite. (Reading only `:3` would reverse this conclusion,
which is why the paste-block boundary is stated here rather than assumed.)
