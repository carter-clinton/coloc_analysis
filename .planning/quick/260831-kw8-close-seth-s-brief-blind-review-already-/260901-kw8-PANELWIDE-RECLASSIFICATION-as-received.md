# AS-RECEIVED — panel-wide reclassification of the repaired sweep (2026-09-01)

Run in-perimeter on the AoU VM, `pcs_panelwide_reclassify.py` at `a4b1704`+.
Post-hoc: reads `pcs_pairs.tsv` + `config/ld_regions.tsv` + the cohort `.bim` only.
No genotypes decoded, no LD computed, the sweep NOT re-run. Verbatim, unedited.

## ANCHORS

```
ba577b5739cd99e70bd6c14d342bd72f  pcs_panelwide_summary.json   14313 B
44cf49b67ce348f1d7c04cbe679fc821  pcs_panelwide_verdicts.tsv    5203 B
```
Both written Sep 1 04:22Z. Runtime 02:29:11Z -> 04:22:50Z = 1h53m, exit 0, ~99% CPU throughout.

## THE ANSWER

**12 of 13 undefined distinct pairs have a member on the production excludelist. ONE does not.**
**14 of 15 undefined ROWS never reach the LD matrix. ONE does.**

The banked sweep reported `n_undefined_not_already_occluded = 3`. That was
ANCHOR-RELATIVE — it asked only whether the partner sits inside *that* deletion's
own REF span. Built over EVERY deletion in the window, as production does, two of
those three are occluded after all.

## THE SURVIVOR (conditional — see SCOPE)

```
row 14: m2_region_00149
  del_vid     chr7:89454077:GCGTA:G  (pos 89454077)
  partner_vid chr7:89454076:C:T      (pos 89454076)
  offset -1  side upstream  pair_key 9776035|9776036
  pair_reaches_matrix True  del_globally_invariant False  partner_globally_invariant False
```
The ONLY row of 15 with both `del_occluded_panelwide` and `partner_occluded_panelwide`
False, and the ONLY row with `pair_reaches_matrix True`. Not disposed of by the
invariance route either (`n_pairs_neither_occluded_and_no_globally_invariant_member = 1`).

**It is the -1 mirror of `m2_region_00057`'s +1** — the case that opened this whole
investigation, and which the pre-committed 21-region sample does not contain. So the
residual class is *immediately adjacent to the REF span, EITHER side*, and this sweep
could only ever observe one of the two sides.

## THE 15 ROWS

```
#   region_id              offset    alr_oc del_occ_pw ptr_occ_pw reaches   del_ginv
0   m2_region_00001        0         True   False     True      False     False
1   m2_region_00001        0         True   False     True      False     False
2   m2_region_00001        0         True   False     True      False     False
3   m2_region_00001        -6        False  False     True      False     False
4   m2_region_00001        0         True   False     True      False     False
5   m2_region_00001        -14       False  True      False     False     False
6   m2_region_00001        0         True   False     True      False     False
7   m2_region_00008        -3        False  False     True      False     False
8   m2_region_00008        0         True   False     True      False     False
9   m2_region_00062        0         True   False     True      False     False
10  m2_region_00081        0         True   False     True      False     False
11  m2_region_00081        0         True   False     True      False     False
12  m2_region_00120__sub03 0         True   False     True      False     False
13  m2_region_00120__sub03 -9        False  True      False     False     False
14  m2_region_00149        -1        False  False     False     True      False
```

The five `already_occluded=False` rows are 3, 5, 7, 13, 14. Four die panel-wide:

| row | region | offset | dies because |
|---|---|---|---|
| 3 | 00001 | -6 | the PARTNER is occluded |
| 5 | 00001 | -14 | **the DELETION is itself occluded** |
| 7 | 00008 | -3 | the PARTNER is occluded |
| 13 | 00120__sub03 | -9 | **the DELETION is itself occluded** |
| 14 | 00149 | -1 | **SURVIVES** |

⚠ Rows 5 and 13 die by a route NEITHER Seth NOR we enumerated: the anchor deletion is
ITSELF inside another deletion's span. Seth predicted the collapse via the partner
("the rule excludes w and thereby deletes the pair"); two of four die deletion-side.
Same outcome, different mechanism, unforeseen by both parties.

## POOLED BLOCK, VERBATIM

```
ambiguous_member_ids                           []
n_defined_rows_in                              353074
n_pairs_member_occluded_panelwide              12
n_pairs_neither_member_occluded_panelwide      1
n_pairs_neither_occluded_and_no_globally_invariant_member 1
n_pairs_with_ambiguous_member_id               0
n_rows_in_tsv                                  353089
n_rows_member_occluded_panelwide               14
n_rows_neither_member_occluded_panelwide       1
n_undefined_distinct_pairs_in                  13
n_undefined_rows_in                            15
n_undefined_rows_out_of_scope                  0
occluded_member_vids                           list[11]
```

## SCOPE — the condition travels WITH the claim, not beside it

The tool's own caveat: occlusion is MONOTONE in the row set. `R ⊆ R'` implies
`occluded(v,R)` implies `occluded(v,R')`. So an OCCLUDED verdict on a subset is
SOUND; a NOT-OCCLUDED verdict on a subset is NOT — it can flip when rows are added.

```
ancestry                   'AFR'
bim_path                   '/home/jupyter/afr_cohort.bim'
bim_n_lines                20767864
bim_sha256                 9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99
pairs_tsv_path             '/home/jupyter/occ_measure/pcs_pairs.tsv'
pairs_tsv_n_lines          353090
pairs_tsv_sha256           eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583
regions_tsv_path           'config/ld_regions.tsv'
regions_tsv_sha256         e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a
region_ids_selected        276     <- the ancestry key worked: 276, not 552
region_ids                 6       <- of 21 scanned, 6 carried undefined rows
region_ids_out_of_scope    0
n_rows_in_window_per_region {'m2_region_00001': 102421, 'm2_region_00008': 207147,
                             'm2_region_00062': 86719, 'm2_region_00081': 196219,
                             'm2_region_00120__sub03': 81033, 'm2_region_00149': 338354}
```

**The conditional claim, stated once:** `m2_region_00149`,
`chr7:89454077:GCGTA:G` x `chr7:89454076:C:T` at offset -1 is NOT occluded
panel-wide **relative to** `bim_sha256 9cc378b7…feeeb99` at `bim_n_lines 20767864`,
region 00149 contributing `n_rows_in_window 338354`. Supply rows beyond that set and
the verdict can flip to occluded; it cannot flip the other way. **The twelve occluded
verdicts carry no such condition.**

## A TRANSCRIPTION SLIP, SETTLED

The agent's earlier stdout paste rendered the chr4 occluded member ending
`…TTCACATATGCC:T` with `AATATAACATATATG` inside. The machine-written JSON (len=197)
gives `…TTCACATATGGC:T` with `AATATACATATATT` — matching the banked sweep record.
**The JSON is authoritative; the paste was the slip**, read off a screenshot of a
wrapped 197-character poly-AT repeat. Noted by the agent itself as the same failure
mode it had just refused to risk on sixteen-digit floats.

## WHAT THIS DOES NOT ESTABLISH

No prevalence. The +1 side is unobserved by construction (00057 is not in the sample).
Nothing here revises a pre-registered number: the sweep's 15 / 13 / 10-3 stand as
measured; this is a SEPARATE, post-hoc quantity answering a different question.
