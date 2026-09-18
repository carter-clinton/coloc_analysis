---
task: 260917-pff
branch: m3-W2-aou-deltas
date: 2026-09-17
docs_only: true
pushed: false
status: COMPLETE
---

# quick-260917-pff — SUMMARY

Banked the reviewer's 2026-09-17 CLOSURE of the Finding 2 review and the 260916 courier text
**as sent**, recorded the closure in §(10e), added Finding 1's scope sentence in his own accepted
formulation to §(10d), reconciled §(10e)'s now-false "Finding 1's text is unchanged", and corrected
both courier status headers in place under their existing filenames. Finding 2 is still
**NOT ESTABLISHED**; the disclosure is still **DRAFTED — NOT POSTED**. Nothing was posted, sent or
pushed; nobody was contacted.

Executed from PLAN **rev 2** (md5 `14ee23902930e9ab7ed97c5160367308`, 1930 lines). Pre-flight ran at
HEAD `afd1a19` with a clean tracked tree; the PLAN pins the five input md5s, not HEAD.

## Commits

| commit | contents |
|---|---|
| `52d3586` (`52d3586b1ddf91ddc618be5efb6411be9aa0f4f2`) | the five deliverables (Task 2) |
| the commit that adds this file | the PLAN and this SUMMARY (Task 3) — a commit cannot state its own hash; it is the child of `52d3586` on `m3-W2-aou-deltas` |

## The five files, as committed (measured, `git show HEAD:<path> | md5sum`)

| path | md5 | size | lines |
|---|---|---|---|
| `.planning/osf_deviations.md` | `22e1b1db105dbacc56c5f8fb3ccc7298` | 89846 B | 1139 |
| `.planning/quick/260917-pff-…/260917-pff-SETH-CLOSURE-finding2-review-as-received.md` | `d2eb6a02afba146b97d06f185c8c9d96` | 4631 B | 47 |
| `.planning/quick/260917-pff-…/260917-pff-260916-COURIER-AS-SENT-measurement-result.md` | `be9211e8caa55f921b3b90c7b7c23f0b` | 6398 B | 102 |
| `.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md` | `f2251f195382f89f6b0305594c48a300` | 7021 B | 106 |
| `.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md` | `764c3d2af5cbb53191699dea7f213d2a` | 6195 B | 90 |

Input pins re-measured at pre-flight and unchanged at install time: osf
`6ba5ad5365b64a2482eafea75168b8ae` (88393 B, 1124 lines), c16 `c068559c298a026e19eaabf9d0566c4d`
(5614 B, 91 lines), c17 `a92d9ec21ebb26b39ae8df99696b2abf` (5763 B, 86 lines), closure paste
`0b9793244d07f407e07c1e47baff994d` (3168 B, 25 lines), text-as-sent scratch
`502fe68481edeedcf42d53442af6b127` (4907 B, 77 lines). `$CLOSURE` mtime measured
**2026-09-17 18:18** — the fact the bank header states as the scratch write time.

The four embedded scripts were extracted from the PLAN and never retyped:
`pff_cites.py c5b1f7ff277b06e560530ec0ef09249f` (3561 B),
`pff_apply.py 6205baadd25f4968787f2b2004b0ccbb` (12209 B),
`pff_guard.py 986586410b0f91f851ce96b5c6ca502d` (36436 B),
`pff_negctl.py 939e28ab18f4d7d66b904d901d4e5c97` (21937 B).

## Sites, with the after-line ranges from the guard census (measured)

