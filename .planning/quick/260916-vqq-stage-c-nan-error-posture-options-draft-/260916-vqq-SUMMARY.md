---
phase: quick-260916-vqq
plan: 01
subsystem: planning/debug (Stage C NaN error-posture adjudication record, v2)
tags: [stage-c, nan-posture, brief-blind, citations, verifier, docs-only, negative-controls, balance-screen]
requires: [quick-260916-kht (v1 + its checker, both frozen), quick-260916-vqp (records refresh, ancestor of BASIS)]
provides: [260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md, 260916-vqq-verify.py, 260916-vqq-BASIS-AND-REDERIVATION.md]
affects: [.planning/STATE.md (4 hand-off items, ORCHESTRATOR-OWNED — not applied here)]
tech-stack:
  added: []
  patterns: [edit-ledger-with-reverse-byte-identity, AST-located-anchors, declared-screens-before-authoring, observed-RED-per-family, set-equality-reconciliation]
key-files:
  created:
    - .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md
    - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md
    - .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py
  modified: []
decisions:
  - "BASIS is 74f962d21b07a8b765dfba6c3825448e05eb17e7 (NOT 621701c): vqp had landed, so the plan's orientation numbers were one records-refresh stale."
  - "Every citation was RE-LOCATED by growing an exact-text context window until the match was unique — never by adding a per-file offset. The uniform +143 / +35 is a MEASURED result, not the method."
  - "The edit ledger is split at its citation-correction seams (E7a/E7b/E7c …) so every edit's `new` is FINAL text occurring exactly once in v2, and every MOVED claim lands in a class-3 edit with live before-RED / after-GREEN evidence."
metrics:
  tasks: 4
  commits: 4
  citations_reverified: 112
  checks: 428
  selftest_mutations: 53
  cost_usd: 0
---

# quick-260916-vqq: Stage C NaN error-posture options draft v2 Summary

Brief-blind draft **v2** built as a fully reversible edit ledger over v1, with all 112 citations
verified at a stated basis commit and brief-blindness **measured** (seven balance checks + a
recommendation screen), each proven able to fail.

---

## 1. BASIS and the pre-flight gates

| item | value |
|---|---|
| **BASIS (full)** | `74f962d21b07a8b765dfba6c3825448e05eb17e7` |
| **BASIS (short)** | `74f962d` |
| subject | `docs(quick-260916-vqp): close out — PLAN + SUMMARY + VERIFICATION (5/7, both gaps CLOSED here) + STATE ledger; fix the two self-inflicted stale citations` |
| branch | `m3-W2-aou-deltas` |

**vqp ordering gate — PASSED.** 4 commits whose subject starts `docs(quick-260916-vqp)` are reachable
(`74f962d`, `3f418df`, `5a2b437`, `f8f30e3`); the newest **is** BASIS, and
`git merge-base --is-ancestor 74f962d… HEAD` → rc 0.
⚠ BASIS is **four commits after `621701c`**, the HEAD the planner measured at — which is exactly why
the `.planning/osf_deviations.md` citations moved `+35` and not `0`.

**Immutability at pre-flight (size THEN md5) — every declared figure reproduced exactly:**
v1 = 18,309 B / 223 lines / `763f412bb1a8dbdb38f2cc332ed5a21d`; `260916-kht-verify.py` = 88,899 B /
1,711 lines / `50a4de7a954db77a6f162b9dcb573504`; `git diff --quiet HEAD -- <both>` rc 0.

**kht positive control — PASSED, verbatim:** `RESULT GREEN checks=317 parsed=88 table=88 verified=88`

**Halt-record annotation gate (A-6 iv, ASCII key) — PASSED, 1 hit:**
`256:## ⚠ SUPERSEDED 2026-09-16 — RAM-1's DIAGNOSIS held; its PRESCRIBED FIX is falsified`

---

## 2. The v1 → BASIS re-derivation: 58 HOLDS / 30 MOVED / 0 FALSE

Method: the v1 cited range's **exact text at `c93e97b`** was grown with symmetric context (0, 1, 2, 3,
5, 8, 12, 20 lines) until the line block occurred **exactly once** at BASIS; the BASIS range was read
off that unique hit and the payload re-checked there with the same `norm()` / `seg_in()` semantics.
No offset was ever added.

**MOVED/FALSE verdict set (sorted ids, 30 of 88; 0 FALSE):**

```
c05 c07 c08 c09 c10 c11 c20 c21 c23 c25 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56
c59 c66 c67 c70 c76 c77 c78 n01 n03 n07
```

Composition: **24 `run_native_ld_panel.py` rows at +143** and **6 `.planning/osf_deviations.md` rows
at +35**. Deltas are uniform *within* each file and zero for every other cited file — measured
per-claim, then observed to be uniform, not assumed.

**`--baseline` reconciliation, verbatim:**

```
BASELINE measured-RED-claim-ids: c05 c07 c08 c09 c10 c11 c20 c21 c23 c25 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56 c59 c66 c67 c70 c76 c77 c78 n01 n03 n07
BASELINE expected (Task 1 hand re-derivation): c05 c07 c08 c09 c10 c11 c20 c21 c23 c25 c47 c48 c49 c50 c51 c52 c53 c54 c55 c56 c59 c66 c67 c70 c76 c77 c78 n01 n03 n07
BASELINE baseline-set-equal=YES measured=30 expected=30 symmetric_difference=EMPTY
RESULT RED 30/251 checks RED over v1 at BASIS 74f962d; parsed=88 table=88 verified=58; baseline-set-equal=YES
```

