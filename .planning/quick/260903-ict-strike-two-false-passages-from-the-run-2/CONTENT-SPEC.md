# CONTENT SPEC — quick-260903-ict

DOCS-ONLY. Two corrections to an existing record, then one new disclosure.
Every number here is measured and verified. Copy; do not recompute.

===============================================================================
## PART A — TWO STRIKES from the committed courier record
File: `.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`
(currently 491 lines, md5 e2c0b5443bf82a12940d492fefb1f282)

### STRIKE 1 — the `## ACTION ITEM — THE 0.0005 BOUND IS A LIVE CONTRADICTION` section
IT IS FALSE. There is NO contradiction. Replace the section with a short
CORRECTION section stating, in substance:

  The two `0.0005` values are DIFFERENT, UNRELATED constants.
  - `_OCCLUSION_ANOMALY_FRACTION = 0.0005` (commit `d9fbc63`) was the OCCLUSION gate.
    It was genuinely withdrawn, and it is REMOVED: 0 hits in `src/` and `tests/`.
    It was replaced by the POSTED two-condition gate (mk7ze):
    `OCCLUSION_SITE_FRACTION_CEILING = 0.005056` + `OCCLUSION_INFLATION_CEILING = 3.42`,
    both live in `src/python/occlusion_gate_constants.py`.
  - `condition_ld_matrix.py` `ceiling_frac = 0.0005` is the LD-MATRIX NaN-ZEROING
    ceiling (`n_zeroed_pairs <= ceiling_frac * n_var`). That file contains the
    string `occlu` ZERO times.
  Therefore `pairwise_completeness_scan.py:45` calling the occlusion bound
  "withdrawn" is CORRECT.
  ROOT CAUSE, stated plainly: the original action item grepped the literal
  `0.0005` and treated textual co-occurrence as semantic identity.

⚠ A SEPARATE, REAL defect remains and must be recorded as DEFERRED (do NOT fix here,
it touches `src/`): `condition_ld_matrix.py:3-4` and `:153` cite
`osf-amendment-afr-native-ld-nan-psd-2026-07-03.md` (OSF `tcujq`) as PRE-REGISTERING
the NaN→0 policy, but `.planning/osf_deviations.md:133` and `:166` record that the
2026-07-10 update (OSF `trsx5`) WITHDRAWS exactly that policy. Accurate label:
"parameter of a withdrawn policy, retained in a frozen module, not called in
production." One-line docstring fix, its own task.

