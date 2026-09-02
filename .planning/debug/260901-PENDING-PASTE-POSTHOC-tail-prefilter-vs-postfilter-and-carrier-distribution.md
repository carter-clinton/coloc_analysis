# PENDING PASTE — the DEFINED-row tail: PRE-filter or POST-filter, and the informative-carrier distribution

STATUS: STAGED — NOT RUN

Nothing in this document has been executed. It fires nothing on its own. Running
it requires an in-perimeter VM, which is **STOPPED**; starting it is Carter's
call, not this document's.

⚠ This is a NEW document. It does **not** modify
`.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md`
(whose BLOCK A has already **FIRED** — re-marking it STAGED would make it lie),
and it does **not** modify the live sweep runbook
`.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`.

---

## WHAT IT ANSWERS

**Are the 3,094 DEFINED rows carrying `max(del_carriers_lost_frac,
partner_carriers_lost_frac) >= 0.9` PRE-filter or POST-filter?**

* **PRE-filter** — a member of the pair is on the production excludelist, so the
  posted rule **already discards them**. The bad `r` never enters the panel. This
  is a characterisation of what the rule is correctly throwing away.
* **POST-filter** — **neither** member is on the excludelist, so the pair
  **survives into the banked LD matrix** and a noise-dominated finite `r` is
  consumed by SuSiE as though it were a measurement.

## WHY THE SWEEP COULD NOT ANSWER IT — IT WAS UNMEASURED, NOT MIS-SCOPED

Two reasons, both structural, neither a defect in the numbers already banked:

1. **`pairwise_completeness_scan` enumerates from the RAW `.bim` and never
   applies `--exclude`.** Its own docstring says the `--exclude` side is only
   PARTLY visible from what it emits. `already_occluded` is ANCHOR-RELATIVE
   (`deletion.pos < partner.pos <= deletion.span_end` against **that row's**
   anchor only); the production excludelist is `detect_occluded_variants` over
   **every** deletion in the window.
2. **`pcs_panelwide_reclassify` filtered its row set to `undefined` rows.** All
   **353,074** defined rows were **READ** and never **CLASSIFIED**. The machinery
   was correct; it was pointed at the wrong subset.

The tool has now been extended to classify the defined tail against the **same
per-region excludelist it already builds** — one `detect_occluded_variants` call
per region, shared by both scopes, never a second call with a different row set.

**The denominator, settled:** 353,074 = 353,089 candidate rows − 15 undefined.
3,094 / 353,074 = 0.876%.

---

## PRE-FLIGHT — run BEFORE either command; each check has a STOP

```bash
cd ~/coloc_analysis
git branch --show-current          # EXPECT m3-W2-aou-deltas, never main
git log --oneline -1

ls -l /home/jupyter/occ_measure/pcs_pairs.tsv \
      /home/jupyter/occ_measure/pcs_summary.json
md5sum /home/jupyter/occ_measure/pcs_pairs.tsv
wc -l  /home/jupyter/occ_measure/pcs_pairs.tsv
ls -l  /home/jupyter/afr_cohort.bim
```

* **`pcs_pairs.tsv` must be THE BANKED ARTIFACT.** Verify, do not assume:
  `md5 287b16b1991f63423ff3933996c0334d`, `wc -l` **353090**, size
  **107,304,497 B**. Its sha256 as recorded by the 2026-09-01 reclassification
  provenance is `eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583`.
  If any of these differ: **STOP.** A different input answers a different
  question and no number below is comparable.
* **`pcs_summary.json` must be the banked one** —
  `md5 4917c46d7348de6a5c9f3da83bc610b8`, **16,412 B**. It is passed to
  `--pcs-summary`, which sums the scanner's own `n_defined_lost_frac_ge_0p9` over
  the scanned regions and **RAISES before writing anything** if it disagrees with
  this run's `n_tail_rows_in`. If the file is absent: **STOP** and ask, rather
  than dropping the flag — dropping it removes the only runtime check that the
  tail predicate has not drifted from the scanner's.
* **`afr_cohort.bim` must be the same panel:** `20767864` lines, sha256
  `9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99`. A different
  `.bim` is a different row set, and every POST-filter verdict is relative to the
  row set (see THE CONDITION below).