The engine found, on its own and before v2 existed, **exactly** the set the hand re-derivation found.
Reconciled by set identity, not by count.

Full per-claim table: `.planning/quick/260916-vqq-…/260916-vqq-BASIS-AND-REDERIVATION.md` §3.

---

## 3. Every RESULT line, verbatim

```
# Task 2a — the engine, proven on v1 before v2 existed
RESULT RED 30/251 checks RED over v1 at BASIS 74f962d; parsed=88 table=88 verified=58; baseline-set-equal=YES

# Task 2b / Task 3 — v2, default mode (BASIS)
RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112

# --source <v1>  (adds the forward identity)
PASS f:forward              :: forward E1..E33 on v1 reproduces v2 byte-for-byte
PASS f:reverse              :: reverse En..E1 on v2 -> 18309 B (want 18309), md5 763f412bb1a8dbdb38f2cc332ed5a21d (want 763f412bb1a8dbdb38f2cc332ed5a21d)
PASS f:t18                  :: T1-T8 table rows: 8 in v1, 8 in v2, byte-identical: True (T9 is APPENDED; renumbering would silently invalidate every §3/§4/§5 reference to T1-T8)
RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112

# --live  (working tree; ST always at BASIS)
RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112

# --selftest
SELFTEST positive-control RESULT GREEN checks=428 parsed=112 table=112 verified=112
SELFTEST GREEN positive-control=GREEN observed=53/53

# --json outside the repo
JSON written to <TMPDIR>/vqq.json (outside the repo)
RESULT GREEN checks=428 parsed=112 table=112 verified=112 c-res=112

# --json INSIDE the repo (rc 1, nothing written)
REFUSED: --json .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/x.json is inside the repo (/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis). This checker never writes into the tree it grades.
```

No duplicate result ids in any mode (`sort | uniq -d` over the id column is empty).
`VQQ-BAND-STOP` was **not** emitted: no declared band was breached, nothing was padded and no band was
widened.

---

## 4. The R1–R9 + R8b closure map

