---
phase: quick-260818-uoi
plan: 01
subsystem: planning-records
tags: [records, deferred-items, runbook, seth-courier, maf-depression, D-11, fire-prep]
requires:
  - "quick-260818-sml (the D-01..D-13 adjudication courier Seth is replying to)"
  - "Seth's 2026-08-18 acceptance courier (banked as-received, no byte anchors supplied)"
provides:
  - "MISS-1 — the registered POST-FIRE within-panel missingness test that replaces the cross-cohort MAF join"
  - "D-11 concurrence on the record (region-1 severity stays FINDING), with an explicit no-code-changed statement"
  - "Two runbook Stage-B notes retargeted from a retired work item to MISS-1"
affects:
  - ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
  - ".planning/quick/260812-ox1-.../260812-ox1-AGENT-PROMPT.md"
  - ".planning/quick/260812-ox1-.../260812-ox1-BROWSER-PASTE.md"
  - ".planning/HANDOFF.json (gates.producer_pre_fire_gates only)"
tech-stack:
  added: []
  patterns:
    - "append below a ^## heading so a heading-delimited extractor terminates at the new boundary rather than absorbing the append"
    - "an enforcer pass criterion of EMPTY OUTPUT DIFF, not exit 0, when the baseline is already red"
    - "every green guard paired with an OBSERVED red negative control before it counts as evidence"
key-files:
  created:
    - ".planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md"
    - ".planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SUMMARY.md"
  modified:
    - ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
    - ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
    - ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md"
    - ".planning/HANDOFF.json"
decisions:
  - "The cross-cohort (panel_maf, sumstats_maf) join is NOT to be built — it is nobody's work item, not a scheduling deferral."
  - "The replacement is a within-panel, post-fire F_MISS test registered as MISS-1; severity FINDING, never a hard stop."
  - "No --missing added to the producer: new behaviour on the $385-1,084 fire path to buy a post-fire diagnostic is refused under the freeze-economy rule."
  - "D-11 accepted as a concurrence with zero code edited anywhere."
  - "The optional HANDOFF.json clause was TAKEN (all guards clean, byte round-trip preserved)."
metrics:
  tasks: 2
  commits: 2
  files_changed: 6
  completed: 2026-08-18
---

# Quick 260818-uoi: Bank Seth's D-Acceptance Courier, Register MISS-1 Summary

Seth's 2026-08-18 acceptance courier is banked in-repo; the MAF-depression
follow-up is redirected from an unbuildable cross-cohort join to a registered
within-panel missingness test (`MISS-1`), and the two runbooks that described the
join as pending work now point a fire-time agent at the item id instead. Zero
code changed.

## What Seth Accepted

**All thirteen adjudications from `quick-260818-sml`, zero contested.** He did
not take them on report: he **reloaded his own prototype and re-ran the failures
himself**, reproducing three broken checks — **3 of his 9 checks**:

| His check | Defect he reproduced | Why it mattered |
|---|---|---|
| **D-02** | `classify_deferrals` matched bare tokens while the producer emits **detail-in-status** by design (`:831`, `:854`) | Every real deferral (~29+) would have HARD_STOPped a healthy $385-1,084 fire **on the gates working**, at every Stage-C check-in |
| **D-02b** | The same function returned **PASS** on `skipped_idempotent`, `verify_failed`, `error: boom` | The quiet hole. `skipped_idempotent` fires for every resumed region after any Spot recycle; `verify_failed` never uploads and `error:` banked nothing. His own verdict: "a quiet hole in a gate is the worse defect" |
| **D-09** | `estimate_markers` went **FAIL on innocent CORRECT prose** ("...estimated from Stage B then MEASURED at rollup") | A gate that reddens on correct text gets switched off — a future reason to disable the check. Two of his four markers did not occur in the file at all |

His framing of the trade: *"Three of nine checks broken, found by measurement,
before the fire rather than during it."*

## D-11 CONCURRENCE — NO CODE CHANGED

Seth asked for **no change**: region-1 severity **stays `FINDING`**. His grounds
— the runbook wording already frames it as the finding, `exit_code` is non-zero
either way, and nothing operational rides on the tier.

