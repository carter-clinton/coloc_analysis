# Reviewer's Stage C adjudication 2026-09-18 — the raising region (AS RECEIVED, ⛔ NOT BYTE-VERIFIED)

**Received:** 2026-09-18 — pasted by Carter into the session at **~18:46 EDT**. ⛔ **Not
byte-verified** against his original message; chat rendering may have altered blank lines or other
whitespace. The time is Carter's in-session record; nothing in the filesystem can confirm it.
**Scratch source:** `SETH-STAGEC-ADJUDICATION-2026-09-18-as-pasted.txt`, md5
`5e35a093a1920ad0f453ae64b353f2e4`, 23,225 B, 141 lines. The fenced block below is that file
byte-for-byte, first line included.
**What he read:** the options draft v2 at `57a3105` and the code at `74f962d`. He states he did not
read `STATE.md`, `HANDOFF.json`, or anything under `.planning/quick/` or `.planning/debug/` other
than the draft itself, did not run the checker, and has not seen `.planning/osf_deviations.md` —
where he cites the ledger or the Stage-B halt record he is citing the draft's citation.
**What it is:** a **brief-blind adjudication**, delivered as a position and not a ruling. It answers
the draft's seven questions, names four framings it calls wrong, lists five omissions, and asks for
**no OSF amendment**.
**Recorded in:** `DEC-2026-09-18-stage-c-nan-posture-adopted` (the posture Carter adopted, the
rejections with his reasons, and **three** determinations of OURS); `§(11)` of the 2026-09-03
entry in
`.planning/osf_deviations.md` (the raising-region accounting, still **DRAFTED — NOT POSTED**);
`R5-RAISED-NAN` in `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`;
and the `STAGE-C RAISE POSTURE` block in
`.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`.
⚠ **The arithmetic slip he caught, recorded here because v2 is NOT edited.** The options draft v2
is the **couriered artifact and stays byte-frozen**. Its **Q3 planning number scaled 1-in-21 to
≈13 regions** using **`m2_region_00149`** — the **PREDICTED** case — as if it were observed, i.e.
it counted the predicted case as the observed rate; the **observed** Stage-B denominator is the
regions actually run (`m2_region_00057`). The draft does label the figure *"For planning only, not
a calibrated rate"* and does flag that the one case is predicted — the defect is that it then
scales that case as the rate. ⛔ **Neither figure is calibrated.**
⚠ **A correction of OURS to his Q5 fix, recorded here because it is ours and not his.** His Q5
prescribes moving the three coordinate-only occlusion artifacts *"out of the `if ok:` block"*.
Measured at `74f962d`, that edit is **insufficient**: a raising region raises inside
`pln.plink_ld_to_npz(...)` and jumps to the outer `except`, **never reaching the `if gs_mode:`
block at all**, so de-indenting the uploads fixes `verify_failed` only and leaves mk7ze
P248-250 false for exactly the raising class. **His diagnosis and his requirement stand; the
prescribed edit was too small**. The fix planned in `quick-260918-qz5` **will** upload from a
helper called before the reader plus a guarded call in the `except`; ⛔ none of it exists
yet. Recorded in full in
`DEC-2026-09-18-stage-c-nan-posture-adopted`, determination **(c)**.
⛔ This is correspondence. It is **not a source for the record**: the treatment it adjudicates is
pre-registered, the accounting it asks for is in the ledger entry above, and the disclosure that
carries it is still **DRAFTED — NOT POSTED**.

---

````
Seth — Stage C adjudication: the raising region. Brief-blind, against draft v2 at 57a3105 and code at 74f962d.
What I read. Draft v2 in full (30,074 B, md5 46537925…). Both posted bodies from my own copies, verified before reading a citation: trsx5 9,695 B / c19be8b2…; mk7ze 22,945 B / 13a49f54…. run_native_ld_panel.py, fire_verifier.py, plink_ld_to_npz.py fetched at 74f962d. Every file:line I rely on below I read at that commit; every trsx5/mk7ze line I quote I read in the posted body. I did not read STATE.md, HANDOFF.json, or anything under .planning/quick/ or .planning/debug/ other than the draft itself. I did not run the checker.

