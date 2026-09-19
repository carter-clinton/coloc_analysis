---
task: 260918-qz0
branch: m3-W2-aou-deltas
date: 2026-09-18
docs_only: true
code_changed: false
pushed: false
status: COMPLETE
---

# quick-260918-qz0 — SUMMARY

Banked the external reviewer's brief-blind **Stage C adjudication** of 2026-09-18 as received, and
recorded the posture Carter decided from it (D1-D7). **Records only; no code.** The disclosure stays
**DRAFTED — NOT POSTED**, Finding 2 stays **NOT ESTABLISHED**, the options draft v2 stays
byte-frozen, nothing was posted, sent or pushed, and neither `STATE.md` nor `HANDOFF.json` was
written.

## Commits

| commit | contents |
|---|---|
| `1647840` (`16478409fe2a2535d0ce4caa3bb75a4626018dc6`) | the five deliverables (Task 2) |
| second commit | this PLAN + this SUMMARY (Task 3) |

## The five deliverables — MEASURED md5s

All five equal their pins, both on disk and as committed blobs (`git show HEAD:<path> | md5sum`).

| path | md5 | bytes | lines |
|---|---|---|---|
| `.planning/osf_deviations.md` | `36767b66449d6eadf7ca82a145f23a6f` | 94,237 | 1189 |
| `.planning/DECISIONS.md` | `9a48a37bb388529c146bd1326f6bf5ea` | 226,582 | 2841 |
| `260812-ox1-AGENT-PROMPT.md` | `48295e108d4ff3b0dab3bf366b70c085` | 46,067 | 709 |
| `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` | `2419f90021f585d09a69133739fe4526` | 89,642 | 1532 |
| `…/260918-qz0-SETH-STAGEC-ADJUDICATION-as-received.md` | `3b4b7430c2ef6b03549f946f9d602bf1` | 26,699 | 188 |

Bases in (all re-checked on the real paths immediately before install, and again against the git
blobs): osf `22e1b1db…` / 1139, dec `1f4a1083…` / 2632, ap `bd7a5c2b…` / 671, def `64fa7a8b…` /
1450, adjudication scratch `5e35a093a1920ad0f453ae64b353f2e4` / 23,225 B / 141 lines. The couriered
draft v2 (`46537925de303ffb8a2d2b31d8160071`) and v1 (`763f412bb1a8dbdb38f2cc332ed5a21d`) are
**byte-unchanged**.

The four extracted scripts matched their embedded md5 pins exactly:
`qz0_cites.py 06500b1362f3dda23b2e9f08a863260b` (8,835 B),
`qz0_apply.py 37484223ac83a3ce431744035808d04d` (40,157 B),
`qz0_guard.py 3952eec5f6563b5dede72f1579ca18fa` (60,287 B),
`qz0_negctl.py d4d0df37ca278578ae06eeb100fec79e` (24,324 B).
No payload text was retyped: every new line came from `qz0_apply.py`, extracted from the PLAN.

## The four sites and the new file — after-line ranges from the guard census

Census lines, verbatim (difflib indexes the element after the final newline, hence the `+1` form):

```
  census osf: insert base 1141-1140 -> after 1141-1190
  census dec: insert base 2634-2633 -> after 2634-2842
  census ap: insert base 640-639 -> after 640-677
  census def: insert base 1452-1451 -> after 1452-1533
```

