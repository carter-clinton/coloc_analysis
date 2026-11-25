---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8a2
slug: W3f-sumstats-orientation-harmonize
type: execute
wave: 15.8a2
depends_on: ["ta-r4-W3f-collector-drop-audit"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158OR-reply-<date>.txt    # committed as received
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158PAL-reply-<date>.txt   # committed as received
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-PLAN.md      # the 15.8a2-a4 planning set, committed here
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-consumers-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-eligibility-and-draft-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-openblas-pin-and-guard-PLAN.md          # amended for 15.8a2-a4 (base chain, depends_on, fixture note), staged in commit 1
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-json-full-precision-PLAN.md          # expected total only
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-qtl-legacy-rule-and-e7-rounding-PLAN.md   # expected total only
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-e7-filtered-cs-counts-PLAN.md            # expected total only
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-multikey-fatal-and-chronology-PLAN.md    # pilot sumstats + oriented bound
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-PLAN.md      # cumulative chain, nine SUMMARYs, gates
  - .planning/DECISIONS.md
  - src/python/ta_r4/sumstats_orient.py
  - tests/ta_r4/test_sumstats_orient.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv           # 16 rows appended (8 oriented files + 8 .tbi, role output); existing rows unchanged
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation.tsv      # new
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf.tsv  # new (diagnostic, not a gate)
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-SUMMARY.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates: Q-157J (gate_157j.sh), Q-158R2 (gate_158r2.sh, label `D: Harmonize r4 sumstats to one orientation (Recommended)`, sha256 4183859f…bacb), Q-158OR and Q-158PAL (new gate_158a2.sh, question texts and labels exactly as in <question>, sha256 pinned there by the orchestrator) each pass through a byte-identical staging copy; a missing reply, a failed gate, or a label other than the Recommended one is STOP before any edit (another label needs a re-plan)"
    - "src/python/ta_r4/sumstats_orient.py classifies every sumstats row in an r4 region window against that region's r4 catalog with measure_orient.py's rule (exact / swapped_only / both / absent on the normalized CHR:POS:REF:ALT key), and on the 8 catalog-source files reproduces data/r4/tmp/w3f/q158/orient_by_fit.tsv (sha256 b154b0fa…c4f1) row for row"
    - "Per Q-158OR A and Q-158PAL A, a row is flipped iff its key is swapped_only: REF and ALT strings exchanged, BETA sign toggled on the string (a zero BETA unchanged), EAF := 1 − EAF in exact decimal arithmetic (NA/empty unchanged); every other byte of the line, every other line, and every line outside the 31 windows is unchanged; A/T and C/G rows are flipped by the same rule"
    - "Must-be-identity: re-measured on the 8 oriented files, swapped_only == 0 in every one of the 248 trait × region rows; per class after_exact == exact + swapped_only and after_both == both (before), absent and n_rows unchanged; harmonizing an oriented file again flips 0 rows and writes identical decompressed bytes"
    - "Cross-module identity: per source file, the number of flipped rows equals the 15.8a audit rows (data/r4/ld/variants_r4_collector_dropped/) with key_in_final_catalog false and swapped_key_in_final_catalog true (total 159,969), and the rows left absent equal the audit rows with both flags false (total 2,755); any difference is STOP"
    - "verify_unflip (an independent per-line check) passes on all 8 files: each output line is the source line or flip(source line), flips only on swapped_only rows; no new duplicate allele key in any window (planner measurement: 12 duplicate keys before and after, all asthma × HLA_6p21, which is not among the 29 fit regions)"
    - "The 8 oriented files are data/r4/sumstats/<trait>.<anc>.r4_oriented.tsv.bgz (+ .tbi); their sha256 rows are appended to sumstats_r4_sha256.tsv (role output) and every existing row, including the 8 catalog-source files and the Track B data/processed files, is unchanged and still verifies (ta_r4.verify_inputs); no data/processed byte changes (sha256 before == after)"
    - "No consumer reads the oriented files yet (paths.sumstats_path unchanged; 15.8a3 switches): FULL == full_15_8a.xml + N_new, no outcome change"
  artifacts:
    - path: "src/python/ta_r4/sumstats_orient.py"
      provides: "classification, flip, harmonize, verify_unflip, measure, pin"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation.tsv"
      provides: "per region × trait counts before/after, flipped, flipped palindromic"
  key_links:
    - from: "sumstats_orient.measure"
      to: "data/r4/tmp/w3f/q158/orient_by_fit.tsv"
      via: "row-for-row identity on the catalog-source inputs (test 9)"
      pattern: "orient_by_fit"
    - from: "sumstats_orient flip counts"
      to: "manifests/catalog_collector_drops.tsv audit files"
      via: "per-source-file identity (test 11)"
      pattern: "swapped_key_in_final_catalog"
---

<objective>
Carry out Carter's Q-158R2 answer ("D: Harmonize r4 sumstats to one orientation"), with the orientation and the
A/T-C/G rule he chooses in Q-158OR and Q-158PAL. The fit's catalog join (run_susie_rss.R:856-870) is exact on
CHR:POS:REF:ALT, so 159,969 r4 sumstats rows that are written the other way round from the catalog never reach a fit
(hypertension EUR 33.5%, stroke EUR 33.6%, stroke AFR 29.4%, t2d AFR 21.9% of their in-window rows). This plan writes
one oriented copy of each of the 8 r4 inputs under data/r4/sumstats/, proves by identities that only the swapped rows
changed and that none remain, and pins the copies. It changes no consumer (15.8a3) and no DRAFT text (15.8a4).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: as in ta-r4-W3f-collector-drop-audit-PLAN.md <question>. Q-158R2: file `W3f-carter-15-8-Q-158R2-reply-2026-11-25.txt`,
sha256 `4183859f21ffe016b3384043a352a5363def84ab4b9820b410d865508d19bacb`, gated by the existing
`$Q8/gate_158r2.sh` (question text and label typed there).

New questions, asked by the orchestrator before this plan executes, verbatim (QID, question text after
`Question <QID> (<date>): `, labels). The orchestrator saves each reply as `$P/W3f-carter-15-8-<QID>-reply-<date>.txt`
(2 lines, LF, as 15.8a) and pins its sha256 in the table below before execution.

- Q-158OR: `Q-158OR (15.8a2, which orientation). Measured: t2d EUR is written in GRCh37 reference orientation (REF equals the 1000 Genomes REF at 658 of 658 anchor SNPs) and asthma nearly so (653 of 658), but bmi, hypertension, stroke and t2d AFR put the effect allele in ALT (about half of anchors reversed). The r4 catalog took each variant's orientation from the first file that named it (mostly bmi for rsids, t2d EUR for chr:pos names), so it is a mix, and 45,383 variants appear in it twice, once each way, under two names. No LD panel is in one orientation either (the 1000G EUR panel has the reference allele as REF at 502 of 656 anchors; UK Biobank and the AFR VCF panels have their own order), and every step after the catalog join already accepts either orientation (panel joins match exact or swapped; coloc matches positions or unordered alleles and does not depend on the sign); only the catalog join is exact. A: flip each trait's rows to the catalog's orientation; catalogs and panels stay byte-identical (checked by rebuilding the catalogs from the flipped files), and each double-entered variant stays, each trait using the entry that matches it. B: flip every file and the catalogs to the GRCh37 reference allele; needs a pinned GRCh37 FASTA, rebuilds and re-pins all 31 catalogs, re-runs the 15.8a audit, and needs a rule for rows whose alleles do not include the reference base; apart from that rule the fits join the same variants either way. Which?`
  Labels: `A: Catalog orientation, catalogs unchanged (Recommended)` / `B: GRCh37 reference orientation, catalogs rebuilt` / `C: Other (free text)`.
- Q-158PAL: `Q-158PAL (15.8a2, A/T and C/G SNPs). Of the 159,969 rows to flip, 28,637 are A/T or C/G SNPs (2,387 with allele frequency 0.4-0.6), where a swap cannot be told apart from a strand flip. Every r4 step that uses an effect's sign already drops these SNPs: the fits' allele-aware panel join (all production arms), and through the fits the cross-panel purity and the QTL bridge. The only step that reads them, A1 on all variants, matches alleles as an unordered pair and uses coloc.abf, which does not depend on the sign. So no reported posterior depends on how they are oriented; the rule changes only the fits' join counters. A: flip them like any other SNP, by allele key (keeps every row; no swapped row is left). B: flip only when the allele frequency is outside 0.4-0.6 and agrees with an unflipped file of the same ancestry; drop the rest from the r4 files. C: drop every A/T or C/G row that would be flipped. Which?`
  Labels: `A: Flip by allele key like other SNPs (Recommended)` / `B: Flip only when the frequency decides, drop the rest` / `C: Drop every A/T or C/G row that would be flipped` / `D: Other (free text)`.

| QID | file | sha256 | label required by this plan |
|---|---|---|---|
| Q-158OR | `W3f-carter-15-8-Q-158OR-reply-2026-11-25.txt` | `b4a87020eb0ec2965b6239c7c37941dc10207854852e9e7dc555b4990ae6646a` | `A: Catalog orientation, catalogs unchanged (Recommended)` |
| Q-158PAL | `W3f-carter-15-8-Q-158PAL-reply-2026-11-25.txt` | `b5cde5c3f787a5c3bdd74c2863398898097183cf07bc85f429d9fbd8394fec13` | `A: Flip by allele key like other SNPs (Recommended)` |

**Gate text (verified 2026-11-25 against the saved replies).** Line 1 of each saved reply is `Question <QID> (2026-11-25): `
followed by the question text above **without its leading `<QID> `** (e.g. Q-158OR's starts `(15.8a2, which orientation).`); the rest is
byte-identical to the text above (checked for Q-158OR, Q-158PAL, Q-158EL). gate_158a2.sh therefore types `--question` as
the text above minus the leading `<QID> `, i.e. exactly line 1 of the reply after its prefix; a gate typed with the QID
included fails, and that is a gate-script error, not a STOP on the reply.

Another label is not a failed gate but a different plan: STOP, record the reply, return to planning (B for Q-158OR
replaces 15.8a2-a3 with a catalog rebuild; B or C for Q-158PAL changes row counts, so the null-window invariance in
Task 2 no longer holds by construction and the selection needs its own decision).
</question>

<protocol>
The **15.8 shared protocol** in ta-r4-W3f-collector-drop-audit-PLAN.md `<protocol>` binds this plan (PY, P, Q8, MAN;
reply gates by staging copy; close.sh / check_<tag>.py; RED first, one junit id per new test, negative controls in
`$Q8/nc_<tag>.txt`; DRAFT rule; the Never list; `git fsck --connectivity-only` before each commit). Changes for the
15.8a2-a4 sub-chain:
- Order 15.8a → 15.8a2 → 15.8a3 → 15.8a4 → 15.8b → … → 15.8f, strictly sequential.
- Base chain: `$Q8/full_15_8a.xml` (written by 15.8a; expected 2,700 = 2,647 P / 53 S / 0 F because Carter's Q-158R2
  was D, so 15.8a's test 7 was not written; **use its actual totals**, read from the file) → `$Q8/full_15_8a2.xml` →
  `full_15_8a3.xml` → `full_15_8a4.xml` → 15.8b.
- Scratch for this plan: `$Q8/a2/`. Slurm: `sbatch -p compute -A clintonlab_cpu -q normal -t <limit> --mem=<m>`; FULL
  adds `--constraint=cascadelake -t 04:00:00 --mem=48G`.
- Tools: `BGZIP=/rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin/bgzip`,
  `TABIX=/rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin/tabix` (measure_orient.py's tabix), passed as CLI
  arguments, recorded in the report with `--version` output.
</protocol>

<context>
@data/r4/tmp/w3f/q158/measure_orient.py
@src/python/ta_r4/collector_drop_audit.py
@src/python/ta_r4/restore_bmi_alleles.py
@src/python/ta_r4/paths.py
@src/python/ta_r4/select_null_windows.py

**Premise, verified at 8da7bfbe (planning, read-only; planner scripts and outputs in `data/r4/tmp/w3f/q158/planner_15_8a2/`, SHA256SUMS there).**
- Inputs = `CATALOG_SUMSTATS["r4"]` (ta_r4_panels.smk:14-17) = `paths.sumstats_path(t, a, "A3_1kg")` in
  config/pipeline.yaml order: bmi.EUR (data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz), t2d.EUR, t2d.AFR,
  hypertension.EUR (data/processed/sumstats_harmonized/…), asthma.EUR, asthma.AFR
  (data/r4/sumstats/asthma.<anc>.grch37_lifted_strand.tsv.bgz), stroke.EUR, stroke.AFR (data/processed/…). All 8 have
  the same 13-column header `CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD`; EAF is the ALT frequency and
  BETA is signed to ALT (run_susie_rss.R:176-183). hypertension writes lower-case alleles.
- Fit join: run_susie_rss.R:856-870 `subset[variant_dt, on = c("CHR","POS","REF","ALT"), nomatch = 0]` after
  upper-casing; production arms all run `--ld-allele-aware true` (commands.py:41-45), whose panel join
  (:220-323) keeps exact or swapped 4-key matches (z negated for swapped, :1185-1194) and drops A/T, C/G SNPs.
- Orientation per file at the 658 anchors of tests/ta_r4/fixtures/build_anchors_grch37_grch38.tsv (1000 Genomes
  GRCh37 REF/ALT): t2d.EUR 658 REF / 0 reversed; asthma.EUR and .AFR 653 / 5; bmi 335 / 323; t2d.AFR 335 / 323;
  hypertension 330 / 316; stroke.EUR 335 / 321; stroke.AFR 178 / 178. The 1000G EUR .bim: A2 = REF at 502 of 656.
  The r4 catalogs hold 45,383 allele pairs present in both orientations (627,685 rows over 31 regions).
- Planner measurement (`orient2.py` → `orient2.tsv`, Slurm 2093312, read-only): over the 31 windows, 1,598,153 rows; exact
  1,257,617; swapped_only 159,969 (of them A/T or C/G 28,637, with EAF 0.4-0.6 2,387); both 177,812; absent 2,755.
  Flipping the swapped_only rows creates no duplicate allele key (12 before = 12 after, asthma × HLA_6p21) and no
  SNP_ID with more than one catalog-joined key (0 before, 0 after). The 15.8a audit (manifests/catalog_collector_drops.tsv)
  totals n_lost_keys 162,724 and n_lost_keys_swapped_present 159,969: lost − swapped-present = 2,755 = absent, and per
  source file the absent counts match (asthma AFR 821, asthma EUR 1,271, stroke AFR 223, t2d AFR 218, hypertension 124,
  stroke EUR 98; classes unnamed_at_named_position 1,520, rsid_other_allele_key 663, unnamed_duplicate 422,
  unnamed_same_position_other_alleles 150). Regions do not overlap, so each position has one catalog.
- EAF check of the flips (`orient2.py`, `asthma_eaf.py`; non-palindromic, vs the same-ancestry reference file after harmonization; median
  |ΔEAF| flipped vs unflipped): hypertension 0.0167 / 0.0164, stroke EUR 0.0157 / 0.0155, stroke AFR 0.0057 / 0.0058,
  t2d AFR 0.0026 / 0.0021, asthma AFR (vs t2d AFR) 0.0019 with 0 of 2,355 above 0.2; asthma EUR 0.0225 with 5 of 204
  above 0.2 (unflipped 0.0047). The flips are allele swaps, not mislabels; asthma's few are where the GRCh38 lift
  changed the reference allele. Recorded as a diagnostic (Task 2), not a filter: unflipped rows are not filtered by
  EAF either.
- Null-window selection (select_null_windows.scan) reads CHR, POS and P and counts rows per tile; a flip changes none
  of them and no row is added or removed, so the selection is invariant (the 15.7h selection stays on its inputs).

<interfaces>
Contract of src/python/ta_r4/sumstats_orient.py (Task 1 writes it; 15.8a3/a4 import it):
```python
HEADER = ["CHR","POS","REF","ALT","BETA","SE","P","EAF","N","SNP_ID","TRAIT","ANCESTRY","BUILD"]
CLASSES = ("exact", "swapped_only", "both", "absent")
OUT_DIR = f"{paths.R4}/sumstats"
#: The 8 r4 catalog inputs in collector order (CATALOG_SUMSTATS["r4"], config/pipeline.yaml order), typed: the
#: sources of the oriented copies. Tests 9, 11, 14 and the harmonize CLI read this constant, never paths.sumstats_path,
#: so 15.8a3's switch of sumstats_path cannot repoint them at the oriented files.
CATALOG_SOURCES = (
    ("bmi", "EUR", "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz"),
    ("t2d", "EUR", "data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz"),
    ("t2d", "AFR", "data/processed/sumstats_harmonized/t2d.AFR.tsv.bgz"),
    ("hypertension", "EUR", "data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz"),
    ("asthma", "EUR", "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"),
    ("asthma", "AFR", "data/r4/sumstats/asthma.AFR.grch37_lifted_strand.tsv.bgz"),
    ("stroke", "EUR", "data/processed/sumstats_harmonized/stroke.EUR.tsv.bgz"),
    ("stroke", "AFR", "data/processed/sumstats_harmonized/stroke.AFR.tsv.bgz"),
)
def oriented_path(trait, anc) -> str          # f"{OUT_DIR}/{trait}.{anc}.r4_oriented.tsv.bgz"
def classify(key, catalog_keys) -> str        # key = collector_drop_audit.norm_key(...); measure_orient.py's rule
def is_palindromic(ref, alt) -> bool          # single-base A/T, T/A, C/G, G/C after strip().upper()
def flip_fields(f: list[str]) -> list[str]    # REF<->ALT, BETA sign toggle (string), EAF 1-EAF (Decimal); rest identical
def windows(repo=".") -> list[tuple[str, str, int, int]]   # (region_safe, chr, start, end) of the 31 r4 catalogs
def harmonize(src, out_tsv, windows, catalog_keys_by_region) -> dict   # writes plain TSV; counts per region; raises OrientError
def verify_unflip(src, out, windows, catalog_keys_by_region) -> dict   # independent re-read of both files; raises OrientError
def measure(files, windows, catalog_keys_by_region, tabix) -> list[dict]  # orient_by_fit.tsv columns + flipped/palindromic
class OrientError(RuntimeError)
# CLI: python -m ta_r4.sumstats_orient harmonize --trait T --anc A --bgzip B --tabix X --report JSON
#      python -m ta_r4.sumstats_orient measure --files F... --tabix X --out TSV
#      python -m ta_r4.sumstats_orient pin --manifest manifests/sumstats_r4_sha256.tsv   (appends the 16 output rows)
```
Inputs of `harmonize --trait T --anc A`: the CATALOG_SOURCES path for (T, A) (equal to `paths.sumstats_path(T, A,
"A3_1kg")` at this plan's HEAD, asserted once in Task 1; 15.8a3 adds `paths.catalog_source_sumstats_path` returning the
same values), sha256-verified against sumstats_r4_sha256.tsv before parsing
(verify_inputs; exit 2 on mismatch), and the 31 catalogs `paths.catalog_path("r4", region)`, verified against
catalogs_sha256.tsv. **Where the output refusal lives:** in the CLI only (`main()` of `harmonize`), which writes to
`oriented_path(T, A)` and refuses any `--out` whose repo-root-relative normalized path is not under `data/r4/sumstats/`
(OrientError, exit 2). The library function `harmonize(src, out_tsv, …)` takes any path, so tests write to tmp_path and
Task 2's idempotence pass calls the library function (`python -c` / a scratch script) with outputs under `$Q8/a2/idem/`;
`--out` exists on the CLI only so that test 7 can exercise the refusal.
</interfaces>
</context>

<new_tests>
tests/ta_r4/test_sumstats_orient.py; N_new = 14 (no parametrize).
1. `test_classify_reproduces_the_measurement_rule` (exact, swapped_only, both, absent; `chr` prefix and allele case normalized)
2. `test_flip_fields_is_exact_on_strings` (BETA `-0.0621`→`0.0621`, `7.297000000000001e-57`→`-7.297000000000001e-57`,
   `0.0100`→`-0.0100` (trailing zeros kept; stroke AFR has 1,904 such BETAs; `str(-float(x))` gives `-0.01`), `0`→`0`;
   EAF `0.372364438206786`→`0.627635561793214`, `0.8365`→`0.1635` (hypertension's first EAF; float gives
   `0.16349999999999998`), `NA`→`NA`, empty→empty; lower-case alleles swapped as written;
   SE, P, N, SNP_ID, TRAIT, ANCESTRY, BUILD identical)
3. `test_harmonize_flips_only_swapped_only_rows_in_a_window` (two synthetic windows + rows outside; one A/T row
   swapped_only is flipped; exact/both/absent/outside lines byte-identical; counts per region)
4. `test_harmonize_is_idempotent` (second pass: 0 flips, identical bytes)
5. `test_harmonize_refuses_a_new_duplicate_allele_key` (a trait with A/G and G/A at a position whose catalog has only A/G)
6. `test_harmonize_refuses_an_unexpected_header` (an extra Z column; a reordered header)
7. `test_harmonize_refuses_an_output_outside_r4_sumstats` (data/processed/... and data/r4/tmp/... outputs)
8. `test_verify_unflip_detects_any_other_change` (SE changed on a flipped row; an outside-window row flipped; a
   swapped_only row left unflipped: each raises)
9. `test_measure_reproduces_the_orchestrator_measurement` (r4_heavy, written in Task 1 with the RED set: `measure` on
   the CATALOG_SOURCES files == data/r4/tmp/w3f/q158/orient_by_fit.tsv row for row, after checking that file's sha256
   b154b0fa…c4f1; the comparison is a helper `_compare(measured, reference_path)` so the NC can feed it a copy)
10. `test_oriented_files_have_no_swapped_only_rows` (r4_heavy: the must-be-identity; per row of
    manifests/sumstats_r4_orientation.tsv recomputed from the oriented files: swapped_only == 0, after_exact == exact +
    swapped_only, after_both == both, absent and n_rows unchanged; helper `_check_oriented(files)`)
11. `test_flips_equal_the_collector_audit_counts` (r4_heavy: per CATALOG_SOURCES file (typed, not paths.sumstats_path),
    flipped == audit rows with key false and swapped key true; absent == audit rows with both false; helper
    `_audit_identity(orientation_rows, audit_counts)`)
12. `test_oriented_pins_match_disk_and_track_b_is_unchanged` (r4_heavy: 16 appended rows verify; every pre-existing
    row of sumstats_r4_sha256.tsv byte-identical to `$Q8/a2/sumstats_manifest_before.tsv` and verifies)
13. `test_null_window_scan_is_invariant_to_flips` (synthetic: select_null_windows.scan on a file and on its harmonized copy
    are equal)
14. `test_real_oriented_file_differs_only_in_flipped_rows` (r4_heavy: verify_unflip(CATALOG_SOURCES stroke.AFR path,
    oriented stroke.AFR) — the smallest changed file; the other seven are verified in Task 2 and recorded)
Expected FULL: base full_15_8a.xml (expected 2,700) + 14 = 2,714 (2,661 P / 53 S / 0 F if the base is 2,647 / 53 / 0).
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gates; commit replies + 15.8a2-a4 plans + DEC; sumstats_orient.py (RED first)</name>
  <files>.planning/DECISIONS.md, src/python/ta_r4/sumstats_orient.py, tests/ta_r4/test_sumstats_orient.py</files>
  <read_first>
    - run_susie_rss.R :170-330, :820-870, :1150-1200; collect_region_variants.py; collector_drop_audit.py :56-92, :287-330
    - data/r4/tmp/w3f/q158/measure_orient.py; data/r4/tmp/w3f/q158/gate_158r2.sh; data/r4/tmp/w3f/q157/gate_reply.py
    - restore_bmi_alleles.py (verify / bgzip+tabix / report pattern); verify_inputs.py
  </read_first>
  <behavior>
    - Tests 1-8 and 13 per <new_tests> on synthetic gzip files in tmp_path (catalog TSVs + regions written there);
      test 9 (r4_heavy) on the real catalog-source files
  </behavior>
  <action>
    0. `mkdir -p $Q8/a2`; `git rev-parse HEAD > $Q8/a2/start.txt`. Confirm 15.8a closed: its SUMMARY committed and
       `$Q8/full_15_8a.xml` exists (else STOP); record its totals. Run `bash $Q8/gate_157j.sh`, `bash $Q8/gate_158r2.sh`.
       Write `$Q8/gate_158a2.sh` as a copy of gate_158.sh with only the Q/S/L entries for Q-158OR and Q-158PAL (texts and
       labels from <question>, sha256 from its table); negative controls: `GATE_NC_MUTATE=1` → exit 2; the Q-158OR text
       with one character changed → exit 2. Run it for both QIDs. Any failure, a missing file, or a non-Recommended label
       → STOP (per <question>). sha256sum each original into `$Q8/a2/gate.txt`.
       Commit 1 (explicit paths): the two reply files as received (`git diff --cached --stat`, sha256 unchanged), the
       three 15.8a2-a4 PLAN files, the six amended 15.8 PLAN files (15.8b openblas-pin-and-guard, 15.8c
       qtl-json-full-precision, 15.8c2 qtl-legacy-rule-and-e7-rounding, 15.8d e7-filtered-cs-counts, 15.8e
       multikey-fatal-and-chronology, 15.8f 15-8-review-suite-and-close; `git diff --cached` of each shows only the
       15.8a2-a4 amendments), and in .planning/DECISIONS.md DEC `DEC-2026-11-25-ta-r4-sumstats-orientation` quoting
       both replies (`cat` + `cmp` against the committed files) and Q-158R2's, stating: canonical orientation = the r4
       catalog's (A), A/T-C/G flipped by key (A), oriented copies under data/r4/sumstats/, consumers switched in 15.8a3,
       DRAFT in 15.8a4; lifts nothing under D-28 (no frozen file edited). Message
       `docs(ta-r4-W3f): 15.8a2-a4 planning set + 15.8b-f amendments + Carter Q-158OR/Q-158PAL replies + DEC (15.8a2)`.
    1. Before-state: `sha256sum` of the 8 inputs, every `data/processed/sumstats_harmonized/*.tsv.bgz` named in
       sumstats_r4_sha256.tsv, the 31 r4 catalogs and `$MAN/sumstats_r4_sha256.tsv` → `$Q8/a2/sha_before.txt`; copy
       sumstats_r4_sha256.tsv to `$Q8/a2/sumstats_manifest_before.tsv`; run `ta_r4.verify_inputs` on the 8 inputs (mismatch = STOP).
    2. Assert `CATALOG_SOURCES` paths == `[paths.sumstats_path(t, a, "A3_1kg") for (t, a, _) in CATALOG_SOURCES]` at this
       HEAD and == collector_drop_audit.r4_sumstats() (list equality, collector order) → `$Q8/a2/sources_check.txt`.
       RED: tests 1-9, 13 (module absent → ImportError; test 9 run under sbatch `-t 00:30:00 --mem=8G`) → `$Q8/red_15_8a2.txt`.
    3. Write sumstats_orient.py to <interfaces>. Streaming line reader on `gzip.open(..., "rt", newline="")`, split on
       `\t` (no csv quoting; a line whose field count != 13 is OrientError), header must equal HEADER exactly. A row is in
       a window when `CHR` (prefix-stripped) == window chr and start <= POS <= end (regions_r4.csv bounds, inclusive, as
       run_coloc_pair_r4.R read_region). Unusable alleles (empty, `NA`, `N`, `-`, case-insensitive) → class absent,
       never flipped. BETA toggle: leading `-` removed, else `-` prepended, unless `Decimal(BETA) == 0` (non-numeric BETA
       on a row to flip = OrientError). EAF: `str(Decimal(1) - Decimal(EAF))` unless EAF is NA/empty; EAF outside [0, 1]
       on a row to flip = OrientError. After flipping, a normalized key that repeats within a window and did not repeat
       before = OrientError naming CHR:POS. Report JSON: per region the four classes before, n_flipped,
       n_flipped_palindromic, n_flipped_palindromic_eaf_0.4_0.6, input/output sha256, tool versions. `harmonize` writes a
       plain TSV next to the output, bgzips it (`BGZIP -c`), indexes it (`TABIX -f -s 1 -b 2 -e 2 -S 1`, the
       restore_bmi_alleles.py call), deletes the plain TSV. Tests 1-9, 13 green (test 9 under sbatch).
    4. Negative controls (`$Q8/nc_15_8a2.txt`, md5-restore after each): (a) flip on `swapped_only or both` → test 3
       fails; (b) BETA toggle via `str(-float(x))` → test 2 fails on `0.0100`; (c) EAF via `str(1 - float(x))` → test 2
       fails on `0.8365`; (d) duplicate-key check removed → test 5 fails; (e) verify_unflip skips outside-window lines →
       test 8 fails; (f) test 9's `_compare` fed a copy of orient_by_fit.tsv with one byte changed in one count → fails
       (test 9 is a characterization test of `measure` against the measurement Carter's decision used; this NC is its
       evidence that it can fail).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158r2.sh && bash data/r4/tmp/w3f/q158/gate_158a2.sh Q-158OR Q-158PAL && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient.py -q -p no:cacheprovider -m "not r4_heavy"</automated>
  </verify>
  <done>Replies, plans and DEC committed; the module exists with its fast tests green and five negative controls seen failing.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Write, verify and pin the 8 oriented files; identities (STOP on any difference)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation.tsv, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_orientation_eaf.tsv, tests/ta_r4/test_sumstats_orient.py</files>
  <behavior>
    - Tests 10-12 and 14 per <new_tests> (RED: written first, fail on the absent manifest / oriented files)
  </behavior>
  <action>
    1. RED tests 10-12, 14 → append to `$Q8/red_15_8a2.txt`.
    2. `$Q8/a2/harmonize_array.sh`: Slurm array 0-7 (one input each; `-t 02:00:00 --mem=8G`), running `harmonize`, then
       `verify_unflip` on (input, output), writing `$Q8/a2/report_<trait>.<anc>.json` and `/usr/bin/time -v` peaks. Any
       OrientError = STOP (no retry with a relaxed rule).
    3. Identities, each to `$Q8/a2/identities.txt` (any difference = STOP; nothing pinned):
       (a) `measure` on the 8 catalog-source files == orient_by_fit.tsv (test 9's check, run at full size);
       (b) `measure` on the 8 oriented files: swapped_only == 0 in all 248 rows; per class after_exact == exact +
       swapped_only and after_both == both; absent and n_rows unchanged; (c) the library `harmonize()` (not the CLI,
       which refuses paths outside data/r4/sumstats/) on each oriented file, plain TSV output under `$Q8/a2/idem/`:
       0 flips and `cmp` against the oriented file's decompressed bytes; (d) per source file, report n_flipped == audit rows (key false,
       swapped key true) and absent == audit rows (both false), over the 31 audit files of 15.8a; totals 159,969 and
       2,755; (e) Track B: every data/processed sha256 in `$Q8/a2/sha_before.txt` unchanged; the 8 inputs and 31
       catalogs unchanged.
    4. Write manifests/sumstats_r4_orientation.tsv (region_safe, trait, ancestry, n_rows, exact, swapped_only, both,
       absent, n_flipped, n_flipped_palindromic, n_flipped_palindromic_eaf_0.4_0.6, after_exact, after_swapped_only,
       after_both, after_absent; 248 rows + no total row) and manifests/sumstats_r4_orientation_eaf.tsv (trait, ancestry,
       class flipped/unflipped, reference file, n, median |ΔEAF|, n above 0.2; non-palindromic rows with numeric EAF in
       both files; reference = t2d.EUR for EUR traits, the oriented asthma.AFR for t2d/stroke AFR, the oriented t2d.AFR
       for asthma AFR; header comment: "diagnostic, not a filter"). `pin`: append 16 rows (path, sha256, bytes, role
       output) to sumstats_r4_sha256.tsv; `diff` against `$Q8/a2/sumstats_manifest_before.tsv` shows only the appended
       lines; `ta_r4.verify_inputs` on all 16 + the 8 inputs passes.
    5. Tests 9-12, 14 green. Negative controls (append to `$Q8/nc_15_8a2.txt`; restore after each):
       (g) test 10's `_check_oriented` on the CATALOG_SOURCES files instead of the oriented ones → fails (swapped_only > 0);
       (h) test 11's `_audit_identity` with one per-file audit count changed by 1 → fails;
       (i) test 12 with one sha256 character changed in a temp copy of sumstats_r4_sha256.tsv, once in an appended row
       and once in a pre-existing data/processed row → fails both times;
       (j) test 14 on a temp copy of the oriented stroke.AFR file with one byte of one unflipped line's SE changed
       (re-bgzipped) → fails. Time the tests (`--durations=0`) into the LOG (test 9 and 10 read the 31 windows by tabix: about
       a minute each expected; if any exceeds 15 minutes, restrict it to the 6 changed files before commit 2).
    6. Commit 2: tests, three manifests (`feat(ta-r4-W3f): r4 sumstats in the catalog's orientation, identities
       proven, pinned (15.8a2)`). The oriented files live on /rs1 through the data/r4 symlink (durable); they are not
       git-tracked, as for the other data/r4/sumstats files.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_sumstats_orient.py -q -p no:cacheprovider && PYTHONPATH=src/python /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.verify_inputs --manifest .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/sumstats_r4_sha256.tsv $(for t in bmi.EUR t2d.EUR t2d.AFR hypertension.EUR asthma.EUR asthma.AFR stroke.EUR stroke.AFR; do echo --file data/r4/sumstats/$t.r4_oriented.tsv.bgz; done)</automated>
  </verify>
  <done>8 oriented files written and pinned; swapped_only is 0 everywhere; flips equal the audit's swapped-present rows; Track B bytes unchanged.</done>
</task>

<task type="auto">
  <name>Task 3: FULL vs full_15_8a.xml; records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-SUMMARY.md</files>
  <action>
    1. `$Q8/close.sh 15_8a2` under sbatch (protocol). `$Q8/check_15_8a2.py` from check_tmpl.run: base full_15_8a.xml,
       NEW = the 14 ids, declared = none, expect = base totals + 14. Restore tests/m3/sparse_parent_benchmark.tsv.
    2. Records: LOG entry (gates, premise table, per-file flip counts, identities (a)-(e), EAF diagnostic, NCs, check
       output, timings); PLAN-INDEX: the three 15.8a2-a4 rows (orchestrator text) + 15.8a2 COMPLETE + the 15.8 note's
       order line; STATE ★ block (NEXT = 15.8a3; NOT PUSHED); SUMMARY with `## Declared spec updates` (none) and
       `## New test ids` (14, junit form). fsck; commit explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8a2.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml;d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False and d['confirmatory']['n_regions_min']==7" && test -z "$(git status --porcelain -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/catalogs_sha256.tsv src/python/ta_r4/paths.py)"</automated>
  </verify>
  <done>FULL reconciled (base + 14, no outcome change); records committed; not pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| pinned r4 inputs → oriented copies | every changed byte must be an intended flip |
| Track B data/processed → r4 | r4 must not write there |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158a2-01 | Tampering | harmonize changes more than the swapped rows | mitigate | verify_unflip per line on all 8 files; idempotence; swapped_only == 0; flips == audit counts |
| T-r4-158a2-02 | Tampering | sign error on a flipped row | mitigate | string-exact BETA toggle and Decimal EAF (test 2, NCs b-c); EAF agreement recorded per trait |
| T-r4-158a2-03 | Tampering | Track B files changed | mitigate | output path refusal (test 7); sha256 of every data/processed input before == after (test 12) |
| T-r4-158a2-04 | Repudiation | reply provenance | mitigate | staging copy cmp + sha256 + exact question text and label |
</threat_model>

<verification>
- All four gates pass and gate_158a2.sh's negative controls exit 2; identities (a)-(e) hold; check_15_8a2.py passes.
</verification>

<success_criteria>
- Every r4 sumstats row whose variant is in the catalog matches it exactly in one orientation, shown by identity, and
  the change is confined to the swapped rows; nothing reads the oriented files yet.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-sumstats-orientation-harmonize-SUMMARY.md`
</output>
