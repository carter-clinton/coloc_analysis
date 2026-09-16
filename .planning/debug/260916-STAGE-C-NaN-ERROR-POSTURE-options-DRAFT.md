# Stage C: what happens to a region that RAISES on a leftover pairwise NaN (options draft)

**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by
an adjudicator who has not seen our reasoning: options are laid out neutrally, with no recommendation.
Every claim cites file:line. Labels: **TEXT** = what a posted record says; **CODE** = what shipped code
does; **READING** = an interpretation offered for adjudication, not a finding.

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
- Code at HEAD `c93e97b`.

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

---

## 0. Premise corrections: the question is narrower than "the fire will halt"

**P1: The committed Stage C command does not use `--fail-fast`.** STEP 10 runs
`run_native_ld_panel.py … --mode square --ancestry AFR` with no `--fail-fast`
(`260812-ox1-AGENT-PROMPT.md:398`), and the card says so twice (`:372-373`, `:417`; also
`260812-ox1-READY-TO-FIRE.md:360-366`). The flag's own help text says "Stage C runs without
--fail-fast" (`run_native_ld_panel.py:1325-1328`).

**P2: Without the flag, a raising region does not stop the loop (CODE).** The NaN raise is
`plink_ld_to_npz.read_square_bin` (`plink_ld_to_npz.py:218-228`), called at
`run_native_ld_panel.py:1090-1093`. `process_region` catches it (`:1144-1146`) and records
`status = "error: square LD carries NaN …"`. The panel row is appended (`:1148`), no `.npz` is uploaded
(uploads happen only under `if ok:`, `:1101-1107`), and the region returns. The loop raises only
`if fail_fast and status != "ok"` (`:1278-1279`).

**P3: What does stop is the human monitoring gate, at the next check-in.** `fire_verifier stage-c`
(`fire_verifier.py:1097-1099`) classifies `error:` as FAILURE (`:302-303`, `:324-326`) and returns
FINDING with the message "Stage C runs without --fail-fast so the loop continues by design; report these
to Carter … Do NOT re-fire blindly" (`:381-389`). Any failed check gives exit 1 (`:976-981`). Under
rule R8 an exit 1 is a STOP-and-report for the agent (`AGENT-PROMPT.md:55-61`, `:422-423`;
`fire_verifier.py:999-1001`). The `nohup` process keeps running.

**P4: Adding `--fail-fast` to Stage C would halt on regions already banked.** The flag raises on any
`status != "ok"` (`run_native_ld_panel.py:1278`). An already-banked region returns
`skipped_idempotent` (`:806-815`), and `00001`, `00017` and `00040__sub14` are banked
(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`run_native_ld_panel.py:1325-1328`).

**P5: One raise is observed; the second is predicted.** `m2_region_00057` (+1) raised in Stage B
(`260824-STAGE-B-HALT-…md:11-16`). `m2_region_00149` (−1) is classified as surviving into the panel by
the pairwise-completeness scan (`.planning/osf_deviations.md:657-663`, a DRAFTED — NOT POSTED ledger
entry) but has **not** been run through `run_native_ld_panel`.