**This task edited no file under `src/`, `tests/`, `config/`, and no Snakefile.**
Measured, not asserted:

```
$ git diff --stat HEAD~2 HEAD -- src/ tests/ config/ '*.smk' Snakefile workflow/
(empty)
```

There is no commit to go looking for. The concurrence lives in the `MISS-1` item
body and here.

## The Redirect

**Decision: the cross-cohort `(panel_maf, sumstats_maf)` join is NOT to be
built.** Not deferred — it is nobody's work item.

**One-line rationale:** the mechanism predicts **callability, not MAF**, so the
within-panel test is a direct measurement while the cross-cohort ratio is a
confounded proxy. Seth's reasoning as preserved in the item: the GWAS AFR cohort
is not the AoU AFR cohort; region 1's ratio 0.0078 / 0.014 = 0.557 is the
predicted direction, but ordinary between-cohort AF differences at MAF ~ 0.01 are
easily that large on their own — so a red would be ambiguous, and **an ambiguous
gate is one people learn to ignore**.

**Registered replacement: `MISS-1`** in
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` — per region,
compare `F_MISS` of the occlusion-excluded variants against that region's own
`F_MISS` distribution (rank-based, or the fraction above the region's 90th
percentile). Elevated implies mechanism-consistent; not elevated is a genuine
FINDING and a cleaner one, because there is no second cohort to blame.
Single-cohort and egress-safe (aggregate per-variant rates only).

**Two runbook sites retargeted** (both now name `MISS-1` literally, so a browser
agent can grep it):

| File | Site | Was | Now |
|---|---|---|---|
| `260812-ox1-AGENT-PROMPT.md` | STEP 9-GATE A-12 note (lines 271-277 at HEAD) | "building it is Carter's planning-side work, not yours" | "NOT TO BE BUILT... the registered replacement is MISS-1" |
| `260812-ox1-BROWSER-PASTE.md` | §9b Stage-B gate block (lines 371-377 at HEAD) | "Producing it is Carter's planning-side work, not the agent's" | "NOT TO BE BUILT... the registered replacement is `MISS-1`" |

Seth's **two cross-cohort constraints** ((CHR,POS)-only key with the GRCh38/37
lift-over in the key; `MAF = min(EAF, 1-EAF)` never raw EAF) survive **VERBATIM**
inside `MISS-1`, so a future implementer cannot reconstruct them from a
paraphrase.

## Measured Premises — and What Is Seth's, Not Ours

Re-verified at execution time against HEAD, not copied from the plan:

| Premise | Measurement | Verdict |
|---|---|---|
| `.lmiss` is not emitted by the fire | recursive search of `src/` for `lmiss` and the `--missing` flag returns **0 hits**; `aou_ld_panel.build_plink_ld_command` builds the square argv as `--r square bin4` + `--keep-allele-order` + `--mac 1 --nonfounders --write-snplist` over `--chr/--from-bp/--to-bp` | **TRUE (ours)** |
| `check_maf_depression` implemented but unwired | `src/python/fire_verifier.py:632`, `⚠ A-12: IMPLEMENTED BUT NOT WIRED` docstring at `:640`, tests at `tests/m3/test_fire_verifier.py:641+` | **TRUE (ours)** |
| the bfile + VM persist post-fire | `HANDOFF.json.cluster` = "STOPPED, not deleted — preserved for the fire"; runbooks say **STOP** (`AGENT-PROMPT:279`, `BROWSER-PASTE:301`); teardown is UI-only and no STEP C-G step deletes the env | **CONSISTENT, NOT GUARANTEED** — nothing *commits* to preserving it after STEP G, and a STANDARD-disk AoU env loses its disk on delete. Fallback if deleted: a **bfile rebuild**, NOT an LD re-fire. Stated conditionally in `MISS-1`. |
| region-1 2x2, `fAmB` = 1.0 in 5 of 6 pairs | the token `fAmB` occurs in this repo **only** in Seth's banked courier and in this task's own planning documents that quote him — no result file, no log, no table | **SETH'S CLAIM — NOT INDEPENDENTLY RECORDED AS OURS.** Attributed as his throughout; never asserted as our measurement. |

## Guard Transcript

Every green below is paired with its observed red. A green without an observed
red is not in this section.

**Before/after enforcer output diffs — all EMPTY:**

| Enforcer | Baseline | After | Diff |
|---|---|---|---|
| `260817-vbu-verify.sh all` | 20 PASS / 0 FAIL, exit 0 | 20 PASS / 0 FAIL, exit 0 | **EMPTY** |
| `260814-guk-verify.sh record` | R1,R2 PASS; **R3,R4 FAIL (pre-existing)**; R5-R8 PASS | identical | **EMPTY** |
| `260814-guk-verify.sh all` | 23 PASS / 5 FAIL (pre-existing) | 23 PASS / 5 FAIL | **EMPTY** |

The criterion was **empty output diff, never exit 0** — `guk record` is already
red at HEAD over `HANDOFF.json.status` (R3) and `resume_on_reconnect[0]` (R4).
Those reds were left exactly as found; "fixing" them was out of scope.

**Append-only and the live R4 gate input:**

```
git diff --numstat -- deferred-items.md   ->   153  0   (deletions == 0)
G2 OK  R4 block preserved: 2776 -> 2777 B, 41 non-empty lines, md5(rstrip) 355164f44503c2aaad8d97bf9adde305
R4 terminator: '## MISS-1 — the MAF-'   (was EOF; now terminates at the new heading, as designed)
R4 heading count: 1     MISS-1 sections: 1
byte-prefix assertion: the 68,856 existing bytes are unchanged byte-for-byte
```

**Pinned trsx5 card blocks — md5 equality vs `git show HEAD:`:**

```
OK  card block unchanged: 260812-ox1-AGENT-PROMPT.md   md5=4d30ed481efc5fce07d33d52c70bbe35
OK  card block unchanged: 260812-ox1-BROWSER-PASTE.md  md5=867b9dd0994ece5d8fa019981b43ac2c
```

Both edits landed in a single hunk each — `@@ -274,4 +274,18 @@` and
`@@ -374,4 +374,18 @@` — far outside the pinned ranges 106-163 / 107-179. No
new 20+ char hex run was introduced (whole-file counts HEAD=5 / worktree=5 on
both files, and 0 on added lines).

### NEGATIVE CONTROL 1 — the `# ` banner hazard (guards G2)

