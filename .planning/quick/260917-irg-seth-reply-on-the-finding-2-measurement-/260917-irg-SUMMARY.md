---
task: 260917-irg
branch: m3-W2-aou-deltas
date: 2026-09-17
docs_only: true
pushed: false
status: COMPLETE
---

# quick-260917-irg — reviewer-reply amendment to the 2026-09-03 tail disclosure (SUMMARY)

The 2026-09-03 DEFINED-ROW TAIL disclosure now states Finding 2's design-corrected result as
evidence rather than as a side of 0.05, at 10 exact-once sites; the reviewer's 2026-09-17 reply is
banked as received; our reply courier is banked UNSENT. The disposition is unchanged: Finding 2 is
**NOT ESTABLISHED**, and the entry is still **DRAFTED — NOT POSTED**. Nothing was posted or sent.

## Commits

| commit | contents |
|---|---|
| `9bdcd7d9a1946bb4340a29ad7f8a0aad331c5476` (`9bdcd7d`) | the three deliverables (Task 2) |

Base before this task: `d880170`. `git diff --name-only d880170 9bdcd7d`:

```
.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
.planning/osf_deviations.md
.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md
```

## Deliverables — md5 as measured on the worktree and on the committed blob

| path | md5 (worktree == `git show HEAD:`) | size | lines |
|---|---|---|---|
| `.planning/osf_deviations.md` | `6ba5ad5365b64a2482eafea75168b8ae` | 88393 B | 1124 |
| `.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md` | `9b4df61d9e2097b88e1ff523c1e6d27d` | 9400 B | 78 |
| `.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md` | `a92d9ec21ebb26b39ae8df99696b2abf` | 5763 B | 86 |

Base `.planning/osf_deviations.md` was `714454a5b23d979396f1d8c6fc1104d4`, 1057 lines, re-checked
immediately before the copy-install. All three files were built by the plan's embedded
`irg_apply.py` in scratch and installed by `cp`; no file was hand-edited.

Embedded scripts extracted from the PLAN, md5 as measured:
`irg_apply.py c2db4d804b10dffb1bac567f95450285` (20501 B),
`irg_guard.py 566ce551c9f4076e7c3495968947d14d` (23151 B),
`irg_negctl.py 584d4df53807fe5618ba14d1e38b1fa3` (9941 B).

## The ten sites, after-line ranges from the guard census