| id | file | edit | after lines | what landed |
|---|---|---|---|---|
| S1 | osf | EOF append, +50 | 1140-1189 | `#### (11) RAISING-REGION ACCOUNTING FOR THE PRODUCTION RUN` — the accounting paragraph (banks no panel / not coerced / no post-hoc treatment / classified on the occlusion axis by its computed count / reported at closeout as UNBANKED, known-class or UNCLASSIFIED; the count a COVERAGE RESULT, ⛔ **not** a deviation — T1 fired as written), the TWO-CONTRACTS framing correction, his §0-iii **as a reading**, his counter-caveat at his strength, and NO OSF amendment |
| S2 | dec | EOF append, +209 | 2633-2841 | `DEC-2026-09-18-stage-c-nan-posture-adopted` — ADOPTED (A's behaviour = T1 executing, with C's stop for an UNCLASSIFIED raise), REJECTED (B, F-as-drafted, E) with his reasons, D only post-the-disclosure, NO OSF amendment, Carter's three implementation decisions, the three determinations of OURS, and the draft's slip |
| S3 | ap | INSERT after :639, +38 | 640-677 | `STAGE-C RAISE POSTURE — THE PRE-FIRE RESUME RULE`, immediately below the gate's *"Any red = STOP under R8"* sentence |
| S4 | def | EOF append, +82 | 1451-1532 | `## R5-RAISED-NAN` on the R4-COVERAGE/C7 template, enforcer NAMED and marked ⛔ NOT WRITTEN, PENDING quick-260918-qz5, with its scope limit stated |
| BANK | new | — | 188 lines | the provenance header (⛔ NOT BYTE-VERIFIED, scratch md5/size/lines, ~18:46 EDT paste, what he read and did not read, a position not a ruling, the arithmetic slip, our Q5 correction, ⛔ correspondence is not a source) + the pasted text byte-for-byte in a 4-backtick fence |

Three of the four edits are pure EOF appends; the fourth inserts at `:639`, and every base line of
every target is byte-identical (the AGENT-PROMPT tail shifted by exactly **+38**, byte-identical).
Exactly one changed hunk per file, each at the planned position.

## Guard — GREEN on the build and against the committed blobs

```
RESULT GREEN  1127/1127 PASS
```

exit 0, **0 FAIL lines**, **155 distinct check ids**. Run twice: on the scratch build, and on the
real paths with the four bases read from `git show HEAD:` — the two outputs are **byte-identical**.

### G01 — the five superseded literals, per file, normalized (verbatim)

```
  enumeration G01 (the five superseded literals, per file, normalized):
    1.652   osf   base 0  after 0
    1.652   dec   base 0  after 0
    1.652   ap    base 0  after 0
    1.652   def   base 0  after 0
    1.652   bank  count 0 (want 0)
    0.0366  osf   base 1  after 1
    0.0366  dec   base 0  after 0
    0.0366  ap    base 0  after 0
    0.0366  def   base 0  after 0
    0.0366  bank  count 0 (want 0)
    1.564   osf   base 0  after 0
    1.564   dec   base 0  after 0
    1.564   ap    base 0  after 0
    1.564   def   base 0  after 0
    1.564   bank  count 0 (want 0)
    0.0556  osf   base 1  after 1
    0.0556  dec   base 0  after 0
    0.0556  ap    base 0  after 0
    0.0556  def   base 0  after 0
    0.0556  bank  count 0 (want 0)
    1.969   osf   base 2  after 2
    1.969   dec   base 0  after 0
    1.969   ap    base 0  after 0
    1.969   def   base 0  after 0
    1.969   bank  count 0 (want 0)
```

No literal increases anywhere; all five are **0 in the bank file**.

### G05 — nothing says or implies that clustering EXPLAINS Finding 2 (verbatim)

```
    -> 0 occurrence(s) in the new osf §(11) (want 0)
    -> 0 occurrence(s) in the new DECISIONS entry (want 0)
    -> 0 occurrence(s) in the new AGENT-PROMPT block (want 0)
    -> 0 occurrence(s) in the new deferred-items item (want 0)
    -> 0 occurrence(s) in the bank provenance header (want 0)
  enumeration G05-bank-fence: explain-family in the bank total 0, inside the verbatim fence 0
```

### G06 — every quotation re-checked against its source (verbatim)