Counterfactual: follow the file's *older* section convention and open the append
with a `# Deferred items — discovered during ... execution (date)` banner. Run in
the scratchpad against a copy; the repo file was never touched.

```
NEGATIVE CONTROL OBSERVED RED (this is the required outcome):
  AssertionError: R4 BLOCK CONTENT CHANGED — the append leaked into the gate input
  R4 block size under the counterfactual: 2776 B -> 2857 B
  R4 non-empty lines: 41 -> 42
  absorbed tail: '\n# Deferred items — discovered during quick-260818-uoi execution (2026-08-18)\n\n'
```

The hazard is real, not theoretical: `_SECTION_HEADING` matches `^## ` and not
`^# `, so the banner is swallowed **into** the block `fire_verifier` parses. G2
detects it. This is why the appended section opens directly with `## MISS-1`.

### NEGATIVE CONTROL 2 — the pinned card-block guard

**First attempt was degenerate and is recorded as such.** Deleting the first
long line in range 106-163 removed the `STEP 6b` **anchor** itself, so the
extractor returned nothing and the guard compared the empty string:

```
  tampered md5=d41d8cd98f00b204e9800998ecf8427e   HEAD md5=4d30ed481efc5fce07d33d52c70bbe35
```

`d41d8cd9...` is the md5 of the empty string — a red that proves only "anchor
missing", not "content changed". Re-run with a victim **strictly inside** the
card, anchor intact:

```
deleting line 130 (strictly inside the card, anchor preserved):
  extracted block lines: tampered=57  HEAD=58  (non-empty => guard compared real content)
FAIL card block MOVED: <scratchpad>/AGENT-PROMPT.NEGCTRL2.md
  tampered md5=3a16e2f422448e527925228232f1f9ab   HEAD md5=4d30ed481efc5fce07d33d52c70bbe35
NEGATIVE CONTROL OBSERVED RED (non-degenerate: both blocks non-empty)
```

