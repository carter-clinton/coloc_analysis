# Seth verdict — adjudication CONFIRMED, oracle error owned, two corrections (as received)

> Provenance: received 2026-08-19 ~15:59 EDT, pasted by Carter into the NCSU
> session, in reply to the brief-blind review request (6,875 B / e09ebbf1c1b20065a3ab3afa79a0bcde).
> AS-RECEIVED transcription of a chat-rendered body; no byte anchors supplied.
> Headline: "your adjudication is CORRECT and the oracle error is MINE" — plus two
> substantive corrections to OUR reading (§4 chaining, §5 the unverified
> same-position premise) and the 0.0005 provenance confession (§8) for the
> amendment rationale.

---

Seth — your adjudication is CORRECT and the oracle error is MINE. Attack delivered, with two things you missed.

Verdict up front, because you asked for loudness in either direction: I find no credible detector-defect story. Your adjudication (1)-(5) survives my attack. The oracle was a false extrapolation and it was mine — the record tags it "Seth 5/5 vs the geometry verdict" and that is accurate attribution.

But two of your specific attack surfaces resolve differently than you concluded, and one premise you are treating as established is unverified in exactly the same way my oracle was. That second one is the reason I would not fire on option A yet.

## 1. My error, named precisely

The June geometry verdict established: of the 6 observed NaN pairs, 5 are ref_span_overlap and 1 is second-order, involving 11 variants and 7 deletions. That is a statement about the NaN-implicated subset. My prototype fixture then encoded it as EXPECTED_DELETION_SIZES and EXPECTED_OCCLUDED_IDXS — i.e. as the window's entire inventory — and that assertion propagated into test_occlusion_span_filter.py:186 and into my check_manifest_rows(expected_records=5).

Your point (2) is the correct diagnosis and the logic is airtight: observable NaN is a strict subset of geometric occlusion. NaN requires complete-case zero variance at that pair; span coverage requires only geometry. So every NaN-implicated occlusion is a geometric occlusion, but not conversely. oracle_subset_of_observed: True with oracle_missing_from_observed: [] is precisely the signature of a correct detector against a too-small oracle — no shift, no displacement, nothing missing. Your point (3) follows: STEP 7's actual purpose, index-origin validation, PASSED. A subset match at exact indices cannot happen under an off-by-one.

Two consequences I own:

1. check_manifest_rows(expected_records=5) is now WRONG and would HARD_STOP on a correct 231-record manifest. It needs to take the detector's own count, not a literal. This is the fourth instance of the same defect class in my prototype (hardcoding a value that should be read from the system) — after 256, 0.0005, 120, 276.
2. My README's "5 occluded vs 51 ceiling, 10x headroom" is false on real data. It is 4.5x OVER. Retract it wherever it propagated.

## 2. Attack surface 1 — detector-defect stories. I find none, and the arithmetic is consistent.

I checked whether 231 is even the right order of magnitude rather than accepting it:

    window span >= 6.40 Mb over 102,421 rows -> mean spacing ~62 bp/variant
    implied mean occluding span to yield 231 from 7,951 deletions ~ 1.8 bp

That is exactly the expected shape: most indels are 1-2 bp and cover nothing, while a long tail (max_span=170) does all the occluding. 231 is what you get from a realistic deletion length distribution, not from a rule error. Combined with your 22 green fixture tests pinning the strict POS_D < POS_V rule, I have no defect story.

## 3. Attack surface 2 — 7.8% multi-base REF is NOT prima facie an artifact

7,951 / 102,421 = 7.76%. For WGS short-variant calls, indels typically run ~8-12% of variants, multi-base REF also captures MNPs, and this is a window not a genome. 7.8% is in range. I would not treat it as evidence of un-normalized multiallelics on its own. Your suspicion is reasonable but the number does not carry it.

## 4. ★ Attack surface 3 — the consecutive runs. You said you could not reconcile them; here is the reconciliation, and it is NOT what either of us assumed.

You read consecutive runs as "multiallelic split records co-located under one deletion span." Test that geometrically:

    run of 4 consecutive indices needs ~250 bp  -> 1.5x local density vs window mean
    run of 6                        ~374 bp  -> 2.2x
    run of 7                        ~437 bp  -> 2.6x
                                     max_span = 170 bp

One span cannot cover a 7-run at mean density. So the "one long deletion" story requires 2.6x local density and is not general.

The reconciliation you were looking for: consecutive OCCLUDED indices do not require a single covering span. A chain of co-located deletions, each occluding its own neighbour, produces a run of consecutive occluded indices with no same-position records and no long span.

Region 1's own documented tangle is exactly this shape, at k=3:

    5922716 DEL(7bp)  ->  occludes SNP 5922718  ->  5922724 DEL(31bp)
    indices              46713 / 46714 / 46715 — consecutive

Scale that to a locally clustered group of k deletions and you get a k-run. So the runs are geometry, as you concluded — but via chaining, not via one span, and chaining is fully compatible with same-position = 0. That resolves the contradiction you flagged as unreconciled.

Cheap discriminator, read-only: the detector already records occluder_idx per occluded variant. Group each run by it. 1 occluder -> many occluded = one long span (needs the density story). many occluders -> many occluded = chain. I predict chain-dominant, and it is one sort | uniq -c on output you already have in /home/jupyter/step7_vv.txt.

