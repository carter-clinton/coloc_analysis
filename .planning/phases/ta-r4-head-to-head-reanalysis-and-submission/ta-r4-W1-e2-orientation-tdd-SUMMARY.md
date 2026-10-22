---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W1-e2-orientation-tdd
subsystem: E-2 allele orientation (BMI sumstats alleles, EUR panel REF/ALT, QTL-beta orientation)
tags: [ta-r4, d-06, d-18, d-15, e-2, tdd, default-off]
requires: [ta-r4-W0d-pair-coloc-r4-script]
provides:
  - src/python/ta_r4/restore_bmi_alleles.py (restore | pin)
  - data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz (+ .tbi), sha256-pinned
  - plink_ld_to_rds.R --emit-ref-alt (default false)
  - run_qtl_coloc.R --qtl-orient (default false) + src/snakemake/scripts/qtl_orient.R
affects: [W2a (R4 EUR panel rule: plink --keep-allele-order + --emit-ref-alt true), W3e (QTL_A3/QTL_A2 argv: --ld-allele-join true --qtl-orient true), W4a/W8a (D-18 disclosure numbers below)]
tech-stack:
  added: []
  patterns: [value-identity classification at the frozen string precision, flag-off identity vs the pre-change git blob, sourced helper only under its flag]
key-files:
  created:
    - src/python/ta_r4/restore_bmi_alleles.py
    - src/snakemake/scripts/qtl_orient.R
    - tests/ta_r4/test_bmi_allele_restoration.py
    - tests/ta_r4/test_plink_ld_to_rds_ref_alt.py
    - tests/ta_r4/test_qtl_orient.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/bmi_allele_restoration_report.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv
  modified:
    - src/snakemake/scripts/plink_ld_to_rds.R
    - src/snakemake/scripts/run_qtl_coloc.R
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "--qtl-orient true requires --ld-allele-join true: orientation is applied to rows bound by the existing panel bridge (W3e already pairs the two flags)."
  - "BETA equal to 0 at the frozen precision (sign uninformative, z = 0) is kept as exact and counted (n_sign_uninformative 23,896)."
  - "Flag-off identity is proven against the pre-W1 git blobs (plink_ld_to_rds.R 6f9986d7, run_qtl_coloc.R 3ec59663), not `git show HEAD:`, which becomes self-comparison once the change is committed."
metrics:
  duration: "~2h45m (2026-10-22), incl. FULL 24m01s and HEAVY 6m59s"
  completed: 2026-10-22
  tasks: 4
  files: 7 created + 2 code modified + LOG/STATE/ROADMAP/SUMMARY
---

# Phase ta-r4 Plan W1: E-2 orientation TDD Summary

W1 fixes E-2 allele orientation for the R4 pipeline in three default-off units. The frozen BMI file gets its REF/ALT
alleles back from the same Yengo 2018 release, and its BETA/SE/P/N strings are kept unchanged. The EUR panel can now
carry REF := A2 and ALT := A1, which a plink `--keep-allele-order` known-answer test confirms. QTL betas can be
re-signed to the panel ALT using the QTL's own alleles. Track B outputs did not move: with the new flags off, both
shared scripts give output identical to the pre-change scripts, and m3, phase1 and phase2 outcomes are unchanged.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `fb0a5b5c` | restore_bmi_alleles.py, its tests, match-rate report, sumstats_r4_sha256.tsv |
| 2 | `4896e011` | plink_ld_to_rds.R --emit-ref-alt, test_plink_ld_to_rds_ref_alt.py |
| 3 | `e7224a91` | run_qtl_coloc.R --qtl-orient, qtl_orient.R, test_qtl_orient.py |
| 4 | wave-close commit | LOG, STATE, ROADMAP, this SUMMARY |

## Unit 1: BMI allele restoration (D-18)