Line 130 was a **blank** line — the guard catches even a whitespace-only change
inside the pinned card.

## HANDOFF.json — Optional Clause TAKEN

Steps 1-4 were entirely clean, so the optional clause was applied.

- Only `gates.producer_pre_fire_gates` changed — `git diff --numstat` shows
  **1 insertion / 1 deletion**, a single string line.
- The three enforcer-pinned keys were asserted unchanged in the same
  transaction: `status` (guk R3), `resume_on_reconnect[0]` (guk R4, md5-pinned),
  `gates.trsx5_posted_body` (guk R2, PASS).
- Pre-edit gate: refused to write unless `json.dumps(d, indent=2,
  ensure_ascii=False)` already reproduced the file byte-identically. It did.
- Post-edit: valid JSON, 40 top-level keys, round-trip byte-identical, **no
  trailing newline**, 75,604 -> 75,969 B; `guk record` output still byte-identical.

## Not Done / Declined

- **No `--missing` added to the producer.** Doing so would put new behaviour on
  the $385-1,084 fire path to buy a post-fire diagnostic. Refused under the
  freeze-economy rule (an open window is a process saving, never a safety
  argument). The `.lmiss` computation is deferred to a cheap VM session.
- **No note added to `260812-ox1-READY-TO-FIRE.md`.** Measured 2026-08-18: it
  carries **zero** hits for the MAF note (searched `MAF`, `improvise`,
  `depression`, `panel_maf`). Adding new content to a third runbook on a frozen
  fire path would be scope creep, so the measured absence is recorded instead.
- **`check_maf_depression` was NOT wired.** It stays implemented, tested, and
  deliberately unwired. `MISS-1` states explicitly that it does not authorise
  wiring it.
- **R3/R4 of `guk record` were NOT fixed.** Pre-existing drift, out of scope.
- **Not pushed.** The push and the STATE.md quick-task row are the
  orchestrator's.

## Deviations from Plan

**1. [Orchestrator directive] SUMMARY left uncommitted**

- **Plan said:** Task 2 step 7 stages `260818-uoi-SUMMARY.md` in the commit.
- **Executed:** the SUMMARY is written but **left uncommitted**, per the
  orchestrator's explicit constraint ("Create summary at ... (leave
  uncommitted)"). The commit therefore carries the two runbooks, the banked
  courier, the PLAN, and `HANDOFF.json`.
- **Effect on guards:** none. No enforcer reads the SUMMARY.

**2. [Rule 1 - method correction] Negative control 2 was strengthened after a
degenerate first result**

- **Found during:** Task 2, step 4's negative control.
- **Issue:** the first tampering deleted the `STEP 6b` anchor line, so the guard
  compared empty strings — a red that did not demonstrate content sensitivity.
- **Fix:** re-ran with a victim strictly inside the card block. Both the
  degenerate and the valid run are recorded above rather than only the passing
  one.
- **Files modified:** none in the repo (scratchpad only).

No architectural changes. No authentication gates. No perimeter contact, no
network, no `gsutil`/`gcloud`/`bq`/`wb`, no fire.

## Commits

| Task | Commit | Message |
|---|---|---|
| 1 | `89a7cb8` | `docs(quick-260818-uoi): register MISS-1 — MAF-depression follow-up redirected to a within-panel missingness test; D-11 concurrence recorded` |
| 2 | `3338ae7` | `docs(quick-260818-uoi): retarget the Stage-B MAF note to MISS-1; bank Seth's D-01..D-13 acceptance courier` |

Not pushed — the push is the orchestrator's.

## Self-Check: PASSED

- All 6 claimed created/modified files exist on disk.
- Both claimed commits (`89a7cb8`, `3338ae7`) resolve in `git log`.
- `deferred-items.md` is 1,350 lines (must_haves min 1,240); exactly one
  `## MISS-1`; the courier path is cited in the item body and again in its
  cross-references.
- Seth's two constraints each appear exactly once, verbatim.
- Forbidden strings: 0 in the SUMMARY, 0 across all three runbooks, and the
  `deferred-items.md` R8 pairing holds at nret == nretired == 1.
- The only untracked file left in the task directory is this SUMMARY, left
  uncommitted per the orchestrator's instruction.
