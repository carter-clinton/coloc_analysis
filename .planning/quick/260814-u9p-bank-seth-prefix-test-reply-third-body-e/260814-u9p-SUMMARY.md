---
phase: quick-260814-u9p
plan: 01
subsystem: record-integrity / osf-disclosure / fire-gate-invariants
tags: [trsx5, osf-ledger, hex-invariant, sha256, courier-in, falsification, fire-held]

requires:
  - "50dc51d (ledger ADJUDICATED sub-entry — the append-only pin)"
  - "260814-guk-verify.sh (_hexlen sub-mode + fire section)"
  - "260814-u9p-SETH-REPLY-VERBATIM.md (courier-in, orchestrator-authored)"
provides:
  - "hex-run invariant accepting {32, 64} with observed negative controls"
  - "260814-u9p-verify.sh {controls|ledger|reply|all} — 22 checks"
  - "RECHARACTERIZED 2026-08-14 ledger sub-entry (pure append)"
  - "260814-u9p-REPLY-TO-SETH.md (courier-out, asks for the 9,907-B re-send)"
affects:
  - ".planning/osf_deviations.md (public-facing OSF disclosure record)"
  - "the trsx5 fire gate (unregressed, still 10/10)"

tech-stack:
  added: []
  patterns:
    - "loosening a safety invariant requires seeing what it still rejects (31/63 RED) AND what it used to reject (pre-edit 64 RED)"
    - "controls drive the SHIPPED code path (_hexlen sub-mode), never a re-implementation"
    - "structural anti-revert guard (C6) reads the shipped function's own length condition"
    - "append-only enforced by a gate (L1, numstat deletions == 0), not by intent"
    - "byte-exact courier-in pinned in the worktree AND re-derived from the git object store"

key-files:
  created:
    - ".planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-verify.sh"
    - ".planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-REPLY-TO-SETH.md"
  modified:
    - ".planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh"
    - ".planning/osf_deviations.md"
  committed-as-is:
    - ".planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-SETH-REPLY-VERBATIM.md"

decisions:
  - "Widen hexlen_bad() to {32, 64} rather than exempt sha256 case-by-case — a 64-char sha256 anchor is legitimate and the old rule pressured the FORBIDDEN repair (truncate to 32)."
  - "P6's guk-era inline allow-list ({32, 40} + the labelled 31-char exemption) left deliberately untouched — it is a statement about one fixed document, not a general length rule."
  - "The ledger recharacterization is a PURE APPEND: the falsified reading stays verbatim, dated and superseded rather than rewritten."
  - "X1 (the display-truncated sha256) is kept OUT of the public ledger entirely and appears in the reply exactly once, with its ellipsis and a truncation warning on the same line."
  - "The reply forbids ANY 64-char hex run in itself (V6) even though V5 would permit a real one — we hold no legitimate sha256 to transcribe, so a 64-char run there could only be invented or padded."

metrics:
  duration: "~20 min"
  tasks: 3
  files: 5
  checks: "22/22 PASS (controls 6, ledger 8, reply 8) + guk fire 10/10"
  completed: 2026-08-14
---

# Quick 260814-u9p: Bank Seth's Prefix-Test Reply — Third Body, Invariant Widened Summary

Seth's ask-#1 prefix test came back **NO** against his own 9,907-byte lineage, so with our own
negative test both lineages are falsified as the posted body's source: the posted 9,695-byte
trsx5 body is an **unexplained third body**, the tgf reading is on the record as FALSIFIED
(original wording preserved), the hex-run invariant now accepts legitimate sha256 anchors with
its negative controls paid for, and the never-arrived 9,907-byte courier has been formally
re-requested. Fire and obligation-(2) remain HELD. `$0`, zero perimeter contact, nothing fired.

## Commits