| id | file | census | gist |
|---|---|---|---|
| S1 | osf | `insert base 1078-1077 -> after 1078-1083` | §(10d) SCOPE OF FINDING 1 — his own accepted formulation: all 21 regions scanned, 21 of the 276-region manifest (§(9)), 7.6% of the panel, defined-but-degraded `r` survives the **posted** predicate, invisible to the retained NaN-raise by construction, plus the ⛔ disclaimer over the 255 unscanned regions and over any other predicate |
| S2 | osf | `replace base 1115-1115 -> after 1121-1127` | §(10e) INTERCHANGEABLE bullet: the stale "This entry does not record his acceptance of the scoping decided here." becomes the closure record |
| S3 | osf | `replace base 1122-1122 -> after 1134-1137` | §(10e) "Finding 1's text is unchanged." → "Finding 1's counts and its claim are unchanged", naming all three clauses S1 adds |
| S4 | c16 | `replace base 3-3 -> after 3-18` | SENT 2026-09-17 in the CORRECTED form, qualifier inside the status sentence, DRAFT OF RECORD, mismatch source UNATTRIBUTED, filename kept |
| S5 | c17 | `replace base 3-3 -> after 3-7` | SENT 2026-09-17, the closure named as its reply, filename kept |
| BANK | new | 47 lines | closure as received: provenance header (both time facts, NOT BYTE-VERIFIED, scratch md5/size/lines) + the paste byte-for-byte in a 4-backtick fence |
| SENTBANK | new | 102 lines | the courier text AS SENT: provenance header (Carter's decision, draft of record named, superseded figures removed, NOT BYTE-VERIFIED, scratch md5/size/lines) + those bytes in a 4-backtick fence |

## Guard

`pff_guard.py` on the real paths, base blobs read from `git show HEAD:…` →
**`RESULT GREEN  396/396 PASS`**, exit 0, 396 check lines over **126 distinct ids**, 0 FAIL. The
real-tree output is byte-identical to the scratch-build output (`diff` rc=0), whose five build md5s
equalled the five pins before any repo write.

RED sanity run, base files passed as both base and after → exit 1, **`RESULT RED  333/383 PASS`**,
50 FAIL lines over **29 distinct FAIL ids**:

`G01-c16-newheader, G04-census-c16-nonempty, G04-census-c17-nonempty, G04-census-osf-nonempty,
G06-7.6-stated, G08-D2, G08-D2-bankref, G08-D2-block, G08-D2-no-new-stats, G08-D2-no-praise,
G08-D2-old-gone, G08-D2-sentences, G09-D3, G09-D3-10e-reconciled, G09-D3-predicate-nonvacuous,
G10-D4-c16, G10-D4-c16-committed-src, G10-D4-c16-new, G10-D4-c16-old, G10-D4-c16-pointer,
G10-D4-c16-qualifier, G10-D4-c16-unattributed, G10-D4-c17, G10-D4-c17-new, G10-D4-c17-old,
G10-D4-mismatch-anchor, G10-D4-mismatch-source, G10-D4-rest-byte-c16, G10-D4-rest-byte-c17`

— every id the PLAN required to appear is present. `G10-D4-c16-noattr` PASSes here, as the PLAN
states (the clause it forbids is absent from the base too); its falsifiability comes from control
N175.

### Enumerations, verbatim from `guard_real.txt`

**G01 (the five superseded literals, per file, normalized):**

```
    1.652   osf     base 0  after 0
    1.652   c16     base 1  after 1
    1.652   c17     base 0  after 0
    1.652   bank    count 0 (want 0)
    1.652   sent    count 0 (want 0)
    0.0366  osf     base 1  after 1
    0.0366  c16     base 2  after 2
    0.0366  c17     base 0  after 0
    0.0366  bank    count 0 (want 0)
    0.0366  sent    count 0 (want 0)
    1.564   osf     base 0  after 0
    1.564   c16     base 1  after 1
    1.564   c17     base 0  after 0
    1.564   bank    count 0 (want 0)
    1.564   sent    count 0 (want 0)
    0.0556  osf     base 1  after 1
    0.0556  c16     base 2  after 2
    0.0556  c17     base 0  after 0
    0.0556  bank    count 0 (want 0)
    0.0556  sent    count 0 (want 0)
    1.969   osf     base 2  after 2
    1.969   c16     base 2  after 2
    1.969   c17     base 0  after 0
    1.969   bank    count 0 (want 0)
    1.969   sent    count 0 (want 0)
```

No literal increases anywhere; both new bank files and the new c16 header carry none.
`G01-c16-warning` PASS — the 260916 file's own ⛔ warning naming all five survives byte-exact.

**G03 (framing phrases in the 2026-09-03 entry, AFTER; every count base == after):**

```
    straddl                      line 1029  uer-correction-log
    straddl                      line 1032  uer-correction-log
    straddl                      line 1102  (10e)
    straddl                      line 1103  (10e)
    straddl                      line 1114  (10e)
    coin                         line 1103  (10e)
    artifact of analytic choice  line 1105  (10e)
    interchangeab                line 1001  S7-scoped
    interchangeab                line 1103  (10e)
    interchangeab                line 1116  (10e)
    interchangeab                line 1119  (10e)
    equally defensible           line 1001  S7-scoped
    equally defensible           line 1103  (10e)
    equally defensible           line 1120  (10e)
```

**G05 (nothing new says or implies clustering EXPLAINS Finding 2):**

```
  enumeration G05-explain-osf (explain family in new osf text):
    -> 0 occurrence(s) in new osf text
  enumeration G05-explain-c16 (explain family in new c16 header):
    -> 0 occurrence(s) in new c16 header
  enumeration G05-explain-c17 (explain family in new c17 header):
    -> 0 occurrence(s) in new c17 header
  enumeration G05-explain-bankhead (explain family in bank provenance header):
    -> 0 occurrence(s) in bank provenance header
  enumeration G05-explain-senthead (explain family in AS-SENT provenance header):
    -> 0 occurrence(s) in AS-SENT provenance header
  enumeration G05-bank-fence: explain-family in bank total 1, inside the verbatim fence 1
  enumeration G05-sent-fence: explain-family in the AS-SENT bank total 3, inside the verbatim fence 3
  enumeration G05-positive ('clustering explains' surface forms, with context):
    c16   ...a demonstration. the disclosure does not say [clustering explains]  NEGATED in context
    sent  ...a demonstration. the disclosure does not say [clustering explains]  NEGATED in context
```

**G09 ('predicate' in the new osf text — three occurrences, all SCOPED):**

```
    block@1078  ...egraded r survives the posted predicate and is invisible to the retained na  SCOPED
    block@1078  ...canned, and nothing about any predicate other than the posted one.  SCOPED
    block@1134  ...1 scanned regions, the posted predicate, and the retained nan-raise — and c  SCOPED
```

Finding 1's counts are byte-frozen: `G09-D3-counts-byte` PASS (lines :1073-1077 byte-identical) and
`G09-D3-counts-text` PASS on all four figures — `2560 pre / 534 post of 3094 (17.26%)`,
`2047 pre / 474 post of 2521 (18.80%)`, `21/21 regions carry tail rows`, `0 regions have zero post`.
`G06-7.6-stated` PASS: 21/276 = 7.61% is stated to one decimal as **7.6%** exactly once, with 7.61%
and 7.7% absent. `G09-D3-banned` PASS — "universal" and "no geometric predicate" remain at 0/0.

**G12 (citation re-resolution):**

```
  citation re-resolution: 212 rows; 201 stable (end <= 1077); 4 MOVED; 7 out of range
    MOVED  .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1090-1090 -> :1096-1096
    MOVED  .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1090-1090 -> :1096-1096
    MOVED  .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1101-1107 -> :1107-1113
    MOVED  .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1101-1107 -> :1107-1113
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1129-1139
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1144-1146
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1148-1148
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1149-1154
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-SUMMARY.md L502   :1278-1279
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-vqp-refresh-stale-records-after-the-2026-09-/260916-vqp-VERIFICATION.md L312   :2030-2030
    OUT-OF-RANGE (not an osf line) .planning/quick/260916-vqp-refresh-stale-records-after-the-2026-09-/260916-vqp-VERIFICATION.md L312   :2030-2030
```

All 11 out-of-range/moved rows come from `260916-kht-SUMMARY.md:502` (9) and
`260916-vqp-VERIFICATION.md:312` (2); none is a live record, and `G11-head1077` PASS proves lines
1-1077 byte-identical, so all 201 stable citations re-resolve to identical bytes.

`pff_cites.py`, run once before any repo write: `PASS-A 212 rows, 150 files, max-end 2030, digest
5d8e9e715223a3095faa0858c09a8273` and `PASS-B 37 rows, 2 files, digest
2f74b0de3f1abae9aa67643d8f9781cb` — both pins matched, and that one JSON fed every guard run.
It was **not** re-run after the Task 3 commit (the PLAN and this SUMMARY legitimately add citations).

**G13:** all 37 bare rows printed with their base → after mapping; `G13-bare-scope` and
`G13-bare-nonvacuous` PASS (every bare reference is inside a `quick-260917-irg` record, and every
one of them moves).

## Negative controls

```
POSITIVE CONTROL (unmutated): 396 checks, FAIL ids = [] -> GREEN
COVERAGE: 126/126 check ids observed RED by at least one control
NEGCTL RESULT: ALL CONTROLS OBSERVED RED, ALL IDS COVERED
```

**113** controls ended in `  OK` (`grep -c '  OK$'` = 113), with **0** `INVALID CONTROL` and **0**
`MISSING` lines; exit 0. No id is labelled UNFALSIFIABLE.

## Neighbouring enforcers — BEFORE == AFTER

| enforcer | BEFORE (last lines) | AFTER (last lines) | diff of line-normalized multiset |
|---|---|---|---|
| `uer guard.py` | `38/40 PASS`, `uer exit=1` | `38/40 PASS`, `uer exit=1` | empty, rc=0 (40 / 40 lines) |
| `vqq --live` | `RESULT RED checks=446 parsed=112 table=112 verified=102 c-res=112`, `vqq exit=1` | identical, `vqq exit=1` | empty, rc=0 (437 / 437 lines) |
| `u9p ledger` | `RESULT: ALL CHECKS PASSED (section: ledger)`, `u9p exit=0` | identical, `u9p exit=0` | empty, rc=0 (9 / 9 lines) |

`reds=[…]` byte-equal before and after, and equal to the PLAN's 10-element list:

```
BEFORE  reds=['c:c01', 'c:c02', 'c:c03', 'c:c04', 'c:c18', 'c:c62', 'c:c63', 'c:n02', 'c:n48', 'c:n06']
AFTER   reds=['c:c01', 'c:c02', 'c:c03', 'c:c04', 'c:c18', 'c:c62', 'c:c63', 'c:n02', 'c:n48', 'c:n06']
```

All three were run without `set -e` and without `|| true`, so the exit codes are the measured ones.

## The irg guard — RED on exactly the five checks that are supposed to be RED

Re-extracted from the closed `quick-260917-irg` PLAN (all three md5 markers matched:
`irg_apply.py c2db4d804b10dffb1bac567f95450285`, `irg_guard.py 566ce551c9f4076e7c3495968947d14d`,
`irg_negctl.py 584d4df53807fe5618ba14d1e38b1fa3`), base blob `9bdcd7d^:.planning/osf_deviations.md`
md5 `714454a5b23d979396f1d8c6fc1104d4`, scratch inputs present → exit 1,
**`RESULT RED  119/124 PASS`**, 124 check lines, **5** FAIL lines, one per id:

| irg check | why it is an expected consequence |
|---|---|
| `G05-osf` | irg's numeric allowlist does not know 276 / 7.6 / 255 (D3) |
| `G06-W1` | its W1 sentence is the stale one D2 replaces |
| `G07-finding1-10d` | §(10d) is no longer byte-identical — D3 adds the scope bullet |
| `G10-courier-status` | the 260917 courier status line is no longer `DRAFTED … NOT SENT` (D4) |
| `G12-census` | the new hunks are outside irg's allowed sites |

Exact-set check: no extra id, no missing id.

## Path scope

`comm -23 before after` printed nothing (nothing vanished, count 0). `comm -13 before after` printed
**exactly** these five lines:

```
 M .planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md
 M .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
 M .planning/osf_deviations.md
?? .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md
?? .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md
```

`git status --porcelain --` over `.planning/amendments`, `STATE.md`, `HANDOFF.json`, `DECISIONS.md`,
the `260917-irg` quick dir, `src` and `tests` → **0** lines.

**RED control, observed:** `touch src/python/__pff_negctl_probe.py` → `comm -13` showed a **6th**
line `?? src/python/__pff_negctl_probe.py` and the frozen-tree count went to **1** (RED). After
`rm -- src/python/__pff_negctl_probe.py`: back to exactly the five lines, frozen-tree count **0**
(GREEN), the post-removal status file byte-identical to the pre-probe one, and
`find . -name '__pff_negctl_probe*'` → 0 hits. The probe left no trace.

Post-commit: `git show --name-only --format= HEAD | wc -l` = 5, the five committed blob md5s equal
the pins, and `git status --porcelain --untracked-files=no | wc -l` = 0.

## Bare line references that go stale BY DESIGN — NOT REWRITTEN (repo-path scope)

All 37 live inside the two closed `quick-260917-irg` plan-time records; they are observations, not
live pointers, and rewriting them is outside this task's five-path scope.

| base | after | where |
|---|---|---|
| 1086 | 1092 | irg PLAN L138 L236 L240 L241; irg SUMMARY L53 L67 L69 L70 L119 — the `(10e)` heading |
| 1096 | 1102 | irg PLAN L234; irg SUMMARY L94 |
| 1097 | 1103 | irg PLAN L234 L235; irg SUMMARY L95 L97 L100 L104 |
| 1099 | 1105 | irg PLAN L234; irg SUMMARY L98 |
| 1108 | 1114 | irg PLAN L234; irg SUMMARY L96 |
| 1110 | 1116 | irg PLAN L235; irg SUMMARY L101 |
| 1113 | 1119 | irg PLAN L235; irg SUMMARY L102 |
| 1114 | 1120 | irg PLAN L235; irg SUMMARY L105 |
| 1124 | 1139 | irg PLAN L49 L121 L232; irg SUMMARY L35 L71 — a LINE COUNT, not a citation |
| 1125 | 1140 | irg PLAN L138 L240; irg SUMMARY L67 L69 — the `split()` trailing-element artifact |

## Provenance of two decisions

- **S3 was not one of D1-D4.** It began as a planner-found internal contradiction — S1 makes
  §(10e)'s "Finding 1's text is unchanged." false on the same date — and was **APPROVED by Carter on
  2026-09-17**; it is reconciled in place rather than left false.
- **D5 (banking the courier text as sent) was Carter's addition on 2026-09-17**, on the same day.

## KNOWN AND DELIBERATELY NOT ACTED ON (reported for Carter, not fixed)

1. **Both filenames still read `UNSENT`** although both were sent. Kept by Carter's decision because
   other records cite those paths; both files now say so in their own headers, and the 260916 one
   points at the AS-SENT bank.
2. **The 37 irg bare line references go stale** (table above). Not rewritten: repo-path scope.
3. **The 260916 courier still carries the superseded figures in its body** and its own ⛔ warning
   naming all five. Both are frozen by D4; S4 points at the warning without restating any figure,
   and the AS-SENT bank contains none of them.
4. **Neither banked correspondence file is byte-verified.** The closure came from a chat paste; the
   text as sent is a session **scratch** copy, not a capture of the reviewer's channel. Both headers
   say so in those words.
5. **The closure's first line opens "Seth —".** Banked verbatim, not interpreted.
6. **The source of the reviewer's "a 0.02 mismatch" figure is UNATTRIBUTED.** Re-verified at
   pre-flight: `$C16`'s only commit is `c93e97b 09-16 14:31` (blob md5 there equals the base pin),
   that blob states `0.02 mismatch` once, and the disclosure at that commit carried the superseded
   value the figure is computed against twice (measured; the literal is not restated here) —
   so the figure was reachable from two files committed **before** his 2026-09-17 reply, while the
   text as sent stated no figure for it. Which one he read is not establishable from this record, so
   S4 records it as unattributed rather than guessing. Nothing in the repo could settle it, and
   asking him is a contact action no agent takes.

## Disposition and scope

- Finding 2: **NOT ESTABLISHED** (unchanged). `G02-disposition` PASS on all six word-for-word
  disposition sentences; `G02-status-line` PASS byte-exact; the "DRAFTED — NOT POSTED" and
  "NOT ESTABLISHED" counts do not fall in the ledger or in either courier, and the text as sent
  still carries "DRAFTED — NOT POSTED" inside its fence (`G02-sent-drafted` PASS).
- Nothing was posted, sent, pushed or transmitted. No OSF, reviewer, cloud or network action was
  taken in any task.
- STATE.md / HANDOFF.json / DECISIONS.md not written — orchestrator close-out.
