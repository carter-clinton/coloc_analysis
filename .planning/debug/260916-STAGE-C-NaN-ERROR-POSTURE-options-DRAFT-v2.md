# Stage C: what happens to a region that RAISES on a leftover pairwise NaN (options draft v2)

**Status:** DRAFT v2, banked in the repo (quick-260916-vqq), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by
an adjudicator who has not seen our reasoning: options are laid out neutrally, with no recommendation.
Every claim cites file:line. Labels: **TEXT** = what a posted record says; **CODE** = what shipped code
does; **READING** = an interpretation offered for adjudication, not a finding.

**SUPERSEDES** `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` for couriering: that draft's code citations were written at `c93e97b`, the code basis has since moved, so every citation here was re-derived at the commit stated below, and the options section was restructured for symmetry.

**Method note.** This draft is screened mechanically by
`.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`: a phrase
screen for advocacy language, and a balance family that measures the option structure — identical
labelled sub-fields, READING symmetry within and across options, a word band, an evaluative-cue screen
over the whole document, precedent placement, and question coverage. Two things are deliberately
**not** balanced, because both are factually determined and evening them out would be falsification:
which options appear in §4, and how much cited ground each option has. The checker prints per-option
citation counts as information only.

**Anchors checked this session (2026-09-16), before any citation was written:**
- **mk7ze (posted)**: repo lines 168–500 of
  `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` =
  22,945 B / md5 `13a49f543cabcc27ce9f1e589783c060` (control: lines 167–500 hash to `8154025b…`, so
  the anchor can fail). Citations below read **mk7ze P*n*** (line *n* of the posted body) with the
  repo line as **R*n***. Each was located by searching for its verbatim quote, not by subtracting 167
  by hand.
- **trsx5 (posted)**:
  `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt`
  = 9,695 B / md5 `c19be8b2ad7cd6a45fee1d668d8a9cf9`, the byte-exact posted body. Cited as **trsx5:*n***.
  The repo draft `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` is **not** the posted body
  and is not cited.
- **Code basis for every citation below:** commit
  `74f962d21b07a8b765dfba6c3825448e05eb17e7` (short `74f962d`) on branch `m3-W2-aou-deltas`. To read
  any cited file exactly as it is cited here, run `git show 74f962d:<path>`; every `file:line` below
  is a 1-based line number in that output. The mechanical re-verification of this draft is
  `.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`, run
  with no arguments from the repository root.

**Files cited** (short form used below → full repo-relative path):
- `260812-ox1-AGENT-PROMPT.md`, `AGENT-PROMPT.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`
- `260812-ox1-READY-TO-FIRE.md`, `READY-TO-FIRE.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
- `260824-STAGE-B-HALT-…md` → `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`
- `run_native_ld_panel.py` → `src/python/run_native_ld_panel.py`
- `fire_verifier.py` → `src/python/fire_verifier.py`
- `plink_ld_to_npz.py` → `src/python/plink_ld_to_npz.py`
- `osf_deviations.md` → `.planning/osf_deviations.md`
- `deferred-items.md` → `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`
- `STATE.md` → `.planning/STATE.md`
- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`
- `260831-…-anchor-relative.md` → `.planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md`
- `260901-kw8-PANELWIDE-RECLASSIFICATION.md` → `.planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md`
- `260902-vsp-CONTENT-SPEC.md` → `.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md`

⚠ **Scope of the `osf_deviations.md` citations.** Every one of them sits inside a single ledger entry
headed "AFR native-panel DEFINED-ROW TAIL disclosure", which is marked **DRAFTED — NOT POSTED**. The
entry begins at `osf_deviations.md:567` and runs to the end of the file. Nothing cited from it is
posted text; it is our own working ledger.

⚠ **Scope of the `260824-STAGE-B-HALT-…md` citations.** That record now carries a
`## ⚠ SUPERSEDED 2026-09-16` section recording that its RAM-measurement passages — the `ru_maxrss`
inheritance reading and the `subprocess.Popen` + `os.wait4` "clean fix" it prescribed — are
FALSIFIED. **No citation in this draft depends on those passages**, and the re-verifier gates that
disjointness mechanically rather than by inspection.

---

## 0. Measured premises: what the committed card and the shipped code fix today

**P1: The committed Stage C command does not use `--fail-fast`.** STEP 10 runs
`run_native_ld_panel.py … --mode square --ancestry AFR` with no `--fail-fast`
(`260812-ox1-AGENT-PROMPT.md:398`), and the card says so twice (`:372-373`, `:417`; also
`260812-ox1-READY-TO-FIRE.md:360-366`). The flag's own help text says "Stage C runs without
--fail-fast" (`run_native_ld_panel.py:1468-1471`).

