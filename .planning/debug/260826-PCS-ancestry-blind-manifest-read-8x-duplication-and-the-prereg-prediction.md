# PCS — the ancestry-blind manifest read, the 8x duplication, and the PRE-REGISTERED PREDICTION

**Date:** 2026-08-26 · **Branch:** `m3-W2-aou-deltas` · **Quick:** `260826-qq9`
**Instrument:** `src/python/pairwise_completeness_scan.py`
**Repaired in:** `d8f4d54` (T1 — the ancestry-keyed read) and `5078cdc` (T2 — defense in depth)

**The command whose output this record banks**, quoted from STEP 3 of
`.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` (that file
is NOT edited by this quick):

```
python3 - <<'EOF'
import subprocess, sys
SAMPLE = "/home/jupyter/occ_measure/occ_measure_sample.tsv"
ids = [l.split("\t")[0] for l in open(SAMPLE).read().splitlines()[1:] if l.strip()]
print("regions in the pre-committed sample:", len(ids))
cmd = [sys.executable, "src/python/pairwise_completeness_scan.py",
       "--bfile-prefix", "/home/jupyter/afr_cohort",
       "--regions-tsv", "config/ld_regions.tsv",
       "--region-ids", ",".join(ids),
       "--window-bp", "25",
       "--out", "/home/jupyter/occ_measure/pcs_pairs.tsv",
       "--summary", "/home/jupyter/occ_measure/pcs_summary.json"]
print(" ".join(cmd), flush=True)
raise SystemExit(subprocess.call(cmd))
EOF
```

Note what that command does NOT contain: an `--ancestry` token. After the T1
repair the scanner's default is `AFR`, which is the cohort `/home/jupyter/afr_cohort`
holds — so the sweep command above becomes CORRECT **unmodified**. That is why
the default is load-bearing and why the PENDING PASTE was left byte-unchanged.

---

## VERDICT, IN ONE LINE

**The identity-level findings SURVIVE. Every row-basis COUNT is CONTAMINATED by
an 8x duplication and must not be quoted.** The manifest
`config/ld_regions.tsv` is keyed on `(region_id x ancestry)` — 553 lines =
1 header + 276 ids x {AFR, EUR} — and the shipped `_read_regions_tsv` read only
0-based columns 0/1/14/15, so it returned every window TWICE.

**Disclosure class:** aggregate counts + variant coordinates/IDs only — the same
class as the already-banked STEP 1 record
(`.planning/debug/260826-STEP0-1-falsifier-PAIRWISE-COMPLETE-as-received.md`).
`pcs_pairs.tsv` stays in-perimeter; it was never pasted, copied or reconstructed.
Nothing was fired to produce this record: zero VM / Dataproc / OSF / `gsutil` /
`gcloud` / network contact, $0.

**Source of every quoted number:** the in-repo artifact
`.planning/quick/260826-qq9-fix-ancestry-blind-region-manifest-read-/260826-qq9-AS-RECEIVED-step3-and-forensics.md`
(**8397 B**, md5 `22cbdd99b8d8714bfe2f22a2b499e58a`, verified at build time by the
script that assembled this record). Section (a) is its BLOCK 1 spliced in
verbatim; section (c) is its BLOCK 2 spliced in verbatim and then re-aggregated
BY SCRIPT. Nothing here was reconstructed from memory, and the last-resort
`NOT BANKED` placeholder is deliberately absent because the artifact exists.

---

## (a) THE STEP 3 SWEEP STDOUT, AS RECEIVED

Copied verbatim from **BLOCK 1** of the as-received artifact. Unedited: no number
is "corrected" in place, and nothing is filled in from the derived aggregates
further down.

