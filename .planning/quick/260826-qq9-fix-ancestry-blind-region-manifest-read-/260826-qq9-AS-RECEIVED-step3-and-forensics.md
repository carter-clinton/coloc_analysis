# AS-RECEIVED — STEP 3 sweep + the §3/§4 forensic pull (2026-08-26)

Pasted by Carter from the AoU agent / VM terminal. **Verbatim, unedited.**
Numbers here are the CONTAMINATED sweep. See the task's debug record for what
survives and what does not. Nothing in this file may be reconstructed or
"corrected" in place — it is the received artifact.

---

## BLOCK 1 — STEP 3 completion report (agent, 2026-08-26 ~13:37Z)

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

---

## BLOCK 2 — §3 (partial) + §4, run by Carter in the VM terminal

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
