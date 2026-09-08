# 260908-hv8 — SUMMARY

**Two defects an external reviewer found IN OUR OWN CORRECTIONS, fixed. DOCS-ONLY.**
Disclosure status **UNCHANGED: DRAFTED — NOT POSTED.** No OSF contact. No Seth contact.
No VM, $0. `src/` and `tests/` untouched. Not pushed.

---

## Pre-flight anchors (all three verified BEFORE any edit)

| Anchor | Expected | Measured | Verdict |
|---|---|---|---|
| `CONTENT-SPEC.md` lines | 73 | 73 | PASS |
| `CONTENT-SPEC.md` md5 | `0b1aca4593a4a59d79af777a9288f68c` | same | PASS |
| `CONTENT-SPEC.md` bytes | 5321 | 5321 | PASS |

mk7ze source located and re-anchored independently:
`.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md`, 598 lines;
slice `NR>=168 && NR<=500` -> md5 `13a49f543cabcc27ce9f1e589783c060`, **22,945 B, 333 lines**
— all three of the spec's anchors reproduced. Posted = repo draft − 167 confirmed.

---

## D8 — SERIOUS: false statement + false equivalence (FIXED)

**The defect.** The entry glossed region-1 **pair 4** as a NaN pair for which no record
covered either member. **That is FALSE**, and our own geometry verdict said so
(`m3_region1_nan_geometry_verdict.md:19-20, 30-37`, read directly, not taken on trust):

- pair 3: `DEL 5922716 (7bp) -> SNP 5922718`, `ref_span_overlap`
- pair 4: `SNP 5922718 -> DEL 5922724 (31bp)`, **`disjoint`**, annotated
  *"2nd-order: SNP already occluded by DEL@5922716"*
- verbatim: *"SNP@5922718 DOES sit inside DEL@**5922716** (span 5922716–5922722)"*

So pair 4's NaN-implicated SNP **IS** covered — by a **THIRD** record — is **excluded by the
predicate**, and yields **ZERO residual**.

**Why it mattered more than a wrong gloss.** The *same phrase* was also used for the chr7
survivor, where it is **true**. One phrase serving both collapsed **two different classes into
one**, from which a reader concludes **the survivor's class was documented before posting.
IT WAS NOT.**

**The fix.** Seth's proposed wording adopted for the pair-4 sentence, plus a new bullet
stating the contrast so it cannot be collapsed again:
**pair 4 = known, handled, ZERO residual** (a covering record exists) vs
**the chr7 survivor = unhandled, IN-PANEL residual** — **NO covering record for EITHER
member**, so it **SURVIVES INTO THE PANEL**.

**The §(4) scoping repair STILL STANDS and was deliberately preserved** (now at
`osf_deviations.md:685-687`): pair 4's two members not being in a coverage relation remains
cited as exactly what shows the narrow reading is what the expectation set was **BUILT ON**.
Only the gloss and the implied equivalence were wrong — the citation is sound for that purpose
and says so explicitly, while stating it establishes **NOTHING** about the survivor's class.

**Two further instances of the shared phrase were also removed** — it appeared **3** times, not
once (see the guard finding below): the survivor at `:657` and the quotable "in substance"
annotation at `:698`. Both now read *"no covering record for EITHER member"*. Leaving them
would have left the false equivalence reconstructible from the surrounding text.

---

## D7 — recorded as an AMBIGUITY fix, NOT "the numbers were wrong again"

**Re-measured independently from the posted body** (not copied from the spec):

| Cited sentence | Begins | Ends | Posted range | Repo draft |
|---|---|---|---|---|
| NaN sentence | 108 | 110 | **108-110** | 275-277 |
| clause (a) | 300 | 302 | **300-302** | 467-469 |

We cited **108** and **300** — where each sentence **BEGINS**. Seth cited **110** and **301** —
where the phrase **he quoted** falls (*"but not conversely"* is on 110; *"covers the position"*
on 301). **Both are defensible referents; neither is sufficient.** The defect is that a single
line number for a multi-line sentence is **AMBIGUOUS** — not that either arithmetic was wrong.
This is stated in those terms in the disclosure: neither overstated against us, nor understated.

**Fix:** cite the **RANGE**, and make the **verbatim quotation the primary locator**, since a
quote survives repagination and a line number does not.

`mk7ze line 104` re-verified against the posted body — posted line 104 does read
*"a settled 5-member expectation"*. **CORRECT; left as-is**, as the spec required.

---

## D9 — `undefined` sweep result (DONE, with a recorded deviation)

Verified independently: `undefined` occurs **EXACTLY ONCE** in the 333-line posted body, at
line 82. Its implication runs **occluded => undefined**, **not** the converse, so it makes no
completeness claim over undefined r and there is **nothing there for the tail finding to
falsify**. Recorded because *a sweep that omits the one relevant term is not a sweep.*

**DEVIATION.** The spec said "ADD, in the silence section". A bullet on `undefined` **already
existed** (added by `260904-dgi`). Adding the spec's paragraph verbatim would have stated the
same fact **twice**, in two slightly different framings, in one section. I **folded the
incremental content into the existing bullet** instead. Substance preserved; duplication
avoided. The self-critical framing ("THE SWEEP MISSED THE WORD THAT MATTERS") was kept
deliberately over the spec's softer "The sweep also covered" — it is the stronger admission.