Census line as the guard printed it (byte-compared against the PLAN's quoted census — equal):

```
census: replace base 608-609 -> after 608-609; replace base 665-670 -> after 665-670; insert base 858-857 -> after 858-868; replace base 878-882 -> after 889-895; insert base 938-937 -> after 951-955; replace base 941-941 -> after 959-961; replace base 980-986 -> after 1000-1012; replace base 990-995 -> after 1016-1022; replace base 1030-1031 -> after 1057-1058; insert base 1059-1058 -> after 1086-1125
```

| id | census entry | after lines | site |
|---|---|---|---|
| S1 | replace base 608-609 | 608-609 | status-block discharge bullet: at most weak under either chr15 treatment |
| S2 | replace base 665-670 | 665-670 | §(2) heterogeneity bullet: evidence beyond measured clustering, not robustly distinguishable from a clustering-only explanation |
| S3 | insert base 858-857 | 858-868 | §(7) PROVENANCE (i)-(iv) with the two `260904-dgi` CONTENT-SPEC.md:45-56 quotes |
| S4 | replace base 878-882 | 889-895 | §(8) FINDING 2 IS NOT ESTABLISHED bullet |
| S5 | insert base 938-937 | 951-955 | (10a) clustered-fraction bullet (719/2521 = 28.52% in 303 clusters; 1,802 = 71.48% singletons) |
| S6 | replace base 941-941 | 959-961 | (10a) ICC_hat 0.728930 scoped to those 719 pairs |
| S7 | replace base 980-986 | 1000-1012 | (10b) REPORT THE EVIDENCE, NOT WHICH SIDE OF A THRESHOLD IT FELL ON |
| S8 | replace base 990-995 | 1016-1022 | (10b) THE CONCLUSION blockquote (courier's replacement sentence) |
| S9 | replace base 1030-1031 | 1057-1058 | (10b) WHAT WAS NOT SHOWN, last sentence |
| S10 | insert base 1059-1058 | 1086-1125 | new `#### (10e) REVIEWER RESPONSE 2026-09-17 …` |

The `insert base 1059-1058` and `after 1086-1125` forms are the `split()` trailing-empty-element
artifact the PLAN documents, not an off-by-one: the (10e) content occupies after-lines 1086-1124 and
the file ends at 1124 lines.

## Guard

`irg_guard.py` on the real repo paths (`$X/guard_real.txt`), exit 0, output byte-identical to the
scratch run:

```
RESULT GREEN  122/122 PASS
```

122 PASS lines, 0 FAIL lines. Same command with the unedited base as BOTH base and after:
exit 1, `RESULT RED  54/101 PASS`, with FAILs in `G03-framing` (10), `G06-D1` (4), `G06-D2` (5),
`G06-D3` (5), `G06-D4` (8), `G06-D8-sentence` (1), `G06-D6-heading` (1), and also
`G03-regions`, `G03b-scoped`, `G06-D2-adjacent`, `G06-D4-quote`, `G06-D6-quote-fidelity`,
`G06-W1`, `G06-W7`, `G07-finding1-10d` — i.e. the guard can see the old state.

### G03 enumeration, verbatim from `guard_real.txt`

```
  enumeration G03 (framing phrases in the 2026-09-03 entry, AFTER):
    straddl                      line 1029  uer-correction-log
    straddl                      line 1032  uer-correction-log
    straddl                      line 1096  (10e)
    straddl                      line 1097  (10e)
    straddl                      line 1108  (10e)
    coin                         line 1097  (10e)
    artifact of analytic choice  line 1099  (10e)
    interchangeab                line 1001  S7-scoped
    interchangeab                line 1097  (10e)
    interchangeab                line 1110  (10e)
    interchangeab                line 1113  (10e)
    equally defensible           line 1001  S7-scoped
    equally defensible           line 1097  (10e)
    equally defensible           line 1114  (10e)
```

No `straddl`, `coin` or `artifact of analytic choice` anywhere in the entry outside the historical
`260908-uer` correction paragraph and the new (10e) note.

### G04 / G04c enumerations, verbatim from `guard_real.txt`

```
  enumeration G04 ('explain' family in new/changed text):
    block@665: ...ustly distinguishable from a clustering-only [explanat]  hypothesis-label (negated)
    block@858: ...s (icc 0.73, §(10a)) without showing that it [accounts for]  negated
    block@889: ...ustly distinguishable from a clustering-only [explanat]  hypothesis-label (negated)
    block@1016: ...ustly distinguishable from a clustering-only [explanat]  hypothesis-label (negated)
    block@1086: ...ustly distinguishable from a clustering-only [explanat]  hypothesis-label (negated)
  enumeration G04c ('explain' family + share claims in the courier paste block):
    carries x% of the excess   quoted attribution
    explanat                   hypothesis-label (negated)
    accounts for               negated
```

Supporting detail lines:

```
PASS  G05-cluster-arith        parsed {1: 1802, 2: 239, 3: 40, 4: 12, 5: 4, 6: 5, 7: 1, 8: 2} -> pairs 2521, singletons 1802, in clusters>=2 719, k(c>=2) 303, sum c^2 3767 (want 2521 / 1802 / 719 / 303 / 3767)
PASS  G07c-courier-share       36% appears on 2 line(s), each attributed; 64% count 0
PASS  G06-D8-sentence          draft replacement sentence: osf x1, paste x1
PASS  G09-bank-fence           exactly 2 fence lines; fenced body == scratch reply bytes
PASS  G09-bank-header          header carries md5 537391c10bdc4cb0dcca91af84c8bd3d, 8316 B, 60 lines, not byte-verified
PASS  G10-courier-status       status header present
PASS  G10-courier-fence        exactly 2 fence lines; paste block == scratch draft bytes
PASS  G10-courier-header       header carries draft md5 and byte count
```

The `G05-cluster-arith` detail line was byte-compared against the PLAN's quoted expectation — equal.

## Negative controls, verbatim from `negctl.txt` (exit 0)

```
POSITIVE CONTROL (unmutated): FAIL ids = [] -> GREEN
N01  osf      expect RED ['G01-osf-0.0366'] -> observed RED ['G01-osf-0.0366', 'G05-osf']  OK
N02  courier  expect RED ['G01-paste-1.652', 'G01-courier-1.652'] -> observed RED ['G01-courier-1.652', 'G01-paste-1.652', 'G05-courier', 'G10-courier-fence']  OK
N03  bank     expect RED ['G01-bank-1.969'] -> observed RED ['G01-bank-1.969', 'G09-bank-fence']  OK
N04  osf      expect RED ['G02-status-line'] -> observed RED ['G02-status-line', 'G12-census', 'G14-positions']  OK
N05  osf      expect RED ['G02-disposition'] -> observed RED ['G02-disposition']  OK
N06  osf      expect RED ['G03-framing'] -> observed RED ['G03-framing']  OK | literal line-grep 'straddl' on the mutated line: 0 (normalized guard RED)
N07  osf      expect RED ['G03-framing', 'G14-positions'] -> observed RED ['G03-framing', 'G14-positions']  OK
N08  osf      expect RED ['G03b-scoped'] -> observed RED ['G03b-scoped']  OK
N09  osf      expect RED ['G04-explain', 'G04-positive-claim'] -> observed RED ['G04-explain', 'G04-positive-claim']  OK
N10  osf      expect RED ['G04-explain'] -> observed RED ['G04-explain', 'G06-D1']  OK
N11  osf      expect RED ['G05-osf', 'G06-D3'] -> observed RED ['G05-osf', 'G06-D3']  OK
N12  osf      expect RED ['G05-osf'] -> observed RED ['G05-osf']  OK
N13  courier  expect RED ['G06-D8-sentence', 'G05-courier', 'G10-courier-fence'] -> observed RED ['G05-courier', 'G06-D8-sentence', 'G10-courier-fence']  OK
N14  osf      expect RED ['G06-D2'] -> observed RED ['G06-D2']  OK
N15  osf      expect RED ['G06-D4-quote'] -> observed RED ['G06-D4-quote']  OK
N16  osf      expect RED ['G07-share'] -> observed RED ['G05-osf', 'G07-share']  OK
N17  osf      expect RED ['G07-universal'] -> observed RED ['G07-universal']  OK
N18  osf      expect RED ['G07-finding1-10d'] -> observed RED ['G07-finding1-10d', 'G12-census']  OK
N19  osf      expect RED ['G08-head566', 'G14-positions', 'G12-census'] -> observed RED ['G08-head566', 'G12-census', 'G14-positions']  OK
N27  osf      expect RED ['G00-entry-head'] -> observed RED ['G00-entry-head']  OK
N20  osf      expect RED ['G08-uer-paragraph', 'G12-census'] -> observed RED ['G05-osf', 'G08-uer-paragraph', 'G12-census']  OK
N21  osf      expect RED ['G14-positions'] -> observed RED ['G14-positions']  OK
N22  osf      expect RED ['G12-census'] -> observed RED ['G05-osf', 'G12-census']  OK
N23  bank     expect RED ['G09-bank-fence'] -> observed RED ['G09-bank-fence']  OK
N24  courier  expect RED ['G10-courier-fence'] -> observed RED ['G10-courier-fence']  OK
N25  osf      expect RED ['G06-D6-heading', 'G03-regions'] -> observed RED ['G03-framing', 'G03-regions', 'G03b-scoped', 'G06-D6-heading', 'G06-D6-quote-fidelity', 'G07-finding1-10d']  OK
N26  osf      expect RED ['G08-table', 'G12-census'] -> observed RED ['G05-osf', 'G08-table', 'G12-census']  OK
N28  courier  expect RED ['G04c-courier', 'G07c-courier-share', 'G10-courier-fence'] -> observed RED ['G04c-courier', 'G07c-courier-share', 'G10-courier-fence']  OK
N29  courier  expect RED ['G04c-courier', 'G10-courier-fence'] -> observed RED ['G04c-courier', 'G10-courier-fence']  OK
N30  courier  expect RED ['G07c-courier-share', 'G10-courier-fence'] -> observed RED ['G07c-courier-share', 'G10-courier-fence']  OK
N31  osf      expect RED ['G05-cluster-arith', 'G12-census'] -> observed RED ['G05-cluster-arith', 'G05-osf', 'G12-census']  OK
N32  osf      expect RED ['G06-D2-adjacent'] -> observed RED ['G06-D2-adjacent']  OK
N33  osf      expect RED ['G07-no'] -> observed RED ['G07-no']  OK
N34  courier  expect RED ['G10-courier-status'] -> observed RED ['G10-courier-status']  OK
N35  bank     expect RED ['G09-bank-header'] -> observed RED ['G09-bank-header']  OK
N39  osf      expect RED ['G06-W1', 'G06-W1-old'] -> observed RED ['G06-W1', 'G06-W1-old']  OK
N40  osf      expect RED ['G06-W7'] -> observed RED ['G06-W7']  OK
N36  base     expect RED ['G05-record-anchors'] -> observed RED ['G05-osf', 'G05-record-anchors']  OK
N37  base     expect RED ['G02-count-not'] -> observed RED ['G02-count-not', 'G12-census', 'G14-positions']  OK
N38  base     expect RED ['G02-count-drafted'] -> observed RED ['G02-count-drafted', 'G07-finding1-10d', 'G12-census']  OK
N41  osf      expect RED ['G06-D4'] -> observed RED ['G06-D4']  OK
N42  courier  expect RED ['G10-courier-header'] -> observed RED ['G10-courier-header']  OK

NEGCTL RESULT: ALL CONTROLS OBSERVED RED
```

42 control lines, all `OK`; no `MISSING` and no `INVALID CONTROL`. N06's literal line-grep for
`straddl` on its mutated line counts 0 while the normalized guard goes RED — the normalized guard
catches what a literal grep misses.

## Neighbouring enforcers — BEFORE == AFTER

`norm_enf` = `^(PASS|FAIL|RESULT)` lines with `[...]` groups and `:N`/`:N-M` line numbers stripped,
`LC_ALL=C sort`ed. All three diffs printed nothing, `rc=0`, and the trailing `exit=` lines are equal.

| enforcer | BEFORE last two lines | AFTER last two lines | normalized multiset |
|---|---|---|---|
| `260908-uer` `guard.py` | `38/40 PASS` / `uer exit=1` | `38/40 PASS` / `uer exit=1` | 40 lines, identical |
| `260916-vqq-verify.py --live` | `RESULT RED checks=446 parsed=112 table=112 verified=102 c-res=112  reds=['c:c01', 'c:c02', 'c:c03', 'c:c04', 'c:c18', 'c:c62', 'c:c63', 'c:n02', 'c:n48', 'c:n06']` / `vqq exit=1` | identical, same 10 reds | 437 lines, identical |
| `260814-u9p-verify.sh ledger` | `RESULT: ALL CHECKS PASSED (section: ledger)` / `u9p exit=0` | same | 9 lines, identical |

The multisets are non-empty (40 / 437 / 9), so the empty diffs are meaningful, not vacuous.

## G13 path scope, with the probe observed RED then GREEN

- `comm -23 status_before status_after` printed nothing (0 lines): nothing vanished.
- `comm -13` printed exactly these 3 lines:
  ```
   M .planning/osf_deviations.md
  ?? .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
  ?? .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md
  ```
- `git status --porcelain -- .planning/amendments .planning/STATE.md .planning/HANDOFF.json .planning/DECISIONS.md src tests | wc -l` == 0.
- RED control: after `touch src/python/__irg_negctl_probe.py`, `comm -13` showed a 4th line
  `?? src/python/__irg_negctl_probe.py` and the explicit `wc -l` became **1** (observed RED).
- After `rm -- src/python/__irg_negctl_probe.py`: back to exactly the 3 lines, `wc -l` == **0**
  (GREEN again); the probe path is absent (`test -e` false) and the post-removal status file is
  byte-identical to the pre-probe one.
- `.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md` was not touched (not in the
  commit, and the tracked tree is clean).

## KNOWN AND DELIBERATELY NOT ACTED ON (copied from the PLAN's context; for Carter, not executor work)

1-3. **RESOLVED UPSTREAM 2026-09-17.** Flags 1-3 (the "everywhere they appear" overstatement, the
   "everything except §3" scoping, and the share-metric mismatch) were applied by the orchestrator to
   `$DRAFT` itself, which is re-pinned at md5 `042fe4798429f30fa5b4bbb59dee9419`. Point 1 now states
   his metric on the POOLED 1.360 (36%), the same metric on the effective deffs 1.19 / 1.26 (19% and
   26%), the removal-share reading (32% and 42%), and that therefore no share goes into the
   disclosure. All six of those figures were re-derived at plan time and are arithmetically correct
   at the stated precision. The point-2 replacement sentence is byte-unchanged, so S8 still matches
   it exactly.
4. `.planning/debug/260916-COURIER-...-UNSENT.md` is still headed UNSENT, but the reviewer quotes its
   §5-§6. **STILL OPEN**; that file is frozen by this plan.
5. The pasted reply's first line opens "Seth —". It is banked verbatim and not interpreted. **STILL
   OPEN by design.**

## Self-Check: PASSED

- All three deliverable paths exist on disk with the pinned md5s, and the committed blobs
  (`git show HEAD:<path>`) carry the same md5s.
- Commit `9bdcd7d` exists in `git log` and lists exactly 3 files.
- Tracked tree clean (`git status --porcelain --untracked-files=no | wc -l` == 0) after the commit.
- No stubs: the three files are final text, not placeholders.

## Deviations from plan

None — the plan executed exactly as written. Every measured value equals its pinned expectation
(build md5s, guard GREEN 122/122, guard RED 54/101 on the unedited file, 42/42 controls RED with the
positive control GREEN, census and detail lines byte-equal to the PLAN's quotes, enforcer multisets
identical). No number was adjusted, no check widened, no guard weakened.

Nothing was posted, sent or transmitted; no OSF, reviewer, cloud or network action occurred; no push.

STATE.md / HANDOFF.json / DECISIONS.md not written — orchestrator close-out.
