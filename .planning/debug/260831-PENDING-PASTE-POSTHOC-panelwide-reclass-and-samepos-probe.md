# PENDING PASTE — POST-HOC panel-wide reclassification + same-position probe

STATUS: STAGED — NOT RUN

Nothing in this document has been executed. It fires nothing on its own.

**Run ONLY after the in-flight ~4h20m pairwise-completeness sweep LANDS and its
artifacts are banked.** Neither block below re-runs that sweep — BOTH READ ITS
OUTPUT. The sweep's `pcs_pairs.tsv` is BLOCK A's *input*.

⚠ This is a NEW document. It does **not** modify
`.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`, which is
the LIVE runbook an operator may be pasting against right now. A document that
changes under a running operator is its own defect class.

---

## BLOCK A — the panel-wide `--exclude` reclassification

### What it answers, and why the scanner could not

`already_occluded` in `pcs_pairs.tsv` is **ANCHOR-RELATIVE**: it is
`deletion.pos < partner.pos <= deletion.span_end` against **that row's anchor
deletion only**. The production excludelist is a **different** quantity —
`detect_occluded_variants` over **every** deletion in the window. So
`already_occluded == False` means *"not inside THIS anchor's span"*, **not**
*"survives `--exclude`"*, and `n_undefined_not_already_occluded` does **not**
count pairs that survive filtering.

This block computes the panel-wide quantity **post hoc**, from the artifact the
sweep already produced. It opens no `.bed`, decodes no genotype, and cannot
require a re-run.

### The command

```bash
cd ~/coloc_analysis
python3 src/python/pcs_panelwide_reclassify.py \
  --pairs-tsv /home/jupyter/occ_measure/pcs_pairs.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --regions-tsv config/ld_regions.tsv \
  --ancestry AFR \
  --out /home/jupyter/occ_measure/pcs_panelwide_reclass.tsv \
  --summary /home/jupyter/occ_measure/pcs_panelwide_reclass.json
```

### PRE-FLIGHT (run BEFORE the command; each has a STOP)

```bash
ls -l /home/jupyter/occ_measure/pcs_pairs.tsv
ls -l /home/jupyter/occ_measure/pcs_panelwide_reclass.tsv \
      /home/jupyter/occ_measure/pcs_panelwide_reclass.json 2>&1
```

* `pcs_pairs.tsv` **must exist and be the banked sweep output.** If it is absent
  or still being written: **STOP.**
* If **either** output path is occupied: **ROTATE, NEVER DELETE** (the standing
  project ruling) —
  `mv <path> <path>.PRE-$(date -u +%Y%m%dT%H%M%SZ)` — then re-check. Refuse to
  overwrite.

### COST NOTE (this is provenance, not overhead)

The tool sha256s the `.bim`. That is a full streamed pass over ~20.7M lines and
takes seconds-to-minutes. It is what makes a NOT-OCCLUDED verdict interpretable
at all (see the scope note below), so it is not optional.

### WHAT TO LOOK FOR — and this is NOT a prediction

Read these from the summary JSON. **No expected value is stated here**, because
the whole point is that the panel-wide quantity has never been computed:

* `n_pairs_member_occluded_panelwide` — the pair never reaches the matrix;
* `n_pairs_neither_member_occluded_panelwide` — the genuine residual;
* both of their **ROW-level twins** (the pair-level and row-level counts are
  DIFFERENT quantities and one is a known undercount of the other — never
  collapse them);
* `n_pairs_neither_occluded_and_no_globally_invariant_member` — the strictest
  tier, with the `--mac 1` side subtracted;
* `n_pairs_with_ambiguous_member_id` and the NAMED `ambiguous_member_ids` —
  production's own `--exclude`-on-a-duplicated-id ambiguity, surfaced not fixed.

The two counts must reconcile against `n_undefined_distinct_pairs_in` (and the
row twin likewise) or the tool RAISES before writing. A count is a claim.

### ⚠ THE PLANNING MEASUREMENT, WITH ITS SCOPE

Measured during planning against the FROZEN detector, on rows **synthesized from
the BANKED vids** — a **SUBSET** row set, not the full window:

* ROW level: of the 5 upstream un-occluded rows, **3** (offsets −14, −9, −6)
  belong to pairs with a panel-wide-occluded member; **2** (−3 `m2_region_00008`,
  −1 `m2_region_00149`) are **UNKNOWN** on the banked subset. `5 = 3 + 2`.