**P2: Without the flag, a raising region does not stop the loop (CODE).** The NaN raise is
`plink_ld_to_npz.read_square_bin` (`plink_ld_to_npz.py:218-228`), called at
`run_native_ld_panel.py:1233-1236`. `process_region` catches it (`:1287-1289`) and records
`status = "error: square LD carries NaN …"`. The panel row is appended (`:1291`), no `.npz` is uploaded
(uploads happen only under `if ok:`, `:1244-1250`), and the region returns. The loop raises only
`if fail_fast and status != "ok"` (`:1421-1422`).

**P3: What does stop is the human monitoring gate, at the next check-in.** `fire_verifier stage-c`
(`fire_verifier.py:1097-1099`) classifies `error:` as FAILURE (`:302-303`, `:324-326`) and returns
FINDING with the message "Stage C runs without --fail-fast so the loop continues by design; report these
to Carter … Do NOT re-fire blindly" (`:381-389`). Any failed check gives exit 1 (`:976-981`). Under
rule R8 an exit 1 is a STOP-and-report for the agent (`AGENT-PROMPT.md:55-61`, `:422-423`;
`fire_verifier.py:999-1001`). The `nohup` process keeps running.

**P4: Adding `--fail-fast` to Stage C would halt on regions already banked.** The flag raises on any
`status != "ok"` (`run_native_ld_panel.py:1421`). An already-banked region returns
`skipped_idempotent` (`:949-958`), and `00001`, `00017` and `00040__sub14` are banked
(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`run_native_ld_panel.py:1468-1471`).

**P5: One raise is observed; the second is predicted.** `m2_region_00057` (+1) raised in Stage B
(`260824-STAGE-B-HALT-…md:11-16`). `m2_region_00149` (−1) is classified as surviving into the panel by
the pairwise-completeness scan (`.planning/osf_deviations.md:692-698`, a DRAFTED — NOT POSTED ledger
entry) but has **not** been run through `run_native_ld_panel`.

**Two questions are open here, and this draft treats both as open.** The first: **does the
operator stop the fire when a region raises, or let the loop continue?** Option C addresses that one.
The second: **what pre-registered disposition does a region get when the raw-panel NaN-raise contract
fires, the region banks nothing, and the loop moves on?** Options A, B and F address that one. For
either: does settling it need a posted amendment-update before Stage C?

---

## 1. What the posted text commits to

| # | TEXT | Where |
|---|---|---|
| T1 | The raw-panel NaN-raise contract: "The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract." | trsx5:39; restated as unchanged at mk7ze P321-322 / R488-489 |
| T2 | Defer-not-exclude is stated for the **anomaly gate**: "If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation." | trsx5:29; mk7ze P261 / R428 ("Deferral remains NOT auto-exclusion. A region over the ceiling …"); mk7ze P311-312 / R478-479 ("A region over the anomaly gate is deferred for re-diagnosis …") |
| T3 | `BRANCH_AFR_OCC_DEFERRED` is defined by its trigger: "the region's occlusion-exclusion count exceeds the anomaly gate". mk7ze lists what routes there: "NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`". | trsx5:47; mk7ze P316-318 / R483-485; the two conditions at mk7ze P155-158 / R322-325 |
| T4 | NONE = "the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified." EXCLUDED = "… fine-mapping proceeds on the reduced variant set". | trsx5:43, trsx5:45 |
| T5 | The branch list is presented as closed: "All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list." | trsx5:49 |
| T6 | Discipline: deviations are logged in `.planning/osf_deviations.md` and disclosed in the manuscript. | trsx5:53; mk7ze P323-324 / R490-491 |
| T7 | Closeout: realized branches, the per-region exclusion manifest and the present-rate go to a follow-up OSF update; "Every region computes its own occlusion count AND its own occluded-site inflation during the production run, so both complete distributions fold in at closeout". | trsx5:59; mk7ze P247-250 / R414-417 |
| T8 | Prohibited or fenced: NaN→0 (trsx5:25; mk7ze P307-308 / R474-475); "choosing the occlusion criterion to obtain a particular fine-mapping result" (trsx5:49; mk7ze P302-305 / R469-472). | as cited |
| T9 | The one posted rule that disposes of NaN-bearing variants, and it is RETAINED: "The fully-NaN-row → drop rule (prior item (a) first branch): a variant row that is entirely NaN (a zero-variance / monomorphic-within-analysis-set source) is dropped by MAF / missingness QC. This converges with the new exclude policy and is retained." Restated as unchanged at "**The fully-NaN-row → drop rule** and **the raw-panel NaN-raise contract**". | trsx5:37; mk7ze P321 / R488 |