### PART A2 (was "STRIKE 2") — ⚠ CORRECTED BY MEASUREMENT: THIS IS AN ADDITION, NOT A STRIKE
The collapse-to-parents argument is **NOT IN THE COURIER RECORD**. Measured across all
491 lines: `collaps` 0, `parent` 0, `2.62` 0, `leave-one-out` 0, `2.48` 0, `0.0063` 0.
It was made in CORRESPONDENCE and never written into the record. My instruction to
"strike" it rested on an unchecked premise — the same error this task's PART A1 corrects.
So PART A2 is a PURE ADDITION of the corrected statistical position. Where the record
discusses heterogeneity, ADD EXACTLY THE INDENTED BLOCK BELOW AND NOTHING ELSE.
⛔ Do NOT introduce the refuted argument in order to refute it: the collapse-test claim
and its statistic must NOT appear anywhere in the record. There is nothing to quote —
it was never written there.

  That test DOES NOT DISCRIMINATE. For a chi-square homogeneity statistic the
  contribution of a deviation scales with the denominator, so merging two same-rate
  sub-windows holds chi-square roughly constant while removing a degree of freedom —
  the ratio rises BY CONSTRUCTION. Simulated under the rival hypothesis being TRUE:
  collapse raises dispersion in 65% of runs (median +3.6%). Same direction under both
  hypotheses, so it distinguished nothing.

  THE VALID REFUTATION (Seth's, not ours): non-independence cannot CREATE dispersion,
  only amplify dispersion already present at parent level. Simulated: parent rates ALL
  EQUAL + duplication -> dispersion 0.98. An observed ~2x therefore REQUIRES real
  parent-level heterogeneity.

  STILL VALID AND RETAINED: leave-one-out over 21 fits — overdispersion 1.99-2.48,
  worst-case p = 0.0063 — independently rules out a single influential point.

  READER-FACING TRANSLATION: overdispersion ~2.0 corresponds to parent-rate
  CV ~= 0.20, i.e. roughly 20% relative variation in tail rate between parent regions.
  (Our simulation; CV 0.25 gives 2.54. Seth proposed 0.25-0.30 — corrected DOWNWARD.)

### PART A3 — DELETE the now-STALE wording note (courier lines ~290-294)
The record carries a note saying the appendix "still says 'the three **pre-registered**
values'" and is "reproduced **unedited** because the appendix is byte-equal by
construction and must not be touched." THAT IS NO LONGER TRUE: commit `ee3af4b` fixed
the phrase AT SOURCE and re-spliced. Measured now: `pre-registered value` = **0
occurrences** in the record and **0** in the appendix; the appendix reads "the three
COMPLETION-CHECK values (see that section — they are NOT a pre-registration)".
DELETE that note. It describes a state that no longer exists, and leaving it invites a
future reader (it already misled this task's planner) to treat "leave it and add a note"
as the governing precedent when the actual precedent is FIX AT SOURCE AND RE-SPLICE.

### ⛔ HOW PART A1 MUST BE APPLIED — fix at SOURCE, do NOT add a supersession note
`LIVE CONTRADICTION` appears TWICE: courier line 296 (BODY heading) and line 450
(INSIDE the byte-frozen VERBATIM APPENDIX, 338-491).
DO **NOT** leave the appendix copy standing behind a note. Do what `ee3af4b` did:
  1. Fix the text AT SOURCE in
     `.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md`
     (its `## ACTION ITEM` section) so it states the CORRECTION, not the false claim.
  2. RE-SPLICE the courier's appendix from that corrected spec (`## ARTIFACTS` → EOF),
     between the BEGIN/END markers.
  3. RE-VERIFY byte-equality and record the NEW anchors for both files.
Byte-equality is a MEANS — proof that no number was retyped — NOT an end. It survives
re-anchoring. Preserving a FALSE CLAIM to protect an md5 is a guard scoped to a proxy
and is exactly what `ee3af4b` rejected.
RESULT REQUIRED: `LIVE CONTRADICTION` = 0 occurrences in the WHOLE record, appendix
included. Do not weaken this guard; make the correction's own prose avoid the phrase.

===============================================================================
## PART B — THE DISCLOSURE (new)
Append a new dated entry to `.planning/osf_deviations.md`, matching the existing
entry pattern (see the 2026-08-22 entry at :422). ⛔ THIS IS A DISCLOSURE, NOT AN
AMENDMENT. NOTHING IS POSTED BY ANY AGENT. Mark it explicitly as
"DRAFTED — NOT POSTED; placement and posting are Carter's."

Heading: `## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure (measured characterisation; NO amendment, NO predicate change, NO carrier floor)`

The entry must contain:

### (1) DISPOSITION, and that it was adjudicated
DISCLOSE + ANNOTATE. No amendment. Re-amending days after posting, for a measured
characterisation that changes NO behaviour, would be poor pre-registration hygiene.
Two disclosure targets: (i) methods disclosure (this log + manuscript); (ii)
data-product annotation on the panel's own provenance manifest — which pairs carry a
degraded informative-carrier count. (ii) is additive provenance under clause (c): it
changes no exclusion, no criterion, no branch. A carrier floor later WOULD be an
amendment, because it changes the panel's contents.

### (2) WHAT WAS MEASURED
21 regions, all in scope, 3,094 defined tail rows at max(carriers_lost_frac) >= 0.9:
  ROWS   2560 PRE-filter / 534 POST-filter of 3094   POST = 17.26%
  PAIRS  2047 PRE-filter / 474 POST-filter of 2521   POST = 18.80%
  Regions with tail rows 21; regions with ZERO POST-filter rows 0.
Heterogeneity: pair-level overdispersion 1.99x (chi2 37.78, dof 19, p 6.3e-3) after
dropping the chr15 double-count. UNEXPLAINED: rho -0.199 (window rows), -0.201
(occluded ids), +0.004 (occlusion density), in a design returning rho +0.886 for
tail rows vs window rows. ~20% relative variation between parent regions.
Definitional axis: rarer != min on 24.27% of tail rows vs 0.52% below tail = 46.5x
enrichment; independent of PRE/POST at rho +0.173.

### (3) ⭐ THE SURVIVOR GEOMETRY — a HEADLINE, and a POSITIVE result for the rule
`m2_region_00149`, deletion `chr7:89454077:GCGTA:G` (REF len 5, span
89454077..89454081) x partner `chr7:89454076:C:T`, offset -1, side upstream,
already_occluded False, pair_key `9776035|9776036`.
The posted predicate is `d.pos < v.pos`: `89454077 < 89454076` = FALSE. The single
survivor is INVISIBLE TO THE PREDICATE BY CONSTRUCTION, and it is the ONLY direction
that survives — NO positive offset appears anywhere across 21 regions. Offset
histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`.
State this as a POSITIVE result: the strictly-downstream predicate is COMPLETE IN ITS
OWN DIRECTION across 21 regions, and 100% of the residual sits on the side the strict
inequality cannot see.
⛔ NO PREDICATE CHANGE. Extending to offset -1 would cost only ~0.12% of the panel,
and that cheapness is an argument AGAINST, not for: it is calibrate-to-pass at n=1.
REGISTERED PREDICTION INSTEAD (record it as pre-registered here):
  "Residual undefined-r is expected EXCLUSIVELY at negative offsets. A positive-offset
   survivor would falsify predicate completeness in the downstream direction."
Production tests it. Change the predicate only if the RATE warrants it against data.

### (4) ⭐ SCOPE OF mk7ze LINE 275 — stated explicitly, as a RECORDED COMMITMENT
mk7ze line 275 reads: "An observable NaN requires complete-case zero variance at that
pair; geometric occlusion requires only coordinate span coverage, so every
NaN-implicated occlusion is a geometric occlusion but not conversely."
RECORD ITS SCOPE HERE: it is a statement about OCCLUSIONS and their relation to
NaN-implication. It makes NO claim about NaNs arising WITHOUT an occlusion. Its
argumentative work is carried by "but not conversely" (not every geometric occlusion
is NaN-implicated), which is substantive, true, and untouched by the survivor.
"Occlusion" is GEOMETRIC throughout mk7ze — clause (a) at line 467: "A variant record
is flagged as an occluder when its reference-allele interval [POS, POS + len(REF) - 1]
covers the position of a neighbouring variant."
The survivor is a NaN with NO covering deletion, hence OUTSIDE the sentence's domain,
not a counterexample within it.
⚠ WHY THIS IS WRITTEN DOWN RATHER THAN LEFT AS AN INTERPRETATION: mk7ze §(a) corrected
a scope promotion and closed with "The scope of the surviving claim is therefore
stated here explicitly, so it cannot be promoted again." §(a)'s remedy was EXPLICIT
SCOPING IN THE RECORD, not narrow reading in correspondence. Recording the scope here
converts the narrow reading from a defence available on challenge into a COMMITMENT.

### (5) ⭐ RECORDING THE SILENCE (not merely the survivor)
mk7ze makes NO claim whatsoever about undefined or degraded r arising outside the
occlusion predicate — verified by sweep of the 598-line posted body: ZERO hits for
"defined row", "finite r", "degraded", "precision", "SE(". That is a SILENCE, not a
false statement. Nothing in the posted record is falsified.
But the silence covers a real, measured class, and a reader of §(c) meets in sequence
a correct detector, a too-small expectation, a passed index-origin validation, and
NaN-implicated ⊆ geometric — from which the natural inference is that geometry
brackets the undefined-r cases. THAT INFERENCE IS NOT LICENSED BY THE TEXT.
So state, in substance:
  "mk7ze characterises the relationship between NaN-implicated occlusions and
   geometric occlusions; it makes no claim about undefined or degraded r arising
   outside the occlusion predicate. Such cases exist and are quantified here: one
   undefined pair with no covering deletion (upstream, offset -1), and 474 pairs
   across 21 regions with a defined but degraded informative-carrier count. Neither
   class is claimed against in the posted record; both are reported here so the
   posted record's silence is not read as coverage."

### (6) NO CARRIER FLOOR — and the definition PINNED before one exists
NO carrier floor is proposed and none is requested. The informative-carrier
DISTRIBUTION is reported so that a floor, if ever warranted, is chosen against data
rather than against a hoped-for pass rate.
📌 PINNED NOW: ANY carrier floor MUST be defined on
min-on-the-pairwise-complete-INTERSECTION, NEVER on rarer-by-overall-MAF. The two
disagree on ~24% of exactly the rows a floor exists to catch, so a floor written
against the wrong quantity would be SILENTLY BLIND on a quarter of its target class.
Mechanism: occlusion strips ~99.4-99.9% of the deletion's carriers on the
intersection, so the variant that is rarer by overall MAF stops being the one with
fewer carriers on the intersection — asymmetric carrier loss INVERTS THE RANK. This
is why the definitional disagreement is a signature of the first finding, not a third
phenomenon.

### (7) THE NEGATIVE RESULT, registered
Three structural correlates measured, NONE found (rho -0.199 / -0.201 / +0.004), in a
design that returns rho +0.886 when structure is present. Register this as a negative
result. It is STRONGER than an unexamined null because both artifact explanations were
eliminated: non-independence cannot create dispersion (0.98 under equal parent rates),
and leave-one-out rules out a single influential point (1.99-2.48, worst p 0.0063).
⛔ Do NOT pre-register a dispersion FIGURE.

### (8) EPISTEMIC STATUS — do not soften
MEASURED, NOT PRE-REGISTERED. The governing document
`.planning/debug/260901-PENDING-PASTE-POSTHOC-...md:211-216` deliberately declined to
state an expected value: "an expectation written down now would be a number picked
from what we hope passes." That refusal is why these findings cannot have been shaped
by an expectation. The genuine pre-registration is
`260826-...prereg-prediction.md` §(e), answered by RUN 1, confirmed 5/5 + histogram
with ZERO adjustments on 2026-09-01. The three values 3094/0/0 are a COMPLETION CHECK,
NOT a pre-registration.
The run finished during a VM reboot: stdout and $? are UNRECOVERABLE and were never
seen. Completion rests on the runtime reconciliation against the scanner's own
independent measurement across all 21 regions (writes nothing on disagreement) plus
the artifacts. No pre-reboot hash exists, so the md5s anchor FORWARD, not backward.

### (9) PROVENANCE
pcs_tail_verdicts.tsv md5 960f283734aea3b2c56c9249cf4fe94b, 1031086 B
pcs_tail_summary.json md5 bd74c0d502d15ac4e2fb5e1bdafc72b1, 38548 B
both written 2026-09-02T21:07:03Z; launched 18:26:17Z; 2h40m46s wall.
bim_sha256 9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99 (20,767,864 lines)
pairs_tsv_sha256 eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583 (353,090 lines)
regions_tsv_sha256 e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a
  — VERIFIED equal to `sha256sum config/ld_regions.tsv` at HEAD.
region_ids_selected = 276 is the ancestry-resolved MANIFEST size, NOT the 21 regions
carrying rows. Say so explicitly.
