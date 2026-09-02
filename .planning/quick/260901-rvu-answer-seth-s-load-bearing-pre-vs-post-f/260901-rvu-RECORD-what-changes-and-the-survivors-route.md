# RECORD — what Seth's reply changes, the survivor's route, and the one thing he got wrong

`quick-260901-rvu`, 2026-09-01. **No code in this file.** Nothing here was run;
the instrument it describes is BUILT, TESTED and STAGED.

---

## 1. WHAT HIS REPLY CHANGES

**Q4 IS CONCEDED, and the concession re-bills an existing control rather than
removing it.** His words: *"I treated 'undefined' as a binary property when the
underlying quantity is continuous … A detector keyed to the endpoint is
structurally blind to the neighbourhood of the endpoint — and the neighbourhood
is where almost all the mass is."* And: *"Do not implement my Q4 recommendation
as written. The NaN-raise remains necessary and must stay, but it is a
zero-detector, not a residual detector, and I mis-sold it as the latter."*

So: **the NaN-raise STAYS. Its billing changes.** It is a ZERO-detector. Nothing
in the pipeline is removed, weakened or re-scoped by this concession; what
changes is what we may claim the raise covers. It never covered the
neighbourhood, and no document of ours may say it did.

**The consultation is BLOCKED, by his own ruling, on one question.** He will not
answer until the pre/post-filter question is settled: *"I have been wrong twice
on this project by carrying a quantity across a scope boundary (row/site,
pair-subset/window). I am not doing it a third time. Tell me which, and my answer
to your consultation may change."*

**His proposed replacement is a pairwise informative-carrier floor whose VALUE he
deliberately withheld** — *"picking a number from 'what passes' is the error we
have now made twice"* — with `m = 25 → SE(r) ~ 0.20` and `m = 100 → ~0.10` given
as CALIBRATION CONTEXT only. That withholding is honoured exactly: **this task
proposes no floor anywhere**, in code, in a key name, or in printed output, and a
machine guard fails if one is ever declared, applied or named.

---

## 2. THE DENOMINATOR, SETTLED

His question 1: *"What is the 0.876% denominator?"*

**353,074 DEFINED rows** = 353,089 candidate rows − 15 undefined rows.
3,094 / 353,074 = **0.876%**.

It is neither of the two hypotheses he offered and it is not the ~353,196 he
guessed. It is the banked `n_defined_rows_in`, already present verbatim in the
2026-09-01 panel-wide reclassification's POOLED block, computed on the same
`pcs_pairs.tsv` (`wc -l` 353090 → 353,089 data rows) that produced every other
number on this thread. The six `defined_carriers_lost_frac_bins` sum to exactly
353,074, which is the arithmetic reconciliation rather than a coincidence.

---

## 3. THE LOAD-BEARING QUESTION IS UNMEASURED, NOT MIS-SCOPED

His question 2 — PRE-filter or POST-filter — **has no answer in any artifact we
hold**, and the reason is structural, not a defect in the banked numbers:

* `pairwise_completeness_scan` enumerates candidates from the RAW `.bim` and
  never applies `--exclude`; its `already_occluded` is ANCHOR-RELATIVE.
* `pcs_panelwide_reclassify` filtered its row set to `undefined` rows, so all
  **353,074** defined rows were **READ** and never **CLASSIFIED**.

The machinery was correct and pointed at the wrong subset. It has now been
extended to classify the defined tail against the **same per-region excludelist
it already builds for the undefined rows** — one `detect_occluded_variants` call
per region, shared, never a second call over a different row set. The instrument
is staged at
`.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`
and **has not been run**.

---

## 4. WHICH ROUTE THE SURVIVOR TOOK — the answer to his open question

He asked, of the one pair that survived the panel-wide reclassification:

> *"My prediction 2 was specific — 'any nonzero count must come from a case where
> the occluding deletion is absent from the panel.' If the survivor is that case,
> the prediction was right in substance and my model is intact. If it reached
> survival some other way, I have another blind spot and I want to know its
> shape."*

