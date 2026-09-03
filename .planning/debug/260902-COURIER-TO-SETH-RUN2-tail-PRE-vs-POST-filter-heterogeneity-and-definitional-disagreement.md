# RUN 2 STEP 2 — the DEFINED-row tail is PRE-filter DOMINANT with a POST-filter RESIDUAL IN EVERY REGION; the regions do NOT share a common POST rate; rarer-vs-min disagreement is a SEPARATE axis

> Provenance: drafted in-repo 2026-09-02 against the RUN 2 STEP 2 artifacts. Status line for the record:
> measurement banked; nothing fired; VM STOPPED; $0; docs-only — `src/` and `tests/` untouched; no OSF contact;
> an agent never posts and never fires.

Seth conceded Q4 and then declined the rest of the consultation until one thing was settled.
**Are the 3,094 DEFINED rows carrying `max(del_carriers_lost_frac, partner_carriers_lost_frac) >= 0.9`
PRE-filter or POST-filter?** PRE-filter means the posted rule already discards them and the tail is a
*characterisation*. POST-filter means they survive into the banked LD matrix and the tail is, in his
words, "a prevalent, systematic, silent corruption." RUN 2 STEP 2 answered it.

**Both — and the POST residual is present in every single region.**

This file is the bank record and the courier in one. It is written to be read by someone who was not in
the session: it states what was run, on which artifacts, what came out, what it means, what it does NOT
establish, and what is being asked. Nothing else needs to be open to read it.

## WHAT THIS BANKS, AND WHERE EVERY NUMBER COMES FROM

Every number in this record originates in
`.planning/quick/260902-vsp-bank-the-run-2-step-2-tail-pre-post-resu/CONTENT-SPEC.md`
(md5 `20fb7fa058b0e0c03ff669706f534349`, **10672** B, 157 lines), which is committed alongside this
file so the appendix has an in-repo origin. The **VERBATIM APPENDIX** at the bottom is spliced **BY
SCRIPT** from that file, `## ARTIFACTS` to EOF, and a checker re-reads BOTH files at verification time
and fails unless the appendix bytes are equal to that slice. **The appendix is the authority.** The
prose above it restates; it never re-derives. Where prose and appendix could ever disagree, the
appendix wins and this sentence is the instruction to treat it that way.

One provenance note, so the plan file committed beside this record does not read as a contradiction:
the plan pinned an EARLIER revision of the spec (`d10acca5ca2b6c15548bb50d5c11bc43`, 8248 B, 124
lines). That revision was **SUPERSEDED at source before execution** — deliberately, not by drift — to
correct a mis-attribution described in the next two sections. Everything outside those sections is
byte-identical between the two revisions. The anchor that governs this record is the 10672-B one.

## THE RUN

Two artifacts, both written **2026-09-02T21:07:03Z**, launched 18:26:17Z, **2 h 40 m 46 s** wall:

* `pcs_tail_verdicts.tsv` — md5 `960f283734aea3b2c56c9249cf4fe94b`, 1031086 B
* `pcs_tail_summary.json` — md5 `bd74c0d502d15ac4e2fb5e1bdafc72b1`, 38548 B

**They live on the AoU VM, not in this repo.** The VM is STOPPED. Nothing in this task read them, and
nothing in this task started anything to read them; the numbers below were transcribed into
`CONTENT-SPEC.md` when the artifacts were inspected, and this record works from that spec.

Run-level provenance (there is NO per-region provenance block):

* `bim_sha256` `9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99` (20,767,864 lines)
* `pairs_tsv_sha256` `eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583` (353,090 lines)
* `regions_tsv_sha256` `e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a` — **VERIFIED IN
  THIS SESSION** to equal `sha256sum config/ld_regions.tsv` at HEAD.
* ancestry AFR; `region_ids_out_of_scope = []` (empty).

⚠ `region_ids_selected = 276` is the **ancestry-resolved MANIFEST size**, NOT the number of regions
carrying rows. **21 regions carry rows.** Any reading that treats 276 as a denominator for the
per-region statistics below is wrong.