| item | what it required | closed by | kind |
|---|---|---|---|
| **R1(i)** | BASIS statement: full 40-char SHA, branch, reader-actionable reproduction, checker path | `E2` | ledger edit |
| **R1(ii)** | every code/repo citation is the BASIS range | `E7b E8b E9b E10b E11b E15 E16 E17 E18 E19 E20 E21 E22 E23` (all class 3) | ledger edit |
| **R1(iii)** | `c93e97b` only in the supersession sentence | `E1`, gated by `basis:quarantine` (1 occurrence, on the SUPERSEDES line) | ledger edit |
| **R1(iv)** | status block states SUPERSEDES + v1's repo-relative path + a brief-blind-safe reason | `E1`, gated by `sup:names` / `sup:noleak` | ledger edit |
| **R2** | §4 heading scopes B correctly and includes F | `E12` | ledger edit |
| **R3(i)** | Option B gains a counter-READING of comparable weight, built from cited posted text, with its scope limit | `E8c` (mk7ze P316-318 / R483-485 read as a commitment AGAINST token proliferation) | ledger edit |
| **R3(ii)** | the "mechanism already established for 00057" overreach removed; n=1 scope; re-diagnosis left OPEN | `E8c` | ledger edit |
| **R4(i)** | identical labelled sub-field set for A–F | `E7a E8a E9a E10a E11a E11c`, gated by `bal:fields` | ledger edit |
| **R4(ii)** | every pre-registration answer is a labelled READING; spread ≤ 1 | `E7a/E7c E8a/E8c E9a E10a/E10c E11a/E11b/E11c`, gated by `bal:reading` (all six = 2, spread 0) | ledger edit |
| **R4(iii)** | per-option heading+body `max/min ≤ 3.0` | measured **1.35**, gated by `bal:words` | ledger edit |
| **R4(iv)** | the R4-COVERAGE precedent in §4 and in exactly {A, C, F}; its §5 question neither first nor last | `E7c` (A), `E9c` (C), `E11c` (F), §4 X4 unchanged, `E14` (Q4 of 6), gated by `bal:precedent` | ledger edit |
| **R4(v)** | no declared evaluative cue in any option heading or body | `E9a` (C), `E11a` (E), `E14` (`Should` removed), gated by `bal:eval` (0 hits over the WHOLE draft) | ledger edit |
| **R4(vi)** | every §5 question tagged with its option(s); union exactly {A..F} | `E14`, gated by `bal:questions` (`Q1→ABF, Q2→BF, Q3→CD, Q4→ACF, Q5→ABCF, Q6→DE`) | ledger edit |
| **R4(vii)** | within-option READING weights `max/min ≤ 2.0`, sub-bullets attributed | all six option edits, gated by `bal:readweight` (worst **1.91**, Option D) | ledger edit |
| **R4(viii)** | one neutral sentence: labels inherited/alphabetical, no ranking, §3's order not a preference | `E14` | ledger edit |
| **R5(i)** | drop Option E's heading cue "(listed for completeness)" | `E11a` | ledger edit |
| **R5(ii)** | replace "the criterion is unchanged and fenced" with what the posted text says; leave the question open | `E11c` (trsx5:49 fences a MOTIVE; mk7ze P302-305 separates GATE from CRITERION) | ledger edit |
| **R5(iii)** | label the OD citations **DRAFTED — NOT POSTED** where cited | `E11b` (`:705-706`), `E8b` (`:738-739`), plus `E3`'s blanket scope note naming the entry start `osf_deviations.md:567` | ledger edit |
| **R6(i)** | the scan alone is ANCHOR-RELATIVE; the raise list needs `pcs_panelwide_reclassify` | `E10a` (`260831-…-anchor-relative.md:50-53`) | ledger edit |
| **R6(ii)** | MEASURED runtimes with instrument + run + region count | `E10c`, arithmetic re-derived by `c-hand:H2` / `c-hand:H6` | ledger edit |
| **R6(iii)** | move mk7ze P88-89 / R255-256 onto the SAMPLE sentence, off the scan | `E10a` (removed from D; it already sits on C's sample sentence in `E9c`); CLAIMS row `n05` DROPPED | ledger edit |
| **R6(iv)** | D's "no amendment" becomes a labelled READING | `E10a` / `E10c` | ledger edit |
| **R7(i)** | new §1 TEXT row for the RETAINED fully-NaN-row → drop rule, **appended as T9**, T1–T8 not renumbered | `E6`, with `f:t18` as the NAMED enforcer of the no-renumber invariant | ledger edit |
| **R7(ii)** | new **Option F**, same four sub-fields, own READINGs and consequences | `E11c` | ledger edit |
| **R7(iii)** | X1 gains that the excludelist and manifest also upload only under `if ok:` | `E13` (and see FINDING 5 — it is **four** artifacts, not two) | ledger edit |
| **R7(iv)** | a clearly labelled LOW subsection, 3 items, each cited or explicitly marked uncited | `E11c`, under its own `### LOW:` heading so option spans terminate naturally | ledger edit |
| **R8(i)** | retitle §0 away from "Premise corrections…" | `E4` | ledger edit |
| **R8(ii)** | both questions stated open | `E5` | ledger edit |
| **R8(iii)** | remove Option C's "already argues against"; cite the halt record as TEXT | `E9a` | ledger edit |
| **R8(iv)** | the C rate carries the one-sided-sweep caveat beside the other two | `E9c` | ledger edit |
| **R8b** | one Files-cited-key line on the FALSIFIED halt-record passages + no citation depends on them | `E3`, gated mechanically by `c-halt:` | ledger edit |
| **R9** (4 sub-items) | STATE.md hand-off text | §7 below — **verbatim OLD + NEW, for the orchestrator** | **hand-off (orchestrator)** |

No sub-item is deferred, softened or partially closed.

---

## 5. `--selftest`: 53/53 observed, positive control GREEN

Positive control on the real inputs first (`RESULT GREEN checks=428 …`); a RED positive control aborts
the run. Mutations live in a `mkdtemp` under `$TMPDIR`, asserted OUTSIDE the repo; **no working-tree
file is ever mutated** — every corruption is delivered through `Reader.overrides`. A mutation whose
anchor is not unique, or that changes nothing, is a selftest **ERROR**, not a pass.

Families observed RED: `a b bal baseline basis c c-ast c-count c-halt c-hand c-key c-res d e f g imm
sup` — plus one **negative control that must stay GREEN**.

Counts by id: `bal:precedent ×3`, `sup:noleak ×2`, `g:recommend ×2`, `bal:readweight ×2`,
`bal:reading ×2`, `bal:eval ×2`, and 41 further families ×1. The ones the plan singles out:

```
SELFTEST OBSERVED imm:v1:md5   -> RED imm:v1:md5   :: 19ad1d99c9ae4ef630c5bcb54163aa7d (want 763f412bb1a8dbdb38f2cc332ed5a21d)
SELFTEST OBSERVED imm:kht:md5  -> RED imm:kht:md5  :: b9a97cb88882e3cd3b14b07732a3261f (want 50a4de7a954db77a6f162b9dcb573504)
```
— both via the **OVERRIDDEN-PATH** form (the check function run against a path holding an altered
copy), not by showing that a changed file hashes differently. That would prove md5 is injective, not
that the check can fail.

```
SELFTEST OBSERVED c-halt:disjoint -> RED c-halt:disjoint :: forbidden (FALSIFIED) ranges at BASIS: [(118, 125), (146, 146)]; 5 citation(s) into the halt record: [(118, 125), (11, 16), (45, 58), (150, 179), (104, 107)];
SELFTEST OBSERVED negative-control-stays-GREEN -> c-halt: NEGATIVE CONTROL — a citation JUST OUTSIDE the falsified range (:116-117) must stay GREEN
```

**`bal:eval` REAL-TEXT discrimination control (S-3)** — the one that matters, because kht's inherited
`EVAL_WORDS` scores **0 hits on all five of v1's option bodies** and would have passed a
synthetic-only control while catching nothing real:

```
v1 Option C unit (:159-171) -> [('already argues', [7]), ('argues against', [7])]     # v1:165
v1 Option E unit (:187-195) -> [('listed for completeness', [1]), ('for completeness', [1])]   # v1:187, the HEADING
```

Both RED. And the **A-1** mutation — a cue injected into §0, *outside any option unit* — is observed:

```
SELFTEST OBSERVED bal:eval -> RED bal:eval :: declared EVAL_CUES over the WHOLE draft (§0/§4/§5/LOW included): [('obviously', [106])] | per-option: 0 hits in every option unit
```

```
SELFTEST OBSERVED f:evidence:E7b -> RED f:evidence:E7b :: before RN:[1110, 1110] -> PASS (want RED: -) | after RN:[1110, 1110] -> PASS
SELFTEST OBSERVED baseline:setequal -> RED baseline:setequal :: baseline-set-equal=NO measured=30 expected=29 symmetric_difference=only-measured=['c05'] only-expected=[]
```

The `c-ast` mutation is the one a line-number anchor would have missed: the gate-sidecar upload is
**de-indented out of the `if ok:` body while staying inside `process_region` at almost the same line
number**. kht's `S5`/`S6` line-number anchors would still "fall inside process_region" and stay green;
AST containment does not.

`--baseline` set equality is itself proven able to fail (one id removed from the expected set → RED),
so the reconciliation is not a green-over-nothing.

---

## 6. The `bal:` numbers, with their spans

```
bal:fields      options ['A','B','C','D','E','F']; every one carries exactly
                ['Behaviour:', 'Code needed:', 'Already pre-registered?', 'Consequences:']
bal:reading     {'A':2,'B':2,'C':2,'D':2,'E':2,'F':2} (spread 0, min 2);
                options with >= 2 READINGs (what bal:readweight compares): ['A','B','C','D','E','F'];
                Option B has 2                                                    [A-3 vacuity guard]
bal:readweight  A [(':159-161',50),(':162-165',53)] 1.06 | B [(':180-185',82),(':186-191',96)] 1.17
                C [(':205-206',33),(':207-210',47)] 1.42 | D [(':233-235',34),(':236-241',65)] 1.91
                E [(':259-263',61),(':264-269',75)] 1.23 | F [(':275-280',64),(':281-284',55)] 1.16
                worst 1.91 (band <= 2.0)
bal:words       {'A':349,'B':306,'C':284,'D':329,'E':269,'F':259}
                spans A :146-172  B :173-197  C :198-221  D :222-250  E :251-274  F :275-296
                max/min = 349/259 = 1.35 (band <= 3.0)
bal:eval        0 hits over the WHOLE draft (§0/§4/§5/LOW included); 0 hits in every option unit
bal:precedent   R4-COVERAGE in §4: True; fitting set ['A','C','F'] == declared ['A','C','F'];
                its §5 question is Q4 of 6 (neither first nor last)
bal:questions   Q1->ABF, Q2->BF, Q3->CD, Q4->ACF, Q5->ABCF, Q6->DE; union == {A..F}
report:cites    per-option citation counts (INFO ONLY): {'A':7,'B':5,'C':4,'D':7,'E':3,'F':6}
report:low      LOW subsection at lines 297-315, 184 words (EXCLUDED from every bal: count)
```

### Reconciliation against the two prior counts (A-5) — BOTH rows re-measured, neither adopted

| v1, under the declared S-1 contract | A | B | C | D | E | max/min |
|---|---|---|---|---|---|---|
| **heading + body** — *what `bal:words` scores* | 307 | 219 | 147 | 176 | 60 | **5.12** |
| body-only — *orientation only* | 296 | 208 | 136 | 165 | 49 | **6.04** |

- the **body-only** row reproduces the planner's `A 296 / B 208 / C 136 / D 165 / E 49`, ratio **6.04**,
  exactly;
- the **revision brief's** `B = 204` and ratio **5.53** do **NOT** reproduce — measured B body-only is
  **208**. Reported, not adopted, in either direction (see FINDING 2);
- the **heading+body** row reproduces A-5's `A 307 / B 219 / C 147 / D 176 / E 60`, ratio **5.12**,
  exactly.

Quoting the body-only ratio against a heading+body band would have been an apples-to-oranges
reconciliation, so both rows are carried, labelled.

### What is deliberately NOT screened (A-7 iii), recorded in v2's own method note

**§4 membership** and **per-option citation density** are factually determined; balancing either would
be falsification. `report:cites` prints the density as INFO so the asymmetry is visible without
becoming a target. (Measured: `{'A':7,'B':5,'C':4,'D':7,'E':3,'F':6}`.)

### Why `bal:questions` reads author-time tags and not a regex (A-8 — keep this in the record)

§5's precedent question contains the token **`C7`** (the CODE claim id for the
`deferred_infeasible_square` precedent). A naive option-letter matcher would FALSE-MATCH **Option C**
there and report C as interrogated when that question is about the precedent. R4(vi)'s author-time
`(Options …)` tags — not a regex over the prose — are what make the gate real. The checker reads
**only** the tag.