**What the posted text does not say (a sweep, not an impression).** Both posted bodies were
normalized (markdown stripped, whitespace collapsed, lower-cased) and searched. `halt`, `abort`, `skip`,
`partial`, `incomplete`, `feasib`: **0 hits in either**. Control: `defer` has 17 hits in mk7ze and 4 in
trsx5; `raise` has 3 and 2, so the search can find terms. **Neither body says what happens to a
region after the raw contract raises.** The existing `deferred_infeasible_square` route is also absent
from both.

---

## 2. What the shipped code and committed runbook do today

| # | CODE / RUNBOOK | Where |
|---|---|---|
| C1 | NaN check runs first in the converter. The message blames a zero-variance variant; for 00057 that diagnosis was measured false (a confined pair, diagonal 1.0). | `plink_ld_to_npz.py:213-228`; `260824-STAGE-B-HALT-…md:45-58` |
| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `run_native_ld_panel.py:1211-1212`, before conversion at `:1233`). No `.npz` upload. | `run_native_ld_panel.py:1287-1291`, `:1244-1250` |
| C3 | Local scratch is reclaimed **only** when `status == "ok"`. The docstring puts intermediates at "~30+ GiB/region … overflows any finite scratch disk". | `:1292-1297`, `:866-868` |
| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:949-958`, an infeasible one at `:1009-1015`). It is uploaded **only** on deferral or on `ok`. | written `:1066-1082`; uploaded `:1104-1108` (deferral), `:1272-1282` (inside `if ok:`) |
| C5 | Resume skips a region only if its `.npz` exists, so an `error:` region is recomputed on every re-fire. | `:942-958` |
| C6 | Verifier: deferrals PASS ("the gates working"), `error:` = FINDING, an unknown status = HARD_STOP. The vocabulary is held by `test_shipped_status_vocabulary_is_covered_by_the_allow_list`. | `fire_verifier.py:330-399`, `:309-312` |
| C7 | Precedent for a region that banks nothing outside the three posted branches: `deferred_infeasible_square` (`run_native_ld_panel.py:1009-1015`). Registered in-repo as "a DISCLOSURE OBLIGATION — not blocking the fire", with measured numbers owed at publication, a remedy path recorded, and a named enforcer. | `deferred-items.md:1148-1191`; enforcer `fire_verifier.py:875-939` |
| C8 | The runbook calls a partial bank "a real, reportable outcome". | `READY-TO-FIRE.md:360-366`; `AGENT-PROMPT.md:424-428` |

---

## 3. Options

### Option A: run the card as committed (no code change)

- **Behaviour:** no `--fail-fast`. A raising region records `error:`, banks nothing, and the loop
  continues (P2). At the next check-in the gate exits 1 and the agent reports to Carter (P3). At
  closeout the region is reported as unbanked and logged as a deviation.
- **Code needed:** none. This is the committed card run unchanged, and no file in the fire path moves.
- **Already pre-registered?** The *raise* is (T1); the *non-halting loop* is runbook, not OSF; the
  *disposition* is what is at issue.
  - No posted branch fits on its face: NONE needs "the panel and fine-mapping result stand unmodified"
    (trsx5:43) and nothing was banked; EXCLUDED needs "fine-mapping proceeds on the reduced variant set"
    (trsx5:45); DEFERRED's trigger is the anomaly gate (T3), and 00057's gate did **not** fire — a
    region whose gate fires returns at `run_native_ld_panel.py:1110` before plink runs, so it cannot
    reach the raise at `:1233`.
  - *READING 1:* logging it under T6 changes no criterion, no gate and no variant's treatment. A
    deviation entry plus manuscript disclosure is what the posted discipline already requires of any
    deviation, so on this reading nothing is owed before Stage C — and no code is involved either way.
  - *READING 2:* T5 presents the three branches as the complete list, and trsx5:53 fixes "the three
    outcome branches … before any occlusion-handling code fires". A region in none of the three is a
    fourth realized outcome, and on this reading a posted amendment-update is owed **before** Stage C
    rather than at closeout.
- **Consequences:** each raising region is a coverage gap shaped like the R4-COVERAGE precedent (C7),
  but with no registered disclosure obligation and no enforcer yet. After the first raise, every later
  `stage-c` check-in exits 1 for the rest of the ~11 days (`AGENT-PROMPT.md:393`), and each exit 1 is
  an R8 STOP, so a *new* failure arrives on a gate that is already red. The verifier does print
  per-status counts (`fire_verifier.py:363-370`), so a new failure is visible by diffing check-ins.
  C3, C4 and C5 apply (see §4).

### Option B: send raising regions to `BRANCH_AFR_OCC_DEFERRED` (defer, don't exclude)

- **Behaviour:** the producer catches this particular raise, records a deferral status, and the
  verifier PASSes it instead of reporting a FINDING.
- **Code needed:** yes. The producer's error path, plus either a new status prefix (which turns the C6
  enforcer red until the vocabulary is extended) or reuse of `deferred_occlusion_anomaly:`.
- **Already pre-registered?**
  - *READING 1:* no. DEFERRED is tied to the anomaly-gate trigger (T3), and defer-not-exclude is
    stated for "a region over the anomaly gate" (T2). Adding a NaN-raise trigger changes what DEFERRED
    denotes, which would need an amendment-update **before** code.
  - Reusing `deferred_occlusion_anomaly:` would record an anomaly the gate did not find.
  - The surviving class has "no covering record for EITHER member" (`osf_deviations.md:738-739`, a
    DRAFTED — NOT POSTED entry), so it is not an occlusion under clause (a) (mk7ze P300-302 / R467-469).
  - *READING 2:* the same posted text can be read the other way. mk7ze commits to "NO fourth branch
    and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity
    companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`" (mk7ze P316-318 / R483-485). A reader
    could take that as a commitment against token proliferation — directing any disposition that is
    neither NONE nor EXCLUDED to the SAME token rather than to a new one. Scope limit: that sentence
    is written about the companion condition, so how far it reaches is itself part of the question.