```
  enumeration G06-quotes (every quotation, re-checked against its source):
    adj True  in-record True  T1 is the disposition, at the only level the posted text speaks to: a NaN-bear
    adj True  in-record True  THE GATES WORKING
    adj True  in-record True  T1 pre-registered the treatment; the rest is accounting, and it rides on the d
    adj True  in-record True  a planning figure I carried from an earlier session, not a Stage-B measurement
    adj True  in-record True  A gate that is always red is a gate no one reads — the second failure arrives 
    adj True  in-record True  I believe it does via pre_window_n_var, but I did not verify the column, so: c
    adj True  in-record True  if from plink --freq independent of the LD pass
    adj True  in-record True  contains no occlusion-undefined pair
    adj True  in-record True  contains >=1 occluded variant under the gate
    adj True  in-record True  the raw per-region panel .npz reader continues to RAISE on any NaN rather than
    adj True  in-record True  banks no panel, is not coerced, receives no post-hoc treatment, is classified 
    adj True  in-record True  The count of such regions is a coverage result, not a deviation.
    adj True  in-record True  this is not a deviation from pre-registration; T1 fired as written
    adj True  in-record True  outcome space has one element: raise, bank nothing
    adj True  in-record True  the outcome space of occlusion handling
    adj True  in-record True  is not a gap in the list
    adj True  in-record True  unbanked, outside the branch list, disclosure obligation with a named enforcer
    adj True  in-record True  it counts the predicted case as the observed rate
    v2  True  in-record True  For planning only, not a calibrated rate
    v2  True  in-record True  the one case is predicted, not observed
  enumeration G07-D1-count: bank header says ['three'], the DECISIONS heading says ['three'], and there are 3 '- **(x)**' items
```

18 adjudication quotations + 2 byte-frozen-v2 quotations: **all 20 matched their source** (wording
**and** capitalization) and **all 20 actually land in a record**. `0` `adj False`, `0`
`in-record False`. The determination count reconciles in all three places.

`G08-D2-idrefs`: `ids ['R4-COVERAGE', 'R5-RAISED-NAN'], unresolved []` — every `R4-*`/`R5-*` id the
new entry names resolves to a real heading in the after `deferred-items.md`.

### G10 — the §(11) makes no claim about a predicate (verbatim)

```
  enumeration G10 ('predicate' in the new osf text): 0 occurrence(s)
```

### G13 — line-position safety (verbatim)

```
  citation re-resolution: 393 rows; 361 unmoved and byte-identical; 0 MOVED; 32 out of range (not a line in that file)
  pass-C INFO (not a gate): 432 rows, stored digest d22c67c6c73584f34252fefa0d36a8dc
  pass-C re-resolution: 432 rows; 398 unmoved and byte-identical; 2 MOVED; 32 out of range
    MOVED  ap   .planning/quick/260918-qz5-stage-c-pre-fire-code-hardening-per-the-/260918-qz5-PLAN.md L166   :640-643 -> :678-681  SELF-DOCUMENTING (its line carries the post-shift range too)
    MOVED  ap   .planning/quick/260918-qz5-stage-c-pre-fire-code-hardening-per-the-/260918-qz5-PLAN.md L166   :646-648 -> :684-686  SELF-DOCUMENTING (its line carries the post-shift range too)
  bare-reference scan (plain integers in the AGENT-PROMPT's moving range [640,671], on lines that NAME the runbook): 0 row(s)
```

`G13-oor-classified`: out-of-range per target `{'osf': 6, 'dec': 0, 'ap': 26, 'def': 0}` and
in-range per target `{'osf': 203, 'dec': 47, 'ap': 43, 'def': 68}` — both equal their pins.

## Negative controls

```
POSITIVE CONTROL (unmutated): 1127 checks, 155 ids, FAIL ids = [] -> GREEN
COVERAGE: 155/155 check ids observed RED by at least one control
NEGCTL RESULT: ALL CONTROLS OBSERVED RED, ALL IDS COVERED
```

**131** lines ending in `  OK` (i.e. **131/131** controls each observed RED on their expected ids),
**0** `INVALID CONTROL`, **0** `MISSING`, **0** `UNCOVERED`; exit 0.

## RED on the unedited files (the guard can see the old state)

```
RESULT RED  933/1119 PASS
```

exit 1, **57 distinct FAIL ids**:

