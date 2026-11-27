---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8f
subsystem: ta-r4 W3f (Carter Q-158AEIM "Measure it first": asthma EUR flipped-row reference check with an unflipped control)
tags: [orientation, eaf-diagnostic, reference-genome, grch38, grch37, disclosure]
requires: [ta-r4-W3f-multikey-fatal-and-chronology]
provides: [src/python/ta_r4/orientation_eaf.py, per-row flipped manifest, unflipped control manifest, GRCh38/GRCh37 reference pins, filled DRAFT (c) sentence (not inserted)]
affects: [15.8g]
tech-stack:
  added: []
  patterns: ["a by-construction hypothesis needs a control group carrying the same columns", "tri-state (Kleene) measurement columns, undetermined never counted as true or false"]
key-files:
  created:
    - src/python/ta_r4/orientation_eaf.py
    - tests/ta_r4/test_asthma_eur_eaf_disclosure.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch37_reference_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/grch38_reference_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv
  modified:
    - .planning/DECISIONS.md
    - config/ta_r4/data_sources.yaml
decisions:
  - "Q-158AEI (Disclose, no filter) + Q-158AEIM (Measure it first) recorded in DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter; the Q-158AEI lift explanation was a planner's guess (harmonize PLAN:154-155)"
  - "GRCh38_mapDamage registered as grch38_fasta_mapdamage (24/24 primary contig lengths); 1000G Phase 3 VCFs used for the GRCh37 half (no GRCh37 FASTA on disk)"
metrics:
  completed: 2026-11-27
  duration: "2026-11-27 00:30 - 05:00 EST (FULL 2h26m)"
---

# Phase ta-r4 Plan 15.8f: asthma EUR flipped-row reference measurement Summary

asthma EUR's 225 flipped rows, plus a seeded 4,525-row unflipped control from the same join, now have measured
tri-state columns against a pinned GRCh38 FASTA and the pinned 1000 Genomes Phase 3 GRCh37 records. The DRAFT (c)
sentence is filled from those counts and is NOT inserted. The plan ends at the blocking Q-158AEIW STOP, and the executor
wrote no reply.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 (0b) | 773f64cb | DECISIONS.md: AEI + AEIM DEC (DECISIONS.md only; see deviation 1) |
| 1 | 4fa9b6a7 | data_sources.yaml grch38_fasta_mapdamage; grch37 / grch38 reference manifests |
| 2 | 1a2cc6c6 | orientation_eaf.py; tests A and B; flipped and control manifests |
| 3 | (records) | HANDOFF, STATE, LOG, PLAN-INDEX, this SUMMARY |

## Gates

- Start 456ae994. gate_157j.sh; gate_158.sh with 10 QIDs (DFX, AEI, AEIM added); gate_158r2.sh; gate_158a2.sh with OR/PAL/EL: all rc 0.
  The AEIM tail line was asserted. Tracked checks on R6G ×2, KW, DFX, AEI and AEIM are OK (gate_15_8f.txt). No other STOP replies exist.
- Gate NCs (gate_nc_15_8f.txt): 9 of 9 return rc 2. The tracked-check NC and the tail NC both FAIL. The real gates return rc 0 afterwards.

## References

- GRCh38: GRCh38_mapDamage.fa.fai has 455 contigs; its 24 primary lengths equal the published GRCh38 values (Slurm 2119477; NC fails).
  There is no `.dict`, so no per-contig md5 exists. As the base-level check, control grch38_ref_match is 4,525 / 4,525 true.
  Symlink: data/r4/inputs/grch38_fasta → /rs1/researchers/c/ckclinto/GRCh38_genome/GRCh38_mapDamage.
- GRCh37: no FASTA was found (the search has a positive control). The 1000G VCF REF bases are used instead, at data/r4/inputs/1kg_vcf (hs37d5, b37).
- Pins (Slurm 2119488): 48 VCF/.tbi files, plus the FASTA, .fai and lifted.bed (FASTA sha256 344399202c86…4f98, lifted.bed b46c21fbc8b9…0f9b).

## Measurement (Task 2)

