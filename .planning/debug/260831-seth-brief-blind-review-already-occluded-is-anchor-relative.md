# Seth's brief-blind review — `already_occluded` is ANCHOR-RELATIVE

**2026-08-31 · coloc_analysis / AoU AFR native-plink LD panel · quick-260831-kw8**

He was right twice. Both findings are confirmed — one in code, one against our
own data — and both were confirmed BEFORE this record was written, not by it.

---

## (a) THE REVIEW AS RECEIVED

The courier
(`.planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260831-kw8-COURIER-SENT-to-seth.md`,
sent 2026-08-29) asked him to adjudicate a **rule**, not a result: is the posted
occlusion predicate

```
d.index != v.index  and  d.pos < v.pos <= d.span_end
```

**directionally complete**, or is there a class it cannot see by construction?

**What was deliberately withheld, and why it mattered.** He was NOT told what our
earlier (contaminated) pass suggested, how many cases we thought existed, or
which direction they fell in. The courier says why: *"if I did, I would be
handing you the conclusion and calling your agreement independent."* He was also
asked to write down his own expectation before reading ours, and explicitly
invited to **attack the framing, not only the question inside it**.

He attacked the framing. That is where both findings came from — neither is
answerable from inside the question as we posed it.

---

## (b) FINDING A, CONFIRMED IN CODE

**The claim he attacked.** `src/python/pairwise_completeness_scan.py:122`, in the
RETAINED-SET PARITY bullet:

> *"the `--exclude` side is already visible as `already_occluded`"*

**It is false.** Three code sites settle it:

| site | what is actually there |
|---|---|
| `pairwise_completeness_scan.py:616` | `already_occluded = bool(deletion.pos < partner.pos <= deletion.span_end)` — evaluated against **THE ANCHOR DELETION OF THAT ROW ONLY** |
| `run_native_ld_panel.py:851-872` | `raw_rows` = the in-window `.bim` rows for `[from_bp, to_bp]` on `chrom`, **no padding** |
| `run_native_ld_panel.py:878` | `occluded_ids, _ = detect_occluded_variants(raw_rows)` — over **EVERY deletion in the window** |

So `already_occluded == False` means **"not inside THIS anchor's span"**. It does
**not** mean "survives `--exclude`", and **`n_undefined_not_already_occluded`
does not count pairs that survive filtering.** The two predicates are different
questions, and the field answers the smaller one.

**Demonstrated, not asserted.**
`tests/m3/test_pairwise_completeness_scan.py::test_already_occluded_is_anchor_relative_and_is_not_the_exclude_side`
constructs one window — deletion A @1000 (`len(REF)` 10, span 1000-1009),
deletion B @1004 (`len(REF)` 2, span 1004-1005), a SNP @1008 — in which the
B-anchored pair carries `already_occluded == False` while
`detect_occluded_variants` over the SAME rows returns that SNP's vid, attributed
to A. The mirror assertion (A-anchored → `True`) blocks a vacuous pass.

**The real case in our own banked data.** Region 1, pair `46714|46715`
(offset −6): `chr1:5922718:G:A` is NOT inside its anchor's span, but IS occluded
panel-wide by `chr1:5922716:ACGGTGG:A`, whose REF length 7 gives span
5922716-5922722. `5922716 < 5922718 <= 5922722`. The pair is
`already_occluded == False` and its member never reaches the matrix.

---

## (c) FINDING B, CONFIRMED AGAINST OUR OWN DATA

Our own courier's geometry sentence was **backwards**. It framed the neighbour as
the party driven invariant. **The invariant party is the DELETION.**