Citation check: every draft citation I tested lands on the text it claims (P2 at :1287-1291, :1244-1250, :1421-1422; C4/X1 at :1257-1282 and :1104-1110; C7 at :1009-1015; the raise at plink_ld_to_npz.py:218-228; verifier vocabulary at :300-303; trsx5:25-59; mk7ze P247-250, P300-302, P316-318, P321-322). I found no citation that is wrong against the text or code. The errors I find are in framing, not in anchoring.

Labels as in the draft: TEXT / CODE / READING. Where I give a reading it is marked.

0. Framing correction that changes the shape of Q1 and Q2
The draft's one-line question is "neither posted body assigns such a region to an outcome branch." That is true, and it is the wrong test. The posted document pre-registers two independent contracts, and the three branches belong to only one of them:

Contract 1 — occlusion handling (trsx5:23-31, :43-49): criterion, lockstep exclusion, manifest, anomaly gate, and the three BRANCH_AFR_OCC_* outcomes. trsx5:53 lists exactly these five objects as "fixed before any occlusion-handling code fires." The branches are the outcome space of occlusion handling — every trigger in T3/T4 is an occlusion count.
Contract 2 — the raw-panel NaN-raise (trsx5:39; mk7ze P321-322): "the raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it." Its outcome space has one element: raise, bank nothing.
A raising region is the realized outcome of Contract 2. Asking which Contract-1 branch it falls under is a domain error — the same one I made on line 275 (asking whether a NaN with no occlusion falsified a sentence quantifying over occlusions). The draft's own B-READING-1 has the fact that dissolves it — the surviving class "has no covering record for EITHER member … so it is not an occlusion under clause (a)" — and does not draw the conclusion: if it is not an occlusion, the occlusion branches are not its outcome space, and its absence from them is not a gap in the list.

Two consequences that run through everything below:

(i) The disposition IS pre-registered. The draft says of Option A, "the disposition is what is at issue." I disagree. T1 is the disposition, at the only level the posted text speaks to: a NaN-bearing panel is not banked and is not coerced. What is unregistered is narrower — the label the region carries in the record and the closeout accounting. Those matter, but they are reporting, not treatment.

(ii) A raise is not a deviation. T6 says deviations are logged. A region raising under T1 is the pre-registered behaviour executing as specified. Logging it under "deviations" mislabels a realized outcome as a departure from plan, in the one file a reviewer reads to find departures. It should be recorded as a realized Contract-2 outcome / coverage disclosure, with the sentence "this is not a deviation from pre-registration; T1 fired as written" attached. The draft treats T6 as the fallback surface throughout (A-R1, Q1); the surface is right, the label is wrong.

(iii) Every raising region ALSO has a Contract-1 classification, and it is computed. The occlusion count and gate verdict are produced before plink runs (:1066-1082, :1211-1212) and the count reaches the TSV (C2). So the region is NONE / EXCLUDED / (DEFERRED) on the occlusion axis and raised on the NaN axis. READING: the branch is the classification clause of trsx5:43/45 ("contains no occlusion-undefined pair" / "contains >=1 occluded variant under the gate"); the consequence clause ("the panel … stand[s] unmodified" / "fine-mapping proceeds on the reduced set") describes what follows when a panel exists. On that reading the region does fall under a posted branch — on the axis the branches classify — and separately banks nothing on the other axis. I hold this as a reading, not a finding, but it is the reading under which the closeout distributions (T7) stay complete: raising regions appear in the branch distribution by their computed count, with an orthogonal raised flag.