`G00-ap-head`, `G00-dec-head`, `G00-def-head`, `G00-head-11`, `G02-new-drafted`, `G02-new-notauth`,
`G02-osf-drafted`, `G03-ap-frozen-tail`, `G03-osf-10e`, `G04-census-ap-nonempty`,
`G04-census-dec-nonempty`, `G04-census-def-nonempty`, `G04-census-osf-nonempty`,
`G04-one-hunk-ap`, `G04-one-hunk-dec`, `G04-one-hunk-def`, `G04-one-hunk-osf`, `G06-quote-used`,
`G07-D1-count`, `G08-D2-adopted`, `G08-D2-bankref`, `G08-D2-c5-correction`, `G08-D2-carter3`,
`G08-D2-carter3-items`, `G08-D2-idrefs-nonvacuous`, `G08-D2-noamend`, `G08-D2-provenance`,
`G08-D2-qz5-not-landed`, `G08-D2-rejected`, `G09-D6-attributed`, `G09-D6a`, `G09-D6b`, `G09-D6c`,
`G09-D7`, `G09-D7-both-places`, `G10-D3-accounting`, `G10-D3-caveat`, `G10-D3-framing`,
`G10-D3-noamend`, `G10-D3-reading`, `G11-D4-conditional`, `G11-D4-decref`, `G11-D4-denominator`,
`G11-D4-exception`, `G11-D4-gate-today`, `G11-D4-position`, `G11-D4-rediagnosis`,
`G11-D4-resume-mechanism`, `G12-D5`, `G12-D5-c7-adopted`, `G12-D5-c7-insufficient`,
`G12-D5-enforcer-named`, `G12-D5-enforcer-pending`, `G12-D5-enforcer-scope`,
`G12-D5-heading-is-the-gate`, `G12-D5-numbers-owed`, `G12-D5-old-enforcer-present`.

All eleven ids the plan names as required coverage are present, plus the four
`G04-census-*-nonempty`.

## Standing enforcers — BEFORE == AFTER

Run **without** `set -e` and **without** `|| true`; two are expected to exit 1.

| enforcer | BEFORE last line | AFTER last line | exit |
|---|---|---|---|
| `uer guard.py` | `37/40 PASS` | `37/40 PASS` | 1 == 1 |
| `vqq --live` | `RESULT RED checks=446 parsed=112 table=112 verified=102 c-res=112  reds=[…]` | identical | 1 == 1 |
| `u9p ledger` | `RESULT: ALL CHECKS PASSED (section: ledger)` | identical | 0 == 0 |

The line-normalized PASS/FAIL/RESULT multisets are **identical** for all three (`diff` printed
nothing, `rc=0` each). The `reds=[…]` list is **byte-equal** before and after, and is the expected
10-element list:

```
BEFORE: reds=['c:c01', 'c:c02', 'c:c03', 'c:c04', 'c:c18', 'c:c62', 'c:c63', 'c:n02', 'c:n48', 'c:n06']
AFTER : reds=['c:c01', 'c:c02', 'c:c03', 'c:c04', 'c:c18', 'c:c62', 'c:c63', 'c:n02', 'c:n48', 'c:n06']
```

## Citations

- **Pass A (TRACKED ONLY, and that limit is stated not implied):** **393 rows** (osf 209, dec 47,
  ap 69, def 68), digest `a1bf7a72f847d21267ae5c26769cb4f7` — **pinned, and unchanged after the
  five files were installed**. **361 in range**, all re-resolving to byte-identical lines at the
  **same** line numbers; **0 MOVED**; **32 out of range**, classified per target against the pin.
- **Pass B (bare integers in the AGENT-PROMPT's moving range `[640,671]` on lines that name the
  runbook):** **0 rows**, digest `d751713988987e9331980363e24189ce` — **pinned, unchanged**.
- **Pass C (UNTRACKED-INCLUSIVE, ⛔ NOT PINNED — INFO only):** **432 rows**, digest
  `d22c67c6c73584f34252fefa0d36a8dc`, **2 MOVED, 0 STALE**, both on `260918-qz5-PLAN.md`'s `L166`
  revision-log line, each **SELF-DOCUMENTING** (the same line carries the post-shift range, i.e. it
  narrates the move). It saw **4 untracked files pass A cannot** — `260813-t21-SUMMARY.md`,
  `260814-guk-PLAN.md`, `260916-vqr-VERIFICATION.md`, `260918-qz5-PLAN.md` — so the moved-empty
  gate did not pass by looking at nothing. ⛔ **Pass C's row count and digest are INFO, never a
  gate:** it reads untracked sibling plans that other tasks edit concurrently, so a digest over
  them goes stale by design; the gate is the **property** (`G13-untracked-moved-empty`), and it is
  GREEN. The row count and digest happened to equal the plan-time figures this run; that is not a
  pin and must not be treated as one.