```bash
ls -l /home/jupyter/occ_measure/pcs_tail_smoke.tsv \
      /home/jupyter/occ_measure/pcs_tail_smoke.json \
      /home/jupyter/occ_measure/pcs_tail_verdicts.tsv \
      /home/jupyter/occ_measure/pcs_tail_summary.json 2>&1
```

* **If ANY output path is occupied: ROTATE, NEVER DELETE** (the standing project
  ruling) —
  `mv <path> <path>.PRE-$(date -u +%Y%m%dT%H%M%SZ)` — then re-check. Refuse to
  overwrite. The 2026-08-31 rotation is why the contaminated 26-Aug artifacts are
  still inspectable with their original mtimes.

---

## STEP 1 — SMOKE FIRST: one region

`m2_region_00149` is the largest banked window (`n_rows_in_window 338354`) and it
carries the one surviving undefined pair, so it exercises both scopes and the
worst per-region cost in a single pass.

```bash
cd ~/coloc_analysis
python3 src/python/pcs_panelwide_reclassify.py \
  --pairs-tsv /home/jupyter/occ_measure/pcs_pairs.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --regions-tsv config/ld_regions.tsv \
  --ancestry AFR \
  --region-ids m2_region_00149 \
  --pcs-summary /home/jupyter/occ_measure/pcs_summary.json \
  --out /home/jupyter/occ_measure/pcs_tail_smoke.tsv \
  --summary /home/jupyter/occ_measure/pcs_tail_smoke.json
```

**STOP if it exits non-zero.** The tool validates every input before opening
either output, so a failure leaves no partial artifact. Read the error: a
`--pcs-summary` disagreement, a missing member vid, or a manifest/ancestry
mismatch are all deliberate hard stops, not warnings.

⚠ With `--region-ids` given, the run is NARROWED on purpose and
`n_defined_rows_out_of_scope` / `n_tail_rows_out_of_scope` will be large. That is
the smoke's basis, not a finding. Only STEP 2 answers the question.

## STEP 2 — the full 21-region run

```bash
cd ~/coloc_analysis
python3 src/python/pcs_panelwide_reclassify.py \
  --pairs-tsv /home/jupyter/occ_measure/pcs_pairs.tsv \
  --bfile-prefix /home/jupyter/afr_cohort \
  --regions-tsv config/ld_regions.tsv \
  --ancestry AFR \
  --pcs-summary /home/jupyter/occ_measure/pcs_summary.json \
  --out /home/jupyter/occ_measure/pcs_tail_verdicts.tsv \
  --summary /home/jupyter/occ_measure/pcs_tail_summary.json
```

Then bank the anchors before reading anything:

```bash
md5sum /home/jupyter/occ_measure/pcs_tail_verdicts.tsv \
       /home/jupyter/occ_measure/pcs_tail_summary.json
ls -l  /home/jupyter/occ_measure/pcs_tail_verdicts.tsv \
       /home/jupyter/occ_measure/pcs_tail_summary.json
```

---

## COST NOTE — a BASIS, explicitly NOT a prediction

The 2026-09-01 reclassification is the only measurement that exists:

* it built excludelists for **6** regions — `n_rows_in_window` totalling
  **1,011,893** rows (`00001` 102,421 · `00008` 207,147 · `00062` 86,719 ·
  `00081` 196,219 · `00120__sub03` 81,033 · `00149` 338,354);
* it ran **1h53m** (02:29:11Z → 04:22:50Z), exit 0, ~99% CPU throughout;
* that time includes **two full streamed sha256 passes** over a **20,767,864**-line
  `.bim` plus one over the 107 MB pairs TSV — provenance, not overhead: a verdict
  that cannot name the bytes it was computed against is not reproducible.

This run builds excludelists for **all 21** regions carrying rows, and
`detect_occluded_variants` is quadratic in the deletions of a window. **No runtime
is stated here.** The 6-region figure is the extrapolation BASIS and nothing more;
a number invented from it would be exactly the "estimate calibrated on the wrong
amount of work" that made the sweep's own 4h20m guess wrong by 4×.

---

