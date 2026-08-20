# Seth reply — C1 CONCUR, C2 SPLIT (sites/rows), C3 derivation, §4 refutation accepted, new §6 (as received)

> Provenance: received 2026-08-19 ~21:42 EDT, pasted by Carter into the NCSU
> session, answering the distribution-and-discriminators courier (7,182 B /
> 5038f7e7a810b1ef65212e18d7c7e1dc). AS-RECEIVED transcription; no byte anchors
> supplied. Net state: ALL adjudication branches CONVERGED — calibration path,
> gate-on-sites / report-rows, 3x-median purpose-anchored ceiling, site-basis
> re-measurement before number instantiation, amendment framed as a corrected
> empirical claim (wrong by 38x on frequency, policy unaffected), §6 same-position
> collinearity caveat to record. Awaiting only Carter's formal branch adoption.

---

Seth — C1 CONCUR, C2 SPLIT (sites for the gate, rows for the accounting), C3 derivation below. And my §4 refutation accepted.

Answering all three, brief-blind, with my derivation stated before I see yours. One new issue surfaced by §5 that neither of us has named yet — §6 below; it is not a blocker but it should not go unrecorded.

## 0. My §4 prediction was wrong, and your refutation is correct

37 of 39 runs single-occluder. Span-dominant, not chain-dominant. My arithmetic was internally valid and rested on a premise your own §5 destroys: I used a 62 bp window-mean spacing to argue a 7-run needs ~437 bp. But a same-position stack has zero bp extent — local density is unbounded exactly where occlusion happens. So one deletion span over a multiallelic stack yields a long consecutive-index run with a single occluder, which is what you measured.

That is the third premise of mine to fail on real data (the 7/5 oracle, same-position = 0, the mean-spacing model), and all three failed the same way: a property measured or assumed at one scale, asserted at another. I am stating that pattern explicitly because it should inform how much weight my derivation in §3 gets — it is reasoning over your 21-region measurement, not over data I have touched.

## 1. C1 — CONCUR: calibration, not normalization

Your reasoning is right and the mechanism is decisive: a plink .bim row is biallelic by construction, so a correctly-normalized split-multiallelic callset necessarily renders one k-allelic site as k same-position rows. Region 1's mean multiplicity is 3.16 (8,358 rows at 2,645 sites) with max 10-21 at indel-adjacent sites — ordinary for WGS, and stable at 7-11% across all 21 regions, which is what a representation convention looks like rather than a defect.

So my §5 warning is answered, not deferred: I flagged same-position-large as possibly un-normalized multiallelics; you established it is the obligatory representation for this substrate. bcftools norm -m + would merge them back into multiallelic records that plink cannot represent — that is the wrong direction. The branch is CALIBRATION. I withdraw the normalization branch.

## 2. C2 — the answer is BOTH, on different objects. This is not a fudge; they are different quantities with different jobs.

The anomaly GATE should count occluded SITES. Its purpose is to detect substrate anomalies. A row-basis gate fires differently on identical biology depending on how the caller split multiallelics — the same deletion over the same site counts 3 at multiplicity 3 and 18 at multiplicity 18. A gate whose threshold moves with a representation convention is not measuring the substrate. Site-basis is representation-invariant, which is exactly the property an anomaly detector needs. Your lean (a) is correct.

The exclusion ACCOUNTING must stay on ROWS. You exclude rows from the panel; the manifest records rows; the lockstep sumstats drop is row-keyed on (CHR,POS). Reporting exclusions in sites would understate what left the panel and would break the manifest's audit purpose. So: gate on sites, exclude and report rows, and state both numbers.

Estimated inflation, so you can judge whether the re-measurement is worth 2 h. From your own region-1 run-length histogram ({2:24, 3:8, 4:3, 5:2, 6:1, 7:1}):

    occluded rows 231 = 107 rows inside runs>=2  +  124 isolated
    if each run collapses to ~1 site: sites ~ 124 + 39 = 163
    row/site inflation ~ 1.42x  ->  region 1 on site basis ~ 0.159% (vs 0.2255% row basis)

Recommendation: yes, re-measure on site basis, but not as a blocker. 1.42x is large enough to matter for a threshold and small enough that it does not change the qualitative finding (21/21 still defer at 0.0005 under either basis). So: run the 2 h site-basis sweep, but treat the derivation method below as basis-agnostic and instantiate the number once. Do not draft the amendment against row-basis and then re-do it.

One caution on the collapse arithmetic: I assumed each consecutive run = one site, which your 37/39 span-dominance supports but does not prove — a run could span two adjacent stacks. The real site count needs the actual position grouping, not my estimate. Treat 1.42x as approximate.

## 3. C3 — my ceiling derivation, with its purpose stated first

Purpose: The gate exists to detect a region whose occlusion count is qualitatively unlike the measured population — i.e. a representation or LD-construction failure — and to do so with a low false-defer rate, because every false defer discards a scientifically usable region. It does not exist to certify that occlusion is rare. That was the original error: 0.0005 was calibrated as "10x headroom over 6 observed NaN pairs," which encoded a belief that occlusion is rare into a gate meant to catch anomalies. The belief was false and the gate inherited it.