Confirmed by STEP 2 of the in-flight instrumentation: `invariant_member:
'deletion'`, `del_carriers_lost_frac: 1.0`, `confounding_pattern:
'perfect_deletion_confounding'` — and consistent with what we had **already
recorded** at `.planning/STATE.md:735` from the July 2×2 (5/6 asymmetric, the
occluder's carriers ~100% missing at the partner).

We had the right fact on file and wrote the wrong sentence in the document we
sent for review. That is the failure mode worth naming: the record was correct
and the *framing* was not, and only an outside reader attacking the framing
caught it.

---

## (d) WHAT CHANGED

1. **A new post-hoc tool** — `src/python/pcs_panelwide_reclassify.py`. It answers
   the panel-wide `--exclude` question from an ALREADY-EMITTED `pcs_pairs.tsv`
   plus the cohort `.bim`. It calls the FROZEN `detect_occluded_variants` (never
   a second copy — function IDENTITY is asserted), reports the two populations
   separately at BOTH row and pair level plus a `--mac 1`-subtracted third tier,
   keys on VID because plink `--exclude` does, counts and NAMES id ambiguity, and
   RAISES on a mismatched `.bim` or a drifted header. It opens no `.bed` and
   **cannot require the sweep to be re-run** — machine-checked by an AST gate.
2. **The behavioural enforcer** of Finding A (above), which is green against the
   code as it stands and stays green after the prose fix.
3. **The rename DECLINED**, argued and enforced (see below).
4. **The same-position probe** — `src/python/samepos_missingness_probe.py`,
   a tested instrument, STAGED and NOT RUN.
5. **The corrected semantics placed where the at-risk reader arrives** —
   `pcs_panelwide_reclassify.py` §(1b), because the prose fix to the scanner
   itself is DEFERRED (next section).

### ⚠ THE DOCSTRING CORRECTION IS **DEFERRED**, NOT DROPPED

The false sentence at `:122` is **still in the file**. This is deliberate and the
reason is measured.

The live runbook
`.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` STEP 0 gate
pins the scanner's **WHOLE-FILE md5 and byte size**
(`e03078ff73502c3c877b0d2ebf93941d` / `73772`), and
`tests/m3/test_pairwise_completeness_scan.py::test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash`
recomputes BOTH at call time. A **docstring-only** edit moves them to
`fc1d68dff1f493f6eb57dd427bed638a` / `78843` and turns that gate RED. Measured:
that edit causes **exactly one** failure across the scanner, freeze-pin and
frozen-detector suites — that gate.

The only way to green it is to rewrite the runbook. **We will not, mid-flight.**
Those pinned values are **currently a TRUE STATEMENT about the ~4h20m sweep that
is running.** Rewriting them now would make the record lie about which instrument
produced the sweep — and that cost is **not recoverable later**, whereas the
prose fix is. (The runbook says so itself: *"Do not 'update' these values from
what the VM reports — that inverts the gate."* Its pin (iii) is
`git log -1 -- <scanner>`, whose new value cannot even be known until after the
commit exists.)

* **Parked, re-appliable unchanged:**
  `.planning/debug/260831-DEFERRED-pairwise-completeness-scan-docstring.patch`
* **TRIGGER:** the post-sweep window — once the sweep LANDS and its artifacts are
  BANKED. Not before.
* **Interim mitigation (costs no pinned bytes):** the TRUE semantics are stated
  in `pcs_panelwide_reclassify.py` §(1b), which NAMES the false sentence and
  marks it FALSE. That note is **SELF-INVALIDATING**: its two claims about the
  scanner (that it still carries the sentence; its current md5/size) are
  recomputed from disk by
  `test_the_tool_docstring_carries_the_true_semantics_and_flags_the_scanners_false_claim`,
  so it goes RED the moment the parked patch lands and forces its own removal.
  The same test is, while the sweep runs, the machine check that the scanner's
  bytes have **not** moved.

### ⚠ THE GUARD-SCOPING BUG IS A **REPEAT**, NOT A FRESH DISCOVERY

This is the second time in **under four weeks** that a whole-file BYTE proxy has
made *correcting a known falsehood in prose* the expensive action.

* **2026-08-06 precedent** (`feedback_scope_a_guard_to_the_property_not_a_proxy`):
  freezing BYTES as a proxy for *"the reported numbers must not move"* made
  shipping a known-false census figure in a comment **cheaper** than fixing it.
  The recorded lesson: *"When the correct action becomes the expensive one, that
  is a scoping bug report."* The fix then was a comment-insensitive CODE pin,
  **proved able to fail before being trusted**.
* **2026-08-31, here:** we designed the STEP 0 content-hash gate ourselves in
  quick-260828-uej (T3) — as the *remedy* for a gate that had matched a commit
  SUBJECT — and chose whole-file md5 as its content pin. Three weeks later that
  choice is blocking the deletion of a false sentence.

Naming it a repeat matters: the 2026-08-06 note existed, was correct, and did not
prevent the recurrence, because the new gate was written as a *fix for a
different failure* and its own scoping was never re-examined. The next reader
should see a **pattern**, not an incident.

**THE DURABLE FIX (option C), SCHEDULED — not hand-waved.** In the post-sweep
window, together with landing the parked patch:

1. Replace the STEP 0 whole-file md5 with a **docstring-insensitive CODE hash**
   (hash of the parsed AST with docstrings stripped, or of the compiled code
   objects), so prose corrections cost nothing and a **behavioural** change still
   trips the gate.
2. **Prove the replacement can still fail before trusting it** — mutate a real
   code path, observe RED, revert. A green pin that has never been seen red is
   not evidence (`feedback_green_assertion_needs_a_negative_control`).
3. Keep the capability check (iv) exactly as it is: it already pins BEHAVIOUR
   rather than text, and it is the part of that gate that was correctly scoped.

---

## (e) WHAT DID NOT CHANGE, AND WHY

⚠ **THE PRE-REGISTERED NUMBERS DO NOT MOVE.**

| quantity | value |
|---|---|
| `n_undefined_rows` | 15 |
| `n_undefined_distinct_pairs` | 13 |
| `n_undefined_already_occluded` | 10 |
| `n_undefined_not_already_occluded` | 3 |
| offset histogram | `{-14: 1, -9: 1, -6: 1, -3: 1, -1: 1, 0: 10}` (sums to 15) |

**Why, in one sentence that cannot be misread: adjusting a pre-registered number
in response to a review is the exact move the pre-registration exists to
prevent.** This work **ADDS a derived quantity** and **CORRECTS an
interpretation**; it revises no prediction.

**The enforcement is structural, not a promise.**
`.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
is **not edited at all** by this task — its `git status --porcelain` stays empty —
and `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` stays green.

Also unchanged: the posted predicate, every threshold, the NaN policy, and the
live runbook.

### The rename was adjudicated and DECLINED

`already_occluded` is **not** renamed. A name is a claim and this one has already
misled a reader, so the decline is argued rather than assumed:

1. **A sweep is MID-FLIGHT** and will emit a header carrying this exact column.
   `TSV_COLUMNS` *is* the emitted header, and `pcs_panelwide_reclassify.py`
   checks it by STRICT EQUALITY — a rename would make the new tool RAISE on the
   in-flight artifact.
2. **The pre-registration names the two summary keys** (`§(e)` above). See the
   sentence in bold two paragraphs up.
3. **`TSV_COLUMNS IS PairResult._fields`** — one rename moves the emitted header,
   `SUMMARY_KEYS`, the banked BLOCK 2 identity pull and every consumer at once.

**TRIGGER for revisiting:** the next OSF version, AFTER the sweep lands and its
artifacts are banked. **ENFORCER:**
`test_the_already_occluded_rename_is_declined_while_the_sweep_artifact_contract_stands`.

---

## (f) ACCEPTED FROM THE REVIEW — NO ACTION BEYOND THIS RECORD

⚠ **A permanent record may not inherit an untraceable number, and may not inherit
an empirical claim its own author previously ruled ambiguous.** Every figure below
carries its source and whether **we** re-derived it. **We re-derived none of
them.**

| ITEM | DISPOSITION | REASON | SOURCE — and did WE re-derive it? |
|---|---|---|---|
| **Widening the predicate** (±5bp / ±50bp) | **DECLINED** | ±5bp costs **6.5**× the current rule; ±50bp costs **12.66**% of the panel; and it would encode a caller artifact as geometry. | **SETH-COMPUTED**, his 2026-08-29 reply §6, from region-1 dimensions. **NOT INDEPENDENTLY RE-DERIVED BY US**, and re-derivation was **not attempted**: it needs region 1's `.bim`, which is in-perimeter (MEASURED: no `afr_cohort*.bim` or `*region_00001*.bim` anywhere under the repo). Neither figure appears anywhere else in `.planning/` (MEASURED by `grep -rn`). ⚠ **The DECISION does not rest on their exact values** — it rests on the geometry argument, so a later correction to either number would **not** reopen the decline. |
| **The retained NaN-raise** | **NOT WEAKENED** | It is the necessary-condition residual detector. | Ours, already posted. |
| **The exclude-the-occluded asymmetry** | **KEPT** — but the mechanism and the ratio are **split** | See the two bullets below. | See the two bullets below. |

**On the asymmetry, the mechanism and the ratio must not be conflated:**

* **THE MECHANISM IS THE REASON, and it is a DERIVATION that needs no data.** An
  in-span variant is callable only on non-deletion haplotypes, so its allele
  frequency is computed on a haplotype-restricted subsample and is **biased BY
  CONSTRUCTION**, while the deletion itself is well-called. This is what Seth's
  new Q5 argues, and it stands on its own.
* **THE RATIO IS OURS, AND IT IS NOT CLEAN SUPPORT — BY ITS OWN AUTHOR'S EARLIER
  RULING.** The panel MAF on the pairwise-complete subset was ~**0.0078** (pairs
  3/4) vs ~**0.014** in the sumstats, a ratio of 0.557
  (`.planning/amendments/m3_panel_occlusion_policy_decision.md:52`). Record it as
  **DIRECTIONALLY CONSISTENT, NOT EVIDENCE.** Seth himself ruled it unusable on
  2026-08-18
  (`.planning/quick/260818-uoi-bank-seth-d-acceptance-courier-register-/260818-uoi-SETH-COURIER-d-acceptance-as-received.md:60`):

  > *"the GWAS AFR cohort is not the AoU AFR cohort. Region 1's ratio is
  > 0.0078 / 0.014 = 0.557 — the direction the mechanism predicts, but ordinary
  > between-cohort AF differences at MAF ~0.01 are easily that large on their
  > own. So a red here would be ambiguous, and an ambiguous gate is one people
  > learn to ignore."*

  His new Q5 cites the same ratio as corroboration. **The 2026-08-18 ruling is
  EARLIER and MORE CONSERVATIVE and therefore GOVERNS.** This record must not be
  readable as quietly promoting a claim its author had already demoted.

**FINDING B's geometry, for the record:** `invariant_member: 'deletion'`;
`del_carriers_lost_frac: 1.0`; `confounding_pattern:
'perfect_deletion_confounding'`; consistent with `.planning/STATE.md:735`.

---

## (g) THE DERIVED QUANTITY AND ITS SCOPE

Measured during planning by running the FROZEN detector on rows **synthesized
from the BANKED vids** — a **SUBSET** row set, not the full window.

**ROW level: 5 = 3 + 2.** Of the 5 upstream un-occluded rows, **3** (offsets −14,
−9, −6) belong to pairs with a panel-wide-occluded member:

| offset | occluded member | occluder | span |
|---|---|---|---|
| −14 | `chr1:7492693:ACAAACACACACGCAGG:A` | `chr1:7492679:…:A` | 7492679-7492709 |
| −9 | `chr4:80782565:TATACAT…:T` | `chr4:80782556:…:G` | 80782556-80782628 |
| −6 | `chr1:5922718:G:A` | `chr1:5922716:ACGGTGG:A` | 5922716-5922722 |

The remaining **2** (−3 `m2_region_00008`, −1 `m2_region_00149`) are **UNKNOWN**
on the banked subset.

**PAIR level: 3 = 1 + 2.** Of the 3 not-already-occluded pairs, **1** is
member-occluded (`46714|46715`, the −6); **2** are UNKNOWN (`924401|924402`,
`9776035|9776036`).

**THE MONOTONICITY ARGUMENT, spelled out.** Occlusion is monotone in the row set:
for a variant `v` present in both, `R ⊆ R'` implies `occluded(v, R) ⟹
occluded(v, R')`, because adding rows can only ADD covering deletions and the
self-guard is index-based and recomputed per call. **Consequence: an OCCLUDED
verdict computed on a subset is SOUND; a NOT-OCCLUDED verdict on a subset is
NOT.**

Therefore the **three positives stand**, and **the two negatives are UNKNOWN**
until `pcs_panelwide_reclassify.py` runs against the FULL window `.bim`
in-perimeter. `tests/m3/test_pcs_panelwide_reclassify.py::test_occlusion_is_monotone_in_the_row_set`
proves the property rather than assuming it.

⚠ **None of this moves 15 / 13 / 10 / 3 or the offset histogram.** It is a NEW
DERIVED QUANTITY beside them.

---

## (h) WHAT THIS RECORD DOES NOT ESTABLISH

* **No prevalence.** Not for occlusion, not for the panel-wide class.
* **No boundary width.** The offset distribution is a distribution, not a width.
* **No partial-confounding tail size.**
* **No answer for the same-position class.** The probe is built and tested on
  synthetic bytes and is **STAGED, NOT RUN**
  (`.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md`).
  The `hl.split_multi_hts` expectation remains an **INFERENCE FROM
  DOCUMENTATION** that this node cannot verify, and **a mismatch is a finding to
  report, never a number to adjust.**
* **No independent re-derivation** of the ±5bp / ±50bp prices. See §(f).

**Nothing was fired.** No enclave, VM, Dataproc, OSF, `gsutil`, `gcloud` or
network contact; $0. No per-sample data was created, read or moved. The in-flight
sweep was neither touched nor required to re-run, and the live runbook was not
edited.