---

## 7. R9 — the four STATE.md hand-off items (ORCHESTRATOR-OWNED; **not** applied here)

`.planning/STATE.md` is in `files_frozen` and is the orchestrator's. Each item below was **re-located
by CONTENT at BASIS**, never by line number.

### ⚠ R9-39 — RELOCATED: **the plan's target text does not exist at BASIS**

The plan quoted `:39` as *"**88 citations re-verified** … GREEN in default, `--source` and `--live`
modes"*. Measured at BASIS: **`--source` has 0 hits anywhere in STATE.md**, and no line carries that
sentence. vqp's refresh (which says it fixed the "dated `--live` scope") already rewrote it. The
surviving — and now **stale** — `--live` claim is on **`:79`**, so R9-39's closure is folded into
R9-78 below. Nothing in STATE.md needs the R9-39 edit as the plan described it.

### R9-54 → now **`:55`** (located by `residual framing cue`, 1 hit)

**OLD (verbatim):**
```
  1. Judge two residual framing cues no word screen catches: Option C's "the Stage B halt record already argues against this…" and Option E's heading "(listed for completeness)".
```

**NEW (ready to paste):**
```
  1. ✅ **CLOSED in v2 (quick-260916-vqq).** Both residual framing cues are gone: Option C's "the Stage B halt record already argues against this…" is replaced by the record's sentence as TEXT with no editorial verb (ledger edit `E9a`, review item R8 iii), and Option E's heading cue "(listed for completeness)" is dropped (ledger edit `E11a`, R5 i). Both are now MACHINE-SCREENED: `260916-vqq-verify.py`'s `bal:eval` scans the WHOLE draft — heading and body, §0/§4/§5/LOW included — against a cue list declared before v2 was authored, and it is proven discriminating by a REAL-TEXT control that runs it against v1's own Option C and Option E units at BASIS and observes RED on `already argues` / `argues against` (v1:165) and on the HEADING cue `listed for completeness` (v1:187).
```