**So the open question is not halt versus continue.** It is: **what pre-registered disposition does a
region get when the raw-panel NaN-raise contract fires, the region banks nothing, and the loop moves
on?** And does settling that need a posted amendment-update before Stage C?

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
| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `run_native_ld_panel.py:1068-1069`, before conversion at `:1090`). No `.npz` upload. | `run_native_ld_panel.py:1144-1148`, `:1101-1107` |
| C3 | Local scratch is reclaimed **only** when `status == "ok"`. The docstring puts intermediates at "~30+ GiB/region … overflows any finite scratch disk". | `:1149-1154`, `:723-725` |
| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:806-815`, an infeasible one at `:866-872`). It is uploaded **only** on deferral or on `ok`. | written `:923-939`; uploaded `:961-965` (deferral), `:1129-1139` (inside `if ok:`) |
| C5 | Resume skips a region only if its `.npz` exists, so an `error:` region is recomputed on every re-fire. | `:799-815` |
| C6 | Verifier: deferrals PASS ("the gates working"), `error:` = FINDING, an unknown status = HARD_STOP. The vocabulary is held by `test_shipped_status_vocabulary_is_covered_by_the_allow_list`. | `fire_verifier.py:330-399`, `:309-312` |
| C7 | Precedent for a region that banks nothing outside the three posted branches: `deferred_infeasible_square` (`run_native_ld_panel.py:866-872`). Registered in-repo as "a DISCLOSURE OBLIGATION — not blocking the fire", with measured numbers owed at publication, a remedy path recorded, and a named enforcer. | `deferred-items.md:1148-1191`; enforcer `fire_verifier.py:875-939` |
| C8 | The runbook calls a partial bank "a real, reportable outcome". | `READY-TO-FIRE.md:360-366`; `AGENT-PROMPT.md:424-428` |

---

## 3. Options

### Option A: run the card as committed (no code change)

- **Behaviour:** no `--fail-fast`. A raising region records `error:`, banks nothing, and the loop
  continues (P2). At the next check-in the gate exits 1 and the agent reports to Carter (P3). At
  closeout the region is reported as unbanked and logged as a deviation.
- **Code needed:** none.
- **Already pre-registered?**
  - The *raise* is (T1). The *non-halting loop* is runbook, not OSF.
  - The *disposition* is not. No branch fits: NONE needs "the panel and fine-mapping result stand unmodified"
    (trsx5:43), but nothing was banked; EXCLUDED needs "fine-mapping proceeds on the reduced variant set"
    (trsx5:45); DEFERRED's trigger is the anomaly gate (T3), and 00057's gate did **not** fire (a region
    whose gate fires returns at `run_native_ld_panel.py:967` before plink runs, so it cannot reach the raise at `:1090`).
  - *READING 1:* logging it under T6 changes no criterion, no gate and no variant's treatment. A
    deviation entry plus disclosure is what the posted discipline already requires, so no amendment
    is needed before code (and no code is involved).
  - *READING 2:* T5 presents the three branches as the complete
    list, and trsx5:53 fixes "the three outcome branches … before any occlusion-handling code fires".
    A region in none of them is a fourth outcome, which may need a posted amendment-update **before**
    Stage C.
- **Consequences:**
  - Each raising region is a coverage gap shaped like R4-COVERAGE (C7), but with **no** registered
    disclosure obligation or enforcer yet.
  - After the first raise, every later `stage-c` check-in exits 1 for the rest of the ~11 days (`AGENT-PROMPT.md:393`). Each is
    an R8 STOP. A *new* failure then shows up on a gate that is already red. The verifier does print
    per-status counts (`fire_verifier.py:363-370`), so a new failure is visible only by diffing check-ins.
  - C3, C4 and C5 apply (see §4).

### Option B: send raising regions to `BRANCH_AFR_OCC_DEFERRED` (defer, don't exclude)

- **Behaviour:** the producer catches this particular raise, records a deferral status, and the
  verifier PASSes it.
- **Code needed:** yes. The producer's error path, plus either a new status prefix (which turns the C6
  enforcer red until the vocabulary is extended) or reuse of `deferred_occlusion_anomaly:`.
- **Already pre-registered?** *READING:* no. DEFERRED is tied to the anomaly-gate trigger (T3), and
  defer-not-exclude is stated for "a region over the anomaly gate" (T2). Adding a NaN-raise trigger
  changes what DEFERRED means, which would need an amendment-update **before** code.
  - Reusing `deferred_occlusion_anomaly:` would record an anomaly the gate did not find.
  - The surviving class has "no covering record for EITHER member" (`osf_deviations.md:703-704`, a
    DRAFTED — NOT POSTED entry), so it is not an occlusion under clause (a) (mk7ze P300-302 / R467-469).
  - A new token runs into the explicit "NO new token" sentence (mk7ze P316 / R483). That sentence is
    scoped to the companion condition, so how far it reaches is itself a question for review.
- **Consequences:** check-ins stay green. A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"
  (`fire_verifier.py:335-336`). "Deferred for
  re-diagnosis" presumes a diagnosis still to do, but the mechanism for this class is already
  established for 00057 (`260824-STAGE-B-HALT-…md:150-179`).

### Option C: halt on each raise and re-diagnose before continuing

- **Behaviour:** literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so
  this option means the operator stopping the fire at the first `error:` row.
- **Code needed:** none (runbook change only).
- **Already pre-registered?** No posted text requires or forbids halting, so no amendment either way.
- **Consequences:** the Stage B halt record already argues against this at an unknown rate:
  "`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown
  per-region failure rate" (`260824-STAGE-B-HALT-…md:104-107`). *For planning only, not a calibrated
  rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:660-663`). The sample was systematic-by-span, not
  random (mk7ze P88-89 / R255-256), and the one case is predicted, not observed (P5). Scaled to 276 that is ≈13 regions, with an
  exact 95% binomial range of 0.3–66.

### Option D: measure before deciding (combines with A or B)

- **Behaviour:** Carter runs the existing pairwise-completeness scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before
  Stage C, so any posture is chosen against a measured list of regions expected to raise. This is a
  read-only measurement. *Unmeasured scaling:* the 21-region run took 48 min (STATE.md frontmatter,
  2026-09-01), which scales linearly to ~10.5 h.
- **Code needed:** none expected. Whether the scan runs unchanged over all 276 has **not** been checked.
- **Already pre-registered?** A read-only measurement changes no analysis choice, so no amendment.
  **But there is a sequencing constraint.** The disclosure's prospective production prediction is "to
  be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"
  (`osf_deviations.md:685-689`), and "Production tests the rate on BOTH sides" (`:682`). A full-panel
  scan would measure that same both-sides rate before production does; whether that uses up the
  prediction is question 5.
- **Consequences:** the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).

### Option E: change what reaches the matrix (listed for completeness)

Options here would be widening the predicate to cover −1/+1, a pairwise-completeness exclusion rule, or
NaN→0. NaN→0 is prohibited (T8). The criterion is unchanged and fenced (T8). "NO PREDICATE CHANGE …
calibrate-to-pass at n=1" is already recorded (`osf_deviations.md:670-671`). Any new exclusion rule
would be an amendment-update **before** code.

---

## 4. Issues that apply to any option that leaves a raising region unbanked (A, C, and B unless B's code also uploads evidence)

- **X1: evidence egress versus the mk7ze closeout commitment.** mk7ze P247-250 commits that "both
  complete distributions fold in at closeout". A raising region's sidecar (site counts, inflation) is
  written locally but never uploaded (C4). Its `n_dropped_occluded` row count does reach the panel TSV
  (C2); its site count and inflation do not. As shipped, the closeout distributions would be missing
  every raising region unless scratch is harvested by hand. Closing that gap in code touches the fire
  path and needs a decision.
- **X2: scratch fills up.** A raising region's `.ld.bin` (n_var² × 4 B; ≈57.6 GB at the
  120,000-variant ceiling; `READY-TO-FIRE.md:369-370`) stays in scratch (C3). The VM's scratch capacity was **not** checked here. A
  few large raising regions could make later regions fail with `error:` for an unrelated reason.
- **X3: resume re-spends compute.** Every re-fire recomputes and re-raises each raising region (C5),
  assuming identical inputs.
- **X4: the disclosure obligation has no enforcer.** R4-COVERAGE has one (C7). This class does not.

## 5. Questions for the adjudicator

1. Does a region that banks nothing *because the raw-panel NaN-raise contract fired* fall under any of
   the three posted branches (T4, T3)? If not, does T5 require a posted amendment-update before Stage C,
   or is a deviation entry plus disclosure (T6) enough?
2. Would routing such a region to `BRANCH_AFR_OCC_DEFERRED` change what DEFERRED means (T3), and does
   "NO new token" (mk7ze P316) reach beyond the companion condition?
3. Should the R4-COVERAGE precedent (C7: a disclosure obligation with a named enforcer, not blocking
   the fire) govern this class?
4. Does honouring mk7ze P247-250 require that a raising region's gate evidence reach the bucket (X1)?
   If so, must that land before Stage C?
5. Does a full-panel scan (D) before the disclosure is posted use up the prospective production
   prediction?