- **Consequences:** check-ins stay green. A contract raise would then be classified under the deferral
  PASS, whose stated reason is "the gates working" (`fire_verifier.py:335-336`). "Deferred for
  re-diagnosis" presumes a diagnosis still to do: the mechanism is measured for one member,
  `m2_region_00057` (`260824-STAGE-B-HALT-…md:150-179`), and predicted rather than observed for the
  second, `m2_region_00149` (P5). Whether "re-diagnosis" is discharged for this class at n=1 is open.

### Option C: stop the fire at the first raise and re-diagnose before continuing

- **Behaviour:** literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so
  this option means the operator stopping the fire at the first `error:` row and resuming by hand.
- **Code needed:** none. This is a runbook change: the committed command is unchanged and the operator
  acts on the check-in the gate already produces.
- **Already pre-registered?**
  - *READING 1:* no posted text requires halting and none forbids it, so on this reading the choice is
    operational, sits outside the amendment surface, and carries nothing to post in either direction.
  - *READING 2:* stopping changes which regions are measured and in what order, and T7 commits the
    realized branches and the genome-wide present-rate to a closeout update. On this reading an
    operator-truncated run is a closeout-disclosure question even though the halt itself is not a
    posted act.
- **Consequences:** the Stage B halt record states: "`--fail-fast` is correct for Stage A/B and **must
  not be carried into Stage C** at an unknown per-region failure rate"
  (`260824-STAGE-B-HALT-…md:104-107`). *For planning only, not a calibrated
  rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:695-698`).
  Three caveats travel with that number: the sample was systematic-by-span rather than random
  (mk7ze P88-89 / R255-256); the one case is predicted, not observed (P5); and the ledger's own caveat
  is that this sweep could observe only one side, while "Production tests the rate on BOTH sides"
  (`:717`). Scaled to 276 that is ≈13 regions, with an exact 95% binomial range of 0.3–66. A region
  skipped by an operator stop is still unbanked, so the R4-COVERAGE-shaped obligation (C7) reaches it
  as it does under A.

### Option D: measure the expected raise list before deciding (combines with A, B or F)

- **Behaviour:** Carter runs the pairwise-completeness scan across the AFR regions before Stage C, so
  any posture is chosen against a measured list rather than against one observed case. The scan alone
  is **anchor-relative**: "`already_occluded == False` means "not inside THIS anchor's span"… does not
  count pairs that survive filtering" (`260831-…-anchor-relative.md:50-53`), so the list of regions
  expected to RAISE needs the separate `pcs_panelwide_reclassify` pass on top of it. Both passes are
  read-only.
- **Code needed:** none expected for the scan; whether it runs unchanged over all 276 regions has
  **not** been checked, and the reclassify pass has so far been run only on subsets of them.
- **Already pre-registered?**
  - *READING 1:* a read-only measurement changes no analysis choice, no criterion and no variant's
    treatment, so on this reading it sits outside the amendment surface entirely and nothing is owed
    before it runs.
  - *READING 2:* there is a sequencing constraint. The disclosure's prospective production prediction
    is "to
    be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"
    (`osf_deviations.md:720-724`), and "Production tests the rate on BOTH sides" (`:717`).
    A full-panel measurement tests that same both-sides rate before production does, and on this
    reading that is the prediction being spent rather than a neutral measurement.
- **Consequences:** the regions expected to raise are measured before Stage C instead of observed
  during it, at the cost of VM time (Carter). Measured runtimes, named by instrument, run and region
  count: the 21-region pairwise-completeness scan took 48 min (`STATE.md:18`), which scales linearly
  to ~10.5 h over 276 regions; the `pcs_panelwide_reclassify` pass covered 6 regions in 1 h 53 m on
  2026-09-01 (`260901-kw8-PANELWIDE-RECLASSIFICATION.md:13`, region count at `STATE.md:485`) and the
  21 regions that carry rows in 2 h 40 m 46 s on 2026-09-02 (`260902-vsp-CONTENT-SPEC.md:10`), which
  scales linearly to ~35.2 h over 276 regions. Both scalings are linear extrapolations of a measured
  run, not measurements.

### Option E: change what reaches the matrix

- **Behaviour:** widen the occlusion predicate to cover −1/+1 offsets, add a pairwise-completeness
  exclusion rule, or coerce NaN→0. NaN→0 is prohibited outright (T8), so the live members of this
  family are the predicate widening and the new exclusion rule.
- **Code needed:** yes, in the panel-build path — and, for the predicate widening, a rebuild of every
  region already banked under the current predicate.
- **Already pre-registered?**
  - *READING 1:* no. "NO PREDICATE CHANGE … calibrate-to-pass at n=1" is already recorded
    (`osf_deviations.md:705-706`, a DRAFTED — NOT POSTED entry), and a new exclusion rule is a new
    criterion, so an amendment-update would be owed **before** code on either live member. That record
    is our own working ledger rather than posted text, so it binds our practice, not the
    pre-registration.
  - *READING 2:* what the posted text fences is narrower than "any change". trsx5:49 fences
    "choosing the occlusion criterion to obtain a particular fine-mapping result", and mk7ze separates
    recalibration from that act: "the anomaly GATE is a different object from the CRITERION, and
    recalibrating the gate against a measured population is not that prohibited act"
    (mk7ze P302-305 / R469-472). On this reading a change made for a stated methodological reason is
    not the fenced act.
- **Consequences:** this is the only family that changes which variants reach the matrix, so it moves
  the panel itself rather than the disposition of a region that banks nothing. Regions banked under
  the current predicate would then be inconsistent with regions built after it unless they are
  rebuilt, which is compute that has not been scoped here.

### Option F: record an operational `deferred_*` status not mapped to a posted branch

- **Behaviour:** the producer records a distinct operational status — say `deferred_pairwise_nan:` —
  which the verifier treats as a deferral PASS, while the draft asserts nothing about whether the
  region falls under `BRANCH_AFR_OCC_DEFERRED` or under any posted branch. The disposition question is
  answered at closeout, in the open, rather than at fire time.
- **Code needed:** yes. A new prefix in the producer's error path and one entry in the verifier's
  deferral allow-list (`fire_verifier.py:300-303`), which the C6 enforcer holds honest.
- **Already pre-registered?**
  - *READING 1:* the shipped code already carries this exact shape. `deferred_infeasible_square`
    (`run_native_ld_panel.py:1009-1015`) is an operational `deferred_*` status that is in the verifier
    vocabulary and in none of the three posted branches, registered in-repo as "a DISCLOSURE
    OBLIGATION — not blocking the fire" (`deferred-items.md:1148-1191`) with a named enforcer
    (`fire_verifier.py:875-939`). On this reading the precedent is the surface that governs.
  - *READING 2:* that precedent is in-repo, not posted. trsx5:49 presents the branch list as closed
    and trsx5:53 fixes the three outcome branches before any occlusion-handling code fires, so a new
    operational token is still a fourth realized outcome in the record. On this reading an
    amendment-update is owed **before** code, exactly as under B.
- **Consequences:** check-ins stay green without asserting anything about the posted branch list. The
  region still banks nothing, so the R4-COVERAGE-shaped obligation (C7) reaches it as under A and C —
  and unlike A, this option would register that obligation and its enforcer when the status is added.

### LOW: three further options with less cited ground at this basis

Brevity here reflects how much cited ground exists at this basis, not a ranking.

- **LOW-1 — a per-region pairwise-completeness pre-check at fire time.** Run the completeness check
  for a region before its plink pass, so a region expected to raise is dispositioned before the
  compute and the scratch are spent: the docstring puts intermediates at "~30+ GiB/region … overflows
  any finite scratch disk" (`run_native_ld_panel.py:866-868`) against a `--max-n-var` ceiling of
  120,000 (`READY-TO-FIRE.md:369-370`). **Cited.**
- **LOW-2 — re-run on a different sample set, or with sample-level QC.** A different analysis set
  changes which rows are monomorphic-within-set, and so which pairs are structurally undefined.
  **UNCITED:** no posted or in-repo record at this basis states what that would do to this class.
- **LOW-3 — the downstream effect on AFR fine-mapping and coloc denominators.** A region that banks
  nothing is absent from the panel and therefore from every downstream denominator. **UNCITED:** the
  posted text defines the panel-stands and reduced-set cases but says nothing about an unbanked
  region, which is the §1 sweep finding restated.

---

## 4. Issues that apply when a raising region banks nothing (A, C and F; and B, where adding uploads to B's code would close X1 but not X2–X4)

- **X1: evidence egress versus the mk7ze closeout commitment.** mk7ze P247-250 commits that "both
  complete distributions fold in at closeout". A raising region's gate sidecar (site counts,
  inflation) is written locally but never uploaded (C4) — and the same `if ok:` block
  (`run_native_ld_panel.py:1245`) gates four further per-region artifacts: the allele-frequency
  sidecar (`:1251-1252`), the **excludelist** (`:1257-1261`), the **occlusion manifest**
  (`:1266-1271`) and the gate sidecar (`:1277-1282`). A raising region therefore loses four egress
  artifacts besides the `.npz` itself, not one. Its `n_dropped_occluded` row count does reach the
  panel TSV (C2); its allele frequencies, site count, inflation, excludelist and manifest do not. As shipped, the closeout
  distributions would be missing every raising region unless scratch is harvested by hand. Closing
  that gap in code touches the fire path and needs a decision.
- **X2: scratch fills up.** A raising region's `.ld.bin` (n_var² × 4 B; ≈57.6 GB at the
  120,000-variant ceiling; `READY-TO-FIRE.md:369-370`) stays in scratch (C3). The VM's scratch capacity was **not** checked here. A
  few large raising regions could make later regions fail with `error:` for an unrelated reason.
- **X3: resume re-spends compute.** Every re-fire recomputes and re-raises each raising region (C5),
  assuming identical inputs.
- **X4: the disclosure obligation has no enforcer.** R4-COVERAGE has one (C7). This class does not.

## 5. Questions for the adjudicator

The A–F labels are inherited and alphabetical: they carry no ranking, and the order in §3 is not an
ordering by merit. The question order below follows the option order and likewise carries no ranking.

1. Does a region that banks nothing *because the raw-panel NaN-raise contract fired* fall under any of
   the three posted branches (T4, T3)? If not, does T5 require a posted amendment-update before Stage
   C, or is a deviation entry plus disclosure (T6) enough? (Options A, B, F)
2. Would routing such a region to `BRANCH_AFR_OCC_DEFERRED` change what DEFERRED means (T3), and does
   "NO new token" (mk7ze P316) reach beyond the companion condition? (Options B, F)
3. Is an operator stop at the first raise a matter the posted text speaks to at all, and does an
   operator-truncated run raise a closeout-disclosure question under T7? (Options C, D)
4. Does the R4-COVERAGE precedent (C7: a disclosure obligation with a named enforcer, not blocking the
   fire) govern this class? (Options A, C, F)
5. Does honouring mk7ze P247-250 require that a raising region's gate evidence — sidecar, excludelist
   and occlusion manifest — reach the bucket (X1)? If so, must that land before Stage C? (Options A,
   B, C, F)
6. Does a full-panel measurement before the disclosure is posted use up the prospective production
   prediction, and would changing the occlusion criterion for a stated methodological reason be the
   act trsx5:49 fences? (Options D, E)