```
pcs_pairs.tsv 871,038,152 B, pcs_summary.json 16,527 B, both 06:13Z.

wc -l /home/jupyter/occ_measure/pcs_pairs.tsv
2865514 /home/jupyter/occ_measure/pcs_pairs.tsv

Pooled lines, verbatim from stdout:

POOLED undefined-set offset histogram: {'-14': 4, '-9': 4, '-6': 4, '-3': 4, '-1': 4, '0': 40}
POOLED defined-row carriers_lost_frac bins: {'0': 1132296, '(0,0.25]': 291643, '(0.25,0.5]': 7631, '(0.5,0.9]': 8798, '(0.9,0.99]': 9979, '(0.99,1)': 2750}
POOLED candidate rows: 2865513
NOTE: these are COUNTS over the scanned regions. They are NOT a prevalence, NOT a boundary width, and NOT a tail size for the panel.

Per-region, derived from pcs_summary.json by script rather than transcribed:

region                  cand_rows    ndel undef_rows undef_pairs  alr_occ  NOT_occ  offsets
m2_region_00001             63008   15902         28           6        5        1  {'-14': 4, '-6': 4, '0': 20}
m2_region_00008            138844   33968          8           2        1        1  {'-3': 4, '0': 4}
m2_region_00017              3556    1146          0           0        0        0  {}
m2_region_00027             94296   22160          0           0        0        0  {}
m2_region_00033             13044    2944          0           0        0        0  {}
m2_region_00040__sub10      56706   16135          0           0        0        0  {}
m2_region_00042             24844    6640          0           0        0        0  {}
m2_region_00053             37216    8844          0           0        0        0  {}
m2_region_00060__sub12      70202   15826          0           0        0        0  {}
m2_region_00060__sub13      52318   11761          0           0        0        0  {}
m2_region_00062             53088   11050          4           1        1        0  {'0': 4}
m2_region_00063             80808   17108          0           0        0        0  {}
m2_region_00064             18752    4416          0           0        0        0  {}
m2_region_00081            156856   36132          8           2        2        0  {'0': 8}
m2_region_00088__sub01      65157   15004          0           0        0        0  {}
m2_region_00111__sub07      56360   14737          0           0        0        0  {}
m2_region_00120__sub03      52897   15575          8           1        1        0  {'-9': 4, '0': 4}
m2_region_00120__sub17      49977   14267          0           0        0        0  {}
m2_region_00145__sub14      57629   16013          0           0        0        0  {}
m2_region_00149            244656   59836          4           1        0        1  {'-1': 4}
m2_region_00161__sub13      62943   16313          0           0        0        0  {}

POOLED n_candidate_rows                                = 1453157
POOLED n_deletions                                     = 355777
POOLED n_undefined_rows                                = 60
POOLED n_undefined_distinct_pairs                      = 13
POOLED n_undefined_already_occluded                    = 10
POOLED n_undefined_not_already_occluded                = 3
POOLED n_undefined_rows_with_globally_invariant_member = 0
POOLED n_globally_invariant_variants                   = 0
POOLED n_candidates_edge_clipped                       = 0
POOLED offset histogram = {'-14': 4, '-9': 4, '-6': 4, '-3': 4, '-1': 4, '0': 40}

### Agent's own flags (as-received, not adjudicated in this file)

1. Three undefined pairs are NOT already occluded — one each in m2_region_00001,
   m2_region_00008, m2_region_00149. The 00149 case sits at offset -1, the exact
   mirror of the 00057 finding at +1.
2. m2_region_00001 is the banked Stage A region and shows 1 un-occluded undefined
   pair — in tension with the STEP 8-GATE result, where the 38,595,391,746 B
   re-read of the Stage A output found no NaN.
3. Two count discrepancies. POOLED candidate rows 2865513 matches wc -l exactly,
   but the per-region n_candidate_rows in the JSON sum to 1,453,157 — a difference
   of 1,412,356 that is not a clean factor of two. Separately, the per-region table
   printed every region twice with identical values.

Offsets are 0 (40 rows) and negative only. No positive offset appears anywhere in
this sweep, and m2_region_00057 is not a member of the 21-region pre-committed
sample, so the +1 case is unrepresented here.

### Agent's self-reported errors (as-received)

- A poll said to be scheduled for 05:36Z was never scheduled. The sweep finished
  06:13Z and sat undetected until 13:37Z — roughly 7.4 h of idle VM, ~$12.
- The ETA was wrong by ~5x: projected 19:00Z-21:00Z, actual finish 06:13Z, total
  runtime 4h18m. At 04:35Z it was called 15.6% complete with 16.5 h remaining; it
  had 1h38m left. The cost model assumed cost scales with variants-in-window.

### §1/§2/§5 answers (agent, same session)

- §1 — ld_regions.tsv: 552 region-id lines, 276 distinct ids, every id exactly
  twice, 276 AFR / 276 EUR.
- §2 — no nohup.out; STEP 3 launch truncated in history (heredoc); STEP 2
  invocation captured in full.
- §5 — STEP 2 output SAVED, confirmed on disk in pcs_00057_crosscheck.tsv.
```

### The evidence gap that STAYS OPEN

BLOCK 1's §5 answer records that **STEP 2's output IS on disk in-perimeter**, in
`pcs_00057_crosscheck.tsv`. Its **verbatim content has still never been pasted
into the NCSU session and is therefore still not banked here.** STEP 2 was
*reported* passed; that report is not the measurement
(`feedback_error_message_named_cause_is_not_the_measurement`). **Request it.**
Expected when it arrives: offset +1, undefined, `n_both_called 71048`,
`del_carriers_lost 871`.

### CONTAMINATED vs SURVIVING, figure by figure

| Reported figure | Class | Why |
|---|---|---|
| `n_candidate_rows` (per-region and POOLED 1,453,157) | **CONTAMINATED** | pass-2 summary over a `.bim` row list that carries duplicated rows |
| `n_distinct_pairs` | **CONTAMINATED** | derived from the same duplicated candidate rows |
| `n_undefined_rows` (POOLED 60) | **CONTAMINATED** | 15 true rows x 4 (see (c)/(d)) |
| `n_undefined_distinct_pairs` (13) | **CONTAMINATED** *as a count* | the pair-key SET is correct (see SURVIVING); it is the count's basis that is contaminated |
| `n_undefined_already_occluded` (10) | **CONTAMINATED** *as a count* | same basis |
| `n_undefined_not_already_occluded` (3) | **CONTAMINATED** *as a count* | same basis — **and see the pair-level UNDERCOUNT in (c)** |
| `n_deletions` (POOLED 355,777) | **CONTAMINATED** | counted over the duplicated in-bounds row list |
| `POOLED candidate rows` (2,865,513) | **CONTAMINATED** | *and on a DIFFERENT basis from the two lines above it* — see (b1) |
| POOLED offset histogram | **CONTAMINATED** | every bin is 4x its true value |
| POOLED `carriers_lost_frac` bins | **CONTAMINATED** | same |
| `wc -l` 2,865,514 | **CONTAMINATED** | 2,865,513 duplicated data rows + 1 header |
| `n_candidates_edge_clipped` = 0 | **ZERO ON A CONTAMINATED BASIS** | a multiplier cannot inflate a zero, but the basis is still the pass-2 summary. **NOT promoted to a clean zero.** |
| `n_globally_invariant_variants` = 0 | **ZERO ON A CONTAMINATED BASIS** | same |
| `n_undefined_rows_with_globally_invariant_member` = 0 | **ZERO ON A CONTAMINATED BASIS** | same |
| WHICH variant pairs are undefined (coordinates + IDs) | **SURVIVING** | identity, not a count |
| their signed `offset` | **SURVIVING** | identity |
| their `side` (`interior` / `upstream`) | **SURVIVING** | identity |
| their `already_occluded` flag | **SURVIVING** | identity |
| the SET of regions in which they occur | **SURVIVING** | identity |