1. Answers to the seven questions
Q1 — Does a raising region fall under a posted branch? If not, amendment before Stage C, or T6?
Not as a fourth member of the branch list, because it is not an occlusion outcome (§0). On the occlusion axis it carries whichever branch its computed count gives it (§0-iii, a reading). T5's closing sentence enumerates three prohibited acts — silent exclusion, fabrication, criterion-gaming — as "the only paths not on this list." A T1 raise is none of those; reading T5 as "every region must land in one of three tokens" promotes a sentence about occlusion outcomes into a sentence about all region outcomes.

Amendment before Stage C: no. T1 already commits the treatment. What is owed before Stage C is a statement of accounting, and there is already a posted-before-production vehicle for it: the drafted disclosure, whose own text commits to being "posted BEFORE production testing" (osf_deviations.md:720-724, per the draft). Add one paragraph to it:

A region whose raw-panel NaN-raise contract (trsx5:39) fires during the production run banks no panel, is not coerced, receives no post-hoc treatment, is classified on the occlusion axis by its computed count, and is reported at closeout as an unbanked region with its raise classified as known-class (boundary-adjacent pairwise-undefined) or unclassified. The count of such regions is a coverage result, not a deviation.

That rides on a document that must be posted first anyway. No separate amendment cycle — and I have argued elsewhere on this thread that amendment cycles are themselves an error surface.

One caveat against my own answer. trsx5:53 fixes the branches "before any occlusion-handling code fires," and Stage C has not fired, so an amendment could still be posted cleanly. The reason not to is that it would change no treatment — it would only add a label — and a posted amendment that adds a label invites the reading that the label was a policy choice.

Q2 — Would routing to DEFERRED change what DEFERRED means? Does "NO new token" reach beyond the companion?
Yes, it changes the meaning, and B should be rejected — for a reason stronger than the definitional one.

Definitional: T3 defines DEFERRED by trigger (count exceeds gate), and 00057's gate did not fire — a gate-firing region returns at :1110 and never reaches :1233. Routing a raise there records an anomaly the gate did not find. Agreed with B-R1.

"Deferred for re-diagnosis" (T2) presupposes a path back to banking. Under the current pre-registration there is none: the only ways a raising region banks are coercion (prohibited, T8) or a criterion change (fixed, trsx5:53). DEFERRED names a pending outcome; a T1 raise is a terminal one. That is the meaning change.

The stronger reason: B converts the contract raise into a verifier PASS whose stated rationale is "THE GATES WORKING" (fire_verifier.py:335-336). The raise is the instrument that surfaced this entire class in region 1. Under B, the first time it fires in production, the check-in is green and no human is told. That is weakening the raw contract at the verifier layer — the thing trsx5:39 forbids at the reader layer, moved one file downstream. B is disqualified on that alone.

"NO new token" (mk7ze P316-318): does not reach beyond the companion. The sentence is "[the companion] condition introduces NO fourth branch and NO new token: a region deferred by EITHER … routes to the SAME BRANCH_AFR_OCC_DEFERRED." Its subject is the companion condition and its object is the two gate conditions. Reading it as a general anti-proliferation rule for all dispositions is scope promotion of exactly the kind §(a) of mk7ze exists to prevent. B-R2 is the promoted reading.

Q3 — Does the posted text speak to an operator stop? Does a truncated run raise a T7 question?
It does not speak to it; the choice is operational. But the answer to "stop or continue" should not be either — it should be conditional on classification, and the record should say so before the fire:

a raise whose mechanism is the known class (boundary-adjacent pairwise-undefined, confirmed by the in-perimeter pairwise diagnostic the Stage-B halt record already ran) → the loop continues (Option A behaviour);
a raise that is not that class → stop and diagnose (Option C behaviour), because an unclassified raise may be a different defect and 275 more regions should not bank behind it.
The Stage-B halt record's "must not carry --fail-fast into Stage C at an unknown per-region failure rate" (260824…:104-107, per the draft) is right about the flag, which halts on banked and deferred regions too (P4). It does not settle whether an operator should stop on an unclassified raise. They should.