**The survivor is `m2_region_00149`:**

| | |
|---|---|
| anchor deletion | `chr7:89454077:GCGTA:G`, pos **89454077**, REF span **[89454077, 89454081]** |
| partner | `chr7:89454076:C:T`, pos **89454076** |
| offset | **−1** (upstream) |
| `del_occluded_panelwide` | **False** |
| `partner_occluded_panelwide` | **False** |

**The partner sits ONE BASE BEFORE the anchor — 89454076 < 89454077 — which is
OUTSIDE the anchor's span, and NEITHER member is occluded panel-wide.**

So **there is no occluding deletion at all** — neither present in the panel nor
absent from it. His prediction 2 **does not explain this pair**: it predicts a
mechanism (an occluder that exists in truth but is missing from the panel) that
is simply not instantiated here.

**THE ROUTE IS ADJACENCY WITHOUT OCCLUSION.** The pair is undefined because the
two variants are immediate neighbours whose called sets do not intersect
informatively, not because anything covers either one. It is the **`−1` mirror of
`m2_region_00057`'s `+1`** — the same adjacency geometry on the opposite side of
the anchor, and the sample excludes the `+1` case by construction, which is
precisely why the `−1` case is the one left standing.

**That is the shape of the blind spot he asked for.** His model treats occlusion
as the mechanism of pair collapse; this pair collapses without any occlusion
event. Note that this is the *second* mechanism on this thread that neither party
enumerated — the first was the two pairs that die because the **anchor deletion
itself** is occluded (occlusion composing on the anchor side), which he has
already conceded and which, as he correctly observed, the posted rule *already*
covers because it does not privilege deletions.