## COMPLETION CHECK — THREE VALUES, ALL THREE PASS, AND THEY ARE **NOT** A PRE-REGISTRATION

| quantity | measured | expected | verdict |
| --- | --- | --- | --- |
| `n_tail_rows_in` | 3094 | 3094 | PASS |
| `n_tail_rows_out_of_scope` | 0 | 0 | PASS |
| `n_defined_rows_out_of_scope` | 0 | 0 | PASS |

⚠ **These three are NOT a pre-registration and this record does not call them one.** They were stated
before the run finished, but they were never uncertain:

* **3094 was ALREADY MEASURED.** The smoke on `m2_region_00149` returned 456 in-scope + 2,638
  out-of-scope = 3,094. It was CARRIED FORWARD, not predicted.
* **The two zeros follow BY CONSTRUCTION** once all 21 regions are in scope.

What they establish is narrower and still worth having: the run **COMPLETED** rather than **RAISED** at
the runtime `_reconcile_against_scanner_summary` check
(`src/python/pcs_panelwide_reclassify.py:1106`), which closes this run's tail predicate against the
**SCANNER'S OWN** `n_defined_lost_frac_ge_0p9` across all 21 regions and **writes nothing on
disagreement**. That is a real and useful guarantee. It is an **INVARIANT CHECK**, not a prediction that
could have come out otherwise.

## THE TWO PRE-REGISTRATIONS — NAMED SEPARATELY, NEVER MERGED

There are two, they belong to two different runs, and merging them would manufacture a confirmation
that was never at risk.