## WHAT EACH ANSWER MEANS — the fork, both branches, stated BEFORE the run

Read `n_tail_rows_neither_member_occluded_panelwide` (and its PAIR twin
`n_tail_pairs_neither_member_occluded_panelwide`) from
`pcs_tail_summary.json`'s `pooled` block.

* **`== 0` → PRE-FILTER.** The posted rule already discards every tail row. The
  bad `r` never enters the panel. In Seth's terms: *"important, but not a policy
  gap"* — his Q4 answer stays wrong as reasoning and harmless in effect. Action:
  **amend for neither finding and disclose both** (the tail as a characterisation,
  the single surviving occlusion pair as a disclosed residual).
* **`> 0` → POST-FILTER.** Those pairs survive into the banked LD matrix. In
  Seth's terms: *"a prevalent, systematic, silent corruption in the banked LD
  matrix … and that is a different and much larger finding than anything else on
  this thread"*, and **unambiguously pre-registration-level**. Action: **amend for
  the TAIL**, folding the single surviving occlusion pair into that same amendment
  as a disclosed residual — one amendment, driven by the systematic finding.

**THE CONDITION, STATED ONCE AND ATTACHED.** Occlusion is MONOTONE in the row
set. A **PRE-filter** verdict (a member IS on the excludelist) is **SOUND**. A
**POST-filter** verdict (NEITHER member is) is **CONDITIONAL** on the row set
named in `provenance` — `bim_path` / `bim_sha256` / `bim_n_lines` and the
per-region `n_rows_in_window` — and can flip to PRE-filter once more rows are
supplied. It cannot flip the other way. The tool prints this sentence
(`tail_verdict_scope`) **inside the split's own block**; do not quote the numbers
without it.

Also read, and do not collapse into each other:

* the **ROW** counts and the **PAIR** counts — different quantities, one a known
  undercount of the other;
* `n_defined_rows_member_occluded_panelwide` + `n_defined_rows_reaching_matrix`
  against `n_defined_rows_in` − `n_defined_rows_out_of_scope` (the in-scope
  identity the tool reconciles or refuses to write);
* `n_defined_rows_rarer_and_min_definitions_disagree` — the rows where `the rarer
  variant` (by marginal MAF) and the precision-binding minimum retained count
  name **different** members. A near-miss between the two is not evidence they
  agree.

### NO EXPECTED VALUE IS STATED

Not for `n_tail_rows_in`, not for either side of the split, not for any
percentile. The whole point is that this quantity has never been computed. A
mismatch against an expectation nobody wrote down cannot be a finding, and an
expectation written down now would be a number picked from what we hope passes.

### NO CARRIER FLOOR IS PROPOSED

The tool emits the informative-carrier **DISTRIBUTION** —
`informative_carriers_percentiles_defined_rows` and its
`..._reaching_matrix` twin, plus exact counts for every `m` in `0..100` and the
cumulative `n_le_*` low tail. It proposes **no floor**, applies none, and carries
a machine-enforced guard that fails if one is ever declared, applied or named.
Seth withheld the value deliberately: *"picking a number from 'what passes' is the
error we have now made twice."* His `m = 25 → SE(r) ~ 0.20` / `m = 100 → ~0.10` is
CALIBRATION CONTEXT for the record only and is not adopted anywhere.

---

## EGRESS

The `pooled` / `per_region` aggregate counts, the percentile and low-tail blocks,
and the NAMED variant ids only. **The per-row verdict TSV stays in-perimeter.**
Every emitted field is a count, a fraction, a coordinate, an id or a label — no
per-sample vector, no sample identifier, no dosage. Emission is bounded to
UNDEFINED + TAIL rows and the tool refuses to return if that bound is violated.

## WHAT THIS DOES NOT DO

It opens no `.bed`, decodes no genotype, computes no LD, moves no criterion,
threshold, manifest or policy, and **cannot require the sweep to be re-run** —
the sweep's output is its input. It does not revise `353089` / `353090` /
`353074`, the 15 rows / 13 pairs / 10-3 split, the offset histogram, or the
panel-wide 12-1 pairs and 14-1 rows. It ADDS a derived quantity beside them.