---

## D10 — §(3) heading (DONE)

`THE SURVIVOR GEOMETRY — a HEADLINE, and a POSITIVE result for the rule`
-> `THE SURVIVOR GEOMETRY — a HEADLINE, and what it does and does NOT establish`

Confirmed the body does withdraw the promotion (*"that promotion is withdrawn as overclaimed
from n=1"*), so the heading had been overselling what its own body gives back.

---

## GUARD FINDING — literal grep was blind, exactly as the brief warned

The pair-4 phrase was **line-wrapped AND bolded** in the source:

```
  region-1 NaN pair (pair 4) whose geometry is **`disjoint`** — a NaN pair with **NO covering
  deletion** — documented **BEFORE posting** …
```

A literal `grep "no covering deletion"` found **2** occurrences. The normalized sweeper
(strip emphasis, collapse all whitespace incl. newlines, lowercase) found **3**. **The single
most important instance — the one D8 exists to fix — was invisible to grep.** Had the guard
been a literal grep, this task would have reported green while leaving the defect in place.

**Negative control, run on the real file:** the wrapped+bolded form was re-injected into a copy
of the edited disclosure. Literal grep: **0 — still blind.** Normalized guard: **1 — RED.**
The guard discriminates; grep does not.

---

## Verification — every check with its negative control seen RED

| # | Check | Result | Negative control |
|---|---|---|---|
| V1 | `osf_deviations.md` **lines 1-531 byte-identical** to `d66efe7` (`cmp`) | PASS | prepend 1 byte -> `differ: byte 1` **RED** |
| V2 | `no covering deletion` = **0**, normalized, whole file | 0 | re-inject wrapped+bolded -> **RED (1)** while grep stayed 0 |
| V3 | Presence: `DEL 5922716` (2), `zero residual` (1), `EITHER member` (3), `SURVIVES INTO THE PANEL` (1) | PASS | each stripped from the real file -> **RED (0)** |
| V4 | `mk7ze lines 108-110` (3), `mk7ze lines 300-302` (1) | PASS | stripped -> **RED (0)** |
| V5 | `mk7ze line 104` present **and still correct** vs posted body | PASS | stripped -> **RED (0)** |
| V6 | §(4) scoping repair still stands (pair 4 still cited as built-on evidence) | PASS `:685-687` | — |
| V7 | Forbidden: `complete in its own direction`, `non-independence cannot create`, `unrelated constants`, `register this as a negative result`, `2.62` | all **0** | — |
| V8 | `git status --porcelain -- src tests` | **EMPTY** | — |
| V9 | Status `DRAFTED — NOT POSTED` intact | PASS | — |
| V10 | Courier record unchanged (`git diff --quiet`) | no diff | — |
| V11 | `HANDOFF.json` still valid JSON | parses | — |

**Sweep scope correction caught mid-flight:** the file grew 778 -> 805 lines, so the original
`532-778` window would have under-swept the entry. Re-run over `532-EOF` **and** the whole file
as a superset. Same result; the stale window is noted because it would have been a silent gap.

---

## Courier / VERBATIM APPENDIX — no re-splice needed (measured, not assumed)

The brief required fixing **at source + re-splice** if any edited text lived inside the
courier's byte-frozen appendix. **Measured:** the courier
(`260902-COURIER-TO-SETH-RUN2-…md`, 613 lines) contains **ZERO** occurrences of *every* target
phrase — `no covering deletion`, `DEL 5922716`, `mk7ze line 104`, all of them. The condition
never fired. Courier left byte-identical; **no supersession note was added anywhere.**

---

## DEVIATIONS (2)

1. **D9 folded into the existing bullet** rather than added as a new paragraph — see above.
   Avoids stating one fact twice in one section.
2. **SCOPE: two LIVE pin sites beyond the stated target were refreshed.**
   - `STATE.md:66` — ambiguous single-line citation.
   - `HANDOFF.json:219` — ambiguous single-line citation **and** the shared phrase
     (*"it has NO covering deletion, not a non-geometric one"*, about the survivor, so true but
     carrying the same collapse). Now *"no covering record for EITHER member"*. JSON re-validated.

   **Rationale:** missed pin sites are a *repeat* defect in this repo — `260904-dgi` PART C was
   itself criticised for exactly this (`HANDOFF.json` escaped an `--include=*.md` guard). Leaving
   a live citation that contradicts the convention this task exists to establish would have
   reproduced the known failure. Both are working documents, **not** the pre-registration chain.
   Flagging rather than hiding: this is broader than the brief's literal edit list.

**Not done, deliberately:** historical task records (`260903-ict` spec/plan, the `260904-dgi`
STATE row) still contain the retired phrase. They are the record of what was done then; editing
them would falsify history. See `deferred-items.md`.

---

## Self-check

- `.planning/osf_deviations.md` — exists, 805 lines, prefix `cmp`-proven
- `.planning/STATE.md` — task row inserted at `:2356`
- `.planning/HANDOFF.json` — valid JSON
- `SUMMARY.md`, `deferred-items.md` — written
- `src/`, `tests/` — **untouched**
- PART D — **QUEUED, not executed** (Carter fires)

## Self-Check: PASSED