**(1) RUN 1's pre-registration — genuine, and CONFIRMED.**
`.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
§(e) *"PRE-REGISTERED PREDICTION — RECORDED BEFORE THE RE-RUN"* states, before the re-run:
`n_undefined_rows` 15, `n_undefined_distinct_pairs` 13, `already_occluded` 10 / not-already-occluded 3,
the offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, POOLED candidate rows 353089,
`wc -l pcs_pairs.tsv` 353090. It was answered by **RUN 1** and **CONFIRMED 5/5 plus the histogram, with
ZERO adjustments, on 2026-09-01**.

⛔ It contains **NONE** of `n_tail_rows_in`, `n_tail_rows_out_of_scope` or
`n_defined_rows_out_of_scope` — verified, zero occurrences of each. **No sentence anywhere in this record
claims that file pre-registered the three completion-check values.**

**(2) The pre-registration governing THIS run — which deliberately declines to predict.**
`.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`
is the runbook for RUN 2 STEP 2, and at `:211-216` it says, in full:

> ### NO EXPECTED VALUE IS STATED
>
> Not for `n_tail_rows_in`, not for either side of the split, not for any percentile. The whole point
> is that this quantity has never been computed. A mismatch against an expectation nobody wrote down
> cannot be a finding, and an expectation written down now would be a number picked from what we hope
> passes.

That refusal covers exactly what follows: the **PRE/POST split**, the **heterogeneity** and the
**definitional-disagreement axis** are **MEASURED, NOT PREDICTED**. **This is a STRENGTH, not a gap.**
It is the reason none of the three findings below can have been shaped by an expectation — there was no
expectation to shape them. The record does not apologise for it and does not work around it.

## FINDING 1 — THE TAIL IS PRE-FILTER DOMINANT, WITH A POST-FILTER RESIDUAL IN EVERY REGION

| basis | PRE | POST | total | POST share |
| --- | --- | --- | --- | --- |
| rows | 2560 | 534 | 3094 | **17.26%** |
| pairs | 2047 | 474 | 2521 | **18.80%** |

**21 regions carry tail rows. ZERO regions have zero POST rows.**

Pooled DEFINED-row accounting: `n_rows_in_tsv` 353089; `n_defined_rows_in` 353074;
`n_undefined_rows_in` 15; `n_defined_rows_member_occluded_panelwide` 7475;
`n_defined_rows_reaching_matrix` 345599; `n_pairs_with_ambiguous_member_id` 0.

**What this means for the fork.** It is not the clean PRE-filter answer that would have made the tail a
characterisation and closed the question — 17.26% of tail rows, and 18.80% of tail pairs, reach the
matrix. It is also not a uniform POST-filter failure: the strong majority is already discarded by the
posted rule. The load-bearing fact is the one in the middle: **the residual is not concentrated in a
handful of regions that could be quarantined. It is present in every single one of the 21.**

## FINDING 2 — THE REGIONS DO NOT SHARE A COMMON POST RATE

**Headline, pair-level, dropping `m2_region_00060__sub13` (78.5% inside sub12's window):
chi2 37.78, dof 19, p 6.3e-3, overdispersion 1.99x.** This is the figure to quote.

The all-21 pair-level figure is **chi2 47.24, dof 20, p 5.4e-4, overdispersion 2.36x**, and it is
shown here only with its explanation: it is **INFLATED by the chr15 overlap**, whose two regions rank
2nd and 3rd on POST fraction and are largely one locus. Quoting 2.36x unqualified would be counting one
locus twice. Row-level, all 21: chi2 51.25, dof 20, p 1.5e-4, overdispersion 2.56. Row-level POST
fraction ranges **8.33% – 36.36%**, CV 0.365.

Whichever figure is used, a single pooled POST rate does not describe these regions.

**UNEXPLAINED — no structural covariate accounts for it:**

* `spearman(POST frac, window rows)` = **-0.199**
* `spearman(POST frac, occluded ids)` = **-0.201**
* `spearman(POST frac, occlusion density)` = **+0.004**

…in a design with the power to find `spearman(tail rows, window rows)` = **+0.886**. That last clause is
the power argument, and it should be read as one: **this design CAN detect a strong structural
correlation across these 21 regions, and did — just not for the POST rate.** The heterogeneity is
therefore an open question, not an artifact of a covariate we forgot to look at.

## FINDING 3 — DEFINITIONAL DISAGREEMENT, A SEPARATE AND INDEPENDENT AXIS

Rows where `informative_carriers_rarer != informative_carriers_min`:

| stratum | disagreeing | total | rate |
| --- | --- | --- | --- |
| in tail | 751 | 3094 | **24.27%** |
| below tail | 1826 | 349980 | **0.52%** |

**Enrichment 46.5x.** **NOT a tie artifact:** `rarer_by_maf_tie` is False for **ALL 3094** tail rows.

**Independence from the PRE/POST axis is carried by `spearman(POST frac, disagree frac) = +0.173` over
the 21 regions.** ⚠ The PRE-vs-POST 2x2 is reported for completeness and is **deliberately NOT used as
support**: 606/2560 = **23.67%** PRE vs 145/534 = **27.15%** POST, chi2 2.914, p **0.088**, Fisher p
**0.096**, with POST trending **HIGHER**. That is **UNDERPOWERED, NOT NULL**, and treating a p of 0.088
as evidence of independence would be exactly the inference this record refuses. The independence claim
leans on the rho.

This axis is also heterogeneous, but less so: chi2 37.80, dof 20, p 0.0094, overdispersion 1.89, CV
0.196; tail disagreement spread by region **13.7% – 32.1%**.

**The definitions, because the disagreement is definitional and not a bug.** "Rarer" is decided by
`*_maf_marginal` — each member's MAF over its **OWN** called set — and **never** by carrier counts,
**because `n_called_del != n_called_partner` IS the phenomenon under study**; deciding rarity by carrier
count would let the phenomenon define its own measurement.
`informative_carriers_min = min(del_retained, partner_retained)`. The two are emitted side by side
because `SE(r) ~ 1/sqrt(m)` binds on the **MINIMUM**, while the rarer-variant definition is the
scientifically motivated one. They name different members in 24.27% of tail rows, and both are needed.

## THE THREE FINDINGS ARE INDEPENDENT

They are three findings, not one result described three ways.

1. **The PRE/POST split** — where the tail rows go.
2. **The between-region heterogeneity of the POST rate** — whether one number describes them.
3. **The rarer-vs-min definitional disagreement** — which member the precision bound names.

The axis linking (1) and (3) is **measured**, not assumed:
`spearman(POST frac, disagree frac) = +0.173` over 21 regions. A reader is entitled to demand that
number before accepting three disclosures where one might do; it is why there are three.

## ALSO BANKED

**Seth's class (i) is EMPTY.**

**The ONE surviving pair:** region `m2_region_00149`, deletion `chr7:89454077:GCGTA:G`, partner
`chr7:89454076:C:T`, offset **-1**, side upstream, `already_occluded` False, `pair_key`
`9776035|9776036`. Offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}` — **NO positive offset
anywhere in the panel.**