- `files-scanned` drifted informationally from `[152, 179, 53, 108]` to `[152, 180, 54, 108]` after
  install (the new text names `DECISIONS.md` and the runbook path). **The digests and row counts —
  the actual pins — did not move**, so the installed files add no *line citation* into any target.

## ⛔ The resume rule's mechanism sentence in rev 1-2 was FALSE

Revisions 1-2 of this plan would have written *"Resume recomputes only the error: regions"* — copied
from the adjudication's narrowing of claim C5 — into a **pre-fire operating instruction**.
**MEASURED at `74f962d`:** the skip guard keys on the region's `.npz` (with the
`_MIN_REGION_NPZ_BYTES` floor) and is the **only** skip condition; neither `deferred_*` path banks
an `.npz` — so **every region that banked nothing recomputes** (`error:`, `verify_failed` **and
both** `deferred_*` classes), and so does a truncated `.npz`. The runbook carries the **code-true**
sentence, the narrowed form is **banned** by `G11-D4-resume-mechanism` (RED control N236), and the
correction is recorded in the DEC entry itself, not only in this SUMMARY.

## ⛔ The sibling plan: qz0 breaks no citation; ONE pin is owed

`260918-qz5-PLAN.md` revision 3 already **expects** this task to have run: it pins the runbook
**POST-qz0** and refuses to start otherwise, names qz0 in `depends_on`, records the **+38** shift,
and relocates both egress sentences by **unique quoted text** instead of by line number. So **qz0
breaks no citation** — pass C finds the pre-shift ranges only on qz5's `:166` revision-log row,
which carries the post-shift ranges on the same line. ⛔ **What the orchestrator must still update
is one pin:** the post-qz0 runbook is now `48295e108d4ff3b0dab3bf366b70c085` / **709 lines** /
**46,067 B**, where qz5 pins `f5584d4d…` / 46,052 B. **The line count and the +38 shift are
unchanged**, so qz5's narrated `:678-681` / `:684-686` stay correct. This task rewrote no other
plan's file.

## ⛔ The BROWSER-PASTE gap

The resume rule lands on the **AGENT** surface only (measured home of STEP 9/9d). The
**PASTE**-surface sync is **assigned and carried in `260918-qz5-PLAN.md` revision 3 at its `:167`**
— P6 Step 3b (the condensed block in BROWSER-PASTE), Step 3c (a test that BOTH surfaces carry the
four rules and the corrected resume mechanism and that NEITHER carries the narrowed form), and Step
4 (a READY-TO-FIRE pointer, not a third copy) — correcting its old `:184` disclaimer. **Both
halves:** the gap is real **until qz5 runs**, and it is **owned there**, not merely recommended.
Nothing in this task's records implies the operator's pasted text already carries the rule.

## ⛔ The orchestrator's `.afreq` premise was WRONG

The brief described the `.afreq` sidecar as *"plink's own output from the same pass"*. **That is
false.** `build_plink_ld_command` **never passes `--freq`** (the square branch emits
`--mac 1 --nonfounders --write-snplist --r square bin4`), plink **1.9**'s `--freq` would write
`{prefix}.frq`, and `.afreq` is plink **2.0**'s name (already recorded as **AF-1**). So the sidecar
is an **existence-gated optional input** and its upload is **existence-gated DEAD CODE on the fire
path** — proven in practice by **5** `WARNING: no --allele-freq sidecar for region '…'` lines in
`260812-ox1-evidence.log` over `m2_region_00001` and `m2_region_00002`. **Carter's decision is
honoured unchanged — it still moves in qz5 — but the record carries the measurement**, calls the
move **DORMANT**, and states that it closes **no part** of the mk7ze P248-250 gap. This is recorded
as the orchestrator's error, not softened.

## The `n_var` 2,854 — what kind of evidence it is