**The contaminated counts are NOT recoverable by dividing by a constant.** The
duplication is NON-UNIFORM across regions. Of the 21 swept regions (ids pulled
from BLOCK 1's own table by script, not typed): **12 have IDENTICAL AFR/EUR
window bounds** — exact 2x — and **9 (`__subNN`) do not**:

```
region                   AFR window                 EUR window
m2_region_00040__sub10   (83811490, 94746265)       (81811490, 96746265)
m2_region_00060__sub12   (81228215, 91874650)       (79228215, 93521095)
m2_region_00060__sub13   (85874650, 93521095)       (83874650, 93521095)
m2_region_00088__sub01   (40208250, 50801281)       (38615219, 52801281)
m2_region_00111__sub07   (122952851, 133548100)     (120952851, 135548100)
m2_region_00120__sub03   (72941765, 83784838)       (70941765, 85784838)
m2_region_00120__sub17   (140744787, 151587860)     (138744787, 153587860)
m2_region_00145__sub14   (133564274, 144447288)     (131564274, 146447288)
m2_region_00161__sub13   (125516640, 136389650)     (123516640, 138262671)
```

⚠ **A PLANNING CLAIM CORRECTED BY MEASUREMENT.** The plan for this quick asserted
that for all 9 the AFR window is *strictly* inside the EUR window with a uniform
+/-2 Mb pad. Measured against `config/ld_regions.tsv`, that is **not exactly
right**, and the data wins:

- AFR is contained in EUR (inclusive) for **9 of 9** — the direction of the
  argument is unchanged;
- it is *strictly* inside for only **8 of 9**. `m2_region_00060__sub13` **shares
  its right edge** with EUR (right pad **0**);
- the pad is **not** uniformly 2 Mb: observed left pads `{1,593,031 · 2,000,000}`,
  right pads `{0 · 1,646,445 · 1,873,021 · 2,000,000}`.

The conclusion that matters is unaffected: **AFR ⊆ EUR everywhere**, so the AFR
pass can only ever emit FEWER-OR-EQUAL rows than the EUR pass — which is exactly
why the two passes are 1,412,356 and 1,453,157 and the ratio is 1.972, not 2.000.

File order in the manifest is **AFR-then-EUR** per region, so the driver's
last-wins `summaries` dict retained the **EUR** pass.

---

## (b1) THE TWO DENOMINATORS, RECONCILED

The receiving agent's flag #3 read: *"POOLED candidate rows 2865513 matches wc -l
exactly, but the per-region n_candidate_rows in the JSON sum to 1,453,157 — a
difference of 1,412,356 that is not a clean factor of two."* That is not a puzzle.
It is an exact, mechanism-derived identity, shown rather than asserted:

`all_results` **accumulates both driver passes**, while `summaries[region_id] = ...`
**last-wins and keeps only the second (EUR) pass**. Therefore:

```
POOLED candidate rows   2,865,513  =  AFR-pass 1,412,356  +  EUR-pass 1,453,157
                                      ^ verified: 1412356 + 1453157 == 2865513
wc -l                   2,865,514  =  2,865,513 data rows + 1 header
                                      ^ verified: 2865513 + 1 == 2865514
the agent's "difference"            =  2,865,513 - 1,453,157 = 1,412,356
                                      ^ i.e. the difference IS the AFR pass, exactly
ratio                   2,865,513 / 1,453,157 = 1.972, NOT 2.000
```

The ratio is 1.972 rather than 2.000 **because 1,412,356 < 1,453,157**: AFR ⊆ EUR
for the 9 `__subNN` regions (see (a)), so the AFR pass emits fewer rows there,
while the 12 identical-bounds regions contribute an exact 2x.

Component check — every one of BLOCK 1's own POOLED scalars was re-summed from
BLOCK 1's 21-row table by script rather than trusted
(`feedback_aggregate_agreement_hides_component_errors`). All six agree exactly:
`cand_rows` 1,453,157 · `n_deletions` 355,777 · `undef_rows` 60 ·
`undef_pairs` 13 · `already_occluded` 10 · `not_occluded` 3, and the summed
per-region offset histograms equal the printed POOLED histogram
`{-14: 4, -9: 4, -6: 4, -3: 4, -1: 4, 0: 40}`.

The same treatment for the undefined set:

```
15 distinct undefined rows x 8  = 120 rows physically in pcs_pairs.tsv
15 distinct undefined rows x 4  =  60 = POOLED n_undefined_rows (pass-2 basis)
```

⚠ **ONE AS-RECEIVED FIGURE THAT DOES NOT REDUCE TO A CLEAN MULTIPLE, REPORTED NOT
SMOOTHED.** BLOCK 2 opens with `distinct rows:    393887`. `393,887 x 8 =
3,151,096`, which is **not** 2,865,513; the implied average multiplicity is
**2,865,513 / 393,887 = 7.275**. That is *consistent* with — indeed further
evidence for — the non-uniform duplication: a row is 8x only when BOTH its
members lie in the AFR∩EUR intersection AND its deletion is in-bounds for both
passes; rows in EUR-only territory are emitted by fewer passes and at lower
multiplicity. It is **not** an exact identity, and the exact column projection
behind "distinct rows" is not recorded in the artifact, so **393,887 must not be
used as a divisor**. It is banked as received.

**This is precisely the defect T2 fixes.** `POOLED candidate rows` is now computed
as `sum(s["n_candidate_rows"] for s in summaries.values())` — the SAME basis as
the pooled histogram and bins — and that sum is checked against `len(all_results)`
by a must-be-identity comparison. All three POOLED lines now state their basis
in-line. The two bases can never silently diverge again.

⚠ **THE FAILURE HANDLING CHANGED AFTER THIS PARAGRAPH WAS FIRST WRITTEN
(`quick-260828-uej`).** It said `main()` *"RAISES (before any output file is
written)"*. That is no longer true and the sentence is corrected here rather than
left standing. `main()` now **writes the TSV (and the summary JSON) FIRST, then
reconciles**, and on disagreement **QUARANTINES the output to `<out>.SUSPECT`
(rotating any prior `.SUSPECT` to `.SUSPECT.<UTC>`) and returns 2** — like every
other failure path in `main()`. The ARITHMETIC is byte-unchanged; only position
and failure handling moved. Three properties follow: nothing survives at `--out`,
so an operator's `wc -l` there fails LOUDLY instead of returning the contaminated
2,865,514 from the previous run; the ~4h18m of compute is salvaged in the
`.SUSPECT` sibling instead of being discarded by a traceback; and writing first
TRUNCATES any stale artifact sitting at the read path. **RESIDUAL:** the EARLY
exits (missing bfile component, `no windows selected`, a duplicate `region_id`, an
empty `--region-ids`) still return 2 before any write, so a stale artifact
survives THOSE — closed by the runbook's STEP 2b ROTATE and STEP 3 pre-flight, not
by the code. See `### RESIDUAL — KNOWN, NOT FIXED, AND WHY` below.