| Task | Commit    | What                                                                        |
| ---- | --------- | --------------------------------------------------------------------------- |
| 1    | `3483a26` | Widen hex-run invariant to {32, 64}; new `260814-u9p-verify.sh`; fire 10/10  |
| 2    | `40acbd9` | RECHARACTERIZED 2026-08-14 ledger sub-entry (pure append, 90/0)             |
| 3    | `dd91a5f` | Courier-in banked byte-exact + `260814-u9p-REPLY-TO-SETH.md`                 |

Nothing pushed. `git rev-list --count origin/m3-W2-aou-deltas..HEAD` = **3**.

## Task 1 — the widening, and the evidence that it is real

### Pre-edit RED transcript (the load-bearing one)

Captured against the **unmodified** `260814-guk-verify.sh`, through its shipped `_hexlen`
sub-mode, before a single character of the widening was written:

```
$ bash .planning/quick/260814-guk-seth-update-2-reply-remediation-fix-inva/260814-guk-verify.sh _hexlen "$CTL/len64.txt"
FAIL  _hexlen(.../len64.txt): hex run(s) present that are not 32 chars:
  len=64  deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
EXIT=1
```

This is what makes the widening non-cosmetic: Seth's claim that the invariant *would have
rejected a legitimate sha256 anchor* is not taken on trust, it is observed. It is also why the
64 GREEN below is evidence rather than an assertion.

Control premise was self-checked rather than hand-counted (`${#s}` against the declared
length for all four strings) — a wrong-length control would have made every result meaningless.

### Post-edit control results

| Control                                    | Length | Expected | Observed  |
| ------------------------------------------ | ------ | -------- | --------- |
| the historical 31-char defect literal      | 31     | RED      | **RED**   |
| synthetic run one char short of a sha256   | 63     | RED      | **RED**   |
| a real md5 (`28ecdb31…`, H5)               | 32     | GREEN    | **GREEN** |
| synthetic sha256-length run                | 64     | GREEN    | **GREEN** |

Raw, all four through the shipped `_hexlen`:

```
--- len31 ---  FAIL  ... hex run(s) present that are neither 32 (md5) nor 64 (sha256):
                 len=31  c19e8b2ad7cd6a45fee1d668d8a9cf9            exit=1
--- len63 ---  FAIL  ... len=63  deadbeef…deadbee                    exit=1
--- len32 ---  PASS  ... every hex run >=20 chars is 32 (md5) or 64 (sha256)   exit=0
--- len64 ---  PASS  ... every hex run >=20 chars is 32 (md5) or 64 (sha256)   exit=0
```

### The edit

- `hexlen_bad()`: `if (length($0) != 32 && length($0) != 64)`. Nothing else in the function.
- Two now-false message strings corrected (`_hexlen` PASS, F1 PASS/FAIL) so the script does not
  ship a statement it has made untrue.
- Dated CHANGELOG block in the header recording the widening, the **FORBIDDEN repair**
  (truncating a sha256 to 32 chars manufactures the exact silent-mismatch class the invariant
  exists to catch), and the deliberate non-change to `P6`.
- Diff was 36 insertions / 6 deletions — the widening is one condition, the rest is the record.

### Fire gate, after the widening

```
--- section: fire -------------------------------------------------
PASS  F1  every hex run >=20 chars inside all three card blocks is 32 (md5) or 64 (sha256) (generic invariant)
PASS  F2  all three card blocks carry 28ecdb31 / 425d925a / c19be8b2
PASS  F3  every advisory-hash line is attributed (Seth + unverified) within a 4-line window
PASS  F4  every card adjudicates SIZE-FIRST (9,758 precedes 28ecdb31 on an earlier line)
PASS  F5  the 31-char literal AND the bare prefix c19e8b2 are GONE from all three runbook files (0 / 0)
PASS  F6  anchor re-derived: 9758 / 28ecdb3160833da80cfa25952f76415b on the working tree AND at ac4c990
PASS  F7  READY-TO-FIRE order is 6 -> 6b -> 7 -> 8 -> 9 -> 10 -> 11 with NO renumbering
PASS  F8  both deferral-vocabulary blocks carry Seth's R3 ceilings (0.0005 / 60.0 / 51.2 / 102,421)
PASS  F9  cost-per-bankable-region appears in AGENT-PROMPT STEP 9, READY-TO-FIRE 11-C and BROWSER-PASTE's cost gate
PASS  F10 the retired framing ('nothing scientific is lost' / 'nothing is lost') appears 0 times in the runbooks

RESULT: ALL CHECKS PASSED (section: fire)
```