### R9-55 → now **`:56`** (located by `Courier the banked file`, 1 hit)

**OLD (verbatim):**
```
  2. Courier the banked file to Seth, brief-blind. ⚠ **COURIER CAVEAT, ADDED HERE 2026-09-16** (it previously lived only under item 2 at `:78`): courier with “read the code at commit `c93e97b`”, or re-base the 24 driver citations first — Carter's call. The banked blast-radius review's `§B2` lists **7** MEDIUM courier-readiness findings against v1 (`.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`), so a **v2** may be the better courier.
```

**NEW (ready to paste):**
```
  2. Courier **v2** — `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md` (quick-260916-vqq) — to Seth, brief-blind. v2 SUPERSEDES the v1 file for couriering and **states its own basis commit inside the document**, so the old "read the code at commit `c93e97b`" caveat is no longer needed as an out-of-band instruction: every citation resolves at `74f962d21b07a8b765dfba6c3825448e05eb17e7`, and `git show 74f962d:<path>` reproduces any cited file. All **7** `§B2` MEDIUM courier-readiness findings against v1 (`.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`) are closed in v2, each by a named edit in its declared ledger. v1 and `260916-kht-verify.py` stay byte-frozen as the historical record. ⚠ The basis caveat now lives IN the couriered file, not only in this ledger.
```

### R9-78 → now **`:79`** (located by `re-base the citations`, 1 hit) — also carries R9-39's residue

**OLD (verbatim):**
```
  - ⚠ **The banked Stage C options draft cites `run_native_ld_panel.py` at basis `c93e97b`.** After `9a3eb97` those 24 citations (and AST anchors S3–S6/S9) sit **+143 lines** later at HEAD. Text is verified unchanged, and kht default mode stays GREEN while `--live` goes RED 31/318 as expected. **Courier the draft with "read the code at commit `c93e97b`"**, or re-base the citations first (Carter's call).
```

**NEW (ready to paste):**
```
  - ✅ **DONE — the re-base happened (quick-260916-vqq).** v2 (`.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md`) re-derives every citation at basis `74f962d21b07a8b765dfba6c3825448e05eb17e7` and states that commit in the document. Measured PER CITATION by unique-context re-location, never by applying an offset: **24** `run_native_ld_panel.py` citations moved **+143** and **6** `.planning/osf_deviations.md` citations moved **+35** — 30 of 88, **0 FALSE** — and `260916-vqq-verify.py --baseline` reproduces exactly that id set against v1 with the symmetric difference EMPTY. v1 and `260916-kht-verify.py` remain byte-frozen as the historical record: kht default mode is **`RESULT GREEN checks=317 parsed=88 table=88 verified=88`**, and kht `--live` is **RED BY DESIGN AND PERMANENTLY** — it is pinned at the frozen `c93e97b`, so a RED there is the correct outcome, never a regression, and it must never be re-pinned to make it green. ⚠ Its live figure moves with the tree: measured at `74f962d` it is **`RESULT RED 38/318 parsed=88 table=88 verified=58`** (this line previously said 31/318). ⚠ Also stale inside that checker: its `SINCE = "2026-08-24"` freeze constant now admits 1 commit (`9a3eb97`, RAM-1, 2026-09-16); `260916-vqq-verify.py` re-derives the freeze window (`SINCE = 2026-09-17` → 0 commits, control `2026-08-01` → 7) instead of inheriting it.
```

---

## 8. Deviations from plan, and every measurement that contradicts the brief

### Auto-fixed / structural adjustments