---

## (b) ROOT CAUSE + THE LOCAL REPRODUCTION

Four links, each with its file and the line it occupied in the shipped
(pre-repair) `src/python/pairwise_completeness_scan.py` at `352ac9e`:

1. **`_read_regions_tsv` (:1168-1196) read columns 0/1/14/15 ONLY** — `region_id`,
   `chr`, `window_start_grch38`, `window_end_grch38`. It never looked at 1-based
   column 7, `ancestry`. MEASURED against the real file:
   `_read_regions_tsv('config/ld_regions.tsv', None)` returned **552 windows,
   276 distinct region_ids, multiplicity histogram `{2: 276}`** — every id twice,
   e.g. `('m2_region_00120__sub03','4',72941765,83784838)` AND
   `('m2_region_00120__sub03','4',70941765,85784838)`. → **windows 2x**
2. **`iter_bim_windows` (:699-727) builds `specs` as a LIST and `out` as a DICT**
   keyed on `region_id`, appending each matching `.bim` row **once per matching
   spec**. → **rows 2x**, hence **`deletion x partner` candidate pairs 4x**
3. **the driver (:1310-1345) writes `summaries[region_id] = ...` (LAST-WINS)
   while `all_results.extend(...)` ACCUMULATES**, so the region is evaluated in
   **two passes**. → **8x in the emitted TSV**, and two mutually inconsistent
   denominators printed under one POOLED heading
4. **the per-region stdout table (:1358-1360) iterates the LIST `windows` while
   looking up the DICT `summaries`** → **every region printed twice with
   identical values** — which is exactly what the agent's flag #3 reported

Empirical confirmation of the 8x, from the data itself: **15 true undefined rows
x 8 = 120** rows in `pcs_pairs.tsv`; **120 / 2 passes = 60 = the reported
`POOLED n_undefined_rows`**.

### The local reproduction — RE-RUN LIVE, not recalled

The original `scratchpad/repro_dup_region.py` lived in a scratch directory that
has since been deleted. Rather than reconstruct it from memory, the equivalent
was **re-run live on 2026-08-26** against a scratch copy of the repaired scanner
with the `iter_bim_windows` guard removed (negative control T2(b)). Source,
inlined so this record survives any scratchpad deletion:

```python
import sys, tempfile, pathlib
sys.path.insert(0, "src/python")
import pairwise_completeness_scan as pcs
bim = pathlib.Path(tempfile.mkdtemp()) / "t.bim"
bim.write_text("".join(f"15\tv{i}\t0\t{1000+i}\tA\tG\n" for i in range(6)))
for name, w in (("CONTROL", [("R","15",1000,1005)]),
                ("CASE A ", [("R","15",1000,1005), ("R","15",1000,1005)]),
                ("CASE B ", [("R","15",1000,1002), ("R","15",1001,1005)])):
    out = pcs.iter_bim_windows(bim, w)
    idx = [i for i, _ in out["R"]]
    print(f"{name} -> {len(idx):2d} rows  indices {idx}")
```

Measured output, verbatim:

```
CONTROL ->  6 rows  indices [0, 1, 2, 3, 4, 5]
CASE A  -> 12 rows  indices [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
CASE B  ->  8 rows  indices [0, 1, 1, 2, 2, 3, 4, 5]
```

**CASE A** (the same id twice with IDENTICAL bounds) is the shape the 12
identical-bounds regions produced — an exact 2x. **CASE B** (the same id twice
with DIFFERENT overlapping bounds) is the shape the 9 `__subNN` regions produced
— a NON-UNIFORM multiplication. **CONTROL** (the id appearing once) is the
negative control: a guard that raised on everything would be worthless.