**10/10, unregressed**, both before and after the edit (pre-edit baseline was also captured, so
the "no regression" claim is a comparison rather than a hope).

### RED-before-GREEN for Tasks 2 and 3

Written in the Task 1 commit and observed failing at that commit:

```
ledger: FAIL L2 no '### RECHARACTERIZED 2026-08-14' heading found
        FAIL L3 the RECHARACTERIZED block is only 0 non-blank lines (>= 25) — VACUOUS
reply:  FAIL V1 …SETH-REPLY-VERBATIM.md is not committed at HEAD
        FAIL V3 260814-u9p-REPLY-TO-SETH.md does not exist
```

## Task 2 — the ledger recharacterization

`git diff --numstat 50dc51d -- .planning/osf_deviations.md` → **`90  0`** — 90 insertions,
**0 deletions**. Pure append confirmed by the gate, not by intent.

The sub-entry records, in order: the STOP verdict **standing unchanged** (it adjudicated on
size alone, 9,695 ∉ {9,758, 9,907}); F-1 with Seth's own re-verification of `425d925a…` first
and `head -c 9695` → `a81c22d9…` ≠ `c19be8b2…`; F-2 (both prefix tests negative); F-3 (the
exhaustive sweep item by item — 9,600–9,919, 51 line boundaries, four whitespace
normalizations, single-line deletion, contiguous 1-25-line block deletion where *not one
candidate even produces a 9,695-byte body*, and the 9,912-byte draft region with its
`5fd58a5`/`0f3c68b` × `2026-07-10`/`2026-07-04` variants); the **dated FALSIFICATION** of our
own reading with the original wording preserved at `50dc51d`; what is now open; the decisive
artifact; the next step labelled **RECOMMENDATION ONLY, NOT A DECISION**; the vocabulary
retirement of "the truncated post"; and provenance attributing Seth's measurements to Seth as
**unreproduced by us**.

**Negative control on L1** (the load-bearing append-only check — a green nobody has seen fail
is not a result): one pre-existing line inside the ADJUDICATED block was deleted in the
worktree, `ledger` was re-run, and L1 went **RED** —

```
FAIL  L1  1 line(s) DELETED from .planning/osf_deviations.md vs 50dc51d — this entry must be a pure append
```

— then restored via `git checkout --`, verified **byte-identical** (md5 `dd380631…` before and
after), and L1 returned **GREEN**. L1 is therefore proven non-vacuous.

## Task 3 — courier-in banked byte-exact, reply written

**Byte-exactness of the courier-in, proven twice:**

| Where                       | md5                                | Bytes | Lines |
| --------------------------- | ---------------------------------- | ----- | ----- |
| worktree, **before** `git add` | `47a017bf8753b147f498dea97cc64338` | 5,763 | 62    |
| git object store at `HEAD`  | `47a017bf8753b147f498dea97cc64338` | 5,763 | 62    |

`git show --numstat dd91a5f` for that path → **`62  0`**, added as a new path. Not one
character was edited.

⚠ The verbatim record contains **two 24-character hex runs** (`40831cdebcc71de21cd536fa…`).
Those are **correct and must stay** — Seth's own display truncation, faithfully banked. No
hex-length invariant is run over that file, by design (stated in the commit message and in the
V2 comment), and nobody may "repair" them: a courier-in record that has been repaired is no
longer a courier-in record.