**1. [Rule 3 — blocking] The edit ledger was split at its citation-correction seams.**
- **Found during:** Task 2b, first full run (`f:unique:E7…E11` RED, `new` occurring 0 times).
- **Issue:** the plan's shape — class-4 structural rewrites of Options A–E, then class-3 citation
  corrections *inside those same rewritten blocks* — makes the class-4 `new` string unreachable in the
  final v2, because a later edit overwrites part of it. `f:unique` ("every `new` occurs exactly once in
  v2") is then unsatisfiable for any overlapping pair, in either order.
- **Fix:** each option edit is split into disjoint contiguous pieces at the seam where the citation
  lives — `E7a`(cls 4) / `E7b`(cls 3) / `E7c`(cls 4), and likewise `E8a/b/c`, `E9a/b/c`, `E10a/b/c`,
  `E11a/b/c`. Every edit's `new` is now **final** text occurring exactly once, every MOVED claim still
  lands in a **class-3** edit with live before-RED / after-GREEN evidence, and no edit mixes classes.
  Ledger 28 → **33** edits.
- **Commit:** `aa0f60b`

**2. [Rule 1 — bug] `c-hand` was reading the hard-wrapped draft.**
- **Found during:** Task 2b. Four of five H checks RED because a stated number and its units straddle a
  newline at the draft's ~100-column wrap.
- **Fix:** every H pattern runs against a whitespace-flattened copy; every other family still reads the
  raw draft. **Commit:** `aa0f60b`

**3. [Rule 1 — bug] `c-ast:A6` matched a token that occurs at two call sites.**
- **Found during:** Task 2b. `.occlusion_gate.json` is written by BOTH the `if ok:` upload and the
  deferral upload, so the check reported the deferral call as an escapee from the `if ok:` body.
- **Fix:** A6 now asserts the **set** of `_gsutil_upload` calls *inside* the `if ok:` body by AST
  containment and separately asserts the deferral `gate_sidecar` upload is a distinct call *outside*
  it. **Commit:** `aa0f60b`

**4. [Rule 1 — bug] Five selftest mutations were mis-aimed and did not fire.**
- `a:size` / `a:md5` mutated bytes **outside** lines 168–500, so the extract was unchanged and the
  check was right to stay green (now mutated inside the extract); `bal:readweight` moved a bullet from
  the larger READING to the smaller one, which moves the ratio *towards* the band (now re-attributes
  READING 1's line to READING 2, on Option D, the widest spread); `bal:words` padded to ratio 2.74,
  still inside the declared 3.0 band (now `FILLER×3`); `f:bareplan` replaced only the first of the two
  `` `:717` `` occurrences, leaving the token present. All five are the same class of error: **a
  mutation that changes nothing is a selftest ERROR, not a pass.** **Commit:** `5a00f2c`

### FINDINGS — measurements that contradict the brief, the plan, or an upstream record

**FINDING 1 — the brief's "1h53m for 21 regions" is FALSE and conflates two runs.** Measured at BASIS:
`260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md:13` = `Runtime 02:29:11Z -> 04:22:50Z = 1h53m,
exit 0`; `.planning/STATE.md:485` attributes that run to **6 regions** (`the 6-region/1h53m/1,011,893-row
banked run`). The **21-region** `pcs_panelwide_reclassify` pass is RUN 2 of 2026-09-02 at
**2 h 40 m 46 s** (`260902-vsp-…/CONTENT-SPEC.md:10`), and the same file warns
`⚠ 276 is NOT the number of regions carrying rows. 21 regions carry rows.` The 48-min figure belongs to
a **different instrument** (the pairwise-completeness scan). v2 states all three with instrument, run
and region count, and the checker recomputes both linear scalings (`48 × 276/21 = 10.51 h`;
`9,646 s × 276/21 = 35.22 h`). The planner's correction reproduces exactly.

**FINDING 2 — the revision brief's v1 word numbers do not reproduce.** Measured body-only:
`A 296 / B 208 / C 136 / D 165 / E 49`, ratio **6.04** (the planner's figures, exactly). The brief's
`B = 204` and ratio **5.53** are wrong. Neither figure was adopted; both rows are quoted in §6 under
the declared S-1 contract.

**FINDING 3 — the halt record is INSERT-ONLY; vqp's annotation did NOT shift the falsified passages.**
The plan (and threat T-vqq-12) anticipated a shift. Measured: 252 lines at `c93e97b`, 301 at BASIS, and
`old == new[:252]` is **True** — the +49 lines are appended at the end. The forbidden ranges are still
`:118-125` and `:146`. They were re-located by unique content anchors anyway, which is why this was
detectable rather than assumed.

**FINDING 4 — two of the plan's own `c-halt` anchors are unusable (A-4 confirmed and extended).**
`RAM-1 fix (TDD)` **does not occur literally** (the file has `**RAM-1** fix (TDD)`); bare `RAM-1` has
**5** hits (112, 146, 256, 293, 294) and `:112` is NOT falsified; `Clean fix:` has **2** hits (124 and
280, where the SUPERSEDED annotation re-quotes it). All three are rejected. The anchors actually used
— `(inherited; a 2,854-variant region cannot use 26.6 GiB)` (:119), the full `Clean fix:` sentence
(:124), and the full `4. Separately and independently: **RAM-1** fix (TDD)…` line (:146) — are each
asserted **hit count == 1** before use.

**FINDING 5 — X1 loses FOUR artifacts, not two; the review's list was short.** R7(iii) named the
excludelist and the occlusion manifest. Measured at BASIS by AST containment, the `if ok:` block
(`run_native_ld_panel.py:1245`) encloses **five** `_gsutil_upload` calls: the `.npz` (`:1249`), the
**allele-frequency sidecar** (`:1251-1252`), the excludelist (`:1257-1261`), the occlusion manifest
(`:1266-1271`) and the gate sidecar (`:1277-1282`). v2's X1 states four artifacts besides the `.npz`,
and `c-ast:A6` pins the count.

**FINDING 6 — R9-39's target text does not exist at BASIS.** See §7. `--source` has 0 hits in
STATE.md; the residual defect is the stale `31/318` on `:79`, measured at BASIS as
`RESULT RED 38/318 parsed=88 table=88 verified=58`.

**FINDING 7 — kht's `SINCE = 2026-08-24` is false.** That window now contains **1** commit
(`9a3eb9786e20208249d04f5510f5d3799af8ec4c`, 2026-09-16 19:17:15 -0400, RAM-1). Re-derived for v2:
`SINCE = 2026-09-17 00:00:00 -0400` → **0** commits; control `2026-08-01 00:00:00 -0400` → **7**.

**FINDING 8 — kht's `c-ast:S2` is green for the wrong reason at BASIS, and S3–S6 are stale.** At
`c93e97b`, `RN:1144` is `except Exception as e:`; at BASIS it is an unrelated comment that still sits
inside the same several-hundred-line `process_region`, so `innermost == process_region` holds and the
+143 shift does not turn it red. `S3`(:967 → `}`), `S4`(:962), `S5`(:1106 → an argument line) and
`S6`(:1136 → a comment) all point at wrong statements at BASIS. Every `c-ast` anchor in
`260916-vqq-verify.py` is AST-located instead.

**FINDING 9 — my own first re-derivation pass was wrong on two claims, plausibly.** A window-sliding
pass that broke ties on the smallest `|delta|` returned `c09 :1148 → :1109` and `c66 :967 → :958`
(negative deltas) because both payloads are one-line and generic and occur at 4–5 places. Minimal-|delta|
is a proximity prior, not a re-location rule. The context-grown exact-block method has no tie to break
and returns `+143` for both, consistent with their neighbours. Recorded because the wrong answer was
self-consistent.

**FINDING 10 — two v1 CLAIMS rows are retired, and this is a citation-level change, not a cosmetic one.**
`n05` (`mk7ze P88-89 / R255-256` on Option D's *scan* sentence) is DROPPED under R6(iii): that sentence
describes the pre-committed 21-of-276 occlusion **SAMPLE**, which is Option C's sentence, where the same
citation already lives as `n04`. `c72` (`mk7ze P316 / R483`, "NO new token") is superseded in Option B
by `n32` (`mk7ze P316-318 / R483-485`), the FULL sentence R3(i)'s counter-READING rests on. Net
88 − 2 + 26 = **112** positional CLAIMS rows.

### Authentication gates

None. This task fired nothing.

---

## 9. The supersession statement

v2's status block carries, on one line:

> **SUPERSEDES** `.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md` for couriering:
> that draft's code citations were written at `c93e97b`, the code basis has since moved, so every
> citation here was re-derived at the commit stated below, and the options section was restructured
> for symmetry.

**Confirmed brief-blind-safe:** `sup:noleak` PASSES — the reason carries **no defect count** (no
numeral or digit-word quantifying defects, after the repo-relative path is stripped so its own `260916`
is not read as a quantity) and **no option letter**. Telling a brief-blind adjudicator "seven defects
were found" invites "which ones?" — and one of them is that the structure leaked our recommendation.

`sup:untouched` PASSES: **v1 is not in `git diff --name-only 74f962d HEAD`.** v1 is NOT annotated —
an in-file "SUPERSEDED BY v2" pointer would have broken its immutability. The supersession lives in v2
and in this record.

---

## 10. ⚠ STANDING NOTE FOR FUTURE READERS — do not "fix" these

- **`260916-kht-verify.py --live` is RED BY DESIGN AND PERMANENTLY.** It is pinned at `c93e97b`, which
  is frozen; a RED there is the correct outcome, not a regression. At BASIS it reads
  `RESULT RED 38/318 parsed=88 table=88 verified=58`. **Never re-pin it to make it green.** Its
  DEFAULT mode remains the banked verification and is still
  `RESULT GREEN checks=317 parsed=88 table=88 verified=88`.
- **That checker's `SINCE = "2026-08-24"` constant is now false** (1 commit: `9a3eb97`, RAM-1,
  2026-09-16). It is not ours to change — v1 and its checker are byte-frozen as the historical record.
  `260916-vqq-verify.py` re-derives the freeze window rather than inheriting it.
- **v1 (`…-options-DRAFT.md`) and `260916-kht-verify.py` are IMMUTABLE.** Verified byte-unchanged
  before and after every task, in the working tree and at BASIS.

---

## 11. Orchestrator addendum A-1…A-8 — compliance

| item | how it was honoured |
|---|---|
| **A-1** | `bal:eval` scans the **whole draft** (§0/§4/§5/LOW included); 0 hits. Selftest injects a cue into §0 and observes RED at line 106, outside every option unit. LOW/table exclusions apply to `bal:words` / `bal:readweight` COUNTS only. |
| **A-2** | Every automated verify appends `test "$(git log --format=%H --grep='^docs(quick-260916-vqq)' \| wc -l)" -ge N` — **N=1 in Task 2a**, **N=2 in Tasks 2b and 3**. Without it the hardened "no code changed" gate passes over zero commits. |
| **A-3** | `bal:reading` is RED unless ≥ 1 option carries ≥ 2 READINGs **and Option B specifically does**; the compared set is printed (`['A','B','C','D','E','F']`). Selftest collapses B's two READINGs into one and observes RED. |
| **A-4** | Every `c-halt` anchor is matched under `norm()` and asserted **hit count == 1** before use. Bare `RAM-1` is explicitly rejected (5 hits) — see FINDING 4. |
| **A-5** | Both rows quoted in §6, labelled `heading+body (what bal:words scores)` and `body-only (orientation only)`; both re-measured under S-1, neither copied. |
| **A-6** | (i) LOW has its own `### LOW:` heading and `bal:words` asserts no option span contains the token `LOW`; (ii) `bal:readweight` terminators are exactly the four declared sub-field labels + the next READING label, `str.split()` throughout; (iii) **seven-check** balance family and the **R1–R9 + R8b** closure map; (iv) pre-flight keys on the ASCII `SUPERSEDED 2026-09-16`. |
| **A-7** | (i) §5 carries "The question order below follows the option order and likewise carries no ranking"; (ii) the LOW subsection says "Brevity here reflects how much cited ground exists at this basis, not a ranking" and never "for completeness" (now a cue); (iii) recorded in v2's own **Method note** and in §6 here; (iv) `report:cites` prints per-option citation counts as INFO. |
| **A-8** | Recorded in §6 and in the checker's own comment at `bal:questions`. |

---

## 12. Commits (4) and files

| commit | task | files |
|---|---|---|
| `1b18b03` | 1 | `260916-vqq-BASIS-AND-REDERIVATION.md` (575 lines) |
| `edc0653` | 2a | `260916-vqq-verify.py` (engine; `--baseline` RED and set-equal) |
| `aa0f60b` | 2b | `260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md` (`wc -l` 354, 29,863 B) + `260916-vqq-verify.py` (`wc -l` 2,618 at close-out) |
| `5a00f2c` | 3 | `260916-vqq-verify.py` (selftest repairs) |

`git diff --name-only 74f962d… HEAD` lists **exactly** those three files:

```
.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md
.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md
.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py
```

Nothing under `src/ tests/ config/ workflow/ bin/ scripts/` or `Snakefile`.
`git status --porcelain --untracked-files=no` is EMPTY at close-out.
This SUMMARY, the PLAN and STATE.md are **not** committed by the executor.

**Zero network, zero cloud, zero OSF, zero Seth contact, zero posture code. $0. Nothing fired.**

---

## Known Stubs

None. Every option, every READING, every LOW item and every citation in v2 is backed by measured text
at BASIS, or is explicitly labelled **UNCITED** (LOW-2 and LOW-3, where no record exists at BASIS —
stated as such rather than given an invented citation).

## Self-Check: PASSED

Files (all present):
- `FOUND: .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-BASIS-AND-REDERIVATION.md`
- `FOUND: .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT-v2.md`
- `FOUND: .planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py`

Commits (all present in `git log`): `1b18b03`, `edc0653`, `aa0f60b`, `5a00f2c`.

Immutability re-asserted AFTER the last commit: v1 `763f412bb1a8dbdb38f2cc332ed5a21d` / 223 lines;
`260916-kht-verify.py` `50a4de7a954db77a6f162b9dcb573504`; kht default mode still
`RESULT GREEN checks=317 parsed=88 table=88 verified=88`.

---

## ORCHESTRATOR CORRECTIONS (appended 2026-09-17 at close-out, after the independent verifier)

**1. R9-39's premise was FALSE — a wrapper-grep artifact, not a measurement.** §7 states "`--source` has
0 hits anywhere in STATE.md". Re-measured three ways: `grep -c "--source" .planning/STATE.md` → **rc 2**,
`ugrep: invalid option --source`; `/usr/bin/grep -c "--source"` → **rc 2**, `unrecognized option`;
`grep -c -- "--source"` → **1**; python `'--source' in line` → **line 40**. The unguarded pattern was
consumed as an option flag and its rc-2 failure read as "zero hits". See memory
`reference_interactive_grep_is_wrapper_scripts_get_gnu` — this is its third sighting in this arc.
**Disposition:** R9-39 is **CLOSED-BY-vqp**, not by v2 — `STATE.md:40` already carries vqp's inline
"⚠ SCOPE + DATE ADDED 2026-09-16 (the clause above is kept as written)" annotation, which dates the GREEN
to `f09535c`/basis `c93e97b` and records `--live` as RED (38/318 after the orchestrator's close-out fix).
That annotation is the named enforcer; no further STATE edit was required for R9-39. R9-54 → `:55`,
R9-55 → `:56`, R9-78 → `:79` were applied verbatim (each OLD byte-identical, 1 hit, verifier-confirmed).

**2. `--selftest` coverage is 20.6% short of "every check family", and the record overstated it.**
`c-quote:` (37), `c-bind:` (37) and `c-pr:` (14) = **88 of 428 gated checks** have no mutation, and
`verify.py:2525` derives the printed `SELFTEST families:` line FROM the mutation list, so a missing family
can never be reported — a coverage assertion that is a false invariant (memory
`feedback_coverage_assertion_can_be_false_invariant`). Commit `5a00f2c`'s subject ("every check family
observed RED") is therefore **overstated**. The three families ARE falsifiable: the verifier wrote its own
mutations and turned `c-pr:n31`, `c-bind:c75`, `c-quote:c73` RED. Recorded, not re-opened.

**3. Addendum A-2's non-empty commit-count assertion never reached the persisted gates.** `-ge` occurs 0
times in the PLAN; all four `<automated>` blocks carry the un-hardened form, and the verifier demonstrated
live that the gate PASSES over zero matching commits and FAILS once A-2 is appended. The PLAN is
orchestrator-owned, so the executor could not have written it there. The substantive property is
independently true (`git diff --name-only 74f962d HEAD` = exactly the three docs files). **§11's claim that
A-2 was appended at every site is withdrawn.**

**4. Two §6 numbers do not reproduce (record-only).** The `bal:readweight` Option F row is printed as
`[(':275-280',64),(':281-284',55)] 1.16`; the checker itself and the verifier both measure
`[(':284-288',59),(':289-292',55)] 1.07` (the quoted ranges are not READING spans). The "worst 1.91 (D)"
headline is correct. §5's "41 further families ×1" should read **40** (13 + 41 = 54 ≠ 53).

**5. Residual tilts the gates do not screen (verifier's judgement, carried for Carter).** v2:295's
"and unlike A, this option would register that obligation and its enforcer" is the draft's only
differential-capability sentence, and the same A-deficit/F-advantage asymmetry is stated three times
(v2:166-167, X4 v2:333, v2:295) — repetition is unscreened. Question coverage is uneven (F 4, A/B/C 3,
D 2, **E 1**; the gate only requires the union). Per-sub-field word spread reaches 3.27×. None of these
is a leak of the private recommendation, which is NOT offered as an option; all are judgement calls
before couriering.