### The second, separate REPORTING defect

Independently of the duplication: `POOLED candidate rows` printed
`len(all_results)` (the emitted-TSV basis) three lines below a histogram and bins
computed from `summaries` (the per-region basis). Two different denominators,
under one heading, with nothing to flag it. That is what let 2,865,513 and
1,453,157 coexist in the same stdout block for a whole sweep.

### What was FIXED, and the test that fails if it regresses

| Defect | Fix | Enforcer |
|---|---|---|
| ancestry-blind manifest read | `_REGIONS_TSV_ANCESTRY_COL = 6`, `_matches_ancestry`, `--ancestry` (default `AFR`) | `test_read_regions_tsv_reads_the_real_manifest_on_region_id_x_ancestry` (276, not 552) |
| the predicate could drift from production | mirrored from `run_native_ld_panel._filter_ancestry` | `test_ancestry_predicate_agrees_with_the_production_filter_contract` (ast + exec, symbol pin) |
| a region present only in the other ancestry vanishing silently | `seen` accumulates post-filter only | `test_region_only_in_the_unrequested_ancestry_raises_naming_the_id` |
| duplicated `region_id` multiplying rows | `_assert_unique_region_ids` in `iter_bim_windows` | `test_iter_bim_windows_duplicate_region_id_identical_bounds_raises` / `..._differing_bounds_raises`; CONTROL kept green by `test_iter_bim_windows_single_region_id_control_still_returns_six_rows` |
| duplicated `region_id` reaching the driver | `_assert_unique_region_ids` in `main()` (pre-loop) | `test_cli_duplicate_region_id_manifest_exits_2_and_writes_no_tsv` |
| `summaries` silently last-winning | `if region_id in summaries: raise` | `test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled` (monkeypatches the shared enforcer to neutralize layers 1+2; attributes by traceback final frame) |
| the two POOLED denominators diverging | must-be-identity check AFTER `write_tsv`; on disagreement the output is quarantined to `<out>.SUSPECT` and `main()` returns 2 (changed in `quick-260828-uej` T1 — it formerly raised BEFORE `write_tsv`, which left the previous run's file at the output path) | `test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2` + `..._is_the_summaries_basis_and_names_it` |
| a region printing twice in the table | unique `windows` by construction | `test_cli_stdout_table_prints_exactly_one_line_per_region_id` |
| the whole 8x, end to end | all of the above | `test_two_ancestry_manifest_emits_no_inflated_counts_end_to_end` |

**UNREACHABLE AS SHIPPED, BUT TESTED — corrected 2026-08-28 (T4).** The driver's
`if region_id in summaries: raise` line is unreachable in the shipped
configuration, because `_assert_unique_region_ids(windows)` runs in `main()`
before the loop AND inside `iter_bim_windows`.

⚠ **This record previously said "No committed test exercises it, and none
should."** That was right about the NAIVE test — feeding a duplicated manifest
through the front door passes via an earlier layer and is a false invariant — and
**wrong to generalise from it.** Testing the innermost layer of a defense-in-depth
stack *requires* disabling the outer ones, the same way a database unique
constraint is tested by bypassing application validation. Layers 1 and 2 both call
the **module-global** `_assert_unique_region_ids`, so a single `monkeypatch.setattr`
neutralises both and leaves exactly layer 3 active.

That test is now committed:
`test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled`.
It asserts the raise message, and **attributes it by the traceback's final frame**
— asserting the raising line sits inside the driver guard — so a green cannot mean
"some other layer stopped it."

**Negative control, observed:** deleting the branch makes that test go RED. What
caught the duplication instead is worth recording — the POOLED denominator
identity, reporting `sum of per-region n_candidate_rows = 4` against `8` emitted
rows. That is the **same 2× inflation that corrupted the 2026-08-26 sweep,
reproduced in miniature on a two-row fixture.** So layer 3 is not the last line of
defence; it is the **earliest**, and the only one that names the offending
`region_id`.

---

## (c) THE 15 TRUE UNDEFINED ROWS — IDENTITY LEVEL

Copied verbatim from **BLOCK 2** of the as-received artifact (the `uniq -c`
identity pull: `region_id, del_vid, partner_vid, offset, side, already_occluded,
pair_key`). Every aggregate below it was re-derived FROM THIS TEXT by script, not
transcribed.

```
jupyter@3bd063b5eb40:~$ cd /home/jupyter/occ_measure

distinct rows:    393887

      8 m2_region_00001 chr1:1980423:CCTCTTACCGTGTGGGGAGGACGGGTGAACGAGAGACTGTATCTAAGCCACCGGCACAGA:C chr1:1980475:G:A 0 interior True 10327|10328
      8 m2_region_00001 chr1:5733474:TCCCATCAGTCCACACACAGCTTCCGTCC:T chr1:5733487:C:T 0 interior True 44783|44784
      8 m2_region_00001 chr1:5922716:ACGGTGG:A chr1:5922718:G:A 0 interior True 46713|46714
      8 m2_region_00001 chr1:5922724:ACTGCCTGCAGTCCTGGCTTAGCCGGGCACG:A chr1:5922718:G:A -6 upstream False 46714|46715
      8 m2_region_00001 chr1:7492679:ACAAACACAAACCTACAAACACACACGCAGG:A chr1:7492693:ACAAACACACACGCAGG:A 0 interior True 59096|59097
      8 m2_region_00001 chr1:7492693:ACAAACACACACGCAGG:A chr1:7492679:ACAAACACAAACCTACAAACACACACGCAGG:A -14 upstream False 59096|59097
      8 m2_region_00001 chr1:8375794:TTCCTCACTCAGCAGCCACTGAAAATGCA:T chr1:8375822:A:T 0 interior True 66728|66730
      8 m2_region_00008 chr1:155856785:AAAG:A chr1:155856782:G:GAAATAGAATGGGAGTAGCCAGGGCAGCTCTTTTATTTCACAGATAATTACTGAGATCAA -3 upstream False 924401|924402
      8 m2_region_00008 chr1:155856785:AAAG:A chr1:155856788:G:GGGGAAAAAAAGAAAAAGAAAGAAAGAAA 0 interior True 924402|924403
      8 m2_region_00062 chr16:2345563:CATTAAAATCTCAGTTTACATATAGTAGAATTCACTCCTTCTCCTAATAATAATATAATTAATTATAATTATAAAAGTGCTTTTATAATGAAATTTTTTATGTTTAAACCTTTATCCATCTGGGGCTTATTTTGCTGGAGTGAGCTAGCCAATTTTCTCAACACTTAAAAACATTAATG:C chr16:2345727:T:G 0 interior True 17471658|17471659
      8 m2_region_00081 chr19:3191008:TGTGGCGGGCAGCAGGGAGATCGTCGTGGTGC:T chr19:3191030:G:A 0 interior True 19291406|19291408
      8 m2_region_00081 chr19:3590637:AC:A chr19:3590638:C:T 0 interior True 19294910|19294911
      8 m2_region_00120__sub03 chr4:80782556:GATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATTAATATATAATATATTC:G chr4:80782565:TATACATATATGAATATATAATATATTCATATATAATATACATATATTAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCACATATGGC:T 0 interior True 5512979|5512980
      8 m2_region_00120__sub03 chr4:80782565:TATACATATATGAATATATAATATATTCATATATAATATACATATATTAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATGAATATATAATATATTCACATATGGC:T chr4:80782556:GATATATAATATACATATATGAATATATAATATATTCATATATAATATACATATATTAATATATAATATATTC:G -9 upstream False 5512979|5512980
      8 m2_region_00149 chr7:89454077:GCGTA:G chr7:89454076:C:T -1 upstream False 9776035|9776036

Columns printed: region_id, del_vid, partner_vid, offset, side, already_occluded, pair_key.
Leading integer is `uniq -c` — the multiplicity of each distinct row in pcs_pairs.tsv.

pcs_pairs.tsv was never read out of the perimeter; only these aggregate and
variant-ID-level lines crossed.
```

### Re-derived by script from the block above

```
identity rows parsed from BLOCK 2 : 15
multiplicity (uniq -c) histogram  : {8: 15}
offset histogram                  : {-14: 1, -9: 1, -6: 1, -3: 1, -1: 1, 0: 10}
  sums to                         : 15
side histogram                    : {'interior': 10, 'upstream': 5}
distinct pair_keys                : 13
pairs already_occluded            : 10
pairs NOT already_occluded        : 3
```

Every re-derived figure agrees with the planning anchors. The regions carrying
undefined rows are `m2_region_00001`, `m2_region_00008`, `m2_region_00062`,
`m2_region_00081`, `m2_region_00120__sub03`, `m2_region_00149` — and BLOCK 2's
per-region row counts x 4 reproduce BLOCK 1's per-region `undef_rows` column
exactly: `{00001: 28, 00008: 8, 00062: 4, 00081: 8, 00120__sub03: 8, 00149: 4}`.

### 15 rows vs 13 pairs — RECONCILED, not left implicit

Two `pair_key`s carry TWO rows each. Both are **deletion x deletion neighbours**,
which emit two ordered rows under one `pair_key` (see
`test_deletion_deletion_neighbour_emits_two_rows_one_pair_key`):

| pair_key | region | offsets | sides | already_occluded |
|---|---|---|---|---|
| `59096\|59097` | `m2_region_00001` | `[0, -14]` | `[interior, upstream]` | `[True, False]` |
| `5512979\|5512980` | `m2_region_00120__sub03` | `[0, -9]` | `[interior, upstream]` | `[True, False]` |

**`13 distinct pairs + 2 extra rows = 15 rows`.**

### The three NOT-already-occluded pairs, named in full

| pair_key | region | offset | deletion | partner |
|---|---|---|---|---|
| `46714\|46715` | `m2_region_00001` | **-6** | `chr1:5922724:ACTGCCTGCAGTCCTGGCTTAGCCGGGCACG:A` | `chr1:5922718:G:A` |
| `924401\|924402` | `m2_region_00008` | **-3** | `chr1:155856785:AAAG:A` | `chr1:155856782:G:GAAATAGAATGGGAGTAGCCAGGGCAGCTCTTTTATTTCACAGATAATTACTGAGATCAA` |
| `9776035\|9776036` | `m2_region_00149` | **-1** | `chr7:89454077:GCGTA:G` | `chr7:89454076:C:T` |

**ALL THREE ARE UPSTREAM / NEGATIVE-OFFSET.** The posted downstream-only
criterion `d.pos < v.pos <= d.span_end` **cannot see them BY CONSTRUCTION** — not
because it mis-measures them, but because they lie on the side of the deletion it
does not look at. Note also that no positive offset appears anywhere in this
sweep, and `m2_region_00057` (the +1 case that motivated the instrument) is not a
member of the pre-committed 21-region sample, so the +1 direction is
**unrepresented here**.

### ⚠ THE PAIR-LEVEL UNDERCOUNT — the dangerous direction, stated explicitly

There are **FIVE undefined UPSTREAM ROWS** — offsets **-14, -9, -6, -3, -1** —
and **all five carry `already_occluded = False`** (re-derived: upstream rows 5,
of which already-occluded **0**, not-occluded **5**; every one carries
`side == upstream`).

The **pair-level rollup surfaces only THREE**, because the -14 row
(`59096|59097`, `m2_region_00001`) and the -9 row (`5512979|5512980`,
`m2_region_00120__sub03`) each share a `pair_key` with an **interior offset-0
sibling row that IS occluded**. Those two pairs are therefore classed
already-occluded **while still carrying an un-occluded upstream row**.

```
n_undefined_not_already_occluded = 3   <- answers: how many PAIRS are wholly unseen?
row-level upstream blindness     = 5   <- answers: how many ROWS are upstream and un-occluded?
```

**`n_undefined_not_already_occluded = 3` UNDER-states row-level upstream
blindness, which is 5.** An undercount is the dangerous direction for any
denominator headed for a public pre-registration. Both numbers are recorded here,
and the smaller one must never stand alone.

**FINDING FOR ADJUDICATION — NOT A CHANGE.** No criterion, threshold or policy
moves in this record. The posted criterion is what `osf.io/trsx5` carries, so any
change is a **pre-registration** question for Seth, **brief-blind** — and a number
must not become a rule in the same conversation that produced it, which is how
the withdrawn `0.0005` was born.

---

## (d) SCOPE: THE DUPLICATION DID NOT MANUFACTURE THE FINDINGS

**All 15 undefined rows lie INSIDE the AFR windows.** None is an artifact of the
EUR window's wider bounds.

**The verification is BLOCK 2's multiplicity column itself.** Every one of the 15
distinct rows carries `uniq -c` **== 8, uniformly**:

```
multiplicity (uniq -c) histogram : {8: 15}
distinct multiplicities among the 15 rows : {8}
```

**The falsifier, stated explicitly:** a row lying OUTSIDE the narrower AFR window
could only have been emitted by the EUR pass, and would therefore read **4**, not
8. **ANY multiplicity of 4 among the 15 would have refuted this claim.** Observed
count of `uniq -c == 4` rows: **0**.

**Conclusion: the duplication MULTIPLIED the findings by exactly 8. It did not
manufacture them.** That is why the identity-level truth in (c) survives intact
while every count in (a) does not.

---

## (e) PRE-REGISTERED PREDICTION — RECORDED BEFORE THE RE-RUN

**THE RE-RUN HAS NOT HAPPENED.** Nothing has been fired since the contaminated
sweep. This section is written and committed **before** the repaired instrument
is run, deliberately.

When STEP 3 is re-run with the repaired scanner, the prediction is:

| Quantity | Predicted |
|---|---|
| `n_undefined_rows` (POOLED) | **15** |
| `n_undefined_distinct_pairs` (POOLED) | **13** |
| `n_undefined_already_occluded` | **10** |
| `n_undefined_not_already_occluded` | **3** |
| POOLED offset histogram | **`{-14: 1, -9: 1, -6: 1, -3: 1, -1: 1, 0: 10}`** |
| `POOLED candidate rows` | **353089** |
| `wc -l pcs_pairs.tsv` | **353090** |

The histogram **sums to 15**, matching the predicted row count — stated here so
the two predictions cannot silently disagree.

**THE TWO DENOMINATOR ROWS ARE DERIVED, NOT GUESSED — added `quick-260828-uej`,
still BEFORE the re-run.** The derivation is shown rather than asserted:

```
every AFR-pass row had BOTH members inside the AFR window, so each was
emitted exactly 4x (rows 2x -> deletion x partner pairs 4x):

  AFR pass 1,412,356 / 4 = 353,089        EXACT  (1412356 % 4 == 0)
  353,089 + 1 header     = 353,090        -> wc -l

the EUR pass does NOT divide:

  EUR pass 1,453,157 / 4 = 363,289.25     NON-INTEGRAL
```

That non-integrality is not an inconvenience — it is **independent corroboration
of the non-uniform-multiplicity account already recorded at (b1)**. AFR ⊆ EUR for
the 9 `__subNN` regions, so EUR-only territory contributes rows at lower
multiplicity and the EUR pass cannot be a clean 4x of anything. The AFR pass,
which is what the repaired AFR-only run reproduces, does divide exactly.

Both rows carry the SAME STATUS as every other line in this table: **DERIVED
BEFORE THE RUN**, and **a mismatch is a finding to report, never a number to
adjust.** Enforcer: `tests/m3/test_pairwise_completeness_scan.py::
test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` parses both
numbers out of this section and asserts `wc == rows + 1` and `rows * 4 ==
1412356`, and that `1412356` still appears in (b1) — so the two sections cannot
drift apart.

Also predicted, as structural consequences of the repair rather than as data:
`POOLED candidate rows` will equal the sum of the per-region `n_candidate_rows`
(otherwise the run QUARANTINES the output to `<out>.SUSPECT` and returns 2), the
per-region table will print **21** lines and not 42, and `wc -l` on
`pcs_pairs.tsv` will be that pooled count + 1.

**The command does not change — the scanner argv is unchanged IN MEANING.** The
repaired scanner's `--ancestry` default of `AFR` makes the already-written,
UNMODIFIED STEP 3 invocation correct. The RUNBOOK AROUND it did change
(`quick-260828-uej`): STEP 0 now gates on the scanner's content hash, byte size,
last-touching commit and a positive behavioural capability check instead of on a
commit subject line; a new STEP 2b ROTATEs the contaminated artifacts off the read
path; STEP 3 refuses to start if either output path is occupied and NAMES all 21
region ids; and the `.bim` the banked `pair_key`s are relative to is recorded.
**No predicted number above changes as a result** — those edits change what the
operator can PROVE, not what the instrument computes.

**A MISMATCH IS A FINDING TO REPORT, NEVER A NUMBER TO ADJUST.** If the re-run
disagrees with any line above, the disagreement is the result — it is reported,
investigated and banked. The prediction is not revised to fit, and neither is the
code, the window, nor the sample.

**Why this is recorded first.** `feedback_internal_validation_cannot_catch_misspecified_premise`:
a harness, a checker and a verifier all enforced a wrong mechanism sentence that
this project's own brief supplied, and only a brief-blind adversarial review
caught it — one step before public posting. And the withdrawn `0.0005` came from
a number becoming a rule in the conversation that produced it. Both failures share
one shape: the expectation was formed *after* seeing the output. This record
breaks that shape by writing the expectation down, in a commit, first.

---

### RESIDUAL — KNOWN, NOT FIXED, AND WHY

Four things are wrong-or-limited and are **deliberately not being fixed** before
the re-run. They are written down so that no one has to rediscover them, and so
that nothing here is quietly load-bearing. Added `quick-260828-uej`.

**1. The `__subNN` window overlap double-counts the POOLED candidate DENOMINATOR.**
MEASURED against the real `config/ld_regions.tsv` (AFR windows):

```
m2_region_00040__sub12  93,681,040 - 104,615,815
m2_region_00040__sub13  98,615,815 - 109,550,590   -> 6,000,000 bp of overlap
m2_region_00060__sub12  81,228,215 -  91,874,650
m2_region_00060__sub13  85,874,650 -  93,521,095   -> 6,000,000 bp of overlap
```

The same `.bim` rows therefore enter **two** regions' candidate sets, and the
POOLED candidate denominator counts them **twice**. This is a pre-existing
region-**DEFINITION** property, not a scanner defect: the scanner is faithfully
reporting the regions it was given. It affects the **denominator only** and **not
the 15 findings** — both of those regions carry **0** undefined rows. And it is
present on the **same basis** in the `1,412,356` from which `353,089` is derived,
so the new prediction is *consistent with* this residual rather than contradicted
by it. Any statement of the form "X of N candidate rows" must therefore say that N
is a **sum over regions**, not a count of distinct `.bim` rows.

**2. The scanner's denominator is pre-`--mac 1` / pre-`--exclude`; the panel's LD
matrix is post-.** The scanner counts candidate rows over the raw `.bim` window;
the production LD matrix is built after MAC filtering and after the occlusion
exclusion list. The two populations are NOT the same. **Any fraction computed from
these counts MUST name its denominator, and none of them is a panel prevalence.**

**3. This plan's OWN code fix has a residual, and it is stated plainly.** The
write-then-reconcile-then-quarantine change (`quick-260828-uej` T1) protects the
output path only on the paths that reach the write. The **early exits** — a
missing bfile component, `ERROR: no windows selected`, a duplicate `region_id`,
and the new empty-`--region-ids` error — all return 2 **before anything is
written**, so a stale artifact sitting at the output path **survives them
untouched**. That hole is closed by the RUNBOOK — STEP 2b's ROTATE plus STEP 3's
pre-flight existence guard in
`.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` — and **NOT
by the code**. Do not read the write-first ordering as covering the early exits.

**4. DECLINED from the as-received external review**, each with its reason. Full
text: `.planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-CODEX-REVIEW-as-received.md`.

| Finding | Severity | Disposition | Reason |
|---|---|---|---|
| Scanner parses the manifest POSITIONALLY while production is header-keyed, so a reordered manifest diverges silently | MEDIUM | DECLINED for now | The checked-in `config/ld_regions.tsv` has the expected column order (MEASURED: ancestry at 1-based column 7 for all 552 data rows, 276 AFR / 276 EUR). The failing input is a manifest that does not exist; fixing it would change the parse on the fire path for a hypothetical file. |
| The duplicate guard only catches exact `str(region_id)` equality, not whitespace/case aliases passed **directly to the iterator** | LOW | DECLINED | An API-only path. The TSV parser strips ids at read time, so the runbook's route cannot reach it; every id the sweep uses comes from `_read_regions_tsv`. |
| The scanner's composite ancestry parse strips where production does not | MEDIUM | **ADDRESSED as a monitored divergence, not closed** | Pinned at the SELECTION layer with the production behaviour measured by `ast` extraction, plus a monitor asserting the real manifest carries **0** padded-or-quoted ancestry cells (`quick-260828-uej` T2). Closing it would break the byte-faithful production mirror; the monitor goes RED the day it becomes live. |

The pair-level **`n_undefined_not_already_occluded = 3` vs row-level upstream
blindness = 5** undercount is **already recorded above** at
`### ⚠ THE PAIR-LEVEL UNDERCOUNT — the dangerous direction, stated explicitly`
and is cited here rather than duplicated.

---

## WHAT THIS RECORD DOES **NOT** ESTABLISH

No prevalence. No boundary width. No partial-confounding tail size. Those remain
OPEN and are settled only by re-running the repaired instrument in-perimeter over
the pre-committed sample — and then adjudicating with Seth, brief-blind.