**Headers (measured):**
- Frozen `bmi.EUR.tsv.bgz`: `CHR POS BETA SE P N SNP_ID TRAIT ANCESTRY BUILD`
- Source `bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz`: `CHR BP SNP EA OA BETA SE P EAF N`
- Raw `bmi.EUR.raw.gz`: `CHR POS SNP Tested_Allele Other_Allele Freq_Tested_Allele_in_HRS BETA SE P N`
- Output: `CHR	POS	REF	ALT	BETA	SE	P	EAF	N	SNP_ID	TRAIT	ANCESTRY	BUILD`. `cat -A` shows tabs, and the header is identical to the required one.
- The frozen .tbi parameters are generic format, -s1 -b2 -e2, meta `#`, skip 1. The output is indexed the same way.

**RED → GREEN:**
- RED: `5 failed, 5 errors in 1.05s`, all `No module named ta_r4.restore_bmi_alleles`.
- GREEN: `10 passed in 1.01s`.

**Negative controls (each restored, `cmp` identical):**
- Flipped class removed: `test_class_counts` RED (`assert {'exact': 2, ..._mismatch': 4} == {..._mismatch': 2}`), plus 4 other tests that depend on it. `test_report_reconciles` stayed GREEN, so the class-count test is the one that discriminates.
- Precision tolerance forced to 0: 5 RED.
- sha256 comparison disabled: `test_wrong_input_sha_exits_2_before_reading` and `test_pin_writes_rows_and_refuses_bad_input` RED.

**Real-file run** (44 s; input sha256s re-checked after the run: both OK):

| metric | value |
|---|---|
| n_frozen | 2,336,269 (= `zcat frozen \| tail -n +2 \| wc -l`) |
| n_exact | 2,327,244 |
| n_flipped | 0 |
| n_value_mismatch | 0 |
| n_unjoined | 9,025 |
| n_kept | 2,327,244 |
| n_sign_uninformative | 23,896 (frozen BETA `0.0`; kept as exact) |
| n_ambiguous_source | 0 |
| raw cross-check | 10,000 sampled, 10,000 ALT == Tested_Allele, 0 reversed, 0 absent, 0 other; rate 1.000000 |

Reconciliation (awk over the report): `n_frozen 2336269 sum 2336269 RECONCILED`. The plan's interfaces block swaps
the row counts: the frozen file is the larger one (2,336,269, the same as the raw file), and the Yengo M1 file has 2,327,244.

**FINDING (disclose in W4a/W8a; Carter at W2c):** all 9,025 unjoined rows are absent from the Yengo M1 file. In the raw
GIANT file they are all palindromic: 3,844 A/T and 5,181 C/G. As the plan specifies, they are dropped from R4 BMI, not restored from raw.
Restoring them from raw would change which file supplies the alleles, so I did not do it. The raw cross-check rate is
1.0, which is above the plan's 0.99 finding threshold.

**sha256 pins** (`manifests/sumstats_r4_sha256.tsv`, 11 rows):
- 9 inputs, each verified against `sha256_manifest_harmonized_m1.tsv`: asthma.EUR, asthma.AFR, hypertension.EUR, stroke.EUR, stroke.AFR, t2d.EUR, t2d.AFR, bmi.EUR, and bmi.EUR.GIANT-UKBB.2018.GRCh37.
- 2 outputs:
  - `data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz`: `2f87e771c5a20660611c3de5e737f6ab29ec66d45f1a62302532e6dc3bc5b1b4` (44,379,564 B)
  - `.tbi`: `36d01d38ead3e09ba7ba8ae4a9c93ba3a55eaf64a051f2e38c944b65d70f572a` (1,421,927 B)
- `sha256sum -c` gives 11/11 OK.

## Unit 2: plink_ld_to_rds.R --emit-ref-alt

**RED → GREEN:**
- RED: `8 failed, 3 passed`, with `long flag "emit-ref-alt" is invalid`. The 3 passes hold before the change by construction: the flag-absent identity on .bim and .pvar, and the plink property test.
- GREEN: `11 passed`, 0 skipped. R4_PLINK is not skippable, so a missing binary is a failure.

