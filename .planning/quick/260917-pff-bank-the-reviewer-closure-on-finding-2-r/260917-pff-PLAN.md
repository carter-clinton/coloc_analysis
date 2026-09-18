---
phase: quick-260917-pff
plan: 01
type: execute
wave: 1
depends_on: []            # ordering is ENFORCED by the Task 1 pre-flight (five input md5 pins + a clean tracked tree), never by a HEAD pin
mode: quick
branch: m3-W2-aou-deltas
worktree: none            # GPFS: no worktree, no branch change. Scratch lives OUTSIDE the repo.
autonomous: true
push: false
requirements: ["pff-D1", "pff-D2", "pff-D3", "pff-D4", "pff-D5"]

# DOCS ONLY. Exactly five deliverable paths, plus this PLAN and its SUMMARY.
files_modified:
  - .planning/osf_deviations.md                                                                                        # 3 exact-once sites (S1 S2 S3), all at or after base :1077
  - .planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md                                                # line 3 only (S4)
  - .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md                                             # line 3 only (S5)
  - .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md   # NEW (D1)
  - .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md  # NEW (D5)
  - .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-PLAN.md                              # this file (committed in Task 3)
  - .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SUMMARY.md                           # NEW (Task 3)

files_frozen:
  - .planning/osf_deviations.md lines 1-1077 (byte-identical; every LIVE line citation into this ledger ends at or below :739)
  - .planning/osf_deviations.md §(10a), §(10b), §(10c) and the frozen 260908-uer correction note (byte-identical)
  - .planning/osf_deviations.md Finding 1's count lines :1073-1077 (byte-identical)
  - both courier files outside line 3, including the 260916 file's own "do NOT send the superseded figures" warning
  - .planning/amendments/**          # posted OSF bodies
  - .planning/STATE.md, .planning/HANDOFF.json, .planning/DECISIONS.md   # close-out is the ORCHESTRATOR's
  - .planning/quick/260917-irg-**    # the irg PLAN/SUMMARY line references go stale BY DESIGN and are NOT rewritten here
  - src/**, tests/**, config/**, workflow/**
  - every enforcer script under .planning/quick/** (run them, never edit them)

must_haves:
  truths:
    - "The reviewer's 2026-09-17 closure is banked as received at .planning/quick/260917-pff-…/260917-pff-SETH-CLOSURE-finding2-review-as-received.md: a provenance header that says NOT BYTE-VERIFIED and carries the scratch md5/size/line count, then the pasted text byte-for-byte inside a 4-backtick fence (D1)"
    - "§(10e)'s INTERCHANGEABLE bullet no longer says 'This entry does not record his acceptance of the scoping decided here'; it records, in two-to-three factual sentences with no praise and no motive, that on 2026-09-17 he accepted all seven points, WITHDREW BOTH objections (the pooled design-effect share, and this post-hoc window selector, which he named as his own threshold objection applied to the selector), and closed with no open objection, with nothing further from him until a new measurement or a posting decision (D2)"
    - "§(10d) carries ONE new scope sentence beside Finding 1, in the reviewer's own accepted formulation with the denominator attached: in all 21 regions scanned — 21 of the 276-region ancestry-resolved manifest, 7.6% of the panel — a post-filter residual of defined-but-degraded r survives the POSTED predicate and is invisible to the retained NaN-raise by construction; it says nothing about the 255 regions not scanned and nothing about any predicate other than the posted one (D3)"
    - "Finding 1's counts are byte-unchanged: 2560 PRE / 534 POST of 3094 (17.26%); 2047 PRE / 474 POST of 2521 (18.80%); 21/21; 0 with zero POST. 21/276 = 7.61% is stated to one decimal as 7.6%, and neither 7.61% nor 7.7% appears. The word 'universal' and the phrase 'no geometric predicate' remain absent from the ledger (D3)"
    - "§(10e)'s 'Finding 1's text is unchanged.' — which the §(10d) bullet falsifies on the same date — is reconciled in place: the counts and the claim are unchanged, and the added scope sentence is named (S3, approved by Carter 2026-09-17)"
    - "Both courier files are corrected in place under their existing filenames: the 260916 file says SENT 2026-09-17 in the CORRECTED form — with the epistemic qualifier IN the status sentence itself (`per Carter's record; the text as sent is banked, not byte-verified, at <AS-SENT path>`) rather than one hop away — that the body below is the DRAFT and not the text sent, that the superseded figures were removed from the two sentences that carried them before it went out and are not restated, and that THIS file stays the draft of record; the 260917 file says SENT 2026-09-17 and names the closure as its reply. Both note that the UNSENT filename is kept because other records cite the path (D4)"
    - "The courier text that ACTUALLY WENT OUT is banked at .planning/quick/260917-pff-…/260917-pff-260916-COURIER-AS-SENT-measurement-result.md: a provenance header saying it is the text as SENT on 2026-09-17 (Carter's decision, recorded today), naming the draft of record, recording that the superseded figures were removed from the two sentences that carried them so this file contains none of them, and saying it is banked from a session scratch copy and is NOT byte-verified against what was pasted into the reviewer's channel — then those bytes verbatim inside a 4-backtick fence (D5)"
    - "The 260916 header states ONLY what the record supports about the reviewer's \"a 0.02 mismatch\" figure: that his reply (§3) characterises the discrepancy with it; that the text as sent stated no figure for it; that the figure was reachable from two files committed BEFORE his reply (this draft's own body, committed in `c93e97b` on 2026-09-16, which states it verbatim, and the disclosure as it stood at that commit, which carried the superseded value it is computed against); and ⛔ that WHICH source he used is NOT established by this record and is recorded as UNATTRIBUTED. The clause 'came from the earlier exchange' is absent (2026-09-18 blocker fix)"
    - "The five superseded literals (1.652, 0.0366, 1.564, 0.0556, 1.969) do not INCREASE in the ledger or in either courier, are 0 in BOTH new bank files, and are 0 in the new 260916 header; the 260916 file's own warning naming them survives byte-exact"
    - "Nothing new says or implies that clustering EXPLAINS Finding 2: zero explain-family occurrences in the new ledger text, in either new courier header, and in BOTH bank provenance headers; each bank's explain-family use sits INSIDE its verbatim fence (1 of 1 in the closure, 3 of 3 in the AS-SENT text); the 'clustering explains' surface form in the 260916 body and in the AS-SENT body is enumerated and negated in context in both"
    - "The Status line is byte-exact; 'DRAFTED — NOT POSTED' and 'NOT ESTABLISHED' counts do not fall in the ledger or in either courier, and the text as sent still carries 'DRAFTED — NOT POSTED' inside its fence; all six Finding 2 disposition sentences survive word for word"
    - "Only the five deliverable paths change (+ PLAN/SUMMARY); nothing under .planning/amendments/, STATE.md, HANDOFF.json, DECISIONS.md, the irg quick dir, src/ or tests/ moves, and a src/ probe is observed RED then GREEN"
    - "Ledger lines 1-1077 are byte-identical, so all 201 enumerated colon citations ending at or below :1077 re-resolve to identical bytes; the 4 colon citations and 37 bare references that move are all inside quick-260917-irg plan-time records and are enumerated with their re-resolved ranges"
    - "The uer guard, vqq --live verifier and u9p ledger check give an identical line-normalized PASS/FAIL/RESULT multiset and identical exit codes before and after; vqq --live stays RESULT RED with exactly reds=['c:c01','c:c02','c:c03','c:c04','c:c18','c:c62','c:c63','c:n02','c:n48','c:n06']"
  artifacts:
    - path: ".planning/osf_deviations.md"
      provides: "the closure banked into §(10d) and §(10e)"
      contains: "SCOPE OF FINDING 1 — the reviewer's own formulation, accepted 2026-09-17"
      md5_after: "22e1b1db105dbacc56c5f8fb3ccc7298"   # 89846 B, 1139 lines, from base 6ba5ad5365b64a2482eafea75168b8ae (88393 B, 1124 lines)
    - path: ".planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md"
      provides: "the reviewer's closure as received, with a provenance header"
      md5: "d2eb6a02afba146b97d06f185c8c9d96"   # 4631 B, 47 lines
    - path: ".planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md"
      provides: "the 260916 courier text AS SENT, with a provenance header"
      md5: "be9211e8caa55f921b3b90c7b7c23f0b"   # 6398 B, 102 lines
    - path: ".planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md"
      provides: "status corrected to SENT (in the corrected form), pointing at the AS-SENT bank, filename kept"
      md5_after: "f2251f195382f89f6b0305594c48a300"   # 7021 B, 106 lines, from base c068559c298a026e19eaabf9d0566c4d (5614 B, 91 lines)
    - path: ".planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md"
      provides: "status corrected to SENT, closure named as its reply, filename kept"
      md5_after: "764c3d2af5cbb53191699dea7f213d2a"   # 6195 B, 90 lines, from base a92d9ec21ebb26b39ae8df99696b2abf (5763 B, 86 lines)
  key_links:
    - from: ".planning/osf_deviations.md §(10e) INTERCHANGEABLE bullet"
      to: ".planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md"
      via: "repo path cited in the D2 sentence"
      enforcer: "pff_guard.py G08-D2-bankref (RED control N114)"
    - from: ".planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md line 3 block"
      to: ".planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md"
      via: "the draft-of-record pointer at the text as sent, and the AS-SENT header's pointer back"
      enforcer: "pff_guard.py G10-D4-c16-pointer + G07-D5-header-draftref (RED controls N173, N174, N171)"
    - from: ".planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md line 3 block"
      to: ".planning/quick/260917-irg-…/260917-irg-SETH-REPLY-finding2-review-as-received.md §3"
      via: "the quoted figure \"a 0.02 mismatch\", which must exist there and nowhere in the sent text, recorded as UNATTRIBUTED"
      enforcer: "pff_guard.py G10-D4-mismatch-anchor + G10-D4-mismatch-source + G10-D4-c16-noattr + G10-D4-c16-unattributed + G10-D4-c16-committed-src (RED controls N093, N136, N175, N176, N177, N178)"
    - from: ".planning/osf_deviations.md §(10d) new scope bullet"
      to: ".planning/osf_deviations.md §(9) `region_ids_selected = 276`"
      via: "the denominator the 7.6% is taken over"
      enforcer: "pff_guard.py G06-record-anchors + G06-7.6-stated (RED controls N096, N090)"
---

## Revision history

- **rev 1** (2026-09-17): plan-checked. Mechanics PASS — guard GREEN 391/391 over 122 ids, 106
  controls, coverage 122/122, RED 331/379 on the unedited files, irg-guard FAIL set exactly
  `{G05-osf, G06-W1, G07-finding1-10d, G10-courier-status, G12-census}` — with **1 BLOCKER and 6
  warnings against the text**.
- **rev 2** (2026-09-18): text only; the task, the five deliverable paths, the disposition and the
  DRAFTED — NOT POSTED status are unchanged.
  - **BLOCKER (S4)** — the header asserted two mutually exclusive provenance claims and the
    load-bearing one was unsupported. Deleted *"came from the earlier exchange rather than from what
    was sent"* entirely; S4 now states only the provable facts and records the figure's source as
    **UNATTRIBUTED**. New evidence re-verified at plan time: the draft has been committed since
    `c93e97b` (2026-09-16 14:31), *before* the reviewer's 2026-09-17 reply; that blob states
    `0.02 mismatch` once; the disclosure at that commit carried the superseded value twice. The
    reviewer reads this repo, so the figure was reachable with nothing sent — Carter's record (only
    the corrected form was sent) stands, and the fix is to stop attributing. KNOWN item 6.
  - **W1** — the closure bank's unenforceable `Received: … 18:11 EDT` (contradicted by the scratch
    file's 18:18 mtime) now states **both** facts, each labelled, both pinned.
  - **W2** — the epistemic qualifier moved INTO the status sentence: *"per Carter's record; the text as
    sent is banked, not byte-verified, at <AS-SENT path>"*.
  - **W3** — the citation note's mis-attribution of 2 of the 11 out-of-range rows corrected (they are
    a `DECISIONS.md` line reference, not `run_native_ld_panel.py`); the conclusion stands.
  - **W4** — S3 now names all three clauses S1 adds, not just the region count.
  - **W5** — Task 2's automated-verify frozen-path assertion now includes the irg quick dir, matching
    its own action step. (No literal verify-tag is written in prose here: a stray opening tag would
    make the plan's own task parser read one giant block.)
  - **W6** — the tautological sub-clause dropped from `G05-enum-nonvacuous` (still falsifiable: N086).
  - Re-derived: guard **GREEN 396/396** over **126** ids, **113** controls all observed RED, coverage
    **126/126**, RED **333/383** (29 ids) on the unedited files, irg-guard FAIL set **unchanged**.

<objective>
Bank the reviewer's 2026-09-17 CLOSURE of the Finding 2 review and the courier text that actually
went out to him, and make the records they falsify true, exactly as Carter decided (D1-D5).

Purpose: he closed out — all seven points accepted, both of his objections withdrawn (his pooled
design-effect share, and his "pick the better-corrected window" selector), nothing open, and nothing
further from him until a new measurement or a posting decision. Three records said otherwise: §(10e)
still said the entry "does not record his acceptance of the scoping decided here", and both couriers
were still headed UNSENT although both were sent on 2026-09-17. His accepted formulation of Finding
1's scope, with its denominator, was not yet in §(10d). And the text that actually reached an external
reviewer existed only as session scratch, so the repo had no record of what was said to him.

Output: one commit with the five deliverables (closure banked; the 260916 courier banked AS SENT;
§(10d) scope sentence; §(10e) closure record and its in-place reconciliation; both courier statuses
corrected in place under their existing filenames), then one commit with this PLAN and its SUMMARY.
The disposition does not move: Finding 2 stays **NOT ESTABLISHED** and the disclosure stays
**DRAFTED — NOT POSTED**. The executor writes neither STATE.md, HANDOFF.json nor DECISIONS.md,
contacts nobody, posts nothing and pushes nothing.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/osf_deviations.md (the 2026-09-03 entry: base :567-1124; §(10d) :1071-1084, §(10e) :1086-1124)
@.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md
@.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
@.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md

## Every shell block in this plan starts with this preamble (shell state does not persist)

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
TD=.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r
SCR=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad
IN=$SCR/pff
X=$SCR/pff-exec
CLOSURE=$IN/SETH-CLOSURE-2026-09-17-as-pasted.txt
SENTTXT=$SCR/SETH-PASTE-1b-measurement-result-SEND.txt
C16=.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md
C17=.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
IRG=.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md
BANK=$TD/260917-pff-SETH-CLOSURE-finding2-review-as-received.md
SENTBANK=$TD/260917-pff-260916-COURIER-AS-SENT-measurement-result.md
U=.planning/quick/260908-uer-correct-the-rao-scott-table-the-pooled-r/guard.py
V=.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py
N=.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-verify.sh
cd "$REPO"
norm_enf() { grep -E '^(PASS|FAIL|RESULT)' "$1" | sed -E 's/\[[^]]*\]//g; s/:[0-9]+(-[0-9]+)?//g' | LC_ALL=C sort; }
```

⚠ `grep` in an interactive shell here is a **ugrep wrapper**. Use `python3`, or `grep --` with the
patterns above, and never trust an exit 0 with empty output: print the count as well.

## Pins (all measured at plan time, 2026-09-17. HEAD is NOT pinned; the five input md5s and a clean tracked tree are.)

| object | pin |
|---|---|
| `.planning/osf_deviations.md` BEFORE | md5 `6ba5ad5365b64a2482eafea75168b8ae`, 88393 B, 1124 lines |
| `$C16` BEFORE | md5 `c068559c298a026e19eaabf9d0566c4d`, 5614 B, 91 lines |
| `$C17` BEFORE | md5 `a92d9ec21ebb26b39ae8df99696b2abf`, 5763 B, 86 lines |
| `$CLOSURE` (paste recorded in-session 2026-09-17 18:11 EDT; **file mtime 2026-09-17 18:18 EDT**; ⛔ NOT byte-verified vs the original) | md5 `0b9793244d07f407e07c1e47baff994d`, 3168 B, 25 lines, no 4-backtick fence, no tab, final newline present |
| `$SENTTXT` (the text AS SENT, from session scratch, ⛔ NOT byte-verified vs the reviewer's channel) | md5 `502fe68481edeedcf42d53442af6b127`, 4907 B, 77 lines, no 4-backtick fence, no tab, final newline present, all five superseded literals 0 |
| embedded `pff_cites.py` / `pff_apply.py` / `pff_guard.py` / `pff_negctl.py` | md5 in each BEGIN marker below |
| `.planning/osf_deviations.md` AFTER | md5 `22e1b1db105dbacc56c5f8fb3ccc7298`, 89846 B, 1139 lines |
| `$BANK` AFTER | md5 `d2eb6a02afba146b97d06f185c8c9d96`, 4631 B, 47 lines |
| `$SENTBANK` AFTER | md5 `be9211e8caa55f921b3b90c7b7c23f0b`, 6398 B, 102 lines |
| `$C16` AFTER | md5 `f2251f195382f89f6b0305594c48a300`, 7021 B, 106 lines |
| `$C17` AFTER | md5 `764c3d2af5cbb53191699dea7f213d2a`, 6195 B, 90 lines |
| citation enumeration | colon pass 212 rows / 150 files, digest `5d8e9e715223a3095faa0858c09a8273`; bare pass 37 rows / 2 files, digest `2f74b0de3f1abae9aa67643d8f9781cb` |

## The five sites and two new files (all text is VERBATIM inside the embedded `pff_apply.py`; nothing is retyped)

| id | file | base lines | after lines | gist | decision |
|---|---|---|---|---|---|
| S1 | osf | insert after 1077 (+6) | 1078-1083 | new §(10d) bullet: SCOPE OF FINDING 1 in the reviewer's own accepted formulation — all 21 regions scanned, 21 of the 276-region manifest (§(9)), 7.6% of the panel, defined-but-degraded `r` survives the POSTED predicate, invisible to the retained NaN-raise by construction, and an explicit ⛔ disclaimer over the 255 unscanned regions and over any other predicate | D3 |
| S2 | osf | replace 1115 (1->7) | 1121-1127 | §(10e) INTERCHANGEABLE bullet: the stale "This entry does not record his acceptance of the scoping decided here." becomes the closure record (three sentences) | D2 |
| S3 | osf | replace 1122 (1->4) | 1134-1137 | §(10e) "Finding 1's text is unchanged." — made FALSE by S1 — becomes "Finding 1's counts and its claim are unchanged", naming ALL THREE clauses the S1 sentence adds (21 of 21 scanned regions, the **posted** predicate, the retained **NaN-raise**) and that the counts do not move. ⚠ Planner-found internal contradiction, **APPROVED by Carter 2026-09-17**; the summary was widened 2026-09-18 (W4) | D3 (reconciliation) |
| S4 | c16 | replace 3 (1->16) | 3-18 | SENT 2026-09-17 in the CORRECTED form, **with the qualifier in the status sentence itself** (`per Carter's record; the text as sent is banked, not byte-verified, at $SENTBANK` — the path appears exactly once, there); the body below is the DRAFT not the text sent; the superseded figures were removed from the two sentences that carried them and are not restated; **this file stays the DRAFT OF RECORD**; and the mismatch paragraph states only what is provable — his reply's §3 puts a figure on the discrepancy, the sent text stated none, the figure was reachable from two files committed before his reply, and ⛔ **which source he used is UNATTRIBUTED**; the UNSENT filename is kept | D4, D5 |
| S5 | c17 | replace 3 (1->5) | 3-7 | SENT 2026-09-17; the reviewer's CLOSURE is the reply to it (all seven accepted, both objections withdrawn, no open objection), banked as received; the UNSENT filename is kept | D4 |
| BANK | new | — | 47 lines | provenance header (**both** time facts — paste recorded in-session 18:11 EDT, scratch file written 18:18 EDT — pasted by Carter, **not byte-verified**, scratch md5/size/lines, what it records, where it is recorded, ⛔ correspondence not a source) + the pasted closure byte-for-byte in a 4-backtick fence | D1 |
| SENTBANK | new | — | 102 lines | provenance header (the text as **SENT** 2026-09-17, Carter's decision recorded today; the draft of record named by repo path; the superseded figures removed from the two sentences that carried them so this file contains none of them; banked from a session **scratch** copy and **not byte-verified** against what was pasted into the reviewer's channel; his reply and his closure named) + those bytes verbatim in a 4-backtick fence | D5 |

⚠ **S3 was not one of the original D1-D4; Carter approved it on 2026-09-17.** D3 adds a bullet to
§(10d); §(10e) asserted *"Finding 1's text is unchanged."* — which S1 makes false on the same date.
Keeping a sentence that this same edit falsifies is the exact defect D2 exists to fix, so it is
reconciled in place, minimally and factually: the counts and the claim ARE unchanged, and the added
scope sentence is named. `G09-D3-10e-reconciled` fails if either form is wrong.

## Decision coverage

| D | where | full? |
|---|---|---|
| D1 closure banked as received, provenance header incl. "not byte-verified" | `pff_apply.py` BANK_HEADER; guard G07-D1-fence / G07-D1-header / G07-D1-header-pins | Full |
| D2 §(10e) stale sentence replaced by the closure record, 2-3 factual sentences, no praise/motive | S2; guard G08-D2 (8 phrases), G08-D2-old-gone, G08-D2-sentences, G08-D2-no-praise, G08-D2-bankref, G08-D2-no-new-stats | Full |
| D3 ONE scope sentence beside Finding 1, denominator attached, counts byte-unchanged, no "universal", nothing about predicates in general or the 255 unscanned, attributed; plus the S3 reconciliation naming all three clauses | S1, S3; guard G09-D3 (7 phrases), G09-D3-banned, G09-D3-counts-byte, G09-D3-counts-text, G09-D3-predicate (now **3** occurrences, all SCOPED), G09-D3-10e-reconciled, G06-7.6-stated | Full |
| D4 both courier statuses corrected in place, filenames kept, rest byte-unchanged incl. the figures warning | S4, S5; guard G10-D4-* (**15 distinct ids / 24 check lines**, measured — the rev-1 figure "13 ids" was neither), G01-c16-warning | Full |
| D4-prov (2026-09-18 blocker fix) the mismatch figure's source is stated as UNATTRIBUTED, and the epistemic qualifier sits in the status sentence | S4; guard G10-D4-c16-noattr, G10-D4-c16-unattributed, G10-D4-c16-committed-src, G10-D4-c16-qualifier, G01-c16-newheader, G01-c16-warning (RED controls N175-N179) | Full |
| D1-time (2026-09-18 W1) the closure bank states BOTH time facts rather than one nothing enforces | BANK_HEADER; guard G07-D1-header (`paste recorded in-session 18:11 edt`, `scratch file written 18:18 edt`; RED controls N103, N104) + the Task 1 mtime pre-flight | Full |
| D5 the text AS SENT banked with a provenance header; the draft of record points at it | SENTBANK, S4; guard G07-D5-fence / G07-D5-header / G07-D5-header-pins / G07-D5-header-draftref, G10-D4-c16-pointer, G10-D4-c16-qualifier, G01-sent-* (5), G02-sent-drafted, G05-sent-fence-scope, G05-positive-sent, G05-positive-senthead, G06-num-sent | Full |
| standing: five literals do not increase; 0 in both banks; 0 in the new c16 header | guard G01 (27 ids) | Full |
| standing: nothing says clustering EXPLAINS Finding 2 | guard G05 (13 ids) + enumerations | Full |
| standing: DRAFTED — NOT POSTED / NOT ESTABLISHED / status line / dispositions survive | guard G02 (7 ids) | Full |
| standing: §(10a-c), the uer note, the tables and lines 1-1077 frozen | guard G11 (6 ids), G04-census-* | Full |
| standing: numbers reconcile (21, 276, 7.6, 255, "seven", 3168/25, 4907/77) | guard G06 (8 ids) | Full |
| standing: line-position safety, citations re-resolved | guard G12 (4 ids), G13 (3 ids) + enumerations | Full |
| standing: path scope | Task 2 step 6 with an observed-RED `src/` probe | Full |
| standing: enforcers unchanged | Task 2 step 5 (uer / vqq --live / u9p) | Full |

## Facts verified at plan time (so the executor does not have to re-derive them, and so a reader can check them)

- **"all seven points"** — the 260917 courier's paste block carries **exactly 7** numbered points
  (1 DISPOSITION, 2 THE STRADDLE, 3 "INTERCHANGEABLE", 4 §3, 5 CREDIT, 6 22.7% vs 28.5%, 7 FINDING 1).
  `pff_guard.py` re-counts them (`G06-derived`, key `seven`; RED control N091), so "seven" is a
  reconciled figure and not an assertion.
- **21 / 276 / 7.6% / 255** — `21 regions` and `` `region_ids_selected = 276` `` are both in the base
  ledger (`G06-record-anchors`); 21/276 = **7.6087%** = **7.61%** at two decimals and **7.6%** at one,
  and the guard requires the one-decimal form to appear exactly once with 7.61% and 7.7% absent
  (`G06-7.6-stated`). 276 − 21 = **255**. ⚠ §(9) `:920-921` warns that 276 is the *manifest* size and
  must never be read as this measurement's region count — S1 therefore names the denominator
  (`21 of the 276-region ancestry-resolved manifest (§(9))`) rather than writing a bare percentage.
- **The text AS SENT (D5)** — `$SENTTXT` was measured at plan time: md5 `502fe68481edeedcf42d53442af6b127`,
  **4907 B, 77 lines**, **no 4-backtick sequence**, no tab, final newline present, and **all five
  superseded literals at 0**. Diffed against the draft body, the two sentences that carried those
  figures are the ones that changed: *"…the straddle TIGHTENED (0.0326 / 0.0517, previously …)"* became
  *"…TIGHTENED, to 0.0326 / 0.0517."*, and *"the fixed-rate pass produced [figure] for drop-sub13 where
  the courier said 1.99 — a 0.02 mismatch"* became *"the fixed-rate pass disagreed with the courier's
  1.99 for drop-sub13 — a small mismatch"*. So the figures were removed from those two sentences before
  sending, which is exactly what the D5 header and S4 record, **and no figure is restated in either**.
- **The courier-vs-table mismatch (D4) — and why S4 ATTRIBUTES NOTHING.** ⚠ The previous revision of
  this plan had S4 assert that the reviewer's *"a 0.02 mismatch"* phrasing *"came from the earlier
  exchange rather than from what was sent"*. **That claim is unsupportable and has been deleted.** What
  the record does support, each item re-verified at plan time 2026-09-18:
  - his banked reply puts the figure on it, *"a 0.02 mismatch"*, in its **§3** (one occurrence;
    `G10-D4-mismatch-source` re-derives the section by walking back to the nearest `N. §M` heading);
  - the text **as sent** states **no figure** for that discrepancy (`$SENTTXT`: *"…disagreed with the
    courier's 1.99 for drop-sub13 — a small mismatch"*);
  - the figure was **reachable from files already committed before his 2026-09-17 reply**, with nothing
    having been sent that carried it:
    `git log --format='%h %ad' --date=format:'%m-%d %H:%M' -- "$C16" | tail -1` → **`c93e97b 09-16
    14:31`** (that is the file's *only* commit, and its blob md5 there equals the base pin), and
    `git show c93e97b:"$C16" | grep -c -- '0.02 mismatch'` → **1**, i.e. this draft's own body states
    the figure verbatim (base `$C16:56`); while
    `git show c93e97b:.planning/osf_deviations.md | grep -c -- '1.969'` → **2**, i.e. the disclosure as
    it stood at that commit carried the superseded value the figure is computed against (base
    `$C16:55` carries the same pairing in the draft body). **The reviewer reads this repo.**
  - ⛔ therefore **which of those two he actually read is NOT established by this record**, and S4
    records it as **unattributed**, not attributed. Carter's record — that only the corrected form was
    sent — stands untouched; nothing is inferred from his phrasing about what went out.
  Enforced by `G10-D4-c16-noattr` (the deleted clause must stay absent), `G10-D4-c16-unattributed`,
  `G10-D4-c16-committed-src` and `G10-D4-c16-qualifier`, each proven falsifiable by N175-N179.
  ⚠ **`$C16`'s body keeps the figure and the superseded value at base `:55-57`** behind its own ⛔
  warning (frozen by D4) — the new header quotes the figure but restates no superseded value
  (`G01-c16-newheader`).
- **The closure's two time facts (W1, 2026-09-18).** The old bank header asserted a bare
  *"Received: 2026-09-17 18:11 EDT"* that **nothing enforced** and that the scratch file's own mtime
  (**18:18 EDT**) contradicts. The header now states both, each labelled by what it is: the **paste
  recorded in-session** at 18:11 EDT (Carter's session record — not file-verifiable, and not claimed to
  be), and the **scratch file written** 18:18 EDT (`stat` on `$CLOSURE`, pinned in Task 1 step 1 and
  by `G07-D1-header`; RED controls N103, N104).
- **The "clustering explains" surface forms** are *"the disclosure does not say clustering explains it,
  and neither do I"* — one in `$C16`'s body and one in the AS-SENT body, **both negated in context**,
  both enumerated by `G05-positive-ctx`, and proven falsifiable by RED control N083.

## Line-position safety — measured, not assumed

`pff_cites.py` runs two mechanical passes and `pff_guard.py` re-resolves every row (`G12`, `G13`):

- **Colon pass**: 212 rows across 150 tracked files (a deliberate SUPERSET — the `bare :N on a line
  that also names the ledger` rule over-reports). **201 rows end at or below `:1077`** and the guard
  proves those lines are byte-identical, so every one of them re-resolves to the same bytes. The
  highest genuine live citation is **`:738-739`** (the Stage C options draft v2; STATE.md's highest is
  `:720-724`; the blast-radius record's is `:680-682`). **No live record's citation moves.**
- The 4 colon rows above `:1077` and 5 of the 7 out-of-range rows come from one token-dump line
  (`260916-kht-SUMMARY.md:502`) and are `run_native_ld_panel.py` source-line refs. ⚠ **Corrected
  2026-09-18 (W3):** the remaining **2** out-of-range rows (both `:2030`, from
  `260916-vqp-VERIFICATION.md:312`) are **not** `run_native_ld_panel.py` refs — that line reads
  `` `.planning/osf_deviations.md` | `DECISIONS.md :: DEC-2026-08-17-trsx5-gate-released` | named
  sub-entry + line `:2030` ``, so `:2030` is a **`.planning/DECISIONS.md`** line reference (2632 lines;
  `:2030` is that DEC heading), swept in only because the row also names the ledger. The conclusion is
  unchanged: **none of the 11 is a line in this ledger.** The guard prints them classified.
- **Bare pass** (line references written as plain integers), SCOPED to the two `quick-260917-irg`
  records: **37 rows**, and **every one of them moves**:

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

  ⚠ **These 37 go stale BY DESIGN and are NOT rewritten by this plan** (the repo-path scope is five
  deliverables plus PLAN/SUMMARY). They are plan-time observations inside a CLOSED quick's PLAN and
  SUMMARY, not live pointers; `G13-bare-scope` fails if any bare reference is ever found in a live
  record instead. ⚠ **SCOPE LIMIT, stated rather than hidden:** a bare integer is not mechanically
  distinguishable from a data value, so pass B is pinned to those two files. STATE.md, HANDOFF.json
  and the blast-radius record do carry integers in 1078-1139, and each was read at plan time: they are
  `run_native_ld_panel.py` line refs, not ledger lines.
- Both digests are pinned (`G12-cites-pin`, `G13-bare-pin`), so a citation added later trips the guard
  instead of being silently missed. ⚠ Run `pff_cites.py` **once, in Task 1, before any repo write**,
  and reuse that JSON for every guard run. Re-running it *after* Task 3 will legitimately differ,
  because this PLAN and its SUMMARY add citations of their own. (Neither new bank file names
  `osf_deviations` with a line number — verified at plan time — so the Task 2 commit does not move
  either digest.)

## Enforcers this plan runs (read-only) and their plan-time behaviour in a shared clone at afd1a19

| enforcer | BEFORE | AFTER (files installed) |
|---|---|---|
| `python3 "$U"` (uer guard) | `38/40 PASS`, exit 1 | identical multiset, exit 1 |
| `python3 "$V" --live` (vqq) | `RESULT RED checks=446 parsed=112 table=112 verified=102 c-res=112  reds=['c:c01','c:c02','c:c03','c:c04','c:c18','c:c62','c:c63','c:n02','c:n48','c:n06']`, exit 1 | identical multiset and identical `reds=[…]`, exit 1 |
| `bash "$N" ledger` (u9p append-only) | `RESULT: ALL CHECKS PASSED (section: ledger)`, exit 0 | identical, exit 0 |

## The irg guard goes RED, and exactly five of its checks are supposed to

`irg_guard.py` is **not** a standing repo enforcer — it exists only as embedded text inside the closed
`quick-260917-irg` PLAN. Extracted at plan time (all three md5 markers match) and run against the
post-edit tree with the irg base blob (`9bdcd7d^`, md5 `714454a5b23d979396f1d8c6fc1104d4`), it gives
**`RESULT RED  119/124 PASS`** with FAIL ids exactly:

| irg check | why it is SUPPOSED to be RED now |
|---|---|
| `G06-W1` | its W1 sentence is the stale one D2 replaces |
| `G07-finding1-10d` | §(10d) is no longer byte-identical — D3 adds the scope bullet |
| `G10-courier-status` | the 260917 courier status line is no longer `DRAFTED … NOT SENT` — D4 |
| `G12-census` | the new hunks are outside irg's allowed sites |
| `G05-osf` | irg's numeric allowlist does not know 276 / 7.6 / 255 |

Task 2 re-runs it and requires **that exact set** — so if this edit breaks anything else the irg guard
could see, it is caught rather than excused.

## KNOWN AND DELIBERATELY NOT ACTED ON. Do not fix these; they are reported for Carter.

1. **Both filenames still read `UNSENT`** although both were sent. Kept by Carter's decision because
   other records cite those paths; both files now say so in their own headers, and the 260916 one
   points at the AS-SENT bank.
2. **The 37 irg bare line references go stale** (table above). Not rewritten: repo-path scope.
3. **The 260916 courier still carries the superseded figures in its body** (`:54-55`) and its own
   ⛔ warning naming all five. Both are frozen by D4; S4 points at the warning without restating any
   figure, and the AS-SENT bank contains none of them.
4. **Neither banked correspondence file is byte-verified.** `$CLOSURE` came from a chat paste;
   `$SENTTXT` is a session **scratch** copy of what was sent, not a capture of the reviewer's channel.
   Both headers say so in those words.
5. **`$CLOSURE`'s first line opens "Seth —".** Banked verbatim, not interpreted.
6. **The source of the reviewer's *"a 0.02 mismatch"* figure is UNATTRIBUTED.** The figure was
   reachable from two files committed before his reply (this draft's body at `c93e97b`, and the
   disclosure as it stood there), and the text as sent stated no figure for it. **Which one he read is
   not establishable from this record**, so S4 records it as unattributed rather than guessing. Not
   acted on further: there is nothing in the repo that could settle it, and asking him is a contact
   action no agent takes.

</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight, extract the four embedded scripts, enumerate citations, build in scratch, prove the guard (GREEN + RED + 113 controls, 126/126 ids covered), capture BEFORE state</name>
  <files>(scratch only: $X/**; no repo file is written in this task)</files>
  <action>
Run each numbered step. Any STOP ends the task and the plan, and you report the exact output.

1. PRE-FLIGHT (STOP on any mismatch):
   - `git rev-parse --abbrev-ref HEAD` == `m3-W2-aou-deltas`. Do not check out anything, do not create a worktree.
   - `git status --porcelain --untracked-files=no` prints NOTHING **and** `git status --porcelain --untracked-files=no | wc -l` == 0. Empty output alone is not proof; print the count.
   - `md5sum .planning/osf_deviations.md "$C16" "$C17" "$CLOSURE" "$SENTTXT"` == `6ba5ad5365b64a2482eafea75168b8ae`, `c068559c298a026e19eaabf9d0566c4d`, `a92d9ec21ebb26b39ae8df99696b2abf`, `0b9793244d07f407e07c1e47baff994d`, `502fe68481edeedcf42d53442af6b127`. `wc -l` == 1124 / 91 / 86 / 25 / 77. If any differs: STOP. Do not re-derive the sites.
   - `test -f "$IRG"` (the banked reviewer reply that anchors the "a 0.02 mismatch" quote).
   - **The `$CLOSURE` mtime the bank header states as fact:** `date -r "$CLOSURE" '+%Y-%m-%d %H:%M'`
     == `2026-09-17 18:18`. If it differs, the header's "scratch file written 18:18 EDT" is false:
     STOP and report. (The 18:11 figure is Carter's in-session paste record and is labelled as such;
     nothing in the filesystem can confirm it, which is why the header says which is which.)
   - **The three provenance facts S4 states** (re-verify; any mismatch = STOP, do not re-word S4):
     `git log --format='%h %ad' --date=format:'%m-%d %H:%M' -- "$C16" | tail -1` → `c93e97b 09-16 14:31`
     (and it is that file's ONLY commit: the same command without `| tail -1` prints one line);
     `git show c93e97b:"$C16" | grep -c -- '0.02 mismatch'` → `1`;
     `git show c93e97b:.planning/osf_deviations.md | grep -c -- '1.969'` → `2`.
     ⚠ Use `grep --` or `python3`; the interactive `grep` is a ugrep wrapper. Do not run these under
     `set -e` — `grep -c` exits 1 on a zero count and that is a FINDING, not a thing to swallow.
   - Neither `$BANK` nor `$SENTBANK` exists, and `git ls-files -- "$BANK" "$SENTBANK"` prints nothing.
   - `mkdir -p "$X"`; `cp .planning/osf_deviations.md "$X/base_osf.md"`; `cp "$C16" "$X/base_c16.md"`; `cp "$C17" "$X/base_c17.md"`; re-check all three md5s on the copies.
2. EXTRACT the four embedded scripts from THIS PLAN, and never retype them:
```bash
python3 - "$REPO/$TD/260917-pff-PLAN.md" "$X" <<'PY'
import hashlib, os, re, sys
plan = open(sys.argv[1], encoding="utf-8").read()
pat = re.compile(r"<!-- BEGIN EMBEDDED (\S+) md5=([0-9a-f]{32}) -->\n````python\n(.*?)````\n<!-- END EMBEDDED \1 -->", re.S)
found = pat.findall(plan)
names = sorted(f[0] for f in found)
if names != ["pff_apply.py", "pff_cites.py", "pff_guard.py", "pff_negctl.py"]:
    print("STOP: embedded set", names); sys.exit(2)
for name, pin, body in found:
    b = body.encode("utf-8"); got = hashlib.md5(b).hexdigest()
    if got != pin:
        print("STOP: md5", name, got, "!= pin", pin); sys.exit(2)
    open(os.path.join(sys.argv[2], name), "wb").write(b)
    print("extracted", name, got, len(b), "B")
PY
```
3. ENUMERATE CITATIONS, before any repo write:
   `python3 "$X/pff_cites.py" "$X/cites.json" > "$X/cites.txt"` → exit 0, and the last two lines must be
   `PASS-A 212 rows, 150 files, max-end 2030, digest 5d8e9e715223a3095faa0858c09a8273` and
   `PASS-B 37 rows, 2 files, digest 2f74b0de3f1abae9aa67643d8f9781cb`. Any other digest: STOP and report
   the diff of `$X/cites.txt` against the tables in this plan's context — a new citation into the ledger
   has appeared and the position analysis must be redone. This JSON is the one every later guard run uses.
4. CAPTURE BEFORE (real tree, before any edit):
   - `git status --porcelain --untracked-files=all | LC_ALL=C sort > "$X/status_before.txt"`
   - `python3 "$U" > "$X/enf_before_uer.txt" 2>&1; echo "uer exit=$?" >> "$X/enf_before_uer.txt"`
   - `python3 "$V" --live > "$X/enf_before_vqq.txt" 2>&1; echo "vqq exit=$?" >> "$X/enf_before_vqq.txt"`
   - `bash "$N" ledger > "$X/enf_before_u9p.txt" 2>&1; echo "u9p exit=$?" >> "$X/enf_before_u9p.txt"`
   - ⚠ **The uer guard and the vqq verifier are EXPECTED to exit 1.** Do NOT run these under `set -e`
     and do NOT append `|| true` — that swallows `$?` and makes the BEFORE/AFTER exit-code comparison in
     Task 2 step 5 vacuous. Capture `$?` immediately, exactly as written above.
   - Each file must be non-empty (`test -s`). Record the last two lines of each. Exit codes 1/1/0 and the
     10-element `reds=[…]` list are EXPECTED (see the enforcer table); what matters is BEFORE == AFTER in Task 2.
5. BUILD in scratch: `python3 "$X/pff_apply.py" "$X/base_osf.md" "$X/base_c16.md" "$X/base_c17.md" "$CLOSURE" "$SENTTXT" "$X/out"` → exit 0, prints `applied S1 (osf)` … `applied S5 (c17)`, and the five `wrote` lines carry EXACTLY md5 `22e1b1db105dbacc56c5f8fb3ccc7298` (89846 B, 1139 lines), `d2eb6a02afba146b97d06f185c8c9d96` (4631 B, 47 lines), `be9211e8caa55f921b3b90c7b7c23f0b` (6398 B, 102 lines), `f2251f195382f89f6b0305594c48a300` (7021 B, 106 lines), `764c3d2af5cbb53191699dea7f213d2a` (6195 B, 90 lines). Any other md5 or an exit of 2: STOP.
6. GUARD, GREEN on the build:
```bash
python3 "$X/pff_guard.py" "$X/base_osf.md" "$X/out/osf_deviations.md" "$X/base_c16.md" "$X/out/courier16.md" \
  "$X/base_c17.md" "$X/out/courier17.md" "$X/out/bank.md" "$X/out/sent.md" "$CLOSURE" "$SENTTXT" \
  "$IRG" "$X/cites.json" > "$X/guard_scratch.txt"; echo exit=$?
```
   → exit 0 and last line `RESULT GREEN  396/396 PASS` (126 distinct ids). Check these enumerations in the output against the plan-time values:
   - `census osf: insert base 1078-1077 -> after 1078-1083; replace base 1115-1115 -> after 1121-1127; replace base 1122-1122 -> after 1134-1137`
   - `census c16: replace base 3-3 -> after 3-18` and `census c17: replace base 3-3 -> after 3-7`
   - G01: per literal — osf base==after (`1.652` 0/0, `0.0366` 1/1, `1.564` 0/0, `0.0556` 1/1, `1.969` 2/2), c16 (1/1, 2/2, 1/1, 2/2, 2/2), c17 all 0/0, **bank all 0, sent all 0**.
   - G03: `straddl` at 1029 and 1032 (uer-correction-log) and at 1102, 1103, 1114 ((10e)); `coin` at 1103; `artifact of analytic choice` at 1105; `interchangeab` at 1001 (S7-scoped) and 1103, 1116, 1119; `equally defensible` at 1001 (S7-scoped) and 1103, 1120. Every count base==after.
   - G05: **0** explain-family occurrences in the new osf text, in the new c16 header, in the new c17 header, in the bank provenance header and in the AS-SENT provenance header; `explain-family in bank total 1, inside the verbatim fence 1`; `explain-family in the AS-SENT bank total 3, inside the verbatim fence 3`; and exactly two enumerated `… the disclosure does not say [clustering explains]  NEGATED in context` rows, one `c16` and one `sent`.
   - G09: `predicate` **three times** in the new osf text, all SCOPED — twice in the S1 block
     (`the posted predicate`; `any predicate other than the posted one`) and once in the S3 block
     (`the posted predicate`, from the W4 widening).
   - G10: `G10-D4-c16-noattr` PASS with `x0`; `G10-D4-c16-unattributed`, `G10-D4-c16-committed-src`
     and `G10-D4-c16-qualifier` each PASS at `x1` / `1/1`.
   - G12: `212 rows; 201 stable (end <= 1077); 4 MOVED; 7 out of range`, with all 11 attributed to `260916-kht-SUMMARY.md:502` / `260916-vqp-VERIFICATION.md:312`.
   - G13: 37 bare rows printed with the base -> after mapping of the table in the context section.
7. GUARD, RED on the unedited files (sanity: it can see the old state). Run the same command with `"$X/base_osf.md"`, `"$X/base_c16.md"`, `"$X/base_c17.md"` as BOTH base and after (the two bank files have no "before", so pass them unchanged) → exit 1, last line `RESULT RED  333/383 PASS`, **29 distinct FAIL ids**, covering at least `G08-D2`, `G08-D2-old-gone`, `G09-D3`, `G09-D3-10e-reconciled`, `G10-D4-c16-new`, `G10-D4-c16-pointer`, `G10-D4-c17-new`, `G10-D4-c16-unattributed`, `G10-D4-c16-committed-src`, `G10-D4-c16-qualifier`, `G06-7.6-stated` and the three `G04-census-*-nonempty`. ⚠ `G10-D4-c16-noattr` legitimately **PASSes** here — the clause it forbids is absent from the base too, so its falsifiability comes from control N175, not from this run.
8. NEGATIVE CONTROLS:
```bash
python3 "$X/pff_negctl.py" "$X" "$X/base_osf.md" "$X/out/osf_deviations.md" "$X/base_c16.md" "$X/out/courier16.md" \
  "$X/base_c17.md" "$X/out/courier17.md" "$X/out/bank.md" "$X/out/sent.md" "$CLOSURE" "$SENTTXT" \
  "$IRG" "$X/cites.json" "$X/negwork" > "$X/negctl.txt"; echo exit=$?
```
   → exit 0, and the output must contain **all four** of:
   - `POSITIVE CONTROL (unmutated): 396 checks, FAIL ids = [] -> GREEN`
   - `113` lines ending in `  OK` (`grep -c '  OK$'`), with **no** `INVALID CONTROL` and **no** `MISSING` line
   - `COVERAGE: 126/126 check ids observed RED by at least one control`
   - `NEGCTL RESULT: ALL CONTROLS OBSERVED RED, ALL IDS COVERED`
   Anything less: STOP. A guard whose checks have not been seen failing is not evidence.
  </action>
  <verify>
    <automated>X=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/pff-exec; test "$(md5sum < "$X/out/osf_deviations.md" | cut -d' ' -f1)" = 22e1b1db105dbacc56c5f8fb3ccc7298 && test "$(md5sum < "$X/out/bank.md" | cut -d' ' -f1)" = d2eb6a02afba146b97d06f185c8c9d96 && test "$(md5sum < "$X/out/sent.md" | cut -d' ' -f1)" = be9211e8caa55f921b3b90c7b7c23f0b && test "$(md5sum < "$X/out/courier16.md" | cut -d' ' -f1)" = f2251f195382f89f6b0305594c48a300 && test "$(md5sum < "$X/out/courier17.md" | cut -d' ' -f1)" = 764c3d2af5cbb53191699dea7f213d2a && tail -1 "$X/guard_scratch.txt" | grep -q -- 'RESULT GREEN  396/396 PASS' && grep -q -- 'NEGCTL RESULT: ALL CONTROLS OBSERVED RED, ALL IDS COVERED' "$X/negctl.txt" && grep -q -- 'COVERAGE: 126/126' "$X/negctl.txt" && test "$(grep -c -- '  OK$' "$X/negctl.txt")" -eq 113 && test "$(grep -c -- 'INVALID CONTROL' "$X/negctl.txt")" -eq 0 && grep -q -- 'PASS-A 212 rows, 150 files, max-end 2030, digest 5d8e9e715223a3095faa0858c09a8273' "$X/cites.txt" && test -s "$X/enf_before_vqq.txt" && echo T1-OK</automated>
  </verify>
  <done>Pre-flight passed on five md5 pins and a clean tracked tree. The citation enumeration matches both pinned digests. Four scripts extracted with matching md5s. Scratch build md5s equal the five pins. Guard GREEN 396/396 on the build and RED 333/383 on the unedited files. 113/113 controls observed RED, 126/126 check ids covered, positive control GREEN. BEFORE state captured. No repo file touched.</done>
</task>

<task type="auto">
  <name>Task 2: Install the five files, re-verify on the real tree (md5, guard, irg-guard exact RED set, enforcers BEFORE == AFTER, path scope with a RED probe), commit the five deliverables</name>
  <files>.planning/osf_deviations.md, .planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md, .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md, .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md, .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md</files>
  <action>
1. Re-check the three base md5s on the real paths (a concurrent writer is the failure this catches). If any differs: STOP.
2. INSTALL by copy, never by hand edit:
   `mkdir -p "$TD"`; `cp "$X/out/osf_deviations.md" .planning/osf_deviations.md`; `cp "$X/out/courier16.md" "$C16"`; `cp "$X/out/courier17.md" "$C17"`; `cp "$X/out/bank.md" "$BANK"`; `cp "$X/out/sent.md" "$SENTBANK"`.
   `md5sum` on the five repo paths must equal `22e1b1db…`, `f2251f19…`, `764c3d2a…`, `d2eb6a02…`, `be9211e8…` in full (pins table).
3. GUARD ON THE REAL PATHS (base blobs read from git, so the comparison is against what is committed):
```bash
python3 "$X/pff_guard.py" <(git show HEAD:.planning/osf_deviations.md) .planning/osf_deviations.md \
  <(git show "HEAD:$C16") "$C16" <(git show "HEAD:$C17") "$C17" "$BANK" "$SENTBANK" "$CLOSURE" "$SENTTXT" \
  "$IRG" "$X/cites.json" > "$X/guard_real.txt"; echo exit=$?
```
   → exit 0, `RESULT GREEN  396/396 PASS`. If your shell lacks process substitution, write the three blobs to `$X/` first with `git show … >` and pass those paths.
4. THE irg GUARD, exact RED set. Extract the three irg scripts from the irg PLAN into `$X/irgx` with the same extractor as Task 1 step 2 (its three md5 markers must match), take the irg base blob with `git show 9bdcd7d^:.planning/osf_deviations.md > "$X/irg_base.md"` (md5 must be `714454a5b23d979396f1d8c6fc1104d4`), then:
```bash
python3 "$X/irgx/irg_guard.py" "$X/irg_base.md" .planning/osf_deviations.md "$IRG" "$C17" \
  "$SCR/irg/SETH-REPLY-2026-09-17-as-pasted.txt" "$SCR/irg/SETH-PASTE-3-reply-to-finding2-review-DRAFT.txt" \
  .planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md > "$X/irg_guard_after.txt" 2>&1; echo exit=$?
```
   → exit 1, last line `RESULT RED  119/124 PASS`, and the FAIL id set must be EXACTLY
   `{G05-osf, G06-W1, G07-finding1-10d, G10-courier-status, G12-census}` (one FAIL line each). Any extra
   id: STOP, restore as in step 5, and report it — this edit broke something the irg guard could see that
   it was not supposed to break. ⚠ If `$SCR/irg/*` is gone, print `IRG-GUARD SKIPPED — scratch inputs absent`
   and say so in the hand-back; do NOT record it as a pass.
5. ENFORCERS AFTER: rerun the three commands of Task 1 step 4 into `enf_after_{uer,vqq,u9p}.txt`. For each,
   `diff <(norm_enf "$X/enf_before_X.txt") <(norm_enf "$X/enf_after_X.txt")` must print NOTHING and `echo rc=$?`
   must be 0; the trailing `exit=` lines must be equal; and `grep -oE "reds=\[.*\]" "$X/enf_after_vqq.txt"` must
   be byte-equal to the BEFORE one and to the 10-element list in the enforcer table. If any multiset differs:
   restore with `git checkout -- .planning/osf_deviations.md "$C16" "$C17"` and `rm -- "$BANK" "$SENTBANK"`, then STOP and report the diff.
6. PATH SCOPE: `git status --porcelain --untracked-files=all | LC_ALL=C sort > "$X/status_after.txt"`. Then:
   - `LC_ALL=C comm -23 "$X/status_before.txt" "$X/status_after.txt"` prints NOTHING (nothing vanished).
   - `LC_ALL=C comm -13 "$X/status_before.txt" "$X/status_after.txt"` prints EXACTLY these 5 lines:
     ` M .planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md`
     ` M .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md`
     ` M .planning/osf_deviations.md`
     `?? .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-260916-COURIER-AS-SENT-measurement-result.md`
     `?? .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md`
   - Assert the frozen trees explicitly anyway: `git status --porcelain -- .planning/amendments .planning/STATE.md .planning/HANDOFF.json .planning/DECISIONS.md .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement- src tests | wc -l` == 0.
   - RED CONTROL for this check: `touch src/python/__pff_negctl_probe.py`, recompute `comm -13` → it MUST now show a 6th line `?? src/python/__pff_negctl_probe.py`, and the explicit `wc -l` MUST be 1 (observed RED). Then `rm -- src/python/__pff_negctl_probe.py` and recompute: back to exactly the 5 lines, `wc -l` == 0 (GREEN again). Record both observations.
7. COMMIT (explicit paths only; never `git add -A` or `.` — the tree is shared and multi-terminal):
   - `git add -- .planning/osf_deviations.md "$C16" "$C17" "$BANK" "$SENTBANK"`
   - `git diff --cached --name-only | LC_ALL=C sort` == exactly those 5 paths, sorted. Anything else staged: `git restore --staged` the extra paths and STOP.
   - ```
     git commit -m "docs(quick-260917-pff): bank the reviewer's 2026-09-17 closure and the courier text as sent — all seven points accepted, both objections withdrawn, nothing open" \
       -m "Per Carter D1-D5. Closure banked as received (not byte-verified), and the 260916 courier banked AS SENT from the session scratch copy (also not byte-verified) with the superseded figures absent — the two sentences that carried them were corrected before sending, and neither new file nor either header restates one. osf 2026-09-03 entry, 3 exact-once sites: §(10d) gains ONE scope sentence beside Finding 1 in his own accepted formulation with the denominator attached (all 21 regions scanned = 21 of the 276-region manifest, 7.6% of the panel; defined-but-degraded r survives the POSTED predicate, invisible to the retained NaN-raise by construction; explicit disclaimer over the 255 unscanned regions and over any other predicate) with Finding 1's counts byte-unchanged; §(10e)'s stale 'does not record his acceptance' sentence becomes the closure record; §(10e)'s 'Finding 1's text is unchanged' is reconciled with the new bullet. Both couriers corrected in place to SENT 2026-09-17 under their existing filenames, the 260916 one flagged DRAFT-of-record and pointing at the AS-SENT bank from inside its own status sentence; that header records the reviewer's \"a 0.02 mismatch\" figure as UNATTRIBUTED — the text as sent stated no figure for it, and the figure was reachable from two files committed before his reply (this draft's body at c93e97b, and the disclosure as it stood there), so which source he read is not established by this record and is not guessed. Guard 396/396, 113/113 RED controls, 126/126 ids covered; uer/vqq/u9p enforcers unchanged; irg guard RED on exactly its five expected checks. Finding 2 still NOT ESTABLISHED; disclosure still DRAFTED — NOT POSTED." \
       -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
     ```
   - If the commit fails with `invalid object` / `Error building trees` (GPFS object loss): STOP and report verbatim. Do not retry and do not attempt recovery.
8. POST-COMMIT: `git show --stat --format=%H HEAD` lists exactly the 5 files. `git show HEAD:<path> | md5sum` equals the pin for each of the five. `git status --porcelain --untracked-files=no | wc -l` == 0.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; X=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/pff-exec; TD=.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r; C16=.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md; C17=.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md; BANK=$TD/260917-pff-SETH-CLOSURE-finding2-review-as-received.md; SENTBANK=$TD/260917-pff-260916-COURIER-AS-SENT-measurement-result.md; norm_enf() { grep -E '^(PASS|FAIL|RESULT)' "$1" | sed -E 's/\[[^]]*\]//g; s/:[0-9]+(-[0-9]+)?//g' | LC_ALL=C sort; }; test "$(git show HEAD:.planning/osf_deviations.md | md5sum | cut -d' ' -f1)" = 22e1b1db105dbacc56c5f8fb3ccc7298 && test "$(git show "HEAD:$BANK" | md5sum | cut -d' ' -f1)" = d2eb6a02afba146b97d06f185c8c9d96 && test "$(git show "HEAD:$SENTBANK" | md5sum | cut -d' ' -f1)" = be9211e8caa55f921b3b90c7b7c23f0b && test "$(git show "HEAD:$C16" | md5sum | cut -d' ' -f1)" = f2251f195382f89f6b0305594c48a300 && test "$(git show "HEAD:$C17" | md5sum | cut -d' ' -f1)" = 764c3d2af5cbb53191699dea7f213d2a && test "$(git show --name-only --format= HEAD | wc -l)" -eq 5 && tail -1 "$X/guard_real.txt" | grep -q -- 'RESULT GREEN  396/396 PASS' && for e in uer vqq u9p; do diff <(norm_enf "$X/enf_before_$e.txt") <(norm_enf "$X/enf_after_$e.txt") > /dev/null || exit 1; done && test "$(git status --porcelain -- .planning/amendments .planning/STATE.md .planning/HANDOFF.json .planning/DECISIONS.md .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement- src tests | wc -l)" -eq 0 && echo T2-OK</automated>
  </verify>
  <done>The five files are committed with the pinned md5s. The guard is GREEN 396/396 on the real tree. The irg guard is RED on exactly its five expected checks (or explicitly SKIPPED with its inputs absent, and reported as such). The uer, vqq --live and u9p multisets, exit codes and vqq reds=[…] list are identical before and after. Exactly five status lines are new, and the src/ probe was observed RED then GREEN. Nothing under .planning/amendments/, STATE.md, HANDOFF.json, DECISIONS.md, the irg quick dir, src/ or tests/ moved. The tracked tree is clean. Nothing was posted or sent.</done>
</task>

<task type="auto">
  <name>Task 3: Write the SUMMARY and commit PLAN + SUMMARY</name>
  <files>.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SUMMARY.md, .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-PLAN.md</files>
  <action>
1. Write `$TD/260917-pff-SUMMARY.md` with the Write tool. Frontmatter: task `260917-pff`, branch `m3-W2-aou-deltas`, date 2026-09-17, docs_only true, pushed false, status COMPLETE. Body — every figure MEASURED in Task 1/2, never copied from this plan:
   - the Task 2 commit hash and the five measured md5s;
   - the S1-S5 + BANK + SENTBANK site table with the after-line ranges from the guard census;
   - the guard result line, and the G01 / G03 / G05 / G09 / G12 / G13 enumerations verbatim from `$X/guard_real.txt`;
   - the negctl positive-control line, the `113` OK count, the `COVERAGE: 126/126` line and the `NEGCTL RESULT` line;
   - the three enforcer BEFORE/AFTER last lines and the two `reds=[…]` lists;
   - the irg-guard line (`RESULT RED  119/124 PASS`) and its five FAIL ids, labelled as expected consequences of D2/D3/D4 — or `SKIPPED — scratch inputs absent`;
   - the path-scope observation including the `src/` probe RED then GREEN;
   - the bare-reference staleness table (37 rows) copied from this plan's context, labelled NOT REWRITTEN (repo-path scope);
   - the six KNOWN AND DELIBERATELY NOT ACTED ON items (item 6 = the mismatch figure's source is unattributed);
   - ⚠ one line recording that S3 began as a planner-found contradiction and was APPROVED by Carter on 2026-09-17, and one line recording that D5 (banking the text as sent) was Carter's addition on the same day;
   - one line: "STATE.md / HANDOFF.json / DECISIONS.md not written — orchestrator close-out."
   If the harness REFUSES the SUMMARY write, do not work around it (no heredoc, no python write). Hand the SUMMARY text back, commit nothing in this task, and say so.
2. `git add -- "$TD/260917-pff-PLAN.md" "$TD/260917-pff-SUMMARY.md"`; `git diff --cached --name-only | LC_ALL=C sort` == exactly those 2 paths; then
   `git commit -m "docs(quick-260917-pff): PLAN + SUMMARY — the closure and the courier as sent banked; Finding 1's scope in his accepted formulation; both couriers SENT" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"`.
   Same GPFS STOP rule as Task 2.
3. Hand back: both commit hashes, the five md5s, `RESULT GREEN  396/396 PASS`, `113/113` controls and `126/126` coverage, the enforcer equality, the irg-guard five, the citation result, and the S3/D5 provenance lines. Do not push. Contact nobody. Do not run `pff_cites.py` again after this commit and read a digest change as a regression — this PLAN and SUMMARY legitimately add citations.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; TD=.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r; COMMITTED="$(git show --name-only --format= HEAD | LC_ALL=C sort | tr '\n' ' ')"; if [ "$COMMITTED" = "$TD/260917-pff-PLAN.md $TD/260917-pff-SUMMARY.md " ]; then test -f "$TD/260917-pff-SUMMARY.md" && test "$(git status --porcelain --untracked-files=no | wc -l)" -eq 0 && echo T3-OK-committed; else test ! -f "$TD/260917-pff-SUMMARY.md" && test "$(git status --porcelain --untracked-files=no | wc -l)" -eq 0 && git log --oneline -1 | grep -q 260917-pff && echo T3-OK-handed-back; fi</automated>
  </verify>
  <done>EITHER the PLAN+SUMMARY commit exists and the tracked tree is clean (`T3-OK-committed`), OR the harness refused the SUMMARY write, no SUMMARY file was left behind, the Task 2 commit is still HEAD and the tracked tree is clean, and the SUMMARY text is in the hand-back (`T3-OK-handed-back`). Both are sanctioned; nothing else is. No push, no contact.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| chat paste -> repo | the reviewer's closure arrived via Carter's paste; it is not byte-verifiable against the original |
| session scratch -> repo | the courier text as sent exists only as a scratch copy; it is not a capture of the reviewer's channel |
| agent -> reviewer-facing record | `.planning/osf_deviations.md` is the methods record a referee will read |
| agent -> outside parties | OSF and the reviewer; no agent crosses this boundary in any task |
| this task -> other records | live documents cite the ledger by line number, and three enforcers read it |
| draft -> sent text | the 260916 courier's body is the DRAFT; the text that went out differs and is now banked separately |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-pff-01 | T | the ledger's §(10d)/§(10e) text | mitigate | five input md5 pins; scripted exact-once replacements; guard `G04-census-*` (only the planned sites), `G11-*` frozen regions, `G09-D3-counts-byte`; pinned output md5s |
| T-pff-02 | I | scope promotion in the new Finding 1 sentence (the exact defect the reviewer flagged) | mitigate | `G09-D3-banned` (universal / no geometric predicate / every-or-all-predicates = 0), `G09-D3-predicate` (every `predicate` mention scoped), the explicit 255-region disclaimer, RED controls N121 N122 N125 |
| T-pff-03 | R | claiming more of his closure than he wrote | mitigate | banked verbatim (`G07-D1-fence`); the D2 sentence is restricted to eight pinned phrases; `G08-D2-no-praise` bans praise/motive vocabulary; "seven" is re-counted from the courier, not asserted |
| T-pff-04 | T | restating a superseded figure while correcting a courier that contains five of them | mitigate | `G01-*` per literal per file (no increase in the ledger and couriers; 0 in BOTH banks; 0 in the new c16 header) and `G01-c16-warning` keeps the warning byte-exact |
| T-pff-05 | E | posting / sending | mitigate | no OSF, reviewer, cloud or network action in any task; `G02-status-line` byte-exact; both courier headers and both banks record that the disclosure is still DRAFTED — NOT POSTED |
| T-pff-06 | T | line citations and neighbouring enforcers | mitigate | lines 1-1077 frozen (`G11-head1077`), 201 colon citations re-resolved (`G12-cite-stable`), 4+37 moving references enumerated and scope-checked (`G12-cite-moved-scope`, `G13-bare-scope`), uer/vqq/u9p multisets compared, irg guard's RED set pinned |
| T-pff-07 | I | overclaim that clustering EXPLAINS Finding 2 | mitigate | `G05-*` (13 ids): zero explain-family in all new text and in both provenance headers, each bank's uses proven inside its verbatim fence, the two surface forms enumerated as negated; RED controls N080-N086, N166, N167 |
| T-pff-08 | T | banked correspondence fidelity (closure AND text as sent) | accept | neither can be verified against the original channel; both headers say "not byte-verified" and record their scratch md5/size/lines; `G07-D1-fence` and `G07-D5-fence` prove byte identity to the scratch files |
| T-pff-09 | R | the internal contradiction S1 creates with §(10e)'s "Finding 1's text is unchanged" | mitigate | S3 reconciles it in place, `G09-D3-10e-reconciled` fails if either form is wrong, and S3 was flagged before it was written and APPROVED by Carter 2026-09-17 |
| T-pff-11 | R | attributing the reviewer's figure to a source the record cannot establish (the 2026-09-18 BLOCKER: the previous revision claimed his phrasing "came from the earlier exchange") | mitigate | the clause is deleted and `G10-D4-c16-noattr` fails if it returns; S4 states only the three verifiable facts (`G10-D4-c16-committed-src`) and records the source as unattributed (`G10-D4-c16-unattributed`); the three `git` facts are re-verified in Task 1 pre-flight; RED controls N175-N178 |
| T-pff-12 | R | an unenforced timestamp in banked correspondence (the W1 warning: `18:11 EDT` asserted, `18:18` on disk) | mitigate | both facts stated and labelled by kind; wording pinned by `G07-D1-header` (N103, N104) and the mtime pinned by Task 1 pre-flight |
| T-pff-10 | R | the AS-SENT bank being mistaken for the draft, or vice versa | mitigate | the AS-SENT header names the draft of record by repo path exactly once (`G07-D5-header-draftref`), the draft points at the AS-SENT bank exactly once (`G10-D4-c16-pointer`), and the draft's header says in words that it is the draft and not the text sent (`G10-D4-c16`) |
</threat_model>

<verification>
- `pff_cites.py`: colon digest `5d8e9e715223a3095faa0858c09a8273` (212 rows/150 files), bare digest `2f74b0de3f1abae9aa67643d8f9781cb` (37 rows/2 files).
- `pff_guard.py` GREEN `396/396` (126 distinct check ids) on the scratch build and on the real paths, and RED `333/383` (29 distinct FAIL ids) on the unedited files.
- `pff_negctl.py`: positive control GREEN (396 checks, no FAIL); 113 controls each observed RED on their expected ids, none INVALID; `COVERAGE: 126/126`.
- `irg_guard.py` re-extracted and run: `RESULT RED  119/124 PASS`, FAIL ids exactly `{G05-osf, G06-W1, G07-finding1-10d, G10-courier-status, G12-census}`.
- Enforcers (uer guard, vqq `--live`, u9p ledger): identical line-normalized PASS/FAIL/RESULT multisets, identical exit codes, identical `reds=[…]`.
- Path scope: exactly five new status lines; the `src/` probe observed RED then GREEN; the frozen trees report 0.
- Committed blob md5s equal the pins; tracked tree clean after each commit.
</verification>

<success_criteria>
- The closure is banked as received, and the courier text that actually went out is banked as sent; both headers say they are NOT byte-verified and carry their scratch md5, size and line count.
- The AS-SENT bank contains **none** of the five superseded figures, and neither it nor the draft's header restates one; the draft keeps its own ⛔ warning byte-exact and now says, in words, that it is the draft and where the sent text lives.
- §(10e) no longer denies what it now records: it states, in his own terms and without praise or motive, that he accepted all seven points, withdrew both objections and closed with no open objection, and that nothing further is expected until a new measurement or a posting decision.
- §(10d) carries his accepted formulation of Finding 1's scope with the denominator attached (21 of 276 = 7.6%), says nothing about the 255 unscanned regions or about predicates in general, and leaves Finding 1's counts byte-identical; §(10e)'s stale "Finding 1's text is unchanged" is reconciled rather than left false.
- Both couriers read SENT 2026-09-17 under their existing filenames, and the 260916 one carries its
  epistemic qualifier (`per Carter's record; … banked, not byte-verified, at <AS-SENT path>`) **in the
  status sentence itself**, not one hop away.
- The 260916 header claims nothing about WHERE the reviewer got his *"a 0.02 mismatch"* figure: it
  states that his §3 uses it, that the sent text stated none, that it was reachable from two files
  committed before his reply, and ⛔ that the source is **unattributed**. The clause "came from the
  earlier exchange" appears nowhere.
- The closure bank states **both** time facts (paste recorded in-session 18:11 EDT; scratch file
  written 18:18 EDT), and both are pinned — the wording by `G07-D1-header`, the mtime by pre-flight.
- No superseded literal increases anywhere, nothing says clustering explains Finding 2, and no live line citation moves.
- Finding 2 is still **NOT ESTABLISHED**. The disclosure is still **DRAFTED — NOT POSTED**. Nothing was posted, sent or pushed.
</success_criteria>

<output>
After completion, create `.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SUMMARY.md` (Task 3).
</output>

## EMBEDDED FILES — extract with Task 1 step 2; never retype

<!-- BEGIN EMBEDDED pff_cites.py md5=c5b1f7ff277b06e560530ec0ef09249f -->
````python
#!/usr/bin/env python3
"""pff_cites.py - enumerate every line-number citation of .planning/osf_deviations.md.

usage: pff_cites.py OUT_JSON
Two passes, both mechanical:
  A) COLON pass over every TRACKED file that names the ledger (`git grep -l`, index-backed):
     `osf_deviations.md:N[-M]` plus bare `:N[-M]` on a line that also names the ledger.
     This pass is a SUPERSET (the bare-on-same-line rule also catches other files' line refs),
     which is the safe direction: it over-reports rather than under-reports.
  B) BARE pass, SCOPED to the two quick-260917-irg records, which cite the ledger's (10e) lines
     as plain integers ("`straddl` at 1096"). Range-limited to 1078-1139, i.e. the lines this
     edit can move. ⚠ SCOPE LIMIT, stated rather than hidden: a bare integer elsewhere in the
     repo is NOT mechanically distinguishable from a data value (STATE.md, HANDOFF.json and the
     blast-radius record all carry 1078-1139 integers that are source-line refs into
     run_native_ld_panel.py, not ledger lines), so pass B is pinned to those two files only.
"""
import hashlib, json, re, subprocess, sys

PAT_FULL = re.compile(r"osf_deviations\.md[`'\"]?\s*[`'\"]?:(\d+)(?:-(\d+))?")
PAT_BARE = re.compile(r"(?<![\w.])`?:(\d+)(?:-(\d+))?`?")
IRG = ".planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/"
BARE_FILES = [IRG + "260917-irg-PLAN.md", IRG + "260917-irg-SUMMARY.md"]
PAT_INT = re.compile(r"(?<![\w.:/-])(1(?:0[7-9]\d|1[0-3]\d))(?![\w.%])")


def main():
    files = subprocess.run(["git", "grep", "-l", "-F", "osf_deviations"],
                           capture_output=True, text=True).stdout.split("\n")
    files = [f for f in files if f]
    if not files:
        print("STOP: git grep found no file naming osf_deviations (empty output is suspect)")
        return 2
    rows = []
    for f in files:
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for i, ln in enumerate(txt.split("\n"), 1):
            seen = set()
            for m in PAT_FULL.finditer(ln):
                a = int(m.group(1)); b = int(m.group(2) or m.group(1)); seen.add(a)
                rows.append([f, i, "explicit", a, b])
            if "osf_deviations" in ln:
                for m in PAT_BARE.finditer(ln):
                    a = int(m.group(1)); b = int(m.group(2) or m.group(1))
                    if a in seen:
                        continue
                    rows.append([f, i, "bare", a, b])
    bare = []
    for f in BARE_FILES:
        for i, ln in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
            for m in PAT_INT.finditer(ln):
                bare.append([f, i, int(m.group(1)), ln.strip()[:70]])
    rows.sort(); bare.sort()
    dg = hashlib.md5(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    dgb = hashlib.md5(json.dumps(bare, sort_keys=True).encode()).hexdigest()
    for r in rows:
        print("A %-93s L%-5d %-9s :%d-%d" % tuple(r))
    for r in bare:
        print("B %-93s L%-5d %d   | %s" % tuple(r))
    print("PASS-A %d rows, %d files, max-end %d, digest %s" % (len(rows), len(files),
                                                               max(r[4] for r in rows), dg))
    print("PASS-B %d rows, %d files, digest %s" % (len(bare), len(BARE_FILES), dgb))
    if len(sys.argv) > 1:
        json.dump({"rows": rows, "digest": dg, "bare": bare, "bare_digest": dgb},
                  open(sys.argv[1], "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED pff_cites.py -->

<!-- BEGIN EMBEDDED pff_apply.py md5=6205baadd25f4968787f2b2004b0ccbb -->
````python
#!/usr/bin/env python3
"""pff_apply.py - quick-260917-pff. Builds the five output files from pinned inputs.

Every new text block is carried here VERBATIM, one source line per list item. Each
replacement is EXACT-ONCE: the old text must occur exactly once in the working text at
the moment it is applied, or the script exits 2 and writes nothing.

usage: pff_apply.py OSF_IN C16_IN C17_IN CLOSURE_TXT SENT_TXT OUT_DIR
writes OUT_DIR/{osf_deviations.md,bank.md,sent.md,courier16.md,courier17.md} (never inside the repo)
"""
import hashlib, os, sys

PIN_OSF = "6ba5ad5365b64a2482eafea75168b8ae"
PIN_C16 = "c068559c298a026e19eaabf9d0566c4d"
PIN_C17 = "a92d9ec21ebb26b39ae8df99696b2abf"
PIN_CLOSURE = "0b9793244d07f407e07c1e47baff994d"
PIN_SENT = "502fe68481edeedcf42d53442af6b127"
FENCE = "`" * 4
TDREL = ".planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/"
BANKREL = TDREL + "260917-pff-SETH-CLOSURE-finding2-review-as-received.md"
SENTREL = TDREL + "260917-pff-260916-COURIER-AS-SENT-measurement-result.md"
IRGREL = (".planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/"
          "260917-irg-SETH-REPLY-finding2-review-as-received.md")
C16REL = ".planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md"
C17REL = ".planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md"


def J(*lines):
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- osf_deviations.md
OSF_EDITS = [
    # ---- S1 (D3) - INSERT the Finding 1 scope bullet into (10d), after base :1077 ----
    ("S1",
     J("  a design effect cannot touch it. It has now survived **five reviewers, two adjudication rounds,",
       "  and this measurement.**",
       "- **Finding 3's status is unchanged:** **no association DETECTED** on the definitional axis, and"),
     J("  a design effect cannot touch it. It has now survived **five reviewers, two adjudication rounds,",
       "  and this measurement.**",
       "- ⚠ **SCOPE OF FINDING 1 — the reviewer's own formulation, accepted 2026-09-17 (§(10e)).** In **all",
       "  21 regions scanned** — **21 of the 276**-region ancestry-resolved manifest (§(9)), **7.6%** of the",
       "  panel — a post-filter residual of **defined-but-degraded `r`** survives the **posted** predicate",
       "  and is **invisible to the retained NaN-raise by construction**, because those rows are defined and",
       "  so never produce a NaN. ⛔ **Stated at that scope deliberately: this says nothing about the 255",
       "  regions NOT scanned, and nothing about any predicate other than the posted one.**",
       "- **Finding 3's status is unchanged:** **no association DETECTED** on the definitional axis, and")),
    # ---- S2 (D2) - (10e) INTERCHANGEABLE bullet: replace the stale last sentence, base :1115 ----
    ("S2",
     J("  analyses stay reported. **This entry does not record his acceptance of the scoping decided here.**"),
     J("  analyses stay reported. ⭐ **He ACCEPTED this scoping on 2026-09-17**, in a closure banked as",
       "  received (**not byte-verified**) at",
       "  `" + BANKREL + "`.",
       "  He accepted **all seven points** of our reply and **WITHDREW BOTH of his objections** — the pooled",
       "  design-effect share, and this post-hoc window selector, which he named as his own threshold",
       "  objection applied to the selector. **He closed with no open objection**, and nothing further is",
       "  expected from him until there is a new measurement or a posting decision.")),
    # ---- S3 - (10e)'s "Finding 1's text is unchanged" is made FALSE by S1; reconciled here.
    #      Planner-found internal contradiction, APPROVED by Carter 2026-09-17.
    ("S3",
     J("- **Finding 1's text is unchanged.**"),
     J("- **Finding 1's counts and its claim are unchanged.** ⚠ On the same date, a **scope sentence** in",
       "  the reviewer's own accepted formulation was added beside it in §(10d) (quick `260917-pff`): it",
       "  states the scope of what was measured — 21 of 21 scanned regions, the **posted** predicate, and the",
       "  retained **NaN-raise** — and changes none of the counts.")),
]

# ---------------------------------------------------------------- courier status lines (D4)
C16_EDITS = [
    ("S4",
     J("**Status:** DRAFTED 2026-09-14, **NOT SENT**. No agent contacts Seth — Carter sends it."),
     J("**Status:** ✅ **SENT 2026-09-17, in the CORRECTED form** — per Carter's record; the text as sent is",
       "banked, not byte-verified, at",
       "`" + SENTREL + "`.",
       "Drafted 2026-09-14; sending was Carter's decision, recorded here 2026-09-17. ⚠ **The body below is",
       "the DRAFT, not the text sent:** before it went out, the **superseded figures were removed from the",
       "two sentences that carried them**, and they are **NOT restated in this header** — the ⛔ warning",
       "below is kept verbatim and still binds. **This file stays the DRAFT OF RECORD**, and the text as",
       "sent is banked at the path above.",
       "⚠ **The courier-vs-table mismatch.** The reviewer's reply (**§3**, banked at",
       "`" + IRGREL + "`)",
       "characterises that discrepancy with a figure — \"a 0.02 mismatch\"; **the sent text stated no figure",
       "for it**. That figure was reachable from two files already committed before his reply: this draft's",
       "own body, committed in `c93e97b` on 2026-09-16, which states it verbatim, and the disclosure as it",
       "stood at that commit, which carried the superseded value it is computed against. ⛔ **Which source",
       "he used is NOT established by this record; it is recorded here as unattributed, not attributed.**",
       "⚠ **The filename still reads `UNSENT`** — kept deliberately, because other records cite this path.")),
]

C17_EDITS = [
    ("S5",
     J("**Status:** DRAFTED 2026-09-17, **NOT SENT**. No agent contacts Seth — Carter sends it."),
     J("**Status:** ✅ **SENT 2026-09-17.** Drafted 2026-09-17; sending was Carter's decision, recorded here",
       "2026-09-17. **The reviewer's CLOSURE is the reply to it** — all seven points accepted, both of his",
       "objections withdrawn, no open objection — banked as received (**not byte-verified**) at",
       "`" + BANKREL + "`.",
       "⚠ **The filename still reads `UNSENT`** — kept deliberately, because other records cite this path.")),
]

BANK_HEADER = J(
    "# Reviewer closure 2026-09-17 — Finding 2 review CLOSED OUT (AS RECEIVED, ⛔ NOT BYTE-VERIFIED)",
    "",
    "**Received:** 2026-09-17 — paste recorded in-session 18:11 EDT; scratch file written 18:18 EDT.",
    "Pasted by Carter into the session. **Not byte-verified** against the original message; chat",
    "rendering may have altered blank lines or other whitespace.",
    "**Scratch source:** `SETH-CLOSURE-2026-09-17-as-pasted.txt`, md5 `0b9793244d07f407e07c1e47baff994d`,",
    "3168 B, 25 lines. The fenced block below is that file byte-for-byte, first line included.",
    "**Replies to:** `" + C17REL + "` (SENT",
    "2026-09-17; that filename is stale by decision, because other records cite the path).",
    "**What it records:** all seven points of that courier accepted; **BOTH** of his objections withdrawn",
    "(his pooled design-effect share, and his \"pick the better-corrected window\" selector, which he names",
    "as his own threshold objection applied to the selector); **no open objection**; and nothing further",
    "from him until there is a new measurement or a posting decision.",
    "**Recorded in:** `.planning/osf_deviations.md`, the 2026-09-03 entry — §(10d) (Finding 1's scope) and",
    "§(10e)'s \"INTERCHANGEABLE\" bullet (quick `260917-pff`).",
    "⛔ This is correspondence. Its figures and wording are NOT a source for the record: the shares it",
    "restates are deliberately absent from the disclosure, which is still **DRAFTED — NOT POSTED**.",
    "",
    "---",
    "")

SENT_HEADER = J(
    "# Courier to Seth — the pairs-per-deletion measurement result, ✅ AS SENT (⛔ NOT BYTE-VERIFIED)",
    "",
    "**Sent:** 2026-09-17, by Carter. **Sending was Carter's decision**, recorded here 2026-09-17.",
    "**This is the text as SENT**, not a draft. ⚠ **Not byte-verified** against what was pasted into the",
    "reviewer's channel: it is banked from a session **scratch** copy, and chat rendering may have altered",
    "blank lines or other whitespace.",
    "**Scratch source:** `SETH-PASTE-1b-measurement-result-SEND.txt`, md5",
    "`502fe68481edeedcf42d53442af6b127`, 4907 B, 77 lines. The fenced block below is that file",
    "byte-for-byte, first line included.",
    "**Draft of record:** `" + C16REL + "`",
    "(drafted 2026-09-14; that filename is stale by decision, because other records cite the path).",
    "**What changed before sending:** the **superseded figures were removed from the two sentences that",
    "carried them**, so **this file contains none of them**, and none is restated in this header. The draft",
    "of record still carries them in its body, behind its own ⛔ warning.",
    "**His reply to this:**",
    "`" + IRGREL + "`.",
    "**His closure of the exchange:** `260917-pff-SETH-CLOSURE-finding2-review-as-received.md`, in this",
    "directory.",
    "⛔ This is correspondence. It is not a source for the record, and the disclosure it describes is still",
    "**DRAFTED — NOT POSTED**.",
    "",
    "---",
    "")


def md5b(b):
    return hashlib.md5(b).hexdigest()


def apply_edits(text, edits, tag):
    for sid, old, new in edits:
        n = text.count(old)
        if n != 1:
            print("STOP: %s old text occurs %d times in %s (want exactly 1)" % (sid, n, tag))
            return None
        text = text.replace(old, new, 1)
        print("applied %s (%s)" % (sid, tag))
    for sid, old, new in edits:
        if text.count(new) != 1:
            print("STOP: %s new text occurs %d times after all edits (want 1)" % (sid, text.count(new)))
            return None
    return text


def main():
    if len(sys.argv) != 7:
        print(__doc__)
        return 2
    osf_p, c16_p, c17_p, clo_p, snt_p, out = sys.argv[1:]
    osf_b = open(osf_p, "rb").read()
    c16_b = open(c16_p, "rb").read()
    c17_b = open(c17_p, "rb").read()
    clo_b = open(clo_p, "rb").read()
    snt_b = open(snt_p, "rb").read()
    for name, b, pin in (("osf", osf_b, PIN_OSF), ("c16", c16_b, PIN_C16), ("c17", c17_b, PIN_C17),
                         ("closure", clo_b, PIN_CLOSURE), ("sent", snt_b, PIN_SENT)):
        if md5b(b) != pin:
            print("STOP: input %s md5 %s != pin %s" % (name, md5b(b), pin))
            return 2
    d = os.path.abspath(out)
    while True:
        if os.path.isdir(os.path.join(d, ".git")):
            print("STOP: OUT_DIR is inside a git work tree (%s); outputs go to scratch only" % d)
            return 2
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    osf_t = apply_edits(osf_b.decode("utf-8"), OSF_EDITS, "osf")
    c16_t = apply_edits(c16_b.decode("utf-8"), C16_EDITS, "c16")
    c17_t = apply_edits(c17_b.decode("utf-8"), C17_EDITS, "c17")
    if osf_t is None or c16_t is None or c17_t is None:
        return 2
    clo_t = clo_b.decode("utf-8")
    snt_t = snt_b.decode("utf-8")
    for name, body in (("closure", clo_t), ("sent", snt_t)):
        if FENCE in body or not body.endswith("\n"):
            print("STOP: %s contains a 4-backtick fence or lacks a final newline" % name)
            return 2
    bank = BANK_HEADER + FENCE + "\n" + clo_t + FENCE + "\n"
    sent = SENT_HEADER + FENCE + "\n" + snt_t + FENCE + "\n"
    os.makedirs(out, exist_ok=True)
    for fn, body in (("osf_deviations.md", osf_t), ("bank.md", bank), ("sent.md", sent),
                     ("courier16.md", c16_t), ("courier17.md", c17_t)):
        p = os.path.join(out, fn)
        bb = body.encode("utf-8")
        with open(p, "wb") as fh:
            fh.write(bb)
        print("wrote %s md5 %s %d B %d lines" % (p, md5b(bb), len(bb), body.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED pff_apply.py -->

<!-- BEGIN EMBEDDED pff_guard.py md5=986586410b0f91f851ce96b5c6ca502d -->
````python
#!/usr/bin/env python3
"""pff_guard.py - quick-260917-pff standing-rule guard. stdlib only; reads, never writes.

usage: pff_guard.py BASE_OSF AFTER_OSF BASE_C16 AFTER_C16 BASE_C17 AFTER_C17 BANK SENT CLOSURE
                    SENT_TXT IRG_REPLY CITES_JSON
exit 0 = every check PASS; exit 1 = any FAIL. One PASS/FAIL line per check id, plus the
enumerations the standing rules require (banned literals, framing phrases, the explain family,
the `predicate` census, the citation re-resolution).

Phrase and literal checks run on NORMALIZED text: markdown * _ ` removed, whitespace runs
collapsed to one space, lowercased. A literal line-grep is blind to bolded or line-wrapped
phrases; every check here is proven able to fail by pff_negctl.py.
"""
import difflib, hashlib, json, re, sys

BANNED = ["1.652", "0.0366", "1.564", "0.0556", "1.969"]
ENTRY_HEAD = "## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure"
STATUS_LINE = ("- **Status:** DRAFTED — NOT POSTED; placement and posting are Carter's. No agent has "
               "contacted")
UER_ANCHOR = "an earlier draft of this table estimated the pooled rate once from all 21 regions"
S7_ANCHOR = "report the evidence, not which side of a threshold it fell on"
E10_HEAD = "#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated"
D10_HEAD = "#### (10d) WHAT IS UNCHANGED — stated explicitly, so the retraction is not over-read"
A10_HEAD = "#### (10a) NEW FINDING — WITHIN-WINDOW CLUSTERING IS REAL, MEASURED, AND STRONG"
C16_WARNING = "⛔ Do NOT send the superseded figures `1.652/0.0366`, `1.564/0.0556`, `1.969`."
# S4's mismatch paragraph: what it may NOT claim, and the four things it must claim instead.
C16_NOATTR = "came from the earlier exchange"
C16_UNATTR = ("which source he used is not established by this record; it is recorded here as"
              " unattributed, not attributed.")
C16_SRC_DRAFT = "committed in c93e97b on 2026-09-16, which states it verbatim"
C16_SRC_LEDGER = ("the disclosure as it stood at that commit, which carried the superseded value it is"
                  " computed against")
SENTREL = ("- .planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/"
           "260917-pff-260916-COURIER-AS-SENT-measurement-result.md")[2:]
# base line numbers (1-based) this edit may replace, and base lines AFTER which it may insert
OSF_ALLOWED_REPLACED = {1115, 1122}
OSF_ALLOWED_INSERT_AFTER = {1077}
POSITION_FROZEN_UPTO = 1077     # every live line citation into this ledger ends at or below :739
CITES_PIN_A = "5d8e9e715223a3095faa0858c09a8273"   # colon pass, 212 rows, measured at plan time
CITES_PIN_B = "2f74b0de3f1abae9aa67643d8f9781cb"   # bare pass, 37 rows, measured at plan time
FINDING1_COUNT_LINES = (1073, 1077)   # byte-frozen: Finding 1's counts
DISPOSITIONS = [  # word-for-word disposition sentences that must survive (normalized)
    "heterogeneity — measured, but not established.",
    "is recorded below as not established.",
    "so the between-region heterogeneity is not established.",
    "finding 2 is not established (recorded 2026-09-08).",
    "#### (10b) finding 2 is not established",
    "the between-region heterogeneity in post-filter rate is not established.",
]
PRAISE = ["gracious", "commendab", "to his credit", "generous", "impressive", "admirab", "rightly",
          "because he wanted", "in order to", "motivat", "good faith", "intellectual honesty"]
EXPLAIN_RE = r"explain|explanat|accounts? for|reproduc"
POSITIVE_EXPLAIN = (r"clustering\s+(alone\s+)?(explains|accounts for|reproduces)"
                    r"|explained by\s+(the\s+)?(within-window\s+)?clustering")


def norm(s):
    s = re.sub(r"[*_`]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def unquote(s):
    return re.sub(r"(?m)^> ?", "", s)


def md5(b):
    return hashlib.md5(b).hexdigest()


def line_of(text, char_idx):
    return text.count("\n", 0, char_idx) + 1


def norm_hits(text, phrase, first_line=1):
    """normalized substring hits -> 1-based line numbers in `text`, offset by first_line-1."""
    out, idx, prev_sp = [], [], False
    for i, ch in enumerate(text):
        if ch in "*_`":
            continue
        if ch.isspace():
            if prev_sp:
                continue
            out.append(" "); idx.append(i); prev_sp = True
        else:
            out.append(ch.lower()); idx.append(i); prev_sp = False
    n = "".join(out); p = norm(phrase); res = []; k = n.find(p)
    while k >= 0:
        res.append(line_of(text, idx[k]) + first_line - 1)
        k = n.find(p, k + 1)
    return res


def paragraph_span(lines, anchor):
    spans, start = [], None
    for i, ln in enumerate(lines + [""], start=1):
        if ln.strip() == "":
            if start is not None:
                spans.append((start, i - 1)); start = None
        elif start is None:
            start = i
    return [s for s in spans if norm(unquote("\n".join(lines[s[0] - 1:s[1]]))).find(norm(anchor)) >= 0]


def extract_fence(body):
    ls = body.split("\n")
    f = [i for i, ln in enumerate(ls) if ln == "`" * 4]
    if len(f) != 2:
        return None, len(f)
    return "\n".join(ls[f[0] + 1:f[1]]) + "\n", 2


def census(BL, AL, allowed_repl, allowed_ins, R, cid, label):
    sm = difflib.SequenceMatcher(None, BL, AL, autojunk=False)
    parts, changed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        parts.append("%s base %d-%d -> after %d-%d" % (tag, i1 + 1, i2, j1 + 1, j2))
        if tag in ("replace", "delete"):
            ok = all((k + 1) in allowed_repl for k in range(i1, i2))
        else:
            ok = i1 in allowed_ins
        R.append((cid, ok, "%s base %d-%d -> after %d-%d" % (tag, i1 + 1, i2, j1 + 1, j2)))
        if tag in ("replace", "insert"):
            changed.append((j1 + 1, "\n".join(AL[j1:j2])))
    print("  census %s: %s" % (label, "; ".join(parts)))
    R.append((cid + "-nonempty", bool(parts), "%s: %d changed hunk(s)" % (label, len(parts))))
    return changed


NUM_RE = re.compile(r"(?<![\w.:/])\d[\d,]*(?:\.\d+)?(?![\w])")
STRUCT_RE = [
    r"\.planning/[^\s`)]+", r"\b20\d\d-\d\d-\d\d\b", r"\b26\d{4}-[a-z0-9]{3}\b", r"\b\d\d:\d\d\b",
    r"§\(\d+[a-e]?\)", r"§\d+", r"\(\d+[a-e]\)", r"\b[0-9a-f]{32}\b", r"finding \d",
    r"quick `?26\d{4}-[a-z0-9]{3}`?", r"(?m)^\s*\d+\. ",
]


def classify_numbers(text, allowed, label, R, cid):
    t = text.lower()
    for pat in STRUCT_RE:
        t = re.sub(pat, " ", t)
    bad = []
    for m in NUM_RE.finditer(t):
        tok = m.group(0).replace(",", "")
        if not allowed.get(tok, False):
            bad.append(tok)
    R.append((cid, not bad, "%s: unreconciled numeric tokens %s" % (label, sorted(set(bad))) if bad
              else "%s: every numeric token reconciled" % label))


def explain_enum(blocks, label, R, cid, allow_quoted=False):
    print("  enumeration %s (explain family in %s):" % (cid, label))
    n = 0
    for first, blk in blocks:
        bn = norm(unquote(blk))
        for m in re.finditer(EXPLAIN_RE, bn):
            n += 1
            pre = bn[max(0, m.start() - 70):m.start()]
            qs = [i for i, ch in enumerate(bn) if ch == '"']
            quoted = allow_quoted and any(qs[k] < m.start() and m.end() <= qs[k + 1]
                                          for k in range(0, len(qs) - 1, 2))
            label_neg = pre.endswith("not robustly distinguishable from a clustering-only ")
            negated = re.search(r"without showing (that )?it $", pre) is not None
            kind = ("hypothesis-label (negated)" if label_neg else "negated" if negated
                    else "quoted attribution" if quoted else "NOT NEGATED")
            print("    block@%-5d ...%s[%s]  %s" % (first, pre[-45:], m.group(0), kind))
            R.append((cid, label_neg or negated or quoted,
                      "block@%d %r -> %s" % (first, pre[-40:] + m.group(0), kind)))
    print("    -> %d occurrence(s) in %s" % (n, label))
    return n


C16REL = ".planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md"


def run(base_p, after_p, b16_p, a16_p, b17_p, a17_p, bank_p, sent_p, clo_p, snt_p, irg_p, cites_p):
    R = []
    rd = lambda p: open(p, encoding="utf-8").read()
    base, after = rd(base_p), rd(after_p)
    b16, a16 = rd(b16_p), rd(a16_p)
    b17, a17 = rd(b17_p), rd(a17_p)
    bank = rd(bank_p)
    sentf = rd(sent_p)
    clo_b = open(clo_p, "rb").read(); clo = clo_b.decode("utf-8")
    snt_b = open(snt_p, "rb").read(); snt = snt_b.decode("utf-8")
    irg = rd(irg_p)
    cites = json.load(open(cites_p))
    BL, AL = base.split("\n"), after.split("\n")
    B16, A16 = b16.split("\n"), a16.split("\n")
    B17, A17 = b17.split("\n"), a17.split("\n")
    base_n, after_n = norm(unquote(base)), norm(unquote(after))

    # ---- G00 anchors ----
    if base.count(ENTRY_HEAD) != 1 or after.count(ENTRY_HEAD) != 1:
        R.append(("G00-entry-head", False, "entry heading count base %d after %d (want 1/1)"
                  % (base.count(ENTRY_HEAD), after.count(ENTRY_HEAD))))
        return R
    R.append(("G00-entry-head", True, "2026-09-03 entry heading present once in base and after"))
    for nm, txt, head in (("10a", after, A10_HEAD), ("10d", after, D10_HEAD), ("10e", after, E10_HEAD)):
        R.append(("G00-head-" + nm, txt.count(head) == 1, "%s heading present once" % nm))

    # ---- G01 banned superseded literals (normalized, prefix-sensitive) ----
    print("  enumeration G01 (the five superseded literals, per file, normalized):")
    for lit in BANNED:
        for nm, b, a in (("osf", base, after), ("c16", b16, a16), ("c17", b17, a17)):
            cb, ca = norm(b).count(lit), norm(a).count(lit)
            print("    %-7s %-7s base %d  after %d" % (lit, nm, cb, ca))
            R.append(("G01-%s-%s" % (nm, lit), ca <= cb, "%s %s base %d after %d" % (nm, lit, cb, ca)))
        for nm, body in (("bank", bank), ("sent", sentf)):
            c = norm(body).count(lit)
            print("    %-7s %-7s count %d (want 0)" % (lit, nm, c))
            R.append(("G01-%s-%s" % (nm, lit), c == 0, "%s %s count %d" % (nm, lit, c)))
    # the c16 warning that NAMES the literals must survive byte-exact
    R.append(("G01-c16-warning", a16.count(C16_WARNING) == b16.count(C16_WARNING) == 1,
              "c16 'do not send the superseded figures' warning present once, byte-exact"))
    # and the NEW c16 header must not restate any of them
    c16_new = "\n".join(A16[2:18])
    R.append(("G01-c16-newheader", all(norm(c16_new).count(l) == 0 for l in BANNED),
              "new c16 status header restates none of the five literals"))

    # ---- G02 survival: status line, DRAFTED — NOT POSTED, NOT ESTABLISHED, dispositions ----
    R.append(("G02-status-line", STATUS_LINE in after and after.count(STATUS_LINE) == base.count(STATUS_LINE) == 1,
              "osf status line present once, byte-exact"))
    for ph in ("drafted — not posted", "not established"):
        cb, ca = norm(base).count(ph), norm(after).count(ph)
        R.append(("G02-osf-" + ph.split()[0], ca >= cb, "osf %r base %d after %d" % (ph, cb, ca)))
    for nm, b, a in (("c16", b16, a16), ("c17", b17, a17)):
        cb, ca = norm(b).count("drafted — not posted"), norm(a).count("drafted — not posted")
        R.append(("G02-%s-drafted" % nm, ca >= cb, "%s 'drafted — not posted' base %d after %d" % (nm, cb, ca)))
    for s in DISPOSITIONS:
        R.append(("G02-disposition", s in after_n, "word-for-word: %r" % s))
    sf0 = extract_fence(sentf)[0] or ""
    R.append(("G02-sent-drafted", norm(sf0).count("drafted — not posted") >= 1,
              "the text AS SENT (inside the fence, not the header) says 'drafted — not posted' x%d"
              " (want >= 1)" % norm(sf0).count("drafted — not posted")))

    # ---- G03 framing phrases: counts UNCHANGED, and every occurrence enumerated ----
    a_entry0 = after.index(ENTRY_HEAD)
    a_entry, a_first = after[a_entry0:], line_of(after, a_entry0)
    uer = paragraph_span(AL, UER_ANCHOR)
    s7 = paragraph_span(AL, S7_ANCHOR)
    e10 = [i + 1 for i, ln in enumerate(AL) if ln == E10_HEAD]
    R.append(("G03-regions", len(uer) == 1 and len(s7) == 1 and len(e10) == 1,
              "uer paragraph %s, S7 paragraph %s, (10e) heading line %s" % (uer, s7, e10)))
    uspan = uer[0] if len(uer) == 1 else (0, -1)
    sspan = s7[0] if len(s7) == 1 else (0, -1)
    e10s = e10[0] if len(e10) == 1 else 10 ** 9
    print("  enumeration G03 (framing phrases in the 2026-09-03 entry, AFTER):")
    for key, ph in (("straddl", "straddl"), ("coin", "coin"), ("artifact", "artifact of analytic choice"),
                    ("interchangeab", "interchangeab"), ("equallydef", "equally defensible")):
        cb, ca = norm(base).count(ph), norm(after).count(ph)
        R.append(("G03-count-" + key, ca == cb, "%r base %d after %d (must be equal)" % (ph, cb, ca)))
        for n in norm_hits(a_entry, ph, a_first):
            where = ("uer-correction-log" if uspan[0] <= n <= uspan[1]
                     else "S7-scoped" if sspan[0] <= n <= sspan[1]
                     else "(10e)" if n >= e10s else "ELSEWHERE")
            print("    %-28s line %4d  %s" % (ph, n, where))
            R.append(("G03-region-" + key, where != "ELSEWHERE", "%r at line %d -> %s" % (ph, n, where)))

    # ---- G04 census of changed hunks (only the planned sites) ----
    ch_osf = census(BL, AL, OSF_ALLOWED_REPLACED, OSF_ALLOWED_INSERT_AFTER, R, "G04-census-osf", "osf")
    ch_16 = census(B16, A16, {3}, set(), R, "G04-census-c16", "c16")
    ch_17 = census(B17, A17, {3}, set(), R, "G04-census-c17", "c17")

    # ---- G05 nothing says or implies clustering EXPLAINS Finding 2 ----
    n_osf = explain_enum(ch_osf, "new osf text", R, "G05-explain-osf")
    n_c16 = explain_enum(ch_16, "new c16 header", R, "G05-explain-c16")
    n_c17 = explain_enum(ch_17, "new c17 header", R, "G05-explain-c17")
    bank_fence, nbf = extract_fence(bank)
    bank_head = bank.split("`" * 4)[0]
    sent_fence, nsf = extract_fence(sentf)
    sent_head = sentf.split("`" * 4)[0]
    n_bh = explain_enum([(1, bank_head)], "bank provenance header", R, "G05-explain-bankhead")
    n_sh = explain_enum([(1, sent_head)], "AS-SENT provenance header", R, "G05-explain-senthead")
    # the bank's received correspondence DOES use the family; it must all sit INSIDE the fence
    tot = len(re.findall(EXPLAIN_RE, norm(bank)))
    infence = len(re.findall(EXPLAIN_RE, norm(bank_fence or "")))
    print("  enumeration G05-bank-fence: explain-family in bank total %d, inside the verbatim fence %d"
          % (tot, infence))
    R.append(("G05-bank-fence-scope", tot == infence and infence > 0,
              "every explain-family use in the bank (%d) is inside the verbatim fence (%d), i.e. received"
              " correspondence, not a statement of the record" % (tot, infence)))
    stot = len(re.findall(EXPLAIN_RE, norm(sentf)))
    sin = len(re.findall(EXPLAIN_RE, norm(sent_fence or "")))
    print("  enumeration G05-sent-fence: explain-family in the AS-SENT bank total %d, inside the"
          " verbatim fence %d" % (stot, sin))
    R.append(("G05-sent-fence-scope", stot == sin and sin > 0,
              "every explain-family use in the AS-SENT bank (%d) is inside the verbatim fence (%d), i.e."
              " correspondence as sent, not a statement of the record" % (stot, sin)))
    print("  enumeration G05-positive ('clustering explains' surface forms, with context):")
    for nm, b, a in (("osf", base_n, after_n), ("c16", norm(b16), norm(a16)),
                     ("c17", norm(b17), norm(a17)), ("sent", None, norm(sentf))):
        cb = len(re.findall(POSITIVE_EXPLAIN, b)) if b is not None else -1
        ca = len(re.findall(POSITIVE_EXPLAIN, a))
        for m in re.finditer(POSITIVE_EXPLAIN, a):
            pre = a[max(0, m.start() - 60):m.start()]
            neg = bool(re.search(r"(does not say|do not say|not|neither|never)\s[^.]{0,40}$", pre))
            print("    %-5s ...%s[%s]  %s" % (nm, pre[-45:], m.group(0),
                                              "NEGATED in context" if neg else "NOT NEGATED"))
            R.append(("G05-positive-ctx", neg, "%s ...%s%s" % (nm, pre[-40:], m.group(0))))
        if nm == "sent":
            # the AS-SENT bank has no "base": the falsifiable property is that every positive
            # surface form sits INSIDE the verbatim fence, i.e. it is the correspondence itself.
            pin_ = len(re.findall(POSITIVE_EXPLAIN, norm(sent_fence or "")))
            R.append(("G05-positive-sent", ca == pin_ and pin_ > 0,
                      "AS-SENT positive 'clustering explains' surface forms: %d in the file, %d inside"
                      " the verbatim fence (must be equal and non-zero)" % (ca, pin_)))
        else:
            R.append(("G05-positive-" + nm, ca <= cb,
                      "%s positive 'clustering explains' surface forms base %d after %d (no increase)"
                      % (nm, cb, ca)))
    for nm, blocks in (("osf", ch_osf), ("c16", ch_16), ("c17", ch_17)):
        c = sum(len(re.findall(POSITIVE_EXPLAIN, norm(b))) for _, b in blocks)
        R.append(("G05-positive-new-" + nm, c == 0,
                  "new %s text carries %d positive 'clustering explains' form(s) (want 0)" % (nm, c)))
    R.append(("G05-positive-bankhead", len(re.findall(POSITIVE_EXPLAIN, norm(bank_head))) == 0,
              "bank header carries no positive 'clustering explains' form"))
    R.append(("G05-positive-senthead", len(re.findall(POSITIVE_EXPLAIN, norm(sent_head))) == 0,
              "AS-SENT header carries no positive 'clustering explains' form"))
    R.append(("G05-enum-nonvacuous",
              infence > 0 and sin > 0,
              "the enumerations ran (osf %d, c16 %d, c17 %d, bank header %d, AS-SENT header %d,"
              " bank fence %d, AS-SENT fence %d)" % (n_osf, n_c16, n_c17, n_bh, n_sh, infence, sin)))

    # ---- G06 numeric reconciliation of every changed block ----
    rec = {
        "21": "21 regions" in base_n,
        "276": "regionidsselected = 276" in base_n,
        "2521": "3767/2521" in base_n,
        "1.99": "observed 1.99" in base_n,
    }
    der = {
        "7.6": "%.1f" % (100 * 21 / 276) == "7.6",
        "7.61": "%.2f" % (100 * 21 / 276) == "7.61",
        "255": (276 - 21) == 255,
        "seven": len([l for l in (extract_fence(a17)[0] or "").split("\n") if re.match(r"^\d+\. ", l)]) == 7,
    }
    R.append(("G06-record-anchors", all(rec.values()),
              "record anchors missing: %s" % [k for k, v in rec.items() if not v]))
    R.append(("G06-derived", all(der.values()),
              "derived recompute mismatches: %s" % [k for k, v in der.items() if not v]))
    R.append(("G06-7.6-stated", after_n.count("7.6%") == 1 and after_n.count("7.61%") == 0
              and after_n.count("7.7%") == 0,
              "21/276 = %.2f%% is stated to one decimal as 7.6%% exactly once, and 7.61%%/7.7%% are absent"
              % (100 * 21 / 276)))
    osf_allowed = {"21": True, "276": True, "7.6": True, "255": True}
    for first, blk in ch_osf:
        classify_numbers(blk, osf_allowed, "osf block@%d" % first, R, "G06-num-osf")
    c16_allowed = {"0.02": "0.02 mismatch" in norm(irg)}
    for first, blk in ch_16:
        classify_numbers(blk, c16_allowed, "c16 block@%d" % first, R, "G06-num-c16")
    for first, blk in ch_17:
        classify_numbers(blk, {}, "c17 block@%d" % first, R, "G06-num-c17")
    classify_numbers(bank_head, {"3168": len(clo_b) == 3168, "25": clo.count("\n") == 25},
                     "bank header", R, "G06-num-bank")
    classify_numbers(sent_head, {"4907": len(snt_b) == 4907, "77": snt.count("\n") == 77},
                     "AS-SENT header", R, "G06-num-sent")

    # ---- G07 D1: the bank file ----
    R.append(("G07-D1-fence", nbf == 2 and bank_fence is not None
              and bank_fence.encode("utf-8") == clo_b,
              "exactly 2 fence lines; fenced body == closure bytes (%d B)" % len(clo_b)))
    hn = norm(bank_head)
    for ph in ("not byte-verified", "pasted by carter into the session",
               "paste recorded in-session 18:11 edt", "scratch file written 18:18 edt",
               "all seven points of that courier accepted", "both of his objections withdrawn",
               "no open objection", "drafted — not posted"):
        R.append(("G07-D1-header", ph in hn, "bank header carries %r" % ph))
    R.append(("G07-D1-header-pins", md5(clo_b) in bank
              and ("%d B, %d lines" % (len(clo_b), clo.count("\n"))) in bank,
              "bank header carries md5 %s and '%d B, %d lines'" % (md5(clo_b), len(clo_b), clo.count("\n"))))

    # ---- G07-D5: the AS-SENT bank (the courier text that actually went out) ----
    R.append(("G07-D5-fence", nsf == 2 and sent_fence is not None
              and sent_fence.encode("utf-8") == snt_b,
              "exactly 2 fence lines; fenced body == the scratch SEND bytes (%d B)" % len(snt_b)))
    shn = norm(sent_head)
    for ph in ("this is the text as sent", "sent: 2026-09-17, by carter",
               "sending was carter's decision", "not byte-verified",
               "banked from a session scratch copy",
               "superseded figures were removed from the two sentences that carried them",
               "this file contains none of them", "draft of record:", "drafted — not posted"):
        R.append(("G07-D5-header", ph in shn, "AS-SENT header carries %r" % ph))
    R.append(("G07-D5-header-draftref", sentf.count(C16REL) == 1,
              "the AS-SENT header names the draft of record exactly once by repo path"))
    R.append(("G07-D5-header-pins", md5(snt_b) in sentf
              and ("%d B, %d lines" % (len(snt_b), snt.count("\n"))) in sentf,
              "AS-SENT header carries md5 %s and '%d B, %d lines'"
              % (md5(snt_b), len(snt_b), snt.count("\n"))))

    # ---- G08 D2: the (10e) closure record ----
    for ph, k in (("he accepted this scoping on 2026-09-17", 1),
                  ("he accepted all seven points of our reply", 1),
                  ("withdrew both of his objections", 1),
                  ("the pooled design-effect share", 1),
                  ("this post-hoc window selector", 1),
                  ("his own threshold objection applied to the selector", 1),
                  ("he closed with no open objection", 1),
                  ("nothing further is expected from him until there is a new measurement or a posting"
                   " decision", 1)):
        R.append(("G08-D2", after_n.count(ph) == k, "%r x%d (want %d)" % (ph, after_n.count(ph), k)))
    R.append(("G08-D2-old-gone",
              "this entry does not record his acceptance of the scoping decided here" not in after_n,
              "the superseded sentence is absent from the after text"))
    d2 = [b for f, b in ch_osf if "ACCEPTED this scoping" in b]
    R.append(("G08-D2-block", len(d2) == 1, "the D2 hunk is exactly one changed block (found %d)" % len(d2)))
    # these four ALWAYS emit: if the D2 block is missing they FAIL rather than silently vanishing
    blk = d2[0] if len(d2) == 1 else ""
    sents = [s for s in re.split(r"(?<=[.!?]) ", norm(blk).split("analyses stay reported. ")[-1]) if s.strip()]
    R.append(("G08-D2-sentences", len(d2) == 1 and 2 <= len(sents) <= 3,
              "the replacement is %d sentence(s) (want 2-3): %s" % (len(sents), [s[:40] for s in sents])))
    bad = [w for w in PRAISE if w in norm(blk)]
    R.append(("G08-D2-no-praise", len(d2) == 1 and not bad,
              "praise/motive vocabulary in the D2 block: %s" % bad))
    R.append(("G08-D2-bankref",
              "260917-pff-SETH-CLOSURE-finding2-review-as-received.md" in blk,
              "the D2 block cites the bank file by repo path"))
    R.append(("G08-D2-no-new-stats", len(d2) == 1 and not re.findall(r"(?<![\w.:/-])\d+\.\d+", blk),
              "the D2 block introduces no decimal statistic: %s"
              % re.findall(r"(?<![\w.:/-])\d+\.\d+", blk)))

    # ---- G09 D3: the Finding 1 scope sentence ----
    for ph, k in (("scope of finding 1 — the reviewer's own formulation, accepted 2026-09-17", 1),
                  ("in all 21 regions scanned", 1),
                  ("21 of the 276-region ancestry-resolved manifest", 1),
                  ("a post-filter residual of defined-but-degraded r survives the posted predicate", 1),
                  ("invisible to the retained nan-raise by construction", 1),
                  ("this says nothing about the 255 regions not scanned", 1),
                  ("nothing about any predicate other than the posted one", 1)):
        R.append(("G09-D3", after_n.count(ph) == k, "%r x%d (want %d)" % (ph, after_n.count(ph), k)))
    for ph in ("universal", "no geometric predicate", "every predicate", "any possible predicate",
               "all possible predicates", "all predicates", "predicates in general"):
        cb, ca = norm(base).count(ph), norm(after).count(ph)
        R.append(("G09-D3-banned", ca == cb == 0, "%r base %d after %d (want 0/0)" % (ph, cb, ca)))
    for ph in ("no predicate",):   # legitimate existing text ("NO PREDICATE CHANGE"): must not grow
        cb, ca = norm(base).count(ph), norm(after).count(ph)
        R.append(("G09-D3-frozen-phrase", ca == cb, "%r base %d after %d (want equal)" % (ph, cb, ca)))
    print("  enumeration G09 ('predicate' in the new osf text):")
    npred = 0
    for first, blk in ch_osf:
        for n in norm_hits(blk, "predicate", first):
            seg = norm(blk); i = seg.find("predicate")
            while i >= 0:
                ctx = seg[max(0, i - 30):i + 45]
                ok = ("the posted predicate" in ctx) or ("any predicate other than the posted one" in ctx)
                print("    block@%-5d ...%s  %s" % (first, ctx, "SCOPED" if ok else "UNSCOPED"))
                R.append(("G09-D3-predicate", ok, "block@%d ...%s" % (first, ctx)))
                npred += 1
                i = seg.find("predicate", i + 1)
            break
    R.append(("G09-D3-predicate-nonvacuous", npred >= 2,
              "'predicate' occurs %d time(s) in the new osf text (want >= 2, both scoped)" % npred))
    b1, b2 = FINDING1_COUNT_LINES
    R.append(("G09-D3-counts-byte", BL[b1 - 1:b2] == AL[b1 - 1:b2],
              "Finding 1's count lines :%d-%d byte-identical" % (b1, b2)))
    for fig in ("2560 pre / 534 post of 3094 (17.26%)", "2047 pre / 474 post of 2521 (18.80%)",
                "21/21 regions carry tail rows", "0 regions have zero post"):
        R.append(("G09-D3-counts-text", after_n.count(fig) == base_n.count(fig) == 1,
                  "Finding 1 figure %r present once, unchanged" % fig))
    R.append(("G09-D3-10e-reconciled",
              after_n.count("finding 1's text is unchanged.") == 0
              and after_n.count("finding 1's counts and its claim are unchanged.") == 1,
              "(10e)'s stale 'Finding 1's text is unchanged' is reconciled with the new §(10d) bullet"))

    # ---- G10 D4: both courier status lines ----
    old_status = "**Status:** DRAFTED 20%s, **NOT SENT**. No agent contacts Seth — Carter sends it."
    for nm, b, a, day in (("c16", b16, a16, "26-09-14"), ("c17", b17, a17, "26-09-17")):
        R.append(("G10-D4-%s-old" % nm, b.count(old_status % day) == 1 and (old_status % day) not in a,
                  "%s old status line present in base, absent after" % nm))
    R.append(("G10-D4-c16-new",
              a16.split("\n")[2] == "**Status:** ✅ **SENT 2026-09-17, in the CORRECTED form** — per "
                                    "Carter's record; the text as sent is",
              "c16 line 3 is the new SENT status line"))
    R.append(("G10-D4-c17-new",
              a17.split("\n")[2] == "**Status:** ✅ **SENT 2026-09-17.** Drafted 2026-09-17; sending was "
                                    "Carter's decision, recorded here",
              "c17 line 3 is the new SENT status line"))
    for ph in ("the body below is the draft, not the text sent",
               "superseded figures were removed from the two sentences that carried them",
               "not restated in this header", "the sent text stated no figure for it",
               "this file stays the draft of record, and the text as sent is banked at the path above",
               "the filename still reads unsent"):
        R.append(("G10-D4-c16", norm(a16).count(ph) == 1, "c16 %r x%d (want 1)" % (ph, norm(a16).count(ph))))
    c17_new = norm("\n".join(A17[2:7]))
    for ph in ("sent 2026-09-17", "the reviewer's closure is the reply to it",
               "all seven points accepted, both of his objections withdrawn, no open objection",
               "not byte-verified", "the filename still reads unsent"):
        R.append(("G10-D4-c17", c17_new.count(ph) == 1,
                  "c17 new header %r x%d (want 1)" % (ph, c17_new.count(ph))))
    nh16 = norm(a16)
    R.append(("G10-D4-c16-noattr", C16_NOATTR not in nh16,
              "the attributing clause %r is absent from c16 (x%d, want 0)"
              % (C16_NOATTR, nh16.count(C16_NOATTR))))
    R.append(("G10-D4-c16-unattributed", nh16.count(C16_UNATTR) == 1,
              "c16 records the figure's source as UNATTRIBUTED x%d (want 1)" % nh16.count(C16_UNATTR)))
    R.append(("G10-D4-c16-committed-src",
              nh16.count(C16_SRC_DRAFT) == 1 and nh16.count(C16_SRC_LEDGER) == 1,
              "c16 names both sources committed before the reply (draft body x%d, disclosure-at-that-"
              "commit x%d; want 1/1)" % (nh16.count(C16_SRC_DRAFT), nh16.count(C16_SRC_LEDGER))))
    qual = ("sent 2026-09-17, in the corrected form — per carter's record; the text as sent is banked,"
            " not byte-verified, at " + SENTREL.lower())
    R.append(("G10-D4-c16-qualifier", nh16.count(qual) == 1,
              "the 'per Carter's record / banked, not byte-verified, at <AS-SENT path>' qualifier sits"
              " inside the Status sentence itself x%d (want 1)" % nh16.count(qual)))
    R.append(("G10-D4-mismatch-anchor", "a 0.02 mismatch" in norm(irg) and '"a 0.02 mismatch"' in a16,
              "the quoted figure is present in the banked reviewer reply and quoted in c16"))
    ir = irg.split("\n")
    hit = [i for i, l in enumerate(ir) if "0.02 mismatch" in l]
    sec = None
    if len(hit) == 1:
        for j in range(hit[0], -1, -1):
            m = re.match(r"^\d+\. §(\d)", ir[j])
            if m:
                sec = m.group(1); break
    R.append(("G10-D4-mismatch-source", len(hit) == 1 and sec == "3" and "§3" in a16,
              "in the banked reply the figure sits under section §%s (one hit at L%s) and c16 names §3"
              % (sec, hit[0] + 1 if len(hit) == 1 else hit)))
    R.append(("G10-D4-c16-pointer", a16.count(SENTREL) == 1
              and "not banked in this repo" not in norm(a16),
              "c16's new header points at the AS-SENT bank exactly once and no longer says the sent"
              " form is unbanked"))
    R.append(("G10-D4-rest-byte-c16", B16[:2] == A16[:2] and B16[3:] == A16[18:],
              "c16 unchanged outside line 3 (head 1-2 and tail 4-end byte-identical)"))
    R.append(("G10-D4-rest-byte-c17", B17[:2] == A17[:2] and B17[3:] == A17[7:],
              "c17 unchanged outside line 3 (head 1-2 and tail 4-end byte-identical)"))

    # ---- G11 frozen regions ----
    R.append(("G11-head1077", BL[:POSITION_FROZEN_UPTO] == AL[:POSITION_FROZEN_UPTO],
              "osf lines 1-%d byte-identical" % POSITION_FROZEN_UPTO))
    def slice_between(txt, head, nxt):
        i, j = txt.find(head), txt.find(nxt)
        return None if (i < 0 or j < 0 or j < i) else txt[i:j]
    for nm, head, nxt in (("10a", A10_HEAD, "#### (10b)"), ("10b", "#### (10b)", "#### (10c)"),
                          ("10c", "#### (10c)", D10_HEAD)):
        bs, as_ = slice_between(base, head, nxt), slice_between(after, head, nxt)
        R.append(("G11-" + nm, bs is not None and bs == as_,
                  "§(%s) byte-identical (base %s B, after %s B)"
                  % (nm, len(bs) if bs is not None else "MISSING",
                     len(as_) if as_ is not None else "MISSING")))
    bu = paragraph_span(BL, UER_ANCHOR)
    R.append(("G11-uer-note", len(bu) == 1 and len(uer) == 1
              and BL[bu[0][0] - 1:bu[0][1]] == AL[uspan[0] - 1:uspan[1]],
              "the frozen 260908-uer correction note is byte-identical"))
    R.append(("G11-table", [l for l in BL if l.startswith("| ")] == [l for l in AL if l.startswith("| ")],
              "every table row byte-identical"))

    # ---- G12 line-position safety: re-resolve every enumerated citation ----
    def shift(n):
        if n <= 1077:
            return n
        if n <= 1114:
            return n + 6
        if n == 1115:
            return None      # replaced
        if n <= 1121:
            return n + 12
        if n == 1122:
            return None      # replaced
        return n + 15
    rows = cites["rows"]
    R.append(("G12-cites-pin", cites["digest"] == CITES_PIN_A and len(rows) == 212,
              "colon pass: %d rows (want 212), digest %s (want %s)"
              % (len(rows), cites["digest"], CITES_PIN_A)))
    stable, moved, oor = [], [], []
    for f, ln, kind, a, b in rows:
        if b > len(BL) - 1:
            oor.append((f, ln, a, b)); continue
        if b <= POSITION_FROZEN_UPTO:
            ok = BL[a - 1:b] == AL[a - 1:b]
            R.append(("G12-cite-stable", ok, "%s:L%d :%d-%d resolves to identical bytes" % (f, ln, a, b)))
            stable.append((f, ln, a, b))
        else:
            moved.append((f, ln, a, b, shift(a), shift(b)))
    print("  citation re-resolution: %d rows; %d stable (end <= %d); %d MOVED; %d out of range"
          % (len(rows), len(stable), POSITION_FROZEN_UPTO, len(moved), len(oor)))
    for f, ln, a, b, na, nb in moved:
        print("    MOVED  %-88s L%-5d :%d-%d -> :%s-%s" % (f, ln, a, b, na, nb))
    for f, ln, a, b in oor:
        print("    OUT-OF-RANGE (not an osf line) %-70s L%-5d :%d-%d" % (f, ln, a, b))
    # every MOVED citation must be inside a quick-260917-irg planning record (a plan-time observation),
    # never a live operational record
    LIVE = (".planning/STATE.md", ".planning/HANDOFF.json", ".planning/DECISIONS.md",
            ".planning/debug/", ".planning/amendments/")
    for f, ln, a, b, na, nb in moved:
        live = f.startswith(LIVE) and "260917-irg" not in f
        R.append(("G12-cite-moved-scope", not live,
                  "%s:L%d :%d-%d moved -> :%s-%s (%s)" % (f, ln, a, b, na, nb,
                                                          "LIVE RECORD" if live else "irg plan-time record")))
    R.append(("G12-moved-nonvacuous", len(moved) > 0,
              "%d citation(s) move; each is enumerated above with its re-resolved range" % len(moved)))

    # ---- G13 the BARE pass (irg plan-time line references into (10e)) ----
    bare = cites["bare"]
    R.append(("G13-bare-pin", cites["bare_digest"] == CITES_PIN_B and len(bare) == 37,
              "bare pass: %d rows (want 37), digest %s (want %s)"
              % (len(bare), cites["bare_digest"], CITES_PIN_B)))
    print("  bare-reference re-resolution (quick-260917-irg plan-time records; these go STALE by"
          " design and are NOT rewritten by this plan):")
    live_bare = []
    for f, ln, v, ctx in bare:
        nv = shift(v)
        print("    %-24s L%-5d %d -> %s   | %s" % (f.split("/")[-1], ln, v, nv, ctx))
        if not f.startswith(".planning/quick/260917-irg"):
            live_bare.append((f, ln, v))
    R.append(("G13-bare-scope", not live_bare,
              "every bare reference is inside a quick-260917-irg record; live records: %s" % live_bare))
    R.append(("G13-bare-nonvacuous", len(bare) > 0 and all(shift(v) != v for _, _, v, _ in bare),
              "%d bare references, every one of them moves (none is silently unaffected)" % len(bare)))
    return R


def main():
    if len(sys.argv) != 13:
        print(__doc__)
        return 2
    R = run(*sys.argv[1:])
    fails = [r for r in R if not r[1]]
    print()
    for cid, ok, detail in R:
        print("%s  %-26s %s" % ("PASS" if ok else "FAIL", cid, detail))
    print("\nRESULT %s  %d/%d PASS" % ("GREEN" if not fails else "RED", len(R) - len(fails), len(R)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED pff_guard.py -->

<!-- BEGIN EMBEDDED pff_negctl.py md5=939e28ab18f4d7d66b904d901d4e5c97 -->
````python
#!/usr/bin/env python3
"""pff_negctl.py - quick-260917-pff. Proves every pff_guard.py check id can go RED.

usage: pff_negctl.py GUARD_DIR BASE_OSF AFTER_OSF BASE_C16 AFTER_C16 BASE_C17 AFTER_C17 BANK SENT
                     CLOSURE SENT_TXT IRG_REPLY CITES_JSON WORK_DIR
Positive control first (unmutated -> all PASS), then each mutation must (a) change its target
exactly once and (b) turn EVERY expected check id RED. Finally, COVERAGE: every check id the
guard emits on the clean build must appear in at least one control's observed-RED set, or be
listed in UNFALSIFIABLE with a reason. exit 0 only if all of that holds.
WORK_DIR must be outside the repo (scratch).
"""
import copy, io, contextlib, json, os, sys

GUARD_DIR = sys.argv[1]
sys.path.insert(0, GUARD_DIR)
import pff_guard as G  # noqa: E402

(base_p, after_p, b16_p, a16_p, b17_p, a17_p, bank_p, sent_p, clo_p, snt_p, irg_p, cites_p,
 work) = sys.argv[2:15]
rd = lambda p: open(p, encoding="utf-8").read()
BASE0, A0 = rd(base_p), rd(after_p)
B160, A160 = rd(b16_p), rd(a16_p)
B170, A170 = rd(b17_p), rd(a17_p)
BANK0 = rd(bank_p)
SENT0 = rd(sent_p)
CIT0 = json.load(open(cites_p))

# Nothing here is UNFALSIFIABLE. If a future edit adds a check with no control, the COVERAGE
# gate below fails and names it, rather than letting it pass vacuously.
UNFALSIFIABLE = {}

LIT = ["1.652", "0.0366", "1.564", "0.0556", "1.969"]

# (id, target, old, new, expected RED ids)
CONTROLS = [
    ("N001", "osf", "## 2026-09-03 — AFR native-panel", "## 2026-09-03 — AFR native panel",
     ["G00-entry-head"]),
    ("N002", "osf", "#### (10a) NEW FINDING — WITHIN-WINDOW", "#### (10a) NEW FINDINGS — WITHIN-WINDOW",
     ["G00-head-10a", "G11-10a"]),
    ("N003", "osf", "#### (10d) WHAT IS UNCHANGED —", "#### (10d) WHAT IS UNCHANGED:",
     ["G00-head-10d", "G11-10c"]),
    ("N004", "osf", "#### (10e) REVIEWER RESPONSE 2026-09-17", "#### (10e) REVIEWER RESPONSE, 2026-09-17",
     ["G00-head-10e", "G03-regions"]),
]
# G01: one control per literal per file (osf/c16 body/c17/bank), plus the c16 header and warning
for lit in LIT:
    CONTROLS.append(("N01" + lit.replace(".", ""), "osf",
                     "  so never produce a NaN.", "  so never produce a NaN (%s)." % lit,
                     ["G01-osf-" + lit, "G06-num-osf"]))
    CONTROLS.append(("N02" + lit.replace(".", ""), "c16",
                     "\nAll of the above is in the disclosure",
                     "\n(%s)\nAll of the above is in the disclosure" % lit,
                     ["G01-c16-" + lit, "G10-D4-rest-byte-c16", "G04-census-c16"]))
    CONTROLS.append(("N03" + lit.replace(".", ""), "c17",
                     "\nThe disclosure stays DRAFTED", "\n%s\nThe disclosure stays DRAFTED" % lit,
                     ["G01-c17-" + lit, "G10-D4-rest-byte-c17", "G04-census-c17"]))
    CONTROLS.append(("N04" + lit.replace(".", ""), "bank",
                     "\n**Received:**", "\n%s\n**Received:**" % lit, ["G01-bank-" + lit]))
CONTROLS += [
    ("N050", "c16", "⛔ Do NOT send the superseded figures", "⛔ Do not send the superseded figures",
     ["G01-c16-warning", "G10-D4-rest-byte-c16", "G04-census-c16"]),
    ("N051", "c16", "kept verbatim and still binds.", "kept verbatim and still binds (1.652).",
     ["G01-c16-newheader", "G01-c16-1.652", "G06-num-c16"]),
    ("N052", "osf", "- **Status:** DRAFTED — NOT POSTED;", "- **Status:** DRAFTED — POSTED;",
     ["G02-status-line"]),
    ("N053", "base", "**Finding 2 — between-region heterogeneity in the POST-filter rate — is recorded below as",
     "**Finding 2 — NOT ESTABLISHED, NOT ESTABLISHED — is recorded below as", ["G02-osf-not"]),
    ("N054", "base", "- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** A reviewer response is",
     "- ⛔ **The status is unchanged: DRAFTED — NOT POSTED. DRAFTED — NOT POSTED.** A reviewer response is",
     ["G02-osf-drafted"]),
    ("N055", "base16", "**Uses the CORRECTED Rao-Scott table**",
     "**DRAFTED — NOT POSTED.** **Uses the CORRECTED Rao-Scott table**", ["G02-c16-drafted"]),
    ("N056", "base17", "**Disclosure status:** still DRAFTED — NOT POSTED.",
     "**Disclosure status:** still DRAFTED — NOT POSTED. DRAFTED — NOT POSTED.", ["G02-c17-drafted"]),
    ("N057", "osf", "> The between-region heterogeneity in POST-filter rate is **NOT ESTABLISHED**.",
     "> The between-region heterogeneity in POST-filter rate is **ESTABLISHED**.", ["G02-disposition"]),
    # G03: each framing phrase planted OUTSIDE its allowed region (in the new (10d) bullet)
    ("N060", "osf", "  so never produce a NaN.", "  so never produce a NaN; they straddle nothing.",
     ["G03-count-straddl", "G03-region-straddl"]),
    ("N061", "osf", "  so never produce a NaN.", "  so never produce a NaN, not a coin.",
     ["G03-count-coin", "G03-region-coin"]),
    ("N062", "osf", "  so never produce a NaN.",
     "  so never produce a NaN; no artifact of analytic choice here.",
     ["G03-count-artifact", "G03-region-artifact"]),
    ("N063", "osf", "  so never produce a NaN.", "  so never produce a NaN; the two are interchangeable.",
     ["G03-count-interchangeab", "G03-region-interchangeab"]),
    ("N064", "osf", "  so never produce a NaN.", "  so never produce a NaN; both are equally defensible.",
     ["G03-count-equallydef", "G03-region-equallydef"]),
    ("N065", "osf", "An earlier draft of this table estimated the pooled rate once from all 21 regions",
     "An earlier draft of this table estimated the pooled rate once from all 21 sub-regions",
     ["G03-regions", "G11-uer-note"]),
    # G04 census + G11/G12 position freezes
    ("N070", "osf", "  primary; ridge λ∈{0.001,0.01,0.1} robustness); fully-NaN-row → drop; raw-panel NaN-raise",
     "  primary; ridge λ∈{0.001,0.01,0.1} robustness); fully NaN-row → drop; raw-panel NaN-raise",
     ["G04-census-osf", "G11-head1077", "G12-cite-stable"]),
    ("N071", "identity-osf", "", "", ["G04-census-osf-nonempty"]),
    ("N072", "identity-c16", "", "", ["G04-census-c16-nonempty"]),
    ("N073", "identity-c17", "", "", ["G04-census-c17-nonempty"]),
    # G05 explain family
    ("N080", "osf", "  so never produce a NaN.",
     "  so never produce a NaN. Clustering explains the dispersion.",
     ["G05-positive-osf", "G05-positive-new-osf"]),
    ("N081", "c16", "kept verbatim and still binds.",
     "kept verbatim and still binds; clustering explains it.",
     ["G05-positive-c16", "G05-positive-new-c16", "G05-explain-c16"]),
    ("N082", "c17", "objections withdrawn, no open objection",
     "objections withdrawn; clustering explains it; no open objection",
     ["G05-positive-c17", "G05-positive-new-c17"]),
    ("N083", "c16", "not say clustering explains it, and neither do I.",
     "now says clustering explains it. And so do I.", ["G05-positive-ctx"]),
    ("N084", "bank", "⛔ This is correspondence.",
     "⛔ Clustering explains it. This is correspondence.",
     ["G05-positive-bankhead", "G05-bank-fence-scope"]),
    ("N085", "bank", "⛔ This is correspondence.", "⛔ This reproduces correspondence.",
     ["G05-bank-fence-scope"]),
    ("N086", "bank", "Reproduced your figures:", "Restated your figures:",
     ["G05-enum-nonvacuous", "G05-bank-fence-scope", "G07-D1-fence"]),
    # G06 numbers
    ("N090", "osf", "manifest (§(9)), **7.6%** of the", "manifest (§(9)), **7.61%** of the",
     ["G06-7.6-stated", "G06-num-osf"]),
    ("N091", "c17", "\n7. FINDING 1 — agreed, it is the result.", "\n7b. FINDING 1 — agreed, it is the result.",
     ["G06-derived", "G10-D4-rest-byte-c17", "G04-census-c17"]),
    ("N092", "bank", "3168 B, 25 lines.", "3168 B, 25 lines, 12 paragraphs.", ["G06-num-bank"]),
    ("N093", "c16", "\"a 0.02 mismatch\"", "\"a 0.03 mismatch\"",
     ["G06-num-c16", "G10-D4-mismatch-anchor"]),
    ("N094", "c17", "recorded here\n2026-09-17.", "recorded here\n2026-09-17, 3 days on.", ["G06-num-c17"]),
    ("N095", "osf", "**21 of the 276**-region", "**21 of the 277**-region", ["G06-num-osf", "G09-D3"]),
    ("N096", "base", "- `region_ids_selected = 276` is the ancestry-resolved MANIFEST size",
     "- `region_ids_chosen = 276` is the ancestry-resolved MANIFEST size",
     ["G06-record-anchors", "G11-head1077", "G12-cite-stable"]),
    # G07 the bank file
    ("N100", "bank", "Seth — all seven accepted.", "Seth — all 7 accepted.", ["G07-D1-fence"]),
    ("N101", "bank", "Pasted by Carter into the session", "Pasted into the session", ["G07-D1-header"]),
    ("N102", "bank", "`0b9793244d07f407e07c1e47baff994d`", "`0b9793244d07f407e07c1e47baff994e`",
     ["G07-D1-header-pins"]),
    # G08 D2
    ("N110", "osf", "**WITHDREW BOTH of his objections**", "**WITHDREW ONE of his objections**", ["G08-D2"]),
    ("N111", "osf", "  expected from him until there is a new measurement or a posting decision.",
     "  expected from him until there is a new measurement or a posting decision. This entry does not"
     " record his acceptance of the scoping decided here.", ["G08-D2-old-gone", "G08-D2-sentences"]),
    ("N112", "osf", "  analyses stay reported. ⭐ **He ACCEPTED this scoping on 2026-09-17**",
     "  analyses stay reported. ⭐ **He agreed to this scoping on 2026-09-17**",
     ["G08-D2-block", "G08-D2", "G08-D2-no-praise", "G08-D2-bankref", "G08-D2-no-new-stats",
      "G08-D2-sentences"]),
    ("N113", "osf", "  objection applied to the selector. **He closed",
     "  objection applied to the selector. To his credit. **He closed",
     ["G08-D2-no-praise", "G08-D2-sentences"]),
    ("N114", "osf", "260917-pff-SETH-CLOSURE-finding2-review-as-received.md`.\n  He accepted",
     "260917-pff-SETH-CLOSURE-finding-2-review-as-received.md`.\n  He accepted", ["G08-D2-bankref"]),
    ("N115", "osf", "  expected from him until there is a new measurement or a posting decision.",
     "  expected from him until there is a new measurement or a posting decision (p = 0.0326).",
     ["G08-D2-no-new-stats", "G06-num-osf"]),
    # G09 D3
    ("N120", "osf", "In **all\n  21 regions scanned**", "In **the\n  21 regions scanned**", ["G09-D3"]),
    ("N121", "osf", "  so never produce a NaN.", "  so never produce a NaN. This is universal.",
     ["G09-D3-banned"]),
    ("N122", "osf", "  so never produce a NaN.",
     "  so never produce a NaN, and no geometric predicate sees it.", ["G09-D3-banned"]),
    ("N123", "osf", "  so never produce a NaN.", "  so never produce a NaN; no predicate applies.",
     ["G09-D3-frozen-phrase"]),
    ("N124", "osf", "  pairs **2047 PRE / 474 POST of 2521 (18.80%)**",
     "  pairs **2047 PRE / 474 POST of 2521 (18.81%)**",
     ["G09-D3-counts-byte", "G09-D3-counts-text", "G11-head1077", "G04-census-osf"]),
    ("N125", "osf", "survives the **posted** predicate", "survives the **relevant** predicate",
     ["G09-D3-predicate", "G09-D3"]),
    ("N126", "osf", "  panel — a post-filter residual of **defined-but-degraded `r`** survives the **posted** predicate\n"
     "  and is **invisible to the retained NaN-raise by construction**, because those rows are defined and\n"
     "  so never produce a NaN. ⛔ **Stated at that scope deliberately: this says nothing about the 255\n"
     "  regions NOT scanned, and nothing about any predicate other than the posted one.**\n",
     "  panel — a post-filter residual is present.\n",
     ["G09-D3-predicate-nonvacuous", "G09-D3"]),
    ("N127", "osf", "- **Finding 1's counts and its claim are unchanged.**",
     "- **Finding 1's text is unchanged.**", ["G09-D3-10e-reconciled"]),
    # G10 D4
    ("N130", "c16", "\n**Uses the CORRECTED Rao-Scott table**",
     "\n**Status:** DRAFTED 2026-09-14, **NOT SENT**. No agent contacts Seth — Carter sends it."
     "\n**Uses the CORRECTED Rao-Scott table**",
     ["G10-D4-c16-old", "G10-D4-rest-byte-c16", "G04-census-c16"]),
    ("N131", "c17", "\n**Replies to:** `.planning/quick/260917-irg",
     "\n**Status:** DRAFTED 2026-09-17, **NOT SENT**. No agent contacts Seth — Carter sends it."
     "\n**Replies to:** `.planning/quick/260917-irg",
     ["G10-D4-c17-old", "G10-D4-rest-byte-c17", "G04-census-c17"]),
    ("N132", "c16", "**Status:** ✅ **SENT 2026-09-17, in the CORRECTED form**",
     "**Status:** ✅ **Sent 2026-09-17, in the CORRECTED form**", ["G10-D4-c16-new"]),
    ("N133", "c17", "**Status:** ✅ **SENT 2026-09-17.**", "**Status:** ✅ **Sent 2026-09-17.**",
     ["G10-D4-c17-new"]),
    ("N134", "c16", "**The body below is\nthe DRAFT, not the text sent:**",
     "**The body below is\nthe draft and the text sent:**", ["G10-D4-c16"]),
    ("N135", "c17", "**The reviewer's CLOSURE is the reply to it**",
     "**The reviewer's answer is the reply to it**", ["G10-D4-c17"]),
    ("N136", "c16", "reply (**§3**, banked at", "reply (banked at", ["G10-D4-mismatch-source"]),
    ("N137", "c16", "\nAll of the above is in the disclosure",
     "\nAn added body line.\nAll of the above is in the disclosure",
     ["G10-D4-rest-byte-c16", "G04-census-c16"]),
    ("N138", "c17", "\nThe disclosure stays DRAFTED", "\nAn added body line.\nThe disclosure stays DRAFTED",
     ["G10-D4-rest-byte-c17", "G04-census-c17"]),
    # G11 frozen regions
    ("N140", "osf", "**n_pairs 2521**; **n_pairs_POST 474**", "**n_pairs 2521**; **n_pairs POST 474**",
     ["G11-10a", "G11-head1077", "G04-census-osf"]),
    ("N141", "osf", "| 1.241                | 0.2171     |", "| 1.242                | 0.2171     |",
     ["G11-10b", "G11-table", "G11-head1077", "G04-census-osf"]),
    ("N142", "osf", "NEITHER fired.**", "NEITHER fired!**",
     ["G11-10c", "G11-head1077", "G04-census-osf"]),
    # G12 / G13 citation re-resolution
    # --- the AS-SENT bank (D5, Carter's 2026-09-17 addition) ---
    ("N160", "sent", "\n**Sent:** 2026-09-17, by Carter.", "\n(1.652)\n**Sent:** 2026-09-17, by Carter.",
     ["G01-sent-1.652", "G06-num-sent"]),
    ("N161", "sent", "\n**This is the text as SENT**", "\n(0.0366)\n**This is the text as SENT**",
     ["G01-sent-0.0366", "G06-num-sent"]),
    ("N162", "sent", "\n**Draft of record:**", "\n(1.564)\n**Draft of record:**",
     ["G01-sent-1.564", "G06-num-sent"]),
    ("N163", "sent", "\n**What changed before sending:**", "\n(0.0556)\n**What changed before sending:**",
     ["G01-sent-0.0556", "G06-num-sent"]),
    ("N164", "sent", "\n**His reply to this:**", "\n(1.969)\n**His reply to this:**",
     ["G01-sent-1.969", "G06-num-sent"]),
    ("N165", "sent", "All of the above is in the disclosure, still DRAFTED — NOT POSTED.",
     "All of the above is in the disclosure.", ["G02-sent-drafted", "G07-D5-fence"]),
    ("N166", "sent", "⛔ This is correspondence. It is not a source",
     "⛔ Clustering explains it. This is correspondence. It is not a source",
     ["G05-positive-senthead", "G05-positive-sent", "G05-sent-fence-scope"]),
    ("N167", "sent", "⛔ This is correspondence. It is not a source",
     "⛔ This reproduces correspondence. It is not a source",
     ["G05-sent-fence-scope", "G05-explain-senthead"]),
    ("N168", "sent", "Seth — the measurement landed.", "Seth — the measurement has landed.",
     ["G07-D5-fence"]),
    ("N169", "sent", "**This is the text as SENT**", "**This is the text we sent**", ["G07-D5-header"]),
    ("N170", "sent", "`502fe68481edeedcf42d53442af6b127`, 4907 B, 77 lines.",
     "`502fe68481edeedcf42d53442af6b128`, 4907 B, 77 lines.", ["G07-D5-header-pins"]),
    ("N171", "sent", "`.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md`",
     "`.planning/debug/260916-COURIER-TO-SETH-measurement-result.md`", ["G07-D5-header-draftref"]),
    ("N172", "sent", "4907 B, 77 lines. The fenced block", "4907 B, 77 lines, 9 sections. The fenced block",
     ["G06-num-sent"]),
    ("N173", "c16", "260917-pff-260916-COURIER-AS-SENT-measurement-result.md`.",
     "260917-pff-260916-COURIER-AS-SENT.md`.", ["G10-D4-c16-pointer"]),
    ("N174", "c16", "**This file stays the DRAFT OF RECORD**, and the text as\nsent is banked at the path above.",
     "**The sent form is not banked in this repo, so this file is\nthe draft of record.**",
     ["G10-D4-c16", "G10-D4-c16-pointer"]),
    # --- the S4 provenance rewrite (blocker, 2026-09-18) and the W1 time facts ---
    ("N175", "c16", "for it**. That figure was reachable",
     "for it**, so that phrasing came from the earlier exchange rather than from what was sent."
     " That figure was reachable", ["G10-D4-c16-noattr"]),
    ("N176", "c16", "unattributed, not attributed.**", "attributed to the draft body.**",
     ["G10-D4-c16-unattributed"]),
    ("N177", "c16", "on 2026-09-16, which states it verbatim,", "on 2026-09-16,",
     ["G10-D4-c16-committed-src"]),
    ("N178", "c16", "stood at that commit, which carried the superseded value it is computed against.",
     "stood at that commit.", ["G10-D4-c16-committed-src"]),
    ("N179", "c16", "banked, not byte-verified, at\n`", "banked at\n`",
     ["G10-D4-c16-qualifier"]),
    ("N103", "bank", "paste recorded in-session 18:11 EDT",
     "paste recorded in-session 18:10 EDT", ["G07-D1-header"]),
    ("N104", "bank", "scratch file written 18:18 EDT", "scratch file written 18:19 EDT",
     ["G07-D1-header"]),
    ("N150", "cites", "digest", "", ["G12-cites-pin"]),
    ("N151", "cites", "drop-moved", "", ["G12-moved-nonvacuous", "G12-cites-pin"]),
    ("N152", "cites", "inject-live", "", ["G12-cite-moved-scope", "G12-cites-pin"]),
    ("N153", "cites", "bare-digest", "", ["G13-bare-pin"]),
    ("N154", "cites", "bare-live", "", ["G13-bare-scope", "G13-bare-pin"]),
    ("N155", "cites", "bare-unmoved", "", ["G13-bare-nonvacuous", "G13-bare-pin"]),
]


def mutate_cites(op):
    c = copy.deepcopy(CIT0)
    if op == "digest":
        c["digest"] = "0" * 32
    elif op == "drop-moved":
        c["rows"] = [r for r in c["rows"] if r[4] <= 1077]
    elif op == "inject-live":
        c["rows"].append([".planning/STATE.md", 999, "explicit", 1100, 1100])
    elif op == "bare-digest":
        c["bare_digest"] = "0" * 32
    elif op == "bare-live":
        c["bare"].append([".planning/STATE.md", 999, 1100, "injected live bare reference"])
    elif op == "bare-unmoved":
        c["bare"].append([".planning/quick/260917-irg-x/260917-irg-PLAN.md", 999, 1077, "injected"])
    else:
        raise SystemExit("unknown cites op " + op)
    return c


def run_with(tag, base, a, b16, a16, b17, a17, bank, sentf, cites):
    d = os.path.join(work, tag)
    os.makedirs(d, exist_ok=True)
    ps = {}
    for fn, body in (("base.md", base), ("after.md", a), ("b16.md", b16), ("a16.md", a16),
                     ("b17.md", b17), ("a17.md", a17), ("bank.md", bank), ("sent.md", sentf)):
        p = os.path.join(d, fn)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        ps[fn] = p
    cp = os.path.join(d, "cites.json")
    json.dump(cites, open(cp, "w"))
    with contextlib.redirect_stdout(io.StringIO()):
        R = G.run(ps["base.md"], ps["after.md"], ps["b16.md"], ps["a16.md"], ps["b17.md"],
                  ps["a17.md"], ps["bank.md"], ps["sent.md"], clo_p, snt_p, irg_p, cp)
    return R


def main():
    bad = 0
    R0 = run_with("positive", BASE0, A0, B160, A160, B170, A170, BANK0, SENT0, CIT0)
    red0 = sorted({cid for cid, ok, _ in R0 if not ok})
    all_ids = sorted({cid for cid, _, _ in R0})
    print("POSITIVE CONTROL (unmutated): %d checks, FAIL ids = %s -> %s"
          % (len(R0), red0, "GREEN" if not red0 else "NOT GREEN"))
    bad += bool(red0)
    covered = set()
    for cid, which, old, new, expect in CONTROLS:
        base, a, b16, a16, b17, a17, bank, sentf, cites = (BASE0, A0, B160, A160, B170, A170,
                                                            BANK0, SENT0, CIT0)
        if which == "cites":
            cites = mutate_cites(old)
        elif which.startswith("identity-"):
            if which == "identity-osf":
                a = BASE0
            elif which == "identity-c16":
                a16 = B160
            else:
                a17 = B170
        else:
            src = {"osf": a, "c16": a16, "c17": a17, "bank": bank, "sent": sentf,
                   "base": base, "base16": b16, "base17": b17}[which]
            n = src.count(old)
            if n != 1:
                print("%s  INVALID CONTROL: old text occurs %d times in %s" % (cid, n, which))
                bad += 1
                continue
            mut = src.replace(old, new, 1)
            if which == "osf":
                a = mut
            elif which == "c16":
                a16 = mut
            elif which == "c17":
                a17 = mut
            elif which == "bank":
                bank = mut
            elif which == "sent":
                sentf = mut
            elif which == "base":
                base = mut
            elif which == "base16":
                b16 = mut
            else:
                b17 = mut
        R = run_with(cid, base, a, b16, a16, b17, a17, bank, sentf, cites)
        red = sorted({c for c, ok, _ in R if not ok})
        covered |= set(red)
        missing = [e for e in expect if e not in red]
        print("%s  %-14s expect RED %s -> observed RED %s  %s"
              % (cid, which, expect, red, "OK" if not missing else "MISSING %s" % missing))
        bad += bool(missing)
    uncovered = [i for i in all_ids if i not in covered and i not in UNFALSIFIABLE]
    print("\nCOVERAGE: %d/%d check ids observed RED by at least one control"
          % (len(all_ids) - len(uncovered), len(all_ids)))
    if uncovered:
        print("  UNCOVERED (no control, no UNFALSIFIABLE label): %s" % uncovered)
        bad += 1
    for k, v in UNFALSIFIABLE.items():
        print("  UNFALSIFIABLE %-24s %s" % (k, v))
    print("\nNEGCTL RESULT: %s" % ("ALL CONTROLS OBSERVED RED, ALL IDS COVERED" if not bad
                                   else "%d PROBLEM(S)" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED pff_negctl.py -->