The T7 question under C: yes, if the operator does not resume. Resume recomputes only error: regions (C5), so a pause-and-resume changes nothing about which regions are measured. A stop that is not resumed truncates the present-rate denominator and is a closeout disclosure. The pre-fire record should state the resume rule so "re-diagnosis" cannot become an occasion for post-hoc treatment: re-diagnosis classifies the raise; it never changes the region's inputs or the criterion.

Q4 — Does the R4-COVERAGE precedent (C7) govern?
For the mechanics, yes; it is not sufficient. deferred_infeasible_square is the right template for "unbanked, outside the branch list, disclosure obligation with a named enforcer, numbers owed at publication." Adopt it.

It is not sufficient because the two cases differ in kind. An infeasible-square region is unbanked for a compute reason; nothing about the data is in question. A raising region is unbanked because a scientific contract fired, and the contract's message is known to mis-state the cause (C1: the raise blames zero-variance, measured false for 00057). So this class carries an obligation the precedent does not: each raise must be classified (known-class vs not), because an unclassified raise is potentially a different defect. X4 (no enforcer) should be closed at the point the status is added, exactly as the draft says for F — and the enforcer should check classification, not just count.

Q5 — Does honouring mk7ze P247-250 require a raising region's gate evidence to reach the bucket? Before Stage C?
Yes, and yes — and this is not a disposition question. It is a code defect against a posted commitment, and it is the one item that must land before Stage C regardless of A–F.

mk7ze P248-250, verbatim: "Every region computes its own occlusion count AND its own occluded-site inflation during the production run, so both complete distributions fold in at closeout." The gate sidecar is computed for every square region before plink (:1066-1082) — the commitment's first half holds. But the upload sits inside if ok: (:1245, :1277-1282), so a raising region's inflation never leaves the VM. The occlusion count does reach the TSV (C2); the inflation does not. As shipped, the second half of P248-250 is false for every raising region, and "both complete distributions" at closeout would be one complete and one missing every raise.

The fix is small and changes no treatment: move the three coordinate-only occlusion artifacts — excludelist (:1257-1261), manifest (:1266-1271), gate sidecar (:1277-1282) — out of the if ok: block and upload them whenever they exist. They are already declared egress-clean by their own comments ("coordinate/id-only … no genotypes, no per-person counts"), and their validity does not depend on the .npz verifying. The .npz stays gated on ok; that gate is correct. Whether the .afreq sidecar (:1251-1252) should also move I cannot say without knowing how af_arg is produced — if from plink --freq independent of the LD pass, it should; flag it as a question.

Note the deferral path already does this right: a gate-firing region uploads its sidecar at :1104-1108 before returning. Only the error: path loses it. That asymmetry is the bug.

It has to land before Stage C because the alternative — harvesting scratch by hand — collides with X2: raising regions' scratch persists (:1296), a few large ones fill the disk, and later regions then fail with error: for an unrelated reason that the TSV cannot distinguish from a T1 raise (see §3 below). Harvest-by-hand is a plan that fails exactly when there are enough raises to matter.

Q6 — Does a full-panel measurement before posting spend the prospective prediction?
Yes, if it runs before the disclosure is posted. No, if after. The falsifiable content of the prediction is not the rate — a rate "to be measured" is barely a prediction — it is both sides and boundary-adjacent only. A full-panel scan tests both of those. Run before posting, the prediction becomes a description of a known result written as a forecast, which is the record-integrity failure the disclosure's own sequencing rule ("posted BEFORE production testing") exists to prevent.

So D is legitimate in exactly one order: post the disclosure → D → Stage C. If Carter will not post before firing, D is off the table and the per-region alternative (LOW-1, §2 below) does the same classification job during production, where it is production testing the prediction rather than pre-empting it.

Cost note: the draft's ~10.5 h + ~35 h linear extrapolations are honest about being extrapolations. Against an ~11-day fire they are not trivial, but they are also not the argument — sequencing is.