## 5. ★ The premise you are treating as established, which is UNVERIFIED — my error, second instance

"Note the oracle also asserted 'same-position variants = 0 (bcftools norm -m fixes none)' — reconcile that with the consecutive-run structure if you can."

Do not reconcile it. Retire it. That 0 was measured on my 11-variant fixture, never on the real 102,421-row window. It is the same false extrapolation as the 7/5 oracle — fixture scope promoted to window scope — and nobody has measured the real number.

This matters more than the reconciliation, because it is the actual discriminator between your two competing readings:

- same-position ≈ 0 on the real window -> normal clustered indel geometry; recalibrate the ceiling and proceed;
- same-position large -> un-normalized multiallelics, which is precisely the "variant-representation problem beyond isolated occlusion" that clause (d)'s interpretation sentence contemplates. In that case the correct action is upstream normalization, and recalibrating the ceiling first would launder a representation defect into the panel.

One line, read-only, no genotypes:

    awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -d | wc -l   # duplicate positions
    awk '{print $1":"$4}' data/aou/region1_window.bim | sort | uniq -c | sort -rn | head -5

I would not choose between A/B/C before that number exists. It is seconds of compute and it can invalidate the premise all three options share.

## 6. Attack surface 4 — "231/102,421 is negligible downstream." Mostly yes, with one caveat you should not wave past.

0.23% of variants is negligible as a fraction. But your own framing of the mechanism cuts against pure fraction-counting: occluded variants are not a random 0.23%. They sit in locally deletion-dense, repeat-rich neighbourhoods — and those are systematically not a random sample of the genome. The question that matters for SuSiE/coloc is not the count, it is whether excluded variants land inside credible sets.

That is measurable and cheap once you have counts: what fraction of excluded variants are within, say, 100 kb of a known association signal, or more directly, do any Stage-A credible sets touch an excluded position. Region 1 already gives one instance that says take this seriously: the occluded SNP at 5922718 was present in 7 of 9 AFR traits with genuine effect estimates. That is the opposite of a variant nobody would have tested.

So: negligible in aggregate, plausibly non-negligible at the loci that matter. I would not state "nothing scientific is lost" — that is the framing I objected to on the coverage gap and it is the same shape here.

## 7. On the decision space — I will not pick, but I will rank the premises

You asked me to attack the premises, not choose. All three options share the premise "the detector is right and the ceiling needs recalibrating." My attack leaves that premise standing except for the same-position gap in §5, which could reassign the whole problem from calibration to normalization. So:

- Any option is premature until §5 is measured. That is my only firm procedural claim.
- C (detector-only over 276 windows) is the one whose premises I can least fault: it is minutes, banks nothing, and replaces an n=1 calibration with a distribution. My ceiling was calibrated on one region's NaN-implicated subset — n=1 and the wrong quantity. Amending from a 276-region distribution fixes the actual defect in how 0.0005 was derived. Note it also answers §6 partially: if occlusion rate varies wildly by region, that is itself a finding.
- A's premise — that a deferral is a useful empirical record — is true but weak: you already know it will defer (231 > 51.2 is arithmetic, not an experiment), so the information gain is a machinery test, not a measurement. Worth something, not worth a fire slot before §5.
- B's premise — that you can write a correct recalibration now — is the weakest: with n=1 you would be picking a new constant with no better basis than the one that just failed. Amend from the distribution, not from region 1.

## 8. Where the ceiling came from, since you will need it for the amendment

Stated plainly for your provenance trace: 0.0005 was my figure. I derived it in July as "~10x headroom over the observed 6 NaN pairs at n_var 102,421" — i.e. calibrated against observed NaN count, on one region, for a policy that then got re-purposed to geometric exclusions. Every one of those three steps is a defect:

    premise  : ~6 per 100,000  = 0.0059%
    measured : 231 per 102,421 = 0.2255%    -> premise low by ~38x

The re-purposing is the deepest error: the amendment says "the same fractional gate as the withdrawn ceiling, re-purposed to exclusions" — and I wrote that sentence without re-deriving the constant for the new, strictly larger quantity. A gate calibrated on NaN counts cannot be transplanted onto geometric-occlusion counts. That belongs in the amendment's rationale.

## 9. Your point (5) — unqualified agreement

Defer, disclose, amend openly; never touch the constant quietly. The pre-registration's own machinery is the sanctioned route and it is working: a gate calibrated on a false premise fired before anything was banked, on first real-data contact. That is the system catching my error at the cheapest possible moment.

## Summary of what I am asking for

1. Measure same-position on the real window (§5) before choosing A/B/C. One line, seconds.
2. Group the consecutive runs by occluder_idx (§4) to confirm chain vs single-span. One line, on output you already have.
3. Treat my expected_records=5 and my README's "10x headroom" as retracted (§1).
4. When you amend, carry §8: the constant was mine, calibrated on the wrong quantity, with n=1.

No line of your adjudication do I want to argue. The oracle error was mine, you found it with a real-data test I did not have access to run, and the two weeks of mutual error-finding worked in this direction too.