The derivation rule I propose: Anchor on the measured population's central tendency, not its edge, and set the bound where a genuine anomaly must lie: a multiple of the median, chosen so that (a) the observed range sits inside it with real margin, and (b) it still catches a several-fold excursion.

Concretely, from your 21: median 0.1888%, max 0.3527%, robust σ (1.4826·MAD) 0.0393%.

    median + 3σ_rob = 0.3067%   -> BELOW the observed max. A NORMAL region defers. REJECT.
    median + 4σ_rob = 0.3460%   -> still below observed max (0.98x). REJECT.
    2x median       = 0.3776%   -> only 1.07x over observed max. Too tight for n=21. REJECT.
    3x median       = 0.5664%   -> 1.61x over observed max; catches >=3x median. CANDIDATE.
    2x observed max = 0.7054%   -> 2.00x margin; catches >=3.7x median. CANDIDATE.

My proposal: ceiling = 3x the measured median, i.e. ~0.57% on row basis (re-instantiate on site basis). Reasoning:

- it is derived from a location statistic, not from where the sample happened to stop, so extending the sample moves it only if the population's centre moves;
- 1.61x margin over the observed max is honest given n=21 of 276 — the upper tail is unmeasured and a bound 7% above the observed max (the 2x median option) would be calibrated to a sample edge;
- it still fires on anything >=3x typical, which is the regime where "representation problem beyond isolated occlusion" actually lives.

What I explicitly reject, and why — this is the part I most want on the record: Do not adopt a multiple because it passes 21/21. Your C3 already says this and I want to reinforce it with the arithmetic: x8 passes 21/21 and so does x10, but a gate at 8 x 0.0005 = 0.4% would have been chosen because it clears the data, which is my original error inverted — fitting the threshold to the observation instead of to the purpose. The fact that my proposed 3x-median (0.57%) happens to pass 21/21 must be a consequence of the derivation, never its justification. If a future region legitimately sits at 0.6%, the gate should fire and we should investigate, not widen the gate.

The honest limitation: n=21 of 276. Your sample was pre-committed and systematic-by-span, which is the right design, and the flatness across size classes (0.13-0.35% with no size trend) is genuinely reassuring. But the upper tail is unknown. Costing it out from your own numbers: 3 h / 21 regions = 8.6 min/region, so a full 276-region sweep is ~39 h of VM time — not "minutes-cheap," a real but non-fire cost. My view: derive from the 21 now, with the margin above chosen to respect the unmeasured tail, and fold the full-sweep counts in as they arrive during the actual fire (every region computes its own count anyway). Do not spend 39 h ahead of the amendment.

## 4. One thing the amendment must say plainly

The recalibration is not a threshold tweak — it is a corrected empirical claim. The posted amendment's clause (d) carries an implicit factual assertion (occlusion is rare enough that 0.05% is generous headroom) which measurement has falsified by ~38x. The disclosure should state: the gate's calibration premise was wrong, the mechanism and the exclusion policy are unaffected, occlusion is a population-scale property of the substrate at 0.13-0.35% of rows, and the gate is re-derived from that measurement. Carry §8 as you have committed.

That framing matters because it is the honest version: we did not discover that our policy was wrong; we discovered that our estimate of how often the policy applies was wrong by a factor of 38. Those are very different claims and only the second one is true.

## 5. Answer to your ask #2, stated as a decision

Site-basis re-measurement: yes, run it (2 h), before drafting the number — but draft the derivation and purpose text now, since it is basis-agnostic. That sequencing costs nothing and avoids drafting twice.

## 6. NEW — surfaced by §5, not previously named by either of us. Flagging, not alarming.

Same-position rows are alternate ALT alleles at one site. A person cannot carry two different ALTs of the same site on the same haplotype, so the dosages of two such rows are structurally anti-correlated — their r is partly determined by the representation, not purely by population LD. At 7-11% of rows genome-wide, with multiplicities up to 21, the panel contains a substantial population of near-deterministic off-diagonal relationships.

I want to be careful about what this is and is not:

- It is not fabrication. The dosages really are anti-correlated; the LD is real as computed.
- It is not the occlusion problem and it does not change any answer above.
- But it is a fine-mapping consideration worth pre-registering awareness of: SuSiE on a submatrix containing several same-position rows sees near-collinear predictors, which is exactly the regime where credible sets inflate or split. That is a known property of split-multiallelic representation, not a defect we introduced.

Ask: when you draft, consider a sentence recording that same-position rows are retained and that fine-mapping at multiallelic sites carries this caveat. If you think it belongs in a separate note rather than this amendment, I agree — I would rather it be recorded somewhere than folded in awkwardly. I am raising it now because §5 is what made it visible, and an unrecorded observation becomes an unanswerable reviewer question later.

## Summary

- C1: concur — calibration, not normalization. Normalization branch withdrawn.
- C2: gate on sites, exclude/report rows, state both. Re-measure on site basis (~1.42x inflation estimated from your histogram); not a blocker for drafting the method.
- C3: ceiling = 3x measured median (~0.57% row basis), purpose-anchored, explicitly NOT chosen for passing 21/21; derive from the 21 with margin for the unmeasured tail rather than spending 39 h first.
- §4: my chain prediction refuted; your span-over-stacks unification is correct.
- §6: new same-position collinearity caveat, for the record.
