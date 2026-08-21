# Seth attack on the instantiated amendment — two defects, one gap in his own C2, one framing correction (as received)

> Provenance: received 2026-08-20 ~21:41 EDT, pasted by Carter into the NCSU session, in reply to the
> brief-blind cover courier (3,212 B / c917b1a1e0bd97c4b619249d74139ff9) + the instantiated amendment
> (31,685 B / b8f9a978c9bdbc7892f97b5d90cf9d27). AS-RECEIVED transcription; no byte anchors supplied.
> Dispositions FIVE-FOR-FIVE identical to ours, reached before reading ours. Net asks: (1) fix the 1.18x
> count-ratio-vs-fraction-ratio trap (BLOCKING); (2) one sentence pre-empting the permissiveness
> comparison; (3) decide the multiplicity companion check (add, or disclose the gate as
> multiplicity-blind); (4) give the §6 collinearity note a specific home; (5) keep the two POSTING_DATE
> occurrences in lockstep. Status line for the record, adopted: measurement banked; amendment drafted,
> NOT posted; code constant unchanged; fire HELD; an agent never posts and never fires.

---

Seth — attack on the instantiated amendment. Two defects worth fixing, one gap in MY OWN recommendation, and a correction to how this run is being described.

Dispositions first (your §2 ordering), then the attack. Arithmetic all independently recomputed from your SLOT_LEDGER; I did not take a number on report.

## 0. A framing correction before anything else — this is not "banked and verified"

The message that reached me said "the run is banked and verified." The amendment says the opposite, and the amendment is right: nothing fired, nothing banked, Stage A untouched, VM stopped, no OSF contact, and _OCCLUSION_ANOMALY_FRACTION is still 0.0005 in code. What is banked is the 21-region measurement sweep and the draft amendment. The panel run has not happened.

I am flagging this because "banked and verified" is exactly the kind of status drift that put a wrong output path in my head for weeks. The correct status line is: measurement banked; amendment drafted, NOT posted; fire still HELD.

## 1. My dispositions on the site-basis numbers, stated before reading yours (§2)

| Candidate | Site-basis value | My disposition |
|---|---|---|
| median + 3σ_rob | 0.2507% | REJECT — 0.93x the observed max; a normal region defers. |
| median + 4σ_rob | 0.2781% | REJECT — 1.03x the observed max. Hugs the sample edge. |
| 2x median | 0.3370% | REJECT — 1.25x margin, too tight for n=21 with an unmeasured tail. |
| 2x observed max | 0.5396% | CANDIDATE, not adopted — anchored on where the sample stopped. |
| 3x median | 0.5056% | ADOPT — 1.87x margin, anchored on a location statistic. |

Identical to yours, five for five, reached before reading your §3. And I recomputed every cell from the ledger: 0.2507 / 0.2781 / 0.3370 / 0.5396 all reproduce exactly; 3 x 0.1685 = 0.5055 vs your printed 0.5056, the 0.0001 pp you already disclose as the unrounded-median artifact. Your §4 substitution did not smuggle a different argument in. My row-basis rejection of median+4σ was "below the observed max"; on site basis it is 1.03x above, and you re-grounded it on "hugs the sample edge" — which is my own stated reason for rejecting 2x-median, applied consistently. The logic is unchanged; only the arithmetic-relation words moved, exactly as you said.

## 2. ★ DEFECT 1 — your §5 question answered: NO, the two bases are NOT reconciled clearly enough. There is an arithmetic trap in the text.

You asked whether a reviewer reading only the paste block can reconcile the row-basis §8 block with the site-basis gate. No — and worse, the document hands them a conversion factor that gives the wrong answer.

The Basis conventions paragraph says row-basis counts exceed site-basis counts "by a representation-dependent factor — measured here as 1.18x on average." A reviewer will apply that to the fractions. Watch what happens:

    site median 0.1685%  x 1.18  =  0.1988%
    actual row median             =  0.1888%      -> overshoots by 5.3%
    true fraction ratio           =  0.1888/0.1685 = 1.120x, not 1.18x

The 1.18x is the ratio of occluded counts (rows/sites). But both percentages also carry a denominator that differs — n_rows / n_sites is itself >1 (region 1: 102,421/96,708 = 1.059). So the ratio of fractions is 1.18 / 1.059 = 1.114, not 1.18. A count-inflation factor cannot be applied to a fraction whose denominator also inflates.

This is the same defect class as the original error — a quantity measured on one object asserted about another — reappearing inside the document that corrects it. Fix: state explicitly that 1.18x is a COUNT ratio and does not convert between the two percentages, and give the measured fraction ratio (~1.12x) separately, or drop the numeric factor from that paragraph and rely on your existing practice of always restating both figures.

## 3. ★ DEFECT 2 — the no-calibrate-to-pass paragraph makes a comparison that undercuts itself

The paragraph rejects 8x and 10x the withdrawn constant (0.4% and 0.5% row basis) as calibrate-to-pass. But the adopted ceiling, in the document's own row-basis restatement, is 0.5664% (row basis).

    REJECTED as calibrate-to-pass : 10x withdrawn = 0.5000% (row)
    ADOPTED                        : 3x site median = 0.5664% (row)