**`chr7:89454077` CANNOT be sited as at-signal versus cold-sequence.** No genome-wide fine-mapping
exists for this panel — only the Track A candidate-locus products under
`results/multitrait/coloc_susie_R2*`, and **NO MTAG outputs**. Siting the deletion requires
genome-wide fine-mapping that is **BLOCKED ON THIS VERY PANEL**: the panel is the input to the work
that would answer the question about the panel. **This is declared BLOCKED, not skipped**, and it does
not become answerable by trying harder with what exists today.

**Informative-carrier distribution** (percentiles p0 / p1 / p5 / p10 / p25 / p50 / p75 / p90 / p99 / p100):

| set | percentiles |
| --- | --- |
| `defined_rows` | 1 / 413 / 792 / 907 / 1419 / 3239 / 7959 / 15948 / 39551 / 54843 |
| `reaching_matrix` | 2 / 728 / 813 / 934 / 1461 / 3314 / 8074 / 16098 / 39630 / 54843 |

Low-tail cumulative: `defined_rows` n_le_1 = 4, n_le_100 = 1938, n_gt_100 = 351136 (sum 353074, OK);
`reaching_matrix` n_le_1 = 0, n_le_100 = 313, n_gt_100 = 345286 (sum 345599, OK).

**NO row has zero informative carriers, and the matrix-reaching set has NO singletons.**
**NO CARRIER FLOOR IS PROPOSED**, applied, or named — here or anywhere in the tool. The tool emits the
distribution only. Seth withheld a floor value deliberately; this record does not supply one, and does
not ask for one.

## SCOPE CAVEATS

Six of them. Each is stated here, in prose, in its own subsection — not as a footnote, not softened,
and not left to the appendix alone.

### (1) `n_tail_distinct_pairs_in = 2521` is a SUM, not a panel-wide dedup

It is the **SUM of per-region distinct pairs**, verified identical to the per-region column sum. A pair
appearing in two regions is counted twice in that total. It is NOT a panel-wide deduplicated count and
must not be quoted as one.

### (2) `pair_key` is INDEX-keyed DELIBERATELY, and deletion-deletion neighbours are STRUCTURAL

`_pair_key` (`src/python/pairwise_completeness_scan.py:508`) is order-normalised over the two
**globally-unique `.bim` ROW INDICES**. A vid-based key would **UNDERCOUNT**, because two `.bim` rows
can share an id. **564 of 2461** panel-wide pairs (**22.9%**) are **DELETION-DELETION NEIGHBOURS**
contributing **two anchored rows each** — a **STRUCTURAL property of the tail, NOT a defect**. Closure
verified: **1897 + 2*564 = 3025**, **+ 69 cross-region = 3094** tail rows.

⚠ `already_occluded` is **ANCHOR-RELATIVE**, so the two anchored rows of one such pair **SHOULD** differ.
That is not a conflict, and a reader who finds one such disagreement has not found a bug.

### (3) The chr15 overlap is the only one, and where it is testable the two adjudications agree

`m2_region_00060__sub12` x `__sub13` share **6,000,001 bp** (78.5% of sub13, 56.4% of sub12). It is the
**ONLY** overlap among the 21 — all **210** pairs were enumerated against `config/ld_regions.tsv`.
**69** ordered rows are adjudicated **TWICE**, under two DIFFERENT excludelists built over two DIFFERENT
row sets; **69/69 agree** on the exact `(del_occ, partner_occ)` tuple, zero disagreements. "Final for its
region" therefore holds **where it is testable** — which is these 69 rows, and not by proof everywhere.

### (4) The below-tail disagreement count has NO regional attribution