Q7 — Is changing the criterion for a stated methodological reason the trsx5:49 fenced act?
Not the literal fenced act; the same act one level up; and it needs an amendment regardless, so the question does not decide anything.

trsx5:49 fences "choosing the occlusion criterion to obtain a particular fine-mapping result." Widening the predicate to ±1 so that boundary-adjacent regions stop raising is choosing the criterion to obtain a particular build result. Not the literal text; the identical shape. It is also calibrate-to-pass at n=1 observed + 1 predicted, which I have already argued against on this thread and the in-repo ledger records (osf_deviations.md:705-706, per the draft).

E-R2's use of mk7ze's gate/criterion separation (P302-305) is misapplied: mk7ze draws that line precisely to say the gate may be recalibrated while the criterion is "UNTOUCHED" (P300-302). It does not license criterion changes for methodological reasons; it fences them off from the thing it permits.

And decisively: the criterion is one of the five objects trsx5:53 fixes before code. Any change to it is an amendment before code, whether or not it is the fenced act. So E's "is it fenced?" question is moot — the answer to "what does E require?" is an amendment, full stop, and the case for that amendment at n~2 does not exist.

2. Things the draft states that are wrong, or frames wrongly
None of the citations are wrong. Four framings are:

"The disposition is what is at issue" (Option A). T1 is the disposition. What is at issue is the label and the accounting. (§0-i.)
A raise logged as a deviation (A-R1, Q1). It is the pre-registered behaviour. Labelling it a deviation in the deviations ledger misreports it to the one reader who consults that file for departures. (§0-ii.)
The whole "which branch" frame. The branches are Contract-1 outcomes; a T1 raise is a Contract-2 outcome. The draft has the disqualifying fact (B-R1: not an occlusion under clause (a)) and does not apply it to its own question. (§0.)
X1 listed as an "issue that applies," parallel to X2–X4. X1 is a code path that falsifies a posted commitment (mk7ze P248-250) for every raising region. It is a precondition, not an issue to weigh against options.
One more, smaller: §0 P5 says 00149 "is predicted." True. But the draft's Q3 planning number then scales 1-in-21 to ~13 regions using 00149 as the one case — i.e. it counts the predicted case as the observed rate. The observed Stage-B rate is 1 of the regions actually run (00057), which is a different denominator. Neither number is calibrated; the draft says so; but it should not use the scan's prediction as if it were the fire's observation.

3. What the draft omits
(a) The error status does not distinguish a T1 raise from any other exception. process_region records f"error: {e}" for every exception (:1287-1288), and the verifier classifies every error: prefix identically as FAILURE (:303, :324-326). A scratch-full failure, a gsutil failure, and a NaN raise are the same row to the verifier. Under A, after the first raise the check-in is permanently red and every subsequent failure of any kind is one more indistinguishable error: row. The message text distinguishes them (plink_ld_to_npz.py:222 is recognisable), but nothing parses it.

Fix: the producer catches the NaN raise specifically (ValueError from read_square_bin whose message begins "square LD carries NaN") and records a distinct prefix — I will call it raised_nan: — that the verifier classifies as its own class: not PASS (that is B's error), not lumped with error: (that is A's operational failure), but a FINDING that reports its own count and region list. The C6 enforcer forces the vocabulary entry. This is a small change in the fire path that alters no treatment, and it is what makes A operable for 11 days.

(b) The permanently-red gate. Under A as committed, one raise on day 2 makes every stage-c check-in exit 1 for the remaining ~9 days, and each exit 1 is an R8 STOP. A gate that is always red is a gate no one reads — the second failure arrives on a light that is already on. The draft notes per-status counts can be diffed; that puts the diff in the human's head. With (a) in place the verifier can report raised_nan as a counted FINDING and reserve exit 1 for new regions in any failure class since the last check-in — or, if a stateless verifier is preferred, exit 1 on any error: and report raised_nan: counts without exit 1 once each raise has been acknowledged by Carter. Either is a design choice; the record should make it before the fire, not at region 180.