**Scoring, honestly:** his sealed brief-blind prediction was directionally right
and beat ours (he said the surviving class was approximately zero; we said "at
least one of three"; the answer was one of three). His own scoring stands: *"'
approximately zero' is not zero, and I wrote it as though it were. 1 is a real
counter-example to a claim I stated without hedging."*

**The verdict's scope, attached:** the survivor is not-occluded **relative to**
`bim_sha256 9cc378b7…feeeb99` at `bim_n_lines 20767864`, with region 00149
contributing `n_rows_in_window 338354`. Occlusion is monotone in the row set, so
this verdict can flip to occluded if rows are added; it cannot flip the other
way. The twelve occluded verdicts are unconditional.

**His own check on his own answer is still OPEN and we should run it before
drafting anything:** *"Is the surviving pair inside, or adjacent to, a credible
set or a known association signal for any of the 9 traits?"* We have not
measured that. Region 1's precedent — the occluded SNP present in 7 of 9 AFR
traits with real effect estimates — is why the question is not rhetorical.

---

## 5. ⚠ HIS STATUS LINE IS STALE — FLAGGED, NOT SILENTLY CORRECTED

He closed with: *"Status unchanged as far as I know it: nothing fired, nothing
banked, constant still 0.0005, fire HELD."*

**`constant still 0.0005` is STALE.** This is flagged to him rather than quietly
fixed, because a correction made inside his own words would leave a record he
could later cite in good faith and be wrong. The evidence, in the order it must
be read — and the order matters, because reading only the first step REVERSES the
conclusion:

1. `.planning/amendments/osf-amendment-…-2026-08-20.md:3` still says *"the
   shipped constant `_OCCLUSION_ANOMALY_FRACTION` = 0.0005 stays exactly as it is
   until this amendment is POSTED."* **That line is a repo-local DRAFT BANNER,
   OUTSIDE the posted paste block** — the posted text is the marker-delimited
   block at lines 167-501. It was never posted and it is not the commitment.
2. **The amendment WAS posted** — `osf.io/mk7ze` on `az52u`, 2026-08-22.
3. **The producer today** uses the TWO-CONDITION gate. Cited by SYMBOL, because a
   line number is a proxy that decays silently on any edit above it:
   `src/python/run_native_ld_panel.py` imports `OCCLUSION_SITE_FRACTION_CEILING`
   (**0.005056**) and `OCCLUSION_INFLATION_CEILING` (**3.42**) from
   `occlusion_gate_constants` — *"THE one pinned place for the posted ceilings"* —
   binds them as module globals `_OCCLUSION_SITE_FRACTION_CEILING` /
   `_OCCLUSION_INFLATION_CEILING`, and compares against them inside
   `run_native_ld_panel.process_region`. (At the time of writing: import
   `:101-104`, binding `:160-161`, comparison `:903-904`.) MEASURED, not
   asserted: `grep -rn "OCCLUSION_ANOMALY_FRACTION" src/python/` returns **0
   lines**, and `0.0005` does not appear in `run_native_ld_panel.py` at all. The
   old constant is **gone from the producer entirely** — name and value.

So the two-condition gate is **live in code and posted publicly**. The
paste-block boundary is stated explicitly above rather than assumed, because
reading `:3` alone would produce the opposite conclusion — which is exactly the
failure mode that made this worth writing down.

The rest of his status line stands: nothing fired, nothing banked, fire HELD, and
an agent neither posts nor fires. So did this task: **$0, no perimeter contact,
VM STOPPED.**

---

## 6. WHAT THE TOOL NOW MEASURES — AND WHAT IT DOES NOT

**IT MEASURES**

* the tail's **PRE-filter vs POST-filter** split, at BOTH row and pair level, as
  separate keys, reconciled arithmetically or the tool refuses to write;
* the **informative-carrier distribution** — integer nearest-rank percentiles at
  `q ∈ {0,1,5,10,25,50,75,90,99,100}`, exact counts for every `m` in `0..100`,
  and cumulative `n_le_*` counts — computed **twice**: over all in-scope defined
  rows, and over the defined rows **reaching the matrix** (Seth's *retained
  pairs*);
* `n_defined_rows_rarer_and_min_definitions_disagree`, the rows where `the rarer
  variant` (decided on marginal MAF) and the precision-binding minimum retained
  count name **different** members. Two definitions that usually agree are not
  one definition, and a near-miss between them may not motivate a hypothesis.

**IT DOES NOT**

* establish any prevalence — these are counts over the scanned regions;
* propose, apply or name a carrier floor. `m = 25 → SE(r) ~ 0.20` and
  `m = 100 → ~0.10` are recorded here as **HIS calibration context** and are
  explicitly **not adopted**;
* move any criterion, threshold, policy, manifest or protocol;
* revise `353089` / `353090` / `353074`, the 15 rows / 13 pairs / 10-3 split, the
  offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, or the panel-wide
  12-1 pairs and 14-1 rows. It ADDS a derived quantity BESIDE them.

**`the rarer variant`, defined once so it cannot drift:** rarity is decided on
`*_maf_marginal` — each member's minor-allele frequency over its OWN called set —
and **never** on `*_carriers_marginal`, which is not comparable across members
because `n_called_del != n_called_partner` **is the phenomenon under study**. On
an exact MAF tie the member with the SMALLER retained count is chosen (the WORSE
precision, the same conservative shape as the scanner's own minor-allele tie
rule), then the smaller marginal count, then `del`; the tie is FLAGGED as
`rarer_by_maf_tie` so a reader can see the choice was forced rather than measured.

---

## 7. STATUS

**BUILT. TESTED. STAGED. NOT RUN.** The input `pcs_pairs.tsv` is in-perimeter and
the VM is **STOPPED**. Running the staged document is Carter's call, later.

Nothing was fired: no enclave, VM, Dataproc, OSF, `gsutil`, `gcloud` or network
contact anywhere in this task. **$0.** No genotype, no `.bed`, no per-sample datum
was read, created or moved.