`n_defined_rows_rarer_and_min_definitions_disagree` has **NO per-region emission**. The per-region
spread quoted in FINDING 3 (13.7% – 32.1%) is available for the **TAIL only**, from the TSV. The
**1826** below-tail disagreements have **NO regional attribution in this artifact** — the 0.52% is a
pooled rate and cannot be decomposed from what was written.

### (5) Provenance is RUN-LEVEL only

There is one shared `bim_sha256` and no per-region provenance block. Per-region monotonicity conditions
attach via `n_rows_in_window` against that single shared hash, not against per-region hashes.

### (6) MONOTONICITY — why these verdicts are final for their region

Occlusion is **monotone in the row set**: an **OCCLUDED** verdict computed on a subset is **SOUND**,
while a **NOT-OCCLUDED** verdict computed on a subset is **CONDITIONAL** on no further rows arriving.
Each region's window is **COMPLETE at `pad_bp=0`** against fixed manifest bounds with **ONE excludelist
per region**, so these verdicts are **FINAL for their region** and do **NOT** shrink as regions are
added.

## HONEST LIMITATIONS

The run finished during a **VM blackout**. The machine rebooted; `uptime` showed 14 min against a
21:07:03Z write. **The full stdout and the exit status `$?` are UNRECOVERABLE and were NEVER SEEN by
anyone.** The completion verdict rests entirely on the three completion-check values plus the
artifacts. There is **NO pre-reboot hash**, so the recorded md5s **anchor FORWARD, not backward** —
they cannot prove byte-identity to what was written at 21:07:03Z.

What they DO establish is bounded and worth stating exactly: **a damaged file would not have parsed and
summed to exactly 3094 / 0 / 0.** That is the whole of it. No consoling clause is appended.

⚠ One wording note, so the appendix is not read as a contradiction of the COMPLETION CHECK section: the
appendix's own HONEST LIMITATIONS paragraph still says "the three **pre-registered** values." That
phrase predates the correction recorded above, and it is reproduced **unedited** because the appendix is
byte-equal by construction and must not be touched. **The governing characterisation is the COMPLETION
CHECK section: those three values are an INVARIANT CHECK, not a pre-registration.**

## ACTION ITEM — THE 0.0005 BOUND IS A LIVE CONTRADICTION (NOT FIXED HERE)

Four citations, each verified present in the tree at execution time:

* `src/python/pairwise_completeness_scan.py:45` — "…the error that produced the withdrawn ``0.0005``
  bound."
