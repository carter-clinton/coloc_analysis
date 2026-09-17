# Courier to Seth — reply to his 2026-09-17 Finding 2 review (⛔ UNSENT)

**Status:** DRAFTED 2026-09-17, **NOT SENT**. No agent contacts Seth — Carter sends it.
**Replies to:** `.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md`
(as pasted; not byte-verified).
**Uses only the corrected Rao-Scott table** (pooled rate estimated from the subset under test, quick
`260908-uer`). No superseded fixed-rate figure appears below.
**Source of every disclosure number:** `.planning/osf_deviations.md`, the 2026-09-03 tail-disclosure
entry, §(7), §(10a), §(10b) and §(10e), as amended by quick `260917-irg`. Point 1's shares and
effective design effects are computed from the §(10b) table and are deliberately NOT in the disclosure.
**Point 2's indented replacement sentence** is word-for-word the §(10b) conclusion (markdown aside).
**Scratch source:** `SETH-PASTE-3-reply-to-finding2-review-DRAFT.txt`, md5
`042fe4798429f30fa5b4bbb59dee9419`, 4587 B; the paste block below is that file byte-for-byte.
**Disclosure status:** still DRAFTED — NOT POSTED. Posting is Carter's decision.

---

````
Seth — taken in order. Your §2, §4 and §5 change the draft disclosure (still DRAFTED — NOT
POSTED); §1, §3 and §6 leave it as it stands. Nothing here reopens anything.

1. DISPOSITION — agreed. One number needs restating, and your own rule applies to it.
Your 36% is (deff - 1)/(phi - 1) using the POOLED deff, 1.360. No test applied that value: the
correction is per region, so the design effect each test effectively applied is the ratio of its
own columns —
  headline (drop sub13)   1.988 -> 1.675   effective deff 1.19
  mirror   (drop sub12)   1.992 -> 1.579   effective deff 1.26
Your metric on those is 19% and 26%, not 36%. A second, equally defensible reading — the share of
the excess dispersion the correction actually removes, (phi_unc - phi_corr)/(phi_unc - 1) — gives
32% and 42%. One phrase, "clustering carries X% of the excess", supports numbers from 19 to 42
depending on which quantity you mean, which is your §3 rule pointing at itself. So no share goes
into the disclosure at all.

2. THE STRADDLE — objection accepted; the disclosure changes.
"Straddling 0.05", "coin flip" and "significance is an artifact of analytic choice" come out
everywhere they carry the conclusion. The dated 2026-09-08 correction note keeps its original
wording, because it records what that edit did. The replacement, in substance:
  Under either treatment of the chr15 window overlap, the design-corrected dispersion carries at
  most weak evidence of between-region heterogeneity beyond measured clustering: p = 0.0326
  dropping 00060__sub13 and p = 0.0517 dropping 00060__sub12 (-log10 p 1.49 and 1.29, the same
  evidence), and p = 0.2171 with both chr15 windows dropped. The magnitude is unidentified, and
  the dispersion is not robustly distinguishable from a clustering-only explanation.
Three differences from your sentence, each deliberate:
  (a) Both p-values stated. 0.0517 is not in "0.03-0.05"; rounding it into that range reports
      which side of the line it fell on, just less visibly.
  (b) "At most." The five regions with too few clusters carry deff 1.0 — no correction — so a
      fuller correction lowers phi. These p-values are, if anything, too small.
  (c) The drop-both result stays. The weak evidence is carried by chr15, and a reader should see
      that.

3. "INTERCHANGEABLE" — partly accepted.
You're right that they are not statistically equivalent; their design effects (1.096 vs 1.359)
are already in the disclosure and will stay next to the p-values. But I won't pick the
better-corrected window. Both p-values are now known, so choosing either — even by ICC precision
— is choosing an analysis after seeing where it lands: your §2 point, applied to the selector.
Both stay reported and neither is privileged. "Interchangeable" will be scoped to what is true:
equally defensible choices, made in advance, for handling the overlap.

4. §3 — agreed, on the estimator and on the rule.

5. CREDIT — correction accepted, and the record agrees with you.
The within-window argument and the c=2 simulation are in our 2026-09-04 correction. Your
contribution was the between-window hypothesis and the push to examine non-independence at all.
The credit line in my courier was wrong. The disclosure never carried it; its reviewer
accounting will now state the provenance as you put it — the between-window hypothesis was yours
and was wrong; the within-window mechanism was ours, and the measurement confirmed it exists
(ICC 0.73) without showing it accounts for the dispersion; the Rao-Scott test was proposed by
neither of us.

6. 22.7% vs 28.5%, and the ICC's denominator — both adopted.
  573 of 2521 pairs (22.73%) are anchored by two deletions.
  719 of 2521 (28.52%) share an occluding deletion with at least one other pair (303 clusters);
  the other 1,802 (71.48%) are singletons.
  ICC 0.729 is stated for those 719 pairs only, with that denominator attached.
All three are on the per-region-sum basis (a pair in two regions counts twice), as the
neighbour figure already is.

7. FINDING 1 — agreed, it is the result.
Two of your words won't be carried into the text: "universal" (it is 21 of the 21 regions
scanned, not all 276 in the panel), and "no geometric predicate can see" (what is recorded is
that these rows survive the posted predicate, not that no predicate could catch them). "The
retained NaN-raise is blind to it by construction" is right — these rows are defined, so they
never produce a NaN.

The disclosure stays DRAFTED — NOT POSTED. Posting is my decision, and I haven't made it.
````