* PAIR level: of the 3 not-already-occluded pairs, **1** is member-occluded
  (`46714|46715`, the −6); **2** are UNKNOWN (`924401|924402`,
  `9776035|9776036`). `3 = 1 + 2`.

Occlusion is **MONOTONE in the row set**: adding rows can only add covering
deletions. Therefore an **OCCLUDED verdict on a subset is SOUND**, while a
**NOT-OCCLUDED verdict on a subset is NOT**. The three positives above stand.
The two negatives are **UNKNOWN**, and this full-window run is what settles them.

⚠ **This does not move `15 / 13 / 10 / 3` or the offset histogram.** It is a NEW
DERIVED QUANTITY beside them.

### EGRESS

The summary JSON's aggregate counts plus the NAMED variant ids only. **The
per-pair TSV stays in-perimeter.**

---

## BLOCK B — the same-position missingness probe

### THE DECISION RULE — READ THIS BEFORE RUNNING, NOT AFTER

* `co_called` — the site being called implies BOTH rows are called; intersecting
  `called(a)` with `called(b)` strips nothing ⇒ the same-position class **cannot**
  produce an undefined pair by co-location alone ⇒ **THE CLASS IS EMPTY.**
* `complementary` — a row's ALT carriers are MISSING at its same-position
  sibling; `called(a) ∩ called(b)` strips exactly a's carriers ⇒ **THE CLASS IS
  REAL**, and the posted predicate's strict left bound (`d.pos < v.pos`) is a
  genuine blind spot.
* `mixed` — neither. Reported as itself.

A rule chosen after seeing the number is not a rule. That is why it is here.

### ⚠ THE INFERENCE, AND ITS UNVERIFIED STATUS — beside the measurement, never instead of it

The pipeline splits multiallelics with `hl.split_multi_hts`
(`src/python/aou_ld_panel.py:2138`). Its **documented** behaviour downcodes
other-ALT carriers to **REFERENCE** — not to MISSING — which **PREDICTS
`co_called` and an EMPTY class**.

That is an **INFERENCE FROM DOCUMENTATION, NOT A MEASUREMENT.** Hail is
**not installed** on the NCSU node and the claim **cannot be verified there**.
The reviewer asked for a measurement rather than an inference; this probe is
that measurement.

**STANDING RULE, verbatim: a mismatch between the inference and the measurement
is a FINDING TO REPORT, never a number to adjust.** If the probe returns
`complementary`, the prediction was wrong and that is the result — do not
re-bin, re-threshold or re-scope to recover it.

### The command

```bash
cd ~/coloc_analysis
python3 src/python/samepos_missingness_probe.py \
  --bfile-prefix /home/jupyter/afr_cohort \
  --regions-tsv config/ld_regions.tsv \
  --ancestry AFR \
  --max-multiplicity 8 \
  --max-sites-per-region 200 \
  --out /home/jupyter/occ_measure/samepos_pairs.tsv \
  --summary /home/jupyter/occ_measure/samepos_summary.json
```

### PRE-FLIGHT

Same rotation rule: if either output path is occupied, **ROTATE, never delete.**

### WHAT TO READ

* `label_counts` over `{co_called, complementary, mixed}` — pooled and per region;
* `frac_histogram` **and** `n_frac_eq_0` / `n_frac_eq_1` — the quantity is
  expected to be bimodal under either hypothesis, so **do not average it**;
* `n_sites_total` **beside** `n_sites_measured`, plus
  `n_sites_skipped_over_max_sites_per_region` and
  `n_groups_skipped_over_max_multiplicity` — **a capped run is a SAMPLE, never a
  census**, and quoting the measured count alone would be a census claim;
* `n_undefined_pairs` and `undefined_pair_vids`.

### EGRESS

Aggregate counts, fractions, histogram bins and variant ids only. **No
genotypes, no per-sample vector, no sample identifier.** The per-pair TSV stays
in-perimeter.

---

## WHAT NEITHER BLOCK DOES

Changes no criterion, no threshold, no policy. Moves no pre-registered number.
Touches the posted predicate not at all. Neither is on the fire path, and
neither requires the sweep to be re-run.