* `src/python/condition_ld_matrix.py:120` — `ceiling_frac: float = 0.0005` (**live default**)
* `src/python/write_conditioned_ld_npz.py:64` — `ceiling_frac: float = 0.0005` (**live default**)
* `src/python/write_conditioned_ld_npz.py:17` — "…``ceiling_frac`` records the pre-registered 0.0005
  ceiling for reproducibility (a fixed pre-registration constant…"

**One module calls the bound withdrawn while another calls it pre-registered, and the value is LIVE in
both.** At most one of those docstrings can be true.

**This task is DOCS-ONLY and deliberately does NOT fix it.** `git status --porcelain -- src tests` is
empty at commit time. The code fix belongs to a **SEPARATE** task, which must decide which reading is
correct, make both docstrings agree with the live default, and land a named enforcer test so the
agreement has a guard rather than a belief. Recorded in this task's `deferred-items.md`.

## THE ASK

Not a re-read of everything. Three specific things, scoped:

1. **Does the every-region POST residual change your PRE/POST fork disposition?** The answer came back
   "both": 17.26% of tail rows reach the matrix, and no region is clean. That is neither the
   characterisation nor the uniform corruption the fork was drawn around.
2. **Does the unexplained heterogeneity change what must be pre-registered?** 1.99x overdispersion
   after removing the chr15 double-count, with no structural covariate accounting for it, in a design
   that finds `spearman(tail rows, window rows) = +0.886` when a structural relationship is there.
3. **Is the rarer-vs-min disagreement a third disclosure, or a property of the first?** 46.5x tail
   enrichment, independent of PRE/POST at rho +0.173, with the 2x2 explicitly declared UNDERPOWERED
   rather than null.

**No carrier floor is proposed, and none is being requested.** The distribution is reported so that a
floor, if one is ever warranted, is chosen against data rather than against a hoped-for pass rate.

## VERBATIM APPENDIX — CONTENT-SPEC.md `## ARTIFACTS` .. EOF (spliced by script)

Spliced BY SCRIPT, never retyped. A checker re-reads both files at verification time and fails
unless the bytes between the two markers below are equal to `CONTENT-SPEC.md` from `## ARTIFACTS`
to EOF. This appendix is the authority for every number in this record.

<!-- BEGIN VERBATIM APPENDIX (byte-equal to CONTENT-SPEC.md from '## ARTIFACTS' to EOF) -->
## ARTIFACTS (on the AoU VM, not in this repo)
pcs_tail_verdicts.tsv  md5 960f283734aea3b2c56c9249cf4fe94b  1031086 B
pcs_tail_summary.json  md5 bd74c0d502d15ac4e2fb5e1bdafc72b1    38548 B
both written 2026-09-02T21:07:03Z; launched 18:26:17Z; 2 h 40 m 46 s wall.

## PROVENANCE (run-level; there is NO per-region provenance block)
bim_sha256        9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99  (20,767,864 lines)
pairs_tsv_sha256  eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583  (353,090 lines)
regions_tsv_sha256 e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a
  -> VERIFIED IN THIS SESSION to equal `sha256sum config/ld_regions.tsv` at HEAD.
ancestry AFR. region_ids_selected = 276 = the ancestry-resolved MANIFEST size.
  ⚠ 276 is NOT the number of regions carrying rows. 21 regions carry rows. Say this explicitly.
region_ids_out_of_scope = [] (empty).

## COMPLETION CHECK — all three PASS
n_tail_rows_in               measured 3094  expected 3094  PASS
n_tail_rows_out_of_scope     measured 0     expected 0     PASS
n_defined_rows_out_of_scope  measured 0     expected 0     PASS

⚠ THESE THREE ARE **NOT** A PRE-REGISTRATION, and the record must NOT call them one.
They were stated before the run finished, but they were never uncertain:
  - 3094 was ALREADY MEASURED — the smoke on m2_region_00149 returned 456 in-scope
    + 2,638 out-of-scope = 3,094. It was CARRIED FORWARD, not predicted.
  - the two zeros follow BY CONSTRUCTION once all 21 regions are in scope.
What they establish is that the run COMPLETED rather than RAISED at the runtime
`_reconcile_against_scanner_summary` check (pcs_panelwide_reclassify.py:1106), which
closes this run's tail predicate against the SCANNER'S OWN n_defined_lost_frac_ge_0p9
across all 21 regions and writes nothing on disagreement. That is a real and useful
guarantee. It is an INVARIANT CHECK, not a prediction that could have come out otherwise.

## THE TWO PRE-REGISTRATIONS — name them separately, never merge them
(1) `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
    §(e) is a GENUINE pre-registration: n_undefined_rows 15, n_undefined_distinct_pairs 13,
    already_occluded 10 / not 3, offset histogram {-14:1,-9:1,-6:1,-3:1,-1:1,0:10},
    POOLED candidate rows 353089, wc -l 353090. It was answered by RUN 1 and CONFIRMED
    5/5 + histogram with ZERO adjustments on 2026-09-01.
    ⛔ It contains NONE of n_tail_rows_in / n_tail_rows_out_of_scope /
      n_defined_rows_out_of_scope — verified, zero occurrences of each. Do NOT write any
      sentence claiming it pre-registered 3094/0/0.
(2) `.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`
    governs THIS run, and at :211-216 it DELIBERATELY DECLINES to state an expectation:
      "### NO EXPECTED VALUE IS STATED
       Not for `n_tail_rows_in`, not for either side of the split, not for any
       percentile. The whole point is that this quantity has never been computed. A
       mismatch against an expectation nobody wrote down cannot be a finding, and an
       expectation written down now would be a number picked from what we hope passes."
    QUOTE THIS IN THE RECORD and say what it covers. The PRE/POST split, the
    heterogeneity and the definitional-disagreement axis are therefore MEASURED-NOT-
    PREDICTED. That refusal is a STRENGTH — it is why none of the three findings below
    can have been shaped by an expectation — and the record must present it as one, not
    apologise for it.

## FINDING 1 — the tail is PRE-filter dominant, POST-filter residual in every region
ROWS   2560 PRE / 534 POST of 3094   POST = 17.26%
PAIRS  2047 PRE / 474 POST of 2521   POST = 18.80%
regions with tail rows = 21 ; regions with ZERO POST rows = 0
Pooled DEFINED: n_rows_in_tsv 353089; n_defined_rows_in 353074; n_undefined_rows_in 15;
  n_defined_rows_member_occluded_panelwide 7475; n_defined_rows_reaching_matrix 345599;
  n_pairs_with_ambiguous_member_id 0.

## FINDING 2 — the regions do NOT share a common POST rate (heterogeneity)
Pair-level, all 21 :   chi2 47.24  dof 20  p 5.4e-4   overdispersion 2.36
Pair-level, dropping m2_region_00060__sub13 (78.5% inside sub12's window):
                       chi2 37.78  dof 19  p 6.3e-3   overdispersion 1.99   <-- QUOTE THIS ONE
Row-level, all 21  :   chi2 51.25  dof 20  p 1.5e-4   overdispersion 2.56
Row-level POST fraction range 8.33% - 36.36%; CV 0.365.
⚠ Quote the REDUCED (1.99x) figure as the headline. The all-21 figure is inflated by the
  chr15 overlap, whose two regions rank 2nd and 3rd on POST fraction and are largely one locus.
UNEXPLAINED — no structural covariate accounts for it:
  spearman(POST frac, window rows)      = -0.199
  spearman(POST frac, occluded ids)     = -0.201
  spearman(POST frac, occlusion density)= +0.004
  ...in a design with the power to find spearman(tail rows, window rows) = +0.886.

## FINDING 3 — definitional disagreement, a SEPARATE and independent axis
informative_carriers_rarer != informative_carriers_min
  in tail      :  751 / 3094      = 24.27%
  below tail   : 1826 / 349980    =  0.52%
  enrichment   : 46.5x
NOT a tie artifact: rarer_by_maf_tie is False for ALL 3094 tail rows.
INDEPENDENT of PRE/POST: spearman(POST frac, disagree frac) = +0.173 over 21 regions.
  ⚠ Do NOT support independence with the PRE-vs-POST 2x2 (606/2560 = 23.67% vs
    145/534 = 27.15%, chi2 2.914 p 0.088, Fisher p 0.096, POST trending HIGHER).
    That is UNDERPOWERED, not null. Lean on the rho.
Also heterogeneous, but less so: chi2 37.80 dof 20 p 0.0094 overdispersion 1.89; CV 0.196.
Tail disagreement spread by region: 13.7% - 32.1%.
Definitions: "rarer" is decided by *_maf_marginal (each member's MAF over its OWN called
set), never by carrier counts, because n_called_del != n_called_partner IS the phenomenon
under study. informative_carriers_min = min(del_retained, partner_retained). They are
emitted side by side because SE(r) ~ 1/sqrt(m) binds on the MINIMUM while the rarer-variant
definition is the scientifically motivated one.

## ALSO BANK
- Seth's class (i) is EMPTY.
- The ONE surviving pair:
    region m2_region_00149
    deletion chr7:89454077:GCGTA:G   partner chr7:89454076:C:T
    offset -1, side upstream, already_occluded False, pair_key 9776035|9776036
  Offset histogram {-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}. NO positive offset anywhere.
- chr7:89454077 CANNOT be sited as at-signal vs cold-sequence. No genome-wide fine-mapping
  exists (only Track A candidate-locus results/multitrait/coloc_susie_R2*; NO MTAG outputs).
  It is BLOCKED ON THIS PANEL, not skipped. State plainly.
- Informative-carrier distribution (percentiles p0/p1/p5/p10/p25/p50/p75/p90/p99/p100):
    defined_rows      1 / 413 / 792 / 907 / 1419 / 3239 / 7959 / 15948 / 39551 / 54843
    reaching_matrix   2 / 728 / 813 / 934 / 1461 / 3314 / 8074 / 16098 / 39630 / 54843
  Low-tail cumulative: defined_rows n_le_1=4, n_le_100=1938, n_gt_100=351136 (sum 353074 OK)
                       reaching_matrix n_le_1=0, n_le_100=313, n_gt_100=345286 (sum 345599 OK)
  NO row has zero informative carriers; the matrix-reaching set has NO singletons.
  NO CARRIER FLOOR IS PROPOSED. The tool emits the distribution only.

## ACTION ITEM (flag it; do NOT fix it in this docs-only task)
The 0.0005 bound is a LIVE CONTRADICTION in the tree:
  src/python/pairwise_completeness_scan.py:45   calls it "the withdrawn 0.0005 bound"
  src/python/condition_ld_matrix.py:120         ceiling_frac: float = 0.0005   (live default)
  src/python/write_conditioned_ld_npz.py:64     ceiling_frac: float = 0.0005   (live default)
  src/python/write_conditioned_ld_npz.py:17     calls it "the pre-registered 0.0005"
One module says withdrawn, another says pre-registered, and the value is live in both.
Needs a code fix in a SEPARATE task.

## SCOPE CAVEATS — state these plainly, do NOT bury them
1. n_tail_distinct_pairs_in = 2521 is the SUM of per-region distinct pairs, NOT a
   panel-wide dedup. Verified identical to the per-region column sum.
2. pair_key is INDEX-keyed DELIBERATELY (pairwise_completeness_scan.py:508). A vid key
   would UNDERCOUNT, because two .bim rows can share an id. 564 of 2461 panel-wide pairs
   (22.9%) are DELETION-DELETION NEIGHBOURS contributing two anchored rows each — a
   STRUCTURAL property of the tail, NOT a defect. Closure verified: 1897 + 2*564 = 3025,
   + 69 cross-region = 3094 tail rows.
   ⚠ already_occluded is ANCHOR-RELATIVE, so the two anchored rows of one such pair SHOULD
     differ. That is not a conflict.
3. chr15 overlap: m2_region_00060__sub12 x __sub13 share 6,000,001 bp (78.5% of sub13,
   56.4% of sub12). This is the ONLY overlap among the 21 — all 210 pairs enumerated
   against config/ld_regions.tsv. 69 ordered rows are adjudicated TWICE under two DIFFERENT
   excludelists built over two DIFFERENT row sets; 69/69 agree on the exact
   (del_occ, partner_occ) tuple, zero disagreements. "Final for its region" holds where testable.
4. n_defined_rows_rarer_and_min_definitions_disagree has NO per-region emission. The
   per-region spread is available for the TAIL only (from the TSV). The 1826 below-tail
   disagreements have NO regional attribution in this artifact.
5. Provenance is RUN-LEVEL only. Per-region monotonicity conditions attach via
   n_rows_in_window against ONE shared bim_sha256.
6. MONOTONICITY: occlusion is monotone in the row set, so an OCCLUDED verdict on a subset
   is SOUND while a NOT-OCCLUDED verdict on a subset is CONDITIONAL. Each region's window
   is COMPLETE at pad_bp=0 against fixed manifest bounds with ONE excludelist per region,
   so these verdicts are FINAL for their region and do NOT shrink as regions are added.

## HONEST LIMITATIONS — do not soften
The run finished during a VM blackout (machine rebooted; `uptime` showed 14 min against a
21:07:03Z write). The full stdout and the exit status $? are UNRECOVERABLE and were NEVER
SEEN by anyone. The completion verdict rests entirely on the three pre-registered values
plus the artifacts. There is NO pre-reboot hash, so the recorded md5s anchor FORWARD, not
backward — they cannot prove byte-identity to what was written at 21:07:03Z. What they do
establish is that a damaged file would not have parsed and summed to exactly 3094/0/0.
<!-- END VERBATIM APPENDIX -->