- Identity (Slurm 2119559): render_eaf_manifest(eaf_diffs()) is byte-equal to sumstats_r4_orientation_eaf.tsv (sha256 7ad5ce50…80c0).
- Per-row (Slurm 2119572): 225 rows, median 0.0270, 19 above 0.2, 204 SNV / 21 indel, 14 indels above 0.2. All match the aggregate.
- Control populations: SNV>0.2 474, SNV<=0.2 198,095, indel>0.2 51, indel<=0.2 17,485 (sum 216,105; > 0.2 sum 525). The sample is 4,525.
- Cross-tab: data/r4/tmp/w3f/q158/aeiw_crosstab_15_8f.tsv (sha256 ce4a15cf6cadf7976c47a142f0c3573cff7e7d06b8b4a51be9875f7d0bb2b844).
  Rows table: aeiw_rows_15_8f.tsv (sha256 b21e4235dd6695baa9f07297e3a35172b9c0f229c02440cbc6efb8dee5aacc54).
- Sentence: aeiw_sentence_15_8f.txt (sha256 238768d4a3b2c5157ed128d4f4041b797ee893eefe0b8253f50546b7b736e776).
- RED (2119534) shows ImportError for both tests. Green (2119604): A 311 s, B 0.8 s.
  The 12 NCs (2119624, nc_15_8f.txt) all fail, and every file is restored to its sha256.

## FULL (Task 3)

- Slurm 2119705 (c020n01 Cascade Lake, HEAD 1a2cc6c6, 2h26m, --mem=96G; MaxRSS 66.9 GiB).
  QUICK 911 P / 2 S, HEAVY 356 P / 5 S, PINS 39 P.
  FULL 2,768 = 2,715 P / 53 S / 0 F (full_15_8f.xml, sha256 48315f252c4b98c1e87a3cf621a81c08ddedd25865022a7b0541c149f82cf16b).
- check_15_8f.py (Slurm 2119989, reconcile_15_8f.txt) gives PASS on both comparisons:
  - (a) vs full_15_7j: 2,694 + 72 (parsed from the 9 SUMMARYs) + 2 = 2,768.
  - (b) vs full_15_8e: +2 ids, everything else identical.
- Checker NC (2119706): full_15_8e.xml given as NEW fails.

## Deviations from Plan

1. **[Orchestrator-directed] The AEIM reply was already committed.** It was committed in 456ae994, so it is gated as
   tracked and unchanged vs HEAD: added-in 456ae994, sha256 b2a13e9c…90e8, `tail -n 1` asserted. Commit 0b (773f64cb) holds DECISIONS.md only.
2. **[Rule 2] FULL memory raised to 96G.** The last two FULLs filled 64G. This one peaked at 66.9 GiB, so 64G would not have been enough headroom.
3. **[Rule 1] The declared check needed a carve-out in check_15_8f (a).**
   `test_e7_qtl_tier_has_the_matched_rounding_columns` is declared in 15.8d but was new in 15.8c2, so it is absent from full_15_7j.
   It is checked as an added id instead of passed -> passed, and the script prints this.
4. **The control manifest's line 1** appends each stratum's population (`SNV>0.2 stratum_n 474; …`) after the plan's rule text, per must_have "states the rule and each stratum's population size".
5. **The first literal-scan NC was mis-built.** It used `/rs1/x`, but the banned literal is `/rs1/researchers`. Redone; it fires (literal_nc_15_8f.txt).

## Observations (not in scope; for Carter / 15.8g)

- catalog_ref_grch37_match compares REF_oriented at its own length. For an indel whose alleles share the anchor base, the
  lifted REF and REF_oriented can both "match" GRCh37 (e.g. 19:45062119 T/TA: grch37 T true, catalog TA true). The
  column is a measurement, not a test of which orientation is the reference.
- Many of the 19 rows have an empty SNP_ID. The lifted.bed join matched exactly one input line for every row anyway.
- grch37 undetermined: 6 of 225 flipped rows and 617 of 4,525 control rows. HANDOFF W3f158_asthma_eur_grch37_fasta is OPEN (a GRCh37 FASTA download is Carter's call).

## New test ids

tests.ta_r4.test_asthma_eur_eaf_disclosure::test_asthma_eur_flipped_eaf_manifests_rederive
tests.ta_r4.test_asthma_eur_eaf_disclosure::test_orientation_eaf_rules_and_import_hygiene

## Declared spec updates

none

## Known Stubs

None. (Test C belongs to 15.8g; the sentence is deliberately not inserted.)

## Self-Check

PASSED: the 6 created files exist; commits 773f64cb, 4fa9b6a7 and 1a2cc6c6 exist; the src diff vs 456ae994 is only the
module; the DRAFT is unchanged; no Q-158AEIW reply file exists.