The adopted ceiling is MORE permissive than a candidate the same paragraph rejects. That is not an error in the reasoning — the distinction is real and is about derivation method, not magnitude — but as written it reads as though 0.4-0.5% is too loose and 0.5664% is fine. A hostile reviewer will quote those two lines side by side.

Fix: say it outright. Something like: "Note the adopted ceiling is numerically slightly more permissive than the rejected 10x-withdrawn candidate. The objection to 8x/10x is not that they are too loose; it is that they would have been selected for clearing the sample. The adopted value is more permissive and still rejected them, which is the point: the derivation is independent of what passes." Stating it pre-empts the quote; leaving it implicit invites it.

## 4. ★ GAP IN MY OWN RECOMMENDATION — the site-basis gate is blind to a real anomaly class

This is the most substantive thing in this reply and it is a hole in the advice I gave you in C2. You implemented it faithfully; I under-specified it.

A site-basis gate counts occluded sites and is invariant to multiplicity — that is exactly why I recommended it. But invariance cuts both ways: a region can have a perfectly normal site-basis occlusion rate while excluding a pathological number of rows.

    region with occluded sites = 164 / 96,708 = 0.1696% (site)   -> near median, gate does NOT fire
      at mean multiplicity 1.18 (normal):    ~194 rows excluded = 0.19% of rows
      at mean multiplicity 5:                 ~820 rows          = 0.80%
      at mean multiplicity 10:               ~1,640 rows         = 1.60%
      at mean multiplicity 21 (observed max): ~3,444 rows        = 3.36%

A region excluding 3.4% of its rows would sail through a site-basis gate reading 0.17%. And a region whose occluded sites are systematically high-multiplicity is a representation anomaly — precisely the class clause (d) exists to catch.

Recommended fix, cheap and already measured: add a companion check on the row/site inflation ratio at occluded sites, per region. You have the population value already — 1.18x mean across 21 regions — so the guard rail is derivable from data in hand, not a new measurement. A region whose occluded-site inflation is several-fold above 1.18x should DEFER even if its site fraction is normal.

I am deliberately not proposing the multiplier for that companion check in this reply, for the same reason I would not pick the main one from "what passes": you have the 21-region inflation distribution and I do not. Derive it the way we derived the main ceiling — from the location statistic, with margin for the unmeasured tail — and it should be a second ledger slot, not a hardcoded literal.

If you would rather ship the single-metric gate now and add the companion in a follow-up amendment, that is defensible — but then the limitation paragraph must say the gate is multiplicity-blind, because an undisclosed blind spot in a pre-registered detector is the reviewer question with no good answer later.

## 5. Checks that PASSED my attack

- Factual correction (a). 7,951 / 7 = 1,136x; you say "~1,140x" — correct at the stated precision. 7/102,421 = 0.0068% reproduces exactly. The gnomAD framing (indels ~14.8%, deletions roughly half) is the right published anchor and makes the claim falsifiable without data access, which is the honest way to state it.
- "Zero pairs are same-position" STANDS. I tested whether that is in tension with 8.2% duplicate rows: P(none of 11 NaN variants sits at a duplicate position) = (1-0.082)^11 = 0.39. 0-of-11 is unremarkable — no tension, and your scope-limiting sentence is the right treatment. This is a case where the surviving claim genuinely survives.
- §8 carried verbatim. Checked against my text; unedited, and the basis label you added ("both figures are row basis") is a correction I should have made myself when I wrote it.
- Harness cross-check. Pre-committing to discard all 21 results unless region 1 reproduces 231 exactly, with the assert preceding the summary, is the right discipline — it makes the sweep falsifiable rather than merely reported.
- Derivation-table dispositions. All five reproduce; margins 0.93 / 1.03 / 1.25 / 2.00 / 1.87 all correct.
- Clause (g) enumeration and the criterion-vs-gate distinction in the fencing paragraph: correct, and worth having stated explicitly since the posted record fences criterion-tuning.

## 6. Two smaller notes

- §6 collinearity caveat. My same-position/near-collinearity note is not in this amendment. I said last round it might belong in a separate note and I still think so — but "somewhere" needs to become a specific place, or it will be nowhere. Your call which; I would rather it be a one-line entry in the deviations log than an unwritten intention.
- Provisional posting date. POSTING_DATE = 2026-08-21 is today's date. If Carter posts later, the one-token edit plus guard all re-run is the right protocol — just do not let the ledger and the paste block drift apart, since they carry the date twice.

## Summary of what I am asking for

1. Fix the 1.18x conversion trap (§2) — it is a count ratio, not a fraction ratio; the fraction ratio is ~1.12x. This is the one I would block a post on.
2. Pre-empt the permissiveness comparison (§3) — one sentence.
3. Decide on the multiplicity companion check (§4): add it, or disclose the gate as multiplicity-blind in the limitation paragraph. My C2 advice was incomplete and this is my correction to it.

Everything else: no objection. The derivation, the dispositions, the factual correction, and the evidence discipline all survive attack.

Status line for the record: measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires.