(c) The hybrid the questions point at but no option names: A + LOW-1. The draft carries LOW-1 (per-region pairwise-completeness pre-check before plink) only as a way to save scratch and compute. Its real value is classification at fire time: the pre-check predicts whether this region will raise on the known class before plink runs. Then:

pre-check predicts a raise, plink raises → known-class, raised_nan:, loop continues, counted;
pre-check predicts no raise, plink raises → unclassified, stop and diagnose (Q3);
pre-check predicts a raise, plink does not → the pre-check is wrong; also a finding.
That turns the raise from a binary into a classified event, gives Q3 its condition, gives Q4 its enforcer something to check, and does D's work incrementally inside production — so it does not spend the prediction (Q6). Cost, from the draft's own measured runtimes: scan ~2.3 min/region (48 min / 21), reclassify ~7.7 min/region (2 h 40 m / 21) — against a plink pass the July digest put at ~148 min/region. Roughly 7% overhead. The draft flags that neither pass has been run over all 276 unchanged; that is a real pre-condition for this option, not a reason to drop it.

(d) The raising region's occlusion-axis classification should be reported. §0-iii. Every raising region has a computed count and gate verdict; the closeout branch distribution should include it by that count with a raised flag, not omit it. Otherwise T7's "realized branches" is systematically missing the raising regions on the axis where they do have a value.

(e) n_var of raising regions is a coverage quantity. Under A/C/F the region is unbanked. Its variant count and span are what the coverage disclosure needs (as R4-COVERAGE already reports "N regions … affected span M Mb"). Both are known before plink. Make sure the TSV row for a raising region carries them — I believe it does via pre_window_n_var, but I did not verify the column, so: check.

4. Where I land, stated as a position and not a ruling
The decision is Carter's; this is the reviewer-defensible shape as I see it.

Treatment: Option A's behaviour — raise, bank nothing, loop continues — because that is T1 executing, with Option C's stop reserved for unclassified raises (Q3). Not B (silences the contract). Not F as drafted (a deferred_* prefix asserts a pending outcome that does not exist — use a non-deferral prefix instead, §3a). Not E (amendment before code; no case at n~2). D only after posting (Q6).

Required on the record before the fire, in order of hardness:

X1 code fix — occlusion artifacts uploaded regardless of ok (Q5). Hard requirement: a posted commitment is currently false in code.

Distinct raised_nan: status + verifier class + C6 vocabulary entry (§3a). Hard requirement for A to be operable and for the closeout count to be mechanical rather than parsed from messages.

The disclosure paragraph stating the raising-region disposition and its "not a deviation" labelling (Q1), in the document that must be posted before production anyway.

The pre-fire resume rule: re-diagnosis classifies, never re-treats (Q3).

Enforcer registered for the raising-region coverage obligation, template C7, checking classification and count (Q4).

Decision on the permanently-red gate (§3b) — a design choice, but made in advance.

Optional but recommended: LOW-1 pre-check as the classifier (§3c), contingent on confirming the scan runs unchanged over 276 regions.

What I am not asking for: an OSF amendment for this. T1 pre-registered the treatment; the rest is accounting, and it rides on the disclosure.

5. Epistemic footing
Everything about the posted text and the code is read directly at the anchors stated.
§0-iii (branch = classification clause; consequence clause presupposes a panel) is a reading. It is the one that keeps T7 complete; it is not the only possible one. If it is rejected, Q1's answer becomes "the region falls under no branch on any axis, and that is correct because it is not an occlusion outcome" — the amendment answer does not change.
I have not seen the 00057 halt record's diagnostic passages except as the draft quotes them, and I have not seen osf_deviations.md. Where I cite either I am citing the draft's citation.
The 7% overhead figure for LOW-1 divides the draft's measured scan runtimes by the July digest's ~148 min/region; the latter is a planning figure I carried from an earlier session, not a Stage-B measurement. Treat the ratio as order-of-magnitude.
````