**Measured (verbatim):**
- `R[1,2] 0.5000000000 cor(A1 dosage 1, A1 dosage 2) 0.5000000000`
- `swapped R[1,2] -0.5000000000 cor(d1, 2 - d2) -0.5000000000`
- `kao R[1,2] 0.5000000000  no-kao R[1,2] -0.5000000000`. Without `--keep-allele-order`, plink re-codes SNP 2, whose A1 is the major allele, so the sign flips.

**Sabotage REDs (each restored, `cmp` identical):**
- `ALT <- A2` (the plan's control): RED on `test_emit_ref_alt_from_bim` and `test_known_answer...`. The second test went RED
  on the ALT label assertion (`('C','C') == ('T','C')`), not on the correlation. A *global* REF/ALT swap leaves every
  pairwise LD sign unchanged (cor(2−a, 2−b) = cor(a, b)), so no sign test can detect it.
- Per-SNP inconsistent ALT (SNP 2 only): the correlation assertion `np.allclose(R, want)` RED. This is the sign-discriminating control.
- `ref_alt_source` attribute set unconditionally: all 4 flag-off identity tests RED.

**Other pre-existing tests:** `tests/m3/test_ld_npz_to_rds.py` and `test_source_freeze_pins.py` pass together with this file: 65 passed, 1 skipped. The skip is the pre-existing hail import in m3.

## Unit 3: run_qtl_coloc.R --qtl-orient

**RED → GREEN:**
- RED: `10 failed, 2 passed`. The 2 passes are the flag-absent identity cases, which are true by construction before the change.
- GREEN: `12 passed`.
- Task verify (4 files): `141 passed in 143.52s`.

**Fixtures:**
- Unit fixture: 7 variant_ids against a panel. The orient vector is `1,-1,NA,NA,NA,NA,-1` and the counters are
  `exact=1, flipped=2, dropped_palindromic=1, dropped_mismatch=1, dropped_unparseable=2`.
- End-to-end fixture: 200 variants, gated.
  - Counters: exact 138, flipped 50, palindromic 4, mismatch 4, unparseable 4. They sum to 200 = `ld_panel_overlap`.
  - `n_snps_overlap` = 188 = exact + flipped.
  - In the transposed fixture, the swapped rows are written as G/A with negated betas. Under the flag it reproduces the exact fixture's summary and all_pairs. Without the flag it does not.

**Sabotage REDs (each restored, `cmp` identical):**
- `join$orient` used as the QTL orientation (the catalog→panel vector, wrong per Pitfall 4): only `test_transposed_qtl_is_negated` RED
  (`PP.H4.abf 0.7488 != 0.7178`, `hit2 rs900101 != rs900099`).
- `qtl_orient: FALSE` emitted when the flag is off: the 4 identity tests RED.

## Wave close (§C)

**QUICK:** `287 passed, 39 deselected in 112.23s`, real 1m53s.
- Reconciliation: 254 + 10 + 11 + 12 = 287.
- Under the 120 s budget, with little headroom: the 5 test_qtl_orient e2e tests take about 11 s each. They are not marked r4_heavy, because the budget was not exceeded.

**HEAVY:** `35 passed, 4 skipped, 287 deselected in 400.47s`. The 4 skips are the live gates, unchanged from W0d.

**Freeze pins:** 39 passed.

**FULL:** `1750 passed, 50 skipped, 4 warnings in 1441.16s`, rc 0 (junit `data/r4/logs/full_W1.xml`).

**Join by junit id vs `full_W0d.xml`** (the join script reproduced W0c→W0d exactly before use):
- Common 1767, **removed 0, changed 0, added 33** (bmi 10, plink 11, qtl_orient 12; all passed).
- Reconciliation: 1767 + 33 = 1800, 1717 + 33 = 1750, 50 + 0 = 50.
- tests/m3: 1299 ids, 0 missing, 0 changed. phase1: 38 ids, 0 missing, 0 changed. phase2: 137 ids, 0 missing, 0 changed. This is the D-15 proof.

**Hygiene:**
- `tests/m3/sparse_parent_benchmark.tsv` restored.
- Shared conda cache after HEAVY: 2188 entries / `f094b37d…9085` / 23348 MB / 0 archives, identical to W0d. No solve happened.
- Frozen files 0-diff vs HEAD and vs `9eb162d8`: run_susie_rss.R, run_coloc_susie.R, Snakefile, config/pipeline.yaml,
  finemap.smk (both copies), ta_r4_finemap.smk, envs/r_coloc.yml, Snakefile.ta_r4, ld_allele_join.R.
- `git fsck --connectivity-only` before the first commit: dangling objects only.

## Deviations from Plan

1. **[Rule 3, test design] Flag-off identity is pinned to the pre-W1 blobs** (`6f9986d7`, `3ec59663`) instead of
   `git show HEAD:`. After the commit, HEAD is the new script, so the plan's literal check would compare the script with itself.
2. **[Rule 3] New file `src/snakemake/scripts/qtl_orient.R`, not in files_modified.** The JSON exposes no betas, so the
   per-row exact/transposed/palindromic/mismatch/unparseable behaviour on the plan's 4-variant panel is only testable as
   a function. It is sourced only under `--qtl-orient true` and fails closed if missing, the same pattern as ld_allele_join.R.
3. **[Rule 1] The plan's regex `^chr…` after `.up()` could never match**, because `.up()` uppercases. The code uses `^CHR[0-9XY]+_[0-9]+_([ACGT]+)_([ACGT]+)$` instead.
4. **[Plumbing] `--qtl-orient true` requires `--ld-allele-join true`** and stops otherwise. The orientation needs the
   bridge's panel row, and W3e already uses both flags together. The "panel lacks REF/ALT" check runs before the join,
   so the plan's message is the one emitted.
5. **[Plan text] "Recompute z exactly as the script already computes z":** the script computes no z. It passes
   beta/varbeta to `coloc::runsusie`, so only beta is multiplied. Orientation drops that leave fewer than 50 rows stop loudly (`qtl_orient_below_threshold`).
6. **[Test design] The plan's `ALT = A2` sabotage cannot turn a sign test RED** (it is a symmetry). It went RED through the
   label assertion, and a per-SNP sabotage was added to show that the correlation assertion discriminates.
7. **[Interfaces block] The row counts were swapped** (see Unit 1). The implementation is unaffected.
8. **[Rule 3] `pin` subcommand** in restore_bmi_alleles.py, so the 11-row pin manifest comes from tested code and not from an ad-hoc command.
9. **[Test fix, my error] The first swap test kept the .bed unchanged**, which left the A1 dosage the same, so it was wrong. Fixed to recode the dosage as the plan says.

Nothing here changes what is computed, as far as I can judge. SNP_ID naming is untouched in both shared scripts. The
`--emit-ref-alt` change only adds REF/ALT columns, and its output is `identical()` when the flag is off. The palindrome
drop (the finding above) follows the plan's specified source.

## Not verified / open

- The panel-rsid name-override decision from W0d is still open and was not touched.
- The 9,025-row palindrome drop needs disclosure wording (W4a/W8a). Carter may want the raw file as an alternative source, which would be a what-is-computed choice.
- The QUICK budget has about 7 s of headroom.

## Known Stubs

None.

## Threat Flags

None beyond the plan's register. T-r4-W1-01/02/03 are mitigated as specified: default-off flags with identity
proofs, sha256-verified inputs, the value-identity classes, and the `join$orient` sabotage RED.

## Self-Check: PASSED

All 7 created files exist and are tracked. Commits `fb0a5b5c`, `4896e011` and `e7224a91` exist.