The `n_var` **2,854** for `m2_region_00057` was **read off the production panel TSV** in **Carter's
pasted VM terminal output of 2026-09-17** (the COST-1 card), which reported
`gs://rw-migration-aou-rw-476cdac2/ld/AFR_aou/m3-W2-native-plink-panel.tsv` as **6 lines (header +
5)** with the raising row reading `m2_region_00057 chr15 2854 error: square LD carries NaN …`. ⚠
**Its evidence class is stated, not implied:** it is a **chat paste**, it is **NOT byte-verified**,
and **no panel TSV is tracked in this repo** — so the **in-repo verification is the code path**
(`result["n_var"] = n_var` at `:1228` before the raise at `:1233`; the handler at `:1287-1288`
rewrites only `status`; `append_panel_row(...)` at `:1291` runs unconditionally; `_PANEL_COLUMNS`
carries `n_var` and there is **no** `pre_window_n_var` column), and the same figure is
independently corroborated by the Stage-B halt record's forensics.

## ⚠ The three determinations in D6 are OURS

They are **our** measurements and **our** readings — not the reviewer's — recorded under a heading
that says so, each naming what was measured and what could not be verified in this repo, and **each
open to his objection**. (a) his §3e check VERIFIED GREEN with the mechanism he guessed corrected;
(b) the `.afreq` sidecar measured as existence-gated dead code, DORMANT, closing no part of the
mk7ze P248-250 gap; (c) his **Q5** fix **as prescribed** does not reach the raising class at all,
because a raise jumps past the whole `if gs_mode:` block — his diagnosis and requirement stand, the
edit was too small.

## Path scope — NO CODE, with an observed RED control

- `git status --porcelain --untracked-files=all`, sorted, before vs after: **nothing vanished**
  (`comm -23` = 0 lines) and **exactly 5 new lines**:
  ` M .planning/DECISIONS.md`, ` M .planning/osf_deviations.md`,
  ` M .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`,
  ` M .planning/quick/260812-ox1-…/260812-ox1-AGENT-PROMPT.md`,
  `?? .planning/quick/260918-qz0-…/260918-qz0-SETH-STAGEC-ADJUDICATION-as-received.md`.
- **NO CODE CHANGED:** `git status --porcelain -- src tests config bin Snakefile workflow | wc -l`
  == **0** (untracked INCLUDED, so a new file would count).
- Frozen trees, tracked-only:
  `git status --porcelain --untracked-files=no -- .planning/amendments .planning/STATE.md .planning/HANDOFF.json .planning/debug | wc -l`
  == **0**. (`--untracked-files=no` is load-bearing: `.planning/debug/` carries a **pre-existing**
  untracked file, `m3-producer-unbounded-dense-read.md`; nothing new appearing there is already
  proven by the `comm -13` check.)
- **RED CONTROL, observed:** `touch src/python/__qz0_negctl_probe.py` → `comm -13` showed a **6th**
  line `?? src/python/__qz0_negctl_probe.py` and the NO-CODE count became **1** (**RED**). After
  `rm`, back to **exactly the 5 lines** and **0** (**GREEN again**). Both observations recorded.
- The commit staged **five explicit paths** (never `git add -A` or `.`); the staged set was asserted
  equal to exactly those five before committing. `git show --stat HEAD` lists exactly 5 files, 567
  insertions, 0 deletions. Tracked tree clean after the commit.

## KNOWN AND DELIBERATELY NOT ACTED ON — reported for Carter, not fixed

1. ⚠ **PLANNER-FOUND, ACCEPTED by the orchestrator as his error:** the brief's `.afreq` premise was
   wrong (see above). The record carries the measurement; the move stays DORMANT and closes no part
   of the mk7ze P248-250 gap.
2. ⚠ **PLANNER-FOUND, ACCEPTED:** the brief's quotation said *"departure"*; the adjudication says
   ***deviation***. The record carries **his** word inside the quotation ("departure" survives only
   in our own following clause about mislabelling).