**The reply** (147 lines) opens by conceding the substantive point and adopting the framing
shift, then covers (a) the courier that **never arrived** — both the filename and the sha256
prefix grepped, zero hits for either — with the re-send request and the full-64-character-anchor
constraint; (b) the widening and its four controls plus the pre-edit RED; (c)
read-the-posted-body-first, labelled a recommendation; (d) what is held; (e) the falsification
and the two unexplained deltas.

Reply hex census: **7 md5 runs, ZERO 64-char runs**, one exempted 24-char truncation carrying
its ellipsis and warning on the same physical line. The 31-char defect literal appears **0**
times.

## Full verification

```
bash .../260814-u9p-verify.sh all   →  exit 0, 22/22 PASS (controls 6, ledger 8, reply 8)
bash .../260814-guk-verify.sh fire  →  exit 0, 10/10 ALL CHECKS PASSED
git diff --numstat 50dc51d -- .planning/osf_deviations.md  →  90  0   (0 deletions)
git log --oneline -3  →  dd91a5f, 40acbd9, 3483a26   (exactly three, one per task)
git status --porcelain <the five listed paths>  →  clean
no STATE.md / ROADMAP.md / 260812-ox1 path in any of the three commits
origin..HEAD = 3 commits, UNPUSHED
```

No temp or control files were committed — the scratch dir lived off-repo under `$TMPDIR` and is
removed by a `trap ... EXIT`.

## Deviations from Plan

None — plan executed exactly as written.

Two things worth flagging as additions rather than deviations, both inside the plan's own
latitude:

1. **L1 negative control** (not required by the plan). The project's baked lesson is that a
   green assertion needs a negative control, and L1 is the mitigation for T-u9p-01 (tampering
   with a reviewer-facing record). It had only ever been observed GREEN, so it was made to fail
   and then restored byte-identically.
2. **V1 strengthened** from the plan's `git diff --stat -- <path>` to `git diff HEAD --stat --
   <path>`, plus a direct worktree md5 comparison. The plan's form compares worktree to index;
   the stronger form compares worktree to HEAD, which is what "byte-exact as committed"
   actually means.

## Authentication Gates

None. No network call, no OSF contact, no perimeter contact, no push, nothing fired. `$0`.

## Known Stubs

None.

## What is still HELD (unchanged by this task)

- **The fire** — no AoU compute, VM never started, browser agent stood down at the Step 3 GATE.
- **Obligation-(2) posting** — same gate.
- **The STOP verdict** — adjudicated on size alone; recharacterized, not reversed.

## What Carter (never an agent) does next

1. Courier `260814-u9p-REPLY-TO-SETH.md` to Seth and get the **9,907-byte body re-sent** with
   its full 64-character sha256 attached.
2. Ship the **9,695-byte posted body** in both directions — base64 to Seth, and into the repo —
   size-first on arrival (9,695, then `c19be8b2…` only to confirm which body).
3. Formally decide (or decline) the read-the-posted-body-first sequencing, which is currently
   recorded as a recommendation only.

## Self-Check: PASSED

Every file and commit claimed above was verified to exist on disk / in the object store:

```
FOUND: 260814-u9p-verify.sh            (407 lines, min_lines 120)
FOUND: 260814-u9p-REPLY-TO-SETH.md     (147 lines, min_lines 60)
FOUND: 260814-u9p-SETH-REPLY-VERBATIM.md
FOUND: 260814-guk-verify.sh
FOUND: .planning/osf_deviations.md
FOUND: commit 3483a26   FOUND: commit 40acbd9   FOUND: commit dd91a5f
```

Artifact `contains` assertions: `.planning/osf_deviations.md` carries `UNEXPLAINED THIRD BODY`;
the courier-in carries `--- VERBATIM BODY BEGINS ---`. Key links: `260814-u9p-verify.sh`
references `_hexlen` (6 occurrences, all sub-mode invocations of the shipped guk path) and the
ledger carries `ADJUDICATED 2026-08-14` adjacent to the new sub-entry.

`260814-u9p-SUMMARY.md` and `260814-u9p-PLAN.md` are intentionally left **unstaged** — the
orchestrator owns the docs commit.