3. **The resume rule lands in `AGENT-PROMPT` only; the `BROWSER-PASTE` sync is ROUTED to
   `quick-260918-qz5` revision 3** (its `:167`, P6 Steps 3b/3c + a READY-TO-FIRE pointer). The gap
   is real until qz5 runs and is owned there. Out of scope for qz0 by path list.
4. **The adjudication is not byte-verified.** It came from a chat paste; the header says so in those
   words and pins the scratch md5, size and line count.
5. **`$ADJ`'s first line opens "Seth — Stage C adjudication…".** Banked verbatim, not interpreted.
6. ⚠ **PLANNER-FOUND / REVISED, ACCEPTED:** the **2,854 WAS** read off the production panel TSV (in
   Carter's pasted VM output of 2026-09-17), and its evidence class is now stated — chat paste, NOT
   byte-verified, no panel TSV tracked here; the code path is the in-repo verification.
7. **The stateful gate is a decision, not a behaviour.** Recorded before the fire, implemented in
   `quick-260918-qz5`; the DEC entry says in words that it is **not in force until that task lands**,
   and the runbook block says what the gate can actually see today.
8. **LOW-1 stays deferred with no date.** Its blocking measurement is COST-1's per-region wall time,
   and COST-1's own target region is currently invalidated (`m2_region_00071` deferred at `n_var`
   169,803 > 120,000). Contingent on a measurement, not on a schedule.
9. ⚠ **PLANNER-FOUND (the FOURTH), and it was ours to catch because we copied it from the
   adjudication:** the resume rule's mechanism sentence was FALSE (see the dedicated section above).
10. ⛔ **ONE NUMBER THE ORCHESTRATOR MUST UPDATE IN THE SIBLING PLAN, AND NOTHING ELSE:** qz5's
    post-qz0 runbook pin, `f5584d4d…` / 46,052 B → **`48295e108d4ff3b0dab3bf366b70c085` / 709 lines
    / 46,067 B**. Line count and +38 shift unchanged. This task rewrote no other plan's file.

## Deviations from the plan

1. **ORCHESTRATOR-MADE correction to the PLAN, before execution (not mine):** two stale "120
   controls" sites became **"131"**. The plan's own `:197` / `:689` / `:706` / `:755` already said
   131, and the orchestrator measured 131 firsthand; the pre-correction copy is in session scratch
   as `qz0-PLAN.pre-orch-fix.md`. The corrected PLAN md5 `e65a317f60a230783b4accfd0180730d` was
   verified before execution, and the negctl run **measured 131** `  OK` lines, confirming the
   correction.
2. **Recorded, not acted on — a plan-internal inconsistency:** Task 3 asks for "the **eight** KNOWN
   AND DELIBERATELY NOT ACTED ON items", but the plan's context section enumerates **ten** (items 9
   and 10 were added by revisions 3 and 4 and the Task 3 count was not updated). **All ten are
   recorded above**, because dropping two would lose the B3 false-mechanism item and the sibling-pin
   item. No plan text was edited.
3. **Recorded, not acted on — a stale figure inside the pinned commit message:** the Task 2 commit
   body says *"Guard 1127/1127 over 143 ids"*. The **measured** value is **155** distinct check ids
   (143 was rev 1-2's figure). The orchestrator's instruction was to use the commit messages
   **exactly as the plan gives them**, so the message was committed **verbatim** rather than
   silently corrected. The correct figure is recorded here and in the hand-back. The other figures
   in that message (`131/131` RED controls, `155/155` ids covered, `0 of 361` citations) are
   correct as written.
4. Pass C's row count (432) and digest (`d22c67c6c73584f34252fefa0d36a8dc`) matched the plan-time
   INFO figures this run. They are reported as **INFO, not pins**, exactly as the plan requires.

No other deviation. No `set -e`, no `|| true` around the enforcers. No `git add -A` or `git add .`.
No workaround was applied to any tool call; none was blocked or refused.

## Not done here, by design

**STATE.md / HANDOFF.json not written — orchestrator close-out.** Nothing was posted, reserved,
uploaded, sent or pushed; no OSF, reviewer, cloud or network action was taken; the options draft v1
and v2 are byte-unchanged; no code file changed; `260918-qz5-PLAN.md` was not edited.
